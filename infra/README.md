# infra/ — ④ ClickStack: the canonical store & serving layer

The **real, persistent ClickStack** the whole Apex pipeline stores into and visualizes from:
**ClickHouse + HyperDX + MongoDB + OTel Collector**. infra owns the ClickHouse *application*;
[`../contract/`](../contract/) owns the *schema*. This lane applies the frozen contract DDL and
adds partitioning/retention, a job-level rollup, the reshape MVs, and the canonical skew SQL.

**Obeys:** [../CONTRACT.md](../CONTRACT.md) (v0.6 + Port Map + rule 1) · **Full brief:** [../docs/lanes/INFRA.md](../docs/lanes/INFRA.md)

**Exit criterion (proven):** a `curl`'d OTLP/HTTP span → `apex.spark_events` (via MV) → a HyperDX
tile **and** the skew query both return it, all threaded by `job_id`.

Os gates locais desta branch e a referência da evidência integrada estão em
[`VALIDATION.md`](VALIDATION.md).

```
  jar / collect ──OTLP:4318──▶ otel-collector ──native:9000──▶ ClickHouse ◀──HTTP:8123── HyperDX ──state──▶ MongoDB
                                                              apex.otel_traces                (UI :8090)      (:27017)
                                                                    │ mv_spark_events / mv_plan_transitions / mv_job_conf
                                                                    ▼
                                                     apex.spark_events ──spark_jobs_1m_mv──▶ apex.spark_jobs_1m (rollup)
                                                     apex.plan_transitions · apex.job_conf   apex.findings (engine writes)
```

## Layout

| Path | What |
|---|---|
| `docker-compose.yml` | 6 services: clickhouse, **ddl-migrate** (one-shot, every `up`), mongodb, hyperdx, **queue-init** (one-shot), otel-collector — every image pinned `tag@sha256` |
| `.env.example` / `.env` | host ports, bind address, memory limits, credentials (`.env` is gitignored; all credentials REQUIRED, none defaulted) |
| `config.d/backups.xml` | ClickHouse backups disk for `make backup` / `make restore` |
| `otel-collector-config.yaml` | contrib collector → `apex.otel_traces` (interop-identical to collect); password from the compose secret file; persistent `file_storage` queue |
| `sql/001..050` | DDL, auto-applied on first ClickHouse init and re-applied by `ddl-migrate` on every `up` (see below) |
| `Makefile` | `make up` (preflight → compose → bootstrap) · `apply-ddl` · `verify-ddl` · `backup` / `restore` |
| `scripts/preflight.sh` | refuses missing/default credentials; renders the gitignored `secrets/` + `.local/` runtime files |
| `scripts/apply_ddl.sh` | idempotently applies every `sql/*.sql` (host mode, or container mode inside `ddl-migrate`) |
| `scripts/verify_ddl.py` | compares every object in `scripts/ddl_manifest.txt` — tables **and** MVs — clause by clause against its DDL sources |
| `scripts/ddl_manifest.txt` | the ONE list of store objects; `verify.sh`, `tests/e2e/run.sh` and `scripts/apex.ps1` read it too |
| `scripts/hyperdx_bootstrap.sh` | registers HyperDX's first user through the API (idempotent) — that is what seeds the connection + source |
| `scripts/seed.sh` | ~50 stage spans via the real OTLP path (ts=now, TTL-safe) + stand-in findings |
| `scripts/verify.sh` | exit-criterion healthcheck; exits 0 when a job_id threads all 3 tables and a stage is tail-bound |
| `scripts/backup.sh` / `restore.sh` | `BACKUP DATABASE apex` + `mongodump`, and the reverse (beside the live data, or over it with `--force`) |
| `dashboards/skew_dashboard.json` | per-tile skew dashboard build-spec, tiles mirror `sql/050` verbatim |
| `HYPERDX_SETUP.md` | **exact** custom-Source + rollup-registration steps (scripted + manual) |

### `sql/` — applied in filename order on first boot, re-applied on every `up`
`001` db · `002` spark_events *(contract v0.5)* · `003` findings *(contract, + 365-day TTL)* ·
`004` rollup + incremental MV *(every v0.5 column)* · `010` otel_traces landing table *(14-day TTL)* ·
`011` plan_transitions *(contract v0.2)* · `012` otel_logs *(14-day TTL)* · `013` job_conf *(contract v0.4)* ·
`020`/`021` reshape MVs (`mv_spark_events`, `mv_plan_transitions`, `mv_job_conf`) ·
`030`/`031` plan_memory + run_outcomes *(ratified v0.3, mirror of `memory/sql/`)* ·
`032` fix_verifications *(ratified v0.3, mirror of `verify/ddl/`, + 365-day TTL)* ·
`033` dedup window *(existing volumes; fresh ones carry it in the base DDL)* ·
`034`–`039` v0.5 `ADD COLUMN`s *(existing volumes)* · `040` the ONE `mv_spark_events` resync *(existing volumes)* ·
`041` rollup v0.5 columns *(existing volumes)* · `042` retention *(existing volumes)* ·
`050` canonical skew queries *(SELECT-only; after every DDL because (A) joins `job_conf`)*.

