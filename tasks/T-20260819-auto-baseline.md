---
id: T-20260819-auto-baseline
title: "Let compare_runs pick its own baseline"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260819-runs-resource]
touches_paths: [serve/src/apex_mcp/diagnose.py, serve/src/apex_mcp/server.py, serve/tests/test_diagnose.py]
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

# Let compare_runs pick its own baseline

> **Why:** compare_runs needs two job_ids the user must already hold, which is the same wall list_runs just removed for analyze_run.

## Goal

Make baseline_job_id optional, defaulting to the most recent prior run of the same app_name with the same plan_fingerprint.

## Context

Same fingerprint matters - comparing across a plan change measures the plan, not the regression. When no such run exists, say so rather than silently comparing against something else.

## Behavior

- **B-1** — GIVEN a current job_id and no baseline WHEN compare_runs is called THEN it selects the most recent prior run with the same app_name and plan_fingerprint
- **B-2** — GIVEN no prior run shares that fingerprint WHEN compare_runs is called with no baseline THEN it returns a stated no-baseline result rather than comparing against an unrelated run
- **B-3** — GIVEN an explicit baseline_job_id WHEN compare_runs is called THEN that baseline is used unchanged, exactly as today
- **B-4** — GIVEN the chosen baseline WHEN the result is read THEN the payload names which run was selected and why

## Success Criteria

```bash
# eval_1: the auto-baseline tests exist and pass
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_diagnose.py::test_auto_baseline_picks_same_fingerprint" "tests/test_diagnose.py::test_auto_baseline_refuses_across_plan_change" "tests/test_diagnose.py::test_explicit_baseline_is_unchanged" )
}

# eval_2: the whole diagnosis suite stays green
eval_2() {
  ( cd serve && uv run --extra dev pytest tests/test_diagnose.py )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the auto-baseline tests exist and pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "the whole diagnosis suite stays green"
    runnable: bash
    check_type: deterministic
    verifies: [B-4]
    terminal: true
    expected_duration_sec: 30
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

- Falling back to any recent run when no fingerprint matches; a silent wrong baseline is worse than none.
- Making baseline selection implicit in the payload, so a user cannot tell what was compared.
- Changing the behavior of an explicitly supplied baseline.

## Do-Not-Touch

- `serve/src/apex_mcp/ch.py`
- `serve/tests/test_server_tools.py`

## Open Questions

(none — this task is fully specified)
