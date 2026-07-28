# infra/ — ④ ClickStack: the canonical store & serving layer

The **real, persistent ClickStack** the whole Apex pipeline stores into and visualizes from:
**ClickHouse + HyperDX + MongoDB + OTel Collector**. infra owns the ClickHouse *application*;
[`../contract/`](../contract/) owns the *schema*. This lane applies the frozen contract DDL and
adds partitioning/TTL, a job-level rollup, the reshape MVs, and skew detection.

**Obeys:** [../CONTRACT.md](../CONTRACT.md) (v0.2 + Port Map + TTL note) · **Full brief:** [../docs/lanes/INFRA.md](../docs/lanes/INFRA.md)

**Exit criterion (proven):** a `curl`'d OTLP/HTTP span → `apex.spark_events` (via MV) → a HyperDX
tile **and** the skew query both return it, all threaded by `job_id`.

Os gates locais desta branch e a referência da evidência integrada estão em
[`VALIDATION.md`](VALIDATION.md).

```
  jar / collect ──OTLP:4318──▶ otel-collector ──native:9000──▶ ClickHouse ◀──HTTP:8123── HyperDX ──state──▶ MongoDB
                                                              apex.otel_traces                (UI :8090)      (:27017)
                                                                    │ mv_spark_events / mv_plan_transitions
                                                                    ▼
                                                     apex.spark_events ──spark_jobs_1m_mv──▶ apex.spark_jobs_1m (rollup)
                                                     apex.plan_transitions                    apex.findings (engine writes)
```

## Layout

| Path | What |
|---|---|
| `docker-compose.yml` | 4 services (clickhouse, mongodb, hyperdx, otel-collector) |
| `.env.example` / `.env` | host ports + creds (`.env` is gitignored; canonical Port Map in `.env.example`) |
| `otel-collector-config.yaml` | contrib collector → `apex.otel_traces` (interop-identical to collect) |
| `sql/001..032` | DDL, auto-applied on first ClickHouse init (see below) |
| `Makefile` | `make apply-ddl` / `make verify-ddl` — schema guardrails (see below) |
| `scripts/apply_ddl.sh` | idempotently applies every `sql/*.sql` to the RUNNING ClickHouse |
| `scripts/verify_ddl.py` | DESCRIBEs each contract table and diffs it against its DDL source of truth |
| `scripts/seed.sh` | ~50 stage spans via the real OTLP path (ts=now, TTL-safe) + stand-in findings |
| `scripts/verify.sh` | exit-criterion healthcheck; exits 0 when a job_id threads all 3 tables |
| `dashboards/skew_dashboard.json` | per-tile skew dashboard build-spec |
| `HYPERDX_SETUP.md` | **exact** custom-Source + rollup-registration steps (scripted + manual) |

### `sql/` — applied in filename order on first boot
`001` db · `002` spark_events *(contract)* · `003` findings *(contract, incl. idempotent
ALTERs for pre-existing volumes)* · `004` rollup + incremental MV · `005` skew queries ·
`010` otel_traces landing table · `011` plan_transitions *(contract v0.2)* ·
`013` job_conf *(contract v0.4)* · `020`/`021` reshape MVs (`mv_spark_events`,
`mv_plan_transitions`, `mv_job_conf`) · `030`/`031` plan_memory + run_outcomes
*(ratified v0.3, mirror of `memory/sql/`)* · `032` fix_verifications *(ratified v0.3,
mirror of `verify/ddl/`)*.

> **⚠️ First-boot-only gotcha:** ClickHouse runs `/docker-entrypoint-initdb.d` ONLY on a
> fresh volume. On a pre-existing volume, any `sql/` file added later is **silently
> skipped** — the schema looks applied while it lags the contract. The guardrails:
>
> ```bash
> make apply-ddl   # idempotently apply every sql/*.sql, in order, to the RUNNING instance
> make verify-ddl  # DESCRIBE each contract table; exit 1 on ANY drift vs its DDL source
> ```
>
> Idempotency lives in the files: `CREATE ... IF NOT EXISTS` everywhere, plus
> `ALTER ... ADD COLUMN IF NOT EXISTS` for columns added to tables that predate them.
> Run both after pulling new DDL; CI/lanes can treat `verify-ddl`'s exit code as schema truth.

