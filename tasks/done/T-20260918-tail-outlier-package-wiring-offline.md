---
id: T-20260918-tail-outlier-package-wiring-offline
title: "Wire tail-outlier through the canonical runner and package command"
status: done
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [dev/scripts/e2e_canonical.ps1, scripts/apex.ps1]
creates_paths: [tests/test_tail_outlier_package.py]
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
signed_off_at: 2026-09-19T00:48:21Z
accepted: true
accepted_by: augustosilva
accepted_at: 2026-09-19T00:49:31Z
signed_off_sig: hmac-sha256-v3:6af918b1:7abe667374862ff6a0aff52142bc67a996787c6e9cb0757d7c023566206b1e56
accepted_tier: 1
accepted_attempt_id: c122a994-0ee1-40e6-a7bf-f1da00214913
accepted_authorization_ref: hmac-sha256-v3:6af918b1:7abe667374862ff6a0aff52142bc67a996787c6e9cb0757d7c023566206b1e56
acceptance_record_digest: sha256:f3198a2706e78929ad1f19ede9c35dcd2debd4804a113355e182796fe7631029
---

# Wire tail-outlier through the canonical runner and package command

> **Why:** The workload and deterministic watcher now exist, but the canonical runner rejects tail_outlier and the public package command still aborts with a stale message before it can reach the Engine assertion.

## Goal

Complete the offline routing path from the public package command to the canonical tail_outlier workload while preserving explicit failure checks and leaving the live Spark/OTLP/ClickHouse proof unexecuted.

## Context

This is package wiring only. The Engine watcher is already accepted locally. Tests may inspect and dry-run routing, but must not start containers, Spark, ClickHouse, Collector, or external services. Runtime success remains separately authorized.

## Behavior

- **B-1** — GIVEN the canonical E2E script WHEN tail_outlier is selected THEN parameter validation accepts it and the workload map resolves it to tail_outlier.py
- **B-2** — GIVEN the public tail-outlier action WHEN non-DryRun execution reaches Invoke-TailOutlierGate THEN it no longer stops at the stale unconditional throw and invokes the canonical runner with Scenario tail_outlier
- **B-3** — GIVEN missing job identity, nonzero Engine exit, or absent tail_outlier_watcher output WHEN the gate evaluates the result THEN it remains fail closed with an explicit error
- **B-4** — GIVEN a successful live result in a separately authorized environment WHEN the gate completes THEN it emits APEX_TAIL_OUTLIER_GATE=passed and llm_calls=0
- **B-5** — GIVEN offline package validation WHEN tests run THEN they prove workload presence, allowlist/mapping, stale-block removal and watcher assertion without claiming runtime execution

## Success Criteria

```bash
# eval_1: focused offline package wiring tests discriminate the complete tail-outlier route
eval_1() {
  ( cd engine && uv run --extra dev pytest -q "../tests/test_tail_outlier_package.py::test_canonical_runner_accepts_and_maps_tail_outlier" "../tests/test_tail_outlier_package.py::test_public_gate_reaches_canonical_tail_outlier" "../tests/test_tail_outlier_package.py::test_public_gate_remains_fail_closed_and_llm_free" -p no:warnings )
}

# eval_2: complete root gate remains green without running external services
eval_2() {
  ( cd engine && uv run --extra dev pytest ../tests -q -p no:warnings )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "focused offline package wiring tests discriminate the complete tail-outlier route"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3, B-4, B-5]
    terminal: true
    expected_duration_sec: 45
  - id: eval_2
    description: "complete root gate remains green without running external services"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3, B-5]
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

- Running the canonical workload, Docker, Spark, Collector or ClickHouse during offline acceptance.
- Removing negative checks for job identity, Engine exit or watcher output.
- Treating DryRun or source assertions as runtime proof.
- Editing Engine watcher semantics in this leaf.
- Publishing, pushing, opening a PR or commenting on GitHub.

## Do-Not-Touch

- `engine/src`
- `engine/tests`
- `jar`
- `collect`
- `infra`
- `serve`
- `front`

## Open Questions

(none — this task is fully specified)
