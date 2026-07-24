"""Tier 2 (T11-T13) verified with a MOCKED LLM — no API key, CI-runnable.

The mock is deliberately placed at the LOWEST possible layer: a `BaseLLM`
subclass whose `call()` returns canned JSON. Everything above it is the real
CrewAI machinery — real `Agent`s, real `Task`s with `output_pydantic=Finding`,
a real sequential `Crew` with `context=[correlate_task]`. So these tests prove
the wiring, not a stub of it.

What is NOT proven here (and cannot be, without a key): that Anthropic returns
sensible content. That is what the one-shot live smoke test is for.
"""

from __future__ import annotations

import json

import pytest

from apex_engine import Confidence, Finding, FindingType, Severity
from apex_engine.crew import REJECTION_THRESHOLD, is_available, judge_candidates, merge_verdict
from apex_engine.crew.judge import build_crew

crewai = pytest.importorskip("crewai", reason="crew extra not installed")


# --- the ambiguous candidate the gate escalates ----------------------------

def ambiguous_candidate(**overrides) -> Finding:
    """A 7x skew: severe enough to matter, not confident enough to assert.

    This is exactly the band Tier 1 leaves to the crew — and note that no real
    job in the store currently produces one, which is the honest signal that
    the gate is tight rather than decorative.
    """
    payload = {
        "job_id": "job-ambiguous", "app_id": "app-1", "stage_id": 4,
        "type": FindingType.SKEW_ON_JOIN, "severity": Severity.CRITICAL,
        "evidence": "p99/p50 = 7.10x on stage 4 (p99=710ms, p50=100ms, 50 tasks)",
        "impact": "Long-tail tasks dominate the stage.",
        "fix": "Enable AQE skew join.",
        "confidence_score": 0.55, "detected_by": "skew_watcher",
        "details": {"skew_ratio": 7.1, "task_count": 50},
    }
    payload.update(overrides)
    return Finding(**payload)


class ScriptedLLM(crewai.llms.base_llm.BaseLLM):
    """A BaseLLM that returns pre-scripted JSON instead of calling Anthropic."""

    def __init__(self, model: str, replies: list[str]):
        super().__init__(model=model)
        self._replies = list(replies)
        self.calls: list[str] = []

    def call(self, messages, tools=None, callbacks=None, available_functions=None,
             from_task=None, from_agent=None, response_model=None):
        self.calls.append(str(messages)[:4000])
        return self._replies[min(len(self.calls) - 1, len(self._replies) - 1)]

    def supports_function_calling(self) -> bool:
        return False


def finding_json(**overrides) -> str:
    payload = {
        "job_id": "job-ambiguous", "app_id": "app-1", "stage_id": 4,
        "type": "SKEW_ON_JOIN", "severity": "critical",
        "evidence": "p99/p50 = 7.10x on stage 4 (p99=710ms, p50=100ms, 50 tasks)",
        "hot_key": "", "impact": "One partition holds a hot key.",
        "fix": "Salt the join key.", "confidence": "HIGH",
        "confidence_score": 0.87, "detected_by": "judger",
    }
    payload.update(overrides)
    return json.dumps(payload)


def scripted_crew_factory(replies: list[str], recorder: dict):
    """Build a real Crew whose two agents are backed by scripted LLMs."""

    def factory(candidate, store=None):
        crew = build_crew(candidate, store)
        llms = []
        for agent, reply in zip(crew.agents, replies):
            scripted = ScriptedLLM(agent.llm.model, [reply])
            agent.llm = scripted
            llms.append(scripted)
        recorder["llms"] = llms
        recorder["crew"] = crew
        return crew

    return factory


# --- T11: model tiering ----------------------------------------------------

def test_models_are_tiered_with_the_required_provider_prefix():
    """A bare model id will not resolve in CrewAI — the prefix is mandatory."""
    from apex_engine.config import CORRELATION_MODEL, JUDGE_MODEL, TRIAGE_MODEL

    assert TRIAGE_MODEL == "anthropic/claude-haiku-4-5"
    assert CORRELATION_MODEL == "anthropic/claude-sonnet-5"
    assert JUDGE_MODEL == "anthropic/claude-opus-4-8"
    for model in (TRIAGE_MODEL, CORRELATION_MODEL, JUDGE_MODEL):
        assert model.startswith("anthropic/")


def test_the_crew_assigns_the_cheaper_model_to_correlation_and_opus_to_the_judge():
    crew = build_crew(ambiguous_candidate())
    correlator, judger = crew.agents
    assert "sonnet" in correlator.llm.model
    assert "opus" in judger.llm.model
    assert judger.llm.temperature == 0.0  # the verdict must be deterministic


# --- T12: the wiring -------------------------------------------------------

def test_crew_is_sequential_correlate_then_judge_with_context():
    crew = build_crew(ambiguous_candidate())
    correlate_task, judge_task = crew.tasks

    assert crew.process is crewai.Process.sequential
    assert judge_task.context == [correlate_task]      # judge sees correlation
    assert correlate_task.output_pydantic is Finding    # the CLASS, never an instance
    assert judge_task.output_pydantic is Finding
    assert [a.allow_delegation for a in crew.agents] == [False, False]


