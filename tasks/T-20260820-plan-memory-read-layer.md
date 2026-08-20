---
id: T-20260820-plan-memory-read-layer
title: "Read plan similarity and prior outcomes"
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

# Read plan similarity and prior outcomes

> **Why:** The memory lane answers the one question no single-run tool can - have we seen this plan shape before, and what configuration worked. It writes apex.plan_memory and apex.run_outcomes, and nothing surfaces either.

## Goal

Find plan shapes similar to a run, and the prior runs of those shapes with their configs and outcomes.

## Context

plan_memory.embedding is L2-normalised and cosineDistance-ready, so similarity runs in ClickHouse - no import of apex_memory, and serve keeps depending only on mcp, clickhouse-connect and pydantic. dim is asserted on read by the memory lane; serve must not assume a fixed width. These are v0.3 additive tables, absent on older clusters.

## Behavior

- **B-1** — GIVEN a plan_fingerprint present in plan_memory WHEN similar_plans() is called THEN it returns other fingerprints ranked by cosine similarity, above a minimum threshold
- **B-2** — GIVEN a set of fingerprints WHEN prior_outcomes() is called THEN it returns runs of those shapes with their config columns and wall clock, newest first
- **B-3** — GIVEN a deployment without the v0.3 tables WHEN either read is called THEN it returns empty and logs, rather than raising
- **B-4** — GIVEN a hostile fingerprint value WHEN either read is called THEN it binds server-side and returns zero rows

## Success Criteria

```bash
# eval_1: the similarity and outcome reads exist and pass
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_ch.py::test_similar_plans_ranks_by_cosine_distance" "tests/test_ch.py::test_prior_outcomes_returns_configs_newest_first" "tests/test_ch.py::test_plan_memory_binds_hostile_fingerprint" )
}

# eval_2: absent additive tables degrade instead of raising
eval_2() {
  ( cd serve && uv run --extra dev pytest "tests/test_ch.py::test_plan_memory_absent_tables_degrade" )
}

# eval_3: serve still depends on no other lane
eval_3() {
  ( cd serve && ! grep -nE 'apex_memory|apex_verify' src/apex_mcp/*.py pyproject.toml )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the similarity and outcome reads exist and pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-4]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "absent additive tables degrade instead of raising"
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

- Importing apex_memory; the contract tables are the integration surface.
- Hardcoding the embedding width instead of reading dim.
- Ranking by raw distance without a minimum similarity, which returns unrelated shapes as neighbours.

## Do-Not-Touch

- `serve/src/apex_mcp/server.py`
- `serve/src/apex_mcp/models.py`

## Open Questions

(none — this task is fully specified)
