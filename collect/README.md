# collect/ — ③ transport

**Role:** config-only OpenTelemetry Collector (`otelcol-contrib` **v0.156.0**, no custom Go build).
OTLP `:4318` → `memory_limiter` → PII scrub → ClickHouse `apex`.
**Obeys:** [`../CONTRACT.md`](../CONTRACT.md) (v0.2) · **Full brief:** [`../docs/lanes/COLLECT.md`](../docs/lanes/COLLECT.md)
**Exit criterion (met):** ingests Spark telemetry on `:4318`, hashes/drops the named PII fields, and lands rows queryable by `job_id` end-to-end.

```
 jar ──OTLP/HTTP :4318──► otel-collector ──native tcp:9000──► ClickHouse apex
                          memory_limiter                     otel_traces (exporter-owned)
                          transform (SHA256 query_text,          │  MATERIALIZED VIEWs
                                     redact plan literals)        ├─ mv_spark_events      ─► spark_events
                          attributes (drop file_path/email)      └─ mv_plan_transitions  ─► plan_transitions
                          redaction/pii (HMAC email/IP)
                          clickhouse exporter (internal sending_queue.batch)
```

## ⚠️ The one constraint that shapes this lane

The `clickhouseexporter` writes **only** its fixed OTLP schema (`otel_traces`/`otel_logs`) — its
INSERT is bound to columns like `Timestamp`, `SpanName`, `SpanAttributes`. It **cannot** target
custom columns like `shuffle_read_bytes`. So:

> **Land spans in `otel_traces`, then reshape into the contract tables with ClickHouse
> MATERIALIZED VIEWs.** Do **NOT** set `traces_table_name: spark_events`.

Both span types the jar emits land in the single `otel_traces` table and are routed by `SpanName`:

| jar span | MV | → contract table |
|---|---|---|
| `apex.stage` | `mv_spark_events` | `apex.spark_events` (19 fields) |
| `apex.plan_transition` (v0.2 AQE signal) | `mv_plan_transitions` | `apex.plan_transitions` |

The MVs flatten the snake_case `SpanAttributes` map into typed columns (see [`ddl/30_`](ddl/30_mv_spark_events.sql) / [`ddl/31_`](ddl/31_mv_plan_transitions.sql)).

## Redaction — defense in depth (second net)

The jar already redacts in-JVM before egress (plan literals stripped, no raw plan text). This
collector is the **second** net:

| Field | Action | Processor |
|---|---|---|
| `query_text` | SHA-256 one-way hash (deterministic) | `transform/redaction` (OTTL `SHA256`, guarded `!= nil`) |
| `plan_json` literals | strip residual `"desc":"…"` → `[REDACTED]` | `transform/redaction` (`replace_pattern`) |
| `file_path`, `email` | delete the key entirely | `attributes/scrub` |
| emails/IPs embedded in any value | keyed HMAC-SHA256 mask | `redaction/pii` (`hmac_key` from env) |

`plan_fingerprint` is **opaque** — computed upstream (Lane 2), passed through untouched, **never
recomputed** here.

## Layout

```
collect/
├── config.yaml            # otelcol-contrib pipeline (otlp → memory_limiter → scrub → clickhouse)
├── docker-compose.yml     # collector + LOCAL throwaway ClickHouse + queue-init sidecar
├── .env.example           # host-port bands + ClickHouse creds + REDACTION_SECRET_KEY
├── ddl/                   # applied on ClickHouse first boot, in filename order:
│   ├── 00_database.sql
│   ├── 10_otel_traces.sql          # exporter-owned schema (PINNED from an empirical probe)
│   ├── 11_otel_logs.sql            # exporter-owned schema
│   ├── 20_spark_events.sql         # CANONICAL contract mirror
│   ├── 21_plan_transitions.sql     # CANONICAL contract v0.2 mirror
│   ├── 22_findings.sql             # CANONICAL contract mirror (engine writes; here for surface parity)
│   ├── 30_mv_spark_events.sql      # reshape otel_traces → spark_events
│   └── 31_mv_plan_transitions.sql  # reshape otel_traces → plan_transitions
└── scripts/
    └── send_sample_events.sh       # POST a real apex.stage + apex.plan_transition to :4318
```

## Run it

```bash
cp .env.example .env
# set a real HMAC secret:
sed -i '' "s/^REDACTION_SECRET_KEY=.*/REDACTION_SECRET_KEY=$(openssl rand -hex 32)/" .env

docker compose up -d              # clickhouse (healthy) → queue-init → collector
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:${HEALTHCHECK_HOST_PORT:-13133}   # → 200

# money shot: real OTLP span → row in spark_events via the MV
bash scripts/send_sample_events.sh
sleep 8   # internal sending_queue.batch flush_timeout is 5s
docker exec apex-clickhouse clickhouse-client --user apex --password apex_local_dev \
  --query "SELECT job_id, stage_id, plan_fingerprint FROM apex.spark_events WHERE job_id='ax151sasadds114'"
```

Validate the config without starting anything:

```bash
docker run --rm -e REDACTION_SECRET_KEY=$(openssl rand -hex 32) \
  -e CLICKHOUSE_USER=apex -e CLICKHOUSE_PASSWORD=apex_local_dev \
  -v "$PWD/config.yaml:/c.yaml:ro" \
  otel/opentelemetry-collector-contrib:0.156.0 validate --config /c.yaml
```

## Lane boundaries & notes

- **We own the collector → ClickHouse wiring, not the ClickHouse server.** The `clickhouse`
  service in `docker-compose.yml` is a **throwaway local test instance** so this lane runs in
  isolation. When the **infra/** lane lands, delete that service and point the collector at
  infra's `clickhouse:9000` over the shared docker network (`endpoint` in `config.yaml` already
  uses the internal DNS name `clickhouse`, not a host port).
- **Ports (CONTRACT.md Port Map):** container-internal ports are the reserved ones — OTLP/HTTP
  `4318`, OTLP/gRPC `4317`, health `13133`. The `.env` **host**-port variables let you shift the
  host bindings to dodge collisions (this box already had another stack squatting on
  `4318`/`8123`/`9000`, so the committed `.env.example` maps them into a high band). The
  collector↔ClickHouse link is internal and unaffected by host remapping.
- **`create_schema: false`** — we own partitioning/TTL; the collector issues **no DDL** at
  startup. The `otel_traces`/`otel_logs` DDL in `ddl/` was captured from an empirical probe run
  of the exporter (`create_schema:true` → `SHOW CREATE TABLE`) so it matches the v0.156.0 INSERT
  byte-for-byte; keep it in sync if you bump the collector version.
- **Batching** uses the exporter's internal `sending_queue.batch` (min 5000 / 5s) — **not** the
  standalone `batch` processor (avoids data loss on shutdown; hits ClickHouse's insert guidance).
- **Crash-safety:** `file_storage` persists the sending queue to disk (`block_on_overflow: true`)
  → at-least-once across restarts. `retry_on_failure` backs off 5s→30s (300s cap).
- **TTL gotcha (test):** `spark_events`/`otel_traces` carry a 90-day TTL on the event `ts`. The
  contract fixture `ts` (2024-06) is older than that, so a raw replay TTL-expires on insert — the
  sample script defaults `ts` to *now* for that reason. Production events are near-real-time, so
  this is a test-only concern.
- **Metrics are alpha** in the clickhouseexporter at 0.156.0 (traces/logs are beta), so Spark
  metrics ride as **spans** with numeric `SpanAttributes`, not OTLP metrics.
