#!/usr/bin/env bash
# Test window: start every service in dependency order, run e2e-runner, collect result, scale down.
source "$(dirname "$0")/lib.sh"
trap '"$(dirname "$0")/scale-down.sh"' EXIT          # always scale down, even on failure
wait_ok() { for _ in $(seq 1 90); do read -r _ st < <(latest_dep "$1"); case $st in SUCCESS) return 0;; FAILED|CRASHED) echo "$2 $st" >&2; return 1;; esac; sleep 10; done; echo "$2 timeout" >&2; return 1; }
for n in "${ORDER[@]}"; do
  id=$(svc_id "$n"); gql 'mutation($s:String!,$e:String!){serviceInstanceRedeploy(serviceId:$s,environmentId:$e)}' "{\"s\":\"$id\",\"e\":\"$ENV_ID\"}" >/dev/null
  wait_ok "$id" "$n"        # s3-init SUCCESS == exited 0
done
id=$(svc_id e2e-runner)
gql 'mutation($s:String!,$e:String!){serviceInstanceRedeploy(serviceId:$s,environmentId:$e)}' "{\"s\":\"$id\",\"e\":\"$ENV_ID\"}" >/dev/null
sleep 20; read -r DEP _ < <(latest_dep "$id")
for _ in $(seq 1 180); do read -r _ st < <(latest_dep "$id"); [[ $st =~ SUCCESS|FAILED|CRASHED|REMOVED ]] && break; sleep 20; done
mkdir -p "$(dirname "$0")/runs"; LOG="$(dirname "$0")/runs/e2e-$(date +%F-%H%M).log"
gql 'query($d:String!){deploymentLogs(deploymentId:$d,limit:5000){message}}' "{\"d\":\"$DEP\"}" | jq -r '.data.deploymentLogs[].message' > "$LOG"
echo "e2e-runner: $st  log: $LOG"; [ "$st" = SUCCESS ]
