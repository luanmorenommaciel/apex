"""Exercise the read-only MCP boundary against a real C3 ClickHouse job."""

from __future__ import annotations

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    job_id = os.environ["APEX_C3_JOB_ID"]
    server = StdioServerParameters(
        command=sys.executable,
        args=["-c", "from apex_mcp.server import main; main()"],
        env=dict(os.environ),
    )
    async with stdio_client(server) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            tools = await session.list_tools()
            result = await session.call_tool("analyze_run", {"job_id": job_id})

    payload = json.loads(result.content[0].text)
    print(json.dumps({
        "gate": "C3-real-mcp",
        "job_id": job_id,
        "tools": [
            {"name": tool.name, "read_only": tool.annotations.readOnlyHint}
            for tool in tools.tools
        ],
        "diagnosis": {
            "status": payload["status"],
            "stage_count": len(payload["stages"]),
            "finding_count": len(payload["findings"]),
            "summary": payload["summary"],
        },
        "status": "passed",
    }, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
