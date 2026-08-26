package apex

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions.col
import org.apache.logging.log4j.{Level, LogManager}
import org.apache.logging.log4j.core.{LogEvent, Logger => CoreLogger}
import org.apache.logging.log4j.core.appender.AbstractAppender
import org.apache.logging.log4j.core.layout.PatternLayout
import org.scalatest.funsuite.AnyFunSuite

import java.lang.reflect.{InvocationHandler, Method, Proxy}
import java.util.concurrent.ConcurrentLinkedQueue
import java.util.concurrent.atomic.AtomicInteger

private object FailureInjectingSink {
  def create(onEmit: ApexStageEvent => Unit): ApexSink = {
    val handler = new InvocationHandler {
      override def invoke(proxy: Any, method: Method, args: Array[AnyRef]): AnyRef =
        method.getName match {
          case "emit" =>
            onEmit(args(0).asInstanceOf[ApexStageEvent])
            null
          case "emitPlanTransition" | "emitJobConf" | "close" => null
          case "toString" => "FailureInjectingSink"
          case "hashCode" => Int.box(System.identityHashCode(proxy))
          case "equals" => Boolean.box(proxy.asInstanceOf[AnyRef] eq args(0))
          case other => throw new UnsupportedOperationException(s"unexpected ApexSink method: $other")
        }
    }
    Proxy.newProxyInstance(
      classOf[ApexSink].getClassLoader,
      Array[Class[_]](classOf[ApexSink]),
      handler).asInstanceOf[ApexSink]
  }
}

/**
 * Test double whose `emit` always throws — used to prove that a sink failure
 * inside a listener callback (issue #36 DoD: "falha do listener não deve
 * quebrar o job") is caught by the `Try { ... }.recover { ... }` wrapping
 * every callback in [[ApexStageListener]], not just documented in a comment.
 */
class ThrowingSink {
  val emitCalls = new AtomicInteger(0)

  val asSink: ApexSink = FailureInjectingSink.create { _ =>
    emitCalls.incrementAndGet()
    throw new RuntimeException("injected-test-failure: apex.ThrowingSink.emit")
  }
}

/**
 * Test double whose `emit` always throws, like [[ThrowingSink]], but also records
 * whether each call originated from `ApexStageListener.flushExecution` (the
 * `onOtherEvent`/`SparkListenerSQLExecutionEnd` path, called only for real SQL/
 * DataFrame executions) as opposed to `dispatchStageEvent`'s direct-emit branches
 * called from `onStageCompleted`. `flushExecution` runs on the same listener bus
 * thread as every other callback, so a plain stack-trace scan is race-free here.
 */
class StackAwareThrowingSink {
  val emitCalls = new AtomicInteger(0)
  val flushExecutionEmitCalls = new AtomicInteger(0)

  val asSink: ApexSink = FailureInjectingSink.create { _ =>
    emitCalls.incrementAndGet()
    val calledFromFlushExecution = Thread.currentThread().getStackTrace.exists { frame =>
      frame.getClassName == "apex.ApexStageListener" && frame.getMethodName == "flushExecution"
    }
    if (calledFromFlushExecution) flushExecutionEmitCalls.incrementAndGet()
    throw new RuntimeException("injected-test-failure: apex.StackAwareThrowingSink.emit")
  }
}

/** Captures WARN messages from ApexStageListener without changing production logging. */
class ListenerWarnAppender(name: String)
    extends AbstractAppender(name, null, PatternLayout.createDefaultLayout(), false, Array.empty) {
  private val messages = new ConcurrentLinkedQueue[String]()

  override def append(event: LogEvent): Unit = {
    if (event.getLevel == Level.WARN) messages.add(event.getMessage.getFormattedMessage)
  }

  def contains(parts: String*): Boolean = {
    val iterator = messages.iterator()
    while (iterator.hasNext) {
      val message = iterator.next()
      if (parts.forall(message.contains)) return true
    }
    false
  }

  def containsPattern(pattern: scala.util.matching.Regex): Boolean = {
    val iterator = messages.iterator()
    while (iterator.hasNext) {
      if (pattern.findFirstIn(iterator.next()).nonEmpty) return true
    }
    false
  }
}

/** Test-only failure-injection harness; it does not change listener production code. */
class ListenerFailureIsolationSpec extends AnyFunSuite {
  private def await(description: String)(condition: => Boolean): Unit = {
    val deadline = System.nanoTime() + 30L * 1000L * 1000L * 1000L
    while (!condition && System.nanoTime() < deadline) Thread.sleep(20L)
    assert(condition, s"timed out waiting for $description")
  }

