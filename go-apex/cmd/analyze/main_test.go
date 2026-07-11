package main

import (
	"testing"

	"github.com/apex/go-apex/internal/models"
)

func TestStartsWithIgnoreCase(t *testing.T) {
	tests := []struct {
		s, prefix string
		expected  bool
	}{
		{"hello", "he", true},
		{"Hello", "he", true},
		{"HELLO", "he", true},
		{"hello", "xyz", false},
		{"", "a", false},
		{"a", "", true},
		{"", "", true},
	}
	for _, tt := range tests {
		got := startsWithIgnoreCase(tt.s, tt.prefix)
		if got != tt.expected {
			t.Errorf("startsWithIgnoreCase(%q, %q) = %v, want %v", tt.s, tt.prefix, got, tt.expected)
		}
	}
}

func TestContainsIgnoreCase(t *testing.T) {
	tests := []struct {
		s, substr string
		expected  bool
	}{
		{"hello world", "WORLD", true},
		{"Hello World", "world", true},
		{"hello", "xyz", false},
		{"", "a", false},
		{"a", "", true},
		{"", "", true},
	}
	for _, tt := range tests {
		got := containsIgnoreCase(tt.s, tt.substr)
		if got != tt.expected {
			t.Errorf("containsIgnoreCase(%q, %q) = %v, want %v", tt.s, tt.substr, got, tt.expected)
		}
	}
}

func TestReviewAnomaly(t *testing.T) {
	// Test with matching runbook and high confidence
	report := models.AnomalyReport{
		AnomalyType: "SKEW",
		Severity:    "HIGH",
	}
	rec := models.Recommendation{
		RunbookID:  "SKEW_fix",
		Confidence: 0.9,
		CodeFix:    "some code",
	}
	result := reviewAnomaly(report, rec)
	if !result.Passed {
		t.Errorf("reviewAnomaly with matching runbook should pass, got Passed=%v", result.Passed)
	}

	// Test with low confidence
	rec2 := models.Recommendation{
		RunbookID:  "SKEW_fix",
		Confidence: 0.3,
		CodeFix:    "some code",
	}
	result2 := reviewAnomaly(report, rec2)
	if result2.Passed {
		t.Errorf("reviewAnomaly with low confidence should fail, got Passed=%v", result2.Passed)
	}

	// Test CRITICAL without code fix
	report3 := models.AnomalyReport{
		AnomalyType: "OOM",
		Severity:    "CRITICAL",
	}
	rec3 := models.Recommendation{
		RunbookID:  "OOM_fix",
		Confidence: 0.9,
		CodeFix:    "",
	}
	result3 := reviewAnomaly(report3, rec3)
	if result3.Passed {
		t.Errorf("reviewAnomaly CRITICAL without code fix should fail, got Passed=%v", result3.Passed)
	}

	// Test with TODO in code fix
	rec4 := models.Recommendation{
		RunbookID:  "SKEW_fix",
		Confidence: 0.9,
		CodeFix:    "// TODO: implement fix",
	}
	report4 := models.AnomalyReport{
		AnomalyType: "SKEW",
		Severity:    "HIGH",
		AffectedStages: []int{1},
	}
	result4 := reviewAnomaly(report4, rec4)
	if result4.Passed {
		t.Errorf("reviewAnomaly with TODO should fail, got Passed=%v", result4.Passed)
	}
}
