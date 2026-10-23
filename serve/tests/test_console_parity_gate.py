"""The live gate's own logic, offline.

What only a live store can prove is proven by running the gate. What is tested
here is that the gate reads the console's statements as the console wrote
them, compares rows the way a screen would see them, and never reports a
check it could not exercise as passed.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import pathlib
import re
import sys

from apex_api.app import create_app
from apex_api.config import Settings
from apex_mcp.ch import ReadStore
from tests.test_ch import _ConsoleClient

GATE_PATH = pathlib.Path(__file__).resolve().parents[1] / "tools" / "console_parity_gate.py"


def load_gate():
    spec = importlib.util.spec_from_file_location("console_parity_gate", GATE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


gate = load_gate()


def test_statements_are_read_from_the_console_as_written():
    statements = gate.console_statements(gate.QUERIES_TS.read_text())
    for name in (
        "RUN_LIST", "RUN_ONE", "LATEST_STAGES", "JOB_CONF", "FINDINGS",
        "PLAN_TRANSITIONS", "RUNS_SHARING_SHAPE", "PLAN_SHAPES", "SHAPE_RUNS",
        "PLAN_SAMPLE", "FIX_VERIFICATIONS",
    ):
        assert name in statements, f"the gate cannot find {name} in queries.ts"
    # The two rollups are BUILT in the TypeScript; the gate builds them the same way.
    assert "WHERE job_id = {job:String}" in statements["RUN_ONE"]
    assert statements["RUN_ONE"].rstrip().endswith("LIMIT 1")
    assert (
        "ORDER BY b.started_at DESC, b.job_id ASC LIMIT {limit:UInt32} OFFSET {offset:UInt32}"
        in statements["RUN_LIST"]
    )
    # P7.5: the list is windowed by run membership, not by a job_id equality.
    base = statements["RUN_LIST"].split("shapes AS")[0].split("f AS")[0]
    assert "WHERE job_id IN (SELECT w.job_id FROM spark_events AS w" in base
    assert "WHERE job_id =" not in base
    for sql in statements.values():
        assert "${" not in sql, "a template placeholder reached the statement"
        # The console's parameter names, not serve's.
        assert "{job_id:String}" not in sql
    # An escaped backtick in a TypeScript comment is a backtick in the SQL.
    assert "\\`" not in statements["LATEST_STAGES"]


def test_the_wire_pattern_is_the_consoles():
    pattern = gate.wire_pattern(gate.TIMESTAMP_TS.read_text())
    assert pattern.fullmatch("2026-09-20T10:00:00.123")
    assert not pattern.fullmatch("2026-09-20 10:00:00.123")
    assert not pattern.fullmatch("2026-09-20T10:00:00")


def test_numerics_are_coerced_by_declared_type_like_the_browser():
    payload = {
        "meta": [
            {"name": "bytes", "type": "Int64"},
            {"name": "slots", "type": "Nullable(Int32)"},
            {"name": "score", "type": "Float32"},
            {"name": "value", "type": "String"},
        ],
        "data": [{"bytes": "4398046511104", "slots": None, "score": "0.9", "value": "200"}],
    }
    assert gate.coerce_numerics(payload) == [
        # A String column holding "200" stays the string it is.
        {"bytes": 4398046511104, "slots": None, "score": 0.9, "value": "200"}
    ]


def test_a_difference_is_named_and_a_float32_is_one_number():
    same = {"job_id": "j", "confidence_score": 0.9, "n": 3, "ts": "2026-09-20T10:00:00.123"}
    widened = dict(same, confidence_score=0.8999999761581421)
    assert gate.difference([same], [widened]) is None

    assert "confidence_score" in gate.difference([same], [dict(same, confidence_score=0.5)])
    assert "browser returned 1, api returned 2" in gate.difference([same], [same, same])
    # The projection defect this gate exists for: a column one door lacks.
    missing = {k: v for k, v in same.items() if k != "ts"}
    found = gate.difference([same], [missing])
    assert "columns differ" in found and "browser only ['ts']" in found
    assert "[0].n" in gate.difference([same], [dict(same, n=4)])
    assert gate.difference(None, None) is None
    assert gate.difference(None, same) is not None


def test_the_in_process_door_reaches_the_app():
    token = "gate-test-token"
    app = create_app(
        store=ReadStore(_ConsoleClient(run_rows=[{"job_id": "j", "stage_id": 1}])),
        settings=Settings(tokens=frozenset({token})),
    )
    status, body = asyncio.run(gate._asgi_get(app, "/v1/runs/j/stages", {"authorization": f"Bearer {token}"}))
    assert status == 200 and json.loads(body) == [{"job_id": "j", "stage_id": 1}]
    # And admission still applies: the gate is a client, not a way around it.
    status, _ = asyncio.run(gate._asgi_get(app, "/v1/runs/j/stages", {}))
    assert status == 401


def test_a_check_the_data_cannot_exercise_is_not_a_pass(monkeypatch):
    """An indexed run, one finding, no re-planned execution: three checks have
    nothing to prove, and say so."""

    def browser(_store, sql, params):
        if "FROM run_outcomes" in sql:
            return [{"count()": 1}]                     # the run IS indexed
        if "getSetting" in sql:
            return [{"readonly": 1}]
        if "uniqExact(execution_id)" in sql:
            return [{"n": 1}]
        if "FROM plan_transitions" in sql:
            return [{"count()": 1}]                     # one row, one execution
        return []

    monkeypatch.setattr(gate, "browser_query", browser)
    report = gate.Report()
    store = gate.Store("h", 1, "apex", "apex", "", "apex_ro", "")
    api = gate.Api(get=lambda path: (200, {}), label="fake")
    seen = {
        "findings": [{"finding_id": "f1", "confidence_score": 0.4, "ts": "2026-09-20T10:00:00.123"}],
        "transitions": [{"execution_id": 1, "update_seq": 0, "ts": "2026-09-20T10:00:00.123"}],
    }
    gate.live_only(
        report, store, api, {"RUN_ONE": ""}, re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}$"),
        seen, job="j", unindexed_job=None,
    )
    verdicts = {name: verdict for verdict, name, _ in report.lines}
    assert verdicts["unindexed run reads as not indexed"] == gate.SKIP
    assert verdicts["findings ordered by confidence_score"] == gate.SKIP
    assert verdicts["one transition per execution"] == gate.SKIP
    assert verdicts["statements run as a read-only user"] == gate.PASS
    assert verdicts["timestamps in the wire format"] == gate.PASS
    assert report.count(gate.SKIP) == 3 and not report.failed


def test_a_privileged_browser_user_voids_the_readonly_proof(monkeypatch):
    def browser(_store, sql, params):
        if "getSetting" in sql:
            return [{"readonly": 0}]
        return [{"count()": 1}]

    monkeypatch.setattr(gate, "browser_query", browser)
    report = gate.Report()
    store = gate.Store("h", 1, "apex", "apex", "", "apex", "")
    gate.live_only(
        report, store, gate.Api(get=lambda path: (200, {}), label="fake"), {"RUN_ONE": ""},
        re.compile("x"), {}, job="j", unindexed_job=None,
    )
    assert report.failed
    assert any(name == "statements run as a read-only user" and verdict == gate.FAIL
               for verdict, name, _ in report.lines)


def test_a_route_that_dropped_a_column_is_reported_not_raised(monkeypatch):
    """The MCP's findings projection has no ts. The gate met it as a KeyError."""
    monkeypatch.setattr(gate, "browser_query", lambda _s, sql, _p: [{"n": 0}])
    report = gate.Report()
    store = gate.Store("h", 1, "apex", "apex", "", "apex_ro", "")
    seen = {
        "findings": [{"finding_id": "f1", "confidence_score": 0.9}, {"finding_id": "f2", "confidence_score": 0.2}],
        "transitions": [{"execution_id": 1}],
    }
    gate.live_only(
        report, store, gate.Api(get=lambda path: (200, {}), label="fake"), {"RUN_ONE": ""},
        re.compile("x"), seen, job="j", unindexed_job=None,
    )
    finding_line = next(line for line in report.lines if line[1] == "findings ordered by confidence_score")
    assert finding_line[0] == gate.FAIL and "no ts" in finding_line[2]


