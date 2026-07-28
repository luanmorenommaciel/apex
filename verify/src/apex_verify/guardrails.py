"""The four deterministic guardrails — the reason this lane exists.

Each one can veto a fix using only data Apex already has, at zero execution cost.
They exist because Apex's own marquee finding failed all four at once
(`189e3495…`, `SKEW_ON_JOIN`, stage 4 of `app-20260724160310-0000`, "critical
21.62x"):

  a. NO-OP GATE       the recommended `spark.sql.adaptive.skewJoin.enabled=true`
                      was ALREADY `true` in the observed run.
  b. BOUND ANALYSIS   stage 4 is work-bound on 2 slots, so a *perfect* skew fix
                      returns 0.0 ms.
  c. NOISE FLOOR      the "21.62x" is 21.62 / 24.71 / 24.53 across three
                      byte-identical runs; job runtime CV is 5.8%.
  d. MECHANISM CHECK  stage 4 moves 278 bytes/task and its plan contains no Join
                      node at all — it is Delta transaction-log processing.

This is DataFlint's published SimilarWeb failure (a confidently-suggested
`repartition(20000)` that left a 3-hour job at 3 hours) reproduced inside Apex.
Refusing beats guessing, so refusal is a first-class output.

SECURITY: `plan_json` is written by the OBSERVED Spark job, not by Apex — the
indirect-injection vector `serve/README.md` documents. It is only ever
regex-matched here, and any excerpt that reaches `detail` is flattened and
truncated by `_excerpt`. It is never evaluated and never re-emitted as prose.
"""

from __future__ import annotations

import re
import statistics
from typing import Iterable, Mapping

from .models import Guardrail, Predictor, StageObservation

# ── (d) mechanism thresholds ────────────────────────────────────────────────
# A task touching under 1 MiB cannot have a DATA-VOLUME tail; a wide p99/p50 at
# that scale is JVM warm-up and scheduler jitter. Chosen as the smallest volume
# at which a single Spark partition's work is plausibly measurable above startup
# cost, not tuned to any one job.
SKEW_MIN_BYTES_PER_TASK = 1 << 20  # 1 MiB

# A p99 over a handful of tasks is not a distribution (engine uses the same 4).
MIN_TASKS_FOR_RATIO = 4

# Logical-plan node names that mean "a join happens in this stage".
_JOIN_NODE = re.compile(r"\bJoin\b|\bBroadcastHashJoin\b|\bSortMergeJoin\b|\bShuffledHashJoin\b")

# ── (a) no-op gate ─────────────────────────────────────────────────────────
# Spark defaults for the perf keys we reason about. VERSION-SENSITIVE: these are
# the Spark 3.5 / 4.x values, which is what this repo pins (Spark 4.0.1 / 4.1.2).
# A key absent here is treated as "no known default" -> we cannot claim the
# proposed value is already in force, so the gate stays silent.
SPARK_DEFAULTS: Mapping[str, str] = {
    "spark.sql.adaptive.enabled": "true",              # true since 3.2.0
    "spark.sql.adaptive.skewJoin.enabled": "true",     # true when AQE is on
    "spark.sql.adaptive.coalescePartitions.enabled": "true",
    "spark.sql.adaptive.skewJoin.skewedPartitionFactor": "5",
    "spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes": "256MB",
    "spark.sql.adaptive.advisoryPartitionSizeInBytes": "64MB",
    "spark.sql.shuffle.partitions": "200",
    "spark.sql.autoBroadcastJoinThreshold": "10MB",
    "spark.sql.files.maxPartitionBytes": "128MB",
}

_BYTE_UNITS = {"": 1, "b": 1, "k": 1 << 10, "kb": 1 << 10, "m": 1 << 20, "mb": 1 << 20,
               "g": 1 << 30, "gb": 1 << 30, "t": 1 << 40, "tb": 1 << 40}
_BYTE_RE = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*([kmgt]?b?)\s*$", re.IGNORECASE)


def _excerpt(text: str, limit: int = 80) -> str:
    """Flatten untrusted plan text so it cannot forge a heading, fence or newline."""
    flat = re.sub(r"[\s`#|]+", " ", text).strip()
    return (flat[:limit] + "…") if len(flat) > limit else flat


