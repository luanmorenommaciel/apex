"""Exercise the packaged Apex MCP server through the official stdio client."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


ROOT = Path(__file__).resolve().parents[1]
BEFORE_JOB_ID = "codex-mcp-before-20260722"
AFTER_JOB_ID = "codex-mcp-after-20260722"


async def main() -> None:
    environment = {
        **os.environ,
        "CLICKHOUSE_HOST": os.getenv("CLICKHOUSE_HOST", "127.0.0.1"),
        "CLICKHOUSE_PORT": os.getenv("CLICKHOUSE_PORT", "8123"),
        "CLICKHOUSE_USER": os.getenv("CLICKHOUSE_USER", "apex"),
        "CLICKHOUSE_PASSWORD": os.getenv("CLICKHOUSE_PASSWORD", "apex_local_dev"),
        "CLICKHOUSE_DATABASE": os.getenv("CLICKHOUSE_DATABASE", "apex"),
    }
    parameters = StdioServerParameters(
        command="uv",
        args=["run", "apex-mcp"],
        env=environment,
        cwd=ROOT,
    )
    async with stdio_client(parameters) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            tools = await session.list_tools()
            tool_metadata = [
                {
                    "name": tool.name,
                    "readOnlyHint": tool.annotations.readOnlyHint if tool.annotations else None,
                    "openWorldHint": tool.annotations.openWorldHint if tool.annotations else None,
                }
                for tool in tools.tools
            ]
            assert tool_metadata == [
                {"name": "analyze_run", "readOnlyHint": True, "openWorldHint": False},
                {"name": "compare_runs", "readOnlyHint": True, "openWorldHint": False},
            ]
            diagnosis = await session.call_tool("analyze_run", {"job_id": BEFORE_JOB_ID})
            comparison = await session.call_tool(
                "compare_runs",
                {"baseline_job_id": BEFORE_JOB_ID, "current_job_id": AFTER_JOB_ID},
            )
            assert not diagnosis.isError
            assert not comparison.isError
            print(json.dumps({
                "gate": "C2-stdio",
                "tools": tool_metadata,
                "analyze_run": [item.model_dump(mode="json") for item in diagnosis.content],
                "compare_runs": [item.model_dump(mode="json") for item in comparison.content],
                "status": "passed",
            }, indent=2, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(main())
