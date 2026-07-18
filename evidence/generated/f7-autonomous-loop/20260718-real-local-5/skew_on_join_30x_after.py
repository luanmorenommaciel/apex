# Auto-gerado por code_generator v4 — scenario: skew_on_join_30x
from pyspark.sql import SparkSession
from pyspark.sql.functions import broadcast, col, rand, when, collect_list

spark = (SparkSession.builder.appName("skew_on_join_30x")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.adaptive.skewJoin.enabled", "true")
    .config("spark.sql.shuffle.partitions", "8")
    .config("spark.sql.adaptive.coalescePartitions.enabled", "false")
    .config("spark.sql.adaptive.autoBroadcastJoinThreshold", "10485760")
    .getOrCreate())

orders = spark.range(200000).select(
    (rand(42) * 100).cast('int').alias('customer_id'),
    col('id').alias('order_id'))
orders = orders.withColumn('customer_id',
    when(rand(13) < 0.8, 7).otherwise(col('customer_id')))
customers = spark.range(100).select(
    col('id').alias('customer_id'), col('id').alias('customer_name'))
result = orders.join(broadcast(customers), "customer_id", "inner")  # APEX::FIXED_BY_F7_LOOP
result.write.mode("overwrite").parquet("/tmp/apex_output")
spark.stop()
