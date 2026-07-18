# ADR-001 - Onde O Apex Roda

Status: aceita localmente

Data: 2026-07-18

## Contexto

A branch Codex provou diagnostico e correcao de jobs Spark com evidencias G0-G6. O caminho validado roda fora do job principal como camada de observabilidade e acao assistida:

- event log em S3A/MinIO;
- SparkListener JVM fail-safe;
- store/ClickHouse ou store local por `app_id`/`job_id`;
- detectores T1 deterministicos;
- MCP/apply guardado para interacao com IDE.

## Decisao

O Apex deve operar como camada externa e fail-safe ao workload Spark. Ele pode observar e recomendar, mas nao deve derrubar o job do cliente quando sua propria instrumentacao falhar.

## Consequencias

- SparkListener deve ser fail-safe por padrao.
- `apply_fix` continua fora do runtime Spark e exige aprovacao humana.
- O caminho T1 deve continuar executavel localmente sem SaaS obrigatorio.
- Crew.ai/Judge futuro nao substitui os gates deterministiscos G0-G6.

## Evidencias

- `evidence/g9-listener-jvm-failsafe-spark-submit.log`
- `evidence/g5-ciclo.log`
- `evidence/g6-remote-workflow-latest-summary.json`

