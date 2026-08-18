---
id: T-20260817-resolve-settings-extract
title: "Extract resolve_settings out of get_client"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260817-table-columns-probe]
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

# Extract resolve_settings out of get_client

> **Why:** Nothing can ask which host was resolved without constructing a client - which is exactly the question you need answered when the client cannot be constructed.

## Goal

Make the resolved configuration inspectable without opening a connection.

## Context

The six os.getenv calls are inline inside the lru_cached factory at ch.py:302-324. Return a frozen dataclass plus a defaulted tuple naming the unset variables.

## Behavior

- **B-1** — GIVEN no CLICKHOUSE_ variables WHEN resolve_settings() is called THEN it returns today's defaults and defaulted lists all six
- **B-2** — GIVEN every variable set WHEN resolve_settings() is called THEN it reflects them and defaulted is empty
- **B-3** — GIVEN CLICKHOUSE_SECURE in 1, true or yes in any case WHEN resolved THEN secure is True and any other value is False, matching current behavior
- **B-4** — GIVEN get_client() WHEN called THEN it behaves as before, now via resolve_settings()

## Success Criteria

```bash
# eval_1: the ClickHouse layer suite passes with the settings tests
eval_1() {
  ( cd serve && uv run --extra dev pytest tests/test_ch.py -q )
}

# eval_2: password is not a field on the settings dataclass
eval_2() {
  ( cd serve && uv run python -c "from apex_mcp.ch import resolve_settings as r; s=r(); assert not hasattr(s,'password'), 'password must not be a settings field'; assert hasattr(s,'defaulted')" )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the ClickHouse layer suite passes with the settings tests"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3, B-4]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "password is not a field on the settings dataclass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
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
eval_1 && eval_2
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Putting password on the returned dataclass; it is needed only by get_client().
- Caching resolve_settings(), which would return a stale answer after the env changes.

## Do-Not-Touch

- `serve/src/apex_mcp/models.py`
- `serve/src/apex_mcp/server.py`

## Open Questions

(none — this task is fully specified)
