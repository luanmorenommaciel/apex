package models

import "time"

// ═══════════════════════════════════════════════════════════
// Enums e constantes complementares (não definidos em finding.go/recommendation.go)
// ═══════════════════════════════════════════════════════════

// Tier representa o nível do diagnóstico/recomendação.
type Tier string

const (
	TierT1 Tier = "T1"
	TierT2 Tier = "T2"
	TierT3 Tier = "T3"
)

// Strategy representa a estratégia usada para gerar uma recomendação.
type Strategy string

const (
	StrategyRunbook   Strategy = "runbook"
	StrategyHeuristic Strategy = "heuristic"
	StrategyLLM       Strategy = "llm"
	StrategyLLMOllama Strategy = "llm_ollama"
	StrategyLLMOpenAI Strategy = "llm_openai"
)

// EvidenceStatus representa o status de validação de uma evidência.
type EvidenceStatus string

const (
	EvidenceStatusValid       EvidenceStatus = "valid"
	EvidenceStatusInvalid     EvidenceStatus = "invalid"
	EvidenceStatusIndeterminate EvidenceStatus = "indeterminate"
)

// MetricType representa os tipos de métricas consultáveis pelo MCP.
type MetricType string

const (
	MetricDuration MetricType = "duration"
	MetricTasks    MetricType = "tasks"
	MetricStages   MetricType = "stages"
	MetricMemory   MetricType = "memory"
	MetricSpill    MetricType = "spill"
)

// TaskType representa os tipos de tasks do Spark.
type TaskType string

const (
	TaskTypeShuffleMapTask TaskType = "ShuffleMapTask"
	TaskTypeResultTask     TaskType = "ResultTask"
)

// CorrelationMethod representa o método de correlação usado para detectar o stage hot.
type CorrelationMethod string

const (
	CorrelationMethodOperatorAccumulator    CorrelationMethod = "operator_accumulator"
	CorrelationMethodStageName                CorrelationMethod = "stage_name"
	CorrelationMethodLargestShuffleFallback CorrelationMethod = "largest_shuffle_fallback"
	CorrelationMethodNone                     CorrelationMethod = "none"
)

// AnomalyType representa o tipo de anomalia detectada no diagnóstico.
type AnomalyType string

const (
	AnomalyTypeSkew              AnomalyType = "data_skew"
	AnomalyTypeSpill             AnomalyType = "spill_to_disk"
	AnomalyTypeMemoryPressure    AnomalyType = "memory_pressure"
	AnomalyTypeGCThrash          AnomalyType = "gc_thrash"
	AnomalyTypeBroadcastMissed   AnomalyType = "broadcast_missed"
	AnomalyTypeTooManyPartitions AnomalyType = "too_many_partitions"
	AnomalyTypeUnknown           AnomalyType = "unknown"
)

// Severity representa o nível de severidade de um finding.
type Severity string

const (
	SeverityCritical Severity = "CRITICAL"
	SeverityHigh     Severity = "HIGH"
	SeverityMedium   Severity = "MEDIUM"
	SeverityLow      Severity = "LOW"
	SeverityError    Severity = "ERROR"
)

// SeverityOrder retorna a ordem de prioridade da severidade (menor = mais grave).
func SeverityOrder(s Severity) int {
	switch s {
	case SeverityCritical:
		return 0
	case SeverityHigh:
		return 1
	case SeverityMedium:
		return 2
	case SeverityLow:
		return 3
	case SeverityError:
		return 4
	default:
		return 99
	}
}

