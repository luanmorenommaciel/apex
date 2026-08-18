package apex

import org.apache.spark.{SparkConf, SparkContext, TaskEndReason, TaskFailedReason}
import org.apache.spark.scheduler._
import org.apache.spark.sql.execution.QueryExecution
import org.apache.spark.sql.execution.ui.SparkListenerSQLExecutionEnd
import org.slf4j.LoggerFactory

import java.util.Properties
import scala.collection.mutable
import scala.util.Try
import scala.util.control.NonFatal

private[apex] final case class PendingCompletedStage(
  baseEvent: ApexStageEvent,
  samples: StageTaskSamples,
  executionId: Option[Long])

private[apex] final case class ApexStageListenerState(
  stageToJob: Int,
  taskSamples: Int,
  stagePeakMem: Int,
  activeStages: Int,
  pendingCompletedStages: Int,
  stageToExec: Int,
  liveJobs: Int)

/**
 * Driver-side SparkListener that turns each completed stage into one
 * [[ApexStageEvent]] (contract § "The telemetry event").
 *
 * Sourcing rules (verified against Spark 3.5 + 4.0):
 *   - Stage metrics come from `stageInfo.taskMetrics` (already summed across tasks).
 *   - `onTaskStart`/`onTaskEnd` track attempts, termination state and duration
 *     samples without treating a missing duration as zero.
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
  private val MaxOverflowedExecutions = MaxLiveExecutions * 4
  private val MaxPendingCompletedStages = 4096

  private val stageToJob   = mutable.Map.empty[Int, String]        // stageId → contract job_id
  private val jobStages    = new JobStageRegistry
  private val taskSamples  = mutable.Map.empty[(Int, Int), StageTaskSamples]
  private val stagePeakMem = mutable.Map.empty[(Int, Int), Long]
  private val activeStages = new ActiveStageRegistry
  private val pendingCompletedStages =
    mutable.LinkedHashMap.empty[(Int, Int), PendingCompletedStage]

  private val stageToExec  = mutable.Map.empty[Int, Long]          // stageId → SQL execution_id
  // execution_id → stage events awaiting their fingerprint (insertion-ordered for LRU eviction)
  private val execBuffers  = mutable.LinkedHashMap.empty[Long, mutable.ArrayBuffer[ApexStageEvent]]
  private val overflowed   = mutable.LinkedHashSet.empty[Long]    // bounded recent executions past cap
  private val closedExecutionPlans =
    mutable.LinkedHashMap.empty[Long, (String, String)]
  private val warnedFingerprintExecutions = mutable.LinkedHashSet.empty[Long]

  /** Package-local observation seam for lifecycle regression tests. */
  private[apex] def lifecycleState: ApexStageListenerState =
    ApexStageListenerState(
      stageToJob = stageToJob.size,
      taskSamples = taskSamples.size,
      stagePeakMem = stagePeakMem.size,
      activeStages = activeStages.size,
      pendingCompletedStages = pendingCompletedStages.size,
      stageToExec = stageToExec.size,
      liveJobs = jobStages.size
    )

  private def ensureIds(): Unit =
    if (appId == null) {
      val sc = SparkContext.getOrCreate()
      appId = sc.applicationId
      appName = confOpt.flatMap(c => Option(c.get("spark.app.name", null))).getOrElse(sc.appName)
      jobId = confOpt.flatMap(_.getOption("spark.apex.job_id")).getOrElse(appId)
    }

  private def executionIdOf(properties: Properties): Option[Long] =
    Option(properties)
      .flatMap(p => Option(p.getProperty("spark.sql.execution.id")))
      .flatMap(s => Try(s.toLong).toOption)

  override def onJobStart(e: SparkListenerJobStart): Unit = Try {
    ensureIds()
    val execId = executionIdOf(e.properties)
    val registeredStages =
      e.stageInfos.iterator.map(si => (si.stageId, si.attemptNumber())).toSet
    jobStages.register(e.jobId, registeredStages)
    e.stageInfos.foreach { si =>
      stageToJob.update(si.stageId, jobId)
      activeStages.submit(si.stageId, si.attemptNumber())
      execId.foreach { id =>
        stageToExec.update(si.stageId, id)
      }
    }
  }.recover { case t => logger.warn(s"apex: onJobStart failed: ${t.getMessage}") }

  override def onJobEnd(e: SparkListenerJobEnd): Unit = Try {
    jobStages.release(e.jobId).foreach(discardUnsubmittedStage)
  }.recover { case t => logger.warn(s"apex: onJobEnd failed: ${t.getMessage}") }

  override def onStageSubmitted(e: SparkListenerStageSubmitted): Unit = Try {
    ensureIds()
    val stageId = e.stageInfo.stageId
    activeStages.submit(stageId, e.stageInfo.attemptNumber())
    stageToJob.update(stageId, jobId)
    executionIdOf(e.properties).foreach(id => stageToExec.update(stageId, id))
  }.recover { case t => logger.warn(s"apex: onStageSubmitted failed: ${t.getMessage}") }

  override def onTaskStart(e: SparkListenerTaskStart): Unit = Try {
    val key = (e.stageId, e.stageAttemptId)
    if (activeStages.accepts(e.stageId, e.stageAttemptId)) {
      taskSamples.getOrElseUpdate(key, new StageTaskSamples).recordStart()
    }
  }.recover { case t => logger.warn(s"apex: onTaskStart failed: ${t.getMessage}") }

  override def onTaskEnd(e: SparkListenerTaskEnd): Unit = Try {
    val key = (e.stageId, e.stageAttemptId)
    if (activeStages.accepts(e.stageId, e.stageAttemptId)) {
      recordTaskEnd(taskSamples.getOrElseUpdate(key, new StageTaskSamples), e)
    } else {
      pendingCompletedStages.get(key).foreach { pending =>
        recordTaskEnd(pending.samples, e)
        if (!pending.samples.hasPendingAttempts) {
          pendingCompletedStages.remove(key)
          warnMissingDurations(key, pending.samples)
          dispatchStageEvent(withSamples(pending.baseEvent, pending.samples.summary), pending.executionId)
        }
      }
    }
  }.recover { case t => logger.warn(s"apex: onTaskEnd failed: ${t.getMessage}") }

  override def onExecutorMetricsUpdate(u: SparkListenerExecutorMetricsUpdate): Unit = Try {
    u.executorUpdates.foreach { case ((stageId, attempt), m) =>
      if (stageId >= 0 && activeStages.accepts(stageId, attempt)) {
        val key = (stageId, attempt)
        stagePeakMem.update(key, math.max(stagePeakMem.getOrElse(key, 0L), m.getMetricValue("JVMHeapMemory")))
      }
    }
  }.recover { case t => logger.warn(s"apex: onExecutorMetricsUpdate failed: ${t.getMessage}") }

  override def onStageCompleted(e: SparkListenerStageCompleted): Unit = Try {
    ensureIds()
    val si  = e.stageInfo
    val key = (si.stageId, si.attemptNumber())
    if (activeStages.complete(si.stageId, si.attemptNumber())) {
      val sampleState = taskSamples.remove(key).getOrElse(new StageTaskSamples)
      val samples = sampleState.summary
      val livePeak = stagePeakMem.remove(key).getOrElse(0L)
      val tm = Option(si.taskMetrics) // null for stages with no tasks
      val stageJobId = stageToJob.remove(si.stageId).getOrElse(jobId)
      val executionId = stageToExec.remove(si.stageId)

      val ev = ApexStageEvent(
        job_id        = stageJobId,
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
        executor_run_time_ms     = tm.map(_.executorRunTime).getOrElse(0L),
        input_bytes              = tm.map(_.inputMetrics.bytesRead).getOrElse(0L),
        output_bytes             = tm.map(_.outputMetrics.bytesWritten).getOrElse(0L),
        peak_execution_mem_bytes = math.max(tm.map(_.peakExecutionMemory).getOrElse(0L), livePeak),
        task_count               = si.numTasks,
        task_duration_p50_ms     = samples.allAttempts.p50Ms,
        task_duration_p99_ms     = samples.allAttempts.p99Ms,
        task_duration_max_ms     = samples.allAttempts.maxMs,
        task_duration_sample_count = samples.taskDurationSampleCount,
        successful_task_duration_p50_ms = samples.successfulTasks.p50Ms,
        successful_task_duration_p99_ms = samples.successfulTasks.p99Ms,
        successful_task_duration_max_ms = samples.successfulTasks.maxMs,
        successful_task_sample_count = samples.successfulTaskSampleCount,
        successful_task_shuffle_read_bytes_p50 = samples.successfulTaskShuffleReadBytesP50,
        successful_task_shuffle_read_bytes_max = samples.successfulTaskShuffleReadBytesMax,
        successful_task_shuffle_read_bytes_sample_count =
          samples.successfulTaskShuffleReadBytesSampleCount,
        task_attempt_count = samples.taskAttemptCount,
        task_failed_attempt_count = samples.taskFailedAttemptCount,
        task_counted_failure_attempt_count = samples.taskCountedFailureAttemptCount,
        task_killed_attempt_count = samples.taskKilledAttemptCount,
        task_speculative_attempt_count = samples.taskSpeculativeAttemptCount,
        plan_fingerprint         = "", // attached at flush, keyed by execution_id
        plan_json                = ""
      )

      if (sampleState.hasPendingAttempts) {
        pendingCompletedStages.update(key, PendingCompletedStage(ev, sampleState, executionId))
        enforcePendingStageCap()
      } else {
        warnMissingDurations(key, sampleState)
        dispatchStageEvent(ev, executionId)
      }
    }
  }.recover { case t => logger.warn(s"apex: onStageCompleted failed for stage ${e.stageInfo.stageId}: ${t.getMessage}") }

  // The SQL execution finished on THIS bus — attach the correct fingerprint and flush.
  override def onOtherEvent(event: SparkListenerEvent): Unit = Try {
    event match {
      case end: SparkListenerSQLExecutionEnd =>
        val (fp, pj) = fingerprintOf(end)
        rememberClosedExecution(end.executionId, fp, pj)
        flushExecution(end.executionId, fp, pj)
      case _ => ()
    }
  }.recover { case t => logger.warn(s"apex: onOtherEvent failed: ${t.getMessage}") }

  override def onApplicationEnd(e: SparkListenerApplicationEnd): Unit = Try {
    pendingCompletedStages.keys.toList.foreach(flushPendingStage)
    execBuffers.keys.toList.foreach(id => flushExecution(id, "", ""))
    stageToJob.clear()
    jobStages.clear()
    taskSamples.clear()
    stagePeakMem.clear()
    activeStages.clear()
    pendingCompletedStages.clear()
    stageToExec.clear()
    execBuffers.clear()
    overflowed.clear()
    closedExecutionPlans.clear()
    warnedFingerprintExecutions.clear()
  }.recover { case t => logger.warn(s"apex: onApplicationEnd failed: ${t.getMessage}") }

  /** Contain both ordinary failures and binary-linkage failures from optional query libraries. */
  private[apex] def recoverFingerprint(
      executionId: Long)(compute: => (String, String)): (String, String) =
    try compute
    catch {
      case t: LinkageError =>
        warnFingerprintFailure(executionId, t)
        ("", "")
      case NonFatal(t) =>
        warnFingerprintFailure(executionId, t)
        ("", "")
    }

  private[apex] def fingerprintWarningCount: Int = warnedFingerprintExecutions.size

  /** Read the logical plan off the End event's driver-local `qe` (reflected getter). */
  private def fingerprintOf(end: SparkListenerSQLExecutionEnd): (String, String) =
    recoverFingerprint(end.executionId) {
      val method = end.getClass.getMethod("qe")
      val raw = method.invoke(end)
      val qe = Option(raw).map(_.asInstanceOf[QueryExecution])
        .getOrElse(throw new IllegalStateException("missing_query_execution"))
      (
        ApexPlanFingerprint.fingerprint(qe.optimizedPlan),
        ApexPlanFingerprint.redactedPlan(qe.optimizedPlan)
      )
    }

  private def warnFingerprintFailure(executionId: Long, cause: Throwable): Unit = {
    if (!warnedFingerprintExecutions.contains(executionId)) {
      logger.warn(
        s"apex: fingerprint unavailable execution=$executionId cause=${cause.getClass.getSimpleName}")
      warnedFingerprintExecutions += executionId
      while (warnedFingerprintExecutions.size > MaxOverflowedExecutions) {
        warnedFingerprintExecutions.remove(warnedFingerprintExecutions.head)
      }
    }
  }

  private def flushExecution(execId: Long, fp: String, pj: String): Unit = {
    execBuffers.remove(execId).foreach { buf =>
      buf.foreach(ev => sink.emit(ev.copy(plan_fingerprint = fp, plan_json = pj)))
    }
    overflowed.remove(execId)
  }

  private def recordTaskEnd(samples: StageTaskSamples, e: SparkListenerTaskEnd): Unit = {
    val durationMs =
      if (e.taskInfo.finished) Try(e.taskInfo.duration).toOption else None
    samples.record(
      logicalPartitionId = TaskIdentity.logicalPartitionId(e.taskInfo.partitionId, e.taskInfo.index),
      durationMs = durationMs,
      successful = e.taskInfo.successful,
      failed = e.taskInfo.failed,
      killed = e.taskInfo.killed,
      speculative = e.taskInfo.speculative,
      countedFailure = TaskFailureSemantics.countsTowardsTaskFailures(e.reason),
      shuffleReadBytes =
        Option(e.taskMetrics).flatMap(metrics =>
          Option(metrics.shuffleReadMetrics).map(_.totalBytesRead))
    )
  }

  private def withSamples(ev: ApexStageEvent, samples: StageTaskSampleSummary): ApexStageEvent =
    ev.copy(
      task_duration_p50_ms = samples.allAttempts.p50Ms,
      task_duration_p99_ms = samples.allAttempts.p99Ms,
      task_duration_max_ms = samples.allAttempts.maxMs,
      task_duration_sample_count = samples.taskDurationSampleCount,
      successful_task_duration_p50_ms = samples.successfulTasks.p50Ms,
      successful_task_duration_p99_ms = samples.successfulTasks.p99Ms,
      successful_task_duration_max_ms = samples.successfulTasks.maxMs,
      successful_task_sample_count = samples.successfulTaskSampleCount,
      successful_task_shuffle_read_bytes_p50 = samples.successfulTaskShuffleReadBytesP50,
      successful_task_shuffle_read_bytes_max = samples.successfulTaskShuffleReadBytesMax,
      successful_task_shuffle_read_bytes_sample_count =
        samples.successfulTaskShuffleReadBytesSampleCount,
      task_attempt_count = samples.taskAttemptCount,
      task_failed_attempt_count = samples.taskFailedAttemptCount,
      task_counted_failure_attempt_count = samples.taskCountedFailureAttemptCount,
      task_killed_attempt_count = samples.taskKilledAttemptCount,
      task_speculative_attempt_count = samples.taskSpeculativeAttemptCount
    )

  private def dispatchStageEvent(ev: ApexStageEvent, executionId: Option[Long]): Unit =
    executionId match {
      case Some(execId) =>
        closedExecutionPlans.get(execId) match {
          case Some((fp, pj)) =>
            sink.emit(ev.copy(plan_fingerprint = fp, plan_json = pj))
          case None if !overflowed.contains(execId) =>
            execBuffers.getOrElseUpdate(execId, mutable.ArrayBuffer.empty[ApexStageEvent]) += ev
            enforceCaps(execId)
          case None =>
            sink.emit(ev)
        }
      case None =>
        sink.emit(ev)
    }

  private def flushPendingStage(key: (Int, Int)): Unit =
    pendingCompletedStages.remove(key).foreach { pending =>
      logger.warn(
        s"apex: flushing stage ${key._1}.${key._2} with unfinished task attempts")
      warnMissingDurations(key, pending.samples)
      dispatchStageEvent(withSamples(pending.baseEvent, pending.samples.summary), pending.executionId)
    }

  private def warnMissingDurations(key: (Int, Int), samples: StageTaskSamples): Unit =
    if (samples.missingDurationCount > 0) {
      logger.warn(
        s"apex: task duration unavailable stage=${key._1} attempt=${key._2} " +
          s"count=${samples.missingDurationCount}")
    }

  private def discardUnsubmittedStage(key: (Int, Int)): Unit = {
    val (stageId, attempt) = key
    if (activeStages.discard(stageId, attempt)) {
      taskSamples.remove(key)
      stagePeakMem.remove(key)
    }
    if (!jobStages.referencesStageId(stageId)) {
      stageToJob.remove(stageId)
      stageToExec.remove(stageId)
    }
  }

  private def enforcePendingStageCap(): Unit =
    while (pendingCompletedStages.size > MaxPendingCompletedStages) {
      flushPendingStage(pendingCompletedStages.head._1)
    }

  private def rememberClosedExecution(execId: Long, fp: String, pj: String): Unit = {
    closedExecutionPlans.remove(execId)
    closedExecutionPlans.update(execId, (fp, pj))
    while (closedExecutionPlans.size > MaxLiveExecutions) {
      closedExecutionPlans.remove(closedExecutionPlans.head._1)
    }
  }

  private def markOverflowed(execId: Long): Unit = {
    overflowed.remove(execId)
    overflowed += execId
    while (overflowed.size > MaxOverflowedExecutions) {
      overflowed.remove(overflowed.head)
    }
  }

  /** Bound driver memory: flush-with-empty rather than grow past the caps. */
  private def enforceCaps(execId: Long): Unit = {
    if (execBuffers.get(execId).exists(_.size > MaxBufferedPerExecution)) {
      logger.warn(s"apex: execution $execId exceeded $MaxBufferedPerExecution buffered stages — flushing without fingerprint")
      flushExecution(execId, "", "")
      markOverflowed(execId)
    }
    while (execBuffers.size > MaxLiveExecutions) {
      val oldest = execBuffers.head._1
      logger.warn(s"apex: >$MaxLiveExecutions live executions — evicting $oldest without fingerprint")
      flushExecution(oldest, "", "")
      markOverflowed(oldest)
    }
  }
}

private[apex] object TaskFailureSemantics {
  def countsTowardsTaskFailures(reason: TaskEndReason): Boolean =
    reason match {
      case failed: TaskFailedReason => failed.countTowardsTaskFailures
      case _ => false
    }
}
