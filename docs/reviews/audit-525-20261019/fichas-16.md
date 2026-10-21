# Fichas documentais — lote 16

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-151"></a>

## DEC-16 — Atualizar escopo do monitor automático — concluída

Frente: decisoes_produto_e_custodia. Encaminhamento: historico_concluido_declarado_sem_reexecucao.

### Identidade e estado

DEC-16 — Atualizar escopo do monitor automático — concluída. Papel proposto: custodiante indicado no registro; não é atribuição nova. Estado desta ficha: historico_concluido_declarado_sem_reexecucao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Preservar a história da decisão sobre monitor automático, distinguindo conclusão declarada de verificação atual de todos os artefatos.

### Feito, faltante e não comprovado

O registro declara escopo atualizado e executor versionado, citando runs e 55 itens. Não foi inspecionada a configuração ativa da automação nem reexecutado o monitor.

### Linhagem

DEC histórica → G06 → conclusão declarada no registro; emprego posterior da evidência tem recorte próprio.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 444. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Registro do monitor → execução histórica declarada → resultados preservados; qualquer uso atual exige conferir corte/escopo.

### Consequências e risco

Reabrir por falta de reexecução duplica custódia; tratar relato histórico como comprovação atual excede a fonte. Nenhuma perda de arquivo foi demonstrada aqui.

### Alternativas e recomendação

Manter encerrada documentalmente; verificar apenas o artefato necessário antes de reutilizá-lo; reabrir se houver divergência específica. Não alterar fontes para alinhar estado.

### Dependências e paralelismo

Sem gate de produto novo. Destino funcional, autoria de handoff e integridade de artefato usado são decisões/verificações distintas.

### Plano e aceite propostos

Não reiniciar monitor nem criar agendamento nesta auditoria. Reabrir apenas se uso atual revelar lacuna de escopo relevante; manter conclusão histórica como relato.

### Comunicação entre responsáveis

Conservar nota datada local; não publicar material de custódia nem mensagens externas por esta ficha.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Reabrir a decisão por falta de reexecução duplicaria custódia, e tratar o relato histórico do monitor como comprovação atual excederia a fonte. Que caso o teste ainda não cobre? — Não se sabe se a automação está ligada hoje ou se só existe o registro antigo, nem se o hash ou recibo identifica o artefato usado ou só um documento que o descreve; a configuração ativa não foi inspecionada. Como eu explicaria isso para outro pod? — Concluída no registro, com escopo atualizado e executor versionado, não significa reexecutada agora; o encerramento histórico fica preservado com esse limite.

### Próxima ação e encerramento

Próxima ação proposta, custodiante indicado no registro: preservar o encerramento histórico com os limites de conferência explícitos. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-152"></a>

## DEC-17 — Preservar o candidato Ask V2 não commitado — concluída

Frente: decisoes_produto_e_custodia. Encaminhamento: historico_concluido_declarado_sem_reexecucao.

### Identidade e estado

DEC-17 — Preservar o candidato Ask V2 não commitado — concluída. Papel proposto: custodiante indicado no registro; não é atribuição nova. Estado desta ficha: historico_concluido_declarado_sem_reexecucao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Preservar a história da decisão sobre preservação do candidato Ask V2, distinguindo conclusão declarada de verificação atual de todos os artefatos.

### Feito, faltante e não comprovado

Registro declara c73269f como evidência e 9e68c10 como snapshot sanitizado, sem ancestralidade do primeiro. README da custódia declara inclusão do bundle sanitizado e exclusão do original com valores locais. Não foi refeito o inventário do candidato nem teste de aplicação.

### Linhagem

DEC histórica → X11 → conclusão declarada no registro; emprego posterior da evidência tem recorte próprio.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 462. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Candidato local → snapshot sanitizado declarado → custódia → decisão funcional #122 separada.

### Consequências e risco

Reabrir por falta de reexecução duplica custódia; tratar relato histórico como comprovação atual excede a fonte. Nenhuma perda de arquivo foi demonstrada aqui.

### Alternativas e recomendação

