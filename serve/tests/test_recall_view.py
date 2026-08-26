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


# --------------------------------------------------------------------------
# recall_similar_runs through the tool layer
#
# The models above constrain what CAN be said; these assert what the tool
# actually says on the three deployments that behave differently.
# --------------------------------------------------------------------------
import asyncio

from apex_mcp.ch import ReadStore
from apex_mcp.server import create_server

FP_NEAR = "b" * 64


class _RecallClient:
    """Routes on the table each statement names."""

    def __init__(
        self,
        *,
        stages: list[dict] | None = None,
        plans: list[dict] | None = None,
        outcomes: list[dict] | None = None,
        tables: tuple[str, ...] = ("plan_memory", "run_outcomes"),
    ) -> None:
        self.stages = stages or []
        self.plans = plans or []
        self.outcomes = outcomes or []
        self.tables = tables

    def query(self, query: str, parameters: dict | None = None):
        if "system.tables" in query:
            rows = [{"name": name} for name in self.tables]
        elif "apex.plan_memory" in query:
            rows = list(self.plans)
        elif "apex.run_outcomes" in query:
            rows = list(self.outcomes)
        else:
            rows = list(self.stages)
        return type("R", (), {"named_results": lambda _s: rows})()


def _stage(fingerprint: str, task_count: int, p50_ms: int) -> dict:
    return {
        "stage_id": 4,
        "stage_attempt": 0,
        "app_id": "app-1",
        "app_name": "nightly_etl",
        "task_count": task_count,
        "shuffle_read_bytes": 0,
        "shuffle_write_bytes": 0,
        "spill_disk_bytes": 0,
        "spill_mem_bytes": 0,
        "gc_time_ms": 0,
        "input_bytes": 0,
        "output_bytes": 0,
        "peak_execution_mem_bytes": 0,
        "p50_ms": p50_ms,
        "p99_ms": p50_ms,
        "plan_fingerprint": fingerprint,
    }


def _outcome(job_id: str, fingerprint: str = FP, wall_clock_ms: int = 600_000) -> dict:
    return {
        "job_id": job_id,
        "app_id": f"app-{job_id}",
        "app_name": "nightly_etl",
        "plan_fingerprint": fingerprint,
        "conf_shuffle_partitions": None,
        "conf_executor_instances": None,
        "conf_executor_cores": None,
        "conf_executor_memory_mb": None,
        "conf_driver_cores": None,
        "conf_driver_memory_mb": None,
        "conf_extra": {},
        "config_source": "unknown",
        "stage_count": 4,
        "task_count": 200,
        "wall_clock_ms": wall_clock_ms,
        "task_time_ms": wall_clock_ms * 3,
        "shuffle_read_bytes": 0,
        "shuffle_write_bytes": 0,
        "spill_disk_bytes": 0,
        "spill_mem_bytes": 0,
        "gc_time_ms": 0,
        "input_bytes": 0,
        "output_bytes": 0,
        "peak_execution_mem_bytes": 0,
        "max_skew_ratio": 1.1,
        "aqe_skew_splits": 0,
        "aqe_coalesces": 1,
        "finding_count": 0,
        "worst_severity": "",
        "outcome_source": "apex",
        "observed_at": "2026-08-12T09:00:00",
    }


def _recall(client: _RecallClient, **arguments) -> dict:
    server = create_server(ReadStore(client))
    result = asyncio.run(
        server.call_tool("recall_similar_runs", {"job_id": "job-current", **arguments})
    )
    return result[1] if isinstance(result, tuple) else result


def test_recall_returns_prior_runs_with_similarity_and_wall_clock():
    """B-2 — prior runs of the shape, with their configs and outcomes."""
    payload = _recall(
        _RecallClient(
            stages=[_stage(FP, task_count=200, p50_ms=300)],
            plans=[
                {
                    "plan_fingerprint": FP_NEAR,
                    "similarity": 0.93,
                    "node_count": 12,
                    "join_count": 1,
                    "agg_count": 1,
                    "exchange_count": 2,
                    "scan_count": 2,
                    "last_seen": "2026-08-19T09:00:00",
                }
            ],
            outcomes=[_outcome("job-old"), _outcome("job-older", wall_clock_ms=700_000)],
        )
    )

    assert payload["status"] == "recalled"
    assert payload["plan_fingerprint"] == FP
    assert [r["job_id"] for r in payload["prior_runs"]] == ["job-old", "job-older"]
    assert payload["prior_runs"][0]["wall_clock_ms"] == 600_000
    assert payload["prior_runs"][0]["match"] == "exact"
    assert payload["prior_runs"][0]["similarity"] == 1.0
    # The exact tier is listed first and needs no embedding.
    assert payload["similar_plans"][0]["match"] == "exact"
    assert payload["similar_plans"][1]["plan_fingerprint"] == FP_NEAR
    assert "prior_runs[].app_name" in payload["untrusted_fields"]


def test_recall_without_a_floor_calls_no_configuration_better():
    """The floor rule, end to end: a 14% spread and no verdict."""
    payload = _recall(
        _RecallClient(
            stages=[_stage(FP, task_count=200, p50_ms=300)],
            outcomes=[_outcome("job-old"), _outcome("job-older", wall_clock_ms=700_000)],
        )
    )

    assert payload["summary"]["compared"] is False
    assert payload["summary"]["faster_job_id"] is None
    assert "better" not in payload["summary"]["claim"].lower()


def test_recall_on_an_unseen_shape_says_so():
    """B-3 — nothing matched, and the nearest unrelated shape is not offered."""
    payload = _recall(
        _RecallClient(stages=[_stage(FP, task_count=200, p50_ms=300)], outcomes=[])
    )

    assert payload["status"] == "no_prior_runs"
    assert payload["prior_runs"] == []
    assert any("not returned in its place" in note for note in payload["notes"])


def test_recall_reports_memory_unavailable_on_an_older_deployment():
    """B-4 — no v0.3 tables is "no history to read", not "no history"."""
    payload = _recall(
        _RecallClient(stages=[_stage(FP, task_count=200, p50_ms=300)], tables=())
    )

    assert payload["status"] == "memory_unavailable"
    assert payload["prior_runs"] == []
    assert any("not present" in note for note in payload["notes"])


def test_recall_without_a_plan_shape_does_not_recall_a_null_fingerprint():
    """The all-zero fixture fingerprint is not a plan shape; recalling on it
    would return every degenerate run in the store as a perfect match."""
    payload = _recall(
        _RecallClient(stages=[_stage("0" * 64, task_count=200, p50_ms=300)])
    )

    assert payload["status"] == "no_plan_shape"
    assert payload["similar_plans"] == []


def test_recall_picks_the_shape_the_run_spent_its_time_in():
    """Many trivial stages must not outrank the one that costs money."""
    payload = _recall(
        _RecallClient(
            stages=[
                _stage(FP_NEAR, task_count=1, p50_ms=1),
                _stage(FP_NEAR, task_count=1, p50_ms=1),
                _stage(FP_NEAR, task_count=1, p50_ms=1),
                _stage(FP, task_count=200, p50_ms=3000),
            ],
            outcomes=[_outcome("job-old")],
        )
    )

    assert payload["plan_fingerprint"] == FP
