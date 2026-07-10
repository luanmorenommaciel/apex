// Package mcp provides tools for the MCP (Model Context Protocol) server.
package mcp

import (
	"context"
	"fmt"

	"github.com/apex/go-apex/internal/clickhouse"
	"github.com/apex/go-apex/internal/models"
)

// QueryJob queries metrics and events for a Spark job from ClickHouse.
func QueryJob(appID string) (*models.JobQueryResult, error) {
	cfg := clickhouse.DefaultConfig()
	client, err := clickhouse.NewClient(cfg)
	if err != nil {
		return nil, fmt.Errorf("connect clickhouse: %w", err)
	}
	defer client.Close()

	result := &models.JobQueryResult{
		AppID:   appID,
		Found:   false,
		Events:  nil,
		Stages:  nil,
		Tasks:   nil,
		MetricsSummary: nil,
		TotalEvents: 0,
	}

	ctx := context.Background()

	// 1. spark_raw_events
	rows, err := client.QueryHTTP(ctx, fmt.Sprintf("SELECT event_type, event_json, timestamp FROM spark_raw_events WHERE app_id = '%s' ORDER BY timestamp", appID))
	if err == nil {
		result.Events = rows
		result.TotalEvents = len(rows)
		if len(rows) > 0 {
			result.Found = true
		}
	} else {
		result.ErrorEvents = err.Error()
	}

	// 2. spark_stages
	rows, err = client.QueryHTTP(ctx, fmt.Sprintf("SELECT stage_id, stage_name, status, duration_ms, num_tasks, timestamp FROM spark_stages WHERE app_id = '%s' ORDER BY stage_id", appID))
	if err == nil {
		result.Stages = rows
	} else {
		result.ErrorStages = err.Error()
	}

	// 3. spark_tasks
	rows, err = client.QueryHTTP(ctx, fmt.Sprintf("SELECT stage_id, task_id, task_index, executor_id, duration_ms, shuffle_read_bytes, shuffle_write_bytes, timestamp FROM spark_tasks WHERE app_id = '%s' ORDER BY task_id", appID))
	if err == nil {
		result.Tasks = rows
	} else {
		result.ErrorTasks = err.Error()
	}

	// 4. metrics summary
	rows, err = client.QueryHTTP(ctx, fmt.Sprintf("SELECT metric_name, avg(metric_value) as avg_value, max(metric_value) as max_value, count(*) as count FROM spark_metrics WHERE app_id = '%s' GROUP BY metric_name ORDER BY metric_name", appID))
	if err == nil {
		result.MetricsSummary = rows
	} else {
		result.ErrorMetrics = err.Error()
	}

	// 5. Anomaly detection (T1)
	result.Anomalies = detectAnomalies(result)
	return result, nil
}

func detectAnomalies(data *models.JobQueryResult) []map[string]interface{} {
	anomalies := []map[string]interface{}{}
	if len(data.Tasks) == 0 {
		return anomalies
	}

	durations := []float64{}
	for _, t := range data.Tasks {
		durations = append(durations, toFloat64(t["duration_ms"]))
	}
	positive := []float64{}
	for _, d := range durations {
		if d > 0 {
			positive = append(positive, d)
		}
	}
	if len(positive) > 0 {
		sortFloat64s(positive)
		median := positive[len(positive)/2]
		maxDur := positive[len(positive)-1]
		if median > 0 && maxDur/median > 10 {
			anomalies = append(anomalies, map[string]interface{}{
				"type":       "data_skew",
				"severity":   "high",
				"detail":     fmt.Sprintf("Task mais lenta (%.0fms) é %.1fx mais lenta que a mediana (%.0fms)", maxDur, maxDur/median, median),
				"suggestion": "Considere salting na chave de join ou aumentar shuffle.partitions",
			})
		}
	}

	shuffleReads := []float64{}
	shuffleWrites := []float64{}
	for _, t := range data.Tasks {
		shuffleReads = append(shuffleReads, toFloat64(t["shuffle_read_bytes"]))
		shuffleWrites = append(shuffleWrites, toFloat64(t["shuffle_write_bytes"]))
	}
	maxRead := maxFloat64(shuffleReads)
	maxWrite := maxFloat64(shuffleWrites)
	threshold := 100.0 * 1024 * 1024
	if maxRead > threshold {
		anomalies = append(anomalies, map[string]interface{}{
			"type":       "spill",
			"severity":   "medium",
			"detail":     fmt.Sprintf("Shuffle read máximo: %.1f MB", maxRead/(1024*1024)),
			"suggestion": "Verifique se há spill to disk; considere aumentar memory.fraction ou usar broadcast join",
		})
	}
	if maxWrite > threshold {
		anomalies = append(anomalies, map[string]interface{}{
			"type":       "spill",
			"severity":   "medium",
			"detail":     fmt.Sprintf("Shuffle write máximo: %.1f MB", maxWrite/(1024*1024)),
			"suggestion": "Verifique se há spill to disk; considere aumentar memory.fraction ou usar broadcast join",
		})
	}
	return anomalies
}

// GetRecommendations queries CREI for diagnosis and recommendations.
func GetRecommendations(appID string) (map[string]interface{}, error) {
	jobData, err := QueryJob(appID)
	if err != nil {
		return nil, err
	}
	return buildFallbackDiagnosis(appID, jobData), nil
}

