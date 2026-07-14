from apex.commander.judge_policy import confidence_score, evaluate_judge_policy


def base_finding(confidence="medium"):
    return {
        "job_id": "job-judge",
        "kind": "shuffle_skew_candidate",
        "confidence": confidence,
        "evidence": {"app_id": "app-judge", "stage_id": 2},
    }


def test_confidence_score_maps_commander_labels():
    assert confidence_score("none") == 0.0
    assert confidence_score("low") == 0.3
    assert confidence_score("medium") == 0.6
    assert confidence_score("high") == 0.85


def test_medium_confidence_stays_on_deterministic_t1_at_default_threshold():
    result = evaluate_judge_policy(base_finding("medium"))

    assert result["status"] == "keep_deterministic"
    assert result["route"] == "deterministic_t1"
    assert result["should_escalate"] is False
    assert result["confidence_score"] == 0.6


def test_low_confidence_escalates_to_future_crew_judge_contract():
    result = evaluate_judge_policy(base_finding("low"))

    assert result["status"] == "escalate"
    assert result["route"] == "crew_judge"
    assert result["should_escalate"] is True
    assert result["reasons"] == ["confidence_below_threshold"]
    assert result["future_contract"]["tool"] == "crew_judge_diagnose"
    assert result["future_contract"]["stage"] == "future_optional_after_evidence_validator"


def test_numeric_confidence_below_threshold_escalates():
    result = evaluate_judge_policy(base_finding(0.59))

    assert result["should_escalate"] is True
    assert result["confidence_score"] == 0.59


def test_validator_rejection_escalates_even_when_confidence_is_high():
    result = evaluate_judge_policy(
        base_finding("high"),
        validation={"status": "invalid", "accepted": False},
    )

    assert result["should_escalate"] is True
    assert result["reasons"] == ["evidence_validator_rejected"]


def test_future_contract_declares_required_inputs_outputs_and_judge_decisions():
    result = evaluate_judge_policy(base_finding("low"))
    contract = result["future_contract"]

    assert contract["required_inputs"] == [
        "job_id",
        "finding_kind",
        "confidence_score",
        "evidence",
        "validation",
    ]
    assert contract["must_return"] == [
        "decision",
        "rationale",
        "cited_evidence",
        "recommended_next_action",
        "human_review_required",
    ]
    assert contract["allowed_decisions"] == [
        "confirm_finding",
        "reject_finding",
        "request_more_evidence",
        "manual_review",
    ]


def test_future_contract_blocks_hallucinated_metrics_and_direct_apply():
    result = evaluate_judge_policy(base_finding("low"))

    assert result["future_contract"]["anti_hallucination_constraints"] == [
        "must_cite_existing_evidence",
        "must_not_invent_metrics",
        "must_not_invent_root_cause",
        "must_mark_unknown_when_evidence_is_missing",
        "must_not_apply_changes_directly",
    ]
