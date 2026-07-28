"""The closed form. CONTRACT.md cross-lane rule 1, and nothing else.

    tail-bound  <=>  p99/p50 > (n_tasks - 1) / (slots - 1)

This is a list-scheduling makespan bound, not a heuristic. Data volume CANCELS
OUT of it (volume scales p50 and p99 together), so the threshold depends only on
how many tasks the stage has and how wide the cluster is. Two consequences the
old fixed `5x`/`10x` thresholds got wrong in both directions:

  * a 21.6x ratio on 50 tasks / 2 slots needs > 49x to be tail-bound — the old
    rule called it CRITICAL, the physics says the stage is WORK-bound and a
    perfect skew fix returns nothing;
  * a 1.5x ratio on 50 tasks / 50 slots needs only > 1x — the old rule never
    looked at it.

`slots` is an OBSERVATION (see jobconf.ClusterWidth). It is never guessed and
never inferred from `spark.sql.shuffle.partitions`, which is a partition count,
not a cluster width. When it is unknown the closed form is not evaluable, and
this module says so rather than substituting a number: `verdict = slots_unknown`
carries `min_slots_required`, the width at which the stage WOULD become
tail-bound, which is derived from the observation itself.

Nothing in this module does I/O and nothing here has a tunable constant.
"""

from __future__ import annotations

from dataclasses import dataclass

# A p99 over a handful of tasks is not a distribution. Shared verbatim with
# verify/ (`guardrails.MIN_TASKS_FOR_RATIO`) so the two lanes cannot disagree
# about what counts as a measurable spread.
MIN_TASKS_FOR_RATIO = 4

# Verdicts. Exhaustive; `TailBound.verdict` is always one of these.
TAIL_BOUND = "tail_bound"
WORK_BOUND = "work_bound"
SLOTS_UNKNOWN = "slots_unknown"
SERIAL = "serial"
NOT_A_DISTRIBUTION = "not_a_distribution"


@dataclass(frozen=True)
class ClusterWidth:
    """Observed cluster width, with provenance. `slots is None` means UNKNOWN.

    `source` is part of the finding's evidence on purpose: a width read off the
    run's own conf and a width supplied by an operator are both observations,
    but they are not equally strong, and a reader is entitled to know which one
    a severity was computed from.
    """

    slots: int | None = None
    source: str = "unknown"
    detail: str = "cluster width not determinable from available telemetry"

    @property
    def known(self) -> bool:
        return self.slots is not None and self.slots > 0

    def __str__(self) -> str:
        return f"{self.slots} slots ({self.source})" if self.known else f"unknown ({self.detail})"


UNKNOWN_WIDTH = ClusterWidth()


@dataclass(frozen=True)
class TailBound:
    """The verdict of rule 1 for one stage, with every input kept visible."""

    n_tasks: int
    ratio: float
    width: ClusterWidth
    threshold: float | None          # (n-1)/(slots-1); None when not evaluable
    verdict: str
    margin: float | None             # ratio / threshold; > 1 means tail-bound
    min_slots_required: float | None  # break-even width for THIS observation
    headroom_frac: float | None      # upper bound on the fraction of stage wall
    #                                  time a perfect rebalance could remove
    headroom_upper_frac: float | None  # the same bound in the slots >= n_tasks
    #                                    limit: width-free, so it survives an
    #                                    unknown cluster width

    @property
    def is_tail_bound(self) -> bool:
        return self.verdict == TAIL_BOUND

    @property
    def claimed_gain_frac(self) -> float | None:
        """The largest win this finding could honestly claim.

        Width-aware when the width is known, and the width-FREE bound otherwise —
        so there is always one quantity to hold against a measured noise floor
        (rule 2), and it is always an upper bound rather than a promise.
        """
        return self.headroom_frac if self.headroom_frac is not None else self.headroom_upper_frac

    @property
    def evaluable(self) -> bool:
        """True when the closed form could actually be applied."""
        return self.verdict in (TAIL_BOUND, WORK_BOUND, SERIAL)

    def explain(self) -> str:
        """One clause, quoting the physics — safe to paste into evidence."""
        if self.verdict == NOT_A_DISTRIBUTION:
            return (
                f"{self.n_tasks} tasks is below the {MIN_TASKS_FOR_RATIO} needed for a p99 "
                f"to describe a distribution"
            )
        if self.verdict == SERIAL:
            return (
                f"cluster width is {self.width.slots} slot: tasks run serially, so the stage is "
                f"work-bound by construction and no tail can dominate it"
            )
        if self.verdict == SLOTS_UNKNOWN:
            need = f"{self.min_slots_required:.1f}" if self.min_slots_required else "?"
            return (
                f"cluster width is {self.width.detail}, so (n-1)/(slots-1) is not evaluable; "
                f"this {self.ratio:.2f}x over {self.n_tasks} tasks is tail-bound only on a "
                f"cluster of more than {need} slots"
            )
        cmp = ">" if self.is_tail_bound else "<="
        return (
            f"p99/p50 = {self.ratio:.2f}x {cmp} (n-1)/(slots-1) = "
            f"({self.n_tasks}-1)/({self.width.slots}-1) = {self.threshold:.2f} "
            f"[{self.width.source}]"
        )


