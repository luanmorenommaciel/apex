# ADR-002 - Amostra de tasks bem-sucedidas sem reinterpretar o contrato

**Status:** aceito e implementado
**Data:** 2026-07-26

## Contexto

Os campos congelados `task_duration_p50_ms`, `task_duration_p99_ms` e
`task_duration_max_ms` representam a distribuicao formada pelos eventos
`onTaskEnd` observados pelo listener. Tentativas falhas, mortas, repetidas ou
especulativas podem alterar essa distribuicao e fazer `task_count` divergir do
tamanho real da amostra.

O contrato permite campos aditivos, mas proibe renomear ou reinterpretar um
campo existente. Portanto, a distribuicao legada deve continuar intacta.

## Decisao

O evento de stage passa a transportar, de forma aditiva:

| Campo | Semantica |
|---|---|
| `task_duration_sample_count` | tentativas finalizadas com duracao disponivel |
| `successful_task_duration_p50_ms` | p50 de uma tentativa bem-sucedida por particao logica |
| `successful_task_duration_p99_ms` | p99 da mesma amostra |
| `successful_task_duration_max_ms` | maximo da mesma amostra |
| `successful_task_sample_count` | quantidade de particoes logicas com sucesso observado |
| `successful_task_shuffle_read_bytes_p50` | mediana do shuffle read da mesma amostra retry-safe |
| `successful_task_shuffle_read_bytes_max` | maior shuffle read da mesma amostra |
| `successful_task_shuffle_read_bytes_sample_count` | particoes com metrica de shuffle observada |
| `task_attempt_count` | total de eventos `onTaskEnd` observados |
| `task_failed_attempt_count` | tentativas com `TaskInfo.failed=true` |
| `task_counted_failure_attempt_count` | tentativas que o scheduler contabiliza via `TaskFailedReason.countTowardsTaskFailures` |
| `task_killed_attempt_count` | tentativas com `TaskInfo.killed=true` |
| `task_speculative_attempt_count` | tentativas marcadas como especulativas |

Para retries e especulacao, o primeiro sucesso observado para cada particao
logica compoe a amostra `successful_*`. O identificador usa
`TaskInfo.partitionId` quando nao negativo e recua para `TaskInfo.index`
somente para dados historicos sem `partitionId`.

Toda tentativa terminada incrementa `task_attempt_count`, mesmo sem duracao.
Somente uma task finalizada cuja duracao esta disponivel alimenta os
percentis legados. Ausencia de duracao nao e representada por zero.

`failed` e `killed` sao estados distintos no Spark. Um perdedor especulativo
morto incrementa `task_killed_attempt_count`, nao
`task_failed_attempt_count`.

O contador aditivo `task_counted_failure_attempt_count` nao substitui o legado.
Ele reproduz a decisao do scheduler: `FetchFailed`, `TaskKilled` e
`TaskCommitDenied` nao consomem o limite; `ExecutorLostFailure` depende de
`exitCausedByApp`; as demais `TaskFailedReason` contam por padrao. Essa
separacao permite investigar retries sem confundir uma falha observada com
uma falha atribuida a task pelo Spark.

O ENGINE prefere `successful_*` quando `successful_task_sample_count > 0` e
usa os campos legados para eventos historicos. Findings devem declarar qual
amostra foi usada. `task_count` permanece sendo o numero de tasks do stage.

ENGINE e gate DEV compartilham a politica de skew em
`apex_engine/skew_policy.py`. Eventos historicos sem volume mantem a politica
anterior. Quando a distribuicao de shuffle read existe, um hidden-tail vira
`critical` somente se `max/p50` de duracao for maior que 10, `max/p50` de
bytes for maior que 5 e o maximo superar o piso local documentado.

