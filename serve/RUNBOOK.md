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

### 3.1 · Prove the rows, not the status codes

The walk above checks status codes, and status codes are what passed while
three routes returned the wrong projection. A 200 says a route answered; it
does not say the console can render what came back.

`tools/console_parity_gate.py` issues every statement the console sends
**twice** — as the browser does, over ClickHouse HTTP as `apex_ro`, and through
the API — and fails unless both doors return the same rows. It reads the
statements out of `front/src/data/queries.ts`, so it compares against what the
console actually sends rather than against a copy.

**What the infra stack needs first**

| Need | How | Without it |
|---|---|---|
| The store is up with the contract applied | step 1 | nothing runs. If only `plan_memory` / `run_outcomes` are missing, the memory checks print `NOT EXERCISED` |
| The console's read-only user | `cd front && make ch-user` | the browser door is `apex_ro`; every browser-side statement is refused and the gate fails on its first line |
| The environment names the store | the `CLICKHOUSE_*` variables from step 2, `CLICKHOUSE_DATABASE` included | the gate connects to `127.0.0.1:8123`, database `apex` — wrong on a host where `infra/.env` moved the port (the shared dev host uses 28123) |
| A user that may write, for the default mode | `CLICKHOUSE_USER=apex` locally | the gate seeds its own rows and deletes them; on a store nobody may write to, use `--job-id` |

```bash
cd serve
CLICKHOUSE_HOST=127.0.0.1 CLICKHOUSE_PORT=8123 \
CLICKHOUSE_USER=apex CLICKHOUSE_PASSWORD=apex_local_dev CLICKHOUSE_DATABASE=apex \
uv run python tools/console_parity_gate.py
```

| Mode | What it does |
|---|---|
| *(default)* | Seeds the required rows under job ids carrying a random suffix, runs every check, and removes exactly those rows — the arrangement `tools/read_only_gate.py` already uses. A seeded check that lacks its required findings tie is a failure. |
| `--job-id <id>` | Writes **nothing**. Compares the two doors on a run the store already holds. A behaviour that run's data cannot exercise prints `NOT EXERCISED`, which is not a pass. |
| `--api-url http://127.0.0.1:8099 --api-token $TOK` | The API door is the **running service** from step 2 instead of an in-process app. This is the one that signs off a deployment; combine it with either mode above. |

On infra's own seed (`infra/scripts/seed.sh`) use
`--job-id ax151sasadds114`: the seed writes stages and one finding per skewed
job, no transitions and no `run_outcomes`, so parity, the sentinel, the
read-only proof and the wire format are exercised, and the findings and
transitions ordering checks print `NOT EXERCISED`. The default mode is what exercises all of them.

**What each line proves**

| Check | Proves | Why a fake cannot |
|---|---|---|
| eleven `same through both doors` lines | each route returns the columns, values and order the console's own statement returns | the projection lives in the SQL; a fake returns whatever rows it is handed |
| `unindexed run reads as not indexed` | a run with no `run_outcomes` row reports `task_time_ms -1`, `shaped_stage_count -1`, `plan_fingerprint ''`, `config_source 'unknown'` | ClickHouse fills a missed `LEFT JOIN` with column DEFAULTS, not NULLs — the fill is the database's |
| `statements run as a read-only user` | every statement executes under `readonly = 1`: none needs a setting, and `if()` found a common type for every branch | the type check and the settings refusal are the server's |
| `findings ordered by confidence_score` | the first finding is the most confident one even when it is not the oldest — what `/verify` opens on | the order is `ORDER BY`'s |
| `findings tie-break by finding_id` (browser and API separately) | each door returns `confidence_score DESC, finding_id ASC` when scores tie | two doors with the same wrong order can pass parity; each must also match the canonical order |
| `one transition per execution` | an execution re-planned three times is one row, carrying its last `update_seq` | the collapse is `GROUP BY` and `argMax` |
| `timestamps in the wire format` | every timestamp leaves as `YYYY-MM-DDTHH:MM:SS.mmm`, UTC, no offset — the pattern `front/src/data/timestamp.ts` declares | the driver decides what a `DateTime64(3)` becomes |

**Findings fixture and required coverage.** The default fixture writes four
findings: one high score, one low score, and two scores of `0.5`. The tied pair
shares a timestamp and is inserted in reverse finding-id order. The indexed
run's `finding_count` is derived from those four rows; the unindexed run's is
zero. The gate checks the tied pair independently through the browser and API
doors. If a seeded door cannot exercise the tie, it reports `FAIL`, not
`NOT EXERCISED`. With `--job-id`, insufficient existing data still reports
`NOT EXERCISED`; that result does not certify the tie-break. An unreadable
confidence score is a diagnostic failure rather than an assumed numeric value.