> **First-boot-only gotcha, closed:** ClickHouse runs `/docker-entrypoint-initdb.d` ONLY on a
> fresh volume. The `ddl-migrate` one-shot service therefore re-applies `sql/` on **every**
> `docker compose up`, after clickhouse is healthy and before hyperdx/otel-collector start.
> The guardrails stay available by hand:
>
> ```bash
> make apply-ddl   # idempotently apply every sql/*.sql, in order, to the RUNNING instance
> make verify-ddl  # every object in ddl_manifest.txt vs its sources: columns, engine, keys, TTL, settings, MV query
> ```
>
> Idempotency lives in the files: `CREATE ... IF NOT EXISTS` everywhere, `ALTER ... ADD COLUMN IF
> NOT EXISTS` / `MODIFY QUERY` / `MODIFY TTL` for volumes that predate a change. The `infra` CI job
> boots a fresh store from `sql/` and runs every live test on it (`tests/infra/`).

> **Schema authority:** `002/003/011/013` are the contract tables applied **verbatim**; `030/031/032`
> mirror `memory/sql/` + `verify/ddl/`; `010/012` + `020`/`021` mirror `collect/ddl/` so a span landing
> in `otel_traces` reshapes identically whether it came via infra's collector or collect's. Columns,
> engine and keys are the lane's; **TTL and SETTINGS are infra's** (retention is a storage policy).
> `verify-ddl` enforces exactly that split, and `tests/infra/test_mv_single_query.py` keeps the three
> copies of the reshape MV query (`020`, `040`, `collect/ddl/30`) byte-equal.

## Ports (CONTRACT.md Port Map — infra's band)

Every host port binds to **`127.0.0.1`** by default (`BIND_HOST` in `.env`). Other lanes reach
infra over the Docker network by container name (`apex-infra-clickhouse`, …), never via a host port.

| Service | Container | Host (default) | Host (this dev box) |
|---|---|---|---|
| ClickHouse HTTP | 8123 | 8123 | **28123** |
| ClickHouse native | 9000 | 9000 | **29000** |
| HyperDX UI | 8090 | **8090** (NOT 8080 — dev owns it) | 8090 |
| HyperDX API | 8000 | 8000 | 8000 |
| HyperDX OpAMP | 4320 | 4320 | 4320 |
| MongoDB | 27017 | 27017 | 27017 |
| OTLP/HTTP | 4318 | 4318 | **24318** |
| OTLP/gRPC | 4317 | 4317 | **24317** |

> ⚠️ **Host hygiene:** on the shared dev host a stray **`oteru-collector`** squats `8123/9000/4318`
> and **collect** runs on `18123/19000/14318`. The committed `.env.example` defaults to the
> canonical Port Map; the local `.env` **shifts ClickHouse→28123/29000 and the collector→24318/24317**
> to dodge the squatter. HyperDX stays canonical (8090/8000/4320 were free). Don't touch the stray stack.

## Quick start

```bash
cd infra
cp .env.example .env
# set the four REQUIRED values (the stack refuses empty or default ones):
#   CLICKHOUSE_PASSWORD=$(openssl rand -hex 24)   HYPERDX_API_KEY=$(openssl rand -hex 32)
#   HYPERDX_ADMIN_EMAIL=you@example.com           HYPERDX_ADMIN_PASSWORD=<12+ chars>
# if 8123/9000/4318 are taken on your host, uncomment the shifted band in .env
make up                                   # preflight → compose up --wait (ddl-migrate runs) → HyperDX first user
./scripts/seed.sh                         # ~50 spans via OTLP (ts=now) + stand-in findings
APEX_CLUSTER_SLOTS=8 ./scripts/verify.sh  # exit 0 = store proven end-to-end (seed data is tail-bound at 8)
make verify-ddl                           # every object matches its DDL sources
```

Then open **http://localhost:8090** and log in as `HYPERDX_ADMIN_EMAIL` — the connection
(**as the read-only `apex_hdx` user**) and the **Spark Events** custom Source were seeded when the
bootstrap created the team. See [`HYPERDX_SETUP.md`](HYPERDX_SETUP.md).

## Security model (what `preflight.sh` enforces)

- **No default credentials.** `CLICKHOUSE_PASSWORD`, `HYPERDX_API_KEY` (64 hex) and the HyperDX
  admin pair are required; `apex_local_dev` / `change-me*` are refused; `docker compose config`
  itself fails without a password.
- **The admin password is a file, not an environment variable.** preflight renders it to
  `secrets/clickhouse_password` (gitignored); ClickHouse reads `CLICKHOUSE_PASSWORD_FILE`, the
  collector `${file:...}`, both as a compose secret. `docker inspect` of no `apex-infra-*`
  container shows it.
- **HyperDX connects as `apex_hdx`**, a read-only user (`readonly=2`, SELECT on the tables its
  source reads) declared in `.local/users.d/apex-hyperdx.xml` with a **sha256 hash**, never the
  admin password.
