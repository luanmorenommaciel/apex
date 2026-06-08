# Rascunho de Revisao das ADRs

Este documento organiza a leitura das ADRs relacionadas ao slice `skew_on_join_30x` v4 corrigido.

Nada aqui decide a arquitetura final. O objetivo e dar ao time um material de revisao antes de comentar nas ADRs oficiais do GitHub.

Contexto correto:

- o estudo foi validado localmente pelo Augusto;
- a Crew A ainda precisa revisar e validar o entendimento;
- a branch usa o GitHub para dar visibilidade, autonomia, rastreabilidade e validacao coletiva;
- as ADRs devem receber comentarios apenas depois da revisao do time.

Branch de referencia:

```text
gustocezar/feature/desacoplamento-geradores
```

## Leitura geral

O slice reforca uma direcao importante para o Apex:

```text
Spark executa job -> Spark gera event log nativo -> Apex analisa fora do cluster -> Watcher emite Finding
```

Essa direcao combina com a ideia de componentes pequenos, desacoplados e testaveis por contrato.

O slice ainda nao implementa ClickHouse, Collector, estado historico ou core em Go. Ele funciona como laboratorio validado localmente para aprender, medir e preparar decisoes.

## ADR-001 - Onde o Apex roda?

Issue:

```text
https://github.com/luanmorenommaciel/apex/issues/5
```

### Entendimento atual

A ADR aponta Apex como componente externo, lendo dados persistidos no ClickHouse.

O slice atual nao usa ClickHouse ainda. Ele le event logs versionados diretamente. Mesmo assim, o desenho respeita a parte mais importante da ADR: Apex fica fora do ciclo de vida do job Spark.

### O que o slice reforca

- Apex pode analisar Spark sem alterar o job do cliente.
- Event log nativo do Spark e uma fonte boa para o primeiro diagnostico.
- O Watcher pode operar sobre evidencias ja materializadas.
- O modelo evita acoplamento com SparkListener injetado.

### Limite atual

O slice ainda nao prova:

- ingestao em ClickHouse;
- leitura do Watcher a partir de ClickHouse;
- latencia real entre execucao Spark e analise Apex;
- schema final para event logs e Findings.

### Comentario sugerido

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

## ADR-002 - Quando o classificador Tier 2 dispara?

Issue:

```text
https://github.com/luanmorenommaciel/apex/issues/6
```

### Entendimento atual

A ADR esta bloqueada porque o time precisa de evidencia empirica antes de decidir thresholds de escalonamento.

O slice reduz parte do bloqueio, porque entrega uma primeira amostra controlada:

- scenario declarativo;
- Watcher deterministico;
- log real;
- oraculo de comparacao;
- evidencia local reproduzivel.

### O que o slice reforca

O time pode separar dois tipos de decisao:

1. O que a regra deterministica ja resolve.
2. O que deve escalar para classificador pesado.

No caso atual, skew em join e detectavel por regra deterministica. Isso sugere que o Tier 2 nao deve ser acionado apenas porque existe skew. Ele deve entrar quando houver ambiguidade, evidencia incompleta, multiplos sinais conflitantes ou baixa confianca.

### Limite atual

O slice ainda nao define threshold de Tier 2. Falta:

- baseline sem skew;
- casos com sinais incompletos;
- multiplos anti-patterns;
- confidence baseada em evidencia;
- historico de falsos positivos e falsos negativos.

### Comentario sugerido

```md
Nota de estudo local:

Esta ADR estava bloqueada por falta de evidencia empirica. O slice `skew_on_join_30x` comeca a reduzir esse bloqueio, porque entrega:

- um scenario controlado;
- um Watcher deterministico;
- comparacao com log real;
- evidencia reproduzivel.

Ainda nao e suficiente para definir threshold de Tier 2. Minha sugestao e usar este slice como primeira amostra e seguir com mais scenarios antes de decidir escalonamento para classificador pesado.
```

## ADR-003 - Onde mora o estado historico do Apex?

Issue:

```text
https://github.com/luanmorenommaciel/apex/issues/7
```

### Entendimento atual

A ADR aponta ClickHouse como store historico do Apex.

O slice ainda nao grava em ClickHouse, mas torna mais concreto o que um registro historico precisa guardar.

### Campos que aparecem no slice

O Finding do Watcher sugere estes campos:

