# Fichas documentais — lote 45

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-441"></a>

## #78 — Proposal: canonical end-to-end traceability ledger across APEX lanes

Frente: historico. Encaminhamento: proposta_encerrada_nao_planejada.

### Identidade e estado

Issue #78, proposta (sem rótulos); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-08-16T02:41:08Z e fechada 4 minutos depois pelo próprio autor com `state_reason=not_planned`; 1 comentário. Única issue deste recorte fechada como `not_planned`. Citada por #63, #115 e #180.

### Intenção e benefício

Propor rastreabilidade canônica ponta a ponta por evento: chaves lógicas por família (stage, AQE, task), landing bruto imutável e visão canônica, para responder em que fronteira um evento se perdeu (JAR, collector, landing, visão, engine, finding, serve). Não alegava perda de dados.

### Feito, faltante e não comprovado

Não planejada: o autor fechou dizendo que a main já tinha o overlay C3, o gate canônico de seis raias e correlação por job/app/stage, e que só reabriria com evidência reproduzível de lacuna (contagem por fronteira, rastreio reverso ou conflito de payload). Nenhuma implementação. A ideia reaparece no #180 (matriz de proveniência, aberta), que a cita.

### Linhagem

Proposta (2026-08-16 02:41) → revisão da main pelo autor → fechamento (02:45) → retomada parcial no #180. Elo ausente: a validação local de lacuna que o fechamento prometia. Timeline pública (API, observada em 2026-10-17T17:31:27Z; 5 eventos): fechada por `gustocezar` em 2026-08-16; referências cruzadas na timeline retornada: #115, #63, #180; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 78); [fechamento](https://github.com/luanmorenommaciel/apex/issues/78#issuecomment-5305388013); main no fechamento `50d596e16`.

### Classe e limite da evidência

DIRETO: datas, motivo `not_planned`, texto. RELATADO: existência de overlay C3, gate canônico e correlação (não conferidos item a item aqui). PROPOSTA: o ledger em si.

### Fluxo

Fluxo proposto: evento → chave lógica → landing (tudo, inclusive duplicatas) → visão canônica (uma ocorrência por chave) → contagem por fronteira → primeiro ponto divergente.

### Consequências e risco

Nenhum impacto: proposta não executada. O valor está na pergunta (onde um evento se perde), que o #180 retoma.

### Alternativas e recomendação

(a) Manter fechada como não planejada (recomendado); (b) levar as chaves lógicas propostas como insumo para o #180; (c) reabrir — o próprio autor condicionou a evidência.

### Dependências e paralelismo

Qualquer retomada depende de evidência reproduzível de lacuna, como o autor definiu, e da decisão do #180.

### Plano e aceite propostos

Condição explícita de não ação: reabrir só com contagem por fronteira mostrando divergência.

### Comunicação entre responsáveis

Para a consolidação: "#78 foi retirada pelo autor; a ideia segue como insumo do #180".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — implementar o ledger exigiria justificar custo, retenção e utilidade antes de ampliar armazenamento; ausência de lacuna demonstrada não prova ausência de uso possível. Que caso o teste ainda não cobre? — as contagens e o rastreio reverso por fronteira não foram executados nesta revisão. Como eu explicaria isso para outro pod? — o autor retirou a proposta por enquanto e condicionou retomada a evidência reproduzível.

### Próxima ação e encerramento

Nenhuma ação. Owner a confirmar: dono do #180, se quiser reaproveitar as chaves. Encerramento definitivo; reabrir só com evidência de lacuna.

<a id="item-442"></a>

## #90 — Design question: should skew_ratio route through the retry-safe fields?

Frente: historico. Encaminhamento: decidida_e_implementada_por_pr_aprovada.

### Identidade e estado

Issue #90, pergunta de desenho (`pod-2-engine`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-08-20; fechada em 2026-09-17T16:46:25Z por `luanmorenommaciel` como "decided + implemented"; 1 comentário.

### Intenção e benefício

Decidir se o `skew_ratio` do watcher de skew deve usar os campos seguros a retry (p99/p50 só de tasks bem-sucedidas, quando há amostra) em vez dos percentis de todas as tentativas, sabendo que isso muda o valor de uma métrica já entregue.

### Feito, faltante e não comprovado

