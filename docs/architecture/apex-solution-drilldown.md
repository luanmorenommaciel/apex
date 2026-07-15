# Apex - Drill-down Completo da Solucao

Este documento apresenta o Apex do contexto de negocio ate a evidencia emitida
por uma task Spark. Ele nasceu no slice `skew_on_join_30x` v4 e continua util
como explicacao de fronteira de observabilidade. Para a fotografia atual da
branch Codex Round2, use tambem `README.md`, `PLANO.md`,
`docs/autoavaliacao.md` e
`docs/architecture/llm-solution-validation-framework-2026-07-15.md`.

## Atualizacao Round2 - 2026-07-15

O slice inicial foi expandido para uma esteira local com:

- G0-G5 fechados com evidencia crua;
- 5 detectores oficiais em G2: skew, GC, shuffle spill, OOM e cartesian product;
- G3 real em Spark multicore: `app-20260712053414-0001`, ratio 29.4x;
- G5 real: finding 1 -> 0 e shuffle 1.157.481 -> 0;
- G3/G5 repetidos na stack autonoma da branch: `app-20260714112858-0003` -> `app-20260714113809-0004`;
- SparkListener JVM real com NDJSON e fail-safe;
- MCP stdio e smoke subprocesso estilo cliente IDE;
- G6 remoto verde no GitHub Actions do campeonato: workflow inteiro `Apex Scenario Gate` passou no commit `6ba5238`;
- gap operacional restante: aprovacao interativa do `apex-commander` em IDE GUI real;
- gap futuro deliberado: Crew.ai/Judge real.

## Legenda de maturidade

| Estado | Significado |
|---|---|
| Validado | Executado localmente, coberto por teste ou comparado com log real |
| Observado | Campo ou evento apareceu no corpus, mas ainda nao existe diagnostico validado |
| Proposto | Direcao arquitetural ou componente ainda sem prova executavel |
| Fora do event log | Exige codigo, profiler, telemetria de infraestrutura ou outra fonte |

## Estado atual em uma frase

```text
O Apex saiu do slice isolado e hoje prova o loop detectar -> corrigir -> rerodar -> limpar.
O caminho deterministico T1 continua sem LLM obrigatorio.
O drift G6 remoto ja foi observado no campeonato; ainda falta transformar isso em produto V1 completo com IDE GUI real e Crew/Judge real.
```

## Visao visual geral

![Apex - fronteira de observabilidade do Spark](assets/spark-event-log-observability-boundary.png)

Esta imagem apresenta as camadas do Spark, os sinais capturados pelo event log e
as fontes complementares. Os diagramas abaixo fazem o drill-down da mesma
solucao. No GitHub, os blocos Mermaid aparecem renderizados dentro deste arquivo.

## Nivel 0 - Contexto do produto

```mermaid
flowchart LR
    USER["Engenheiro de dados"] --> SPARK["Spark ou Databricks"]
    SPARK --> SOURCE["Telemetria nativa"]
    SOURCE --> APEX["Apex"]
    APEX --> FINDING["Finding e recomendacao"]
    FINDING --> USER

    REPO["Repositorio e codigo Spark"] -.-> APEX
    GITHUB["GitHub, CI e issues"] -.-> APEX
    CREW["Crew A"] -->|"revisa e valida"| GITHUB

    classDef validated fill:#dff3df,stroke:#2f7d32,color:#172417
    classDef proposed fill:#eeeeee,stroke:#777777,color:#222222
    class SPARK,SOURCE validated
    class APEX,FINDING,REPO,GITHUB,CREW proposed
```

Leitura:

- o cliente executa workloads Spark;
- a plataforma produz event logs ou outra telemetria;
- o Apex analisa a evidencia fora do ciclo de vida do job;
- a Crew A usa GitHub, testes e documentos para validar cada slice.

O slice atual prova apenas uma parte desse ciclo: event log, skew, Finding e
comparacao com log real.

## Nivel 1 - Fluxo macro da solucao

