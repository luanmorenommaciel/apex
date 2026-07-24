"""Integration tests against a real ClickHouse (infra's stack).

Skipped automatically when infra is not up, so the unit suite stays runnable
offline. Bring infra up with `docker compose up -d` in infra/ to run these.

Every seeded row uses ts=now(). The contract fixture's ts is June 2024 and the
tables carry a 90-day TTL on ts, so inserting it verbatim succeeds and then
silently vanishes on merge (contract/README.md).
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest

from apex_engine import analyze
from apex_engine.clickhouse import EngineStore
from apex_engine.config import ClickHouseSettings
from apex_engine.schema import FindingType

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "contract" / "sample_event.json"

# The real job the P0 run left behind: 17 stages, stage 4 skewed at 21.62x.
P0_JOB_ID = "app-20260724160310-0000"

EVENT_COLUMNS = [
    "job_id", "app_id", "app_name", "stage_id", "stage_attempt", "ts",
    "shuffle_read_bytes", "shuffle_write_bytes", "spill_disk_bytes", "spill_mem_bytes",
    "gc_time_ms", "input_bytes", "output_bytes", "peak_execution_mem_bytes",
    "task_count", "task_duration_p50_ms", "task_duration_p99_ms",
    "plan_fingerprint", "plan_json",
]


def _client():
    try:
        client = ClickHouseSettings().connect()
        client.query("SELECT 1")
        return client
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"ClickHouse unavailable: {exc}")


@pytest.fixture
def store():
    return EngineStore(_client())


@pytest.fixture
def seeded(store):
    """Seed stage rows under a throwaway job_id and always clean them up."""
    created: list[str] = []

    def seed(stages: list[dict]) -> str:
        job_id = f"engine-test-{uuid.uuid4().hex[:12]}"
        created.append(job_id)
        base = json.loads(FIXTURE.read_text(encoding="utf-8"))
        rows = []
        for i, overrides in enumerate(stages):
            row = {**base, "job_id": job_id, "app_id": f"app-{job_id}",
                   "stage_id": i, "stage_attempt": 0,
                   # TTL gotcha: the fixture ts is 2024 and would be dropped.
                   "ts": datetime.now(timezone.utc)}
            row.update(overrides)
            rows.append([row[c] for c in EVENT_COLUMNS])
        store.client.insert(table="spark_events", database="apex",
                            data=rows, column_names=EVENT_COLUMNS)
        return job_id

    yield seed

    for job_id in created:
        store.client.command(
            "ALTER TABLE apex.spark_events DELETE WHERE job_id = %(j)s SETTINGS mutations_sync=1",
            parameters={"j": job_id})
        store.client.command(
            "ALTER TABLE apex.findings DELETE WHERE job_id = %(j)s SETTINGS mutations_sync=1",
            parameters={"j": job_id})


HEALTHY = {"task_duration_p50_ms": 100, "task_duration_p99_ms": 110,
           "shuffle_read_bytes": 1_000, "shuffle_write_bytes": 1_000,
           "spill_disk_bytes": 0, "spill_mem_bytes": 0, "gc_time_ms": 5,
           "input_bytes": 1_000_000, "output_bytes": 900_000,
           "peak_execution_mem_bytes": 1_000, "task_count": 50,
           "plan_json": "Project [id]\n+- Relation parquet"}

SKEWED = {**HEALTHY, "task_duration_p50_ms": 21, "task_duration_p99_ms": 454}


def test_fixture_ts_would_be_ttl_expired(seeded, store):
    """Documents the trap: the fixture's own ts is outside the 90-day TTL."""
    fixture_ts_ms = json.loads(FIXTURE.read_text(encoding="utf-8"))["ts"]
    fixture_ts = datetime.fromtimestamp(fixture_ts_ms / 1000, timezone.utc)
    age_days = (datetime.now(timezone.utc) - fixture_ts).days
    assert age_days > 90, "fixture is no longer old enough to demonstrate the TTL trap"


