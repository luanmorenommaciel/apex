# Fichas documentais — lote 9

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-081"></a>

## F09 — Consumidor Front live compatível (T15)

Frente: contratos_e_decisoes. Encaminhamento: consumo_front_dependente_do_contrato_aprovado.

### Identidade e estado

F09 — Consumidor Front live compatível (T15); ID de origem preservado. Acompanhamento [#117](fichas-02.md#item-015); owner a confirmar, sem atribuição nova. Estado nesta visão: consumo_front_dependente_do_contrato_aprovado.

### Intenção e benefício

Apresentar verificações live com estado e origem honestos, sem inferir atribuição ou medir piso a partir de amostras inexistentes.

### Feito, faltante e não comprovado

A Console já dispõe de adapter live e dados HTTP/ClickHouse. As amostras de replay individuais estão nulas no adapter lido. A futura representação de atribuição ainda precisa atravessar a fronteira aprovada; isso não torna toda a UI ausente.

### Linhagem

F03/F08 → F09/T15 no Front; #172 cobre prova nginx/browser e #156/#157–159 têm recortes próprios de integração/paridade. Não duplicar prova já delimitada nem ampliá-la a uma tela não observada.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md#reg-f09, linha 738; CSV/MATRIX/PUBLICATION preservados. Código na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874 e fontes primárias de [#117](fichas-02.md#item-015); consulta 16–17/10 explicitada nos recibos. As referências abaixo permitem conferir os trechos.

### Classe e limite da evidência

DIRETO ESTÁTICO: código/contratos descritos no campo 3. RELATO: resultados históricos atribuídos, sem reexecução. INFERÊNCIA: consequências possíveis, não incidentes. PROPOSTA/DECISÃO PENDENTE: alternativas e controles; nenhuma autorização, teste de produto ou persistência nova decorre desta revisão.

### Fluxo

Payload/linha → adapter → estado de fonte/atribuição/piso → renderização e mensagem. Ausência e erro seguem caminhos diferentes de zero e sucesso vazio.

### Consequências e risco

Converter unknown em true ou erro em lista vazia induz uma leitura falsa. Teste em processo com DOM simulado não prova nginx/imagem/browser real. Não foi observado incidente novo.

### Alternativas e recomendação

Atualizar o adapter/render mínimo após contrato ou explicitar indisponibilidade da capacidade enquanto não existe. Não manter rótulo de cálculo local se não há amostras, nem forçar rollout completo de outras lanes.

### Dependências e paralelismo

F03/F08 condicionam formato final; casos de UI podem ser preparados em paralelo. A relevância para v1 não está decidida só porque a ficha antiga dizia não bloqueia v1.

### Plano e aceite propostos

Definir estados visuais true/false/unknown, piso ausente, medido/fornecido, erro e vazio. Testar adapter/render e controles que retiram campo/alteram estado. Prova browser da rota selecionada deve referenciar imagem/ref e usar ambiente autorizado quando necessária ao critério.

### Comunicação entre responsáveis

Mostrar exemplos de mensagens e origem do dado aos outros pods. Dizer o que o browser prova versus teste de componente; reaproveitar #172 para a fronteira compartilhada.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Converter unknown em true ou erro em lista vazia induziria uma leitura falsa, e manter rótulo de cálculo local sem amostras afirmaria uma medição inexistente. Que caso o teste ainda não cobre? — Teste de componente com DOM simulado não prova nginx, imagem nem browser real; a captura visual precisa corresponder ao mesmo payload e ref, e o histórico unknown ainda não tem estado visual definido. Como eu explicaria isso para outro pod? — A Console já tem adapter live; o que muda é mostrar se o piso foi medido ou fornecido e por quem, distinguir erro de ausência e reaproveitar a #172 para a prova de browser.

### Próxima ação e encerramento

Owner Front a confirmar: revisar apresentação junto do contrato e associar prova browser pertinente. Encerrar F09 por comportamento/rota demonstrados no escopo mantido, sem declarar tela inteira fixture.

<a id="item-082"></a>

## F10 — E2E Verify→storage→Serve→Front (T16)

Frente: contratos_e_decisoes. Encaminhamento: prova_integrada_condicionada_a_rota_real.

### Identidade e estado

F10 — E2E Verify→storage→Serve→Front (T16); ID de origem preservado. Acompanhamento [#117](fichas-02.md#item-015); owner a confirmar, sem atribuição nova. Estado nesta visão: prova_integrada_condicionada_a_rota_real.

### Intenção e benefício

Verificar que um resultado conserva significado desde o produtor até a leitura e a tela na rota realmente escolhida.

### Feito, faltante e não comprovado

Nenhum recibo de persistência real da rota completa foi revalidado aqui. Não foi comprovada ausência universal de escritor; fontes dizem não localizado no recorte. Fixtures podem provar contrato/offline, mas não gravação/entrega reais.

### Linhagem

F06 identifica rota; F04/F05/F08/F09 concretizam fronteiras quando aplicáveis; F10/T16 prova a combinação. API/curl ou browser isolado não são automaticamente prova produtor→storage→consumidor.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md#reg-f10, linha 770; CSV/MATRIX/PUBLICATION preservados. Código na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874 e fontes primárias de [#117](fichas-02.md#item-015); consulta 16–17/10 explicitada nos recibos. As referências abaixo permitem conferir os trechos.

### Classe e limite da evidência

DIRETO ESTÁTICO: código/contratos descritos no campo 3. RELATO: resultados históricos atribuídos, sem reexecução. INFERÊNCIA: consequências possíveis, não incidentes. PROPOSTA/DECISÃO PENDENTE: alternativas e controles; nenhuma autorização, teste de produto ou persistência nova decorre desta revisão.

### Fluxo

Resultado com identidade → serialização → escritor/storage → leitura/projeção → render → comparação com expectativa independente. Cada transição conserva referência e classe de prova.

### Consequências e risco

Chamar fixture de prova de persistência superestima integração. Esperar todas as implementações para planejar os casos atrasa descoberta de incompatibilidades. O planejamento pode antecipar a execução.

### Alternativas e recomendação

Planejar a matriz já, executar somente quando a rota existir e estiver autorizada. Se persistência for retirada do escopo, renomear a prova e revisar critérios; não chamar um teste menor pelo mesmo nome E2E completo.

### Dependências e paralelismo

Execução depende da rota e contratos efetivos; desenho de controles pode avançar em paralelo. F05 é condicional a schema. Browser/nginx #172 é parte somente quando o critério inclui essa superfície.

### Plano e aceite propostos

Positivo com linha de identidade própria; negativos false/unknown, piso não medido/igualdade e mecanismo independente; comprovar leitura do dado gravado, não fixture residual. Registrar SHA, ambiente, comandos, IDs e limpeza restrita. Aceite distingue offline, persistência real e render observado; NOT EXERCISED não vira passed.

### Comunicação entre responsáveis

Apresentar uma cadeia de recibos com que fronteira cada um cobre. Não substituir ausência de prova de um elo por um verde de outro workflow ou outro job.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Chamar fixture de prova de persistência superestimaria a integração, e esperar todas as implementações para planejar os casos atrasaria a descoberta de incompatibilidades. Que caso o teste ainda não cobre? — Nenhum recibo da rota completa foi revalidado; falta mostrar que o consumidor leu a linha criada nesta prova, e não uma fixture residual, e que a limpeza afeta só recursos da própria prova. Como eu explicaria isso para outro pod? — A prova encadeia recibos de produtor, serialização, storage, leitura e render, cada um com sua classe; o estado vem de quem produziu a linha, e NOT EXERCISED não vira passed.

### Próxima ação e encerramento

Owners da rota a confirmar: preparar plano e obter recibo delimitado quando autorizado. Encerrar apenas o escopo efetivamente exercitado ou registrar alteração explícita de requisito.

<a id="item-083"></a>

## F11 — Direção, igualdade e delta↔saving (T11)

Frente: contratos_e_decisoes. Encaminhamento: preservar_correcao_de_direcao_e_decidir_fronteiras.

### Identidade e estado

F11 — Direção, igualdade e delta↔saving (T11); ID de origem preservado. Acompanhamento [#117](fichas-02.md#item-015); owner a confirmar, sem atribuição nova. Estado nesta visão: preservar_correcao_de_direcao_e_decidir_fronteiras.

### Intenção e benefício

Separar delta medido, saving previsto, direção e magnitude resolvível, especialmente na igualdade e em zero.

### Feito, faltante e não comprovado

A mensagem de ruleTwoRuntimeResolvable já distingue saving negativo além do piso como slowdown; a acusação histórica de chamar -12/5 inside the floor está superada. SQL converte predicted_delta em -predicted_saving e mantém >; Verify usa >=. Zero/zero requer política explícita antes de mudança mecânica.

### Linhagem

F11/T11 → #136 e relato TS08 (correção de narração) → resíduos F02/#117. A entrega integrada não decidiu automaticamente todos os operadores e convenções de direção.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md#reg-f11, linha 804; CSV/MATRIX/PUBLICATION preservados. Código na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874 e fontes primárias de [#117](fichas-02.md#item-015); consulta 16–17/10 explicitada nos recibos. As referências abaixo permitem conferir os trechos.

### Classe e limite da evidência

DIRETO ESTÁTICO: código/contratos descritos no campo 3. RELATO: resultados históricos atribuídos, sem reexecução. INFERÊNCIA: consequências possíveis, não incidentes. PROPOSTA/DECISÃO PENDENTE: alternativas e controles; nenhuma autorização, teste de produto ou persistência nova decorre desta revisão.

### Fluxo

Delta/saving com convenção identificada → magnitude versus piso → resolubilidade → rótulo de direção. Uma piora resolvível não é benefício; uma mudança não resolvível não é necessariamente zero.

### Consequências e risco

Inverter sinal duas vezes pode transformar piora em ganho. Trocar apenas > por >= pode lançar zero no ramo regressed sem justificar o significado. São riscos de implementação, não incidente demonstrado.

### Alternativas e recomendação

Manter correção de mensagem existente e discutir apenas a fronteira residual. Preferir tabela normativa de sinais/igualdade a rótulos improvisados por consumidor; não refazer #136.

### Dependências e paralelismo

F02/DEC-05 definem zero/igualdade. Estudo de convenção pode ser paralelo à decisão de representação F03. Alteração do operador depende de política; texto honesto já integrado não espera nova migração.

### Plano e aceite propostos

Casos previstos ±12 com piso 5, ±3 dentro, igualdade ±5, zero/piso zero e piso ausente. Confirmar convenção delta→saving exatamente uma vez. Negativo: piora não pode receber recomendação positiva; rótulo de ruído não afirma delta zero. Preservar controles já existentes.

### Comunicação entre responsáveis

Mostrar exemplos numerados com unidade e sentido; explicar que a correção textual anterior continua válida. Não anunciar ganhos medidos por ser uma previsão resolvível.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Inverter o sinal duas vezes pode transformar piora em ganho, e trocar só > por >= pode lançar zero no ramo regressed sem justificar o significado. Que caso o teste ainda não cobre? — Conferir a cobertura integrada e a regra aprovada para fronteiras como ±12%, igualdade e zero, preservando os testes já existentes; não se afirma ausência de todos esses vetores. Como eu explicaria isso para outro pod? — A mensagem de ruleTwoRuntimeResolvable já trata saving negativo além do piso como slowdown; a SQL converte predicted_delta em -predicted_saving, e ficar dentro do piso não significa mudança zero.

### Próxima ação e encerramento

Owners Verify/Front/Serve a confirmar: ratificar as fronteiras e alterar apenas o necessário. Encerrar F11 com controles residuais e preservação da correção integrada.

<a id="item-084"></a>

## F17 — Alinhar ou remover o recálculo de CV no Front (T10)

Frente: contratos_e_decisoes. Encaminhamento: alinhar_ou_remover_recalculo_do_piso.

### Identidade e estado

F17 — Alinhar ou remover o recálculo de CV no Front (T10); ID de origem preservado. Acompanhamento [#117](fichas-02.md#item-015); owner a confirmar, sem atribuição nova. Estado nesta visão: alinhar_ou_remover_recalculo_do_piso.

### Intenção e benefício

Evitar que o mesmo conjunto de amostras produza dois pisos sob o mesmo rótulo e que o Front alegue cálculo que não pôde fazer.

### Feito, faltante e não comprovado

guardrails.runtime_cv_pct usa desvio padrão amostral/média; measureNoiseFloorPct usa (máximo−mínimo)/média, apesar do comentário half-spread. O vetor histórico [963000,1068000,1147000] é relatado como 8,7136% versus 17,3694%. Adapter live não fornece amostras; não foi demonstrada divergência exibida em produção.

### Linhagem

F17/T10 → #117 e F02/H-3 → decisão manter recálculo convergente ou remover. F07 trata retenção/amostras, não resolve sozinho a escolha da fórmula.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md#reg-f17, linha 979; CSV/MATRIX/PUBLICATION preservados. Código na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874 e fontes primárias de [#117](fichas-02.md#item-015); consulta 16–17/10 explicitada nos recibos. As referências abaixo permitem conferir os trechos.

### Classe e limite da evidência

DIRETO ESTÁTICO: código/contratos descritos no campo 3. RELATO: resultados históricos atribuídos, sem reexecução. INFERÊNCIA: consequências possíveis, não incidentes. PROPOSTA/DECISÃO PENDENTE: alternativas e controles; nenhuma autorização, teste de produto ou persistência nova decorre desta revisão.

### Fluxo

Amostras válidas do braço/unidade definidos → fórmula escolhida → piso ou indisponível → rótulo de origem. Sem amostras, usar piso fornecido apenas sob contrato explícito.

### Consequências e risco

Fórmulas distintas mudam a fronteira de resolubilidade. Chamar amplitude de CV ou half-spread altera interpretação. O vetor positivo não cobre entradas inválidas/insuficientes e não é teste runtime.

### Alternativas e recomendação

Alinhar fórmula, filtros e tolerância com a regra ratificada ou remover recálculo e corrigir rótulos. Não manter duas métricas distintas sob o mesmo nome; se ambas tiverem utilidade, nomear e justificar cada uma.

### Dependências e paralelismo

F02 define regra e F07 disponibilidade. A escolha e teste do vetor podem ser planejados offline sem writer; live medido depende de amostras reais na rota. Não impor schema apenas para corrigir uma fórmula de fixture.

### Plano e aceite propostos

Casos do vetor de referência, duas amostras, insuficientes, média inválida e valores fora do domínio conforme política. Negativo deve diferenciar amplitude de CV; se removido, nenhuma UI afirma medição local. Aceite: equivalência com tolerância ou remoção coerente em todos os chamadores abrangidos.

### Comunicação entre responsáveis

Explicar a fórmula e unidade com o mesmo vetor, dizendo que os resultados históricos são cálculo relatado. Corrigir o comentário half-spread se a fórmula for mantida com outro nome.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Manter duas métricas distintas sob o mesmo nome muda a fronteira de resolubilidade: runtime_cv_pct usa desvio padrão amostral e measureNoiseFloorPct usa amplitude sobre média, apesar do comentário half-spread. Que caso o teste ainda não cobre? — Falta um teste que detecte amplitude no lugar de desvio com o vetor [963000,1068000,1147000], relatado como 8,7136% × 17,3694%, além de entradas insuficientes e inválidas; não há divergência exibida em produção demonstrada. Como eu explicaria isso para outro pod? — O live não tem amostras, só piso armazenado; a escolha é alinhar fórmula, braço, população e filtro de válidos com a regra ratificada, ou remover o recálculo e corrigir os rótulos.

### Próxima ação e encerramento

Owners Verify/Front a confirmar: decidir manter/remover e executar folha pequena com controles próprios quando autorizada. Encerrar F17 por consistência de cálculo/rotulagem, não por mera discussão.

<a id="item-085"></a>

## DEC-05 — Escopo e representação do contrato de piso/atribuição (#117)

Frente: contratos_e_decisoes. Encaminhamento: decisao_de_contrato_sem_bloqueio_global.

### Identidade e estado

DEC-05 — Escopo e representação do contrato de piso/atribuição (#117); ID de origem preservado. Acompanhamento [#117](fichas-02.md#item-015); owner a confirmar, sem atribuição nova. Estado nesta visão: decisao_de_contrato_sem_bloqueio_global.

### Intenção e benefício

Ratificar o significado de atribuição, piso e disponibilidade entre Verify, Front e Serve, separando decisão de arquitetura e prova funcional.

### Feito, faltante e não comprovado

to_row omite atribuição; fórmulas/igualdade diferem. As fontes lidas não registram ratificação final das escolhas H-1…H-8. O fluxo anterior dizia to_row grava: a função produz uma representação, não persiste por si. Leitura Serve já existe.

### Linhagem

X02/F02/F03 → #117 → DEC-05; DEC-06 identifica rota e ownership. F04–F11/F17/S10 são frentes relacionadas, não necessariamente uma fila serial única.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/F-DECISOES-NECESSARIAS.md#dec-05, linha 192; CSV/MATRIX/PUBLICATION preservados. Código na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874 e fontes primárias de [#117](fichas-02.md#item-015); consulta 16–17/10 explicitada nos recibos. As referências abaixo permitem conferir os trechos.

### Classe e limite da evidência

DIRETO ESTÁTICO: código/contratos descritos no campo 3. RELATO: resultados históricos atribuídos, sem reexecução. INFERÊNCIA: consequências possíveis, não incidentes. PROPOSTA/DECISÃO PENDENTE: alternativas e controles; nenhuma autorização, teste de produto ou persistência nova decorre desta revisão.

### Fluxo

Medição → representação → writer ainda a identificar → storage/projeção → leitor. A decisão fixa estados/unidades e qual fronteira precisará mudar; não adiciona escritor automaticamente.

### Consequências e risco

Inventar ordem absoluta bloqueia estudos úteis. Decidir fora da v1 sem revisão explícita de critérios esconde requisitos públicos. A possibilidade de falsa certificação depende de uma rota que persista/consuma a representação problemática.

### Alternativas e recomendação

Comparar tri-estado versionado, projeção publicável separada e eventual revisão de escopo da v1. A última é escolha de produto a ser ratificada, não recomendação já aprovada. Definir CV, unidade, igualdade, direção e histórico desconhecido.

### Dependências e paralelismo

Coordenar com DEC-06; nenhuma precisa esperar a outra para levantar evidência e alternativas. Aplicação e prova real dependem da rota escolhida. #162 e M1 não bloqueiam por padrão.

### Plano e aceite propostos

Preparar tabela por decisão: evidência, alternativas, consumidores, critérios preservados e impacto de compatibilidade. Saída mínima é decisão atribuída e datada; implementação e testes seguem em folhas com controles discriminantes. Fechar DEC-05 como decisão não fecha a issue #117 funcionalmente.

### Comunicação entre responsáveis

Registrar decidido/não decidido/owner e consequências por folha. Não misturar valores brutos, disponibilidade e certificação nem chamar uma reunião de prova de integração.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Impor uma ordem absoluta entre as frentes bloquearia estudos úteis, e tirar persistência da v1 sem revisão explícita esconderia critérios públicos da #117. Que caso o teste ainda não cobre? — A falsa certificação só ocorre numa rota que persista e consuma a representação problemática, e essa rota ainda não foi identificada; as escolhas H-1 a H-8 não têm ratificação final nas fontes lidas. Como eu explicaria isso para outro pod? — DEC-05 ratifica estados e unidades: se linha histórica sem campo continua unknown, qual regra vale na igualdade e se o piso é percentual ou fração; decidir isso não fecha a #117 funcionalmente.

### Próxima ação e encerramento

Mantenedor com owners Verify/Front/Serve a confirmar: ratificar escolhas e registrar efeitos. Encerrar esta decisão quando escolhas/justificativas estiverem rastreáveis; manter provas de implementação nos destinos próprios.

<a id="item-086"></a>

## DEC-06 — Ownership de Verify e Memory e existência de escritor externo

Frente: contratos_e_decisoes. Encaminhamento: identificar_escritor_e_responsaveis_por_ambiente.

### Identidade e estado

DEC-06 — Ownership de Verify e Memory e existência de escritor externo; ID de origem preservado. Acompanhamento [#117](fichas-02.md#item-015); owner a confirmar, sem atribuição nova. Estado nesta visão: identificar_escritor_e_responsaveis_por_ambiente.

### Intenção e benefício

Definir ownership de Verify/Memory e a rota de persistência pretendida, evitando implementar consumidor ou sink sob pressuposto errado.

### Feito, faltante e não comprovado

Escritor de produção não localizado no relato histórico e não buscado exaustivamente em sistemas externos nesta revisão. Leitores existentes e matriz estática não resolvem essa pergunta. F06 foi absorvido na #117; F19/#162 corrige identidade de versão do módulo e não depende desta decisão por efeito de persistência.

### Linhagem

F06 → P-DEC06 → disposition reuse_existing #117 → DEC-06. L10/S10/S14 têm escopos próprios; referências no registro não autorizam dizer que toda implementação de M3 está tecnicamente bloqueada.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/F-DECISOES-NECESSARIAS.md#dec-06, linha 210; CSV/MATRIX/PUBLICATION preservados. Código na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874 e fontes primárias de [#117](fichas-02.md#item-015); consulta 16–17/10 explicitada nos recibos. As referências abaixo permitem conferir os trechos.

### Classe e limite da evidência

DIRETO ESTÁTICO: código/contratos descritos no campo 3. RELATO: resultados históricos atribuídos, sem reexecução. INFERÊNCIA: consequências possíveis, não incidentes. PROPOSTA/DECISÃO PENDENTE: alternativas e controles; nenhuma autorização, teste de produto ou persistência nova decorre desta revisão.

### Fluxo

Ambiente/perfil → produtor e writer identificados → storage → consumidor. Cada elo tem owner e fonte, ou ausência explicitada dentro do recorte.

### Consequências e risco

Sem fonte de dados identificada, a integração pode ser planejada para um caminho inexistente no ambiente. Mas inferir que toda tela calcula na hora ou é fixture a partir desse desconhecimento também é incorreto.

### Alternativas e recomendação

Reutilizar writer externo, criar sink delimitado ou excluir persistência de um escopo são alternativas. Adiar a decisão mantém dependentes específicos abertos; não bloqueia toda análise de contrato ou correção textual.

### Dependências e paralelismo

Não há predecessor técnico para inventariar a rota. DEC-05 pode avançar em paralelo. Execução de F10 depende da rota, e F05 de eventual schema; #162 não é dependente funcional.

### Plano e aceite propostos

Inventariar perfis e fontes de linhas, identificar responsável e verificar evidência de escrita existente antes de decidir. Controle de revisão: toda afirmação de dado live/fixture vem da rota, não de suposição. Aceite: decisão de escopo, owners a confirmar/ratificar e próximos itens delimitados.

### Comunicação entre responsáveis

Explicar o que /verify lê em cada perfil e qual evidência sustenta isso. Registrar exclusões com precisão, sem proclamar inexistência de integrações não inspecionadas.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Planejar integração sem fonte de dados identificada pode mirar um caminho inexistente no ambiente, e inferir que toda tela é fixture por desconhecer o escritor também seria incorreto. Que caso o teste ainda não cobre? — Não se sabe se há escritor externo nem qual perfil foi inspecionado: o escritor não foi localizado no relato histórico e sistemas externos não foram buscados nesta revisão. Como eu explicaria isso para outro pod? — A decisão é quem possui os dados de Verify e Memory e por qual rota eles chegam ao storage; inventariar essa rota, estudar DEC-05 e correções textuais podem seguir sem essa resposta.

### Próxima ação e encerramento

Mantenedor e owners a confirmar: registrar ambiente, rota e responsabilidade. Encerrar a decisão com fonte verificável ou limite explícito; nenhuma implementação ou autorização de runtime decorre da ficha.

<a id="item-087"></a>

## DEC-09 — Consumo da atribuição de stage (#115)

Frente: contratos_e_decisoes. Encaminhamento: selecionar_primeira_superficie_reutilizando_resolver.

### Identidade e estado

DEC-09 — Consumo da atribuição de stage (#115); ID de origem preservado. Acompanhamento [#115](fichas-02.md#item-014); owner a confirmar, sem atribuição nova. Estado nesta visão: selecionar_primeira_superficie_reutilizando_resolver.

### Intenção e benefício

Escolher onde expor primeiro a atribuição de stages e como apresentar seus estados, aproveitando o contrato offline já implementado.

### Feito, faltante e não comprovado

Resolver e controles de conflito do mesmo stage já existem. AQE usa sentinel de job e o Front sinaliza indisponibilidade; esses trechos não provam ausência universal de todo consumidor. A questão em aberto é a integração/superfície ratificada, não definir do zero a política que a função já aplica.

### Linhagem

P01/#126 → E02/#115 → DEC-09; E01 conserva a prova SQL/RDD. DEC-23/#169 pode informar seleção de tentativa, sem bloquear incondicionalmente estudos do consumidor.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/F-DECISOES-NECESSARIAS.md#dec-09, linha 264; CSV/MATRIX/PUBLICATION preservados. Código na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874 e fontes primárias de [#115](fichas-02.md#item-014); consulta 16–17/10 explicitada nos recibos. As referências abaixo permitem conferir os trechos.

### Classe e limite da evidência

DIRETO ESTÁTICO: código/contratos descritos no campo 3. RELATO: resultados históricos atribuídos, sem reexecução. INFERÊNCIA: consequências possíveis, não incidentes. PROPOSTA/DECISÃO PENDENTE: alternativas e controles; nenhuma autorização, teste de produto ou persistência nova decorre desta revisão.

### Fluxo

Fonte tipada → resolver existente → consumidor selecionado → representação pública. Engine→Serve→Front é uma alternativa, não uma ordem já aprovada.

### Consequências e risco

Ativar flag antes de dado coerente promete disponibilidade inexistente. Reabrir a definição de conflito como se não houvesse código/teste pode alterar contrato sem necessidade. Não foi demonstrado stage incorreto em produção.

### Alternativas e recomendação

Engine primeiro, Serve/query primeiro ou superfície documental delimitada são alternativas do corpo. Recomenda-se escolher pelo caso de uso e menor fronteira útil; documentação sozinha não substitui a prova funcional mantida na issue.

### Dependências e paralelismo

Produtor e resolver já integrados. A decisão de superfície precede sua implementação; levantamento e controles podem avançar em paralelo à política de tentativa. Não exigir três PRs.

### Plano e aceite propostos

Registrar consumidor, entrada/saída, estado absent/not_found/conflict e tratamento de zero/escopo. Planejar controle que perde estado no adapter e deve falhar, além de prova SQL/RDD em E01. Critérios devem dizer comportamento, não número de PRs.

### Comunicação entre responsáveis

Informar aos pods qual é a origem do stage e quando o resultado continua job-level. Não repetir que falta teste de conflito: o teste existe; falta integrar sua semântica.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Ativar a flag do Front antes de haver dado coerente prometeria disponibilidade inexistente, e reabrir a definição de conflito alteraria um contrato que já tem código e teste. Que caso o teste ainda não cobre? — O resolver já cobre conflito do mesmo stage; o que falta é a superfície escolhida mostrar esse estado, e a #169 só informa a seleção de tentativa, sem bloquear esta folha. Como eu explicaria isso para outro pod? — Engine primeiro, Serve ou query primeiro e superfície documental são alternativas do corpo da #115; a escolha define quem mostra o conflito e quando o resultado continua job-level, sem exigir três PRs.

### Próxima ação e encerramento

Owner da #115 a confirmar: registrar escolha e seus critérios. Encerrar DEC-09 com decisão rastreável; E02/E01 continuam até suas provas, sem retirar genericamente -1 dos watchers.

<a id="item-088"></a>

## DEC-N6 — Associação forte/fraca no gate tail-outlier (E17)

Frente: contratos_e_decisoes. Encaminhamento: decidir_garantia_e_controles_condicionais.

### Identidade e estado

DEC-N6 — Associação forte/fraca no gate tail-outlier (E17); ID de origem preservado. Acompanhamento [#123](fichas-02.md#item-016); owner a confirmar, sem atribuição nova. Estado nesta visão: decidir_garantia_e_controles_condicionais.

### Intenção e benefício

Definir a garantia do gate tail-outlier: encontrar resultado no job ou associá-lo ao mesmo stage/tentativa/população/snapshot da asserção.

### Feito, faltante e não comprovado

O wrapper confirma job_id, RC zero e substring do watcher; não compara a identidade do finding nem valida o contador LLM impresso. Há runtime histórico relatado em setembro, portanto a decisão não bloqueia retroativamente uma prova que já ocorreu.

### Linhagem

Estudo da revisão de #127 → E17 → reuse_existing #123 → DEC-N6. O catálogo anterior marcava sem objeto público; há acompanhamento relacionado #123, embora a decisão não seja uma issue pública separada.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/F-DECISOES-NECESSARIAS.md#dec-n6, linha 318; CSV/MATRIX/PUBLICATION preservados. Código na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874 e fontes primárias de [#123](fichas-02.md#item-016); consulta 16–17/10 explicitada nos recibos. As referências abaixo permitem conferir os trechos.

### Classe e limite da evidência

DIRETO ESTÁTICO: código/contratos descritos no campo 3. RELATO: resultados históricos atribuídos, sem reexecução. INFERÊNCIA: consequências possíveis, não incidentes. PROPOSTA/DECISÃO PENDENTE: alternativas e controles; nenhuma autorização, teste de produto ou persistência nova decorre desta revisão.

### Fluxo

Garantia escolhida → campos observados → predicado do gate → controles → evidência. O comportamento atual não pode ser explicado como prova do stage escolhido.

### Consequências e risco

Uma string/finding de outro stage pode satisfazer o predicado atual; risco estático, sem falso PASS reproduzido. Escolher opção fraca e exigir depois todos os controles de associação forte cria critério contraditório.

### Alternativas e recomendação

Forte: associar identidades e população/snapshot. Fraca: delimitar garantia por job. Híbrida: explicitar o que adverte e o que falha. Recomenda-se escolher pela finalidade do gate, sem declarar decisão nesta auditoria.

### Dependências e paralelismo

A decisão pode ser estudada sem runtime. Nova execução/prova segue ambiente e guardas próprios; não é razão para apagar o recibo de setembro ou esperar toda política #175 para ler o código.

### Plano e aceite propostos

Registrar garantia e regra de aceitação. Se forte, controles de outro stage/tentativa/população/snapshot e nome isolado precisam falhar; positivo corresponde à identidade. Se fraca, controles/refusal devem cobrir a garantia menor e a documentação não promete mais. Zero LLM exige contador observado se mantido como garantia.

### Comunicação entre responsáveis

Na eventual atualização autorizada de #123, explicar regra escolhida, controles e limites. Usar job ou stage/snapshot conforme a decisão, sem frase que já apresente strong binding como existente.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Escolher a garantia fraca e depois exigir todos os controles de associação forte criaria critério contraditório; com o predicado atual, uma string ou finding de outro stage pode satisfazer o gate. Que caso o teste ainda não cobre? — O wrapper confere job_id, RC zero e substring do watcher, mas não identifica snapshot nem população do finding, e o contador LLM é impresso, não medido; nenhum falso PASS foi reproduzido. Como eu explicaria isso para outro pod? — O runtime histórico permanece como relato público com árvore, ambiente e limites próprios. Escolher garantia fraca ou forte define os controles adicionais; não impor associação forte após ratificar outra política.

### Próxima ação e encerramento

Mantenedor/Package a confirmar: ratificar garantia e produzir folha pequena com testes apropriados. Encerrar DEC-N6 com decisão e plano; implementar/validar gate depois, sem novas operações nesta revisão.

<a id="item-089"></a>

## #21 — [FEATURE] CI Integration (pre-merge code review)

Frente: issues_restantes. Encaminhamento: decidir_produto_sem_confundir_governanca_ci.

### Identidade e estado

Issue #21, aberta; assignees: nenhum. Consulta 2026-10-16T18:29:24.609Z. Origens: X08. Responsável futuro a confirmar; disposição decidir_produto_sem_confundir_governanca_ci.

### Intenção e benefício

Avaliar APEX Recommendation Engine em diffs de PR e feedback antes do merge. Essa feature é diferente de rodar testes do próprio repositório.

### Feito, faltante e não comprovado

A issue descreve GitHub Actions/Azure DevOps e comentários em PR. Os comentários de julho relatam scenario-gate, correções e um oracle local; dizem explicitamente que isso ainda não implementava review automático. Não há nesses relatos aceite da feature. Ausência de comentário recente não prova ausência universal de trabalho.

### Linhagem

Epic #15 → #21; comentários ligam #29 e linhas históricas de cenário/oracle. #125 é governança de merge e #130 capacidade operacional, não implementações do analisador.

### Fontes e corte

Corpo público preservado em fontes/batch-rest-issues-sources/issue-21.md, extraído da consulta de 16/10; comentários do snapshot-20261016. Ficha de origem: ../parte-03-claude-v2/fontes/claude-v2/C02-ISSUES-ABERTAS.md#i-21, linha 89. Código, quando citado, fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Fontes adicionais abaixo; recibo de custódia da #105 é novo em 17/10.

### Classe e limite da evidência

DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Na #105 há verificação própria de arquivo Git, sem executar código de produto; demais execuções não foram realizadas.

### Fluxo

Diff não confiável → análise delimitada → recomendações com fonte/confiança → feedback revisável no PR. Fluxo proposto; um teste de cenário não cobre essa cadeia.

### Consequências e risco

Confundir teste verde com análise automática de performance infla a entrega. Um bot que executa conteúdo de PR sem fronteira pode ampliar permissões; risco de desenho, sem incidente relatado.

### Alternativas e recomendação

Decidir implementar piloto, adiar ou rejeitar conforme prioridade de produto. Adiamento é recomendação anterior ainda a ratificar; estudo não precisa aguardar toda a proteção da main.

### Dependências e paralelismo

Definir objeto analisado, permissões e dono precede implementação. #125/#130 afetam operação futura conforme plataforma, mas não são gates para estudo. Maturidade do Serve só é dependência se a solução escolhida o usar.

### Plano e aceite propostos

Propor uma superfície mínima de entrada/saída e casos anti-pattern positivo/negativo, diff vazio e entrada hostil. Separar teste do repositório, análise APEX e publicação de comentário. Aceite futuro requer recomendações discriminantes e permissões mínimas; publicação externa continua ação específica.

### Comunicação entre responsáveis

Explicar ao time quais gates históricos existem e qual função de produto ainda está apenas proposta. Não prometer comentário automático por haver workflow.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Confundir teste verde do repositório com análise automática de performance inflaria a entrega, e um bot que execute conteúdo de PR sem fronteira ampliaria permissões. Que caso o teste ainda não cobre? — O scenario-gate e o oracle de julho não implementavam review automático; ainda falta definir qual código o bot inspeciona, o que executa e se um falso positivo poderia bloquear merge. Como eu explicaria isso para outro pod? — A feature é rodar o APEX sobre diffs de PR e publicar recomendações revisáveis, não rodar pytest do repositório; quem pode publicar e se haverá piloto, adiamento ou rejeição é decisão de produto.

### Próxima ação e encerramento

Mantenedor/owner de produto a confirmar: decidir piloto/adiar/rejeitar e registrar escopo. A issue não está encerrada pelo cenário histórico nem automaticamente adiada nesta auditoria.

<a id="item-090"></a>

## #33 — [Governance] Add SECURITY.md (LICENSE + NOTICE done)

Frente: issues_restantes. Encaminhamento: decidir_canal_e_politica_de_vulnerabilidades.

### Identidade e estado

Issue #33, aberta; assignees: nenhum. Consulta 2026-10-16T18:29:24.609Z. Origens: X04. Responsável futuro a confirmar; disposição decidir_canal_e_politica_de_vulnerabilidades.

### Intenção e benefício

Definir um canal privado e responsáveis para relatos de vulnerabilidade, com versões suportadas e expectativas de resposta realistas.

### Feito, faltante e não comprovado

A árvore completa c3c3ea3 contém LICENSE e NOTICE e nenhum SECURITY.md em qualquer caminho listado. O comentário restringe o escopo: licença Apache-2.0 e atribuição já entregues; SECURITY.md é a lacuna. Isso não é nova avaliação jurídica de titularidade ou permissão de relicenciamento.

### Linhagem

#33 originalmente misturava licença/proveniência/política → comentário de encerramento parcial → SECURITY.md residual. #42 trata arquitetura offline/on-prem, uma decisão distinta.

### Fontes e corte

Corpo público preservado em fontes/batch-rest-issues-sources/issue-33.md, extraído da consulta de 16/10; comentários do snapshot-20261016. Ficha de origem: ../parte-03-claude-v2/fontes/claude-v2/C02-ISSUES-ABERTAS.md#i-33, linha 51. Código, quando citado, fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Fontes adicionais abaixo; recibo de custódia da #105 é novo em 17/10.

### Classe e limite da evidência

DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Na #105 há verificação própria de arquivo Git, sem executar código de produto; demais execuções não foram realizadas.

### Fluxo

Descobridor → canal privado definido → triagem pelo responsável → confirmação/correção/divulgação coordenada conforme política. Fluxo futuro, sem contato ou publicação executados aqui.

### Consequências e risco

Canal sem responsável pode receber relato sem tratamento; prazo fictício cria promessa operacional. Reabrir licença inteira ignora a atualização explícita do mantenedor.

### Alternativas e recomendação

Usar canal privado existente do repositório/organização ou contato dedicado validado pelo dono. Escolher pela capacidade de triagem; não inventar endereço nem assumir que recurso GitHub está habilitado.

### Dependências e paralelismo

Mantenedor define canal, responsáveis e suporte. Desenho de #42 pode ocorrer em paralelo; disclosure não é predecessor técnico universal de qualquer estudo on-prem.

### Plano e aceite propostos

Redigir política com canal confirmado, escopo, dados sanitizados, versões e processo de triagem. Controle de revisão: link/canal existe e não incentiva publicar segredo em issue; prazos têm responsável. Integrar após revisão, sem refazer LICENSE/NOTICE.

### Comunicação entre responsáveis

Comunicar somente o residual da política e distinguir disponibilidade do arquivo de eficácia operacional do canal. Não publicar contato inferido.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Publicar um canal sem responsável deixaria relatos sem tratamento, prazo fictício criaria promessa operacional, e reabrir a licença ignoraria a atualização do mantenedor. Que caso o teste ainda não cobre? — A árvore c3c3ea3 tem LICENSE e NOTICE e nenhum SECURITY.md; falta confirmar que o canal é realmente privado e quais versões são suportadas, sem contato inferido. Como eu explicaria isso para outro pod? — O que resta da #33 é a política de vulnerabilidades: quem recebe e responde, por qual canal privado, e que informação sensível não deve aparecer em issue pública.

### Próxima ação e encerramento

Mantenedor/admin a confirmar: escolher canal e responsáveis; próxima entrega é texto revisável. Encerrar quando política e canal estiverem coerentes e integrados, sem contato externo nesta auditoria.

