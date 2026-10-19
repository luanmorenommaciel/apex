---
id: T-20261019-refused-count-server
title: "Compute refused_count in the run rollup both doors run"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-auto-never-fixtures]
supersedes: (none)
touches_paths: [front/src/data/queries.ts, front/src/data/repository.ts, front/src/contract/rules.ts, front/src/screens/RunsScreen.tsx, front/README.md, serve/src/apex_mcp/ch.py, serve/tests/test_console_parity_gate.py, serve/tests/test_api_resources.py, serve/tests/test_ch.py]
creates_paths: [front/src/contract/refusedCount.test.ts]
source_note: "D-refused-count-home, option A; front/src/data/repository.ts (refused_count -1), front/src/contract/rules.ts assessStage() (rules 1, 6, 7), front/src/data/queries.ts runRollup, serve/src/apex_mcp/ch.py _run_rollup_sql, serve/tools/console_parity_gate.py"
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

# Compute refused_count in the run rollup both doors run

> **Why:** refused_count is -1 on every run in the list because it is derived from stage rows the list query does not read, so the runs screen shows a dash where the engine's restraint should be visible. The rule logic exists only in TypeScript.

## Goal

RUN_LIST and RUN_ONE carry a refused_count column computed by a CTE over spark_events and job_conf that encodes rules 1, 6 and 7 exactly as assessStage() does, serve's copy of the rollup carries the same CTE, the parity gate proves the two doors agree, and a front test runs assessStage() over the fixtures and asserts the SQL's arithmetic reproduces it for every recorded stage.

## Context

This is cross-lane - serve's ch.py and its tests change - and the commit says so. refused_count is the count of stages among the TAIL_SAMPLE loudest p99/p50 ratios that assessStage() reports as not reportable, the number RunDetail already shows as "N of the N loudest refused"; the CTE ranks the latest attempt of each stage by ratio, takes the top five, and counts those whose refusal is work_bound, cluster_width_unknown or not_a_distribution with the same arithmetic rules.ts uses - volume floor, slots from job_conf, (n-1)/(s-1) bar - so a stage with no job_conf slots counts as cluster_width_unknown, refused, not unknown. The sentinel stays -1 for a run with no stage rows. The refusedCount test evaluates the same arithmetic in TypeScript over fx.stagesByJob and fx.jobConfByJob and compares with assessStage(); the live parity gate is the proof the SQL itself agrees, run per the disposable-ClickHouse recipe before accepting.

## Behavior

- **B-1** — GIVEN the fixtures' stages and conf WHEN assessStage() counts refusals among the five loudest and the CTE's arithmetic is evaluated over the same rows THEN the counts are equal per run
- **B-2** — GIVEN RUN_LIST and RUN_ONE in front and serve WHEN serve's static tests and the parity gate's statement reader run THEN refused_count is present in both rollups and the texts agree
- **B-3** — GIVEN the runs screen WHEN it renders a run with stage rows THEN refused_count is a number, never a dash

## Success Criteria

```bash
# eval_1: the SQL arithmetic reproduces assessStage over the recording
eval_1() {
  ( cd front && npx vitest --run src/contract/refusedCount.test.ts )
}

# eval_2: serve's rollup carries the same column and its static tests pass
eval_2() {
  ( cd serve && uv run --extra dev pytest tests/test_console_reads.py tests/test_console_parity_gate.py tests/test_api_resources.py tests/test_ch.py tests/test_projection_parity.py -q -p no:warnings )
}

# eval_3: the whole front gate stays green
eval_3() {
  ( cd front && npm run typecheck && npm run lint && npm test -- --run && npm run build )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the SQL arithmetic reproduces assessStage over the recording"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "serve's rollup carries the same column and its static tests pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-2]
    terminal: true
    expected_duration_sec: 90
  - id: eval_3
    description: "the whole front gate stays green"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
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

- A Python port of assessStage; the SQL is the single owner both doors run.
- Counting an unindexed run or a run with no stage rows as zero refusals.
- Editing the refusal thresholds in rules.ts to make the SQL match.

## Do-Not-Touch

- `engine`
- `front/src/data/fixtures.ts`

## Open Questions

(none — this task is fully specified)
