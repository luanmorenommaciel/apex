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
import struct
import sys
from types import SimpleNamespace

import pytest

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
    assert "ORDER BY b.started_at DESC LIMIT {limit:UInt32}" in statements["RUN_LIST"]
    assert "WHERE job_id" not in statements["RUN_LIST"].split("shapes AS")[0].split("f AS")[0]
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
    assert verdicts[f"{gate.TIE_BREAK} · api"] == gate.SKIP
    assert report.count(gate.SKIP) == 4 and not report.failed


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


# --------------------------------------------------------------------------
# The tie-break: confidence_score DESC, finding_id ASC
#
# Nothing below executes SQL. seed() and remove() write to an inert client that
# only records; every door is a controlled response.
# --------------------------------------------------------------------------
WIRE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}$")
TS = "2026-09-20T10:00:00.123"


class _Capture:
    """A client that records what it is handed and runs nothing."""

    def __init__(self, *, rollup_exists=False):
        self.inserts, self.commands = [], []
        self.queries, self.command_settings = [], []
        self.rollup_exists = rollup_exists

    def insert(self, table, rows, column_names):
        self.inserts.append((table, [list(row) for row in rows], list(column_names)))

    def command(self, sql, settings=None):
        self.commands.append(sql)
        self.command_settings.append(settings)

    def query(self, sql):
        self.queries.append(sql)
        return SimpleNamespace(result_rows=[[int(self.rollup_exists)]])


def test_cleanup_retracts_only_its_job_ids_from_the_optional_rollup():
    fx = gate.new_fixture()
    client = _Capture(rollup_exists=True)
    gate.remove(client, fx)
    assert client.queries == ["EXISTS TABLE spark_jobs_1m"]
    rollup = [sql for sql in client.commands if sql.startswith("ALTER TABLE spark_jobs_1m ")]
    assert rollup == [
        "ALTER TABLE spark_jobs_1m DELETE WHERE job_id IN "
        f"('{fx.indexed}', '{fx.baseline}', '{fx.unindexed}')"
    ]
    assert all(settings == {"mutations_sync": 1} for settings in client.command_settings)
    assert not any("LIKE" in sql or "TRUNCATE" in sql for sql in client.commands)


def test_cleanup_still_works_when_the_optional_rollup_is_absent():
    client = _Capture(rollup_exists=False)
    gate.remove(client, gate.new_fixture())
    assert client.queries == ["EXISTS TABLE spark_jobs_1m"]
    assert len(client.commands) == 7
    assert not any("spark_jobs_1m" in sql for sql in client.commands)


def test_a_failed_rollup_lookup_is_not_treated_as_an_absent_table(monkeypatch):
    client = _Capture()

    def failed_lookup(_sql):
        raise RuntimeError("store unavailable")

    monkeypatch.setattr(client, "query", failed_lookup)
    with pytest.raises(RuntimeError, match="store unavailable"):
        gate.remove(client, gate.new_fixture())
    assert client.commands == [], "the lookup failed before any cleanup mutation"


def _quiet_store(_store, sql, _params):
    """Every live-only probe answered so that only the findings checks can fail."""
    if "FROM run_outcomes" in sql:
        return [{"count()": 1}]
    if "getSetting" in sql:
        return [{"readonly": 1}]
    if "uniqExact(execution_id)" in sql:
        return [{"n": 1}]
    if "FROM plan_transitions" in sql:
        return [{"count()": 1}]
    return []


def _finding(finding_id, score, ts=TS):
    return {"finding_id": finding_id, "confidence_score": score, "ts": ts}


def _verdicts(report):
    return {name: (verdict, detail) for verdict, name, detail in report.lines}


def _timestamp_report(monkeypatch, rows):
    monkeypatch.setattr(gate, "browser_query", _quiet_store)
    report = gate.Report()
    gate.live_only(report, gate.Store("h", 1, "apex", "apex", "", "apex_ro", ""),
                   gate.Api(get=lambda path: (200, {}), label="fake"), {"RUN_ONE": ""}, WIRE,
                   {"findings": rows, "transitions": []}, job="j", unindexed_job=None)
    return _verdicts(report)


