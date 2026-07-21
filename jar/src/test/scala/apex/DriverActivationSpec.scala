package apex

import org.apache.spark.sql.SparkSession
import org.scalatest.funsuite.AnyFunSuite

/**
 * T9 + T10 driver-run proofs, using a REAL local Spark driver:
 *   - T10: `spark.plugins` and `spark.extraListeners` produce identical per-stage
 *     events, one per stage, with non-zero shuffle_read_bytes.
 *   - T9:  with the collector DOWN, a ~100-stage job completes and wall-clock is
 *     not inflated (bounded queue drops, never blocks the driver).
 */
class DriverActivationSpec extends AnyFunSuite {

  private def resetSessions(): Unit = {
    ApexSinks.reset()
    CapturingSink.latest = null
    SparkSession.clearActiveSession()
    SparkSession.clearDefaultSession()
  }

  /** Run a shuffle job under the given activation, capturing the emitted events. */
  private def runCapturing(activate: SparkSession.Builder => SparkSession.Builder): Seq[ApexStageEvent] = {
    resetSessions()
    val spark = activate(
      SparkSession.builder()
        .master("local[2]")
        .appName("apex-activation")
        .config("spark.apex.sink.class", "apex.CapturingSink")            // capture instead of OTLP
        .config("spark.sql.adaptive.enabled", "false")                    // deterministic stage graph for parity
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "4")
    ).getOrCreate()

    try {
      spark.range(0, 20000).selectExpr("id", "id % 100 as k")
        .groupBy("k").count().collect()
    } finally {
      spark.stop() // drains the listener bus → all stage-completed events delivered
    }
    val events = Option(CapturingSink.latest).map(_.events.toList).getOrElse(Nil)
    resetSessions()
    events
  }

  test("T10: spark.plugins and spark.extraListeners emit identical per-stage events (shuffle > 0)") {
    val viaPlugin = runCapturing(_.config("spark.plugins", "apex.ApexPlugin"))
    val viaExtra  = runCapturing(_.config("spark.extraListeners", "apex.ApexStageListener"))

    // groupBy+count with AQE off = exactly 2 stages → one event each.
    assert(viaPlugin.size == 2, s"plugin path: expected 2 stage events, got ${viaPlugin.size}")
    assert(viaExtra.size == 2,  s"extraListeners path: expected 2 stage events, got ${viaExtra.size}")
    assert(viaPlugin.exists(_.shuffle_read_bytes > 0),  "plugin path: expected a stage with shuffle_read_bytes > 0")
    assert(viaExtra.exists(_.shuffle_read_bytes > 0),   "extraListeners path: expected shuffle_read_bytes > 0")
    assert(viaPlugin.forall(e => e.job_id.nonEmpty && e.app_id.nonEmpty), "job_id/app_id must be populated")

    // Ordering fix: every stage row of the one query carries the SAME correct 64-hex
    // fingerprint (attached via execution_id buffer flushed at SQL execution end).
    val fps = viaPlugin.map(_.plan_fingerprint).distinct
    assert(fps.size == 1 && fps.head.matches("[0-9a-f]{64}"),
      s"plugin path: expected one 64-hex fingerprint across stages, got $fps")
    info(s"per-stage fingerprint (plugin): ${fps.head}")

    // Parity: the two activation paths capture the same per-stage numbers.
    def shape(es: Seq[ApexStageEvent]) =
      es.map(e => (e.stage_id, e.shuffle_read_bytes, e.shuffle_write_bytes, e.task_count)).toSet
    assert(shape(viaPlugin) == shape(viaExtra),
      s"events differ between activation paths:\n  plugin=${shape(viaPlugin)}\n  extra =${shape(viaExtra)}")

    def render(es: Seq[ApexStageEvent]) =
      es.sortBy(_.stage_id).map(e =>
        s"stage=${e.stage_id} shRead=${e.shuffle_read_bytes} shWrite=${e.shuffle_write_bytes} tasks=${e.task_count}").mkString(" | ")
    info(s"plugin        : ${render(viaPlugin)}")
    info(s"extraListeners: ${render(viaExtra)}")
  }

  test("T9: collector DOWN — ~100-stage job completes, wall-clock not inflated (bounded drop)") {
    resetSessions()
    val spark = SparkSession.builder()
      .master("local[2]")
      .appName("apex-safety")
      .config("spark.plugins", "apex.ApexPlugin")
      .config("spark.apex.otlp.endpoint", "http://127.0.0.1:1") // DEAD collector
      .config("spark.sql.adaptive.enabled", "false")
      .config("spark.ui.enabled", "false")
      .config("spark.sql.shuffle.partitions", "2")
      .getOrCreate()

    try {
      val t0 = System.nanoTime()
      var i = 0
      while (i < 50) { // 50 shuffles × (map + reduce) = ~100 stages
        spark.range(0, 2000).selectExpr("id", "id % 50 as k").groupBy("k").count().collect()
        i += 1
      }
      val elapsedMs = (System.nanoTime() - t0) / 1000000
      info(s"50 shuffle jobs (~100 stages) with a DEAD collector completed in ${elapsedMs} ms")
      // A blocking sink (SimpleSpanProcessor, 5s timeout/export) would take >>60s for 100 stages.
      assert(elapsedMs < 60000, s"wall-clock inflated to ${elapsedMs} ms — the sink appears to be blocking")
    } finally {
      spark.stop()
      resetSessions()
    }
  }
}
