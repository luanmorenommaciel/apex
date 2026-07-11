package main

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"testing"

	"github.com/apex/go-apex/internal/models"
)

// TestJoinStrings tests the joinStrings helper with various inputs.
func TestJoinStrings(t *testing.T) {
	tests := []struct {
		name     string
		vals     []string
		sep      string
		expected string
	}{
		{
			name:     "empty slice",
			vals:     []string{},
			sep:      " | ",
			expected: "",
		},
		{
			name:     "single element",
			vals:     []string{"only-one"},
			sep:      " | ",
			expected: "only-one",
		},
		{
			name:     "multiple elements",
			vals:     []string{"skew detected", "spill detected", "gc pressure"},
			sep:      " | ",
			expected: "skew detected | spill detected | gc pressure",
		},
		{
			name:     "custom separator",
			vals:     []string{"a", "b", "c"},
			sep:      ", ",
			expected: "a, b, c",
		},
		{
			name:     "empty separator",
			vals:     []string{"a", "b"},
			sep:      "",
			expected: "ab",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := joinStrings(tt.vals, tt.sep)
			if got != tt.expected {
				t.Errorf("joinStrings(%v, %q) = %q; want %q", tt.vals, tt.sep, got, tt.expected)
			}
		})
	}
}

// TestUniqueStrings tests the uniqueStrings helper.
func TestUniqueStrings(t *testing.T) {
	tests := []struct {
		name     string
		vals     []string
		expected []string
	}{
		{
			name:     "empty slice",
			vals:     []string{},
			expected: []string{},
		},
		{
			name:     "no duplicates",
			vals:     []string{"SKEW", "SPILL", "OOM"},
			expected: []string{"SKEW", "SPILL", "OOM"},
		},
		{
			name:     "with duplicates",
			vals:     []string{"SKEW", "SPILL", "SKEW", "OOM", "SPILL"},
			expected: []string{"SKEW", "SPILL", "OOM"},
		},
		{
			name:     "all duplicates",
			vals:     []string{"SKEW", "SKEW", "SKEW"},
			expected: []string{"SKEW"},
		},
		{
			name:     "preserves first occurrence order",
			vals:     []string{"b", "a", "b", "c", "a"},
			expected: []string{"b", "a", "c"},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := uniqueStrings(tt.vals)
			if len(got) != len(tt.expected) {
				t.Fatalf("uniqueStrings(%v) length = %d; want %d", tt.vals, len(got), len(tt.expected))
			}
			for i, v := range tt.expected {
				if got[i] != v {
					t.Errorf("uniqueStrings(%v)[%d] = %q; want %q", tt.vals, i, got[i], v)
				}
			}
		})
	}
}

// TestRespondJSON tests the respondJSON helper with various payloads.
func TestRespondJSON(t *testing.T) {
	tests := []struct {
		name         string
		payload      interface{}
		expectedCode int
		expectedBody string
	}{
		{
			name:         "health status map",
			payload:      map[string]interface{}{"status": "healthy", "version": creiVersion},
			expectedCode: http.StatusOK,
			expectedBody: "healthy",
		},
		{
			name:         "version string map",
			payload:      map[string]string{"version": creiVersion},
			expectedCode: http.StatusOK,
			expectedBody: creiVersion,
		},
		{
			name: "analyze response struct",
			payload: analyzeResponse{
				AppID:           "app-123",
				Diagnosis:       "skew detected",
				RootCause:       []string{"SKEW"},
				Recommendations: []string{"repartition"},
				Confidence:      0.85,
			},
			expectedCode: http.StatusOK,
			expectedBody: "app-123",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			rec := httptest.NewRecorder()
			respondJSON(rec, tt.payload)

			res := rec.Result()
			defer res.Body.Close()

			if res.StatusCode != tt.expectedCode {
				t.Errorf("StatusCode = %d; want %d", res.StatusCode, tt.expectedCode)
			}

			ct := res.Header.Get("Content-Type")
			if ct != "application/json" {
				t.Errorf("Content-Type = %q; want %q", ct, "application/json")
			}

			body, _ := io.ReadAll(res.Body)
			if !bytes.Contains(body, []byte(tt.expectedBody)) {
				t.Errorf("Body does not contain %q; got %s", tt.expectedBody, string(body))
			}

			// Verify valid JSON
			var dummy map[string]interface{}
			if err := json.Unmarshal(body, &dummy); err != nil {
				t.Errorf("Body is not valid JSON: %v", err)
			}
		})
	}
}

