# apex-v0.1 — Detailed Technical Guide

> Local platform for **Spark execution optimization and observability**. It stands
> up a Spark 4.1.2 + Delta lakehouse on MinIO, captures Spark's native event logs,
> normalizes everything into ClickHouse, and runs deterministic diagnostics (plus
> an optional CrewAI layer) that turn raw execution metrics into `spark.conf`
> recommendations.

---

## Table of contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [End-to-end pipeline](#3-end-to-end-pipeline)
4. [Stage 1 — Capturing event logs](#4-stage-1--capturing-event-logs)
5. [Stage 2 — Idempotent ingestion](#5-stage-2--idempotent-ingestion)
6. [ClickHouse table catalog](#6-clickhouse-table-catalog)
7. [Stage 3 — Detecting errors and problems](#7-stage-3--detecting-errors-and-problems)
8. [Stage 4 — ClickStack / HyperDX](#8-stage-4--clickstack--hyperdx)
9. [Synthetic workloads](#9-synthetic-workloads)
10. [Full experiment cycle](#10-full-experiment-cycle)
11. [Spark application utilities](#11-spark-application-utilities)
12. [MCP server](#12-mcp-server)
13. [Tests](#13-tests)
14. [Make command reference](#14-make-command-reference)
15. [Machine requirements and versions](#15-machine-requirements-and-versions)

---

## 1. Overview

**What.** `APEX-v0.1` (internal package `apex-v0.1`, images `apex-v01-*`) is a
self-contained, laptop-scale environment for studying Spark performance and
building agent workflows that reason about real Spark runs.

**Why.** There is no agent installed in the jobs. Observability comes from Spark's
**native event log**, kept in MinIO as a replayable source, normalized into
ClickHouse, and analyzed by deterministic detectors. It is a study bench for
agent-driven Spark optimization.

**How.** Everything runs from project-local Docker images built from local
dependency caches — `make compose` never silently pulls images nor drifts.

### Stack

| Component | Version | Role |
|-----------|---------|------|
| Apache Spark | 4.1.2 (`scala2.13`, `java17`) | Execution engine (`spark-submit`, `client` deploy) |
| Delta Lake | 4.2.0 | Lakehouse table format |
| Hadoop AWS (S3A) | 3.4.2 | S3A connector for MinIO |
| MinIO | RELEASE.2025-09-07 | S3-compatible object store (lakehouse + event logs) |
| ClickHouse | 26.5.1 | Analytical store for execution telemetry |
| HyperDX (ClickStack) | 2-beta | UI over the observability tables (MongoDB-backed) |
| eventlog-loader | Go 1.26 | On-demand loader: event logs → ClickHouse |
| CrewAI | ≥ 1.15.1 | Optional LLM layer that interprets findings |
| uv / Python | ≥ 3.10 | Project tooling and test environment |

---

## 2. Architecture

The core decision: **MinIO** is the durable object store for raw data;
**ClickHouse** is the analytical store for parsed execution observability.

![apex platform data flow: one Spark engine feeds a lakehouse data plane (MinIO lakehouse bucket to Delta medallion tables) and an execution-observability plane (MinIO spark-logs bucket to Spark History and the Go loader, into ClickHouse, then out to HyperDX and apex_diagnostics)](diagrams/platform-data-flow.png)

### Image model

- All services run from project-local images after `make build`. The base images
  are still official upstream, but Compose points only at local tags, so
  `make compose` does not pull or drift.
- Each Docker build uses **only its own directory** as context; no build receives
  the whole project tree.
- Spark master and workers share the same runtime image (`apex-v01-spark:4.1.2`) —
  intentional: master, worker, submit client, and History Server are all commands
  from the same Spark 4.1.x distribution.
- Spark History uses a thin dedicated image (`apex-v01-spark-history:4.1.2`) that
  extends the runtime image and only changes the entrypoint.
- MinIO has two image definitions (`build/images/minio`) because MinIO server and
  client are separate upstream images. The client image contains `init-buckets.sh`,
  which waits for the MinIO API, creates the `lakehouse` and `spark-logs` buckets,
  the `bronze/`, `silver/`, `gold/` lakehouse prefixes, and the `events/` prefix
  used by the event logs.

### Dependency model

- Spark JVM dependencies are resolved once by `make bootstrap` into
  `build/config/spark/jars`. Before `make build`,
  `build/scripts/prepare-image-contexts.sh` stages the Spark context under
  `build/images/spark/context`. The runtime image copies those jars — **no Maven**
  during `make build` or `spark-submit`.
- Spark Python dependencies live in `build/images/spark/requirements.txt`. Bootstrap
  downloads wheels into `build/cache/python-wheels`; the image installs from cache.
- `pyspark` and `delta-spark` are **not** installed via pip: the official Spark
  image owns PySpark, and Delta comes through Scala jars.

### Why event logs go to MinIO first

`spark.eventLog.dir` requires a filesystem-compatible destination (`file://`, HDFS,
`s3a://`). ClickHouse is an analytical database, not a Hadoop-compatible filesystem
— pointing Spark straight at it is not a valid event-log target. Keeping the raw
logs in MinIO gives a **replayable source of truth**: if the parser changes, the
schema evolves, or a loader bug appears, the logs can be reprocessed without
rerunning the jobs.

### Why the loader is manual

The loader runs on demand via `make spark-logs`; it is **deliberately** not a
long-running service in v0. The local flow — `make compose` → run jobs →
`make spark-logs` — keeps failure modes clear and is easy to wrap in Make/CI later.

### Local state and permissions

Compose keeps MinIO and ClickHouse state in bind mounts under `build/var`, for
inspection without Docker volume tooling. The tradeoff is host file-ownership
friction (services may write as container users/root). That is why `make clean-data`
first tries a normal cleanup and, on failure, falls back to a temporary Docker
container running as root that deletes only the `build/var` state (uses
`--pull=never`; downloads nothing). The Spark runtime and History return to the
upstream `spark` user (`uid=185`) after the build steps.

---

## 3. End-to-end pipeline

The full path, from `spark-submit` to ClickStack, in four stages:

![End-to-end pipeline: spark-submit produces event logs in MinIO spark-logs (.zstd), which Spark History reads and the Go eventlog-loader loads into ClickHouse; deterministic detectors and Crew A produce spark_diagnostic_reports, and ClickStack/HyperDX visualizes everything](diagrams/dd-pipeline-e2e.png)

| Stage | What happens | Command |
|-------|--------------|---------|
| **[1] Capture** | The Spark driver emits JSON events (`JsonProtocol`) to `s3a://spark-logs/events/` as `.zstd` files | `make smoke` / `make workloads` |
| **[2] Ingestion** | `eventlog-loader` (Go) reads the event logs and writes normalized + raw tables into ClickHouse | `make spark-logs` |
| **[3] Detection** | Deterministic detectors → findings → Crew A (optional LLM) → `spark_diagnostic_reports` | chained in `make spark-logs` |
| **[4] Visualization** | HyperDX/ClickStack queries ClickHouse: 9 sources, 10 dashboards, 5 alerts | `http://127.0.0.1:28088` |

The Spark History UI (`:28080`) reads **exactly the same** event-log files — it is
just another view of the same source.

---

## 4. Stage 1 — Capturing event logs

There is no agent in the jobs: capture uses Spark's native event log, enabled in
`build/config/spark/spark-defaults.conf`:

```text
spark.eventLog.enabled true
spark.eventLog.dir s3a://spark-logs/events
spark.history.fs.logDirectory s3a://spark-logs/events   # History reads the SAME directory
spark.eventLog.logStageExecutorMetrics true
```

During execution, the driver serializes each event from the internal bus
(`SparkListenerEvent`) as one JSON line and writes it to MinIO in
`eventlog_v2_<app_id>/events_*.zstd` files (event log v2, Zstandard-compressed).

### Relevant events and what they carry

| Event | What it carries |
|-------|-----------------|
| `SparkListenerApplicationStart/End` | `app_id`, application name, timestamps |
| `SparkListenerJobStart/End` | `job_id`, the job's stages, result (`JobSucceeded`/`JobFailed`) |
| `SparkListenerStageCompleted` | `stage_id`, name, task count, submission/completion |
| `SparkListenerTaskEnd` | **Task Metrics**: duration, CPU, peak memory, shuffle read/write, `JVM GC Time`, `Memory/Disk Bytes Spilled`, and `Task End Reason` (success or the exception) |
| `SparkListenerSQLExecutionStart/End` | `execution_id`, initial physical plan, `error_message` at the end |
| `SparkListenerSQLAdaptiveExecutionUpdate` | each AQE re-plan (updated physical plan) |

Beyond these, `spark_raw_events` keeps **every** event-log line — full coverage for
exploring fields not yet normalized (e.g. `SparkListenerExecutorMetricsUpdate`,
`SparkListenerEnvironmentUpdate`, `SparkListenerStageExecutorMetrics`,
`SparkListenerTaskStart`, etc.).

> **Outside the event log (not ingested):** driver/executor stdout/stderr/log4j,
> Docker container logs, History process logs, MinIO/ClickHouse service logs. Those
> would be a separate ingestion path.

---

## 5. Stage 2 — Idempotent ingestion

`make spark-logs` runs the `eventlog-loader` container
(`build/images/eventlog-loader/main.go`, Go):

![Stage 2 — idempotent ingestion: the loader lists objects in MinIO spark-logs, checks the etag in spark_eventlog_files (skips if already ingested), parses NDJSON decompressing zstd, and writes spark_raw_events plus the normalized tables; schema.sql (CREATE/ALTER IF NOT EXISTS) defines the tables on every run](diagrams/dd-ingestion-loader.png)

1. **Lists** the objects under `spark-logs/events/` in MinIO.
2. **Idempotency**: queries `spark_eventlog_files` by `(bucket, object_key, etag)` —
   an object already ingested with the same etag is skipped. Running
   `make spark-logs` multiple times **never duplicates anything**.
3. **Parses** each NDJSON line (decompressing zstd) and writes:
   - the raw JSON of every line into `spark_raw_events` (total coverage);
   - recognized events into normalized tables via per-type extractors (e.g.
     `taskFromEvent` maps `Task Metrics` to the `spark_tasks` columns, including
     `jvm_gc_time_ms`, `memory_bytes_spilled`, `disk_bytes_spilled`).
4. **Schema as code**: the loader **embeds** `schema.sql` and applies all statements
   on every run (`CREATE TABLE IF NOT EXISTS`, `CREATE VIEW IF NOT EXISTS`,
   `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` for migration). A single source of
   truth; no separate init script.

---

## 6. ClickHouse table catalog

Database `spark_observability`. Event → table mapping and primary use:

| Table | Origin | Primary use |
|-------|--------|-------------|
| `spark_raw_events` | every event-log line | free exploration, fields not yet normalized |
| `spark_tasks` | `SparkListenerTaskEnd` | skew, spill, GC, shuffle, per-task failures |
| `spark_stages` | `SparkListenerStageCompleted` | stage duration (drill-down) |
| `spark_jobs` | `JobStart` + `JobEnd` | job result and duration |
| `spark_sql_executions` | `SQLExecutionStart` | physical plans, query description |
| `spark_sql_execution_ends` | `SQLExecutionEnd` | query errors (`error_message`) |
| `spark_sql_execution_durations` (VIEW) | join of the two above | per-query latency, `has_error` |
| `spark_sql_adaptive_plans` | `SQLAdaptiveExecutionUpdate` | AQE re-plan history (`physical_plan` + `sparkPlanInfo`) |
| `spark_sql_execution_jobs` | `JobStart` (with `spark.sql.execution.id`) | SQL → job → stage → task traceability |
| `spark_diagnostic_reports` | `apex_diagnostics` | Crew A reports (stage 3), with `max_severity` |
| `spark_eventlog_files` | the loader itself | ingestion idempotency (`bucket`, `object_key`, `etag`) |

### Notable columns in `spark_tasks`

`spark_tasks` is the richest table for diagnostics. Column groups:

- **Identity**: `app_id`, `stage_id`, `stage_attempt_id`, `task_id`, `task_index`, `task_attempt`
- **Location**: `executor_id`, `host`
- **Time**: `launch_time_ms`, `finish_time_ms`, `duration_ms`, `executor_run_time_ms`, `executor_cpu_time_ns`
- **Status**: `task_type`, `successful` (0 = failed), `reason` (the full exception)
- **Memory/IO**: `peak_execution_memory`, `input_bytes/records`, `output_bytes/records`, `shuffle_read_bytes`, `shuffle_write_bytes`, `jvm_gc_time_ms`, `memory_bytes_spilled`, `disk_bytes_spilled`

> **Physical plan:** it lives at the SQL-execution level, not per task. Since AQE
> rewrites the plan after `SQLExecutionStart`, prefer `spark_sql_adaptive_plans`
> (the plan that actually ran) over `spark_sql_executions.physical_plan`.

### Engine and views

All tables are `ReplacingMergeTree` (version = `ingested_at`, or `generated_at` for
reports), with `ORDER BY` on the natural keys — which makes ingestion idempotent at
the row level too. Beyond the tables, `schema.sql` defines two views:

- **`spark_sql_execution_durations`** — INNER JOIN of `spark_sql_executions` with
  `spark_sql_execution_ends` on `app_id`+`execution_id`; exposes `duration_ms` and
  `has_error` (`error_message != ''`).
- **`spark_cache_blocks`** — extracts `SparkListenerBlockUpdated` events from
  `spark_raw_events` (`block_id`, `executor_id`, `in_memory`, `on_disk`,
  `memory_size`, `disk_size`); fed by the `cache_heavy` workload (which turns on
  `spark.eventLog.logBlockUpdates.enabled`).

The column migrations (`ALTER TABLE ... ADD COLUMN IF NOT EXISTS`) exist because
`CREATE TABLE IF NOT EXISTS` does not alter pre-existing tables: that is how
`jvm_gc_time_ms`, `memory_bytes_spilled`, and `disk_bytes_spilled` were added to
`spark_tasks` without recreating the database.

---

## 7. Stage 3 — Detecting errors and problems

There are **two complementary mechanisms**: error facts (straight from the tables)
and performance detectors (deterministic SQL → typed findings).

![apex_diagnostics engine: ClickHouse observability tables fan out to five deterministic detectors (skew, shuffle, plans, gc, oom) that converge into typed Pydantic findings; a CREW_LLM_MODEL decision routes either to Crew A (Diagnostic Analyst then Recommendation Writer producing spark.conf recommendations) or to a detectors-only report, both persisting to the spark_diagnostic_reports table](diagrams/diagnostics-engine.png)

### 7a. Execution errors (facts, straight from the tables)

They come from Spark itself, with no heuristics:

- **Task failed** → `spark_tasks.successful = 0`; the full exception is in `reason`
  (e.g. `ExceptionFailure ... PythonException`).
- **Job failed** → `spark_jobs.result != 'JobSucceeded'` (Spark aborts the job after
  `spark.task.maxFailures` attempts of the same task).
- **SQL query failed** → `spark_sql_execution_ends.error_message != ''` (also exposed
  as `has_error` in the durations view).

The ClickStack **Error Handling** tab and the "Tasks failing" / "Job with no
recorded completion" alerts read exactly these conditions.

### 7b. Performance problems (deterministic detectors)

`src/apex_diagnostics/detectors/` runs parameterized, pure SQL (**the LLM never
writes SQL**) and emits typed findings (Pydantic). Thresholds and guards live in
`src/config/diagnostics.yaml`, and the plan-text anti-pattern catalog in
`src/config/anti_patterns.yaml` — calibrating a threshold or adding a plan pattern
is a YAML edit:

| Detector | Rule (summary) | Anti-false-positive guards |
|----------|----------------|----------------------------|
| `skew` | slowest task ÷ median ≥ 3 (warning) / ≥ 6 (critical) per stage | stage with ≥ 8 tasks **AND** slowest task ≥ 5 s |
| `shuffle` | memory spill > 0 or shuffle > 256 MiB (warning); **disk spill > 0** or > 1 GiB (critical) | stage shuffle ≥ 16 MiB |
| `plans` | ≥ 3 AQE re-plans (info); physical-plan anti-patterns from `anti_patterns.yaml`: `CartesianProduct` (critical), `BroadcastNestedLoopJoin` (warning), `groupByKey` (warning) | — |
| `gc` | GC ≥ 10% of the stage's summed task time (warning) / ≥ 20% (critical) | summed stage duration ≥ 5 s |
| `oom` | failed task with `OutOfMemoryError` or `ExecutorLostFailure` in `reason` (critical) | — |

> **Plan anti-patterns are data, not code (Seam 1b).** `detect_plans` scans each
> SQL execution's physical plan (initial + every AQE-adaptive version) for the
> `signal` substrings in `src/config/anti_patterns.yaml`. Each entry carries a
> stable `id` (e.g. `ANTI-001`), surfaced on the finding as
> `evidence["anti_pattern_id"]`. Adding a plan-text-detectable anti-pattern is a
> YAML entry — no detector code change. The ids stay in sync with the KB
> superset at `.claude/kb/spark/specs/anti-patterns.yaml`.

The guards are why a small, healthy run (`make smoke`) **never** produces a critical,
even with statistically high ratios: a 96× skew on a 2.8 s task is not an
operational problem.

### Diagnostic flow

`make diagnose` (chained at the end of `make spark-logs` **non-fatally** — analysis
failure never breaks the load):

```text
detectors → findings → [CREW_LLM_MODEL set?]
                            ├─ yes → Crew A (Analyst → Writer) → spark.conf recommendations
                            └─ no  → "detectors_only" report (findings without recommendations)
                        → spark_diagnostic_reports (full JSON + max_severity)
```

- **Crew A** (CrewAI, `Process.sequential`): two agents.
  - *Spark Diagnostic Analyst* — gets all five detector tools (`detect_skew`,
    `detect_shuffle`, `detect_plans`, `detect_gc`, `detect_oom`), ranks root causes
    referencing the evidence. The tools are built from the shared `DETECTORS`
    registry (`crew/tools.py` iterates it), so the crew always sees exactly what
    `run_all` and the MCP server expose — no 3-vs-5 drift.
  - *Spark Recommendation Writer* — uses the analyst's context, writes the summary,
    keeps the findings unchanged, and produces **≥ 1 recommendation per
    warning/critical finding** with an exact `spark.conf` key/value; its output is
    validated as a `DiagnosticReport` (`output_pydantic`), with `status="full"`.
  - **Conf grounding (Seam 2).** Before the writer runs, `crew/recommendations.py`
    turns the actionable findings + `src/config/conf_recommendations.yaml` into a
    grounding block that is appended to the writer's task. Each line pins a
    validated `spark.conf` key/value (or a "code review" note when `conf_key` is
    null) per `(detector, severity[, pattern])`, so recommendations reuse vetted
    tuning instead of the LLM inventing keys per run. Grounding is best-effort — an
    empty/missing catalog degrades to the ungrounded prompt rather than failing
    (mirrors the detectors-only fallback below).
  - Requires `CREW_LLM_MODEL` (e.g. `anthropic/claude-sonnet-4-5`, `temperature=0.2`)
    and the provider's API key.
- **Graceful degradation in two layers:** `build_llm()` returns `None` when the model
  is not configured (or errors), and `analyze()` catches any crew exception — in both
  cases it falls back to the `detectors_only` report (findings without
  recommendations) instead of failing. The event-log load never breaks because of
  the LLM.
- The "Critical run detected" alert watches `max_severity='critical'` in that table.

`make diagnose` without `APP_ID` analyzes recent runs with no report
(`unanalyzed_runs`); with `APP_ID` it re-analyzes a specific run.

### Domain models (Pydantic, `apex_diagnostics/models.py`)

All detector and crew output is typed:

| Model | Main fields |
|-------|-------------|
| `Finding` | `detector` (`skew`/`shuffle`/`plans`/`gc`/`oom`), `severity`, `app_id`, `stage_id?`, `execution_id?`, `title`, `evidence: dict` |
| `Recommendation` | `conf_key`, `suggested_value`, `rationale`, `related_stage_ids: list[int]` |
| `DiagnosticReport` | `app_id`, `status` (`full`/`detectors_only`), `summary`, `findings[]`, `recommendations[]`; method `max_severity()` |

Severity is ranked by `SEVERITY_RANK = {info: 0, warning: 1, critical: 2}`;
`max_severity()` returns `"none"` when there are no findings.

`store.save_report` generates a `report_uid` (uuid4) and inserts one row into
`spark_diagnostic_reports` with: `app_id`, `report_uid`, `status`, `max_severity`,
`findings_count`, `report_json` (the serialized `DiagnosticReport`), `llm_model`
(populated only when `status="full"`), and `generated_at`.

> **Thresholds in two places that must stay in sync:** the defaults in
> `apex_diagnostics/config.py` (Pydantic models) and `src/config/diagnostics.yaml`.
> The YAML has **no** `oom` section because `detect_oom` takes no thresholds. The
> ClickHouse connections read env: `CLICKHOUSE_HTTP_HOST`, `CLICKHOUSE_HTTP_PORT`
> (default `28123`), `CLICKHOUSE_DB`, `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD`.
>
> **Diagnostics config catalog (`src/config/`, all packaged into the Spark image):**
> `diagnostics.yaml` (thresholds), `anti_patterns.yaml` (plan-text patterns, Seam 1b,
> loaded by `load_plan_patterns`), and `conf_recommendations.yaml` (writer grounding,
> Seam 2, loaded by `load_conf_recommendations`). All three are validated on load by
> Pydantic models in `config.py`, so a bad `severity` or shape fails fast at parse
> time.

---

## 8. Stage 4 — ClickStack / HyperDX

HyperDX does not query Spark: it queries **ClickHouse** through the provisioned
connection (`clickhouse:8123`, database `spark_observability`). Each table/view
becomes a **source**, and the dashboards aggregate over the sources. Access it at
`http://127.0.0.1:28088`.

### Seeding (idempotent)

`build/scripts/seed-clickstack.sh` runs at the end of `make compose`:

1. Creates the local account (`HYPERDX_SEED_EMAIL`/`PASSWORD` in `.env`; defaults
   `admin@spark-plat.local` / `Spv0Hyperdx123!`). Team creation triggers the
   auto-provisioning of the connection + basic sources (`DEFAULT_CONNECTIONS` /
   `DEFAULT_SOURCES` in `docker-compose.yml`).
2. Sources from `build/config/clickstack/sources.json` (**9**).
3. Dashboards from `build/config/clickstack/dashboards/*.json` (**10**) — existing
   dashboards are skipped; edit the JSON and re-run the seed to recreate.
4. Webhook + alerts from `build/config/clickstack/alerts.json` (**5**).

`make clean-data` wipes the MongoDB state; the next `make compose` reseeds from
scratch.

### The 9 sources

`Spark Diagnostic Reports`, `Spark Raw Events`, `Spark Tasks`, `Spark Jobs`,
`Spark Stages`, `Spark SQL Executions`, `Spark SQL Execution Ends`,
`Spark SQL Durations` (view `spark_sql_execution_durations`), `Spark SQL Plans`.

### The 10 dashboards

| # | Dashboard | Focus |
|---|-----------|-------|
| 1 | Spark Diagnostics | report severity, spill, skew (task max vs p50 per stage) |
| 2 | Run Summary | duration, core-hours, peak memory, shuffle, disk spill, activity rate per run |
| 3 | Cluster Status — Real-time | event throughput by type, active apps, tasks finishing, spill and GC in window |
| 4 | Cluster Status | tasks/GC/memory/shuffle per executor and host, jobs by result |
| 5 | Error Handling | critical reports, failed tasks and reasons, errored SQL executions, unfinished jobs |
| 6 | Heat Map | heatmaps of task duration, shuffle write, GC (stragglers = isolated points at the top) |
| 7 | SQL Plans | AQE plan updates per app, SQL started, ended ok vs error |
| 8 | Data Jobs Monitoring | job lifecycle, p95 duration, per-stage drill-down, estimated cost (`COST_PER_CORE_HOUR` × core-hours), right-sizing |
| 9 | ETL Performance (SLI) | task error rate (%), p95 task and SQL latency, individual slow queries, throughput |
| 10 | Memory & Cache | GC pressure per app, tasks killed by OOM/lost executor, cache bytes in memory and disk (view `spark_cache_blocks`) |

### The 5 alerts

Webhook channel `local-sink` (replace the URL with Slack in Team Settings):

1. "Critical run detected" (`max_severity='critical'`)
2. "Disk spill in some run"
3. "Tasks failing"
4. "Job with no recorded completion"
5. "Task error rate above 5%"

### Ports and credentials (local defaults)

| Service | URL / port | Credentials |
|---------|-----------|-------------|
| HyperDX (ClickStack) | `http://127.0.0.1:28088` | `admin@spark-plat.local` / `Spv0Hyperdx123!` |
| MinIO Console | `http://127.0.0.1:29001` | `spv0minio` / `spv0minio123` |
| Spark History | `http://127.0.0.1:28080` | — |
| Spark Master | `http://127.0.0.1:28081` | — |
| ClickHouse HTTP | `http://127.0.0.1:28123` | `spv0` / `spv0clickhouse123` (db `spark_observability`) |
| ClickHouse native | `127.0.0.1:29002` | same |

> **"Real-time" latency:** data arrives when `make spark-logs` runs; the alerts
> evaluate 5-minute windows every ~1 min. A streaming SparkListener (Apex roadmap)
> would remove this batch latency. The credentials here are **local-only** — do not
> reuse them in shared environments.

---

## 9. Synthetic workloads

Deliberately misbehaving Spark jobs that produce **ground truth** for the detectors.
Each forces one reproducible pathology to calibrate the thresholds. All materialize
through the `noop` sink (full computation, no storage side effects) and target
< ~3 min on a laptop-class machine.

| Target | Workload | Proven dimension |
|--------|----------|------------------|
| `make workload-skew` | hot-key join, AQE off | skew (task 121× the median) |
| `make workload-shuffle` | wide aggregation, starved memory | shuffle + memory/disk spill |
| `make workload-gc` | object churn via `collect_list`, SerialGC + 4m young gen | GC ≥ 10% (warning) |
| `make workload-oom` | `reverse(sequence(1, 60M))` — non-spillable array > heap; **fails on purpose** | critical OOM + Error Handling |
| `make workload-crossjoin` | explicit cross join 3k×3k | code analysis: `CartesianProduct` in the plan |
| `make workload-cache` | persist `MEMORY_AND_DISK` larger than the pool, incompressible payload | cache tracking (view `spark_cache_blocks`) |

`make workloads` runs all six.

### Calibration lessons (empirical, baked into the defaults)

- Catalyst optimizes `size(sequence(...))` without allocating — that is why the OOM
  uses `reverse`.
- Columnar cache compresses repetitive payloads ~7:1 — that is why the payload uses
  distinct md5 segments.
- Java 17's G1 absorbs SQL churn at ~1% GC — only the serial collector with a minimal
  young gen makes GC measurable (~12%).

### Environment overrides

Every parameter can be overridden via env (`WORKLOAD_<FIELD>` over the fields in
`src/workloads/catalog.py`), passed into the container:

```bash
# more extreme skew
docker compose --env-file .env -f build/docker-compose.yml exec -T spark-master \
  env PYTHONPATH=/opt/spark/src WORKLOAD_HOT_KEY_RATIO=0.97 WORKLOAD_ROWS=20000000 \
  /opt/spark/bin/spark-submit --master spark://spark-master:7077 --deploy-mode client \
  --conf spark.executorEnv.PYTHONPATH=/opt/spark/src /opt/spark/src/workloads/skew_join.py

# more aggressive spill
... WORKLOAD_ROWS=3000000 WORKLOAD_MEMORY_FRACTION=0.1 .../shuffle_heavy.py
```

Each dataclass's `spark_conf()` methods hold the deliberately bad session settings
(AQE off, `autoBroadcastJoinThreshold=-1`, fixed shuffle partitions, shrunken
`memory.fraction`) — **keep them intact** or Spark optimizes the pathologies away.
If a workload stops tripping its detector, raise `rows` / `payload_repeat` (more data
per task) or lower `memory_fraction` **before** touching the thresholds.

> **Skew rule of thumb:** for the detector to fire, the hot task must exceed **5 s**
> (the `min_duration_ms` guard) in addition to the ratio; scale `rows` until that
> happens on your hardware.

### Creating a new workload

1. **Parameters** in `src/workloads/catalog.py`: a new frozen dataclass with defaults
   + `spark_conf()`; register it in `CATALOG`.
2. **Script** `src/workloads/<name>.py`: pure builders
   (`build_*(spark, params) -> DataFrame`), a `main()` that loads config, creates the
   session via `SparkSessionFactory.get_or_create(..., extra_conf=params.spark_conf())`,
   materializes with `noop`, and ends with `raise SystemExit(main())`. Set
   `app_name = "workload-<name>"`.
3. **Make target**:
   ```make
   workload-<name>:
   	@$(SPARK_SUBMIT) /opt/spark/src/workloads/<name>.py
   ```
4. **Run and calibrate**: `make workload-<name> && make spark-logs`; check
   `spark_diagnostic_reports` to see whether the expected detector fired.

---

## 10. Full experiment cycle

The experiment loop: healthy baseline (control) vs. known pathologies (ground
truth), with re-analysis at the end.

![Experiment cycle: make compose brings up the stack and ClickStack; make smoke produces the healthy baseline; make workloads produces 6 pathologies; make spark-logs ingests and diagnoses; ClickStack :28088 shows tabs and alerts; make diagnose re-analyzes a run and the cycle returns to workloads to adjust and repeat](diagrams/dd-experiment-lifecycle.png)

```bash
make compose          # stack + seeded ClickStack
make smoke            # healthy baseline (experiment control)
make workloads        # known pathologies (ground truth)
# + variations via WORKLOAD_* and/or a failing job
make spark-logs       # idempotent ingestion + automatic diagnostics
# ClickStack :28088 → tabs + Alerts tab (fires in ~1-3 min)
make diagnose APP_ID=<app>   # re-analyze a specific run (with LLM, if configured)
```

### Testing the error surfaces (Error Handling)

A single job can light up a failed task, an aborted job, and an errored SQL. Submit
a job with a UDF that raises above a threshold, with `--conf spark.task.maxFailures=2`
to abort fast. After `make spark-logs`, the Error Handling tab and the corresponding
alerts light up.

---

## 11. Spark application utilities

Reusable under `src/spark_platform` (clear package boundaries: `session/` owns the
runtime lifecycle; `jobs/` owns the execution contract; `io/` owns dataset specs and
reader/writer calls):

| Module | Role |
|--------|------|
| `config/loader.py` | loads `src/config/lakehouse.yaml`, resolves per-entity/layer read/write config and expands env |
| `session/factory.py` | creates a Delta-enabled `SparkSession`; scripts extend it with extra config via `get_or_create(..., extra_conf=...)` |
| `io/specs.py` | validates read/write specs before IO execution (testable IO) |
| `io/datasets.py` | public read/write helpers for Delta and JSON |
| `jobs/base.py` | `SparkPlatJob` ABC/template — the contract for app scripts |
| `utils/logger.py` | project logger |
| `utils/plan_debug.py` | optional (commented) helper for physical-plan inspection in local dev |

`SparkSessionFactory.get_or_create(config, app_name=None, extra_conf=None)` merges
config in this precedence order: `DEFAULT_CONF` (Delta extensions —
`DeltaSparkSessionExtension` + `DeltaCatalog`) → `spark.config` from the YAML →
`extra_conf` from the script (this is how workloads inject their deliberately bad
configs). The `SparkPlatJob.run()` contract runs `extract → transform → load` and
always calls `stop_active()` in `finally`. The IO specs (`io/specs.py`) only accept
the `delta` and `json` formats.

### Sample scripts (`src/apps/sample_scripts`)

The segmented flow for the `customer` entity:

1. `simple_persist_customers_landing.py` — writes fake customer JSON to
   `s3a://lakehouse/landing/customer` (does not use `SparkPlatJob`; represents an
   ingestion edge).
2. `smoke_job_plat_minio.py` — a `SparkPlatJob` that reads landing JSON, applies a
   named transform, and writes `s3a://lakehouse/bronze/customer` as Delta.
3. `check_sanity.py` — validates landing and bronze (row counts, expected columns)
   and runs a grouped action so the event logs carry useful detail.

`make smoke` runs all three (`make ingest-landing`, `make bronze`, `make sanity`) and
validates MinIO, Delta, and the Spark History indexing.

---

## 12. MCP server

An MCP (stdio) server exposes the diagnostic tools to agents. Because the project
uses a src layout and is not installed as a package, `PYTHONPATH=src` is required:

```bash
claude mcp add spark-diagnostics --env PYTHONPATH=src -- \
  uv run --directory apex-v0.1 python -m apex_diagnostics.mcp_server
```

The server (`FastMCP("spark-diagnostics")`) exposes **8 tools**. The detection ones
never call an LLM; only `analyze_run` runs the full pipeline. Client and thresholds
are cached (`lru_cache`).

| MCP tool | What it does |
|----------|--------------|
| `list_runs(limit=20)` | recent runs with the count of already-stored reports |
| `detect_skew(app_id)` | per-stage task-skew findings (no LLM) |
| `detect_shuffle(app_id)` | per-stage shuffle/spill/GC findings (no LLM) |
| `detect_plans(app_id)` | AQE re-plans + plan antipatterns per SQL execution (no LLM) |
| `detect_gc(app_id)` | per-stage GC-pressure findings (no LLM) |
| `detect_oom(app_id)` | OOM / lost-executor classification of failed tasks (no LLM) |
| `get_report(app_id)` | the app's latest stored report |
| `analyze_run(app_id)` | full pipeline (detectors + Crew A) and persists; degrades to `detectors_only` without an LLM |

> **Note:** the MCP server, Crew A (`crew/tools.py`), and `run_all` all derive their
> detectors from the same `DETECTORS` registry (`detectors/__init__.py`), so every
> surface exposes the same **5** detectors — the earlier 3-vs-5 drift (the Analyst
> once saw only `detect_skew`/`detect_shuffle`/`detect_plans`) is gone.

---

## 13. Tests

Managed with `uv` from the project root. Fast and stack-free:

```bash
make tests    # pytest: detectors/models/tools/store over FakeCHClient (fixtures)
# make test is an alias for make tests
```

- **IO tests** use fake Spark objects (`tests/fakes/spark.py`): they validate the
  fluent-API calls without a cluster and without importing PySpark.
- **Detector tests** use a fake ClickHouse client (`tests/fakes/clickhouse.py`) that
  matches on the **exact SQL** — changing a detector's SQL breaks the test on
  purpose. They run without the Docker stack and without an LLM.
- **Go loader**: inline fixtures in `build/images/eventlog-loader/main_test.go` pin
  the parse (`go test ./...`; host without Go 1.26 → use the `golang:1.26-bookworm`
  image).
- **Tests that call a real LLM**: mark with `@pytest.mark.llm` and gate with
  `RUN_LLM_TESTS=1` — they never run in the default `make tests`.
- **Ground-truth E2E** (`tests/e2e/`, marked `e2e`): the only tests that hit the
  **running** stack. `make validate-detectors` runs the problem workloads →
  `make spark-logs` (ingest + diagnose) → then asserts each workload's expected
  detector actually fired at the expected severity, reusing the production read
  path (`ClickHouseConnectClient` + `get_report`) so real SQL/schema drift surfaces
  here. Gated by `APEX_E2E=1` (set by the Make target), so `make tests` never
  reaches ClickHouse. It skips gracefully if the stack is unreachable.

---

## 14. Make command reference

| Command | What it does |
|---------|--------------|
| `make bootstrap` | downloads jars, wheels, and Go deps once; validates `uv` and runs `uv sync` |
| `make build` | builds all project-local Docker images |
| `make validate` | validates tools, jars, images, and ports before Compose |
| `make compose` | brings up the stack (MinIO, ClickHouse, Mongo, HyperDX, Spark master/worker/History) + readiness + ClickStack seed |
| `make ingest-landing` / `bronze` / `sanity` | submits each step of the sample flow individually |
| `make smoke` | full landing→bronze→sanity flow + MinIO/History validation |
| `make spark-logs` | runs the Go loader, validates ingestion, and chains `make diagnose` |
| `make workloads` | runs the 6 synthetic workloads |
| `make workload-<name>` | runs an individual workload |
| `make diagnose [APP_ID=<app>]` | diagnoses an app (or recent runs with no report) |
| `make validate-detectors` | ground-truth E2E: runs the problem workloads → ingests + diagnoses → asserts each detector fired (`APEX_E2E=1`, needs the running stack) |
| `make services` | prints URLs, credentials, and UI paths |
| `make tests` / `make test` | fast Python tests via `uv` |
| `make down` | stops the stack without deleting local data |
| `make clean-data` | deletes local MinIO/ClickHouse/Mongo state (with a Docker-root fallback) |
| `make removeimage` | removes only the local project images; keeps caches |

---

## 15. Machine requirements and versions

The project runs Spark, Delta, MinIO, ClickHouse, and the loader **inside Docker**.
The host needs only the CLIs below — Java, Spark, Hadoop, Scala, MinIO, ClickHouse,
and Go do **not** need to be installed on the host.

| Host tool | Validated version |
|-----------|-------------------|
| Docker Engine | 29.2.1 |
| Docker Compose | v5.0.2 |
| uv | 0.10.0 (bootstrap installs it if missing and `curl` is present) |
| GNU Make | 4.3 |
| Bash | 5.2.21 |
| curl | 8.5.0 |
| coreutils / sha256sum | 9.4 |
| iproute2 / ss | 6.1.0 |

Nearby newer versions should work; if behavior changes, validate with
`make bootstrap`, `make build`, `make validate`, `make tests`.

---
