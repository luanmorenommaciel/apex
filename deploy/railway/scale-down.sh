#!/usr/bin/env bash
# Stop every running deployment (compute billing stops; volumes keep data, ~$0.15/GB-mo).
source "$(dirname "$0")/lib.sh"
for n in e2e-runner "${ORDER[@]}"; do
  id=$(svc_id "$n"); [ -z "$id" ] && continue
  read -r dep _ < <(latest_dep "$id")
  stopped=$(gql 'query($d:String!){deployment(id:$d){deploymentStopped}}' "{\"d\":\"$dep\"}" | jq -r .data.deployment.deploymentStopped)
  if [ "$stopped" != true ]; then
    gql 'mutation($d:String!){deploymentStop(id:$d)}' "{\"d\":\"$dep\"}" >/dev/null && echo "stopped $n"; else echo "already stopped $n"; fi
done
