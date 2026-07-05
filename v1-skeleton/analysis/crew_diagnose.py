"""
Apex V1 — Diagnóstico Crew.ai (substitui diagnose.py)

Pipeline multi-agent:
  MetricsAnalyzer  → lê ClickHouse, identifica padrão e bottleneck
  RecommendationWriter → recebe análise, escreve fix concreto

Uso:
    python analysis/crew_diagnose.py --app-id <app_id>
    python analysis/crew_diagnose.py --app-id <app_id> --model claude-sonnet-4-6

Em MCP: import crew_diagnose; crew_diagnose.diagnose(app_id)
"""
import argparse
import json
import os
import sys
import logging
from typing import Any

import clickhouse_connect
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_anthropic import ChatAnthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("apex.crew")

# ── Config ───────────────────────────────────────────────────────────────────

CH_HOST     = os.getenv("APEX_CH_HOST", "localhost")
CH_PORT     = int(os.getenv("APEX_CH_PORT", "8123"))
CH_USER     = os.getenv("APEX_CH_USER", "apex")
CH_PASSWORD = os.getenv("APEX_CH_PASSWORD", "apex123")

ANTHROPIC_KEY  = os.getenv("ANTHROPIC_API_KEY")
DEFAULT_MODEL  = os.getenv("APEX_LLM_MODEL", "claude-sonnet-4-6")

# ── Padrões detectáveis (contrato anti-alucinação) ───────────────────────────

KNOWN_PATTERNS = {
    "skew": {
        "description": "Uma task processa significativamente mais dados que as demais",
        "key_signals": ["max_task_ms / avg_task_ms > 3", "shuffle_read desigual entre tasks"],
        "threshold": {"max_avg_ratio": 3.0},
    },
    "parallelism_collapse": {
        "description": "Stage com número de tasks muito baixo para o volume de dados",
        "key_signals": ["num_tasks < 8 com input_bytes > 1GB", "executor idle time alto"],
        "threshold": {"tasks_per_gb": 8},
    },
    "spill": {
        "description": "Tasks derramando dados para disco por falta de memória",
        "key_signals": ["disk_spill > 0", "memory_spill > 0"],
        "threshold": {"spill_bytes": 1},
    },
    "broadcast_miss": {
        "description": "Join sem broadcast em tabela pequena, causando shuffle desnecessário",
        "key_signals": ["shuffle_read alto em stage com input pequeno"],
        "threshold": {},
    },
    "small_files": {
        "description": "Muitos arquivos pequenos causando overhead de task scheduling",
        "key_signals": ["num_tasks muito alto com duration_ms muito baixo"],
        "threshold": {},
    },
    "other": {
        "description": "Anti-pattern identificado mas não classificado nos padrões conhecidos",
        "key_signals": [],
        "threshold": {},
    },
}

SEVERITY_LEVELS = ["critical", "high", "medium", "low"]

FINDING_SCHEMA = {
    "pattern": list(KNOWN_PATTERNS.keys()),
    "severity": SEVERITY_LEVELS,
    "confidence": "float 0.0–1.0",
    "bottleneck_stage_id": "int or null",
    "root_cause": "string descritiva (max 300 chars)",
    "recommendation": "string com o fix concreto e aplicável (max 500 chars)",
    "evidence": {
        "key_metric": "nome da métrica principal",
        "key_value": "valor observado",
        "expected_value": "valor esperado em condição normal",
    },
}

# ── ClickHouse tools (disponíveis para MetricsAnalyzer) ──────────────────────

def _get_ch():
    return clickhouse_connect.get_client(
        host=CH_HOST, port=CH_PORT,
        username=CH_USER, password=CH_PASSWORD,
    )


@tool("fetch_stage_metrics")
def fetch_stage_metrics(app_id: str) -> str:
    """
    Busca métricas de stage do ClickHouse para o app_id informado.
    Retorna os top 20 stages por duração em formato JSON.
    Use sempre como primeiro passo da análise.
    """
    try:
        ch = _get_ch()
        rows = ch.query("""
            SELECT
                stage_id, stage_name, num_tasks, duration_ms,
                input_bytes, shuffle_read, shuffle_write,
                memory_spill, disk_spill, gc_time_ms
            FROM apex.stage_metrics
            WHERE app_id = {app_id:String}
            ORDER BY duration_ms DESC
            LIMIT 20
        """, parameters={"app_id": app_id}).named_results()
        result = list(rows)
        if not result:
            return f"ERRO: Nenhuma métrica encontrada para app_id={app_id}"
        return json.dumps(result, default=str)
    except Exception as e:
        return f"ERRO ao buscar stage metrics: {e}"


