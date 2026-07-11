# Codex Gate 7 ClickHouse Real Local Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Validate Commander telemetry persistence against a real local ClickHouse HTTP endpoint while keeping the regular test suite deterministic and local-only.

**Architecture:** Gate 7 adds a standard-library `ClickHouseHttpClient` implementing the same client boundary already used by `ClickHouseTelemetryStore`: `command`, `insert`, and `query`. Unit tests use a fake opener with no network; the real ClickHouse test is explicitly opt-in via environment variables and uses a unique table that is dropped before and after the run.

**Tech Stack:** Python standard library (`urllib.request`, `urllib.parse`, `base64`, `json`, `os`), existing `apex.commander` modules, pytest, local ClickHouse HTTP endpoint.

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
- requiring a real ClickHouse instance for the default suite;
- using a shared production table;
- exposing credentials in docs.

## File Structure

- Create: `apex/commander/clickhouse_http_client.py` for the real HTTP client.
- Create: `tests/test_commander_clickhouse_http_client.py` for no-network HTTP client unit tests.
- Create: `tests/test_commander_clickhouse_real_integration.py` for opt-in real ClickHouse validation.
- Modify: `docs/playbooks/commander-v01-local.md` to document Gate 7.
- Modify: `docs/architecture/llm-solution-validation-framework-2026-07-09.md` to update Gate 7 status.

## Task 1: Add ClickHouse HTTP Client Unit Tests

**Files:**
- Create: `tests/test_commander_clickhouse_http_client.py`
- Create: `apex/commander/clickhouse_http_client.py`

- [ ] **Step 1: Write failing no-network tests**

Create `tests/test_commander_clickhouse_http_client.py`:

```python
import base64
import json
from urllib.parse import parse_qs, urlparse

from apex.commander.clickhouse_http_client import ClickHouseHttpClient


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.body


class RecordingOpener:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def __call__(self, request, timeout):
        self.requests.append({"request": request, "timeout": timeout})
        return FakeResponse(self.responses.pop(0))


def query_params(request):
    return parse_qs(urlparse(request.full_url).query)


def test_command_sends_sql_with_basic_auth():
    opener = RecordingOpener([b""])
    client = ClickHouseHttpClient(
        "http://clickhouse.local:8123",
        user="commander",
        password="secret",
        opener=opener,
        timeout=3,
    )

    client.command("SELECT 1")

    sent = opener.requests[0]
    request = sent["request"]
    assert sent["timeout"] == 3
    assert query_params(request)["query"] == ["SELECT 1"]
    expected = base64.b64encode(b"commander:secret").decode("ascii")
    assert request.headers["Authorization"] == f"Basic {expected}"


def test_insert_sends_json_each_row_body():
    opener = RecordingOpener([b""])
    client = ClickHouseHttpClient("http://clickhouse.local:8123", opener=opener)

    client.insert(
        "commander_telemetry",
        [("schema", "job-42")],
        column_names=("schema_version", "job_id"),
    )

    request = opener.requests[0]["request"]
    assert query_params(request)["query"] == [
        "INSERT INTO commander_telemetry (schema_version, job_id) FORMAT JSONEachRow"
    ]
    assert json.loads(request.data.decode("utf-8").strip()) == {
        "schema_version": "schema",
        "job_id": "job-42",
    }


def test_query_parses_json_each_row_response():
    body = b'{"envelope_json":"{\\"job_id\\": \\"job-42\\"}"}\n'
    opener = RecordingOpener([body])
    client = ClickHouseHttpClient("http://clickhouse.local:8123", opener=opener)

    result = client.query(
        "SELECT envelope_json FROM commander_telemetry WHERE job_id = {job_id:String}",
        parameters={"job_id": "job-42"},
    )

    request = opener.requests[0]["request"]
    params = query_params(request)
    assert params["param_job_id"] == ["job-42"]
    assert params["query"][0].endswith("FORMAT JSONEachRow")
    assert result.result_rows == [['{"job_id": "job-42"}']]
```

- [ ] **Step 2: Run RED**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_clickhouse_http_client.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'apex.commander.clickhouse_http_client'
```

- [ ] **Step 3: Implement client**

Create `apex/commander/clickhouse_http_client.py`:

```python
"""Small ClickHouse HTTP client for Commander local validation."""

import base64
import json
from urllib import parse, request


class ClickHouseQueryResult:
    def __init__(self, result_rows):
        self.result_rows = result_rows


class ClickHouseHttpClient:
    def __init__(self, base_url, *, user=None, password=None, timeout=10, opener=None):
        self.base_url = base_url.rstrip("/")
        self.user = user
        self.password = password
        self.timeout = timeout
        self.opener = opener or request.urlopen

    def command(self, sql):
        self._request(sql)

    def insert(self, table, rows, column_names):
        sql = f"INSERT INTO {table} ({', '.join(column_names)}) FORMAT JSONEachRow"
        lines = [
            json.dumps(dict(zip(column_names, row)), sort_keys=True)
            for row in rows
        ]
        body = ("\n".join(lines) + "\n").encode("utf-8")
        self._request(sql, body=body)

    def query(self, sql, parameters=None):
        query_sql = _ensure_json_each_row(sql)
        response = self._request(query_sql, parameters=parameters or {})
        rows = []
        for line in response.decode("utf-8").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            rows.append(list(item.values()))
        return ClickHouseQueryResult(rows)

    def _request(self, sql, *, body=None, parameters=None):
        query = {"query": sql}
        for key, value in (parameters or {}).items():
            query[f"param_{key}"] = value
        url = f"{self.base_url}/?{parse.urlencode(query)}"
        req = request.Request(url, data=body, method="POST")
        if self.user is not None:
            token = base64.b64encode(
                f"{self.user}:{self.password or ''}".encode("utf-8")
            ).decode("ascii")
            req.add_header("Authorization", f"Basic {token}")
        if body is not None:
            req.add_header("Content-Type", "application/json")
        with self.opener(req, timeout=self.timeout) as response:
            return response.read()


