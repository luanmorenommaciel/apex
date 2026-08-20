---
id: T-20260820-detail-parameter
title: "Give analyze_run a detail level"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
touches_paths: [serve/src/apex_mcp/diagnose.py, serve/src/apex_mcp/server.py, serve/tests/test_diagnose.py]
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

# Give analyze_run a detail level

> **Why:** The real P0 run returns 17 stages plus every finding in one payload. The default answer to "why was this slow" should be three lines, not a data dump the reader has to triage.

## Goal

analyze_run takes detail=summary|stages|full, defaulting to summary.

## Context

analyze() already computes everything; this trims what leaves. Nothing may be recomputed per level - the same diagnosis must underlie all three, or two callers get different answers to the same question.

## Behavior

- **B-1** — GIVEN no detail argument WHEN analyze_run is called THEN the payload carries status, worst stage, primary symptom, summary and aqe_ground_truth, and omits the per-stage and per-finding arrays
- **B-2** — GIVEN detail=stages WHEN analyze_run is called THEN the stage array is included and findings are still omitted
- **B-3** — GIVEN detail=full WHEN analyze_run is called THEN the payload is byte-identical to today's response
- **B-4** — GIVEN any detail level WHEN the worst stage and primary symptom are read THEN they are the same across all three, because trimming never re-runs the analysis

## Success Criteria

```bash
# eval_1: the detail-level tests exist and pass
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_diagnose.py::test_summary_omits_stage_and_finding_arrays" "tests/test_diagnose.py::test_stages_level_includes_stages_not_findings" "tests/test_diagnose.py::test_full_level_is_unchanged_from_today" )
}

# eval_2: every level agrees on the verdict
eval_2() {
  ( cd serve && uv run --extra dev pytest "tests/test_diagnose.py::test_verdict_is_identical_across_detail_levels" )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the detail-level tests exist and pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "every level agrees on the verdict"
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

- Recomputing the diagnosis per level; trim one result, never analyse three times.
- Making summary the only tested path while stages and full drift.
- Dropping aqe_ground_truth from summary - it is the note that stops a user misreading skew.

## Do-Not-Touch

- `serve/src/apex_mcp/ch.py`
- `serve/tests/test_server_tools.py`

## Open Questions

(none — this task is fully specified)
