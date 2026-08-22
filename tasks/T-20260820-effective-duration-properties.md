---
id: T-20260820-effective-duration-properties
title: "Add the effective_* fallback properties, plus the raw fields they and tail_outlier need"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260820-tail-outlier-raw-fields]
touches_paths: [engine/src/apex_engine/schema.py, engine/src/apex_engine/clickhouse.py]
creates_paths: []
source_note: "ported from a prior independent APEX baseline, adapted; see T-20260819-retry-pressure-watcher for the same-shape precedent"
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

# Add the effective_* fallback properties, plus the raw fields they and tail_outlier need

> **Why:** `tail_outlier` needs a duration/sample source that prefers the retry-safe `successful_task_*` fields when present, falling back to the legacy all-attempts fields otherwise — and it reads four raw fields directly that its predecessor unit missed.

## Goal

Add computed properties to `StageAggregate` that pick `successful_task_*`
duration fields when a real sample exists, falling back to the legacy
`task_duration_*` fields when it does not — purely additive, zero change to
any existing property or watcher. Also land the four raw fields
`T-20260820-tail-outlier-raw-fields` missed: `task_duration_sample_count`,
`successful_task_duration_p50_ms`, `successful_task_duration_p99_ms`, and
`successful_task_shuffle_read_bytes_p50`.

## Context

`successful_task_sample_count > 0` means at least one non-retry, non-
speculative attempt was measured for that stage; when it is `0`, the legacy
`task_duration_p50_ms` / `p99_ms` (all attempts, including retries) are the
only signal available. This is the same measured-vs-proxy distinction
`memory.py`'s `_runtime_basis()` already applies to `executor_run_time_ms`.

The four raw fields came from the same migration batch as the fields the
predecessor unit landed but were left out of that unit's scope by mistake —
found by reading the full `tail_outlier.py` this contribution adapts from
and cross-checking every field it touches, directly or through a property,
against what is currently reachable. `task_killed_attempt_count` exists on
the schema too but is deliberately excluded: nothing in this contribution
reads it.

**Explicitly not in scope:**
- `skew_ratio` keeps reading the legacy fields directly, exactly as it does
  today. The source `tail_outlier.py` this contribution adapts from *does*
  expect a retry-safe `skew_ratio` (its own SQL computes it that way, and
  `evaluate()` gates on it to avoid double-reporting what the skew watcher
  already would) — so building the watcher itself needs that decision made
  first. This unit stops short of it on purpose: the properties here are
  useful and inert on their own, and do not force the decision.
- A `shuffle_read_volume_ratio` computed property was considered (the
  baseline this adapts from has one) and dropped: nothing reads it.

## Behavior

- **B-1** — GIVEN `successful_task_sample_count > 0` WHEN `effective_task_duration_p50_ms` / `p99_ms` / `max_ms` are read THEN they return the corresponding `successful_task_duration_*` value
- **B-2** — GIVEN `successful_task_sample_count == 0` WHEN the same three properties are read THEN they fall back to `task_duration_p50_ms` / `p99_ms` / `task_duration_max_ms`
- **B-3** — GIVEN either state WHEN `duration_sample_source` is read THEN it returns `"successful_tasks"` or `"legacy_all_attempts"` matching which branch fired, and `duration_sample_count` returns the sample count actually backing the duration figures
- **B-4** — GIVEN this unit lands WHEN `skew_ratio`'s source is inspected THEN it is byte-for-byte unchanged from before this unit
- **B-5** — GIVEN a `spark_events` row with the four raw fields populated WHEN `stage_aggregates()` runs THEN the returned `StageAggregate` carries all four, defaulting to `0` for historical rows

## Success Criteria