Manter encerrada documentalmente; verificar apenas o artefato necessário antes de reutilizá-lo; reabrir se houver divergência específica. Não alterar fontes para alinhar estado.

### Dependências e paralelismo

Sem gate de produto novo. Destino funcional, autoria de handoff e integridade de artefato usado são decisões/verificações distintas.

### Plano e aceite propostos

Conservar artefato e registro; se houver proceed na #122, conferir identidade e diferença contra API #129 antes de qualquer reuso. Não reabrir a decisão de preservação apenas porque a feature segue indecisa.

### Comunicação entre responsáveis

Conservar nota datada local; não publicar material de custódia nem mensagens externas por esta ficha.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Compartilhar o candidato original c73269f em vez do snapshot sanitizado 9e68c10 poderia expor valores locais que a custódia excluiu de propósito. Que caso o teste ainda não cobre? — O inventário do candidato e um teste de aplicação não foram refeitos, e o recibo pode descrever o artefato sem identificá-lo pelo hash; antes de qualquer reuso falta comparar com a API da #129. Como eu explicaria isso para outro pod? — Concluída no registro significa preservado, não reexecutado agora; o destino funcional do Ask continua na #122.

### Próxima ação e encerramento

Próxima ação proposta, custodiante indicado no registro: preservar o encerramento histórico com os limites de conferência explícitos. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-153"></a>

## DEC-18 — Custódia dos relatórios 09-21 — concluída

Frente: decisoes_produto_e_custodia. Encaminhamento: historico_concluido_declarado_sem_reexecucao.

### Identidade e estado

DEC-18 — Custódia dos relatórios 09-21 — concluída. Papel proposto: custodiante indicado no registro; não é atribuição nova. Estado desta ficha: historico_concluido_declarado_sem_reexecucao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Preservar a história da decisão sobre custódia dos relatórios de 21/09, distinguindo conclusão declarada de verificação atual de todos os artefatos.

### Feito, faltante e não comprovado

Registro declara 126 arquivos, reconciliação e bundle sanitizado preservados fora do iCloud. README local confirma propósito e localização. Não foram revalidados todos os 126 hashes nesta ficha; X16 continua como follow-up separado.

### Linhagem

DEC histórica → X10 → conclusão declarada no registro; emprego posterior da evidência tem recorte próprio.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 480. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Relatórios históricos → cópia de custódia declarada → referência pela análise → eventual conferência do arquivo efetivamente necessário.

### Consequências e risco

Reabrir por falta de reexecução duplica custódia; tratar relato histórico como comprovação atual excede a fonte. Nenhuma perda de arquivo foi demonstrada aqui.

### Alternativas e recomendação

Manter encerrada documentalmente; verificar apenas o artefato necessário antes de reutilizá-lo; reabrir se houver divergência específica. Não alterar fontes para alinhar estado.

### Dependências e paralelismo

Sem gate de produto novo. Destino funcional, autoria de handoff e integridade de artefato usado são decisões/verificações distintas.

### Plano e aceite propostos

Manter o registro encerrado no seu recorte. Conferir artefato específico se for usado como prova posterior; não recustodiar toda a coleção sem motivo.

### Comunicação entre responsáveis

Conservar nota datada local; não publicar material de custódia nem mensagens externas por esta ficha.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Reabrir para recustodiar toda a coleção sem motivo duplicaria trabalho, e tratar a custódia declarada como comprovação atual dos 126 arquivos excederia a fonte. Que caso o teste ainda não cobre? — Os 126 hashes não foram revalidados nesta ficha; antes de usar um relatório como prova é preciso localizá-lo e identificá-lo pelo recibo, sem alterar a custódia. Como eu explicaria isso para outro pod? — Concluída no registro, com relatórios de 21/09 guardados fora do iCloud, não significa reexecutada agora; o X16 continua como follow-up separado.

### Próxima ação e encerramento

Próxima ação proposta, custodiante indicado no registro: preservar o encerramento histórico com os limites de conferência explícitos. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-154"></a>

