"""Skew watcher — DETERMINISTIC, and rebuilt against physics instead of a guess.

Three independently-reported defects in the old version, all fixed here:

**1. The finding TYPE was fabricated.** It labelled every wide p99/p50 ratio
`SKEW_ON_JOIN`, including stage 4 of `app-20260724160310-0000` — a Delta-metadata
`!Aggregate` stage with no Join node in its plan and `shuffle_read_bytes = 0`,
writing 4,750 shuffle bytes. `SKEW_ON_JOIN` now requires plan evidence of a join
(`plans.join_evidence`). Without it the tail is reported as `TASK_SKEW`, and its
fix never mentions `skewJoin` — that flag only ever applies to a join.

**2. The fixed 5x/10x threshold was wrong in both directions** (CONTRACT.md
rule 1). The threshold is `(n_tasks - 1) / (slots - 1)`; volume cancels out. On
50 tasks / 2 slots the bar is >49x, so the celebrated "critical 21.62x" was
WORK-bound and a perfect fix returns nothing; on 50 tasks / 50 slots the bar is
>1x, which the old rule never looked at. The closed form lives in `physics.py`
and `slots` is an observation — when it cannot be determined, confidence is
capped and the finding says so instead of substituting a number.

**3. The ratio was treated as a statistic at any volume** (dev: "the tiny
50-task Delta-metadata stages ... will still fool any watcher that doesn't key on
shuffle volume"). A ratio over stages moving kilobytes measures JVM warm-up and
scheduler jitter. Below 1 MiB/task there is no data-volume tail to find, so the
ratio is not computed into a claim at all.

Plus rule 2: the predicted win is checked against a **measured** floor for this
stage shape at this scale (never a constant), and a win under the floor is
suppressed rather than rendered. And rule 3: the fix text refuses to credit
tuning when history holds fewer than 2 distinct configs.
"""

from __future__ import annotations

from ..context import JobContext, context_for
from ..jobconf import SKEW_JOIN_ENABLED
from ..physics import (
    MIN_TASKS_FOR_RATIO,
    NOT_A_DISTRIBUTION,
    SERIAL,
    SLOTS_UNKNOWN,
    WORK_BOUND,
)
from ..plans import join_evidence
from ..schema import Finding, FindingType, Severity, StageAggregate
from .base import MIB, human_bytes, stage_finding

NAME = "skew_watcher"

# --- mechanism bound, not a noise floor (rule 2 forbids the latter) ---------
# A task touching under 1 MiB cannot have a DATA-VOLUME tail: at that scale the
# spread is JVM warm-up and scheduler jitter, whatever the ratio says. This is a
# measurability bound on the mechanism, and it is the same constant verify/ uses
# (`guardrails.SKEW_MIN_BYTES_PER_TASK`) so the two lanes cannot disagree about
# which stages are even eligible.
MIN_BYTES_PER_TASK = 1 * MIB

# --- confidence, by the strength of the WIDTH observation ------------------
# Nothing here is a threshold on the data; these express how much is actually
# known about the input the closed form needs.
CONF_CONF_STRONG = 0.88   # width read from the run's own job_conf, large win
CONF_CONF_WEAK = 0.72     # width read from job_conf, modest win
CONF_OPERATOR_STRONG = 0.80  # width supplied by an operator, not by the run
CONF_OPERATOR_WEAK = 0.65
CONF_SLOTS_UNKNOWN = 0.50  # capped below the gate: the closed form is not evaluable
# Tail-bound, join-evidenced, but the win is under the shape's MEASURED floor:
# real mechanism, unverifiable payoff. Reported, not asserted, and never severe.
CONF_WITHIN_NOISE = 0.45
# An unmeasured floor weakens the predicted NUMBER, not the tail-bound verdict —
# the verdict is a deduction from the closed form and stands on its own. So a
# first-ever run of a shape still reports its tail; it just cannot claim the win
# is resolvable, which costs a little confidence and never a whole tier.
NO_FLOOR_PENALTY = 0.03

# Once a stage IS tail-bound, severity follows the SIZE OF THE WIN, not the size
# of the ratio. Those are not independent — headroom ~= 1 - 1/margin, where margin
# is ratio/threshold — so gating on both would just be a stricter headroom bar in
# disguise (margin >= 2 means headroom >= ~50%, which would demote dev's
# genuinely-skewed stage at 39.6% to a warning). `margin` stays in the evidence.
STRONG_HEADROOM = 0.25

