# Fichas documentais — lote 5

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-041"></a>

## G08 — Validar semanticamente a combinação #127×#128

Frente: Pod 2/Package. Encaminhamento: ENCERRAR_COMPOSICAO_HISTORICA_E_SEPARAR_PROVA_ATUAL.

### Identidade e estado

ID original G08; título: Validar semanticamente a combinação #127×#128; tipo de origem: validação; pod: Pod 2/Package; responsável para o próximo passo: responsável por Pod 2/Package, a confirmar; nenhuma atribuição feita nesta revisão. Objetos públicos: PR #127: integrada em 2026-10-06T19:56:00Z; autoria pública gustocezar; assignees nenhum no snapshot; PR #128: integrada em 2026-10-06T19:56:14Z; autoria pública gustocezar; assignees nenhum no snapshot. Destino consolidado: ENCERRAR_COMPOSICAO_HISTORICA_E_SEPARAR_PROVA_ATUAL. O autor público não é automaticamente assignee ou aprovador.

### Intenção e benefício

Verificar se o roteamento PowerShell e o caminho tail-outlier coexistiam na combinação de #127/#128. O objetivo original era encontrar incompatibilidade semântica que um merge textual limpo não detecta.

### Feito, faltante e não comprovado

As duas PRs foram integradas. O registro canônico relata composições offline em ambas as ordens, inclusive em 01/10 com #127 4e44bfd e #128 2b84c7a, árvore igual e suites registradas. Essa lacuna histórica não deve ser repetida como não executada. A main atual possui outro workflow; não há neste lote reexecução da combinação nem prova de CI principal verde em c3c3ea3. A revisão de #124 identifica limite dos testes atuais: Handler textual em DryRun não observa a invocação de Command para todas as ações. A composição histórica encerrada não encerra esse critério público.

### Linhagem

G08 → combinação dos heads #127/#128 sobre a289e53 → relatos de parser/suites offline → merges → código combinado na main. Prova atual de CI é follow-up de G01 e das fichas atuais, não condição retroativa para declarar que o estudo de composição existiu. Identidades preservadas do snapshot público: #127: head 4e44bfdce5586fe9b8ed7c96e41932b55f231a88, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge fec8a7fb0b3669343725141ab60eef0d8dff74a0; #128: head 2b84c7a14fbcc5c009a3366536ccb80ebe316ca0, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge d8c1a3c67948c047ea282ca4d839462153b4e60a. Elos de revisão formal, execução independente ou aceite funcional não citados nesta ficha permanecem não verificados; não se infere ausência a partir de falta de Closes.

### Fontes e corte

Fontes confrontadas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json#/rows/7; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv#[id=G08]; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/BACKLOG-LEARNING.json#[id=G08]; ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md:194; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json#[number=127]; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json#[number=128]; fontes/main-workflow.txt; fontes/lote2-tests__test_apex_initial_package.py.txt; fontes/lote2-docs__e2e__TAIL_OUTLIER_RUNTIME_GATE.md.txt. Base de referência de código APEX: c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. O CSV e BACKLOG-LEARNING preservam seu corte histórico; não são leitura do estado atual. A ficha Claude é proposta de partida, não validação independente.

### Classe e limite da evidência

FATO OBSERVADO: leitura dos metadados, textos e trechos estáticos expressamente citados nos campos 3–5. RELATO HISTÓRICO do registro, sem reexecução: derived: merge-tree limpo do par; reported: 18 testes #128 no head 7d3266d; delta 2026-09-29: reported: evidência persistida da combinação TS13 (raiz 72) examinada no lote 1, sem reexecução nem aceite formal; direct_offline: checkout isolado com heads #127 4e44bfd e #128 7d3266d sobre main a289e53; duas ordens de merge têm árvore idêntica; Engine 181 coletados/10 skips rc 0, Dev 30 rc 0, raiz 72 passed, parser PowerShell e diff --check verdes; direct_offline 2026-10-01: heads #127 4e44bfd/#128 2b84c7a sobre main a289e53; merges nas duas ordens limpos e árvore idêntica; Engine 171 passed/11 skipped, Dev 30 passed, raiz 72 passed, parser PowerShell e diff --check verdes. INFERÊNCIA: consequências possíveis do campo 8, com os limites ali indicados. PROPOSTA: alternativas, plano e próximos passos desta ficha. DECISÃO PENDENTE: escolhas de escopo/owner indicadas nos campos 9–10. Teste local, CI por SHA, integração e aprovação humana não são intercambiáveis; nenhuma execução de produto foi feita nesta revisão.

### Fluxo

Fluxo histórico: duas ordens de composição → árvore resultante → testes de dispatch, guards e pacote → comparação de resultados. Fluxo futuro opcional: ref integrada escolhida → root gate com pwsh verificado → recibo por suite; isso não substitui runtime Spark.

### Consequências e risco

Um merge textual limpo pode esconder um desvio de handler ou guard. O relato de testes reduz essa dúvida para os heads históricos, sem demonstrar compatibilidade de qualquer ref futura. Repetir como pendência já não feita apagaria essa prova delimitada.

### Alternativas e recomendação

Encerrar o estudo da combinação histórica e conservar seus recibos é o caminho recomendado. Exigir prova nova em main é opção proporcional ao aceite de release atual, sem reabrir os merges. Reexecutar uma combinação antiga pode esclarecer regressão localizada, mas não certifica a main atual.

### Dependências e paralelismo

Não há dependência ativa nos merges, já ocorridos. Uma nova prova hospedada depende do workflow/ref escolhido e de runner com PowerShell; runtime tail-outlier é outra fronteira. Estudos de contrato podem seguir em paralelo.

### Plano e aceite propostos

Preservar heads, ordem, árvore e resultados históricos como relato. Na visão atual, separar quatro níveis: composição textual, testes offline de dispatch, CI principal e runtime do pacote. Controle para eventual nova prova: pwsh ausente não pode resultar em cobertura silenciosamente pulada; casos de help/invalid-action não devem mutar estado. Aceite documental: G08 histórico encerrado e prova atual, se requerida, nomeada em destino próprio. O controle de invocação real do dispatcher de #124 permanece obrigatório no aceite dessa issue; não foi demonstrado pelo relato da combinação. Um futuro teste seguro deve distinguir Handler correto com Command trocado.

### Comunicação entre responsáveis

Citar a data e os heads das duas ordens, explicar o que os testes offline cobrem e indicar que #127 tem registro runtime distinto. Evitar dizer que combinação verde significa cold start ou Windows já comprovados.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Uma interação de handlers poderia escapar apesar de merge limpo. Que caso o teste ainda não cobre? A main atual no CI principal e ambientes live adicionais. Como eu explicaria isso para outro pod? A combinação histórica foi estudada; cada prova futura pertence à sua ref.

