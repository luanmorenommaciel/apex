"""Canonicalisation of the allowlisted SparkConf captured in apex.job_conf (v0.4).

WHY THIS MODULE EXISTS
----------------------
Spark accepts the same configuration value spelled many ways, and the live store
contains several of those spellings at once. Comparing the raw strings would be
wrong in BOTH directions, which is the worst kind of wrong:

  * `spark.sql.adaptive.skewJoin.skewedPartitionFactor` is `'5.0'` on 40 runs and
    `'5'` on 11. Identical value, two spellings -- raw comparison invents a
    configuration difference that does not exist, and under the v0.4
    attributability rule an invented difference is enough to unlock a delta
    claim that should have been suppressed.
  * `spark.sql.adaptive.advisoryPartitionSizeInBytes` is `'67108864b'` on 40 runs
    and `'8m'` on 11 -- 64 MiB versus 8 MiB, a real 8x difference that a naive
    "are these strings different?" check would catch but a naive numeric parse
    (`int('8m')`) would crash on.

So every value is parsed according to what its key actually means before it is
compared or averaged.

ABSENT IS NOT DEFAULT
---------------------
Only 8 of the 13 allowlisted keys reach standalone runs; `spark.executor.*` and
`spark.driver.*` appear only when explicitly set (10, 4 and 6 runs out of 51
respectively). The jar deliberately does not synthesise the rest, because a
fabricated default recorded as "the config that worked" would poison the exact
recommendation this lane exists to make. Nothing here fills a gap either: a
missing key stays missing all the way to the caller.
"""

from __future__ import annotations

import re

# ── Key typing ───────────────────────────────────────────────────────────────
# Values are byte sizes, memory strings, integers, floats or booleans depending
# on the key. Spark itself parses them with different helpers; so do we.
BYTE_KEYS = frozenset({
    "spark.sql.adaptive.advisoryPartitionSizeInBytes",
    "spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes",
    "spark.sql.autoBroadcastJoinThreshold",
})
# Spark parses these with byteStringAsMb, so a bare number means MiB, not bytes.
MEMORY_MB_KEYS = frozenset({
    "spark.executor.memory",
    "spark.driver.memory",
})
INT_KEYS = frozenset({
    "spark.sql.shuffle.partitions",
    "spark.executor.instances",
    "spark.executor.cores",
    "spark.driver.cores",
})
FLOAT_KEYS = frozenset({
    "spark.sql.adaptive.skewJoin.skewedPartitionFactor",
})
BOOL_KEYS = frozenset({
    "spark.sql.adaptive.enabled",
    "spark.sql.adaptive.coalescePartitions.enabled",
    "spark.sql.adaptive.skewJoin.enabled",
})

# Keys whose value is a magnitude that can be meaningfully averaged. Booleans
# cannot -- the mean of true and false is not a configuration -- so they are
# pooled by majority vote instead. ZEST tunes only numeric parameters and its
# paper does not address categoricals at all (arXiv 2503.03826 § 4.2), so this
# split is an explicit extension of Algorithm 1, not something inherited from it.
NUMERIC_KEYS = BYTE_KEYS | MEMORY_MB_KEYS | INT_KEYS | FLOAT_KEYS

# The ZEST six -> the run_outcomes typed columns they populate.
ZEST_KEY_TO_COLUMN: dict[str, str] = {
    "spark.sql.shuffle.partitions": "conf_shuffle_partitions",
    "spark.executor.instances": "conf_executor_instances",
    "spark.executor.cores": "conf_executor_cores",
    "spark.executor.memory": "conf_executor_memory_mb",
    "spark.driver.cores": "conf_driver_cores",
    "spark.driver.memory": "conf_driver_memory_mb",
}

_SIZE_RE = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*([kmgtp]?)b?\s*$", re.IGNORECASE)
_UNIT_MULTIPLIER = {
    "": 1,
    "k": 1024,
    "m": 1024**2,
    "g": 1024**3,
    "t": 1024**4,
    "p": 1024**5,
}


def parse_size(raw: str, *, bare_unit_bytes: int = 1) -> float | None:
    """Parse a Spark size string ('8m', '67108864b', '1g', '-1') to a number.

    `bare_unit_bytes` is the multiplier for a value with no unit suffix, which
    differs by key: byte-typed configs treat a bare number as bytes, memory
    configs treat it as MiB.

    A negative value is returned verbatim. `-1` is Spark's "disabled" sentinel
    (autoBroadcastJoinThreshold) and scaling it by a unit would turn a flag into
    a nonsense magnitude.
    """
    match = _SIZE_RE.match(raw)
    if not match:
        return None
    number = float(match.group(1))
    if number < 0:
        return number
    unit = match.group(2).lower()
    multiplier = _UNIT_MULTIPLIER[unit] if unit else bare_unit_bytes
    return number * multiplier


