# Codex Gate 8 ClickHouse Findings Persistence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persist validated Commander findings in ClickHouse so Apex has an auditable decision trail, not only runtime diagnosis from telemetry envelopes.

**Architecture:** Gate 8 adds a `ClickHouseFindingStore` beside the existing telemetry store. Telemetry remains the input source; findings are derived by deterministic detectors, validated by `EvidenceValidator`, persisted to a dedicated findings table, and queryable by `job_id`.

**Tech Stack:** Python standard library, existing `apex.commander` modules, pytest, fake ClickHouse client, opt-in real local ClickHouse HTTP integration.

---

## Branch Rule

All work happens only on:

```text
gustocezar/feature/codex-desacoplamento-geradores
```

Forbidden:

- pushing to GitHub;
- editing Spike, Cowork, Kimi, DataFlint, or evaluated remote branches;
- adding a third-party ClickHouse driver dependency;
- requiring real ClickHouse for the default test suite;
- storing credentials in files or docs;
- changing the existing NDJSON CLI default.

## File Structure

- Create: `apex/commander/clickhouse_findings.py` for findings table schema, insert, query, and validation persistence helper.
- Create: `tests/test_commander_clickhouse_findings.py` for fake-client findings persistence tests.
- Create: `tests/test_commander_clickhouse_findings_real_integration.py` for opt-in real ClickHouse findings persistence validation.
- Modify: `docs/playbooks/commander-v01-local.md` to document Gate 8.
- Modify: `docs/architecture/llm-solution-validation-framework-2026-07-09.md` to update Gate 8 status.

## Task 1: Add Findings Store With Fake Client Tests

**Files:**
- Create: `tests/test_commander_clickhouse_findings.py`
- Create: `apex/commander/clickhouse_findings.py`

- [ ] **Step 1: Write failing fake-client tests**

Create `tests/test_commander_clickhouse_findings.py`:

```python
from apex.commander.clickhouse_findings import (
    ClickHouseFindingStore,
    persist_validated_findings,
)
from apex.commander.findings import build_finding


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
            [row["finding_json"], row["validation_json"]]
            for row in self.rows
            if row["job_id"] == job_id
        ]
        return FakeQueryResult(rows)


def valid_finding():
    return build_finding(
        "shuffle_skew_candidate",
        "job-42",
        "warning",
        "medium",
        {
            "schema_version": "apex.commander.telemetry.v1",
            "app_id": "app-findings",
            "stage_id": 2,
            "ratio": 29.5,
            "hot_records": 165297,
            "median_cold_records": 5596,
            "task_count": 8,
        },
        ["Validar skew antes de aplicar mudanca."],
    )


def test_finding_store_creates_schema():
    client = FakeClickHouseClient()
    store = ClickHouseFindingStore(client, table="commander_findings")

    store.ensure_schema()

    assert len(client.commands) == 1
    assert "CREATE TABLE IF NOT EXISTS commander_findings" in client.commands[0]
    assert "finding_json String" in client.commands[0]
    assert "validation_json String" in client.commands[0]
    assert "ENGINE = MergeTree" in client.commands[0]


def test_persist_validated_findings_inserts_and_queries_by_job_id():
    client = FakeClickHouseClient()
    store = ClickHouseFindingStore(client)
    records = persist_validated_findings(store, [valid_finding()])

    assert records[0]["validation"]["accepted"] is True
    assert client.inserts[0]["table"] == "commander_findings"

    persisted = store.query_by_job_id("job-42")

    assert persisted[0]["finding"]["kind"] == "shuffle_skew_candidate"
    assert persisted[0]["validation"]["status"] == "valid"


def test_finding_store_rejects_unsafe_table_name():
    try:
        ClickHouseFindingStore(FakeClickHouseClient(), table="bad;drop")
    except ValueError as exc:
        assert str(exc) == "unsafe_table_name"
    else:
        raise AssertionError("expected unsafe table name rejection")
```

- [ ] **Step 2: Run RED**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_clickhouse_findings.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'apex.commander.clickhouse_findings'
```

- [ ] **Step 3: Implement findings store**

Create `apex/commander/clickhouse_findings.py` with:

- `ClickHouseFindingStore.ensure_schema()`;
- `append_record(finding, validation)`;
- `query_by_job_id(job_id)`;
- `persist_validated_findings(store, findings)`;
- safe table-name validation.

- [ ] **Step 4: Run GREEN**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_clickhouse_findings.py -q
```

Expected:

```text
3 passed
```

## Task 2: Add Real ClickHouse Findings Integration

**Files:**
- Create: `tests/test_commander_clickhouse_findings_real_integration.py`

- [ ] **Step 1: Add opt-in real integration test**

Create a test that:

- skips unless `APEX_CLICKHOUSE_REAL_URL` is set;
- creates a unique telemetry table and findings table;
- persists a skew telemetry envelope in real ClickHouse;
- runs `diagnose_findings`;
- persists validated findings in real ClickHouse;
- queries persisted findings by `job_id`;
- drops both tables in `finally`.

- [ ] **Step 2: Run skipped by default**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_clickhouse_findings_real_integration.py -q
```

Expected:

```text
1 skipped
```

- [ ] **Step 3: Run against real local ClickHouse when env vars are available**

Run with env:

```powershell
$env:APEX_CLICKHOUSE_REAL_URL='http://localhost:28123'
$env:APEX_CLICKHOUSE_REAL_USER='<local user>'
$env:APEX_CLICKHOUSE_REAL_PASSWORD='<local password>'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_clickhouse_findings_real_integration.py -q
```

Expected:

```text
1 passed
```

## Task 3: Update Documentation

**Files:**
- Modify: `docs/playbooks/commander-v01-local.md`
- Modify: `docs/architecture/llm-solution-validation-framework-2026-07-09.md`

- [ ] **Step 1: Document Gate 8**

Add a Gate 8 section explaining the telemetry-to-finding audit trail and the real/local validation commands.

- [ ] **Step 2: Update validation framework**

Update current status, Gate 8 evidence, and backlog.

- [ ] **Step 3: Run documentation sanity grep**

Run:

```powershell
rg -n "TBD|TODO|implement later|fill in details|placeholder" docs/playbooks/commander-v01-local.md docs/architecture/llm-solution-validation-framework-2026-07-09.md
```

Expected: no matches.

## Task 4: Final Verification

**Files:**
- Modify: none

- [ ] **Step 1: Run focused default tests**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_clickhouse_findings.py tests/test_commander_clickhouse_findings_real_integration.py tests/test_commander_clickhouse_real_integration.py -q --basetemp .pytest-commander-gate8
```

Expected: fake findings tests pass; real tests skip unless env vars are set.

- [ ] **Step 2: Run real integration if local ClickHouse is available**

Run with env vars as in Task 2 Step 3.

- [ ] **Step 3: Run full suite**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests -q --basetemp .pytest-codex-gate8-final
```

Expected: all default tests pass.

- [ ] **Step 4: Confirm branch remains local-only**

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
