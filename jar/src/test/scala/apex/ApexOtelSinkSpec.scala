package apex

import com.sun.net.httpserver.{HttpExchange, HttpHandler, HttpServer}
import org.scalatest.funsuite.AnyFunSuite

import java.net.InetSocketAddress
import java.nio.charset.StandardCharsets
import java.util.concurrent.{CountDownLatch, TimeUnit}
import scala.collection.mutable.ArrayBuffer

class ApexOtelSinkSpec extends AnyFunSuite {

  private def stageEvent(executionId: Option[Long]): ApexStageEvent =
    ApexStageEvent(
      job_id = "job-1", app_id = "app-1", app_name = "apex-test",
      stage_id = 1, stage_attempt = 0, execution_id = executionId, ts = 1L,
      shuffle_read_bytes = 0L, shuffle_write_bytes = 0L,
      spill_disk_bytes = 0L, spill_mem_bytes = 0L, gc_time_ms = 0L,
      executor_run_time_ms = 0L, input_bytes = 0L, output_bytes = 0L,
      peak_execution_mem_bytes = 0L, task_count = 1,
      task_duration_p50_ms = 1L, task_duration_p99_ms = 1L,
      task_duration_max_ms = 1L, task_duration_sample_count = 1,
      successful_task_duration_p50_ms = 1L,
      successful_task_duration_p99_ms = 1L,
      successful_task_duration_max_ms = 1L,
      successful_task_sample_count = 1,
      successful_task_shuffle_read_bytes_p50 = 0L,
      successful_task_shuffle_read_bytes_max = 0L,
      successful_task_shuffle_read_bytes_sample_count = 1,
      task_attempt_count = 1, task_failed_attempt_count = 0,
      task_counted_failure_attempt_count = 0, task_killed_attempt_count = 0,
      task_speculative_attempt_count = 0, plan_fingerprint = "", plan_json = ""
    )

  private def exportedBytes(executionId: Option[Long]): Array[Byte] = {
    val received = ArrayBuffer.empty[Byte]
    val receivedLatch = new CountDownLatch(1)
    val server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0)
    server.createContext("/v1/traces", new HttpHandler {
      override def handle(exchange: HttpExchange): Unit = {
        received.synchronized { received ++= exchange.getRequestBody.readAllBytes() }
        exchange.sendResponseHeaders(200, -1)
        exchange.close()
        receivedLatch.countDown()
      }
    })
    server.start()
    val sink = new ApexOtelSink(s"http://127.0.0.1:${server.getAddress.getPort}", "apex-test")
    try {
      sink.emit(stageEvent(executionId))
      sink.close()
      assert(receivedLatch.await(5, TimeUnit.SECONDS), "OTLP exporter did not reach local test server")
      received.synchronized(received.toArray)
    } finally server.stop(0)
  }

  private final case class Field(number: Int, wireType: Int, value: Long, bytes: Array[Byte])

  private def readVarint(bytes: Array[Byte], start: Int): (Long, Int) = {
    var value = 0L
    var shift = 0
    var index = start
    while (index < bytes.length && shift < 64) {
      val b = bytes(index) & 0xff
      value |= (b & 0x7f).toLong << shift
      index += 1
      if ((b & 0x80) == 0) return (value, index)
      shift += 7
    }
    fail("invalid protobuf varint")
  }

  private def fields(bytes: Array[Byte]): Seq[Field] = {
    val result = ArrayBuffer.empty[Field]
    var index = 0
    while (index < bytes.length) {
      val (tag, afterTag) = readVarint(bytes, index)
      val number = (tag >>> 3).toInt
      val wireType = (tag & 0x07).toInt
      wireType match {
        case 0 =>
          val (value, afterValue) = readVarint(bytes, afterTag)
          result += Field(number, wireType, value, Array.emptyByteArray)
          index = afterValue
        case 1 =>
          require(afterTag + 8 <= bytes.length, "truncated fixed64 protobuf field")
          result += Field(number, wireType, 0L, Array.emptyByteArray)
          index = afterTag + 8
        case 2 =>
          val (length, afterLength) = readVarint(bytes, afterTag)
          require(length <= Int.MaxValue && afterLength + length <= bytes.length,
            "truncated length-delimited protobuf field")
          val end = afterLength + length.toInt
          result += Field(number, wireType, 0L, bytes.slice(afterLength, end))
          index = end
        case 5 =>
          require(afterTag + 4 <= bytes.length, "truncated fixed32 protobuf field")
          result += Field(number, wireType, 0L, Array.emptyByteArray)
          index = afterTag + 4
        case other => fail(s"unsupported protobuf wire type $other")
      }
    }
    result.toSeq
  }

  private def nested(message: Array[Byte], number: Int): Seq[Array[Byte]] =
    fields(message).collect { case Field(`number`, 2, _, bytes) => bytes }

  /** Extract `execution_id` only from OTLP KeyValue → AnyValue.int_value. */
  private def executionIdValues(request: Array[Byte]): Seq[Long] =
    // ExportTraceServiceRequest.resource_spans (1) → ResourceSpans.scope_spans (2)
    // → ScopeSpans.spans (2) → Span.attributes (9) → KeyValue.value (2).
    for {
      resourceSpans <- nested(request, 1)
      scopeSpans <- nested(resourceSpans, 2)
      spans <- nested(scopeSpans, 2)
      attribute <- nested(spans, 9)
      key <- nested(attribute, 1)
      if new String(key, StandardCharsets.UTF_8) == "execution_id"
      anyValue <- nested(attribute, 2)
      Field(3, 0, value, _) <- fields(anyValue)
    } yield value

  test("apex.stage exports execution_id as Int64 only when SQL correlation is available") {
    assert(executionIdValues(exportedBytes(Some(42L))) == Seq(42L),
      "OTLP KeyValue must encode execution_id as AnyValue.int_value=42")
    assert(executionIdValues(exportedBytes(None)).isEmpty,
      "OTLP payload must omit execution_id when no SQL correlation exists")
  }
}
