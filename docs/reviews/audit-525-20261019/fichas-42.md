# Fichas documentais — lote 42

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-411"></a>

## #25 — [CA] Decide shadow repo governance — dataship-spark-plat-v0

Frente: historico. Encaminhamento: duplicata_encerrada_com_destino.

### Identidade e estado

Issue #25, Commander Attention (`type:commander-attention`, `priority:p0`); autor `luanmorenommaciel` (OWNER); sem assignee. Criada em 2026-05-26; fechada em 2026-09-17T16:45:43Z (`completed`) como duplicata de #23; 2 comentários. O rótulo `duplicate` foi aplicado no dia do fechamento (timeline). Diz "See ADR-002", que aqui significa #23, não o ADR-002 canônico.

### Intenção e benefício

Cobrar do Commander a decisão integrar/espelhar/isolar sobre o `dataship-spark-plat-v0`, com idade de ~47 h desde o anúncio de Gabriel.

### Feito, faltante e não comprovado

Encerrada como duplicata de #23, que foi resolvida por reconstrução interna. O fechamento diz que a questão se resolveu pela reconstrução de julho e pelo plano de arquivamento do #105. Relatado (2026-06-08): a branch `gustocezar/feature/desacoplamento-geradores` como evidência da proposta "repositório de evidência → slice curado → validação coletiva". Nada falta além do que #23 e #105 carregam.

### Linhagem

Commander Attention (2026-05-26) → nota (2026-06-08) → referências cruzadas de #29, #30, #33 e #40 → rótulo `duplicate` e fechamento (2026-09-17). Elo de destino: #23 (decisão) e #105 (arquivamento). Timeline pública (API, observada em 2026-10-17T17:30:51Z; 15 eventos): fechada por `luanmorenommaciel` em 2026-09-17; rótulos aplicados no dia do fechamento: `duplicate`; item adicionado a um Project do GitHub; referências cruzadas na timeline retornada: #29, #30, #33, #40; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 25); [nota](https://github.com/luanmorenommaciel/apex/issues/25#issuecomment-4648533968); [fechamento](https://github.com/luanmorenommaciel/apex/issues/25#issuecomment-5718027624); timeline coletada em `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/issue25-timeline.json`.

### Classe e limite da evidência

DIRETO: rótulo e datas da timeline; texto. RELATADO: o fluxo proposto. Não há afirmação técnica nova além das de #23.

### Fluxo

Fluxo de escalonamento: pergunta de governança → Commander Attention → duplicata do ADR → resolução por reconstrução → fechamento com destino.

### Consequências e risco

Nenhum impacto. O fechamento aponta o destino, o que preserva a rastreabilidade.

### Alternativas e recomendação

(a) Manter fechada como duplicata (recomendado); (b) trocar o motivo para `not_planned`/duplicate — cosmético e exige permissão do mantenedor.

### Dependências e paralelismo

Nenhuma dependência própria: o destino da decisão é #23 e o da custódia das branches é #105; esta issue não acrescenta requisito.

### Plano e aceite propostos

Condição explícita de não ação: duplicata com destino registrado; nada a produzir além do que #23 e #105 já cobrem.

### Comunicação entre responsáveis

Para a consolidação: "#25 é duplicata de #23 (rótulo aplicado no fechamento); a decisão e a custódia ficam em #23 e #105".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — tratar #25 como decisão separada duplicaria a contagem de governança. (b) Que caso o teste ainda não cobre? — não encontrei teste ligado a este item nas fontes lidas; é escalonamento. (c) Como eu explicaria isso para outro pod? — "era o lembrete para o Commander da mesma pergunta do #23". (d) Commander Attention duplicadas deveriam ser fechadas no momento da criação?

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento definitivo como duplicata; o destino é #23 e não há condição própria de reabertura.

<a id="item-412"></a>

## #26 — [CA] Validate Gabriel's 'deprioritization' pivot before Tuesday sync

Frente: historico. Encaminhamento: duplicata_encerrada_com_destino.

### Identidade e estado

Issue #26, Commander Attention (`priority:p0`); autor `luanmorenommaciel` (OWNER); sem assignee. Criada em 2026-05-26; fechada em 2026-09-17T16:45:47Z (`completed`) como duplicata de #24; 1 comentário. Rótulo `duplicate` aplicado no dia do fechamento (timeline). "See ADR-003" aqui é #24.

### Intenção e benefício

Pedir ao Commander que aprovasse, contestasse ou exigisse justificativa para a despriorização proposta pela Crew antes do sync de terça.

### Feito, faltante e não comprovado

Encerrada como duplicata de #24. O fechamento acrescenta que o prazo (sync de 2026-05-27) passou e que o #34 "re-escopou" o trabalho. Não comprovado aqui: a relação com o #34, que será revisada na ficha própria do #34.

### Linhagem

