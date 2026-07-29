package apex

import org.apache.spark.SparkContext
import org.apache.spark.sql.SparkSession

import scala.util.Try

/**
 * The resolved SparkConf subset for ONE application run (contract v0.4 proposal
 * § "job conf") — the signal that lets `memory/` recall "the config that worked"
 * and lets `verify/` run its NO-OP gate ("was skewJoin.enabled already true on
 * this run?") from ClickHouse alone, with no History Server.
 *
 * SECURITY — ALLOWLIST, never the whole conf. A SparkConf routinely carries
 * credentials (s3a secret keys, JDBC passwords, tokens); those must never reach
 * telemetry. Every key in [[ApexJobConfAllowlist.Keys]] is a pure performance
 * knob whose value is a number, a byte size, or a boolean. If a key's safety
 * cannot be argued, it is not on the list.
 *
 * Values are RESOLVED: `spark.sql.*` keys go through the session RuntimeConfig,
 * so an unset-but-defaulted flag (e.g. `spark.sql.adaptive.enabled`, default
 * true in 3.5/4.x) is captured with its effective value rather than omitted.
 */
final case class JobConfEvent(
  job_id: String,
  app_id: String,
  app_name: String,
  conf: Map[String, String], // allowlisted keys only, resolved values
  ts: Long
)

object ApexJobConfAllowlist {

  /**
   * ZEST's 6 tunables + the AQE flags the watchers reason about + the broadcast
   * threshold. ALL are performance knobs; NONE can carry a credential. This is
   * a security boundary: extend only with keys provably incapable of holding a
   * secret, and never replace it with a whole-conf dump or a prefix filter.
   */
  val Keys: List[String] = List(
    // ZEST tunables
    "spark.sql.shuffle.partitions",
    "spark.executor.instances",
    "spark.executor.cores",
    "spark.executor.memory",
    "spark.driver.cores",
    "spark.driver.memory",
    // AQE flags the watchers reason about
    "spark.sql.adaptive.enabled",
    "spark.sql.adaptive.skewJoin.enabled",
    "spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes",
    "spark.sql.adaptive.skewJoin.skewedPartitionFactor",
    "spark.sql.adaptive.coalescePartitions.enabled",
    "spark.sql.adaptive.advisoryPartitionSizeInBytes",
    // join strategy
    "spark.sql.autoBroadcastJoinThreshold"
  )

  /**
   * Resolve the allowlist against a live application: the session RuntimeConfig
   * first (it resolves SQLConf defaults, so an unset `spark.sql.*` key still
   * captures its effective value), then the raw SparkConf for executor/driver
   * keys that only exist there. A key that resolves nowhere is OMITTED — it was
   * never set anywhere, so it is not "the config that ran".
   */
  def resolve(sc: SparkContext): Map[String, String] = {
    val sess = SparkSession.getActiveSession.orElse(SparkSession.getDefaultSession)
    Keys.flatMap { k =>
      val v = sess.flatMap(s => Try(s.conf.get(k)).toOption).orElse(sc.getConf.getOption(k))
      v.map(k -> _)
    }.toMap
  }
}
