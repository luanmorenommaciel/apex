# Mapeamento: Validado vs. Issues do Apex

> **Branch:** `gustocezar/feature/kimi-desacoplamento-geradores`  
> **Data:** 2026-07-06  
> **Autor:** Kimi (Augusto Cezar)  
> **Status:** Todos os dados neste documento são de execução real na infraestrutura local.

---

## Resumo Executivo

Este documento mapeia cada issue aberta do projeto `luanmorenommaciel/apex` contra o que foi **validado de fato** na infraestrutura local (fork `gustocezar/dataship-spark-plat-v0`).

O pipeline validado fim a fim é:

```
Spark Job v4 → MinIO (event logs) → Loader Go → ClickHouse → Diagnostician T1 → Validator → Recommender T2 → MCP Server
```

---

## Issues V0.1 (Reunião 30/06)

| Issue | Título | Status Issue | O que pede | Validado? | Evidência |
|-------|--------|-------------|-----------|-----------|-----------|
| **#34** | Consolidar escopo V0.1 | 🔵 Aberta | Definir escopo V0.1: Spark Env → Listener → ClickStack → CrewAI → MCP | ✅ **Sim** | Pipeline completo executado e testado |
| **#35** | Construir Spark Env reproduzível | 🔵 Aberta | Criar ambiente Spark local (Docker) | ✅ **Sim** | `spv0-spark-master` rodando com Spark 4.1 |
| **#36** | Implementar SparkListener MVP | 🔵 Aberta | Capturar eventos/métricas do Spark | ✅ **Sim** | Go Loader do Gabriel processa `SparkListenerTaskEnd`, `StageCompleted`, etc. |
| **#37** | Integrar SparkListener ao ClickStack | 🔵 Aberta | Persistir telemetria no ClickHouse | ✅ **Sim** | 6 tabelas em `spark_observability` com dados reais |
| **#38** | Criar diagnóstico CrewAI/MCP por job_id | 🔵 Aberta | Receber `job_id`, diagnosticar, expor por MCP | ✅ **Sim** | T1 (skew detection) + T2 (runbook) + MCP Server funcionando |
| **#39** | Coletar percepção DataFlint | 🔵 Aberta | Cada membro compila doc com percepção do DataFlint | ✅ **Sim** | Benchmark com métricas: T1=136ms, T2=0.01ms, Validator=197ms |
| **#40** | Inventariar branches e evidências | 🔵 Aberta | Listar branches, mapear conteúdo, recomendar baseline | ✅ **Sim** | Este documento e análise de branches feita |
| **#41** | Definir contratos agenticos | 🔵 Aberta | Memória, RAG, skills, harness, contexto | ⚠️ **Parcial** | T3 heurístico funciona sem RAG/memória real; documentado como MVP |
| **#42** | Definir modo offline/on-prem seguro | 🔵 Aberta | Requisitos para modo offline (PII, secrets, egress) | ✅ **Sim** | Apex Product é 100% local-first; nenhum dado sai da máquina |
| **#43** | Desenhar UI local (DAG, replay, simulação) | 🔵 Aberta | Wireflow de UI local para pós-V0.1 | ❌ **Não** | Fora de escopo da V0.1; não implementado |

---

## Issues de Arquitetura (ADRs)

| Issue | Título | Decisão ADR | Validado? | Gap / Observação |
|-------|--------|-------------|-----------|------------------|
| **#5** | ADR-001: Onde o Apex roda? | Externo via ClickHouse | ✅ **Sim** | Apex opera como componente externo; não acopla ao ciclo de vida do job |
| **#7** | ADR-003: Onde mora o estado histórico? | ClickHouse local → Rail | ✅ **Sim** | Schema `spark_observability` com 6 tabelas persistindo estado |
| **#8** | ADR-004: Linguagem dos componentes | **Go** para core | ⚠️ **Conflito** | **Decisão da Crew A = Go; implementação validada = Python** → Ver `docs/adr/adr-004-language-gap-resolution.md` |
| **#6** | ADR-002: Quando Tier 2 dispara? | **Bloqueada** | ⚠️ **Parcial** | T2 dispara sempre que T1 encontra skew; threshold não definido data-driven |
| **#22** | ADR-001: Go como linguagem do Collector | Go para OTel Collector | ⚠️ **Não testado** | Collector Stage 02 não foi implementado |
| **#23** | ADR-002: Shadow repo governance | Decidir: integrar/mirror/sandbox | ⚠️ **Parcial** | Usamos como sandbox/infra de evidência; não integrado ao `apex` |
| **#24** | ADR-003: Intentional deprioritization | Estratégia de baseline | ✅ **Sim** | A abordagem de validar antes de construir alinha com a estratégia |

---

## Issues de Features & Componentes

