package apex

import org.scalatest.funsuite.AnyFunSuite

class StageDurationStatsSpec extends AnyFunSuite {
  private def oneOutlier(taskCount: Int): Seq[Long] =
    Seq.fill(taskCount - 1)(100L) :+ 3000L

  test("nearest-rank p99 stops representing a single maximum at 100 tasks") {
    val expectedP99 = Map(
      8 -> 3000L,
      99 -> 3000L,
      100 -> 100L,
      200 -> 100L,
      400 -> 100L
    )

    expectedP99.foreach { case (taskCount, p99) =>
      val summary = StageDurationStats.summarize(oneOutlier(taskCount))
      assert(summary.p50Ms == 100L, s"unexpected p50 for $taskCount tasks")
      assert(summary.p99Ms == p99, s"unexpected p99 for $taskCount tasks")
      assert(summary.maxMs == 3000L, s"maximum must preserve the outlier for $taskCount tasks")
    }
  }

  test("two outliers remain invisible to p99 at 200 and 400 tasks") {
    Seq(200, 400).foreach { taskCount =>
      val durations = Seq.fill(taskCount - 2)(100L) ++ Seq(3000L, 3000L)
      val summary = StageDurationStats.summarize(durations)
      assert(summary.p99Ms == 100L, s"p99 unexpectedly captured two outliers for $taskCount tasks")
      assert(summary.maxMs == 3000L)
    }
  }

  test("healthy stages keep p50 p99 and max aligned") {
    Seq(100, 200, 400).foreach { taskCount =>
      assert(StageDurationStats.summarize(Seq.fill(taskCount)(100L)) ==
        StageDurationSummary(100L, 100L, 100L))
    }
  }

  test("empty stages emit zero duration metrics") {
    assert(StageDurationStats.summarize(Seq.empty) == StageDurationSummary(0L, 0L, 0L))
  }
}
