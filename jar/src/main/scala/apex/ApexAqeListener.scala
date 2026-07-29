package apex

import org.apache.spark.{SparkConf, SparkContext}
import org.apache.spark.scheduler.{SparkListener, SparkListenerEvent}
import org.apache.spark.sql.execution.SparkPlanInfo
import org.apache.spark.sql.execution.ui.{SparkListenerDriverAccumUpdates, SparkListenerSQLAdaptiveExecutionUpdate, SparkListenerSQLExecutionEnd, SparkListenerSQLExecutionStart}
import org.slf4j.LoggerFactory

import scala.collection.mutable
import scala.util.Try

/**
 * Captures AQE's OWN runtime decisions (contract v0.2 § "AQE plan transitions"),
 * the signal DataFlint/sparkMeasure lack — they aggregate `TaskEnd` symptoms; this
 * records that Spark split a skewed join / demoted SMJ→BHJ / coalesced partitions.
 *
 * Mechanism (all verified against Spark 3.5 + 4.0):
 *   - `SparkListenerSQLAdaptiveExecutionUpdate` fires LIVE on the driver bus each
 *     time AQE re-plans (`AdaptiveSparkPlanExec.onUpdatePlan`), delivered via
 *     `onOtherEvent`. It carries a `SparkPlanInfo` SNAPSHOT of the current physical
 *     plan — so we keep the prior snapshot per `execution_id` and DIFF consecutive
 *     ones, emitting only real STRUCTURAL changes (no-op re-plans are dropped).
 *   - Baseline is the pre-AQE plan from `SparkListenerSQLExecutionStart`, so even
 *     the first re-plan is captured.
 *
 * Detection tiers (contract honesty): join-strategy switch (join nodeName change)
 * and skew/coalesce/local (`AQEShuffleRead` `simpleString` descriptor) are HIGH
 * confidence — structural. We never ship `physicalPlanDescription`; `detail`/`before`/
 * `after` are built from node names + AQE descriptors only (no literals).
 *
 * Skew counts: the descriptor counts skewed PARTITIONS (Spark's own
 * `numSkewedPartitions` driver metric), not AQEShuffleRead nodes — one read can
 * split several hot partitions, and counting reads undercounts ("skewed x1" when
 * two hot partitions split). The metric value is not in the plan snapshot; Spark
 * posts it as `SparkListenerDriverAccumUpdates` when the skewed read EXECUTES,
 * after the re-plan update. So a skew_split is parked until the value lands and
 * emitted with the true count; if it never lands (aborted query), execution end
 * flushes it with the read count as a fallback. Same strings on 3.5/4.0/4.1.
 *
 * Behind `spark.apex.aqe.enabled`; registered by the plugin. Rides the same sink +
 * bounded queue + `Try`. Snapshot maps are bounded and cleaned on execution end.
 * All callbacks run on the single listener-bus thread → no synchronization.
 */
class ApexAqeListener(sink: ApexSink, private var jobId: String) extends SparkListener {

  /**
   * Plugin activation. Resolves `job_id` lazily because `applicationId` is null at
   * plugin-init time — the same reason [[ApexStageListener]] resolves lazily.
   */
  def this(conf: SparkConf) = this(ApexSinks.instance(conf), conf.getOption("spark.apex.job_id").orNull)

  private val logger = LoggerFactory.getLogger(getClass)
  private val MaxLiveExecutions = 128

  private val snapshots   = mutable.LinkedHashMap.empty[Long, ApexAqeListener.PlanShape]
  private val nextSeq     = mutable.Map.empty[Long, Int]
  private val pendingSkew = mutable.Map.empty[Long, List[ApexAqeListener.PendingSkew]]
  private val accumValues = mutable.Map.empty[Long, mutable.Map[Long, Long]]

  // spark.apex.job_id override, else applicationId — resolved at event time (context is up by then).
  private def resolvedJobId(): String = {
    if (jobId == null) {
      val sc = SparkContext.getOrCreate()
      jobId = sc.getConf.getOption("spark.apex.job_id").getOrElse(sc.applicationId)
    }
    jobId
  }