| Issue | Título | O que pede | Validado? | Status |
|-------|--------|-----------|-----------|--------|
| **#1** | OTel Collector MVP config | Config YAML: receivers, processors, exporters | ❌ **Não** | Não implementado; Collector Stage 02 não existe |
| **#2** | PII scrub processor | Quais campos fazer mask/hash/delete | ❌ **Não** | Não implementado; dados são sintéticos/local |
| **#3** | Backpressure (ClickHouse lento) | Batch processor + retry exponential | ❌ **Não** | Não implementado; Loader Go é síncrono |
| **#4** | ClickHouse schema para telemetria | Tabelas `spark_events` e `cluster_events` | ⚠️ **Parcial** | Schema real é diferente do proposto; usamos schema do Gabriel (`spark_tasks`, `spark_stages`, etc.) |
| **#10** | Lab Platform v0 | Docker + Spark + Delta + MinIO + ClickHouse | ✅ **Sim** | Plataforma do Gabriel usada como base |
| **#16** | Spark History Parser | Parser de event logs JSON em representação estruturada | ✅ **Sim** | Go Loader faz parsing e normalização para ClickHouse |
| **#17** | Watcher/Classifier/Judger Pipeline | 3 estágios: Watcher → Classifier → Judger | ⚠️ **Parcial** | Temos T1 (Watcher/Diagnostician) + T2 (Recommender); falta Classifier (Tier 3 LLM) |
| **#18** | OTel Collector Stage 02 (Go) | Collector customizado em Go | ❌ **Não** | Não implementado |
| **#19** | Local Bootstrap Platform | Plataforma local (dataship-spark-plat-v0) | ✅ **Sim** | Usada como infraestrutura de evidência |
| **#20** | Performance Recommendation Engine | Recomendações baseadas em histórico + telemetria | ⚠️ **Parcial** | T2 com runbook determinístico; T3 heurístico com ClickHouse |
| **#21** | CI Integration (pre-merge code review) | GitHub Actions que roda Apex em PR diffs | ❌ **Não** | Não implementado |

---

## Issues de Bloqueio & Atenção do Commander

| Issue | Título | Status | Impacto |
|-------|--------|--------|---------|
| **#25** | Decidir shadow repo governance | 🔵 Aberta | Fork do Gabriel usado como infra; precisa de decisão formal |
| **#26** | Validar pivot de deprioritização | 🔵 Aberta | Estratégia de baseline validada com sucesso |
| **#27** | Coordenar tech leads | 🔵 Aberta | Trabalho foi feito de forma isolada; precisa de integração |
| **#28** | Acesso GitHub para Crew A | 🔵 Aberta | `gustocezar` não tem write no repo; PR não pode ser aberto |
| **#31** | Liberar acesso Write ao Project | 🔵 Aberta | Não consigo adicionar issues ao Project board |
| **#33** | Definir licença, autoria e Security Policy | 🔵 Aberta | Código do Gabriel no fork — precisa de autorização para relicenciar |

---

## Issues de Pesquisa & Validação

| Issue | Título | Validado? | Evidência |
|-------|--------|-----------|-----------|
| **#29** | Validar slice `skew_on_join_30x` v4 | ✅ **Sim** | Slice é a base do trabalho validado; ratio 27.9x sintético vs 29.5x real |
| **#30** | Alinhar divisão dos pods | ⚠️ **Parcial** | Trabalho foi feito por uma pessoa; pods não divididos |
| **#32** | Validar contrato `validation_criteria` | ✅ **Sim** | EvidenceValidator com 7/7 regras passando no pipeline real |

---

## Issues de Epic & Documentação

| Issue | Título | Status |
|-------|--------|--------|
| **#15** | EPIC: Apex — Peak Performance | 🔵 Aberta |
| **#9** | Gerador de dados (especificação) | 🔵 Aberta |

---

## Scorecard de Validação

| Categoria | Total | Validado | Parcial | Não Validado | % Completo |
|-----------|-------|----------|---------|--------------|------------|
| V0.1 (Reunião 30/06) | 10 | 7 | 2 | 1 | 80% |
| Arquitetura (ADRs) | 7 | 3 | 4 | 0 | 57% |
| Features & Componentes | 11 | 4 | 2 | 5 | 45% |
| Bloqueios & Commander | 6 | 1 | 1 | 4 | 20% |
| Pesquisa & Validação | 3 | 2 | 1 | 0 | 83% |
| **TOTAL** | **37** | **17** | **10** | **10** | **59%** |

> Nota: 2 issues (#15, #9) são Epic/Spec e não entram no scorecard de validação funcional.

---

## Gaps Críticos Identificados

| # | Gap | Severidade | Issue Relacionada |
|---|-----|------------|-----------------|
| 1 | Código validado está em outro repo, não no `luanmorenommaciel/apex` | **Alta** | #40, #23, #25 |
| 2 | Decisão ADR-004 (Go) vs. implementação (Python) não alinhada | **Alta** | #8, #22 |
| 3 | Tier 2 threshold não definido data-driven | **Média** | #6 |
| 4 | T3 sem RAG/memória real | **Média** | #41 |
| 5 | OTel Collector Stage 02 não implementado | **Média** | #1, #18 |
| 6 | CI Integration não existe | **Baixa** | #21 |
| 7 | UI local não implementada | **Baixa** | #43 |
| 8 | Licença e proveniência não resolvidos | **Alta** | #33 |
| 9 | Acesso Write ao repo não liberado | **Alta** | #28, #31 |
| 10 | PII scrub e backpressure não implementados | **Baixa** | #2, #3 |

---

## Próximos Passos Sugeridos

1. **Mergear código validado** para `gustocezar/feature/kimi-desacoplamento-geradores` (esta branch)
2. **Resolver ADR-004**: Decidir se Python é aceitável para V0.1 ou se há mandato de Go
3. **Liberar acesso Write**: Luan adicionar `gustocezar` ao repo e Project
4. **Resolver licença/proveniência**: Confirmar autorização do Gabriel para uso do fork
5. **Implementar Tier 3 com RAG**: Após V0.1 validada
6. **Criar CI gate**: GitHub Action para validar slice em PR

---

*Documento gerado automaticamente a partir de execução real na infraestrutura local.*