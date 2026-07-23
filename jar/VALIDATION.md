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
  sbtscala/scala-sbt:eclipse-temurin-jammy-17.0.10_7_1.10.4_3.5.2 `
  sbt -batch "apex_41/test" "apex_41/assembly"
```

## Estado atual

**Pendente no ambiente local.** Uma tentativa inicial ficou bloqueada antes da
compilação porque o sbt/Coursier tentou resolver plugins por uma entrada
histórica de `repo1.maven.org`. O projeto agora fixa Maven Central em
`project/repositories`, carregado por `.jvmopts`.

Em 2026-07-23, a nova tentativa carregou o projeto com essa configuração e
baixou dependências, mas `apex_41/test` e `apex_41/assembly` não começaram
dentro do limite de dez minutos. Não existe resultado de teste nem assembly
nesta branch limpa; o gate não deve ser declarado verde até concluir.

## Rollback

Reverter este commit remove somente a célula Spark 4.1.2 e a configuração de
assembly; o contrato de telemetria e as raias vizinhas não são alterados.
