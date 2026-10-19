---
id: T-20261019-tls-external-terminator
title: "Behave correctly behind an external TLS terminator and say so"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [front/nginx.conf, front/README.md]
creates_paths: []
source_note: "D-tls-termination, option B; front/nginx.conf (listen 80, no HSTS, the bare /clickhouse 301 comment names the absolute-http-redirect hazard)"
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

# Behave correctly behind an external TLS terminator and say so

> **Why:** TLS terminates in front of the image, which nothing in the repository says. nginx's own redirects - the trailing-slash 301 try_files issues for a directory, the bare /clickhouse case already guarded - are absolute and carry http as the scheme, so behind a terminator a browser refuses them as mixed content, and nobody has written down that HSTS and the certificate belong to the terminator.

## Goal

nginx issues only relative redirects, keeps listening on 80 with no Strict-Transport-Security, and the README has a section that states the terminator contract - TLS, HSTS and the certificate live in front, X-Forwarded-Proto is forwarded, the image never redirects to an absolute http URL - proven on a running container.

## Context

absolute_redirect off in the server block turns every nginx-generated Location into a path, so a redirect is scheme-agnostic whichever side of the terminator it crosses; port_in_redirect off beside it keeps the published port out as well. Proof is the real image in fixtures mode on port 18082 answering GET /assets (no trailing slash) with a Location that starts with a slash and no scheme, and eval_1 rendering the template through nginx -t as the hardening leaf did. The README section sits under Configure a deployment after the headers paragraph and says in plain words what the image does NOT do - no 443, no HSTS, no redirect to https - and what the terminator must do.

## Behavior

- **B-1** — GIVEN the real image in fixtures mode WHEN GET /assets without a trailing slash is requested THEN the 301 Location is a path, not an absolute http URL
- **B-2** — GIVEN nginx.conf WHEN it is read THEN it declares absolute_redirect off, listens on 80 only and names no Strict-Transport-Security
- **B-3** — GIVEN the README WHEN it is read THEN a section names the external terminator, X-Forwarded-Proto and where HSTS is set

## Success Criteria

```bash
# eval_1: the real image renders the template and accepts it
eval_1() {
  ( cd front && docker run --rm -e CLICKHOUSE_UPSTREAM=http://127.0.0.1:1 -e APEX_API_UPSTREAM=http://127.0.0.1:1 -e 'NGINX_ENVSUBST_FILTER=^(CLICKHOUSE_UPSTREAM|APEX_API_UPSTREAM)$' -v "$PWD/nginx.conf:/etc/nginx/templates/default.conf.template:ro" nginx:1.27-alpine nginx -t )
}

# eval_2: a live container redirects with a relative Location
eval_2() {
  ( cd front && docker rm -f apex-console-tls-eval > /dev/null 2>&1; docker build -q --target prod -t apex-console:tls-eval . > /dev/null && docker run -d --rm --name apex-console-tls-eval -p 18082:80 -e DATA_SOURCE=fixtures apex-console:tls-eval > /dev/null && sleep 2 && R="$(curl -sI http://127.0.0.1:18082/assets)"; docker rm -f apex-console-tls-eval > /dev/null; echo "$R" | grep -q "301" && echo "$R" | grep -qi "^location. /assets/" && ! echo "$R" | grep -qi "^location. http" )
}

# eval_3: the config and the docs say what the image does and does not do
eval_3() {
  ( cd front && grep -q "absolute_redirect off" nginx.conf && grep -q "port_in_redirect off" nginx.conf && test "$(grep -c '^  listen ' nginx.conf)" = 1 && ! grep -q "Strict-Transport-Security" nginx.conf && grep -q "X-Forwarded-Proto" README.md && grep -qi "terminator" README.md )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the real image renders the template and accepts it"
    runnable: bash
    check_type: deterministic
    verifies: [B-2]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "a live container redirects with a relative Location"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 180
  - id: eval_3
    description: "the config and the docs say what the image does and does not do"
    runnable: bash
    check_type: deterministic
    verifies: [B-2, B-3]
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

- A 443 listener or a certificate path in the image; option A was not chosen.
- Strict-Transport-Security from the plain listener.
- A redirect from http to https inside the image; that is the terminator's.

## Do-Not-Touch

- `front/Dockerfile`
- `front/docker-entrypoint.d`
- `front/src`

## Open Questions

(none — this task is fully specified)
