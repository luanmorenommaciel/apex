---
id: T-20260817-testpypi-rehearsal
title: "Rehearse the publish on TestPyPI"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260817-wheel-content-check, T-20260817-four-to-five-doc-ripple]
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

# Rehearse the publish on TestPyPI

> **Why:** A PyPI release is immutable, so the first exercise of the one-command install must not be against the real index.

## Goal

Publish a dev version to TestPyPI and install it clean, recording the result.

## Context

Requires a TestPyPI API token, so the upload step is human-gated. Use a devN suffix so the real release number stays clean.

## Behavior

- **B-1** — GIVEN built artifacts WHEN uploaded to TestPyPI THEN the upload succeeds and the project page renders the README
- **B-2** — GIVEN a directory with no local checkout WHEN uvx installs from the TestPyPI index THEN the server starts and blocks on stdin with zero bytes on stdout
- **B-3** — GIVEN the installed package WHEN its dependencies resolve THEN mcp and clickhouse-connect come from real PyPI via the extra index

## Success Criteria

```bash
# eval_1: a clean install from TestPyPI launches with a silent stdout
eval_1() {
  ( cd /tmp && uvx --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ apex-mcp </dev/null >/tmp/tp-stdout.bin 2>/tmp/tp-stderr.txt; test ! -s /tmp/tp-stdout.bin )
}

# eval_2: the rehearsal outcome is recorded in the lane validation record
eval_2() {
  ( cd serve && grep -qi 'testpypi' VALIDATION.md )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "a clean install from TestPyPI launches with a silent stdout"
    runnable: bash
    check_type: deterministic
    verifies: [B-2, B-3]
    terminal: true
    expected_duration_sec: 180
  - id: eval_2
    description: "the rehearsal outcome is recorded in the lane validation record"
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

- Reusing the version number intended for the real release; TestPyPI is immutable per version too.
- Testing from inside serve/, where a local install can satisfy the import and produce a false pass.
- Omitting the extra index and then vendoring a dependency to make resolution succeed.

## Do-Not-Touch

- `serve/pyproject.toml`

## Open Questions

(none — this task is fully specified)
