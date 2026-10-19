# Fichas documentais — lote 14

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-131"></a>

## DEC-02 — Política de proteção da `main` e de dependências

Frente: governanca_e_integracao. Encaminhamento: decisao_pendente_sem_autorizacao.

### Identidade e estado

DEC-02 — Política de proteção da `main` e de dependências. Papel proposto: administrador do repositório e mantenedor; não é atribuição nova. Estado desta ficha: decisao_pendente_sem_autorizacao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Escolher regras de integração proporcionais ao risco e compatíveis com os workflows reais, incluindo revisão, checks e exceções auditáveis.

### Feito, faltante e não comprovado

A captura da branch informa protected=false; todos os rulesets aplicáveis não foram inspecionados. CI possui três jobs gerais e filtros de docs/Markdown/jar; jar tem workflow próprio com paths. Uma configuração de checks obrigatórios pode exigir resultado que esses filtros impedem de surgir. Política de dependências E15 é uma decisão associada, não conteúdo implementado pela #125.

### Linhagem

G02/E15 → #125 → inventário de regras efetivas ainda necessário → política aprovada → eventual configuração e demonstração de bloqueio/merge.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 66. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

PR e paths → workflows elegíveis → status exigidos e revisão → merge ou bloqueio; bypass precisa de responsável, motivo e registro de restauração da regra.

### Consequências e risco

Exigir check ausente por filtro trava a fila; deixar bypass irrestrito enfraquece a política. O metadado da branch não permite afirmar ausência universal de regras.

### Alternativas e recomendação

Comparar workflow geral sempre disparado com jobs condicionais e resultado agregador; checks por fronteira suportados pela configuração efetiva; ou revisão inicial e expansão posterior. Não apresentar ruleset condicional por caminho como recurso já confirmado. CODEOWNERS e dependências são escolhas separadas.

### Dependências e paralelismo

Desenhar política não espera DEC-01. Habilitar checks depende de resultado coerente para todos os tipos de alteração. A revisão da #161 pode influenciar como um agregador detecta falhas anteriores.

### Plano e aceite propostos

Inspecionar regras efetivas → registrar check/trigger/estado esperado → escolher política → configurar somente com autorização → demonstrar PR vermelha bloqueada, verde permitida e docs/jar tratados como previsto. Não criar testes de PR nesta auditoria.

### Comunicação entre responsáveis

Na #125, propor tabela de contextos exatos, execução por path e regra de emergência. Evidência de configuração não deve ser vendida como prova de runtime.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Exigir um check que o filtro de paths nunca cria, como em PRs só de docs ou só de jar, travaria a fila; deixar o bypass irrestrito enfraqueceria a política. Que caso o teste ainda não cobre? — Docs-only, jar-only e dependência que falha antes do root gate ainda precisam de linha na tabela trigger → check → estado esperado; todos os rulesets aplicáveis não foram inspecionados. Como eu explicaria isso para outro pod? — A regra só pode exigir resultados que o fluxo realmente produz; protected=false não prova ausência de outras regras, e CODEOWNERS e dependências são escolhas separadas.

### Próxima ação e encerramento

Próxima ação proposta, administrador do repositório e mantenedor: elaborar a tabela da política e identificar a configuração efetiva ainda não lida. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-132"></a>

## DEC-03 — Merge e ordem da fila #126–#134

Frente: governanca_e_integracao. Encaminhamento: historico_superado_preservado.

### Identidade e estado

DEC-03 — Merge e ordem da fila #126–#134. Papel proposto: mantenedor; não é atribuição nova. Estado desta ficha: historico_superado_preservado; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Preservar a decisão histórica da fila de setembro sem reapresentá-la como integração ainda pendente.

### Feito, faltante e não comprovado

No snapshot de pulls, #126–129 e #131–134 têm merged_at em 06/10. #130 é issue, não PR da fila. A decisão de ordenar esses merges perdeu seu objeto; isso não encerra as issues de critérios funcionais.

