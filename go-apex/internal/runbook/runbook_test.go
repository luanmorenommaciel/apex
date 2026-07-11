package runbook

import (
	"os"
	"path/filepath"
	"testing"
)

func TestValidateRunbook(t *testing.T) {
	tests := []struct {
		name    string
		rb      *Runbook
		wantErr bool
	}{
		{
			name: "valid",
			rb: &Runbook{
				ID: "runbook-test",
				Steps: []Step{
					{Order: 1, Action: "step1"},
				},
			},
			wantErr: false,
		},
		{
			name:    "missing id",
			rb:      &Runbook{Steps: []Step{{Order: 1, Action: "step1"}}},
			wantErr: true,
		},
		{
			name:    "no steps",
			rb:      &Runbook{ID: "runbook-test"},
			wantErr: true,
		},
		{
			name: "duplicate order",
			rb: &Runbook{
				ID: "runbook-test",
				Steps: []Step{
					{Order: 1, Action: "step1"},
					{Order: 1, Action: "step2"},
				},
			},
			wantErr: true,
		},
		{
			name: "missing order",
			rb: &Runbook{
				ID: "runbook-test",
				Steps: []Step{
					{Order: 1, Action: "step1"},
					{Order: 3, Action: "step3"},
				},
			},
			wantErr: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := validateRunbook(tt.rb)
			if (err != nil) != tt.wantErr {
				t.Errorf("validateRunbook() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestAnomalyToFilename(t *testing.T) {
	tests := []struct {
		input    string
		expected string
	}{
		{"SKEW", "skew_on_join.json"},
		{"SPILL", "spill_to_disk.json"},
		{"OOM", "spill_to_disk.json"},
		{"data_skew", "skew_on_join.json"},
		{"UNKNOWN", ""},
	}
	for _, tt := range tests {
		t.Run(tt.input, func(t *testing.T) {
			got := anomalyToFilename(tt.input)
			if got != tt.expected {
				t.Errorf("anomalyToFilename(%q) = %q, want %q", tt.input, got, tt.expected)
			}
		})
	}
}

func TestValidateIDPrefix(t *testing.T) {
	tests := []struct {
		name    string
		id      string
		wantErr bool
	}{
		{"valid", "runbook-abc", false},
		{"invalid", "abc", true},
		{"empty", "", true},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ValidateIDPrefix(tt.id)
			if (err != nil) != tt.wantErr {
				t.Errorf("ValidateIDPrefix(%q) error = %v, wantErr %v", tt.id, err, tt.wantErr)
			}
		})
	}
}

func TestSaveAndLoadRunbook(t *testing.T) {
	tmpDir := t.TempDir()
	path := filepath.Join(tmpDir, "test_runbook.json")

	rb := &Runbook{
		ID:      "runbook-test",
		Name:    "Test Runbook",
		Version: "1.0",
		Summary: "Summary",
		Trigger: Trigger{AnomalyType: "SKEW", MinConfidence: 0.8},
		Steps: []Step{
			{Order: 1, Action: "Check metrics", Details: "details"},
		},
		Severity: High,
	}

	t.Run("save", func(t *testing.T) {
		err := SaveRunbook(rb, path)
		if err != nil {
			t.Fatalf("SaveRunbook() error = %v", err)
		}
		_, err = os.Stat(path)
		if err != nil {
			t.Fatalf("runbook file not created: %v", err)
		}
	})

	t.Run("load", func(t *testing.T) {
		loaded, err := LoadRunbook(path)
		if err != nil {
			t.Fatalf("LoadRunbook() error = %v", err)
		}
		if loaded.ID != rb.ID {
			t.Errorf("loaded.ID = %q, want %q", loaded.ID, rb.ID)
		}
		if loaded.Name != rb.Name {
			t.Errorf("loaded.Name = %q, want %q", loaded.Name, rb.Name)
		}
		if len(loaded.Steps) != 1 {
			t.Errorf("len(loaded.Steps) = %d, want %d", len(loaded.Steps), 1)
		}
	})

	t.Run("load invalid", func(t *testing.T) {
		badPath := filepath.Join(tmpDir, "bad.json")
		os.WriteFile(badPath, []byte("not json"), 0644)
		_, err := LoadRunbook(badPath)
		if err == nil {
			t.Error("LoadRunbook() expected error for invalid JSON")
		}
	})
}
