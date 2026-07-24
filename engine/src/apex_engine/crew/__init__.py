"""Tier 2 — CrewAI. Reached ONLY through the escalation gate.

Nothing in this package runs for a healthy job, and nothing here runs for a
finding Tier 1 is already confident about. `is_available()` is checked before
any import cost is paid, so an engine without `crewai` installed or without an
API key still runs the full deterministic tier.
"""

from __future__ import annotations

import json
from typing import Any, Callable

from ..schema import Finding
from .judge import REJECTION_THRESHOLD, build_crew, merge_verdict

__all__ = [
    "REJECTION_THRESHOLD",
    "build_crew",
    "is_available",
    "judge_candidates",
    "merge_verdict",
]

# Two LLM-backed task executions per escalated candidate: correlate, then judge.
TASKS_PER_CANDIDATE = 2


def is_available() -> tuple[bool, str]:
    """Can the crew actually run? Cheap to call; imports nothing heavy on failure."""
    try:
        import crewai  # noqa: F401
    except ImportError:
        return False, "crewai_not_installed"

    from ..config import anthropic_api_key

    if not anthropic_api_key():
        return False, "no_anthropic_api_key"
    return True, "ok"


def _crew_inputs(candidate: Finding, siblings: list[Finding]) -> dict[str, Any]:
    """Everything the crew is allowed to see, as plain JSON."""
    return {
        "candidate": json.dumps(candidate.model_dump(mode="json"), default=str),
        "evidence": json.dumps(candidate.details, default=str),
        "siblings": json.dumps(
            [
                {"type": s.type.value, "stage_id": s.stage_id, "severity": s.severity.value,
                 "evidence": s.evidence}
                for s in siblings
                if s.finding_id != candidate.finding_id
            ],
            default=str,
        ),
    }


def judge_candidates(
    candidates: list[Finding],
    store=None,
    *,
    all_findings: list[Finding] | None = None,
    crew_factory: Callable[..., Any] | None = None,
) -> tuple[list[Finding], int]:
    """Run correlation + judging over the escalated candidates.

    Returns `(surviving_findings, llm_backed_task_executions)`. A candidate the
    Judger rejects is dropped. A candidate whose crew run FAILS is kept at its
    Tier-1 confidence — an infrastructure problem must not silently delete a
    finding a deterministic rule already measured.
    """
    if not candidates:
        return [], 0

    factory = crew_factory or build_crew
    siblings = all_findings if all_findings is not None else candidates

    survivors: list[Finding] = []
    calls = 0

    for candidate in candidates:
        crew = factory(candidate, store)
        try:
            output = crew.kickoff(inputs=_crew_inputs(candidate, siblings))
            calls += TASKS_PER_CANDIDATE
            judged = getattr(output, "pydantic", None)
        except Exception as exc:  # noqa: BLE001 - never lose a measured finding
            survivors.append(
                candidate.model_copy(update={
                    "details": {**candidate.details, "crew_error": str(exc)[:200]},
                })
            )
            continue

        if (merged := merge_verdict(candidate, judged)) is not None:
            survivors.append(merged)

    return survivors, calls
