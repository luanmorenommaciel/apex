package validator

import (
	"math"
	"reflect"
	"testing"
)

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

func TestToInt(t *testing.T) {
	tests := []struct {
		name     string
		input    interface{}
		expected int
	}{
		{"nil", nil, 0},
		{"int", 42, 42},
		{"float64", 3.9, 3},
		{"string", "123", 123},
		{"invalid string", "abc", 0},
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

func TestToBool(t *testing.T) {
	tests := []struct {
		name     string
		input    interface{}
		expected bool
	}{
		{"nil", nil, false},
		{"true", true, true},
		{"false", false, false},
		{"string true", "true", true},
		{"string 1", "1", true},
		{"string false", "false", false},
		{"int 1", 1, true},
		{"int 0", 0, false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := toBool(tt.input)
			if got != tt.expected {
				t.Errorf("toBool(%v) = %v, want %v", tt.input, got, tt.expected)
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

func TestDerefString(t *testing.T) {
	s := "hello"
	tests := []struct {
		name     string
		input    *string
		expected string
	}{
		{"nil", nil, ""},
		{"value", &s, "hello"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := derefString(tt.input)
			if got != tt.expected {
				t.Errorf("derefString() = %q, want %q", got, tt.expected)
			}
		})
	}
}

func TestHasIssue(t *testing.T) {
	issues := []string{"a", "b", "c"}
	tests := []struct {
		name     string
		target   string
		expected bool
	}{
		{"exists", "b", true},
		{"missing", "z", false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := hasIssue(issues, tt.target)
			if got != tt.expected {
				t.Errorf("hasIssue(%v, %q) = %v, want %v", issues, tt.target, got, tt.expected)
			}
		})
	}
}

func TestContainsInt(t *testing.T) {
	vals := []int{1, 2, 3}
	tests := []struct {
		name     string
		target   int
		expected bool
	}{
		{"exists", 2, true},
		{"missing", 5, false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := containsInt(vals, tt.target)
			if got != tt.expected {
				t.Errorf("containsInt(%v, %d) = %v, want %v", vals, tt.target, got, tt.expected)
			}
		})
	}
}

func TestStringsContains(t *testing.T) {
	tests := []struct {
		name     string
		s        string
		substr   string
		expected bool
	}{
		{"contains", "hello world", "world", true},
		{"not contains", "hello", "xyz", false},
		{"exact", "abc", "abc", true},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := stringsContains(tt.s, tt.substr)
			if got != tt.expected {
				t.Errorf("stringsContains(%q, %q) = %v, want %v", tt.s, tt.substr, got, tt.expected)
			}
		})
	}
}

func TestIndexOf(t *testing.T) {
	tests := []struct {
		name     string
		s        string
		substr   string
		expected int
	}{
		{"found", "abcdef", "cd", 2},
		{"not found", "abc", "xyz", -1},
		{"empty", "abc", "", 0},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := indexOf(tt.s, tt.substr)
			if got != tt.expected {
				t.Errorf("indexOf(%q, %q) = %d, want %d", tt.s, tt.substr, got, tt.expected)
			}
		})
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

func TestMaxInt(t *testing.T) {
	input := []int{3, 1, 4, 1, 5}
	got := maxInt(input)
	if got != 5 {
		t.Errorf("maxInt(%v) = %d, want %d", input, got, 5)
	}
}

func TestMaxKey(t *testing.T) {
	m := map[int][]map[string]interface{}{
		1: {},
		5: {},
		3: {},
	}
	got := maxKey(m)
	if got != 5 {
		t.Errorf("maxKey() = %d, want %d", got, 5)
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
	})
}
