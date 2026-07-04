"""
Apex V1 — MCP Server
Expõe os findings do ClickHouse via Model Context Protocol.

O engenheiro conecta o Claude Code / Cursor a este MCP e pergunta:
  "O que está errado com o job app-20240630-123456?"
  "Quais são os 3 jobs mais lentos esta semana?"

Instalar dependência:
    pip install mcp clickhouse-connect

Rodar:
    python mcp/server.py

Registrar no Claude Code (~/.claude/claude.json):
    {
      "mcpServers": {
        "apex": {
          "command": "python",
          "args": ["/path/to/v1-skeleton/mcp/server.py"]
        }
      }
    }
"""
import os
import json
import logging
from typing import Any

import clickhouse_connect
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("apex.mcp")

CH_HOST     = os.getenv("APEX_CH_HOST", "localhost")
CH_PORT     = int(os.getenv("APEX_CH_PORT", "8123"))
CH_USER     = os.getenv("APEX_CH_USER", "apex")
CH_PASSWORD = os.getenv("APEX_CH_PASSWORD", "apex123")

app = Server("apex-v1")


def get_ch():
    return clickhouse_connect.get_client(
        host=CH_HOST, port=CH_PORT,
        username=CH_USER, password=CH_PASSWORD,
    )


# ── Tools ───────────────────────────────────────────────────────────────────

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_findings",
            description=(
                "Retorna os findings de diagnóstico Apex para um app_id Spark. "
                "Use quando o engenheiro perguntar sobre performance de um job específico."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "app_id": {
                        "type": "string",
                        "description": "Spark application ID (ex: app-20240630-123456)"
                    }
                },
                "required": ["app_id"],
            },
        ),
        Tool(
            name="get_stage_metrics",
            description=(
                "Retorna métricas detalhadas dos stages para um app_id. "
                "Use para investigar qual stage é o bottleneck."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "app_id": {
                        "type": "string",
                        "description": "Spark application ID"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Número máximo de stages (default: 10)",
                        "default": 10,
                    }
                },
                "required": ["app_id"],
            },
        ),
        Tool(
            name="list_slow_apps",
            description=(
                "Lista os jobs Spark mais lentos das últimas 24h. "
                "Use para encontrar onde está o maior problema de performance."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "hours": {
                        "type": "integer",
                        "description": "Janela de tempo em horas (default: 24)",
                        "default": 24,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Top N jobs (default: 10)",
                        "default": 10,
                    }
                },
            },
        ),
        Tool(
            name="trigger_diagnosis",
            description=(
                "Dispara um diagnóstico LLM para um app_id que ainda não foi analisado. "
                "Usa claude-sonnet para gerar o finding e persiste no ClickHouse."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "app_id": {
                        "type": "string",
                        "description": "Spark application ID para diagnosticar"
                    }
                },
                "required": ["app_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    ch = get_ch()

    if name == "get_findings":
        app_id = arguments["app_id"]
        rows = ch.query("""
            SELECT pattern, severity, confidence, root_cause, recommendation, created_at
            FROM apex.findings
            WHERE app_id = {app_id:String}
            ORDER BY created_at DESC
            LIMIT 5
        """, parameters={"app_id": app_id}).named_results()

        results = list(rows)
        if not results:
            return [TextContent(
                type="text",
                text=f"Nenhum finding encontrado para app_id={app_id}. "
                     f"Use trigger_diagnosis para gerar um diagnóstico."
            )]

        return [TextContent(
            type="text",
            text=json.dumps(results, indent=2, default=str)
        )]

    elif name == "get_stage_metrics":
        app_id = arguments["app_id"]
        limit  = arguments.get("limit", 10)

        rows = ch.query("""
            SELECT stage_id, stage_name, num_tasks, duration_ms,
                   input_bytes, disk_spill, memory_spill, shuffle_read
            FROM apex.stage_metrics
            WHERE app_id = {app_id:String}
            ORDER BY duration_ms DESC
            LIMIT {limit:UInt32}
        """, parameters={"app_id": app_id, "limit": limit}).named_results()

        return [TextContent(
            type="text",
            text=json.dumps(list(rows), indent=2, default=str)
        )]

    elif name == "list_slow_apps":
        hours = arguments.get("hours", 24)
        limit = arguments.get("limit", 10)

        rows = ch.query("""
            SELECT app_id,
                   sum(duration_ms) AS total_ms,
                   sum(disk_spill)  AS total_spill,
                   count()          AS num_stages,
                   max(ingested_at) AS last_seen
            FROM apex.stage_metrics
            WHERE ingested_at >= now() - INTERVAL {hours:UInt32} HOUR
            GROUP BY app_id
            ORDER BY total_ms DESC
            LIMIT {limit:UInt32}
        """, parameters={"hours": hours, "limit": limit}).named_results()

        return [TextContent(
            type="text",
            text=json.dumps(list(rows), indent=2, default=str)
        )]

    elif name == "trigger_diagnosis":
        app_id = arguments["app_id"]
        # Chama o módulo de análise
        import subprocess, sys
        result = subprocess.run(
            [sys.executable, "analysis/diagnose.py", "--app-id", app_id],
            capture_output=True, text=True,
        )
        output = result.stdout + result.stderr
        return [TextContent(type="text", text=output)]

    return [TextContent(type="text", text=f"Tool desconhecida: {name}")]


# ── Entry point ─────────────────────────────────────────────────────────────

async def main():
    logger.info("Apex MCP Server iniciando...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