Commander Attention (2026-05-26) → referência cruzada do #40 (2026-07-04) → rótulo `duplicate` e fechamento (2026-09-17). Destino: #24; trabalho re-escopado no #34. Timeline pública (API, observada em 2026-10-17T17:30:53Z; 11 eventos): fechada por `luanmorenommaciel` em 2026-09-17; rótulos aplicados no dia do fechamento: `duplicate`; item adicionado a um Project do GitHub; referências cruzadas na timeline retornada: #40; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 26); [fechamento](https://github.com/luanmorenommaciel/apex/issues/26#issuecomment-5718028740); timeline em `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/issue26-timeline.json`.

### Classe e limite da evidência

DIRETO: datas e rótulos. RELATADO: "#34 re-scoped the work" (a conferir na ficha #34).

### Fluxo

Fluxo de escalonamento: proposta da Crew → lembrete ao Commander → prazo vence → duplicata → fechamento.

### Consequências e risco

Nenhum impacto em produto ou backlog: o fechamento aponta o destino (#24) e o motivo (prazo vencido). Confiança alta.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) nenhuma alternativa útil.

### Dependências e paralelismo

Nenhuma dependência própria: a decisão de prioridade é #24 e o re-escopo citado é #34; esta issue não acrescenta requisito.

### Plano e aceite propostos

Condição explícita de não ação: lembrete de decisão vencido, com destino registrado.

### Comunicação entre responsáveis

Para consolidação: #26 foi encerrada como duplicata de #24; o mantenedor cita prazo passado em 27/05 e re-escopo em #34. A data citada é quarta-feira e diverge do Tuesday do corpo.

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — contar #26 como trabalho próprio inflaria o backlog histórico. (b) Que caso o teste ainda não cobre? — não encontrei teste ligado a este item nas fontes lidas. (c) Como eu explicaria isso para outro pod? — "o lembrete de uma decisão que já tinha issue própria". (d) O #34 de fato substituiu esse escopo?

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento definitivo como duplicata de #24, sem condição própria de reabertura.

<a id="item-413"></a>

## #27 — [CA] Coordinate dual tech leads — Gabriel + Guilherme on independent stacks

Frente: historico. Encaminhamento: historico_obsoleto_ownership_estrutural.

### Identidade e estado

Issue #27, Commander Attention (`priority:p1`); autor `luanmorenommaciel` (OWNER); sem assignee. Criada em 2026-05-26; fechada em 2026-09-17T16:45:49Z (`completed`) como "obsolete"; 1 comentário.

### Intenção e benefício

Evitar paralelismo sem plano de integração entre duas lideranças técnicas emergentes (plataforma de Gabriel e collector em Go de Guilherme), com uma mensagem explícita de "quem é dono do quê".

### Feito, faltante e não comprovado

Fechamento relata ownership estrutural por briefs de raia, tasks/done e fluxo branch por issue. O extrato de 1e0ba80 confirma docs/lanes e tasks/done, sem contagem de seus arquivos. Mudanças em #18/#22 e #19/#23 contextualizam o encerramento dos dois stacks originais.

### Linhagem

Sinal de risco (2026-05-26) → divisão de pods em #30 → raias de 2026-07-23 → fechamento. Elo ausente: a mensagem de coordenação recomendada; não encontrei registro dela nas fontes lidas. Timeline pública (API, observada em 2026-10-17T17:30:54Z; 11 eventos): fechada por `luanmorenommaciel` em 2026-09-17; item adicionado a um Project do GitHub; referências cruzadas na timeline retornada: #30, #40; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 27); [fechamento](https://github.com/luanmorenommaciel/apex/issues/27#issuecomment-5718029180); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_27.txt` (`docs/lanes`, `tasks/done` em `1e0ba802049b4ebe8fb474a7853c604df2b93aeb`).

### Classe e limite da evidência

DIRETO: diretórios do ledger. RELATADO: "no coordination signal observed in Discord". INFERÊNCIA: o risco se dissolveu porque os dois stacks não seguiram adiante.

### Fluxo

Fluxo de coordenação: duas frentes paralelas → risco de integração → raias com briefs e ledger → ownership por raia.

### Consequências e risco

Nenhum. Limite: "ownership estrutural" por documento não garante dono ativo hoje; a v2 e o Codex registram que autor não equivale a owner designado.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) nenhuma alternativa útil.

### Dependências e paralelismo

Nenhuma dependência: as duas frentes do risco não seguiram (#18/#22 sem collector próprio; #19/#23 com plataforma reconstruída).

### Plano e aceite propostos

Condição explícita de não ação: o risco descrito perdeu o objeto; nenhum artefato ou controle a criar.

### Comunicação entre responsáveis

Para consolidação: #27 foi fechado como sinal obsoleto; o mantenedor aponta raias e ledger como mecanismo de ownership, sem provar designação ativa de pessoas hoje.

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — reabrir um sinal de coordenação de maio não refletiria o time atual. (b) Que caso o teste ainda não cobre? — não encontrei teste ligado a este item nas fontes lidas. (c) Como eu explicaria isso para outro pod? — "o risco era duas frentes sem plano; as raias resolveram". (d) As raias têm dono nomeado hoje?

### Próxima ação e encerramento

Nenhuma ação. Owner a confirmar: nenhum. Encerramento definitivo; reabrir só se surgirem de novo duas frentes paralelas sem plano de integração.

<a id="item-414"></a>

## #28 — [BLOCKER] GitHub repo access for Crew A members

Frente: historico. Encaminhamento: bloqueio_resolvido_com_evidencia_indireta.

### Identidade e estado

Issue #28, blocker (`type:blocker`, `priority:p0`, `blocked`); autor `luanmorenommaciel` (OWNER); sem assignee. Criada em 2026-05-26; fechada em 2026-09-17T16:45:51Z (`completed`) como "resolved"; 1 comentário.

### Intenção e benefício

Dar acesso de escrita aos membros da Crew A, que relataram não conseguir abrir PR. Critério do corpo: fechar quando todos os handles tiverem acesso de escrita.

### Feito, faltante e não comprovado

Resolvido segundo o fechamento, com evidência indireta: a API de contribuidores mostraria gustocezar (52), sidymar (66) e agmarcastro (7) commits. Conferi por `git shortlog` em `1e0ba80`: "Sidymar Prexedes" 65 + "Sidymar" 1 = 66; agmarcastro 7; Augusto aparece sob três nomes (Augusto Cezar 40, Augusto Silva 17, gustocezar 8), então o 52 não é reproduzível só por nomes do Git. Indício adicional no mesmo dia: #11 e #12 foram criadas por colaboradores às 21:07–21:08 de 2026-05-26. Não comprovado: que todos os handles da Crew tinham escrita; o corpo não lista os handles esperados.

### Linhagem

Bloqueio (2026-05-26, "tentamos fazer o PR e estamos sem acesso") → Commander assume → issues de teste #11/#12 no mesmo dia → contribuições de agosto → fechamento por evidência de commits. Elo ausente: registro de quando o acesso foi concedido e a quem. Timeline pública (API, observada em 2026-10-17T17:30:55Z; 10 eventos): fechada por `luanmorenommaciel` em 2026-09-17; item adicionado a um Project do GitHub; referências cruzadas na timeline retornada: nenhuma; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 28); [fechamento](https://github.com/luanmorenommaciel/apex/issues/28#issuecomment-5718029643); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_28.txt` (`git shortlog -sn` em `1e0ba802049b4ebe8fb474a7853c604df2b93aeb`).

### Classe e limite da evidência

DIRETO: contagem de commits por nome no Git; datas das issues de teste. RELATADO: números da API de contribuidores (não reconsultada). INFERÊNCIA: commits na main implicam acesso de escrita ou merge por terceiros; não distinguem os dois.

### Fluxo

Fluxo relatado: membro informa falta de acesso → Commander assume mitigação → atividade posterior em issues/commits → fechamento em setembro. Convite, concessão e lista de permissões não foram demonstrados nas fontes.

### Consequências e risco

Nenhum impacto atual. Limite: "commits na main" não prova acesso direto de escrita (o merge pode ter sido feito por outra pessoa).

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) nenhuma ação: permissões atuais estão fora do escopo histórico.

### Dependências e paralelismo

Nenhuma dependência técnica própria nesta ficha; o mantenedor encerrou o pedido de acesso ao repositório. Permissão no Project é objeto distinto em #31.

### Plano e aceite propostos

Condição de não ação histórica: pedido encerrado pelo mantenedor em setembro; a data de concessão e abrangência dos handles não foram comprovadas. Permissões atuais estão fora do recorte.

### Comunicação entre responsáveis

Para a consolidação: "#28 resolvido; a evidência é de atividade, não de lista de permissões".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — tratar contribuições como prova universal de Write confundiria autoria, merge e permissão. Que caso o teste ainda não cobre? — lista completa de handles e concessões de acesso. Como eu explicaria isso para outro pod? — o mantenedor encerrou o bloqueio com base em atividade; a data exata de liberação não foi demonstrada.

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento definitivo; reabrir só se um membro ativo relatar de novo falta de acesso ao repositório.

<a id="item-415"></a>

## #29 — [TASK] Validar slice skew_on_join_30x v4 corrigido com a Crew A

Frente: historico. Encaminhamento: historico_substituido_slice_em_branch_arquivada.

### Identidade e estado

Issue #29, tarefa de validação (`type:task`, `phase:review`, `documentation`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-06-08 (renomeada e rotulada em 2026-06-09); fechada em 2026-09-17T16:45:54Z por `luanmorenommaciel` como "superseded"; 3 comentários. Foi a "issue central de validação": as notas de 2026-06-08 em #5–#9, #16, #17, #19, #21–#25 e #30 apontam para ela (timeline).

### Intenção e benefício

Pedir à Crew A que revisasse, reproduzisse e decidisse se o slice `skew_on_join_30x` v4 (cenário YAML, gerador sintético, watcher de `shuffle_skew`, oráculo contra log real, testes, CI e documentação) seria o padrão dos próximos slices.

### Feito, faltante e não comprovado

Relatado no corpo: evidência local (sintético 27,9x, real 29,5x, "GATE VERDE", 29 testes). Substituído, segundo o fechamento: o slice YAML não está na main de referência e vive na branch; o caminho aceito é `dev/jobs/skew_join.py` → `engine/watchers/skew.py` (regra de cauda em forma fechada) → guardrails da `verify/`. Conferi: os três arquivos existem em `1e0ba80`; `skew.py` implementa veredito de cauda (`tail_bound`, `WORK_BOUND`, linhas 132–165); o commit `8ec2d39` citado está em cinco branches remotas, entre elas `gustocezar/feature/desacoplamento-geradores`, que contém `docs/specs/scenario-validation-criteria-v1.md` e `docs/specs/skew-slice-v4.md`; esse ref (`bd8a08b`), com `8ec2d39`, está no bundle do #105 (`fontes/batch-claude-historico-corrigido-sources/claude/fontes/reconferencia/ponto12-bundle-105.txt`). Falta: não encontrei registro da decisão da Crew sobre o padrão nas fontes lidas.

### Linhagem

Slice local (2026-06-08) → sugestão de RAG no ClickHouse por `Josenyldo` (2026-06-08) → separação do `validation_criteria` para #32 (2026-06-09) → laboratório e watcher da main seguem outro desenho → fechamento. Elos ausentes: revisão da Crew e decisão sobre o padrão; destino da sugestão de RAG (sem resposta registrada). Timeline pública (API, observada em 2026-10-17T17:30:57Z; 28 eventos): fechada por `luanmorenommaciel` em 2026-09-17; referências cruzadas na timeline retornada: #9, #16, #17, #19, #21, #23, #25, #5, #6, #7, #8, #22, #24, #30, #32, #33; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 29); [comentário Josenyldo](https://github.com/luanmorenommaciel/apex/issues/29#issuecomment-4654615089), [separação para #32](https://github.com/luanmorenommaciel/apex/issues/29#issuecomment-4660723716), [fechamento](https://github.com/luanmorenommaciel/apex/issues/29#issuecomment-5718030104); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_29.txt` (branches que contêm `8ec2d39`, arquivos da branch, `skew.py` em `1e0ba802049b4ebe8fb474a7853c604df2b93aeb`).

### Classe e limite da evidência

DIRETO: arquivos na branch e na main, branches que contêm o commit (clone de 2026-10-16). RELATADO: razões 27,9x/29,5x, 29 testes, "GATE VERDE" — execução local não reproduzida. INFERÊNCIA: a main resolveu skew com regra analítica sobre dados reais, não com oráculo sintético.

### Fluxo

Dois fluxos: (estudo) cenário YAML → event log sintético → watcher → oráculo contra `real_log.ndjson`; (main) `skew_join.py` → telemetria → `watchers/skew.py` → `verify/` guardrails.

### Consequências e risco

Risco de leitura: o corpo afirma "validado de ponta a ponta" para um artefato que não está na main. A evidência do estudo está no bundle do #105 (o ref `gustocezar/feature/desacoplamento-geradores` = `bd8a08b` contém `8ec2d39` e os dois specs). Nenhum incidente registrado nas fontes lidas.

### Alternativas e recomendação

(a) Manter fechada; a branch já está preservada no bundle do #105 (recomendado); (b) portar o oráculo sintético como teste de regressão do watcher atual — trabalho novo, exige decisão; (c) reabrir — o fechamento indica outro caminho aceito.

### Dependências e paralelismo

Custódia coberta pelo bundle do #105 (recibo Codex de 2026-10-17: 5 refs restauradas, `fsck` PASS; hash e contenção reconferidos aqui). Um eventual porte do oráculo seria trabalho novo da raia engine.

### Plano e aceite propostos

Não ação. Se o oráculo for reaproveitado: issue nova com aceite "o watcher atual dispara no log real de skew e não dispara no baseline sem skew" (controle negativo).

### Comunicação entre responsáveis

Para a consolidação: "#29 foi o centro do estudo de junho; o slice ficou na branch e a main seguiu outro desenho".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — perder branches e também o bundle removeria os rastros de estudo identificados. Que caso o teste ainda não cobre? — qualidade da distribuição, incluindo task fria vazia, é preocupação documentada em #32; não certificada nesta revisão. Como eu explicaria isso para outro pod? — houve um estudo local relatado de skew, preservado em branch/bundle; a main seguiu outro desenho. A sugestão de RAG teve decisão documentada?

### Próxima ação e encerramento

Nenhuma aqui. Owner a confirmar: custodiante do #105 para a branch. Encerramento: já fechada.

<a id="item-416"></a>

## #30 — [TASK] Alinhar divisao dos pods e responsabilidades da Crew A

Frente: historico. Encaminhamento: historico_substituido_por_raias.

### Identidade e estado

Issue #30, tarefa de organização (`type:task`, `phase:design`, `priority:p1`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-06-08; fechada em 2026-09-17T16:45:57Z (`completed`) como "superseded"; 1 comentário. O épico #15 aponta para ela como referência dos membros e pods.

### Intenção e benefício

Definir uma divisão inicial de pods (Generator/Scenarios, Parser/Evidence, Watchers, Oracle, CI, Platform, Collector/Storage, Docs) com responsabilidades e pontos de integração, para evitar trabalho duplicado.

### Feito, faltante e não comprovado

Substituído: segundo o fechamento, a divisão foi decidida em 2026-07-23 em `docs/architecture/APEX-V1-SWIMLANES.md` e `APEX-V1-PR-PLAN.md` (raias, capitães e plano de 12 PRs) e entregue como 8 raias. Conferi: os dois arquivos foram adicionados em `85de52d` (2026-07-23, "definir arquitetura por raias e plano de prs"); em `1e0ba80` o SWIMLANES se declara "HISTORICAL — the 6-lane design as approved on 2026-07-23" e nomeia "Captain: Augusto Cezar". Ou seja, o documento aprovou 6 raias, e o CHANGELOG da v0.1.0 fala em 8. Os pods de hoje (Pod 1 Front/Verify, Pod 2 Engine/Infra, Pod 3 Serve) não são os pods propostos aqui.

### Linhagem

Proposta de pods (2026-06-08) → raias aprovadas (2026-07-23) → v0.1.0 com 8 raias → pods atuais (1–3) → fechamento. Elo ausente: mapeamento entre a proposta, as 6 raias aprovadas, as 8 entregues e os 3 pods atuais. Timeline pública (API, observada em 2026-10-17T17:30:58Z; 12 eventos): fechada por `luanmorenommaciel` em 2026-09-17; referências cruzadas na timeline retornada: #15, #29, #33, #34, #39; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 30); [fechamento](https://github.com/luanmorenommaciel/apex/issues/30#issuecomment-5718030675); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_30.txt` (commit de criação e seções do SWIMLANES em `1e0ba802049b4ebe8fb474a7853c604df2b93aeb`).

### Classe e limite da evidência

DIRETO: data de criação dos documentos e o aviso HISTORICAL. RELATADO: "shipped as 8 lanes". INFERÊNCIA: houve três organizações sucessivas (proposta, 6 raias, 8 raias) e uma quarta por pods.

### Fluxo

Fluxo organizacional: pods propostos → raias aprovadas → raias entregues → pods atuais.

### Consequências e risco

Baixo. Risco de leitura: quem procurar "divisão de pods" encontra quatro versões; nenhuma diz qual vale para o backlog atual.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) acrescentar à consolidação uma tabela raia × pod atual; (c) reabrir — sem objeto.

