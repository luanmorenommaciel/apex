"""Heuristics: symptom detection, AQE ground truth, run comparison."""

from __future__ import annotations

import pytest

from apex_mcp import diagnose
from apex_mcp.models import PriorRun, RunConfig
from tests.conftest import (
    FINGERPRINT_A,
    FINGERPRINT_B,
    finding_row,
    stage_row,
    transition_row,
)

MB = 1 << 20
GB = 1 << 30


# -- analyze ---------------------------------------------------------------
def test_missing_job_reports_not_found_and_queries_nothing_else():
    result = diagnose.analyze("nope", [], [], [])
    assert result.status == "not_found"
    assert result.stages == []
    assert result.worst_stage_id is None


def test_clean_run_is_healthy():
    rows = [stage_row(1, p50_ms=100, p99_ms=110), stage_row(2, p50_ms=90, p99_ms=95)]
    result = diagnose.analyze("job-1", rows, [], [])
    assert result.status == "healthy"
    assert result.primary_symptom == "healthy"
    assert result.symptoms == []


def test_skew_is_reported_as_a_measurement_not_a_verdict():
    """A big ratio over real volume is surfaced — at info, unadjudicated.
    Grading it by the ratio was the P0 false positive (CONTRACT.md rule 1)."""
    result = diagnose.analyze(
        "job-1",
        [stage_row(4, p50_ms=20, p99_ms=460, shuffle_read_bytes=50 * 10 * MB)],
        [],
        [],
    )
    symptom = result.symptoms[0]
    assert result.primary_symptom == "skew"
    assert result.worst_stage_id == 4
    assert symptom.severity == "info"
    assert symptom.adjudicated is False
    assert "p99/p50" in symptom.evidence


def test_single_task_stage_is_never_called_skewed():
    """One task cannot have a tail relative to itself."""
    result = diagnose.analyze(
        "job-1", [stage_row(1, p50_ms=10, p99_ms=5000, task_count=1)], [], []
    )
    assert all(s.symptom != "skew" for s in result.symptoms)


def test_spill_magnitude_uses_both_memory_and_disk():
    """The two spill columns are one event: 48 MiB live -> 381 KiB serialized.

    Ranking off the disk number alone under-reads the problem by ~130x.
    """
    rows = [stage_row(26, spill_disk_bytes=390_465, spill_mem_bytes=50_331_552)]
    result = diagnose.analyze("job-1", rows, [], [])
    spill = next(s for s in result.symptoms if s.symptom == "disk_spill")
    assert "48.0 MiB" in spill.evidence  # memory side is reported
    assert "381.3 KiB" in spill.evidence  # disk side too


def test_memory_only_spill_is_typed_separately():
    rows = [stage_row(3, spill_mem_bytes=200 * MB)]
    result = diagnose.analyze("job-1", rows, [], [])
    assert result.symptoms[0].symptom == "memory_spill"
    assert "nothing on disk yet" in result.symptoms[0].evidence


def test_symptoms_rank_by_severity_then_time_share():
    """Bytes and ratios are different units — severity must dominate."""
    rows = [
        stage_row(4, p50_ms=20, p99_ms=460, gc_time_ms=400),  # gc 40%, critical
        stage_row(26, p99_ms=1335, p50_ms=733, task_count=2,
                  spill_disk_bytes=390_465, spill_mem_bytes=50_331_552),  # spill, info
    ]
    result = diagnose.analyze("job-1", rows, [], [])
    assert result.symptoms[0].severity == "critical"
    assert result.symptoms[0].stage_id == 4
    assert result.symptoms[-1].severity == "info"


def test_gc_pressure_uses_share_of_task_time_not_raw_ms():
    rows = [stage_row(5, p50_ms=100, p99_ms=100, task_count=10, gc_time_ms=400)]
    result = diagnose.analyze("job-1", rows, [], [])
    gc = next(s for s in result.symptoms if s.symptom == "gc_pressure")
    assert gc.severity == "critical"  # 400 / (100*10) = 40%
    assert "40%" in gc.evidence


