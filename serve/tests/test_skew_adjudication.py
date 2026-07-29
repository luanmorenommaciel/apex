"""The P0 contradiction: serve's fixed skew thresholds vs engine's closed form.

Stage 4 of the real P0 job (`app-20260724160310-0000`): p99/p50 = 21.62x over
50 tasks at ~278 B/task, no join evidence, and apex.findings EMPTY for that
stage — engine's closed form (CONTRACT.md rule 1: tail-bound iff
p99/p50 > (n_tasks - 1)/(slots - 1), plus the 1 MiB/task volume bound) emits
NOTHING for it. serve used to grade the same row CRITICAL off SKEW_RATIO_CRIT
= 20.0, so one MCP response carried two contradictory verdicts and the wrong
one was louder.

These tests pin the split this fix lands on:

  a SYMPTOM is a MEASUREMENT  — "p99/p50 = 21.62x across 50 tasks, 278 B/task"
  a VERDICT  is an ADJUDICATION — "critical skew, fix with X" (engine's job;
                                Spark's own AQE skew_split is execution-scoped
                                and adjudicates no individual stage)
"""

from __future__ import annotations

from apex_mcp import diagnose
from tests.conftest import stage_row, transition_row

MB = 1 << 20

# The real P0 stage-4 numbers.
P0_RATIO = 21.62
P0_TASKS = 50
P0_BYTES_PER_TASK = 278


def p0_stage4_row() -> dict:
    return stage_row(
        4,
        p50_ms=37,
        p99_ms=800,  # 800/37 = 21.62x
        task_count=P0_TASKS,
        shuffle_write_bytes=P0_BYTES_PER_TASK * P0_TASKS,  # 13,900 B total
    )


def test_p0_stage4_emits_no_skew_verdict():
    """The exact row that used to render CRITICAL against an empty findings
    table. The measurement must survive; the verdict must not."""
    result = diagnose.analyze("p0-job", [p0_stage4_row()], [], [])

    stage = result.stages[0]
    assert stage.p99_p50_ratio == P0_RATIO  # the measurement is still served

    # ...but no symptom may contradict engine's (empty) adjudication.
    assert all(s.symptom != "skew" for s in result.symptoms)
    assert all(
        s.severity not in ("warning", "critical", "blocker")
        for s in result.symptoms
    )
    assert result.primary_symptom != "skew"


def test_fallback_reports_real_skew_as_an_unadjudicated_measurement():
    """Same ratio with real volume (100 MiB/task): the un-analyzed-job fallback
    must keep working — as a labelled measurement, never a severity verdict."""
    row = stage_row(
        4, p50_ms=37, p99_ms=800, task_count=50,
        shuffle_read_bytes=50 * 10 * MB,
    )
    result = diagnose.analyze("job-1", [row], [], [])

    skew = next(s for s in result.symptoms if s.symptom == "skew")
    assert skew.severity == "info"
    assert skew.adjudicated is False
    assert "unadjudicated" in skew.evidence
    # Rule 1 inverted, from the observation alone: 1 + 49/21.62 ~= 3.3 slots.
    # serve says what a verdict would NEED instead of guessing a width.
    assert "3.3 slots" in skew.evidence


def test_a_skew_split_adjudicates_no_individual_stage():
    """Live gate run `app-20260729180235-0044`: the only skew symptom clearing
    the volume floor was stage 25 at 1.03x over 8 tasks — balanced — and a
    skew_split elsewhere in the job promoted it to "critical skew, confirmed by
    Spark itself", with evidence reading "unadjudicated measurement… is
    engine's call" in the same breath.

    A skew_split is EXECUTION-scoped: contract v0.2 keys transitions by
    (job_id, execution_id) and carries no execution→stage map, so it proves
    skew existed SOMEWHERE in the execution, never that a given stage is
    skewed. Engine places its AQE finding at stage_id -1 for exactly this
    reason. A stage-scoped symptom cannot carry an execution-scoped verdict.
    """
    row = stage_row(
        25, p50_ms=1000, p99_ms=1030, task_count=8,  # 1.03x — balanced
        shuffle_read_bytes=8 * 2 * MB,               # 2 MiB/task: clears the floor
    )
    result = diagnose.analyze("job-1", [row], [], [transition_row("skew_split")])

    skew = next(s for s in result.symptoms if s.symptom == "skew")
    assert skew.severity == "info"
    assert skew.adjudicated is False
    assert skew.ground_truth is False
    assert "unadjudicated" in skew.evidence
    # The ground truth survives — execution-scoped, in the job-level surface
    # where it belongs, and saying so.
    assert any("execution" in note for note in result.aqe_ground_truth)


def test_aqe_skew_split_makes_no_stage_scoped_adjudication():
    """Spark's own runtime decision is ground truth serve CAN report — but only
    at the decision's own scope. A 5x tail with real volume keeps its
    measurement; the split adds an execution-scoped note, not a verdict."""
    row = stage_row(
        4, p50_ms=100, p99_ms=500, task_count=50,
        shuffle_read_bytes=50 * 10 * MB,
    )
    result = diagnose.analyze("job-1", [row], [], [transition_row("skew_split")])
    skew = next(s for s in result.symptoms if s.symptom == "skew")
    assert skew.ground_truth is False
    assert skew.adjudicated is False
    assert skew.severity == "info"
    assert any("execution" in note for note in result.aqe_ground_truth)


def test_compare_runs_does_not_report_noise_as_regression():
    """Rule 2: the measured shape-level floor is 32-59% at 8 tasks and 32.9% at
    100 tasks, so the flat REGRESSION_PCT = 0.20 sat BELOW the floor — a +25%
    p99 move is unresolvable noise, not a regression. Without a floor, compare
    must render the delta as a measurement only."""
    before = [stage_row(2, p99_ms=1000)]
    after = [stage_row(2, p99_ms=1250)]  # +25%: over the old 20% bar, under the floor
    result = diagnose.compare("a", "b", before, after, [], [])

    assert not any("p99_regressed" in r for r in result.regressions)
    assert result.status != "regressed"
    # The number stays visible as data — rule 2 forbids the verdict, not the measurement.
    delta = next(m for m in result.stages[0].metrics if m.metric == "p99_ms")
    assert delta.pct_change == 0.25
    assert any("noise floor" in note for note in result.notes)


def test_compare_runs_adjudicates_only_with_a_supplied_floor():
    """A caller who measured the floor may adjudicate against it."""
    before = [stage_row(2, p99_ms=1000)]
    after = [stage_row(2, p99_ms=1500)]  # +50%
    unresolved = diagnose.compare("a", "b", before, after, [], [], noise_floor_pct=0.60)
    resolved = diagnose.compare("a", "b", before, after, [], [], noise_floor_pct=0.40)

    assert not any("p99_regressed" in r for r in unresolved.regressions)
    assert any("p99_regressed" in r for r in resolved.regressions)
    assert resolved.status == "regressed"
