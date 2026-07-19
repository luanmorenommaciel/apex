"""Serializable contract for Commander Judge decisions."""

from __future__ import annotations

from typing import Any

RULE_SET = "apex.commander.judge_contract.v1"

ALLOWED_DECISIONS = {
    "confirm_finding",
    "reject_finding",
    "request_more_evidence",
    "manual_review",
}

ALLOWED_NEXT_ACTIONS = {
    "recommend_fix",
    "request_more_evidence",
    "manual_review",
    "none",
}

REQUIRED_GUARDRAILS = [
    "must_cite_existing_evidence",
    "must_not_invent_metrics",
    "must_not_invent_root_cause",
    "must_mark_unknown_when_evidence_is_missing",
    "must_not_apply_changes_directly",
]


def build_judge_envelope(
    *,
    job_id: str,
    finding: dict[str, Any],
    validation: dict[str, Any],
    policy: dict[str, Any],
    evidence: dict[str, Any] | None = None,
    candidate_recommendations: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build the only payload a Judge provider may inspect."""
    return {
        "rule_set": RULE_SET,
        "job_id": job_id,
        "finding": finding or {},
        "validation": validation or {},
        "policy": policy or {},
        "evidence": evidence or {},
        "candidate_recommendations": candidate_recommendations or [],
        "guardrails": list(REQUIRED_GUARDRAILS),
    }


def normalize_judge_decision(
    decision: dict[str, Any],
    *,
    provider: str,
    envelope: dict[str, Any],
) -> dict[str, Any]:
    """Normalize and constrain a provider decision to the Judge contract."""
    raw_decision = str(decision.get("decision") or "manual_review")
    normalized_decision = (
        raw_decision if raw_decision in ALLOWED_DECISIONS else "manual_review"
    )
    raw_next_action = str(decision.get("recommended_next_action") or "manual_review")
    next_action = (
        raw_next_action if raw_next_action in ALLOWED_NEXT_ACTIONS else "manual_review"
    )
    cited_evidence = _valid_cited_evidence(decision.get("cited_evidence"), envelope)
    human_review_required = bool(
        decision.get("human_review_required", normalized_decision != "confirm_finding")
    )

    if not cited_evidence:
        normalized_decision = "manual_review"
        next_action = "manual_review"
        human_review_required = True

    return {
        "status": decision.get("status", "judged"),
        "provider": provider,
        "rule_set": RULE_SET,
        "decision": normalized_decision,
        "rationale": str(decision.get("rationale") or "manual review required"),
        "cited_evidence": cited_evidence,
        "recommended_next_action": next_action,
        "human_review_required": human_review_required,
        "guardrails": list(REQUIRED_GUARDRAILS),
        "raw_provider_status": decision.get("status", "judged"),
    }


def validate_judge_decision(
    decision: dict[str, Any],
    envelope: dict[str, Any],
) -> dict[str, Any]:
    """Validate anti-hallucination constraints for a Judge decision."""
    issues = []
    if decision.get("decision") not in ALLOWED_DECISIONS:
        issues.append("invalid_decision")
    if decision.get("recommended_next_action") not in ALLOWED_NEXT_ACTIONS:
        issues.append("invalid_recommended_next_action")
    if not decision.get("cited_evidence"):
        issues.append("missing_cited_evidence")
    elif not _valid_cited_evidence(decision.get("cited_evidence"), envelope):
        issues.append("cited_evidence_not_present_in_envelope")
    if decision.get("recommended_next_action") == "apply_fix":
        issues.append("judge_must_not_apply_changes_directly")

    return {
        "rule_set": RULE_SET,
        "accepted": not issues,
        "status": "valid" if not issues else "invalid",
        "issues": issues,
    }


def evidence_citations(envelope: dict[str, Any]) -> list[str]:
    """Return stable citation strings derived only from existing evidence."""
    finding = envelope.get("finding") or {}
    validation = envelope.get("validation") or {}
    evidence = finding.get("evidence") or {}
    citations = []

    for key in (
        "app_id",
        "stage_id",
        "ratio",
        "hot_records",
        "median_cold_records",
        "spilled_bytes",
        "gc_ratio",
        "failure_reasons",
        "physical_plan",
    ):
        if key in evidence:
            citations.append(f"finding.evidence.{key}={evidence[key]}")

    if "accepted" in validation:
        citations.append(f"validation.accepted={validation['accepted']}")
    if validation.get("issues"):
        citations.append(f"validation.issues={validation['issues']}")

    envelope_evidence = envelope.get("evidence") or {}
    if envelope_evidence.get("app_id"):
        citations.append(f"evidence.app_id={envelope_evidence['app_id']}")
    if envelope_evidence.get("event_counts"):
        citations.append(f"evidence.event_counts={envelope_evidence['event_counts']}")

    return citations


def _valid_cited_evidence(value: Any, envelope: dict[str, Any]) -> list[str]:
    if isinstance(value, str):
        requested = [value]
    elif isinstance(value, list):
        requested = [str(item) for item in value if str(item).strip()]
    else:
        requested = []

    allowed = set(evidence_citations(envelope))
    return [item for item in requested if item in allowed]
