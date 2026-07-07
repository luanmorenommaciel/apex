from collections.abc import Callable
from typing import Any

from spark_platform.config import load_config
from spark_platform.session import SparkSessionFactory
from spark_platform.utils.logger import logger


def run_spark_app(
    app_name: str,
    body: Callable[[Any, dict[str, Any]], int],
    extra_conf: dict[str, Any] | None = None,
    env: str | None = None,
) -> int:
    """Run a Spark application body with the standard lifecycle.

    Centralizes the config-load -> log-level -> session -> try/finally: stop
    ritual that every workload and sample script repeated verbatim. `body`
    receives the live SparkSession and the loaded config (workloads that don't
    need the config can ignore it) and returns the process exit code.

    Example:
        def main() -> int:
            params = load_params("skew_join")
            def body(spark, config):
                build_skewed_join(spark, params).write.format("noop").save()
                return 0
            return run_spark_app("workload-skew", body, extra_conf=params.spark_conf())
    """
    config = load_config(env=env)
    logger.set_level(config.get("app", {}).get("log_level", "INFO"))
    logger.info(f"Starting {app_name}")
    spark = SparkSessionFactory.get_or_create(config, app_name=app_name, extra_conf=extra_conf)
    try:
        return body(spark, config)
    finally:
        SparkSessionFactory.stop_active()