def test_an_invalid_timestamp_type_is_named_without_conversion(monkeypatch):
    for bad in (None, 7, [], {}):
        rows = [_finding("hi", 0.9, bad), _finding("lo", 0.2)]
        before = json.dumps(rows)
        verdicts = _timestamp_report(monkeypatch, rows)
        verdict, detail = verdicts["findings ordered by confidence_score"]
        assert verdict == gate.FAIL
        assert "hi" in detail and type(bad).__name__ in detail and repr(bad) in detail
        assert verdicts["timestamps in the wire format"][0] == gate.FAIL
        assert verdicts[f"{gate.TIE_BREAK} · api"][0] == gate.SKIP
        assert json.dumps(rows) == before, "diagnosis must not rewrite the timestamp"


def test_a_malformed_timestamp_string_is_not_used_to_establish_order(monkeypatch):
    for bad in ("", "2026-09-20 10:00:00.123"):
        verdicts = _timestamp_report(monkeypatch, [_finding("hi", 0.9, bad), _finding("lo", 0.2)])
        verdict, detail = verdicts["findings ordered by confidence_score"]
        assert verdict == gate.FAIL
        assert "hi" in detail and repr(bad) in detail
        assert verdicts["timestamps in the wire format"][0] == gate.FAIL


def test_one_invalid_timestamp_is_a_defect_not_an_unexercised_order(monkeypatch):
    verdicts = _timestamp_report(monkeypatch, [_finding("single", 0.9, None)])
    assert verdicts["findings ordered by confidence_score"][0] == gate.FAIL
    assert verdicts[f"{gate.TIE_BREAK} · api"][0] == gate.SKIP


def test_the_seed_ties_two_findings_inserted_against_the_canonical_order():
    fx = gate.new_fixture()
    client = _Capture()
    gate.seed(client, fx)
    assert client.commands == [], "seeding inserts; it issues no statement"

    (columns, rows), = [(c, r) for table, r, c in client.inserts if table == "findings"]
    findings = [dict(zip(columns, row)) for row in rows]
    by_id = {f["finding_id"]: f for f in findings}
    first, second = by_id[fx.finding_tie_first], by_id[fx.finding_tie_second]

    # Tied on everything the score and the table's ORDER BY could decide by.
    for column in ("confidence_score", "ts", "severity", "job_id"):
        assert first[column] == second[column], column
    # ... and still tied once ClickHouse stores the score as a Float32.
    as_float32 = lambda v: struct.unpack("f", struct.pack("f", v))[0]  # noqa: E731
    assert as_float32(first["confidence_score"]) == as_float32(second["confidence_score"])
    # finding_id ASC puts -a- first; the fixture inserts -b- first.
    assert fx.finding_tie_first < fx.finding_tie_second
    order = [f["finding_id"] for f in findings]
    assert order.index(fx.finding_tie_second) < order.index(fx.finding_tie_first)
    assert len(set(order)) == len(order)

    # What was there before is still there: the score/ts disagreement ...
    high, low = by_id[fx.finding_high], by_id[fx.finding_low]
    assert (high["confidence_score"], low["confidence_score"]) == (0.9, 0.2)
    assert low["ts"] < high["ts"]
    # ... the verification hangs off finding_high ...
    (vcols, vrows), = [(c, r) for table, r, c in client.inserts if table == "fix_verifications"]
    assert [dict(zip(vcols, row))["finding_id"] for row in vrows] == [fx.finding_high]
    # ... and the cleanup still reaches every row, by the same three job ids.
    assert fx.job_ids == [fx.indexed, fx.baseline, fx.unindexed]
    assert {f["job_id"] for f in findings} <= set(fx.job_ids)
    # The run_outcomes rows count the findings the fixture seeds for each run.
    (ocols, orows), = [(c, r) for table, r, c in client.inserts if table == "run_outcomes"]
    for outcome in (dict(zip(ocols, row)) for row in orows):
        seeded = sum(1 for f in findings if f["job_id"] == outcome["job_id"])
        assert outcome["finding_count"] == seeded, outcome["job_id"]
    assert seeded_for(fx.indexed, findings) == 4
    gate.remove(client, fx)
    findings_delete = [sql for sql in client.commands if sql.startswith("ALTER TABLE findings ")]
    assert findings_delete == [
        "ALTER TABLE findings DELETE WHERE job_id IN "
        f"('{fx.indexed}', '{fx.baseline}', '{fx.unindexed}')"
    ]


def seeded_for(job, findings):
    return sum(1 for f in findings if f["job_id"] == job)


