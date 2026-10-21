# Fichas documentais — lote 11

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-101"></a>

## #125 — [Governance] Protect main with required CI checks and pull-request review

Frente: issues_restantes. Encaminhamento: decidir_protecao_por_contexto_e_filtro.

### Identidade e estado

Issue #125, aberta; assignees: nenhum. Consulta 2026-10-16T18:29:24.609Z. Origens: G02, E15. Responsável futuro a confirmar; disposição decidir_protecao_por_contexto_e_filtro.

### Intenção e benefício

Tornar política de PR/checks/review aplicável na main, sem confundir governança GitHub com feature de análise #21.

### Feito, faltante e não comprovado

Branch snapshot informa protected=false; isso não inventaria sozinho todos os rulesets. O workflow mudou para três jobs principais, com filtros docs/Markdown/JAR; JAR tem workflow próprio. Requisitos históricos de onze contextos precisam ser reconciliados.

### Linhagem

#125/G02/E15 → decisão de checks/reviews/bypass → configuração administrativa futura. #160 alterou CI; #130 é capacidade operacional relacionada. Nenhuma configuração foi aplicada nesta revisão.

### Fontes e corte

Corpo público preservado em fontes/batch-rest-issues-sources/issue-125.md, extraído da consulta de 16/10; comentários do snapshot-20261016. Ficha de origem: ../parte-03-claude-v2/fontes/claude-v2/C02-ISSUES-ABERTAS.md#i-125, linha 32. Código, quando citado, fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Fontes adicionais abaixo; recibo de custódia da #105 é novo em 17/10.

### Classe e limite da evidência

DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Na #105 há verificação própria de arquivo Git, sem executar código de produto; demais execuções não foram realizadas.

### Fluxo

Tipo de mudança → workflow que dispara → contexto de check → regra de merge/review/bypass → caminho de recuperação. A política precisa funcionar também para docs-only/JAR-only.

### Consequências e risco

Exigir um contexto que não é emitido para aquele tipo de PR pode bloquear a fila sem melhorar a prova. Um verde de CI não prova runtime que não foi executado. protected=false não basta para concluir ausência total de regras equivalentes.

### Alternativas e recomendação

Escolher check estável que sempre reporta, adaptar triggers ou regras compatíveis com tipos de PR; comparar bypass emergencial com bloqueio estrito. Não fixar número de reviews/CODEOWNERS sem decisão.

### Dependências e paralelismo

Titular/admin é necessário para aplicar regra. Capacidade de CI afeta sua operação, mas desenho pode avançar com G01 em aberto. Não declarar que todas as PRs esperam regularização financeira, pois há checks verdes observados.

### Plano e aceite propostos

Preparar matriz tipo de PR→trigger→check requerido; revisar docs/JAR-only, falha real, check ausente, verde e bypass. Aceite administrativo conforme issue: regra habilitada, proteção de force-push/deleção e PRs de controle. Esta auditoria não acessou/configurou todos os rulesets.

### Comunicação entre responsáveis

Comunicar exatamente quais checks são exigidos e quais provas continuam externas ao CI. Preservar caminho de emergência auditável.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Exigir um contexto de check que não é emitido para PRs docs-only ou JAR-only bloquearia a fila sem melhorar a prova, e um verde de CI não prova runtime que não rodou. Que caso o teste ainda não cobre? — Esta auditoria não inventariou todos os rulesets, e protected=false não basta para concluir que não há regra equivalente; se o check aparece em toda PR abrangida ainda precisa da matriz tipo de PR → trigger → check. Como eu explicaria isso para outro pod? — A política define quais checks são exigidos, qual bypass emergencial é permitido e como recuperar a verificação depois; CODEOWNERS e número de reviews são escolhas ainda não feitas.

### Próxima ação e encerramento

Mantenedor/admin a confirmar: revisar regra concreta e aplicar quando autorizado. Encerrar apenas com configuração e controles observados; não por minuta ou contagem de jobs.

<a id="item-102"></a>

## #130 — [Governance] Restore GitHub Actions billing for required CI

Frente: issues_restantes. Encaminhamento: reconciliar_bloqueio_historico_e_execucao_por_sha.

### Identidade e estado

Issue #130, aberta; assignees: nenhum. Consulta 2026-10-16T18:29:24.609Z. Origens: G01. Responsável futuro a confirmar; disposição reconciliar_bloqueio_historico_e_execucao_por_sha.

### Intenção e benefício

Restabelecer e demonstrar capacidade de executar CI, distinguindo recusa de runner de falha real dos testes.

### Feito, faltante e não comprovado

Runs históricos registraram bloqueio por billing; há runs posteriores verdes em heads #157–159/#161/#162 e JAR agendado na main. Logo não se sustenta bloqueio universal atual. O estado financeiro não foi consultado. No SHA da main, três runs retornados incluem CI principal falho e JAR schedule verde.

### Linhagem

#130/G01 → bloqueio histórico #126–128 → merges de 06/10 e sucessos posteriores → reconciliação necessária. O corpo original ainda exige reruns de #126–128; substituir isso por um único CI main é mudança de critério a ser decidida, não conclusão desta auditoria.

### Fontes e corte

