---
id: T-20260929-console-parity-live-gate
title: "Make RUNBOOK step 3 prove the console's rows against a live store"
status: in-progress
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260929-wire-timestamp-format]
supersedes: (none)
touches_paths: [serve/RUNBOOK.md]
creates_paths: [serve/tools/console_parity_gate.py, serve/tests/test_console_parity_gate.py]
source_note: "serve/RUNBOOK.md"
created: "2026-09-29T00:00:00Z"
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

# Make RUNBOOK step 3 prove the console's rows against a live store

> **Why:** RUNBOOK step 3 checks status codes - 200, 401, 404 - and status codes are what passed while the stages route returned the wrong projection, and would have kept passing for findings, transitions and an unindexed run. Every SQL statement the sweep wrote or changed was proven against fakes that return whatever rows they are handed; the projection lives in the SQL, and no test here has ever run it. The sweep's own report says so. What is owed is a check that a status code cannot satisfy.

## Goal

One command in RUNBOOK step 3 that, against the infra stack, issues each console statement twice - as the browser does, over ClickHouse HTTP as apex_ro, and through the API - and fails unless the two return the same rows; plus the four behaviours only a live store can show, each exercised on rows the gate seeds and removes itself, and each named with what it proves.

## Context

serve/tools/ already holds the live gates (read_only_gate.py, mcp_stdio_gate.py) and VALIDATION.md lists them; this is a third, same conventions - CLICKHOUSE_* from the environment, exit 0 or 1, one line per check. It reads the browser's statements out of front/src/data/queries.ts rather than restating them, so it compares what the console actually sends. It builds the API in-process with create_app() over a real ReadStore, so no port and no token are needed to run it; RUNBOOK step 3 keeps its curl walk for the deployed service. Rows are compared after the wire-timestamp normalisation, which is why this leaf depends on that one. The four live-only behaviours - (1) an unindexed run returns -1, -1, '' and 'unknown', the sentinel a fake cannot exercise because the fill is ClickHouse's; (2) both rollups execute as apex_ro, readonly = 1, proving no statement needs a setting and that if() found a common type for every branch; (3) findings come back confidence_score DESC when that order differs from ts ASC; (4) an execution re-planned three times is one transition row carrying the last update_seq. infra's seed.sh cannot exercise all four - it writes spark_events and one finding per skewed job, no transitions and no run_outcomes - so the gate does what read_only_gate.py already does in this directory and seeds its OWN disposable rows under job ids carrying a random suffix, then removes exactly those rows. Those writes are the fixture's; every code path under test, on both doors, issues SELECTs only. With --job-id the gate seeds nothing and compares the two paths on a run the store already holds, which is the mode for a store nobody may write to; there a behaviour the run's data cannot exercise prints NOT EXERCISED and does not count as passed - an unexercised check that prints green is how the nginx eval shipped.

## Behavior

- **B-1** — GIVEN a live store and a job_id WHEN the gate runs THEN for each console statement it prints one line comparing the browser path's rows with the API's, and exits non-zero if any differ
- **B-2** — GIVEN a store holding a run with no run_outcomes row WHEN the gate runs THEN it asserts task_time_ms -1, shaped_stage_count -1, plan_fingerprint '' and config_source 'unknown' on both paths
- **B-3** — GIVEN --job-id naming a run whose data cannot exercise a behaviour - no re-planned execution, a single finding, an indexed run WHEN the gate runs THEN that check prints NOT EXERCISED with the data that would exercise it, does not count as passed, and nothing is written to the store
- **B-4** — GIVEN the statements in front/src/data/queries.ts WHEN the gate extracts them THEN it issues them verbatim, with the console's parameter names, as apex_ro
- **B-5** — GIVEN RUNBOOK step 3 WHEN it is read THEN it names the command, the four live-only behaviours and what each proves, and how to bring the infra stack to a state that exercises all four

## Success Criteria

```bash
# eval_1: the gate extracts the console's statements and compares rows correctly, offline
eval_1() {
  ( cd serve && uv run --extra dev pytest tests/test_console_parity_gate.py )
}

# eval_2: the runbook names the gate and the behaviours it proves
eval_2() {
  ( cd serve && grep -q "console_parity_gate.py" RUNBOOK.md && grep -q "NOT EXERCISED" RUNBOOK.md && grep -q "apex_ro" RUNBOOK.md )
}

# eval_3: LIVE - needs the infra stack up (RUNBOOK steps 1 and 3) - the two paths return the same rows
eval_3() {
  ( cd serve && uv run python tools/console_parity_gate.py )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the gate extracts the console's statements and compares rows correctly, offline"
    runnable: bash
    check_type: deterministic
    verifies: [B-3, B-4]
    terminal: true
    expected_duration_sec: 60
  - id: eval_2
    description: "the runbook names the gate and the behaviours it proves"
    runnable: bash
    check_type: deterministic
    verifies: [B-5]
    terminal: true
    expected_duration_sec: 10
  - id: eval_3
    description: "LIVE - needs the infra stack up (RUNBOOK steps 1 and 3) - the two paths return the same rows"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 120
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

- Comparing status codes; they are what passed while three routes returned the wrong rows.
- Printing PASS for a check the store's data could not exercise.
- Restating the console's SQL in the gate; it must read queries.ts.
- Leaving a seeded row behind, or deleting by anything broader than the gate's own job ids.
- Seeding in --job-id mode; that mode exists for a store nobody may write to.

## Do-Not-Touch

- `serve/src/apex_mcp/`
- `front/src/`
- `infra/`

## Open Questions

(none — this task is fully specified)
