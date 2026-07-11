package clickhouse

import (
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
		{"int64", int64(99), "99"},
		{"float64", 3.14, "3.14"},
		{"bool", true, "true"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := ToString(tt.input)
			if got != tt.expected {
				t.Errorf("ToString(%v) = %q, want %q", tt.input, got, tt.expected)
			}
		})
	}
}

func TestToInt64(t *testing.T) {
	tests := []struct {
		name     string
		input    interface{}
		expected int64
	}{
		{"nil", nil, 0},
		{"int64", int64(10), 10},
		{"int", 5, 5},
		{"int32", int32(7), 7},
		{"float64", 3.9, 3},
		{"string valid", "123", 123},
		{"string invalid", "abc", 0},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := ToInt64(tt.input)
			if got != tt.expected {
				t.Errorf("ToInt64(%v) = %d, want %d", tt.input, got, tt.expected)
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
		{"int64", int64(4), 4.0},
		{"int", 8, 8.0},
		{"string valid", "1.5", 1.5},
		{"string invalid", "xyz", 0},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := ToFloat64(tt.input)
			if got != tt.expected {
				t.Errorf("ToFloat64(%v) = %f, want %f", tt.input, got, tt.expected)
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
		{"empty slice", []interface{}{}, []string{}},
		{"mixed", []interface{}{"a", 1, true}, []string{"a", "1", "true"}},
		{"not slice", "hello", nil},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := ToStringSlice(tt.input)
			if !reflect.DeepEqual(got, tt.expected) {
				t.Errorf("ToStringSlice(%v) = %v, want %v", tt.input, got, tt.expected)
			}
		})
	}
}

func TestGetValue(t *testing.T) {
	columns := []string{"id", "name", "score"}
	row := []interface{}{1, "alice", 9.5}

	tests := []struct {
		name     string
		col      string
		expected interface{}
	}{
		{"existing col", "name", "alice"},
		{"missing col", "missing", nil},
		{"out of bounds", "score", 9.5},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := GetValue(row, columns, tt.col)
			if got != tt.expected {
				t.Errorf("GetValue(row, columns, %q) = %v, want %v", tt.col, got, tt.expected)
			}
		})
	}
}

func TestGetString(t *testing.T) {
	columns := []string{"name"}
	row := []interface{}{"bob"}
	got := GetString(row, columns, "name")
	if got != "bob" {
		t.Errorf("GetString() = %q, want %q", got, "bob")
	}
}

func TestGetInt64(t *testing.T) {
	columns := []string{"count"}
	row := []interface{}{42}
	got := GetInt64(row, columns, "count")
	if got != 42 {
		t.Errorf("GetInt64() = %d, want %d", got, 42)
	}
}

func TestGetFloat64(t *testing.T) {
	columns := []string{"rate"}
	row := []interface{}{1.23}
	got := GetFloat64(row, columns, "rate")
	if got != 1.23 {
		t.Errorf("GetFloat64() = %f, want %f", got, 1.23)
	}
}

func TestGetStringSlice(t *testing.T) {
	columns := []string{"tags"}
	row := []interface{}{[]interface{}{"a", "b"}}
	got := GetStringSlice(row, columns, "tags")
	expected := []string{"a", "b"}
	if !reflect.DeepEqual(got, expected) {
		t.Errorf("GetStringSlice() = %v, want %v", got, expected)
	}
}

func TestJSONMapString(t *testing.T) {
	input := map[string]interface{}{"a": 1, "b": "hello"}
	got := JSONMapString(input)
	expected := map[string]string{"a": "1", "b": "hello"}
	if !reflect.DeepEqual(got, expected) {
		t.Errorf("JSONMapString() = %v, want %v", got, expected)
	}
}

func TestJSONMapInt64(t *testing.T) {
	input := map[string]interface{}{"x": 10, "y": "20"}
	got := JSONMapInt64(input)
	expected := map[string]int64{"x": 10, "y": 20}
	if !reflect.DeepEqual(got, expected) {
		t.Errorf("JSONMapInt64() = %v, want %v", got, expected)
	}
}

func TestJSONMapFloat64(t *testing.T) {
	input := map[string]interface{}{"pi": 3.14, "e": "2.71"}
	got := JSONMapFloat64(input)
	expected := map[string]float64{"pi": 3.14, "e": 2.71}
	if !reflect.DeepEqual(got, expected) {
		t.Errorf("JSONMapFloat64() = %v, want %v", got, expected)
	}
}
