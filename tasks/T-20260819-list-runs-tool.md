---
id: T-20260819-list-runs-tool
title: "Register the list_runs tool"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260819-runs-read-layer, T-20260819-run-summary-models]
touches_paths: [serve/src/apex_mcp/server.py]
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
signed_off: true
signed_off_by: sidymar
signed_off_at: 2026-08-19T17:50:12Z
accepted: true
accepted_by: sidymar
accepted_at: 2026-08-19T17:50:13Z
signed_off_sig: hmac-sha256-v2:5153084e:8a5bf102a175ae774610ca6b4fe369b5a1b1348aa3da5a58d31b7719c098dd0e
---

# Register the list_runs tool

> **Why:** This is the commit where the lane stops requiring a job_id from outside the system.

## Goal

Expose list_runs(limit, since_hours, app_name) as a fifth read-only tool.

## Context

One tool with filters covers the leg's list_runs, find_run and latest_run features - three tools differing only by a WHERE clause would be API bloat and three injection surfaces instead of one. The four-tools assertion is expected to fail after this unit and is repaired by its own follow-up; any other failure means this unit broke something.

## Behavior

- **B-1** — GIVEN a built server WHEN list_tools() is called THEN list_runs is present with readOnlyHint True and openWorldHint False
- **B-2** — GIVEN list_runs is invoked with no arguments WHEN the store has runs THEN it returns schema-valid RunList, newest first, under the default limit
- **B-3** — GIVEN list_runs is invoked with app_name WHEN the store has runs from several applications THEN only the named application's runs return
- **B-4** — GIVEN the module docstring WHEN read THEN it describes five tools and still states that stdout is the JSON-RPC channel

## Success Criteria

```bash
# eval_1: list_runs is registered read-only with the right annotations
eval_1() {
  ( cd serve && uv run python -c "import asyncio; from apex_mcp.server import create_server; from apex_mcp.ch import ReadStore; from tests.conftest import FakeClient; s=create_server(ReadStore(FakeClient())); t={x.name:x for x in asyncio.run(s.list_tools())}; assert 'list_runs' in t, sorted(t); a=t['list_runs'].annotations; assert a.readOnlyHint and a.openWorldHint is False, a" )
}

# eval_2: the module docstring no longer claims four tools
eval_2() {
  ( cd serve && ! grep -n 'Four tools' src/apex_mcp/server.py )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "list_runs is registered read-only with the right annotations"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 20
  - id: eval_2
    description: "the module docstring no longer claims four tools"
    runnable: bash
    check_type: deterministic
    verifies: [B-4]
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

- Repairing the failing four-tools assertion in this unit; that is the follow-up, and merging them hides the surface change.
- Adding separate find_run and latest_run tools; app_name and limit already express both.
- Annotating with anything but READ_ONLY.

## Do-Not-Touch

- `serve/tests/test_server_tools.py`
- `serve/src/apex_mcp/ch.py`

## Open Questions

(none — this task is fully specified)
