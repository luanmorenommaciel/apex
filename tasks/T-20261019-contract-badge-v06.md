---
id: T-20261019-contract-badge-v06
title: "Report the contract version the repository actually declares"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [front/src/contract/types.ts, front/src/components/molecules/NavBar.test.tsx]
creates_paths: [front/src/contract/version.test.ts]
source_note: "CONTRACT.md line 7 (contract v0.6), front/src/contract/types.ts line 8 (CONTRACT_VERSION 0.5), front/README.md line 4 (reads the contract v0.6 tables)"
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

# Report the contract version the repository actually declares

> **Why:** The header badge renders CONTRACT_VERSION, which is the string 0.5 in front/src/contract/types.ts, while CONTRACT.md, README.md and front/README.md all say v0.6. The console tells every visitor it reads an older contract than the one it was written against, and nothing fails when the two drift.

## Goal

CONTRACT_VERSION is 0.6, the NavBar renders contract v0.6, and a test reads CONTRACT.md and fails the moment the two versions differ again.

## Context

v0.6 is additive only - an optional execution_id on the apex.stage payload that no ClickHouse schema and no console read consumes (CONTRACT.md changelog). So the change is the constant, the file header that calls the row shapes v0.5, and a drift test in front/src/contract/version.test.ts that reads ../../../CONTRACT.md with node fs and asserts the line that says contract **v0.6** carries CONTRACT_VERSION. The prose in RunDetailScreen, DualVerdictPanel, LayerTabs and rules.ts that says what v0.5 does NOT carry stays true for v0.6 and is not rewritten. The existing NavBar test gains one assertion on the badge text.

## Behavior

- **B-1** — GIVEN CONTRACT.md declaring contract v0.6 WHEN the version test runs THEN it passes because CONTRACT_VERSION is 0.6, and it fails when either side moves alone
- **B-2** — GIVEN the NavBar mounted with any repository kind WHEN its text is read THEN it contains contract v0.6 and not v0.5

## Success Criteria

```bash
# eval_1: the version test and the NavBar test pass
eval_1() {
  ( cd front && npx vitest --run src/contract/version.test.ts src/components/molecules/NavBar.test.tsx )
}

# eval_2: the constant and the header say 0.6 and the test reads CONTRACT.md rather than restating it
eval_2() {
  ( cd front && grep -q 'CONTRACT_VERSION = "0.6"' src/contract/types.ts && ! grep -q "contract, v0.5" src/contract/types.ts && grep -q "CONTRACT.md" src/contract/version.test.ts )
}

# eval_3: the whole front gate stays green
eval_3() {
  ( cd front && npm run typecheck && npm run lint && npm test -- --run )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the version test and the NavBar test pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "the constant and the header say 0.6 and the test reads CONTRACT.md rather than restating it"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 5
  - id: eval_3
    description: "the whole front gate stays green"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
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

- Hardcoding 0.6 in the test instead of reading CONTRACT.md, which is the drift this leaf exists to catch.
- Rewriting screen prose that says what v0.5 lacks - v0.6 lacks the same things.
- Adding execution_id to SparkEventRow - no read path consumes it and CONTRACT.md says consumers ignore it.

## Do-Not-Touch

- `front/src/screens`
- `front/src/data`
- `CONTRACT.md`

## Open Questions

(none — this task is fully specified)
