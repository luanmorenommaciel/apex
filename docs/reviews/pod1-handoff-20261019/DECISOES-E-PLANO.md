# Três encaminhamentos propostos — Pod 1 / Front-end

Escolher a primeira revisão e confirmar papéis/prazos com o time. Estes são recortes de preparação, não três implementações já autorizadas. Decisões adicionais ficam separadas em [PERGUNTAS-DE-DECISAO.md](PERGUNTAS-DE-DECISAO.md).

## 1. Revisar a proposta API-only e preservar os testes

- **Tipo:** Preparação e revisão sem runtime.
- **Entrada:** Heads da PR #182 (74fdb079), #158 (514b0e57) e #159 (1685f8ac), com os dois usos de helpers removidos já identificados.
- **Entrega pequena:** Parecer por superfície Front/Serve, ordem de integração proposta e lista das duas adaptações dos testes.
- **Concluído quando:** A proposta preserva os casos Serve aditivo/legado, desempate canônico, controles de dados malformados e limpeza. Nomear os trechos lidos e o que fica fora; não afirmar conflito textual de merge sem prova.
- **Dependência real:** Coordenação técnica dos testes na superfície que a #182 remove; não depende de resolver Ask ou todos os estudos. Validar a combinação será uma etapa posterior à escolha da árvore.
- **Papel a combinar:** Autores e revisores de Front e Serve, a confirmar.
- **Prazo:** a combinar, depois de confirmar o responsável.

## 2. Escolher o perfil de exposição e custódia do token

- **Tipo:** Decisão do time.
- **Entrada:** Alternativas por perfil e o fato de que a proposta #182 entrega apiToken ao navegador por config.js.
- **Entrega pequena:** Registro de decisão por ambiente: exposição de docs/OpenAPI e lugar de custódia do token, com motivo e eventual adiamento.
- **Concluído quando:** A decisão distingue perfil local, ambiente compartilhado e proteção por proxy; não chama token compartilhado de identidade individual. O responsável pela política é confirmado pelo time.
- **Dependência real:** A política precisa ser coerente com o perfil que for adotado; pode ser discutida enquanto a revisão de código avança. Não cria bloqueio universal de leitura ou estudo.
- **Papel a combinar:** Representantes de Front/Serve e responsável pelo ambiente, a confirmar.
- **Prazo:** a combinar, depois de confirmar o responsável.

## 3. Reconciliar as provas existentes com os critérios HTTP no navegador

- **Tipo:** Preparação sem runtime.
- **Entrada:** Recibos do Agmar: E2E histórico #153, corpo/commits #182, imagem/curl/fixtures e relato de E2E nginx compartilhado no Discord, com cortes separados.
- **Entrega pequena:** Mapa dos critérios já atendidos e eventual complemento específico da #172, com rotas, dados, recibos e exclusões. Primeiro conferir as provas existentes, sem repetir trabalho suficiente.
- **Concluído quando:** Identificar commit, imagem, DATA_SOURCE=http, perfil de token, request por nginx, resposta sanitizada e estado visual esperado. Incluir vazio, erro e indisponibilidade; ausente não vira zero nem fixture silenciosa.
- **Dependência real:** Conferir os recibos pode avançar offline. Somente eventual execução adicional depende do residual identificado, árvore e ambiente próprios, fora desta entrega.
- **Papel a combinar:** Revisores/executores de Front e Serve, a confirmar.
- **Prazo:** a combinar, depois de confirmar o responsável.

## Execução posterior

Testar uma combinação, operar stack, executar navegador ou medir overhead exige o ambiente e o escopo específicos. Preparar um controle não equivale a executá-lo. Registrar somente os resultados realmente obtidos.
