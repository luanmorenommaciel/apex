"""
Persist sample customer data into the landing layer.

Manual submit command, assuming the Compose stack is already running:
docker exec -it spv0-spark-master \
  env PYTHONPATH=/opt/spark/src /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --conf spark.executorEnv.PYTHONPATH=/opt/spark/src \
  /opt/spark/src/apps/sample_scripts/simple_persist_customers_landing.py

Execution sequence:
1. Load lakehouse configuration from YAML.
2. Create a Spark session using this script app name.
3. Generate a small customer DataFrame in memory.
4. Persist the customer entity to the landing layer as JSON.
5. Stop the Spark session.
"""

from pyspark.sql import functions as F

from spark_platform.config import get_write_config
from spark_platform.io import write_dataset
from spark_platform.runner import run_spark_app
from spark_platform.utils.logger import logger

APP_NAME = "spark-plat-v0-sample-customer-landing"
ENTITY_NAME = "customer"
LAYER = "landing"


def customer_rows() -> list[dict[str, object]]:
    """Step 3: define the small fake customer payload used by this sample ingestion."""
    return [
        {
            "customer_id": 1,
            "customer_name": "Ada Lovelace",
            "country": "UK",
            "status": "active",
            "lifetime_value": 1200.50,
        },
        {
            "customer_id": 2,
            "customer_name": "Grace Hopper",
            "country": "US",
            "status": "active",
            "lifetime_value": 980.00,
        },
        {
            "customer_id": 3,
            "customer_name": "Katherine Johnson",
            "country": "US",
            "status": "active",
            "lifetime_value": 1560.75,
        },
        {
            "customer_id": 4,
            "customer_name": "Mary Jackson",
            "country": "US",
            "status": "inactive",
            "lifetime_value": 430.25,
        },
        {
            "customer_id": 5,
            "customer_name": "Dorothy Vaughan",
            "country": "US",
            "status": "active",
            "lifetime_value": 870.00,
        },
    ]


def build_customer_dataframe(spark):
    """Step 3: turn the fake customer payload into a Spark DataFrame with ingestion metadata."""
    return spark.createDataFrame(customer_rows()).withColumn("ingestion_ts", F.current_timestamp())


def main() -> int:
    """
    Run the landing ingestion script.

    1. Load lakehouse configuration from YAML.
    2. Create a Spark session using this script app name.
    3. Generate a small customer DataFrame in memory.
    4. Persist the customer entity to the landing layer as JSON.
    5. Stop the Spark session.
    """
    def body(spark, config) -> int:
        dataframe = build_customer_dataframe(spark)
        write_config = get_write_config(config, ENTITY_NAME, LAYER)
        write_dataset(dataframe, write_config)
        logger.info(f"Wrote {LAYER}.{ENTITY_NAME} to {write_config['path']}")
        logger.info(f"Completed {APP_NAME}")
        return 0

    return run_spark_app(APP_NAME, body)


# Run only when this file is executed directly by spark-submit.
# SystemExit propagates main() as the process exit code, so Make/CI can
# fail correctly if a future main() returns a non-zero status.
if __name__ == "__main__":
    raise SystemExit(main())