| Campo | Papel |
|---|---|
| `watcher` | Identifica o componente que emitiu o Finding. |
| `stage` | Stage Spark onde o sinal apareceu. |
| `severity` | Gravidade inicial do problema. |
| `confidence` | Confianca do Watcher. |
| `evidence` | Evidencias legiveis usadas na decisao. |
| `root_cause` | Explicacao da causa raiz. |
| `recommendations` | Acoes sugeridas. |
| `scenario_hash` | Hash do contrato usado na geracao. |
| `provenance` | Validacao da origem do log sintetico. |

### Limite atual

O slice ainda nao define:

- schema ClickHouse final;
- chaves de particionamento;
- retencao;
- formato para guardar `evidence`;
- relacao entre job, execution, stage, task e Finding.

### Comentario sugerido

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

## ADR-004 - Linguagem dos componentes

Issue:

```text
https://github.com/luanmorenommaciel/apex/issues/8
```

### Entendimento atual

A ADR aponta Go para componentes core do Apex.

O slice atual usa Python porque ele esta servindo como laboratorio, spec executavel e material de aprendizado. Isso nao precisa contradizer a ADR, desde que o time deixe claro o papel de cada linguagem.

### Separacao recomendada

| Uso | Linguagem sugerida |
|---|---|
| Prototipacao, fixtures, validacao local, docs executaveis | Python |
| Collector, servicos de infra, pipeline de producao | Go |
| Contratos e cenarios | YAML / Markdown |

### Risco se nao separar

Sem essa separacao, o time pode discutir linguagem antes de validar comportamento. A recomendacao e usar Python para aprender rapido e portar para Go apenas quando o contrato estiver estavel.

### Comentario sugerido

```md
Nota de estudo local:

O slice atual usa Python como laboratorio e spec executavel, nao como decisao final de core.

Isso nao precisa conflitar com a decisao de Go para componentes de infraestrutura. Minha leitura:

- Python: estudo, validacao, fixtures, prototipacao e documentacao executavel;
- Go: possivel caminho para core, Collector e componentes de producao apos validacao.

A Crew A pode usar o slice para aprender e validar contrato antes de portar partes maduras para Go.
```

## ADR-001 Go as language for OTel Collector

Issue:

```text
https://github.com/luanmorenommaciel/apex/issues/22
```

### Entendimento atual

Esta ADR fala especificamente do Collector. O slice `skew_on_join_30x` nao mexe no Collector.

O ponto de conexao futuro e garantir que o Collector preserve dados suficientes para Watchers operarem depois.

### O que o slice reforca

Watchers precisam de:

- operador de join;
- stage correto;
- metricas por task;
- volumes de shuffle;
- origem/provenance;
- dados comparaveis entre sintetico e real.

Se o Collector ou ClickHouse perderem esses campos, o Watcher perde qualidade.

### Comentario sugerido

```md
Nota de estudo local:

O slice `skew_on_join_30x` nao altera a decisao sobre Go no OTel Collector.

Ele atua antes, como evidencia de diagnostico sobre event logs Spark. A parte de Collector continua podendo seguir em Go conforme a ADR.

Ponto de integracao futuro: garantir que o Collector e o pipeline de storage preservem os dados necessarios para Watchers como este operarem sobre ClickHouse.
```

## ADR-003 Intentional deprioritization strategy

Issue:

```text
https://github.com/luanmorenommaciel/apex/issues/24
```

### Entendimento atual

A estrategia de baseline antes de divergencia faz sentido quando produz artefato revisavel.

O slice atual e uma evidencia concreta: o tempo investido em baseline gerou um fluxo que pode ser visto, testado, discutido e melhorado pelo time.

### O que o slice reforca

- O time ganha uma referencia comum.
- A discussao sai do abstrato e vai para evidencia.
- A branch registra caminho, decisao e limites.
- O capitao consegue conduzir validacao sem impor conclusao.

### Limite atual

Isso nao encerra a discussao de governanca. O time ainda precisa decidir:

- como o fork deve continuar;
- o que entra no Apex;
- quem valida cada proximo slice;
- quando um estudo vira entrega oficial.

### Comentario sugerido

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

## Recomendacao para revisao com a Crew A

Antes de publicar qualquer comentario nas ADRs:

1. Revisar este documento com o time.
2. Confirmar se a leitura das ADRs esta correta.
3. Ajustar termos que possam parecer decisao final.
4. Publicar comentarios apenas como "nota de estudo local" ou "evidencia para revisao".
5. Evitar fechar ADRs ate haver decisao explicita da Crew A ou do Commander.

