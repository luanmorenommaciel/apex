"""FastMCP stdio server exposing APEX diagnosis and non-applying proposals."""

from __future__ import annotations

import os

import clickhouse_connect
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .service import ApexReadService
from .store import ReadStore


def create_server(service: ApexReadService) -> FastMCP:
    mcp = FastMCP("apex")

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False))
    def analyze_run(job_id: str) -> dict:
        """Return persisted findings and stage telemetry for one APEX job_id."""
        return service.analyze_run(job_id).model_dump(mode="json")

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False))
    def compare_runs(baseline_job_id: str, current_job_id: str) -> dict:
        """Compare two telemetry runs; lower findings, skew and spill are better."""
        return service.compare_runs(baseline_job_id, current_job_id).model_dump(mode="json")

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False))
    def search_kb(query: str, top_k: int = 5) -> dict:
        """Search persisted, redacted finding evidence and remediation notes."""
        return service.search_kb(query, top_k).model_dump(mode="json")

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False))
    def suggest_fix(job_id: str, finding_id: str | None = None, min_confidence: float = 0.75) -> dict:
        """Return a review-only diff and PR body; never writes files, Git, or Spark."""
        return service.suggest_fix(job_id, finding_id, min_confidence).model_dump(mode="json")

    return mcp


def main() -> None:
    client = clickhouse_connect.get_client(
        host=os.environ["CLICKHOUSE_HOST"],
        port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
        username=os.getenv("CLICKHOUSE_USER", "apex"),
        password=os.environ["CLICKHOUSE_PASSWORD"],
        database=os.getenv("CLICKHOUSE_DATABASE", "apex"),
    )
    create_server(ApexReadService(ReadStore(client))).run(transport="stdio")
