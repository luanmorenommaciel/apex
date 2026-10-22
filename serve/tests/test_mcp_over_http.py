"""P7.1 — apex-mcp reads through the Apex API.

Four properties, each with its own section:

  1. PARITY. Every tool and apex://runs, run through the REAL FastAPI app
     in-process, returns exactly what the direct ClickHouse backend returns on
     the same fake data — and the tool surface (names, annotations,
     docstrings, schemas) is identical across backends.
  2. SANITIZATION. No transport failure, refusal or malformed answer puts the
     token, the URL, the host or the port into what the model reads.
  3. CONFIGURATION. API mode, the explicit ClickHouse opt-in, and neither.
  4. NO CIRCULARITY. The API process builds its tools over its own ReadStore,
     whatever APEX_API_URL / APEX_MCP_BACKEND say in its environment.
"""

from __future__ import annotations

import ast
import asyncio
import json
import socket
from pathlib import Path
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from apex_api.app import create_app
from apex_api.config import Settings
from apex_api.routes.diagnostics import TOOL_ROUTES
from apex_mcp import api_client, server
from apex_mcp.api_client import ApiClient, ApiTools
from apex_mcp.ch import ApexStoreError, ReadStore
from apex_mcp.server import create_api_server, create_server
from tests.conftest import finding_row, reads, stage_row, transition_row
from tests.test_injection_hardening import (  # noqa: F401 — pytest fixture
    PAYLOAD,
    no_side_effects,
)
from tests.test_recall_view import FP_NEAR, _outcome, _stage
from tests.test_server_tools import CONTRACTED_TOOLS
from tests.test_verify_fix import _row as verification_row

SRC = Path(__file__).resolve().parents[1] / "src"

TOKEN = "tok-SECRET-5a9e3f17c2"
HOST = "apex-api.secret-host.example"
PORT = 9876
BASE_URL = f"http://{HOST}:{PORT}"

FP = "a" * 64

# What must never reach a model, in any error.
LEAKS = (TOKEN, BASE_URL, HOST, str(PORT), "secret-host")

FINDINGS_COLUMNS = [
    "finding_id", "job_id", "app_id", "stage_id", "type", "severity",
    "evidence", "hot_key", "impact", "fix", "confidence", "confidence_score",
    "detected_by", "ts",
]


class _WorldClient:
    """One fake store that answers every read the eight tools make.

    conftest's FakeClient falls through to spark_events for anything it does
    not recognise, which would make recall and verify_fix trivially "absent";
    this routes each table so those tools take their substantive paths.
    """

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.stages = {
            "j": [
                stage_row(4, job_id="j", p50_ms=20, p99_ms=460,
                          shuffle_read_bytes=8 << 30, spill_disk_bytes=3 << 30),
                stage_row(5, job_id="j", p50_ms=100, p99_ms=120),
            ],
            "base": [stage_row(4, job_id="base"), stage_row(5, job_id="base")],
            "evil": [stage_row(2, job_id="evil", p50_ms=10, p99_ms=500)],
            "job-current": [_stage(FP, task_count=200, p50_ms=900)],
        }
        self.findings = {
            "j": [finding_row(job_id="j", stage_id=4, confidence_score=0.9)],
            "evil": [finding_row(job_id="evil", evidence=PAYLOAD, impact=PAYLOAD,
                                 fix=PAYLOAD, hot_key=PAYLOAD)],
        }
        self.transitions = {
            "j": [transition_row("skew_split")],
            "evil": [transition_row("skew_split", detail=PAYLOAD)],
        }
        self.runs = [
            {
                "job_id": "j", "app_id": "app-j", "app_name": "test-app",
                "first_ts": "2026-08-19T09:00:00", "last_ts": "2026-08-19T09:12:00",
                "stage_count": 2, "spill_disk_bytes": 3 << 30, "worst_p99_ms": 460,
            },
            {
                "job_id": "base", "app_id": "app-base", "app_name": "test-app",
                "first_ts": "2026-08-18T09:00:00", "last_ts": "2026-08-18T09:10:00",
                "stage_count": 2, "spill_disk_bytes": 0, "worst_p99_ms": 100,
            },
        ]
        self.plans = [
            {"plan_fingerprint": FP_NEAR, "similarity": 0.91, "node_count": 12,
             "join_count": 2, "agg_count": 1, "exchange_count": 3,
             "scan_count": 2, "last_seen": "2026-08-19T09:00:00"},
        ]
        self.outcomes = [
            _outcome("job-prior-1", FP, wall_clock_ms=600_000),
            _outcome("job-prior-2", FP_NEAR, wall_clock_ms=420_000),
        ]
        self.verifications = [
            verification_row("v-1", job_id="j", finding_id="finding-1"),
            verification_row("v-2", job_id="j", finding_id="finding-2",
                             method="replayed", measured_delta_pct=-22.0,
                             noise_floor_pct=5.0, replay_reps=5),
        ]
        self.search = [
            {"source": "findings", "job_id": "j", "stage_id": 4,
             "finding_id": "finding-1", "type": "SKEW_ON_JOIN",
             "severity": "critical", "snippet": "skew tail", "score": 2.0,
             "matched_tokens": ["skew"]},
        ]

    def query(self, query: str, parameters: dict | None = None):
        parameters = parameters or {}
        self.calls.append((query, parameters))
        job_id = parameters.get("job_id", "")
        if "system.columns" in query:
            if parameters.get("table") == "fix_verifications":
                rows = [{"name": "verification_id"}]
            else:
                rows = [{"name": name} for name in FINDINGS_COLUMNS]
        elif "system.tables" in query:
            rows = [{"name": "plan_memory"}, {"name": "run_outcomes"}]
        elif "positionCaseInsensitive" in query:
            rows = list(self.search)
        elif reads(query, "plan_memory"):
            rows = list(self.plans)
        elif reads(query, "run_outcomes"):
            rows = [r for r in self.outcomes
                    if r["job_id"] != parameters.get("exclude_job_id")]
        elif reads(query, "fix_verifications"):
            finding_id = parameters.get("finding_id") or ""
            rows = [r for r in self.verifications
                    if r["job_id"] == job_id
                    and (not finding_id or r["finding_id"] == finding_id)]
        elif reads(query, "plan_transitions"):
            rows = list(self.transitions.get(job_id, []))
        elif reads(query, "findings"):
            rows = list(self.findings.get(job_id, []))
        elif "since" in parameters:
            rows = [r for r in self.runs
                    if not parameters.get("app_name")
                    or r["app_name"] == parameters["app_name"]]
        else:
            rows = list(self.stages.get(job_id, []))
        return type("R", (), {"named_results": lambda _self: list(rows)})()


