# Fichas documentais — lote 48

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-471"></a>

## PR#79 — serve/L1 Connect: 23 signed Task-Specs, first two units accepted

Frente: historico. Encaminhamento: integrada_parcial_por_desenho_com_review_aprovada.

### Identidade e estado

PR #79, `serve/l1-connect` → `main`; autor `sidymar` (COLLABORATOR); criada em 2026-08-17 e integrada em 2026-08-18T21:11:51Z (merge `e7519d0`); 8 commits; 57 arquivos. Review: bot Codex com 6 comentários inline (P2) e 6 respostas inline do autor, seis reviews `COMMENTED` vazias do autor e aprovação do mantenedor em 2026-08-18.

### Intenção e benefício

Abrir L1 Connect como 23 Task-Specs escritas e consumir duas pelo ciclo declarado gate→build→accept: ServerStatus e ReadStore.store_health. O corpo corrige a promessa do título: as 21 restantes ficam sem assinatura antes do despacho; apex_status ainda não é ferramenta viva nesta PR.

### Feito, faltante e não comprovado

Feito: 2 de 23 unidades, parcial por desenho; as outras 21 ficaram escritas e **sem assinatura**, porque `taskspec gate --stamp` revalida os evals contra o código antes de cada despacho. Commits separam correções de contrato de spec das implementações; um deles registra "8 specs had evals that passed before the work existed". O último commit responde à review do bot (índice morto, backlog poluído, status velho). A aprovação diz "Serves the project as a 2-of-23 L1 increment, not as a finished Connect leg". As specs legadas foram para `docs/lanes/L1_legacy_specs/`. O Codex (C04-18) registra que o plano `l1-connect.yaml` tem 23 unidades e não deve ser tratado como entregue pela #79.

### Linhagem

Plano L1 → PR #79 (2026-08-17) → review do bot → correções → aprovação → merge → PR #101 (contrato de merge da raia serve) e L2–L6 nas PRs #83, #86–#88.

### Fontes e corte

Snapshot (PR 79); dossiê (57 arquivos, 8 commits); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/pr79-reviews.json` e `pr79-comments.json`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_runs-push-main-por-dia.txt` (push verde do merge às 21:11); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos, commits, reviews e comentários inline. RELATADO: execução do ciclo gate → build → accept. DERIVADO: a política declarada evita carimbar as 21 specs antes da validação por unidade. Os campos signed_off/accepted são artefatos observados; não se verificou a chave HMAC, execução dos evals ou autorização humana externa. Review formal (API, observada em 2026-10-17T17:28:25Z): 8 — `chatgpt-codex-connector[bot]` COMMENTED em 2026-08-17; `sidymar` COMMENTED em 2026-08-17; `sidymar` COMMENTED em 2026-08-17; `sidymar` COMMENTED em 2026-08-17; `sidymar` COMMENTED em 2026-08-17; `sidymar` COMMENTED em 2026-08-17; `sidymar` COMMENTED em 2026-08-17; `luanmorenommaciel` APPROVED em 2026-08-18. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 12 (chatgpt-codex-connector[bot] 6, sidymar 6). Runs do Actions com o head `4e22940` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 32052294351, tentativa 1, created_at 2026-08-17 17:52:50Z, run_started_at 2026-08-17 17:52:50Z, updated_at 2026-08-17 17:55:43Z (antes do merge pelo updated_at). Complemento documental de 19/10, RELATADO na seção Verification: TASK_PLAN=OK, DoD 23 COMPLETE/0 gaps, suite Serve 102 passed e duas folhas com gate TIER=1/ACCEPTED=1. São resultados e aceites declarados do corte do autor, sem nova validação de HMAC ou execução nesta auditoria.

### Fluxo

Fluxo Task-Spec: plano aprovado → 23 specs → `gate --stamp` revalida evals → build → accept → spec em `tasks/done/`; só 2 percorreram o ciclo aqui.

### Consequências e risco

Médio valor de processo. Limite: "aceita" significa evals da própria spec passando; não é aceite humano nem runtime (C04-17 do Codex mostra evals que não exercitam o comportamento em L5/L6).

### Alternativas e recomendação

(a) Manter como histórico parcial; (b) tratar as 21 specs não consumidas como backlog a revisar no estado e autorização pertinentes; (c) antes de reusar o plano, confrontar dependências e evals com o código atual. A ausência de assinatura capturada não prova inexistência de toda autorização posterior.

### Dependências e paralelismo

O destino das 21 unidades depende do mantenedor; alguns itens (PyPI) dependem de DEC-N2.

### Plano e aceite propostos

Condição explícita de não ação: integrada como incremento parcial declarado. Qualquer reuso do plano exige revisar os evals antes.

### Comunicação entre responsáveis

Para a consolidação: "PR #79 integrou duas de 23 unidades L1; as demais estão sem assinatura no recorte e apex_status ainda não é ferramenta registrada nesse incremento".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — usar ready_queue como ordem de despacho ignora depends_on, limite reconhecido pelo autor; carimbar todas as specs antecipadamente contraria a política relatada. Que caso o teste ainda não cobre? — os carimbos não certificam runtime, autorização humana ou validade atual das 21 unidades não consumidas. Como eu explicaria isso para outro pod? — o merge entrega modelo de status e consulta de saúde; o restante do plano precisa de revisão e despacho próprios.

### Próxima ação e encerramento

Owner a confirmar: dono do serve (Pod 3), para o destino das 21 unidades. Encerramento: a PR segue integrada.

<a id="item-472"></a>

## PR#80 — chore: bump contract to v0.5 with additive task analysis fields

Frente: historico. Encaminhamento: integrada_sem_review_formal_introduziu_erro_de_ddl.

### Identidade e estado

PR #80, `cursor/contract-v05-sync-a95c` → `main`; autor `luanmorenommaciel` (OWNER), commit único `51f4848` com autor de commit "Cursor Agent" (metadado do commit; não descreve todo o processo de autoria); criada em 2026-08-18T21:15:05Z e integrada em 2026-08-18T21:17:52Z (merge `4fb5f39`); 20 arquivos. Sem review formal registrada; há um comentário do próprio OWNER pedindo dois ajustes.

