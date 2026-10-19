# Fichas documentais — lote 2

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-011"></a>

## #3 — Collector backpressure: estratégia histórica documentada

Frente: historico. Encaminhamento: historico_preservado_com_justificativa.

### Identidade e estado

Issue #3: [Collector] Backpressure: como lidar se ClickHouse fica lento?. Autor Guilherme-daCosta; encerrada em 2026-09-17T16:45:07Z; motivo API completed. Esta ficha corrige a leitura histórica; não muda o GitHub.

### Intenção e benefício

Definir o comportamento de fila e retry quando ClickHouse fica lento, preservando limite de memória e previsibilidade operacional.

### Feito, faltante e não comprovado

O encerramento relata memory_limiter no início, sending_queue de 10000 com file_storage, block_on_overflow e retry de 5s a 30s com máximo de 300s. Isso fornece desenho e parâmetros, mas não prova durabilidade, ausência de perdas ou desempenho sob toda falha.

### Linhagem

Issue → discussão/comentário(s) de encerramento → arquivos e controles ali citados → estado fechado. Uma PR com Closes não foi identificada por este recorte; isso não significa ausência de implementação, teste ou review. Comentários: https://github.com/luanmorenommaciel/apex/issues/3#issuecomment-5718018930.

### Fontes e corte

Fontes: snapshot preservado issues_all.json, item number=3; icomments_all.json pelos URLs https://github.com/luanmorenommaciel/apex/issues/3#issuecomment-5718018930; ficha anterior C07-HISTORICO-ENCERRADO.md. Consulta original do pacote em 16/10/2026; main atual c3c3ea3 para a distinção de versões.

### Classe e limite da evidência

DIRETO: estado, autoria e existência do texto dos comentários. RELATADO: implementação, parâmetros e validação descritos no fechamento. NÃO VERIFICADO nesta ficha: comportamento atual em runtime e cadeia completa de commits/reviews/testes. Não converter ausência de link Closes em ausência de prova.

### Fluxo

Entrada OTLP → limite de memória → fila persistida → tentativas de exportação. Pressão de saída pode repercutir na admissão; detalhes de execução e limites precisam dos artefatos da versão pertinente.

### Consequências e risco

Tratar a ficha como sem fluxo apagaria o desenho que fundamenta a decisão. Tratar parâmetros declarados como soak test seria extrapolação. Não foi executada carga ou falha de ClickHouse.

### Alternativas e recomendação

Manter decisão histórica. Um ensaio de saturação/crash é uma prova adicional para uma garantia operacional escolhida; não duplicar a implementação só pela falta de PR fechadora textual.

### Dependências e paralelismo

Nenhuma nova dependência imposta ao item encerrado. Localizar um recibo histórico é trabalho de linhagem, não bloqueio de produto. Um follow-up atual precisa de lacuna específica e owner a confirmar.

### Plano e aceite propostos

Se priorizado um ensaio, delimitar volume, duração, reinício e contadores antes da execução. Nenhum ensaio é disparado por este relatório.

### Comunicação entre responsáveis

Na consolidação, explicar por que #3 permanece fechada e apontar o comentário que sustenta sua interpretação. Nenhuma mensagem externa foi enviada; eventual follow-up deve distinguir fato atual de relato histórico.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Tratar a ficha como sem fluxo apagaria o desenho relatado (memory_limiter, sending_queue de 10000 com file_storage, block_on_overflow, retry de 5s a 30s até 300s); tratar esses parâmetros como soak test seria extrapolação. Que caso o teste ainda não cobre? — Não foram mostrados o comportamento ao atingir queue_size, a interrupção em que a persistência foi provada, nem a perda ou recusa observável quando o retry expira; nenhuma carga ou falha de ClickHouse foi executada. Como eu explicaria isso para outro pod? — #3 fica fechada com uma estratégia histórica de fila e retry documentada no encerramento; ela descreve desenho e parâmetros, não garante durabilidade, ausência de perdas ou desempenho sob toda falha.

### Próxima ação e encerramento

Próxima ação de produto: nenhuma criada por esta revisão. Ação documental: conservar esta correção e, se for necessário certificar uma garantia atual, abrir recorte próprio com fonte, owner e critério discriminante.

<a id="item-012"></a>

## #4 — Schema Collector: proposta substituída pelo contrato

Frente: historico. Encaminhamento: historico_preservado_com_justificativa.

### Identidade e estado

Issue #4: [Collector] ClickHouse schema: definir tables pra telemetria. Autor Guilherme-daCosta; encerrada em 2026-09-17T16:45:10Z; motivo API completed. Esta ficha corrige a leitura histórica; não muda o GitHub.

### Intenção e benefício

Escolher a representação de telemetria no ClickHouse e manter ligação entre a discussão inicial e o contrato que a substituiu.

### Feito, faltante e não comprovado

Dois comentários apontam substituição da proposta por CONTRACT.md v0.5, spark_events, migrações 034–039 e DDLs de plan_transitions/job_conf/findings. A main atual declara v0.6; a data/versão do comentário deve ser preservada como histórica.

### Linhagem

Issue → discussão/comentário(s) de encerramento → arquivos e controles ali citados → estado fechado. Uma PR com Closes não foi identificada por este recorte; isso não significa ausência de implementação, teste ou review. Comentários: https://github.com/luanmorenommaciel/apex/issues/4#issuecomment-5359987433; https://github.com/luanmorenommaciel/apex/issues/4#issuecomment-5718019375.

### Fontes e corte

Fontes: snapshot preservado issues_all.json, item number=4; icomments_all.json pelos URLs https://github.com/luanmorenommaciel/apex/issues/4#issuecomment-5359987433; https://github.com/luanmorenommaciel/apex/issues/4#issuecomment-5718019375; ficha anterior C07-HISTORICO-ENCERRADO.md. Consulta original do pacote em 16/10/2026; main atual c3c3ea3 para a distinção de versões.

### Classe e limite da evidência

DIRETO: estado, autoria e existência do texto dos comentários. RELATADO: implementação, parâmetros e validação descritos no fechamento. NÃO VERIFICADO nesta ficha: comportamento atual em runtime e cadeia completa de commits/reviews/testes. Não converter ausência de link Closes em ausência de prova.

### Fluxo

Discussão #4 → contrato e extensões aceitos historicamente → SQL de evolução aplicado pelo processo de infra. O estado closed/completed não exige que a proposta original tenha sido implementada literalmente.

### Consequências e risco

Copiar o desenho inicial ignorando a substituição cria uma segunda fonte de schema. A existência dos DDLs não prova o schema aplicado em um store específico.

### Alternativas e recomendação

