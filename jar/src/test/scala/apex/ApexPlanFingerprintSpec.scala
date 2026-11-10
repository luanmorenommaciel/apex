package apex

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.catalyst.analysis.UnresolvedAttribute
import org.apache.spark.sql.catalyst.expressions.{AttributeReference, GreaterThan, Literal}
import org.apache.spark.sql.catalyst.plans.logical.{Filter, LocalRelation, LogicalPlan, Project}
import org.apache.spark.sql.types.IntegerType
import org.scalatest.funsuite.AnyFunSuite

import java.security.MessageDigest

case class FpProbeRow(a: Int, b: String)

/**
 * T7 proof: the logical-plan fingerprint is stable across literal changes and AQE,
 * and distinct for structurally-different queries. (The LIVE per-stage attachment is
 * proved end-to-end in DriverActivationSpec / AqeTransitionSpec.)
 */
class ApexPlanFingerprintSpec extends AnyFunSuite {

  private def withSpark[T](f: SparkSession => T): T = {
    val spark = SparkSession.builder()
      .master("local[2]")
      .appName("apex-fp-test")
      .config("spark.sql.adaptive.enabled", "true") // AQE ON — fingerprint must survive it
      .config("spark.ui.enabled", "false")
      .config("spark.sql.shuffle.partitions", "4")
      .getOrCreate()
    try f(spark) finally spark.stop()
  }

  private def sha256(s: String): String =
    MessageDigest.getInstance("SHA-256").digest(s.getBytes("UTF-8")).map("%02x".format(_)).mkString

  test("same query, different literals, AQE on -> identical 64-hex fingerprint") {
    withSpark { spark =>
      spark.range(0, 1000)
        .selectExpr("id", "id % 10 as amount", "id % 3 as segment")
        .createOrReplaceTempView("t")

      def fp(sql: String): String =
        ApexPlanFingerprint.fingerprint(spark.sql(sql).queryExecution.optimizedPlan)

      val fp1 = fp("select segment, count(*) c from t where id > 100 group by segment")
      val fp2 = fp("select segment, count(*) c from t where id > 900 group by segment")
      val fp3 = fp("select segment, sum(amount) s from t group by segment")

      assert(fp1.matches("[0-9a-f]{64}"), s"not 64 hex chars: $fp1")
      assert(fp1 == fp2, s"different literals must hash identically:\n  $fp1\n  $fp2")
      assert(fp1 != fp3, s"structurally different query must differ, both=$fp1")

      def rawFp(sql: String): String =
        sha256(spark.sql(sql).queryExecution.optimizedPlan.canonicalized.toString)
      val raw1 = rawFp("select segment, count(*) c from t where id > 100 group by segment")
      val raw2 = rawFp("select segment, count(*) c from t where id > 900 group by segment")

      info(s"normalized  fp1 == fp2 : ${fp1 == fp2}   fp=$fp1")
      info(s"raw-canon   raw1 == raw2: ${raw1 == raw2}  (raw1=${raw1.take(16)}… raw2=${raw2.take(16)}…)")
      assert(raw1 != raw2,
        "expected raw canonicalized to DIFFER on literals — justifies the normalization pass")
    }
  }

  // ── Spark 4.1 canonicalization fallback (T-20261019-jar-fingerprint-unresolved-spark41) ──
  //
  // Reproduced 2026-10-19 with the dev lane on apex_41: Delta's "Cache Delta Table
  // State" executions (SerializeFromObject / MapPartitions / DeserializeToObject)
  // carry UnresolvedAttributes that `canonicalized` trips over in 4.1
  // (allAttributes -> AttributeSeq -> qualifier -> UnresolvedException), and every
  // job lost the fingerprint of one to three stages. The plan shape below forces
  // the same path on any cell: a Project over an UnresolvedAttribute.

  // The unresolved attribute must sit in a CHILD's output: `allAttributes` is built
  // from children.flatMap(_.output), which is where 4.1 calls `qualifier`.
  private def unresolvedPlan(name: String): LogicalPlan = {
    val x = AttributeReference("x", IntegerType)()
    val relation = LocalRelation(x, AttributeReference("y", IntegerType)())
    Project(Seq(x), Project(Seq(UnresolvedAttribute(name)), relation))
  }

  test("a plan whose canonicalization throws still yields a stable 64-hex fingerprint") {
    val plan = unresolvedPlan("x")
    val fp1 = ApexPlanFingerprint.fingerprint(plan)
    val fp2 = ApexPlanFingerprint.fingerprint(unresolvedPlan("x"))
    val other = ApexPlanFingerprint.fingerprint(unresolvedPlan("y"))
    info(s"canonicalization fails on this cell: ${ApexPlanFingerprint.canonicalizationFails(plan)}")
    assert(fp1.matches("[0-9a-f]{64}"), s"not 64 hex chars: $fp1")
    assert(fp1 == fp2, "same unresolved shape must hash identically across calls")
    assert(fp1 != other, "a different unresolved shape must hash differently")
    assert(ApexPlanFingerprint.redactedPlan(plan).nonEmpty)
  }

  test("the fallback still normalizes literals and scrubs per-run ExprIds and lambda identities") {
    val x = AttributeReference("x", IntegerType)()
    val relation = LocalRelation(x)
    def plan(lit: Int): LogicalPlan =
      Project(Seq(x), Project(Seq(UnresolvedAttribute("x")), Filter(GreaterThan(x, Literal(lit)), relation)))
    assert(ApexPlanFingerprint.fingerprint(plan(100)) == ApexPlanFingerprint.fingerprint(plan(900)),
      "different literals must hash identically through the fallback too")
    val scrubbed = ApexPlanFingerprint.scrub(
      "MapPartitions org.apache.spark.sql.delta.Snapshot$$Lambda$5638/0x00000078025a59a8@1e546002, obj#858: X, add#780L")
    assert(scrubbed == "MapPartitions org.apache.spark.sql.delta.Snapshot$$Lambda, obj#: X, add#", scrubbed)
    // JDK 21 drops the lambda counter and the CI matrix runs there.
    val jdk21 = ApexPlanFingerprint.scrubIdentities(
      "MapElements apex.ApexPlanFingerprintSpec$$Lambda/0x00007f3a1c0b2c40@6f3a1c2e, obj#12: X")
    assert(jdk21 == "MapElements apex.ApexPlanFingerprintSpec$$Lambda, obj#12: X", jdk21)
  }

  test("typed Dataset plans (object operators) get a fingerprint on every cell") {
    withSpark { spark =>
      import spark.implicits._
      val ds = spark.range(0, 100).map(i => FpProbeRow(i.toInt, s"v$i")).filter(_.a % 2 == 0)
      val plan = ds.queryExecution.optimizedPlan
      val fp = ApexPlanFingerprint.fingerprint(plan)
      val again = ApexPlanFingerprint.fingerprint(
        spark.range(0, 100).map(i => FpProbeRow(i.toInt, s"v$i")).filter(_.a % 2 == 0).queryExecution.optimizedPlan)
      info(s"object plan canonicalization fails on this cell: ${ApexPlanFingerprint.canonicalizationFails(plan)}")
      assert(fp.matches("[0-9a-f]{64}"), s"not 64 hex chars: $fp")
      assert(fp == again, "the same typed pipeline must hash identically across two executions")
    }
  }
}