### Dependências e paralelismo

Nenhuma dependência técnica; a tabela raia × pod sugerida no campo 11 depende só de leitura de `docs/architecture` e dos pods atuais.

### Plano e aceite propostos

Não ação. Documentação mínima sugerida: tabela raia → pod atual na consolidação, com fonte.

### Comunicação entre responsáveis

Para a consolidação: "#30 foi substituída pelas raias de julho; os pods atuais são outra divisão".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — reaplicar a divisão de junho conflitaria com os pods atuais. (b) Que caso o teste ainda não cobre? — não encontrei teste ligado a este item nas fontes lidas; é organização. (c) Como eu explicaria isso para outro pod? — "a divisão de junho virou raias em julho e pods depois". (d) Qual documento diz hoje quem é dono de cada raia?

### Próxima ação e encerramento

Nenhuma ação obrigatória. Owner a confirmar: mantenedor, se quiser a tabela raia × pod. Encerramento: já fechada.

<a id="item-417"></a>

## #31 — [CA] Liberar acesso Write ao Project Crew A — Apex

Frente: historico. Encaminhamento: obsoleto_criterio_nao_atendido_sem_efeito.

### Identidade e estado

Issue #31, Commander Attention (`priority:p1`, `blocked`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-06-09; fechada em 2026-09-17T16:45:59Z por `luanmorenommaciel` como "obsolete"; 1 comentário.