def _settings() -> Settings:
    return Settings(tokens=frozenset({TOKEN}))


def _api_server(store_client: Any | None = None, token: str = TOKEN):
    """apex-mcp in API mode, wired to the real API app over an in-process transport.

    TestClient is an httpx.Client, so the MCP side's request goes through
    httpx, the API's auth middleware, its routing and its handlers — every
    layer but a socket.
    """
    app = create_app(
        store=ReadStore(store_client or _WorldClient()), settings=_settings()
    )
    http = TestClient(app, base_url=BASE_URL, raise_server_exceptions=False)
    return create_api_server(ApiClient(BASE_URL, token, http=http))


def _direct_server(store_client: Any | None = None):
    return create_server(ReadStore(store_client or _WorldClient()))


def _structured(result: Any) -> Any:
    return result[1] if isinstance(result, tuple) else result


def _call(mcp, tool: str, arguments: dict) -> Any:
    return _structured(asyncio.run(mcp.call_tool(tool, arguments)))


def _error(mcp, tool: str, arguments: dict) -> str:
    with pytest.raises(Exception) as caught:
        asyncio.run(mcp.call_tool(tool, arguments))
    return str(caught.value)


# ===========================================================================
# 1. Parity
# ===========================================================================
CASES = [
    ("analyze_run", {"job_id": "j"}),
    ("analyze_run", {"job_id": "j", "detail": "stages"}),
    ("analyze_run", {"job_id": "j", "detail": "full"}),
    ("analyze_run", {"job_id": "no-such-job"}),
    ("explain_stage", {"job_id": "j", "stage_id": 4}),
    ("explain_stage", {"job_id": "j", "stage_id": 999}),
    ("compare_runs", {"current_job_id": "j", "baseline_job_id": "base"}),
    ("compare_runs", {"current_job_id": "j", "baseline_job_id": "base",
                      "noise_floor_pct": 0.159}),
    ("compare_runs", {"current_job_id": "j"}),  # auto-baseline
    ("list_runs", {}),
    ("list_runs", {"limit": 1, "since_hours": 24, "app_name": "test-app"}),
    ("search_kb", {"query": "skew tail", "top_k": 3}),
    ("search_kb", {"query": ""}),
    ("recall_similar_runs", {"job_id": "job-current"}),
    ("recall_similar_runs", {"job_id": "job-current", "top_k": 2,
                             "noise_floor_pct": 0.05}),
    ("recall_similar_runs", {"job_id": "no-such-job"}),
    ("verify_fix", {"job_id": "j"}),
    ("verify_fix", {"job_id": "j", "finding_id": "finding-2"}),
    ("verify_fix", {"job_id": "no-such-job"}),
    ("suggest_fix", {"job_id": "j"}),
    ("suggest_fix", {"job_id": "j", "finding_id": "finding-1",
                     "min_confidence": 0.5}),
    ("suggest_fix", {"job_id": "evil"}),
    # job_ids that must survive being a URL path segment
    ("analyze_run", {"job_id": "x' OR 1=1 --"}),
    ("analyze_run", {"job_id": ".."}),
    # Not "%2F": Starlette's TestClient decodes the path twice (httpx's
    # URL.path is already decoded), which a real server does not.
    ("analyze_run", {"job_id": "a?b#c 100% & d=e"}),
]


