from apex_engine import Confidence, Finding, FindingType, JudgeDecision, Severity, analyze_events, requires_judge

from test_contract_engine import clean_event


class FakeJudge:
    def __init__(self, decision: JudgeDecision) -> None:
        self.decision = decision
        self.calls = 0

    def judge(self, finding: Finding) -> JudgeDecision:
        self.calls += 1
        return self.decision


def candidate() -> Finding:
    return Finding(
        job_id="candidate-job", stage_id=3, type=FindingType.SKEW_ON_JOIN,
        severity=Severity.CRITICAL, confidence=Confidence.LOW,
        evidence="p99/p50=29.5x", impact="long tail", fix="enable AQE",
        detected_by="test", details={"p99_p50_ratio": 29.5, "task_count": 8},
    )


def test_gate_requires_only_low_confidence_high_severity_candidates():
    assert requires_judge(candidate()) is True
    assert requires_judge(candidate().model_copy(update={"confidence": Confidence.MEDIUM})) is False
    assert requires_judge(candidate().model_copy(update={"severity": Severity.WARNING})) is False


def test_ungated_deterministic_findings_never_call_judge():
    judge = FakeJudge(JudgeDecision(decision="confirm", rationale="unused", cited_evidence=["x"]))
    result = analyze_events([clean_event(task_duration_p50_ms=100, task_duration_p99_ms=2_000)], judge=judge)
    assert result["llm_calls"] == 0
    assert judge.calls == 0


def test_gated_judge_can_confirm_only_when_citing_existing_evidence(monkeypatch):
    from apex_engine import pipeline
    monkeypatch.setattr(pipeline, "run_all", lambda _: [candidate()])
    judge = FakeJudge(JudgeDecision(decision="confirm", rationale="ratio proves skew", cited_evidence=["p99/p50=29.5x"]))
    result = analyze_events([clean_event()], judge=judge)
    assert result["mode"] == "gated_crew"
    assert result["llm_calls"] == 1
    assert len(result["findings"]) == 1
    assert result["findings"][0].job_id == "candidate-job"
    assert result["findings"][0].evidence == "p99/p50=29.5x"


def test_gated_judge_rejection_is_audited_not_silently_dropped(monkeypatch):
    from apex_engine import pipeline
    monkeypatch.setattr(pipeline, "run_all", lambda _: [candidate()])
    judge = FakeJudge(JudgeDecision(decision="reject", rationale="insufficient", cited_evidence=["p99/p50=29.5x"]))
    result = analyze_events([clean_event()], judge=judge)
    assert result["findings"] == []
    assert result["rejected"][0]["reason"] == "judge_rejected_or_ungrounded"