# With no measured floor to compare a predicted win against, the only claim that
# needs no reference measurement is that the tail DOMINATES the stage: removing it
# could more than halve the stage's wall time. Not a noise floor — a floor would
# be an estimate of variance, and this is a property of the single observation.
DOMINANT_GAIN = 0.5

# Pushdown. It can no longer carry the verdict — the closed form needs the
# cluster width, which is not in this table — so it pushes down only the
# mechanism prerequisites (enough tasks, enough volume, a spread at all) and
# leaves rule 1 to Python, where `slots` is known. `evaluate` re-checks all of
# it so the offline path reaches the same verdict without the pushdown.
SQL = """
SELECT
  job_id,
  any(app_id)                                      AS app_id,
  stage_id,
  max(stage_attempt)                               AS attempt,
  argMax(task_duration_p50_ms, ts)                 AS task_duration_p50_ms,
  argMax(task_duration_p99_ms, ts)                 AS task_duration_p99_ms,
  argMax(task_count, ts)                           AS task_count,
  argMax(shuffle_read_bytes, ts)                   AS shuffle_read_bytes,
  argMax(shuffle_write_bytes, ts)                  AS shuffle_write_bytes,
  argMax(input_bytes, ts)                          AS input_bytes,
  argMax(spill_disk_bytes, ts)                     AS spill_disk_bytes,
  argMax(gc_time_ms, ts)                           AS gc_time_ms,
  argMax(plan_fingerprint, ts)                     AS plan_fingerprint,
  argMax(plan_json, ts)                            AS plan_json,
  round(argMax(task_duration_p99_ms, ts) / nullIf(argMax(task_duration_p50_ms, ts), 0), 2) AS skew_ratio
FROM apex.spark_events
WHERE job_id = {job_id:String}
GROUP BY job_id, stage_id
HAVING task_count >= {min_tasks:Int32}
   AND skew_ratio > 1
   AND (shuffle_read_bytes + shuffle_write_bytes + input_bytes) / task_count
       >= {min_bytes_per_task:Int64}
ORDER BY skew_ratio DESC
"""

SQL_PARAMETERS = {"min_tasks": MIN_TASKS_FOR_RATIO, "min_bytes_per_task": MIN_BYTES_PER_TASK}


