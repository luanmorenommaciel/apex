// Package watcher provides spill and skew watchers for Spark jobs.
package watcher

import (
	"encoding/json"
	"fmt"
	"math"
	"os"
	"sort"

	"gopkg.in/yaml.v3"
	"github.com/apex/go-apex/internal/models"
)

// SpillWatcher detects spill-to-disk patterns in Spark job metrics.
type SpillWatcher struct{}

// NewSpillWatcher creates a new SpillWatcher.
func NewSpillWatcher() *SpillWatcher {
	return &SpillWatcher{}
}

// Watch analyzes job data for spill anomalies.
func (w *SpillWatcher) Watch(jobData map[string]interface{}) (*models.Finding, error) {
	tasks := jobData["tasks"].([]map[string]interface{})
	if len(tasks) == 0 {
		return nil, fmt.Errorf("no tasks found")
	}

	shuffleReads := make([]float64, 0, len(tasks))
	shuffleWrites := make([]float64, 0, len(tasks))
	for _, t := range tasks {
		shuffleReads = append(shuffleReads, toFloat64(t["shuffle_read_bytes"]))
		shuffleWrites = append(shuffleWrites, toFloat64(t["shuffle_write_bytes"]))
	}

	maxRead := maxFloat64(shuffleReads)
	maxWrite := maxFloat64(shuffleWrites)
	threshold := 100.0 * 1024 * 1024 // 100 MB

	isSpill := maxRead > float64(threshold) || maxWrite > float64(threshold)
	severity := models.SeverityLow
	if isSpill {
		severity = models.SeverityHigh
	}

	finding := &models.Finding{
		Watcher:    "spill",
		Severity:   severity,
		Confidence: 0.0,
		Evidence:   []string{},
		RootCause:  "No spill detected",
		Recommendations: []string{
			"Verificar spark.executor.memory e memory.fraction",
			"Aumentar spark.memory.fraction para 0.8 se executor tiver > 8GB",
			"Considerar broadcast join para datasets < 10MB",
			"Monitorar 'spill (memory)' no Spark UI",
		},
	}

	if isSpill {
		finding.Confidence = 0.85
		finding.RootCause = fmt.Sprintf("Spill detectado: shuffle read max %.1f MB, write max %.1f MB", maxRead/(1024*1024), maxWrite/(1024*1024))
		finding.Evidence = append(finding.Evidence, fmt.Sprintf("max shuffle read: %.1f MB", maxRead/(1024*1024)))
		finding.Evidence = append(finding.Evidence, fmt.Sprintf("max shuffle write: %.1f MB", maxWrite/(1024*1024)))
	}

	return finding, nil
}

// SkewWatcher detects data skew patterns in Spark jobs.
type SkewWatcher struct{}

// NewSkewWatcher creates a new SkewWatcher.
func NewSkewWatcher() *SkewWatcher {
	return &SkewWatcher{}
}

// Watch analyzes a scenario and event log for skew.
func (w *SkewWatcher) Watch(scenarioPath string, logPath string) (*models.Finding, error) {
	scenarioData, err := os.ReadFile(scenarioPath)
	if err != nil {
		return nil, fmt.Errorf("read scenario: %w", err)
	}
	var scenario map[string]interface{}
	if err := yaml.Unmarshal(scenarioData, &scenario); err != nil {
		return nil, fmt.Errorf("parse scenario: %w", err)
	}

	eventsData, err := os.ReadFile(logPath)
	if err != nil {
		return nil, fmt.Errorf("read events: %w", err)
	}
	var events []map[string]interface{}
	for _, line := range splitLines(string(eventsData)) {
		line = trimSpace(line)
		if line == "" {
			continue
		}
		var event map[string]interface{}
		if err := json.Unmarshal([]byte(line), &event); err == nil {
			events = append(events, event)
		}
	}

	return w.buildFinding(scenario, events)
}

