---
id: T-20260920-api-openapi-auth
title: "Say in the OpenAPI schema that /v1 needs a token"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260920-api-resource-routes]
touches_paths: [serve/src/apex_api/app.py]
creates_paths: [serve/tests/test_api_openapi.py]
source_note: "serve/src/apex_api/auth.py"
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
signed_off_at: 2026-09-21T00:20:19Z
accepted: true
accepted_by: sidymar
accepted_at: 2026-09-21T00:21:19Z
signed_off_sig: hmac-sha256-v2:5153084e:121f7549c5c32604d227e6a9b40350d929107727bf3eb4c5877bbdf6b8b84187
---

# Say in the OpenAPI schema that /v1 needs a token

> **Why:** FastAPI already serves Swagger at /docs and the schema at /openapi.json, but admission is MIDDLEWARE, so the schema says nothing about needing a credential. A consumer reads the docs, calls a route, gets 401 and has nothing to tell them why - and Swagger offers no Authorize button to try it with.

## Goal

The schema declares a bearer scheme, every /v1 operation but health requires it, and health does not.

## Context

The requirement is declared, not enforced, here - auth.py stays the enforcement point, because a dependency-based scheme would move admission behind routing and reopen the route oracle it exists to close. This unit only makes the schema tell the truth about what auth.py already does.

## Behavior

- **B-1** — GIVEN the OpenAPI schema WHEN it is read THEN it declares an http bearer security scheme
- **B-2** — GIVEN any /v1 operation other than health WHEN its schema entry is read THEN it carries that security requirement
- **B-3** — GIVEN /v1/health WHEN its schema entry is read THEN it carries no security requirement, because a liveness probe holds no token
- **B-4** — GIVEN no Authorization header WHEN /docs, /redoc and /openapi.json are fetched THEN they answer, because a schema is a description and carries no row from the store

## Success Criteria

```bash
# eval_1: the scheme is declared and applied to exactly the right operations
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_api_openapi.py::test_schema_declares_a_bearer_scheme" "tests/test_api_openapi.py::test_every_v1_operation_but_health_requires_it" )
}

# eval_2: the docs stay readable and carry no data
eval_2() {
  ( cd serve && uv run --extra dev pytest "tests/test_api_openapi.py::test_docs_are_reachable_without_a_token" )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the scheme is declared and applied to exactly the right operations"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 60
  - id: eval_2
    description: "the docs stay readable and carry no data"
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
eval_1 && eval_2
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Replacing the middleware with a route dependency to get the schema for free; that moves admission behind routing and tells an anonymous caller which routes exist.
- Marking health as secured, which would tell an orchestrator to hold a secret to run a liveness probe.
- Gating /openapi.json on a token so the docs cannot be read by the consumer who needs them.

## Do-Not-Touch

- `serve/src/apex_api/auth.py`

## Open Questions

(none — this task is fully specified)
