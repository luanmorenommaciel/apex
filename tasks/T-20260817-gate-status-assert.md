---
id: T-20260817-gate-status-assert
title: "Assert apex_status in the live read-only gate"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260817-register-apex-status, T-20260817-surface-defaulted-vars]
touches_paths: [serve/tools/read_only_gate.py]
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

# Assert apex_status in the live read-only gate

> **Why:** A FakeClient returns whatever column set the test author typed, so only a real database can validate a tool that reports on schema conformance.

## Goal

Prove apex_status against live ClickHouse, cross-checked against the gate's own DESCRIBE.

## Context

The gate already performs an independent DESCRIBE at read_only_gate.py:73. Compare the tool's answer to that, not to the code under test.

## Behavior

- **B-1** — GIVEN a live store with the gate's seeded rows WHEN apex_status() is called THEN connected is True and run_count is greater than zero
- **B-2** — GIVEN the same call WHEN contract_tables is read THEN it agrees with the gate's independent DESCRIBE for all three tables
- **B-3** — GIVEN freshly seeded rows WHEN status reports THEN latest_ingest_age_seconds is small and positive
- **B-4** — GIVEN the gate completes WHEN it prints its JSON THEN a status block is included and the overall result is passed

## Success Criteria

```bash
# eval_1: the live gate passes and its status block agrees with DESCRIBE
eval_1() {
  ( cd serve && uv run python tools/read_only_gate.py > /tmp/gate.json && uv run python -c "import json; g=json.load(open('/tmp/gate.json')); assert g['status']=='passed', g; s=g['status_tool']; assert s['connected'] and s['run_count']>0, s; assert s['contract_tables']==g['describe_missing'], (s['contract_tables'], g['describe_missing'])" )
}

# eval_2: the reported ingest age is small and positive for freshly seeded rows
eval_2() {
  ( cd serve && uv run python -c "import json; s=json.load(open('/tmp/gate.json'))['status_tool']; a=s['latest_ingest_age_seconds']; assert a is not None and 0 <= a < 3600, a" )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the live gate passes and its status block agrees with DESCRIBE"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-4]
    terminal: true
    expected_duration_sec: 120
  - id: eval_2
    description: "the reported ingest age is small and positive for freshly seeded rows"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
    terminal: true
    expected_duration_sec: 10
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

- Building the expected column set from table_columns(), which compares the code under test to itself.
- Weakening the gate's guarantee that it deletes only its own fixture rows.
- Rewriting the existing conformance, argMax or injection assertions.

## Do-Not-Touch

- `serve/src/apex_mcp`

## Open Questions

(none — this task is fully specified)