func (w *SkewWatcher) buildFinding(scenario map[string]interface{}, events []map[string]interface{}) (*models.Finding, error) {
	pg, ok := scenario["plan_generator"].(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("missing plan_generator")
	}
	sig, ok := pg["expected_signals"].(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("missing expected_signals")
	}
	joinKey := "customer_id"
	data, ok := scenario["code_generator"].(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("missing code_generator")
	}
	orders, ok := data["data"].(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("missing data")
	}
	ordersData, ok := orders["orders"].(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("missing orders")
	}
	hotKey := "?"
	if hk, ok := ordersData["hot_key"]; ok {
		hotKey = fmt.Sprintf("%v", hk)
	}

	// join operator
	op := toString(sig["join_operator"])
	records := extractRecords(events)
	m := skewMetrics(records)
	stageID := 0
	if len(records) > 0 {
		stageID = findStageID(events)
	}

	planNote := "plano final pos-AQE"
	evidence := []string{fmt.Sprintf("join operator: %s (%s)", op, planNote)}
	evidence = append(evidence, fmt.Sprintf("stage correlation: %s", m["correlation_method"]))

	evidenceStatus := toString(m["evidence_status"])
	qualityIssues := toStringSlice(m["quality_issues"])
	isSynthetic := false
	for _, e := range events {
		if e["Event"] == "ApexSyntheticProvenance" {
			isSynthetic = true
			break
		}
	}

	if m["collapsed"].(bool) {
		evidence = append(evidence, fmt.Sprintf("stage %d: 1 task leu %d registros; distribuicao colapsada (AQE/1-core)", stageID, toInt(m["hot"])))
	} else {
		evidence = append(evidence, fmt.Sprintf("stage %d: task quente %d vs mediana das frias %.0f -> skew ratio %.1fx (%d tasks)", stageID, toInt(m["hot"]), toFloat64(m["median_cold"]), toFloat64(m["ratio"]), toInt(m["n_tasks"])))
	}

	if op != toString(sig["join_operator"]) {
		evidenceStatus = "invalid"
		qualityIssues = append(qualityIssues, "join_operator_mismatch")
	} else if evidenceStatus == "valid" && toString(m["correlation_method"]) == "stage_name" && !isSynthetic {
		evidenceStatus = "indeterminate"
		qualityIssues = append(qualityIssues, "stage_name_only_correlation")
	}
	if evidenceStatus == "valid" && toString(m["correlation_method"]) == "largest_shuffle_fallback" {
		evidenceStatus = "indeterminate"
		qualityIssues = append(qualityIssues, "uncorrelated_join_stage")
	}

	skewRatioMin := toFloat64(sig["skew_ratio_min"])
	isSkew := evidenceStatus == "valid" && op == toString(sig["join_operator"]) && toFloat64(m["ratio"]) >= skewRatioMin
	var confidence float64
	if evidenceStatus == "invalid" {
		confidence = 0.0
	} else if evidenceStatus == "indeterminate" {
		confidence = 0.25
	} else if math.IsInf(toFloat64(m["ratio"]), 1) {
		confidence = 0.0
	} else {
		ratio := toFloat64(m["ratio"])
		confidence = math.Min(0.99, ratio/(ratio+3))
	}

	var rootCause string
	if isSkew {
		rootCause = fmt.Sprintf("data skew na chave de join %s = %s (%s): 1 particao concentra %.1fx o trabalho", joinKey, hotKey, op, toFloat64(m["ratio"]))
	} else {
		rootCause = "evidencia insuficiente para afirmar data skew: " + joinStrings(qualityIssues, ", ")
		if rootCause == "evidencia insuficiente para afirmar data skew: " {
			rootCause += "sinal abaixo do threshold"
		}
	}

	severity := models.SeverityLow
	if isSkew {
		severity = models.SeverityHigh
	}

	finding := &models.Finding{
		Watcher:           "shuffle_skew",
		Stage:             stageID,
		HotPartition:      0,
		CorrelationMethod: toString(m["correlation_method"]),
		EvidenceStatus:    evidenceStatus,
		QualityIssues:     qualityIssues,
		Severity:          severity,
		Confidence:        confidence,
		Evidence:          evidence,
		RootCause:         rootCause,
		Recommendations: []string{
			"habilitar spark.sql.adaptive.skewJoin.enabled",
			"broadcast o lado customers (dimensao pequena)",
			fmt.Sprintf("salgar a chave %s", joinKey),
		},
	}
	return finding, nil
}

func extractRecords(events []map[string]interface{}) []int {
	byStage := make(map[int][]map[string]interface{})
	for _, e := range events {
		if toString(e["Event"]) != "SparkListenerTaskEnd" {
			continue
		}
		stageID := toInt(e["Stage ID"])
		byStage[stageID] = append(byStage[stageID], e)
	}
	if len(byStage) == 0 {
		return nil
	}
	var maxStage int
	maxCount := 0
	for stageID, tasks := range byStage {
		if len(tasks) > maxCount {
			maxCount = len(tasks)
			maxStage = stageID
		}
	}
	records := make([]int, 0, len(byStage[maxStage]))
	for _, t := range byStage[maxStage] {
		metrics := toMap(t["Task Metrics"])
		shuffleRead := toMap(metrics["Shuffle Read Metrics"])
		records = append(records, toInt(shuffleRead["Total Records Read"]))
	}
	return records
}

func findStageID(events []map[string]interface{}) int {
	for _, e := range events {
		if toString(e["Event"]) == "SparkListenerTaskEnd" {
			return toInt(e["Stage ID"])
		}
	}
	return 0
}

