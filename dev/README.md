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
runner timeout above seven minutes. The full run log is not committed (build logs are gitignored); reproduce it with `make c3-full`.

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
make gen-data                # deterministic 10M-row ~50% hot-key fact + dim Delta tables
make run-pathology JOB=skew_join
make calibrate RUNS=3        # prove each pathology is mechanical (3-run signal CVs + noise floor)
make down                    # stop (keep data)   |   make clean = down -v (full reset)
```

Ports (host, overridable in `.env`): MinIO API `:9010` (shifted off `:9000` to dodge the collect-lane ClickHouse), MinIO console `:9001`, Spark master `:8080`, History Server `:18080`.

## The pathologies

Each job self-configures its pathology conf (**AQE OFF + `autoBroadcastJoinThreshold=-1`** so it can't self-heal), seeds every `rand()`, and relies on `ApexPlugin` to emit one canonical event per completed stage through OTLP.

| `JOB=` | What it triggers | Signal in canonical ClickHouse telemetry | Toggles |
|---|---|---|---|
| `skew_join` | two hot keys (~25% each of 10M rows) → two ~26 MB shuffle partitions on a sort-merge join over ~113 MB (payload-carrying query — see Calibration) | p99/p50 ≈ 22-28× on the 100-task join reduce stage (tail-bound, see below) + hot-task spill | `AQE=on` |
| `spill` | global sort of the full 10M-row fact (~200 MB) under a starved memory pool + few partitions | `spill_disk_bytes` ≈ 230 MB every run (CV ~2%) | `FIX=on` |
| `bad_shuffle` | `shuffle.partitions=2` → two ~65 MB reduce tasks | a shuffle-read stage with `task_count=2`; giant-task duration CV ~5% | `FIX=on` |
| `driver_oom` | `collect()` of ~5 GB to a 512 MB driver | driver process OOMs (3/3 runs); pre-collect stages persist in ClickHouse | `SAFE=on` |

**Toggles** (`make run-pathology JOB=… TOGGLE=on`):
- **`AQE=on`** (skew_join) — enables Adaptive Query Execution. Each hot partition (~26 MB) is ~1.6× the cell's `skewedPartitionThresholdInBytes` (16m), so the runtime **skew-split fires by data volume**: AQE splits both hot partitions (~4 subpartitions each, 17-task stage) and coalesces the cold ones. This is the scenario the jar lane's `plan_transition` differentiator captures, and it lands as a `transition_type='skew_split'` (HIGH) row in `apex.plan_transitions`. Runs the same query, so fingerprints match.
- **`FIX=on`** (spill, bad_shuffle) — the healthy config (more memory / partitions). Produces a non-pathological baseline so `engine`/`serve` `compare_runs` has something to diff the pathology against. `bad_shuffle FIX=on` doubles as the calibration harness's noise-floor control.
- **`SAFE=on`** (driver_oom) — collect only a small sample instead of OOMing.

### Calibration (2026-07-28): mechanism, not noise

The verify lane proved the old jobs produced *measurement noise*: the skew_join
query let Catalyst prune everything except the INT join key (and a bare
`.count()` action pruned even the aggregate), so the whole join exchange
shuffled ~10 MB at ~2 B/row and the hot partition (~5 MB) sat **below**
`spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes`. AQE had no real
reason to split, and the "critical 21.62× skew" on a 95-bytes-per-task stage was
JVM/scheduler jitter — three byte-identical runs gave 21.62× / 24.71× / 24.53×.

Fixes applied here:

1. **Payload-carrying query** (`skew_join.py`): `sum(amount)` + a downstream
   `sum()` action pins the double payload into the join exchange → ~113 MB
   shuffled. Without the consuming action, Catalyst drops the aggregate as
   unused and the exchange degenerates to bare int keys (measured).
2. **Scale**: default `APEX_ROWS` raised 5M → 10M (still seeded/deterministic;
   `grand_total` is byte-identical across every run/config: 4,999,507,894.6).
3. **Staleness marker** (`common/data.py`): `ensure_data` checks a `_gen_meta`
   marker (version/rows/seed/partitions) and regenerates on mismatch —
   previously ANY existing fact table was silently reused, so scale changes
   never took effect.
4. **Two hot keys (~25% each), not one 50% key**: percentile statistics
   (Spark's taskSummary AND the plugin's p99 in `spark_events`) interpolate /
   nearest-rank p99 to a *cold* task when a single task in a hundred is hot —
   measured: plugin p99/p50 = 12.46× on a stage whose max task was 53× the
   median. Two hot tasks put the skew above the p99 rank, so the statistic the
   engine actually consumes sees it. Each hot partition stays >16 MB so the
   AQE split still fires (on both).
5. **n=100 reduce partitions** (`skew_join.py`): at the 200-task default the
   hot tasks were ranks 199/200 and p99 stayed cold.
6. **8 worker slots** (measured minimum 6): verify's closed form — a stage is
   tail-bound iff `p99/p50 > (n_tasks−1)/(slots−1)` — needs
   `(100−1)/(slots−1)` below the measured 22-28× ratio. **2 slots can NEVER
   satisfy it** (the duration ratio is bounded by the bytes ratio n−1 = 99);
   4 slots (threshold 33) fails on the plugin's interpolated p99; 6 slots
   (19.8) passes with only ~1.1× margin; 8 slots (14.1) gives 1.5-2×.
7. **Telemetry routing**: two bugs made whole apps vanish from ClickHouse
   (~50-70% loss). (a) `apex-infra-otel-collector` held a manual
   `--alias apex-otel-collector` on `apex-collect-net`, so DNS round-robined
   between the collect collector and infra's — and infra's exporter resolved
   `clickhouse` to collect's *throwaway* ClickHouse (no reshape MVs). Removed
   the alias at runtime (2026-07-28); a file-level fix belongs to infra/.
   (b) `make run-pathology`'s plain `up` recreated containers OFF the C3
   overlay; the Makefile now composes with the overlay whenever
   `apex-collect-net` exists. Plus a 5 s pre-stop OTLP drain in
   `common/session.py` (`stop_session`) for the plugin's bounded queue.

**Proof harness** — `make calibrate RUNS=3` runs every pathology 3×, pulls the
real stage metrics from the History Server AND the plugin's own p50/p99 from
`apex.spark_events`, evaluates verify's tail-bound closed form with the live
slot count from the master API, checks the `skew_split` transition per AQE run,
and reports signal CVs against a noise-floor control (`bad_shuffle FIX=on`, a
balanced 200-partition reduce over the same data). Full numbers: latest
`out/calibration-*.json`. A signal whose CV is comparable to the noise floor is
reported as noise, not a pathology.

**Measured at the shipping cell (2026-07-28, 10M rows, n=100, 1 worker × 8
cores/2g = 8 slots, 3 runs each; noise floor = control max-task-duration CV):**

| Pathology | Volume (identical every run) | Mechanism | Signal | 3-run CV |
|---|---|---|---|---|
| `skew_join` | join shuffle 112,930,867 B; hot partitions 2 × 26,146,301 B (1.6× the 16m AQE threshold) | SMJ forced, payload carried, n=100 | p99/p50 = 18.9/20.6/19.4 (REST), 17.7/18.7/19.4 (plugin) — **tail-bound ✓ every run** vs threshold (100−1)/(8−1) = 14.14 | 4.4% (floor 9.2%) |
| `skew_join AQE=on` | same data; split stage = 17 tasks, split sub-partition 7,934,642 B | AQE splits both hot partitions ×4, coalesces cold | `skew_split` (HIGH) + 2 `coalesce` rows in `apex.plan_transitions` **3/3 runs** | — |
| `spill` | 209-211 MB spilled to disk every run | starved pool (fraction 0.1) + 2 pinned executor cores + 8 partitions | `spill_disk_bytes` = 209,067,592 / 209,064,633 / 210,655,879 | 0.4% |
| `bad_shuffle` | reduce stage = 2 tasks × 65,782,456 B | `shuffle.partitions=2` | `task_count=2` + giant tasks 1.9/2.4/2.1 s — bytes exact; giant-task wall CV 11% ≈ floor (durations are the floor, bytes are the mechanism) | 0% (bytes), 11% (wall) |
| `driver_oom` | collect of ~5 GB → 512 MB driver | result materialization > heap | `OutOfMemoryError` **3/3**, ~25 s each | binary |
| noise floor | control = balanced 200-task reduce, 137 MB | — | max-task durations 214/255/249 ms | **9.2%** |

The duration noise floor at this scale is ~9% (it was ~5.8% at the old tiny
scale); bytes-based signals are CV ≈ 0-0.4% — those are the mechanical ones.
Jitter alone still produces p99/p50 of 8-12× on balanced stages, which is why
the acceptance is the *closed form* (ratio vs `(n−1)/(slots−1)`), not a fixed
10× gate: control stages measure 9.3/11.9/7.7 vs their 28.4 threshold (never
tail-bound), the skew stage measures ~19× vs its 14.14 threshold (always
tail-bound).

**Laptop tradeoff:** 10M rows is the smallest volume that keeps both hot
partitions comfortably above the 16m AQE threshold *with the payload query*
(~26 MB each). Jobs run in ~20-35 s each on one 8-core/2g worker (6 cores is
the measured tail-bound minimum; 2 cores is *provably* insufficient for a
single-worker lab — see fix 6). No bigger cluster is needed for any of the
four mechanisms; add workers (`make scale WORKERS=N`) only to shorten wall
time — the generator's pinned `numPartitions=16` keeps the data byte-identical
regardless.

### driver_oom notes
`spark.driver.memory` is set at **submit** time (`--driver-memory 512m`, injected automatically by the Makefile) — the driver JVM heap is fixed at launch, so setting it in-code is too late. A shuffle stage runs and completes **before** the fatal `collect()`; `ApexPlugin` exports it through OTLP and C7 requires that it materialize in ClickHouse. Because the driver crashes before `spark.stop()`, the event log stays `.inprogress` and the **History Server entry is incomplete** — that is the correct, expected outcome for a driver OOM.

## Determinism & reproducibility

- **Pinned everything:** the default quartet (Spark 4.0.1 · Hadoop/hadoop-aws 3.4.1 · Delta 4.0.0/Scala 2.13 · AWS SDK v2 bundle 2.24.6) lives in `.env`; the additive validated 4.1.2 cell is `./.env.spark41.example` (Hadoop 3.4.2, Delta 4.1.0, `apex_41`). MinIO + mc are pinned by **image digest**.
- **Readiness-gated startup:** every service has a healthcheck; `docker compose up --wait` comes up green in dependency order. MinIO uses `mc ready local`.
- **Seeded data:** `common/data.py` seeds every `rand()` and **pins `numPartitions=16`**, so the fact table is byte-identical across runs *and* across different cluster core counts (`rand(seed)` depends on partition layout). Proven: two runs → identical `hot_rows` and identical `grand_total`.
- **Staleness-safe:** a `_gen_meta` marker (generator version, rows, seed, partitions) is written with the data; `ensure_data` regenerates deterministically on any mismatch, so stale wrong-scale tables can never silently persist.
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