### Intenção e benefício

Dar a `@gustocezar` permissão Write no Project "Crew A — Apex" para incluir e classificar as issues #1–#10, #29 e #30, mantendo o Project como fonte oficial de acompanhamento.

### Feito, faltante e não comprovado

Fechamento declara obsolescência pela mudança da fonte de verdade para tasks/done e docs/task-specs; não documenta concessão de permissão. Corpo relata erro AddProjectV2ItemById para gustocezar. O cumprimento do critério original e permissões atuais não foram verificados; atividade no repositório é domínio de permissão diferente.

### Linhagem

Pedido (2026-06-09) → nenhuma resposta registrada até o fechamento → mudança da fonte de verdade para o ledger → fechamento como obsoleto. Elo ausente: não encontrei evidência de que o critério de conclusão do corpo tenha sido cumprido. Timeline pública (API, observada em 2026-10-17T17:30:59Z; 6 eventos): fechada por `luanmorenommaciel` em 2026-09-17; referências cruzadas na timeline retornada: nenhuma; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 31); [fechamento](https://github.com/luanmorenommaciel/apex/issues/31#issuecomment-5718031207); timelines de #25, #26, #28 e #31 em `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/`.

### Classe e limite da evidência

DIRETO: texto do erro, datas, eventos de Project na timeline. RELATADO: mudança da fonte de verdade. NÃO VERIFICADO: permissões e conteúdo do Project.

### Fluxo

Fluxo documentado: pedido de Write no Project após erro relatado → fechamento por migração do acompanhamento para ledger. Não é possível inferir a lista completa de pessoas com Write no Project.

### Consequências e risco

Baixo. O Project pode estar desatualizado e ser lido como oficial por alguém; o fechamento declara que não é mais a fonte. Limite: a v2 e o Codex usam o ledger e as issues, não o Project.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) se o Project for usado de novo, conceder a permissão na hora, sem tarefa; (c) arquivar o Project para evitar leitura como oficial — decisão do dono.