def evaluate(stage: StageAggregate, ctx: JobContext | None = None) -> Finding | None:
    ctx = context_for(ctx)
    tail = ctx.tail_bound(stage)

    # (a) a p99 over a handful of tasks is not a distribution.
    if tail.verdict == NOT_A_DISTRIBUTION:
        return None

    # (b) BUG 3 — volume first. Without data there is no data skew, and the
    # ratio is not promoted to a statistic.
    if stage.bytes_per_task < MIN_BYTES_PER_TASK:
        return None

    # (c) BUG 2 — the closed form. A work-bound stage returns nothing from a
    # perfect skew fix, so there is no finding to make.
    if tail.verdict in (WORK_BOUND, SERIAL):
        return None

    # (d) rule 2 — a predicted win below the MEASURED floor for this shape at
    # this scale cannot be resolved by replay, so it is not rendered as a claim.
    # `claimed_gain_frac` falls back to the width-FREE bound, so this check still
    # bites when the width is unknown — which is the case that would otherwise
    # emit a capped warning for every stage whose p99 merely exceeds its p50.
    floor = ctx.noise_floor(stage)
    gain_frac = tail.claimed_gain_frac
    gain_pct = gain_frac * 100 if gain_frac is not None else None

    # (e) Where the closed form does NOT discriminate, something else must. Two
    # such regimes, and both used to emit pure jitter:
    #   * slots >= n_tasks -> the bar is (n-1)/(slots-1) <= 1, so any ratio above
    #     1 "passes" (8 tasks on 8 slots gave a bar of 1.00 and reported a 1.01x
    #     ratio worth 0.8% of the stage);
    #   * width unknown -> there is no bar at all.
    # In those regimes the claim rests entirely on the SIZE of the win, so it needs
    # a reference: the shape's MEASURED floor when one exists, and otherwise only
    # the claim that the tail DOMINATES the stage. Where the bar does discriminate,
    # tail-boundness is a deduction from the closed form and stands without a
    # floor — rule 2 then governs only whether the predicted number is rendered.
    if gain_frac is None:
        return None
    if tail.threshold is None or tail.threshold <= 1.0:
        if floor.known:
            if floor.resolves(gain_pct) is not True:
                return None
        elif gain_frac <= DOMINANT_GAIN:
            return None

    # (f) BUG 1 — the type follows the plan, not the ratio.
    join = join_evidence(stage)
    within_noise = floor.resolves(gain_pct) is False
    if within_noise and not join.supports_join_skew:
        # Nothing actionable survives: no identified mechanism AND a win the
        # measured floor says replay could not confirm.
        return None
    # A join-evidenced tail below the floor is still reported, because noise
    # proves a delta UNRESOLVABLE, never zero (contract rule 2, and verify/'s own
    # noise guardrail sets caps_delta_at_zero=False for exactly this reason).
    # What rule 2 forbids is RENDERING the number, so `_evidence` withholds it.
    slots_unknown = tail.verdict == SLOTS_UNKNOWN
    strong = not within_noise and not slots_unknown and (tail.headroom_frac or 0) >= STRONG_HEADROOM

    if within_noise:
        severity, confidence_score = Severity.INFO, CONF_WITHIN_NOISE
    else:
        severity = Severity.CRITICAL if strong else Severity.WARNING
        confidence_score = _confidence(tail.width.source, strong, slots_unknown, floor.known)
    attribution = ctx.attribution(stage)

    return stage_finding(
        stage,
        finding_type=FindingType.SKEW_ON_JOIN if join.supports_join_skew else FindingType.TASK_SKEW,
        severity=severity,
        confidence_score=confidence_score,
        evidence=_evidence(stage, tail, join, gain_pct, within_noise),
        impact=_impact(tail, gain_pct, floor, within_noise),
        fix=_fix(ctx, join.supports_join_skew, attribution),
        detected_by=NAME,
        details={
            # what the claim rests on — the validator re-checks these
            "skew_ratio": tail.ratio,
            "task_count": stage.task_count,
            "task_duration_p50_ms": stage.task_duration_p50_ms,
            "task_duration_p99_ms": stage.task_duration_p99_ms,
            "bytes_touched": stage.bytes_touched,
            "bytes_per_task": stage.bytes_per_task,
            "shuffle_read_bytes": stage.shuffle_read_bytes,
            # rule 1
            "tail_bound_verdict": tail.verdict,
            "tail_bound_threshold": tail.threshold,
            "tail_bound_margin": tail.margin,
            "slots": tail.width.slots,
            "slots_source": tail.width.source,
            "slots_detail": tail.width.detail,
            "min_slots_required": tail.min_slots_required,
            "headroom_frac_upper_bound": tail.headroom_frac,
            "headroom_frac_width_free": tail.headroom_upper_frac,
            # rule 2
            "noise_floor_pct": floor.pct,
            "noise_floor_level": floor.level,
            "noise_floor_samples": floor.samples,
            "gain_within_noise": within_noise,
            "ratio_spread": ctx.ratio_spread(stage),
            # rule 3
            "history_runs": attribution.runs,
            "history_distinct_configs": attribution.distinct_configs,
            "delta_attributable": attribution.creditable,
            # BUG 1
            "join_node": join.has_join_node,
            "plan_fingerprint": stage.plan_fingerprint,
        },
    )


def _confidence(width_source: str, strong: bool, slots_unknown: bool, floor_known: bool) -> float:
    """Confidence tracks how well the closed form's INPUTS are known."""
    if slots_unknown:
        # Rule 1: "if it cannot be determined, confidence is capped, never
        # guessed." No LLM can supply a cluster width either, so this stays
        # deterministic and below the HIGH tier rather than being escalated.
        return CONF_SLOTS_UNKNOWN
    if width_source == "job_conf":
        score = CONF_CONF_STRONG if strong else CONF_CONF_WEAK
    else:
        score = CONF_OPERATOR_STRONG if strong else CONF_OPERATOR_WEAK
    return score if floor_known else round(score - NO_FLOOR_PENALTY, 2)


