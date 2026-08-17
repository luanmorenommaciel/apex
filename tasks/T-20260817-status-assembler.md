---
id: T-20260817-status-assembler
title: "Add the pure diagnose.status assembler"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260817-serverstatus-model]
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

# Add the pure diagnose.status assembler

> **Why:** Every other diagnosis in this lane is a pure function handed its I/O; status must follow or it becomes the one piece needing ClickHouse to test.

## Goal

Turn raw health numbers into a ServerStatus a user can act on, with no I/O.

## Context

The required-column set already exists at serve/tools/read_only_gate.py:33-59. Lift it to one shared constant rather than writing a second copy.

## Behavior

- **B-1** — GIVEN health numbers, per-table column sets, resolved settings and a tool list WHEN status() is called THEN it returns a ServerStatus and performs no I/O
- **B-2** — GIVEN a latest ingest four minutes old WHEN status() runs THEN latest_ingest_age_seconds is approximately 240 and connected is True
- **B-3** — GIVEN findings missing confidence_score WHEN status() runs THEN contract_tables lists the column and remediation names both it and the infra lane
- **B-4** — GIVEN a reachable store with zero rows WHEN status() runs THEN connected is True and remediation says the store is empty, not broken

## Success Criteria

```bash
# eval_1: all four assembler behaviors are covered by passing tests
eval_1() {
  cd serve && uv run --extra dev pytest tests/test_status.py -q
}

# eval_2: the assembler performs no I/O
eval_2() {
  cd serve && ! grep -nE '(get_client|clickhouse_connect|ReadStore\()' src/apex_mcp/diagnose.py
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "all four assembler behaviors are covered by passing tests"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3, B-4]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "the assembler performs no I/O"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 5
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

- Calling get_client() or a ReadStore from inside status().
- Building remediation text out of observed data; remediation is Apex's own string.
- Reporting connected=True because the process is alive rather than a query returning.

## Do-Not-Touch

- `serve/src/apex_mcp/ch.py`
- `serve/src/apex_mcp/server.py`

## Open Questions

(none — this task is fully specified)
