# Fichas documentais — lote 12

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-111"></a>

## DEC-15 — Publicação dos candidatos locais

Frente: decisoes_candidatos_locais. Encaminhamento: decidir_publicacao_do_artefato_correto.

### Identidade e estado

DEC-15 — Publicação dos candidatos locais. Decisão ainda não ratificada; responsáveis específicos a confirmar. A auditoria recomenda sem decidir pelo mantenedor.

### Intenção e benefício

Definir qual candidato será submetido, como seu diff será dividido e qual prova é necessária para o escopo escolhido; publicar e integrar são decisões distintas.

### Feito, faltante e não comprovado

Existem candidato conjunto 1122d031 com binding false e variante runner-only PATCH-167.diff com binding padrão. Há recibo integral e2e/macOS para o primeiro e seis casos argv para o segundo. C2/31 passes é gerador G2: retirar seu aceite formal como gate automático. Nenhuma PR nova foi criada por esta auditoria.

### Linhagem

E08/E16 → #174/#167 → candidatos de identidades distintas → DEC-N5 escolhe contrato → DEC-15 escolhe submissão → revisão/CI/integração posteriores. CL-05/06 é linha externa de tooling G2, sem dependência técnica demonstrada.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 426. Releitura de 17/10/2026 dos candidatos CL-01, CL-03, CL-06; suas fontes primárias/hashes estão relacionadas abaixo e em CAPTURA-E-INTEGRIDADE.json. Código APEX fixado em c3c3ea3; execuções históricas conservam suas datas.

### Classe e limite da evidência

FATO OBSERVADO: conteúdo estático e identidade dos artefatos. RELATO HISTÓRICO: resultados de execução, sem reexecução. INFERÊNCIA: riscos condicionais. PROPOSTA: critérios futuros. DECISÃO PENDENTE: opção e owner, sem nova autorização funcional.

### Fluxo

Contrato escolhido + bytes fixados → pacote de revisão por fonte/controle → autorização de publicação → PR → prova da árvore final → decisão de merge. Cada seta produz um artefato/decisão, não um aceite presumido.

### Consequências e risco

Submeter variante com recibos de outra cria aparência de cobertura; esperar tooling G2 atrasa a correção por relação falsa. Publicação por si não remove a cópia da main. Não foi observada perda de arquivo real.

### Alternativas e recomendação

Publicar candidato conjunto coeso ou separar interface/preservação são opções. Provar Windows antes de submeter ou registrar limite e gate posterior depende da promessa/critério ratificado. Não requer unanimidade de modelos; review deve examinar evidência.

### Dependências e paralelismo

DEC-N5 e comparação do diff final governam preparação. Review/capacidade do CI aplicável governam integração, sem exigir toda M1 nem nova decisão de billing onde execuções já são possíveis. A autorização do usuário nesta conversa é para auditoria e delegação, não publicação GitHub.

### Plano e aceite propostos

Escolher variante e recorte; mapear testes/bytes/ações; registrar gaps Windows/Compose/ações integrais; preparar descrição com controles de cópia e encaminhamento; solicitar publicação apenas em tarefa autorizada de implementação. Critério da decisão: escolha atribuída com gates proporcionais e destino dos resíduos. Critério do produto continua mudança integrada e provada.

### Comunicação entre responsáveis

Na futura PR, separar prova local de CI e Windows; não somar seis casos argv a dez casos e2e como se fossem um mesmo patch. Explicar que o aceite G2 foi retirado por objeto distinto.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Trocar a variante sem repetir a comparação aplicaria recibos de um patch a outro; esperar o tooling G2 atrasaria a correção por uma relação falsa. Que caso o teste ainda não cobre? — O teste integral cobre só a ação e2e em macOS com stubs; smoke, tail-outlier, Windows e Compose real seguem fora, e nenhuma PR foi criada por esta auditoria. Como eu explicaria isso para outro pod? — C2/G2 saiu da cadeia porque testou outro objeto; a decisão é qual candidato submeter e como dividir o diff, e publicar e integrar continuam etapas distintas.

### Próxima ação e encerramento

Usuário/autor candidato e mantenedor a confirmar: receber inventário por hash e decidir destino. Saída verificável: decisão e pacote revisável; nenhuma publicação ou merge por esta ficha.

<a id="item-112"></a>

## DEC-N5 — Binding posicional do runner ON (#167)

Frente: decisoes_candidatos_locais. Encaminhamento: ratificar_binding_por_variante_e_compatibilidade.

### Identidade e estado

