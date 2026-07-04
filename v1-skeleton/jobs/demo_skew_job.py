"""
Apex V1 — Demo Job com ApexSparkListener
Gera um job com skew proposital para testar o pipeline.

Uso dentro do container:
    spark-submit \
      --master spark://spark-master:7077 \
      --py-files /opt/listener/spark_listener.py,/opt/listener/clickhouse_writer.py \
      /opt/jobs/demo_skew_job.py
"""
import sys
import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("apex.demo_job")

# Config ClickHouse — lê de env var ou usa default (docker-compose)
CH_HOST = os.getenv("APEX_CH_HOST", "clickhouse")
CH_PORT = int(os.getenv("APEX_CH_PORT", "8123"))


def build_spark() -> SparkSession:
    return (
        SparkSession.builder
        .appName("apex-demo-skew-job")
        .config("spark.eventLog.enabled", "true")
        .config("spark.eventLog.dir", "/spark-logs")
        .config("spark.sql.shuffle.partitions", "50")
        .getOrCreate()
    )


def generate_skewed_data(spark: SparkSession):
    """
    Gera um dataset com hot key proposital.
    80% dos registros têm key='HOT_KEY' → simula skew real.
    """
    schema = StructType([
        StructField("key",   StringType(),  False),
        StructField("value", LongType(),    False),
    ])

    normal_keys = [(f"key_{i % 20}", i * 100) for i in range(10_000)]
    hot_keys    = [("HOT_KEY", i) for i in range(40_000)]  # 4x mais

    data = normal_keys + hot_keys

    return spark.createDataFrame(data, schema=schema)


def run_skew_aggregation(spark: SparkSession):
    """
    Join + GroupBy que vai provocar skew visível nas métricas.
    """
    df = generate_skewed_data(spark)

    # Simula join sem broadcast (força shuffle)
    df2 = df.select(
        F.col("key").alias("join_key"),
        (F.col("value") * 2).alias("value2")
    )

    joined = df.join(df2, df["key"] == df2["join_key"])

    result = (
        joined
        .groupBy("key")
        .agg(
            F.count("*").alias("count"),
            F.sum("value").alias("total_value"),
            F.avg("value").alias("avg_value"),
        )
        .orderBy(F.desc("count"))
    )

    # Força materialização
    count = result.count()
    logger.info(f"Job completo — {count} grupos processados")
    return result


def main():
    logger.info("Iniciando Apex Demo Job (Skew)")

    spark = build_spark()
    app_id = spark.sparkContext.applicationId
    logger.info(f"app_id={app_id}")

    # Registra o listener ANTES de rodar qualquer ação
    try:
        sys.path.insert(0, "/opt/listener")
        from spark_listener import attach_to_spark
        attach_to_spark(spark, app_id=app_id, ch_host=CH_HOST)
        logger.info("ApexSparkListener registrado com sucesso")
    except Exception as e:
        logger.warning(f"Listener não registrado (continuando sem): {e}")

    # Roda o job com skew
    run_skew_aggregation(spark)

    spark.stop()
    logger.info(f"Job finalizado | app_id={app_id}")
    logger.info(f"Consulte o ClickHouse: SELECT * FROM apex.suspicious_stages WHERE app_id='{app_id}'")


if __name__ == "__main__":
    main()
