---
id: T-20260919-execution-attribution-scope-collision
title: "Pin attribution scope against realistic stage-ID collisions"
status: ready
format_version: 3
profile: standard
effort: S
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
signed_off_at: 2026-09-19T21:14:30Z
accepted: false
accepted_by: (none)
accepted_at: (none)
signed_off_sig: hmac-sha256-v3:6af918b1:8f88101e275a7e51bb92fe97e6eb5c13dbf41f6dd28874724210803f6e020c82
---

# Pin attribution scope against realistic stage-ID collisions

> **Why:** The first audit-hardening pass scoped foreign rows but used only non-overlapping stage IDs, leaving realistic repeated stage-ID leakage insufficiently tested.

## Goal

Strengthen test-only identity-boundary coverage so foreign app/job rows reusing in-scope stage IDs or target identity cannot change absent, not-found, attributed, or conflict results.

## Context

This is a regression-test leaf only. Resolver behavior, public integration, schema, validation, runtime and docs remain unchanged.

## Behavior

- **B-1** — GIVEN foreign app/job rows whose stage IDs collide with in-scope stages and whose identities include the target or conflicting non-null IDs WHEN attribution is resolved THEN exact app_id/job_id scoping preserves the original in-scope status and exact stage/conflict IDs
- **B-2** — GIVEN only foreign rows with None execution IDs and no in-scope observations WHEN attribution is resolved THEN the result is execution_id_not_found rather than execution_id_absent
- **B-3** — GIVEN these new regression cases WHEN they run THEN they make no claim about cross-lane, runtime, or public-surface behavior

## Success Criteria

```bash
# eval_1: focused collision and attribution boundary tests pass
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
    description: "focused collision and attribution boundary tests pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 45
  - id: eval_2
    description: "complete offline Engine suite remains green"
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
eval_1 && eval_2
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Changing resolver code or status semantics.
- Adding cross-lane wiring, schema changes, watcher changes, runtime proof, PRs, or publication.
- Treating foreign rows as in-scope to make tests pass.

## Do-Not-Touch

- `engine/src`
- `engine/src/apex_engine/watchers`
- `serve`
- `front`
- `dev`
- `scripts`
- `infra`

## Open Questions

(none — this task is fully specified)