## DEC-19 — Estudos #106–#109, #112–#114: adotar/adiar/rejeitar

Frente: decisoes_produto_e_custodia. Encaminhamento: decisao_pendente_sem_autorizacao.

### Identidade e estado

DEC-19 — Estudos #106–#109, #112–#114: adotar/adiar/rejeitar. Papel proposto: mantenedor e responsáveis pelos estudos; não é atribuição nova. Estado desta ficha: decisao_pendente_sem_autorizacao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Escolher adoção, adiamento ou rejeição por benefício e risco de cada estudo, sem impor uma fila serial universal.

### Feito, faltante e não comprovado

#106–109 e #112–114 estão abertas na captura. Poucos/zero comentários não provam ausência de atividade. #112 contém resultado posterior com schema JSON e três exemplos; não apenas proposta parcial. Os corpos separam estudos, implementação e runtime.

### Linhagem

X07/F15/E05–07/S12–13 → estudos públicos → resultados delimitados → decisão por estudo → implementação opcional em novas folhas.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 498. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Pergunta → estudo/documento/matriz → avaliação de utilidade → adotar, adiar com gatilho ou rejeitar; implementar só se decidido.

### Consequências e risco

Adiar tudo até v1 por rótulo pode postergar estudo que reduz risco da própria release. Adotar resultados declarados sem prova pode criar dependências artificiais.

### Alternativas e recomendação

Priorizar estudo que informa decisão próxima; tocar frentes independentes em paralelo; adiar com motivo e condição de retomada. Não escolher pós-v1 automaticamente por falta de comentários.

### Dependências e paralelismo

#107–109 podem estudar em paralelo a #106; implementação aguarda schema pertinente. #108 não exige obrigatoriamente provider #107. Design #113/#114 não espera concluir #167/#170; runtime tem requisitos próprios.

### Plano e aceite propostos

Para cada issue: registrar pergunta, resultado existente, menor entrega e critério de decisão. Se adiar, ligar reativação a necessidade concreta. Não abrir implementação sem conclusão do estudo.

### Comunicação entre responsáveis

Atualizações propostas por issue com o resultado e próximo responsável, sem publicar só “pós-v1” para toda a família.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Adiar todos os estudos para pós-v1 por rótulo poderia postergar um estudo que reduz incerteza de uma decisão próxima, e adotar resultados declarados sem prova criaria dependências artificiais. Que caso o teste ainda não cobre? — Ausência de comentário não é ausência de resultado: a #112 já tem schema JSON e três exemplos; cada estudo ainda precisa de pergunta, resultado existente e critério de decisão registrados. Como eu explicaria isso para outro pod? — Os estudos #106–#109 e #112–#114 podem correr em paralelo, e só a implementação tem dependências específicas, como o schema da #106; cada um se decide entre adotar, adiar com gatilho ou rejeitar.

### Próxima ação e encerramento

Próxima ação proposta, mantenedor e responsáveis pelos estudos: formular prioridade e critério de decisão por estudo. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-155"></a>

## DEC-20 — Merge da PR #1 e prioridade do roadmap do laboratório

Frente: decisoes_produto_e_custodia. Encaminhamento: decisao_externa_no_corte.

### Identidade e estado

DEC-20 — Merge da PR #1 e prioridade do roadmap do laboratório. Papel proposto: mantenedor do laboratório externo; não é atribuição nova. Estado desta ficha: decisao_externa_no_corte; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Distinguir integração do laboratório Dataship das dependências realmente demonstradas no produto APEX.

### Feito, faltante e não comprovado

Recibos públicos de 16/10 mostram Dataship PR#1 aberta, 2 arquivos alterados, e PR #2 aberta, 1426 arquivos alterados. O número é changed_files, não 1426 arquivos necessariamente adicionados. Não houve revisão integral desses diffs nesta decisão nem consulta atual implícita.

### Linhagem

P10/D01/D15 → PRs do laboratório → decisão do upstream → eventual consumidor APEX, cuja dependência precisa ser demonstrada separadamente.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 516. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Ambiente do laboratório → output/dependências do loader → estudo e consumidor externo; isso não certifica execução das lanes APEX.

