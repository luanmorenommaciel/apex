# Fontes e contribuições desta complementação

Base: `c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874`, reconfirmada em 19/10/2026 pela API pública da branch main. As fichas L1, patches e recibos históricos já haviam sido revalidados; não houve repetição integral da auditoria.

## Revisão e produção assistidas

Claude instalado recebeu pedido limitado e concluiu duas minutas: ADR-004 e governança das Task-Specs. Kimi instalado recebeu outro pedido e concluiu alternativas Ask, onboarding e distribuição. Codex leu ambos os retornos, consolidou, confrontou as fontes necessárias e conferiu links e dados estruturados. Modelos fornecem contribuições; suas respostas não substituem fonte ou decisão do time.

Correções na integração:

- Regra `done` exige decisão explícita sobre sua relação com aceite. Preservar legado com aceite ausente não pode ser confundido com aprovar a regra para novas entregas.
- A alternativa de fachada pode coexistir com a adaptação da API, mas não é apenas escolher como fatiar PRs: também pode definir responsabilidade de composição/envelope. O contrato decidirá a diferença útil.
- Adiamento não significa “zero risco”: preserva limitações e custo de oportunidade. Nenhuma garantia de ausência de regressão foi incorporada.
- A matriz de evidências e o guia do estado atual começam antes dos merges e sem esperar aprovar Ask ou N11.
- Codex conferiu o comando em `serve/.mcp.json` e README; o Kimi havia registrado essa conferência como lacuna. Os exemplos foram baseados nesses arquivos e nas fontes oficiais.
- O diagrama distingue implementação observada de prova operacional; nginx/browser não recebeu selo de validação da #156.
- Foram conferidos diretamente os seis front matters `done/accepted:false` e os três erros YAML. A correção protege escalares sem executar comandos nem alterar status.

## Fontes públicas principais

- [Índice #181](https://github.com/luanmorenommaciel/apex/issues/181), [L1 #79](https://github.com/luanmorenommaciel/apex/pull/79), [API #129](https://github.com/luanmorenommaciel/apex/pull/129).
- [Ask #122](https://github.com/luanmorenommaciel/apex/issues/122), [política v1 #171](https://github.com/luanmorenommaciel/apex/issues/171), [provas #156](https://github.com/luanmorenommaciel/apex/issues/156), [browser #172](https://github.com/luanmorenommaciel/apex/issues/172).
- [PR #157](https://github.com/luanmorenommaciel/apex/pull/157), [#158](https://github.com/luanmorenommaciel/apex/pull/158), [#159](https://github.com/luanmorenommaciel/apex/pull/159), [#163](https://github.com/luanmorenommaciel/apex/pull/163), [#164](https://github.com/luanmorenommaciel/apex/pull/164).
- Consulta adicional em 19/10: coleção aberta de PRs e listas de arquivos de #182/#157/#158/#159/#163/#164. A nova #182 tem 65 arquivos e sobreposição de caminhos com #158/#159, registrada na [triagem](COORDENACAO-PR-182.md). O corpo relata provas; não foram reproduzidas nesta etapa.
- [ADR-004](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/docs/architecture/ADR-004-SOURCE-CORRELATION-BOUNDARY.md), código/specs/planos nos links de cada ficha L1.
- [Claude MCP](https://code.claude.com/docs/en/mcp), [Cursor MCP](https://cursor.com/docs/mcp), [Cursor integração/logs](https://prod.cursor.com/help/customization/mcp), [Codex MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli), consultados em 19/10/2026.
- [GitHub: rollout Ubuntu 26](https://github.blog/changelog/2026-09-17-ubuntu-26-generally-available-and-latest-migration/), consultado em 19/10/2026; datas de 19/10–19/11/2026.

## Limites

Conferência de documentos, parse YAML/JSON/TOML, cobertura e links não é runtime do APEX. Não foram executados os comandos de produto/planos, testes, build, CI, setup dos clientes ou upload de pacote. O guia tem validação operacional pendente. Decisões fora do GitHub não foram inferidas. Estados de PRs são os snapshots citados; reconferir antes de integrar. Os planos originais inválidos impedem comparar duas árvores YAML válidas; o recibo confirma diff de representação e igualdade dos textos convertidos.
