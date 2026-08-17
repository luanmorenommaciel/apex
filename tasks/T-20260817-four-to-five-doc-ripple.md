---
id: T-20260817-four-to-five-doc-ripple
title: "Close the four-to-five documentation ripple"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260817-register-apex-status, T-20260817-gate-status-assert, T-20260817-stdio-gate-five-tools, T-20260817-cursor-codex-config]
touches_paths: [serve/README.md, serve/VALIDATION.md, docs/lanes/SERVE.md]
creates_paths: []
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
signed_off: false
signed_off_by: (none)
signed_off_at: (none)
accepted: false
accepted_by: (none)
accepted_at: (none)
---

# Close the four-to-five documentation ripple

> **Why:** VALIDATION.md records what was observed, so a stale record is a false one.

## Goal

Leave no document claiming four tools, with a test count copied from an actual run.

## Context

Thirteen sites assert the four-tool surface across code, tests, gates and three documents. Source docstrings are handled by their own units; this one closes the prose. Sized M for three document paths.

## Behavior

- **B-1** — GIVEN serve/README.md WHEN read THEN the tool table has five rows and the prose and install comment match
- **B-2** — GIVEN serve/VALIDATION.md WHEN read THEN the scope table lists apex_status and the test count matches the suite's actual output
- **B-3** — GIVEN docs/lanes/SERVE.md WHEN read THEN the mission statement and the T11 accept criterion both say five

## Success Criteria

```bash
# eval_1: no document or gate still claims a four-tool surface
eval_1() {
  ( ! grep -rniE 'four tools|exactly 4 tools|four contracted|all four' serve/ docs/lanes/SERVE.md --include='*.md' --include='*.py' )
}

# eval_2: the recorded test count equals the count the suite actually reports
eval_2() {
  ( cd serve && n=$(uv run --extra dev pytest 2>&1 | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+') && grep -q "$n passed" VALIDATION.md )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "no document or gate still claims a four-tool surface"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 10
  - id: eval_2
    description: "the recorded test count equals the count the suite actually reports"
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
- Editing the SERVE.md T1-T14 checklist, which records what shipped.

## Do-Not-Touch

- `serve/src/apex_mcp`
- `serve/tests`

## Open Questions

(none — this task is fully specified)