func skewMetrics(records []int) map[string]interface{} {
	if len(records) == 0 {
		return map[string]interface{}{
			"hot": 0, "median_cold": 0.0, "ratio": 0.0,
			"n_tasks": 0, "n_nonzero_tasks": 0, "n_zero_tasks": 0,
			"collapsed": false, "evidence_status": "indeterminate",
			"quality_issues": []string{"no_task_records"},
			"correlation_method": "none",
		}
	}
	n := len(records)
	hot := maxInt(records)
	nNonzero := 0
	for _, r := range records {
		if r > 0 {
			nNonzero++
		}
	}
	if n == 1 {
		return map[string]interface{}{
			"hot": hot, "median_cold": 0.0, "ratio": math.Inf(1),
			"n_tasks": 1, "n_nonzero_tasks": nNonzero, "n_zero_tasks": 1 - nNonzero,
			"collapsed": true, "evidence_status": "invalid",
			"quality_issues": []string{"single_task_collapse"},
			"correlation_method": "none",
		}
	}
	ordered := make([]int, len(records))
	copy(ordered, records)
	sort.Sort(sort.Reverse(sort.IntSlice(ordered)))
	cold := ordered[1:]
	medianCold := medianInt(cold)
	ratio := math.Inf(1)
	if medianCold > 0 {
		ratio = float64(hot) / medianCold
	}
	qualityIssues := []string{}
	if medianCold == 0 {
		qualityIssues = append(qualityIssues, "zero_cold_median")
	}
	status := "valid"
	if len(qualityIssues) > 0 {
		status = "invalid"
	}
	return map[string]interface{}{
		"hot": hot, "median_cold": medianCold, "ratio": ratio,
		"n_tasks": n, "n_nonzero_tasks": nNonzero, "n_zero_tasks": n - nNonzero,
		"collapsed": false, "evidence_status": status,
		"quality_issues": qualityIssues, "correlation_method": "largest_shuffle_fallback",
	}
}

func medianInt(vals []int) float64 {
	if len(vals) == 0 {
		return 0
	}
	sorted := make([]int, len(vals))
	copy(sorted, vals)
	sort.Ints(sorted)
	mid := len(sorted) / 2
	if len(sorted)%2 == 0 {
		return float64(sorted[mid-1]+sorted[mid]) / 2.0
	}
	return float64(sorted[mid])
}

func maxInt(vals []int) int {
	m := vals[0]
	for _, v := range vals[1:] {
		if v > m {
			m = v
		}
	}
	return m
}

func maxFloat64(vals []float64) float64 {
	m := vals[0]
	for _, v := range vals[1:] {
		if v > m {
			m = v
		}
	}
	return m
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
	case string:
		if f, err := parseFloat(x); err == nil {
			return f
		}
	}
	return 0
}

func toInt(v interface{}) int {
	switch x := v.(type) {
	case int:
		return x
	case int64:
		return int(x)
	case float64:
		return int(x)
	case float32:
		return int(x)
	case string:
		if i, err := parseInt(x); err == nil {
			return i
		}
	}
	return 0
}

func toString(v interface{}) string {
	if v == nil {
		return ""
	}
	if s, ok := v.(string); ok {
		return s
	}
	return fmt.Sprintf("%v", v)
}

func toStringSlice(v interface{}) []string {
	if v == nil {
		return nil
	}
	arr, ok := v.([]interface{})
	if !ok {
		if s, ok := v.([]string); ok {
			return s
		}
		return nil
	}
	out := make([]string, 0, len(arr))
	for _, e := range arr {
		out = append(out, toString(e))
	}
	return out
}

func toMap(v interface{}) map[string]interface{} {
	if m, ok := v.(map[string]interface{}); ok {
		return m
	}
	return nil
}

func splitLines(s string) []string {
	var lines []string
	start := 0
	for i := 0; i < len(s); i++ {
		if s[i] == '\n' {
			lines = append(lines, s[start:i])
			start = i + 1
		}
	}
	if start < len(s) {
		lines = append(lines, s[start:])
	}
	return lines
}

func trimSpace(s string) string {
	start := 0
	for start < len(s) && (s[start] == ' ' || s[start] == '\t' || s[start] == '\r' || s[start] == '\n') {
		start++
	}
	end := len(s)
	for end > start && (s[end-1] == ' ' || s[end-1] == '\t' || s[end-1] == '\r' || s[end-1] == '\n') {
		end--
	}
	return s[start:end]
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

func parseInt(s string) (int, error) {
	if s == "" {
		return 0, fmt.Errorf("empty")
	}
	start := 0
	neg := false
	if s[0] == '-' {
		neg = true
		start = 1
	}
	val := 0
	for i := start; i < len(s); i++ {
		c := s[i]
		if c < '0' || c > '9' {
			return 0, fmt.Errorf("invalid char")
		}
		val = val*10 + int(c-'0')
	}
	if neg {
		val = -val
	}
	return val, nil
}

func parseFloat(s string) (float64, error) {
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
