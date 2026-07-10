// Package validator provides evidence validation before diagnosis.
// This component must be called BEFORE the Watcher.
package validator

import (
	"fmt"
	"math"
	"sort"

	"github.com/apex/go-apex/internal/models"
)

// EvidenceValidator applies structural quality rules before diagnosis.
type EvidenceValidator struct {
	bundle *models.EvidenceBundle
	issues []string
}

// NewEvidenceValidator creates a new EvidenceValidator.
func NewEvidenceValidator(bundle *models.EvidenceBundle) *EvidenceValidator {
	return &EvidenceValidator{bundle: bundle}
}

// Validate executes the full validation pipeline.
func (v *EvidenceValidator) Validate() *models.EvidenceValidationResult {
	v.issues = nil

	// 1. Provenance
	provHash := v.validateProvenance()
	if hasIssue(v.issues, "provenance_mismatch") {
		return v.result("invalid", provHash, nil, nil, nil, nil)
	}

	// 2. Schema
	v.validateSchema()

	// 3. Correlation / operator
	op, usedFinal := joinOperator(v.bundle.Events)
	_ = usedFinal
	expectedOp := v.expectedJoinOperator()
	selected := hottestReduceStageDetails(v.bundle.Events, op)
	stageID := selected.StageID
	records := selected.Records
	correlationMethod := selected.CorrelationMethod

	v.validateOperator(op, expectedOp)
	v.validateCorrelationMethod(correlationMethod, v.isSynthetic())

	// 4. Distribution
	metrics := v.validateDistribution(records)

	// 5. Structural
	v.validateStructural(records)

	if len(v.issues) > 0 {
		if v.isIndeterminateOnly() {
			return v.result("indeterminate", provHash, &correlationMethod, &stageID, records, metrics)
		}
		return v.result("invalid", provHash, &correlationMethod, &stageID, records, metrics)
	}

	return v.result("valid", provHash, &correlationMethod, &stageID, records, metrics)
}

func (v *EvidenceValidator) validateProvenance() string {
	for _, e := range v.bundle.Events {
		if e["Event"] == "ApexSyntheticProvenance" {
			if hash, ok := e["scenario_hash"].(string); ok {
				return hash
			}
		}
	}
	return ""
}

func (v *EvidenceValidator) validateSchema() {
	var hasTaskEnd, hasSQLExec bool
	for _, e := range v.bundle.Events {
		ev := toString(e["Event"])
		if ev == "SparkListenerTaskEnd" {
			hasTaskEnd = true
		}
		if len(ev) >= len("SQLExecutionStart") && ev[len(ev)-len("SQLExecutionStart"):] == "SQLExecutionStart" {
			hasSQLExec = true
		}
	}
	if !hasTaskEnd {
		v.issues = append(v.issues, "missing_task_end_events")
	}
	if !hasSQLExec {
		v.issues = append(v.issues, "missing_sql_execution_events")
	}
}

func (v *EvidenceValidator) validateOperator(detected, expected string) {
	if expected == "" {
		return
	}
	if detected != expected {
		v.issues = append(v.issues, "join_operator_mismatch")
	}
}

func (v *EvidenceValidator) validateCorrelationMethod(method string, isSynthetic bool) {
	if method == "largest_shuffle_fallback" {
		v.issues = append(v.issues, "uncorrelated_join_stage")
	} else if method == "stage_name" && !isSynthetic {
		v.issues = append(v.issues, "stage_name_only_correlation")
	} else if method == "none" {
		v.issues = append(v.issues, "no_stage_correlation")
	}
}

func (v *EvidenceValidator) validateDistribution(records []int) map[string]interface{} {
	m := skewMetrics(records)
	if toBool(m["collapsed"]) {
		v.issues = append(v.issues, "single_task_collapse")
	}
	if hasIssue(toStringSlice(m["quality_issues"]), "zero_cold_median") {
		v.issues = append(v.issues, "zero_cold_median")
	}

	vc, ok := v.bundle.Scenario["validation_criteria"].(map[string]interface{})
	if !ok {
		return m
	}
	target, ok := vc["target_stage"].(map[string]interface{})
	if !ok {
		return m
	}
	if minTasks := toInt(target["min_tasks"]); minTasks > 0 && toInt(m["n_tasks"]) < minTasks {
		v.issues = append(v.issues, fmt.Sprintf("insufficient_tasks:%d<%d", toInt(m["n_tasks"]), minTasks))
	}
	if minNonzero := toInt(target["min_nonzero_tasks"]); minNonzero > 0 && toInt(m["n_nonzero_tasks"]) < minNonzero {
		v.issues = append(v.issues, fmt.Sprintf("insufficient_nonzero_tasks:%d<%d", toInt(m["n_nonzero_tasks"]), minNonzero))
	}
	return m
}