// Finding representa uma anomalia detectada em um job Spark.
// União de campos usados pelo watcher e pelo diagnostician.
type Finding struct {
	AnomalyType       AnomalyType `json:"type,omitempty"`
	Severity          Severity    `json:"severity,omitempty"`
	Confidence        float64     `json:"confidence,omitempty"`
	Description       string      `json:"description,omitempty"`
	StageID           *int64      `json:"stage_id,omitempty"`
	TaskID            *int64      `json:"task_id,omitempty"`
	MetricValue       *float64    `json:"metric_value,omitempty"`
	MetricThreshold   *float64    `json:"metric_threshold,omitempty"`
	Query             string      `json:"query,omitempty"`
	Watcher           string      `json:"watcher,omitempty"`
	Stage             int         `json:"stage,omitempty"`
	HotPartition      int         `json:"hot_partition,omitempty"`
	CorrelationMethod string      `json:"correlation_method,omitempty"`
	EvidenceStatus    string      `json:"evidence_status,omitempty"`
	QualityIssues     []string    `json:"quality_issues,omitempty"`
	Evidence          []string    `json:"evidence,omitempty"`
	RootCause         string      `json:"root_cause,omitempty"`
	Recommendations   []string    `json:"recommendations,omitempty"`
}

// DiagnosisResult é o resultado consolidado do diagnóstico T1.
type DiagnosisResult struct {
	Tier          string    `json:"tier"`
	JobID         string    `json:"job_id"`
	FindingsCount int       `json:"findings_count"`
	Findings      []Finding `json:"findings"`
	ResolvedByT1  bool      `json:"resolved_by_t1"`
}

// Recommendation representa uma recomendação de correção para uma anomalia detectada.
type Recommendation struct {
	AnomalyType    string       `json:"anomaly_type"`
	Confidence     float64      `json:"confidence"`
	Summary        string       `json:"summary"`
	Steps          []StepAction `json:"steps"`
	CodeFix        string       `json:"code_fix,omitempty"`
	ExpectedImpact string       `json:"expected_impact"`
	RunbookID      string       `json:"runbook_id,omitempty"`
}

// StepAction representa um passo de ação em uma recomendação.
type StepAction struct {
	Action  string `json:"action"`
	Details string `json:"details"`
}

type AnomalyReport struct {
	AppID          string                 `json:"app_id"`
	AnomalyType    string                 `json:"anomaly_type"` // SKEW, SPILL, OOM, GC_PRESSURE, UNKNOWN, TASK_FAILURE
	Severity       string                 `json:"severity"`     // CRITICAL, HIGH, MEDIUM, LOW
	Description    string                 `json:"description"`
	Evidence       map[string]interface{} `json:"evidence"`
	AffectedStages []int                  `json:"affected_stages"`
	Confidence     float64                `json:"confidence"`
}

// JobQueryResult representa o resultado de uma consulta de job ao ClickHouse.
type JobQueryResult struct {
	AppID          string                   `json:"app_id"`
	Found          bool                     `json:"found"`
	Events         []map[string]interface{} `json:"events,omitempty"`
	Stages         []map[string]interface{} `json:"stages,omitempty"`
	Tasks          []map[string]interface{} `json:"tasks,omitempty"`
	MetricsSummary []map[string]interface{} `json:"metrics_summary,omitempty"`
	TotalEvents    int                      `json:"total_events"`
	Anomalies      []map[string]interface{} `json:"anomalies,omitempty"`
	ErrorEvents    string                   `json:"error_events,omitempty"`
	ErrorStages    string                   `json:"error_stages,omitempty"`
	ErrorTasks     string                   `json:"error_tasks,omitempty"`
	ErrorMetrics   string                   `json:"error_metrics,omitempty"`
}

// RecommendationSet é um conjunto de recomendações para um job.
type RecommendationSet struct {
	AppID           string         `json:"app_id"`
	Source          string         `json:"source"`
	Diagnosis       string         `json:"diagnosis"`
	RootCauses      []string       `json:"root_causes"`
	Recommendations []string       `json:"recommendations"`
	Runbook         *RunbookResult `json:"runbook,omitempty"`
	Confidence      float64        `json:"confidence"`
	JobDataSummary  JobDataSummary `json:"job_data_summary"`
}

