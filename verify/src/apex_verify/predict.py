"""Stage 1 — PREDICT. Analytic estimation with zero execution.

The core model is a makespan bound, not a regression. For a stage of `n` tasks on
`slots` concurrent task slots, list-scheduling gives

    max(longest_task, W/slots)  <=  T  <=  W/slots + longest_task·(1 - 1/slots)

so `T ≈ max(p99, W/slots)` is the estimate we use. A skew fix REDISTRIBUTES work,
it does not remove it, so total work `W` is conserved (charitably — splitting a
skewed partition actually adds shuffle) and after a perfect fix every task is
`W/n`, giving `T_after = W/slots`. Therefore:

    Δ_stage = W/slots − max(p99, W/slots)

which is **exactly zero whenever W/slots ≥ p99**. That is the work-bound regime,
and it is the single most useful thing this module computes: it says "even a
perfect fix returns nothing" from two order statistics and a core count.

`W` is not measured. `executor_run_time_ms` exists in engine's in-memory
`StageEvent` but is NOT a column in `apex.spark_events` (verified against
`system.columns`), so W is BRACKETED between two task-distribution models and the
prediction is reported as an interval. When both ends of the bracket agree, the
conclusion is robust *despite* the estimate being loose — which is why a
work-bound verdict can be trusted more than its inputs suggest.

Grounding: gray-box per-stage-then-compose runtime prediction reaches 83–94%
accuracy (Al-Sayeh, Hagedorn & Sattler, *Distributed and Parallel Databases* 38(4)
819–839, 2020) — but that is a *trained* model over a job corpus. Apex has 7
job_ids. So this module deliberately does NOT learn: it computes a bound, which
needs no corpus and cannot silently drift.
"""

from __future__ import annotations

from typing import Iterable, Mapping

from .guardrails import mechanism_check, noise_floor, noop_gate, runtime_cv_pct
from .models import (
    PREDICTED_IMPROVEMENT_SCORE_CAP,
    FindingRef,
    Guardrail,
    Prediction,
    Predictor,
    StageObservation,
)

# Conf keys whose effect is to redistribute a long tail — the class the makespan
# model above actually describes.
_TAIL_FIX_KEYS = {
    "spark.sql.adaptive.enabled",
    "spark.sql.adaptive.skewJoin.enabled",
    "spark.sql.adaptive.skewJoin.skewedPartitionFactor",
    "spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes",
    "spark.sql.adaptive.forceOptimizeSkewedJoin",
}
_PARTITION_SIZING_KEYS = {
    "spark.sql.shuffle.partitions",
    "spark.sql.adaptive.advisoryPartitionSizeInBytes",
    "spark.sql.adaptive.coalescePartitions.enabled",
    "spark.sql.files.maxPartitionBytes",
}


class FixClass:
    TAIL = "tail_redistribution"
    PARTITION_SIZING = "partition_sizing"
    UNKNOWN = "unknown"


def classify_fix(proposed_config: Mapping[str, str]) -> str:
    keys = set(proposed_config)
    if keys & _TAIL_FIX_KEYS:
        return FixClass.TAIL
    if keys & _PARTITION_SIZING_KEYS:
        return FixClass.PARTITION_SIZING
    return FixClass.UNKNOWN


def work_bracket(stage: StageObservation) -> tuple[float, float]:
    """Bracket total task-time for a stage from p50, p99 and task_count.

    Two task-distribution models, deliberately chosen to straddle reality:
      * single outlier — one task at p99, the rest at p50 (tightest possible W)
      * heavy top decile — 10% of tasks at p99, 90% at p50 (a fat tail)
    Returned numerically ordered; for small `n` the "heavy" model can be the
    smaller of the two, so do not assume an ordering.
    """
    n = stage.task_count
    p50 = stage.task_duration_p50_ms
    p99 = stage.task_duration_p99_ms
    if n <= 0:
        return 0.0, 0.0
    w_outlier = (n - 1) * p50 + p99
    w_heavy = 0.9 * n * p50 + 0.1 * n * p99
    return min(w_outlier, w_heavy), max(w_outlier, w_heavy)


def tail_bound_ratio_threshold(task_count: int, slots: int) -> float | None:
    """The skew ratio a stage must EXCEED before its tail is on the critical path.

    Falls straight out of the makespan bound. Tail-bound means W/slots < p99;
    substituting the single-outlier work model W = (n-1)·p50 + p99:

        ((n-1)·p50 + p99) / slots < p99
        (n-1)·p50 < (slots-1)·p99
        p99/p50   > (n-1)/(slots-1)

    So the threshold depends only on task count and cluster width — not on data
    volume at all. Consequences worth internalising:

      * 50 tasks on   2 slots -> ratio must exceed 49.0  (dev lab: 21.62x is not close)
      * 50 tasks on  50 slots -> ratio must exceed  1.0  (real cluster: almost any skew bites)
      *  4 tasks on   2 slots -> ratio must exceed  3.0

    This is why "fix the skew" is sound advice on a wide cluster and worthless on
    a narrow one, and why adding DATA to a narrow bench will never make a skew
    finding reproducible — the threshold does not move.

    Returns None for slots <= 1, where a single slot is always work-bound.
    """
    if slots <= 1 or task_count <= 0:
        return None
    return (task_count - 1) / (slots - 1)


