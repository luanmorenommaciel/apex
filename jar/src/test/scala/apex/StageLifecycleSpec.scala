package apex

import org.apache.spark.sql.SparkSession
import org.scalatest.funsuite.AnyFunSuite

class StageLifecycleSpec extends AnyFunSuite {
  private def await(description: String)(condition: => Boolean): Unit = {
    val deadline = System.nanoTime() + 10L * 1000L * 1000L * 1000L
    while (!condition && System.nanoTime() < deadline) {
      Thread.sleep(10L)
    }
    assert(condition, s"timed out waiting for $description")
  }

  test("fingerprint linkage failures are contained and warned once per execution") {
    val listener =
      new ApexStageListener(new CapturingSink, "local-app", "linkage-test", "local-job")

    val first = listener.recoverFingerprint(41L) {
      throw new NoSuchMethodError("binary details must not escape")
    }
    val repeated = listener.recoverFingerprint(41L) {
      throw new NoSuchMethodError("binary details must not escape")
    }

    assert(first == ("", ""))
    assert(repeated == ("", ""))
    assert(listener.fingerprintWarningCount == 1)
  }

  test("reused completed shuffle stages are released when their jobs end") {
    val spark = SparkSession.builder()
      .master("local[2]")
      .appName("apex-stage-lifecycle-experiment")
      .config("spark.ui.enabled", "false")
      .config("spark.sql.shuffle.partitions", "4")
      .getOrCreate()
    val sink = new CapturingSink
    val listener = new ApexStageListener(sink, "local-app", "lifecycle-experiment", "local-job")
    spark.sparkContext.addSparkListener(listener)

    try {
      val iterations = 12
      (0 until iterations).foreach { iteration =>
        val shuffled = spark.sparkContext
          .parallelize(0 until 1000, 4)
          .map(value => (value % 20, value))
          .reduceByKey(_ + _)
          .persist()

        val beforeMaterialize = sink.events.size
        shuffled.count()
        await(s"materialization events for iteration $iteration") {
          sink.events.size > beforeMaterialize
        }

        val beforeReuse = sink.events.size
        shuffled.filter(_._1 == iteration % 20).count()
        await(s"reuse events for iteration $iteration") {
          sink.events.size > beforeReuse
        }
        shuffled.unpersist(blocking = true)
      }

      await("job-end lifecycle cleanup") {
        val state = listener.lifecycleState
        state.stageToJob == 0 && state.activeStages == 0 && state.liveJobs == 0
      }
      val retained = listener.lifecycleState
      info(s"retained lifecycle state after 12 reused shuffles: $retained")
      assert(retained.stageToJob == 0)
      assert(retained.activeStages == 0)
      assert(retained.taskSamples == 0)
      assert(retained.stagePeakMem == 0)
      assert(retained.pendingCompletedStages == 0)
      assert(retained.stageToExec == 0)
      assert(retained.liveJobs == 0)
    } finally {
      spark.stop()
    }
  }
}
