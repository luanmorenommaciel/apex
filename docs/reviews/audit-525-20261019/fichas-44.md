# Fichas documentais — lote 44

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-431"></a>

## #59 — JDK gate for the Spark 4.x cells

Frente: historico. Encaminhamento: concluida_sem_codigo_novo_gate_preexistente.

### Identidade e estado

Issue #59, melhoria (`enhancement`, `pod-2-engine`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-08-06; fechada em 2026-09-17T16:46:21Z por `luanmorenommaciel` como "implemented"; 2 comentários.

### Intenção e benefício

Ter um gate que falhe rápido, com mensagem clara, quando a JVM em uso não atende ao mínimo das células Spark 4.x.

### Feito, faltante e não comprovado

Já existia: o comentário do autor (2026-08-16) diz que `scripts/find-jdk.sh` já estava na main, ligado a três alvos do Makefile, e que os dois caminhos de falha foram exercitados (`find-jdk.sh 999` → exit 1; `APEX_JDK_HOME` inválido → exit 1). Conferi em `1e0ba80`: `scripts/find-jdk.sh` existe; `Makefile:22` define `JDK_MIN := 17`; os alvos `test-jar` (105), `test-jar-cell` (112) e `jdk` (117) chamam o script. O arquivo foi adicionado em `0d310bd` (2026-07-29), antes da issue. Relatado: as duas execuções de falha. A linha "#59" em `docs/testing/LINEAGE.md` da branch `docs/pod-2-engine-testing-log` não está na main.

### Linhagem

Gate criado em `0d310bd` (2026-07-29) → issue (2026-08-06) → verificação do autor (2026-08-16) → fechamento (2026-09-17). Não encontrei PR ligada no snapshot; não era necessária. Timeline pública (API, observada em 2026-10-17T17:31:14Z; 9 eventos): fechada por `luanmorenommaciel` em 2026-09-17; referências cruzadas na timeline retornada: nenhuma; eventos `referenced` com commit na timeline retornada: 97f7607766.

### Fontes e corte

Snapshot (item 59); [verificação](https://github.com/luanmorenommaciel/apex/issues/59#issuecomment-5309840339); [fechamento](https://github.com/luanmorenommaciel/apex/issues/59#issuecomment-5718035843); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_59.txt` (script, Makefile e commit de criação).

### Classe e limite da evidência

DIRETO: script, alvos, constante e data de criação. RELATADO: os dois caminhos de falha executados. Não reexecutado aqui.

### Fluxo

Fluxo do gate: `make test-jar` → `find-jdk.sh 17` (prefere 21, depois 17; valida `APEX_JDK_HOME`) → caminho do JDK ou exit 1 com mensagem → `sbt -java-home`.

### Consequências e risco

Nenhum impacto: o gate existe. Limite: cobre os alvos do Makefile; quem chamar `sbt` direto não passa pelo gate.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) nenhuma alternativa necessária.

### Dependências e paralelismo

Nenhuma dependência: o gate é autocontido (script + Makefile) e não exige outra mudança; a ligação com o CI é questão separada.

### Plano e aceite propostos

Condição de não ação: o pedido já estava atendido antes da issue.

### Comunicação entre responsáveis

Para a consolidação: "#59 já estava resolvida por `find-jdk.sh` desde 2026-07-29".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — sem o gate, uma JVM 11 falharia tarde dentro das células 4.x com erro obscuro. (b) Que caso o teste ainda não cobre? — `sbt` chamado fora do Makefile. (c) Como eu explicaria isso para outro pod? — "o make procura um JDK 17+ e para com mensagem clara se não achar". (d) O CI usa o mesmo script?

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: já fechada; reabrir só se os alvos deixarem de chamar o script.

<a id="item-432"></a>

## #60 — Typed column for executor runtime

Frente: historico. Encaminhamento: concluida_por_pr_com_closes.

### Identidade e estado

Issue #60, melhoria (`enhancement`, `pod-2-engine`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-08-06; fechada em 2026-08-18T20:03:23Z, dois segundos depois do merge da PR #68 (`Closes`); 0 comentários.

### Intenção e benefício

Tipar o runtime de executor medido como coluna própria, em vez de só no mapa de atributos, para ganhar desempenho de consulta.

### Feito, faltante e não comprovado

Feito pela PR #68 ("typed columns for the telemetry fields the JAR now emits"). Conferi no merge `2a6a896e6`: `infra/sql/039_executor_runtime_additive.sql:6` faz `ADD COLUMN IF NOT EXISTS executor_run_time_ms Int64 DEFAULT 0`. A PR acrescenta seis migrações aditivas (034–039). O corpo citava um comportamento de tempo na criação de MVs; a camada de 2026-10-10 registra que ele foi reinterpretado no #71 como expiração por TTL de linhas sem `ts`. Esta coluna é a mesma que `predict.py` e `models.py` ainda dizem não existir (CL-02/#179).

### Linhagem