### Linhagem

Registro DEC-03/G03 → PRs históricas → merges observados em 06/10 → método da fila aberta tratado em DEC-N4.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 102. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Proposta de ordem → merges efetivos → registro histórico → aprendizado para a próxima fila, preservando as identidades das PRs.

### Consequências e risco

Reabrir a ordem antiga duplicaria trabalho; usar merge como prova de runtime apagaria critérios ainda abertos em #115/#123/#124.

### Alternativas e recomendação

Marcar a decisão como superada no derivado datado e manter a fonte intacta. Análise da ordem real é útil se responder a risco concreto; não é requisito para refazer merges já ocorridos.

### Dependências e paralelismo

Nenhuma integração nova depende desta decisão. DEC-N4 trata outra fila; as dependências técnicas atuais devem ser lidas nas árvores atuais.

### Plano e aceite propostos

Conferir números/timestamps na API e relacionar a decisão ao histórico. Controle de consistência: #130 permanece issue e nenhum merge é contado como aceite funcional.

### Comunicação entre responsáveis

Nota local de supersessão com data e links; nenhum comentário externo é necessário para preservar o fato histórico.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Tentar reordenar commits já integrados não traz ganho: #126–#129 e #131–#134 têm merged_at em 06/10, e a decisão de ordem perdeu o objeto. Que caso o teste ainda não cobre? — O snapshot distingue a issue #130 dos pulls do intervalo, então ela não conta como PR da fila; nenhum merge desses vale como aceite funcional. Como eu explicaria isso para outro pod? — A decisão antiga acabou, mas as obrigações de #115, #123 e #124 continuam; a ordem da fila aberta atual é tratada em DEC-N4.

### Próxima ação e encerramento

Próxima ação proposta, mantenedor: manter a decisão superada na visão derivada. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-133"></a>

## NOV-01 — Migração de `ubuntu-latest` para Ubuntu 26 entre 2026-10-19 e 2026-11-19; o manifesto da imagem lista PowerShell 7.6.6 (AC-07)

Frente: governanca_e_integracao. Encaminhamento: achado_documental_com_decisao_pendente.

### Identidade e estado

NOV-01 — Migração de `ubuntu-latest` para Ubuntu 26 entre 2026-10-19 e 2026-11-19; o manifesto da imagem lista PowerShell 7.6.6 (AC-07). Papel proposto: mantenedor de CI; não é atribuição nova. Estado desta ficha: achado_documental_com_decisao_pendente; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Preparar a transição de imagem de runner com evidência da ferramenta usada, evitando pin ou instalação sem necessidade demonstrada.

### Feito, faltante e não comprovado

As fontes oficiais capturadas em 17/10 anunciam rollout de 19/10 a 19/11 e imagem 20261012.163.1 com PowerShell 7.6.6. O ci.yml usa ubuntu-latest nos três jobs, setup-node 22, setup-uv, pwsh e Docker/Collector. Execução APEX nessa imagem não foi identificada neste recorte. Manifesto não prova daemon, downloads ou comportamento do workflow.

### Linhagem

Aviso de runner → fontes oficiais datadas → NOV-01 descreve risco → DEC-N1 escolhe acompanhamento ou recuo. O calendário do fornecedor não é uma data de entrega APEX.

### Fontes e corte

Origem preservada: C06B-CANDIDATOS-E-ACHADOS.md, linha 9. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Label ubuntu-latest → imagem efetivamente atribuída ao job → ferramentas instaladas/configuradas → steps do APEX → resultado e metadados do runner.

### Consequências e risco

Sem registrar imagem, uma falha pode ser atribuída incorretamente ao produto. Pinar uma imagem suportada não implica automaticamente atraso de correções de segurança; os ciclos precisam ser avaliados.

### Alternativas e recomendação

Acompanhar latest com verificação da imagem; usar pin temporário justificado se houver incompatibilidade; instalar dependência explicitamente se ausente. Recomendação: preparar diagnóstico e recuo antes de escolher mudança.