  override def onOtherEvent(event: SparkListenerEvent): Unit = Try {
    event match {
      case start: SparkListenerSQLExecutionStart =>
        val shape = ApexAqeListener.extract(start.sparkPlanInfo)
        if (shape.nonEmpty) setSnapshot(start.executionId, shape) // ignore the v4.0 EMPTY placeholder Start

      case up: SparkListenerSQLAdaptiveExecutionUpdate =>
        val cur = ApexAqeListener.extract(up.sparkPlanInfo)
        snapshots.get(up.executionId) match {
          case Some(prev) =>
            ApexAqeListener.diff(prev, cur).foreach {
              // A skew_split whose metric ids are known is PARKED until Spark posts
              // numSkewedPartitions (see class doc); everything else emits at once.
              case t if t.kind == PlanTransition.SkewSplit && t.skewAccumIds.nonEmpty =>
                pendingSkew.update(up.executionId,
                  pendingSkew.getOrElse(up.executionId, Nil) :+
                    ApexAqeListener.PendingSkew(t.skewAccumIds, prev.skewAccumIds, t.readCount, t.before, t.after))
                flushPending(up.executionId)
              case t =>
                emit(up.executionId, t.kind, t.detail, t.before, t.after, t.confidence)
            }
            setSnapshot(up.executionId, cur) // advance baseline to latest
          case None =>
            setSnapshot(up.executionId, cur) // no baseline yet → establish one, emit nothing
        }

      case upd: SparkListenerDriverAccumUpdates =>
        // numSkewedPartitions lands here, when the skewed read executes — after the
        // plan update that introduced it.
        val vals = accumValues.getOrElseUpdate(upd.executionId, mutable.Map.empty)
        upd.accumUpdates.foreach { case (id, v) => vals.update(id, v) }
        flushPending(upd.executionId)

      case end: SparkListenerSQLExecutionEnd =>
        // Never lose a transition: if the skew metric never arrived (aborted query),
        // flush with the read count — the old, undercounting descriptor.
        pendingSkew.remove(end.executionId).toList.flatten.foreach { p =>
          emit(end.executionId, PlanTransition.SkewSplit,
            s"AQEShuffleRead skewed x${p.readCount}", p.before, p.after, PlanTransition.High)
        }
        snapshots.remove(end.executionId)
        nextSeq.remove(end.executionId)
        accumValues.remove(end.executionId)

      case _ => ()
    }
  }.recover { case t => logger.warn(s"apex: AQE onOtherEvent failed: ${t.getMessage}") }

  private def emit(execId: Long, kind: String, detail: String, before: String, after: String, confidence: String): Unit = {
    val seq = nextSeq.getOrElse(execId, 0)
    nextSeq.update(execId, seq + 1)
    sink.emitPlanTransition(PlanTransition(
      job_id = resolvedJobId(), execution_id = execId, update_seq = seq,
      transition_type = kind, detail = detail, before = before, after = after,
      confidence = confidence, ts = System.currentTimeMillis()))
  }

  /** Emit parked skew_splits whose partition counts Spark has now reported. */
  private def flushPending(execId: Long): Unit = {
    val vals = accumValues.getOrElse(execId, mutable.Map.empty)
    val (ready, waiting) = pendingSkew.getOrElse(execId, Nil).partition(p => p.accumIds.forall(vals.contains))
    if (ready.nonEmpty) pendingSkew.update(execId, waiting)
    ready.foreach { p =>
      val split  = p.accumIds.flatMap(vals.get).sum      // hot partitions split by THIS re-plan
      val before = p.prevAccumIds.flatMap(vals.get).sum  // hot partitions already split before it
      emit(execId, PlanTransition.SkewSplit,
        s"AQEShuffleRead skewed x$split", s"$before skewed", s"${before + split} skewed", PlanTransition.High)
    }
  }

  private def setSnapshot(execId: Long, shape: ApexAqeListener.PlanShape): Unit = {
    snapshots.update(execId, shape)
    while (snapshots.size > MaxLiveExecutions) {
      val oldest = snapshots.head._1
      snapshots.remove(oldest)
      nextSeq.remove(oldest)
      pendingSkew.remove(oldest)
      accumValues.remove(oldest)
    }
  }
}

object ApexAqeListener {

  private val JoinNames = Set("SortMergeJoin", "ShuffledHashJoin", "BroadcastHashJoin", "BroadcastNestedLoopJoin")
  private val AqeReadName = "AQEShuffleRead"
  // Spark's display name for the driver metric that counts hot partitions split
  // (exact match — must NOT catch "number of skewed partition splits"). Identical
  // on 3.5 / 4.0 / 4.1 (AQEShuffleReadExec.metrics).
  private val SkewedPartitionsMetric = "number of skewed partitions"

