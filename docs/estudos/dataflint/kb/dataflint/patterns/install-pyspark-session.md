# Install on a Live Session

> **Purpose**: Activate the DataFlint tab on a running job's driver Spark UI — PySpark builder and spark-submit, with telemetry off for internal/regulated data
> **MCP Validated**: Full-source validation 2026-06-22 (GitHub README + GitBook docs + dataflint.io)

## When to Use

- A developer wants the DataFlint tab on the live driver Spark UI for an active job
- Diagnosing a job *while it runs* (dev/test), not a finished run (for finished runs use
  [install-history-server.md](install-history-server.md))

## Prerequisites

- Spark **3.2+** (this repo: 3.5.6) — see
  [../concepts/what-is-dataflint.md](../concepts/what-is-dataflint.md)
- The correct Scala artifact confirmed via `spark-submit --version` — see
  [../concepts/package-version-matrix.md](../concepts/package-version-matrix.md)
- On Kubernetes with no egress, do **not** rely on `spark.jars.packages` — see
  [install-on-kubernetes.md](install-on-kubernetes.md)

## PySpark Builder (this repo's primary path)

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    # 1) Pull the plugin jar at submit time (match Scala + pin the version)
    .config("spark.jars.packages", "io.dataflint:spark_2.12:0.9.9")
    # 2) Register the plugin — this is what activates DataFlint
    .config("spark.plugins", "io.dataflint.spark.SparkDataflintPlugin")
    # 3) Opt out of usage telemetry (recommended for internal/regulated data)
    .config("spark.dataflint.telemetry.enabled", "false")
    .getOrCreate()
)
# DataFlint tab appears in the driver UI: http://<driver>:4040 -> "DataFlint"
```

> If `spark.plugins` is already set for another plugin, comma-append:
> `...,io.dataflint.spark.SparkDataflintPlugin` — do not overwrite it.

## spark-submit

```bash
spark-submit \
  --packages io.dataflint:spark_2.12:0.9.9 \
  --conf spark.plugins=io.dataflint.spark.SparkDataflintPlugin \
  --conf spark.dataflint.telemetry.enabled=false \
  your_job.py
```

## Confirmed Extra Configs

```properties
# Enable Iceberg WRITE metrics (confirmed)
spark.dataflint.iceberg.autoCatalogDiscovery   true

# Native Spark: log full filter predicates untruncated (helps the
# "Long Filter Conditions" alert) — recommend 1000
spark.sql.maxMetadataStringLength              1000
```

## Optional Instrumentation (EXPERIMENTAL — opt-in, off by default)

> Instrumentation is **OPTIONAL, opt-in, DISABLED by default, and EXPERIMENTAL**: DataFlint
> wraps physical-plan nodes (`TimedExec`) to add `duration` + `rddId` metrics Spark doesn't
> report — *use with caution*. All keys default to `false`.

```python
    # Global toggle — turns on UDF + window + SQL-node instrumentation:
    .config("spark.dataflint.instrument.spark.enabled", "true")
    # …or granular, e.g. just PySpark vectorized UDFs:
    .config("spark.dataflint.instrument.spark.mapInPandas.enabled", "true")
    .config("spark.dataflint.instrument.spark.sqlNodes.enabled", "true")
    # Delta Lake metadata (v0.7.0+, flaky on Databricks):
    .config("spark.dataflint.instrument.deltalake.enabled", "true")
```

Guides: PySpark-UDF / Window / SQL-nodes under `integrations/spark-instrumentation`.
Full verified flag reference (12 keys): [../specs/dataflint-config-schema.yaml](../specs/dataflint-config-schema.yaml).

## Verify

1. Open the driver UI (`:4040` locally, or the mapped port on K8s).
2. Confirm a **DataFlint** tab is present alongside Jobs/Stages/SQL.
3. Run a stage; confirm alerts render. No tab usually means a Scala/Spark mismatch — see
   [../concepts/package-version-matrix.md](../concepts/package-version-matrix.md).

## Pitfalls

| Don't | Do |
|-------|----|
| Use `spark_2.13` on a Scala 2.12 build (or vice-versa) | Match the `spark-submit --version` banner |
| Use a floating version `...:spark_2.12:+` | Pin an exact version in production |
| Leave telemetry on for sensitive data | Set `spark.dataflint.telemetry.enabled=false` |
| Rely on `spark.jars.packages` on egress-blocked pods | Bake/stage the jar — [install-on-kubernetes.md](install-on-kubernetes.md) |
| Treat a fired alert as a fix to apply | Confirm + route — [alert-triage-routing.md](alert-triage-routing.md) |

## See Also

- [install-history-server.md](install-history-server.md)
- [install-on-kubernetes.md](install-on-kubernetes.md)
- [../concepts/plugin-architecture.md](../concepts/plugin-architecture.md)
- [../specs/dataflint-config-schema.yaml](../specs/dataflint-config-schema.yaml)
