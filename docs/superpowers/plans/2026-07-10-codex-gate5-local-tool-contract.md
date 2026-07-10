# Codex Gate 5 Local Tool Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose Commander diagnosis, evidence explanation, negative-baseline evaluation, and fix preview through a local read-only tool contract that can later be wrapped by MCP.

**Architecture:** Gate 5 adds a small in-process dispatcher over existing Commander functions. It does not start a server, install MCP dependencies, apply fixes, or publish anything remotely; it creates stable tool metadata and a `CommanderToolContract.call_tool(name, arguments)` boundary.

**Tech Stack:** Python standard library, existing `apex.commander` modules, pytest, NDJSON local store.

---

## Branch Rule

All work happens only on:

```text
gustocezar/feature/codex-desacoplamento-geradores
```

Forbidden:

- pushing to GitHub;
- editing Spike, Cowork, Kimi, DataFlint, or evaluated remote branches;
- adding an MCP package dependency;
- starting a server process;
- implementing `apply_fix`;
- mutating target files through the tool contract.

## File Structure

- Create: `apex/commander/tool_contract.py` for local tool metadata and dispatch.
- Create: `tests/test_commander_tool_contract.py` for read-only tool contract behavior.
- Modify: `docs/playbooks/commander-v01-local.md` to document Gate 5.
- Modify: `docs/architecture/llm-solution-validation-framework-2026-07-09.md` to update Gate 5 status.

## Task 1: Add Tool Metadata And Dispatcher

**Files:**
- Create: `tests/test_commander_tool_contract.py`
- Create: `apex/commander/tool_contract.py`

- [ ] **Step 1: Write failing tests for tool listing and unknown tool rejection**

Create `tests/test_commander_tool_contract.py`:

```python
import pytest

from apex.commander.tool_contract import CommanderToolContract, list_tools


def test_list_tools_exposes_only_read_only_commander_tools():
    tools = list_tools()
    tool_names = [tool["name"] for tool in tools]

    assert tool_names == [
        "debug_job",
        "explain_evidence",
        "evaluate_negative_baseline",
        "preview_fix",
    ]
    assert all(tool["safety"] == "read_only" for tool in tools)
    assert "apply_fix" not in tool_names
    assert tools[0]["input_schema"]["required"] == ["job_id"]


def test_unknown_tool_is_rejected(tmp_path):
    contract = CommanderToolContract(tmp_path / "store.ndjson")

    with pytest.raises(ValueError, match="unknown_tool"):
        contract.call_tool("apply_fix", {"job_id": "job-42"})
```

- [ ] **Step 2: Run RED**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_tool_contract.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'apex.commander.tool_contract'
```

- [ ] **Step 3: Implement minimal metadata and dispatcher skeleton**

Create `apex/commander/tool_contract.py`:

```python
"""Local Commander tool contract, ready to be wrapped by MCP later."""

from copy import deepcopy

TOOL_SPECS = [
    {
        "name": "debug_job",
        "description": "Return validated Commander findings for one job_id.",
        "safety": "read_only",
        "input_schema": {
            "type": "object",
            "required": ["job_id"],
            "properties": {"job_id": {"type": "string"}},
        },
    },
    {
        "name": "explain_evidence",
        "description": "Return latest stored telemetry evidence for one job_id.",
        "safety": "read_only",
        "input_schema": {
            "type": "object",
            "required": ["job_id"],
            "properties": {"job_id": {"type": "string"}},
        },
    },
    {
        "name": "evaluate_negative_baseline",
        "description": "Evaluate whether a job unexpectedly triggers Commander findings.",
        "safety": "read_only",
        "input_schema": {
            "type": "object",
            "required": ["job_id"],
            "properties": {"job_id": {"type": "string"}},
        },
    },
    {
        "name": "preview_fix",
        "description": "Return a unified diff preview without modifying the target file.",
        "safety": "read_only",
        "input_schema": {
            "type": "object",
            "required": ["path", "recommendation", "replacement"],
            "properties": {
                "path": {"type": "string"},
                "recommendation": {"type": "string"},
                "replacement": {"type": "string"},
            },
        },
    },
]


def list_tools():
    return deepcopy(TOOL_SPECS)


class CommanderToolContract:
    def __init__(self, store):
        self.store = store

    def call_tool(self, name, arguments):
        raise ValueError(f"unknown_tool:{name}")
```

- [ ] **Step 4: Run GREEN for metadata tests**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_tool_contract.py -q
```

Expected:

```text
2 passed
```

## Task 2: Dispatch Existing Commander Tools

**Files:**
- Modify: `tests/test_commander_tool_contract.py`
- Modify: `apex/commander/tool_contract.py`

- [ ] **Step 1: Add failing tests for debug, evidence, baseline, and preview dispatch**

Append to `tests/test_commander_tool_contract.py`:

