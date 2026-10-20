# Pareceres recebidos e conferência do Codex

Claude e Kimi terminaram as missões delimitadas. Os textos originais foram preservados em acervo local dos pareceres auxiliares; este documento prevalece sobre interpretações auxiliares divergentes. Nenhum parecer é review formal do GitHub nem autorização de merge. A análise documental original segue 525/525, com limites por ficha; não são 525 funcionalidades aceitas.

## Claude — integração #182 × #158/#159

Autoria da #182: Agmar. Heads considerados: #182 `74fdb0791825aa89c419694ec71f2aa3e6ea4d74`, #158 `514b0e573bce9593ac1737869568161b3e951a49`, #159 `1685f8ac91b8e9b68a83d10176519c963e186ad4`. O relatório auxiliar foi verificado contra os patches preservados nas capturas Codex; veja confronto por arquivo preservado no acervo local (14 patches comparados com recibos Codex).

| Ponto | Conclusão conferida | Encaminhamento proposto |
|---|---|---|
| R1: teste novo da #158 usa `front_query` | Confirmado estaticamente: o caso front chama esse helper; #182 remove helper e queries.ts. A combinação que conserve o teste sem adaptação referencia nome ausente. Nenhum teste combinado foi executado. | Portar/remover apenas o caso front ao integrar a arquitetura API-only; preservar as assertivas Serve aditivo/legado e o desempate canônico. |
| R2: testes novos da #159 usam `console_statements`/`QUERIES_TS` | Confirmado estaticamente em `_two_doors`; #182 substitui o leitor por `serve_statements`. O acesso à função removida falha numa combinação sem adaptação. | Portar helper e bindings; preservar controles de empate errado nas duas respostas, dados malformados, seleção de finding e limpeza. |
| R3: conflito textual alegado | **Não demonstrado.** O intervalo dos hunks se sobrepõe em contexto; as linhas efetivamente alteradas lidas não bastam para afirmar conflito de merge ou resolução manual obrigatória. Não foi tentado merge/rebase. | Conferir resultado da integração; manter `browser_seen` da #159 e bindings/limites da #182. Coordenação é necessária pelas dependências R1/R2, independentemente de conflito textual. |
| R4: `refused_count` | Os testes de fragmentos SQL e a réplica TypeScript da regra não executam a CTE. **O corpo da #182 já relata execução live em ClickHouse 24.8, sob usuário readonly: seis stages sintéticos e resultado 3; também relata gate 17/17.** Esses resultados do Agmar devem ser reconhecidos. Comparar o mesmo SQL por duas portas cobre integração, mas não constitui um resultado esperado independente da regra. Não reproduzimos esses resultados nem verificamos uma fixture SQL versionada com esse oráculo. | Conferir primeiro os artefatos e o alcance da prova já apresentada; propor apenas complemento específico que o time considere necessário. Não é defeito demonstrado nem novo bloqueio automático para #182/#158/#159. |
| R5: alcance do gate | Aceito como explicação: comparação de SQL crua com HTTP da mesma implementação verifica integração/serialização; um oráculo canônico separado protege a regra e a ordem. | Explicitar no RUNBOOK ao atualizar o gate. Não descartar a utilidade da comparação. |

Não foram ratificadas as afirmações auxiliares sobre comportamento de join/NULL em ClickHouse, exclusividade de um único oráculo de ordem ou equivalência com Engine. Exigiriam o contrato e a prova específicos. A ausência de alteração no trecho de limpeza foi observada no diff; não prova isolamento de todas as execuções.

Uma ordem possível é revisar #158/#159 e depois adaptar #182; outra é adaptar as duas primeiras após #182. A escolha cabe aos autores/revisores. Nenhum rebase foi feito. Revisão focal dos arquivos Serve não equivale a revisão dos 65 arquivos da #182.

## Kimi — encaminhamentos da Parte07

| Ponto | Conferência | Tratamento na Parte08 |
|---|---|---|
| “23 L1 reconciliadas” | A matriz das 23 existe e separa estado/implementação/aceite; portanto reconciliação não era falsa. A review histórica “2-of-23” não substitui a matriz atual. A formulação curta pode ser ambígua. | Escrever “23 tarefas mapeadas; registro declara duas done/accepted e 21 ready/accepted:false; sem novo aceite nesta auditoria”. As seis L3 e os três YAML são recortes separados. |
| Frase da #105 em outros 15 objetos | O texto antigo nomeava explicitamente #105; não afirmava literalmente prova Git própria em cada outro objeto. A repetição é desnecessária e prejudica leitura por objeto. | Referência específica mantida apenas em #105. Nos demais, preservar o limite da leitura e os recibos próprios; não negar verificações históricas que existam. |
| #172 mistura preparação e execução | Procede: a próxima ação continha preparação documental antes da observação de navegador. | Separar #172a preparação offline de #172b prova com ambiente. Subpassos locais da mesma issue, sem novo tracker. |
| Base/checks #157/#158/#159 | Procede a ressalva de não transferir checks para uma árvore futura. `base_sha` retornado no objeto não prova sozinho o checkout efetivo dos jobs. | Registrar head/base do recibo e a ausência de revalidação da futura integração. Rejeitada a afirmação categórica de que todos os checks executaram a base antiga apenas por esse campo. |
| NOV-03 | É um identificador interno; descrição ajuda o time. | Expandido para fila aberta sem revisão/ordem de ondas, sem publicar tracker duplicado. |

As correções foram aplicadas em cópias sucessoras da Parte08. Parte07 preserva o corte histórico de 48 objetos. Não reescrevemos recibos antigos como se fossem da consulta atual.

## Efeito da #185

No corte histórico desta seção, a consulta retornou **12 PRs + 37 issues = 49 objetos abertos**. A revalidação posterior inventariou 15 PRs abertas; não usar 49 como contagem atual. A #185 é contribuição do Agmar e acrescenta implementação candidata em temas antes só mapeados. Veja [triagem focal](TRIAGEM-PR185.md). Não encerra automaticamente #167/#174/#175/#178/#113 ou N06. Quatro checks verdes e zero reviews são os recibos novos; não reproduzimos os 106 testes nem o runtime relatados pelo autor.

Os estados/heads dos outros 48 foram comparados; seus checks/reviews permanecem os da Parte07. A main segue `c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874`. A revisão do Kimi era intencionalmente do corte Parte07 e não fica incorreta por anteceder a #185.

## Ganho concreto e próximo passo

O time recebe dois pontos de adaptação dos testes identificados antes da integração, limites mais claros para CI/aceite, preparação de navegador separada de execução, e um mapa para reaproveitar a #185 sem duplicar contribuição. O número de modelos concordando não é critério de aceite; importam as fontes e os contracasos.

1. Revisores Serve/Front escolhem a ordem de integração e preservam os controles R1/R2; responsáveis e prazos a confirmar.
2. Revisores DEV/Package/JAR conferem o alcance da #185 perante as issues existentes, sem criar implementação concorrente por inércia.
3. Publicar o adendo pertinente à #181 conforme autorização de Augusto. Provas operacionais e decisões humanas seguem seus critérios, não são substituídas por esta análise.

O parecer original foi produzido sem novas escritas Git/GitHub ou execução de produto. Esta edição é publicada após autorização de Augusto; não houve envio ao Discord. O fechamento amplo e as fontes continuam locais; não há autorização para apagar arquivos.
