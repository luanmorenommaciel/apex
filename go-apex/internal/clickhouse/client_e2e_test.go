//go:build e2e

package clickhouse

import (
	"context"
	"encoding/json"
	"net"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

// mockClickHouseResponse builds a JSON response matching ClickHouse HTTP JSON format.
func mockClickHouseResponse(meta []map[string]interface{}, data []map[string]interface{}, rows int64) []byte {
	resp := map[string]interface{}{
		"meta": meta,
		"data": data,
		"rows": rows,
	}
	b, _ := json.Marshal(resp)
	return b
}

// newMockServer creates an httptest.Server that simulates ClickHouse HTTP endpoint.
func newMockServer(t *testing.T, handler http.HandlerFunc) *httptest.Server {
	ts := httptest.NewServer(handler)
	t.Cleanup(func() { ts.Close() })
	return ts
}

// TestNewClient_E2E verifies that NewClient creates a valid Client and Close is a no-op.
func TestNewClient_E2E(t *testing.T) {
	cfg := Config{
		Host:     "127.0.0.1",
		Port:     8123,
		Database: "test_db",
		User:     "test_user",
		Password: "test_pass",
	}

	client, err := NewClient(cfg)
	if err != nil {
		t.Fatalf("NewClient() error = %v", err)
	}
	if client == nil {
		t.Fatal("NewClient() returned nil")
	}
	if client.Database() != "test_db" {
		t.Errorf("Database() = %q, want %q", client.Database(), "test_db")
	}

	// Close should be a no-op and not panic.
	client.Close()
}

// TestQuery_E2E verifies Query parses a ClickHouse JSON response correctly.
func TestQuery_E2E(t *testing.T) {
	meta := []map[string]interface{}{
		{"name": "id", "type": "Int64"},
		{"name": "name", "type": "String"},
	}
	data := []map[string]interface{}{
		{"id": 1, "name": "Alice"},
		{"id": 2, "name": "Bob"},
	}
	mockBody := mockClickHouseResponse(meta, data, 2)

	ts := newMockServer(t, func(w http.ResponseWriter, r *http.Request) {
		// Verify query parameters expected by the client.
		if r.Method != http.MethodPost {
			t.Errorf("expected POST, got %s", r.Method)
		}
		q := r.URL.Query()
		if q.Get("database") != "spark_observability" {
			t.Errorf("expected database=spark_observability, got %s", q.Get("database"))
		}
		if q.Get("default_format") != "JSON" {
			t.Errorf("expected default_format=JSON, got %s", q.Get("default_format"))
		}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write(mockBody)
	})

	cfg := DefaultConfig()
	cfg.Host = ts.Listener.Addr().(*net.TCPAddr).IP.String()
	cfg.Port = ts.Listener.Addr().(*net.TCPAddr).Port

	client, err := NewClient(cfg)
	if err != nil {
		t.Fatalf("NewClient() error = %v", err)
	}
	defer client.Close()

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	res, err := client.Query(ctx, "SELECT id, name FROM users")
	if err != nil {
		t.Fatalf("Query() error = %v", err)
	}
	if res == nil {
		t.Fatal("Query() returned nil")
	}
	if res.Rows != 2 {
		t.Errorf("Rows = %d, want 2", res.Rows)
	}
	if len(res.Meta) != 2 {
		t.Errorf("len(Meta) = %d, want 2", len(res.Meta))
	}
	if len(res.Data) != 2 {
		t.Errorf("len(Data) = %d, want 2", len(res.Data))
	}

	// Verify first row values.
	first := res.Data[0]
	if ToInt64(first["id"]) != 1 {
		t.Errorf("first row id = %v, want 1", first["id"])
	}
	if ToString(first["name"]) != "Alice" {
		t.Errorf("first row name = %v, want Alice", first["name"])
	}
}

// TestQueryRow_E2E verifies QueryRow returns a single row as a slice of values.
func TestQueryRow_E2E(t *testing.T) {
	meta := []map[string]interface{}{
		{"name": "job_id", "type": "String"},
		{"name": "stage_id", "type": "Int64"},
		{"name": "task_count", "type": "Int64"},
	}
	data := []map[string]interface{}{
		{"job_id": "app-123", "stage_id": 5, "task_count": 42},
	}
	mockBody := mockClickHouseResponse(meta, data, 1)

	ts := newMockServer(t, func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write(mockBody)
	})

	cfg := DefaultConfig()
	cfg.Host = ts.Listener.Addr().(*net.TCPAddr).IP.String()
	cfg.Port = ts.Listener.Addr().(*net.TCPAddr).Port

	client, err := NewClient(cfg)
	if err != nil {
		t.Fatalf("NewClient() error = %v", err)
	}
	defer client.Close()

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	row, err := client.QueryRow(ctx, "SELECT job_id, stage_id, task_count FROM spark_tasks LIMIT 1")
	if err != nil {
		t.Fatalf("QueryRow() error = %v", err)
	}
	if row == nil {
		t.Fatal("QueryRow() returned nil")
	}
	if len(row) != 3 {
		t.Fatalf("len(row) = %d, want 3", len(row))
	}

	if ToString(row[0]) != "app-123" {
		t.Errorf("row[0] = %v, want app-123", row[0])
	}
	if ToInt64(row[1]) != 5 {
		t.Errorf("row[1] = %v, want 5", row[1])
	}
	if ToInt64(row[2]) != 42 {
		t.Errorf("row[2] = %v, want 42", row[2])
	}
}

