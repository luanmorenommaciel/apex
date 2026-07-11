"""Minimal read-only MCP stdio server for Commander."""

import json
import sys
from copy import deepcopy

from apex.commander.tool_contract import list_tools

PROTOCOL_VERSION = "2025-06-18"
SERVER_INFO = {"name": "apex-commander", "version": "0.1.0"}


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
        if method == "tools/call":
            params = message.get("params") or {}
            payload = contract.call_tool(
                _required(params, "name"),
                params.get("arguments") or {},
            )
            return _result(request_id, _tool_result(payload))
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
                "annotations": _tool_annotations(spec),
            }
        )
    return tools


def _tool_annotations(spec):
    read_only = spec["safety"] == "read_only"
    annotations = {"readOnlyHint": read_only}
    if not read_only:
        annotations["destructiveHint"] = True
        annotations["idempotentHint"] = False
    return annotations


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


def _result(request_id, result):
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id, code, message):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }
