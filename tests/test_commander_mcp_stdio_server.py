import json
import subprocess
import sys
from io import StringIO

from apex.commander.clickstack_mvp import append_envelope
from apex.commander.mcp_stdio_server import handle_jsonrpc_message, serve_stdio
from apex.commander.tool_contract import CommanderToolContract


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


def contract(tmp_path):
    return CommanderToolContract(tmp_path / "store.ndjson")


def test_initialize_declares_read_only_tools_capability(tmp_path):
    response = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "pytest", "version": "1.0"},
            },
        },
        contract(tmp_path),
    )

    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 1
    assert response["result"]["protocolVersion"] == "2025-06-18"
    assert response["result"]["serverInfo"]["name"] == "apex-commander"
    assert response["result"]["capabilities"] == {"tools": {"listChanged": False}}


def test_tools_list_returns_mcp_tool_metadata(tmp_path):
    response = handle_jsonrpc_message(
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        contract(tmp_path),
    )

    tools = response["result"]["tools"]
    assert [tool["name"] for tool in tools] == [
        "debug_job",
        "explain_evidence",
        "evaluate_negative_baseline",
        "query_persisted_findings",
        "recommend_fix",
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
    assert tools[0]["inputSchema"]["required"] == ["job_id"]
    assert tools[0]["annotations"] == {"readOnlyHint": True}
    apply_tool = next(tool for tool in tools if tool["name"] == "apply_recommendation")
    assert apply_tool["annotations"]["readOnlyHint"] is False
    assert apply_tool["annotations"]["destructiveHint"] is True
    apply_fix_tool = next(tool for tool in tools if tool["name"] == "apply_fix")
    assert apply_fix_tool["annotations"]["readOnlyHint"] is False
    assert apply_fix_tool["annotations"]["destructiveHint"] is True
    rerun_tool = next(tool for tool in tools if tool["name"] == "execute_rerun_and_compare")
    assert rerun_tool["annotations"]["readOnlyHint"] is False
    assert rerun_tool["annotations"]["destructiveHint"] is True
    poll_rerun_tool = next(
        tool for tool in tools if tool["name"] == "execute_rerun_poll_and_compare"
    )
    assert poll_rerun_tool["annotations"]["readOnlyHint"] is False
    assert poll_rerun_tool["annotations"]["destructiveHint"] is True


def telemetry_envelope(job_id="job-42"):
    return {
        "schema_version": "apex.commander.telemetry.v1",
        "job_id": job_id,
        "app_id": "app-mcp-stdio",
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
                "app_id": "app-mcp-stdio",
                "stage_id": 2,
                "ratio": 29.5,
                "hot_records": 165297,
                "median_cold_records": 5596,
            },
        },
        "validation": {"status": "valid", "accepted": True},
    }


def test_tools_call_returns_text_json_content(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope())
    response = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "debug_job",
                "arguments": {"job_id": "job-42"},
            },
        },
        CommanderToolContract(store),
    )

    payload = json.loads(response["result"]["content"][0]["text"])
    assert payload["job_id"] == "job-42"
    assert payload["findings"][0]["kind"] == "shuffle_skew_candidate"


def test_tools_call_can_query_persisted_findings(tmp_path):
    finding_store = FakeFindingStore(
        {
            "job-42": [persisted_skew_record()]
        }
    )
    response = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "query_persisted_findings",
                "arguments": {"job_id": "job-42"},
            },
        },
        CommanderToolContract(tmp_path / "store.ndjson", finding_store=finding_store),
    )

    payload = json.loads(response["result"]["content"][0]["text"])
    assert payload["status"] == "found"
    assert payload["records"][0]["validation"]["accepted"] is True


