package apex

import org.apache.spark._
import org.scalatest.funsuite.AnyFunSuite

class TaskFailureSemanticsSpec extends AnyFunSuite {
  test("scheduler failure matrix follows TaskFailedReason exactly") {
    val matrix = Seq(
      Success -> false,
      FetchFailed(null, 1, 2L, 3, 4, "fetch failed") -> false,
      ExceptionFailure(
        "java.lang.IllegalStateException",
        "user code failed",
        Array.empty[StackTraceElement],
        "java.lang.IllegalStateException: user code failed",
        None) -> true,
      TaskKilled("speculative loser") -> false,
      TaskCommitDenied(1, 0, 2) -> false,
      ExecutorLostFailure("executor-1", exitCausedByApp = false, Some("host lost")) -> false,
      ExecutorLostFailure("executor-1", exitCausedByApp = true, Some("application exit")) -> true,
      TaskResultLost -> true,
      UnknownReason -> true
    )

    matrix.foreach { case (reason, expected) =>
      assert(
        TaskFailureSemantics.countsTowardsTaskFailures(reason) == expected,
        s"$reason should count=$expected")
    }
  }
}
