# C11 - Canonical pathology rerun (2026-07-25)

## Scope and boundary

This record applies only to `base-project-e2e-augusto`. It does not modify,
approve, or claim a merge into Luan's `feat/base-project-e2e` branch.

The run used local Spark 4.1.2, `apex.ApexPlugin`, the OTLP collector and
canonical ClickHouse. All reported credentials stayed in ignored local
environment files; this document contains no secret values.

## Fresh real-pathology evidence

| Scenario | Fresh Spark app id | Canonical assertion | Result |
|---|---|---|---|
| deterministic data | `app-20260725015101-0001` | 5,000,000 rows; hot-key fraction `0.5003` | passed |
| `skew_join` | `app-20260725020700-0002` | p99/p50 maximum `39.946`, 12 stages | passed |
| `spill` | `app-20260725022235-0003` | `103,708,706` spill bytes, 14 stages | passed |
| `bad_shuffle` | `app-20260725023759-0004` | stage `15`, two tasks, large shuffle read, 13 stages | passed |
| `driver_oom` | `app-20260725031911-0006` | expected `java.lang.OutOfMemoryError`; 9 pre-failure stages persisted | passed |

`driver_oom` was first attempted as `app-20260725030806-0005`. That attempt
was stopped before the intended failure after its old Delta preflight stalled.
It is not counted as a passing result. The replacement app `...0006` is the
only driver-OOM result used above.

## Runtime improvement made during the rerun

`dev/common/data.py` previously used `limit(1).collect()` to decide whether
the shared Delta inputs existed. Each pathology therefore paid for one or more
distributed reads before its actual workload. The helper now checks S3A for a
committed JSON transaction in `_delta_log`, avoiding a Spark action while
preserving the practical definition of a materialized Delta table.

The fresh driver-OOM app reached its intentional pre-collection stage and
produced the expected heap failure after this change. This is operational
evidence that the preflight no longer blocks the path; it is not a benchmark
claim for all storage backends.

## Renewed six-lane gate

The pathology assertions above validate `DEV -> JAR -> COLLECT -> INFRA` for
the listed applications. The separate six-lane gate was then run against the
fresh skew application:

| Gate | App id | Result |
|---|---|---|
| `scripts/e2e_six_lanes.py` | `app-20260725020700-0002` | passed: 17 canonical stage events/fingerprints, 4 deterministic findings, 0 LLM calls, 0 validator rejections, read-only `analyze_run` |

SERVE returned diagnostic status `degraded` because the pathological job has
four findings; the gate still passed because its tool is read-only and its
findings exactly match ENGINE persistence. This is the intended product state,
not a successful-job health label.

The initial six-lane attempt exposed an old local `apex.findings` schema
without v0.2 additive columns. `infra/sql/021_findings_v02_additive.sql` and
`infra/scripts/apply_schema_migrations.ps1` now make that upgrade explicit and
idempotent for retained ClickHouse volumes. The rerun passed after migration.