def normalize_conf_value(value: str) -> str:
    """Canonicalize a Spark conf value so equal settings compare equal.

    `true`/`TRUE`/`True` are one value; `16m`, `16MB` and `16777216` are one
    value. Anything unrecognised is lower-cased and stripped only — never
    coerced, so an opaque value still compares exactly.
    """
    v = str(value).strip()
    low = v.lower()
    if low in {"true", "false"}:
        return low
    m = _BYTE_RE.match(low)
    if m and m.group(2) in _BYTE_UNITS:
        try:
            return str(int(float(m.group(1)) * _BYTE_UNITS[m.group(2)]))
        except (ValueError, OverflowError):
            return low
    return low


def noop_gate(
    proposed_config: Mapping[str, str],
    observed_config: Mapping[str, str] | None,
) -> Guardrail:
    """(a) Is every proposed key ALREADY at the proposed value in the observed run?

    Returns a fired guardrail only when we can prove it — either the key is
    explicitly set to an equivalent value, or it is unset and Spark's default for
    this version already equals the proposal. If `observed_config` is None we
    know nothing and must not claim anything.
    """
    if observed_config is None:
        return Guardrail(
            name=Predictor.NOOP_GATE,
            fired=False,
            verdict="config_unknown",
            detail=(
                "The observed run's effective SparkConf is unknown (no apex.job_conf "
                "row and no History Server fallback succeeded — see config_source.py). "
                "Cannot rule out that this fix is already active."
            ),
        )
    if not proposed_config:
        return Guardrail(
            name=Predictor.NOOP_GATE, fired=False, verdict="no_config_proposed",
            detail="No Spark conf overlay was proposed, so there is nothing to compare.",
        )

    already: list[str] = []
    changes: list[str] = []
    for key, want in proposed_config.items():
        want_n = normalize_conf_value(want)
        if key in observed_config:
            have_n = normalize_conf_value(observed_config[key])
            source = "explicitly set"
        elif key in SPARK_DEFAULTS:
            have_n = normalize_conf_value(SPARK_DEFAULTS[key])
            source = "Spark default"
        else:
            changes.append(f"{key}: current value unknown")
            continue
        if have_n == want_n:
            already.append(f"{key}={want} (already {source})")
        else:
            changes.append(f"{key}: {observed_config.get(key, SPARK_DEFAULTS.get(key))} -> {want}")

    if already and not changes:
        return Guardrail(
            name=Predictor.NOOP_GATE,
            fired=True,
            verdict="already_active",
            detail=(
                "Every proposed setting is already in force in the observed run — "
                + "; ".join(already)
                + ". Applying this changes nothing."
            ),
            caps_delta_at_zero=True,
            # A fact read straight off the run's own configuration. Certainty here
            # is warranted; this is a deduction, not an extrapolation.
            score=0.95,
        )
    return Guardrail(
        name=Predictor.NOOP_GATE,
        fired=False,
        verdict="changes_something" if changes else "indeterminate",
        detail=(
            ("Would change: " + "; ".join(changes)) if changes else "No comparison possible."
        )
        + (f" Already in force: {'; '.join(already)}." if already else ""),
    )


