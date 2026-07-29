"""The two-arm replay: attributability, measured floor, fidelity, control."""

from __future__ import annotations

import pytest

from apex_verify.models import (
    Confidence,
    Measurement,
    Predictor,
    ReplayVerdict,
    SafetyReport,
    SafetyVerdict,
    StageObservation,
)
from apex_verify.predict import predict, score_prediction
from apex_verify.replay import (
    Arm,
    BenchShape,
    MechanismEvidence,
    analyse_replay,
    config_identity,
    evaluate_mechanism,
    evaluate_positive_control,
    score_measurement,
    shape_fidelity,
    verdict_from_replay,
)
from fixtures import (
    FINDING_SKEW_STAGE4,
    JOB_RUNTIME_MS,
    OBSERVED_CONFIG,
    PLAUSIBLE_REDUCE_STAGE,
    PROPOSED_CONFIG_SKEW,
    SLOTS,
    STAGE4_OBSERVED,
)

# dev's calibrated skew_join bench (calibration-20260728T193824Z, slots=8):
# n=100, p99/p50 = 17.7–20.6 vs threshold 14.14 — tail-bound every run.
SKEW_BENCH = BenchShape(
    name="dev:skew_join",
    task_count=100,
    p99_p50=18.0,
    bytes_per_task=261_463,
    slots=8,
)

SAFETY_OK = SafetyReport(safe=True, verdict=SafetyVerdict.ALLOW, detail="test")


def _arm(name, config, samples):
    return Arm(name=name, config=config, samples_ms=list(samples))


BASELINE_CONF = {"spark.sql.adaptive.enabled": "false", "spark.sql.shuffle.partitions": "100"}
TREATMENT_CONF = {"spark.sql.adaptive.enabled": "true", "spark.sql.adaptive.skewJoin.enabled": "true"}


# ── rule 3: attributability ──────────────────────────────────────────────────
def test_config_identity_canonicalises_spellings():
    assert config_identity({"k": "16m"}) == config_identity({"k": "16777216"})
    assert config_identity({"k": "TRUE"}) == config_identity({"k": "true"})
    assert config_identity({"k": "16m"}) != config_identity({"k": "32m"})


def test_distinct_arms_are_attributable_and_a_real_delta_resolves():
    m = analyse_replay(
        bench="dev:skew_join",
        baseline=_arm("base", BASELINE_CONF, [1000, 1100, 1050]),
        treatment=_arm("treat", TREATMENT_CONF, [700, 720, 710]),
        shape_fidelity=1.0,
    )
    assert m.attributable
    assert m.floor_measured
    assert m.noise_floor_pct == pytest.approx(4.76, abs=0.01)   # CV of the baseline arm
    assert m.delta_pct == pytest.approx(-32.38, abs=0.01)
    assert m.significant
    assert m.resolved_delta_pct == m.delta_pct


def test_identical_arms_are_unattributable_never_a_zero_percent_win():
    """The fix-already-on case: both arms canonicalise to the same conf, so even
    a large observed spread is run-to-run variance with nothing to credit it to.
    (The 18.65% spread on byte-identical work that motivated contract rule 3.)"""
    m = analyse_replay(
        bench="dev:skew_join",
        baseline=_arm("base", TREATMENT_CONF, [1000, 1100, 1050]),
        treatment=_arm("treat", {"spark.sql.adaptive.enabled": "TRUE",  # same conf, new spelling
                                 "spark.sql.adaptive.skewJoin.enabled": "true"},
                       [830, 860, 845]),   # -18.7% — would clear any job-level floor
        shape_fidelity=1.0,
    )
    assert not m.attributable
    assert "SAME configuration" in m.attribution_detail
    assert not m.significant
    assert m.resolved_delta_pct is None      # NOT "-18.7% faster", NOT "0% improvement"


def test_unattributable_headline_says_so():
    m = analyse_replay(
        bench="dev:skew_join",
        baseline=_arm("base", TREATMENT_CONF, [1000, 1100, 1050]),
        treatment=_arm("treat", TREATMENT_CONF, [840, 870, 855]),
        shape_fidelity=1.0,
    )
    verdict = verdict_from_replay(
        FINDING_SKEW_STAGE4, PROPOSED_CONFIG_SKEW,
        _prediction(), m, SAFETY_OK,
    )
    assert "UNATTRIBUTABLE" in verdict.headline()
    assert "0%" not in verdict.headline().split("—")[0]


