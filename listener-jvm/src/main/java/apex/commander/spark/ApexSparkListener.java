package apex.commander.spark;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;

import org.apache.spark.SparkConf;
import org.apache.spark.executor.TaskMetrics;
import org.apache.spark.scheduler.SparkListener;
import org.apache.spark.scheduler.SparkListenerApplicationEnd;
import org.apache.spark.scheduler.SparkListenerApplicationStart;
import org.apache.spark.scheduler.SparkListenerStageSubmitted;
import org.apache.spark.scheduler.SparkListenerTaskEnd;

/**
 * Minimal fail-safe SparkListener for Apex telemetry capture.
 *
 * <p>This listener is intentionally conservative: every Spark callback is wrapped
 * in a catch-all guard so internal telemetry failures do not fail the Spark job.
 */
public final class ApexSparkListener extends SparkListener {
    static final String JOB_ID_KEY = "spark.apex.jobId";
    static final String OUTPUT_KEY = "spark.apex.listener.output";
    static final String FAIL_MODE_KEY = "spark.apex.listener.failMode";

    private final String jobId;
    private final Path outputPath;
    private final boolean failMode;
    private volatile String appId = "";

    public ApexSparkListener() {
        this(new SparkConf());
    }

    public ApexSparkListener(SparkConf conf) {
        this.jobId = conf.get(JOB_ID_KEY, "");
        String output = conf.get(OUTPUT_KEY, "");
        this.outputPath = output == null || output.isBlank() ? null : Paths.get(output);
        this.failMode = Boolean.parseBoolean(conf.get(FAIL_MODE_KEY, "false"));
    }

    @Override
    public void onApplicationStart(SparkListenerApplicationStart applicationStart) {
        safeRun("application_start", () -> {
            maybeFail();
            if (applicationStart != null && applicationStart.appId().isDefined()) {
                appId = String.valueOf(applicationStart.appId().get());
            }

            Map<String, Object> event = baseEvent("application_start");
            if (applicationStart != null) {
                event.put("app_name", applicationStart.appName());
                event.put("app_id", appId);
                event.put("time", applicationStart.time());
            }
            writeEvent(event);
        });
    }

    @Override
    public void onStageSubmitted(SparkListenerStageSubmitted stageSubmitted) {
        safeRun("stage_submitted", () -> {
            maybeFail();
            Map<String, Object> event = baseEvent("stage_submitted");
            if (stageSubmitted != null && stageSubmitted.stageInfo() != null) {
                event.put("stage_id", stageSubmitted.stageInfo().stageId());
                event.put("stage_attempt_id", stageSubmitted.stageInfo().attemptNumber());
                event.put("stage_name", stageSubmitted.stageInfo().name());
                event.put("task_count", stageSubmitted.stageInfo().numTasks());
            }
            writeEvent(event);
        });
    }

    @Override
    public void onTaskEnd(SparkListenerTaskEnd taskEnd) {
        safeRun("task_end", () -> {
            maybeFail();
            Map<String, Object> event = baseEvent("task_end");
            if (taskEnd != null) {
                event.put("stage_id", taskEnd.stageId());
                event.put("stage_attempt_id", taskEnd.stageAttemptId());
                event.put("task_type", taskEnd.taskType());
                event.put("reason", String.valueOf(taskEnd.reason()));
                addTaskMetrics(event, taskEnd.taskMetrics());
            }
            writeEvent(event);
        });
    }

    @Override
    public void onApplicationEnd(SparkListenerApplicationEnd applicationEnd) {
        safeRun("application_end", () -> {
            maybeFail();
            Map<String, Object> event = baseEvent("application_end");
            if (applicationEnd != null) {
                event.put("time", applicationEnd.time());
            }
            writeEvent(event);
        });
    }

    void emitForSelfTest(String eventType) {
        safeRun(eventType, () -> {
            maybeFail();
            writeEvent(baseEvent(eventType));
        });
    }

    private Map<String, Object> baseEvent(String eventType) {
        Map<String, Object> event = new LinkedHashMap<>();
        event.put("ts", Instant.now().toString());
        event.put("job_id", jobId);
        event.put("app_id", appId);
        event.put("event_type", eventType);
        return event;
    }

    private void addTaskMetrics(Map<String, Object> event, TaskMetrics metrics) {
        if (metrics == null) {
            return;
        }

        event.put("executor_run_time_ms", metrics.executorRunTime());
        event.put("jvm_gc_time_ms", metrics.jvmGCTime());
        event.put("disk_bytes_spilled", metrics.diskBytesSpilled());
        event.put("memory_bytes_spilled", metrics.memoryBytesSpilled());

        if (metrics.shuffleReadMetrics() != null) {
            event.put("shuffle_remote_bytes_read", metrics.shuffleReadMetrics().remoteBytesRead());
            event.put("shuffle_local_bytes_read", metrics.shuffleReadMetrics().localBytesRead());
        }

        if (metrics.shuffleWriteMetrics() != null) {
            event.put("shuffle_bytes_written", metrics.shuffleWriteMetrics().bytesWritten());
        }
    }

    private void maybeFail() {
        if (failMode) {
            throw new IllegalStateException("spark.apex.listener.failMode=true");
        }
    }

    private void safeRun(String callback, ThrowingRunnable runnable) {
        try {
            runnable.run();
        } catch (Throwable throwable) {
            System.err.println("[apex-listener] callback=" + callback + " failed: " + throwable);
        }
    }

    private synchronized void writeEvent(Map<String, Object> event) throws IOException {
        if (outputPath == null) {
            return;
        }

        Path parent = outputPath.getParent();
        if (parent != null) {
            Files.createDirectories(parent);
        }

        Files.writeString(
            outputPath,
            toJson(event) + System.lineSeparator(),
            StandardCharsets.UTF_8,
            StandardOpenOption.CREATE,
            StandardOpenOption.APPEND
        );
    }

    private String toJson(Map<String, Object> event) {
        StringBuilder builder = new StringBuilder();
        builder.append('{');
        boolean first = true;
        for (Map.Entry<String, Object> entry : event.entrySet()) {
            if (!first) {
                builder.append(',');
            }
            first = false;
            builder.append('"').append(escapeJson(entry.getKey())).append('"').append(':');
            appendJsonValue(builder, entry.getValue());
        }
        builder.append('}');
        return builder.toString();
    }

    private void appendJsonValue(StringBuilder builder, Object value) {
        if (value == null) {
            builder.append("null");
        } else if (value instanceof Number || value instanceof Boolean) {
            builder.append(value);
        } else {
            builder.append('"').append(escapeJson(String.valueOf(value))).append('"');
        }
    }

    private String escapeJson(String value) {
        return value
            .replace("\\", "\\\\")
            .replace("\"", "\\\"")
            .replace("\r", "\\r")
            .replace("\n", "\\n")
            .replace("\t", "\\t");
    }

    @FunctionalInterface
    private interface ThrowingRunnable {
        void run() throws Exception;
    }
}
