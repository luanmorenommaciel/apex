package clickhouse

import (
	"context"
	"fmt"
	"strings"
)

// QueryBuilder oferece métodos para construir e executar queries específicas do Apex.
type QueryBuilder struct {
	client *Client
	db     string
}

// NewQueryBuilder cria um QueryBuilder com o cliente fornecido.
func NewQueryBuilder(client *Client) *QueryBuilder {
	return &QueryBuilder{
		client: client,
		db:     client.Database(),
	}
}

// ═══════════════════════════════════════════════════════════
// Queries do Diagnostician (T1)
// ═══════════════════════════════════════════════════════════

// DetectSkewQuery detecta skew via max/median input_records por stage.
func (qb *QueryBuilder) DetectSkewQuery(jobID string, threshold float64) string {
	return fmt.Sprintf(`
SELECT
    stage_id,
    task_id,
    input_records,
    max_records,
    median_records,
    input_records / median_records as skew_ratio
FROM (
    SELECT
        stage_id,
        task_id,
        input_records,
        max(input_records) OVER (PARTITION BY stage_id) as max_records,
        median(input_records) OVER (PARTITION BY stage_id) as median_records
    FROM %s.spark_tasks
    WHERE app_id = '%s'
      AND successful = 1
)
WHERE median_records > 0
  AND skew_ratio > %f
ORDER BY skew_ratio DESC
LIMIT 10`, qb.db, escapeSQLString(jobID), threshold)
}

// DetectDurationSkewQuery detecta skew via max/median executor_run_time_ms por stage.
func (qb *QueryBuilder) DetectDurationSkewQuery(jobID string, threshold float64) string {
	return fmt.Sprintf(`
SELECT
    stage_id,
    task_id,
    exec_time,
    max_time,
    median_time,
    exec_time / median_time as duration_skew_ratio
FROM (
    SELECT
        stage_id,
        task_id,
        executor_run_time_ms as exec_time,
        max(executor_run_time_ms) OVER (PARTITION BY stage_id) as max_time,
        median(executor_run_time_ms) OVER (PARTITION BY stage_id) as median_time
    FROM %s.spark_tasks
    WHERE app_id = '%s'
      AND successful = 1
)
WHERE median_time > 0
  AND duration_skew_ratio > %f
ORDER BY duration_skew_ratio DESC
LIMIT 10`, qb.db, escapeSQLString(jobID), threshold)
}

// DetectSpillQuery detecta spill usando shuffle bytes como proxy.
func (qb *QueryBuilder) DetectSpillQuery(jobID string, thresholdBytes int64) string {
	return fmt.Sprintf(`
SELECT
    stage_id,
    task_id,
    shuffle_read_bytes + shuffle_write_bytes as spill_proxy
FROM %s.spark_tasks
WHERE app_id = '%s'
  AND shuffle_read_bytes + shuffle_write_bytes > %d
ORDER BY spill_proxy DESC
LIMIT 10`, qb.db, escapeSQLString(jobID), thresholdBytes)
}

// DetectMemoryPressureQuery detecta pressão de memória.
func (qb *QueryBuilder) DetectMemoryPressureQuery(jobID string, gcThresholdMs int64) string {
	return fmt.Sprintf(`
SELECT
    stage_id,
    task_id,
    executor_run_time_ms,
    peak_execution_memory
FROM %s.spark_tasks
WHERE app_id = '%s'
  AND (
      executor_run_time_ms > %d
      OR peak_execution_memory > 500000000
  )
ORDER BY peak_execution_memory DESC
LIMIT 10`, qb.db, escapeSQLString(jobID), gcThresholdMs)
}

// ═══════════════════════════════════════════════════════════
// Queries do Recommender (T2/T3)
// ═══════════════════════════════════════════════════════════

// StageStatsQuery retorna estatísticas agregadas de um stage.
func (qb *QueryBuilder) StageStatsQuery(jobID string, stageID int64) string {
	return fmt.Sprintf(`
SELECT
    count() as total_tasks,
    avg(duration_ms) as avg_duration,
    max(duration_ms) as max_duration,
    quantile(0.5)(duration_ms) as median_duration,
    max(duration_ms) / quantile(0.5)(duration_ms) as skew_ratio,
    sum(shuffle_read_bytes) as shuffle_read,
    sum(shuffle_write_bytes) as shuffle_write
FROM %s.spark_tasks
WHERE app_id = '%s' AND stage_id = %d`, qb.db, escapeSQLString(jobID), stageID)
}

