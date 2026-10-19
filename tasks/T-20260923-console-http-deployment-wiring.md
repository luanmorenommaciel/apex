---
id: T-20260923-console-http-deployment-wiring
title: "Let compose, make prod and the README run the console in http mode"
status: in-progress
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [front/docker-compose.yml, front/Makefile, front/README.md, front/.env.example]
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

# Let compose, make prod and the README run the console in http mode

> **Why:** Everything RUNBOOK section 5 documents by hand, the repo's own entry points cannot do. docker-compose.yml passes no VITE_APEX_API_PROXY_TARGET or VITE_APEX_API_TOKEN, and inside the container the proxy's default 127.0.0.1:8099 is the container itself, so `make up` cannot reach an API on the host. `make prod` passes no APEX_API_UPSTREAM or APEX_API_TOKEN. README.md:129 still says HttpRepository "...is the one to write" and :223 says /ask is waiting on it being written. .env.example's closing NOTE lists the container variables and omits the three API ones.

## Goal

VITE_DATA_SOURCE=http make up reaches an API on the host through the dev proxy; make prod accepts APEX_API_UPSTREAM and APEX_API_TOKEN; the README describes the http data source as something that exists and how to select it in dev and in the image; .env.example's NOTE lists the container variables including the API ones.

## Context

In compose the proxy target defaults to http://host.docker.internal:8099, the same gateway alias VITE_CLICKHOUSE_URL already uses, and stays overridable; the token is passed through from the shell and never written into the file. In the Makefile APEX_API_UPSTREAM defaults to the same alias and both variables are passed with -e; APEX_API_URL is deliberately NOT passed - it makes the browser call cross-origin and the API sends no CORS header. Passing an unset APEX_API_TOKEN as an empty -e is fine - the entrypoint emits an empty apiToken key, which is the bundle's own default. PR 129's lesson applies to the evals - a grep on a config file passed on a file nginx rejected - so the compose change is checked by rendering it with `docker compose config`, which interpolates and validates, and the Makefile change by `make -n prod`, which prints the docker run it would execute. The README rows to rewrite are the fenced block under "Querying ClickHouse from the browser" and the /ask row of "What waits on other lanes" - which should now say the diagnostics tier exists over /v1 and what is missing is a consumer, the decision recorded in this plan's metadata.open_decisions. The docs greps in eval_3 are on prose, where a grep is the right tool.

## Behavior

- **B-1** — GIVEN VITE_DATA_SOURCE=http in the shell WHEN docker compose config renders the console service THEN it carries VITE_DATA_SOURCE http and VITE_APEX_API_PROXY_TARGET http://host.docker.internal:8099, and no VITE_APEX_API_URL
- **B-2** — GIVEN make -n prod with APEX_API_UPSTREAM and APEX_API_TOKEN set WHEN the docker run line is printed THEN it carries -e APEX_API_UPSTREAM and -e APEX_API_TOKEN and never -e APEX_API_URL
- **B-3** — GIVEN the README WHEN it is read THEN it no longer says HttpRepository is to be written, and it documents DATA_SOURCE=http for dev and for the image
- **B-4** — GIVEN .env.example's closing NOTE WHEN it is read THEN the container variable list includes APEX_API_UPSTREAM, APEX_API_TOKEN and APEX_API_URL

## Success Criteria

```bash
# eval_1: compose renders the http wiring and never a cross-origin url
eval_1() {
  ( cd front && VITE_DATA_SOURCE=http docker compose config > /dev/null && VITE_DATA_SOURCE=http docker compose config | grep -q "VITE_APEX_API_PROXY_TARGET.*host.docker.internal.8099" && VITE_DATA_SOURCE=http docker compose config | grep -q "VITE_DATA_SOURCE.*http$" && ! (docker compose config | grep -q VITE_APEX_API_URL) )
}

# eval_2: make prod passes the two API variables and not the third
eval_2() {
  ( cd front && make -n prod CLICKHOUSE_UPSTREAM=http://ch.test.8123 APEX_API_UPSTREAM=http://api.test.8099 APEX_API_TOKEN=tok | grep -q -- "-e APEX_API_UPSTREAM" && make -n prod CLICKHOUSE_UPSTREAM=http://ch.test.8123 APEX_API_UPSTREAM=http://api.test.8099 APEX_API_TOKEN=tok | grep -q -- "-e APEX_API_TOKEN" && ! (make -n prod CLICKHOUSE_UPSTREAM=http://ch.test.8123 | grep -q APEX_API_URL) )
}

# eval_3: the docs say what exists
eval_3() {
  ( cd front && ! grep -q "is the one to write" README.md && grep -q "DATA_SOURCE=http" README.md && grep -q "APEX_API_UPSTREAM" .env.example && grep -q "APEX_API_TOKEN" .env.example )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "compose renders the http wiring and never a cross-origin url"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 60
  - id: eval_2
    description: "make prod passes the two API variables and not the third"
    runnable: bash
    check_type: deterministic
    verifies: [B-2]
    terminal: true
    expected_duration_sec: 30
  - id: eval_3
    description: "the docs say what exists"
    runnable: bash
    check_type: deterministic
    verifies: [B-3, B-4]
    terminal: true
    expected_duration_sec: 30
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

- A proxy target of 127.0.0.1 inside a container; it is the container.
- Passing APEX_API_URL to the image "for completeness"; it is the cross-origin path the API does not allow.
- A token literal in docker-compose.yml or the Makefile.
- Guarding the compose or Makefile change with a grep on the file instead of rendering it.

## Do-Not-Touch

- `front/nginx.conf`
- `front/Dockerfile`
- `front/docker-entrypoint.d/`
- `front/src/`

## Open Questions

(none — this task is fully specified)
