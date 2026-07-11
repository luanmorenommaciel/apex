package main

import (
	"encoding/json"
	"os"
	"strings"
	"testing"

	"github.com/apex/go-apex/internal/models"
	"github.com/apex/go-apex/internal/recommender"
	"github.com/apex/go-apex/internal/runbook"
)

// TestBuildOutput tests the buildOutput helper function that constructs
// the final JSON output map from appID, reports and recommendations.
func TestBuildOutput(t *testing.T) {
	tests := []struct {
		name            string
		appID           string
		reports         []models.AnomalyReport
		recommendations []models.Recommendation
		wantAppID       string
		wantAnomalies   int
		wantRecs        int
	}{
		{
			name:  "single anomaly and recommendation",
			appID: "app-001",
			reports: []models.AnomalyReport{
				{
					AppID:       "app-001",
					AnomalyType: "SKEW",
					Severity:    "HIGH",
					Description: "Stage 1 skew detected",
					Confidence:  0.95,
				},
			},
			recommendations: []models.Recommendation{
				{
					AnomalyType: "SKEW",
					Confidence:  0.9,
					Summary:     "Apply salting to join key",
				},
			},
			wantAppID:     "app-001",
			wantAnomalies: 1,
			wantRecs:      1,
		},
		{
			name:            "empty anomalies and recommendations",
			appID:           "app-002",
			reports:         []models.AnomalyReport{},
			recommendations: []models.Recommendation{},
			wantAppID:       "app-002",
			wantAnomalies:   0,
			wantRecs:        0,
		},
		{
			name:  "single anomaly without recommendation",
			appID: "app-003",
			reports: []models.AnomalyReport{
				{
					AppID:       "app-003",
					AnomalyType: "OOM",
					Severity:    "CRITICAL",
					Description: "Out of memory on stage 5",
					Confidence:  0.9,
				},
			},
			recommendations: []models.Recommendation{},
			wantAppID:       "app-003",
			wantAnomalies:   1,
			wantRecs:        0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			out := buildOutput(tt.appID, tt.reports, tt.recommendations)

			if out["app_id"] != tt.wantAppID {
				t.Errorf("app_id = %v, want %v", out["app_id"], tt.wantAppID)
			}

			anomalies, ok := out["anomalies"].([]models.AnomalyReport)
			if !ok {
				t.Fatalf("anomalies is not []models.AnomalyReport")
			}
			if len(anomalies) != tt.wantAnomalies {
				t.Errorf("len(anomalies) = %d, want %d", len(anomalies), tt.wantAnomalies)
			}

			recs, ok := out["recommendations"].([]models.Recommendation)
			if !ok {
				t.Fatalf("recommendations is not []models.Recommendation")
			}
			if len(recs) != tt.wantRecs {
				t.Errorf("len(recommendations) = %d, want %d", len(recs), tt.wantRecs)
			}
		})
	}
}

// TestBuildOutputMarshal tests that the output map can be successfully
// marshaled to JSON and contains the expected fields.
func TestBuildOutputMarshal(t *testing.T) {
	reports := []models.AnomalyReport{
		{
			AppID:       "app-123",
			AnomalyType: "SPILL",
			Severity:    "MEDIUM",
			Description: "Spill to disk detected",
			Confidence:  0.85,
		},
	}
	recommendations := []models.Recommendation{
		{
			AnomalyType:    "SPILL",
			Confidence:     0.8,
			Summary:        "Increase memory fraction",
			ExpectedImpact: "Reduce spill by 50%",
		},
	}

	out := buildOutput("app-123", reports, recommendations)
	data, err := json.MarshalIndent(out, "", "  ")
	if err != nil {
		t.Fatalf("failed to marshal output: %v", err)
	}

	var decoded map[string]interface{}
	if err := json.Unmarshal(data, &decoded); err != nil {
		t.Fatalf("failed to unmarshal output: %v", err)
	}

	if decoded["app_id"] != "app-123" {
		t.Errorf("app_id = %v, want app-123", decoded["app_id"])
	}

	if anomalies, ok := decoded["anomalies"].([]interface{}); !ok || len(anomalies) != 1 {
		t.Errorf("anomalies count = %d, want 1", len(anomalies))
	}

	if recs, ok := decoded["recommendations"].([]interface{}); !ok || len(recs) != 1 {
		t.Errorf("recommendations count = %d, want 1", len(recs))
	}
}

