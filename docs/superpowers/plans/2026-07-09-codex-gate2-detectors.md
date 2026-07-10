# Codex Gate 2 Detectors Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the Codex Commander contract from a single skew detector to a local multi-detector engine covering skew, shuffle/spill, GC pressure, OOM/lost executor, and plan/AQE signals.

**Architecture:** This plan stays entirely inside `gustocezar/feature/codex-desacoplamento-geradores`. It does not merge or edit `spike/apex-v0.1`; it reimplements detector contracts in Codex with focused tests and keeps the local NDJSON store as the execution boundary. `debug_job(job_id)` becomes the public contract that returns all validated findings for one job.

**Tech Stack:** Python standard library, existing `apex.commander` modules, existing `apex.apexlib`, pytest, NDJSON local store.

---

## Branch Rule

All work happens only on:

```text
gustocezar/feature/codex-desacoplamento-geradores
```

Forbidden:

- raw-merging Spike, Cowork, Kimi, or DataFlint branches;
- editing any remote branch;
- pushing to GitHub;
- adding ClickHouse or real MCP server in this gate;
- adding LLM calls.

## Design Decision

Gate 2 introduces a normalized local finding contract:

```python
{
    "status": "finding",
    "kind": "shuffle_skew_candidate",
    "severity": "warning",
    "confidence": "medium",
    "job_id": "job-42",
    "evidence": {...},
    "recommendations": [...],
}
```

Legacy `title` remains for backwards compatibility during this gate. New code should use `kind`.

## File Structure

- Create: `apex/commander/findings.py` for normalized finding builders.
- Create: `apex/commander/detectors.py` for local deterministic detectors.
- Modify: `apex/commander/telemetry.py` to capture additional task metrics needed by detectors.
- Modify: `apex/commander/diagnostic_mvp.py` to call all local detectors.
- Modify: `apex/commander/evidence_validator.py` to validate multiple finding kinds.
- Modify: `apex/commander/mcp_contract.py` to return `findings` while keeping `finding` for compatibility.
- Create: `tests/test_commander_detectors.py`.
- Modify: `tests/test_commander_mcp_contract.py`.
- Modify: `tests/test_commander_evidence_validator.py`.
- Modify: `docs/playbooks/commander-v01-local.md`.

## Task 1: Confirm Gate 1 Baseline

**Files:**
- Modify: none
- Test: full Codex suite

- [ ] **Step 1: Confirm branch and clean state**

Run:

```powershell
git status --short --branch
```

Expected:

```text
## gustocezar/feature/codex-desacoplamento-geradores
```

- [ ] **Step 2: Run baseline tests**

Run:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests -q --basetemp .pytest-codex-gate2-baseline
```

Expected:

```text
53 passed
```

## Task 2: Add Normalized Finding Builders

**Files:**
- Create: `apex/commander/findings.py`
- Create: `tests/test_commander_detectors.py`

- [ ] **Step 1: Write failing tests for finding shape**

Create `tests/test_commander_detectors.py`:

```python
from apex.commander.findings import build_finding


def test_build_finding_keeps_legacy_title_and_new_kind():
    finding = build_finding(
        kind="shuffle_spill_candidate",
        job_id="job-42",
        severity="warning",
        confidence="medium",
        evidence={"stage_id": 3},
        recommendations=["Reduce shuffle spill."],
    )

    assert finding["status"] == "finding"
    assert finding["kind"] == "shuffle_spill_candidate"
    assert finding["title"] == "shuffle_spill_candidate"
    assert finding["job_id"] == "job-42"
    assert finding["evidence"]["stage_id"] == 3
```

- [ ] **Step 2: Run RED**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_detectors.py::test_build_finding_keeps_legacy_title_and_new_kind -q
```

Expected:

```text
ModuleNotFoundError: No module named 'apex.commander.findings'
```

- [ ] **Step 3: Implement finding builder**

Create `apex/commander/findings.py`:

```python
"""Finding helpers for Commander detector output."""


def build_finding(kind, job_id, severity, confidence, evidence, recommendations):
    return {
        "status": "finding",
        "kind": kind,
        "title": kind,
        "severity": severity,
        "confidence": confidence,
        "job_id": job_id,
        "evidence": evidence,
        "recommendations": recommendations,
    }
```

- [ ] **Step 4: Run GREEN**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_detectors.py::test_build_finding_keeps_legacy_title_and_new_kind -q
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Commit**

Run:

```powershell
git add apex/commander/findings.py tests/test_commander_detectors.py
git commit -m "feat: add commander finding builder"
```

## Task 3: Capture Extended Telemetry Metrics

