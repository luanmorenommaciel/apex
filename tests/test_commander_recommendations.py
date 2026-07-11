from apex.commander.findings import build_finding
from apex.commander.recommendations import preview_recommendation, recommend_fix


class FakeFindingStore:
    def __init__(self, records):
        self.records = records

    def query_by_job_id(self, job_id):
        return self.records.get(job_id, [])


def accepted_skew_record():
    finding = build_finding(
        "shuffle_skew_candidate",
        "job-42",
        "warning",
        "medium",
        {
            "app_id": "app-recommend",
            "stage_id": 2,
            "ratio": 29.5,
            "hot_records": 165297,
            "median_cold_records": 5596,
            "task_count": 8,
        },
        ["Validar skew antes de aplicar mudanca."],
    )
    return {"finding": finding, "validation": {"status": "valid", "accepted": True}}


def test_recommend_fix_builds_deterministic_recommendation_from_persisted_finding():
    store = FakeFindingStore({"job-42": [accepted_skew_record()]})

    result = recommend_fix(store, "job-42")

    assert result["status"] == "found"
    assert result["count"] == 1
    assert result["recommendations"][0]["id"] == (
        "job-42:shuffle_skew_candidate:stage-2:0"
    )
    assert result["recommendations"][0]["action"] == (
        "validate_aqe_then_consider_salting_or_repartition"
    )
    assert result["recommendations"][0]["preview"]["requires_approval_before_apply"]


def test_recommend_fix_skips_unaccepted_validation():
    record = accepted_skew_record()
    record["validation"] = {"status": "invalid", "accepted": False}
    store = FakeFindingStore({"job-42": [record]})

    result = recommend_fix(store, "job-42")

    assert result["status"] == "no_recommendation"
    assert result["count"] == 0
    assert result["skipped_count"] == 1


def test_recommend_fix_without_store_is_not_configured():
    result = recommend_fix(None, "job-42")

    assert result["status"] == "not_configured"
    assert result["recommendations"] == []


def test_preview_recommendation_returns_diff_without_modifying_file(tmp_path):
    store = FakeFindingStore({"job-42": [accepted_skew_record()]})
    source = tmp_path / "job.py"
    source.write_text("df.join(dim, 'id').count()\n", encoding="utf-8")

    result = preview_recommendation(
        store,
        "job-42",
        "job-42:shuffle_skew_candidate:stage-2:0",
        source,
        "# REVIEW: validate skew mitigation before this join\ndf.join(dim, 'id').count()\n",
    )

    assert result["status"] == "preview_ready"
    assert result["requires_approval"] is True
    assert result["recommendation_id"] == "job-42:shuffle_skew_candidate:stage-2:0"
    assert "+# REVIEW: validate skew mitigation before this join" in result["diff"]
    assert source.read_text(encoding="utf-8") == "df.join(dim, 'id').count()\n"


def test_preview_recommendation_rejects_unknown_recommendation_without_file_read(tmp_path):
    store = FakeFindingStore({"job-42": [accepted_skew_record()]})
    missing_source = tmp_path / "missing.py"

    result = preview_recommendation(
        store,
        "job-42",
        "unknown-recommendation",
        missing_source,
        "replacement",
    )

    assert result["status"] == "recommendation_not_found"
    assert result["diff"] == ""
