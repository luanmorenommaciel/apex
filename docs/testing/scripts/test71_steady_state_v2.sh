#!/usr/bin/env bash
set -uo pipefail
CH="docker exec -i apex-mv-recon-test clickhouse-client --user apex --password apex_local_dev"

ok=0
fail=0
lost_ids=""

for i in $(seq 1 40); do
  jid="steady2-$i"
  now_ms=$(($(date +%s%N)/1000000))
  $CH --query "INSERT INTO apex.otel_traces (SpanName, SpanAttributes, Timestamp) VALUES ('apex.stage', {'job_id':'$jid','app_id':'a1','stage_id':'1','ts':'$now_ms'}, now64(9))" 2>/tmp/insert_err.txt
  rc=$?
  if [ $rc -ne 0 ]; then
    echo "$i insert_FAILED rc=$rc"
    continue
  fi
  cnt=$($CH --query "SELECT count() FROM apex.spark_events WHERE job_id='$jid'" 2>/dev/null | tr -d '[:space:]')
  if [ "$cnt" = "1" ]; then
    ok=$((ok+1))
    echo "$i propagated"
  else
    fail=$((fail+1))
    echo "$i LOST (count=$cnt)"
    lost_ids="$lost_ids $jid"
  fi
done
echo "=== resumo: ok=$ok fail=$fail ==="
echo "perdidos:$lost_ids"
