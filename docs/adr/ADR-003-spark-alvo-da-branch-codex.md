# ADR-003 - Spark Alvo Da Branch Codex

Status: aceita

Data: 2026-07-18

## Contexto

A branch Codex validou historicamente G3/G5 autonomos em Spark 4.0.0. A branch
Agmar/Spike e o contrato de plataforma compartilhado apontam para Spark 4.1.2.
Para reduzir divergencia entre engines antes da escolha da branch final, o
Commander definiu Spark 4.1.2 como alvo da V1.

## Decisao

Spark 4.1.2 passa a ser o alvo oficial desta branch.

O `docker-compose.yml` raiz ja usa `spark-plat-v0-spark:4.1.2`. A stack
autonoma foi alinhada para `apex-autonomous-spark:4.1.2-s3a`, e o
`SparkListener` JVM foi promovido para caminho oficial dos jobs:

- JAR montado em `/opt/apex/listener/apex-spark-listener-0.1.0.jar`;
- `spark.jars` aponta para esse JAR;
- `spark.extraListeners` carrega `apex.commander.spark.ApexSparkListener`;
- `spark.apex.listener.output` usa `/tmp/apex-listener-events.ndjson`;
- `spark.apex.listener.failMode=false` e o default operacional.

## Consequencias

- As evidencias G3/G5 antigas em Spark 4.0.0 continuam historicas.
- Em 18/07, G3/G5 foram reexecutados em Spark 4.1.2 na stack autonoma:
  before `app-20260718172202-0002` detectou skew high ratio 29.4 e after
  `app-20260718175410-0004` ficou limpo com finding_count 0.
- A imagem autonoma Spark 4.1.2 usa `spark-plat-v0-spark:4.1.2` como base
  local, evitando o download Maven do AWS SDK bundle em tempo de build.
- A primeira reexecucao after sem memoria explicita resolveu skew, mas gerou
  pressao de GC; por isso o caminho oficial passou a definir
  `spark.executor.memory=3g` e `spark.driver.memory=2g`.

## Evidencias

- `docker-compose.yml`
- `docker-compose.autonomous.yml`
- `docker/spark/spark-defaults.conf`
- `docker/autonomous/spark/spark-defaults.conf`
- `apex/commander/spark_rerun_template.py`
- `evidence/f7-spark412-official-listener-tests-2026-07-18.log`
- `evidence/f7-spark412-official-listener-compose-root-2026-07-18.log`
- `evidence/f7-spark412-official-listener-compose-autonomous-2026-07-18.log`
- `evidence/f7-spark412-official-listener-docker-build-2026-07-18.log`
- `evidence/f7-spark412-autonomous-ps-2026-07-18.log`
- `evidence/f7-spark412-g3-before-diagnosis-2026-07-18.log`
- `evidence/f7-spark412-g5-compare-memory-2026-07-18.log`
