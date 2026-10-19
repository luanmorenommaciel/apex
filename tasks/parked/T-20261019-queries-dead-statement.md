---
id: T-20261019-queries-dead-statement
title: "Remove PLAN_MEMORY and pin that every statement has a consumer"
status: parked
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [front/src/data/queries.ts]
creates_paths: [front/src/data/queries.consumed.test.ts]
source_note: "front/src/data/queries.ts lines 260-266 (PLAN_MEMORY, no importer in front/src or serve), serve/tests/test_console_parity_gate.py line 39 (the eleven statements the gate reads, PLAN_MEMORY not among them)"
created: "2026-10-19T00:00:00Z"
tags: []
owner: (none)
priority: P2
severity: feature
due_date: (none)
precondition: (none)
blocked_reason: "superseded by D-api-only on 2026-10-19: queries.ts no longer exists, so a dead statement cannot exist either; its evals cannot run at HEAD and the leaf is not accepted"
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

# Remove PLAN_MEMORY and pin that every statement has a consumer

> **Why:** queries.ts exports PLAN_MEMORY, which nothing in the console or the serve lane runs, and whose shape is wrong on its face - it joins plan_transitions to spark_events on job_id alone and groups by a column that is ambiguous between the two. A statement nobody executes is a statement nobody tests, and the serve parity gate would run it against the live store if it were ever listed.

## Goal

PLAN_MEMORY is gone, a test reads queries.ts and repository.ts and fails when an exported statement has no consumer, and serve's static parity tests still pass.

## Context

The test is text-level like serve's - it collects every export const NAME in queries.ts and asserts repository.ts references Q.NAME - so a future dead statement fails here rather than silently shipping. The serve tests read FINDINGS, PLAN_TRANSITIONS and FIX_VERIFICATIONS from queries.ts verbatim and the gate reads eleven named exports; none is touched. eval_2 runs those serve tests with uv the way CI does; if uv resolves a Python the serve lane cannot use, pin UV_PYTHON=3.12 as the memory on this repo notes.

## Behavior

- **B-1** — GIVEN queries.ts after the change WHEN it is searched THEN PLAN_MEMORY is absent
- **B-2** — GIVEN every export const in queries.ts WHEN the consumer test runs THEN each is referenced from repository.ts, and the test fails when one is not
- **B-3** — GIVEN serve's static parity tests WHEN they run THEN they still find FINDINGS, PLAN_TRANSITIONS, FIX_VERIFICATIONS and the gate's eleven statements

## Success Criteria

```bash
# eval_1: the statement is gone and every remaining one is consumed
eval_1() {
  ( cd front && ! grep -q "PLAN_MEMORY" src/data/queries.ts && npx vitest --run src/data/queries.consumed.test.ts )
}

# eval_2: serve still reads what it reads from queries.ts
eval_2() {
  ( cd serve && uv run --extra dev pytest tests/test_console_reads.py tests/test_projection_parity.py tests/test_console_parity_gate.py -q -p no:warnings )
}

# eval_3: the whole front gate stays green
eval_3() {
  ( cd front && npm run typecheck && npm run lint && npm test -- --run )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the statement is gone and every remaining one is consumed"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 20
  - id: eval_2
    description: "serve still reads what it reads from queries.ts"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
    terminal: true
    expected_duration_sec: 60
  - id: eval_3
    description: "the whole front gate stays green"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
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
eval_1 && eval_2 && eval_3
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Editing any other statement in queries.ts - serve pins their text.
- Moving SQL between lanes; that is D-console-sql-home.

## Do-Not-Touch

- `serve`
- `front/src/data/repository.ts`
- `front/src/screens`

## Open Questions

(none — this task is fully specified)