### Consequências e risco

Tratar PR externa como bloqueio geral da v1 cria caminho crítico sem prova. Contagem grande não demonstra defeito ou necessidade de merge.

### Alternativas e recomendação

Upstream pode revisar, dividir, integrar ou rejeitar; no plano APEX, delimitar o consumidor que precisa do resultado ou manter a trilha externa independente.

### Dependências e paralelismo

Nenhuma dependência técnica universal da v1 demonstrada. Uma entrega APEX específica pode vir a depender de dado/artefato do laboratório, mas precisa explicitar essa aresta.

### Plano e aceite propostos

Preservar estado datado e referências; antes de decisão de integração externa, reconsultar PRs e revisar diff/prova próprios. Não executar nem mandar mensagem ao upstream nesta auditoria.

### Comunicação entre responsáveis

Na consolidação local, nomear repositório e PR para não confundir os números com APEX; nenhum comentário externo autorizado por esta ficha.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Tratar a PR #1 ou a #2 do Dataship como bloqueio geral da v1 criaria um caminho crítico sem prova; falta nomear qual consumidor APEX precisa concretamente dessa PR externa. Que caso o teste ainda não cobre? — Os 1426 da PR #2 são changed_files, que inclui arquivos modificados, não necessariamente novos; os diffs não foram revisados integralmente. Como eu explicaria isso para outro pod? — A decisão de merge do laboratório pertence a outra linha de trabalho, e no APEX só um consumidor concreto pode tornar essa aresta dependência.

### Próxima ação e encerramento

Próxima ação proposta, mantenedor do laboratório externo: manter a trilha externa identificada e a dependência condicionada a consumidor concreto. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-156"></a>

## DEC-21 — Merge da workspace PR #4 e valores MinIO

Frente: decisoes_produto_e_custodia. Encaminhamento: relato_externo_com_limite_de_acesso.

### Identidade e estado

DEC-21 — Merge da workspace PR #4 e valores MinIO. Papel proposto: dono do workspace externo; não é atribuição nova. Estado desta ficha: relato_externo_com_limite_de_acesso; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Preservar o contexto do workspace/Oráculo sem fabricar estado público ou configuração operacional.

### Feito, faltante e não comprovado

O registro declara integração da workspace PR#4 e decisões MinIO. A revisão anterior recebeu 404 publicamente; 404 não prova sozinho repositório privado, removido ou inexistente. Esta ficha não consultou o conteúdo interno nem validou valores MinIO.

### Linhagem

P09/W01/W05 e registro histórico → workspace PR#4 relatada → acesso/conteúdo não verificados neste recorte → eventual revalidação local pelo dono.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 534. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Configuração do workspace → captura Oráculo/MinIO proposta → evidência com identidade e acesso próprios; não é fluxo de produto APEX automaticamente.

### Consequências e risco

Copiar valores locais sem verificar escopo pode usar credenciais/ambiente errados. Ausência de acesso público não sustenta conclusão funcional nem incidente.

### Alternativas e recomendação

Manter trilha externa com limites; obter leitura autorizada quando houver decisão concreta; não reproduzir configuração nem bloquear toda a v1 por falta de acesso.

### Dependências e paralelismo

Acesso é necessário para concluir a revisão técnica externa, não para continuar a revisão do APEX público. Nenhum gate geral do produto demonstrado.

### Plano e aceite propostos

Identificar artefato e dono do workspace antes de eventual consulta. Se dados dessa trilha forem usados, exigir recibo do recorte relevante sem expor segredos.

### Comunicação entre responsáveis