DEC-N5 — Binding posicional do runner ON (#167). Decisão ainda não ratificada; responsáveis específicos a confirmar. A auditoria recomenda sem decidir pelo mantenedor.

### Intenção e benefício

Escolher contrato de argumentos que aceite a chamada nomeada do harness e trate chamadas posicionais deliberadamente, sem transformação silenciosa de intenção.

### Feito, faltante e não comprovado

A main não declara EnvFile/AdditionalComposeFile. O candidato conjunto adiciona ambos com binding false; a variante posterior mantém binding padrão, atribuindo posições adicionais conforme relato argv. O pacote Windows exige false. Portanto a frase anterior patch testado usa binding padrão é ambígua: existem dois patches testados em escopos distintos.

### Linhagem

#167 → incompatibilidade de parâmetros → variante conjunta 1122d031 e variante PATCH-167.diff → recibos separados → DEC-N5 ainda pendente. Nenhuma escolha de um parecer anterior é ratificação do mantenedor.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 300. Releitura de 17/10/2026 dos candidatos CL-01, CL-03; suas fontes primárias/hashes estão relacionadas abaixo e em CAPTURA-E-INTEGRIDADE.json. Código APEX fixado em c3c3ea3; execuções históricas conservam suas datas.

### Classe e limite da evidência

FATO OBSERVADO: conteúdo estático e identidade dos artefatos. RELATO HISTÓRICO: resultados de execução, sem reexecução. INFERÊNCIA: riscos condicionais. PROPOSTA: critérios futuros. DECISÃO PENDENTE: opção e owner, sem nova autorização funcional.

### Fluxo

Callsite → sequência de argumentos → binder PowerShell → Scenario/EnvFile/overlays → Compose argv. Contrato de chamadas externas precisa sobreviver à escolha; mais de um overlay via array em processo não equivale ao transporte por pwsh -File.

### Consequências e risco

Binding padrão pode aceitar um argumento extra como EnvFile; false pode recusar chamada posicional legada. O corpus consultado na prova argv não achou callsite posicional, mas isso não demonstra ausência de consumidores externos.

### Alternativas e recomendação

Manter padrão, nomeados obrigatórios ou compatibilidade posicional explicitamente limitada são alternativas. Escolher a política com base no corpus e promessa pública. Não declarar false obsoleto para todo candidato nem promover default a opção já aprovada.

### Dependências e paralelismo

Inventário de callsites e contrato legado precedem alteração final; a decisão não depende de #175 ou do tooling G2. Ajustar fixtures Windows ao mesmo artefato escolhido, sem aproveitar hashes antigos após mudança.

### Plano e aceite propostos

Enumerar chamadas nomeadas, Scenario legado, segundo argumento inesperado, múltiplos overlays e caminhos especiais; registrar aceitar/recusar antes do teste. Controles futuros devem detectar argumento perdido, reordenação e rebinding indevido. Aceite: política documentada e resultados ligados ao hash final; receipt de outra variante não satisfaz o critério.

### Comunicação entre responsáveis

Explicar compatibilidade preservada/removida e como o operador passa um ou vários overlays. Mostrar argv e efeito observável, sem expor conteúdo de configuração.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Com binding padrão, uma segunda palavra posicional pode virar EnvFile sem aviso; com binding false, uma chamada posicional legada pode ser recusada. Que caso o teste ainda não cobre? — Há seis testes argv na linhagem consultada; conferir a adequação por variante, múltiplos overlays e Windows. Não transferir o e2e do candidato com binding false ao PATCH com binding padrão. Como eu explicaria isso para outro pod? — A decisão escolhe entre manter o padrão, exigir nomeados ou limitar a compatibilidade posicional; um array de overlays em processo não equivale ao transporte por pwsh -File.

### Próxima ação e encerramento

Owner Package/Harness a confirmar: decidir política a partir dos callsites e contratos; saída matriz de binding ratificada e critérios do candidato final. Encerrar decisão separadamente da implementação e da prova Windows.

<a id="item-113"></a>

## DEC-N3 — Escopo da #164 e da correção de texto (predict.py, models.py)

Frente: decisoes_candidatos_locais. Encaminhamento: decidir_diff_textual_com_guarda_e_sem_promessa_runtime.

### Identidade e estado

DEC-N3 — Escopo da #164 e da correção de texto (predict.py, models.py). Decisão ainda não ratificada; responsáveis específicos a confirmar. A auditoria recomenda sem decidir pelo mantenedor.

### Intenção e benefício

Escolher como corrigir os textos de Verify sem misturar revisão documental com novo cálculo de W ou garantia de persistência.

### Feito, faltante e não comprovado

CL-02 altera dois pontos de predict.py; models.py e a guarda que exige sua frase antiga ficam fora. DDL declara executor_run_time_ms, mas a redação stored do patch pode sugerir observação de dados que não existe neste recorte. #164 só Markdown não cobre automaticamente o novo diff Python.

### Linhagem

#164 de docs → CL-02 local → contradições predict/models e guarda → DEC-N3 → pequena mudança futura. #179 é estudo measured/estimated, não condição para corrigir as frases.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 174. Releitura de 17/10/2026 dos candidatos CL-02; suas fontes primárias/hashes estão relacionadas abaixo e em CAPTURA-E-INTEGRIDADE.json. Código APEX fixado em c3c3ea3; execuções históricas conservam suas datas.

### Classe e limite da evidência

FATO OBSERVADO: conteúdo estático e identidade dos artefatos. RELATO HISTÓRICO: resultados de execução, sem reexecução. INFERÊNCIA: riscos condicionais. PROPOSTA: critérios futuros. DECISÃO PENDENTE: opção e owner, sem nova autorização funcional.

### Fluxo

Fonte normativa de schema + consumo atual → redação coerente → detail ao usuário e comentários ao mantenedor → guarda correspondente. Fórmula e consulta de dados não mudam por esta decisão.

### Consequências e risco

Escolher apenas embalagem sem inventariar os três textos deixa erro parcial. Confundir declarado com armazenado ou medido cria nova promessa indevida. Impacto textual, sem incidente de cálculo comprovado.

### Alternativas e recomendação

Ampliar #164, PR própria pequena ou follow-up temporário explícito. Recomenda-se menor diff completo com guarda, evitando alteração matemática; escolha pertence ao mantenedor. Adiar estudo de W não exige manter afirmação falsa sobre schema.

### Dependências e paralelismo

Nenhuma dependência de escritor, migração ou #117 para a correção textual. O diff final define verificações aplicáveis; decisão de billing não é predecessor universal da redação/revisão.

### Plano e aceite propostos

Revisar docstring, detail e comentário; preferir coluna declarada e não consumida pelo predictor; atualizar asserção estática com propósito preservado; conferir exemplo de saída quando implementado. Negativo deve detectar retorno da frase falsa; cálculo permanece igual. Aceite: três locais e guarda coerentes, diff/recibo ligados à ref final.

### Comunicação entre responsáveis

Explicar coluna no DDL, schema aplicado e medição do predictor como dimensões separadas. Na PR indicar que o estudo funcional #179 não foi implementado.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Mudar a fórmula junto com o texto misturaria correção editorial com decisão de modelo da #179, e trocar uma frase falsa por stored criaria nova promessa de persistência não observada. Que caso o teste ainda não cobre? — Se só predict.py mudar, o comentário de models.py continua errado, e a asserção da matriz que exige a frase antiga continua presa a ela; a #164 só de Markdown não cobre o diff Python. Como eu explicaria isso para outro pod? — Coluna declarada no DDL, schema aplicado e consumo pelo predictor são dimensões separadas; a decisão é o escopo e a embalagem da correção dos três textos com a guarda, sem prometer runtime.

### Próxima ação e encerramento

Mantenedor e owner Verify a confirmar: selecionar destino e revisar redação completa. Saída: decisão de escopo e patch posterior proporcional; encerrar por integração ou follow-up explícito, sem alegar prova runtime.

<a id="item-114"></a>

## PROP-D09-MAIN-TEST — [Test][Loader] Suíte de testes unitários em main_test.go para eventlog-loader (TS11)

Frente: externo_dataship. Encaminhamento: externo_reconciliar_candidato_de_testes.

### Identidade e estado

PROP-D09-MAIN-TEST — [Test][Loader] Suíte de testes unitários em main_test.go para eventlog-loader (TS11). Tipo test; pods laboratorio; origens D09. Minuta de 11/10/2026; executor histórico registrado na triagem: G-gemini, sem nova designação de responsável. Escopo externo Gabriel-Philot/dataship-spark-plat-v0. Nenhuma publicação desta minuta demonstrada no ledger consultado; estado atual upstream não verificado. Owner externo a confirmar.

### Intenção e benefício

Proteger helpers do eventlog-loader com uma suíte rápida em Go antes de refatorar D02. O ganho pretendido é detectar regressões de decodificação sem exigir um cluster para cada alteração.

### Feito, faltante e não comprovado

A minuta registra TS11, commit abreviado 8ca806a sobre a PR externa #2/dbbf4cb, oito testes e onze mutantes de helpers. Esse relato de candidato contradiz a leitura literal de que nada foi feito. Não inspecionei o patch nem seus recibos; readEventLog, roteamento G01/G02 e E2E continuam fora da cobertura anunciada.

### Linhagem

D09 → TS11 relatada → candidato 8ca806a sobre dbbf4cb → minuta de publicação após #2. Sem vínculo de merge, CI do head, review ou adoção atual demonstrado neste recorte. Preservar D02 como consumidor possível dessa proteção, sem confundir #2 externa com issue APEX.

### Fontes e corte

Minuta original preservada em fontes/batch-proposals-review-sources/PROP-D09-MAIN-TEST.md; MATRIX.json, proposals[key=PROP-D09-MAIN-TEST]; PUBLICATION.json, items/dispositions, verificado historicamente em 11/10/2026 04:25:48 UTC. Fontes adicionais lidas: o conteúdo e a reconciliação dos dois ledgers citados. SHA-256 da cópia da minuta em fontes/batch-proposals-review-sources/SOURCE-MANIFEST.json. A leitura desta ficha é de 17/10/2026; datas de snapshot não são atualização online nesta rodada.

### Classe e limite da evidência

FATO OBSERVADO: a minuta contém os números e as exclusões. RELATO HISTÓRICO: testes/mutantes e commits. PROPOSTA: submeter a suíte após reconciliar a base. Nenhuma execução independente comprova os resultados citados.

### Fluxo

Eventos/entradas controladas → helpers Go → valores esperados; alteração negativa do helper → teste deve falhar. Esse fluxo é o desenho da prova offline. MinIO→readEventLog→roteamento→ClickHouse é outra prova, explicitamente excluída.

### Consequências e risco

Uma refatoração pode preservar os testes dos helpers e quebrar a leitura/roteamento não exercitados. O risco decorre da fronteira declarada; não é regressão observada nem razão para vender a suíte como proteção integral.

### Alternativas e recomendação

Recomendo localizar e revisar o candidato existente. Integrar os testes sobre base reconciliada ou reaplicar apenas os casos ainda úteis são opções; criar uma suíte concorrente perde a linhagem. Acrescentar readEventLog deve ser folha distinta quando o risco a justificar.

### Dependências e paralelismo

Depende de acesso ao candidato e decisão do mantenedor externo. Merge da #2 era condição histórica, a reconfirmar; revisão dos testes e desenho de D02 podem começar em paralelo. Não é gate da v1 APEX.

### Plano e aceite propostos

Fixar base/head reais do candidato; mapear oito casos ao comportamento de cada helper; conferir controles negativos e gaps G01/G02; retirar duplicatas com testes atuais. Menor entrega: patch de teste reconciliado e recibo futuro de go test/go vet com versão/árvore. Aceite: mutação relevante falha pelo motivo esperado, controle íntegro passa, escopo excluído documentado; quantidade de testes não é critério suficiente.

### Comunicação entre responsáveis

Em eventual PR externa, citar TS11/D09, base, helpers protegidos e exclusões. Oito testes/onze mutantes são relato até confrontar os arquivos; não anunciar E2E ou aprovação APEX.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Refatorar o eventlog-loader antes de caracterizar os helpers deixaria a D02 sem rede de proteção, e criar uma suíte concorrente perderia a linhagem do candidato TS11 existente. Que caso o teste ainda não cobre? — readEventLog, o roteamento G01/G02 e o E2E ficam fora da cobertura anunciada; os oito testes e onze mutantes sobre 8ca806a são relato, e o patch não foi inspecionado aqui. Como eu explicaria isso para outro pod? — A suíte protege helpers Go de decodificação, não o pipeline integrado MinIO→ClickHouse; é proposta externa ao Dataship, e o merge da PR #2 é condição histórica a reconfirmar.

### Próxima ação e encerramento

Owner externo a confirmar: entrada candidato TS11 e estado da PR #2; saída inventário caso→comportamento→controle e decisão de integração. Encerrar a minuta após adoção/rejeição fundamentada no repositório de destino, preservando lacunas em IDs próprios.

<a id="item-115"></a>

## PROP-D02-LOADER-MODULARIZATION — [Tooling][Dataship] Refatoração modular do eventlog-loader por responsabilidade (D02)

Frente: externo_dataship. Encaminhamento: externo_estudar_refatoracao_delimitada.

### Identidade e estado

PROP-D02-LOADER-MODULARIZATION — [Tooling][Dataship] Refatoração modular do eventlog-loader por responsabilidade (D02). Tipo tooling; pods laboratorio; origens D02. Minuta de 11/10/2026; executor histórico registrado na triagem: G-gemini, sem nova designação de responsável. Proposta externa Dataship; nenhuma adoção atual demonstrada. Mantenedor upstream decide fronteiras; a atribuição histórica ao executor da minuta não o torna owner do loader.

### Intenção e benefício

Reduzir acoplamento entre leitura, decodificação, batching e inserção do eventlog-loader para facilitar evolução sem alterar os dados produzidos.

### Feito, faltante e não comprovado

As 582 linhas de main.go e a falta de testes Go pertencem ao diagnóstico histórico. D09 já descreve um candidato de testes; por isso não repetir ausência absoluta de trabalho. A minuta define equivalência funcional e exclui DDL/protocolo MinIO, mas não apresenta decomposição nem prova de equivalência.

### Linhagem

D02 registrado → minuta modularização; D09/TS11 é proteção proposta antes do delta. Não há implementação, commit de refatoração, review ou aceite atual rastreado aqui. D03–D06 são extensões futuras, não prova de necessidade de todos os módulos.

### Fontes e corte

Minuta original preservada em fontes/batch-proposals-review-sources/PROP-D02-LOADER-MODULARIZATION.md; MATRIX.json, proposals[key=PROP-D02-LOADER-MODULARIZATION]; PUBLICATION.json, items/dispositions, verificado historicamente em 11/10/2026 04:25:48 UTC. Fontes adicionais lidas: o conteúdo e a reconciliação dos dois ledgers citados. SHA-256 da cópia da minuta em fontes/batch-proposals-review-sources/SOURCE-MANIFEST.json. A leitura desta ficha é de 17/10/2026; datas de snapshot não são atualização online nesta rodada.

### Classe e limite da evidência

FATO OBSERVADO: recorte da minuta. RELATO HISTÓRICO: tamanho/estrutura do loader. PROPOSTA: modularizar preservando comportamento. INFERÊNCIA: melhor separação pode reduzir custo de manutenção; benefício não medido.

### Fluxo

Fonte de log → leitor → decodificador → lote → escritor ClickHouse. Separar essas responsabilidades é fluxo proposto, mantendo entradas/saídas, ordem, erros e política de flush que a base real demonstrar.

### Consequências e risco

Uma extração ampla pode mudar buffering, ordenação ou propagação de erro mesmo com nomes idênticos. Confiança alta no risco geral da fronteira, sem defeito observado. O número de linhas não estabelece sozinho a prioridade.

### Alternativas e recomendação

Recomendo caracterizar e extrair uma responsabilidade de cada vez. Alternativas: permanecer no mesmo pacote com funções menores; criar pacotes apenas onde há dependências separáveis; manter a estrutura se a demanda não justificar o custo. Evitar interface genérica antes de haver segundo consumidor.

### Dependências e paralelismo

A implementação requer base atual e proteção adequada D09 ou equivalente aceita. Inventário de responsabilidades e decisão de design podem ocorrer antes do merge de D09. D03–D06 não devem obrigar refatoração completa se uma extensão menor for revisável.

### Plano e aceite propostos

Mapear efeitos e dependências; escolher primeiro seam; registrar entradas, saídas, erros e invariantes; extrair sem mudar DDL; comparar resultados antes/depois sobre fixtures representativas. Negativos propostos: erro no decoder, falha no writer, lote parcial e EOF. Aceite: equivalência observável e teste que detecte mudança indevida de flush/erro, com rollback por extração pequena.

### Comunicação entre responsáveis

Explicar por que a fronteira escolhida reduz acoplamento e o que continua igual. Na PR externa separar refatoração de nova tabela e declarar o alcance dos testes, sem transferir evidência APEX.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Mudar o batching junto com a extração dos módulos poderia alterar buffering, ordenação ou propagação de erro mesmo com nomes idênticos. Que caso o teste ainda não cobre? — Os casos e a cobertura necessários para preservar o comportamento precisam de conferência no diff e no conjunto de testes escolhidos; não foram comprovados nesta revisão da proposta. Como eu explicaria isso para outro pod? — A refatoração separa leitor, decodificador, lote e escritor uma responsabilidade por vez, mostrando o mesmo evento antes e depois; DDL e protocolo MinIO ficam fora e não é condição da v1 APEX.

### Próxima ação e encerramento

Mantenedor Dataship a confirmar: receber mapa atual e cobertura disponível; devolver decisão e primeira extração delimitada. Encerrar apenas após equivalência revisada/integração ou adiamento explícito, sem tornar este refactor condição automática da v1 APEX.

<a id="item-116"></a>

## PROP-D03-SPARK-JOBS — [Feature][Dataship] Ingestão da entidade spark_jobs no ClickHouse (D03)

Frente: externo_dataship. Encaminhamento: externo_adiar_implementacao_e_definir_contrato.

### Identidade e estado

PROP-D03-SPARK-JOBS — [Feature][Dataship] Ingestão da entidade spark_jobs no ClickHouse (D03). Tipo feature; pods laboratorio; origens D03. Minuta de 11/10/2026; executor histórico registrado na triagem: G-gemini, sem nova designação de responsável. Feature externa Dataship; estado atual da tabela/loader não reinspecionado. Owner de schema/loader upstream a confirmar.

### Intenção e benefício

Representar jobs para relacionar início/fim, estágios e execução de uma carga. Isso permitiria análise no nível de job que o registro histórico considerava ausente.

### Feito, faltante e não comprovado

A minuta propõe spark_jobs a partir de SparkListenerJobStart/End e menciona seis tabelas na base histórica. Não comprova que a tabela ainda falte. DDL e parsing não foram fornecidos como entrega integrada neste recorte; cardinalidade, eventos parciais e identidade ainda precisam contrato.

### Linhagem

D03 no registro → minuta spark_jobs → dependências históricas D02/D09. Sem issue/PR própria comprovada no ledger. D04 acrescentaria vínculos SQL; D06 contexto de aplicação. Essas conexões são desenho, não cadeia de commits existente.

### Fontes e corte

Minuta original preservada em fontes/batch-proposals-review-sources/PROP-D03-SPARK-JOBS.md; MATRIX.json, proposals[key=PROP-D03-SPARK-JOBS]; PUBLICATION.json, items/dispositions, verificado historicamente em 11/10/2026 04:25:48 UTC. Fontes adicionais lidas: o conteúdo e a reconciliação dos dois ledgers citados. SHA-256 da cópia da minuta em fontes/batch-proposals-review-sources/SOURCE-MANIFEST.json. A leitura desta ficha é de 17/10/2026; datas de snapshot não são atualização online nesta rodada.

### Classe e limite da evidência

FATO OBSERVADO: proposta de tabela e parser. RELATO HISTÓRICO: lacuna entre SQL/job/stage/task. DECISÃO PENDENTE: schema, chave e utilidade atual. Não há inserção ClickHouse observada nesta revisão.

### Fluxo

JobStart/JobEnd → parser do loader → registro spark_jobs → consulta por job e stages. Fluxo proposto: precisa preservar app_id no escopo da chave para não confundir IDs locais de jobs entre aplicações.

### Consequências e risco

Uma tabela sem chave contextual pode fundir jobs diferentes ou preencher duração quando só existe um evento. Impacto possível em correlação; frequência desconhecida. Uma tabela nova aumenta manutenção do DDL e do parser.

### Alternativas e recomendação

Recomendo confirmar demanda e desenhar a representação mínima. Comparar tabela derivada persistente com consulta sobre eventos brutos; a primeira facilita consulta, a segunda evita novo estado mas pode custar mais leitura. Escolher após amostra e consumo alvo.

### Dependências e paralelismo

Desenho pode correr em paralelo a D02/D09. Implementação depende de interfaces de loader e schema acordadas, não necessariamente de toda refatoração. D04 depende da identidade resultante, não impede a primeira caracterização.

### Plano e aceite propostos

Inventariar schema atual; identificar consumidor; especificar chave, campos opcionais e associação a stages; preparar fixtures Start/End completos, End ausente, duplicata, ordem invertida e mesmo job_id em apps diferentes. Entrega mínima futura: DDL e parser do mesmo contrato, com resultado determinístico e preservação de tabelas existentes. Prova de escrita real deve ter recibo separado da decodificação offline.

### Comunicação entre responsáveis

Na proposta upstream, mostrar um job completo e um parcial, explicar campos ausentes e o vínculo com D04. Não chamar o desenho de hierarquia SQL já completa.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Usar só job_id como chave fundiria jobs de aplicações diferentes, e preencher duração com um único evento produziria valores sem base. Que caso o teste ainda não cobre? — Conferir os casos de execução e identidade que a proposta pretende suportar, incluindo ausência de dados; implementação e cobertura não foram comprovadas neste recorte. Como eu explicaria isso para outro pod? — spark_jobs representaria o job a partir de JobStart/JobEnd, com app_id na chave; job e execução SQL são entidades diferentes, e o vínculo SQL fica na D04.

### Próxima ação e encerramento

Owner Dataship a confirmar: entrada schema/eventos do commit escolhido; saída contrato mínimo e decisão adotar/adiar. Encerramento exige integração/prova acordada se adotado, ou registro de rejeição; nenhuma ação APEX automática.

<a id="item-117"></a>

## PROP-D04-SPARK-SQL-EXECUTION-JOBS — [Feature][Dataship] Mapeamento relacional spark_sql_execution_jobs (D04)

Frente: externo_dataship. Encaminhamento: externo_estudar_vinculo_sql_job.

### Identidade e estado

PROP-D04-SPARK-SQL-EXECUTION-JOBS — [Feature][Dataship] Mapeamento relacional spark_sql_execution_jobs (D04). Tipo feature; pods laboratorio; origens D04. Minuta de 11/10/2026; executor histórico registrado na triagem: G-gemini, sem nova designação de responsável. Feature externa Dataship ligada a D04; nenhum estado atual upstream inferido. Owner de schema/loader a confirmar.

### Intenção e benefício

Permitir seguir uma execução SQL até seus jobs por uma relação explícita, sem usar proximidade temporal como identidade.

### Feito, faltante e não comprovado

A minuta chama a relação de N:M e pede pares execution_id/job_id determinísticos. Isso é escolha de modelagem proposta, não cardinalidade provada pelos eventos lidos nesta rodada. Falta identificar a fonte do vínculo, seu escopo por aplicação e representação de jobs sem SQL.

### Linhagem

D04 → minuta de tabela de junção → D03 como antecedente de modelo. D07 é extração de plano, excluída. Não há schema/commit/PR/review demonstrado para essa tabela; nenhuma ligação automática com a atribuição APEX #115 é estabelecida.

### Fontes e corte

Minuta original preservada em fontes/batch-proposals-review-sources/PROP-D04-SPARK-SQL-EXECUTION-JOBS.md; MATRIX.json, proposals[key=PROP-D04-SPARK-SQL-EXECUTION-JOBS]; PUBLICATION.json, items/dispositions, verificado historicamente em 11/10/2026 04:25:48 UTC. Fontes adicionais lidas: o conteúdo e a reconciliação dos dois ledgers citados. SHA-256 da cópia da minuta em fontes/batch-proposals-review-sources/SOURCE-MANIFEST.json. A leitura desta ficha é de 17/10/2026; datas de snapshot não são atualização online nesta rodada.

### Classe e limite da evidência

FATO OBSERVADO: escopo da minuta. PROPOSTA: tabela e decodificador. DECISÃO PENDENTE: cardinalidade e fonte. INFERÊNCIA a evitar: SQLExecutionStart, sozinho, provar todos os jobs vinculados.

### Fluxo

Evento com propriedade explícita de execução + identidade contextual do job → relação persistida → consulta SQL→jobs. O fluxo é proposto; ausência ou conflito de vínculo deve permanecer representável, não ser resolvido por timestamp aproximado.

### Consequências e risco

Vínculo inferido indevidamente pode atribuir custo e falhas ao SQL errado. Confiança na possibilidade, sem ocorrência medida; o dano é maior que uma relação ausente explicitamente marcada.

### Alternativas e recomendação

Recomendo relação derivada apenas de campos observáveis. Comparar tabela de junção, coluna na entidade job ou cálculo em leitura; a cardinalidade comprovada e o suporte a conflitos devem governar a escolha. Manter unknown é preferível a inventar associação.

### Dependências e paralelismo

Contrato de identidade D03 é dependência da implementação. Análise dos eventos e casos pode começar em paralelo; D07 não é gate. Não transportar políticas APEX #115 para Dataship sem comparação explícita.

### Plano e aceite propostos

Localizar eventos/campos que sustentam o vínculo; documentar cardinalidade e escopo; especificar ausência/conflito; propor DDL e parsing mínimos. Casos: SQL com vários jobs, job sem SQL, IDs repetidos entre apps, vínculo duplicado e referências conflitantes. Aceite: relações só com origem rastreável, idempotência acordada e consulta que não mistura aplicações; escrita real separada do teste sintético.

### Comunicação entre responsáveis

Explicar qual campo autoriza cada aresta e como o leitor vê ausência. Não resumir “tabela N:M” como prova de auditoria ponta a ponta.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Ligar execução SQL e job por proximidade temporal poderia atribuir custo e falhas ao SQL errado; vínculo ausente explicitamente marcado é melhor que associação inventada. Que caso o teste ainda não cobre? — Conferir associação ambígua, ausência e multiplicidade com exemplos identificados; os controles propostos não foram comprovados neste recorte. Como eu explicaria isso para outro pod? — Cada aresta da relação precisa mostrar o campo observável que a autoriza, com escopo de aplicação; SQLExecutionStart sozinho não prova todos os jobs vinculados.

### Próxima ação e encerramento

Mantenedor externo a confirmar: entrada eventos e contrato D03; saída decisão de chave/cardinalidade e proposta revisável. Encerrar após adoção validada ou rejeição fundamentada, preservando a possibilidade de concluir estudo sem implementar.

<a id="item-118"></a>

## S01 — task_time_ms=0 para run não indexado

Frente: Pod 3/Serve+Pod 1/Front. Encaminhamento: ENCERRAR_CORRECAO_INTEGRADA.

### Identidade e estado

S01 — task_time_ms=0 para run não indexado. Tipo: correção; frente: Pod 3/Serve+Pod 1/Front. PUBLICATION registra already_corrected; #129 integrada. Sem nova issue própria. O autor de um artefato não é automaticamente o responsável pelo próximo passo.

### Intenção e benefício

Distinguir trabalho não indexado de uma medição real igual a zero no resumo de runs; evita que o usuário conclua economia ou ausência de custo a partir de um default do JOIN.

### Feito, faltante e não comprovado

O diagnóstico antigo de ifNull que nunca dispara foi superado: _run_rollup_sql declara indexed=1 nas linhas reais e produz -1 quando o LEFT JOIN não encontra run_outcomes; a cópia Front segue o sentinel. Não se repetiu SQL real nem browser. O fechamento documental não certifica todas as rotas da Console.

### Linhagem

S01 → correção dentro da linhagem #129 → PUBLICATION already_corrected. O registro do problema em fab6620 continua histórico; não é prova de persistência do defeito em c3c3ea3. S02/#156 conserva a prova de API e S03/S04 o perfil nginx/browser; não há nova PR S01 a publicar.

### Fontes e corte

Fontes efetivamente lidas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; fontes/lote2-serve__src__apex_mcp__ch.py.txt; fontes/lote2-front__src__data__queries.ts.txt; fontes/main-repository.txt. Registro histórico preservado até 01/10; reconciliação/publicação de 11/10; snapshots públicos de 16/10/2026. Código, quando citado, refere-se à main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. As fontes de narrativa não substituem o código/recibo identificado.

### Classe e limite da evidência

FATO OBSERVADO: o conteúdo e os estados documentais discriminados nos campos 3–5. RELATO HISTÓRICO: resultados atribuídos a autores/recibos, sem reexecução nesta auditoria. INFERÊNCIA: consequências condicionais do campo 8. PROPOSTA: alternativas e plano abaixo. DECISÃO PENDENTE: escolhas humanas explicitadas. Teste local, CI em um head, integração e aprovação humana conservam escopos separados.

### Fluxo

Observado estaticamente: spark_events identifica run → LEFT JOIN run_outcomes → indexed distingue presença → task_time_ms=-1 para ausência → adapter da Console representa indisponibilidade. Zero de linha realmente indexada continua zero.

### Consequências e risco

Regredir para ifNull sobre coluna não nullable poderia transformar ausência em zero medido; confiança alta no mecanismo estático, incidência atual não demonstrada.

### Alternativas e recomendação

Manter sentinel explícito é a menor solução já integrada. join_use_nulls=1 mudaria a configuração da consulta e o contrato de credenciais readonly; não há motivo demonstrado para substituir o mecanismo agora.

### Dependências e paralelismo

S01 pode ser encerrado documentalmente independentemente de #117 ou da decisão Ask. Provas futuras de apresentação pertencem ao recorte S04; não reabrir esta correção só porque um teste de browser falta.

### Plano e aceite propostos

Conciliar a linha histórica com o código atual e registrar dois controles de preservação para futura alteração: run sem índice conserva ausência; run indexado com valor zero conserva zero. Aceite deste ID: destino already_corrected e referência ao sentinel, sem alegar execução nova. Se surgir contraexemplo, abrir resíduo delimitado.

### Comunicação entre responsáveis

Explicar no registro que a mudança representa ausência, não uma otimização de task_time_ms; citar os dois produtores SQL e o consumidor, preservando a reprodução antiga com seu head.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Usar zero como ausência faria o resumo de runs mostrar economia ou custo nulo a partir de um default do LEFT JOIN, e voltar a ifNull sobre coluna não nullable reintroduziria esse efeito. Que caso o teste ainda não cobre? — Nenhum browser nem SQL real foi executado: a apresentação do sentinela na Console fica no recorte S04, e o fechamento documental não certifica todas as rotas. Como eu explicaria isso para outro pod? — _run_rollup_sql marca indexed=1 nas linhas reais e produz -1 quando falta run_outcomes, e o Front segue esse sentinela; zero de linha indexada continua sendo medição zero.

### Próxima ação e encerramento

Owner Front/Serve a confirmar: entrada PUBLICATION e os dois rollups em c3c3ea3; saída nota de reconciliação S01 encerrada no catálogo. Encerramento não requer recriar patch ou executar o pipeline.

<a id="item-119"></a>

## S02 — Queries da #129 contra ClickHouse real

Frente: Pod 3/Serve. Encaminhamento: AGRUPAR_RECONCILIAR_PROVA_EXISTENTE.

### Identidade e estado

S02 — Queries da #129 contra ClickHouse real. Tipo: runtime; frente: Pod 3/Serve. #156 aberta sem assignee no snapshot; #129 integrada; #157–#159 abertas. O autor de um artefato não é automaticamente o responsável pelo próximo passo.

### Intenção e benefício

Demonstrar que as queries e rotas Serve operam sobre ClickHouse real, além de fake clients, sem pedir uma repetição cega de toda a API.

### Feito, faltante e não comprovado

PUBLICATION reuse_existing absorveu S02 na #156. O corpo público registra G1-F1c real 19 PASS/0 FAIL no blob 3e0b3bbe e transporte real dos oito tools com blobs de API/MCP declarados idênticos; são recibos relatados, não execuções desta revisão. A main pós-integração e browser não estão cobertos automaticamente. Falta reconciliação após a decisão de merge.

### Linhagem

S02 nasce do resíduo de #129/fab6620 → provas posteriores registradas em #156 → gate #159 e testes #157/#158 → revisão/integração pendentes. Prova de transporte anterior não certifica F1c; o gate F1c tem recibo próprio. Não criar issue duplicada pela minuta antiga.

### Fontes e corte

Fontes efetivamente lidas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; fontes/batch-rest-issues-sources/issue-156.md; fontes/pr159-files.json; fontes/pr159-checks.json. Registro histórico preservado até 01/10; reconciliação/publicação de 11/10; snapshots públicos de 16/10/2026. Código, quando citado, refere-se à main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. As fontes de narrativa não substituem o código/recibo identificado.

### Classe e limite da evidência

FATO OBSERVADO: o conteúdo e os estados documentais discriminados nos campos 3–5. RELATO HISTÓRICO: resultados atribuídos a autores/recibos, sem reexecução nesta auditoria. INFERÊNCIA: consequências condicionais do campo 8. PROPOSTA: alternativas e plano abaixo. DECISÃO PENDENTE: escolhas humanas explicitadas. Teste local, CI em um head, integração e aprovação humana conservam escopos separados.

### Fluxo

Fluxo relatado: fixtures próprias em ClickHouse → CLI/API e MCP → respostas/asserções → cleanup de oito tabelas e controle preservado. Fluxo futuro: comparar árvore integrada com blobs provados → executar apenas diferença material.

### Consequências e risco

Ignorar recibos existentes desperdiça execução; transferi-los para blobs alterados pode mascarar regressão. Não há falha atual de query demonstrada nesta ficha.

### Alternativas e recomendação

Reutilizar a evidência delimitada e revisar diferenças é recomendado. Reexecutar tudo só se a alteração da árvore invalidar o escopo; aceitar apenas fake clients não satisfaz a intenção de prova real original.

### Dependências e paralelismo

Decisão de integração da #156/#159 e comparação de blobs; não depende de completar Ask, #117 ou todo o marco M1. Inventário de provas pode ocorrer já. Runtime residual depende de ambiente e autorização próprios.

### Plano e aceite propostos

Inventariar objeto/comando/fixture/resultado de cada recibo; distinguir G1 de transporte; comparar código com integração escolhida; documentar resíduo e controles. Aceite: consultas relevantes com resultados positivos e ausentes coerentes, falhas sanitizadas e cleanup próprio, mais reconciliação explícita dos critérios de #156. Browser permanece em S04.

### Comunicação entre responsáveis

Na #156, vincular S02 explicitamente, dizer quais blobs receberam prova real e quais só CI; não converter 33 checks individuais em prova integrada ou 19 PASS em cobertura universal.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Se o gate mudar e o recibo antigo for reutilizado, uma regressão pode passar despercebida; ignorar os recibos existentes desperdiçaria execução já feita. Que caso o teste ainda não cobre? — Rotas e parâmetros fora dos blobs provados, a main pós-integração e o browser não estão cobertos; os 19 PASS do G1-F1c e o transporte dos oito tools são relatos de blobs específicos. Como eu explicaria isso para outro pod? — API real com ClickHouse e browser são provas diferentes: S02 cobre queries e rotas Serve, e S04 cobre a tela; 33 checks individuais não são prova integrada.

### Próxima ação e encerramento

Revisor Serve/mantenedor a confirmar: entrada #156, heads #157–#159 e recibos; saída matriz de equivalência/diferenças e decisão de prova residual. Encerrar S02 quando a representação na #156 e a reconciliação exigida estiverem resolvidas, sem nova publicação automática.

<a id="item-120"></a>

## S03 — Build/teste nginx com proxy /v1

Frente: Pod 3+Pod 1. Encaminhamento: AGRUPAR_PROVA_NGINX.

### Identidade e estado

S03 — Build/teste nginx com proxy /v1. Tipo: runtime; frente: Pod 3+Pod 1. #172 aberta; representa S03 e S04. A #129 já foi integrada. O autor de um artefato não é automaticamente o responsável pelo próximo passo.

### Intenção e benefício

Validar a imagem da Console e o proxy same-origin /v1 que o usuário efetivamente acessa. Uma API correta isoladamente não demonstra que a configuração da imagem chega ao upstream.

### Feito, faltante e não comprovado

nginx.conf encaminha /v1/ para ${APEX_API_UPSTREAM}/v1/ e mantém /config.js sem cache. A #172 delimita a lacuna de imagem/proxy após os recibos reais de API da #156. Não foi construído container nesta auditoria, e não se afirma ausência universal de qualquer build histórico.

### Linhagem

Resíduo de #129 → S03 → publicação #172. #156 é prova adjacente de API/MCP/ClickHouse, não substituto do nginx. Faltam árvore/imagem e recibo de tráfego pelo proxy para o recorte pretendido.

### Fontes e corte

Fontes efetivamente lidas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; fontes/batch-public-sources/issue-172.md; fontes/batch-public-sources/front__nginx.conf.txt; fontes/batch-rest-issues-sources/issue-156.md. Registro histórico preservado até 01/10; reconciliação/publicação de 11/10; snapshots públicos de 16/10/2026. Código, quando citado, refere-se à main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. As fontes de narrativa não substituem o código/recibo identificado.

### Classe e limite da evidência

FATO OBSERVADO: o conteúdo e os estados documentais discriminados nos campos 3–5. RELATO HISTÓRICO: resultados atribuídos a autores/recibos, sem reexecução nesta auditoria. INFERÊNCIA: consequências condicionais do campo 8. PROPOSTA: alternativas e plano abaixo. DECISÃO PENDENTE: escolhas humanas explicitadas. Teste local, CI em um head, integração e aprovação humana conservam escopos separados.

### Fluxo

Proposto para prova: browser/curl → nginx da imagem construída → /v1 upstream → API → JSON/401/erro → mesma origem. A substituição de variáveis no entrypoint precisa fazer parte da árvore escolhida.

### Consequências e risco

Erro de upstream, prefixo ou variável pode deixar a Console indisponível apesar de API saudável. Risco plausível de integração; nenhum defeito novo do proxy foi reproduzido.

### Alternativas e recomendação

Provar uma rota representativa e os estados de recusa primeiro reduz custo. Um mock de nginx testa configuração textual, mas não o roteamento da imagem. Uma suíte ampla de tools repetiria escopo S02 sem provar melhor o container.

### Dependências e paralelismo

Definir imagem, commit, portas e recursos próprios; a política de token #171 só bloqueia novas alegações sobre perfil ainda não decidido, não caracterização do comportamento existente. Preparação da matriz pode seguir com S04.

### Plano e aceite propostos

Revisar Dockerfile/entrypoint na ref escolhida; fixar variáveis e digest da imagem; posteriormente comprovar /v1, 401 sem token e upstream indisponível, com diagnóstico distinto de SPA/HTML 200. Preservar evidência sanitizada e remover apenas recursos próprios. Aceite: proxy observado na imagem e limites de rotas explícitos.

### Comunicação entre responsáveis

Apresentar a diferença entre rota API e rota same-origin, listar a configuração usada sem segredos e registrar que curl não certifica renderização S04.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Se /v1 devolver index.html com 200, a Console pareceria funcionar sem chegar à API; erro de upstream, prefixo ou variável pode deixar a Console indisponível com a API saudável. Que caso o teste ainda não cobre? — O curl pelo proxy não cobre renderização, que é o recorte S04; nenhum container foi construído nesta auditoria, e o entrypoint que substitui variáveis precisa estar na árvore escolhida. Como eu explicaria isso para outro pod? — nginx.conf encaminha /v1/ para APEX_API_UPSTREAM; API verde isolada não prova que a configuração da imagem chega ao upstream, por isso o proxy tem prova própria na #172.

### Próxima ação e encerramento

Front/Serve a confirmar: entrada nginx, imagem e perfis; saída plano de ensaio e depois recibo proxy por ref. Encerrar o recorte S03 em #172 ao cumprir o critério de imagem/rota, mantendo S04 separado.

