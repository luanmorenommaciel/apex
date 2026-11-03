#!/usr/bin/env bash
# Apex infra · seed the store via the REAL ingestion path (OTLP/HTTP -> collector -> otel_traces
# -> mv_spark_events -> spark_events). ~50 stage spans across 3 job_ids, several skewed.
#
# ⚠️ TTL GOTCHA (contract/README.md): tables have a 90-day TTL on ts. The fixture's ts is
#    June 2024 -> a raw insert TTL-expires (count stays 0). This seeder stamps ts = now(),
#    so rows survive. Production events are near-real-time; this only matters for replay.
#
# Also inserts ONE representative findings row per skewed job so the E2E trace check
# (verify.sh) can thread spark_events -> spark_jobs_1m -> findings by job_id. In the real
# pipeline the engine lane writes findings; this is a stand-in until engine is live.
#
# Usage:  ./scripts/seed.sh            (reads ports from ../.env)
set -euo pipefail
cd "$(dirname "$0")/.."
ENV_FILE="${INFRA_ENV_FILE:-.env}"
set -a; [ -f "$ENV_FILE" ] && . "$ENV_FILE"; set +a

OTLP_PORT="${OTLP_HTTP_HOST_PORT:-4318}"
CH_PORT="${CLICKHOUSE_HTTP_HOST_PORT:-8123}"
CH_USER="${CLICKHOUSE_USER:-apex}"
CH_PASS="${CLICKHOUSE_PASSWORD:-$(cat "${INFRA_SECRETS_DIR:-secrets}/clickhouse_password" 2>/dev/null || true)}"
[ -n "$CH_PASS" ] || { echo "❌ CLICKHOUSE_PASSWORD is required (set it in infra/.env and run scripts/preflight.sh; there is no default)"; exit 1; }
OTLP_URL="http://localhost:${OTLP_PORT}/v1/traces"
CH_URL="http://localhost:${CH_PORT}/"

echo "seeding -> OTLP ${OTLP_URL}  (ts=now, TTL-safe)"

python3 - "$OTLP_URL" <<'PY'
import json, time, sys, urllib.request, random
url = sys.argv[1]
random.seed(7)  # deterministic
now_ms = int(time.time() * 1000)
now_ns = int(time.time() * 1e9)
JOBS = [
    ("ax151sasadds114", "application_1718553600000_0042", "daily_revenue"),
    ("bo992kkllmm007",  "application_1718553600000_0099", "nightly_etl"),
    ("cz771ppqqrr223",  "application_1718553600000_0177", "sessionize"),
]
spans = []
n = 0
for ji, (job, app, name) in enumerate(JOBS):
    for stage in range(0, 17):          # 17 stages each -> 51 spans total
        # make ~1 stage per job badly skewed (p99 >> p50), the rest healthy
        skewed = (stage == 7)
        p50 = random.randint(800, 3000)
        p99 = p50 * random.randint(30, 60) if skewed else int(p50 * random.uniform(1.0, 1.8))
        spill = random.randint(2_000_000_000, 9_000_000_000) if skewed else 0
        attrs = {
            "job_id": job, "app_id": app, "app_name": name,
            "stage_id": str(stage), "stage_attempt": "0", "ts": str(now_ms + n),
            "shuffle_read_bytes": str(random.randint(10**6, 5*10**10)),
            "shuffle_write_bytes": str(random.randint(10**6, 10**10)),
            "spill_disk_bytes": str(spill), "spill_mem_bytes": "0",
            "gc_time_ms": str(random.randint(50, 45000)),
            "input_bytes": str(random.randint(10**6, 10**8)),
            "output_bytes": str(random.randint(10**6, 3*10**8)),
            "peak_execution_mem_bytes": str(random.randint(10**9, 2*10**10)),
            "task_count": str(random.choice([8, 50, 200])),
            "task_duration_p50_ms": str(p50), "task_duration_p99_ms": str(p99),
            "plan_fingerprint": ("%064x" % (ji*10000 + stage))[:64],
            "plan_json": "Join Inner, (customer_id = customer_id)" if skewed else "Scan parquet",
        }
        spans.append({
            "traceId": "%032x" % (0xa0f7651916cd43dd8448eb211c80000 + n),
            "spanId": "%016x" % (0xb7ad6b7169200000 + n),
            "name": "apex.stage", "kind": 2,
            "startTimeUnixNano": str(now_ns + n), "endTimeUnixNano": str(now_ns + n),
            "attributes": [{"key": k, "value": {"stringValue": v}} for k, v in attrs.items()],
        })
        n += 1
