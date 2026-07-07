from abc import ABC, abstractmethod
from typing import Any

from spark_platform.config import get_read_config, get_write_config, load_config
from spark_platform.io import read_dataset, write_dataset
from spark_platform.session import SparkSessionFactory
from spark_platform.utils.logger import logger


class SparkPlatJob(ABC):
    app_name = SparkSessionFactory.DEFAULT_APP_NAME
    entity_name: str | None = None
    layer: str | None = None

    def __init__(self, env: str | None = None):
        self.env = env
        self.config: dict[str, Any] = {}
        self.spark = None

    def run(self) -> int:
        self.config = load_config(env=self.env)
        logger.set_level(self.config.get("app", {}).get("log_level", "INFO"))
        logger.info(f"Starting {self.app_name}")

        self.spark = SparkSessionFactory.get_or_create(self.config, app_name=self.app_name)
        try:
            extracted = self.extract()
            transformed = self.transform(extracted)
            self.load(transformed)
            logger.info(f"Completed {self.app_name}")
            return 0
        finally:
            SparkSessionFactory.stop_active()

    def read_config(self, entity_name: str | None = None, layer: str | None = None) -> dict[str, Any]:
        return get_read_config(self.config, entity_name or self.require_entity_name(), layer or self.require_layer())

    def write_config(self, entity_name: str | None = None, layer: str | None = None) -> dict[str, Any]:
        return get_write_config(self.config, entity_name or self.require_entity_name(), layer or self.require_layer())

    def read_dataset(self, entity_name: str | None = None, layer: str | None = None) -> Any:
        return read_dataset(self.require_spark(), self.read_config(entity_name, layer))

    def write_dataset(self, dataframe: Any, entity_name: str | None = None, layer: str | None = None) -> None:
        write_dataset(dataframe, self.write_config(entity_name, layer))

    @abstractmethod
    def extract(self) -> Any:
        pass

    def transform(self, data: Any) -> Any:
        return data

    def load(self, data: Any) -> None:
        self.write_dataset(data)

    def require_spark(self) -> Any:
        if self.spark is None:
            raise RuntimeError("Spark session is not initialized")
        return self.spark

    def require_entity_name(self) -> str:
        if not self.entity_name:
            raise ValueError("Job must define entity_name or pass one explicitly")
        return self.entity_name

    def require_layer(self) -> str:
        if not self.layer:
            raise ValueError("Job must define layer or pass one explicitly")
        return self.layer
