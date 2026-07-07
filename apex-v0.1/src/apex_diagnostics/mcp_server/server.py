"""MCP stdio server exposing Spark diagnostics (design D-006).

Register with Claude Code (PYTHONPATH=src is required; the project uses a
src layout without installing itself as a package):
    claude mcp add spark-diagnostics --env PYTHONPATH=src -- \
        uv run --directory <repo> python -m apex_diagnostics.mcp_server

Deterministic tools (list_runs, detect_*, get_report) never call an LLM;
analyze_run runs the full pipeline and degrades to detectors-only without one.
"""

from functools import lru_cache
from typing import Any

from mcp.server.fastmcp import FastMCP

from apex_diagnostics import detectors
from apex_diagnostics.clickhouse import ClickHouseConnectClient
from apex_diagnostics.config import DiagnosticsThresholds, load_thresholds
from apex_diagnostics.crew.pipeline import analyze
from apex_diagnostics.reports import store

mcp = FastMCP("spark-diagnostics")


@lru_cache(maxsize=1)
def _client() -> ClickHouseConnectClient:
    return ClickHouseConnectClient()


@lru_cache(maxsize=1)
def _thresholds() -> DiagnosticsThresholds:
    return load_thresholds()


@mcp.tool()
def list_runs(limit: int = 20) -> list[dict[str, Any]]:
    """List recent Spark application runs with their stored-report counts."""
    return store.list_runs(_client(), limit)


@mcp.tool()
def detect_skew(app_id: str) -> list[dict[str, Any]]:
    """Deterministic per-stage task-skew findings for a Spark application (no LLM)."""
    return [f.model_dump() for f in detectors.detect_skew(_client(), app_id, _thresholds().skew)]


@mcp.tool()
def detect_shuffle(app_id: str) -> list[dict[str, Any]]:
    """Deterministic per-stage shuffle/spill/GC findings for a Spark application (no LLM)."""
    return [f.model_dump() for f in detectors.detect_shuffle(_client(), app_id, _thresholds().shuffle)]


@mcp.tool()
def detect_plans(app_id: str) -> list[dict[str, Any]]:
    """Deterministic AQE plan-update and plan-antipattern findings per SQL execution (no LLM)."""
    return [f.model_dump() for f in detectors.detect_plans(_client(), app_id, _thresholds().plans)]


@mcp.tool()
def detect_gc(app_id: str) -> list[dict[str, Any]]:
    """Deterministic GC-pressure findings per stage (no LLM)."""
    return [f.model_dump() for f in detectors.detect_gc(_client(), app_id, _thresholds().gc)]


@mcp.tool()
def detect_oom(app_id: str) -> list[dict[str, Any]]:
    """Deterministic OOM / lost-executor classification of failed tasks (no LLM)."""
    return [f.model_dump() for f in detectors.detect_oom(_client(), app_id)]


@mcp.tool()
def get_report(app_id: str) -> dict[str, Any]:
    """Latest stored diagnostic report for a Spark application."""
    report = store.get_report(_client(), app_id)
    if report is None:
        return {"app_id": app_id, "error": "no stored report; call analyze_run first"}
    return report.model_dump()


@mcp.tool()
def analyze_run(app_id: str) -> dict[str, Any]:
    """Full pipeline: detectors -> Crew A -> stored report. Degrades to detectors-only without an LLM."""
    report = analyze(app_id, _client(), _thresholds())
    report_uid = store.save_report(_client(), report)
    payload = report.model_dump()
    payload["report_uid"] = report_uid
    return payload


if __name__ == "__main__":
    mcp.run()
