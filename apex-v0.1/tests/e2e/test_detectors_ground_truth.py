"""End-to-end ground-truth validation for the apex_diagnostics detectors.

Unlike tests/apex/* (which feed synthetic rows through FakeCHClient), this closes
the full loop against the running stack: a synthetic workload deliberately
triggers one pathology -> event logs are ingested into ClickHouse -> the CLI runs
the detectors + stores a report -> here we assert the expected detector actually
fired at the expected severity. This is the only test that exercises the real SQL,
the real schema columns (jvm_gc_time_ms, reason, shuffle_*), and the calibrated
thresholds against genuine Spark output.

It reuses the production read path (ClickHouseConnectClient + reports.store.get_report)
so a schema/SQL drift surfaces here, not just in a fake.

Run it via `make validate-detectors` (which runs the workloads, ingests, diagnoses,
then invokes this module). The module skips itself unless APEX_E2E=1 so the default
`make tests` never tries to reach ClickHouse.
"""

import os

import pytest

# Guard before importing anything stack-specific: keeps `make tests` (unit suite)
# from ever attempting a ClickHouse connection. `make validate-detectors` sets
# APEX_E2E=1 after the workloads have been ingested and diagnosed.
if os.environ.get("APEX_E2E") != "1":
    pytest.skip(
        "E2E ground-truth tests need the running stack; set APEX_E2E=1 "
        "(use `make validate-detectors`).",
        allow_module_level=True,
    )

from apex_diagnostics.models import SEVERITY_RANK  # noqa: E402
from apex_diagnostics.reports.store import get_report  # noqa: E402

pytestmark = pytest.mark.e2e

# App Name (set by each workload's APP_NAME) -> (expected detector, minimum
# severity). Ground truth from src/workloads/catalog.py sizing + the calibration
# notes in docs/Apex-Detailed-guide.md sec. 12:
#   skew_join      -> one straggler task 100x+ the median            -> skew critical
#   shuffle_heavy  -> wide aggregation spills memory/disk            -> shuffle >= warning
#   gc_churn       -> serial GC + tiny young gen, ~12% GC time       -> gc >= warning
#   oom_victim     -> unspillable array > heap, tasks die            -> oom critical
#   cross_join     -> CartesianProduct visible in the physical plan  -> plans critical
GROUND_TRUTH = [
    ("workload-skew", "skew", "critical"),
    ("workload-shuffle", "shuffle", "warning"),
    ("workload-gc", "gc", "warning"),
    ("workload-oom", "oom", "critical"),
    ("workload-crossjoin", "plans", "critical"),
]

# App Name lives only in SparkListenerApplicationStart; event_time_ms is set from
# the event's top-level Timestamp by the loader, so ORDER BY it DESC picks the most
# recent run of a workload that may have been submitted several times.
APP_ID_SQL = """
SELECT app_id
FROM spark_raw_events
WHERE event_type = 'SparkListenerApplicationStart'
  AND JSONExtractString(raw, 'App Name') = {app_name:String}
ORDER BY event_time_ms DESC
LIMIT 1
"""


@pytest.fixture(scope="module")
def client():
    from apex_diagnostics.clickhouse import ClickHouseConnectClient

    try:
        ch = ClickHouseConnectClient()
        ch.query("SELECT 1")
    except Exception as exc:  # unreachable stack / missing password -> skip, don't fail
        pytest.skip(f"ClickHouse not reachable for E2E ({type(exc).__name__}: {exc})")
    return ch


def _latest_app_id(client, app_name: str) -> str | None:
    rows = client.query(APP_ID_SQL, {"app_name": app_name})
    return rows[0]["app_id"] if rows else None


@pytest.mark.parametrize(
    "app_name,detector,min_severity",
    GROUND_TRUTH,
    ids=[name for name, _, _ in GROUND_TRUTH],
)
def test_workload_triggers_expected_detector(client, app_name, detector, min_severity):
    app_id = _latest_app_id(client, app_name)
    assert app_id, (
        f"No ingested run named {app_name!r} in spark_raw_events. Run the workload "
        f"and ingest first (`make validate-detectors` does workloads -> spark-logs -> this test)."
    )

    report = get_report(client, app_id)
    assert report is not None, (
        f"{app_name} ({app_id}) was ingested but has no diagnostic report; "
        f"did `make diagnose` / `make spark-logs` run after the workload?"
    )

    matches = [f for f in report.findings if f.detector == detector]
    assert matches, (
        f"{app_name} ({app_id}) produced no '{detector}' finding. "
        f"Report status={report.status}, findings="
        f"{[(f.detector, f.severity.value) for f in report.findings]}. "
        f"If the run was too small, raise the workload size (see catalog.py) before touching thresholds."
    )

    best = max(SEVERITY_RANK[f.severity.value] for f in matches)
    assert best >= SEVERITY_RANK[min_severity], (
        f"{app_name}: '{detector}' fired but below the expected '{min_severity}' severity — "
        f"got {[f.severity.value for f in matches]}. The pathology may be under-provoked."
    )
