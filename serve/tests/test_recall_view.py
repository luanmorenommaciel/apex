"""The recall payload: bounded similarity, typed config, honest provenance.

recall_similar_runs is the only tool that says "this configuration worked", so
these models are where that claim is constrained. Two properties are enforced
by the schema rather than by convention, and both are asserted here: similarity
is a bounded NUMBER, and `config_source` never defaults to `observed`.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from apex_mcp.models import (
    CONFIG_UNAVAILABLE,
    PriorRun,
    RecallResult,
    RecallSummary,
    RunConfig,
    SimilarPlan,
)

FP = "a" * 64


def _observed_config() -> RunConfig:
    return RunConfig(
        shuffle_partitions=200,
        executor_instances=4,
        executor_cores=4,
        executor_memory_mb=8192,
        driver_cores=2,
        driver_memory_mb=4096,
    )


def test_similar_plan_carries_bounded_similarity():
    """B-1 — the fingerprint plus a score between 0 and 1."""
    plan = SimilarPlan(plan_fingerprint=FP, similarity=0.91, node_count=12)

    assert plan.plan_fingerprint == FP
    assert plan.similarity == pytest.approx(0.91)
    assert plan.match == "structural"

    for out_of_range in (1.4, -0.1):
        with pytest.raises(ValidationError):
            SimilarPlan(plan_fingerprint=FP, similarity=out_of_range)


def test_similarity_is_a_number_not_a_boolean():
    """Collapsing it into same/different throws away the only thing that lets a
    reader judge whether the neighbour is worth learning from."""
    schema = SimilarPlan.model_json_schema()["properties"]["similarity"]

    assert schema["type"] == "number"
    assert schema["minimum"] == 0.0
    assert schema["maximum"] == 1.0


def test_prior_run_carries_config_and_source():
    """B-2 — the config columns, the wall clock, and where the config came from."""
    run = PriorRun(
        job_id="job-old",
        app_name="nightly_etl",
        plan_fingerprint=FP,
        config=_observed_config(),
        config_source="observed",
        wall_clock_ms=612_000,
        task_time_ms=1_840_000,
    )

    payload = run.model_dump()

    assert payload["config"]["shuffle_partitions"] == 200
    assert payload["config"]["executor_memory_mb"] == 8192
    assert payload["config_source"] == "observed"
    assert payload["wall_clock_ms"] == 612_000
    assert run.config_known is True
    assert payload["config_note"] == ""


def test_app_name_is_marked_untrusted():
    """B-3 — app_name reaches the model's context exactly as it does in
    list_runs: chosen by whoever wrote the Spark job, not by Apex."""
    payload = RecallResult(job_id="job-1", status="recalled").model_dump()

    assert "prior_runs[].app_name" in payload["untrusted_fields"]


def test_unknown_config_source_stays_visible():
    """B-4 — a run whose config was never captured must READ as never captured.

    The v0.3 DDL is explicit that Apex captures no SparkConf today, so most
    rows carry six nulls. Presenting those as an observed configuration would
    turn missing data into a recommendation.
    """
    run = PriorRun(job_id="job-old", wall_clock_ms=612_000)

    assert run.config_source == "unknown"
    assert run.config_known is False
    assert run.config_note == CONFIG_UNAVAILABLE
    assert "config_unavailable" in run.model_dump()["config_note"]


def test_config_source_is_never_defaulted_to_observed():
    assert PriorRun.model_fields["config_source"].default == "unknown"
    with pytest.raises(ValidationError):
        PriorRun(job_id="j", config_source="assumed")


def test_a_claimed_observed_source_with_no_config_is_still_flagged():
    """`observed` with six nulls is not an observation, it is a gap wearing a
    label. The note appears anyway."""
    run = PriorRun(job_id="job-old", config_source="observed")

    assert run.config_known is False
    assert run.config_note == CONFIG_UNAVAILABLE


def test_missing_config_is_null_never_zero():
    """"never captured" and "set to 0" are different facts; a 0 sentinel would
    drag every average toward zero and invent a confident recommendation."""
    config = RunConfig()

    assert config.is_empty() is True
    assert set(config.model_dump().values()) == {None}


def test_recall_result_defaults_draw_no_conclusion():
    result = RecallResult(job_id="job-1", status="no_prior_runs")

    assert result.prior_runs == []
    assert result.summary == RecallSummary()
    assert result.summary.compared is False
    assert result.summary.claim == ""
    assert result.summary.noise_floor_pct is None


def test_recall_timestamps_accept_driver_datetimes():
    """A real ClickHouse hands back datetime objects; the wire carries strings.
    This is the exact gap that made every real row fail validation in L2."""
    from datetime import datetime

    run = PriorRun(job_id="j", observed_at=datetime(2026, 8, 19, 9, 0, 0))
    plan = SimilarPlan(
        plan_fingerprint=FP, similarity=1.0, last_seen=datetime(2026, 8, 19, 9, 0, 0)
    )

    assert run.observed_at == "2026-08-19T09:00:00"
    assert plan.last_seen == "2026-08-19T09:00:00"