Catalogar como proposta substituída. Eventuais divergências atuais pertencem ao contrato/DDL ou à decisão #170/#165 conforme o recorte; não restaurar a proposta inicial sem nova justificativa.

### Dependências e paralelismo

Nenhuma nova dependência imposta ao item encerrado. Localizar um recibo histórico é trabalho de linhagem, não bloqueio de produto. Um follow-up atual precisa de lacuna específica e owner a confirmar.

### Plano e aceite propostos

Preservar links para contrato e migrações, com corte histórico. Não há migração ou alteração de schema a executar para encerrar esta ficha.

### Comunicação entre responsáveis

Na consolidação, explicar por que #4 permanece fechada e apontar o comentário que sustenta sua interpretação. Nenhuma mensagem externa foi enviada; eventual follow-up deve distinguir fato atual de relato histórico.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Copiar o desenho inicial da #4 ignorando a substituição criaria uma segunda fonte de schema ao lado do contrato. Que caso o teste ainda não cobre? — A existência dos DDLs de plan_transitions, job_conf e findings não prova o schema aplicado num store específico; nenhuma migração foi executada neste recorte. Como eu explicaria isso para outro pod? — A proposta inicial de tabelas foi substituída, segundo os comentários, por CONTRACT.md v0.5, spark_events e as migrações 034–039; v0.5 é a versão do comentário histórico, e a main atual declara v0.6.

### Próxima ação e encerramento

Próxima ação de produto: nenhuma criada por esta revisão. Ação documental: conservar esta correção e, se for necessário certificar uma garantia atual, abrir recorte próprio com fonte, owner e critério discriminante.

<a id="item-013"></a>

## T-20260923-console-auto-prefers-api — Preferência automática pela API — proposta substituída

Frente: taskspecs. Encaminhamento: historico_substituido_nao_reexecutar_spec_antiga.

### Identidade e estado

T-20260923-console-auto-prefers-api, tasks/parked/T-20260923-console-auto-prefers-api.md, main c3c3ea3. Status parked, accepted=false; owner não designado. Blob d2f64c1f25c86cf7be6c8b09d5317a5073287677 verificado na Parte03.

### Intenção e benefício

A proposta original pretendia sondar API same-origin mesmo com apiUrl vazio e preferir API que respondesse 200, permitindo fallback após 401. Benefício pretendido: usar perfil HTTP sem credencial direta de banco.

### Feito, faltante e não comprovado

O blocked_reason declara superseded em 29/09 por fab6620, com semântica diferente: 401 seleciona API. Na main, resolveRepository sonda apiPing incondicionalmente em auto; apiPing aceita 401 ou corpo status=ok em resposta bem-sucedida. Portanto a decisão original não está simplesmente esperando execução.

### Linhagem

Proposta de 23/09 → substituição declarada por fab6620 → arquivo parked preservado → implementação atual em repository.ts/http.ts → #153 referenciada no inventário. O papel exato de cada commit ancestral não foi reconstruído integralmente nesta ficha; a divergência entre proposta antiga e código atual é direta.

### Fontes e corte

Fontes: cópia Git da spec no snapshot; campos blocked_reason e Behavior B-2; fontes/main-repository.txt:369–387 e fontes/main-http.txt:121–149. A captura usa ref c3c3ea3 completa. Conferência de blob em TASKSPECS-106.json da Parte03.

### Classe e limite da evidência

DIRETO: texto de substituição e lógica atual de sondagem. HISTÓRICO: intenção da spec. INFERÊNCIA sustentada: executar B-2 como está reintroduziria fallback 401 contrário ao código atual. Nenhum teste/runtime foi executado e nenhum aceite foi carimbado.

### Fluxo

auto → apiPing same-origin/URL configurada → 401 ou status=ok: HttpRepository; ausência/erro/não API: ping ClickHouse → fixtures se também indisponível. Depois de escolhido HTTP, erro de autenticação permanece erro; não vira fallback silencioso.

### Consequências e risco

Reativar a spec antiga pode restaurar credencial de banco no browser após uma recusa da API. Risco derivado do fluxo, não incidente observado. Manter parked é compatível com substituição e não é, por si só, status incorreto.

### Alternativas e recomendação

Recomendação: catalogar como substituída e manter a justificativa. Se a convenção local preferir retired/archived, fazer apenas housekeeping com referência. Alterar política de 401 exige nova decisão e nova spec; não usar esta proposta obsoleta como requisito atual.

### Dependências e paralelismo

Sem dependência necessária de #171 ou #122 para catalogar a substituição já declarada. Essas decisões podem mudar política futura, mas não reabrem retroativamente esta tarefa. Não tratar accepted=false como obrigação de implementação.

### Plano e aceite propostos

Consolidar o estado superseded/parked e a diferença de B-2; manter bytes de origem. Aceite documental: leitor identifica intenção antiga, motivo de substituição e código atual. Se houver mudança futura, testar 200 HTML, status=ok, 401, erro de rede e perfil pinned sob a nova política autorizada.

### Comunicação entre responsáveis

Explicar a Front/Serve que o contrato vigente da sondagem difere da proposta estacionada. Evitar colocar “executar ou arquivar” como pendência de produto sem mencionar a substituição.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Executar o B-2 da spec antiga reintroduziria o fallback após 401, contrário ao código atual, e poderia devolver ao browser a credencial direta de banco depois de uma recusa da API. Que caso o teste ainda não cobre? — Nenhum teste foi executado aqui; uma política futura teria de separar 200 com HTML, corpo status=ok, 401, erro de rede e perfil pinned, porque um 200 com HTML não prova que a resposta veio da API. Como eu explicaria isso para outro pod? — A tarefa está parked com blocked_reason superseded por fab6620, em que 401 seleciona a API; parked aqui registra a substituição, não decisão ausente, e a história fica preservada sem reativar a spec obsoleta.

### Próxima ação e encerramento

Owner documental a confirmar: entrada spec e código na mesma ref; saída catálogo corrigido. Nenhuma execução ou decisão externa é necessária para registrar o fato; eventual política nova segue escopo próprio.

<a id="item-014"></a>

## #115 — Atribuição execution_id → stages: resolver existente e integração por escolher

Frente: issues_centrais. Encaminhamento: selecionar_consumidor_e_preservar_contrato.

### Identidade e estado

Issue #115 aberta, Pod 2/Engine, sem assignee na consulta de 17/10/2026 00:47 UTC. E01/E02/P01 são origens relacionadas; a PR #126 é uma implementação parcial integrada, não o encerramento de toda a issue.

### Intenção e benefício

Relacionar uma execução SQL ao conjunto exato de stages dentro de app_id e job_id, mantendo execution_id opcional para RDD. O ganho é uma navegação e um diagnóstico que não dependam de adivinhar correlações por horário.

### Feito, faltante e não comprovado