Corpo público preservado em fontes/batch-rest-issues-sources/issue-130.md, extraído da consulta de 16/10; comentários do snapshot-20261016. Ficha de origem: ../parte-03-claude-v2/fontes/claude-v2/C02-ISSUES-ABERTAS.md#i-130, linha 13. Código, quando citado, fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Fontes adicionais abaixo; recibo de custódia da #105 é novo em 17/10.

### Classe e limite da evidência

DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Na #105 há verificação própria de arquivo Git, sem executar código de produto; demais execuções não foram realizadas.

### Fluxo

Solicitação de run → alocação de runner → checkout/setup/testes → logs/resultados por suíte. Cobrança regularizada, job iniciado e teste aprovado são fatos distintos.

### Consequências e risco

Tratar vermelho sem steps como regressão provoca correção de código indevida. Tratar um verde JAR como todas as lanes aprovadas ou prova de saldo financeiro atual também excede a evidência.

### Alternativas e recomendação

Reconciliar critérios históricos e confirmar condição operacional com titular; escolher ref/prova útil de forma explícita. Não aumentar gasto, rerodar CI ou trocar runner por presunção nesta revisão.

### Dependências e paralelismo

Titular/admin confirma condições operacionais. Revisão de PRs e política #125 podem avançar; uma nova execução depende do meio de prova quando necessário. Não impor bloqueio a toda a fila.

### Plano e aceite propostos

Mapear cada critério original a runs/steps e identificar o que ainda falta ou requer revisão pelo mantenedor após merge. Controle negativo: sem runner/logs não conta como teste; check do SHA errado não prova a árvore alvo. Aceite é critério reconciliado e evidência por suíte.

### Comunicação entre responsáveis

Explicar cronologia com SHAs e workflows, evitando uma frase presente de conta bloqueada baseada só em setembro. Não expor informações financeiras.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Tratar vermelho sem steps como regressão provocaria correção de código indevida, e tratar um verde do JAR como todas as lanes aprovadas, ou como prova de saldo financeiro, excederia a evidência. Que caso o teste ainda não cobre? — Falta ligar cada critério original a runs com steps, suíte e SHA; o que resta dos reruns de #126–#128 e se o CI da main foi ratificado como substituto não foram decididos. Como eu explicaria isso para outro pod? — O bloqueio por billing registrado em setembro não é universal hoje: há verdes posteriores em #157–#159, #161, #162 e no JAR agendado da main; cobrança regularizada, job iniciado e teste aprovado são fatos distintos.

### Próxima ação e encerramento

Titular/mantenedor a confirmar: reconciliar estado/critério e decidir prova restante. Encerrar por critérios públicos atendidos ou explicitamente revisados, sem disparo de CI nesta auditoria.

<a id="item-103"></a>

## #154 — [Test][Pod 2 / Engine] Keep schema preflight aligned with stage queries

Frente: issues_restantes. Encaminhamento: revisar_entrega_publicada_e_residual_de_board.

### Identidade e estado

Issue #154, aberta; assignees: nenhum. Consulta 2026-10-16T18:29:24.609Z. Origens: E20. Responsável futuro a confirmar; disposição revisar_entrega_publicada_e_residual_de_board.

### Intenção e benefício

Manter igualdade entre colunas exigidas pelo preflight e lidas pelas duas queries de stage, usando uma guarda de regressão pequena.

### Feito, faltante e não comprovado

PR #155 está publicada e foi lida nesta Parte04. A caixa de link+board permanece desmarcada porque o link existe mas o board não foi atualizado no relato. Os resultados 46 focados/310 com 11 skips e mutações são relatos locais; checks do head consultado falharam. Não confundir falta de board com falta de publicação.

### Linhagem

#95/#131 (preflight) + #94/#139 (SQL×DDL) → E20/#154 → candidato local 746dc3b → #155 head 561b27e. Igualdade de árvore local/remota é relato da publicação; diff e checks públicos foram lidos.

### Fontes e corte

Corpo público preservado em fontes/batch-rest-issues-sources/issue-154.md, extraído da consulta de 16/10; comentários do snapshot-20261016. Ficha de origem: ../parte-03-claude-v2/fontes/claude-v2/C02-ISSUES-ABERTAS.md#i-154, linha 131. Código, quando citado, fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Fontes adicionais abaixo; recibo de custódia da #105 é novo em 17/10.

### Classe e limite da evidência

DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Na #105 há verificação própria de arquivo Git, sem executar código de produto; demais execuções não foram realizadas.

### Fluxo

SQL das duas queries → extrator existente → conjunto ↔ REQUIRED_SPARK_EVENTS_COLUMNS → asserção bilateral. Isso observa coerência estática, não conexão/schema real.

### Consequências e risco

Remover coluna necessária sem guarda pode passar despercebido; reaproveitar extrator compartilha seus limites de parsing. A presença de 11 skips não deve ser contada como prova runtime.

### Alternativas e recomendação

Revisar pequeno teste e sua evidência; ampliar SHAPE_HISTORY_SQL é decisão separada. Nenhuma necessidade de novo produto ou suite universal decorre do ajuste de board.

### Dependências e paralelismo

Predecessoras já integradas. Prova de integração escolhida precisa da árvore correta; G01 é condição operacional se execução remota for necessária. Mantenedor pode revisar antes de novo CI.

### Plano e aceite propostos

