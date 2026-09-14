---
id: T-20260819-retry-pressure-watcher
title: "Add the retry-pressure watcher and register it"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 20
agent: any
parent: (none)
depends_on: [T-20260819-retry-safe-stage-fields]
touches_paths: [engine/src/apex_engine/watchers/__init__.py, engine/tests/test_watchers.py]
creates_paths: [engine/src/apex_engine/watchers/retry_pressure.py]
source_note: "CONTRACT.md v0.5 changelog: 'Affects: engine/memory/verify (read)'"
created: "2026-08-19T00:00:00Z"
tags: []
owner: (none)
priority: P2
severity: feature
due_date: (none)
precondition: (none)
blocked_reason: (none)
security_class: (none)
source_action_item: (none)
tracker_ref: (none)
execution_backend: any
signed_off: false
signed_off_by: (none)
signed_off_at: (none)
accepted: false
accepted_by: (none)
accepted_at: (none)
---

# Add the retry-pressure watcher and register it

> **Why:** the three retry-safe counters are now on `StageAggregate`, but nothing evaluates them — the finding they should produce still does not exist.

## Goal

Add a sixth Tier-1 watcher that reports how much of a stage's scheduler
failure budget was consumed by counted task failures, and register it so it
runs in `run_all_offline` / `run_all` like the other five.

## Context

`task_counted_failure_attempt_count` says whether a failed attempt counted
against Spark's own scheduler retry budget; it does not say whether the root
cause was application code or infrastructure. This watcher reports budget
consumption as a fact and stops there — it does not attempt cause inference.
`watchers/__init__.py` currently documents and enumerates "the five
deterministic watchers" / "the five contract watchers"; both phrases become
wrong the moment a sixth is registered and must be corrected in the same
unit, not left stale.

## Behavior

- **B-1** — GIVEN a stage with `task_counted_failure_attempt_count > 0` WHEN the watcher evaluates it THEN it returns a `RETRY_PRESSURE` finding at `INFO` severity citing the counted-vs-observed attempt counts
- **B-2** — GIVEN a stage with `task_counted_failure_attempt_count == 0` WHEN the watcher evaluates it THEN it returns `None`, even when `task_failed_attempt_count > 0` (killed or speculative attempts that never counted against the budget are not this finding)
- **B-3** — GIVEN the full watcher list WHEN it runs against a job with zero counted failures THEN `RETRY_PRESSURE` never appears among the findings, and the watcher is reachable through `STAGE_WATCHERS` / `run_all_offline` like the other five

## Success Criteria

```bash
# eval_1: new watcher's own unit tests pass
eval_1() {
  ( cd engine && uv run --extra dev pytest tests/test_watchers.py -k retry_pressure -q )
}

# eval_2: the watcher is actually registered, not just importable
eval_2() {
  ( cd engine && uv run --extra dev python -c "
from apex_engine.watchers import retry_pressure, STAGE_WATCHERS
assert retry_pressure in STAGE_WATCHERS, 'not registered in STAGE_WATCHERS'
" )
}

# eval_3: full engine suite still green — no regression in the other five watchers
eval_3() {
  ( cd engine && uv run --extra dev pytest -q )
}

# eval_4: the stale "five watchers" prose has been updated, not left to mislead the next reader
eval_4() {
  ( cd engine && ! grep -n 'the five deterministic watchers\|The five contract watchers' src/apex_engine/watchers/__init__.py )
}
```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "new watcher's own unit tests pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "the watcher is registered in STAGE_WATCHERS, not just importable"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
    terminal: true
    expected_duration_sec: 15
  - id: eval_3
    description: "full engine suite still green, no regression"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 60
  - id: eval_4
    description: "stale five-watchers prose updated to six"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
    terminal: true
    expected_duration_sec: 5
retry_policy:
  max_iterations: 20
  circuit_breaker_no_progress: 3
  on_terminal_failure: park_with_context
agent_contract:
  version: 2
  read: [intent, behavior, contract, guardrails]
  produce: [code, tests]
  required_tools: [git, bash, uv]
  timeout_minutes: 30
  sandbox_type: host
  output_artifacts: []
  mcp_dependencies: []
  emit: [pass, fail, retry_with_reason, parked_with_context]
  backend_metadata: {}
```

## Exit Check

```bash
eval_1 && eval_2 && eval_3 && eval_4
```

## Rollback Plan

Pure code revert — no DDL, no migration, no data touched. Revert the two
touched files and delete the created watcher file; `git status` returns to
clean against `origin/main`.

## Observability Hooks

(none — a pure deterministic Python rule over already-materialized rows,
same as the other five watchers; no new observability surface)

## Anti-Patterns

- Inferring application-code-vs-infrastructure root cause from the counted-
  failure flag alone — Spark's own semantics don't support that distinction
  (see Why / Context).
- Bundling the `tail_outlier` watcher (`successful_task_*` columns, a
  different finding type) into this unit — separate task.
- Leaving the "five watchers" prose stale once a sixth is registered.

## Do-Not-Touch

- `infra/sql/` — all required migrations already landed; this unit is engine-only
- `jar/` — already emits the three fields; no jar change needed
- `engine/src/apex_engine/watchers/tail_outlier.py` — not created here, separate task

## Open Questions

(none — this task is fully specified)
