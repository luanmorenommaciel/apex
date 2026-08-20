---
id: T-20260820-verification-models
title: "Type the verification payload"
status: done
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
touches_paths: [serve/src/apex_mcp/models.py]
creates_paths: [serve/tests/test_verify_view.py]
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
signed_off: true
signed_off_by: sidymar
signed_off_at: 2026-08-20T14:43:14Z
accepted: true
accepted_by: sidymar
accepted_at: 2026-08-20T14:43:35Z
signed_off_sig: hmac-sha256-v2:5153084e:dc106c91b28064e397aa8267f3fb34e8c352dbec5253811fb0499de407f26fad
---

# Type the verification payload

> **Why:** FastMCP derives the tool's output schema from the return annotation, and a verdict about whether a fix works is exactly the payload a client must be able to reject if malformed.

## Goal

VerificationView and FixVerdict carrying prediction, measurement, safety and confidence.

## Context

predicted_delta_pct is SIGNED and negative means faster - a sign error here reports a regression as an improvement, so the field description must state the convention. measured_delta_pct is nullable because a prediction may never have been replayed.

## Behavior

- **B-1** — GIVEN a VerificationView WHEN constructed from a predicted-only row THEN it validates with measured_delta_pct None
- **B-2** — GIVEN the schema WHEN predicted_delta_pct is read THEN its description states the sign convention, negative meaning faster
- **B-3** — GIVEN a FixVerdict WHEN serialized THEN evidence and caveats are present, and untrusted_fields marks nothing Apex did not author

## Success Criteria

```bash
# eval_1: the verification model tests exist and pass
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_verify_view.py::test_predicted_only_row_validates" "tests/test_verify_view.py::test_sign_convention_is_documented" "tests/test_verify_view.py::test_verdict_carries_evidence_and_caveats" )
}

# eval_2: models.py still imports nothing from the package at runtime
eval_2() {
  ( cd serve && ! grep -nE '^from \.(ch|diagnose|server)|^from apex_mcp\.(ch|diagnose|server)' src/apex_mcp/models.py )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the verification model tests exist and pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "models.py still imports nothing from the package at runtime"
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
eval_1 && eval_2
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Storing the delta unsigned or flipping the sign for display; negative means faster, everywhere.
- Defaulting measured_delta_pct to 0, which would report an unreplayed prediction as a measured no-op.

## Do-Not-Touch

- `serve/src/apex_mcp/ch.py`
- `serve/src/apex_mcp/server.py`

## Open Questions

(none — this task is fully specified)