### Intenção e benefício

Sincronizar a documentação e os artefatos do contrato congelado com o que entrou na main em 2026-08-18 (PRs #66–#77): `CONTRACT.md` v0.5 com ~15 chaves OTLP para análise segura a retry, semântica `sample_count=0` = "sem amostra", e DDLs canônicos atualizados.

### Feito, faltante e não comprovado

Feito, com um defeito: os DDLs canônicos (`infra/sql/002_spark_events.sql`, `contract/spark_events.ddl.sql`, `collect/ddl/20_spark_events.sql`) passaram a ter `SETTINGS` antes de `TTL`; a ordem é observável no diff, e a rejeição pelo ClickHouse é relatada na PR #82 (saída `Code: 62` no init), não reproduzida aqui. Conferi: até `e7519d0` o arquivo terminava em `TTL …;`; em `4fb5f39` (merge desta PR) tem `SETTINGS` na linha 53 e `TTL` na 54; o único commit no intervalo é o `51f4848` desta PR (`fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/PR_82.txt`). A PR #82 corrigiu em 2026-08-20. Os dois ajustes pedidos pelo OWNER não foram feitos: o corpo ainda tem `Closes #66 #67 #68 #70 #74 #75 #76 #77`, e `contract/sample_event.json` continua com campos v0.5 zerados ao lado de p50/p99 reais, sem nota (`fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/PR_80.txt`).

### Linhagem

Merges de 2026-08-18 → PR #80 (commit único com autor "Cursor Agent") → merge às 21:17:52Z, 6 minutos depois do merge da #79 e antes de o run de PR no head concluir (32186736350, `success` às 21:18:21Z) → run de push do merge (32186978125) com `success` às 21:21:05Z (`fontes/batch-claude-historico-corrigido-sources/claude/fontes/reconferencia/pontos03-05-06-runs-por-pr.json`) → falha de provisionamento do zero relatada na PR #82 → PR #82 (merge 2026-08-20T02:45:27Z). O #37 usou o `CONTRACT.md` v0.5 desta PR como "schema MVP documentado".

### Fontes e corte

Snapshot (PR 80) e comentário do OWNER; dossiê; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/PR_80.txt` e `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/PR_82.txt`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_runs-push-main-por-dia.txt`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: ordem das cláusulas por SHA, commit único, run de PR concluído 29 s depois do merge, run de push do merge verde, nits não tratados. RELATADO (PR #82): o erro `Code: 62` no provisionamento do zero. DIRETO adicional: CI.yml no head executa suites offline/JAR, validação de Collector e licença, sem provisionamento limpo do ClickHouse. Isso explica a lacuna desse workflow; a revisão não certifica toda execução externa ou todos os outros workflows. Review formal (API, observada em 2026-10-17T17:28:25Z): 0 registradas; isso não prova ausência de leitura humana. Comentários inline de review: 0. Runs do Actions com o head `51f4848` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 32186736350, tentativa 1, created_at 2026-08-18 21:15:08Z, run_started_at 2026-08-18 21:15:08Z, updated_at 2026-08-18 21:18:21Z (depois do merge pelo updated_at).

### Fluxo

Fluxo do defeito relatado em #82: DDL canônico com SETTINGS antes de TTL → init de volume novo tenta criar spark_events → Code62 no TTL e saída 62. O erro nesse arquivo não prova que nenhum objeto anterior, como o database criado no 001, chegou a existir.

### Consequências e risco

Alto na hipótese relatada pela #82: um provisionamento do zero com estes DDLs falharia. O intervalo entre os merges da #80 (2026-08-18T21:17:52Z) e da #82 (2026-08-20T02:45:27Z) é de ~29,5 h; isso não é duração de outage nem contagem de deploys falhos, que não foram observados nesta revisão. A lição de processo: mudança de DDL canônico com commit de autor "Cursor Agent", sem review formal registrada, com CI verde que, segundo a review da #82, não provisiona do zero.

### Alternativas e recomendação

(a) Registrar como exemplo na consolidação e na DEC-02 (recomendado); (b) acrescentar ao CI um job de provisionamento limpo do ClickHouse (DDL inicial) — mudança de CI que exige decisão; (c) tratar os dois nits pendentes numa PR de documentação.

### Dependências e paralelismo

A opção (b) depende de DEC-01 (CI disponível) e DEC-02 (política de checks). A (c) é independente.

### Plano e aceite propostos

Passo documental mínimo opcional: comparar a ordem TTL/SETTINGS nos três DDLs e fixar a versão defeituosa como controle. Aplicar DDL em ClickHouse descartável é prova runtime, não teste estático, e depende de decisão e autorização próprias; nada disso foi executado nesta revisão.

### Comunicação entre responsáveis

Para a consolidação: "PR #80 inverteu TTL/SETTINGS nos DDLs canônicos (visível no diff); a falha de provisionamento do zero é relatada na #82, integrada ~29,5 h depois; o CI verde não provisiona do zero".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — manter o DDL defeituoso deixaria provisionamento novo exposto ao erro de sintaxe relatado em #82. Que caso o teste ainda não cobre? — o CI.yml auditado não cria ClickHouse do zero; a auditoria não executou esse caminho. Como eu explicaria isso para outro pod? — o diff mostra a ordem errada e #82 relata sua falha real; CI success desse workflow não validava o DDL inicial.

### Próxima ação e encerramento

Owner a confirmar: mantenedor, para a decisão sobre o job de provisionamento (DEC-02). Entrada: este registro. Saída: decisão registrada. Encerramento: a PR segue integrada; o defeito foi corrigido pela #82.

<a id="item-473"></a>

## PR#81 — dev: cover the scripts #74 shipped without tests — and make the lane actually run

Frente: historico. Encaminhamento: integrada_com_review_aprovada_e_ci_verde.

### Identidade e estado

PR #81, `candidate/dev-tests-coverage` → `main`; autor `gustocezar`; `pod-2-engine`; criada em 2026-08-19, aprovada em 2026-08-25 e integrada em 2026-09-14T16:17:42Z (merge `6be1bb9`), na leva de 15 merges de 2026-09-14; 3 commits; 8 arquivos. Ligada ao registro G06.

### Intenção e benefício

Acrescentar testes de dois scripts de evidência entregues em #74 e do runner canônico e2e preexistente, além de dar à raia dev um ambiente pytest declarado e entrada na matriz CI.

### Feito, faltante e não comprovado

Feito: três arquivos de testes, pyproject/lock do dev, inclusão de dev na matriz CI e rename test_fingerprint.py→prove_fingerprint.py. O runner e2e_canonical.ps1 já tem commits em julho e não foi introduzido em #74. O teste de runner verifica ausência de oito strings no fonte; isso não certifica toda forma possível de passar segredo. O corpo relata 13 testes, a review menciona 10/10 e diz prove_fingerprint coletado; o rename retira justamente o nome de coleta pytest. A execução não foi refeita nesta revisão.

### Linhagem

PR #74 (sem testes) → PR #81 (2026-08-19) → aprovação (2026-08-25) → merge na leva de 2026-09-14, cujos pushes foram cancelados em sequência até o `success` do run criado às 16:47:05Z e concluído às 16:50:57Z (`fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_runs-push-main-por-dia.txt`).

### Fontes e corte

Snapshot (PR 81); dossiê (8 arquivos; o renome aparece como `{test_fingerprint.py => prove_fingerprint.py}`); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/pr81-reviews.json`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_runs-push-main-por-dia.txt`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos, aprovação, run verde de PR no head. RELATADO: a falha de coleta antes da mudança. O push do merge foi cancelado pela concorrência; o próximo `success` na main concluiu às 16:50:57Z (merge da #87). Review formal (API, observada em 2026-10-17T17:28:26Z): 1 — `luanmorenommaciel` APPROVED em 2026-08-25. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `2970e15` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 32482255915, tentativa 1, created_at 2026-08-21 12:31:03Z, run_started_at 2026-08-21 12:31:03Z, updated_at 2026-08-21 12:34:46Z (antes do merge pelo updated_at).

### Fluxo

Fluxo de prova da raia dev: `ci.yml` matriz → `dev (py)` → `uv run pytest` em `dev/` → testes de redação e de runner.

### Consequências e risco

Alto valor de processo: fechou um "verde silencioso" (testes que, segundo a PR, não rodavam em lugar nenhum). Limite: o push do próprio merge foi cancelado; a primeira prova verde observada na main é o run concluído às 16:50:57Z.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) checar periodicamente se toda pasta `*/tests` tem runner no CI, a mesma classe de lacuna.

### Dependências e paralelismo

Nenhuma dependência pendente: a raia dev entrou na matriz do CI nesta PR. A checagem (b) é independente e só exige leitura do `ci.yml` e das pastas de testes.

### Plano e aceite propostos

Condição explícita de não ação: integrada. Sugestão de controle: um teste de repositório que falhe se existir pasta `tests/` sem lane correspondente no CI.

### Comunicação entre responsáveis

Para a consolidação: "PR #81 declarou runner e CI para a raia dev e acrescentou três grupos de testes; suas contagens e execuções são relatos e o runner e2e testado é anterior à #74".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — testes fora da configuração do runner podem deixar mudanças sem os checks esperados. Que caso o teste ainda não cobre? — buscar strings proibidas no runner não demonstra ausência de vazamento por toda construção equivalente nem cobre runtime. Como eu explicaria isso para outro pod? — o dev ganhou ambiente de teste e job CI; renomeou uma prova Spark para ela deixar de parecer teste pytest.

### Próxima ação e encerramento

Nenhuma ação obrigatória. Owner a confirmar: mantenedor do CI, para o controle (b). Encerramento: histórico.

<a id="item-474"></a>

## PR#82 — fix: spark_events DDL cannot create the table — no fresh deployment can start

Frente: historico. Encaminhamento: integrada_com_review_aprovada_corrige_regressao_da_pr80.

### Identidade e estado

PR #82, `fix/spark-events-ddl-clause-order` → `main`; autor `sidymar`; `pod-3-serve`; criada em 2026-08-19, aprovada no mesmo dia e integrada em 2026-08-20T02:45:27Z (merge `482092d`); 1 commit; 3 arquivos (+2/-2 cada).

### Intenção e benefício

Corrigir a ordem das cláusulas nas três cópias do DDL de `spark_events`: `SETTINGS` precisa ser a última cláusula, depois de `TTL`. Segundo o corpo, sem isso o init do ClickHouse aborta no `002_spark_events.sql` e nenhum deploy novo sobe.

### Feito, faltante e não comprovado

Feito: as três cópias corrigidas (conferido: em `482092d`, `TTL` na linha 53 e `SETTINGS` na 54). Origem do erro, conferida nesta revisão: a PR #80 (`51f4848`, 2026-08-18). A aprovação: "SETTINGS last is the ClickHouse law … Fresh provision is the only way to see it — that's why CI never caught it". O bot Codex não revisou (limite de uso). A PR #83 traz a mesma correção nos mesmos três arquivos, integrada 8 segundos depois.

### Linhagem

PR #80 (erro) → deploy do zero falha (`Code: 62`, contêiner sai) → PR #82 (2026-08-19) → aprovação → merge (2026-08-20 02:45:27) → PR #83 com a mesma correção (02:45:35).

### Fontes e corte

Snapshot (PR 82); dossiê; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/pr82-reviews.json`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/PR_82.txt` (ordem das cláusulas em cinco SHAs e o commit causador); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_runs-push-main-por-dia.txt`.

### Classe e limite da evidência

DIRETO: ordem das cláusulas por SHA, review, runs verdes de PR e de push no head. RELATADO: a saída do init com `Code: 62` e o contêiner saindo com 62. Review formal (API, observada em 2026-10-17T17:28:26Z): 1 — `luanmorenommaciel` APPROVED em 2026-08-19. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `6bae427` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` push success, run 32294494810, tentativa 1, created_at 2026-08-19 19:42:22Z, run_started_at 2026-08-19 19:42:22Z, updated_at 2026-08-19 19:45:29Z (antes do merge pelo updated_at); `CI` pull_request success, run 32294498017, tentativa 1, created_at 2026-08-19 19:42:24Z, run_started_at 2026-08-19 19:42:24Z, updated_at 2026-08-19 19:45:51Z (antes do merge pelo updated_at).

### Fluxo

Fluxo pretendido: CREATE TABLE spark_events com TTL antes de SETTINGS → init segue aos demais arquivos. O corpo relata sucesso num volume vazio; não foi reproduzido nesta auditoria. O erro histórico em 002 não prova ausência de objetos criados por arquivos anteriores.

### Consequências e risco

Alto: restaurou a ordem de cláusulas que, segundo o relato desta PR, impedia subir um deploy novo. Limite: o problema de fundo (CI que não provisiona do zero) continua; ver ficha PR#80.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) levar o teste de provisionamento sugerido na ficha PR#80 à decisão de CI.

### Dependências e paralelismo

A opção (b) depende de DEC-01 (CI disponível) e DEC-02 (quais checks são exigidos); a correção em si não depende de nada e já está na main.

### Plano e aceite propostos

Condição explícita de não ação nesta PR. O controle preventivo está descrito na ficha PR#80.

### Comunicação entre responsáveis

Para a consolidação: "PR #82 restaurou a ordem TTL → SETTINGS ~29,5 h depois do merge da #80; a falha de provisionamento é relato desta PR".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — o DDL anterior permanece exposto ao Code62 relatado no init e pode impedir a nova stack de ficar operacional. Que caso o teste ainda não cobre? — o workflow CI auditado não provisiona ClickHouse do zero e esta auditoria não executou esse caminho. Como eu explicaria isso para outro pod? — três cópias tinham a mesma ordem incorreta; o diff corrige a sintaxe e o autor relata que o provisionamento vazio passa.

### Próxima ação e encerramento

Nenhuma ação obrigatória. Owner do controle preventivo: mantenedor (DEC-02). Encerramento: histórico.

<a id="item-475"></a>

## PR#83 — serve/L2 Discover: list_runs, apex://runs, and a self-selecting comparison baseline

Frente: historico. Encaminhamento: integrada_com_review_aprovada_e_ci_verde.

### Identidade e estado

PR #83, `serve/l2-discover` → `main`; autor `sidymar`; `pod-3-serve`; criada em 2026-08-19, aprovada no mesmo dia e integrada em 2026-08-20T02:45:35Z (merge `e10ab85`); 27 commits; 31 arquivos.

### Intenção e benefício

Fechar a perna L2 (Discover): dar ao usuário um jeito de obter `job_id` (`list_runs`, quinta ferramenta), o recurso MCP `apex://runs` e um baseline de comparação escolhido pelo próprio `compare_runs`, com `app_name` tratado como dado não confiável.

### Feito, faltante e não comprovado

Feito: 10 de 10 unidades aceitas no Tier 1 (`tasks/done/T-20260819-*.md`); `ReadStore.runs()` com limite de partição e `app_name` como parâmetro; teste de injeção (`test_injection_hardening.py`); gates vivos atualizados. A PR também inclui a mesma correção de DDL da PR #82. Dois arquivos que ela versionava (`tasks/_metrics.jsonl`, `tasks/_state.yaml`) saíram do versionamento depois, pela PR #101. A aprovação: "L2 is the missing read … Refusing a bad baseline is Apex law". Leitura adicional de server.py/diagnose.py: candidatos vêm de runs recentes da aplicação, com exclusão do job atual e igualdade do conjunto de fingerprints; não há filtro comparando timestamps ao run atual. Assim, anterioridade do baseline é intenção declarada, não condição implementada nesse caminho.

### Linhagem

Plano L2 (`tasks/.plans/l2-discover.yaml`) → PR #83 → aprovação → merge 8 s depois da #82 → PR #101 remove os arquivos gerados → L3/L5/L6 seguem.

### Fontes e corte

Snapshot (PR 83); dossiê (31 arquivos, 27 commits); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/pr83-reviews.json`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_runs-push-main-por-dia.txt`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos, specs em `tasks/done/`, review. RELATADO: aceite das 10 unidades por evals. O push do merge foi cancelado pelo merge seguinte (#84), que passou verde. Review formal (API, observada em 2026-10-17T17:28:27Z): 1 — `luanmorenommaciel` APPROVED em 2026-08-19. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `9a1ae67` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 32294567917, tentativa 1, created_at 2026-08-19 19:43:10Z, run_started_at 2026-08-19 19:43:10Z, updated_at 2026-08-19 19:46:21Z (antes do merge pelo updated_at).

### Fluxo

Fluxo: list_runs→ReadStore.runs com ts mínimo, limite e app_name vinculado→RunList. compare_runs sem baseline explícito busca até dez candidatos recentes da aplicação e escolhe o primeiro com conjunto de fingerprints igual; exclui o atual, mas não exige que o candidato seja temporalmente anterior. Baseline explícito usa o caminho comparativo e pode reportar mudança de plano.

### Consequências e risco

A descoberta de runs tem valor estático claro; teste de injeção e gates relatados não são aceite de usuário. Limites declarados: até dez consultas extras, janela recente e gate stdio requer um run. Limite adicional observado: o auto-baseline não impõe anterioridade temporal ao run analisado, portanto a promessa prior é mais forte que o filtro lido.

### Alternativas e recomendação

(a) Manter entrega como histórico; (b) registrar para triagem documental o limite de anterioridade do auto-baseline, sem presumir incidente nem executar correção; (c) preservar a necessidade de prova MCP/ClickHouse com escopo próprio.

### Dependências e paralelismo

Nenhuma pendente; a reconciliação dos arquivos gerados foi feita na PR #101.

### Plano e aceite propostos

Condição explícita de não ação: integrada, com aceite por unidade.

### Comunicação entre responsáveis

Para a consolidação: "PR #83 entregou list_runs e apex://runs, além de baseline automático por plano; a anterioridade temporal prometida não é imposta no filtro auditado".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — escolher baseline só por recência pode comparar planos distintos; igualdade de fingerprints reduz esse risco sem provar equivalência completa de workload. Que caso o teste ainda não cobre? — esta revisão não observou prova de seleção temporalmente anterior quando há run posterior do mesmo plano. Como eu explicaria isso para outro pod? — o MCP lista runs e tenta achar o mesmo plano; o código não garante que esse candidato ocorreu antes do run atual.

### Próxima ação e encerramento

Nenhuma mutação nesta auditoria. Owner a confirmar para avaliar o limite de anterioridade do baseline; a PR permanece integrada. Injeção e limites de consulta continuam controles a preservar.

<a id="item-476"></a>

## PR#84 — harness: verify optional ClickHouse endpoint identity

Frente: historico. Encaminhamento: integrada_com_review_aprovada_e_ci_verde.

### Identidade e estado

PR #84, `codex/harn-endpoint-pr-prep` → `main`; autor `gustocezar` (commit de "Augusto Silva"); `pod-2-engine`; criada em 2026-08-20T02:12:12Z e integrada em 2026-08-20T02:45:43Z (merge `7c5460c`, o SHA que o v2 e esta revisão usam como "main de 2026-08-20"); 1 commit; 4 arquivos.

### Intenção e benefício

Acrescentar ao gate E2E de seis raias uma checagem opcional de identidade do ClickHouse: com `CLICKHOUSE_EXPECTED_HOSTNAME` definido, `SELECT hostName()` precisa coincidir antes de `run_gate()`, evitando rodar contra a instância errada em ambientes com vários runtimes.

### Feito, faltante e não comprovado

Feito: `scripts/e2e_six_lanes.py` (+26), `tests/test_e2e_six_lanes.py` (+133), `docs/e2e/README.md` e `docs/task-specs/HARN-ENDPOINT.md`. Comportamento: variável ausente = legado; igual = segue; diferente, erro ou resposta inválida = falha fechada antes de análise ou escrita. Relatado: 13 testes, cobrindo os caminhos de falha e provando que `run_gate()` não é chamado. A aprovação: "Harness-only and opt-in".

### Linhagem

Task-Spec HARN-ENDPOINT → PR #84 → aprovação → merge (push verde, `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_runs-push-main-por-dia.txt`) → `7c5460c` vira a main de referência até 2026-09-14.

### Fontes e corte

Snapshot (PR 84); dossiê; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/pr84-reviews.json`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_runs-push-main-por-dia.txt`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos, review, runs verdes de PR e de push. RELATADO: 13 testes. Review formal (API, observada em 2026-10-17T17:28:27Z): 1 — `luanmorenommaciel` APPROVED em 2026-08-20. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `2de02dd` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 32323797695, tentativa 1, created_at 2026-08-20 02:12:14Z, run_started_at 2026-08-20 02:12:14Z, updated_at 2026-08-20 02:15:42Z (antes do merge pelo updated_at).

### Fluxo

Fluxo do gate: cliente ClickHouse conectado → `CLICKHOUSE_EXPECTED_HOSTNAME`? → `SELECT hostName()` → igual: `run_gate()`; diferente: `GateFailure` sanitizado, sem escrita.

### Consequências e risco

Checagem útil contra roteamento ao hostname diferente do configurado. Limites: ausente/vazia desativa; igualdade de hostname não garante identidade única, mesma instância, schema ou ownership. Ensaios e 13 testes continuam relatos da entrega.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) tornar a variável obrigatória em ambientes compartilhados — decisão do dono do harness.

### Dependências e paralelismo

A opção (b) se liga ao #175 (identidade de stack) e ao #178 (propagação de endpoint).

### Plano e aceite propostos

Condição explícita de não ação nesta PR. Sugestão: o #175 considerar esta checagem como parte da identidade de stack.

### Comunicação entre responsáveis

Para a consolidação: "PR #84 compara opcionalmente SELECT hostName() com o nome esperado antes do gate; isso reduz confusão de destino sem atestar identidade única".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — consultar destino inesperado pode invalidar a interpretação de uma prova E2E. Que caso o teste ainda não cobre? — dois ClickHouses com o mesmo hostname não são diferenciados pelo contrato desta checagem. Como eu explicaria isso para outro pod? — o gate exige o nome esperado quando configurado e falha antes da análise se divergir; isso não é identidade global do banco.

### Próxima ação e encerramento

Nenhuma ação obrigatória. Owner a confirmar: dono do harness, para a opção (b). Encerramento: histórico.

<a id="item-477"></a>

## PR#85 — docs: define pre-submit provenance for E2E runs

Frente: historico. Encaminhamento: integrada_sem_review_formal_documental.

### Identidade e estado

PR #85, `codex/pre-submit-provenance` → `main`; autor `gustocezar` (commit de "Augusto Silva"); `pod-2-engine`; criada em 2026-08-20T02:36:05Z e integrada em 2026-08-20T02:39:50Z (merge `0da32ce`); 1 commit; 2 arquivos. Sem review formal registrada. Ligada aos registros DD10 e L06.

### Intenção e benefício

Definir uma convenção opcional de proveniência antes da submissão de runs E2E: Task-Spec → hash → manifesto de autorização → hash → recibo pós-run, com `harness_execution_id`, manifestos não autorreferentes e `secrets_included: false`.

### Feito, faltante e não comprovado

Feito como documentação: `docs/e2e/PRE_SUBMIT_PROVENANCE.md` (+103) e link no README de e2e. Escopo declarado: nenhuma mudança em Spark, JAR, collector, ClickHouse, engine, serve, CI ou Docker; nenhuma aplicação em runtime; nível inicial de garantia temporal `local_declared_not_externally_anchored`. Relatado: "Gemini design review" (texto de outra LLM, alegação). Não verificado: uso da convenção em algum recibo posterior.

### Linhagem

Necessidade de proveniência de runs (DD10/L06) → PR #85 → merge sem review formal (push verde, `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_runs-push-main-por-dia.txt`) → convenção disponível, sem aplicação obrigatória.

### Fontes e corte

Snapshot (PR 85); dossiê; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/pr85-reviews.json`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_runs-push-main-por-dia.txt`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos, ausência de review formal, push verde. RELATADO: revisão de desenho por outra LLM, que esta auditoria trata como alegação. Review formal (API, observada em 2026-10-17T17:28:28Z): 0 registradas; isso não prova ausência de leitura humana. Comentários inline de review: 0. Runs do Actions com o head `9176acd` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 32325217706, tentativa 1, created_at 2026-08-20 02:36:08Z, run_started_at 2026-08-20 02:36:08Z, updated_at 2026-08-20 02:39:33Z (antes do merge pelo updated_at).

### Fluxo

Fluxo documental: intenção (Task-Spec) → `task_spec_sha256` → manifesto de autorização → `authorization_manifest_sha256` → execução → recibo.

### Consequências e risco

Documento opt-in sem enforcement introduzido. Dá formato à custódia da intenção e do recibo; adoção efetiva não foi medida nesta ficha, nem se demonstrou causa de eventual baixa adoção. O próprio texto limita tempo a declaração local e distingue integridade de ancoragem externa.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) adotar a convenção como requisito para provas de runtime da v1 (M4) — decisão do mantenedor.

### Dependências e paralelismo

A opção (b) depende de decisão de política de evidência; não há dependência técnica.

### Plano e aceite propostos

Condição explícita de não ação: documento opt-in. Se adotado em M4: exigir manifesto e recibo nos runs que a release citar.

### Comunicação entre responsáveis

Para a consolidação: "PR #85 define convenção opcional para vincular intenção, manifesto e recibo; hashes comprovam integridade comparada, enquanto identidade do autorizador e tempo precisam de evidência própria".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — sem vínculo de integridade fica mais difícil conferir qual escopo um recibo referencia; mesmo com hash, autorização e anterioridade externa exigem prova própria. Que caso o teste ainda não cobre? — documento e exemplos não demonstram enforcement automático nem adoção posterior da convenção. Como eu explicaria isso para outro pod? — registre o escopo e o manifesto antes, depois faça o recibo apontar para os bytes usados; timestamps locais continuam declarados.

### Próxima ação e encerramento

Owner a confirmar: mantenedor, para a decisão (b) em M4. Encerramento: histórico.

<a id="item-478"></a>

## PR#86 — serve/L6 — cross-run memory: recall_similar_runs over the memory lane

Frente: historico. Encaminhamento: integrada_com_review_aprovada_e_ci_verde.

### Identidade e estado

PR #86, `serve/l6-learn` → `main`; autora `sidymar`; `pod-3-serve`; criada em 2026-08-20, com review `COMMENTED` (2026-08-25, "Do not merge this onto today's main") e `APPROVED` (2026-09-14); integrada em 2026-09-14T17:05:10Z (merge `1e0ba80`, o último da leva e o SHA da main usado como "fechamento" em várias fichas deste pacote); 10 commits; 19 arquivos.

### Intenção e benefício

Acrescentar ao MCP a sexta ferramenta, `recall_similar_runs`: dado um `job_id`, achar formas de plano parecidas e devolver as execuções históricas delas, como superfície sobre a raia memory, sem reimplementar o backend de embeddings.

### Feito, faltante e não comprovado

Feito: `ch.py` (+218), `diagnose.py` (+156), `models.py` (+200), `server.py` (+224), testes (`test_recall_view.py` +354, `test_ch.py` +294) e `tools/recall_gate.py` (+368); plano `l6-learn.yaml` e seis specs em `tasks/done/`. Correção registrada: o plano previa "implementar o backend de embeddings", que já existia na memory (47 testes), e F6.1 foi retirada. Rebase depois da PR #101, com `CONTRACTED_TOOLS` ganhando uma linha. O Codex (C04-17) aponta que, no `l6-learn.yaml`, o eval de `recall-runs-tool` não exercita payload, forma ausente nem memória indisponível; o aceite por eval aqui é fraco. Atualização 19/10: o gate stdio `serve/tools/mcp_stdio_gate.py` lista 7 tools na base histórica, sem `recall_similar_runs`; o último commit no arquivo é `3758d00` (#87, re-pin em seis) e nenhum commit da L6 o tocou. Leitura estática, não executada.

### Linhagem

Plano L6 → PR #86 (2026-08-20) → conflito previsto com #87/#88 (simulação de `gustocezar`, 2026-08-22) → PR #101 (2026-08-26) → rebase → aprovação → merge (push verde às 17:05, `fontes/git/_runs-push-main-por-dia.txt`).

### Fontes e corte

Snapshot (PR 86) com comentários de coordenação; dossiê (19 arquivos); `fontes/api-reviews/pr86-reviews.json`; `fontes/git/_runs-push-main-por-dia.txt`; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos, reviews, run verde de PR no head e de push no merge. RELATADO: 162 testes e 9/9 CI após rebase. INFERÊNCIA (do Codex, conferível no plano): evals de L6 não discriminam o comportamento anunciado. Review formal (API, observada em 2026-10-17T17:28:28Z): 2 — `luanmorenommaciel` COMMENTED em 2026-08-25; `luanmorenommaciel` APPROVED em 2026-09-14. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `be0a4d8` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 34871977860, tentativa 1, created_at 2026-09-14 16:59:24Z, run_started_at 2026-09-14 16:59:24Z, updated_at 2026-09-14 17:02:54Z (antes do merge pelo updated_at).

### Fluxo

Fluxo L6: `recall_similar_runs(job_id)` → forma de plano do run → raia memory (encoder, embeddings, limiar e piso de ruído) → formas similares → execuções históricas com configuração e resultado.

### Consequências e risco

Médio-alto valor; limite real: a garantia de aceite das unidades é mais fraca do que os nomes sugerem (C04-17). A coordenação entre #86/#87/#88 via #101 é exemplo bom de gestão de conflitos. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) corrigir os evals do plano L6 antes de qualquer reuso, como o Codex propõe.

### Dependências e paralelismo

A ferramenta está integrada na base histórica; verde no merge não certifica ausência de dependências ou toda a superfície. Governança e eventual reuso dos evals seguem N09; o gate stdio divergente segue N16 na #181, sem reabrir a PR histórica.

### Plano e aceite propostos

Condição explícita de não ação na PR. Se o plano for reusado: reescrever os evals para chamar a ferramenta com memória indisponível e forma ausente (controles negativos).

### Comunicação entre responsáveis

Para a consolidação: "PR #86 deu memória entre execuções ao MCP; os evals do plano são fracos".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — um segundo backend de embeddings daria respostas divergentes da memory. (b) Que caso o teste ainda não cobre? — memória indisponível no eval do plano. (c) Como eu explicaria isso para outro pod? — "o MCP pergunta à memory quais execuções se parecem com esta". (d) O `recall_gate.py` substitui os evals fracos?

### Próxima ação e encerramento

Nenhuma ação obrigatória. Owner a confirmar: Pod 3, se o plano L6 for reusado. Encerramento: histórico. Resíduo do gate stdio registrado como proposta N16 na #181.

<a id="item-479"></a>

## PR#87 — serve/L5: expose the verify lane over MCP as verify_fix

Frente: historico. Encaminhamento: integrada_sem_aprovacao_formal_com_ci_do_head_falho.

### Identidade e estado

PR #87, `serve/l5-fix` → `main`; autora `sidymar`; `pod-3-serve`; criada em 2026-08-20 e integrada em 2026-09-14T16:47:02Z (merge `4adb854`); 8 commits; 20 arquivos. **Única review: `COMMENTED` do mantenedor em 2026-08-25** ("Do not merge this onto today's main … wait for #101, rebase"). Não há `APPROVED` registrado, diferente de #86 e #88.

### Intenção e benefício

Expor a raia verify pelo MCP como `verify_fix`, lendo `apex.fix_verifications` (contrato v0.3), e fazer `suggest_fix` revelar o que a verify já concluiu, sem duplicar a verify.

### Feito, faltante e não comprovado

Feito no código: `ReadStore.verifications()`, `VerificationView`/`FixVerdict`, `verify_fix`, re-pin da superfície e `suggest_fix` com proveniência; testes `test_verify_fix.py` (+241), `test_verify_view.py` (+178), `test_suggest_fix_safety.py` (+206). Prova no merge: o único run com o head final (`cd59c8d`) no universo retornado, o 34868325801 (pull_request, tentativa 1, criado 16:23:37Z, concluído 16:27:31Z), **falhou no job `root six-lane gate`, passo `pytest tests/`**; os outros 10 jobs passaram (`run34868325801-jobs.json`). Heads anteriores do mesmo branch passaram (2026-08-20, 08-24, 08-26). O merge veio às 16:47:02Z, cerca de 20 minutos depois da conclusão desse run; o run de push do merge (`4adb854`, 34870745971) foi criado 16:47:05Z e concluiu com `success` às 16:50:57Z, numa árvore que já incluía a PR #121 (merge 16:46:27Z). O head `cd59c8d` foi rebaseado em 2026-09-14 (committer 16:22:57Z) sobre `8d3efa7` (merge da #100), que já continha #96 e #111; o run de PR testa a merge ref, cuja base exata a API não devolveu (`pull_requests` vazio) (`fontes/reconferencia/git-reconferencia.txt`). Leitura: a falha coincide com o run de push do merge da #98 (`3fb411a`, criado 16:22:37Z, `failure` às 16:28:02Z), cujos jobs não foram coletados. Não comprovado: a causa exata, pois o log do job não foi lido. Lado de produto: o #117 registra problemas de representação em `fix_verifications` (`to_row` sem `attributable`) que esta superfície expõe. Atualização 19/10: o gate stdio `serve/tools/mcp_stdio_gate.py` lista 7 tools na base histórica, sem `recall_similar_runs`; o último commit no arquivo é `3758d00` (#87, re-pin em seis) e nenhum commit da L6 o tocou. Leitura estática, não executada.

### Linhagem

Plano L5 → PR #87 (2026-08-20) → review COMMENTED pedindo a #101 → rebase (2026-08-26, "179 passed, 9/9 CI") → "are we good to go?" (2026-08-30) → rebase em 2026-09-14 sobre `8d3efa7` (committer 16:22:57Z) → run de PR do head falha no `pytest tests/` (16:27:31Z) → merge sem APPROVED (16:47:02Z) → run de push do merge com `success` (16:50:57Z).

### Fontes e corte

Snapshot (PR 87); dossiê; `fontes/api-reviews/pr87-reviews.json`; `fontes/api-reviews/run34868325801-jobs.json` (jobs e passos do run falho); `fontes/git/_runs-push-main-por-dia.txt` (linha do tempo de 2026-09-14); `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: ausência de APPROVED, falha do root gate no head, push verde do merge, heads anteriores verdes. INFERÊNCIA: a falha pode ter vindo da base naquela janela (coincidência temporal e `success` pós-merge numa árvore que já tinha a #121); não provado sem o log, e cancelamentos ou verdes posteriores não estabelecem causalidade. Review formal (API, observada em 2026-10-17T17:28:29Z): 1 — `luanmorenommaciel` COMMENTED em 2026-08-25. `APPROVED` humano antes do merge: não. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `cd59c8d` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request failure, run 34868325801, tentativa 1, created_at 2026-09-14 16:23:37Z, run_started_at 2026-09-14 16:23:37Z, updated_at 2026-09-14 16:27:31Z (antes do merge pelo updated_at); jobs coletados desta tentativa: 11, steps: 81.

### Fluxo

Fluxo L5: `verify_fix(job_id, finding_id?)` → `ReadStore.verifications()` → `apex.fix_verifications` → `FixVerdict`; `suggest_fix` anexa o que a verify concluiu.

### Consequências e risco

Médio. Entre as 35 PRs deste recorte integradas em agosto/setembro, é a única cujo único run do head final concluiu em `failure` antes do merge e que entrou sem `APPROVED` humano (`fontes/reconferencia/pontos03-05-06-runs-por-pr.json`, `fontes/reconferencia/ponto06-reviews.json`). Mesmo que a falha venha da main, o merge não teve prova verde do head que entrou. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Registrar a exceção na consolidação e na DEC-02 (recomendado); (b) obter o log do job falho para fechar a causa — leitura de API autenticada, fora do escopo anônimo; (c) nenhuma ação de código, porque o push pós-merge está verde.

### Dependências e paralelismo

A opção (b) depende de acesso autenticado aos logs. A política que evitaria a repetição é DEC-02 (checks exigidos).

### Plano e aceite propostos

Passo mínimo: na DEC-02, citar #87 como caso de "merge com check vermelho no head e sem aprovação" que a proteção impediria. Nenhuma execução.

### Comunicação entre responsáveis

Para a consolidação: "PR #87 entrou sem APPROVED e com o root gate vermelho no único run do head; o run de push do merge concluiu com success às 16:50:57Z".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — exigir check verde no head teria segurado a #87 até a main voltar ao verde. (b) Que caso o teste ainda não cobre? — o motivo exato da falha do `pytest tests/` (log não lido). (c) Como eu explicaria isso para outro pod? — "entrou com o CI vermelho, com causa ainda não confirmada, e o commit de merge passou logo depois". (d) A review COMMENTED pedindo rebase conta como aprovação implícita?

### Próxima ação e encerramento

Owner a confirmar: mantenedor, ao decidir a DEC-02. Entrada: este registro e os jobs do run. Saída: caso citado na política. Encerramento: a PR segue integrada.

<a id="item-480"></a>

## PR#88 — serve/L3: diagnosis readability — detail levels, coverage, explain_stage, share of tail

Frente: historico. Encaminhamento: integrada_com_review_aprovada_e_ci_verde.

### Identidade e estado

PR #88, `serve/l3-understand` → `main` (base `847d7a0`, o merge da #101); autora `sidymar`; `pod-3-serve`; criada em 2026-08-20; review `COMMENTED` (2026-08-25) e `APPROVED` (2026-09-14); integrada em 2026-09-14T16:18:37Z (merge `1125cdb`); 10 commits; 18 arquivos.

### Intenção e benefício

Tornar o diagnóstico legível: `analyze_run(detail="summary"|"stages"|"full")`, `Diagnosis.coverage` com frescor em todo caminho, `explain_stage` para descer a um stage, e enquadramento do gargalo como parcela da cauda (`tail_share`). Motivação: o run P0 real respondia com 17 stages e todos os findings num só payload.

### Feito, faltante e não comprovado

Feito: `diagnose.py` (+212), `models.py` (+62), `server.py` (+110), `test_diagnose.py` (+294), gate stdio atualizado, `docs/lanes/L4_PROPOSAL.md` (+98), plano `l3-understand.yaml` e seis specs em `tasks/done/`. Achado da autora no rebase: aceitar a versão da main de `test_server_tools.py` apagou dois testes de `explain_stage` em silêncio (144 → 142, ainda verde); ela os restaurou. A aprovação diz que a L3 "lands first so #87/#86 rebase cleanly". Atualização 19/10: as seis Task-Specs `T-20260820-*` desta perna estão em `tasks/done/` com `status: done` e `accepted: false`; o código está na main (por exemplo, `explain_stage`). É implementação sem aceite registrado, tema da governança de Task-Specs proposta na #181.

### Linhagem

Plano L3 → PR #88 → review COMMENTED → PR #101 → rebase (2026-08-26, CI verde no head) → aprovação → merge na leva de 2026-09-14.

### Fontes e corte

Snapshot (PR 88); dossiê; `fontes/api-reviews/pr88-reviews.json`; `fontes/git/_runs-push-main-por-dia.txt`; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos, reviews, run verde de PR no head (2026-08-26). RELATADO: a perda e a restauração dos dois testes. O push do merge foi cancelado pela concorrência. Review formal (API, observada em 2026-10-17T17:28:30Z): 2 — `luanmorenommaciel` COMMENTED em 2026-08-25; `luanmorenommaciel` APPROVED em 2026-09-14. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `9ff859b` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 32976688967, tentativa 1, created_at 2026-08-26 13:51:16Z, run_started_at 2026-08-26 13:51:16Z, updated_at 2026-08-26 13:54:04Z (antes do merge pelo updated_at).

### Fluxo

Fluxo L3: `analyze_run(job_id, detail)` → mesma análise, três larguras → `coverage` → `explain_stage(job_id, stage_id)` → `tail_share` aponta onde a cauda pesa.

### Consequências e risco

Alto valor de uso. Lição de processo valiosa: resolver conflito pegando a versão da main pode apagar testes sem deixar o CI vermelho. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Preservar o histórico e levar a diferença entre implementação e aceite para N09. Para futuros rebases, conferir cenários e diff dos testes; contagem mínima é alternativa fraca, pois quantidade não garante comportamento.

### Dependências e paralelismo

Nenhuma dependência pendente: a PR entrou depois da #101 e antes de #87/#86, como a aprovação pedia. A ideia (b) é independente e não exige mudança de produto.

### Plano e aceite propostos

Condição explícita de não ação: integrada com aprovação e CI verde no head.

### Comunicação entre responsáveis

Para a consolidação: "PR #88 deu níveis de detalhe ao diagnóstico; o rebase quase apagou dois testes sem alarme".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — um payload único com 17 stages esconde o gargalo. (b) Que caso o teste ainda não cobre? — teste removido em conflito sem o CI notar. (c) Como eu explicaria isso para outro pod? — "primeiro o veredito; detalhe só quando pedir". (d) Como detectar testes que somem num rebase?

### Próxima ação e encerramento

Sem reabertura automática da PR integrada. Encaminhar os seis aceites pendentes para a governança N09, com responsável e critério a combinar; eventual reuso do plano exige prova discriminante.