// RunbookResult é uma visão simplificada do runbook usado no resultado.
type RunbookResult struct {
	Steps      []string `json:"steps"`
	CodeFix    string   `json:"code_fix,omitempty"`
	Validation string   `json:"validation,omitempty"`
}

// JobDataSummary fornece um resumo dos dados do job.
type JobDataSummary struct {
	TotalEvents    int         `json:"total_events"`
	StagesCount    int         `json:"stages_count"`
	TasksCount     int         `json:"tasks_count"`
	AnomaliesCount int         `json:"anomalies_count"`
	MetricsSample  []interface{} `json:"metrics_sample,omitempty"`
}

// AnalysisResult representa o resultado completo da análise de um job.
type AnalysisResult struct {
	AppID           string                `json:"app_id"`
	Status          string                `json:"status"`
	Message         string                `json:"message,omitempty"`
	Anomalies       []AnomalyReport       `json:"anomalies,omitempty"`
	Recommendations []Recommendation      `json:"recommendations,omitempty"`
	Reviews         []map[string]interface{} `json:"reviews,omitempty"`
}

// ReviewResult representa o resultado da revisão automática de uma recomendação.
type ReviewResult struct {
	Passed     bool     `json:"passed"`
	Issues     []string `json:"issues,omitempty"`
	Confidence float64  `json:"confidence"`
	Severity   string   `json:"severity"`
}

// ═══════════════════════════════════════════════════════════
// Tipos de domínio complementares
// ═══════════════════════════════════════════════════════════

// DiagnosisResponse é a resposta completa do pipeline T1→T2→T3.
type DiagnosisResponse struct {
	JobID           string           `json:"job_id"`
	Tier            Tier             `json:"tier"`
	Status          string           `json:"status"`
	FindingsCount   int              `json:"findings_count"`
	Findings        []Finding        `json:"findings"`
	Recommendations []FindingRecPair `json:"recommendations,omitempty"`
	T1Result        *DiagnosisResult `json:"t1_result,omitempty"`
	Message         string           `json:"message,omitempty"`
}

// FindingRecPair agrupa um finding com sua recomendação.
type FindingRecPair struct {
	Finding        Finding         `json:"finding"`
	Recommendation Recommendation `json:"recommendation"`
}

// StageStats representa estatísticas agregadas de um stage.
type StageStats struct {
	TotalTasks        int64   `json:"total_tasks"`
	AvgDurationMs     float64 `json:"avg_duration_ms"`
	MaxDurationMs     float64 `json:"max_duration_ms"`
	MedianDurationMs  float64 `json:"median_duration_ms"`
	SkewRatio         float64 `json:"skew_ratio"`
	ShuffleReadBytes  int64   `json:"shuffle_read_bytes"`
	ShuffleWriteBytes int64   `json:"shuffle_write_bytes"`
}

// TaskStats representa estatísticas de uma task específica.
type TaskStats struct {
	DurationMs        int64 `json:"duration_ms"`
	ExecutorRunTimeMs int64 `json:"executor_run_time_ms"`
	InputBytes        int64 `json:"input_bytes"`
	OutputBytes       int64 `json:"output_bytes"`
	ShuffleReadBytes  int64 `json:"shuffle_read_bytes"`
	ShuffleWriteBytes int64 `json:"shuffle_write_bytes"`
	PeakMemoryBytes   int64 `json:"peak_memory_bytes"`
}

// StageSummary representa um resumo de stage para o job.
type StageSummary struct {
	StageID       int64   `json:"stage_id"`
	Tasks         int64   `json:"tasks"`
	AvgDurationMs float64 `json:"avg_duration_ms"`
	MaxDurationMs float64 `json:"max_duration_ms"`
}

