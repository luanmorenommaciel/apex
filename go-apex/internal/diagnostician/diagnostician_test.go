package diagnostician

import (
	"os"
	"reflect"
	"testing"
)

func TestToInt(t *testing.T) {
	tests := []struct {
		name     string
		input    interface{}
		expected int
	}{
		{"nil", nil, 0},
		{"int", 42, 42},
		{"int64", int64(10), 10},
		{"float64", 3.9, 3},
		{"string valid", "99", 99},
		{"string invalid", "abc", 0},
		{"uint8", uint8(5), 5},
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
		{"string valid", "1.5", 1.5},
		{"string invalid", "xyz", 0},
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

func TestToStringSlice(t *testing.T) {
	tests := []struct {
		name     string
		input    interface{}
		expected []string
	}{
		{"nil", nil, nil},
		{"interface slice", []interface{}{"a", "b"}, []string{"a", "b"}},
		{"string", "hello", []string{"hello"}},
		{"invalid", 42, nil},
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

func TestContains(t *testing.T) {
	tests := []struct {
		name     string
		s        string
		substr   string
		expected bool
	}{
		{"contains", "hello world", "world", true},
		{"not contains", "hello", "xyz", false},
		{"empty substr", "hello", "", false},
		{"exact match", "hello", "hello", true},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := contains(tt.s, tt.substr)
			if got != tt.expected {
				t.Errorf("contains(%q, %q) = %v, want %v", tt.s, tt.substr, got, tt.expected)
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
		{"not found", "abcdef", "xyz", -1},
		{"empty substr", "abc", "", 0},
		{"at start", "abc", "ab", 0},
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

func TestMin(t *testing.T) {
	tests := []struct {
		name     string
		a, b     int
		expected int
	}{
		{"a smaller", 1, 5, 1},
		{"b smaller", 10, 3, 3},
		{"equal", 4, 4, 4},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := min(tt.a, tt.b)
			if got != tt.expected {
				t.Errorf("min(%d, %d) = %d, want %d", tt.a, tt.b, got, tt.expected)
			}
		})
	}
}

func TestParseEnvFloat(t *testing.T) {
	t.Run("env set valid", func(t *testing.T) {
		t.Setenv("TEST_FLOAT", "3.14")
		got := parseEnvFloat("TEST_FLOAT", 1.0)
		if got != 3.14 {
			t.Errorf("parseEnvFloat() = %f, want %f", got, 3.14)
		}
	})

	t.Run("env set invalid", func(t *testing.T) {
		t.Setenv("TEST_FLOAT", "abc")
		got := parseEnvFloat("TEST_FLOAT", 2.0)
		if got != 2.0 {
			t.Errorf("parseEnvFloat() = %f, want %f", got, 2.0)
		}
	})

	t.Run("env not set", func(t *testing.T) {
		os.Unsetenv("TEST_FLOAT_MISSING")
		got := parseEnvFloat("TEST_FLOAT_MISSING", 5.0)
		if got != 5.0 {
			t.Errorf("parseEnvFloat() = %f, want %f", got, 5.0)
		}
	})
}
