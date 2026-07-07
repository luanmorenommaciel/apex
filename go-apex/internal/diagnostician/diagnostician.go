package diagnostician

import (
	"context"
	"fmt"
	"os"
	"strconv"

	"github.com/apex/go-apex/internal/clickhouse"
	"github.com/apex/go-apex/internal/models"
)

// Diagnostician performs Tier 1 anomaly detection for Spark jobs using SQL rules.
type Diagnostician struct {
	client           *clickhouse.Client
	skewRatio        float64
	spillThresholdMB float64
	gcTimeRatio      float64
	failedTaskRate   float64
}

// NewDiagnostician creates a new Diagnostician with default or env-configured thresholds.
func NewDiagnostician(cfg clickhouse.Config) (*Diagnostician, error) {
	client, err := clickhouse.NewClient(cfg)
	if err != nil {
		return nil, err
	}
	return &Diagnostician{
		client:           client,
		skewRatio:        parseEnvFloat("SKEW_RATIO", 5.0),
		spillThresholdMB: parseEnvFloat("SPILL_THRESHOLD_MB", 100.0),
		gcTimeRatio:      parseEnvFloat("GC_TIME_RATIO", 0.3),
		failedTaskRate:   parseEnvFloat("FAILED_TASK_RATE", 0.05),
	}, nil
}

func parseEnvFloat(key string, fallback float64) float64 {
	if v := os.Getenv(key); v != "" {
		if f, err := strconv.ParseFloat(v, 64); err == nil {
			return f
		}
	}
	return fallback
}

// Close closes the underlying ClickHouse client.
func (d *Diagnostician) Close() error {
	return d.client.Close()
}

// Diagnose runs the full diagnostic pipeline for an app_id.
func (d *Diagnostician) Diagnose(appID string) ([]models.AnomalyReport, error) {
	var reports []models.AnomalyReport

	skew, err := d.detectSkew(appID)
	if err != nil {
		return nil, fmt.Errorf("detect skew: %w", err)
	}
	reports = append(reports, skew...)

	spill, err := d.detectSpill(appID)
	if err != nil {
		return nil, fmt.Errorf("detect spill: %w", err)
	}
	reports = append(reports, spill...)

	gc, err := d.detectGCPressure(appID)
	if err != nil {
		return nil, fmt.Errorf("detect gc pressure: %w", err)
	}
	reports = append(reports, gc...)

	oom, err := d.detectOOM(appID)
	if err != nil {
		return nil, fmt.Errorf("detect oom: %w", err)
	}
	reports = append(reports, oom...)

	severityOrder := map[string]int{
		"CRITICAL": 0,
		"HIGH":     1,
		"MEDIUM":   2,
		"LOW":      3,
	}
	for i := 0; i < len(reports); i++ {
		for j := i + 1; j < len(reports); j++ {
			if severityOrder[reports[i].Severity] > severityOrder[reports[j].Severity] {
				reports[i], reports[j] = reports[j], reports[i]
			}
		}
	}
	return reports, nil
}

func (d *Diagnostician) detectSkew(appID string) ([]models.AnomalyReport, error) {
	query := fmt.Sprintf(`
		SELECT
			stage_id,
			max(task_duration_ms) AS max_duration,
			median(task_duration_ms) AS median_duration,
			count() AS task_count,
			max_duration / if(median_duration = 0, 1, median_duration) AS skew_ratio
		FROM spark_tasks
		WHERE app_id = '%s'
		GROUP BY stage_id
		HAVING skew_ratio > %f
		ORDER BY skew_ratio DESC
	`, appID, d.skewRatio)

	rows, err := d.client.QueryHTTP(context.Background(), query)
	if err != nil {
		return nil, err
	}

	var reports []models.AnomalyReport
	for _, row := range rows {
		stageID := toInt(row["stage_id"])
		maxDur := toFloat64(row["max_duration"])
		medianDur := toFloat64(row["median_duration"])
		taskCount := toInt(row["task_count"])
		skewRatio := toFloat64(row["skew_ratio"])

		severity := "HIGH"
		if skewRatio > 30 {
			severity = "CRITICAL"
		}
		confidence := 0.95
		if skewRatio < 100 {
			confidence = 0.5 + skewRatio/100.0
		}
		if confidence > 0.95 {
			confidence = 0.95
		}

		reports = append(reports, models.AnomalyReport{
			AppID:       appID,
			AnomalyType: "SKEW",
			Severity:    severity,
			Description: fmt.Sprintf("Stage %d apresenta skew de %.1fx: task mais lenta (%.0fms) vs mediana (%.0fms). Total de tasks: %d.", stageID, skewRatio, maxDur, medianDur, taskCount),
			Evidence: map[string]interface{}{
				"stage_id":          stageID,
				"max_duration_ms":   maxDur,
				"median_duration_ms": medianDur,
				"task_count":        taskCount,
				"skew_ratio":        skewRatio,
			},
			AffectedStages: []int{stageID},
			Confidence:     confidence,
		})
	}
	return reports, nil
}

