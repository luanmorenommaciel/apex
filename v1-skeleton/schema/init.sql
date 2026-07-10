-- Apex V1 — ClickHouse Schema
-- Criado automaticamente ao subir o container

CREATE DATABASE IF NOT EXISTS apex;

-- Métricas por stage (granularidade principal do diagnóstico)
CREATE TABLE IF NOT EXISTS apex.stage_metrics (
    app_id          String,
    job_id          UInt32,
    stage_id        UInt32,
    attempt_id      UInt32,
    stage_name      String,
    -- Timing
    submission_time DateTime64(3),
    completion_time DateTime64(3),
    duration_ms     UInt64,
    -- Tasks
    num_tasks       UInt32,
    failed_tasks    UInt32,
    -- I/O
    input_bytes     UInt64,
    output_bytes    UInt64,
    shuffle_read    UInt64,
    shuffle_write   UInt64,
    -- Spill
    memory_spill    UInt64,
    disk_spill      UInt64,
    -- GC
    gc_time_ms      UInt64,
    -- Executor
    executor_cpu_ms UInt64,
    -- Meta
    ingested_at     DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (app_id, job_id, stage_id)
PARTITION BY toYYYYMM(ingested_at);

-- Métricas por task (granularidade fina — detecta skew)
CREATE TABLE IF NOT EXISTS apex.task_metrics (
    app_id          String,
    stage_id        UInt32,
    task_id         UInt64,
    attempt_number  UInt32,
    executor_id     String,
    -- Timing
    launch_time     DateTime64(3),
    finish_time     DateTime64(3),
    duration_ms     UInt64,
    -- I/O
    input_bytes     UInt64,
    output_bytes    UInt64,
    shuffle_read    UInt64,
    shuffle_records UInt64,  -- registros lidos no shuffle — skew de registros nem sempre vira skew de duracao
    shuffle_write   UInt64,
    -- Spill
    memory_spill    UInt64,
    disk_spill      UInt64,
    -- Status
    status          String,  -- SUCCESS | FAILED
    -- Meta
    ingested_at     DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (app_id, stage_id, task_id)
PARTITION BY toYYYYMM(ingested_at);

-- Findings gerados pelo LLM (diagnósticos)
CREATE TABLE IF NOT EXISTS apex.findings (
    finding_id      UUID DEFAULT generateUUIDv4(),
    app_id          String,
    stage_id        Nullable(UInt32),
    pattern         String,   -- skew | parallelism_collapse | spill | etc.
    severity        String,   -- critical | high | medium | low
    confidence      Float32,
    root_cause      String,
    recommendation  String,
    llm_model       String,
    created_at      DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (app_id, created_at)
PARTITION BY toYYYYMM(created_at);

-- View: stages com problemas (wasted cores, spill, skew)
CREATE VIEW IF NOT EXISTS apex.suspicious_stages AS
SELECT
    app_id,
    stage_id,
    stage_name,
    num_tasks,
    duration_ms,
    memory_spill,
    disk_spill,
    shuffle_read,
    -- Indicadores de problema
    (disk_spill > 0)                                    AS has_spill,
    (num_tasks < 4 AND input_bytes > 1073741824)        AS low_parallelism,  -- < 4 tasks, > 1GB input
    -- Custo estimado de spill (disk I/O penalty)
    round(disk_spill / 1e9, 2)                          AS spill_gb
FROM apex.stage_metrics
WHERE duration_ms > 10000  -- só stages > 10s
ORDER BY disk_spill DESC, duration_ms DESC;