`012_otel_logs.sql` is the exporter-owned OTLP logs landing table. It is needed
when the canonical `collect/` pipeline is connected to infra, because that
pipeline declares both trace and log exporters even though the current Spark
plugin emits spans only.

> **Schema authority:** `002/003/011/013` are the contract tables applied **verbatim** — never
> rename/repurpose a column. `030/031/032` **mirror `memory/sql/` + `verify/ddl/`** (the lanes own
> the DDL; infra owns applying it). `010` + `020`/`021` **mirror `collect/ddl/`** so a span landing in
> `otel_traces` reshapes identically whether it came via infra's collector or collect's. If infra
> and a lane ever differ on a table, **the lane's source of truth wins and infra re-mirrors.**

## Ports (CONTRACT.md Port Map — infra's band)

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
cp .env.example .env            # then set HYPERDX_API_KEY=$(openssl rand -hex 32)
# if 8123/9000/4318 are taken on your host, uncomment the shifted band in .env
docker compose up -d            # 4 services; clickhouse applies sql/ on first init
./scripts/seed.sh               # ~50 spans via OTLP (ts=now) + stand-in findings
./scripts/verify.sh             # exit 0 = store proven end-to-end
```

Then open **http://localhost:8090**, register the first user (seeds the ClickHouse connection +
the **Spark Events** custom Source automatically), and Search the source. See
[`HYPERDX_SETUP.md`](HYPERDX_SETUP.md).

## Point collect/ at this ClickHouse (the integration path)

infra's own collector is the self-contained one. In the full pipeline, **collect's** collector is
the OTLP receiver and writes into **this** ClickHouse (both write the identical `apex.otel_traces`,
so the reshape MVs fire either way). To wire collect → infra:

- Attach collect's `otel-collector` to network `apex-infra-net` (or set its clickhouse exporter
  endpoint to `tcp://host.docker.internal:29000`), with `CLICKHOUSE_USER/PASSWORD` = `apex` /
  `.env` value. A POSTed `apex.stage` span then lands in **this** `apex.spark_events` via the MV.

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
   `DEFAULT_CONNECTIONS`, `MONGO_URI`). Never use the short service name on a shared network.
2. **Never `docker network connect --alias` a foreign name onto a container.** If a container
   must join another lane's network, join it with no alias or with its own `apex-<lane>-*` name.
   Check for squatters with `docker network inspect <net> | grep -A2 Aliases`.

## Teardown

```bash
docker compose down            # stop; KEEP volumes (Mongo state + CH data persist)
docker compose down -v         # also wipe volumes (fresh DB; re-register + re-seed next up)
```

## Notes / gotchas (verified)

- **MongoDB is required** — HyperDX stores dashboards/sources/connections/users there, not in
  ClickHouse. Verified: after `down`+`up` the team/source/connection survive.
- **TTL gotcha** — 90-day TTL on `ts`; the June-2024 fixture ts TTL-expires on merge. Seed with
  `ts=now()` (seed.sh does).
- **`attributes` is `Map(String,String)`**, not the beta JSON type.
- **HyperDX custom Source** — set every expression or it returns nothing (Timestamp=`ts`,
  Service=`app_id`, attributes=`attributes`, Trace Id=`job_id`). Scripted here via `DEFAULT_SOURCES`.
- **Rollup** — `AggregatingMergeTree` + incremental MV, quantile **states** (not final values),
  1-min buckets, `<aggFn>__<col>` naming for HyperDX acceleration. MV is BETA/not backfilled.
- **HyperDX image** — the brief's `clickhouse/hdx-oss-v2` isn't a real repo; use
  `hyperdx/hyperdx:2` (= `docker.hyperdx.io/hyperdx/hyperdx`). Override via `HDX_IMAGE` in `.env`.
