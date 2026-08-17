---
id: T-20260817-status-degraded-path
title: "Make status survive an unreachable store"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260817-status-assembler]
touches_paths: [serve/src/apex_mcp/diagnose.py, serve/tests/test_status.py]
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

# Make status survive an unreachable store

> **Why:** A status call that fails when the database is down only works when you do not need it.

## Goal

Return a degraded ServerStatus carrying the sanitized code and a next action, instead of raising.

## Context

get_client() is lazy by design at ch.py:302, so the server lists tools with the database down. This task pays that back.

## Behavior

- **B-1** — GIVEN a store whose every query raises ApexStoreError WHEN status() is called THEN it returns ServerStatus(connected=False) and does not raise
- **B-2** — GIVEN that same failure WHEN the result is read THEN degraded_reason carries the sanitized code and remediation carries a next action
- **B-3** — GIVEN a store raising a non-ApexStoreError exception WHEN status() is called THEN that exception propagates
- **B-4** — GIVEN any degraded response WHEN it is serialized THEN no credential appears in any field including degraded_reason

## Success Criteria

```bash
# eval_1: the degraded-path tests exist and pass
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_status.py::test_status_degrades_when_store_unreachable" "tests/test_status.py::test_status_propagates_unexpected_exception" )
}

# eval_2: a sentinel password never reaches a degraded response
eval_2() {
  ( cd serve && CLICKHOUSE_PASSWORD='sentinel-pw-do-not-leak' uv run --extra dev pytest tests/test_status.py -q )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the degraded-path tests exist and pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "a sentinel password never reaches a degraded response"
    runnable: bash
    check_type: deterministic
    verifies: [B-4]
    terminal: true
    expected_duration_sec: 30
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

- A bare except Exception, which turns a real bug into a database-down report.
- Re-deriving remediation from the exception message instead of mapping the sanitized code.
- Retry loops; status reports, it does not repair.

## Do-Not-Touch

- `serve/src/apex_mcp/ch.py`

## Open Questions

(none — this task is fully specified)
