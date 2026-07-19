import os

from apex.commander.crew_judge import crew_judge_diagnose
from apex.commander.judge_contract import (
    build_judge_envelope,
    normalize_judge_decision,
    validate_judge_decision,
)
from apex.commander.judge_providers import (
    CrewAIJudgeProvider,
    DeterministicJudgeProvider,
    NoopJudgeProvider,
)
from apex.commander.clickstack_mvp import append_envelope


class FakeFindingStore:
    def __init__(self, records):
        self.records = records

    def query_by_job_id(self, job_id):
        return self.records.get(job_id, [])


def telemetry_envelope(job_id="job-judge"):
    return {
        "schema_version": "apex.commander.telemetry.v1",
        "job_id": job_id,
        "app_id": "app-judge",
        "event_counts": {"SparkListenerTaskEnd": 4},
        "stages": [
            {
                "stage_id": 2,
                "task_count": 8,
                "records": [165297, 5596, 5600, 5700],
                "ratio": 29.5,
                "evidence_status": "valid",
                "quality_issues": [],
            }
        ],
        "skew_candidates": [
            {
                "kind": "shuffle_skew_candidate",
                "stage_id": 2,
                "ratio": 29.5,
                "hot_records": 165297,
                "median_cold_records": 5596,
                "task_count": 8,
            }
        ],
    }


def persisted_record(confidence="medium", accepted=True):
    return {
        "finding": {
            "job_id": "job-judge",
            "kind": "shuffle_skew_candidate",
            "severity": "warning",
            "confidence": confidence,
            "evidence": {
                "app_id": "app-judge",
                "stage_id": 2,
                "ratio": 29.5,
                "hot_records": 165297,
                "median_cold_records": 5596,
            },
        },
        "validation": {"status": "valid" if accepted else "invalid", "accepted": accepted},
    }


def envelope(confidence="medium", accepted=True):
    record = persisted_record(confidence, accepted)
    return build_judge_envelope(
        job_id="job-judge",
        finding=record["finding"],
        validation=record["validation"],
        policy={"should_escalate": confidence == "low", "reasons": []},
        evidence={"app_id": "app-judge", "event_counts": {"SparkListenerTaskEnd": 4}},
        candidate_recommendations=[],
    )


def test_deterministic_provider_confirms_valid_medium_confidence_finding():
    result = DeterministicJudgeProvider().diagnose(envelope())

    assert result["provider"] == "deterministic"
    assert result["decision"] == "confirm_finding"
    assert result["recommended_next_action"] == "recommend_fix"
    assert result["human_review_required"] is False
    assert result["cited_evidence"]


def test_deterministic_provider_requests_more_evidence_when_validator_rejects():
    result = DeterministicJudgeProvider().diagnose(envelope(accepted=False))

    assert result["decision"] == "request_more_evidence"
    assert result["recommended_next_action"] == "request_more_evidence"
    assert result["human_review_required"] is True


def test_noop_provider_is_explicit_not_configured():
    result = NoopJudgeProvider("test_reason").diagnose(envelope())

    assert result["status"] == "not_configured"
    assert result["provider"] == "noop"
    assert result["decision"] == "manual_review"
    assert "test_reason" in result["rationale"]


def test_crew_ai_provider_without_enable_flag_degrades_safely(monkeypatch):
    monkeypatch.delenv("APEX_CREW_JUDGE_ENABLED", raising=False)

    result = CrewAIJudgeProvider().diagnose(envelope())

    assert result["status"] == "not_configured"
    assert result["provider"] == "noop"
    assert "APEX_CREW_JUDGE_ENABLED_not_1" in result["rationale"]


def test_crew_ai_provider_with_enable_flag_but_no_credentials_degrades_safely(
    monkeypatch,
):
    monkeypatch.setenv("APEX_CREW_JUDGE_ENABLED", "1")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    result = CrewAIJudgeProvider().diagnose(envelope())

    assert result["status"] == "not_configured"
    assert result["provider"] == "noop"
    assert "llm_credentials_missing" in result["rationale"]


def test_contract_rejects_hallucinated_citation_and_direct_apply():
    env = envelope()
    decision = normalize_judge_decision(
        {
            "decision": "confirm_finding",
            "rationale": "invented metric",
            "cited_evidence": ["finding.evidence.fake_metric=999"],
            "recommended_next_action": "apply_fix",
            "human_review_required": False,
        },
        provider="deterministic",
        envelope=env,
    )
    validation = validate_judge_decision(decision, env)

    assert decision["decision"] == "manual_review"
    assert validation["accepted"] is False
    assert "missing_cited_evidence" in validation["issues"]


def test_crew_judge_diagnose_tool_returns_read_only_contract(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope())
    finding_store = FakeFindingStore({"job-judge": [persisted_record()]})

    result = crew_judge_diagnose(
        store,
        finding_store,
        "job-judge",
        provider="deterministic",
    )

    assert result["rule_set"] == "apex.commander.crew_judge.v1"
    assert result["provider_used"] == "deterministic"
    assert result["decision"]["decision"] == "confirm_finding"
    assert result["contract_validation"]["accepted"] is True
    assert result["read_only"] is True
    assert result["mutation_allowed"] is False
