# Codex Gate 6 MCP Stdio Local Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wrap the local Commander tool contract in a read-only MCP-compatible JSON-RPC stdio server.

**Architecture:** Gate 6 adds a small stdio JSON-RPC layer over `CommanderToolContract`. It supports the MCP lifecycle/tool subset needed locally: `initialize`, `notifications/initialized`, `tools/list`, and `tools/call`; it does not use network, SDK dependencies, `apply_fix`, or remote publication.

**Tech Stack:** Python standard library, existing `apex.commander` modules, pytest, NDJSON local store.

---

## Branch Rule

All work happens only on:

```text
gustocezar/feature/codex-desacoplamento-geradores
```

Forbidden:

- pushing to GitHub;
- editing Spike, Cowork, Kimi, DataFlint, or evaluated remote branches;
- adding a real MCP package dependency;
- opening network sockets;
- implementing or exposing `apply_fix`;
- mutating target files through MCP.

## File Structure

- Create: `apex/commander/mcp_stdio_server.py` for JSON-RPC/MCP request handling and stdio serving.
- Create: `tests/test_commander_mcp_stdio_server.py` for MCP lifecycle, tool listing, tool call, notification, and error tests.
- Modify: `docs/playbooks/commander-v01-local.md` to document Gate 6.
- Modify: `docs/architecture/llm-solution-validation-framework-2026-07-09.md` to update Gate 6 status.

## Task 1: Add MCP Initialize And Tool Discovery

**Files:**
- Create: `tests/test_commander_mcp_stdio_server.py`
- Create: `apex/commander/mcp_stdio_server.py`

- [ ] **Step 1: Write failing tests for initialize and tools/list**

Create `tests/test_commander_mcp_stdio_server.py`:

```python
from apex.commander.mcp_stdio_server import handle_jsonrpc_message
from apex.commander.tool_contract import CommanderToolContract


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
        "preview_fix",
    ]
    assert tools[0]["inputSchema"]["required"] == ["job_id"]
    assert tools[0]["annotations"] == {"readOnlyHint": True}
```

- [ ] **Step 2: Run RED**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_mcp_stdio_server.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'apex.commander.mcp_stdio_server'
```

- [ ] **Step 3: Implement initialize and tools/list**

Create `apex/commander/mcp_stdio_server.py`:

```python
"""Minimal read-only MCP stdio server for Commander."""

PROTOCOL_VERSION = "2025-06-18"
SERVER_INFO = {"name": "apex-commander", "version": "0.1.0"}

from copy import deepcopy

from apex.commander.tool_contract import list_tools


def handle_jsonrpc_message(message, contract):
    method = message.get("method")
    request_id = message.get("id")
    try:
        if method == "initialize":
            return _result(
                request_id,
                {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": SERVER_INFO,
                },
            )
        if method == "notifications/initialized":
            return None
        if method == "tools/list":
            return _result(request_id, {"tools": _mcp_tools()})
        return _error(request_id, -32601, f"method_not_found:{method}")
    except ValueError as exc:
        return _error(request_id, -32602, str(exc))


def _mcp_tools():
    tools = []
    for spec in list_tools():
        tools.append(
            {
                "name": spec["name"],
                "title": spec["name"],
                "description": spec["description"],
                "inputSchema": deepcopy(spec["input_schema"]),
                "annotations": {"readOnlyHint": spec["safety"] == "read_only"},
            }
        )
    return tools


def _result(request_id, result):
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id, code, message):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }
```

- [ ] **Step 4: Run GREEN**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_mcp_stdio_server.py -q
```

Expected:

```text
2 passed
```

## Task 2: Add MCP Tool Call

**Files:**
- Modify: `tests/test_commander_mcp_stdio_server.py`
- Modify: `apex/commander/mcp_stdio_server.py`

- [ ] **Step 1: Add failing tools/call test**

Append to `tests/test_commander_mcp_stdio_server.py`:

```python
import json

from apex.commander.clickstack_mvp import append_envelope


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
```

