"""P7.5 — one run list: the MCP's list_runs and the console's GET /v1/runs.

Three doors list runs (the MCP tool, GET /v1/diagnostics/runs, GET /v1/runs —
plus the browser's RUN_LIST statement). For the same arguments they must name
the same runs in the same order. What is provable offline is proven here: one
membership literal, one order, one set of defaults, every filter bound. That
the two projections return the same job_id ORDER on a real store is the live
parity gate's (tools/console_parity_gate.py, "cross-door order").
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import pathlib
import re
import sqlite3
import sys
from typing import Any
from unittest.mock import Mock

import pytest
import httpx
from fastapi.testclient import TestClient

from apex_api.app import create_app
from apex_api.config import Settings
from apex_mcp import ch
from apex_mcp.ch import ApexStoreError, ReadStore
from apex_mcp.api_client import ApiClient
from apex_mcp.models import RunList
from apex_mcp.server import create_api_server, create_server

TOKEN = "test-token-p75"
AUTH = {"Authorization": f"Bearer {TOKEN}"}
HOSTILE = "' OR 1=1 --"
FP = "c" * 64

GATE_PATH = pathlib.Path(__file__).resolve().parents[1] / "tools" / "console_parity_gate.py"


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"--[^\n]*", "", text)).strip()


class _ListClient:
    """Records every statement; answers the memory probe, returns no rows."""

    def __init__(self, tables: tuple[str, ...] = ("plan_memory", "run_outcomes")) -> None:
        self.tables = tables
        self.calls: list[tuple[str, dict]] = []

    def query(self, query: str, parameters: dict | None = None):
        self.calls.append((query, dict(parameters or {})))
        if "system.tables" in query:
            rows = [{"name": t} for t in self.tables]
        elif "system.columns" in query:  # ReadStore.table_exists
            rows = [{"name": "job_id"}] if (parameters or {}).get("table") in self.tables else []
        else:
            rows = []
        return type("R", (), {"named_results": lambda _s: list(rows)})()

    def listing(self) -> tuple[str, dict]:
        """The one run-listing statement issued (probes skipped)."""
        found = [(q, p) for q, p in self.calls if "since_hours" in p]
        assert len(found) == 1, f"expected one listing, saw {len(found)}"
        return found[0]


def _app(client: Any) -> TestClient:
    return TestClient(
        create_app(store=ReadStore(client), settings=Settings(tokens=frozenset({TOKEN})))
    )


# --------------------------------------------------------------------------
# One membership, one order
# --------------------------------------------------------------------------
def test_both_projections_share_one_membership_and_one_order():
    for sql in (ch.RUNS_SQL, ch.RUNS_BY_SHAPE_SQL, ch.RUN_LIST_SQL):
        assert ch.RUN_MEMBERSHIP in sql
        assert ch.RUN_PAGE in sql
    assert ch.RUN_SHAPE_FILTER in ch.RUN_LIST_SQL
    assert ch.RUN_SHAPE_FILTER in ch.RUNS_BY_SHAPE_SQL
    # RUNS_SQL must work on a v0.2 deployment: no v0.3 table in it.
    assert "run_outcomes" not in ch.RUNS_SQL
    # first_ts is min(ts) over the run — the rollup's started_at.
    assert "min(ts)                        AS first_ts" in ch.RUNS_SQL
    assert "ORDER BY first_ts DESC, job_id ASC" in ch.RUNS_SQL
    assert "min(ts) AS started_at" in ch.RUN_LIST_SQL
    assert "ORDER BY b.started_at DESC, b.job_id ASC" in ch.RUN_LIST_SQL


def test_the_window_prunes_on_ts_but_aggregates_cover_every_event():
    """The ts bound sits in the membership sub-select, never on the outer read."""
    inner = "w.ts >= now() - toIntervalHour({since_hours:UInt32})"
    for sql in (ch.RUNS_SQL, ch.RUN_LIST_SQL):
        assert inner in sql
        assert re.search(r"WHERE job_id IN \(SELECT w\.job_id FROM spark_events AS w", sql)
        # No unqualified outer ts predicate truncating a straddling run.
        assert not re.search(r"(?<![\w.])ts\s*>=", sql)


def test_the_browser_sends_the_same_run_list_statement():
    """queries.ts RUN_LIST, assembled as the gate assembles it, IS RUN_LIST_SQL."""
    spec = importlib.util.spec_from_file_location("console_parity_gate_p75", GATE_PATH)
    gate = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = gate
    spec.loader.exec_module(gate)
    statements = gate.console_statements(gate.QUERIES_TS.read_text())
    assert _normalise(statements["RUN_LIST"]) == _normalise(ch.RUN_LIST_SQL)


# --------------------------------------------------------------------------
# Defaults — the same on every door
# --------------------------------------------------------------------------
DEFAULTS = {"limit": 50, "since_hours": 168, "offset": 0, "app_name": "",
            "job_id_prefix": "", "has_findings": -1}


def test_store_defaults():
    for call in (lambda s: s.runs(), lambda s: s.run_list()):
        client = _ListClient()
        call(ReadStore(client))
        _, params = client.listing()
        assert {k: params[k] for k in DEFAULTS} == DEFAULTS


def test_mcp_tool_defaults():
    client = _ListClient()
    payload = asyncio.run(create_server(ReadStore(client)).call_tool("list_runs", {}))
    payload = payload[1] if isinstance(payload, tuple) else payload
    _, params = client.listing()
    assert {k: params[k] for k in DEFAULTS} == DEFAULTS
    assert (payload["limit"], payload["since_hours"], payload["offset"]) == (50, 168, 0)


@pytest.mark.parametrize("backend", ["direct", "api-in-process"])
def test_real_runs_resource_echoes_defaults_and_passes_them_to_store(monkeypatch, backend):
    client = _ListClient()
    store = ReadStore(client)
    runs = Mock(wraps=store.runs)
    monkeypatch.setattr(store, "runs", runs)
    with TestClient(create_app(store=store, settings=Settings(tokens=frozenset({TOKEN})))) as http:
        server = create_server(store) if backend == "direct" else create_api_server(
            ApiClient("http://testserver", TOKEN, http=http))
        contents = list(asyncio.run(server.read_resource("apex://runs")))
    assert len(contents) == 1
    payload = json.loads(contents[0].content)
    assert (payload["limit"], payload["since_hours"], payload["offset"]) == (50, 168, 0)
    assert payload["returned"] == 0 and payload["runs"] == []
    assert runs.call_count == 1
    assert {key: runs.call_args.kwargs[key] for key in ("limit", "since_hours", "offset")} == {
        "limit": 50, "since_hours": 168, "offset": 0,
    }
    _, bound = client.listing()
    assert (bound["limit"], bound["since_hours"], bound["offset"]) == (50, 168, 0)


def test_api_runs_resource_keeps_effective_defaults_from_fake_transport():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json=RunList(
            runs=[], returned=0, limit=50, since_hours=168, offset=0,
        ).model_dump(mode="json"))

    with httpx.Client(base_url="http://offline.test", transport=httpx.MockTransport(handler)) as http:
        server = create_api_server(ApiClient("http://offline.test", TOKEN, http=http))
        contents = list(asyncio.run(server.read_resource("apex://runs")))
    assert len(seen) == 1
    assert seen[0].url.path == "/v1/diagnostics/runs"
    payload = json.loads(contents[0].content)
    assert (payload["limit"], payload["since_hours"], payload["offset"]) == (50, 168, 0)


@pytest.mark.parametrize("path", ["/v1/runs", "/v1/diagnostics/runs"])
def test_http_defaults(path):
    client = _ListClient()
    response = _app(client).get(path, headers=AUTH)
    assert response.status_code == 200, response.text
    _, params = client.listing()
    assert {k: params[k] for k in DEFAULTS} == DEFAULTS


# --------------------------------------------------------------------------
# Every filter binds — L2 style
# --------------------------------------------------------------------------
@pytest.mark.parametrize("method", ["runs", "run_list"])
@pytest.mark.parametrize("field", ["app_name", "job_id_prefix", "plan_fingerprint"])
def test_hostile_filter_values_bind_as_data(method, field):
    client = _ListClient()
    getattr(ReadStore(client), method)(**{field: HOSTILE})
    sql, params = client.listing()
    expected = ch.RUN_LIST_SQL if method == "run_list" else (
        ch.RUNS_BY_SHAPE_SQL if field == "plan_fingerprint" else ch.RUNS_SQL)
    assert sql == expected, "the statement text must not change with a value"
    assert HOSTILE not in sql
    assert params[field] == HOSTILE
    assert f"{{{field}:String}}" in sql


@pytest.mark.parametrize("path", ["/v1/runs", "/v1/diagnostics/runs"])
@pytest.mark.parametrize("field", ["app_name", "job_id_prefix", "plan_fingerprint"])
def test_hostile_filter_values_bind_through_http(path, field):
    client = _ListClient()
    response = _app(client).get(path, params={field: HOSTILE}, headers=AUTH)
    assert response.status_code == 200, response.text
    sql, params = client.listing()
    assert HOSTILE not in sql
    assert params[field] == HOSTILE
    assert sql in (ch.RUNS_SQL, ch.RUNS_BY_SHAPE_SQL, ch.RUN_LIST_SQL)


@pytest.mark.parametrize(("given", "bound"), [(None, -1), (True, 1), (False, 0)])
def test_has_findings_is_tri_state(given, bound):
    client = _ListClient()
    ReadStore(client).runs(has_findings=given)
    assert client.listing()[1]["has_findings"] == bound
    assert "{has_findings:Int8} = -1" in ch.RUN_MEMBERSHIP


@pytest.mark.parametrize("path", ["/v1/runs", "/v1/diagnostics/runs"])
@pytest.mark.parametrize(("query", "bound"), [("true", 1), ("false", 0)])
def test_has_findings_over_http(path, query, bound):
    client = _ListClient()
    assert _app(client).get(path, params={"has_findings": query}, headers=AUTH).status_code == 200
    assert client.listing()[1]["has_findings"] == bound


def test_limit_and_window_clamp_but_offset_is_refused():
    client = _ListClient()
    ReadStore(client).run_list(limit=0, since_hours=0)
    params = client.listing()[1]
    assert (params["limit"], params["since_hours"], params["offset"]) == (1, 1, 0)
    client = _ListClient()
    ReadStore(client).runs(limit=10**6, since_hours=10**9, offset=ReadStore.MAX_RUNS_OFFSET)
    params = client.listing()[1]
    assert params["limit"] == ReadStore.MAX_RUNS
    assert params["since_hours"] == ReadStore.MAX_SINCE_HOURS
    assert params["offset"] == ReadStore.MAX_RUNS_OFFSET == 10_000
    # A clamped offset is a DIFFERENT page than the one asked for: refused.
    for method in ("runs", "run_list"):
        for offset in (-1, 10_001):
            client = _ListClient()
            with pytest.raises(ApexStoreError, match=r"^offset_out_of_range: "):
                getattr(ReadStore(client), method)(offset=offset)
            assert client.calls == []


@pytest.mark.parametrize("path", ["/v1/runs", "/v1/diagnostics/runs"])
@pytest.mark.parametrize("offset", ["-1", "10001"])
def test_http_refuses_an_out_of_range_offset_with_422(path, offset):
    client = _ListClient()
    response = _app(client).get(path, params={"offset": offset}, headers=AUTH)
    assert response.status_code == 422
    assert client.calls == []
    assert _app(_ListClient()).get(path, params={"offset": "10000"}, headers=AUTH).status_code == 200


def test_mcp_echoes_the_effective_page_not_the_requested_one():
    client = _ListClient()
    payload = asyncio.run(create_server(ReadStore(client)).call_tool(
        "list_runs", {"limit": 10**6, "since_hours": 0}))
    payload = payload[1] if isinstance(payload, tuple) else payload
    assert (payload["limit"], payload["since_hours"], payload["offset"]) == (200, 1, 0)


@pytest.mark.parametrize("offset", [-1, 10_001])
def test_mcp_refuses_an_out_of_range_offset(offset):
    client = _ListClient()
    with pytest.raises(Exception, match="offset_out_of_range"):
        asyncio.run(create_server(ReadStore(client)).call_tool("list_runs", {"offset": offset}))
    assert client.calls == []


@pytest.mark.parametrize("method", ["runs", "run_list"])
@pytest.mark.parametrize(("field", "size"), [
    ("app_name", 513), ("job_id_prefix", 513), ("plan_fingerprint", 65),
])
def test_oversized_filter_is_refused_before_any_query(method, field, size):
    client = _ListClient()
    with pytest.raises(ApexStoreError, match=rf"^{field}_too_long: "):
        getattr(ReadStore(client), method)(**{field: "x" * size})
    assert client.calls == []
    # At the limit it is still a filter, not an error.
    getattr(ReadStore(_ListClient()), method)(**{field: "x" * (size - 1)})


def test_fingerprint_is_compared_as_the_column_is_stored():
    """FixedString(64), the house way: capped before toFixedString, which throws."""
    assert "toFixedString(substring({plan_fingerprint:String}, 1, 64), 64)" in ch.RUN_SHAPE_FILTER


def _offline_shape_rows(sql, fingerprint):
    """Execute the shipped predicate, translating only CH dialect mechanics.

    SQLite supplies boolean/subquery semantics; the UDF supplies FixedString
    padding. ASCII hex fixtures avoid character/byte length differences. This
    does not claim to verify ClickHouse parsing, FINAL or query optimization.
    """
    match = re.search(r" AND \(\{plan_fingerprint:String\} = ''.*?\)\)\)", sql, re.S)
    assert match, "the supplied production statement must contain the shape predicate"
    predicate = match[0].replace("{plan_fingerprint:String}", ":plan_fingerprint")
    predicate = predicate.replace(" AS o FINAL", " AS o")
    with sqlite3.connect(":memory:") as db:
        db.create_function("toFixedString", 2, lambda value, size: value.encode().ljust(size, b"\0"))
        db.execute("CREATE TABLE candidates (job_id TEXT)")
        db.execute("CREATE TABLE run_outcomes (job_id TEXT, plan_fingerprint BLOB)")
        db.execute("INSERT INTO candidates VALUES ('matching-prefix')")
        db.execute("INSERT INTO run_outcomes VALUES (?, ?)", ("matching-prefix", FP.encode()))
        return [row[0] for row in db.execute(
            "SELECT job_id FROM candidates WHERE 1" + predicate,
            {"plan_fingerprint": fingerprint},
        )]


@pytest.mark.parametrize("sql", [ch.RUNS_BY_SHAPE_SQL, ch.RUN_LIST_SQL], ids=["mcp", "console-projection"])
@pytest.mark.parametrize(("fingerprint", "expected"), [
    ("", ["matching-prefix"]),
    (FP, ["matching-prefix"]),
    ("d" * 64, []),
    (FP[:-1], []),
    (FP + "d", []),
    (FP + "d" * 64, []),
])
def test_actual_sql_shape_predicate_rejects_long_values_with_matching_prefix(sql, fingerprint, expected):
    # Deliberately enter below ReadStore's pre-query input refusal: that refusal
    # cannot establish that the actual SQL guard works. Record the raw binding.
    seen = []

    class OfflinePredicateClient:
        def query(self, query, parameters):
            seen.append((query, dict(parameters)))
            rows = [{"job_id": job} for job in _offline_shape_rows(query, parameters["plan_fingerprint"])]
            return type("Result", (), {"named_results": lambda self: rows})()

    rows = ReadStore(OfflinePredicateClient())._query(sql, {"plan_fingerprint": fingerprint})
    assert seen == [(sql, {"plan_fingerprint": fingerprint})]
    assert [row["job_id"] for row in rows] == expected


@pytest.mark.parametrize("sql", [ch.RUNS_BY_SHAPE_SQL, ch.RUN_LIST_SQL])
def test_sql_fixture_reproduces_truncated_prefix_match_without_length_guard(sql):
    # Negative control: the old predicate really matches the 65-character input.
    old_sql = sql.replace("length({plan_fingerprint:String}) <= 64 AND ", "")
    assert old_sql != sql
    assert _offline_shape_rows(old_sql, FP + "d") == ["matching-prefix"]


def test_mcp_fingerprint_filter_needs_run_outcomes_only():
    """Not an empty list: "no table" and "no runs of that shape" differ."""
    client = _ListClient(tables=())
    with pytest.raises(ApexStoreError, match="memory_unavailable.*run_outcomes"):
        ReadStore(client).runs(plan_fingerprint=FP)
    # plan_memory is not read by this filter, so its absence does not matter
    # (a partial v0.3 rollout, as in fix_verification).
    client = _ListClient(tables=("run_outcomes",))
    ReadStore(client).runs(plan_fingerprint=FP)
    sql, params = client.listing()
    assert sql == ch.RUNS_BY_SHAPE_SQL and params["plan_fingerprint"] == FP
    # Without the filter, a v0.2 deployment still lists runs and probes nothing.
    client = _ListClient(tables=())
    ReadStore(client).runs()
    assert all("system.tables" not in q for q, _ in client.calls)


def test_mcp_echoes_the_filters_and_offset():
    client = _ListClient()
    payload = asyncio.run(create_server(ReadStore(client)).call_tool("list_runs", {
        "limit": 5, "offset": 10, "job_id_prefix": "app-", "plan_fingerprint": FP,
        "has_findings": False, "app_name": "etl",
    }))
    payload = payload[1] if isinstance(payload, tuple) else payload
    assert payload["offset"] == 10
    assert payload["job_id_prefix_filter"] == "app-"
    assert payload["plan_fingerprint_filter"] == FP
    assert payload["has_findings_filter"] is False
    assert payload["app_name_filter"] == "etl"
    _, params = client.listing()
    assert (params["limit"], params["offset"], params["has_findings"]) == (5, 10, 0)


def test_tool_stays_flat_and_read_only():
    server = create_server(ReadStore(_ListClient()))
    tool = next(t for t in asyncio.run(server.list_tools()) if t.name == "list_runs")
    assert tool.annotations.readOnlyHint is True
    assert set(tool.inputSchema["properties"]) == {
        "limit", "since_hours", "app_name", "offset", "job_id_prefix",
        "plan_fingerprint", "has_findings",
    }