### Dependências e paralelismo

Nenhuma dependência: a mudança de fonte de verdade para o ledger já ocorreu; o arquivamento do Project é decisão isolada do dono.

### Plano e aceite propostos

Condição explícita de não ação: o critério perdeu sentido com a mudança de fonte de verdade.

### Comunicação entre responsáveis

Para consolidação: #31 foi fechada como obsoleta pela migração ao ledger; o cumprimento do acesso solicitado não foi demonstrado nas fontes.

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — manter Project e ledger em paralelo criaria duas fontes de status. (b) Que caso o teste ainda não cobre? — não encontrei teste ligado a este item nas fontes lidas; é permissão. (c) Como eu explicaria isso para outro pod? — "o quadro do GitHub não é mais onde acompanhamos o trabalho". (d) O Project antigo deveria ser arquivado?

### Próxima ação e encerramento

Nenhuma. Owner a confirmar: dono do Project, se quiser arquivá-lo. Encerramento definitivo.

<a id="item-418"></a>

## #32 — [TASK] Validar contrato validation_criteria dos scenarios Apex

Frente: historico. Encaminhamento: historico_nao_implementado_funcao_coberta_em_parte.

### Identidade e estado

Issue #32, tarefa de contrato (`type:task`, `phase:review`, `documentation`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-06-09; fechada em 2026-09-17T16:46:01Z por `luanmorenommaciel` como "superseded"; 1 comentário. Ligada ao registro L15.

