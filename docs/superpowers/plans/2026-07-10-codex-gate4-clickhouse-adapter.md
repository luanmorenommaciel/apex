# Codex Gate 4 ClickHouse Adapter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare a local ClickHouse/ClickStack telemetry adapter with fake-client tests, while preserving the existing NDJSON store contract.

**Architecture:** Gate 4 introduces a dependency-injected `ClickHouseTelemetryStore` that speaks a small ClickHouse client protocol: `command`, `insert`, and `query`. Existing Commander diagnosis continues to work with file paths, and gains support for store objects exposing `query_by_job_id(job_id)`.

**Tech Stack:** Python standard library, existing `apex.commander` modules, pytest, fake ClickHouse client in tests, no real network, no real ClickHouse dependency.

---

## Branch Rule

All work happens only on:

```text
gustocezar/feature/codex-desacoplamento-geradores
```

Forbidden:

- pushing to GitHub;
- editing Spike, Cowork, Kimi, DataFlint, or evaluated remote branches;
- adding a real ClickHouse package dependency;
- opening network connections;
- replacing the existing NDJSON MVP store.

## File Structure

- Create: `apex/commander/clickhouse_adapter.py` for the injectable ClickHouse telemetry store.
- Create: `apex/commander/telemetry_store.py` for store-neutral envelope querying.
- Create: `tests/test_commander_clickhouse_adapter.py` for fake-client adapter tests.
- Modify: `apex/commander/diagnostic_mvp.py` to use `query_envelopes`.
- Modify: `apex/commander/mcp_contract.py` to use `query_envelopes`.
- Modify: `docs/playbooks/commander-v01-local.md` to document Gate 4.
- Modify: `docs/architecture/llm-solution-validation-framework-2026-07-09.md` to update Gate 4 status.

## Task 1: Add ClickHouse Adapter Shape

**Files:**
- Create: `tests/test_commander_clickhouse_adapter.py`
- Create: `apex/commander/clickhouse_adapter.py`

- [ ] **Step 1: Write failing fake-client tests**

Create `tests/test_commander_clickhouse_adapter.py`:

```python
import json

import pytest

from apex.commander.clickhouse_adapter import ClickHouseTelemetryStore


class FakeQueryResult:
    def __init__(self, result_rows):
        self.result_rows = result_rows


class FakeClickHouseClient:
    def __init__(self):
        self.commands = []
        self.inserts = []
        self.rows = []

    def command(self, sql):
        self.commands.append(sql)

    def insert(self, table, rows, column_names):
        self.inserts.append(
            {"table": table, "rows": rows, "column_names": column_names}
        )
        for row in rows:
            self.rows.append(dict(zip(column_names, row)))

    def query(self, sql, parameters):
        job_id = parameters["job_id"]
        rows = [
            [row["envelope_json"]]
            for row in self.rows
            if row["job_id"] == job_id
        ]
        return FakeQueryResult(rows)


def telemetry_envelope(job_id="job-42"):
    return {
        "schema_version": "apex.commander.telemetry.v1",
        "job_id": job_id,
        "app_id": "app-clickhouse",
        "event_counts": {"SparkListenerTaskEnd": 1},
        "stages": [{"stage_id": 1, "task_count": 1}],
        "skew_candidates": [],
    }


def test_clickhouse_adapter_creates_schema():
    client = FakeClickHouseClient()
    store = ClickHouseTelemetryStore(client, table="commander_telemetry")

    store.ensure_schema()

    assert len(client.commands) == 1
    assert "CREATE TABLE IF NOT EXISTS commander_telemetry" in client.commands[0]
    assert "envelope_json String" in client.commands[0]
    assert "ENGINE = MergeTree" in client.commands[0]


def test_clickhouse_adapter_appends_and_queries_by_job_id():
    client = FakeClickHouseClient()
    store = ClickHouseTelemetryStore(client)
    envelope = telemetry_envelope()

    store.append_envelope(envelope)

    assert client.inserts[0]["table"] == "commander_telemetry"
    assert store.query_by_job_id("job-42") == [envelope]
    assert store.query_by_job_id("missing-job") == []


def test_clickhouse_adapter_rejects_unsafe_table_name():
    with pytest.raises(ValueError, match="unsafe_table_name"):
        ClickHouseTelemetryStore(FakeClickHouseClient(), table="bad;drop")
```