func (v *EvidenceValidator) validateStructural(records []int) {
	vc, ok := v.bundle.Scenario["validation_criteria"].(map[string]interface{})
	if !ok {
		return
	}
	scope, ok := vc["scope"].(map[string]interface{})
	if !ok {
		return
	}
	if requireSingle, ok := scope["require_single_application"].(bool); ok && requireSingle {
		appIDs := make(map[string]struct{})
		for _, e := range v.bundle.Events {
			if id := toString(e["app_id"]); id != "" {
				appIDs[id] = struct{}{}
			} else if id := toString(e["App ID"]); id != "" {
				appIDs[id] = struct{}{}
			}
		}
		if len(appIDs) > 1 {
			v.issues = append(v.issues, "multiple_applications")
		}
	}
}

func (v *EvidenceValidator) expectedJoinOperator() string {
	vc, ok := v.bundle.Scenario["validation_criteria"].(map[string]interface{})
	if !ok {
		return ""
	}
	plan, ok := vc["plan"].(map[string]interface{})
	if ok {
		if op := toString(plan["expected_join_operator"]); op != "" {
			return op
		}
	}
	pg, ok := v.bundle.Scenario["plan_generator"].(map[string]interface{})
	if !ok {
		return ""
	}
	sig, ok := pg["expected_signals"].(map[string]interface{})
	if !ok {
		return ""
	}
	return toString(sig["join_operator"])
}

func (v *EvidenceValidator) isSynthetic() bool {
	for _, e := range v.bundle.Events {
		if e["Event"] == "ApexSyntheticProvenance" {
			return true
		}
	}
	return false
}

func (v *EvidenceValidator) isIndeterminateOnly() bool {
	if len(v.issues) == 0 {
		return false
	}
	indeterminate := map[string]bool{
		"stage_name_only_correlation": true,
		"uncorrelated_join_stage":     true,
	}
	for _, i := range v.issues {
		if !indeterminate[i] {
			return false
		}
	}
	return true
}

func (v *EvidenceValidator) result(status, provHash string, correlationMethod *string, stageID *int, records []int, metrics map[string]interface{}) *models.EvidenceValidationResult {
	return &models.EvidenceValidationResult{
		Status:            status,
		QualityIssues:     append([]string(nil), v.issues...),
		CorrelationMethod: derefString(correlationMethod),
		StageID:           stageID,
		Records:           records,
		Metrics:           metrics,
		ProvenanceHash:    provHash,
	}
}

func derefString(s *string) string {
	if s == nil {
		return ""
	}
	return *s
}

func hasIssue(issues []string, target string) bool {
	for _, i := range issues {
		if i == target {
			return true
		}
	}
	return false
}

func joinOperator(events []map[string]interface{}) (string, bool) {
	finalByExec := make(map[interface{}]string)
	initialByExec := make(map[interface{}]string)
	joinOps := []string{"BroadcastHashJoin", "SortMergeJoin", "ShuffledHashJoin", "BroadcastNestedLoopJoin"}

	for _, e := range events {
		ev := toString(e["Event"])
		execID := e["executionId"]
		if execID == nil {
			execID = e["sqlExecutionId"]
		}
		plan := toString(e["physicalPlanDescription"])
		if plan == "" {
			continue
		}
		if len(ev) > 0 && ev[len(ev)-len("SparkListenerSQLAdaptiveExecutionUpdate"):] == "SparkListenerSQLAdaptiveExecutionUpdate" {
			finalByExec[execID] = plan
		} else if len(ev) > 0 && ev[len(ev)-len("SparkListenerSQLExecutionStart"):] == "SparkListenerSQLExecutionStart" {
			initialByExec[execID] = plan
		}
	}

	for execID, plan := range finalByExec {
		_ = execID
		for _, op := range joinOps {
			if stringsContains(plan, op) {
				return op, true
			}
		}
	}
	for execID, plan := range initialByExec {
		_ = execID
		for _, op := range joinOps {
			if stringsContains(plan, op) {
				return op, false
			}
		}
	}
	return "", len(finalByExec) > 0
}

