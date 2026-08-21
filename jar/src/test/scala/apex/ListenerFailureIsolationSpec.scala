package apex

import org.apache.spark.sql.SparkSession
import org.scalatest.funsuite.AnyFunSuite

import java.util.concurrent.atomic.AtomicInteger

/**
 * Test double whose `emit` always throws — used to prove that a sink failure
 * inside a listener callback (issue #36 DoD: "falha do listener não deve
 * quebrar o job") is caught by the `Try { ... }.recover { ... }` wrapping
 * every callback in [[ApexStageListener]], not just documented in a comment.
 */
class ThrowingSink extends ApexSink {
  val emitCalls = new AtomicInteger(0)

  override def emit(ev: ApexStageEvent): Unit = {
    emitCalls.incrementAndGet()
    throw new RuntimeException("injected-test-failure: apex.ThrowingSink.emit")
  }
  override def emitPlanTransition(t: PlanTransition): Unit = ()
  override def emitJobConf(ev: JobConfEvent): Unit = ()
  override def close(): Unit = ()
}

/** Test-only failure-injection harness; it does not change listener production code. */
class ListenerFailureIsolationSpec extends AnyFunSuite {
  private def await(description: String)(condition: => Boolean): Unit = {
    val deadline = System.nanoTime() + 30L * 1000L * 1000L * 1000L
    while (!condition && System.nanoTime() < deadline) Thread.sleep(20L)
    assert(condition, s"timed out waiting for $description")
  }

  test("a sink that always throws on emit does not break the job, and the listener keeps running") {
    val jobs = 5
    val spark = SparkSession.builder().master("local[2]").appName("apex-listener-failure-isolation-test")
      .config("spark.ui.enabled", "false").config("spark.sql.shuffle.partitions", "4").getOrCreate()
    val sink = new ThrowingSink
    val listener = new ApexStageListener(sink, "local-app", "failure-test", "local-job")
    spark.sparkContext.addSparkListener(listener)
    try {
      (0 until jobs).foreach { _ =>
        // Every job's onStageCompleted will hit sink.emit, which always throws.
        val total = spark.sparkContext.parallelize(0 until 500, 2).map(v => (v % 7, v)).reduceByKey(_ + _).values.sum()
        assert(total > 0, "job must complete successfully despite the listener's sink throwing")
      }

      await("job-end lifecycle cleanup despite repeated sink failures") {
        val state = listener.lifecycleState
        state.stageToJob == 0 && state.activeStages == 0 && state.liveJobs == 0
      }

      // The listener kept being invoked across all 5 jobs — it was never evicted
      // from the bus after the first failure, and each onStageCompleted really
      // reached sink.emit (the Try body ran to completion, not short-circuited).
      assert(sink.emitCalls.get() >= jobs,
        s"expected at least $jobs emit attempts (one per job's final stage), got ${sink.emitCalls.get()}")

      // Listener lifecycle state is clean — the caught failure didn't leave
      // dangling per-stage/per-job bookkeeping behind.
      val state = listener.lifecycleState
      assert(state.stageToJob == 0)
      assert(state.activeStages == 0)
      assert(state.pendingCompletedStages == 0)
      assert(state.liveJobs == 0)
    } finally spark.stop()
  }
}
