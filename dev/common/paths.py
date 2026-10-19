"""Dataset location resolver (pyspark-free, importable on the host).

The pathology jobs read one fact and one dim Delta table plus a generation
marker. By default they live under the shared warehouse bucket. An
orchestrator that needs an ISOLATED dataset (the r9d OFF arm, a calibration
run that must not disturb the shared tables) exports APEX_FACT_PATH and
APEX_DIM_PATH; the marker follows the fact table into the same dataset so a
stale marker from the default dataset can never make `ensure_data` skip the
generation of the isolated one. APEX_META_PATH overrides the marker location
explicitly when needed.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping

DEFAULT_FACT_PATH = "s3a://warehouse/fact"
DEFAULT_DIM_PATH = "s3a://warehouse/dim"
DEFAULT_META_PATH = "s3a://warehouse/_gen_meta"

FACT_ENV = "APEX_FACT_PATH"
DIM_ENV = "APEX_DIM_PATH"
META_ENV = "APEX_META_PATH"


@dataclass(frozen=True)
class DatasetPaths:
    fact: str
    dim: str
    meta: str


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _sibling_marker(fact_path: str) -> str:
    """Marker next to the fact table: s3a://bucket/x/fact -> s3a://bucket/x/_gen_meta."""
    base = fact_path.rstrip("/")
    parent, _, _ = base.rpartition("/")
    return f"{parent}/_gen_meta" if parent else f"{base}/_gen_meta"


def resolve_dataset_paths(env: Mapping[str, str] | None = None) -> DatasetPaths:
    """Resolve fact, dim and marker paths from the environment."""
    source = os.environ if env is None else env
    fact = _clean(source.get(FACT_ENV))
    dim = _clean(source.get(DIM_ENV))
    meta = _clean(source.get(META_ENV))

    if fact is None and dim is None:
        return DatasetPaths(DEFAULT_FACT_PATH, DEFAULT_DIM_PATH, meta or DEFAULT_META_PATH)

    fact_path = fact or DEFAULT_FACT_PATH
    dim_path = dim or DEFAULT_DIM_PATH
    meta_path = meta or _sibling_marker(fact_path)
    return DatasetPaths(fact_path, dim_path, meta_path)
