# Apex Commander UI Local - Design

Data: 2026-07-19

## Objetivo

Entregar uma demonstracao visual local para o Commander e o time navegarem sem
alterar o caminho deterministico, o contrato MCP ou o `apply_fix` guardado.

## Decisao

Uma aplicacao Python da biblioteca padrao, vinculada somente a `127.0.0.1`,
serve a pagina HTML e duas rotas somente leitura:

```text
GET /              pagina Apex Commander UI
GET /api/health    estado local do servidor
GET /api/snapshot  snapshot sanitizado das evidencias
GET /api/recommendations recomendacao deterministica do job demo
GET /api/preview   preview real em alvo demo fixo, sem approval token
```

Nao existem rotas `POST`, `apply_fix`, tokens de aprovacao ou credenciais na
UI. O preview usa o contrato real, mas apenas um alvo versionado e uma
substituicao fixa; o token retornado internamente e removido antes da resposta.

## Fontes Permitidas

- `evidence/apex-product-readiness-2026-07-19-summary.json`
- `evidence/generated/mcp-ide-subprocess-smoke/store.ndjson`
- `evidence/generated/mcp-ide-subprocess-smoke/findings.ndjson`
- `evidence/crew-judge-external-llm-success-final-2026-07-19.json`

## Validacao

- testes de parsing, escaping e ausencia de controles mutaveis;
- smoke HTTP para pagina, snapshot, health e bloqueio de `POST`;
- guia de demonstracao reproduzivel em menos de 10 minutos.

## Risco e Rollback

O servidor e local, sem autenticacao, e por isso recusa bind fora de loopback.
Para remover a experiencia visual basta nao executar `tools/run_commander_ui.py`;
os modulos de diagnostico, MCP e Spark nao sao afetados.
