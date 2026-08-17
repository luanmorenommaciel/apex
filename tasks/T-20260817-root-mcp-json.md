---
id: T-20260817-root-mcp-json
title: "Add the root .mcp.json with a drift test"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
touches_paths: []
creates_paths: [.mcp.json, serve/tests/test_config_parity.py]
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

# Add the root .mcp.json with a drift test

> **Why:** serve/.mcp.json documents that it must be copied to the repository root to activate, and nothing performs that copy, so project scope is an instruction nobody executed.

## Goal

Ship the root config as a real file and guard the duplication with a test.

## Context

This repo already carries two hand-maintained copies of one schema in infra/sql and collect/ddl, and W0 is the bill for that going unchecked.

## Behavior

- **B-1** — GIVEN a fresh clone WHEN a client opens the repo THEN the root .mcp.json is found with no manual step
- **B-2** — GIVEN both files WHEN parsed THEN their mcpServers blocks are identical and only the comment key may differ
- **B-3** — GIVEN either file edited alone WHEN the suite runs THEN the parity test fails and names both paths
- **B-4** — GIVEN the root file WHEN inspected THEN it is a regular file and not a symlink

## Success Criteria

```bash
# eval_1: the parity test passes
eval_1() {
  cd serve && uv run --extra dev pytest tests/test_config_parity.py -q
}

# eval_2: the root config is a regular file whose server block matches serve
eval_2() {
  cd /opt/projects/dataship/git/apex && test -f .mcp.json && test ! -L .mcp.json && python3 -c "import json; a=json.load(open('.mcp.json')); b=json.load(open('serve/.mcp.json')); assert a['mcpServers']==b['mcpServers']"
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the parity test passes"
    runnable: bash
    check_type: deterministic
    verifies: [B-2, B-3]
    terminal: true
    expected_duration_sec: 30
  - id: eval_2
    description: "the root config is a regular file whose server block matches serve"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-4]
    terminal: true
    expected_duration_sec: 10
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

- Using a symlink; Codex on Windows and some client sandboxes do not follow them.
- Generating the root file at build time; it must exist in a fresh clone.
- Redesigning the mcpServers content, which is settled.

## Do-Not-Touch

- `serve/src/apex_mcp`

## Open Questions

(none — this task is fully specified)