def test_a_score_of_the_wrong_type_is_named_not_raised_by_the_live_checks(monkeypatch):
    """0.5 beside '0.5', ts reversed: the primary check reached sorted() over
    the scores and raised TypeError before the tie-break could report. Both
    checks now FAIL and name the value; neither converts it."""
    monkeypatch.setattr(gate, "browser_query", _quiet_store)
    report = gate.Report()
    seen = {"findings": [_finding("b", 0.5, "2026-09-20T11:00:00.123"),
                         _finding("a", "0.5", "2026-09-20T10:00:00.123")],
            "transitions": []}
    gate.live_only(report, gate.Store("h", 1, "apex", "apex", "", "apex_ro", ""),
                   gate.Api(get=lambda path: (200, {}), label="fake"), {"RUN_ONE": ""}, WIRE,
                   seen, job="j", unindexed_job=None)
    verdicts = _verdicts(report)
    primary = verdicts["findings ordered by confidence_score"]
    assert primary[0] == gate.FAIL and "str '0.5'" in primary[1]
    tie = verdicts[f"{gate.TIE_BREAK} · api"]
    assert tie[0] == gate.FAIL and "str '0.5'" in tie[1]
    # The checks after them still ran.
    assert verdicts["timestamps in the wire format"][0] == gate.PASS


def test_the_canonical_tie_break_passes():
    rows = [_finding("hi", 0.9), _finding("a", 0.5), _finding("b", 0.5), _finding("lo", 0.2)]
    verdict, detail = gate.tie_break(rows)
    assert verdict == gate.PASS and "['a', 'b']" in detail


def test_tied_findings_with_reversed_ids_fail():
    rows = [_finding("hi", 0.9), _finding("b", 0.5), _finding("a", 0.5), _finding("lo", 0.2)]
    verdict, detail = gate.tie_break(rows)
    assert verdict == gate.FAIL
    assert "[1] is 'b'" in detail and "puts 'a'" in detail


def test_without_a_tie_the_tie_break_is_not_exercised():
    for rows in (None, [], [_finding("a", 0.5)], [_finding("b", 0.9), _finding("a", 0.5)]):
        verdict, _ = gate.tie_break(rows)
        assert verdict == gate.SKIP, rows


def test_a_legacy_zero_score_still_needs_its_tie_break():
    """A store without the v0.2 column reads every score as 0: one big tie,
    which finding_id alone orders. Nothing is inferred from the zeros."""
    assert gate.tie_break([_finding("a", 0.0), _finding("b", 0.0)])[0] == gate.PASS
    assert gate.tie_break([_finding("b", 0), _finding("a", 0)])[0] == gate.FAIL


def test_an_unreadable_finding_is_named_not_raised_and_not_guessed():
    no_id = gate.tie_break([{"confidence_score": 0.5, "ts": TS}, _finding("a", 0.5)])
    assert no_id[0] == gate.FAIL and "[0] carries no finding_id" in no_id[1]
    # A missing score is not taken to be the column default.
    no_score = gate.tie_break([{"finding_id": "a", "ts": TS}, _finding("b", 0.0)])
    assert no_score[0] == gate.FAIL and "[0] carries no confidence_score" in no_score[1]
    # A type the console does not declare is named, not compared.
    as_text = gate.tie_break([_finding("a", "0.5"), _finding("b", "0.5")])
    assert as_text[0] == gate.FAIL and "str '0.5'" in as_text[1]
    numeric_id = gate.tie_break([_finding(2, 0.5), _finding(1, 0.5)])
    assert numeric_id[0] == gate.FAIL and "not a String" in numeric_id[1]
    assert gate.tie_break({"finding_id": "a"})[0] == gate.FAIL


def test_a_tied_finding_without_an_id_fails_through_the_live_checks(monkeypatch):
    """The primary order check met it as a KeyError; now both checks report."""
    monkeypatch.setattr(gate, "browser_query", _quiet_store)
    report = gate.Report()
    seen = {"findings": [{"confidence_score": 0.5, "ts": TS}, _finding("a", 0.5)], "transitions": []}
    gate.live_only(report, gate.Store("h", 1, "apex", "apex", "", "apex_ro", ""),
                   gate.Api(get=lambda path: (200, {}), label="fake"), {"RUN_ONE": ""}, WIRE,
                   seen, job="j", unindexed_job=None)
    verdict, detail = _verdicts(report)[f"{gate.TIE_BREAK} · api"]
    assert verdict == gate.FAIL and "no finding_id" in detail


