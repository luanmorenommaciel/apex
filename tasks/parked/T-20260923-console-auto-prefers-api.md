---
id: T-20260923-console-auto-prefers-api
title: "Let auto reach the API without an absolute apiUrl"
status: parked
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [front/src/data/repository.ts, front/src/data/httpRepository.test.ts]
creates_paths: []
source_note: "front/src/data/repository.ts"
created: "2026-09-23T00:00:00Z"
tags: []
owner: (none)
priority: P2
severity: feature
due_date: (none)
precondition: (none)
blocked_reason: superseded on 2026-09-29 by fab6620 on the base, which made auto probe the same-origin API with different semantics (a 401 selects the API)
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

# Let auto reach the API without an absolute apiUrl

> **Why:** resolveRepository() only probes the API when runtimeConfig.apiUrl is set, and T-20260921 made the correct configuration one where apiUrl is EMPTY so the browser stays same-origin. So auto never chooses the API - the one data source that needs no database user is the one auto skips - and .env.example's promise that auto "prefers the API when one is configured and answering" is false for every documented setup. The fix makes that sentence true; the file is not edited here, T-20260923-console-http-deployment-wiring owns it.

## Goal

In auto mode the console probes /v1/health at the same base HttpRepository would use - relative when apiUrl is empty - and prefers the API when it answers 200; ClickHouse-mode and fixtures deployments still resolve as they do today, because their /v1/health does not answer 200.

## Context

apiPing() already builds its target from base(), so with apiUrl empty it already probes /v1/health relative; only the guard in resolveRepository is wrong. Dropping the guard is safe on every existing deployment - the production image forwards /v1 to APEX_API_UPSTREAM, which defaults to the unroutable http://127.0.0.1:1, so a ClickHouse-mode container answers the probe with 502 and auto moves on; the Vite dev server with nothing on the proxy target answers 500 for the same effect. The order stays API, then ClickHouse, then fixtures. The probe must stay TOKENLESS - health is public, and a credential on a probe is a credential sent before anyone asked for it - and only 200 is a yes; a 401 on a public route is a misconfiguration, not an answering API. One proposed choice, open for review - RepositoryProvider renders nothing until resolveRepository settles, so a proxy that hangs would hold the whole console blank; apiPing already accepts an AbortSignal, and passing AbortSignal.timeout(2000) from the resolver bounds that without touching http.ts. The 2000 is a proposal, not a requirement.

## Behavior

- **B-1** — GIVEN dataSource auto and an empty apiUrl WHEN /v1/health answers 200 THEN resolveRepository returns an HttpRepository, and the only request issued before that decision was one relative probe of /v1/health with no Authorization header
- **B-2** — GIVEN dataSource auto WHEN /v1/health fails to connect, or answers 500, 502 or 401 THEN resolution continues to the ClickHouse ping and then fixtures, exactly as today
- **B-3** — GIVEN dataSource http WHEN the repository is resolved THEN no probe is issued - pinned stays pinned
- **B-4** — GIVEN dataSource auto and an absolute apiUrl WHEN the repository is resolved THEN the probe goes to that absolute base, unchanged from today
- **B-5** — GIVEN the change WHEN the tree is diffed THEN no file under front/src/screens or front/src/components changed

## Success Criteria

```bash
# eval_1: auto prefers an answering API, relative or absolute, and moves on when it does not answer
eval_1() {
  ( cd front && npm run test -- --run src/data/httpRepository.test.ts -t "auto" )
}

# eval_2: pinned http still issues no probe
eval_2() {
  ( cd front && npm run test -- --run src/data/httpRepository.test.ts -t "does not probe when pinned" )
}

# eval_3: types check and no screen moved
eval_3() {
  ( cd front && npm run typecheck && git diff --exit-code --stat -- src/screens src/components )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "auto prefers an answering API, relative or absolute, and moves on when it does not answer"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-4]
    terminal: true
    expected_duration_sec: 120
  - id: eval_2
    description: "pinned http still issues no probe"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
    terminal: true
    expected_duration_sec: 120
  - id: eval_3
    description: "types check and no screen moved"
    runnable: bash
    check_type: deterministic
    verifies: [B-5]
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

- Sending the token on the probe; health is public and the token belongs on data requests only.
- Treating a 401 from /v1/health as "the API is there"; it is a misconfigured API and auto must not commit to it.
- Falling back to ClickHouse after the API was chosen and a later call returns 401; that is the silent restoration T-20260920-console-http-repository forbids.
- A test whose stubbed fetch answers 200 to everything, which proves nothing about which probe ran first.

## Do-Not-Touch

- `front/src/data/http.ts`
- `front/src/screens/`
- `front/src/components/`

## Open Questions

(none — this task is fully specified)
