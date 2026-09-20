---
id: T-20260920-readstore-console-queries
title: "Move the console's six remaining queries into ReadStore"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
touches_paths: [serve/src/apex_mcp/ch.py, serve/tests/test_ch.py]
creates_paths: []
source_note: "front/src/data/queries.ts"
created: "2026-09-20T00:00:00Z"
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
signed_off_at: 2026-09-20T17:24:39Z
accepted: true
accepted_by: sidymar
accepted_at: 2026-09-20T17:29:12Z
signed_off_sig: hmac-sha256-v2:5153084e:b5571d2807e334f9487ed02f72f7339c41814f8d1a449d469379187397dc0ad4
---

# Move the console's six remaining queries into ReadStore

> **Why:** Six of the console's queries exist only as SQL in the browser bundle - RUN_ONE, JOB_CONF, RUNS_SHARING_SHAPE, PLAN_SHAPES, PLAN_SAMPLE, SHAPE_RUNS. Until they have a server-side home, the console cannot leave its direct ClickHouse connection no matter what routes exist.

## Goal

ReadStore gains run, job_conf, baseline_candidates, plan_shapes, plan_sample and shape_runs, parameter-bound like every method already there.

## Context

These are ports, not redesigns. The console's SQL is the reference behaviour; a port that returns different rows is a regression the console will surface as changed numbers on screen. Every existing ReadStore method binds parameters server-side - these must too.

## Behavior

- **B-1** — GIVEN a job_id that exists WHEN ReadStore.run is called THEN it returns the same single rollup row the console's RUN_ONE returns, and None for an unknown job_id rather than a synthesised zero
- **B-2** — GIVEN a job_id WHEN ReadStore.job_conf is called THEN it returns the job's configuration rows, empty when the jar emitted no job_conf
- **B-3** — GIVEN a plan fingerprint WHEN ReadStore.shape_runs and ReadStore.plan_sample are called THEN they return that shape's runs oldest-first and its redacted exemplar, and plan_sample returns None for an unindexed shape rather than an empty string
- **B-4** — GIVEN any of the six methods WHEN a caller passes a value containing SQL syntax THEN it is bound as a parameter and never interpolated, consistent with the existing methods
- **B-5** — GIVEN the contract v0.3 memory tables are absent WHEN plan_shapes or shape_runs is called THEN the absence is reported the way memory_tables_present already reports it, not as an empty history

## Success Criteria

```bash
# eval_1: the six ports return the console's shapes
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_ch.py::test_run_returns_one_rollup_row" "tests/test_ch.py::test_run_returns_none_for_unknown_job" "tests/test_ch.py::test_job_conf_returns_rows_and_empty_when_absent" "tests/test_ch.py::test_shape_runs_and_plan_sample" )
}

# eval_2: parameters are bound and missing memory tables are reported honestly
eval_2() {
  ( cd serve && uv run --extra dev pytest "tests/test_ch.py::test_new_methods_bind_parameters" "tests/test_ch.py::test_plan_shapes_reports_absent_memory_tables" )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the six ports return the console's shapes"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 90
  - id: eval_2
    description: "parameters are bound and missing memory tables are reported honestly"
    runnable: bash
    check_type: deterministic
    verifies: [B-4, B-5]
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

- Rewriting the SQL while porting it; the console's rendered numbers are the acceptance criterion.
- String-interpolating a fingerprint or job_id into the query text.
- Returning an empty list when the memory tables are missing, which reads as "no history" instead of "no table".

## Do-Not-Touch

- `front/src/data/queries.ts`
- `serve/src/apex_mcp/server.py`

## Open Questions

(none — this task is fully specified)
