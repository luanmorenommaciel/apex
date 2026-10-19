import importlib.util
from pathlib import Path

import zstandard


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_s3_runtime_evidence.py"
SPEC = importlib.util.spec_from_file_location("verify_s3_runtime_evidence", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
verify = MODULE.verify


PROVIDER = "org.apache.hadoop.fs.s3a.EnvironmentVariableCredentialsProvider"


def _event_log(
    path: Path,
    access_value: str,
    secret_value: str,
    *,
    spark_version: str | None = "4.1.2",
    provider: str | None = PROVIDER,
) -> Path:
    lines = []
    if spark_version is not None:
        lines.append(f'{{"Event":"SparkListenerLogStart","Spark Version":"{spark_version}"}}')
    hadoop = [
        f'["fs.s3a.access.key","{access_value}"]',
        f'["fs.s3a.secret.key","{secret_value}"]',
    ]
    if provider is not None:
        hadoop.append(f'["fs.s3a.aws.credentials.provider","{provider}"]')
    lines.append(
        '{"Event":"SparkListenerEnvironmentUpdate",'
        '"Spark Properties":[["spark.app.id","app-test"]],'
        '"Hadoop Properties":[' + ",".join(hadoop) + "]}"
    )
    raw = ("\n".join(lines) + "\n").encode()
    path.write_bytes(zstandard.ZstdCompressor().compress(raw))
    return path


def test_accepts_redacted_hadoop_properties_without_sparkconf_credentials(
    tmp_path: Path,
) -> None:
    access = tmp_path / "access"
    secret = tmp_path / "secret"
    access.write_text("local-access", encoding="utf-8")
    secret.write_text("local-secret", encoding="utf-8")
    event_log = _event_log(
        tmp_path / "event.zstd",
        "*********(redacted)",
        "*********(redacted)",
    )

    result = verify(event_log, access, secret, "app-test", True, False)

    assert result["status"] == "passed"
    assert result["secret_values_recorded"] is False
    # Attested from the run, not from literals in the script.
    assert result["spark_version"] == "4.1.2"
    assert result["credentials_provider"] == "EnvironmentVariableCredentialsProvider"
    assert result["credentials_provider_class"] == PROVIDER


def test_rejects_actual_secret_value_in_event_log(tmp_path: Path) -> None:
    access = tmp_path / "access"
    secret = tmp_path / "secret"
    access.write_text("local-access", encoding="utf-8")
    secret.write_text("local-secret", encoding="utf-8")
    event_log = _event_log(
        tmp_path / "event.zstd",
        "local-access",
        "local-secret",
    )

    result = verify(event_log, access, secret, "app-test", True, False)

    assert result["status"] == "failed"
    assert result["checks"]["event_log_secret_key_match"] is True


def test_rejects_actual_secret_value_when_secret_files_end_with_newline(
    tmp_path: Path,
) -> None:
    access = tmp_path / "access"
    secret = tmp_path / "secret"
    access.write_text("local-access\n", encoding="utf-8")
    secret.write_text("local-secret\n", encoding="utf-8")
    event_log = _event_log(
        tmp_path / "event.zstd",
        "local-access",
        "local-secret",
    )

    result = verify(event_log, access, secret, "app-test", True, False)

    assert result["status"] == "failed"
    assert result["checks"]["event_log_access_key_match"] is True
    assert result["checks"]["event_log_secret_key_match"] is True


def test_rejects_empty_secret_file(tmp_path: Path) -> None:
    access = tmp_path / "access"
    secret = tmp_path / "secret"
    access.write_text("", encoding="utf-8")
    secret.write_text("local-secret", encoding="utf-8")
    event_log = _event_log(
        tmp_path / "event.zstd",
        "*********(redacted)",
        "*********(redacted)",
    )

    try:
        verify(event_log, access, secret, "app-test", True, False)
    except ValueError as exc:
        assert str(exc) == "s3_secret_file_empty"
    else:
        raise AssertionError("empty S3 secret file must be rejected")


def test_spark_version_and_provider_follow_the_event_log(tmp_path: Path) -> None:
    access = tmp_path / "access"
    secret = tmp_path / "secret"
    access.write_text("local-access", encoding="utf-8")
    secret.write_text("local-secret", encoding="utf-8")
    event_log = _event_log(
        tmp_path / "event.zstd",
        "*********(redacted)",
        "*********(redacted)",
        spark_version="4.0.1",
        provider="org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
    )

    result = verify(event_log, access, secret, "app-test", True, False)

    assert result["spark_version"] == "4.0.1"
    assert result["credentials_provider"] == "SimpleAWSCredentialsProvider"


def test_missing_spark_version_is_a_named_error(tmp_path: Path) -> None:
    access = tmp_path / "access"
    secret = tmp_path / "secret"
    access.write_text("local-access", encoding="utf-8")
    secret.write_text("local-secret", encoding="utf-8")
    event_log = _event_log(
        tmp_path / "event.zstd", "*********(redacted)", "*********(redacted)", spark_version=None
    )

    try:
        verify(event_log, access, secret, "app-test", True, False)
    except MODULE.EvidenceError as exc:
        assert str(exc) == "spark_version_missing_from_event_log"
    else:
        raise AssertionError("a manifest without a run-derived Spark version must not be produced")


def test_missing_credentials_provider_is_a_named_error(tmp_path: Path) -> None:
    access = tmp_path / "access"
    secret = tmp_path / "secret"
    access.write_text("local-access", encoding="utf-8")
    secret.write_text("local-secret", encoding="utf-8")
    event_log = _event_log(
        tmp_path / "event.zstd", "*********(redacted)", "*********(redacted)", provider=None
    )

    try:
        verify(event_log, access, secret, "app-test", True, False)
    except MODULE.EvidenceError as exc:
        assert str(exc) == "credentials_provider_missing_from_event_log"
    else:
        raise AssertionError("a manifest without a run-derived provider must not be produced")


def test_script_has_no_literal_version_or_provider() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    assert '"4.1.2"' not in source
    assert '"EnvironmentVariableCredentialsProvider"' not in source
