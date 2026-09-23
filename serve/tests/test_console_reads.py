"""The console's findings and transitions reads, and the database they run in.

Three regressions the resource tier shipped with, pinned here:

* ``/transitions`` served the MCP's per-UPDATE list, so an execution AQE
  re-planned kept its stale decisions on screen and the rows lacked the
  job_id / plan_fingerprint / ts the console's PlanTransitionRow reads.
* ``/findings`` served the MCP's FindingView: oldest first, no ts.
* Every statement hardcoded an ``apex.`` prefix, so CLICKHOUSE_DATABASE moved
  the session and the probes but not the queries.

The front's own SQL (``front/src/data/queries.ts``) is the contract for the
first two, so it is READ here rather than restated: a hand-kept copy would let
the two sides drift while every assertion still passed.
"""

from __future__ import annotations

import pathlib
import re
import sys
import types
from typing import Any

import pytest
from fastapi.testclient import TestClient

from apex_api.app import create_app
from apex_api.config import Settings, load_settings
from apex_mcp import ch
from apex_mcp.ch import ReadStore
from tests.conftest import FakeClient, finding_row, reads, transition_row

TOKEN = "test-token-6c1f9a"
SETTINGS = Settings(tokens=frozenset({TOKEN}))
AUTH = {"Authorization": f"Bearer {TOKEN}"}

QUERIES_TS = (
    pathlib.Path(__file__).resolve().parents[2] / "front" / "src" / "data" / "queries.ts"
)


def front_query(name: str) -> str:
    """The text of one ``export const NAME = `...`;`` in front's queries.ts."""
    source = QUERIES_TS.read_text()
    match = re.search(rf"export const {name} = `(.*?)`;", source, flags=re.DOTALL)
    assert match, f"front/src/data/queries.ts no longer exports {name}"
    return match.group(1)


def normalise(sql: str) -> str:
    """Comments and whitespace are not part of the contract; the text is."""
    no_comments = re.sub(r"--[^\n]*", "", sql)
    return re.sub(r"\s+", " ", no_comments).strip()


def select_names(sql: str) -> list[str]:
    """Output column names of the outermost SELECT, in order."""
    body = re.search(r"\bSELECT\b(.*?)\bFROM\b", normalise(sql), flags=re.DOTALL)
    assert body
    items: list[str] = []
    depth, current = 0, ""
    for char in body.group(1):
        depth += char == "("
        depth -= char == ")"
        if char == "," and depth == 0:
            items.append(current)
            current = ""
        else:
            current += char
    items.append(current)
    names = []
    for item in items:
        alias = re.search(r"\bAS\s+(\w+)\s*$", item.strip())
        names.append(alias.group(1) if alias else item.strip().split(".")[-1])
    return names


def build(client: Any) -> TestClient:
    return TestClient(create_app(store=ReadStore(client), settings=SETTINGS))


# -- transitions ------------------------------------------------------------


def test_console_transitions_sql_is_the_fronts_query():
    """Same statement, same latest-per-execution semantics — only the binding name differs."""
    mine = normalise(ch.CONSOLE_PLAN_TRANSITIONS_SQL)
    theirs = normalise(front_query("PLAN_TRANSITIONS")).replace("{job:String}", "{job_id:String}")
    assert mine == theirs


def test_console_transitions_take_the_latest_update_per_execution():
    """Structural pin: every non-key column is argMax'd on update_seq.

    Not executed against ClickHouse (no server in this lane). What it does
    prove is that no column can come from anything but the greatest update_seq
    of its execution, so a stale decision cannot survive next to its
    replacement.
    """
    sql = normalise(ch.CONSOLE_PLAN_TRANSITIONS_SQL)
    assert "GROUP BY t.job_id, t.execution_id" in sql
    for column in ("update_seq", "transition_type", "detail", "before", "after", "confidence"):
        assert f"argMax(t.{column}, t.update_seq) AS {column}" in sql, column
    # No transition column is projected bare, which GROUP BY would reject or,
    # worse, resolve to an arbitrary update.
    projected = sql.split("FROM plan_transitions")[0]
    assert not re.search(r"(?<!\()\bt\.(transition_type|detail|before|after)\b(?!,)\s*(,|$)", projected)


