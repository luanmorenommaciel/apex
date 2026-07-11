# Apex — Roadmap de Versões: do Provado à Solução Única Autônoma

> **Data:** 2026-07-10 · **Princípio (L9 do Commander):** mínimo viável de cada
> componente, evolução declarada — cada pendência e cada ponto de honestidade dos
> Captain's Reports tem dono de versão. Nada some: ou está sanado, ou está agendado.
>
> Spec de referência: `docs/specs/apex-v1-spec-reproducivel.md` · Decisão: `docs/adr/ADR-006`

---

## V0.1 — "Provado" (estado atual + dias)

**O que é:** o pipeline validado fim a fim com dado real (gates G0–G5), operado
manualmente por uma pessoa. É a versão que se APLICA JÁ — demo, uso interno pelo
Captain, material de decisão.

**Capacidades:** 5 detectores determinísticos · T1 em ms/zero tokens · validator
7 regras · baseline anti-falso-positivo · Crew.ai fallback · MCP no IDE com
`apply_fix` (backup+diff) · oráculo sintético vs real · 52 testes · CI Mundo A.

**Sana nesta versão (itens de horas):**

| Problema (origem) | Ação |
|---|---|
| Demo IDE não executada ponta a ponta no IDE (honestidade 10/07) | Executar no Claude Code com o MCP já registrado; gravar o roteiro `demo-apply-fix-g5.md` |
| Comentários #17/#19/#20/#21 pendentes desde junho (honestidade) | Postar usando os 2 Captain's Reports como material |
| G6 sem infra (bloqueio) | Opção (c): oráculo agendado local (Task Scheduler) — vigia existe HOJE, migra p/ runner no V1 |
| História git com commits descartados (honestidade) | Sanado — íntegra verificada; lição documentada na spec §6 |

**Critério de saída:** demo executada no IDE + issues comentadas + oráculo local rodando.

---

## V1 — "Solução Única Mínima Viável" (pós-martelo ADR-006, ~2 sprints)

**O que é:** as 4 branches viram UM repositório operável pelo time inteiro —
`docker compose up` → jobs monitorados → findings no IDE de qualquer engenheiro.
Autonomia de *detecção* (contínua, sem humano); ação ainda humana ("aplica?").

**Sana nesta versão:**

| Pendência | Ação |
|---|---|
| Divergência das 4 branches | Merge físico conforme ADR-006; branches antigas arquivadas |
| A02 — loader Go do spike escreve schema próprio | Migrar para `apex.*` (contrato v1) — destrava a base falar com o diagnóstico |
| Watch não é contínuo | `log_poller` → ingest → validator → T1 automático a cada job (Spark Envy gerando carga) |
| P1-7 chave de join hardcoded · P2-8 confiança arbitrária | Chave extraída do plano; confiança derivada de evidência (margem sobre threshold) — benchmarks A06 dão a base |
| P2-11 sem critério prototype→validated | Critério = G1+G2+G3 verdes por cenário; `skew_on_join_30x` promovido primeiro |
| CI só Mundo A | Gate para Mundo B (`listener_*.yaml` executados contra o pipeline V1) |
| G6 local é frágil | Self-hosted runner (opção a) numa máquina do time |
| A07 thresholds espalhados | Tudo em `diagnostics.yaml`, runbooks JSON do kimi convertidos |
| Viés de autoavaliação (honestidade) | Rodada 2 do campeonato: spec reproduzível, re-score pelo Commander/time |

**Critério de saída:** um repo, um schema, watch contínuo, qualquer membro do time
roda a demo em <10 min, DataFlint-gap reduzido (5→8 detectores).

---

## V2 — "Autônoma Supervisionada" (Sprint 3–4)

**O que é:** o sistema detecta, diagnostica, **gera E valida o próprio fix** —
o humano só aprova o diff. Resolve a maior crítica de honestidade do V0.1.

**Sana nesta versão:**

| Problema | Ação |
|---|---|
| Fix gerado exigiu revisão humana — 2 bugs (honestidade 10/07) | **Loop de auto-validação do apply_fix:** fix gerado → `py_compile`/lint → re-submit em sandbox (Spark Envy) → re-diagnóstico limpo → SÓ ENTÃO propõe o diff. O ciclo detectar→corrigir→provar que fizemos manualmente em 10/07 vira automático |
| Bridge por polling (ADR-005) | JAR Scala `SparkListener` real-time, fail-safe (L3), métricas direto no ClickHouse |
| Cobertura 5-8 vs ~14 do DataFlint | Detectores restantes (small_files, broadcast_miss, serialização, executor sizing...) — cada um com cenário + baseline pelo funil de gates |
| Sem visibilidade agregada | Dashboard (A08/HyperDX): frota de jobs, findings, custo economizado |
| kimi-Go parado | Se compilar e passar gates, vira o T1 de alta frequência (~136ms alvo) |

**Critério de saída:** fix proposto já vem com prova de execução anexa; latência
detecção→proposta < 5 min sem intervenção.

---

## Visão — "Autônoma" (a parte que o Luan chamou de "onde vai o tempo")

**O que é:** a camada agêntica completa. O humano define política; o sistema opera.

- **Memória e aprendizado:** fixes aceitos/rejeitados alimentam runbooks (RAG);
  recomendações melhoram com o histórico do próprio cluster.
- **Shift-left total:** finding vira **PR automático** com fix validado + evidência
  — o "aplica nossa sugestão" acontece no code review, antes da produção.
- **Simulação:** "rode com o novo código" — estima o efeito do fix pelas
  estatísticas capturadas antes de executar (ideia do Luan, 30/06).
- **Multi-agent pleno:** Watcher→Classifier→Coordinator→Judge com orçamento de
  custo por severidade; on-prem LLM para ambientes fechados (pergunta do Augusto, 30/06).
- **Limite deliberado:** mudança de código em produção SEMPRE passa por aprovação
  humana — autonomia é do pipeline (detectar→diagnosticar→propor→provar), não do deploy.

---

## Regra de evolução

Nenhum item pula de versão sem passar pelo funil: cenário + baseline + gate verde +
registro no framework. Todo problema novo descoberto entra nesta tabela com dono de
versão — o documento é vivo e auditado a cada Captain's Report.
