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
docker run --rm -v "${PWD}:/workspace" `
  -v apex-sbt-ivy:/root/.ivy2 -v apex-sbt-coursier:/root/.cache/coursier `
  -w /workspace/jar `
  sbtscala/scala-sbt:eclipse-temurin-jammy-17.0.10_7_1.10.4_3.5.2 `
  sbt -batch "apex_41/test" "apex_41/assembly"
```

## Estado atual

**Aprovado localmente em 2026-07-24.** O Maven Central está fixado em
`project/repositories`, carregado por `.jvmopts`; os volumes nomeados do
comando preservam apenas o cache de dependências entre execuções.

- `apex_41/test`: **4 testes aprovados**, 0 falhas, em 7 min 52 s.
- T9, com coletor OTLP indisponível: baseline sem plugin de **50.593 ms** e
  execução instrumentada de **38.216 ms**. A prova compara o mesmo workload
  em vez de depender de um limite absoluto que varia em Docker/WSL.
- `apex_41/assembly`: **aprovado**; artefato
  `target/spark41-jvm-2.13/apex_4.1-0.1.0-assembly.jar`.
- SHA-256 do artefato local: `daaca29ab8eb314840a82c3174a590be7fcc8af0c95f5c88fb226da0b717bc26`.

O log de falha de conexão com `127.0.0.1:1` no T9 é esperado: ele é o coletor
deliberadamente indisponível usado para provar que o `BatchSpanProcessor` não
bloqueia o driver.

## Rollback

Reverter este commit remove somente a célula Spark 4.1.2 e a configuração de
assembly; o contrato de telemetria e as raias vizinhas não são alterados.
