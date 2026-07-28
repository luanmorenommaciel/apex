"""SparkConf canonicalisation. Every case here is a value seen in the live store."""

from __future__ import annotations

from apex_memory.conf import (
    canonical_value,
    config_identity,
    numeric_value,
    pool_configs,
    zest_columns,
)

FACTOR = "spark.sql.adaptive.skewJoin.skewedPartitionFactor"
ADVISORY = "spark.sql.adaptive.advisoryPartitionSizeInBytes"
THRESHOLD = "spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes"
BROADCAST = "spark.sql.autoBroadcastJoinThreshold"
PARTITIONS = "spark.sql.shuffle.partitions"


def test_same_value_spelled_two_ways_is_one_config():
    """'5.0' (40 runs) and '5' (11 runs) are the same setting.

    Counting them as two would invent configuration variation, and under
    contract v0.4 rule 3 invented variation unlocks a delta claim that should
    have stayed suppressed."""
    assert config_identity({FACTOR: "5.0"}) == config_identity({FACTOR: "5"})


def test_different_byte_sizes_stay_different():
    """'8m' vs '67108864b' is a real 8x difference."""
    assert config_identity({ADVISORY: "8m"}) != config_identity({ADVISORY: "67108864b"})
    assert numeric_value(ADVISORY, "8m") == 8 * 1024**2
    assert numeric_value(ADVISORY, "67108864b") == 67108864


def test_byte_suffixes_parse():
    assert numeric_value(THRESHOLD, "16m") == 16 * 1024**2
    assert numeric_value(THRESHOLD, "268435456b") == 268435456
    assert numeric_value("spark.executor.memory", "1g") == 1024  # MiB
    assert numeric_value("spark.driver.memory", "512m") == 512  # MiB


def test_negative_sentinel_is_not_scaled():
    """-1 disables autoBroadcastJoinThreshold; scaling it by a unit would turn
    a flag into a nonsense magnitude."""
    assert numeric_value(BROADCAST, "-1") == -1
    assert canonical_value(BROADCAST, "-1") == "-1"


def test_integer_keys_round_rather_than_render_a_float():
    """Averaging 200/100/8 gives 102.666...; `shuffle.partitions=102.666` is
    not a value Spark accepts, so the recommendation would be unappliable."""
    pooled, _ = pool_configs([{PARTITIONS: "200"}, {PARTITIONS: "100"}, {PARTITIONS: "8"}])
    assert pooled[PARTITIONS].lstrip("-").isdigit()
    assert pooled[PARTITIONS] == "103"


def test_booleans_are_pooled_by_majority_not_averaged():
    key = "spark.sql.adaptive.enabled"
    pooled, _ = pool_configs([{key: "true"}, {key: "true"}, {key: "false"}])
    assert pooled[key] == "true"


def test_key_support_is_reported():
    """A key set by one contributor out of three is weaker evidence than one
    they all agreed on, and the caller must be able to tell."""
    _, support = pool_configs(
        [{PARTITIONS: "200", "spark.executor.memory": "1g"}, {PARTITIONS: "100"}, {PARTITIONS: "8"}]
    )
    assert support[PARTITIONS] == 3
    assert support["spark.executor.memory"] == 1


def test_absent_key_is_none_never_a_default():
    """Only 8 of 13 allowlisted keys reach standalone runs. A synthesised
    default would be indistinguishable from an observation."""
    columns = zest_columns({PARTITIONS: "200"})
    assert columns["conf_shuffle_partitions"] == 200
    assert columns["conf_executor_memory_mb"] is None
    assert columns["conf_executor_instances"] is None