def test_transitions_route_serves_the_console_projection_not_every_update():
    """The route asks for the collapsed statement, and the rows carry the console's fields."""
    collapsed = dict(
        transition_row("coalesce_partitions", execution_id=1, update_seq=1),
        job_id="j",
        plan_fingerprint="a" * 64,
        ts="2026-09-20 10:00:00",
    )
    client = FakeClient(transitions={"j": [collapsed]})
    got = build(client).get("/v1/runs/j/transitions", headers=AUTH).json()

    assert [row["transition_type"] for row in got] == ["coalesce_partitions"]
    assert {
        "job_id", "execution_id", "update_seq", "transition_type", "detail",
        "before", "after", "confidence", "plan_fingerprint", "ts",
    } <= set(got[0])
    (sql, parameters), = [call for call in client.calls if reads(call[0], "plan_transitions")]
    assert sql == ch.CONSOLE_PLAN_TRANSITIONS_SQL
    assert parameters == {"job_id": "j"}


def test_the_mcp_transition_list_is_unchanged():
    """The diagnosis still reads every update; only the console's route collapses."""
    client = FakeClient(
        transitions={
            "j": [
                transition_row("skew_split", execution_id=1, update_seq=0),
                transition_row("coalesce_partitions", execution_id=1, update_seq=1),
            ]
        }
    )
    rows = ReadStore(client).plan_transitions("j")
    assert [row["transition_type"] for row in rows] == ["skew_split", "coalesce_partitions"]
    assert client.calls[-1][0] == ch.PLAN_TRANSITIONS_SQL


# -- findings ---------------------------------------------------------------

FINDING_ROW_FIELDS = [
    "finding_id", "job_id", "stage_id", "type", "severity", "confidence",
    "confidence_score", "detected_by", "evidence", "impact", "fix", "hot_key", "ts",
]


def test_console_findings_project_the_fronts_findingrow_fields():
    assert select_names(front_query("FINDINGS")) == FINDING_ROW_FIELDS
    assert select_names(ch._console_findings_sql(set(ch._FINDINGS_ADDITIVE))) == FINDING_ROW_FIELDS


@pytest.mark.parametrize("present", [set(ch._FINDINGS_ADDITIVE), set()], ids=["additive", "legacy"])
def test_console_findings_rank_on_the_raw_score_descending(present: set[str]):
    """The ordering the console's screens rely on, on a legacy table too."""
    sql = normalise(ch._console_findings_sql(present))
    assert "ORDER BY confidence_score DESC" in sql
    assert "ts ASC" not in sql  # the MCP's detection order is not the console's
    assert "FROM findings WHERE job_id = {job_id:String}" in sql
    if not present:
        assert "toFloat64(0) AS confidence_score" in sql


def test_findings_route_carries_ts_and_the_ranked_statement():
    rows = [
        dict(finding_row(job_id="j", finding_id="hi", confidence_score=0.9), ts="2026-09-20 10:00:00"),
        dict(finding_row(job_id="j", finding_id="lo", confidence_score=0.2), ts="2026-09-20 10:05:00"),
    ]
    client = FakeClient(findings={"j": rows})
    got = build(client).get("/v1/runs/j/findings", headers=AUTH).json()

    assert [row["finding_id"] for row in got] == ["hi", "lo"]
    assert all(set(FINDING_ROW_FIELDS) <= set(row) for row in got)
    assert got[0]["ts"] == "2026-09-20 10:00:00"
    sql = [q for q, _ in client.calls if reads(q, "findings")][-1]
    assert "ORDER BY confidence_score DESC" in normalise(sql)


def test_the_mcp_findings_read_keeps_its_detection_order():
    client = FakeClient(findings={"j": [finding_row(job_id="j")]})
    ReadStore(client).findings("j")
    sql = [q for q, _ in client.calls if reads(q, "findings")][-1]
    assert "ORDER BY ts ASC, finding_id ASC" in normalise(sql)


# -- the configured database ------------------------------------------------