Reconciliar critérios com PR/diff; conferir omissão, coluna extra, query-only e mudança coerente; avaliar evidência hospedada útil e atualizar board quando autorizado. Critérios originais de publicação não devem ser confundidos automaticamente com release; a PR traz Closes para eventual integração.

### Comunicação entre responsáveis

Explicar publicação realizada e estado administrativo restante. Indicar limites do extrator e do alcance das duas queries.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Remover uma coluna necessária do preflight sem a guarda poderia passar despercebido, e o reuso do extrator herda seus limites de parsing. Que caso o teste ainda não cobre? — O relato público identifica c4541a5 e uma árvore local equivalente à remota. Os jobs hospedados sem steps não executaram a suíte; preservar o relato local com seu alcance, sem chamá-lo de prova hospedada nova. Como eu explicaria isso para outro pod? — A PR #155 já está publicada e vinculada; o que resta é a atualização do board, que é estado administrativo e não evidência de teste, e a decisão sobre a contribuição.

### Próxima ação e encerramento

Mantenedor/revisor Engine a confirmar: revisar #155 e reconciliar critérios/board. Encerramento depende da decisão registrada sobre a contribuição; nenhuma mutação GitHub ocorreu aqui.

<a id="item-104"></a>

## #156 — [Test][Pod 3 / Serve] Strengthen transport parity and console findings regression gates

Frente: issues_restantes. Encaminhamento: revisar_integracao_sem_reabrir_provas_delimitadas.

### Identidade e estado

Issue #156, aberta; assignees: nenhum. Consulta 2026-10-16T18:29:24.609Z. Origens: S02, S08, S24. Responsável futuro a confirmar; disposição revisar_integracao_sem_reabrir_provas_delimitadas.

### Intenção e benefício

Acompanhar três contribuições de qualidade: paridade de tools, ordenação e gate Console, com provas corretamente ligadas aos heads/árvores.

### Feito, faltante e não comprovado

#157–159 continuam abertas no snapshot; cada head tem 11 checks antigos verdes e nenhum review formal no endpoint. O corpo registra 572 testes combinados locais, G1-F1c 19 PASS e transporte MCP/HTTP; são relatos com objetos diferentes. #163 adiciona caso plan_json sobre base #157, não foi incorporada automaticamente aos critérios originais.

### Linhagem

#156/S02/S08/S24 → #157/#158/#159 → decisões de integração; #163 é descendente específico. #129/#131/#135/#144/#147 já integradas não são gates futuros. Aceite documental S24 não é aceite retrospectivo de implementação/runtime.

### Fontes e corte

Corpo público preservado em fontes/batch-rest-issues-sources/issue-156.md, extraído da consulta de 16/10; comentários do snapshot-20261016. Ficha de origem: ../parte-03-claude-v2/fontes/claude-v2/C02-ISSUES-ABERTAS.md#i-156, linha 150. Código, quando citado, fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Fontes adicionais abaixo; recibo de custódia da #105 é novo em 17/10.

### Classe e limite da evidência

DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Na #105 há verificação própria de arquivo Git, sem executar código de produto; demais execuções não foram realizadas.

### Fluxo

Diffs independentes → provas locais/por head → review → árvore de integração escolhida → reconciliação com main. Gate F1c, transporte com gate anterior e combinação 572 não são intercambiáveis.

### Consequências e risco

Transferir 33 checks para uma nova árvore ou impor todo limite declarado como novo bloqueador altera o escopo. Rotular API/ClickHouse real como inexistente por falta de browser também ignora evidência delimitada.

### Alternativas e recomendação

Revisar e integrar por PR ou combinação escolhida, revalidando diferenças novas. Browser #172 e positivo plan_json #163 têm escopos próprios quando priorizados; não são critérios universais retroativos da #156.

### Dependências e paralelismo

A decisão de integração e os diffs efetivos governam a prova. G01 não bloqueia genericamente os heads já verdes. #163 depende de helpers/base #157; política de release/RC é separada.

### Plano e aceite propostos

Conferir review/pedidos das três PRs, decidir integração e reconciliar main após mudanças. Manter evidência por SHA, negativos de ordenação/paridade/limpeza e NOT EXERCISED explícito. Aceite segue a matriz pública de 09/10; não exigir novo runtime sem motivo delimitado.

### Comunicação entre responsáveis

Explicar caixas de publicação versus merge, 572 local versus checks individuais e limites de cada recibo. Não anunciar release aprovada.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Transferir os 33 checks para uma nova árvore, ou impor cada limite declarado como novo bloqueador, mudaria o escopo; chamar API e ClickHouse reais de inexistentes por falta de browser ignoraria evidência delimitada. Que caso o teste ainda não cobre? — O caso positivo de plan_json da #163 não foi incorporado automaticamente aos critérios originais e fica como follow-up; a mudança nova pode alterar o caminho coberto e exigir revalidação. Como eu explicaria isso para outro pod? — Cada prova tem seu objeto: checks por head nas #157–#159, a combinação local de 572 testes, o gate G1-F1c e o transporte MCP/HTTP; o recibo S24 é documental e não aceita implementação ou runtime retroativamente.

### Próxima ação e encerramento

