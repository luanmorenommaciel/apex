"""EngineStore.connect() must fail fast when the live schema is behind.

A ClickHouse volume only receives migrations on first init
(infra/docker-compose.yml mounts infra/sql as docker-entrypoint-initdb.d), so
two stores on the same commit of main can disagree on columns depending on
when their volume was created. Before this preflight, that surfaced mid
analyze() as a raw `Code: 47 ... Unknown expression or function identifier`
naming one column and nothing about the schema (issue #95).

These are unit tests against a fake client — no ClickHouse involved, real or
otherwise. Integration coverage against a real store lives in
test_integration_clickhouse.py and skips when infra is not up.
"""

from __future__ import annotations

import pytest

from apex_engine.clickhouse import (
    REQUIRED_SPARK_EVENTS_COLUMNS,
    EngineStore,
    SchemaOutOfDateError,
)


class FakeColumnsResult:
    def __init__(self, names: list[str]) -> None:
        self._names = names

    def named_results(self):
        return [{"name": name} for name in self._names]


class FakeSchemaClient:
    """Only implements what `_preflight_schema` calls: `query(...)`."""

    def __init__(self, columns: list[str]) -> None:
        self._columns = columns
        self.query_calls: list[tuple[str, dict]] = []

    def query(self, query, parameters):
        self.query_calls.append((query, parameters))
        return FakeColumnsResult(self._columns)


class FakeSettings:
    """Duck-types `ClickHouseSettings`: `.connect()` and `.database` only."""

    def __init__(self, client: FakeSchemaClient, database: str = "apex") -> None:
        self._client = client
        self.database = database

    def connect(self):
        return self._client


def test_connect_succeeds_when_schema_is_complete():
    client = FakeSchemaClient(sorted(REQUIRED_SPARK_EVENTS_COLUMNS))

    store = EngineStore.connect(FakeSettings(client))

    assert store.client is client
    # The preflight queried system.columns for the configured database.
    query, params = client.query_calls[0]
    assert "system.columns" in query
    assert params == {"database": "apex"}


def test_connect_succeeds_when_schema_has_extra_unknown_columns():
    """A newer, forward-compatible schema must not be rejected."""
    client = FakeSchemaClient([*REQUIRED_SPARK_EVENTS_COLUMNS, "some_future_column"])

    store = EngineStore.connect(FakeSettings(client))

    assert store.client is client


def test_connect_fails_fast_when_columns_are_missing():
    present = sorted(REQUIRED_SPARK_EVENTS_COLUMNS)[:-3]
    missing = sorted(set(REQUIRED_SPARK_EVENTS_COLUMNS) - set(present))
    client = FakeSchemaClient(present)

    with pytest.raises(SchemaOutOfDateError) as excinfo:
        EngineStore.connect(FakeSettings(client))

    error = excinfo.value
    assert error.database == "apex"
    assert error.missing_columns == frozenset(missing)
    message = str(error)
    assert "apex schema is behind" in message
    assert f"{len(missing)} column(s)" in message
    for name in missing:
        assert name in message
    assert "infra/scripts/apply_schema_migrations.ps1" in message


def test_connect_reports_every_missing_column_when_schema_is_empty():
    """An empty/absent table is the extreme case of "behind" — report all of it."""
    client = FakeSchemaClient([])

    with pytest.raises(SchemaOutOfDateError) as excinfo:
        EngineStore.connect(FakeSettings(client))

    assert excinfo.value.missing_columns == REQUIRED_SPARK_EVENTS_COLUMNS


def test_preflight_respects_the_configured_database():
    client = FakeSchemaClient(sorted(REQUIRED_SPARK_EVENTS_COLUMNS))

    EngineStore.connect(FakeSettings(client, database="apex_staging"))

    query, params = client.query_calls[0]
    assert params == {"database": "apex_staging"}


def test_preflight_does_not_swallow_connection_errors():
    """A failure to connect must surface as-is, not be hidden behind a schema
    error or silently degraded — this is not one of the optional reads."""

    class ExplodingSettings:
        database = "apex"

        def connect(self):
            raise ConnectionError("clickhouse unreachable")

    with pytest.raises(ConnectionError, match="clickhouse unreachable"):
        EngineStore.connect(ExplodingSettings())


def test_direct_construction_does_not_run_the_preflight():
    """`EngineStore(client)` stays preflight-free: fixtures and the fake-client
    unit suite construct it directly and must not need a schema to satisfy."""
    client = FakeSchemaClient([])  # would fail the preflight if it ran

    store = EngineStore(client)

    assert store.client is client