**Files:**
- Modify: `apex/commander/telemetry.py`
- Modify: `tests/test_commander_detectors.py`

- [ ] **Step 1: Add test for extended stage metrics**

Append to `tests/test_commander_detectors.py`:

```python
from apex.commander.telemetry import build_telemetry


def task_end(stage, partition, records, *, disk_spill=0, memory_spill=0, gc_time=0, duration=1000, reason="Success"):
    return {
        "Event": "SparkListenerTaskEnd",
        "App ID": "app-detectors",
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


def test_build_telemetry_captures_extended_stage_metrics():
    envelope = build_telemetry(
        [
            task_end(3, 0, 1000, disk_spill=2048, memory_spill=1024, gc_time=200, duration=1000),
            task_end(3, 1, 1000, disk_spill=0, memory_spill=0, gc_time=100, duration=1000),
        ],
        job_id="job-42",
    )

    stage = envelope["stages"][0]
    assert stage["disk_bytes_spilled"] == 2048
    assert stage["memory_bytes_spilled"] == 1024
    assert stage["jvm_gc_time_ms"] == 300
    assert stage["executor_run_time_ms"] == 2000
```

- [ ] **Step 2: Run RED**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_detectors.py::test_build_telemetry_captures_extended_stage_metrics -q
```

Expected: fail with `KeyError` for one of the new metrics.

- [ ] **Step 3: Implement metric aggregation**

Modify `apex/commander/telemetry.py`.

Add helper:

```python
def _task_metric_by_stage(events):
    by_stage = {}
    for event in events:
        if event.get("Event") != "SparkListenerTaskEnd":
            continue
        stage_id = event.get("Stage ID")
        if stage_id is None:
            continue
        metrics = event.get("Task Metrics") or {}
        stage = by_stage.setdefault(
            stage_id,
            {
                "disk_bytes_spilled": 0,
                "memory_bytes_spilled": 0,
                "jvm_gc_time_ms": 0,
                "executor_run_time_ms": 0,
                "failure_reasons": [],
            },
        )
        stage["disk_bytes_spilled"] += int(metrics.get("Disk Bytes Spilled") or 0)
        stage["memory_bytes_spilled"] += int(metrics.get("Memory Bytes Spilled") or 0)
        stage["jvm_gc_time_ms"] += int(metrics.get("JVM GC Time") or 0)
        stage["executor_run_time_ms"] += int(metrics.get("Executor Run Time") or 0)
        reason = (event.get("Task End Reason") or {}).get("Reason")
        if reason and reason != "Success":
            stage["failure_reasons"].append(reason)
    return by_stage
```

Update `stage_summaries(events)` so each summary merges the extra metrics:

```python
extra_by_stage = _task_metric_by_stage(events)
...
summary = {...existing fields...}
summary.update(extra_by_stage.get(stage_id, {
    "disk_bytes_spilled": 0,
    "memory_bytes_spilled": 0,
    "jvm_gc_time_ms": 0,
    "executor_run_time_ms": 0,
    "failure_reasons": [],
}))
summaries.append(summary)
```

- [ ] **Step 4: Run GREEN**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_detectors.py::test_build_telemetry_captures_extended_stage_metrics -q
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Run existing Commander tests**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_v01.py -q
```

Expected:

```text
5 passed
```

- [ ] **Step 6: Commit**

Run:

```powershell
git add apex/commander/telemetry.py tests/test_commander_detectors.py
git commit -m "feat: capture commander extended task metrics"
```

## Task 4: Add Local Deterministic Detectors

**Files:**
- Create: `apex/commander/detectors.py`
- Modify: `tests/test_commander_detectors.py`

- [ ] **Step 1: Add detector tests**

Append to `tests/test_commander_detectors.py`:

