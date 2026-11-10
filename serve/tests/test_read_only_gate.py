"""Fixture lifecycle of the real gate, offline; no ClickHouse connection.

Diagnostic results are stubs: these tests prove orchestration and bounded
cleanup, not the correctness of diagnoses or ClickHouse mutation execution.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
from types import SimpleNamespace

import pytest


PATH = Path(__file__).resolve().parents[1] / "tools" / "read_only_gate.py"
spec = importlib.util.spec_from_file_location("read_only_gate", PATH)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
TABLES = ("spark_events", "findings", "plan_transitions", "spark_jobs_1m")
FOREIGN = gate.BEFORE_JOB_ID + "-not-owned"


class FixtureClient:
    def __init__(self, *, rollup=True, insert_failure=None, cleanup_failure=None,
                 discovery_failure=False, schema_failure=False):
        self.rollup = rollup
        self.insert_failure = insert_failure
        self.cleanup_failure = cleanup_failure
        self.discovery_failure = discovery_failure
        self.schema_failure = schema_failure
        self.rows = {table: {FOREIGN} for table in TABLES}
        self.inserted = []
        self.deletions = []
        self.commands = []

    def query(self, sql):
        table = sql.split(".")[-1]
        columns = {
            "spark_events": gate.REQUIRED_SPARK_EVENTS,
            "findings": gate.REQUIRED_FINDINGS | gate.ADDITIVE_FINDINGS,
            "plan_transitions": gate.REQUIRED_PLAN_TRANSITIONS,
        }[table]
        return SimpleNamespace(result_rows=[] if self.schema_failure else [(c,) for c in columns])

    def insert(self, table, rows, *, column_names):
        self.inserted.append(table)
        for row in rows:
            job = row[column_names.index("job_id")]
            self.rows[table].add(job)
            if table == "spark_events" and self.rollup:
                self.rows["spark_jobs_1m"].add(job)
        if self.insert_failure == table:
            raise RuntimeError("partial insert failed")

    def command(self, sql, *, parameters=None, settings=None):
        self.commands.append(sql)
        if sql == "EXISTS TABLE spark_jobs_1m":
            if self.discovery_failure:
                raise RuntimeError("driver detail: private-connection-string")
            return int(self.rollup)
        # Evaluate only this bounded predicate, not prefix matching or an
        # unconditional DELETE. An unrelated near-prefix job must survive.
        match = re.fullmatch(
            r"ALTER TABLE (?:apex\.)?(\w+) DELETE WHERE job_id IN "
            r"\(\{before:String\}, \{after:String\}\)", sql,
        )
        assert match, f"unexpected mutation: {sql}"
        table = match.group(1)
        self.deletions.append((table, parameters, settings, sql))
        if self.cleanup_failure == table:
            raise RuntimeError("driver detail: private-connection-string")
        self.rows[table].difference_update(parameters.values())


class StubStore:
    def __init__(self, _client):
        pass

    def stages(self, job):
        if job == "' OR 1=1 --":
            return []
        return [{"stage_id": 2, "stage_attempt": 1, "p99_ms": 110, "spill_disk_bytes": 0}]

    def findings(self, _job):
        return []

    def plan_transitions(self, _job):
        return []

    def search(self, *_args):
        return []

    def runs(self, *, app_name=None, **_kwargs):
        if app_name == "' OR 1=1 --":
            return []
        return [{"job_id": job, "stage_count": 1, "app_name": "gate", "last_ts": 1}
                for job in (gate.BEFORE_JOB_ID, gate.AFTER_JOB_ID)]


@pytest.fixture
def setup_gate(monkeypatch):
    def setup(client):
        monkeypatch.setattr(gate.clickhouse_connect, "get_client", lambda **_kw: client)
        monkeypatch.setattr(gate, "ReadStore", StubStore)
        monkeypatch.setattr(gate.diagnose, "analyze", lambda *_a: SimpleNamespace(
            status="degraded", worst_stage_id=2, aqe_ground_truth=["note"],
            symptoms=[], primary_symptom="disk_spill"))
        monkeypatch.setattr(gate.diagnose, "compare", lambda before, after, *_a: SimpleNamespace(
            status="unchanged" if before == after else "regressed", findings=[],
            regressions=[] if before == after else [
                "spill_introduced", "plan_fingerprint_changed", "finding_introduced"]))
        monkeypatch.setattr(gate.diagnose, "build_hits", lambda *_a: SimpleNamespace(total=1))
        monkeypatch.setattr(gate.diagnose, "suggest_fix", lambda _job, _finding, floor, *_a:
                            SimpleNamespace(applied=False, requires_human_approval=True,
                                            source="findings_table", proposed_diff="" if floor > .99 else "diff",
                                            gated=floor > .99, confidence=.91))
    return setup


def assert_removed(client, *, failed_table=None):
    for table in TABLES:
        assert FOREIGN in client.rows[table], "cleanup removed a foreign job"
        if table != failed_table:
            assert client.rows[table] == {FOREIGN}, f"owned rows left in {table}"


def assert_bounded_deletes(client, expected=TABLES):
    assert [entry[0] for entry in client.deletions] == list(expected)
    for _table, params, settings, sql in client.deletions:
        assert params == {"before": gate.BEFORE_JOB_ID, "after": gate.AFTER_JOB_ID}
        assert settings == {"mutations_sync": 2}
        assert "apex." not in sql, "cleanup must use the same session database as inserts"


def test_success_cleans_sources_and_optional_rollup_before_pass(setup_gate, capsys):
    client = FixtureClient()
    setup_gate(client)
    assert gate.main() == 0
    assert_removed(client)
    assert_bounded_deletes(client)
    assert json.loads(capsys.readouterr().out)["status"] == "passed"


@pytest.mark.parametrize("table", TABLES[:3])
def test_partial_insert_failure_cleans_even_the_first_write(table, setup_gate, capsys):
    client = FixtureClient(insert_failure=table)
    setup_gate(client)
    with pytest.raises(RuntimeError, match="partial insert failed"):
        gate.main()
    assert_removed(client)
    assert_bounded_deletes(client)
    assert capsys.readouterr().out == ""


def test_assertion_failure_still_cleans_owned_rows(setup_gate, monkeypatch, capsys):
    client = FixtureClient()
    setup_gate(client)
    original = AssertionError("diagnostic assertion failed")

    def fail(*_args):
        raise original

    monkeypatch.setattr(gate.diagnose, "analyze", fail)
    with pytest.raises(AssertionError) as raised:
        gate.main()
    assert raised.value is original
    assert_removed(client)
    assert_bounded_deletes(client)
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("table", TABLES)
def test_cleanup_failure_attempts_other_tables_and_cannot_pass(table, setup_gate, capsys):
    client = FixtureClient(cleanup_failure=table)
    setup_gate(client)
    with pytest.raises(RuntimeError, match="fixture_cleanup_failed") as raised:
        gate.main()
    assert "private-connection-string" not in str(raised.value)
    assert_removed(client, failed_table=table)
    assert_bounded_deletes(client)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "private-connection-string" not in captured.err


def test_cleanup_error_is_visible_without_replacing_primary_failure(setup_gate, monkeypatch, capsys):
    client = FixtureClient(cleanup_failure="spark_events")
    setup_gate(client)
    original = AssertionError("primary gate failure")

    def fail(*_args):
        raise original

    monkeypatch.setattr(gate.diagnose, "analyze", fail)
    with pytest.raises(AssertionError) as raised:
        gate.main()
    assert raised.value is original
    assert_removed(client, failed_table="spark_events")
    assert_bounded_deletes(client)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "fixture_cleanup_failed: spark_events" in captured.err
    assert "private-connection-string" not in captured.err


def test_missing_optional_rollup_does_not_fail_gate(setup_gate):
    client = FixtureClient(rollup=False)
    setup_gate(client)
    assert gate.main() == 0
    assert_removed(client)
    assert_bounded_deletes(client, TABLES[:3])


def test_rollup_discovery_failure_still_cleans_source_tables(setup_gate, capsys):
    client = FixtureClient(discovery_failure=True)
    setup_gate(client)
    with pytest.raises(RuntimeError, match="fixture_cleanup_failed: spark_jobs_1m discovery"):
        gate.main()
    assert_removed(client, failed_table="spark_jobs_1m")
    assert_bounded_deletes(client, TABLES[:3])
    assert capsys.readouterr().out == ""


def test_schema_failure_before_seeding_performs_no_mutations(setup_gate, capsys):
    client = FixtureClient(schema_failure=True)
    setup_gate(client)
    with pytest.raises(AssertionError, match="spark_events missing"):
        gate.main()
    assert client.inserted == []
    assert client.commands == []
    assert capsys.readouterr().out == ""