// TaskStatsQuery retorna estatísticas de uma task específica.
func (qb *QueryBuilder) TaskStatsQuery(jobID string, stageID, taskID int64) string {
	return fmt.Sprintf(`
SELECT
    duration_ms,
    executor_run_time_ms,
    input_bytes,
    output_bytes,
    shuffle_read_bytes,
    shuffle_write_bytes,
    peak_memory_bytes
FROM %s.spark_tasks
WHERE app_id = '%s' AND stage_id = %d AND task_id = %d
LIMIT 1`, qb.db, escapeSQLString(jobID), stageID, taskID)
}

// JobStagesQuery retorna um resumo de todos os stages de um job.
func (qb *QueryBuilder) JobStagesQuery(jobID string) string {
	return fmt.Sprintf(`
SELECT
    stage_id,
    count() as tasks,
    avg(duration_ms) as avg_dur,
    max(duration_ms) as max_dur
FROM %s.spark_tasks
WHERE app_id = '%s'
GROUP BY stage_id
ORDER BY stage_id`, qb.db, escapeSQLString(jobID))
}

// ═══════════════════════════════════════════════════════════
// Queries do Evidence Validator
// ═══════════════════════════════════════════════════════════

// ProvenanceQuery conta tasks de um job.
func (qb *QueryBuilder) ProvenanceQuery(jobID string) string {
	return fmt.Sprintf(`
SELECT COUNT(*)
FROM %s.spark_tasks
WHERE app_id = '%s'`, qb.db, escapeSQLString(jobID))
}

// SchemaValidationQuery valida campos obrigatórios.
func (qb *QueryBuilder) SchemaValidationQuery(jobID string) string {
	return fmt.Sprintf(`
SELECT
    countIf(app_id != '') as has_app_id,
    countIf(stage_id > 0) as has_stage_id,
    countIf(task_id >= 0) as has_task_id,
    countIf(task_type != '') as has_task_type,
    countIf(successful >= 0) as has_successful,
    countIf(executor_run_time_ms >= 0) as has_exec_time,
    countIf(input_records >= 0) as has_input_records
FROM %s.spark_tasks
WHERE app_id = '%s'`, qb.db, escapeSQLString(jobID))
}

// OperatorQuery retorna task types distintos de um job.
func (qb *QueryBuilder) OperatorQuery(jobID string) string {
	return fmt.Sprintf(`
SELECT DISTINCT task_type
FROM %s.spark_tasks
WHERE app_id = '%s'`, qb.db, escapeSQLString(jobID))
}

// CorrelationQuery verifica variação de records/duration.
func (qb *QueryBuilder) CorrelationQuery(jobID string) string {
	return fmt.Sprintf(`
SELECT
    stage_id,
    count(DISTINCT task_id) as task_count,
    varPop(input_records) as var_records,
    varPop(executor_run_time_ms) as var_duration
FROM %s.spark_tasks
WHERE app_id = '%s'
  AND successful = 1
GROUP BY stage_id
HAVING task_count > 1
ORDER BY var_records + var_duration DESC
LIMIT 1`, qb.db, escapeSQLString(jobID))
}

// DistributionQuery verifica distribuição (colapso, mediana).
func (qb *QueryBuilder) DistributionQuery(jobID string) string {
	return fmt.Sprintf(`
SELECT
    count(DISTINCT task_id) as task_count,
    median(input_records) as median_records,
    median(executor_run_time_ms) as median_duration
FROM %s.spark_tasks
WHERE app_id = '%s'
  AND successful = 1`, qb.db, escapeSQLString(jobID))
}

// StructuralQuery verifica consistência estrutural por stage.
func (qb *QueryBuilder) StructuralQuery(jobID string) string {
	return fmt.Sprintf(`
SELECT
    stage_id,
    groupUniqArray(task_type) as task_types,
    count(DISTINCT task_id) as task_count
FROM %s.spark_tasks
WHERE app_id = '%s'
  AND successful = 1
GROUP BY stage_id`, qb.db, escapeSQLString(jobID))
}

// SingleAppQuery verifica se há apenas um app_id.
func (qb *QueryBuilder) SingleAppQuery(jobID string) string {
	return fmt.Sprintf(`
SELECT COUNT(DISTINCT app_id)
FROM %s.spark_tasks
WHERE app_id = '%s'`, qb.db, escapeSQLString(jobID))
}

// ═══════════════════════════════════════════════════════════
// Queries do Spill Watcher
// ═══════════════════════════════════════════════════════════

