from __future__ import annotations

import sys
from pathlib import Path

DEV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEV))

from common.paths import (  # noqa: E402
    DEFAULT_DIM_PATH,
    DEFAULT_FACT_PATH,
    DEFAULT_META_PATH,
    resolve_dataset_paths,
)


def test_defaults_match_the_shared_warehouse_layout() -> None:
    paths = resolve_dataset_paths({})
    assert paths.fact == DEFAULT_FACT_PATH == "s3a://warehouse/fact"
    assert paths.dim == DEFAULT_DIM_PATH == "s3a://warehouse/dim"
    assert paths.meta == DEFAULT_META_PATH == "s3a://warehouse/_gen_meta"


def test_overrides_move_fact_dim_and_marker_into_the_isolated_dataset() -> None:
    paths = resolve_dataset_paths(
        {
            "APEX_FACT_PATH": "s3a://warehouse/apex-runs/20261019T120000Z-42/fact",
            "APEX_DIM_PATH": "s3a://warehouse/apex-runs/20261019T120000Z-42/dim",
        }
    )
    assert paths.fact == "s3a://warehouse/apex-runs/20261019T120000Z-42/fact"
    assert paths.dim == "s3a://warehouse/apex-runs/20261019T120000Z-42/dim"
    # The marker must NOT stay at the default location, otherwise a stale
    # default marker could make ensure_data skip the isolated generation.
    assert paths.meta == "s3a://warehouse/apex-runs/20261019T120000Z-42/_gen_meta"
    assert paths.meta != DEFAULT_META_PATH


def test_explicit_meta_override_wins() -> None:
    paths = resolve_dataset_paths(
        {
            "APEX_FACT_PATH": "s3a://b/x/fact",
            "APEX_DIM_PATH": "s3a://b/x/dim",
            "APEX_META_PATH": "s3a://b/markers/x",
        }
    )
    assert paths.meta == "s3a://b/markers/x"


def test_blank_values_are_treated_as_unset() -> None:
    paths = resolve_dataset_paths({"APEX_FACT_PATH": "  ", "APEX_DIM_PATH": ""})
    assert paths.fact == DEFAULT_FACT_PATH
    assert paths.dim == DEFAULT_DIM_PATH
    assert paths.meta == DEFAULT_META_PATH


def test_trailing_slash_on_fact_does_not_break_the_sibling_marker() -> None:
    paths = resolve_dataset_paths({"APEX_FACT_PATH": "s3a://b/run1/fact/"})
    assert paths.meta == "s3a://b/run1/_gen_meta"


def test_resolver_reads_the_process_environment_by_default(monkeypatch) -> None:
    monkeypatch.setenv("APEX_FACT_PATH", "s3a://b/env/fact")
    monkeypatch.setenv("APEX_DIM_PATH", "s3a://b/env/dim")
    monkeypatch.delenv("APEX_META_PATH", raising=False)
    paths = resolve_dataset_paths()
    assert paths.fact == "s3a://b/env/fact"
    assert paths.meta == "s3a://b/env/_gen_meta"


def test_common_paths_has_no_pyspark_import() -> None:
    source = (DEV / "common" / "paths.py").read_text(encoding="utf-8")
    assert "import pyspark" not in source and "from pyspark" not in source
