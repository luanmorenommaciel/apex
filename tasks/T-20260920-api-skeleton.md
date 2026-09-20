---
id: T-20260920-api-skeleton
title: "Stand up the apex-api FastAPI application"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
touches_paths: [serve/pyproject.toml, serve/uv.lock]
creates_paths: [serve/src/apex_api/__init__.py, serve/src/apex_api/app.py, serve/src/apex_api/config.py, serve/src/apex_api/auth.py, serve/src/apex_api/routes/__init__.py, serve/tests/test_api_app.py]
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
signed_off: true
signed_off_by: sidymar
signed_off_at: 2026-09-20T17:24:38Z
accepted: true
accepted_by: sidymar
accepted_at: 2026-09-20T17:26:36Z
signed_off_sig: hmac-sha256-v2:5153084e:677b49a34caac4d6cb38f233fdab26be2f54ef0c8ff38703f7b936b5631b989c
---

# Stand up the apex-api FastAPI application

> **Why:** The console queries ClickHouse from the browser with a credential that ships to every visitor (front/contract/01-readonly-user.sql). Nothing can move off that connection until there is a service to move it to.

## Goal

A FastAPI app with an injectable ReadStore, a /v1/health route, bearer-token auth, an error envelope that cannot leak the DSN, and a router registry the later route units extend without editing app.py.

## Context

apex-mcp already depends on the SDK-bundled FastMCP, which is Starlette and uvicorn underneath, so FastAPI adds no new runtime. ch.py already has _sanitize() and server.py has _fail() - the API needs the same guarantee at the HTTP boundary, not a second sanitizer with different rules. app.py discovers routers under apex_api/routes/ rather than importing them by name, so the diagnostic and resource units add a file each instead of all three editing app.py. Auth belongs here rather than in a follow-up unit: a service that is open between two tasks has been open in someone's environment. Tokens come from server configuration, never a committed file, and /v1/health is the one route probe-able without one, because a liveness check that needs a secret is not a liveness check.

## Behavior

- **B-1** — GIVEN a running app with a reachable store WHEN GET /v1/health is called THEN it returns the ReadStore.store_health() payload and HTTP 200
- **B-2** — GIVEN a store whose client raises with the DSN in the exception text WHEN any route is called THEN the response body and status line contain no part of the DSN, and the detail is logged to stderr instead
- **B-3** — GIVEN the app factory WHEN it is constructed in a test THEN a ReadStore can be injected without a live ClickHouse, the same way serve/tests/conftest.py injects a fake client today
- **B-4** — GIVEN ClickHouse is down WHEN GET /v1/health is called THEN the app still answers, reporting the store as unreachable, rather than failing to start
- **B-5** — GIVEN a module exposing a router is added under apex_api/routes/ WHEN the app is constructed THEN its routes are served without app.py being edited
- **B-6** — GIVEN no Authorization header, or a token that is not configured WHEN any /v1 route other than health is called THEN the response is 401, no query is issued to the store, and the body does not reveal whether the route or the token was wrong
- **B-7** — GIVEN a configured token WHEN a /v1 route is called with it THEN the request is served normally
- **B-8** — GIVEN no token is configured at all WHEN the app starts THEN it refuses to start rather than serving open

## Success Criteria

```bash
# eval_1: health and injectability tests exist and pass
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_api_app.py::test_health_reports_store_health" "tests/test_api_app.py::test_app_accepts_an_injected_store" )
}

# eval_2: the DSN never reaches a response, and a down store still answers
eval_2() {
  ( cd serve && uv run --extra dev pytest "tests/test_api_app.py::test_dsn_never_appears_in_a_response" "tests/test_api_app.py::test_health_answers_when_the_store_is_unreachable" )
}

# eval_3: routers are discovered without editing app.py
eval_3() {
  ( cd serve && uv run --extra dev pytest "tests/test_api_app.py::test_a_router_dropped_into_routes_is_served" )
}

# eval_4: tokens are required, accepted, and mandatory to start
eval_4() {
  ( cd serve && uv run --extra dev pytest "tests/test_api_app.py::test_missing_token_is_refused_without_querying" "tests/test_api_app.py::test_unknown_token_is_refused" "tests/test_api_app.py::test_configured_token_is_accepted" "tests/test_api_app.py::test_startup_refuses_when_no_token_is_configured" )
}

# eval_5: health stays probe-able and no token literal is committed
eval_5() {
  ( cd serve && uv run --extra dev pytest "tests/test_api_app.py::test_health_is_reachable_without_a_token" "tests/test_api_app.py::test_no_token_literal_in_the_package" )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "health and injectability tests exist and pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-3]
    terminal: true
    expected_duration_sec: 60
  - id: eval_2
    description: "the DSN never reaches a response, and a down store still answers"
    runnable: bash
    check_type: deterministic
    verifies: [B-2, B-4]
    terminal: true
    expected_duration_sec: 60
  - id: eval_3
    description: "routers are discovered without editing app.py"
    runnable: bash
    check_type: deterministic
    verifies: [B-5]
    terminal: true
    expected_duration_sec: 60
  - id: eval_4
    description: "tokens are required, accepted, and mandatory to start"
    runnable: bash
    check_type: deterministic
    verifies: [B-6, B-7, B-8]
    terminal: true
    expected_duration_sec: 60
  - id: eval_5
    description: "health stays probe-able and no token literal is committed"
    runnable: bash
    check_type: deterministic
    verifies: [B-6]
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
eval_1 && eval_2 && eval_3 && eval_4 && eval_5
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Constructing a ClickHouse client at import time; the MCP server defers it via LazyClient for exactly this reason.
- Writing a second sanitizer; reuse ch.ApexStoreError and the existing _sanitize path.
- Adding the separate PyPI fastmcp 3.x package. The pin in pyproject.toml is mcp[cli]>=1.27,<2 and the import root differs.
- Importing each router by name in app.py, which puts every later route unit back into this file.
- Defaulting to allow-all when no token is configured; refuse to start instead.
- Different error bodies for unknown route and bad token, which turns 401 into a route oracle.

## Do-Not-Touch

- `serve/src/apex_mcp/server.py`
- `serve/tests/test_server_tools.py`

## Open Questions

(none — this task is fully specified)