def _two_doors(monkeypatch, browser_rows, api_rows, *, seeded_tie=False):
    """compare_doors and live_only on findings, each door answering as given."""

    def browser(store, sql, params):
        if "FROM findings" in sql:
            return [dict(row) for row in browser_rows]
        return _quiet_store(store, sql, params)

    monkeypatch.setattr(gate, "browser_query", browser)
    store = gate.Store("h", 1, "apex", "apex", "", "apex_ro", "")
    api = gate.Api(get=lambda path: (200, [dict(row) for row in api_rows]), label="fake")
    statements = gate.console_statements(gate.QUERIES_TS.read_text())
    report, browser_seen = gate.Report(), {}
    seen = gate.compare_doors(report, store, api, statements, "j", "", "",
                              only={"findings"}, browser_seen=browser_seen)
    gate.live_only(report, store, api, statements, WIRE, seen, job="j", unindexed_job=None,
                   browser_seen=browser_seen, seeded_tie=seeded_tie)
    return report


CANONICAL = [_finding("hi", 0.9, "2026-09-20T10:05:00.123"), _finding("a", 0.5), _finding("b", 0.5),
             _finding("lo", 0.2, "2026-09-20T09:00:00.123")]
REVERSED = [CANONICAL[0], CANONICAL[2], CANONICAL[1], CANONICAL[3]]


def test_two_doors_right_the_same_way_pass(monkeypatch):
    """Positive control: canonical rows through both doors fail nothing."""
    report = _two_doors(monkeypatch, CANONICAL, CANONICAL)
    verdicts = _verdicts(report)
    assert verdicts["findings  [FINDINGS]"][0] == gate.PASS
    assert verdicts["findings ordered by confidence_score"][0] == gate.PASS
    assert not report.failed
    assert all(verdict == gate.PASS for verdict, name, _ in report.lines if name.startswith(gate.TIE_BREAK))


def test_two_doors_wrong_the_same_way_fail_though_parity_passes(monkeypatch):
    report = _two_doors(monkeypatch, REVERSED, REVERSED)
    verdicts = _verdicts(report)
    # The doors agree, and the score order is right: the existing checks pass ...
    assert verdicts["findings  [FINDINGS]"][0] == gate.PASS
    assert verdicts["findings ordered by confidence_score"][0] == gate.PASS
    # ... and the tie-break fails on each door all the same.
    assert verdicts[f"{gate.TIE_BREAK} · api"][0] == gate.FAIL
    assert verdicts[f"{gate.TIE_BREAK} · browser"][0] == gate.FAIL
    assert report.failed


def test_one_door_wrong_is_named_by_door(monkeypatch):
    report = _two_doors(monkeypatch, REVERSED, CANONICAL)
    verdicts = _verdicts(report)
    assert verdicts["findings  [FINDINGS]"][0] == gate.FAIL
    assert verdicts[f"{gate.TIE_BREAK} · browser"][0] == gate.FAIL
    assert verdicts[f"{gate.TIE_BREAK} · api"][0] == gate.PASS


def test_a_seeded_tie_the_doors_did_not_return_fails(monkeypatch):
    """With --job-id a run may have no tie; the seeded fixture always has one."""
    untied = [CANONICAL[0], CANONICAL[1], CANONICAL[3]]
    assert all(verdict != gate.FAIL for verdict, name, _ in _two_doors(monkeypatch, untied, untied).lines
               if name.startswith(gate.TIE_BREAK))
    report = _two_doors(monkeypatch, untied, untied, seeded_tie=True)
    verdict, detail = _verdicts(report)[f"{gate.TIE_BREAK} · api"]
    assert verdict == gate.FAIL and "seeded two tied findings" in detail


