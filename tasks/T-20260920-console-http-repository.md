---
id: T-20260920-console-http-repository
title: "Give the console an http data source"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260920-api-resource-routes]
touches_paths: [front/src/data/repository.ts, front/src/data/runtimeConfig.ts, front/src/data/env.d.ts, front/.env.example]
creates_paths: [front/src/data/http.ts, front/src/data/httpRepository.test.ts]
source_note: "front/src/data/clickhouse.ts"
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
signed_off_at: 2026-09-20T21:24:58Z
accepted: true
accepted_by: sidymar
accepted_at: 2026-09-20T21:27:05Z
signed_off_sig: hmac-sha256-v2:5153084e:8e267b884a58deb9286e3d5f3dfd22b539edfa79143ffa7a91f1145ab1ecbb7d
---

# Give the console an http data source

> **Why:** clickhouse.ts already names the exit - swap ClickHouseRepository for an HTTP client against serve/, the Repository interface is the seam. This takes that exit without a big-bang cutover.

## Goal

An HttpRepository implementing Repository, selected by a new "http" data source, with clickhouse and fixtures still selectable.

## Context

runtimeConfig.ts:26 declares DATA_SOURCES as auto, clickhouse, fixtures and repository.ts:246 picks by mode; adding http is a typed change in three places. The token is deployment configuration, resolved the same runtime way the ClickHouse credential is today, so one image can still be pointed anywhere. No screen may change - that is the proof the seam held.

## Behavior

- **B-1** — GIVEN DATA_SOURCE=http WHEN the repository is constructed THEN an HttpRepository is returned and its kind reports http
- **B-2** — GIVEN an HttpRepository WHEN each of the twelve Repository methods is called THEN each issues one request to its /v1 route and returns the declared type
- **B-3** — GIVEN DATA_SOURCE=clickhouse or fixtures WHEN the repository is constructed THEN the existing implementations are returned unchanged
- **B-4** — GIVEN the API answers 401 WHEN a screen loads THEN the console reports an authentication failure and does not fall back to a direct ClickHouse query
- **B-5** — GIVEN the http data source WHEN the screens are rendered against it THEN no file under front/src/screens is modified

## Success Criteria

```bash
# eval_1: the http mode is selectable and covers the interface
eval_1() {
  ( cd front && npm run test -- --run src/data/httpRepository.test.ts )
}

# eval_2: types still check and no screen changed
eval_2() {
  ( cd front && npm run typecheck && git diff --exit-code --stat -- src/screens )
}

# eval_3: a 401 surfaces instead of silently falling back
eval_3() {
  ( cd front && npm run test -- --run src/data/httpRepository.test.ts -t "401" )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the http mode is selectable and covers the interface"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 120
  - id: eval_2
    description: "types still check and no screen changed"
    runnable: bash
    check_type: deterministic
    verifies: [B-5]
    terminal: true
    expected_duration_sec: 120
  - id: eval_3
    description: "a 401 surfaces instead of silently falling back"
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
eval_1 && eval_2 && eval_3
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Letting auto fall back from http to clickhouse on a 401, which quietly restores the credential this work removes.
- Changing a screen to fit the HTTP response instead of matching the Repository types.
- Baking the API token into the built bundle rather than resolving it at container start like the existing config.

## Do-Not-Touch

- `front/src/screens/`
- `front/src/components/`

## Open Questions

(none — this task is fully specified)
