# Matrix Comparativa — 4 Abordagens para Diagnóstico Spark

> **Avaliador:** Cowork (Claude / Anthropic) — Branch `gustocezar/feature/cowork-desacoplamento-geradores`  
> **Data:** 2026-07-07  
> **Nota metodológica:** Esta avaliação é feita pela própria LLM que implementou a solução `cowork`. Possível viés: tende a valorizar `apply_fix` e documentação de ADRs, pois foram as contribuições desta branch. Leia com senso crítico.

---

## As 4 Soluções

| # | Solução | Branch / Origem | Responsável |
|---|---------|-----------------|-------------|
| 1 | **spike/apex-v0.1** | `spike/apex-v0.1` (luanmorenommaciel/apex) | Aguimar |
| 2 | **cowork** | `gustocezar/feature/cowork-desacoplamento-geradores` | Claude (Anthropic / Cowork) |
| 3 | **kimi** | `gustocezar/feature/kimi-desacoplamento-geradores` | Kimi Work |
| 4 | **DataFlint** | SaaS externo | Produto comercial |

---

## Matrix Principal

### 🏗️ Arquitetura

| Dimensão | spike/apex-v0.1 | cowork | kimi | DataFlint |
|----------|-----------------|--------|------|-----------|
| Tipo | Full stack Docker local | Python + ClickHouse | Docker Compose (CREI+MCP) | SaaS Cloud |
| Stack de infra | Spark 4.1.2 + Delta Lake + MinIO + ClickHouse 26.5.1 + HyperDX | ClickHouse (existente) | Docker Compose isolado | Cloud própria |
| Linguagem principal | Go (loader) + Python (detectors + agents) | Python | Python | N/A (produto) |
| Ingestão de logs | Go eventlog-loader | log_poller Python (15s poll) | log_poller Python (15s poll) | SDK/agente SaaS |
| Configuração | `diagnostics.yaml` (thresholds versionados) | Hardcoded em código | JSON runbooks | Admin UI SaaS |
| Deploy | `make compose` (Docker) | Scripts Python | `docker compose up` | Conta SaaS |
| On-premise | ✅ | ✅ | ✅ | ❌ |

---

### 🔍 Detecção de Anti-patterns

| Anti-pattern | spike/apex-v0.1 | cowork | kimi | DataFlint |
|--------------|-----------------|--------|------|-----------|
| Skew em join/shuffle | ✅ crítico/warning (ratio 6x/3x) | ✅ (1 detector) | ✅ T1 SQL 136ms | ✅ AI-based |
| Shuffle excessivo | ✅ (256MiB warn / 1GiB crit) | ❌ | ✅ | ✅ |
| Re-planning AQE | ✅ (>3 re-plans = info) | ❌ | ❌ | ✅ |
| GC pressure | ✅ (>10% warn / >20% crit) | ❌ | ❌ | ✅ |
| OOM | ✅ | ❌ | ❌ | ✅ |
| Spill para disco | ❌ (não confirmado) | ❌ | ✅ | ✅ |
| Cache ineficiente | ✅ (workload cache_heavy) | ❌ | ❌ | ✅ |
| Cross join sem filtro | ✅ (workload cross_join) | ❌ | ❌ | ✅ |
| **Total detectores** | **5** | **1** | **~3** | **10+** |

---

### ⚡ Velocidade e Qualidade do Diagnóstico

| Dimensão | spike/apex-v0.1 | cowork | kimi | DataFlint |
|----------|-----------------|--------|------|-----------|
| Latência T1 (heurística) | N/A (SQL direto) | N/A (sem T1) | **136ms** (medido) | segundos |
| Latência validação | Config YAML (sem LLM) | Sem validação | **198ms** (7/7 regras) | N/A |
| Latência T2 (recomendação) | CrewAI (estimado: 5-30s) | CrewAI (sempre, 5-30s) | **0.01ms** (runbook JSON) | AI (segundos) |
| Funciona sem LLM | ✅ (detecção determinística) | ❌ (Crew.ai obrigatório) | ✅ (T1+T2 sem LLM) | ❌ |
| Falsos positivos | Controlado (guards no YAML) | Sem controle explícito | EvidenceValidator (7/7) | Não documentado |
| Benchmarks medidos | ❌ não publicados | ❌ não medidos | **✅ job app-20260706035238-0001** | Caso SimilarWeb (100x) |

---

### 🔧 MCP e Integração com IDE

