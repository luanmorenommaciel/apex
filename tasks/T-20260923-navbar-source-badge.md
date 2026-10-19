---
id: T-20260923-navbar-source-badge
title: "Name the http source in the console header"
status: in-progress
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [front/src/components/molecules/NavBar.tsx]
creates_paths: [front/src/components/molecules/NavBar.test.tsx]
source_note: "front/src/components/molecules/NavBar.tsx"
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

# Name the http source in the console header

> **Why:** NavBar.tsx:39-43 is a two-way branch - clickhouse, else "source ◐ fixtures". With the http data source every row on screen came from apex-api and the header says the data is the recorded run. On a console whose whole argument is that it does not overclaim, the badge overclaims in the other direction. It was left this way because front/src/components was do-not-touch for every unit in this plan.

## Goal

The header renders one label per Repository kind - clickhouse, http naming apex-api, fixtures - through an exhaustive map, so a fourth kind is a type error rather than a fallthrough; a mounted test asserts each label.

## Context

NavBar reads repo.kind from useRepository(), and VerifyScreen.source-state.test.tsx already shows the pattern for mounting a component under jsdom with useRepository mocked to a chosen repository. A Record keyed on Repository["kind"] is what makes the map exhaustive under tsc. One proposed choice, open for the visual owner - http is live data, so it takes the same "●" certified tone clickhouse has, and fixtures keeps "◐" withheld; the ratified identity (modelo/Apex Console Visual Identity.pdf) has a semantic palette and this follows it, but the reviewer decides.

## Behavior

- **B-1** — GIVEN a repository whose kind is http WHEN NavBar mounts THEN the header names http and apex-api and does not say fixtures
- **B-2** — GIVEN a repository whose kind is clickhouse or fixtures WHEN NavBar mounts THEN the header text is what it is today
- **B-3** — GIVEN a kind added to Repository["kind"] without a label WHEN tsc runs THEN it fails

## Success Criteria

```bash
# eval_1: each kind renders its own label
eval_1() {
  ( cd front && npm run test -- --run src/components/molecules/NavBar.test.tsx )
}

# eval_2: the map is exhaustive and lints clean
eval_2() {
  ( cd front && npm run typecheck && npm run lint )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "each kind renders its own label"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 120
  - id: eval_2
    description: "the map is exhaustive and lints clean"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
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
eval_1 && eval_2
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- A third else-if; the next kind falls through exactly as this one did.
- Reading runtimeConfig.dataSource instead of repo.kind; auto resolves to a kind, and the header must say what was resolved.

## Do-Not-Touch

- `front/src/screens/`
- `front/src/data/`

## Open Questions

(none — this task is fully specified)