func (d *Diagnostician) detectSpill(appID string) ([]models.AnomalyReport, error) {
	thresholdBytes := d.spillThresholdMB * 1024 * 1024
	query := fmt.Sprintf(`
		SELECT
			stage_id,
			sum(shuffle_bytes_written) AS total_spill_bytes,
			count() AS task_count,
			avg(task_duration_ms) AS avg_duration
		FROM spark_tasks
		WHERE app_id = '%s'
		  AND shuffle_bytes_written > %f
		GROUP BY stage_id
		HAVING total_spill_bytes > 0
		ORDER BY total_spill_bytes DESC
	`, appID, thresholdBytes)

	rows, err := d.client.QueryHTTP(context.Background(), query)
	if err != nil {
		return nil, err
	}

	var reports []models.AnomalyReport
	for _, row := range rows {
		stageID := toInt(row["stage_id"])
		spillBytes := toFloat64(row["total_spill_bytes"])
		taskCount := toInt(row["task_count"])
		avgDuration := toFloat64(row["avg_duration"])
		spillMB := spillBytes / (1024 * 1024)

		severity := "MEDIUM"
		if spillMB > 500 {
			severity = "HIGH"
		}
		confidence := 0.6 + spillMB/2000.0
		if confidence > 0.95 {
			confidence = 0.95
		}

		reports = append(reports, models.AnomalyReport{
			AppID:       appID,
			AnomalyType: "SPILL",
			Severity:    severity,
			Description: fmt.Sprintf("Stage %d com %.1fMB de spill para disco em %d tasks. Duração média: %.0fms.", stageID, spillMB, taskCount, avgDuration),
			Evidence: map[string]interface{}{
				"stage_id":        stageID,
				"spill_bytes":     spillBytes,
				"spill_mb":        spillMB,
				"task_count":      taskCount,
				"avg_duration_ms": avgDuration,
			},
			AffectedStages: []int{stageID},
			Confidence:     confidence,
		})
	}
	return reports, nil
}

func (d *Diagnostician) detectGCPressure(appID string) ([]models.AnomalyReport, error) {
	query := fmt.Sprintf(`
		SELECT
			stage_id,
			task_id,
			task_duration_ms,
			gc_time_ms,
			gc_time_ms / if(task_duration_ms = 0, 1, task_duration_ms) AS gc_ratio
		FROM spark_tasks
		WHERE app_id = '%s'
		  AND gc_time_ms > 0
		HAVING gc_ratio > %f
		ORDER BY gc_ratio DESC
		LIMIT 10
	`, appID, d.gcTimeRatio)

	rows, err := d.client.QueryHTTP(context.Background(), query)
	if err != nil {
		return nil, err
	}

	// Group by stage
	stageGC := make(map[int][]map[string]interface{})
	for _, row := range rows {
		stageID := toInt(row["stage_id"])
		stageGC[stageID] = append(stageGC[stageID], map[string]interface{}{
			"task_id":     toInt(row["task_id"]),
			"duration_ms": toFloat64(row["task_duration_ms"]),
			"gc_time_ms":  toFloat64(row["gc_time_ms"]),
			"gc_ratio":    toFloat64(row["gc_ratio"]),
		})
	}

	var reports []models.AnomalyReport
	for stageID, tasks := range stageGC {
		maxGCRatio := 0.0
		for _, t := range tasks {
			if r := t["gc_ratio"].(float64); r > maxGCRatio {
				maxGCRatio = r
			}
		}
		severity := "MEDIUM"
		if maxGCRatio > 0.5 {
			severity = "HIGH"
		}
		confidence := 0.5 + maxGCRatio
		if confidence > 0.9 {
			confidence = 0.9
		}
		reports = append(reports, models.AnomalyReport{
			AppID:       appID,
			AnomalyType: "GC_PRESSURE",
			Severity:    severity,
			Description: fmt.Sprintf("Stage %d com %d tasks sob alta pressão de GC. Maior gc_ratio: %.1f%%. Sugere heap insuficiente ou coleta de dados muito grande por task.", stageID, len(tasks), maxGCRatio*100),
			Evidence: map[string]interface{}{
				"stage_id":       stageID,
				"affected_tasks": len(tasks),
				"max_gc_ratio":   maxGCRatio,
				"sample_tasks":   tasks[:min(3, len(tasks))],
			},
			AffectedStages: []int{stageID},
			Confidence:     confidence,
		})
	}
	return reports, nil
}

