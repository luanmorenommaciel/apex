# Fichas documentais — lote 29

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-281"></a>

## T-20260923-screens-surface-query-failures — T-20260923-screens-surface-query-failures.md

Frente: Front / estados de falha honestos (#153). Encaminhamento: reconciliar_status_implementado_com_ajuste_posterior.

### Identidade e estado

`tasks/T-20260923-screens-surface-query-failures.md` (blob 52a23a46). 'Show a failed query on every screen, and name a rejected token', M, standard, P2; owner `(none)`; sem dependências. Estado `in-progress`, `accepted: false`. Pod provável: Pod 1/Front. Spec criada com status in-progress no commit 9841119362 (agmarcastro, 2026-09-29, 'close the eight serve-api leaves, add the two sweep manifests'), integrada pela PR #153 em 2026-10-06 (merge c9c35cf); nenhum commit posterior mudou o status.

### Intenção e benefício

Uma molécula `QueryFailure` renderizada pelas cinco telas antes de qualquer estado vazio: token rejeitado nomeia APEX_API_TOKEN, ApiError mostra o detail sanitizado, erro genérico vira linha fixa, a fonte nomeada segue repo.kind. Benefício: um token errado deixa de parecer 'Console conectada e vazia' e `memory_unavailable` deixa de parecer 'nada indexado'.

### Feito, faltante e não comprovado

Implementado (ad03572 em 2026-09-29, ajustado por d8c7cee em 2026-10-06 — 'render an API error's detail only when it is text'), ambos na #153: `QueryFailure.tsx` com ramos ApiAuthError/ApiError/genérico e rótulo por kind; `QueryFailure.test.tsx` com `it.each(SCREENS)` sobre as cinco telas (token, sem estado vazio no lugar), memory_unavailable, detail não-texto (422 do FastAPI), mensagem de erro genérico nunca no DOM, e 'nunca ClickHouse para http'. Contradiz a v2 'sem indício por grep'. VerifyScreen/useVerifyQuery não aparecem no histórico dos caminhos desta folha. Falta: status/aceite.

### Linhagem

useAsync sem leitura de error (4 telas) → plano serve-api-sweep:288 → spec 9841119362 → ad03572 → d8c7cee (guarda de detail não-texto, independente da ordem da #151) → #153 → spec in-progress. Elos ausentes: aceite formal; o eval_2 usa `git diff --exit-code` contra o worktree, que só discrimina antes do commit.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__T-20260923-screens-surface-query-failures.md; fontes/batch-revalidated-specs58-sources/history/T-20260923-screens-surface-query-failures.txt; fontes/batch-revalidated-specs58-sources/git/front__src__components__molecules__QueryFailure.tsx; fontes/batch-revalidated-specs58-sources/git/front__src__screens__QueryFailure.test.tsx; fontes/batch-revalidated-specs58-sources/public-captured-pulls.json. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

FATO OBSERVADO: molécula e testes que montam as cinco telas para token rejeitado, além de detail não-textual e segredo em Error genérico. RELATO: suíte front na #153. B-5 exige arquivos preservados e suítes próprias aprovadas: presença de testes não é prova durável, e git diff contra worktree após commit não compara o estado anterior à mudança. Essa obrigação requer diff entre refs identificados e recibo das suítes pertinentes.

### Fluxo

Fluxo observado: repo.method() rejeita → useAsync.error → tela renderiza <QueryFailure error kind> antes do estado vazio → ApiAuthError: aviso de token APEX_API_TOKEN; ApiError com detail string: status+detail; outro Error: linha fixa (mensagem nunca no DOM); rótulo de fonte = repo.kind.

### Consequências e risco

Implementação presente reduz a lacuna erro-vazio. ApiError.detail textual é exibido como texto, mas a proteção depende do contrato de erro de cada rota; a leitura da molécula não certifica sanitização universal do servidor. Falta prova durável de B-5 ligada aos refs.

### Alternativas e recomendação

Recomendado: done com nota (ad03572, d8c7cee). Alternativa: além de exibir detail, restringir a uma lista de códigos conhecidos (mais conservador, menos informativo). Não fundir com SourceState do VerifyScreen (anti-padrão declarado).

### Dependências e paralelismo

Sem dependência técnica pendente: ApiAuthError/ApiError existem em http.ts. Independente da ordem de #151 graças a d8c7cee. O fechamento corre em paralelo às demais folhas; a prova em navegador real das mesmas telas é a #172, separada.

### Plano e aceite propostos

Na nota de reconciliação, vincular ad03572/d8c7cee e o resultado histórico específico das suítes VerifyScreen, com refs comparados para os dois arquivos protegidos. Caso não localizados, registrar B-5 pendente. Manter os controles já presentes de erro não-textual e segredo genérico; somente preservar arquivos de teste não encerra a obrigação.

### Comunicação entre responsáveis

Explicar: 'As cinco telas já mostram falha em vez de vazio, nomeando o token quando a API recusa (ad03572/d8c7cee, #153). A spec só não foi fechada.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Resolver a rejeição para [] dentro de useAsync faria um token errado parecer uma Console vazia de novo. Que caso o teste ainda não cobre? — Um ApiError cujo detail textual contenha dado vindo do job observado, que seria exibido como texto. Como eu explicaria isso para outro pod? — 'Falha e vazio têm telas diferentes; e a Console nunca imprime a mensagem de um erro genérico porque ela pode trazer o corpo de uma resposta.'

### Próxima ação e encerramento

Ação: reconciliar implementação e registrar limite de B-5. Owner a confirmar: Front. Entrada: commits, diff de refs e recibos específicos. Saída: nota documental com lacuna explícita se a prova faltar. done e accepted são distintos; não aceitar pela simples existência dos testes.

<a id="item-282"></a>

## T-20260929-console-parity-live-gate — T-20260929-console-parity-live-gate.md

Frente: Serve / gate live de paridade (#153, #159). Encaminhamento: reconciliar_status_com_recibo_live_e_continuidade_em_159.

### Identidade e estado

`tasks/T-20260929-console-parity-live-gate.md` (blob 15dfceaf). 'Make RUNBOOK step 3 prove the console's rows against a live store', M, standard, P2; owner `(none)`; depends_on wire-timestamp-format (entregue). Estado `in-progress`, `accepted: false`. Pod provável: Pod 3/Serve. Spec criada com status in-progress no commit 9841119362 (agmarcastro, 2026-09-29, 'close the eight serve-api leaves, add the two sweep manifests'), integrada pela PR #153 em 2026-10-06 (merge c9c35cf); nenhum commit posterior mudou o status. Plano tasks/.plans/serve-api-wire.yaml:93.

### Intenção e benefício

Um comando no RUNBOOK passo 3 que emite cada declaração da Console duas vezes (ClickHouse HTTP como apex_ro, e pela API em processo) e falha se as linhas diferirem, mais quatro comportamentos que só um store real mostra, com dados semeados e removidos pelo próprio gate e modo `--job-id` sem escrita que imprime NOT EXERCISED. Benefício: prova de conteúdo que um status 200 não dá.

### Feito, faltante e não comprovado

Implementado (35acb47, #153): `serve/tools/console_parity_gate.py` e `test_console_parity_gate.py` (8 casos offline, segundo VALIDATION: lê as declarações como escritas, coerção numérica, coluna faltante reportada, check não exercitado nunca é pass, usuário privilegiado anula a prova read-only); RUNBOOK passo 3 nomeia o comando, apex_ro e NOT EXERCISED (`RUNBOOK.md:141-173`). Recibo live registrado: VALIDATION 'console_parity_gate.py — live ClickHouse 24.8, CONSOLE_PARITY_GATE=PASS' e corpo da #153 '17/17 seeded ... --job-id --api-url on three real jobs'. Continuação aberta fora deste SHA: PR #159 (diagnóstico de deriva e limpeza de linhas derivadas da fixture, segundo a ficha Codex). Falta: aceite formal.

### Linhagem

RUNBOOK passo 3 (só status) → plano serve-api-wire:93 → spec 9841119362 → 35acb47 → recibo live local → #153 (2026-10-06) → #159 aberta (base c4541a5, ainda não integrada). Elos ausentes: aceite; integração da #159 se escolhida.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__T-20260929-console-parity-live-gate.md; fontes/batch-revalidated-specs58-sources/history/T-20260929-console-parity-live-gate.txt; fontes/batch-revalidated-specs58-sources/git/serve__tools__console_parity_gate.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_console_parity_gate.py; fontes/batch-revalidated-specs58-sources/git/serve__VALIDATION.md; fontes/batch-revalidated-specs58-sources/public-captured-pulls.json. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: o gate separa PASS/FAIL/NOT EXERCISED e os testes exercitam essa distinção. RELATO: VALIDATION de29/09 registra17/17 seeded em container descartável ClickHouse24.8, explicitamente não stack durável; #153 relata infra stack e três jobs reais em06/10. Não fundir os escopos nem chamar o corpo de PR de execução reproduzida. eval_3 exige live. A limpeza remove tabelas enumeradas por IDs/fingerprint, sem provar que toda derivação foi removida.

### Fluxo

Fluxo observado estaticamente: gate → lê declarações de front/src/data/queries.ts → (a) ClickHouse HTTP como apex_ro, (b) create_app() sobre ReadStore real em processo → normalização wire → compara linhas por declaração → 4 checks live (sentinela não indexado, rollups como readonly, ordem de findings, colapso de transições) → semeia/limpa só ids com sufixo aleatório; `--job-id`: nada escreve, NOT EXERCISED não conta.

### Consequências e risco

Sem ação: a spec segue in-progress com recibo existente. Limites: modo semeado escreve no store (por isso o modo `--job-id`); se a limpeza deixar linhas derivadas (motivação da #159), reuso do ambiente pode ser afetado — relato, não observado. Confiança alta no código; média no recibo.

### Alternativas e recomendação

Reconciliar implementação com35acb47 e a prova live exigida por eval_3, preservando data, SHA, ambiente e checks não exercitados em cada recibo. A continuação #159 deve ser examinada no seu próprio recorte; uma promessa de melhoria não substitui decisão sobre os limites do gate atual. accepted é separado de done.

### Dependências e paralelismo

Depende de wire-timestamp-format (entregue). A #159 é paralela e não bloqueia o fechamento documental. Execução live nova depende de ambiente autorizado.

### Plano e aceite propostos

Passos: (1) nota de fechamento com recibo; (2) revisão própria da #159 (diff, limpeza, limites de ids/tabelas); (3) controles existentes: NOT EXERCISED nunca é pass; privilégio do usuário do navegador anula a prova; (4) negativo desejável já citado pela #159: resíduo após limpeza deve falhar o gate. Doc: VALIDATION já registra.

### Comunicação entre responsáveis

Explicar: o gate e seus controles offline existem; registros históricos distintos descrevem seeded29/09 e jobs reais06/10. Cada check não exercitado continua sem prova, mesmo que o processo termine sem falhas. A limpeza e a continuação #159 devem manter seus limites explícitos.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Comparando só status HTTP, as três rotas com projeção errada teriam passado de novo; restando a SQL da Console no gate em vez de lê-la de queries.ts, o gate compararia algo que a Console não envia. Que caso o teste ainda não cobre? — Linhas derivadas da fixture que sobrevivem à limpeza e contaminam a próxima execução (motivo da #159). Como eu explicaria isso para outro pod? — 'O gate envia a mesma pergunta pelas duas portas e exige a mesma resposta; um check que os dados não exercitam aparece como NOT EXERCISED, nunca como verde.'

### Próxima ação e encerramento

Ação: reconciliar status com prova live identificada e encaminhar #159 para revisão própria. Owner a confirmar: Serve/acceptor. Entrada:35acb47, VALIDATION e snapshot da PR. Saída: nota com ambiente/cobertura por recibo; encerramento funcional depende da aceitação da prova, não do movimento do arquivo.

<a id="item-283"></a>

## T-20260929-wire-timestamp-format — T-20260929-wire-timestamp-format.md

Frente: Serve+Front / contrato de tempo (#153). Encaminhamento: reconciliar_status_implementado_e_ratificar_precisao.

### Identidade e estado

`tasks/T-20260929-wire-timestamp-format.md` (blob 30596c24). 'Return timestamps in one format, the API's, from every data source', M, standard, P2; owner `(none)`; sem dependências. Estado `in-progress`, `accepted: false`. Pods prováveis: Pod 3/Serve e Pod 1/Front (caminhos serve/ e front/); nenhum pod no arquivo. Spec criada com status in-progress no commit 9841119362 (agmarcastro, 2026-09-29, 'close the eight serve-api leaves, add the two sweep manifests'), integrada pela PR #153 em 2026-10-06 (merge c9c35cf); nenhum commit posterior mudou o status. Plano tasks/.plans/serve-api-wire.yaml:13.

### Intenção e benefício

Uma só forma de timestamp na fronteira — ISO 8601 com T, UTC, milissegundos fixos, sem offset (`2026-09-20T10:00:00.123`) — emitida de propósito pela API e devolvida igual pelos três repositórios da Console. Benefício: uma tela não consegue distinguir de que porta veio um horário, e um valor com offset não perde duas horas silenciosamente.

### Feito, faltante e não comprovado

Implementado (f080ce3, #153): `serve/src/apex_api/wire.py` e `test_api_wire.py` criados; teste `test_every_timestamp_leaves_in_the_wire_format` lê `WIRE_TIMESTAMP` de `front/src/data/timestamp.ts` e exercita datetime com/sem fração, aware +02:00 e texto do ClickHouse (`test_api_resources.py:282-330`); `timestamp.ts` e `timestamp.test.ts` no front. Também `/health` passa por `wire()` (`app.py:171`). A decisão do dono (formato da API é o alvo) está registrada na spec com data 2026-09-29; o refinamento 'milissegundos sempre' era proposta aberta e o corpo da #153 lista essa escolha em 'Open'. Falta: status/aceite e ratificação da precisão.

### Linhagem

Achado da varredura da #129 → decisão do dono 2026-09-29 → plano serve-api-wire:13 → spec 9841119362 → f080ce3 → #153 → spec in-progress. Elos ausentes: ratificação da precisão fixa; aceite formal.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__T-20260929-wire-timestamp-format.md; fontes/batch-revalidated-specs58-sources/history/T-20260929-wire-timestamp-format.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_api__wire.py; fontes/batch-revalidated-specs58-sources/git/front__src__data__timestamp.ts; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_api_wire.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_api_resources.py; fontes/batch-revalidated-specs58-sources/public-captured-pulls.json. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

FATO OBSERVADO: normalizador nos dois hosts e teste que amarra um ao outro pela regex declarada no TypeScript. RELATO: suítes verdes (corpo #153, local). INFERÊNCIA: evals 1–4 satisfeitos; eval_5 usa `git diff --exit-code -- src/apex_mcp`, que só discrimina antes do commit. DECISÃO PENDENTE de ratificação: precisão fixa em ms vs largura variável. Nenhuma execução nesta revisão.

### Fluxo

Fluxo observado: ReadStore (datetimes, intocado) → rota de recurso → wire() → strings 'YYYY-MM-DDTHH:MM:SS.mmm' UTC só sob chaves de timestamp conhecidas → JSON; navegador: ClickHouse JSON 'YYYY-MM-DD HH:MM:SS.mmm' → mapper do repositório → toWireTimestamp → mesma forma; fixtures normalizadas na saída.

### Consequências e risco

Normalizadores cobrem os formatos válidos do contrato e preservam textos fora do padrão. Limite observado: no TypeScript, ramo sem zona retorna diretamente date/time normalizados, enquanto Python valida datetime.fromisoformat; uma string como2026-13-45 99:99:99 poderia ser transformada no front e preservada na API. Inferência estática, não reproduzida; isso limita a afirmação geral de equivalência para entradas inválidas.

### Alternativas e recomendação

Recomendado: done com nota (f080ce3) e decisão explícita do dono sobre a precisão fixa (já implementada). Alternativa: largura variável como `isoformat()` — a spec chama isso de 'emular um acidente'. Não converter em ReadStore (as tools MCP fazem aritmética com datetimes).

### Dependências e paralelismo

Sem dependência técnica pendente. console-parity-live-gate depende desta e está entregue. A ratificação da precisão é decisão humana em paralelo.

### Plano e aceite propostos

Preparar nota comf080ce3, ratificação da precisão e recibos de suítes. Para preservar B-6, comparar refs definidos e vincular resultados MCP/diagnóstico; git diff limpo do worktree é insuficiente. Caso discriminante proposto: a mesma data inválida com formato reconhecível atravessando ambos os normalizadores e permanecendo verbatim.

### Comunicação entre responsáveis

Explicar: 'Todo timestamp sai da API e dos três repositórios no mesmo formato desde f080ce3 (#153), e um teste lê o padrão do TypeScript. Falta o dono confirmar a precisão fixa em milissegundos.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Converter no ReadStore troca datetimes por strings onde MCP faz aritmética; descartar offset desloca o instante. Que caso o teste ainda não cobre? Equivalência entre os normalizadores para uma data inválida sem zona: o ramo TypeScript pode reformatá-la enquanto Python a preserva. Como eu explicaria isso para outro pod? A API e o front compartilham um formato, mas a equivalência deve ser aferida também nas fronteiras do domínio válido.

### Próxima ação e encerramento

Ação: reconciliar implementação, ratificar precisão e registrar caso inválido como limite a decidir. Owner a confirmar: Serve+Front. Entrada:f080ce3, testes e registros históricos. Saída: nota comdone separado deaccepted; encerramento exige evidência e responsável, sem novo aceite desta auditoria.

<a id="item-284"></a>

## T-20261006-console-e2e-reflection — T-20261006-console-e2e-reflection.md

Frente: Console / prova integrada e DEV (#153). Encaminhamento: reconciliar_status_com_recibo_live_e_limite_de_browser_real.

### Identidade e estado

`tasks/T-20261006-console-e2e-reflection.md` (blob dff61c38). 'Prove one real job from the Spark plugin to every console screen', M, standard, P2; owner `(none)`; sem dependências. Estado `in-progress`, `accepted: false`. Pods prováveis: Pod 1/Front, Pod 3/Serve e DEV. Criada no mesmo commit da implementação (eb449cb, agmarcastro, 2026-10-06), integrada pela #153. Plano tasks/.plans/serve-api-e2e.yaml:12 — arquivo que o PyYAML rejeita na linha 101 (Codex C04-06); a spec em si é válida.

### Intenção e benefício

Um quarto ponto de entrada e2e que pega um job no store, roda engine e memory como um operador, sobe a apex-api, prova as linhas pelas duas portas e monta o App REAL contra a API lendo cada tela — recusando NaN, undefined, [object Object], Infinity e avisos de falha, e exigindo que as contagens da tela sejam as da API. Benefício: pela primeira vez, a cadeia Spark→…→tela foi exercitada.

### Feito, faltante e não comprovado

Implementado (eb449cb): `tests/e2e/console_reflection.sh` (recusa sem job_id com uso/exit 2; mata a API pela porta), `front/src/e2e/console.live.test.tsx` com `describe.skipIf(!LIVE)` e lista de invariantes (linhas 50-56); RUNBOOK/VALIDATION/CHANGELOG/docs/e2e atualizados. Recibo relatado: 'End to end — one job to every screen, recorded 2026-10-06' em VALIDATION e no corpo da #153 (três jobs, dois gerados e um de julho). Limite (concordo com a ficha Codex do plano): o App é montado em teste com MemoryRouter e fetch real em Node — não é imagem nginx nem navegador real. Falta: aceite formal.

### Linhagem

docs/e2e/README (três entradas sem Console) → spec+implementação eb449cb → recibo local 2026-10-06 → #153 → spec in-progress. Elos ausentes: aceite; prova de navegador real e imagem (#172); YAML do plano inválido para reuso.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__T-20261006-console-e2e-reflection.md; fontes/batch-revalidated-specs58-sources/history/T-20261006-console-e2e-reflection.txt; fontes/batch-revalidated-specs58-sources/git/tests__e2e__console_reflection.sh; fontes/batch-revalidated-specs58-sources/git/front__src__e2e__console.live.test.tsx; fontes/batch-revalidated-specs58-sources/git/serve__VALIDATION.md. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

FATO OBSERVADO: orquestrador, teste live com skip declarado, invariantes. RELATO HISTÓRICO: verde em três jobs (local, autor); 'With the current jar the no-op gate fires on screen'. INFERÊNCIA: eval_1 depende de `vitest` relatar 'skipped' (grep na saída); eval_2 prova recusa sem argumento; eval_3 é live. Sem execução. Não é CI, nem browser real, nem aceite humano.

### Fluxo

Fluxo relatado e observado no código: job_id → engine (findings determinísticos, llm_calls 0) → memory index → apex-api (health store ok) → console_parity_gate --job-id → vitest live: App + RepositoryProvider + MemoryRouter + HttpRepository real (fetch Node) → leitura de cada tela → invariantes → PASS/FAIL por etapa; job sem job_conf → WARN.

### Consequências e risco

App real montado em jsdom e HTTP real estão presentes; recibo histórico descreve três jobs. Não há prova de navegador/nginx nesta folha. Limite adicional observado: o último teste usa shapes.length global para decidir se o job atual foi indexado; shapes de outro job podem tornar inválida essa inferência. A execução live continua distinta da leitura documental.

### Alternativas e recomendação

Reconciliar implementação e recibo live obrigatório de eval_3 com SHA, ambiente e cobertura. Ratificar o escopo jsdom e registrar a prova de navegador separada. done registra implementação; accepted requer responsável e evidência vinculada.

### Dependências e paralelismo

Sem dependência técnica declarada. O exit check inclui eval_3 live: o recibo de06/10 pode instruir a aceitação quando identificado e julgado pelo acceptor; não é dispensado por esta auditoria. A pendência de navegador tem escopo próprio.

### Plano e aceite propostos

Vincular o recibo de06/10 e registrar checks NOT EXERCISED. Conferir o job do recibo e o objeto aceito. Caso adicional proposto: /plans contém somente shapes de outro job e o job atual não está indexado; o teste de sentinela deve decidir pelo job, não pela existência global de shapes.

### Comunicação entre responsáveis

Explicar: 'Um job real já foi do plugin Spark até cada tela da Console em teste montado (eb449cb, 2026-10-06). Isso não é o navegador nem a imagem nginx; essa prova é a #172.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Simulando qualquer porta no teste live, a cadeia deixaria de provar que a tela mostra o que o job fez; passando quando as variáveis faltam, um 'verde' sem execução entraria nos recibos. Que caso o teste ainda não cobre? — O navegador real com nginx, /config.js e token, e um job sem job_conf além do WARN. Como eu explicaria isso para outro pod? — 'É a primeira prova de ponta a ponta até a tela, feita com o App montado em teste; a prova em navegador é outra etapa.'

### Próxima ação e encerramento

Ação: reconciliar estado e prova terminal obrigatória. Owner a confirmar: Front+Serve+DEV/acceptor. Entrada:eb449cb e VALIDATION com contexto. Saída: nota com garantia jsdom e limites. Encerramento: avaliação explícita do recibo live; movimento de arquivo não equivale a aceite.

<a id="item-285"></a>

## T-20261006-dev-c3-driver-host — T-20261006-dev-c3-driver-host.md

Frente: DEV / overlay C3-C4 (#153). Encaminhamento: reconciliar_status_implementado_eval_make_n_nao_isolado.

### Identidade e estado

`tasks/T-20261006-dev-c3-driver-host.md` (blob 478cb672). 'Advertise the Spark driver by service name on the C3 overlay', XS, standard, P2; owner `(none)`; sem dependências. Estado `in-progress`, `accepted: false`. Pod provável: DEV/Package (caminhos dev/ e tests/e2e/). Criada no mesmo commit da implementação (7fa7ea5, agmarcastro, 2026-10-06), integrada pela #153. Plano tasks/.plans/serve-api-e2e.yaml:110 (YAML inválido na linha 101).

### Intenção e benefício

Fazer todo submit C3/C4 do Makefile de dev e o de tests/e2e/run.sh passar `spark.driver.host=spark-master` e `spark.driver.bindAddress=0.0.0.0`, como `e2e_canonical.sh` já fazia, para que executores não sejam recusados por o driver anunciar o endereço de uma rede e escutar em outra.

### Feito, faltante e não comprovado

Implementado (7fa7ea5): `C3_DRIVER_CONF` em `dev/Makefile:91` com as duas confs e uso nos alvos c3-plugin-skew/c4-aqe-skew/c4-aqe-skewsplit/c4-aqe-probe (linhas 96-123), e `tests/e2e/run.sh:87`. Relato na spec: reproduzido em 2026-10-06, passou em 25 s com as confs. Limite do eval: `make -n` no `dev/Makefile` não é isolado — a linha 7 avalia `$(shell docker network inspect apex-collect-net ...)` na expansão (concordo com Codex C04-15); é leitura do daemon, não escrita, mas exige Docker. Falta: aceite formal.

### Linhagem

Falha intermitente observada em 2026-10-06 (relato) → spec + correção 7fa7ea5 → #153 → spec in-progress. Elos ausentes: aceite; teste que não dependa de `make -n`.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__T-20261006-dev-c3-driver-host.md; fontes/batch-revalidated-specs58-sources/history/T-20261006-dev-c3-driver-host.txt; fontes/batch-revalidated-specs58-sources/git/dev__Makefile; fontes/batch-revalidated-specs58-sources/git/tests__e2e__run.sh. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: C3_DRIVER_CONF contém host e bindAddress e é usado nos quatro submits; run.sh repete as duas confs. OBSERVADO: expansão imediata de docker network inspect na linha7 mesmo em make -n. RELATO:25s e reprodução de06/10 na spec/histórico. Não executados make, Docker ou shell de produto; a satisfação do eval é inferência textual.

### Fluxo

Fluxo observado: make c3-*/c4-* → c3-up (overlay com duas redes) → spark-submit com C3_DRIVER_CONF → driver anuncia spark-master e escuta em 0.0.0.0 → executores conectam. Sem a conf: hostname do container resolve para uma rede, RPC escuta na primeira interface → recusa → 'Initial job has not accepted any resources'.

### Consequências e risco

Sem ação: nenhuma regressão. Risco de processo: reutilizar o eval com `make -n` como se fosse puramente estático. Anti-padrão declarado correto: não colocar driver.host em spark-defaults (quebra execuções locais). Confiança alta.

### Alternativas e recomendação

Recomendado: done com nota (7fa7ea5) e registro de que o eval usa Docker na expansão. Alternativa para reuso: teste que leia o texto do Makefile e verifique que cada alvo C3/C4 referencia `C3_DRIVER_CONF` — estático e sem Docker. Reversível.

### Dependências e paralelismo

Sem dependência de outras specs; só da topologia C3/C4 do dev. Independente das folhas da Console e de decisões de produto. O fechamento documental e a troca do eval por leitura estática podem correr em paralelo a tudo; nova reprodução runtime exige Docker autorizado.

### Plano e aceite propostos

Passos: (1) nota de fechamento; (2) para reuso, trocar `make -n` por leitura estática do Makefile; (3) controle negativo: remover a conf de um alvo deve falhar o teste estático; (4) prova runtime fica como relato de 2026-10-06. Doc: comentário no Makefile já explica.

### Comunicação entre responsáveis

Explicar: 'Os submits C3/C4 e o run.sh já anunciam o driver pelo nome do serviço (7fa7ea5, #153), como o e2e canônico. O eval usa make -n, que neste Makefile chama docker na expansão.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Com driver.host em spark-defaults.conf, execuções locais como fp-test anunciariam um spark-master inexistente; sem a conf nos alvos C3/C4, executores voltariam a ser recusados de forma intermitente conforme a ordem das interfaces. Que caso o teste ainda não cobre? — Um alvo C3/C4 novo que não use C3_DRIVER_CONF, já que o eval lista quatro nomes fixos. Como eu explicaria isso para outro pod? — 'Com duas redes, o driver precisa anunciar um nome que todos resolvem e escutar em todas as interfaces; senão o job fica esperando recursos para sempre.'

### Próxima ação e encerramento

Ação: reconciliar implementação e limite do eval. Owner a confirmar: DEV. Entrada:7fa7ea5 e trechos preservados. Saída: nota de status com evidência e responsável. done e accepted são atos distintos; esta auditoria não move nem aceita a spec.

<a id="item-286"></a>

## T-20261006-six-lane-gate-full-detail — T-20261006-six-lane-gate-full-detail.md

Frente: Console / prova integrada e DEV (#153). Encaminhamento: reconciliar_status_implementado_com_teste_que_fixa_argumentos.

### Identidade e estado

`tasks/T-20261006-six-lane-gate-full-detail.md` (blob de1f50c9). 'Ask analyze_run for the full diagnosis in the canonical gate', XS, standard, P2; owner `(none)`; sem dependências. Estado `in-progress`, `accepted: false`. Pods prováveis: Pod 3/Serve e gate raiz. Criada no commit da correção (3816084, 2026-10-06) e tocada de novo em eb449cb; integrada pela #153. Plano tasks/.plans/serve-api-e2e.yaml:70 (YAML inválido na linha 101).

### Intenção e benefício

Fazer o probe MCP do gate canônico de seis lanes pedir `detail: full`, porque desde L3 (2026-08-20) o default `summary` corta stages e findings para lista vazia e o gate comparava a lista cortada como se fosse o todo, falhando todo job com `mcp_stage_count_mismatch 0 != N`.

### Feito, faltante e não comprovado

Implementado (3816084): `ANALYZE_RUN_ARGUMENTS = {"detail": "full"}` em `scripts/e2e_six_lanes.py:172-176` com comentário do motivo; teste `test_live_probe_asks_analyze_run_for_the_full_diagnosis` (`tests/test_e2e_six_lanes.py:262-307`) falsifica os módulos do cliente MCP e afirma `calls == [("analyze_run", {"job_id": "j", "detail": "full"})]` — controle discriminante de B-1. B-2 é live: relato de passar em dois jobs gerados com a correção e falhar sem ela (spec e corpo #153). Falta: aceite formal.

### Linhagem

L3 muda default de analyze_run (#88, 2026-08-20/09-14) → gate tocado pela última vez em 2026-08-19 → falha observada em 2026-10-06 → 3816084 → #153 → spec in-progress. Elo histórico ausente: nenhum teste ligava o gate ao default de L3 por seis semanas (CI não roda o gate live).

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__T-20261006-six-lane-gate-full-detail.md; fontes/batch-revalidated-specs58-sources/history/T-20261006-six-lane-gate-full-detail.txt; fontes/batch-revalidated-specs58-sources/git/scripts__e2e_six_lanes.py; fontes/batch-revalidated-specs58-sources/git/tests__test_e2e_six_lanes.py; fontes/batch-revalidated-specs58-sources/git/serve__VALIDATION.md. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: ANALYZE_RUN_ARGUMENTS e call_tool incluem detail full; o teste compara exatamente os argumentos. O fake responde stages/findings vazios e não prova a semântica de full nem contagens reais. RELATO: recibos06/10 no histórico/VALIDATION. eval_2 requer ambiente live; não executado nesta auditoria.

### Fluxo

Fluxo observado: e2e_six_lanes → engine (persiste findings, idempotente) → live_mcp_probe → stdio MCP analyze_run(job_id, detail=full) → Diagnosis com stages/findings completos → compara stage_count e finding_count com ClickHouse/engine → status passed/failed.

### Consequências e risco

Sem ação: nenhuma regressão. Lição de processo: uma mudança de default numa lane (L3) quebrou um gate de outra sem teste ligando-as; o teste novo cobre só o argumento. Confiança alta.

### Alternativas e recomendação

Reconciliar3816084 com a prova live obrigatória de eval_2, identificando SHA, jobs e ambiente do recibo histórico. Preservar distinção entre argumento controlado offline e igualdade de contagens live. Não aceitar lista vazia para afrouxar o gate.

### Dependências e paralelismo

Sem dependência de outras specs; depende só do default de detail definido em L3 (#88). Prova live depende de ambiente infra autorizado e de job analisado. O fechamento documental e o teste em processo opcional podem correr em paralelo às demais folhas.

### Plano e aceite propostos

Passos: (1) nota de fechamento; (2) opcional: teste em processo do probe contra create_server com FakeClient (stages e findings não vazios); (3) controle negativo existente: argumento diferente de full falha o teste; (4) recibo live existente. Doc: comentário no gate já explica.

### Comunicação entre responsáveis

Explicar: 'O gate de seis lanes falhava todo job porque pedia o resumo cortado; agora pede detail=full e um teste fixa isso (3816084, #153).'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Aceitando lista vazia no gate, um run cortado pelo resumo passaria como se não tivesse stages, escondendo divergência real entre engine e MCP. Que caso o teste ainda não cobre? — Uma mudança futura na semântica de `full` no servidor (por exemplo, limite de linhas), já que o teste só fixa o argumento enviado. Como eu explicaria isso para outro pod? — 'Quando você muda um default numa tool, procure quem compara a saída dela; o gate de seis lanes confiava no default antigo.'

### Próxima ação e encerramento

Ação: reconciliar implementação e prova live exigida. Owner a confirmar: dono do gate/Serve e acceptor. Entrada:3816084, teste e recibo identificado. Saída: nota com escopo e decisão responsável; movimento para done não constitui aceitação.

<a id="item-287"></a>

## T-20260819-auto-baseline — T-20260819-auto-baseline.md

Frente: Serve / L2 Discover — descoberta de runs (#83). Encaminhamento: encerrada_com_limite_de_janela_e_ordem_temporal_nao_testado.

### Identidade e estado

`tasks/done/T-20260819-auto-baseline.md` (blob fd8cab3d). 'Let compare_runs pick its own baseline', M, standard, P2; owner `(none)`; depends_on runs-resource. Estado: `done`, `accepted: true` em 2026-08-19T17:55:41Z, aceite registrado no arquivo por `sidymar` via taskspec accept (autor da implementação; não é revisão independente nem nova autorização). Pod provável: Pod 3/Serve (caminhos serve/ e docs/lanes; nenhum pod no arquivo).

### Intenção e benefício

Tornar `baseline_job_id` opcional em compare_runs, escolhendo o run anterior mais recente do mesmo app_name com o mesmo plan_fingerprint, e recusar (em vez de adivinhar) quando não houver — comparar através de uma mudança de plano mede o plano, não a regressão.

### Feito, faltante e não comprovado

Implementado: `diagnose.select_baseline` (`diagnose.py:1798-1840`) e a ligação em compare_runs (`server.py:324-344`), com nota de seleção/recusa e status `not_comparable`. Testes `test_auto_baseline_picks_same_fingerprint`, `..._refuses_across_plan_change`, `test_explicit_baseline_is_unchanged` (`test_diagnose.py:587-625`) — exercitam a função pura com candidatos fornecidos. Não coberto por teste (leitura): os candidatos vêm de `store.runs(app_name, limit=10)` com janela padrão de 168 h e ordenados por last_ts; o código exclui só o próprio job_id, então 'anterior' não é imposto — ao comparar um run que não é o mais novo, pode ser escolhido um run posterior; e a recusa diz 'no prior run ... shares its plan shape' mesmo quando o par existe fora da janela de 7 dias/10 candidatos. Inferências estáticas, sem incidente observado.

### Linhagem

SERVE-LEGS L2 → tasks/.plans/l2-discover.yaml (approved: true) → spec d244af7 (2026-08-19) → implementação 8732ac5 com accepted:true → done 692cd6a → Duplicatas regeneradas em tasks/ (ready/false) por aab2988 e removidas por f504255 no mesmo dia; a cópia em tasks/done/ é o objeto que chegou a c3c3ea3 → PR #83 integrada (merge e10ab85, 2026-08-20 UTC). Elos ausentes: teste da ligação servidor↔janela/ordem; nenhuma issue posterior sobre isso localizada.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260819-auto-baseline.md; fontes/batch-revalidated-specs58-sources/history/T-20260819-auto-baseline.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__diagnose.py; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__server.py; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__ch.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_diagnose.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: seleção recebe candidatos ordenados e só exclui o próprio job; nenhuma comparação temporal impõe prior. A ligação solicita store.runs limit10 e herda since_hours168. O teste de baseline explícito chama diagnose.compare, portanto cobre a função pura e não a passagem pelo servidor. RELATOS históricos de suíte/aceite não foram reproduzidos. B-1 temporal permanece lacuna inferida estaticamente, sem incidente observado.

### Fluxo

Fluxo observado: compare_runs(current, baseline vazio) → stages(current) → app_name da primeira linha → runs(app_name, limit=10, since 168h) → stages de cada candidato → select_baseline (mesmo conjunto de fingerprints) → baseline + nota | not_comparable + nota → compare().

### Consequências e risco

O caminho observado escolhe o primeiro candidato com conjunto idêntico de fingerprints; não certifica B-1 para todo run, nem mesmo o mais novo quando o par está fora da janela/limite. Há risco de selecionar candidato posterior ao atual ou de texto de recusa amplo demais. A ficha mantém a entrega histórica encerrada e propõe robustez separada, sem novo aceite.

### Alternativas e recomendação

Recomendado: manter encerrada e abrir item pequeno de robustez: filtrar candidatos por last_ts < first_ts do atual e citar a janela na nota de recusa. Alternativa: documentar o limite na docstring sem mudar código. Não trocar recusa por fallback ao run mais recente (anti-padrão).

### Dependências e paralelismo

Nenhuma dependência para permanecer encerrada. O item de robustez independe de outras specs e de ClickHouse (testável com FakeClient). Pode correr em paralelo a qualquer frente.

### Plano e aceite propostos

Para o item novo: (1) teste no nível do servidor com FakeClient: atual mais antigo que um candidato com mesmo shape → não escolher o posterior; (2) teste: par fora da janela → nota menciona 7 dias; (3) controle negativo: remover o filtro temporal faz o teste falhar; (4) doc na docstring de compare_runs. Esta spec: nenhuma ação.

### Comunicação entre responsáveis

Explicar: 'compare_runs escolhe o baseline sozinho desde #83 e recusa quando o plano mudou. Dois limites não testados: ele não impede escolher um run posterior e a recusa ignora que a busca olha só 7 dias e 10 runs.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Com fallback para o run mais recente de qualquer plano, a comparação mediria a mudança de plano e afirmaria uma regressão falsa com confiança. Que caso o teste ainda não cobre? — Analisar um run antigo quando existe um run mais novo com o mesmo shape, e um par válido com mais de 7 dias. Como eu explicaria isso para outro pod? — 'O baseline automático é o run mais recente do mesmo app e plano dentro de uma janela; fora dela, passe o baseline explícito.'

### Próxima ação e encerramento

Ação: manter encerrada e propor item de robustez. Owner a confirmar: Serve. Entrada: server.py:324-344 e diagnose.select_baseline. Saída: item com dois testes ou nota documental. Encerramento: limite documentado ou corrigido com teste.

<a id="item-288"></a>

## T-20260819-discover-docs — T-20260819-discover-docs.md

Frente: Serve / L2 Discover — descoberta de runs (#83). Encaminhamento: encerrada_historica_documentos_atuais_seguem_reconciliacao.

### Identidade e estado

`tasks/done/T-20260819-discover-docs.md` (blob 2d333ed2). 'Document run discovery across the lane docs', M, standard, P2; owner `(none)`; depends_on runs-gates. Estado `done`, `accepted: true` em 2026-08-19T19:15:05Z, aceite registrado no arquivo por `sidymar` via taskspec accept (autor da implementação; não é revisão independente nem nova autorização). Pod provável: Pod 3/Serve (caminhos serve/ e docs/lanes; nenhum pod no arquivo). Eval reescrito por aab2988 para não sair do próprio raio (SERVE.md virou unidade separada).

### Intenção e benefício

Refletir a quinta tool (list_runs), o primeiro recurso e o auto-baseline em README, VALIDATION e SERVE-LEGS, registrando por que uma tool filtrada substituiu find_run/latest_run. Benefício: documentos coerentes com o código naquele momento.

### Feito, faltante e não comprovado

Feito em f504255 (2026-08-19): README ganhou list_runs, apex://runs e a seção 'Finding a run'; VALIDATION ganhou '## L2 — run discovery, recorded 2026-08-19' (`VALIDATION.md:146-195`) com gates e os dois defeitos que só o banco real achou; SERVE-LEGS marcou L2 entregue com a decisão de uma tool. Estado atual: esses documentos foram reescritos depois (L3/L5/L6/#129/#132) e hoje têm deriva própria — README com título 'The six tools' e prosa 'eight tools'. A seção histórica L2 do VALIDATION está preservada. Não comprovado aqui: o 'test count copiado de execução' (eval_2) — o VALIDATION tem várias contagens por leg.

### Linhagem

SERVE-LEGS L2 → tasks/.plans/l2-discover.yaml (approved: true) → spec d244af7 (2026-08-19) → implementação f504255 com accepted:true → done e4f398e → Duplicatas regeneradas em tasks/ (ready/false) por aab2988 e removidas por f504255 no mesmo dia; a cópia em tasks/done/ é o objeto que chegou a c3c3ea3 → PR #83 integrada (merge e10ab85, 2026-08-20 UTC). Elo posterior: reconciliações documentais de #132; deriva atual registrada na ficha de four-to-five-doc-ripple do lote anterior.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260819-discover-docs.md; fontes/batch-revalidated-specs58-sources/history/T-20260819-discover-docs.txt; fontes/batch-revalidated-specs58-sources/git/serve__README.md; fontes/batch-revalidated-specs58-sources/git/serve__VALIDATION.md; fontes/batch-revalidated-specs58-sources/git/docs__lanes__SERVE-LEGS.md. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: README preserva Finding a run e recurso; título six tools diverge da prosa/tabela de oito. VALIDATION mantém L2 datada com123passed e relato de dois defeitos live. eval_2 procura a contagem em qualquer lugar do diário e não amarra seção ou SHA; sem pipefail, grep também pode ocultar saída não-zero de pytest. Portanto não é possível afirmar que falharia hoje só porque a suíte cresceu; a ausência de vínculo torna o controle fraco. Nada executado.

### Fluxo

Fluxo documental: execução da suíte e dos gates (2026-08-19) → números copiados → VALIDATION (seção datada) ; decisão 'uma tool filtrada' → SERVE-LEGS ; superfície → README. Leitor de outro pod → documentos.

### Consequências e risco

Sem ação: nada quebra no produto; o risco é um leitor de outro pod tomar a seção L2 do VALIDATION (123 passed, gates de 2026-08-19) como estado atual, ou confiar na prosa do README que hoje mistura 'six' e 'eight'. Probabilidade média de confusão, impacto baixo; confiança alta nos fatos.

### Alternativas e recomendação

Recomendado: manter encerrada; tratar a deriva atual (contagens 4/6/7/8) num item de reconciliação documental único, preservando as seções datadas. Alternativa: reescrever as seções históricas — rejeitada, apaga registro.

### Dependências e paralelismo

Nenhuma dependência técnica: depende só de runs-gates, já entregue. O item de reconciliação documental da prosa atual é independente desta spec, não depende de ClickHouse e pode correr em paralelo a qualquer revisão de PR.

### Plano e aceite propostos

Não ação sobre esta spec. Para reuso de evals de contagem: exigir que a contagem venha de uma execução registrada com SHA e sucesso total (não só 'N passed' extraído). Doc: nenhuma.

### Comunicação entre responsáveis

Explicar: 'A documentação de L2 foi feita e está preservada como seção datada; o que diverge hoje é a prosa atual, que vários legs depois reescreveram.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Reescrevendo a seção L2 com números atuais, o VALIDATION deixaria de registrar o que foi observado em 2026-08-19, inclusive os dois defeitos achados pelo banco real. Que caso o teste ainda não cobre? — O eval de contagem aceita qualquer 'N passed' de uma execução com falhas e não distingue seção histórica de atual. Como eu explicaria isso para outro pod? — 'VALIDATION é um diário: cada leg tem sua seção com data; a prosa do README é que precisa refletir o presente.'

### Próxima ação e encerramento

Ação: nenhuma nesta spec; remeter deriva ao item documental. Owner a confirmar: Serve/documentação. Entrada: este parecer. Saída: referência cruzada. Encerramento: já encerrada.

<a id="item-289"></a>

## T-20260819-list-runs-tool — T-20260819-list-runs-tool.md

Frente: Serve / L2 Discover — descoberta de runs (#83). Encaminhamento: encerrada_com_eval_que_nao_invoca_a_tool.

### Identidade e estado

`tasks/done/T-20260819-list-runs-tool.md` (blob 42362567). 'Register the list_runs tool', XS, standard, P2; owner `(none)`; depends_on runs-read-layer e run-summary-models. Estado `done`, `accepted: true` em 2026-08-19T17:50:13Z, aceite registrado no arquivo por `sidymar` via taskspec accept (autor da implementação; não é revisão independente nem nova autorização). Pod provável: Pod 3/Serve (caminhos serve/ e docs/lanes; nenhum pod no arquivo).

### Intenção e benefício

Expor `list_runs(limit, since_hours, app_name)` como tool read-only: é o commit em que a lane deixa de exigir um job_id vindo de fora. Uma tool com filtros cobre list_runs, find_run e latest_run (menos superfície de injeção).

### Feito, faltante e não comprovado

Implementado (1451ed5): tool em `server.py:361-397` com READ_ONLY, RunList com notas de truncamento e untrusted_fields; docstring do módulo hoje diz 'Eight tools' (B-4 'cinco' é histórico). Controle real de B-2/B-3: o eval_1 só lista a tool e confere anotações — não invoca list_runs nem verifica ordem ou filtro, embora declare B-2/B-3 (mesma classe que Codex C04-17 aponta em L5/L6). Ordem e filtro são cobertos no nível do store (`test_runs_*` em test_ch.py) e live pelo read_only_gate, não pela tool. Observação de leitura: a nota de truncamento só aparece quando `len(runs) == store.MAX_RUNS`, não quando o resultado é cortado pelo `limit` pedido.

### Linhagem

SERVE-LEGS L2 → tasks/.plans/l2-discover.yaml (approved: true) → spec d244af7 (2026-08-19) → implementação 1451ed5 com accepted:true → done d1d3db4 → Duplicatas regeneradas em tasks/ (ready/false) por aab2988 e removidas por f504255 no mesmo dia; a cópia em tasks/done/ é o objeto que chegou a c3c3ea3 → PR #83 integrada (merge e10ab85, 2026-08-20 UTC)

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260819-list-runs-tool.md; fontes/batch-revalidated-specs58-sources/history/T-20260819-list-runs-tool.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__server.py; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__ch.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

FATO OBSERVADO: tool registrada e anotada; evals não exercitam B-2/B-3. RELATO: gate stdio 'passed 5 tools + apex://runs' (PR #83). INFERÊNCIA: o aceite de B-2/B-3 se apoia em testes do store e no gate, não no eval declarado. Sem execução.

### Fluxo

Fluxo observado: cliente MCP → tools/call list_runs(limit, since_hours, app_name) → ReadStore.runs (since ligado, app_name ligado, limit clamp) → RunSummary.model_validate → RunList(notes, untrusted_fields) → resposta estruturada.

### Consequências e risco

Registro e delegação de parâmetros estão presentes, sem evidência de regressão nesta leitura. eval_1 não invoca a tool: não discrimina reordenação ou perda de filtro no servidor. A nota só considera MAX_RUNS, e RunList.limit/since_hours preservam o pedido, enquanto o store pode aplicar clamp diferente; o payload não certifica o limite efetivo.

### Alternativas e recomendação

Recomendado: manter encerrada; para reuso do plano, substituir o eval por chamada real da tool com FakeClient (ordem, filtro, limite). Alternativa: aceitar a cobertura indireta do store/gate, documentando-a. Corrigir a condição da nota de truncamento é melhoria opcional.

### Dependências e paralelismo

Nenhuma dependência pendente (runs-read-layer e run-summary-models entregues). Um teste que invoque a tool com FakeClient independe de ambiente e de outras decisões; pode correr em paralelo a qualquer frente, inclusive à reconciliação do gate stdio.

### Plano e aceite propostos

Para reuso, chamar a tool com FakeClient e verificar delegação de filtros, ordem e metadados sob clamp. Usar limite pedido menor que o conjunto e caso acima de MAX_RUNS, distinguindo existência de mais dados de mero comprimento igual ao limite. Esta revisão não altera código nem aceite histórico.

### Comunicação entre responsáveis

Explicar: 'list_runs existe desde #83 e é de onde vêm os job_id. O eval que fechou a spec só conferia que a tool estava listada; ordem e filtro são provados em outro nível.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Com três tools (list_runs, find_run, latest_run), seriam três superfícies de injeção e três nomes globais para o cliente, diferindo só no WHERE. Que caso o teste ainda não cobre? — A tool chamada de fato com filtro e limite, e o aviso de truncamento quando o corte vem do limite pedido. Como eu explicaria isso para outro pod? — 'Uma tool listada não é uma tool testada; o eval desta folha prova o registro, não o comportamento.'

### Próxima ação e encerramento

Ação: nenhuma na spec; registrar a lacuna de eval para reuso. Owner a confirmar: Serve. Entrada: este parecer. Saída: nota no plano/índice. Encerramento: já encerrada.

<a id="item-290"></a>

## T-20260819-run-summary-models — T-20260819-run-summary-models.md

Frente: Serve / L2 Discover — descoberta de runs (#83). Encaminhamento: encerrada_com_correcao_live_posterior.

### Identidade e estado

`tasks/done/T-20260819-run-summary-models.md` (blob 66779faa). 'Add RunSummary and RunList models', S, standard, P2; owner `(none)`; sem dependências. Estado `done`, `accepted: true` em 2026-08-19T17:49:31Z, aceite registrado no arquivo por `sidymar` via taskspec accept (autor da implementação; não é revisão independente nem nova autorização). Pod provável: Pod 3/Serve (caminhos serve/ e docs/lanes; nenhum pod no arquivo).

### Intenção e benefício

Tipar o payload de descoberta de runs (FastMCP deriva o schema do retorno) e marcar app_name como não confiável, porque o autor do job Spark controla esse texto.

### Feito, faltante e não comprovado

Implementado (76e712a) e corrigido depois do aceite por 9dc290a ('RunSummary rejected the timestamps ClickHouse actually returns'): `first_ts`/`last_ts` com validador que converte datetime em string (`models.py` RunSummary, ~620-650), RunList com `untrusted_fields` padrão `runs[].app_name` (653-668). Testes `test_run_summary_defaults_from_job_id`, `test_run_list_schema_renders`, `test_app_name_is_marked_untrusted` e, após a correção, `test_timestamps_from_the_driver_are_coerced_to_strings` (`test_runs.py`). O defeito de tipo só apareceu no gate live (PR #83 'What the live gate caught'): o aceite Tier 1 de 17:49Z passou com fakes que forneciam strings.

### Linhagem

SERVE-LEGS L2 → tasks/.plans/l2-discover.yaml (approved: true) → spec d244af7 (2026-08-19) → implementação 76e712a com accepted:true → done 79e3b47 → Duplicatas regeneradas em tasks/ (ready/false) por aab2988 e removidas por f504255 no mesmo dia; a cópia em tasks/done/ é o objeto que chegou a c3c3ea3 → PR #83 integrada (merge e10ab85, 2026-08-20 UTC); correção 9dc290a após o aceite e antes do merge. Elo: o aceite registrado antecede a correção — o arquivo não registra re-aceite.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260819-run-summary-models.md; fontes/batch-revalidated-specs58-sources/history/T-20260819-run-summary-models.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__models.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_runs.py; fontes/batch-revalidated-specs58-sources/git/serve__VALIDATION.md. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: RunSummary aceita campos mínimos, converte timestamps por _as_iso e RunList marca app_name. Testes nomeados cobrem defaults/schema/marcador; regressão de coerção usa datetime sem fuso. RELATO: VALIDATION descreve falha de datetime no banco real e correção. A ficha registra aceite histórico anterior à correção, sem revalidar assinatura ou reproduzir suíte. O estado final tem controle presente, não prova runtime universal.

### Fluxo

Fluxo observado: driver ClickHouse (datetime) → RunSummary(_isoformat) → string → RunList(untrusted_fields=['runs[].app_name']) → schema FastMCP → cliente.

### Consequências e risco

A falha histórica possui correção e teste presente. Permanecem limites de tipos/fusos não exercitados pelos casos lidos e a diferença entre objeto historicamente aceito e versão corrigida. Aceite Tier1 com fakes não certifica compatibilidade universal com o driver real.

### Alternativas e recomendação

Recomendado: manter encerrada, anotando que o estado aceito foi complementado por 9dc290a. Alternativa: re-aceite formal sobre o SHA corrigido, se o processo exigir que o aceite cubra o estado final.

### Dependências e paralelismo

Nenhuma dependência técnica pendente. A nota 'aceite em 76e712a, correção 9dc290a' é documental e corre em paralelo; um re-aceite formal sobre o SHA corrigido, se exigido, não depende de ClickHouse porque o teste de coerção usa datetime em processo.

### Plano e aceite propostos

Não ação no código. Nota documental: 'aceite em 76e712a; correção 9dc290a por defeito achado no gate live'. Para reuso: fakes devem devolver `datetime` como o driver.

### Comunicação entre responsáveis

Explicar: 'O modelo de runs foi aceito com testes que usavam texto e quebrou no primeiro dado real; a correção entrou antes do merge, com teste. O aceite do arquivo é anterior à correção.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Sem marcar app_name como não confiável, um nome de aplicação com instrução embutida chegaria ao modelo como se fosse texto do Apex. Que caso o teste ainda não cobre? — Um datetime com fuso devolvido pelo driver, que o validador converte sem normalizar para UTC nesta camada MCP. Como eu explicaria isso para outro pod? — 'Testes com fakes de texto passaram; o banco real devolve datetime. Faça os fakes parecerem o driver.'

### Próxima ação e encerramento

Ação: anotar a sequência aceite→correção. Owner a confirmar: Serve. Entrada: commits citados. Saída: nota no índice. Encerramento: já encerrada.