### Dependências e paralelismo

Leitura do manifesto e preparação da matriz não esperam billing nem #124. A prova hospedada depende da capacidade e disponibilidade da imagem; não bloqueia todas as PRs.

### Plano e aceite propostos

Relacionar cada ferramenta ao setup explícito ou à imagem. Na próxima execução pertinente autorizada, registrar ImageVersion/OS, versões e resultado. Controle: não chamar run em outra imagem de prova da migração.

### Comunicação entre responsáveis

Nota proposta ao mantenedor com referência ao manifesto datado e à imagem de cada run; sem avisar que pwsh está ausente quando a fonte o lista.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Fixar a imagem sem risco concreto atrasaria a migração por precaução não demonstrada, e sem registrar a imagem de cada run uma falha pode ser atribuída ao produto. Que caso o teste ainda não cobre? — Nenhuma execução do APEX na imagem nova foi identificada neste recorte; o manifesto lista PowerShell 7.6.6, mas não prova daemon, downloads nem o comportamento do workflow. Como eu explicaria isso para outro pod? — O manifesto da imagem 20261012.163.1 prevê o ambiente; o run mostra o ambiente realmente usado, e o calendário do fornecedor de 19/10 a 19/11 não é data de entrega do APEX.

### Próxima ação e encerramento

Próxima ação proposta, mantenedor de CI: preparar a matriz de ferramentas e registrar o critério de acompanhamento ou recuo. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-134"></a>

## DEC-N1 — Runner do CI frente à migração Ubuntu 26

Frente: governanca_e_integracao. Encaminhamento: decisao_pendente_sem_autorizacao.

### Identidade e estado

DEC-N1 — Runner do CI frente à migração Ubuntu 26. Papel proposto: mantenedor de CI; não é atribuição nova. Estado desta ficha: decisao_pendente_sem_autorizacao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Preparar a transição de imagem de runner com evidência da ferramenta usada, evitando pin ou instalação sem necessidade demonstrada.

### Feito, faltante e não comprovado

As fontes oficiais capturadas em 17/10 anunciam rollout de 19/10 a 19/11 e imagem 20261012.163.1 com PowerShell 7.6.6. O ci.yml usa ubuntu-latest nos três jobs, setup-node 22, setup-uv, pwsh e Docker/Collector. Execução APEX nessa imagem não foi identificada neste recorte. Manifesto não prova daemon, downloads ou comportamento do workflow.

### Linhagem

Aviso de runner → fontes oficiais datadas → NOV-01 descreve risco → DEC-N1 escolhe acompanhamento ou recuo. O calendário do fornecedor não é uma data de entrega APEX.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 84. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Label ubuntu-latest → imagem efetivamente atribuída ao job → ferramentas instaladas/configuradas → steps do APEX → resultado e metadados do runner.

### Consequências e risco

Sem registrar imagem, uma falha pode ser atribuída incorretamente ao produto. Pinar uma imagem suportada não implica automaticamente atraso de correções de segurança; os ciclos precisam ser avaliados.

### Alternativas e recomendação

Acompanhar latest com verificação da imagem; usar pin temporário justificado se houver incompatibilidade; instalar dependência explicitamente se ausente. Recomendação: preparar diagnóstico e recuo antes de escolher mudança.

### Dependências e paralelismo

Leitura do manifesto e preparação da matriz não esperam billing nem #124. A prova hospedada depende da capacidade e disponibilidade da imagem; não bloqueia todas as PRs.

### Plano e aceite propostos

Relacionar cada ferramenta ao setup explícito ou à imagem. Na próxima execução pertinente autorizada, registrar ImageVersion/OS, versões e resultado. Controle: não chamar run em outra imagem de prova da migração.

### Comunicação entre responsáveis