def test_tools_call_can_recommend_fix_from_persisted_findings(tmp_path):
    finding_store = FakeFindingStore({"job-42": [persisted_skew_record()]})
    response = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "recommend_fix",
                "arguments": {"job_id": "job-42"},
            },
        },
        CommanderToolContract(tmp_path / "store.ndjson", finding_store=finding_store),
    )

    payload = json.loads(response["result"]["content"][0]["text"])
    assert payload["status"] == "found"
    assert payload["recommendations"][0]["preview"]["tool"] == "preview_recommendation"


def test_tools_call_can_preview_recommendation_without_modifying_file(tmp_path):
    source = tmp_path / "job.py"
    source.write_text("df.join(dim, 'id').count()\n", encoding="utf-8")
    finding_store = FakeFindingStore({"job-42": [persisted_skew_record()]})
    response = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "preview_recommendation",
                "arguments": {
                    "job_id": "job-42",
                    "recommendation_id": "job-42:shuffle_skew_candidate:stage-2:0",
                    "path": str(source),
                    "replacement": (
                        "# REVIEW: validate skew before this join\n"
                        "df.join(dim, 'id').count()\n"
                    ),
                },
            },
        },
        CommanderToolContract(tmp_path / "store.ndjson", finding_store=finding_store),
    )

    payload = json.loads(response["result"]["content"][0]["text"])
    assert payload["status"] == "preview_ready"
    assert len(payload["approval"]["token"]) == 64
    assert "+# REVIEW: validate skew before this join" in payload["diff"]
    assert source.read_text(encoding="utf-8") == "df.join(dim, 'id').count()\n"


def test_tools_call_can_apply_recommendation_with_matching_token(tmp_path):
    source = tmp_path / "job.py"
    replacement = "# REVIEW: validate skew before this join\ndf.join(dim, 'id').count()\n"
    source.write_text("df.join(dim, 'id').count()\n", encoding="utf-8")
    finding_store = FakeFindingStore({"job-42": [persisted_skew_record()]})
    contract = CommanderToolContract(
        tmp_path / "store.ndjson",
        finding_store=finding_store,
        apply_root=tmp_path,
    )
    preview_response = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "preview_recommendation",
                "arguments": {
                    "job_id": "job-42",
                    "recommendation_id": "job-42:shuffle_skew_candidate:stage-2:0",
                    "path": str(source),
                    "replacement": replacement,
                },
            },
        },
        contract,
    )
    preview = json.loads(preview_response["result"]["content"][0]["text"])

    apply_response = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "apply_recommendation",
                "arguments": {
                    "job_id": "job-42",
                    "recommendation_id": "job-42:shuffle_skew_candidate:stage-2:0",
                    "path": str(source),
                    "replacement": replacement,
                    "approval_token": preview["approval"]["token"],
                },
            },
        },
        contract,
    )

    payload = json.loads(apply_response["result"]["content"][0]["text"])
    assert payload["status"] == "applied"
    assert payload["verification"]["status"] == "verified"
    assert source.read_text(encoding="utf-8") == replacement


def test_tools_call_can_apply_fix_with_matching_token(tmp_path):
    source = tmp_path / "job.py"
    replacement = "# REVIEW: validate skew before this join\ndf.join(dim, 'id').count()\n"
    source.write_text("df.join(dim, 'id').count()\n", encoding="utf-8")
    finding_store = FakeFindingStore({"job-42": [persisted_skew_record()]})
    contract = CommanderToolContract(
        tmp_path / "store.ndjson",
        finding_store=finding_store,
        apply_root=tmp_path,
    )
    preview_response = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 80,
            "method": "tools/call",
            "params": {
                "name": "preview_recommendation",
                "arguments": {
                    "job_id": "job-42",
                    "recommendation_id": "job-42:shuffle_skew_candidate:stage-2:0",
                    "path": str(source),
                    "replacement": replacement,
                },
            },
        },
        contract,
    )
    preview = json.loads(preview_response["result"]["content"][0]["text"])

    apply_response = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 81,
            "method": "tools/call",
            "params": {
                "name": "apply_fix",
                "arguments": {
                    "job_id": "job-42",
                    "recommendation_id": "job-42:shuffle_skew_candidate:stage-2:0",
                    "path": str(source),
                    "replacement": replacement,
                    "approval_token": preview["approval"]["token"],
                },
            },
        },
        contract,
    )

    payload = json.loads(apply_response["result"]["content"][0]["text"])
    assert payload["status"] == "applied"
    assert payload["mode"] == "guarded_apply"
    assert payload["verification"]["status"] == "verified"
    assert source.read_text(encoding="utf-8") == replacement


