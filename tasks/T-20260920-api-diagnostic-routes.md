---
id: T-20260920-api-diagnostic-routes
title: "Expose the eight MCP tools as /v1 diagnostic routes"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260920-api-skeleton]
touches_paths: []
creates_paths: [serve/src/apex_api/routes/diagnostics.py, serve/tests/test_api_diagnostics.py]
source_note: "serve/src/apex_mcp/server.py"
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

# Expose the eight MCP tools as /v1 diagnostic routes

> **Why:** The console's chat and any external consumer need the verdict-level answers, and those already exist as eight tested MCP tools. Re-implementing them against ClickHouse would give two answers to the same question.

## Goal

Eight routes that dispatch through create_server(store).call_tool(), with a test that fails when the tool set and the route set diverge.

## Context

serve/tests/test_server_tools.py already drives list_tools() and call_tool() in-process with no transport, so this is a dispatch adapter, not new analysis. call_tool returns Sequence[ContentBlock] | dict - the adapter must normalise both, as that test does. test_the_contracted_tool_surface asserts exact tool-set equality because an unnoticed tool a model can call is a security event; that control has to extend here rather than be duplicated.

## Behavior

- **B-1** — GIVEN the app WHEN the route table is compared against create_server(store).list_tools() THEN every tool name has exactly one route and every route maps to exactly one tool, with no extras on either side
- **B-2** — GIVEN a job_id WHEN GET /v1/runs/{job_id}/diagnosis is called THEN the body validates against the Diagnosis model and equals what call_tool("analyze_run") returns for the same store
- **B-3** — GIVEN call_tool returns a tuple rather than a dict WHEN any diagnostic route is called THEN the adapter normalises it and the client sees the structured payload either way
- **B-4** — GIVEN POST /v1/runs/{job_id}/fix-suggestion WHEN it succeeds THEN the payload reports applied false and requires_human_approval true, and nothing is written
- **B-5** — GIVEN a tool that raises ApexStoreError WHEN its route is called THEN the response is a sanitized error, not a traceback

## Success Criteria

```bash
# eval_1: routes and tools cannot drift apart
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_api_diagnostics.py::test_every_tool_has_exactly_one_route" "tests/test_api_diagnostics.py::test_every_route_maps_to_a_tool" )
}

# eval_2: a route returns what the tool returns, however call_tool shapes it
eval_2() {
  ( cd serve && uv run --extra dev pytest "tests/test_api_diagnostics.py::test_diagnosis_route_matches_the_tool" "tests/test_api_diagnostics.py::test_tuple_and_dict_results_are_both_normalised" )
}

# eval_3: the proposal tool stays a proposal and errors stay sanitized
eval_3() {
  ( cd serve && uv run --extra dev pytest "tests/test_api_diagnostics.py::test_fix_suggestion_route_applies_nothing" "tests/test_api_diagnostics.py::test_store_error_is_sanitized_at_the_boundary" )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "routes and tools cannot drift apart"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 60
  - id: eval_2
    description: "a route returns what the tool returns, however call_tool shapes it"
    runnable: bash
    check_type: deterministic
    verifies: [B-2, B-3]
    terminal: true
    expected_duration_sec: 60
  - id: eval_3
    description: "the proposal tool stays a proposal and errors stay sanitized"
    runnable: bash
    check_type: deterministic
    verifies: [B-4, B-5]
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

- Hand-listing the eight route handlers so a ninth tool can ship without a route and without a failure.
- Calling diagnose.analyze() directly and bypassing the tool layer, which drops the annotations and the docstring contract.
- Making fix-suggestion a GET because it happens not to write anything.

## Do-Not-Touch

- `serve/src/apex_mcp/server.py`
- `serve/src/apex_mcp/diagnose.py`

## Open Questions

(none — this task is fully specified)