def tail_bound_threshold(n_tasks: int, slots: int | None) -> float | None:
    """(n_tasks - 1) / (slots - 1), or None when that is not a number.

    None for an unknown width and for a single slot (the divisor is 0 — a
    one-slot stage is serial, so no finite ratio makes it tail-bound).
    """
    if slots is None or slots <= 1 or n_tasks < 2:
        return None
    return (n_tasks - 1) / (slots - 1)


def min_slots_for_tail_bound(n_tasks: int, ratio: float) -> float | None:
    """Break-even cluster width: solve ratio > (n-1)/(s-1) for s.

    Derived from the observation alone, so it is reportable even when the width
    is unknown — it converts "we don't know" into "here is what it would take".
    """
    if ratio <= 0 or n_tasks < 2:
        return None
    return 1.0 + (n_tasks - 1) / ratio


def headroom_fraction(n_tasks: int, p50_ms: float, p99_ms: float, slots: int | None) -> float | None:
    """UPPER bound on what removing the tail could return, as a fraction.

    A tail-bound stage's makespan is set by its slowest task (~p99). Perfectly
    rebalanced, the same work takes ~max(n * p50 / slots, p50) — every slot busy
    with an average task, but never less than one task. The difference is the
    most a fix could possibly win, which is what makes it the right quantity to
    compare against a MEASURED noise floor (rule 2): a predicted win under the
    floor cannot be confirmed by replay, so it must not be asserted.

    It is an upper bound and must be labelled as one: it assumes a perfect
    redistribution with no added shuffle.
    """
    if slots is None or slots < 1 or n_tasks < 1 or p99_ms <= 0 or p50_ms <= 0:
        return None
    balanced_ms = max(n_tasks * p50_ms / slots, p50_ms)
    if balanced_ms >= p99_ms:
        return 0.0
    return 1.0 - balanced_ms / p99_ms


def evaluate_tail_bound(
    *,
    n_tasks: int,
    p50_ms: float,
    p99_ms: float,
    width: ClusterWidth = UNKNOWN_WIDTH,
) -> TailBound:
    """Apply rule 1 to one stage. Pure; the only place the closed form is used."""
    ratio = p99_ms / p50_ms if p50_ms > 0 else 0.0
    min_slots = min_slots_for_tail_bound(n_tasks, ratio)
    threshold = tail_bound_threshold(n_tasks, width.slots)
    headroom = headroom_fraction(n_tasks, p50_ms, p99_ms, width.slots)
    # slots >= n_tasks makes `balanced_ms` collapse to p50, which is the most
    # favourable width any cluster could have — hence an upper bound with no
    # width in it at all.
    headroom_upper = headroom_fraction(n_tasks, p50_ms, p99_ms, n_tasks)

    if n_tasks < MIN_TASKS_FOR_RATIO or ratio <= 0:
        verdict = NOT_A_DISTRIBUTION
    elif not width.known:
        verdict = SLOTS_UNKNOWN
    elif width.slots == 1:
        verdict = SERIAL
    elif threshold is not None and ratio > threshold:
        verdict = TAIL_BOUND
    else:
        verdict = WORK_BOUND

    return TailBound(
        n_tasks=n_tasks,
        ratio=ratio,
        width=width,
        threshold=threshold,
        verdict=verdict,
        margin=(ratio / threshold) if threshold else None,
        min_slots_required=min_slots,
        headroom_frac=headroom,
        headroom_upper_frac=headroom_upper,
    )
