package clickhouse

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"
)

// Config holds ClickHouse connection parameters.
type Config struct {
	Host     string
	Port     int
	Database string
	User     string
	Password string
}

// DefaultConfig returns a Config populated from environment variables.
func DefaultConfig() Config {
	port, _ := strconv.Atoi(os.Getenv("CLICKHOUSE_PORT"))
	if port == 0 {
		port = 8123
	}
	return Config{
		Host:     getEnv("CLICKHOUSE_HOST", "spv0-clickhouse"),
		Port:     port,
		Database: getEnv("CLICKHOUSE_DATABASE", "spark_observability"),
		User:     getEnv("CLICKHOUSE_USER", "spv0"),
		Password: getEnv("CLICKHOUSE_PASSWORD", "spv0clickhouse123"),
	}
}

func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

// JSONResponse mirrors the structure returned by ClickHouse HTTP JSON format.
type JSONResponse struct {
	Meta []struct {
		Name string `json:"name"`
		Type string `json:"type"`
	} `json:"meta"`
	Data []map[string]interface{} `json:"data"`
	Rows int64                    `json:"rows"`
}

// Client is a lightweight HTTP client for ClickHouse queries returning JSON.
type Client struct {
	cfg    Config
	client *http.Client
}

// NewClient creates a new ClickHouse HTTP client.
func NewClient(cfg Config) (*Client, error) {
	return &Client{
		cfg: cfg,
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
	}, nil
}

// Database returns the configured database name.
func (c *Client) Database() string {
	return c.cfg.Database
}

// Close is a no-op for the HTTP client; kept for API compatibility.
func (c *Client) Close() {}

// queryInternal performs the HTTP request and decodes the JSON response.
func (c *Client) queryInternal(ctx context.Context, query string, params map[string]interface{}) (*JSONResponse, error) {
	baseURL := fmt.Sprintf("http://%s:%d", c.cfg.Host, c.cfg.Port)
	u, err := url.Parse(baseURL)
	if err != nil {
		return nil, err
	}

	q := u.Query()
	q.Set("database", c.cfg.Database)
	q.Set("user", c.cfg.User)
	q.Set("password", c.cfg.Password)
	q.Set("default_format", "JSON")

	for k, v := range params {
		switch val := v.(type) {
		case string:
			q.Set("param_"+k, val)
		case int:
			q.Set("param_"+k, strconv.Itoa(val))
		case int64:
			q.Set("param_"+k, strconv.FormatInt(val, 10))
		case float64:
			q.Set("param_"+k, strconv.FormatFloat(val, 'f', -1, 64))
		case bool:
			q.Set("param_"+k, strconv.FormatBool(val))
		default:
			q.Set("param_"+k, fmt.Sprintf("%v", v))
		}
	}

	u.RawQuery = q.Encode()

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, u.String(), strings.NewReader(query))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/octet-stream")

	resp, err := c.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("clickhouse returned HTTP %d: %s", resp.StatusCode, string(body))
	}

	var result JSONResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode clickhouse JSON response: %w", err)
	}
	return &result, nil
}

// Query executes a SQL query with context and parses the JSON response.
func (c *Client) Query(ctx context.Context, query string) (*JSONResponse, error) {
	return c.queryInternal(ctx, query, nil)
}

// QueryWithParams executes a SQL query with named parameters via HTTP query string.
func (c *Client) QueryWithParams(ctx context.Context, query string, params map[string]interface{}) (*JSONResponse, error) {
	return c.queryInternal(ctx, query, params)
}

// QueryRow executes a query expected to return a single row and returns the values as a slice.
func (c *Client) QueryRow(ctx context.Context, query string) ([]interface{}, error) {
	res, err := c.queryInternal(ctx, query, nil)
	if err != nil {
		return nil, err
	}
	if len(res.Data) == 0 {
		return nil, nil
	}
	row := res.Data[0]
	out := make([]interface{}, 0, len(res.Meta))
	for _, m := range res.Meta {
		out = append(out, row[m.Name])
	}
	return out, nil
}

// QueryHTTP executes a SQL query and returns raw rows as maps.
// This is a convenience method used by cmd/spillwatch.
func (c *Client) QueryHTTP(ctx context.Context, query string) ([]map[string]interface{}, error) {
	res, err := c.queryInternal(ctx, query, nil)
	if err != nil {
		return nil, err
	}
	return res.Data, nil
}
