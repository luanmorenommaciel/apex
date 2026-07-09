# Codex Luan Gate 1 Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the Codex branch into the executable validation contract for Luan's architecture: `debug_job(job_id)` over local Spark evidence, evidence validation, negative baseline, and preview-first fix handling.

**Architecture:** This plan works only inside `gustocezar/feature/codex-desacoplamento-geradores`. It does not edit or merge Spike, Cowork, Kimi, DataFlint, or the evaluated remote branch; it imports ideas only by writing tested Codex-local modules. The first gate stays local and deterministic: no ClickHouse, no real MCP server, and no LLM are required yet.

**Tech Stack:** Python standard library, existing `apex.apexlib`, existing `apex.commander` harness, pytest, NDJSON local store.

---

## Branch Rule

All work in this plan must happen on:

```text
gustocezar/feature/codex-desacoplamento-geradores
```

Forbidden in this plan:

- editing remote branches from other LLMs;
- raw-merging `spike/apex-v0.1`, `cowork`, or `kimi`;
- pushing to GitHub;
- adding real LLM calls;
- writing directly to engineer source files as part of fix handling.

## File Structure

- Existing: `apex/commander/telemetry.py` normalizes Spark event logs into telemetry envelopes.
- Existing: `apex/commander/clickstack_mvp.py` appends and queries local NDJSON telemetry.
- Existing: `apex/commander/diagnostic_mvp.py` returns deterministic skew findings.
- Existing: `tools/commander_v01_demo.py` proves the local flow.
- Create: `apex/commander/evidence_validator.py` validates findings before delivery.
- Create: `apex/commander/mcp_contract.py` exposes local read-only tool functions before a real MCP server exists.
- Create: `apex/commander/fix_preview.py` creates diffs without modifying files.
- Create: `tests/test_commander_evidence_validator.py` validates accepted/rejected findings.
- Create: `tests/test_commander_mcp_contract.py` validates `debug_job(job_id)` and `explain_evidence(job_id)`.
- Create: `tests/test_commander_fix_preview.py` validates preview-only fix behavior.
- Modify: `tests/test_commander_v01.py` to add a no-skew baseline test.
- Modify: `docs/playbooks/commander-v01-local.md` to document the new gate.

## Task 1: Confirm Local Branch Safety

**Files:**
- Modify: none
- Test: git state only

- [ ] **Step 1: Confirm the active branch**

Run:

```powershell
git status --short --branch
```

Expected:

```text
## gustocezar/feature/codex-desacoplamento-geradores
```

- [ ] **Step 2: Confirm the branch has no upstream**

Run:

```powershell
git rev-parse --abbrev-ref --symbolic-full-name '@{u}'
```

Expected:

```text
fatal: no upstream configured for branch 'gustocezar/feature/codex-desacoplamento-geradores'
```

- [ ] **Step 3: Run baseline tests**

Run:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests -q --basetemp .pytest-codex-gate1-baseline
```

Expected:

```text
44 passed
```

## Task 2: Add Evidence Validator

**Files:**
- Create: `apex/commander/evidence_validator.py`
- Create: `tests/test_commander_evidence_validator.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_commander_evidence_validator.py`:

```python
from apex.commander.evidence_validator import validate_finding


def valid_skew_finding():
    return {
        "status": "finding",
        "title": "shuffle_skew_candidate",
        "confidence": "medium",
        "job_id": "job-42",
        "evidence": {
            "schema_version": "apex.commander.telemetry.v1",
            "app_id": "app-skew",
            "stage_id": 2,
            "ratio": 29.5,
            "hot_records": 165297,
            "median_cold_records": 5596,
            "task_count": 8,
        },
        "recommendations": [
            "Validar habilitacao de spark.sql.adaptive.skewJoin.enabled para este job."
        ],
    }


def test_accepts_complete_skew_finding():
    result = validate_finding(valid_skew_finding())
    assert result["status"] == "valid"
    assert result["accepted"] is True
    assert result["issues"] == []


def test_rejects_missing_job_id():
    finding = valid_skew_finding()
    finding.pop("job_id")
    result = validate_finding(finding)
    assert result["status"] == "invalid"
    assert "missing_job_id" in result["issues"]