```mermaid
flowchart LR
    subgraph Inputs["Fontes"]
        EL["Event log Spark"]
        CODE["Codigo e PR"]
        INFRA["Metricas de infraestrutura"]
        PROFILE["Query Profile e system tables"]
    end

    subgraph Evidence["Camada de evidencia"]
        PARSER["Parser de event log"]
        CORR["Evidence Correlator"]
        VALIDATOR["Evidence Validator"]
        AST["Analisador AST"]
        ADAPTER["Adapters de runtime"]
        STORE["ClickHouse e corpus historico"]
    end

    subgraph Diagnosis["Camada de diagnostico"]
        WATCHER["Watchers deterministicos"]
        REF["Reference Selector"]
        ORACLE["Oraculo e quality gates"]
        TIER2["Classifier Tier 2"]
    end

    subgraph Delivery["Entrega"]
        FINDING["Finding"]
        CI["Comentario em PR"]
        HISTORY["Historico e auditoria"]
    end

    EL --> PARSER
    CODE -.-> AST
    INFRA -.-> ADAPTER
    PROFILE -.-> ADAPTER
    PARSER --> CORR
    CORR -.-> VALIDATOR
    VALIDATOR -.-> WATCHER
    PARSER -.-> STORE
    AST -.-> WATCHER
    ADAPTER -.-> WATCHER
    STORE -.-> REF
    REF -.-> ORACLE
    WATCHER --> ORACLE
    WATCHER --> FINDING
    WATCHER -.-> TIER2
    TIER2 -.-> FINDING
    FINDING -.-> CI
    FINDING -.-> HISTORY
    ORACLE --> FINDING

    classDef validated fill:#dff3df,stroke:#2f7d32,color:#172417
    classDef observed fill:#fff3cd,stroke:#b58105,color:#332701
    classDef proposed fill:#eeeeee,stroke:#777777,color:#222222
    class EL,PARSER validated
    class WATCHER,ORACLE,FINDING observed
    class STORE observed
    class CORR,VALIDATOR,REF,CODE,INFRA,PROFILE,AST,ADAPTER,TIER2,CI,HISTORY proposed
```

As linhas continuas representam o caminho exercitado no estudo. As linhas
tracejadas representam integracoes propostas. Watcher, Oraculo e Finding estao
marcados como observados porque funcionam no scenario controlado, mas ainda nao
possuem o gate e a descoberta cega propostos.

## Nivel 2 - Componentes e responsabilidades

| Componente | Responsabilidade | Estado |
|---|---|---|
| Scenario YAML | Descrever dados, sinais esperados, tolerancia e acceptance | Validado para skew |
| Code Generator | Gerar job PySpark e manifesto a partir do scenario | Validado para skew |
| Plan Generator | Gerar event log sintetico com provenance | Validado para skew |
| Spark real | Produzir o log de referencia | Validado para um job de skew |
| `apexlib` | Ler logs, attempts, plano, stages, tasks e provenance | Correlacao por acumuladores validada; app scope e streaming dos consumidores pendentes |
| Coverage Inventory | Listar Spark emite x Apex consome x falta | Validado em uma aplicacao |
| Evidence Validator | Classificar evidencia como valid, invalid ou indeterminate | Proposto na issue #32 |
| Evidence Correlator | Ligar execution, job, stage, operador, acumulador e task | Proposto |
| Skew Watcher | Detectar shuffle skew e emitir Finding | Validado em confirmacao controlada |
| Oraculo | Comparar sinais sinteticos com log real | Validado para tres sinais do skew |
| ClickHouse | Persistir eventos, evidencias e historico | Proposto para este slice |
| RAG | Recuperar casos e documentacao semelhantes | Proposto; nao substitui comparacao numerica |
| AST Classifier | Detectar UDF, RDD e `collect()` no codigo | Proposto |
| CodeGrounder | Ligar evidencia runtime a arquivo e linha | Proposto |
| Tier 2 | Analisar casos ambiguos ou fora das regras | Proposto; ADR continua bloqueada |
| CI Review | Executar Apex e comentar no PR | Gate inicial existe; comentario nao validado |

## Nivel 3 - Caminho executado do slice controlado