Registrar somente estado relatado e limite de acesso; não anunciar private como fato deduzido de 404.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Concluir que o workspace é privado a partir de um 404 ignoraria outras hipóteses, como remoção ou inexistência, e copiar valores MinIO sem escopo poderia usar ambiente ou credencial errados. Que caso o teste ainda não cobre? — O conteúdo da PR #4 foi depois conferido no clone local em P09/W01. O 404 anônimo não informa o estado remoto interno. Origem e ambiente de dados do Oráculo exigem o recibo próprio do resultado a reutilizar. Como eu explicaria isso para outro pod? — A integração documentada no clone e o acesso remoto atual são provas diferentes. Preservar o resultado local e suas limitações; a revisão do APEX público pode avançar.

### Próxima ação e encerramento

Próxima ação proposta, dono do workspace externo: manter o contexto externo delimitado até haver necessidade e fonte acessível. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-157"></a>

## DEC-22 — F4.3 como leg própria do Serve

Frente: decisoes_produto_e_custodia. Encaminhamento: decisao_pendente_sem_autorizacao.

### Identidade e estado

DEC-22 — F4.3 como leg própria do Serve. Papel proposto: responsável por Serve e mantenedor; não é atribuição nova. Estado desta ficha: decisao_pendente_sem_autorizacao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Decidir se narrar AQE junto da configuração capturada produz benefício sem afirmar causalidade não observada.

### Feito, faltante e não comprovado

#177 pede estudo e exemplos; Serve já possui JOB_CONF_SQL/job_conf e notas AQE. Isso não prova cruzamento narrativo completo. A issue exige configuração conhecida, chave ausente e captura indisponível, além de ownership explícito.

### Linhagem

S15/F4.3 → fontes Serve existentes → #177 → exemplos e limites → decisão implementar/adiar/rejeitar.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 552. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Transição AQE observada + configuração capturada no escopo certo → texto que distingue observação e hipótese → usuário.

### Consequências e risco

Inferir causa por correlação ou usar default como configuração capturada aumenta confiança sem base. Zero comentário não prova ausência de estudo fora da issue.

### Alternativas e recomendação

Texto determinístico delimitado, outra superfície de explicação, adiamento com gatilho ou rejeição fundamentada. A escolha pós-v1 não é obrigatória.

### Dependências e paralelismo

Exemplos e estudo não precisam esperar fechamento #115. Integração que una stage/execução deve respeitar a atribuição disponível e declarar unknown onde faltar.

### Plano e aceite propostos

Criar exemplos dos três estados e critérios de utilidade. Se aprovado, planejar controles contra configuração inventada, escopo errado e causalidade automática; runtime posterior é prova própria.

### Comunicação entre responsáveis

Na #177, registrar decisão e exemplos com limites; não dizer que job_conf falta no Serve.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Afirmar que a configuração observada causou a decisão AQE, ou usar um default como configuração capturada, aumentaria a confiança sem base. Que caso o teste ainda não cobre? — Conferir a redação para chave ausente e captura indisponível. JOB_CONF_SQL e notas AQE existem, mas o cruzamento narrativo não foi provado nesta ficha. Como eu explicaria isso para outro pod? — A narração explica o que foi visto e configurado, sem fabricar causa; implementar como leg própria do Serve, adiar ou rejeitar é decisão de utilidade, sem obrigação de pós-v1.

### Próxima ação e encerramento

Próxima ação proposta, responsável por Serve e mantenedor: propor exemplos e uma decisão de utilidade delimitada. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-158"></a>

## DEC-23 — Convenção de tentativa nas leituras do Serve: `ts` × `(stage_attempt, ts)` (delta 2026-09-29)

Frente: decisoes_produto_e_custodia. Encaminhamento: decisao_pendente_sem_autorizacao.

### Identidade e estado

DEC-23 — Convenção de tentativa nas leituras do Serve: `ts` × `(stage_attempt, ts)` (delta 2026-09-29). Papel proposto: responsáveis Engine/Serve/Front/Memory e mantenedor; não é atribuição nova. Estado desta ficha: decisao_pendente_sem_autorizacao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Escolher seleção/desempate coerentes de tentativas e observações por consumidor.

### Feito, faltante e não comprovado

#169 descreve divergência entre seleção offline por (stage_attempt, ts), max(stage_attempt) combinado com argMax por ts e outras projeções. Isso pode misturar rótulo/métrica; ocorrência em dados reais não foi medida. Identidade de tentativa e identidade de execução SQL são problemas distintos.

