# dev/ — ① generate

**Role:** Spark/Delta pathology lab. Deterministic jobs (skew · spill · bad-shuffle · driver-OOM) on a local standalone Spark cluster + Delta on MinIO + History Server. `ApexPlugin` emits the contract telemetry per stage through OTLP.
**Language:** Python + Docker (+ a tiny JVM helper) · **Full brief:** [../docs/lanes/DEV.md](../docs/lanes/DEV.md) · **Obeys:** [../CONTRACT.md](../CONTRACT.md)
**Exit criterion:** `make run-pathology JOB=skew_join` completes, appears in the History Server, and lands a `spark_events` row per stage keyed by `job_id`.

The image build assembles and embeds the official `apex.ApexPlugin` JAR
(Spark 4.0 and 4.1.2 / Scala 2.13, including OTel). It is activated by default
through `spark.plugins` in `conf/spark-defaults.conf`. It is the sole telemetry
path: ClickHouse telemetry comes from the plugin over OTLP.

### C3 OTLP integration

`docker-compose.c3-otlp.yml` is an explicit, optional overlay for the C3
tracer bullet. After `infra/` and the `collect` C3 overlay are running,
`make c3-plugin-skew` joins the Spark master and worker to `apex-collect-net` and submits the normal skew job with
`spark.plugins=apex.ApexPlugin` and an internal OTLP endpoint. This overlay is
not required for standalone `make up`; it is required for canonical ClickHouse
assertions such as `make e2e-canonical`.

The C3 tracer bullet was completed with `app-20260722192806-0000`: 19 plugin
spans crossed `collect` into the canonical `infra` ClickHouse, became 19
contract events, produced five deterministic skew findings, and were read by
the MCP server. The two-core local scenario took about 385 seconds; use a
runner timeout above seven minutes. Full evidence:
[`../evidence/c3-full-tracer-bullet-2026-07-22.log`](../evidence/c3-full-tracer-bullet-2026-07-22.log).

`make c4-aqe-skew` enables the dedicated AQE pathology. For a narrow runtime
calibration, `make c4-aqe-probe` mirrors the JAR AQE test and must persist a
`skew_split` row in the canonical ClickHouse store. The 4.1.2 proof recorded
that transition with `app-20260722225707-0002`.

Layout: `docker-compose.yml` · `Dockerfile` · `conf/` · `jobs/` (generate_data + 4 pathologies) · `common/` (session, fingerprint, data) · `jvm/` (test-only `PlanFingerprint`) · `scripts/` (smoke · verify · canonical E2E) · `Makefile`.

## Quickstart (fresh clone)

### Spark 4.1.2 compatibility cell

```bash
make env-spark41
make build
make up
```

`env-spark41` combines the pinned baseline with the Spark 4.1.2 overlay and
does not overwrite an existing `.env`. Remove or rename `.env` before
switching between the default and Spark 4.1.2 cells.

```bash
cd dev
cp .env.example .env         # pinned version quartet + image digests
make verify                  # proves the platform end-to-end, then tears down
# with collect + infra already running and APEX_CANONICAL_CH_PASSWORD set:
make e2e                     # canonical ClickHouse gate for all four pathologies
```

Interactive:
```bash
make up                      # build + start, waits until every service is healthy
make gen-data                # deterministic ~50% hot-key fact + dim Delta tables
make run-pathology JOB=skew_join
make down                    # stop (keep data)   |   make clean = down -v (full reset)
```

Ports (host, overridable in `.env`): MinIO API `:9010` (shifted off `:9000` to dodge the collect-lane ClickHouse), MinIO console `:9001`, Spark master `:8080`, History Server `:18080`.

## The pathologies

