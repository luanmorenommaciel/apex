---
id: T-20260820-noise-floor-honesty
title: "Never call a configuration better without a floor"
status: done
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260820-recall-runs-tool]
touches_paths: [serve/src/apex_mcp/diagnose.py, serve/tests/test_diagnose.py]
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
signed_off_by: sidymar.prexede@gmail.com
signed_off_at: "2026-08-20T00:00:00Z"
accepted: true
accepted_by: sidymar.prexede@gmail.com
accepted_at: "2026-08-20T00:00:00Z"
---

# Never call a configuration better without a floor

> **Why:** The whole value of cross-run memory is distinguishing this config is better from this run happened to be faster. Rank prior runs by wall clock and you have built a machine for confusing the two.

## Goal

Prior runs are reported with their measurements, and a configuration is only called better against a measured floor.

## Context

CONTRACT.md rule 2 already forbids serve inventing a dispersion figure, and compare_runs honours it via noise_floor_pct. Cross-run recall must honour the same rule - the memory lane computes a floor, serve reports it and refuses to rank without one.

## Behavior

- **B-1** — GIVEN prior runs and no noise floor WHEN recall is summarised THEN runs are reported as measurements and no configuration is called better
- **B-2** — GIVEN prior runs and a measured floor WHEN a difference clears that floor THEN it may be called better, and the floor it cleared is named
- **B-3** — GIVEN a difference inside the floor WHEN recall is summarised THEN it is reported as indistinguishable from run-to-run variation
- **B-4** — GIVEN a single prior run WHEN recall is summarised THEN no comparison is drawn, because one run cannot measure its own dispersion

## Success Criteria

```bash
# eval_1: the floor-honesty tests exist and pass
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_diagnose.py::test_no_floor_means_no_better_claim" "tests/test_diagnose.py::test_difference_inside_floor_is_indistinguishable" "tests/test_diagnose.py::test_single_prior_run_draws_no_comparison" )
}

# eval_2: a cleared floor is named in the claim
eval_2() {
  ( cd serve && uv run --extra dev pytest "tests/test_diagnose.py::test_cleared_floor_is_named" )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the floor-honesty tests exist and pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-3, B-4]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "a cleared floor is named in the claim"
    runnable: bash
    check_type: deterministic
    verifies: [B-2]
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

- Sorting prior runs by wall clock and presenting the top one as the best configuration.
- Inventing a floor from the runs being compared; CONTRACT rule 2 forbids exactly that.

## Do-Not-Touch

- `serve/src/apex_mcp/ch.py`
- `serve/src/apex_mcp/server.py`

## Open Questions

(none — this task is fully specified)
