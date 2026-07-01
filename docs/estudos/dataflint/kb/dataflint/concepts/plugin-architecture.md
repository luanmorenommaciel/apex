# Plugin Architecture

> **Purpose**: How DataFlint hooks into Spark via the `spark.plugins` / `SparkPlugin` API — in-process, reads the same metrics the Spark UI uses, zero query-plan impact, fails safe, and how it removes cleanly
> **Confidence**: 0.95
> **MCP Validated**: Full-source validation 2026-06-22 (GitHub README + GitBook docs + dataflint.io)

## Overview

DataFlint activates through Spark's standard **plugin** mechanism. You register it with a
single config — `spark.plugins=io.dataflint.spark.SparkDataflintPlugin` — and Spark
instantiates it **in-process** on the driver (and, where relevant, executors) during
`SparkContext` startup. There is no separate daemon, port, or sidecar. The whole product
is "two configs": the package jar plus the `spark.plugins` registration.

## The Hook

```
SparkContext start
  └─ read spark.plugins
        └─ instantiate io.dataflint.spark.SparkDataflintPlugin   (in-process)
              └─ attach to the SAME event/metric stream the Spark UI consumes
              └─ serve the "DataFlint" view via the EXISTING Spark UI endpoint
              └─ evaluate metrics → raise NAMED alerts (read-only)
```

`SparkPlugin` is Spark's official extension point (since Spark 3.0) for driver/executor
plugins. DataFlint uses it purely as a **listener/reader** of metrics — it consumes the
event stream and renders an alerting view.

## Reads the Same Metrics — Zero Plan Impact

> DataFlint consumes the **same** stage/task/SQL metrics the Spark UI already exposes. It
> does **not** rewrite the logical/physical plan, does not insert exchanges, and does not
> change scheduling. It cannot make a job faster or slower by being present.

- An alert is a *reading* of metrics that already existed — DataFlint just names the
  pattern. Confirm the underlying metric before acting (see
  [../patterns/alert-triage-routing.md](../patterns/alert-triage-routing.md)).
- Because it only reads, it is safe to add for a diagnosis pass and remove afterward with
  no behavioural change.

## Security Posture

- **Runs locally** on the driver or the history server; it serves the DataFlint view
  through the **existing Spark UI endpoint** — it exposes **NO new endpoints or ports**.
- **Open source**; the Maven stable jar cannot be mutated.
- **No executor compute** — see Performance below.

## Stability — Fails Safe

> If DataFlint fails on startup it throws a **warning and lets the app CONTINUE** — it
> never blocks the job. Driver-side errors run in a **separate thread** and shouldn't
> affect runtime.

## Performance Profile

- Compute is mostly in the **DataFlint Web UI**, not in Spark.
- On the driver it runs **only when the DataFlint tab is open & active**, polling the
  driver API roughly **every ~1 second** — perf impact ≈ watching the normal Spark UI and
  refreshing it.
- **No executor compute.**

## Telemetry

- Anonymous, via **MixPanel**.
- Collects **only the Spark version + App id** — **no job data**.
- Opt out with `spark.dataflint.telemetry.enabled=false` (the default on this platform).

## Live vs History Server — Same Plugin, Two Feeds

| Feed | How the plugin gets metrics |
|------|-----------------------------|
| **Live** | Attached to the running driver's live listener bus; view at `:4040` |
| **History Server** | Loaded on the SHS classpath; renders from **replayed** event logs |

For the SHS feed to have data, the event-log prerequisites must hold — DataFlint shows
nothing if the SHS itself is empty (an `eventLog.dir` vs `history.fs.logDirectory`
mismatch or MinIO `s3a` creds/endpoint). See
[../patterns/install-history-server.md](../patterns/install-history-server.md) and the
spark-history KB.

## Clean Removal Contract

Because the plugin only reads metrics in-process, you remove it by deleting its two
configs — no migration, no cleanup of state:

```properties
# Remove these two lines and DataFlint is gone; the job behaves identically.
spark.jars.packages   io.dataflint:spark_2.12:0.9.9          # (or spark.jars)
spark.plugins         io.dataflint.spark.SparkDataflintPlugin
```

> If `spark.plugins` already lists other plugins, removing DataFlint means removing only
> the `io.dataflint...` entry, not the whole config.

## Related

- [what-is-dataflint.md](what-is-dataflint.md)
- [alerts-catalog.md](alerts-catalog.md)
- [package-version-matrix.md](package-version-matrix.md)
- [../patterns/install-pyspark-session.md](../patterns/install-pyspark-session.md)
- [../specs/dataflint-config-schema.yaml](../specs/dataflint-config-schema.yaml)