def test_clean_job_inserts_zero_rows_and_makes_zero_llm_calls(seeded, store):
    """The exit criterion, against real ClickHouse."""
    job_id = seeded([HEALTHY, HEALTHY, HEALTHY])
    result = analyze(job_id, store)

    assert result["stages_analyzed"] == 3
    assert result["findings"] == []
    assert result["written_rows"] == 0
    assert result["llm_calls"] == 0
    assert result["escalated"] == []
    assert result["crew"] == "not_needed"

    stored = store.client.query(
        "SELECT count() FROM apex.findings WHERE job_id = {j:String}",
        parameters={"j": job_id}).result_rows[0][0]
    assert stored == 0


def test_skewed_job_writes_a_finding_no_llm_needed(seeded, store):
    job_id = seeded([HEALTHY, SKEWED])
    result = analyze(job_id, store)

    skew = [f for f in result["findings"] if f.type is FindingType.SKEW_ON_JOIN]
    assert len(skew) == 1
    assert skew[0].stage_id == 1
    assert "21.62x" in skew[0].evidence
    assert result["written_rows"] == len(result["findings"])
    assert result["llm_calls"] == 0

    row = store.client.query(
        "SELECT type, severity, confidence, detected_by FROM apex.findings "
        "WHERE job_id = {j:String} AND type = 'SKEW_ON_JOIN'",
        parameters={"j": job_id}).result_rows[0]
    assert row == ("SKEW_ON_JOIN", "critical", "HIGH", "skew_watcher")


def test_re_analysis_converges_instead_of_duplicating(seeded, store):
    """apex.findings is a plain MergeTree; a second run must not append copies."""
    job_id = seeded([SKEWED])

    first = analyze(job_id, store)
    assert first["persistence"]["mode"] == "inserted"
    assert first["written_rows"] >= 1

    second = analyze(job_id, store)
    assert second["persistence"]["mode"] == "already_present"
    assert second["written_rows"] == 0
    assert second["persistence"]["skipped_existing"] == first["written_rows"]

    total = store.client.query(
        "SELECT count() FROM apex.findings WHERE job_id = {j:String}",
        parameters={"j": job_id}).result_rows[0][0]
    assert total == first["written_rows"]


def test_dry_run_never_writes(seeded, store):
    job_id = seeded([SKEWED])
    result = analyze(job_id, store, persist=False)
    assert result["findings"], "expected the skewed stage to be detected"
    assert result["written_rows"] == 0
    stored = store.client.query(
        "SELECT count() FROM apex.findings WHERE job_id = {j:String}",
        parameters={"j": job_id}).result_rows[0][0]
    assert stored == 0


def test_real_p0_job_reproduces_the_proven_skew(store):
    """The exact case infra/sql/005_skew.sql already proved: 21.62x on stage 4."""
    aggregates = store.stage_aggregates(P0_JOB_ID)
    if not aggregates:
        pytest.skip(f"{P0_JOB_ID} not present in this ClickHouse")

    result = analyze(P0_JOB_ID, store, persist=False, use_crew=False)
    assert result["stages_analyzed"] == 17
    assert result["llm_calls"] == 0

    by_stage = {f.stage_id: f for f in result["findings"] if f.type is FindingType.SKEW_ON_JOIN}
    assert "21.62x" in by_stage[4].evidence
    # and the healthy stages 005_skew.sql leaves alone stay unflagged
    assert 19 not in by_stage and 21 not in by_stage and 0 not in by_stage


def test_real_p0_job_yields_aqe_ground_truth(store):
    """plan_transitions is consumed: 2 HIGH-confidence coalesce re-plans."""
    transitions = store.plan_transitions(P0_JOB_ID)
    if not transitions:
        pytest.skip(f"{P0_JOB_ID} has no plan_transitions in this ClickHouse")

    assert all(t.is_ground_truth for t in transitions)
    result = analyze(P0_JOB_ID, store, persist=False, use_crew=False)
    aqe = [f for f in result["findings"] if f.detected_by == "aqe_watcher"]
    assert len(aqe) == 1
    assert aqe[0].type is FindingType.AQE_REPLAN
    assert aqe[0].stage_id == -1  # job-level: v0.2 has no execution->stage map
