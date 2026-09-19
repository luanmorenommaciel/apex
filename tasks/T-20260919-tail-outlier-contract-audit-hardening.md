---
id: T-20260919-tail-outlier-contract-audit-hardening
title: "Harden tail-outlier contract rejection boundaries"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [engine/src/apex_engine/validation.py, engine/tests/test_contract_engine.py]
creates_paths: []
source_note: "https://github.com/luanmorenommaciel/apex/issues/123"
created: "2026-09-19T00:00:00Z"
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
signed_off_at: 2026-09-19T19:06:51Z
accepted: true
accepted_by: augustosilva
accepted_at: 2026-09-19T20:57:50Z
signed_off_sig: hmac-sha256-v3:6af918b1:9c60aaa1f963c6b8b69ae30dc9ccfbe8aadc1d05c941f0ba6a5d56f98b82fe44
accepted_tier: 1
accepted_attempt_id: 7b64b618-8bc5-4010-9f4a-cf8ef9dac160
accepted_authorization_ref: hmac-sha256-v3:6af918b1:9c60aaa1f963c6b8b69ae30dc9ccfbe8aadc1d05c941f0ba6a5d56f98b82fe44
acceptance_record_digest: sha256:6ba61e395fcb89847364a0996017b4fa1b82d9d42c97e16b3439bb49729845a9
---

# Harden tail-outlier contract rejection boundaries

> **Why:** Independent review found that an enormous Python integer can escape the tail-outlier validator through OverflowError, contradicting the fail-closed invalid-evidence contract.

## Goal

Make tail-outlier numeric rejection fail closed for unrepresentable values and pin every declared threshold and skew-isolation boundary without changing the finding type, threshold policy, watcher, or persistence.

## Context

This is contract-only audit remediation. It may make numeric conversion safe but must not alter TAIL_OUTLIER acceptance semantics for finite valid values or weaken SKEW_ON_JOIN/TASK_SKEW validation.

## Behavior

- **B-1** — GIVEN an enormous integer, bool, string, NaN, or infinity in a tail numeric field WHEN validation runs THEN it returns deterministic invalid-tail evidence issues and never raises conversion overflow
- **B-2** — GIVEN tail evidence at 99/100 task or sample counts, zero/negative p50 or max, and exact/above-10 tail ratio WHEN validation runs THEN only the stated inclusive and strict boundaries are accepted
- **B-3** — GIVEN tail-shaped details attached to SKEW_ON_JOIN or TASK_SKEW WHEN required skew evidence remains missing THEN skew validation still rejects it rather than laundering it through the tail contract

## Success Criteria

```bash
# eval_1: tail-outlier contract boundary and skew-isolation tests pass
eval_1() {
  ( cd engine && uv run --extra dev pytest -q tests/test_contract_engine.py -p no:warnings )
}

# eval_2: complete offline Engine suite remains green
eval_2() {
  ( cd engine && uv run --extra dev pytest -q -p no:warnings )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "tail-outlier contract boundary and skew-isolation tests pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 60
  - id: eval_2
    description: "complete offline Engine suite remains green"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
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

- Changing the 100-count or strict greater-than-10 threshold policy.
- Weakening skew validation, adding DDL, watcher behavior, DEV/package wiring, or runtime proof.
- Coercing invalid numeric evidence into accepted values.

## Do-Not-Touch

- `engine/src/apex_engine/schema.py`
- `engine/src/apex_engine/watchers`
- `dev`
- `scripts`
- `contract/findings.ddl.sql`
- `infra`

## Open Questions

(none — this task is fully specified)
