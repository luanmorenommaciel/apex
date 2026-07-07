package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/apex/go-apex/internal/clickhouse"
	"github.com/apex/go-apex/internal/diagnostician"
	"github.com/apex/go-apex/internal/recommender"
)

const creiVersion = "0.1.0-alpha"

type analyzeRequest struct {
	AppID       string                 `json:"app_id"`
	JobData     map[string]interface{} `json:"job_data,omitempty"`
	RequestType string                 `json:"request_type,omitempty"`
}

type analyzeResponse struct {
	AppID       string                 `json:"app_id"`
	Diagnosis   string                 `json:"diagnosis"`
	RootCause   []string               `json:"root_cause"`
	Recommendations []string           `json:"recommendations"`
	Runbook     map[string]interface{} `json:"runbook,omitempty"`
	Confidence  float64                `json:"confidence"`
	JobDataSummary map[string]interface{} `json:"job_data_summary,omitempty"`
}

func main() {
	port := os.Getenv("CREI_PORT")
	if port == "" {
		port = "8000"
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/health", healthHandler)
	mux.HandleFunc("/analyze", analyzeHandler)
	mux.HandleFunc("/version", versionHandler)

	addr := ":" + port
	log.Printf("CREI Server starting on %s", addr)
	if err := http.ListenAndServe(addr, mux); err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	status := map[string]interface{}{
		"status":  "healthy",
		"version": creiVersion,
	}
	respondJSON(w, status)
}

func versionHandler(w http.ResponseWriter, r *http.Request) {
	respondJSON(w, map[string]string{"version": creiVersion})
}

func analyzeHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req analyzeRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid JSON: "+err.Error(), http.StatusBadRequest)
		return
	}

	if req.AppID == "" {
		http.Error(w, "app_id is required", http.StatusBadRequest)
		return
	}

	cfg := clickhouse.DefaultConfig()
	d, err := diagnostician.NewDiagnostician(cfg)
	if err != nil {
		http.Error(w, "Diagnostician error: "+err.Error(), http.StatusInternalServerError)
		return
	}
	defer d.Close()

	reports, err := d.Diagnose(req.AppID)
	if err != nil {
		http.Error(w, "Diagnosis failed: "+err.Error(), http.StatusInternalServerError)
		return
	}

	rec := recommender.NewRecommender("runbooks")
	recommendations := rec.RecommendAll(reports)

	diagnosisParts := []string{}
	rootCause := []string{}
	recommendationStrs := []string{}
	for _, rep := range reports {
		diagnosisParts = append(diagnosisParts, rep.Description)
		rootCause = append(rootCause, rep.AnomalyType)
	}
	for _, rec := range recommendations {
		recommendationStrs = append(recommendationStrs, rec.Summary)
	}
	if len(diagnosisParts) == 0 {
		diagnosisParts = append(diagnosisParts, "Nenhuma anomalia detectada.")
		rootCause = append(rootCause, "no_anomaly")
		recommendationStrs = append(recommendationStrs, "Monitorar métricas de baseline")
	}

	resp := analyzeResponse{
		AppID:       req.AppID,
		Diagnosis:   joinStrings(diagnosisParts, " | "),
		RootCause:   uniqueStrings(rootCause),
		Recommendations: uniqueStrings(recommendationStrs),
		Confidence:  0.85,
		JobDataSummary: map[string]interface{}{
			"anomalies_count": len(reports),
			"recommendations_count": len(recommendations),
		},
	}

	respondJSON(w, resp)
}

func respondJSON(w http.ResponseWriter, v interface{}) {
	w.Header().Set("Content-Type", "application/json")
	data, err := json.MarshalIndent(v, "", "  ")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	w.Write(data)
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
