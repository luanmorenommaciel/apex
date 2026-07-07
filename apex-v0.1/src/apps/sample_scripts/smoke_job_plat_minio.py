"""
Customer landing-to-bronze smoke job.

Manual submit command, assuming the Compose stack is already running:
docker exec -it spv0-spark-master \
  env PYTHONPATH=/opt/spark/src /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --conf spark.executorEnv.PYTHONPATH=/opt/spark/src \
  /opt/spark/src/apps/sample_scripts/smoke_job_plat_minio.py

Execution sequence:
1. Load lakehouse configuration from YAML.
2. Create a Spark session using this script app name.
3. Read the customer entity from the landing layer as JSON.
4. Standardize the customer DataFrame with the PySpark `.transform(...)` API.
5. Write the customer entity to the bronze layer as Delta.
6. Stop the Spark session.
"""

from pyspark.sql import functions as F

from spark_platform.jobs import SparkPlatJob
from spark_platform.utils.logger import logger


def standardize_customer(dataframe):
    """Step 4: standardize landing customer columns before writing bronze Delta."""
    return dataframe.select(
        F.col("customer_id").cast("long").alias("customer_id"),
        F.col("customer_name").cast("string").alias("customer_name"),
        F.col("country").cast("string").alias("country"),
        F.col("status").cast("string").alias("status"),
        F.col("lifetime_value").cast("double").alias("lifetime_value"),
        F.col("ingestion_ts").cast("timestamp").alias("landing_ingestion_ts"),
    ).withColumn("bronze_loaded_ts", F.current_timestamp())


class CustomerLandingToBronzeJob(SparkPlatJob):
    """Contract-based sample job that reads customer landing JSON and writes bronze Delta."""

    app_name = "spark-plat-v0-smoke-customer-bronze"
    entity_name = "customer"
    layer = "bronze"
    source_layer = "landing"

    def extract(self):
        """Step 3: read the customer entity from the landing layer as JSON."""
        return self.read_dataset(layer=self.source_layer)

    def transform(self, data):
        """Step 4: apply the named DataFrame transform that standardizes bronze columns."""
        return data.transform(standardize_customer)

    def load(self, data) -> None:
        """Step 5: write the transformed customer entity to the bronze layer as Delta."""
        self.write_dataset(data, layer=self.layer)
        logger.info(f"Wrote {self.layer}.{self.entity_name} to {self.write_config()['path']}")


def main() -> int:
    """
    Run the SparkPlatJob template.

    1. Load lakehouse configuration from YAML.
    2. Create a Spark session using this script app name.
    3. Read the customer entity from the landing layer as JSON.
    4. Standardize the customer DataFrame with `.transform(...)`.
    5. Write the customer entity to the bronze layer as Delta.
    6. Stop the Spark session.
    """
    return CustomerLandingToBronzeJob().run()


# Run only when this file is executed directly by spark-submit.
# SystemExit propagates main() as the process exit code, so Make/CI can
# fail correctly if a future main() returns a non-zero status.
if __name__ == "__main__":
    raise SystemExit(main())
