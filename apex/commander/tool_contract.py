"""Local Commander tool contract, ready to be wrapped by MCP later."""

from copy import deepcopy

from apex.commander.apply_verify import (
    apply_fix,
    apply_recommendation,
    verify_recommendation_apply,
)
from apex.commander.baselines import evaluate_negative_baseline
from apex.commander.fix_preview import build_fix_preview
from apex.commander.mcp_contract import (
    debug_job,
    explain_evidence,
    query_persisted_findings,
)
from apex.commander.recommendations import (
    preview_recommendation,
    recommend_fix,
)
from apex.commander.rerun_orchestrator import (
    DEFAULT_TIMEOUT_SECONDS,
    execute_rerun_and_compare,
    execute_rerun_poll_and_compare,
    plan_rerun,
)
from apex.commander.spark_rerun_template import (
    DEFAULT_LISTENER_CLASS,
    DEFAULT_MASTER,
    DEFAULT_SPARK_SUBMIT,
    build_spark_submit_rerun_command,
)
from apex.commander.telemetry_compare import compare_job_telemetry
from apex.commander.telemetry_polling import (
    DEFAULT_POLL_ATTEMPTS,
    DEFAULT_POLL_INTERVAL_SECONDS,
    poll_for_telemetry,
)

TOOL_SPECS = [
    {
        "name": "debug_job",
        "description": "Return validated Commander findings for one job_id.",
        "safety": "read_only",
        "input_schema": {
            "type": "object",
            "required": ["job_id"],
            "properties": {"job_id": {"type": "string"}},
        },
    },
    {
        "name": "explain_evidence",
        "description": "Return latest stored telemetry evidence for one job_id.",
        "safety": "read_only",
        "input_schema": {
            "type": "object",
            "required": ["job_id"],
            "properties": {"job_id": {"type": "string"}},
        },
    },
    {
        "name": "evaluate_negative_baseline",
        "description": "Evaluate whether a job unexpectedly triggers Commander findings.",
        "safety": "read_only",
        "input_schema": {
            "type": "object",
            "required": ["job_id"],
            "properties": {"job_id": {"type": "string"}},
        },
    },
    {
        "name": "query_persisted_findings",
        "description": "Return validated findings already persisted for one job_id.",
        "safety": "read_only",
        "input_schema": {
            "type": "object",
            "required": ["job_id"],
            "properties": {"job_id": {"type": "string"}},
        },
    },
    {
        "name": "recommend_fix",
        "description": "Return deterministic recommendations from persisted findings.",
        "safety": "read_only",
        "input_schema": {
            "type": "object",
            "required": ["job_id"],
            "properties": {"job_id": {"type": "string"}},
        },
    },
    {
        "name": "preview_recommendation",
        "description": "Return a diff preview for a selected recommendation without modifying files.",
        "safety": "read_only",
        "input_schema": {
            "type": "object",
            "required": ["job_id", "recommendation_id", "path", "replacement"],
            "properties": {
                "job_id": {"type": "string"},
                "recommendation_id": {"type": "string"},
                "path": {"type": "string"},
                "replacement": {"type": "string"},
            },
        },
    },
    {
        "name": "apply_recommendation",
        "description": "Deprecated compatibility alias for apply_fix.",
        "safety": "guarded_mutation",
        "input_schema": {
            "type": "object",
            "required": [
                "job_id",
                "recommendation_id",
                "path",
                "replacement",
                "approval_token",
            ],
            "properties": {
                "job_id": {"type": "string"},
                "recommendation_id": {"type": "string"},
                "path": {"type": "string"},
                "replacement": {"type": "string"},
                "approval_token": {"type": "string"},
            },
        },
    },
    {
        "name": "apply_fix",
        "description": "Apply a selected fix only with a matching approval token.",
        "safety": "guarded_mutation",
        "input_schema": {
            "type": "object",
            "required": [
                "job_id",
                "recommendation_id",
                "path",
                "replacement",
                "approval_token",
            ],
            "properties": {
                "job_id": {"type": "string"},
                "recommendation_id": {"type": "string"},
                "path": {"type": "string"},
                "replacement": {"type": "string"},
                "approval_token": {"type": "string"},
            },
        },
    },
    {
        "name": "verify_recommendation_apply",
        "description": "Verify a target file hash after a guarded recommendation apply.",
        "safety": "read_only",
        "input_schema": {
            "type": "object",
            "required": ["path", "expected_sha256"],
            "properties": {
                "path": {"type": "string"},
                "expected_sha256": {"type": "string"},
            },
        },
    },
    {
        "name": "compare_job_telemetry",
        "description": "Compare before/after Commander telemetry for two job ids.",
        "safety": "read_only",
        "input_schema": {
            "type": "object",
            "required": ["before_job_id", "after_job_id"],
            "properties": {
                "before_job_id": {"type": "string"},
                "after_job_id": {"type": "string"},
            },
        },
    },
    {
        "name": "build_spark_submit_rerun_command",
        "description": "Build a canonical spark-submit command for a telemetry rerun.",
        "safety": "read_only",
        "input_schema": {
            "type": "object",
            "required": ["app_path", "after_job_id"],
            "properties": {
                "app_path": {"type": "string"},
                "after_job_id": {"type": "string"},
                "spark_submit": {"type": "string"},
                "master": {"type": "string"},
                "app_args": {"type": "array", "items": {"type": "string"}},
                "conf": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                },
                "listener_class": {"type": "string"},
            },
        },
    },
    {
        "name": "poll_telemetry",
        "description": "Wait until telemetry for one job_id is visible in the store.",
        "safety": "read_only",
        "input_schema": {
            "type": "object",
            "required": ["job_id"],
            "properties": {
                "job_id": {"type": "string"},
                "attempts": {"type": "integer"},
                "interval_seconds": {"type": "number"},
            },
        },
    },
    {
        "name": "plan_rerun",
        "description": "Create an approval-token-bound plan for an allowed rerun command.",
        "safety": "read_only",
        "input_schema": {
            "type": "object",
            "required": ["before_job_id", "after_job_id", "command"],
            "properties": {
                "before_job_id": {"type": "string"},
                "after_job_id": {"type": "string"},
                "command": {"type": "array", "items": {"type": "string"}},
                "cwd": {"type": "string"},
                "timeout_seconds": {"type": "integer"},
            },
        },
    },
    {
        "name": "execute_rerun_and_compare",
        "description": "Run an approved rerun command and compare before/after telemetry.",
        "safety": "guarded_mutation",
        "input_schema": {
            "type": "object",
            "required": ["before_job_id", "after_job_id", "command", "approval_token"],
            "properties": {
                "before_job_id": {"type": "string"},
                "after_job_id": {"type": "string"},
                "command": {"type": "array", "items": {"type": "string"}},
                "approval_token": {"type": "string"},
                "cwd": {"type": "string"},
                "timeout_seconds": {"type": "integer"},
            },
        },
    },
    {
        "name": "execute_rerun_poll_and_compare",
        "description": (
            "Run an approved rerun command, wait for after telemetry, and compare."
        ),
        "safety": "guarded_mutation",
        "input_schema": {
            "type": "object",
            "required": ["before_job_id", "after_job_id", "command", "approval_token"],
            "properties": {
                "before_job_id": {"type": "string"},
                "after_job_id": {"type": "string"},
                "command": {"type": "array", "items": {"type": "string"}},
                "approval_token": {"type": "string"},
                "cwd": {"type": "string"},
                "timeout_seconds": {"type": "integer"},
                "poll_attempts": {"type": "integer"},
                "poll_interval_seconds": {"type": "number"},
            },
        },
    },
    {
        "name": "preview_fix",
        "description": "Return a unified diff preview without modifying the target file.",
        "safety": "read_only",
        "input_schema": {
            "type": "object",
            "required": ["path", "recommendation", "replacement"],
            "properties": {
                "path": {"type": "string"},
                "recommendation": {"type": "string"},
                "replacement": {"type": "string"},
            },
        },
    },
]


