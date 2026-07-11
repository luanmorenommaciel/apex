import pytest

from apex.commander.clickstack_mvp import append_envelope
from apex.commander.tool_contract import CommanderToolContract, list_tools


class FakeFindingStore:
    def __init__(self, records):
        self.records = records

    def query_by_job_id(self, job_id):
        return self.records.get(job_id, [])


def test_list_tools_exposes_only_read_only_commander_tools():
    tools = list_tools()
    tool_names = [tool["name"] for tool in tools]

    assert tool_names == [
        "debug_job",
        "explain_evidence",
        "evaluate_negative_baseline",
        "query_persisted_findings",
        "recommend_fix",
        "preview_recommendation",
        "apply_recommendation",
        "verify_recommendation_apply",
        "compare_job_telemetry",
        "preview_fix",
    ]
    assert [tool["safety"] for tool in tools].count("guarded_mutation") == 1
    assert all(
        tool["safety"] == "read_only"
        for tool in tools
        if tool["name"] != "apply_recommendation"
    )
    assert "apply_fix" not in tool_names
    assert tools[0]["input_schema"]["required"] == ["job_id"]


def test_unknown_tool_is_rejected(tmp_path):
    contract = CommanderToolContract(tmp_path / "store.ndjson")

    with pytest.raises(ValueError, match="unknown_tool"):
        contract.call_tool("apply_fix", {"job_id": "job-42"})


