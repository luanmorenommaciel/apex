# Apex — The Frozen Contract

> **This is the one file every stage depends on. Freeze it first; change it only by explicit version bump.**
> It defines the data shapes that flow between stages so each directory can be built independently and still fuse.
> A stage may **add** a field; it may never rename or repurpose one. Breaking changes = version bump + a note here.

**Status:** contract **v0.5** · **Consumed by:** `dev` · `jar` · `collect` · `infra` · `engine` · `serve` · `memory` · `verify`
**Artifacts:** [`contract/sample_event.json`](contract/) · [`spark_events`](contract/spark_events.ddl.sql) · [`findings`](contract/findings.ddl.sql) · [`plan_transitions`](contract/plan_transitions.ddl.sql) · [`job_conf`](contract/job_conf.ddl.sql) · `memory/sql/030_plan_memory.sql` · `memory/sql/031_run_outcomes.sql` · `verify/ddl/fix_verifications.ddl.sql`

**Changelog:**
- **v0.5** — ADDITIVE: ~15 OTLP keys for retry-safe task analysis. All columns default to 0 for historical events; consumers must treat `sample_count=0` as "no sample available" (0-on-empty semantics).
  - **Tail-outlier visibility:** `task_duration_max_ms` (maximum task duration) + `task_duration_sample_count` (attempts with duration available).
  - **Retry-safe successful-task sample:** `successful_task_duration_p50_ms`, `successful_task_duration_p99_ms`, `successful_task_duration_max_ms`, `successful_task_sample_count` — one successful attempt per logical partition, excluding retries/speculation.
  - **Shuffle-read distribution:** `successful_task_shuffle_read_bytes_p50`, `successful_task_shuffle_read_bytes_max`, `successful_task_shuffle_read_bytes_sample_count`.
  - **Task-termination counters:** `task_attempt_count` (all `onTaskEnd` events), `task_failed_attempt_count` (`TaskInfo.failed=true`), `task_counted_failure_attempt_count` (scheduler budget via `countTowardsTaskFailures`), `task_killed_attempt_count` (`TaskInfo.killed=true`), `task_speculative_attempt_count`.
  - **Executor runtime:** `executor_run_time_ms` (Spark's measured executor wall-clock runtime).
  - **Convention:** unfinished task durations do not enter percentiles; only tasks with a measured duration feed `task_duration_*` / `successful_task_duration_*`. Absence of duration is not represented by zero — check `sample_count`. ENGINE prefers `successful_*` when `successful_task_sample_count > 0` and falls back to legacy fields for historical events.
  - Affects: `jar` (emits), `collect`+`infra` (store), `engine`/`memory`/`verify` (read).
- **v0.4** — ADDITIVE: `apex.job_conf` (one row per `job_id`, `conf Map(String,String)` of an **allowlisted** resolved `spark.*` subset). Emitted at **first `onJobStart`**, NOT `onApplicationStart` — at ApplicationStart no SparkSession exists, so `spark.sql.*` defaults cannot be resolved and you would lose `adaptive.enabled` on exactly the keys the no-op gate depends on. **Allowlist only, never a whole-conf dump** (SparkConf can hold s3a keys / JDBC passwords / tokens). Resource keys (`spark.executor.*`/`spark.driver.*`) are present **iff explicitly set** — never synthesized, because a fabricated default poisons "the config that worked". Affects: `jar` (emits), `collect`+`infra` (route/store), `engine`/`memory`/`verify` (read).
- **v0.3** — ADDITIVE: `apex.plan_memory` + `apex.run_outcomes` (cross-job plan-similarity memory: fuzzy structural index + per-run outcome evidence) and `apex.fix_verifications` (predicted/replayed fix outcomes). No existing table changed.
- **v0.2** — ADDITIVE: `plan_transition` event + `apex.plan_transitions` (AQE runtime-decision capture). Existing tables unchanged.

---

## Seven cross-lane rules (derived from real data — every consumer must honor these)

**1. Skew is only worth fixing if the stage is TAIL-BOUND.** From list-scheduling makespan bounds (derived and independently re-verified):

> **tail-bound ⟺ `p99/p50 > (n_tasks − 1) / (slots − 1)`**

Data volume **cancels out** (it scales `p50` and `p99` together), so the threshold depends only on **task count and cluster width**. A 21.6× ratio is worthless advice on 2 slots (needs > 49×) and sound advice on 50 slots (needs > 1×). **A fixed `5×`/`10×` skew threshold is wrong** — it must be computed per stage. `slots` comes from the observed cluster width; if it cannot be determined, confidence is capped, never guessed. *Empirically validated: a balanced control stage manufactures 8–12× ratios from jitter alone but never passes the closed form (9.3/11.9/7.7 vs its 28.4 threshold), while a genuinely skewed stage always does.*

**2. The noise floor is SCALE-DEPENDENT and must be MEASURED, never hardcoded.** Observed on the same system: **5.8%** (job level, tiny scale) → **9.2%** (job level, calibrated scale) → **37.7%** (shape level, 8 tasks, byte-identical work). Measure it at the level and scale you are comparing. When `|delta| < measured_floor`, **no consumer may render the number**. Noise proves a delta is *unresolvable* — never that it is *zero*.

**3. A delta is only creditable to tuning if it is ATTRIBUTABLE.** If history holds **fewer than 2 distinct configurations**, no observed difference between runs can be credited to a config change — it is run-to-run variance. Passing the noise floor is **necessary but not sufficient**. (Real case: byte-identical shuffle/spill across 4 runs still spanned 18.65% in task time, which clears a 5.8% floor and would have shipped as a confident win.) Values must be **canonicalized** before counting distinct configs: `'5.0'` and `'5'` are one setting in two spellings, while `'8m'` vs `'67108864b'` is a real 8× difference.

**4. MECHANISM-level and RUNTIME-level evidence are separate verdicts.** A fix can be *proven to have worked mechanically* while its *runtime effect is unresolvable*. These must never be conflated:

| Verdict | Claim | Requires |
|---|---|---|
| **mechanism_confirmed** | "AQE split the skewed partitions; the tail ratio collapsed 18–24× → 1.4–2.6×" | the structural change is observable (e.g. a `skew_split` transition, a ratio collapse well above its own floor). **Does NOT require clearing the runtime floor.** |
| **runtime_certified** | "−9.9% wall clock" | `\|delta\| ≥ measured floor` at the compared level **and** ≥2 distinct configs (rules 2–3) |
| **runtime_unresolved** | "the effect is below what this bench can resolve" | the honest verdict when the mechanism fired but the magnitude can't clear the floor |

Reporting `runtime_unresolved` alongside `mechanism_confirmed` is **more useful and more honest** than a fabricated percentage. A laptop-scale bench with ~1.2s/stage fixed scheduling overhead on a ~2s stage puts a 17–23% floor under everything — a ~10% effect is *structurally* uncertifiable there, regardless of reps. **Runtime certification of small effects requires a cluster where the stage is long enough to amortize fixed overhead.** Adding reps does not fix this: on a shared host, reps are not independent (background load correlates), so shrinking a standard error is measuring the wrong thing.

> ⚠️ **Corollary — pick a positive control the predictor can model.** AQE `skew_split` typically *coalesces* partitions too (e.g. 100 → 17), so W is **not** conserved and it is a repartitioning, not a pure tail redistribution. A predictor that (correctly) refuses the makespan bound for partition-sizing changes cannot certify such a control. Choose a control whose fix class the model handles.

**5. `skew_split` gating on exchange bytes creates a false-NEGATIVE class.** AQE only splits a partition exceeding `skewedPartitionThresholdInBytes`, so any downstream query shape that **prunes to a narrow key** (`groupBy(k).count()`, `select(k).count()`, …) shrinks the exchange and silently disqualifies an otherwise genuinely skewed stage. *Real case: a 5M-row / 65MB table produced only a 10.6MB exchange and a ~5MB hot partition — under the 16m threshold — so `skew_split` never fired for reasons that had nothing to do with data volume.* Absence of a `skew_split` transition is **not** evidence of absence of skew.

**6. Rule 1 is VACUOUS when `n_tasks ≤ slots`, and must not be applied there.** The bar is `(n−1)/(slots−1)`, so `bar ≤ 1` **exactly when** `n ≤ slots` — and `p99/p50 ≥ 1` always. Therefore *every* stage with `n ≤ slots` satisfies rule 1 unconditionally, **including a perfectly uniform one**. This is arithmetic, not an edge case.

*Real case (`app-20260729182801-0045`, 8 slots): stage 25 at ratio **1.03** (bar 1.0), stage 12 at **1.01** (bar 0.43), stage 2 at **1.00** (bar 0.43) — all "tail-bound." Stage 25 was the only symptom to survive every other gate, and it is perfectly balanced; it is what a consumer then promoted to "critical skew."*

The verdict is *technically* correct — with a single wave, makespan **is** the longest task — but it carries **zero information about skew**, because it holds for every such stage. A stage with `n ≤ slots` cannot be helped by redistribution at all: every task already owns a slot. **Exclude `n ≤ slots` stages from rule-1 skew reasoning rather than passing them.** Where cluster width is UNKNOWN, this exclusion is unavailable — one more reason a rule-1 verdict at unknown width may never carry full confidence.

**7. A threshold evaluated on POST-INTERVENTION telemetry measures the healed state.** AQE reshapes a stage *before* the plugin observes it, so the metrics that arrive already reflect the fix. Any per-task threshold applied to them is compared against a bound derived for the *pre*-intervention shape.

*Real case: stage 29's exchange of 113,632,037 bytes over its original `spark.sql.shuffle.partitions=100` is **1,136,320 B/task — 1.084 MiB, above the 1 MiB floor**. AQE split it into **114** tasks, giving 996,772 B/task = 0.951 MiB — **below** the floor. The stage was disqualified by the dilution its own fix produced.*

This is **not** a threshold-tuning problem: lowering the cut to 950 KiB only relocates the boundary and rescues a different arbitrary stage. Detect the reshape instead — `task_count > spark.sql.shuffle.partitions` (joinable via `apex.job_conf`) marks an AQE-reshaped stage, whose pre-intervention shape must be reconstructed before any per-task bound is applied to it. **Do not soften a measurability bound to compensate for a timing artifact.** (Credit: serve lane.)

---

## The trace key

Everything is threaded by **`job_id`** — a stable id for one Spark application run (the Spark `applicationId`, or a UUID via `spark.apex.job_id`). Every event, row, finding, and MCP call carries it. Example: `job_id = "ax151sasadds114"`.

```
dev  ──[job_id]──►  jar  ──[job_id]──►  collect  ──[job_id]──►  infra  ──[job_id]──►  engine  ──[job_id]──►  serve
```

## The telemetry event (jar → collect)

One event **per completed stage**, OTLP/HTTP to the collector on `:4318`. Fields (snake_case, exact):

- **Identity:** `job_id`, `app_id`, `app_name`, `stage_id`, `stage_attempt`, `ts` (epoch millis).
- **Stage metrics** (from `stageInfo.taskMetrics`): `shuffle_read_bytes`, `shuffle_write_bytes`, `spill_disk_bytes`, `spill_mem_bytes`, `gc_time_ms`, `executor_run_time_ms` *(v0.5)*, `input_bytes`, `output_bytes`, `peak_execution_mem_bytes`, `task_count`, `task_duration_p50_ms`, `task_duration_p99_ms`, `task_duration_max_ms` *(v0.5)*, `task_duration_sample_count` *(v0.5)*.
- **Successful-task sample** *(v0.5, retry-safe)*: `successful_task_duration_p50_ms`, `successful_task_duration_p99_ms`, `successful_task_duration_max_ms`, `successful_task_sample_count`, `successful_task_shuffle_read_bytes_p50`, `successful_task_shuffle_read_bytes_max`, `successful_task_shuffle_read_bytes_sample_count`.
- **Task-termination counters** *(v0.5)*: `task_attempt_count`, `task_failed_attempt_count`, `task_counted_failure_attempt_count`, `task_killed_attempt_count`, `task_speculative_attempt_count`.
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

> ⚠️ **Interpreting transition_type (verified on real data, engine T-Tier1):** `skew_split` **is** a ground-truth SKEW finding — it upgrades an ambiguous 5–10× p99/p50 heuristic to HIGH so it emits free. But `coalesce` is **NOT skew** — it means over-provisioned `spark.sql.shuffle.partitions` (Spark merged too-small partitions), so consumers (`engine`) must report it as a *partition-sizing* finding, not skew. Calling `coalesce` skew is a false positive. `join_switch` = a broadcast-eligibility finding. Only `skew_split` corroborates the skew watcher.

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

Pydantic model whose field names match the `findings` table (see [`contract/findings.ddl.sql`](contract/findings.ddl.sql) — the DDL is authoritative if prose disagrees): `finding_id`, `job_id`, `app_id`, `stage_id`, `type`, `severity` (`info|warning|critical|blocker`), `evidence`, `hot_key`, `impact`, `fix`, `detected_by`, `ts`, and **two** confidence fields — `confidence` = the human tier `Enum8('LOW','MEDIUM','HIGH')` (drives display) and `confidence_score` = the raw `Float32` 0–1 (drives engine's escalation gate + serve's `compare_runs`). *(v0.2: `app_id` + `confidence_score` are additive columns; engine follows the DDL.)*

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

*This file is the authoritative contract. [`contract/`](contract/) holds the enforceable artifacts — the DDL each lane mirrors and the `sample_event.json` fixture — and `make verify-ddl` asserts the store matches them byte-for-byte. An earlier `LANE-0-CONTRACT.md` described contract v0.1 and was removed at v0.4; it had been superseded field-by-field and kept only as a trap for anyone who read it.*