```mermaid
flowchart TD
    S["1. Scenario skew_on_join_30x.yaml"] --> CG["2. Code Generator"]
    S --> PG["3. Plan Generator"]
    CG --> JOB["4. Job PySpark e manifesto"]
    PG --> SYN["5. Event log sintetico"]
    JOB --> RUN["6. Execucao Spark real"]
    RUN --> REAL["7. real_log.ndjson"]

    SYN --> LIB["8. apexlib"]
    REAL --> LIB
    LIB --> W["9. Skew Watcher"]
    W --> F["10. Finding"]

    SYN --> O["11. Oraculo"]
    REAL --> O
    O --> RESULT["12. Calibracao dos sinais dentro da tolerancia"]

    F --> TEST["13. Testes e gate"]
    RESULT --> TEST
    TEST --> REVIEW["14. Revisao da Crew A na issue 29"]

    classDef validated fill:#dff3df,stroke:#2f7d32,color:#172417
    classDef review fill:#fff3cd,stroke:#b58105,color:#332701
    class S,CG,PG,JOB,SYN,RUN,REAL,LIB,W,F,O,RESULT,TEST validated
    class REVIEW review
```

### Sequencia detalhada do modo de confirmacao

```mermaid
sequenceDiagram
    autonumber
    actor Captain as Captain Augusto
    participant Scenario as scenario.yaml
    participant CodeGen as code_generator.py
    participant PlanGen as plan_generator.py
    participant Spark as Spark real
    participant Synthetic as apex-synthetic.ndjson
    participant Real as real_log.ndjson
    participant Parser as apexlib
    participant Watcher as skew_watcher.py
    participant Oracle as oracle/compare.py
    participant Tests as Testes e scenario gate
    actor Crew as Crew A

    Captain->>Scenario: Define rows, hot_share, partitions e acceptance
    Scenario->>CodeGen: Carrega o contrato
    CodeGen->>CodeGen: Calcula scenario_hash
    CodeGen-->>Captain: Gera job.py e job.meta.json

    Scenario->>PlanGen: Carrega o mesmo contrato
    PlanGen->>PlanGen: Calcula hot_records e cold_each
    PlanGen->>Synthetic: Escreve eventos Spark e provenance

    Captain->>Spark: Executa o job PySpark
    Spark->>Real: Grava o event log nativo

    Captain->>Watcher: Informa scenario e log sintetico
    Watcher->>Parser: Solicita eventos, plano e metricas
    Parser->>Synthetic: Materializa eventos via read_events
    Synthetic-->>Parser: SQLExecution, stages e TaskEnd
    Parser-->>Watcher: Join, stage, tasks e provenance
    Watcher->>Watcher: Calcula ratio 27.9x
    Watcher->>Watcher: Valida acceptance
    Watcher-->>Captain: Finding esperado e GATE VERDE

    Captain->>Oracle: Informa scenario, sintetico e real
    Oracle->>Parser: Solicita metricas comparaveis
    Parser->>Synthetic: Le operador, hot records e ratio
    Parser->>Real: Le operador, hot records e ratio
    Parser-->>Oracle: Sintetico 27.9x e real 29.5x
    Oracle->>Oracle: Aplica tolerancia do scenario
    Oracle-->>Captain: Sinais agregados calibrados contra o real

    Captain->>Tests: Executa a suite
    Tests->>Parser: Testa formatos e selecao de stage
    Tests->>Watcher: Testa Finding, acceptance e provenance
    Tests->>Oracle: Testa fidelidade e divergencias
    Tests-->>Captain: 40 testes aprovados

    Captain->>Crew: Publica branch e solicita revisao
    Crew-->>Captain: Reproduz, questiona e decide o proximo slice
```

Esta sequencia confirma que o scenario gerou e detectou o comportamento
esperado. Ela nao representa descoberta cega, porque o Watcher atual ainda le
chave e valor quente do scenario.

Ela tambem nao prova processamento streaming ponta a ponta: `iter_events`
existe, mas Watcher e Oraculo chamam `read_events` e materializam o log.
Os CLIs agora usam status ASCII e possuem teste explicito com output `cp1252`.

## Nivel 4 - Arquitetura alvo com persistencia e Tier 2

Este nivel descreve a direcao em discussao. O slice atual nao executa esta
sequencia de ponta a ponta.

