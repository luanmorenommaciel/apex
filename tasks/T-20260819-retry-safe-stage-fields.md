---
id: T-20260819-retry-safe-stage-fields
title: "Land the retry-safe attempt counters on StageAggregate"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
touches_paths: [engine/src/apex_engine/schema.py, engine/src/apex_engine/clickhouse.py]
creates_paths: []
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

# Land the retry-safe attempt counters on StageAggregate

> **Why:** three columns the JAR already emits and infra already stores are invisible to every Python consumer in engine, because nothing selects them or models them.

## Goal

Add `task_attempt_count`, `task_failed_attempt_count`, and
`task_counted_failure_attempt_count` to `StageAggregate` and to the SQL that
populates it, plus the additive `RETRY_PRESSURE` `FindingType` value the next
task will use. No watcher reads these yet — this unit only makes the data
reachable.

## Context

Migrations 034-039 (already on `main`) put these three columns on
`apex.spark_events`; the JAR emits all three. `STAGE_AGGREGATES_SQL` in
`clickhouse.py` does not select any of them, and `StageAggregate` in
`schema.py` has no fields for them. CONTRACT.md v0.5's `0-on-empty semantics`
convention applies: historical rows written before these columns existed
must default to `0`, not raise or null out.

`findings.type` is an open `String` column (contract precedent: `TASK_SKEW`
was added the same way), so adding `RETRY_PRESSURE` to the enum is additive,
not a schema change.

## Behavior

- **B-1** — GIVEN a `spark_events` row with the three columns populated WHEN `stage_aggregates()` runs THEN the returned `StageAggregate` carries all three values
- **B-2** — GIVEN a row written before these columns existed WHEN `stage_aggregates()` runs THEN the three fields default to `0`, matching CONTRACT.md's 0-on-empty convention, not an exception
- **B-3** — GIVEN the `FindingType` enum WHEN `RETRY_PRESSURE` is added THEN no existing member is renamed, reordered, or removed

## Success Criteria

```bash
# eval_1: the SQL constant now selects all three columns
eval_1() {
  ( cd engine && grep -q 'task_attempt_count' src/apex_engine/clickhouse.py \
    && grep -q 'task_failed_attempt_count' src/apex_engine/clickhouse.py \
    && grep -q 'task_counted_failure_attempt_count' src/apex_engine/clickhouse.py )
}

# eval_2: StageAggregate accepts and defaults the three fields
eval_2() {
  ( cd engine && uv run --extra dev python -c "
from apex_engine import StageAggregate
s = StageAggregate.model_validate({'job_id': 'j', 'stage_id': 1})
assert s.task_attempt_count == 0
assert s.task_failed_attempt_count == 0
assert s.task_counted_failure_attempt_count == 0
" )
}

# eval_3: RETRY_PRESSURE exists and is additive (nothing else in the enum moved)
eval_3() {
  ( cd engine && uv run --extra dev python -c "
from apex_engine import FindingType
assert FindingType.RETRY_PRESSURE == 'RETRY_PRESSURE'
assert FindingType.SKEW_ON_JOIN == 'SKEW_ON_JOIN'
" )
}

# eval_4: full engine suite still green
eval_4() {
  ( cd engine && uv run --extra dev pytest -q )
}
```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "SQL constant selects the three retry-safe columns"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 10
  - id: eval_2
    description: "StageAggregate accepts and defaults the three fields"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 15
  - id: eval_3
    description: "RETRY_PRESSURE is additive on FindingType"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
    terminal: true
    expected_duration_sec: 15
  - id: eval_4
    description: "full engine suite still green, no regression"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 60
retry_policy:
  max_iterations: 15
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

Pure code revert — no DDL, no migration. Revert both touched files; `git
status` returns to clean against `origin/main`.

## Observability Hooks

(none — additive model fields and an additive enum value, no runtime surface)

## Anti-Patterns

- Reading the three columns without the 0-on-empty fallback, which would
  raise or misreport on historical rows written before the migration.
- Wiring a watcher in this unit — that is the next task, kept separate so
  each stays within its effort-gate write-path budget.

## Do-Not-Touch

- `infra/sql/` — migrations already landed
- `jar/` — already emits the three fields
- `engine/src/apex_engine/watchers/` — no watcher in this unit

## Open Questions

(none — this task is fully specified)
