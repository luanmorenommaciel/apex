---
id: T-20260817-table-columns-probe
title: "Generalize findings_columns into an allowlisted table_columns probe"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260817-store-health-query]
touches_paths: [serve/src/apex_mcp/ch.py, serve/tests/test_ch.py]
creates_paths: []
source_note: "docs/lanes/L1_tasks.md"
created: "2026-08-17T00:00:00Z"
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

# Generalize findings_columns into an allowlisted table_columns probe

> **Why:** The schema probe is why serve degraded gracefully while the engine write path was dead; it currently covers one table of three.

## Goal

Let the status tool report contract conformance for spark_events, findings and plan_transitions.

## Context

findings_columns() at ch.py:214 probes system.columns for one hardcoded table. Preserve it as a thin caller.

## Behavior

- **B-1** — GIVEN table_columns("spark_events") WHEN the table exists THEN it returns that table's column names as a set
- **B-2** — GIVEN findings_columns() WHEN called THEN it returns exactly what it returns today with caching unchanged
- **B-3** — GIVEN a table name outside the allowlist WHEN table_columns is called THEN it raises ApexStoreError before issuing any query

## Success Criteria

```bash
# eval_1: the ClickHouse layer suite passes with the new probe tests
eval_1() {
  ( cd serve && uv run --extra dev pytest tests/test_ch.py -q )
}

# eval_2: the pre-existing additive-column test was not rewritten to pass
eval_2() {
  ( cd serve && test -z "$(git diff HEAD -- tests/test_ch.py | grep '^-' | grep -v '^---')" )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the ClickHouse layer suite passes with the new probe tests"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "the pre-existing additive-column test was not rewritten to pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-2]
    terminal: true
    expected_duration_sec: 10
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
eval_1 && eval_2
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Interpolating the table name into SQL instead of binding it behind the allowlist.
- Dropping the memoization the current probe relies on.
- Widening the allowlist to any table in the apex database.

## Do-Not-Touch

- `serve/src/apex_mcp/models.py`
- `serve/src/apex_mcp/server.py`

## Open Questions

(none — this task is fully specified)