def test_rejects_low_ratio_false_positive():
    finding = valid_skew_finding()
    finding["evidence"]["ratio"] = 2.0
    result = validate_finding(finding)
    assert result["status"] == "invalid"
    assert "skew_ratio_below_threshold" in result["issues"]


def test_rejects_insufficient_task_count():
    finding = valid_skew_finding()
    finding["evidence"]["task_count"] = 1
    result = validate_finding(finding)
    assert result["status"] == "invalid"
    assert "insufficient_task_count" in result["issues"]
```

- [ ] **Step 2: Run RED**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_evidence_validator.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'apex.commander.evidence_validator'
```

- [ ] **Step 3: Implement the validator**

Create `apex/commander/evidence_validator.py`:

```python
"""Evidence validation for Commander findings before delivery to MCP or agents."""

RULE_SET = "apex.commander.evidence_validator.v1"
MIN_SKEW_RATIO = 10.0
MIN_TASK_COUNT = 2


def validate_finding(finding):
    """Return a machine-readable validation result for a Commander finding."""
    issues = []

    if not finding.get("job_id"):
        issues.append("missing_job_id")
    if finding.get("status") != "finding":
        issues.append("not_a_finding")
    if finding.get("title") != "shuffle_skew_candidate":
        issues.append("unsupported_finding_title")

    evidence = finding.get("evidence")
    if not isinstance(evidence, dict):
        issues.append("missing_evidence")
        evidence = {}

    if evidence.get("stage_id") is None:
        issues.append("missing_stage_id")
    if not evidence.get("app_id"):
        issues.append("missing_app_id")

    ratio = evidence.get("ratio")
    if ratio is None:
        issues.append("missing_skew_ratio")
    elif ratio < MIN_SKEW_RATIO:
        issues.append("skew_ratio_below_threshold")

    task_count = evidence.get("task_count")
    if task_count is None:
        issues.append("missing_task_count")
    elif task_count < MIN_TASK_COUNT:
        issues.append("insufficient_task_count")

    if not finding.get("recommendations"):
        issues.append("missing_recommendations")

    return {
        "rule_set": RULE_SET,
        "accepted": not issues,
        "status": "valid" if not issues else "invalid",
        "issues": issues,
    }
```

- [ ] **Step 4: Run GREEN**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_evidence_validator.py -q
```

Expected:

```text
4 passed
```

- [ ] **Step 5: Commit**

Run:

```powershell
git add apex/commander/evidence_validator.py tests/test_commander_evidence_validator.py
git commit -m "feat: validate commander findings before delivery"
```

## Task 3: Add `debug_job(job_id)` Contract

**Files:**
- Create: `apex/commander/mcp_contract.py`
- Create: `tests/test_commander_mcp_contract.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_commander_mcp_contract.py`:

```python
from apex.commander.clickstack_mvp import append_envelope
from apex.commander.mcp_contract import debug_job, explain_evidence


