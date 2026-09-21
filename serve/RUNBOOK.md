# RUNBOOK — apex-api

Operating the HTTP layer in `src/apex_api/`. The MCP server is a separate
process with its own instructions in [`README.md`](README.md); this document
does not cover it.

Every command below was run against a local stack on 2026-09-21. Where
something is **not** yet exercised, it says so.

---

## What this service is for

One HTTP surface in front of the Apex store, so the console and any other
consumer hold an **API token** and never a database user. Two tiers:

| Tier | Paths | Returns |
|---|---|---|
| Resources | `/v1/runs…`, `/v1/plans…`, `/v1/findings…` | the console's row shapes |
| Diagnostics | `/v1/runs/{job}/diagnosis`, `/v1/diagnostics/…` | the eight MCP tools' verdicts |

Health is `/v1/health`. Interactive docs are `/docs`.

---

## Prerequisites

- Docker running (the store is a container).
- `uv` on PATH.
- This repo checked out; commands run from `serve/` unless stated.

---

## 1 · Bring up the store

```bash
cd infra
cp .env.example .env          # first time only
# set a real HYPERDX_API_KEY — compose refuses to interpolate without one,
# even when you only want ClickHouse:
#   python3 -c "import secrets; print(secrets.token_hex(32))"
docker compose up -d clickhouse
```

`infra/.env` is gitignored. Never commit it.

Confirm the contract schema is there — `infra/sql/*.sql` is applied on **first
boot of the volume**, so an existing `ch-data` volume is not re-initialised:

```bash
curl -s "http://127.0.0.1:8123/?user=apex&password=apex_local_dev" \
  --data-binary "SHOW TABLES FROM apex"
```

Expect `spark_events`, `findings`, `job_conf`, `plan_transitions`,
`fix_verifications`, and the v0.3 pair `plan_memory` / `run_outcomes`. If the
last two are missing, the memory routes will answer 502 `memory_unavailable` —
see Troubleshooting.

---

## 2 · Configure and start the API

| Variable | Default | Notes |
|---|---|---|
| `APEX_API_TOKENS` | *(none)* | **Required.** Comma-separated. No token ⇒ the server refuses to start. |
| `APEX_API_HOST` | `127.0.0.1` | |
| `APEX_API_PORT` | `8000` | ⚠️ see the port note below |
| `APEX_LOG_LEVEL` | `INFO` | stderr only |