func hottestReduceStageDetails(events []map[string]interface{}, joinOp string) models.HottestReduceStageDetails {
	by := shuffleTasksByStage(events)
	if len(by) == 0 {
		return models.HottestReduceStageDetails{
			StageID:           -1,
			Tasks:             nil,
			Records:           nil,
			CorrelationMethod: "none",
		}
	}

	if joinOp != "" {
		operatorAccumulators := operatorAccumulatorIDs(events, joinOp)
		if len(operatorAccumulators) > 0 {
			matches := make(map[int]int)
			for stageID, tasks := range by {
				matched := 0
				for _, t := range tasks {
					if taskAccIDs, ok := t["accumulator_ids"].([]int); ok {
						for _, id := range taskAccIDs {
							if containsInt(operatorAccumulators, id) {
								matched++
								break
							}
						}
					}
				}
				if matched > 0 {
					matches[stageID] = matched
				}
			}
			if len(matches) > 0 {
				stageID := maxByMatchesAndRecords(matches, by)
				return buildDetails(stageID, by, "operator_accumulator")
			}
		}

		names := stageNames(events)
		var joinish []int
		for stageID := range by {
			if stringsContains(names[stageID], joinOp) {
				joinish = append(joinish, stageID)
			}
		}
		if len(joinish) > 0 {
			stageID := maxByRecords(joinish, by)
			return buildDetails(stageID, by, "stage_name")
		}
	}

	stageID := maxByRecordsMap(by)
	return buildDetails(stageID, by, "largest_shuffle_fallback")
}

func buildDetails(stageID int, by map[int][]map[string]interface{}, method string) models.HottestReduceStageDetails {
	tasks := by[stageID]
	records := make([]int, 0, len(tasks))
	for _, t := range tasks {
		records = append(records, toInt(t["records"]))
	}
	return models.HottestReduceStageDetails{
		StageID:           stageID,
		Tasks:             tasks,
		Records:           records,
		CorrelationMethod: method,
	}
}

func shuffleTasksByStage(events []map[string]interface{}) map[int][]map[string]interface{} {
	byStageAttempt := make(map[int]map[int][]map[string]interface{})
	for _, e := range events {
		if toString(e["Event"]) != "SparkListenerTaskEnd" {
			continue
		}
		stageID := toInt(e["Stage ID"])
		if stageID == 0 && e["Stage ID"] == nil {
			continue
		}
		stageAttempt := toInt(e["Stage Attempt ID"])
		if byStageAttempt[stageID] == nil {
			byStageAttempt[stageID] = make(map[int][]map[string]interface{})
		}
		byStageAttempt[stageID][stageAttempt] = append(byStageAttempt[stageID][stageAttempt], e)
	}

	result := make(map[int][]map[string]interface{})
	for stageID, attempts := range byStageAttempt {
		maxAttempt := maxKey(attempts)
		byPartition := make(map[int][]map[string]interface{})
		for _, event := range attempts[maxAttempt] {
			partition := taskPartition(event)
			byPartition[partition] = append(byPartition[partition], event)
		}

		var effective []map[string]interface{}
		for _, candidates := range byPartition {
			event := effectiveTask(candidates)
			if event == nil {
				continue
			}
			taskInfo := toMap(event["Task Info"])
			shuffleRead := toMap(event["Task Metrics"])
			if len(shuffleRead) > 0 {
				shuffleRead = toMap(shuffleRead["Shuffle Read Metrics"])
			}
			effective = append(effective, map[string]interface{}{
				"stage_id":        stageID,
				"stage_attempt":   maxAttempt,
				"partition":       taskPartition(event),
				"task_attempt":    toInt(taskInfo["Attempt"]),
				"task_id":         toInt(taskInfo["Task ID"]),
				"finish_time":     taskInfo["Finish Time"],
				"records":         toInt(shuffleRead["Total Records Read"]),
				"task_type":       event["Task Type"],
				"accumulator_ids": taskAccumulatorIDs(event),
			})
		}
		sortByPartition(effective)
		result[stageID] = effective
	}
	return result
}

