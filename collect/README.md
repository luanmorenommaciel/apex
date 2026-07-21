# collect/ — ③ transport

**Role:** OpenTelemetry Collector (config-only, `otelcol-contrib` v0.156.0). OTLP :4318 → PII scrub → ClickHouse.
**Language:** YAML · **Branch prefix:** `collect/*` (e.g. `collect/T8-internal-batch`)
**Full brief:** [../docs/lanes/COLLECT.md](../docs/lanes/COLLECT.md) · **Obeys:** [../CONTRACT.md](../CONTRACT.md)
**Exit criterion:** ingests Spark telemetry on :4318, hashes/drops the named PII fields, and lands rows queryable by `job_id`.

Layout: `config.yaml` (otlp → memory_limiter → transform/attributes → clickhouse exporter) · `docker-compose.yml`.
Watch: the exporter can't target custom columns — land in `otel_traces`, reshape into `spark_events` via a **Materialized View**. Use the internal `sending_queue.batch`, not the standalone batch processor.
