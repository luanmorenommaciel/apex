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


# 4 x 2 = 8 slots. Seeded into apex.job_conf (contract v0.4) because rule 1's
# threshold is (n-1)/(slots-1) and without a width there is no verdict to assert.
CLUSTER_CONF = {"spark.executor.instances": "4", "spark.executor.cores": "2",
                "spark.sql.adaptive.enabled": "true",
                "spark.sql.adaptive.skewJoin.enabled": "true"}


@pytest.fixture
def seeded(store):
    """Seed stage rows (+ a job_conf row) under a throwaway job_id, then clean up."""
    created: list[str] = []

    def seed(stages: list[dict], conf: dict | None = CLUSTER_CONF) -> str:
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
        if conf is not None:
            store.client.insert(
                table="job_conf", database="apex",
                data=[[job_id, f"app-{job_id}", "engine-test", dict(conf),
                       datetime.now(timezone.utc)]],
                column_names=["job_id", "app_id", "app_name", "conf", "ts"])
        return job_id

    yield seed

    for job_id in created:
        for table in ("spark_events", "findings", "job_conf"):
            store.client.command(
                f"ALTER TABLE apex.{table} DELETE WHERE job_id = %(j)s SETTINGS mutations_sync=1",
                parameters={"j": job_id})


HEALTHY = {"task_duration_p50_ms": 100, "task_duration_p99_ms": 110,
           "shuffle_read_bytes": 1_000, "shuffle_write_bytes": 1_000,
           "spill_disk_bytes": 0, "spill_mem_bytes": 0, "gc_time_ms": 5,
           "input_bytes": 1_000_000, "output_bytes": 900_000,
           "peak_execution_mem_bytes": 1_000, "task_count": 50,
           "plan_json": "Project [id]\n+- Relation parquet"}

# A skew claim needs VOLUME (dev's finding) and a Join node (the fabricated-type
# bug). 112 MB of shuffle READ over 50 tasks is 2.3 MB/task — a real tail.
SKEWED = {**HEALTHY, "task_duration_p50_ms": 21, "task_duration_p99_ms": 454,
          "shuffle_read_bytes": 112_930_867,
          "plan_json": "'Join Inner, (none#2L = cast(none#0 as bigint))"}

# Byte-for-byte the same ratio with no volume and no join: the shape of the
# marquee false positive, and now invisible.
JITTER_ONLY = {**HEALTHY, "task_duration_p50_ms": 21, "task_duration_p99_ms": 454}


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


def test_a_jitter_only_ratio_writes_nothing_even_against_real_clickhouse(seeded, store):
    """21.62x over 13 KB with no Join: the false positive's shape, end to end."""
    job_id = seeded([HEALTHY, JITTER_ONLY])
    result = analyze(job_id, store)

    assert result["findings"] == []
    assert result["written_rows"] == 0
    assert result["llm_calls"] == 0


def test_skewed_job_writes_a_finding_no_llm_needed(seeded, store):
    job_id = seeded([HEALTHY, SKEWED])
    result = analyze(job_id, store)

    skew = [f for f in result["findings"] if f.type is FindingType.SKEW_ON_JOIN]
    assert len(skew) == 1
    assert skew[0].stage_id == 1
    assert "21.62x" in skew[0].evidence
    # the width came from the seeded v0.4 job_conf row: 4 instances x 2 cores
    assert result["cluster_width"] == "8 slots (job_conf)"
    assert result["job_conf_present"] is True
    assert skew[0].details["tail_bound_threshold"] == pytest.approx(7.0)
    # NO-OP CHECK: skewJoin.enabled is already true on the seeded run
    assert "ALREADY true" in skew[0].fix
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


