---
id: T-20260919-pwsh-package-audit-hardening
title: "Harden PowerShell package contract regression coverage"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [tests/test_apex_initial_package.py]
creates_paths: []
source_note: "https://github.com/luanmorenommaciel/apex/issues/124"
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
signed_off_at: 2026-09-19T19:06:42Z
accepted: true
accepted_by: augustosilva
accepted_at: 2026-09-19T21:08:23Z
signed_off_sig: hmac-sha256-v3:6af918b1:9a9b780a01402504cb23dd179ab235387ee0bc950d704382a1f9587fcb466e46
accepted_tier: 1
accepted_attempt_id: 629f10d6-e49b-4c59-809f-ce6b51712e10
accepted_authorization_ref: hmac-sha256-v3:6af918b1:9a9b780a01402504cb23dd179ab235387ee0bc950d704382a1f9587fcb466e46
acceptance_record_digest: sha256:871ae4e6c14776c16ccbe356d6c999328dbb43b7f40bcb922f4f1dc9bb7ef9e4
---

# Harden PowerShell package contract regression coverage

> **Why:** Independent review found that the current DryRun test can accept a prefix-matched wrong handler, omits help/ValidateSet coverage, and proves non-mutation only through a printed string.

## Goal

Make the package tests prove exact DryRun action identity, safe help/ValidateSet behavior, and the absence of an .apex runtime directory without changing production PowerShell or CI behavior.

## Context

This is test-only audit remediation. It must remain offline and must not execute a product gate, external service, Docker, Spark, ClickHouse, or tail-outlier runtime path.

## Behavior

- **B-1** — GIVEN each supported non-help action and DryRun WHEN package tests execute it THEN they match the complete reported summary rather than a handler substring
- **B-2** — GIVEN help and an invalid action WHEN PowerShell dispatch runs without DryRun THEN help executes its safe handler and an invalid action is rejected by ValidateSet without creating runtime state
- **B-3** — GIVEN a clean candidate worktree with no .apex directory WHEN representative DryRun commands run THEN .apex remains absent as well as reporting zero mutations and external calls

## Success Criteria

```bash
# eval_1: focused PowerShell package contract tests pass
eval_1() {
  ( cd engine && uv run --extra dev pytest ../tests/test_apex_initial_package.py -q -p no:warnings )
}

# eval_2: complete root offline test gate remains green
eval_2() {
  ( cd engine && uv run --extra dev pytest ../tests -q -p no:warnings )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "focused PowerShell package contract tests pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 60
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

- Editing scripts/apex.ps1 or .github/workflows/ci.yml unless a test proves a real production defect.
- Deleting or modifying a pre-existing .apex directory to arrange a test precondition.
- Starting Docker, Spark, ClickHouse, or a tail-outlier live path.

## Do-Not-Touch

- `scripts/apex.ps1`
- `.github/workflows/ci.yml`
- `engine/src`
- `dev`
- `front`
- `serve`
- `infra`

## Open Questions

(none — this task is fully specified)
