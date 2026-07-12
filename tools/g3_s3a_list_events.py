from pyspark.sql import SparkSession


spark = SparkSession.builder.appName("apex-g3-s3a-list-events").getOrCreate()
try:
    jvm = spark.sparkContext._jvm
    conf = spark.sparkContext._jsc.hadoopConfiguration()
    path = jvm.org.apache.hadoop.fs.Path("s3a://spark-logs/events")
    filesystem = path.getFileSystem(conf)
    for status in filesystem.listStatus(path):
        print(status.getPath().toString())
finally:
    spark.stop()
