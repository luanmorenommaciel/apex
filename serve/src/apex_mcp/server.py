"""FastMCP stdio server exposing read-only APEX diagnosis."""

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