### Intenção e benefício

Validar um gate de qualidade estrutural do event log antes do Watcher (`validation_criteria`): eventos obrigatórios, número mínimo de tasks, colapso em uma única task, tasks frias vazias, operador de join e stage correto, para que o Watcher não emita "GATE VERDE" sobre evidência inválida.

### Feito, faltante e não comprovado

O fechamento relata que validation_criteria nunca foi implementado. As buscas pelo literal retornam zero nos SHAs 1e0ba80 e c3c3ea3; guardrails.py, CONTRACT-EXTENSION-v0.3 e a classe Coverage existem no recorte. Isso não exclui lógica equivalente com outros nomes nem demonstra a cobertura dos casos específicos. O aceite desta issue pedia validar e acordar o contrato, explicitamente sem implementá-lo; essa validação contemporânea não foi localizada nas fontes lidas.

### Linhagem

Proposta separada do #29 (2026-06-09, commit `8ec2d39`) → referência do #41 (2026-07-04) → não implementado na main de referência → fechamento "superseded". Elo ausente: comparação caso a caso entre o contrato proposto e os guardrails atuais. Timeline pública (API, observada em 2026-10-17T17:31:00Z; 9 eventos): fechada por `luanmorenommaciel` em 2026-09-17; referências cruzadas na timeline retornada: #29, #41; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 32); [fechamento](https://github.com/luanmorenommaciel/apex/issues/32#issuecomment-5718031645); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_32.txt` (busca vazia por `validation_criteria`, arquivos da verify e `Coverage` em `1e0ba802049b4ebe8fb474a7853c604df2b93aeb`); branch conferida em `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_29.txt`.

### Classe e limite da evidência

DIRETO: proposta, fechamento, buscas negativas pelo literal nos dois SHAs e existência dos caminhos/classe citados. RELATADO: não implementação e substituição funcional. NÃO VERIFICADO: acordo contemporâneo do contrato e equivalência caso a caso.

### Fluxo

Fluxo proposto: event log → `validation_criteria` (pré-condições) → Watcher → `acceptance` → oráculo. Fluxo atual: telemetria → watcher (com guardas próprias) → serve com `Coverage` → verify com guardrails.

