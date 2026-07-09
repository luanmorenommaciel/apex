# Codex Desacoplamento Geradores Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Codex local integration branch for Luan's V1 direction: Spark evidence -> telemetry contract -> ClickHouse-ready store -> deterministic diagnosis -> optional agentic diagnosis -> MCP delivery -> guarded fix.

**Architecture:** Keep the current `apex.commander` harness as the stable contract. Add integration adapters in small steps so Cowork runtime pieces and Kimi validation pieces can be absorbed without raw-merging their large branches.

**Tech Stack:** Python 3, pytest, existing `apex.apexlib`, optional ClickHouse client, optional CrewAI, MCP stdio server contract.

---

## File Structure

- Existing: `apex/commander/telemetry.py` normalizes Spark events into `job_id` envelopes.
- Existing: `apex/commander/clickstack_mvp.py` stores envelopes in local NDJSON.
- Existing: `apex/commander/diagnostic_mvp.py` returns deterministic skew findings.
- Existing: `tools/commander_v01_demo.py` proves the local flow.
- Create: `apex/commander/evidence_validator.py` with deterministic validation rules.
- Create: `apex/commander/runbooks.py` for local JSON/YAML runbook lookup.
- Create: `apex/commander/mcp_contract.py` for testable MCP tool functions before a server wrapper.
- Create: `apex/commander/fix_preview.py` for patch-preview-first fix handling.
- Create: `tests/test_commander_evidence_validator.py`.
- Create: `tests/test_commander_mcp_contract.py`.
- Create: `tests/test_commander_fix_preview.py`.
- Create: `docs/playbooks/codex-v1-integration.md`.

## Task 1: Protect The Branch And Baseline

**Files:**
- Modify: none
- Test: full existing test suite

- [ ] **Step 1: Confirm branch and no upstream**

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

- [ ] **Step 2: Run baseline tests**

Run:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests -q --basetemp .pytest-codex-baseline
```

Expected:

```text
44 passed
```

- [ ] **Step 3: Commit branch analysis and plan**

Run:

```powershell
git add docs/architecture/codex-luan-branch-reassessment-2026-07-09.md docs/superpowers/specs/2026-07-09-codex-desacoplamento-geradores-design.md docs/superpowers/plans/2026-07-09-codex-desacoplamento-geradores.md
git commit -m "docs: plan codex integration for luan commander v1"
```

Expected: one local commit, no push.

## Task 2: Add Evidence Validator

**Files:**
- Create: `apex/commander/evidence_validator.py`
- Create: `tests/test_commander_evidence_validator.py`

- [ ] **Step 1: Write the failing tests**

Add `tests/test_commander_evidence_validator.py`:

```python
from apex.commander.evidence_validator import validate_finding


def valid_finding():
    return {
        "status": "finding",
        "title": "shuffle_skew_candidate",
        "confidence": "medium",
        "job_id": "job-42",
        "evidence": {
            "stage_id": 4,
            "ratio": 31.0,
            "max_records": 160000,
            "median_records": 5200,
        },
        "recommendations": [
            "Enable spark.sql.adaptive.skewJoin.enabled and review hot keys."
        ],
    }


def test_validator_accepts_complete_skew_finding():
    result = validate_finding(valid_finding())
    assert result["accepted"] is True
    assert result["errors"] == []


def test_validator_rejects_missing_job_id():
    finding = valid_finding()
    finding.pop("job_id")
    result = validate_finding(finding)
    assert result["accepted"] is False
    assert "missing job_id" in result["errors"]


def test_validator_rejects_weak_skew_ratio():
    finding = valid_finding()
    finding["evidence"]["ratio"] = 2.0
    result = validate_finding(finding)
    assert result["accepted"] is False
    assert "skew ratio below threshold" in result["errors"]
```

- [ ] **Step 2: Run RED**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_evidence_validator.py -q
```

Expected: fail with `ModuleNotFoundError` for `apex.commander.evidence_validator`.

- [ ] **Step 3: Implement minimal validator**

Create `apex/commander/evidence_validator.py`:

```python
REQUIRED_FIELDS = ("status", "title", "job_id", "evidence", "recommendations")


def validate_finding(finding, *, min_skew_ratio=10.0):
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in finding:
            errors.append(f"missing {field}")

    evidence = finding.get("evidence") or {}
    ratio = evidence.get("ratio")
    if ratio is None:
        errors.append("missing evidence.ratio")
    elif ratio < min_skew_ratio:
        errors.append("skew ratio below threshold")

    if not evidence.get("stage_id") and evidence.get("stage_id") != 0:
        errors.append("missing evidence.stage_id")

    if not finding.get("recommendations"):
        errors.append("missing recommendations")

    return {
        "accepted": not errors,
        "errors": errors,
        "rule_set": "apex.commander.evidence_validator.v1",
    }
```

