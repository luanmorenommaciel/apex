"""Tier 1 — the six deterministic watchers, plus the AQE ground-truth watcher.

ALL of these are plain Python functions over deterministic SQL rules. None is a
CrewAI agent, none is `@tool`-wrapped, none calls an LLM. Tier 1 answers 95%+ of
findings at $0; CrewAI only ever sees what the gate escalates.

Two feeds, one rule set:
  * `run_all(job_id, store)`  — reads ClickHouse (the real path);
  * `run_all_offline(...)`    — the same rules over in-memory aggregates.
Both evaluate `StageAggregate` rows produced by the same reduction, so they
cannot disagree.

Every `evaluate` takes an optional `JobContext` — the job-scoped observations the
cross-lane rules need (cluster width, measured noise floors, config history).
It is optional so the offline path stays a one-liner, and a missing context is
the EMPTY one, in which the rules that depend on it degrade to "cannot
determine" rather than to a default.
"""

from __future__ import annotations

from ..context import JobContext, context_for
from ..schema import Finding, PlanTransition, StageAggregate
from . import aqe, code, cost, memory, retry_pressure, shuffle, skew

# The six contract watchers. Order is the order findings are emitted in.
STAGE_WATCHERS = (skew, shuffle, memory, cost, code, retry_pressure)
WATCHER_NAMES = tuple(module.NAME for module in STAGE_WATCHERS) + (aqe.NAME,)

__all__ = [
    "STAGE_WATCHERS",
    "WATCHER_NAMES",
    "aqe", "code", "cost", "memory", "retry_pressure", "shuffle", "skew",
    "run_all", "run_all_offline",
]


def run_all_offline(
    aggregates: list[StageAggregate],
    transitions: list[PlanTransition] | None = None,
    ctx: JobContext | None = None,
) -> list[Finding]:
    """Every deterministic rule over already-materialized rows. No I/O, no LLM."""
    transitions = list(transitions or [])
    ctx = context_for(ctx)
    findings: list[Finding] = []

    for module in STAGE_WATCHERS:
        for stage in aggregates:
            if finding := module.evaluate(stage, ctx):
                findings.append(finding)

    findings.extend(code.evaluate_job(aggregates))

    if aggregates:
        findings.extend(aqe.evaluate_job(aggregates[0].job_id, aggregates[0].app_id, transitions))
    elif transitions:
        findings.extend(aqe.evaluate_job(transitions[0].job_id, "", transitions))

    # Ground truth outranks heuristics: let AQE upgrade what it confirms.
    return aqe.corroborate_skew(findings, transitions)


def run_all(job_id: str, store, ctx: JobContext | None = None) -> list[Finding]:
    """Deterministic analysis of one job straight out of ClickHouse."""
    return run_all_offline(
        store.stage_aggregates(job_id), store.plan_transitions(job_id), ctx
    )