Mantenedor/revisores a confirmar: revisar #157–159, escolher integração e registrar reconciliação. Encerrar #156 pelos seus critérios; preservar #163/#172 com seus recortes, sem nova execução aqui.

<a id="item-105"></a>

## CL-01 — Candidato local #167/#174 (`candidate.patch`, sha256 1122d031…) e prova do entrypoint integral sob stubs

Frente: candidatos_locais_e_linhagem. Encaminhamento: revisar_candidato_preservando_duas_linhagens.

### Identidade e estado

CL-01: Candidato local #167/#174 (`candidate.patch`, sha256 1122d031…) e prova do entrypoint integral sob stubs. Tipo candidato/achado local; owner específico a confirmar. Estado revisto por leitura de artefatos em 17/10/2026; não publicado por esta revisão.

### Intenção e benefício

Encaminhar a configuração sem sobrescrever dev/.env e fazer o runner ON aceitar os argumentos do harness. O benefício é preservar configuração do operador e remover a incompatibilidade de interface.

### Feito, faltante e não comprovado

O patch 1122d031… foi lido diretamente e seu hash confere. Ele usa PositionalBinding=false, adiciona EnvFile/AdditionalComposeFile e substitui cópia por forwarding nos gates. O recibo registra 59 testes novos e 26 existentes; a prova posterior do arquivo integral registra 7/3 na main, 10/0 no candidato e 8/2 no controle. Somente e2e foi exercitado integralmente nessa prova, em macOS com stubs e endpoint HTTP local fictício. A prova de seis casos argv usa outro PATCH-167.diff, com binding padrão: não é validação adicional automática deste patch.

### Linhagem

#167/#174 → candidate.patch 1122d031… → recibos de helper/runner → prova integral e2e com hash de teste 7d313d54… → integração não localizada no snapshot. Em paralelo, PATCH-167.diff trata só runner e mantém binding padrão. C2/31 passes trata gerador G2 e não pertence a esta linha.

### Fontes e corte

Fontes de origem na ficha Claude, linha 161; fontes locais copiadas com caminho original e hash em CAPTURA-E-INTEGRIDADE.json. Código público herdado das fichas #167, #174, limitado a seus recibos. Corte de produto c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Classe e limite da evidência

FATO OBSERVADO: bytes, conteúdo e hashes lidos agora. RELATO HISTÓRICO: execuções registradas nos recibos, não repetidas. INFERÊNCIA: riscos condicionais. PROPOSTA/DECISÃO PENDENTE: próximo trabalho e escolhas; nenhum aceite de produto por esta ficha.

### Fluxo

Wrapper integral e2e → configuração .apex/dev.env → pwsh real/runner → argv observado por stub Docker. A preservação de dev/.env é comparada em bytes. O controle reinsere Copy-Item mantendo forwarding, discriminando preservação de simples passagem do argumento.

### Consequências e risco

Somar provas de patches distintos pode aprovar comportamento nunca testado. Windows nativo, interpretação real do Compose e smoke/tail-outlier integrais não estão demonstrados por estes dez casos. O risco de sobrescrita é estático na main, não incidente com dados reais observado.

### Alternativas e recomendação

Reaproveitar o candidato conjunto após selecionar a política de binding, ou separar a interface #167 da preservação #174 mantendo dependências explícitas. Não reimplementar do zero por ignorar os recibos; não transportar o verde de um patch para outro.

### Dependências e paralelismo

DEC-N5 escolhe contrato de entrada; DEC-15 escolhe publicação. A revisão do candidato pode avançar sem toda fila M1, sem política global #175 e sem aceite formal do gerador G2. Meio de validação do diff final é requisito da integração, não decisão financeira universal.

### Plano e aceite propostos

Fixar o patch escolhido e comparar fontes à main; reconciliar callsites e compatibilidade; associar cada teste ao hash/ação que observa; revisar diff e guardas. Controle de cópia reintroduzida deve falhar; perda de EnvFile/overlay deve falhar. Se prometer três ações integrais ou Windows, obter provas próprias. A revisão atual não aplicou nem executou o patch.

### Comunicação entre responsáveis

Tabela por artefato, hash, ação, plataforma, classe de prova e limites. Dizer que HTTP local fictício foi usado; não chamar esta prova de zero sockets/rede. Nenhum aceite estrutural G2 deve aparecer como evidência de APEX.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Somar provas de patches distintos aprovaria comportamento nunca testado: os seis casos argv vêm de PATCH-167.diff com binding padrão, e os dez casos e2e vêm do candidate.patch 1122d031 com PositionalBinding=false. Que caso o teste ainda não cobre? — Smoke e tail-outlier integrais, Windows nativo e interpretação real do Compose não estão nos dez casos; a prova usou macOS com stubs e endpoint HTTP local fictício, e o patch não foi aplicado nem executado aqui. Como eu explicaria isso para outro pod? — O controle reinsere Copy-Item mantendo o forwarding, o que distingue copiar de encaminhar; argv observado por stub Docker não é Compose real, e cada resultado precisa estar ligado ao hash do patch que o produziu.

### Próxima ação e encerramento

Package/Harness e mantenedor a confirmar: selecionar candidato e completar revisão do diff final. Saída: pacote de revisão com prova por hash; encerramento de CL-01 exige destino explícito, integração ou rejeição fundamentada, sem publicação nesta auditoria.