O resolver puro já existe: filtra aplicação/job, deduplica e ordena stages entre tentativas, distingue ausência de IDs, execução não encontrada e conflito. O teste de conflito já cobre o mesmo stage associado a dois execution_ids não nulos e retém a atribuição parcial; vários stages para uma execução são válidos. Há controles de escopo estrangeiro e de zero versus None. Faltam selecionar e demonstrar a integração pública e a prova SQL/RDD. O sentinel -1 em findings AQE representa nível de job; não é prova de que todos os watchers careçam de stage nem autorização para substituí-lo indiscriminadamente. attributionIsAvailable() ainda retorna false.

### Linhagem

#96 (produtor) → #115 → planos issue115-* → #126, head 4ddb082cf8e916736e336d6a5554bccbba083a19, merge abed50893977e14dcf70ffdc4274e70793b76030 em 06/10 → resolver na main. Comentário de 17/09 lista Engine/Serve/Front como trabalho restante; corpo original deixa a primeira superfície e a forma query/biblioteca como decisões. Nenhuma dessas referências exige exatamente três PRs.

### Fontes e corte

Código fixado em main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: attribution.py; test_execution_attribution.py; watchers/aqe.py e base.py; front/src/contract/rules.ts. Recibos lote2 preservam URL e data. Corpo da issue reconsultado em 17/10; comentário e PR #126 lidos no snapshot de 16/10. Fontes históricas não foram convertidas em resultados novos.

### Classe e limite da evidência

DIRETO ESTÁTICO: regras do resolver, testes escritos e flag Front. RELATADO: 25 testes focados e 213 testes Engine/root, com 11 skips, no corpo de #126. PENDENTE: integração e recibo runtime SQL/RDD no recorte escolhido. A leitura de testes não afirma que passaram nesta auditoria.

### Fluxo

Observações de stage → filtro app_id/job_id → correspondência execution_id → conjunto de stages ou estado explícito → consumidor a escolher. A coleta/parsing das observações fica fora da função pura atual. Não unir identidades de governança, execução SQL e stage por coincidência numérica.

### Consequências e risco

Ligar a disponibilidade no Front sem estado correspondente no consumidor pode apresentar atribuição inexistente. Ignorar app_id/job_id pode misturar execuções. O texto anterior ainda propunha testar um conflito já coberto; isso desperdiçaria esforço e ocultaria a lacuna real de integração. Nenhum incidente de atribuição foi demonstrado.

### Alternativas e recomendação

Recomenda-se aproveitar o resolver e selecionar uma superfície mínima com mantenedor. Engine, Serve ou query documentada são alternativas permitidas pelo corpo. Engine pode originar dado consumível, mas não é uma decisão já tomada. Manter resultado indisponível enquanto a superfície não existe é reversível e honesto.

### Dependências e paralelismo

A precondição histórica de integração do produtor #96 já foi atendida. #169 ajuda a explicitar seleção de tentativa, mas não bloqueia o estudo de contrato ou a definição da primeira superfície por padrão. Mudanças de schema ou thresholds não entram implicitamente. #117 pode ser estudada em paralelo.

### Plano e aceite propostos

Folha proposta 1: definir superfície e adapter de observações sem alterar thresholds. Folha 2: integrar estados do resolver, com controles de app/job estrangeiro, zero, None, conflito e duplicatas. Aceite offline: consumidor conserva cada estado e não transforma conflito em conjunto parcial. Prova separada, quando autorizada: SQL com conjunto esperado e RDD sem execution_id. Quantidade de PRs depende dessas fronteiras, não é critério em si.

### Comunicação entre responsáveis

Minuta para os pods: o resolver já define conflito; falta decidir quem o expõe e como o estado chega ao usuário. Listar critérios satisfeitos, integração ainda pendente e limites do runtime histórico. Não anunciar que Engine/Serve/Front já foram integrados.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Ligar attributionIsAvailable() sem um consumidor que carregue os estados do resolver mostraria atribuição inexistente, e ignorar app_id/job_id misturaria execuções. Que caso o teste ainda não cobre? — O teste de conflito já separa o mesmo stage com dois execution_ids de vários stages válidos da mesma execução; falta a integração pública e a prova SQL com conjunto esperado e RDD sem execution_id, sem tratar ausência como zero. Como eu explicaria isso para outro pod? — O resolver puro da #126 já atribui stages por app_id/job_id e explicita ausência, não encontrado e conflito; falta escolher qual consumidor o expõe e qual identidade ele recebe, e execution_id continua opcional para RDD.

### Próxima ação e encerramento

Mantenedor/owner a confirmar: registrar superfície, reaproveitar testes discriminantes existentes e fechar apenas critérios demonstrados. Encerramento requer satisfação dos critérios públicos ou uma revisão explícita de escopo, incluindo a prova SQL/RDD exigida. Três PRs e remoção geral de -1 não são requisitos autorizados.

<a id="item-015"></a>

## #117 — Atribuição e piso de ruído entre Verify, storage, Serve e Front

Frente: issues_centrais. Encaminhamento: ratificar_contrato_e_validar_residuos.

### Identidade e estado

Issue #117 aberta, sem assignee em 17/10/2026 00:47 UTC; contrato compartilhado Verify/Front/Serve. O comentário de 17/09 destaca superfície Memory→Serve, réplicas para recálculo e teste write→read→render. F06 foi destinado à issue em PUBLICATION.json; isso não equivale a um escritor implementado.

### Intenção e benefício

Conservar o significado de uma medição: atribuição, disponibilidade do piso, magnitude, direção e mecanismo devem sobreviver à serialização e aos consumidores. O usuário não deve receber uma certificação que a biblioteca recusou.

### Feito, faltante e não comprovado

Measurement considera atribuição e piso válido; significant usa abs(delta) >= piso. to_row conserva delta bruto e piso válido, mas não serializa attributable nem as amostras individuais. Os dois DDLs lidos também não têm a coluna de atribuição. Front e projeção equivalente em Serve usam >; o render de replay do Serve recusa apenas <, portanto aceita igualdade. Front ainda calcula amplitude/média, Verify usa CV amostral, e o adapter live fornece replay_durations_ms=None. Já há leitura de verificação no Serve: a ausência registrada no head antigo não descreve a main atual. Defesas de piso inválido, direção negativa e independência mecanismo/runtime já tiveram correções integradas; não refazê-las como se ausentes.

### Linhagem

Gap documentado em 5b4fc4f → #117 → correções parciais (#136, #142, #143–#145, entre outras) e superfície Serve de #129 → contrato residual na main. Estudos/IDs canônicos indicam decomposição pretendida, não decisões ratificadas. F06/P-DEC06 reaproveita #117; não criar duplicata porque a classificação histórica dizia proposed_issue.

