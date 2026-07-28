"""Confidence scoring and delta prediction.

This module is the point of the lane. A retrieval system that always answers is
worse than useless for capacity planning: it launders a guess into a number
someone will act on. ZEST itself has no fallback -- it averages its k neighbours
whether or not any of them resemble the query (arXiv 2503.03826 § 4.2 describes
no similarity threshold and no abstention). Apex must do better than that,
because Apex's answer is shown to an engineer as advice.

Two independent gates therefore stand between evidence and a claim:
  * `score_confidence` -- is there enough INDEPENDENT history to say anything?
  * `predict_delta`    -- is the improvement bigger than the noise?
"""

from __future__ import annotations

import statistics

from .config import (
    HIGH_MIN_CONFIG_VARIANTS,
    HIGH_MIN_EXACT_JOBS,
    MEDIUM_MIN_CONFIG_VARIANTS,
    MEDIUM_MIN_EXACT_JOBS,
    MIN_RUNS_FOR_NOISE_ESTIMATE,
    MIN_RUNS_PER_CONFIG_GROUP,
    SHAPE_NOISE_FLOOR_PCT,
)
from .schema import Confidence, PredictedDelta

# Bucket boundaries copied from engine/config.py so a memory confidence and a
# finding confidence mean the same thing to a reader. Divergence here would be a
# subtle cross-lane lie.
CONFIDENCE_LOW_MAX = 0.60
CONFIDENCE_MEDIUM_MAX = 0.85

# Comparing task_time_ms across runs is only fair when they processed comparable
# input. Beyond this relative gap the "improvement" may be nothing but a smaller
# dataset, so the delta is reported as not meaningful.
MAX_INPUT_SIZE_RATIO = 1.20


def _tier_from_score(score: float) -> Confidence:
    if score < CONFIDENCE_LOW_MAX:
        return Confidence.LOW
    if score < CONFIDENCE_MEDIUM_MAX:
        return Confidence.MEDIUM
    return Confidence.HIGH


def _tier_from_rules(n_exact_jobs: int, n_config_variants: int) -> Confidence:
    if n_exact_jobs >= HIGH_MIN_EXACT_JOBS and n_config_variants >= HIGH_MIN_CONFIG_VARIANTS:
        return Confidence.HIGH
    if n_exact_jobs >= MEDIUM_MIN_EXACT_JOBS and n_config_variants >= MEDIUM_MIN_CONFIG_VARIANTS:
        return Confidence.MEDIUM
    return Confidence.LOW


def score_confidence(
    *,
    n_exact_jobs: int,
    n_structural_jobs: int,
    n_config_variants: int,
    mean_similarity: float,
) -> tuple[Confidence, float, list[str]]:
    """Return (tier, score, human-readable reasons).

    `n_exact_jobs` and `n_structural_jobs` count DISTINCT JOBS, never rows. One
    job contributing seventeen stages is one observation; counting stages would
    turn a single run into an evidence pile and is the most tempting way to
    manufacture confidence out of nothing.

    A structural job is worth less than an exact one and is weighted at a third,
    because a structural match only means the encoder could not tell two plans
    apart after redaction (encoder.py § KNOWN LIMIT).
    """
    reasons: list[str] = []

    effective_jobs = n_exact_jobs + n_structural_jobs / 3.0
    evidence = min(1.0, effective_jobs / HIGH_MIN_EXACT_JOBS)
    config = min(1.0, n_config_variants / HIGH_MIN_CONFIG_VARIANTS)
    similarity = max(0.0, min(1.0, mean_similarity))

    score = 0.5 * evidence + 0.3 * config + 0.2 * similarity

    # The stricter of the two verdicts wins. The rule tier can veto a score
    # inflated by many near-identical runs; the score tier can veto a rule pass
    # backed by poor-quality matches. Requiring both to agree is what keeps a
    # thin history from ever presenting as HIGH.
    tier = min(
        _tier_from_rules(n_exact_jobs, n_config_variants),
        _tier_from_score(score),
        key=lambda c: ["LOW", "MEDIUM", "HIGH"].index(c.value),
    )

    if n_exact_jobs == 0 and n_structural_jobs == 0:
        reasons.append("no historical runs of this plan shape — nothing to recall")
    else:
        reasons.append(
            f"{n_exact_jobs} exact-fingerprint job(s) and {n_structural_jobs} "
            f"structurally-similar job(s) in history"
        )
    if n_exact_jobs < MEDIUM_MIN_EXACT_JOBS:
        reasons.append(
            f"n={n_exact_jobs} exact jobs is below the {MEDIUM_MIN_EXACT_JOBS} "
            f"needed for MEDIUM — history is thin"
        )
    if n_config_variants == 0:
        reasons.append(
            "zero configuration variation observed: no run in history recorded "
            "the config it used, so no configuration can be recommended"
        )
    elif n_config_variants < MEDIUM_MIN_CONFIG_VARIANTS:
        reasons.append(
            f"only {n_config_variants} distinct config(s) observed — with no "
            f"variation there is nothing to learn about which config is better"
        )
    if mean_similarity < 0.9 and n_structural_jobs:
        reasons.append(f"mean neighbour similarity {mean_similarity:.3f} is moderate")

    if tier is not Confidence.LOW:
        # Say what is actually holding the tier up, so a HIGH is auditable
        # rather than merely asserted.
        reasons.append(
            f"{tier.value}: {n_exact_jobs} independent job(s) ran this exact plan "
            f"under {n_config_variants} distinct configuration(s) — enough "
            f"variation for history to be compared rather than merely counted"
        )

    return tier, round(score, 4), reasons


