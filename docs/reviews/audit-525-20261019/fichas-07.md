# Fichas documentais — lote 7

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-061"></a>

## serve-api-wire.yaml — serve-api-wire.yaml

Frente: Serve / contrato de tempo e paridade live. Encaminhamento: Catalogar plano histórico; preservar NOT EXERCISED.

### Identidade e estado

serve-api-wire.yaml; TaskPlan histórico com 2 unidades: T-20260929-wire-timestamp-format, T-20260929-console-parity-live-gate. Origem tasks/.plans/serve-api-sweep.yaml; responsável Serve / contrato de tempo e paridade live, pessoa a confirmar. Literal approved=true não é autorização atual nem aceite das folhas.

### Intenção e benefício

Duas folhas unificam timestamps de recursos API/ClickHouse/fixtures e comparam linhas pelos dois caminhos reais. O objetivo é provar conteúdo e semântica de Store que um status HTTP 200 não demonstra.

### Feito, faltante e não comprovado

O plano distingue formato aprovado no relato do owner e refinamento de precisão proposto. A execução live tem modo fixture próprio e --job-id sem escrita. O manifesto não comprova que cada cenário foi exercitado.

### Linhagem

tasks/.plans/serve-api-sweep.yaml → serve-api-wire.yaml → unidades nomeadas no campo 1. O inventário associa #153 (commit 9841119362); relação histórica, não implementado_por. Commits/CI/revisões/aceites requerem recibos separados; esta ficha não certifica a implementação de cada folha.

### Fontes e corte

../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_serve-api-wire.yaml:1; unidades T-20260929-wire-timestamp-format:L13; T-20260929-console-parity-live-gate:L93. Blob 571d1f9ed2e76ef1788b957cbb9c89f892f4c32e na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/serve-api-wire.yaml. Auditoria de declarações: _build/spec-audit.json; correções D e F da Parte04.

### Classe e limite da evidência

FATO OBSERVADO: conteúdo preservado, integridade e carregamento YAML; RELATO HISTÓRICO: approved, motivação e resultados narrados; PROPOSTA: contratos/controles; INFERÊNCIA: adequação documental. Nenhum teste, serviço, publicação ou aceite humano novo.

### Fluxo

datetime/strings em chaves de tempo → normalizador de fronteira HTTP e mappers Front → UTC com milissegundos → comparação browser SQL versus API; dados inadequados → NOT EXERCISED. MCP/ReadStore mantêm datetimes para aritmética.

### Consequências e risco

Remover offset sem conversão muda instante; normalizar todo texto altera evidência não confiável; comparar só 200 deixa regressões de linhas invisíveis. Probabilidade atual não medida.

### Alternativas e recomendação

Normalizadores na fronteira preservam MCP e SQL. Alternativa de formatDateTime nas queries amplia superfície de aliases; padrão ISO com offset explícito seria outro contrato, não decisão desta revisão. Para store não mutável, --job-id conserva limites e não finge cobrir cenário ausente.

### Dependências e paralelismo

Gate depende de wire-timestamp-format para comparar representações equivalentes. Prova readonly é propriedade dos caminhos sob teste; fixture pode escrever somente seus próprios dados quando autorizada. A #159 trata evolução posterior do gate.

### Plano e aceite propostos

Contratos de tempo: naive/aware/fuso/fracionamento, mesmo instante, desconhecido/null/texto intocados, três repositories, MCP inalterado. Gate: linhas iguais, run sem outcome sentinela, SQL literal como apex_ro, ordering de findings e último update_seq. evals offline verificam normalização/extração; eval live requer dados adequados e recibo. NOT EXERCISED não conta como passed. Menor reuso: caso faltante com IDs próprios, cleanup restrito, documentação do alcance.

### Comunicação entre responsáveis

Comunicar equivalência de instantes e a diferença entre fixture que escreve e query read-only. Incluir cenários não exercitados e não transferir resultado para head posterior.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Apenas remover o +02:00 sem converter mudaria o instante, e normalizar todo texto alteraria evidência não confiável; o normalizador fica na fronteira HTTP e nos mappers do Front, com MCP inalterado. Que caso o teste ainda não cobre? — Store com um só finding ou nenhuma transição não exercita a ordenação nem o último update_seq e deve aparecer como NOT EXERCISED, que não conta como passed; o manifesto não comprova que cada cenário foi exercitado. Como eu explicaria isso para outro pod? — Formato de tempo e semântica de Store são provas diferentes: o mesmo instante em UTC com milissegundos nas duas portas, e linhas iguais via SQL e API; fixture que escreve é distinta de query read-only com --job-id.

### Próxima ação e encerramento

Catalogar duas unidades; dono Serve/Front a confirmar. Reconciliar recibos #156 e evolução #159 antes de nova prova; encerrar documentalmente com cenário, origem e limite explícitos.

<a id="item-062"></a>

## serve-api.yaml — serve-api.yaml

Frente: Serve / API HTTP e adaptação da Console. Encaminhamento: Catalogar plano histórico inválido como YAML; preservar oito contratos.

### Identidade e estado

serve-api.yaml; TaskPlan histórico com 8 unidades: T-20260920-api-skeleton, T-20260920-readstore-console-queries, T-20260920-api-diagnostic-routes, T-20260920-api-resource-routes, T-20260920-console-http-repository, T-20260920-api-openapi-auth, T-20260921-console-same-origin-api, T-20260921-pr129-review-fixes. Origem brain/01-projects/apex/08-meetings/krisp/2026-09-15-weekly-sync-crew-a-apex.md; responsável Serve / API HTTP e adaptação da Console, pessoa a confirmar. Literal approved=true não é autorização atual nem aceite das folhas.