def _ensure_json_each_row(sql):
    normalized = sql.strip()
    if normalized.upper().endswith("FORMAT JSONEACHROW"):
        return normalized
    return f"{normalized} FORMAT JSONEachRow"
```

- [ ] **Step 4: Run GREEN**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_clickhouse_http_client.py -q
```

Expected:

```text
3 passed
```

## Task 2: Add Real ClickHouse Integration Test

**Files:**
- Create: `tests/test_commander_clickhouse_real_integration.py`

- [ ] **Step 1: Add opt-in integration test**

Create `tests/test_commander_clickhouse_real_integration.py`:

```python
import os
import uuid

import pytest

from apex.commander.clickhouse_adapter import ClickHouseTelemetryStore
from apex.commander.clickhouse_http_client import ClickHouseHttpClient
from apex.commander.diagnostic_mvp import diagnose_findings
from apex.commander.mcp_contract import explain_evidence


def real_clickhouse_config():
    url = os.environ.get("APEX_CLICKHOUSE_REAL_URL")
    if not url:
        pytest.skip("APEX_CLICKHOUSE_REAL_URL is not set")
    return {
        "url": url,
        "user": os.environ.get("APEX_CLICKHOUSE_REAL_USER"),
        "password": os.environ.get("APEX_CLICKHOUSE_REAL_PASSWORD"),
    }


def skew_envelope(job_id):
    return {
        "schema_version": "apex.commander.telemetry.v1",
        "job_id": job_id,
        "app_id": "app-clickhouse-real",
        "event_counts": {"SparkListenerTaskEnd": 4},
        "stages": [
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
        ],
        "skew_candidates": [
            {
                "kind": "shuffle_skew_candidate",
                "stage_id": 2,
                "ratio": 29.5,
                "hot_records": 165297,
                "median_cold_records": 5596,
                "task_count": 8,
            }
        ],
    }


def test_real_clickhouse_roundtrip_and_diagnosis():
    config = real_clickhouse_config()
    client = ClickHouseHttpClient(
        config["url"],
        user=config["user"],
        password=config["password"],
    )
    table = f"commander_gate7_{uuid.uuid4().hex}"
    store = ClickHouseTelemetryStore(client, table=table)
    job_id = f"gate7-real-{uuid.uuid4().hex}"

    try:
        client.command(f"DROP TABLE IF EXISTS {table}")
        store.ensure_schema()
        store.append_envelope(skew_envelope(job_id))

        assert store.query_by_job_id(job_id)[0]["job_id"] == job_id
        assert diagnose_findings(store, job_id)[0]["kind"] == "shuffle_skew_candidate"
        assert explain_evidence(store, job_id)["status"] == "found"
    finally:
        client.command(f"DROP TABLE IF EXISTS {table}")
```

- [ ] **Step 2: Run skipped by default**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_clickhouse_real_integration.py -q
```

Expected:

```text
1 skipped
```

- [ ] **Step 3: Run against real local ClickHouse when credentials are available**

Run with local env:

```powershell
$env:APEX_CLICKHOUSE_REAL_URL='http://localhost:28123'
$env:APEX_CLICKHOUSE_REAL_USER='<local user>'
$env:APEX_CLICKHOUSE_REAL_PASSWORD='<local password>'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_clickhouse_real_integration.py -q
```

Expected:

```text
1 passed
```

## Task 3: Update Documentation

**Files:**
- Modify: `docs/playbooks/commander-v01-local.md`
- Modify: `docs/architecture/llm-solution-validation-framework-2026-07-09.md`

- [ ] **Step 1: Document Gate 7**

Add a Gate 7 section explaining:

- `ClickHouseHttpClient` uses standard library HTTP;
- default suite remains fake/skipped unless env vars are set;
- real integration requires `APEX_CLICKHOUSE_REAL_URL`, optional user/password;
- test creates and drops a unique local table.

- [ ] **Step 2: Update validation framework**

Update Current Codex Status, Gate 7, and Immediate Codex Backlog to mark real local ClickHouse validation as implemented when env is available.

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
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_clickhouse_http_client.py tests/test_commander_clickhouse_adapter.py tests/test_commander_clickhouse_real_integration.py -q --basetemp .pytest-commander-gate7
```

Expected: HTTP and adapter tests pass; real integration skips unless env vars are set.

- [ ] **Step 2: Run real integration if local ClickHouse is available**

Run with env vars as in Task 2 Step 3.

- [ ] **Step 3: Run full suite**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests -q --basetemp .pytest-codex-gate7-final
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
