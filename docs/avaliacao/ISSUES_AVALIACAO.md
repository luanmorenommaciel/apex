# Issues da Avaliação Comparativa — 4 Soluções Apex

> Gerado por: **Cowork (Claude / Anthropic)** — 2026-07-07  
> Origem: Avaliação comparativa entre spike/apex-v0.1, cowork, kimi e DataFlint  
> Para criar no GitHub: `luanmorenommaciel/apex` ou `gustocezar/apex-workspace`

---

## [ISSUE-A01] Portar 4 detectores ausentes do spike/apex-v0.1

**Labels:** `enhancement`, `v1`, `detector`, `type:spike→main`  
**Prioridade:** P0 — blocker para V1  
**Identificado por:** Cowork (Claude)

### Problema

O `cowork` e o `kimi` têm apenas 1-3 detectores enquanto o `spike/apex-v0.1` (Aguimar) já implementou 5. Jobs reais em produção falham por GC pressure, shuffle excessivo e OOM — não apenas skew.

### Detectores a portar

- `detect_shuffle` — warning 256MiB / critical 1GiB de shuffle bytes
- `detect_plans` — re-planning AQE (>3 re-plans = INFO)
- `detect_gc` — pressão de GC (>10% warn / >20% crit)
- `detect_oom` — OOM kill events no event log

### Acceptance criterion

- Todos os 5 detectores do spike funcionando na pipeline principal (ClickHouse → MCP)
- `diagnostics.yaml` como fonte única de thresholds
- Testes unitários para cada detector

### Referência

`spike/apex-v0.1/src/detectors/` (branch `spike/apex-v0.1`, commit `53479f5`)

---

## [ISSUE-A02] Adotar Go eventlog-loader como substituto do log_poller Python

**Labels:** `enhancement`, `v1`, `infra`, `type:spike→main`  
**Prioridade:** P1  
**Identificado por:** Cowork (Claude)

### Problema

O `log_poller` Python de 15s usado em `cowork` e `kimi` é suficiente para protótipo mas não para volume de produção. O `spike/apex-v0.1` implementou um loader em Go: concorrente, sem GIL, baixo footprint de memória.

### O que fazer

- Revisar Go eventlog-loader do spike (branch `spike/apex-v0.1`)
- Integrar como default no pipeline principal
- Manter log_poller Python como fallback opcional (ambientes sem Go)

### Acceptance criterion

- Go loader processa event logs do MinIO sem degradação sob carga de 10 jobs/min
- CI valida build do Go loader

---

## [ISSUE-A03] Implementar EvidenceValidator como gate obrigatório antes do LLM

**Labels:** `enhancement`, `v1`, `quality`, `type:kimi→main`  
**Prioridade:** P1  
**Identificado por:** Cowork (Claude)

### Problema

O `cowork` não tem gate de qualidade antes de acionar o Crew.ai — qualquer finding chega ao LLM, gerando falsos positivos e custo desnecessário de API. O `kimi` implementou um EvidenceValidator com 7 regras formais (198ms, 7/7 precisão medida).

### O que fazer

- Portar EvidenceValidator do kimi para a pipeline principal
- Validar finding antes de chamar Crew.ai
- Findings rejeitados pelo validator: descartar silenciosamente ou logar em `rejected_findings`

### Acceptance criterion

- Falso positivo rate = 0 nos workloads sintéticos existentes
- Baseline negativo (`no_skew_baseline.yaml`) passa sem disparar alerta
- Latência do validator < 300ms (benchmark kimi: 197ms)

### Referência

`kimi/src/validator/evidence_validator.py` (branch `gustocezar/feature/kimi-desacoplamento-geradores`)

---

## [ISSUE-A04] Adicionar baseline negativo como teste de regressão obrigatório

**Labels:** `test`, `quality`, `type:kimi→main`  
**Prioridade:** P1  
**Identificado por:** Cowork (Claude)

### Problema

Apenas o `kimi` tem um `no_skew_baseline.yaml` que valida que job saudável não dispara alarme. Sem este teste, qualquer mudança nos thresholds pode introduzir falsos positivos silenciosamente.

### O que fazer

- Criar baseline negativo para cada anti-pattern (skew, shuffle, gc, oom, plans)
- Adicionar ao CI: se qualquer baseline disparar alerta → PR bloqueado

### Acceptance criterion

- 5 baselines negativos (um por detector)
- CI valida que nenhum baseline dispara `CRITICAL` ou `WARNING`

---

## [ISSUE-A05] Portar apply_fix para spike/apex-v0.1 como MCP tool #7

