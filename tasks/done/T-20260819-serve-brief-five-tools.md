---
id: T-20260819-serve-brief-five-tools
title: "Update the SERVE lane brief to the five-tool surface"
status: done
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260819-discover-docs]
touches_paths: [docs/lanes/SERVE.md]
creates_paths: []
source_note: "docs/lanes/SERVE-LEGS.md"
created: "2026-08-19T00:00:00Z"
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
signed_off_by: sidymar
signed_off_at: 2026-08-19T19:16:08Z
accepted: true
accepted_by: sidymar
accepted_at: 2026-08-19T19:16:23Z
signed_off_sig: hmac-sha256-v2:5153084e:977ef9e0a6578c10108557feeaa54e41149eabbfa1ecbaed8f084f16eb9ca9db
---

# Update the SERVE lane brief to the five-tool surface

> **Why:** The lane brief still states the server exposes four tools, which is now simply false; a brief that contradicts the code is worse than no brief.

## Goal

Bring SERVE.md's mission statement and T11 accept criterion to the current surface.

## Context

Split out of discover-docs because that unit's write surface was already at its M budget of three paths. The T1-T14 checklist records what L1 shipped and is history - only the counts that claim a present-tense surface change.

## Behavior

- **B-1** — GIVEN the mission statement WHEN read THEN it names five tools including list_runs, and the apex://runs resource
- **B-2** — GIVEN the T11 accept criterion WHEN read THEN it says five rather than four, with a note pointing at the leg that changed it
- **B-3** — GIVEN the T1 to T14 checklist WHEN read THEN it is otherwise unchanged, because it records what L1 shipped

## Success Criteria

```bash
# eval_1: the lane brief no longer claims a four-tool surface
eval_1() {
  ( ! grep -rniE 'four tools|exactly 4 tools' docs/lanes/SERVE.md )
}

# eval_2: the brief names list_runs and the resource, and keeps its checklist
eval_2() {
  ( grep -q 'list_runs' docs/lanes/SERVE.md && grep -q 'apex://runs' docs/lanes/SERVE.md && test "$(grep -c '^- \[ \] \*\*T' docs/lanes/SERVE.md)" -ge 14 )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the lane brief no longer claims a four-tool surface"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 5
  - id: eval_2
    description: "the brief names list_runs and the resource, and keeps its checklist"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-3]
    terminal: true
    expected_duration_sec: 5
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

- Rewriting the T1-T14 checklist; it is a record of what L1 shipped, not a live plan.
- Editing the Key decisions table, which remains accurate.

## Do-Not-Touch

- `serve/src/apex_mcp`
- `serve/README.md`
- `serve/VALIDATION.md`

## Open Questions

(none — this task is fully specified)