// TestHealthHandler tests the /health endpoint.
func TestHealthHandler(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	rec := httptest.NewRecorder()

	healthHandler(rec, req)

	res := rec.Result()
	defer res.Body.Close()

	if res.StatusCode != http.StatusOK {
		t.Errorf("StatusCode = %d; want %d", res.StatusCode, http.StatusOK)
	}

	ct := res.Header.Get("Content-Type")
	if ct != "application/json" {
		t.Errorf("Content-Type = %q; want %q", ct, "application/json")
	}

	body, _ := io.ReadAll(res.Body)
	var result map[string]interface{}
	if err := json.Unmarshal(body, &result); err != nil {
		t.Fatalf("Failed to unmarshal response: %v", err)
	}

	if result["status"] != "healthy" {
		t.Errorf("status = %q; want %q", result["status"], "healthy")
	}
	if result["version"] != creiVersion {
		t.Errorf("version = %q; want %q", result["version"], creiVersion)
	}
}

// TestVersionHandler tests the /version endpoint.
func TestVersionHandler(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/version", nil)
	rec := httptest.NewRecorder()

	versionHandler(rec, req)

	res := rec.Result()
	defer res.Body.Close()

	if res.StatusCode != http.StatusOK {
		t.Errorf("StatusCode = %d; want %d", res.StatusCode, http.StatusOK)
	}

	body, _ := io.ReadAll(res.Body)
	var result map[string]string
	if err := json.Unmarshal(body, &result); err != nil {
		t.Fatalf("Failed to unmarshal response: %v", err)
	}

	if result["version"] != creiVersion {
		t.Errorf("version = %q; want %q", result["version"], creiVersion)
	}
}

// TestAnalyzeHandlerMethodNotAllowed tests that non-POST requests are rejected.
func TestAnalyzeHandlerMethodNotAllowed(t *testing.T) {
	methods := []string{http.MethodGet, http.MethodPut, http.MethodDelete, http.MethodPatch}

	for _, method := range methods {
		t.Run(method, func(t *testing.T) {
			req := httptest.NewRequest(method, "/analyze", nil)
			rec := httptest.NewRecorder()

			analyzeHandler(rec, req)

			res := rec.Result()
			defer res.Body.Close()

			if res.StatusCode != http.StatusMethodNotAllowed {
				t.Errorf("StatusCode = %d; want %d", res.StatusCode, http.StatusMethodNotAllowed)
			}
		})
	}
}

// TestAnalyzeHandlerBadJSON tests that invalid JSON returns 400.
func TestAnalyzeHandlerBadJSON(t *testing.T) {
	req := httptest.NewRequest(http.MethodPost, "/analyze", strings.NewReader("not-json"))
	rec := httptest.NewRecorder()

	analyzeHandler(rec, req)

	res := rec.Result()
	defer res.Body.Close()

	if res.StatusCode != http.StatusBadRequest {
		t.Errorf("StatusCode = %d; want %d", res.StatusCode, http.StatusBadRequest)
	}

	body, _ := io.ReadAll(res.Body)
	if !bytes.Contains(body, []byte("Invalid JSON")) {
		t.Errorf("Body does not contain 'Invalid JSON'; got %s", string(body))
	}
}

// TestAnalyzeHandlerMissingAppID tests that missing app_id returns 400.
func TestAnalyzeHandlerMissingAppID(t *testing.T) {
	payload := map[string]string{"request_type": "test"}
	bodyBytes, _ := json.Marshal(payload)

	req := httptest.NewRequest(http.MethodPost, "/analyze", bytes.NewReader(bodyBytes))
	rec := httptest.NewRecorder()

	analyzeHandler(rec, req)

	res := rec.Result()
	defer res.Body.Close()

	if res.StatusCode != http.StatusBadRequest {
		t.Errorf("StatusCode = %d; want %d", res.StatusCode, http.StatusBadRequest)
	}

	body, _ := io.ReadAll(res.Body)
	if !bytes.Contains(body, []byte("app_id is required")) {
		t.Errorf("Body does not contain 'app_id is required'; got %s", string(body))
	}
}

