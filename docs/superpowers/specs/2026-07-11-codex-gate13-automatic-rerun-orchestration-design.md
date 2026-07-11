# Gate 13 Design: Automatic Re-Run Orchestration

Date: 2026-07-11
Branch: `gustocezar/feature/codex-desacoplamento-geradores`
Prepared by: Codex

## Decision

Add controlled rerun orchestration through two tools:

- `plan_rerun`
- `execute_rerun_and_compare`

## Why

Gate 12 can compare before/after telemetry, but it assumes the after-run already happened. Gate 13 adds the controlled step that triggers a local command and then runs the comparison.

## Data Flow

```text
plan_rerun
  -> validate rerun_root / cwd / allowlist / timeout
  -> approval token
execute_rerun_and_compare
  -> validate approval token
  -> runner.run(command)
  -> compare_job_telemetry
```

## Safety Model

Commands are not strings and are not sent through a shell. They are argument lists, checked against allowlisted prefixes.

The default contract is safe because execution is blocked unless `rerun_root` and `rerun_allowed_command_prefixes` are configured.

## Output Shape

```json
{
  "status": "rerun_completed",
  "runner": {
    "status": "succeeded",
    "exit_code": 0
  },
  "comparison": {
    "status": "improved"
  }
}
```

## Out Of Scope

- No canonical Spark job command yet.
- No telemetry polling loop yet.
- No production scheduler.
- No rollback automation.
- No remote publication.

## Next Gate

Gate 14 should add a canonical local Spark job template plus telemetry polling:

```text
execute rerun -> poll ClickHouse for after_job_id -> compare
```
