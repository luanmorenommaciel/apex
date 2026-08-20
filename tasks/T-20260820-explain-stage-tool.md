---
id: T-20260820-explain-stage-tool
title: "Add explain_stage for drill-down"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260820-detail-parameter]
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

# Add explain_stage for drill-down

> **Why:** Once summary is the default, the user needs somewhere to go for one stage rather than re-requesting the whole run at full detail.

## Goal

explain_stage(job_id, stage_id) returns one stage's metrics, symptoms and findings.

## Context

The sixth tool. L1's register-apex-status also moves the surface assertion, to a different six; whichever leg lands second reconciles. The five-tools assertion is expected to fail after this unit and is repaired by its own follow-up.

## Behavior

- **B-1** — GIVEN a built server WHEN list_tools() is called THEN explain_stage is present with readOnlyHint True and openWorldHint False
- **B-2** — GIVEN a job_id and a stage_id that exists WHEN explain_stage is called THEN it returns that stage's metrics, its symptoms and any findings scoped to it
- **B-3** — GIVEN a stage_id absent from the run WHEN explain_stage is called THEN it says the stage was not observed rather than returning an empty success

## Success Criteria

```bash
# eval_1: explain_stage is registered read-only with the right annotations
eval_1() {
  ( cd serve && uv run python -c "import asyncio; from apex_mcp.server import create_server; from apex_mcp.ch import ReadStore; from tests.conftest import FakeClient; s=create_server(ReadStore(FakeClient())); t={x.name:x for x in asyncio.run(s.list_tools())}; assert 'explain_stage' in t, sorted(t); a=t['explain_stage'].annotations; assert a.readOnlyHint and a.openWorldHint is False, a" )
}

# eval_2: a missing stage is stated, not silently empty
eval_2() {
  ( cd serve && ! grep -n 'Five tools' src/apex_mcp/server.py )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "explain_stage is registered read-only with the right annotations"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 20
  - id: eval_2
    description: "a missing stage is stated, not silently empty"
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

- Repairing the failing surface assertion here; that is the follow-up.
- Returning an empty stage object for an unknown stage_id.

## Do-Not-Touch

- `serve/tests/test_server_tools.py`
- `serve/src/apex_mcp/diagnose.py`

## Open Questions

(none — this task is fully specified)
