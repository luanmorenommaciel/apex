"""Tier-1 deterministic pipeline with a gated, auditable Tier-2 Judge."""

from __future__ import annotations

from collections.abc import Iterable

from .schema import Finding, StageEvent
from .crew import CandidateJudge, configured_judge, decision_is_grounded, requires_judge
from .validation import validate_finding
from .watchers import run_all


def analyze_events(
    events: Iterable[StageEvent | dict[str, object]], judge: CandidateJudge | None = None
) -> dict[str, object]:
    normalized = [event if isinstance(event, StageEvent) else StageEvent.model_validate(event) for event in events]
    candidates = run_all(normalized)
    accepted: list[Finding] = []
    rejected: list[dict[str, object]] = []
    judge = judge if judge is not None else configured_judge()
    llm_calls = 0
    for finding in candidates:
        validation = validate_finding(finding)
        if not validation["accepted"]:
            rejected.append({"finding": finding, "validation": validation})
            continue
        if judge is None or not requires_judge(finding):
            accepted.append(finding)
            continue
        llm_calls += 1
        decision = judge.judge(finding)
        if decision.decision == "confirm" and decision_is_grounded(decision, finding):
            accepted.append(finding)
        else:
            rejected.append({
                "finding": finding,
                "validation": validation,
                "judge": decision.model_dump(),
                "reason": "judge_rejected_or_ungrounded",
            })
    return {
        "mode": "gated_crew" if llm_calls else "deterministic",
        "llm_calls": llm_calls,
        "findings": accepted,
        "rejected": rejected,
    }


def analyze_job(store, job_id: str) -> dict[str, object]:
    """Run deterministic analysis for persisted telemetry and write accepted rows."""
    result = analyze_events(store.stage_events(job_id))
    result["written_rows"] = store.persist_findings(result["findings"])
    return result
