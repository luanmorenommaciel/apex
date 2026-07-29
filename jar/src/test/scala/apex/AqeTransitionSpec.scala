package apex

import org.apache.spark.sql.SparkSession
import org.scalatest.funsuite.AnyFunSuite

/**
 * T-AQE proof: with AQE ON, a skewed join makes Spark re-plan at runtime, and the
 * ApexAqeListener captures that decision as an `apex.plan_transition`. Also proves
 * (a) — stage rows now carry a correct non-empty fingerprint under AQE (the
 * execution_id-buffered ordering fix).
 */
class AqeTransitionSpec extends AnyFunSuite {

  private val ValidTypes = Set(
    PlanTransition.JoinSwitch, PlanTransition.SkewSplit,
    PlanTransition.Coalesce, PlanTransition.LocalRead, PlanTransition.Other)

  private def resetSessions(): Unit = {
    ApexSinks.reset()
    CapturingSink.latest = null
    SparkSession.clearActiveSession()
    SparkSession.clearDefaultSession()
  }

  test("T-AQE-count: two hot partitions in ONE shuffle read report 'skewed x2', not x1") {
    resetSessions()
    val spark = SparkSession.builder()
      .master("local[2]")
      .appName("apex-aqe-count")
      .config("spark.plugins", "apex.ApexPlugin")
      .config("spark.apex.sink.class", "apex.CapturingSink")
      .config("spark.apex.aqe.enabled", "true")
      .config("spark.ui.enabled", "false")
      .config("spark.sql.adaptive.enabled", "true")
      .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
      .config("spark.sql.adaptive.skewJoin.enabled", "true")
      .config("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "16")
      .config("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "2")
      .config("spark.sql.adaptive.advisoryPartitionSizeInBytes", "64")
      .config("spark.sql.autoBroadcastJoinThreshold", "-1") // force SMJ so the skew path is used
      .config("spark.sql.shuffle.partitions", "16")
      .getOrCreate()

    try {
      // Keys 1 and 2 each dominate (~45%) → TWO hot partitions in the SAME
      // AQEShuffleRead (verified: k=1→p13, k=2→p8 under hash mod 16). Counting
      // read nodes says "skewed x1"; the truth is 2 skewed partitions (Spark's
      // numSkewedPartitions driver metric). The sha2 payload makes every row
      // incompressible — skew detection works on (compressed) shuffle BYTES,
      // and a constant key compresses to nothing, which would make the "hot"
      // partitions look small.
      val a = spark.range(0, 100000).selectExpr(
        "CASE WHEN id < 45000 THEN 1 WHEN id < 90000 THEN 2 ELSE id END as k",
        "id as v1", "sha2(cast(id as string), 256) as payload")
      val b = spark.range(0, 100000).selectExpr("id as k", "id as v2")
      // sum(length(payload)) forces the payload through the shuffle — a bare
      // count() lets the optimizer prune it and the rows compress to nothing.
      a.join(b, "k").selectExpr("count(1) as c", "sum(length(payload)) as s").collect()
    } finally {
      spark.stop()
    }

    val transitions = Option(CapturingSink.latest).map(_.transitions.toList).getOrElse(Nil)
    resetSessions()

    transitions.foreach(t => info(s"  seq=${t.update_seq} type=${t.transition_type} detail='${t.detail}' " +
      s"before='${t.before}' after='${t.after}' conf=${t.confidence} exec=${t.execution_id}"))
    val skew = transitions.filter(_.transition_type == PlanTransition.SkewSplit)
    assert(skew.nonEmpty, "expected a skew_split transition from the two-hot-partition join")
    val counts = skew.flatMap(t => "x(\\d+)".r.findFirstMatchIn(t.detail).map(_.group(1).toInt))
    assert(counts.nonEmpty && counts.max >= 2,
      s"descriptor must count skewed PARTITIONS (2 hot), not reads — got: ${skew.map(_.detail).mkString(", ")}")
    // before/after must agree with the partition count, not the read count.
    assert(skew.exists(t => t.after.matches("([2-9]|\\d{2,}) skewed")),
      s"'after' must report the partition total, got: ${skew.map(_.after).mkString(", ")}")
  }

  test("T-AQE: a skewed join with AQE ON emits a plan_transition; stages carry a 64-hex fingerprint") {
    resetSessions()
    val spark = SparkSession.builder()
      .master("local[2]")
      .appName("apex-aqe")
      .config("spark.plugins", "apex.ApexPlugin")
      .config("spark.apex.sink.class", "apex.CapturingSink")
      .config("spark.apex.aqe.enabled", "true")
      .config("spark.ui.enabled", "false")
      .config("spark.sql.adaptive.enabled", "true")
      .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
      .config("spark.sql.adaptive.skewJoin.enabled", "true")
      .config("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "16")
      .config("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "2")
      .config("spark.sql.adaptive.advisoryPartitionSizeInBytes", "64")
      .config("spark.sql.autoBroadcastJoinThreshold", "-1") // force SMJ so the skew path is used
      .config("spark.sql.shuffle.partitions", "16")
      .getOrCreate()

    try {
      import spark.implicits._
      // Key 1 dominates the left side (~90%) → one huge shuffle partition → AQE skew-splits it.
      val a = spark.range(0, 100000).selectExpr("CASE WHEN id < 90000 THEN 1 ELSE id END as k", "id as v1")
      val b = spark.range(0, 100000).selectExpr("id as k", "id as v2")
      a.join(b, "k").count()
    } finally {
      spark.stop() // drains the bus → all stage events + transitions delivered
    }

    val sink        = CapturingSink.latest
    val events      = Option(sink).map(_.events.toList).getOrElse(Nil)
    val transitions = Option(sink).map(_.transitions.toList).getOrElse(Nil)
    resetSessions()

    // (b) a real AQE decision was captured.
    info(s"captured ${transitions.size} plan_transition(s):")
    transitions.foreach(t => info(s"  seq=${t.update_seq} type=${t.transition_type} detail='${t.detail}' " +
      s"before='${t.before}' after='${t.after}' conf=${t.confidence} exec=${t.execution_id}"))
    assert(transitions.nonEmpty, "expected at least one AQE plan_transition from the skewed join")
    assert(transitions.forall(t => ValidTypes.contains(t.transition_type)), s"invalid transition_type in $transitions")
    assert(transitions.forall(t => t.job_id.nonEmpty && t.execution_id >= 0), "transition must carry job_id + execution_id")
    assert(transitions.exists(t => t.confidence == PlanTransition.High), "expected a HIGH-confidence structural transition")
    // update_seq is monotonic per execution_id
    transitions.groupBy(_.execution_id).foreach { case (execId, ts) =>
      val seqs = ts.map(_.update_seq)
      assert(seqs == seqs.sorted && seqs.distinct == seqs, s"update_seq not monotonic for exec $execId: $seqs")
    }
    // never ship raw plan text / literals
    assert(transitions.forall(t => !t.detail.contains("\n") && !t.before.contains("Filter")),
      "detail/before/after must be structured descriptors, not raw plan text")

    // (a) stage rows carry a correct non-empty 64-hex fingerprint even under AQE.
    assert(events.nonEmpty, "expected stage events")
    events.foreach(e => info(s"  stage=${e.stage_id} fp=${Option(e.plan_fingerprint).map(v => if (v.isEmpty) "<empty>" else v.take(16) + "…").getOrElse("<null>")}"))
    val fps = events.flatMap(e => Option(e.plan_fingerprint)).filter(_.nonEmpty).distinct
    assert(fps.nonEmpty && fps.forall(_.matches("[0-9a-f]{64}")),
      s"expected non-empty 64-hex fingerprints on stage rows, got $fps")
  }
}
