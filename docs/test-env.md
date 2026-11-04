# Apex test environment on Railway

A full-stack Apex environment for end-to-end tests, in the Railway project `apex.env`
(environment `production`). It runs only during weekday test windows and is stopped
otherwise (volumes keep their data). Plan, service table and cost estimate:
[`deploy/railway/PLAN.md`](../deploy/railway/PLAN.md).

## How it is built

12 services, created once by `deploy/railway/deploy.sh` through Railway's GraphQL API:

| Service | Built from |
|---|---|
| clickhouse | `deploy/railway/clickhouse/Dockerfile` (bakes `infra/sql` into initdb) |
| mongodb, s3 (MinIO), s3-init, hyperdx | public images |
| otel-collector | `deploy/railway/otel-collector/Dockerfile` (bakes `infra/otel-collector-config.yaml`) |
| spark-master / spark-worker / spark-history | `deploy/railway/spark/Dockerfile` + `start.sh <role>` |
| apex-api (+ stdio apex-mcp) | `deploy/railway/serve/Dockerfile` |
| console | `deploy/railway/console/Dockerfile` (front prod/nginx, `/v1` → apex-api) |
| e2e-runner (one-shot) | `deploy/railway/e2e/Dockerfile` + `e2e.sh` |

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

Filled in after the first deploy:

- Console: `https://<console>.up.railway.app`
- HyperDX: `https://<hyperdx>.up.railway.app`
- Spark History: `https://<spark-history>.up.railway.app`

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

## Known gaps

- Spark standalone over Railway's IPv6-first private network is untested; expect iteration.
- Keep `spark-worker` at 1 replica (per-replica hostnames needed for more).
- ClickHouse initdb runs only on an empty volume; later migrations need a manual apply.
