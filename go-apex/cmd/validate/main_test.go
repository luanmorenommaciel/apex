package main

import (
	"testing"
)

func TestSplitLines(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected []string
	}{
		{"single", "hello", []string{"hello"}},
		{"multiple", "a\nb\nc", []string{"a", "b", "c"}},
		{"trailing newline", "a\n", []string{"a"}},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := splitLines(tt.input)
			if len(got) != len(tt.expected) {
				t.Fatalf("splitLines(%q) = %v, want %v", tt.input, got, tt.expected)
			}
			for i := range got {
				if got[i] != tt.expected[i] {
					t.Errorf("splitLines[%d] = %q, want %q", i, got[i], tt.expected[i])
				}
			}
		})
	}
}

func TestTrimSpace(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected string
	}{
		{"no spaces", "hello", "hello"},
		{"leading", "  hello", "hello"},
		{"trailing", "hello  ", "hello"},
		{"both", "  hello  ", "hello"},
		{"tabs", "\thello\t", "hello"},
		{"empty", "", ""},
		{"only spaces", "   ", ""},
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