Nota proposta ao mantenedor com referência ao manifesto datado e à imagem de cada run; sem avisar que pwsh está ausente quando a fonte o lista.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Pinar a imagem ou instalar ferramentas sem incompatibilidade demonstrada seria mudança sem evidência; acompanhar latest sem registrar a imagem tornaria uma falha ambígua. Que caso o teste ainda não cobre? — Ainda não há job do APEX identificado na imagem nova; a matriz de ferramentas por setup explícito ou pela imagem está por preparar, e um run em outra imagem não prova a migração. Como eu explicaria isso para outro pod? — A decisão é acompanhar ubuntu-latest verificando ImageVersion e versões, ou usar pin temporário justificado se aparecer incompatibilidade; diagnóstico e recuo vêm antes da escolha.

### Próxima ação e encerramento

Próxima ação proposta, mantenedor de CI: preparar a matriz de ferramentas e registrar o critério de acompanhamento ou recuo. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-135"></a>

## NOV-02 — CI principal sem run verde na main pós-integração; prova hospedada parcial: `jar` agendado verde em 2026-10-12 no SHA atual (AC-06)

Frente: governanca_e_integracao. Encaminhamento: achado_confirmado_no_corte.

### Identidade e estado

NOV-02 — CI principal sem run verde na main pós-integração; prova hospedada parcial: `jar` agendado verde em 2026-10-12 no SHA atual (AC-06). Papel proposto: mantenedor de CI; não é atribuição nova. Estado desta ficha: achado_confirmado_no_corte; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Identificar a prova que falta para a árvore de integração sem apagar os resultados parciais já existentes.

### Feito, faltante e não comprovado

Para c3c3ea3, a captura por SHA retorna três runs: CI push 37831091789 failure, jar push 37831091718 failure e jar schedule 38266693976 success. Não há CI principal verde nessa consulta completa por SHA. Isso não prova que nenhum teste incorporado tenha rodado em outras árvores. A listagem histórica disponível tem 213 runs e não é garantia de retenção de todas as tentativas anteriores.

### Linhagem

Merges → árvore c3c3ea3 → consulta por SHA → prova jar parcial → ausência de verde CI principal na captura. AH-14 do Claude exagerava ao dizer nunca executado em CI hospedado.

### Fontes e corte

Origem preservada: C06B-CANDIDATOS-E-ACHADOS.md, linha 29. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Árvore exata + workflow identificado → steps/suites executados → resultado limitado àquela árvore e ao que efetivamente rodou.

### Consequências e risco

Confundir jar verde com validação de todas as lanes ou confundir failure sem steps com teste reprovado leva a aceite incorreto. Uma regressão combinada é risco, não incidente demonstrado aqui.

### Alternativas e recomendação

Escolher execução autorizada do workflow principal na árvore que será aceita; aproveitar uma execução futura pertinente com a mesma identidade; ou declarar prova apenas local. Não prometer que dispatch é barato sem medir.

### Dependências e paralelismo

Não depende de confirmar billing se o serviço já puder executar. Não substitui silenciosamente os critérios de #130. Atualização de docs e revisão das PRs seguem em paralelo.

### Plano e aceite propostos

Preparar recibo com SHA, workflow, imagem, tentativa, jobs e cobertura; interpretar failures pelos steps/logs. Controle: jar-only ou jobs vazios não devem satisfazer aceite da suíte principal.

### Comunicação entre responsáveis

Redação proposta: CI principal sem verde observado na árvore c3c3ea3; jar possui verde parcial. Preservar a data da consulta.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Se só o jar passar, as lanes Python, o root gate e o front do CI principal ficam sem cobertura; confundir failure sem steps com teste reprovado levaria a aceite ou correção indevidos. Que caso o teste ainda não cobre? — A consulta por SHA de c3c3ea3 retorna CI push em failure, jar push em failure e jar schedule verde; um recibo de ancestral não prova a árvore escolhida. Como eu explicaria isso para outro pod? — Na árvore c3c3ea3 não há CI principal verde observado, e o jar tem verde parcial; o resultado vale para o código e os passos que executaram, e não prova que nenhum teste rodou em outras árvores.

