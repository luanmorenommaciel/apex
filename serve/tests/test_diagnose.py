"""Heuristics: symptom detection, AQE ground truth, run comparison."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from apex_mcp import diagnose
from apex_mcp.models import Coverage, Diagnosis
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





# -- share of tail ---------------------------------------------------------
def test_stage_carries_share_of_tail():
    """B-1 — analyze() already sums p99 to rank stages; keep the shape."""
    rows = [
        stage_row(1, p99_ms=800),
        stage_row(2, p99_ms=150),
        stage_row(3, p99_ms=50),
    ]

    result = diagnose.analyze("job-1", rows, [], [])

    by_id = {s.stage_id: s for s in result.stages}
    assert by_id[1].tail_share == 0.8
    assert by_id[2].tail_share == 0.15
    assert by_id[3].tail_share == 0.05
    assert sum(s.tail_share for s in result.stages) == 1.0


def test_dominant_stage_is_named_alone():
    """B-2 — "stage 1 is 80% of the tail" beats a sorted list to read."""
    rows = [
        stage_row(1, p99_ms=800),
        stage_row(2, p99_ms=150),
        stage_row(3, p99_ms=50),
    ]

    result = diagnose.analyze("job-1", rows, [], [])

    assert result.tail_dominant_stage_ids == [1]
    assert any("80%" in note for note in result.notes)


def test_even_stages_name_no_bottleneck():
    """B-3 — no bottleneck exists, so naming one sends the reader to optimize
    a stage that is merely first in a tie."""
    rows = [stage_row(n, p99_ms=100) for n in (1, 2, 3, 4)]

    result = diagnose.analyze("job-1", rows, [], [])

    assert result.tail_dominant_stage_ids == []
    assert all(s.tail_share == 0.25 for s in result.stages)
    assert not any("tail time" in note for note in result.notes)


def test_a_single_stage_is_not_its_own_bottleneck():
    """One stage owns 100% of its own tail, which says nothing at all."""
    result = diagnose.analyze("job-1", [stage_row(1, p99_ms=500)], [], [])

    assert result.tail_dominant_stage_ids == []


def test_two_stages_share_the_tail_when_neither_dominates():
    """The set is the SMALLEST covering most of the tail, not always one."""
    rows = [
        stage_row(1, p99_ms=400),
        stage_row(2, p99_ms=350),
        stage_row(3, p99_ms=150),
        stage_row(4, p99_ms=100),
    ]

    result = diagnose.analyze("job-1", rows, [], [])

    assert result.tail_dominant_stage_ids == [1, 2]


def test_tail_share_survives_to_the_summary_level():
    """The point of the unit: the bottleneck is readable without the stages."""
    rows = [stage_row(1, p99_ms=800), stage_row(2, p99_ms=200)]

    summary = diagnose.trim(diagnose.analyze("job-1", rows, [], []), "summary")

    assert summary.stages == []
    assert summary.tail_dominant_stage_ids == [1]


def test_the_tail_share_field_does_not_claim_a_scheduling_critical_path():
    """B-4 — p99 stands in for wall time and stages overlap, so the honest
    name is share of tail. A client reading the schema must see that."""
    schema = json.dumps(Diagnosis.model_json_schema()).lower()

    assert "share of tail" in schema
    assert "not a scheduling critical path" in schema


# -- coverage: what the verdict is standing on -----------------------------
def test_diagnosis_reports_coverage():
    """B-1 — stages seen, findings seen, and how old the newest event is."""
    rows = [
        stage_row(1, ts="2026-08-20T10:00:00+00:00"),
        stage_row(2, ts="2026-08-20T10:05:00+00:00"),
    ]

    result = diagnose.analyze(
        "job-1",
        rows,
        [finding_row()],
        [transition_row("skew_split")],
        now=datetime(2026, 8, 20, 10, 6, tzinfo=timezone.utc),
    )

    assert result.coverage.stages_observed == 2
    assert result.coverage.findings_observed == 1
    assert result.coverage.plan_transitions_observed == 1
    # the NEWEST event, not the first one seen
    assert result.coverage.newest_event_ts == "2026-08-20T10:05:00+00:00"
    assert result.coverage.newest_event_age_seconds == 60.0


def test_thin_coverage_is_visible_on_a_healthy_verdict():
    """B-3 — a healthy verdict must say how much it looked at.

    W1: without this, one stage that happened to be clean and a job whose
    telemetry was mostly dropped produce the same confident "healthy".
    """
    result = diagnose.analyze("job-1", [stage_row(1, p50_ms=100, p99_ms=110)], [], [])

    assert result.status == "healthy"
    # the coverage rides on the healthy path too — the easy branch to forget
    assert result.coverage.stages_observed == 1
    assert result.coverage.findings_observed == 0
    # and the verdict itself is scoped to what was observed
    assert "observed" in result.summary


def test_coverage_survives_trimming_so_an_empty_array_stays_legible():
    """Trimming empties arrays; coverage is what keeps them readable."""
    full = _rich_diagnosis()

    summary = diagnose.trim(full, "summary")

    assert summary.findings == []
    assert summary.coverage.findings_observed == full.coverage.findings_observed == 1


def test_ingest_age_is_reported_not_judged():
    """B-2 — Apex reports the number and owns no staleness threshold.

    A nightly batch and a streaming job disagree about what an hour means, so
    a false "stale" would be worse than no claim at all.
    """
    rows = [stage_row(1, ts="2026-08-20T04:00:00+00:00")]

    result = diagnose.analyze(
        "job-1", rows, [], [], now=datetime(2026, 8, 20, 10, 0, tzinfo=timezone.utc)
    )

    assert result.coverage.newest_event_age_seconds == 6 * 3600.0
    # nothing anywhere in the payload grades that number
    blob = result.model_dump_json().lower()
    for verdict in ("stale", "fresh", "outdated", "up to date", "up-to-date"):
        assert verdict not in blob, f"Apex judged ingest age: {verdict!r}"
    # ...and the schema says so, so a client cannot expect a verdict either
    described = Coverage.model_json_schema()["properties"]
    age = described["newest_event_age_seconds"]["description"].lower()
    assert "never judged" in age


def test_a_missing_timestamp_reads_unknown_not_fresh():
    """None must never be mistaken for age zero."""
    result = diagnose.analyze("job-1", [stage_row(1)], [], [])

    assert result.coverage.newest_event_age_seconds is None
    assert result.coverage.newest_event_ts is None
    assert any("UNKNOWN" in note for note in result.notes)


def test_an_unparseable_timestamp_does_not_break_the_diagnosis():
    """A bad ts is a missing ts, never an exception inside a diagnosis."""
    result = diagnose.analyze("job-1", [stage_row(1, ts="not-a-timestamp")], [], [])

    assert result.status == "healthy"
    assert result.coverage.newest_event_age_seconds is None


# -- detail levels ---------------------------------------------------------
def _rich_diagnosis():
    """A diagnosis with something in every array, so trimming is observable."""
    rows = [
        stage_row(4, p50_ms=20, p99_ms=460, shuffle_read_bytes=50 * 10 * MB),
        stage_row(26, spill_disk_bytes=390_465, spill_mem_bytes=50_331_552),
    ]
    result = diagnose.analyze(
        "job-1", rows, [finding_row()], [transition_row("skew_split")]
    )
    assert result.stages and result.symptoms and result.findings
    assert result.plan_transitions and result.aqe_ground_truth
    return result


def test_summary_omits_stage_and_finding_arrays():
    """B-1 — the default answer is the verdict, not a data dump to triage."""
    full = _rich_diagnosis()

    summary = diagnose.trim(full, "summary")

    assert summary.stages == []
    assert summary.symptoms == []
    assert summary.findings == []
    assert summary.plan_transitions == []
    # the verdict — and the AQE note that stops a reader misreading skew —
    # survive, because they are what the caller actually asked for
    assert summary.status == full.status
    assert summary.worst_stage_id == full.worst_stage_id
    assert summary.primary_symptom == full.primary_symptom
    assert summary.summary == full.summary
    assert summary.aqe_ground_truth == full.aqe_ground_truth
    # an emptied array is not the same claim as an empty run
    assert any("TRIMMED" in note for note in summary.notes)
    assert any("1 finding(s)" in note for note in summary.notes)


def test_stages_level_includes_stages_not_findings():
    """B-2 — the middle level buys metrics, not engine's adjudication."""
    full = _rich_diagnosis()

    staged = diagnose.trim(full, "stages")

    assert staged.stages == full.stages
    assert staged.symptoms == full.symptoms
    assert staged.findings == []
    assert staged.plan_transitions == []
    assert any("TRIMMED" in note for note in staged.notes)


