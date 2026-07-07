import pytest

from spark_platform.io import WriteSpec
from spark_platform.io import write_dataset
from tests.fakes.spark import FakeDataFrame


def test_write_dataset_uses_delta_format_mode_options_and_path():
    df = FakeDataFrame()

    write_dataset(
        df,
        {
            "format": "delta",
            "path": "s3a://lakehouse/bronze/customer",
            "mode": "overwrite",
            "options": {"overwriteSchema": True},
        },
    )

    writer = df.write.writers[0]
    assert writer.dataset_format == "delta"
    assert writer.mode_value == "overwrite"
    assert writer.options == [("overwriteSchema", "true")]
    assert writer.partition_columns == ()
    assert writer.saved_path == "s3a://lakehouse/bronze/customer"


def test_write_dataset_supports_partition_by_string():
    df = FakeDataFrame()

    write_dataset(
        df,
        WriteSpec(
            format="delta",
            path="s3a://lakehouse/silver/customer",
            mode="append",
            partition_by=("country",),
        ),
    )

    writer = df.write.writers[0]
    assert writer.partition_columns == ("country",)
    assert writer.saved_path == "s3a://lakehouse/silver/customer"


def test_write_dataset_supports_partition_by_list_from_mapping():
    df = FakeDataFrame()

    write_dataset(
        df,
        {
            "format": "delta",
            "path": "s3a://lakehouse/gold/customer",
            "partition_by": ["country", "status"],
        },
    )

    writer = df.write.writers[0]
    assert writer.mode_value == "errorifexists"
    assert writer.partition_columns == ("country", "status")


def test_write_dataset_supports_json_landing_format():
    df = FakeDataFrame()

    write_dataset(
        df,
        {
            "format": "json",
            "path": "s3a://lakehouse/landing/customer",
            "mode": "overwrite",
        },
    )

    writer = df.write.writers[0]
    assert writer.dataset_format == "json"
    assert writer.mode_value == "overwrite"
    assert writer.saved_path == "s3a://lakehouse/landing/customer"


def test_write_dataset_rejects_unsupported_format():
    with pytest.raises(ValueError, match="Unsupported write format"):
        write_dataset(FakeDataFrame(), {"format": "parquet", "path": "s3a://lakehouse/customer"})


def test_write_dataset_requires_path():
    with pytest.raises(ValueError, match="requires a path"):
        write_dataset(FakeDataFrame(), {"format": "delta"})
