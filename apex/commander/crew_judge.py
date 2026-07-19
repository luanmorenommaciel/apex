"""Commander Crew/Judge read-only diagnosis tool."""

from __future__ import annotations

from typing import Any

from apex.commander.judge_contract import (
    build_judge_envelope,
    validate_judge_decision,
)
from apex.commander.judge_policy import evaluate_judge_policy
from apex.commander.judge_providers import select_judge_provider
from apex.commander.mcp_contract import debug_job, explain_evidence
from apex.commander.recommendations import recommend_fix

RULE_SET = "apex.commander.crew_judge.v1"


def crew_judge_diagnose(
    store,
    finding_store,
    job_id: str,
    *,
    provider: str = "auto",
) -> dict[str, Any]:
    """Run a read-only Judge pass after deterministic diagnosis."""
    debug = debug_job(store, job_id)
    finding = debug.get("finding") or {}
    validation = debug.get("validation") or {}
    policy = evaluate_judge_policy(finding, validation)
    evidence = explain_evidence(store, job_id)
    recommendations = recommend_fix(finding_store, job_id).get("recommendations", [])
    envelope = build_judge_envelope(
        job_id=job_id,
        finding=finding,
        validation=validation,
        policy=policy,
        evidence=evidence,
        candidate_recommendations=recommendations,
    )

    selected = select_judge_provider(provider)
    decision = selected.diagnose(envelope)
    contract_validation = validate_judge_decision(decision, envelope)

    return {
        "job_id": job_id,
        "status": decision["status"],
        "rule_set": RULE_SET,
        "provider_requested": provider,
        "provider_used": decision["provider"],
        "policy": policy,
        "decision": decision,
        "contract_validation": contract_validation,
        "read_only": True,
        "mutation_allowed": False,
    }
