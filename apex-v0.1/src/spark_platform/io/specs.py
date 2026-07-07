from dataclasses import dataclass, field
from typing import Any, Mapping

READ_FORMATS = frozenset({"delta", "json"})
WRITE_FORMATS = frozenset({"delta", "json"})


@dataclass(frozen=True)
class ReadSpec:
    format: str
    path: str
    options: Mapping[str, Any] = field(default_factory=dict)
    # Optional Spark DDL schema string (e.g. "id BIGINT, name STRING"). When set,
    # it is applied on read instead of letting Spark infer — this avoids the
    # extra inference pass and silent type/column drift on JSON landing data.
    schema: str | None = None

    @classmethod
    def from_mapping(cls, config: Mapping[str, Any]) -> "ReadSpec":
        dataset_format = str(config.get("format", "delta")).lower()
        path = str(config.get("path", ""))
        options = config.get("options") or {}
        schema = config.get("schema")

        if dataset_format not in READ_FORMATS:
            raise ValueError(f"Unsupported read format '{dataset_format}'. Expected one of {sorted(READ_FORMATS)}")
        if not path:
            raise ValueError("Read configuration requires a path")
        if not isinstance(options, Mapping):
            raise ValueError("Read options must be a mapping")

        return cls(
            format=dataset_format,
            path=path,
            options=dict(options),
            schema=str(schema) if schema else None,
        )


@dataclass(frozen=True)
class WriteSpec:
    format: str
    path: str
    mode: str = "errorifexists"
    options: Mapping[str, Any] = field(default_factory=dict)
    partition_by: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, config: Mapping[str, Any]) -> "WriteSpec":
        dataset_format = str(config.get("format", "delta")).lower()
        path = str(config.get("path", ""))
        mode = str(config.get("mode", "errorifexists"))
        options = config.get("options") or {}
        partition_by = _normalize_partition_by(config.get("partition_by"))

        if dataset_format not in WRITE_FORMATS:
            raise ValueError(f"Unsupported write format '{dataset_format}'. Expected one of {sorted(WRITE_FORMATS)}")
        if not path:
            raise ValueError("Write configuration requires a path")
        if not isinstance(options, Mapping):
            raise ValueError("Write options must be a mapping")

        return cls(
            format=dataset_format,
            path=path,
            mode=mode,
            options=dict(options),
            partition_by=partition_by,
        )


def ensure_read_spec(config: Mapping[str, Any] | ReadSpec) -> ReadSpec:
    if isinstance(config, ReadSpec):
        return config
    return ReadSpec.from_mapping(config)


def ensure_write_spec(config: Mapping[str, Any] | WriteSpec) -> WriteSpec:
    if isinstance(config, WriteSpec):
        return config
    return WriteSpec.from_mapping(config)


def option_value(value: Any) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _normalize_partition_by(value: Any) -> tuple[str, ...]:
    if value is None or value == "":
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(str(item) for item in value)
