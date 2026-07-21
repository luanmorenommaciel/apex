package apex

import org.apache.spark.sql.SparkSession
import org.scalatest.funsuite.AnyFunSuite

import java.security.MessageDigest

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
}
