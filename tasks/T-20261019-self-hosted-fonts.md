---
id: T-20261019-self-hosted-fonts
title: "Serve the three typefaces from the bundle instead of Google Fonts"
status: in-progress
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-node-engines-pin]
supersedes: (none)
touches_paths: [front/index.html, front/src/main.tsx, front/package.json, front/package-lock.json, front/README.md]
creates_paths: []
source_note: "front/index.html lines 16-21 (preconnect and stylesheet to fonts.googleapis.com and fonts.gstatic.com), front/tailwind.config.js fontFamily (JetBrains Mono, IBM Plex Sans, Archivo Black)"
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

# Serve the three typefaces from the bundle instead of Google Fonts

> **Why:** index.html loads JetBrains Mono, IBM Plex Sans and Archivo Black from fonts.googleapis.com and fonts.gstatic.com. An air-gapped deployment renders in fallback fonts, every visitor's browser contacts Google, and a Content-Security-Policy that keeps the console on its own origin cannot be written while those two hosts are in the page.

## Goal

The three families ship as woff2 in dist/assets, imported from the bundle, with the exact weights the design tokens use, and nothing in index.html or the CSS names a Google host.

## Context

@fontsource/jetbrains-mono (400, 500, 600, 700), @fontsource/ibm-plex-sans (400, 500, 600) and @fontsource/archivo-black (400) are the OFL packages that mirror what the Google stylesheet served; each weight is one side-effect import in src/main.tsx ahead of index.css. Vite emits the woff2 files into dist/assets with the family in the file name, which is what eval_2 looks for. tailwind.config.js keeps its fontFamily entries because the family names do not change. The two preconnect links and the stylesheet link leave index.html. The README design-tokens section gains one sentence saying the fonts are bundled and where from.

## Behavior

- **B-1** — GIVEN index.html and src/index.css after the change WHEN they are searched for Google Fonts hosts THEN neither names fonts.googleapis.com or fonts.gstatic.com
- **B-2** — GIVEN a production build WHEN dist/assets is listed THEN it holds woff2 files for jetbrains-mono, ibm-plex-sans and archivo-black
- **B-3** — GIVEN the tailwind font families WHEN tailwind.config.js is read THEN mono, sans and display still name the same three families

## Success Criteria

```bash
# eval_1: no Google Fonts host remains in the page or the stylesheet
eval_1() {
  ( cd front && ! grep -rq "fonts.googleapis\|fonts.gstatic" index.html src/index.css src/main.tsx )
}

# eval_2: the built assets carry the three families as woff2
eval_2() {
  ( cd front && npm run build > /dev/null && test -n "$(find dist/assets -iname "*jetbrains-mono*.woff2")" && test -n "$(find dist/assets -iname "*ibm-plex-sans*.woff2")" && test -n "$(find dist/assets -iname "*archivo-black*.woff2")" && grep -q "JetBrains Mono" tailwind.config.js && grep -q "IBM Plex Sans" tailwind.config.js && grep -q "Archivo Black" tailwind.config.js )
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
    description: "no Google Fonts host remains in the page or the stylesheet"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 5
  - id: eval_2
    description: "the built assets carry the three families as woff2"
    runnable: bash
    check_type: deterministic
    verifies: [B-2, B-3]
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

- Copying woff2 files into public/ by hand - the fontsource packages are versioned and licensed.
- Importing every weight of a family; the tokens use four, three and one.
- Changing font family names in tailwind.config.js.

## Do-Not-Touch

- `front/tailwind.config.js`
- `front/nginx.conf`
- `front/src/screens`
- `front/src/components`

## Open Questions

(none — this task is fully specified)