### Próxima ação e encerramento

Curador e mantenedor, a confirmar: encerrar G08 no recorte histórico, preservando #127/#128 e relatos de 01/10; se release exigir nova prova integrada, nomear ref, suite e destino. Saída: limites explícitos sem apagar resultado anterior.

<a id="item-042"></a>

## G09 — Citar o segredo gerado no gate de configuração do Collector

Frente: Governança/CI. Encaminhamento: ENCERRAR_QUOTING_INTEGRADO.

### Identidade e estado

ID original G09; título: Citar o segredo gerado no gate de configuração do Collector; tipo de origem: correção CI; pod: Governança/CI; responsável para o próximo passo: responsável por Governança/CI, a confirmar; nenhuma atribuição feita nesta revisão. Objetos públicos: PR #149: integrada em 2026-10-06T20:12:13Z; autoria pública gustocezar; assignees nenhum no snapshot. Destino consolidado: ENCERRAR_QUOTING_INTEGRADO. O autor público não é automaticamente assignee ou aprovador.

### Intenção e benefício

Fazer o shell passar REDACTION_SECRET_KEY como um único argumento ao container de validação do Collector, removendo SC2046. O escopo é a construção do argv, não mudança da política de segredo ou da configuração do Collector.

### Feito, faltante e não comprovado

#149 foi integrada. ci.yml atual conserva -e com o argumento completo entre aspas e gera um hexadecimal de 64 caracteres. O corpo da PR relata actionlint verde e probe de argv; nenhuma execução atual de actionlint, shell ou container ocorreu neste lote.

### Linhagem

G09 → achado SC2046 → #149, diff de quoting → merge → argumento presente em ci.yml c3c3ea3. G10 estudou a composição com outras PRs de CI. #148 é correção textual distinta, não implementação desta correção. Identidades preservadas do snapshot público: #149: head bf308c77ccf3996d9fd58320cfa0eaccca51ce06, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge e188a4bc966c2fcaecddf402bfd2f18f532ad9d5. Elos de revisão formal, execução independente ou aceite funcional não citados nesta ficha permanecem não verificados; não se infere ausência a partir de falta de Closes.

### Fontes e corte

Fontes confrontadas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json#/rows/8; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv#[id=G09]; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/BACKLOG-LEARNING.json#[id=G09]; ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md:230; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json#[number=149]; fontes/main-workflow.txt. Base de referência de código APEX: c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. O CSV e BACKLOG-LEARNING preservam seu corte histórico; não são leitura do estado atual. A ficha Claude é proposta de partida, não validação independente.

### Classe e limite da evidência

FATO OBSERVADO: leitura dos metadados, textos e trechos estáticos expressamente citados nos campos 3–5. RELATO HISTÓRICO do registro, sem reexecução: direct_static/offline: actionlint falha SC2046 na main e passa no head; YAML carrega com seis jobs; probe shell mostra argv idêntico antes/depois para segredo hexadecimal de 64 caracteres; diff de uma linha, PR aberta e mergeável. INFERÊNCIA: consequências possíveis do campo 8, com os limites ali indicados. PROPOSTA: alternativas, plano e próximos passos desta ficha. DECISÃO PENDENTE: escolhas de escopo/owner indicadas nos campos 9–10. Teste local, CI por SHA, integração e aprovação humana não são intercambiáveis; nenhuma execução de produto foi feita nesta revisão.

### Fluxo

Fluxo estático: openssl produz valor hexadecimal → expansão shell dentro de argumento citado → opção -e do Docker → variável de ambiente consumida pela validação. O teste de argv relatado compara a unidade do argumento, não o comportamento interno do Collector.

### Consequências e risco

Expansão sem quoting pode permitir separação de palavras ou globbing para valores gerais. Para o hexadecimal gerado, o próprio relato mostrou argv equivalente; não há incidente de segredo corrompido demonstrado. A correção expressa a fronteira robusta do argumento.

### Alternativas e recomendação

Manter quoting do argumento completo é a menor mudança. Exportar a variável e usar outra forma de passagem adicionaria escopo sem benefício demonstrado aqui. Ignorar SC2046 manteria uma fragilidade de estilo/expansão; alterar gerador ou segredo é outra decisão.

### Dependências e paralelismo

Nenhuma nova dependência para este fechamento. A configuração do Collector e seus requisitos continuam pertencendo ao job; CI hospedado é evidência separada, sem gate retroativo sobre a PR integrada.

### Plano e aceite propostos

Conferir a PR integrada e presença do quoting no workflow atual; registrar que o probe histórico comparou um hexadecimal de 64 caracteres e que o container não foi iniciado naquela validação. Aceite documental satisfeito: intenção de quoting preservada. Um futuro teste de shell só é necessário se o formato ou montagem do argumento mudar.

### Comunicação entre responsáveis

Descrever o que muda no argv e por que o valor válido antigo era equivalente. Não apresentar o ajuste como prova de entrega de telemetria nem divulgar segredo real na evidência.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Um valor contendo separadores poderia ser dividido pelo shell. Que caso o teste ainda não cobre? A validação do Collector em execução e formatos de segredo não usados pelo gerador. Como eu explicaria isso para outro pod? A PR protege a passagem de um argumento.

### Próxima ação e encerramento

Curador: fechar o ID documentalmente com #149 e ci.yml atual. Entrada: diff relatado e linha presente; saída: vínculo de encerramento com limite estático. Sem nova alteração ou execução.

<a id="item-043"></a>

## G10 — Revisar SC2016 na combinação dos PRs de CI

Frente: Governança/CI. Encaminhamento: ENCERRAR_ANALISE_DE_COMPOSICAO_DO_CI.

### Identidade e estado

ID original G10; título: Revisar SC2016 na combinação dos PRs de CI; tipo de origem: validação/correção; pod: Governança/CI; responsável para o próximo passo: responsável por Governança/CI, a confirmar; nenhuma atribuição feita nesta revisão. Objetos públicos: PR #128: integrada em 2026-10-06T19:56:14Z; autoria pública gustocezar; assignees nenhum no snapshot; PR #138: integrada em 2026-10-06T20:12:02Z; autoria pública gustocezar; assignees nenhum no snapshot; PR #148: integrada em 2026-10-06T20:18:24Z; autoria pública gustocezar; assignees nenhum no snapshot; PR #149: integrada em 2026-10-06T20:12:13Z; autoria pública gustocezar; assignees nenhum no snapshot. Destino consolidado: ENCERRAR_ANALISE_DE_COMPOSICAO_DO_CI. O autor público não é automaticamente assignee ou aprovador.

### Intenção e benefício

