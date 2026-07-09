from apex.commander.evidence_validator import validate_finding


def valid_skew_finding():
    return {
        "status": "finding",
        "title": "shuffle_skew_candidate",
        "confidence": "medium",
        "job_id": "job-42",
        "evidence": {
            "schema_version": "apex.commander.telemetry.v1",
            "app_id": "app-skew",
            "stage_id": 2,
            "ratio": 29.5,
            "hot_records": 165297,
            "median_cold_records": 5596,
            "task_count": 8,
        },
        "recommendations": [
            "Validar habilitacao de spark.sql.adaptive.skewJoin.enabled para este job."
        ],
    }


def test_accepts_complete_skew_finding():
    result = validate_finding(valid_skew_finding())
    assert result["status"] == "valid"
    assert result["accepted"] is True
    assert result["issues"] == []


def test_rejects_missing_job_id():
    finding = valid_skew_finding()
    finding.pop("job_id")
    result = validate_finding(finding)
    assert result["status"] == "invalid"
    assert "missing_job_id" in result["issues"]


def test_rejects_low_ratio_false_positive():
    finding = valid_skew_finding()
    finding["evidence"]["ratio"] = 2.0
    result = validate_finding(finding)
    assert result["status"] == "invalid"
    assert "skew_ratio_below_threshold" in result["issues"]


def test_rejects_insufficient_task_count():
    finding = valid_skew_finding()
    finding["evidence"]["task_count"] = 1
    result = validate_finding(finding)
    assert result["status"] == "invalid"
    assert "insufficient_task_count" in result["issues"]
