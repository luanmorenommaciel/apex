# Luan V0.1 Commander Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local, no-push V0.1 harness for the Commander flow: Spark evidence -> listener contract -> ClickStack-like store -> diagnosis by `job_id`.

**Architecture:** This first cut uses existing Spark event logs as input and a file-backed NDJSON store as the ClickStack MVP. It does not claim to be a real JVM SparkListener, real ClickHouse, CrewAI, or MCP server yet; it creates the contract those components must satisfy.

**Tech Stack:** Python standard library, existing `apex.apexlib`, pytest, NDJSON files.

---

## File Structure

- Create `apex/commander/__init__.py`: package marker for V0.1 harness.
- Create `apex/commander/telemetry.py`: normalize Spark event logs into telemetry envelopes keyed by `job_id`.
- Create `apex/commander/clickstack_mvp.py`: append/query NDJSON store that stands in for ClickStack during local development.
- Create `apex/commander/diagnostic_mvp.py`: deterministic diagnosis over stored telemetry for a `job_id`.
- Create `tools/commander_v01_demo.py`: local CLI demo for the Commander flow.
- Create `tests/test_commander_v01.py`: TDD coverage for envelope, store, diagnosis, and CLI.
- Create `docs/playbooks/commander-v01-local.md`: reproducible local playbook.

## Task 1: Telemetry Envelope Contract

**Files:**
- Create: `tests/test_commander_v01.py`
- Create: `apex/commander/__init__.py`
- Create: `apex/commander/telemetry.py`

- [ ] **Step 1: Write failing tests for Spark event normalization**

Add tests that build small Spark-like events and assert `build_telemetry()` returns a `job_id`, `app_id`, event counters, stage summaries, and skew candidates.

- [ ] **Step 2: Run RED**

Run: `uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_v01.py -q`

Expected: fail with `ModuleNotFoundError: No module named 'apex.commander'`.

- [ ] **Step 3: Implement minimal telemetry module**

Implement:

- `build_telemetry(events, job_id=None)`
- `infer_job_id(events)`
- `stage_summaries(events)`

Use `apex.apexlib.shuffle_read_by_stage()` and `apex.apexlib.skew_metrics()`.

- [ ] **Step 4: Run GREEN**

Run the same test command. Expected: tests pass.

## Task 2: ClickStack MVP Store

**Files:**
- Modify: `tests/test_commander_v01.py`
- Create: `apex/commander/clickstack_mvp.py`

- [ ] **Step 1: Write failing tests for append/query**

Assert the store appends telemetry envelopes as NDJSON and can query by `job_id`.

- [ ] **Step 2: Run RED**

Expected: fail because `apex.commander.clickstack_mvp` does not exist.

- [ ] **Step 3: Implement minimal file-backed store**

Implement:

- `append_envelope(path, envelope)`
- `query_by_job_id(path, job_id)`

- [ ] **Step 4: Run GREEN**

Run commander tests and ensure they pass.

## Task 3: Diagnosis by Job ID

**Files:**
- Modify: `tests/test_commander_v01.py`
- Create: `apex/commander/diagnostic_mvp.py`

- [ ] **Step 1: Write failing tests for diagnosis**

Assert a job with a skewed stage returns:

- status `finding`
- title `shuffle_skew_candidate`
- confidence `medium`
- evidence with stage id and ratio
- recommendation that mentions AQE skew join

- [ ] **Step 2: Run RED**

Expected: fail because diagnosis module does not exist.

- [ ] **Step 3: Implement deterministic diagnosis**

Implement `diagnose_job(store_path, job_id)` using `query_by_job_id()`.

- [ ] **Step 4: Run GREEN**

Run commander tests and ensure they pass.

## Task 4: Local CLI Demo

**Files:**
- Modify: `tests/test_commander_v01.py`
- Create: `tools/commander_v01_demo.py`

- [ ] **Step 1: Write failing CLI smoke test**

Run the CLI over a tiny NDJSON input and assert stdout contains `shuffle_skew_candidate`.

- [ ] **Step 2: Run RED**

Expected: fail because CLI script does not exist.

- [ ] **Step 3: Implement CLI**

CLI arguments:

```text
python tools/commander_v01_demo.py <event-log.ndjson> <store.ndjson> --job-id <job-id>
```

Behavior:

1. Read Spark events with `apex.apexlib.read_events()`.
2. Build telemetry envelope.
3. Append envelope to store.
4. Diagnose by `job_id`.
5. Print JSON diagnosis.

- [ ] **Step 4: Run GREEN**

Run commander tests and CLI manually.

## Task 5: Playbook and Full Verification

**Files:**
- Create: `docs/playbooks/commander-v01-local.md`

- [ ] **Step 1: Add playbook**

Document:

- branch name: `local/luan-v01-commander`
- no-push rule
- local harness scope
- demo command
- limitations versus real SparkListener, ClickStack, CrewAI, and MCP

- [ ] **Step 2: Run full verification**

Run:

```powershell
$env:PYTHONUTF8='1'; uv run --offline --with-requirements requirements.txt python -m pytest tests -q --basetemp .pytest-luan-v01-final
```

Expected: all tests pass.

- [ ] **Step 3: Confirm no remote tracking/push**

Run:

```powershell
git status --short --branch
git log -1 --oneline --decorate
```

Expected: branch is `local/luan-v01-commander`, no remote push performed.
