---
id: T-20260919-execution-attribution-audit-hardening
title: "Harden offline execution attribution identity-boundary coverage"
status: done
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [engine/src/apex_engine/attribution.py, engine/tests/test_execution_attribution.py]
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
signed_off_at: 2026-09-19T21:08:56Z
accepted: true
accepted_by: augustosilva
accepted_at: 2026-09-19T21:09:10Z
signed_off_sig: hmac-sha256-v3:6af918b1:cf751f9f35088b0e5d8c8e5a1155efb4fa9f381d1c4e998f424f106a4da2ddc6
accepted_tier: 1
accepted_attempt_id: a68a9e42-4cae-4c32-a6c9-8171c46173d4
accepted_authorization_ref: hmac-sha256-v3:6af918b1:cf751f9f35088b0e5d8c8e5a1155efb4fa9f381d1c4e998f424f106a4da2ddc6
acceptance_record_digest: sha256:ddf28bf169ea09459082e72275c8e71bcc9e33243423b3603921f98223166ad4
---

# Harden offline execution attribution identity-boundary coverage

> **Why:** Independent review approved the pure attribution primitive but found that foreign job scope and the mixed None/non-target-ID outcome were not pinned by tests or documented.

## Goal

Add only documentation and regression coverage for the existing scoped attribution behavior, without changing resolver outcomes or integrating it with a public surface.

## Context

This is audit remediation for the already accepted offline #115 leaf. It deliberately does not add cross-lane wiring, queries, schema changes, runtime proof, or a new identity-validation policy.

## Behavior

- **B-1** — GIVEN foreign application or job observations alongside an in-scope request WHEN absent, not-found, or conflict attribution is resolved THEN foreign rows cannot alter the in-scope status or returned IDs
- **B-2** — GIVEN in-scope observations mixing None and a non-target non-null execution identity WHEN attribution is resolved THEN the explicit result is execution_id_not_found; None beside a target remains attributed and another non-null target-stage identity remains conflict
- **B-3** — GIVEN the public resolver docstring WHEN a reader inspects its status rules THEN it accurately states the in-scope absent, not-found, attributed, and conflict boundaries

## Success Criteria

```bash
# eval_1: focused attribution boundary tests pass
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
    description: "focused attribution boundary tests pass"
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

- Changing resolver status behavior, constructor validation, schema, ClickHouse, watcher, Serve, Front, or runtime infrastructure.
- Treating foreign job rows as in-scope evidence.
- Publishing, pushing, opening a PR, or running Spark/ClickHouse.

## Do-Not-Touch

- `engine/src/apex_engine/schema.py`
- `engine/src/apex_engine/clickhouse.py`
- `engine/src/apex_engine/watchers`
- `serve`
- `front`
- `jar`
- `infra`
- `collect`

## Open Questions

(none — this task is fully specified)
