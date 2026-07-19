# Como Testar o Apex Commander UI

## Objetivo

Demonstrar visualmente o loop do Apex sem executar alteracoes: telemetria,
finding validado, Crew/Judge, comparacao before/after e o ponto seguro de
entrada para um preview MCP.

## Inicio Rapido

No diretorio raiz da branch:

```powershell
python tools/run_commander_ui.py
```

Abra `http://127.0.0.1:8765/` no navegador. Para encerrar, pressione `Ctrl+C`
no terminal.

## Roteiro de 10 Minutos

1. Em **Visao Geral**, confirme score, latencia T1 e os apps before/after.
2. Em **Jobs e Findings**, abra o finding de skew e confira ratio e stage.
3. Em **Telemetria por Stage**, compare `before-job` (ratio `29.5`) com
   `after-job` (ratio `1.0`).
4. Em **Crew/Judge**, confira provider, decisao conservadora e citacoes de
   evidencia existentes.
5. Em **Before/After**, confirme que o finding e as metricas melhoraram.
6. Em **Fix Center**, confirme que a tela e demonstrativa: ela nao aplica
   alteracao, nao possui token e orienta usar `preview_fix` pelo MCP.
7. Em **Demo MCP Segura**, clique em **Carregar recomendacao real** e depois
   em **Gerar preview real**. A resposta vem do contrato real do Commander,
   mas o arquivo alvo e fixo (`examples/apex_ui_demo_skew_job.py`) e nenhum
   approval token e devolvido ao navegador.

## Rotas Para Teste Tecnico

```text
GET http://127.0.0.1:8765/
GET http://127.0.0.1:8765/api/health
GET http://127.0.0.1:8765/api/snapshot
```

Qualquer `POST` retorna `405 method_not_allowed`. O servidor recusa hosts fora
de loopback para evitar uma exposicao acidental de evidencias locais. As rotas
`GET /api/recommendations` e `GET /api/preview` sao uma demo fixa e read-only.

## Limites Declarados

Este e um MVP de demonstracao local, nao um SaaS multiusuario. Acoes reais
continuam no fluxo MCP guardado: `recommend_fix` -> `preview_fix` -> aprovacao
humana -> `apply_fix` -> rerun/compare.