func (d *Diagnostician) detectOOM(appID string) ([]models.AnomalyReport, error) {
	query := fmt.Sprintf(`
		SELECT
			stage_id,
			count() AS failed_count,
			groupUniqArray(10)(reason) AS failure_reasons
		FROM spark_tasks
		WHERE app_id = '%s'
		  AND failed = 1
		GROUP BY stage_id
		HAVING failed_count > 0
		ORDER BY failed_count DESC
	`, appID)

	rows, err := d.client.QueryHTTP(context.Background(), query)
	if err != nil {
		return nil, err
	}

	var reports []models.AnomalyReport
	for _, row := range rows {
		stageID := toInt(row["stage_id"])
		failedCount := toInt(row["failed_count"])
		reasonsRaw := row["failure_reasons"]
		reasons := toStringSlice(reasonsRaw)

		isOOM := false
		for _, r := range reasons {
			if contains(r, "OutOfMemory") || contains(r, "OOM") {
				isOOM = true
				break
			}
		}

		anomalyType := "TASK_FAILURE"
		severity := "HIGH"
		confidence := 0.7
		if isOOM {
			anomalyType = "OOM"
			severity = "CRITICAL"
			confidence = 0.9
		}

		reports = append(reports, models.AnomalyReport{
			AppID:       appID,
			AnomalyType: anomalyType,
			Severity:    severity,
			Description: fmt.Sprintf("Stage %d com %d tasks falhas. Razões: %v.", stageID, failedCount, reasons),
			Evidence: map[string]interface{}{
				"stage_id":        stageID,
				"failed_count":    failedCount,
				"failure_reasons": reasons,
				"oom_detected":    isOOM,
			},
			AffectedStages: []int{stageID},
			Confidence:     confidence,
		})
	}
	return reports, nil
}

func toInt(v interface{}) int {
	switch x := v.(type) {
	case int:
		return x
	case int8:
		return int(x)
	case int16:
		return int(x)
	case int32:
		return int(x)
	case int64:
		return int(x)
	case uint:
		return int(x)
	case uint8:
		return int(x)
	case uint16:
		return int(x)
	case uint32:
		return int(x)
	case uint64:
		return int(x)
	case float32:
		return int(x)
	case float64:
		return int(x)
	case string:
		if i, err := strconv.Atoi(x); err == nil {
			return i
		}
	}
	return 0
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
		if f, err := strconv.ParseFloat(x, 64); err == nil {
			return f
		}
	}
	return 0
}

func toStringSlice(v interface{}) []string {
	if v == nil {
		return nil
	}
	if arr, ok := v.([]interface{}); ok {
		out := make([]string, 0, len(arr))
		for _, e := range arr {
			if s, ok := e.(string); ok {
				out = append(out, s)
			}
		}
		return out
	}
	if s, ok := v.(string); ok {
		return []string{s}
	}
	return nil
}

func contains(s, substr string) bool {
	return len(s) >= len(substr) && (s == substr || len(s) > 0 && len(substr) > 0 && indexOf(s, substr) >= 0)
}

func indexOf(s, substr string) int {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return i
		}
	}
	return -1
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