```python
from apex.commander.detectors import detect_findings


def envelope_with_stage(stage):
    return {
        "job_id": "job-42",
        "app_id": "app-detectors",
        "stages": [stage],
        "skew_candidates": [],
    }


def base_stage(**overrides):
    stage = {
        "stage_id": 1,
        "task_count": 8,
        "ratio": 1.0,
        "max_records": 1000,
        "median_cold_records": 1000,
        "disk_bytes_spilled": 0,
        "memory_bytes_spilled": 0,
        "jvm_gc_time_ms": 0,
        "executor_run_time_ms": 10000,
        "failure_reasons": [],
    }
    stage.update(overrides)
    return stage


def test_detects_shuffle_spill_candidate():
    findings = detect_findings(envelope_with_stage(base_stage(disk_bytes_spilled=1024 * 1024)))
    assert findings[0]["kind"] == "shuffle_spill_candidate"


def test_detects_gc_pressure_candidate():
    findings = detect_findings(envelope_with_stage(base_stage(jvm_gc_time_ms=3000, executor_run_time_ms=10000)))
    assert findings[0]["kind"] == "gc_pressure_candidate"


def test_detects_oom_candidate():
    findings = detect_findings(envelope_with_stage(base_stage(failure_reasons=["ExecutorLostFailure: Container killed by YARN for exceeding memory limits"])))
    assert findings[0]["kind"] == "oom_candidate"


def test_detects_plan_aqe_candidate_from_event_counts():
    envelope = envelope_with_stage(base_stage())
    envelope["event_counts"] = {"SparkListenerSQLAdaptiveExecutionUpdate": 4}
    findings = detect_findings(envelope)
    assert findings[0]["kind"] == "plan_aqe_replan_candidate"


def test_balanced_stage_has_no_detector_findings():
    assert detect_findings(envelope_with_stage(base_stage())) == []
```

- [ ] **Step 2: Run RED**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_detectors.py -q
```

Expected: fail with `ModuleNotFoundError` for `apex.commander.detectors`.

- [ ] **Step 3: Implement detectors**

Create `apex/commander/detectors.py`:

```python
"""Local deterministic Commander detectors."""

from apex.commander.findings import build_finding

SHUFFLE_SPILL_BYTES_MIN = 1024 * 1024
GC_RATIO_MIN = 0.20
AQE_REPLAN_COUNT_MIN = 3


def detect_findings(envelope):
    findings = []
    findings.extend(_detect_shuffle_spill(envelope))
    findings.extend(_detect_gc_pressure(envelope))
    findings.extend(_detect_oom(envelope))
    findings.extend(_detect_plan_aqe(envelope))
    return findings


def _detect_shuffle_spill(envelope):
    findings = []
    for stage in envelope.get("stages", []):
        spilled = int(stage.get("disk_bytes_spilled") or 0) + int(stage.get("memory_bytes_spilled") or 0)
        if spilled >= SHUFFLE_SPILL_BYTES_MIN:
            findings.append(
                build_finding(
                    "shuffle_spill_candidate",
                    envelope["job_id"],
                    "warning",
                    "medium",
                    {
                        "app_id": envelope.get("app_id"),
                        "stage_id": stage.get("stage_id"),
                        "spilled_bytes": spilled,
                    },
                    [
                        "Validar particionamento e reduzir spill de shuffle antes de escalar recursos.",
                    ],
                )
            )
    return findings


def _detect_gc_pressure(envelope):
    findings = []
    for stage in envelope.get("stages", []):
        run_time = int(stage.get("executor_run_time_ms") or 0)
        gc_time = int(stage.get("jvm_gc_time_ms") or 0)
        ratio = gc_time / run_time if run_time else 0
        if ratio >= GC_RATIO_MIN:
            findings.append(
                build_finding(
                    "gc_pressure_candidate",
                    envelope["job_id"],
                    "warning",
                    "medium",
                    {
                        "app_id": envelope.get("app_id"),
                        "stage_id": stage.get("stage_id"),
                        "gc_ratio": ratio,
                        "jvm_gc_time_ms": gc_time,
                        "executor_run_time_ms": run_time,
                    },
                    [
                        "Avaliar tamanho de particoes, cache e memoria antes de aumentar executores.",
                    ],
                )
            )
    return findings


def _detect_oom(envelope):
    findings = []
    for stage in envelope.get("stages", []):
        reasons = stage.get("failure_reasons") or []
        oom_reasons = [reason for reason in reasons if "memory" in reason.lower() or "oom" in reason.lower()]
        if oom_reasons:
            findings.append(
                build_finding(
                    "oom_candidate",
                    envelope["job_id"],
                    "critical",
                    "high",
                    {
                        "app_id": envelope.get("app_id"),
                        "stage_id": stage.get("stage_id"),
                        "failure_reasons": oom_reasons,
                    },
                    [
                        "Revisar volume por particao, joins e configuracao de memoria antes de reexecutar.",
                    ],
                )
            )
    return findings


def _detect_plan_aqe(envelope):
    event_counts = envelope.get("event_counts") or {}
    replan_count = int(event_counts.get("SparkListenerSQLAdaptiveExecutionUpdate") or 0)
    if replan_count < AQE_REPLAN_COUNT_MIN:
        return []
    return [
        build_finding(
            "plan_aqe_replan_candidate",
            envelope["job_id"],
            "info",
            "medium",
            {
                "app_id": envelope.get("app_id"),
                "adaptive_execution_updates": replan_count,
            },
            [
                "Inspecionar plano AQE para entender mudancas de join, shuffle e coalescing.",
            ],
        )
    ]
