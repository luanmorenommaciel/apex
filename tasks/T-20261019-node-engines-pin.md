---
id: T-20261019-node-engines-pin
title: "Pin one Node major across the image, CI and the host"
status: in-progress
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [front/package.json, front/Dockerfile, front/README.md]
creates_paths: [front/.nvmrc, front/engines.test.ts]
source_note: "front/Dockerfile lines 2 and 11 (node 20-alpine), .github/workflows/ci.yml line 44 (node 22), local node v25.6.1, npm ci EBADENGINE for jsdom 30.0.1 (requires ^22.22.2 || ^24.15.0 || >=26.0.0)"
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
signed_off_at: 2026-10-19T15:49:07Z
accepted: false
accepted_by: (none)
accepted_at: (none)
signed_off_sig: hmac-sha256-v3:60832560:1ee06e34977d305f5fd55de122b59f1f022546c4e89cf5ed14fa842e904e41ab
---

# Pin one Node major across the image, CI and the host

> **Why:** The image builds on Node 20, CI tests on 22 and the host runs 25. jsdom 30 refuses 20 and 25 outright, vite 8 and eslint 10 need 20.19 or 22.12 at least, and package.json declares no engines, so each environment finds out on its own and none of them agrees with the others.

## Goal

package.json declares an engines.node range that every devDependency accepts, .nvmrc and both Dockerfile stages name that major, CI already does, the README says which Node to use, and a test fails when any of the four drifts.

## Context

The tightest range among the installed devDependencies is jsdom's - ^22.22.2 || ^24.15.0 || >=26.0.0 - so the proposed engines.node is ^22.22.2 || ^24.15.0 and the pinned major is 22, the one CI already uses; node 22-alpine replaces node 20-alpine in both Dockerfile stages. The test in front/engines.test.ts reads package.json, .nvmrc, Dockerfile and ../.github/workflows/ci.yml, checks the three majors agree, and uses the semver package already in node_modules (6.3.1, transitive) to assert the engines range intersects every devDependency's own engines field - read from node_modules, not restated. vitest picks up a root-level test by its default include, and eslint lints src only, so the file needs no config change. engine-strict in an .npmrc would make npm ci refuse the host's Node 25 today - that is a proposed choice left open below, not applied here. The README gains one line under the install step naming the Node major and nvm use.

## Behavior

- **B-1** — GIVEN package.json after the change WHEN engines.node is read THEN it is a range jsdom, vite, eslint, vitest and typescript-eslint all accept, and Node 20 is outside it
- **B-2** — GIVEN .nvmrc, both Dockerfile FROM lines and ci.yml node-version WHEN their majors are compared THEN all name 22
- **B-3** — GIVEN the README WHEN it is read THEN it names the Node major and the nvmrc

## Success Criteria

```bash
# eval_1: the engines test passes against the real files
eval_1() {
  ( cd front && npx vitest --run engines.test.ts )
}

# eval_2: both image stages build on 22 and the nvmrc agrees
eval_2() {
  ( cd front && test "$(grep -c 'FROM node:22-alpine' Dockerfile)" = 2 && ! grep -q 'node:20' Dockerfile && grep -qx 22 .nvmrc && grep -q '"engines"' package.json && grep -q 'nvmrc\|Node 22' README.md )
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
    description: "the engines test passes against the real files"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 20
  - id: eval_2
    description: "both image stages build on 22 and the nvmrc agrees"
    runnable: bash
    check_type: deterministic
    verifies: [B-2, B-3]
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

- Restating each dependency's engines range in the test - read it from node_modules.
- Adding engine-strict to an .npmrc in this leaf; it is listed as an open choice.
- Touching .github/workflows/ci.yml - it is already on 22 and CI is billing-locked anyway.

## Do-Not-Touch

- `.github/workflows/ci.yml`
- `front/src`
- `front/nginx.conf`

## Open Questions

(none — this task is fully specified)
