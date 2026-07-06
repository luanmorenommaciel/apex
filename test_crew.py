"""
Diagnostico minimo — isola onde crew_diagnose.py falha silenciosamente.
"""
import os, sys

os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"

print("1. imports...", flush=True)
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
import clickhouse_connect
print("   OK", flush=True)

print("2. ClickHouse connection...", flush=True)
ch = clickhouse_connect.get_client(
    host=os.getenv("APEX_CH_HOST", "localhost"),
    port=int(os.getenv("APEX_CH_PORT", "28123")),
    username=os.getenv("APEX_CH_USER", "spv0"),
    password=os.getenv("APEX_CH_PASSWORD", "spv0clickhouse123"),
)
rows = ch.query("SELECT count() FROM apex.stage_metrics WHERE app_id = 'app-20260706010516-0004'").result_rows
print(f"   stage_metrics count={rows[0][0]}", flush=True)

print("3. LLM init...", flush=True)
key = os.getenv("ANTHROPIC_API_KEY")
print(f"   key present: {bool(key)} len={len(key) if key else 0}", flush=True)
llm = LLM(model="anthropic/claude-sonnet-4-6", api_key=key, max_tokens=200)
print("   OK", flush=True)

print("4. Agent + Task + Crew...", flush=True)
agent = Agent(
    role="Test",
    goal="Responda 'pong'",
    backstory="Agente de teste simples.",
    llm=llm,
    verbose=False,
    max_iter=1,
)
task = Task(description="Diga apenas 'pong'.", expected_output="pong", agent=agent)
crew = Crew(agents=[agent], tasks=[task], verbose=False)
print("   OK", flush=True)

print("5. kickoff...", flush=True)
result = crew.kickoff()
raw = result.raw if hasattr(result, "raw") else str(result)
print(f"   result: {raw[:300]}", flush=True)

print("DONE", flush=True)