```

- [ ] **Step 4: Run GREEN**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_detectors.py -q
```

Expected:

```text
All tests in tests/test_commander_detectors.py pass
```

- [ ] **Step 5: Commit**

Run:

```powershell
git add apex/commander/detectors.py tests/test_commander_detectors.py
git commit -m "feat: add commander local multi-detectors"
```

## Task 5: Include All Detectors In `diagnose_job`

**Files:**
- Modify: `apex/commander/diagnostic_mvp.py`
- Modify: `tests/test_commander_mcp_contract.py`

- [ ] **Step 1: Add test for multiple findings in debug response**

Modify `tests/test_commander_mcp_contract.py`.

In `telemetry_envelope()`, add these fields to the first stage:

```python
"disk_bytes_spilled": 2 * 1024 * 1024,
"memory_bytes_spilled": 0,
"jvm_gc_time_ms": 0,
"executor_run_time_ms": 10000,
"failure_reasons": [],
```

Add a new assertion to `test_debug_job_returns_validated_finding`:

```python
assert [item["kind"] for item in result["findings"]] == [
    "shuffle_skew_candidate",
    "shuffle_spill_candidate",
]
```

- [ ] **Step 2: Run RED**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_mcp_contract.py::test_debug_job_returns_validated_finding -q
```

Expected: fail because `debug_job()` does not return `findings` yet.

- [ ] **Step 3: Modify diagnosis to return findings list**

Modify `apex/commander/diagnostic_mvp.py`:

- import `detect_findings` and `build_finding`;
- keep current `diagnose_job()` return shape for compatibility;
- add `diagnose_findings(store_path, job_id)` returning a list of findings.

Implementation:

```python
from apex.commander.detectors import detect_findings
from apex.commander.findings import build_finding
```

Add:

```python
def diagnose_findings(store_path, job_id):
    envelopes = query_by_job_id(store_path, job_id)
    if not envelopes:
        return []
    envelope = envelopes[-1]
    findings = []
    for candidate in envelope.get("skew_candidates") or []:
        findings.append(
            build_finding(
                "shuffle_skew_candidate",
                job_id,
                "warning",
                "medium",
                {
                    "schema_version": envelope.get("schema_version"),
                    "app_id": envelope.get("app_id"),
                    "stage_id": candidate["stage_id"],
                    "ratio": candidate["ratio"],
                    "hot_records": candidate["hot_records"],
                    "median_cold_records": candidate["median_cold_records"],
                    "task_count": candidate["task_count"],
                },
                [
                    "Validar habilitacao de spark.sql.adaptive.skewJoin.enabled para este job.",
                    "Confirmar chave de join e avaliar salting/repartition antes de aplicar mudanca.",
                ],
            )
        )
    findings.extend(detect_findings(envelope))
    return findings
```

Update `diagnose_job()` so when findings exist, it returns `diagnose_findings(...)[0]` with legacy fields intact. Keep `not_found` and `no_finding` paths unchanged.

- [ ] **Step 4: Modify `debug_job()` to return list**

Modify `apex/commander/mcp_contract.py`:

```python
from apex.commander.diagnostic_mvp import diagnose_findings, diagnose_job
```

Update `debug_job()`:

```python
findings = diagnose_findings(store_path, job_id)
finding = findings[0] if findings else diagnose_job(store_path, job_id)
validations = [validate_finding(item) for item in findings]
...
return {
    "job_id": job_id,
    "finding": finding,
    "findings": findings,
    "validation": validation,
    "validations": validations,
}
```

- [ ] **Step 5: Run GREEN**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_mcp_contract.py -q
```

Expected:

```text
3 passed
```

- [ ] **Step 6: Run Commander focused tests**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_v01.py tests/test_commander_detectors.py tests/test_commander_evidence_validator.py tests/test_commander_mcp_contract.py -q
```

Expected: all focused tests pass.

- [ ] **Step 7: Commit**

Run:

```powershell
git add apex/commander/diagnostic_mvp.py apex/commander/mcp_contract.py tests/test_commander_mcp_contract.py
git commit -m "feat: return validated commander findings list"
```

## Task 6: Extend Evidence Validator To Multiple Finding Kinds

**Files:**
- Modify: `apex/commander/evidence_validator.py`
- Modify: `tests/test_commander_evidence_validator.py`

- [ ] **Step 1: Add validation tests for non-skew findings**

Append to `tests/test_commander_evidence_validator.py`:

```python
def test_accepts_shuffle_spill_candidate():
    finding = {
        "status": "finding",
        "kind": "shuffle_spill_candidate",
        "title": "shuffle_spill_candidate",
        "job_id": "job-42",
        "evidence": {"app_id": "app-1", "stage_id": 3, "spilled_bytes": 2 * 1024 * 1024},
        "recommendations": ["Reduce shuffle spill."],
    }
    assert validate_finding(finding)["accepted"] is True