- **The console's browser-shipped user `apex_ro`** (front/contract/01-readonly-user.sql) is granted
  the seven tables it queries, not `apex.*` — the raw `otel_*` landing tables are refused.
- **Loopback by default**, see Ports.

## Retention (decision D-8 in `tasks/.plans/infra-hardening.intent.md`)

| Tables | TTL | Why |
|---|---|---|
| `otel_traces`, `otel_traces_trace_id_ts`, `otel_logs` | **14 days** | raw landing only — every span is reshaped into the contract tables |
| `spark_events`, `plan_transitions`, `job_conf`, `spark_jobs_1m` | 90 days | the contract tables |
| `findings`, `fix_verifications`, `plan_memory`, `run_outcomes` | 365 days | derived knowledge outlives the raw events |

`make backup` snapshots ClickHouse (`BACKUP DATABASE apex` to the backups disk, copied to
`./backups/`) and Mongo (`mongodump`); `make restore FILE=... INTO=<db>` restores beside the live
data, `FORCE=1` over it. Replica is out of scope: a single node by design.

## Point collect/ at this ClickHouse (the integration path)

infra's own collector is the self-contained one. In the full pipeline, **collect's** collector is
the OTLP receiver and writes into **this** ClickHouse (both write the identical `apex.otel_traces`,
so the reshape MVs fire either way). To wire collect → infra:

```bash
cd collect
APEX_INFRA_CLICKHOUSE_PASSWORD="$(cat ../infra/secrets/clickhouse_password)" \
docker compose -f docker-compose.yml -f docker-compose.c3-infra.yml \
  --env-file .env.example --env-file .env.c3-infra.example up -d
```

The overlay **refuses** to start without `APEX_INFRA_CLICKHOUSE_PASSWORD`: a collector that
authenticates with the wrong password drops every span silently, which is exactly how 50–70% of
telemetry once vanished.

### Shared-network alias rule (hard-won; breaking it cost us 50–70% of telemetry)

Compose gives every service a short network alias equal to its service name. Both infra's and
collect's ClickHouse therefore answer to `clickhouse` — on a shared network that alias resolves
to **both** containers and Docker DNS round-robins between them. Spans delivered to collect's
throwaway ClickHouse (no reshape MVs there) silently vanish. The same failure let a runtime
`docker network connect --alias apex-otel-collector` turn infra's collector into an impostor for
collect's container. Rules:

1. **Reference services across lanes only by their globally-unique container-name alias**
   (`apex-infra-clickhouse`, `apex-infra-otel-collector`, …) — container names are unique per
   Docker daemon, so these can never collide. Infra declares them explicitly in
   `docker-compose.yml` and uses them for every internal hop (collector exporter, HyperDX
   connection, `MONGO_URI`). Never use the short service name on a shared network.
2. **Never `docker network connect --alias` a foreign name onto a container.** If a container
   must join another lane's network, join it with no alias or with its own `apex-<lane>-*` name
   (`tests/e2e/run.sh` does exactly that). Check for squatters with `docker network inspect <net> | grep -A2 Aliases`.

## Teardown

```bash
make down                      # stop; KEEP volumes (Mongo state + CH data + backups persist)
docker compose down -v         # also wipe volumes (fresh DB; `make up` re-migrates, re-registers; re-seed)
```

## Notes / gotchas (verified)

- **MongoDB is required** — HyperDX stores dashboards/sources/connections/users there, not in
  ClickHouse. Verified: after `down`+`up` the team/source/connection survive. `hyperdx` waits for
  it to be **healthy** (the healthcheck greps for a lone `1`, so a false ping fails).
- **TTL gotcha** — retention is on `ts`; the June-2024 fixture ts TTL-expires on merge. Seed with
  `ts=now()` (seed.sh does).
- **`attributes` is `Map(String,String)`**, not the beta JSON type.
- **HyperDX custom Source** — set every expression or it returns nothing (Timestamp=`ts`,
  Service=`app_id`, attributes=`attributes`, Trace Id=`job_id`). Scripted here via `DEFAULT_SOURCES`.
- **Rollup** — `AggregatingMergeTree` + incremental MV, quantile **states** (not final values),
  1-min buckets, `<aggFn>__<col>` naming for HyperDX acceleration (`quantilesIf__` for the
  successful-sample sketches). MV is BETA/not backfilled.
- **Skew** — `sql/050` (A) judges a stage by CONTRACT rule 1, `p99/p50 > (n_tasks−1)/(slots−1)`,
  on the successful-task population; `slots` comes from `job_conf` or `APEX_CLUSTER_SLOTS`, never a
  guess; unknown width ⇒ NULL verdict + `min_slots_for_tail_bound`. There is no 5× anywhere.
- **Images** — pinned by digest; Mongo stays on the 5.0 line HyperDX itself ships (D-7). Bump a tag
  and its digest together (`.env.example` says how).
- **Collector restarts** — the sending queue is on a named volume (`file_storage`), so a restart
  during a ClickHouse outage loses nothing.
