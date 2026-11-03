# Validação da Raia INFRA — ClickStack canônico

## Escopo

Esta branch (`feat/infra-performance-improvements`, plano `tasks/.plans/infra-hardening.yaml`)
endurece a raia infra: uma única query do MV de reshape, janela de dedup em todo DDL base,
rollup com as colunas v0.5, skew pela forma fechada do contrato, credenciais sem default e
fora do ambiente dos containers, HyperDX registrado pela API como usuário read-only,
`ddl-migrate` em todo `up`, retenção explícita, `verify-ddl` objeto a objeto, imagens
pinadas por digest, fila persistente do collector, backup/restore e CI com store fresco.

## Contrato

- ClickHouse permanece o store canônico para telemetria e findings;
- `otel_traces` e `otel_logs` são schemas de aterrissagem do exporter (14 dias);
- materialized views transformam spans em `spark_events`, `plan_transitions` e `job_conf`;
- todos os dados continuam correlacionados por `job_id`;
- colunas/engine/chaves pertencem à raia de origem; TTL/SETTINGS pertencem à infra.

## Gates executados nesta branch

Cada folha do plano prova-se em `tests/infra/` (offline, ou vivo com `APEX_INFRA_LIVE=1`
num `clickhouse-server:24.8` descartável). O gate integrado é `make gate` (`scripts/gate.sh`):
sobe a stack REAL a partir do `.env`, com secrets, migração, bootstrap do HyperDX, varredura
de `docker inspect`, portas em loopback, reinício do collector durante uma queda do
ClickHouse e, no caminho fresco, o `tests/e2e/run.sh` completo.

### Caminho de convergência (volume pré-existente) — 2026-11-03

```
WIPE=0 SKIP_E2E=1 APEX_CLUSTER_SLOTS=8 ./scripts/gate.sh
== 0/9 preconditions ==
  PASS WIPE=0: volumes kept (converge path)
  PASS no foreign apex stack running
== 1/9 volumes ==
  PASS stack stopped, volumes kept: apex-infra_ch-backups apex-infra_ch-data apex-infra_mongo-data apex-infra_otel-queue 
== 2/9 make up (preflight -> compose up --wait -> HyperDX bootstrap) ==
  PASS make up
  PASS apex-infra-clickhouse running
  PASS apex-infra-mongodb running
  PASS apex-infra-hyperdx running
  PASS apex-infra-otel-collector running
  PASS ddl-migrate completed (exit 0)
== 3/9 seed + verify.sh (APEX_CLUSTER_SLOTS=8) ==
  PASS seed.sh
  PASS verify.sh (exit criterion + tail-bound stage)
== 4/9 make verify-ddl (every object, clause by clause) ==
  PASS verify-ddl: ✅ verify-ddl PASSED — 16 objects match their DDL sources clause by clause.
== 5/9 no admin password in any container environment; every port on loopback ==
  PASS docker inspect: admin password in no apex-infra-* environment
  PASS every published port is bound to 127.0.0.1
== 6/9 HyperDX seeded through the API as the read-only user ==
  PASS GET /installation: team exists
  PASS HyperDX connection user: apex_hdx
  PASS Spark Events source seeded
== 7/9 collector restart during a ClickHouse outage loses nothing ==
  PASS clickhouse stopped
  PASS span accepted by the collector while ClickHouse is down (HTTP 200)
  PASS collector restarted (queue must come back from file_storage)
  PASS clickhouse started
  PASS the span landed in spark_events after the restart (job_id gate-20261103T192355Z)
== 8/9 tests/e2e/run.sh (dev -> jar -> collector -> ClickHouse -> HyperDX) ==
  SKIP (SKIP_E2E=1)
== 9/9 result ==
✔ INFRA GATE GREEN — WIPE=0, slots=8, 2026-11-03T19:24:06Z
```

Observação: neste host a porta 8000 está ocupada por outro processo, por isso o `.env`
local desloca `HYPERDX_API_HOST_PORT=28000` (a porta do container permanece 8000 por causa
do healthcheck embutido na imagem).

### Caminho fresco (volumes apagados, e2e completo) — 2026-11-03