def test_accepts_gc_pressure_candidate():
    finding = {
        "status": "finding",
        "kind": "gc_pressure_candidate",
        "title": "gc_pressure_candidate",
        "job_id": "job-42",
        "evidence": {"app_id": "app-1", "stage_id": 3, "gc_ratio": 0.3},
        "recommendations": ["Reduce GC pressure."],
    }
    assert validate_finding(finding)["accepted"] is True
```

- [ ] **Step 2: Run RED**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_evidence_validator.py -q
```

Expected: new tests fail because validator only supports `shuffle_skew_candidate`.

- [ ] **Step 3: Update validator**

Modify `apex/commander/evidence_validator.py`:

- derive kind from `finding.get("kind") or finding.get("title")`;
- allow these kinds:

```python
SUPPORTED_KINDS = {
    "shuffle_skew_candidate",
    "shuffle_spill_candidate",
    "gc_pressure_candidate",
    "oom_candidate",
    "plan_aqe_replan_candidate",
}
```

- keep skew-specific ratio/task checks only for `shuffle_skew_candidate`;
- require `stage_id` for stage-level findings except `plan_aqe_replan_candidate`;
- require recommendations for all findings.

- [ ] **Step 4: Run GREEN**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_evidence_validator.py -q
```

Expected: all validator tests pass.

- [ ] **Step 5: Commit**

Run:

```powershell
git add apex/commander/evidence_validator.py tests/test_commander_evidence_validator.py
git commit -m "feat: validate commander multi-detector findings"
```

## Task 7: Update Playbook And Framework Status

**Files:**
- Modify: `docs/playbooks/commander-v01-local.md`
- Modify: `docs/architecture/llm-solution-validation-framework-2026-07-09.md`

- [ ] **Step 1: Add Gate 2 section to playbook**

Append to `docs/playbooks/commander-v01-local.md`:

```markdown
## Gate 2: Detectores locais multiplos

O Gate 2 amplia `debug_job(job_id)` para retornar uma lista de findings validados.

Detectores locais:

- `shuffle_skew_candidate`
- `shuffle_spill_candidate`
- `gc_pressure_candidate`
- `oom_candidate`
- `plan_aqe_replan_candidate`

Rodar:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_detectors.py tests/test_commander_mcp_contract.py tests/test_commander_evidence_validator.py -q --basetemp .pytest-commander-gate2
```
```

- [ ] **Step 2: Update validation framework current status**

Modify `docs/architecture/llm-solution-validation-framework-2026-07-09.md` in "Immediate Codex Backlog":

- mark Gate 1 items as done in prose;
- add Gate 2 detector list as the active next validation gate.

- [ ] **Step 3: Run documentation sanity grep**

Run:

```powershell
rg -n "TBD|TODO|implement later|fill in details|placeholder" docs/playbooks/commander-v01-local.md docs/architecture/llm-solution-validation-framework-2026-07-09.md
```

Expected: no matches.

- [ ] **Step 4: Commit**

Run:

```powershell
git add docs/playbooks/commander-v01-local.md docs/architecture/llm-solution-validation-framework-2026-07-09.md
git commit -m "docs: document commander gate2 detector validation"
```

## Task 8: Final Verification

**Files:**
- Modify: none
- Test: full suite and real-log demo

- [ ] **Step 1: Run full test suite**

Run:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests -q --basetemp .pytest-codex-gate2-final
```

Expected: all tests pass.

- [ ] **Step 2: Run real-log demo**

Run:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python tools/commander_v01_demo.py real_log.ndjson .commander-gate2-store.ndjson --job-id gate2-real-log
```

Expected JSON fields:

```json
{
  "status": "finding",
  "title": "shuffle_skew_candidate",
  "job_id": "gate2-real-log"
}
```

- [ ] **Step 3: Clean generated artifacts**

Run:

```powershell
Remove-Item -LiteralPath .commander-gate2-store.ndjson -Force
```

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

## Handoff After Gate 2

After Gate 2, the next plan should cover:

- ClickHouse adapter with fake-client tests;
- real MCP stdio server around `mcp_contract.py`;
- guarded `apply_fix(job_id, file_path, confirmation)` using `fix_preview` and backups.