def _stage_delta_ms(stage: StageObservation, work_ms: float, slots: int) -> tuple[float, str]:
    """Δ (ms, negative = faster) for a perfect tail fix, plus the regime label."""
    slots = max(1, slots)
    n_after = max(stage.task_count, slots)
    throughput_ms = work_ms / slots
    t_before = max(stage.task_duration_p99_ms, throughput_ms)
    t_after = max(work_ms / n_after if n_after else 0.0, throughput_ms)
    regime = "work_bound" if throughput_ms >= stage.task_duration_p99_ms else "tail_bound"
    return t_after - t_before, regime


def bound_analysis(
    stage: StageObservation, slots: int, job_runtime_ms: float
) -> tuple[Guardrail, float, float, float]:
    """(b) Work-bound vs tail-bound. Returns (guardrail, delta, low, high) in %."""
    w_lo, w_hi = work_bracket(stage)
    d_lo_ms, regime_lo = _stage_delta_ms(stage, w_lo, slots)   # least work -> most saving
    d_hi_ms, regime_hi = _stage_delta_ms(stage, w_hi, slots)   # most work  -> least saving

    def pct(ms: float) -> float:
        return 100.0 * ms / job_runtime_ms if job_runtime_ms > 0 else 0.0

    # Numerically ordered interval; negative = faster, so `low` is the most saving.
    low, high = sorted((pct(d_lo_ms), pct(d_hi_ms)))
    mid = (low + high) / 2.0
    both_zero = d_lo_ms == 0.0 and d_hi_ms == 0.0
    throughput_lo = w_lo / max(1, slots)

    detail = (
        f"Stage {stage.stage_id}: {stage.task_count} tasks, p50={stage.task_duration_p50_ms:.0f}ms, "
        f"p99={stage.task_duration_p99_ms:.0f}ms on {slots} task slot(s). "
        f"Estimated total task-time W is bracketed {w_lo:,.0f}–{w_hi:,.0f}ms "
        f"(W is not measured: executor_run_time_ms is not a spark_events column). "
        f"Throughput floor W/slots = {throughput_lo:,.0f}ms vs tail p99 = "
        f"{stage.task_duration_p99_ms:.0f}ms -> {regime_lo.upper()}. "
    )
    if both_zero:
        detail += (
            "The stage is limited by total work, not by its slowest task, at BOTH ends "
            "of the bracket: the tail finishes inside the time the other tasks need "
            "anyway. A perfect redistribution of the tail therefore saves 0ms — there "
            "is no tail time on the critical path to recover."
        )
    else:
        detail += (
            f"Recoverable tail time is {-d_lo_ms:,.0f}ms at best and {-d_hi_ms:,.0f}ms at "
            f"worst, i.e. {low:+.1f}%..{high:+.1f}% of the {job_runtime_ms:,.0f}ms job."
        )

    return (
        Guardrail(
            name=Predictor.AMDAHL_TAIL_SHARE,
            fired=both_zero,
            verdict=regime_lo if not both_zero else "work_bound_saves_nothing",
            detail=detail,
            caps_delta_at_zero=both_zero,
            score=0.85 if both_zero else None,
        ),
        mid,
        low,
        high,
    )