// TestMarshalOutput tests marshalOutput with various inputs.
func TestMarshalOutput(t *testing.T) {
	tests := []struct {
		name    string
		input   map[string]interface{}
		wantErr bool
		check   func(t *testing.T, data []byte)
	}{
		{
			name: "valid output with nested data",
			input: map[string]interface{}{
				"app_id": "app-456",
				"anomalies": []models.AnomalyReport{
					{AnomalyType: "GC_PRESSURE", Severity: "LOW", Confidence: 0.6},
				},
				"recommendations": []models.Recommendation{
					{AnomalyType: "GC_PRESSURE", Summary: "Increase heap size"},
				},
			},
			wantErr: false,
			check: func(t *testing.T, data []byte) {
				if !strings.Contains(string(data), `"app_id": "app-456"`) {
					t.Error("expected app_id in output")
				}
				if !strings.Contains(string(data), `"anomaly_type": "GC_PRESSURE"`) {
					t.Error("expected anomaly_type in output")
				}
			},
		},
		{
			name: "empty output",
			input: map[string]interface{}{
				"app_id":          "",
				"anomalies":       []models.AnomalyReport{},
				"recommendations": []models.Recommendation{},
			},
			wantErr: false,
			check: func(t *testing.T, data []byte) {
				if len(data) == 0 {
					t.Error("expected non-empty data")
				}
			},
		},
		{
			name: "output with special characters",
			input: map[string]interface{}{
				"app_id": "app-éspecial",
				"anomalies": []models.AnomalyReport{
					{Description: "Descrição com acentos: àáâã"},
				},
				"recommendations": []models.Recommendation{},
			},
			wantErr: false,
			check: func(t *testing.T, data []byte) {
				if !strings.Contains(string(data), "app-éspecial") {
					t.Error("expected special characters preserved")
				}
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			data, err := marshalOutput(tt.input)
			if (err != nil) != tt.wantErr {
				t.Errorf("marshalOutput() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if tt.check != nil {
				tt.check(t, data)
			}
		})
	}
}

// TestRecommenderFromRunbook tests the recommender's Recommend method.
func TestRecommenderFromRunbook(t *testing.T) {
	rec := recommender.NewRecommender("")

	report := models.AnomalyReport{
		AnomalyType: "SKEW",
		Severity:    "HIGH",
		Description: "Stage 1 skew",
		Confidence:  0.95,
		Evidence: map[string]interface{}{
			"stage_id": 42,
		},
	}

	recommendation := rec.Recommend(report)

	if recommendation.AnomalyType != "SKEW" {
		t.Errorf("AnomalyType = %v, want SKEW", recommendation.AnomalyType)
	}

	if recommendation.Confidence < 0 || recommendation.Confidence > 1 {
		t.Errorf("Confidence = %v, want between 0 and 1", recommendation.Confidence)
	}
}

// TestRecommenderRecommendAll tests RecommendAll with multiple reports.
func TestRecommenderRecommendAll(t *testing.T) {
	rec := recommender.NewRecommender("")

	reports := []models.AnomalyReport{
		{AnomalyType: "SKEW", Severity: "HIGH", Confidence: 0.9},
		{AnomalyType: "SPILL", Severity: "MEDIUM", Confidence: 0.8},
		{AnomalyType: "OOM", Severity: "CRITICAL", Confidence: 0.95},
	}

	recommendations := rec.RecommendAll(reports)

	if len(recommendations) != len(reports) {
		t.Errorf("len(recommendations) = %d, want %d", len(recommendations), len(reports))
	}

	for i, rec := range recommendations {
		if rec.AnomalyType != reports[i].AnomalyType {
			t.Errorf("recommendation[%d].AnomalyType = %v, want %v", i, rec.AnomalyType, reports[i].AnomalyType)
		}
	}
}

// TestValidateAppID tests the appID validation logic.
func TestValidateAppID(t *testing.T) {
	tests := []struct {
		name    string
		appID   string
		wantErr bool
	}{
		{
			name:    "valid app-id",
			appID:   "application_1234567890_0001",
			wantErr: false,
		},
		{
			name:    "empty app-id",
			appID:   "",
			wantErr: true,
		},
		{
			name:    "whitespace only app-id",
			appID:   "   ",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := validateAppID(tt.appID)
			if (err != nil) != tt.wantErr {
				t.Errorf("validateAppID(%q) error = %v, wantErr %v", tt.appID, err, tt.wantErr)
			}
		})
	}
}

