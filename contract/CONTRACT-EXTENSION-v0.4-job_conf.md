# Proposed CONTRACT extension v0.4 — `apex.job_conf`

**Status:** 🟡 **PROPOSED — awaiting central ratification.** Built locally in `jar` + `collect` against this proposal; `CONTRACT.md` is intentionally NOT amended until ratified.
**Proposed by:** integration across `jar` + `collect` · **Kind:** purely **additive** (one new span type + one new table; no existing span, column, or table renamed, retyped or repurposed)
**Canonical DDL:** [`job_conf.ddl.sql`](job_conf.ddl.sql)
**Affects:** `jar` (emits) · `collect` (routes) · `infra` (creates the table + MV) · `memory` / `verify` (read — this unblocks both) · `engine` / `serve` (may read; unaffected today)

> **Numbering note:** `verify/`'s `apex.fix_verifications` proposal already holds the **v0.3** slot (still pending ratification itself) and explicitly defers this feature to "a future v0.4". This document takes that v0.4 slot.

---

## The gap this closes

Apex captured **no Spark configuration at all**. `attributes` on `spark_events` just mirrors the typed columns, so nothing downstream can say what config a run had. Two shipped lanes are blocked on exactly this:

- **`memory/`** — its entire ZEST value proposition is answering "the config that worked" for a workload. Without the resolved conf there is nothing to recall.
- **`verify/`** — its **NO-OP GATE** (refuse to recommend a fix that is already active) needs the observed run's effective SparkConf. This is the gate that would have caught Apex's headline false positive: recommending `spark.sql.adaptive.skewJoin.enabled=true` on a run where that flag was **already true**. Today `verify` works around the gap by scraping the History Server REST API, which does not exist in every deployment.

## The event (jar → collect)

One `apex.job_conf` span **per application** (the conf is constant for the run — per-stage emission would be pure duplication), emitted at the **first `onJobStart`**:

- At `onApplicationStart` no `SparkSession` exists yet, so `spark.sql.*` **defaults could not be resolved** — the effective value of an unset flag (e.g. `adaptive.enabled=true` in 3.5/4.x) would be lost. At first job start the session is up and every allowlisted key resolves to its effective value.
- An application that never runs a job emits no row (there is no run to tune).

**Span attributes** (OTLP, snake_case): `job_id`, `app_id`, `app_name`, `ts` (epoch millis) — plus **one string attribute per allowlisted key**, keyed by the Spark key itself (e.g. attribute `spark.sql.adaptive.skewJoin.enabled` = `"true"`).

Rides the same bounded `BatchSpanProcessor` + `Try`/recover as `apex.stage` and `apex.plan_transition` — it cannot block the driver. Behind **`spark.apex.conf.enabled`** (default on). Registered by `ApexPlugin`; also usable standalone via `spark.extraListeners=apex.ApexConfListener`.

### The allowlist (the security boundary)

Exactly 13 keys — ZEST's 6 tunables, the AQE flags the watchers reason about, and the broadcast threshold:

| Group | Keys |
|---|---|
| ZEST tunables | `spark.sql.shuffle.partitions`, `spark.executor.instances`, `spark.executor.cores`, `spark.executor.memory`, `spark.driver.cores`, `spark.driver.memory` |
| AQE flags | `spark.sql.adaptive.enabled`, `.skewJoin.enabled`, `.skewJoin.skewedPartitionThresholdInBytes`, `.skewJoin.skewedPartitionFactor`, `.coalescePartitions.enabled`, `.advisoryPartitionSizeInBytes` |
| Join strategy | `spark.sql.autoBroadcastJoinThreshold` |