def test_judged_verdict_flows_back_into_the_finding():
    recorder: dict = {}
    candidate = ambiguous_candidate()
    factory = scripted_crew_factory(
        [finding_json(), finding_json(confidence_score=0.87, fix="Salt the join key.")],
        recorder,
    )

    survivors, calls = judge_candidates([candidate], crew_factory=factory)

    assert calls == 2  # correlate + judge
    assert len(survivors) == 1
    judged = survivors[0]
    assert judged.confidence_score == pytest.approx(0.87)
    assert judged.confidence is Confidence.HIGH   # recalibrated up from LOW
    assert judged.fix == "Salt the join key."
    assert judged.detected_by == "skew_watcher+judger"
    assert judged.details["judged"] is True
    assert judged.details["tier1_confidence_score"] == pytest.approx(0.55)


def test_the_judge_can_kill_a_false_positive():
    recorder: dict = {}
    factory = scripted_crew_factory(
        [finding_json(), finding_json(confidence_score=0.05, confidence="LOW")],
        recorder,
    )
    survivors, calls = judge_candidates([ambiguous_candidate()], crew_factory=factory)

    assert survivors == []       # rejected, never shown to a user
    assert calls == 2            # but it did cost the two calls to find out


def test_measured_identity_and_evidence_survive_a_hallucinating_judge():
    """The model may claim anything; only its JUDGEMENT is allowed through."""
    recorder: dict = {}
    factory = scripted_crew_factory(
        [finding_json(), finding_json(
            job_id="attacker-job", stage_id=999, type="DRIVER_OOM",
            evidence="fabricated evidence the watcher never measured",
            confidence_score=0.9)],
        recorder,
    )
    candidate = ambiguous_candidate()
    survivors, _ = judge_candidates([candidate], crew_factory=factory)

    judged = survivors[0]
    assert judged.job_id == candidate.job_id
    assert judged.stage_id == candidate.stage_id
    assert judged.type is candidate.type
    assert judged.evidence == candidate.evidence
    assert judged.details["skew_ratio"] == 7.1  # the real measurement is intact


def test_a_crew_failure_keeps_the_measured_finding():
    """An outage must not silently delete something a SQL rule measured."""

    def exploding_factory(candidate, store=None):
        class Boom:
            def kickoff(self, inputs=None):
                raise RuntimeError("anthropic 529 overloaded")

        return Boom()

    survivors, calls = judge_candidates([ambiguous_candidate()], crew_factory=exploding_factory)

    assert len(survivors) == 1
    assert survivors[0].confidence_score == pytest.approx(0.55)  # unchanged Tier-1 value
    assert "anthropic 529" in survivors[0].details["crew_error"]
    assert calls == 0


def test_no_candidates_means_no_crew_and_no_calls():
    assert judge_candidates([]) == ([], 0)


# --- merge semantics -------------------------------------------------------

def test_merge_rejects_at_or_below_the_threshold_and_keeps_just_above():
    candidate = ambiguous_candidate()
    at_threshold = candidate.model_copy(update={"confidence_score": REJECTION_THRESHOLD})
    just_above = candidate.model_copy(update={"confidence_score": REJECTION_THRESHOLD + 0.01})

    assert merge_verdict(candidate, at_threshold) is None
    assert merge_verdict(candidate, just_above) is not None


def test_merge_falls_back_to_the_enum_when_the_model_omits_the_score():
    candidate = ambiguous_candidate()
    judged = Finding(
        job_id="j", stage_id=4, type=FindingType.SKEW_ON_JOIN, severity=Severity.CRITICAL,
        evidence="e", impact="i", fix="f", confidence=Confidence.HIGH, detected_by="judger",
    )
    merged = merge_verdict(candidate, judged)
    assert merged.confidence is Confidence.HIGH


# --- T13: the read-only tool ----------------------------------------------

def test_the_agent_tool_refuses_anything_outside_the_whitelist():
    from apex_engine.crew.tools import QUERIES, run_named_query

    result = run_named_query(None, "DROP TABLE apex.findings", "job-1")
    assert result["error"].startswith("unknown_query")
    assert set(result["allowed"]) == set(QUERIES)


def test_every_whitelisted_query_is_read_only_parameterized_and_bounded():
    from apex_engine.crew.tools import QUERIES

    for name, sql in QUERIES.items():
        upper = sql.upper()
        assert upper.strip().startswith("\n        SELECT") or "SELECT" in upper.split()[0:2]
        for forbidden in ("INSERT", "ALTER", "DROP", "DELETE", "TRUNCATE", "CREATE", "ATTACH"):
            assert forbidden not in upper, f"{name} is not read-only"
        assert "{job_id:String}" in sql, f"{name} interpolates instead of binding"
        assert "LIMIT {limit:Int32}" in sql, f"{name} is unbounded"


def test_the_correlator_gets_the_tool_only_when_a_store_exists():
    assert build_crew(ambiguous_candidate(), store=None).agents[0].tools == []


# --- availability ----------------------------------------------------------

def test_is_available_reports_a_missing_key_rather_than_raising(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    available, reason = is_available()
    assert available is False
    assert reason == "no_anthropic_api_key"