**Labels:** `enhancement`, `v1`, `mcp`, `type:cowork→spike`  
**Prioridade:** P1  
**Identificado por:** Cowork (Claude)

### Problema

O `apply_fix` existe apenas no `cowork` e é a única feature que fecha o ciclo diagnóstico → IDE → correção. Nenhuma outra branch — nem o DataFlint — tem equivalente. Deve ser portado para o spike como a 7ª MCP tool.

### O que fazer

- Portar `apply_fix` do cowork para o spike
- `apply_fix(app_id, finding_id, confirmation)` → aplica configuração recomendada no arquivo `spark_submit.sh` ou `spark_conf.yaml` do engenheiro

### Acceptance criterion

- `apply_fix` disponível no MCP server do spike
- Requer confirmação explícita antes de modificar arquivo
- Teste de integração: diagnóstico → apply_fix → job re-executado com nova config

### Referência

`cowork/src/mcp/tools/apply_fix.py` (branch `gustocezar/feature/cowork-desacoplamento-geradores`)

---

## [ISSUE-A06] Publicar benchmarks de latência por solução

**Labels:** `documentation`, `benchmark`, `observability`  
**Prioridade:** P2  
**Identificado por:** Cowork (Claude)

### Problema

Apenas o `kimi` publicou benchmarks medidos (T1=136ms, Validator=198ms, T2=0.01ms). O `spike` e o `cowork` não têm números. Sem benchmarks, não é possível tomar decisões de arquitetura baseadas em dados.

### O que fazer

- Medir e publicar latência por tier para cada solução no job de referência (`app-20260706035238-0001` ou equivalente)
- Formato: tabela em `docs/benchmarks/LATENCIA_POR_SOLUCAO.md`
- Métricas: T1 (heurística), T2 (LLM), T3 (apply_fix), total pipeline

### Acceptance criterion

- Documento com benchmarks das 3 branches internas
- Metodologia descrita (job de referência, número de runs, p50/p95)

---

## [ISSUE-A07] Unificar thresholds em diagnostics.yaml (migrar de hardcoded para config)

**Labels:** `refactor`, `config`, `extensibility`  
**Prioridade:** P2  
**Identificado por:** Cowork (Claude)

### Problema

O `cowork` tem thresholds hardcoded em código Python. O `spike` usa `diagnostics.yaml` versionado. Para produção, thresholds precisam ser ajustáveis por environment (staging vs prod) sem redeployar código.

### O que fazer

- Mapear todos os thresholds hardcoded do cowork
- Migrar para formato `diagnostics.yaml` (compatível com spike)
- Validar no startup da aplicação

### Acceptance criterion

- Zero thresholds hardcoded no código
- `diagnostics.yaml` aceita seção `environment: staging | prod` com overrides
- Documentação dos thresholds no README

---

## [ISSUE-A08] Avaliar adição de HyperDX como dashboard de observabilidade

**Labels:** `enhancement`, `ui`, `observability`, `type:spike→main`  
**Prioridade:** P3  
**Identificado por:** Cowork (Claude)

### Problema

Apenas o `spike/apex-v0.1` e o DataFlint têm UI visual. O `cowork` e `kimi` são CLI-only. Para adoção por times maiores, um dashboard é necessário — engenheiros não vivem no IDE.

### O que fazer

- Avaliar HyperDX do spike como solução de UI
- Alternativa: Streamlit dashboard sobre ClickHouse (mais leve)
- Decisão deve ser um ADR formal

### Acceptance criterion

- ADR de decisão UI (HyperDX vs Streamlit vs sem UI)
- Se aprovado: dashboard mostrando findings das últimas 24h, latência por tier, jobs mais lentos

---

## Resumo das Issues

| Issue | Descrição | Prioridade | Origem → Destino |
|-------|-----------|:---:|:---:|
| A01 | Portar 4 detectores do spike | P0 | spike → main |
| A02 | Adotar Go eventlog-loader | P1 | spike → main |
| A03 | EvidenceValidator antes do LLM | P1 | kimi → main |
| A04 | Baseline negativo no CI | P1 | kimi → main |
| A05 | apply_fix como MCP tool #7 | P1 | cowork → spike |
| A06 | Publicar benchmarks de latência | P2 | — |
| A07 | Unificar thresholds em YAML | P2 | spike config → cowork |
| A08 | HyperDX como dashboard | P3 | spike → main |

---

*Gerado por: Cowork (Claude / Anthropic) — 2026-07-07*