  /** Structural summary of a plan snapshot — node names + AQE-read descriptors only. */
  final case class PlanShape(joins: List[String], reads: List[String], skewAccumIds: Set[Long], signature: String) {
    def nonEmpty: Boolean = signature.nonEmpty
  }

  private final case class Trans(kind: String, detail: String, before: String, after: String, confidence: String,
                                 skewAccumIds: Set[Long] = Set.empty, readCount: Int = 0)

  /** A skew_split parked until Spark posts numSkewedPartitions for its reads. */
  private final case class PendingSkew(accumIds: Set[Long], prevAccumIds: Set[Long],
                                       readCount: Int, before: String, after: String)

  /** Walk a SparkPlanInfo tree collecting join node names + AQEShuffleRead descriptors. */
  private[apex] def extract(info: SparkPlanInfo): PlanShape = {
    val joins = mutable.ArrayBuffer.empty[String]
    val reads = mutable.ArrayBuffer.empty[String]
    val skewIds = mutable.Set.empty[Long]
    val sig   = new StringBuilder
    def walk(n: SparkPlanInfo): Unit = {
      val name = n.nodeName
      sig.append(name)
      if (JoinNames.contains(name)) joins += name
      if (name == AqeReadName) {
        val d = descriptorOf(n.simpleString)
        reads += d
        if (d.contains("skewed"))
          skewIds ++= n.metrics.filter(_.name == SkewedPartitionsMetric).map(_.accumulatorId)
        sig.append('[').append(d).append(']')
      }
      sig.append('(')
      n.children.foreach(walk)
      sig.append(')')
    }
    walk(info)
    PlanShape(joins.toList, reads.toList, skewIds.toSet, sig.toString)
  }

  /** Classify an AQEShuffleRead from its simpleString descriptor (verified strings). */
  private def descriptorOf(simpleString: String): String = {
    val s = simpleString.toLowerCase
    val c = s.contains("coalesced"); val k = s.contains("skewed"); val l = s.contains("local")
    if (c && k) "coalesced and skewed" else if (c) "coalesced" else if (k) "skewed" else if (l) "local" else ""
  }

  /** Consecutive-snapshot diff → real transitions only (empty ⇒ no-op re-plan, dropped). */
  private def diff(prev: PlanShape, cur: PlanShape): Seq[Trans] = {
    val out = mutable.ArrayBuffer.empty[Trans]

    // Join-strategy switches: same tree position changed join type (HIGH — structural).
    val n = math.min(prev.joins.size, cur.joins.size)
    var i = 0
    while (i < n) {
      if (prev.joins(i) != cur.joins(i))
        out += Trans(PlanTransition.JoinSwitch, s"${prev.joins(i)}->${cur.joins(i)}",
          prev.joins(i), cur.joins(i), PlanTransition.High)
      i += 1
    }

    // New AQEShuffleRead descriptors → skew split / coalesce / local read (HIGH — structural).
    def count(reads: Seq[String], key: String): Int = reads.count(_.contains(key))
    Seq(("skewed", PlanTransition.SkewSplit), ("coalesced", PlanTransition.Coalesce), ("local", PlanTransition.LocalRead))
      .foreach { case (key, kind) =>
        val added = count(cur.reads, key) - count(prev.reads, key)
        if (added > 0) {
          // For skew: the accumulator ids of the reads this re-plan made skewed, so the
          // listener can report the true PARTITION count once Spark posts it. (A read
          // node persists across snapshots with a stable id → set difference = new.)
          val newIds = if (kind == PlanTransition.SkewSplit) cur.skewAccumIds -- prev.skewAccumIds else Set.empty[Long]
          out += Trans(kind, s"AQEShuffleRead $key x$added",
            s"${count(prev.reads, key)} $key", s"${count(cur.reads, key)} $key", PlanTransition.High,
            skewAccumIds = newIds, readCount = added)
        }
      }

    // No specific structural signal → treat as a no-op re-plan and drop (avoids noise
    // from benign AQEShuffleRead insertion). `other` is reserved for future use.
    out.toList
  }
}