Conciliar SC2016 e SC2046 ao combinar as mudanças de CI sem perder a expansão intencional de PowerShell ou confundir advertências preexistentes com regressão. O público é quem mantém e revisa os workflows.

### Feito, faltante e não comprovado

As PRs relacionadas foram integradas. O registro relata que o comentário shellcheck disable=SC2016 resolveu a leitura equivocada da expansão PowerShell e que a combinação teve actionlint rc 0 em 01/10. O workflow atual preserva o disable e o quoting do segredo; isso foi lido estaticamente. Actionlint atual não foi executado.

### Linhagem

G10 → análise combinada #128/#138/#148/#149 → correção pontual de comentário/quoting → relatos de duas ordens e actionlint → merges. #160 alterou depois a organização de jobs; não se transfere o rc histórico para todo workflow futuro. Identidades preservadas do snapshot público: #128: head 2b84c7a14fbcc5c009a3366536ccb80ebe316ca0, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge d8c1a3c67948c047ea282ca4d839462153b4e60a; #138: head 4b5798d5a2f0ef23199faea32743e960b69570e6, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge 9763b2f413d7d3c9d477e9b95f7d4f81c83fc6d5; #148: head d4f85c3c58931654c91c3ba627cbca0a116d75d1, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge d07aad29ab9ec8e8a14ae6ea7b5f31cc351f2d45; #149: head bf308c77ccf3996d9fd58320cfa0eaccca51ce06, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge e188a4bc966c2fcaecddf402bfd2f18f532ad9d5. Elos de revisão formal, execução independente ou aceite funcional não citados nesta ficha permanecem não verificados; não se infere ausência a partir de falta de Closes.

### Fontes e corte

Fontes confrontadas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json#/rows/9; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv#[id=G10]; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/BACKLOG-LEARNING.json#[id=G10]; ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md:250; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json#[number=128]; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json#[number=138]; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json#[number=148]; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json#[number=149]; fontes/main-workflow.txt. Base de referência de código APEX: c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. O CSV e BACKLOG-LEARNING preservam seu corte histórico; não são leitura do estado atual. A ficha Claude é proposta de partida, não validação independente.

### Classe e limite da evidência

FATO OBSERVADO: leitura dos metadados, textos e trechos estáticos expressamente citados nos campos 3–5. RELATO HISTÓRICO do registro, sem reexecução: direct_offline: duas ordens de merge sem conflito e mesma árvore; Front 87, raiz 69, pwsh 7; Codex reexecutou raiz 69; actionlint main rc 1 SC2046, combinação rc 1 SC2016; delta 2026-10-01: direct_offline Codex: patch local de comentário shellcheck disable=SC2016 faz actionlint do ci.yml combinado rc 0; não publicado; clone E20 do mesmo lote não aceito por mutação residual e whitespace (antigravity-batch-4h/lane1-g10; REVIEW.md); direct_offline: #128 perde SC2016 e mantém apenas SC2046 de #149; combinação actionlint rc 0; direct_remote: push fast-forward, PR mergeável, run 36923303788 com 11 jobs/0 steps e anotação explícita de billing; direct_offline 2026-10-01: heads atuais #128/#138/#148/#149 sobre main a289e53; merges em duas ordens limpos/mesma árvore; diff contra combinação antiga = um comentário; actionlint rc 0, Front 87 passed, raiz 69 passed, PowerShell 7.6.4, diff --check rc 0. INFERÊNCIA: consequências possíveis do campo 8, com os limites ali indicados. PROPOSTA: alternativas, plano e próximos passos desta ficha. DECISÃO PENDENTE: escolhas de escopo/owner indicadas nos campos 9–10. Teste local, CI por SHA, integração e aprovação humana não são intercambiáveis; nenhuma execução de produto foi feita nesta revisão.

### Fluxo

Fluxo histórico: YAML combinado → shell analisado por actionlint/ShellCheck → distinção de expansão PowerShell literal → supressão localizada → lint. Fluxo atual observado: script PowerShell segue com comentário explicativo; resultado do lint atual continua não verificado.

### Consequências e risco

Suprimir regra globalmente esconderia problemas reais; retirar a supressão localizada pode voltar a acusar expansão intencional. A presença do comentário reduz ambiguidade, mas não prova que o workflow inteiro passa em qualquer versão do analisador.

### Alternativas e recomendação

Conservar supressão localizada e explicável é proporcional. Reescrever o comando PowerShell pode evitar o diagnóstico, mas exige preservar sua semântica. Adicionar actionlint ao CI seria melhoria opcional de tooling com escopo próprio, não requisito automático deste ID.

### Dependências e paralelismo

Nenhuma fila histórica ainda precisa ser integrada. G02 consome os nomes atuais dos checks; uma proposta nova de actionlint exige owner e decisão de política separados. Resultados de CI não decorrem da presença do comentário.

### Plano e aceite propostos

Registrar cabeças e resultados históricos sem reexecutá-los; conferir na main a supressão localizada e quoting. Aceite documental: a causa de cada alerta e a correção correspondente permanecem identificadas. Controle de manutenção proposto: futura alteração não deve tornar a supressão global nem remover a expressão PowerShell necessária. Encerrar G10; tratar lint contínuo separadamente se desejado.

### Comunicação entre responsáveis

Explicar que SC2016 era um aviso sobre interpretação do shell e SC2046 dizia respeito ao argumento do segredo. Distinguir a análise da combinação histórica de uma certificação atual de todos os jobs.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Uma supressão ampla esconderia erros de shell sem relação com PowerShell. Que caso o teste ainda não cobre? O lint completo no workflow/ref e versão de ferramenta atuais. Como eu explicaria isso para outro pod? Cada aviso foi tratado na fronteira onde fazia sentido.

### Próxima ação e encerramento

Curador da consolidação: encerrar G10 com os resultados históricos e a leitura atual dos dois trechos. Saída: decisão de manutenção rastreável; eventual adição de lint terá item próprio. Nenhum novo teste é necessário para registrar esse encerramento documental.

<a id="item-044"></a>

## issue115-attribution-audit-hardening.yaml — issue115-attribution-audit-hardening.yaml

Frente: Engine / atribuição de execução. Encaminhamento: Catalogar plano histórico; remeter integração pública à #115.

### Identidade e estado

issue115-attribution-audit-hardening.yaml; TaskPlan histórico; 1 unidade(s): T-20260919-execution-attribution-audit-hardening. Origem https://github.com/luanmorenommaciel/apex/issues/115; approved=true é registro de planejamento. Owner das folhas não atribuído por esta revisão; papel Engine / atribuição de execução a confirmar. Arquivo na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Complementar o resolvedor offline com documentação e regressões para que observações de outro app/job não alterem a atribuição. Beneficiário: consumidor que precisa distinguir ausência opcional, identidade não encontrada e conflito.

