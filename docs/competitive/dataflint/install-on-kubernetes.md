# Install on Kubernetes (Spark Operator + Egress-Blocked Pods)

> **Purpose**: Get DataFlint onto Spark/SHS pods on K8s — the official Spark Operator manifest, jar baking vs `spark.jars`, the manual-jar path for egress-blocked pods, and image/Helm placement
> **MCP Validated**: Full-source validation 2026-06-22 (GitHub README + GitBook docs + dataflint.io)

## When to Use

- You run Spark on Kubernetes via the **Spark Operator** (`SparkApplication` CRD) — the
  highest-value path for this repo (Spark 3.5.6 on K8s).
- Spark driver/executor pods or the SHS pod have **no internet egress**.

## Official Spark Operator Manifest

```yaml
# kind: SparkApplication
spec:
  deps:
    packages:
      - io.dataflint:spark_2.12:0.9.9
  sparkConf:
    spark.plugins: "io.dataflint.spark.SparkDataflintPlugin"
    spark.driver.extraJavaOptions: "-Divy.cache.dir=/tmp -Divy.home=/tmp"   # ivy cache must be writable in the pod
```

> The `-Divy.cache.dir=/tmp -Divy.home=/tmp` is essential: when `deps.packages` resolves
> from Maven, Ivy needs a **writable** cache dir inside the pod.

## The Egress Trap

> `spark.jars.packages` / `deps.packages` resolves the artifact from **Maven at runtime**.
> On egress-blocked pods this fails — the job hangs on dependency resolution or dies with a
> resolution error, and the DataFlint plugin never loads.

| Approach | How | Best for |
|----------|-----|----------|
| **Bake into the image** | `COPY` the jar into `$SPARK_HOME/jars/` | Permanent, fleet-wide install |
| **Stage on MinIO + `spark.jars`** | Upload jar to MinIO; reference via `spark.jars` | Per-job, no image rebuild |
| **Manual jar (Option 4)** | `wget` from Maven Central + `--driver-class-path` | One-off / pinned, no Operator resolution |

## Option A: Bake the Jar into the Image

```dockerfile
COPY spark_2.12-0.9.9.jar /opt/spark/jars/
```

Then jobs/SHS only need the plugin registration — no package pull:

```properties
spark.plugins                       io.dataflint.spark.SparkDataflintPlugin
spark.dataflint.telemetry.enabled   false
```

## Option B: Stage on MinIO and Use `spark.jars`

```python
spark = (
    SparkSession.builder
    .config("spark.jars", "s3a://artifacts/spark_2.12-0.9.9.jar")
    .config("spark.plugins", "io.dataflint.spark.SparkDataflintPlugin")
    .config("spark.dataflint.telemetry.enabled", "false")
    .getOrCreate()
)
```

## Option 4: Manual Jar (egress-blocked, official form)

```bash
DATAFLINT_VERSION="0.9.9"
wget -O /tmp/spark_2.12-$DATAFLINT_VERSION.jar \
  https://repo1.maven.org/maven2/io/dataflint/spark_2.12/$DATAFLINT_VERSION/spark_2.12-$DATAFLINT_VERSION.jar
spark-submit \
  --driver-class-path /tmp/spark_2.12-$DATAFLINT_VERSION.jar \
  --conf spark.jars=files:///tmp/spark_2.12-$DATAFLINT_VERSION.jar \
  --conf spark.plugins=io.dataflint.spark.SparkDataflintPlugin
```

> Pre-stage the jar in the image or on MinIO if the pod cannot even reach
> `repo1.maven.org`. `spark.jars` distributes an already-resolved jar; `spark.jars.packages`
> / `deps.packages` resolves coordinates from Maven and **needs egress**.

## Helm / Deployment Placement

| Target | Where to set |
|--------|--------------|
| Driver/executor plugin config | `SparkApplication.sparkConf` / `spark-defaults.conf` in the image |
| SHS classpath | SHS Deployment: jar in image `jars/` **or** `SPARK_DAEMON_CLASSPATH` via env |
| Staged jar location | A MinIO bucket reachable by the pods (`s3a://...`) |

Coordinate the cluster-manager/image side with the `spark-manager-specialist`, and the
SHS storage side with the `spark-history-specialist`.

## Verify

```bash
kubectl -n spark exec deploy/<spark-or-shs> -- ls /opt/spark/jars/ | grep -i dataflint
# Then confirm the DataFlint view renders in the UI.
```

## Pitfalls

| Don't | Do |
|-------|----|
| Rely on `deps.packages` on egress-blocked pods | Bake the jar, stage on MinIO, or use Option 4 |
| Omit the ivy cache dirs in the Operator manifest | Set `-Divy.cache.dir=/tmp -Divy.home=/tmp` |
| Bake the wrong Scala jar | Match the image's Spark Scala version |
| Rebuild only the job image, forget the SHS image | Update both for live + offline DataFlint |

## See Also

- [install-pyspark-session.md](install-pyspark-session.md)
- [install-history-server.md](install-history-server.md)
- [../concepts/package-version-matrix.md](../concepts/package-version-matrix.md)
