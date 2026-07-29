"""recall() end-to-end against a fake store — no ClickHouse required."""

from __future__ import annotations

from datetime import datetime, timezone

from apex_memory.clickhouse import MemoryStore
from apex_memory.encoder import encode
from apex_memory.recall import recall
from apex_memory.schema import Confidence, MatchTier

NOW = datetime(2026, 7, 28, tzinfo=timezone.utc)
FP_A = "a" * 64
FP_B = "b" * 64
PLAN = (
    "'Aggregate [count(null) AS #0L]\n"
    "+- 'Join Inner, (none#1L = none#0)\n"
    "   :- Relation [none#0] parquet\n"
    "   +- Relation [none#1] parquet\n"
)

AQE_ON = {"spark.sql.adaptive.enabled": "true", "spark.sql.shuffle.partitions": "200"}
AQE_OFF = {"spark.sql.adaptive.enabled": "false", "spark.sql.shuffle.partitions": "100"}


def _outcome(job_id, fp, task_time, conf, input_bytes=1_000_000):
    return {
        "job_id": job_id, "app_id": job_id, "app_name": "test", "plan_fingerprint": fp,
        "conf_shuffle_partitions": None, "conf_executor_instances": None,
        "conf_executor_cores": None, "conf_executor_memory_mb": None,
        "conf_driver_cores": None, "conf_driver_memory_mb": None,
        "conf_extra": dict(conf), "config_source": "observed" if conf else "unknown",
        "stage_count": 1, "task_count": 100, "wall_clock_ms": task_time,
        "task_time_ms": task_time, "shuffle_read_bytes": 0, "shuffle_write_bytes": 0,
        "spill_disk_bytes": 0, "spill_mem_bytes": 0, "gc_time_ms": 0,
        "input_bytes": input_bytes, "output_bytes": 0, "peak_execution_mem_bytes": 0,
        "max_skew_ratio": 1.0, "aqe_skew_splits": 0, "aqe_coalesces": 0,
        "finding_count": 0, "worst_severity": "", "outcome_source": "apex",
        "observed_at": NOW, "indexed_at": NOW,
    }


class FakeStore(MemoryStore):
    """Routes each SQL constant to canned rows by matching a distinctive token."""

    def __init__(self, outcomes, *, job_conf=None, shapes=None, neighbours=None):
        self._outcomes, self._job_conf = outcomes, job_conf or {}
        self._shapes, self._neighbours = shapes or [], neighbours or []

    def query(self, sql, parameters=None):
        parameters = parameters or {}
        if "FROM apex.job_conf" in sql:
            conf = self._job_conf.get(parameters.get("job_id"))
            return [{"conf": conf}] if conf else []
        if "AS wall_clock_ms" in sql:
            return self._shapes
        if "cosineDistance" in sql:
            return self._neighbours
        if "FROM apex.plan_memory" in sql:
            return [{"embedding": encode(PLAN).vector, "sample_plan_json": PLAN}]
        if "FROM apex.run_outcomes" in sql:
            wanted = set(parameters.get("fps", []))
            return [o for o in self._outcomes if o["plan_fingerprint"] in wanted]
        raise AssertionError(f"unexpected SQL: {sql[:80]}")


def test_a_run_is_not_evidence_about_itself():
    store = FakeStore([_outcome("self", FP_A, 1000, AQE_ON)])
    result = recall(store, job_id="self", plan_fingerprint=FP_A)
    assert result.similar_runs == []
    assert result.confidence is Confidence.LOW
    assert any("nothing to recall" in r for r in result.confidence_reasons)


def test_exact_matches_are_tiered_above_structural():
    outcomes = [
        _outcome("j1", FP_A, 1000, AQE_ON),
        _outcome("j2", FP_B, 900, AQE_ON),
    ]
    store = FakeStore(outcomes, neighbours=[{"plan_fingerprint": FP_B, "similarity": 0.95}])
    result = recall(store, plan_fingerprint=FP_A)
    tiers = [m.tier for m in result.similar_runs]
    assert tiers[0] is MatchTier.EXACT
    assert MatchTier.STRUCTURAL in tiers


def test_low_similarity_neighbours_are_dropped():
    store = FakeStore(
        [_outcome("j2", FP_B, 900, AQE_ON)],
        neighbours=[{"plan_fingerprint": FP_B, "similarity": 0.40}],
    )
    result = recall(store, plan_fingerprint=FP_A, min_similarity=0.80)
    assert result.similar_runs == []


def test_config_unavailable_is_stated_not_guessed():
    store = FakeStore([_outcome("j1", FP_A, 1000, {}), _outcome("j2", FP_A, 900, {})])
    result = recall(store, plan_fingerprint=FP_A)
    assert result.best_known_config.available is False
    assert result.best_known_config.config == {}
    assert "config_unavailable" in result.best_known_config.reason


def test_ab_regime_recommends_the_config_that_actually_won():
    outcomes = [
        _outcome("fast1", FP_A, 400, AQE_ON), _outcome("fast2", FP_A, 500, AQE_ON),
        _outcome("slow1", FP_A, 1500, AQE_OFF), _outcome("slow2", FP_A, 1600, AQE_OFF),
    ]
    shapes = [{"plan_fingerprint": FP_A, "task_time_ms": 1550, "input_bytes": 1_000_000}]
    store = FakeStore(outcomes, shapes=shapes, job_conf={"q": AQE_OFF})
    result = recall(store, job_id="q", plan_fingerprint=FP_A)

    rec = result.best_known_config
    assert rec.available is True
    assert rec.config["spark.sql.adaptive.enabled"] == "true"
    assert "A/B over history" in rec.method
    # Two keys differ, so the gain belongs to the bundle, not to one knob.
    assert set(rec.differs_from_current) == set(AQE_ON)
    assert "bundle as a whole" in rec.method


def test_delta_is_gated_when_history_has_one_config():
    outcomes = [_outcome("j1", FP_A, 400, AQE_ON), _outcome("j2", FP_A, 1600, AQE_ON)]
    shapes = [{"plan_fingerprint": FP_A, "task_time_ms": 1600, "input_bytes": 1_000_000}]
    store = FakeStore(outcomes, shapes=shapes, job_conf={"q": AQE_ON})
    result = recall(store, job_id="q", plan_fingerprint=FP_A)
    assert result.predicted_delta.meaningful is False
    assert "unattributable" in result.predicted_delta.reason


def test_cold_start_plan_json_needs_no_fingerprint():
    """The ZEST case: a plan that has never executed still has a logical plan."""
    store = FakeStore(
        [_outcome("j2", FP_B, 900, AQE_ON)],
        neighbours=[{"plan_fingerprint": FP_B, "similarity": 0.99}],
    )
    result = recall(store, plan_json=PLAN)
    assert result.query_plan_fingerprint is None
    assert len(result.similar_runs) == 1
    assert result.similar_runs[0].tier is MatchTier.STRUCTURAL


def test_untrusted_fields_are_declared():
    store = FakeStore([_outcome("j1", FP_A, 1000, AQE_ON)])
    assert recall(store, plan_fingerprint=FP_A).untrusted_fields


def test_recall_requires_an_argument():
    import pytest

    with pytest.raises(ValueError):
        recall(FakeStore([]))
