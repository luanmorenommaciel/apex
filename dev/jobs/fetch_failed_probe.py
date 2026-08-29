"""P2 real failure-semantics probe.

The first action materializes shuffle map outputs. The operator then removes
only shuffle files from one live worker while this process waits. The second
action reuses the same shuffle dependency, forcing a real fetch attempt against
the missing blocks. The expected scheduler reason is FetchFailed, which must
not increment task_counted_failure_attempt_count.
"""

from __future__ import annotations

import os
import time

from pyspark.sql import SparkSession


spark = (
    SparkSession.builder.appName("apex-p2-fetch-failed-probe")
    .config("spark.apex.job_id", os.environ.get("APEX_JOB_ID", "p2-fetch-failed-probe"))
    .config("spark.sql.adaptive.enabled", "false")
    .getOrCreate()
)
sc = spark.sparkContext
sc.setLogLevel("INFO")

partition_count = int(os.environ.get("APEX_P2_PARTITIONS", "32"))
row_count = int(os.environ.get("APEX_P2_ROWS", "2000000"))
pause_seconds = int(os.environ.get("APEX_P2_PAUSE_SECONDS", "45"))

shuffled = (
    sc.parallelize(range(row_count), partition_count)
    .map(lambda value: (value % 4096, value))
    .reduceByKey(lambda left, right: left + right, numPartitions=partition_count)
)

first_count = shuffled.count()
print(
    f"APEX_P2_SHUFFLE_READY count={first_count} "
    f"partitions={partition_count} pause_seconds={pause_seconds}",
    flush=True,
)
time.sleep(pause_seconds)

second_count = shuffled.count()
print(f"APEX_P2_SECOND_ACTION_COMPLETE count={second_count}", flush=True)
spark.stop()
