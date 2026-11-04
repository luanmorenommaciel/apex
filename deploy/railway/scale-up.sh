#!/usr/bin/env bash
# Test window: start every service in dependency order, run e2e-runner, collect result, scale down.
source "$(dirname "$0")/lib.sh"
trap '"$(dirname "$0")/scale-down.sh"' EXIT          # always scale down, even on failure
# DeployV2 builds from the current instance config + branch HEAD (Redeploy would replay the old snapshot).
deploy_now() { gql 'mutation($s:String!,$e:String!){serviceInstanceDeployV2(serviceId:$s,environmentId:$e)}' "{\"s\":\"$1\",\"e\":\"$ENV_ID\"}" | jq -r .data.serviceInstanceDeployV2; }
dep_status() { gql 'query($d:String!){deployment(id:$d){status}}' "{\"d\":\"$1\"}" | jq -r .data.deployment.status; }
logs_of() { gql 'query($d:String!){deploymentLogs(deploymentId:$d,limit:5000){message}}' "{\"d\":\"$1\"}" | jq -r '.data.deploymentLogs[].message'; }
wait_log() { # depId regex tries — one-shots stay "SUCCESS" while running, so wait for their own marker
  for _ in $(seq 1 "$3"); do logs_of "$1" | grep -Eq "$2" && return 0; sleep 20; done; return 1; }
wait_ok() { for _ in $(seq 1 180); do st=$(dep_status "$1"); case $st in SUCCESS) return 0;; FAILED|CRASHED) echo "$2 $st" >&2; return 1;; esac; sleep 10; done; echo "$2 timeout" >&2; return 1; }
for n in "${ORDER[@]}"; do
  d=$(deploy_now "$(svc_id "$n")"); echo "deploying $n" >&2
  wait_ok "$d" "$n"
  if [ "$n" = s3-init ]; then wait_log "$d" "buckets ready" 30 || { echo "s3-init: no buckets" >&2; exit 1; }; fi
done
id=$(svc_id e2e-runner)
DEP=$(deploy_now "$id"); wait_ok "$DEP" e2e-runner
wait_log "$DEP" '^E2E_EXIT=' 90 || echo "e2e-runner: no exit marker after 30 min" >&2
mkdir -p "$(dirname "$0")/runs"; LOG="$(dirname "$0")/runs/e2e-$(date +%F-%H%M).log"
logs_of "$DEP" > "$LOG"; st=$(grep -o '^E2E_EXIT=[0-9]*' "$LOG" | tail -1); st=${st:-E2E_EXIT=none}
echo "e2e-runner: $st  log: $LOG"; [ "$st" = E2E_EXIT=0 ]