<a id="item-106"></a>

## CL-02 — Correção de texto: predict.py:19-21,158 e models.py:38-40 (patch local cobre só predict.py; AC-10)

Frente: candidatos_locais_e_linhagem. Encaminhamento: completar_correcao_textual_e_guarda.

### Identidade e estado

CL-02: Correção de texto: predict.py:19-21,158 e models.py:38-40 (patch local cobre só predict.py; AC-10). Tipo candidato/achado local; owner específico a confirmar. Estado revisto por leitura de artefatos em 17/10/2026; não publicado por esta revisão.

### Intenção e benefício

Corrigir a alegação falsa de que executor_run_time_ms inexiste no schema, mantendo explícito que o predictor não mede W a partir dessa coluna.

### Feito, faltante e não comprovado

O patch local foi lido: altera docstring e detail em predict.py, deixa models.py fora. DDL declara a coluna; isso não demonstra migração aplicada ou linhas persistidas. O teste de matriz exige literalmente a frase antiga NOT a\n# column e precisa ser reconciliado. A nova palavra stored no detail também pode sugerir persistência observada que o patch não demonstra.

### Linhagem

#164 documental → patch local CL-02 → #179 como estudo funcional distinto. Correção em models.py e guarda estática não estão no diff local. Não houve aplicação, teste ou nova PR nesta revisão.

### Fontes e corte

Fontes de origem na ficha Claude, linha 181; fontes locais copiadas com caminho original e hash em CAPTURA-E-INTEGRIDADE.json. Código público herdado das fichas #179, PR#164, limitado a seus recibos. Corte de produto c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Classe e limite da evidência

FATO OBSERVADO: bytes, conteúdo e hashes lidos agora. RELATO HISTÓRICO: execuções registradas nos recibos, não repetidas. INFERÊNCIA: riscos condicionais. PROPOSTA/DECISÃO PENDENTE: próximo trabalho e escolhas; nenhum aceite de produto por esta ficha.

### Fluxo

DDL declarado → descrição no código → detail entregue ao usuário; fórmula permanece estimativa → rótulo honesto. Estudo measured/estimated segue fluxo distinto.

### Consequências e risco

Aplicar somente o patch deixa contradição em models.py e uma asserção exigindo texto antigo. Trocar uma frase errada por promessa de persistência não medida mantém o problema epistemológico; não é incidente funcional comprovado.

### Alternativas e recomendação

Uma pequena PR com três textos e guarda correspondente, ou ampliar #164 com escopo explícito. Preferir linguagem schema defines e predictor does not consume em vez de afirmar dados armazenados num ambiente. Não alterar fórmula por esta correção.

### Dependências e paralelismo

Nenhuma dependência de fórmula nova ou adoção completa de #179. DEC-N3 decide embalagem. Ao incluir Python/teste, revisar CI aplicável ao diff; o verde anterior da #164 não cobre código novo.

### Plano e aceite propostos

Revisar três redações e a guarda; definir exemplo de detail gerado coerente com cálculo atual; conferir diff sem alteração matemática. Negativo: a alegação de coluna inexistente deve ser detectada; não fixar versão/ambiente além da fonte. Critério: textos concordam com schema e consumo real, sem promessa runtime.

### Comunicação entre responsáveis

Explicar coluna declarada, migração aplicada e uso pelo predictor como três fatos distintos. Relacionar #179 sem prometer resolvedor novo de W.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Mudar o cálculo junto com o texto misturaria correção editorial com decisão de modelo, e aplicar só o patch local deixaria a contradição em models.py. Que caso o teste ainda não cobre? — O patch cobre só predict.py, não models.py:38-40, e o teste da matriz exige literalmente a frase antiga; a palavra stored no detail sugere persistência observada que o patch não demonstra. Como eu explicaria isso para outro pod? — Coluna declarada no DDL, migração aplicada e uso pelo predictor são três fatos distintos; o texto corrigido diz que o schema define a coluna e que o predictor não a consome.

### Próxima ação e encerramento

Owner Verify e revisor documental a confirmar: completar diff revisável com guarda e decidir destino. Encerrar por integração do texto/contrato descrito, sem certificar persistência ou novo predictor.

<a id="item-107"></a>

## CL-03 — Pacote `windows-ready/` (15 itens previstos)

Frente: candidatos_locais_e_linhagem. Encaminhamento: prova_windows_pendente_com_escopo_corrigido.

### Identidade e estado

CL-03: Pacote `windows-ready/` (15 itens previstos). Tipo candidato/achado local; owner específico a confirmar. Estado revisto por leitura de artefatos em 17/10/2026; não publicado por esta revisão.

### Intenção e benefício

Obter prova nativa Windows do runner e dos casos de arquivo/argv relevantes, sem confundí-la com prova completa do wrapper ou de serviços.

### Feito, faltante e não comprovado

Os 14 arquivos listados no manifesto conferiram agora; 15 é a contagem de itens pytest esperada pelo launcher, não de arquivos. O launcher recusa plataforma não Win32NT/pwsh<7 e exige 15/15 sem skip. w01 exige PositionalBinding=false; w07 chama apenas helper extraído e seu teste de preservação é descrito no próprio código como vácuo por construção. Não há resultado Windows no pacote consultado.

