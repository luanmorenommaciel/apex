"""The schema preflight and every read must target the SAME database.

`EngineStore.connect()` preflights `settings.database`, and `ClickHouseSettings
.connect()` opens the client with `database=settings.database`, so an
unqualified table name in a read resolves to that database. A literal `apex.`
prefix in the SQL bypasses that: `CLICKHOUSE_DATABASE=apex_staging` would pass
the preflight against apex_staging and then read `apex`.

The fake client below models that resolution rule (unqualified -> the client's
default database, qualified -> the qualifier), so the test fails on a hard-coded
`apex.` instead of only checking the parameter sent to system.columns. It is a
model of ClickHouse's name resolution, not ClickHouse: no server is involved.
"""

from __future__ import annotations

import re

import pytest

from apex_engine import clickhouse as ch
from apex_engine.clickhouse import REQUIRED_SPARK_EVENTS_COLUMNS, EngineStore
from apex_engine.crew import tools as crew_tools

READ_SQL = {
    "STAGE_EVENTS_SQL": ch.STAGE_EVENTS_SQL,
    "STAGE_AGGREGATES_SQL": ch.STAGE_AGGREGATES_SQL,
    "PLAN_TRANSITIONS_SQL": ch.PLAN_TRANSITIONS_SQL,
    "EXISTING_FINDINGS_SQL": ch.EXISTING_FINDINGS_SQL,
    "JOB_CONF_SQL": ch.JOB_CONF_SQL,
    "JOB_CONFS_SQL": ch.JOB_CONFS_SQL,
    "SHAPE_HISTORY_SQL": ch.SHAPE_HISTORY_SQL,
    **{f"crew:{name}": sql for name, sql in crew_tools.QUERIES.items()},
}

_TABLE_REF = re.compile(r"\b(?:FROM|JOIN)\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)?)", re.IGNORECASE)


def _strip_comments(sql: str) -> str:
    return "\n".join(line.split("--", 1)[0] for line in sql.splitlines())


def resolved_databases(sql: str, default_database: str) -> set[str]:
    """Database each table reference in `sql` resolves to, ClickHouse-style."""
    refs = _TABLE_REF.findall(_strip_comments(sql))
    return {ref.split(".", 1)[0] if "." in ref else default_database for ref in refs}


class DatabaseAwareClient:
    def __init__(self, database: str) -> None:
        self.database = database
        self.schema_databases: list[str] = []
        self.read_calls: list[tuple[str, set[str]]] = []

    def query(self, query, parameters):
        if "system.columns" in query:
            self.schema_databases.append(parameters["database"])
            rows = [{"name": name} for name in sorted(REQUIRED_SPARK_EVENTS_COLUMNS)]
        else:
            self.read_calls.append((query, resolved_databases(query, self.database)))
            rows = []
        return _Result(rows)


class _Result:
    def __init__(self, rows):
        self._rows = rows

    def named_results(self):
        return self._rows


class FakeSettings:
    def __init__(self, database: str) -> None:
        self.database = database
        self.client = DatabaseAwareClient(database)

    def connect(self):
        return self.client


def _run_every_read(store: EngineStore) -> None:
    store.stage_events("job-1")
    store.stage_aggregates("job-1")
    store.plan_transitions("job-1")
    store.job_conf("job-1")
    store.job_confs(["job-1"])
    store.shape_history(["fp"])
    store.existing_signatures("job-1")
    for name in crew_tools.QUERIES:
        crew_tools.run_named_query(store, name, "job-1", stage_id=1)


def test_the_fake_client_would_catch_a_hardcoded_apex_prefix():
    """Guards the guard: a qualified `apex.` must NOT follow the default database."""
    assert resolved_databases("SELECT 1 FROM apex.spark_events", "apex_staging") == {"apex"}
    assert resolved_databases("SELECT 1 FROM spark_events", "apex_staging") == {"apex_staging"}


@pytest.mark.parametrize("database", ["apex", "apex_staging"])
def test_preflight_and_every_read_target_the_selected_database(database):
    settings = FakeSettings(database)

    store = EngineStore.connect(settings)
    _run_every_read(store)

    client = settings.client
    assert client.schema_databases == [database]
    # 7 EngineStore reads + 3 Crew queries, none skipped.
    assert len(client.read_calls) == 10
    for sql, databases in client.read_calls:
        assert databases == {database}, f"read targets {databases}, not {database}: {sql.strip()[:80]}"


@pytest.mark.parametrize("name", sorted(READ_SQL))
def test_read_sql_names_tables_without_a_database_qualifier(name):
    refs = _TABLE_REF.findall(_strip_comments(READ_SQL[name]))

    assert refs, f"{name}: no table reference found, the check would be vacuous"
    assert all("." not in ref for ref in refs), f"{name} qualifies a table: {refs}"


@pytest.mark.parametrize("name", sorted(READ_SQL))
def test_the_database_is_never_interpolated_into_read_sql(name):
    assert "{database" not in READ_SQL[name]
    assert "%(database" not in READ_SQL[name]
    assert "{db" not in READ_SQL[name]


def test_reads_send_the_module_sql_unchanged():
    """No identifier rewriting between the constant and the client."""
    settings = FakeSettings("apex_staging")
    store = EngineStore.connect(settings)

    _run_every_read(store)

    sent = {sql for sql, _ in settings.client.read_calls}
    assert sent == set(READ_SQL.values())
