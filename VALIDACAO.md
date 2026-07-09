# VALIDAÇÃO — Branch `gustocezar/feature/cowork-desacoplamento-geradores`

> **Para o time revisar.** Este documento mapeia o que foi pedido (reunião 30/06 + issues do projeto) contra o que está entregue nesta branch.
>
> **Captain:** Augusto · **Branch criada em:** 2026-07-06  
> **Base:** `gustocezar/apex-workspace` (cowork) → pushed para `luanmorenommaciel/apex`

---

## 1. Issues da reunião 30/06 — status por issue

| Issue | Título | Status | Onde está na branch |
|-------|--------|--------|---------------------|
| #22 | Documento V1 completo: arquitetura + pods + escopo | 🟡 Parcial | `docs/presentations/apex_v1_apresentacao_luan.html` — 8 slides com arquitetura, evidências e comparação DataFlint |
| #23 | Pod Ambiente: Spark Envy Docker | ✅ Existe | `dataship-spark-plat-v0` (repo separado) — Spark 4.1.2 + MinIO + ClickHouse via docker compose |
| #24 | Pod Listener: SparkListener in-process | 🟡 Bridge | `v1-skeleton/listener/spark_listener.py` existe. **Blocker py4j** documentado no ADR-005 — bridge via event log polling funcional |
| #25 | Pod Infra: ClickHouse setup + schema | ✅ Feito | `v1-skeleton/ingest/event_log_ingest.py` — popula `apex.stage_metrics` e `apex.task_metrics`. Schema criado e validado com dados reais |
| #26 | Pod Diagnóstico: Crew.ai + MCP | ✅ Feito | `v1-skeleton/analysis/crew_diagnose.py` + `v1-skeleton/mcp/server.py` — pipeline end-to-end validado hoje |
| #27 | ADR-005: SparkListener vs zero-JAR | ✅ Feito | `docs/adr/ADR-005-sparklistener-vs-zero-jar.md` — decisão formalizada: V1 segue SparkListener (Mundo B), bridge via event log |
| #28 | Research DataFlint — time completo | ✅ Feito (Augusto) | `docs/competitive/` — análise completa: arquitetura, matrix de capabilities, community pain points |
| #29 | Revisão da branch Augusto | 👁️ Esta branch | Esta é a branch que o Luan vai revisar |
| #30 | On-premise / offline mode | ⏸️ Futuro | Não endereçado — registrado como Sprint 4+ |

---

## 2. Issues do repo `luanmorenommaciel/apex` — status

| Issue | Título | Status | O que foi entregue |
|-------|--------|--------|--------------------|
| #17 | Watcher / Classifier / Judger Pipeline | 🟡 Parcial | V1 tem 2 agentes Crew.ai (MetricsAnalyzer + RecommendationWriter). Tier 4 (Judge) existe na lógica de contrato (escala quando `confidence < 0.6`). Watcher contínuo → log_poller.py (15s) |
| #18 | OTel Collector Stage 02 (Go) | ⏸️ Guilherme | Não endereçado aqui — domínio do Guilherme |
| #19 | Local Bootstrap Platform (plat-v0) | ✅ Existe | `dataship-spark-plat-v0` — Spark 4.1.2 + MinIO + ClickHouse rodando |
| #20 | Performance Recommendation Engine | ✅ Feito | `crew_diagnose.py` → `ApexFinding` com `recommendation` (fix concreto com código de exemplo) entregue via MCP ao IDE |
| #21 | CI Integration | ⏸️ Sprint 2 | `.github/workflows/scenario-gate.yml` existe para Mundo A. V1 ainda sem CI |

---

## 3. O que o Luan pediu na reunião — mapeado diretamente

> Citações diretas da transcrição 30/06

| Pedido | Status | Evidência |
|--------|--------|-----------|
| *"Spark Envy gerando ambiente + jobs Docker"* | ✅ | `dataship-spark-plat-v0` — docker compose up funcional |
| *"SparkListener injetado no cluster"* | 🟡 Bridge | ADR-005 documenta blocker py4j. Bridge: event log polling 15s via `log_poller.py` |
| *"ClickStack recebendo métricas do listener"* | ✅ | `event_log_ingest.py` popula ClickHouse. 5 stages, 7 tasks validados com dados reais |
| *"Crew.ai vai olhar e vai falar qual o problema"* | ✅ | `crew_diagnose.py` — 2 agentes, output `ApexFinding` JSON com pattern, severity, confidence, root_cause, recommendation |
| *"Fix entregue via MCP ao engenheiro no IDE"* | ✅ | `server.py` — 5 ferramentas MCP: `get_findings`, `get_stage_metrics`, `list_slow_apps`, `trigger_diagnosis`, `apply_fix` |
| *"Aplica nossa sugestão"* | ✅ | `apply_fix` MCP tool — lê finding do ClickHouse, usa LLM para editar o arquivo PySpark, salva backup |
| *"Vou olhar a branch que você colocou, Augusto"* | 👁️ Esta branch | |

---

## 4. O que esta branch contém — mapa de arquivos