- [ ] **Step 4: Run GREEN**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_evidence_validator.py -q
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```powershell
git add apex/commander/evidence_validator.py tests/test_commander_evidence_validator.py
git commit -m "feat: validate commander evidence before diagnosis delivery"
```

## Task 3: Add MCP Contract Functions Before Server Runtime

**Files:**
- Create: `apex/commander/mcp_contract.py`
- Create: `tests/test_commander_mcp_contract.py`

- [ ] **Step 1: Write failing MCP contract tests**

Add `tests/test_commander_mcp_contract.py`:

```python
from apex.commander.clickstack_mvp import append_envelope
from apex.commander.mcp_contract import debug_job, explain_evidence


def envelope():
    return {
        "schema_version": "apex.commander.telemetry.v1",
        "job_id": "job-42",
        "app_id": "app-skew",
        "event_counts": {"SparkListenerTaskEnd": 4},
        "stages": [
            {
                "stage_id": 4,
                "task_count": 4,
                "max_records": 160000,
                "median_records": 5200,
            }
        ],
        "skew_candidates": [
            {
                "stage_id": 4,
                "ratio": 31.0,
                "max_records": 160000,
                "median_records": 5200,
            }
        ],
    }


def test_debug_job_returns_validated_finding(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, envelope())
    result = debug_job(store, "job-42")
    assert result["finding"]["title"] == "shuffle_skew_candidate"
    assert result["validation"]["accepted"] is True


def test_explain_evidence_returns_stored_telemetry(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, envelope())
    result = explain_evidence(store, "job-42")
    assert result["job_id"] == "job-42"
    assert result["stages"][0]["stage_id"] == 4
```

- [ ] **Step 2: Run RED**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_mcp_contract.py -q
```

Expected: fail with `ModuleNotFoundError` for `apex.commander.mcp_contract`.

- [ ] **Step 3: Implement contract functions**

Create `apex/commander/mcp_contract.py`:

```python
from apex.commander.clickstack_mvp import query_by_job_id
from apex.commander.diagnostic_mvp import diagnose_job
from apex.commander.evidence_validator import validate_finding


def debug_job(store_path, job_id):
    finding = diagnose_job(store_path, job_id)
    return {
        "job_id": job_id,
        "finding": finding,
        "validation": validate_finding(finding) if finding.get("status") == "finding" else {
            "accepted": False,
            "errors": ["no finding"],
            "rule_set": "apex.commander.evidence_validator.v1",
        },
    }


def explain_evidence(store_path, job_id):
    matches = query_by_job_id(store_path, job_id)
    if not matches:
        return {"job_id": job_id, "status": "not_found", "stages": [], "skew_candidates": []}
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

Expected: `2 passed`.

- [ ] **Step 5: Commit**

```powershell
git add apex/commander/mcp_contract.py tests/test_commander_mcp_contract.py
git commit -m "feat: add commander mcp contract functions"
```

## Task 4: Add Fix Preview Guard

**Files:**
- Create: `apex/commander/fix_preview.py`
- Create: `tests/test_commander_fix_preview.py`

- [ ] **Step 1: Write failing tests for preview-first behavior**

Add `tests/test_commander_fix_preview.py`:

```python
from apex.commander.fix_preview import build_fix_preview


def test_fix_preview_does_not_modify_file(tmp_path):
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
    assert "-df.join(dim, 'id').count()" in preview["diff"]
    assert "+# REVIEW: Add salting before this join" in preview["diff"]
```

- [ ] **Step 2: Run RED**

Run:

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_fix_preview.py -q
```

Expected: fail with `ModuleNotFoundError` for `apex.commander.fix_preview`.

- [ ] **Step 3: Implement preview-only diff**

Create `apex/commander/fix_preview.py`:

```python
from difflib import unified_diff
from pathlib import Path


