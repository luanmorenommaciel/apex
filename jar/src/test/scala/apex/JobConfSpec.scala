package apex

import org.apache.spark.sql.SparkSession
import org.scalatest.funsuite.AnyFunSuite

/**
 * Contract v0.4 proposal — the resolved SparkConf allowlist, once per application:
 *   - emitted EXACTLY ONCE per application, keyed by job_id (two queries → one row)
 *   - `spark.sql.*` defaults RESOLVED (an unset adaptive.enabled is captured as its
 *     effective default "true" — the value the NO-OP gate in verify/ needs)
 *   - explicit values captured verbatim
 *   - SECURITY: credentials set in the conf NEVER leave the JVM (allowlist only)
 *   - `spark.apex.conf.enabled=false` disables capture
 */
class JobConfSpec extends AnyFunSuite {

  private def resetSessions(): Unit = {
    ApexSinks.reset()
    CapturingSink.latest = null
    SparkSession.clearActiveSession()
    SparkSession.clearDefaultSession()
  }

  /** Decoy credentials a real cluster conf carries — none may appear in the event. */
  private val DecoySecrets = Map(
    "spark.hadoop.fs.s3a.secret.key"            -> "AKIA-FAKE-SECRET-KEY",
    "spark.hadoop.fs.s3a.access.key"            -> "AKIAFAKEACCESSKEY",
    "spark.jdbc.password"                       -> "hunter2",
    "spark.kubernetes.authenticate.submission.oauthToken" -> "tok-abc123"
  )

  /** Run TWO queries under the plugin and return every job_conf event captured. */
  private def runCapturing(extra: SparkSession.Builder => SparkSession.Builder): Seq[JobConfEvent] = {
    resetSessions()
    val base = SparkSession.builder()
      .master("local[2]")
      .appName("apex-job-conf")
      .config("spark.apex.sink.class", "apex.CapturingSink")  // capture instead of OTLP
      .config("spark.ui.enabled", "false")
      .config("spark.sql.shuffle.partitions", "7")            // explicit value, must be captured
      .config("spark.driver.memory", "2g")                    // explicit value, must be captured
    val withDecoys = DecoySecrets.foldLeft(base) { case (b, (k, v)) => b.config(k, v) }
    val spark = extra(withDecoys).getOrCreate()
    try {
      spark.range(0, 1000).selectExpr("id", "id % 10 as k").groupBy("k").count().collect()
      spark.range(0, 100).selectExpr("id", "id % 3 as k").groupBy("k").count().collect()
    } finally {
      spark.stop() // drains the listener bus
    }
    val res = Option(CapturingSink.latest).map(_.jobConfs.toList).getOrElse(Nil)
    resetSessions()
    res
  }

  test("emits exactly one resolved job_conf per application; secrets never leave the JVM") {
    val confs = runCapturing(_.config("spark.plugins", "apex.ApexPlugin"))

    assert(confs.size == 1, s"expected exactly one job_conf per application (two queries ran), got ${confs.size}")
    val ev = confs.head
    assert(ev.job_id.nonEmpty && ev.app_id.nonEmpty, "job_id/app_id must be populated")
    assert(ev.app_name == "apex-job-conf")
    assert(ev.ts > 0)

    // Explicit values captured verbatim.
    assert(ev.conf.get("spark.sql.shuffle.partitions").contains("7"))
    assert(ev.conf.get("spark.driver.memory").contains("2g"))

    // RESOLVED defaults: adaptive.enabled + skewJoin.enabled are unset here, but their
    // effective defaults (true in 3.5/4.x) must be captured — this is what lets verify/
    // answer "was skewJoin.enabled true on this run?" with no History Server.
    assert(ev.conf.get("spark.sql.adaptive.enabled").contains("true"),
      s"unset adaptive.enabled must resolve to its default; got ${ev.conf.get("spark.sql.adaptive.enabled")}")
    assert(ev.conf.get("spark.sql.adaptive.skewJoin.enabled").contains("true"))

    // SECURITY: every emitted key is allowlisted; no decoy key or value escaped.
    val leaked = ev.conf.keySet -- ApexJobConfAllowlist.Keys.toSet
    assert(leaked.isEmpty, s"non-allowlisted keys emitted: $leaked")
    DecoySecrets.foreach { case (k, v) =>
      assert(!ev.conf.contains(k), s"credential key leaked: $k")
      assert(!ev.conf.values.exists(_.contains(v)), s"credential VALUE leaked under another key: $v")
    }
  }

  test("allowlist covers the contract v0.4 required keys") {
    val required = Seq(
      "spark.sql.shuffle.partitions", "spark.executor.instances", "spark.executor.cores",
      "spark.executor.memory", "spark.driver.cores", "spark.driver.memory",
      "spark.sql.adaptive.enabled", "spark.sql.adaptive.skewJoin.enabled",
      "spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes",
      "spark.sql.adaptive.skewJoin.skewedPartitionFactor",
      "spark.sql.adaptive.coalescePartitions.enabled",
      "spark.sql.adaptive.advisoryPartitionSizeInBytes",
      "spark.sql.autoBroadcastJoinThreshold")
    val missing = required.toSet -- ApexJobConfAllowlist.Keys.toSet
    assert(missing.isEmpty, s"allowlist is missing required keys: $missing")
  }

  test("spark.apex.conf.enabled=false disables capture") {
    val confs = runCapturing(_
      .config("spark.plugins", "apex.ApexPlugin")
      .config("spark.apex.conf.enabled", "false"))
    assert(confs.isEmpty, s"expected no job_conf when disabled, got ${confs.size}")
  }

  test("extraListeners path captures job_conf standalone") {
    val confs = runCapturing(_.config("spark.extraListeners", "apex.ApexConfListener"))
    assert(confs.size == 1, s"expected one job_conf via extraListeners, got ${confs.size}")
    assert(confs.head.conf.get("spark.sql.shuffle.partitions").contains("7"))
  }
}
