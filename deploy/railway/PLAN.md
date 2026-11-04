# Apex full-stack Railway plan — apex.env / production (PLAN ONLY, 2026-11-04)

Status: nothing created, nothing run, $0 spent. Scripts here (`deploy.sh`, `scale-up.sh`, `scale-down.sh`, `lib.sh`)
are syntax-checked only. Mutation names/inputs were checked read-only against Railway's live GraphQL schema
(`serviceCreate`, `serviceInstanceUpdate`, `variableCollectionUpsert`, `volumeCreate`, `serviceDomainCreate`,
`serviceInstanceRedeploy`, `deploymentStop`). Source: apex `main` @ 0e84c10 + `/workspace/apex-steward-prep-2026-11-04.md`.

## 1. Services (12)
| Service | Source | Start | Port(s) | Volume |
|---|---|---|---|---|
| clickhouse | repo, `deploy/railway/clickhouse/Dockerfile` = `FROM clickhouse/clickhouse-server:24.8` + `COPY infra/sql /docker-entrypoint-initdb.d` | image default | 8123, 9000 | `/var/lib/clickhouse` (10 GB) |
| mongodb | image `mongo:5.0.14-focal` | `mongod --bind_ip_all --ipv6` | 27017 | `/data/db` (1 GB) |
| s3 | image `minio/minio:latest` (→ `rustfs/rustfs` if #197 merges) | `minio server /data --address [::]:9000 --console-address [::]:9001` | 9000 | `/data` (10 GB) |
| otel-collector | repo, wrapper `FROM otel/opentelemetry-collector-contrib:0.156.0` + `COPY infra/otel-collector-config.yaml` | `--config /etc/otelcol-contrib/config.yaml` | 4318, 4317, 13133 | `/var/lib/otelcol/queue` (1 GB) |
| s3-init (one-shot) | image `minio/mc:latest` | mc alias + `mb --ignore-existing` warehouse, spark-logs + `events/.keep` | — | — |
| spark-master | repo, wrapper `FROM` dev/Dockerfile build (jar baked) + `start.sh` | `start.sh master` | 7077, 8080 | — |
| spark-worker | same image | `start.sh worker` | 8081 + ephemeral | — |
| spark-history | same image | `start.sh history` | 18080 (public domain) | — |
| apex-api | repo, `deploy/railway/serve/Dockerfile` (python3.12 + `uv sync` in serve/) | `apex-api` | 8099, health `/v1/health` | — |
| hyperdx | image `hyperdx/hyperdx:2` | image default | 8090 (public), 8000, 4320 | — (state in mongodb) |
| console | repo, `front/Dockerfile` target `prod` (nginx) via wrapper | image default | 80 (public) | — |
| e2e-runner (one-shot) | repo, wrapper on spark image + uv + serve + tests | `e2e.sh` | — | — |

apex-mcp is **stdio-only** (`serve/src/apex_mcp/server.py`), so it is not a network service: it ships inside the
apex-api and e2e-runner images and the e2e runner exercises it locally against `APEX_API_URL`.
queue-init is **dropped**: `RAILWAY_RUN_UID=0` on otel-collector replaces the chown one-shot (Railway volumes mount root-owned).
(Infra's collector config doesn't use the file_storage queue today; the volume is there for the collect-lane config.)

## 2. Private hostnames (compose → Railway)
`apex-infra-clickhouse`/`clickhouse` → `clickhouse.railway.internal` · `apex-infra-mongodb` → `mongodb.railway.internal` ·
`minio` → `s3.railway.internal:9000` · `apex-otel-collector`/`apex-infra-otel-collector` → `otel-collector.railway.internal:4318` ·
`spark-master` → `spark-master.railway.internal:7077` · `host.docker.internal:8099` → `apex-api.railway.internal:8099`.
Every bind must listen on `::` (Railway private net is IPv6-first).

## 3. Variables (names only; values live only in Railway vars, set by deploy.sh from local env)
Secrets: `CLICKHOUSE_PASSWORD`, `REDACTION_SECRET_KEY`, `HYPERDX_API_KEY`, `MINIO_ROOT_USER`/`MINIO_ROOT_PASSWORD` (= `S3_ACCESS_KEY`/`S3_SECRET_KEY`), `APEX_API_TOKENS`, `VITE_APEX_API_TOKEN`/`APEX_API_TOKEN`.
- clickhouse: CLICKHOUSE_USER, CLICKHOUSE_PASSWORD, CLICKHOUSE_DB, CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT
- s3: MINIO_ROOT_USER, MINIO_ROOT_PASSWORD
- otel-collector: CLICKHOUSE_USER, CLICKHOUSE_PASSWORD, CLICKHOUSE_ENDPOINT, REDACTION_SECRET_KEY, RAILWAY_RUN_UID
- s3-init: S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, WAREHOUSE_BUCKET, LOGS_BUCKET
- spark-*: SPARK_MASTER_URL, SPARK_WORKER_CORES, SPARK_WORKER_MEMORY, S3_ENDPOINT, S3_REGION, S3_ACCESS_KEY, S3_SECRET_KEY, WAREHOUSE_BUCKET, LOGS_BUCKET, APEX_OTLP_ENDPOINT, AWS_REGION, SPARK_NO_DAEMONIZE, PYTHONHASHSEED, TZ, (history) SPARK_HISTORY_OPTS
- apex-api: APEX_API_HOST, APEX_API_PORT, APEX_API_TOKENS, CLICKHOUSE_HOST, CLICKHOUSE_PORT, CLICKHOUSE_USER, CLICKHOUSE_PASSWORD
- hyperdx: HYPERDX_API_KEY, HYPERDX_API_PORT, HYPERDX_APP_PORT, FRONTEND_URL, HYPERDX_APP_URL, NEXT_PUBLIC_SERVER_URL, MONGO_URI, OPAMP_PORT, OTEL_SERVICE_NAME, USAGE_STATS_ENABLED, DEFAULT_CONNECTIONS, DEFAULT_SOURCES
- console: VITE_DATA_SOURCE=http, VITE_APEX_API_TOKEN, APEX_API_UPSTREAM
- e2e-runner: spark + CH vars + APEX_API_URL, APEX_API_TOKEN
- all repo builds: RAILWAY_DOCKERFILE_PATH
- If #208 merges: add APEX_INFRA_CLICKHOUSE_PASSWORD, APEX_CLUSTER_SLOTS.

## 4. One-shot steps
- ClickHouse DDL: baked into the image's initdb dir; runs once on an empty volume (re-runs need `make verify-ddl`-style apply, see blocker 5).
- s3-init: `restartPolicyType: NEVER`, idempotent; scale-up.sh waits for its deployment to reach SUCCESS (exit 0) before Spark starts.
- queue-init: replaced by RAILWAY_RUN_UID=0.
- e2e-runner: `NEVER` restart; scale-up.sh redeploys it last, polls status, saves logs to `runs/`.

## 5. Scale to 0 outside windows
`scale-down.sh` calls `deploymentStop` on each service's latest deployment (compute stops; volumes persist).
`scale-up.sh` redeploys in order clickhouse → mongodb → s3 → otel-collector → s3-init → spark-master → worker → history → apex-api → hyperdx → console,
waits for SUCCESS each, runs e2e-runner, pulls logs, and **always** scales down via `trap EXIT`.
Run it from the weekday routine (after Luan's yes), e.g. once per weekday.

Cost estimate (Railway Pro rates, not a quote): running ≈ 7 GB RAM + 1.5 vCPU ≈ $0.14/h → 2 h × 22 weekdays ≈ $6;
volumes 22 GB ≈ $3.30/mo; builds/egress ≈ $1–3. **≈ $10–13/mo**, inside the approved $10–20.

## 6. Blockers / risks
1. **`make e2e` cannot target Railway as-is.** `scripts/apex.sh` is a macOS/Windows docker-compose package flow (Makefile rejects Linux). The e2e-runner needs a new `e2e.sh` that calls `scripts/e2e_six_lanes.py` / lane commands with Railway endpoints. Biggest unknown; needs repo work.
2. **Spark networking.** Master must bind `::` and advertise `spark-master.railway.internal`; worker and driver (in e2e-runner) need `SPARK_LOCAL_HOSTNAME=$RAILWAY_PRIVATE_DOMAIN`, fixed `spark.driver.port`/`spark.blockManager.port`, and IPv6 (`-Djava.net.preferIPv6Addresses=true`). Spark standalone over IPv6-only DNS is untested; expect iteration. Worker scale >1 needs per-replica hostnames (keep 1 replica).
3. **Bind-mounted config.** `spark-defaults.conf` hardcodes `minio:9000`, `minioadmin` keys and `apex-otel-collector:4318`; collector/ClickHouse configs are bind mounts. Railway has no bind mounts, so wrapper Dockerfiles under `deploy/railway/{clickhouse,otel-collector,spark,serve,console,e2e}/` plus `start.sh` (renders spark-defaults from env) and `e2e.sh` must exist on a branch (`railway-test-env`). That's a fix PR to open (Luan approved fix PRs via Helm; confirm in chat).
4. **minio image pull failures** noted in #197; if Railway can't pull, switch `s3` to RustFS.
5. ClickHouse initdb runs only on a fresh volume, so later migrations (#208's 040) need a separate apply step.
6. HyperDX `DEFAULT_SOURCES` is copied verbatim into `hyperdx/default-sources.json` and set by deploy.sh; the console needs `/v1` proxied (APEX_API_UPSTREAM), and the API has no CORS.
7. **Main CI not green** (Actions billing lock); deploy from a known-green commit.
8. Railway's first `serviceCreate` with a source auto-deploys, so run `scale-down.sh` right after `deploy.sh`.
