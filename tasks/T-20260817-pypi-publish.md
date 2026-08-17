---
id: T-20260817-pypi-publish
title: "Publish apex-mcp to PyPI"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260817-testpypi-rehearsal]
touches_paths: [serve/VALIDATION.md]
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

# Publish apex-mcp to PyPI

> **Why:** Split from the config edits because publishing is one-way and editing configs before the upload succeeds would point the repo at a package that does not exist.

## Goal

Upload the release and verify a clean-machine uvx apex-mcp launch.

## Context

Requires PyPI credentials and a confirmed distribution name. Build from a clean tree so the artifact matches a commit.

## Behavior

- **B-1** — GIVEN a released version WHEN uvx apex-mcp runs on a machine with no local checkout THEN the server starts, blocks on stdin and writes zero bytes to stdout
- **B-2** — GIVEN the release WHEN the user registers it with an MCP client THEN the client reports the apex server as connected

## Success Criteria

```bash
# eval_1: a clean uvx install from real PyPI launches with a silent stdout
eval_1() {
  cd /tmp && uvx apex-mcp </dev/null >/tmp/p-stdout.bin 2>/tmp/p-stderr.txt; test ! -s /tmp/p-stdout.bin
}

# eval_2: the published release is recorded in the lane validation record
eval_2() {
  cd serve && grep -qiE 'published|pypi release' VALIDATION.md
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "a clean uvx install from real PyPI launches with a silent stdout"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 180
  - id: eval_2
    description: "the published release is recorded in the lane validation record"
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

- Publishing before the TestPyPI rehearsal passed; the version is immutable and a broken release is permanent.
- Publishing from a dirty tree.
- Editing any .mcp.json or README in this unit; that is the follow-up.

## Do-Not-Touch

- `.mcp.json`
- `serve/.mcp.json`
- `serve/README.md`

## Open Questions

(none — this task is fully specified)
