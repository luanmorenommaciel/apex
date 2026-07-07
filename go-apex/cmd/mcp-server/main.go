package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"strings"

	"github.com/apex/go-apex/pkg/mcp"
)

const mcpVersion = "0.1.0-alpha"

func main() {
	fmt.Fprintln(os.Stderr, "Apex MCP Server starting (stdio transport)")
	fmt.Fprintln(os.Stderr, "Version:", mcpVersion)

	scanner := bufio.NewScanner(os.Stdin)
	for scanner.Scan() {
		line := scanner.Text()
		if line == "" {
			continue
		}
		var req map[string]interface{}
		if err := json.Unmarshal([]byte(line), &req); err != nil {
			sendError(nil, err.Error())
			continue
		}
		method, _ := req["method"].(string)
		id := req["id"]

		params, _ := req["params"].(map[string]interface{})
		if params == nil {
			params = map[string]interface{}{}
		}

		switch method {
		case "query_job":
			handleQueryJob(id, params)
		case "get_recommendations":
			handleGetRecommendations(id, params)
		case "health_check":
			handleHealthCheck(id)
		default:
			sendError(id, "unknown method: "+method)
		}
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintf(os.Stderr, "Scanner error: %v\n", err)
	}
}

func handleQueryJob(id interface{}, params map[string]interface{}) {
	appID, _ := params["app_id"].(string)
	if appID == "" {
		sendError(id, "app_id is required")
		return
	}
	result, err := mcp.QueryJob(appID)
	if err != nil {
		sendError(id, err.Error())
		return
	}
	data, _ := json.MarshalIndent(result, "", "  ")
	sendResult(id, string(data))
}

func handleGetRecommendations(id interface{}, params map[string]interface{}) {
	appID, _ := params["app_id"].(string)
	if appID == "" {
		sendError(id, "app_id is required")
		return
	}
	result, err := mcp.GetRecommendations(appID)
	if err != nil {
		sendError(id, err.Error())
		return
	}
	data, _ := json.MarshalIndent(result, "", "  ")
	sendResult(id, string(data))
}

func handleHealthCheck(id interface{}) {
	status := map[string]interface{}{
		"mcp_version":      mcpVersion,
		"mcp_status":       "healthy",
		"clickhouse_url":     os.Getenv("CLICKHOUSE_URL"),
		"crei_url":          os.Getenv("CREI_URL"),
	}
	if status["clickhouse_url"] == "" {
		status["clickhouse_url"] = "http://localhost:8123"
	}
	if status["crei_url"] == "" {
		status["crei_url"] = "http://localhost:8000"
	}

	// Test ClickHouse
	chStatus := "unavailable"
	if _, err := mcp.QueryJob("health_check"); err == nil {
		chStatus = "connected"
	} else {
		status["clickhouse_status"] = "unavailable: " + err.Error()
	}
	if chStatus == "connected" {
		status["clickhouse_status"] = "connected"
	}
	status["crei_status"] = "not implemented"

	data, _ := json.MarshalIndent(status, "", "  ")
	sendResult(id, string(data))
}

func sendResult(id interface{}, result string) {
	resp := map[string]interface{}{
		"jsonrpc": "2.0",
		"id":      id,
		"result":  result,
	}
	data, _ := json.Marshal(resp)
	fmt.Println(string(data))
}

func sendError(id interface{}, msg string) {
	resp := map[string]interface{}{
		"jsonrpc": "2.0",
		"id":      id,
		"error": map[string]interface{}{
			"code":    -32600,
			"message": msg,
		},
	}
	data, _ := json.Marshal(resp)
	fmt.Println(string(data))
}

func envDefault(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

func containsStr(s, substr string) bool {
	return strings.Contains(s, substr)
}