def all_sql() -> list[tuple[str, str]]:
    """Every statement text this module can issue, by name."""
    statements = [
        (name, value)
        for name, value in vars(ch).items()
        if name.endswith("_SQL") and isinstance(value, str)
    ]
    additive = set(ch._FINDINGS_ADDITIVE)
    statements += [
        ("findings(all)", ch._findings_sql(additive)),
        ("findings(legacy)", ch._findings_sql(set())),
        ("console_findings(all)", ch._console_findings_sql(additive)),
        ("console_findings(legacy)", ch._console_findings_sql(set())),
        ("findings_search", ch._findings_search_sql(["t0", "t1"])),
        ("plans_search", ch._plans_search_sql(["t0", "t1"])),
    ]
    return statements


def test_no_statement_names_a_database():
    """Tables are unqualified, so the session database is the only selector.

    A ``db.table`` reference would ignore CLICKHOUSE_DATABASE for that
    statement. ``system.*`` is the one legitimate qualifier: the probes read
    ClickHouse's own catalogue and bind the target database as a PARAMETER.
    """
    statements = all_sql()
    assert len(statements) > 20
    for name, sql in statements:
        qualified = re.findall(r"\b(?:FROM|JOIN)\s+(\w+)\.\w+", sql)
        assert set(qualified) <= {"system"}, f"{name} qualifies a table with {qualified}"
        assert not re.search(r"\bapex\.", sql), f"{name} hardcodes the apex database"


def test_settings_read_the_configured_database():
    env = {"APEX_API_TOKENS": TOKEN, "CLICKHOUSE_DATABASE": "apex_staging"}
    assert load_settings(env).database == "apex_staging"
    assert load_settings({"APEX_API_TOKENS": TOKEN}).database == "apex"
    # Blank is unset, not a database named "".
    assert load_settings({"APEX_API_TOKENS": TOKEN, "CLICKHOUSE_DATABASE": "  "}).database == "apex"


def test_the_api_store_is_built_on_the_configured_database(monkeypatch: pytest.MonkeyPatch):
    """Settings reach ReadStore: its catalogue probes look in the SAME database."""
    client = FakeClient(findings={"j": [finding_row(job_id="j")]})
    monkeypatch.setattr(ch, "get_client", lambda: client)

    app = create_app(settings=Settings(tokens=frozenset({TOKEN}), database="apex_staging"))
    assert app.state.store._database == "apex_staging"  # noqa: SLF001

    assert TestClient(app).get("/v1/runs/j/findings", headers=AUTH).status_code == 200
    probes = [params for q, params in client.calls if "system.columns" in q]
    assert probes == [{"database": "apex_staging", "table": "findings"}]
    # And nothing it ran carried a database name of its own.
    assert not any(re.search(r"\bapex\w*\.", q) for q, _ in client.calls)


def test_the_session_database_comes_from_the_same_variable(monkeypatch: pytest.MonkeyPatch):
    """get_client opens the session on CLICKHOUSE_DATABASE; get_store probes it."""
    opened: dict[str, Any] = {}

    def get_client(**kwargs: Any) -> str:
        opened.update(kwargs)
        return "client"

    monkeypatch.setitem(sys.modules, "clickhouse_connect", types.SimpleNamespace(get_client=get_client))
    monkeypatch.setenv("CLICKHOUSE_DATABASE", "apex_staging")
    ch.get_client.cache_clear()
    try:
        store = ch.get_store()
    finally:
        ch.get_client.cache_clear()

    assert opened["database"] == "apex_staging"
    assert store._database == "apex_staging"  # noqa: SLF001

    monkeypatch.delenv("CLICKHOUSE_DATABASE")
    assert ch.configured_database() == "apex"


def test_probes_and_messages_name_the_configured_database(caplog: pytest.LogCaptureFixture):
    client = FakeClient(columns=["finding_id", "job_id"])
    store = ReadStore(client, database="apex_staging")
    with caplog.at_level("WARNING", logger="apex_mcp.ch"):
        store.findings_columns()
    assert "apex_staging.findings is missing" in caplog.text
    assert client.calls[0][1] == {"database": "apex_staging", "table": "findings"}
