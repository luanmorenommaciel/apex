"""
Apex V1 — MCP Server (5 tools: get_findings, get_stage_metrics, list_slow_apps,
trigger_diagnosis, apply_fix)
"""
import os, sys, json, logging, datetime, difflib, shutil
from typing import Any

import clickhouse_connect
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("apex.mcp")

CH_HOST     = os.getenv("APEX_CH_HOST", "localhost")
CH_PORT     = int(os.getenv("APEX_CH_PORT", "28123"))       # default plat-v0
CH_USER     = os.getenv("APEX_CH_USER", "spv0")
CH_PASSWORD = os.getenv("APEX_CH_PASSWORD", "spv0clickhouse123")

app = Server("apex-v1")

def get_ch():
    return clickhouse_connect.get_client(
        host=CH_HOST, port=CH_PORT, username=CH_USER, password=CH_PASSWORD)

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(name="get_findings",
             description="Retorna findings de diagnóstico Apex para um app_id Spark.",
             inputSchema={"type":"object","properties":{"app_id":{"type":"string"}},"required":["app_id"]}),
        Tool(name="get_stage_metrics",
             description="Retorna métricas dos stages para um app_id (top por duration).",
             inputSchema={"type":"object","properties":{"app_id":{"type":"string"},"limit":{"type":"integer","default":10}},"required":["app_id"]}),
        Tool(name="list_slow_apps",
             description="Lista jobs Spark mais lentos das últimas N horas.",
             inputSchema={"type":"object","properties":{"hours":{"type":"integer","default":24},"limit":{"type":"integer","default":10}}}),
        Tool(name="trigger_diagnosis",
             description="Dispara diagnóstico Crew.ai para um app_id e persiste o finding.",
             inputSchema={"type":"object","properties":{"app_id":{"type":"string"}},"required":["app_id"]}),
        Tool(name="apply_fix",
             description="Aplica a recomendação Apex no arquivo PySpark do engenheiro (com backup).",
             inputSchema={"type":"object","properties":{"app_id":{"type":"string"},"file_path":{"type":"string"},"dry_run":{"type":"boolean","default":False}},"required":["app_id","file_path"]}),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    ch = get_ch()

    if name == "get_findings":
        app_id = arguments["app_id"]
        rows = list(ch.query(
            "SELECT pattern, severity, confidence, root_cause, recommendation, created_at "
            "FROM apex.findings WHERE app_id = {app_id:String} ORDER BY created_at DESC LIMIT 5",
            parameters={"app_id": app_id}).named_results())
        if not rows:
            return [TextContent(type="text", text=f"Nenhum finding para {app_id}. Use trigger_diagnosis.")]
        return [TextContent(type="text", text=json.dumps(rows, indent=2, default=str))]

    elif name == "get_stage_metrics":
        app_id = arguments["app_id"]
        limit  = arguments.get("limit", 10)
        rows = list(ch.query(
            "SELECT stage_id, stage_name, num_tasks, duration_ms, input_bytes, disk_spill, memory_spill, shuffle_read "
            "FROM apex.stage_metrics WHERE app_id = {app_id:String} ORDER BY duration_ms DESC LIMIT {limit:UInt32}",
            parameters={"app_id": app_id, "limit": limit}).named_results())
        return [TextContent(type="text", text=json.dumps(rows, indent=2, default=str))]

    elif name == "list_slow_apps":
        hours = arguments.get("hours", 24)
        limit = arguments.get("limit", 10)
        rows = list(ch.query(
            "SELECT app_id, sum(duration_ms) AS total_ms, sum(disk_spill) AS total_spill, "
            "count() AS num_stages, max(ingested_at) AS last_seen "
            "FROM apex.stage_metrics WHERE ingested_at >= now() - INTERVAL {hours:UInt32} HOUR "
            "GROUP BY app_id ORDER BY total_ms DESC LIMIT {limit:UInt32}",
            parameters={"hours": hours, "limit": limit}).named_results())
        return [TextContent(type="text", text=json.dumps(rows, indent=2, default=str))]

    elif name == "trigger_diagnosis":
        app_id = arguments["app_id"]
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from analysis.crew_diagnose import diagnose as crew_diagnose, persist_finding
            finding = crew_diagnose(app_id)
            persist_finding(finding)
            return [TextContent(type="text", text=json.dumps(finding, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Erro no diagnóstico: {e}")]

    elif name == "apply_fix":
        app_id    = arguments["app_id"]
        file_path = arguments["file_path"]
        dry_run   = arguments.get("dry_run", False)

        rows = list(ch.query(
            "SELECT pattern, severity, root_cause, recommendation FROM apex.findings "
            "WHERE app_id = {app_id:String} ORDER BY created_at DESC LIMIT 1",
            parameters={"app_id": app_id}).named_results())
        if not rows:
            return [TextContent(type="text", text=f"Sem finding para {app_id}. Execute trigger_diagnosis primeiro.")]
        finding = rows[0]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_code = f.read()
        except Exception as e:
            return [TextContent(type="text", text=f"Erro ao ler {file_path}: {e}")]

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return [TextContent(type="text", text="ANTHROPIC_API_KEY não configurada.")]

        import anthropic as _ant
        client = _ant.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=4096,
            messages=[{"role": "user", "content": (
                f"Você é um Spark performance engineer. Aplique o fix abaixo no código PySpark.\n\n"
                f"DIAGNÓSTICO: padrão={finding['pattern']} | severidade={finding['severity']}\n"
                f"CAUSA RAIZ: {finding['root_cause']}\n"
                f"RECOMENDAÇÃO: {finding['recommendation']}\n\n"
                f"CÓDIGO ({file_path}):\n```python\n{original_code}\n```\n\n"
                f"Retorne APENAS o código corrigido, sem markdown fences."
            )}])
        fixed_code = msg.content[0].text.strip()
        if fixed_code.startswith("```"):
            lines = fixed_code.split("\n")
            fixed_code = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        diff = "".join(difflib.unified_diff(
            original_code.splitlines(keepends=True),
            fixed_code.splitlines(keepends=True),
            fromfile=f"{file_path} (original)", tofile=f"{file_path} (apex fix)",
        )) or "(sem alterações)"

        if dry_run:
            return [TextContent(type="text", text=f"DRY RUN — diff ({finding['pattern']}):\n\n{diff}")]

        backup = file_path + f".apex_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(fixed_code)
        return [TextContent(type="text", text=(
            f"✅ Fix aplicado — {finding['pattern']} ({finding['severity']})\n"
            f"Backup: {backup}\n\nDiff:\n{diff}"))]

    return [TextContent(type="text", text=f"Tool desconhecida: {name}")]


async def main():
    logger.info("Apex MCP Server iniciando...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
