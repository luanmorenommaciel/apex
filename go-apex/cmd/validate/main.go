package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"

	"github.com/apex/go-apex/internal/models"
	"github.com/apex/go-apex/internal/validator"
)

func main() {
	var (
		scenarioPath string
		logPath      string
	)
	flag.StringVar(&scenarioPath, "scenario", "", "Path to scenario YAML (required)")
	flag.StringVar(&logPath, "log", "", "Path to event log file or directory (required)")
	flag.Parse()

	if scenarioPath == "" || logPath == "" {
		fmt.Fprintln(os.Stderr, "Usage: validate -scenario=<path> -log=<path>")
		os.Exit(1)
	}

	// Read scenario
	scenarioData, err := os.ReadFile(scenarioPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to read scenario: %v\n", err)
		os.Exit(1)
	}
	var scenario map[string]interface{}
	// We skip yaml parsing here; store raw JSON-like for now
	if err := json.Unmarshal(scenarioData, &scenario); err != nil {
		scenario = map[string]interface{}{"raw": string(scenarioData)}
	}

	// Read events (ndjson)
	logData, err := os.ReadFile(logPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to read log: %v\n", err)
		os.Exit(1)
	}
	var events []map[string]interface{}
	for _, line := range splitLines(string(logData)) {
		line = trimSpace(line)
		if line == "" {
			continue
		}
		var event map[string]interface{}
		if err := json.Unmarshal([]byte(line), &event); err == nil {
			events = append(events, event)
		}
	}

	bundle := &models.EvidenceBundle{
		Events:   events,
		Scenario: scenario,
	}

	v := validator.NewEvidenceValidator(bundle)
	result := v.Validate()

	data, err := json.MarshalIndent(result, "", "  ")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to marshal output: %v\n", err)
		os.Exit(1)
	}
	fmt.Println(string(data))
}

func splitLines(s string) []string {
	var lines []string
	start := 0
	for i := 0; i < len(s); i++ {
		if s[i] == '\n' {
			lines = append(lines, s[start:i])
			start = i + 1
		}
	}
	if start < len(s) {
		lines = append(lines, s[start:])
	}
	return lines
}

func trimSpace(s string) string {
	start := 0
	for start < len(s) && (s[start] == ' ' || s[start] == '\t' || s[start] == '\r' || s[start] == '\n') {
		start++
	}
	end := len(s)
	for end > start && (s[end-1] == ' ' || s[end-1] == '\t' || s[end-1] == '\r' || s[end-1] == '\n') {
		end--
	}
	return s[start:end]
}
