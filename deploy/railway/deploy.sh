#!/usr/bin/env bash
# ONE-TIME create of the full Apex stack in apex.env / production. DO NOT RUN without Luan's yes.
# Idempotent: skips services that already exist. Secrets are read from local env vars and
# written only into Railway variables; nothing is printed.
source "$(dirname "$0")/lib.sh"
for s in CLICKHOUSE_PASSWORD REDACTION_SECRET_KEY HYPERDX_API_KEY S3_ACCESS_KEY S3_SECRET_KEY APEX_API_TOKEN; do
  : "${!s:?export $s locally first (value goes to Railway vars only)}"; done
I=railway.internal

create() { # name sourceJson
  local id; id=$(svc_id "$1"); if [ -n "$id" ]; then echo "exists: $1" >&2; echo "$id"; return; fi
  gql 'mutation($i:ServiceCreateInput!){serviceCreate(input:$i){id}}' \
    "$(jq -nc --arg p "$PROJECT_ID" --arg e "$ENV_ID" --arg n "$1" --argjson s "$2" --arg b "$BRANCH" \
       '{i:({projectId:$p,environmentId:$e,name:$n,source:$s} + (if $s.repo then {branch:$b} else {} end))}')" \
    | jq -r .data.serviceCreate.id
  # serviceCreate ignores branch (deploys default branch); pin repo services to $BRANCH explicitly.
  if echo "$2" | jq -e .repo >/dev/null; then id=$(svc_id "$1")
    gql 'mutation($id:String!,$i:ServiceConnectInput!){serviceConnect(id:$id,input:$i){id}}' \
      "$(jq -nc --arg id "$id" --arg r "$REPO" --arg b "$BRANCH" '{id:$id,i:{repo:$r,branch:$b}}')" >/dev/null; fi; }
img()  { jq -nc --arg i "$1" '{image:$i}'; }
repo() { jq -nc --arg r "$REPO" '{repo:$r}'; }
inst() { # id instanceInputJson
  gql 'mutation($s:String!,$e:String!,$i:ServiceInstanceUpdateInput!){serviceInstanceUpdate(serviceId:$s,environmentId:$e,input:$i)}' \
    "$(jq -nc --arg s "$1" --arg e "$ENV_ID" --argjson i "$2" '{s:$s,e:$e,i:$i}')" >/dev/null; }
vars() { # id varsJson
  gql 'mutation($i:VariableCollectionUpsertInput!){variableCollectionUpsert(input:$i)}' \
    "$(jq -nc --arg p "$PROJECT_ID" --arg e "$ENV_ID" --arg s "$1" --argjson v "$2" '{i:{projectId:$p,environmentId:$e,serviceId:$s,variables:$v,skipDeploys:true}}')" >/dev/null; }
vol()  { # id mountPath
  gql 'mutation($i:VolumeCreateInput!){volumeCreate(input:$i){id}}' \
    "$(jq -nc --arg p "$PROJECT_ID" --arg e "$ENV_ID" --arg s "$1" --arg m "$2" '{i:{projectId:$p,environmentId:$e,serviceId:$s,mountPath:$m}}')" >/dev/null; }
domain() { gql 'mutation($i:ServiceDomainCreateInput!){serviceDomainCreate(input:$i){domain}}' \
    "$(jq -nc --arg e "$ENV_ID" --arg s "$1" --argjson p "$2" '{i:{environmentId:$e,serviceId:$s,targetPort:$p}}')" | jq -r .data.serviceDomainCreate.domain; }

CH_COMMON=$(jq -nc --arg pw "$CLICKHOUSE_PASSWORD" '{CLICKHOUSE_USER:"apex",CLICKHOUSE_PASSWORD:$pw,CLICKHOUSE_DB:"apex"}')
S3=$(jq -nc --arg a "$S3_ACCESS_KEY" --arg s "$S3_SECRET_KEY" '{S3_ACCESS_KEY:$a,S3_SECRET_KEY:$s,S3_ENDPOINT:"http://s3.railway.internal:9000",S3_REGION:"us-east-1",WAREHOUSE_BUCKET:"warehouse",LOGS_BUCKET:"spark-logs"}')
SPARK=$(jq -nc --argjson s3 "$S3" '$s3 + {SPARK_NO_DAEMONIZE:"true",PYTHONHASHSEED:"0",TZ:"UTC",AWS_REGION:"us-east-1",
  APEX_OTLP_ENDPOINT:"http://otel-collector.railway.internal:4318",SPARK_MASTER_URL:"spark://spark-master.railway.internal:7077",
  SPARK_WORKER_CORES:"2",SPARK_WORKER_MEMORY:"2g",RAILWAY_DOCKERFILE_PATH:"deploy/railway/spark/Dockerfile"}')

