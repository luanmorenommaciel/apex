---
id: T-20260920-api-resource-routes
title: "Serve the console's row-level data over /v1"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260920-api-skeleton, T-20260920-readstore-console-queries]
touches_paths: []
creates_paths: [serve/src/apex_api/routes/resources.py, serve/tests/test_api_resources.py]
source_note: "front/src/data/repository.ts"
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

# Serve the console's row-level data over /v1

> **Why:** The six data screens need rows, not verdicts. Without these routes the console keeps its browser-side database credential regardless of what the diagnostic tier offers.

## Goal

A route for each of the twelve Repository methods, returning the same row shapes the console renders today.

## Context

front/src/data/repository.ts is the contract - twelve methods whose return types the screens already consume. The response shapes must match those types, because the acceptance test on the other side is that no screen changes.

## Behavior

- **B-1** — GIVEN each of the twelve Repository methods WHEN the route table is enumerated THEN there is exactly one route per method
- **B-2** — GIVEN a known job_id WHEN the runs, stages, findings, transitions and conf routes are called THEN each returns the row shape declared in front/src/contract/types for that query
- **B-3** — GIVEN an unknown job_id WHEN the single-run route is called THEN the response is 404 and never a zero-filled row
- **B-4** — GIVEN the contract v0.3 memory tables are absent WHEN the plan-shape routes are called THEN the response says the tables are absent rather than returning an empty list
- **B-5** — GIVEN a list route WHEN it is called without bounds THEN the same MAX_RUNS-style truncation ReadStore already applies is applied and reported

## Success Criteria

```bash
# eval_1: every Repository method has a route and the row shapes match
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_api_resources.py::test_every_repository_method_has_a_route" "tests/test_api_resources.py::test_row_shapes_match_the_console_contract" )
}

# eval_2: absence is reported as absence
eval_2() {
  ( cd serve && uv run --extra dev pytest "tests/test_api_resources.py::test_unknown_job_is_404_not_a_zero_row" "tests/test_api_resources.py::test_absent_memory_tables_are_reported" )
}

# eval_3: unbounded listings are truncated and say so
eval_3() {
  ( cd serve && uv run --extra dev pytest "tests/test_api_resources.py::test_unbounded_listing_is_truncated_and_reported" )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "every Repository method has a route and the row shapes match"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 90
  - id: eval_2
    description: "absence is reported as absence"
    runnable: bash
    check_type: deterministic
    verifies: [B-3, B-4]
    terminal: true
    expected_duration_sec: 60
  - id: eval_3
    description: "unbounded listings are truncated and say so"
    runnable: bash
    check_type: deterministic
    verifies: [B-5]
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

- Returning 200 with an empty body for an unknown job; the console renders that as a real but empty run.
- Inventing a new row shape and making the console adapt, which turns a swap into a rewrite.
- Accepting raw SQL from the client on any route.

## Do-Not-Touch

- `front/src/`

## Open Questions

(none — this task is fully specified)
