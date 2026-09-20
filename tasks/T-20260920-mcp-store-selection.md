---
id: T-20260920-mcp-store-selection
title: "Let the MCP server read through the API when configured"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260920-api-resource-routes]
touches_paths: [serve/src/apex_mcp/server.py]
creates_paths: [serve/src/apex_mcp/http_store.py, serve/tests/test_store_selection.py]
source_note: "brain/01-projects/apex/08-meetings/krisp/2026-09-15-weekly-sync-crew-a-apex.md"
created: "2026-09-20T00:00:00Z"
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

# Let the MCP server read through the API when configured

> **Why:** Luan asked for the MCP to route its queries through the API so one process holds the credentials and every query is auditable. Making that a configuration rather than the only path keeps uvx apex-mcp working for someone with direct ClickHouse access.

## Goal

An HttpReadStore with the same method surface as ReadStore, selected when APEX_API_URL is set and not otherwise.

## Context

create_server(store) is already parameterised on the store and the tests already inject a fake, so no tool changes. The tool surface must stay byte-identical under either store, or the two front doors stop agreeing.

## Behavior

- **B-1** — GIVEN APEX_API_URL is unset WHEN the server starts THEN it uses the ClickHouse-backed ReadStore, exactly as today
- **B-2** — GIVEN APEX_API_URL is set WHEN the server starts THEN it uses HttpReadStore and issues no direct ClickHouse connection
- **B-3** — GIVEN either store WHEN list_tools() is called THEN the tool set, annotations and output schemas are identical
- **B-4** — GIVEN HttpReadStore and an API that returns 401 or is unreachable WHEN a tool is called THEN the failure is reported as a sanitized store error and never as an empty result

## Success Criteria

```bash
# eval_1: the store is selected by configuration
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_store_selection.py::test_unset_url_uses_clickhouse" "tests/test_store_selection.py::test_set_url_uses_http_and_opens_no_clickhouse_connection" )
}

# eval_2: the tool surface is identical under either store
eval_2() {
  ( cd serve && uv run --extra dev pytest "tests/test_store_selection.py::test_tool_surface_is_identical_under_both_stores" "tests/test_server_tools.py::test_the_contracted_tool_surface" )
}

# eval_3: an unreachable API is an error, not an empty answer
eval_3() {
  ( cd serve && uv run --extra dev pytest "tests/test_store_selection.py::test_unreachable_api_is_an_error_not_an_empty_result" )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the store is selected by configuration"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 60
  - id: eval_2
    description: "the tool surface is identical under either store"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
    terminal: true
    expected_duration_sec: 60
  - id: eval_3
    description: "an unreachable API is an error, not an empty answer"
    runnable: bash
    check_type: deterministic
    verifies: [B-4]
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
eval_1 && eval_2 && eval_3
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Falling back to ClickHouse when the API is unreachable, which defeats the single-credential-holder property.
- Returning [] on an HTTP failure, which a model reads as "this run has no stages".
- Changing any tool signature or docstring; only the store behind them changes.

## Do-Not-Touch

- `serve/src/apex_mcp/diagnose.py`
- `serve/src/apex_mcp/models.py`

## Open Questions

(none — this task is fully specified)