### Próxima ação e encerramento

Próxima ação proposta, mantenedor de CI: selecionar o objeto da próxima prova de integração e seus critérios. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-136"></a>

## NOV-03 — Fila aberta #155, #157–#159, #161–#164 sem review formal registrada; 3 heads com CI só do workflow anterior a #160 (AC-12)

Frente: governanca_e_integracao. Encaminhamento: achado_confirmado_no_corte.

### Identidade e estado

NOV-03 — Fila aberta #155, #157–#159, #161–#164 sem review formal registrada; 3 heads com CI só do workflow anterior a #160 (AC-12). Papel proposto: mantenedor e revisores das PRs; não é atribuição nova. Estado desta ficha: achado_confirmado_no_corte; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Transformar a fila aberta em decisões por PR, preservando revisões registradas, prova útil e limites de cada head.

### Feito, faltante e não comprovado

Nas oito PRs da captura, as APIs de reviews retornam zero registros. #157–159 têm 11 checks verdes do workflow anterior; #161/#162 têm três checks verdes do workflow enxuto; #155 tem 11 failures sem steps; #163/#164 não têm checks. #163 usa base #157 e #164 altera Markdown coberto por filtros. Ausência formal não implica ausência de leitura humana.

### Linhagem

Heads/bases das oito PRs → diff e checks por SHA → revisão de mérito → escolha do método em DEC-N4 → decisão de integração.

### Fontes e corte

Origem preservada: C06B-CANDIDATOS-E-ACHADOS.md, linha 54. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Prova existente identificada → lacuna específica → revisão → prova adicional apenas quando a mudança/critério exigir → decisão do mantenedor.

### Consequências e risco

Repetir testes indiscriminadamente consome capacidade; transferir verde de outra árvore ignora mudança de integração. Check antigo no mesmo head não é, por si, transferência entre heads.

### Alternativas e recomendação

Revisar por escopo e dependência; agrupar quando houver ganho concreto; validar uma pilha combinada quando apropriado. Não é necessário esperar a política geral #125 para começar as revisões.

### Dependências e paralelismo

#163 utiliza helpers de #157. #155/#161/#162 e docs podem ser revistos em paralelo. #159 tem limpeza/ambiente próprios. DEC-N3 decide alcance documental de #164, não gate global.

### Plano e aceite propostos

Para cada PR: identificar diff, base/head e checks; explicar o que o recibo cobre; completar review e selecionar prova adicional proporcional. Se a árvore mudar, avaliar o delta e a prova aplicável.

### Comunicação entre responsáveis

Um parecer por PR com o resultado e resíduo concreto; não usar “nenhuma revisão humana” quando só foram consultados registros formais.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Refazer prova do mesmo head sem lacuna concreta consome capacidade, e transferir o verde de outra árvore ignoraria mudanças da integração. Que caso o teste ainda não cobre? — Uma mudança de base pode alterar o que o workflow executa: #157–#159 têm 11 checks do workflow anterior à #160, #161 e #162 têm três do enxuto, #155 tem 11 failures sem steps e #163 e #164 não têm checks. Como eu explicaria isso para outro pod? — O verde antigo continua válido como histórico do mesmo head; a decisão de integração precisa do escopo certo, e zero reviews formais não significa ausência de leitura humana.

### Próxima ação e encerramento

Próxima ação proposta, mantenedor e revisores das PRs: produzir revisão por PR usando as oito fichas já consolidadas. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-137"></a>

## DEC-N4 — Método e ordem de integração da fila #155–#164

Frente: governanca_e_integracao. Encaminhamento: decisao_pendente_sem_autorizacao.

### Identidade e estado

DEC-N4 — Método e ordem de integração da fila #155–#164. Papel proposto: mantenedor; não é atribuição nova. Estado desta ficha: decisao_pendente_sem_autorizacao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Escolher método de integração por entrega, preservando dependências técnicas e a identidade das árvores provadas.

### Feito, faltante e não comprovado