def _http_findings_gate(monkeypatch, payload, *, browser_rows=None, valid_preflight=False,
                        invalid_preflight_only=False, first_findings=None, selected_findings=None):
    """Exercise main's RC through actual comparison/diagnosis, with HTTP 200
    responses supplied by a controlled API door and no store or network."""
    report = gate.Report()
    monkeypatch.setattr(gate, "Report", lambda: report)
    finding_reads = 0

    def get(path):
        nonlocal finding_reads
        if path.endswith("/findings"):
            finding_reads += 1
            if first_findings is not None and finding_reads == 1:
                return 200, first_findings
            if valid_preflight and finding_reads == 1:
                return 200, CANONICAL
            if invalid_preflight_only and finding_reads > 1:
                return 200, CANONICAL
            return 200, payload
        return 200, {"job_id": "j"}

    api = gate.Api(get=get, label="controlled HTTP 200")
    monkeypatch.setattr(gate, "remote_api", lambda _url, _token: api)

    def browser(store, sql, params):
        if "FROM findings" in sql:
            return CANONICAL if browser_rows is None else browser_rows
        return _quiet_store(store, sql, params)

    monkeypatch.setattr(gate, "browser_query", browser)
    compare = gate.compare_doors

    def findings_only(*args, **kwargs):
        if selected_findings is not None:
            selected_findings.append(args[6])
        seen = compare(*args, **kwargs, only={"findings"})
        # A separate valid payload lets subsequent checks prove they ran.
        seen["transitions"] = [{"execution_id": 1, "update_seq": 0, "ts": TS}]
        return seen

    monkeypatch.setattr(gate, "compare_doors", findings_only)
    rc = gate.main(["--job-id", "j", "--api-url", "http://controlled.invalid", "--api-token", "test"])
    return rc, _verdicts(report)


@pytest.mark.parametrize(
    "payload",
    [{"finding_id": "object", "confidence_score": 0.5, "ts": TS}, {}, None, "not a list", ""],
    ids=["dict", "empty-dict", "null", "string", "empty-string"],
)
def test_http_200_findings_with_a_non_list_payload_fail_without_coercion(monkeypatch, payload):
    before = json.dumps(payload)
    rc, verdicts = _http_findings_gate(monkeypatch, payload)
    assert rc == 1
    assert verdicts["findings  [FINDINGS]"][0] == gate.FAIL
    for name in ("findings ordered by confidence_score", f"{gate.TIE_BREAK} · api"):
        verdict, detail = verdicts[name]
        assert verdict == gate.FAIL
        assert type(payload).__name__ in detail and "not a list" in detail
    assert verdicts["one transition per execution"][0] == gate.SKIP
    assert verdicts["timestamps in the wire format"][0] == gate.PASS
    assert json.dumps(payload) == before, "diagnosis must not coerce the HTTP payload"


def test_http_200_findings_with_a_valid_list_keep_the_gate_success(monkeypatch):
    before = json.dumps(CANONICAL)
    rc, verdicts = _http_findings_gate(monkeypatch, CANONICAL)
    assert rc == 0
    assert verdicts["findings  [FINDINGS]"][0] == gate.PASS
    assert verdicts["findings ordered by confidence_score"][0] == gate.PASS
    assert verdicts[f"{gate.TIE_BREAK} · api"][0] == gate.PASS
    assert verdicts[f"{gate.TIE_BREAK} · browser"][0] == gate.PASS
    assert verdicts["timestamps in the wire format"][0] == gate.PASS
    assert json.dumps(CANONICAL) == before


@pytest.mark.parametrize("door", ["api", "browser", "both"])
@pytest.mark.parametrize("phase", ["first", "later"])
@pytest.mark.parametrize(
    "rows,bad_index,bad_type",
    [([1, 2], 0, "int"), (["ts", "finding_id"], 0, "str"),
     ([CANONICAL[0], None], 1, "NoneType"), ([[]], 0, "list"), ([7], 0, "int")],
    ids=["ints", "strings", "mixed-null", "nested-list", "single-int"],
)
def test_findings_non_row_items_fail_by_door_index_and_type(monkeypatch, capsys, door, phase,
                                                           rows, bad_index, bad_type):
    api_rows = rows if door in ("api", "both") else CANONICAL
    browser_rows = rows if door in ("browser", "both") else CANONICAL
    before = json.dumps([api_rows, browser_rows])
    rc, verdicts = _http_findings_gate(monkeypatch, api_rows, browser_rows=browser_rows,
                                      valid_preflight=phase == "later")
    assert rc == 1
    primary_verdict, primary_detail = verdicts["findings ordered by confidence_score"]
    assert primary_verdict == gate.FAIL
    for affected in ("api", "browser") if door == "both" else (door,):
        assert f"{affected}[{bad_index}] is {bad_type}" in primary_detail
        verdict, detail = verdicts[f"{gate.TIE_BREAK} · {affected}"]
        assert verdict == gate.FAIL
        assert f"{affected}[{bad_index}] is {bad_type}" in detail
    assert verdicts["one transition per execution"][0] == gate.SKIP
    assert verdicts["timestamps in the wire format"][0] == gate.PASS
    assert json.dumps([api_rows, browser_rows]) == before
    output = capsys.readouterr()
    assert "CONSOLE_PARITY_GATE=FAIL" in output.out
    assert "Traceback" not in output.out + output.err


