package apex

import org.apache.spark.SparkConf

/**
 * The egress seam. Both listeners talk to an `ApexSink`, never to a concrete
 * exporter — so the stage listener, the plan listener (registered independently
 * via `spark.sql.queryExecutionListeners`), and the AQE listener can share ONE
 * sink instance, and tests can swap in a capturing double.
 */
trait ApexSink {
  /** Emit one completed stage as an `apex.stage` span. Must be non-blocking. */
  def emit(ev: ApexStageEvent): Unit

  /** Emit one AQE re-plan as an `apex.plan_transition` span (v0.2). Non-blocking. */
  def emitPlanTransition(t: PlanTransition): Unit

  /** Emit the resolved conf allowlist as one `apex.job_conf` span (v0.4 proposal). Non-blocking. */
  def emitJobConf(ev: JobConfEvent): Unit

  /** Flush + release. Idempotent; bounded so shutdown can't hang. */
  def close(): Unit
}

/**
 * Process-wide sink singleton. A Spark driver is one JVM running one application,
 * so one sink is correct — and it's what lets the plan listener (constructed by
 * Spark from `spark.sql.queryExecutionListeners`, a different instance than the
 * plugin-registered stage listener) share plan context with the stage listener.
 *
 * `spark.apex.sink.class` (test-only) swaps in a no-arg `ApexSink` implementation
 * via reflection; otherwise the real OTLP sink is built from `spark.apex.*` conf.
 */
object ApexSinks {
  @volatile private var singleton: ApexSink = _

  def instance(conf: SparkConf): ApexSink = synchronized {
    if (singleton == null) singleton = build(conf)
    singleton
  }

  /** Close and clear (driver shutdown, or between tests). */
  def reset(): Unit = synchronized {
    if (singleton != null) {
      try singleton.close() catch { case _: Throwable => () }
      singleton = null
    }
  }

  private def build(conf: SparkConf): ApexSink =
    conf.getOption("spark.apex.sink.class").filter(_.nonEmpty) match {
      case Some(className) =>
        Class.forName(className).getDeclaredConstructor().newInstance().asInstanceOf[ApexSink]
      case None =>
        new ApexOtelSink(
          conf.get("spark.apex.otlp.endpoint", "http://localhost:4318"),
          conf.get("spark.apex.service.name", "apex-spark"))
    }
}
