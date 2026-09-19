---
id: T-20260918-pwsh-command-aware-coverage
title: "Make package dry-run coverage explicit and command-aware"
status: done
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [.github/workflows/ci.yml, scripts/apex.ps1, tests/test_apex_initial_package.py]
creates_paths: [tasks/.plans/issue124-pwsh-command-aware.yaml]
source_note: "https://github.com/luanmorenommaciel/apex/issues/124"
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
signed_off_at: 2026-09-19T00:41:51Z
accepted: true
accepted_by: augustosilva
accepted_at: 2026-09-19T00:42:03Z
signed_off_sig: hmac-sha256-v3:6af918b1:1d3dae8ea2c3b52fb38b3603073c2d59a6162596a5593dc27655d61762969c73
accepted_tier: 1
accepted_attempt_id: 085a2807-0b09-4269-adda-89eac4f08595
accepted_authorization_ref: hmac-sha256-v3:6af918b1:1d3dae8ea2c3b52fb38b3603073c2d59a6162596a5593dc27655d61762969c73
acceptance_record_digest: sha256:4fcdf672b99626c19f52c5e1d196b58210d79552a80d6328e7561c9bcc03b49a
---

# Make package dry-run coverage explicit and command-aware

> **Why:** The current root gate executes PowerShell, but the workflow relies on the runner image and the generic DryRun exits before dispatch, so a named action can look covered while its real handler is unreachable.

## Goal

Explicitly verify PowerShell 7 in CI and make DryRun report the same resolved handler that real execution would invoke, without performing mutations or external calls.

## Context

This is offline package-contract work only. It must not repair the tail-outlier watcher or scenario, start containers, use secrets, publish a PR, or claim runtime proof. The latest main root gate had 64 passed and one macOS-only skip; this task is prevention and coverage, not a claim that current CI skipped PowerShell.

## Behavior

- **B-1** — GIVEN the required root-gate CI job WHEN package tests start THEN PowerShell 7 is explicitly resolved and its version is logged, and absence or an older major version fails the job
- **B-2** — GIVEN pwsh is absent from PATH WHEN the package contract test requests it THEN the test fails with a dependency error instead of producing eight skips
- **B-3** — GIVEN any declared package action and DryRun WHEN the command is executed THEN it resolves and reports the exact handler for that action while preserving mutations=0 and external_calls=0
- **B-4** — GIVEN normal non-DryRun execution WHEN an action is selected THEN execution uses the same resolved action plan that DryRun reported, so the two mappings cannot drift
- **B-5** — GIVEN tail-outlier DryRun WHEN the command returns successfully THEN it proves routing to Invoke-TailOutlierGate but does not claim that the still-blocked live gate works

## Success Criteria

```bash
# eval_1: package contract tests cover dependency failure, all actions, handler identity and non-mutation
eval_1() {
  ( cd engine && uv run --extra dev pytest ../tests/test_apex_initial_package.py -q -p no:warnings )
}

# eval_2: the complete root gate remains green
eval_2() {
  ( cd engine && uv run --extra dev pytest ../tests -q -p no:warnings )
}

# eval_3: CI explicitly verifies PowerShell 7 before the root tests
eval_3() {
  ( grep -nE 'PowerShell 7|PSVersionTable|pwsh' .github/workflows/ci.yml )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "package contract tests cover dependency failure, all actions, handler identity and non-mutation"
    runnable: bash
    check_type: deterministic
    verifies: [B-2, B-3, B-4, B-5]
    terminal: true
    expected_duration_sec: 45
  - id: eval_2
    description: "the complete root gate remains green"
    runnable: bash
    check_type: deterministic
    verifies: [B-2, B-3, B-4]
    terminal: true
    expected_duration_sec: 90
  - id: eval_3
    description: "CI explicitly verifies PowerShell 7 before the root tests"
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
eval_1 && eval_2 && eval_3
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Treating generic DryRun success as evidence that the live action body works.
- Starting Docker, Spark, ClickHouse or any external service from a routing test.
- Installing a legacy Windows PowerShell fallback.
- Fixing issue #123 inside this leaf.
- Relaxing the eight-action equality or silently skipping a missing pwsh dependency.

## Do-Not-Touch

- `engine/src`
- `dev/jobs`
- `dev/scripts`
- `front`
- `serve`

## Open Questions

(none — this task is fully specified)
