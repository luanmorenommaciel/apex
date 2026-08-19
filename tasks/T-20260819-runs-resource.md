---
id: T-20260819-runs-resource
title: "Expose apex://runs as an MCP resource"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260819-tool-surface-five]
touches_paths: [serve/src/apex_mcp/server.py, serve/tests/test_server_tools.py]
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
signed_off_at: 2026-08-19T17:52:43Z
accepted: true
accepted_by: sidymar
accepted_at: 2026-08-19T17:53:17Z
signed_off_sig: hmac-sha256-v2:5153084e:197701b9cdc85c8d7a827577bdeb9d3f7cc730aa57e2d985862b173e8a935921
---

# Expose apex://runs as an MCP resource

> **Why:** Apex uses one of MCP's primitives. A resource lets a client browse recent runs without spending a tool call, which is what orientation should cost.

## Goal

Serve the recent-run list as a readable resource alongside the tool.

## Context

This is the lane's first resource, so it also establishes that resources inherit the same read-only discipline and untrusted-field marking as tools.

## Behavior

- **B-1** — GIVEN a built server WHEN list_resources() is called THEN apex://runs is present with a name and a mime type
- **B-2** — GIVEN apex://runs WHEN it is read THEN it returns the same run data the tool returns, serialized as JSON
- **B-3** — GIVEN the store is unreachable WHEN apex://runs is read THEN it fails with the sanitized code and leaks no credential

## Success Criteria

```bash
# eval_1: the resource tests exist and pass
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_server_tools.py::test_runs_resource_is_listed" "tests/test_server_tools.py::test_runs_resource_returns_run_data" )
}

# eval_2: the full tool-surface suite stays green with a sentinel password exported
eval_2() {
  ( cd serve && CLICKHOUSE_PASSWORD=sentinel-pw-do-not-leak uv run --extra dev pytest tests/test_server_tools.py )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the resource tests exist and pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "the full tool-surface suite stays green with a sentinel password exported"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
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

- Letting the resource bypass ReadStore and query the client directly.
- Returning free text instead of the same typed payload the tool returns.
- Changing the tool count; a resource is not a tool and must not appear in list_tools().

## Do-Not-Touch

- `serve/src/apex_mcp/ch.py`
- `serve/src/apex_mcp/models.py`

## Open Questions

(none — this task is fully specified)
