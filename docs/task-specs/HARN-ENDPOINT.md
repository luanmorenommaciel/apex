# Task-Spec — HARN-ENDPOINT

## Identidade

- `task_spec_id`: `HARN-ENDPOINT`
- `created_at_utc`: `2026-08-19T23:55:08Z`
- `harness_execution_id`: `codex-harn-endpoint-20260819`
- `predecessor_receipt_sha256`: `null`

## Intenção

Permitir que o harness E2E confirme opcionalmente a identidade do servidor
ClickHouse já conectado antes de executar o gate, o MCP ou qualquer persistência
de findings.

## Contrato

- Hipótese falsificável: quando `CLICKHOUSE_EXPECTED_HOSTNAME` está configurada,
  comparar seu valor exato com a única linha de `SELECT hostName()` impede que o
  gate opere sobre um servidor ClickHouse diferente do autorizado.
- Única variável: identidade declarada do servidor ClickHouse já conectado.
- Escopo autorizado: `scripts/e2e_six_lanes.py`,
  `tests/test_e2e_six_lanes.py`, `docs/e2e/README.md` e esta Task-Spec.
- Proibições: não alterar contratos, DDL, código de produção das raias, Docker,
  credenciais, persistência, remotos Git ou dependências.
- Given / When / Then: dado um cliente conectado e um hostname esperado não
  vazio, quando o harness consulta `SELECT hostName()`, então `run_gate` só pode
  iniciar se houver exatamente um hostname não vazio e exatamente igual ao
  esperado.
- Critério de aceite: cinco novos testes unitários passam offline e a suíte root
  existente permanece verde; ausência ou valor literal vazio da variável não
  adiciona query e mantém o comportamento anterior.
- Rollback: descartar somente as alterações nos quatro caminhos autorizados.
- Receipt esperado: saída local do `make test-root` e diff Git revisado.

## Comportamentos verificáveis

- **B-1** — variável ausente ou literal vazia não executa query adicional.
- **B-2** — hostname único, não vazio e exatamente igual permite iniciar o gate.
- **B-3** — hostname diferente impede que `run_gate` seja chamado.
- **B-4** — resposta sem linha, com múltiplas linhas, sem o campo `hostName()` ou
  com hostname vazio falha fechada.
- **B-5** — erro da query falha com `GateFailure` sanitizado, sem URL, senha ou
  nomes/valores de variáveis de ambiente.

## Validação offline

```bash
UV_OFFLINE=1 make test-root
git diff --check
git diff -- scripts/e2e_six_lanes.py tests/test_e2e_six_lanes.py docs/e2e/README.md docs/task-specs/HARN-ENDPOINT.md
```

## Decisões de fronteira

- `_connect_clickhouse()` conserva o comportamento anterior.
- A identidade é consultada pelo mesmo cliente, antes de `run_gate`, MCP ou
  persistência.
- A comparação é exata; não há trim, normalização de caixa ou aliases.
- Falhas não incluem hostname esperado/real, URL, usuário, senha ou env vars.
- O trabalho termina sem commit, push ou abertura de PR.
