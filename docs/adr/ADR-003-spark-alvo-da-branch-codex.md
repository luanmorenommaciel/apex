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

- As evidencias G3/G5 antigas em Spark 4.0.0 continuam historicas, mas nao
  bastam para declarar runtime autonomo 4.1.2 totalmente equivalente.
- G3/G5/G6 devem ser reexecutados em Spark 4.1.2 antes de declarar a stack
  autonoma como runtime final.
- O build da imagem autonoma Spark 4.1.2 depende dos jars S3A/AWS. A tag Spark
  4.1.2 existe e resolveu por digest, mas o download do AWS SDK bundle via Maven
  ainda ficou bloqueado por tamanho/rede nesta rodada.

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