Decidida (sim) e implementada pela PR #99 ("make skew_ratio retry-safe"), integrada em 2026-09-14; a API mostra review de `luanmorenommaciel` com `CHANGES_REQUESTED` em 2026-08-25 e `APPROVED` em 2026-09-14. Conferi em `1e0ba80`: `engine/src/apex_engine/schema.py:203-221` calcula a razão por `effective_task_duration_*`, mantém `legacy_skew_ratio` (209) e escolhe a população `successful_tasks` quando `successful_task_sample_count > 0` (216). A PR inclui `docs/task-specs/ISSUE-90-RETRY-SAFE-SKEW.md` e testes em `test_watchers.py`, `test_physics_rules.py` e `test_clickhouse_boundary.py`.

### Linhagem

Pergunta (2026-08-20) → PR #89 (integrada em 2026-09-14, cita a issue) → PR #99 com Task-Spec → aprovação (2026-09-14) → fechamento (2026-09-17). Timeline pública (API, observada em 2026-10-17T17:31:28Z; 5 eventos): fechada por `luanmorenommaciel` em 2026-09-17; referências cruzadas na timeline retornada: PR#99, PR#89; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 90); [fechamento](https://github.com/luanmorenommaciel/apex/issues/90#issuecomment-5718036779); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_90.txt` (schema em `1e0ba802049b4ebe8fb474a7853c604df2b93aeb`); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/pr99-reviews.json`; dossiê da PR #99.

### Classe e limite da evidência

DIRETO: código, reviews, arquivos da PR. RELATADO: efeito de retries inflando o p99 legado (motivação). DECISÃO: registrada como aprovação de PR e Task-Spec.

### Fluxo

Fluxo da métrica: stage → amostra de tasks bem-sucedidas? → sim: p99/p50 bem-sucedidas; não: p99/p50 de todas as tentativas → `skew_ratio`; `legacy_skew_ratio` mantido para comparação.

### Consequências e risco

Baixo. A mudança altera valores de findings em stages com retries, de forma intencional. Limite: findings antigos gravados com a razão legada não são recalculados.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) nenhuma alternativa: decidido e entregue.

### Dependências e paralelismo

