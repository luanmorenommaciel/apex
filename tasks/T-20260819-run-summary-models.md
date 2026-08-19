---
id: T-20260819-run-summary-models
title: "Add RunSummary and RunList models"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
touches_paths: [serve/src/apex_mcp/models.py]
creates_paths: [serve/tests/test_runs.py]
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

# Add RunSummary and RunList models

> **Why:** FastMCP derives each tool's output schema from its return annotation, and schema-constrained output is the lane's stated mitigation against tool poisoning.

## Goal

Type the run-discovery payload, marking app_name as observed and therefore untrusted.

## Context

models.py has no intra-package runtime import and must keep none. app_name originates in the observed Spark job, so it belongs in UNTRUSTED_FIELDS alongside the existing finding text.

## Behavior

- **B-1** — GIVEN a RunSummary WHEN constructed with only job_id THEN it validates and every other field defaults
- **B-2** — GIVEN RunList WHEN model_json_schema() is called THEN it renders with runs as an array of RunSummary
- **B-3** — GIVEN any RunList WHEN it is serialized THEN untrusted_fields names app_name, because a Spark job author controls that string

## Success Criteria

```bash
# eval_1: the run model tests exist and pass
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_runs.py::test_run_summary_defaults_from_job_id" "tests/test_runs.py::test_run_list_schema_renders" "tests/test_runs.py::test_app_name_is_marked_untrusted" )
}

# eval_2: models.py still has no intra-package runtime import
eval_2() {
  ( cd serve && ! grep -nE '^from \.(ch|diagnose|server)|^from apex_mcp\.(ch|diagnose|server)' src/apex_mcp/models.py )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the run model tests exist and pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "models.py still has no intra-package runtime import"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
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

- Returning a bare dict instead of a model.
- Omitting app_name from the untrusted set because it looks like metadata; the Spark job author sets it.
- Importing ch or diagnose into models.py.

## Do-Not-Touch

- `serve/src/apex_mcp/ch.py`
- `serve/src/apex_mcp/server.py`

## Open Questions

(none — this task is fully specified)