### Intenção e benefício

Oito unidades constroem API FastAPI sobre ReadStore e tools MCP, portas das queries Console, HttpRepository, OpenAPI, proxy same-origin e correções da revisão. O ganho é expor dados/diagnóstico sem duplicar a lógica de análise.

### Feito, faltante e não comprovado

YAML rejeitado na linha 20; conteúdo foi lido textualmente. Existe divergência interna: Goal/B-1 de recursos diz doze métodos, Context diz onze mais kind; não usar o número como contrato sem conferir interface. approved e PR relacionada não provam todas as projeções.

### Linhagem

brain/01-projects/apex/08-meetings/krisp/2026-09-15-weekly-sync-crew-a-apex.md → serve-api.yaml → unidades nomeadas no campo 1. O inventário associa #129 (commit 7fb0879aa0); relação histórica, não implementado_por. Commits/CI/revisões/aceites requerem recibos separados; esta ficha não certifica a implementação de cada folha.

### Fontes e corte

../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_serve-api.yaml:1; unidades T-20260920-api-skeleton:L8; T-20260920-readstore-console-queries:L96; T-20260920-api-diagnostic-routes:L151; T-20260920-api-resource-routes:L212; T-20260920-console-http-repository:L284; T-20260920-api-openapi-auth:L345; T-20260921-console-same-origin-api:L395; T-20260921-pr129-review-fixes:L456. Blob acbce1eba89383292d0f3eacdd35fba08996474c na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/serve-api.yaml. Auditoria de declarações: _build/spec-audit.json; correções D e F da Parte04.

### Classe e limite da evidência

FATO OBSERVADO: conteúdo preservado, integridade e falha de parsing reproduzida na auditoria; RELATO HISTÓRICO: approved, motivação e resultados narrados; PROPOSTA: contratos/controles; INFERÊNCIA: adequação documental. Nenhum teste, serviço, publicação ou aceite humano novo.

### Fluxo

HTTP /v1 → admissão bearer antes de consulta → router → tool MCP ou ReadStore → envelope sanitizado; recursos → HttpRepository → telas; health é público, schema/docs historicamente públicos; nginx/Vite fazem proxy quando apiUrl vazio.

### Consequências e risco

Método com nome parecido pode retornar projeção diferente; HTTP 200 não prova campos; configuração de proxy pode passar grep e falhar em nginx. As correções históricas registram essas fronteiras, sem novo incidente inferido.

### Alternativas e recomendação

Adapter sobre MCP reutiliza análise; queries de Console precisam projeção explícita, não associação por nome. Same-origin evita exigir CORS no caso padrão; apiUrl absoluto continua alternativa deliberada. Exposição docs/token é decisão #171, Ask/BFF é #122.

### Dependências e paralelismo

Skeleton e leitura podem ser paralelos; diagnóstico depende do skeleton; recursos de ambos; HttpRepository depende de recursos; OpenAPI também; same-origin segue repository; review-fixes segue same-origin. Decisões de token v1 não equivalem à arquitetura Ask.

### Plano e aceite propostos

Preservar oito folhas: auth/health/sanitização, seis query ports, paridade tool-route, recursos com ausência/truncamento, adapter com 401 sem fallback, OpenAPI fiel, proxy/config e fixes nginx/projeção/stages. Controles negativos: token ausente/incorreto sem query, DSN fictício, job inexistente, memory ausente e binding hostil. Corrigir sintaxe antes de reuso e reconciliar onze métodos+kind; procurar recibos de nginx real/linhas e não inferir sucesso de grep.

### Comunicação entre responsáveis

Comunicar API como transporte e projeções específicas como contratos, distinguindo schema de enforcement. O contexto histórico de FastAPI não é análise de dependências atual. Nomear lacunas nginx/browser separadamente.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Mapear a API pelo nome da função pode devolver projeção diferente da que a Console esperava; o plano exige projeção explícita por query port, e o YAML falha no safe_load na linha 20. Que caso o teste ainda não cobre? — Um fake que retorna campos que a SQL omite passa; HTTP 200 não prova campos, um proxy pode passar no grep e falhar no nginx, e o plano diverge entre doze métodos e onze mais kind. Como eu explicaria isso para outro pod? — Health é público, a admissão bearer em /v1 ocorre antes de qualquer consulta e os dados vêm por tool MCP ou ReadStore; exposição de docs e custódia do token são da #171, e Ask/BFF da #122.

### Próxima ação e encerramento

Catalogar oito unidades com contexto #129/#153; dono Serve/Front a confirmar. Saída: síntese completa e limite de parsing; eventual reuso requer base/interface e prova atuais, sem reabrir a PR histórica por sintaxe.

<a id="item-063"></a>

## P01 — PR #126 — atribuição offline execution→stages

Frente: registro_associado_issues_centrais. Encaminhamento: encerrar_entrega_historica_preservando_residuos.

### Identidade e estado

ID canônico P01: PR #126 — atribuição offline execution→stages. Origem preservada no registro de 158 IDs; acompanhamento [#115](fichas-02.md#item-014). Responsável do próximo passo a confirmar. Disposição: encerrar_entrega_historica_preservando_residuos.

### Intenção e benefício

Entregar o resolver offline de execution_id para stages, com identidade opcional explícita e proteção de escopo. O objeto P01 é a entrega da PR #126; E02 e E01 tratam integração e prova real.

### Feito, faltante e não comprovado

