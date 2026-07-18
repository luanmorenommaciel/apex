"""Canonical Spark submit command templates for Commander reruns."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

DEFAULT_LISTENER_CLASS = "apex.commander.spark.ApexSparkListener"
DEFAULT_LISTENER_JAR = "listener-jvm/build/libs/apex-spark-listener-0.1.0.jar"
DEFAULT_LISTENER_OUTPUT = "/tmp/apex-listener-events.ndjson"
DEFAULT_MASTER = "local[*]"
DEFAULT_SPARK_SUBMIT = "spark-submit"
RULE_SET = "apex.commander.spark_rerun_template.v1"


def build_spark_submit_rerun_command(
    *,
    app_path: str,
    after_job_id: str,
    spark_submit: str = DEFAULT_SPARK_SUBMIT,
    master: str = DEFAULT_MASTER,
    app_args: Sequence[str] | None = None,
    conf: Mapping[str, str] | None = None,
    listener_class: str = DEFAULT_LISTENER_CLASS,
    listener_jar: str | None = DEFAULT_LISTENER_JAR,
    listener_output: str = DEFAULT_LISTENER_OUTPUT,
    rerun_root: str | None = None,
) -> dict[str, Any]:
    """Build a shell-free Spark command that emits Commander telemetry."""

    invalid = _validate_non_empty(
        {
            "app_path": app_path,
            "after_job_id": after_job_id,
            "spark_submit": spark_submit,
            "master": master,
            "listener_class": listener_class,
            "listener_output": listener_output,
        }
    )
    if invalid:
        return invalid

    app_target = _resolve_app_path(app_path, rerun_root)
    if isinstance(app_target, dict):
        return app_target

    extra_args = _validate_args(app_args or [])
    if isinstance(extra_args, dict):
        return extra_args

    extra_conf, conf_error = _validate_conf(conf or {})
    if conf_error:
        return conf_error

    effective_conf = {
        **extra_conf,
        "spark.extraListeners": listener_class,
        "spark.apex.jobId": after_job_id,
        "spark.apex.listener.output": listener_output,
        "spark.apex.listener.failMode": "false",
    }

    command = [spark_submit, "--master", master]
    if listener_jar is not None:
        listener_jar = _validate_listener_jar(listener_jar)
        if isinstance(listener_jar, dict):
            return listener_jar
        command.extend(["--jars", listener_jar])
    for key in sorted(effective_conf):
        command.extend(["--conf", f"{key}={effective_conf[key]}"])
    command.append(str(app_target))
    command.extend(extra_args)

    return {
        "status": "planned",
        "rule_set": RULE_SET,
        "command": command,
        "after_job_id": after_job_id,
        "app_path": str(app_target),
        "spark_submit": spark_submit,
        "master": master,
        "conf": effective_conf,
        "app_args": extra_args,
        "listener_jar": listener_jar,
        "listener_output": listener_output,
    }


def _validate_non_empty(values: Mapping[str, str]) -> dict[str, Any] | None:
    for name, value in values.items():
        if not isinstance(value, str) or not value.strip():
            return {
                "status": "invalid_spark_template",
                "rule_set": RULE_SET,
                "reason": f"{name} must be a non-empty string",
            }
    return None


def _resolve_app_path(app_path: str, rerun_root: str | None) -> Path | dict[str, Any]:
    root = Path(rerun_root).resolve() if rerun_root else None
    target = Path(app_path)
    if not target.is_absolute() and root is not None:
        target = root / target
    target = target.resolve()

    if root is not None and not _is_relative_to(target, root):
        return {
            "status": "app_path_outside_rerun_root",
            "rule_set": RULE_SET,
            "reason": f"app_path must stay under rerun_root: {root}",
        }
    if not target.exists() or not target.is_file():
        return {
            "status": "app_path_not_found",
            "rule_set": RULE_SET,
            "reason": f"app_path was not found: {target}",
        }
    return target


def _validate_args(values: Iterable[str]) -> list[str] | dict[str, Any]:
    args = list(values)
    if any(not isinstance(value, str) or not value for value in args):
        return {
            "status": "invalid_spark_template_args",
            "rule_set": RULE_SET,
            "reason": "app_args must contain only non-empty strings",
        }
    return args


def _validate_listener_jar(value: str) -> str | dict[str, Any]:
    if not isinstance(value, str) or not value.strip():
        return {
            "status": "invalid_spark_template_listener_jar",
            "rule_set": RULE_SET,
            "reason": "listener_jar must be a non-empty string or null",
        }
    return value


def _validate_conf(
    values: Mapping[str, str],
) -> tuple[dict[str, str] | None, dict[str, Any] | None]:
    if not isinstance(values, Mapping):
        return None, {
            "status": "invalid_spark_template_conf",
            "rule_set": RULE_SET,
            "reason": "conf must be an object",
        }

    normalized: dict[str, str] = {}
    for key, value in values.items():
        if not isinstance(key, str) or not key.strip():
            return None, {
                "status": "invalid_spark_template_conf",
                "rule_set": RULE_SET,
                "reason": "conf keys must be non-empty strings",
            }
        if not isinstance(value, str) or not value:
            return None, {
                "status": "invalid_spark_template_conf",
                "rule_set": RULE_SET,
                "reason": "conf values must be non-empty strings",
            }
        normalized[key] = value
    return normalized, None


def _is_relative_to(target: Path, root: Path) -> bool:
    try:
        target.relative_to(root)
    except ValueError:
        return False
    return True
