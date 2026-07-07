"""
Run a small sanity check over customer landing and bronze data.

Manual submit command, assuming the Compose stack is already running:
docker exec -it spv0-spark-master \
  env PYTHONPATH=/opt/spark/src /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --conf spark.executorEnv.PYTHONPATH=/opt/spark/src \
  /opt/spark/src/apps/sample_scripts/check_sanity.py

Execution sequence:
1. Load lakehouse configuration from YAML.
2. Create a Spark session using this script app name.
3. Read customer landing JSON and bronze Delta datasets.
4. Validate row counts, expected bronze columns, and basic grouped execution.
5. Stop the Spark session.
"""

from pyspark.sql import functions as F

from spark_platform.config import get_read_config
from spark_platform.io import read_dataset
from spark_platform.runner import run_spark_app
from spark_platform.utils.logger import logger

APP_NAME = "spark-plat-v0-sanity-customer-lakehouse"
ENTITY_NAME = "customer"
REQUIRED_BRONZE_COLUMNS = frozenset(
    {
        "customer_id",
        "customer_name",
        "country",
        "status",
        "lifetime_value",
        "landing_ingestion_ts",
        "bronze_loaded_ts",
    }
)


def validate_customer_datasets(landing_df, bronze_df) -> None:
    """
    Step 4: validate row counts, expected bronze columns, and grouped execution.

    This is intentionally separated from the ingestion and bronze jobs. Jobs should
    stay focused on data movement/transformation, while this script owns smoke
    assertions and Spark actions such as `count()`.
    """
    missing_columns = REQUIRED_BRONZE_COLUMNS.difference(bronze_df.columns)
    if missing_columns:
        raise ValueError(f"Bronze customer is missing columns: {sorted(missing_columns)}")

    landing_rows = landing_df.count()
    bronze_rows = bronze_df.count()
    if landing_rows == 0:
        raise ValueError("Landing customer dataset is empty")
    if bronze_rows != landing_rows:
        raise ValueError(f"Landing rows ({landing_rows}) differ from bronze rows ({bronze_rows})")

    country_groups = bronze_df.groupBy("country").agg(F.count("*").alias("customer_count"))
    country_group_count = country_groups.count()
    if country_group_count == 0:
        raise ValueError("Bronze customer grouped sanity check returned no countries")

    logger.info(
        "Sanity check passed "
        f"landing_rows={landing_rows} bronze_rows={bronze_rows} country_groups={country_group_count}"
    )


def main() -> int:
    """
    Run the customer lakehouse sanity check.

    1. Load lakehouse configuration from YAML.
    2. Create a Spark session using this script app name.
    3. Read customer landing JSON and bronze Delta datasets.
    4. Validate row counts, expected bronze columns, and basic grouped execution.
    5. Stop the Spark session.
    """
    def body(spark, config) -> int:
        landing_df = read_dataset(spark, get_read_config(config, ENTITY_NAME, "landing"))
        bronze_df = read_dataset(spark, get_read_config(config, ENTITY_NAME, "bronze"))
        validate_customer_datasets(landing_df, bronze_df)
        logger.info(f"Completed {APP_NAME}")
        return 0

    return run_spark_app(APP_NAME, body)


# Run only when this file is executed directly by spark-submit.
# SystemExit propagates main() as the process exit code, so Make/CI can
# fail correctly if a future main() returns a non-zero status.
if __name__ == "__main__":
    raise SystemExit(main())
