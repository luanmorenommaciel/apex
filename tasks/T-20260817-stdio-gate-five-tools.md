---
id: T-20260817-stdio-gate-five-tools
title: "Assert five tools in the real stdio MCP gate"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260817-register-apex-status]
touches_paths: [serve/tools/mcp_stdio_gate.py]
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

# Assert five tools in the real stdio MCP gate

> **Why:** The in-process test skips JSON-RPC framing, the client handshake and serialization - exactly where a stray stdout byte or a rejected schema would appear.

## Goal

Confirm the fifth tool over a real MCP client on real stdio.

## Context

Keep the suggest_fix assertions untouched; they pin the lane's headline safety claims over the wire.

## Behavior

- **B-1** — GIVEN the server spawned over stdio WHEN the official client lists tools THEN it sees exactly five, apex_status among them
- **B-2** — GIVEN that listing WHEN annotations are read THEN apex_status carries readOnlyHint true and openWorldHint false
- **B-3** — GIVEN apex_status invoked through the client WHEN the response returns THEN it is schema-valid structured output
- **B-4** — GIVEN the whole session WHEN it completes THEN no framing error occurred

## Success Criteria

```bash
# eval_1: the stdio gate passes end to end
eval_1() {
  cd serve && uv run python tools/mcp_stdio_gate.py
}

# eval_2: the gate no longer claims a four-tool surface
eval_2() {
  cd serve && ! grep -n 'four contracted tools' tools/mcp_stdio_gate.py
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the stdio gate passes end to end"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3, B-4]
    terminal: true
    expected_duration_sec: 120
  - id: eval_2
    description: "the gate no longer claims a four-tool surface"
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
eval_1 && eval_2
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Softening the assertion to contains apex_status; the value is pinning the exact surface a client sees.
- Skipping the annotation assertion, since the annotation is what the client acts on.

## Do-Not-Touch

- `serve/src/apex_mcp`

## Open Questions

(none — this task is fully specified)