```
v1-skeleton/
├── listener/
│   └── spark_listener.py       # SparkListener Python (bridge via event log — ADR-005)
├── ingest/
│   ├── event_log_ingest.py     # Event log → ClickHouse (stage_metrics + task_metrics)
│   └── log_poller.py           # Rolling watch MinIO/local a cada 15s → auto-ingest + diagnose
├── analysis/
│   └── crew_diagnose.py        # Crew.ai 2 agentes → ApexFinding (Pydantic, anti-alucinação)
└── mcp/
    ├── server.py               # MCP Server 5 ferramentas
    └── claude_code_config.json # Config para registrar no Cursor / Claude Code

docs/
├── adr/
│   └── ADR-005-sparklistener-vs-zero-jar.md  # Decisão arquitetural formalizada
├── presentations/
│   └── apex_v1_apresentacao_luan.html        # 8 slides: pipeline + DataFlint comparison
└── competitive/
    ├── dataflint-apex-study.html             # Análise completa DataFlint
    ├── dataflint-vs-apex-matrix.md           # Matrix de capabilities
    └── dataflint/                            # Docs individuais por feature DataFlint

generators/                     # v4 — desacoplamento geradores (scenario.yaml → job + event log)
watchers/                       # v4 — Skew Watcher
tests/                          # 40 testes passando
```

---

## 5. O que ainda falta (honesto)

| Item | Sprint | Observação |
|------|--------|------------|
| SparkListener real-time verdadeiro | Sprint 3 | Requer Scala JAR — blocker py4j documentado no ADR-005 |
| Mais cenários além de skew (spill, broadcast_miss, parallelism_collapse) | Sprint 2 | 1 cenário hoje vs DataFlint 14 |
| CI para V1 | Sprint 2 | CI de Mundo A existe, V1 sem gate |
| OTel Collector Go | Guilherme | Domínio separado |
| On-premise LLM | Sprint 4+ | Decisão estratégica pendente com Luan |

---

## 6. Como validar localmente

```bash
# 1. Clonar a branch
git clone https://github.com/luanmorenommaciel/apex.git
cd apex
git checkout gustocezar/feature/cowork-desacoplamento-geradores

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Rodar os 40 testes (Mundo A — geradores)
pytest tests/ -v

# 4. Testar o pipeline V1 (precisa do plat-v0 rodando)
# Subir: dataship-spark-plat-v0 (docker compose up)
# Depois:
python v1-skeleton/ingest/event_log_ingest.py <app_id>
python v1-skeleton/analysis/crew_diagnose.py --app-id <app_id>

# 5. Rodar o poller (detecta novos jobs automaticamente)
python v1-skeleton/ingest/log_poller.py --interval 15
```

---

## 7. Reavaliação 08/07 — correções de CI e caminho para o V1 final

> Adendo pós-revisão completa da branch em 2026-07-08. Detalhes no Captain's Report: `docs/meetings/captains-report-2026-07-08.md`

### 7.1 Bugs de CI encontrados e corrigidos (commit `0ddb550`)

| Bug | Impacto | Fix |
|-----|---------|-----|
| `scenario-gate.yml` iterava `scenarios/*.yaml` incluindo os 3 `listener_*.yaml` (Mundo B, sem `code_generator`) | **KeyError → gate vermelho em qualquer PR** | Loop pula cenários sem `code_generator:` (validado localmente: skips corretos + GATE VERDE 27.9x) |
| `oracle-weekly.yml` chamava `scripts/fetch_real_log.py` que não existia + `python` em vez de `python3` | Oráculo semanal (P2-12) falhava silenciosamente toda segunda | Script criado (`scripts/fetch_real_log.py`, MinIO → log mais recente) + `python3` + mesmo filtro world B |

**Pendente para fechar P2-12:** configurar secrets `MINIO_*` no repo e disparar um `workflow_dispatch` manual do oracle-weekly.

### 7.2 O que falta para a solução final (proposta ao Commander)

Conclusão da avaliação comparativa (`docs/avaliacao/`): nenhuma das 3 branches resolve sozinha. Proposta — **spike/apex-v0.1 (Aguimar) como base do merge**, absorvendo:

1. **T1 heurístico + EvidenceValidator** do kimi (diagnóstico em ~136ms, LLM só como fallback)
2. **`apply_fix` MCP** do cowork (única branch que fecha o loop no IDE — pedido direto do Luan em 30/06)
3. **Go eventlog-loader** do spike substitui o `log_poller.py`

**Decisão que precisamos do Luan:** bater o martelo na direção de merge acima. Sem isso, as 3 branches continuam divergindo.

### 7.3 Caminho crítico pós-decisão (issues prontas em `docs/avaliacao/ISSUES_AVALIACAO.md`)

| Ordem | Item | Prioridade |
|-------|------|-----------|
| 1 | A01 — portar 4 detectores do spike (GC, shuffle, OOM, replans) | P0 — blocker V1 |
| 2 | A04 — baseline negativo `no_skew_baseline.yaml` (destrava P1-7 e P2-10; sem ele não há garantia contra falso positivo) | P1 |
| 3 | A03 — EvidenceValidator como gate antes do LLM | P1 |
| 4 | A05 — `apply_fix` integrado à base escolhida | P1 |
| 5 | P1-7 chave de join dinâmica + P2-8 confiança defensável | P1/P2 |
| 6 | CI para V1 (hoje só Mundo A tem gate) + validação multi-core 8 tasks | P2 |
| 7 | Listener real-time verdadeiro (JAR Scala) | Sprint 3 — ADR-005 |

---

*Qualquer dúvida ou feedback — abrir como comentário na PR ou mencionar `@gustocezar`.*