A fila observada tem oito PRs e estados distintos descritos em NOV-03. A pilha #157→#163 tem dependência de código; #161/#162 já têm checks do CI enxuto. A documentação GitHub confirma que rerun reutiliza SHA/ref do evento original, não uma árvore atual automaticamente.

### Linhagem

NOV-03 + diferenças das PRs → dependências de código e prova → método escolhido por PR/pilha → integração autorizada. As ondas do parecer v2 eram proposta, não regra vigente.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 120. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Escolher árvore candidata → revisar delta contra base → evento compatível com os filtros → capturar SHA/ref reais → validar → decidir merge.

### Consequências e risco

Fechar/reabrir ou commit vazio sem inspecionar run não garante workflow/árvore esperados e produz ruído. Serializar toda a fila por billing ou #159 não tem dependência de código demonstrada.

### Alternativas e recomendação

Integrar #157 antes e reposicionar #163; ou validar a pilha combinada. Para outros itens, manter prova existente pertinente ou atualizar a base quando necessário. Evento novo é mecanismo a conferir, não garantia autossuficiente.

### Dependências e paralelismo

Código: helpers #157 para #163. Revisão de #159 considera limpeza; docs têm filtros. Capacidade e política influenciam a agenda, sem converter tudo em predecessores técnicos.

### Plano e aceite propostos

Registrar árvore/base, método e revisão por PR. Caso se altere base/head, comparar delta e selecionar checks. Controle negativo: resultado de ref antiga não pode ser etiquetado como árvore nova. Nenhum evento disparado aqui.

### Comunicação entre responsáveis

Plano ao mantenedor com ordem mínima e evidência existente; quando executado, anexar identidades reais dos runs e a decisão de review.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Adiar uma PR independente até toda a fila terminar não tem dependência de código demonstrada; só a #163 depende dos helpers da #157. Que caso o teste ainda não cobre? — Um rerun reutiliza o SHA e a ref do evento original, então resultado de ref antiga não pode ser etiquetado como árvore nova; falta registrar se cada teste foi feito no head ou na árvore sintética de merge. Como eu explicaria isso para outro pod? — A dependência de helpers exige compatibilidade entre #157 e #163, mas a forma de integrar a pilha é escolha: integrar a #157 e reposicionar a #163, ou validar a pilha combinada.

### Próxima ação e encerramento

Próxima ação proposta, mantenedor: registrar método por PR e pela pilha #157/#163, sem iniciar eventos. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-138"></a>

## NOV-04 — Falta uma visão atual datada: o registro CSV é histórico; o MATRIX.csv não carrega o estado reconciliado, que está em MATRIX.json (AC-04)

Frente: governanca_e_integracao. Encaminhamento: achado_corrigido_derivado_em_andamento.

### Identidade e estado

NOV-04 — Falta uma visão atual datada: o registro CSV é histórico; o MATRIX.csv não carrega o estado reconciliado, que está em MATRIX.json (AC-04). Papel proposto: custodiante e responsável pelo inventário; não é atribuição nova. Estado desta ficha: achado_corrigido_derivado_em_andamento; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Oferecer uma visão datada que preserve tanto a história quanto representações e pendências posteriores.

### Feito, faltante e não comprovado

MATRIX.json já continha public_representations e merged_at para P01/#126, G07/#148, F12/#136 e S20/#140. O CSV canônico é histórico e MATRIX.csv não carrega toda a reconciliação. A Parte04 já fornece inventário 525 e registro 158 derivados; o resíduo é completar a revisão semântica e decidir distribuição, não começar outra visão do zero.

### Linhagem

Registro histórico → MATRIX.json reconciliado → PUBLICATION.json → snapshots públicos → inventário derivado e status por ID, preservando a origem.

### Fontes e corte

Origem preservada: C06B-CANDIDATOS-E-ACHADOS.md, linha 79. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Leitor do registro → data e fonte histórica → representação posterior tipada → ficha revista ou pendência explícita → decisão por entrega.

