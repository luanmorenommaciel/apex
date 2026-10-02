"""The error boundary, end to end: what a store failure looks like to a client.

test_api_app.py pins the boundary on /v1/health and test_ch.py pins
classification inside the store. Neither proves the two meet: that a failure
raised under a ROUTE reaches the client as the sanitized code, with the status
app.py names for it, over HTTP and over the MCP protocol a model actually
speaks. The only route-level check, test_store_error_is_sanitized_at_the_boundary,
accepts 500 or 502 — and 500 is what a client gets if diagnostics._call ever
stops recovering ApexStoreError from the SDK's ToolError chain. That test only
notices because the default TestClient re-raises the ToolError; the clients
here are built with raise_server_exceptions=False and assert the status.

Only behaviour the code already documents is pinned here:

  * app.STORE_ERROR_STATUS: a store failure is 502 ``{error: store_error}``;
  * diagnostics._call: the sanitized code survives the SDK wrapper;
  * app._unexpected: anything else is 500 with a fixed body;
  * server._fail / ch._sanitize: no raw exception text reaches a client.

Deliberately NOT pinned, because each is an open owner decision or changes
with #140: the status for input refused by the store guards, the status for a
bug inside a tool, metadata-probe failures (plans, recall, verification), and
the driver codes #140 reclassifies (81, 516, other coded errors). The
envelope is pinned only as far as app.py documents it — ``error`` and
``detail`` are present — so a decision to add a field (C8 L3) does not break
this file; a leak through any field is still caught by assert_no_leak on the
whole body.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from fastapi.testclient import TestClient
from mcp.shared.memory import create_connected_server_and_client_session

import apex_mcp.diagnose as diagnose
from apex_api.app import STORE_ERROR_STATUS, create_app
from apex_api.config import Settings
from apex_mcp.ch import ReadStore
from apex_mcp.server import create_server
from tests.conftest import FakeClient, stage_row

TOKEN = "test-token-6c1f9a"
SETTINGS = Settings(tokens=frozenset({TOKEN}))
AUTH = {"Authorization": f"Bearer {TOKEN}"}

DSN = "clickhouse://apex:sup3rs3cr3t@db.internal.example:8123/apex"
SECRETS = (DSN, "sup3rs3cr3t", "db.internal.example")


class OperationalError(Exception):
    """Named like clickhouse_connect's; ch._sanitize classifies on the name."""


# Driver failures whose code is the same with and without #140, so this file
# holds on #129 alone and on #129+#140.
STORE_FAILURES: dict[str, tuple[type[Exception], str]] = {
    "connection": (ConnectionError, "clickhouse_unavailable"),
    "operational": (OperationalError, "clickhouse_unavailable"),
    "runtime": (RuntimeError, "clickhouse_query_failed"),
}

# Routes that read the store directly, one or more per tier. The metadata
# probes are left out on purpose (see the module docstring).
VERDICT_ROUTES = [
    ("GET", "/v1/runs/j/diagnosis"),
    ("GET", "/v1/runs/j/stages/2/diagnosis"),
    ("GET", "/v1/diagnostics/search?q=skew"),
]
RESOURCE_ROUTES = [
    ("GET", "/v1/runs/j/stages"),
    ("GET", "/v1/runs"),
]
TOOL_CALLS = [
    ("analyze_run", {"job_id": "j"}),
    ("explain_stage", {"job_id": "j", "stage_id": 2}),
    ("search_kb", {"query": "skew"}),
]


class Exploding:
    """Every query raises, with the DSN in the message as a real driver does."""

    def __init__(self, exc_type: type[Exception]) -> None:
        self.exc = exc_type(f"could not connect to {DSN}: DB::Exception")

    def query(self, query: str, parameters: dict | None = None) -> Any:
        raise self.exc


def build(client: Any) -> TestClient:
    app = create_app(store=ReadStore(client), settings=SETTINGS)
    return TestClient(app, raise_server_exceptions=False)


def call_over_protocol(client: Any, tool: str, arguments: dict) -> tuple[bool, str]:
    """One tools/call through the SDK's JSON-RPC path, as an MCP client sees it.

    server.call_tool would skip the protocol layer, which is where the SDK
    turns a raised error into ``isError`` text.
    """

    async def go() -> tuple[bool, str]:
        server = create_server(ReadStore(client))
        async with create_connected_server_and_client_session(server) as session:
            result = await session.call_tool(tool, arguments)
        return bool(result.isError), " ".join(
            getattr(block, "text", "") for block in result.content
        )

    return asyncio.run(go())


