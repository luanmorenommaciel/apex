---
id: T-20260817-drop-from-path
title: "Drop the uvx --from fallback now that the package is published"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260817-pypi-publish, T-20260817-root-mcp-json, T-20260817-four-to-five-doc-ripple]
touches_paths: [.mcp.json, serve/.mcp.json, serve/README.md]
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

# Drop the uvx --from fallback now that the package is published

> **Why:** serve/.mcp.json already carries the instruction to make this change once the package is published; this unit executes that note.

## Goal

Point every client config and document at plain uvx apex-mcp.

## Context

Sized M because the write surface is three paths. Runs only after the upload succeeds.

## Behavior

- **B-1** — GIVEN both .mcp.json files WHEN read THEN args is exactly ["apex-mcp"] and the comment no longer instructs a future reader to make this change
- **B-2** — GIVEN serve/README.md WHEN read THEN the --from path fallback is gone

## Success Criteria

```bash
# eval_1: no config or document still references the --from fallback
eval_1() {
  ( ! grep -rn -- '--from' .mcp.json serve/.mcp.json serve/README.md )
}

# eval_2: both configs invoke the published console script directly
eval_2() {
  ( python3 -c "import json; a=json.load(open('.mcp.json')); b=json.load(open('serve/.mcp.json')); assert a['mcpServers']['apex']['args']==['apex-mcp'], a['mcpServers']['apex']['args']; assert a['mcpServers']==b['mcpServers']" )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "no config or document still references the --from fallback"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 10
  - id: eval_2
    description: "both configs invoke the published console script directly"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
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

- Running this before the upload succeeded, which points the repo at a package that does not exist.
- Letting the root and serve copies diverge while editing them.

## Do-Not-Touch

- `serve/pyproject.toml`
- `serve/src/apex_mcp`

## Open Questions

(none — this task is fully specified)
