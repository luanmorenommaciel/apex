package apex.commander.spark;

import java.nio.file.Files;
import java.nio.file.Path;

import org.apache.spark.SparkConf;

public final class ApexSparkListenerSelfTest {
    private ApexSparkListenerSelfTest() {
    }

    public static void main(String[] args) throws Exception {
        Path output = Files.createTempFile("apex-listener-", ".ndjson");

        SparkConf normalConf = new SparkConf(false)
            .set(ApexSparkListener.JOB_ID_KEY, "self-test-job")
            .set(ApexSparkListener.OUTPUT_KEY, output.toString());
        ApexSparkListener normal = new ApexSparkListener(normalConf);
        normal.emitForSelfTest("self_test");

        String content = Files.readString(output);
        if (!content.contains("\"event_type\":\"self_test\"")) {
            throw new AssertionError("self-test event was not written");
        }
        if (!content.contains("\"job_id\":\"self-test-job\"")) {
            throw new AssertionError("job_id was not written");
        }

        SparkConf failConf = new SparkConf(false)
            .set(ApexSparkListener.FAIL_MODE_KEY, "true")
            .set(ApexSparkListener.OUTPUT_KEY, output.toString());
        ApexSparkListener failSafe = new ApexSparkListener(failConf);
        failSafe.emitForSelfTest("forced_failure");

        System.out.println("ApexSparkListenerSelfTest passed");
    }
}
