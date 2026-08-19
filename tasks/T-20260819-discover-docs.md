---
id: T-20260819-discover-docs
title: "Document run discovery across the lane docs"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260819-runs-gates]
touches_paths: [serve/README.md, serve/VALIDATION.md, docs/lanes/SERVE-LEGS.md]
creates_paths: []
source_note: "docs/lanes/SERVE-LEGS.md"
created: "2026-08-19T00:00:00Z"
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

# Document run discovery across the lane docs

> **Why:** VALIDATION.md records what was observed, so leaving it at four tools makes it a false record rather than a stale one.

## Goal

Reflect the fifth tool, the first resource and the auto-baseline in every lane document.

## Context

SERVE-LEGS.md lists find_run and latest_run as separate features; record that one filtered tool covers them and why, so the decision survives the session that made it.

## Behavior

- **B-1** — GIVEN serve/README.md WHEN read THEN the tool table lists list_runs, the resource is documented, and no prose says four tools
- **B-2** — GIVEN serve/VALIDATION.md WHEN read THEN it records the run-discovery gate result and a test count copied from an actual run
- **B-3** — GIVEN docs/lanes/SERVE-LEGS.md WHEN read THEN L2 marks F2.1 to F2.5 delivered, and states that one filtered tool subsumed find_run and latest_run

## Success Criteria

```bash
# eval_1: no lane document still claims a four-tool surface
eval_1() {
  ( ! grep -rniE 'four tools|exactly 4 tools' serve/ docs/lanes/SERVE.md docs/lanes/SERVE-LEGS.md --include=*.md )
}

# eval_2: the recorded test count equals what the suite actually reports
eval_2() {
  ( cd serve && n=$(uv run --extra dev pytest 2>&1 | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+') && grep -q "$n passed" VALIDATION.md )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "no lane document still claims a four-tool surface"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-3]
    terminal: true
    expected_duration_sec: 10
  - id: eval_2
    description: "the recorded test count equals what the suite actually reports"
    runnable: bash
    check_type: deterministic
    verifies: [B-2]
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

- Writing a test count from memory instead of copying it from a run.
- Recording gate results without rerunning the gates.
- Marking L2 features delivered that this plan did not build.

## Do-Not-Touch

- `serve/src/apex_mcp`
- `serve/tests`

## Open Questions

(none — this task is fully specified)
