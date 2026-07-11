import json
from io import StringIO

from apex.commander.clickstack_mvp import append_envelope
from apex.commander.mcp_stdio_server import handle_jsonrpc_message, serve_stdio
from apex.commander.tool_contract import CommanderToolContract


class FakeFindingStore:
    def __init__(self, records):
        self.records = records

    def query_by_job_id(self, job_id):
        return self.records.get(job_id, [])


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
        "preview_fix",
    ]
    assert tools[0]["inputSchema"]["required"] == ["job_id"]
    assert tools[0]["annotations"] == {"readOnlyHint": True}


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
            "job-42": [
                {
                    "finding": {
                        "job_id": "job-42",
                        "kind": "shuffle_skew_candidate",
                    },
                    "validation": {"status": "valid", "accepted": True},
                }
            ]
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
