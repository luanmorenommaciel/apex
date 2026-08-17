---
id: T-20260817-name-endpoint-in-error
title: "Name the resolved endpoint in the unavailable error"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260817-resolve-settings-extract]
touches_paths: [serve/src/apex_mcp/ch.py, serve/tests/test_injection_hardening.py]
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

# Name the resolved endpoint in the unavailable error

> **Why:** The message names no value, so a user cannot tell whether the server tried the host they meant.

## Goal

Include host, port and database in the connection-failure message while keeping user and password out.

## Context

This pulls against the security rail at ch.py:274. The endpoint is configuration the user supplied; the credential is not. Only the first moves.

## Behavior

- **B-1** — GIVEN a connection failure against a configured endpoint WHEN the error surfaces THEN the message contains host, port and database
- **B-2** — GIVEN CLICKHOUSE_PASSWORD set to a sentinel WHEN any sanitized error is produced THEN the sentinel appears in none of them
- **B-3** — GIVEN a connection failure WHEN the message is read THEN CLICKHOUSE_USER does not appear
- **B-4** — GIVEN a driver exception carrying a full DSN in its own text WHEN sanitized THEN none of that original text is forwarded

## Success Criteria

```bash
# eval_1: the disclosure suite passes with the endpoint assertions
eval_1() {
  ( cd serve && uv run --extra dev pytest tests/test_injection_hardening.py -q )
}

# eval_2: neither sentinel credential escapes with both exported
eval_2() {
  ( cd serve && CLICKHOUSE_PASSWORD='sentinel-pw-do-not-leak' CLICKHOUSE_USER='sentinel-user' uv run --extra dev pytest -q )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the disclosure suite passes with the endpoint assertions"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-3, B-4]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "neither sentinel credential escapes with both exported"
    runnable: bash
    check_type: deterministic
    verifies: [B-2, B-3]
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

- Interpolating str(exc) into the returned message; driver text is where the DSN lives.
- Adding the username on the grounds that it is not the password.
- Widening the same treatment to clickhouse_query_failed.

## Do-Not-Touch

- `serve/src/apex_mcp/server.py`

## Open Questions

(none — this task is fully specified)
