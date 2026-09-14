# Task-Spec — STAGE-EXECUTION-ID

## Intent

Preserve Spark SQL `execution_id` on correlated `apex.stage` spans without
synthesizing a value for non-SQL work.

## Scope and contract

- Hypothesis: a SQL stage's existing listener correlation can be carried through
  `ApexStageEvent` and emitted as the optional OTLP Int64 attribute
  `execution_id`.
- Given a Spark SQL stage, when its completion event is emitted, then the span
  carries the same numeric execution id. Given a pure RDD stage or an event with
  no correlation, then the attribute is absent.
- `execution_id` remains Spark SQL correlation only. It does not replace
  `job_id`, `stage_id`, `stage_attempt`, trace IDs, or span IDs, and no sentinel
  value is generated.
- Authorized production scope: the stage event, its listener, and the OTLP sink.
  Collector, ClickHouse DDL/MVs, Engine, Serve, Memory, Verify, and runtime
  harnesses are explicitly out of scope.

## Proof and boundary

- Listener tests cover both activation paths for SQL stages and a pure-RDD
  workload for absence semantics.
- The OTLP test parses the captured protobuf payload, proving `Some(42L)` is an
  Int64 value of `42` and `None` produces no `execution_id` attribute.
- Contract v0.6 ratifies this as an additive producer attribute. Existing
  consumers can ignore it, while a future execution-to-stage attribution gate
  remains a separately scoped, runtime-validated increment.
