---
id: T-20260820-verify-fix-tool
title: "Add verify_fix"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260820-verifications-read-layer, T-20260820-verification-models]
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

# Add verify_fix

> **Why:** suggest_fix returns a diff and stops. The user applies it, reruns, and is on their own - while the verify lane already holds the answer.

## Goal

verify_fix(job_id, finding_id?) returns what the verify lane concluded about the proposed fixes.

## Context

The sixth tool in this leg's numbering. L1, L3 and L6 each move the same surface assertion in their own worktrees; whichever lands last reconciles. The five-tools assertion is expected to fail after this unit.

## Behavior

- **B-1** — GIVEN a built server WHEN list_tools() is called THEN verify_fix is present with readOnlyHint True
- **B-2** — GIVEN a job_id with a predicted verification WHEN verify_fix is called THEN it reports the predicted range, the safety verdict and the confidence
- **B-3** — GIVEN a job_id with no verification rows WHEN verify_fix is called THEN it says the verify lane has not assessed this run, rather than returning an empty success
- **B-4** — GIVEN a verification whose safety verdict blocked execution WHEN verify_fix is called THEN the block and its reason are surfaced, not hidden behind a low confidence

## Success Criteria

```bash
# eval_1: verify_fix is registered read-only
eval_1() {
  ( cd serve && uv run python -c "import asyncio; from apex_mcp.server import create_server; from apex_mcp.ch import ReadStore; from tests.conftest import FakeClient; s=create_server(ReadStore(FakeClient())); t={x.name:x for x in asyncio.run(s.list_tools())}; assert 'verify_fix' in t, sorted(t); assert t['verify_fix'].annotations.readOnlyHint" )
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
    description: "verify_fix is registered read-only"
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

- Recomputing a prediction in serve; the verify lane owns that judgement and serve reports it.
- Collapsing a safety block into low confidence - they mean different things to a user.
- Repairing the surface assertion here.

## Do-Not-Touch

- `serve/tests/test_server_tools.py`
- `serve/src/apex_mcp/ch.py`

## Open Questions

(none — this task is fully specified)