### Linhagem

Candidato 1122d031… → fontes windows-ready com binding false → protocolo e fixtures → execução Windows pendente. PATCH-167.diff padrão não é intercambiável com essas fixtures. Prova macOS de e2e é outra aresta, não preenche Windows.

### Fontes e corte

Fontes de origem na ficha Claude, linha 201; fontes locais copiadas com caminho original e hash em CAPTURA-E-INTEGRIDADE.json. Código público herdado das fichas #167, #174, limitado a seus recibos. Corte de produto c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Classe e limite da evidência

FATO OBSERVADO: bytes, conteúdo e hashes lidos agora. RELATO HISTÓRICO: execuções registradas nos recibos, não repetidas. INFERÊNCIA: riscos condicionais. PROPOSTA/DECISÃO PENDENTE: próximo trabalho e escolhas; nenhum aceite de produto por esta ficha.

### Fluxo

Host Windows → guards de plataforma/hash → pytest dos runners com stubs → relatório por caso. Wrapper helper → argumentos, sem invocar fluxo completo; serviços não entram.

### Consequências e risco

Quinze passes poderiam ser relatados como preservação integral no Windows embora w07 não percorra escrita/dispatch. Paths com espaço/colchetes e locking têm testes propostos, sem observação nativa atual. Não se afirmou falha real.

### Alternativas e recomendação

Executar o pacote como prova delimitada de runner/helper ou expandi-lo antes se o requisito for entrypoint completo. Runner hospedado e máquina do time são opções operacionais; publicação prévia não é requisito técnico, desde que os bytes candidatos estejam fixados.

### Dependências e paralelismo

Política de binding escolhida, bytes coerentes e host Windows autorizado para execução futura. Não depende de CL-05/CL-06; não impor publicação como único meio de levar o candidato ao host.

### Plano e aceite propostos

Ratificar escopo; conferir hashes e ferramentas; coletar recibos nativos sem skips. Se requerer preservação pelo entrypoint, acrescentar caso que invoque wrapper inteiro e controle de cópia reintroduzida. Conservar falha/skip como falha/inconclusivo e registrar diferenças de artefato.

### Comunicação entre responsáveis

Identificar runner, helper ou entrypoint em cada linha. Não escrever pacote na main: estes arquivos são locais. Os 15 itens não certificam Docker/Compose/APIs.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Aceitar o pacote Windows como execução concluída transferiria uma prova que ele não contém. O pacote propõe verificar runner e helpers; não há resultado Windows aceito nesta revisão. Que caso o teste ainda não cobre? — Uma cópia reintroduzida fora do helper não seria vista; não há resultado Windows no pacote, e as fixtures esperam PositionalBinding=false, que precisa coincidir com a política do patch escolhido. Como eu explicaria isso para outro pod? — O pacote prova runner e helper em Windows nativo com stubs, sem Docker, Compose ou APIs; um skip conta como falha ou inconclusivo, não como passe, e 15 é a contagem de itens pytest, não de arquivos.

### Próxima ação e encerramento

Owner de validação Windows a confirmar: executar apenas quando autorizado ou registrar pendência. Saída: recibo nativo por hash/escopo; encerrar a prova de runner separadamente do eventual gate de wrapper.

<a id="item-108"></a>

## CL-04 — `generate_g2_results.py` com alegação obsoleta de isolamento (tooling de revisão)

Frente: candidatos_locais_e_linhagem. Encaminhamento: arquivar_original_e_avaliar_correcao_existente.

### Identidade e estado

CL-04: `generate_g2_results.py` com alegação obsoleta de isolamento (tooling de revisão). Tipo candidato/achado local; owner específico a confirmar. Estado revisto por leitura de artefatos em 17/10/2026; não publicado por esta revisão.

### Intenção e benefício

Evitar que o tooling de geração de resultados transforme configuração de processo em garantia não medida de isolamento.

### Feito, faltante e não comprovado

Leitura direta confirma a frase zero network or socket access no original e chamadas subprocess a docker/docker-compose, PATH herdado e caminhos fixos. Existe cópia documental corrigida em correction-20261012 que explicita isolamento desconhecido; portanto não falta toda correção. Ambas continuam contendo chamadas externas. Nenhuma foi executada aqui.

### Linhagem

Original G2 → correção de relatório → cópia documental corrigida → redesenhos separados. O original permanece histórico, não recomendado para uso. O recibo C2 refere outro candidato v2 fixado por hash.

### Fontes e corte

Fontes de origem na ficha Claude, linha 221; fontes locais copiadas com caminho original e hash em CAPTURA-E-INTEGRIDADE.json. Código público herdado das fichas não aplicável, limitado a seus recibos. Corte de produto c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Classe e limite da evidência

FATO OBSERVADO: bytes, conteúdo e hashes lidos agora. RELATO HISTÓRICO: execuções registradas nos recibos, não repetidas. INFERÊNCIA: riscos condicionais. PROPOSTA/DECISÃO PENDENTE: próximo trabalho e escolhas; nenhum aceite de produto por esta ficha.

### Fluxo

Gerador → ferramentas host → saída obtida e campos textuais → relatório. Uma string fixa pode afirmar mais do que observou; cópia documental corrige linguagem, não fronteira de execução.

