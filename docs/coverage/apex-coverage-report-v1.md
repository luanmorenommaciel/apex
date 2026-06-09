# Cobertura do event log - Spark emite x Apex consome x falta

Fontes analisadas: **1** | aplicacoes: **1** | eventos: **57** | tipos de evento: **18**

> Corpus parcial: 1 aplicacao e 18 tipos de evento. A ausencia de um sinal neste relatorio nao prova que o Spark nao o emite.

## Tipos de evento observados

| evento | ocorrencias |
|---|---|
| `SparkListenerTaskEnd` | 12 |
| `SparkListenerTaskStart` | 12 |
| `SparkListenerExecutorMetricsUpdate` | 6 |
| `SparkListenerStageExecutorMetrics` | 6 |
| `SparkListenerStageCompleted` | 3 |
| `SparkListenerStageSubmitted` | 3 |
| `SparkListenerDriverAccumUpdates` | 3 |
| `SparkListenerBlockManagerAdded` | 2 |
| `SparkListenerApplicationEnd` | 1 |
| `SparkListenerApplicationStart` | 1 |
| `SparkListenerEnvironmentUpdate` | 1 |
| `SparkListenerExecutorAdded` | 1 |
| `SparkListenerJobEnd` | 1 |
| `SparkListenerJobStart` | 1 |
| `SparkListenerLogStart` | 1 |
| `SparkListenerResourceProfileAdded` | 1 |
| `SparkListenerSQLExecutionEnd` | 1 |
| `SparkListenerSQLExecutionStart` | 1 |

## [A] Consumido pelo Apex atual - 7 campos

- `Event`
- `Stage ID`
- `Stage Info.Stage ID`
- `Stage Info.Stage Name`
- `Task Metrics.Shuffle Read Metrics.Total Records Read`
- `executionId`
- `physicalPlanDescription`

## [B*] Observado e valioso, ainda nao consumido - 32 campos

| campo observado | uso potencial |
|---|---|
| `Stage Info.Number of Tasks` | paralelismo do stage |
| `Stage Info.RDD Info.Callsite` | local de criacao do RDD |
| `Stage Info.RDD Info.Scope` | escopo e operacao do RDD |
| `Stage Info.Stage Attempt ID` | retries do stage |
| `Task End Reason.Reason` | motivo registrado para termino ou falha |
| `Task Info.Getting Result Time` | inicio do fetch de resultado pelo driver |
| `Task Metrics.Disk Bytes Spilled` | spill em disco |
| `Task Metrics.Executor CPU Time` | comparar CPU time com run time |
| `Task Metrics.Executor Run Time` | tempo de execucao por task |
| `Task Metrics.Input Metrics.Bytes Read` | volume de scan |
| `Task Metrics.Input Metrics.Records Read` | volume de registros por task |
| `Task Metrics.JVM GC Time` | pressao de GC |
| `Task Metrics.Memory Bytes Spilled` | spill em memoria |
| `Task Metrics.Output Metrics.Bytes Written` | volume de escrita |
| `Task Metrics.Output Metrics.Records Written` | registros escritos |
| `Task Metrics.Peak Execution Memory` | indicador parcial de pressao de memoria |
| `Task Metrics.Result Serialization Time` | custo de serializacao do resultado |
| `Task Metrics.Result Size` | volume devolvido ao driver |
| `Task Metrics.Shuffle Read Metrics.Fetch Wait Time` | espera por fetch de shuffle |
| `Task Metrics.Shuffle Read Metrics.Remote Bytes Read` | shuffle remoto |
| `Task Metrics.Shuffle Write Metrics.Shuffle Bytes Written` | distribuicao do shuffle write |
| `Task Metrics.Shuffle Write Metrics.Shuffle Records Written` | registros no shuffle write |
| `sparkPlanInfo.children.metrics.accumulatorId` | arvore estruturada do plano e metricas SQL por no |
| `sparkPlanInfo.children.metrics.metricType` | arvore estruturada do plano e metricas SQL por no |
| `sparkPlanInfo.children.metrics.name` | arvore estruturada do plano e metricas SQL por no |
| `sparkPlanInfo.children.nodeName` | arvore estruturada do plano e metricas SQL por no |
| `sparkPlanInfo.children.simpleString` | arvore estruturada do plano e metricas SQL por no |
| `sparkPlanInfo.metrics.accumulatorId` | arvore estruturada do plano e metricas SQL por no |
| `sparkPlanInfo.metrics.metricType` | arvore estruturada do plano e metricas SQL por no |
| `sparkPlanInfo.metrics.name` | arvore estruturada do plano e metricas SQL por no |
| `sparkPlanInfo.nodeName` | arvore estruturada do plano e metricas SQL por no |
| `sparkPlanInfo.simpleString` | arvore estruturada do plano e metricas SQL por no |

## [B] Demais campos observados, ainda nao consumidos - 254 campos

