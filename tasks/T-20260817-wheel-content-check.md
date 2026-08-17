---
id: T-20260817-wheel-content-check
title: "Assert the wheel ships the package and nothing else"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20260817-pypi-metadata]
touches_paths: [serve/pyproject.toml]
creates_paths: [serve/tests/test_packaging.py]
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

# Assert the wheel ships the package and nothing else

> **Why:** serve/tools holds two live gates that write fixture rows to ClickHouse; shipping them would put a seeding script into every user's environment.

## Goal

Prove the built wheel contains only apex_mcp and its dist-info.

## Context

The wheel target already names packages = src/apex_mcp, but nothing asserts it. Expect zero config change - this unit usually only proves the current setting.

## Behavior

- **B-1** — GIVEN a built wheel WHEN its contents are listed THEN every entry is under apex_mcp/ or the dist-info directory
- **B-2** — GIVEN a built wheel WHEN its contents are listed THEN no path contains tests/, tools/ or scripts/
- **B-3** — GIVEN the sdist WHEN inspected THEN it contains README.md and pyproject.toml, enough to rebuild from source

## Success Criteria

```bash
# eval_1: the packaging test passes
eval_1() {
  cd serve && uv run --extra dev pytest tests/test_packaging.py -q
}

# eval_2: the artifact itself contains no test, tool or script path
eval_2() {
  cd serve && rm -rf dist && uv build >/dev/null && uv run python -c "import glob,zipfile; n=zipfile.ZipFile(glob.glob('dist/*.whl')[0]).namelist(); bad=[x for x in n if not (x.startswith('apex_mcp/') or '.dist-info/' in x)]; assert not bad, bad; assert not [x for x in n if any(p in x for p in ('tests/','tools/','scripts/'))]; print(len(n),'entries in-package')"
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the packaging test passes"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2, B-3]
    terminal: true
    expected_duration_sec: 60
  - id: eval_2
    description: "the artifact itself contains no test, tool or script path"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
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

- Adding tools/ to the wheel so users can run the gates; the gates seed fixture rows.
- Excluding files via gitignore and assuming the build honors it; assert on the artifact.

## Do-Not-Touch

- `serve/src/apex_mcp`

## Open Questions

(none — this task is fully specified)
