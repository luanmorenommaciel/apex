import importlib.util
from pathlib import Path

import zstandard


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_s3_runtime_evidence.py"
SPEC = importlib.util.spec_from_file_location("verify_s3_runtime_evidence", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
verify = MODULE.verify


def _event_log(path: Path, access_value: str, secret_value: str) -> Path:
    raw = (
        '{"Event":"SparkListenerEnvironmentUpdate",'
        '"Spark Properties":[["spark.app.id","app-test"]],'
        '"Hadoop Properties":['
        f'["fs.s3a.access.key","{access_value}"],'
        f'["fs.s3a.secret.key","{secret_value}"]'
        "]}\n"
    ).encode()
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
