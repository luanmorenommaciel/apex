---
id: T-20260921-pr129-review-fixes
title: "Fix the four defects Codex found on PR 129"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260921-console-same-origin-api]
touches_paths: [front/nginx.conf, front/vite.config.ts, front/src/data/runtimeConfig.ts, front/src/data/env.d.ts, front/src/data/httpRepository.test.ts, front/.env.example, serve/src/apex_mcp/ch.py, serve/tests/test_ch.py, serve/src/apex_api/routes/resources.py, serve/tests/test_api_resources.py, serve/RUNBOOK.md]
creates_paths: []
source_note: "https://github.com/luanmorenommaciel/apex/pull/129"
created: "2026-09-21T00:00:00Z"
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
signed_off_at: 2026-09-21T14:59:11Z
accepted: false
accepted_by: (none)
accepted_at: (none)
signed_off_sig: hmac-sha256-v2:5153084e:9297d27c4a20846db2dc0e720788ae4100949880c1dfe10f77f3a3051917d396
---

# Fix the four defects Codex found on PR 129

> **Why:** Two P1s and two P2s, all reproduced. The nginx block was spliced INSIDE the clickhouse proxy_pass because the insertion matched the brace inside ${CLICKHOUSE_UPSTREAM}, so no container starts at all - and the eval that was meant to guard it only grepped for a string, which passes on the broken file. The stages route returns the MCP's p50_ms/p99_ms and omits job_id, stage_name and ts, so three screens would render NaN.

## Goal

nginx validates in a real container, the stages route returns the console's projection, the dev proxy target stops forcing a cross-origin apiUrl, and fix_verification gates only on the tables it reads.

## Context

The stages gap is a PORT, not a rename - LATEST_STAGES also projects job_id, stage_name and ts, which STAGES_SQL has never carried. That makes it the eighth console query to move server-side, and the fourth time this plan mapped a console method onto a ReadStore method by name without comparing projections. Every eval here executes the thing it claims to check; the previous nginx eval did not.

## Behavior

- **B-1** — GIVEN the nginx template with both upstreams set WHEN the image renders it and runs nginx -t THEN the configuration is valid, with /clickhouse and /v1 as sibling location blocks
- **B-2** — GIVEN a job_id WHEN GET /v1/runs/{job_id}/stages is called THEN every field SparkEventRow declares is present, including task_duration_p50_ms, task_duration_p99_ms, job_id, stage_name and ts
- **B-3** — GIVEN the documented development environment WHEN runtimeConfig is resolved THEN apiUrl is empty, so requests stay relative and reach the API through the proxy rather than cross-origin
- **B-4** — GIVEN an explicit absolute apiUrl WHEN runtimeConfig is resolved THEN it is honoured, because a deliberate cross-origin deployment is still supported
- **B-5** — GIVEN apex.fix_verifications and apex.run_outcomes present but apex.plan_memory absent WHEN fix_verification is called THEN it returns the row, because that query reads neither plan_memory nor anything derived from it

## Success Criteria

```bash
# eval_1: nginx renders and validates in the real image
eval_1() {
  ( cd front && docker run --rm -e CLICKHOUSE_UPSTREAM=http://127.0.0.1:8123 -e APEX_API_UPSTREAM=http://127.0.0.1:8099 -e 'NGINX_ENVSUBST_FILTER=^(CLICKHOUSE_UPSTREAM|APEX_API_UPSTREAM)$' -v "$PWD/nginx.conf:/etc/nginx/templates/default.conf.template:ro" nginx:1.27-alpine nginx -t )
}

# eval_2: the stages route carries the console's projection
eval_2() {
  ( cd serve && uv run --extra dev pytest "tests/test_api_resources.py::test_stages_route_returns_the_console_projection" "tests/test_ch.py::test_console_stages_projects_what_the_console_reads" )
}

# eval_3: the documented dev setup stays same-origin
eval_3() {
  ( cd front && npm run test -- --run src/data/httpRepository.test.ts -t "proxy target" )
}

# eval_4: verification does not require the plan-memory table
eval_4() {
  ( cd serve && uv run --extra dev pytest "tests/test_ch.py::test_fix_verification_needs_no_plan_memory_table" )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "nginx renders and validates in the real image"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 120
  - id: eval_2
    description: "the stages route carries the console's projection"
    runnable: bash
    check_type: deterministic
    verifies: [B-2]
    terminal: true
    expected_duration_sec: 90
  - id: eval_3
    description: "the documented dev setup stays same-origin"
    runnable: bash
    check_type: deterministic
    verifies: [B-3, B-4]
    terminal: true
    expected_duration_sec: 120
  - id: eval_4
    description: "verification does not require the plan-memory table"
    runnable: bash
    check_type: deterministic
    verifies: [B-5]
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

- Guarding a config file with a grep for a substring; it passed on a file nginx rejects, which is how this shipped.
- Renaming two timing fields and calling the stages gap closed; job_id, stage_name and ts are missing too.
- Making the browser's apiUrl and the dev proxy target the same variable, which is the fault being fixed.

## Do-Not-Touch

- `front/src/screens/`
- `front/src/data/repository.ts`

## Open Questions

(none — this task is fully specified)
