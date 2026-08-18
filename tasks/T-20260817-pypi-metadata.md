---
id: T-20260817-pypi-metadata
title: "Add PyPI metadata to the serve pyproject"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
touches_paths: [serve/pyproject.toml]
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

# Add PyPI metadata to the serve pyproject

> **Why:** Until the package is publishable every install path needs uvx --from a path, which is the difference between one command and a paragraph.

## Goal

Carry readme, license, authors, keywords, classifiers and project urls in the wheel metadata.

## Context

The repository is now Apache-2.0 licensed, which settles the licence question this unit previously carried as open.

## Behavior

- **B-1** — GIVEN the project WHEN built THEN the wheel metadata carries readme, license, authors, keywords, classifiers and urls
- **B-2** — GIVEN the built artifacts WHEN twine check runs THEN every one reports PASSED
- **B-3** — GIVEN the dependency pins WHEN read THEN mcp[cli]>=1.27,<2 is unchanged, because the upper bound is a researched decision

## Success Criteria

```bash
# eval_1: metadata is complete and the pin survived
eval_1() {
  ( cd serve && uv run python -c "import tomllib,pathlib; p=tomllib.loads(pathlib.Path('pyproject.toml').read_text())['project']; need={'readme','license','authors','keywords','classifiers','urls'}; missing=need-p.keys(); assert not missing, missing; assert p['dependencies'][0].startswith('mcp[cli]>=1.27,<2'), p['dependencies'][0]" )
}

# eval_2: the built wheel and sdist pass twine check
eval_2() {
  ( cd serve && rm -rf dist && uv build >/dev/null && uvx twine check dist/* | grep -q PASSED )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "metadata is complete and the pin survived"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-3]
    terminal: true
    expected_duration_sec: 15
  - id: eval_2
    description: "the built wheel and sdist pass twine check"
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

- Bumping version here; publishing is a separate unit.
- Relaxing the mcp upper bound while in the file.
- Rewriting serve/README.md to please the PyPI renderer.

## Do-Not-Touch

- `serve/src/apex_mcp`

## Open Questions

(none — this task is fully specified)
