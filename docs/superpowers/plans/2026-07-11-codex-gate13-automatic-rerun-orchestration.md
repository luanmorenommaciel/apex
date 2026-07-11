# Gate 13: Automatic Re-Run Orchestration

Date: 2026-07-11
Branch: `gustocezar/feature/codex-desacoplamento-geradores`
Prepared by: Codex

## Goal

Trigger a controlled local rerun command and then compare before/after telemetry.

## Scope

- Add `plan_rerun(before_job_id, after_job_id, command)`.
- Add `execute_rerun_and_compare(...)`.
- Require `rerun_root`.
- Require command allowlist.
- Require approval token from the plan.
- Run commands without shell expansion.
- Call `compare_job_telemetry` after successful execution.

## Guardrails

- No `rerun_root`, no execution.
- Command outside allowlist, no execution.
- `cwd` outside `rerun_root`, no execution.
- Invalid approval token, no execution.
- Failed or timed-out runner does not compare telemetry.
- Runner output is truncated.
- No remote branch is modified.

## Validation

Run:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_rerun_orchestrator.py tests/test_commander_telemetry_compare.py tests/test_commander_tool_contract.py tests/test_commander_mcp_stdio_server.py -q --basetemp .pytest-commander-gate13-code
```

Expected:

```text
40 passed
```

## Acceptance

- Plan returns an approval token for allowed commands.
- Missing `rerun_root` blocks execution.
- Unapproved command blocks execution.
- CWD outside root blocks execution.
- Wrong token blocks execution and does not call the runner.
- Successful fake runner can collect after telemetry.
- Successful rerun calls `compare_job_telemetry`.
- MCP exposes planning as read-only and execution as guarded mutation.
