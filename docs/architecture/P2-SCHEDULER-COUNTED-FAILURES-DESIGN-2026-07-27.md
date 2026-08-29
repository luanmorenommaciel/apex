# P2 - Semantica de falha contabilizada pelo scheduler

Data: 2026-07-27
Status: aprovado e implementado

## Problema

`task_failed_attempt_count` registra tentativas em que `TaskInfo.failed=true`.
Esse sinal e util, mas nao representa exatamente a decisao do scheduler sobre
consumir o limite de falhas da task. No Spark 4.1.2, essa decisao pertence a
`TaskFailedReason.countTowardsTaskFailures`.

Exemplos oficiais:

- `FetchFailed`, `TaskKilled` e `TaskCommitDenied` nao contam;
- `ExecutorLostFailure` depende de `exitCausedByApp`;
- outras subclasses de `TaskFailedReason` contam por padrao.

## Decisao

Adicionar, sem renomear ou reinterpretar campos existentes:

`task_counted_failure_attempt_count`

O JAR calcula o campo por pattern matching sobre `SparkListenerTaskEnd.reason`.
Somente uma instancia de `TaskFailedReason` pode incrementar o contador, e o
valor usado e o proprio `countTowardsTaskFailures` fornecido pelo Spark.

O campo atravessa as seis raias:

1. JAR: classificacao e agregacao por stage;
2. contrato OTLP: atributo aditivo;
3. Collector: coluna e materialized view;
4. Infra: migration aditiva, sem `DROP VIEW`;
5. Engine: schema, leitura e agregacao;
6. DEV/E2E: matriz JVM e experimento real de falha.

## Compatibilidade

- `task_failed_attempt_count` continua significando `TaskInfo.failed=true`;
- `task_killed_attempt_count` continua separado;
- dados historicos recebem zero por default;
- consumidores que desconhecem o campo novo continuam validos;
- a migration usa `ADD COLUMN IF NOT EXISTS` e `MODIFY QUERY`.

## Criterios de aceite

1. Matriz JVM prova:
   - sucesso, `FetchFailed`, `TaskKilled` e `TaskCommitDenied`: nao contam;
   - `ExecutorLostFailure(false)`: nao conta;
   - `ExecutorLostFailure(true)` e uma falha padrao: contam.
2. O resumo de stage mantem os contadores legado e oficial independentes.
3. Fixture, DDL, OTLP, ClickHouse e Engine propagam o novo campo.
4. Testes impedem regressao para `DROP VIEW`.
5. Um experimento real tenta produzir `FetchFailed`; se o ambiente nao o
   produzir, o resultado fica explicitamente inconclusivo, nunca simulado.

## Fonte oficial

Spark 4.1.2:
`core/src/main/scala/org/apache/spark/TaskEndReason.scala`.