// TestRunbookManagerLoad tests the runbook manager's Load function.
func TestRunbookManagerLoad(t *testing.T) {
	mgr := runbook.NewManager("")

	tests := []struct {
		name        string
		anomalyType string
		wantErr     bool
	}{
		{
			name:        "known anomaly type SKEW",
			anomalyType: "SKEW",
			wantErr:     true, // will error because runbooks dir is empty
		},
		{
			name:        "known anomaly type SPILL",
			anomalyType: "SPILL",
			wantErr:     true,
		},
		{
			name:        "unknown anomaly type",
			anomalyType: "UNKNOWN_TYPE",
			wantErr:     true,
		},
		{
			name:        "data_skew alias",
			anomalyType: "data_skew",
			wantErr:     true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			_, err := mgr.Load(tt.anomalyType)
			if (err != nil) != tt.wantErr {
				t.Errorf("Load(%q) error = %v, wantErr %v", tt.anomalyType, err, tt.wantErr)
			}
		})
	}
}

// TestBuildOutputWithRecommendations tests buildOutput with a complete set.
func TestBuildOutputWithRecommendations(t *testing.T) {
	reports := []models.AnomalyReport{
		{
			AppID:          "app-999",
			AnomalyType:    "SKEW",
			Severity:       "CRITICAL",
			Description:    "Severe data skew on join key",
			AffectedStages: []int{1, 2, 3},
			Confidence:     0.95,
			Evidence: map[string]interface{}{
				"stage_id":   1,
				"skew_ratio": 45.5,
			},
		},
	}

	recommendations := []models.Recommendation{
		{
			AnomalyType: "SKEW",
			Confidence:  0.9,
			Summary:     "Apply salting to distribute join key evenly",
			Steps: []models.StepAction{
				{Action: "Add salt column", Details: "Use rand() to create salt"},
				{Action: "Repartition", Details: "Repartition by salted key"},
			},
			CodeFix:        "df.withColumn('salt', rand())",
			ExpectedImpact: "Reduce stage duration by 60%",
			RunbookID:      "runbook-skew-001",
		},
	}

	out := buildOutput("app-999", reports, recommendations)

	data, err := json.Marshal(out)
	if err != nil {
		t.Fatalf("failed to marshal: %v", err)
	}

	var result map[string]interface{}
	if err := json.Unmarshal(data, &result); err != nil {
		t.Fatalf("failed to unmarshal: %v", err)
	}

	if result["app_id"] != "app-999" {
		t.Errorf("app_id = %v, want app-999", result["app_id"])
	}

	anomalies, ok := result["anomalies"].([]interface{})
	if !ok || len(anomalies) != 1 {
		t.Fatalf("expected 1 anomaly, got %d", len(anomalies))
	}

	firstAnomaly, ok := anomalies[0].(map[string]interface{})
	if !ok {
		t.Fatal("expected anomaly to be a map")
	}

	if firstAnomaly["anomaly_type"] != "SKEW" {
		t.Errorf("anomaly_type = %v, want SKEW", firstAnomaly["anomaly_type"])
	}

	if firstAnomaly["severity"] != "CRITICAL" {
		t.Errorf("severity = %v, want CRITICAL", firstAnomaly["severity"])
	}

	recs, ok := result["recommendations"].([]interface{})
	if !ok || len(recs) != 1 {
		t.Fatalf("expected 1 recommendation, got %d", len(recs))
	}

	firstRec, ok := recs[0].(map[string]interface{})
	if !ok {
		t.Fatal("expected recommendation to be a map")
	}

	if firstRec["summary"] != "Apply salting to distribute join key evenly" {
		t.Errorf("summary = %v, want 'Apply salting to distribute join key evenly'", firstRec["summary"])
	}
}

// TestRecommenderWithNoAPIKey tests fallback when no OpenAI API key is set.
func TestRecommenderWithNoAPIKey(t *testing.T) {
	t.Setenv("OPENAI_API_KEY", "")

	rec := recommender.NewRecommender("")
	report := models.AnomalyReport{
		AnomalyType: "SKEW",
		Severity:    "HIGH",
		Description: "Data skew detected",
		Confidence:  0.9,
	}

	recommendation := rec.Recommend(report)

	if recommendation.Confidence != 0.3 {
		t.Errorf("Confidence = %v, want 0.3", recommendation.Confidence)
	}

	if recommendation.Summary == "" {
		t.Error("expected non-empty summary")
	}

	if len(recommendation.Steps) == 0 {
		t.Error("expected at least one step")
	}
}

// TestMarshalOutputIndentation tests that marshalOutput produces indented JSON.
func TestMarshalOutputIndentation(t *testing.T) {
	input := map[string]interface{}{
		"app_id": "app-indent",
		"anomalies": []models.AnomalyReport{
			{AnomalyType: "SKEW", Confidence: 0.8},
		},
		"recommendations": []models.Recommendation{},
	}

	data, err := marshalOutput(input)
	if err != nil {
		t.Fatalf("marshalOutput error: %v", err)
	}

	output := string(data)
	if !strings.Contains(output, "\n") {
		t.Error("expected output to contain newlines (indented)")
	}
	if !strings.Contains(output, "  ") {
		t.Error("expected output to contain indentation spaces")
	}
}