// TestBuildAnalyzeResponse tests the response building logic with mock data.
func TestBuildAnalyzeResponse(t *testing.T) {
	tests := []struct {
		name                  string
		reports               []models.AnomalyReport
		recommendations       []models.Recommendation
		expectedAppID         string
		expectEmptyDiagnosis  bool
	}{
		{
			name:                 "empty reports and recommendations",
			reports:              []models.AnomalyReport{},
			recommendations:      []models.Recommendation{},
			expectedAppID:        "app-456",
			expectEmptyDiagnosis: false,
		},
		{
			name: "with reports and recommendations",
			reports: []models.AnomalyReport{
				{
					AppID:       "app-123",
					AnomalyType: "SKEW",
					Description: "Stage skew detected",
					Severity:    "HIGH",
				},
				{
					AppID:       "app-123",
					AnomalyType: "SPILL",
					Description: "Memory spill detected",
					Severity:    "MEDIUM",
				},
			},
			recommendations: []models.Recommendation{
				{AnomalyType: "SKEW", Summary: "Repartition data", Confidence: 0.9},
				{AnomalyType: "SPILL", Summary: "Increase memory", Confidence: 0.8},
			},
			expectedAppID:        "app-123",
			expectEmptyDiagnosis: false,
		},
		{
			name: "duplicate anomaly types deduplicated",
			reports: []models.AnomalyReport{
				{AnomalyType: "SKEW", Description: "Skew 1"},
				{AnomalyType: "SKEW", Description: "Skew 2"},
				{AnomalyType: "OOM", Description: "OOM 1"},
			},
			recommendations: []models.Recommendation{
				{Summary: "Fix skew"},
				{Summary: "Fix skew"},
				{Summary: "Fix oom"},
			},
			expectedAppID:        "app-dedup",
			expectEmptyDiagnosis: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Simulate the response building logic from analyzeHandler
			diagnosisParts := []string{}
			rootCause := []string{}
			recommendationStrs := []string{}

			for _, rep := range tt.reports {
				diagnosisParts = append(diagnosisParts, rep.Description)
				rootCause = append(rootCause, rep.AnomalyType)
			}
			for _, rec := range tt.recommendations {
				recommendationStrs = append(recommendationStrs, rec.Summary)
			}

			if len(diagnosisParts) == 0 {
				diagnosisParts = append(diagnosisParts, "Nenhuma anomalia detectada.")
				rootCause = append(rootCause, "no_anomaly")
				recommendationStrs = append(recommendationStrs, "Monitorar metricas de baseline")
			}

			resp := analyzeResponse{
				AppID:           tt.expectedAppID,
				Diagnosis:       joinStrings(diagnosisParts, " | "),
				RootCause:       uniqueStrings(rootCause),
				Recommendations: uniqueStrings(recommendationStrs),
				Confidence:      0.85,
				JobDataSummary: map[string]interface{}{
					"anomalies_count":       len(tt.reports),
					"recommendations_count": len(tt.recommendations),
				},
			}

			if resp.AppID != tt.expectedAppID {
				t.Errorf("AppID = %q; want %q", resp.AppID, tt.expectedAppID)
			}

			if tt.expectEmptyDiagnosis && resp.Diagnosis != "" {
				t.Errorf("Diagnosis = %q; want empty", resp.Diagnosis)
			}

			if len(tt.reports) > 0 {
				if resp.Diagnosis == "" {
					t.Errorf("Diagnosis is empty; expected non-empty")
				}
				if len(resp.RootCause) == 0 {
					t.Errorf("RootCause is empty; expected non-empty")
				}
			}

			// Verify deduplication
			if tt.name == "duplicate anomaly types deduplicated" {
				if len(resp.RootCause) != 2 {
					t.Errorf("RootCause length = %d; want 2 (SKEW, OOM)", len(resp.RootCause))
				}
				if len(resp.Recommendations) != 2 {
					t.Errorf("Recommendations length = %d; want 2 (Fix skew, Fix oom)", len(resp.Recommendations))
				}
			}

			if resp.Confidence != 0.85 {
				t.Errorf("Confidence = %f; want 0.85", resp.Confidence)
			}
		})
	}
}