def _evidence(stage, tail, join, gain_pct, within_noise: bool) -> str:
    """The STABLE core of the claim — everything the signature may derive from.

    `evidence` is persisted and is part of the dedup signature
    (`clickhouse._signature`), so it may only carry what re-analysis of THIS job
    reproduces byte-for-byte. The measured floor (pct, sample count) and the
    ratio spread are functions of OTHER runs and move every time a sibling run
    lands; rendered here they made one finding sign differently on each
    re-analysis, and `persist_new_findings` accumulated rows instead of
    converging. They live in `details` (exclude=True, never persisted) — already
    populated in `evaluate` — never in this string.
    """
    parts = [
        f"p99/p50 = {tail.ratio:.2f}x on stage {stage.stage_id} "
        f"(p99={stage.task_duration_p99_ms:.0f}ms, p50={stage.task_duration_p50_ms:.0f}ms, "
        f"{stage.task_count} tasks, {human_bytes(int(stage.bytes_per_task))}/task)",
        tail.explain(),
    ]
    if not join.supports_join_skew:
        parts.append(f"NOT reported as join skew: {join.why_not()}")
    if within_noise:
        # Rule 2: the number is NOT rendered — it is below the measured floor and
        # therefore unresolvable, which is a statement about verifiability only.
        # The floor FIGURE is not quoted either: it moves as history grows.
        parts.append(
            "the predicted win is BELOW this shape's measured run-to-run floor, "
            "so no replay could confirm it and the figure is withheld"
        )
    elif gain_pct is not None:
        basis = "at this width" if tail.headroom_frac is not None else "at ANY width"
        parts.append(
            f"an ideal rebalance could remove at most {gain_pct:.1f}% of this stage's "
            f"wall time (upper bound {basis})"
        )
    return "; ".join(parts)


def _impact(tail, gain_pct, floor, within_noise: bool) -> str:
    if within_noise:
        return (
            "A skewed join is present and the stage is tail-bound, but this shape's own "
            f"run-to-run spread ({floor}) is wider than anything removing the tail could "
            "return. The skew is real; the payoff is not measurable on this cluster, so "
            "this is reported for awareness rather than as a tuning opportunity."
        )
    if tail.verdict == SLOTS_UNKNOWN:
        bound = f" Even on an unbounded cluster it could not return more than {gain_pct:.1f}%." if gain_pct is not None else ""
        return (
            "The stage's slowest task is far slower than its median. Whether that tail actually "
            "bounds the stage depends on cluster width, which this run's telemetry does not "
            f"carry, so the cost of the tail cannot be quantified here — only its shape.{bound}"
        )
    head = f"at most {gain_pct:.1f}% of the stage's wall time" if gain_pct is not None else "the tail"
    floor_note = (
        f" That is above the {floor.pct:.1f}% run-to-run floor measured for this shape, so it is "
        f"a resolvable difference."
        if floor.known
        else " No repeated runs of this shape exist to say how much of that is resolvable."
    )
    return (
        f"The stage cannot finish before its slowest partition: most slots idle while one task "
        f"finishes, and removing the tail could return {head}.{floor_note}"
    )


def _fix(ctx, is_join: bool, attribution) -> str:
    """The fix, with the NO-OP CHECK applied before anything is recommended.

    Apex's headline false positive recommended `skewJoin.enabled=true` on a run
    where it was already `true` (and it is `true` in 51 of 51 `job_conf` rows in
    this store). verify/ owns the full gate; engine's duty is not to emit an
    obviously-already-enabled recommendation in the first place.
    """
    if not is_join:
        # skewJoin only ever applies to a join. Recommending it here would repeat
        # the category error this watcher was rebuilt to stop.
        steps = [
            "This is a task-level tail, not join skew: spark.sql.adaptive.skewJoin.* does not "
            "apply. Rebalance the input instead — repartition on a higher-cardinality key, "
            "split the oversized input partition, or salt the grouping key"
        ]
    else:
        active = ctx.job_conf.already_active(SKEW_JOIN_ENABLED, "true")
        if active is True:
            steps = [
                f"NO-OP CHECK: {SKEW_JOIN_ENABLED} is ALREADY true on this run — do not "
                "recommend enabling it. Remove the skew at the source instead: salt the hot "
                "key, pre-aggregate before the join, or broadcast the small side"
            ]
        elif active is False:
            steps = [
                f"Set {SKEW_JOIN_ENABLED}=true (observed false on this run); if the hot key "
                "survives that, salt it or broadcast the small side"
            ]
        else:
            steps = [
                f"Whether {SKEW_JOIN_ENABLED} was already in force cannot be read for this run "
                "(no apex.job_conf row), so no config change is recommended: salt the hot key "
                "or broadcast the small side, which works either way"
            ]
    if not attribution.creditable:
        steps.append(f"attribution: {attribution.explain()}")
    return ". ".join(steps) + "."