Issue (2026-08-06) → PR #68 com `Closes #60` → merge (2026-08-18) → consumidor #61/PR #70 → texto contraditório no Verify (#179, aberta). PR #74 também cita a issue. Timeline pública (API, observada em 2026-10-17T17:31:15Z; 12 eventos): fechada por `luanmorenommaciel` em 2026-08-18; referências cruzadas na timeline retornada: #61, PR#68, PR#74, #58, PR#70; eventos `referenced` com commit na timeline retornada: cf26b68d86.

### Fontes e corte

Snapshot (item 60); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_60.txt` (DDL em `2a6a896e6`); dossiê da PR #68; ficha #179 em `review-20261016-v2/C02-ISSUES-ABERTAS.md`.

### Classe e limite da evidência

DIRETO: DDL no merge, Closes e metadados da PR. RELATADO: aplicação das migrações em schema real; #179 relata texto interno obsoleto no corte c3c3ea3. DERIVADO: coluna disponível e narrativa desatualizada são estados relacionados; não se prova que esta PR introduziu um defeito posterior.

### Fluxo

Fluxo de schema: OTLP attribute `executor_run_time_ms` → MV → coluna tipada `executor_run_time_ms` (default 0) → leitores (engine; o Verify ainda não).

### Consequências e risco

A presença da coluna não garante valor útil ou equivalência com wall-clock. Default 0 em linha histórica exige seleção/fallback cuidadosos. A discrepância de texto e modelo tem destino de estudo em #179; não é regressão demonstrada desta migração.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) nenhuma alternativa; o resíduo pertence ao #179.

### Dependências e paralelismo

Nenhuma pendente aqui; o resíduo depende da DEC-N3 e do #179.

### Plano e aceite propostos

Condição de não ação nesta issue. O resíduo textual tem destino próprio (#179/CL-02).

### Comunicação entre responsáveis

Para a consolidação: "#60 entregue pela PR #68; a coluna existe, e o Verify ainda diz que não".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — sem coluna tipada, todo leitor faria parsing do mapa de atributos. (b) Que caso o teste ainda não cobre? — linha antiga com default 0 lida como medição. (c) Como eu explicaria isso para outro pod? — "o runtime medido tem coluna própria desde agosto". (d) Quem atualiza o texto do Verify?

### Próxima ação e encerramento

Nenhuma ação aqui. Owner do resíduo: quem decidir a DEC-N3. Encerramento: já fechada.

<a id="item-433"></a>

## #61 — Engine consuming the typed runtime column

Frente: historico. Encaminhamento: concluida_por_pr_com_closes.

### Identidade e estado

Issue #61, melhoria (`enhancement`, `pod-2-engine`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-08-06; fechada em 2026-08-18T20:04:51Z, um segundo depois do merge da PR #70 (`Closes`); 0 comentários.

### Intenção e benefício

Fazer o engine ler a coluna tipada de runtime em vez do mapa de atributos, depois do #60.

### Feito, faltante e não comprovado

Feito pela PR #70 ("read the typed executor runtime column, Map as fallback"). Conferi no merge `2195d4012`: `engine/src/apex_engine/clickhouse.py:70-72` e `watchers/memory.py:41-42` usam `argMax(if(executor_run_time_ms > 0, executor_run_time_ms, toInt64OrZero(attributes['executor_run_time_ms'])), ts)`, ou seja, coluna com fallback para o mapa. A PR inclui `engine/tests/test_integration_clickhouse.py` (+63). Não executado aqui.

### Linhagem

Issue (2026-08-06, dependente do #60) → PR #68 (coluna) → PR #70 com `Closes #61` → merge e fechamento (2026-08-18). Timeline pública (API, observada em 2026-10-17T17:31:17Z; 12 eventos): fechada por `luanmorenommaciel` em 2026-08-18; referências cruzadas na timeline retornada: PR#70, PR#74, #71, #60, #58; eventos `referenced` com commit na timeline retornada: cf26b68d86.

### Fontes e corte

