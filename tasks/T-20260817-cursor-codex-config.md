---
id: T-20260817-cursor-codex-config
title: "Document the Cursor and Codex config paths"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
touches_paths: [serve/README.md]
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

# Document the Cursor and Codex config paths

> **Why:** Two of the three supported clients are documented only by implication - the README says they read the same schema without saying where each looks.

## Goal

Let a Cursor or Codex user install Apex from the README alone.

## Context

Verify each path against that client's current documentation and record the source; a wrong config path is worse than none because it looks authoritative.

## Behavior

- **B-1** — GIVEN the README WHEN a Cursor or Codex user reads it THEN the exact config path and the project versus user scope distinction are named
- **B-2** — GIVEN any of the three client sections WHEN followed THEN the verification step is named
- **B-3** — GIVEN the sections WHEN read THEN each states that variables expand at client start, so exporting one afterwards needs a restart

## Success Criteria

```bash
# eval_1: per-client sections exist for all three harnesses
eval_1() {
  ( cd serve && grep -q '^### Cursor' README.md && grep -q '^### Codex' README.md && grep -q '^### Claude Code' README.md )
}

# eval_2: each client section names how to verify the connection
eval_2() {
  ( cd serve && grep -qiE 'mcp list|/mcp' README.md )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "per-client sections exist for all three harnesses"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-3]
    terminal: true
    expected_duration_sec: 5
  - id: eval_2
    description: "each client section names how to verify the connection"
    runnable: bash
    check_type: deterministic
    verifies: [B-2]
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

- Documenting a config path from memory rather than verifying it.
- Duplicating the environment table per client.

## Do-Not-Touch

- `serve/.mcp.json`

## Open Questions

(none — this task is fully specified)
