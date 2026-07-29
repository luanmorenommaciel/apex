# Plano de entrega por PR

> ## ⓘ HISTORICAL — this plan was executed. Do not follow it as a live plan.
>
> Written 2026-07-23, before the lanes were built. **Waves 0–1 shipped** as PRs #44–51
> (`git log --merges`). The plan is kept because it records how eight concurrent lanes were
> organized, which is a genuinely reusable result — not because it describes remaining work.
>
> **Where reality diverged:**
> - Two lanes it does not mention were added mid-build: **`memory/`** (⑦ recall) and
>   **`verify/`** (⑧ refute). `verify` turned out to be the lane that most distinguishes the
>   product — it refuted Apex's own headline finding.
> - The contract went **v0.2 → v0.4** and grew **seven cross-lane rules**, every one discovered
>   by an implementation contradicting the spec.
> - Delivery ran as parallel agent sessions against a frozen contract rather than as sequenced
>   PR waves. Result: 50+ commits, eight lanes, **zero merge conflicts**.
>
> **Current state:** [`../../README.md`](../../README.md) ·
> [`../../PIPELINE.md`](../../PIPELINE.md) · [`../../CHANGELOG.md`](../../CHANGELOG.md)
> · lane briefs in [`../lanes/`](../lanes/)

**Base de todos os PRs:** `origin/feat/base-project-e2e` (`9d51aca`)

Os nomes abaixo são propostas. Nenhuma branch remota ou PR foi criado.

## Ondas

### Onda 0: alinhamento

| PR | Branch | Escopo | Aceite | Modelo |
|---|---|---|---|---|
| 0 | `docs/v1-swimlanes-contracts` | arquitetura, contratos, gates e decisões | Luan confirma o escopo da V1 | Sol Alto |

### Onda 1: raias fundamentais

Estas branches podem evoluir em paralelo depois do PR 0.

| PR | Branch | Reaproveitamento local | Aceite | Modelo |
|---|---|---|---|---|
| 1 | `jar/spark-4.1.2-plugin` | matriz sbt, plugin, AQE, fail-safe | build 4.1.2 e job real sem bloquear driver | Sol Alto |
| 2 | `dev/spark-4.1.2-env` | Docker, MinIO, History e patologias | ambiente novo reproduz os quatro cenários | Sol Médio |
| 3 | `collect/otlp-contract-v02` | Collector C3, scrub e roteamento | span de teste vira linha sanitizada | Sol Médio |
| 4 | `infra/canonical-clickstack` | DDL, MV, ClickHouse e HyperDX | schemas e consultas por `job_id` | Sol Médio |
| 5 | `engine/deterministic-diagnostics` | watchers, validator e sink | baseline limpo e patologias detectadas | Sol Alto |
| 6 | `serve/mcp-readonly` | MCP stdio, `analyze_run`, `compare_runs` | cliente MCP real consulta ClickHouse | Sol Médio |

### Onda 2: integração

| PR | Branch | Escopo | Aceite | Modelo |
|---|---|---|---|---|
| 7 | `e2e/six-lane-canonical-gates` | C6, C7, bootstrap de teste e artifacts | job cruza as seis raias; quatro patologias passam | Sol Alto |

### Onda 3: loop agêntico

| PR | Branch | Escopo | Aceite | Modelo |
|---|---|---|---|---|
| 8 | `engine/crew-judge-gated` | política, provider e contrato do Judge | cita evidência; fallback determinístico | Sol Alto |
| 9 | `serve/guarded-fix-loop` | suggest, preview, apply, rerun e compare | nenhuma mutação sem aprovação; before/after real | Sol Alto |

### Onda 4: produto

| PR | Branch | Escopo | Aceite | Modelo |
|---|---|---|---|---|
| 10 | `product/local-commander-ui` | UI local da jornada do job | demo navegável, conteúdo escapado | Sol Médio |
| 11 | `product/bootstrap-doctor-ci` | instalação, doctor, secrets e CI | máquina nova executa o runbook | Sol Alto |
| 12 | `docs/v1-demo-dataflint` | README, one-slide, demo e comparativo | apresentação de três minutos | Terra Médio |

## Mapeamento dos commits locais

| Capacidade | Commits de referência | PR de destino |
|---|---|---|
| engine e ClickHouse | `999ad84`, `e0b419d` | PR 5 |
| MCP read-only | `abe9443` | PR 6 |
| matriz e plugin | `ab17060`, `1eea18c`, `4d18175`, `4b5cd83` | PR 1 |
| imagem e runtime dev | `e59a0fa`, `3138e64` | PR 2 |
| Collector e ClickStack | `027a750` | PRs 3 e 4 |
| AQE | `801af42` | PR 1 |
| gates E2E | `de56ed1`, `9261c17` | PR 7 |
| retirada JSONL | `50c94d0`, `0f71ce5` | PRs 1, 2 e 7 |

Os commits servem como fonte. Cada branch nova recebe somente os arquivos da
raia correspondente e ganha um commit próprio.

## Ordem de merge

```text
PR 0
├── PR 1 jar ─────┐
├── PR 2 dev ─────┤
├── PR 3 collect ─┤
├── PR 4 infra ───┼── PR 7 integração
├── PR 5 engine ──┤       ├── PR 8 Judge
└── PR 6 serve ───┘       └── PR 9 fix loop
                                  ├── PR 10 UI
                                  ├── PR 11 instalável/CI
                                  └── PR 12 apresentação
```

PRs 3 e 4 podem ser revisados em paralelo, mas o teste de integração exige os
dois. PRs 5 e 6 usam fixtures até o ClickHouse real ficar disponível.

## Template de aceite

Cada PR deve responder:

- qual raia é dona da mudança;
- quais campos do contrato consome e produz;
- quais arquivos pertencem ao escopo;
- quais testes passaram;
- qual execução real foi feita;
- quais limitações permanecem;
- como reverter;
- se existe impacto de segurança, custo ou segredo.

## Política de evidência

- versionar resumos curtos em `evidence/`;
- publicar logs extensos como artifact de CI;
- não transportar logs históricos brutos para os PRs;
- não usar evidência da branch Codex como prova do código portado;
- repetir o gate após cada merge relevante.

## Modelos

| Tipo de trabalho | Modelo |
|---|---|
| contrato, arquitetura, Scala/SparkListener, segurança, Judge e apply | Sol Alto |
| Docker, Collector, ClickHouse, MCP read-only e UI | Sol Médio |
| revisão mecânica, diagramas derivados e apresentação | Terra Médio |
| formatação, links e limpeza textual | Terra Leve |

O modelo pode descer de nível depois que testes e contratos delimitarem a
tarefa. Falhas de integração, concorrência ou segurança voltam para Sol Alto.
