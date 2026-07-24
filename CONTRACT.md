# Apex — The Frozen Contract

> **This is the one file every stage depends on. Freeze it first; change it only by explicit version bump.**
> It defines the data shapes that flow between stages so each directory can be built independently and still fuse.
> A stage may **add** a field; it may never rename or repurpose one. Breaking changes = version bump + a note here.

**Status:** contract **v0.2** · **Consumed by:** `dev` · `jar` · `collect` · `infra` · `engine` · `serve`
**Artifacts:** [`contract/sample_event.json`](contract/) (the fixture) · [`contract/spark_events.ddl.sql`](contract/) · [`contract/findings.ddl.sql`](contract/) · [`contract/plan_transitions.ddl.sql`](contract/)

**Changelog:**
- **v0.2** — ADDITIVE: new optional `plan_transition` event + `apex.plan_transitions` table (AQE runtime-decision capture — Spark's own optimization decisions as ground-truth signal). Existing `spark_events`/`findings` unchanged. See § "AQE plan transitions" below. Affects: `jar` (emits), `collect` (routes), `infra` (creates table), `engine`/`serve` (may read).

---

## The trace key

Everything is threaded by **`job_id`** — a stable id for one Spark application run (the Spark `applicationId`, or a UUID via `spark.apex.job_id`). Every event, row, finding, and MCP call carries it. Example: `job_id = "ax151sasadds114"`.

```
dev  ──[job_id]──►  jar  ──[job_id]──►  collect  ──[job_id]──►  infra  ──[job_id]──►  engine  ──[job_id]──►  serve
```

## The telemetry event (jar → collect)

One event **per completed stage**, OTLP/HTTP to the collector on `:4318`. Fields (snake_case, exact):

- **Identity:** `job_id`, `app_id`, `app_name`, `stage_id`, `stage_attempt`, `ts` (epoch millis).
- **Stage metrics** (from `stageInfo.taskMetrics`): `shuffle_read_bytes`, `shuffle_write_bytes`, `spill_disk_bytes`, `spill_mem_bytes`, `gc_time_ms`, `input_bytes`, `output_bytes`, `peak_execution_mem_bytes`, `task_count`, `task_duration_p50_ms`, `task_duration_p99_ms`.
- **Plan:** `plan_fingerprint` (SHA-256 of the **normalized LOGICAL** plan — **not** physical), `plan_json` (redacted Catalyst **tree-string**, NOT JSON — e.g. `Filter (order_ts#2 >= null)`; both listeners converged on this; don't parse it as JSON downstream).
  - ⚠️ **`optimizedPlan.canonicalized` is NOT sufficient alone** (verified empirically, jar T7): it does **not** normalize literal *values*, so `id > 100` and `id > 900` hash differently — which fails the "same query, different literals → same fingerprint" requirement and would break `compare_runs` regression detection. **Every listener (jar Scala AND dev Python) MUST apply a literal-normalization pass on top of the canonicalized logical plan before hashing.** Still purely logical, never physical. Cross-version stable (verified identical Spark 3.5 ↔ 4.0).

The canonical values live in [`contract/sample_event.json`](contract/) — build `engine/` and `serve/` against it.

## The store (infra owns application, contract owns the schema)

Database `apex`. Canonical DDL in [`contract/`](contract/):
- **`spark_events`** — MergeTree, `PARTITION BY toYYYYMM(ts)`, `ORDER BY (job_id, stage_id)`, one row per stage.
- **`findings`** — one row per detected issue (`engine/` writes, `serve/` reads).
- **`plan_transitions`** *(v0.2, optional)* — one row per AQE runtime re-plan (see below).

## AQE plan transitions (v0.2 — the ground-truth signal that beats DataFlint)

> **Why this exists:** DataFlint & sparkMeasure only aggregate `TaskEnd` *symptoms* (shuffle bytes, spill, p50/p99). This captures Spark's own *decisions* — when AQE splits a skewed join, demotes a sort-merge join to broadcast, or coalesces partitions at runtime. That turns a heuristic finding ("p99/p50 = 52× → probably skew", needs an LLM) into a **ground-truth finding at $0** ("AQE split this join into N subpartitions"). It's the causal *why* layer neither competitor has.

**Mechanism (jar):** a `SparkListener` overriding `onOtherEvent`, pattern-matching `SparkListenerSQLAdaptiveExecutionUpdate` (fires **live** on the driver bus, verified against `AdaptiveSparkPlanExec.onUpdatePlan`, `@DeveloperApi`, identical Spark 3.5↔4.0). The event is a **snapshot** of the current physical plan — the JAR keeps the prior snapshot per `execution_id` and diffs consecutive ones to derive the transition. Behind `spark.apex.aqe.enabled` (default on). Rides the same OTLP sink + bounded queue + `Try/recover`; emits a distinct span `apex.plan_transition`.

**Event fields** (OTLP attributes, snake_case):

| Field | Type | Notes |
|---|---|---|
| `job_id` | string | = `applicationId` (constant, always present) |
| `execution_id` | int64 | the SQL execution id (AQE's correlation key) |
| `update_seq` | int32 | monotonic per `execution_id` (0,1,2… as AQE re-plans) |
| `transition_type` | string | `join_switch` \| `skew_split` \| `coalesce` \| `local_read` \| `other` |
| `detail` | string | structured descriptor (e.g. `"SortMergeJoin→BroadcastHashJoin"`, `"200→17 partitions"`) — **redacted, no literals** |
| `before` | string | prior structural descriptor (redacted) |
| `after` | string | new structural descriptor (redacted) |
| `confidence` | string | `HIGH` (node-type delta / AQEShuffleRead descriptor) \| `BEST_EFFORT` (exact counts from simpleString) |
| `ts` | int64 | epoch millis |

**Detection tiers (honesty on reliability):** join-strategy switch (`SortMergeJoinExec`/`ShuffledHashJoinExec` → `BroadcastHashJoinExec`) and skew/coalesce (`AQEShuffleReadExec.hasSkewedPartition`/`hasCoalescedPartition`) = **HIGH** confidence (structural). Exact before/after partition counts = **BEST_EFFORT** (parsed from `simpleString`/metrics).

**Stage linkage:** keyed by `(job_id, execution_id)` first cut. Linking a transition to specific `stage_id`s needs an `execution_id→job→stage` map (from `spark.sql.execution.id` in `onJobStart` properties) — a later enhancement, not blocking.

**Redaction:** `physicalPlanDescription` is full plan text with literals — **never shipped raw.** Only structured descriptors are emitted; redact like `plan_json` (§ Redaction).

**DDL** — canonical in [`contract/plan_transitions.ddl.sql`](contract/):
```sql
CREATE TABLE apex.plan_transitions (
  job_id          String,
  execution_id    Int64,
  update_seq      Int32,
  transition_type LowCardinality(String),   -- join_switch|skew_split|coalesce|local_read|other
  detail          String,
  before          String,
  after           String,
  confidence      LowCardinality(String),   -- HIGH|BEST_EFFORT
  ts              DateTime64(3)
) ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (job_id, execution_id, update_seq);
```

**Deferred (NOT in v0.2):** per-SQL-node metric *values* (rows/bytes per operator). The node→`accumulatorId` map is free from `SparkPlanInfo.metrics`, but the *values* require correlating `DriverAccumUpdates` (a subset) with task-side accumulators — a non-trivial two-stream join. Revisit if the value justifies it.

## The Finding (engine → serve)

Pydantic model whose field names match the `findings` table exactly: `job_id`, `app_id`, `type` (skew|spill|shuffle|memory|cost|code), `severity` (info|warning|critical|blocker), `stage_id`, `evidence`, `impact`, `fix`, `confidence` (0–1).

## Redaction (enforced in two places)

Plan/query text carries PII → **redact in-JVM before egress** (`jar/`, primary) with the collector as a second net (`collect/`): hash `query_text`, drop `file_path`/`email`, strip `plan_json` literals. `plan_fingerprint` is computed upstream and passed as an opaque value — redaction never recomputes it.

## Port Map (all lanes share one dev host — reserve these, no collisions)

Every lane's `docker-compose` runs on the **same developer host**. To avoid the collisions we've already hit (dev MinIO ↔ ClickHouse :9000; HyperDX would collide with Spark master :8080), each lane owns a distinct **host-port band**. Container-internal ports stay standard; only the **host** mapping is reserved here. Parametrize host ports via `.env` so they can be overridden, but default to these.

| Lane | Service | Host port | Notes |
|---|---|---|---|
| **dev** | Spark master UI | **8080** | already assigned |
| dev | Spark master RPC | **7077** | |
| dev | Spark worker UI | **8081** | |
| dev | Spark History | **18080** | |
| dev | MinIO S3 API | **9010** | shifted off 9000 to avoid ClickHouse |
| dev | MinIO console | **9001** | |
| **collect** | OTLP/HTTP receiver | **4318** | jar → collect transport (contract §transport) |
| collect | OTLP/gRPC (optional) | **4317** | |
| collect | health_check | **13133** | |
| **infra** | ClickHouse HTTP | **8123** | |
| infra | ClickHouse native | **9000** | dev's MinIO is on 9010 precisely to leave this free |
| infra | HyperDX UI | **8090** | ⚠️ NOT 8080 (dev Spark master owns it) |
| infra | HyperDX OpAMP | **4320** | |
| infra | MongoDB | **27017** | HyperDX app state |
| **serve** | MCP is **stdio** | — | no host port; spawned as a subprocess |
| **engine** | (library; no server) | — | reads ClickHouse on infra's ports |

**Rule:** a lane binds only its own band. If you need a port not listed, add it here first (a new host-port reservation is an additive contract change). `collect` and `infra` connect to ClickHouse via the **internal** docker network (`clickhouse:8123`/`:9000`), not the host ports — the host ports are only for a human/tool reaching in.

## Activation (how a job turns Apex on)

```python
# Real coordinates as published by the jar lane (sbt +publishLocal → ~/.ivy2/local):
#   apex_3.5_2.12 · apex_3.5_2.13 · apex_4.0_2.13  (version 0.1.0)
# Pick the cell matching your Spark/Scala. Example for Spark 4.0 / Scala 2.13:
SparkSession.builder \
  .config("spark.jars.packages",   "io.dataship:apex_4.0_2.13:0.1.0") \
  .config("spark.plugins",         "apex.ApexPlugin") \
  .config("spark.apex.otlp.endpoint", "http://collect:4318") \
  .config("spark.apex.aqe.enabled", "true")   # captures AQE plan_transitions
# Fallback (stage events only, no AQE, no clean-shutdown flush):
#   .config("spark.extraListeners", "apex.ApexStageListener")
```

> **Config keys (verified against the built jar):** `spark.plugins=apex.ApexPlugin` (primary) or `spark.extraListeners=apex.ApexStageListener` (fallback) · `spark.apex.otlp.endpoint` (base URL; Apex appends `/v1/traces`) · `spark.apex.service.name` · `spark.apex.aqe.enabled` · `spark.apex.job_id`. See [`jar/README.md`](jar/README.md) for the full table.

---

*The full, authoritative version of this contract (with every field's type + Spark source) is the original `LANE-0-CONTRACT.md`. This top-level copy is the always-visible summary; the `contract/` dir holds the enforceable artifacts. Keep them in sync on any change.*