Nenhuma pendente. O watcher `tail_outlier` que motivou a pergunta veio depois (#123/PR #127).

### Plano e aceite propostos

Condição explícita de não ação: decisão registrada (aprovação da PR #99 e Task-Spec), código e testes na main; nada a acrescentar nesta issue.

### Comunicação entre responsáveis

Para a consolidação: "#90 decidida e entregue pela PR #99, aprovada em 2026-09-14".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — manter só os percentis legados deixaria retries inflarem o skew reportado. (b) Que caso o teste ainda não cobre? — stage com amostra de sucesso muito pequena. (c) Como eu explicaria isso para outro pod? — "o skew agora ignora tentativas repetidas quando há dado para isso". (d) Findings antigos com a razão legada devem ser marcados?

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: já fechada; reabrir só se a escolha de população voltar a ser contestada.

<a id="item-443"></a>

## #95 — Engine fails with a raw ClickHouse error when the store's schema is behind

Frente: historico. Encaminhamento: concluida_por_pr_com_closes_integrada_sem_review_formal.

### Identidade e estado

Issue #95, tarefa (`type:task`, `phase:design`, `priority:p1`, `pod-2-engine`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-08-22; fechada em 2026-10-06T19:56:22Z, dois segundos depois do merge da PR #131 (`Closes`), na integração em lote de 2026-10-06; 0 comentários. Ligada a DD09, G04 e P05.

### Intenção e benefício

Fazer o engine falhar com mensagem clara quando o schema do ClickHouse está atrás do repositório (volume criado antes de migrações), em vez de um `Code: 47` que parece bug de SQL.

### Feito, faltante e não comprovado

Feito pela PR #131 ("fail fast on connect when spark_events schema is behind"). Conferi na main `c3c3ea3`: `engine/src/apex_engine/clickhouse.py` tem `_preflight_schema` (283), chamado na conexão (319), com comentário que cita o #95 (122) e a etapa de recuperação a nomear (266). A PR acrescenta `test_clickhouse_schema_preflight.py` (+175) e `test_database_selection_consistency.py` (+182). Detalhe: o corpo da issue manda rodar `infra/scripts/apply_schema_migrations.ps1`, arquivo que não existe na main; o script real é `infra/scripts/apply_ddl.sh` (conferido). Não comprovado: run verde da PR #131 no head final, porque ela entrou na integração de 2026-10-06 sem CI verde observado (NOV-02 da v2).

### Linhagem

Issue (2026-08-22) → PR #131 com `Closes #95` → merge em lote (2026-10-06). Depois, a #154 (aberta) e a PR #155 (aberta) cuidam do alinhamento entre colunas exigidas e consultas. Elos ausentes: review formal da PR #131 (a API retornou 0) e CI verde no head. Timeline pública (API, observada em 2026-10-17T17:31:29Z; 12 eventos): fechada por `luanmorenommaciel` em 2026-10-06; referências cruzadas na timeline retornada: #109, #114, #130, PR#131, #154, #72, #37; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 95); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_95.txt` (preflight e `infra/scripts/` na main); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/pr131-reviews.json`; dossiê da PR #131.

### Classe e limite da evidência

DIRETO: código do preflight, testes adicionados, ausência do script citado no corpo, 0 reviews formais. RELATADO: reprodução do `Code: 47` com volume anterior a `78236de`. NÃO VERIFICADO: CI e runtime do preflight.

### Fluxo

Fluxo de conexão: engine conecta → `_preflight_schema` compara colunas exigidas com o schema real → faltou coluna: erro nomeando o passo de recuperação; ok: análise segue.

### Consequências e risco

Artefato de preflight está presente, mas esta revisão não mede seu comportamento. A API capturada retornou zero reviews formais; isso não prova ausência de toda revisão fora dessa API. Um run verde no head final não foi conferido aqui, e ausência de run observado não equivale a CI executado e falho.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) incluir a PR #131 na prova pós-integração da main (P-INT-0 na v2); (c) corrigir o nome do script no texto, se ele aparecer em documentação atual.

### Dependências e paralelismo

A prova hospedada depende de DEC-01 (CI disponível). O alinhamento fino com as consultas segue na #154/PR #155.

### Plano e aceite propostos

Passo mínimo: quando o CI principal rodar na main, confirmar que `test_clickhouse_schema_preflight.py` passa. Controle discriminante: volume sem `executor_run_time_ms` deve gerar o erro nomeado, não `Code: 47`.

### Comunicação entre responsáveis

Para a consolidação: "#95 entregue pela PR #131 em 2026-10-06, sem CI verde observado nem review formal; o resíduo de prova é o mesmo da integração em lote".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — sem o preflight, duas máquinas no mesmo commit divergem e o erro aponta para o SQL errado. (b) Que caso o teste ainda não cobre? — coluna presente com tipo diferente. (c) Como eu explicaria isso para outro pod? — "se o banco está atrasado, o engine diz isso e como corrigir". (d) O texto do erro aponta para `apply_ddl.sh`?

### Próxima ação e encerramento

Owner a confirmar: mantenedor, na prova pós-integração (M0). Entrada: CI principal disponível. Saída: run verde que inclui os testes do preflight. Encerramento: a issue segue fechada; o resíduo é de prova, não de escopo.

<a id="item-444"></a>

## #102 — Pod 1: consolidar camada de dados e definir fronteira browser–serviços

Frente: historico. Encaminhamento: concluida_com_fronteira_posteriormente_ampliada.

### Identidade e estado

Issue #102, tarefa de Pod 1 (sem rótulos); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-08-24; fechada em 2026-09-17T16:46:28Z por `luanmorenommaciel` como "implemented"; 1 comentário. Ligada a P04 e X01; citada por #108, #116, #117 e #122.

### Intenção e benefício

Recuperar a camada `front/src/data` ausente do commit `c04efec` (typecheck e build falhavam), definir o menor incremento integrável e escolher a fronteira browser → serviços (host MCP, BFF, HTTP versionado ou outra), questionando o acesso direto do browser ao ClickHouse.

### Feito, faltante e não comprovado

Feito, segundo o fechamento, e conferido em `1e0ba80`: `front/src/data/` tem `repository.ts`, `clickhouse.ts`, `queries.ts`, `runtimeConfig.ts`, `useRepository.tsx`, `fixtures.ts` e testes; `front/nginx.conf` define `location = /clickhouse` e `location /clickhouse/` (linhas 33 e 38), com comentário explicando por que os dois blocos são necessários. A fronteira escolhida na época foi browser → nginx de mesma origem → ClickHouse. Evoluiu depois: na main `c3c3ea3` o nginx também tem `location /v1/` para a API HTTP da PR #129 (fronteira cuja segurança está em discussão na #171). Não conferido aqui: alinhamento do README do front ao contrato v0.5.

### Linhagem

Relato de validação de c04efec → consolidação front → follow-ups /verify → fechamento → API v1 amplia caminhos no corte de outubro. O recorte não fornece registro contemporâneo separado da decisão de fronteira; isso não prova que não exista em outro documento.

### Fontes e corte

Snapshot (item 102); [fechamento](https://github.com/luanmorenommaciel/apex/issues/102#issuecomment-5718037260); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_102.txt` (camada de dados e nginx em `1e0ba802049b4ebe8fb474a7853c604df2b93aeb` e na main).

### Classe e limite da evidência

DIRETO: arquivos da camada de dados e blocos do nginx nos dois SHAs. RELATADO: falhas de typecheck/build/lint em `c04efec`. INFERÊNCIA: a pergunta 4 (acesso direto do browser ao ClickHouse) foi respondida com proxy de mesma origem, não com BFF.

### Fluxo

Fluxo de dados do front (2026-09): componente → `repository.ts` → `clickhouse.ts` → `/clickhouse/` (nginx) → ClickHouse; desde 2026-10: alternativa `/v1/` → API → ClickHouse.

### Consequências e risco

Médio para segurança, já tratado em outros itens: o caminho browser → ClickHouse por proxy é a base sobre a qual #171 (token e exposição) e #122 (BFF) discutem. Esta issue não cria risco novo.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) registrar na consolidação que a fronteira de setembro foi ampliada pela API v1; (c) reabrir — a discussão atual vive em #171/#122.

### Dependências e paralelismo

Nenhuma pendente aqui. Decisões atuais de fronteira dependem de DEC-08 (#171) e DEC-07 (#122).

### Plano e aceite propostos

Condição de não ação: camada de dados entregue; a fronteira evoluiu e tem issues próprias.

### Comunicação entre responsáveis

Para a consolidação: "#102 entregou a camada de dados e um proxy para ClickHouse; a fronteira hoje inclui a API v1".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — mudar o transporte exige reavaliar CORS, autenticação e exposição; proxy same-origin sozinho não comprova proteção de credenciais. Que caso o teste ainda não cobre? — o caminho bare /clickhouse e a integração real da API não foram exercitados nesta auditoria. Como eu explicaria isso para outro pod? — há camada de dados e proxy para ClickHouse; no corte de outubro também há rota /v1, com decisões de fronteira em itens próprios.

### Próxima ação e encerramento

Nenhuma ação aqui. Owner das decisões atuais: donos de DEC-07/DEC-08. Encerramento: já fechada.

<a id="item-445"></a>

## #103 — [Cross-lane] Add an executable telemetry compatibility matrix

Frente: historico. Encaminhamento: concluida_por_pr_com_closes.

### Identidade e estado

Issue #103, tarefa cross-lane (`type:task`, `phase:review`, `documentation`, `priority:p1`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-08-25; fechada em 2026-09-14T16:20:04Z, dois segundos depois do merge da PR #111 (`Closes`); 0 comentários. Ligada a L08; #106–#109, #117 e #180 a citam como predecessora de evidência.

### Intenção e benefício

Criar uma matriz de compatibilidade executável que mostre onde cada campo de telemetria é produzido, transportado, armazenado e consumido, como gate estático, sem sugerir prova de runtime.

### Feito, faltante e não comprovado

Feito pela PR #111 (`docs/architecture/TELEMETRY-COMPATIBILITY-MATRIX.md` +186 e `tests/test_telemetry_compatibility_matrix.py` +200), integrada em 2026-09-14 com review aprovada (API, ficha PR#111). Os dois arquivos existem na main. Limite declarado no próprio corpo: "must not imply that a path has been proven at runtime". Ressalva apontada pelo Codex (C04-16) e reconferida por mim: o teste exige literalmente `PROPOSED v0.4` (linha 145), `PROPOSED, not ratified` (147) e a frase obsoleta de `models.py` "NOT a\n# column in apex.spark_events" (166). Ele a registra como drift conhecido `verify_executor_runtime_claim_outdated` (159–168). Corrigir o texto em #165 ou #179 exige atualizar o manifesto e a asserção juntos.

### Linhagem

Issue (2026-08-25, baseline `7c5460c`) → PR #111 com `Closes #103` → merge (2026-09-14) → base de #106–#109 e #180. Timeline pública (API, observada em 2026-10-17T17:31:32Z; 14 eventos): fechada por `luanmorenommaciel` em 2026-09-14; referências cruzadas na timeline retornada: #106, #107, #108, #109, PR#111, #117, #29, #180; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 103); dossiê da PR #111; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_103.txt` (arquivos na main e linhas 135–175 do teste); `D-CORRECOES-E-LIMITES.md` do Codex (C04-16), conferido contra a fonte.

### Classe e limite da evidência

DIRETO: arquivos, merge e as asserções literais da guarda (linhas 145, 147 e 166). Limite do artefato: estático, com `offline_unproven` explícito; não prova runtime.

### Fluxo

Fluxo da matriz: campo → produtor (JAR) → transporte (collector) → armazenamento (DDL) → consumidores (engine, serve, memory, verify) → teste estático confere a tabela contra o repositório.

### Consequências e risco

Baixo. Efeito colateral: a guarda trava textos que outras issues querem corrigir (#165, #179), o que exige mudar texto e asserção juntos.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) nenhuma alternativa; a coordenação com #165/#179 é registrada lá.

### Dependências e paralelismo

Nenhuma pendente aqui. Correções de texto em #165/#179 dependem de ajustar esta guarda.

### Plano e aceite propostos

Condição de não ação. Nota para quem corrigir textos: alterar `tests/test_telemetry_compatibility_matrix.py` na mesma PR.

### Comunicação entre responsáveis

Para a consolidação: "#103 entregue pela PR #111; a guarda estática precisa acompanhar correções de texto".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — sem a matriz, campo emitido e não consumido ficaria invisível. (b) Que caso o teste ainda não cobre? — interoperabilidade em runtime, por desenho. (c) Como eu explicaria isso para outro pod? — "uma tabela testada de onde cada campo nasce e quem o lê". (d) A guarda deveria checar intenção em vez de texto literal?

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: já fechada; reabrir só se a matriz deixar de ser verificada por teste ou passar a afirmar prova de runtime.

<a id="item-446"></a>

## #104 — [DevEx] Detect hidden editable .pth files on macOS/Python 3.14

Frente: historico. Encaminhamento: concluida_por_pr_com_closes.

### Identidade e estado

Issue #104, DevEx (`type:task`, `priority:p2`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-08-25; fechada em 2026-09-14T16:19:58Z, um segundo depois do merge da PR #110 (`Closes`); 0 comentários.

### Intenção e benefício

Criar um preflight somente leitura que detecte o flag `hidden` do macOS em arquivos `.pth` de instalação editável, que o CPython 3.14 ignora, para distinguir ambiente local quebrado de defeito do APEX.

### Feito, faltante e não comprovado

Feito pela PR #110: `scripts/editable_pth_preflight.py` (+160) e `tests/test_editable_pth_preflight.py` (+361), integrada em 2026-09-14 com review aprovada (API, ficha PR#110). Relatado no corpo: um workspace macOS local com imports falhando em quatro raias e reconstrução limpa a partir da mesma main, que funcionou. O corpo declara que não é falha geral nem multiplataforma.

### Linhagem

Incidente local relatado → issue → PR #110 com Closes → merge de 14/09. A busca por editable_pth_preflight em Makefile, scripts/apex.ps1 e scripts/apex.sh não encontrou referência em c3c3ea3; isso delimita ausência de integração textual nesses caminhos, sem provar inexistência de qualquer uso externo.

### Fontes e corte

Snapshot (item 104); dossiê da PR #110 (2 arquivos); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_104.txt` (script e teste na main; nenhuma chamada no Makefile nem nos scripts do pacote); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/pr110-reviews.json`.

### Classe e limite da evidência

DIRETO: arquivos e merge. RELATADO: incidente e reconstrução limpa. NÃO VERIFICADO: execução do preflight.

### Fluxo

Fluxo do preflight: localizar `.pth` editáveis → ler flags do sistema de arquivos → `hidden` → mensagem acionável; sem alterar o ambiente.

### Consequências e risco

Baixo: ferramenta de diagnóstico, sem efeito no produto. Evitou um pin `<3.14` desnecessário, segundo o corpo.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) ligar o preflight ao doctor, se o problema reaparecer.

### Dependências e paralelismo

Nenhuma dependência: o preflight é autocontido e só lê o sistema de arquivos; ligá-lo ao doctor seria decisão separada do dono do pacote.

### Plano e aceite propostos

Condição de não ação: ferramenta entregue com teste próprio.

### Comunicação entre responsáveis

Para a consolidação: "#104 entregue pela PR #110; diagnóstico local de macOS".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — sem diagnóstico, o time poderia fixar Python abaixo de 3.14 por um problema local. (b) Que caso o teste ainda não cobre? — outras formas de `.pth` ignorado fora do macOS. (c) Como eu explicaria isso para outro pod? — "se o import some no Mac com 3.14, rode o preflight antes de culpar o código". (d) O doctor deveria chamar esse preflight?

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: já fechada; reabrir só se o problema de `.pth` oculto reaparecer sem diagnóstico.

<a id="item-447"></a>

## #116 — [Front] /verify: estados por fonte e apresentação fiel da proposta e das evidências

Frente: historico. Encaminhamento: concluida_por_duas_prs.

### Identidade e estado

Issue #116, front (sem rótulos); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-09-11; fechada em 2026-09-14T16:20:48Z, um segundo depois do merge da PR #118, que a cita com `close`; a PR #119 também a cita e entrou 22 segundos depois; 0 comentários. Ligada a F01 e G06.

### Intenção e benefício

Na tela `/verify`, impedir que a indisponibilidade de uma fonte vire conclusão sobre dados ("sem findings") e que a apresentação afirme mais do que foi validado (por exemplo, namespace positivo para proposta interpretada só em parte), preservando a correção de `fixQ.error` já existente.

### Feito, faltante e não comprovado

Feito em duas partes: PR #118 ("isolate /verify source states and async selections (I1)": `useVerifyQuery.ts`, `VerifyScreen.tsx` e `VerifyScreen.source-state.test.tsx` +266) e PR #119 ("present /verify proposals and evidence faithfully (I2)": `contract/rules.ts` +69/-22, `rules.test.ts` +80, `DualVerdictPanel.tsx` e mais testes de estado). As duas foram integradas em 2026-09-14 com review aprovada (API). Relatado no corpo: comportamentos reproduzidos em SSR local no commit `5b4fc4f`. Não comprovado: browser real e ClickHouse real, limite que o próprio registro declara.

### Linhagem

Issue de 11/09 → PR118 I1 integrada em 14/09 16:20:47 → fechamento 16:20:48 → PR119 I2 integrada 16:21:10. O fechamento antecedeu I2 em 22 segundos; a cronologia é direta, mas nenhum efeito operacional desse intervalo foi observado nesta auditoria.

### Fontes e corte

Snapshot (item 116); dossiês das PRs #118 e #119; reviews em `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/pr118-reviews.json` e `pr119-reviews.json`.

### Classe e limite da evidência

DIRETO: arquivos, testes adicionados, merges e reviews. RELATADO: reproduções SSR. NÃO VERIFICADO: comportamento no navegador e com dados reais.

### Fluxo

Fluxo da tela: consultas por fonte (runs, findings, verificação, configuração, transições, memória) → estado próprio de cada fonte (loading, erro, vazio, dado) → painel que só afirma o que foi interpretado.

### Consequências e risco

Baixo depois das PRs. O risco original era real para o usuário (concluir "sem anomalias" por erro de consulta). Os problemas de contrato que restam no `/verify` estão no #117 (aberta).

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) nenhuma alternativa; a prova em navegador pertence a #172.

### Dependências e paralelismo

A prova em navegador e com dados reais depende de #172 (aberta).

### Plano e aceite propostos

Condição de não ação nesta issue; a prova integrada está em #172.

### Comunicação entre responsáveis

Para a consolidação: "#116 entregue pelas PRs #118 e #119; a prova em navegador segue em #172".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — uma guarda global de erros bloquearia a tela num caminho que funciona, como o corpo alerta. (b) Que caso o teste ainda não cobre? — navegador real com ClickHouse indisponível. (c) Como eu explicaria isso para outro pod? — "cada fonte da tela diz seu próprio estado; erro não vira ‘vazio’". (d) Os estados por fonte cobrem a API v1 além do ClickHouse?

### Próxima ação e encerramento

Nenhuma ação aqui. Owner da prova integrada: Pod 1 em #172. Encerramento: já fechada.

<a id="item-448"></a>

## PR#13 — chore: permission check test

Frente: historico. Encaminhamento: pr_de_teste_fechada_sem_merge.

### Identidade e estado

PR #13, `test/permission-check` → `main`; autor `antonylucas` (COLLABORATOR); criada e fechada em 2026-05-26, **sem merge**; 1 commit (`5e3f522`, +2 linhas no README); sem rótulos, assignee ou reviewer pedido. O head não está na main.

### Intenção e benefício

Validar permissões de push e de abertura de PR no repositório, "a pedido do @luanmorenommaciel" (comentário do autor). Sem intenção de produto.

### Feito, faltante e não comprovado

A PR foi aberta e encerrada sem merge. Isso demonstra a capacidade de abrir essa PR naquele contexto; não prova todo grant de push/Write, proteção de main ou permissões atuais. O plano de teste permaneceu desmarcado; não há entrega de produto.

### Linhagem

Pedido de acesso no #28 (2026-05-26) → issues de teste #11/#12 → PR #13 (mesmo dia) → fechamento sem merge. Sem relação com registro ou Task-Spec.

### Fontes e corte

Snapshot `pulls_all.json` (PR 13) e `icomments_all.json` (comentário do autor); dossiê com o diff de 1 arquivo; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: metadados, diff de 2 linhas, comentário. INFERÊNCIA: parte da mesma rodada de teste de acesso do #28. Review formal (API, observada em 2026-10-17T17:27:58Z): 0 registradas; isso não prova ausência de leitura humana. Comentários inline de review: 0. Runs do Actions com o head `5e3f522`: nenhum no universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada. Isso não prova que nenhum CI tenha rodado fora desse universo.

### Fluxo

Fluxo administrativo documentado: branch de teste → PR → comentário do autor sobre intenção de validar permissões → fechamento sem merge.

### Consequências e risco

Nenhum impacto observado: o head não é ancestral da main, e a linha que o diff acrescenta (`<!-- permission check -->`) não aparece no README da main `c3c3ea3` nem em `git log -S` da main (`fontes/batch-claude-historico-corrigido-sources/claude/fontes/reconferencia/git-reconferencia.txt`). Isso delimita a conferência ao README; não prova que conteúdo equivalente nunca tenha entrado por outro caminho.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) apagar a branch `test/permission-check`, se ainda existir, dentro do plano do #105.

### Dependências e paralelismo

Nenhuma dependência; a eventual limpeza da branch segue o #105.

### Plano e aceite propostos

Condição explícita de não ação: PR de teste sem conteúdo de produto.

### Comunicação entre responsáveis

Nenhuma comunicação necessária; na consolidação basta agrupar as PRs #13 e #14 com as issues #11/#12.

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — integrar a linha de teste no README não traria valor e poluiria o histórico. (b) Que caso o teste ainda não cobre? — não encontrei teste ligado a este item nas fontes lidas; é verificação de permissão. (c) Como eu explicaria isso para outro pod? — "foi o teste de acesso do primeiro dia".

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento definitivo; a branch, se existir, segue o plano de arquivamento do #105.

<a id="item-449"></a>

## PR#14 — Add additional spacing in README.md

Frente: historico. Encaminhamento: pr_de_teste_fechada_sem_merge.

### Identidade e estado

PR #14, `sidymar-patch-1` → `main`; autor `sidymar` (COLLABORATOR); criada e fechada em 2026-05-26, **sem merge**; 1 commit (`6fdbb07`, +2 linhas no README, com committer `GitHub <noreply@github.com>`, compatível com edição pela interface web ou pela API; o nome da branch sozinho não prova a ferramenta). Corpo: "Just testing".

### Intenção e benefício

Testar o fluxo de PR do colaborador no primeiro dia de acesso. Sem intenção de produto.

### Feito, faltante e não comprovado

A PR existiu e foi encerrada sem merge; demonstra abertura naquele contexto, sem provar push direto a main, permissões gerais ou atuais. Não há entrega de produto.

### Linhagem

Pedido de acesso no #28 → issue de teste #12 do mesmo autor → PR #14 (mesmo dia) → fechamento sem merge.

### Fontes e corte

Snapshot `pulls_all.json` (PR 14); dossiê com o diff; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: metadados e diff. INFERÊNCIA: teste de acesso, pelo corpo e pela sequência com #12. Review formal (API, observada em 2026-10-17T17:27:59Z): 0 registradas; isso não prova ausência de leitura humana. Comentários inline de review: 0. Runs do Actions com o head `6fdbb07`: nenhum no universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada. Isso não prova que nenhum CI tenha rodado fora desse universo.

### Fluxo

Fluxo observado: commit de teste com committer GitHub → branch sidymar-patch-1 → PR → fechamento; a ferramenta de edição não foi estabelecida.

### Consequências e risco

Nenhum impacto observado: o head não é ancestral da main, e o diff só acrescenta duas linhas em branco ao README; não há conteúdo substantivo cuja incorporação por outro caminho valha conferir.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) limpar a branch `sidymar-patch-1` dentro do #105, se ainda existir.

