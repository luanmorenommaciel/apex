#!/usr/bin/env bash
# Stop every running deployment (compute billing stops; volumes keep data, ~$0.15/GB-mo).
source "$(dirname "$0")/lib.sh"
for n in e2e-runner "${ORDER[@]}"; do
  id=$(svc_id "$n"); [ -z "$id" ] && continue
  read -r dep st < <(latest_dep "$id")
  if [[ $st =~ SUCCESS|DEPLOYING|BUILDING|INITIALIZING|SLEEPING ]]; then
    gql 'mutation($d:String!){deploymentStop(id:$d)}' "{\"d\":\"$dep\"}" >/dev/null && echo "stopped $n"; fi
done
