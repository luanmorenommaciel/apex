---
id: T-20261006-six-lane-gate-full-detail
title: "Ask analyze_run for the full diagnosis in the canonical gate"
status: in-progress
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [scripts/e2e_six_lanes.py, tests/test_e2e_six_lanes.py]
creates_paths: []
source_note: "scripts/e2e_six_lanes.py"
created: "2026-10-06T00:00:00Z"
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

# Ask analyze_run for the full diagnosis in the canonical gate

> **Why:** The canonical six-lane gate failed every job with mcp_stage_count_mismatch 0 vs N. Its MCP probe called analyze_run with no detail, and since serve's L3 leg (2026-08-20) the default summary trims stages and findings to an empty list - a trimmed list, which the gate read as the whole. The gate was last touched 2026-08-19. Found live on 2026-10-06 against a 20-stage job.

## Goal

The probe asks for detail full, a unit test pins the arguments the probe sends, and the gate passes on a real job - engine idempotent, MCP read-only, stage and finding counts equal.

## Context

The fix is one argument; the test fakes the mcp client modules in sys.modules so live_mcp_probe runs without a server and the call_tool arguments can be asserted. Recorded 2026-10-06 - the gate passes on two generated jobs with the fix and fails on both without it.

## Behavior

- **B-1** — GIVEN the live probe WHEN it calls analyze_run THEN the arguments carry detail full
- **B-2** — GIVEN a job in the store with findings WHEN the gate runs THEN it reports status passed with serve stage_count equal to the stage rows and finding_count equal to engine's

## Success Criteria

```bash
# eval_1: the probe's arguments are pinned, and the gate's unit suite holds
eval_1() {
  ( cd engine && uv run --extra dev pytest ../tests/test_e2e_six_lanes.py -q -p no:warnings )
}

# eval_2: LIVE - needs infra up and an analysed job - the gate passes on the newest job
eval_2() {
  ( cd serve && uv run --extra dev python ../scripts/e2e_six_lanes.py --job-id "$(docker exec apex-infra-clickhouse clickhouse-client --user apex --password apex_local_dev -q "SELECT job_id FROM apex.spark_events GROUP BY job_id ORDER BY max(ts) DESC LIMIT 1")" | grep -q '"status": "passed"' )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the probe's arguments are pinned, and the gate's unit suite holds"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 60
  - id: eval_2
    description: "LIVE - needs infra up and an analysed job - the gate passes on the newest job"
    runnable: bash
    check_type: deterministic
    verifies: [B-2]
    terminal: true
    expected_duration_sec: 120
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

- Loosening the gate to accept an empty stage list; the list is empty because it was trimmed, not because the run was.

## Do-Not-Touch

- `serve/src/`

## Open Questions

(none — this task is fully specified)