// JobContext coleta contexto adicional do ClickHouse para enriquecer diagnósticos.
type JobContext struct {
	HasData    bool           `json:"has_data"`
	JobID      string         `json:"job_id"`
	StageStats *StageStats    `json:"stage_stats,omitempty"`
	TaskStats  *TaskStats     `json:"task_stats,omitempty"`
	Stages     []StageSummary `json:"stages,omitempty"`
	Error      string         `json:"error,omitempty"`
}

// ValidationResult representa o resultado de uma regra de validação.
type ValidationResult struct {
	Rule    string         `json:"rule"`
	Status  EvidenceStatus `json:"status"`
	Message string         `json:"message"`
}

// ValidationReport é o resultado consolidado da validação de evidências.
type ValidationReport struct {
	JobID         string             `json:"job_id"`
	Status        EvidenceStatus     `json:"status"`
	Rules         []ValidationResult `json:"rules"`
	Passed        int                `json:"passed"`
	Failed        int                `json:"failed"`
	Indeterminate int                `json:"indeterminate"`
}

// SpillInfo representa informação de spill de uma task.
type SpillInfo struct {
	StageID          int64    `json:"stage_id"`
	TaskID           int64    `json:"task_id"`
	SpillBytes       int64    `json:"spill_bytes"`
	SpillMB          float64  `json:"spill_mb"`
	SpillMemoryBytes int64    `json:"spill_memory_bytes"`
	SpillDiskBytes   int64    `json:"spill_disk_bytes"`
	PeakMemory       int64    `json:"peak_memory"`
	RunTimeMs        int64    `json:"run_time_ms"`
	Severity         Severity `json:"severity"`
}

// SpillDetectionResult é o resultado da detecção de spill.
type SpillDetectionResult struct {
	Status          string    `json:"status"`
	JobID           string    `json:"job_id,omitempty"`
	ThresholdMB     float64   `json:"threshold_mb,omitempty"`
	SpillsCount     int       `json:"spills_count,omitempty"`
	TotalSpillMB    float64   `json:"total_spill_mb,omitempty"`
	Spills          []SpillInfo `json:"spills,omitempty"`
	Recommendations []string  `json:"recommendations,omitempty"`
	Message         string    `json:"message,omitempty"`
}

// HealthCheck representa o resultado de um health check.
type HealthCheck struct {
	Service string `json:"service"`
	Status  string `json:"status"`
}

// MCPResponse é a resposta padrão do MCP Server.
type MCPResponse struct {
	Tool      string            `json:"tool,omitempty"`
	JobID     string            `json:"job_id,omitempty"`
	Metric    MetricType        `json:"metric,omitempty"`
	Data      interface{}       `json:"data,omitempty"`
	Status    string            `json:"status,omitempty"`
	Checks    map[string]string `json:"checks,omitempty"`
	Error     string            `json:"error,omitempty"`
	Diagnosis *DiagnosisResponse  `json:"diagnosis,omitempty"`
}

// MCPTool representa uma tool exposta pelo MCP Server.
type MCPTool struct {
	Name        string                 `json:"name"`
	Description string                 `json:"description"`
	Parameters  map[string]interface{} `json:"parameters"`
}

// MCPServerInfo representa as informações do servidor MCP.
type MCPServerInfo struct {
	Service string    `json:"service"`
	Version string    `json:"version"`
	Tools   []MCPTool `json:"tools"`
}

// CREIServerInfo representa as informações do servidor CREI.
type CREIServerInfo struct {
	Service   string   `json:"service"`
	Version   string   `json:"version"`
	Endpoints []string `json:"endpoints"`
}

// ═══════════════════════════════════════════════════════════
// Tipos para o validator (evidências baseadas em eventos)
// ═══════════════════════════════════════════════════════════

// EvidenceBundle agrupa eventos e scenario para validação.
type EvidenceBundle struct {
	Events       []map[string]interface{} `json:"events"`
	ScenarioPath string                   `json:"scenario_path"`
	Scenario     map[string]interface{}   `json:"scenario"`
}