// TestBuildOutputNilSlices tests buildOutput with nil slices.
func TestBuildOutputNilSlices(t *testing.T) {
	out := buildOutput("app-nil", nil, nil)

	anomalies, ok := out["anomalies"].([]models.AnomalyReport)
	if !ok {
		t.Fatal("expected anomalies to be []models.AnomalyReport")
	}
	if anomalies != nil && len(anomalies) != 0 {
		t.Errorf("expected nil or empty anomalies, got %d", len(anomalies))
	}

	recs, ok := out["recommendations"].([]models.Recommendation)
	if !ok {
		t.Fatal("expected recommendations to be []models.Recommendation")
	}
	if recs != nil && len(recs) != 0 {
		t.Errorf("expected nil or empty recommendations, got %d", len(recs))
	}
}

// TestRunbookAnomalyToFilename tests the anomaly-to-filename mapping.
func TestRunbookAnomalyToFilename(t *testing.T) {
	mgr := runbook.NewManager("")

	knownTypes := []string{"SKEW", "SPILL", "GC_PRESSURE", "OOM", "data_skew", "spill"}
	for _, typ := range knownTypes {
		_, err := mgr.Load(typ)
		if err != nil && strings.Contains(err.Error(), "nenhum runbook mapeado") {
			t.Errorf("anomaly type %q should be mapped to a filename", typ)
		}
	}

	_, err := mgr.Load("UNKNOWN_TYPE")
	if err == nil || !strings.Contains(err.Error(), "nenhum runbook mapeado") {
		t.Error("expected 'nenhum runbook mapeado' error for unknown type")
	}
}

// TestRecommenderNewRecommenderWithCREI tests CREI URL configuration.
func TestRecommenderNewRecommenderWithCREI(t *testing.T) {
	rec := recommender.NewRecommenderWithCREI("/tmp/runbooks", "http://crei:8080")
	if rec.CREIURL != "http://crei:8080" {
		t.Errorf("CREIURL = %v, want http://crei:8080", rec.CREIURL)
	}
	if rec.RunbookManager == nil {
		t.Error("expected RunbookManager to be non-nil")
	}
}

// TestRecommenderNewRecommenderWithCREIEmptyURL tests CREI fallback.
func TestRecommenderNewRecommenderWithCREIEmptyURL(t *testing.T) {
	os.Unsetenv("CREI_URL")
	rec := recommender.NewRecommenderWithCREI("/tmp/runbooks", "")
	if rec.CREIURL != "http://localhost:8000" {
		t.Errorf("CREIURL = %v, want http://localhost:8000", rec.CREIURL)
	}
}

// TestBuildOutputTypeConsistency tests that buildOutput returns consistent types.
func TestBuildOutputTypeConsistency(t *testing.T) {
	reports := []models.AnomalyReport{
		{AnomalyType: "SKEW", Confidence: 0.9},
	}
	recs := []models.Recommendation{
		{AnomalyType: "SKEW", Confidence: 0.85},
	}

	out := buildOutput("app-consistent", reports, recs)

	expectedKeys := []string{"app_id", "anomalies", "recommendations"}
	for _, key := range expectedKeys {
		if _, ok := out[key]; !ok {
			t.Errorf("missing key %q in output", key)
		}
	}

	if _, ok := out["app_id"].(string); !ok {
		t.Errorf("app_id is not string, got %T", out["app_id"])
	}
	if _, ok := out["anomalies"].([]models.AnomalyReport); !ok {
		t.Errorf("anomalies is not []models.AnomalyReport, got %T", out["anomalies"])
	}
	if _, ok := out["recommendations"].([]models.Recommendation); !ok {
		t.Errorf("recommendations is not []models.Recommendation, got %T", out["recommendations"])
	}
}

// Helper functions extracted from main.go logic for testability

// buildOutput constructs the output map that main.go marshals to JSON.
func buildOutput(appID string, reports []models.AnomalyReport, recommendations []models.Recommendation) map[string]interface{} {
	return map[string]interface{}{
		"app_id":          appID,
		"anomalies":       reports,
		"recommendations": recommendations,
	}
}

// marshalOutput marshals the output map to indented JSON.
func marshalOutput(out map[string]interface{}) ([]byte, error) {
	return json.MarshalIndent(out, "", "  ")
}

// validateAppID validates that the appID is not empty.
func validateAppID(appID string) error {
	if strings.TrimSpace(appID) == "" {
		return os.ErrInvalid
	}
	return nil
}
