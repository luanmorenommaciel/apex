"""Deterministic escalation policy for a future Crew/Judge layer."""

from __future__ import annotations

from numbers import Real
from typing import Any


DEFAULT_ESCALATION_THRESHOLD = 0.6

CONFIDENCE_LABEL_SCORES = {
    "none": 0.0,
    "unknown": 0.0,
    "low": 0.3,
    "medium": 0.6,
    "high": 0.85,
    "critical": 0.95,
}


def confidence_score(confidence: Any) -> float:
    """Normalize Commander confidence into a numeric score in [0.0, 1.0]."""
    if isinstance(confidence, bool):
        return 1.0 if confidence else 0.0

    if isinstance(confidence, Real):
        return max(0.0, min(1.0, float(confidence)))

    if isinstance(confidence, str):
        normalized = confidence.strip().lower()
        if normalized in CONFIDENCE_LABEL_SCORES:
            return CONFIDENCE_LABEL_SCORES[normalized]
        try:
            return max(0.0, min(1.0, float(normalized)))
        except ValueError:
            return 0.0

    return 0.0


def evaluate_judge_policy(
    finding: dict[str, Any],
    validation: dict[str, Any] | None = None,
    threshold: float = DEFAULT_ESCALATION_THRESHOLD,
) -> dict[str, Any]:
    """Route a finding between deterministic T1 and the future Crew/Judge path.

    This is intentionally local and dependency-free. It defines the contract
    that a future Crew.ai/Judge implementation can consume without becoming a
    required dependency for the fast deterministic path.
    """
    score = confidence_score(finding.get("confidence"))
    reasons = []

    if score < threshold:
        reasons.append("confidence_below_threshold")

    if validation is not None and validation.get("accepted") is False:
        reasons.append("evidence_validator_rejected")

    route = "crew_judge" if reasons else "deterministic_t1"
    return {
        "status": "escalate" if reasons else "keep_deterministic",
        "route": route,
        "should_escalate": bool(reasons),
        "threshold": threshold,
        "confidence": finding.get("confidence"),
        "confidence_score": score,
        "reasons": reasons,
        "finding_kind": finding.get("kind") or finding.get("title"),
        "job_id": finding.get("job_id"),
        "future_contract": {
            "tool": "crew_judge_diagnose",
            "required_inputs": [
                "job_id",
                "finding_kind",
                "confidence_score",
                "evidence",
                "validation",
            ],
            "must_return": [
                "decision",
                "rationale",
                "cited_evidence",
                "recommended_next_action",
            ],
            "guardrail": "judge_must_cite_existing_evidence",
        },
    }
