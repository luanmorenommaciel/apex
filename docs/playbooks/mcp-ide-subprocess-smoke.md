# MCP IDE Subprocess Smoke

Este playbook aproxima o smoke MCP local de um cliente IDE real sem abrir GUI.
Ele sobe o servidor com:

```powershell
python -m apex.commander.mcp_stdio_cli
```

e conversa por JSON-RPC/MCP em stdin/stdout, como VS Code, Cursor ou Claude
Code fariam ao iniciar um servidor MCP local.

## Convencao local

Agora ha `.mcp.json` versionado na raiz do repositorio, com o servidor
`apex-commander` em escopo de projeto para Claude Code. Cursor/VS Code podem
usar a mesma forma conceitual de comando stdio.

Validacao feita em 2026-07-14:

```powershell
claude mcp list
claude mcp get apex-commander
```

Evidencia:

```text
evidence/g6-claude-code-project-mcp-smoke.log
```

Resultado: Claude Code reconhece o servidor `apex-commander` em `.mcp.json`,
mas marca como `Pending approval`. Isso ainda nao prova GUI/interacao completa;
o proximo passo e abrir `claude` interativo e aprovar o servidor do projeto.

O smoke executavel e:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python tools/mcp_ide_subprocess_smoke.py
```

Evidencia esperada:

```text
evidence/g6-mcp-ide-subprocess-smoke.jsonl
evidence/generated/mcp-ide-subprocess-smoke/job.py
evidence/generated/mcp-ide-subprocess-smoke/findings.ndjson
evidence/generated/mcp-ide-subprocess-smoke/store.ndjson
```

O transcript precisa conter estes eventos:

```text
initialize
initialized_notification
tools_list
recommend_fix
preview_recommendation
apply_fix
final_source
harness_result
```

## Exemplo de configuracao MCP

Configuracao versionada atual em `.mcp.json`:

```json
{
  "mcpServers": {
    "apex-commander": {
      "type": "stdio",
      "command": "python",
      "args": [
        "-m",
        "apex.commander.mcp_stdio_cli",
        "--store",
        "evidence\\generated\\mcp-ide-subprocess-smoke\\store.ndjson",
        "--finding-store",
        "evidence\\generated\\mcp-ide-subprocess-smoke\\findings.ndjson",
        "--apply-root",
        "evidence\\generated\\mcp-ide-subprocess-smoke"
      ],
      "env": {}
    }
  }
}
```

Para um smoke manual no IDE:

1. Inicie o servidor `apex-commander`.
2. Confira que `tools/list` mostra `apply_fix` com `readOnlyHint: false`.
3. Chame `recommend_fix` com `job_id: "job-42"`.
4. Chame `preview_recommendation` usando o arquivo `job.py` gerado.
5. Passe o token de `preview_recommendation.approval.token` para `apply_fix`.
6. Confirme que `apply_fix.status` e `apply_fix.verification.status` sejam
   `applied` e `verified`.

Este smoke ainda nao prova uma GUI especifica. Ele valida o contrato de processo
externo, stdio persistente, descoberta de tools, token de aprovacao e mutacao
guardada que os clientes MCP de IDE usam.
