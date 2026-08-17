---
id: T-20260817-status-store-down-e2e
title: "Prove status answers through the tool boundary while the store is down"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260817-register-apex-status, T-20260817-five-tools-assertion]
touches_paths: [serve/tests/test_server_tools.py]
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

# Prove status answers through the tool boundary while the store is down

> **Why:** Between the pure function and the client sit create_server, _fail() and FastMCP serialization, any of which could turn a degraded response back into an error.

## Goal

Assert end-to-end that apex_status returns data, not an error, when every query raises.

## Context

conftest already provides FakeClient; extend it rather than repointing fixtures other suites rely on.

## Behavior

- **B-1** — GIVEN a FakeClient that raises on every query WHEN apex_status is invoked through the built server THEN it returns schema-valid ServerStatus with connected False
- **B-2** — GIVEN the same call WHEN the response is inspected THEN no ApexStoreError reached the client as a tool error
- **B-3** — GIVEN CLICKHOUSE_PASSWORD set to a sentinel WHEN the degraded response is serialized THEN the sentinel appears nowhere in it

## Success Criteria

```bash
# eval_1: the tool-surface suite passes with the store-down case
eval_1() {
  ( cd serve && uv run --extra dev pytest tests/test_server_tools.py -q )
}

# eval_2: the whole suite stays green with a sentinel password exported
eval_2() {
  ( cd serve && CLICKHOUSE_PASSWORD='sentinel-pw-do-not-leak' uv run --extra dev pytest -q )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the tool-surface suite passes with the store-down case"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "the whole suite stays green with a sentinel password exported"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
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

- Asserting on exact remediation wording instead of the response shape.
- Calling diagnose.status() directly; the value of this unit is going through the server.

## Do-Not-Touch

- `serve/src/apex_mcp`

## Open Questions

(none — this task is fully specified)
