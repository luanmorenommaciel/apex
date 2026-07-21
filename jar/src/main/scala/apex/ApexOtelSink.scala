package apex

import io.opentelemetry.api.trace.Tracer
import io.opentelemetry.exporter.otlp.http.trace.OtlpHttpSpanExporter
import io.opentelemetry.sdk.OpenTelemetrySdk
import io.opentelemetry.sdk.resources.Resource
import io.opentelemetry.sdk.trace.SdkTracerProvider
import io.opentelemetry.sdk.trace.export.BatchSpanProcessor
import org.slf4j.LoggerFactory

import java.time.Duration
import java.util.concurrent.TimeUnit
import scala.util.Try

/**
 * The one egress point. Every completed stage becomes an `apex.stage` OTLP span,
 * shipped through a BOUNDED [[BatchSpanProcessor]] so a slow or dead collector can
 * NEVER stall the Spark driver:
 *
 *   - BatchSpanProcessor exports on its OWN thread → `emit` returns immediately.
 *   - The queue is bounded (2048) → when full it DROPS, it never blocks or grows
 *     the driver heap. (SimpleSpanProcessor, by contrast, exports synchronously on
 *     the caller thread and would stall the driver — never use it here.)
 *   - Every SDK call is wrapped in `Try` and logs-and-drops on failure, so a
 *     listener callback can't throw and get evicted from Spark's listener bus.
 *
 * The exporter endpoint MUST carry the full `/v1/traces` path — the OTLP/HTTP SDK
 * stores the string as-is and does not append it.
 */
class ApexOtelSink(endpoint: String, service: String) extends ApexSink {
  private val logger = LoggerFactory.getLogger(getClass)

  // Full path is mandatory; tolerate a base with or without the suffix / trailing slash.
  private val tracesEndpoint: String = {
    val base = endpoint.stripSuffix("/")
    if (base.endsWith("/v1/traces")) base else s"$base/v1/traces"
  }

  private val exporter =
    OtlpHttpSpanExporter.builder()
      .setEndpoint(tracesEndpoint)
      .setTimeout(Duration.ofSeconds(5))
      .build()

  private val processor =
    BatchSpanProcessor.builder(exporter)
      .setMaxQueueSize(2048)                       // BOUNDED → drops when full, never blocks the driver
      .setMaxExportBatchSize(512)
      .setScheduleDelay(Duration.ofSeconds(1))
      .setExporterTimeout(Duration.ofSeconds(5))
      .build()

  private val sdk =
    OpenTelemetrySdk.builder()
      .setTracerProvider(
        SdkTracerProvider.builder()
          .setResource(Resource.getDefault.merge(
            Resource.builder().put("service.name", service).build()))
          .addSpanProcessor(processor)
          .build())
      .build()

  private val tracer: Tracer = sdk.getTracer("apex")

  /** Emit one completed stage as an `apex.stage` span. Non-blocking; drops on any failure. */
  def emit(ev: ApexStageEvent): Unit = Try {
    val span = tracer.spanBuilder("apex.stage").startSpan()
    try {
      span
        .setAttribute(ApexAttributes.JobId, ev.job_id)
        .setAttribute(ApexAttributes.AppId, ev.app_id)
        .setAttribute(ApexAttributes.AppName, ev.app_name)
        .setAttribute(ApexAttributes.StageId, Long.box(ev.stage_id.toLong))
        .setAttribute(ApexAttributes.StageAttempt, Long.box(ev.stage_attempt.toLong))
        .setAttribute(ApexAttributes.Ts, Long.box(ev.ts))
        .setAttribute(ApexAttributes.ShuffleReadBytes, Long.box(ev.shuffle_read_bytes))
        .setAttribute(ApexAttributes.ShuffleWriteBytes, Long.box(ev.shuffle_write_bytes))
        .setAttribute(ApexAttributes.SpillDiskBytes, Long.box(ev.spill_disk_bytes))
        .setAttribute(ApexAttributes.SpillMemBytes, Long.box(ev.spill_mem_bytes))
        .setAttribute(ApexAttributes.GcTimeMs, Long.box(ev.gc_time_ms))
        .setAttribute(ApexAttributes.InputBytes, Long.box(ev.input_bytes))
        .setAttribute(ApexAttributes.OutputBytes, Long.box(ev.output_bytes))
        .setAttribute(ApexAttributes.PeakExecutionMemBytes, Long.box(ev.peak_execution_mem_bytes))
        .setAttribute(ApexAttributes.TaskCount, Long.box(ev.task_count.toLong))
        .setAttribute(ApexAttributes.TaskDurationP50Ms, Long.box(ev.task_duration_p50_ms))
        .setAttribute(ApexAttributes.TaskDurationP99Ms, Long.box(ev.task_duration_p99_ms))
        .setAttribute(ApexAttributes.PlanFingerprint, ev.plan_fingerprint)
        .setAttribute(ApexAttributes.PlanJson, ev.plan_json)
    } finally span.end()
  }.recover { case t => logger.warn(s"apex: dropped stage ${ev.stage_id}: ${t.getMessage}") }

  /** Emit one AQE re-plan as an `apex.plan_transition` span. Non-blocking; drops on failure. */
  def emitPlanTransition(t: PlanTransition): Unit = Try {
    val span = tracer.spanBuilder("apex.plan_transition").startSpan()
    try {
      span
        .setAttribute(ApexAttributes.JobId, t.job_id)
        .setAttribute(ApexAttributes.ExecutionId, Long.box(t.execution_id))
        .setAttribute(ApexAttributes.UpdateSeq, Long.box(t.update_seq.toLong))
        .setAttribute(ApexAttributes.TransitionType, t.transition_type)
        .setAttribute(ApexAttributes.Detail, t.detail)
        .setAttribute(ApexAttributes.Before, t.before)
        .setAttribute(ApexAttributes.After, t.after)
        .setAttribute(ApexAttributes.Confidence, t.confidence)
        .setAttribute(ApexAttributes.Ts, Long.box(t.ts))
    } finally span.end()
  }.recover { case th => logger.warn(s"apex: dropped plan_transition exec=${t.execution_id} seq=${t.update_seq}: ${th.getMessage}") }

  /** Flush and close on driver shutdown, bounded so shutdown can't hang. */
  def close(): Unit = {
    Try(sdk.getSdkTracerProvider.forceFlush().join(5, TimeUnit.SECONDS))
    Try(sdk.close())
  }
}