### Consequências e risco

Reexecutar original pode reapresentar garantia falsa. Usar cópia corrigida como ferramenta adotada ignora configuração e saídas fixas. Não foi observado acesso externo novo nesta revisão.

### Alternativas e recomendação

Conservar original como arquivo e apontar para ressalva; adotar gerador redesenhado só com interface/saídas e prova próprias; remover tooling da cadeia se não houver consumidor. Corrigir o original histórico não é requisito automático.

### Dependências e paralelismo

Dono do tooling e decisão de adoção, sem dependência do APEX v1. Kimi/Gemini cancelados não impedem revisar artefatos históricos, nem exigem novas rodadas.

### Plano e aceite propostos

Registrar origem e sucessores por hash; retirar o original de qualquer instrução operacional atual. Para adoção futura, separar dados medidos de declarações e testar com executor falso e saídas isoladas; uma chamada inesperada deve falhar. Não reexecutar para verificar meramente texto.

### Comunicação entre responsáveis

Nota local: configuração Docker não comprova isolamento de rede/daemon; a correção arquivística não é aprovação operacional. Evitar texto absoluto não observado.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Reexecutar o original reapresentaria a garantia falsa de zero network or socket access, e adotar a cópia corrigida como ferramenta ignoraria que ela ainda chama docker e docker-compose. Que caso o teste ainda não cobre? — O status de isolamento não é medido em nenhuma das duas versões, e nenhum controle detecta chamada inesperada; nenhuma delas foi executada aqui. Como eu explicaria isso para outro pod? — A cópia de correction-20261012 corrige a linguagem, não a fronteira de execução; outro pod pode concluir que o isolamento é desconhecido, e o original fica arquivado como histórico.

### Próxima ação e encerramento

Dono do tooling: vincular correção existente e decidir adotar ou arquivar. Encerrar CL-04 documental com referência inequívoca; adoção é tarefa distinta com prova adequada.

<a id="item-109"></a>

## CL-05 — Correção mínima do Task-Spec 3.9.0 (handoff Tier-2 estrutural)

Frente: candidatos_locais_e_linhagem. Encaminhamento: revisar_fix_de_preflight_externo_sem_gate_apex.

### Identidade e estado

CL-05: Correção mínima do Task-Spec 3.9.0 (handoff Tier-2 estrutural). Tipo candidato/achado local; owner específico a confirmar. Estado revisto por leitura de artefatos em 17/10/2026; não publicado por esta revisão.

### Intenção e benefício

Reconciliar a representação de autorização estrutural sem assinatura entre builder e preflight do Task-Spec 3.9.0, preservando checagens de autorização dos demais casos.

### Feito, faltante e não comprovado

Patch lido normaliza signed_off_sig ausente para string vazia e scheme structural; preflight instalado em 3.9.0 ainda tem comparação ref versus None. Log histórico do trial contém ACCEPTED=1 Tier2; ele pertence a clone isolado, não à tarefa real. A inspeção preserva o ramo para string com dois-pontos, mas não prova toda segurança HMAC nem abrange toda assinatura inválida.

### Linhagem

Falha HANDOFF_STALE da tarefa G2 → proposta tier2-structural-handoff.patch → trial isolado → ferramenta autoritativa ainda sem esse diff no arquivo lido. Não é defeito do runner APEX #167 nem gate necessário de CL-01.

### Fontes e corte

Fontes de origem na ficha Claude, linha 241; fontes locais copiadas com caminho original e hash em CAPTURA-E-INTEGRIDADE.json. Código público herdado das fichas não aplicável, limitado a seus recibos. Corte de produto c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Classe e limite da evidência

FATO OBSERVADO: bytes, conteúdo e hashes lidos agora. RELATO HISTÓRICO: execuções registradas nos recibos, não repetidas. INFERÊNCIA: riscos condicionais. PROPOSTA/DECISÃO PENDENTE: próximo trabalho e escolhas; nenhum aceite de produto por esta ficha.

### Fluxo

Frontmatter sem assinatura → handoff ref vazio/structural → preflight compara representações → aceite por política de tier/autoridade. Normalização de metadados não equivale a verificar assinatura.

### Consequências e risco

O ramo else structural também abrange valores truthy sem dois-pontos; não se deve afirmar que somente ausência é afetada sem revisar validações anteriores. Trial positivo não prova recusa de assinatura adulterada, tier indevido ou metadata divergente.

### Alternativas e recomendação

Revisar/corrigir tooling na fonte autoritativa com regressões; usar caminho HMAC suportado com titular da chave quando apropriado; manter tarefa não aceita. Não editar assinatura à mão nem copiar o aceite do clone.

### Dependências e paralelismo

Mantenedor do tooling, especificação da autorização e casos negativos. Independente da publicação do candidato APEX; só bloqueia a retomada deste aceite G2 se mantido o mesmo mecanismo.

### Plano e aceite propostos

Comparar builder/preflight; definir domínio válido de signed_off_sig; cobrir ausente, vazio, HMAC válido/inválido, string sem separador, tier/assinante/revisão/base divergentes. Aceite: caso estrutural autorizado passa e casos inválidos continuam recusados; regenerar handoff para tarefa real após correção adotada. Nenhum ensaio novo aqui.

### Comunicação entre responsáveis