def predict(
    finding: FindingRef,
    stage: StageObservation,
    proposed_config: Mapping[str, str],
    *,
    slots: int | None,
    job_runtime_ms: float,
    observed_config: Mapping[str, str] | None = None,
    siblings: Iterable[StageObservation] = (),
    sibling_job_runtimes_ms: Iterable[float] = (),
) -> Prediction:
    """Predict the job-runtime delta of `proposed_config`, executing nothing.

    Guardrails run cheapest-and-most-decisive first. Any one of them can pin the
    prediction at zero; when that happens we stop reasoning about magnitude and
    report *why the fix is pointless*, which is more actionable than a number.

    `slots=None` means the cluster width could not be determined (job_conf
    captures `spark.executor.*` only when explicitly set). The makespan bound
    is then uncomputable, so it is not computed — confidence is capped, never
    guessed (contract rule 1).
    """
    rails: list[Guardrail] = []

    g_noop = noop_gate(proposed_config, observed_config)
    rails.append(g_noop)
    g_mech = mechanism_check(stage, finding.type)
    rails.append(g_mech)
    g_noise = noise_floor(stage, siblings, sibling_job_runtimes_ms)
    rails.append(g_noise)

    fix_class = classify_fix(proposed_config)
    cv = runtime_cv_pct(sibling_job_runtimes_ms)

    # ── (a) already active: nothing to predict, and we are sure of it ────────
    if g_noop.fired:
        return Prediction(
            predictor=Predictor.NOOP_GATE,
            delta_pct=0.0, low_pct=0.0, high_pct=0.0,
            evidence=g_noop.detail,
            caveats=(
                "Read from the observed run's effective SparkConf. If that conf was "
                "captured from a different attempt or a restarted driver, re-check it."
            ),
            guardrails=rails,
        )

    # ── (d) the pathology cannot exist here: the fix has nothing to act on ──
    if g_mech.caps_delta_at_zero:
        return Prediction(
            predictor=Predictor.MECHANISM_CHECK,
            delta_pct=0.0, low_pct=0.0, high_pct=0.0,
            evidence=g_mech.detail,
            caveats=(
                "This rejects the finding's stated mechanism, not the possibility that "
                "the job is slow for some other reason. A different stage may still hold "
                "a real pathology."
            ),
            guardrails=rails,
        )

    # ── no analytic model for this fix class: say so, do not improvise ───────
    if fix_class is FixClass.UNKNOWN:
        return Prediction(
            predictor=Predictor.NONE,
            delta_pct=0.0,
            low_pct=-100.0, high_pct=100.0,
            evidence=(
                f"No analytic model covers this fix class (keys: "
                f"{', '.join(sorted(proposed_config)) or 'none'}). The makespan bound "
                f"only describes tail-redistribution fixes."
            ),
            caveats="Unverified, predicted only, LOW confidence. Replay is required.",
            guardrails=rails,
        )

    if fix_class is FixClass.PARTITION_SIZING:
        return Prediction(
            predictor=Predictor.PARTITION_SIZING,
            delta_pct=0.0,
            low_pct=-100.0, high_pct=100.0,
            evidence=(
                "Partition-sizing changes alter the number and size of tasks, so total "
                "work W is not conserved and the makespan bound above does not apply. "
                "No analytic estimate is offered."
            ),
            caveats="Unverified, predicted only, LOW confidence. Replay is required.",
            guardrails=rails,
        )

    # ── (b) the makespan bound ──────────────────────────────────────────────
    if slots is None:
        return Prediction(
            predictor=Predictor.NONE,
            delta_pct=0.0,
            low_pct=-100.0, high_pct=100.0,
            evidence=(
                "Cluster width is unknown: apex.job_conf captures spark.executor.instances/"
                "cores only when they were explicitly set, and this run did not set them. "
                "The tail-bound question — p99/p50 > (n_tasks−1)/(slots−1) — is unanswerable "
                "without a slot count, so no makespan bound is computed. Contract rule 1: "
                "confidence is capped, never guessed."
            ),
            caveats=(
                "Slots unknown, prediction withheld. Re-observe with executor sizing set "
                "explicitly, or replay on the calibrated bench (8 slots) and measure instead."
            ),
            guardrails=rails,
        )

    g_bound, mid, low, high = bound_analysis(stage, slots, job_runtime_ms)
    rails.append(g_bound)

    caveats: list[str] = []
    if g_bound.caps_delta_at_zero:
        evidence = g_bound.detail
    else:
        evidence = g_bound.detail
        caveats.append(
            "Unverified, predicted only — this is a makespan CEILING (the best a "
            "perfect fix could do), not an expected value. AQE's actual split is "
            "imperfect and adds shuffle, so the real gain is smaller."
        )
        if cv is not None and abs(mid) < cv:
            caveats.append(
                f"The predicted {mid:+.1f}% is below the {cv:.1f}% run-to-run noise floor "
                f"of this shape, so a replay cannot confirm it at any repetition count."
            )
    if g_noise.fired:
        caveats.append(g_noise.detail)

    return Prediction(
        predictor=Predictor.AMDAHL_TAIL_SHARE,
        delta_pct=mid, low_pct=low, high_pct=high,
        evidence=evidence,
        caveats=" ".join(caveats),
        guardrails=rails,
    )


def score_prediction(prediction: Prediction) -> float:
    """Confidence 0–1 for a prediction, honouring the refuse/promise asymmetry.

    A guardrail that pins the delta at zero contributes its own high score: those
    are deductions from facts in hand. A predicted IMPROVEMENT is an
    extrapolation from two order statistics and is capped at MEDIUM until
    something is actually executed.
    """
    pinning = [g for g in prediction.guardrails if g.caps_delta_at_zero and g.score is not None]
    if pinning:
        return max(g.score for g in pinning)  # type: ignore[arg-type]
    if prediction.predictor in (Predictor.NONE, Predictor.PARTITION_SIZING):
        return 0.35  # LOW — honest "no model"
    width = abs(prediction.high_pct - prediction.low_pct)
    # A tight bracket earns more, but never more than the cap.
    base = 0.70 if width <= 5.0 else 0.55 if width <= 20.0 else 0.40
    return min(base, PREDICTED_IMPROVEMENT_SCORE_CAP)
