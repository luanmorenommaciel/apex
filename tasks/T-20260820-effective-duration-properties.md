---
id: T-20260820-effective-duration-properties
title: "Add the effective_* fallback properties, plus the p50 shuffle field they need"
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

# Add the effective_* fallback properties, plus the p50 shuffle field they need

> **Why:** the `tail_outlier` watcher needs a duration/sample source that prefers the retry-safe `successful_task_*` fields when present and falls back to the legacy all-attempts fields otherwise — and it reads `successful_task_shuffle_read_bytes_p50` directly, a raw field its predecessor unit missed.

## Goal

Add computed properties to `StageAggregate` that pick `successful_task_*`
duration fields when a real sample exists, falling back to the legacy
`task_duration_*` fields when it does not — purely additive, zero change to
any existing property or watcher. Also land the one raw field
`T-20260820-tail-outlier-raw-fields` missed:
`successful_task_shuffle_read_bytes_p50`, which `tail_outlier` reads
directly rather than through a computed property.

## Context

`successful_task_sample_count > 0` means at least one non-retry, non-
speculative attempt was measured for that stage; when it is `0`, the legacy
`task_duration_p50_ms` / `p99_ms` (all attempts, including retries) are the
only signal available. This is precisely the same measured-vs-proxy
distinction `memory.py`'s `_runtime_basis()` already applies to
`executor_run_time_ms` — same shape, new field family.

`successful_task_shuffle_read_bytes_p50` came from the same migration batch
as the fields the predecessor unit landed, but was left out of that unit's
scope by mistake — `tail_outlier.py` (the source this contribution adapts)
reads it as a raw stage attribute for its finding details, not through a
computed ratio, so it belongs here as a plain field, not a property.

**Explicitly not in scope:**
- `skew_ratio` keeps reading the legacy fields directly, exactly as it does
  today. Whether it should switch to routing through the new `effective_*`
  properties is a real design question — it would change an existing,
  already-shipped watcher's output for any stage that has retry data — and
  is a separate decision, not a side effect of this unit.
- A `shuffle_read_volume_ratio` computed property was considered (the
  baseline this adapts from has one) and dropped: nothing in `tail_outlier`
  or any other consumer reads it, so it would be unused surface.

## Behavior

- **B-1** — GIVEN `successful_task_sample_count > 0` WHEN `effective_task_duration_p50_ms` / `p99_ms` / `max_ms` are read THEN they return the corresponding `successful_task_duration_*` value
- **B-2** — GIVEN `successful_task_sample_count == 0` WHEN the same three properties are read THEN they fall back to `task_duration_p50_ms` / `p99_ms` / `task_duration_max_ms`
- **B-3** — GIVEN either state WHEN `duration_sample_source` is read THEN it returns `"successful_tasks"` or `"legacy_all_attempts"` matching which branch fired, and `duration_sample_count` returns the sample count actually backing the duration figures
- **B-4** — GIVEN this unit lands WHEN `skew_ratio`'s source is inspected THEN it is byte-for-byte unchanged from before this unit
- **B-5** — GIVEN a `spark_events` row with `successful_task_shuffle_read_bytes_p50` populated WHEN `stage_aggregates()` runs THEN the returned `StageAggregate` carries that value, defaulting to `0` for historical rows

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

# eval_3: tail_ratio is guarded against div-by-zero, and the p50 shuffle field is reachable
eval_3() {
  ( cd engine && uv run --extra dev python -c "
from apex_engine import StageAggregate
s = StageAggregate.model_validate({'job_id': 'j', 'stage_id': 1})
assert s.tail_ratio == 0.0
assert s.successful_task_shuffle_read_bytes_p50 == 0
s2 = StageAggregate.model_validate({
    'job_id': 'j', 'stage_id': 1,
    'successful_task_duration_max_ms': 500, 'successful_task_duration_p50_ms': 50,
    'successful_task_sample_count': 5, 'successful_task_shuffle_read_bytes_p50': 4096,
})
assert s2.tail_ratio == 10.0
assert s2.successful_task_shuffle_read_bytes_p50 == 4096
" )
  ( cd engine && grep -q 'successful_task_shuffle_read_bytes_p50' src/apex_engine/clickhouse.py )
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
    description: "tail_ratio guarded against div-by-zero; p50 shuffle field reachable"
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

Pure code revert — new `@property` methods plus one raw field and one SQL
column, no state, no DDL, no migration. Revert the two touched files; `git
status` returns to clean.

## Observability Hooks

(none — pure computed properties and one additive raw field, no runtime surface)

## Anti-Patterns

- Changing `skew_ratio` to route through `effective_task_duration_p50_ms` /
  `p99_ms` in this unit — real design question, separate decision, not a
  side effect of adding new properties.
- Silently changing div-by-zero behavior on any *existing* property while
  touching this file.
- Adding `shuffle_read_volume_ratio` or any other computed property nothing
  in this contribution actually reads.

## Do-Not-Touch

- `skew_ratio` — must remain byte-for-byte identical (eval_4 checks this)
- `engine/src/apex_engine/watchers/` — no watcher in this unit

## Open Questions

(none — this task is fully specified)