```python
from apex.commander.clickstack_mvp import append_envelope


def telemetry_envelope(job_id="job-42"):
    return {
        "schema_version": "apex.commander.telemetry.v1",
        "job_id": job_id,
        "app_id": "app-tool-contract",
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


def test_call_tool_debug_job_returns_findings(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope())
    contract = CommanderToolContract(store)

    result = contract.call_tool("debug_job", {"job_id": "job-42"})

    assert result["job_id"] == "job-42"
    assert result["findings"][0]["kind"] == "shuffle_skew_candidate"


def test_call_tool_explain_evidence_returns_stages(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope())
    contract = CommanderToolContract(store)

    result = contract.call_tool("explain_evidence", {"job_id": "job-42"})

    assert result["status"] == "found"
    assert result["stages"][0]["stage_id"] == 2


def test_call_tool_evaluate_negative_baseline_returns_failed_for_skew(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope())
    contract = CommanderToolContract(store)

    result = contract.call_tool("evaluate_negative_baseline", {"job_id": "job-42"})

    assert result["status"] == "failed"
    assert result["unexpected_findings"][0]["kind"] == "shuffle_skew_candidate"


def test_call_tool_preview_fix_returns_diff_without_modifying_file(tmp_path):
    source = tmp_path / "job.py"
    source.write_text("df.join(dim, 'id').count()\n", encoding="utf-8")
    contract = CommanderToolContract(tmp_path / "store.ndjson")

    result = contract.call_tool(
        "preview_fix",
        {
            "path": str(source),
            "recommendation": "Add salting before the skewed join.",
            "replacement": "# REVIEW: Add salting before this join\ndf.join(dim, 'id').count()\n",
        },
    )

    assert result["mode"] == "preview"
    assert "+# REVIEW: Add salting before this join" in result["diff"]
    assert source.read_text(encoding="utf-8") == "df.join(dim, 'id').count()\n"
```

- [ ] **Step 2: Run RED**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_tool_contract.py -q
```

Expected: new tests fail because dispatcher only rejects unknown tools.

- [ ] **Step 3: Implement dispatch**

Modify `apex/commander/tool_contract.py`:

```python
from apex.commander.baselines import evaluate_negative_baseline
from apex.commander.fix_preview import build_fix_preview
from apex.commander.mcp_contract import debug_job, explain_evidence
```

Replace `call_tool` with:

```python
    def call_tool(self, name, arguments):
        args = arguments or {}
        if name == "debug_job":
            return debug_job(self.store, _required(args, "job_id"))
        if name == "explain_evidence":
            return explain_evidence(self.store, _required(args, "job_id"))
        if name == "evaluate_negative_baseline":
            return evaluate_negative_baseline(self.store, _required(args, "job_id"))
        if name == "preview_fix":
            return build_fix_preview(
                _required(args, "path"),
                _required(args, "recommendation"),
                replacement=_required(args, "replacement"),
            )
        raise ValueError(f"unknown_tool:{name}")


def _required(arguments, key):
    value = arguments.get(key)
    if value in (None, ""):
        raise ValueError(f"missing_argument:{key}")
    return value
```

- [ ] **Step 4: Run GREEN**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_tool_contract.py -q
```

Expected:

```text
6 passed
```

## Task 3: Add Argument Validation Test

**Files:**
- Modify: `tests/test_commander_tool_contract.py`

- [ ] **Step 1: Add missing argument test**

Append:

```python
def test_call_tool_rejects_missing_required_argument(tmp_path):
    contract = CommanderToolContract(tmp_path / "store.ndjson")

    with pytest.raises(ValueError, match="missing_argument:job_id"):
        contract.call_tool("debug_job", {})
```

- [ ] **Step 2: Run validation tests**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_tool_contract.py -q
```

Expected:

```text
7 passed
```

## Task 4: Update Documentation

**Files:**
- Modify: `docs/playbooks/commander-v01-local.md`
- Modify: `docs/architecture/llm-solution-validation-framework-2026-07-09.md`

- [ ] **Step 1: Document Gate 5**

Add a Gate 5 section explaining:

- this is a local in-process tool contract;
- all exposed tools are `read_only`;
- exposed tools are `debug_job`, `explain_evidence`, `evaluate_negative_baseline`, and `preview_fix`;
- `apply_fix` is intentionally absent.

- [ ] **Step 2: Update validation framework**

Update Current Codex Status, Gate 5, and Immediate Codex Backlog to mark the local tool contract as implemented. Keep real MCP stdio server as a remaining gap.

- [ ] **Step 3: Run documentation sanity grep**

Run:

```powershell
rg -n "TBD|TODO|implement later|fill in details|placeholder" docs/playbooks/commander-v01-local.md docs/architecture/llm-solution-validation-framework-2026-07-09.md
```

Expected: no matches.

## Task 5: Final Verification

**Files:**
- Modify: none

- [ ] **Step 1: Run focused Commander tests**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_tool_contract.py tests/test_commander_mcp_contract.py tests/test_commander_fix_preview.py tests/test_commander_negative_baselines.py -q --basetemp .pytest-commander-gate5
```

Expected: all focused tests pass.

- [ ] **Step 2: Run full suite**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests -q --basetemp .pytest-codex-gate5-final
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
