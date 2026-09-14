---
id: T-20260820-coverage-freshness
title: "Report what the diagnosis actually saw"
status: done
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260820-detail-parameter]
touches_paths: [serve/src/apex_mcp/models.py, serve/src/apex_mcp/diagnose.py]
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

# Report what the diagnosis actually saw

> **Why:** A bare healthy verdict and a healthy verdict that says what it saw are different claims. W1 in the weaknesses doc is exactly this failure - a dropped job_id is indistinguishable from a clean run.

## Goal

Every Diagnosis carries stage count observed, findings observed, and how old the newest event is.

## Context

analyze() already returns status=not_found for zero stages. This adds the weaker case - telemetry arrived, but thin or stale - which currently reads as full confidence.

## Behavior

- **B-1** — GIVEN any diagnosis WHEN it is read THEN it reports stages observed, findings observed and the age of the newest event
- **B-2** — GIVEN a run whose newest event is hours old WHEN the diagnosis is read THEN the age is reported as a number and is never judged stale or fresh by Apex
- **B-3** — GIVEN a healthy verdict on a single observed stage WHEN the diagnosis is read THEN the coverage makes the thinness visible rather than implying a full picture

## Success Criteria

```bash
# eval_1: the coverage tests exist and pass
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_diagnose.py::test_diagnosis_reports_coverage" "tests/test_diagnose.py::test_thin_coverage_is_visible_on_a_healthy_verdict" )
}

# eval_2: Apex reports the age and does not judge it
eval_2() {
  ( cd serve && uv run --extra dev pytest "tests/test_diagnose.py::test_ingest_age_is_reported_not_judged" )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the coverage tests exist and pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-3]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "Apex reports the age and does not judge it"
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

- Calling a run stale past a threshold; a nightly batch and a streaming job disagree, and a false stale is worse than none.
- Computing coverage from a second query rather than from the rows already in hand.

## Do-Not-Touch

- `serve/src/apex_mcp/ch.py`
- `serve/src/apex_mcp/server.py`

## Open Questions

(none — this task is fully specified)