Each job self-configures its pathology conf (**AQE OFF + `autoBroadcastJoinThreshold=-1`** so it can't self-heal), seeds every `rand()`, and relies on `ApexPlugin` to emit one canonical event per completed stage through OTLP.

| `JOB=` | What it triggers | Signal in canonical ClickHouse telemetry | Toggles |
|---|---|---|---|
| `skew_join` | hot key (~50% of rows) → one giant shuffle partition on a sort-merge join | `task_duration_p99_ms ≫ p50` (>10×) on the join reduce stage | `AQE=on` |
| `spill` | global sort under a starved memory pool + few partitions | `spill_disk_bytes > 0` | `FIX=on` |
| `bad_shuffle` | `shuffle.partitions=2` → a couple of enormous reduce tasks | a shuffle-read stage with `task_count=2` | `FIX=on` |
| `driver_oom` | `collect()` of a multi-GB result to a 512 MB driver | driver process OOMs; pre-collect stages persist in ClickHouse | `SAFE=on` |

**Toggles** (`make run-pathology JOB=… TOGGLE=on`):
- **`AQE=on`** (skew_join) — enables Adaptive Query Execution *and* lowers the skew-join thresholds so the runtime **skew-split actually fires** on this lab's modest data. This is the scenario the jar lane's `plan_transition` differentiator captures (a real AQE re-plan). Runs the same query, so fingerprints match.
- **`FIX=on`** (spill, bad_shuffle) — the healthy config (more memory / partitions). Produces a non-pathological baseline so `engine`/`serve` `compare_runs` has something to diff the pathology against.
- **`SAFE=on`** (driver_oom) — collect only a small sample instead of OOMing.

### driver_oom notes
`spark.driver.memory` is set at **submit** time (`--driver-memory 512m`, injected automatically by the Makefile) — the driver JVM heap is fixed at launch, so setting it in-code is too late. A shuffle stage runs and completes **before** the fatal `collect()`; `ApexPlugin` exports it through OTLP and C7 requires that it materialize in ClickHouse. Because the driver crashes before `spark.stop()`, the event log stays `.inprogress` and the **History Server entry is incomplete** — that is the correct, expected outcome for a driver OOM.

## Determinism & reproducibility

- **Pinned everything:** the default quartet (Spark 4.0.1 · Hadoop/hadoop-aws 3.4.1 · Delta 4.0.0/Scala 2.13 · AWS SDK v2 bundle 2.24.6) lives in `.env`; the additive validated 4.1.2 cell is `./.env.spark41.example` (Hadoop 3.4.2, Delta 4.1.0, `apex_41`). MinIO + mc are pinned by **image digest**.
- **Readiness-gated startup:** every service has a healthcheck; `docker compose up --wait` comes up green in dependency order. MinIO uses `mc ready local`.
- **Seeded data:** `common/data.py` seeds every `rand()` and **pins `numPartitions=16`**, so the fact table is byte-identical across runs *and* across different cluster core counts (`rand(seed)` depends on partition layout). Proven: two runs → identical `hot_rows`.
- **`PYTHONHASHSEED=0`, `TZ=UTC`** on all Spark services.

## The telemetry: plan_fingerprint

`common/fingerprint.py` computes the contract `plan_fingerprint` (normalized **logical** plan → SHA-256) via the JVM helper `apexdev.PlanFingerprint`, which runs the **identical Catalyst operations as the jar's `apex.ApexPlanFingerprint`** (literal-null + canonicalized). Same query → byte-identical hash across the dev (Python) and jar (Scala) listeners — proven by `make fp-crosscheck` against the jar's compiled class. `make fp-test` proves the literal-normalization invariant (`id>100` and `id>900` → same hash).

## Telemetry path

The driver loads `apex.ApexPlugin` through `spark.plugins`. The plugin registers
the in-process Scala listener, correlates logical-plan fingerprints by execution
id, exports bounded OTLP spans, and remains fail-safe when the collector is not
reachable. The C3 overlay delivers those spans to `collect`, which materializes
`apex.spark_events` in ClickHouse. No Python callback, JSONL sink, or `setPlan()`
API remains in the runtime path.

## Future option (considered, not built): Spark Connect

Spark Connect (`sc://…`, `:15002`) would give a faster inner loop for iterating on job code. Deliberately not used: this lab's purpose is running full pathology jobs on the real 2-worker cluster where the SparkListener sees genuine stage metrics.
