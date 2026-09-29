"""A probe that fails is an error, never a confirmed absence, and is not cached.

ReadStore probes the additive tables once (table_exists for fix_verifications,
memory_tables_present for the v0.3 memory tables) and caches the answer. A probe
that ANSWERS without the table is a normal older deployment. A probe that
FAILS - connection, credentials, missing database, the query itself - says
nothing about the table: it must surface its sanitized error, and the next call
on the same store must probe again instead of replaying a cached "absent".

The failures are the driver's real exception classes, built as
clickhouse-connect's build_http_error builds them (DatabaseError carrying the
server code, OperationalError for a refused connection). No ClickHouse runs.
"""

from __future__ import annotations

import pytest
from clickhouse_connect.driver.exceptions import DatabaseError, OperationalError

from apex_mcp.ch import MEMORY_TABLES, ApexStoreError, ReadStore
from tests.conftest import FakeResult

MARKER = "SYNTH-SENSITIVE-9b2e"
URL = f"http://apex:{MARKER}@db.internal.example:8123"


def _server_error(code: int | None) -> DatabaseError:
    return DatabaseError(
        f"Received ClickHouse exception, code: {code}, server response: "
        f"Code: {code}. DB::Exception: {MARKER} (for url {URL})",
        code=code,
    )


FAILURES = {
    "connection refused": (OperationalError(f"Connection refused to {URL}"), "clickhouse_unavailable"),
    "authentication 516": (_server_error(516), "clickhouse_access_denied"),
    "unknown database 81": (_server_error(81), "clickhouse_database_missing"),
    "memory limit 241": (_server_error(241), "clickhouse_query_failed"),
    "no server code": (DatabaseError(f"HTTP driver received HTTP status 502 ({URL})", code=None), "clickhouse_query_failed"),
}


class ProbeStore:
    """Answers system.columns/system.tables like a store that has (or lacks)
    the additive tables, after failing the first `fail_probes` probes."""

    def __init__(self, failure: Exception | None = None, *, fail_probes: int = 0, tables_present: bool = True) -> None:
        self.failure = failure
        self.fail_probes = fail_probes
        self.tables_present = tables_present
        self.probe_calls = 0
        self.read_failure: Exception | None = None

    def query(self, query: str, parameters: dict | None = None) -> FakeResult:
        parameters = parameters or {}
        if "system.columns" in query or "system.tables" in query:
            self.probe_calls += 1
            if self.probe_calls <= self.fail_probes:
                raise self.failure
            if not self.tables_present:
                return FakeResult([])
            if "system.tables" in query:
                return FakeResult([{"name": name} for name in MEMORY_TABLES])
            return FakeResult([{"name": "finding_id"}])
        if self.read_failure is not None:
            raise self.read_failure
        return FakeResult([])


PROBES = {
    "table_exists": lambda store: store.table_exists("fix_verifications"),
    "memory_tables_present": lambda store: store.memory_tables_present(),
}


@pytest.mark.parametrize("probe", sorted(PROBES))
@pytest.mark.parametrize("failure", sorted(FAILURES))
def test_a_failed_probe_raises_its_category_and_is_retried_on_the_same_store(probe, failure):
    """B-1, B-2, B-5 — the error surfaces sanitized; nothing is cached; the next
    call on the SAME store probes again and gets the real answer."""
    exc, prefix = FAILURES[failure]
    client = ProbeStore(exc, fail_probes=1)
    store = ReadStore(client)

    with pytest.raises(ApexStoreError) as caught:
        PROBES[probe](store)
    message = str(caught.value)
    assert message.split(":")[0] == prefix
    for fragment in (MARKER, "db.internal.example", "8123", "DB::Exception"):
        assert fragment not in message

    assert PROBES[probe](store) is True
    assert client.probe_calls == 2
    # The recovered answer is the one that is cached.
    assert PROBES[probe](store) is True
    assert client.probe_calls == 2


@pytest.mark.parametrize("failure", sorted(FAILURES))
def test_verifications_during_a_failed_probe_is_an_error_not_an_empty_answer(failure):
    """B-1 — verify_fix builds on this read; [] would read as 'not assessed'."""
    exc, prefix = FAILURES[failure]
    store = ReadStore(ProbeStore(exc, fail_probes=1))

    with pytest.raises(ApexStoreError) as caught:
        store.verifications("job-1")

    assert str(caught.value).startswith(prefix)
    assert store.verifications("job-1") == []  # recovered: table present, no rows for this job


@pytest.mark.parametrize("failure", sorted(FAILURES))
def test_recall_during_a_failed_memory_probe_is_an_error_not_no_history(failure):
    """B-1 — similar_plans/prior_outcomes probe first; a failure there must not
    read as 'no cross-run memory'."""
    exc, prefix = FAILURES[failure]
    store = ReadStore(ProbeStore(exc, fail_probes=1))

    with pytest.raises(ApexStoreError) as caught:
        store.prior_outcomes(["1" * 64])

    assert str(caught.value).startswith(prefix)


def test_an_older_deployment_still_reads_as_absent_and_is_cached(caplog):
    """B-3 — a probe that answers without the tables is normal absence."""
    client = ProbeStore(tables_present=False)
    store = ReadStore(client)

    with caplog.at_level("WARNING", logger="apex_mcp.ch"):
        assert store.table_exists("fix_verifications") is False
        assert store.memory_tables_present() is False
        assert store.verifications("job-1") == []
        assert store.similar_plans("1" * 64) == []
        assert store.prior_outcomes(["1" * 64]) == []

    assert client.probe_calls == 2  # one per probe, then cached
    assert "fix_verifications is not present" in caplog.text
    assert "cross-run memory unavailable" in caplog.text


@pytest.mark.parametrize("failure", sorted(FAILURES))
def test_recall_does_not_degrade_when_the_re_probe_fails(failure):
    """B-4 — a schema-shaped read error only degrades after a re-probe ANSWERS
    that the tables are gone; a re-probe that fails raises instead."""
    exc, prefix = FAILURES[failure]
    client = ProbeStore(exc)
    store = ReadStore(client)
    assert store.memory_tables_present() is True     # first probe answers
    client.read_failure = _server_error(60)           # the read hits UNKNOWN_TABLE
    client.fail_probes = client.probe_calls + 1       # ...and the re-probe fails

    with pytest.raises(ApexStoreError) as caught:
        store.prior_outcomes(["1" * 64])

    assert str(caught.value).startswith(prefix)


def test_recall_still_degrades_when_the_re_probe_confirms_absence(caplog):
    """B-4 — the existing contract with real exceptions: a dropped table,
    confirmed by a re-probe that answers, degrades to empty."""
    client = ProbeStore()
    store = ReadStore(client)
    assert store.memory_tables_present() is True
    client.read_failure = _server_error(60)
    client.tables_present = False

    with caplog.at_level("WARNING", logger="apex_mcp.ch"):
        assert store.prior_outcomes(["1" * 64]) == []

    assert "degraded to empty" in caplog.text