PR #126 integrada. Na fonte atual, o resolver e testes já distinguem zero de None, escopo vazio de ausência opcional e conflito do mesmo stage. A formulação histórica de testes de zero ainda faltantes está superada. A função pura não consulta storage nem integra consumidores; merge não prova runtime.

### Linhagem

P01 → #126 (head 4ddb082cf8e916736e336d6a5554bccbba083a19; merge abed50893977e14dcf70ffdc4274e70793b76030 em 06/10) → código atual; #115 permanece como guarda-chuva. E02/E01 recebem resíduos distintos.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md#reg-p01, linha 273; CSV, MATRIX e PUBLICATION preservados. Fontes primárias, datas e SHA de código são os da ficha [#115](fichas-02.md#item-014), relacionadas abaixo. Código APEX fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; estados públicos são os recibos de 16–17/10, não uma consulta implícita nova.

### Classe e limite da evidência

DIRETO ESTÁTICO: trechos e metadados descritos nos campos 3–5 e na ficha [#115](fichas-02.md#item-014). RELATO: execuções/resultados históricos ali atribuídos. INFERÊNCIA: riscos condicionais do campo 8. PROPOSTA: opções e menor prova futura; nenhuma decisão de mantenedor, execução de produto ou publicação nova nesta revisão.

### Fluxo

Observações tipadas → filtro app/job → execução alvo → stages distintos ou absent/not_found/conflict. stage_attempt participa da proveniência sem duplicar membership. Zero é ID real.

### Consequências e risco

Reabrir P01 por controles já existentes duplica trabalho. Fechá-lo como entrega histórica sem conservar E01/E02 apagaria requisitos públicos. Não se demonstrou regressão atual.

### Alternativas e recomendação

Catalogar P01 como entrega integrada e manter resíduos vinculados. Uma revisão nova da política de IDs, se desejada, deve indicar qual exigência atual foi contrariada; não presumir que uma decisão histórica continua bloqueando o merge ocorrido.

### Dependências e paralelismo

G01 era condição operacional histórica; não bloqueia o registro do merge. O contrato existente pode ser reutilizado por E02. Prova runtime de E01 continua separada da integração da PR.

### Plano e aceite propostos

Conferir identidade da PR e ligação ao resolver; registrar controles já presentes; apontar E02/E01. Aceite documental: P01 não é proposto novamente e não carrega certificação runtime. Controle negativo da consolidação: zero não pode ser catalogado como sentinel ausente.

### Comunicação entre responsáveis

Explicar que o componente offline foi integrado, mas o produto ainda precisa selecionar e provar o consumidor. Referenciar testes existentes pelo comportamento, sem convertê-los em execução nova.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Reabrir P01 por controles de zero e conflito que já existem duplicaria trabalho, e encerrá-lo sem manter E01 e E02 apagaria requisitos públicos da #115. Que caso o teste ainda não cobre? — Os testes já distinguem zero de None e tratam dois stages da mesma execução como atribuição válida, não conflito; integração no consumidor e prova SQL/RDD ficam em E02 e E01. Como eu explicaria isso para outro pod? — O resolver offline da #126 foi integrado e não consulta storage nem consumidores; merge não prova runtime, e escolher e provar o consumidor é o passo seguinte.

### Próxima ação e encerramento

Curador: registrar entrega histórica encerrada e vínculos E01/E02/#115; reabrir somente por lacuna específica nova. Não há nova PR ou teste de produto exigido apenas para catalogar o merge.

<a id="item-064"></a>

## P02 — PR #127 — gate determinístico tail-outlier

Frente: registro_associado_issues_centrais. Encaminhamento: encerrar_pr_integrada_e_reconciliar_runtime_historico.

### Identidade e estado

ID canônico P02: PR #127 — gate determinístico tail-outlier. Origem preservada no registro de 158 IDs; acompanhamento [#123](fichas-02.md#item-016). Responsável do próximo passo a confirmar. Disposição: encerrar_pr_integrada_e_reconciliar_runtime_historico.

### Intenção e benefício

Entregar watcher determinístico, cenário canônico e caminho público tail-outlier. O objeto representa #127 e não absorve toda compatibilidade de ambiente ou higiene futura do gate.

### Feito, faltante e não comprovado

PR #127 integrada e caminho presente. Há dois runtimes relatados: núcleo em 20/09 e wrapper macOS/Spark 4.0.1 em 21/09. Corrigir a associação do registro: 373,364× pertence ao núcleo de 200 tarefas, não está demonstrado para app-20260921024421-0001 do wrapper. Sem nova validação de logs ou main atual.

### Linhagem

P02 → #127, head 4e44bfdce5586fe9b8ed7c96e41932b55f231a88 e merge fec8a7fb0b3669343725141ab60eef0d8dff74a0 → #123 ainda aberta. E14 trata suporte; E16/#167 interface; E17/#123 predicado do gate; E08/#174 e E09/#175 protegem operação.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md#reg-p02, linha 293; CSV, MATRIX e PUBLICATION preservados. Fontes primárias, datas e SHA de código são os da ficha [#123](fichas-02.md#item-016), relacionadas abaixo. Código APEX fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; estados públicos são os recibos de 16–17/10, não uma consulta implícita nova.

### Classe e limite da evidência

DIRETO ESTÁTICO: trechos e metadados descritos nos campos 3–5 e na ficha [#123](fichas-02.md#item-016). RELATO: execuções/resultados históricos ali atribuídos. INFERÊNCIA: riscos condicionais do campo 8. PROPOSTA: opções e menor prova futura; nenhuma decisão de mantenedor, execução de produto ou publicação nova nesta revisão.

### Fluxo

Workload tail_outlier → telemetria → asserção canônica → Engine determinístico → marcador do wrapper. Os dois recibos históricos têm ambientes/jobs distintos; o PASS atual está limitado ao predicado descrito na ficha #123.

### Consequências e risco

Misturar números de dois jobs produz prova inexata. Atribuir cold start à prova com cache e recursos parciais superestima suporte. Chamar todo runtime de ausente também é incorreto.

### Alternativas e recomendação

Encerrar a unidade PR integrada e reconciliar critérios de #123 com evidência histórica delimitada. Uma nova execução pode cobrir o resíduo escolhido, sem repetir implementação já existente. Não impor retroativamente as condições pré-merge como se o merge não tivesse ocorrido.

### Dependências e paralelismo

G01 e DEC-10 são contexto histórico da integração. Uso futuro depende das condições reais de ambiente; não foram autorizadas operações aqui. Associação forte e matriz de plataformas dependem de escolhas próprias.

### Plano e aceite propostos

Separar no mapa os dois jobs, datas, versões declaradas, comandos e resultados; manter cache/reuso como limites. Aceite documental: PR integrada catalogada, número 373,364 ligado ao núcleo correto e follow-ups com destino. Não preencher lacunas do wrapper com números do núcleo.

### Comunicação entre responsáveis

Comunicar três estados: código integrado, runtime histórico relatado e suporte/associação ainda delimitados. O corpo da PR e o delivery record são relatos verificáveis, não resultados reproduzidos nesta auditoria.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Misturar números dos dois jobs produziria prova inexata: o ratio 373,364 pertence ao núcleo de 200 tarefas de 20/09, não ao app-20260921024421-0001 do wrapper. Que caso o teste ainda não cobre? — A prova do wrapper usou cache de imagens e recursos parciais, não cold start; Windows, associação ao stage e a main atual não ficam cobertos pelo runtime relatado. Como eu explicaria isso para outro pod? — Há três estados: código integrado pela #127, runtime histórico relatado em dois ambientes e suporte e associação ainda delimitados na #123; encerrar P02 não equivale a release certificada.

### Próxima ação e encerramento

Curador e mantenedor: preservar P02 encerrado como entrega integrada e reconciliar #123/E14/E17 sem duplicar o trabalho. Encerramento deste ID não equivale a release certificada.

<a id="item-065"></a>

## P03 — PR #128 — cobertura PowerShell command-aware

Frente: registro_associado_issues_centrais. Encaminhamento: pr_integrada_com_criterio_dispatch_ainda_pendente.

### Identidade e estado

ID canônico P03: PR #128 — cobertura PowerShell command-aware. Origem preservada no registro de 158 IDs; acompanhamento [#124](fichas-02.md#item-017). Responsável do próximo passo a confirmar. Disposição: pr_integrada_com_criterio_dispatch_ainda_pendente.

### Intenção e benefício

Entregar exigência explícita de pwsh e cobertura por ação. P03 representa #128; a satisfação de cada critério da issue #124 é uma avaliação adicional.

### Feito, faltante e não comprovado

PR #128 integrada. Ausência de pwsh falha explicitamente e dry-run compara oito rótulos Handler. Ainda falta observar a invocação de Command: trocar somente o scriptblock mantém a string e escapa da asserção. Portanto não resta somente uma decisão administrativa de fechamento, como dizia a ficha anterior.

### Linhagem

P03 → #128, head 2b84c7a14fbcc5c009a3366536ccb80ebe316ca0 e merge d8c1a3c67948c047ea282ca4d839462153b4e60a → #124 aberta. G04 reconcilia os critérios; G08 preserva testes históricos da combinação #127×#128 sem lhes atribuir força adicional.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md#reg-p03, linha 313; CSV, MATRIX e PUBLICATION preservados. Fontes primárias, datas e SHA de código são os da ficha [#124](fichas-02.md#item-017), relacionadas abaixo. Código APEX fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; estados públicos são os recibos de 16–17/10, não uma consulta implícita nova.

### Classe e limite da evidência

DIRETO ESTÁTICO: trechos e metadados descritos nos campos 3–5 e na ficha [#124](fichas-02.md#item-017). RELATO: execuções/resultados históricos ali atribuídos. INFERÊNCIA: riscos condicionais do campo 8. PROPOSTA: opções e menor prova futura; nenhuma decisão de mantenedor, execução de produto ou publicação nova nesta revisão.

### Fluxo

Ação → objeto {Handler string, Command scriptblock}; DryRun imprime string e sai; modo normal chama Command. A comparação de string é prova do plano anunciado, não da chamada.

### Consequências e risco

Catalogar a PR como integrada é correto. Afirmar que roteamento está integralmente provado ou só falta CI obscurece o critério público de dispatcher. Não foi observado mapeamento de produção incorreto.

### Alternativas e recomendação

Preservar o merge e registrar follow-up dentro da #124 para controle discriminante com stubs seguros. Não exigir desfazer a PR; não rebaixar a lacuna a melhoria opcional apenas para fechar a issue.

### Dependências e paralelismo

A revisão offline de dispatch independe de Docker/Spark e de uma decisão geral de billing. CI aplicável ajuda a comprovar execução do teste escolhido; um verde não acrescenta uma asserção ausente.

### Plano e aceite propostos

Registrar o que a PR satisfez e o que não foi demonstrado. Proposta de menor prova: chamar dispatcher com handlers inofensivos para cada ação; mutar alvo preservando Handler deve falhar. Documentação macOS/Linux deve ter fonte. Nenhum desses testes foi executado nesta auditoria.

### Comunicação entre responsáveis

Usar a formulação PR integrada; critério de invocação ainda pendente. Separar relato de 18/69 testes da #128 de prova do comportamento que cada asserção observa.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Afirmar que o roteamento está provado, ou que só falta CI, esconderia o critério público de dispatcher: trocar só o scriptblock Command mantém a string Handler e passa na asserção. Que caso o teste ainda não cobre? — Nenhuma asserção vê Handler certo com Command errado, porque o DryRun imprime o plano e sai sem invocar o dispatcher; um CI verde só executa as asserções que existem. Como eu explicaria isso para outro pod? — A PR #128 está integrada e torna explícita a exigência de pwsh; o critério de invocação real do Command segue pendente na #124, e catalogar P03 não fecha a issue.

### Próxima ação e encerramento

Curador: manter P03 como PR integrada e sinalizar #124/G04 com lacuna concreta. Mantenedor decide implementação do controle ou altera formalmente o critério; não fechar #124 por mera catalogação de P03.

<a id="item-066"></a>

## E01 — Provar #126 em runtime completo

Frente: registro_associado_issues_centrais. Encaminhamento: prova_runtime_delimitada_a_planejar.

### Identidade e estado

ID canônico E01: Provar #126 em runtime completo. Origem preservada no registro de 158 IDs; acompanhamento [#115](fichas-02.md#item-014). Responsável do próximo passo a confirmar. Disposição: prova_runtime_delimitada_a_planejar.

### Intenção e benefício

Demonstrar que a identidade SQL opcional chega à superfície escolhida e que os stages retornados correspondem ao workload real; preservar RDD sem identidade SQL.

### Feito, faltante e não comprovado

Resolver offline integrado e controles de chave presentes. Neste recorte não foi localizado recibo que satisfaça a prova SQL/RDD da #115. Isso é lacuna de evidência consultada, não afirmação universal de que nunca houve qualquer execução.

### Linhagem

Produtor #96 → resolver #126/P01 → decisão de superfície E02 → prova E01 sob #115. E01 não é uma implementação adicional do produtor nem reabertura do ledger #78.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/C03b-REGISTRO-E.md#reg-e01, linha 8; CSV, MATRIX e PUBLICATION preservados. Fontes primárias, datas e SHA de código são os da ficha [#115](fichas-02.md#item-014), relacionadas abaixo. Código APEX fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; estados públicos são os recibos de 16–17/10, não uma consulta implícita nova.

### Classe e limite da evidência

DIRETO ESTÁTICO: trechos e metadados descritos nos campos 3–5 e na ficha [#115](fichas-02.md#item-014). RELATO: execuções/resultados históricos ali atribuídos. INFERÊNCIA: riscos condicionais do campo 8. PROPOSTA: opções e menor prova futura; nenhuma decisão de mantenedor, execução de produto ou publicação nova nesta revisão.

### Fluxo

Workload e identidade esperada → JAR/OTLP/ClickHouse → adapter/resolver escolhido → stages observados confrontados com esperado; controle RDD → estado opcional explícito.

### Consequências e risco

Fixture não comprova entrega ou schema aplicado. Confundir zero com ausência ou omitir escopo pode atribuir stages alheios. Não se demonstrou ocorrência desses danos.

### Alternativas e recomendação

Planejar a menor prova que satisfaça os critérios públicos e registrar casos adicionais como proposta. Pode-se preparar um probe de atributos antes da UI final; a execução deve declarar exatamente a superfície que observa.

### Dependências e paralelismo

A definição da superfície/adapter e o ambiente identificável condicionam a execução. O desenho da matriz pode ocorrer em paralelo a E02. Não exigir terminar Engine, Serve e Front para começar a planejar o controle SQL/RDD.

### Plano e aceite propostos

Definir workload SQL, conjunto esperado e controle RDD; incluir zero, retry e colisões conforme a fronteira escolhida sem fingir que já são prova real. Registrar SHA, comando, app/job/exec/stage/tentativa, população, RC e saída sanitizada. Negativo: identidade de outro app/job não entra no conjunto. Critérios adicionais devem ser ratificados antes de virar gate.

### Comunicação entre responsáveis

Distinguir key/optional/conflict testados offline de transporte/schema/atribuição observados em runtime. Não prometer certificação do sistema inteiro a partir de um workload.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Tratar fixture como prova de entrega ou de schema aplicado, ou confundir zero com ausência, poderia atribuir stages alheios sem que o recibo mostrasse isso. Que caso o teste ainda não cobre? — O conjunto esperado de stages não pode ser derivado do mesmo código sob teste; faltam o controle RDD sem execution_id, a identidade zero preservada e a colisão entre duas aplicações, e não foi localizado recibo SQL/RDD neste recorte. Como eu explicaria isso para outro pod? — O que foi testado offline são chave, opcionalidade e conflito; a prova runtime observa transporte, schema e atribuição na superfície escolhida, sem certificar o sistema inteiro a partir de um workload.

### Próxima ação e encerramento

Owner Engine a confirmar: produzir plano/recibo da prova autorizada quando a superfície estiver definida. Encerrar E01 após confronto dos critérios SQL/RDD com evidência real, sem execução nesta revisão.

<a id="item-067"></a>

## E02 — Integrar atribuição de stages aos consumidores (T24b–d)

Frente: registro_associado_issues_centrais. Encaminhamento: decidir_superficie_e_integrar_sem_gate_de_tres_prs.

### Identidade e estado

ID canônico E02: Integrar atribuição de stages aos consumidores (T24b–d). Origem preservada no registro de 158 IDs; acompanhamento [#115](fichas-02.md#item-014). Responsável do próximo passo a confirmar. Disposição: decidir_superficie_e_integrar_sem_gate_de_tres_prs.

### Intenção e benefício

Expor a atribuição nos consumidores sem perder estados de ausência/conflito. O benefício é informação específica quando disponível e nível de job honesto quando não disponível.

### Feito, faltante e não comprovado

O comentário de 17/09 lista Engine/Serve/Front. O resolver já existe; AQE usa sentinel de job intencional e a disponibilidade Front permanece false. O comentário é uma lista de resíduos, não aceite explícito de uma ordem rígida ou exatamente três PRs.

### Linhagem

P01/#126 → E02 sob #115; DEC-09 corresponde à escolha da primeira superfície. E01 é prova runtime complementar. #169 pode influir em seleção de tentativa, sem revogar o contrato offline atual.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/C03b-REGISTRO-E.md#reg-e02, linha 42; CSV, MATRIX e PUBLICATION preservados. Fontes primárias, datas e SHA de código são os da ficha [#115](fichas-02.md#item-014), relacionadas abaixo. Código APEX fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; estados públicos são os recibos de 16–17/10, não uma consulta implícita nova.

### Classe e limite da evidência

DIRETO ESTÁTICO: trechos e metadados descritos nos campos 3–5 e na ficha [#115](fichas-02.md#item-014). RELATO: execuções/resultados históricos ali atribuídos. INFERÊNCIA: riscos condicionais do campo 8. PROPOSTA: opções e menor prova futura; nenhuma decisão de mantenedor, execução de produto ou publicação nova nesta revisão.

### Fluxo

Adapter tipado da fonte escolhida → resolver → estado/identidade → representação consumível → UI ou API selecionada. Findings de nível de job permanecem de job onde não houver atribuição válida.

### Consequências e risco

Trocar -1 por um stage arbitrário cria precisão falsa. Ativar flag Front antes de expor dados coerentes promete suporte inexistente. Impor três PRs mede embalagem, não comportamento.

### Alternativas e recomendação

Escolher uma primeira superfície pequena e ampliar conforme necessidade. Engine primeiro é opção, Serve/query também constam no corpo. Não confundir recomendação da revisão com decisão tomada pelo owner.

### Dependências e paralelismo

Produtor e resolver já integrados. Decisão de contrato do consumidor precede sua implementação; revisão de integração e controles pode ocorrer em paralelo à preparação de E01. #117 não é predecessor global.

### Plano e aceite propostos

Definir schema de observação e resposta; implementar adapter/consumidor mínimo; testar attributed, absent, not_found e conflict incluindo zero e escopo estrangeiro. Aceite: o consumidor não inventa stage, flag reflete suporte real e critérios de #115 são reconciliados. A quantidade de PRs é escolha de revisão.

### Comunicação entre responsáveis

Explicar o estado que cada consumidor recebe e mostra, com um exemplo positivo e outro ausente/conflitante. Não anunciar que todos os watchers precisam ser convertidos.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Trocar o sentinel -1 por um stage arbitrário criaria precisão falsa, e ativar a flag do Front antes de expor dados coerentes prometeria suporte inexistente; contar três PRs mediria embalagem, não comportamento. Que caso o teste ainda não cobre? — Faltam os estados attributed, absent, not_found e conflict no consumidor escolhido, inclusive zero e escopo estrangeiro; não há necessidade demonstrada de mudar thresholds ou schema. Como eu explicaria isso para outro pod? — O dono da primeira superfície ainda não foi decidido; findings sem atribuição válida continuam de nível de job, e o usuário precisa ver o conflito como estado próprio, não como conjunto parcial.

### Próxima ação e encerramento

Mantenedor e donos das superfícies a confirmar: decidir recorte e produzir folha revisável, reaproveitando o resolver. Encerrar E02 por comportamento integrado no escopo ratificado, não por três PRs contadas.

<a id="item-068"></a>

## E14 — Validar #127 nas combinações Spark prometidas

Frente: registro_associado_issues_centrais. Encaminhamento: matriz_de_suporte_com_prova_por_celula.

### Identidade e estado

ID canônico E14: Validar #127 nas combinações Spark prometidas. Origem preservada no registro de 158 IDs; acompanhamento [#123](fichas-02.md#item-016). Responsável do próximo passo a confirmar. Disposição: matriz_de_suporte_com_prova_por_celula.

### Intenção e benefício

Alinhar a promessa de suporte a combinações de Spark, sistema hospedeiro, JDK e bootstrap realmente provadas ou explicitamente não cobertas.

### Feito, faltante e não comprovado

O delivery record relata wrapper macOS em Spark 4.0.1, além do núcleo de setembro. O registro atribui Spark 4.1.2 ao núcleo; essa identificação adicional permanece relato do registro nesta ficha. JAR agendado verde em JDK 17/21 é prova de outro recorte. Windows real e fresh cold start do wrapper não estão demonstrados nessas fontes.

### Linhagem

#127/P02 → relatório de runtime com limites → E14. DEC-10 contém alternativas históricas de contenção antes do merge, que já ocorreu; não é uma decisão atual de suporte ratificada automaticamente.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/C03b-REGISTRO-E.md#reg-e14, linha 449; CSV, MATRIX e PUBLICATION preservados. Fontes primárias, datas e SHA de código são os da ficha [#123](fichas-02.md#item-016), relacionadas abaixo. Código APEX fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; estados públicos são os recibos de 16–17/10, não uma consulta implícita nova.

### Classe e limite da evidência

DIRETO ESTÁTICO: trechos e metadados descritos nos campos 3–5 e na ficha [#123](fichas-02.md#item-016). RELATO: execuções/resultados históricos ali atribuídos. INFERÊNCIA: riscos condicionais do campo 8. PROPOSTA: opções e menor prova futura; nenhuma decisão de mantenedor, execução de produto ou publicação nova nesta revisão.

### Fluxo

Promessa pública por perfil → célula (versão/host/bootstrap) → recibo com SHA/comandos ou estado não provado → documentação de suporte. Resultado JAR não preenche célula de wrapper macOS/Windows.

### Consequências e risco

Transportar um verde de JDK para stack Spark ou chamar o wrapper de cold start faz o usuário assumir compatibilidade inexistente na evidência. Não foi demonstrada incompatibilidade nas células não testadas.

### Alternativas e recomendação

Restringir promessa ao que está sustentado ou obter prova adicional das células escolhidas. Adiar suporte Windows é opção de produto, não decisão desta auditoria. Registrar o núcleo 4.1.2 como relato até conferir o recibo de versão correspondente.

### Dependências e paralelismo

Decidir a promessa precede custo de testar combinações. Env/ownership importam ao planejar nova execução; matriz documental pode ser produzida já. Não impor toda a matriz como gate de qualquer PR de texto/teste.

### Plano e aceite propostos

Construir tabela com componente, ref, Spark/JDK, host, imagem/cache, dados, resultado e classe de prova. Preencher wrapper 4.0.1/macOS com relato e limites; não preencher Windows/cold start a partir dele. Controle de revisão: cada célula exige recibo próprio ou rótulo explícito não demonstrado.

### Comunicação entre responsáveis

Comunicar suporte observado, declarado e proposto separadamente. Os resultados históricos continuam válidos dentro de sua fronteira e não passam a ser execução da main atual.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Transportar o verde do JAR em JDK 17/21 para a stack Spark, ou chamar o wrapper de cold start, levaria o usuário a assumir compatibilidade que a evidência não mostra. Que caso o teste ainda não cobre? — Windows real e cold start do wrapper não têm prova; a versão Spark 4.1.2 do núcleo é relato do registro ainda sem recibo conferido, e a imagem do wrapper veio de cache. Como eu explicaria isso para outro pod? — Cada célula da matriz (Spark/JDK, host, bootstrap) precisa de recibo próprio ou rótulo de não demonstrado; qual plataforma o produto promete agora é decisão anterior ao custo de testar.

### Próxima ação e encerramento

Owner Package/Infra a confirmar: ratificar matriz e vincular provas existentes antes de pedir novas execuções. Encerrar a decisão documental com promessa explícita; validar somente as células adicionais acordadas.

<a id="item-069"></a>

## E17 — Higiene do gate tail-outlier (P10, P12, P13)

Frente: registro_associado_issues_centrais. Encaminhamento: decidir_garantia_do_gate_e_conservar_destino_123.

### Identidade e estado

ID canônico E17: Higiene do gate tail-outlier (P10, P12, P13). Origem preservada no registro de 158 IDs; acompanhamento [#123](fichas-02.md#item-016). Responsável do próximo passo a confirmar. Disposição: decidir_garantia_do_gate_e_conservar_destino_123.

### Intenção e benefício

Reduzir custo e tornar explícita a força da associação entre cenário, finding e evidência. O conjunto histórico P10/P12/P13 não constitui uma única implementação obrigatória.

### Feito, faltante e não comprovado

Confirmados estaticamente: filtro textual do watcher, contador final literal e ausência de comparação explícita com stage/snapshot. generate_data supostamente desnecessário e requisitos de migração são alegações históricas não revalidadas integralmente neste ID. E17 é reuse_existing #123 em PUBLICATION, não #167.

### Linhagem

Revisão histórica de #127 → E17/P-GATE → disposição de reaproveitar #123 → estudo de 11/10 e DEC-N6. Publicação e discussão não significam patch integrado.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/C03b-REGISTRO-E.md#reg-e17, linha 551; CSV, MATRIX e PUBLICATION preservados. Fontes primárias, datas e SHA de código são os da ficha [#123](fichas-02.md#item-016), relacionadas abaixo. Código APEX fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; estados públicos são os recibos de 16–17/10, não uma consulta implícita nova.

### Classe e limite da evidência

DIRETO ESTÁTICO: trechos e metadados descritos nos campos 3–5 e na ficha [#123](fichas-02.md#item-016). RELATO: execuções/resultados históricos ali atribuídos. INFERÊNCIA: riscos condicionais do campo 8. PROPOSTA: opções e menor prova futura; nenhuma decisão de mantenedor, execução de produto ou publicação nova nesta revisão.

### Fluxo

Cenário/job → asserção de cauda → saída Engine → predicado atual por RC/nome → PASS. Associação forte proposta adicionaria identidade/população/snapshot e medição do contador; sua forma depende de decisão.

### Consequências e risco

O predicado pode aceitar texto/finding sem a identidade pretendida. É uma hipótese estática; não houve execução com falso PASS nesta revisão. Apagar geração de dados sem verificar dependências pode quebrar o ambiente; a acusação de custo desnecessário requer prova própria.

### Alternativas e recomendação

Escolher associação por job com alcance declarado ou forte por stage/tentativa/snapshot/população. Na forte, parsear resultado estruturado e testar contracasos; na fraca, não afirmar que o stage escolhido foi provado. Separar redução de setup do fortalecimento da asserção.

### Dependências e paralelismo

#127 já integrada. DEC-N6 define qual garantia testar. #174/#175 afetam nova operação, não a leitura de predicado. A decisão fraca não pode herdar critério forte incondicional sem resolver a contradição.

### Plano e aceite propostos

Mapear cada subalegação P10/P12/P13 à fonte. Para associação forte: outro stage, tentativa/população divergente, snapshot antigo e nome isolado devem falhar; positivo com identidade correspondente passa. Para zero LLM, observar contador real. Para custo de setup, comparar dependências antes de remover trabalho. Critérios condicionais à opção ratificada.

### Comunicação entre responsáveis

Registrar o ID E17 em #123 numa eventual atualização autorizada e explicar garantia atual versus proposta. Não publicar minuta duplicada nem transferir toda a higiene do gate a #167.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Remover generate_data sem verificar dependências pode quebrar o ambiente, e afirmar associação ao stage com o predicado atual excede o código. Que caso o teste ainda não cobre? — O gate não confere se o finding pertence ao mesmo stage e snapshot, e o marcador zero LLM é literal, não medido; um falso PASS não foi reproduzido, e a dependência de generate_data não foi revalidada. Como eu explicaria isso para outro pod? — E17 reaproveita a #123, não a #167; a garantia por job ou por stage, tentativa e snapshot é escolha do mantenedor em DEC-N6, e o estudo não implementa nada.

### Próxima ação e encerramento

Mantenedor com owner Package: decidir garantia, decompor os subitens confirmados e preservar os ainda não verificados. Encerrar cada folha com prova correspondente; não declarar E17 implementado pela existência do estudo.

<a id="item-070"></a>

## L09 — HARN-BINDING — run-pathology repassar APEX_OTLP_ENDPOINT

Frente: registro_associado_issues_centrais. Encaminhamento: propagacao_offline_independente_da_politica_global.

### Identidade e estado

ID canônico L09: HARN-BINDING — run-pathology repassar APEX_OTLP_ENDPOINT. Origem preservada no registro de 158 IDs; acompanhamento [#178](fichas-04.md#item-031). Responsável do próximo passo a confirmar. Disposição: propagacao_offline_independente_da_politica_global.

### Intenção e benefício

Levar o endpoint OTLP escolhido pelo operador até a configuração efetiva de submit, conservando o default quando não há override.

### Feito, faltante e não comprovado

Na fonte fixada, run-pathology não repassa endpoint, c3/c4 usam literal e spark-defaults tem default fixo. O corpo #178 diz expressamente que a prova de propagação não depende de escolher toda a política de ownership. O predecessor incondicional E09/DEC-10 da ficha antiga é excessivo.

### Linhagem

L09/HARN-BINDING → PROP-L09-HARN-BINDING → #178 publicada. E09/#175 é frente complementar; não é implementado_por nem requisito universal. O comentário histórico de aliases não autoriza criar novas implementações para cada alias.

### Fontes e corte

Fonte de origem: ../parte-03-claude-v2/fontes/claude-v2/C03d-REGISTRO-L-DD-W-D.md#reg-l09, linha 168; CSV, MATRIX e PUBLICATION preservados. Fontes primárias, datas e SHA de código são os da ficha [#178](fichas-04.md#item-031), relacionadas abaixo. Código APEX fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; estados públicos são os recibos de 16–17/10, não uma consulta implícita nova.

### Classe e limite da evidência

DIRETO ESTÁTICO: trechos e metadados descritos nos campos 3–5 e na ficha [#178](fichas-04.md#item-031). RELATO: execuções/resultados históricos ali atribuídos. INFERÊNCIA: riscos condicionais do campo 8. PROPOSTA: opções e menor prova futura; nenhuma decisão de mantenedor, execução de produto ou publicação nova nesta revisão.

### Fluxo

Escolha do operador → precedência default/override → launcher → configuração final Spark. Entrega OTLP ao Collector é uma prova diferente e posterior, não implicada pelo comando renderizado.

### Consequências e risco

Override perdido pode encaminhar telemetria ao Collector errado. Não houve incidente observado. Passar -e sem tradução para conf pode deixar o comportamento inalterado; make -n tampouco garante ausência de Docker por causa do shell expandido no Makefile.

### Alternativas e recomendação

Definir uma precedência coerente e testar o caminho completo da configuração. Não aguardar política global de stacks para uma correção offline pequena. Ownership continua necessário quando a operação efetiva o exigir.

### Dependências e paralelismo

Inspeção e prova do comando podem avançar sem E09. É preciso conhecer as interfaces dos jobs/scripts e controlar expansão de comandos externos. Runtime/entrega depende do ambiente e autorização próprios, fora desta revisão.

### Plano e aceite propostos

Inventariar alvos afetados, default e override vazio/válido; testar comando final com substituição segura de acessos externos. Controle negativo remove endpoint e falha. Aceite: escolha/default chegam ao argumento efetivo sem Docker/OTLP no teste; uma variável só no host/container não basta.

### Comunicação entre responsáveis

Explicar o que foi propagado e o que não foi medido: configuração não é entrega. Relacionar #175 como complemento e justificar a retirada do gate histórico.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Passar -e sem traduzir a variável para spark.apex.otlp.endpoint deixaria o comportamento inalterado, e um override perdido encaminharia telemetria ao Collector errado. Que caso o teste ainda não cobre? — Falta um controle que detecte perda do endpoint depois do launcher, e make -n ainda expande o shell do Makefile; a entrega OTLP ao Collector é prova posterior. Como eu explicaria isso para outro pod? — A precedência entre default e override decide qual endpoint vale, e a prova offline mostra até o argumento efetivo de submit; não depende da política global de stacks da #175.

### Próxima ação e encerramento

Owner Harness a confirmar: produzir menor correção de forwarding com prova offline e documentação. Encerrar L09 por integração e critérios da #178; não condicionar a conclusão à escolha de toda a identidade de stacks.

