"""Deterministic C0/C1 pipeline with no CrewAI dependency or side effect."""

from __future__ import annotations

from collections.abc import Iterable

from .schema import Finding, StageEvent
from .validation import validate_finding
from .watchers import run_all


def analyze_events(events: Iterable[StageEvent | dict[str, object]]) -> dict[str, object]:
    normalized = [event if isinstance(event, StageEvent) else StageEvent.model_validate(event) for event in events]
    candidates = run_all(normalized)
    accepted: list[Finding] = []
    rejected: list[dict[str, object]] = []
    for finding in candidates:
        validation = validate_finding(finding)
        if validation["accepted"]:
            accepted.append(finding)
        else:
            rejected.append({"finding": finding, "validation": validation})
    return {"mode": "deterministic", "llm_calls": 0, "findings": accepted, "rejected": rejected}


def analyze_job(store, job_id: str) -> dict[str, object]:
    """Run deterministic analysis for persisted telemetry and write accepted rows."""
    result = analyze_events(store.stage_events(job_id))
    result["written_rows"] = store.persist_findings(result["findings"])
    return result
