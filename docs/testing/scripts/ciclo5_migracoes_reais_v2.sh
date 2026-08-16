#!/usr/bin/env bash
# Ciclo 5 v2 -- migracoes REAIS 022-028 do fork sobre o DDL REAL do upstream
# Robustecido: espera N confirmacoes seguidas, retry por comando, schema real do seed.
set -uo pipefail
BL="${APEX_REPO:-$(git rev-parse --show-toplevel)}"
SC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/migrations-60"

wait_stable() {
  local c="$1" OK=0
  for i in $(seq 1 40); do
    if docker exec "$c" clickhouse-client --user apex --password apex_local_dev --query "SELECT count() FROM apex.spark_events" >/dev/null 2>&1; then
      OK=$((OK+1))
      [ "$OK" -ge 3 ] && { echo "  $c ESTAVEL (3 confirmacoes seguidas contra o schema real)"; return 0; }
    else
      OK=0
    fi
    sleep 2
  done
  echo "  $c NUNCA ESTABILIZOU"; return 1
}

run_retry() {
  # $1=container $2=sql-file-or-'-' (stdin via redirect outside)
  local c="$1" tries=0 out=""
  while [ $tries -lt 5 ]; do
    out=$(docker exec -i "$c" clickhouse-client --user apex --password apex_local_dev --multiquery 2>&1)
    if [ -z "$out" ] || ! echo "$out" | grep -q "NETWORK_ERROR\|Connection refused"; then
      echo "$out"
      return 0
    fi
    tries=$((tries+1))
    sleep 3
  done
  echo "$out"
  return 1
}

echo "=== CONTAINER A: volume FRESCO, DDL real do upstream no boot ==="
docker rm -f apex-loop-migA2 >/dev/null 2>&1
docker run -d --name apex-loop-migA2 \
  -e CLICKHOUSE_USER=apex -e CLICKHOUSE_PASSWORD=apex_local_dev -e CLICKHOUSE_DB=apex \
  -v "$BL/infra/sql:/docker-entrypoint-initdb.d:ro" \
  clickhouse/clickhouse-server:24.8 >/dev/null
wait_stable apex-loop-migA2 || exit 1

echo "  aplicando as 7 migracoes, com retry por comando:"
FAIL=0
for f in "$SC"/*.sql; do
  name=$(basename "$f")
  ERR=$(run_retry apex-loop-migA2 < "$f")
  if [ -n "$ERR" ]; then
    echo "  [$name] FALHOU (apos retries): $ERR"
    FAIL=1
  else
    echo "  [$name] OK"
  fi
done
echo "  === CONTAINER A (volume fresco): $([ $FAIL -eq 0 ] && echo 'TODAS 7 OK' || echo 'ALGUMA FALHOU DE VERDADE') ==="

echo
echo "=== CONTAINER B: volume COM DADO real antes da migracao ==="
docker rm -f apex-loop-migB2 >/dev/null 2>&1
docker run -d --name apex-loop-migB2 \
  -e CLICKHOUSE_USER=apex -e CLICKHOUSE_PASSWORD=apex_local_dev -e CLICKHOUSE_DB=apex \
  -v "$BL/infra/sql:/docker-entrypoint-initdb.d:ro" \
  clickhouse/clickhouse-server:24.8 >/dev/null
wait_stable apex-loop-migB2 || exit 1

echo "  seed com o schema REAL de otel_traces (todas as colunas, defaults onde nao importa):"
SEED_ERR=$(run_retry apex-loop-migB2 <<'SQL'
INSERT INTO apex.otel_traces
(Timestamp, TraceId, SpanId, ParentSpanId, TraceState, SpanName, SpanKind, ServiceName,
 ResourceAttributes, ScopeName, ScopeVersion, SpanAttributes, Duration, StatusCode, StatusMessage)
VALUES
(now64(9), 'trace-seed-1', 'span-seed-1', '', '', 'apex.stage', 'SPAN_KIND_INTERNAL', 'apex-jar',
 map(), 'apex', '1.0',
 map('job_id','job-seed','app_id','app-seed','app_name','seed','stage_id','1','stage_attempt','0',
     'ts','1700000000000','shuffle_read_bytes','100','shuffle_write_bytes','100',
     'spill_disk_bytes','0','spill_mem_bytes','0','gc_time_ms','10',
     'input_bytes','100','output_bytes','100','peak_execution_mem_bytes','1000',
     'task_count','4','task_duration_p50_ms','10','task_duration_p99_ms','20'),
 1000000, 'STATUS_CODE_UNSET', '');
SQL
)
[ -n "$SEED_ERR" ] && echo "  SEED FALHOU: $SEED_ERR"
sleep 3
SEED_ROWS=$(docker exec apex-loop-migB2 clickhouse-client --user apex --password apex_local_dev --query "SELECT count() FROM apex.spark_events")
echo "  linhas em spark_events apos seed real: $SEED_ROWS"

echo
echo "  aplicando as 7 migracoes SOBRE volume com dado:"
FAIL=0
for f in "$SC"/*.sql; do
  name=$(basename "$f")
  ERR=$(run_retry apex-loop-migB2 < "$f")
  if [ -n "$ERR" ]; then
    echo "  [$name] FALHOU (apos retries): $ERR"
    FAIL=1
  else
    echo "  [$name] OK"
  fi
done
POST_ROWS=$(docker exec apex-loop-migB2 clickhouse-client --user apex --password apex_local_dev --query "SELECT count() FROM apex.spark_events")
POST_ERT=$(docker exec apex-loop-migB2 clickhouse-client --user apex --password apex_local_dev --query "SELECT job_id, executor_run_time_ms FROM apex.spark_events WHERE job_id='job-seed'")
echo "  linhas apos migracoes: $POST_ROWS (esperado igual a $SEED_ROWS)"
echo "  linha antiga + coluna nova (esperado DEFAULT 0): $POST_ERT"

if [ "$POST_ROWS" = "$SEED_ROWS" ] && [ "$SEED_ROWS" -gt 0 ] && [ "$FAIL" -eq 0 ]; then
  echo "  === CONTAINER B (volume com dado): PASS -- migracoes OK, dado real preservado ==="
else
  echo "  === CONTAINER B (volume com dado): FAIL -- ver detalhes acima ==="
fi

docker rm -f apex-loop-migA2 apex-loop-migB2 >/dev/null 2>&1
echo
echo "containers removidos"
