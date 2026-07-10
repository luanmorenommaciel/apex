from apex.commander.clickstack_mvp import append_envelope
from apex.commander.mcp_contract import debug_job, explain_evidence


def telemetry_envelope():
    return {
        "schema_version": "apex.commander.telemetry.v1",
        "job_id": "job-42",
        "app_id": "app-skew",
        "event_counts": {"SparkListenerTaskEnd": 8},
        "stages": [
            {
                "stage_id": 2,
                "task_count": 8,
                "records": [165297, 5596, 5600, 5700],
                "total_records": 182193,
                "max_records": 165297,
                "median_cold_records": 5596,
                "ratio": 29.5,
                "evidence_status": "valid",
                "quality_issues": [],
                "disk_bytes_spilled": 2 * 1024 * 1024,
                "memory_bytes_spilled": 0,
                "jvm_gc_time_ms": 0,
                "executor_run_time_ms": 10000,
                "failure_reasons": [],
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


def test_debug_job_returns_validated_finding(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope())

    result = debug_job(store, "job-42")

    assert result["job_id"] == "job-42"
    assert result["finding"]["title"] == "shuffle_skew_candidate"
    assert result["validation"]["accepted"] is True
    assert result["validation"]["status"] == "valid"
    assert [item["kind"] for item in result["findings"]] == [
        "shuffle_skew_candidate",
        "shuffle_spill_candidate",
    ]


def test_debug_job_reports_not_found(tmp_path):
    result = debug_job(tmp_path / "missing.ndjson", "missing-job")

    assert result["job_id"] == "missing-job"
    assert result["finding"]["status"] == "not_found"
    assert result["validation"]["accepted"] is False


def test_explain_evidence_returns_latest_envelope(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope())

    result = explain_evidence(store, "job-42")

    assert result["status"] == "found"
    assert result["job_id"] == "job-42"
    assert result["stages"][0]["stage_id"] == 2
    assert result["skew_candidates"][0]["ratio"] == 29.5