```mermaid
sequenceDiagram
    autonumber
    actor Engineer as Engenheiro de dados
    participant Spark as Spark e Databricks
    participant Raw as Event log ou Query Profile
    participant Loader as Loader e Collector
    participant CH as ClickHouse
    participant Parser as Evidence Parser
    participant Watcher as Watcher deterministico
    participant Oracle as Oracle e baseline
    participant Tier2 as Classifier Tier 2
    participant AST as AST e CodeGrounder
    participant Finding as Finding Store
    participant CI as GitHub e CI

    Engineer->>Spark: Executa workload
    Spark->>Raw: Produz telemetria nativa
    Raw->>Loader: Disponibiliza novos eventos
    Loader->>CH: Persiste raw events e metadados
    Loader->>Parser: Solicita normalizacao
    Parser->>CH: Grava SQL, stages, tasks e metricas

    Watcher->>CH: Consulta sinais do job
    CH-->>Watcher: Plano e metricas normalizadas
    Watcher->>Watcher: Aplica regra deterministica
    Watcher->>Oracle: Compara com baseline confiavel
    Oracle->>CH: Consulta execucoes de referencia
    CH-->>Oracle: Corpus e metricas historicas
    Oracle-->>Watcher: Similaridade, tolerancia e divergencias

    alt Evidencia suficiente
        Watcher->>Finding: Emite causa, evidencia e recomendacao
    else Evidencia ambigua ou regra ausente
        Watcher->>Tier2: Envia evidencias e limites
        Tier2->>AST: Solicita contexto do codigo
        AST-->>Tier2: Operadores, arquivo e linha candidatos
        Tier2->>Finding: Emite hipotese com confidence limitada
    end

    Finding->>CH: Persiste resultado e audit trail
    Finding->>CI: Publica resumo no PR ou alerta runtime
    CI-->>Engineer: Mostra evidencia, recomendacao e nivel de confianca
```

### Papel de ClickHouse, Oracle e RAG

```mermaid
flowchart LR
    RAW["Logs brutos confiaveis"] --> CH["ClickHouse"]
    CH --> SQL["Comparacao numerica<br/>SQL deterministico"]
    CH --> SEARCH["Busca de casos semelhantes"]
    SQL --> ORACLE["Oraculo"]
    SEARCH --> RAG["RAG opcional"]
    ORACLE --> DECISION["Gate de fidelidade"]
    RAG --> CONTEXT["Contexto e explicacao"]
    DECISION --> FINDING["Finding"]
    CONTEXT -.-> FINDING
```

O Oraculo deve usar comparacoes deterministicas para ratio, operador, volume e
tolerancia. Uma RAG pode recuperar execucoes parecidas, documentos e
recomendacoes anteriores. Ela nao deve decidir sozinha se o sintetico e fiel ao
real.

## Nivel 5 - Drill-down da evidencia

```mermaid
flowchart TD
    APP["Application"] --> SQL["SQL Execution"]
    SQL --> PLAN["Catalyst e plano fisico"]
    SQL --> JOB["Job"]
    JOB --> STAGE["Stage"]
    STAGE --> TASK["Task"]
    TASK --> METRICS["TaskMetrics"]
    METRICS --> SHUFFLE["Shuffle records e bytes"]
    METRICS --> CPU["CPU time e run time"]
    METRICS --> MEMORY["GC, spill e peak memory"]
    TASK --> REASON["TaskEndReason"]

    PLAN --> DIRECT["Evidencia direta"]
    SHUFFLE --> DIRECT
    CPU --> INFERRED["Evidencia inferida"]
    MEMORY --> INFERRED
    REASON --> PARTIAL["Causa parcial"]

    CODE["Corpo de UDF ou closure RDD"] --> OUTSIDE["Fora do event log"]
    HOTKEY["Valor da hot key<br/>normalmente ausente"] --> OUTSIDE
    HOST["CPU, disco e rede do host"] --> OUTSIDE
```

No slice validado, o Watcher usa:

```text
physicalPlanDescription
Stage ID e Stage Name
Shuffle Read Total Records Read por task
sparkPlanInfo.accumulatorId e TaskInfo.Accumulables
partition index, attempt efetivo e task type
scenario_hash e provenance
```

No log real versionado, os nomes de stage sao genericos. O stage 2 agora e
correlacionado pelo acumulador `45` do `SortMergeJoin`, presente nas
`TaskInfo.Accumulables`. Quando esses dados nao existem, o fallback de maior
volume permanece explicito e o Watcher retorna evidencia indeterminada. O
caminho alvo ainda deve completar `executionId`, DAG, escopo por aplicacao e
processamento incremental, conforme o
[fluxo de validacao e cadeia de evidencia](validation-evidence-flow.md).

