---
id: T-20261019-fixtures-lazy-chunk
title: "Keep the recorded run out of the entry bundle"
status: done
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [front/src/data/repository.ts, front/src/data/repository.test.ts]
creates_paths: []
source_note: "front/src/data/fixtures.ts (1633 lines), front/src/data/repository.ts line 13 (static import * as fx), baseline build dist/assets/index-*.js 342.7 kB containing app-20260803014217-0071"
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
signed_off_at: 2026-10-19T15:52:02Z
accepted: true
accepted_by: agmarcastro
accepted_at: 2026-10-19T15:52:14Z
signed_off_sig: hmac-sha256-v3:60832560:4197a1479be11fdbdf77f380d98e870d9cec8564bb9e1f1c4e4de5c7ccc59d23
accepted_tier: 1
accepted_attempt_id: 81fd76e4-98cf-4328-b5ab-dc4c6fc62eb8
accepted_authorization_ref: hmac-sha256-v3:60832560:4197a1479be11fdbdf77f380d98e870d9cec8564bb9e1f1c4e4de5c7ccc59d23
acceptance_record_digest: sha256:6f7b0156e587d4682d90088aa2f82e5561584cd6cde2aa7aa6f4cebec64d30d8
---

# Keep the recorded run out of the entry bundle

> **Why:** repository.ts imports fixtures.ts statically, so the 1633-line recording is in the entry chunk of every deployment, including the http and clickhouse ones that never read it.

## Goal

A production build emits the recording as its own chunk that only FixtureRepository loads, the entry chunk no longer contains it, and FixtureRepository returns the same rows as before.

## Context

FixtureRepository replaces the static import with one memoised dynamic import - a private load() returning the module promise - and each method awaits it; the methods are already async so no signature changes and the serve parity test that reads Repository method names is unaffected. Vite names the chunk after the module, so eval_1 looks for dist/assets/fixtures-*.js. The default RepoContext value in useRepository.tsx (new FixtureRepository()) stays, as constructing it loads nothing. Tests that import fixtures directly (rules.test.ts, VerifyScreen.source-state.test.tsx) keep doing so - they are tests, not the bundle.

## Behavior

- **B-1** — GIVEN a production build WHEN the entry chunk is searched for the recorded job id THEN it is absent, and a fixtures chunk contains it
- **B-2** — GIVEN FixtureRepository WHEN listRuns, run, stages, findings, planShapes, shapeRuns and fixVerification are called THEN they return the same rows as before the change

## Success Criteria

```bash
# eval_1: the recording is its own chunk and the entry chunk is free of it
eval_1() {
  ( cd front && npm run build > /dev/null && ! grep -q "2de5e5760399189a81ab5500a216db0bae5c67f72cf42c08bd9f62689b404cf0" dist/assets/index-*.js && grep -lq "2de5e5760399189a81ab5500a216db0bae5c67f72cf42c08bd9f62689b404cf0" dist/assets/fixtures-*.js )
}

# eval_2: the repository tests and the whole front gate stay green
eval_2() {
  ( cd front && npm run typecheck && npm run lint && npm test -- --run )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the recording is its own chunk and the entry chunk is free of it"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 60
  - id: eval_2
    description: "the repository tests and the whole front gate stay green"
    runnable: bash
    check_type: deterministic
    verifies: [B-2]
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
eval_1 && eval_2
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Splitting with a manualChunks rule in vite.config.ts - the dynamic import is the boundary, and the config would hide it.
- Changing Repository method signatures.

## Do-Not-Touch

- `front/src/data/fixtures.ts`
- `front/src/screens`
- `front/vite.config.ts`

## Open Questions

(none — this task is fully specified)
