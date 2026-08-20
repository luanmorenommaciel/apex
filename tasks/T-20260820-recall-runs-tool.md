---
id: T-20260820-recall-runs-tool
title: "Add recall_similar_runs"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260820-plan-memory-read-layer, T-20260820-recall-models]
touches_paths: [serve/src/apex_mcp/server.py]
creates_paths: []
source_note: "docs/lanes/SERVE-LEGS.md"
created: "2026-08-20T00:00:00Z"
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

# Add recall_similar_runs

> **Why:** Every serve tool reasons about one run. This is the first that reasons across them.

## Goal

recall_similar_runs(job_id, top_k) returns prior runs of the same plan shape with their configs and outcomes.

## Context

L1, L3 and L5 each move the same surface assertion in their own worktrees; whichever lands last reconciles. The five-tools assertion is expected to fail after this unit.

## Behavior

- **B-1** — GIVEN a built server WHEN list_tools() is called THEN recall_similar_runs is present with readOnlyHint True
- **B-2** — GIVEN a job_id whose shape has prior runs WHEN recall_similar_runs is called THEN it returns those runs with similarity, config and wall clock
- **B-3** — GIVEN a shape never seen before WHEN recall_similar_runs is called THEN it says so, rather than returning the nearest unrelated shape
- **B-4** — GIVEN a deployment without the memory tables WHEN recall_similar_runs is called THEN it reports that cross-run memory is unavailable on this deployment

## Success Criteria

```bash
# eval_1: recall_similar_runs is registered read-only
eval_1() {
  ( cd serve && uv run python -c "import asyncio; from apex_mcp.server import create_server; from apex_mcp.ch import ReadStore; from tests.conftest import FakeClient; s=create_server(ReadStore(FakeClient())); t={x.name:x for x in asyncio.run(s.list_tools())}; assert 'recall_similar_runs' in t, sorted(t); assert t['recall_similar_runs'].annotations.readOnlyHint" )
}

# eval_2: the docstring no longer claims five tools
eval_2() {
  ( cd serve && ! grep -n 'Five tools' src/apex_mcp/server.py )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "recall_similar_runs is registered read-only"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 20
  - id: eval_2
    description: "the docstring no longer claims five tools"
    runnable: bash
    check_type: deterministic
    verifies: [B-3, B-4]
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

- Returning the nearest shape regardless of similarity; below the threshold the honest answer is that nothing matches.
- Repairing the surface assertion here.

## Do-Not-Touch

- `serve/tests/test_server_tools.py`
- `serve/src/apex_mcp/ch.py`

## Open Questions

(none — this task is fully specified)
