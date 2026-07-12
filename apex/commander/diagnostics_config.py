"""Diagnostics thresholds sourced from the common package contract."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import yaml


DEFAULT_DIAGNOSTICS = {
    "gc": {
        "warning_ratio": 0.10,
        "critical_ratio": 0.20,
        "min_stage_duration_ms": 5000,
    },
    "shuffle": {
        "warning_shuffle_bytes": 268435456,
        "critical_shuffle_bytes": 1073741824,
        "min_shuffle_bytes": 16777216,
    },
    "plans": {
        "info_replan_count": 3,
    },
    "oom": {},
    "skew": {
        "ratio_min": 10,
        "min_tasks": 4,
    },
    "parallelism": {
        "min_tasks": 4,
        "min_input_bytes": 1073741824,
    },
}


def load_diagnostics_config(path=None):
    """Load the immutable diagnostics contract, with literal fallback values."""
    config_path = Path(path) if path else _default_config_path()
    if not config_path.exists():
        return deepcopy(DEFAULT_DIAGNOSTICS)

    loaded = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return _deep_merge(DEFAULT_DIAGNOSTICS, loaded)


def _default_config_path():
    return Path(__file__).resolve().parents[2] / "pacote-comum" / "diagnostics.yaml"


def _deep_merge(defaults, loaded):
    merged = deepcopy(defaults)
    for key, value in loaded.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key].update(value)
        else:
            merged[key] = value
    return merged