Snapshot (item 61); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_61.txt` (consultas em `2195d4012`); dossiê da PR #70.

### Classe e limite da evidência

DIRETO: SQL com fallback e teste de integração adicionado. RELATADO: nada além do corpo. Não verificado: execução do teste de integração.

### Fluxo

Fluxo de leitura: `spark_events.executor_run_time_ms` > 0 → usa a coluna; senão → `attributes['executor_run_time_ms']` → `argMax` por `ts`.

### Consequências e risco

O fallback preserva leituras históricas com coluna default 0 e valor no mapa. Uma coluna legítima 0 também cai no mapa, que pode divergir; a consulta não prova que esse caso sempre preserve a medição correta. Não foram executados testes nesta revisão.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) nenhuma alternativa necessária.

### Dependências e paralelismo

Nenhuma dependência pendente: a coluna veio do #60 (PR #68) no mesmo dia; o texto contraditório do Verify é assunto do #179.

### Plano e aceite propostos

Condição explícita de não ação: entregue com fallback para dados antigos e teste de integração adicionado; nada a acrescentar nesta issue.

### Comunicação entre responsáveis

Para a consolidação: "#61 entregue pela PR #70, com fallback para dados antigos".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — ler só a coluna zeraria o runtime de eventos anteriores à migração. (b) Que caso o teste ainda não cobre? — evento com coluna e mapa divergentes. (c) Como eu explicaria isso para outro pod? — "o engine prefere a coluna e cai no mapa se ela estiver vazia". (d) O Verify deveria usar a mesma regra?

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: já fechada; reabrir só se o engine voltar a ler apenas o mapa de atributos ou perder o fallback.

<a id="item-434"></a>

## #62 — Local operational package (bootstrap/doctor/smoke)

Frente: historico. Encaminhamento: concluida_por_pr_com_closes_e_lacuna_registrada.

### Identidade e estado

Issue #62, melhoria (`enhancement`, `pod-2-engine`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-08-06; fechada em 2026-08-18T20:06:03Z, um segundo depois do merge da PR #76 (`Closes`); 3 comentários de escopo e execução.

### Intenção e benefício

Trazer comandos operacionais locais (bootstrap, doctor, smoke) para subir e verificar o ambiente.

### Feito, faltante e não comprovado

Feito pela PR #76 ("local operational package (bootstrap/doctor/smoke/e2e/status/down)"), com `Makefile` (+52), `scripts/apex.ps1` (+772), `scripts/apex.sh` (+101) e `dev/docker-compose.package.yml` (+21). Os comentários registram: Makefiles disjuntos (operador × verificação); dependência de `infra/scripts/apply_schema_migrations.ps1` trocada por `infra/scripts/apply_ddl.sh` (o primeiro não existe na main; o segundo existe, conferido no dossiê); 8 bootstraps reais com 4 correções (hyperdx/mongodb, corrida de porta do ClickHouse, credencial MinIO). Relatado: `APEX_DOCTOR=ready spark=4.0.1 schema=3/3`. Os problemas posteriores do pacote (sobrescrita de `dev/.env`, ownership de stack) estão em #174 e #175, abertas.

### Linhagem

Issue (2026-08-06) → análise de escopo (2026-08-06, 2026-08-11) → port e testes (2026-08-13) → PR #76 com `Closes #62` → merge (2026-08-18). #174 e #176 citam a issue. Timeline pública (API, observada em 2026-10-17T17:31:18Z; 15 eventos): fechada por `luanmorenommaciel` em 2026-08-18; referências cruzadas na timeline retornada: PR#76, PR#68, #64, #174, #176; eventos `referenced` com commit na timeline retornada: f59c8d9c0b.

### Fontes e corte

