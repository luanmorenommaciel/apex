---
id: T-20260919-execution-attribution-conflict-collision
title: "Make foreign conflict-stage collision observable"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [engine/tests/test_execution_attribution.py]
creates_paths: []
source_note: "https://github.com/luanmorenommaciel/apex/issues/115"
created: "2026-09-19T00:00:00Z"
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
signed_off_by: augustosilva
signed_off_at: 2026-09-19T21:17:27Z
accepted: false
accepted_by: (none)
accepted_at: (none)
signed_off_sig: hmac-sha256-v3:6af918b1:3e22964fea7d1993e7f792fca2f65977be20048b081233ca85aa9296eacc20aa
---

# Make foreign conflict-stage collision observable

> **Why:** Follow-up review found that the new conflict leak test used a foreign stage absent from the in-scope set, so its stage-ID collision requirement was not directly observable.

## Goal

Pin a true collision by placing a target-mapped stage in scope and a conflicting foreign mapping on that same stage, while preserving the expected conflict set.

## Context

Test-only follow-up. Resolver behavior, status semantics, docs, runtime and cross-lane integration remain unchanged.

## Behavior

- **B-1** — GIVEN an in-scope target stage that is not conflicting and a foreign app/job row with the same stage ID and a non-target identity WHEN attribution resolves another in-scope conflict THEN the foreign row cannot add that shared stage ID to the exact conflict set
- **B-2** — GIVEN the test mutation WHEN it runs THEN it remains limited to static offline regression coverage

## Success Criteria

```bash
# eval_1: focused attribution collision tests pass
eval_1() {
  ( cd engine && PYTHONPATH=src uv run --extra dev pytest -q tests/test_execution_attribution.py -p no:warnings )
}

# eval_2: complete offline Engine suite remains green
eval_2() {
  ( cd engine && PYTHONPATH=src uv run --extra dev pytest -q -p no:warnings )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "focused attribution collision tests pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 45
  - id: eval_2
    description: "complete offline Engine suite remains green"
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

- Changing resolver production code or status semantics.
- Adding public-surface, schema, watcher, runtime, PR, or publication work.

## Do-Not-Touch

- `engine/src`
- `serve`
- `front`
- `dev`
- `scripts`
- `infra`

## Open Questions

(none — this task is fully specified)