### Linhagem

E24/S14/S19 → mapeamento de queries → #169 → fixtures discriminantes → política antes da mudança SQL.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 570. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Eventos de várias tentativas → chave/seletor/desempate → conjunto coerente de rótulo e métricas → diagnóstico.

### Consequências e risco

Escolher maior tentativa não equivale necessariamente a escolher evento mais recente. Empates e campos agregados separadamente podem produzir uma linha sem observação correspondente.

### Alternativas e recomendação

Maior tentativa, recência ou tentativa bem-sucedida conforme contrato, com desempate explícito. Nenhuma opção é ratificada apenas pelo parecer; requisitos de histórico precisam acompanhar a escolha.

### Dependências e paralelismo

Preparação da matriz e fixtures é paralela à decisão. Correção de SQL/compatibilidade espera política pertinente; #115 não deve ser confundida com seleção de tentativas.

### Plano e aceite propostos

Matriz por consumidor com casos fora de ordem, empate e múltiplas tentativas; definir resultado esperado e testes de paridade. Só após escolha implementar folhas; runtime sintético não prova Spark real.

### Comunicação entre responsáveis

Na #169, compartilhar caso/resultado/seletor e critério de fallback, não apenas nome de operador SQL.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Escolher maior tentativa não equivale a escolher o evento mais recente, então a métrica selecionada pode não pertencer à tentativa exibida. Que caso o teste ainda não cobre? — Conferir política e controles para timestamps empatados, observações conflitantes e eventos fora de ordem. Há caracterização histórica relacionada à #169; sua presença não ratifica uma regra nem comprova ocorrência em dados reais. Como eu explicaria isso para outro pod? — Engine, Serve, Front e Memory precisam referir-se à mesma observação, não apenas ao mesmo job; seleção de tentativa é problema distinto da identidade de execução SQL da #115.

### Próxima ação e encerramento

Próxima ação proposta, responsáveis Engine/Serve/Front/Memory e mantenedor: completar matriz de seletores e submeter política específica. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-159"></a>

## DEC-24 — Rótulo de população e migração de `run_outcomes` na Memory (delta 2026-09-29)

Frente: decisoes_produto_e_custodia. Encaminhamento: decisao_pendente_sem_autorizacao.

### Identidade e estado

DEC-24 — Rótulo de população e migração de `run_outcomes` na Memory (delta 2026-09-29). Papel proposto: owner Memory a confirmar e mantenedor; não é atribuição nova. Estado desta ficha: decisao_pendente_sem_autorizacao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Definir população de métricas e tratamento do histórico sem inventar amostras successful-task retroativamente.

### Feito, faltante e não comprovado

#169 agrega seleção de tentativa e população. O registro DEC-24 focaliza run_outcomes/Memory; ter uma issue comum não elimina essa pergunta própria. Queries Memory do corte usam reduções e percentis legados; não foi demonstrado recall incorreto em dados reais.

### Linhagem

S14/Memory → diferença de população → #169/DEC24 → owner DEC-06 e política de legado → migração somente se necessária.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 588. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Observação/população → persistência histórica → seleção/recall Memory → interpretação com metadados de população conhecidos ou desconhecidos.

### Consequências e risco

Migrar sem origem pode fabricar successful-task; manter legado sem rótulo pode induzir comparação de populações diferentes. Não há incidente quantificado nesta revisão.

### Alternativas e recomendação

Rotular legado, manter leitura compatível com ausência explícita, migrar dados reconstruíveis ou conservar comportamento com limite documentado. Escolha depende da fonte disponível e objetivo do consumidor.

### Dependências e paralelismo

Estudo/matriz pode avançar antes da atribuição final do owner; mudança de dados/contrato exige responsável e política. Não impor migração para toda opção.

### Plano e aceite propostos

Identificar produtor e leitor de run_outcomes, rotular população e ausência; planejar controles de linha legada e comparação cruzada. Se migrar, definir rollback e fonte reconstruível; nenhuma migração executada.