### Fontes e corte

Issue reconsultada em 17/10. Código em main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: Verify models/replay/guardrails; Front rules/queries/repository; Serve ch/diagnose; DDL infra e Verify. Comentário de 17/09 e estados das PRs no snapshot de 16/10. Os recibos da Parte04 permitem conferir cada arquivo.

### Classe e limite da evidência

DIRETO ESTÁTICO: campo omitido na serialização, representação dos DDLs, operadores de comparação, fórmulas e leitura Serve existente. RELATADO: reprodução histórica com configs iguais e vetores numéricos na issue. INFERÊNCIA CONDICIONAL: se a linha bruta for persistida e consumida sem estado de atribuição, o predicado pode certificar magnitude não atribuível. Não foi observado incidente nem comprovado um escritor de produção nesta rodada.

### Fluxo

Verify Measurement → to_row (atribuição omitida) → escritor/storage ainda a identificar no ambiente alvo → projeções Front/Serve → rótulo. Memory pode fornecer piso conforme desenho ainda a decidir. Atenção a unidades: compare_runs no Serve usa fração (0,159 = 15,9%); replay/linhas usam percentual. Um contrato compartilhado precisa normalizar essa diferença explicitamente.

### Consequências e risco

A omissão pode tornar um resultado não atribuível indistinguível de outro na fronteira persistida. A diferença >= versus > muda exatamente o caso de igualdade, e CV versus amplitude/média muda o piso. Os problemas são de contrato verificáveis em fonte, mas o dano em produção continua hipotético. Criar somente decisões e folhas não satisfaz os critérios de comportamento e integração da issue.

### Alternativas e recomendação

Comparar representação trivalorada versionada com uma projeção publicável separada dos valores brutos. Ambas devem preservar histórico desconhecido. Manter persistência fora de uma versão pode ser uma decisão do mantenedor, mas não foi aprovada aqui e exige revisão explícita do escopo. Coluna nova exige verificar leitores, migração e rollback; os DDLs lidos não sustentam a hipótese de coluna já existente.

### Dependências e paralelismo

Identificar produtor/escritor/consumidores condiciona a implementação e o tipo de prova, não todo o estudo. F02/F03 (semântica), F06 (rota), F07 (amostras), F08/F09 (consumo) podem ser preparados em paralelo. F05 só é necessário se a solução escolhida alterar schema. A PR #162 trata __version__ e não bloqueia esta decisão.

### Plano e aceite propostos

1. Registrar estados, unidade, fórmula, fronteira de igualdade e rota alvo. 2. Alterar a menor fronteira escolhida com compatibilidade. 3. Testar ausência/falso/verdadeiro, linha histórica desconhecida, piso inválido, abaixo/igual/acima, direções ± e mecanismo independente. 4. Validar produtor→serialização→leitura→render; se houver storage real no escopo, guardar prova própria. Stubs servem ao contrato offline, não ao aceite de persistência. Donos devem ratificar qualquer retirada de critério.

### Comunicação entre responsáveis

Minuta: o Serve já lê verificações; o que falta é um contrato consistente ao longo da rota selecionada. Explicar separadamente perda de representação, possível persistência e efeito ainda não demonstrado. Registrar F06 como origem absorvida, sem afirmar que sua rastreabilidade textual resolve o comportamento.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Persistir a linha de to_row sem attributable tornaria um resultado não atribuível indistinguível de outro, e um consumidor poderia certificar uma magnitude que a biblioteca recusou; o dano em produção não foi demonstrado. Que caso o teste ainda não cobre? — Falta acompanhar o mesmo vetor ao serializar, ler e renderizar, inclusive com mecanismo falso, e a igualdade com o piso: Verify usa >=, Front e a projeção do Serve usam >, e o replay do Serve aceita igualdade; quem grava as linhas no ambiente alvo segue não identificado. Como eu explicaria isso para outro pod? — O Serve já lê verificações; falta um contrato único que distinga linha antiga desconhecida de false, normalize o piso entre fração (compare_runs) e percentual (replay) e fixe a regra de igualdade ao longo da rota escolhida.

### Próxima ação e encerramento

Owner Verify a confirmar com Front/Serve e Infra somente se necessária: primeiro fechar o desenho, depois aceitar as folhas e a rota delimitada. Não encerrar #117 apenas porque uma reunião decidiu ou novas issues foram criadas; encerrar após critérios atendidos ou alteração explícita e rastreável de escopo pelo mantenedor.

<a id="item-016"></a>

## #123 — Tail-outlier: integração presente, runtime histórico e associação limitada

Frente: issues_centrais. Encaminhamento: reconciliar_provas_e_decidir_associacao.

### Identidade e estado

Issue #123 aberta, assignee gustocezar, Pod 2/Engine; estado reconsultado em 17/10/2026 00:47 UTC. P02 é a integração; E17 foi destinado a esta issue para higiene/associação do gate, não à #167 (interface R9D).

### Intenção e benefício

Fazer o comando público tail-outlier atravessar workload Spark, telemetria e Engine determinístico, registrando o finding esperado sem chamadas LLM. A garantia precisa dizer se vale por job ou pelo mesmo stage/população escolhidos pela asserção.

### Feito, faltante e não comprovado

Watcher, registro, cenário canônico e comando real já existem; o throw incondicional foi removido. Há relato público detalhado de dois runtimes: núcleo isolado em 20/09 e wrapper macOS/Spark 4.0.1 em 21/09. Portanto runtime ausente é incorreto como afirmação geral. No wrapper atual, Engine recebe o job_id da sessão e --dry-run --no-crew; o gate exige exit code zero e substring tail_outlier_watcher, mas não compara stage/snapshot/população nem lê o contador LLM para validar o llm_calls=0 que imprime.

### Linhagem

P02 → #123 → planos/Task-Spec de setembro → PR #127 (head 4e44bfdce5586fe9b8ed7c96e41932b55f231a88; merge fec8a7fb0b3669343725141ab60eef0d8dff74a0 em 06/10) → implementação na main. O delivery record situa o wrapper no conteúdo depois commitado como 754f45e e 5b41c77. Estudo de 11/10 no comentário introduz a lacuna E17; não apaga a prova histórica nem demonstra uma execução adversarial real.

### Fontes e corte

Issue e código na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; TAIL_OUTLIER_RUNTIME_GATE.md, apex.ps1:677–710, canonical_e2e_assert.py, runner canônico, watcher/registry e CLI. PR #127/comentários no snapshot de 16/10. O documento registra app-20260920130100-0001 (200 tarefas; successful_tasks) e app-20260921024421-0001 (wrapper). Datas da evidência: 20–21/09, distintas da leitura em outubro.

### Classe e limite da evidência

