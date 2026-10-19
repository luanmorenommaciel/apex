# Fichas documentais — lote 30

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-291"></a>

## T-20260819-runs-gates — T-20260819-runs-gates.md

Frente: Serve / L2 Discover — descoberta de runs (#83). Encaminhamento: encerrada_historica_gate_stdio_atual_com_deriva.

### Identidade e estado

`tasks/done/T-20260819-runs-gates.md` (blob 05982ae8). 'Assert run discovery in both live gates', S, standard, P2; owner `(none)`; depends_on auto-baseline. Estado `done`, `accepted: true` em 2026-08-19T19:11:59Z, aceite registrado no arquivo por `sidymar` via taskspec accept (autor da implementação; não é revisão independente nem nova autorização). Pod provável: Pod 3/Serve (caminhos serve/ e docs/lanes; nenhum pod no arquivo). Passou por `blocked` (91a7cae, 'blocked on live ClickHouse') antes do aceite.

### Intenção e benefício

Provar list_runs e apex://runs contra ClickHouse real e por stdio real, porque um FakeClient devolve o que o autor do teste digitou; só o banco real prova agregação, binding e varredura limitada por partição.

### Feito, faltante e não comprovado

Feito (d377e5a): `read_only_gate.py:210-250` semeia, lista, confere newest-first, filtro por app_name e app_name hostil (0 linhas) e emite bloco `runs`; `mcp_stdio_gate.py` passou a descobrir o próprio job via list_runs. Recibo relatado: 'read_only_gate passed runs: listed 6, seeded_found 2, newest_first true, hostile_app_name_rows 0' e 'mcp_stdio_gate passed 5 tools + apex://runs' (PR #83, 2026-08-19). Estado atual: o gate stdio no SHA tem `EXPECTED_TOOLS` com 7 entradas para 8 tools (sem recall_similar_runs) — deriva posterior, não deste aceite (ver lote anterior, stdio-gate-five-tools). O eval_2 desta spec rodado na main falharia por isso (inferência).

### Linhagem

SERVE-LEGS L2 → tasks/.plans/l2-discover.yaml (approved: true) → spec d244af7 (2026-08-19) → implementação d377e5a com accepted:true → done 6ee4245 → Duplicatas regeneradas em tasks/ (ready/false) por aab2988 e removidas por f504255 no mesmo dia; a cópia em tasks/done/ é o objeto que chegou a c3c3ea3 → PR #83 integrada (merge e10ab85, 2026-08-20 UTC); antes, 91a7cae marcou blocked por falta de ClickHouse. Elos posteriores: 3758d00 (L5) atualizou o gate stdio; L6 não.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260819-runs-gates.md; fontes/batch-revalidated-specs58-sources/history/T-20260819-runs-gates.txt; fontes/batch-revalidated-specs58-sources/git/serve__tools__read_only_gate.py; fontes/batch-revalidated-specs58-sources/git/serve__tools__mcp_stdio_gate.py; fontes/batch-revalidated-specs58-sources/git/serve__VALIDATION.md. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: gate verifica presença dos dois jobs, ordem, hostil vazio e inclusão do AFTER_JOB_ID no filtro; não verifica exclusão de jobs de outro app. stdio compara exatamente EXPECTED_TOOLS, que não contém recall_similar_runs. RELATO: VALIDATION08/19 registra gates verdes locais. Limpeza textual remove só IDs próprios, mas roda depois das asserções sem finally: não é garantida em falha. Nenhuma execução nesta revisão.

### Fluxo

Gate semeia fixtures → consultas/asserts no store → deletes dos IDs próprios → JSON; uma exceção antes dos deletes interrompe essa limpeza. stdio compara superfície exata e descobre sujeito via list_runs antes das demais tools.

### Consequências e risco

A entrega e o aceite históricos permanecem registrados. O gate stdio atual diverge da superfície de oito tools e a limpeza do gate de store não é garantida se uma asserção falhar. Isso impede tratar presença do script ou recibo antigo como prova atual; nenhum resíduo real foi pesquisado nesta auditoria.

### Alternativas e recomendação

Recomendado: manter encerrada e tratar a reconciliação do gate stdio no item já proposto. Alternativa: reabrir esta spec — mistura entrega histórica com deriva posterior.

### Dependências e paralelismo

Nenhuma dependência para permanecer encerrada. A reconciliação do gate stdio é independente e pode correr em paralelo; executar gates exige ClickHouse autorizado.

### Plano e aceite propostos

Não ação na spec. Para reuso: (1) saída do gate em arquivo temporário por execução; (2) gate stdio derivando a lista de tools de fonte única; (3) recibo com SHA e versão do ClickHouse. Doc: VALIDATION já registra.

### Comunicação entre responsáveis

Explicar: 'Os gates live provaram a descoberta de runs em 2026-08-19. Hoje o gate stdio está com 7 tools para 8 servidas — um problema posterior, separado desta spec.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Construir o esperado com o próprio ReadStore ocultaria erro de SQL; afrouxar igualdade da superfície esconderia deriva. Que caso o teste ainda não cobre? Falha de asserção após semear e antes do delete; outro app sendo indevidamente incluído pelo filtro. Como eu explicaria isso para outro pod? O script contém provas e limites distintos: o recibo é histórico, a superfície atual precisa coerência e a limpeza precisa sobreviver à falha.

### Próxima ação e encerramento

Ação: nenhuma na spec; vincular ao item do gate stdio. Owner a confirmar: Serve. Entrada: este parecer. Saída: referência cruzada. Encerramento: já encerrada.

<a id="item-292"></a>

## T-20260819-runs-injection-hardening — T-20260819-runs-injection-hardening.md

Frente: Serve / L2 Discover — descoberta de runs (#83). Encaminhamento: encerrada_controles_presentes.

### Identidade e estado

`tasks/done/T-20260819-runs-injection-hardening.md` (blob bd86af85). 'Harden run discovery against a hostile app_name', XS, standard, P2; owner `(none)`; depends_on runs-read-layer. Estado `done`, `accepted: true` em 2026-08-19T17:52:09Z, aceite registrado no arquivo por `sidymar` via taskspec accept (autor da implementação; não é revisão independente nem nova autorização). Pod provável: Pod 3/Serve (caminhos serve/ e docs/lanes; nenhum pod no arquivo).

### Intenção e benefício

Provar que um app_name hostil (definido pelo job observado) não chega ao SQL nem sai como instrução: é um novo caminho influenciado por usuário para o WHERE e para o contexto do modelo.

### Feito, faltante e não comprovado

Implementado (ab40928): `test_hostile_app_name_stays_data` (texto só em campos tipados, verbatim, em nenhuma string gerada pelo Apex), `test_hostile_app_name_triggers_no_action` (sem subprocess/os/open de escrita) e `test_hostile_app_name_is_bound_never_interpolated` (`test_injection_hardening.py:293-330`). Mapeamento: B-3 aparece no eval_2 (arquivo inteiro), e o teste de binding existe — controle real presente. Ao vivo, o read_only_gate conferiu app_name hostil = 0 linhas (runs-gates). Arquivo tocado depois por 6cb31ea (#140) em outros testes.

### Linhagem

SERVE-LEGS L2 → tasks/.plans/l2-discover.yaml (approved: true) → spec d244af7 (2026-08-19) → implementação ab40928 com accepted:true → done 0b7d8b2 → Duplicatas regeneradas em tasks/ (ready/false) por aab2988 e removidas por f504255 no mesmo dia; a cópia em tasks/done/ é o objeto que chegou a c3c3ea3 → PR #83 integrada (merge e10ab85, 2026-08-20 UTC)

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260819-runs-injection-hardening.md; fontes/batch-revalidated-specs58-sources/history/T-20260819-runs-injection-hardening.txt; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_injection_hardening.py; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__ch.py; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__server.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: três testes verificam payload construído com RunList, fixture sem ações e parâmetros de store.runs. Não chamam a tool list_runs; o fake de binding devolve vazio por construção. O SQL observado liga app_name. RELATO histórico de zero linhas live é outra evidência; presença/nomes dos testes não provam execução nem comportamento de um modelo real.

### Fluxo

Fluxo observado: app_name hostil (do job) → spark_events → RUNS_SQL (binding) → RunSummary.app_name (campo tipado) → RunList.untrusted_fields → cliente; nenhuma ação de SO disparada.

### Consequências e risco

Controles estáticos adequados ao caminho store/model lido, com limites: alterações na composição da resposta da tool ou clientes que ignoram untrusted_fields não são discriminadas por esses casos. Não foi verificada segurança universal de execução/modelos.

### Alternativas e recomendação

Recomendado: manter encerrada sem mudança. Alternativas consideradas e rejeitadas pela própria spec: escapar ou sanitizar app_name (binding substitui escaping e não perde o texto original) e asserir o texto exato do payload (frágil; o importante é onde ele pode aparecer). Padrão aplicado: dado não confiável em campo tipado com marcação explícita.

### Dependências e paralelismo

Nenhuma dependência pendente: runs-read-layer (binding) está entregue e o teste live correspondente está em runs-gates. Paralelo a tudo; nenhuma revisão ou estudo precisa esperar por esta spec, que só voltaria se o caminho de app_name mudar.

### Plano e aceite propostos

Manter o registro histórico e os limites explícitos. Os três casos cobrem store/model, não a chamada MCP. Para reuso, um teste pela tool deve conferir que filtro e app_name retornado continuam em campos tipados e nunca entram nas notas geradas. Nova utilização em comandos ou arquivos exige revisão própria.

### Comunicação entre responsáveis

Explicar a outro pod: 'Um app_name hostil entra como parâmetro ligado e sai como dado marcado em untrusted_fields; três testes desde #83 provam que não vira SQL, ação de sistema nem frase do Apex.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Escapando app_name no lugar do binding, um caso de escape não previsto alteraria a consulta. Que caso o teste ainda não cobre? — O cliente MCP que reproduz app_name em texto livre próprio, fora do payload do Apex. Como eu explicaria isso para outro pod? — 'Texto do job é dado: entra ligado, sai em campo tipado com aviso de não confiável.'

### Próxima ação e encerramento

Ação: nenhuma; registrar a ficha como encerrada sem resíduo. Owner a confirmar: Serve. Entrada: nenhuma nova. Saída: esta ficha como referência. Encerramento: já encerrada; condição de reabertura é uso novo de app_name fora de campo tipado.

<a id="item-293"></a>

## T-20260819-runs-read-layer — T-20260819-runs-read-layer.md

Frente: Serve / L2 Discover — descoberta de runs (#83). Encaminhamento: encerrada_com_correcao_live_posterior.

### Identidade e estado

`tasks/done/T-20260819-runs-read-layer.md` (blob c68283a4). 'Add ReadStore.runs for bounded run discovery', S, standard, P2; owner `(none)`; sem dependências. Estado `done`, `accepted: true` em 2026-08-19T15:18:44Z, aceite registrado no arquivo por `sidymar` via taskspec accept (autor da implementação; não é revisão independente nem nova autorização). Pod provável: Pod 3/Serve (caminhos serve/ e docs/lanes; nenhum pod no arquivo).

### Intenção e benefício

Uma leitura limitada que devolve runs recentes agregados por job_id, filtrável por app_name, com janela `since` ligada no WHERE para podar partições (spark_events é ordenada por job_id e particionada por mês).

### Feito, faltante e não comprovado

Implementado (b21d3e3): `RUNS_SQL` (`ch.py:108-124`) com `e.ts >= {since:DateTime}`, `app_name` ligado, `GROUP BY job_id`, `ORDER BY last_ts DESC`, `LIMIT {limit:UInt32}`; `runs()` (743-770) com clamp de limite e mínimo de 1 hora. Testes `test_runs_aggregates_one_row_per_job`, `..._filters_by_app_name`, `..._binds_hostile_app_name`, `..._bounds_the_scan_on_ts`, `..._clamps_a_caller_supplied_limit` (`test_ch.py:213-280`). Defeito achado só no gate live (PR #83): o alias `argMax(app_name, ts) AS app_name` fazia o `app_name` do WHERE resolver para o agregado (ILLEGAL_AGGREGATION); hoje o WHERE usa `e.app_name` qualificado — correção posterior ao aceite.

### Linhagem

SERVE-LEGS L2 → tasks/.plans/l2-discover.yaml (approved: true) → spec d244af7 (2026-08-19) → implementação b21d3e3 com accepted:true → done 10488a6 → Duplicatas regeneradas em tasks/ (ready/false) por aab2988 e removidas por f504255 no mesmo dia; a cópia em tasks/done/ é o objeto que chegou a c3c3ea3 → PR #83 integrada (merge e10ab85, 2026-08-20 UTC); correção do alias depois do aceite, antes do merge (PR #83).

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260819-runs-read-layer.md; fontes/batch-revalidated-specs58-sources/history/T-20260819-runs-read-layer.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__ch.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_ch.py; fontes/batch-revalidated-specs58-sources/git/serve__VALIDATION.md. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: GROUP BY, ORDER BY, janela ligada e e.app_name qualificado. Os testes de agregação/filtro recebem linhas já agregadas/filtradas do fake e verificam SQL/parâmetros; não analisam SQL. eval_3 procura três fragmentos, insuficientes para provar poda ou parser válido. RELATO: VALIDATION documenta ILLEGAL_AGGREGATION no banco real e correção anterior ao merge. Nada executado.

### Fluxo

runs calcula since e clamp → consulta parametrizada RUNS_SQL → linhas do cliente. O predicado permite poda de partições; a poda efetiva não foi observada nesta auditoria.

### Consequências e risco

O alias problemático já está qualificado no snapshot. O store ainda permite since_hours arbitrariamente alto, portanto a existência do predicado não garante custo baixo em qualquer pedido. Os controles offline não certificam agregação nem plano do banco; riscos atuais universais não podem ser excluídos por leitura.

### Alternativas e recomendação

Recomendado: manter encerrada com nota da correção do alias após o aceite. Alternativa: re-aceite formal no SHA corrigido para que o aceite cubra o estado final. Tradeoff: a nota custa nada e preserva a história; o re-aceite exige executar evals em etapa autorizada.

### Dependências e paralelismo

Nenhuma dependência: é a primeira unidade do L2 e não tem predecessor. É precondição de list-runs-tool, auto-baseline e runs-injection-hardening, todas entregues. A nota documental corre em paralelo a tudo.

### Plano e aceite propostos

Condição de não ação no código. Nota documental: 'aceite em b21d3e3; alias corrigido antes do merge (PR #83)'. Para reuso do plano: acrescentar um controle que detecte sombreamento de alias (gate live ou parser SQL), já que o eval_3 é um grep de estrutura que não prova a poda.

### Comunicação entre responsáveis

Explicar: 'A leitura de runs existe desde #83, com janela e binding; o primeiro teste em banco real achou um alias que o fake não achava, corrigido antes do merge.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Sem o predicado de ts, a listagem varreria todas as partições de uma tabela ordenada por job_id. Que caso o teste ainda não cobre? — A poda de partições em si (o teste vê o predicado, não o plano de execução) e o sombreamento de alias, que só o ClickHouse rejeita. Como eu explicaria isso para outro pod? — 'since_hours não é conveniência: é o que torna a listagem barata nesta tabela.'

### Próxima ação e encerramento

Ação: anotar a correção pós-aceite. Owner a confirmar: Serve. Entrada: PR #83 seção 'What the live gate caught'. Saída: nota no índice/plano. Encerramento: já encerrada; reabrir só se RUNS_SQL mudar sem gate live.

<a id="item-294"></a>

## T-20260819-runs-resource — T-20260819-runs-resource.md

Frente: Serve / L2 Discover — descoberta de runs (#83). Encaminhamento: encerrada_com_b3_sem_teste_dedicado.

### Identidade e estado

`tasks/done/T-20260819-runs-resource.md` (blob 22afe1f5). 'Expose apex://runs as an MCP resource', S, standard, P2; owner `(none)`; depends_on tool-surface-five. Estado `done`, `accepted: true` em 2026-08-19T17:53:17Z, aceite registrado no arquivo por `sidymar` via taskspec accept (autor da implementação; não é revisão independente nem nova autorização). Pod provável: Pod 3/Serve (caminhos serve/ e docs/lanes; nenhum pod no arquivo).

### Intenção e benefício

Servir a lista de runs recentes como recurso MCP legível, para orientação sem gastar uma chamada de tool, herdando a disciplina read-only e a marcação de campos não confiáveis.

### Feito, faltante e não comprovado

Implementado (b185564): `@mcp.resource('apex://runs', mime_type='application/json')` em `server.py:530-555`, usando `store.runs()` e `_fail()`; testes `test_runs_resource_is_listed`, `..._returns_run_data`, `..._is_not_a_tool` (`test_server_tools.py:198-255`). B-3 (store inacessível → código sanitizado sem credencial) não tem teste dedicado: o eval_2 só exporta senha sentinela e roda o arquivo; pela leitura, o caminho passa por `_fail()` e seria sanitizado. Diferença menor: o recurso monta `RunList(runs, returned)` sem `limit`/`since_hours`, então o payload declara `limit: 0, since_hours: 0` embora a busca use 20/168 — metadado impreciso, não dado errado.

### Linhagem

SERVE-LEGS L2 → tasks/.plans/l2-discover.yaml (approved: true) → spec d244af7 (2026-08-19) → implementação b185564 com accepted:true → done 33d1e1a → Duplicatas regeneradas em tasks/ (ready/false) por aab2988 e removidas por f504255 no mesmo dia; a cópia em tasks/done/ é o objeto que chegou a c3c3ea3 → PR #83 integrada (merge e10ab85, 2026-08-20 UTC)

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260819-runs-resource.md; fontes/batch-revalidated-specs58-sources/history/T-20260819-runs-resource.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__server.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_server_tools.py; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__models.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: recurso JSON com RunList, marcado untrusted e excluído da superfície de tools. RunList recebe runs/returned e herda limit0/since_hours0, divergindo da busca20/168. O except chama _fail, mas os testes lidos não exercitam store indisponível pela leitura do recurso; exportar senha sentinela sem esse estímulo não prova B-3. A sanitização é intenção estática, não resultado executado.

### Fluxo

Fluxo observado: cliente → resources/list → apex://runs ; resources/read → runs_resource → store.runs() (defaults) → RunList(runs, returned) → JSON indentado ; falha → _fail → ApexStoreError sanitizado.

### Consequências e risco

Sem ação: nenhum risco relevante de dado. Consequência possível: um cliente que exiba a janela do payload mostraria 'limit 0, since_hours 0', o que é falso; e uma mudança futura que removesse `_fail` do recurso não seria pega por teste. Probabilidade baixa; confiança alta.

### Alternativas e recomendação

Recomendado: manter encerrada; melhoria opcional pequena: passar limit/since_hours ao RunList do recurso e adicionar teste de store inacessível. Alternativa: documentar que o recurso não informa a janela.

### Dependências e paralelismo

Nenhuma dependência pendente (tool-surface-five e list_runs entregues). A melhoria opcional (metadados e teste de store fora) independe de ambiente e de outras specs e pode correr em paralelo a qualquer frente.

### Plano e aceite propostos

Se adotada a melhoria: (1) RunList com limit=20, since_hours=168; (2) teste com FakeClient que levanta → mensagem com código e sem senha sentinela; (3) controle negativo: remover `_fail` faz falhar. Esta spec: nenhuma ação.

### Comunicação entre responsáveis

Explicar: 'apex://runs existe desde #83 e não infla a lista de tools. O caso de banco fora não tem teste próprio e o payload informa limite 0, um detalhe a corrigir se for útil.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Se o recurso consultasse o cliente direto em vez do ReadStore, perderia a sanitização e os limites; se virasse tool, aumentaria a superfície que o modelo vê. Que caso o teste ainda não cobre? — Leitura do recurso com o store inacessível e a precisão dos metadados de janela. Como eu explicaria isso para outro pod? — 'Recurso é para orientação barata; ele devolve o mesmo payload de list_runs nos defaults.'

### Próxima ação e encerramento

Ação: registrar melhoria opcional. Owner a confirmar: Serve. Entrada: server.py:530-555. Saída: item pequeno ou nota. Encerramento: já encerrada.

<a id="item-295"></a>

## T-20260819-serve-brief-five-tools — T-20260819-serve-brief-five-tools.md

Frente: Serve / L2 Discover — descoberta de runs (#83). Encaminhamento: encerrada_historica_brief_atual_desatualizado.

### Identidade e estado

`tasks/done/T-20260819-serve-brief-five-tools.md` (blob 1b3e905c). 'Update the SERVE lane brief to the five-tool surface', XS, standard, P2; owner `(none)`; depends_on discover-docs. Estado `done`, `accepted: true` em 2026-08-19T19:16:23Z, aceite registrado no arquivo por `sidymar` via taskspec accept (autor da implementação; não é revisão independente nem nova autorização). Pod provável: Pod 3/Serve (caminhos serve/ e docs/lanes; nenhum pod no arquivo). Criada já na regeneração aab2988 (separada de discover-docs para caber no orçamento M).

### Intenção e benefício

Levar a missão e o critério T11 de `docs/lanes/SERVE.md` à superfície de então (cinco tools e apex://runs), preservando o checklist T1–T14 como registro histórico do L1.

### Feito, faltante e não comprovado

Feito (7f83554, 2026-08-19). Estado atual no SHA: a missão de `SERVE.md:9` ainda diz '**five tools**: four read-only (list_runs, analyze_run, compare_runs, search_kb) and one ... WRITE tool' — desatualizada frente às oito tools; o arquivo não foi tocado depois de 7f83554 (último commit no caminho). As linhas T10/T12 ainda falam em '/mcp lists the 4 tools' — são checklist histórico que a spec mandou preservar. Concluída no seu escopo; a deriva é posterior.

### Linhagem

Criada na regeneração aab2988 (separada de discover-docs para caber no orçamento M de três caminhos) → edição 7f83554 → done 9a1ae67 → PR #83 (2026-08-20 UTC). Elo ausente: nenhuma leg posterior (L3, L5, L6, #129, #132) atualizou a missão de SERVE.md, que é o último commit no caminho.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260819-serve-brief-five-tools.md; fontes/batch-revalidated-specs58-sources/history/T-20260819-serve-brief-five-tools.txt; fontes/batch-revalidated-specs58-sources/git/docs__lanes__SERVE.md; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_server_tools.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: missão mantém cinco tools e recurso; checklist conserva texto histórico de quatro. Os evals só proíbem duas expressões e contam ao menos14marcadores; não comparam T1–T14 entre refs, logo não provam B-3 unchanged nem uma contagem atual correta. O histórico registra entrega/aceite; não houve diff histórico independente completo nem execução nesta auditoria.

### Fluxo

Fluxo documental: superfície registrada pelo servidor (hoje oito tools e um recurso) → missão de docs/lanes/SERVE.md → leitor de outro pod que planeja trabalho; checklist T1–T14 → registro histórico do que o L1 entregou. Observado: a primeira seta parou em 2026-08-19.

### Consequências e risco

Sem ação: o brief da lane afirma 'cinco tools' para quem o lê hoje — a própria spec diz que 'um brief que contradiz o código é pior que nenhum'. Impacto documental. Confiança alta.

### Alternativas e recomendação

Recomendado: manter encerrada e incluir a missão de SERVE.md no item único de reconciliação documental (preferindo texto sem contagem ou derivado de CONTRACTED_TOOLS). Alternativa: atualizar só o número — repete a deriva na próxima tool.

### Dependências e paralelismo

Nenhuma dependência para permanecer encerrada. O item de reconciliação documental (missão de SERVE.md junto com README/VALIDATION/gates) é independente desta spec e de qualquer ambiente; pode correr em paralelo às revisões de PR.

### Plano e aceite propostos

Não ação na spec. No item documental: corrigir a missão, manter checklist histórico, controle: checagem estática de contagem igual a len(CONTRACTED_TOOLS) fora de seções históricas.

### Comunicação entre responsáveis

Explicar a outro pod: 'O brief foi atualizado para cinco tools em agosto e ninguém o tocou depois; hoje o servidor tem oito. O checklist T1–T14 é histórico e deve ficar como está; a missão é que precisa refletir o presente.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Editando o checklist T1–T14, perderíamos o registro do que L1 entregou e quando. Que caso o teste ainda não cobre? — Um número errado que não seja 'four': o eval só proíbe 'four tools'. Como eu explicaria isso para outro pod? — 'A missão é presente e precisa acompanhar o código; o checklist é passado e fica como está.'

### Próxima ação e encerramento

Ação: incluir no item de reconciliação documental. Owner a confirmar: Serve/documentação. Entrada: SERVE.md:9. Saída: missão atualizada no item novo. Encerramento: esta spec já encerrada.

<a id="item-296"></a>

## T-20260819-tool-surface-five — T-20260819-tool-surface-five.md

Frente: Serve / L2 Discover — descoberta de runs (#83). Encaminhamento: encerrada_historica_eval_aponta_teste_renomeado.

### Identidade e estado

`tasks/done/T-20260819-tool-surface-five.md` (blob fc1f9c32). 'Re-pin the tool surface assertion at five', XS, standard, P2; owner `(none)`; depends_on list-runs-tool. Estado `done`, `accepted: true` em 2026-08-19T17:50:59Z, aceite registrado no arquivo por `sidymar` via taskspec accept (autor da implementação; não é revisão independente nem nova autorização). Pod provável: Pod 3/Serve (caminhos serve/ e docs/lanes; nenhum pod no arquivo).

### Intenção e benefício

Mover a asserção exata da superfície de tools de quatro para cinco nomes (com list_runs), mantendo igualdade: uma tool acidental num servidor que um modelo chama é evento de segurança.

### Feito, faltante e não comprovado

Feito em 2fd8a09 (2026-08-19). Superação posterior: df6fe77 (autor 2026-08-24; integrado por #101 em 2026-08-26) trocou por lista única `CONTRACTED_TOOLS` comparada **ordenada** (sorted), hoje com oito nomes, e o teste se chama `test_the_contracted_tool_surface` (`test_server_tools.py:20-67`). O eval_1 desta spec nomeia `test_exactly_the_five_contracted_tools`, que não existe mais no SHA — rodado na main, seria erro de coleta (inferência). B-1 'ordem exata' foi substituída por decisão documentada no docstring (ordem de registro causava colisão entre pernas). O controle de igualdade (B-2) continua.

### Linhagem

SERVE-LEGS → l2-discover.yaml:164 → spec → 2fd8a09 (aceite) → d395c33 (done) → PR #83 → df6fe77/#101 (lista única ordenada) → L3/L5/L6 acrescentam nomes. Elo: o contexto da spec já previa reconciliação com o 'outro cinco' do L1 (apex_status), que nunca veio.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260819-tool-surface-five.md; fontes/batch-revalidated-specs58-sources/history/T-20260819-tool-surface-five.txt; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_server_tools.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

FATO OBSERVADO: teste renomeado, oito nomes, comparação sorted. INFERÊNCIA: aceite vale para 2fd8a09; reexecutar o eval na main falharia por nome inexistente, não por regressão. DECISÃO já tomada (df6fe77) sobre ordenada vs registro. Sem execução.

### Fluxo

Fluxo observado estaticamente: create_server registra oito tools → FastMCP.list_tools → nomes → sorted → comparação de igualdade com CONTRACTED_TOOLS → falha em tool extra ou ausente. Na época da spec: lista literal de cinco na ordem de registro.

### Consequências e risco

O controle atual preserva igualdade dos nomes e permite paralelismo sem depender da ordem de registro. Isso não certifica anotações ou segurança de cada tool; tais controles têm escopo separado. O eval antigo aponta nó ausente no snapshot e não deve ser usado como prova de regressão funcional.

### Alternativas e recomendação

Recomendado: manter encerrada com nota apontando o sucessor df6fe77/#101. Alternativa: emendar o eval para o nome atual — reescreve a história do aceite; prefiro nota. Não recomendo voltar à ordem de registro: o docstring atual registra que ela causava colisão entre pernas paralelas.

### Dependências e paralelismo

Nenhuma dependência: list-runs-tool entregue; o sucessor do controle já está na main. Paralelo a tudo. A spec gêmea do L1 (T-20260817-five-tools-assertion) deve ser encerrada pela mesma referência, sem esperar esta.

### Plano e aceite propostos

Condição de não ação no código. Nota documental: 'eval_1 aponta test_exactly_the_five_contracted_tools, renomeado em df6fe77; controle vigente test_the_contracted_tool_surface com lista única de oito'. Não reexecutar o eval antigo como prova de regressão.

### Comunicação entre responsáveis

Explicar: 'A asserção de cinco tools foi o controle de agosto; hoje é uma lista única de oito, comparada ordenada. O eval desta spec aponta um teste que mudou de nome.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Uma checagem de subconjunto permitiria tools extras sem revisão; depender da ordem de registro introduz acoplamento entre folhas. Que caso o teste ainda não cobre? Uma alteração perigosa de anotação ou comportamento com os mesmos oito nomes. Como eu explicaria isso para outro pod? O controle atual compara a lista completa de nomes; o eval histórico usa um nome de teste superado e precisa remissão ao sucessor.

### Próxima ação e encerramento

Ação: nota de sucessor no índice. Owner a confirmar: Serve. Entrada: df6fe77 e teste atual. Saída: nota. Encerramento: já encerrada; o controle de superfície continua ativo e é o único a manter.

<a id="item-297"></a>

## T-20260820-coverage-freshness — T-20260820-coverage-freshness.md

Frente: Serve / L3 Understand — legibilidade do diagnóstico (#88). Encaminhamento: encerrada_sem_aceite_formal_com_lacuna_live_documentada.

### Identidade e estado

`tasks/done/T-20260820-coverage-freshness.md` (blob a7bf240b). 'Report what the diagnosis actually saw', S, standard, P2; owner `(none)`; depends_on detail-parameter. Estado `done`; `accepted: false` e `signed_off: false` por escolha registrada: o commit 9ff859b e o corpo da PR #88 dizem que esses bits pertencem a `taskspec gate --stamp`, 'which is not in this repo', e que marcá-los à mão anula seu propósito — portanto 'done sem aceite' é deliberado e não omissão. Pod provável: Pod 3/Serve (caminhos serve/; nenhum pod no arquivo).

### Intenção e benefício

Todo Diagnosis passa a dizer quantos stages e findings observou e a idade do evento mais novo, para que um 'healthy' visto sobre um stage não pareça um quadro completo e para que um job_id perdido não se confunda com um run limpo (fraqueza W1).

### Feito, faltante e não comprovado

Implementado (27beadb): `Coverage` em `models.py:154-180` (stages_observed, findings_observed, plan_transitions_observed, newest_event_ts, newest_event_age_seconds) e `_coverage()` em `diagnose.py:387-415`, que só relata a idade (sem limiar). Testes nomeados nos evals presentes (`test_diagnosis_reports_coverage`, `test_thin_coverage_is_visible_on_a_healthy_verdict`, `test_ingest_age_is_reported_not_judged`, `test_diagnose.py:245-300`). Lacuna deliberada e ainda presente no SHA: no caminho live, `STAGES_SQL` não projeta `ts` (só argMax(col, ts)), e `_row_ts` procura `ts`/`last_ts`/`latest_ts` — logo `newest_event_age_seconds` é null com dados reais; os testes usam linhas com ts. Registrado em VALIDATION 'Known limits' e SERVE-LEGS:153; a PR chamou de 'Worth a follow-up task' — nenhum follow-up foi localizado no snapshot de issues/PRs de 2026-10-16 nem em tasks/.

### Linhagem

SERVE-LEGS L3 → l3-understand.yaml (approved: true) → specs dc1c2ce (autor 2026-08-20; commit 2026-08-26) → implementações no mesmo ramo → 9ff859b 'six units done' (status done, accepted false) → PR #88 integrada em 2026-09-14 (merge 1125cdb). Elo ausente: follow-up para projetar o tempo do evento em STAGES_SQL (ch.py era do-not-touch para esta unidade).

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260820-coverage-freshness.md; fontes/batch-revalidated-specs58-sources/history/T-20260820-coverage-freshness.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__models.py; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__diagnose.py; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__ch.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_diagnose.py; fontes/batch-revalidated-specs58-sources/git/serve__VALIDATION.md. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: contagens Coverage, _row_ts e testes com timestamps fornecidos. STAGES_SQL usa ts em argMax, mas não o retorna. Assim idade numérica de B-1/B-2 é demonstrada pelo desenho dos fakes, não pelo caminho real de stages; ambos ficam limitados no live. O relatório UNKNOWN evita julgar stale/fresh, mas honestidade do nulo não cumpre a capacidade numérica prometida. RELATO: evals/gates verdes e opção por flags falsas no histórico. Nada executado.

### Fluxo

Fluxo observado: ReadStore.stages (argMax por stage, sem ts) → analyze() → _coverage(rows) → _row_ts(row) não acha chave de tempo → newest_event_ts/age = null → Diagnosis.coverage → nota no payload 'UNKNOWN, not fresh'. Com fakes que trazem ts: idade numérica.

### Consequências e risco

Sem ação: usuários veem idade nula em todo diagnóstico real; o texto diz 'desconhecido', o que é honesto, mas a capacidade prometida (frescor) não existe em produção. Impacto médio para quem quer distinguir dado velho; nenhum incidente. Confiança alta (leitura direta).

### Alternativas e recomendação

Preservar status histórico done/accepted false e registrar que a promessa numérica de B-1/B-2 permanece incompleta no caminho stages real. Propor follow-up que acrescente tempo às mesmas linhas analisadas, com teste e prova live; não tratar documentação do limite como satisfação integral da spec.

### Dependências e paralelismo

Nenhuma dependência para permanecer encerrada. O follow-up depende de decisão de tocar ch.py e de prova live para a SQL; estudo e teste offline podem correr em paralelo a qualquer frente.

### Plano e aceite propostos

Follow-up: (1) acrescentar coluna de tempo por stage em STAGES_SQL; (2) teste com FakeClient devolvendo datetime do driver; (3) gate live: idade numérica e pequena para linhas semeadas; (4) controle negativo: remover a coluna faz a idade voltar a null e o teste falhar; (5) atualizar VALIDATION/SERVE-LEGS. Esta spec: nota de 'aceite não formalizado por desenho'.

### Comunicação entre responsáveis

Explicar: 'Todo diagnóstico diz o que viu desde #88, mas a idade do evento é nula com dados reais porque a consulta de stages não traz o tempo. Está documentado; falta o follow-up que a própria PR sugeriu.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Com um limiar de 'stale' do Apex, um batch noturno e um job de streaming receberiam veredito errado; calculando a cobertura com uma segunda consulta, os números poderiam divergir das linhas usadas no diagnóstico. Que caso o teste ainda não cobre? — O caminho live, em que STAGES_SQL não traz ts e a idade fica sempre nula. Como eu explicaria isso para outro pod? — 'Cobertura conta o que foi visto; a idade só aparece se a linha tiver tempo, e hoje a consulta real não traz.'

### Próxima ação e encerramento

Ação: propor follow-up da idade no caminho live. Owner a confirmar: Serve. Entrada: STAGES_SQL e VALIDATION:272-280. Saída: issue/spec nova com prova live. Encerramento: idade numérica no live, ou decisão de manter nulo documentada.

<a id="item-298"></a>

## T-20260820-critical-path — T-20260820-critical-path.md

Frente: Serve / L3 Understand — legibilidade do diagnóstico (#88). Encaminhamento: encerrada_sem_aceite_formal_controles_presentes.

### Identidade e estado

`tasks/done/T-20260820-critical-path.md` (blob 8c930574). 'Frame the bottleneck as a path, not a list', S, standard, P2; owner `(none)`; depends_on coverage-freshness. Estado `done`; `accepted: false` e `signed_off: false` por escolha registrada: o commit 9ff859b e o corpo da PR #88 dizem que esses bits pertencem a `taskspec gate --stamp`, 'which is not in this repo', e que marcá-los à mão anula seu propósito — portanto 'done sem aceite' é deliberado e não omissão. Pod provável: Pod 3/Serve (caminhos serve/; nenhum pod no arquivo).

### Intenção e benefício

Relatar a participação de cada stage no tempo total de cauda (soma de p99) e o menor conjunto que cobre a maior parte — 'o stage 4 é 61% da cauda' é acionável; uma lista de dezessete stages é lição de casa. Com o aviso explícito de que é participação na cauda, não caminho crítico de escalonamento.

### Feito, faltante e não comprovado

Implementado (80c8fab): `StageView.tail_share` com descrição 'SHARE OF TAIL. It is NOT a scheduling critical path' (`models.py:101-108`) e `Diagnosis.tail_dominant_stage_ids` (207-216); `_tail_dominant` em `diagnose.py:317-360`. Testes `test_stage_carries_share_of_tail`, `test_dominant_stage_is_named_alone`, `test_even_stages_name_no_bottleneck` (`test_diagnose.py:161-200`). eval_2 lê o JSON Schema e exige a ressalva — controle real de B-4. O título da spec ('path') foi corrigido no nome do campo para 'share of tail', como a própria spec manda.

### Linhagem

SERVE-LEGS L3 → l3-understand.yaml (approved: true) → specs dc1c2ce (autor 2026-08-20; commit 2026-08-26) → implementações no mesmo ramo → 9ff859b 'six units done' (status done, accepted false) → PR #88 integrada em 2026-09-14 (merge 1125cdb). Sem elos ausentes relevantes além do aceite formal.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260820-critical-path.md; fontes/batch-revalidated-specs58-sources/history/T-20260820-critical-path.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__models.py; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__diagnose.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_diagnose.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: campo declara share of tail e ressalva de sobreposição; _tail_dominant separa concentração e cobertura; casos de80% e divisão igual presentes. eval_2 procura share of tail OU not a scheduling em todo JSON Schema, portanto pode passar mesmo se o campo específico perder sua ressalva. A descrição atual cumpre a intenção; o controle é menos estrito que B-4. Execução verde é relato histórico, não reproduzida.

### Fluxo

Fluxo observado: stages (p99) → soma de p99 = cauda total → tail_share por stage → _tail_dominant (menor conjunto que cobre a maior parte; nenhum se a distribuição é plana) → Diagnosis.tail_dominant_stage_ids → resumo.

### Consequências e risco

A leitura sustenta a implementação da métrica e o limite declarado de modelagem. Não exclui riscos universais: sobreposição, valores inválidos ou extremos não são resolvidos por três exemplos; a ressalva explica por que a métrica não mede ganho real de parede.

### Alternativas e recomendação

Recomendado: manter encerrada; registrar o aceite como 'não formalizado por desenho'. Alternativa futura: caminho crítico real exigiria tempos de início/fim por stage e mapa de dependências que o contrato não carrega — estudo separado, não correção.

### Dependências e paralelismo

Nenhuma dependência pendente. Um estudo de caminho crítico real dependeria de mudança de contrato (JAR/collector) e pode correr em paralelo sem bloquear nada.

### Plano e aceite propostos

Condição de não ação: controles presentes cobrem os quatro comportamentos. Se o contrato passar a carregar início/fim por stage, abrir spec nova para caminho crítico verdadeiro, mantendo tail_share com a ressalva.

### Comunicação entre responsáveis

Explicar: 'O diagnóstico diz qual parte da cauda cada stage representa e nomeia o dominante só quando existe; o schema avisa que não é caminho crítico.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Chamando o campo de caminho crítico, um leitor trataria a soma de p99 como verdade de escalonamento e otimizaria um stage que roda em paralelo com outro. Que caso o teste ainda não cobre? — Stages fortemente sobrepostos no tempo, em que a participação na cauda superestima o ganho real. Como eu explicaria isso para outro pod? — 'É participação na cauda medida por p99, não ordem de execução; quando ninguém domina, o Apex não inventa um gargalo.'

### Próxima ação e encerramento

Ação: nenhuma no código; registrar no índice que o aceite não foi formalizado por desenho (9ff859b). Owner a confirmar: Serve. Entrada: esta ficha. Saída: nota. Encerramento: já encerrada; reabrir só se o contrato passar a carregar início/fim por stage.

<a id="item-299"></a>

## T-20260820-detail-parameter — T-20260820-detail-parameter.md

Frente: Serve / L3 Understand — legibilidade do diagnóstico (#88). Encaminhamento: encerrada_sem_aceite_formal_com_efeito_colateral_corrigido_em_153.

### Identidade e estado

`tasks/done/T-20260820-detail-parameter.md` (blob 4e38193b). 'Give analyze_run a detail level', M, standard, P2; owner `(none)`; sem dependências. Estado `done`; `accepted: false` e `signed_off: false` por escolha registrada: o commit 9ff859b e o corpo da PR #88 dizem que esses bits pertencem a `taskspec gate --stamp`, 'which is not in this repo', e que marcá-los à mão anula seu propósito — portanto 'done sem aceite' é deliberado e não omissão. Pod provável: Pod 3/Serve (caminhos serve/; nenhum pod no arquivo).

### Intenção e benefício

Dar a analyze_run `detail=summary|stages|full` com padrão `summary`, porque o run P0 real devolvia 17 stages e todos os findings num payload; a resposta padrão a 'por que ficou lento' deve caber em três linhas, e todas as larguras devem vir da mesma análise.

### Feito, faltante e não comprovado

Implementado (6af165e): `diagnose.trim()` (`diagnose.py:548-600`) — `full` é identidade; `stages` e `summary` cortam e acrescentam nota 'TRIMMED from this payload, not absent'; a tool usa `detail` com padrão summary (`server.py:172-207`). Testes `test_summary_omits_stage_and_finding_arrays`, `..._stages_level_includes_stages_not_findings`, `..._full_level_is_unchanged_from_today`, `test_verdict_is_identical_across_detail_levels` (`test_diagnose.py:349-410`). Efeito colateral posterior observado: o gate canônico `scripts/e2e_six_lanes.py` (não tocado desde 2026-08-19) lia o padrão summary como todo e falhou todo job até 3816084 (#153, 2026-10-06) pedir `detail: full`.

### Linhagem

SERVE-LEGS L3 → l3-understand.yaml (approved: true) → specs dc1c2ce (autor 2026-08-20; commit 2026-08-26) → implementações no mesmo ramo → 9ff859b 'six units done' (status done, accepted false) → PR #88 integrada em 2026-09-14 (merge 1125cdb) → 2026-10-06: quebra do gate de seis lanes descoberta e corrigida em #153 (T-20261006-six-lane-gate-full-detail). Elo ausente na época: nenhum teste ligando o novo padrão aos consumidores fora do serve.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260820-detail-parameter.md; fontes/batch-revalidated-specs58-sources/history/T-20260820-detail-parameter.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__diagnose.py; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__server.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_diagnose.py; fontes/batch-revalidated-specs58-sources/git/scripts__e2e_six_lanes.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: trim(full) retorna o próprio objeto; testes comparam identidade e model_dump da análise atual, não um payload histórico byte a byte. Os demais níveis cortam arrays e preservam veredito; a tool analisa uma vez por chamada e depois corta. Isso não garante respostas idênticas entre chamadas separadas enquanto o store muda. RELATO histórico de falha do consumidor e evals verdes não foi reexecutado.

### Fluxo

Fluxo observado: analyze_run(job_id, detail) → diagnose.analyze (uma vez) → trim(detail) → summary: sem stages/symptoms/findings/transitions + nota ; stages: sem findings/transitions + nota ; full: o mesmo objeto. Consumidores: clientes MCP, gate de seis lanes (agora com full), stdio gate (verifica que o padrão é cortado e o veredito idêntico em full).

### Consequências e risco

Gate de seis lanes pede full no snapshot. Outros consumidores que contam arrays no padrão podem tratar corte como ausência; notas ajudam a interpretação, mas não corrigem scripts. A identidade de trim protege o objeto corrente, sem congelar contrato histórico nem eliminar riscos dos demais consumidores.

### Alternativas e recomendação

Recomendado: manter encerrada; registrar a lição (mudança de padrão exige procurar consumidores que contam) e a ligação com 3816084. Alternativa: tornar `full` o padrão para chamadas de script — contraria o objetivo de legibilidade.

### Dependências e paralelismo

Nenhuma dependência pendente. A busca por outros consumidores que contam arrays é um estudo pequeno, independente e paralelo; não exige ambiente.

### Plano e aceite propostos

Condição de não ação no código. Estudo opcional: grep de chamadas a analyze_run sem `detail` em scripts/gates (hoje o gate de seis lanes já usa full) e teste de contrato que falhe se um consumidor contar arrays de summary. Nota de aceite por desenho.

### Comunicação entre responsáveis

Explicar: 'analyze_run responde em três larguras desde #88, sempre da mesma análise. O padrão resumido quebrou um gate que contava stages até #153 corrigir; scripts que contam devem pedir detail=full.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Recalculando a análise por nível, dois chamadores poderiam receber vereditos diferentes para o mesmo run; omitindo a nota de corte, `findings: []` seria lido como 'engine não achou nada'. Que caso o teste ainda não cobre? — Consumidores fora do serve que contam arrays no nível padrão, como o gate de seis lanes antes de 3816084. Como eu explicaria isso para outro pod? — 'O padrão é o veredito curto; se você conta linhas, peça full.'

### Próxima ação e encerramento

Ação: nota de aceite por desenho e da lição de consumidores. Owner a confirmar: Serve. Entrada: 3816084. Saída: nota. Encerramento: já encerrada.

<a id="item-300"></a>

## T-20260820-explain-stage-tool — T-20260820-explain-stage-tool.md

Frente: Serve / L3 Understand — legibilidade do diagnóstico (#88). Encaminhamento: encerrada_sem_aceite_formal_eval_b3_desconectado.

### Identidade e estado

`tasks/done/T-20260820-explain-stage-tool.md` (blob f1457987). 'Add explain_stage for drill-down', XS, standard, P2; owner `(none)`; depends_on detail-parameter. Estado `done`; `accepted: false` e `signed_off: false` por escolha registrada: o commit 9ff859b e o corpo da PR #88 dizem que esses bits pertencem a `taskspec gate --stamp`, 'which is not in this repo', e que marcá-los à mão anula seu propósito — portanto 'done sem aceite' é deliberado e não omissão. Pod provável: Pod 3/Serve (caminhos serve/; nenhum pod no arquivo).

### Intenção e benefício

Oferecer `explain_stage(job_id, stage_id)` com métricas, sintomas e findings de um stage, para que o usuário aprofunde sem pedir o run inteiro em `full`, e declarar 'stage não observado' em vez de sucesso vazio.

### Feito, faltante e não comprovado

Implementado (915cd2f): tool em `server.py:209-260` — devolve Diagnosis estreitado ao stage; stage ausente → `status="not_found"` com a lista de ids observados. Testes de comportamento existem: `test_explain_stage_narrows_to_the_one_stage` e `test_explain_stage_states_an_unobserved_stage` (`test_server_tools.py:256-295`). Divergência no eval: o eval_2 se descreve como 'a missing stage is stated, not silently empty' e declara verificar B-3, mas seu corpo é `! grep -n 'Five tools' src/apex_mcp/server.py` — não exercita B-3 (mesma classe que C04-17 aponta em L5/L6). O eval_1 também declara B-2 e só confere registro/anotação. O aceite de B-2/B-3 repousa nos testes acima, não nos evals.

### Linhagem

SERVE-LEGS L3 → l3-understand.yaml (approved: true) → specs dc1c2ce (autor 2026-08-20; commit 2026-08-26) → implementações no mesmo ramo → 9ff859b 'six units done' (status done, accepted false) → PR #88 integrada em 2026-09-14 (merge 1125cdb). Elo de processo ausente: verificação de que a descrição de cada eval corresponde ao seu corpo.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260820-explain-stage-tool.md; fontes/batch-revalidated-specs58-sources/history/T-20260820-explain-stage-tool.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__server.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_server_tools.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: explain_stage encontra/filtra stage e retorna not_found com IDs quando ausente; testes invocam tool. eval_1 verifica registro e eval_2 ausência de Five tools, sem discriminar B-2/B-3. RELATO: todos12evals verdes no histórico; não verificado aqui. O teste de estreitamento usa fixture com um único stage, por isso não demonstra exclusão de outro stage real.

### Fluxo

Fluxo observado: explain_stage(job, stage) → analyze(run inteiro) → stage encontrado: Diagnosis com stages/symptoms/findings só do stage, coverage do run ; não encontrado: status not_found + 'Observed stage id(s): [...]'.

### Consequências e risco

O caminho correto está presente e há testes de chamada. O eval declarado não protege o comportamento e o caso de estreitamento com um só stage não discrimina mistura entre stages. Isso é lacuna de controle, sem incidente funcional demonstrado.

### Alternativas e recomendação

Recomendado: manter encerrada e corrigir o mapeamento ao reutilizar o plano: eval_2 deve nomear `test_explain_stage_states_an_unobserved_stage`. Alternativa: registrar só a nota. Não refazer a tool.

### Dependências e paralelismo

Nenhuma dependência pendente: detail-parameter está entregue. A correção do mapeamento eval↔comportamento no plano l3-understand.yaml é documental, independente de ambiente e pode correr em paralelo com a mesma correção pedida por C04-17 para L5/L6.

### Plano e aceite propostos

Para reuso: (1) eval_2 → teste de stage ausente; (2) eval_1 → teste de estreitamento; (3) checagem de processo: comparar 'description' e corpo de cada eval. Esta spec: nota de aceite por desenho e da divergência.

### Comunicação entre responsáveis

Explicar a outro pod: 'explain_stage funciona e tem testes próprios para o stage estreitado e para o stage ausente; o eval que dizia provar o stage ausente só procurava a ausência de um texto no servidor, então seu verde não prova o comportamento.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Retornar sucesso vazio para stage desconhecido confundiria ausência de observação com stage saudável. Que caso o teste ainda não cobre? Run com dois stages, sintomas/findings distintos e pedido de um só, para detectar vazamento do outro; os evals também não invocam esses comportamentos. Como eu explicaria isso para outro pod? Há implementação e testes de chamada, mas o eval declarado verifica outro fato e a fixture precisa discriminar exclusão entre stages.

### Próxima ação e encerramento

Ação: registrar divergência eval↔descrição. Owner a confirmar: Serve. Entrada: spec e testes. Saída: nota e correção no plano se reutilizado. Encerramento: já encerrada.

