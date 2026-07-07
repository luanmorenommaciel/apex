from apex_diagnostics.models import DiagnosticReport, Finding, Severity
from apex_diagnostics.reports.store import (
    LATEST_REPORT_SQL,
    UNANALYZED_RUNS_SQL,
    get_report,
    save_report,
    unanalyzed_runs,
)

from tests.fakes.clickhouse import FakeCHClient

APP = "app-20260706-0003"


def make_report() -> DiagnosticReport:
    return DiagnosticReport(
        app_id=APP,
        status="detectors_only",
        summary="s",
        findings=[Finding(detector="shuffle", severity=Severity.WARNING, app_id=APP, title="t")],
    )


def test_save_report_inserts_expected_row(monkeypatch):
    monkeypatch.delenv("CREW_LLM_MODEL", raising=False)
    client = FakeCHClient()
    report_uid = save_report(client, make_report())
    table, rows = client.inserted[0]
    row = rows[0]
    assert table == "spark_diagnostic_reports"
    assert row["report_uid"] == report_uid
    assert row["app_id"] == APP
    assert row["status"] == "detectors_only"
    assert row["max_severity"] == "warning"
    assert row["findings_count"] == 1
    assert row["llm_model"] == ""
    assert "generated_at" not in row


def test_get_report_round_trips_json():
    report = make_report()
    client = FakeCHClient({LATEST_REPORT_SQL: [{"report_json": report.model_dump_json()}]})
    assert get_report(client, APP) == report


def test_get_report_returns_none_without_rows():
    client = FakeCHClient({LATEST_REPORT_SQL: []})
    assert get_report(client, APP) is None


def test_unanalyzed_runs_returns_app_ids():
    client = FakeCHClient({UNANALYZED_RUNS_SQL: [{"app_id": "a1", "last_task_finish_ms": 2}, {"app_id": "a2", "last_task_finish_ms": 1}]})
    assert unanalyzed_runs(client) == ["a1", "a2"]