### Consequências e risco

Sobrescrever custódia perde a história; chamar esta Parte04 de revisão completa antes de concluir os IDs mascara pendências. existing_pr não significa PR aberta.

### Alternativas e recomendação

Manter derivado datado e apontar para ele; ampliar exportação tabular com campos tipados; ou consumir diretamente JSON. Recomendo concluir o derivado existente e conservar os originais.

### Dependências e paralelismo

Completar relações e revisão por ID é trabalho local autorizado. Publicar externamente, se desejado, exige destino e instrução próprios; não atribuir automaticamente essa tarefa ao usuário.

### Plano e aceite propostos

Validar 525 IDs, igualdade dos 158 registros, links e status. Acrescentar só revisões concluídas. Controle: uma publicação não deve mudar a relação para implementado sem fonte de implementação.

### Comunicação entre responsáveis

Explicar em texto curto onde estão história, reconciliação e pendências, com data e SHA. Não repetir o erro da v1 como achado atual.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Trocar o registro histórico pela visão atual perderia a origem dos IDs, e sobrescrever a custódia apagaria a história; existing_pr não significa PR aberta. Que caso o teste ainda não cobre? — A exportação tabular ainda não preserva relações tipadas e revisões pendentes: MATRIX.csv não carrega a reconciliação que está em MATRIX.json. Como eu explicaria isso para outro pod? — A visão atual deriva das fontes sem reescrevê-las: inventário de 525 IDs e registro de 158 com data e SHA, e o resíduo é concluir a revisão semântica, não começar outra visão.

### Próxima ação e encerramento

Próxima ação proposta, custodiante e responsável pelo inventário: completar o inventário derivado existente e seu saldo semântico. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-139"></a>

## NOV-05 — Front declara `CONTRACT_VERSION = "0.5"` enquanto `CONTRACT.md` declara v0.6

Frente: governanca_e_integracao. Encaminhamento: divergencia_documental_sem_incidente_provado.

### Identidade e estado

NOV-05 — Front declara `CONTRACT_VERSION = "0.5"` enquanto `CONTRACT.md` declara v0.6. Papel proposto: responsável pelo contrato do Front; não é atribuição nova. Estado desta ficha: divergencia_documental_sem_incidente_provado; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Explicitar o significado da versão declarada pelo consumidor sem tratá-la automaticamente como defeito de compatibilidade.

### Feito, faltante e não comprovado

types.ts mantém descrição v0.5 e CONTRACT_VERSION="0.5"; o contrato publicado é v0.6, com campos aditivos. O próprio comentário do Front diz que SparkEventRow é projeção estreita e campos aditivos são opcionais. Não foi demonstrado incidente de incompatibilidade por essa constante.

### Linhagem

Contrato publicado → tipos/projeção consumida → constante do Front → comentário #180 → decisão de semântica ainda necessária.

### Fontes e corte

Origem preservada: C06B-CANDIDATOS-E-ACHADOS.md, linha 99. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Contrato geral → subconjunto consultado → representação do Front → informação de versão para leitores/consumidores.

### Consequências e risco

Trocar só o número pode sugerir suporte completo que não existe; manter 0.5 sem explicar a semântica causa confusão documental. Consumidores externos da constante não foram inventariados.

### Alternativas e recomendação

Documentar versão da projeção, nomear separadamente versão publicada/consumida, ou alinhar a declaração após conferir consumidores. Escolher pelo uso real da constante, sem mudança numérica automática.

### Dependências e paralelismo

Decidir nomenclatura não espera #115. A adoção de novos campos de atribuição, se escolhida, tem contrato e prova próprios.

### Plano e aceite propostos

Inventariar referências da constante e tipos; definir significado; preparar alteração mínima com verificação proporcional. Controle: não declarar suporte a campo opcional não selecionado pelas queries.

### Comunicação entre responsáveis