### Feito, faltante e não comprovado

O escopo declarado é documentação e testes do resolvedor existente; não muda resultados nem conecta ClickHouse, findings ou superfície pública. A ficha Claude dizia não haver lacuna no manifesto, mas essa afirmação só pode ser documental. A cópia confere com blob 9e9fe71edd0a46c37d3223b8dffcd46ca30ece12; nenhum teste ou aceite foi reexecutado.

### Linhagem

https://github.com/luanmorenommaciel/apex/issues/115 → manifesto issue115-attribution-audit-hardening.yaml → T-20260919-execution-attribution-audit-hardening. O inventário associa historicamente #126 (commit 1ecc310896); essa referência não prova implementação de cada comportamento. Commits, checks e aceite funcional exigem elos próprios, não inferidos do nome do arquivo.

### Fontes e corte

Fonte primária preservada: ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_issue115-attribution-audit-hardening.yaml:1; unidades T-20260919-execution-attribution-audit-hardening:L8. Git: https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/issue115-attribution-audit-hardening.yaml. Integridade: ../parte-03-claude-v2/TASKSPECS-106.json. Proposta revisada: C05-TASKSPECS-REPO.md:1754.

### Classe e limite da evidência

FATO OBSERVADO: texto do manifesto e integridade da cópia; RELATO HISTÓRICO: approved e motivação da auditoria; PROPOSTA: comportamentos/controles declarados; INFERÊNCIA: adequação documental das fronteiras; aceite humano, CI do head e runtime não certificados. YAML válido é apenas sintaxe.

### Fluxo

Observações normalizadas → filtro exato app_id/job_id → resolvedor → status e IDs. O controle novo introduz linhas estrangeiras nos casos absent/not_found/conflict e mistura None com identidade não alvo; a docstring explica as mesmas fronteiras. Fluxo contratado pelo plano, sem prova runtime nesta ficha.

### Consequências e risco

Se o isolamento de escopo regredir, uma linha estrangeira pode alterar status ou conjunto de stages; confiança alta na relevância do contrato, ocorrência atual não demonstrada.

### Alternativas e recomendação

Preservar a correção histórica com testes dirigidos e docstring é adequado ao problema descrito. Alterar o resolvedor só faria sentido diante de divergência reproduzida; adicionar I/O aqui ampliaria a fronteira e dificultaria isolar o erro. Uma tabela parametrizada pode reduzir repetição sem enfraquecer as identidades exatas.

### Dependências e paralelismo

depends_on vazio no manifesto não significa independência funcional: ele pressupõe o resolvedor offline já existente da #115. Pode ser analisado em paralelo à integração pública, mantendo um contrato de status comum.

### Plano e aceite propostos

Plano histórico: caracterizar linhas estrangeiras; fixar o resultado execution_id_not_found para None com identidade não alvo; documentar fronteiras. Menor entrega: attribution.py/docstring e test_execution_attribution.py. eval_1 aponta a suíte focada para B-1…B-3 e eval_2 a suíte Engine para B-1/B-2; são declarações, não resultados lidos. Controle negativo: linha estrangeira não muda status nem IDs. Aceite funcional exige asserções e recibo do head pertinente; não executar ou reabrir só pela existência do manifesto.

### Comunicação entre responsáveis

Explicar na #115 que esta folha reforça a prova de uma primitiva pura; não atribui execução no caminho público. Citar cada estado, o escopo app/job e os limites da suíte offline.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Filtrar apenas por app_id deixaria uma linha de outro job alterar status ou conjunto de stages; o plano exige identidade exata app_id/job_id antes do resolvedor. Que caso o teste ainda não cobre? — O plano não fixa o caso de duas linhas estrangeiras que reutilizam o mesmo stage; os evals citados são declarações, não resultados lidos, e nada foi reexecutado. Como eu explicaria isso para outro pod? — Esta folha reforça a prova da primitiva pura com testes e docstring sobre ausência, não encontrado e conflito; não atribui execução no caminho público da #115.

### Próxima ação e encerramento

Catalogar a relação com T-20260919-execution-attribution-audit-hardening e #115. Responsável a confirmar: Engine. Entrada: plano, testes e recibos históricos quando necessários; saída: ligação rastreável e limite offline. Encerrar a revisão documental sem exigir nova implementação.

<a id="item-045"></a>

## issue115-attribution-conflict-collision.yaml — issue115-attribution-conflict-collision.yaml

Frente: Engine / colisão no conjunto de conflitos. Encaminhamento: Catalogar plano histórico de teste; preservar vínculo com #115.

### Identidade e estado

issue115-attribution-conflict-collision.yaml; TaskPlan histórico; 1 unidade(s): T-20260919-execution-attribution-conflict-collision. Origem https://github.com/luanmorenommaciel/apex/issues/115; approved=true é registro de planejamento. Owner das folhas não atribuído por esta revisão; papel Engine / colisão no conjunto de conflitos a confirmar. Arquivo na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Tornar observável uma colisão real de stage_id entre o alvo em escopo e uma linha estrangeira, protegendo o conjunto exato de conflitos. O teste anterior usava stage estrangeiro ausente do conjunto local e não discriminava esse vazamento.

### Feito, faltante e não comprovado

Uma única folha de teste em engine/tests/test_execution_attribution.py. O contrato de produção e sua documentação ficam fora do escopo; a existência deste plano não demonstra que a regressão de produto ocorria. A cópia confere com blob 607cb8d40d3efb141567766f9129b05bb492e327; nenhum teste ou aceite foi reexecutado.

### Linhagem

https://github.com/luanmorenommaciel/apex/issues/115 → manifesto issue115-attribution-conflict-collision.yaml → T-20260919-execution-attribution-conflict-collision. O inventário associa historicamente #126 (commit c6db7b93be); essa referência não prova implementação de cada comportamento. Commits, checks e aceite funcional exigem elos próprios, não inferidos do nome do arquivo.

### Fontes e corte

Fonte primária preservada: ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_issue115-attribution-conflict-collision.yaml:1; unidades T-20260919-execution-attribution-conflict-collision:L8. Git: https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/issue115-attribution-conflict-collision.yaml. Integridade: ../parte-03-claude-v2/TASKSPECS-106.json. Proposta revisada: C05-TASKSPECS-REPO.md:1774.

### Classe e limite da evidência

FATO OBSERVADO: texto do manifesto e integridade da cópia; RELATO HISTÓRICO: approved e motivação da auditoria; PROPOSTA: comportamentos/controles declarados; INFERÊNCIA: adequação documental das fronteiras; aceite humano, CI do head e runtime não certificados. YAML válido é apenas sintaxe.

### Fluxo

