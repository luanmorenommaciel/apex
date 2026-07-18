# Playbook - Smoke IDE GUI Do apex-commander

Status: pendente de execucao em GUI real

Data: 2026-07-18

## Objetivo

Fechar CODEX-029 validando o servidor MCP `apex-commander` dentro de uma IDE real, nao apenas por subprocesso local.

IDE alvo:

- Claude Code, preferencial porque ja reconheceu `.mcp.json`;
- Cursor ou VS Code, se configurados para MCP stdio.

## Pre-condicoes

Na raiz da branch:

```text
.mcp.json
```

Servidor configurado:

```text
apex-commander
```

Comando configurado:

```text
python -m apex.commander.mcp_stdio_cli
```

Evidencia atual:

```text
evidence/g6-claude-code-project-mcp-smoke.log
```

Estado esperado antes da aprovacao:

```text
Pending approval
```

## Passos Na GUI

1. Abrir a branch no Claude Code/Cursor/VS Code.
2. Aprovar o servidor MCP `apex-commander` quando a IDE pedir permissao.
3. Confirmar que o servidor aparece como ativo.
4. Executar, pela superficie MCP da IDE, uma chamada equivalente a `tools/list`.
5. Executar uma chamada read-only, preferencialmente `recommend_fix`.
6. Executar `preview_fix` ou `preview_recommendation` e confirmar que o diff e exibido sem alterar arquivo.
7. Executar `apply_fix` somente contra o workspace de smoke em `evidence/generated/mcp-ide-subprocess-smoke`, com approval token valido.

## Evidencia A Salvar

Salvar transcript ou screenshot textual em:

```text
evidence/g6-mcp-ide-gui-smoke-2026-07-18.log
```

Conteudo minimo esperado:

```text
IDE: Claude Code/Cursor/VS Code
Server: apex-commander
Status: approved/active
tools/list: success
recommend_fix: success
preview_fix: success, no file mutation
apply_fix: success, guarded mutation inside apply_root
```

## Criterio De Fechamento

CODEX-029 fecha quando:

- a IDE real mostra `apex-commander` aprovado/ativo;
- `tools/list` retorna tools incluindo `apply_fix`;
- uma chamada read-only funciona;
- o preview mostra diff sem mutacao;
- `apply_fix` funciona apenas dentro de `apply_root`;
- a evidencia fica salva em `evidence/g6-mcp-ide-gui-smoke-2026-07-18.log`.

Depois de salvar o transcript, rode:

```powershell
uv run --with-requirements requirements.txt python tools/agentic_validation_loop.py --iterations 2 --output evidence/agentic-validation-loop-report.json
```

O loop deve reconhecer automaticamente os marcadores do transcript e mudar
`mcp_project_config` para `pass`.

## O Que Nao Fazer

- Nao aplicar fix fora de `evidence/generated/mcp-ide-subprocess-smoke`.
- Nao usar arquivo real de cliente para smoke.
- Nao fechar CODEX-029 apenas com subprocesso local; isso ja foi feito e nao substitui GUI real.
