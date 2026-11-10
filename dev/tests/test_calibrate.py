from __future__ import annotations

import importlib.util
import math
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "calibrate.py"
SPEC = importlib.util.spec_from_file_location("calibrate", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

APP_ID = "app-20261019161337-0000"


def test_ch_request_binds_app_id_as_a_url_parameter_and_keeps_sql_constant() -> None:
    req = MODULE.ch_request(MODULE.TRANSITIONS_SQL, APP_ID, "pw", user="u", url="http://ch:8123/")
    parsed = urlparse(req.full_url)
    assert parse_qs(parsed.query) == {"param_app_id": [APP_ID]}
    body = req.data.decode("utf-8")
    assert body == MODULE.TRANSITIONS_SQL
    assert "{app_id:String}" in body
    assert APP_ID not in body
    assert req.get_method() == "POST"
    assert req.get_header("Authorization", "").startswith("Basic ")


def test_both_queries_are_constants_with_a_bound_placeholder() -> None:
    for sql in (MODULE.TRANSITIONS_SQL, MODULE.STAGE_P99_SQL):
        assert "{app_id:String}" in sql
        assert "'" not in sql


@pytest.mark.parametrize(
    "hostile",
    [
        "app-20261019161337-0000' OR 1=1 --",
        "app-2026",
        "",
        "APP-20261019161337-0000",
        "app-20261019161337-0000\n",
    ],
)
def test_ch_request_rejects_non_application_ids_before_any_request(hostile: str) -> None:
    with pytest.raises(ValueError, match="app_id_must_be_a_spark_application_id"):
        MODULE.ch_request(MODULE.STAGE_P99_SQL, hostile, "pw", user="u", url="http://ch:8123")


def test_ch_functions_return_none_without_a_password(monkeypatch) -> None:
    monkeypatch.delenv("APEX_CANONICAL_CH_PASSWORD", raising=False)
    assert MODULE.ch_transitions(APP_ID) is None
    assert MODULE.ch_stage_p99(APP_ID) is None


def test_ch_stage_p99_uses_the_bound_request_through_a_fake_transport(monkeypatch) -> None:
    seen = {}

    class _Resp:
        def __init__(self, payload: bytes):
            self._payload = payload

        def read(self) -> bytes:
            return self._payload

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def fake_urlopen(req, timeout=0):
        seen["url"] = req.full_url
        seen["body"] = req.data.decode("utf-8")
        return _Resp(b'{"stage_id":4,"task_count":100,"task_duration_p50_ms":10,"task_duration_p99_ms":250}\n')

    monkeypatch.setenv("APEX_CANONICAL_CH_PASSWORD", "pw")
    monkeypatch.setattr(MODULE.urllib.request, "urlopen", fake_urlopen)
    row = MODULE.ch_stage_p99(APP_ID, wait_seconds=1)
    assert row == {"stage_id": 4, "task_count": 100, "task_duration_p50_ms": 10, "task_duration_p99_ms": 250}
    assert parse_qs(urlparse(seen["url"]).query) == {"param_app_id": [APP_ID]}
    assert APP_ID not in seen["body"]


def test_cv_is_sample_std_over_mean() -> None:
    assert MODULE.cv([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]) == pytest.approx(2.138089935 / 5.0)
    assert MODULE.cv([1.0]) is None
    assert MODULE.cv([0.0, 0.0]) == 0.0
    assert MODULE.cv([None, 3.0, 3.0]) == 0.0


def test_pct_formats_ratios_and_none() -> None:
    assert MODULE.pct(None) == "n/a"
    assert MODULE.pct(0.1234) == "12.3%"


def test_extract_signal_driver_oom_is_binary_and_needs_no_history_server() -> None:
    out = MODULE.extract_signal("driver_oom", APP_ID, "... java.lang.OutOfMemoryError: Java heap space", 1, 12.34, 8)
    assert out["failed_as_expected"] is True
    assert out["oom_in_log"] is True
    assert out["wall_s"] == 12.3
    missing = MODULE.extract_signal("driver_oom", APP_ID, "completed normally", 0, 1.0, 8)
    assert missing["failed_as_expected"] is False


def test_extract_signal_skew_uses_history_metrics_and_closed_form(monkeypatch) -> None:
    stages = [
        {"stageId": 1, "attemptId": 0, "status": "COMPLETE", "shuffleReadBytes": 10, "numTasks": 16, "diskBytesSpilled": 0},
        {"stageId": 3, "attemptId": 0, "status": "COMPLETE", "shuffleReadBytes": 50_000_000, "numTasks": 100, "diskBytesSpilled": 0},
    ]
    summary = {"duration": [1.0, 100.0, 2500.0, 2600.0],
               "shuffleReadMetrics": {"readBytes": [1.0, 2.0, 3.0, 28_000_000.0]}}
    monkeypatch.setattr(MODULE, "wait_stages", lambda app_id, timeout_s=240: stages)
    monkeypatch.setattr(MODULE, "task_summary", lambda app_id, stage_id, attempt: summary)
    monkeypatch.delenv("APEX_CANONICAL_CH_PASSWORD", raising=False)

    out = MODULE.extract_signal("skew_join", APP_ID, "", 0, 30.0, 8)

    assert out["signal_stage"] == 3
    assert out["stage_tasks"] == 100
    assert out["p99_p50"] == 25.0
    assert out["skew_ratio"] == 26.0
    assert out["hot_partition_bytes"] == 28_000_000
    assert out["tail_threshold"] == pytest.approx((100 - 1) / (8 - 1), abs=0.01)
    assert out["tail_bound"] is True
    assert "plugin_p99_ms" not in out  # no ClickHouse creds, no plugin statistic


def test_extract_signal_reports_missing_shuffle_stage_instead_of_crashing(monkeypatch) -> None:
    monkeypatch.setattr(MODULE, "wait_stages", lambda app_id, timeout_s=240: [
        {"stageId": 0, "attemptId": 0, "status": "COMPLETE", "shuffleReadBytes": 0, "numTasks": 1}
    ])
    out = MODULE.extract_signal("bad_shuffle", APP_ID, "", 0, 1.0, 8)
    assert out["error"] == "no shuffle-read stage found"
    assert out["stage_count"] == 1
    assert math.isfinite(out["wall_s"])
