"""Guarded rerun orchestration for Commander telemetry comparison."""

import json
import subprocess
from hashlib import sha256
from pathlib import Path

from apex.commander.telemetry_compare import compare_job_telemetry
from apex.commander.telemetry_polling import (
    DEFAULT_POLL_ATTEMPTS,
    DEFAULT_POLL_INTERVAL_SECONDS,
    poll_for_telemetry,
    validate_poll_settings,
)

RULE_SET = "apex.commander.rerun_orchestrator.v1"
DEFAULT_TIMEOUT_SECONDS = 300
MAX_TIMEOUT_SECONDS = 3600
OUTPUT_LIMIT = 4000


class SubprocessRerunRunner:
    """Run an approved command without shell expansion."""

    def run(self, command, cwd, timeout_seconds):
        try:
            completed = subprocess.run(
                command,
                cwd=str(cwd),
                timeout=timeout_seconds,
                capture_output=True,
                text=True,
                shell=False,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return {
                "status": "timed_out",
                "exit_code": None,
                "timed_out": True,
                "stdout": _limit_output(exc.stdout or ""),
                "stderr": _limit_output(exc.stderr or ""),
            }

        return {
            "status": "succeeded" if completed.returncode == 0 else "failed",
            "exit_code": completed.returncode,
            "timed_out": False,
            "stdout": _limit_output(completed.stdout or ""),
            "stderr": _limit_output(completed.stderr or ""),
        }


def plan_rerun(
    before_job_id,
    after_job_id,
    command,
    *,
    cwd=".",
    timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
    rerun_root=None,
    allowed_command_prefixes=None,
):
    """Build an approval-token-bound rerun plan."""
    validation = _validate_rerun_request(
        command,
        cwd,
        timeout_seconds,
        rerun_root,
        allowed_command_prefixes,
    )
    if validation["status"] != "ok":
        return {
            "rule_set": RULE_SET,
            "status": validation["status"],
            "runnable": False,
            "before_job_id": before_job_id,
            "after_job_id": after_job_id,
            "command": list(command) if isinstance(command, list) else command,
            "cwd": str(cwd),
            "timeout_seconds": timeout_seconds,
            "approval": {"required": True, "token": ""},
        }

    plan = {
        "rule_set": RULE_SET,
        "status": "planned",
        "runnable": True,
        "before_job_id": before_job_id,
        "after_job_id": after_job_id,
        "command": list(command),
        "cwd": str(validation["cwd"]),
        "timeout_seconds": int(timeout_seconds),
        "command_sha256": _sha256_json(list(command)),
    }
    plan["approval"] = {
        "required": True,
        "token": approval_token_from_plan(plan),
        "token_scope": "before_job_id+after_job_id+command+cwd+timeout_seconds",
    }
    return plan


def execute_rerun_and_compare(
    store,
    before_job_id,
    after_job_id,
    command,
    approval_token,
    *,
    cwd=".",
    timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
    rerun_root=None,
    allowed_command_prefixes=None,
    runner=None,
):
    """Run an approved rerun command and compare before/after telemetry."""
    plan = plan_rerun(
        before_job_id,
        after_job_id,
        command,
        cwd=cwd,
        timeout_seconds=timeout_seconds,
        rerun_root=rerun_root,
        allowed_command_prefixes=allowed_command_prefixes,
    )
    if plan["status"] != "planned":
        return _blocked_execution(plan, plan["status"])

    expected_token = plan["approval"]["token"]
    if approval_token != expected_token:
        return _blocked_execution(plan, "invalid_approval_token")

    selected_runner = runner or SubprocessRerunRunner()
    runner_result = selected_runner.run(
        plan["command"],
        Path(plan["cwd"]),
        plan["timeout_seconds"],
    )
    if runner_result["status"] == "timed_out":
        return _execution_result(plan, "rerun_timed_out", runner_result)
    if runner_result["exit_code"] != 0:
        return _execution_result(plan, "rerun_failed", runner_result)

    comparison = compare_job_telemetry(store, before_job_id, after_job_id)
    return _execution_result(
        plan,
        "rerun_completed",
        runner_result,
        comparison=comparison,
    )


def execute_rerun_poll_and_compare(
    store,
    before_job_id,
    after_job_id,
    command,
    approval_token,
    *,
    cwd=".",
    timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
    rerun_root=None,
    allowed_command_prefixes=None,
    runner=None,
    poll_attempts=DEFAULT_POLL_ATTEMPTS,
    poll_interval_seconds=DEFAULT_POLL_INTERVAL_SECONDS,
    poll_sleeper=None,
):
    """Run an approved command, wait for after telemetry, then compare."""
    plan = plan_rerun(
        before_job_id,
        after_job_id,
        command,
        cwd=cwd,
        timeout_seconds=timeout_seconds,
        rerun_root=rerun_root,
        allowed_command_prefixes=allowed_command_prefixes,
    )
    if plan["status"] != "planned":
        return _blocked_execution(plan, plan["status"], telemetry={"status": "not_run"})

    poll_validation = validate_poll_settings(poll_attempts, poll_interval_seconds)
    if poll_validation["status"] != "ok":
        return _blocked_execution(
            plan,
            poll_validation["status"],
            telemetry=poll_validation,
        )

    expected_token = plan["approval"]["token"]
    if approval_token != expected_token:
        return _blocked_execution(
            plan,
            "invalid_approval_token",
            telemetry={"status": "not_run"},
        )

    selected_runner = runner or SubprocessRerunRunner()
    runner_result = selected_runner.run(
        plan["command"],
        Path(plan["cwd"]),
        plan["timeout_seconds"],
    )
    if runner_result["status"] == "timed_out":
        return _execution_result(
            plan,
            "rerun_timed_out",
            runner_result,
            telemetry={"status": "not_run"},
        )
    if runner_result["exit_code"] != 0:
        return _execution_result(
            plan,
            "rerun_failed",
            runner_result,
            telemetry={"status": "not_run"},
        )

    telemetry = poll_for_telemetry(
        store,
        after_job_id,
        attempts=poll_validation["attempts"],
        interval_seconds=poll_validation["interval_seconds"],
        sleeper=poll_sleeper,
    )
    if telemetry["status"] != "found":
        return _execution_result(
            plan,
            "telemetry_not_available",
            runner_result,
            comparison={"status": "not_run"},
            telemetry=telemetry,
        )

    comparison = compare_job_telemetry(store, before_job_id, after_job_id)
    return _execution_result(
        plan,
        "rerun_completed",
        runner_result,
        comparison=comparison,
        telemetry=telemetry,
    )


def approval_token_from_plan(plan):
    payload = {
        "before_job_id": plan["before_job_id"],
        "after_job_id": plan["after_job_id"],
        "command": plan["command"],
        "cwd": plan["cwd"],
        "timeout_seconds": plan["timeout_seconds"],
    }
    return _sha256_json(payload)


def _validate_rerun_request(
    command,
    cwd,
    timeout_seconds,
    rerun_root,
    allowed_command_prefixes,
):
    if rerun_root is None:
        return {"status": "rerun_root_not_configured"}
    if not _valid_command(command):
        return {"status": "invalid_command"}
    if not _valid_timeout(timeout_seconds):
        return {"status": "invalid_timeout"}
    if not _command_allowed(command, allowed_command_prefixes):
        return {"status": "command_not_allowed"}

    root = Path(rerun_root).resolve()
    selected_cwd = _resolve_cwd(cwd, root)
    if not _is_relative_to(selected_cwd, root):
        return {"status": "outside_rerun_root"}
    if not selected_cwd.exists() or not selected_cwd.is_dir():
        return {"status": "cwd_not_found"}
    return {"status": "ok", "cwd": selected_cwd}


def _valid_command(command):
    return (
        isinstance(command, list)
        and len(command) > 0
        and all(isinstance(part, str) and part for part in command)
    )


def _valid_timeout(timeout_seconds):
    try:
        value = int(timeout_seconds)
    except (TypeError, ValueError):
        return False
    return 0 < value <= MAX_TIMEOUT_SECONDS


def _command_allowed(command, allowed_command_prefixes):
    if not allowed_command_prefixes:
        return False
    for prefix in allowed_command_prefixes:
        prefix_list = list(prefix)
        if command[: len(prefix_list)] == prefix_list:
            return True
    return False


def _resolve_cwd(cwd, root):
    candidate = Path(cwd)
    if candidate.is_absolute():
        return candidate.resolve()
    return (root / candidate).resolve()


def _is_relative_to(path, root):
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _blocked_execution(plan, status, *, telemetry=None):
    result = {
        "rule_set": RULE_SET,
        "status": status,
        "plan": plan,
        "runner": {"status": "not_run"},
        "comparison": {"status": "not_run"},
    }
    if telemetry is not None:
        result["telemetry"] = telemetry
    return result


def _execution_result(plan, status, runner_result, *, comparison=None, telemetry=None):
    result = {
        "rule_set": RULE_SET,
        "status": status,
        "plan": plan,
        "runner": runner_result,
        "comparison": comparison or {"status": "not_run"},
    }
    if telemetry is not None:
        result["telemetry"] = telemetry
    return result


def _limit_output(value):
    if not isinstance(value, str):
        value = value.decode("utf-8", errors="replace")
    if len(value) <= OUTPUT_LIMIT:
        return value
    return value[:OUTPUT_LIMIT] + "...<truncated>"


def _sha256_json(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8")).hexdigest()
