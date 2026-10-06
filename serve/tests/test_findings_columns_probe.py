"""findings_columns: a failed probe is an error, never an empty cached column set.

ReadStore probes apex.findings' columns once so the v0.2 additive columns can be
served as defaults on a cluster whose ALTER has not landed. A probe that ANSWERS
with a subset is that older deployment. A probe that FAILS says nothing about
the columns; caching it as an empty set served defaults for every additive
column for the life of the process, even after the store answered again.

Failures are the driver's real exception classes, built as clickhouse-connect's
build_http_error builds them. No ClickHouse runs. Access denied (497) on the
metadata read is included on purpose: it is an error like the others, not a
signal to serve defaults. A deployment where only system.columns is denied is a
hypothesis here, not a reproduced case.
"""

from __future__ import annotations

import pytest
from clickhouse_connect.driver.exceptions import DatabaseError, OperationalError

from apex_mcp.ch import ApexStoreError, ReadStore
from tests.conftest import FakeResult

MARKER = "SYNTH-SENSITIVE-4c1d"
URL = f"http://apex:{MARKER}@db.internal.example:8123"

ALL_COLUMNS = [
    "finding_id", "job_id", "app_id", "stage_id", "type", "severity", "evidence",
    "hot_key", "impact", "fix", "confidence", "confidence_score", "detected_by", "ts",
]
PRE_V02_COLUMNS = [c for c in ALL_COLUMNS if c not in ("app_id", "confidence_score")]


def _server_error(code: int | None) -> DatabaseError:
    return DatabaseError(
        f"Received ClickHouse exception, code: {code}, server response: "
        f"Code: {code}. DB::Exception: {MARKER} (for url {URL})",
        code=code,
    )


FAILURES = {
    "connection refused": (OperationalError(f"Connection refused to {URL}"), "clickhouse_unavailable"),
    "authentication 516": (_server_error(516), "clickhouse_access_denied"),
    "access denied 497": (_server_error(497), "clickhouse_access_denied"),
    "unknown database 81": (_server_error(81), "clickhouse_database_missing"),
    "memory limit 241": (_server_error(241), "clickhouse_query_failed"),
    "no server code": (DatabaseError(f"HTTP driver received HTTP status 502 ({URL})", code=None), "clickhouse_query_failed"),
}


class ColumnsStore:
    """Answers the findings column probe after failing the first `fail_probes`."""

    def __init__(self, failure: Exception | None = None, *, fail_probes: int = 0, columns: list[str] = ALL_COLUMNS) -> None:
        self.failure = failure
        self.fail_probes = fail_probes
        self.columns = columns
        self.probe_calls = 0
        self.findings_sql: list[str] = []

    def query(self, query: str, parameters: dict | None = None) -> FakeResult:
        if "system.columns" in query:
            self.probe_calls += 1
            if self.probe_calls <= self.fail_probes:
                raise self.failure
            return FakeResult([{"name": name} for name in self.columns])
        self.findings_sql.append(query)
        return FakeResult([])


@pytest.mark.parametrize("failure", sorted(FAILURES))
def test_a_failed_column_probe_raises_and_serves_no_defaults(failure):
    """B-1, B-4 — the read fails with the sanitized category; no findings query
    runs on a guessed column set."""
    exc, prefix = FAILURES[failure]
    client = ColumnsStore(exc, fail_probes=1)
    store = ReadStore(client)

    with pytest.raises(ApexStoreError) as caught:
        store.findings("job-1")

    message = str(caught.value)
    assert message.split(":")[0] == prefix
    for fragment in (MARKER, "db.internal.example", "8123", "DB::Exception"):
        assert fragment not in message
    assert client.findings_sql == []


@pytest.mark.parametrize("failure", sorted(FAILURES))
def test_the_same_store_recovers_the_real_columns_after_a_failed_probe(failure):
    """B-2 — nothing was cached, so the next call probes again and the real
    additive columns are read, not their defaults."""
    exc, _ = FAILURES[failure]
    client = ColumnsStore(exc, fail_probes=1)
    store = ReadStore(client)
    with pytest.raises(ApexStoreError):
        store.findings_columns()

    assert store.findings_columns() == set(ALL_COLUMNS)
    store.findings("job-1")
    assert client.probe_calls == 2
    assert "'' AS app_id" not in client.findings_sql[-1]
    assert "toFloat64(0) AS confidence_score" not in client.findings_sql[-1]
    # The recovered answer is the one cached.
    store.findings("job-1")
    assert client.probe_calls == 2


def test_an_older_deployment_still_serves_defaults_for_its_missing_columns(caplog):
    """B-3 — a probe that ANSWERS without the additive columns is the pre-v0.2
    contract: defaults, a warning, and the answer cached."""
    client = ColumnsStore(columns=PRE_V02_COLUMNS)
    store = ReadStore(client)

    with caplog.at_level("WARNING", logger="apex_mcp.ch"):
        store.findings("job-1")
        store.findings("job-1")

    assert client.probe_calls == 1
    assert "'' AS app_id" in client.findings_sql[-1]
    assert "toFloat64(0) AS confidence_score" in client.findings_sql[-1]
    assert "missing additive contract column(s): app_id, confidence_score" in caplog.text


def test_a_probe_that_answers_with_no_rows_is_cached_as_an_absent_table():
    """B-3 — no rows is an answer (the table is not there), unlike a failure."""
    client = ColumnsStore(columns=[])
    store = ReadStore(client)

    assert store.findings_columns() == set()
    assert store.findings_columns() == set()
    assert client.probe_calls == 1