func buildFallbackDiagnosis(appID string, jobData *models.JobQueryResult) map[string]interface{} {
	anomalies := jobData.Anomalies
	stages := jobData.Stages
	tasks := jobData.Tasks
	metrics := jobData.MetricsSummary

	diagnosisParts := []string{}
	rootCause := []string{}
	recommendations := []string{}

	if len(anomalies) > 0 {
		for _, a := range anomalies {
			diagnosisParts = append(diagnosisParts, a["detail"].(string))
			rootCause = append(rootCause, a["type"].(string))
			recommendations = append(recommendations, a["suggestion"].(string))
		}
	} else {
		diagnosisParts = append(diagnosisParts, "Nenhuma anomalia detectada pelas regras T1.")
		rootCause = append(rootCause, "no_anomaly")
		recommendations = append(recommendations, "Monitorar métricas de baseline")
	}

	if len(stages) > 0 {
		totalDur := 0.0
		for _, s := range stages {
			totalDur += toFloat64(s["duration_ms"])
		}
		diagnosisParts = append(diagnosisParts, fmt.Sprintf("Job executou %d stage(s) em %.0fms total.", len(stages), totalDur))
	}

	runbookSteps := []string{}
	codeFix := ""
	validation := ""
	for _, a := range anomalies {
		if a["type"] == "data_skew" {
			runbookSteps = []string{
				"1. Verificar distribuição da chave de join via countByKey",
				"2. Aplicar salting na chave: key + '_' + rand(0, N)",
				"3. Re-executar job e comparar duração das tasks",
				"4. Se persistir, avaliar broadcast join para smaller dataset",
			}
			codeFix = "# Exemplo de salting na chave de join\nfrom pyspark.sql.functions import rand, concat, lit\n\nsalt_count = 10\norders = orders.withColumn(\n    'salted_key',\n    concat('customer_id', lit('_'), (rand(42) * salt_count).cast('int'))\n)\ncustomers = customers.withColumn(\n    'salted_key',\n    explode(array([lit(f'_{i}') for i in range(salt_count)]))\n).withColumn('salted_key', concat('customer_id', 'salted_key'))\n\nresult = orders.join(customers, 'salted_key', 'inner')"
			validation = "Comparar max/median task duration antes e depois; skew ratio < 3x é aceitável"
		} else if a["type"] == "spill" {
			runbookSteps = []string{
				"1. Verificar spark.executor.memory e memory.fraction",
				"2. Aumentar spark.memory.fraction para 0.8 se executor tiver > 8GB",
				"3. Considerar broadcast join para datasets < 10MB",
				"4. Monitorar 'spill (memory)' no Spark UI",
			}
			codeFix = "# Exemplo de broadcast join para smaller dataset\nfrom pyspark.sql.functions import broadcast\n\nresult = large_df.join(broadcast(small_df), 'join_key', 'inner')"
			validation = "Verificar no Spark UI que 'Spill (Memory)' = 0 após correção"
		}
	}

	return map[string]interface{}{
		"app_id": appID,
		"source": "t1_fallback",
		"diagnosis": joinStrings(diagnosisParts, " | "),
		"root_cause": uniqueStrings(rootCause),
		"recommendations": uniqueStrings(recommendations),
		"runbook": map[string]interface{}{
			"steps":      runbookSteps,
			"code_fix":   codeFix,
			"validation": validation,
		},
		"confidence": func() float64 {
			if len(anomalies) > 0 {
				return 0.75
			}
			return 0.95
		}(),
		"job_data_summary": map[string]interface{}{
			"total_events":    jobData.TotalEvents,
			"stages_count":    len(stages),
			"tasks_count":     len(tasks),
			"anomalies_count": len(anomalies),
			"metrics_sample":  metrics[:minInt(5, len(metrics))],
		},
	}
}

func toFloat64(v interface{}) float64 {
	switch x := v.(type) {
	case float64:
		return x
	case float32:
		return float64(x)
	case int:
		return float64(x)
	case int64:
		return float64(x)
	case int32:
		return float64(x)
	case string:
		if f, err := strconvParseFloat(x); err == nil {
			return f
		}
	}
	return 0
}

func sortFloat64s(vals []float64) {
	for i := 0; i < len(vals); i++ {
		for j := i + 1; j < len(vals); j++ {
			if vals[i] > vals[j] {
				vals[i], vals[j] = vals[j], vals[i]
			}
		}
	}
}

func maxFloat64(vals []float64) float64 {
	if len(vals) == 0 {
		return 0
	}
	m := vals[0]
	for _, v := range vals[1:] {
		if v > m {
			m = v
		}
	}
	return m
}

func minInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func joinStrings(vals []string, sep string) string {
	if len(vals) == 0 {
		return ""
	}
	result := vals[0]
	for _, v := range vals[1:] {
		result += sep + v
	}
	return result
}

func uniqueStrings(vals []string) []string {
	seen := make(map[string]bool)
	out := []string{}
	for _, v := range vals {
		if !seen[v] {
			seen[v] = true
			out = append(out, v)
		}
	}
	return out
}

func strconvParseFloat(s string) (float64, error) {
	if s == "" {
		return 0, fmt.Errorf("empty")
	}
	start := 0
	neg := false
	if s[0] == '-' {
		neg = true
		start = 1
	}
	val := 0.0
	div := 1.0
	decimal := false
	for i := start; i < len(s); i++ {
		c := s[i]
		if c == '.' {
			decimal = true
			continue
		}
		if c < '0' || c > '9' {
			return 0, fmt.Errorf("invalid char")
		}
		if decimal {
			div *= 10
			val += float64(c-'0') / div
		} else {
			val = val*10 + float64(c-'0')
		}
	}
	if neg {
		val = -val
	}
	return val, nil
}