def test_heavy_shuffle_needs_real_volume():
    small = diagnose.analyze("job-1", [stage_row(1, shuffle_read_bytes=10 * MB)], [], [])
    big = diagnose.analyze("job-1", [stage_row(1, shuffle_read_bytes=9 * GB)], [], [])
    assert all(s.symptom != "heavy_shuffle" for s in small.symptoms)
    assert big.symptoms[0].symptom == "heavy_shuffle"
    assert big.symptoms[0].severity == "critical"


# -- AQE ground truth ------------------------------------------------------
def test_skew_split_is_execution_scoped_and_promotes_no_stage_symptom():
    """A skew_split proves skew existed SOMEWHERE in the execution (contract
    v0.2 has no execution→stage map), so it is a job-level note — never a
    per-stage verdict. Before this split was enforced, the mere presence of a
    split promoted every skew symptom in the job to critical."""
    rows = [stage_row(4, p50_ms=100, p99_ms=500, shuffle_read_bytes=50 * 10 * MB)]
    plain = diagnose.analyze("job-1", rows, [], [])
    assert plain.symptoms[0].severity == "info"
    assert plain.symptoms[0].ground_truth is False

    confirmed = diagnose.analyze("job-1", rows, [], [transition_row("skew_split")])
    # the symptom is unchanged — still an unadjudicated measurement...
    assert confirmed.symptoms[0].severity == "info"
    assert confirmed.symptoms[0].adjudicated is False
    assert confirmed.symptoms[0].ground_truth is False
    # ...while the ground truth is reported at its own scope, saying so
    assert any("execution" in note for note in confirmed.aqe_ground_truth)


def test_coalesce_is_not_evidence_of_skew():
    """Contract v0.2, verified on real P0 data: coalescing means
    spark.sql.shuffle.partitions is over-sized, NOT that the data is skewed.
    Promoting it would be a false positive in the demo."""
    rows = [stage_row(4, p50_ms=100, p99_ms=500, shuffle_read_bytes=50 * 10 * MB)]
    result = diagnose.analyze("job-1", rows, [], [transition_row("coalesce")])
    assert result.symptoms[0].ground_truth is False
    assert result.symptoms[0].severity == "info"
    assert any("NOT evidence of skew" in note for note in result.aqe_ground_truth)


def test_best_effort_transitions_do_not_confer_ground_truth():
    rows = [stage_row(4, p50_ms=100, p99_ms=500, shuffle_read_bytes=50 * 10 * MB)]
    result = diagnose.analyze(
        "job-1", rows, [], [transition_row("skew_split", confidence="BEST_EFFORT")]
    )
    assert result.symptoms[0].ground_truth is False


def test_findings_absence_is_stated_not_hidden():
    result = diagnose.analyze("job-1", [stage_row(1)], [], [])
    assert any("apex.findings holds no rows" in note for note in result.notes)


# -- compare ---------------------------------------------------------------
def test_run_against_itself_reports_no_deltas():
    rows = [stage_row(1), stage_row(2, p50_ms=50, p99_ms=60)]
    result = diagnose.compare("a", "a", rows, rows, [], [])
    assert result.status == "unchanged"
    assert result.regressions == []
    assert result.plan_fingerprint_changed is False
    assert {s.aligned_by for s in result.stages} == {"stage_id+plan_fingerprint"}


def test_missing_run_is_not_comparable():
    result = diagnose.compare("a", "b", [], [stage_row(1)], [], [])
    assert result.status == "not_comparable"
    assert result.missing_job_ids == ["a"]


def test_spill_introduced_is_flagged():
    before = [stage_row(2)]
    after = [stage_row(2, spill_disk_bytes=500 * MB)]
    result = diagnose.compare("a", "b", before, after, [], [])
    assert result.status == "regressed"
    assert any("spill_introduced" in r for r in result.regressions)


def test_spill_eliminated_is_an_improvement():
    before = [stage_row(2, spill_disk_bytes=500 * MB)]
    after = [stage_row(2)]
    result = diagnose.compare("a", "b", before, after, [], [])
    assert result.status == "improved"
    assert any("spill_eliminated" in i for i in result.improvements)