DIRETO ESTÁTICO: caminho do gate e seus predicados. RELATO PÚBLICO HISTÓRICO: runtimes, saídas e testes de setembro. Não foram reexecutados nem todos os logs brutos revalidados nesta rodada. O wrapper reutilizou cache de imagens com identidade conferida e recursos parciais; não provou cold start de registry vazio. Windows e main atual não se tornam certificados por esse relato. Merge é observado; review humano formal não foi inferido.

### Fluxo

Canonical seleciona candidato com cauda de duração → marcador de sessão/job → Engine no mesmo job → retorno zero + ocorrência do nome do watcher → PASS. A asserção de cauda e a regra Engine de ownership por skew têm fronteiras diferentes. Não existe comparação explícita de identidade do finding com o stage/snapshot escolhido pela asserção.

### Consequências e risco

Um finding ou marcador de outro contexto dentro da saída poderia satisfazer a busca textual; é hipótese decorrente do predicado, não um falso PASS reproduzido. Dizer que o gate já prova o stage selecionado excede o código. Exigir novo runtime sem ler a prova de setembro também gera retrabalho e uma história incorreta.

### Alternativas e recomendação

Primeiro reconciliar os critérios com o recibo existente. Depois o mantenedor escolhe garantia por job ou associação forte por stage/tentativa/população/snapshot. A opção fraca pode ser suficiente para um escopo explícito; a opção forte exige formato verificável. Dividir a issue é opção de gestão, não evidência de que a parte runtime nunca ocorreu.

### Dependências e paralelismo

DEC-N6/E17 governa a garantia de associação. #174/E08 (dev/.env) e #175/E09 (ownership de recursos) condicionam uma nova execução segura no ambiente escolhido, mas não anulam historicamente o runtime existente. #124 cobre dispatch offline. Cold start e Windows são lacunas próprias, não requisitos universais inventados para todo item.

### Plano e aceite propostos

Montar mapa critério→fonte→SHA/data→limite. Se escolhida associação forte, folha offline com saída estruturada e controles de stage diferente, snapshot antigo, população divergente e marcador falso, mais caso positivo; validar contador real quando a garantia exige zero LLM. Se escolhida associação por job, documentar alcance e negativos correspondentes. Nova prova runtime só para o resíduo de aceite e em ambiente autorizado; não repetir watcher já integrado.

### Comunicação entre responsáveis

Minuta: implementação integrada e runtime histórico relatado; associação atual é por job mais predicado textual. Mostrar explicitamente quais critérios têm relato, código ou prova ainda faltante. Não descrever como ausente nem apresentar o snapshot atual como runtime recém-validado.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Exigir novo runtime sem ler a prova de 20–21/09 geraria retrabalho e uma história incorreta, e dizer que o gate já prova o stage selecionado excede o código. Que caso o teste ainda não cobre? — O gate aceita exit code zero com a substring tail_outlier_watcher, então um texto de log com esse nome passaria sem finding estruturado do mesmo stage, tentativa, população e snapshot; o llm_calls=0 é impresso, não lido do contador. Como eu explicaria isso para outro pod? — A integração está na main e o runtime de setembro é relato público; a associação atual vale por job mais um predicado textual, e falta mapear quais comandos e hashes do recibo histórico cobrem cada critério aberto antes de escolher associação por job ou por stage.

### Próxima ação e encerramento

Mantenedor com gustocezar: reconciliar a evidência existente e ratificar a garantia pretendida. Encerramento depende desse mapa e do resíduo comprovado, com referência ao recibo correto; não apenas merge nem ausência presumida de runtime. Nenhuma publicação, fechamento ou nova execução foi feita nesta auditoria.

<a id="item-017"></a>

## #124 — PowerShell: dependência explícita e lacuna na prova do dispatch

Frente: issues_centrais. Encaminhamento: manter_criterio_dispatch_pendente.

### Identidade e estado

Issue #124 aberta, Pod 2/Engine, sem assignee em 17/10/2026 00:47 UTC. A PR #128 foi integrada em 06/10; o autor da PR não foi convertido em responsável designado pela próxima ação.

### Intenção e benefício

Exigir PowerShell real na lane obrigatória e distinguir preflight não mutante de prova de que cada ação alcança o handler correto. O ganho é evitar um teste verde que valida somente texto ou um caminho interrompido antes do comando real.

### Feito, faltante e não comprovado

ci.yml verifica PowerShell 7 e registra versão; o helper de teste falha quando pwsh falta e um teste cobre a ausência. ACTION_HANDLERS enumera oito ações e subprocessos executam -DryRun comparando a linha handler=...; há guardas de não mutação. Contudo Handler é uma string independente de Command. O dry-run sai antes de & $actionPlan.Command: trocar só o scriptblock preserva o rótulo e escapa dessa asserção. Os pares atuais parecem coerentes na leitura; não foi encontrado um dispatch real trocado. O critério de documentação macOS/Linux continua não comprovado por este recorte.

### Linhagem

#92 (contrato dry-run anterior) → P03/#124 → planos issue124-* → #128, head 2b84c7a14fbcc5c009a3366536ccb80ebe316ca0, merge d8c1a3c67948c047ea282ca4d839462153b4e60a → código atual. #123 é vizinha para runtime tail-outlier, não o destino da prova offline de dispatch.

### Fontes e corte

Critérios públicos da #124 reconsultados em 17/10; main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: tests/test_apex_initial_package.py, scripts/apex.ps1 (actionPlan e branch DryRun), ci.yml e testes tail-outlier. PR #128 no snapshot de 16/10 registra testes locais. Capturas de checks da Parte04 são de SHAs específicos e não são uma execução nova.

### Classe e limite da evidência

DIRETO ESTÁTICO: ausência de pwsh provoca falha, oito rótulos são comparados e a execução de Command ocorre depois da saída dry-run. RELATADO: 18 testes focados/69 root na entrega da #128. INFERÊNCIA VERIFICÁVEL: mutar somente Command deixa o rótulo esperado intacto. A mutação não foi aplicada nem o produto executado nesta revisão.

### Fluxo

Ação → switch constrói {Handler, Command} → com DryRun imprime Handler e retorna; sem DryRun executa Command. O teste lê o ramo do rótulo. Para provar dispatch, a observação precisa alcançar a chamada real ou uma interface de despacho cujo alvo seja capturado sem side effects.

### Consequências e risco

A lacuna corresponde ao critério explícito de testes separados por handler; não é mero aperfeiçoamento opcional depois do fechamento. CI verde apenas executaria as asserções que existem. Manter esse critério aberto comunica o alcance da prova; não significa que o dispatcher atual esteja funcionalmente quebrado.

### Alternativas e recomendação

