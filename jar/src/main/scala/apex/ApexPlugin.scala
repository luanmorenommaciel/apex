package apex

import org.apache.spark.SparkContext
import org.apache.spark.api.plugin.{DriverPlugin, ExecutorPlugin, PluginContext, SparkPlugin}

import java.util.{Collections, Map => JMap}

/**
 * Primary activation:  --conf spark.plugins=apex.ApexPlugin
 *
 * Driver-side only (no executor plugin). `DriverPlugin.init` hands us the live
 * SparkContext, giving a clean lifecycle: build the sink, register the stage
 * listener, and flush on `shutdown`.
 *
 * The stage listener also carries the plan-fingerprint attachment (buffered by
 * execution_id, flushed at SQL execution end) — no separate QueryExecutionListener
 * is needed, so activation is just `spark.plugins` (or the extraListeners fallback).
 * The AQE listener is registered behind `spark.apex.aqe.enabled` (default on).
 */
class ApexPlugin extends SparkPlugin {
  override def driverPlugin(): DriverPlugin = new ApexDriverPlugin
  override def executorPlugin(): ExecutorPlugin = null
}

class ApexDriverPlugin extends DriverPlugin {
  override def init(sc: SparkContext, ctx: PluginContext): JMap[String, String] = {
    val conf = sc.getConf
    ApexSinks.instance(conf) // build the singleton sink now; listeners share it

    // Both listeners take the SparkConf ctor and resolve app_id/job_id LAZILY at
    // event time — `sc.applicationId` is still null here at plugin-init time.
    sc.addSparkListener(new ApexStageListener(conf))
    if (conf.getBoolean("spark.apex.aqe.enabled", defaultValue = true))
      sc.addSparkListener(new ApexAqeListener(conf))
    Collections.emptyMap()
  }

  override def shutdown(): Unit = ApexSinks.reset() // forceFlush + close, then clear the singleton
}