@pytest.mark.parametrize(
    ("tool", "arguments"), CASES, ids=[f"{t}-{i}" for i, (t, _) in enumerate(CASES)]
)
def test_api_backend_returns_what_the_direct_backend_returns(tool, arguments):
    direct = _call(_direct_server(), tool, arguments)
    over_http = _call(_api_server(), tool, arguments)
    assert over_http == direct


def test_every_tool_is_covered_by_the_parity_cases():
    assert sorted({tool for tool, _ in CASES}) == CONTRACTED_TOOLS


def test_parity_cases_take_substantive_paths():
    """Guard the fixture: parity over eight 'not_found's would prove nothing."""
    mcp = _direct_server()
    assert _call(mcp, "analyze_run", {"job_id": "j"})["status"] == "degraded"
    assert _call(mcp, "recall_similar_runs", {"job_id": "job-current"})[
        "status"] == "recalled"
    assert _call(mcp, "verify_fix", {"job_id": "j"})["status"] != "not_assessed"
    assert _call(mcp, "list_runs", {})["returned"] == 2
    assert _call(mcp, "search_kb", {"query": "skew"})["hits"]
    assert _call(mcp, "compare_runs", {"current_job_id": "j"})["baseline_job_id"] == "base"


def test_runs_resource_is_byte_identical_over_the_api():
    direct = list(asyncio.run(_direct_server().read_resource("apex://runs")))
    over_http = list(asyncio.run(_api_server().read_resource("apex://runs")))
    assert over_http[0].content == direct[0].content
    payload = json.loads(over_http[0].content)
    assert payload["returned"] == 2
    assert "runs[].app_name" in payload["untrusted_fields"]


def _surface(mcp) -> str:
    tools = [t.model_dump(mode="json") for t in asyncio.run(mcp.list_tools())]
    resources = [r.model_dump(mode="json") for r in asyncio.run(mcp.list_resources())]
    return json.dumps({"tools": tools, "resources": resources}, sort_keys=True)


def test_tool_surface_is_identical_across_backends():
    """Names, annotations, docstrings, input AND output schemas, resources."""
    unconfigured = server._build_server(server._UnconfiguredTools("x: y"))
    assert _surface(_api_server()) == _surface(_direct_server())
    assert _surface(unconfigured) == _surface(_direct_server())


def test_suggest_fix_over_the_api_applies_nothing(no_side_effects):  # noqa: F811
    payload = _call(_api_server(), "suggest_fix", {"job_id": "evil"})
    assert payload["applied"] is False
    assert payload["requires_human_approval"] is True
    assert "/etc/passwd" not in payload["proposed_diff"]


def test_api_backend_triggers_no_action_on_hostile_text(no_side_effects):  # noqa: F811
    payload = _call(_api_server(), "analyze_run", {"job_id": "evil", "detail": "full"})
    assert payload["findings"][0]["evidence"] == PAYLOAD
    assert "rm -rf" not in payload["summary"]


def test_hostile_job_id_reaches_the_store_bound_and_intact():
    client = _WorldClient()
    hostile = "x'; DROP TABLE spark_events; -- .. ?q=1#frag"
    _call(_api_server(client), "analyze_run", {"job_id": hostile})
    bound = [p["job_id"] for _, p in client.calls if "job_id" in p]
    assert bound and all(value == hostile for value in bound)
    assert all(hostile not in sql for sql, _ in client.calls)


@pytest.mark.parametrize(
    "tamper", [{"applied": True}, {"requires_human_approval": False},
               {"applied": "true"}]
)
def test_a_payload_claiming_it_was_applied_cannot_be_constructed(tamper):
    """A complete, otherwise genuine suggestion — with the safety flags flipped."""
    genuine = _call(_direct_server(), "suggest_fix", {"job_id": "j"})
    assert genuine["applied"] is False

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={**genuine, **tamper})

    message = _error(_mock_server(handler), "suggest_fix", {"job_id": "j"})
    assert message.endswith(api_client.BAD_RESPONSE)


def test_a_job_id_with_a_slash_fails_closed_over_http():
    """Known limit: the API's path routing cannot address it. It must say so."""
    message = _error(_api_server(), "analyze_run", {"job_id": "a/b"})
    assert message.endswith(api_client.NOT_FOUND)


def test_client_routes_match_the_api_routes():
    """The client's copy of the route table cannot drift from the server's."""
    assert api_client.TOOL_PATHS == TOOL_ROUTES


