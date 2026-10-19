---
id: T-20260923-console-findings-transitions-projection
title: "Serve findings and transitions in the console's projection"
status: in-progress
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [serve/src/apex_mcp/ch.py, serve/src/apex_api/routes/resources.py, serve/tests/test_ch.py, serve/tests/test_api_resources.py]
creates_paths: []
source_note: "front/src/data/queries.ts"
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

# Serve findings and transitions in the console's projection

> **Why:** The fifth time this plan mapped a console method onto a ReadStore method by NAME without comparing projections - runs, verifications and stages were the first three, and the stages fix (PR 129) corrected only stages. /v1/runs/{job}/findings serves ch._findings_sql, which omits ts and orders by ts ASC; the console's FINDINGS orders by confidence_score DESC and VerifyScreen.tsx:58 takes [0] as the highest-confidence finding, so /verify with no parameters opens on the OLDEST one. /v1/runs/{job}/transitions serves PLAN_TRANSITIONS_SQL, one row per update_seq with no job_id, plan_fingerprint or ts; the console's PLAN_TRANSITIONS collapses to one row per execution_id at max(update_seq), so a re-plan logged three times counts as three transitions on RunDetailScreen.tsx:354 and FindingScreen.tsx:139, and FindingScreen.tsx:54 renders the oldest before/after as the current one.

## Goal

ReadStore gains console_findings and console_transitions, ported from FINDINGS and PLAN_TRANSITIONS the way console_stages was; the two routes serve them; and a parity test reads the field lists from front/src/contract/types.ts and front/src/data/repository.ts and fails when any declared field is not projected by the SQL that serves it - so this class of defect cannot ship a sixth time.

## Context

These are PORTS, like the six in T-20260920-readstore-console-queries - the console's rendered numbers are the acceptance criterion. Two mechanical differences from the browser copies, both already handled by the earlier ports - tables are qualified apex. and the bound parameter is job_id, not job. One difference is a DECISION and is recorded here as a proposed choice, open for review - the MCP's _findings_sql probes system.columns for the v0.2 additive columns app_id and confidence_score and serves defaults when a cluster predates them; the console's FINDINGS never probed and reads confidence_score unconditionally, because FindingRow.confidence_score is required. The port keeps the console's behaviour and does not probe. If a pre-v0.2 cluster must be served by the API, that is a follow-up, not something to fold in silently. Why test_row_shapes_match_the_console_contract did not catch this - it asserts a SUBSET of columns per route, and the fakes return whatever rows they are handed, so the projection that lives in the SQL is never compared to the contract. The parity test closes that - it extracts each interface's field names from the TypeScript the same way repository_methods() already extracts the method names, and checks every field appears as a SELECT alias in the SQL constant that serves the route. Fields the console's own mapper supplies rather than the SQL (FixVerificationRow's replay_durations_ms, requires_human_approval, applied - see toFixVerification in repository.ts) are an explicit allow-list in the test, with the reason beside each. RunSummary is derived by toRunSummary from the RunRollupRow interface in repository.ts, so RunRollupRow is the wire shape the test reads for the runs routes. Live parity - the two routes against the infra stack compared row-for-row with the console's ClickHouse path - is the acceptor's terminal proof and is not automatable offline; RUNBOOK section 3 shows the walk.

## Behavior

- **B-1** — GIVEN a job_id WHEN GET /v1/runs/{job_id}/findings is called THEN every row carries every FindingRow field including ts, and the rows are ordered by confidence_score DESC - the order VerifyScreen assumes when it takes the first row
- **B-2** — GIVEN a job whose execution_id was re-planned more than once WHEN GET /v1/runs/{job_id}/transitions is called THEN there is ONE row per execution_id carrying the values at max(update_seq), plus job_id, plan_fingerprint joined from spark_events and ts, as the console's PLAN_TRANSITIONS returns
- **B-3** — GIVEN the SQL constants that serve the console routes WHEN the parity test reads FindingRow, PlanTransitionRow, JobConfRow and FixVerificationRow from front/src/contract/types.ts and RunRollupRow from front/src/data/repository.ts THEN every declared field is projected as an alias by the SQL that serves it, and removing one alias fails the test
- **B-4** — GIVEN the MCP tools WHEN findings() and plan_transitions() are called THEN they are unchanged - the MCP's own projections and the eight tools' tests still pass
- **B-5** — GIVEN a job_id containing SQL syntax WHEN console_findings or console_transitions is called THEN it is bound as a parameter and never interpolated, consistent with every existing method

## Success Criteria

```bash
# eval_1: the two routes return the console's projection and order
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_api_resources.py::test_findings_route_returns_the_console_projection" "tests/test_api_resources.py::test_transitions_route_returns_the_console_projection" )
}

# eval_2: the ports order, collapse and bind the way the console's SQL does
eval_2() {
  ( cd serve && uv run --extra dev pytest "tests/test_ch.py::test_console_findings_orders_by_confidence_score" "tests/test_ch.py::test_console_transitions_collapse_per_execution" "tests/test_ch.py::test_console_findings_and_transitions_bind_parameters" )
}

# eval_3: every contract field is projected by the SQL that serves it
eval_3() {
  ( cd serve && uv run --extra dev pytest "tests/test_api_resources.py::test_every_console_field_is_projected" )
}

# eval_4: the MCP side did not move
eval_4() {
  ( cd serve && uv run --extra dev pytest tests/test_server_tools.py tests/test_api_diagnostics.py )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the two routes return the console's projection and order"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 90
  - id: eval_2
    description: "the ports order, collapse and bind the way the console's SQL does"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-5]
    terminal: true
    expected_duration_sec: 60
  - id: eval_3
    description: "every contract field is projected by the SQL that serves it"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
    terminal: true
    expected_duration_sec: 60
  - id: eval_4
    description: "the MCP side did not move"
    runnable: bash
    check_type: deterministic
    verifies: [B-4]
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
eval_1 && eval_2 && eval_3 && eval_4
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Mapping a console method onto a ReadStore method by name; the five prior cases are the reason this leaf exists.
- Adding ts and the console's ORDER BY to the MCP's _findings_sql or PLAN_TRANSITIONS_SQL so one query serves both; two consumers, two projections, exactly as stages() and console_stages() already stand.
- A parity test that asserts a hand-kept subset of columns; the field list must come from the TypeScript.
- Folding the additive-column probe into the console SQL without recording it as the decision it is.

## Do-Not-Touch

- `serve/src/apex_mcp/server.py`
- `serve/tests/test_server_tools.py`
- `front/src/`

## Open Questions

(none — this task is fully specified)