@tool("fetch_task_distribution")
def fetch_task_distribution(app_id: str, stage_id: int) -> str:
    """
    Busca distribuição de tasks de um stage específico para detectar skew.
    Retorna min/max/avg de duration_ms e total de disk_spill.
    Use após identificar o stage mais lento com fetch_stage_metrics.
    """
    try:
        ch = _get_ch()
        rows = ch.query("""
            SELECT
                count()          AS total_tasks,
                max(duration_ms) AS max_task_ms,
                min(duration_ms) AS min_task_ms,
                avg(duration_ms) AS avg_task_ms,
                sum(disk_spill)  AS total_spill_bytes,
                sum(memory_spill) AS total_memory_spill
            FROM apex.task_metrics
            WHERE app_id = {app_id:String}
              AND stage_id = {stage_id:UInt32}
        """, parameters={"app_id": app_id, "stage_id": stage_id}).named_results()
        result = list(rows)
        return json.dumps(result[0] if result else {}, default=str)
    except Exception as e:
        return f"ERRO ao buscar task distribution: {e}"


# ── LLM ──────────────────────────────────────────────────────────────────────

def _get_llm(model: str):
    if not ANTHROPIC_KEY:
        raise EnvironmentError("ANTHROPIC_API_KEY não configurada")
    return ChatAnthropic(
        model=model,
        anthropic_api_key=ANTHROPIC_KEY,
        max_tokens=1024,
    )


# ── Agents ───────────────────────────────────────────────────────────────────

def build_metrics_analyzer(llm) -> Agent:
    """
    MetricsAnalyzer: lê ClickHouse, identifica padrão e bottleneck.
    Tem acesso às tools de ClickHouse. Produz análise intermediária estruturada.
    """
    return Agent(
        role="Spark Performance Analyst",
        goal=(
            "Identificar o principal anti-pattern de performance em um job Spark "
            "analisando métricas de stage e task do ClickHouse. "
            "Produzir uma análise estruturada com: padrão identificado, stage bottleneck, "
            "evidências quantitativas e nível de confiança."
        ),
        backstory=(
            "Especialista em internals do Spark com 8 anos de experiência. "
            "Conhece profundamente skew, spill, parallelism collapse, broadcast miss e small files. "
            "Sempre baseia conclusões em dados — nunca alucina. "
            f"Padrões válidos: {list(KNOWN_PATTERNS.keys())}. "
            "Se os dados não evidenciam claramente um padrão, reporta 'other' com confidence < 0.5."
        ),
        tools=[fetch_stage_metrics, fetch_task_distribution],
        llm=llm,
        verbose=True,
        max_iter=5,
        allow_delegation=False,
    )


def build_recommendation_writer(llm) -> Agent:
    """
    RecommendationWriter: recebe a análise do MetricsAnalyzer e escreve o fix.
    Sem acesso a tools — trabalha apenas com o output do agente anterior.
    """
    return Agent(
        role="Spark Fix Engineer",
        goal=(
            "Converter a análise de performance em uma recomendação concreta e aplicável. "
            "O fix deve ser específico, com código de exemplo quando possível, "
            "e entregue no schema JSON exato definido pelo contrato Apex."
        ),
        backstory=(
            "Senior Spark engineer que escreve código, não apenas conselhos. "
            "Quando detecta skew, sugere salting + repartition com parâmetros concretos. "
            "Quando detecta spill, sugere configurações de memória específicas. "
            "NUNCA inventa dados ou métricas que não estavam na análise recebida. "
            f"Schema de saída obrigatório: {json.dumps(FINDING_SCHEMA, indent=2)}"
        ),
        tools=[],
        llm=llm,
        verbose=True,
        max_iter=3,
        allow_delegation=False,
    )


# ── Tasks ─────────────────────────────────────────────────────────────────────

