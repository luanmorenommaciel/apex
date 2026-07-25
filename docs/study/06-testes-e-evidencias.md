# Testes e evidencias sanitizadas

## Regra de seguranca

Os comandos podem exigir credenciais locais, mas este documento nunca mostra
valor de senha, token, chave de API ou variavel de ambiente completa. Use
placeholders e um gerenciador de segredos/local `.env` ignorado pelo Git.

## Verificacao local registrada em 2026-07-24

| Superficie | Escopo | Resultado | Evidencia/documento |
|---|---|---:|---|
| Gate E2E | `tests/test_e2e_six_lanes.py` | 4 passed | [C10](../convergence/C10-AUGUSTO-E2E-READINESS-2026-07-24.md) |
| SERVE | `serve/tests` | 87 passed | [C10](../convergence/C10-AUGUSTO-E2E-READINESS-2026-07-24.md) |
| ENGINE | `engine/tests`, sem integracao ClickHouse dependente do ambiente | 75 passed | [C10](../convergence/C10-AUGUSTO-E2E-READINESS-2026-07-24.md) |
| DEV | `dev/tests/test_canonical_e2e_assert.py` | 7 passed | [C10](../convergence/C10-AUGUSTO-E2E-READINESS-2026-07-24.md) |
| Crew/Judge provider | smoke externo, sem mutacao | passou | [evidence](../../evidence/engine-c5-crewai-provider-2026-07-24.log) |
| MCP stdio | quatro ferramentas reais | passou | [evidence](../../evidence/serve-c4-stdio-mcp-2026-07-24.log) |

## Evidencia de execucao real ja registrada

O [gate canonico](../e2e/CANONICAL_GATE.md) registra quatro execucoes Spark
4.1.2 em 2026-07-24:

| Cenario | Observacao registrada |
|---|---|
| `skew_join` | p99/p50 47.07; gate das seis raias passou |
| `spill` | 14 estagios; 104076355 bytes de spill em disco |
| `bad_shuffle` | 13 estagios; estagio 15 com shuffle alto em duas tasks |
| `driver_oom` | falha esperada; 16 estagios pre-falha persistidos |

As contagens sao historico de uma execucao especifica, nao SLA e nao devem ser
inventadas para uma nova rodada.

## Reproducao segura do caminho E2E

```powershell
# A senha e fornecida apenas nesta sessao; nunca a coloque no comando ou Git.
$env:APEX_CANONICAL_CH_PASSWORD = '<local-secret>'
Set-Location dev
.\scripts\e2e_canonical.ps1 -StartDev

# Para cada job_id emitido por APEX_SESSION, configure apenas valores locais.
$env:CLICKHOUSE_HOST = '127.0.0.1'
$env:CLICKHOUSE_PORT = '8123'
$env:CLICKHOUSE_USER = 'apex'
$env:CLICKHOUSE_PASSWORD = '<local-secret>'
Set-Location ..
uv run --project serve --extra dev python scripts/e2e_six_lanes.py --job-id '<spark-app-id>'
```

Antes da proxima rodada, confirme que `docker version` responde. Se o daemon
nao responder, a rodada esta bloqueada por ambiente e nao deve ser marcada como
falha do APEX.

## Interpretacao da evidencia

Um gate completo aceita somente quando:

1. eventos existem para um unico `app_id` do `job_id`;
2. ENGINE deterministico gera findings sem chamadas LLM;
3. persistencia e idempotente;
4. MCP `analyze_run` devolve os mesmos findings;
5. a ferramenta MCP e marcada read-only onde aplicavel.

O commit `52a36da` reforca o item 4: `type` e `severity` sao comparados de
forma semantica, e nao pela capitalizacao usada em cada transporte.