# -- P7.5: the run list's filters and the cross-door order -------------------
def test_run_list_cases_bind_every_placeholder_and_map_to_the_routes():
    statements = gate.console_statements(gate.QUERIES_TS.read_text())
    placeholders = set(re.findall(r"\{(\w+):", statements["RUN_LIST"]))
    for _name, params in gate.run_list_cases("parity-gate-", "f" * 64):
        assert set(params) == placeholders
    assert gate.run_list_query(gate.run_list_params()) == (
        "limit=50&since_hours=168&offset=0&app_name=&job_id_prefix=&plan_fingerprint="
    )
    assert "has_findings=true" in gate.run_list_query(gate.run_list_params(has_findings=1))
    assert "has_findings=false" in gate.run_list_query(gate.run_list_params(has_findings=0))
    hostile = gate.run_list_query(gate.run_list_params(job_id_prefix="' OR 1=1 --&x=1"))
    assert "x=1" not in hostile.split("&")


def _order_api(mcp_ids, console_ids, status=200):
    def get(path):
        if path.startswith("/v1/diagnostics/runs"):
            return status, {"runs": [{"job_id": j} for j in mcp_ids]}
        return status, [{"job_id": j} for j in console_ids]
    return gate.Api(get=get, label="fake")


def test_cross_door_order_passes_on_the_same_order_and_fails_on_a_swap():
    report = gate.Report()
    gate.cross_door_order(report, _order_api(["a", "b"], ["a", "b"]), prefix="p", fingerprint="")
    assert not report.failed and report.count(gate.PASS) == 5
    report = gate.Report()
    gate.cross_door_order(report, _order_api(["a", "b"], ["b", "a"]), prefix="p", fingerprint="")
    assert report.failed


def test_cross_door_order_on_nothing_is_not_a_pass():
    report = gate.Report()
    gate.cross_door_order(report, _order_api([], []), prefix="p", fingerprint="")
    assert report.count(gate.SKIP) == 5 and report.count(gate.PASS) == 0


def test_the_cross_door_order_holds_through_the_real_app():
    """In process, over one store: the two routes reach one membership/order."""
    token = "gate-test-token"
    rows = [{"job_id": "b", "started_at": "2026-09-20 10:00:00"},
            {"job_id": "a", "started_at": "2026-09-20 09:00:00"}]

    class Client:
        def query(self, query, parameters=None):
            out = rows if "since_hours" in (parameters or {}) else []
            if "shaped_stage_count" not in query:
                out = [{"job_id": r["job_id"], "first_ts": r["started_at"]} for r in out]
            return type("R", (), {"named_results": lambda _s: list(out)})()

    app = create_app(store=ReadStore(Client()), settings=Settings(tokens=frozenset({token})))

    def get(path):
        status, body = asyncio.run(gate._asgi_get(app, path, {"authorization": f"Bearer {token}"}))
        return status, json.loads(body)

    report = gate.Report()
    gate.cross_door_order(report, gate.Api(get=get, label="in-process"), prefix="", fingerprint="")
    assert not report.failed and report.count(gate.PASS) == 5