Stage alvo local não conflitante + mapeamento estrangeiro com mesmo stage_id + outro conflito local → resolvedor → conjunto exato de conflitos. O ID compartilhado deve continuar fora desse conjunto. Fluxo especificado, não execução revalidada.

### Consequências e risco

Um teste sem colisão real pode permanecer verde enquanto escopo estrangeiro contamina o conflito. Risco de cobertura plausível e delimitado ao cenário; sem incidente observado nesta rodada.

### Alternativas e recomendação

Manter o teste mínimo com colisão verdadeira torna a regressão discriminante. Alternativa: gerar combinações por propriedade, com maior esforço de diagnóstico. Trocar código de produção para satisfazer um teste ainda não demonstrado seria prematuro.

### Dependências e paralelismo

Não há depends_on declarado; o contexto pressupõe resolvedor e testes anteriores de atribuição. A inspeção do teste pode correr paralela ao trabalho público da #115, mas precisa preservar o mesmo significado de conflito.

### Plano e aceite propostos

Plano histórico: montar alvo local e estrangeiro com stage_id coincidente; adicionar outro conflito local; afirmar igualdade exata do conjunto. Menor entrega: um arquivo de teste. eval_1 mapeia B-1/B-2 à suíte focada; eval_2 mapeia B-1 à suíte completa. O controle é o ID coincidente não entrar no resultado. Verificar o corpo das asserções e recibo antes de aceite funcional; nenhuma execução nesta revisão.

### Comunicação entre responsáveis

Comunicar por que um stage estrangeiro exclusivo não exercitava a colisão, ilustrando o conjunto esperado. Distinguir melhoria do teste de mudança de semântica ou integração.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Usar um stage_id estrangeiro exclusivo, como no teste anterior, deixaria o teste verde mesmo se o escopo estrangeiro contaminasse o conjunto de conflitos, porque não há colisão real a discriminar. Que caso o teste ainda não cobre? — O plano fixa um caso com stage_id coincidente e outro conflito local; combinações com múltiplos conflitos locais além desse caso seguem sem cobertura, e nenhuma asserção foi reexecutada. Como eu explicaria isso para outro pod? — Com um alvo local e uma linha estrangeira que compartilham o stage_id, o ID compartilhado deve ficar fora do conjunto de conflitos; é melhoria do teste, não mudança de semântica nem integração.

### Próxima ação e encerramento

Preservar T-20260919-execution-attribution-conflict-collision como folha histórica do grupo #115/#126. Dono Engine a confirmar; saída documental: ligação e limite de teste. Reuso depende de lacuna atual demonstrada, sem reabertura automática.

<a id="item-046"></a>

## issue115-attribution-scope-collision.yaml — issue115-attribution-scope-collision.yaml

Frente: Engine / isolamento app-job. Encaminhamento: Catalogar plano histórico de teste; preservar vínculo com #115.

### Identidade e estado

issue115-attribution-scope-collision.yaml; TaskPlan histórico; 1 unidade(s): T-20260919-execution-attribution-scope-collision. Origem https://github.com/luanmorenommaciel/apex/issues/115; approved=true é registro de planejamento. Owner das folhas não atribuído por esta revisão; papel Engine / isolamento app-job a confirmar. Arquivo na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Cobrir colisões de stage_id e identidades entre aplicações/jobs para preservar os quatro resultados do resolvedor. A primeira auditoria só usava stage IDs distintos e deixava uma fronteira realista sem discriminação.

### Feito, faltante e não comprovado

Manifesto de uma folha somente de testes; observa estados absent, not_found, attributed e conflict com coincidência de IDs. Não altera resolvedor, schema, validação nem runtime. A cópia confere com blob 36b6d3194e3ee7f07f16f44cf6b04fd931101576; nenhum teste ou aceite foi reexecutado.

### Linhagem

https://github.com/luanmorenommaciel/apex/issues/115 → manifesto issue115-attribution-scope-collision.yaml → T-20260919-execution-attribution-scope-collision. O inventário associa historicamente #126 (commit 62b2c4de7c); essa referência não prova implementação de cada comportamento. Commits, checks e aceite funcional exigem elos próprios, não inferidos do nome do arquivo.

### Fontes e corte

Fonte primária preservada: ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_issue115-attribution-scope-collision.yaml:1; unidades T-20260919-execution-attribution-scope-collision:L8. Git: https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/issue115-attribution-scope-collision.yaml. Integridade: ../parte-03-claude-v2/TASKSPECS-106.json. Proposta revisada: C05-TASKSPECS-REPO.md:1794.

### Classe e limite da evidência

FATO OBSERVADO: texto do manifesto e integridade da cópia; RELATO HISTÓRICO: approved e motivação da auditoria; PROPOSTA: comportamentos/controles declarados; INFERÊNCIA: adequação documental das fronteiras; aceite humano, CI do head e runtime não certificados. YAML válido é apenas sintaxe.

### Fluxo

Linhas locais e estrangeiras com IDs reutilizados → recorte app_id/job_id → resolução → status e conjuntos exatos. Só linhas estrangeiras com None e nenhum dado local devem resultar not_found, não absent. Este é o contrato de teste declarado.

### Consequências e risco

Confundir falta de dados locais com ausência opcional de execution_id pode produzir explicação errada; misturar escopos pode atribuir stage alheio. Probabilidade de ocorrência não medida.

### Alternativas e recomendação

Recomendado conservar os casos explícitos que tornam o escopo visível. Alternativa de teste por propriedades pode explorar combinações maiores, preservando casos mínimos legíveis. Ampliar integração entre lanes não é necessário para demonstrar esta fronteira pura.

### Dependências e paralelismo

depends_on vazio; pré-requisito semântico é a primitiva de atribuição existente. Trabalho de documentação pública pode avançar em paralelo desde que não anuncie integração por este teste.

### Plano e aceite propostos

Plano histórico: reutilizar stage IDs nos quatro estados; incluir somente linhas estrangeiras nulas; afirmar status e IDs exatos. Menor entrega: test_execution_attribution.py. eval_1 declara B-1…B-3 na suíte focada; eval_2 B-1/B-2 na suíte Engine. Controle negativo distingue not_found de absent sem observação local. Aceite da folha requer recibo próprio e asserções, não contagem de evals.

### Comunicação entre responsáveis

Explicar que app_id e job_id fazem parte da chave, stage_id isolado não. Publicação da folha não resolve a integração restante da #115.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Deduplicar stage IDs antes de filtrar app_id/job_id deixaria uma linha alheia entrar no resultado, e confundir falta de dados locais com ausência opcional de execution_id produziria explicação errada. Que caso o teste ainda não cobre? — Os casos reutilizam stage IDs nos quatro estados e incluem linhas estrangeiras nulas; IDs inválidos ficam fora desta folha, e o recibo da suíte não foi lido aqui. Como eu explicaria isso para outro pod? — A chave é app_id mais job_id, não stage_id isolado: só linhas estrangeiras com None e nenhum dado local resultam em not_found, enquanto absent é ausência do campo numa observação local.

