#!/usr/bin/env bash
# Ciclo 1 -- concorrencia real do PR-6
set -uo pipefail
CONTAINER="apex-loop-concur"
docker rm -f "$CONTAINER" >/dev/null 2>&1
docker run -d --name "$CONTAINER" \
  -e CLICKHOUSE_USER=apex -e CLICKHOUSE_PASSWORD=apex_local_dev -e CLICKHOUSE_DB=apex \
  clickhouse/clickhouse-server:24.8 >/dev/null

VERSION=""
for i in $(seq 1 25); do
  V=$(docker exec "$CONTAINER" clickhouse-client --user apex --password apex_local_dev --query "SELECT version()" 2>/dev/null)
  if [ -n "$V" ]; then VERSION="$V"; break; fi
  sleep 2
done
if [ -z "$VERSION" ]; then echo "SETUP FALHOU"; exit 1; fi
echo "container pronto: $VERSION"

CH() { docker exec -i "$CONTAINER" clickhouse-client --user apex --password apex_local_dev --multiquery; }

cat <<'SQL' | CH
DROP DATABASE IF EXISTS concur SYNC;
CREATE DATABASE concur;
CREATE TABLE concur.spark_events (job_id String, stage_id UInt32, ts DateTime, shuffle_read_bytes Int64)
ENGINE = MergeTree ORDER BY (job_id, stage_id)
SETTINGS non_replicated_deduplication_window = 100;
SQL

N=10
echo "=== disparando $N clientes concorrentes, cada um insere UM lote + 1 retry identico ==="
T0=$(date +%s%N)
for i in $(seq 1 $N); do
  (
    TS="2026-08-06 05:00:0$((i % 6))"
    SQL="INSERT INTO concur.spark_events SETTINGS async_insert=0, deduplicate_blocks_in_dependent_materialized_views=1 VALUES ('job-c$i',1,'$TS',$((i*100)));"
    docker exec -i "$CONTAINER" clickhouse-client --user apex --password apex_local_dev --multiquery <<< "$SQL"
    docker exec -i "$CONTAINER" clickhouse-client --user apex --password apex_local_dev --multiquery <<< "$SQL"
  ) &
done
wait
T1=$(date +%s%N)
CONCURRENT_MS=$(( (T1-T0)/1000000 ))

TOTAL_ROWS=$(echo "SELECT count() FROM concur.spark_events" | CH)
DISTINCT_JOBS=$(echo "SELECT count(DISTINCT job_id) FROM concur.spark_events" | CH)

echo
echo "=== resultado ==="
echo "linhas totais apos $N clientes x (1 insert + 1 retry identico): $TOTAL_ROWS"
echo "jobs distintos: $DISTINCT_JOBS (esperado $N)"
echo "tempo total concorrente: ${CONCURRENT_MS}ms"

if [ "$TOTAL_ROWS" = "$N" ] && [ "$DISTINCT_JOBS" = "$N" ]; then
  echo "VEREDITO: PASS -- dedup correto sob concorrencia, sem duplicar nem perder"
else
  echo "VEREDITO: FAIL -- esperado $N linhas/$N jobs, obtido $TOTAL_ROWS/$DISTINCT_JOBS"
fi

echo
echo "=== comparativo sequencial (mesma carga, um cliente por vez) ==="
docker exec -i "$CONTAINER" clickhouse-client --user apex --password apex_local_dev --query "TRUNCATE TABLE concur.spark_events"
T0=$(date +%s%N)
for i in $(seq 1 $N); do
  TS="2026-08-06 05:00:0$((i % 6))"
  SQL="INSERT INTO concur.spark_events SETTINGS async_insert=0, deduplicate_blocks_in_dependent_materialized_views=1 VALUES ('job-s$i',1,'$TS',$((i*100)));"
  echo "$SQL" | CH
  echo "$SQL" | CH
done
T1=$(date +%s%N)
SEQ_MS=$(( (T1-T0)/1000000 ))
echo "tempo total sequencial: ${SEQ_MS}ms"
echo
echo "=== RESUMO: concorrente=${CONCURRENT_MS}ms sequencial=${SEQ_MS}ms ==="

docker rm -f "$CONTAINER" >/dev/null 2>&1
echo "container removido"