  private def captureListenerWarnings(): (CoreLogger, ListenerWarnAppender) = {
    val logger = LogManager.getLogger(classOf[ApexStageListener]).asInstanceOf[CoreLogger]
    val appender = new ListenerWarnAppender(s"listener-warn-${System.nanoTime()}")
    appender.start()
    logger.addAppender(appender)
    (logger, appender)
  }

  private def stopCapturing(logger: CoreLogger, appender: ListenerWarnAppender): Unit = {
    logger.removeAppender(appender)
    appender.stop()
  }

  test("a sink that always throws on emit does not break the job, and the listener keeps running") {
    val jobs = 5
    val spark = SparkSession.builder().master("local[2]").appName("apex-listener-failure-isolation-test")
      .config("spark.ui.enabled", "false").config("spark.sql.shuffle.partitions", "4").getOrCreate()
    val sink = new ThrowingSink
    val listener = new ApexStageListener(sink.asSink, "local-app", "failure-test", "local-job")
    val (logger, warnings) = captureListenerWarnings()
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
      assert(warnings.containsPattern(
        "apex: onStageCompleted failed for stage [0-9]+: injected-test-failure".r),
        "expected a WARN with the stage ID and cause for the injected RDD-path sink failure")

      // Listener lifecycle state is clean — the caught failure didn't leave
      // dangling per-stage/per-job bookkeeping behind.
      val state = listener.lifecycleState
      assert(state.stageToJob == 0)
      assert(state.activeStages == 0)
      assert(state.pendingCompletedStages == 0)
      assert(state.liveJobs == 0)
    } finally {
      stopCapturing(logger, warnings)
      spark.stop()
    }
  }

  test("a sink that always throws on emit does not break a real SQL/DataFrame job, " +
    "and the failure inside flushExecution (onOtherEvent / SparkListenerSQLExecutionEnd) is isolated") {
    val spark = SparkSession.builder().master("local[2]").appName("apex-listener-sql-failure-isolation-test")
      .config("spark.ui.enabled", "false").config("spark.sql.shuffle.partitions", "4").getOrCreate()
    val sink = new StackAwareThrowingSink
    val listener = new ApexStageListener(sink.asSink, "local-app", "sql-failure-test", "local-job")
    val (logger, warnings) = captureListenerWarnings()
    spark.sparkContext.addSparkListener(listener)
    try {
      // A real DataFrame aggregation forces spark.sql.execution.id to be set on the job's
      // properties, and drives a SparkListenerSQLExecutionEnd through onOtherEvent once the
      // query finishes — the only way flushExecution (and its sink.emit call, line 304) is
      // ever reached. parallelize(...) alone (as in the RDD test above) never exercises this.
      val rowCount = spark.range(0, 1000).groupBy((col("id") % 7).as("bucket")).count().count()
      assert(rowCount > 0, "SQL job must complete successfully despite the listener's sink " +
        "throwing on every emit, including inside flushExecution")

      await("flushExecution to run (and fail) at least once despite sink.emit always throwing") {
        sink.flushExecutionEmitCalls.get() > 0
      }

      // Proves the SQL execution path was actually exercised — not just that the job produced
      // no stages to report. If flushExecution were unreachable (e.g. SparkListenerSQLExecutionEnd
      // never fired, or execution_id was never attached), this would stay at 0 and the test above
      // would time out first.
      assert(sink.flushExecutionEmitCalls.get() > 0,
        "expected at least one sink.emit call originating from ApexStageListener.flushExecution")
      assert(warnings.contains("apex: onOtherEvent failed", "injected-test-failure"),
        "expected a WARN that clearly records the injected SQL/flushExecution sink failure")

      await("job-end lifecycle cleanup despite the SQL execution flush failing") {
        val state = listener.lifecycleState
        state.stageToJob == 0 && state.activeStages == 0 && state.liveJobs == 0
      }

      val state = listener.lifecycleState
      assert(state.stageToJob == 0)
      assert(state.activeStages == 0)
      assert(state.pendingCompletedStages == 0)
      assert(state.stageToExec == 0, "stageToExec entries must be released once their stage completes")
      assert(state.liveJobs == 0)
    } finally {
      stopCapturing(logger, warnings)
      spark.stop()
    }
  }
}