### Próxima ação e encerramento

Catalogar T-20260919-execution-attribution-scope-collision, com vínculo histórico #126 e pendência pública #115 separados. Dono Engine a confirmar; encerrar quando contrato e limites estiverem rastreáveis, sem novo dispatch.

<a id="item-047"></a>

## issue115-execution-attribution-offline.yaml — issue115-execution-attribution-offline.yaml

Frente: Engine / resolvedor puro. Encaminhamento: Catalogar contrato offline; integração pública segue na #115.

### Identidade e estado

issue115-execution-attribution-offline.yaml; TaskPlan histórico; 1 unidade(s): T-20260918-execution-stage-attribution-offline. Origem https://github.com/luanmorenommaciel/apex/issues/115; approved=true é registro de planejamento. Owner das folhas não atribuído por esta revisão; papel Engine / resolvedor puro a confirmar. Arquivo na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Consumir a identidade opcional do contrato v0.6 em uma primitiva determinística, separando atribuição exata, campo ausente, identidade não encontrada e associação conflitante. Beneficiário: consumidor de execução SQL que não pode inventar stages.

### Feito, faltante e não comprovado

A proposta cria attribution.py e seu teste sem tocar StageEvent/StageAggregate, consultas, findings, watchers, Serve ou Front. Portanto o plano não é prova de consumo público da identidade nem encerra sozinho #115. A cópia confere com blob 6010d3077725f6ee7e604fd68141c205b78d017a; nenhum teste ou aceite foi reexecutado.

### Linhagem

https://github.com/luanmorenommaciel/apex/issues/115 → manifesto issue115-execution-attribution-offline.yaml → T-20260918-execution-stage-attribution-offline. O inventário associa historicamente #126 (commit 04a4af710a); essa referência não prova implementação de cada comportamento. Commits, checks e aceite funcional exigem elos próprios, não inferidos do nome do arquivo.

### Fontes e corte

Fonte primária preservada: ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_issue115-execution-attribution-offline.yaml:1; unidades T-20260918-execution-stage-attribution-offline:L8. Git: https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/issue115-execution-attribution-offline.yaml. Integridade: ../parte-03-claude-v2/TASKSPECS-106.json. Proposta revisada: C05-TASKSPECS-REPO.md:1814.

### Classe e limite da evidência

FATO OBSERVADO: texto do manifesto e integridade da cópia; RELATO HISTÓRICO: approved e motivação da auditoria; PROPOSTA: comportamentos/controles declarados; INFERÊNCIA: adequação documental das fronteiras; aceite humano, CI do head e runtime não certificados. YAML válido é apenas sintaxe.

### Fluxo

Observações normalizadas + pedido app_id/job_id/execution_id → validação → filtro de escopo → deduplicação de stage IDs → resultado explícito e ordenado. Duplicata/tentativa repetida preserva proveniência; zero é identidade válida; conflito elimina atribuição parcial.

### Consequências e risco

Usar zero ou -1 como ausência, aceitar escopo estrangeiro ou devolver atribuição parcial pode vincular diagnóstico à execução errada. O plano define prevenção; não há medição de falha em produção nesta revisão.

### Alternativas e recomendação

Resolvedor puro e resultado tipado favorecem testes determinísticos e fronteira pequena. Alternativa de resolver diretamente no SQL mistura seleção, I/O e política; pode ser avaliada na integração, preservando os mesmos estados. Inferir vínculo a partir de stage_id global não atende o contrato de escopo.

### Dependências e paralelismo

Sem depends_on explícito; requer observações normalizadas compatíveis com identidade opcional v0.6. A incorporação no caminho Engine/Serve/Front é entrega separada em #115, com contratos e provas próprios.

### Plano e aceite propostos

Plano histórico: criar modelo/validação e resolvedor; testar os sete comportamentos; documentar status. Menor entrega: dois arquivos. eval_1 declara os sete B-n na suíte focada; eval_2 regressões de atribuição, ausência, conflito e zero. Casos negativos: identidades em branco, stage/attempt negativo, nenhum dado local, identidade estrangeira e conflito sem resultado parcial. Aceite funcional não deriva de approved=true; necessita código/asserções/recibo correlacionados.

### Comunicação entre responsáveis

Comunicar os quatro estados com exemplos, a validade de zero, a ordenação e deduplicação e a fronteira sem I/O. Nomear explicitamente as lanes ainda não conectadas.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Devolver stages parciais num conflito vincularia diagnóstico à execução errada, assim como tratar zero ou -1 como ausência ou aceitar escopo estrangeiro. Que caso o teste ainda não cobre? — O plano cobre a primitiva pura com sete comportamentos; o transporte de execution_id desde StageEvent, consultas e findings até esta função fica fora, e a integração Engine/Serve/Front segue na #115. Como eu explicaria isso para outro pod? — É um contrato puro sem I/O com quatro estados: atribuído, campo ausente, identidade não encontrada e conflito; zero é identidade válida, e isso não é dado runtime nem consumo público da identidade.

### Próxima ação e encerramento

Catalogar T-20260918-execution-stage-attribution-offline e seus refinamentos; responsável Engine a confirmar. Entrada futura para integração: contrato atual e fonte real das observações; saída documental agora: escopo offline e elos ausentes explicitados.

<a id="item-048"></a>

## issue123-audit-remediation.yaml — issue123-audit-remediation.yaml

Frente: Engine / auditoria tail-outlier. Encaminhamento: Catalogar três folhas históricas; prova integrada segue na #123.

### Identidade e estado

issue123-audit-remediation.yaml; TaskPlan histórico; 3 unidade(s): T-20260919-tail-outlier-contract-audit-hardening, T-20260919-tail-outlier-watcher-audit-hardening, T-20260919-tail-outlier-wiring-audit-hardening. Origem https://github.com/luanmorenommaciel/apex/issues/123; approved=true é registro de planejamento. Owner das folhas não atribuído por esta revisão; papel Engine / auditoria tail-outlier a confirmar. Arquivo na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Reforçar três fronteiras distintas: rejeição numérica segura do contrato TAIL_OUTLIER, consistência do finding emitido pelo watcher e capacidade dos testes de detectar remoção dos guards do pacote.

### Feito, faltante e não comprovado

O plano separa três folhas: validação pode tratar OverflowError; watcher recebe testes/documentação; wiring recebe apenas testes estruturais. Não autoriza alterar limiares, política de skew, PowerShell ou infraestrutura para obter verde. A cópia confere com blob 8f610ccdbdb2ab532ed50cc0eb5935352450a465; nenhum teste ou aceite foi reexecutado.

