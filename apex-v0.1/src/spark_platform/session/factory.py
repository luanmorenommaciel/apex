from typing import Any

from spark_platform.utils.logger import logger


class SparkSessionFactory:
    DEFAULT_APP_NAME = "spark-plat-v0-default-app"
    DEFAULT_CONF = {
        "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
        "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
    }

    @classmethod
    def get_or_create(
        cls,
        config: dict[str, Any],
        app_name: str | None = None,
        extra_conf: dict[str, Any] | None = None,
    ) -> Any:
        from pyspark.sql import SparkSession

        spark_config = config.get("spark", {})
        resolved_app_name = app_name or cls.DEFAULT_APP_NAME

        builder = SparkSession.builder.appName(resolved_app_name)
        if spark_config.get("master"):
            builder = builder.master(spark_config["master"])

        spark_conf = dict(cls.DEFAULT_CONF)
        spark_conf.update(spark_config.get("config", {}) or {})
        spark_conf.update(extra_conf or {})

        for key, value in spark_conf.items():
            builder = builder.config(key, _to_spark_conf_value(value))

        logger.info(f"Creating SparkSession app_name={resolved_app_name}")
        spark = builder.getOrCreate()

        if spark_config.get("log_level"):
            spark.sparkContext.setLogLevel(str(spark_config["log_level"]).upper())

        return spark

    @staticmethod
    def stop_active() -> None:
        from pyspark.sql import SparkSession

        active = SparkSession.getActiveSession()
        if active is not None:
            logger.info("Stopping active SparkSession")
            active.stop()


def _to_spark_conf_value(value: Any) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)
