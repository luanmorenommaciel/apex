---
id: T-20260817-register-apex-status
title: "Register the apex_status tool"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260817-status-assembler, T-20260817-status-degraded-path, T-20260817-store-health-query, T-20260817-table-columns-probe]
touches_paths: [serve/src/apex_mcp/server.py]
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

# Register the apex_status tool

> **Why:** This is the commit where the lane stops having four tools; keeping it alone makes the surface change legible in git log.

## Goal

Expose apex_status as a fifth read-only tool wired to store_health, table_columns and diagnose.status.

## Context

The four-tools test is expected to fail after this task and is repaired by its own follow-up unit. Any other failure means this task broke something.

## Behavior

- **B-1** — GIVEN a built server WHEN list_tools() is called THEN apex_status is present with readOnlyHint True and openWorldHint False
- **B-2** — GIVEN apex_status is invoked with a reachable store WHEN the response is validated THEN it returns schema-valid structured output matching ServerStatus
- **B-3** — GIVEN the server module WHEN its docstring is read THEN it describes five tools and still states that stdout is the JSON-RPC channel

## Success Criteria

```bash
# eval_1: the tool is listed read-only with the correct annotations
eval_1() {
  cd serve && uv run python -c "import asyncio; from apex_mcp.server import create_server; from apex_mcp.ch import ReadStore; from tests.conftest import FakeClient; s=create_server(ReadStore(FakeClient())); t={x.name:x for x in asyncio.run(s.list_tools())}; assert 'apex_status' in t, sorted(t); a=t['apex_status'].annotations; assert a.readOnlyHint and a.openWorldHint is False, a"
}

# eval_2: the module docstring no longer claims four tools
eval_2() {
  cd serve && ! grep -n 'Four tools' src/apex_mcp/server.py
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the tool is listed read-only with the correct annotations"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 20
  - id: eval_2
    description: "the module docstring no longer claims four tools"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
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

- Repairing the failing four-tools assertion in this unit.
- Annotating with PROPOSAL_ONLY instead of READ_ONLY.
- Adding parameters; apex_status takes none in v1 and so has no injection surface.

## Do-Not-Touch

- `serve/tests/test_server_tools.py`
- `serve/src/apex_mcp/diagnose.py`

## Open Questions

(none — this task is fully specified)
