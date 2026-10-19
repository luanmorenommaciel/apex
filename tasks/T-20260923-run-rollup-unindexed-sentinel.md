---
id: T-20260923-run-rollup-unindexed-sentinel
title: "Report an unindexed run as null, not zero, in both rollups"
status: in-progress
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260923-console-findings-transitions-projection]
supersedes: (none)
touches_paths: [serve/src/apex_mcp/ch.py, serve/tests/test_ch.py, front/src/data/queries.ts, front/src/data/queries.test.ts, serve/RUNBOOK.md]
creates_paths: []
source_note: "serve/RUNBOOK.md"
created: "2026-09-23T00:00:00Z"
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

# Report an unindexed run as null, not zero, in both rollups

> **Why:** RUNBOOK's Known gaps records it and nothing fixes it - a run the memory lane has not indexed reports task_time_ms 0, not null. The rollup LEFT JOINs run_outcomes and writes ifNull(s.task_time_ms, -1), but ClickHouse fills a missed join's non-Nullable columns with DEFAULTS, not NULL (join_use_nulls is 0), so the ifNull never fires and -1 - the sentinel repository.ts turns into null - is never produced. The console then renders a measured zero for a number nobody measured, and the same miss turns shaped_stage_count into 0 instead of null and config_source into the enum's first value instead of 'unknown'. The bug is in the console's SQL and was carried into ch.py verbatim by the port, so both copies are wrong the same way.

## Goal

Both rollups mark a missed shapes join with a sentinel column and derive -1, '' and 'unknown' from it, so task_time_ms, shaped_stage_count, plan_fingerprint and config_source say "not indexed" for a run the memory lane never reached; a test on each side pins it; a third test pins the two copies to each other; the RUNBOOK gap is removed.

## Context

SETTINGS join_use_nulls = 1 is the obvious fix and is NOT available - front/contract/01-readonly-user.sql creates apex_ro with readonly = 1, and ClickHouse refuses query-level settings from a readonly = 1 user, so the browser copy would fail outright; it would also change the f join's semantics for no reason. The settings-free form is a column the shapes CTE always emits and a miss cannot - proposed as `1 AS indexed` - read as if(s.indexed = 1, s.task_time_ms, -1) and the same for shaped_stage_count, plan_fingerprint and config_source. The name is a proposed choice, open for review; the mechanism is not. repository.ts already maps -1 to null through notIndexed() and is not touched. The two copies must stay one rollup on two hosts - test_run_rollup_matches_the_console_sql reads runRollup() out of queries.ts and compares it, normalised for whitespace, the apex. qualification and the parameter names, against _run_rollup_sql; test_api_resources.py already reads repository.ts from serve, so the precedent exists. What no offline test can prove is the ClickHouse fill behaviour itself - the acceptor runs RUN_ONE against the infra stack for a job that has spark_events rows and no run_outcomes row and reads -1, which the RUNBOOK gap entry currently says comes back as 0. This leaf shares ch.py, test_ch.py and RUNBOOK.md with T-20260923-console-findings-transitions-projection; the depends_on is a WRITE-ORDER dependency, not an outcome one - nothing here reads that leaf's result, the two must simply not edit the same files at once.

## Behavior

- **B-1** — GIVEN a job with spark_events rows and no run_outcomes row WHEN RUN_ONE or RUN_LIST runs on either copy THEN task_time_ms is -1, shaped_stage_count is -1, plan_fingerprint is '' and config_source is 'unknown' - never 0, never the enum's first value
- **B-2** — GIVEN a job the memory lane indexed WHEN the rollups run THEN every value is what it is today
- **B-3** — GIVEN the two rollup copies WHEN they are compared normalised for the apex. qualification and parameter names THEN they are the same statement
- **B-4** — GIVEN the browser copy WHEN it is issued as apex_ro THEN it carries no SETTINGS clause, because readonly = 1 refuses one

## Success Criteria

```bash
# eval_1: the serve copy marks a missed join and carries no settings
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_ch.py::test_run_rollup_marks_a_missed_shapes_join" "tests/test_ch.py::test_run_rollup_carries_no_settings_clause" )
}

# eval_2: the browser copy marks a missed join and carries no settings
eval_2() {
  ( cd front && npm run test -- --run src/data/queries.test.ts -t "unindexed" )
}

# eval_3: one rollup, two hosts
eval_3() {
  ( cd serve && uv run --extra dev pytest "tests/test_ch.py::test_run_rollup_matches_the_console_sql" )
}

# eval_4: the indexed path is untouched and the gap entry is gone
eval_4() {
  ( cd serve && uv run --extra dev pytest "tests/test_ch.py::test_run_returns_one_rollup_row" "tests/test_ch.py::test_run_list_returns_the_console_rollup" && ! grep -q "has not indexed reports" RUNBOOK.md )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the serve copy marks a missed join and carries no settings"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-4]
    terminal: true
    expected_duration_sec: 60
  - id: eval_2
    description: "the browser copy marks a missed join and carries no settings"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-4]
    terminal: true
    expected_duration_sec: 120
  - id: eval_3
    description: "one rollup, two hosts"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
    terminal: true
    expected_duration_sec: 60
  - id: eval_4
    description: "the indexed path is untouched and the gap entry is gone"
    runnable: bash
    check_type: deterministic
    verifies: [B-2]
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
eval_1 && eval_2 && eval_3 && eval_4
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- SETTINGS join_use_nulls = 1; apex_ro is readonly = 1 and the browser copy would stop working.
- Fixing ch.py and leaving queries.ts, or the reverse; the clickhouse and http data sources would then disagree about whether a run was indexed.
- Testing the miss with s.job_id = '' instead of a named sentinel; it works and says nothing about why.
- Changing notIndexed() in repository.ts; the mapper is right, the SQL never gave it the sentinel.

## Do-Not-Touch

- `front/src/data/repository.ts`
- `front/src/screens/`
- `serve/src/apex_api/`

## Open Questions

(none — this task is fully specified)