def test_p99_regression_needs_a_floor_and_absolute_movement():
    """A 1ms -> 2ms move is 100% worse and completely meaningless; a big move
    still needs a measured floor before it may be called a regression."""
    noise = diagnose.compare(
        "a", "b", [stage_row(2, p99_ms=1)], [stage_row(2, p99_ms=2)], [], [],
        noise_floor_pct=0.20,
    )
    real = diagnose.compare(
        "a", "b", [stage_row(2, p99_ms=1000)], [stage_row(2, p99_ms=3000)], [], [],
        noise_floor_pct=0.20,
    )
    assert not any("p99_regressed" in r for r in noise.regressions)
    assert any("p99_regressed" in r for r in real.regressions)


def test_stages_align_by_fingerprint_when_stage_ids_shift():
    """Stage ids are not stable across runs; the literal-normalized
    fingerprint is. Same work must still be compared."""
    before = [stage_row(4, plan_fingerprint=FINGERPRINT_A, p99_ms=1000)]
    after = [stage_row(19, plan_fingerprint=FINGERPRINT_A, p99_ms=3000)]
    result = diagnose.compare("a", "b", before, after, [], [], noise_floor_pct=0.20)
    pair = result.stages[0]
    assert pair.aligned_by == "plan_fingerprint"
    assert pair.baseline_stage_id == 4
    assert pair.current_stage_id == 19
    assert pair.plan_changed is False
    assert any("p99_regressed" in r for r in result.regressions)


def test_plan_change_at_the_same_stage_id_is_flagged_as_not_like_for_like():
    before = [stage_row(19, plan_fingerprint=FINGERPRINT_A)]
    after = [stage_row(19, plan_fingerprint=FINGERPRINT_B)]
    result = diagnose.compare("a", "b", before, after, [], [])
    pair = result.stages[0]
    assert pair.plan_changed is True
    assert pair.aligned_by == "stage_id"
    assert result.plan_fingerprint_changed is True
    assert any("plan_fingerprint_changed" in r for r in result.regressions)
    assert any("literal-normalized" in n for n in result.notes)


def test_unmatched_stages_are_reported_per_side():
    result = diagnose.compare(
        "a", "b",
        [stage_row(1, plan_fingerprint=FINGERPRINT_A)],
        [stage_row(2, plan_fingerprint=FINGERPRINT_B)],
        [], [],
    )
    sides = {s.present_in for s in result.stages}
    assert sides == {"baseline_only", "current_only"}


# -- findings comparison (contract v0.2 confidence_score) ------------------
def test_new_finding_is_a_regression_ranked_on_raw_confidence_score():
    after = [finding_row(job_id="b", confidence_score=0.93)]
    result = diagnose.compare("a", "b", [stage_row(2)], [stage_row(2)], [], after)
    assert result.status == "regressed"
    delta = result.findings[0]
    assert delta.change == "introduced"
    assert delta.current_confidence_score == 0.93
    assert any("finding_introduced" in r for r in result.regressions)


def test_resolved_finding_is_an_improvement():
    before = [finding_row(job_id="a", confidence_score=0.9)]
    result = diagnose.compare("a", "b", [stage_row(2)], [stage_row(2)], before, [])
    assert result.status == "improved"
    assert result.findings[0].change == "resolved"


def test_confidence_score_beats_the_display_tier():
    """Both rows read HIGH, but the raw score moved — the tier would hide it."""
    before = [finding_row(job_id="a", confidence="HIGH", confidence_score=0.80)]
    after = [finding_row(job_id="b", confidence="HIGH", confidence_score=0.99)]
    result = diagnose.compare("a", "b", [stage_row(2)], [stage_row(2)], before, after)
    assert result.findings[0].change == "confidence_up"
    assert result.findings[0].baseline_confidence_score == 0.80


def test_enum_tier_is_the_fallback_when_score_is_absent():
    """Rows written before the additive column default to 0.0."""
    rows = [finding_row(job_id="a", confidence="HIGH", confidence_score=0.0)]
    result = diagnose.compare("a", "b", [stage_row(2)], [stage_row(2)], rows, [])
    assert result.findings[0].baseline_confidence_score == 0.9  # HIGH tier


def test_small_confidence_wobble_is_ignored():
    before = [finding_row(job_id="a", confidence_score=0.90)]
    after = [finding_row(job_id="b", confidence_score=0.94)]
    result = diagnose.compare("a", "b", [stage_row(2)], [stage_row(2)], before, after)
    assert result.findings == []
    assert result.status == "unchanged"


