# Plano de entrega por PR

**Base de todos os PRs:** `origin/feat/base-project-e2e`

## Estado da entrega em 24/07/2026

O plano abaixo foi a sequência de construção. As PRs fundamentais já foram
mergeadas; as extensões ENGINE/SERVE estão abertas para revisão. Esta tabela é
a fonte rápida para distinguir plano histórico de estado atual.

| Raia/onda | Entrega | Estado | PR |
|---|---|---|---|
| 0 | contratos e raias | mergeada | [#45](https://github.com/luanmorenommaciel/apex/pull/45) |
| 1 | DEV | mergeada | [#47](https://github.com/luanmorenommaciel/apex/pull/47) |
| 1 | JAR | mergeada | [#50](https://github.com/luanmorenommaciel/apex/pull/50) |
| 1 | COLLECT | mergeada | [#49](https://github.com/luanmorenommaciel/apex/pull/49) |
| 1 | INFRA | mergeada | [#48](https://github.com/luanmorenommaciel/apex/pull/48) |
| 1 | ENGINE determinístico | mergeada | [#46](https://github.com/luanmorenommaciel/apex/pull/46) |
| 1 | SERVE read-only | mergeada | [#44](https://github.com/luanmorenommaciel/apex/pull/44) |
| 2 | E2E canônico das seis raias | mergeada | [#51](https://github.com/luanmorenommaciel/apex/pull/51) |
| 3 | ENGINE Crew/Judge com gate | aberta | [#52](https://github.com/luanmorenommaciel/apex/pull/52) |
| 3 | SERVE KB e proposta segura | aberta | [#53](https://github.com/luanmorenommaciel/apex/pull/53) |
| acompanhamento | evidência e ordem de integração | aberta | [#54](https://github.com/luanmorenommaciel/apex/pull/54) |

Após o merge de #52 e #53, a única pendência da V1 é repetir o gate integrado
C9 na base resultante. As ondas 4 e seguintes permanecem propostas de produto,
não compromissos desta entrega.

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
