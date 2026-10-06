"""The verdict tier: parity with the tool set, and fidelity to what it returns."""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi.testclient import TestClient

from apex_api.app import create_app
from apex_api.config import Settings
from apex_api.routes.diagnostics import TOOL_ROUTES
from apex_mcp.ch import ApexStoreError, ReadStore
from apex_mcp.server import create_server
from tests.conftest import FakeClient, finding_row, stage_row, transition_row

TOKEN = "test-token-6c1f9a"
SETTINGS = Settings(tokens=frozenset({TOKEN}))
AUTH = {"Authorization": f"Bearer {TOKEN}"}

DSN = "clickhouse://apex:sup3rs3cr3t@db.internal.example:8123/apex"


def fake_client() -> FakeClient:
    return FakeClient(
        stages={"j": [stage_row(4, p50_ms=20, p99_ms=460)], "base": [stage_row(4)]},
        findings={"j": [finding_row(job_id="j", confidence_score=0.9)], "base": []},
        transitions={"j": [transition_row("skew_split")]},
        search=[
            {
                "source": "findings", "job_id": "j", "stage_id": 2,
                "finding_id": "f1", "type": "SKEW_ON_JOIN", "severity": "critical",
                "snippet": "skew tail", "score": 2.0, "matched_tokens": ["skew"],
            }
        ],
    )


def build(client: Any | None = None) -> TestClient:
    store = ReadStore(client if client is not None else fake_client())
    return TestClient(create_app(store=store, settings=SETTINGS))


def tool_names() -> set[str]:
    server = create_server(ReadStore(fake_client()))
    return {tool.name for tool in asyncio.run(server.list_tools())}


# -- parity -----------------------------------------------------------------


def test_every_tool_has_exactly_one_route():
    """A ninth tool cannot ship without a route.

    The MCP side already refuses an unnoticed tool; this is the same control
    on the HTTP side, where the tool would otherwise be unreachable and
    nothing would say so.
    """
    missing = tool_names() - set(TOOL_ROUTES)
    assert missing == set(), f"tools with no route: {sorted(missing)}"
    # One path per tool, so two tools cannot collapse onto one endpoint.
    paths = [path for _, path in TOOL_ROUTES.values()]
    assert len(paths) == len(set(paths))


def test_every_route_maps_to_a_tool():
    """And a route cannot exist for a tool that does not."""
    extra = set(TOOL_ROUTES) - tool_names()
    assert extra == set(), f"routes with no tool: {sorted(extra)}"

    # The declared table is what the app actually serves, not a parallel list.
    # Read from the OpenAPI schema rather than app.routes: an included router
    # appears there as an opaque _IncludedRouter carrying neither path nor
    # methods, so walking app.routes would silently see zero routes and pass.
    schema = create_app(store=ReadStore(fake_client()), settings=SETTINGS).openapi()
    served = {
        (method.upper(), path.removeprefix("/v1"))
        for path, operations in schema["paths"].items()
        for method in operations
    }
    for tool, (method, path) in TOOL_ROUTES.items():
        assert (method, path) in served, f"{tool} is declared but not served"


# -- fidelity ---------------------------------------------------------------


def test_diagnosis_route_matches_the_tool():
    """The route is a transport, not a second analysis."""
    client = fake_client()
    body = build(client).get("/v1/runs/j/diagnosis", headers=AUTH).json()

    server = create_server(ReadStore(fake_client()))
    direct = asyncio.run(server.call_tool("analyze_run", {"job_id": "j", "detail": "summary"}))
    expected = direct[1] if isinstance(direct, tuple) else direct

    assert body == expected
    # And it is a Diagnosis, not an opaque blob.
    for field in ("status", "job_id", "summary"):
        assert field in body


def test_tuple_and_dict_results_are_both_normalised():
    """call_tool is typed Sequence[ContentBlock] | dict; both must work."""
    from apex_api.routes.diagnostics import _structured

    assert _structured({"applied": False}) == {"applied": False}
    assert _structured((["content-block"], {"applied": False})) == {"applied": False}

    # A shape carrying no structured payload is an error, never a silent pass
    # of content blocks to a client expecting a model.
    try:
        _structured(["content-block"])
    except ApexStoreError as exc:
        assert "unreadable" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("a bare content sequence should not be accepted")


# -- guarantees -------------------------------------------------------------


def test_fix_suggestion_route_applies_nothing():
    """The HTTP surface must not describe the proposal tool as safer than it is."""
    body = build().post("/v1/runs/j/fix-suggestion", headers=AUTH).json()
    assert body["applied"] is False
    assert body["requires_human_approval"] is True
    # POST, because the tool is the one the MCP layer marks not read-only.
    assert TOOL_ROUTES["suggest_fix"][0] == "POST"
    assert build().get("/v1/runs/j/fix-suggestion", headers=AUTH).status_code == 405


def test_store_error_is_sanitized_at_the_boundary():
    class Exploding:
        def query(self, query: str, parameters: dict | None = None):
            raise RuntimeError(f"could not connect to {DSN}")

    response = build(Exploding()).get("/v1/runs/j/diagnosis", headers=AUTH)
    assert response.status_code in (500, 502)
    for secret in (DSN, "sup3rs3cr3t", "db.internal.example"):
        assert secret not in response.text
    assert "Traceback" not in response.text