// SpillDetectionQuery detecta spill via spark_raw_events (JSON).
func (qb *QueryBuilder) SpillDetectionQuery(jobID string, thresholdBytes int64) string {
	return fmt.Sprintf(`
SELECT
    JSONExtractInt(raw, 'Stage ID') as stage_id,
    JSONExtractInt(raw, 'Task Info', 'Task ID') as task_id,
    JSONExtractInt(raw, 'Task Metrics', 'Memory Bytes Spilled') as spill_mem,
    JSONExtractInt(raw, 'Task Metrics', 'Disk Bytes Spilled') as spill_disk,
    JSONExtractInt(raw, 'Task Metrics', 'Peak Execution Memory') as peak_memory,
    JSONExtractInt(raw, 'Task Metrics', 'Executor Run Time') as run_time_ms
FROM %s.spark_raw_events
WHERE app_id = '%s'
  AND event_type = 'SparkListenerTaskEnd'
  AND (
      JSONExtractInt(raw, 'Task Metrics', 'Memory Bytes Spilled') > %d
      OR JSONExtractInt(raw, 'Task Metrics', 'Disk Bytes Spilled') > %d
  )
ORDER BY spill_mem + spill_disk DESC
LIMIT 20`, qb.db, escapeSQLString(jobID), thresholdBytes, thresholdBytes)
}

// ═══════════════════════════════════════════════════════════
// Queries do MCP Server
// ═══════════════════════════════════════════════════════════

// DurationQuery retorna duração máxima e média por stage.
func (qb *QueryBuilder) DurationQuery(jobID string) string {
	return fmt.Sprintf(`
SELECT stage_id,
       max(duration_ms) as max_duration_ms,
       avg(duration_ms) as avg_duration_ms
FROM %s.spark_tasks
WHERE app_id = '%s'
GROUP BY stage_id
ORDER BY max_duration_ms DESC`, qb.db, escapeSQLString(jobID))
}

// TaskCountQuery retorna contagem de tasks por stage.
func (qb *QueryBuilder) TaskCountQuery(jobID string) string {
	return fmt.Sprintf(`
SELECT stage_id, count(*) as task_count
FROM %s.spark_tasks
WHERE app_id = '%s'
GROUP BY stage_id`, qb.db, escapeSQLString(jobID))
}

// StagesQuery retorna informações dos stages.
func (qb *QueryBuilder) StagesQuery(jobID string) string {
	return fmt.Sprintf(`
SELECT stage_id, stage_name, num_tasks as task_count
FROM %s.spark_stages
WHERE app_id = '%s'
ORDER BY stage_id`, qb.db, escapeSQLString(jobID))
}

// MemoryQuery retorna tasks com maior peak_execution_memory.
func (qb *QueryBuilder) MemoryQuery(jobID string) string {
	return fmt.Sprintf(`
SELECT stage_id, task_id, peak_execution_memory
FROM %s.spark_tasks
WHERE app_id = '%s'
ORDER BY peak_execution_memory DESC
LIMIT 20`, qb.db, escapeSQLString(jobID))
}

// SpillFallbackQuery retorna spill via spark_raw_events (JSONExtract) quando spark_tasks não tem coluna spill.
func (qb *QueryBuilder) SpillFallbackQuery(jobID string) string {
	return fmt.Sprintf(`
SELECT JSONExtractInt(raw, 'Stage ID') as stage_id,
       JSONExtractInt(raw, 'Task Info', 'Task ID') as task_id,
       JSONExtractInt(raw, 'Task Metrics', 'Memory Bytes Spilled') as spill_bytes,
       JSONExtractInt(raw, 'Task Metrics', 'Disk Bytes Spilled') as disk_spill_bytes
FROM %s.spark_raw_events
WHERE app_id = '%s' AND event_type = 'SparkListenerTaskEnd'
  AND JSONExtractInt(raw, 'Task Metrics', 'Memory Bytes Spilled') > 0
ORDER BY spill_bytes DESC
LIMIT 20`, qb.db, escapeSQLString(jobID))
}

// ═══════════════════════════════════════════════════════════
// Utilitários
// ═══════════════════════════════════════════════════════════

// Exec executa uma query e retorna o resultado JSONResponse.
func (qb *QueryBuilder) Exec(ctx context.Context, sql string) (*JSONResponse, error) {
	return qb.client.Query(ctx, sql)
}

// escapeSQLString escapa aspas simples para SQL.
func escapeSQLString(s string) string {
	return strings.ReplaceAll(s, "'", "\\'")
}
