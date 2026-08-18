---
id: T-20260817-startup-stderr-banner
title: "Log one resolved-configuration banner to stderr at startup"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260817-resolve-settings-extract, T-20260817-status-store-down-e2e]
touches_paths: [serve/src/apex_mcp/server.py, serve/tests/test_server_tools.py]
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

# Log one resolved-configuration banner to stderr at startup

> **Why:** MCP servers are spawned by a client whose config the user may not have written; when Apex looks empty the first need is proof of which endpoint it resolved.

## Goal

Emit one stderr line naming host, port, database and secure, with stdout untouched.

## Context

stdout is the JSON-RPC channel. Nothing in src/apex_mcp may print().

## Behavior

- **B-1** — GIVEN the server starts WHEN it initializes THEN one line on stderr names host, port, database and secure
- **B-2** — GIVEN the server is launched with immediate EOF WHEN it exits THEN stdout received zero bytes
- **B-3** — GIVEN CLICKHOUSE_PASSWORD is set WHEN the banner is written THEN the password does not appear in any form
- **B-4** — GIVEN APEX_LOG_LEVEL=WARNING WHEN the server starts THEN the banner is suppressed, because it is a log line and not a print

## Success Criteria

```bash
# eval_1: the tool-surface suite passes with the banner test
eval_1() {
  ( cd serve && uv run --extra dev pytest tests/test_server_tools.py -q )
}

# eval_2: a live launch writes zero bytes to stdout and leaks no password to stderr
eval_2() {
  ( cd serve && CLICKHOUSE_PASSWORD='sentinel-pw-do-not-leak' uv run apex-mcp </dev/null >/tmp/apex-stdout.bin 2>/tmp/apex-stderr.txt; test ! -s /tmp/apex-stdout.bin && ! grep -q 'sentinel-pw' /tmp/apex-stderr.txt && grep -qi 'clickhouse' /tmp/apex-stderr.txt )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the tool-surface suite passes with the banner test"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-4]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "a live launch writes zero bytes to stdout and leaks no password to stderr"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
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

- print() anywhere in src/apex_mcp for any reason.
- Logging the password even masked; do not read it here at all.
- Emitting the banner at module import rather than in main().

## Do-Not-Touch

- `serve/src/apex_mcp/ch.py`

## Open Questions

(none — this task is fully specified)
