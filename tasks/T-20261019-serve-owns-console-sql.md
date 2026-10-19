---
id: T-20261019-serve-owns-console-sql
title: "Make serve the sole owner of the console statements"
status: in-progress
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [serve/src/apex_mcp/ch.py, serve/tests/test_console_reads.py, serve/tests/test_projection_parity.py, serve/tests/test_ch.py, serve/tests/test_console_parity_gate.py, serve/tools/console_parity_gate.py, serve/RUNBOOK.md]
creates_paths: [serve/tools/sql/01-parity-readonly-user.sql]
source_note: "D-api-only; serve/tests/test_console_reads.py front_query(), test_projection_parity.py front_fix_verifications(), test_ch.py test_run_rollup_matches_the_console_sql, test_console_parity_gate.py + tools/console_parity_gate.py console_statements() (all read front/src/data/queries.ts); serve/RUNBOOK.md lines 142-166 (the two doors, make ch-user)"
created: "2026-10-19T00:00:00Z"
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
signed_off: true
signed_off_by: agmarcastro
signed_off_at: 2026-10-19T15:55:28Z
accepted: false
accepted_by: (none)
accepted_at: (none)
signed_off_sig: hmac-sha256-v3:60832560:a19777fe6d7066e6b5a7c53b44fa16cf96bb9dfbf01edfa1a70b1ef090c5b1b1
---

# Make serve the sole owner of the console statements

> **Why:** Five serve tests and the live gate read front/src/data/queries.ts as the contract for the console's SQL. The next leaf deletes that file, so serve must own its statements before the console stops carrying them, or the serve suite and the gate break on a file that no longer exists.

## Goal

No serve test or tool reads front/src/data/queries.ts; ch.py's constants are asserted directly; the gate runs ch.py's own statements over ClickHouse HTTP as a readonly user whose DDL now lives in serve/tools/sql, compares those rows with the API's, and keeps every live behaviour check it has; RUNBOOK says so; the full serve suite passes.

## Context

test_console_reads keeps its three regressions but asserts on ch._console_findings_sql() and ch.CONSOLE_PLAN_TRANSITIONS_SQL instead of front_query(); test_projection_parity becomes a test that FIX_VERIFICATION_SQL still derives rule 2 the documented way (floor boundary, sign flip, NULL mechanism_confirmed) rather than a byte comparison with a file that is gone; test_ch's rollup-match test is replaced by an assertion that RUN_ONE_SQL and RUN_LIST_SQL are one body with two literals. The gate's console_statements() is replaced by a dict of ch.py constants keyed by the same names the gate already uses, with the serve binding names, and browser_query() stays as the raw-SQL door; its readonly user is created from serve/tools/sql/01-parity-readonly-user.sql (the text of front/contract/01-readonly-user.sql, which the console leaf deletes) and RUNBOOK's "make ch-user" row points at it. The ch.py docstrings that say "edit both or neither" and "serve/src/apex_mcp/ch.py carries this same body" are rewritten to say ch.py is the owner. test_api_resources is untouched: Repository method names, RunSummary and the wire timestamp stay the console's contract.

## Behavior

- **B-1** — GIVEN the serve tests and tools WHEN they are searched THEN none names front/src/data/queries.ts or front_query
- **B-2** — GIVEN the full serve suite WHEN it runs THEN it passes, with the three console-read regressions still pinned on ch.py's own text
- **B-3** — GIVEN the gate's statement table WHEN its test runs THEN every name the gate sends is a ch.py constant and carries serve's binding names, never the console's

## Success Criteria

```bash
# eval_1: nothing in serve reads the console's SQL any more
eval_1() {
  ( grep -q "def serve_statements" serve/tools/console_parity_gate.py && test -z "$(grep -rl --exclude-dir=__pycache__ "front/src/data/queries.ts\|front_query\|QUERIES_TS" serve/tests serve/tools serve/src)" )
}

# eval_2: the full serve suite passes
eval_2() {
  ( cd serve && uv run --extra dev pytest -q -p no:warnings )
}

# eval_3: the readonly user DDL and the runbook moved with the gate
eval_3() {
  ( test -f serve/tools/sql/01-parity-readonly-user.sql && grep -q "readonly = 1" serve/tools/sql/01-parity-readonly-user.sql && grep -q "tools/sql/01-parity-readonly-user.sql" serve/RUNBOOK.md && ! grep -q "make ch-user" serve/RUNBOOK.md )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "nothing in serve reads the console's SQL any more"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 5
  - id: eval_2
    description: "the full serve suite passes"
    runnable: bash
    check_type: deterministic
    verifies: [B-2, B-3]
    terminal: true
    expected_duration_sec: 120
  - id: eval_3
    description: "the readonly user DDL and the runbook moved with the gate"
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
eval_1 && eval_2 && eval_3
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Copying queries.ts into a serve test as a string to keep a byte comparison alive.
- Dropping the gate's readonly or unindexed-run checks because the browser door is gone; raw SQL as a readonly user is still the reference.
- Touching front/ in this leaf.

## Do-Not-Touch

- `front`
- `engine`
- `serve/src/apex_api`

## Open Questions

(none — this task is fully specified)