No mesmo corpus, o acumulador `45` do `SortMergeJoin` aparece nas tasks do stage
2, mostrando que a correlacao estruturada e executavel. O log real concentra a
hot key na particao 3 com `ResultTask`; o sintetico fixa a particao 0 e usa
`ShuffleMapTask`. O Oraculo agora compara essas dimensoes e emite warnings; o
gerador ainda nao reproduz essa estrutura.

O inventario observou outros campos, como CPU, GC, spill, input e shuffle
write. Esses campos ainda nao sustentam novos Findings testados.

## Skills e ferramentas de apoio

Skills ajudam a construir, revisar ou apresentar o projeto. Elas nao fazem parte
do runtime do Apex enquanto o time nao criar e validar uma integracao explicita.

| Recurso | Uso neste trabalho | Estado |
|---|---|---|
| WarpGrep | Busca assistida em repositorios | Instalado; nao validado como componente Apex |
| stop-slop | Revisao da escrita dos documentos | Usado na documentacao; sem relacao com diagnostico Spark |
| imagegen | Criacao do PNG de arquitetura | Usado e revisado visualmente |
| Mermaid | Diagramas versionados em Markdown | Usado na documentacao |
| AST Classifier | Cobrir UDF, RDD e `collect()` | Proposta arquitetural; nao implementada |
| CodeGrounder | Relacionar runtime a arquivo e linha | Proposta arquitetural; nao implementada |

O time deve avaliar skills como ferramenta de produtividade separadamente dos
componentes do Apex. O resultado validado continua sendo o slice de skew.

## Matriz final de comprovacao

| Capacidade | Evidencia atual | Estado |
|---|---|---|
| Gerar scenario de skew | YAML, geradores e testes | Validado |
| Detectar skew em scenario controlado | Finding e GATE VERDE | Validado |
| Descobrir chave e causa sem scenario | Nao implementado | Proposto |
| Comparar sinais agregados com real | operador, hot records e ratio | Validado |
| Detectar divergencia estrutural | particao, task type e stage correlation | Validado como warning |
| Processar logs grandes incrementalmente | Watcher e Oraculo materializam eventos | Nao validado |
| Validar attempts, zeros e colapso | testes adversariais e `evidence_status` | Validado |
| Evidence Validator dirigido por YAML | Spec e issue #32 | Proposto |
| Inventariar event log | 57 eventos e 18 tipos | Validado em um corpus |
| Detectar spill | Campos existem, valores zero | Observado |
| Classificar CPU-bound | CPU e run time existem | Observado; sem regra validada |
| Detectar UDF no plano | Nao exercitado no corpus | Proposto para novo scenario |
| Entender corpo de UDF | Ausente do event log | Exige AST ou profiler |
| Persistir no ClickHouse | ADR e comentario da issue | Proposto |
| Usar RAG de execucoes | Comentario da issue 29 | Proposto |
| Executar Tier 2 | ADR bloqueada | Proposto |
| Comentar em PR | Feature e gate inicial | Parcial |

## Fluxo de versionamento e validacao coletiva

```mermaid
flowchart LR
    EDIT["Editar documentos e codigo"] --> TEST["Executar testes e revisar diff"]
    TEST --> COMMIT["Commit com versao identificavel"]
    COMMIT --> PUSH["Push na branch"]
    PUSH --> ISSUE["Atualizar issue 29 com links"]
    ISSUE --> CREW["Crew A revisa e reproduz"]
    CREW --> DECISION{"Aprovado?"}
    DECISION -->|"ajustes"| EDIT
    DECISION -->|"sim"| PR["Abrir PR ou definir proximo slice"]
```

Salvar um arquivo cria uma alteracao local. O commit cria a versao. O push
publica essa versao. A issue deve apontar para um commit ou para arquivos ja
publicados, evitando links para material que existe apenas na maquina do autor.

Toda mudanca no contrato de validacao deve revisar tambem o
[fluxo de validacao e cadeia de evidencia](validation-evidence-flow.md), que
mantem fluxo, arquitetura, sequencia, valor, gargalos e rupturas na mesma versao.
