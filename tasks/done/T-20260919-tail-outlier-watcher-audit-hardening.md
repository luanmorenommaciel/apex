---
id: T-20260919-tail-outlier-watcher-audit-hardening
title: "Harden emitted tail-outlier watcher contract coverage"
status: done
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260919-tail-outlier-contract-audit-hardening]
supersedes: (none)
touches_paths: [engine/src/apex_engine/schema.py, engine/src/apex_engine/watchers/__init__.py, engine/tests/test_watchers.py]
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
signed_off_at: 2026-09-19T19:06:53Z
accepted: true
accepted_by: augustosilva
accepted_at: 2026-09-19T20:59:22Z
signed_off_sig: hmac-sha256-v3:6af918b1:b51644fdaf37e6ae68751eb83eafa4b6f21ff9e4951e72090b3803344c2210c9
accepted_tier: 1
accepted_attempt_id: d02ca52b-761d-4bb3-b801-fa3a34b44506
accepted_authorization_ref: hmac-sha256-v3:6af918b1:b51644fdaf37e6ae68751eb83eafa4b6f21ff9e4951e72090b3803344c2210c9
acceptance_record_digest: sha256:98e454fff7c41a9e9723a124bb6def8f3bc54121471097dfd85fdaa442efaa1a
---

# Harden emitted tail-outlier watcher contract coverage

> **Why:** Independent review approved watcher behavior but found unpinned emitted identity/validator integration and two stale comments.

## Goal

Add regression coverage for the actual watcher-emitted finding contract and correct only confirmed stale watcher documentation, without changing watcher detection behavior.

## Context

The preceding remediation hardens the validator. This leaf is test and documentation hardening only; it does not adjust thresholds, source fallback, registry behavior, DEV/package wiring, or runtime proof.

## Behavior

- **B-1** — GIVEN a qualifying retry-safe duration tail WHEN the watcher emits a finding THEN tests assert its type, warning severity, medium confidence, detector identity, and required structured details
- **B-2** — GIVEN the actual watcher-emitted finding WHEN it is sent through the validator THEN it is accepted as the same contract the watcher claims to emit
- **B-3** — GIVEN watcher-adjacent comments and registry documentation WHEN they describe watcher count or fields used by tail_outlier THEN stale wording is corrected without changing production behavior

## Success Criteria

```bash
# eval_1: focused watcher contract tests pass
eval_1() {
  ( cd engine && uv run --extra dev pytest -q tests/test_watchers.py -p no:warnings )
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
    description: "focused watcher contract tests pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 60
  - id: eval_2
    description: "complete offline Engine suite remains green"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
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

- Changing detection thresholds, source fallback, skew ownership, registry membership, or confidence policy.
- Adding I/O, Crew, LLM, DEV/package wiring, DDL, or runtime claims.

## Do-Not-Touch

- `dev`
- `scripts`
- `jar`
- `collect`
- `infra`
- `serve`
- `front`

## Open Questions

(none — this task is fully specified)
