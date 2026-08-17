---
id: T-20260817-surface-defaulted-vars
title: "Surface defaulted environment variables in ServerStatus"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260817-serverstatus-model, T-20260817-resolve-settings-extract, T-20260817-status-assembler, T-20260817-status-degraded-path, T-20260817-startup-stderr-banner]
touches_paths: [serve/src/apex_mcp/diagnose.py, serve/src/apex_mcp/server.py, serve/tests/test_status.py]
creates_paths: []
source_note: "docs/lanes/L1_tasks.md"
created: "2026-08-17T00:00:00Z"
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

# Surface defaulted environment variables in ServerStatus

> **Why:** The commonest way Apex looks broken is a default endpoint the user never chose, and every variable has a working local default, so the failure is silent.

## Goal

Let apex_status report which CLICKHOUSE_ variables were never set, by name only.

## Context

Sized M rather than S because the write surface is three paths - the assembler, the tool body and the tests. Reclassified up rather than split, since it is one coherent change.

## Behavior

- **B-1** — GIVEN no CLICKHOUSE_ variables set WHEN apex_status() is called THEN using_defaults lists all six variable names
- **B-2** — GIVEN all six set WHEN apex_status() is called THEN using_defaults is empty
- **B-3** — GIVEN using_defaults is non-empty and the store is empty WHEN the result is read THEN remediation connects the two as a probable wrong-endpoint case
- **B-4** — GIVEN any response WHEN it is serialized THEN using_defaults contains variable names only, never their values

## Success Criteria

```bash
# eval_1: the defaulted-variable tests exist and pass
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_status.py::test_using_defaults_lists_unset_variables" "tests/test_status.py::test_defaults_plus_empty_store_suggests_wrong_endpoint" )
}

# eval_2: the full suite stays green and no variable value is emitted
eval_2() {
  ( cd serve && CLICKHOUSE_PASSWORD='sentinel-pw-do-not-leak' uv run --extra dev pytest -q )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the defaulted-variable tests exist and pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-3]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "the full suite stays green and no variable value is emitted"
    runnable: bash
    check_type: deterministic
    verifies: [B-2, B-4]
    terminal: true
    expected_duration_sec: 60
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

- Including values; CLICKHOUSE_PASSWORD is one of the six names.
- Treating defaults as an error, since a local dev stack legitimately runs on all six.

## Do-Not-Touch

- `serve/src/apex_mcp/ch.py`

## Open Questions

(none — this task is fully specified)