### Consequências e risco

A equivalência funcional dos guardrails atuais com os casos de uma task, mediana fria zero e operador divergente permanece não verificada. Não há incidente demonstrado. Busca textual negativa não prova ausência de qualquer mecanismo equivalente.

### Alternativas e recomendação

(a) Manter fechada e registrar a equivalência como não comprovada (recomendado); (b) estudo curto que mapeie cada critério do contrato para uma guarda atual ou uma lacuna — só leitura; (c) reabrir — o contrato foi desenhado para o slice YAML, que não existe na main.

### Dependências e paralelismo

Um eventual estudo (b) depende só de leitura do código atual. Não depende de #105, embora o contrato viva na branch arquivada.

### Plano e aceite propostos

Passo mínimo, se o mantenedor quiser: tabela critério × guarda atual, com controles negativos ("stage com uma task" e "tasks frias vazias") a serem testados no watcher de skew atual.

### Comunicação entre responsáveis

Para consolidação: #32 foi encerrada como substituída; a proposta não foi implementada segundo o mantenedor, e a equivalência dos casos com as guardas atuais não está demonstrada.

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — reimplementar o contrato YAML exigiria o slice que não está na main. (b) Que caso o teste ainda não cobre? — stage de join com uma única task e tasks frias vazias. (c) Como eu explicaria isso para outro pod? — "a ideia era barrar evidência ruim antes do watcher; hoje há guardas parecidas, sem prova de que cubram os mesmos casos". (d) Qual critério do contrato não tem guarda equivalente?

### Próxima ação e encerramento

Nenhuma obrigatória. Owner a confirmar: raia engine/verify, para o estudo (b). Encerramento: já fechada; reabrir só com caso real de evidência inválida aceita.

<a id="item-419"></a>

## #34 — [COMMANDER] Consolidar escopo Apex V0.1 da reuniao 2026-06-30

Frente: historico. Encaminhamento: historico_preservado_com_justificativa.

### Identidade e estado

Issue #34, Commander Attention (`phase:design`, `priority:p0`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-07-04; fechada em 2026-09-17T16:46:03Z por `luanmorenommaciel` como "implemented"; 1 comentário. É a mãe das tarefas #35–#43 de 2026-07-04, e o #26 a cita como o re-escopo que substituiu a discussão de maio.

### Intenção e benefício

Fixar uma V0.1 simples e demonstrável (decisão da reunião de 2026-06-30): Spark Env → SparkListener → ClickStack → CrewAI → MCP → usuário informa `job_id` e recebe diagnóstico. Fora do escopo: Databricks Serverless, clonar a UI do DataFlint, UI de DAG/replay, auto-aplicar mudanças e multi-agente antes de haver telemetria persistida.

### Feito, faltante e não comprovado

Fechamento relata implementação do escopo e aponta README, PIPELINE e SWIMLANES. Em 1e0ba80, a listagem confirma esses documentos e a busca localiza Quick start; #30 fornece a criação do SWIMLANES em 85de52d. Esse extrato não comprova o conteúdo integral das fronteiras ou um entregável único para o DoD.

### Linhagem

Reunião de 2026-06-30 → issue (2026-07-04) → filhas #35–#43 → SWIMLANES (2026-07-23) → v0.1.0 (2026-07-29) → fechamento. Elo ausente: o documento de escopo pedido no DoD; o fechamento aponta README, PIPELINE e SWIMLANES como equivalentes. Timeline pública (API, observada em 2026-10-17T17:31:02Z; 9 eventos): fechada por `luanmorenommaciel` em 2026-09-17; referências cruzadas na timeline retornada: #26, #55; eventos `referenced` com commit na timeline retornada: 79a23d2cd8.

### Fontes e corte

Snapshot (item 34); [fechamento](https://github.com/luanmorenommaciel/apex/issues/34#issuecomment-5718032132); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_34.txt` (`PIPELINE.md`, README e SWIMLANES em `1e0ba802049b4ebe8fb474a7853c604df2b93aeb`); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_30.txt` (data do SWIMLANES).

### Classe e limite da evidência

DIRETO: corpo, comentário de fechamento, existência dos documentos e seção Quick start. RELATADO: equivalência com a arquitetura entregue e reaprovação em 23/07. NÃO VERIFICADO: cobertura integral das fronteiras e uso do documento para dividir pods.

### Fluxo

Fluxo V0.1: Spark Env (`dev/`) → listener (`jar/`) → OTLP → ClickStack (`collect/` + `infra/`) → engine (watchers + gate + crew) → MCP (`serve/`) → cliente com `job_id`.

### Consequências e risco

Confiança alta no registro de escopo da issue e no fechamento; equivalência integral do DoD documental permanece não verificada. A lista de exclusões está no corpo; não se conclui que só exista ali.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) copiar a lista "fora de escopo" para a consolidação como restrição histórica; (c) reabrir — sem objeto.

### Dependências e paralelismo

