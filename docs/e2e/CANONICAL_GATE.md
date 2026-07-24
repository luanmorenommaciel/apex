# Gate Canônico E2E

## Propósito

`scripts/e2e_six_lanes.py` valida uma aplicação Spark já submetida através das
seis raias:

`DEV -> JAR -> COLLECT -> INFRA -> ENGINE -> SERVE`

O gate falha quando não há telemetria, há mais de um `app_id`, o caminho ENGINE
deixa de ser determinístico, o validador rejeita evidência, a persistência de
findings diverge ou o MCP deixa de ser somente leitura. Repetições são
idempotentes: findings existentes precisam ter a mesma assinatura, não são
duplicados.

## Execução real - 2026-07-24

Ambiente local: Spark 4.1.2, plugin `apex.ApexPlugin`, OTLP Collector,
ClickHouse e MCP stdio.

| Prova | Aplicação | Resultado observado |
|---|---|---|
| skew_join | `app-20260724014653-0000` | passou; razão p99/p50 `47.07`; 12 estágios na asserção de patologia |
| six-lane gate | `app-20260724014653-0000` | passou; 17 eventos/fingerprints, 3 findings determinísticos, 0 chamadas LLM, `analyze_run` read-only |
| spill | `app-20260724015703-0001` | passou; 14 estágios e `104076355` bytes de spill em disco |
| bad_shuffle | `app-20260724020318-0002` | passou; 13 estágios, estágio `15` com shuffle grande em duas tasks |
| driver_oom | `app-20260724021334-0003` | passou; falha esperada do driver e 16 estágios pré-falha persistidos |

As contagens podem aumentar entre a asserção de patologia e o gate das seis
raias porque a ingestão OTLP é assíncrona. O gate exige consistência do conjunto
persistido no instante em que executa; ele não depende de uma contagem fixa de
estágios.

## Reprodução

Pré-requisitos: Docker Desktop, COLLECT e INFRA ativos, rede
`apex-collect-net` e variáveis locais de ClickHouse fornecidas pelo operador.
Não registre essas variáveis em Git.

```powershell
cd dev
make env-spark41
$env:APEX_CANONICAL_CH_PASSWORD = "<local-secret>"
.\scripts\e2e_canonical.ps1 -StartDev
```

Para reusar os dados Delta já existentes e executar só um cenário:

```powershell
.\scripts\e2e_canonical.ps1 -SkipGenerate -Scenario skew_join
```

Depois, execute o gate entre raias com o `job_id` emitido como
`APEX_SESSION job_id=...`:

```powershell
$env:CLICKHOUSE_HOST = "127.0.0.1"
$env:CLICKHOUSE_PORT = "8123"
$env:CLICKHOUSE_USER = "apex"
$env:CLICKHOUSE_PASSWORD = "<local-secret>"
uv run --project serve --extra dev python scripts/e2e_six_lanes.py --job-id <spark-app-id>
```

## Artefatos

- `scripts/e2e_six_lanes.py`: gate cross-lane e MCP stdio real.
- `tests/test_e2e_six_lanes.py`: quatro testes sem infraestrutura externa.
- `dev/scripts/e2e_canonical.ps1`: orquestração Docker nativa no Windows.
- `dev/scripts/canonical_e2e_assert.py`: asserção contra ClickHouse canônico.

Os logs operacionais são escritos em `dev/out/`, que permanece ignorado pelo
Git por poder conter volume excessivo e detalhes do ambiente local.