**Every value is a number, a byte size, or a boolean. None can carry a credential. The whole conf is NEVER shipped** — a real SparkConf contains `spark.hadoop.fs.s3a.secret.key`, JDBC passwords, OAuth tokens (the dev lane's own `spark-defaults.conf` carries MinIO credentials). This is enforced by a hard-coded allowlist in the jar (`ApexJobConfAllowlist`), tested with decoy credentials in `JobConfSpec` ("secrets never leave the JVM"). A prefix filter (`spark.*` minus a denylist) was rejected: it fails open the day someone puts a secret under a new prefix.

**Resolution semantics (a deliberate contract decision):** `spark.sql.*` keys resolve through the session `RuntimeConfig`, so an unset-but-defaulted flag is captured with its **effective** value (`adaptive.enabled` → `"true"`), and `executor`/`driver` keys come from the SparkConf. A key that is set nowhere is **omitted**, not defaulted — for those there is no single deploy-independent default to report honestly. So: `spark.sql.*` rows are always present with effective values; executor/driver keys are present iff explicitly set.

## The table (collect / infra → ClickHouse)

See [`job_conf.ddl.sql`](job_conf.ddl.sql). Shape:

```sql
CREATE TABLE apex.job_conf (
  job_id   String,
  app_id   String,
  app_name String,
  conf     Map(String, String),   -- allowlisted key -> resolved value
  ts       DateTime64(3)
) ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (job_id)
TTL toDateTime(ts) + INTERVAL 90 DAY DELETE
SETTINGS ttl_only_drop_parts = 1;
```

Routing mirrors the existing pattern: the span lands in `otel_traces` and a MATERIALIZED VIEW (`mv_job_conf`, routing on `SpanName = 'apex.job_conf'`) lifts the 4 identity attributes into typed columns and passes **every remaining attribute** through as the `conf` Map.

## Three decisions that need your explicit sign-off

**1. `conf` as `Map(String, String)` instead of 13 typed columns.**
The Map makes the MV a generic passthrough: adding a key to the jar allowlist needs **no DDL/MV change** (a typed schema forces an ALTER + MV edit per key, in three repos). Values are strings (`"true"`, `"64m"`) exactly as Spark reports them — consumers compare strings, which is what a NO-OP gate does anyway. Alternative: 13 typed columns (`LowCardinality(String)`/UInt64); say if you prefer it and the DDL is a mechanical rewrite.

**2. One row per `job_id`, not per `execution_id`.** The conf is application-constant. Consumers that set `spark.apex.job_id` to correlate a logical job across runs get one row per run sharing that key, and should pick `argMax(conf, ts)` (or filter by `app_id`). Duplicate-row tolerance is the same as `spark_events` (MergeTree, at-least-once).

**3. Emission at first `onJobStart`.** The alternative (`onApplicationStart`) cannot resolve SQL defaults and would report an incomplete conf on exactly the keys verify/ gates on. Trade-off: an app that never runs a job leaves no row. Accepted — there is no run to tune.

## Migration

Additive `CREATE TABLE` + `CREATE MATERIALIZED VIEW` (both `IF NOT EXISTS`). No `ALTER`, no backfill, no reader changes. Clusters that have not applied it simply receive one more unrouted span type in `otel_traces` (a few hundred bytes per application) — no failure mode.

## Built locally against this proposal (pending ratification)

- `jar/`: `ApexJobConf.scala` (allowlist + event), `ApexConfListener.scala` (emit-once), `ApexSink.emitJobConf`, plugin wiring behind `spark.apex.conf.enabled`, `JobConfSpec` (4 tests incl. the credential-leak test) — green on the Spark 3.5/2.13 cell.
- `collect/`: `ddl/23_job_conf.sql` + `ddl/32_mv_job_conf.sql`.
- `infra/`: `sql/013_job_conf.sql` + `sql/021_mv_job_conf.sql` (needed for the canonical e2e proof; same "infra creates the table" split as v0.3's proposal).
- End-to-end proof (dev job → OTLP → collect → canonical ClickHouse → `conf['spark.sql.adaptive.skewJoin.enabled']` answerable) accompanies the ratification report.
