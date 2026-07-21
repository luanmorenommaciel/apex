# contract/ — the frozen interface (as artifacts)

The enforceable half of [../CONTRACT.md](../CONTRACT.md). Every stage builds against these files; obey the field names exactly.

| File | What it is | Who uses it |
|---|---|---|
| `sample_event.json` | One canonical telemetry event (the fixture) | `engine/` + `serve/` build against it **before `jar/` is real** — load it into ClickHouse and the brain is unblocked |
| `spark_events.ddl.sql` | Canonical `CREATE TABLE apex.spark_events` | `infra/` applies it (+ partitioning/TTL/rollups); `engine/`/`serve/` read it |
| `findings.ddl.sql` | Canonical `CREATE TABLE apex.findings` | `engine/` writes; `serve/` reads |
| `plan_transitions.ddl.sql` | Canonical `CREATE TABLE apex.plan_transitions` (v0.2) | AQE-decision rows; `engine/`/`serve/` may read |

**Status:** all artifacts are populated and verified against real `jar`/`dev`/`collect` implementations.

> ⚠️ **Loading the fixture into ClickHouse — TTL gotcha:** the tables have a **90-day TTL on `ts`**. The fixture's `ts` (`1718553999000` ≈ June 2024) is **older than 90 days**, so a raw insert **TTL-expires immediately** — the INSERT succeeds but `count()` stays 0 (confirmed by the `collect` lane). **When loading the fixture, override `ts` to `now()`** (or a recent timestamp). Production events are near-real-time so this only affects fixture replay in `engine`/`serve` testing.

> Rule: a stage may **add** a column; it may never rename or repurpose one. Any change here = version bump in [../CONTRACT.md](../CONTRACT.md).
