---
id: T-20261019-nginx-hardening
title: "Give the production nginx security headers, proxy timeouts and gzip"
status: in-progress
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-self-hosted-fonts]
supersedes: (none)
touches_paths: [front/nginx.conf, front/README.md]
creates_paths: []
source_note: "front/nginx.conf (one server block, listen 80, no add_header beyond Cache-Control on /config.js, no proxy timeouts, no gzip), front/Dockerfile (nginx 1.27-alpine, NGINX_ENVSUBST_FILTER)"
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
signed_off: true
signed_off_by: agmarcastro
signed_off_at: 2026-10-19T15:51:31Z
accepted: false
accepted_by: (none)
accepted_at: (none)
signed_off_sig: hmac-sha256-v3:60832560:6988089d4a1d60f184025eaf34778a132a3bd0c144b712f261fee144a847abcd
---

# Give the production nginx security headers, proxy timeouts and gzip

> **Why:** The image answers every request without a Content-Security-Policy, X-Content-Type-Options, Referrer-Policy or frame-ancestors restriction, forwards to ClickHouse and the API with nginx's default 60 second timeouts and no connect bound, and sends a 343 kB bundle uncompressed.

## Goal

Every response from the image carries a same-origin CSP and the standard hardening headers, the two proxies have explicit connect, send and read timeouts, hashed assets are cached immutably, text responses are gzipped, and a live container proves all of it.

## Context

nginx add_header is NOT inherited into a location that declares its own add_header, so the headers go in one snippet that the server block and the /config.js location both include, or are repeated in that location - otherwise /config.js, the one response that must not be cached, is also the one without a CSP. The policy is default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' (Bar.tsx, DataTable.tsx, SignalStrip.tsx, FindingScreen.tsx and MemoryScreen.tsx set style attributes, which style-src governs); img-src 'self' data:; font-src 'self' (possible only after the fonts leaf); connect-src 'self' (both doors are same-origin by design); frame-ancestors 'none'; base-uri 'self'; form-action 'self'. Also X-Content-Type-Options nosniff, Referrer-Policy strict-origin-when-cross-origin, X-Frame-Options DENY, Permissions-Policy denying camera, microphone and geolocation. No Strict-Transport-Security - the image terminates no TLS, see D-tls-termination. Proposed timeouts, open for review - proxy_connect_timeout 5s, proxy_send_timeout 30s, proxy_read_timeout 60s on both proxies; ClickHouse queries over a large spark_events may approach the read bound and the README should say which variable to raise. location /assets/ gets Cache-Control public, max-age one year, immutable - the file names are hashed. gzip on, gzip_types for text, css, js, json and svg, gzip_min_length 1024, gzip_vary on. The envsubst template keeps ${CLICKHOUSE_UPSTREAM} and ${APEX_API_UPSTREAM} as its only variables, so eval_1 renders it through the real image with nginx -t and eval_2 starts the prod image in fixtures mode on port 18080 and reads the headers with curl. The README table under Configure a deployment gains the headers and the timeout variables.

## Behavior

- **B-1** — GIVEN the template rendered by the nginx image WHEN nginx -t runs THEN the configuration is accepted
- **B-2** — GIVEN the prod image running in fixtures mode WHEN / and /config.js are requested THEN both carry Content-Security-Policy, X-Content-Type-Options nosniff, Referrer-Policy and X-Frame-Options, and /config.js still carries Cache-Control no-store
- **B-3** — GIVEN a request for / with Accept-Encoding gzip WHEN the response headers are read THEN Content-Encoding is gzip
- **B-4** — GIVEN nginx.conf WHEN both proxy locations are read THEN each declares proxy_connect_timeout, proxy_send_timeout and proxy_read_timeout

## Success Criteria

```bash
# eval_1: the real image renders the template and accepts it
eval_1() {
  ( cd front && docker run --rm -e CLICKHOUSE_UPSTREAM=http://127.0.0.1:1 -e APEX_API_UPSTREAM=http://127.0.0.1:1 -e 'NGINX_ENVSUBST_FILTER=^(CLICKHOUSE_UPSTREAM|APEX_API_UPSTREAM)$' -v "$PWD/nginx.conf:/etc/nginx/templates/default.conf.template:ro" nginx:1.27-alpine nginx -t )
}

# eval_2: a live container sends the headers on / and on /config.js and gzips the page
eval_2() {
  ( cd front && docker rm -f apex-console-hardening-eval > /dev/null 2>&1; docker build -q --target prod -t apex-console:hardening-eval . > /dev/null && docker run -d --rm --name apex-console-hardening-eval -p 18080:80 -e DATA_SOURCE=fixtures apex-console:hardening-eval > /dev/null && sleep 2 && H="$(curl -sI http://127.0.0.1:18080/)" && C="$(curl -sI http://127.0.0.1:18080/config.js)" && G="$(curl -sI -H 'Accept-Encoding:gzip' http://127.0.0.1:18080/)"; docker rm -f apex-console-hardening-eval > /dev/null; echo "$H" | grep -qi "^content-security-policy" && echo "$H" | grep -qi "nosniff" && echo "$H" | grep -qi "^referrer-policy" && echo "$H" | grep -qi "^x-frame-options" && echo "$C" | grep -qi "^content-security-policy" && echo "$C" | grep -qi "no-store" && echo "$G" | grep -qi "^content-encoding" )
}

# eval_3: both proxies carry the three timeouts and the hashed assets are immutable
eval_3() {
  ( cd front && test "$(grep -c proxy_read_timeout nginx.conf)" -ge 1 && test "$(grep -c proxy_connect_timeout nginx.conf)" -ge 1 && test "$(grep -c proxy_send_timeout nginx.conf)" -ge 1 && grep -q "immutable" nginx.conf && grep -q "gzip on" nginx.conf && ! grep -q "Strict-Transport-Security" nginx.conf )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the real image renders the template and accepts it"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "a live container sends the headers on / and on /config.js and gzips the page"
    runnable: bash
    check_type: deterministic
    verifies: [B-2, B-3]
    terminal: true
    expected_duration_sec: 180
  - id: eval_3
    description: "both proxies carry the three timeouts and the hashed assets are immutable"
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

- Proving the headers with a grep on nginx.conf instead of a running container - PR 129 shipped a config nginx rejected that way.
- Sending Strict-Transport-Security from a listener that is plain http.
- A CSP that names fonts.googleapis.com - the fonts leaf removed the need.
- Adding a variable to the template without extending NGINX_ENVSUBST_FILTER in the Dockerfile.

## Do-Not-Touch

- `front/docker-entrypoint.d`
- `front/src`
- `front/index.html`

## Open Questions

(none — this task is fully specified. Eval amended before sealing on 2026-10-19: D-api-only removed the /clickhouse proxy and the up-clickhouse target after this leaf was built, so the assertions that counted them were narrowed to what still exists; see tasks/.plans/front-lane-hardening.yaml.)
