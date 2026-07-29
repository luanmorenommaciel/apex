#!/usr/bin/env python3
"""Assert one real pathology from canonical ClickHouse stage telemetry."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import Request, urlopen


APP_ID_PATTERN = re.compile(r"^app-\d{14}-\d{4}$")
SCENARIOS = ("skew_join", "spill", "bad_shuffle", "driver_oom")
STAGES_SQL = """
SELECT
  stage_id, stage_attempt, shuffle_read_bytes, spill_disk_bytes,
  task_count, task_duration_p50_ms, task_duration_p99_ms
FROM apex.spark_events
WHERE job_id = {job_id:String}
ORDER BY stage_id, stage_attempt, ts
FORMAT JSONEachRow
"""


class AssertionFailure(RuntimeError):
    """The canonical store does not prove the expected pathology."""


def _number(row: dict[str, Any], field: str) -> float:
    value = row.get(field, 0)
    try:
        return float(value or 0)
    except (TypeError, ValueError) as exc:
        raise AssertionFailure(f"invalid_{field}:{value!r}") from exc


def evaluate(scenario: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Evaluate the same four signals as the legacy JSONL gate."""
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown_scenario:{scenario}")
    if not rows:
        raise AssertionFailure("canonical_stage_telemetry_missing")

    if scenario == "skew_join":
        ratios = [
            _number(row, "task_duration_p99_ms") / _number(row, "task_duration_p50_ms")
            for row in rows
            if _number(row, "task_duration_p50_ms") > 0
        ]
        maximum = max(ratios, default=0.0)
        if maximum <= 10:
            raise AssertionFailure(f"skew_ratio_not_above_10:{maximum:.3f}")
        return {"max_p99_p50_ratio": round(maximum, 3), "stage_count": len(rows)}

    if scenario == "spill":
        total = sum(_number(row, "spill_disk_bytes") for row in rows)
        if total <= 0:
            raise AssertionFailure("spill_disk_bytes_is_zero")
        return {"spill_disk_bytes": int(total), "stage_count": len(rows)}

    if scenario == "bad_shuffle":
        matched = [
            row for row in rows
            if _number(row, "task_count") == 2 and _number(row, "shuffle_read_bytes") > 1_000_000
        ]
        if not matched:
            raise AssertionFailure("two_task_large_shuffle_stage_missing")
        return {
            "matched_stage_ids": [int(_number(row, "stage_id")) for row in matched],
            "stage_count": len(rows),
        }

    return {"pre_oom_stage_count": len(rows), "stage_count": len(rows)}


def fetch_stages(*, job_id: str, url: str, user: str, password: str) -> list[dict[str, Any]]:
    if not APP_ID_PATTERN.fullmatch(job_id):
        raise ValueError("job_id_must_be_a_spark_application_id")
    query_url = f"{url.rstrip('/')}?{urlencode({'param_job_id': job_id})}"
    auth = base64.b64encode(f"{user}:{password}".encode("utf-8")).decode("ascii")
    request = Request(
        query_url,
        data=STAGES_SQL.encode("utf-8"),
        headers={"Authorization": f"Basic {auth}", "Content-Type": "text/plain; charset=utf-8"},
        method="POST",
    )
    with urlopen(request, timeout=15) as response:  # nosec B310: operator-provided local endpoint
        body = response.read().decode("utf-8")
    return [json.loads(line) for line in body.splitlines() if line.strip()]


def wait_for_evidence(
    fetch: Callable[[], list[dict[str, Any]]],
    *,
    scenario: str,
    wait_seconds: int,
    poll_seconds: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Wait for the scenario's terminal evidence, not merely the first stage row.

    OTLP ingestion is asynchronous: early rows for a job can arrive before the
    final shuffle/spill stage. Returning at the first row would create a false
    negative for a real pathology that is still being persisted.
    """
    deadline = time.monotonic() + wait_seconds
    last_error = "canonical_stage_telemetry_missing"
    while True:
        rows = fetch()
        try:
            return rows, evaluate(scenario, rows)
        except AssertionFailure as exc:
            last_error = str(exc)
        if time.monotonic() >= deadline:
            raise AssertionFailure(f"canonical_evidence_timeout:{wait_seconds}s:{last_error}")
        time.sleep(poll_seconds)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--scenario", required=True, choices=SCENARIOS)
    parser.add_argument("--wait-seconds", type=int, default=120)
    parser.add_argument("--poll-seconds", type=float, default=3.0)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    password = os.environ.get("APEX_CANONICAL_CH_PASSWORD")
    if not password:
        print(json.dumps({"status": "failed", "error": "APEX_CANONICAL_CH_PASSWORD_required"}))
        return 2
    try:
        rows, result = wait_for_evidence(
            lambda: fetch_stages(
                job_id=args.job_id,
                url=os.getenv("APEX_CANONICAL_CH_URL", "http://127.0.0.1:8123"),
                user=os.getenv("APEX_CANONICAL_CH_USER", "apex"),
                password=password,
            ),
            scenario=args.scenario,
            wait_seconds=args.wait_seconds,
            poll_seconds=args.poll_seconds,
        )
    except Exception as exc:
        print(json.dumps({"job_id": args.job_id, "scenario": args.scenario, "status": "failed", "error": f"{type(exc).__name__}:{exc}"}))
        return 1
    print(json.dumps({"job_id": args.job_id, "scenario": args.scenario, "status": "passed", **result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