def telemetry_envelope(job_id="job-42"):
    return {
        "schema_version": "apex.commander.telemetry.v1",
        "job_id": job_id,
        "app_id": "app-tool-contract",
        "event_counts": {"SparkListenerTaskEnd": 4},
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
                "disk_bytes_spilled": 0,
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


def healthy_telemetry_envelope(job_id="job-healthy"):
    envelope = telemetry_envelope(job_id)
    envelope["stages"][0].update(
        {
            "records": [1000, 1000, 1000, 1000],
            "total_records": 4000,
            "max_records": 1000,
            "median_cold_records": 1000,
            "ratio": 1.0,
        }
    )
    envelope["skew_candidates"] = []
    return envelope


def persisted_skew_record():
    return {
        "finding": {
            "job_id": "job-42",
            "kind": "shuffle_skew_candidate",
            "severity": "warning",
            "confidence": "medium",
            "evidence": {
                "app_id": "app-tool-contract",
                "stage_id": 2,
                "ratio": 29.5,
                "hot_records": 165297,
                "median_cold_records": 5596,
            },
        },
        "validation": {"status": "valid", "accepted": True},
    }


def test_call_tool_debug_job_returns_findings(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope())
    contract = CommanderToolContract(store)

    result = contract.call_tool("debug_job", {"job_id": "job-42"})

    assert result["job_id"] == "job-42"
    assert result["findings"][0]["kind"] == "shuffle_skew_candidate"


def test_call_tool_explain_evidence_returns_stages(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope())
    contract = CommanderToolContract(store)

    result = contract.call_tool("explain_evidence", {"job_id": "job-42"})

    assert result["status"] == "found"
    assert result["stages"][0]["stage_id"] == 2


def test_call_tool_evaluate_negative_baseline_returns_failed_for_skew(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope())
    contract = CommanderToolContract(store)

    result = contract.call_tool("evaluate_negative_baseline", {"job_id": "job-42"})

    assert result["status"] == "failed"
    assert result["unexpected_findings"][0]["kind"] == "shuffle_skew_candidate"


def test_call_tool_query_persisted_findings_returns_records(tmp_path):
    finding_store = FakeFindingStore(
        {
            "job-42": [persisted_skew_record()]
        }
    )
    contract = CommanderToolContract(
        tmp_path / "store.ndjson",
        finding_store=finding_store,
    )

    result = contract.call_tool("query_persisted_findings", {"job_id": "job-42"})

    assert result["status"] == "found"
    assert result["count"] == 1
    assert result["records"][0]["finding"]["kind"] == "shuffle_skew_candidate"


def test_call_tool_recommend_fix_returns_structured_recommendation(tmp_path):
    finding_store = FakeFindingStore({"job-42": [persisted_skew_record()]})
    contract = CommanderToolContract(
        tmp_path / "store.ndjson",
        finding_store=finding_store,
    )

    result = contract.call_tool("recommend_fix", {"job_id": "job-42"})

    assert result["status"] == "found"
    assert result["recommendations"][0]["id"] == (
        "job-42:shuffle_skew_candidate:stage-2:0"
    )
    assert result["recommendations"][0]["preview"]["tool"] == "preview_recommendation"


def test_call_tool_preview_recommendation_returns_diff_without_modifying_file(tmp_path):
    source = tmp_path / "job.py"
    source.write_text("df.join(dim, 'id').count()\n", encoding="utf-8")
    finding_store = FakeFindingStore({"job-42": [persisted_skew_record()]})
    contract = CommanderToolContract(
        tmp_path / "store.ndjson",
        finding_store=finding_store,
    )

    result = contract.call_tool(
        "preview_recommendation",
        {
            "job_id": "job-42",
            "recommendation_id": "job-42:shuffle_skew_candidate:stage-2:0",
            "path": str(source),
            "replacement": "# REVIEW: validate skew before this join\ndf.join(dim, 'id').count()\n",
        },
    )

    assert result["status"] == "preview_ready"
    assert result["requires_approval"] is True
    assert len(result["approval"]["token"]) == 64
    assert "+# REVIEW: validate skew before this join" in result["diff"]
    assert source.read_text(encoding="utf-8") == "df.join(dim, 'id').count()\n"


def test_call_tool_apply_recommendation_requires_apply_root(tmp_path):
    source = tmp_path / "job.py"
    source.write_text("df.join(dim, 'id').count()\n", encoding="utf-8")
    finding_store = FakeFindingStore({"job-42": [persisted_skew_record()]})
    contract = CommanderToolContract(
        tmp_path / "store.ndjson",
        finding_store=finding_store,
    )

    result = contract.call_tool(
        "apply_recommendation",
        {
            "job_id": "job-42",
            "recommendation_id": "job-42:shuffle_skew_candidate:stage-2:0",
            "path": str(source),
            "replacement": "# REVIEW: validate skew before this join\ndf.join(dim, 'id').count()\n",
            "approval_token": "token",
        },
    )

    assert result["status"] == "apply_root_not_configured"
    assert source.read_text(encoding="utf-8") == "df.join(dim, 'id').count()\n"


def test_call_tool_apply_recommendation_writes_with_matching_token(tmp_path):
    source = tmp_path / "job.py"
    replacement = "# REVIEW: validate skew before this join\ndf.join(dim, 'id').count()\n"
    source.write_text("df.join(dim, 'id').count()\n", encoding="utf-8")
    finding_store = FakeFindingStore({"job-42": [persisted_skew_record()]})
    contract = CommanderToolContract(
        tmp_path / "store.ndjson",
        finding_store=finding_store,
        apply_root=tmp_path,
    )
    preview = contract.call_tool(
        "preview_recommendation",
        {
            "job_id": "job-42",
            "recommendation_id": "job-42:shuffle_skew_candidate:stage-2:0",
            "path": str(source),
            "replacement": replacement,
        },
    )

    result = contract.call_tool(
        "apply_recommendation",
        {
            "job_id": "job-42",
            "recommendation_id": "job-42:shuffle_skew_candidate:stage-2:0",
            "path": str(source),
            "replacement": replacement,
            "approval_token": preview["approval"]["token"],
        },
    )

    assert result["status"] == "applied"
    assert result["verification"]["status"] == "verified"
    assert source.read_text(encoding="utf-8") == replacement


def test_call_tool_verify_recommendation_apply_returns_hash_status(tmp_path):
    source = tmp_path / "job.py"
    source.write_text("df.join(dim, 'id').count()\n", encoding="utf-8")
    contract = CommanderToolContract(tmp_path / "store.ndjson", apply_root=tmp_path)

    result = contract.call_tool(
        "verify_recommendation_apply",
        {"path": str(source), "expected_sha256": "0" * 64},
    )

    assert result["status"] == "mismatch"


def test_call_tool_compare_job_telemetry_returns_improved(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope("before-job"))
    append_envelope(store, healthy_telemetry_envelope("after-job"))
    contract = CommanderToolContract(store)

    result = contract.call_tool(
        "compare_job_telemetry",
        {"before_job_id": "before-job", "after_job_id": "after-job"},
    )

    assert result["status"] == "improved"
    assert result["before"]["finding_count"] == 1
    assert result["after"]["finding_count"] == 0


def test_call_tool_query_persisted_findings_without_store_is_not_configured(tmp_path):
    contract = CommanderToolContract(tmp_path / "store.ndjson")

    result = contract.call_tool("query_persisted_findings", {"job_id": "job-42"})

    assert result == {
        "job_id": "job-42",
        "status": "not_configured",
        "count": 0,
        "records": [],
    }


def test_call_tool_preview_fix_returns_diff_without_modifying_file(tmp_path):
    source = tmp_path / "job.py"
    source.write_text("df.join(dim, 'id').count()\n", encoding="utf-8")
    contract = CommanderToolContract(tmp_path / "store.ndjson")

    result = contract.call_tool(
        "preview_fix",
        {
            "path": str(source),
            "recommendation": "Add salting before the skewed join.",
            "replacement": "# REVIEW: Add salting before this join\ndf.join(dim, 'id').count()\n",
        },
    )

    assert result["mode"] == "preview"
    assert "+# REVIEW: Add salting before this join" in result["diff"]
    assert source.read_text(encoding="utf-8") == "df.join(dim, 'id').count()\n"


def test_call_tool_rejects_missing_required_argument(tmp_path):
    contract = CommanderToolContract(tmp_path / "store.ndjson")

    with pytest.raises(ValueError, match="missing_argument:job_id"):
        contract.call_tool("debug_job", {})
