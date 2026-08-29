package apex

import org.apache.spark.sql.SparkSession
import org.scalatest.funsuite.AnyFunSuite

/** Test-only long-lived-driver harness; it does not change listener production code. */
class DriverListenerSoakSpec extends AnyFunSuite {
  private def await(description: String)(condition: => Boolean): Unit = {
    val deadline = System.nanoTime() + 30L * 1000L * 1000L * 1000L
    while (!condition && System.nanoTime() < deadline) Thread.sleep(20L)
    assert(condition, s"timed out waiting for $description")
  }

  test("controlled repeated jobs leave no listener lifecycle state") {
    val cycles = sys.props.get("apex.soak.cycles").flatMap(value => scala.util.Try(value.toInt).toOption).getOrElse(60)
    require(cycles > 0, "apex.soak.cycles must be positive")
    val spark = SparkSession.builder().master("local[2]").appName("apex-driver-listener-soak-test")
      .config("spark.ui.enabled", "false").config("spark.sql.shuffle.partitions", "4").getOrCreate()
    val sink = new CapturingSink
    val listener = new ApexStageListener(sink, "local-app", "soak-test", "local-job")
    spark.sparkContext.addSparkListener(listener)
    try {
      (0 until cycles).foreach { _ =>
        val total = spark.sparkContext.parallelize(0 until 2000, 4).map(value => (value % 31, value)).reduceByKey(_ + _).values.sum()
        assert(total > 0)
      }
      await("job-end lifecycle cleanup") {
        val state = listener.lifecycleState
        state.stageToJob == 0 && state.activeStages == 0 && state.liveJobs == 0
      }
      val state = listener.lifecycleState
      assert(state.stageToJob == 0)
      assert(state.taskSamples == 0)
      assert(state.stagePeakMem == 0)
      assert(state.activeStages == 0)
      assert(state.pendingCompletedStages == 0)
      assert(state.stageToExec == 0)
      assert(state.liveJobs == 0)
      assert(sink.events.size >= cycles)
    } finally spark.stop()
  }
}