def test_tools_call_can_compare_job_telemetry(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope("before-job"))
    append_envelope(store, healthy_telemetry_envelope("after-job"))
    response = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {
                "name": "compare_job_telemetry",
                "arguments": {
                    "before_job_id": "before-job",
                    "after_job_id": "after-job",
                },
            },
        },
        CommanderToolContract(store),
    )

    payload = json.loads(response["result"]["content"][0]["text"])
    assert payload["status"] == "improved"
    assert payload["summary"]["resolved_findings"] == ["shuffle_skew_candidate"]


def test_tools_call_can_build_spark_submit_rerun_command(tmp_path):
    source = tmp_path / "job.py"
    source.write_text("print('spark job')\n", encoding="utf-8")
    response = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {
                "name": "build_spark_submit_rerun_command",
                "arguments": {
                    "app_path": "job.py",
                    "after_job_id": "after-job",
                },
            },
        },
        CommanderToolContract(tmp_path / "store.ndjson", rerun_root=tmp_path),
    )

    payload = json.loads(response["result"]["content"][0]["text"])
    assert payload["status"] == "planned"
    assert payload["command"][0] == "spark-submit"
    assert "--jars" in payload["command"]
    assert (
        "listener-jvm/build/libs/apex-spark-listener-0.1.0.jar"
        in payload["command"]
    )
    assert "spark.apex.jobId=after-job" in payload["command"]
    assert "spark.apex.listener.output=/tmp/apex-listener-events.ndjson" in payload[
        "command"
    ]
    assert payload["command"][-1] == str(source.resolve())


def test_tools_call_can_plan_and_execute_rerun_with_fake_runner(tmp_path):
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
    plan_response = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {
                "name": "plan_rerun",
                "arguments": {
                    "before_job_id": "before-job",
                    "after_job_id": "after-job",
                    "command": ["spark-submit", "job.py"],
                },
            },
        },
        contract,
    )
    plan = json.loads(plan_response["result"]["content"][0]["text"])

    execute_response = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 12,
            "method": "tools/call",
            "params": {
                "name": "execute_rerun_and_compare",
                "arguments": {
                    "before_job_id": "before-job",
                    "after_job_id": "after-job",
                    "command": ["spark-submit", "job.py"],
                    "approval_token": plan["approval"]["token"],
                },
            },
        },
        contract,
    )

    payload = json.loads(execute_response["result"]["content"][0]["text"])
    assert payload["status"] == "rerun_completed"
    assert payload["comparison"]["status"] == "improved"
    assert runner.calls[0]["command"] == ["spark-submit", "job.py"]


def test_tools_call_can_execute_rerun_poll_and_compare(tmp_path):
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
    plan_response = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 13,
            "method": "tools/call",
            "params": {
                "name": "plan_rerun",
                "arguments": {
                    "before_job_id": "before-job",
                    "after_job_id": "after-job",
                    "command": ["spark-submit", "job.py"],
                },
            },
        },
        contract,
    )
    plan = json.loads(plan_response["result"]["content"][0]["text"])

    execute_response = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 14,
            "method": "tools/call",
            "params": {
                "name": "execute_rerun_poll_and_compare",
                "arguments": {
                    "before_job_id": "before-job",
                    "after_job_id": "after-job",
                    "command": ["spark-submit", "job.py"],
                    "approval_token": plan["approval"]["token"],
                    "poll_attempts": 3,
                    "poll_interval_seconds": 0.1,
                },
            },
        },
        contract,
    )

    payload = json.loads(execute_response["result"]["content"][0]["text"])
    assert payload["status"] == "rerun_completed"
    assert payload["telemetry"]["status"] == "found"
    assert payload["comparison"]["status"] == "improved"
    assert runner.calls[0]["command"] == ["spark-submit", "job.py"]