def test_empty_job_id_is_refused_before_any_request():
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("no request should be made")

    message = _error(_mock_server(handler), "analyze_run", {"job_id": ""})
    assert "job_id_required" in message


def test_store_errors_from_the_api_keep_their_code():
    """The API's 502 carries ch._sanitize's text; its code survives the hop."""

    class Down:
        def query(self, *_a, **_k):
            raise ConnectionError(f"clickhouse://apex:pw@{HOST}:8123 refused")

    message = _error(_api_server(Down()), "analyze_run", {"job_id": "j"})
    # The code survives; the text is this server's own and points at the API.
    assert message.endswith(api_client.STORE_ERRORS["clickhouse_unavailable"])
    assert "Apex API" in message and "not of this MCP server" in message
    for leak in LEAKS + ("pw@", "8123"):
        assert leak not in message


# ===========================================================================
# 2. Sanitization
# ===========================================================================
def _mock_server(handler):
    http = httpx.Client(
        base_url=BASE_URL, transport=httpx.MockTransport(handler),
        follow_redirects=False,
    )
    return create_api_server(ApiClient(BASE_URL, TOKEN, http=http))


def _raises(exc_type):
    def handler(request: httpx.Request) -> httpx.Response:
        raise exc_type(
            f"failed talking to {request.url} with "
            f"{request.headers.get('authorization')}",
            request=request,
        )

    return handler


def _responds(status: int, *, content: bytes | None = None, body: Any = None):
    def handler(request: httpx.Request) -> httpx.Response:
        if body is not None:
            return httpx.Response(status, json=body)
        return httpx.Response(status, content=content or b"")

    return handler


LEAKY_DETAIL = f"clickhouse_unavailable: see {BASE_URL} Bearer {TOKEN}"

FAILURES = {
    "connection_refused": (_raises(httpx.ConnectError), api_client.UNAVAILABLE),
    "connect_timeout": (_raises(httpx.ConnectTimeout), api_client.TIMEOUT),
    "read_timeout": (_raises(httpx.ReadTimeout), api_client.TIMEOUT),
    "network_error": (_raises(httpx.ReadError), api_client.UNAVAILABLE),
    "401": (_responds(401, body={"error": "unauthorized", "detail": TOKEN}),
            api_client.UNAUTHORIZED),
    "403": (_responds(403, content=BASE_URL.encode()), api_client.UNAUTHORIZED),
    "404": (_responds(404, body={"detail": f"Not Found {BASE_URL}"}),
            api_client.NOT_FOUND),
    "422": (_responds(422, body={"detail": [{"input": TOKEN}]}),
            api_client.INVALID_REQUEST),
    "500": (_responds(500, body={"error": "internal_error", "detail": BASE_URL}),
            api_client.FAILED),
    "502_leaky_detail": (_responds(502, body={"error": "store_error",
                                              "detail": LEAKY_DETAIL}),
                         api_client.STORE_ERRORS["clickhouse_unavailable"]),
    "502_host_in_detail": (_responds(502, body={
        "error": "store_error",
        "detail": f"clickhouse_query_failed: {HOST} said no"}),
        api_client.STORE_ERRORS["clickhouse_query_failed"]),
    "502_unknown_code": (_responds(502, body={
        "error": "store_error", "detail": f"brand_new_code: {BASE_URL}"}),
        api_client.FAILED),
    "502_no_code": (_responds(502, body={
        "error": "store_error", "detail": f"{HOST} exploded"}),
        api_client.FAILED),
    "502_proxy_html": (_responds(502, content=b"<html>bad gateway nginx</html>"),
                       api_client.UNAVAILABLE),
    "503": (_responds(503, content=HOST.encode()), api_client.UNAVAILABLE),
    "302_redirect": (lambda r: httpx.Response(302, headers={
        "location": f"http://evil.example/steal?{TOKEN}"}), api_client.FAILED),
    "bad_json": (_responds(200, content=b"{not json " + TOKEN.encode()),
                 api_client.BAD_RESPONSE),
    "wrong_shape": (_responds(200, body={"unexpected": BASE_URL}),
                    api_client.BAD_RESPONSE),
}


@pytest.mark.parametrize("case", sorted(FAILURES))
@pytest.mark.parametrize("tool", CONTRACTED_TOOLS)
def test_tool_errors_never_leak_the_endpoint_or_token(case, tool, caplog):
    handler, expected = FAILURES[case]
    arguments = {
        "explain_stage": {"job_id": "j", "stage_id": 1},
        "compare_runs": {"current_job_id": "j"},
        "list_runs": {},
        "search_kb": {"query": "skew"},
    }.get(tool, {"job_id": "j"})
    message = _error(_mock_server(handler), tool, arguments)
    assert message.endswith(expected), message
    for leak in LEAKS:
        assert leak not in message, f"{leak!r} leaked: {message}"
    # stderr gets the details, but never the bearer token.
    assert TOKEN not in caplog.text


