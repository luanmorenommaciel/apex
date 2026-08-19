---
id: T-20260819-runs-injection-hardening
title: "Harden run discovery against a hostile app_name"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260819-runs-read-layer]
touches_paths: [serve/tests/test_injection_hardening.py]
creates_paths: []
source_note: "docs/lanes/SERVE-LEGS.md"
created: "2026-08-19T00:00:00Z"
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
signed_off_at: 2026-08-19T17:51:57Z
accepted: true
accepted_by: sidymar
accepted_at: 2026-08-19T17:52:09Z
signed_off_sig: hmac-sha256-v2:5153084e:7a97b0e297c4b38e742bb960506aa173085dd1d174083f4dd69cbac83a32735d
---

# Harden run discovery against a hostile app_name

> **Why:** app_name is set by the observed Spark job and now reaches a WHERE clause and a returned payload - a new user-influenced path into both SQL and the model's context.

## Goal

Prove a hostile app_name neither reaches SQL nor rides out as instructions.

## Context

The existing suite patches subprocess, os and write-mode open to fail if called. Extend that discipline to the discovery path rather than writing a parallel harness.

## Behavior

- **B-1** — GIVEN an app_name carrying an instruction-override payload WHEN it is returned by list_runs THEN the text appears only in typed data fields, verbatim, and in no string Apex generates
- **B-2** — GIVEN that same payload WHEN run discovery executes THEN no subprocess, os or write-mode open call is made
- **B-3** — GIVEN an app_name containing a SQL fragment WHEN it reaches the store THEN it binds as a parameter and returns zero rows

## Success Criteria

```bash
# eval_1: the discovery hardening tests exist and pass
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_injection_hardening.py::test_hostile_app_name_stays_data" "tests/test_injection_hardening.py::test_hostile_app_name_triggers_no_action" )
}

# eval_2: the full disclosure and injection suite stays green
eval_2() {
  ( cd serve && uv run --extra dev pytest tests/test_injection_hardening.py )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the discovery hardening tests exist and pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "the full disclosure and injection suite stays green"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
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

- Sanitising or escaping app_name instead of binding it; escaping is what binding exists to replace.
- Asserting on the payload's exact wording rather than on where it is allowed to appear.

## Do-Not-Touch

- `serve/src/apex_mcp`

## Open Questions

(none — this task is fully specified)
