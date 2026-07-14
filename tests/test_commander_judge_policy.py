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