def build_analyze_task(agent: Agent, app_id: str) -> Task:
    return Task(
        description=(
            f"Analise as métricas de performance do job Spark com app_id='{app_id}'.\n\n"
            "Passos obrigatórios:\n"
            "1. Use fetch_stage_metrics para obter os stages do job\n"
            "2. Identifique o stage mais lento (maior duration_ms)\n"
            "3. Use fetch_task_distribution no stage mais lento para verificar skew\n"
            "4. Classifique o anti-pattern principal usando APENAS estes padrões: "
            f"{list(KNOWN_PATTERNS.keys())}\n"
            "5. Calcule a confiança baseada nas evidências quantitativas\n\n"
            "Sinais por padrão:\n"
            + "\n".join(
                f"  - {k}: {v['description']} | Signals: {v['key_signals']}"
                for k, v in KNOWN_PATTERNS.items()
            )
        ),
        expected_output=(
            "JSON com: pattern, confidence (0-1), bottleneck_stage_id, "
            "evidências quantitativas (métricas observadas vs esperadas), "
            "e resumo em 2-3 frases do que está acontecendo."
        ),
        agent=agent,
    )


def build_recommendation_task(agent: Agent, app_id: str) -> Task:
    return Task(
        description=(
            f"Com base na análise do job '{app_id}' fornecida pelo MetricsAnalyzer, "
            "produza o finding final no schema JSON exato do Apex.\n\n"
            "Regras:\n"
            "1. Não invente dados — use APENAS as evidências da análise\n"
            "2. recommendation deve ser um fix concreto e aplicável (max 500 chars)\n"
            "3. Se padrão for skew: inclua exemplo de salting ou repartition\n"
            "4. Se padrão for spill: inclua configuração de memória específica\n"
            "5. severity: critical se job falhar ou demorar 10x+, high 3-10x, medium 1.5-3x, low < 1.5x\n\n"
            f"Schema obrigatório:\n{json.dumps(FINDING_SCHEMA, indent=2)}\n\n"
            "Retorne APENAS o JSON válido, sem texto adicional."
        ),
        expected_output=(
            "JSON válido com todos os campos do schema: pattern, severity, confidence, "
            "bottleneck_stage_id, root_cause, recommendation, evidence."
        ),
        agent=agent,
        output_json=True,
    )


# ── Validação de contrato ─────────────────────────────────────────────────────

def _validate_against_contract(finding: dict) -> dict:
    """
    Valida o finding do Crew.ai contra o contrato do cenário.
    Implementa o 'contract_enforcement' definido nos listener_*.yaml.

    Regras:
    - Padrão não reconhecido → override para 'other'
    - Severity inválida → override para 'medium'
    - Confidence < 0.6 → sinaliza para escalação ao Judge (Tier 4)
    - Evidence ausente → adiciona warning no finding
    """
    # 1. Padrão reconhecido
    if finding.get("pattern") not in KNOWN_PATTERNS:
        logger.warning(f"[CONTRATO] Padrão '{finding.get('pattern')}' não reconhecido → 'other'")
        finding["pattern"] = "other"

    # 2. Severity válida
    if finding.get("severity") not in SEVERITY_LEVELS:
        logger.warning(f"[CONTRATO] Severity '{finding.get('severity')}' inválida → 'medium'")
        finding["severity"] = "medium"

    # 3. Confidence abaixo do mínimo → sinaliza Judge
    confidence = float(finding.get("confidence", 0.0))
    if confidence < 0.6:
        logger.warning(f"[CONTRATO] Confidence {confidence:.2f} < 0.6 → marcado para Tier 4 (Judge)")
        finding["needs_judge"] = True
        finding["judge_reason"] = f"confidence={confidence:.2f} abaixo do threshold 0.6"
    else:
        finding["needs_judge"] = False

    # 4. Evidence presente
    evidence = finding.get("evidence")
    if not evidence or not isinstance(evidence, dict):
        logger.warning("[CONTRATO] Evidence ausente → finding pode estar alucinando")
        finding["contract_warning"] = "evidence_missing"
        finding["needs_judge"] = True

    # 5. Validação de recomendação mínima por padrão
    pattern = finding.get("pattern", "other")
    recommendation = finding.get("recommendation", "").lower()
    pattern_keywords = {
        "skew":                  ["salting", "repartition", "skewhint", "adaptive"],
        "spill":                 ["spark.executor.memory", "spark.memory.fraction", "repartition", "persist"],
        "parallelism_collapse":  ["repartition", "spark.default.parallelism", "spark.sql.shuffle.partitions"],
        "broadcast_miss":        ["broadcast", "hint", "autoBroadcastJoinThreshold"],
        "small_files":           ["coalesce", "repartition", "compact"],
    }
    required_keywords = pattern_keywords.get(pattern, [])
    if required_keywords and not any(kw.lower() in recommendation for kw in required_keywords):
        logger.warning(f"[CONTRATO] Recommendation para '{pattern}' não menciona nenhum de {required_keywords}")
        finding["contract_warning"] = finding.get("contract_warning", "") + " recommendation_keywords_missing"

    logger.info(f"[CONTRATO] Validação concluída: pattern={pattern}, confidence={confidence:.2f}, needs_judge={finding.get('needs_judge')}")
    return finding