func taskPartition(event map[string]interface{}) int {
	taskInfo := toMap(event["Task Info"])
	if idx := toInt(taskInfo["Index"]); idx != 0 || taskInfo["Index"] != nil {
		return idx
	}
	if idx := toInt(taskInfo["Partition ID"]); idx != 0 || taskInfo["Partition ID"] != nil {
		return idx
	}
	return toInt(taskInfo["Task ID"])
}

func taskAccumulatorIDs(event map[string]interface{}) []int {
	taskInfo := toMap(event["Task Info"])
	accumulables, ok := taskInfo["Accumulables"].([]interface{})
	if !ok {
		return nil
	}
	var ids []int
	for _, acc := range accumulables {
		accMap := toMap(acc)
		if id := toInt(accMap["ID"]); id != 0 || accMap["ID"] != nil {
			ids = append(ids, id)
		} else if id := toInt(accMap["id"]); id != 0 || accMap["id"] != nil {
			ids = append(ids, id)
		}
	}
	return ids
}

func effectiveTask(candidates []map[string]interface{}) map[string]interface{} {
	var successful []map[string]interface{}
	for _, event := range candidates {
		taskInfo := toMap(event["Task Info"])
		if failed, ok := taskInfo["Failed"].(bool); ok && failed {
			continue
		}
		reason := toMap(event["Task End Reason"])
		if reason["Reason"] == nil || toString(reason["Reason"]) == "Success" {
			successful = append(successful, event)
		}
	}
	if len(successful) == 0 {
		return nil
	}
	var best = successful[0]
	for _, event := range successful[1:] {
		if taskBetter(event, best) {
			best = event
		}
	}
	return best
}

func taskBetter(a, b map[string]interface{}) bool {
	ai := toMap(a["Task Info"])
	bi := toMap(b["Task Info"])
	af := toFloat64(ai["Finish Time"])
	bf := toFloat64(bi["Finish Time"])
	if af != bf {
		return af < bf
	}
	if aa := toInt(ai["Attempt"]); aa != toInt(bi["Attempt"]) {
		return aa < toInt(bi["Attempt"])
	}
	return toInt(ai["Task ID"]) < toInt(bi["Task ID"])
}

func stageNames(events []map[string]interface{}) map[int]string {
	names := make(map[int]string)
	for _, e := range events {
		ev := toString(e["Event"])
		if len(ev) > 0 && ev[len(ev)-len("StageSubmitted"):] == "StageSubmitted" {
			si := toMap(e["Stage Info"])
			names[toInt(si["Stage ID"])] = toString(si["Stage Name"])
		}
	}
	return names
}

func operatorAccumulatorIDs(events []map[string]interface{}, joinOp string) []int {
	ids := make(map[int]struct{})
	for _, e := range events {
		visitPlanInfo(e["sparkPlanInfo"], joinOp, ids)
	}
	out := make([]int, 0, len(ids))
	for id := range ids {
		out = append(out, id)
	}
	return out
}

func visitPlanInfo(node interface{}, joinOp string, ids map[int]struct{}) {
	m, ok := node.(map[string]interface{})
	if !ok {
		return
	}
	if stringsContains(toString(m["nodeName"]), joinOp) {
		metrics, ok := m["metrics"].([]interface{})
		if ok {
			for _, metric := range metrics {
				metricMap := toMap(metric)
				if id := toInt(metricMap["accumulatorId"]); id != 0 || metricMap["accumulatorId"] != nil {
					ids[id] = struct{}{}
				} else if id := toInt(metricMap["accumulatorID"]); id != 0 || metricMap["accumulatorID"] != nil {
					ids[id] = struct{}{}
				}
			}
		}
	}
	children, ok := m["children"].([]interface{})
	if ok {
		for _, child := range children {
			visitPlanInfo(child, joinOp, ids)
		}
	}
}

