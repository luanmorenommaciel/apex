package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"

	"github.com/apex/go-apex/internal/clickhouse"
	"github.com/apex/go-apex/internal/diagnostician"
	"github.com/apex/go-apex/internal/models"
	"github.com/apex/go-apex/internal/recommender"
)

func main() {
	var (
		appID   string
		output  string
	)
	flag.StringVar(&appID, "app-id", "", "Spark application ID (required)")
	flag.StringVar(&output, "output", "", "Output file for JSON result (optional)")
	flag.Parse()

	if appID == "" {
		fmt.Fprintln(os.Stderr, "Usage: analyze -app-id=<app_id> [-output=<file>]")
		os.Exit(1)
	}

	fmt.Printf("[CREI] Iniciando análise para app_id=%s\n", appID)

	cfg := clickhouse.DefaultConfig()
	d, err := diagnostician.NewDiagnostician(cfg)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to create diagnostician: %v\n", err)
		os.Exit(1)
	}
	defer d.Close()

	fmt.Println("[CREI] Stage 1: Diagnóstico...")
	anomalies, err := d.Diagnose(appID)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Diagnosis failed: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("[CREI] %d anomalia(s) detectada(s)\n", len(anomalies))

	if len(anomalies) == 0 {
		result := models.AnalysisResult{
			AppID:   appID,
			Status:  "HEALTHY",
			Message: "Nenhuma anomalia detectada. Job dentro dos parâmetros normais.",
		}
		printResult(result, output)
		os.Exit(0)
	}

	fmt.Println("[CREI] Stage 2: Recomendações...")
	rec := recommender.NewRecommender("runbooks")
	recommendations := rec.RecommendAll(anomalies)

	fmt.Println("[CREI] Stage 3: Revisão...")
	reviews := make([]map[string]interface{}, 0, len(anomalies))
	for i, anomaly := range anomalies {
		var recModel models.Recommendation
		if i < len(recommendations) {
			recModel = recommendations[i]
		}
		review := reviewAnomaly(anomaly, recModel)
		reviews = append(reviews, map[string]interface{}{
			"anomaly_type":            anomaly.AnomalyType,
			"recommendation_summary":  recModel.Summary,
			"review":                  review,
		})
	}

	finalStatus := "ACTIONABLE"
	for _, r := range reviews {
		rev := r["review"].(models.ReviewResult)
		if !rev.Passed {
			finalStatus = "NEEDS_ATTENTION"
			fmt.Println("[CREI] ALERTA: Uma ou mais recomendações não passaram na revisão automática.")
			break
		}
	}

	result := models.AnalysisResult{
		AppID:           appID,
		Status:          finalStatus,
		Anomalies:       anomalies,
		Recommendations: recommendations,
		Reviews:         reviews,
	}

	code := 0
	if finalStatus == "NEEDS_ATTENTION" {
		code = 1
	}
	printResult(result, output)
	os.Exit(code)
}

func reviewAnomaly(report models.AnomalyReport, rec models.Recommendation) models.ReviewResult {
	issues := []string{}
	passed := true

	if rec.RunbookID != "" && report.AnomalyType != "" && !startsWithIgnoreCase(rec.RunbookID, report.AnomalyType) {
		if report.AnomalyType != "GC_PRESSURE" && report.AnomalyType != "OOM" {
			issues = append(issues, "Runbook usado pode não ser o ideal para a anomalia.")
			passed = false
		}
	}
	if rec.Confidence < 0.4 {
		issues = append(issues, "Confiança da recomendação muito baixa (< 0.4).")
		passed = false
	}
	if report.Severity == "CRITICAL" && rec.CodeFix == "" {
		issues = append(issues, "Anomalia CRITICAL sem code_fix sugerido.")
		passed = false
	}
	if len(report.AffectedStages) > 0 && rec.CodeFix != "" {
		if containsIgnoreCase(rec.CodeFix, "TODO") || containsIgnoreCase(rec.CodeFix, "FIXME") {
			issues = append(issues, "code_fix contém placeholders (TODO/FIXME).")
			passed = false
		}
	}

	return models.ReviewResult{
		Passed:     passed,
		Issues:     issues,
		Confidence: rec.Confidence,
		Severity:   report.Severity,
	}
}

func startsWithIgnoreCase(s, prefix string) bool {
	if len(s) < len(prefix) {
		return false
	}
	for i := 0; i < len(prefix); i++ {
		c1 := s[i]
		c2 := prefix[i]
		if c1 >= 'A' && c1 <= 'Z' {
			c1 = c1 + ('a' - 'A')
		}
		if c2 >= 'A' && c2 <= 'Z' {
			c2 = c2 + ('a' - 'A')
		}
		if c1 != c2 {
			return false
		}
	}
	return true
}

func containsIgnoreCase(s, substr string) bool {
	if len(substr) > len(s) {
		return false
	}
	for i := 0; i <= len(s)-len(substr); i++ {
		match := true
		for j := 0; j < len(substr); j++ {
			c1 := s[i+j]
			c2 := substr[j]
			if c1 >= 'A' && c1 <= 'Z' {
				c1 = c1 + ('a' - 'A')
			}
			if c2 >= 'A' && c2 <= 'Z' {
				c2 = c2 + ('a' - 'A')
			}
			if c1 != c2 {
				match = false
				break
			}
		}
		if match {
			return true
		}
	}
	return false
}

func printResult(result models.AnalysisResult, output string) {
	data, err := json.MarshalIndent(result, "", "  ")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to marshal output: %v\n", err)
		os.Exit(1)
	}
	if output != "" {
		if err := os.WriteFile(output, data, 0644); err != nil {
			fmt.Fprintf(os.Stderr, "Failed to write output: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("[CREI] Resultado salvo em: %s\n", output)
	} else {
		fmt.Println(string(data))
	}
}
