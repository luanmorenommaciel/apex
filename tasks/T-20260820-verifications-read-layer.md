---
id: T-20260820-verifications-read-layer
title: "Read apex.fix_verifications from the serve store"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
touches_paths: [serve/src/apex_mcp/ch.py, serve/tests/test_ch.py]
creates_paths: []
source_note: "docs/lanes/SERVE-LEGS.md"
created: "2026-08-20T00:00:00Z"
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

# Read apex.fix_verifications from the serve store

> **Why:** The verify lane decides whether a fix would work and writes apex.fix_verifications, but nothing surfaces it. A whole lane with 105 tests has no user surface.

## Goal

Fetch verification rows for a job_id, optionally narrowed to one finding.

## Context

Lanes integrate through ClickHouse, not imports - serve depends only on mcp, clickhouse-connect and pydantic, and reads engine's findings the same way. Do NOT add apex_verify as a dependency. Probe for the table like findings_columns does, so a deployment without the v0.3 tables degrades instead of erroring.

## Behavior

- **B-1** — GIVEN a job_id with verifications WHEN verifications() is called THEN it returns them newest-first with method, predictor, predicted and measured deltas, safety verdict and confidence
- **B-2** — GIVEN a finding_id filter WHEN verifications() is called THEN only that finding's rows return, bound server-side
- **B-3** — GIVEN a deployment whose apex.fix_verifications does not exist WHEN verifications() is called THEN it returns empty and logs, rather than raising - the v0.3 tables are additive
- **B-4** — GIVEN a hostile finding_id WHEN verifications() is called THEN it binds and returns zero rows

## Success Criteria

```bash
# eval_1: the verification read tests exist and pass
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_ch.py::test_verifications_returns_rows_newest_first" "tests/test_ch.py::test_verifications_filters_by_finding_id" "tests/test_ch.py::test_verifications_binds_hostile_finding_id" )
}

# eval_2: a missing additive table degrades instead of raising
eval_2() {
  ( cd serve && uv run --extra dev pytest "tests/test_ch.py::test_verifications_absent_table_degrades" )
}

# eval_3: serve still depends on no other lane
eval_3() {
  ( cd serve && ! grep -nE 'apex_verify|apex_memory' src/apex_mcp/*.py pyproject.toml )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the verification read tests exist and pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-4]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "a missing additive table degrades instead of raising"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
    terminal: true
    expected_duration_sec: 30
  - id: eval_3
    description: "serve still depends on no other lane"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
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
eval_1 && eval_2 && eval_3
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Importing apex_verify; the contract table is the integration surface.
- Raising when the table is absent - v0.3 tables are additive and older clusters lack them.
- Interpolating job_id or finding_id into SQL.

## Do-Not-Touch

- `serve/src/apex_mcp/server.py`
- `serve/src/apex_mcp/models.py`

## Open Questions

(none — this task is fully specified)