def test_initialized_notification_returns_no_response(tmp_path):
    response = handle_jsonrpc_message(
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        contract(tmp_path),
    )

    assert response is None


def test_unknown_method_returns_jsonrpc_error(tmp_path):
    response = handle_jsonrpc_message(
        {"jsonrpc": "2.0", "id": 9, "method": "unknown/method"},
        contract(tmp_path),
    )

    assert response["error"]["code"] == -32601
    assert response["error"]["message"] == "method_not_found:unknown/method"


def test_stdio_loop_processes_line_delimited_jsonrpc(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope())
    stdin = StringIO(
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        + "\n"
        + json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        + "\n"
        + json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "debug_job", "arguments": {"job_id": "job-42"}},
            }
        )
        + "\n"
    )
    stdout = StringIO()

    serve_stdio(CommanderToolContract(store), stdin=stdin, stdout=stdout)

    responses = [json.loads(line) for line in stdout.getvalue().splitlines()]
    assert [response["id"] for response in responses] == [1, 2, 3]
    payload = json.loads(responses[2]["result"]["content"][0]["text"])
    assert payload["findings"][0]["kind"] == "shuffle_skew_candidate"


def test_mcp_stdio_cli_subprocess_can_apply_fix(tmp_path):
    source = tmp_path / "job.py"
    replacement = "# REVIEW: validate skew before this join\ndf.join(dim, 'id').count()\n"
    source.write_text("df.join(dim, 'id').count()\n", encoding="utf-8")
    finding_store = tmp_path / "findings.ndjson"
    finding_store.write_text(json.dumps(persisted_skew_record()) + "\n", encoding="utf-8")
    store = tmp_path / "store.ndjson"

    preview_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "preview_recommendation",
            "arguments": {
                "job_id": "job-42",
                "recommendation_id": "job-42:shuffle_skew_candidate:stage-2:0",
                "path": str(source),
                "replacement": replacement,
            },
        },
    }
    process = subprocess.run(
        [
            sys.executable,
            "-m",
            "apex.commander.mcp_stdio_cli",
            "--store",
            str(store),
            "--finding-store",
            str(finding_store),
            "--apply-root",
            str(tmp_path),
        ],
        input="\n".join(
            [
                json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"}),
                json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
                json.dumps(preview_request),
            ]
        )
        + "\n",
        capture_output=True,
        text=True,
        check=True,
    )
    responses = [json.loads(line) for line in process.stdout.splitlines()]
    tools = responses[1]["result"]["tools"]
    assert "apply_fix" in [tool["name"] for tool in tools]
    preview = json.loads(responses[2]["result"]["content"][0]["text"])

    apply_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "apply_fix",
            "arguments": {
                "job_id": "job-42",
                "recommendation_id": "job-42:shuffle_skew_candidate:stage-2:0",
                "path": str(source),
                "replacement": replacement,
                "approval_token": preview["approval"]["token"],
            },
        },
    }
    process = subprocess.run(
        [
            sys.executable,
            "-m",
            "apex.commander.mcp_stdio_cli",
            "--store",
            str(store),
            "--finding-store",
            str(finding_store),
            "--apply-root",
            str(tmp_path),
        ],
        input=json.dumps(apply_request) + "\n",
        capture_output=True,
        text=True,
        check=True,
    )
    apply_response = json.loads(process.stdout)
    payload = json.loads(apply_response["result"]["content"][0]["text"])
    assert payload["status"] == "applied"
    assert payload["verification"]["status"] == "verified"
    assert source.read_text(encoding="utf-8") == replacement