@pytest.mark.parametrize("case", sorted(FAILURES))
def test_resource_errors_never_leak_the_endpoint_or_token(case):
    handler, expected = FAILURES[case]
    with pytest.raises(Exception) as caught:
        asyncio.run(_mock_server(handler).read_resource("apex://runs"))
    message = str(caught.value)
    assert expected in message, message
    for leak in LEAKS:
        assert leak not in message


@pytest.mark.parametrize("code", sorted(api_client.STORE_ERRORS))
def test_a_known_store_code_maps_to_a_fixed_local_message(code):
    """Only the code is read; the API's own text never reaches the model."""
    handler = _responds(502, body={
        "error": "store_error",
        "detail": f"{code}: API-AUTHORED TEXT that must not be forwarded"})
    message = _error(_mock_server(handler), "analyze_run", {"job_id": "j"})
    assert message.endswith(api_client.STORE_ERRORS[code])
    assert "API-AUTHORED" not in message


def test_f1_free_text_in_a_known_code_does_not_reach_the_model():
    """QA F-1: a plausible, code-prefixed detail with infrastructure in it."""
    detail = ("clickhouse_query_failed: replica ch-internal-zz9 at 10.9.8.7 "
              "port 9440 rejected the query")
    handler = _responds(502, body={"error": "store_error", "detail": detail})
    for tool, arguments in (("analyze_run", {"job_id": "j"}), ("list_runs", {})):
        message = _error(_mock_server(handler), tool, arguments)
        assert message.endswith(api_client.STORE_ERRORS["clickhouse_query_failed"])
        for leak in ("ch-internal-zz9", "10.9.8.7", "9440", "replica"):
            assert leak not in message


def test_every_code_the_api_can_raise_is_on_the_allowlist():
    """A new ApexStoreError code must be mapped, or it degrades to apex_api_failed.

    Scanned from source so the allowlist cannot silently fall behind ch.py,
    server.py or the API's diagnostics route.
    """
    import re

    pattern = re.compile(r'ApexStoreError\(\s*\(?\s*f?"([a-z][a-z0-9_]*):')
    found: set[str] = set()
    for path in [SRC / "apex_mcp" / "ch.py", SRC / "apex_mcp" / "server.py",
                 *(SRC / "apex_api").rglob("*.py")]:
        found |= set(pattern.findall(path.read_text()))
    # ch._require_optional_id builds "{name}_too_long"; finding_id is the
    # only name a TOOL passes it.
    found.add("finding_id_too_long")
    assert {"clickhouse_unavailable", "apex_tool_result_unreadable"} <= found
    assert found - set(api_client.STORE_ERRORS) == set()


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_a_real_refused_connection_is_sanitized():
    """No mock: a real socket, refused by the OS."""
    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    mcp = create_api_server(ApiClient(url, TOKEN, timeout=5))
    message = _error(mcp, "list_runs", {})
    assert message.endswith(api_client.UNAVAILABLE)
    for leak in (TOKEN, url, "127.0.0.1", str(port)):
        assert leak not in message


def test_wrong_token_against_the_real_api_is_unauthorized():
    message = _error(_api_server(token="not-the-token"), "list_runs", {})
    assert message.endswith(api_client.UNAUTHORIZED)
    assert "not-the-token" not in message


def test_the_request_carries_the_bearer_token_and_no_redirects_are_followed():
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(307, headers={"location": "http://evil.example/"})

    # The production client, as built from the environment, never follows.
    assert ApiClient(BASE_URL, TOKEN)._client().follow_redirects is False
    client = ApiClient(BASE_URL, TOKEN, http=httpx.Client(
        base_url=BASE_URL, transport=httpx.MockTransport(handler),
        follow_redirects=False,
    ))
    with pytest.raises(ApexStoreError) as caught:
        client.get_json("GET", "/diagnostics/runs")
    assert str(caught.value) == api_client.FAILED
    assert len(seen) == 1
    assert seen[0].headers["authorization"] == f"Bearer {TOKEN}"
    assert seen[0].url.host == HOST


@pytest.mark.parametrize(
    ("configured", "expected"),
    [
        (BASE_URL, f"{BASE_URL}/v1/diagnostics/runs"),
        (f"{BASE_URL}/", f"{BASE_URL}/v1/diagnostics/runs"),
        (f"{BASE_URL}/v1", f"{BASE_URL}/v1/diagnostics/runs"),
        (f"{BASE_URL}/apex/", f"{BASE_URL}/apex/v1/diagnostics/runs"),
    ],
)
def test_the_base_url_is_the_api_root(configured, expected):
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(str(request.url).split("?")[0])
        return httpx.Response(200, json={"runs": [], "returned": 0})

    client = ApiClient(configured, TOKEN)
    client._http = httpx.Client(base_url=client._base_url,
                                transport=httpx.MockTransport(handler))
    client.get_json("GET", "/diagnostics/runs")
    assert seen == [expected]


