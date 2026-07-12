import sys

from pyspark.sql import SparkSession


if len(sys.argv) != 3:
    raise SystemExit(
        "usage: g3_s3a_fetch_event_log.py <s3a://bucket/path/events.zstd> <local-output>"
    )

source_uri = sys.argv[1]
target_path = sys.argv[2]

spark = SparkSession.builder.appName("apex-g3-s3a-fetch-event-log").getOrCreate()
try:
    jvm = spark.sparkContext._jvm
    conf = spark.sparkContext._jsc.hadoopConfiguration()

    source = jvm.org.apache.hadoop.fs.Path(source_uri)
    target = jvm.org.apache.hadoop.fs.Path(target_path)
    source_fs = source.getFileSystem(conf)
    local_fs = jvm.org.apache.hadoop.fs.FileSystem.getLocal(conf)

    parent = target.getParent()
    if parent is not None:
        local_fs.mkdirs(parent)
    if local_fs.exists(target):
        local_fs.delete(target, True)

    copied = jvm.org.apache.hadoop.fs.FileUtil.copy(
        source_fs,
        source,
        local_fs,
        target,
        False,
        conf,
    )
    if not copied:
        raise RuntimeError(f"copy returned false: {source_uri} -> {target_path}")
    print(f"copied {source_uri} -> {target_path}")
finally:
    spark.stop()