Plus every `CLICKHOUSE_*` variable from [`README.md`](README.md#configuration).

> **Port note.** The default is 8000, and `infra/docker-compose.yml` gives
> **HyperDX's API host port 8000** too. On a host running the full infra stack
> they collide. Use another port — this runbook uses **8099**.

```bash
cd serve
uv sync --extra dev

APEX_API_TOKENS="local-dev-token-a1b2c3" \
APEX_API_HOST=127.0.0.1 APEX_API_PORT=8099 \
CLICKHOUSE_HOST=127.0.0.1 CLICKHOUSE_PORT=8123 \
CLICKHOUSE_USER=apex CLICKHOUSE_PASSWORD=apex_local_dev CLICKHOUSE_DATABASE=apex \
uv run apex-api
```

Startup is clean when you see `Application startup complete.` The ClickHouse
connection is **lazy**: the service binds its port and answers `/v1/health`
even when the store is down, so a failed start means a configuration fault,
not an outage.

Generate a real token rather than reusing the sample above:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 3 · Verify

```bash
API=http://127.0.0.1:8099
TOK=local-dev-token-a1b2c3
H="Authorization: Bearer $TOK"

curl -s $API/v1/health                       # 200, no token needed
curl -s -o /dev/null -w '%{http_code}\n' $API/v1/runs            # 401
curl -s -o /dev/null -w '%{http_code}\n' -H "$H" $API/v1/runs    # 200
curl -s -o /dev/null -w '%{http_code}\n' -H "$H" $API/v1/runs/nope  # 404
```

A healthy store reports its own numbers:

```json
{"status":"ok","store":"ok","row_count":10,"job_count":4,"latest_ts":"..."}
```

Walk the surface with a real job id:

```bash
JOB=$(curl -s -H "$H" $API/v1/runs | python3 -c 'import sys,json;print(json.load(sys.stdin)[0]["job_id"])')
for p in "" /stages /findings /transitions /conf /baseline-candidates \
         /diagnosis /recall /verification; do
  printf '%-26s %s\n' "$p" \
    "$(curl -s -o /dev/null -w '%{http_code}' -H "$H" "$API/v1/runs/$JOB$p")"
done
```

All 200 on a store with data. Recorded result: 16/16 routes 200, unknown job
404, missing and bad tokens both 401, `fix-suggestion` returning
`applied: false`.

---

## 4 · The docs

| URL | What |
|---|---|
| `/docs` | Swagger UI, with an **Authorize** button |
| `/redoc` | ReDoc |
| `/openapi.json` | the schema |

All three answer **without a token**. A schema carries no row from the store,
but it does enumerate the surface — if that is not acceptable for a given
deployment, put the gate in front of the service rather than in `auth.py`,
which must keep answering before routing.

In Swagger: **Authorize** → paste the token → every `/v1` operation but
`/v1/health` shows a padlock.

---

## 5 · Point the console at it

```bash
cd front
VITE_DATA_SOURCE=http \
VITE_APEX_API_URL=http://127.0.0.1:8099 \
VITE_APEX_API_TOKEN=local-dev-token-a1b2c3 \
npm run dev
```

**Not yet exercised.** The console's HTTP path is covered by unit tests
against a stubbed `fetch`; nobody has driven the six data screens against a
running API. Treat this block as the intended invocation, not a verified one.

**Production is not wired yet.** `front/docker-entrypoint.d/30-apex-console-config.sh`
writes only `CLICKHOUSE_UPSTREAM`, `CLICKHOUSE_DB`, `CLICKHOUSE_USER`,
`CLICKHOUSE_PASSWORD` and `DATA_SOURCE` into `/config.js`. It does not write
`apiUrl` or `apiToken`, so a production console container cannot be pointed at
the API even with `DATA_SOURCE=http` — `runtimeConfig` would read both as empty
and every request would go to a relative URL with no token. The dev-server
invocation above works because Vite supplies the `VITE_*` values instead.

Closing this needs two keys added to that entrypoint script. Until then, the
http data source is a development and testing path only.

---

## 6 · Troubleshooting

| Symptom | Cause | Action |
|---|---|---|
| Startup raises `apex_api_unconfigured` | No `APEX_API_TOKENS` | Set one. The refusal is deliberate — an API that serves openly when unconfigured moves the credential problem rather than solving it. |
| Every `/v1` call is 401, including ones you expect to work | Token mismatch, or the header is not `Authorization: Bearer <token>` | Compare against `APEX_API_TOKENS`. The body is identical for a bad token and an unknown path, on purpose: it must not become a route oracle. |
| `/v1/health` says `"store":"unreachable"` | ClickHouse down or misaddressed | `docker compose ps clickhouse`; check `CLICKHOUSE_*`. The process is fine — that is why health still answers 200. |
| A route returns 502 `clickhouse_unavailable` | Same, surfaced per call | As above. |
| 502 `memory_unavailable` on `/v1/plans`, `/v1/plans/*`, `/v1/runs/*/baseline-candidates` | The v0.3 tables are absent | Apply `infra/sql/030_plan_memory.sql` and `031_run_outcomes.sql`, then run the memory lane's indexer. This is raised, not returned as `[]`, because no table is not an empty history. |
| 404 on a job you can see in `/v1/runs` | The id is from a different store, or was truncated | `/v1/runs/{job_id}` 404s rather than returning a zero-filled row. |
| `address already in use` on start | HyperDX holds 8000 | Use `APEX_API_PORT=8099`. |
| Response bodies never name the failing host | Working as designed | Driver exceptions embed the DSN; `ch._sanitize` strips it and the API does not undo that. The detail is on **stderr**. |

---

## 7 · Shut down

```bash
pkill -f apex-api            # the API process
cd infra && docker compose down          # stop the store, keep the volume
cd infra && docker compose down -v       # ALSO DELETES the data volume
```

`-v` destroys `ch-data`. The next `up` re-applies `infra/sql/*.sql` into an
empty store.

---

## Known gaps

- **A run the memory lane has not indexed reports `task_time_ms: 0`, not
  `null`.** `front/src/data/repository.ts` treats `-1` as the "not indexed"
  sentinel, but a ClickHouse `LEFT JOIN` miss fills a non-Nullable column with
  `0`, so `ifNull(…, -1)` never fires. The console then renders a measured
  zero for a number nobody measured. Pre-existing in the console's SQL and
  carried into `ch.py` by the port; not yet fixed.
- **The console's production image cannot use the API.** Its entrypoint never
  writes `apiUrl` / `apiToken` into `/config.js` (see §5), so `DATA_SOURCE=http`
  is a dev-only path until that script is updated.
- The MCP server still reads ClickHouse directly. Routing it through this API
  was planned and dropped: its tools need store primitives (`search`,
  `similar_plans`, `prior_outcomes`, …) that no route exposes.
- `/ask` is unimplemented; the console's chat screen is a scripted mockup.