# ===========================================================================
# 3. Configuration
# ===========================================================================
def _backend(env: dict[str, str]):
    return server.resolve_backend(env)


def test_api_url_and_token_select_the_api_backend():
    backend = _backend({"APEX_API_URL": BASE_URL, "APEX_API_TOKEN": TOKEN})
    assert isinstance(backend, ApiTools)


def test_explicit_api_backend_selects_the_api_backend():
    backend = _backend({"APEX_MCP_BACKEND": "api", "APEX_API_URL": BASE_URL,
                        "APEX_API_TOKEN": TOKEN})
    assert isinstance(backend, ApiTools)


def test_clickhouse_is_an_explicit_opt_in():
    backend = _backend({"APEX_MCP_BACKEND": "clickhouse"})
    assert isinstance(backend, server._StoreTools)
    assert isinstance(backend._store, ReadStore)
    assert isinstance(backend._store._client, server.LazyClient)


def test_the_clickhouse_opt_in_wins_over_an_api_url():
    backend = _backend({"APEX_MCP_BACKEND": "ClickHouse", "APEX_API_URL": BASE_URL,
                        "APEX_API_TOKEN": TOKEN})
    assert isinstance(backend, server._StoreTools)


def test_clickhouse_variables_alone_do_not_opt_in():
    backend = _backend({"CLICKHOUSE_HOST": "127.0.0.1", "CLICKHOUSE_PORT": "8123"})
    assert isinstance(backend, server._UnconfiguredTools)


@pytest.mark.parametrize(
    ("env", "expected"),
    [
        ({}, server.UNCONFIGURED),
        ({"APEX_MCP_BACKEND": "api"}, server.NO_API_URL),
        ({"APEX_MCP_BACKEND": f"mysql://{HOST}"}, server.BAD_BACKEND),
        ({"APEX_API_URL": BASE_URL}, server.NO_API_TOKEN),
        ({"APEX_API_URL": f"ftp://{HOST}:{PORT}", "APEX_API_TOKEN": TOKEN},
         server.BAD_API_URL),
        ({"APEX_API_URL": f"{HOST}:{PORT}", "APEX_API_TOKEN": TOKEN},
         server.BAD_API_URL),
        # D-1: malformed or out-of-range ports must not kill startup.
        ({"APEX_API_URL": f"http://{HOST}:99999", "APEX_API_TOKEN": TOKEN},
         server.BAD_API_URL),
        ({"APEX_API_URL": f"http://{HOST}:abc", "APEX_API_TOKEN": TOKEN},
         server.BAD_API_URL),
        ({"APEX_API_URL": f"http://{HOST}:-1", "APEX_API_TOKEN": TOKEN},
         server.BAD_API_URL),
        ({"APEX_API_URL": f"http://{HOST}:65536", "APEX_API_TOKEN": TOKEN},
         server.BAD_API_URL),
        ({"APEX_API_URL": f"http://{HOST}:0", "APEX_API_TOKEN": TOKEN},
         server.BAD_API_URL),
        # Review #3: userinfo would become Basic auth and replace the bearer.
        ({"APEX_API_URL": f"http://apex:{PORT}pw@{HOST}", "APEX_API_TOKEN": TOKEN},
         server.BAD_API_URL),
        ({"APEX_API_URL": f"https://user@{HOST}:{PORT}", "APEX_API_TOKEN": TOKEN},
         server.BAD_API_URL),
    ],
)
def test_misconfiguration_starts_lists_tools_and_fails_each_call(env, expected):
    mcp = server.server_from_env(env)
    assert sorted(t.name for t in asyncio.run(mcp.list_tools())) == CONTRACTED_TOOLS
    for tool in CONTRACTED_TOOLS:
        arguments = {"explain_stage": {"job_id": "j", "stage_id": 1},
                     "compare_runs": {"current_job_id": "j"},
                     "list_runs": {}, "search_kb": {"query": "q"}}.get(
                         tool, {"job_id": "j"})
        message = _error(mcp, tool, arguments)
        assert message.endswith(expected)
        assert message.split(": ", 1)[1].startswith(("apex_mcp_unconfigured:",
                                                     "apex_api_unconfigured:"))
        for leak in LEAKS:
            assert leak not in message
    with pytest.raises(Exception) as caught:
        asyncio.run(mcp.read_resource("apex://runs"))
    assert expected in str(caught.value)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("", 30.0), ("5", 5.0), ("0.5", 0.5), ("0", 30.0), ("-1", 30.0),
     ("abc", 30.0), ("inf", 30.0), ("nan", 30.0)],
)
def test_timeout_parsing(raw, expected):
    assert server._timeout(raw) == expected


