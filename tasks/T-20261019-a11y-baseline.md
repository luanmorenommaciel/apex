---
id: T-20261019-a11y-baseline
title: "Lint for accessibility and give every control a name"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-screen-component-tests, T-20261019-self-hosted-fonts]
supersedes: (none)
touches_paths: [front/package.json, front/package-lock.json, front/eslint.config.js, front/src/screens, front/src/components]
creates_paths: [front/src/screens/a11y.test.tsx]
source_note: "one aria-label in front/src (VerifyScreen.tsx line 421), no label or htmlFor anywhere, no jsx-a11y in eslint.config.js, RunsScreen.tsx lines 72 and 83 (status by colour class and StatusPill), Pill.tsx tones"
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

# Lint for accessibility and give every control a name

> **Why:** The console has one aria-label, no form label, status conveyed by colour alone in the runs list, and no lint rule that would notice the next one. A screen reader hears an unlabeled textbox and a list of coloured dots.

## Goal

eslint-plugin-jsx-a11y runs at error level in the lint gate and passes, every input and select in the screens has an accessible name, every status or severity that is a colour also reads as text, the nav and header are landmarks with names, and a test asserts the first two of those against the real screens.

## Context

Add eslint-plugin-jsx-a11y and its flat recommended config to eslint.config.js for src files at error level, run the lint, and fix what it reports - the errors are the work list. Then the things lint cannot see - the search input and filter in RunsScreen get a visible label or aria-label, the nav in NavBar gets aria-label Primary, the source and contract badges get a title, and StatusPill and the severity pills must contain the word, not only the tone (Pill already renders children; check each call site passes text and not an empty glyph). The a11y test mounts RunsScreen, CompareScreen and MemoryScreen against FixtureRepository and asserts every input and select has aria-label, aria-labelledby or an associated label element, and that each run row's status cell textContent contains healthy, warning or degraded. The screen tests from the previous leaf must still pass unchanged - they assert on text, not markup.

## Behavior

- **B-1** — GIVEN eslint.config.js with jsx-a11y recommended at error level WHEN npm run lint runs THEN it passes with zero warnings
- **B-2** — GIVEN RunsScreen, CompareScreen and MemoryScreen mounted WHEN their inputs and selects are enumerated THEN each has an accessible name
- **B-3** — GIVEN the runs list rows WHEN the status cell text is read THEN it contains the status word, not only a colour
- **B-4** — GIVEN the NavBar WHEN its nav element is read THEN it carries aria-label

## Success Criteria

```bash
# eval_1: the a11y plugin is wired at error level and lint passes
eval_1() {
  ( cd front && grep -q "jsx-a11y" eslint.config.js && grep -q "eslint-plugin-jsx-a11y" package.json && npm run lint )
}

# eval_2: the a11y test and the screen tests pass
eval_2() {
  ( cd front && npx vitest --run src/screens/a11y.test.tsx src/screens src/components )
}

# eval_3: the whole front gate stays green
eval_3() {
  ( cd front && npm run typecheck && npm test -- --run && npm run build )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the a11y plugin is wired at error level and lint passes"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 60
  - id: eval_2
    description: "the a11y test and the screen tests pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-2, B-3, B-4]
    terminal: true
    expected_duration_sec: 60
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

- Disabling a jsx-a11y rule to make lint pass instead of fixing the markup.
- aria-hidden on content a sighted user reads.
- Replacing a colour token with text - the text goes beside the colour, the palette is the ratified identity.

## Do-Not-Touch

- `front/tailwind.config.js`
- `front/src/data`
- `front/src/contract`

## Open Questions

(none — this task is fully specified)
