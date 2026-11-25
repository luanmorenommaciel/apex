# Ask: alternativas para decisão na #122

Estado: proposta para discussão. Decisor, executor, revisor e data: **a confirmar**. Fonte: [#122](https://github.com/luanmorenommaciel/apex/issues/122); a API v1 já entregue na [#129](https://github.com/luanmorenommaciel/apex/pull/129) é o ponto de partida. A política de OpenAPI/token da v1 tem registro próprio na [#171](https://github.com/luanmorenommaciel/apex/issues/171).

## Problema

Escolher a superfície HTTP consumida pelo Ask no perfil compartilhado sem duplicar regras diagnósticas nem publicar o candidato integrado inteiro de uma vez. A existência da API v1 resolve uma parte da infraestrutura; não decide envelope Ask, identidade, intents ou política de navegador.

| Critério | A — adaptar a superfície v1 | B — fachada Ask interna | C — adiar nova superfície |
|---|---|---|---|
| Menor entrega | Explicitar o que o Front pode obter das rotas atuais e o contrato incremental necessário | Contrato Ask e adaptador/roteador no mesmo aplicativo FastAPI, reutilizando serviços | Registro `defer`, limites da API atual e condição de retomada |
| Envelope/intents | Avaliar composição das rotas atuais; não presumir equivalência com os cinco intents propostos | Envelope Ask e despacho de intents explícitos, sem duplicar diagnóstico | Contrato Ask continua proposto; evitar documentação que o apresente como entregue |
| Compatibilidade | Preservar consumidores v1; identificar mudanças aditivas versus quebra | Preservar v1 e versionar a nova fachada; contrato de erros documentado | Preservar o contrato atual; registrar lacunas de produto |
| Impacto no Front | Mais composição pode permanecer no cliente; demonstrar por fluxo antes de escolher | Cliente pode usar uma fronteira Ask; adaptação do Front ocorre após contrato | Continuar comportamento atual dentro do perfil permitido |
| Confiança/autenticação | Definir perfis e quem possui token na #171 | Definir identidade validada, origem, segredo e boundary da fachada; não confiar em identidade arbitrária do body | Documentar política atual e decisões pendentes; adiamento não corrige riscos por si |
| Origin/CSRF | Avaliar credenciais e navegador reais; same-origin não substitui autenticação | Registrar requisitos por perfil e por mecanismo de credencial, incluindo cookies se adotados | Não anunciar garantias futuras; registrar as necessidades do compartilhado |
| Readiness/concorrência | Explicitar comportamento atual e os controles que seriam necessários | Definir prontidão, timeout, limites e saturação com testes do contrato escolhido | Manter limitações visíveis e condição para reabrir o estudo |
| Custo e revisão | Menos superfície nova pode reduzir trabalho; verificar contra os casos reais | Mais contrato/adaptador a manter, porém responsabilidade de composição explícita | Menor implementação imediata, com custo de oportunidade e dívida de decisão |
| Evidência mínima | Mapa caso Ask→rota/serviço e prova de que a composição satisfaz o caso | Prova de contrato, reutilização da camada e perfil compartilhado | Decisão justificada, consumidor atual e gatilho de retomada |

As opções A e B podem coexistir: uma fachada é responsabilidade de código, não obrigação de criar outro processo. Não há estimativa numérica de esforço validada.

## Recomendação proposta

Antes de escolher, mapear os cinco intents da #122 aos serviços/rotas existentes e identificar quais precisam de envelope ou composição. Se a superfície atual satisfizer o consumidor com contrato pequeno, preferir adaptação aditiva. Se houver necessidade demonstrada de uma fronteira Ask, avaliar fachada interna. Se faltarem prioridade ou decisão de confiança, registrar adiamento explícito. Esta recomendação não ratifica nenhuma opção.

## Perguntas e próximos passos

1. Quais consumidores e perfis entram na primeira entrega? Quem decide contrato entre Front/Serve?
2. Que identidade o servidor recebe e valida? Onde ficam token e segredo? Como se relaciona com a #171?
3. Quais intents, esquema de resposta/erro, limites e condições de indisponibilidade entram no primeiro recorte?
4. O que continua local e o que fica permitido no perfil compartilhado? Registrar proposta de same-origin e acesso ao store por perfil.
5. Decisão: `proceed`, `defer`, `reject` ou revisar alternativa; justificativa, decisor e data.

Se `proceed`: dividir contrato/documentação → adaptador Serve → integração Front/perfil, em PRs pequenas com critérios próprios. Não publicar em bloco o candidato local sem reconciliação. #171 pode avançar em paralelo; manter decisões coerentes.

## Conclusão

Conclui a decisão quando a alternativa, limites, autores da decisão e próxima entrega estiverem escritos na #122. Código, testes e release terão aceite próprio. Até lá o estado é **pendente**, e a revisão das PRs de testes atuais pode continuar.