# 1 ClickHouse (+volume). Wrapper image bakes infra/sql into /docker-entrypoint-initdb.d.
id=$(create clickhouse "$(repo)")
vars "$id" "$(jq -nc --argjson c "$CH_COMMON" '$c+{CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT:"1",RAILWAY_DOCKERFILE_PATH:"deploy/railway/clickhouse/Dockerfile"}')"
inst "$id" '{"restartPolicyType":"ON_FAILURE","restartPolicyMaxRetries":5}'
vol "$id" /var/lib/clickhouse

# 2 MongoDB (+volume), HyperDX state only.
id=$(create mongodb "$(img mongo:5.0.14-focal)")
inst "$id" '{"startCommand":"mongod --bind_ip_all --ipv6","restartPolicyType":"ON_FAILURE"}'
vol "$id" /data/db

# 3 S3 store (MinIO, pinned tag; swap to rustfs/rustfs if PR #197 merges) (+volume).
id=$(create s3 "$(img minio/minio:RELEASE.2025-04-22T22-12-26Z)")
vars "$id" "$(jq -nc --arg a "$S3_ACCESS_KEY" --arg s "$S3_SECRET_KEY" '{MINIO_ROOT_USER:$a,MINIO_ROOT_PASSWORD:$s}')"
inst "$id" '{"startCommand":"minio server /data --address [::]:9000 --console-address [::]:9001","healthcheckPath":"/minio/health/ready","restartPolicyType":"ON_FAILURE"}'
vol "$id" /data

# 4 OTel collector. Wrapper bakes infra/otel-collector-config.yaml. RAILWAY_RUN_UID=0 replaces queue-init
#   (Railway volumes mount root-owned; running as root removes the chown one-shot).
id=$(create otel-collector "$(repo)")
vars "$id" "$(jq -nc --argjson c "$CH_COMMON" --arg r "$REDACTION_SECRET_KEY" '$c+{REDACTION_SECRET_KEY:$r,RAILWAY_RUN_UID:"0",
  CLICKHOUSE_ENDPOINT:"tcp://clickhouse.railway.internal:9000?compress=lz4&async_insert=0&deduplicate_blocks_in_dependent_materialized_views=1",
  RAILWAY_DOCKERFILE_PATH:"deploy/railway/otel-collector/Dockerfile"}')"
inst "$id" '{"restartPolicyType":"ON_FAILURE"}'
vol "$id" /var/lib/otelcol/queue

# 5 s3-init one-shot (minio-init). restartPolicy NEVER; exits 0 after buckets exist. Re-run is idempotent.
id=$(create s3-init "$(img minio/mc:RELEASE.2025-04-16T18-13-26Z)")
vars "$id" "$S3"
inst "$id" "$(jq -nc '{restartPolicyType:"NEVER",startCommand:"/bin/sh -c \"until mc alias set local $S3_ENDPOINT $S3_ACCESS_KEY $S3_SECRET_KEY; do sleep 3; done && mc mb --ignore-existing local/$WAREHOUSE_BUCKET && mc mb --ignore-existing local/$LOGS_BUCKET && echo apex | mc pipe local/$LOGS_BUCKET/events/.keep && echo buckets ready\""}')"

# 6-8 Spark from dev/Dockerfile (via deploy/railway/spark wrapper that renders spark-defaults.conf from env).
id=$(create spark-master "$(repo)"); vars "$id" "$SPARK"
inst "$id" '{"startCommand":"/opt/apex/railway/start.sh master","restartPolicyType":"ON_FAILURE"}'
id=$(create spark-worker "$(repo)"); vars "$id" "$SPARK"
inst "$id" '{"startCommand":"/opt/apex/railway/start.sh worker","restartPolicyType":"ON_FAILURE","numReplicas":1}'
id=$(create spark-history "$(repo)"); vars "$id" "$(jq -nc --argjson s "$SPARK" '$s+{SPARK_HISTORY_OPTS:"-Dspark.history.fs.logDirectory=s3a://spark-logs/events/ -Dspark.history.ui.port=18080"}')"
inst "$id" '{"startCommand":"/opt/apex/railway/start.sh history","restartPolicyType":"ON_FAILURE"}'
# private only (no public domain); reach it via `railway connect`/port-forward.