```bash
# eval_1: prefers successful_task_* when a real sample exists
eval_1() {
  ( cd engine && uv run --extra dev python -c "
from apex_engine import StageAggregate
s = StageAggregate.model_validate({
    'job_id': 'j', 'stage_id': 1,
    'task_duration_p50_ms': 100, 'task_duration_p99_ms': 900, 'task_duration_max_ms': 4000,
    'successful_task_duration_p50_ms': 80, 'successful_task_duration_p99_ms': 300,
    'successful_task_duration_max_ms': 500, 'successful_task_sample_count': 12,
})
assert s.effective_task_duration_p50_ms == 80
assert s.effective_task_duration_p99_ms == 300
assert s.effective_task_duration_max_ms == 500
assert s.duration_sample_source == 'successful_tasks'
assert s.duration_sample_count == 12
" )
}

# eval_2: falls back to legacy fields when no successful-task sample exists
eval_2() {
  ( cd engine && uv run --extra dev python -c "
from apex_engine import StageAggregate
s = StageAggregate.model_validate({
    'job_id': 'j', 'stage_id': 1,
    'task_duration_p50_ms': 100, 'task_duration_p99_ms': 900, 'task_duration_max_ms': 4000,
    'task_duration_sample_count': 50, 'successful_task_sample_count': 0,
})
assert s.effective_task_duration_p50_ms == 100
assert s.effective_task_duration_p99_ms == 900
assert s.effective_task_duration_max_ms == 4000
assert s.duration_sample_source == 'legacy_all_attempts'
assert s.duration_sample_count == 50
" )
}

# eval_3: tail_ratio guarded against div-by-zero; all four raw fields reachable
eval_3() {
  ( cd engine && uv run --extra dev python -c "
from apex_engine import StageAggregate
s = StageAggregate.model_validate({'job_id': 'j', 'stage_id': 1})
assert s.tail_ratio == 0.0
assert s.task_duration_sample_count == 0
assert s.successful_task_duration_p50_ms == 0
assert s.successful_task_duration_p99_ms == 0
assert s.successful_task_shuffle_read_bytes_p50 == 0
s2 = StageAggregate.model_validate({
    'job_id': 'j', 'stage_id': 1,
    'successful_task_duration_max_ms': 500, 'successful_task_duration_p50_ms': 50,
    'successful_task_sample_count': 5, 'successful_task_shuffle_read_bytes_p50': 4096,
})
assert s2.tail_ratio == 10.0
" )
  ( cd engine && for col in task_duration_sample_count successful_task_duration_p50_ms \
      successful_task_duration_p99_ms successful_task_shuffle_read_bytes_p50; do
      grep -q "$col" src/apex_engine/clickhouse.py || exit 1
    done )
}

# eval_4: skew_ratio's existing definition is untouched, and full suite is green
eval_4() {
  ( cd engine && grep -A2 'def skew_ratio' src/apex_engine/schema.py | grep -q 'self.task_duration_p99_ms / self.task_duration_p50_ms' \
    && uv run --extra dev pytest -q )
}
```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "prefers successful_task_* when a real sample exists"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-3]
    terminal: true
    expected_duration_sec: 15
  - id: eval_2
    description: "falls back to legacy fields with no successful-task sample"
    runnable: bash
    check_type: deterministic
    verifies: [B-2, B-3]
    terminal: true
    expected_duration_sec: 15
  - id: eval_3
    description: "tail_ratio guarded against div-by-zero; four raw fields reachable"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-5]
    terminal: true
    expected_duration_sec: 15
  - id: eval_4
    description: "skew_ratio untouched, full engine suite green"
    runnable: bash
    check_type: deterministic
    verifies: [B-4]
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

Pure code revert — new `@property` methods plus four raw fields and four SQL
columns, no state, no DDL, no migration. Revert the two touched files; `git
status` returns to clean.

## Observability Hooks

(none — pure computed properties and additive raw fields, no runtime surface)

## Anti-Patterns

- Changing `skew_ratio` to route through `effective_task_duration_p50_ms` /
  `p99_ms` in this unit — real design question, blocks the `tail_outlier`
  watcher itself, but is not a side effect of adding these properties.
- Silently changing div-by-zero behavior on any *existing* property while
  touching this file.
- Adding `shuffle_read_volume_ratio` or any other computed property nothing
  in this contribution actually reads.

## Do-Not-Touch

- `skew_ratio` — must remain byte-for-byte identical (eval_4 checks this)
- `engine/src/apex_engine/watchers/` — no watcher in this unit
- `task_killed_attempt_count` — exists on the schema, deliberately not
  landed here; nothing in this contribution reads it

## Open Questions

- Whether `skew_ratio` should route through `effective_task_duration_p50_ms`
  / `p99_ms` — real design question, blocks building `tail_outlier` itself,
  needs a maintainer decision, not resolved by this unit.