```
WIPE=1 APEX_CLUSTER_SLOTS=8 SKIP_BUILD=1 DEV_EXTRA_COMPOSE_FILES=.apex/dev-minio-fallback.yml ./scripts/gate.sh
== 0/9 preconditions ==
  PASS WIPE=1: the infra volumes will be deleted (fresh path)
  PASS no foreign apex stack running
== 1/9 volumes ==
  PASS infra volumes removed
== 2/9 make up (preflight -> compose up --wait -> HyperDX bootstrap) ==
  PASS make up
  PASS apex-infra-clickhouse running
  PASS apex-infra-mongodb running
  PASS apex-infra-hyperdx running
  PASS apex-infra-otel-collector running
  PASS ddl-migrate completed (exit 0)
== 3/9 seed + verify.sh (APEX_CLUSTER_SLOTS=8) ==
  PASS seed.sh
  PASS verify.sh (exit criterion + tail-bound stage)
== 4/9 make verify-ddl (every object, clause by clause) ==
  PASS verify-ddl: ✅ verify-ddl PASSED — 16 objects match their DDL sources clause by clause.
== 5/9 no admin password in any container environment; every port on loopback ==
  PASS docker inspect: admin password in no apex-infra-* environment
  PASS every published port is bound to 127.0.0.1
== 6/9 HyperDX seeded through the API as the read-only user ==
  PASS GET /installation: team exists
  PASS HyperDX connection user: apex_hdx
  PASS Spark Events source seeded
== 7/9 collector restart during a ClickHouse outage loses nothing ==
  PASS clickhouse stopped
  PASS span accepted by the collector while ClickHouse is down (HTTP 200)
  PASS collector restarted (queue must come back from file_storage)
  PASS clickhouse started
  PASS the span landed in spark_events after the restart (job_id gate-20261103T194056Z)
== 8/9 tests/e2e/run.sh (dev -> jar -> collector -> ClickHouse -> HyperDX) ==
== 1/6 infra up (canonical ClickStack) ==
  PASS apex.spark_events exists
  PASS apex.findings exists
  PASS apex.spark_jobs_1m exists
  PASS apex.otel_traces exists
  PASS apex.otel_traces_trace_id_ts exists
  PASS apex.plan_transitions exists
  PASS apex.otel_logs exists
  PASS apex.job_conf exists
  PASS apex.plan_memory exists
  PASS apex.run_outcomes exists
  PASS apex.fix_verifications exists
  PASS apex.spark_jobs_1m_mv exists
  PASS apex.otel_traces_trace_id_ts_mv exists
  PASS apex.mv_spark_events exists
  PASS apex.mv_plan_transitions exists
  PASS apex.mv_job_conf exists
  PASS collector health :13133
  PASS HyperDX UI :8090
== 2/6 network glue: infra collector on apex-collect-net (own name only, no alias) ==
  PASS infra collector joined apex-collect-net as apex-infra-otel-collector
== 3/6 dev lane up (plugin baked from ../jar) ==
  PASS dev → apex-infra-otel-collector:4318 reachable
== 4/6 run instrumented pathology: skew_join, ApexPlugin, AQE on (CONTRACT §Activation) ==
  PASS skew_join completed (exit 0)
  PASS job_id=app-20261103194135-0000
== 5/6 assert the signal landed in infra ClickHouse (job_id=app-20261103194135-0000) ==
  PASS spark_events: 20 stage rows
  PASS plan_transitions: 3 AQE decision(s): ['coalesce/HIGH','coalesce/HIGH','skew_split/HIGH']
  PASS skew watcher (sql/050 A): 2 tail-bound stage(s) at 8 slots
  PASS plan_fingerprint present (8 distinct plans)
  PASS redaction: plan_json carries no literals/paths/emails
== 6/6 HyperDX query engine sees the job ==
  PASS HyperDX first user registered (or already present)
  PASS HyperDX charts/series returns app-20261103194135-0000
== teardown ==
  PASS e2e runner green
== 9/9 result ==
✔ INFRA GATE GREEN — WIPE=1, slots=8, 2026-11-03T19:42:07Z
```

`SKIP_BUILD=1` reaproveita a imagem `apex-spark:local` construída logo antes; o overlay
`.apex/dev-minio-fallback.yml` (gitignored, só neste host) troca as imagens MinIO que o Docker
Hub deixou de servir — nenhum dos dois toca arquivos da raia.

### O que o gate encontrou (e esta branch corrigiu)

- `seed.sh` inseria `findings` sem lista de colunas; desde as colunas v0.2 (`app_id`,
  `confidence_score`) o ClickHouse recusava com HTTP 400 que o `curl -s` engolia — num volume
  fresco havia zero findings e o critério de saída do `verify.sh` falhava sem dizer por quê.
  Agora a lista é explícita, `curl -f` torna o erro fatal e o script confere a contagem.
- `seed.sh` dormia 4 s fixos antes de derivar findings; numa stack fria os spans ainda não
  tinham aterrissado. Agora espera (até 60 s) pelas 51 linhas semeadas.
- `tests/e2e/run.sh` tinha as portas de host do HyperDX/collector fixas em 8000/8090/13133;
  lê-as do `infra/.env` (este host desloca a API para 28000 porque a 8000 está ocupada) e
  deriva `dev/secrets/` do `dev/.env`, que a raia dev passou a exigir.
- A política de senha do HyperDX 2.43 exige maiúscula, minúscula e caractere especial
  (um hex é recusado com 400): documentado em `.env.example`, `hyperdx_bootstrap.sh`,
  `scripts/apex.ps1` e README.
- `NEXT_PUBLIC_SERVER_URL` apontava para a porta do container; o browser disca a porta do
  host — corrigido no compose. A porta do container fica em 8000 (healthcheck da imagem).

## Limite e rollback

Reverter esta branch restaura o compose anterior (credenciais por env, `apex.*` para o
`apex_ro`, TTL de 90 dias nas tabelas cruas) — os dados não são tocados por um revert, mas
um volume que já recebeu `042` mantém os TTLs novos até um `MODIFY TTL` manual. Réplica
continua fora de escopo (nó único por desenho); `make backup` é o caminho de recuperação.
