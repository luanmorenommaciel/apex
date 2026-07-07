import os
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

DEFAULT_ENV = "local"
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "lakehouse.yaml"
_ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(:-([^}]*))?\}")


def load_config(env: str | None = None, config_path: str | Path | None = None) -> dict[str, Any]:
    selected_env = env or os.environ.get("SPARK_PLAT_CONFIG_ENV", DEFAULT_ENV)
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH

    with path.open("r", encoding="utf-8") as file:
        raw_config = yaml.safe_load(file) or {}

    if selected_env != "default" and selected_env not in raw_config:
        raise ValueError(f"Environment '{selected_env}' was not found in {path}")

    config = _deep_merge(raw_config.get("default", {}), raw_config.get(selected_env, {}))
    return _expand_env(config)


def get_entity_layer(config: dict[str, Any], entity_name: str, layer: str) -> dict[str, Any]:
    try:
        return config["entities"][entity_name][layer]
    except KeyError as exc:
        available_entities = sorted(config.get("entities", {}).keys())
        raise KeyError(
            f"Missing layer '{layer}' for entity '{entity_name}'. Available entities: {available_entities}"
        ) from exc


def get_read_config(config: dict[str, Any], entity_name: str, layer: str) -> dict[str, Any]:
    entity_layer = get_entity_layer(config, entity_name, layer)
    try:
        return entity_layer["read"]
    except KeyError as exc:
        raise KeyError(f"Missing read configuration for {layer}.{entity_name}") from exc


def get_write_config(config: dict[str, Any], entity_name: str, layer: str) -> dict[str, Any]:
    entity_layer = get_entity_layer(config, entity_name, layer)
    try:
        return entity_layer["write"]
    except KeyError as exc:
        raise KeyError(f"Missing write configuration for {layer}.{entity_name}") from exc


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _expand_env(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _expand_env(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_expand_env(child) for child in value]
    if isinstance(value, str):
        return _ENV_PATTERN.sub(lambda match: os.environ.get(match.group(1), match.group(3) or ""), value)
    return value
