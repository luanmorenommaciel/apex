"""Verify that a real Spark event log does not expose S3 credential values."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import zstandard


SENSITIVE_KEYS = {"fs.s3a.access.key", "fs.s3a.secret.key"}
REDACTED = "*********(redacted)"


def _read_zstd(path: Path) -> bytes:
    with path.open("rb") as source:
        with zstandard.ZstdDecompressor().stream_reader(source) as reader:
            return reader.read()


def _property_pairs(event: dict[str, object], section: str) -> dict[str, str]:
    raw = event.get(section, [])
    if not isinstance(raw, list):
        return {}
    return {
        str(pair[0]): str(pair[1])
        for pair in raw
        if isinstance(pair, list) and len(pair) >= 2
    }


def verify(
    event_log: Path,
    access_key_file: Path,
    secret_key_file: Path,
    app_id: str,
    spark_submit_observed: bool,
    argv_secret_match: bool,
) -> dict[str, object]:
    blob = _read_zstd(event_log)
    # Docker secret files may end with a newline. Compare their logical values,
    # and reject empty files so a containment check cannot pass vacuously.
    access_key = access_key_file.read_bytes().strip()
    secret_key = secret_key_file.read_bytes().strip()
    if not access_key or not secret_key:
        raise ValueError("s3_secret_file_empty")
    spark_properties: dict[str, str] = {}
    hadoop_properties: dict[str, str] = {}

    for line in blob.splitlines():
        if not line:
            continue
        event = json.loads(line)
        if event.get("Event") != "SparkListenerEnvironmentUpdate":
            continue
        spark_properties.update(_property_pairs(event, "Spark Properties"))
        hadoop_properties.update(_property_pairs(event, "Hadoop Properties"))

    hadoop_sensitive_values = {
        key: hadoop_properties[key]
        for key in SENSITIVE_KEYS
        if key in hadoop_properties
    }
    checks = {
        "s3a_job_completed": bool(app_id),
        "spark_submit_observed_live": spark_submit_observed,
        "spark_submit_argv_secret_match": argv_secret_match,
        "event_log_access_key_match": access_key in blob,
        "event_log_secret_key_match": secret_key in blob,
        "spark_properties_sensitive_keys": sorted(
            SENSITIVE_KEYS.intersection(spark_properties)
        ),
        "hadoop_sensitive_values_redacted": all(
            value == REDACTED for value in hadoop_sensitive_values.values()
        ),
    }
    passed = (
        checks["s3a_job_completed"]
        and checks["spark_submit_observed_live"]
        and not checks["spark_submit_argv_secret_match"]
        and not checks["event_log_access_key_match"]
        and not checks["event_log_secret_key_match"]
        and not checks["spark_properties_sensitive_keys"]
        and checks["hadoop_sensitive_values_redacted"]
    )
    return {
        "schema": "apex.r1.s3a_runtime_secrets.v1",
        "status": "passed" if passed else "failed",
        "app_id": app_id,
        "spark_version": "4.1.2",
        "credentials_provider": "EnvironmentVariableCredentialsProvider",
        "checks": checks,
        "secret_values_recorded": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-log", type=Path, required=True)
    parser.add_argument("--access-key-file", type=Path, required=True)
    parser.add_argument("--secret-key-file", type=Path, required=True)
    parser.add_argument("--app-id", required=True)
    parser.add_argument("--spark-submit-observed", action="store_true")
    parser.add_argument("--argv-secret-match", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = verify(
        args.event_log,
        args.access_key_file,
        args.secret_key_file,
        args.app_id,
        args.spark_submit_observed,
        args.argv_secret_match,
    )
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(f"{rendered}\n", encoding="utf-8")
    print(rendered)
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