`App ID`, `App Name`, `Block Manager ID.Executor ID`, `Block Manager ID.Host`, `Block Manager ID.Port`, `Classpath Entries.<entry>`, `Completion Time`, `Executor ID`, `Executor Info.Host`, `Executor Info.Log Urls.stderr`, `Executor Info.Log Urls.stdout`, `Executor Info.Registration Time`, `Executor Info.Resource Profile Id`, `Executor Info.Total Cores`, `Executor Metrics Updated.Executor Metrics.ConcurrentGCCount`, `Executor Metrics Updated.Executor Metrics.ConcurrentGCTime`, `Executor Metrics Updated.Executor Metrics.DirectPoolMemory`, `Executor Metrics Updated.Executor Metrics.JVMHeapMemory`, `Executor Metrics Updated.Executor Metrics.JVMOffHeapMemory`, `Executor Metrics Updated.Executor Metrics.MajorGCCount`, `Executor Metrics Updated.Executor Metrics.MajorGCTime`, `Executor Metrics Updated.Executor Metrics.MappedPoolMemory`, `Executor Metrics Updated.Executor Metrics.MinorGCCount`, `Executor Metrics Updated.Executor Metrics.MinorGCTime`, `Executor Metrics Updated.Executor Metrics.OffHeapExecutionMemory`, `Executor Metrics Updated.Executor Metrics.OffHeapStorageMemory`, `Executor Metrics Updated.Executor Metrics.OffHeapUnifiedMemory`, `Executor Metrics Updated.Executor Metrics.OnHeapExecutionMemory`, `Executor Metrics Updated.Executor Metrics.OnHeapStorageMemory`, `Executor Metrics Updated.Executor Metrics.OnHeapUnifiedMemory`, `Executor Metrics Updated.Executor Metrics.ProcessTreeJVMRSSMemory`, `Executor Metrics Updated.Executor Metrics.ProcessTreeJVMVMemory`, `Executor Metrics Updated.Executor Metrics.ProcessTreeOtherRSSMemory`, `Executor Metrics Updated.Executor Metrics.ProcessTreeOtherVMemory`, `Executor Metrics Updated.Executor Metrics.ProcessTreePythonRSSMemory`, `Executor Metrics Updated.Executor Metrics.ProcessTreePythonVMemory`, `Executor Metrics Updated.Executor Metrics.TotalGCTime`, `Executor Metrics Updated.Stage Attempt ID`, `Executor Metrics Updated.Stage ID`, `Executor Metrics.ConcurrentGCCount`, `Executor Metrics.ConcurrentGCTime`, `Executor Metrics.DirectPoolMemory`, `Executor Metrics.JVMHeapMemory`, `Executor Metrics.JVMOffHeapMemory`, `Executor Metrics.MajorGCCount`, `Executor Metrics.MajorGCTime`, `Executor Metrics.MappedPoolMemory`, `Executor Metrics.MinorGCCount`, `Executor Metrics.MinorGCTime`, `Executor Metrics.OffHeapExecutionMemory`, `Executor Metrics.OffHeapStorageMemory`, `Executor Metrics.OffHeapUnifiedMemory`, `Executor Metrics.OnHeapExecutionMemory`, `Executor Metrics.OnHeapStorageMemory`, `Executor Metrics.OnHeapUnifiedMemory`, `Executor Metrics.ProcessTreeJVMRSSMemory`, `Executor Metrics.ProcessTreeJVMVMemory`, `Executor Metrics.ProcessTreeOtherRSSMemory`, `Executor Metrics.ProcessTreeOtherVMemory`, `Executor Metrics.ProcessTreePythonRSSMemory`

_Lista resumida: 194 campos omitidos._

## [C] Depende de configuracao ou runtime

| caso | interpretacao |
|---|---|
| metricas de processo e host | dependem das configuracoes de executor metrics e process tree metrics |
| perfil detalhado de Python UDF | depende do profiler e das opcoes disponiveis na versao do Spark |
| campos especificos de Databricks Runtime e Photon | o schema e a disponibilidade variam por runtime |
| telemetria de Databricks Serverless | compute event logs nao sao a fonte padrao; exige Query Profile ou system tables |
| detalhes longos de callsite | dependem de spark.eventLog.longForm.enabled |

## [D] Nao observado neste corpus

Estes sinais precisam de outros cenarios antes de qualquer conclusao sobre cobertura:
- AQE com atualizacao de plano final
- Structured Streaming QueryProgressEvent
- perda ou remocao de executor
- Python UDF ou Pandas UDF no plano
- mais de uma execucao SQL na mesma amostra
- spill efetivo (> 0)
- falha, retry ou tentativa especulativa real

## [E] Ausente do event log padrao

| caso | interpretacao |
|---|---|
| implementacao interna de UDF Python, Scala ou Java | o plano registra o operador, nao o corpo executado |
| corpo das closures de RDD | RDD Info registra lineage, scope e callsite, nao a funcao serializada |
| valores das linhas e da chave quente | as metricas registram volumes e tempos, nao os dados do cliente |
| codigo do driver entre actions Spark | nao existe evento de task para codigo local comum |
| alternativas descartadas e trilha completa de regras do Catalyst | o log padrao registra planos, nao todo o processo de busca |
| codigo Java gerado pelo whole-stage codegen | o plano indica codegen, mas nao inclui o codigo gerado completo |
| contencao de threads e lock waits detalhados da JVM | exige profiler ou telemetria complementar |

## [F] Inferivel, sem causalidade comprovada

| caso | interpretacao |
|---|---|
| CPU-bound versus espera | CPU time dividido por run time e um indicador, nao prova saturacao do host |
| small files | muitas tasks com poucos bytes ou registros sugerem o problema |
| pressao de memoria ou risco de OOM | GC, spill e peak memory sao sinais parciais |
| espera em JDBC, S3 ou API | task lenta pode indicar espera externa, mas o event log nao prova a origem |
| causa externa da perda de executor | reason e stack trace podem existir, mas spot, OOM killer ou falha do no podem ficar ambiguos |
| valor da hot key | a distribuicao aponta a particao quente, nao identifica o valor sem outra fonte |
| motivo exato da decisao do AQE | o update mostra o novo plano, nao toda a conta que levou a decisao |

## Leitura correta deste resultado

- O corpus comprova que o Apex consumiu **7** campos observados.
- O corpus revelou **32** campos valiosos ainda nao consumidos.
- O corpus revelou **254** outros caminhos de campo apos agrupar mapas dinamicos.
- A secao [D] registra lacunas do corpus, nao limites do Spark.
- As secoes [C], [E] e [F] sao conhecimento arquitetural versionado no script.
