# ADR-001: sinal de cauda extrema para skew com alta paralelizacao

**Status:** implementado e validado localmente
**Data:** 2026-07-26

## Contexto

O listener calcula `task_duration_p99_ms` por nearest-rank. Com menos de 100
tasks, p99 coincide com a maior duracao; com 100 ou mais, um ou dois outliers
podem ficar fora do p99. O watcher heuristico atual usa somente `p99/p50`.

O sinal AQE `skew_split` continua sendo evidencia independente e forte quando
Spark executa a divisao. A lacuna afeta o caminho heuristico quando AQE esta
desligado, mal configurado ou nao produz uma transicao.

## Decisao

Adicionar `task_duration_max_ms` como campo aditivo de telemetria e preservar
`task_duration_p99_ms` sem reinterpretacao.

O ENGINE tratara os sinais assim:

| Sinal | Decisao |
|---|---|
| `p99/p50 > 10` | mantem finding critico atual |
| AQE `skew_split` | mantem evidencia forte/critica atual |
| `max/p50` elevado com `task_count >= 100` | candidato de cauda extrema; nao sobe sozinho para critico |

`max/p50` nao e chamado de p99 nem substitui o sinal de distribuicao. A
severidade final exige calibracao contra execucao real e, quando disponivel,
corroboracao por AQE ou outro sinal deterministico.

## Consequencias

- O contrato permanece aditivo; eventos antigos continuam legiveis.
- A migracao precisa preencher o novo campo com zero para telemetria anterior.
- A cobertura passa a incluir 100, 200 e 400 tasks, com um e dois outliers.
- O produto ganha visibilidade sobre cauda extrema sem transformar um
  straggler isolado em causa-raiz automaticamente.

## Revisao de raciocinio

A hipotese foi reavaliada com Terra Medio em 2026-07-26. Essa revisao confirma
a aritmetica e o fluxo de dados no codigo, mas nao substitui a prova Spark real
com `spark.sql.shuffle.partitions=200`.

## Validacao

Em 2026-07-26, um probe Spark 4.1.2 com 200 tasks produziu
`p99/p50=3,988x` e `max/p50=31,631x`. O watcher canonico permaneceu silencioso
e `tail_outlier_watcher` emitiu um candidato `warning/MEDIUM`, sem Crew/LLM.