# --------------------------------------------------------------------------
# auto-baseline: identical plan shape, or nothing
# --------------------------------------------------------------------------
def test_auto_baseline_picks_same_fingerprint():
    """B-1 — the newest prior run whose plan shape matches, not just the newest."""
    current = [stage_row(1, plan_fingerprint=FINGERPRINT_A)]
    candidates = [
        ("job-newer-different-plan", [stage_row(1, plan_fingerprint=FINGERPRINT_B)]),
        ("job-older-same-plan", [stage_row(1, plan_fingerprint=FINGERPRINT_A)]),
    ]

    chosen, reason = diagnose.select_baseline("job-current", current, candidates)

    assert chosen == "job-older-same-plan"
    assert "identical plan shape" in reason


def test_auto_baseline_refuses_across_plan_change():
    """B-2 — a silently wrong baseline yields a confident wrong answer."""
    current = [stage_row(1, plan_fingerprint=FINGERPRINT_A)]
    candidates = [("job-other", [stage_row(1, plan_fingerprint=FINGERPRINT_B)])]

    chosen, reason = diagnose.select_baseline("job-current", current, candidates)

    assert chosen is None
    assert "plan change" in reason
    assert "baseline_job_id" in reason


def test_explicit_baseline_is_unchanged():
    """B-3 — supplying a baseline behaves exactly as before."""
    baseline = [stage_row(1, p50_ms=100, p99_ms=100, plan_fingerprint=FINGERPRINT_A)]
    current = [stage_row(1, p50_ms=100, p99_ms=100, plan_fingerprint=FINGERPRINT_A)]

    result = diagnose.compare("base", "cur", baseline, current, [], [])

    assert result.baseline_job_id == "base"
    assert result.current_job_id == "cur"
    assert result.status == "unchanged"
    assert result.plan_fingerprint_changed is False


def test_auto_baseline_skips_the_current_run_and_empty_candidates():
    """The current run always matches itself; it must never be its own baseline."""
    current = [stage_row(1, plan_fingerprint=FINGERPRINT_A)]
    candidates = [
        ("job-current", current),
        ("job-empty", []),
        ("job-match", [stage_row(1, plan_fingerprint=FINGERPRINT_A)]),
    ]

    chosen, _ = diagnose.select_baseline("job-current", current, candidates)

    assert chosen == "job-match"


def test_auto_baseline_refuses_when_the_current_run_has_no_fingerprint():
    """Without a fingerprint there is no shape to match, so do not guess."""
    current = [stage_row(1, plan_fingerprint="")]

    chosen, reason = diagnose.select_baseline("job-current", current, [("j", current)])

    assert chosen is None
    assert "no plan_fingerprint" in reason


# --------------------------------------------------------------------------
# Cross-run recall — never call a configuration better without a floor
#
# The whole value of cross-run memory is distinguishing "this config is better"
# from "this run happened to be faster". Ranking a shape's prior runs by wall
# clock builds a machine for confusing the two, so the word "better" is only
# reachable through a floor the caller measured.
# --------------------------------------------------------------------------
def _prior_run(
    job_id: str,
    wall_clock_ms: int,
    *,
    shuffle_partitions: int | None = None,
    config_source: str = "unknown",
) -> PriorRun:
    config = RunConfig(
        shuffle_partitions=shuffle_partitions,
        executor_instances=4,
        executor_cores=4,
        executor_memory_mb=8192,
        driver_cores=2,
        driver_memory_mb=4096,
    ) if shuffle_partitions is not None else RunConfig()
    return PriorRun(
        job_id=job_id,
        wall_clock_ms=wall_clock_ms,
        config=config,
        config_source=config_source,
    )


def test_no_floor_means_no_better_claim():
    """B-1 — runs are measurements; nothing is called better."""
    summary = diagnose.summarise_recall(
        [_prior_run("job-fast", 60_000), _prior_run("job-slow", 120_000)]
    )

    assert summary.compared is False
    assert summary.faster_job_id is None
    assert summary.noise_floor_pct is None
    assert "better" not in summary.claim.lower()
    assert "measurements" in summary.claim
    assert any("noise floor" in note for note in summary.notes)


