import pytest

from spark_platform.io import read_dataset
from spark_platform.io import ReadSpec
from tests.fakes.spark import FakeSparkSession


def test_read_dataset_uses_delta_format_options_and_path():
    spark = FakeSparkSession()

    result = read_dataset(
        spark,
        {
            "format": "delta",
            "path": "s3a://lakehouse/bronze/customer",
            "options": {"mergeSchema": True},
        },
    )

    reader = spark.read.readers[0]
    assert reader.dataset_format == "delta"
    assert reader.options == [("mergeSchema", "true")]
    assert reader.loaded_path == "s3a://lakehouse/bronze/customer"
    assert result.path == "s3a://lakehouse/bronze/customer"


def test_read_dataset_supports_json_format():
    spark = FakeSparkSession()

    read_dataset(
        spark,
        ReadSpec(
            format="json",
            path="s3a://lakehouse/landing/customer",
            options={"multiLine": False},
        ),
    )

    reader = spark.read.readers[0]
    assert reader.dataset_format == "json"
    assert reader.options == [("multiLine", "false")]
    assert reader.loaded_path == "s3a://lakehouse/landing/customer"


def test_read_dataset_rejects_unsupported_format():
    with pytest.raises(ValueError, match="Unsupported read format"):
        read_dataset(FakeSparkSession(), {"format": "parquet", "path": "s3a://lakehouse/customer"})


def test_read_dataset_requires_path():
    with pytest.raises(ValueError, match="requires a path"):
        read_dataset(FakeSparkSession(), {"format": "delta"})