# ── rule 2: the floor is measured, never inherited ───────────────────────────
def test_fewer_than_three_reps_leaves_the_floor_unmeasured():
    m = analyse_replay(
        bench="dev:skew_join",
        baseline=_arm("base", BASELINE_CONF, [1000, 1100]),
        treatment=_arm("treat", TREATMENT_CONF, [600, 620]),
        shape_fidelity=1.0,
    )
    assert not m.floor_measured
    assert not m.significant
    assert m.resolved_delta_pct is None    # a huge delta with no floor is still unquotable


def test_unmeasured_floor_serialises_as_null_not_zero():
    m = analyse_replay(
        bench="dev:skew_join",
        baseline=_arm("base", BASELINE_CONF, [1000, 1100]),
        treatment=_arm("treat", TREATMENT_CONF, [600, 620]),
        shape_fidelity=1.0,
    )
    verdict = verdict_from_replay(FINDING_SKEW_STAGE4, PROPOSED_CONFIG_SKEW,
                                  _prediction(), m, SAFETY_OK)
    row = verdict.to_row()
    assert row["noise_floor_pct"] is None    # an unmeasured floor is not a 0% floor
    assert row["measured_delta_pct"] is not None


def test_a_delta_inside_the_measured_floor_does_not_resolve():
    m = analyse_replay(
        bench="dev:skew_join",
        baseline=_arm("base", BASELINE_CONF, [1000, 1050, 1100]),   # floor ≈ 4.76%
        treatment=_arm("treat", TREATMENT_CONF, [1020, 1060, 1110]),  # delta ≈ +0.95%
        shape_fidelity=1.0,
    )
    assert m.floor_measured and m.attributable
    assert not m.significant
    assert m.resolved_delta_pct is None


def _prediction():
    return predict(
        FINDING_SKEW_STAGE4, PLAUSIBLE_REDUCE_STAGE,
        {"spark.sql.adaptive.skewJoin.skewedPartitionFactor": "2"},
        slots=50, job_runtime_ms=60_000.0, observed_config=OBSERVED_CONFIG,
    )


# ── shape fidelity ───────────────────────────────────────────────────────────
def test_fidelity_is_one_when_the_bench_is_the_shape():
    observed = StageObservation(
        stage_id=1, task_count=100, task_duration_p50_ms=60, task_duration_p99_ms=1080,
        shuffle_read_bytes=261_463 * 100, plan_json="+- Join Inner",
    )
    assert shape_fidelity(observed, SKEW_BENCH, observed_slots=8) == pytest.approx(1.0)


def test_regime_mismatch_caps_fidelity_at_a_half():
    # Same shape as the bench, but observed on 2 slots: threshold (100-1)/(2-1)=99
    # makes it WORK-bound while the bench is tail-bound — different physics.
    observed = StageObservation(
        stage_id=1, task_count=100, task_duration_p50_ms=60, task_duration_p99_ms=1080,
        shuffle_read_bytes=261_463 * 100, plan_json="+- Join Inner",
    )
    assert shape_fidelity(observed, SKEW_BENCH, observed_slots=2) == pytest.approx(0.5)


def test_the_real_stage4_finding_scores_low_fidelity_against_the_skew_bench():
    # 50 vs 100 tasks, 278 bytes/task vs 261 KB/task, work-bound vs tail-bound.
    f = shape_fidelity(STAGE4_OBSERVED, SKEW_BENCH, observed_slots=SLOTS)
    assert f < 0.5


def test_unknown_observed_slots_skips_the_regime_cap():
    observed = StageObservation(
        stage_id=1, task_count=100, task_duration_p50_ms=60, task_duration_p99_ms=1080,
        shuffle_read_bytes=261_463 * 100, plan_json="+- Join Inner",
    )
    # slots unknown (executor keys not explicitly set): the regime test is skipped,
    # not failed — the cap is a deduction, and deductions need facts.
    assert shape_fidelity(observed, SKEW_BENCH, observed_slots=None) == pytest.approx(1.0)