// EvidenceValidationResult é o resultado da validação de evidências.
type EvidenceValidationResult struct {
	Status            string                 `json:"status"`
	QualityIssues     []string               `json:"quality_issues"`
	CorrelationMethod string                 `json:"correlation_method"`
	StageID           *int                   `json:"stage_id,omitempty"`
	Records           []int                  `json:"records,omitempty"`
	Metrics           map[string]interface{} `json:"metrics,omitempty"`
	ProvenanceHash    string                 `json:"provenance_hash,omitempty"`
}

// HottestReduceStageDetails detalha o stage de reduce mais quente.
type HottestReduceStageDetails struct {
	StageID           int                      `json:"stage_id"`
	Tasks             []map[string]interface{} `json:"tasks"`
	Records           []int                    `json:"records"`
	CorrelationMethod string                   `json:"correlation_method"`
}


// Anomaly represents a detected anomaly for MCP tools.
type Anomaly struct {
	Type       string `json:"type"`
	Severity   string `json:"severity"`
	Detail     string `json:"detail"`
	Suggestion string `json:"suggestion"`
}

// ═══════════════════════════════════════════════════════════
// Tipos de dados do ClickHouse (tabelas)
// ═══════════════════════════════════════════════════════════

// SparkTask representa uma linha da tabela spark_tasks no ClickHouse.
type SparkTask struct {
	AppID               string    `json:"app_id"`
	StageID             int64     `json:"stage_id"`
	TaskID              int64     `json:"task_id"`
	TaskType            string    `json:"task_type"`
	Successful          int8      `json:"successful"`
	DurationMs          int64     `json:"duration_ms"`
	ExecutorRunTimeMs   int64     `json:"executor_run_time_ms"`
	InputRecords        int64     `json:"input_records"`
	InputBytes          int64     `json:"input_bytes"`
	OutputRecords       int64     `json:"output_records"`
	OutputBytes         int64     `json:"output_bytes"`
	ShuffleReadBytes    int64     `json:"shuffle_read_bytes"`
	ShuffleWriteBytes   int64     `json:"shuffle_write_bytes"`
	PeakExecutionMemory int64     `json:"peak_execution_memory"`
	PeakMemoryBytes     int64     `json:"peak_memory_bytes"`
	MemoryBytesSpilled  int64     `json:"memory_bytes_spilled"`
	DiskBytesSpilled    int64     `json:"disk_bytes_spilled"`
	GCTimeMs            int64     `json:"gc_time_ms"`
	EventTime           time.Time `json:"event_time"`
}

// SparkStage representa uma linha da tabela spark_stages no ClickHouse.
type SparkStage struct {
	AppID          string `json:"app_id"`
	StageID        int64  `json:"stage_id"`
	StageName      string `json:"stage_name"`
	NumTasks       int64  `json:"num_tasks"`
	SubmissionTime int64  `json:"submission_time_ms,omitempty"`
	CompletionTime int64  `json:"completion_time_ms,omitempty"`
}

// SparkRawEvent representa uma linha da tabela spark_raw_events no ClickHouse.
type SparkRawEvent struct {
	AppID     string    `json:"app_id"`
	EventType string    `json:"event_type"`
	EventJSON string    `json:"event_json"`
	Raw       string    `json:"raw"`
	EventTime time.Time `json:"event_time"`
}

// SparkSQLExecution representa uma linha da tabela spark_sql_executions no ClickHouse.
type SparkSQLExecution struct {
	AppID        string `json:"app_id"`
	ExecutionID  int64  `json:"execution_id"`
	Description  string `json:"description"`
	PhysicalPlan string `json:"physical_plan_description"`
	StartTime    int64  `json:"start_time_ms,omitempty"`
	EndTime      int64  `json:"end_time_ms,omitempty"`
}

// DurationRow representa uma linha do resultado da query de duration.
type DurationRow struct {
	StageID       int64   `json:"stage_id"`
	MaxDurationMs float64 `json:"max_duration_ms"`
	AvgDurationMs float64 `json:"avg_duration_ms"`
}

