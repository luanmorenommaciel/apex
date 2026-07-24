"""Gated CrewAI correlation and adversarial judgement for Tier 2.

Tier 1 remains the source of truth for metrics.  This module only receives
validated deterministic candidates and returns an auditable accept/reject
decision; it never writes findings or executes a remediation.
"""

from __future__ import annotations

import os
from typing import Literal, Protocol

from pydantic import BaseModel, Field

from .schema import Confidence, Finding, Severity


CONFIDENCE_SCORE = {
    Confidence.LOW: 0.3,
    Confidence.MEDIUM: 0.6,
    Confidence.HIGH: 0.9,
}


class JudgeDecision(BaseModel):
    """The only data a Tier 2 provider may return to the pipeline."""

    decision: Literal["confirm", "reject"]
    rationale: str = Field(min_length=1, max_length=2_000)
    cited_evidence: list[str] = Field(default_factory=list)


class CandidateJudge(Protocol):
    def judge(self, finding: Finding) -> JudgeDecision: ...


def requires_judge(finding: Finding) -> bool:
    """The documented gate: confidence < 0.6 and severity >= high.

    The v0.2 contract has categorical confidence, so LOW maps to 0.3,
    MEDIUM to 0.6 and HIGH to 0.9.  "high" severity is represented by
    CRITICAL/BLOCKER in the frozen contract.
    """

    return (
        CONFIDENCE_SCORE[finding.confidence] < 0.6
        and finding.severity.at_least(Severity.CRITICAL)
    )


class CrewAIJudge:
    """Lazy CrewAI adapter so deterministic installs need no provider or key."""

    def __init__(self, correlator_model: str, judge_model: str) -> None:
        self._correlator_model = correlator_model
        self._judge_model = judge_model

    def judge(self, finding: Finding) -> JudgeDecision:
        try:
            from crewai import Agent, Crew, LLM, Process, Task
        except ImportError as exc:  # pragma: no cover - depends on optional extra
            raise RuntimeError("crewai_extra_not_installed") from exc

        payload = finding.model_dump(mode="json", exclude={"details"})
        evidence = finding.evidence
        correlator = Agent(
            role="APEX evidence correlator",
            goal="Correlate only the supplied deterministic evidence.",
            backstory="You never invent metrics or root causes.",
            llm=LLM(model=self._correlator_model, temperature=0.0),
            allow_delegation=False,
        )
        judger = Agent(
            role="APEX adversarial finding judge",
            goal="Reject candidates whose supplied evidence is insufficient.",
            backstory="You are skeptical and must cite the supplied evidence.",
            llm=LLM(model=self._judge_model, temperature=0.0),
            allow_delegation=False,
        )
        correlate_task = Task(
            description=f"Correlate this finding without adding facts: {payload}",
            expected_output="Evidence-only correlation notes.",
            agent=correlator,
        )
        judge_task = Task(
            description=(
                "Return confirm or reject, a short rationale, and exact citations "
                f"from this evidence only: {evidence!r}."
            ),
            expected_output="A structured JudgeDecision.",
            agent=judger,
            context=[correlate_task],
            output_pydantic=JudgeDecision,
        )
        result = Crew(
            agents=[correlator, judger], tasks=[correlate_task, judge_task],
            process=Process.sequential,
        ).kickoff()
        return JudgeDecision.model_validate(result.pydantic)


def configured_judge() -> CandidateJudge | None:
    """Return a real provider only after explicit operator opt-in."""

    if os.getenv("APEX_CREW_JUDGE_ENABLED") != "1":
        return None
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("anthropic_api_key_required_for_crew_judge")
    return CrewAIJudge(
        correlator_model=os.getenv("APEX_CREW_CORRELATOR_MODEL", "anthropic/claude-sonnet-5"),
        judge_model=os.getenv("APEX_CREW_JUDGE_MODEL", "anthropic/claude-opus-4-8"),
    )


def decision_is_grounded(decision: JudgeDecision, finding: Finding) -> bool:
    """Reject a provider answer that does not cite supplied deterministic evidence."""

    return bool(decision.cited_evidence) and all(
        citation and citation in finding.evidence for citation in decision.cited_evidence
    )
