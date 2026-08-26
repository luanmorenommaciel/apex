---
id: T-20260820-tool-surface-six
title: "Re-pin the tool surface at six"
status: done
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260820-explain-stage-tool]
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
signed_off: false
signed_off_by: (none)
signed_off_at: (none)
accepted: false
accepted_by: (none)
accepted_at: (none)
---

# Re-pin the tool surface at six

> **Why:** An unnoticed tool on a server a model can call is a security event; the exact ordered assertion is the control that catches one.

## Goal

Move the ordered tool-name assertion from five names to six, keeping it an equality.

## Context

Deliberately its own commit so the surface change is legible in git log.

## Behavior

- **B-1** — GIVEN the built server WHEN list_tools() is called THEN the assertion compares against an exact ordered list of six names including explain_stage
- **B-2** — GIVEN a seventh tool were added WHEN the suite runs THEN it fails, because the assertion is neither a subset nor a count

## Success Criteria

```bash
# eval_1: the six-tool assertion exists and passes
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
    description: "the six-tool assertion exists and passes"
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

- Relaxing the assertion so it stops needing maintenance; the maintenance is the control.
- Bundling any source change into this unit.

## Do-Not-Touch

- `serve/src/apex_mcp`

## Open Questions

(none — this task is fully specified)
