# Apex — The Frozen Contract

> **This is the one file every stage depends on. Freeze it first; change it only by explicit version bump.**
> It defines the data shapes that flow between stages so each directory can be built independently and still fuse.
> A stage may **add** a field; it may never rename or repurpose one. Breaking changes = version bump + a note here.

**Status:** contract v0.1 · **Consumed by:** `dev` · `jar` · `collect` · `infra` · `engine` · `serve`
**Artifacts:** [`contract/sample_event.json`](contract/) (the fixture) · [`contract/spark_events.ddl.sql`](contract/) · [`contract/findings.ddl.sql`](contract/)

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
- **Plan:** `plan_fingerprint` (SHA-256 of the **normalized LOGICAL** plan — `optimizedPlan.canonicalized`, **not** physical), `plan_json` (redacted `node.desc`).

The canonical values live in [`contract/sample_event.json`](contract/) — build `engine/` and `serve/` against it.

## The store (infra owns application, contract owns the schema)

Database `apex`. Canonical DDL in [`contract/`](contract/):
- **`spark_events`** — MergeTree, `PARTITION BY toYYYYMM(ts)`, `ORDER BY (job_id, stage_id)`, one row per stage.
- **`findings`** — one row per detected issue (`engine/` writes, `serve/` reads).

## The Finding (engine → serve)

Pydantic model whose field names match the `findings` table exactly: `job_id`, `app_id`, `type` (skew|spill|shuffle|memory|cost|code), `severity` (info|warning|critical|blocker), `stage_id`, `evidence`, `impact`, `fix`, `confidence` (0–1).

## Redaction (enforced in two places)

Plan/query text carries PII → **redact in-JVM before egress** (`jar/`, primary) with the collector as a second net (`collect/`): hash `query_text`, drop `file_path`/`email`, strip `plan_json` literals. `plan_fingerprint` is computed upstream and passed as an opaque value — redaction never recomputes it.

## Activation (how a job turns Apex on)

```python
SparkSession.builder \
  .config("spark.jars.packages",  "io.dataship:apex_2.12:0.1.0") \
  .config("spark.extraListeners", "io.dataship.apex.ApexSparkListener") \
  .config("spark.apex.endpoint",  "http://collect:4318")
```

---

*The full, authoritative version of this contract (with every field's type + Spark source) is the original `LANE-0-CONTRACT.md`. This top-level copy is the always-visible summary; the `contract/` dir holds the enforceable artifacts. Keep them in sync on any change.*
