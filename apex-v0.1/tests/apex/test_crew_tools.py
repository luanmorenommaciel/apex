import json

from apex_diagnostics.config import DiagnosticsThresholds
from apex_diagnostics.crew.llm import ENV_MODEL_KEY, build_llm
from apex_diagnostics.crew.pipeline import analyze, detectors_only_report
from apex_diagnostics.crew.tools import build_detector_tools
from apex_diagnostics.detectors.gc import GC_SQL
from apex_diagnostics.detectors.oom import OOM_SQL
from apex_diagnostics.detectors.plans import ADAPTIVE_PLAN_TEXT_SQL, PLAN_TEXT_SQL, PLANS_SQL
from apex_diagnostics.detectors.shuffle import SHUFFLE_SQL
from apex_diagnostics.detectors.skew import SKEW_SQL
from apex_diagnostics.models import Finding, Severity

from tests.fakes.clickhouse import FakeCHClient

THRESHOLDS = DiagnosticsThresholds()
APP = "app-20260706-0002"

# stage_attempt_id is required by the per-attempt grouping in detectors/skew.py.
SKEWED = [{"stage_id": 4, "stage_attempt_id": 0, "max_ms": 45000, "p50_ms": 3000, "n_tasks": 24}]


def make_client() -> FakeCHClient:
    return FakeCHClient(
        {
            SKEW_SQL: SKEWED,
            SHUFFLE_SQL: [],
            PLANS_SQL: [],
            PLAN_TEXT_SQL: [],
            ADAPTIVE_PLAN_TEXT_SQL: [],
            GC_SQL: [],
            OOM_SQL: [],
        }
    )


def test_detector_tools_run_without_llm():
    tools = build_detector_tools(make_client(), THRESHOLDS)
    # All five registered detectors are exposed to the crew (no 3-vs-5 drift);
    # order follows detectors.DETECTORS.
    assert [tool.name for tool in tools] == [
        "detect_skew",
        "detect_shuffle",
        "detect_plans",
        "detect_gc",
        "detect_oom",
    ]
    payload = json.loads(tools[0].run(app_id=APP))
    assert payload[0]["detector"] == "skew"
    assert payload[0]["severity"] == "critical"


def test_build_llm_returns_none_when_unconfigured(monkeypatch):
    monkeypatch.delenv(ENV_MODEL_KEY, raising=False)
    assert build_llm() is None


def test_analyze_degrades_to_detectors_only_without_llm(monkeypatch):
    monkeypatch.delenv(ENV_MODEL_KEY, raising=False)
    report = analyze(APP, make_client(), THRESHOLDS)
    assert report.status == "detectors_only"
    assert report.app_id == APP
    assert len(report.findings) == 1
    assert report.recommendations == []
    assert report.max_severity() == "critical"


def test_detectors_only_report_summarizes_counts():
    findings = [
        Finding(detector="skew", severity=Severity.CRITICAL, app_id=APP, title="t"),
        Finding(detector="shuffle", severity=Severity.WARNING, app_id=APP, title="t"),
    ]
    report = detectors_only_report(APP, findings)
    assert "1 critical" in report.summary
    assert "1 warning" in report.summary
