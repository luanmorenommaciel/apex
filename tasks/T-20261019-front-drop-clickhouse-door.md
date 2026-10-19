---
id: T-20261019-front-drop-clickhouse-door
title: "Remove the ClickHouse door from the console's deployment surface"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-front-http-only-resolution]
supersedes: (none)
touches_paths: [front/nginx.conf, front/Dockerfile, front/docker-entrypoint.d/30-apex-console-config.sh, front/docker-compose.yml, front/Makefile, front/.env.example, front/vite.config.ts, front/README.md, front/src/data/entrypoint.test.ts]
creates_paths: []
source_note: "D-api-only with P-fixtures-in-image; front/nginx.conf (location = /clickhouse and /clickhouse/), Dockerfile (ENV CLICKHOUSE_UPSTREAM, NGINX_ENVSUBST_FILTER), docker-entrypoint.d/30-apex-console-config.sh (clickhouse and auto branches, CLICKHOUSE_DB/USER/PASSWORD keys), docker-compose.yml (VITE_CLICKHOUSE_*), Makefile (CH_*, store, ch-ping, ch-tables, ch-user, up-clickhouse, prod -e CLICKHOUSE_*), .env.example, vite.config.ts (/clickhouse proxy), front/contract/01-readonly-user.sql, src/data/entrypoint.test.ts (clickhouse and auto describes)"
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

# Remove the ClickHouse door from the console's deployment surface

> **Why:** With the door gone from the source, the image still proxies /clickhouse to a deployment-owned upstream, the entrypoint still writes a database user and password into /config.js, and the Makefile still creates apex_ro on infra's store. Every one of those is a way to put the browser back on the database.

## Goal

The image knows one upstream, APEX_API_UPSTREAM; DATA_SOURCE accepts http (default) and fixtures and the entrypoint refuses anything else by name; /config.js carries dataSource, apiUrl and apiToken only; nginx and Vite proxy /v1 only; the Makefile and compose start the console against the API or the recording and nothing else; the read-only user DDL is gone from front/contract; the entrypoint tests and README describe exactly that; the prod image builds and answers.

## Context

nginx.conf loses both /clickhouse locations and their comment; NGINX_ENVSUBST_FILTER and the ENV defaults in the Dockerfile keep APEX_API_UPSTREAM alone. The entrypoint's header, the mode case and the config.js keys shrink to http and fixtures - an unrecognised DATA_SOURCE is now refused at boot with its value named, because the bundle's "anything else is http" would otherwise hide a typo; the auto branch and its messages go. compose drops the three VITE_CLICKHOUSE_* lines and the store comment; the Makefile drops CH, CH_CONTAINER, CH_ADMIN_*, CLICKHOUSE_UPSTREAM, CH_DB/USER/PASSWORD, the store, ch-ping, ch-tables, ch-user and up-clickhouse targets, and prod stops passing -e CLICKHOUSE_*. vite.config.ts keeps the /v1 proxy only. .env.example keeps the API variables and the two data sources. README - the quick start, the deployment table, the "Querying ClickHouse from the browser" section (which becomes a short history note saying the door was removed on 2026-10-19 and why), the layout block and the ledger. entrypoint.test.ts loses the clickhouse and auto describes and gains a case for a refused unknown value. The prod image is built and curled in fixtures mode as the hardening leaf did.

## Behavior

- **B-1** — GIVEN nginx.conf, Dockerfile, vite.config.ts and the entrypoint WHEN they are searched THEN none names CLICKHOUSE_UPSTREAM, /clickhouse, CLICKHOUSE_DB, CLICKHOUSE_USER or CLICKHOUSE_PASSWORD
- **B-2** — GIVEN the entrypoint with DATA_SOURCE unset, http, fixtures and an unknown value WHEN it runs THEN unset and http behave alike, fixtures needs no upstream, and the unknown value is refused with the value in the message
- **B-3** — GIVEN the prod image in fixtures mode WHEN / is requested THEN it answers 200 with the hardening headers, and /config.js carries no database key
- **B-4** — GIVEN the Makefile and compose WHEN rendered THEN no CLICKHOUSE variable and no ch- target remain, and the README has no apex_ro setup step

## Success Criteria

```bash
# eval_1: the door is gone from every deployment file
eval_1() {
  ( cd front && ! grep -rn "CLICKHOUSE_UPSTREAM\|/clickhouse\|CLICKHOUSE_DB\|CLICKHOUSE_USER\|CLICKHOUSE_PASSWORD\|VITE_CLICKHOUSE" nginx.conf Dockerfile vite.config.ts docker-entrypoint.d docker-compose.yml Makefile .env.example && test ! -f contract/01-readonly-user.sql && ! grep -q "ch-user\|up-clickhouse\|apex_ro" Makefile && ! grep -q "make ch-user\|up-clickhouse" README.md )
}

# eval_2: the entrypoint tests pass with the two modes and the refusal
eval_2() {
  ( cd front && npx vitest --run src/data/entrypoint.test.ts && grep -q "unknown\|unrecognised" src/data/entrypoint.test.ts )
}

# eval_3: the prod image builds and serves the recording with the headers and no database key
eval_3() {
  ( cd front && docker rm -f apex-console-apionly-eval > /dev/null 2>&1; docker build -q --target prod -t apex-console:apionly-eval . > /dev/null && docker run -d --rm --name apex-console-apionly-eval -p 18083:80 -e DATA_SOURCE=fixtures apex-console:apionly-eval > /dev/null && sleep 2 && H="$(curl -sI http://127.0.0.1:18083/)" && C="$(curl -s http://127.0.0.1:18083/config.js)"; docker rm -f apex-console-apionly-eval > /dev/null; echo "$H" | grep -q "200" && echo "$H" | grep -qi "^content-security-policy" && echo "$C" | grep -q "dataSource" && ! echo "$C" | grep -qi "database\|password" )
}

# eval_4: compose and make render without the store, and the whole front gate stays green
eval_4() {
  ( cd front && docker compose config > /dev/null && ! (docker compose config | grep -q CLICKHOUSE) && make -n prod | grep -q APEX_API_UPSTREAM && ! (make -n prod | grep -q CLICKHOUSE) && npm run typecheck && npm run lint && npm test -- --run )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the door is gone from every deployment file"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-4]
    terminal: true
    expected_duration_sec: 5
  - id: eval_2
    description: "the entrypoint tests pass with the two modes and the refusal"
    runnable: bash
    check_type: deterministic
    verifies: [B-2]
    terminal: true
    expected_duration_sec: 30
  - id: eval_3
    description: "the prod image builds and serves the recording with the headers and no database key"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
    terminal: true
    expected_duration_sec: 180
  - id: eval_4
    description: "compose and make render without the store, and the whole front gate stays green"
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

- Leaving the /clickhouse location "for compatibility"; a proxy to a store nobody configures is the door reopened.
- Keeping CLICKHOUSE_PASSWORD in /config.js as an empty key; the key itself is the leak.
- Silently mapping an unknown DATA_SOURCE to http in the entrypoint; it is refused by name.

## Do-Not-Touch

- `front/src/data/repository.ts`
- `front/src/screens`
- `front/src/components`
- `serve`
- `infra`

## Open Questions

(none — this task is fully specified. touches_paths narrowed before sealing on 2026-10-19: front/contract/01-readonly-user.sql is the file this leaf deleted, and the validator refuses a declared path that no longer exists.)