func skewMetrics(records []int) map[string]interface{} {
	if len(records) == 0 {
		return map[string]interface{}{
			"hot":             0,
			"median_cold":     0.0,
			"ratio":           0.0,
			"n_tasks":         0,
			"n_nonzero_tasks": 0,
			"n_zero_tasks":    0,
			"collapsed":       false,
			"evidence_status": "indeterminate",
			"quality_issues":  []string{"no_task_records"},
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
	nZero := n - nNonzero
	if n == 1 {
		return map[string]interface{}{
			"hot":             hot,
			"median_cold":     0.0,
			"ratio":           math.Inf(1),
			"n_tasks":         1,
			"n_nonzero_tasks": nNonzero,
			"n_zero_tasks":    nZero,
			"collapsed":       true,
			"evidence_status": "invalid",
			"quality_issues":  []string{"single_task_collapse"},
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
		"hot":             hot,
		"median_cold":     medianCold,
		"ratio":           ratio,
		"n_tasks":         n,
		"n_nonzero_tasks": nNonzero,
		"n_zero_tasks":    nZero,
		"collapsed":       false,
		"evidence_status": status,
		"quality_issues":  qualityIssues,
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

func maxKey(m map[int][]map[string]interface{}) int {
	maxK := -1
	for k := range m {
		if k > maxK {
			maxK = k
		}
	}
	return maxK
}

func maxByMatchesAndRecords(matches map[int]int, by map[int][]map[string]interface{}) int {
	type pair struct {
		stageID int
		matches int
		records int
	}
	var pairs []pair
	for stageID, matchCount := range matches {
		totalRecords := 0
		for _, t := range by[stageID] {
			totalRecords += toInt(t["records"])
		}
		pairs = append(pairs, pair{stageID: stageID, matches: matchCount, records: totalRecords})
	}
	sort.Slice(pairs, func(i, j int) bool {
		if pairs[i].matches != pairs[j].matches {
			return pairs[i].matches > pairs[j].matches
		}
		return pairs[i].records > pairs[j].records
	})
	return pairs[0].stageID
}

func maxByRecords(stageIDs []int, by map[int][]map[string]interface{}) int {
	type pair struct {
		stageID int
		records int
	}
	var pairs []pair
	for _, stageID := range stageIDs {
		total := 0
		for _, t := range by[stageID] {
			total += toInt(t["records"])
		}
		pairs = append(pairs, pair{stageID: stageID, records: total})
	}
	sort.Slice(pairs, func(i, j int) bool {
		return pairs[i].records > pairs[j].records
	})
	return pairs[0].stageID
}

func maxByRecordsMap(by map[int][]map[string]interface{}) int {
	type pair struct {
		stageID int
		records int
	}
	var pairs []pair
	for stageID, tasks := range by {
		total := 0
		for _, t := range tasks {
			total += toInt(t["records"])
		}
		pairs = append(pairs, pair{stageID: stageID, records: total})
	}
	sort.Slice(pairs, func(i, j int) bool {
		return pairs[i].records > pairs[j].records
	})
	return pairs[0].stageID
}

func sortByPartition(tasks []map[string]interface{}) {
	sort.Slice(tasks, func(i, j int) bool {
		return toInt(tasks[i]["partition"]) < toInt(tasks[j]["partition"])
	})
}

func containsInt(vals []int, target int) bool {
	for _, v := range vals {
		if v == target {
			return true
		}
	}
	return false
}

func stringsContains(s, substr string) bool {
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

func toBool(v interface{}) bool {
	if v == nil {
		return false
	}
	if b, ok := v.(bool); ok {
		return b
	}
	if s, ok := v.(string); ok {
		return s == "true" || s == "True" || s == "1"
	}
	if i, ok := v.(int); ok {
		return i != 0
	}
	return false
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

func toString(v interface{}) string {
	if v == nil {
		return ""
	}
	if s, ok := v.(string); ok {
		return s
	}
	if s, ok := v.(fmt.Stringer); ok {
		return s.String()
	}
	return fmt.Sprintf("%v", v)
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
		if i, err := parseInt(x); err == nil {
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
		if f, err := parseFloat(x); err == nil {
			return f
		}
	}
	return 0
}

func toMap(v interface{}) map[string]interface{} {
	if v == nil {
		return nil
	}
	if m, ok := v.(map[string]interface{}); ok {
		return m
	}
	return nil
}

func parseInt(s string) (int, error) {
	if s == "" {
		return 0, fmt.Errorf("empty string")
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
		return 0, fmt.Errorf("empty string")
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
