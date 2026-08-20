---
id: T-20260820-suggest-fix-provenance
title: "Tell suggest_fix what verify already concluded"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260820-verify-fix-tool]
touches_paths: [serve/src/apex_mcp/diagnose.py, serve/tests/test_suggest_fix_safety.py]
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

# Tell suggest_fix what verify already concluded

> **Why:** suggest_fix currently proposes a diff with no idea that the same fix was already predicted, or measured, or refused as unsafe. Proposing a fix verify has refused is the worst output this lane can produce.

## Goal

A suggestion carries any existing verification for its finding, including a refusal.

## Context

This must not change what suggest_fix proposes - only what it discloses. applied stays Literal[False] and the tree stays untouched.

## Behavior

- **B-1** — GIVEN a finding with a prior verification WHEN suggest_fix runs THEN the suggestion reports the predicted range and any measurement
- **B-2** — GIVEN a finding whose fix verify refused as unsafe WHEN suggest_fix runs THEN the refusal is stated prominently and the suggestion does not present it as ready to apply
- **B-3** — GIVEN a finding with no verification WHEN suggest_fix runs THEN the output is unchanged from today
- **B-4** — GIVEN any path WHEN the suggestion is returned THEN applied is False, requires_human_approval is True and git status is unchanged

## Success Criteria

```bash
# eval_1: the provenance tests exist and pass
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_suggest_fix_safety.py::test_suggestion_reports_prior_verification" "tests/test_suggest_fix_safety.py::test_refused_fix_is_not_presented_as_ready" "tests/test_suggest_fix_safety.py::test_unverified_finding_output_is_unchanged" )
}

# eval_2: the never-applies guarantee is untouched
eval_2() {
  ( cd serve && uv run --extra dev pytest tests/test_suggest_fix_safety.py )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the provenance tests exist and pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "the never-applies guarantee is untouched"
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

- Changing which fix is proposed; this unit discloses, it does not decide.
- Weakening the Literal[False] on applied for any reason.

## Do-Not-Touch

- `serve/src/apex_mcp/server.py`
- `serve/src/apex_mcp/ch.py`

## Open Questions

(none — this task is fully specified)