### Linhagem

https://github.com/luanmorenommaciel/apex/issues/123 → manifesto issue123-audit-remediation.yaml → T-20260919-tail-outlier-contract-audit-hardening, T-20260919-tail-outlier-watcher-audit-hardening, T-20260919-tail-outlier-wiring-audit-hardening. O inventário associa historicamente #127 (commit fe40eb85e4); essa referência não prova implementação de cada comportamento. Commits, checks e aceite funcional exigem elos próprios, não inferidos do nome do arquivo.

### Fontes e corte

Fonte primária preservada: ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_issue123-audit-remediation.yaml:1; unidades T-20260919-tail-outlier-contract-audit-hardening:L8; T-20260919-tail-outlier-watcher-audit-hardening:L61; T-20260919-tail-outlier-wiring-audit-hardening:L115. Git: https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/issue123-audit-remediation.yaml. Integridade: ../parte-03-claude-v2/TASKSPECS-106.json. Proposta revisada: C05-TASKSPECS-REPO.md:1834.

### Classe e limite da evidência

FATO OBSERVADO: texto do manifesto e integridade da cópia; RELATO HISTÓRICO: approved e motivação da auditoria; PROPOSTA: comportamentos/controles declarados; INFERÊNCIA: adequação documental das fronteiras; aceite humano, CI do head e runtime não certificados. YAML válido é apenas sintaxe.

### Fluxo

Evidência numérica → validador → aceitação/rejeição; agregado → watcher → finding real → mesmo validador; script de pacote → inspeção condição+throw → teste de fail-closed. Os três fluxos são complementares e não equivalem a Spark→OTLP→ClickHouse.

### Consequências e risco

Inteiro enorme pode escapar por overflow; finding emitido pode divergir do contrato; busca por texto pode passar mesmo após remoção de guard. São falhas/coberturas relatadas no contexto do plano, não nova reprodução nesta rodada.

### Alternativas e recomendação

Preservar a divisão em três folhas mantém causas e provas isoladas. Um teste monolítico live seria mais caro e dificultaria localizar regressão; grep por mensagem isolada não discrimina remoção de condição. O watcher deve manter política enquanto sua evidência é fortalecida.

### Dependências e paralelismo

A folha watcher depende explicitamente de T-20260919-tail-outlier-contract-audit-hardening; a folha wiring tem depends_on vazio e pode ser revisada em paralelo. Integração pública permanece #123; piso absoluto é decisão distinta #168.

### Plano e aceite propostos

Plano histórico: fazer conversão numérica falhar fechada; testar 99/100, razão exata/acima de 10 e isolamento skew; passar finding emitido pelo validador; exigir condição seguida do throw para job ausente, exit não zero e watcher ausente. Menores entregas: uma folha por fronteira, com suites test_contract_engine.py, test_watchers.py e test_tail_outlier_package.py. evals declaram mapeamentos por folha, mas leitura do comando não certifica a força das asserções nem runtime. Guardar recibos separados.

### Comunicação entre responsáveis

Explicar o que cada folha fortalece e o que permanece fora: nenhum ajuste de threshold e nenhuma prova do caminho live. Evidência estática de no-Crew/marker não deve ser comunicada como observação de zero chamadas.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Aceitar bool ou string como número válido, ou deixar OverflowError escapar com inteiro enorme, faria o validador do contrato TAIL_OUTLIER aprovar evidência inválida. Que caso o teste ainda não cobre? — Uma busca pelo marcador ou pela mensagem continua passando se a condição do guard for removida; por isso a folha de wiring exige condição seguida do throw, e nenhuma dessas suítes foi reexecutada. Como eu explicaria isso para outro pod? — São três folhas para três fronteiras: contrato numérico, finding emitido pelo watcher e guards do pacote; nenhuma ajusta threshold nem prova o caminho Spark→OTLP→ClickHouse.

### Próxima ação e encerramento

Catalogar as três unidades e sua dependência; responsável Engine/Package a confirmar. Encerrar esta revisão com fontes e limites por folha; eventual prova integrada deve ser planejada na #123 contra uma árvore identificada, sem reexecutar este plano por status.

<a id="item-049"></a>

## issue123-tail-outlier-engine.yaml — issue123-tail-outlier-engine.yaml

Frente: Engine / contrato e watcher de cauda. Encaminhamento: Catalogar contrato histórico; execução pública permanece #123.

### Identidade e estado

issue123-tail-outlier-engine.yaml; TaskPlan histórico aprovado no texto; unidades T-20260918-tail-outlier-finding-contract, T-20260918-tail-outlier-watcher-offline; origem https://github.com/luanmorenommaciel/apex/issues/123. Papel responsável Engine / contrato e watcher de cauda, pessoa a confirmar; arquivo na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Distinguir cauda extrema de duração de skew de join. Duas folhas definem TAIL_OUTLIER aditivo e o watcher determinístico, beneficiando usuários que precisam de um aviso fiel à evidência.

### Feito, faltante e não comprovado

A primeira folha não registra watcher; a segunda depende dela. Campo findings.type aberto evita migração DDL. Não se promete causa raiz, volume desbalanceado ou ganho de configuração.

### Linhagem

https://github.com/luanmorenommaciel/apex/issues/123 → issue123-tail-outlier-engine.yaml → T-20260918-tail-outlier-finding-contract, T-20260918-tail-outlier-watcher-offline. Inventário relaciona #127 (commit 552db1b65e) como antecedente histórico; não equivale a implementação comprovada de cada obrigação. Revisão e recibos por head não foram certificados nesta ficha.

### Fontes e corte

../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_issue123-tail-outlier-engine.yaml:1; unidades T-20260918-tail-outlier-finding-contract:L8; T-20260918-tail-outlier-watcher-offline:L66; blob 3002ca70071dccce6acf80814050dc5123a66695; https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/issue123-tail-outlier-engine.yaml. Conferência de integridade: TASKSPECS-106.json; proposta C05:1854.

### Classe e limite da evidência

FATO OBSERVADO: conteúdo preservado e sintaxe; RELATO HISTÓRICO: approved/contexto; PROPOSTA: fluxo e controles; INFERÊNCIA: adequação das fronteiras. Não houve aceite humano novo, execução de teste, CI ou runtime. Presença do manifesto não certifica implementação.

### Fluxo

Agregado de stage → população successful-task, ou fallback legado rotulado → guards de 100 tasks/100 amostras, p50 positivo e max/p50 estritamente maior que 10 → consulta de ownership ao skew atual → TAIL_OUTLIER WARNING/MEDIUM → validador. Registry torna a avaliação acessível sem Crew/LLM.

### Consequências e risco

