#!/usr/bin/env bash
# Shared helpers. Token is read from env, never echoed. Requires curl + jq.
set -euo pipefail
: "${RAILWAY_API_TOKEN:?RAILWAY_API_TOKEN not set}"
API=https://backboard.railway.com/graphql/v2
PROJECT_ID=e970aeef-1f77-4f88-ad55-d7042a93fff7
REPO=luanmorenommaciel/apex
BRANCH=${APEX_RAILWAY_BRANCH:-railway-test-env}   # branch carrying deploy/railway/* wrappers (see docs/test-env.md "Redeploy")
gql() { # gql '<query>' '<json vars>'
  local body; body=$(jq -nc --arg q "$1" --argjson v "${2:-{\}}" '{query:$q,variables:$v}')
  local out; out=$(curl -sS "$API" -H "Authorization: Bearer $RAILWAY_API_TOKEN" -H 'Content-Type: application/json' -d "$body")
  if echo "$out" | jq -e '.errors' >/dev/null; then echo "GraphQL error: $(echo "$out" | jq -c .errors)" >&2; return 1; fi
  echo "$out"
}
ENV_ID=$(gql 'query($p:String!){project(id:$p){environments{edges{node{id name}}}}}' "{\"p\":\"$PROJECT_ID\"}" \
  | jq -r '.data.project.environments.edges[].node|select(.name=="production").id')
svc_id() { gql 'query($p:String!){project(id:$p){services{edges{node{id name}}}}}' "{\"p\":\"$PROJECT_ID\"}" \
  | jq -r --arg n "$1" '.data.project.services.edges[].node|select(.name==$n).id'; }
latest_dep() { gql 'query($s:String!,$e:String!){deployments(first:1,input:{serviceId:$s,environmentId:$e}){edges{node{id status}}}}' \
  "{\"s\":\"$1\",\"e\":\"$ENV_ID\"}" | jq -r '.data.deployments.edges[0].node|"\(.id) \(.status)"'; }
# Boot order (dependencies first). e2e-runner is last and one-shot.
ORDER=(clickhouse mongodb s3 otel-collector s3-init spark-master spark-worker spark-history apex-api hyperdx console)
