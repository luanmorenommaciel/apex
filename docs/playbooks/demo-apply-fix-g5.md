# Demo G5 — "aplica nossa sugestão": do job quebrado ao diff no IDE

> **Objetivo:** roteiro reproduzível de ~5 min que prova o L6 do Luan — a experiência
> que o DataFlint não tem. Job com skew → finding no ClickHouse → engenheiro pergunta
> no IDE → `apply_fix` edita o código com backup + diff.
>
> **Pré-requisitos:** plat-v0 rodando (`docker compose up` no `dataship-spark-plat-v0`),
> `ANTHROPIC_API_KEY` exportada, Claude Code ou Cursor instalado.

---

## Passo 0 — Sanidade (1 min)

```bash
cd apex   # raiz do repo, branch gustocezar/feature/cowork-desacoplamento-geradores
pip install -r requirements.txt
python3 -m pytest tests/ -q            # esperado: 31 passed
curl -s http://localhost:28123/ping    # esperado: Ok. (ClickHouse do plat-v0)
```

## Passo 1 — Gerar o job com anti-pattern (30 s)

```bash
python3 generators/code_generator.py scenarios/skew_on_join_30x.yaml demo_job.py
# ✅ demo_job.py gerado. Anti-pattern na linha 20 (join com chave 80% quente)
```

`demo_job.py` é o "código do cliente" que o Apex vai corrigir ao final.

## Passo 2 — Rodar no Spark e ingerir (2 min)

```bash
# submete ao cluster do plat-v0 (Spark 4.1.2) e captura o event log do MinIO
# (ver README do plat-v0); com o app_id em mãos:
python3 v1-skeleton/ingest/event_log_ingest.py <app_id>
# alternativa sem cluster (fallback sintético): 
#   python3 generators/plan_generator.py scenarios/skew_on_join_30x.yaml demo_log.ndjson
#   python3 v1-skeleton/ingest/event_log_ingest.py --local demo_log.ndjson
```

## Passo 3 — Diagnóstico Crew.ai (30–60 s)

```bash
python3 v1-skeleton/analysis/crew_diagnose.py --app-id <app_id>
# ApexFinding JSON: pattern=data_skew_on_join_key, severity=high,
# root_cause + recommendation com código de exemplo → gravado em apex.findings
```

## Passo 4 — Registrar o MCP no IDE (1x só)

```bash
# Claude Code:
claude mcp add apex -- python v1-skeleton/mcp/server.py
# ou copiar v1-skeleton/mcp/claude_code_config.json (ajustar ANTHROPIC_API_KEY)
```

Ferramentas expostas: `get_findings`, `get_stage_metrics`, `list_slow_apps`,
`trigger_diagnosis`, `apply_fix`.

## Passo 5 — A cena (o momento da demo)

No Claude Code/Cursor, com `demo_job.py` aberto:

> **Engenheiro:** "Tô com problema de performance no job `<app_id>`. O que está acontecendo?"
>
> **IDE (via `get_findings`):** skew 27.9x no stage do join, chave `customer_id = 7`,
> recomendação: AQE skewJoin + broadcast + salting.
>
> **Engenheiro:** "Aplica a sugestão no demo_job.py."
>
> **IDE (via `apply_fix`):** edita o arquivo, salva backup
> `demo_job.py.apex_backup_<timestamp>` e mostra o **diff** para revisão.

O diff esperado: hint de broadcast / configs AQE na linha do join (a linha 20 do manifesto).

## Passo 6 — Fechar o loop (opcional, +2 min)

Re-submeter o `demo_job.py` corrigido ao plat-v0 e mostrar o novo diagnóstico
limpo (`trigger_diagnosis` → sem finding high). Baseline G1 garante que job
saudável não gera alerta.

---

## Roteiro de fala (30 s)

"O DataFlint mostra 14 alertas e para aí — a ação é do humano. O Apex detecta
com regra determinística (sem custo de LLM), explica com evidência, e quando o
engenheiro diz *aplica*, o código dele é corrigido no IDE com backup e diff.
Detecção → diagnóstico → ação, no mesmo fluxo. Isso é o L6 do plano do Luan,
funcionando."

## Se algo falhar na hora

| Sintoma | Fallback |
|---|---|
| plat-v0 fora do ar | Passo 2 alternativo (log sintético) — o resto do fluxo é idêntico |
| Sem ANTHROPIC_API_KEY | `get_findings`/`get_stage_metrics` funcionam (dados do ClickHouse); pular `apply_fix` e mostrar o diff de um backup anterior |
| MCP não conecta | `python v1-skeleton/mcp/server.py` manual e checar env `APEX_CH_*` |