def test_main_reads_the_environment(monkeypatch):
    monkeypatch.setenv("APEX_API_URL", BASE_URL)
    monkeypatch.setenv("APEX_API_TOKEN", TOKEN)
    monkeypatch.delenv("APEX_MCP_BACKEND", raising=False)
    assert isinstance(server.resolve_backend(), ApiTools)


def test_unconfigured_stdio_server_lists_tools_and_explains_itself():
    """End to end over real stdio: initialize, list, call — with no config."""
    from mcp import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client

    async def run() -> tuple[list[str], Any]:
        parameters = StdioServerParameters(
            command=__import__("sys").executable,
            args=["-c", "from apex_mcp.server import main; main()"],
            env={"PATH": "/usr/bin:/bin", "PYTHONPATH": str(SRC)},
        )
        async with stdio_client(parameters) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                listed = await session.list_tools()
                result = await session.call_tool("list_runs", {})
                return sorted(t.name for t in listed.tools), result

    names, result = asyncio.run(run())
    assert names == CONTRACTED_TOOLS
    assert result.isError
    assert "apex_mcp_unconfigured:" in result.content[0].text


# ===========================================================================
# 4. No circularity: the API process never reads through the API
# ===========================================================================
API_MODE_ENV = {
    "APEX_MCP_BACKEND": "api",
    "APEX_API_URL": BASE_URL,
    "APEX_API_TOKEN": TOKEN,
}


def test_create_server_accepts_only_a_direct_store():
    for not_a_store in (
        ApiClient(BASE_URL, TOKEN),
        ApiTools(ApiClient(BASE_URL, TOKEN)),
        server._UnconfiguredTools("x: y"),
        object(),
    ):
        with pytest.raises(TypeError):
            create_server(not_a_store)  # type: ignore[arg-type]


def test_api_process_serves_from_its_own_store_even_in_api_mode_env(monkeypatch):
    """APEX_API_URL in the API's own environment must change nothing."""
    for name, value in API_MODE_ENV.items():
        monkeypatch.setenv(name, value)

    def no_network(*_args, **_kwargs):
        raise AssertionError("the API process made an outbound HTTP request")

    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", no_network)
    monkeypatch.setattr(api_client.ApiClient, "get_json", no_network)

    client = _WorldClient()
    app = create_app(store=ReadStore(client), settings=_settings())
    http = TestClient(app)
    response = http.get("/v1/runs/j/diagnosis",
                        headers={"Authorization": f"Bearer {TOKEN}"})
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "degraded"
    assert client.calls, "the API did not read its own store"
    built = app.state.mcp_server
    tool = built._tool_manager.get_tool("analyze_run")
    # The registered tool closes over the backend; it must be the store one.
    backend = [c.cell_contents for c in tool.fn.__closure__
               if isinstance(c.cell_contents, (server._StoreTools, ApiTools))]
    assert backend and all(isinstance(b, server._StoreTools) for b in backend)


def test_api_app_without_an_injected_store_still_builds_a_clickhouse_store(monkeypatch):
    for name, value in API_MODE_ENV.items():
        monkeypatch.setenv(name, value)
    app = create_app(settings=_settings())
    assert type(app.state.store) is ReadStore


def test_api_package_never_references_env_backend_selection():
    """Structural: nothing under apex_api can reach the HTTP backend."""
    forbidden = {
        "server_from_env", "resolve_backend", "create_api_server", "_build_server",
        "ApiClient", "ApiTools", "api_client", "_UnconfiguredTools", "main",
    }
    offenders = []
    for path in (SRC / "apex_api").rglob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith(
                "apex_mcp"
            ):
                names = [alias.name for alias in node.names]
                names.append(node.module.rsplit(".", 1)[-1])
            elif isinstance(node, ast.Import):
                names = [alias.name.rsplit(".", 1)[-1] for alias in node.names]
            elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                if node.value.id in {"server", "apex_mcp"}:
                    names = [node.attr]
            offenders += [f"{path.name}:{node.lineno}:{n}" for n in names
                          if n in forbidden]
    assert offenders == []


# ===========================================================================
# Invariants carried over
# ===========================================================================
def test_the_api_client_module_never_prints():
    tree = ast.parse((SRC / "apex_mcp" / "api_client.py").read_text())
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
             and n.func.id == "print"]
    assert calls == []


# ===========================================================================
# URL hygiene
# ===========================================================================
@pytest.mark.parametrize(
    "url", [f"http://{HOST}:99999", f"http://{HOST}:abc", f"http://{HOST}:-1",
            f"http://{HOST}:65536", f"http://u:p@{HOST}"],
)
def test_a_bad_url_never_raises_at_startup(url):
    """resolve_backend never raises, and ApiClient survives direct construction."""
    assert isinstance(server.resolve_backend(
        {"APEX_API_URL": url, "APEX_API_TOKEN": TOKEN}), server._UnconfiguredTools)
    ApiClient(url, TOKEN)  # must not raise