Informar que o log do trial é evidência histórica isolada. O ramo HMAC mantido no diff é observação estática, não certificação completa de segurança.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Copiar o aceite do clone isolado ou editar assinatura à mão para a tarefa real deixaria o aceite sem base; o ramo else structural também abrange valores truthy sem dois-pontos. Que caso o teste ainda não cobre? — Não foi conferido controle negativo suficiente para HMAC ou valores inválidos no recorte aceito. Isso não permite afirmar que nenhum teste exista em qualquer artefato. Como eu explicaria isso para outro pod? — É um ajuste no tooling Task-Spec 3.9.0, que normaliza signed_off_sig ausente para handoff estrutural; não é defeito do runner APEX nem gate do CL-01.

### Próxima ação e encerramento

Mantenedor Task-Spec a confirmar: revisar proposta com controles e decidir adoção. Encerrar por correção autoritativa e prova específica, sem tratar CL-01 como dependente deste tooling.

<a id="item-110"></a>

## CL-06 — Linhagem de aceite estrutural C2 (31 passed; sem aceite formal)

Frente: candidatos_locais_e_linhagem. Encaminhamento: corrigir_objeto_da_linhagem_para_gerador_g2.

### Identidade e estado

CL-06: Linhagem de aceite estrutural C2 (31 passed; sem aceite formal). Tipo candidato/achado local; owner específico a confirmar. Estado revisto por leitura de artefatos em 17/10/2026; não publicado por esta revisão.

### Intenção e benefício

Preservar o recibo e o estado de aceite da verificação estrutural G2, ligando resultado ao candidato e tentativa corretos.

### Feito, faltante e não comprovado

A ficha Claude vinculava C2/31 passes ao candidato APEX #167/#174. O recibo primário identifica generate_g2_results.candidate.v2.py (21066b5a…) e sua suíte (f5fba79e…), ambos conferidos agora. A tarefa T-20261012-clean-g2-structural-verify-r2 está accepted:false; 31 passed in 0.28s é resultado histórico do gerador com fake runner. Trial separado tem aceite Tier2, que não altera a tarefa real.

### Linhagem

Gerador G2 v2 → task base d9e32f17… → receipt STRUCTURAL-VERIFY → duas tentativas HANDOFF_STALE → trial externo do fix. Não há aresta de implementação ou teste para candidate.patch 1122d031… do APEX.

### Fontes e corte

Fontes de origem na ficha Claude, linha 261; fontes locais copiadas com caminho original e hash em CAPTURA-E-INTEGRIDADE.json. Código público herdado das fichas não aplicável, limitado a seus recibos. Corte de produto c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Classe e limite da evidência

FATO OBSERVADO: bytes, conteúdo e hashes lidos agora. RELATO HISTÓRICO: execuções registradas nos recibos, não repetidas. INFERÊNCIA: riscos condicionais. PROPOSTA/DECISÃO PENDENTE: próximo trabalho e escolhas; nenhum aceite de produto por esta ficha.

### Fluxo

Hashes G2 → suíte com fake runner → sumário de 31 itens → recibo limitado → preflight formal. Os evals verificam resultado e algumas frases do recibo; as frases não provam runtime.

### Consequências e risco

Transferir 31 passes ao APEX cria evidência de objeto errado; usar blocked G2 como gate de CL-01 cria dependência falsa. A ausência de aceite real permanece, mas não invalida automaticamente a observação histórica dos testes do gerador.

### Alternativas e recomendação

Manter aceite G2 como tarefa externa se útil; corrigir tooling e repetir o aceite real quando autorizado; arquivar a linha sem promover a resultado de produto. Retirar a dependência automática da PR APEX.

### Dependências e paralelismo

CL-05 apenas se decidir continuar este aceite. DEC-15 não depende necessariamente de G2. Nenhuma necessidade de novos pareceres Gemini/Kimi.

### Plano e aceite propostos

Corrigir mapa ID→artefato; preservar hash/base/attempt/recibo; registrar accepted:false real e aceite trial separado. Controle documental: qualquer linha que atribua 31 testes a scripts/apex.ps1 deve ser rejeitada. Aceite da correção é ligação precisa, não execução de produto.

### Comunicação entre responsáveis

Dizer gerador G2, 31 testes estruturais com fake runner, tarefa real não aceita; não dizer candidato C2 APEX. A autoria C2 é papel da rodada, não identidade de software.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Transferir os 31 passes ao candidato APEX da #174 criaria evidência sobre o objeto errado, e usar o G2 bloqueado como gate do CL-01 criaria uma dependência falsa. Que caso o teste ainda não cobre? — Os 31 testes rodaram sobre generate_g2_results.candidate.v2.py (21066b5a…) com fake runner; a tarefa real está accepted:false, e o aceite Tier2 do clone é de outro attempt. Como eu explicaria isso para outro pod? — C2 é o papel da rodada, não a identidade do software: o recibo é do gerador G2 e não tem aresta para scripts/apex.ps1, então nome de agente não identifica o produto.

### Próxima ação e encerramento

Curador da auditoria: corrigir CL-06 e dependências de CL-01/DEC-15. Dono do tooling decide destino do aceite G2. Encerrar a correção de linhagem com fontes inequívocas e limites preservados.