### Dependências e paralelismo

Nenhuma dependência técnica; a única ação possível, apagar a branch `sidymar-patch-1`, segue o plano de arquivamento do #105.

### Plano e aceite propostos

Condição explícita de não ação: PR de teste sem conteúdo de produto, sem artefato nem controle a produzir.

### Comunicação entre responsáveis

Nenhuma comunicação necessária; agrupar com #13 na consolidação.

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — integrar espaços no README não teria efeito útil. (b) Que caso o teste ainda não cobre? — não encontrei teste ligado a este item nas fontes lidas. (c) Como eu explicaria isso para outro pod? — "outro teste de acesso de 2026-05-26".

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento definitivo; não há escopo para reabrir.

<a id="item-450"></a>

## PR#44 — feat(serve): adicionar MCP somente leitura

Frente: historico. Encaminhamento: integrada_em_branch_de_convergencia_codigo_reestruturado_depois.

### Identidade e estado

PR #44, `serve/mcp-readonly` → `feat/base-project-e2e` (branch de convergência, não `main`); autor `gustocezar`; criada em 2026-07-23 e integrada em 2026-07-24T00:42:54Z (merge `40a35c1`); 1 commit; 13 arquivos. Chegou à main pela PR #57 (`50d596e`, 2026-07-29), conforme `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Intenção e benefício

