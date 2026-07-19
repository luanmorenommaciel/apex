"""Judge providers for optional Commander Crew/Judge escalation."""

from __future__ import annotations

import json
import os
from typing import Any

from apex.commander.judge_contract import (
    evidence_citations,
    normalize_judge_decision,
)


class DeterministicJudgeProvider:
    name = "deterministic"

    def diagnose(self, envelope: dict[str, Any]) -> dict[str, Any]:
        finding = envelope.get("finding") or {}
        validation = envelope.get("validation") or {}
        policy = envelope.get("policy") or {}
        citations = evidence_citations(envelope)

        if not citations:
            raw = {
                "decision": "request_more_evidence",
                "rationale": "Judge could not cite existing evidence from the envelope.",
                "cited_evidence": [],
                "recommended_next_action": "request_more_evidence",
                "human_review_required": True,
            }
            return normalize_judge_decision(raw, provider=self.name, envelope=envelope)

        if validation.get("accepted") is False:
            raw = {
                "decision": "request_more_evidence",
                "rationale": "EvidenceValidator rejected the finding, so more evidence is required before recommending a fix.",
                "cited_evidence": citations[:3],
                "recommended_next_action": "request_more_evidence",
                "human_review_required": True,
            }
            return normalize_judge_decision(raw, provider=self.name, envelope=envelope)

        if policy.get("should_escalate"):
            raw = {
                "decision": "manual_review",
                "rationale": "Policy escalated this finding; deterministic Judge preserves safety and asks for human review.",
                "cited_evidence": citations[:3],
                "recommended_next_action": "manual_review",
                "human_review_required": True,
            }
            return normalize_judge_decision(raw, provider=self.name, envelope=envelope)

        raw = {
            "decision": "confirm_finding",
            "rationale": f"Finding {finding.get('kind') or finding.get('title')} is supported by validated evidence.",
            "cited_evidence": citations[:3],
            "recommended_next_action": "recommend_fix",
            "human_review_required": False,
        }
        return normalize_judge_decision(raw, provider=self.name, envelope=envelope)


class NoopJudgeProvider:
    name = "noop"

    def __init__(self, reason: str = "crew_ai_not_configured"):
        self.reason = reason

    def diagnose(self, envelope: dict[str, Any]) -> dict[str, Any]:
        citations = evidence_citations(envelope)
        raw = {
            "status": "not_configured",
            "decision": "manual_review",
            "rationale": f"Crew/Judge provider is unavailable: {self.reason}.",
            "cited_evidence": citations[:1],
            "recommended_next_action": "manual_review",
            "human_review_required": True,
        }
        return normalize_judge_decision(raw, provider=self.name, envelope=envelope)


class CrewAIJudgeProvider:
    name = "crew_ai"

    def __init__(self, *, enabled: bool | None = None):
        self.enabled = (
            os.environ.get("APEX_CREW_JUDGE_ENABLED") == "1"
            if enabled is None
            else enabled
        )

    def diagnose(self, envelope: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return NoopJudgeProvider("APEX_CREW_JUDGE_ENABLED_not_1").diagnose(envelope)

        try:
            from crewai import Agent, Crew, Task
        except ImportError:
            return NoopJudgeProvider("crewai_import_failed").diagnose(envelope)

        try:
            agent = Agent(
                role="Apex Commander Judge",
                goal=(
                    "Review Spark diagnostic evidence and return only a JSON "
                    "decision using cited evidence from the provided envelope."
                ),
                backstory=(
                    "You are a conservative Spark observability judge. You never "
                    "invent metrics and never apply code changes."
                ),
                allow_delegation=False,
            )
            task = Task(
                description=_crew_task_description(envelope),
                expected_output=(
                    "A JSON object with decision, rationale, cited_evidence, "
                    "recommended_next_action, and human_review_required."
                ),
                agent=agent,
            )
            crew = Crew(agents=[agent], tasks=[task])
            result = crew.kickoff()
            raw = _parse_crew_result(result)
        except Exception as exc:  # pragma: no cover - depends on optional runtime
            return NoopJudgeProvider(f"crew_ai_runtime_failed:{type(exc).__name__}").diagnose(
                envelope
            )

        return normalize_judge_decision(raw, provider=self.name, envelope=envelope)


def select_judge_provider(name: str = "auto"):
    provider = (name or "auto").strip().lower()
    if provider == "deterministic":
        return DeterministicJudgeProvider()
    if provider == "noop":
        return NoopJudgeProvider()
    if provider == "crew_ai":
        return CrewAIJudgeProvider()
    if provider == "auto" and os.environ.get("APEX_CREW_JUDGE_ENABLED") == "1":
        return CrewAIJudgeProvider()
    return DeterministicJudgeProvider()


def _crew_task_description(envelope: dict[str, Any]) -> str:
    allowed_citations = evidence_citations(envelope)
    safe_envelope = {
        "job_id": envelope.get("job_id"),
        "finding": envelope.get("finding"),
        "validation": envelope.get("validation"),
        "policy": envelope.get("policy"),
        "candidate_recommendations": envelope.get("candidate_recommendations"),
        "allowed_citations": allowed_citations,
        "guardrails": envelope.get("guardrails"),
    }
    return (
        "Review this Apex Commander evidence envelope. Return JSON only. "
        "Use cited_evidence values only from allowed_citations. Do not propose "
        "direct apply. Envelope:\n"
        + json.dumps(safe_envelope, sort_keys=True)
    )


def _parse_crew_result(result: Any) -> dict[str, Any]:
    text = getattr(result, "raw", result)
    if not isinstance(text, str):
        text = str(text)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return {
            "decision": "manual_review",
            "rationale": "Crew.ai result was not JSON.",
            "cited_evidence": [],
            "recommended_next_action": "manual_review",
            "human_review_required": True,
        }
    try:
        parsed = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return {
            "decision": "manual_review",
            "rationale": "Crew.ai result JSON could not be parsed.",
            "cited_evidence": [],
            "recommended_next_action": "manual_review",
            "human_review_required": True,
        }
    if not isinstance(parsed, dict):
        return {
            "decision": "manual_review",
            "rationale": "Crew.ai result was not an object.",
            "cited_evidence": [],
            "recommended_next_action": "manual_review",
            "human_review_required": True,
        }
    return parsed