def estimate_noise_floor(groups: list[list[float]]) -> tuple[float, str]:
    """Measure this shape's own run-to-run variance from its history.

    Each element of `groups` is the task times of runs sharing one
    configuration, so any spread inside a group is by construction NOT caused by
    configuration. The median of those within-group coefficients of variation is
    the empirical noise floor for this shape.

    Measuring per shape rather than applying one global constant matters because
    the corpus-wide distribution is severely right-skewed -- median 15.9%, p90
    76.4% -- so a single number describes almost no individual shape well. Falls
    back to the measured global median when no group is large enough to estimate.
    """
    cvs: list[float] = []
    for times in groups:
        usable = [t for t in times if t > 0]
        if len(usable) < MIN_RUNS_FOR_NOISE_ESTIMATE:
            continue
        mean = statistics.fmean(usable)
        if mean > 0:
            cvs.append(100.0 * statistics.stdev(usable) / mean)

    if not cvs:
        return SHAPE_NOISE_FLOOR_PCT, (
            f"global fallback: no configuration group has "
            f"{MIN_RUNS_FOR_NOISE_ESTIMATE}+ runs, so the corpus-wide measured "
            f"median of {SHAPE_NOISE_FLOOR_PCT}% (1σ) is used"
        )
    floor = statistics.median(cvs)
    return floor, (
        f"measured from this shape's own history: median within-config "
        f"CV of {floor:.1f}% (1σ) across {len(cvs)} configuration group(s)"
    )


