---
id: T-20260817-serverstatus-model
title: "Add the ServerStatus Pydantic model"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
touches_paths: [serve/src/apex_mcp/models.py]
creates_paths: [serve/tests/test_status.py]
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
signed_off: true
signed_off_by: sidymar
signed_off_at: 2026-08-17T14:37:36Z
accepted: false
accepted_by: (none)
accepted_at: (none)
signed_off_sig: hmac-sha256-v2:5153084e:6c4ab6b63d1720dcb81b48fe50a648da6cd90e13147ff84b432c37b98a8035fd
---

# Add the ServerStatus Pydantic model

> **Why:** FastMCP derives each tool's output schema from its return annotation; a status tool returning a bare dict would be the one hole in that mitigation.

## Goal

Define the typed payload apex_status() returns, before anything produces one.

## Context

models.py already holds Diagnosis, RunComparison, KbHits and FixSuggestion and has no intra-package runtime import. Keep it that way.

## Behavior

- **B-1** — GIVEN no arguments but connected=False WHEN a ServerStatus is constructed THEN it validates with every remaining field taking a default
- **B-2** — GIVEN the class WHEN model_json_schema() is called THEN it renders with connected required and boolean
- **B-3** — GIVEN any ServerStatus WHEN it is serialized THEN no field can carry a credential - no user, password, dsn or connection URL

## Success Criteria

```bash
# eval_1: the status model test file passes
eval_1() {
  ( cd serve && uv run --extra dev pytest tests/test_status.py -q )
}

# eval_2: the model exposes the contracted field set
eval_2() {
  ( cd serve && uv run python -c "from apex_mcp.models import ServerStatus; k=set(ServerStatus(connected=False).model_dump()); need={'connected','database','run_count','latest_ingest_age_seconds','contract_tables','using_defaults','degraded_reason','remediation','tools'}; assert need <= k, need - k" )
}

# eval_3: no credential-shaped field exists on the model
eval_3() {
  ( cd serve && ! grep -nE '^\s+(password|dsn|secret)\s*:' src/apex_mcp/models.py )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the status model test file passes"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "the model exposes the contracted field set"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 15
  - id: eval_3
    description: "no credential-shaped field exists on the model"
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
eval_1 && eval_2 && eval_3
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Returning dict[str, Any] instead of a model.
- Adding a dsn or password field for debugging.
- Importing ch or diagnose into models.py.

## Do-Not-Touch

- `serve/src/apex_mcp/server.py`
- `serve/src/apex_mcp/ch.py`
- `serve/src/apex_mcp/diagnose.py`

## Open Questions

(none — this task is fully specified)
