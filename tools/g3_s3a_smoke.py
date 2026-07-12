from pyspark.sql import SparkSession


spark = SparkSession.builder.appName("apex-g3-s3a-smoke").getOrCreate()
try:
    spark.range(0, 1000, 1, 8).repartition(8).count()
finally:
    spark.stop()
