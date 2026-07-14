# Apex Spark Listener JVM

Modulo JVM minimo para provar a premissa de um `SparkListener` real, carregado
por `spark.extraListeners`, com comportamento fail-safe.

## Classe

```text
apex.commander.spark.ApexSparkListener
```

Callbacks cobertos:

- `onApplicationStart`
- `onStageSubmitted`
- `onTaskEnd`
- `onApplicationEnd`

Cada callback e protegido por `try/catch Throwable`. Erros internos do listener
sao enviados para `System.err` e nao sao relancados para o Spark.

## Configuracao

| Propriedade Spark | Descricao | Default |
|---|---|---|
| `spark.apex.jobId` | Identificador Apex do job. | vazio |
| `spark.apex.listener.output` | Caminho do arquivo NDJSON append-only. | vazio, desabilita escrita |
| `spark.apex.listener.failMode` | Forca falha interna para validar fail-safe. | `false` |

## Build

```powershell
gradle -p listener-jvm clean jar
gradle -p listener-jvm check
```

Por default o build usa:

```text
spark-core_2.13:4.1.2
```

Para trocar a versao:

```powershell
gradle -p listener-jvm check -PsparkVersion=4.1.2 -PscalaBinaryVersion=2.13
```

## Uso com Spark

```powershell
spark-submit `
  --jars listener-jvm/build/libs/apex-spark-listener-0.1.0.jar `
  --conf spark.extraListeners=apex.commander.spark.ApexSparkListener `
  --conf spark.apex.jobId=<job_id> `
  --conf spark.apex.listener.output=/tmp/apex-listener-events.ndjson `
  job.py
```

## Fail-safe smoke

Para validar que erro interno do listener nao derruba o processo:

```powershell
spark-submit `
  --jars listener-jvm/build/libs/apex-spark-listener-0.1.0.jar `
  --conf spark.extraListeners=apex.commander.spark.ApexSparkListener `
  --conf spark.apex.listener.failMode=true `
  job.py
```

O job Spark deve terminar de acordo com o proprio codigo do job. O listener deve
registrar o erro em stderr e nao relancar a excecao.