// TaskCountRow representa uma linha do resultado da query de tasks.
type TaskCountRow struct {
	StageID   int64 `json:"stage_id"`
	TaskCount int64 `json:"task_count"`
}

// StageRow representa uma linha do resultado da query de stages.
type StageRow struct {
	StageID   int64  `json:"stage_id"`
	StageName string `json:"stage_name"`
	TaskCount int64  `json:"task_count"`
}

// MemoryRow representa uma linha do resultado da query de memory.
type MemoryRow struct {
	StageID             int64 `json:"stage_id"`
	TaskID              int64 `json:"task_id"`
	PeakExecutionMemory int64 `json:"peak_execution_memory"`
}

// SpillRow representa uma linha do resultado da query de spill.
type SpillRow struct {
	StageID        int64 `json:"stage_id"`
	TaskID         int64 `json:"task_id"`
	SpillBytes     int64 `json:"spill_bytes"`
	DiskSpillBytes int64 `json:"disk_spill_bytes"`
}

// SkewRow representa uma linha do resultado da query de skew.
type SkewRow struct {
	StageID       int64   `json:"stage_id"`
	TaskID        int64   `json:"task_id"`
	Records       int64   `json:"records"`
	MaxRecords    int64   `json:"max_records"`
	MedianRecords int64   `json:"median_records"`
	SkewRatio     float64 `json:"skew_ratio"`
}

// DurationSkewRow representa uma linha do resultado da query de duration skew.
type DurationSkewRow struct {
	StageID           int64   `json:"stage_id"`
	TaskID            int64   `json:"task_id"`
	ExecTime          int64   `json:"exec_time"`
	MaxTime           int64   `json:"max_time"`
	MedianTime        int64   `json:"median_time"`
	DurationSkewRatio float64 `json:"duration_skew_ratio"`
}

// SpillProxyRow representa uma linha do resultado da query de spill proxy.
type SpillProxyRow struct {
	StageID    int64 `json:"stage_id"`
	TaskID     int64 `json:"task_id"`
	SpillProxy int64 `json:"spill_proxy"`
}

// MemoryPressureRow representa uma linha do resultado da query de memory pressure.
type MemoryPressureRow struct {
	StageID             int64 `json:"stage_id"`
	TaskID              int64 `json:"task_id"`
	ExecutorRunTimeMs   int64 `json:"executor_run_time_ms"`
	PeakExecutionMemory int64 `json:"peak_execution_memory"`
}

// SchemaValidationRow representa uma linha do resultado da validação de schema.
type SchemaValidationRow struct {
	HasAppID        int64 `json:"has_app_id"`
	HasStageID      int64 `json:"has_stage_id"`
	HasTaskID       int64 `json:"has_task_id"`
	HasTaskType     int64 `json:"has_task_type"`
	HasSuccessful   int64 `json:"has_successful"`
	HasExecTime     int64 `json:"has_exec_time"`
	HasInputRecords int64 `json:"has_input_records"`
}

// CorrelationRow representa uma linha do resultado da validação de correlação.
type CorrelationRow struct {
	StageID     int64   `json:"stage_id"`
	TaskCount   int64   `json:"task_count"`
	VarRecords  float64 `json:"var_records"`
	VarDuration float64 `json:"var_duration"`
}

// DistributionRow representa uma linha do resultado da validação de distribuição.
type DistributionRow struct {
	TaskCount      int64   `json:"task_count"`
	MedianRecords  float64 `json:"median_records"`
	MedianDuration float64 `json:"median_duration"`
}

// StructuralRow representa uma linha do resultado da validação estrutural.
type StructuralRow struct {
	StageID   int64    `json:"stage_id"`
	TaskTypes []string `json:"task_types"`
	TaskCount int64    `json:"task_count"`
}