### Comunicação entre responsáveis

Registrar na #169 a política de histórico e sua relação com o seletor de tentativa, sem colapsar duas decisões numa só.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Migrar run_outcomes sem fonte reconstruível fabricaria amostras successful-task que nunca foram armazenadas. Que caso o teste ainda não cobre? — Linha antiga sem metadado de população ainda não tem tratamento definido entre ficar unknown ou ser reinterpretada; não foi demonstrado recall incorreto em dados reais. Como eu explicaria isso para outro pod? — A Memory precisa dizer de qual população lembra; rotular o legado, manter leitura com ausência explícita ou migrar só o reconstruível são as opções, e essa decisão é distinta da seleção de tentativa na mesma #169.

### Próxima ação e encerramento

Próxima ação proposta, owner Memory a confirmar e mantenedor: formular tratamento de legado e identificar owner da mudança. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-160"></a>

## DEC-25 — Reaplicação de DDL durante ingestão e escopo do `verify_ddl.py` (delta 2026-09-30)

Frente: decisoes_produto_e_custodia. Encaminhamento: decisao_pendente_sem_autorizacao.

### Identidade e estado

DEC-25 — Reaplicação de DDL durante ingestão e escopo do `verify_ddl.py` (delta 2026-09-30). Papel proposto: responsável por Infra/ingestão e mantenedor; não é atribuição nova. Estado desta ficha: decisao_pendente_sem_autorizacao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Escolher política de reaplicação/migração e declarar exatamente o que o verificador de DDL observa.

### Feito, faltante e não comprovado

#170 e o código separam aplicação SQL de comparação de schema. O verificador examinado compara nomes/tipos, não toda semântica de DEFAULT/TTL/SETTINGS/MVs. O registro relata ensaios sintéticos de janelas durante migração; eles não demonstram ingestão concorrente real ou incidente produtivo.

### Linhagem

E22/E23 + ensaios relatados → #170 → decisão de suporte à ingestão ativa e alcance do verificador → eventual implementação/prova.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 606. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

DDL e ordem de aplicação → schema/MV intermediários → eventos aceitos nesse estado → verificação delimitada → dados finais e possibilidade de reparo.

### Consequências e risco

Verde restrito pode ser lido como migração completa. Ausência de pausa ou reparo definido cria risco de dados transitórios; ocorrência real ainda não foi medida.

### Alternativas e recomendação

Exigir quietude para certas operações; suportar concorrência com mecanismo de transição/reparo comprovado; manter verificador restrito com nome/contrato claros ou ampliá-lo por propriedades escolhidas. Não impor toda expansão sem critério.

### Dependências e paralelismo

Classificação SQL e desenho #109/#114 podem avançar em paralelo. Runtime e mudanças de migração precisam de política/ambiente; #170 não é gate universal para estudos.

### Plano e aceite propostos

Mapear SQLs/propriedades observadas; escolher política e controles de interrupção/reaplicação/linha legada. Prova sintética e Spark real têm fronteiras distintas. Não executar DDL nesta auditoria.

### Comunicação entre responsáveis

Na #170, registrar o que verde inclui/exclui e quando pausar ingestão; publicar resultado futuro com ambiente e fonte dos dados.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Ler um verde de verify_ddl.py como migração completa seria engano, porque a comparação de nomes e tipos não detecta alteração de MV, DEFAULT, TTL nem SETTINGS. Que caso o teste ainda não cobre? — Eventos recebidos entre duas migrações não têm tratamento definido; os ensaios sintéticos relatados não demonstram ingestão concorrente real. Como eu explicaria isso para outro pod? — Schema coerente e migração de dados segura são provas diferentes; a decisão é exigir quietude para certas operações ou suportar concorrência com reparo comprovado, e declarar o que o verificador observa.

### Próxima ação e encerramento

Próxima ação proposta, responsável por Infra/ingestão e mantenedor: propor política de reaplicação e contrato observável do verificador. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

