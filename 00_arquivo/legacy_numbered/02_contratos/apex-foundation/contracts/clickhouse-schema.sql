-- contracts/clickhouse-schema.sql  (apex-schema-v1)
--
-- Onde os eventos de telemetria pousam. O Collector ESCREVE aqui; os Watchers LEEM
-- daqui via SQL. Esta e a versao normalizada do que o `eventlog-loader` do plat-v0 ja
-- produz hoje, mais a tabela bruta proposta pelo Guilherme.
--
-- Por que ClickHouse: e um banco colunar, otimo pra varrer milhoes de eventos e calcular
-- agregacoes (ex.: "qual a distribuicao de shuffle_read entre as tarefas deste stage?")
-- em milissegundos — exatamente o tipo de pergunta que um Watcher faz.

-- Tabela bruta: 1 linha por evento, espelhando o contrato apex-event.schema.json.
CREATE TABLE IF NOT EXISTS spark_events (
    event_id              String,
    timestamp             DateTime64(3),
    kind                  LowCardinality(String),  -- task_end, stage_completed, ...
    service_name          LowCardinality(String),
    spark_app_id          String,
    spark_app_name        String,
    execution_id          Int64,
    job_id                Int64,
    stage_id              Int64,
    task_id               Int64,
    call_site             String,                  -- "job.py:58" — liga ao codigo
    plan_fingerprint      String,
    run_time_ms           Int64,
    shuffle_read_records  Int64,
    shuffle_read_bytes    Int64,
    spill_bytes           Int64,
    gc_time_ms            Int64
)
ENGINE = MergeTree
PARTITION BY toYYYYMMDD(timestamp)   -- particiona por dia: consultas recentes ficam rapidas
ORDER BY (spark_app_id, execution_id, stage_id, task_id);

-- Exemplo de pergunta que o Watcher de Skew faz contra esta tabela:
--   "neste stage, a tarefa mais lenta leu quantas vezes mais registros que a mediana?"
-- (se for muitas vezes mais, e skew)
--
-- SELECT stage_id,
--        max(shuffle_read_records)                          AS task_mais_pesada,
--        quantile(0.5)(shuffle_read_records)                AS mediana,
--        max(shuffle_read_records) / quantile(0.5)(shuffle_read_records) AS razao_skew
-- FROM spark_events
-- WHERE execution_id = 1 AND kind = 'task_end'
-- GROUP BY stage_id
-- HAVING razao_skew > 5;       -- 5x acima da mediana ja e suspeito
