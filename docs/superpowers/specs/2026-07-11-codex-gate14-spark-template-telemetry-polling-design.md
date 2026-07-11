# Gate 14 Design: Spark Job Template + Telemetry Polling

Date: 2026-07-11
Branch: `gustocezar/feature/codex-desacoplamento-geradores`
Prepared by: Codex

## Decision

Add a canonical Spark rerun template and a bounded polling loop before telemetry comparison.

New public functions and tools:

- `build_spark_submit_rerun_command`
- `poll_for_telemetry` / `poll_telemetry`
- `execute_rerun_poll_and_compare`

## Why

Gate 13 can execute a controlled command, but it compares immediately. In a real Spark + ClickHouse path, telemetry may arrive after the process exits or after an async collector flushes data. Gate 14 makes that delay explicit.

## Data Flow

```text
build_spark_submit_rerun_command
  -> command[]
plan_rerun
  -> approval token
execute_rerun_poll_and_compare
  -> runner.run(command[])
  -> poll_for_telemetry(after_job_id)
  -> compare_job_telemetry
```

## Spark Command Contract

The generated command is an argument list:

```text
spark-submit
  --master local[*]
  --conf spark.apex.jobId=<after_job_id>
  --conf spark.extraListeners=apex.commander.spark.ApexSparkListener
  <app_path>
```

Additional Spark conf and app args may be appended, but the Apex job id and listener are controlled by the template.

## Polling Contract

`poll_for_telemetry` queries the configured store by `job_id` and returns:

- `found` when at least one envelope exists;
- `not_found` when all attempts are exhausted;
- `invalid_poll_attempts` or `invalid_poll_interval` before sleeping or querying with unsafe settings.

## Safety Model

Execution remains guarded by Gate 13:

- configured `rerun_root`;
- command allowlist;
- approval token;
- no shell expansion.

Gate 14 adds:

- path restriction for the app template;
- bounded polling;
- no comparison until telemetry exists.

## Output Shape

Successful path:

```json
{
  "status": "rerun_completed",
  "runner": {"status": "succeeded"},
  "telemetry": {"status": "found"},
  "comparison": {"status": "improved"}
}
```

Missing telemetry:

```json
{
  "status": "telemetry_not_available",
  "runner": {"status": "succeeded"},
  "telemetry": {"status": "not_found"},
  "comparison": {"status": "not_run"}
}
```

## Out Of Scope

- No JVM SparkListener package yet.
- No real Spark CI run yet.
- No production scheduler.
- No rollback automation.
- No remote publication.

## Next Gate

The next natural gate is a real local Spark listener/package path:

```text
Spark job -> Apex listener -> ClickHouse telemetry -> Gate 14 polling compare
```
