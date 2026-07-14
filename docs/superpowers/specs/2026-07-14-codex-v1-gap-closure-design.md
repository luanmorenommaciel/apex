# Design - Fechamento Dos Gaps V1 Codex

Data: 2026-07-14

Branch: `codex-round2`

## Objetivo

Fechar progressivamente os quatro gaps declarados apos F5:

1. contrato `apply_fix`;
2. validacao MCP/IDE;
3. `docker compose` autonomo da branch;
4. SparkListener JVM real fail-safe.

O principio operacional e preservar G0-G5 verdes. Nenhum componente novo deve
substituir a evidencia existente sem primeiro reproduzir os gates.

## Gate A - `apply_fix` Contract

Status: concluido localmente.

Mudancas:

- `apply_fix` exposto como tool oficial em `apex/commander/tool_contract.py`;
- `apply_recommendation` preservado como alias de compatibilidade;
- `apply_fix` usa o mesmo caminho guardado:
  - preview;
  - approval token;
  - `apply_root`;
  - hash antes/depois;
  - verify.

Evidencia:

```text
evidence/g6-apply-fix-mcp-smoke.log
27 passed
```

## Gate B - MCP Stdio Smoke Local

Status: concluido localmente, incluindo subprocess.

Escopo validado:

- `tools/list` inclui `apply_fix`;
- metadados de safety marcam `apply_fix` como mutacao guardada;
- `tools/call apply_fix` aplica com token valido e verify.
- `python -m apex.commander.mcp_stdio_cli` funciona como processo externo via
  stdin/stdout, aproximando o smoke de um cliente IDE real.

Limite:

- isso ainda nao e validacao em IDE real. Falta smoke em Cursor, VS Code,
  Claude Code ou cliente MCP equivalente.

## Gate C - Docker Compose Autonomo

Status: parcialmente implementado.

O que existe:

- `docker-compose.yml` com ClickHouse, MinIO, Spark master/worker e volumes
  nomeados;
- `docker/spark/spark-defaults.conf` com event log em
  `s3a://spark-logs/events`;
- portas alinhadas ao ambiente `spv0`/plat-v0.
- `docker-compose.autonomous.yml` paralelo, preservando o compose atual;
- `docker/autonomous/` com Dockerfile Spark, `spark-defaults.conf`, init MinIO
  explicito e README operacional.

Evidencia:

```text
evidence/g7-autonomous-compose-config.log
docker compose -f docker-compose.autonomous.yml config

evidence/g7-autonomous-compose-build-v2.log
docker compose -f docker-compose.autonomous.yml build spark-master

evidence/g7-autonomous-compose-ps-final.log
docker compose -f docker-compose.autonomous.yml ps

evidence/g7-autonomous-spark-pi-v2.log
spark-submit PythonPi gravando event log em s3a://spark-logs/events

evidence/g7-autonomous-minio-events-v2.log
eventlog_v2_app-20260714053216-0000 listado no bucket spark-logs/events
```

Bloqueio restante:

- G3/G5 ainda nao foram repetidos na stack autonoma;
- a stack usa `apache/spark:4.0.0-scala2.13-java17-python3-ubuntu`, diferente
  da validacao historica em `plat-v0`; isso precisa ser declarado na comparacao.

Correcao aplicada:

- o primeiro smoke falhou com `NoClassDefFoundError:
  software/amazon/awssdk/auth/credentials/AwsCredentialsProvider`;
- `docker/autonomous/spark/Dockerfile` foi corrigido para baixar AWS SDK v2
  (`software.amazon.awssdk:bundle`) em vez do bundle AWS SDK v1;
- depois da correcao, o Spark gravou event log em S3A/MinIO.

Plano minimo:

1. Criar compose autonomo paralelo, sem remover o compose atual.
2. Adicionar build local ou imagens publicas pinadas.
3. Garantir Spark com suporte S3A/Hadoop AWS.
4. Tornar `minio-init` explicito para criar `spark-logs/events`.
5. Validar `docker compose up -d`, healthchecks e registro master/worker.
6. Rodar job minimo que grava event log em S3A.
7. Repetir G3 e G5 contra a stack autonoma.

Risco:

- trocar imagem Spark/S3A pode quebrar G3/G5. Por isso, o compose autonomo deve
  nascer em paralelo e so substituir o atual depois de reproduzir a evidencia.

## Gate D - SparkListener JVM Real Fail-Safe

Status: implementacao inicial criada localmente, build/JAR/self-test concluido
e validacao via `spark-submit --jars` executada na stack autonoma.

O que existe:

- `apex/commander/spark_rerun_template.py` injeta:
  - `spark.extraListeners=apex.commander.spark.ApexSparkListener`;
  - `spark.apex.jobId=<job_id>`;
- testes confirmam que o comando contem o listener e o job id.

Bloqueio restante:

- ambiente local nao tem `java` nem `gradle` no PATH, entao a validacao foi
  feita via container `gradle:8.10.2-jdk17`;
- o listener ainda precisa entrar no template dos jobs oficiais G3/G5
  autonomos.

Plano minimo recomendado:

1. Criar modulo `listener-jvm/` em Java.
2. Implementar `apex.commander.spark.ApexSparkListener` estendendo
   `org.apache.spark.scheduler.SparkListener`.
3. Cobrir callbacks iniciais:
   - `onApplicationStart`;
   - `onStageSubmitted`;
   - `onTaskEnd`;
   - `onApplicationEnd`.
4. Proteger cada callback com `try/catch Throwable`, sem relancar excecao.
5. Escrever telemetria minima NDJSON append-only:
   - `job_id`;
   - `app_id`;
   - `event_type`;
   - `stage_id`;
   - metricas basicas de task/shuffle/gc/spill quando disponiveis.
6. Gerar JAR via Gradle.
7. Rodar `spark-submit --jars listener.jar --conf spark.extraListeners=...`.
8. Validar que job termina com sucesso mesmo se o listener falhar internamente.

Artefato inicial:

- `listener-jvm/` criado com Java + Gradle;
- classe `apex.commander.spark.ApexSparkListener`;
- callbacks `onApplicationStart`, `onStageSubmitted`, `onTaskEnd` e
  `onApplicationEnd`;
- `try/catch Throwable` em todos os callbacks;
- saida NDJSON configuravel por `spark.apex.listener.output`;
- `spark.apex.listener.failMode=true` para smoke fail-safe;
- self-test sem JUnit em `gradle -p listener-jvm check`.
- JAR gerado em `listener-jvm/build/libs/apex-spark-listener-0.1.0.jar`.

Pendencia:

- integrar o JAR validado ao template dos jobs oficiais e repetir G3/G5 na
  stack autonoma.

Evidencia:

```text
evidence/g9-listener-jvm-environment.log
java/gradle ausentes no host

evidence/g9-listener-jvm-docker-gradle-final.log
gradle selfTest jar em container: ApexSparkListenerSelfTest passed; BUILD SUCCESSFUL

evidence/g9-listener-jvm-spark-submit.log
Spark registrou apex.commander.spark.ApexSparkListener e terminou com exit 0

evidence/g9-listener-jvm-output.ndjson
listener emitiu application_start, stage_submitted, task_end e application_end

evidence/g9-listener-jvm-failsafe-spark-submit.log
spark.apex.listener.failMode=true gerou falhas internas, mas o job terminou com exit 0
```

## Ordem Recomendada

1. Fechar e publicar Gate A/B.
2. Fazer smoke com IDE real.
3. Build/up do compose autonomo paralelo.
4. Reproduzir G3/G5 no compose autonomo.
5. Compilar `listener-jvm` e gerar JAR.
6. Reproduzir G3/G5 com listener habilitado.
7. So depois expandir Crew.ai/Judge real.
