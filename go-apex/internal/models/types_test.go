package models

import (
	"encoding/json"
	"testing"
)

func TestFindingMarshalUnmarshal(t *testing.T) {
	stageID := int64(5)
	finding := Finding{
		AnomalyType: "data_skew",
		Severity:    SeverityCritical,
		Confidence:  0.92,
		Description: "Stage 5 has skew ratio 29.5x",
		StageID:     &stageID,
		RootCause:   "Shuffle join with unbalanced key",
	}

	data, err := json.Marshal(finding)
	if err != nil {
		t.Fatalf("marshal failed: %v", err)
	}

	var decoded Finding
	if err := json.Unmarshal(data, &decoded); err != nil {
		t.Fatalf("unmarshal failed: %v", err)
	}

	if decoded.AnomalyType != finding.AnomalyType {
		t.Errorf("anomaly type mismatch: got %q, want %q", decoded.AnomalyType, finding.AnomalyType)
	}
	if decoded.Confidence != finding.Confidence {
		t.Errorf("confidence mismatch: got %f, want %f", decoded.Confidence, finding.Confidence)
	}
	if decoded.StageID == nil || *decoded.StageID != stageID{
		t.Errorf("stage_id mismatch")
	}
}

func TestSeverityString(t *testing.T) {
	tests := []struct {
		severity Severity
		want     string
	}{
		{SeverityCritical, "CRITICAL"},
		{SeverityHigh, "HIGH"},
		{SeverityMedium, "MEDIUM"},
		{SeverityLow, "LOW"},
		{SeverityError, "ERROR"},
	}

	for _, tt := range tests {
		t.Run(tt.want, func(t *testing.T) {
			got := string(tt.severity)
			if got != tt.want {
				t.Errorf("String() = %q, want %q", got, tt.want)
			}
		})
	}
}

func TestValidationResult(t *testing.T) {
	result := ValidationResult{
		Rule:    "SkewRatioRule",
		Status:  EvidenceStatusValid,
		Message: "Skew ratio 29.5x exceeds threshold",
	}

	if result.Status != EvidenceStatusValid {
		t.Errorf("expected status valid, got %v", result.Status)
	}
	if result.Rule != "SkewRatioRule" {
		t.Errorf("rule mismatch: got %q", result.Rule)
	}
}

func TestDiagnosisResult(t *testing.T) {
	result := DiagnosisResult{
		Tier:          "T1",
		JobID:         "app-test",
		FindingsCount: 3,
		Findings:      []Finding{},
		ResolvedByT1:  false,
	}

	if result.FindingsCount != 3 {
		t.Errorf("findings count: got %d, want 3", result.FindingsCount)
	}
	if result.Tier != "T1" {
		t.Errorf("tier mismatch: got %q, want T1", result.Tier)
	}
}

func TestRecommendation(t *testing.T) {
	rec := Recommendation{
		AnomalyType:    "data_skew",
		Confidence:     0.92,
		Summary:        "Apply salting with 10 buckets",
		Steps:          []StepAction{{Action: "salting", Details: "add 10 buckets"}},
		ExpectedImpact: "Speedup 15x",
	}

	if rec.Confidence < 0.9 {
		t.Errorf("confidence too low: %f", rec.Confidence)
	}
	if len(rec.Steps) != 1 {
		t.Errorf("steps count: got %d, want 1", len(rec.Steps))
	}
}

func TestEvidenceStatusConstants(t *testing.T) {
	if EvidenceStatusValid != "valid" {
		t.Errorf("valid status mismatch")
	}
	if EvidenceStatusInvalid != "invalid" {
		t.Errorf("invalid status mismatch")
	}
	if EvidenceStatusIndeterminate != "indeterminate" {
		t.Errorf("indeterminate status mismatch")
	}
}
