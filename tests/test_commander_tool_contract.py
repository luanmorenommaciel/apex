import pytest

from apex.commander.clickstack_mvp import append_envelope
from apex.commander.tool_contract import CommanderToolContract, list_tools


class FakeFindingStore:
    def __init__(self, records):
        self.records = records

    def query_by_job_id(self, job_id):
        return self.records.get(job_id, [])


class FakeRerunRunner:
    def __init__(self, on_run=None):
        self.calls = []
        self.on_run = on_run

    def run(self, command, cwd, timeout_seconds):
        self.calls.append(
            {
                "command": command,
                "cwd": str(cwd),
                "timeout_seconds": timeout_seconds,
            }
        )
        if self.on_run:
            self.on_run()
        return {
            "status": "succeeded",
            "exit_code": 0,
            "timed_out": False,
            "stdout": "ok",
            "stderr": "",
        }


def test_list_tools_exposes_only_read_only_commander_tools():
    tools = list_tools()
    tool_names = [tool["name"] for tool in tools]

    assert tool_names == [
        "debug_job",
        "explain_evidence",
        "evaluate_negative_baseline",
        "query_persisted_findings",
        "recommend_fix",
        "crew_judge_diagnose",
        "preview_recommendation",
        "apply_recommendation",
        "apply_fix",
        "verify_recommendation_apply",
        "compare_job_telemetry",
        "build_spark_submit_rerun_command",
        "poll_telemetry",
        "plan_rerun",
        "execute_rerun_and_compare",
        "execute_rerun_poll_and_compare",
        "preview_fix",
    ]
    assert [tool["safety"] for tool in tools].count("guarded_mutation") == 4
    assert all(
        tool["safety"] == "read_only"
        for tool in tools
        if tool["name"]
        not in (
            "apply_recommendation",
            "apply_fix",
            "execute_rerun_and_compare",
            "execute_rerun_poll_and_compare",
        )
    )
    assert tools[0]["input_schema"]["required"] == ["job_id"]


def test_unknown_tool_is_rejected(tmp_path):
    contract = CommanderToolContract(tmp_path / "store.ndjson")

    with pytest.raises(ValueError, match="unknown_tool"):
        contract.call_tool("not_a_tool", {"job_id": "job-42"})


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


def test_call_tool_crew_judge_diagnose_returns_read_only_decision(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope())
    finding_store = FakeFindingStore({"job-42": [persisted_skew_record()]})
    contract = CommanderToolContract(store, finding_store=finding_store)

    result = contract.call_tool(
        "crew_judge_diagnose",
        {"job_id": "job-42", "provider": "deterministic"},
    )

    assert result["status"] == "judged"
    assert result["provider_used"] == "deterministic"
    assert result["read_only"] is True
    assert result["mutation_allowed"] is False
    assert result["decision"]["decision"] == "confirm_finding"
    assert result["decision"]["recommended_next_action"] == "recommend_fix"
    assert result["contract_validation"]["accepted"] is True


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


def test_call_tool_build_spark_submit_rerun_command_returns_command(tmp_path):
    source = tmp_path / "job.py"
    source.write_text("print('spark job')\n", encoding="utf-8")
    contract = CommanderToolContract(
        tmp_path / "store.ndjson",
        rerun_root=tmp_path,
    )

    result = contract.call_tool(
        "build_spark_submit_rerun_command",
        {
            "app_path": "job.py",
            "after_job_id": "after-job",
            "conf": {"spark.sql.adaptive.enabled": "true"},
        },
    )

    assert result["status"] == "planned"
    assert result["command"][0] == "spark-submit"
    assert "--jars" in result["command"]
    assert (
        "listener-jvm/build/libs/apex-spark-listener-0.1.0.jar"
        in result["command"]
    )
    assert "spark.apex.jobId=after-job" in result["command"]
    assert "spark.apex.listener.output=/tmp/apex-listener-events.ndjson" in result[
        "command"
    ]
    assert "spark.sql.adaptive.enabled=true" in result["command"]
    assert result["command"][-1] == str(source.resolve())


def test_call_tool_poll_telemetry_returns_found(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, healthy_telemetry_envelope("after-job"))
    contract = CommanderToolContract(store)

    result = contract.call_tool(
        "poll_telemetry",
        {"job_id": "after-job", "attempts": 1, "interval_seconds": 0},
    )

    assert result["status"] == "found"
    assert result["envelope_count"] == 1


def test_call_tool_plan_rerun_returns_approval_token(tmp_path):
    contract = CommanderToolContract(
        tmp_path / "store.ndjson",
        rerun_root=tmp_path,
        rerun_allowed_command_prefixes=[["spark-submit"]],
    )

    result = contract.call_tool(
        "plan_rerun",
        {
            "before_job_id": "before-job",
            "after_job_id": "after-job",
            "command": ["spark-submit", "job.py"],
        },
    )

    assert result["status"] == "planned"
    assert len(result["approval"]["token"]) == 64


def test_call_tool_execute_rerun_and_compare_runs_fake_runner(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope("before-job"))

    def collect_after_telemetry():
        append_envelope(store, healthy_telemetry_envelope("after-job"))

    runner = FakeRerunRunner(on_run=collect_after_telemetry)
    contract = CommanderToolContract(
        store,
        rerun_root=tmp_path,
        rerun_allowed_command_prefixes=[["spark-submit"]],
        rerun_runner=runner,
    )
    plan = contract.call_tool(
        "plan_rerun",
        {
            "before_job_id": "before-job",
            "after_job_id": "after-job",
            "command": ["spark-submit", "job.py"],
        },
    )

    result = contract.call_tool(
        "execute_rerun_and_compare",
        {
            "before_job_id": "before-job",
            "after_job_id": "after-job",
            "command": ["spark-submit", "job.py"],
            "approval_token": plan["approval"]["token"],
        },
    )

    assert result["status"] == "rerun_completed"
    assert result["comparison"]["status"] == "improved"
    assert runner.calls[0]["command"] == ["spark-submit", "job.py"]


def test_call_tool_execute_rerun_poll_and_compare_waits_for_telemetry(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope("before-job"))

    def collect_after_telemetry(interval_seconds):
        assert interval_seconds == 0.1
        append_envelope(store, healthy_telemetry_envelope("after-job"))

    runner = FakeRerunRunner()
    contract = CommanderToolContract(
        store,
        rerun_root=tmp_path,
        rerun_allowed_command_prefixes=[["spark-submit"]],
        rerun_runner=runner,
        telemetry_poll_sleeper=collect_after_telemetry,
    )
    plan = contract.call_tool(
        "plan_rerun",
        {
            "before_job_id": "before-job",
            "after_job_id": "after-job",
            "command": ["spark-submit", "job.py"],
        },
    )

    result = contract.call_tool(
        "execute_rerun_poll_and_compare",
        {
            "before_job_id": "before-job",
            "after_job_id": "after-job",
            "command": ["spark-submit", "job.py"],
            "approval_token": plan["approval"]["token"],
            "poll_attempts": 3,
            "poll_interval_seconds": 0.1,
        },
    )

    assert result["status"] == "rerun_completed"
    assert result["telemetry"]["status"] == "found"
    assert result["comparison"]["status"] == "improved"
    assert runner.calls[0]["command"] == ["spark-submit", "job.py"]


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