# ── rule 4: mechanism vs runtime ─────────────────────────────────────────────
MECH_COLLAPSE = MechanismEvidence(
    transition_fired=True,
    transition_detail="skew_split 3/3",
    baseline_ratios=[24.0, 18.4, 21.4],     # tonight's real baseline ratios
    treatment_ratios=[1.4, 2.6, 2.3],       # and their post-split collapse
)


def test_mechanism_confirmed_by_transition_alone():
    ok, detail = evaluate_mechanism(MechanismEvidence(transition_fired=True))
    assert ok is True
    assert "ground truth" in detail


def test_mechanism_confirmed_by_ratio_collapse_beyond_its_own_floor():
    ok, detail = evaluate_mechanism(
        MechanismEvidence(baseline_ratios=[24.0, 18.4, 21.4], treatment_ratios=[1.4, 2.6, 2.3])
    )
    assert ok is True
    assert "collapsed" in detail


def test_mechanism_not_confirmed_when_nothing_fires():
    ok, detail = evaluate_mechanism(
        MechanismEvidence(transition_fired=False,
                          baseline_ratios=[24.0, 18.4, 21.4], treatment_ratios=[22.0, 19.5, 23.1])
    )
    assert ok is False
    assert "NOT confirmed" in detail


def test_mechanism_is_none_when_no_evidence_exists():
    ok, detail = evaluate_mechanism(None)
    assert ok is None
    ok, _ = evaluate_mechanism(MechanismEvidence())
    assert ok is None


def test_runtime_verdict_is_a_separate_first_class_verdict():
    certified = analyse_replay(
        bench="b",
        baseline=_arm("base", BASELINE_CONF, [1000, 1100, 1050]),
        treatment=_arm("treat", TREATMENT_CONF, [700, 720, 710]),
        shape_fidelity=1.0, mechanism=MECH_COLLAPSE,
    )
    assert certified.runtime_verdict is ReplayVerdict.RUNTIME_CERTIFIED
    assert certified.verdicts == [ReplayVerdict.MECHANISM_CONFIRMED, ReplayVerdict.RUNTIME_CERTIFIED]

    unresolved = analyse_replay(
        bench="b",
        baseline=_arm("base", BASELINE_CONF, [1000, 1050, 1100]),
        treatment=_arm("treat", TREATMENT_CONF, [1020, 1060, 1110]),
        shape_fidelity=1.0, mechanism=MECH_COLLAPSE,
    )
    assert unresolved.runtime_verdict is ReplayVerdict.RUNTIME_UNRESOLVED
    assert unresolved.verdicts == [ReplayVerdict.MECHANISM_CONFIRMED, ReplayVerdict.RUNTIME_UNRESOLVED]

    # Rule 3 voids the comparison entirely: unattributable arms get no verdict.
    void = analyse_replay(
        bench="b",
        baseline=_arm("base", TREATMENT_CONF, [1000, 1100, 1050]),
        treatment=_arm("treat", TREATMENT_CONF, [700, 720, 710]),
        shape_fidelity=1.0, mechanism=MECH_COLLAPSE,
    )
    assert void.runtime_verdict is None
    assert ReplayVerdict.MECHANISM_CONFIRMED in void.verdicts  # mechanism fact still stands


def test_headline_emits_the_rule4_pair():
    m = analyse_replay(
        bench="dev:skew_join",
        baseline=_arm("base", BASELINE_CONF, [2424, 1948, 1747]),   # tonight's real samples
        treatment=_arm("treat", TREATMENT_CONF, [1756, 1507, 2017]),
        shape_fidelity=1.0, mechanism=MECH_COLLAPSE,
    )
    assert not m.significant            # -9.9% vs a ±17% floor: unresolved
    assert m.mechanism_confirmed
    verdict = verdict_from_replay(FINDING_SKEW_STAGE4, PROPOSED_CONFIG_SKEW,
                                  _prediction(), m, SAFETY_OK)
    assert "MECHANISM CONFIRMED, RUNTIME UNRESOLVED" in verdict.headline()
    assert "magnitude deferred" in verdict.headline().lower().replace(",", "")


