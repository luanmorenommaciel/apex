---
id: T-20261019-front-http-only-resolution
title: "Read only through the API in the console's source"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-serve-owns-console-sql]
supersedes: (none)
touches_paths: [front/src/data, front/src/components/molecules, front/src/screens, front/src/contract/types.ts, front/src/contract/rules.ts, front/src/contract/refusedCount.test.ts, front/src/e2e/console.live.test.tsx]
creates_paths: []
source_note: "D-api-only with P-fixtures-in-image and P-boot-probe; front/src/data/repository.ts (ClickHouseRepository, resolveRepository), clickhouse.ts, queries.ts, runtimeConfig.ts, env.d.ts, the tests beside them, NavBar.tsx SOURCE, QueryFailure.tsx SOURCE_NAME, StoreUnreachable.tsx, the screen tests' failing() proxies (kind clickhouse)"
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

# Read only through the API in the console's source

> **Why:** The console still carries a second door - SQL text, a ClickHouse HTTP client, a database user and password in its runtime config - that the user decided it must not have. While it exists, auto can open it and a deployment can be pointed at it.

## Goal

The console's source has one data door, HttpRepository, plus FixtureRepository for the recording; DataSource is http or fixtures; runtimeConfig carries dataSource, apiUrl and apiToken only; resolveRepository in http mode probes /v1/health once and renders StoreUnreachable only when nothing answers; every test passes and no file under front/src names ClickHouse as a source.

## Context

Delete src/data/clickhouse.ts, queries.ts, queries.test.ts, queries.consumed.test.ts and findingsProjection.test.ts; remove ClickHouseRepository and the FINDINGS probe from repository.ts; Repository.kind becomes http or fixtures and NavBar's SOURCE and QueryFailure's SOURCE_NAME shrink with it (exhaustive records, so the compiler lists every site). runtimeConfig drops database, user and password and env.d.ts drops VITE_CLICKHOUSE_*; the window.__APEX_CONFIG__ shape drops them too. resolveRepository - fixtures returns FixtureRepository; http calls apiPing() once - true, or a 401, mounts HttpRepository; a probe that gets no HTTP answer at all throws StoreUnreachableError naming only /v1/health (P-boot-probe). auto and clickhouse are no longer DataSource values; asDataSource maps anything unrecognised to http. httpRepository.test.ts loses its clickhouse and auto cases and gains the boot-probe ones; resolveRepository.test.ts is rewritten for the two modes; useAsync.test.tsx keeps the abort test for HttpRepository only; the screen tests' failing() proxies set kind http and assert the apex-api wording QueryFailure already has; the e2e test's mocked runtimeConfig drops the three ClickHouse fields. Comments in RunDetailScreen.tsx, types.ts and rules.ts that name queries.ts or the browser door are reworded to name the API. StoreUnreachable lists what was probed from the error, so it needs no change beyond wording.

## Behavior

- **B-1** — GIVEN front/src after the change WHEN it is searched THEN no clickhouse.ts, no queries.ts, no ClickHouseRepository, no VITE_CLICKHOUSE and no X-ClickHouse header
- **B-2** — GIVEN DATA_SOURCE=http with an API that answers or answers 401 WHEN the app boots THEN HttpRepository is used and the app mounts
- **B-3** — GIVEN DATA_SOURCE=http with no HTTP answer at /v1/health WHEN the app boots THEN StoreUnreachable renders naming /v1/health and nothing else
- **B-4** — GIVEN DATA_SOURCE=fixtures WHEN the app boots THEN FixtureRepository is used without any probe

## Success Criteria

```bash
# eval_1: the door is gone from the source
eval_1() {
  ( cd front && test ! -f src/data/clickhouse.ts && test ! -f src/data/queries.ts && ! grep -rn "ClickHouseRepository\|VITE_CLICKHOUSE\|X-ClickHouse\|\"clickhouse\"" src )
}

# eval_2: the resolution tests pass
eval_2() {
  ( cd front && npx vitest --run src/data/resolveRepository.test.ts src/data/httpRepository.test.ts src/data/useAsync.test.tsx )
}

# eval_3: the whole front gate stays green
eval_3() {
  ( cd front && npm run typecheck && npm run lint && npm test -- --run && npm run build )
}

# eval_4: serve still finds every Repository method and row type it serves
eval_4() {
  ( cd serve && uv run --extra dev pytest tests/test_api_resources.py -q -p no:warnings )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the door is gone from the source"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 5
  - id: eval_2
    description: "the resolution tests pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-2, B-3, B-4]
    terminal: true
    expected_duration_sec: 30
  - id: eval_3
    description: "the whole front gate stays green"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 90
  - id: eval_4
    description: "serve still finds every Repository method and row type it serves"
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

- Keeping ClickHouseRepository behind a flag "in case"; the decision is the door goes.
- Removing FixtureRepository; tests and up-fixtures use it, and P-fixtures-in-image keeps it explicit.
- Treating a 401 at boot as unreachable; the API exists and refused, which the screens report.
- Touching the deployment files (nginx.conf, Dockerfile, entrypoint, compose, Makefile); that is the next leaf.

## Do-Not-Touch

- `front/nginx.conf`
- `front/Dockerfile`
- `front/docker-entrypoint.d`
- `front/docker-compose.yml`
- `front/Makefile`
- `front/.env.example`
- `front/vite.config.ts`
- `front/README.md`
- `serve`

## Open Questions

(none — this task is fully specified)