def numeric_value(key: str, raw: str) -> float | None:
    """The comparable magnitude for a key, or None if it has none."""
    raw = (raw or "").strip()
    if not raw:
        return None
    if key in BYTE_KEYS:
        return parse_size(raw, bare_unit_bytes=1)
    if key in MEMORY_MB_KEYS:
        # Normalise to MiB to match the conf_*_memory_mb columns.
        as_bytes = parse_size(raw, bare_unit_bytes=1024**2)
        return None if as_bytes is None else as_bytes / (1024**2)
    if key in INT_KEYS or key in FLOAT_KEYS:
        try:
            return float(raw)
        except ValueError:
            return None
    return None


def canonical_value(key: str, raw: str) -> str:
    """A single spelling per distinct value, for identity comparison.

    This is what makes `'5'` and `'5.0'` one configuration rather than two, and
    keeps `'8m'` and `'67108864b'` two rather than one.
    """
    raw = (raw or "").strip()
    if key in BOOL_KEYS:
        return raw.lower()
    number = numeric_value(key, raw)
    if number is None:
        return raw
    if key in MEMORY_MB_KEYS:
        return f"{round(number)}m"
    # Integer-typed keys must round, not merely render. Averaging three
    # partition counts yields 102.666..., and `spark.sql.shuffle.partitions=
    # 102.66666666666667` is not a value Spark accepts -- emitting it would make
    # a recommendation that cannot even be applied.
    if key in INT_KEYS or key in BYTE_KEYS:
        return str(round(number))
    if number.is_integer():
        return str(int(number))
    return repr(number)


def canonicalise(conf: dict[str, str]) -> dict[str, str]:
    """Canonicalise every value in an observed conf map."""
    return {key: canonical_value(key, value) for key, value in sorted(conf.items())}


def config_identity(conf: dict[str, str]) -> tuple[tuple[str, str], ...]:
    """A hashable identity for a configuration, used to count distinct variants.

    Built from canonical values so that two runs configured identically but
    spelled differently count as ONE variant -- the v0.4 attributability rule
    turns on this count, so an inflated count directly unlocks delta claims that
    should stay suppressed.
    """
    return tuple(sorted(canonicalise(conf).items()))


def zest_columns(conf: dict[str, str]) -> dict[str, int | None]:
    """Extract the ZEST six into their typed run_outcomes columns.

    Every key absent from `conf` maps to None. None means "not captured" and
    must never be rendered as a default -- see this module's header.
    """
    out: dict[str, int | None] = {column: None for column in ZEST_KEY_TO_COLUMN.values()}
    for key, column in ZEST_KEY_TO_COLUMN.items():
        if key in conf:
            value = numeric_value(key, conf[key])
            if value is not None:
                out[column] = int(round(value))
    return out


def pool_configs(configs: list[dict[str, str]]) -> tuple[dict[str, str], dict[str, int]]:
    """Pool several configurations into one recommendation.

    ZEST Algorithm 1 takes the parameter-wise mean of the retrieved neighbours'
    configurations. That is applied verbatim to numeric keys. Booleans have no
    mean, so they are pooled by majority vote; ties resolve to the value that
    sorts first, which makes the result deterministic.

    Returns (pooled_config, key_support) where `key_support` counts how many
    inputs actually carried each key. Support is returned rather than hidden
    because a key set by one contributor out of six is a far weaker
    recommendation than one they all agreed on, and the caller must be able to
    see the difference.
    """
    keys = sorted({key for conf in configs for key in conf})
    pooled: dict[str, str] = {}
    support: dict[str, int] = {}

    for key in keys:
        present = [conf[key] for conf in configs if key in conf]
        support[key] = len(present)
        if not present:
            continue

        if key in NUMERIC_KEYS:
            numbers = [n for raw in present if (n := numeric_value(key, raw)) is not None]
            if numbers:
                pooled[key] = canonical_value(key, str(sum(numbers) / len(numbers)))
                continue

        # Categorical / boolean / unparseable: majority vote.
        canonical = [canonical_value(key, raw) for raw in present]
        pooled[key] = max(sorted(set(canonical)), key=canonical.count)

    return pooled, support
