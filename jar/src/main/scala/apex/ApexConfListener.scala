package apex

import org.apache.spark.{SparkConf, SparkContext}
import org.apache.spark.scheduler.{SparkListener, SparkListenerJobStart}
import org.slf4j.LoggerFactory

import scala.util.Try

/**
 * Emits the resolved, ALLOWLISTED SparkConf subset ONCE per application as a
 * distinct `apex.job_conf` span (contract v0.4 proposal), keyed by `job_id`.
 *
 * Timing — first `onJobStart`, not `onApplicationStart`: at ApplicationStart no
 * SparkSession exists yet, so `spark.sql.*` defaults (e.g. adaptive.enabled=true)
 * could not be resolved. At first job start the session is up and every
 * allowlisted key resolves to its effective value. An application that never
 * runs a job emits no row — there is no run to tune.
 *
 * Registered by the plugin behind `spark.apex.conf.enabled` (default on); also
 * usable standalone via `spark.extraListeners=apex.ApexConfListener`. Rides the
 * same bounded sink + `Try`/recover as the other listeners: it can never block
 * the driver, and a failure logs-and-drops instead of getting the listener
 * evicted from the bus. Callbacks run on the single listener-bus thread, so the
 * emit-once flag needs no synchronization.
 */
class ApexConfListener(sink: ApexSink, conf: SparkConf) extends SparkListener {

  /** Plugin / extraListeners activation — shares the JVM-singleton sink. */
  def this(conf: SparkConf) = this(ApexSinks.instance(conf), conf)

  private val logger = LoggerFactory.getLogger(getClass)
  private var emitted = false

  override def onJobStart(e: SparkListenerJobStart): Unit = Try {
    if (!emitted) {
      emitted = true
      val sc    = SparkContext.getOrCreate()
      val appId = sc.applicationId
      sink.emitJobConf(JobConfEvent(
        job_id   = conf.getOption("spark.apex.job_id").getOrElse(appId),
        app_id   = appId,
        app_name = conf.get("spark.app.name", sc.appName),
        conf     = ApexJobConfAllowlist.resolve(sc),
        ts       = System.currentTimeMillis()))
    }
  }.recover { case t => logger.warn(s"apex: job_conf emission failed: ${t.getMessage}") }
}
