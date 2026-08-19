---
id: T-20260819-runs-read-layer
title: "Add ReadStore.runs for bounded run discovery"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
touches_paths: [serve/src/apex_mcp/ch.py, serve/tests/test_ch.py]
creates_paths: []
source_note: "docs/lanes/SERVE-LEGS.md"
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

# Add ReadStore.runs for bounded run discovery

> **Why:** Every existing tool demands a job_id the user has no way to obtain from Apex, so the lane can diagnose a run but cannot help you find one.

## Goal

One bounded read returning recent runs aggregated per job_id, filterable by app_name.

## Context

spark_events is ORDER BY (job_id, stage_id, stage_attempt) PARTITION BY toYYYYMM(ts), so a time-ordered listing is a full scan unless bounded. The since window must reach the WHERE clause as a bound parameter so partitions prune. app_name is user-controlled and must bind, never interpolate.

## Behavior

- **B-1** — GIVEN a store holding several runs WHEN runs() is called THEN it returns one row per job_id with app_id, app_name, first and last ts, and stage count
- **B-2** — GIVEN an app_name filter WHEN runs() is called THEN only that application's runs come back, and the filter binds server-side
- **B-3** — GIVEN a limit WHEN runs() is called THEN at most that many rows return, newest first
- **B-4** — GIVEN an app_name containing a quote or SQL fragment WHEN runs() is called THEN it binds and returns zero rows rather than erroring or widening the query

## Success Criteria

```bash
# eval_1: the run-discovery tests exist and pass
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_ch.py::test_runs_aggregates_one_row_per_job" "tests/test_ch.py::test_runs_filters_by_app_name" "tests/test_ch.py::test_runs_binds_hostile_app_name" )
}

# eval_2: the whole ClickHouse layer suite stays green
eval_2() {
  ( cd serve && uv run --extra dev pytest tests/test_ch.py )
}

# eval_3: the runs SQL bounds by ts so partitions can prune
eval_3() {
  ( cd serve && uv run python -c "from apex_mcp import ch; s=ch.RUNS_SQL; assert 'GROUP BY job_id' in s, s; assert 'ts >=' in s or 'ts>' in s, 'unbounded scan: no ts predicate'; assert '{' in s, 'no bound parameter'" )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the run-discovery tests exist and pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-4]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "the whole ClickHouse layer suite stays green"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
    terminal: true
    expected_duration_sec: 30
  - id: eval_3
    description: "the runs SQL bounds by ts so partitions can prune"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-3]
    terminal: true
    expected_duration_sec: 15
retry_policy:
  max_iterations: 15
  circuit_breaker_no_progress: 3
  on_terminal_failure: park_with_context
agent_contract:
  version: 2
  read: [intent, behavior, contract, guardrails]
  produce: [code, tests]
  required_tools: [git, bash]
  timeout_minutes: 30
  sandbox_type: host
  output_artifacts: []
  mcp_dependencies: []
  emit: [pass, fail, retry_with_reason, parked_with_context]
  backend_metadata: {}
```

## Exit Check

```bash
eval_1 && eval_2 && eval_3
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Interpolating app_name or limit into the SQL; both are user-controlled.
- An unbounded scan with no ts predicate, which defeats partition pruning on a MergeTree keyed by job_id.
- Returning per-stage rows and expecting the caller to aggregate.

## Do-Not-Touch

- `serve/src/apex_mcp/server.py`
- `serve/src/apex_mcp/models.py`
- `serve/src/apex_mcp/diagnose.py`

## Open Questions

(none — this task is fully specified)
