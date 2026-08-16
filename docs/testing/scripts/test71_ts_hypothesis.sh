#!/usr/bin/env bash
set -uo pipefail
CH="docker exec -i apex-mv-recon-test clickhouse-client --user apex --password apex_local_dev"

echo "=== reproducao EXATA da issue: sem 'ts' em SpanAttributes, 30 inserts ==="
for i in $(seq 1 30); do
  jid="nots-$i"
  $CH --query "INSERT INTO apex.otel_traces (SpanName, SpanAttributes, Timestamp) VALUES ('apex.stage', {'job_id':'$jid','app_id':'a1','stage_id':'1'}, now64(9))" 2>/tmp/insert_err.txt
  imm=$($CH --query "SELECT count() FROM apex.spark_events WHERE job_id='$jid'" 2>/dev/null | tr -d '[:space:]')
  echo "$i imediato=$imm"
done

echo
echo "=== revisitando TODOS apos 8s de espera (parts tiveram tempo de sofrer merge/TTL) ==="
sleep 8
for i in $(seq 1 30); do
  jid="nots-$i"
  later=$($CH --query "SELECT count() FROM apex.spark_events WHERE job_id='$jid'" 2>/dev/null | tr -d '[:space:]')
  tsval=$($CH --query "SELECT toString(ts) FROM apex.spark_events WHERE job_id='$jid' LIMIT 1" 2>/dev/null)
  echo "$i depois=$later ts=$tsval"
done

echo
echo "=== contagem final na tabela otel_traces (origem, deve ter as 30) ==="
$CH --query "SELECT count() FROM apex.otel_traces WHERE SpanName='apex.stage' AND SpanAttributes['job_id'] LIKE 'nots-%'"
echo "=== contagem final em spark_events (destino) ==="
$CH --query "SELECT count() FROM apex.spark_events WHERE job_id LIKE 'nots-%'"
