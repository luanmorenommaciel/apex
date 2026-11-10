# Perguntas de decisão — uma escolha por registro

Alternativas e recomendações para discussão; nenhum item abaixo está ratificado. Responsáveis e prazos não foram nomeados pelo auditor. Aceitar uma arquitetura não encerra automaticamente todas as provas que dela dependem.

## Arquitetura e ordem de integração

- **Onde registrar:** PR #182, coordenada com #158/#159.
- **Alternativas:** Adotar API-only; pedir ajuste delimitado; ou adiar com motivo. A ordem de integração pode variar se preservar os testes.
- **Recomendação para discussão:** Revisar por superfície e manter os dois ajustes conhecidos explícitos.
- **Se adiar:** Adiar mantém a arquitetura atual; mudanças novas na superfície removida precisam coordenação. Não paralisa todos os estudos.
- **Quem precisa participar:** Autores/revisores Front e Serve, a confirmar.
- **Resultado a escrever:** Ordem, revisores e escopo que ficou de fora.

## Token e exposição

- **Onde registrar:** Issue #171.
- **Alternativas:** Definir perfis local, compartilhado ou protegido por proxy; escolher custódia/exposição coerente com cada um.
- **Recomendação para discussão:** Registrar decisão por ambiente; config.js entregue ao browser não é armazenamento secreto ou identidade individual.
- **Se adiar:** A proposta pode ser revisada enquanto a política é discutida; não declarar ambiente compartilhado seguro sem decisão/prova.
- **Quem precisa participar:** Representantes Front/Serve e responsável pelo ambiente, a confirmar.
- **Resultado a escrever:** Perfil, custódia, docs/OpenAPI, motivo e critério de verificação.

## Ask: qual fatia avança?

- **Onde registrar:** Issue #122.
- **Alternativas:** Prosseguir com fatia que usa API existente; avaliar fachada quando houver necessidade; ou adiar/rejeitar escopo com motivo.
- **Recomendação para discussão:** Usar a comparação já preparada no Pod 3; explicitar contrato e sequência Serve→Front.
- **Se adiar:** Ask continua no estado declarado; token ou API-only não resolvem automaticamente esta decisão.
- **Quem precisa participar:** Representantes de produto/Front/Serve, a confirmar.
- **Resultado a escrever:** Fatia, entradas/saídas, fora de escopo e decisão proceed/defer/reject.

## Árvore e casos da prova de navegador

- **Onde registrar:** Issue #172.
- **Alternativas:** Escolher main ou árvore candidata; escolher rotas e casos suficientes para a próxima garantia.
- **Recomendação para discussão:** Preparar protocolo antes da execução e separar relato API/jsdom/curl de browser real.
- **Se adiar:** A ausência de screenshot consultado não invalida automaticamente prova API anterior; garantia específica de navegador continua pendente.
- **Quem precisa participar:** Front/Serve e executor com ambiente, a confirmar.
- **Resultado a escrever:** Árvore/imagem/perfil, casos, exclusões e executor.

## Próxima fatia de contrato e estudos

- **Onde registrar:** Issues #117/#115; #166/#179/#108/#180.
- **Alternativas:** Escolher um consumidor/caso; manter os demais como fila; ou adiar com motivo e gatilho de reavaliação.
- **Recomendação para discussão:** Não juntar piso, atribuição, narrativa de cauda e estudo de modelo em uma implementação monolítica.
- **Se adiar:** Adiar um estudo não bloqueia uma revisão independente.
- **Quem precisa participar:** Representantes dos consumidores envolvidos, a confirmar.
- **Resultado a escrever:** Primeira fatia e seu critério; estudos mantidos na fila.