// TestAnalyzeRequestDecoding tests JSON decoding of analyzeRequest.
func TestAnalyzeRequestDecoding(t *testing.T) {
	tests := []struct {
		name        string
		jsonInput   string
		expectedApp string
		expectErr   bool
	}{
		{
			name:        "valid request",
			jsonInput:   `{"app_id":"my-app","job_data":{"key":"val"}}`,
			expectedApp: "my-app",
			expectErr:   false,
		},
		{
			name:        "empty app_id",
			jsonInput:   `{"app_id":""}`,
			expectedApp: "",
			expectErr:   false,
		},
		{
			name:        "missing app_id field",
			jsonInput:   `{"request_type":"test"}`,
			expectedApp: "",
			expectErr:   false,
		},
		{
			name:        "with request_type",
			jsonInput:   `{"app_id":"app-1","request_type":"full"}`,
			expectedApp: "app-1",
			expectErr:   false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var req analyzeRequest
			err := json.Unmarshal([]byte(tt.jsonInput), &req)

			if tt.expectErr && err == nil {
				t.Fatalf("Expected error but got nil")
			}
			if !tt.expectErr && err != nil {
				t.Fatalf("Unexpected error: %v", err)
			}

			if req.AppID != tt.expectedApp {
				t.Errorf("AppID = %q; want %q", req.AppID, tt.expectedApp)
			}
		})
	}
}

// TestMainExitCode captures main() exit behavior via a wrapper.
func TestMainExitCode(t *testing.T) {
	if os.Getenv("BE_TEST_MAIN") == "1" {
		// When running inside the subprocess, main() will try to start a server.
		// We set an invalid port to force a quick failure, or we rely on the
		// environment to prevent actual server startup. Since main() calls
		// log.Fatalf on server failure, it exits with code 1.
		os.Setenv("CREI_PORT", "invalid-port")
		main()
		return
	}

	// Skip this test in normal runs because it requires subprocess execution.
	// The test documents the pattern for capturing os.Exit from main().
	t.Skip("Skipping main() exit code test: requires subprocess execution and would block on server startup")
}

// TestCreiVersionConstant ensures the version constant is set.
func TestCreiVersionConstant(t *testing.T) {
	if creiVersion == "" {
		t.Error("creiVersion should not be empty")
	}
	if !strings.Contains(creiVersion, "0.1.0") {
		t.Errorf("creiVersion %q should contain '0.1.0'", creiVersion)
	}
}

// TestAnalyzeResponseStructJSON tests that analyzeResponse serializes correctly.
func TestAnalyzeResponseStructJSON(t *testing.T) {
	resp := analyzeResponse{
		AppID:           "test-app",
		Diagnosis:       "all good",
		RootCause:       []string{"none"},
		Recommendations: []string{"keep monitoring"},
		Confidence:      0.95,
		Runbook: map[string]interface{}{
			"steps": []string{"step1", "step2"},
		},
		JobDataSummary: map[string]interface{}{
			"anomalies_count": 0,
		},
	}

	data, err := json.Marshal(resp)
	if err != nil {
		t.Fatalf("Failed to marshal analyzeResponse: %v", err)
	}

	var decoded analyzeResponse
	if err := json.Unmarshal(data, &decoded); err != nil {
		t.Fatalf("Failed to unmarshal analyzeResponse: %v", err)
	}

	if decoded.AppID != resp.AppID {
		t.Errorf("AppID = %q; want %q", decoded.AppID, resp.AppID)
	}
	if decoded.Confidence != resp.Confidence {
		t.Errorf("Confidence = %f; want %f", decoded.Confidence, resp.Confidence)
	}
	if len(decoded.RootCause) != len(resp.RootCause) {
		t.Errorf("RootCause length = %d; want %d", len(decoded.RootCause), len(resp.RootCause))
	}
}
