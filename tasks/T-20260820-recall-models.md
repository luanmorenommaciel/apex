---
id: T-20260820-recall-models
title: "Type the recall payload"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
touches_paths: [serve/src/apex_mcp/models.py]
creates_paths: [serve/tests/test_recall_view.py]
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

# Type the recall payload

> **Why:** A claim about what configuration worked is the most consequential thing this server can say, so it must be schema-constrained and carry its own uncertainty.

## Goal

SimilarPlan and PriorRun models carrying similarity, config and outcome, with app_name marked untrusted.

## Context

app_name comes from the observed Spark job, exactly as in list_runs. Similarity must be carried as a number the reader can judge, never collapsed into a same or different boolean.

## Behavior

- **B-1** — GIVEN a SimilarPlan WHEN constructed THEN it carries the fingerprint and a similarity score between 0 and 1
- **B-2** — GIVEN a PriorRun WHEN serialized THEN it carries the config columns, wall clock, and which config_source they came from
- **B-3** — GIVEN any recall payload WHEN serialized THEN untrusted_fields names app_name
- **B-4** — GIVEN a run whose config_source is unknown WHEN the payload is read THEN that is visible rather than presented as an observed configuration

## Success Criteria

```bash
# eval_1: the recall model tests exist and pass
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_recall_view.py::test_similar_plan_carries_bounded_similarity" "tests/test_recall_view.py::test_prior_run_carries_config_and_source" "tests/test_recall_view.py::test_app_name_is_marked_untrusted" )
}

# eval_2: an unknown config source is not laundered into an observed one
eval_2() {
  ( cd serve && uv run --extra dev pytest "tests/test_recall_view.py::test_unknown_config_source_stays_visible" )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the recall model tests exist and pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "an unknown config source is not laundered into an observed one"
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

- Collapsing similarity into a boolean; the reader needs the number to judge the neighbour.
- Defaulting config_source to observed, which turns a seeded guess into evidence.

## Do-Not-Touch

- `serve/src/apex_mcp/ch.py`
- `serve/src/apex_mcp/server.py`

## Open Questions

(none — this task is fully specified)
