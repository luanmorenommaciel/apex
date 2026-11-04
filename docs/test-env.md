# Apex test environment on Railway

A full-stack Apex environment for end-to-end tests, in the Railway project `apex.env`
(environment `production`). It runs only during weekday test windows and is stopped
otherwise (volumes keep their data).

## How it is built

12 services, created once by `deploy/railway/deploy.sh` through Railway's GraphQL API:

| Service | Built from |
|---|---|
| clickhouse | `deploy/railway/clickhouse/Dockerfile` (bakes `infra/sql` into initdb) |
| mongodb, hyperdx | public images (`mongo:5.0.14-focal`, `hyperdx/hyperdx:2`) |
| s3 / s3-init | `rustfs/rustfs:1.0.3` / `amazon/aws-cli:2.38.5`, pinned by digest (minio/minio and minio/mc can no longer be pulled) |
| otel-collector | `deploy/railway/otel-collector/Dockerfile` (bakes `infra/otel-collector-config.yaml`) |
| spark-master / spark-worker / spark-history | `deploy/railway/spark/Dockerfile` + `start.sh <role>` |
| apex-api (+ stdio apex-mcp) | `deploy/railway/serve/Dockerfile` |
| console | `deploy/railway/console/Dockerfile` (front prod/nginx, `/v1` → apex-api) |
| e2e-runner (one-shot) | `deploy/railway/e2e/Dockerfile` + `e2e.sh` |

apex-mcp is stdio-only, so it is not a network service: it ships inside the apex-api and
e2e-runner images. compose's queue-init is replaced by `RAILWAY_RUN_UID=0` on otel-collector
(Railway volumes mount root-owned; RustFS runs as root for the same reason).

Volumes: clickhouse `/var/lib/clickhouse`, mongodb `/data/db`, s3 `/data`,
otel-collector `/var/lib/otelcol/queue`.

Private hostnames (compose → Railway): `clickhouse` → `clickhouse.railway.internal`,
`minio` → `s3.railway.internal:9000`, `apex-otel-collector` → `otel-collector.railway.internal:4318`,
`spark-master` → `spark-master.railway.internal:7077`, `host.docker.internal:8099` →
`apex-api.railway.internal:8099`, mongodb → `mongodb.railway.internal`. Railway's private
network is IPv6-first, so every service binds `::`.

Railway has no bind mounts, so configs are baked into wrapper images. `spark/start.sh`
renders `spark-defaults.conf` from env (`S3_ENDPOINT`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`,
`APEX_OTLP_ENDPOINT`, buckets), advertises `$RAILWAY_PRIVATE_DOMAIN`, binds on `::`, and
pins `spark.driver.port` (7078) and `spark.blockManager.port` (7079). HyperDX's
`DEFAULT_SOURCES` is copied verbatim from `infra/docker-compose.yml` into
`deploy/railway/hyperdx/default-sources.json`.

Secrets live only in Railway variables. `deploy.sh` reads them from your local shell
(`CLICKHOUSE_PASSWORD`, `REDACTION_SECRET_KEY`, `HYPERDX_API_KEY`, `S3_ACCESS_KEY`,
`S3_SECRET_KEY`, `APEX_API_TOKEN`, plus `RAILWAY_API_TOKEN`) and never prints them.
Nothing secret is committed.

## URLs

- HyperDX: https://hyperdx-production-c12c.up.railway.app (HyperDX login; only up during a test window)
- Console and Spark History are **private** (no public domain): the console renders the API
  token into `/config.js`. Reach them over the private network, e.g. `railway connect` or a
  temporary domain you remove afterwards.

## Run the end-to-end test

```bash
export RAILWAY_API_TOKEN=...      # never commit
deploy/railway/scale-up.sh        # start in order, run e2e-runner, save log, scale down
```

`scale-up.sh` starts services in dependency order, waits for each to be healthy,
redeploys `e2e-runner`, saves its log to `deploy/railway/runs/`, and always scales
down on exit. `e2e.sh` submits `dev/jobs/$E2E_JOB.py` (default `skew_join`) with a
fresh `spark.apex.job_id`, waits `E2E_SETTLE_SECONDS`, then runs
`scripts/e2e_six_lanes.py --job-id <id>` against `CLICKHOUSE_HOST` and `APEX_API_URL`.

## Redeploy

Push to the tracked branch (`APEX_RAILWAY_BRANCH`, default `railway-test-env`, switch
to `main` once merged), then run `scale-up.sh`; each service redeploys at its latest
commit. To change a variable, edit it in Railway (or re-run the matching block in
`deploy.sh`, which skips existing services).

## Scale up / down

- `deploy/railway/scale-up.sh` — test window (starts everything, runs e2e, stops).
- `deploy/railway/scale-down.sh` — stop all deployments now; compute billing stops,
  volumes persist.
- Right after the first `deploy.sh`, run `scale-down.sh` (Railway auto-deploys on create).
- `scale-up.sh` uses `serviceInstanceDeployV2`, so it builds the current config at branch
  HEAD (`serviceInstanceRedeploy` would replay the old snapshot). One-shots (`s3-init`,
  `e2e-runner`) are tracked by log markers (`buckets ready`, `E2E_EXIT=<code>`).

Cost (Railway Pro usage rates, estimate): ~7 GB RAM + 1.5 vCPU while up (~$0.14/h), about
2 h per weekday window, plus ~22 GB of volumes and builds: roughly $10–13/month.

## Known gaps

- `deploy.sh` pins repo services to the branch with `serviceConnect` (`serviceCreate`
  ignores `branch`).
- Keep `spark-worker` at 1 replica (per-replica hostnames needed for more).
- ClickHouse initdb runs only on an empty volume; later migrations (e.g. #208's 040) need a manual apply.
- nginx in the console resolves `apex-api.railway.internal` at start, so apex-api must be up first.
- Deploy from a commit whose CI is green.
