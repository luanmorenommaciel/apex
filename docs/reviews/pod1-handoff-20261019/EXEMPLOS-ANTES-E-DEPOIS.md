# Exemplos de contribuição — Pod 1 / Front-end

Exemplos para explicar o benefício, com autoria e limite. Fonte detalhada: [histórico e autoria](ENTREGAS-E-AUTORIA.md). Antes/depois descreve a intenção e a alteração documentada, não uma reprodução de defeito nesta rodada.

## Estado e seleção no Verify

- **Antes:** Uma seleção explícita podia depender do estado da lista de runs, misturando fontes e estados assíncronos.
- **Depois:** Estados por fonte e seleção assíncrona passaram a ser tratados separadamente.
- **Contribuição:** Augusto (`gustocezar`), [#118](https://github.com/luanmorenommaciel/apex/pull/118), [commit a8ccc52](https://github.com/luanmorenommaciel/apex/commit/a8ccc52e8a9db89e84a976ba28cfd00f4401f81f).
- **Prova e limite:** testes e detalhes de CI mantêm o corte histórico. Não é nova prova de navegador.

## Proposta original e evidência fiéis

- **Antes:** Representações diferentes de proposta podiam ser tratadas sem distinguir estrutura e validade com clareza.
- **Depois:** Classificação e apresentação foram ajustadas, preservando o texto original e limites das evidências.
- **Contribuição:** Augusto (`gustocezar`), [#119](https://github.com/luanmorenommaciel/apex/pull/119), [mudança principal 0b4b20d](https://github.com/luanmorenommaciel/apex/commit/0b4b20d228465a93243b65b058dd1a471b725aaa) e [ajustes de review 0f19712](https://github.com/luanmorenommaciel/apex/commit/0f1971255d55b654dc3ead5e0dda6aedd91f12ae).
- **Prova e limite:** não certifica por si a segurança de toda proposta ou a execução runtime.

## Região acessível para proposta original

- **Antes:** O bloco pre tinha nome acessível sem papel explícito adequado.
- **Depois:** O papel region foi declarado e o teste verifica a região nomeada e o texto preservado.
- **Contribuição:** Augusto (`gustocezar`), [#120](https://github.com/luanmorenommaciel/apex/pull/120), [commit 961e296](https://github.com/luanmorenommaciel/apex/commit/961e296b190ee84eff83b50161a03171884dfce2).
- **Prova e limite:** garantia de componente no recorte lido, sem nova sessão de leitor de tela nesta rodada.

## Mecanismo e runtime independentes

- **Antes:** A regra vinculava veredictos que precisam ser analisados separadamente e havia narração incorreta de regressão prevista.
- **Depois:** Os veredictos foram desacoplados e a narração da regressão foi corrigida.
- **Contribuição:** Augusto (`gustocezar`), [#136](https://github.com/luanmorenommaciel/apex/pull/136), [independência 78062d3](https://github.com/luanmorenommaciel/apex/commit/78062d348e23bbede8c9c11499a329088862c9f6) e [narração da regressão 2fa0781](https://github.com/luanmorenommaciel/apex/commit/2fa078104758cf97070328f16ab6066df7d92ce2).
- **Prova e limite:** mantém a decisão de contrato na #117. Resultados locais históricos não foram reproduzidos.

## Erro HTTP legível

- **Antes:** detail em formato de lista podia ser exibido como [object Object].
- **Depois:** Somente detail/error textuais são exibidos; nos demais casos há fallback para o status HTTP.
- **Contribuição:** Augusto (`gustocezar`), [#151](https://github.com/luanmorenommaciel/apex/pull/151), [commit 488bd8a](https://github.com/luanmorenommaciel/apex/commit/488bd8aed068e732f287ac73e939f6642f33fb65).
- **Prova e limite:** testes unitários relatados, sem browser novo. Solução paralela de Agmar na #153 permanece creditada.

## Autoria da base compartilhada

A Console original (#100) e a paridade (#153) são do Agmar. Augusto tem contribuições específicas na #100 e nas PRs acima. A API #129 é do Sidymar, incluindo HTTP/same-origin; fab6620 conclui ajustes de integração feitos por Augusto. A #182 é proposta aberta do Agmar, não entrega integrada de Augusto.
