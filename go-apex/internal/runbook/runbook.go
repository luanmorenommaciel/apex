// Package runbook defines runbook schemas for structured anomaly correction.
package runbook

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"
)

// Severity represents anomaly severity.
type Severity string

const (
	Low      Severity = "LOW"
	Medium   Severity = "MEDIUM"
	High     Severity = "HIGH"
	Critical Severity = "CRITICAL"
)

// CodeExample represents a code correction snippet.
type CodeExample struct {
	Language    string `json:"language"`
	Snippet     string `json:"snippet"`
	Description string `json:"description,omitempty"`
}

// Validation defines how to validate a correction.
type Validation struct {
	Query          string `json:"query,omitempty"`
	ExpectedMetric string `json:"expected_metric,omitempty"`
	ManualStep     string `json:"manual_step,omitempty"`
	TimeoutSeconds int    `json:"timeout_seconds"`
}

// ExpectedImpact describes the expected impact of applying a runbook.
type ExpectedImpact struct {
	PerformanceGain        string `json:"performance_gain,omitempty"`
	CostReduction          string `json:"cost_reduction,omitempty"`
	ReliabilityImprovement string `json:"reliability_improvement,omitempty"`
	Summary                string `json:"summary"`
}

// Step represents a single correction step.
type Step struct {
	Order       int          `json:"order"`
	Action      string       `json:"action"`
	Details     string       `json:"details"`
	CodeExample *CodeExample `json:"code_example,omitempty"`
	Validation  *Validation  `json:"validation,omitempty"`
}

// Trigger defines conditions that activate a runbook.
type Trigger struct {
	AnomalyType   string   `json:"anomaly_type"`
	Conditions    []string `json:"conditions,omitempty"`
	MinConfidence float64  `json:"min_confidence"`
}

// Runbook is a structured correction playbook for Spark anomalies.
type Runbook struct {
	ID             string         `json:"id"`
	Name           string         `json:"name"`
	Version        string         `json:"version"`
	Summary        string         `json:"summary"`
	Trigger        Trigger        `json:"trigger"`
	Steps          []Step         `json:"steps"`
	ExpectedImpact *ExpectedImpact `json:"expected_impact,omitempty"`
	CodeTemplate   string         `json:"code_template,omitempty"`
	Tags           []string       `json:"tags,omitempty"`
	Severity       Severity       `json:"severity"`
}

// LoadRunbook loads and validates a runbook JSON from disk.
func LoadRunbook(path string) (*Runbook, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read runbook: %w", err)
	}
	var rb Runbook
	if err := json.Unmarshal(data, &rb); err != nil {
		return nil, fmt.Errorf("parse runbook: %w", err)
	}
	if err := validateRunbook(&rb); err != nil {
		return nil, fmt.Errorf("validate runbook: %w", err)
	}
	return &rb, nil
}

// SaveRunbook serializes a runbook to JSON on disk.
func SaveRunbook(rb *Runbook, path string) error {
	data, err := json.MarshalIndent(rb, "", "  ")
	if err != nil {
		return fmt.Errorf("marshal runbook: %w", err)
	}
	if err := os.WriteFile(path, data, 0644); err != nil {
		return fmt.Errorf("write runbook: %w", err)
	}
	return nil
}

func validateRunbook(rb *Runbook) error {
	if rb.ID == "" {
		return fmt.Errorf("id is required")
	}
	if len(rb.Steps) == 0 {
		return fmt.Errorf("at least one step is required")
	}
	orders := make(map[int]bool)
	for _, s := range rb.Steps {
		if orders[s.Order] {
			return fmt.Errorf("duplicate step order: %d", s.Order)
		}
		orders[s.Order] = true
	}
	for i := 1; i <= len(rb.Steps); i++ {
		if !orders[i] {
			return fmt.Errorf("missing step order: %d", i)
		}
	}
	return nil
}

// Manager gerencia o carregamento e cache de runbooks.
type Manager struct {
	runbooksDir string
	mu          sync.RWMutex
	cache       map[string]*Runbook // key: filename
}

// NewManager cria um novo Manager de runbooks.
func NewManager(runbooksDir string) *Manager {
	if runbooksDir == "" {
		runbooksDir = filepath.Join("runbooks")
	}
	return &Manager{
		runbooksDir: runbooksDir,
		cache:       make(map[string]*Runbook),
	}
}

// anomalyToFilename mapeia tipos de anomalia para arquivos de runbook.
func anomalyToFilename(anomalyType string) string {
	mapping := map[string]string{
		"SKEW":             "skew_on_join.json",
		"SPILL":            "spill_to_disk.json",
		"GC_PRESSURE":      "spill_to_disk.json",
		"OOM":              "spill_to_disk.json",
		"data_skew":        "skew_on_join.json",
		"spill":            "spill_to_disk.json",
		"spill_to_disk":    "spill_to_disk.json",
		"memory_pressure":  "spill_to_disk.json",
		"gc_thrash":        "spill_to_disk.json",
	}
	return mapping[anomalyType]
}

// Load carrega um runbook do disco (ou cache) para o tipo de anomalia dado.
func (m *Manager) Load(anomalyType string) (*Runbook, error) {
	filename := anomalyToFilename(anomalyType)
	if filename == "" {
		return nil, fmt.Errorf("nenhum runbook mapeado para anomalia: %s", anomalyType)
	}

	m.mu.RLock()
	if rb, ok := m.cache[filename]; ok {
		m.mu.RUnlock()
		return rb, nil
	}
	m.mu.RUnlock()

	path := filepath.Join(m.runbooksDir, filename)
	data, err := os.ReadFile(path)
	if err != nil {
		if os.IsNotExist(err) {
			return nil, fmt.Errorf("runbook não encontrado: %s", path)
		}
		return nil, fmt.Errorf("erro ao ler runbook %s: %w", path, err)
	}

	var rb Runbook
	if err := json.Unmarshal(data, &rb); err != nil {
		return nil, fmt.Errorf("erro ao parsear runbook %s: %w", path, err)
	}
	if err := validateRunbook(&rb); err != nil {
		return nil, fmt.Errorf("runbook %s inválido: %w", path, err)
	}

	m.mu.Lock()
	m.cache[filename] = &rb
	m.mu.Unlock()

	return &rb, nil
}

// GetAllCached retorna todos os runbooks atualmente em cache.
func (m *Manager) GetAllCached() []*Runbook {
	m.mu.RLock()
	defer m.mu.RUnlock()
	var out []*Runbook
	for _, rb := range m.cache {
		out = append(out, rb)
	}
	return out
}

// ClearCache limpa o cache de runbooks.
func (m *Manager) ClearCache() {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.cache = make(map[string]*Runbook)
}

// ValidateIDPrefix verifica se o ID do runbook tem o prefixo correto.
func ValidateIDPrefix(id string) error {
	if !strings.HasPrefix(id, "runbook-") {
		return fmt.Errorf("id do runbook deve começar com 'runbook-': %s", id)
	}
	return nil
}
