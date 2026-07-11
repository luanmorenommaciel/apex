package watcher

import (
	"math"
	"reflect"
	"testing"
)

func TestToFloat64(t *testing.T) {
	tests := []struct {
		name     string
		input    interface{}
		expected float64
	}{
		{"nil", nil, 0},
		{"float64", 2.5, 2.5},
		{"int", 4, 4.0},
		{"string", "1.5", 1.5},
		{"invalid", "xyz", 0},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := toFloat64(tt.input)
			if got != tt.expected {
				t.Errorf("toFloat64(%v) = %f, want %f", tt.input, got, tt.expected)
			}
		})
	}
}

func TestToInt(t *testing.T) {
	tests := []struct {
		name     string
		input    interface{}
		expected int
	}{
		{"nil", nil, 0},
		{"int", 42, 42},
		{"float64", 3.9, 3},
		{"string", "99", 99},
		{"invalid", "abc", 0},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := toInt(tt.input)
			if got != tt.expected {
				t.Errorf("toInt(%v) = %d, want %d", tt.input, got, tt.expected)
			}
		})
	}
}

func TestToString(t *testing.T) {
	tests := []struct {
		name     string
		input    interface{}
		expected string
	}{
		{"nil", nil, ""},
		{"string", "hello", "hello"},
		{"int", 42, "42"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := toString(tt.input)
			if got != tt.expected {
				t.Errorf("toString(%v) = %q, want %q", tt.input, got, tt.expected)
			}
		})
	}
}

func TestToStringSlice(t *testing.T) {
	tests := []struct {
		name     string
		input    interface{}
		expected []string
	}{
		{"nil", nil, nil},
		{"interface slice", []interface{}{"a", 1}, []string{"a", "1"}},
		{"string slice", []string{"a", "b"}, []string{"a", "b"}},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := toStringSlice(tt.input)
			if !reflect.DeepEqual(got, tt.expected) {
				t.Errorf("toStringSlice(%v) = %v, want %v", tt.input, got, tt.expected)
			}
		})
	}
}

func TestToMap(t *testing.T) {
	tests := []struct {
		name     string
		input    interface{}
		expected map[string]interface{}
	}{
		{"nil", nil, nil},
		{"map", map[string]interface{}{"a": 1}, map[string]interface{}{"a": 1}},
		{"not map", "hello", nil},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := toMap(tt.input)
			if !reflect.DeepEqual(got, tt.expected) {
				t.Errorf("toMap(%v) = %v, want %v", tt.input, got, tt.expected)
			}
		})
	}
}

func TestMaxInt(t *testing.T) {
	input := []int{3, 1, 4, 1, 5}
	got := maxInt(input)
	if got != 5 {
		t.Errorf("maxInt(%v) = %d, want %d", input, got, 5)
	}
}

func TestMaxFloat64(t *testing.T) {
	input := []float64{1.1, 3.3, 2.2}
	got := maxFloat64(input)
	if got != 3.3 {
		t.Errorf("maxFloat64(%v) = %f, want %f", input, got, 3.3)
	}
}

func TestMedianInt(t *testing.T) {
	tests := []struct {
		name     string
		input    []int
		expected float64
	}{
		{"empty", []int{}, 0},
		{"odd", []int{1, 2, 3}, 2},
		{"even", []int{1, 2, 3, 4}, 2.5},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := medianInt(tt.input)
			if got != tt.expected {
				t.Errorf("medianInt(%v) = %f, want %f", tt.input, got, tt.expected)
			}
		})
	}
}

func TestSkewMetrics(t *testing.T) {
	t.Run("empty", func(t *testing.T) {
		got := skewMetrics([]int{})
		if got["n_tasks"] != 0 {
			t.Errorf("skewMetrics empty n_tasks = %v, want 0", got["n_tasks"])
		}
	})

	t.Run("single", func(t *testing.T) {
		got := skewMetrics([]int{10})
		if got["collapsed"] != true {
			t.Errorf("skewMetrics single collapsed = %v, want true", got["collapsed"])
		}
	})

	t.Run("normal", func(t *testing.T) {
		got := skewMetrics([]int{10, 2, 2})
		if got["hot"] != 10 {
			t.Errorf("skewMetrics hot = %v, want 10", got["hot"])
		}
		if math.IsInf(got["ratio"].(float64), 1) {
			t.Errorf("skewMetrics ratio should not be Inf for normal case")
		}
	})
}

func TestParseInt(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected int
		wantErr  bool
	}{
		{"positive", "123", 123, false},
		{"negative", "-45", -45, false},
		{"empty", "", 0, true},
		{"invalid", "abc", 0, true},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := parseInt(tt.input)
			if (err != nil) != tt.wantErr {
				t.Errorf("parseInt(%q) error = %v, wantErr %v", tt.input, err, tt.wantErr)
				return
			}
			if got != tt.expected {
				t.Errorf("parseInt(%q) = %d, want %d", tt.input, got, tt.expected)
			}
		})
	}
}

func TestParseFloat(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected float64
		wantErr  bool
	}{
		{"positive", "3.14", 3.14, false},
		{"negative", "-2.5", -2.5, false},
		{"integer", "10", 10.0, false},
		{"empty", "", 0, true},
		{"invalid", "abc", 0, true},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := parseFloat(tt.input)
			if (err != nil) != tt.wantErr {
				t.Errorf("parseFloat(%q) error = %v, wantErr %v", tt.input, err, tt.wantErr)
				return
			}
			if math.Abs(got-tt.expected) > 1e-9 {
				t.Errorf("parseFloat(%q) = %f, want %f", tt.input, got, tt.expected)
			}
		})
	}
}

func TestSplitLines(t *testing.T) {
	input := "line1\nline2\nline3"
	got := splitLines(input)
	expected := []string{"line1", "line2", "line3"}
	if !reflect.DeepEqual(got, expected) {
		t.Errorf("splitLines(%q) = %v, want %v", input, got, expected)
	}
}

func TestTrimSpace(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected string
	}{
		{"spaces", "  hello  ", "hello"},
		{"tabs", "\thello\t", "hello"},
		{"mixed", " \t hello \r\n", "hello"},
		{"empty", "", ""},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := trimSpace(tt.input)
			if got != tt.expected {
				t.Errorf("trimSpace(%q) = %q, want %q", tt.input, got, tt.expected)
			}
		})
	}
}

func TestJoinStrings(t *testing.T) {
	input := []string{"a", "b", "c"}
	got := joinStrings(input, ", ")
	expected := "a, b, c"
	if got != expected {
		t.Errorf("joinStrings(%v, %q) = %q, want %q", input, ", ", got, expected)
	}
}

func TestExtractRecords(t *testing.T) {
	events := []map[string]interface{}{
		{"Event": "SparkListenerTaskEnd", "Stage ID": 1, "Task Metrics": map[string]interface{}{
			"Shuffle Read Metrics": map[string]interface{}{"Total Records Read": 100},
		}},
		{"Event": "SparkListenerTaskEnd", "Stage ID": 1, "Task Metrics": map[string]interface{}{
			"Shuffle Read Metrics": map[string]interface{}{"Total Records Read": 200},
		}},
	}
	got := extractRecords(events)
	if len(got) != 2 {
		t.Errorf("len(extractRecords) = %d, want 2", len(got))
	}
	if got[0] != 100 || got[1] != 200 {
		t.Errorf("extractRecords() = %v, want [100 200]", got)
	}
}
