---
id: T-20260819-runs-gates
title: "Assert run discovery in both live gates"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260819-auto-baseline]
touches_paths: [serve/tools/read_only_gate.py, serve/tools/mcp_stdio_gate.py]
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
signed_off_at: 2026-08-19T19:07:20Z
accepted: true
accepted_by: sidymar
accepted_at: 2026-08-19T19:11:59Z
signed_off_sig: hmac-sha256-v2:5153084e:a8ba6935c5a49ace024f9f9598cedbb5578d3018d46fdfe80995d84dcc3c5292
---

# Assert run discovery in both live gates

> **Why:** A FakeClient returns whatever rows the test author typed; only a real database proves the aggregation, the binding and the partition-bounded scan.

## Goal

Prove list_runs and apex://runs against live ClickHouse and over real stdio.

## Context

The read-only gate seeds its own disposable rows and deletes only those; this addition must not weaken that.

## Behavior

- **B-1** — GIVEN the live gate's seeded runs WHEN list_runs is called THEN it returns them newest first with correct per-job aggregation
- **B-2** — GIVEN an app_name of a quote-bearing SQL fragment WHEN list_runs is called live THEN it binds and returns zero rows
- **B-3** — GIVEN the server spawned over stdio WHEN the official client lists tools and resources THEN it sees five tools and the apex://runs resource
- **B-4** — GIVEN the gate completes WHEN it prints its JSON THEN a runs block is included and the overall result is passed

## Success Criteria

```bash
# eval_1: the live gate passes and reports the runs block
eval_1() {
  ( cd serve && uv run python tools/read_only_gate.py > /tmp/l2gate.json && uv run python -c "import json; g=json.load(open('/tmp/l2gate.json')); assert g['status']=='passed', g; r=g['runs']; assert r['listed']>0 and r['hostile_app_name_rows']==0, r" )
}

# eval_2: the stdio gate sees five tools and the runs resource
eval_2() {
  ( cd serve && uv run python tools/mcp_stdio_gate.py )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the live gate passes and reports the runs block"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-4]
    terminal: true
    expected_duration_sec: 180
  - id: eval_2
    description: "the stdio gate sees five tools and the runs resource"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
    terminal: true
    expected_duration_sec: 180
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

- Building the expected run set from ReadStore.runs(); that is the code under test.
- Leaving fixture rows behind, or widening the gate's delete beyond its own rows.
- Softening the stdio assertion to contains rather than an exact surface.

## Do-Not-Touch

- `serve/src/apex_mcp`

## Open Questions

(none — this task is fully specified)
