# Rascunhos de Comentarios para Issues e ADRs

Este documento guarda textos publicados no inicio do estudo e novos rascunhos
que ainda dependem de revisao.

A issue #29 ja existe. Os blocos marcados como rascunho abaixo nao foram
publicados. O objetivo e revisar o texto na branch antes de alterar o historico
oficial das issues.

Contexto correto:

- o estudo foi validado localmente pelo Augusto;
- a branch existe para dar visibilidade, autonomia, rastreabilidade e validacao coletiva;
- a Crew A ainda precisa revisar e decidir se este padrao deve seguir;
- os comentarios abaixo usam `Refs`, nao `Closes`, porque nao fecham as issues maiores.

Branch de referencia:

```text
gustocezar/feature/desacoplamento-geradores
```

## Rascunho de atualizacao da issue #29

Publicar este comentario somente depois que os novos documentos receberem commit
e push na branch.

```md
## Atualizacao do material para validacao

O estudo ganhou uma camada de cobertura e arquitetura sem ampliar o que
consideramos validado.

### O que foi acrescentado

- inventario executavel de campos do Spark event log;
- relatorio empirico sobre o corpus atual;
- fronteira de observabilidade do event log;
- drill-down da solucao do contexto do produto ate task metrics;
- sequencia detalhada do slice atual;
- sequencia da arquitetura alvo com ClickHouse, AST e Tier 2.

### Estado correto da validacao

| Capacidade | Estado |
|---|---|
| `skew_on_join_30x` | Validado localmente |
| Watcher e Oraculo de skew | Validados |
| Inventario do event log | Executado sobre uma aplicacao |
| Spill, CPU, GC e shuffle write | Campos observados; sem diagnostico validado |
| UDF, RDD, AST Classifier e CodeGrounder | Propostos; nao testados |
| ClickHouse, RAG e Tier 2 | Arquitetura em discussao |

O unico anti-pattern diagnosticado de ponta a ponta continua sendo skew em
join. O inventario mostra oportunidades de parsing e novos scenarios; ele nao
prova que esses novos diagnosticos funcionam.

### Novos documentos para revisao

- `docs/specs/event-log-coverage-inventory-v1.md`
- `docs/coverage/apex-coverage-report-v1.md`
- `docs/architecture/event-log-observability-boundary.md`
- `docs/architecture/apex-solution-drilldown.md`
- `docs/coverage/README.md`

Peco que a Crew A revise principalmente:

1. se a separacao entre validado, observado e proposto esta correta;
2. se o fluxo macro representa a arquitetura desejada;
3. se ClickHouse deve armazenar logs brutos, modelo normalizado e Findings;
4. qual scenario deve ampliar o corpus depois do baseline sem skew.
```

## Rascunho de resposta ao comentario sobre RAG e ClickHouse

Resposta sugerida para o comentario de Josenyldo na issue #29:

```md
Obrigado, Josenyldo. A ideia de manter no ClickHouse um corpus de execucoes de
referencia faz sentido para dar historico, rastreabilidade e uma base comum ao
Oraculo.

Eu separaria duas responsabilidades:

1. O Oraculo compara metricas de forma deterministica, por exemplo operador de
join, hot task, skew ratio, volume e tolerancia.
2. Uma RAG recupera execucoes semelhantes, Findings anteriores e documentacao
para enriquecer a explicacao.

Assim, a RAG ajuda com contexto, mas nao decide sozinha se o log sintetico e fiel
ao real. Antes disso, precisamos definir no ClickHouse a identidade do scenario,
versao do Spark/runtime, provenance, metricas comparaveis e criterio para marcar
uma execucao como referencia confiavel.

Vou levar esse ponto para a revisao da Crew A como parte da arquitetura alvo. No
slice atual, a comparacao continua usando o `real_log.ndjson` versionado.
```

## Issue do slice

Titulo sugerido:

```text
Validar slice skew_on_join_30x v4 corrigido com a Crew A
```

Corpo sugerido:

