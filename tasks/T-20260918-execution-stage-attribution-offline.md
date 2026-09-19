---
id: T-20260918-execution-stage-attribution-offline
title: "Resolve execution identity to stages offline"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: []
creates_paths: [engine/src/apex_engine/attribution.py, engine/tests/test_execution_attribution.py]
source_note: "https://github.com/luanmorenommaciel/apex/issues/115"
created: "2026-09-18T00:00:00Z"
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
signed_off_at: 2026-09-19T00:42:55Z
accepted: false
accepted_by: (none)
accepted_at: (none)
signed_off_sig: hmac-sha256-v3:6af918b1:d2ee414b956039dbf77391ce05a45155dedc2f364d156684a03b0c1bca9dc7c5
---

# Resolve execution identity to stages offline

> **Why:** Contract v0.6 landed the optional producer identity, but Engine has no bounded consumer primitive that distinguishes exact attribution, optional absence, not-found identity, and conflicting stage membership.

## Goal

Add a pure two-file Engine resolver from normalized stage observations to an explicit, deterministic attribution result without touching ClickHouse, findings, Serve, Front, schema, watchers, or runtime infrastructure.

## Context

This is the ready_offline slice of issue #115 only. It keeps JOB_LEVEL_STAGE_ID unchanged and deliberately does not choose the first public surface. Runtime delivery, store/query integration, per-stage Serve projection and Front availability are separate owner/runtime-gated increments.

## Behavior

- **B-1** — GIVEN observations containing the requested execution identity WHEN they are resolved within an exact app_id and job_id scope THEN the result is attributed with all and only the distinct stage IDs sorted ascending
- **B-2** — GIVEN duplicate deliveries or multiple attempts for one stage WHEN attribution is resolved THEN stage_attempt remains provenance and the returned stage ID is not duplicated
- **B-3** — GIVEN scoped observations whose execution identity is absent on every row WHEN attribution is resolved THEN the result is execution_id_absent with no stage IDs and no synthesized sentinel
- **B-4** — GIVEN scoped observations with non-null identities but not the requested one, or no scoped observations WHEN attribution is resolved THEN the result is execution_id_not_found with no stage IDs
- **B-5** — GIVEN a stage associated with the requested identity and another non-null identity in the same app/job scope WHEN attribution is resolved THEN the result is conflict, returns no partial attribution, and names the conflicting stage IDs deterministically
- **B-6** — GIVEN a target identity of zero or rows from another application sharing the same job_id WHEN attribution is resolved THEN zero remains a real identity and foreign-app rows cannot bleed into the result
- **B-7** — GIVEN invalid blank identities or negative stage/attempt values WHEN an observation or request is created THEN validation rejects the invalid input before resolution

## Success Criteria

```bash
# eval_1: focused attribution states and identity boundaries pass
eval_1() {
  ( cd engine && uv run --extra dev pytest -q tests/test_execution_attribution.py -p no:warnings )
}

# eval_2: complete offline Engine suite remains green
eval_2() {
  ( cd engine && uv run --extra dev pytest -q -p no:warnings )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "focused attribution states and identity boundaries pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3, B-4, B-5, B-6, B-7]
    terminal: true
    expected_duration_sec: 45
  - id: eval_2
    description: "complete offline Engine suite remains green"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-3, B-5, B-6]
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

- Reading ClickHouse or OTLP inside the resolver.
- Adding execution_id to StageEvent or StageAggregate in this leaf.
- Changing JOB_LEVEL_STAGE_ID, findings, thresholds, watchers, Serve or Front.
- Treating zero as absence or synthesizing minus one for a missing execution identity.
- Returning a partial stage set when a conflicting non-null mapping exists.
- Publishing, pushing, opening a PR, or running Spark/ClickHouse for this offline leaf.

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