- [ ] **Step 2: Run RED**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_clickhouse_adapter.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'apex.commander.clickhouse_adapter'
```

- [ ] **Step 3: Implement adapter**

Create `apex/commander/clickhouse_adapter.py`:

```python
"""ClickHouse-backed telemetry store adapter for Commander."""

import json
import re

COLUMNS = (
    "schema_version",
    "job_id",
    "app_id",
    "event_counts_json",
    "stages_json",
    "skew_candidates_json",
    "envelope_json",
)


class ClickHouseTelemetryStore:
    def __init__(self, client, table="commander_telemetry"):
        self.client = client
        self.table = _validate_identifier(table)

    def ensure_schema(self):
        self.client.command(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table}
            (
                schema_version String,
                job_id String,
                app_id Nullable(String),
                event_counts_json String,
                stages_json String,
                skew_candidates_json String,
                envelope_json String,
                inserted_at DateTime DEFAULT now()
            )
            ENGINE = MergeTree
            ORDER BY (job_id, inserted_at)
            """
        )

    def append_envelope(self, envelope):
        self.client.insert(
            self.table,
            [_row_from_envelope(envelope)],
            column_names=COLUMNS,
        )

    def query_by_job_id(self, job_id):
        result = self.client.query(
            f"""
            SELECT envelope_json
            FROM {self.table}
            WHERE job_id = {{job_id:String}}
            ORDER BY inserted_at ASC
            """,
            parameters={"job_id": job_id},
        )
        return [json.loads(row[0]) for row in result.result_rows]


def _row_from_envelope(envelope):
    return (
        envelope.get("schema_version", ""),
        envelope["job_id"],
        envelope.get("app_id"),
        json.dumps(envelope.get("event_counts", {}), sort_keys=True),
        json.dumps(envelope.get("stages", []), sort_keys=True),
        json.dumps(envelope.get("skew_candidates", []), sort_keys=True),
        json.dumps(envelope, sort_keys=True),
    )


def _validate_identifier(identifier):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", identifier):
        raise ValueError("unsafe_table_name")
    return identifier
```

- [ ] **Step 4: Run GREEN**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_clickhouse_adapter.py -q
```

Expected:

```text
3 passed
```

## Task 2: Make Commander Read Store Objects

**Files:**
- Create: `apex/commander/telemetry_store.py`
- Modify: `apex/commander/diagnostic_mvp.py`
- Modify: `apex/commander/mcp_contract.py`
- Modify: `tests/test_commander_clickhouse_adapter.py`

- [ ] **Step 1: Add failing integration test**

Append to `tests/test_commander_clickhouse_adapter.py`:

```python
from apex.commander.diagnostic_mvp import diagnose_findings
from apex.commander.mcp_contract import explain_evidence


def skew_envelope():
    envelope = telemetry_envelope("job-skew")
    envelope["stages"] = [
        {
            "stage_id": 2,
            "task_count": 8,
            "records": [165297, 5596, 5600, 5700],
            "total_records": 182193,
            "max_records": 165297,
            "median_cold_records": 5596,
            "ratio": 29.5,
            "evidence_status": "valid",
            "quality_issues": [],
            "disk_bytes_spilled": 0,
            "memory_bytes_spilled": 0,
            "jvm_gc_time_ms": 0,
            "executor_run_time_ms": 10000,
            "failure_reasons": [],
        }
    ]
    envelope["skew_candidates"] = [
        {
            "kind": "shuffle_skew_candidate",
            "stage_id": 2,
            "ratio": 29.5,
            "hot_records": 165297,
            "median_cold_records": 5596,
            "task_count": 8,
        }
    ]
    return envelope


def test_diagnosis_reads_from_clickhouse_adapter():
    store = ClickHouseTelemetryStore(FakeClickHouseClient())
    store.append_envelope(skew_envelope())

    findings = diagnose_findings(store, "job-skew")

    assert [finding["kind"] for finding in findings] == ["shuffle_skew_candidate"]


def test_explain_evidence_reads_from_clickhouse_adapter():
    store = ClickHouseTelemetryStore(FakeClickHouseClient())
    store.append_envelope(skew_envelope())

    result = explain_evidence(store, "job-skew")

    assert result["status"] == "found"
    assert result["job_id"] == "job-skew"
    assert result["stages"][0]["stage_id"] == 2
```

- [ ] **Step 2: Run RED**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_clickhouse_adapter.py::test_diagnosis_reads_from_clickhouse_adapter tests/test_commander_clickhouse_adapter.py::test_explain_evidence_reads_from_clickhouse_adapter -q
```

Expected: tests fail because existing code treats the store object as an NDJSON path.

- [ ] **Step 3: Add store-neutral query helper**

Create `apex/commander/telemetry_store.py`:

```python
"""Store-neutral telemetry query helpers."""

from apex.commander.clickstack_mvp import query_by_job_id as query_ndjson_by_job_id


def query_envelopes(store, job_id):
    if hasattr(store, "query_by_job_id"):
        return store.query_by_job_id(job_id)
    return query_ndjson_by_job_id(store, job_id)
```

Modify `apex/commander/diagnostic_mvp.py`:

```python
from apex.commander.telemetry_store import query_envelopes
```

Replace both calls to `query_by_job_id(store_path, job_id)` with:

```python
query_envelopes(store_path, job_id)
```

Modify `apex/commander/mcp_contract.py`:

```python
from apex.commander.telemetry_store import query_envelopes
```

Replace `query_by_job_id(store_path, job_id)` with:

```python
query_envelopes(store_path, job_id)
```

- [ ] **Step 4: Run GREEN**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_clickhouse_adapter.py tests/test_commander_v01.py tests/test_commander_mcp_contract.py -q
```

Expected: all tests pass.

## Task 3: Update Documentation

**Files:**
- Modify: `docs/playbooks/commander-v01-local.md`
- Modify: `docs/architecture/llm-solution-validation-framework-2026-07-09.md`

- [ ] **Step 1: Document Gate 4**

Add a Gate 4 section explaining:

- `ClickHouseTelemetryStore` is adapter-only;
- fake client proves command/insert/query behavior;
- existing NDJSON store remains supported;
- no real ClickHouse server is required in this gate.

- [ ] **Step 2: Update validation framework**

Update Current Codex Status, Gate 4, and Immediate Codex Backlog to mark the adapter as implemented locally with fake-client tests, while real Docker/ClickHouse validation remains a later gap.

- [ ] **Step 3: Run documentation sanity grep**

Run:

```powershell
rg -n "TBD|TODO|implement later|fill in details|placeholder" docs/playbooks/commander-v01-local.md docs/architecture/llm-solution-validation-framework-2026-07-09.md
```

Expected: no matches.

## Task 4: Final Verification

**Files:**
- Modify: none

- [ ] **Step 1: Run focused Commander tests**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_clickhouse_adapter.py tests/test_commander_negative_baselines.py tests/test_commander_mcp_contract.py tests/test_commander_v01.py -q --basetemp .pytest-commander-gate4
```

Expected: all focused tests pass.

- [ ] **Step 2: Run full suite**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests -q --basetemp .pytest-codex-gate4-final
```

Expected: all tests pass.

- [ ] **Step 3: Confirm branch remains local-only**

Run:

```powershell
git status --short --branch
git rev-parse --abbrev-ref --symbolic-full-name '@{u}'
```

Expected:

```text
## gustocezar/feature/codex-desacoplamento-geradores
fatal: no upstream configured for branch 'gustocezar/feature/codex-desacoplamento-geradores'
```
