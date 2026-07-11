"""Local Commander tool contract, ready to be wrapped by MCP later."""

from copy import deepcopy

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
    def __init__(self, store, *, finding_store=None):
        self.store = store
        self.finding_store = finding_store

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
