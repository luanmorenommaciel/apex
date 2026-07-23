# Validação da Raia JAR - Spark 4.1.2

## Escopo

Esta mudança adiciona a célula `apex_4.1` (Spark 4.1.2 / Scala 2.13.17),
atualiza o plugin `sbt-projectmatrix` e cria o assembly que inclui somente o
plugin Apex e OpenTelemetry. Spark, Jackson e Scala continuam fornecidos pelo
cluster.

## Contrato produzido

- `apex.stage`: métricas de estágio, `job_id` e fingerprint lógico redigido;
- `apex.plan_transition`: decisões estruturais AQE;
- transporte: OTLP/HTTP para `/v1/traces`, de forma assíncrona e limitada.

## Evidência anterior de referência

Na fonte de convergência, a célula Spark 4.1.2 foi executada com Spark, Delta
e S3A reais; o plugin entregou eventos de estágio e transições AQE no
ClickHouse. O resumo sanitizado está em
`docs/convergence/C5-SPARK-4.1.2-VALIDATION-2026-07-22.md` na branch
`gustocezar/feature/codex-base-e2e-convergencia`.

Essa evidência informa o reaproveitamento, mas não substitui o gate deste PR.

## Reprodução do gate deste PR

```powershell
docker run --rm -v "${PWD}:/workspace" -w /workspace/jar `
  -e COURSIER_REPOSITORIES=https://repo.maven.apache.org/maven2 `
  sbtscala/scala-sbt:eclipse-temurin-jammy-17.0.10_7_1.10.4_3.5.2 `
  sbt -batch "apex_41/test" "apex_41/assembly"
```

## Estado atual

**Pendente no ambiente local.** Em 2026-07-23, a tentativa chegou ao
carregamento do build, mas ficou bloqueada antes da compilação ao resolver
`sbt-projectmatrix` pelo Coursier. Não houve resultado de teste ou assembly
nesta branch limpa. O PR não deve declarar o gate Spark 4.1.2 verde até esta
execução concluir.

## Rollback

Reverter este commit remove somente a célula Spark 4.1.2 e a configuração de
assembly; o contrato de telemetria e as raias vizinhas não são alterados.