payload = {"resourceSpans": [{
    "resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "apex-seed"}}]},
    "scopeSpans": [{"scope": {"name": "apex.seed"}, "spans": spans}]}]}
req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                             headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as r:
    print(f"POSTed {len(spans)} apex.stage spans -> HTTP {r.status}")
PY

# Wait until the spans are actually queryable before deriving findings from them: on a
# cold stack the collector's first export can take longer than a fixed sleep, and a
# findings INSERT that runs too early selects zero rows — silently — so verify.sh's exit
# criterion then finds no job. Poll for the seeded row count (51 spans) instead.
echo "waiting for the seeded spans to land in spark_events..."
landed=0
for _ in $(seq 1 30); do
  n=$(curl -s -u "${CH_USER}:${CH_PASS}" "${CH_URL}" --data-binary "SELECT count() FROM apex.spark_events WHERE app_name IN ('daily_revenue','nightly_etl','sessionize')" | tr -d '[:space:]')
  [ "${n:-0}" -ge 51 ] && { landed=1; break; }
  sleep 2
done
[ "$landed" = 1 ] || { echo "❌ seeded spans did not land in spark_events within 60s (got ${n:-0}/51) — is the collector pointed at this ClickHouse?"; exit 1; }
echo "   ${n} seeded rows present"

# One findings row per skewed stage (stand-in for the engine lane) so verify.sh can thread
# spark_events -> spark_jobs_1m -> findings by job_id. detected_by marks it as a seed.
# Explicit column list: the table carries v0.2 columns (app_id, confidence_score) a bare
# INSERT ... SELECT would have to supply too, and ClickHouse rejects the mismatch with an
# HTTP 400 that `curl -s` used to swallow — a fresh volume then had zero findings and the
# exit criterion failed for a reason nobody saw. `-f` makes that error fatal here.
curl -sf -u "${CH_USER}:${CH_PASS}" "${CH_URL}" --data-binary "
INSERT INTO apex.findings (finding_id, job_id, app_id, stage_id, type, severity, evidence, hot_key, impact, fix, confidence, confidence_score, detected_by, ts)
SELECT
  generateUUIDv4()                                   AS finding_id,
  job_id, app_id, stage_id,
  'SKEW_ON_JOIN'                                      AS type,
  'critical'                                          AS severity,
  concat('p99/p50 = ', toString(round(task_duration_p99_ms / nullIf(task_duration_p50_ms,0),1)), 'x') AS evidence,
  ''                                                  AS hot_key,
  'skew tail dominates stage runtime'                AS impact,
  'enable AQE skew join (spark.sql.adaptive.skewJoin.enabled=true)' AS fix,
  'HIGH'                                              AS confidence,
  0.9                                                 AS confidence_score,
  'seed'                                              AS detected_by,
  now64(3)                                            AS ts
FROM apex.spark_events
WHERE app_name IN ('daily_revenue','nightly_etl','sessionize')
  AND task_duration_p99_ms / nullIf(task_duration_p50_ms,0) > 5
" >/dev/null || { echo "❌ findings INSERT failed (HTTP error from ClickHouse)"; exit 1; }
seeded=$(curl -s -u "${CH_USER}:${CH_PASS}" "${CH_URL}" --data-binary "SELECT count() FROM apex.findings WHERE detected_by = 'seed'" | tr -d '[:space:]')
[ "${seeded:-0}" -ge 1 ] || { echo "❌ no findings rows after the seed INSERT"; exit 1; }
echo "seeded ${seeded} findings rows for skewed stages"

echo "done. spark_events count:"
curl -s -u "${CH_USER}:${CH_PASS}" "${CH_URL}" --data-binary \
  "SELECT count() AS rows, uniq(job_id) AS jobs FROM apex.spark_events FORMAT TSVWithNames"
