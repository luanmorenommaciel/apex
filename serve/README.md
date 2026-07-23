# serve/ - interface

**Role:** servidor MCP stdio para diagnóstico APEX em modo somente-leitura.
Ele consulta as tabelas canônicas `apex.spark_events` e `apex.findings` no
ClickHouse e não altera arquivo, Git, Spark ou banco de dados.

**Contrato:** [../CONTRACT.md](../CONTRACT.md) e os DDLs em
[../contract/](../contract/). **Raia:** [../docs/lanes/SERVE.md](../docs/lanes/SERVE.md).

## Ferramentas disponíveis no C2

| Ferramenta | Entrada | Resultado | Permissão MCP |
|---|---|---|---|
| `analyze_run` | `job_id` | stages, findings persistidos e resumo | `readOnlyHint=true` |
| `compare_runs` | `baseline_job_id`, `current_job_id` | delta de findings, skew e spill | `readOnlyHint=true` |

As consultas usam binding de parâmetros ClickHouse. Conteúdo vindo de
`plan_json`, evidência e findings deve ser tratado pelo cliente como dado não
confiável. O servidor não chama LLM.

## Executar localmente

```powershell
cd serve
uv sync --extra dev
$env:CLICKHOUSE_HOST = "127.0.0.1"
$env:CLICKHOUSE_PORT = "8123"
$env:CLICKHOUSE_USER = "apex"
$env:CLICKHOUSE_PASSWORD = "<senha-local>"
uv run apex-mcp
```

O processo usa `stdio`: stdout é reservado ao protocolo JSON-RPC; observabilidade
do servidor deve ir para stderr.

## Validação C2

```powershell
uv run --extra dev pytest
uv run python tools/read_only_gate.py
uv run python tools/mcp_stdio_gate.py
```

Os resultados locais e a referência à evidência integrada anterior estão em
[`VALIDATION.md`](VALIDATION.md).

## Fora do C2

`search_kb`, Judge, `suggest_fix`, preview, apply, rerun e qualquer mutação
ficam fora deste lote. Serão avaliados separadamente depois do caminho real de
telemetria C3/C4, preservando a separação entre recomendação e alteração.