- [ ] **Step 2: Run RED**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_mcp_stdio_server.py::test_tools_call_returns_text_json_content -q
```

Expected: fail with method not found for `tools/call`.

- [ ] **Step 3: Implement tools/call**

Modify `apex/commander/mcp_stdio_server.py`:

```python
import json
```

Inside `handle_jsonrpc_message`, before method not found:

```python
        if method == "tools/call":
            params = message.get("params") or {}
            payload = contract.call_tool(
                _required(params, "name"),
                params.get("arguments") or {},
            )
            return _result(request_id, _tool_result(payload))
```

Add helpers:

```python
def _tool_result(payload):
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(payload, sort_keys=True),
            }
        ]
    }


def _required(mapping, key):
    value = mapping.get(key)
    if value in (None, ""):
        raise ValueError(f"missing_argument:{key}")
    return value
```

- [ ] **Step 4: Run GREEN**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_mcp_stdio_server.py -q
```

Expected:

```text
3 passed
```

## Task 3: Add Notifications, Error Handling, And Stdio Loop

**Files:**
- Modify: `tests/test_commander_mcp_stdio_server.py`
- Modify: `apex/commander/mcp_stdio_server.py`

- [ ] **Step 1: Add failing notification/error/stdio tests**

Append:

```python
from io import StringIO

from apex.commander.mcp_stdio_server import serve_stdio


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
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"}) + "\n"
        + json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}) + "\n"
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
```

- [ ] **Step 2: Run RED**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_mcp_stdio_server.py -q
```

Expected: fail because `serve_stdio` does not exist yet.

- [ ] **Step 3: Implement stdio loop**

Modify `apex/commander/mcp_stdio_server.py`:

```python
import sys
```

Add:

```python
def serve_stdio(contract, *, stdin=None, stdout=None):
    input_stream = stdin or sys.stdin
    output_stream = stdout or sys.stdout
    for line in input_stream:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError as exc:
            response = _error(None, -32700, f"parse_error:{exc.msg}")
        else:
            response = handle_jsonrpc_message(message, contract)
        if response is None:
            continue
        output_stream.write(json.dumps(response, sort_keys=True) + "\n")
        output_stream.flush()
```

- [ ] **Step 4: Run GREEN**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_mcp_stdio_server.py -q
```

Expected:

```text
6 passed
```

## Task 4: Update Documentation

**Files:**
- Modify: `docs/playbooks/commander-v01-local.md`
- Modify: `docs/architecture/llm-solution-validation-framework-2026-07-09.md`

- [ ] **Step 1: Document Gate 6**

Add a Gate 6 section explaining:

- server is local stdio and JSON-RPC based;
- supported methods are `initialize`, `notifications/initialized`, `tools/list`, and `tools/call`;
- all exposed tools remain read-only;
- no network, SDK, or `apply_fix`.

- [ ] **Step 2: Update validation framework**

Update Current Codex Status, Gate 6, and Immediate Codex Backlog to mark MCP stdio local as implemented and leave SDK/client integration as a later gap.

- [ ] **Step 3: Run documentation sanity grep**

Run:

```powershell
rg -n "TBD|TODO|implement later|fill in details|placeholder" docs/playbooks/commander-v01-local.md docs/architecture/llm-solution-validation-framework-2026-07-09.md
```

Expected: no matches.

## Task 5: Final Verification

**Files:**
- Modify: none

- [ ] **Step 1: Run focused Commander tests**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_mcp_stdio_server.py tests/test_commander_tool_contract.py tests/test_commander_mcp_contract.py -q --basetemp .pytest-commander-gate6
```

Expected: all focused tests pass.

- [ ] **Step 2: Run full suite**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests -q --basetemp .pytest-codex-gate6-final
```

Expected: all tests pass.

- [ ] **Step 3: Confirm branch remains local-only**

Run:

```powershell
git status --short --branch
git rev-parse --abbrev-ref --symbolic-full-name '@{u}'
```

Expected:

```text
## gustocezar/feature/codex-desacoplamento-geradores
fatal: no upstream configured for branch 'gustocezar/feature/codex-desacoplamento-geradores'
```
