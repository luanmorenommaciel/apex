package recommender

import (
	"errors"
	"reflect"
	"testing"

	"github.com/apex/go-apex/internal/models"
)

func TestToJSON(t *testing.T) {
	tests := []struct {
		name     string
		input    interface{}
		expected string
	}{
		{"map", map[string]interface{}{"k": "v"}, `{"k":"v"}`},
		{"nil", nil, "null"},
		{"empty map", map[string]interface{}{}, "{}"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := toJSON(tt.input)
			if got != tt.expected {
				t.Errorf("toJSON() = %q, want %q", got, tt.expected)
			}
		})
	}
}

func TestExtractJSON(t *testing.T) {
	tests := []struct {
		name    string
		input   string
		wantErr bool
	}{
		{"valid JSON", `{"a":1}`, false},
		{"JSON in text", `result: {"a":1} end`, false},
		{"no JSON", `no json here`, true},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			_, err := extractJSON(tt.input)
			if tt.wantErr && err == nil {
				t.Errorf("expected error, got nil")
			}
			if !tt.wantErr && err != nil {
				t.Errorf("unexpected error: %v", err)
			}
		})
	}
}

func TestGetString(t *testing.T) {
	m := map[string]interface{}{"a": "val", "b": 42}
	if got := getString(m, "a", "def"); got != "val" {
		t.Errorf("getString(a) = %q, want val", got)
	}
	if got := getString(m, "missing", "def"); got != "def" {
		t.Errorf("getString(missing) = %q, want def", got)
	}
}

func TestGetFloat(t *testing.T) {
	m := map[string]interface{}{"f": 3.14, "i": 42}
	if got := getFloat(m, "f", 0); got != 3.14 {
		t.Errorf("getFloat(f) = %v, want 3.14", got)
	}
	if got := getFloat(m, "i", 0); got != 0 {
		t.Errorf("getFloat(i) = %v, want 0 (int not float64)", got)
	}
}

func TestGetInt(t *testing.T) {
	m := map[string]interface{}{"f": 42.0, "i": 99}
	if got := getInt(m, "f", 0); got != 42 {
		t.Errorf("getInt(f) = %v, want 42", got)
	}
	if got := getInt(m, "missing", -1); got != -1 {
		t.Errorf("getInt(missing) = %v, want -1", got)
	}
}

func TestToStringSlice(t *testing.T) {
	got := toStringSlice([]interface{}{"a", "b"})
	if !reflect.DeepEqual(got, []string{"a", "b"}) {
		t.Errorf("toStringSlice = %v, want [a b]", got)
	}
	got = toStringSlice(nil)
	if len(got) != 0 {
		t.Errorf("toStringSlice(nil) = %v, want empty", got)
	}
}

func TestUniqueStrings(t *testing.T) {
	got := uniqueStrings([]string{"a", "b", "a"})
	if !reflect.DeepEqual(got, []string{"a", "b"}) {
		t.Errorf("uniqueStrings = %v, want [a b]", got)
	}
}

func TestSliceFirstN(t *testing.T) {
	got := sliceFirstN([]interface{}{1, 2, 3, 4}, 2)
	if !reflect.DeepEqual(got, []interface{}{1, 2}) {
		t.Errorf("sliceFirstN = %v, want [1 2]", got)
	}
}

func TestFallbackError(t *testing.T) {
	report := models.AnomalyReport{AnomalyType: "skew"}
	got := fallbackError(report, errors.New("fail"))
	if got.Confidence != 0.2 {
		t.Errorf("Confidence = %v, want 0.2", got.Confidence)
	}
	if got.AnomalyType != "skew" {
		t.Errorf("AnomalyType = %q, want skew", got.AnomalyType)
	}
}
