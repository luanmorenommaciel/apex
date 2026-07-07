package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"

	"github.com/apex/go-apex/internal/clickhouse"
	"github.com/apex/go-apex/internal/diagnostician"
	"github.com/apex/go-apex/internal/recommender"
)

func main() {
	var (
		appID       string
		runbooksDir string
	)
	flag.StringVar(&appID, "app-id", "", "Spark application ID (required)")
	flag.StringVar(&runbooksDir, "runbooks", "runbooks", "Path to runbooks directory")
	flag.Parse()

	if appID == "" {
		fmt.Fprintln(os.Stderr, "Usage: recommend -app-id=<app_id> [-runbooks=<dir>]")
		os.Exit(1)
	}

	cfg := clickhouse.DefaultConfig()
	d, err := diagnostician.NewDiagnostician(cfg)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to create diagnostician: %v\n", err)
		os.Exit(1)
	}
	defer d.Close()

	reports, err := d.Diagnose(appID)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Diagnosis failed: %v\n", err)
		os.Exit(1)
	}

	rec := recommender.NewRecommender(runbooksDir)
	recommendations := rec.RecommendAll(reports)

	out := map[string]interface{}{
		"app_id":          appID,
		"anomalies":       reports,
		"recommendations": recommendations,
	}
	data, err := json.MarshalIndent(out, "", "  ")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to marshal output: %v\n", err)
		os.Exit(1)
	}
	fmt.Println(string(data))
}