def test_userinfo_would_have_replaced_the_bearer_token():
    """Why userinfo is refused: httpx sends Basic auth INSTEAD of our header."""
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={})

    url = f"http://apex:pw@{HOST}"
    httpx.Client(base_url=url, transport=httpx.MockTransport(handler)).get(
        "/v1/x", headers={"Authorization": f"Bearer {TOKEN}"})
    assert not seen[0].headers["authorization"].startswith("Bearer")
    assert api_client.valid_base_url(url) is False


@pytest.mark.parametrize(
    ("url", "warns"),
    [(f"http://{HOST}:{PORT}", True), ("http://10.0.0.5:8099", True),
     ("http://127.0.0.1:8099", False), ("http://localhost:8099", False),
     ("http://[::1]:8099", False), (f"https://{HOST}", False)],
)
def test_plain_http_to_a_remote_host_warns_once(url, warns, caplog):
    caplog.set_level("WARNING", logger="apex_mcp")
    server.resolve_backend({"APEX_API_URL": url, "APEX_API_TOKEN": TOKEN})
    hits = [r for r in caplog.records if "sent unencrypted" in r.getMessage()]
    assert len(hits) == (1 if warns else 0)
    assert TOKEN not in caplog.text


# ===========================================================================
# noise_floor_pct parity (review #5)
# ===========================================================================
INVALID_FLOORS = [-0.1, float("inf"), float("-inf"), float("nan")]

_NO_FLOOR_NOTE = "No noise floor was supplied"
_INVALID_FLOOR_NOTE = "An invalid noise floor was supplied"


def _without_floor_notes(payload: dict) -> dict:
    """The payload minus the one note direct and API mode word differently."""
    def keep(note: str) -> bool:
        return not note.startswith((_NO_FLOOR_NOTE, _INVALID_FLOOR_NOTE))

    trimmed = json.loads(json.dumps(payload))
    trimmed["notes"] = [n for n in trimmed.get("notes", []) if keep(n)]
    if isinstance(trimmed.get("summary"), dict):
        trimmed["summary"]["notes"] = [
            n for n in trimmed["summary"].get("notes", []) if keep(n)]
    return trimmed


@pytest.mark.parametrize("floor", INVALID_FLOORS, ids=str)
@pytest.mark.parametrize(
    ("tool", "arguments"),
    [("compare_runs", {"current_job_id": "j", "baseline_job_id": "base"}),
     ("recall_similar_runs", {"job_id": "job-current"})],
)
def test_an_invalid_noise_floor_succeeds_over_the_api_like_direct_mode(
    tool, arguments, floor
):
    """Same verdict as direct mode — not a 422.

    What remains different, by construction: direct mode passes the invalid
    value to diagnose, which says "An invalid noise floor was supplied"; API
    mode sends no floor, so diagnose says "No noise floor was supplied". The
    API rejects the value before diagnose could see it, and apex_api is out of
    scope, so that note is the one difference left.
    """
    arguments = {**arguments, "noise_floor_pct": floor}
    direct = _call(_direct_server(), tool, arguments)
    over_http = _call(_api_server(), tool, arguments)
    assert _without_floor_notes(over_http) == _without_floor_notes(direct)

    def notes(payload: dict) -> list[str]:
        nested = payload.get("summary")
        return payload.get("notes", []) + (
            nested.get("notes", []) if isinstance(nested, dict) else [])

    assert any(n.startswith(_INVALID_FLOOR_NOTE) for n in notes(direct))
    assert any(n.startswith(_NO_FLOOR_NOTE) for n in notes(over_http))


def test_a_valid_noise_floor_is_sent_unchanged():
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(503)

    for floor, expected in ((0.159, "0.159"), (0.0, "0.0"), (-1.0, None),
                            (float("nan"), None), (None, None)):
        seen.clear()
        with pytest.raises(Exception):
            asyncio.run(_mock_server(handler).call_tool(
                "compare_runs", {"current_job_id": "j", "noise_floor_pct": floor}))
        assert seen[0].url.params.get("noise_floor_pct") == expected


def test_the_bearer_token_outranks_url_userinfo():
    """valid_base_url refuses userinfo; a directly built client is safe anyway."""
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={})

    url = f"http://apex:pw@{HOST}"
    client = ApiClient(url, TOKEN, http=httpx.Client(
        base_url=url, transport=httpx.MockTransport(handler)))
    client.get_json("GET", "/diagnostics/runs")
    assert seen[-1].headers["authorization"] == f"Bearer {TOKEN}"