Snapshot (item 62); [escopo](https://github.com/luanmorenommaciel/apex/issues/62#issuecomment-5208130722), [dependências](https://github.com/luanmorenommaciel/apex/issues/62#issuecomment-5252914568), [execução](https://github.com/luanmorenommaciel/apex/issues/62#issuecomment-5274203501); dossiê da PR #76 (4 arquivos).

### Classe e limite da evidência

DIRETO: arquivos da PR e existência dos caminhos citados. RELATADO: oito bootstraps e smoke reais, correções feitas. Não reproduzido aqui.

### Fluxo

Fluxo declarado: make bootstrap → scripts/apex.ps1; em macOS, scripts/apex.sh atua como dispatcher para o mesmo PowerShell → Compose e apply_ddl.sh → doctor; smoke invoca o gate de patologia.

### Consequências e risco

O pacote foi integrado e o autor declarou bootstrap/doctor/smoke executados. Ele explicitou que e2e, pilot-clean e install não foram exercitados. #174/#175 registram riscos posteriores; isso não certifica cumprimento integral de toda operação local nem permite atribuir causalidade além do código identificado.

### Alternativas e recomendação

(a) Manter fechada e apontar #174/#175 como resíduo do pacote (recomendado); (b) reabrir — duplicaria #174/#175.

### Dependências e paralelismo

Os resíduos dependem de DEC-10 e DEC-15 (publicação do CL-01).

### Plano e aceite propostos

Condição de não ação nesta issue; os resíduos têm destino em #174/#175.

### Comunicação entre responsáveis

Para a consolidação: "#62 entregue pela PR #76; os defeitos do pacote seguem em #174/#175".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — trazer o orquestrador de 700+ linhas dentro de uma PR de lógica misturaria revisões, como o autor alertou. (b) Que caso o teste ainda não cobre? — bootstrap em checkout compartilhado com `dev/.env` local. (c) Como eu explicaria isso para outro pod? — "um comando sobe tudo; os problemas que surgiram depois estão em #174/#175". (d) O smoke atual cobre o caminho tail-outlier?

### Próxima ação e encerramento

Nenhuma ação aqui. Owner dos resíduos: dono do pacote (DEC-10). Encerramento: já fechada.

<a id="item-435"></a>

## #63 — Data integrity in the Collector under retry

Frente: historico. Encaminhamento: concluida_por_pr_com_closes_e_residuo_estatico.

### Identidade e estado

Issue #63, bug (`bug`, `pod-2-engine`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-08-06; fechada em 2026-08-18T20:02:39Z, um segundo depois do merge da PR #67 (`Closes`); 0 comentários.

### Intenção e benefício

Evitar duplicação de dados quando o Collector reenviasse um lote após timeout, o que inflaria agregados.

### Feito, faltante e não comprovado

Feito pela PR #67 ("switch Collector to synchronous inserts, fix retry duplication"). Conferi: `infra/sql/033_dedup_window_additive.sql` aplica `non_replicated_deduplication_window = 100` em `otel_traces`, `spark_events`, `plan_transitions` e `spark_jobs_1m`; o endpoint do collector de `infra/` usa `async_insert=0&deduplicate_blocks_in_dependent_materialized_views=1`; o collector de `collect/` recebe o mesmo endpoint por `CLICKHOUSE_ENDPOINT` nos dois Compose (main `c3c3ea3`). Resíduo estático: `collect/ddl/10_otel_traces.sql` (DDL da raia collect isolada) cria `otel_traces` sem a janela de deduplicação, e não há equivalente da migração 033 nessa raia. O pacote padrão usa o ClickHouse de `infra/` (overlay `c3-infra`), onde a 033 se aplica. Relatado no corpo: testes com retry, lote e concorrência reais.

### Linhagem

Issue (2026-08-06) → PR #67 com `Closes #63` → merge (2026-08-18). Elo ausente: a mesma janela no DDL da raia collect. Timeline pública (API, observada em 2026-10-17T17:31:19Z; 7 eventos): fechada por `luanmorenommaciel` em 2026-08-18; referências cruzadas na timeline retornada: PR#67; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 63); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_63.txt` (migração 033, endpoints dos dois collectors, DDLs de `otel_traces` em `infra/` e `collect/`).

### Classe e limite da evidência

DIRETO: configurações e DDLs. RELATADO: quatro cenários de teste. INFERÊNCIA: na raia collect isolada, um reenvio pode duplicar linhas de `otel_traces` (o `spark_events` dessa raia tem a janela). Não demonstrado em execução.

### Fluxo

Fluxo configurado: inserts síncronos e deduplicação em MVs dependentes; janela de 100 blocos nas quatro tabelas da migração infra. A intenção é descartar reenvio do mesmo bloco dentro da janela. Blocos reagrupados ou reenvios fora da janela não estão certificados por esses settings.

### Consequências e risco

Há resíduo estático no DDL collect isolado e relato de cenários testados. A revisão não demonstrou duplicação nessa raia nem imunidade universal no pacote padrão; a proteção é delimitada por identidade do bloco, settings e janela.

### Alternativas e recomendação

(a) Manter fechada e registrar o resíduo da raia collect (recomendado); (b) acrescentar a janela ao `collect/ddl/10_otel_traces.sql` — mudança pequena, exige PR própria; (c) reabrir — desproporcional.

### Dependências e paralelismo

A opção (b) não depende de nada; poderia andar em paralelo, como follow-up de baixo risco.

### Plano e aceite propostos

Passo mínimo se o mantenedor quiser: PR com a janela no DDL da raia collect e um teste estático que compare os `SETTINGS` dos dois DDLs de `otel_traces`. Controle discriminante: o teste deve falhar no DDL atual.

### Comunicação entre responsáveis

Para a consolidação: "#63 entregue pela PR #67; a raia collect isolada não tem a janela em `otel_traces`".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — o comentário de configuração registra incompatibilidade de async_insert=1 com o setting em ClickHouse 24.8. Que caso o teste ainda não cobre? — retry na raia collect isolada, reagrupamento ou reenvio após a janela não foram observados nesta auditoria. Como eu explicaria isso para outro pod? — o desenho protege reenvio do mesmo bloco dentro de uma janela configurada; não é deduplicação universal por conteúdo de linha.

### Próxima ação e encerramento

Owner a confirmar: Pod 2, para a decisão sobre o DDL da raia collect. Entrada: este registro. Saída: PR ou registro de não ação. Encerramento: a issue segue fechada; reabrir só com duplicação observada.

<a id="item-436"></a>

## #64 — Clean Docker environment guard-rail

Frente: historico. Encaminhamento: concluida_por_pr_com_closes_guarda_nao_ligada_ao_bootstrap.

### Identidade e estado

Issue #64, melhoria (`enhancement`, `pod-2-engine`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-08-06; fechada em 2026-08-18T20:02:47Z, um segundo depois do merge da PR #69 (`Closes`); 0 comentários.

### Intenção e benefício

Detectar recursos Docker preexistentes antes de operações de setup e recusar, em vez de limpar automaticamente, motivado por um incidente real em testes locais.

### Feito, faltante e não comprovado

Feito como script avulso pela PR #69: `scripts/assert_clean_docker_env.ps1` (+86) inventaria contêineres, redes e volumes, "REFUSES to proceed … never removes anything" e sai com 1 (`APEX_CLEAN_DOCKER=refused`). Conferi na main `c3c3ea3`: nenhum arquivo além do próprio script o referencia. O `bootstrap` (`Start-Package`, linha 506 de `apex.ps1`) não o chama. A recusa por resíduos existe no `apex.ps1` só para `pilot-clean` (`Assert-CleanPilotEnvironment`, linhas 292–297, que lança erro sem remover nada). Relatado no corpo: recusa correta e mutação zero em teste ao vivo.

### Linhagem

Incidente local → issue (2026-08-06) → PR #69 com `Closes #64` → merge (2026-08-18). Elo ausente: a ligação da guarda ao fluxo de setup padrão. #175 (ownership de stack, aberta) cita a issue. Timeline pública (API, observada em 2026-10-17T17:31:21Z; 10 eventos): fechada por `luanmorenommaciel` em 2026-08-18; referências cruzadas na timeline retornada: PR#69, #62, PR#70, #175; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 64); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_64.txt` (script em `046e2cb1d`, busca de referências e trechos de `apex.ps1` na main).

### Classe e limite da evidência

DIRETO: script, ausência de chamada no bootstrap, guarda do `pilot-clean`. RELATADO: teste ao vivo de recusa. INFERÊNCIA: a proteção no bootstrap depende de alguém rodar o script à mão.

### Fluxo

Fluxos: (avulso) `pwsh scripts/assert_clean_docker_env.ps1` → inventário → recusa ou passa; (pacote) `pilot-clean` → `Assert-CleanPilotEnvironment` → recusa sem remover; `bootstrap` → sem checagem de resíduos.

### Consequências e risco

Médio para operação local: o problema que motivou a issue (setup sobre recursos preexistentes) pode se repetir no `bootstrap`. Isso se liga ao #175 (identidade e ownership da stack). Não há incidente novo registrado.

### Alternativas e recomendação

(a) Manter fechada e registrar que a guarda não está ligada ao bootstrap (recomendado); (b) chamar a guarda no início de `Start-Package` — muda comportamento e precisa da decisão de ownership (#175); (c) remover o script avulso — perderia a ferramenta.

### Dependências e paralelismo

A opção (b) depende de DEC-10/#175, porque recusar resíduos colide com o caso "subir de novo a própria stack".

### Plano e aceite propostos

Passo mínimo documental: registrar no #175 que existem duas guardas (script avulso e `pilot-clean`) e nenhuma no bootstrap. Se ligada: controle negativo com stack própria anterior, que não pode ser recusada indevidamente.

### Comunicação entre responsáveis

Para a consolidação: "#64 entregou uma guarda que o bootstrap não chama (busca na main de referência)".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — ligar a guarda sem regra de ownership impediria reiniciar a própria stack. (b) Que caso o teste ainda não cobre? — bootstrap com recursos de outra pessoa na mesma máquina. (c) Como eu explicaria isso para outro pod? — "existe um script que recusa ambiente sujo, mas o bootstrap não o usa". (d) O incidente original aconteceria hoje com `make bootstrap`?

### Próxima ação e encerramento

Owner a confirmar: dono do pacote, junto ao #175. Entrada: este registro. Saída: decisão de ligar ou não a guarda. Encerramento: a issue segue fechada; o resíduo vai para o #175.

<a id="item-437"></a>

## #65 — Design decision: AQE re-plan detection logic

Frente: historico. Encaminhamento: decidida_e_implementada_com_follow_up_cumprido.

### Identidade e estado

Issue #65, decisão (Commander Attention, `pod-2-engine`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-08-06; fechada em 2026-09-17T16:46:23Z por `luanmorenommaciel` como "decided"; 2 comentários.

### Intenção e benefício

Escolher entre duas abordagens incompatíveis na mesma função de detecção de re-plano do AQE (contagem precisa de partições com skew × correção do alinhamento de joins sob inserção/remoção) ou um candidato combinado. Decisão de time, não só técnica.

### Feito, faltante e não comprovado

Decisão explícita na review APPROVED de 14/09 da PR #98 escolhe opção 3 e supera proposta separada #93. Specs e ADR existem no recorte. Status proposed em 1e0ba80 (14/09) e accepted em c3c3ea3 (08/10) corroboram atualização entre os cortes; não se trata do mesmo dia do fechamento em 17/09. 34/34 e 0,72 ms/100 joins são medições relatadas pelo autor.

### Linhagem

Issue (2026-08-06) → evidência do autor com status DECIDE (2026-08-16) → PR #93 (fechada sem merge, cita `closes`) → PR #98 (aprovada e integrada em 2026-09-14) → fechamento (2026-09-17) → status do ADR atualizado depois. Timeline pública (API, observada em 2026-10-17T17:31:22Z; 12 eventos): fechada por `luanmorenommaciel` em 2026-09-17; referências cruzadas na timeline retornada: PR#66, PR#93, PR#98; eventos `referenced` com commit na timeline retornada: 97f7607766, 5f5311b063.

### Fontes e corte

Snapshot (item 65); [evidência](https://github.com/luanmorenommaciel/apex/issues/65#issuecomment-5309840436), [fechamento](https://github.com/luanmorenommaciel/apex/issues/65#issuecomment-5718036247); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_65.txt` (status do ADR nos dois SHAs, specs); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/pr98-reviews.json`.

### Classe e limite da evidência

DIRETO: reviews da PR #98, arquivos, status do ADR. RELATADO: 34/34 testes e medições de custo. DECISÃO: registrada como aprovação de PR e no ADR, não como comentário da issue.

### Fluxo

Fluxo de detecção: eventos de plano do AQE → alinhamento por edição entre plano anterior e novo → contagem acumulada de partições com skew → `plan_transitions`.

### Consequências e risco

Baixo. Limite registrado pelo autor: não houve trace de produção com mais de ~100 joins; o custo acima disso foi extrapolado.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) nenhuma alternativa: a decisão foi tomada e documentada.

### Dependências e paralelismo

Nenhuma dependência pendente: a PR #98 foi integrada e o status do ADR-003 foi atualizado na main (conferido nos dois SHAs).

### Plano e aceite propostos

Condição de não ação: decisão, implementação e documentação estão na main.

### Comunicação entre responsáveis

Para a consolidação: "#65 decidida pela aprovação da PR #98; o ADR-003 canônico já diz accepted".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — sem alinhamento por edição, inserção/remoção de join pode produzir transições desalinhadas, conforme o estudo relatado. Que caso o teste ainda não cobre? — não havia trace de produção acima de cerca de 100 joins; extrapolação além da escala sintética não é observação real. Como eu explicaria isso para outro pod? — Commander aprovou o detector combinado na PR #98; custos publicados pertencem às medições e escalas relatadas.

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: já fechada; reabrir só com plano real em que o alinhamento custe caro.

<a id="item-438"></a>

## #71 — mv_spark_events does not reliably propagate inserts (pre-existing, independent of #66-#68/#61)

Frente: historico. Encaminhamento: nao_e_defeito_retratado_pelo_autor.

### Identidade e estado

Issue #71, investigação (`pod-2-engine`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-08-06; fechada em 2026-08-22T02:46:57Z pelo próprio autor como "not a bug", com motivo `completed`; 6 comentários. Ligada ao registro DD08.

### Intenção e benefício

Relatar que `mv_spark_events` (em `infra/sql/020_mv_reshape.sql`) não propagaria de forma confiável inserts de `otel_traces` para `spark_events`, independentemente das PRs de telemetria abertas na época.

### Feito, faltante e não comprovado

Retratado pelo próprio autor, em quatro etapas registradas nos comentários: (1) bissecção sem peça isolada que falhasse; (2) 10 iterações com 8/10 propagadas; (3) busca de bug upstream sem correspondência; (4) em 2026-08-11, a explicação certa: os inserts de teste não tinham `SpanAttributes['ts']`, a MV materializava `ts = 1970-01-01`, e o TTL de 90 dias apagava as linhas na janela de leitura. Fechamento: 40/40 inserts com `ts` real propagaram; 51/51 sem `ts`, com merges parados, permaneceram. Conferi em `7c5460c`: `infra/sql/002_spark_events.sql:53` tem `TTL toDateTime(ts) + INTERVAL 90 DAY`, e as linhas 8–9 já avisam que linhas de fixture com `ts` congelado expiram no merge. Os scripts citados (`test71_ts_hypothesis.sh`, `METHODOLOGY.md`) existem só na branch `docs/pod-2-engine-testing-log` (`97f7607`).

### Linhagem

Relato (2026-08-06) → bissecção → forense com 10 iterações → busca upstream → retratação (2026-08-11) → brief REVIEW (2026-08-16) → fechamento (2026-08-22). A PR #75 cita a issue (guarda de ordem de MV, assunto do #72). Elo opcional sugerido e não feito: exigir `ts` válido em fixtures OTLP sintéticas. Timeline pública (API, observada em 2026-10-17T17:31:23Z; 13 eventos): fechada por `gustocezar` em 2026-08-22; referências cruzadas na timeline retornada: #72, PR#75, #60; eventos `referenced` com commit na timeline retornada: 97f7607766.

### Fontes e corte

Snapshot (item 71) com os seis comentários, em especial a [retratação](https://github.com/luanmorenommaciel/apex/issues/71#issuecomment-5248332655) e o [fechamento](https://github.com/luanmorenommaciel/apex/issues/71#issuecomment-5377449873); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_71.txt` (TTL e aviso no DDL; arquivos da branch de testes).

### Classe e limite da evidência

DIRETO: retratação, fechamento, TTL e aviso de fixtures nos extratos. RELATADO: contagens e confirmação de que spans JAR emitem ts. A conclusão específica do autor é que o achado inicial era artefato de teste; nenhuma conclusão universal sobre produção foi verificada nesta revisão.

### Fluxo

Fluxo do engano: insert sem `ts` → MV calcula `ts = 0` → linha em `spark_events` já expirada → merge em segundo plano apaga → leitura posterior vê 0 linhas e parece perda de propagação.

### Consequências e risco

O achado inicial foi retirado pelo autor, com testes e mecanismo TTL publicados. Não há incidente de produção demonstrado nas fontes desta ficha; isso não prova ausência universal de impacto. Fixtures sem ts válido continuam um risco metodológico.

### Alternativas e recomendação

(a) Manter fechada como não defeito (recomendado); (b) fazer o follow-up opcional: validar `ts` em fixtures sintéticas; (c) reabrir — contraria a evidência.

### Dependências e paralelismo

O follow-up (b) não depende de nada e seria uma checagem de teste pequena; não há dependência de produto.

### Plano e aceite propostos

Passo mínimo opcional: asserção de teste que rejeite fixture OTLP sem `SpanAttributes['ts']` ou com `ts` mais antigo que o TTL. Controle discriminante: a fixture usada no relato original deve falhar nessa asserção.

### Comunicação entre responsáveis

Para a consolidação: "#71 foi retratada pelo autor: era TTL em dados de teste sem ts, não perda na MV".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — tratar a primeira conclusão como final levaria a reescrever uma MV correta. (b) Que caso o teste ainda não cobre? — fixture sintética sem `ts` em testes de integração. (c) Como eu explicaria isso para outro pod? — "a MV funcionava; os dados de teste nasciam vencidos". (d) Onde fica a regra de que toda fixture precisa de `ts`?

### Próxima ação e encerramento

Owner a confirmar: Pod 2, se quiser o follow-up de fixtures. Entrada: este registro. Saída: asserção de teste ou decisão de não fazer. Encerramento: a issue segue fechada; reabrir só com perda observada em tráfego com `ts` válido.

<a id="item-439"></a>

## #72 — MV creation succeeds against a missing target table, then rejects every insert (bootstrap ordering risk)

Frente: historico. Encaminhamento: concluida_por_pr_com_closes.

### Identidade e estado

Issue #72, risco de bootstrap (`pod-2-engine`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-08-07; fechada em 2026-08-18T20:02:43Z, um segundo depois do merge da PR #75 (`Closes`); 0 comentários. Ligada ao registro E21.

### Intenção e benefício

Registrar que o ClickHouse 24.8 aceita `CREATE MATERIALIZED VIEW ... TO <tabela inexistente>` sem erro e depois rejeita todo insert na tabela de origem, um risco de ordem de bootstrap diferente do #71.

### Feito, faltante e não comprovado

PR #75 introduziu no apply_ddl.sh uma verificação após cada arquivo para alvos de MV que o extrator reconhecia. O código fornecido usa grep por linha: não reconhece CREATE MATERIALIZED VIEW e TO em linhas separadas. PR #147 registra e corrige esse limite depois; execução Code 60 e testes de correção são relatos das respectivas fontes.

### Linhagem

Achado ao reverificar o #71 (2026-08-07) → issue → PR #75 com `Closes #72` → merge (2026-08-18). Timeline pública (API, observada em 2026-10-17T17:31:24Z; 7 eventos): fechada por `luanmorenommaciel` em 2026-08-18; referências cruzadas na timeline retornada: PR#75, #71, #60; eventos `referenced` com commit na timeline retornada: b643a9e481.

### Fontes e corte

Snapshot (item 72); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_72.txt` (`apply_ddl.sh` em `f020f9a97`); dossiê da PR #75.

### Classe e limite da evidência

DIRETO: guarda no script. RELATADO: reprodução do erro. INFERÊNCIA: a guarda cobre o caminho `apply_ddl.sh`; o init do contêiner (`docker-entrypoint-initdb.d`) aplica os arquivos em ordem numérica, onde o risco depende da numeração.

### Fluxo

Fluxo original: aplica SQL → extrai padrões MV/TO da mesma linha → EXISTS TABLE → falha se alvo reconhecido faltar. A PR #147 passa a remover comentários e unir linhas antes da extração, sem constituir parser SQL geral.

### Consequências e risco

A entrega original reduz risco para a sintaxe coberta, sem checar todo alvo multiline. No corte posterior há correção #147 para a sintaxe atual; aplicações manuais continuam fora desse mecanismo e nenhum runtime foi reexecutado.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) nenhuma alternativa necessária.

### Dependências e paralelismo

Nenhuma pendente. Relacionada à política de reaplicação de DDL do #170 (aberta), que trata o alcance do `verify-ddl`.

### Plano e aceite propostos

Condição de não ação: entregue com guarda no ponto de aplicação.

### Comunicação entre responsáveis

Para consolidação: #72 foi encerrada pela PR #75; sua guarda original tinha limite multiline, tratado posteriormente pela PR #147.

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — sem a guarda, um bootstrap parcial pareceria sucesso até a ingestão parar inteira. (b) Que caso o teste ainda não cobre? — DDL aplicado à mão sem o script. (c) Como eu explicaria isso para outro pod? — "criar a MV antes da tabela não dá erro; o script agora confere". (d) O #170 deveria incorporar essa checagem ao verify-ddl?

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: já fechada; reabrir só se a guarda sair de `apply_ddl.sh`.

<a id="item-440"></a>

## #73 — Real-pathology test tooling for dev/ + design docs for merged telemetry fields

Frente: historico. Encaminhamento: concluida_por_pr_com_closes_bloqueio_resolvido.

### Identidade e estado

Issue #73, proposta de ferramental (`pod-2-engine`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-08-09; fechada em 2026-08-18T20:06:00Z, dois segundos depois do merge da PR #74 (`Closes`); 1 comentário. O #113 (protocolo de overhead) a cita.

### Intenção e benefício

Trazer ferramental de patologias reais para `dev/` (4 probes: `fetch_failed_probe`, `retry_speculation`, `tail_outlier`, `listener_soak`; scripts de evento, credenciais e overhead) e documentos de desenho que expliquem campos de telemetria já integrados.

### Feito, faltante e não comprovado

Feito pela PR #74 (17 arquivos: os 4 probes, 7 scripts em `dev/scripts/`, `dev/.gitignore` (+5), `dev/secrets/README.md`, +12 no `dev/docker-compose.yml` e três documentos de arquitetura, entre eles `ADR-001-TAIL-OUTLIER-SKEW-SIGNAL.md` e `ADR-002-SUCCESSFUL-TASK-SAMPLE-CONTRACT.md`, que viraram os ADR-001/002 canônicos do índice). O bloqueio relatado em 2026-08-10 (três orquestradores falhavam porque `with-s3-credentials.sh` esperava segredos em arquivo, e o Compose da main não os provia) foi resolvido pela opção 1: conferi no merge `e289e18ae` um bloco `secrets:` com `apex_s3_access_key`/`apex_s3_secret_key` (linhas 7–11) montado em dois serviços (109–111, 133–135). Relatado: `phase_a_eventlog_report.py` e `verify_s3_runtime_evidence.py` passaram contra event log real, sem vazamento de credencial.

### Linhagem

Proposta (2026-08-09) → execução dos 5 itens não executados (2026-08-10, 2 passam, 3 falham pela mesma causa) → PR #74 com segredos no Compose e `Closes #73` → merge (2026-08-18). O `r9d_overhead_ab.py` dessa PR é a base local do número de overhead discutido no #113. Timeline pública (API, observada em 2026-10-17T17:31:26Z; 7 eventos): fechada por `luanmorenommaciel` em 2026-08-18; referências cruzadas na timeline retornada: PR#74, #113, #58; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 73); [execução e bloqueio](https://github.com/luanmorenommaciel/apex/issues/73#issuecomment-5235528175); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_73.txt` (bloco de segredos e wrapper em `e289e18ae`); dossiê da PR #74.

### Classe e limite da evidência

DIRETO: arquivos da PR, bloco de segredos, wrapper com saída 78. RELATADO: execuções reais de dois scripts e falha dos outros três antes da correção. NÃO VERIFICADO: a execução dos três orquestradores depois da correção (não registrada nesta issue).

### Fluxo

Fluxo de credencial: arquivos em `dev/secrets/` → segredos do Compose em `/run/secrets/` → `with-s3-credentials.sh` exporta `AWS_*` → `spark-submit` dos probes.

### Consequências e risco

Baixo. O cuidado com credenciais é explícito (wrapper recusa com saída 78; verificação de que o event log não expõe chaves). Limite: depois da correção, não encontrei registro de execução dos três orquestradores nas fontes lidas.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) registrar uma execução dos três orquestradores, se forem usados como prova (por exemplo pelo #113).

### Dependências e paralelismo

O uso do `r9d_overhead_ab.py` como prova depende do protocolo do #113.

### Plano e aceite propostos

Condição de não ação nesta issue. Se o #113 for retomado, o primeiro passo é executar `r9d_e2e_canonical_noplugin.ps1` com os segredos atuais e anexar o recibo.

### Comunicação entre responsáveis

Para consolidação: #73 foi entregue pela PR #74 com ajuste estático de segredos no Compose; reexecução dos três orquestradores após esse ajuste não está demonstrada nesta ficha.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — passar valores secretos na linha de comando pode expô-los em histórico, processos ou logs; o wrapper usa arquivos. Que caso o teste ainda não cobre? — nesta ficha não há recibo dos três orquestradores após o ajuste do Compose. Como eu explicaria isso para outro pod? — há probes e um wrapper que recusa segredo ausente; o mount foi corrigido, mas isso não substitui execução posterior dos orquestradores.

### Próxima ação e encerramento

Nenhuma ação obrigatória. Owner a confirmar: quem retomar o #113. Encerramento: já fechada.

