# jar/ — ② capture

**Role:** a self-contained Scala **Spark plugin JAR** that captures per-stage
`TaskMetrics` + a normalized **logical**-plan fingerprint, and — the differentiator —
**AQE runtime decisions** (skew splits, join switches, coalesces), shipping each as an
**OTLP span** over a **bounded, non-blocking** queue.

**Obeys:** [`../CONTRACT.md`](../CONTRACT.md) (v0.2) · **Full brief:** [`../docs/lanes/JAR.md`](../docs/lanes/JAR.md)
**Language:** Scala (sbt) · **Emits:** OTLP/HTTP spans to a collector on `:4318`

It beats sparkMeasure/DataFlint on one axis they don't cover: those aggregate `TaskEnd`
*symptoms* (shuffle bytes, spill, p50/p99); Apex also records Spark's **own** optimization
*decisions* as ground truth — see [`apex.plan_transition`](#the-differentiator-apexplan_transition) below.

---

## Activate

Add the JAR (pick the cell matching your cluster's Spark×Scala) and turn the plugin on.

```python
SparkSession.builder \
  .config("spark.jars.packages", "io.dataship:apex_3.5_2.12:0.1.0") \
  .config("spark.plugins",       "apex.ApexPlugin") \
  .config("spark.apex.otlp.endpoint", "http://collect:4318")
```

```bash
spark-submit \
  --packages io.dataship:apex_3.5_2.12:0.1.0 \
  --conf spark.plugins=apex.ApexPlugin \
  --conf spark.apex.otlp.endpoint=http://collect:4318 \
  your_app.py
```

### Two activation paths

| Path | Config | Captures | Clean shutdown flush |
|---|---|---|---|
| **Primary** (recommended) | `--conf spark.plugins=apex.ApexPlugin` | stage events **+ AQE plan transitions** | ✅ `DriverPlugin.shutdown` → `forceFlush` |
| **Fallback** (lighter) | `--conf spark.extraListeners=apex.ApexStageListener` | stage events only (**no** AQE transitions) | ❌ no shutdown hook — last batch may drop |

Both paths emit the **identical** `apex.stage` events (verified byte-for-byte on Spark
3.5 and 4.0). The plugin path additionally registers the AQE listener — so if you want the
`apex.plan_transition` signal, use `spark.plugins`. The plan-fingerprint attachment works on
**both** paths (it lives in the stage listener).

> The `extraListeners` fallback exists because it has no clean lifecycle hook: no
> `shutdown()` to flush the exporter, and AQE capture isn't wired. Prefer `spark.plugins`.

---

## Configuration — every `spark.apex.*` key

| Key | Default | Meaning |
|---|---|---|
| `spark.apex.otlp.endpoint` | `http://localhost:4318` | Collector base URL. Apex appends `/v1/traces` itself — pass the **base**, not the full path. |
| `spark.apex.service.name` | `apex-spark` | OTel resource `service.name` on every span. |
| `spark.apex.aqe.enabled` | `true` | Register the AQE listener (`apex.plan_transition`). Only effective on the `spark.plugins` path. Set `false` to disable AQE capture. |
| `spark.apex.conf.enabled` | `true` | Register the job-conf listener (`apex.job_conf`, v0.4 proposal): the resolved, allowlisted SparkConf subset, once per application. Set `false` to disable. |
| `spark.apex.job_id` | `applicationId` | The contract trace key threaded through every event. Override to correlate a logical job across app runs (e.g. a nightly pipeline); otherwise the Spark `applicationId` is used. |

Standard AQE is unaffected — leave `spark.sql.adaptive.enabled=true` (the default in 3.5/4.0)
to get plan transitions.

---

## What it emits

### `apex.stage` — one span per completed stage

Attributes are the [contract §"telemetry event"](../CONTRACT.md) fields verbatim (snake_case),
landing in `apex.spark_events`:

`job_id`, `app_id`, `app_name`, `stage_id`, `stage_attempt`, `ts`,
`shuffle_read_bytes`, `shuffle_write_bytes`, `spill_disk_bytes`, `spill_mem_bytes`,
`gc_time_ms`, `input_bytes`, `output_bytes`, `peak_execution_mem_bytes`,
`task_count`, `task_duration_p50_ms`, `task_duration_p99_ms`,
`plan_fingerprint`, `plan_json`.

- **`plan_fingerprint`** — SHA-256 (64 hex → `FixedString(64)`) of the **normalized LOGICAL**
  plan (`optimizedPlan.canonicalized` **plus a literal-normalization pass**, so the same query
  with different date/constant literals hashes identically — and it survives AQE, which rewrites
  the *physical* plan at runtime). Attached to every stage of a query by buffering per
  `execution_id` and flushing at SQL execution end.
- **`plan_json`** — redacted plan text (literals removed, emails/paths stripped). The raw plan
  is **never** shipped.

### The differentiator: `apex.plan_transition`

One span per **real** AQE re-plan (no-op re-plans are dropped), landing in
`apex.plan_transitions` ([contract v0.2](../CONTRACT.md)):

| Attribute | Meaning |
|---|---|
| `job_id`, `execution_id`, `update_seq` | key — `update_seq` is monotonic per execution |
| `transition_type` | `join_switch` \| `skew_split` \| `coalesce` \| `local_read` \| `other` |
| `detail`, `before`, `after` | structured descriptors (node names + AQE descriptors only — **no literals**) |
| `confidence` | `HIGH` (structural: node-type delta / `AQEShuffleRead` descriptor) \| `BEST_EFFORT` |
| `ts` | epoch millis |

This is Spark's own decision as ground truth: *"AQE split this skewed join"* / *"AQE demoted
SortMergeJoin→BroadcastHashJoin"* / *"AQE coalesced partitions"* — a finding at **$0, no LLM
inference**, and the causal *why* behind the stage metrics.

### `apex.job_conf` (v0.4 proposal — pending ratification)

**One span per application**, emitted at the first `onJobStart` (a SparkSession
exists by then, so `spark.sql.*` **defaults resolve** — an unset
`adaptive.enabled` is captured as its effective `"true"`), landing in
`apex.job_conf` ([proposal](../contract/CONTRACT-EXTENSION-v0.4-job_conf.md)):

| Attribute | Meaning |
|---|---|
| `job_id`, `app_id`, `app_name`, `ts` | identity (same keys as `apex.stage`) |
| one attribute per allowlisted key | e.g. `spark.sql.adaptive.skewJoin.enabled` = `"true"` — the **resolved** value |

**SECURITY: hard-coded ALLOWLIST, never the whole conf.** Only 13 pure
performance knobs (ZEST's 6 tunables, the AQE flags, `autoBroadcastJoinThreshold`)
— a SparkConf carries s3a secret keys, JDBC passwords, tokens, and those must
never reach telemetry. See `ApexJobConfAllowlist`; the invariant is enforced by
`JobConfSpec` ("secrets never leave the JVM"). Unset executor/driver keys are
omitted; `spark.sql.*` keys are always present with their effective value.

---

## Design guarantees

- **Zero added driver latency / no crash if the collector is down.** Spans go through a
  **bounded** `BatchSpanProcessor` (queue 2048, batch 512, 1s schedule, 5s export timeout) that
  exports on its own thread and **drops** when full — it never blocks the driver. Verified: a
  100-stage job with a dead collector completes in ~2 s (a blocking sink would take >60 s).
- **A listener never takes down the bus.** Every metric read and OTLP call is wrapped in
  `Try`/recover (a `SparkListener` that throws is evicted from Spark's bus).
- **Bounded memory.** The per-`execution_id` fingerprint buffer is size-capped (4096 stages /
  128 live executions); past the cap it flushes without a fingerprint rather than grow.

---

## Build & publish locally

Cross-built with `sbt-projectmatrix` — four cells (Spark 4.x requires Scala 2.13):

| Artifact | Spark | Scala | JDK to build |
|---|---|---|---|
| `io.dataship:apex_3.5_2.12:0.1.0` | 3.5.x | 2.12 | 8 / 11 / 17 |
| `io.dataship:apex_3.5_2.13:0.1.0` | 3.5.x | 2.13 | 8 / 11 / 17 |
| `io.dataship:apex_4.0_2.13:0.1.0` | 4.0.x | 2.13 | **17** / 21 |
| `io.dataship:apex_4.1_2.13:0.1.0` | 4.1.2 | 2.13.17 | **17** / 21 |

```bash
# One JDK 17 builds all four cells (3.5 supports 8/11/17; Spark 4.x needs 17/21).
export JAVA_HOME=<path-to-jdk-17>

sbt "+compile"       # build all four cells
sbt "+test"          # run the test suite on every cell (spins up a local Spark)
sbt "+publishLocal"  # publish all four to ~/.ivy2/local for local consumers (dev/, e2e)
```

Spark and Jackson are `provided` (the cluster supplies them); the OTel SDK is bundled. A user
consuming from `~/.ivy2/local` references the coordinate exactly as with `spark.jars.packages`
above.

> Publishing to Maven Central is a **post-integration release step**, intentionally not done
> here. `publishLocal` is what `dev/` and the eventual end-to-end test consume.

---

## Layout

```
jar/
├── build.sbt                         # projectmatrix: 4 cells, Spark/Jackson provided, OTel bundled
├── project/                          # sbt + projectmatrix plugin + SparkAxis
└── src/
    ├── main/scala/apex/
    │   ├── ApexPlugin.scala          # spark.plugins entry → registers listeners
    │   ├── ApexStageListener.scala   # stage metrics + execution_id-buffered fingerprint
    │   ├── ApexAqeListener.scala     # AQE plan transitions (onOtherEvent, structural diff)
    │   ├── ApexOtelSink.scala        # bounded BatchSpanProcessor → OTLP /v1/traces
    │   ├── ApexSink.scala            # sink seam + JVM-singleton factory
    │   ├── ApexPlanFingerprint.scala # normalized-logical-plan SHA-256
    │   ├── ApexStageEvent.scala      # contract fields + OTel attribute keys
    │   ├── ApexPlanTransition.scala  # v0.2 plan_transition record
    │   ├── ApexJobConf.scala         # v0.4 proposal: job_conf record + security allowlist
    │   └── ApexConfListener.scala    # v0.4 proposal: resolved conf allowlist, once per app
    └── test/scala/apex/              # fingerprint, dual-activation, AQE-transition, job-conf specs
```