def mechanism_check(stage: StageObservation, finding_type: str) -> Guardrail:
    """(d) Is the claimed pathology physically possible in this stage?

    Two independent tests, both from fields the contract already carries:
      * volume — a data-skew tail needs data. Under 1 MiB/task there is none.
      * plan shape — SKEW_ON_JOIN on a stage whose logical plan has no Join node
        is a category error, not a tuning opportunity.
    """
    reasons: list[str] = []
    hard = False

    if stage.task_count and stage.bytes_per_task < SKEW_MIN_BYTES_PER_TASK:
        reasons.append(
            f"the stage moves {stage.bytes_touched:,} bytes across "
            f"{stage.task_count} tasks = {stage.bytes_per_task:,.0f} bytes/task, "
            f"far below the {SKEW_MIN_BYTES_PER_TASK:,} bytes/task at which a "
            f"data-volume tail is even measurable — the duration spread is "
            f"JVM warm-up and scheduler jitter, not data skew"
        )
        hard = True

    if finding_type.upper() == "SKEW_ON_JOIN" and stage.plan_json:
        if not _JOIN_NODE.search(stage.plan_json):
            reasons.append(
                "the stage's logical plan contains no Join node "
                f"(plan starts: \"{_excerpt(stage.plan_json)}\"), so it cannot "
                "exhibit join skew"
            )
            hard = True
        if stage.shuffle_read_bytes == 0:
            reasons.append(
                "the stage reads 0 shuffle bytes; sort-merge join skew appears on "
                "the shuffle READ side, so a join-skew tail cannot originate here"
            )

    if stage.task_count < MIN_TASKS_FOR_RATIO:
        reasons.append(
            f"{stage.task_count} tasks is too few for a p99 to describe a distribution"
        )
        hard = True

    if not reasons:
        return Guardrail(
            name=Predictor.MECHANISM_CHECK, fired=False, verdict="plausible",
            detail=(
                f"Mechanism is plausible: {stage.bytes_per_task:,.0f} bytes/task over "
                f"{stage.task_count} tasks."
            ),
        )
    return Guardrail(
        name=Predictor.MECHANISM_CHECK,
        fired=True,
        verdict="mechanism_impossible" if hard else "mechanism_doubtful",
        detail=f"The finding's premise does not hold: {'; and '.join(reasons)}.",
        caps_delta_at_zero=hard,
        score=0.90 if hard else 0.55,
    )


def noise_floor(
    stage: StageObservation,
    siblings: Iterable[StageObservation] = (),
    job_runtimes_ms: Iterable[float] = (),
) -> Guardrail:
    """(c) Is the signal distinguishable from run-to-run variance?

    Two separate claims, deliberately not conflated:
      1. ratio instability — if p99/p50 swings across *identical* runs, the exact
         quoted ratio is not a stable quantity and must be quoted as a range.
         (This attacks the finding's precision, not its existence.)
      2. verifiability floor — the CV of total job runtime is the minimum
         detectable effect. No predicted improvement below it can be confirmed by
         replay, however many repetitions we run.
    """
    sib = [s for s in siblings if s.task_duration_p50_ms > 0]
    ratios = [s.skew_ratio for s in sib]
    parts: list[str] = []
    score: float | None = None
    fired = False

    if len(ratios) >= 3:
        mean_r = statistics.mean(ratios)
        sd_r = statistics.stdev(ratios)
        cv_r = 100 * sd_r / mean_r if mean_r else 0.0
        parts.append(
            f"across {len(ratios)} runs of the same query at the same config the "
            f"p99/p50 ratio is {', '.join(f'{r:.2f}x' for r in ratios)} "
            f"(mean {mean_r:.2f}x, sd {sd_r:.2f}, CV {cv_r:.1f}%) — the observed "
            f"{stage.skew_ratio:.2f}x is one draw from that spread, not a fixed property"
        )
        if cv_r >= 5.0:
            fired = True
            score = 0.80

    runtimes = [r for r in job_runtimes_ms if r > 0]
    if len(runtimes) >= 3:
        mean_t = statistics.mean(runtimes)
        cv_t = 100 * statistics.stdev(runtimes) / mean_t if mean_t else 0.0
        parts.append(
            f"total job runtime over the same {len(runtimes)} runs is "
            f"{', '.join(f'{t:.0f}ms' for t in runtimes)} (mean {mean_t:.0f}ms, "
            f"CV {cv_t:.1f}%), so {cv_t:.1f}% is the minimum effect any replay "
            f"of this shape can resolve"
        )

    if not parts:
        return Guardrail(
            name=Predictor.NOISE_FLOOR, fired=False, verdict="no_baseline",
            detail="No repeated runs of this shape are available, so no noise floor is known.",
        )
    return Guardrail(
        name=Predictor.NOISE_FLOOR,
        fired=fired,
        verdict="signal_within_noise" if fired else "noise_characterised",
        detail=("Measured run-to-run variance: " + "; ".join(parts) + "."),
        caps_delta_at_zero=False,   # noise never proves a delta is zero, only unresolvable
        score=score,
    )


def runtime_cv_pct(job_runtimes_ms: Iterable[float]) -> float | None:
    """Coefficient of variation (%) of a set of runtimes. None if under 2 samples."""
    vals = [v for v in job_runtimes_ms if v > 0]
    if len(vals) < 2:
        return None
    mean = statistics.mean(vals)
    return 100 * statistics.stdev(vals) / mean if mean else None
