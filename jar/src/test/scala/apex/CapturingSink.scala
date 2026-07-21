package apex

import scala.collection.mutable.ArrayBuffer

/**
 * Test double: records emitted stage events + plan transitions instead of shipping
 * OTLP. Selected via `spark.apex.sink.class=apex.CapturingSink`, so it exercises the
 * REAL activation path (plugin / extraListeners → ApexSinks → here). No-arg ctor
 * (ApexSinks builds it reflectively); publishes itself to `CapturingSink.latest`.
 */
class CapturingSink extends ApexSink {
  val events      = ArrayBuffer.empty[ApexStageEvent]
  val transitions = ArrayBuffer.empty[PlanTransition]

  CapturingSink.latest = this

  override def emit(ev: ApexStageEvent): Unit = synchronized { events += ev }
  override def emitPlanTransition(t: PlanTransition): Unit = synchronized { transitions += t }
  override def close(): Unit = ()
}

object CapturingSink {
  @volatile var latest: CapturingSink = _
}
