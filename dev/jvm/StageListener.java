package apexdev;

import org.apache.spark.executor.TaskMetrics;
import org.apache.spark.scheduler.SparkListener;
import org.apache.spark.scheduler.SparkListenerStageCompleted;
import org.apache.spark.scheduler.SparkListenerTaskEnd;
import org.apache.spark.scheduler.StageInfo;
import scala.Option;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Dev-lane JVM SparkListener → one contract record per completed stage (the exact
 * 19 CONTRACT.md fields). Mirrors the jar's apex.ApexStageListener.
 *
 * Why JVM-side (Java) rather than a py4j Python listener: PySpark 4.0 uses py4j
 * ClientServer, under which JVM→Python callbacks on the async listener bus are
 * unreliable ("Error while obtaining a new communication channel / Connection
 * refused"). A JVM listener is invoked in-process by Spark — no callback plumbing —
 * so it is robust. Python only makes Python→JVM calls (construct, register,
 * setPlan), which always work.
 *
 * Sourcing matches the jar exactly: stage metrics come from stageInfo.taskMetrics
 * (already summed across tasks); onTaskEnd only collects per-task durations for
 * p50/p99 (nearest-rank); every callback is defensive so it never disrupts the bus.
 */
public class StageListener extends SparkListener {

    private final String jobId;
    private final String appId;
    private final String appName;
    private final String outPath;

    // Set from Python (setPlan) before the action; attached to each emitted record.
    private volatile String planFingerprint = "";
    private volatile String planJson = "";

    // (stageId, attempt) -> per-task durations (ms), for p50/p99 only.
    private final Map<Long, List<Long>> taskDur = new HashMap<>();

    public StageListener(String jobId, String appId, String appName, String outPath) {
        this.jobId = jobId;
        this.appId = appId;
        this.appName = appName;
        this.outPath = outPath;
        File parent = new File(outPath).getParentFile();
        if (parent != null) parent.mkdirs();
    }

    /** Current query's fingerprint + redacted plan_json (called from Python pre-action). */
    public void setPlan(String fingerprint, String json) {
        this.planFingerprint = fingerprint == null ? "" : fingerprint;
        this.planJson = json == null ? "" : json;
    }

    private static long key(int stage, int attempt) {
        return (((long) stage) << 32) | (attempt & 0xffffffffL);
    }

    @Override
    public void onTaskEnd(SparkListenerTaskEnd e) {
        try {
            long k = key(e.stageId(), e.stageAttemptId());
            long d = e.taskInfo().duration();
            synchronized (taskDur) {
                taskDur.computeIfAbsent(k, x -> new ArrayList<>()).add(d);
            }
        } catch (Throwable t) {
            // a listener that throws is evicted from the bus — never let it escape
        }
    }

    @Override
    public void onStageCompleted(SparkListenerStageCompleted e) {
        try {
            StageInfo si = e.stageInfo();
            int sid = si.stageId();
            int att = si.attemptNumber();

            List<Long> durs;
            synchronized (taskDur) {
                durs = taskDur.remove(key(sid, att));
            }
            if (durs == null) durs = new ArrayList<>();
            Collections.sort(durs);

            TaskMetrics tm = si.taskMetrics(); // null for stages with no tasks

            Option<Object> ct = si.completionTime();
            long ts = (ct != null && ct.isDefined())
                    ? ((Number) ct.get()).longValue()
                    : System.currentTimeMillis();

            StringBuilder sb = new StringBuilder(512);
            sb.append('{');
            str(sb, "job_id", jobId);            sb.append(',');
            str(sb, "app_id", appId);            sb.append(',');
            str(sb, "app_name", appName);        sb.append(',');
            num(sb, "stage_id", sid);            sb.append(',');
            num(sb, "stage_attempt", att);       sb.append(',');
            num(sb, "ts", ts);                   sb.append(',');
            num(sb, "shuffle_read_bytes",  tm == null ? 0 : tm.shuffleReadMetrics().totalBytesRead());  sb.append(',');
            num(sb, "shuffle_write_bytes", tm == null ? 0 : tm.shuffleWriteMetrics().bytesWritten());   sb.append(',');
            num(sb, "spill_disk_bytes",    tm == null ? 0 : tm.diskBytesSpilled());                     sb.append(',');
            num(sb, "spill_mem_bytes",     tm == null ? 0 : tm.memoryBytesSpilled());                   sb.append(',');
            num(sb, "gc_time_ms",          tm == null ? 0 : tm.jvmGCTime());                            sb.append(',');
            num(sb, "input_bytes",         tm == null ? 0 : tm.inputMetrics().bytesRead());             sb.append(',');
            num(sb, "output_bytes",        tm == null ? 0 : tm.outputMetrics().bytesWritten());         sb.append(',');
            num(sb, "peak_execution_mem_bytes", tm == null ? 0 : tm.peakExecutionMemory());            sb.append(',');
            num(sb, "task_count", si.numTasks());              sb.append(',');
            num(sb, "task_duration_p50_ms", percentile(durs, 0.50)); sb.append(',');
            num(sb, "task_duration_p99_ms", percentile(durs, 0.99)); sb.append(',');
            str(sb, "plan_fingerprint", planFingerprint); sb.append(',');
            str(sb, "plan_json", planJson);
            sb.append('}');

            writeLine(sb.toString());
        } catch (Throwable t) {
            System.err.println("apexdev StageListener onStageCompleted error: " + t);
        }
    }

    /** Nearest-rank percentile over an ascending list; 0 if empty. Matches the jar. */
    private static long percentile(List<Long> sorted, double q) {
        int n = sorted.size();
        if (n == 0) return 0L;
        int rank = (int) Math.ceil(q * n);
        return sorted.get(Math.min(n - 1, Math.max(0, rank - 1)));
    }

    private synchronized void writeLine(String line) {
        try (BufferedWriter w = new BufferedWriter(new FileWriter(outPath, true))) {
            w.write(line);
            w.newLine();
        } catch (Exception ex) {
            System.err.println("apexdev StageListener write error: " + ex);
        }
    }

    private static void num(StringBuilder sb, String k, long v) {
        sb.append('"').append(k).append("\":").append(v);
    }

    private static void str(StringBuilder sb, String k, String v) {
        sb.append('"').append(k).append("\":\"").append(escape(v == null ? "" : v)).append('"');
    }

    private static String escape(String s) {
        StringBuilder b = new StringBuilder(s.length() + 8);
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '"':  b.append("\\\""); break;
                case '\\': b.append("\\\\"); break;
                case '\n': b.append("\\n"); break;
                case '\r': b.append("\\r"); break;
                case '\t': b.append("\\t"); break;
                default:
                    if (c < 0x20) b.append(String.format("\\u%04x", (int) c));
                    else b.append(c);
            }
        }
        return b.toString();
    }
}
