# jar/ — ② capture

**Role:** Scala Spark plugin JAR. `SparkListener` stage metrics + normalized **logical** plan fingerprint → OTLP, bounded/non-blocking.
**Language:** Scala (sbt) · **Branch prefix:** `jar/*` (e.g. `jar/T4-stage-metrics`)
**Full brief:** [../docs/lanes/JAR.md](../docs/lanes/JAR.md) · **Obeys:** [../CONTRACT.md](../CONTRACT.md)
**Exit criterion:** `spark-submit --conf spark.plugins=apex.ApexPlugin` → one OTLP event per stage in `apex.spark_events`, zero driver latency, no crash if the collector is down.

Layout: `build.sbt` (sbt-projectmatrix: Spark 3.5×2.12/2.13, 4.0×2.13) · `project/` · `src/main/scala/apex/` (ApexPlugin · ApexStageListener · ApexPlanListener · ApexOtelSink).
Watch: fingerprint the **logical** plan (`optimizedPlan.canonicalized`), never physical. Use `onExecutorMetricsUpdate` for live peak memory.