def assert_no_leak(text: str) -> None:
    for secret in SECRETS:
        assert secret not in text, f"{secret!r} leaked"
    assert "Traceback" not in text
    assert "DB::Exception" not in text


# -- store failures ---------------------------------------------------------


@pytest.mark.parametrize("kind", sorted(STORE_FAILURES))
@pytest.mark.parametrize(("method", "path"), VERDICT_ROUTES + RESOURCE_ROUTES)
def test_store_failure_is_502_with_the_sanitized_code(kind, method, path):
    """Both tiers answer a store failure the same way: 502, store_error, code.

    On the verdict tier this is the ToolError-chain recovery in _call; without
    it the same request is a 500 internal_error that names nothing actionable.
    """
    exc_type, code = STORE_FAILURES[kind]
    response = build(Exploding(exc_type)).request(method, path, headers=AUTH)
    assert response.status_code == STORE_ERROR_STATUS == 502
    body = response.json()
    # At least these two keys, not exactly these: an added field is an open
    # envelope decision, and assert_no_leak below covers every field's text.
    assert {"error", "detail"} <= set(body)
    assert body["error"] == "store_error"
    assert body["detail"].startswith(f"{code}:")
    assert_no_leak(response.text)


@pytest.mark.parametrize("kind", sorted(STORE_FAILURES))
@pytest.mark.parametrize(("tool", "arguments"), TOOL_CALLS)
def test_store_failure_over_the_mcp_protocol_is_isError_with_the_code(kind, tool, arguments):
    exc_type, code = STORE_FAILURES[kind]
    is_error, text = call_over_protocol(Exploding(exc_type), tool, arguments)
    assert is_error
    assert f"{code}:" in text
    assert "apex_tool_failed" not in text  # a store failure is not a tool bug
    assert_no_leak(text)


@pytest.mark.parametrize("kind", sorted(STORE_FAILURES))
def test_health_reports_every_store_failure_class_without_failing(kind):
    exc_type, code = STORE_FAILURES[kind]
    response = build(Exploding(exc_type)).get("/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert (body["status"], body["store"]) == ("ok", "unreachable")
    assert body["detail"].startswith(f"{code}:")
    assert_no_leak(response.text)


# -- failures that are not the store's --------------------------------------


def test_non_store_failure_on_the_resource_tier_is_500_with_a_fixed_body(monkeypatch):
    """app._unexpected: the exception text never travels, whatever it holds."""

    def broken(self, job_id):  # noqa: ANN001, ANN202
        raise ValueError(f"handler bug near {DSN}")

    monkeypatch.setattr(ReadStore, "console_stages", broken)
    response = build(Exploding(RuntimeError)).get("/v1/runs/j/stages", headers=AUTH)
    assert response.status_code == 500
    body = response.json()
    assert body["error"] == "internal_error"
    assert "ValueError" not in response.text
    assert "handler bug" not in response.text
    assert_no_leak(response.text)


def test_a_tool_bug_never_reaches_either_transport_raw(monkeypatch):
    """Only the leak is pinned. Which 5xx and which key is owner leaf L2."""

    calls: list[str] = []

    def broken(*_args, **_kwargs):  # noqa: ANN002, ANN003, ANN202
        calls.append("analyze")
        raise KeyError(f"bug while reading {DSN}")

    monkeypatch.setattr(diagnose, "analyze", broken)
    healthy = FakeClient(stages={"j": [stage_row(2, job_id="j")]})

    response = build(healthy).get("/v1/runs/j/diagnosis", headers=AUTH)
    assert response.status_code in (500, 502)
    assert "KeyError" not in response.text
    assert "bug while reading" not in response.text
    assert_no_leak(response.text)

    is_error, text = call_over_protocol(healthy, "analyze_run", {"job_id": "j"})
    assert is_error
    assert calls == ["analyze", "analyze"]  # the bug, not the store, failed both
    assert "KeyError" not in text
    assert "bug while reading" not in text
    assert_no_leak(text)
