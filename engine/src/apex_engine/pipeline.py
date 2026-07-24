"""The pipeline: watchers -> validate -> gate -> (gated crew) -> merge -> insert.

`analyze(job_id)` is the lane's entry point and the exit criterion:
a clean job inserts 0 rows and makes 0 LLM calls.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from . import gate
from .clickhouse import EngineStore, aggregate_events
from .schema import Finding, PlanTransition, StageAggregate, StageEvent
from .validation import validate_finding
from .watchers import run_all_offline


def _validate(candidates: Iterable[Finding]) -> tuple[list[Finding], list[dict[str, Any]]]:
    accepted: list[Finding] = []
    rejected: list[dict[str, Any]] = []
    for finding in candidates:
        validation = validate_finding(finding)
        if validation["accepted"]:
            accepted.append(finding)
        else:
            rejected.append({"finding": finding, "validation": validation})
    return accepted, rejected


def analyze_events(events: Iterable[StageEvent | dict[str, object]]) -> dict[str, Any]:
    """Deterministic-only analysis of in-memory events. Never calls an LLM.

    This is the offline/fixture path and the one the six-lane E2E gate drives;
    its `mode`/`llm_calls` contract is what that gate asserts on.
    """
    normalized = [e if isinstance(e, StageEvent) else StageEvent.model_validate(e) for e in events]
    accepted, rejected = _validate(run_all_offline(aggregate_events(normalized)))
    return {"mode": "deterministic", "llm_calls": 0, "findings": accepted, "rejected": rejected}


def analyze_aggregates(
    aggregates: list[StageAggregate],
    transitions: list[PlanTransition] | None = None,
) -> dict[str, Any]:
    """Deterministic-only analysis of already-reduced rows (+ AQE ground truth)."""
    accepted, rejected = _validate(run_all_offline(aggregates, transitions))
    return {"mode": "deterministic", "llm_calls": 0, "findings": accepted, "rejected": rejected}


def analyze(
    job_id: str,
    store: EngineStore | None = None,
    *,
    persist: bool = True,
    use_crew: bool = True,
    crew_factory: Any = None,
) -> dict[str, Any]:
    """Analyze one job end to end.

    Tier 1 runs deterministically over ClickHouse. Only candidates the gate
    escalates (confidence < 0.6 AND severity >= critical) reach CrewAI, and only
    if `use_crew` is on and the crew is actually available. Everything else —
    including every finding of a healthy job, of which there are none — costs $0.
    """
    if not job_id:
        raise ValueError("job_id_required")
    store = store or EngineStore.connect()

    aggregates = store.stage_aggregates(job_id)
    transitions = store.plan_transitions(job_id)
    candidates = run_all_offline(aggregates, transitions)
    accepted, rejected = _validate(candidates)

    direct, escalated = gate.partition(accepted)
    gate_trace = [
        {"type": f.type.value, "stage_id": f.stage_id, "confidence": round(f.confidence_score, 2),
         "severity": f.severity.value, "decision": gate.explain(f)}
        for f in accepted
    ]

    judged: list[Finding] = []
    llm_calls = 0
    crew_status = "not_needed" if not escalated else "skipped"

    if escalated and use_crew:
        from .crew import is_available, judge_candidates

        # An explicitly supplied factory IS the crew, so no key is needed.
        available, reason = (True, "injected") if crew_factory else is_available()
        if available:
            judged, llm_calls = judge_candidates(
                escalated, store=store, all_findings=accepted, crew_factory=crew_factory
            )
            crew_status = "ran"
        else:
            # No API key / crewai not installed: keep the Tier-1 candidates
            # rather than silently losing them, and say so in the trace.
            judged = list(escalated)
            crew_status = f"unavailable:{reason}"
    elif escalated:
        judged = list(escalated)
        crew_status = "disabled"

    # A judged finding is re-validated: the Judger may recalibrate a finding,
    # but it must still be backed by the measurement Tier 1 took.
    judged, judge_rejected = _validate(judged)
    rejected.extend(judge_rejected)

    findings = direct + judged
    persistence = (
        store.persist_new_findings(job_id, findings)
        if persist
        else {"mode": "dry_run", "written_rows": 0, "skipped_existing": 0}
    )

    return {
        "job_id": job_id,
        "mode": "deterministic" if llm_calls == 0 else "deterministic+crew",
        "stages_analyzed": len(aggregates),
        "plan_transitions": len(transitions),
        "candidates": len(candidates),
        "findings": findings,
        "rejected": rejected,
        "escalated": escalated,
        "crew": crew_status,
        "judge_rejected": len(escalated) - len(judged) if crew_status == "ran" else 0,
        "llm_calls": llm_calls,
        "gate_trace": gate_trace,
        "persistence": persistence,
        "written_rows": persistence["written_rows"],
    }


def analyze_job(store: EngineStore, job_id: str) -> dict[str, Any]:
    """Deterministic-only analyze + persist. Kept for the six-lane E2E gate."""
    result = analyze_events(store.stage_events(job_id))
    result["written_rows"] = store.persist_findings(result["findings"])
    return result