| Dimensão | spike/apex-v0.1 | cowork | kimi | DataFlint |
|----------|-----------------|--------|------|-----------|
| MCP tools | 6 | 5 | 2 | ❌ (Slack/Email) |
| `list_runs` | ✅ | ❌ | ❌ | ❌ |
| `detect_skew` | ✅ | via `get_findings` | via `query_job` | ❌ |
| `detect_shuffle` | ✅ | ❌ | ❌ | ❌ |
| `detect_plans` | ✅ | ❌ | ❌ | ❌ |
| `get_report` | ✅ | ❌ | ❌ | ❌ |
| `analyze_run` | ✅ | via `trigger_diagnosis` | via `get_recommendations` | ❌ |
| **`apply_fix`** | ❌ | **✅** | ❌ | ❌ |
| Entrega no IDE | MCP | MCP | MCP | Slack / Email / UI |
| Dashboard visual | ✅ HyperDX | ❌ | ❌ | ✅ UI rica |

---

### 🤖 Pipeline LLM/AI

| Dimensão | spike/apex-v0.1 | cowork | kimi | DataFlint |
|----------|-----------------|--------|------|-----------|
| Framework | CrewAI | Crew.ai | sem LLM (T1/T2) | AI proprietária |
| Agentes | Diagnostic Analyst → Recommendation Writer | MetricsAnalyzer → RecommendationWriter | — | — |
| LLM obrigatório | Opcional | **Obrigatório** | Opcional (T3 fallback) | Sim (SaaS) |
| Recomendação com código | ✅ spark.conf + exemplos | ✅ + apply_fix | ✅ runbooks JSON | ✅ sugestões AI |
| Custo por diagnóstico | LLM API (opcional) | LLM API (sempre) | quase zero (sem LLM) | SaaS pricing |

---

### 🧪 Qualidade de Engenharia

| Dimensão | spike/apex-v0.1 | cowork | kimi | DataFlint |
|----------|-----------------|--------|------|-----------|
| Testes | ✅ fake Spark + fake ClickHouse | ✅ 40 testes (Mundo A) | ✅ unit + integration | N/A |
| Workloads sintéticos | **6** (skew, shuffle, gc, oom, cross_join, cache_heavy) | 1 (skew) | 3 (skew, spill, memory) | N/A |
| Baseline negativo | ✅ (aceita app saudável) | ❌ | ✅ `no_skew_baseline.yaml` | N/A |
| Gestão de projeto | `uv` + pyproject.toml | pip + requirements.txt | pip | N/A |
| CI/CD | não confirmado | scenario-gate.yml + oracle-weekly.yml | não confirmado | CI interno SaaS |
| ADRs documentados | não confirmado | ✅ ADR-005 | não confirmado | N/A |
| Documentação | README + comentários | ADR-005 + VALIDACAO.md | benchmarks medidos | Docs SaaS |

---

### 💰 Viabilidade e Custo

| Dimensão | spike/apex-v0.1 | cowork | kimi | DataFlint |
|----------|-----------------|--------|------|-----------|
| Custo de infra | Docker local (gratuito) | Docker local (gratuito) | Docker local (gratuito) | 💰 SaaS (pago) |
| Custo LLM por run | API (opcional) | API (sempre) | ~zero | Incluído no SaaS |
| Vendor lock-in | Nenhum | Nenhum | Nenhum | Alto (SaaS cloud) |
| Suporte cloud gerenciado | ❌ | ❌ | ❌ | ✅ |
| Databricks nativo | ❌ | ❌ | ❌ | ✅ |
| Privacidade de dados | ✅ dados locais | ✅ dados locais | ✅ dados locais | ❌ dados na nuvem |

---

### 🚀 Maturidade e Produção

| Dimensão | spike/apex-v0.1 | cowork | kimi | DataFlint |
|----------|-----------------|--------|------|-----------|
| Maturidade geral | **Alta** | Média | Média | Alta (produto) |
| Pronto para produção | Quase (falta CI) | Não (sem validação) | Não (poucos detectores) | ✅ produto |
| Extensível | ✅ YAML config | Médio | Médio | ❌ caixa preta |
| Comunidade/OSS | Privado | Privado | Privado | Proprietário |

---

## Pontuação Resumida

> Escala: 0–5 por categoria. **Avaliador: Cowork (Claude).**

| Categoria | spike/apex-v0.1 | cowork | kimi | DataFlint |
|-----------|:---:|:---:|:---:|:---:|
| Cobertura de detectores | **5** | 1 | 3 | 5 |
| Velocidade de diagnóstico | 3 | 2 | **5** | 3 |
| Qualidade / falsos positivos | 4 | 2 | **5** | 3 |
| MCP + IDE integration | 4 | **5** | 3 | 1 |
| Maturidade de engenharia | **5** | 3 | 4 | 4 |
| Extensibilidade | **5** | 3 | 3 | 1 |
| Custo total de operação | **5** | **5** | **5** | 1 |
| **TOTAL** | **31** | **21** | **28** | **18** |

> **Nota metodológica final (Cowork / Claude):** O score do `cowork` é provavelmente subestimado em "MCP integration" porque valorizei o `apply_fix` — que foi minha própria contribuição. Leitores devem considerar que a branch `kimi` e `spike` são mais confiáveis para pipeline de detecção sem bias de quem avaliou.
