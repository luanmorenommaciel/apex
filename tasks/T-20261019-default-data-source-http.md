---
id: T-20261019-default-data-source-http
title: "Make http the console's default data source"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-nginx-hardening]
supersedes: (none)
touches_paths: [front/Makefile, front/docker-compose.yml, front/.env.example, front/README.md]
creates_paths: []
source_note: "the user's decision D-2026-10-19-default-http (metadata.decisions); front/Makefile line 24 (DATA_SOURCE ?= clickhouse), front/docker-compose.yml VITE_DATA_SOURCE default clickhouse, front/.env.example VITE_DATA_SOURCE=auto, front/contract/01-readonly-user.sql (apex_ro, no_password)"
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

# Make http the console's default data source

> **Why:** make prod and docker compose up both default to DATA_SOURCE=clickhouse, the mode that ships a database credential to every browser - apex_ro with no password. The http mode exists precisely so the browser holds an API token instead, and the user decided on 2026-10-19 that it is the default; today it must be asked for.

## Goal

With nothing set, make prod runs the image with DATA_SOURCE=http, docker compose up runs the dev server with VITE_DATA_SOURCE=http, .env.example says http, the README presents http as the default and clickhouse as the explicit bench mode, and an up-clickhouse target exists beside up-fixtures for the bench.

## Context

The Makefile default becomes DATA_SOURCE ?= http and the compose default VITE_DATA_SOURCE default http; the up target's help text and the compose header comment say to start the API first (serve, APEX_API_PORT 8099) with the store step as the clickhouse alternative, and a new up-clickhouse target sets VITE_DATA_SOURCE=clickhouse the way up-fixtures sets fixtures. The image entrypoint default stays auto - it already probes the API first, and what auto does on failure is D-auto-fallback-policy, not this leaf. The README Configure a deployment table row for DATA_SOURCE keeps auto as the IMAGE default and says the repo entry points default to http; the Querying ClickHouse from the browser section opens by saying that mode is opt-in and why. Like T-20260923-console-http-deployment-wiring, the compose change is proven by rendering with docker compose config and the Makefile by make -n, never by grep on the file.

## Behavior

- **B-1** — GIVEN no VITE_DATA_SOURCE in the shell WHEN docker compose config renders the console service THEN VITE_DATA_SOURCE is http
- **B-2** — GIVEN make -n prod with only CLICKHOUSE_UPSTREAM given WHEN the docker run line is printed THEN it carries -e DATA_SOURCE=http
- **B-3** — GIVEN make -n up-clickhouse WHEN the compose line is printed THEN it sets VITE_DATA_SOURCE=clickhouse
- **B-4** — GIVEN .env.example and README.md WHEN they are read THEN .env.example sets VITE_DATA_SOURCE=http and the README names http as the default and clickhouse as opt-in

## Success Criteria

```bash
# eval_1: compose renders http with nothing set
eval_1() {
  ( cd front && env -u VITE_DATA_SOURCE docker compose config | grep -q "VITE_DATA_SOURCE.*http$" )
}

# eval_2: make prod and make up-clickhouse print the right mode
eval_2() {
  ( cd front && make -n prod | grep -q -- '-e DATA_SOURCE="http"' )
}

# eval_3: the docs say http is the default
eval_3() {
  ( cd front && grep -q "^VITE_DATA_SOURCE=http" .env.example && grep -qi "default.*http\|http.*default" README.md )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "compose renders http with nothing set"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "make prod and make up-clickhouse print the right mode"
    runnable: bash
    check_type: deterministic
    verifies: [B-2, B-3]
    terminal: true
    expected_duration_sec: 10
  - id: eval_3
    description: "the docs say http is the default"
    runnable: bash
    check_type: deterministic
    verifies: [B-4]
    terminal: true
    expected_duration_sec: 5
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

- Changing the image entrypoint default or runtimeConfig - auto on the image is a separate decision.
- Removing the clickhouse mode or apex_ro - the bench still uses them, explicitly.
- A token literal anywhere in the Makefile, compose file or env example.

## Do-Not-Touch

- `front/docker-entrypoint.d`
- `front/src`
- `front/nginx.conf`
- `front/contract`

## Open Questions

(none — this task is fully specified. Eval amended before sealing on 2026-10-19: D-api-only removed the /clickhouse proxy and the up-clickhouse target after this leaf was built, so the assertions that counted them were narrowed to what still exists; see tasks/.plans/front-lane-hardening.yaml.)
