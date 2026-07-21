package apex

import org.apache.spark.{SparkConf, SparkContext}
import org.apache.spark.scheduler.{SparkListener, SparkListenerEvent}
import org.apache.spark.sql.execution.SparkPlanInfo
import org.apache.spark.sql.execution.ui.{SparkListenerSQLAdaptiveExecutionUpdate, SparkListenerSQLExecutionEnd, SparkListenerSQLExecutionStart}
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

  private val snapshots = mutable.LinkedHashMap.empty[Long, ApexAqeListener.PlanShape]
  private val nextSeq   = mutable.Map.empty[Long, Int]

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
            val transitions = ApexAqeListener.diff(prev, cur)
            transitions.foreach { t =>
              val seq = nextSeq.getOrElse(up.executionId, 0)
              nextSeq.update(up.executionId, seq + 1)
              sink.emitPlanTransition(PlanTransition(
                job_id = resolvedJobId(), execution_id = up.executionId, update_seq = seq,
                transition_type = t.kind, detail = t.detail, before = t.before, after = t.after,
                confidence = t.confidence, ts = System.currentTimeMillis()))
            }
            setSnapshot(up.executionId, cur) // advance baseline to latest
          case None =>
            setSnapshot(up.executionId, cur) // no baseline yet → establish one, emit nothing
        }

      case end: SparkListenerSQLExecutionEnd =>
        snapshots.remove(end.executionId)
        nextSeq.remove(end.executionId)

      case _ => ()
    }
  }.recover { case t => logger.warn(s"apex: AQE onOtherEvent failed: ${t.getMessage}") }

  private def setSnapshot(execId: Long, shape: ApexAqeListener.PlanShape): Unit = {
    snapshots.update(execId, shape)
    while (snapshots.size > MaxLiveExecutions) {
      val oldest = snapshots.head._1
      snapshots.remove(oldest)
      nextSeq.remove(oldest)
    }
  }
}

object ApexAqeListener {

  private val JoinNames = Set("SortMergeJoin", "ShuffledHashJoin", "BroadcastHashJoin", "BroadcastNestedLoopJoin")
  private val AqeReadName = "AQEShuffleRead"

  /** Structural summary of a plan snapshot — node names + AQE-read descriptors only. */
  final case class PlanShape(joins: List[String], reads: List[String], signature: String) {
    def nonEmpty: Boolean = signature.nonEmpty
  }

  private final case class Trans(kind: String, detail: String, before: String, after: String, confidence: String)

  /** Walk a SparkPlanInfo tree collecting join node names + AQEShuffleRead descriptors. */
  private[apex] def extract(info: SparkPlanInfo): PlanShape = {
    val joins = mutable.ArrayBuffer.empty[String]
    val reads = mutable.ArrayBuffer.empty[String]
    val sig   = new StringBuilder
    def walk(n: SparkPlanInfo): Unit = {
      val name = n.nodeName
      sig.append(name)
      if (JoinNames.contains(name)) joins += name
      if (name == AqeReadName) {
        val d = descriptorOf(n.simpleString)
        reads += d
        sig.append('[').append(d).append(']')
      }
      sig.append('(')
      n.children.foreach(walk)
      sig.append(')')
    }
    walk(info)
    PlanShape(joins.toList, reads.toList, sig.toString)
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
        if (added > 0)
          out += Trans(kind, s"AQEShuffleRead $key x$added",
            s"${count(prev.reads, key)} $key", s"${count(cur.reads, key)} $key", PlanTransition.High)
      }

    // No specific structural signal → treat as a no-op re-plan and drop (avoids noise
    // from benign AQEShuffleRead insertion). `other` is reserved for future use.
    out.toList
  }
}
