---
id: T-20260817-store-health-query
title: "Add ReadStore.store_health for counts and freshness"
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
signed_off: true
signed_off_by: sidymar
signed_off_at: 2026-08-17T14:44:07Z
accepted: true
accepted_by: sidymar
accepted_at: 2026-08-17T14:44:09Z
signed_off_sig: hmac-sha256-v2:5153084e:bfea9eeb592d87dbf929a0f02126c7058736f863f1579391855d361e21dad2c5
---

# Add ReadStore.store_health for counts and freshness

> **Why:** A connected-but-empty Apex is currently indistinguishable from a broken one.

## Goal

One read that answers whether there is data and how fresh it is.

## Context

ReadStore at ch.py:197 exposes only job_id-keyed reads. Route the new read through _query() so sanitization is inherited.

## Behavior

- **B-1** — GIVEN a store holding runs WHEN store_health() is called THEN it returns total row count, distinct job_id count and max(ts) from apex.spark_events
- **B-2** — GIVEN an empty but reachable apex.spark_events WHEN store_health() is called THEN it returns zeros and a null timestamp without raising
- **B-3** — GIVEN an unreachable store WHEN store_health() is called THEN it raises ApexStoreError with the existing sanitized code

## Success Criteria

```bash
# eval_1: the ClickHouse layer suite passes including the empty-table case
eval_1() {
  ( cd serve && uv run --extra dev pytest tests/test_ch.py -q )
}

# eval_2: user-controlled values reach SQL only through server-side binding
eval_2() {
  ( cd serve && uv run --extra dev pytest "tests/test_ch.py::test_every_query_uses_server_side_binding" "tests/test_ch.py::test_store_health_sql_is_bound_not_interpolated" )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the ClickHouse layer suite passes including the empty-table case"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "user-controlled values reach SQL only through server-side binding"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
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

- Building the SQL with an f-string.
- Bypassing _query() and losing _sanitize().
- SELECT star, or any scan not bounded to apex.spark_events.

## Do-Not-Touch

- `serve/src/apex_mcp/models.py`
- `serve/src/apex_mcp/server.py`
- `serve/src/apex_mcp/diagnose.py`

## Open Questions

(none — this task is fully specified)