def test_full_level_is_unchanged_from_today():
    """B-3 — full is the identity, so the widest payload cannot drift.

    Asserted against analyze()'s own output rather than a frozen literal: the
    guarantee is "trimming does nothing at full", which stays true as the
    diagnosis gains fields.
    """
    full = _rich_diagnosis()

    assert diagnose.trim(full, "full") is full
    assert diagnose.trim(full, "full").model_dump() == full.model_dump()


def test_verdict_is_identical_across_detail_levels():
    """B-4 — trimming never re-runs the analysis, so no two callers can be
    given different answers to the same question."""
    full = _rich_diagnosis()
    before = full.model_dump()

    verdicts = {
        (d.status, d.worst_stage_id, d.primary_symptom, d.summary)
        for d in (diagnose.trim(full, level) for level in diagnose.DETAIL_LEVELS)
    }

    assert len(verdicts) == 1, verdicts
    # and trimming is non-destructive: the source diagnosis is untouched
    assert full.model_dump() == before


def test_an_unknown_detail_level_is_refused():
    """Silently falling back to full would defeat the whole unit."""
    try:
        diagnose.trim(_rich_diagnosis(), "everything")
    except ValueError as exc:
        assert "detail must be one of" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("an unknown detail level was accepted")


def test_analyze_run_defaults_to_summary():
    """B-1 at the tool layer — the default is the trimmed answer."""
    import asyncio

    from apex_mcp.ch import ReadStore
    from apex_mcp.server import create_server
    from tests.conftest import FakeClient

    client = FakeClient(
        stages={"j": [stage_row(4, p50_ms=20, p99_ms=460, job_id="j")]},
        findings={"j": [finding_row(job_id="j")]},
        transitions={"j": [transition_row("skew_split")]},
    )
    server = create_server(ReadStore(client))

    result = asyncio.run(server.call_tool("analyze_run", {"job_id": "j"}))
    payload = result[1] if isinstance(result, tuple) else result

    assert payload["stages"] == []
    assert payload["findings"] == []
    assert payload["summary"]
    assert any("TRIMMED" in note for note in payload["notes"])


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
