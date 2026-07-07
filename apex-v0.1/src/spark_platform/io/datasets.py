from typing import Any, Mapping

from spark_platform.io.specs import ReadSpec, WriteSpec, ensure_read_spec, ensure_write_spec, option_value
from spark_platform.utils.logger import logger


def read_dataset(spark: Any, read_config: Mapping[str, Any] | ReadSpec) -> Any:
    spec = ensure_read_spec(read_config)
    reader = spark.read.format(spec.format)
    if spec.schema:
        reader = reader.schema(spec.schema)
    for key, value in spec.options.items():
        reader = reader.option(key, option_value(value))

    logger.info(f"Reading {spec.format} dataset from {spec.path}")
    return reader.load(spec.path)


def write_dataset(dataframe: Any, write_config: Mapping[str, Any] | WriteSpec) -> None:
    spec = ensure_write_spec(write_config)
    writer = dataframe.write.format(spec.format).mode(spec.mode)
    for key, value in spec.options.items():
        writer = writer.option(key, option_value(value))
    if spec.partition_by:
        writer = writer.partitionBy(*spec.partition_by)

    logger.info(f"Writing {spec.format} dataset to {spec.path} with mode={spec.mode}")
    writer.save(spec.path)
