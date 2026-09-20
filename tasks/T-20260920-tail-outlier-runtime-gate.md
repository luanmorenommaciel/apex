---
id: T-20260920-tail-outlier-runtime-gate
title: "Prove the tail-outlier public path against real canonical telemetry"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [dev/scripts/canonical_e2e_assert.py, dev/scripts/e2e_canonical.sh, dev/tests/test_canonical_e2e_assert.py]
creates_paths: []
source_note: "https://github.com/luanmorenommaciel/apex/issues/123"
created: "2026-09-20T00:00:00Z"
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
signed_off_at: 2026-09-20T12:48:47Z
accepted: false
accepted_by: (none)
accepted_at: (none)
signed_off_sig: hmac-sha256-v3:6af918b1:96f0d3acede4a49b0fa80fc5a67d99fffaadcbc16764a6214798f07a854e946e
---

# Prove the tail-outlier public path against real canonical telemetry

> **Why:** The offline route can prove source wiring but cannot show that a real Spark job emits sufficient duration-tail telemetry, that it reaches canonical ClickHouse, or that the public gate reaches the Engine watcher. The current canonical assertion rejects tail_outlier before that proof can occur.

## Goal

Make tail_outlier a manually runnable, fail-closed local Docker runtime gate that validates fresh Spark telemetry before the existing public package gate checks for tail_outlier_watcher.

## Context

The user explicitly authorized local runtime validation. This is not a GitHub Actions job and must not claim remote CI evidence. It uses the existing package bootstrap and canonical Docker topology only when the operator elects to provision it; it must not stop, remove, or overwrite pre-existing Docker resources.

## Behavior

- **B-1** — GIVEN canonical ClickHouse stage rows for a tail_outlier job WHEN the canonical assertion evaluates them THEN it accepts only a stage with at least 100 tasks and effective duration samples, positive effective p50, and strict effective max/p50 greater than 10
- **B-2** — GIVEN absent, incomplete, or non-qualifying tail telemetry WHEN the assertion evaluates it THEN it fails with a diagnostic rather than treating generic stage telemetry or p99 data alone as proof
- **B-3** — GIVEN dev/scripts/e2e_canonical.sh is asked for tail_outlier WHEN a canonical Docker platform is already provisioned THEN it submits the real tail_outlier Spark workload and waits for canonical ClickHouse evidence using the new scenario
- **B-4** — GIVEN the existing public package command runs after canonical evidence arrives WHEN Engine analyzes that fresh job in dry-run/no-Crew mode THEN its existing fail-closed tail_outlier_watcher check remains the final public success condition
- **B-5** — GIVEN configuration or canonical Docker prerequisites are absent WHEN a runtime gate is requested THEN it refuses without starting, stopping, deleting, or reusing unrelated resources

## Success Criteria

```bash
# eval_1: focused canonical assertion tests discriminate the tail-outlier telemetry shape without Docker
eval_1() {
  python3 -m unittest dev/tests/test_canonical_e2e_assert.py
}

# eval_2: manually run the public tail-outlier gate against a freshly bootstrapped local canonical Docker platform
eval_2() {
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/apex.ps1 tail-outlier
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "focused canonical assertion tests discriminate the tail-outlier telemetry shape without Docker"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "manually run the public tail-outlier gate against a freshly bootstrapped local canonical Docker platform"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3, B-4, B-5]
    terminal: true
    expected_duration_sec: 1800
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

- Lowering the 100-sample or strict max/p50 greater-than-10 proof threshold.
- Treating a prior log, a DryRun, source inspection, or generic ClickHouse row as runtime proof.
- Changing Engine watcher policy, Spark telemetry schema, DDL, Collector behavior, or CI configuration.
- Starting, stopping, deleting, or mutating an unrelated pre-existing Docker environment.
- Claiming this local gate proves GitHub Actions or remote deployment.

## Do-Not-Touch

- `engine/src`
- `engine/tests`
- `infra`
- `collect`
- `jar`
- `serve`
- `front`
- `.github`
- `scripts/apex.ps1`

## Open Questions

(none — this task is fully specified)
