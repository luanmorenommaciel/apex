#!/usr/bin/env bash
# Post two real OTLP/HTTP spans to the collector's /v1/traces:
#   1. apex.stage           — the 19 contract fields (from contract/sample_event.json)
#                             + PII bait (query_text, file_path, email, plan_json "desc")
#                             to prove the redaction second-net.
#   2. apex.plan_transition — the v0.2 AQE-decision signal.
#   3. apex.job_conf        — the v0.4 proposal: resolved conf allowlist (one row/app).
#
# Usage: scripts/send_sample_events.sh [OTLP_BASE_URL]
#   default endpoint derives from .env (OTLP_HTTP_HOST_PORT), else http://localhost:4318
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] && set -a && . ./.env && set +a || true
BASE="${1:-http://localhost:${OTLP_HTTP_HOST_PORT:-4318}}"
URL="${BASE%/}/v1/traces"

# Contract fixture ts (1718553999000 = 2024-06) is older than the 90-day TTL, so the row
# would TTL-expire on insert. Default to NOW so the E2E test survives; override with TS_MS=.
TS_MS="${TS_MS:-$(python3 -c 'import time; print(int(time.time()*1000))')}"
TS_NS=$(( TS_MS * 1000000 ))
JOB_ID="${JOB_ID:-ax151sasadds114}"

read -r -d '' PAYLOAD <<JSON || true
{
  "resourceSpans": [{
    "resource": { "attributes": [
      { "key": "service.name", "value": { "stringValue": "apex-spark" } }
    ]},
    "scopeSpans": [{
      "scope": { "name": "apex" },
      "spans": [
        {
          "traceId": "5b8efff798038103d269b633813fc60c",
          "spanId": "eee19b7ec3c1b174",
          "name": "apex.stage",
          "kind": 1,
          "startTimeUnixNano": "${TS_NS}",
          "endTimeUnixNano": "${TS_NS}",
          "attributes": [
            { "key": "job_id",                   "value": { "stringValue": "${JOB_ID}" } },
            { "key": "app_id",                   "value": { "stringValue": "application_1718553600000_0042" } },
            { "key": "app_name",                 "value": { "stringValue": "daily_revenue" } },
            { "key": "stage_id",                 "value": { "stringValue": "7" } },
            { "key": "stage_attempt",            "value": { "stringValue": "0" } },
            { "key": "ts",                       "value": { "stringValue": "${TS_MS}" } },
            { "key": "shuffle_read_bytes",       "value": { "stringValue": "50465865728" } },
            { "key": "shuffle_write_bytes",      "value": { "stringValue": "12123000000" } },
            { "key": "spill_disk_bytes",         "value": { "stringValue": "8100000000" } },
            { "key": "spill_mem_bytes",          "value": { "stringValue": "0" } },
            { "key": "gc_time_ms",               "value": { "stringValue": "41200" } },
            { "key": "input_bytes",              "value": { "stringValue": "88000000" } },
            { "key": "output_bytes",             "value": { "stringValue": "240000000" } },
            { "key": "peak_execution_mem_bytes", "value": { "stringValue": "17179869184" } },
            { "key": "task_count",               "value": { "stringValue": "200" } },
            { "key": "task_duration_p50_ms",     "value": { "stringValue": "47000" } },
            { "key": "task_duration_p99_ms",     "value": { "stringValue": "2478000" } },
            { "key": "plan_fingerprint",         "value": { "stringValue": "2de5e5760399189a81ab5500a216db0bae5c67f72cf42c08bd9f62689b404cf0" } },
            { "key": "plan_json",                "value": { "stringValue": "Join Inner, (customer_id#0L = customer_id#10L) {\"desc\":\"leaked literal x=42\"}" } },
            { "key": "query_text",               "value": { "stringValue": "SELECT * FROM orders WHERE customer_id = 12847" } },
            { "key": "file_path",                "value": { "stringValue": "/data/warehouse/pii/orders.parquet" } },
            { "key": "email",                    "value": { "stringValue": "analyst@owshq.com" } }
          ]
        },
        {
          "traceId": "5b8efff798038103d269b633813fc60d",
          "spanId": "eee19b7ec3c1b175",
          "name": "apex.plan_transition",
          "kind": 1,
          "startTimeUnixNano": "${TS_NS}",
          "endTimeUnixNano": "${TS_NS}",
          "attributes": [
            { "key": "job_id",          "value": { "stringValue": "${JOB_ID}" } },
            { "key": "execution_id",    "value": { "stringValue": "3" } },
            { "key": "update_seq",      "value": { "stringValue": "1" } },
            { "key": "transition_type", "value": { "stringValue": "skew_split" } },
            { "key": "detail",          "value": { "stringValue": "200->17 partitions" } },
            { "key": "before",          "value": { "stringValue": "SortMergeJoin" } },
            { "key": "after",           "value": { "stringValue": "SortMergeJoin+AQEShuffleRead(skew)" } },
            { "key": "confidence",      "value": { "stringValue": "HIGH" } },
            { "key": "ts",              "value": { "stringValue": "${TS_MS}" } }
          ]
        },
        {
          "traceId": "5b8efff798038103d269b633813fc60e",
          "spanId": "eee19b7ec3c1b176",
          "name": "apex.job_conf",
          "kind": 1,
          "startTimeUnixNano": "${TS_NS}",
          "endTimeUnixNano": "${TS_NS}",
          "attributes": [
            { "key": "job_id",                          "value": { "stringValue": "${JOB_ID}" } },
            { "key": "app_id",                          "value": { "stringValue": "application_1718553600000_0042" } },
            { "key": "app_name",                        "value": { "stringValue": "daily_revenue" } },
            { "key": "ts",                              "value": { "stringValue": "${TS_MS}" } },
            { "key": "spark.sql.shuffle.partitions",    "value": { "stringValue": "200" } },
            { "key": "spark.executor.instances",        "value": { "stringValue": "4" } },
            { "key": "spark.executor.cores",            "value": { "stringValue": "4" } },
            { "key": "spark.executor.memory",           "value": { "stringValue": "8g" } },
            { "key": "spark.driver.cores",              "value": { "stringValue": "2" } },
            { "key": "spark.driver.memory",             "value": { "stringValue": "4g" } },
            { "key": "spark.sql.adaptive.enabled",      "value": { "stringValue": "true" } },
            { "key": "spark.sql.adaptive.skewJoin.enabled", "value": { "stringValue": "true" } },
            { "key": "spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "value": { "stringValue": "256m" } },
            { "key": "spark.sql.adaptive.skewJoin.skewedPartitionFactor", "value": { "stringValue": "5" } },
            { "key": "spark.sql.adaptive.coalescePartitions.enabled", "value": { "stringValue": "true" } },
            { "key": "spark.sql.adaptive.advisoryPartitionSizeInBytes", "value": { "stringValue": "64m" } },
            { "key": "spark.sql.autoBroadcastJoinThreshold", "value": { "stringValue": "10m" } }
          ]
        }
      ]
    }]
  }]
}
JSON

echo "POST ${URL}"
curl -sS -X POST "${URL}" \
  -H "Content-Type: application/json" \
  --data-binary "${PAYLOAD}" \
  -w "\nHTTP %{http_code}\n"