Recomenda-se testar despacho com handlers substituídos por stubs/callbacks observáveis, sem containers/escritas/secrets. Uma estrutura única que derive nome e chamada pode reduzir divergência, mas deve ser verificada na fronteira realmente executada. Comparar strings no código é opção mais frágil. O mantenedor pode alterar o critério, desde que registre essa decisão.

### Dependências e paralelismo

A prova de dispatch pode ser desenvolvida offline sem Spark, ClickHouse, #117 ou conclusão total de #130. CI é evidência complementar sobre o SHA escolhido. Obter primeiro CI verde na main não substitui o controle discriminante nem é a única forma possível de provar a alteração. Plataforma/runner deve respeitar a matriz escolhida, sem inventar Ubuntu 26.04 ou Windows como requisito original desta issue.

### Plano e aceite propostos

Folha 1: invocar dispatcher sob handlers inofensivos e observar a ação realmente chamada para todas as oito entradas. Controle negativo: trocar o alvo preservando Handler deve falhar. Manter ausência de pwsh como erro e dry-run não mutante. Folha 2: conferir documentação macOS/Linux e anexar evidência hospedada aplicável. Aceite: cada critério explícito tem teste/documento e limite de plataforma; runtime tail-outlier fica na #123.

### Comunicação entre responsáveis

Minuta para revisão: dependência de pwsh e plano por ação existem; ainda falta prova discriminante da ligação Command→handler. Evitar mensagem de critérios todos satisfeitos ou recomendação de fechar somente por CI verde.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Tratar a comparação do rótulo handler= como prova de dispatch deixaria passar um Command trocado, porque o -DryRun retorna antes de & $actionPlan.Command; fechar só por CI verde comunicaria um alcance que o teste não tem. Que caso o teste ainda não cobre? — Nenhum dos testes consultados atual falha se o Command de tail-outlier apontar para outro handler mantendo a string; um stub ou callback observável cobriria a chamada real sem efeitos externos, e quais plataformas foram executadas e quais só documentadas segue em aberto. Como eu explicaria isso para outro pod? — A dependência de pwsh já é explícita na lane obrigatória e falha quando falta, e o plano por ação existe; o que segue aberto na #124 é a prova discriminante da ligação Command→handler e a documentação macOS/Linux.

### Próxima ação e encerramento

Owner a confirmar: manter #124 aberta para reconciliação do critério de dispatch e documentação. Fechar depois de prova discriminante e critérios restantes atendidos, ou de mudança explícita de escopo pelo mantenedor. Não mover a lacuna para follow-up opcional para justificar um fechamento prematuro.

<a id="item-018"></a>

## #165 — [Docs][Cross-pod] Reconciliar a linhagem do contrato e os cabeçalhos SQL

Frente: contratos_e_documentacao. Encaminhamento: decisao_do_mantenedor_e_documentacao.

### Identidade e estado

#165 — [Docs][Cross-pod] Reconciliar a linhagem do contrato e os cabeçalhos SQL. Autor gustocezar; gustocezar; aberta na consulta de 16/10/2026 18:29:24 UTC. O assignee histórico não ratifica owner ou prazo para a próxima entrega. Corte técnico c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Evitar que os pods confundam versão vigente, cabeçalho histórico e proposta ainda não ratificada. O benefício é uma explicação coerente das fronteiras de job_conf, correlação SQL e memória, sem alterar dados emitidos.

### Feito, faltante e não comprovado

O changelog v0.6 declara execution_id opcional e não altera o comportamento dos consumidores; a seção de stage linkage ainda fala de mapa futuro. A emissão de job_conf no primeiro onJobStart, descrita na linha 30, é outro fluxo. Confirmei PROPOSED em job_conf/Memory e RATIFIED no espelho infra. O comentário de 11/10 relata quatro propostas antes/depois, sem decisão do mantenedor; textos locais não foram reaceitos aqui.

### Linhagem

X13 → minuta PROP-X13-CONTRACT-RECONCILIATION → #165 → estudo documental comentado em 11/10. #115 é a frente de atribuição do consumidor; #117 é outra decisão de Verify. Não há commit/PR implementador apresentado nos comentários; código existente não constitui ratificação dos cabeçalhos.

### Fontes e corte

