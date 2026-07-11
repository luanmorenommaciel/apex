-- Apex Telemetry v1 — DDL canonico (contrato: docs/specs/telemetry-schema-contract-v1.md)
-- Unifica spike (spark_tasks), cowork (apex.*) e kimi (fork Gabriel).

CREATE DATABASE IF NOT EXISTS apex;

-- ---------------------------------------------------------------- task_metrics
-- Grao: task attempt. Dedup por CHAVE NATURAL (licao do spike: uid posicional
-- duplica task re-ingerida de log .compact). Consultas devem usar FINAL.
CREATE TABLE IF NOT EXISTS apex.task_metrics
(
    schema_version        LowCardinality(String) DEFAULT 'apex.telemetry.v1',
    job_id                String,                -- envelope codex: app_id | spark-job-<id> | local-job
    app_id                String,
    stage_id              UInt64,
    stage_attempt_id      UInt64,
    task_id               UInt64,
    task_attempt          UInt64,
    executor_id           String,
    host                  String,
    launch_time_ms        UInt64,
    finish_time_ms        UInt64,
    duration_ms           UInt64,
    task_type             LowCardinality(String),
    successful            UInt8,                 -- 0 => so alimenta detector de OOM
    reason                String,                -- Task End Reason serializado
    executor_run_time_ms  UInt64,
    executor_cpu_time_ns  UInt64,
    peak_execution_memory UInt64,
    input_bytes           UInt64,
    input_records         UInt64,
    output_bytes          UInt64,
    output_records        UInt64,
    shuffle_read_bytes    UInt64,
    shuffle_read_records  UInt64,
    shuffle_write_bytes   UInt64,
    shuffle_fetch_wait_ms UInt64,
    jvm_gc_time_ms        UInt64,
    memory_bytes_spilled  UInt64,
    disk_bytes_spilled    UInt64,
    ingested_at           DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(ingested_at)
ORDER BY (app_id, stage_id, stage_attempt_id, task_id, task_attempt);

-- --------------------------------------------------------------- stage_metrics
CREATE TABLE IF NOT EXISTS apex.stage_metrics
(
    schema_version   LowCardinality(String) DEFAULT 'apex.telemetry.v1',
    job_id           String,
    app_id           String,
    stage_id         UInt64,
    stage_attempt_id UInt64,
    stage_name       String,
    submission_time  DateTime64(3),
    completion_time  DateTime64(3),
    duration_ms      UInt64,
    num_tasks        UInt32,
    failed_tasks     UInt32,
    input_bytes      UInt64,
    output_bytes     UInt64,
    shuffle_read     UInt64,
    shuffle_write    UInt64,
    memory_spill     UInt64,
    disk_spill       UInt64,
    gc_time_ms       UInt64,
    executor_cpu_ms  UInt64,
    ingested_at      DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(ingested_at)
ORDER BY (app_id, stage_id, stage_attempt_id);

-- ------------------------------------------------------------------ sql_plans
-- Plano inicial E cada update AQE (licao P1-6/spike: padrao pode existir so no
-- plano adaptativo). plan_kind: initial | adaptive.
CREATE TABLE IF NOT EXISTS apex.sql_plans
(
    schema_version LowCardinality(String) DEFAULT 'apex.telemetry.v1',
    job_id         String,
    app_id         String,
    execution_id   UInt64,
    plan_kind      LowCardinality(String),
    plan_seq       UInt32,                 -- ordem dos updates AQE na execucao
    physical_plan  String,
    event_time     DateTime64(3),
    ingested_at    DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(ingested_at)
ORDER BY (app_id, execution_id, plan_kind, plan_seq);

-- ------------------------------------------------------------------- findings
CREATE TABLE IF NOT EXISTS apex.findings
(
    schema_version LowCardinality(String) DEFAULT 'apex.telemetry.v1',
    finding_id     UUID DEFAULT generateUUIDv4(),
    job_id         String,
    app_id         String,
    detector       LowCardinality(String),   -- skew|gc|shuffle|oom|plans|crew
    severity       LowCardinality(String),   -- info|warning|critical
    stage_id       Int64 DEFAULT -1,
    execution_id   Int64 DEFAULT -1,
    title          String,
    root_cause     String,
    recommendation String,
    confidence     Float32,
    evidence       String,                   -- JSON
    created_at     DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = MergeTree()
ORDER BY (app_id, created_at);
