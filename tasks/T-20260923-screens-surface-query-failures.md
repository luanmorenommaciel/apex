---
id: T-20260923-screens-surface-query-failures
title: "Show a failed query on every screen, and name a rejected token"
status: in-progress
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [front/src/screens/RunsScreen.tsx, front/src/screens/RunDetailScreen.tsx, front/src/screens/CompareScreen.tsx, front/src/screens/MemoryScreen.tsx, front/src/screens/FindingScreen.tsx, front/src/components/molecules/index.ts]
creates_paths: [front/src/components/molecules/QueryFailure.tsx, front/src/screens/QueryFailure.test.tsx]
source_note: "front/src/data/useRepository.tsx"
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

# Show a failed query on every screen, and name a rejected token

> **Why:** useAsync returns error and four screens never read it - RunDetail, Compare, Memory and Finding render a rejected query as an empty store. With the http source that turns a wrong APEX_API_TOKEN into a console that looks connected and empty, and it turns the API's 502 memory_unavailable - which says there is no TABLE - into MemoryScreen's "nothing indexed yet", which says there is no HISTORY. RunsScreen does render the error, labelled "ClickHouse did not answer" whatever the source was. T-20260920-console-http-repository's B-4, "the console reports an authentication failure", is proven at the repository layer and nowhere a person looks.

## Goal

One QueryFailure molecule, rendered by the five screens whenever a query rejects and before any empty state; an ApiAuthError renders as a token problem naming APEX_API_TOKEN; an ApiError renders the API's detail; anything else renders a generic line; the source it names follows repo.kind. VerifyScreen keeps its own SourceState untouched.

## Context

The molecule reads the same AsyncState the screens already hold, so the change per screen is a render, not a data-flow change. Order matters on MemoryScreen - the failure must render before the "nothing indexed yet" branch, which today swallows it. ApiAuthError and ApiError are exported from http.ts and instanceof-checkable; neither carries the token. What text to show is a proposed choice, open for review, and it follows VerifyScreen's caution - VerifyScreen.error-state.test.ts asserts that a rejection's message never reaches the DOM, because a response body can carry text. So the molecule shows an ApiError's status and detail, which ch._sanitize already stripped of connection details server-side, and a fixed line for any other Error; RunsScreen's verbatim error.message goes away with this. VerifyScreen and useVerifyQuery are do-not-touch - their SourceState is a deliberate design with its own tests, and this leaf must not fork it. QueryFailure.test.tsx mounts each of the five screens with useRepository mocked to a repository whose methods reject, the way VerifyScreen.source-state.test.tsx mounts VerifyScreen.

## Behavior

- **B-1** — GIVEN a repository whose method rejects with ApiAuthError WHEN each of RunsScreen, RunDetailScreen, CompareScreen, MemoryScreen and FindingScreen mounts THEN the screen shows a token-rejected notice naming APEX_API_TOKEN, and none of its empty-state copy renders in its place
- **B-2** — GIVEN planShapes rejecting with an ApiError whose detail begins memory_unavailable WHEN MemoryScreen mounts THEN it shows that detail and not "nothing indexed yet"
- **B-3** — GIVEN a repository whose method rejects with a plain Error carrying a secret in its message WHEN a screen mounts THEN a failure notice renders and the secret does not appear in the DOM
- **B-4** — GIVEN a repository whose kind is http WHEN a failure notice renders THEN it names apex-api and never says ClickHouse
- **B-5** — GIVEN VerifyScreen and useVerifyQuery WHEN the tree is diffed and their tests run THEN neither file changed and both suites pass

## Success Criteria

```bash
# eval_1: every screen surfaces a rejection, names the token, and hides an untrusted message
eval_1() {
  ( cd front && npm run test -- --run src/screens/QueryFailure.test.tsx )
}

# eval_2: VerifyScreen's own design is untouched
eval_2() {
  ( cd front && npm run test -- --run src/screens/VerifyScreen.error-state.test.ts src/screens/VerifyScreen.source-state.test.tsx && git diff --exit-code --stat -- src/screens/VerifyScreen.tsx src/screens/useVerifyQuery.ts )
}

# eval_3: types and lint
eval_3() {
  ( cd front && npm run typecheck && npm run lint )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "every screen surfaces a rejection, names the token, and hides an untrusted message"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3, B-4]
    terminal: true
    expected_duration_sec: 180
  - id: eval_2
    description: "VerifyScreen's own design is untouched"
    runnable: bash
    check_type: deterministic
    verifies: [B-5]
    terminal: true
    expected_duration_sec: 180
  - id: eval_3
    description: "types and lint"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
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

- Catching inside useAsync and resolving to [] or null; that is the fault-as-empty-store this leaf removes.
- Rendering error.message verbatim for a non-API error; VerifyScreen's tests exist because a body can carry text.
- Five copies of a banner, one per screen; the molecule is the point.
- Reworking VerifyScreen's SourceState to use the molecule; it is do-not-touch here and has its own design.

## Do-Not-Touch

- `front/src/screens/VerifyScreen.tsx`
- `front/src/screens/useVerifyQuery.ts`
- `front/src/data/`

## Open Questions

(none — this task is fully specified)