```md
## Contexto

Esta issue registra a revisao do slice `skew_on_join_30x` v4 corrigido, preparado na branch:

`gustocezar/feature/desacoplamento-geradores`

O objetivo e usar a estrutura do GitHub para dar visibilidade, autonomia, rastreabilidade e validacao coletiva ao estudo feito localmente pelo Augusto.

A validacao atual foi feita localmente durante o estudo. Esta issue existe para a Crew A revisar, reproduzir, questionar e decidir se este padrao deve seguir como referencia para os proximos slices do Apex.

## O que este slice cobre

- scenario declarativo em YAML;
- gerador de log sintetico;
- watcher deterministico para `shuffle_skew`;
- oraculo comparando sintetico contra log real versionado;
- testes automatizados;
- gate inicial de CI;
- documentacao tecnica, playbook, linhagem e guia didatico para revisao do time.

## Evidencia local atual

```text
synthetic ratio: 27.9x
real ratio:      29.5x
watcher:         GATE VERDE
oracle:          sintetico fiel ao Spark real dentro da tolerancia
```

Essa evidencia mostra que o log sintetico ficou proximo do comportamento observado no Spark real para este cenario especifico.

## Documentos para revisao

- `README.md`
- `docs/team-validation-guide.md`
- `docs/apex-v4-lineage.md`
- `docs/specs/skew-slice-v4.md`
- `docs/playbooks/skew-slice-v4.md`
- `docs/agentspec-alignment.md`

## Decisoes esperadas da Crew A

- validar se este padrao de slice faz sentido para o Apex;
- decidir se scenarios declarativos devem guiar os proximos anti-patterns;
- decidir se o fork `gustocezar/dataship-spark-plat-v0` segue como repo de evidencia reproduzivel;
- confirmar o contrato de coleta nao-intrusiva via event log nativo do Spark;
- escolher o proximo passo tecnico apos a revisao.

## Fora de escopo desta issue

Este slice ainda nao prova:

- todos os anti-patterns do Apex;
- baseline sem skew;
- confidence madura baseada em evidencia;
- persistencia em ClickHouse;
- comentario automatico em PR;
- implementacao final do core em Go.

## Proximos passos sugeridos apos validacao

Se a Crew A aprovar a abordagem:

- criar `scenarios/no_skew_baseline.yaml`;
- adicionar `validation_criteria` ao scenario;
- melhorar o calculo de `confidence`;
- criar Action semanal do oraculo contra log real versionado;
- desenhar schema ClickHouse para Findings;
- repetir o mesmo padrao para novos anti-patterns.

## Issues relacionadas

Refs #9 #16 #17 #19 #21 #23 #25
```

## Comentarios nas issues

### #9 - Data Generator

```md
Atualizacao de estudo local do Augusto:

A branch `gustocezar/feature/desacoplamento-geradores` organiza um primeiro slice de gerador para o cenario `skew_on_join_30x`.

O objetivo nao e fechar esta issue ainda, mas dar visibilidade para a Crew A revisar uma primeira abordagem com:

- scenario declarativo em YAML;
- geracao de event log sintetico;
- comparacao contra log real versionado;
- testes e documentacao.

A validacao atual foi feita localmente. Proximo passo: revisao da Crew A para decidir se este padrao deve orientar os proximos scenarios do Apex.
```

### #16 - Spark History Parser

```md
Atualizacao de estudo local do Augusto:

O slice `skew_on_join_30x` inclui um parser inicial em `apex/apexlib.py`, usado para ler event logs, identificar operador de join, stage relevante e sinais de skew.

Isso ainda nao cobre todo o escopo do parser do Apex, mas serve como primeira evidencia pratica para revisao da Crew A.

A intencao e usar a branch como trilha de validacao: o que ja funciona, o que precisa evoluir e quais contratos devem ser preservados.
```

### #17 - Watcher / Classifier / Judger

```md
Atualizacao de estudo local do Augusto:

A branch adiciona um primeiro Watcher deterministico para `shuffle_skew`.

Ele emite um Finding com:

- stage;
- severity;
- confidence inicial;
- evidence;
- root cause;
- recommendations.

Este trabalho nao resolve ainda Classifier/Judger. Ele cria uma primeira fatia revisavel para a Crew A validar se o padrao de Watcher por scenario faz sentido para o Apex.
```

### #19 - Local Bootstrap Platform

```md
Atualizacao de estudo local do Augusto:

O estudo usou o projeto `dataship-spark-plat-v0` como base de evidencia reproduzivel.

Minha recomendacao para discussao com a Crew A e manter o fork `gustocezar/dataship-spark-plat-v0` como repo de evidencia no curto prazo, enquanto o Apex recebe apenas a parte curada: scenario, parser, watcher, oraculo, testes e docs.

Isso ajuda a preservar rastreabilidade sem misturar toda a plataforma experimental dentro do Apex antes da decisao coletiva.
```

### #21 - CI Integration

```md
Atualizacao de estudo local do Augusto:

A branch adiciona um primeiro `scenario-gate.yml` para executar testes e validar o slice em CI.

Isso ainda nao implementa comentario automatico em PR nem integracao completa de code review. E apenas um primeiro gate para dar visibilidade e tornar a validacao reproduzivel.

Proximo passo apos revisao da Crew A: decidir se esse gate evolui para multiplos scenarios e integracao com comentarios em PR.
```

