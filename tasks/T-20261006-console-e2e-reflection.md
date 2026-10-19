---
id: T-20261006-console-e2e-reflection
title: "Prove one real job from the Spark plugin to every console screen"
status: in-progress
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [serve/RUNBOOK.md, serve/VALIDATION.md, CHANGELOG.md, docs/e2e/README.md]
creates_paths: [tests/e2e/console_reflection.sh, front/src/e2e/console.live.test.tsx]
source_note: "docs/e2e/README.md"
created: "2026-10-06T00:00:00Z"
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

# Prove one real job from the Spark plugin to every console screen

> **Why:** Three end-to-end entry points exist and none reaches the console. tests/e2e/run.sh stops at the store, scripts/e2e_six_lanes.py stops at the MCP, and every console test stubs a door. Nothing had ever shown a job going Spark - plugin - OTLP - ClickHouse - engine - memory - API - screen, so nothing could say whether what a person reads on a screen is what the job did.

## Goal

A fourth entry point that takes a job already in the store, runs engine and memory on it exactly as an operator would, starts apex-api over the same store, proves the console's rows through both doors, then mounts the REAL App against that API and reads every screen for the job - refusing NaN, undefined, [object Object], the console's own failure notices, and requiring the counts a screen shows to be the counts the API returned.

## Context

The live test is skipped unless APEX_E2E_API_URL, APEX_E2E_API_TOKEN and APEX_E2E_JOB_ID are set - skipped and reported, never passed. It mounts App inside RepositoryProvider and a MemoryRouter with runtimeConfig mocked to the live API, so the HttpRepository under test is the real one over node's fetch. APEX_E2E_DUMP=<file> writes what each screen showed, because the invariants catch what must never appear and a person still has to read what does. The orchestrator kills the API by its listening port, not by the subshell's pid, because `uv run` leaves uvicorn behind - the first version left an orphan on 8099. It warns when a job carries no apex.job_conf row, naming what that costs on screen and the most likely cause, a dev image older than jar/src. Recorded 2026-10-06 against the infra stack on three jobs - two generated in the session, one from July - all green, and the generated runs are what found the two leaves below and the stale image.

## Behavior

- **B-1** — GIVEN a job_id with spark_events rows in infra's ClickHouse WHEN the orchestrator runs THEN engine writes deterministic findings with llm_calls 0, memory indexes the job, apex-api answers health with store ok, the parity gate passes on that job, and the live console test passes - one PASS line per step and a non-zero exit on any FAIL
- **B-2** — GIVEN the live variables are absent WHEN the front suite runs THEN the live test file is reported skipped and the suite still passes
- **B-3** — GIVEN a job with no apex.job_conf row WHEN the orchestrator runs THEN it prints a WARN naming the consequence on screen and the likely cause, and continues
- **B-4** — GIVEN the live test against a running API WHEN each screen settles THEN no screen contains NaN, undefined, [object Object], Infinity, APEX_API_TOKEN, query failed, could not be reached or NO RUN ROW, and /runs/:job shows the API's stage and finding counts

## Success Criteria

```bash
# eval_1: the live file is skipped, not failed, without a live API; types and lint hold
eval_1() {
  ( cd front && npm run typecheck && npm run lint && npx vitest run src/e2e/console.live.test.tsx 2>&1 | grep "skipped" >/dev/null )
}

# eval_2: the orchestrator is sound shell and refuses to run without a job id
eval_2() {
  ( bash -n tests/e2e/console_reflection.sh && ! tests/e2e/console_reflection.sh >/dev/null 2>&1 )
}

# eval_3: LIVE - needs infra up and a job in the store - the whole chain on one job
eval_3() {
  ( tests/e2e/console_reflection.sh --latest )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the live file is skipped, not failed, without a live API; types and lint hold"
    runnable: bash
    check_type: deterministic
    verifies: [B-2]
    terminal: true
    expected_duration_sec: 180
  - id: eval_2
    description: "the orchestrator is sound shell and refuses to run without a job id"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 10
  - id: eval_3
    description: "LIVE - needs infra up and a job in the store - the whole chain on one job"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-3, B-4]
    terminal: true
    expected_duration_sec: 300
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

- Stubbing any door in the live test; the point is that none is.
- Passing when the live variables are absent; a skip is reported as a skip.
- Killing the API by the subshell pid; uvicorn survives and the next run finds the port taken.

## Do-Not-Touch

- `front/src/screens/`
- `front/src/data/`
- `serve/src/`

## Open Questions

(none — this task is fully specified)
