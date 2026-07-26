package apex

import org.apache.spark.{SparkConf, SparkContext}
import org.apache.spark.scheduler._
import org.apache.spark.sql.execution.QueryExecution
import org.apache.spark.sql.execution.ui.SparkListenerSQLExecutionEnd
import org.slf4j.LoggerFactory

import scala.collection.mutable
import scala.util.Try

/**
 * Driver-side SparkListener that turns each completed stage into one
 * [[ApexStageEvent]] (contract § "The telemetry event").
 *
 * Sourcing rules (verified against Spark 3.5 + 4.0):
 *   - Stage metrics come from `stageInfo.taskMetrics` (already summed across tasks).
 *   - `onTaskEnd` is used ONLY to collect per-task durations for p50/p99.
 *   - Live peak execution memory comes from `onExecutorMetricsUpdate`
 *     (`onStageExecutorMetrics` is history-server-replay-only, never live).
 *   - Every callback is wrapped in `Try`: a listener that throws is evicted from
 *     the bus, so none may escape.
 *
 * plan_fingerprint ordering fix (folded in with T-AQE):
 *   `QueryExecutionListener.onSuccess` fires at query END — after stages complete
 *   and emit — so attaching "latest plan" produced empty/stale fingerprints. Instead
 *   we BUFFER each stage event by its `execution_id` (from `spark.sql.execution.id`
 *   in the job's properties) and flush them with the correct fingerprint when the
 *   `SparkListenerSQLExecutionEnd` for that execution arrives on THIS same bus — its
 *   `qe` field carries the logical plan. One bus, one thread → no cross-bus race.
 *
 * Buffers are BOUNDED (guardrail: a missing fingerprint is recoverable, a driver
 * OOM is not). Over a per-execution or live-execution cap, we flush with an empty
 * fingerprint rather than grow. All callbacks run on the single listener-bus thread,
 * so the mutable maps need no synchronization.
 */
