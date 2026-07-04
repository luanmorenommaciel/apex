# Package & Version Matrix

> **Purpose**: Selecting the correct `io.dataflint` Maven artifact for a given Spark + Scala build, plus the realtime-vs-History-Server platform compatibility matrix
> **Confidence**: 0.95
> **MCP Validated**: Full-source validation 2026-06-22 (GitHub README + GitBook docs + dataflint.io)

## Overview

DataFlint ships **per-Scala** artifacts. The single most common install failure is picking
the wrong Scala variant for your Spark build — the plugin then fails to load. Match the
artifact to your Spark build's Scala version, which `spark-submit --version` prints.

## The Artifact Matrix

| Target | Scala | Maven artifact (latest 0.9.9) |
|--------|-------|-------------------------------|
| Spark 3.x | 2.12 | `io.dataflint:spark_2.12:0.9.9` (this repo) |
| Spark 3.x | 2.13 | `io.dataflint:spark_2.13:0.9.9` |
| Spark 4.x | 2.13 | `io.dataflint:dataflint-spark4_2.13:0.9.9` |
| Databricks Runtime 17.3+ | 2.13 | `io.dataflint:dataflint-spark4-databricks_2.13:0.9.9` |

> **Spark 4 artifactId**: the canonical Maven coordinate uses a **HYPHEN**
> (`dataflint-spark4_2.13`). The GitBook page shows an underscore variant
> (`dataflint_spark4_2.13`) which appears to be a docs typo — Maven Central uses the hyphen.

> **Databricks 17.3+**: DBR 17.3+ ships `javax.servlet` instead of `jakarta.servlet`, so it
> needs the dedicated `dataflint-spark4-databricks_2.13` coordinate. **Same plugin class**
> (`io.dataflint.spark.SparkDataflintPlugin`) — only the coordinate differs.

> **This repo**: Spark **3.5.6**, default build → **Scala 2.12** → use
> `io.dataflint:spark_2.12:0.9.9`.

## Supported Spark / Scala / Modes

- **Spark**: 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 4.0 (README states "3.2 and up"; the
  supported-versions page lists 3.0–4.0).
- **Scala**: 2.12 or 2.13.
- **Modes**: batch + streaming.

## Current Version

- Latest release: **0.9.9** (tag `v0.9.9`, May 18 2026).
- **Always confirm the latest version on Maven Central before pinning** — pin an exact
  version in production; never use a floating range (`...:spark_2.12:+`).

```bash
# Confirm the Scala version of YOUR Spark build BEFORE choosing the artifact:
spark-submit --version
# banner prints e.g. "Using Scala version 2.12.18" -> pick spark_2.12
```

## Platform Compatibility — Realtime vs History Server

| Platform | Realtime (live UI) | History Server (SHS) |
|----------|:---:|:---:|
| Local | ✅ | ✅ |
| Standalone | ✅ | ✅ |
| Kubernetes (Spark Operator) | ✅ | ✅ |
| EMR | ✅ | ✅ |
| Dataproc | ✅ | ✅ |
| HDInsight | ✅ | ❌ |
| Databricks | ✅ | ❌ |

> **KEY LIMITATION**: DataFlint does **NOT** support **persistent** history servers
> (Databricks, EMR-persistent) because they cannot load custom providers.

## The Mismatch Failure Mode

| Wrong choice | Symptom | Fix |
|--------------|---------|-----|
| `spark_2.13` jar on a Scala 2.12 build | `ClassNotFound` / plugin silently never loads; no DataFlint view | Switch to `spark_2.12` |
| `spark_2.12` jar on a Scala 2.13 build | Same — `NoClassDefFound` / no view | Switch to `spark_2.13` |
| `spark_2.12`/`_2.13` on Spark 4.x | Incompatible API surface | Use `dataflint-spark4_2.13` |
| Spark 4 artifact on Databricks 17.3+ | servlet (jakarta vs javax) mismatch | Use `dataflint-spark4-databricks_2.13` |
| Floating version `...:+` | Non-reproducible / surprise upgrade | Pin an exact version |

## How the Artifact Is Supplied

Pulled at runtime via `spark.jars.packages` (Maven resolution) **or** supplied as a
pre-staged jar via `spark.jars`. On egress-blocked Kubernetes pods, Maven resolution fails
— bake the jar into the image or stage it on MinIO. See
[../patterns/install-on-kubernetes.md](../patterns/install-on-kubernetes.md).

## Related

- [what-is-dataflint.md](what-is-dataflint.md)
- [plugin-architecture.md](plugin-architecture.md)
- [../patterns/install-pyspark-session.md](../patterns/install-pyspark-session.md)
- [../patterns/install-on-kubernetes.md](../patterns/install-on-kubernetes.md)
- [../specs/dataflint-config-schema.yaml](../specs/dataflint-config-schema.yaml)
