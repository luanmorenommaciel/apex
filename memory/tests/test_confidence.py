"""The honesty gates. These tests are the product, not a formality."""

from __future__ import annotations

from apex_memory.config import SHAPE_NOISE_FLOOR_PCT
from apex_memory.confidence import estimate_noise_floor, predict_delta, score_confidence
from apex_memory.schema import Confidence


# ── Attributability (contract v0.4, cross-lane rule 3) ───────────────────────

def test_no_config_variation_means_no_creditable_delta():
    """The case that proved the rule: four runs of one shape with byte-identical
    shuffle and spill still ranged 2708-4347 ms. That 18.65% clears any
    plausible noise floor, so the floor alone does not catch it."""
    delta = predict_delta(
        baseline_task_time_ms=3329,
        best_task_time_ms=2708,
        n_config_variants=0,
        best_group_n=4,
    )
    assert delta.meaningful is False
    assert "unattributable" in delta.reason
    assert delta.delta_pct == 18.65


def test_single_config_is_still_unattributable():
    delta = predict_delta(
        baseline_task_time_ms=1000, best_task_time_ms=100, n_config_variants=1, best_group_n=5
    )
    assert delta.meaningful is False
    assert "unattributable" in delta.reason


# ── Group support ────────────────────────────────────────────────────────────

def test_single_run_group_is_a_sample_not_an_estimate():
    """min() over N noisy samples drifts lower as N grows, so a best-config
    chosen that way looks better the more history you have — backwards."""
    delta = predict_delta(
        baseline_task_time_ms=1000,
        best_task_time_ms=100,
        n_config_variants=3,
        best_group_n=1,
    )
    assert delta.meaningful is False
    assert "insufficient_group_support" in delta.reason


# ── Noise floor ──────────────────────────────────────────────────────────────

def test_improvement_below_the_floor_is_not_meaningful():
    delta = predict_delta(
        baseline_task_time_ms=1000,
        best_task_time_ms=950,
        n_config_variants=2,
        best_group_n=3,
        noise_floor_pct=15.9,
    )
    assert delta.meaningful is False
    assert "below_noise_floor" in delta.reason


def test_improvement_above_the_floor_is_meaningful():
    delta = predict_delta(
        baseline_task_time_ms=15344,
        best_task_time_ms=4730,
        baseline_input_bytes=96757174,
        best_input_bytes=96129686,
        n_config_variants=4,
        best_group_n=5,
        noise_floor_pct=23.7,
    )
    assert delta.meaningful is True
    assert delta.delta_pct > 23.7


def test_incomparable_input_blocks_the_claim():
    """An improvement measured on materially less input is not an improvement."""
    delta = predict_delta(
        baseline_task_time_ms=1000,
        best_task_time_ms=100,
        baseline_input_bytes=1_000_000,
        best_input_bytes=10_000,
        n_config_variants=3,
        best_group_n=5,
    )
    assert delta.meaningful is False
    assert "incomparable_input_size" in delta.reason


def test_noise_floor_is_measured_from_within_config_spread():
    # Two config groups, each internally noisy by ~20%.
    floor, basis = estimate_noise_floor([[100, 120, 80], [200, 240, 160]])
    assert floor > 15
    assert "measured from this shape" in basis


def test_noise_floor_falls_back_when_groups_are_too_small():
    floor, basis = estimate_noise_floor([[100], [200, 210]])
    assert floor == SHAPE_NOISE_FLOOR_PCT
    assert "global fallback" in basis


# ── Confidence tiers ─────────────────────────────────────────────────────────

def test_thin_history_is_low_confidence():
    tier, score, reasons = score_confidence(
        n_exact_jobs=3, n_structural_jobs=0, n_config_variants=0, mean_similarity=1.0
    )
    assert tier is Confidence.LOW
    assert any("thin" in r for r in reasons)
    assert any("zero configuration variation" in r for r in reasons)


def test_rich_history_with_real_variation_reaches_high():
    tier, score, reasons = score_confidence(
        n_exact_jobs=17, n_structural_jobs=5, n_config_variants=4, mean_similarity=1.0
    )
    assert tier is Confidence.HIGH
    assert score > 0.85
    assert any("HIGH:" in r for r in reasons), "a HIGH must state what supports it"


def test_many_jobs_but_one_config_cannot_reach_high():
    """Evidence count alone is not enough: without variation there is nothing
    to learn about which config is better."""
    tier, _, _ = score_confidence(
        n_exact_jobs=50, n_structural_jobs=0, n_config_variants=1, mean_similarity=1.0
    )
    assert tier is Confidence.LOW


def test_structural_jobs_count_less_than_exact_ones():
    exact, _, _ = score_confidence(
        n_exact_jobs=9, n_structural_jobs=0, n_config_variants=3, mean_similarity=1.0
    )
    structural, _, _ = score_confidence(
        n_exact_jobs=0, n_structural_jobs=9, n_config_variants=3, mean_similarity=1.0
    )
    assert exact is Confidence.HIGH
    assert structural is not Confidence.HIGH


def test_no_history_says_so():
    tier, score, reasons = score_confidence(
        n_exact_jobs=0, n_structural_jobs=0, n_config_variants=0, mean_similarity=0.0
    )
    assert tier is Confidence.LOW
    assert any("nothing to recall" in r for r in reasons)
