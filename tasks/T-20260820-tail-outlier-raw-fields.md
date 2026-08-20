---
id: T-20260820-tail-outlier-raw-fields
title: "Land the raw fields the tail-outlier watcher needs"
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
created: "2026-08-20T00:00:00Z"
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

# Land the raw fields the tail-outlier watcher needs

> **Why:** six columns from CONTRACT.md v0.5 exist on `apex.spark_events` and are emitted by the JAR, but `StageAggregate` and `STAGE_AGGREGATES_SQL` do not carry any of them yet — the same reachability gap `T-20260819-retry-safe-stage-fields` closed for the retry counters.

## Goal

Add `task_duration_max_ms`, `successful_task_duration_max_ms`,
`successful_task_sample_count`, `successful_task_shuffle_read_bytes_max`,
`successful_task_shuffle_read_bytes_sample_count`, and
`task_speculative_attempt_count` to `StageAggregate` and to the SQL that
populates it. No watcher and no computed property reads them yet — this unit
only makes the data reachable, exactly like its predecessor did for the
retry-safe counters.

## Context

Migrations 034-039 (already on `main`) put all six columns on
`apex.spark_events`, typed `Int32`/`Int64` with `DEFAULT 0`; the JAR emits
all six. None is selected by `STAGE_AGGREGATES_SQL` and none has a field on
`StageAggregate`. CONTRACT.md v0.5's `0-on-empty semantics` applies the same
way it did for the retry counters: historical rows default to `0`, they do
not raise.

This is deliberately scoped to raw fields only. The computed `effective_*`
fallback properties (prefer `successful_task_*` when populated, else the
legacy field) and the `tail_outlier` watcher itself are separate follow-up
units — this one only lands what they will read.

## Behavior

- **B-1** — GIVEN a `spark_events` row with all six columns populated WHEN `stage_aggregates()` runs THEN the returned `StageAggregate` carries all six values
- **B-2** — GIVEN a row written before these columns existed WHEN `stage_aggregates()` runs THEN all six fields default to `0`, not an exception
- **B-3** — GIVEN the existing `skew_ratio` property WHEN this unit lands THEN its definition is byte-for-byte unchanged — this unit adds fields, it does not touch any existing property or watcher behavior

## Success Criteria

```bash
# eval_1: the SQL constant now selects all six columns
eval_1() {
  ( cd engine && for col in task_duration_max_ms successful_task_duration_max_ms \
      successful_task_sample_count successful_task_shuffle_read_bytes_max \
      successful_task_shuffle_read_bytes_sample_count task_speculative_attempt_count; do
      grep -q "$col" src/apex_engine/clickhouse.py || exit 1
    done )
}

# eval_2: StageAggregate accepts and defaults all six fields
eval_2() {
  ( cd engine && uv run --extra dev python -c "
from apex_engine import StageAggregate
s = StageAggregate.model_validate({'job_id': 'j', 'stage_id': 1})
for f in ['task_duration_max_ms', 'successful_task_duration_max_ms',
          'successful_task_sample_count', 'successful_task_shuffle_read_bytes_max',
          'successful_task_shuffle_read_bytes_sample_count', 'task_speculative_attempt_count']:
    assert getattr(s, f) == 0, f
" )
}

# eval_3: skew_ratio's source is untouched by this unit
eval_3() {
  ( cd engine && grep -A2 'def skew_ratio' src/apex_engine/schema.py | grep -q 'self.task_duration_p99_ms / self.task_duration_p50_ms' )
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
    description: "SQL constant selects all six new columns"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 10
  - id: eval_2
    description: "StageAggregate accepts and defaults all six fields"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 15
  - id: eval_3
    description: "skew_ratio's existing definition is untouched"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
    terminal: true
    expected_duration_sec: 5
  - id: eval_4
    description: "full engine suite still green, no regression"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 90
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
status` returns to clean.

## Observability Hooks

(none — additive model fields, no runtime surface)

## Anti-Patterns

- Changing `skew_ratio` or any other existing property's definition in this
  unit — that is a behavior change to a shipped watcher and needs its own
  decision, not a side effect of adding fields.
- Adding the `effective_*` computed properties here — separate unit, so each
  stays reviewable and revertable on its own.

## Do-Not-Touch

- `infra/sql/` — migrations already landed
- `jar/` — already emits all six fields
- `engine/src/apex_engine/watchers/` — no watcher in this unit
- `skew_ratio` and every other existing `@property` on `StageAggregate`

## Open Questions

(none — this task is fully specified)
