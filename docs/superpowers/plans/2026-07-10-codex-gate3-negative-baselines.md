# Codex Gate 3 Negative Baselines Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an executable negative-baseline gate proving healthy Spark telemetry does not generate Commander findings, while failing loudly when a detector fires.

**Architecture:** Gate 3 stays local and deterministic. It reuses the existing NDJSON ClickStack MVP store, `diagnose_findings(store_path, job_id)`, and pytest fixtures; no remote branch, real ClickHouse, MCP server, or LLM call is introduced.

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
- adding external SaaS or LLM dependencies;
- replacing the existing NDJSON store with ClickHouse in this gate.

## File Structure

- Create: `apex/commander/baselines.py` for executable baseline evaluation.
- Create: `tests/test_commander_negative_baselines.py` for healthy and failing baseline scenarios.
- Modify: `docs/playbooks/commander-v01-local.md` to document Gate 3.
- Modify: `docs/architecture/llm-solution-validation-framework-2026-07-09.md` to update current Codex status.

## Task 1: Add Negative Baseline Evaluator

**Files:**
- Create: `apex/commander/baselines.py`
- Create: `tests/test_commander_negative_baselines.py`

- [ ] **Step 1: Write failing test for healthy baseline**

Create `tests/test_commander_negative_baselines.py`:

```python
from apex.commander.baselines import evaluate_negative_baseline
from apex.commander.clickstack_mvp import append_envelope
from apex.commander.telemetry import build_telemetry


def app_start(app_id="app-healthy"):
    return {
        "Event": "SparkListenerApplicationStart",
        "App ID": app_id,
        "App Name": "apex-negative-baseline",
    }


def task_end(stage, partition, records, *, app_id="app-healthy", disk_spill=0, memory_spill=0, gc_time=0, duration=1000, reason="Success"):
    return {
        "Event": "SparkListenerTaskEnd",
        "App ID": app_id,
        "Stage ID": stage,
        "Task End Reason": {"Reason": reason},
        "Task Info": {
            "Task ID": partition,
            "Index": partition,
            "Duration": duration,
        },
        "Task Metrics": {
            "Executor Run Time": duration,
            "JVM GC Time": gc_time,
            "Disk Bytes Spilled": disk_spill,
            "Memory Bytes Spilled": memory_spill,
            "Shuffle Read Metrics": {
                "Total Records Read": records,
            },
        },
    }


def aqe_update(app_id="app-healthy"):
    return {
        "Event": "SparkListenerSQLAdaptiveExecutionUpdate",
        "App ID": app_id,
    }


def store_envelope(tmp_path, events, job_id):
    store = tmp_path / "clickstack.ndjson"
    append_envelope(store, build_telemetry(events, job_id=job_id))
    return store


def healthy_events():
    return [
        app_start(),
        task_end(2, 0, 10000, disk_spill=128 * 1024, gc_time=50),
        task_end(2, 1, 10200, disk_spill=128 * 1024, gc_time=50),
        task_end(2, 2, 9900, disk_spill=128 * 1024, gc_time=50),
        task_end(2, 3, 10100, disk_spill=128 * 1024, gc_time=50),
        aqe_update(),
        aqe_update(),
    ]


def test_negative_baseline_passes_for_healthy_job(tmp_path):
    store = store_envelope(tmp_path, healthy_events(), "healthy-job")

    result = evaluate_negative_baseline(store, "healthy-job")

    assert result == {
        "job_id": "healthy-job",
        "status": "passed",
        "unexpected_findings": [],
        "unexpected_finding_count": 0,
    }
```

- [ ] **Step 2: Run RED**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_negative_baselines.py::test_negative_baseline_passes_for_healthy_job -q
```

Expected:

```text
ModuleNotFoundError: No module named 'apex.commander.baselines'
```

- [ ] **Step 3: Implement baseline evaluator**

Create `apex/commander/baselines.py`:

```python
"""Executable negative baselines for Commander detector false-positive control."""

from apex.commander.diagnostic_mvp import diagnose_findings


def evaluate_negative_baseline(store_path, job_id):
    findings = diagnose_findings(store_path, job_id)
    return {
        "job_id": job_id,
        "status": "failed" if findings else "passed",
        "unexpected_findings": findings,
        "unexpected_finding_count": len(findings),
    }
```

- [ ] **Step 4: Run GREEN**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_negative_baselines.py::test_negative_baseline_passes_for_healthy_job -q
```

Expected:

```text
1 passed
```

## Task 2: Add Failing Baseline Scenario

**Files:**
- Modify: `tests/test_commander_negative_baselines.py`

- [ ] **Step 1: Add test proving the gate fails when a detector fires**

Append:

```python
def spill_events():
    return [
        app_start("app-spill"),
        task_end(3, 0, 10000, app_id="app-spill", disk_spill=1024 * 1024),
        task_end(3, 1, 10200, app_id="app-spill"),
    ]


def test_negative_baseline_fails_when_detector_fires(tmp_path):
    store = store_envelope(tmp_path, spill_events(), "spill-job")

    result = evaluate_negative_baseline(store, "spill-job")

    assert result["job_id"] == "spill-job"
    assert result["status"] == "failed"
    assert result["unexpected_finding_count"] == 1
    assert result["unexpected_findings"][0]["kind"] == "shuffle_spill_candidate"
```

- [ ] **Step 2: Run test**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_negative_baselines.py -q
```

Expected:

```text
2 passed
```

## Task 3: Update Documentation

**Files:**
- Modify: `docs/playbooks/commander-v01-local.md`
- Modify: `docs/architecture/llm-solution-validation-framework-2026-07-09.md`

- [ ] **Step 1: Document Gate 3**

Add a Gate 3 section explaining:

- healthy baseline must return `passed`;
- any unexpected finding makes the baseline return `failed`;
- the command to run the baseline tests.

- [ ] **Step 2: Update framework current status**

Update the current status and validation gates to show Gate 3 is implemented locally as an executable false-positive control.

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
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_negative_baselines.py tests/test_commander_detectors.py tests/test_commander_mcp_contract.py tests/test_commander_evidence_validator.py -q --basetemp .pytest-commander-gate3
```

Expected: all focused tests pass.

- [ ] **Step 2: Run full suite**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests -q --basetemp .pytest-codex-gate3-final
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