def test_difference_inside_floor_is_indistinguishable():
    """B-3 — a 10% spread under a 20% floor is run-to-run variation."""
    summary = diagnose.summarise_recall(
        [_prior_run("job-a", 100_000), _prior_run("job-b", 110_000)],
        noise_floor_pct=0.20,
    )

    assert summary.compared is False
    assert summary.faster_job_id is None
    assert "indistinguishable" in summary.claim
    assert "20.0%" in summary.claim
    assert "better" not in summary.claim.lower()
    assert any("not proof of zero change" in note for note in summary.notes)


def test_single_prior_run_draws_no_comparison():
    """B-4 — one run cannot measure its own dispersion."""
    summary = diagnose.summarise_recall(
        [_prior_run("job-only", 60_000)], noise_floor_pct=0.05
    )

    assert summary.compared is False
    assert summary.pct_difference is None
    assert "cannot measure its own dispersion" in summary.claim
    assert "better" not in summary.claim.lower()


def test_cleared_floor_is_named():
    """B-2 — above the floor a verdict is allowed, and the floor is named."""
    summary = diagnose.summarise_recall(
        [
            _prior_run("job-fast", 60_000, shuffle_partitions=200, config_source="observed"),
            _prior_run("job-slow", 120_000, shuffle_partitions=800, config_source="observed"),
        ],
        noise_floor_pct=0.15,
    )

    assert summary.compared is True
    assert summary.faster_job_id == "job-fast"
    assert summary.slower_job_id == "job-slow"
    assert summary.noise_floor_pct == pytest.approx(0.15)
    assert "15.0%" in summary.claim
    assert "clears" in summary.claim
    assert summary.attributable_to_config is True
    assert "better" in summary.claim


def test_a_real_difference_with_one_config_is_not_credited_to_tuning():
    """CONTRACT.md rule 3 — clearing the floor is necessary, not sufficient.

    Byte-identical work across four runs still spanned 18.65% on this system.
    With one captured configuration there is no experiment in the history, so
    the difference is real and still not attributable.
    """
    summary = diagnose.summarise_recall(
        [
            _prior_run("job-fast", 60_000, shuffle_partitions=200, config_source="observed"),
            _prior_run("job-slow", 120_000, shuffle_partitions=200, config_source="observed"),
        ],
        noise_floor_pct=0.15,
    )

    assert summary.compared is True
    assert summary.attributable_to_config is False
    assert "better" not in summary.claim.lower()
    assert any("NOT creditable to configuration" in note for note in summary.notes)


def test_uncaptured_configs_are_not_two_configurations():
    """Two runs whose configs were never captured are one absence, twice."""
    summary = diagnose.summarise_recall(
        [_prior_run("job-fast", 60_000), _prior_run("job-slow", 120_000)],
        noise_floor_pct=0.15,
    )

    assert summary.compared is True
    assert summary.attributable_to_config is False
    assert any("CONTRACT.md rule 3" in note for note in summary.notes)


def test_recall_is_never_summarised_by_sorting_on_wall_clock():
    """The anti-pattern stated as a test: the fastest run is not promoted to
    "the best configuration" just for being first in a sorted list."""
    runs = [
        _prior_run("job-fast", 10_000),
        _prior_run("job-mid", 11_000),
        _prior_run("job-slow", 12_000),
    ]

    summary = diagnose.summarise_recall(runs, noise_floor_pct=0.30)

    assert summary.compared is False
    assert summary.faster_job_id is None
    assert "indistinguishable" in summary.claim


def test_zero_wall_clock_runs_are_not_fast_runs():
    """A missing duration reads as 0ms and would win every ranking."""
    summary = diagnose.summarise_recall(
        [_prior_run("job-unmeasured", 0), _prior_run("job-real", 60_000)],
        noise_floor_pct=0.05,
    )

    assert summary.compared is False
    assert "cannot measure its own dispersion" in summary.claim


def test_no_prior_runs_says_so():
    summary = diagnose.summarise_recall([], noise_floor_pct=0.05)

    assert summary.compared is False
    assert summary.claim == ""
    assert any("No prior runs" in note for note in summary.notes)