# 9 Apex API :8099 (apex-mcp ships in the same image; it is stdio-only, so no standalone service).
id=$(create apex-api "$(repo)")
vars "$id" "$(jq -nc --arg pw "$CLICKHOUSE_PASSWORD" --arg t "$APEX_API_TOKEN" '{APEX_API_HOST:"::",APEX_API_PORT:"8099",APEX_API_TOKENS:$t,
  CLICKHOUSE_HOST:"clickhouse.railway.internal",CLICKHOUSE_PORT:"8123",CLICKHOUSE_USER:"apex",CLICKHOUSE_PASSWORD:$pw,
  RAILWAY_DOCKERFILE_PATH:"deploy/railway/serve/Dockerfile"}')"
inst "$id" '{"startCommand":"apex-api","healthcheckPath":"/v1/health","restartPolicyType":"ON_FAILURE"}'

# 10 HyperDX (UI) -> ClickHouse + Mongo over private network; public domain on 8090.
id=$(create hyperdx "$(img hyperdx/hyperdx:2)")
HDX_DOMAIN=$(domain "$id" 8090)
vars "$id" "$(jq -nc --arg k "$HYPERDX_API_KEY" --arg pw "$CLICKHOUSE_PASSWORD" --arg d "https://$HDX_DOMAIN" '{HYPERDX_API_KEY:$k,HYPERDX_API_PORT:"8000",HYPERDX_APP_PORT:"8090",
  FRONTEND_URL:$d,HYPERDX_APP_URL:$d,NEXT_PUBLIC_SERVER_URL:$d,MONGO_URI:"mongodb://mongodb.railway.internal:27017/hyperdx",OPAMP_PORT:"4320",
  OTEL_SERVICE_NAME:"hdx-oss-api",USAGE_STATS_ENABLED:"false",PORT:"8090",
  DEFAULT_CONNECTIONS:([{name:"Apex ClickHouse",host:"http://clickhouse.railway.internal:8123",username:"apex",password:$pw}]|tojson)}')"
# DEFAULT_SOURCES: copied verbatim from infra/docker-compose.yml (Spark Events source) into hyperdx/default-sources.json.
vars "$id" "$(jq -nc --arg s "$(jq -c . "$(dirname "$0")/hyperdx/default-sources.json")" '{DEFAULT_SOURCES:$s}')"

# 11 Front console (front/Dockerfile prod target, nginx, http mode via API).
id=$(create console "$(repo)")
vars "$id" "$(jq -nc --arg t "$APEX_API_TOKEN" '{RAILWAY_DOCKERFILE_PATH:"deploy/railway/console/Dockerfile",DATA_SOURCE:"http",APEX_API_TOKEN:$t,
  APEX_API_UPSTREAM:"http://apex-api.railway.internal:8099",PORT:"80"}')"
# private only: the API token is rendered into /config.js, so no public domain.

# 12 e2e-runner one-shot: runs the six-lane e2e against the services above, then exits.
id=$(create e2e-runner "$(repo)")
vars "$id" "$(jq -nc --argjson s "$SPARK" --argjson c "$CH_COMMON" --arg t "$APEX_API_TOKEN" '$s+$c+{CLICKHOUSE_HOST:"clickhouse.railway.internal",
  APEX_API_URL:"http://apex-api.railway.internal:8099",APEX_API_TOKEN:$t,RAILWAY_DOCKERFILE_PATH:"deploy/railway/e2e/Dockerfile"}')"
inst "$id" '{"restartPolicyType":"NEVER","startCommand":"/opt/apex/railway/e2e.sh"}'
echo "Created. Nothing deployed yet beyond Railway's auto-first-deploy; run scale-down.sh to stop, scale-up.sh for a test window."
