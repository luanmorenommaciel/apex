---
id: T-20261019-screen-component-tests
title: "Give Runs, RunDetail, Finding, Compare and Memory a component test each"
status: done
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: []
creates_paths: [front/src/screens/RunsScreen.test.tsx, front/src/screens/RunDetailScreen.test.tsx, front/src/screens/FindingScreen.test.tsx, front/src/screens/CompareScreen.test.tsx, front/src/screens/MemoryScreen.test.tsx]
source_note: "front/src/screens (five screens with no test beside them), front/src/screens/VerifyScreen.source-state.test.tsx and QueryFailure.test.tsx (the convention - jsdom, react act, createMemoryRouter, FixtureRepository, vi.mock of useRepository)"
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
signed_off_at: 2026-10-19T15:44:21Z
accepted: true
accepted_by: agmarcastro
accepted_at: 2026-10-19T15:47:43Z
signed_off_sig: hmac-sha256-v3:60832560:fb40f204bcee2da5828445b71bb18da1452a4116c1d5b3754bbb4bc07ac12a2e
accepted_tier: 1
accepted_attempt_id: fcc95645-ce63-4d04-a676-8160722416f9
accepted_authorization_ref: hmac-sha256-v3:60832560:fb40f204bcee2da5828445b71bb18da1452a4116c1d5b3754bbb4bc07ac12a2e
acceptance_record_digest: sha256:e127c0ebe560c60af49922d3beaf2656b9e085357ec3abf7ecef6201de0b37f3
---

# Give Runs, RunDetail, Finding, Compare and Memory a component test each

> **Why:** Five of the seven screens have no component test. The accessibility, caching and bundle leaves that follow all change how these screens mount and fetch, and without a test there is nothing to say a screen still renders the recording after them.

## Goal

Each of the five screens has a test in the existing convention that mounts it against FixtureRepository through a memory router, asserts the recorded data appears, asserts a rejected query renders QueryFailure with the source name, and asserts nothing private leaks from an error, so later leaves have a regression net.

## Context

Follow VerifyScreen.source-state.test.tsx - the @vitest-environment jsdom pragma, IS_REACT_ACT_ENVIRONMENT, createRoot plus act, createMemoryRouter with the screen's route, the hoisted vi.mock of useRepository, and FixtureRepository as the data. Assert on text the user sees (job ids from fixtures CURRENT_JOB and BASELINE_JOB, the finding type, PLAN_FINGERPRINT) and never on class names, so the a11y leaf can change markup. For the failure case wrap FixtureRepository in a Proxy that rejects one method with an Error whose message is marked PRIVATE and assert the message is absent from the page while the source badge name is present, as QueryFailure.test.tsx does. CompareScreen takes job ids from the query string; mount it at /compare?current=CURRENT_JOB&baseline=BASELINE_JOB and once with no params. MemoryScreen defaults to the most-run shape; assert the fingerprint and a shape run row. RunsScreen has a search input - type into it through act and assert the list filters. Keep each file under the size of the Verify test; two or three cases per screen is the goal, not coverage of every branch.

## Behavior

- **B-1** — GIVEN each of the five screens mounted against FixtureRepository WHEN the data resolves THEN the recorded run, finding, comparison or shape is on the page
- **B-2** — GIVEN a repository whose read rejects with a private message WHEN the screen renders THEN QueryFailure names the source and the private message is not on the page
- **B-3** — GIVEN RunsScreen with text typed into its search WHEN the list re-renders THEN only matching runs remain

## Success Criteria

```bash
# eval_1: all five test files exist and pass
eval_1() {
  ( cd front && for s in RunsScreen RunDetailScreen FindingScreen CompareScreen MemoryScreen; do test -f "src/screens/$s.test.tsx" || exit 1; done && npx vitest --run src/screens )
}

# eval_2: the whole front gate stays green, including lint on the new tests
eval_2() {
  ( cd front && npm run typecheck && npm run lint && npm test -- --run )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "all five test files exist and pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 60
  - id: eval_2
    description: "the whole front gate stays green, including lint on the new tests"
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
eval_1 && eval_2
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Adding a testing library - the convention is react-dom act and querySelector, and the repo has no @testing-library.
- Asserting on Tailwind class names.
- Changing a screen to make it testable; if one cannot be mounted, park with the reason.

## Do-Not-Touch

- `front/src/screens/RunsScreen.tsx`
- `front/src/screens/RunDetailScreen.tsx`
- `front/src/screens/FindingScreen.tsx`
- `front/src/screens/CompareScreen.tsx`
- `front/src/screens/MemoryScreen.tsx`
- `front/src/data`
- `front/src/components`

## Open Questions

(none — this task is fully specified)
