# ADR-004 - MCP IDE E apply_fix Guardado

Status: aceita localmente

Data: 2026-07-18

## Contexto

O loop funcional provado pela branch Codex e:

```text
finding -> recommend -> preview -> apply_fix guardado -> rerun -> compare
```

Esse loop ja passou por MCP stdio/subprocesso, mas ainda falta aprovacao interativa em IDE GUI real.

## Decisao

`apply_fix` e o contrato publico preferencial. `apply_recommendation` permanece apenas como alias de compatibilidade. Toda mutacao deve exigir:

- preview de diff;
- approval token;
- validacao de `apply_root`;
- hash antes/depois;
- verify posterior.

## Consequencias

- O Apex pode agir, mas nao age sem aprovacao e evidencia.
- A validacao GUI real deve usar exatamente o contrato `apex-commander`.
- A pendencia CODEX-029 so fecha com transcript de IDE real.

## Evidencias

- `apex/commander/tool_contract.py`
- `apex/commander/apply_verify.py`
- `evidence/g6-mcp-ide-subprocess-smoke.jsonl`
- `.mcp.json`