# ── Pipeline principal ────────────────────────────────────────────────────────

def diagnose(app_id: str, model: str = DEFAULT_MODEL) -> dict:
    """
    Pipeline Crew.ai: ClickHouse → MetricsAnalyzer → RecommendationWriter → finding JSON.

    Args:
        app_id: Spark application ID (ex: app-20240630-123456)
        model:  Modelo Anthropic (default: claude-sonnet-4-6)

    Returns:
        dict com o finding estruturado
    """
    logger.info(f"Iniciando diagnóstico Crew.ai para app_id={app_id}, model={model}")

    llm = _get_llm(model)

    metrics_analyzer    = build_metrics_analyzer(llm)
    recommendation_writer = build_recommendation_writer(llm)

    analyze_task        = build_analyze_task(metrics_analyzer, app_id)
    recommendation_task = build_recommendation_task(recommendation_writer, app_id)

    # RecommendationWriter depende do output do MetricsAnalyzer
    recommendation_task.context = [analyze_task]

    crew = Crew(
        agents=[metrics_analyzer, recommendation_writer],
        tasks=[analyze_task, recommendation_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff(inputs={"app_id": app_id})

    # Parse do output final
    raw = result.raw if hasattr(result, "raw") else str(result)

    # Remove markdown fences se presentes
    if raw.strip().startswith("```"):
        raw = raw.strip().split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        finding = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: tenta extrair JSON do texto
        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            finding = json.loads(match.group())
        else:
            logger.error(f"Output inválido do Crew.ai: {raw[:200]}")
            raise ValueError(f"Crew.ai não retornou JSON válido: {raw[:200]}")

    # ── Validação de contrato (anti-alucinação) ──────────────────────────────
    finding = _validate_against_contract(finding)
    # ─────────────────────────────────────────────────────────────────────────

    finding["app_id"]   = app_id
    finding["llm_model"] = model
    finding["pipeline"] = "crewai"

    logger.info(f"Diagnóstico concluído: pattern={finding.get('pattern')}, severity={finding.get('severity')}, confidence={finding.get('confidence')}")
    return finding


def persist_finding(finding: dict) -> None:
    """Salva o finding no ClickHouse (apex.findings)."""
    try:
        ch = _get_ch()
        ch.insert(
            "apex.findings",
            [[
                finding["app_id"],
                finding.get("bottleneck_stage_id"),
                finding.get("pattern", "other"),
                finding.get("severity", "medium"),
                float(finding.get("confidence", 0.0)),
                finding.get("root_cause", ""),
                finding.get("recommendation", ""),
                finding.get("llm_model", DEFAULT_MODEL),
            ]],
            column_names=[
                "app_id", "stage_id", "pattern", "severity", "confidence",
                "root_cause", "recommendation", "llm_model",
            ],
        )
        logger.info("Finding persistido no ClickHouse")
    except Exception as e:
        logger.error(f"Erro ao persistir finding: {e}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Apex V1 — Diagnóstico Crew.ai")
    parser.add_argument("--app-id", required=True, help="Spark application ID")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Modelo Anthropic")
    parser.add_argument("--no-persist", action="store_true", help="Não salva no ClickHouse")
    args = parser.parse_args()

    finding = diagnose(args.app_id, args.model)

    if not args.no_persist:
        persist_finding(finding)

    print("\n" + "=" * 60)
    print("APEX FINDING (Crew.ai)")
    print("=" * 60)
    print(json.dumps(finding, indent=2, ensure_ascii=False))
    print("=" * 60)

    exit_codes = {"critical": 2, "high": 1, "medium": 0, "low": 0}
    sys.exit(exit_codes.get(finding.get("severity", "low"), 0))


if __name__ == "__main__":
    main()