Nenhuma dependência nova. As filhas têm fichas próprias (#35–#43).

### Plano e aceite propostos

Não ação. Documentação mínima opcional: citar a lista "fora de escopo" da V0.1 na consolidação, porque ela explica decisões posteriores (`applied=False` no MCP, UI sem DAG).

### Comunicação entre responsáveis

Para consolidação: #34 registra o escopo V0.1 e suas exclusões; o mantenedor o declara implementado e aponta documentos posteriores como referência.

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — perder a lista de exclusões abriria espaço para auto-aplicação sem aprovação. (b) Que caso o teste ainda não cobre? — o fluxo completo com `job_id` em máquina limpa. (c) Como eu explicaria isso para outro pod? — "a V0.1 é job_id entra, diagnóstico sai; o resto ficou para depois". (d) Qual documento hoje lista o que está fora da v1?

### Próxima ação e encerramento

Nenhuma ação obrigatória. Owner a confirmar: mantenedor, se quiser levar a lista de exclusões à consolidação. Entrada: corpo da issue. Saída: restrição histórica citada. Encerramento: já fechada; reabrir só se o fluxo V0.1 for redefinido.

<a id="item-420"></a>

## #35 — [TASK] Construir Spark Env reproduzivel para Apex V0.1

Frente: historico. Encaminhamento: concluida_com_evidencia_anexada.

### Identidade e estado

Issue #35, tarefa (`type:task`, `phase:build`, `priority:p0`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-07-04; fechada em 2026-08-20T18:22:12Z pelo próprio autor, logo após anexar evidência; 1 comentário.

### Intenção e benefício

Ter um Spark Env local pequeno, reaproveitando o trabalho de Philo/Gabriel, para rodar job de exemplo, gerar event logs e servir de onboarding.

### Feito, faltante e não comprovado

Feito, com evidência anexada: o comentário relata ambiente com `dev/docker-compose.yml` + `docker-compose.c3-otlp.yml` subido por `make bootstrap` (PR #76), o job `skew_join` com `exitCode 0` e 10 milhões de linhas, e `APEX_DOCTOR=ready spark=4.0.1 schema=3/3`. Conferi em `7c5460c` (main no fechamento): alvo `bootstrap:` em `Makefile:164`, `dev/docker-compose.c3-otlp.yml`, `dev/README.md` e `docs/lanes/DEV.md` existem; a PR #76 entrou em 2026-08-18, antes do fechamento. Relatado e não reproduzido: as saídas do job e do doctor.

### Linhagem

Tarefa (2026-07-04) → PR #76 (pacote operacional, integrada em 2026-08-18) → execução relatada → evidência e fechamento (2026-08-20). A PR #76 não usa `Closes #35`; o vínculo é o texto do comentário. Timeline pública (API, observada em 2026-10-17T17:31:02Z; 7 eventos): fechada por `gustocezar` em 2026-08-20; referências cruzadas na timeline retornada: nenhuma; eventos `referenced` com commit na timeline retornada: 79a23d2cd8.

### Fontes e corte

Snapshot (item 35); [evidência](https://github.com/luanmorenommaciel/apex/issues/35#issuecomment-5359985914); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_35.txt` (`Makefile`, compose, docs em `7c5460c87421d7f9493a664acb1cfbcc54259b51`; head da PR #76); `pulls_all.json` (datas da PR #76).

### Classe e limite da evidência

DIRETO: arquivos e alvo no SHA do fechamento; data de merge da PR #76. RELATADO: saídas `APEX_JOB` e `APEX_DOCTOR` de uma execução local. Não encontrei CI desse runtime nas fontes lidas.

### Fluxo

Fluxo de ambiente: `make bootstrap` → Compose de `dev/` + OTLP → `skew_join.py` → event logs e telemetria → `doctor` confirma prontidão.

### Consequências e risco

Baixo. O DoD pedia "evidência anexada", e há. Limite: execução única relatada, sem reprodução independente; a versão Spark relatada (4.0.1) é a da época.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) nenhuma alternativa útil.

### Dependências e paralelismo

Nenhuma pendente; a operação local do pacote evoluiu em #62 (fechada), #174 e #175.

### Plano e aceite propostos

Condição de não ação documental: o autor encerrou a tarefa com evidência textual no próprio objeto. Esta revisão não reproduziu job, event logs ou doctor. Uma validação operacional futura deve usar o pacote e ambiente então autorizados.

### Comunicação entre responsáveis

Para a consolidação: "#35 fechada com evidência local anexada".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — usar apenas presença de arquivos como prova de runtime confundiria implementação e execução. Que caso o teste ainda não cobre? — esta auditoria não observou cold start nem Windows nativo. Como eu explicaria isso para outro pod? — o autor anexou uma execução declarada com 10 milhões de linhas e doctor ready; arquivos do ambiente existem no SHA do fechamento.

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: já fechada com evidência anexada; reabrir só se o comando de bootstrap deixar de subir o ambiente descrito.

