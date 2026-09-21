---
id: T-20260921-console-same-origin-api
title: "Reach the API same-origin, the way the console reaches ClickHouse"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260920-console-http-repository]
touches_paths: [front/vite.config.ts, front/nginx.conf, front/Dockerfile, front/docker-entrypoint.d/30-apex-console-config.sh, front/src/data/httpRepository.test.ts, front/.env.example, serve/RUNBOOK.md]
creates_paths: []
source_note: "front/src/data/clickhouse.ts"
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
signed_off_at: 2026-09-21T12:13:00Z
accepted: false
accepted_by: (none)
accepted_at: (none)
signed_off_sig: hmac-sha256-v2:5153084e:8063a018df166a850ce169291290e9241c29985e6092a668ad83b09a6ff07d1f
---

# Reach the API same-origin, the way the console reaches ClickHouse

> **Why:** HttpRepository calls an ABSOLUTE url and the API sends no CORS header, so in a real browser every request fails preflight. The console's tests stub fetch, which is why nothing caught it. The ClickHouse path already solved this - "same-origin is achieved with a proxy (Vite in dev, nginx in prod), so ClickHouse itself never needs add_http_cors_header" - and the API deserves the same treatment rather than a second, weaker answer.

## Goal

With no apiUrl configured the console calls /v1 same-origin, and both proxies forward it; the container can be pointed at an API without a rebuild.

## Context

http.ts already produces a relative /v1 path when apiUrl is empty, so the client half is done - what is missing is the two proxies and the two config keys. Leaving apiUrl set remains supported for a direct cross-origin call, which then DOES need CORS on the API and is documented as such rather than silently broken. The entrypoint must keep emitting no key for an unset variable, because an emitted empty string is a real value the bundle would take over its own default. APEX_API_UPSTREAM is defaulted in the DOCKERFILE, not the entrypoint: the image's own 20-envsubst-on-templates.sh runs before 30-apex-console-config.sh, so a default exported there would arrive too late, and NGINX_ENVSUBST_FILTER must be widened or the placeholder survives into the served config and nginx refuses to start.

## Behavior

- **B-1** — GIVEN no apiUrl configured WHEN any HttpRepository method is called THEN the request path is relative and begins /v1, so the browser stays same-origin
- **B-2** — GIVEN an apiUrl is configured WHEN any HttpRepository method is called THEN the absolute url is used, unchanged from today
- **B-3** — GIVEN the dev server WHEN its config is read THEN it proxies /v1 to the API the same way it already proxies /clickhouse
- **B-4** — GIVEN APEX_API_URL and APEX_API_TOKEN are set in the container WHEN the entrypoint runs THEN config.js carries apiUrl and apiToken, and carries neither key when they are unset
- **B-5** — GIVEN nginx WHEN its config is read THEN it forwards /v1 to an APEX_API_UPSTREAM, and still refuses to start with an unset CLICKHOUSE_UPSTREAM only when that path is in use

## Success Criteria

```bash
# eval_1: the relative and absolute bases both behave
eval_1() {
  ( cd front && npm run test -- --run src/data/httpRepository.test.ts -t "same-origin" )
}

# eval_2: both proxies declare the route
eval_2() {
  ( cd front && grep -qE '"/v1"[[:space:]]*:' vite.config.ts && grep -q 'APEX_API_UPSTREAM' nginx.conf && grep -q 'APEX_API_UPSTREAM' Dockerfile )
}

# eval_3: the entrypoint emits the keys, and omits them when unset
eval_3() {
  ( cd front && bash -c 'set -e; d=$(mktemp -d); mkdir -p "$d/usr/share/nginx/html"; CLICKHOUSE_UPSTREAM=http://ch:8123 APEX_API_URL=http://api:8099 APEX_API_TOKEN=tok sh -c "sed \"s#/usr/share/nginx/html#$d/usr/share/nginx/html#\" docker-entrypoint.d/30-apex-console-config.sh | sh"; grep -q apiUrl "$d/usr/share/nginx/html/config.js"; grep -q apiToken "$d/usr/share/nginx/html/config.js"; CLICKHOUSE_UPSTREAM=http://ch:8123 sh -c "sed \"s#/usr/share/nginx/html#$d/usr/share/nginx/html#\" docker-entrypoint.d/30-apex-console-config.sh | sh"; ! grep -q apiUrl "$d/usr/share/nginx/html/config.js"' )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the relative and absolute bases both behave"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 120
  - id: eval_2
    description: "both proxies declare the route"
    runnable: bash
    check_type: deterministic
    verifies: [B-3, B-5]
    terminal: true
    expected_duration_sec: 30
  - id: eval_3
    description: "the entrypoint emits the keys, and omits them when unset"
    runnable: bash
    check_type: deterministic
    verifies: [B-4]
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
eval_1 && eval_2 && eval_3
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Adding CORS to the API instead of proxying, which makes the store's own answer to this question inconsistent with the API's and widens what any origin may call.
- Emitting an empty apiUrl key when the variable is unset; an empty string is a real value and would override the bundle's default.
- Requiring APEX_API_UPSTREAM unconditionally, which would break every ClickHouse-mode deployment that has no API.

## Do-Not-Touch

- `front/src/screens/`
- `front/src/data/repository.ts`

## Open Questions

(none — this task is fully specified)
