# DataFlint Quick Reference

> Fast lookup tables. For detail, see linked files. Stack: Spark 3.5.6 / Scala 2.12 / MinIO / K8s.
> **MCP Validated**: Full-source validation 2026-06-22 (GitHub README + GitBook docs + dataflint.io)

## Live Install (PySpark)

```python
spark = (SparkSession.builder
    .config("spark.jars.packages", "io.dataflint:spark_2.12:0.9.9")
    .config("spark.plugins", "io.dataflint.spark.SparkDataflintPlugin")
    .config("spark.dataflint.telemetry.enabled", "false")
    .getOrCreate())   # tab at http://<driver>:4040 -> "DataFlint"
```

## K8s Spark Operator (official)

```yaml
# kind: SparkApplication
spec:
  deps:
    packages: [ io.dataflint:spark_2.12:0.9.9 ]
  sparkConf:
    spark.plugins: "io.dataflint.spark.SparkDataflintPlugin"
    spark.driver.extraJavaOptions: "-Divy.cache.dir=/tmp -Divy.home=/tmp"
```

## History Server Install (offline / post-mortem)

```bash
cp spark_2.12-0.9.9.jar "$SPARK_HOME/jars/"   # or SPARK_DAEMON_CLASSPATH=/path/jar (no Ivy on SHS)
"$SPARK_HOME/sbin/stop-history-server.sh" && "$SPARK_HOME/sbin/start-history-server.sh"
# Prereq: spark.eventLog.dir == spark.history.fs.logDirectory. NOT supported on persistent SHS.
```

## Config Flags

| Config | Default | Notes |
|--------|---------|-------|
| `spark.plugins` | unset | Set to `io.dataflint.spark.SparkDataflintPlugin` to activate |
| `spark.dataflint.telemetry.enabled` | `true` | Anonymous MixPanel (Spark ver + App id only). Set **false** here |
| `spark.dataflint.iceberg.autoCatalogDiscovery` | `false` | Enables Iceberg **write** metrics (confirmed) |
| `spark.sql.maxMetadataStringLength` | (native) | Set **1000** for full "Long Filter Conditions" predicates |
| `spark.dataflint.instrument.spark.enabled` | `false` | Global toggle: UDF + window + SQL-node duration metrics (experimental) |
| `spark.dataflint.instrument.deltalake.enabled` | `false` | Delta metadata (partition/Z-Order/clustering); v0.7.0+, experimental |

## Version / Artifact Matrix (latest 0.9.9)

| Target | Scala | Artifact |
|--------|-------|----------|
| Spark 3.x | 2.12 | `io.dataflint:spark_2.12:0.9.9` (this repo) |
| Spark 3.x | 2.13 | `io.dataflint:spark_2.13:0.9.9` |
| Spark 4.x | 2.13 | `io.dataflint:dataflint-spark4_2.13:0.9.9` (HYPHEN) |
| Databricks 17.3+ | 2.13 | `io.dataflint:dataflint-spark4-databricks_2.13:0.9.9` |

Supported Spark 3.0–4.0 (README: "3.2 and up"), Scala 2.12/2.13, batch + streaming.
Confirm latest on Maven Central; `spark-submit --version` prints your Scala.

## Platform Matrix (realtime / SHS)

| Local | Standalone | K8s Operator | EMR | Dataproc | HDInsight | Databricks |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| ✅/✅ | ✅/✅ | ✅/✅ | ✅/✅ | ✅/✅ | ✅/❌ | ✅/❌ |

No support for **persistent** history servers (Databricks, EMR-persistent).

## Official Features (6)

Real-time query & cluster status · Query breakdown (heat map) · Application Run Summary · Performance alerts & suggestions · Identify query failures · Spark AI Assistant.

## Alert → Specialist (official names)

| DataFlint alert | Route to |
|-----------------|----------|
| Reading / Writing Small Files; Large Partition Size; Long Filter Conditions | `spark-specialist` |
| Apache Iceberg – inefficient replace of data | `spark-specialist` |
| Large Number Of Small Tasks; Large Data Broadcast; Broadcast small table in SMJ; Large Cross Join Scan | `spark-shuffle-specialist` |
| Partition Skew | `spark-skew-specialist` |
| Memory Over/Under-Provisioning; High wasted cores rate | `spark-manager-specialist` |
| Query Failures | `spark-troubleshooter` |

## Top Pitfalls

| Don't | Do |
|-------|----|
| `spark_2.13` jar on a Scala 2.12 build | Match `spark-submit --version` banner |
| Floating version `...:spark_2.12:+` | Pin an exact version in prod |
| `deps.packages` on egress-blocked K8s pods | Bake jar, stage on MinIO, or manual-jar |
| Apply every alert as a config change | Confirm metric, then route (DataFlint = candidates) |
| Telemetry on for sensitive data | `spark.dataflint.telemetry.enabled=false` |
| Enable SaaS/external egress unprompted | Separate opt-in; CRITICAL — ask first |
| `spark.jars.packages` on the SHS | No Ivy on SHS — download the jar manually |

## Related Documentation

| Topic | Path |
|-------|------|
| Full config schema | `specs/dataflint-config-schema.yaml` |
| Alert triage + routing | `patterns/alert-triage-routing.md` |
| Full Index | `index.md` |
