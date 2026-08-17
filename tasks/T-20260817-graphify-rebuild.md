---
id: T-20260817-graphify-rebuild
title: "Rebuild the graphify knowledge graph for L1"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260817-four-to-five-doc-ripple]
touches_paths: [graphify-out]
creates_paths: []
source_note: "docs/lanes/L1_tasks.md"
created: "2026-08-17T00:00:00Z"
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

# Rebuild the graphify knowledge graph for L1

> **Why:** A stale graph does not fail loudly; it quietly answers questions about a codebase that no longer exists.

## Goal

Make the graph know apex_status, ServerStatus, resolve_settings and store_health.

## Context

The graph was built on 2026-07-27 and this leg was scoped from a graph query. Use --update rather than a full rebuild.

## Behavior

- **B-1** — GIVEN the rebuilt graph WHEN queried for apex_status THEN the node exists with its source location in server.py
- **B-2** — GIVEN the rebuilt graph WHEN queried for the serve lane THEN ServerStatus, resolve_settings and store_health appear
- **B-3** — GIVEN the rebuild WHEN it completes THEN the pre-existing nodes for the original four tools are still present

## Success Criteria

```bash
# eval_1: the new symbols are present in the graph
eval_1() {
  cd /opt/projects/dataship/git/apex && graphify query "apex_status ServerStatus resolve_settings store_health" --budget 800 | grep -q apex_status
}

# eval_2: the rebuild was an update and did not truncate pre-existing nodes
eval_2() {
  cd /opt/projects/dataship/git/apex && graphify query "suggest_fix" --budget 400 | grep -q suggest_fix
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the new symbols are present in the graph"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 300
  - id: eval_2
    description: "the rebuild was an update and did not truncate pre-existing nodes"
    runnable: bash
    check_type: deterministic
    verifies: [B-3]
    terminal: true
    expected_duration_sec: 180
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

- A full rebuild when --update suffices.
- Committing graphify-out without a deliberate repository-level decision; it is currently untracked.

## Do-Not-Touch

- `graphify-out/.graphify_root`
- `graphify-out/.graphify_python`

## Open Questions

(none — this task is fully specified)