Fontes lidas: fontes/batch-public-sources/issue-165.md; fontes/current-open-issues.json; _build/input-registro.json; fontes/main-contract.txt:11; fontes/batch-public-sources/contract__job_conf.ddl.sql.txt:1; fontes/batch-public-sources/memory__sql__030_plan_memory.sql.txt:1; fontes/batch-public-sources/infra__sql__030_plan_memory.sql.txt:1. Corpos/comentários preservados do snapshot 16/10/2026; código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Recibos novos de código em batch-public-sources/*.json registram 17/10/2026 00:47 UTC; não atualizam o estado das issues. Linhas citadas usam os arquivos .txt/.md correspondentes. Fonte adicional: fontes/batch-public-sources/tests__test_telemetry_compatibility_matrix.py.txt:145.

### Classe e limite da evidência

FATO OBSERVADO: declarações divergentes nos arquivos fixados. RELATO HISTÓRICO: estudo e quatro alternativas atribuídos no comentário a Kimi/Codex em 11/10. PROPOSTA: reconciliação editorial com prova de autoridade para qualquer mudança normativa. Não houve teste nem prova de produtor nesta revisão.

### Fluxo

CONTRACT (versão/invariantes) + cabeçalhos job_conf/Memory + espelho infra (status declarado) → comparação por cláusula → mantenedor (autoridade e redação) → documentação coerente. Fluxo proposto para revisão; separa emissão onJobStart de correlação execution→stage.

### Consequências e risco

Um leitor pode interpretar um cabeçalho antigo como contrato atual e implementar um vínculo errado. A divergência textual tem alta confiança; sua ocorrência como erro de implementação ou incidente não foi demonstrada.

### Alternativas e recomendação

Recomendo uma PR documental pequena, preservando a história por notas e referências. Alternativa: manter PROPOSED com explicação explícita do status. Remover marcadores em massa reduziria ambiguidade aparente, mas inventaria ratificação; alterar DDL seria outro escopo. Texto é reversível, decisão normativa exige registro.

### Dependências e paralelismo

Depende de o mantenedor identificar qual ato ratificou cada extensão e aprovar o texto correspondente. A preparação dos quatro trechos pode correr em paralelo ao gate #115 e ao estudo #117; essas entregas não são gates técnicos para reconciliar redação. Coordenação limitada adicional: tests/test_telemetry_compatibility_matrix.py:145–147 exige os marcadores PROPOSED literalmente; se a redação mudar, atualizar essa guarda com evidência da história preservada, sem depender de concluir toda #180.

### Plano e aceite propostos

Inventariar quatro trechos com antes/depois e URL/SHA; associar cada afirmação a fonte normativa; marcar dúvidas de autoridade; revisar apenas texto; conferir links e que nenhuma mudança de SQL executável entrou no diff. Aceite: não confundir job_conf emitido com mapa de atribuição, nem declarar ratificação sem fonte. Caso negativo: texto novo que prometa consumo universal de execution_id deve ser rejeitado. Incluir revisão das asserções literais :145–147 do teste da matriz para que a correção autorizada de texto não seja rejeitada pelo retrato anterior.

### Comunicação entre responsáveis

Explicar ao outro pod o que é contrato aditivo, o que é implementação de consumidor e o que é decisão histórica. Na eventual PR, incluir tabela de cláusulas e limites; não dizer que o runtime foi consertado.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Tratar a emissão de job_conf no onJobStart como a mesma pendência da correlação execution→stage misturaria fluxos distintos, e retirar os marcadores PROPOSED em massa inventaria uma ratificação. Que caso o teste ainda não cobre? — Conferir links não basta: falta associar cada cabeçalho ao documento que autoriza retirar seu PROPOSED, e tests/test_telemetry_compatibility_matrix.py:145–147 fixa esses marcadores literalmente. Como eu explicaria isso para outro pod? — O contrato v0.6 é aditivo e torna execution_id opcional; os cabeçalhos de job_conf e Memory ainda dizem PROPOSED e o espelho infra diz RATIFIED, e só o mantenedor decide a redação, sem que isso conserte runtime.

### Próxima ação e encerramento

Mantenedor do contrato a confirmar: receber os quatro trechos e suas fontes; devolver decisões de status/redação. Encerrar após reconciliação documental revisada e integrada, ou decisão explícita de manter marcadores com justificativa. Sem nova tarefa runtime por inferência.

<a id="item-019"></a>

## #166 — [Feature][Pods 1 e 3] Explicar TAIL_OUTLIER nos consumidores sem confundir cauda com skew

Frente: front_verify_serve. Encaminhamento: decisao_de_apresentacao_e_implementacao_delimitada.

### Identidade e estado

#166 — [Feature][Pods 1 e 3] Explicar TAIL_OUTLIER nos consumidores sem confundir cauda com skew. Autor gustocezar; gustocezar; aberta na consulta de 16/10/2026 18:29:24 UTC. O assignee histórico não ratifica owner ou prazo para a próxima entrega. Corte técnico c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Explicar TAIL_OUTLIER sem convertê-lo em prova de join skew nem prescrever uma correção que o finding não sustenta. Os usuários de Front, Verify e Serve precisam distinguir sintoma observado, mecanismo conhecido e tratamento não aplicável.

### Feito, faltante e não comprovado

Confirmei que KnownFindingType inclui RETRY_PRESSURE e omite TAIL_OUTLIER, enquanto FindingType aceita strings novas. O watcher já existe e tem confiança 0.72. Serve mapeia TAIL_OUTLIER para unknown e tem fallback adaptive.enabled=true; o ramo de confiança baixa esvazia proposed_config, enquanto recusa de Verify retém diff/PR body mas conserva a receita acima do limiar. mechanism_check contém justificativa genérica de data skew. Comentários relatam 16 fixtures e matriz de 12 células, sem execução.

### Linhagem

F13 (Front), F18 (texto Verify), S17 (Serve) → P-TAIL → #166. #127 entregou o detector relacionado à #123; #137 já tratou RETRY_PRESSURE. Estudos C2 nos comentários caracterizam consumidores e não implementam o comportamento proposto. #168 estuda escala absoluta separadamente.

### Fontes e corte

Fontes lidas: fontes/batch-public-sources/issue-166.md; fontes/current-open-issues.json; _build/input-registro.json; ../parte-02-gemini/evidencias/escopos/types-ts.txt:62; fontes/lote2-engine__src__apex_engine__watchers__tail_outlier.py.txt:15; fontes/lote2-serve__src__apex_mcp__diagnose.py.txt:1685; fontes/lote2-verify__src__apex_verify__guardrails.py.txt:168. Corpos/comentários preservados do snapshot 16/10/2026; código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Recibos novos de código em batch-public-sources/*.json registram 17/10/2026 00:47 UTC; não atualizam o estado das issues. Linhas citadas usam os arquivos .txt/.md correspondentes.

### Classe e limite da evidência

FATO OBSERVADO: uniões de tipos, mapeamento e ramos do código. RELATO HISTÓRICO: matrizes e fixtures locais em 11/10; não aceite novo. INFERÊNCIA delimitada: fallback pode oferecer configuração não justificada quando os gates permitirem; não afirmo que o finding padrão de confiança 0.72 oferece diff com limiar padrão 0.75. PROPOSTA: política explícita por tipo.

### Fluxo

Engine → finding TAIL_OUTLIER com duração/população → Front (rótulo), Verify (mecanismo ou não aplicável) e Serve (explicação/receita); confiança e recusa já registrada → gates independentes do diff. Fluxo observado estaticamente; nenhuma chamada real ou tela executada.

### Consequências e risco

Confundir cauda e skew pode induzir tuning indevido; omitir explicação pode ocultar a limitação. A existência dos ramos é certa; frequência e dano operacional não foram medidos. A abertura do tipo impede concluir que a UI rejeita automaticamente o finding.

### Alternativas e recomendação

Recomendo preservar o finding e explicar limites antes de criar receita. Alternativas: rótulo específico com advisory; Verify declarar não aplicável; receita nova somente com base causal adequada. Reutilizar receita de skew reduz trabalho mas viola a evidência de duração isolada. Mudanças de apresentação são reversíveis; novos mecanismos exigem estudo.

### Dependências e paralelismo

Owners dos três consumidores devem decidir mensagens e comportamento de unknown. Pode ser dividido em mudanças atômicas Front/Verify/Serve com a mesma matriz; não depende de alterar threshold da #168 nem de implementar RETRY_PRESSURE de novo. O detector da #127 é antecedente já integrado.

### Plano e aceite propostos

Caracterizar tipos TAIL_OUTLIER, SKEW_ON_JOIN, RETRY_PRESSURE e unknown; fixar política de mensagem/receita; preparar testes abaixo, igual e acima de 0.75, com/sem recusa; verificar proposed_config, diff e PR body separadamente. Aceite: nenhum conselho de skew fundamentado apenas em duração, fallback explícito e controles existentes preservados. Registrar consumers sem predictor, sem simular ganho certificado.

### Comunicação entre responsáveis

Na issue/PR futura, mostrar um mesmo finding atravessando as três superfícies e explicar por que preservar uma receita, gerar diff e certificar execução são estados distintos. A matriz local relatada é ponto de partida, não resultado de testes novos.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Usar a receita de skew para toda cauda induziria tuning sem base causal, porque TAIL_OUTLIER registra duração e população, não join skew; o fallback adaptive.enabled=true do Serve pode oferecer essa configuração quando os gates permitirem. Que caso o teste ainda não cobre? — Falta discriminar confiança abaixo, igual e acima do limiar 0,75, com e sem recusa do Verify, separando proposed_config, diff e PR body; o finding padrão tem confiança 0,72. Como eu explicaria isso para outro pod? — KnownFindingType omite TAIL_OUTLIER, mas o tipo aberto aceita a string, então a UI não o rejeita; um tipo desconhecido pode ser mostrado honestamente sem receita, e a política por tipo cabe aos owners de Front, Verify e Serve.

### Próxima ação e encerramento

Pods 1 e 3/Verify a confirmar: escolher a política a partir dos ramos citados e revisar fixtures. Encerrar apenas quando os consumidores afetados tiverem comportamento decidido, testes discriminantes e evidência de integração correspondente; manter detector e piso absoluto fora do delta.

<a id="item-020"></a>

## #167 — [Bug][Pod 2] Alinhar argumentos do braço ON do harness R9D com o runner canônico

Frente: harness_e_pacote. Encaminhamento: revisao_de_candidato_e_provas_delimitadas.

### Identidade e estado

#167 — [Bug][Pod 2] Alinhar argumentos do braço ON do harness R9D com o runner canônico. Autor gustocezar; gustocezar; aberta na consulta de 16/10/2026 18:29:24 UTC. O assignee histórico não ratifica owner ou prazo para a próxima entrega. Corte técnico c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Alinhar a interface do runner ON com os argumentos emitidos pelo R9D, para que o experimento possa iniciar sem alterar silenciosamente a configuração comparada entre os braços.

### Feito, faltante e não comprovado

Na base, e2e_command envia EnvFile e AdditionalComposeFile aos dois runners; só OFF os declara. O comentário mais recente relata candidato local conjunto com #174, prova do dispatcher e2e em macOS sob stubs (base 7/3, candidato 10/0, controle 8/2) e análise Compose sem daemon. Windows/Compose real, assimetria de preflight e decisão de múltiplos overlays por -File permanecem abertos. Não há URL pública de implementação nos comentários.

### Linhagem

E16 → P-GATE → #167; E08 → #174 compartilha passagem de configuração. E17 continua #123. #113 define protocolo de overhead. A sequência histórica contém desenho de fixtures, correções estáticas e depois prova de entrypoint relatada; não voltar a tratar toda a prova como apenas helper W07. Nenhuma árvore local foi identificada/reaceita nesta rodada.

### Fontes e corte

Fontes lidas: fontes/batch-public-sources/issue-167.md; fontes/current-open-issues.json; _build/input-registro.json; fontes/batch-public-sources/dev__scripts__r9d_overhead_ab.py.txt:368; fontes/lote2-dev__scripts__e2e_canonical.ps1.txt:1; fontes/batch-public-sources/dev__scripts__r9d_e2e_canonical_noplugin.ps1.txt:1. Corpos/comentários preservados do snapshot 16/10/2026; código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Recibos novos de código em batch-public-sources/*.json registram 17/10/2026 00:47 UTC; não atualizam o estado das issues. Linhas citadas usam os arquivos .txt/.md correspondentes.

### Classe e limite da evidência

FATO OBSERVADO: incompatibilidade entre chamada Python e assinaturas PowerShell nos blobs fixados. RELATO HISTÓRICO: 85 testes iniciais e prova posterior de 10 casos com stubs; não somar como execução desta revisão. A análise de parser sem daemon não prova isolamento de rede. PROPOSTA: revisar candidato e aceitar separadamente contrato de argumentos e execução real.

### Fluxo

R9D → argv com EnvFile/overlay → runner ON ou OFF → Compose com configuração comparável → workload futuro. ON mantém assertions de telemetria e OFF as omite por desenho; essa diferença funcional deve ficar fora da métrica primária de submit, conforme o harness. Fluxo estático.

### Consequências e risco

A falha de binding pode impedir iniciar; uma correção parcial pode introduzir comparação entre ambientes distintos. Alta confiança na incompatibilidade estática, sem benchmark executado. Não atribuir à #167 a higiene do gate tail-outlier nem a validade estatística do protocolo.

### Alternativas e recomendação

Recomendo preservar uma interface comum explícita, revisando o candidato que declara os parâmetros no ON. Adaptar apenas a chamada é possível, mas deve manter seleção equivalente de configuração; copiar configuração para .env reintroduz o risco #174. Uma PR conjunta pequena com E08 pode ser coesa; dividir só com ordem/contrato claros.

### Dependências e paralelismo

O contrato compartilhado com #174 é dependência técnica do delta; publicação e escopo da PR são decisões do mantenedor. Windows e Compose são camadas posteriores de prova, não razões para repetir testes já relatados sem mudança. #113 governa benchmark; #123/E17 permanece em paralelo.

### Plano e aceite propostos

Identificar hash/árvore do candidato; confrontar delta com as três fontes; revisar forwarding, preflight e argumento retirado como controle negativo; decidir suporte de múltiplos overlays por -File. Validar futuramente binding em Windows e depois configuração/identidade Compose própria, registrando RCs e limites. Aceite da correção: argumentos aceitos e mesma configuração intencional nos braços; aceite de overhead exige protocolo/prova próprios.

### Comunicação entre responsáveis

Explicar por que a correção é de interface e configuração. Publicar somente resumo sanitizado, hashes e resultados por ambiente, distinguindo parser, stubs, Windows e Compose. Registrar a correção do RC negativo para 1 e não repetir a alegação não demonstrada de zero sockets do gerador histórico.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Misturar variantes ou diferenças de ambiente não identificadas pode confundir a atribuição de um resultado. Fixar candidato, configuração e alcance da prova antes de compará-los. Que caso o teste ainda não cobre? — A prova relatada usa stubs no macOS e análise Compose sem daemon; -File com vários overlays, Windows nativo e Compose real seguem sem prova. Como eu explicaria isso para outro pod? — É uma correção de interface: o R9D envia os mesmos argumentos aos dois runners e só o OFF os declarava; as assertions de telemetria só no ON são diferença deliberada fora da métrica primária, e qualquer outra diferença contamina a comparação.

### Próxima ação e encerramento

Autor/owner Pod 2 a confirmar: fornecer candidato identificado e provas existentes; saída revisável é delta mínimo e matriz de argumentos/configuração. Fechar a issue após integração e provas de aceite acordadas, sem declarar overhead medido por teste de binding. Não criar outra implementação concorrente antes de revisar o candidato.

