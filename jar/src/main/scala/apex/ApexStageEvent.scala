package apex

import io.opentelemetry.api.common.AttributeKey

/**
 * One completed Spark stage, as it crosses the jar → collector boundary.
 *
 * Field names are the CONTRACT (§ "The telemetry event") verbatim, snake_case —
 * they are the OTLP span attribute keys and the `apex.spark_events` columns, so
 * they must never be renamed here. A stage may ADD a field; never repurpose one.
 *
 * All byte/ms metrics are Long; ids and counts are Int; `ts` is epoch millis.
 * `plan_fingerprint` is the 64-hex-char SHA-256 of the normalized LOGICAL plan
 * (see [[ApexPlanListener]]) — an opaque value, never recomputed downstream.
 */
final case class ApexStageEvent(
  job_id: String,
  app_id: String,
  app_name: String,
  stage_id: Int,
  stage_attempt: Int,
  ts: Long,
  shuffle_read_bytes: Long,
  shuffle_write_bytes: Long,
  spill_disk_bytes: Long,
  spill_mem_bytes: Long,
  gc_time_ms: Long,
  executor_run_time_ms: Long,
  input_bytes: Long,
  output_bytes: Long,
  peak_execution_mem_bytes: Long,
  task_count: Int,
  task_duration_p50_ms: Long,
  task_duration_p99_ms: Long,
  task_duration_max_ms: Long,
  task_duration_sample_count: Int,
  successful_task_duration_p50_ms: Long,
  successful_task_duration_p99_ms: Long,
  successful_task_duration_max_ms: Long,
  successful_task_sample_count: Int,
  successful_task_shuffle_read_bytes_p50: Long,
  successful_task_shuffle_read_bytes_max: Long,
  successful_task_shuffle_read_bytes_sample_count: Int,
  task_attempt_count: Int,
  task_failed_attempt_count: Int,
  task_counted_failure_attempt_count: Int,
  task_killed_attempt_count: Int,
  task_speculative_attempt_count: Int,
  plan_fingerprint: String,
  plan_json: String
)

/**
 * Typed OTLP attribute keys — one per contract field, so [[ApexOtelSink]] sets
 * each value through a strongly-typed key rather than a bare string. The key
 * name equals the contract field name, keeping span attributes, DDL columns, and
 * the sample fixture in lockstep.
 */
object ApexAttributes {
  val JobId: AttributeKey[String]              = AttributeKey.stringKey("job_id")
  val AppId: AttributeKey[String]              = AttributeKey.stringKey("app_id")
  val AppName: AttributeKey[String]            = AttributeKey.stringKey("app_name")
  val StageId: AttributeKey[java.lang.Long]    = AttributeKey.longKey("stage_id")
  val StageAttempt: AttributeKey[java.lang.Long] = AttributeKey.longKey("stage_attempt")
  val Ts: AttributeKey[java.lang.Long]         = AttributeKey.longKey("ts")
  val ShuffleReadBytes: AttributeKey[java.lang.Long]  = AttributeKey.longKey("shuffle_read_bytes")
  val ShuffleWriteBytes: AttributeKey[java.lang.Long] = AttributeKey.longKey("shuffle_write_bytes")
  val SpillDiskBytes: AttributeKey[java.lang.Long]    = AttributeKey.longKey("spill_disk_bytes")
  val SpillMemBytes: AttributeKey[java.lang.Long]     = AttributeKey.longKey("spill_mem_bytes")
  val GcTimeMs: AttributeKey[java.lang.Long]          = AttributeKey.longKey("gc_time_ms")
  val ExecutorRunTimeMs: AttributeKey[java.lang.Long] = AttributeKey.longKey("executor_run_time_ms")
  val InputBytes: AttributeKey[java.lang.Long]        = AttributeKey.longKey("input_bytes")
  val OutputBytes: AttributeKey[java.lang.Long]       = AttributeKey.longKey("output_bytes")
  val PeakExecutionMemBytes: AttributeKey[java.lang.Long] = AttributeKey.longKey("peak_execution_mem_bytes")
  val TaskCount: AttributeKey[java.lang.Long]         = AttributeKey.longKey("task_count")
  val TaskDurationP50Ms: AttributeKey[java.lang.Long] = AttributeKey.longKey("task_duration_p50_ms")
  val TaskDurationP99Ms: AttributeKey[java.lang.Long] = AttributeKey.longKey("task_duration_p99_ms")
  val TaskDurationMaxMs: AttributeKey[java.lang.Long] = AttributeKey.longKey("task_duration_max_ms")
  val TaskDurationSampleCount: AttributeKey[java.lang.Long] =
    AttributeKey.longKey("task_duration_sample_count")
  val SuccessfulTaskDurationP50Ms: AttributeKey[java.lang.Long] =
    AttributeKey.longKey("successful_task_duration_p50_ms")
  val SuccessfulTaskDurationP99Ms: AttributeKey[java.lang.Long] =
    AttributeKey.longKey("successful_task_duration_p99_ms")
  val SuccessfulTaskDurationMaxMs: AttributeKey[java.lang.Long] =
    AttributeKey.longKey("successful_task_duration_max_ms")
  val SuccessfulTaskSampleCount: AttributeKey[java.lang.Long] =
    AttributeKey.longKey("successful_task_sample_count")
  val SuccessfulTaskShuffleReadBytesP50: AttributeKey[java.lang.Long] =
    AttributeKey.longKey("successful_task_shuffle_read_bytes_p50")
  val SuccessfulTaskShuffleReadBytesMax: AttributeKey[java.lang.Long] =
    AttributeKey.longKey("successful_task_shuffle_read_bytes_max")
  val SuccessfulTaskShuffleReadBytesSampleCount: AttributeKey[java.lang.Long] =
    AttributeKey.longKey("successful_task_shuffle_read_bytes_sample_count")
  val TaskAttemptCount: AttributeKey[java.lang.Long] =
    AttributeKey.longKey("task_attempt_count")
  val TaskFailedAttemptCount: AttributeKey[java.lang.Long] =
    AttributeKey.longKey("task_failed_attempt_count")
  val TaskCountedFailureAttemptCount: AttributeKey[java.lang.Long] =
    AttributeKey.longKey("task_counted_failure_attempt_count")
  val TaskKilledAttemptCount: AttributeKey[java.lang.Long] =
    AttributeKey.longKey("task_killed_attempt_count")
  val TaskSpeculativeAttemptCount: AttributeKey[java.lang.Long] =
    AttributeKey.longKey("task_speculative_attempt_count")
  val PlanFingerprint: AttributeKey[String]  = AttributeKey.stringKey("plan_fingerprint")
  val PlanJson: AttributeKey[String]         = AttributeKey.stringKey("plan_json")

  // v0.2 plan_transition span (AQE runtime decisions). job_id + ts reuse the keys above.
  val ExecutionId: AttributeKey[java.lang.Long] = AttributeKey.longKey("execution_id")
  val UpdateSeq: AttributeKey[java.lang.Long]   = AttributeKey.longKey("update_seq")
  val TransitionType: AttributeKey[String]      = AttributeKey.stringKey("transition_type")
  val Detail: AttributeKey[String]              = AttributeKey.stringKey("detail")
  val Before: AttributeKey[String]              = AttributeKey.stringKey("before")
  val After: AttributeKey[String]               = AttributeKey.stringKey("after")
  val Confidence: AttributeKey[String]          = AttributeKey.stringKey("confidence")
}
