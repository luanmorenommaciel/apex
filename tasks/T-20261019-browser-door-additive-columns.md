---
id: T-20261019-browser-door-additive-columns
title: "Let the browser door read a findings table without confidence_score"
status: in-progress
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-queries-dead-statement, T-20261019-fixtures-lazy-chunk]
supersedes: (none)
touches_paths: [front/src/data/queries.ts, front/src/data/repository.ts]
creates_paths: [front/src/data/findingsProjection.test.ts]
source_note: "front/src/data/queries.ts FINDINGS (projects and orders by confidence_score unconditionally), serve/src/apex_mcp/ch.py lines 80-96 and 552-566 (_FINDINGS_ADDITIVE, system.columns probe, toFloat64(0) fallback), front/contract/01-readonly-user.sql (SELECT and SHOW TABLES on apex.*)"
created: "2026-10-19T00:00:00Z"
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

# Let the browser door read a findings table without confidence_score

> **Why:** confidence_score is a v0.2 additive column of apex.findings. The API probes system.columns and projects toFloat64(0) when a cluster predates it; the browser door sends FINDINGS as written and the query fails with an unknown-identifier error, so the same deployment works through one door and breaks through the other.

## Goal

ClickHouseRepository probes the findings columns once per instance and sends the full FINDINGS when confidence_score exists, or a second exported statement that projects toFloat64(0) AS confidence_score and keeps the same output columns and order when it does not; the probe falling over leaves the full statement in place so the real error still surfaces.

## Context

queries.ts gains export const FINDINGS_COLUMNS (SELECT name FROM system.columns WHERE database = currentDatabase() AND table = 'findings') and export const FINDINGS_WITHOUT_SCORE, which is FINDINGS with the column replaced by toFloat64(0) AS confidence_score and the ORDER BY kept, so the row shape the console renders is identical to the API's fallback. FINDINGS itself is not edited - serve/tests/test_console_reads.py reads its text. The two new exports must be consumed from repository.ts, or the consumer test from T-20261019-queries-dead-statement fails if that leaf has landed. apex_ro sees its own tables in system.columns because any privilege on a table implies SHOW on it. ClickHouseRepository caches the probe result in a private promise, like ReadStore.findings_columns() does in ch.py. The test stubs fetch, like httpRepository.test.ts does, answering the probe with and without the column and asserting which statement the next findings() call sends; a third case rejects the probe and asserts FINDINGS is sent and the findings error is the one reported.

## Behavior

- **B-1** — GIVEN a store whose findings table has confidence_score WHEN findings() is called THEN FINDINGS is sent, after one probe per repository instance
- **B-2** — GIVEN a store whose findings table lacks it WHEN findings() is called THEN FINDINGS_WITHOUT_SCORE is sent and rows carry confidence_score 0
- **B-3** — GIVEN a probe that fails WHEN findings() is called THEN FINDINGS is sent and its own error, not the probe's, is what the caller sees
- **B-4** — GIVEN serve's static parity tests WHEN they run THEN FINDINGS is unchanged and still found

## Success Criteria

```bash
# eval_1: the projection tests pass
eval_1() {
  ( cd front && npx vitest --run src/data/findingsProjection.test.ts )
}

# eval_2: serve still reads FINDINGS as written
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
    description: "the projection tests pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "serve still reads FINDINGS as written"
    runnable: bash
    check_type: deterministic
    verifies: [B-4]
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

- Editing the text of FINDINGS - serve pins it.
- Catching the findings error when the probe fails; the fallback is the statement, not silence.
- Probing on every call.

## Do-Not-Touch

- `serve`
- `front/src/screens`
- `front/src/contract`

## Open Questions

(none — this task is fully specified)
