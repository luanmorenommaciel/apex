# Fichas documentais — lote 8

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-071"></a>

## X06 — Arquivar branches históricas antes de excluir (#105)

Frente: registro_associado_issues_centrais. Encaminhamento: arquivo_verificado_custodia_a_reconciliar.

### Identidade e estado

ID canônico X06: Arquivar branches históricas antes de excluir (#105). Origem preservada no registro de 158 IDs; acompanhamento [#105](fichas-10.md#item-092). Responsável do próximo passo a confirmar. Disposição: arquivo_verificado_custodia_a_reconciliar.

### Intenção e benefício

Preservar recuperação das cinco linhas históricas antes de qualquer exclusão, com identidade exata e responsável de custódia.

### Feito, faltante e não comprovado

Arquivo de 26/08 localizado. Nova verificação Codex: cinco arquivos conformes ao SHA256SUMS, bundle verify, restauração de cinco refs, igualdade com BRANCH-TO-SHA.tsv e fsck estrito passaram em 17/10. Isso corrige a contradição da ficha original, que dizia bundle existe e depois bundle não criado. Nenhuma branch remota foi consultada novamente ou modificada.

### Linhagem

#105 → bundle de 26/08 → X06/L03 e EV-30 no registro → recibo próprio de 17/10. Quatro branches APEX e uma workspace têm repositórios distintos; o mapa preserva essa separação.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/C03c-REGISTRO-S-X.md#reg-x06, linha 892; CSV, MATRIX e PUBLICATION preservados. Fontes primárias, datas e SHA de código são os da ficha [#105](fichas-10.md#item-092), relacionadas abaixo. Código APEX fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; estados públicos são os recibos de 16–17/10, não uma consulta implícita nova.

### Classe e limite da evidência

DIRETO ESTÁTICO: trechos e metadados descritos nos campos 3–5 e na ficha [#105](fichas-10.md#item-092). RELATO: execuções/resultados históricos ali atribuídos. INFERÊNCIA: riscos condicionais do campo 8. PROPOSTA: opções e menor prova futura; nenhuma decisão de mantenedor, execução de produto ou publicação nova nesta revisão.

### Fluxo

Heads no mapa → bundle → hashes → restauração em bare isolado → comparação de cinco commits. A consulta de uso futuro em PRs é um elo posterior à verificação do arquivo.

### Consequências e risco

Recriar o bundle sem necessidade duplica trabalho; excluir com base em snapshot antigo pode perder commits/uso novo. Restauração prova recuperabilidade dos objetos arquivados, não equivalência com remoto atual.

### Alternativas e recomendação

Reutilizar o arquivo e registrar custódia. Se heads remotos tiverem mudado, preservar snapshot adicional após comparação; não sobrescrever o histórico. Publicação externa é decisão distinta.

### Dependências e paralelismo

X12 pode orientar limpeza geral, mas não é requisito para reconhecer este arquivo já válido. Consulta atual de heads/PRs e decisão de exclusão são gates de eventual deleção, não da conferência feita.

### Plano e aceite propostos

Vincular recibo e metadados aos cinco heads; registrar custodiante e meio de recuperação. Controle de integridade já executado detecta hash/ref divergente. Antes de exclusão futura, atualizar head/base usage e preservar diferenças. Aceite documental desta folha: arquivo real reconhecido, limites e decisão restante explícitos.

### Comunicação entre responsáveis

Corrigir a afirmação de ausência numa eventual atualização autorizada da #105. Comunicar hash/refs sem caminhos pessoais no texto público; não anunciar exclusão nem merge de código histórico.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Recriar o bundle sem necessidade duplicaria trabalho, e excluir branches com base no snapshot antigo de uso em PRs poderia perder commits ou uso posterior. Que caso o teste ainda não cobre? — A restauração de 17/10 prova recuperabilidade dos cinco objetos arquivados conforme BRANCH-TO-SHA.tsv, não equivalência com o remoto atual; se algum head avançou e qual snapshot de uso em PRs vale para a exclusão futura não foi consultado. Como eu explicaria isso para outro pod? — O arquivo de 26/08 existe e passou por hash, bundle verify, restauração e fsck em 17/10; falta registrar quem garante a custódia, e exclusão ou publicação são decisões separadas.

### Próxima ação e encerramento

Custodiante/mantenedor a confirmar: registrar recuperação e destino de custódia. Não criar bundle novo nem excluir branches por esta auditoria; a issue deve ser reconciliada com o arquivo existente.

<a id="item-072"></a>

## L03 — Salvage das cinco branches

Frente: registro_associado_issues_centrais. Encaminhamento: salvage_preservado_sem_reaplicar_produto.

### Identidade e estado

ID canônico L03: Salvage das cinco branches. Origem preservada no registro de 158 IDs; acompanhamento [#105](fichas-10.md#item-092). Responsável do próximo passo a confirmar. Disposição: salvage_preservado_sem_reaplicar_produto.

### Intenção e benefício

Conservar a linhagem e ideias úteis de cinco branches históricas sem fundir árvores de produto obsoletas na main.

### Feito, faltante e não comprovado

Os cinco refs arquivados foram restaurados e conferidos em 17/10. O relato histórico de heads iguais aos remotos não foi renovado: a conclusão atual é sobre o arquivo. Valor técnico das ideias/patches de cada branch não foi reavaliado integralmente nesta ficha.

### Linhagem

Auditoria salvage de agosto → #105/bundle → L03 encerrado como registro de história → X06/DEC-13 para custódia. O elo público existe por #105 mesmo que a ficha antiga dissesse nenhum objeto APEX ligado.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/C03d-REGISTRO-L-DD-W-D.md#reg-l03, linha 48; CSV, MATRIX e PUBLICATION preservados. Fontes primárias, datas e SHA de código são os da ficha [#105](fichas-10.md#item-092), relacionadas abaixo. Código APEX fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; estados públicos são os recibos de 16–17/10, não uma consulta implícita nova.

### Classe e limite da evidência

DIRETO ESTÁTICO: trechos e metadados descritos nos campos 3–5 e na ficha [#105](fichas-10.md#item-092). RELATO: execuções/resultados históricos ali atribuídos. INFERÊNCIA: riscos condicionais do campo 8. PROPOSTA: opções e menor prova futura; nenhuma decisão de mantenedor, execução de produto ou publicação nova nesta revisão.

### Fluxo

História Git preservada → inspeção futura de ideias/evidências → proposta nova delimitada, se houver utilidade atual. Não há seta automática arquivo→merge.

### Consequências e risco

Interpretar código recuperável como compatível com a main pode reintroduzir arquiteturas superadas. Apagar a história por não haver PR Closes perde a trilha de contribuição.

### Alternativas e recomendação

Manter L03 catalogado como história recuperável e referenciar X06. Extração seletiva de ideia pode ser estudada se surgir necessidade; reaplicar branches completas não é recomendação desta revisão.

### Dependências e paralelismo

Custódia durável pertence a DEC-13/X06. Não há nova implementação dependente de L03; eventual extração começa por comparar o recorte atual e sua fonte histórica.

### Plano e aceite propostos

Preservar mapeamento branch/repositório/commit e links ao arquivo. Verificação da auditoria já demonstrou restauração dos objetos; qualquer reaproveitamento exige prova nova da mudança proposta. Controle documental: merge histórico não pode ser inferido de um bundle ou de um comentário.

### Comunicação entre responsáveis

Explicar o que foi preservado e o que continua apenas contexto. Atribuir cada contribuição à branch/commit original, sem transportar testes antigos para a main.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Tratar código recuperável como compatível com a main poderia reintroduzir arquiteturas superadas, e apagar a história por falta de PR com Closes perderia a trilha de contribuição. Que caso o teste ainda não cobre? — O valor técnico das ideias de cada branch não foi reavaliado; uma prova antiga vale para a tree em que foi gerada, e cada commit precisa ser atribuído ao repositório de origem, já que quatro branches são do APEX e uma da workspace. Como eu explicaria isso para outro pod? — O salvage fica como história recuperável, com os cinco refs restaurados em 17/10; não há seta automática de arquivo para merge, e só uma necessidade atual justificaria novo patch em vez de simples referência.

### Próxima ação e encerramento

Curador: encerrar a catalogação do salvage com refs verificáveis e custódia em X06/DEC-13. Nenhuma ação de produto ou exclusão está indicada por este ID.

<a id="item-073"></a>

## DEC-13 — Custódia do bundle #105 e escopo de branches

Frente: registro_associado_issues_centrais. Encaminhamento: decidir_custodia_publicacao_e_eventual_exclusao.

### Identidade e estado

ID canônico DEC-13: Custódia do bundle #105 e escopo de branches. Origem preservada no registro de 158 IDs; acompanhamento [#105](fichas-10.md#item-092). Responsável do próximo passo a confirmar. Disposição: decidir_custodia_publicacao_e_eventual_exclusao.

### Intenção e benefício

Definir quem guarda o arquivo recuperável, onde ele fica disponível aos responsáveis e se alguma publicação ou exclusão futura é apropriada.

### Feito, faltante e não comprovado

Bundle, inventário e README já existem e passaram por nova recuperação nesta auditoria. A lacuna não é criar artefatos do zero. Custódia/publicação e uso remoto atual não foram decididos ou consultados por essa prova.

### Linhagem

Arquivo #105/26-08 → X06/L03 → DEC-13. A identidade do bundle 5523adca… coincide com o catálogo histórico; nenhuma autoridade de exclusão decorre do hash.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/F-DECISOES-NECESSARIAS.md#dec-13, linha 372; CSV, MATRIX e PUBLICATION preservados. Fontes primárias, datas e SHA de código são os da ficha [#105](fichas-10.md#item-092), relacionadas abaixo. Código APEX fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; estados públicos são os recibos de 16–17/10, não uma consulta implícita nova.

### Classe e limite da evidência

DIRETO ESTÁTICO: trechos e metadados descritos nos campos 3–5 e na ficha [#105](fichas-10.md#item-092). RELATO: execuções/resultados históricos ali atribuídos. INFERÊNCIA: riscos condicionais do campo 8. PROPOSTA: opções e menor prova futura; nenhuma decisão de mantenedor, execução de produto ou publicação nova nesta revisão.

### Fluxo

Arquivo verificado → custodiante/local de recuperação decidido → eventual divulgação autorizada → consulta atual de refs/PRs → decisão de excluir ou manter. Cada decisão é separável.

### Consequências e risco

Custódia apenas implícita pode perder acesso a longo prazo. Publicar um arquivo por existir sem revisar destino/conteúdo amplia escopo; excluir com uso antigo de PRs ignora mudanças posteriores.

### Alternativas e recomendação

Manter custódia local organizada, replicar em local escolhido pelos owners ou publicar metadados/bundle após revisão específica. Preservar branches é alternativa válida; limpeza não é requisito automático do archive.

### Dependências e paralelismo

Integridade/restauração dos cinco objetos já comprovada. Inventário X12 e consulta de uso são necessários conforme escopo da limpeza pretendida, não para decidir custódia. Toda ação externa exige decisão própria.

### Plano e aceite propostos

Registrar custodiante, acesso, retenção e recuperação; definir o que pode ser divulgado. Para eventual exclusão, comparar heads atuais e uso em PRs imediatamente antes, manter recuperação e registrar aprovação. Aceite da decisão: escolhas atribuídas com limites; nenhuma deleção necessária para fechar custódia.

### Comunicação entre responsáveis

Comunicar arquivo disponível e restauração verificada, sem anunciar que branches atuais estão sem uso. Metadado público não deve expor caminhos pessoais ou credenciais.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Manter a custódia apenas implícita pode perder o acesso se a máquina mudar, e excluir branches com uso antigo de PRs ignora mudanças posteriores; o hash 5523adca… não dá autoridade de exclusão. Que caso o teste ainda não cobre? — Integridade e restauração dos cinco objetos estão comprovadas; a consulta de uso em PRs de 26/08 não é atual para uma decisão de exclusão, e publicar bytes ou só a referência ainda não foi decidido. Como eu explicaria isso para outro pod? — O arquivo já existe e foi verificado; a decisão é quem guarda e recupera, o que pode ser divulgado e qual condição justificaria excluir, cada uma separável e nenhuma executada aqui.

### Próxima ação e encerramento

Mantenedor/custodiante a confirmar: ratificar destino/retenção/acesso e reconciliar #105. Encerrar DEC-13 conforme decisão de custódia; manter publicação e exclusão como ações explícitas, sem executá-las aqui.

<a id="item-074"></a>

## F02 — Tabela verdade do piso de ruído (T09a)

Frente: contratos_e_decisoes. Encaminhamento: ratificar_semantica_por_fronteira.

### Identidade e estado

F02 — Tabela verdade do piso de ruído (T09a); ID de origem preservado. Acompanhamento [#117](fichas-02.md#item-015); owner a confirmar, sem atribuição nova. Estado nesta visão: ratificar_semantica_por_fronteira.

### Intenção e benefício

Unificar o significado do piso, igualdade, ausência e direção para que a mesma observação não receba certificações incompatíveis entre Verify, projeção SQL e UI.

### Feito, faltante e não comprovado

Verify usa abs(delta)>=piso quando atribuível e piso válido; SQL Front/Serve usa >; o render replay de Serve recusa < e aceita igualdade. Defesas de piso não medido/inválido já existem. O relato de 32 casos/oito divergências da Lane C é histórico, não foi reexecutado. Zero/zero e fronteiras numéricas exigem tratamento explícito; não basta substituir um operador.

### Linhagem

F02/T09a e X02 → #117/DEC-05 → correções parciais integradas de pisos inválidos → tabela residual. #145 é correção específica, não implementação de todas as decisões H-1…H-8.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md#reg-f02, linha 496; CSV/MATRIX/PUBLICATION preservados. Código na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874 e fontes primárias de [#117](fichas-02.md#item-015); consulta 16–17/10 explicitada nos recibos. As referências abaixo permitem conferir os trechos.

### Classe e limite da evidência

DIRETO ESTÁTICO: código/contratos descritos no campo 3. RELATO: resultados históricos atribuídos, sem reexecução. INFERÊNCIA: consequências possíveis, não incidentes. PROPOSTA/DECISÃO PENDENTE: alternativas e controles; nenhuma autorização, teste de produto ou persistência nova decorre desta revisão.

### Fluxo

Medição + atribuição + disponibilidade/unidade do piso → magnitude resolvível → direção → estado de apresentação. Uma ausência não entra como zero e mecanismo é dimensão independente.

### Consequências e risco

Mudar só > para >= pode criar zero/zero certificado e rótulo regressed no ramo final. Isso é consequência possível da expressão lida, não execução com incidente. Forçar todos os consumidores à mesma fórmula sem tratar unidades pode criar nova divergência.

### Alternativas e recomendação

Recomenda-se tabela ratificada por estado e fronteira. Manter diferença deliberada entre previsão/medição é possível se documentada; divergência acidental não deve ser normalizada como preferência de UI.

### Dependências e paralelismo

Owners e rota de F06 ajudam a delimitar consumidores. A tabela pode ser estudada em paralelo a F03/F06; não precisa aguardar fim de M1 nem #162. Implementação segue a política escolhida.

### Plano e aceite propostos

Preparar linhas com piso ausente, inválido, zero e positivo; delta negativo/zero/positivo; abaixo/igual/acima; atribuição true/false/unknown; mecanismo independente. Definir unidade e tolerância. Aceite: cada consumidor relevante tem resultado esperado e controle negativo que diferencia regra antiga da acordada; casos históricos não são apagados.

### Comunicação entre responsáveis

Mostrar tabela com decisão, fonte normativa, consumidores afetados e casos preservados. Separar magnitude resolvível de benefício, estado de atribuição e causa.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Trocar só > por >= pode certificar zero/zero e lançar zero no rótulo regressed, e forçar todos os consumidores à mesma fórmula sem tratar unidades criaria nova divergência. Que caso o teste ainda não cobre? — Conferir a tabela de decisão e o roundtrip nos casos de empate, zero e fronteira. O estudo histórico de 32 casos é relato preservado, não uma execução refeita nesta revisão nem ausência de casos. Como eu explicaria isso para outro pod? — Verify usa abs(delta)>=piso, a SQL de Front e Serve usa > e o replay do Serve aceita igualdade; a tabela ratificada define o que zero/zero significa, a regra na igualdade, o sentido de delta negativo e se a unidade é fração ou percentual.

### Próxima ação e encerramento

Owners Verify/Front/Serve a confirmar: ratificar tabela e aceitar mudanças por fronteira. Encerrar F02 com decisão e controles do escopo escolhido, não com criação de folhas apenas.

<a id="item-075"></a>

## F03 — Atribuição true/false/unknown (T09b)

Frente: contratos_e_decisoes. Encaminhamento: decidir_representacao_de_atribuicao.

### Identidade e estado

F03 — Atribuição true/false/unknown (T09b); ID de origem preservado. Acompanhamento [#117](fichas-02.md#item-015); owner a confirmar, sem atribuição nova. Estado nesta visão: decidir_representacao_de_atribuicao.

### Intenção e benefício

Conservar true/false/unknown ao atravessar fronteiras, para que um histórico sem informação não vire atribuível por convenção.

### Feito, faltante e não comprovado

Measurement.attributable tem default True, mas to_row não serializa o campo. A forma persistida lida não distingue os estados de atribuição. Nenhum escritor real foi comprovado neste recorte; não há incidente E2E demonstrado.

### Linhagem

F03/T09b → #117/DEC-05 → escolha entre representação explícita e projeção publicável. F04 é implementação posterior; F05 depende de como a representação atravessará storage.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md#reg-f03, linha 532; CSV/MATRIX/PUBLICATION preservados. Código na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874 e fontes primárias de [#117](fichas-02.md#item-015); consulta 16–17/10 explicitada nos recibos. As referências abaixo permitem conferir os trechos.

### Classe e limite da evidência

DIRETO ESTÁTICO: código/contratos descritos no campo 3. RELATO: resultados históricos atribuídos, sem reexecução. INFERÊNCIA: consequências possíveis, não incidentes. PROPOSTA/DECISÃO PENDENTE: alternativas e controles; nenhuma autorização, teste de produto ou persistência nova decorre desta revisão.

### Fluxo

Estado em memória → representação com presença explícita → linha/contrato de leitura → consumidor. Histórico sem campo entra como desconhecido, nunca inferido de safe, method ou confidence.

### Consequências e risco

Adicionar default verdadeiro à leitura de payload antigo fabricaria atribuição. Alterar o default do construtor sem entender os chamadores também pode modificar comportamento além do necessário; o desenho deve distinguir nova instância e registro histórico.

### Alternativas e recomendação

Tri-estado versionado é uma opção; projeção publicável separada é outra prevista no corpo. Recomenda-se decidir compatibilidade antes de escolher enum/coluna, preservando o dado bruto quando útil.

### Dependências e paralelismo

F02 informa magnitude e F06 identifica rota; os estudos podem avançar em paralelo. Não há dependência serial absoluta F02→F03 para levantar alternativas; aplicação depende da representação ratificada.

### Plano e aceite propostos

Exemplificar true, false, campo ausente e valor desconhecido conforme contrato. Definir versão, defaults por fronteira e tratamento de payload antigo. Controle negativo: remover o estado na serialização não pode continuar produzindo o mesmo resultado certificável. Aceite inclui leitura/render da rota selecionada.

### Comunicação entre responsáveis

Comunicar quais registros são desconhecidos e por quê. Explicar a diferença entre default interno e dado persistido; evitar prometer que coluna isolada resolve a integração.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Pôr default verdadeiro na leitura de payload antigo fabricaria atribuição, e mudar o default do construtor sem entender os chamadores mudaria comportamento além do necessário. Que caso o teste ainda não cobre? — Measurement.attributable não é serializado por to_row, então false não sobrevive ao round-trip; não há escritor real comprovado, e quais leitores toleram o formato novo ainda não foi levantado. Como eu explicaria isso para outro pod? — Registro antigo sem o campo deve aparecer como desconhecido, nunca reconstruído de safe, method ou confidence; tri-estado versionado ou projeção publicável separada são opções em aberto.

### Próxima ação e encerramento

Donos Verify/Serve/Front a confirmar: registrar representação e compatibilidade; direcionar F04/F05. Encerrar a decisão com critérios verificáveis, mantendo integração pendente até prova.

<a id="item-076"></a>

## F04 — Corrigir modelo e serialização da atribuição (T13a)

Frente: contratos_e_decisoes. Encaminhamento: implementar_fronteira_escolhida_apos_decisao.

### Identidade e estado

F04 — Corrigir modelo e serialização da atribuição (T13a); ID de origem preservado. Acompanhamento [#117](fichas-02.md#item-015); owner a confirmar, sem atribuição nova. Estado nesta visão: implementar_fronteira_escolhida_apos_decisao.

### Intenção e benefício

Implementar a conservação da atribuição na fronteira escolhida, sem transformar a proposta de tri-estado em solução já obrigatória.

### Feito, faltante e não comprovado

A perda em to_row continua visível. A ficha anterior tratava modelo de três estados como entrega fixa, embora F03 ainda admita projeção separada. Não há patch novo aceito nesta revisão.

### Linhagem

F03 define contrato → F04/T13a implementa modelo/serialização ou fronteira alternativa → consumidores. #117 continua objeto público e F05 só entra se houver persistência/schema a ajustar.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md#reg-f04, linha 566; CSV/MATRIX/PUBLICATION preservados. Código na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874 e fontes primárias de [#117](fichas-02.md#item-015); consulta 16–17/10 explicitada nos recibos. As referências abaixo permitem conferir os trechos.

### Classe e limite da evidência

DIRETO ESTÁTICO: código/contratos descritos no campo 3. RELATO: resultados históricos atribuídos, sem reexecução. INFERÊNCIA: consequências possíveis, não incidentes. PROPOSTA/DECISÃO PENDENTE: alternativas e controles; nenhuma autorização, teste de produto ou persistência nova decorre desta revisão.

### Fluxo

Entrada nova/antiga → normalização de estado → representação escolhida → round-trip preservando disponibilidade e atribuição. A prova observa a fronteira realmente usada, não só uma propriedade interna.

### Consequências e risco

Criar enum antes de decisão fixa uma arquitetura não aprovada; testar apenas construtor pode deixar perda em to_row intacta. Nenhum defeito adicional de runtime foi demonstrado.

### Alternativas e recomendação

Menor mudança deve seguir F03: campo com semântica compatível ou projeção publicável. Manter biblioteca interna estável pode ser preferível se a perda estiver apenas na fronteira de exportação.

### Dependências e paralelismo

Representação ratificada é predecessor técnico. Definir testes pode ocorrer enquanto F03 é discutido, com expectativas alternativas identificadas. Novo sink ou UI inteira não é requisito automático desta folha.

### Plano e aceite propostos

Criar controles de true/false/unknown, payload antigo e ida/volta da representação aprovada; preservar piso inválido como ausente e valores brutos quando previstos. Negativo remove o estado e deve alterar o resultado observado. Aceite: pequeno diff, contratos compatíveis e recibo do SHA; não executar nesta auditoria.

### Comunicação entre responsáveis

Explicar exatamente onde o estado antes se perdia e onde passa a ser conservado. Não anunciar persistência real por um round-trip em memória.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Criar um enum antes da decisão de F03 fixaria uma arquitetura não aprovada, e testar só o construtor deixaria intacta a perda em to_row. Que caso o teste ainda não cobre? — O teste precisa passar pela serialização que o consumidor usa, não por uma propriedade interna; nenhum patch foi aceito nesta revisão, e o comportamento antigo a preservar depende do contrato escolhido. Como eu explicaria isso para outro pod? — F04 implementa a conservação da atribuição na fronteira que F03 escolher; se a perda estiver só na exportação, uma projeção separada pode dispensar mudar Measurement.

### Próxima ação e encerramento

Owner Verify a confirmar: implementar somente após decisão do contrato; encerrar com prova discriminante da fronteira e destino dos resíduos de storage/consumo.

<a id="item-077"></a>

## F05 — Representação persistida e migração (T13b)

Frente: contratos_e_decisoes. Encaminhamento: migracao_condicional_a_representacao.

### Identidade e estado

F05 — Representação persistida e migração (T13b); ID de origem preservado. Acompanhamento [#117](fichas-02.md#item-015); owner a confirmar, sem atribuição nova. Estado nesta visão: migracao_condicional_a_representacao.

### Intenção e benefício

Garantir compatibilidade de storage e leitores quando a solução escolhida exigir alteração persistida; histórico sem informação continua desconhecido.

### Feito, faltante e não comprovado

Os DDLs infra/sql/032_fix_verifications.sql e verify/ddl/fix_verifications.ddl.sql lidos não têm coluna de atribuição. Isso elimina a suposição de coluna já disponível nesses arquivos, mas não prova o schema de um banco executado. Nenhuma migração foi criada/aplicada.

### Linhagem

F03/DEC-05 → escolha de representação → F05/T13b se precisar mudar persistência. F06 identifica escritor/ambiente; código de DDL não comprova migração já aplicada.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md#reg-f05, linha 600; CSV/MATRIX/PUBLICATION preservados. Código na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874 e fontes primárias de [#117](fichas-02.md#item-015); consulta 16–17/10 explicitada nos recibos. As referências abaixo permitem conferir os trechos.

### Classe e limite da evidência

DIRETO ESTÁTICO: código/contratos descritos no campo 3. RELATO: resultados históricos atribuídos, sem reexecução. INFERÊNCIA: consequências possíveis, não incidentes. PROPOSTA/DECISÃO PENDENTE: alternativas e controles; nenhuma autorização, teste de produto ou persistência nova decorre desta revisão.

### Fluxo

Contrato aprovado → alteração compatível de schema/projeção → leitor antigo/novo → histórico desconhecido → estratégia de rollback. O fluxo só é aplicável se houver mudança persistida.

### Consequências e risco

Uma coluna com default true pode fabricar atribuição de linhas antigas; rollback sem pensar nos leitores pode perder informação ou quebrar consumo. Esses são riscos de desenho, não incidente observado.

### Alternativas e recomendação

Classificar N/A com justificativa se a solução não exigir mudança de schema; caso exija, desenho aditivo e compatibilidade podem reduzir risco. Não presumir que rollback sempre significa apagar coluna/dados.

### Dependências e paralelismo

F03 define formato, F06 define rota, Infra participa quando necessária. O estudo de compatibilidade pode ocorrer em paralelo; aplicação depende de decisão e ambiente delimitado.

### Plano e aceite propostos

Comparar schemas declarados e efetivo quando autorizado; definir legado/null, ordem de writer/reader e reversão. Controle: leitor antigo e novo diante de linha antiga/nova; nenhuma promoção unknown→true. Aceite N/A fundamentado ou migração/compatibilidade/rollback demonstrados no ambiente apropriado.

### Comunicação entre responsáveis

Indicar quais mudanças são schema, projeção ou somente biblioteca. Documentar claramente a diferença entre DDL no Git e schema aplicado.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Uma coluna com default true fabricaria atribuição em linhas antigas, e um rollback que ignore os leitores poderia perder informação ou quebrar o consumo. Que caso o teste ainda não cobre? — Os DDLs 032_fix_verifications.sql e fix_verifications.ddl.sql não têm coluna de atribuição, mas isso não prova o schema de um banco executado; leitor antigo diante de linha nova ainda não foi exercitado. Como eu explicaria isso para outro pod? — F05 só se aplica se a representação escolhida exigir mudança física; caso contrário fica N/A justificado, e em qualquer caso o histórico preserva desconhecido sem promover unknown a true.

### Próxima ação e encerramento

Infra/Verify a confirmar: registrar N/A ou plano de migração com prova própria. Não abrir DDL por presunção nem fechar como aplicada por existir arquivo.

<a id="item-078"></a>

## F06 — Gravador de fix_verifications / pipeline Verify (T08/T13c)

Frente: contratos_e_decisoes. Encaminhamento: identificar_rota_e_owner_sem_presumir_ausencia.

### Identidade e estado

F06 — Gravador de fix_verifications / pipeline Verify (T08/T13c); ID de origem preservado. Acompanhamento [#117](fichas-02.md#item-015); owner a confirmar, sem atribuição nova. Estado nesta visão: identificar_rota_e_owner_sem_presumir_ausencia.

### Intenção e benefício

Identificar quem produz/persiste verificações e quem responde pelo contrato, para escolher implementação e prova com um caminho de uso real.

### Feito, faltante e não comprovado

O relato da #117 não localizou escritor no head histórico; a auditoria não fez busca exaustiva de sistemas externos. O teste estático de matriz vigia ausência no recorte da lane Verify, não todos os escritores possíveis. PUBLICATION destina F06 à #117. Leitura Serve/Front existente não revela por si de onde vêm todas as linhas.

### Linhagem

F06 → P-DEC06 → disposition reuse_existing #117 → DEC-06. O inventário antigo proposed_issue não autoriza nova publicação duplicada. F19/#162 é identidade de versão do módulo, não correção deste pipeline.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md#reg-f06, linha 634; CSV/MATRIX/PUBLICATION preservados. Código na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874 e fontes primárias de [#117](fichas-02.md#item-015); consulta 16–17/10 explicitada nos recibos. As referências abaixo permitem conferir os trechos.

### Classe e limite da evidência

DIRETO ESTÁTICO: código/contratos descritos no campo 3. RELATO: resultados históricos atribuídos, sem reexecução. INFERÊNCIA: consequências possíveis, não incidentes. PROPOSTA/DECISÃO PENDENTE: alternativas e controles; nenhuma autorização, teste de produto ou persistência nova decorre desta revisão.

### Fluxo

Produtor identificado → escritor identificado ou ausência explicitada → storage → leitor → UI. A existência do leitor não prova escritor; a falta de escritor localizado não torna toda tela fixture ou cálculo local.

### Consequências e risco

Construir um sink duplicado sem mapear o ambiente pode criar duas fontes concorrentes. Rotular todo dado live como fixture por falta de escritor no repo também é incorreto. Não há evidência de incidente de produção nesta revisão.

### Alternativas e recomendação

Adaptar escritor externo existente, criar sink delimitado ou manter representação como contrato futuro são opções. Recomenda-se identificar ambiente/consumidores antes da escolha. Retirar persistência da v1 exige decisão explícita de escopo.

### Dependências e paralelismo

Não depende de #162 ou CI global para investigar. F03/F02 podem avançar em paralelo; integração real F10 depende da rota selecionada. Ownership Verify/Memory deve ser confirmado sem atribuir pessoas automaticamente.

### Plano e aceite propostos

Inventariar entradas, gravação, identidades, versão, retries/idempotência quando aplicáveis e consumidores; registrar dono e fonte. Controle documental: cada seta é observada, declarada ou ausente no recorte. Se escritor for escolhido, abrir folha com critérios próprios; se excluído, rever escopo/rótulos de forma precisa.

### Comunicação entre responsáveis

Explicar de onde cada perfil obtém dados, sem resumir ausência de escritor local como tela que calcula sozinha. Registrar F06 como origem de #117 em eventual comunicação autorizada.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Construir um sink novo sem mapear o ambiente poderia criar duas fontes concorrentes, e rotular todo dado live como fixture por não haver escritor no repositório também seria incorreto. Que caso o teste ainda não cobre? — A matriz estática vigia ausência só no recorte da lane Verify; o escritor não foi localizado no head histórico e sistemas externos não foram buscados, então a fonte pode ser interna, externa, fixture ou importação. Como eu explicaria isso para outro pod? — Existir leitor no Serve e no Front não prova escritor; a decisão é quem grava no ambiente pretendido e se a persistência entra ou sai do escopo, registrada na #117 sem nova publicação duplicada.

### Próxima ação e encerramento

Mantenedor e owners a confirmar: registrar rota e escopo. Encerrar a decisão F06 com fonte/owner/destino e consequências; não fechar #117 funcionalmente só por isso.

<a id="item-079"></a>

## F07 — Persistir amostras de replay para recalcular CV (T13d)

Frente: contratos_e_decisoes. Encaminhamento: decidir_amostras_retencao_e_recalculo.

### Identidade e estado

F07 — Persistir amostras de replay para recalcular CV (T13d); ID de origem preservado. Acompanhamento [#117](fichas-02.md#item-015); owner a confirmar, sem atribuição nova. Estado nesta visão: decidir_amostras_retencao_e_recalculo.

### Intenção e benefício

Tornar o piso de ruído reproduzível quando o produto promete recálculo, conservando amostras, unidade, população e política de retenção apropriadas.

### Feito, faltante e não comprovado

Measurement possui amostras em memória; to_row/DDL lidos guardam medianas e replay_reps, não os vetores individuais. O adapter live retorna replay_durations_ms=None. A contagem de repetições e duas medianas não bastam para reconstruir CV amostral.

### Linhagem

F07/T13d → item de réplicas no comentário de #117 → F02/F17 (semântica/fórmula) e F06 (rota). Armazenar vetores é proposta, não implementação decorrente da presença dos campos em memória.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md#reg-f07, linha 668; CSV/MATRIX/PUBLICATION preservados. Código na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874 e fontes primárias de [#117](fichas-02.md#item-015); consulta 16–17/10 explicitada nos recibos. As referências abaixo permitem conferir os trechos.

### Classe e limite da evidência

DIRETO ESTÁTICO: código/contratos descritos no campo 3. RELATO: resultados históricos atribuídos, sem reexecução. INFERÊNCIA: consequências possíveis, não incidentes. PROPOSTA/DECISÃO PENDENTE: alternativas e controles; nenhuma autorização, teste de produto ou persistência nova decorre desta revisão.

### Fluxo

Amostras do braço escolhido → validação/população/unidade → cálculo do piso → persistência de dados suficientes, se aprovada → recálculo/linhagem ou apresentação de piso fornecido.

### Consequências e risco

Guardar só número de repetições e afirmar piso refeito no cliente seria enganoso. Persistir tudo sem retenção/custo/consumidor cria volume sem finalidade. Não foi medido custo real neste recorte.

### Alternativas e recomendação

Persistir vetores com retenção delimitada, guardar estatísticas suficientes se matematicamente e contratualmente adequadas, ou remover promessa de recálculo são alternativas. Nenhuma foi ratificada; não declarar automaticamente não bloqueante para v1.

### Dependências e paralelismo

F02/F17 definem o cálculo; F06 decide rota. F05 é condicional ao formato, não predecessor incondicional para discutir amostras. A obrigatoriedade na v1 depende dos critérios que o mantenedor mantiver.

### Plano e aceite propostos

Definir braço, unidade, tamanho mínimo, validade, ordenação/identidade e retenção. Controle negativo: dados insuficientes ou população incompatível não geram piso medido; positivo reproduz o valor dentro de tolerância. Se não guardar amostras, consumidor deve dizer que o piso foi fornecido e não medido ali.

### Comunicação entre responsáveis

Distinguir replay_reps, amostras individuais, medianas e piso. Explicar quais permitem recálculo e quais apenas identificam a execução.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Guardar só replay_reps e duas medianas e afirmar que o piso é refeito no cliente seria enganoso; persistir todos os vetores sem retenção nem consumidor cria volume sem finalidade. Que caso o teste ainda não cobre? — O adapter live retorna replay_durations_ms=None, e os dados que bastam para a fórmula escolhida ainda não foram definidos, nem como evitar misturar escalas e populações; o custo real não foi medido. Como eu explicaria isso para outro pod? — Amostras individuais permitem recálculo, medianas e repetições só identificam a execução; persistir vetores, guardar estatísticas suficientes ou retirar a promessa de recálculo da v1 são as opções, e quem consumirá ainda está em aberto.

### Próxima ação e encerramento

Owners Verify/Memory/Front a confirmar: decidir representação e retenção. Encerrar com decisão e provas condicionais de leitura/recálculo; se adiado, registrar a alteração de escopo e os rótulos afetados.

<a id="item-080"></a>

## F08 — VerificationView canônica e versionada (T14)

Frente: contratos_e_decisoes. Encaminhamento: projecao_compartilhada_sem_apagar_leitores_existentes.

### Identidade e estado

F08 — VerificationView canônica e versionada (T14); ID de origem preservado. Acompanhamento [#117](fichas-02.md#item-015); owner a confirmar, sem atribuição nova. Estado nesta visão: projecao_compartilhada_sem_apagar_leitores_existentes.

### Intenção e benefício

Fazer Serve e Front interpretar as mesmas verificações de maneira coerente, com contrato de estados e testes nas fronteiras relevantes.

### Feito, faltante e não comprovado

Serve já tem leitura de fix_verifications e representação de verificação; Front possui query/adapter e a API #129 já foi integrada. O objetivo não é criar toda a leitura do zero. Igualdade/atribuição seguem como gaps do contrato compartilhado. A expressão canônica não existe deve ser entendida como contrato unificado ainda não ratificado, não classe inexistente.

### Linhagem

F08/T14 → F03/F02 (contrato) + #129/P04 (leitura/API existente) → consumidores. Guardas/paridade anteriores não garantem automaticamente estados novos da atribuição.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md#reg-f08, linha 703; CSV/MATRIX/PUBLICATION preservados. Código na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874 e fontes primárias de [#117](fichas-02.md#item-015); consulta 16–17/10 explicitada nos recibos. As referências abaixo permitem conferir os trechos.

### Classe e limite da evidência

DIRETO ESTÁTICO: código/contratos descritos no campo 3. RELATO: resultados históricos atribuídos, sem reexecução. INFERÊNCIA: consequências possíveis, não incidentes. PROPOSTA/DECISÃO PENDENTE: alternativas e controles; nenhuma autorização, teste de produto ou persistência nova decorre desta revisão.

### Fluxo

Linha de verificação + proveniência → projeção com estado/disponibilidade → Serve/Front. O mesmo tipo nominal não garante semântica idêntica em queries e renderizadores.

### Consequências e risco

Criar representação paralela sem mapear as existentes mantém divergência e aumenta manutenção. Comparar dois consumidores igualmente errados não comprova aderência à regra ratificada.

### Alternativas e recomendação

Contrato compartilhado com fixtures normativas e implementações distintas pode bastar; endpoint/projeção único é alternativa arquitetural. Recomenda-se decidir pelo menor ponto que elimina duplicação prejudicial, sem exigir nova API por princípio.

### Dependências e paralelismo

F03/F02 definem estados e operadores; desenho pode ocorrer em paralelo. #129 já integrada não é gate futuro. Transporte/browser #172 é prova específica e não requisito de todo teste de projeção.

### Plano e aceite propostos

Mapear campos das projeções atuais; acrescentar casos normativos true/false/unknown, piso ausente/igualdade e mecanismo independente. Controle negativo altera um consumidor e deve quebrar paridade ou expectativa normativa. Aceite: cada campo preserva significado/ausência; paridade não substitui prova de storage real.

### Comunicação entre responsáveis

Explicar qual parte já existe e qual é nova. Usar tabela campo→fonte→unidade→estado, com limite por consumidor; não prometer unificação pelo nome VerificationView.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Criar uma representação paralela sem mapear as existentes manteria a divergência, e comparar dois consumidores igualmente errados não prova aderência à regra ratificada. Que caso o teste ainda não cobre? — A paridade atual compara valores, não necessariamente estados como atribuição e piso ausente; quando os dois consumidores concordam no erro, a fonte normativa tem de ser a tabela de F02/F03, e a compatibilidade dos leitores antigos não foi conferida. Como eu explicaria isso para outro pod? — Serve e Front já leem fix_verifications; o que falta é um contrato compartilhado de estados ratificado, não uma classe nova, e o nome VerificationView sozinho não unifica a semântica.

### Próxima ação e encerramento

Owners Serve/Front a confirmar: escolher contrato/projeção e folha mínima. Encerrar após integração e controles dos estados escolhidos, mantendo runtime específico separado.