Criar o servidor MCP via stdio com `analyze_run` e `compare_runs`, modelos tipados e um store ClickHouse somente leitura, com `readOnlyHint=true`; Judge, preview, apply e rerun ficavam fora.

### Feito, faltante e não comprovado

Feito no recorte da época. Hoje, na main `c3c3ea3`, três arquivos desta PR não existem mais: `serve/src/apex_mcp/service.py`, `store.py` e `tests/test_read_only_service.py` (o serviço foi reestruturado em `diagnose.py`/`ch.py`, ver #38). Continuam: `server.py`, `models.py`, `serve/VALIDATION.md` e os gates `tools/mcp_stdio_gate.py` e `tools/read_only_gate.py`. Relatado: "5 passed" e gates C2/C2-stdio aprovados. Não reexecutado.

### Linhagem

Plano de PRs da V1 (PR #45) → PR #44 na branch de convergência → PR #57 leva tudo à main → serve cresce para 8 ferramentas (#38). Nenhuma issue fechada por palavra-chave no corpo da PR.

### Fontes e corte

Snapshot `pulls_all.json` (PR 44); dossiê (13 arquivos, presença na main); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: datas/base, diff, ancestralidade e inventário de caminhos. RELATADO: cinco testes e gates C2/C2-stdio. A reestruturação não implica regressão nem equivalência automática; a fronteira atual deve ser lida no código e seus testes. API capturada tem zero reviews/inline; runs para o head não aparecem na janela pública delimitada.

### Fluxo

Fluxo de então: IDE → MCP stdio (`analyze_run`/`compare_runs`) → store ClickHouse somente leitura → resposta tipada. Estático.

### Consequências e risco

Baixo. Limite de leitura: quem procurar `service.py` (citado no corpo) não o achará; a lógica mudou de lugar.

### Alternativas e recomendação

(a) Manter como registro histórico (recomendado); (b) nenhuma ação: a PR está integrada e o código evoluiu.

### Dependências e paralelismo

Nenhuma pendente. A evolução do serve está nas fichas #38 e #20.

### Plano e aceite propostos

Condição explícita de não ação: PR integrada há meses; o código atual é o que vale.

### Comunicação entre responsáveis

Para a consolidação: "PR #44 introduziu o MCP somente leitura; parte dos arquivos foi reestruturada depois".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — uma ferramenta com escrita precisaria de fronteiras de autorização e produto próprias. Que caso o teste ainda não cobre? — readOnlyHint é metadado de intenção; a revisão não verificou enforcement de autorização em clientes ou servidores. Como eu explicaria isso para outro pod? — esta PR introduziu duas ferramentas de consulta e testes estáticos; presença de hint não certifica segurança.

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: histórico; reabrir só se alguma ferramenta MCP passar a escrever.

