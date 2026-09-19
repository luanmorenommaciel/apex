---
id: T-20260919-tail-outlier-wiring-audit-hardening
title: "Harden tail-outlier package fail-closed regression coverage"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [tests/test_tail_outlier_package.py]
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
signed_off_at: 2026-09-19T19:07:00Z
accepted: false
accepted_by: (none)
accepted_at: (none)
signed_off_sig: hmac-sha256-v3:6af918b1:bc2624fca27d3a69f40f8606861e4e5d99f7ac8626e108aa47f3657a304fbc68
---

# Harden tail-outlier package fail-closed regression coverage

> **Why:** Independent review found that current static tests can pass after a guard condition is removed because they only search for bare messages and watcher substrings.

## Goal

Prove the existing package gate remains fail closed through condition-plus-throw structural assertions, without changing the PowerShell production gate or claiming runtime success.

## Context

This is a static test-only leaf. The gate still does not prove Spark, OTLP, ClickHouse or live watcher behavior.

## Behavior

- **B-1** — GIVEN the tail-outlier public gate WHEN static package regression tests inspect its three failure paths THEN each missing-job, nonzero-engine, and absent-watcher check is asserted as its own condition followed by its own throw
- **B-2** — GIVEN the telemetry failure path WHEN static tests inspect it THEN the watcher identifier alone cannot satisfy the assertion outside the negative-match guard and throw
- **B-3** — GIVEN the successful route WHEN static tests inspect it THEN no-Crew invocation and the passed marker remain checked without asserting live runtime behavior

## Success Criteria

```bash
# eval_1: focused package guard regression tests pass
eval_1() {
  ( cd engine && uv run --extra dev pytest -q ../tests/test_tail_outlier_package.py -p no:warnings )
}

# eval_2: complete root offline test gate remains green
eval_2() {
  ( cd engine && uv run --extra dev pytest -q ../tests -p no:warnings )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "focused package guard regression tests pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 45
  - id: eval_2
    description: "complete root offline test gate remains green"
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

- Editing dev/scripts/e2e_canonical.ps1 or scripts/apex.ps1 unless a stronger test exposes a real production defect.
- Starting containers, Spark, ClickHouse, OTLP, or Crew/LLM.
- Treating static string checks as live proof.

## Do-Not-Touch

- `dev`
- `scripts`
- `engine/src`
- `front`
- `serve`
- `infra`

## Open Questions

(none — this task is fully specified)
