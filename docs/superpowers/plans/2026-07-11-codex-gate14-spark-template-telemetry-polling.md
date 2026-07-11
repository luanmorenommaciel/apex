# Gate 14: Spark Job Template + Telemetry Polling

Date: 2026-07-11
Branch: `gustocezar/feature/codex-desacoplamento-geradores`
Prepared by: Codex

## Goal

Define a canonical local Spark rerun command and wait for `after_job_id` telemetry before comparing before/after evidence.

## Scope

- Add `build_spark_submit_rerun_command(...)`.
- Add bounded telemetry polling.
- Add `poll_telemetry(job_id)` to the local tool contract.
- Add `execute_rerun_poll_and_compare(...)`.
- Expose the new tools through MCP stdio metadata.
- Keep the command model as an argument list, not a shell string.

## Guardrails

- `app_path` stays under `rerun_root` when a rerun root is configured.
- The canonical template owns `spark.extraListeners` and `spark.apex.jobId`.
- Polling has bounded attempts and interval.
- Invalid polling configuration blocks execution before the runner is called.
- Missing after telemetry returns `telemetry_not_available`.
- The comparison only runs after telemetry is found.
- No remote branch is modified.

## Validation

Run:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_rerun_orchestrator.py tests/test_commander_tool_contract.py tests/test_commander_mcp_stdio_server.py -q --basetemp .pytest-commander-gate14-focused
```

Expected:

```text
46 passed
```

## Acceptance

- Spark template returns a `spark-submit` command containing `spark.apex.jobId`.
- Spark template rejects app paths outside `rerun_root`.
- Polling waits until telemetry is visible.
- Polling can report `not_found` without inventing telemetry.
- Guarded rerun with polling returns `rerun_completed` only after telemetry exists.
- Missing telemetry returns `telemetry_not_available`.
- MCP exposes template and polling as read-only tools.
- MCP exposes polling rerun as guarded mutation.