def build_fix_preview(path, recommendation, *, replacement):
    target = Path(path)
    original = target.read_text(encoding="utf-8")
    diff = "".join(
        unified_diff(
            original.splitlines(keepends=True),
            replacement.splitlines(keepends=True),
            fromfile=str(target),
            tofile=f"{target} (preview)",
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

Expected: `1 passed`.

- [ ] **Step 5: Commit**

```powershell
git add apex/commander/fix_preview.py tests/test_commander_fix_preview.py
git commit -m "feat: add preview-first commander fix guard"
```

## Task 5: Import Cowork Runtime Selectively

**Files:**
- Create: `apex/commander/v1_ingest.py`
- Create: `apex/commander/v1_mcp_server.py`
- Create: `docs/adr/ADR-005-sparklistener-vs-zero-jar.md`
- Create: `scripts/fetch_real_log.py`
- Test: `tests/test_commander_v1_ingest.py`

- [ ] **Step 1: Bring only safe Cowork sources**

Use source inspection instead of raw merge:

```powershell
git show origin/gustocezar/feature/cowork-desacoplamento-geradores:v1-skeleton/ingest/event_log_ingest.py
git show origin/gustocezar/feature/cowork-desacoplamento-geradores:v1-skeleton/mcp/server.py
git show origin/gustocezar/feature/cowork-desacoplamento-geradores:docs/adr/ADR-005-sparklistener-vs-zero-jar.md
git show origin/gustocezar/feature/cowork-desacoplamento-geradores:scripts/fetch_real_log.py
```

Expected: copy only the logic needed behind `apex.commander` interfaces. Do not copy caches or archive folders.

- [ ] **Step 2: Add tests with fake ClickHouse client**

Create `tests/test_commander_v1_ingest.py` with a fake client that records inserted rows. Assert stage/task rows include `job_id`, `app_id`, `stage_id`, task counts and skew fields.

- [ ] **Step 3: Implement adapter**

Create `apex/commander/v1_ingest.py` with an adapter that converts `build_telemetry()` output into ClickHouse-ready rows. Keep network writes behind an injectable client.

- [ ] **Step 4: Run focused tests**

```powershell
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_v1_ingest.py -q
```

Expected: new ingest tests pass without Docker or ClickHouse.

- [ ] **Step 5: Commit**

```powershell
git add apex/commander/v1_ingest.py tests/test_commander_v1_ingest.py docs/adr/ADR-005-sparklistener-vs-zero-jar.md scripts/fetch_real_log.py
git commit -m "feat: add selective commander v1 ingest contract"
```

## Task 6: Import Kimi Validation Concepts

**Files:**
- Create: `apex/commander/runbooks.py`
- Create: `apex/commander/runbooks/skew_on_join.json`
- Create: `apex/commander/runbooks/spill_to_disk.json`
- Create: `scenarios/no_skew_baseline.yaml`
- Test: `tests/test_commander_runbooks.py`

- [ ] **Step 1: Copy runbook semantics, not the whole Go tree**

Read:

```powershell
git show origin/gustocezar/feature/kimi-desacoplamento-geradores:go-apex/runbooks/skew_on_join.json
git show origin/gustocezar/feature/kimi-desacoplamento-geradores:go-apex/runbooks/spill_to_disk.json
```

Expected: convert these into Python-readable runbooks under `apex/commander/runbooks/`.

- [ ] **Step 2: Add runbook lookup tests**

Create `tests/test_commander_runbooks.py` asserting `load_runbook("shuffle_skew_candidate")` returns deterministic remediation text and Spark config hints.

- [ ] **Step 3: Add negative baseline scenario**

Create `scenarios/no_skew_baseline.yaml` with balanced partition metrics and assert it produces no skew finding in a focused test.

- [ ] **Step 4: Commit**

```powershell
git add apex/commander/runbooks.py apex/commander/runbooks scenarios/no_skew_baseline.yaml tests/test_commander_runbooks.py
git commit -m "feat: add commander runbooks and negative baseline"
```

## Task 7: Final Verification And Publish Decision

**Files:**
- Modify: `docs/playbooks/codex-v1-integration.md`

- [ ] **Step 1: Add final playbook**

Create `docs/playbooks/codex-v1-integration.md` with:

```markdown
# Codex V1 Integration Playbook

Branch: `gustocezar/feature/codex-desacoplamento-geradores`

## Local Safety

This branch is local until explicitly pushed. It must not modify `origin/gustocezar/feature/desacoplamento-geradores`.

## Validation

Run:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests -q --basetemp .pytest-codex-final
```

Expected: all tests pass.
```

- [ ] **Step 2: Run full verification**

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests -q --basetemp .pytest-codex-final
```

Expected: all tests pass.

- [ ] **Step 3: Check git state**

```powershell
git status --short --branch
git log --oneline --decorate -5
```

Expected: local commits only; no upstream unless the user explicitly asked for publication.

- [ ] **Step 4: Only push when explicitly requested**

```powershell
git push -u origin gustocezar/feature/codex-desacoplamento-geradores
```

Expected: run this command only after explicit user approval to publish the Codex branch.