def test_real_p0_job_no_longer_fabricates_join_skew(store):
    """The marquee false positive, against the real rows that produced it.

    `005_skew.sql` flagged stage 4 of this job at 21.62x and engine shipped it as
    a CRITICAL SKEW_ON_JOIN. Three independent facts in these same rows say it is
    not one, and each alone is disqualifying:
      * its logical plan is a Delta-metadata `!Aggregate` with no Join node;
      * it reads 0 shuffle bytes, and join skew lands on the shuffle READ side;
      * it moves 13,913 bytes over 50 tasks — 278 bytes/task, no volume tail.
    """
    aggregates = store.stage_aggregates(P0_JOB_ID)
    if not aggregates:
        pytest.skip(f"{P0_JOB_ID} not present in this ClickHouse")

    stage4 = next(s for s in aggregates if s.stage_id == 4)
    assert stage4.skew_ratio > 21  # the ratio is real...
    assert stage4.bytes_per_task < 1024 * 1024  # ...and it is measuring nothing

    result = analyze(P0_JOB_ID, store, persist=False, use_crew=False)
    assert result["stages_analyzed"] == 17
    assert result["llm_calls"] == 0

    skew = [f for f in result["findings"]
            if f.type in (FindingType.SKEW_ON_JOIN, FindingType.TASK_SKEW)
            and f.detected_by.startswith("skew_watcher")]
    assert skew == [], f"expected no heuristic skew finding, got {[f.evidence for f in skew]}"


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


# --- typed executor runtime, read with the Map as a FALLBACK ---------------
# The column is additive, so three row shapes coexist in a real store and the
# read has to survive all three. Only the middle one is interesting: it is the
# transition window, and reading the typed column ALONE demotes it from
# `measured` (0.85) to the proxy (0.45), which silently flips it back to
# escalation-eligible. That regression is invisible offline — the SQL is what
# changes, and the unit suite builds StageAggregate directly — so it is pinned
# here, against a real ClickHouse.
RUNTIME_ROW_COLUMNS = [
    "job_id", "app_id", "stage_id", "stage_attempt", "ts",
    "gc_time_ms", "task_count", "task_duration_p50_ms", "task_duration_p99_ms",
    "executor_run_time_ms", "attributes",
]


@pytest.fixture
def runtime_rows(store):
    job_id = f"engine-test-{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc)
    rows = [
        # 0: pre-column run — nothing anywhere, the proxy is correct here.
        [job_id, f"app-{job_id}", 0, 0, now, 3_000, 10, 100, 100, 0, {}],
        # 1: TRANSITION — typed column defaulted to 0, value still in the Map.
        [job_id, f"app-{job_id}", 1, 0, now, 3_000, 10, 100, 100, 0,
         {"executor_run_time_ms": "10000"}],
        # 2: post-migration run — typed column populated.
        [job_id, f"app-{job_id}", 2, 0, now, 3_000, 10, 100, 100, 20_000,
         {"executor_run_time_ms": "20000"}],
    ]
    store.client.insert(table="spark_events", database="apex",
                        data=rows, column_names=RUNTIME_ROW_COLUMNS)
    yield job_id
    store.client.command(
        "ALTER TABLE apex.spark_events DELETE WHERE job_id = %(j)s SETTINGS mutations_sync=1",
        parameters={"j": job_id})


def test_typed_runtime_column_is_read_with_the_map_as_fallback(runtime_rows, store):
    by_stage = {s.stage_id: s for s in store.stage_aggregates(runtime_rows)}

    assert by_stage[0].executor_run_time_ms == 0, "no value anywhere -> proxy, unchanged"
    assert by_stage[1].executor_run_time_ms == 10_000, (
        "transition row: typed column is 0 but the Map still carries the value. "
        "Reading the column alone loses it and demotes the finding to the proxy."
    )
    assert by_stage[2].executor_run_time_ms == 20_000, "typed column is preferred"


def test_transition_row_still_reports_a_measured_runtime(runtime_rows, store):
    """The behavioural consequence, not just the number: a transition row must
    stay `measured` and stay above the 0.60 gate."""
    result = analyze(runtime_rows, store, persist=False, use_crew=False)
    memory_findings = {f.stage_id: f for f in result["findings"]
                       if f.detected_by == "memory_watcher"}

    transition = memory_findings[1]
    assert transition.details["runtime_basis"] == "measured"
    assert transition.confidence_score >= 0.60, "must not fall back to escalation-eligible"

    pre_column = memory_findings[0]
    assert "estimated" in pre_column.details["runtime_basis"], "historical rows keep the proxy"