Current evidence for the extension tracked in
[issue #156](https://github.com/luanmorenommaciel/apex/issues/156) is recorded in
`VALIDATION.md`, section "Console gate follow-up — local evidence, 2026-10-07".
It separates the original six live ordering controls, the corrected cleanup
proof, the existing-job HTTP proof and the final offline combination. The
historical results below precede this extension and remain historical.

**Cleanup boundary.** Default mode removes only its fixture's exact job IDs
from the six job-keyed contract tables and its exact fingerprint from
`plan_memory`. When `spark_jobs_1m` exists in the configured session database,
it also deletes those job IDs from that rollup, waiting for the mutations.
Deleting `spark_events` alone does not retract an incremental materialized
view's target. An explicitly absent rollup supports older schemas; a failed
existence query is an error, not absence. The writer needs deletion permission
on the rollup too when present. Store or permission failure during cleanup
propagates; do not assume the fixture was removed after an error.

**Invalid timestamps.** The primary findings check names a timestamp that is
null, of the wrong type or outside the console's wire pattern before sorting.
It reports `FAIL` without converting or guessing the value; a single invalid
row is still a defect. This is a format check, not calendar validation. Existing
runs without tied findings retain `NOT EXERCISED` on both tie-break checks.

**Recorded result**, 2026-09-29, `clickhouse/clickhouse-server:24.8` — the
image `infra/docker-compose.yml` pins — with `infra/sql/` 001–032 and
`front/contract/01-readonly-user.sql` applied, in a disposable container:

```text
17 passed · 0 failed · 0 not exercised          (default mode)
12 passed · 0 failed · 2 not exercised          (--job-id, one finding, no transitions)
CONSOLE_PARITY_GATE=PASS
```

After every default run each contract table held 0 rows: the gate removed what
it seeded.

**Recorded 2026-10-06 against the long-lived infra stack** (`infra/` compose,
ClickHouse 24.8, `make apply-ddl` current), in both modes:

| Mode | Job | Result |
|---|---|---|
| default (seeded) | — | `17 passed · 0 failed · 0 not exercised`, 0 rows left behind |
| `--job-id --api-url` against a running `apex-api` | `app-20260728210428-0004` (July) | `15 passed · 1 not exercised` (indexed) |
| `--job-id --api-url` | `app-20261006193136-0000` (generated, old image) | `14 passed · 2 not exercised` |
| `--job-id --api-url` | `app-20261006195655-0002` (generated, current jar) | `13 passed · 3 not exercised` — its three findings happen to be in ts order too |

Those three jobs went Spark → plugin → OTLP → this store → engine → memory →
API → every console screen in one run of `tests/e2e/console_reflection.sh`;
`serve/VALIDATION.md` has the record and what it found.

**The gate was checked against the defects it exists for.** Each was put back
in a scratch copy and the gate was run on it:

| Defect put back | What the gate said |
|---|---|
| findings route serves the MCP's projection | `columns differ — browser only ['ts'], api only ['app_id']` |
| transitions route serves every `update_seq` | `browser returned 2, api returned 4` |
| serve's rollup reads `ifNull()` | `task_time_ms: browser -1 != api 0` |
| the console's rollup reads `ifNull()` | `task_time_ms: browser 0 != api -1` |
| the API stops pinning its timestamps | `browser '…T19:00:20.123' != api '…T19:00:20.123000'` |

**Timestamps.** Every timestamp on the resource tier and on `/v1/health` leaves
in one format — ISO 8601 with a `T`, UTC, millisecond precision, no offset —
set in `src/apex_api/wire.py`. The console brings its ClickHouse and fixture
paths to the same format, so a row reads the same whichever door it came
through. The diagnostics tier is not covered: its payloads are the MCP tools'
own models.

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
VITE_APEX_API_PROXY_TARGET=http://127.0.0.1:8099 \
VITE_APEX_API_TOKEN=local-dev-token-a1b2c3 \
npm run dev
```

`VITE_APEX_API_PROXY_TARGET` configures the **dev server**, not the bundle. The
browser keeps calling `/v1` relative; Vite forwards it here and nginx forwards
it in the image, so the browser stays on one origin and apex-api needs no CORS
header — the same arrangement `/clickhouse` has always used.

`VITE_APEX_API_URL` is a different thing: it sets the browser's own base and
makes it call the API **directly, cross-origin**, bypassing the proxy. The API
sends no CORS header, so a browser blocks that. Leave it empty unless you mean
it. (These were one variable until the PR #129 review; sharing them made the
documented command defeat its own proxy.)

In a container:

| Variable | Purpose |
|---|---|
| `DATA_SOURCE=http` | select the API path |
| `APEX_API_UPSTREAM` | where nginx forwards `/v1` (defaults to an unroutable address, so a ClickHouse-mode image still boots) |
| `APEX_API_TOKEN` | the bearer token, written into `/config.js` |
| `APEX_API_URL` | only for a deliberate cross-origin call; normally unset |

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

- The MCP server still reads ClickHouse directly. Routing it through this API
  was planned and dropped: its tools need store primitives (`search`,
  `similar_plans`, `prior_outcomes`, …) that no route exposes.
- `/ask` is unimplemented; the console's chat screen is a scripted mockup.