def list_tools():
    return deepcopy(TOOL_SPECS)


class CommanderToolContract:
    def __init__(
        self,
        store,
        *,
        finding_store=None,
        apply_root=None,
        rerun_root=None,
        rerun_allowed_command_prefixes=None,
        rerun_runner=None,
        telemetry_poll_sleeper=None,
    ):
        self.store = store
        self.finding_store = finding_store
        self.apply_root = apply_root
        self.rerun_root = rerun_root
        self.rerun_allowed_command_prefixes = rerun_allowed_command_prefixes
        self.rerun_runner = rerun_runner
        self.telemetry_poll_sleeper = telemetry_poll_sleeper

    def call_tool(self, name, arguments):
        args = arguments or {}
        if name == "debug_job":
            return debug_job(self.store, _required(args, "job_id"))
        if name == "explain_evidence":
            return explain_evidence(self.store, _required(args, "job_id"))
        if name == "evaluate_negative_baseline":
            return evaluate_negative_baseline(self.store, _required(args, "job_id"))
        if name == "query_persisted_findings":
            return query_persisted_findings(
                self.finding_store,
                _required(args, "job_id"),
            )
        if name == "recommend_fix":
            return recommend_fix(self.finding_store, _required(args, "job_id"))
        if name == "preview_recommendation":
            return preview_recommendation(
                self.finding_store,
                _required(args, "job_id"),
                _required(args, "recommendation_id"),
                _required(args, "path"),
                _required(args, "replacement"),
            )
        if name == "apply_recommendation":
            return apply_recommendation(
                self.finding_store,
                _required(args, "job_id"),
                _required(args, "recommendation_id"),
                _required(args, "path"),
                _required(args, "replacement"),
                _required(args, "approval_token"),
                apply_root=self.apply_root,
            )
        if name == "apply_fix":
            return apply_fix(
                self.finding_store,
                _required(args, "job_id"),
                _required(args, "recommendation_id"),
                _required(args, "path"),
                _required(args, "replacement"),
                _required(args, "approval_token"),
                apply_root=self.apply_root,
            )
        if name == "verify_recommendation_apply":
            return verify_recommendation_apply(
                _required(args, "path"),
                _required(args, "expected_sha256"),
                apply_root=self.apply_root,
            )
        if name == "compare_job_telemetry":
            return compare_job_telemetry(
                self.store,
                _required(args, "before_job_id"),
                _required(args, "after_job_id"),
            )
        if name == "build_spark_submit_rerun_command":
            return build_spark_submit_rerun_command(
                app_path=_required(args, "app_path"),
                after_job_id=_required(args, "after_job_id"),
                spark_submit=args.get("spark_submit", DEFAULT_SPARK_SUBMIT),
                master=args.get("master", DEFAULT_MASTER),
                app_args=args.get("app_args"),
                conf=args.get("conf"),
                listener_class=args.get("listener_class", DEFAULT_LISTENER_CLASS),
                rerun_root=self.rerun_root,
            )
        if name == "poll_telemetry":
            return poll_for_telemetry(
                self.store,
                _required(args, "job_id"),
                attempts=args.get("attempts", DEFAULT_POLL_ATTEMPTS),
                interval_seconds=args.get(
                    "interval_seconds",
                    DEFAULT_POLL_INTERVAL_SECONDS,
                ),
                sleeper=self.telemetry_poll_sleeper,
            )
        if name == "plan_rerun":
            return plan_rerun(
                _required(args, "before_job_id"),
                _required(args, "after_job_id"),
                _required(args, "command"),
                cwd=args.get("cwd", "."),
                timeout_seconds=args.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS),
                rerun_root=self.rerun_root,
                allowed_command_prefixes=self.rerun_allowed_command_prefixes,
            )
        if name == "execute_rerun_and_compare":
            return execute_rerun_and_compare(
                self.store,
                _required(args, "before_job_id"),
                _required(args, "after_job_id"),
                _required(args, "command"),
                _required(args, "approval_token"),
                cwd=args.get("cwd", "."),
                timeout_seconds=args.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS),
                rerun_root=self.rerun_root,
                allowed_command_prefixes=self.rerun_allowed_command_prefixes,
                runner=self.rerun_runner,
            )
        if name == "execute_rerun_poll_and_compare":
            return execute_rerun_poll_and_compare(
                self.store,
                _required(args, "before_job_id"),
                _required(args, "after_job_id"),
                _required(args, "command"),
                _required(args, "approval_token"),
                cwd=args.get("cwd", "."),
                timeout_seconds=args.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS),
                rerun_root=self.rerun_root,
                allowed_command_prefixes=self.rerun_allowed_command_prefixes,
                runner=self.rerun_runner,
                poll_attempts=args.get("poll_attempts", DEFAULT_POLL_ATTEMPTS),
                poll_interval_seconds=args.get(
                    "poll_interval_seconds",
                    DEFAULT_POLL_INTERVAL_SECONDS,
                ),
                poll_sleeper=self.telemetry_poll_sleeper,
            )
        if name == "preview_fix":
            return build_fix_preview(
                _required(args, "path"),
                _required(args, "recommendation"),
                replacement=_required(args, "replacement"),
            )
        raise ValueError(f"unknown_tool:{name}")


def _required(arguments, key):
    value = arguments.get(key)
    if value in (None, ""):
        raise ValueError(f"missing_argument:{key}")
    return value
