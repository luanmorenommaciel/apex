---
id: T-20260918-tail-outlier-finding-contract
title: "Add an honest tail-outlier finding contract"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [engine/src/apex_engine/schema.py, engine/src/apex_engine/validation.py, engine/tests/test_contract_engine.py]
creates_paths: []
source_note: "https://github.com/luanmorenommaciel/apex/issues/123"
created: "2026-09-18T00:00:00Z"
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
signed_off_by: augustosilva
signed_off_at: 2026-09-19T00:44:26Z
accepted: false
accepted_by: (none)
accepted_at: (none)
signed_off_sig: hmac-sha256-v3:6af918b1:86d050825f76b37bb2a88338d263bafbd4f234f92f1e30bd7e429a798b847312
---

# Add an honest tail-outlier finding contract

> **Why:** Historical tail-outlier code labeled a duration-only candidate as SKEW_ON_JOIN, but the current validator correctly requires volume, closed-form tail-bound evidence and a join node for that type.

## Goal

Add an additive TAIL_OUTLIER finding type and a narrow validator that accepts only structured sparse-duration-tail evidence without weakening the current skew validator.

## Context

findings.type is an open String, so this needs no DDL migration. The new type is a warning-level diagnostic candidate, not proof of join skew or root cause. This leaf does not implement or register a watcher.

## Behavior

- **B-1** — GIVEN a Finding typed TAIL_OUTLIER WHEN it is serialized or validated THEN it remains an additive distinct type and is not coerced to SKEW_ON_JOIN or TASK_SKEW
- **B-2** — GIVEN structured evidence with task_count and duration_sample_count at least 100, positive effective p50/max, and tail_ratio strictly greater than 10 WHEN the finding is validated THEN it is accepted without requiring shuffle bytes, join evidence or a cluster-width verdict
- **B-3** — GIVEN missing, non-numeric or out-of-range tail measurements WHEN the finding is validated THEN it is rejected with a deterministic tail-outlier validation issue
- **B-4** — GIVEN an existing SKEW_ON_JOIN or TASK_SKEW finding WHEN validation runs THEN all current volume, join, closed-form and confidence requirements remain unchanged

## Success Criteria

```bash
# eval_1: focused contract tests accept coherent tail evidence and reject incomplete or boundary evidence
eval_1() {
  ( cd engine && uv run --extra dev pytest -q "tests/test_contract_engine.py::test_tail_outlier_contract_accepts_coherent_duration_candidate" "tests/test_contract_engine.py::test_tail_outlier_contract_rejects_incomplete_or_boundary_evidence" "tests/test_contract_engine.py::test_tail_outlier_type_does_not_weaken_skew_validation" -p no:warnings )
}

# eval_2: complete offline Engine suite remains green after the additive type
eval_2() {
  ( cd engine && uv run --extra dev pytest -q -p no:warnings )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "focused contract tests accept coherent tail evidence and reject incomplete or boundary evidence"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3, B-4]
    terminal: true
    expected_duration_sec: 45
  - id: eval_2
    description: "complete offline Engine suite remains green after the additive type"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-4]
    terminal: true
    expected_duration_sec: 90
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

- Reusing SKEW_ON_JOIN for duration-only evidence.
- Weakening _skew_issues or adding an exception that lets skew bypass volume and plan checks.
- Adding a DDL migration for an open String field.
- Implementing a watcher or DEV/package wiring in this contract leaf.

## Do-Not-Touch

- `engine/src/apex_engine/watchers`
- `dev`
- `scripts`
- `contract/findings.ddl.sql`
- `infra`

## Open Questions

(none — this task is fully specified)