// TestQueryHTTP_E2E verifies QueryHTTP returns raw rows as maps.
func TestQueryHTTP_E2E(t *testing.T) {
	meta := []map[string]interface{}{
		{"name": "stage_id", "type": "Int64"},
		{"name": "avg_duration", "type": "Float64"},
		{"name": "max_duration", "type": "Float64"},
	}
	data := []map[string]interface{}{
		{"stage_id": 1, "avg_duration": 150.5, "max_duration": 300.0},
		{"stage_id": 2, "avg_duration": 80.25, "max_duration": 120.0},
	}
	mockBody := mockClickHouseResponse(meta, data, 2)

	ts := newMockServer(t, func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write(mockBody)
	})

	cfg := DefaultConfig()
	cfg.Host = ts.Listener.Addr().(*net.TCPAddr).IP.String()
	cfg.Port = ts.Listener.Addr().(*net.TCPAddr).Port

	client, err := NewClient(cfg)
	if err != nil {
		t.Fatalf("NewClient() error = %v", err)
	}
	defer client.Close()

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	rows, err := client.QueryHTTP(ctx, "SELECT stage_id, avg_duration, max_duration FROM stage_stats")
	if err != nil {
		t.Fatalf("QueryHTTP() error = %v", err)
	}
	if rows == nil {
		t.Fatal("QueryHTTP() returned nil")
	}
	if len(rows) != 2 {
		t.Fatalf("len(rows) = %d, want 2", len(rows))
	}

	// Verify first row.
	first := rows[0]
	if ToInt64(first["stage_id"]) != 1 {
		t.Errorf("first stage_id = %v, want 1", first["stage_id"])
	}
	if ToFloat64(first["avg_duration"]) != 150.5 {
		t.Errorf("first avg_duration = %v, want 150.5", first["avg_duration"])
	}
	if ToFloat64(first["max_duration"]) != 300.0 {
		t.Errorf("first max_duration = %v, want 300.0", first["max_duration"])
	}

	// Verify second row.
	second := rows[1]
	if ToInt64(second["stage_id"]) != 2 {
		t.Errorf("second stage_id = %v, want 2", second["stage_id"])
	}
}

// TestQueryWithParams_E2E verifies QueryWithParams sends named parameters via HTTP query string.
func TestQueryWithParams_E2E(t *testing.T) {
	meta := []map[string]interface{}{
		{"name": "result", "type": "String"},
	}
	data := []map[string]interface{}{
		{"result": "param_ok"},
	}
	mockBody := mockClickHouseResponse(meta, data, 1)

	var capturedParams map[string]string
	ts := newMockServer(t, func(w http.ResponseWriter, r *http.Request) {
		q := r.URL.Query()
		capturedParams = make(map[string]string)
		for k, v := range q {
			if len(v) > 0 {
				capturedParams[k] = v[0]
			}
		}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write(mockBody)
	})

	cfg := DefaultConfig()
	cfg.Host = ts.Listener.Addr().(*net.TCPAddr).IP.String()
	cfg.Port = ts.Listener.Addr().(*net.TCPAddr).Port

	client, err := NewClient(cfg)
	if err != nil {
		t.Fatalf("NewClient() error = %v", err)
	}
	defer client.Close()

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	params := map[string]interface{}{
		"job_id":    "app-456",
		"threshold": 1.5,
		"limit":     10,
		"active":    true,
	}

	res, err := client.QueryWithParams(ctx, "SELECT 'param_ok' as result", params)
	if err != nil {
		t.Fatalf("QueryWithParams() error = %v", err)
	}
	if res == nil {
		t.Fatal("QueryWithParams() returned nil")
	}
	if res.Rows != 1 {
		t.Errorf("Rows = %d, want 1", res.Rows)
	}

	// Verify parameters were sent correctly.
	if capturedParams["param_job_id"] != "app-456" {
		t.Errorf("param_job_id = %q, want app-456", capturedParams["param_job_id"])
	}
	if capturedParams["param_threshold"] != "1.5" {
		t.Errorf("param_threshold = %q, want 1.5", capturedParams["param_threshold"])
	}
	if capturedParams["param_limit"] != "10" {
		t.Errorf("param_limit = %q, want 10", capturedParams["param_limit"])
	}
	if capturedParams["param_active"] != "true" {
		t.Errorf("param_active = %q, want true", capturedParams["param_active"])
	}
}