Reconciliar a nota na #180 com o significado escolhido; evitar anunciar incompatibilidade funcional sem demonstração.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Mudar a constante CONTRACT_VERSION para 0.6 não faria o Front consumir os campos novos e poderia sugerir suporte completo que não existe. Que caso o teste ainda não cobre? — Consumidores externos que usem o valor como negociação de schema não foram inventariados, e nenhum incidente de incompatibilidade foi demonstrado. Como eu explicaria isso para outro pod? — A versão do contrato publicado e a da projeção consumida podem ter funções diferentes: o Front declara 0.5 para uma projeção estreita em que os campos aditivos da v0.6 são opcionais.

### Próxima ação e encerramento

Próxima ação proposta, responsável pelo contrato do Front: definir a semântica da declaração antes de alterar o número. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-140"></a>

## NOV-06 — Status desatualizado de Task-Specs em `tasks/`

Frente: governanca_e_integracao. Encaminhamento: achado_de_declaracoes_com_revisao_individual_pendente.

### Identidade e estado

NOV-06 — Status desatualizado de Task-Specs em `tasks/`. Papel proposto: mantenedor e autores das respectivas specs; não é atribuição nova. Estado desta ficha: achado_de_declaracoes_com_revisao_individual_pendente; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Fazer a fila de Task-Specs distinguir trabalho disponível, substituído, implementado e efetivamente aceito.

### Feito, faltante e não comprovado

A conferência de declarações cobre 87 specs e 19 planos, mas não equivale a revisão semântica desses 106 objetos. Três YAMLs têm falha de parse. Há specs com status aberto e caminhos existentes, além de referências antigas a cinco tools; isso não demonstra automaticamente entrega/aceite. Uma spec substituída já tem ficha própria; 86 seguem em revisão independente.

### Linhagem

Spec e seus B-n → eval declarado → implementação e recibo no SHA certo → aceite ou motivo de substituição → atualização rastreável de status. Plano integrado não fecha automaticamente suas folhas.

### Fontes e corte

Origem preservada: C06B-CANDIDATOS-E-ACHADOS.md, linha 119. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Intenção → comportamento verificável → observação → avaliação independente → estado documental; arquivo presente é somente um dos elos.

### Consequências e risco

Marcar done por grep ou presença de arquivo pode ocultar comportamento ausente. Executar spec antiga sem reconciliação pode repetir trabalho ou atingir superfície obsoleta.

### Alternativas e recomendação

Autor atualiza junto à entrega e revisor confere; ou responsável faz reconciliação periódica com prova por ID. Preservar histórico de supersessão, em vez de apagar specs para limpar a fila.

### Dependências e paralelismo

Definir responsabilidade pode avançar agora. Mudar estado de cada spec exige conferência própria; decisões PyPI/apex_status só bloqueiam folhas correspondentes, não toda a reconciliação.

### Plano e aceite propostos

Montar tabela spec/caminho/SHA/critério/recibo/status proposto. Parse inválido precisa reparo documental antes de reuso, sem execução nesta auditoria. Controle: tools/list e grep não devem passar por evidência de chamada/comportamento.

### Comunicação entre responsáveis

Propor regra em tasks/README ou CONTRIBUTING e atualizar cada folha com motivo e link ao aceite, sem declarar resultados nunca executados.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Mover um arquivo para done sem recibo cria falsa entrega, e executar uma spec antiga sem reconciliar pode repetir trabalho ou atingir superfície obsoleta. Que caso o teste ainda não cobre? — Vários evals medem existência de texto, como tools/list ou grep, e não o comportamento B-n; três YAMLs falham no parse, e a conferência de 87 specs e 19 planos não é revisão semântica. Como eu explicaria isso para outro pod? — A spec precisa de critério, prova e decisão, e o diretório não certifica o resultado; a regra de quem registra e quem confere o encerramento ainda está por definir.

### Próxima ação e encerramento

Próxima ação proposta, mantenedor e autores das respectivas specs: definir quem registra e quem confere o encerramento; concluir o mapa por spec. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

