---
id: T-20260918-tail-outlier-watcher-offline
title: "Implement and register the deterministic tail-outlier watcher"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260918-tail-outlier-finding-contract]
supersedes: (none)
touches_paths: [engine/src/apex_engine/watchers/__init__.py, engine/tests/test_watchers.py]
creates_paths: [engine/src/apex_engine/watchers/tail_outlier.py]
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
signed_off_at: 2026-09-19T00:44:27Z
accepted: false
accepted_by: (none)
accepted_at: (none)
signed_off_sig: hmac-sha256-v3:6af918b1:da6c5a8d94c7ba11271909d37f77b3cbb453b09595e3a328d5b06dad0b769531
---

# Implement and register the deterministic tail-outlier watcher

> **Why:** The v0.5 data fields and ADR describe a sparse duration-tail signal, but current main has no watcher implementation or registration, so the public gate can never observe tail_outlier_watcher.

## Goal

Add a pure deterministic watcher that emits an honest TAIL_OUTLIER warning only for a large sparse effective-duration tail not already owned by the current skew watcher.

## Context

This is Engine Slice A only. It does not add the canonical DEV scenario, remove the package throw, run a live workload, or call Crew/LLM. Historical code is evidence only and must not be copied verbatim because its fixed p99 threshold and SKEW_ON_JOIN type conflict with the current contract.

## Behavior

- **B-1** — GIVEN at least 100 tasks and 100 effective duration samples with effective max/p50 strictly greater than 10 WHEN current skew evaluation produces no finding THEN the watcher emits a warning/MEDIUM TAIL_OUTLIER candidate with the effective p50, p99, max, ratios, source and counts in structured details
- **B-2** — GIVEN successful-task samples exist WHEN the watcher evaluates the stage THEN it uses the retry-safe successful population and ignores a tail visible only in raw attempts
- **B-3** — GIVEN no successful-task sample exists WHEN the watcher evaluates a historical stage THEN it uses the declared legacy duration and sample-count fallback and labels that source
- **B-4** — GIVEN 99 tasks, 99 effective samples, an exact 10 ratio or zero p50 WHEN evaluation runs THEN no finding is emitted
- **B-5** — GIVEN current skew.evaluate returns a volume-aware finding WHEN tail evaluation runs THEN tail_outlier returns none rather than duplicating ownership
- **B-6** — GIVEN high volume that does not satisfy current skew policy WHEN a valid sparse duration tail exists THEN the tail candidate may still emit because suppression is based on actual skew ownership, not volume presence alone
- **B-7** — GIVEN the watcher registry and run_all_offline WHEN Engine evaluates eligible aggregates THEN tail_outlier_watcher is registered, reachable, deterministic and makes no Crew/LLM calls

## Success Criteria

```bash
# eval_1: focused watcher tests cover retry-safe, historical, boundaries, ownership and registry reachability
eval_1() {
  ( cd engine && uv run --extra dev pytest -q "tests/test_watchers.py::test_tail_outlier_prefers_retry_safe_population" "tests/test_watchers.py::test_tail_outlier_uses_legacy_fallback" "tests/test_watchers.py::test_tail_outlier_boundaries_are_silent" "tests/test_watchers.py::test_tail_outlier_defers_to_current_skew_owner" "tests/test_watchers.py::test_tail_outlier_allows_high_volume_without_skew_owner" "tests/test_watchers.py::test_tail_outlier_is_registered_and_reachable" -p no:warnings )
}

# eval_2: contract validator and complete offline Engine suite remain green
eval_2() {
  ( cd engine && uv run --extra dev pytest -q -p no:warnings )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "focused watcher tests cover retry-safe, historical, boundaries, ownership and registry reachability"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3, B-4, B-5, B-6, B-7]
    terminal: true
    expected_duration_sec: 60
  - id: eval_2
    description: "contract validator and complete offline Engine suite remain green"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-5, B-7]
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

- Copying historical fixed p99/p50 <= 5 logic or emitting SKEW_ON_JOIN.
- Suppressing every stage merely because shuffle-volume samples exist.
- Duplicating skew policy instead of asking current skew.evaluate whether it owns the verdict.
- Adding SQL, store I/O, Crew, LLM, DEV/package wiring or runtime evidence.
- Lowering the strict max/p50 greater-than-10 boundary or reducing the 100-sample gate.

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
