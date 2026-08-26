---
id: T-20260820-critical-path
title: "Frame the bottleneck as a path, not a list"
status: done
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260820-coverage-freshness]
touches_paths: [serve/src/apex_mcp/diagnose.py, serve/tests/test_diagnose.py]
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

# Frame the bottleneck as a path, not a list

> **Why:** analyze() already sums p99 as tail time to rank stages, then throws the shape away. "Stage 4 is 61% of the tail" is actionable; a sorted list of seventeen stages is homework.

## Goal

Report each stage's share of total tail time and the smallest set covering most of it.

## Context

p99 is the closest stand-in for stage wall time the contract gives, and this is a SHARE OF TAIL, not a true DAG critical path - stages may overlap. Say so in the field description so nobody reads it as scheduling truth.

## Behavior

- **B-1** — GIVEN a diagnosis with several stages WHEN it is read THEN each stage carries its share of total tail time
- **B-2** — GIVEN one stage dominating the tail WHEN the diagnosis is read THEN the smallest set of stages covering most of the tail names that stage alone
- **B-3** — GIVEN stages of equal duration WHEN the diagnosis is read THEN no stage is singled out, because there is no bottleneck to name
- **B-4** — GIVEN the payload WHEN the tail-share field is read THEN its description states this is share of tail, not a scheduling critical path

## Success Criteria

```bash
# eval_1: the tail-share tests exist and pass
eval_1() {
  ( cd serve && uv run --extra dev pytest "tests/test_diagnose.py::test_stage_carries_share_of_tail" "tests/test_diagnose.py::test_dominant_stage_is_named_alone" "tests/test_diagnose.py::test_even_stages_name_no_bottleneck" )
}

# eval_2: the field does not claim to be a scheduling critical path
eval_2() {
  ( cd serve && uv run python -c "import json; from apex_mcp.models import Diagnosis; s=json.dumps(Diagnosis.model_json_schema()); assert 'share of tail' in s.lower() or 'not a scheduling' in s.lower(), 'tail-share field lacks its caveat'" )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the tail-share tests exist and pass"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "the field does not claim to be a scheduling critical path"
    runnable: bash
    check_type: deterministic
    verifies: [B-4]
    terminal: true
    expected_duration_sec: 15
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

- Calling it a critical path; stages overlap and p99 is a stand-in, so the honest name is share of tail.
- Naming a bottleneck when the distribution is flat.

## Do-Not-Touch

- `serve/src/apex_mcp/ch.py`
- `serve/src/apex_mcp/server.py`

## Open Questions

(none — this task is fully specified)