Historicamente, a guarda criava uma descontinuidade deliberada em
`n=99 -> 100`: em amostras
com 100 ou mais tasks, uma unica cauda extrema com `p99/p50 <= 5` e
`max/p50 > 10` e emitida pelo `tail_outlier_watcher` como `SKEW_ON_JOIN` de
severidade `warning`, e nao como skew critico. A execucao real canonica
`app-20260727033059-0001` demonstrou esse caso com 200 tasks,
`p99/p50=4.602` e `max/p50=35.566`. O P1 fechou esse gap sem reduzir limiar:
`app-20260727233345-0000` mediu duracao `max/p50=56.43x` e shuffle read
`max/p50=8.427x`, produzindo finding `critical` validado. Para eventos novos,
o `tail_outlier_watcher` nao duplica a decisao baseada em volume.

O sinal implementado separa dados de tempo: a definicao de AQE do Spark usa
bytes da particao contra a mediana, enquanto uma pausa de GC pode alterar a
duracao sem aumentar bytes. `tail_outlier_watcher` preserva cobertura
diagnostica conservadora ate essa extensao existir. O precedente
[SPARK-22902](https://issues.apache.org/jira/browse/SPARK-22902) e o TODO
aberto do projeto sparkMeasure sobre metricas de tasks nao bem-sucedidas
explicam por que o Apex mantem uma camada propria de contadores e amostras.
O piso de `256 KiB` foi calibrado somente para o fixture local; nao substitui
calibracao por perfil de workload em producao.

## Ciclo de vida do listener

- somente stages submetidos e ativos, ou stages concluidos aguardando
  `TaskEnd`, aceitam metricas de task;
- `TaskStart` define quantas tentativas precisam encerrar;
- se `StageCompleted` chegar antes de um `TaskEnd`, o evento fica num mapa
  limitado e e emitido quando `TaskEnd` fecha a contagem;
- na ausencia definitiva do callback, o evento parcial e descarregado no
  limite de memoria ou em `ApplicationEnd`, com aviso;
- mapas stage/job/execution sao limpos na conclusao do stage;
- stages pendentes, fingerprints de execucoes encerradas e marcadores de
  overflow permanecem limitados;
- o encerramento da aplicacao limpa todo estado residual;
- nenhuma excecao do listener pode escapar para o Spark.

## Migracao

As novas colunas usam `DEFAULT 0`. Eventos antigos continuam validos.

A materialized view e atualizada sem uma janela de `DROP VIEW`.
`ALTER TABLE apex.mv_spark_events MODIFY QUERY` foi validado contra ClickHouse
24.8.14.39 e e o caminho implementado. Versoes sem esse suporte devem recusar
ingestao concorrente e exigir uma janela de manutencao explicita.

## Interpretacao da especulacao

Usar o primeiro vencedor por particao funciona como filtro natural de ruido:

- skew de dados continua visivel porque as duas copias processam a mesma
  particao grande;
- straggler de executor pode desaparecer quando a copia especulativa termina
  rapidamente, evitando classificar lentidao de infraestrutura como skew de
  dados.

## Seguranca e governanca

- nenhum payload novo carrega texto livre, chave, segredo ou identificador de
  usuario;
- a extensao e numerica e nao amplia a superficie de PII;
- a branch do Commander nao e alterada;
- publicacao remota depende de autorizacao posterior.

## Validacao

1. testes JVM para sucesso, retry, falha, task morta, especulacao e callback
   atrasado;
2. matriz de percentis e compatibilidade dos campos legados;
3. propagacao OTLP -> Collector -> ClickHouse;
4. fallback do ENGINE para linhas historicas;
5. preferencia do ENGINE pela amostra `successful_*`;
6. migracao idempotente sem ausencia da materialized view;
7. gate real Spark 4.1.2 e regressao das seis raias.
8. gate canonico de quatro patologias com dados Delta reais e credenciais S3A
   fornecidas apenas em runtime.
9. prova de S3A via Docker Secrets, sem valores no SparkConf, argv ou
   event log.
10. matriz com os seis casos acordados de skew, tail e baseline.

Evidencia de execucao real para os itens acima esta documentada no PR que
acompanha este ADR.

## Rollback

Os consumidores podem ignorar os novos campos e continuar usando os campos
legados. As colunas aditivas nao precisam ser removidas. O watcher pode voltar
ao fallback legado sem reescrever dados historicos.
