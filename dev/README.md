# dev/ — ① generate

**Role:** Spark/Delta pathology lab. Deterministic jobs (skew · spill · bad-shuffle · driver-OOM) on a local standalone Spark cluster + Delta on MinIO + History Server, with a SparkListener that emits the contract telemetry per stage.
**Language:** Python + Docker (+ a tiny JVM helper) · **Full brief:** [../docs/lanes/DEV.md](../docs/lanes/DEV.md) · **Obeys:** [../CONTRACT.md](../CONTRACT.md)
**Exit criterion:** `make run-pathology JOB=skew_join` completes, appears in the History Server, and lands a `spark_events` row per stage keyed by `job_id`.

Layout: `docker-compose.yml` · `Dockerfile` · `conf/` · `jobs/` (generate_data + 4 pathologies) · `common/` (session, listener, fingerprint, data) · `jvm/` (StageListener + PlanFingerprint, compiled into the image) · `scripts/` (smoke · verify · e2e) · `Makefile`.

## Quickstart (fresh clone)

```bash
cd dev
cp .env.example .env         # pinned version quartet + image digests
make verify                  # proves the platform end-to-end, then tears down
make e2e                     # runs ALL 4 pathologies, asserts each signal, tears down
```

Interactive:
```bash
make up                      # build + start, waits until every service is healthy
make gen-data                # deterministic ~50% hot-key fact + dim Delta tables
make run-pathology JOB=skew_join
make logs-check              # tail the emitted contract rows (out/spark_events.jsonl)
make down                    # stop (keep data)   |   make clean = down -v (full reset)
```

Ports (host, overridable in `.env`): MinIO API `:9010` (shifted off `:9000` to dodge the collect-lane ClickHouse), MinIO console `:9001`, Spark master `:8080`, History Server `:18080`.

## The pathologies

Each job self-configures its pathology conf (**AQE OFF + `autoBroadcastJoinThreshold=-1`** so it can't self-heal), seeds every `rand()`, attaches the listener, and emits one contract record per stage to `out/spark_events.jsonl`.

| `JOB=` | What it triggers | Signal in `spark_events.jsonl` | Toggles |
|---|---|---|---|
| `skew_join` | hot key (~50% of rows) → one giant shuffle partition on a sort-merge join | `task_duration_p99_ms ≫ p50` (>10×) on the join reduce stage | `AQE=on` |
| `spill` | global sort under a starved memory pool + few partitions | `spill_disk_bytes > 0` | `FIX=on` |
| `bad_shuffle` | `shuffle.partitions=2` → a couple of enormous reduce tasks | a shuffle-read stage with `task_count=2` | `FIX=on` |
| `driver_oom` | `collect()` of a multi-GB result to a 512 MB driver | driver process OOMs; pre-collect stage records still on disk | `SAFE=on` |

**Toggles** (`make run-pathology JOB=… TOGGLE=on`):
- **`AQE=on`** (skew_join) — enables Adaptive Query Execution *and* lowers the skew-join thresholds so the runtime **skew-split actually fires** on this lab's modest data. This is the scenario the jar lane's `plan_transition` differentiator captures (a real AQE re-plan). Runs the same query, so fingerprints match.
- **`FIX=on`** (spill, bad_shuffle) — the healthy config (more memory / partitions). Produces a non-pathological baseline so `engine`/`serve` `compare_runs` has something to diff the pathology against.
- **`SAFE=on`** (driver_oom) — collect only a small sample instead of OOMing.

### driver_oom notes
`spark.driver.memory` is set at **submit** time (`--driver-memory 512m`, injected automatically by the Makefile) — the driver JVM heap is fixed at launch, so setting it in-code is too late. A shuffle stage runs and completes **before** the fatal `collect()`; the JVM listener writes each stage record the moment the stage completes, so the OOM never loses that telemetry. Because the driver crashes before `spark.stop()`, the event log stays `.inprogress` and the **History Server entry is incomplete** — that is the correct, expected outcome for a driver OOM.

## Determinism & reproducibility

- **Pinned everything:** version quartet (Spark 4.0.1 · Hadoop/hadoop-aws 3.4.1 · Delta 4.0.0/Scala 2.13 · AWS SDK v2 bundle 2.24.6) in `.env`; MinIO + mc pinned by **image digest**.
- **Readiness-gated startup:** every service has a healthcheck; `docker compose up --wait` comes up green in dependency order. MinIO uses `mc ready local`.
- **Seeded data:** `common/data.py` seeds every `rand()` and **pins `numPartitions=16`**, so the fact table is byte-identical across runs *and* across different cluster core counts (`rand(seed)` depends on partition layout). Proven: two runs → identical `hot_rows`.
- **`PYTHONHASHSEED=0`, `TZ=UTC`** on all Spark services.

## The telemetry: plan_fingerprint

`common/fingerprint.py` computes the contract `plan_fingerprint` (normalized **logical** plan → SHA-256) via the JVM helper `apexdev.PlanFingerprint`, which runs the **identical Catalyst operations as the jar's `apex.ApexPlanFingerprint`** (literal-null + canonicalized). Same query → byte-identical hash across the dev (Python) and jar (Scala) listeners — proven by `make fp-crosscheck` against the jar's compiled class. `make fp-test` proves the literal-normalization invariant (`id>100` and `id>900` → same hash).

## The listener

`common/listener.py` attaches a **JVM** SparkListener (`jvm/StageListener.java`) rather than a py4j Python listener: under Spark 4.0's py4j ClientServer gateway, JVM→Python callbacks on the async listener bus are unreliable. A JVM listener is invoked in-process by Spark (robust, and closer to how the real jar captures). Python only makes Python→JVM calls (construct, register, `setPlan`).

## Future option (considered, not built): Spark Connect

Spark Connect (`sc://…`, `:15002`) would give a faster inner loop for iterating on job code. Deliberately not used: this lab's purpose is running full pathology jobs on the real 2-worker cluster where the SparkListener sees genuine stage metrics.