@pytest.mark.parametrize("rows", [[1, 2], ["ts", "finding_id"], [CANONICAL[0], None], [[]], [7]],
                         ids=["ints", "strings", "mixed-null", "nested-list", "single-int"])
def test_an_invalid_first_findings_response_is_not_hidden_by_a_valid_second_one(monkeypatch, capsys, rows):
    before = json.dumps(rows)
    rc, verdicts = _http_findings_gate(monkeypatch, rows, invalid_preflight_only=True)
    assert rc == 1
    verdict, detail = verdicts["findings for verification selection"]
    assert verdict == gate.FAIL and "api[" in detail and "not a row" in detail
    assert verdicts["findings ordered by confidence_score"][0] == gate.PASS
    assert verdicts["timestamps in the wire format"][0] == gate.PASS
    assert json.dumps(rows) == before
    output = capsys.readouterr()
    assert "CONSOLE_PARITY_GATE=FAIL" in output.out
    assert "Traceback" not in output.out + output.err


def test_empty_findings_lists_keep_the_checks_not_exercised(monkeypatch):
    rc, verdicts = _http_findings_gate(monkeypatch, [], browser_rows=[])
    assert rc == 0
    for name in ("findings ordered by confidence_score", f"{gate.TIE_BREAK} · api",
                 f"{gate.TIE_BREAK} · browser"):
        assert verdicts[name][0] == gate.SKIP


def test_incomplete_findings_rows_keep_the_missing_column_diagnosis(monkeypatch):
    rows = [{"finding_id": "a", "confidence_score": 0.9},
            {"finding_id": "b", "confidence_score": 0.2}]
    before = json.dumps(rows)
    rc, verdicts = _http_findings_gate(monkeypatch, rows, browser_rows=rows)
    assert rc == 1
    verdict, detail = verdicts["findings ordered by confidence_score"]
    assert verdict == gate.FAIL and "no ts" in detail
    assert "not a row" not in detail
    assert verdicts["one transition per execution"][0] == gate.SKIP
    assert verdicts["timestamps in the wire format"][0] == gate.PASS
    assert json.dumps(rows) == before


@pytest.mark.parametrize(
    "finding_id",
    [None, 7, 0.5, True, ["private-finding-id"], {"private-finding-id": "secret"}],
    ids=["null", "int", "float", "bool", "list", "dict"],
)
def test_first_finding_id_with_wrong_type_fails_without_value_disclosure(monkeypatch, capsys, finding_id):
    first = [{"finding_id": finding_id}]
    before = json.dumps(first)
    selected = []
    rc, verdicts = _http_findings_gate(monkeypatch, CANONICAL, first_findings=first,
                                      selected_findings=selected)
    assert rc == 1
    verdict, detail = verdicts["findings for verification selection"]
    assert verdict == gate.FAIL
    assert detail == f"api[0].finding_id is {type(finding_id).__name__}, not a String"
    assert selected == [""], "an invalid ID cannot select a verification"
    assert verdicts["findings ordered by confidence_score"][0] == gate.PASS
    assert verdicts["one transition per execution"][0] == gate.SKIP
    assert verdicts["timestamps in the wire format"][0] == gate.PASS
    assert json.dumps(first) == before
    output = capsys.readouterr()
    assert "CONSOLE_PARITY_GATE=FAIL" in output.out
    assert "Traceback" not in output.out + output.err
    assert "private-finding-id" not in output.out + output.err
    assert "secret" not in output.out + output.err


@pytest.mark.parametrize(
    "first,selected_id",
    [([{"finding_id": "regular-id"}], "regular-id"), ([{"finding_id": ""}], ""),
     ([], ""), ([{}], "")],
    ids=["string", "empty-string", "empty-list", "missing-field"],
)
def test_first_finding_id_compatible_cases_keep_selection(monkeypatch, first, selected_id):
    before = json.dumps(first)
    selected = []
    rc, verdicts = _http_findings_gate(monkeypatch, CANONICAL, first_findings=first,
                                      selected_findings=selected)
    assert rc == 0
    assert "findings for verification selection" not in verdicts
    assert selected == [selected_id]
    assert verdicts["findings ordered by confidence_score"][0] == gate.PASS
    assert verdicts["timestamps in the wire format"][0] == gate.PASS
    assert json.dumps(first) == before