# ── the positive control (rule 4: mechanism is the gate, runtime is reported) ─
def test_positive_control_passes_with_runtime_certified_when_the_delta_resolves():
    m = analyse_replay(
        bench="dev:skew_join",
        baseline=_arm("base", BASELINE_CONF, [1000, 1100, 1050]),
        treatment=_arm("treat", TREATMENT_CONF, [700, 720, 710]),
        shape_fidelity=1.0, mechanism=MECH_COLLAPSE,
    )
    result = evaluate_positive_control(m)
    assert result.passed
    assert "runtime_certified" in result.detail


def test_positive_control_passes_with_runtime_unresolved_when_only_mechanism_proves():
    """The bench certifies mechanism and defers magnitude — a PASS under rule 4,
    and the honest limit of laptop scale if even the W-conserving control
    cannot clear the floor."""
    m = analyse_replay(
        bench="dev:skew_join",
        baseline=_arm("base", BASELINE_CONF, [2424, 1948, 1747]),
        treatment=_arm("treat", TREATMENT_CONF, [1756, 1507, 2017]),
        shape_fidelity=1.0, mechanism=MECH_COLLAPSE,
    )
    result = evaluate_positive_control(m)
    assert result.passed
    assert "runtime_unresolved" in result.detail
    assert "not to tune away" in result.detail


def test_positive_control_fails_when_the_mechanism_cannot_be_confirmed():
    """A runtime delta without mechanism ground truth proves nothing — this is
    the mis-specified-control trap (a repartitioning masquerading as a tail fix)."""
    m = analyse_replay(
        bench="dev:skew_join",
        baseline=_arm("base", BASELINE_CONF, [1000, 1100, 1050]),
        treatment=_arm("treat", TREATMENT_CONF, [700, 720, 710]),
        shape_fidelity=1.0,   # big runtime delta, NO mechanism evidence
    )
    result = evaluate_positive_control(m)
    assert not result.passed
    assert "mechanism" in result.detail


def test_positive_control_fails_closed_on_unattributable_or_floorless_runs():
    identical = analyse_replay(
        bench="dev:skew_join",
        baseline=_arm("base", TREATMENT_CONF, [1000, 1100, 1050]),
        treatment=_arm("treat", TREATMENT_CONF, [700, 720, 710]),
        shape_fidelity=1.0, mechanism=MECH_COLLAPSE,
    )
    assert not evaluate_positive_control(identical).passed

    floorless = analyse_replay(
        bench="dev:skew_join",
        baseline=_arm("base", BASELINE_CONF, [1000, 1100]),
        treatment=_arm("treat", TREATMENT_CONF, [600, 620]),
        shape_fidelity=1.0, mechanism=MECH_COLLAPSE,
    )
    assert not evaluate_positive_control(floorless).passed


# ── scoring ──────────────────────────────────────────────────────────────────
def test_measurement_score_is_fidelity_scaled_once_legal():
    good = Measurement(delta_pct=-30, baseline_ms=1050, treatment_ms=710,
                       noise_floor_pct=4.8, reps=3, bench="b", shape_fidelity=1.0)
    half = good.model_copy(update={"shape_fidelity": 0.5})
    assert score_measurement(good) == pytest.approx(0.90)   # never the 0.95 of a deduction
    assert score_measurement(half) == pytest.approx(0.70)
    assert Confidence.from_score(score_measurement(good)) is Confidence.HIGH
    assert Confidence.from_score(score_measurement(half)) is Confidence.MEDIUM


def test_measurement_score_fails_closed():
    base = Measurement(delta_pct=-30, baseline_ms=1050, treatment_ms=710,
                       noise_floor_pct=4.8, reps=3, bench="b", shape_fidelity=1.0)
    assert score_measurement(base.model_copy(update={"attributable": False})) == 0.35
    assert score_measurement(base.model_copy(update={"floor_measured": False})) == 0.45


# ── slots unknown: capped, never guessed (contract rule 1) ───────────────────
def test_predict_withholds_the_bound_when_slots_are_unknown():
    p = predict(
        FINDING_SKEW_STAGE4, PLAUSIBLE_REDUCE_STAGE,
        {"spark.sql.adaptive.skewJoin.skewedPartitionFactor": "2"},
        slots=None, job_runtime_ms=60_000.0, observed_config=OBSERVED_CONFIG,
    )
    assert p.predictor is Predictor.NONE
    assert "rule 1" in p.evidence
    assert "never guessed" in p.evidence
    assert Confidence.from_score(score_prediction(p)) is Confidence.LOW
