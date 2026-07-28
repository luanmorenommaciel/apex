"""Heuristics: symptom detection, AQE ground truth, run comparison."""

from __future__ import annotations

from apex_mcp import diagnose
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
def test_skew_split_promotes_the_skew_heuristic_to_ground_truth():
    rows = [stage_row(4, p50_ms=100, p99_ms=500, shuffle_read_bytes=50 * 10 * MB)]
    plain = diagnose.analyze("job-1", rows, [], [])
    assert plain.symptoms[0].severity == "info"
    assert plain.symptoms[0].ground_truth is False

    confirmed = diagnose.analyze("job-1", rows, [], [transition_row("skew_split")])
    assert confirmed.symptoms[0].ground_truth is True
    assert confirmed.symptoms[0].severity == "critical"
    assert "Confirmed by an AQE runtime decision" in confirmed.summary


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
