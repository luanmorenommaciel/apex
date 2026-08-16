#!/usr/bin/env bash
set -uo pipefail
CH="docker exec -i apex-mv-race-test clickhouse-client --user apex --password apex_local_dev"

ok=0
fail=0
first_fail=""
last_ok_before_first_fail=""

for i in $(seq 1 30); do
  jid="steady-$i"
  $CH --query "INSERT INTO apex.otel_traces (SpanName, SpanAttributes, Timestamp) VALUES ('apex.stage', {'job_id':'$jid','app_id':'a1','stage_id':'1'}, now64(9))" 2>/tmp/insert_err.txt
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
    [ -z "$first_fail" ] && first_fail=$i
  fi
done
echo "=== resumo: ok=$ok fail=$fail primeira_perda_no_indice=$first_fail ==="