def predict_delta(
    *,
    baseline_task_time_ms: float,
    best_task_time_ms: float,
    baseline_input_bytes: int = 0,
    best_input_bytes: int = 0,
    n_config_variants: int = 0,
    best_group_n: int = 1,
    noise_floor_pct: float = SHAPE_NOISE_FLOOR_PCT,
    noise_floor_basis: str = "",
    metric: str = "task_time_ms",
) -> PredictedDelta:
    """Predict the improvement available, refusing to quote noise as signal.

    Four gates, in order of how badly they would mislead:

    1. ATTRIBUTABILITY (contract v0.4, cross-lane rule 3). If fewer than two
       distinct configurations appear in history, nothing explains a performance
       gap, so the gap is variance by definition. This gate is first because it
       is the one raw numbers fail hardest: four runs of one shape with
       byte-identical shuffle (10,852,769 B) and spill (390,465 B) still ranged
       2708-4347 ms -- an 18.65% gap with no config difference to credit it to,
       which clears any plausible noise floor. The floor alone does NOT catch it.

    2. GROUP SUPPORT. `best_task_time_ms` must be a config group's MEDIAN over at
       least MIN_RUNS_PER_CONFIG_GROUP runs, never the single fastest run. The
       minimum of N noisy samples is a biased estimator: it drifts lower as N
       grows, so a "best known config" chosen that way looks better the more
       history you accumulate, which is precisely backwards. Medians of groups
       are compared instead, and a one-run group is a sample, not an estimate.

    3. COMPARABILITY. An improvement measured on materially less input is not an
       improvement.

    4. THE NOISE FLOOR, measured rather than assumed. `noise_floor_pct` should
       come from estimate_noise_floor() on this shape's own same-config runs.
       The verify lane's 5.8% is JOB-level; per-shape task_time_ms is far
       noisier (corpus median 15.9% 1σ, p90 76.4%), so 5.8% is a lower bound
       that would wave through pure variance if applied here.
    """
    if n_config_variants < 2:
        return PredictedDelta(
            metric=metric,
            baseline_value=baseline_task_time_ms,
            best_value=best_task_time_ms,
            delta_pct=round(
                (baseline_task_time_ms - best_task_time_ms)
                / baseline_task_time_ms
                * 100.0,
                2,
            )
            if baseline_task_time_ms > 0
            else 0.0,
            meaningful=False,
            noise_floor_pct=noise_floor_pct,
            reason=(
                "unattributable: history contains "
                f"{n_config_variants} distinct configuration(s), so no observed "
                "difference can be credited to tuning. Any spread between these "
                "runs is run-to-run variance, not an available gain."
            ),
        )

    if baseline_task_time_ms <= 0:
        return PredictedDelta(
            metric=metric,
            baseline_value=baseline_task_time_ms,
            best_value=best_task_time_ms,
            delta_pct=0.0,
            meaningful=False,
            noise_floor_pct=noise_floor_pct,
            reason="no_baseline: the query run has no measured task time",
        )

    if best_group_n < MIN_RUNS_PER_CONFIG_GROUP:
        return PredictedDelta(
            metric=metric,
            baseline_value=baseline_task_time_ms,
            best_value=best_task_time_ms,
            delta_pct=round(
                (baseline_task_time_ms - best_task_time_ms)
                / baseline_task_time_ms
                * 100.0,
                2,
            ),
            meaningful=False,
            noise_floor_pct=noise_floor_pct,
            reason=(
                f"insufficient_group_support: the best configuration was observed "
                f"on only {best_group_n} run(s), below the "
                f"{MIN_RUNS_PER_CONFIG_GROUP} needed to treat its median as that "
                f"configuration's performance rather than a single sample"
            ),
        )

    delta_pct = (baseline_task_time_ms - best_task_time_ms) / baseline_task_time_ms * 100.0

    # An "improvement" achieved on materially less input is not an improvement.
    if baseline_input_bytes > 0 and best_input_bytes > 0:
        ratio = max(baseline_input_bytes, best_input_bytes) / min(
            baseline_input_bytes, best_input_bytes
        )
        if ratio > MAX_INPUT_SIZE_RATIO:
            return PredictedDelta(
                metric=metric,
                baseline_value=baseline_task_time_ms,
                best_value=best_task_time_ms,
                delta_pct=round(delta_pct, 2),
                meaningful=False,
                noise_floor_pct=noise_floor_pct,
                reason=(
                    f"incomparable_input_size: best run processed {ratio:.2f}x "
                    f"different input, so the gap is not attributable to tuning"
                ),
            )

    if delta_pct <= 0:
        return PredictedDelta(
            metric=metric,
            baseline_value=baseline_task_time_ms,
            best_value=best_task_time_ms,
            delta_pct=round(delta_pct, 2),
            meaningful=False,
            noise_floor_pct=noise_floor_pct,
            reason="no_improvement_available: this run is already the best on record",
        )

    if delta_pct < noise_floor_pct:
        return PredictedDelta(
            metric=metric,
            baseline_value=baseline_task_time_ms,
            best_value=best_task_time_ms,
            delta_pct=round(delta_pct, 2),
            meaningful=False,
            noise_floor_pct=noise_floor_pct,
            reason=(
                f"below_noise_floor: {delta_pct:.1f}% is within this shape's "
                f"{noise_floor_pct:.1f}% (1σ) run-to-run variance, so it is "
                f"indistinguishable from re-running the same job unchanged "
                f"[{noise_floor_basis}]"
            ),
        )

    return PredictedDelta(
        metric=metric,
        baseline_value=baseline_task_time_ms,
        best_value=best_task_time_ms,
        delta_pct=round(delta_pct, 2),
        meaningful=True,
        noise_floor_pct=noise_floor_pct,
        reason=(
            f"{delta_pct:.1f}% faster than this run: the best configuration "
            f"group's median over {best_group_n} run(s) beats this run by more "
            f"than the {noise_floor_pct:.1f}% (1σ) noise floor "
            f"[{noise_floor_basis}]"
        ),
    )