// TestQueryHTTP_EmptyResult_E2E verifies QueryHTTP handles empty result sets gracefully.
func TestQueryHTTP_EmptyResult_E2E(t *testing.T) {
	meta := []map[string]interface{}{
		{"name": "id", "type": "Int64"},
	}
	data := []map[string]interface{}{}
	mockBody := mockClickHouseResponse(meta, data, 0)

	ts := newMockServer(t, func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write(mockBody)
	})

	cfg := DefaultConfig()
	cfg.Host = ts.Listener.Addr().(*net.TCPAddr).IP.String()
	cfg.Port = ts.Listener.Addr().(*net.TCPAddr).Port

	client, err := NewClient(cfg)
	if err != nil {
		t.Fatalf("NewClient() error = %v", err)
	}
	defer client.Close()

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	rows, err := client.QueryHTTP(ctx, "SELECT id FROM empty_table")
	if err != nil {
		t.Fatalf("QueryHTTP() error = %v", err)
	}
	if rows == nil {
		t.Fatal("QueryHTTP() returned nil for empty result")
	}
	if len(rows) != 0 {
		t.Errorf("len(rows) = %d, want 0", len(rows))
	}
}

// TestQuery_HTTPError_E2E verifies Query handles non-200 HTTP responses correctly.
func TestQuery_HTTPError_E2E(t *testing.T) {
	ts := newMockServer(t, func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte("Internal Server Error"))
	})

	cfg := DefaultConfig()
	cfg.Host = ts.Listener.Addr().(*net.TCPAddr).IP.String()
	cfg.Port = ts.Listener.Addr().(*net.TCPAddr).Port

	client, err := NewClient(cfg)
	if err != nil {
		t.Fatalf("NewClient() error = %v", err)
	}
	defer client.Close()

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	res, err := client.Query(ctx, "SELECT 1")
	if err == nil {
		t.Fatal("Query() expected error for HTTP 500, got nil")
	}
	if res != nil {
		t.Errorf("Query() expected nil result for HTTP 500, got %v", res)
	}
	expectedErr := "clickhouse returned HTTP 500"
	if len(err.Error()) < len(expectedErr) || err.Error()[:len(expectedErr)] != expectedErr {
		t.Errorf("Query() error = %q, expected prefix %q", err.Error(), expectedErr)
	}
}

// TestQueryRow_EmptyResult_E2E verifies QueryRow returns nil for empty result sets.
func TestQueryRow_EmptyResult_E2E(t *testing.T) {
	meta := []map[string]interface{}{
		{"name": "id", "type": "Int64"},
	}
	data := []map[string]interface{}{}
	mockBody := mockClickHouseResponse(meta, data, 0)

	ts := newMockServer(t, func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write(mockBody)
	})

	cfg := DefaultConfig()
	cfg.Host = ts.Listener.Addr().(*net.TCPAddr).IP.String()
	cfg.Port = ts.Listener.Addr().(*net.TCPAddr).Port

	client, err := NewClient(cfg)
	if err != nil {
		t.Fatalf("NewClient() error = %v", err)
	}
	defer client.Close()

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	row, err := client.QueryRow(ctx, "SELECT id FROM empty_table")
	if err != nil {
		t.Fatalf("QueryRow() error = %v", err)
	}
	if row != nil {
		t.Errorf("QueryRow() = %v, want nil for empty result", row)
	}
}
