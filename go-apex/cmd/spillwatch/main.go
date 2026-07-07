package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"os"

	"github.com/apex/go-apex/internal/clickhouse"
	"github.com/apex/go-apex/internal/watcher"
)

func main() {
	var appID string
	flag.StringVar(&appID, "app-id", "", "Spark application ID (required)")
	flag.Parse()

	if appID == "" {
		fmt.Fprintln(os.Stderr, "Usage: spillwatch -app-id=<app_id>")
		os.Exit(1)
	}

	cfg := clickhouse.DefaultConfig()
	client, err := clickhouse.NewClient(cfg)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to connect to ClickHouse: %v\n", err)
		os.Exit(1)
	}
	defer client.Close()

	// Query job data
	query := fmt.Sprintf("SELECT * FROM spark_tasks WHERE app_id = '%s'", appID)
	ctx := context.Background()
	rows, err := client.QueryHTTP(ctx, query)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Query failed: %v\n", err)
		os.Exit(1)
	}

	jobData := map[string]interface{}{"tasks": rows}
	w := watcher.NewSpillWatcher()
	finding, err := w.Watch(jobData)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Watch failed: %v\n", err)
		os.Exit(1)
	}

	data, err := json.MarshalIndent(finding, "", "  ")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to marshal output: %v\n", err)
		os.Exit(1)
	}
	fmt.Println(string(data))
}
