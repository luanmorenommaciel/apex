---
id: T-20261019-query-cache-dedupe-abort
title: "Dedupe, cache and abort the console's reads"
status: in-progress
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-screen-component-tests, T-20261019-browser-door-additive-columns]
supersedes: (none)
touches_paths: [front/src/data/useRepository.tsx, front/src/data/repository.ts, front/src/data/http.ts, front/src/screens/RunDetailScreen.tsx, front/src/screens/FindingScreen.tsx, front/src/screens/CompareScreen.tsx, front/src/screens/MemoryScreen.tsx, front/src/screens/RunsScreen.tsx]
creates_paths: [front/src/data/useAsync.test.tsx]
source_note: "front/src/data/useRepository.tsx useAsync (no cache, no dedupe, no AbortSignal), RunDetailScreen.tsx 8 useAsync calls, CompareScreen.tsx 8, FindingScreen.tsx 6, clickhouse.ts query() accepts a signal nobody passes, http.ts apiGet() accepts none"
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

# Dedupe, cache and abort the console's reads

> **Why:** useAsync starts a fetch per call site per mount and never cancels. RunDetail issues eight reads on every visit and Compare eight more; opening a finding from a run refetches the four reads the run just made; under React StrictMode every one of them runs twice; and a response that lands after navigation is only dropped by a boolean, the request itself runs to completion against ClickHouse or the API.

## Goal

Concurrent callers of the same read share one request, a read repeated within a short window is served from memory, an unmounted or superseded read is aborted at the fetch, and a test counts repository calls to prove each, including that a StrictMode mount of RunDetail issues each read once.

## Context

Replace the body of useAsync with a small keyed cache owned by the repository instance - a Map from key to entry holding the promise, the settled value, its timestamp and an AbortController - where the key is the method name plus its JSON-encoded arguments; callers pass the key explicitly or useAsync derives it from a method-and-args form so RunDetail and Finding share entries. In flight means one promise, settled within the TTL means the value, otherwise a new request. Proposed TTL, open for review - 30 seconds; the console is read-only and new runs arrive on the order of minutes. Every Repository method gains an optional trailing signal parameter, forwarded to clickhouse.ts query() and to a new signal parameter on http.ts apiGet() and fetch; FixtureRepository ignores it. On unmount or deps change the hook aborts the controller only when no other subscriber holds the entry. The serve parity test reads Repository method names with a regex that stops at the opening parenthesis, so the extra parameter does not break it. The test file wraps FixtureRepository in a counting Proxy, mounts RunDetailScreen under StrictMode through the memory router, and asserts each method was called once; mounts two components with the same key and asserts one call; and stubs a fetch that observes its signal to assert abort on unmount for ClickHouseRepository and HttpRepository.

## Behavior

- **B-1** — GIVEN two components mounting the same read at the same time WHEN both resolve THEN the repository method ran once
- **B-2** — GIVEN a component unmounted before its read settles WHEN the fetch's signal is inspected THEN it is aborted, and no state update follows
- **B-3** — GIVEN RunDetailScreen mounted under StrictMode against a counting repository WHEN it settles THEN run, stages, jobConf, findings and transitions were each called once
- **B-4** — GIVEN a read settled within the TTL WHEN another screen asks for the same key THEN the value is served without a repository call

## Success Criteria

```bash
# eval_1: the cache, dedupe and abort tests pass
eval_1() {
  ( cd front && npx vitest --run src/data/useAsync.test.tsx )
}

# eval_2: the screen tests from the regression net still pass and the API client forwards a signal
eval_2() {
  ( cd front && npx vitest --run src/screens src/data && grep -q "signal" src/data/http.ts )
}

# eval_3: the whole front gate stays green
eval_3() {
  ( cd front && npm run typecheck && npm run lint && npm test -- --run && npm run build )
}

# eval_4: serve still finds every Repository method by name
eval_4() {
  ( cd serve && uv run --extra dev pytest tests/test_api_resources.py -q -p no:warnings -k repository_method )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the cache, dedupe and abort tests pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3, B-4]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "the screen tests from the regression net still pass and the API client forwards a signal"
    runnable: bash
    check_type: deterministic
    verifies: [B-2]
    terminal: true
    expected_duration_sec: 60
  - id: eval_3
    description: "the whole front gate stays green"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 90
  - id: eval_4
    description: "serve still finds every Repository method by name"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
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
eval_1 && eval_2 && eval_3 && eval_4
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Adding a data-fetching library - the hook's deps list stays honest and the dependency set stays three packages.
- A module-level cache that survives a repository swap - the cache belongs to the instance.
- Caching a rejected read; an error is retried on the next mount.
- Removing a Repository method or renaming one - serve pins the names.

## Do-Not-Touch

- `serve`
- `front/src/data/queries.ts`
- `front/src/data/fixtures.ts`
- `front/src/contract`

## Open Questions

(none — this task is fully specified)