def telemetry_envelope():
    return {
        "schema_version": "apex.commander.telemetry.v1",
        "job_id": "job-42",
        "app_id": "app-skew",
        "event_counts": {"SparkListenerTaskEnd": 8},
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


def test_debug_job_returns_validated_finding(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope())

    result = debug_job(store, "job-42")

    assert result["job_id"] == "job-42"
    assert result["finding"]["title"] == "shuffle_skew_candidate"
    assert result["validation"]["accepted"] is True
    assert result["validation"]["status"] == "valid"


def test_debug_job_reports_not_found(tmp_path):
    result = debug_job(tmp_path / "missing.ndjson", "missing-job")

    assert result["job_id"] == "missing-job"
    assert result["finding"]["status"] == "not_found"
    assert result["validation"]["accepted"] is False


def test_explain_evidence_returns_latest_envelope(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope())

    result = explain_evidence(store, "job-42")

    assert result["status"] == "found"
    assert result["job_id"] == "job-42"
    assert result["stages"][0]["stage_id"] == 2
    assert result["skew_candidates"][0]["ratio"] == 29.5
```

- [ ] **Step 2: Run RED**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_mcp_contract.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'apex.commander.mcp_contract'
```

- [ ] **Step 3: Implement local MCP contract functions**

Create `apex/commander/mcp_contract.py`:

```python
"""Local tool contract for Commander before a real MCP server is introduced."""

from apex.commander.clickstack_mvp import query_by_job_id
from apex.commander.diagnostic_mvp import diagnose_job
from apex.commander.evidence_validator import validate_finding


def debug_job(store_path, job_id):
    """Return a finding plus validation status for one job_id."""
    finding = diagnose_job(store_path, job_id)
    if finding.get("status") == "finding":
        validation = validate_finding(finding)
    else:
        validation = {
            "rule_set": "apex.commander.evidence_validator.v1",
            "accepted": False,
            "status": "invalid",
            "issues": [finding.get("status", "no_finding")],
        }
    return {
        "job_id": job_id,
        "finding": finding,
        "validation": validation,
    }


def explain_evidence(store_path, job_id):
    """Return the latest stored telemetry envelope for one job_id."""
    matches = query_by_job_id(store_path, job_id)
    if not matches:
        return {
            "job_id": job_id,
            "status": "not_found",
            "event_counts": {},
            "stages": [],
            "skew_candidates": [],
        }
    latest = matches[-1]
    return {
        "job_id": job_id,
        "status": "found",
        "app_id": latest.get("app_id"),
        "event_counts": latest.get("event_counts", {}),
        "stages": latest.get("stages", []),
        "skew_candidates": latest.get("skew_candidates", []),
    }
```

- [ ] **Step 4: Run GREEN**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_mcp_contract.py -q
```

Expected:

```text
3 passed
```

- [ ] **Step 5: Commit**

Run:

```powershell
git add apex/commander/mcp_contract.py tests/test_commander_mcp_contract.py
git commit -m "feat: add commander debug job contract"
```

## Task 4: Add Negative Baseline For No-Skew Evidence

**Files:**
- Modify: `tests/test_commander_v01.py`

- [ ] **Step 1: Add a no-skew fixture and test**

Modify `tests/test_commander_v01.py` by adding these helpers after `skew_events()`:

```python
def no_skew_events():
    return [
        app_start("app-balanced"),
        task_end(2, 0, 10000, app_id="app-balanced"),
        task_end(2, 1, 10500, app_id="app-balanced"),
        task_end(2, 2, 9800, app_id="app-balanced"),
        task_end(2, 3, 10100, app_id="app-balanced"),
    ]
```

Add this test after `test_diagnose_job_returns_skew_finding`:

```python
def test_diagnose_job_does_not_flag_balanced_baseline(tmp_path):
    from apex.commander.clickstack_mvp import append_envelope
    from apex.commander.diagnostic_mvp import diagnose_job
    from apex.commander.telemetry import build_telemetry

    store = tmp_path / "clickstack.ndjson"
    append_envelope(store, build_telemetry(no_skew_events(), job_id="balanced-job"))

    finding = diagnose_job(store, "balanced-job")

    assert finding["status"] == "no_finding"
    assert finding["title"] == "no_commander_v01_finding"
```

- [ ] **Step 2: Run focused test**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_v01.py::test_diagnose_job_does_not_flag_balanced_baseline -q
```

Expected:

```text
1 passed
```

- [ ] **Step 3: Run Commander test file**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_v01.py -q
```

Expected:

```text
5 passed
```

- [ ] **Step 4: Commit**

Run:

```powershell
git add tests/test_commander_v01.py
git commit -m "test: add commander no-skew baseline"
```

## Task 5: Add Preview-First Fix Guard

**Files:**
- Create: `apex/commander/fix_preview.py`
- Create: `tests/test_commander_fix_preview.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_commander_fix_preview.py`:

```python
from apex.commander.fix_preview import build_fix_preview


def test_build_fix_preview_returns_diff_without_modifying_file(tmp_path):
    source = tmp_path / "job.py"
    source.write_text("df.join(dim, 'id').count()\n", encoding="utf-8")

    preview = build_fix_preview(
        source,
        "Add salting before the skewed join.",
        replacement="# REVIEW: Add salting before this join\ndf.join(dim, 'id').count()\n",
    )

    assert source.read_text(encoding="utf-8") == "df.join(dim, 'id').count()\n"
    assert preview["mode"] == "preview"
    assert preview["target"] == str(source)
    assert "Add salting before the skewed join." in preview["recommendation"]
    assert "-df.join(dim, 'id').count()" in preview["diff"]
    assert "+# REVIEW: Add salting before this join" in preview["diff"]
```

- [ ] **Step 2: Run RED**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_fix_preview.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'apex.commander.fix_preview'
```

- [ ] **Step 3: Implement preview-only fix module**

Create `apex/commander/fix_preview.py`:

```python
"""Preview-only fix support for Commander recommendations."""

from difflib import unified_diff
from pathlib import Path


def build_fix_preview(path, recommendation, *, replacement):
    """Build a unified diff without modifying the target file."""
    target = Path(path)
    original = target.read_text(encoding="utf-8")
    diff = "".join(
        unified_diff(
            original.splitlines(keepends=True),
            replacement.splitlines(keepends=True),
            fromfile=str(target),
            tofile=f"{target} (apex preview)",
        )
    )
    return {
        "mode": "preview",
        "target": str(target),
        "recommendation": recommendation,
        "diff": diff,
    }
```

- [ ] **Step 4: Run GREEN**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_fix_preview.py -q
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Commit**

Run:

```powershell
git add apex/commander/fix_preview.py tests/test_commander_fix_preview.py
git commit -m "feat: add preview-first commander fix guard"
```

## Task 6: Update Playbook

**Files:**
- Modify: `docs/playbooks/commander-v01-local.md`

- [ ] **Step 1: Add Gate 1 section**

Append this section to `docs/playbooks/commander-v01-local.md`:

```markdown
## Gate 1: Contrato executavel do Luan

Este gate transforma a branch Codex em uma validacao local da arquitetura do Luan.

Componentes:

- `debug_job(job_id)`: retorna diagnostico deterministico e validacao de evidencia.
- `explain_evidence(job_id)`: mostra a telemetria armazenada para o job.
- `EvidenceValidator`: bloqueia findings fracos antes de qualquer agente/LLM.
- Baseline negativo: job balanceado nao pode gerar skew.
- `fix_preview`: gera diff sem alterar arquivo.

Rodar:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_v01.py tests/test_commander_evidence_validator.py tests/test_commander_mcp_contract.py tests/test_commander_fix_preview.py -q --basetemp .pytest-commander-gate1
```

Esperado:

```text
13 passed
```
```

- [ ] **Step 2: Run focused gate tests**

Run:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_v01.py tests/test_commander_evidence_validator.py tests/test_commander_mcp_contract.py tests/test_commander_fix_preview.py -q --basetemp .pytest-commander-gate1
```

Expected:

```text
13 passed
```

- [ ] **Step 3: Commit**

Run:

```powershell
git add docs/playbooks/commander-v01-local.md
git commit -m "docs: document commander gate1 validation"
```

## Task 7: Full Verification

**Files:**
- Modify: none
- Test: full suite and real-log CLI

- [ ] **Step 1: Run full test suite**

Run:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests -q --basetemp .pytest-codex-gate1-final
```

Expected:

```text
All tests pass
```

- [ ] **Step 2: Run real-log demo**

Run:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python tools/commander_v01_demo.py real_log.ndjson .commander-gate1-store.ndjson --job-id gate1-real-log
```

Expected JSON fields:

```json
{
  "status": "finding",
  "title": "shuffle_skew_candidate",
  "job_id": "gate1-real-log"
}
```

- [ ] **Step 3: Clean local artifacts**

Run:

```powershell
Remove-Item -LiteralPath .commander-gate1-store.ndjson -Force
```

Expected: local store file removed.

- [ ] **Step 4: Confirm no remote publication**

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

## Handoff After This Plan

When this plan is complete, the next plan should cover:

- importing Spike detector contracts one by one;
- adding a ClickHouse adapter with fake-client tests;
- wrapping `mcp_contract.py` in a real MCP stdio server;
- turning `fix_preview` into guarded `apply_fix` with explicit confirmation and backup.
