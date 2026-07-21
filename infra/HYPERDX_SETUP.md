# HyperDX setup — custom Source, MV registration, skew dashboard

HyperDX **auto-infers only the default OTel schema**. `apex.spark_events` is a *custom* table, so
you must define a **custom Source** with every expression set explicitly — **a source with a
wrong/blank Timestamp or Service expression silently returns nothing** (the #1 HyperDX gotcha).

This stack **scripts the source for you** (recommended), and the exact manual steps are below as a
fallback / for understanding.

---

## Option A — scripted (default in this repo) ✅

`docker-compose.yml` passes `DEFAULT_CONNECTIONS` + `DEFAULT_SOURCES` to the HyperDX app. HyperDX
applies them **once, when the first team is created** (i.e. at first user registration), then
persists them in MongoDB. So:

1. `docker compose up -d`
2. Open **http://localhost:8090** and **register the first user** (any email/password). This
   creates the team → HyperDX seeds:
   - Connection **“Apex ClickHouse”** → `http://clickhouse:8123`, user `apex`.
   - Source **“Spark Events”** → `apex.spark_events` with the mapping below.
3. Go to **Search**, pick the **Spark Events** source → your rows appear. Filter by `job_id`.

Verify it seeded (no UI needed):
```bash
docker exec apex-infra-mongodb mongosh --quiet hyperdx \
  --eval 'db.sources.find({},{name:1,"from":1,timestampValueExpression:1,serviceNameExpression:1,eventAttributesExpression:1,traceIdExpression:1}).forEach(printjson)'
```

> Registration is required because the seed is attached to the **team**, which doesn't exist until
> someone signs up. Until then `GET :8000/installation` returns `{"isTeamExisting":false}` and
> `db.sources` is empty — that's expected, not a failure.

---

## Option B — manual (Team Settings → Sources)

If you'd rather create it by hand (or the seed was cleared):

1. **http://localhost:8090** → register/login.
2. **Team Settings → Connections → Add Connection**
   - Name: `Apex ClickHouse`
   - Host: `http://clickhouse:8123`  ·  Username: `apex`  ·  Password: (`CLICKHOUSE_PASSWORD` from `.env`)
   - Save. (HyperDX will “test” it — it should succeed.)
3. **Team Settings → Sources → Add Source** → kind **Log**. Set **every** field:

   | HyperDX field | Value | Why |
   |---|---|---|
   | Name | `Spark Events` | — |
   | Connection | `Apex ClickHouse` | the connection above |
   | Database / Table | `apex` / `spark_events` | the custom table |
   | **Timestamp Column Expression** | `ts` | ← without this the source returns nothing |
   | **Service Name Expression** | `app_id` | groups/filters by Spark app |
   | **Event Attributes Expression** | `attributes` | the `Map(String,String)` column |
   | **Resource Attributes Expression** | `attributes` | (reuse; spark_events has one map) |
   | **Trace Id Expression** | `job_id` | the Apex trace key — search/correlate by it |
   | Body / Implicit Column Expression | `plan_json` | shown as the row body |
   | Default Select | `ts,app_id,job_id,stage_id,task_duration_p50_ms,task_duration_p99_ms` | table columns |
   | Severity Text Expression | *(leave blank)* | spark_events has no severity |

4. Save → **Search** → select **Spark Events** → rows appear; filter `job_id: ax151sasadds114`.

---

## Register the rollup MV for auto-acceleration (spark_jobs_1m)

HyperDX can auto-accelerate time charts off the `AggregatingMergeTree` rollup **iff** the MV
columns follow `<aggFn>__<sourceColumn>` (they do: `sum__shuffle_read_bytes`,
`quantiles__task_duration_p99_ms`, …).

1. **Team Settings → Sources → Add Source** (or edit) pointing at `apex.spark_jobs_1m`.
2. Timestamp expression: `bucket`. Set **granularity = 1 minute** and **min date = `min(bucket)`**.
3. On a time tile using metrics like `sum(shuffle_read_bytes)` or a p99, HyperDX shows a **green
   accelerated bolt**; the optimization modal names **`spark_jobs_1m`**.

> ⚠️ The incremental MV is **BETA and not backfilled** — it only contains rows inserted into
> `spark_events` *after* the MV existed. Set “min date” correctly; **don't** use `POPULATE`.
> To backfill a window manually:
> ```sql
> INSERT INTO apex.spark_jobs_1m
> SELECT toStartOfMinute(ts) AS bucket, job_id, app_id,
>        countState(), sumSimpleState(shuffle_read_bytes), sumSimpleState(shuffle_write_bytes),
>        sumSimpleState(spill_disk_bytes), sumSimpleState(spill_mem_bytes),
>        sumSimpleState(input_bytes), sumSimpleState(output_bytes),
>        maxSimpleState(gc_time_ms), maxSimpleState(peak_execution_mem_bytes),
>        quantilesState(0.5,0.99)(task_duration_p50_ms), quantilesState(0.5,0.99)(task_duration_p99_ms)
> FROM apex.spark_events WHERE ts >= now() - INTERVAL 24 HOUR
> GROUP BY bucket, job_id, app_id;
> ```

---

## Skew dashboard

See [`dashboards/skew_dashboard.json`](dashboards/skew_dashboard.json) — a per-tile build spec
(source + query + viz). Each tile's query matches `sql/005` for the same job/window, so a tile and
the raw SQL agree. Create **Dashboards → New**, add one tile per entry against the **Spark Events**
source (use the rollup source for the accelerated time tiles).