### #23 - Shadow Repo Governance

```md
Atualizacao de estudo local do Augusto:

O estudo reforca uma opcao intermediaria de governanca: manter o fork como repo de evidencia reproduzivel e levar para o Apex apenas a parte curada.

Proposta para discussao:

- fork `gustocezar/dataship-spark-plat-v0`: evidencia, reproducao e historico do estudo;
- repo `luanmorenommaciel/apex`: slice curado, documentacao, contratos e decisoes oficiais.

Isso da visibilidade e autonomia sem transformar o Apex em copia integral da plataforma experimental antes da validacao da Crew A.
```

### #25 - Commander Attention Governance

```md
Atualizacao de estudo local do Augusto:

A branch `gustocezar/feature/desacoplamento-geradores` cria uma evidencia concreta para apoiar a decisao de governanca sobre o uso do `dataship-spark-plat-v0`.

A validacao atual foi feita localmente. O proximo passo e revisao da Crew A para decidir se seguimos com o modelo:

`repo de evidencia reproduzivel -> slice curado no Apex -> validacao coletiva via PR/issues`.

Esse fluxo usa GitHub para dar visibilidade, autonomia e rastreabilidade ao estudo antes de qualquer decisao definitiva.
```

## Comentarios nas ADRs

### #5 - ADR-001 Onde o Apex roda?

```md
Nota de estudo local:

O slice `skew_on_join_30x` reforca a direcao de Apex externo e nao-intrusivo.

A prova atual le event logs versionados, nao ClickHouse ainda. Mesmo assim, ela preserva o contrato arquitetural desejado:

- sem JAR customizado;
- sem listener injetado;
- sem alteracao de `SparkSession` do cliente;
- analise feita fora do ciclo de vida do job Spark.

Proximo passo apos validacao da Crew A: conectar esse padrao ao caminho ClickHouse definido pela ADR.
```

### #6 - ADR-002 Tier 2

```md
Nota de estudo local:

Esta ADR estava bloqueada por falta de evidencia empirica. O slice `skew_on_join_30x` comeca a reduzir esse bloqueio, porque entrega:

- um scenario controlado;
- um Watcher deterministico;
- comparacao com log real;
- evidencia reproduzivel.

Ainda nao e suficiente para definir threshold de Tier 2. Minha sugestao e usar este slice como primeira amostra e seguir com mais scenarios antes de decidir escalonamento para classificador pesado.
```

### #7 - ADR-003 Estado historico

```md
Nota de estudo local:

O Finding emitido pelo Watcher sugere campos uteis para o futuro schema historico no ClickHouse:

- watcher;
- stage;
- severity;
- confidence;
- evidence;
- root_cause;
- recommendations;
- scenario_hash;
- provenance.

O slice ainda nao grava estado historico. Ele apenas ajuda a tornar o contrato de saida mais concreto para a Crew A revisar antes do primeiro desenho de tabela.
```

### #8 - ADR-004 Linguagem dos componentes

```md
Nota de estudo local:

O slice atual usa Python como laboratorio e spec executavel, nao como decisao final de core.

Isso nao precisa conflitar com a decisao de Go para componentes de infraestrutura. Minha leitura:

- Python: estudo, validacao, fixtures, prototipacao e documentacao executavel;
- Go: possivel caminho para core, Collector e componentes de producao apos validacao.

A Crew A pode usar o slice para aprender e validar contrato antes de portar partes maduras para Go.
```

### #22 - Go as language for OTel Collector

```md
Nota de estudo local:

O slice `skew_on_join_30x` nao altera a decisao sobre Go no OTel Collector.

Ele atua antes, como evidencia de diagnostico sobre event logs Spark. A parte de Collector continua podendo seguir em Go conforme a ADR.

Ponto de integracao futuro: garantir que o Collector e o pipeline de storage preservem os dados necessarios para Watchers como este operarem sobre ClickHouse.
```

### #24 - Intentional deprioritization

```md
Nota de estudo local:

O slice da uma evidencia concreta de que a estrategia de baseline antes de divergencia trouxe valor.

Em vez de cada pessoa seguir por um caminho isolado, o estudo gerou uma fatia revisavel com:

- contrato declarativo;
- evidencia local;
- log real;
- testes;
- documentacao;
- proposta de validacao pela Crew A.

Isso nao encerra a discussao, mas ajuda o time a avaliar a decisao com artefato concreto em vez de apenas intencao.
```
