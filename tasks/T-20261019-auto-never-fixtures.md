---
id: T-20261019-auto-never-fixtures
title: "Stop auto from serving the recording as production data"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-tls-external-terminator]
supersedes: (none)
touches_paths: [front/src/data/repository.ts, front/src/data/useRepository.tsx, front/src/data/httpRepository.test.ts, front/src/data/entrypoint.test.ts, front/src/components/molecules/index.ts, front/docker-entrypoint.d/30-apex-console-config.sh, front/README.md, front/.env.example]
creates_paths: [front/src/components/molecules/StoreUnreachable.tsx, front/src/data/resolveRepository.test.ts]
source_note: "D-auto-fallback-policy, option A; front/src/data/repository.ts resolveRepository() (auto falls through to FixtureRepository), front/docker-entrypoint.d/30-apex-console-config.sh (auto with no store is refused at boot, auto with an unreachable store is not), front/src/data/httpRepository.test.ts (the selection tests)"
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

# Stop auto from serving the recording as production data

> **Why:** In auto, when the API and ClickHouse both fail to answer, the console shows the recorded gate run with only a small header badge to say so. A production visitor sees a run that never happened on their cluster.

## Goal

auto resolves to the API, then ClickHouse, and otherwise to a named failure screen that lists what was probed and how to pin a source; FixtureRepository is reachable only through DATA_SOURCE=fixtures; the entrypoint's auto message and the docs say so.

## Context

resolveRepository returns a discriminated result - a Repository, or an unreachable record carrying the two probe outcomes - and RepositoryProvider renders StoreUnreachable instead of mounting the app when it is the latter. StoreUnreachable is a molecule exported from the index like QueryFailure, names /v1/health and /clickhouse/ping as what was asked, and says to set DATA_SOURCE to http, clickhouse or fixtures deliberately. httpRepository.test.ts has the selection tests for resolveRepository and its "falls back to fixtures" case changes meaning; the new resolveRepository.test.ts covers the unreachable branch and that fixtures still resolves on DATA_SOURCE=fixtures. The dev server keeps the same rule; developers who want the recording set VITE_DATA_SOURCE=fixtures, which make up-fixtures does. The entrypoint's auto-with-API-only warning stops promising the recorded run. The screen component tests mock useRepository and are untouched.

## Behavior

- **B-1** — GIVEN DATA_SOURCE=auto with both probes failing WHEN the app boots THEN StoreUnreachable renders, naming /v1/health and /clickhouse/ping, and no FixtureRepository is constructed
- **B-2** — GIVEN DATA_SOURCE=fixtures WHEN the app boots THEN FixtureRepository is used, as before
- **B-3** — GIVEN the entrypoint in auto with only the API configured WHEN it writes its warning THEN the warning no longer promises the recorded run as a fallback

## Success Criteria

```bash
# eval_1: the resolution tests pass
eval_1() {
  ( cd front && npx vitest --run src/data/resolveRepository.test.ts src/data/httpRepository.test.ts )
}

# eval_2: the entrypoint and docs stop promising the recording
eval_2() {
  ( cd front && ! grep -q "shows the recorded run" docker-entrypoint.d/30-apex-console-config.sh && ! grep -q "falls back to fixtures" .env.example && ! grep -q "falls back to the recorded" README.md && grep -qi "no store answered" README.md )
}

# eval_3: the whole front gate stays green
eval_3() {
  ( cd front && npm run typecheck && npm run lint && npm test -- --run && npm run build )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the resolution tests pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "the entrypoint and docs stop promising the recording"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
    terminal: true
    expected_duration_sec: 5
  - id: eval_3
    description: "the whole front gate stays green"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 90
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

- A banner over fixture data; that is option B, which was not chosen.
- Removing FixtureRepository or the fixtures mode.
- Catching a 401 from the API as "unreachable"; apiPing() already counts it as an API that exists.

## Do-Not-Touch

- `front/src/data/fixtures.ts`
- `front/src/screens`
- `front/nginx.conf`

## Open Questions

(none — this task is fully specified. Eval amended before sealing on 2026-10-19: the README was rewritten by D-api-only after this leaf was built and names the page by its words, "no store answered".)
