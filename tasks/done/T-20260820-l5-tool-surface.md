---
id: T-20260820-l5-tool-surface
title: "Re-pin the tool surface for verify_fix"
status: done
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260820-verify-fix-tool]
touches_paths: [serve/tests/test_server_tools.py]
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
signed_off: true
signed_off_by: sidymar
signed_off_at: 2026-08-20T14:43:18Z
accepted: true
accepted_by: sidymar
accepted_at: 2026-08-20T14:43:38Z
signed_off_sig: hmac-sha256-v2:5153084e:6eaa06978c1ce40d28ca9ff49b950c294d0d721eb8e4e2eec0675c60335bd83f
---

# Re-pin the tool surface for verify_fix

> **Why:** An unnoticed tool on a server a model can call is a security event.

## Goal

Move the ordered assertion to include verify_fix, keeping it an exact equality.

## Context

Its own commit so the surface change is legible in git log.

## Behavior

- **B-1** — GIVEN the built server WHEN list_tools() is called THEN the assertion is an exact ordered list including verify_fix
- **B-2** — GIVEN another tool were added WHEN the suite runs THEN it fails, because the assertion is neither a subset nor a count

## Success Criteria

```bash
# eval_1: the updated surface assertion exists and passes
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_server_tools.py::test_exactly_the_six_contracted_tools" )
}

# eval_2: the assertion is still an ordered equality
eval_2() {
  ( cd serve && ! grep -nE '(issubset|len\(_tools|set\(\[t\.name)' tests/test_server_tools.py )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the updated surface assertion exists and passes"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "the assertion is still an ordered equality"
    runnable: bash
    check_type: deterministic
    verifies: [B-2]
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

- Relaxing the assertion so it stops needing maintenance.
- Bundling source changes into this unit.

## Do-Not-Touch

- `serve/src/apex_mcp`

## Open Questions

(none — this task is fully specified)