Rotular duração como skew pode sugerir correção sem causalidade; usar população raw quando há successful-task mistura tentativas. Risco de política descrito, sem incidente atual medido.

### Alternativas e recomendação

Manter tipo separado e consultar o dono de skew evita duplicação de política. Alternativas de emitir SKEW_ON_JOIN ou suprimir todo stage com volume não respeitam a evidência. Um piso absoluto pode ser estudado em #168, sem alterar retroativamente o contrato desta entrega.

### Dependências e paralelismo

Watcher depende explicitamente do contrato. Wiring, prova real e consumidores são recortes próprios: #123 e #166. Revisão dos consumidores pode correr em paralelo com estudo de escala.

### Plano e aceite propostos

Preservar duas entregas: contrato/validador e watcher/registro. No contrato, eval_1 declara B-1…B-4 com casos válidos, faltantes e skew inalterado; no watcher, eval_1 declara B-1…B-7 com successful-task, legado, 99/100, razão=10, skew real, alto volume sem dono e registry. Suítes completas são regressão declarada. Avaliar asserções/recibos antes de concluir cobertura; nada executado.

### Comunicação entre responsáveis

Explicar que cauda é sintoma e que ausência de Crew é contrato offline; nomear fonte da população e os guards. A #127 é relação histórica, não recibo suficiente de runtime.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Classificar duração como skew sugeriria correção sem causalidade, e usar população raw quando há successful-task misturaria tentativas. Que caso o teste ainda não cobre? — O transporte das métricas effective até o watcher fica fora do plano; os evals declaram casos de 99/100, razão igual a 10, skew real e alto volume sem dono, mas as asserções não foram lidas aqui. Como eu explicaria isso para outro pod? — TAIL_OUTLIER é sintoma de cauda, separado de SKEW_ON_JOIN, sem Crew/LLM e sem promessa de causa raiz; a #127 é relação histórica, e #166 e #168 tratam consumidores e piso absoluto.

### Próxima ação e encerramento

Catalogar as duas unidades; dono Engine a confirmar. Entrada para qualquer mudança: comportamento atual e lacuna específica; saída agora: contrato preservado e vínculos #123/#166/#168 separados.

<a id="item-050"></a>

## issue123-tail-outlier-package-wiring.yaml — issue123-tail-outlier-package-wiring.yaml

Frente: Package / roteamento tail-outlier. Encaminhamento: Catalogar wiring histórico; não converter prova estática em runtime.

### Identidade e estado

issue123-tail-outlier-package-wiring.yaml; TaskPlan histórico aprovado no texto; unidades T-20260918-tail-outlier-package-wiring-offline; origem https://github.com/luanmorenommaciel/apex/issues/123. Papel responsável Package / roteamento tail-outlier, pessoa a confirmar; arquivo na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Conectar a ação pública tail-outlier ao cenário canônico já existente, removendo bloqueio incondicional antigo e preservando falha explícita quando falta identidade, Engine falha ou watcher não aparece.

### Feito, faltante e não comprovado

Uma folha altera o runner PowerShell e scripts/apex.ps1 e acrescenta teste de pacote. O próprio plano restringe aceite à rota offline; B-4 descreve sucesso live futuro, apesar de eval_1 declarar que o verifica.

### Linhagem

https://github.com/luanmorenommaciel/apex/issues/123 → issue123-tail-outlier-package-wiring.yaml → T-20260918-tail-outlier-package-wiring-offline. Inventário relaciona #127 (commit 8b772ed76f) como antecedente histórico; não equivale a implementação comprovada de cada obrigação. Revisão e recibos por head não foram certificados nesta ficha.

### Fontes e corte

../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_issue123-tail-outlier-package-wiring.yaml:1; unidades T-20260918-tail-outlier-package-wiring-offline:L8; blob 5660e463bf0b62b80a734d6b826a93a370c98e1a; https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/issue123-tail-outlier-package-wiring.yaml. Conferência de integridade: TASKSPECS-106.json; proposta C05:1874.

### Classe e limite da evidência

FATO OBSERVADO: conteúdo preservado e sintaxe; RELATO HISTÓRICO: approved/contexto; PROPOSTA: fluxo e controles; INFERÊNCIA: adequação das fronteiras. Não houve aceite humano novo, execução de teste, CI ou runtime. Presença do manifesto não certifica implementação.

### Fluxo

Comando tail-outlier → Invoke-TailOutlierGate → Scenario tail_outlier → workload tail_outlier.py → job_id → Engine dry-run/no-Crew → guarda de exit/watcher → marcador passed. Setas de execução são contrato, não percurso executado nesta auditoria.

### Consequências e risco

Remover um throw sem preservar guards pode produzir sucesso sem evidência; marcador llm_calls=0 impresso não mede chamadas reais. Confiança alta na distinção de prova, ocorrência atual não reproduzida.

### Alternativas e recomendação

Roteamento compartilhado com guards explícitos é preferível a um atalho específico que ignore cenário/identidade. Teste estrutural é barato, mas prova live separada é necessária para alegar integração; não se resolve essa diferença ampliando o texto do marcador.

### Dependências e paralelismo

depends_on está vazio, porém contexto pressupõe workload e watcher existentes. Aceite de integração precisa do ambiente próprio e evidência por job/stage em #123; higiene E17 permanece nessa issue.

### Plano e aceite propostos

Plano histórico mínimo: aceitar/mapear cenário, retirar bloqueio obsoleto, preservar três falhas e marcador. eval_1 lista testes de mapping, alcance e fail-closed e declara B-1…B-5; eval_2 cobre regressão root. Leitura estática só sustenta estrutura para B-4, não sucesso live. Controle negativo deve falhar se cada guarda for removida; recibos offline e runtime ficam separados.

### Comunicação entre responsáveis

Na comunicação, identificar arquivos de roteamento, guards e qual prova é apenas source/DryRun. Não dizer que o comando live funciona porque o teste encontrou o nome do watcher.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Aceitar qualquer saída do Engine como sucesso, ao remover o throw antigo sem preservar os guards de identidade, falha do Engine e watcher ausente, produziria PASS sem evidência. Que caso o teste ainda não cobre? — A correspondência entre finding e stage fica fora desta folha; a leitura estática sustenta a estrutura de B-4, não o sucesso live, e o marcador llm_calls=0 impresso não mede chamadas. Como eu explicaria isso para outro pod? — A folha liga o comando tail-outlier ao cenário canônico com três falhas explícitas; rota testada offline e execução live são provas separadas, e esta última fica na #123.

### Próxima ação e encerramento

Catalogar T-20260918-tail-outlier-package-wiring-offline; dono Package a confirmar. Encerrar a ficha documental com limite B-4 explícito. Provas posteriores só preenchem lacuna na #123 para SHA/cenário identificados.