class ApexStageListener private (
    sink: ApexSink,
    confOpt: Option[SparkConf],
    private var appId: String,
    private var appName: String,
    private var jobId: String)
    extends SparkListener {

  /** Primary activation — `spark.plugins`: the plugin has the live SparkContext. */
  def this(sink: ApexSink, appId: String, appName: String, jobId: String) =
    this(sink, None, appId, appName, jobId)

  /** Fallback activation — `spark.extraListeners=apex.ApexStageListener` (SparkConf ctor). */
  def this(conf: SparkConf) = this(ApexSinks.instance(conf), Some(conf), null, null, null)

  private val logger = LoggerFactory.getLogger(getClass)

  private val MaxLiveExecutions       = 128
  private val MaxBufferedPerExecution = 4096

  private val stageToJob   = mutable.Map.empty[Int, String]        // stageId → contract job_id
  private val taskDur      = mutable.Map.empty[(Int, Int), mutable.ArrayBuffer[Long]]
  private val stagePeakMem = mutable.Map.empty[(Int, Int), Long]

  private val stageToExec  = mutable.Map.empty[Int, Long]          // stageId → SQL execution_id
  private val execToStages = mutable.Map.empty[Long, mutable.Set[Int]]
  // execution_id → stage events awaiting their fingerprint (insertion-ordered for LRU eviction)
  private val execBuffers  = mutable.LinkedHashMap.empty[Long, mutable.ArrayBuffer[ApexStageEvent]]
  private val overflowed   = mutable.Set.empty[Long]              // executions past cap → emit immediately

  private def ensureIds(): Unit =
    if (appId == null) {
      val sc = SparkContext.getOrCreate()
      appId = sc.applicationId
      appName = confOpt.flatMap(c => Option(c.get("spark.app.name", null))).getOrElse(sc.appName)
      jobId = confOpt.flatMap(_.getOption("spark.apex.job_id")).getOrElse(appId)
    }

  override def onJobStart(e: SparkListenerJobStart): Unit = Try {
    ensureIds()
    val execId = Option(e.properties).flatMap(p => Option(p.getProperty("spark.sql.execution.id"))).flatMap(s => Try(s.toLong).toOption)
    e.stageInfos.foreach { si =>
      stageToJob.update(si.stageId, jobId)
      execId.foreach { id =>
        stageToExec.update(si.stageId, id)
        execToStages.getOrElseUpdate(id, mutable.Set.empty[Int]) += si.stageId
      }
    }
  }.recover { case t => logger.warn(s"apex: onJobStart failed: ${t.getMessage}") }

  override def onTaskEnd(e: SparkListenerTaskEnd): Unit = Try {
    val key = (e.stageId, e.stageAttemptId)
    taskDur.getOrElseUpdate(key, mutable.ArrayBuffer.empty[Long]) += e.taskInfo.duration
  }.recover { case t => logger.warn(s"apex: onTaskEnd failed: ${t.getMessage}") }

  override def onExecutorMetricsUpdate(u: SparkListenerExecutorMetricsUpdate): Unit = Try {
    u.executorUpdates.foreach { case ((stageId, attempt), m) =>
      if (stageId >= 0) {
        val key = (stageId, attempt)
        stagePeakMem.update(key, math.max(stagePeakMem.getOrElse(key, 0L), m.getMetricValue("JVMHeapMemory")))
      }
    }
  }.recover { case t => logger.warn(s"apex: onExecutorMetricsUpdate failed: ${t.getMessage}") }

  override def onStageCompleted(e: SparkListenerStageCompleted): Unit = Try {
    ensureIds()
    val si  = e.stageInfo
    val key = (si.stageId, si.attemptNumber())
    val durationStats = StageDurationStats.summarize(
      taskDur.remove(key).map(_.toSeq).getOrElse(Seq.empty[Long])
    )
    val livePeak = stagePeakMem.remove(key).getOrElse(0L)
    val tm = Option(si.taskMetrics) // null for stages with no tasks

    val ev = ApexStageEvent(
      job_id        = stageToJob.getOrElse(si.stageId, jobId),
      app_id        = appId,
      app_name      = appName,
      stage_id      = si.stageId,
      stage_attempt = si.attemptNumber(),
      ts            = si.completionTime.getOrElse(System.currentTimeMillis()),
      shuffle_read_bytes       = tm.map(_.shuffleReadMetrics.totalBytesRead).getOrElse(0L),
      shuffle_write_bytes      = tm.map(_.shuffleWriteMetrics.bytesWritten).getOrElse(0L),
      spill_disk_bytes         = tm.map(_.diskBytesSpilled).getOrElse(0L),
      spill_mem_bytes          = tm.map(_.memoryBytesSpilled).getOrElse(0L),
      gc_time_ms               = tm.map(_.jvmGCTime).getOrElse(0L),
      input_bytes              = tm.map(_.inputMetrics.bytesRead).getOrElse(0L),
      output_bytes             = tm.map(_.outputMetrics.bytesWritten).getOrElse(0L),
      peak_execution_mem_bytes = math.max(tm.map(_.peakExecutionMemory).getOrElse(0L), livePeak),
      task_count               = si.numTasks,
      task_duration_p50_ms     = durationStats.p50Ms,
      task_duration_p99_ms     = durationStats.p99Ms,
      task_duration_max_ms     = durationStats.maxMs,
      plan_fingerprint         = "", // attached at flush, keyed by execution_id
      plan_json                = ""
    )

    stageToExec.get(si.stageId) match {
      case Some(execId) if !overflowed.contains(execId) =>
        execBuffers.getOrElseUpdate(execId, mutable.ArrayBuffer.empty[ApexStageEvent]) += ev
        enforceCaps(execId)
      case _ =>
        // Non-SQL job (no execution_id → no logical plan), or this execution overflowed.
        sink.emit(ev)
    }
  }.recover { case t => logger.warn(s"apex: onStageCompleted failed for stage ${e.stageInfo.stageId}: ${t.getMessage}") }

  // The SQL execution finished on THIS bus — attach the correct fingerprint and flush.
  override def onOtherEvent(event: SparkListenerEvent): Unit = Try {
    event match {
      case end: SparkListenerSQLExecutionEnd =>
        val (fp, pj) = fingerprintOf(end)
        flushExecution(end.executionId, fp, pj)
      case _ => ()
    }
  }.recover { case t => logger.warn(s"apex: onOtherEvent failed: ${t.getMessage}") }

  /** Read the logical plan off the End event's driver-local `qe` (reflected getter). */
  private def fingerprintOf(end: SparkListenerSQLExecutionEnd): (String, String) =
    Try(end.getClass.getMethod("qe").invoke(end))
      .toOption.flatMap(Option(_)).map(_.asInstanceOf[QueryExecution])
      .flatMap { qe =>
        Try((ApexPlanFingerprint.fingerprint(qe.optimizedPlan), ApexPlanFingerprint.redactedPlan(qe.optimizedPlan))).toOption
      }
      .getOrElse(("", "")) // graceful: a missing plan means an empty (recoverable) fingerprint

  private def flushExecution(execId: Long, fp: String, pj: String): Unit = {
    execBuffers.remove(execId).foreach { buf =>
      buf.foreach(ev => sink.emit(ev.copy(plan_fingerprint = fp, plan_json = pj)))
    }
    execToStages.remove(execId).foreach(_.foreach { sid => stageToExec.remove(sid); stageToJob.remove(sid) })
    overflowed.remove(execId)
  }

  /** Bound driver memory: flush-with-empty rather than grow past the caps. */
  private def enforceCaps(execId: Long): Unit = {
    if (execBuffers.get(execId).exists(_.size > MaxBufferedPerExecution)) {
      logger.warn(s"apex: execution $execId exceeded $MaxBufferedPerExecution buffered stages — flushing without fingerprint")
      flushExecution(execId, "", "")
      overflowed += execId
    }
    while (execBuffers.size > MaxLiveExecutions) {
      val oldest = execBuffers.head._1
      logger.warn(s"apex: >$MaxLiveExecutions live executions — evicting $oldest without fingerprint")
      flushExecution(oldest, "", "")
      overflowed += oldest
    }
  }
}
