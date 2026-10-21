# Fichas documentais — lote 49

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-481"></a>

## PR#89 — engine: retry-safe telemetry — reachability + the retry_pressure watcher

Frente: historico. Encaminhamento: integrada_com_review_aprovada_e_ci_verde.

### Identidade e estado

PR #89, `candidate/retry-safe-stage-fields` → `main`; autor `gustocezar` (commits de "Augusto Cezar" e "Augusto Silva"); `pod-2-engine`; criada em 2026-08-20, aprovada em 2026-08-25 e integrada em 2026-09-14T16:17:47Z (merge `c67ba0e`); 11 commits; 13 arquivos. O #90 a cita.

### Intenção e benefício

Fazer o engine ler os ~15 campos seguros a retry do contrato v0.5 (que o JAR já emitia e ninguém lia): campos brutos em `StageAggregate`, propriedades `effective_*` que preferem o subconjunto de tasks bem-sucedidas quando há amostra, e o sexto watcher determinístico, `retry_pressure`.

### Feito, faltante e não comprovado

Feito: `schema.py` (+73), `clickhouse.py` (+52), `validation.py` (+30), `watchers/retry_pressure.py` (+66), testes em quatro arquivos, quatro Task-Specs em `tasks/`. A aprovação: "the sixth deterministic watcher … reports scheduler-budget use at INFO. It does not guess a root cause". O `retry_pressure` aparece na lista de watchers da main (conferido para o #17). As quatro Task-Specs foram criadas em `tasks/T-2026081*`/`T-2026082*`, não em `tasks/done/`; o fechamento delas é assunto do NOV-06/DEC-N7. A decisão de passar o `skew_ratio` para os campos seguros veio depois, na PR #99 (#90).

### Linhagem

Contrato v0.5 (PR #80) → PR #89 (2026-08-20) → aprovação (2026-08-25) → merge na leva de 2026-09-14 → PR #99 (`skew_ratio` seguro a retry).

### Fontes e corte

Snapshot (PR 89); dossiê (13 arquivos, 11 commits); `fontes/api-reviews/pr89-reviews.json`; `fontes/git/_runs-push-main-por-dia.txt`; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos, review, run verde de PR no head (2026-08-22). RELATADO: cobertura dos caminhos de fallback. O push do merge foi cancelado pela concorrência da leva. Review formal (API, observada em 2026-10-17T17:28:30Z): 1 — `luanmorenommaciel` APPROVED em 2026-08-25. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `c731aca` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 32545708655, tentativa 1, created_at 2026-08-22 02:14:37Z, run_started_at 2026-08-22 02:14:37Z, updated_at 2026-08-22 02:18:04Z (antes do merge pelo updated_at).

### Fluxo

Fluxo: `spark_events` (campos v0.5) → `StageAggregate` → `effective_*` (sucesso se `sample_count > 0`, senão legado) → watchers; `retry_pressure` informa o uso do orçamento de falhas do scheduler.

### Consequências e risco

Médio-alto: fechou a lacuna "o JAR emite, ninguém lê". Limite: as quatro Task-Specs continuam fora de `tasks/done/` (achado de processo da v2). Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) mover as quatro specs para `done/` com evidência, dentro da regra da DEC-N7.

### Dependências e paralelismo

A opção (b) depende da DEC-N7 (quem fecha Task-Specs); o código desta PR não tem dependência pendente e já é lido pela PR #99.

### Plano e aceite propostos

Condição explícita de não ação na PR. O fechamento das specs segue a regra que a DEC-N7 vier a definir.

### Comunicação entre responsáveis

Para a consolidação: "PR #89 fez o engine ler os campos seguros a retry e criou o `retry_pressure`".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — usar só percentis de todas as tentativas deixaria retries inflarem as métricas. (b) Que caso o teste ainda não cobre? — stage com amostra de sucesso pequena. (c) Como eu explicaria isso para outro pod? — "o engine passou a usar as tasks que deram certo quando há dado". (d) As quatro specs desta PR devem ir para `done/`?

### Próxima ação e encerramento

Nenhuma ação obrigatória. Owner a confirmar: quem decidir a DEC-N7. Encerramento: histórico.

<a id="item-482"></a>

## PR#91 — jar: prove listener sink failure never breaks the job (#36)

Frente: historico. Encaminhamento: integrada_com_review_aprovada_apos_mudancas.

### Identidade e estado

PR #91, `candidate/listener-failure-isolation-test` → `main`; autor `gustocezar`; `pod-2-engine`; criada em 2026-08-21; `CHANGES_REQUESTED` em 2026-08-25, `APPROVED` em 2026-08-26; integrada em 2026-09-14T16:17:51Z (merge `3a11690`); 3 commits; 1 arquivo de teste (+210). Nenhum código de produção alterado.

### Intenção e benefício

Provar com um `SparkContext` real que uma falha do sink do listener nunca derruba o job e que fica registrada, fechando o item do DoD do #36 que só tinha o código como evidência.

### Feito, faltante e não comprovado

Feito: `ListenerFailureIsolationSpec.scala` com `ThrowingSink` e `StackAwareThrowingSink`, cobrindo o caminho RDD e o caminho SQL/`flushExecution`. A primeira review aprovou a prova, mas pediu que o WARN fosse afirmado; o commit de 2026-08-26 acrescenta asserções da mensagem nos dois caminhos (`apex: onStageCompleted failed for stage N: injected-test-failure` e `apex: onOtherEvent failed`), conferidas na main (`fontes/git/_36.txt`). Detalhe de linhagem: o #36 foi fechado em 2026-08-21, citando esta PR antes de ela ser revisada e integrada.

### Linhagem

#36 (DoD) → PR #91 (2026-08-21) → mudança pedida (WARN) → aprovação (2026-08-26) → merge na leva de 2026-09-14 (push cancelado pela concorrência; próximo `success` na main concluído às 16:50:57Z, no merge da #87, `fontes/git/_runs-push-main-por-dia.txt`).

### Fontes e corte

Snapshot (PR 91); dossiê; `fontes/api-reviews/pr91-reviews.json`; `fontes/git/_36.txt`; `fontes/git/_runs-push-main-por-dia.txt`; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivo de teste, asserções de WARN, ciclo de review, CI verde de PR no head (2026-08-26). RELATADO: saída `All tests passed` com 5 jobs reais. Review formal (API, observada em 2026-10-17T17:28:31Z): 2 — `luanmorenommaciel` CHANGES_REQUESTED em 2026-08-25; `luanmorenommaciel` APPROVED em 2026-08-26. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `2b735df` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 32973502939, tentativa 1, created_at 2026-08-26 13:19:20Z, run_started_at 2026-08-26 13:19:20Z, updated_at 2026-08-26 13:22:58Z (antes do merge pelo updated_at).

### Fluxo

Fluxo testado: job Spark real → callback do listener → `emit` lança → `Try` captura → WARN com stage e causa → job termina; listener segue no bus.

### Consequências e risco

Médio-alto valor: transforma uma propriedade de segurança do produto ("não quebrar o job do cliente") em teste. Limite: sink de teste, não sink OTLP real com rede. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) acrescentar um caso com o exportador OTLP real apontado para um endpoint inexistente, se a v1 afirmar isolamento de falha de rede.

### Dependências e paralelismo

A opção (b) depende de a release citar isolamento de rede; não há dependência técnica pendente nesta PR.

### Plano e aceite propostos

Condição explícita de não ação: prova integrada com review e mudança atendida.

### Comunicação entre responsáveis

Para a consolidação: "PR #91 prova que falha do Apex não derruba o job; o #36 fechou antes de ela entrar".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — sem a asserção de WARN, a falha poderia ser engolida em silêncio e o teste ainda passaria. (b) Que caso o teste ainda não cobre? — exportador OTLP real sem rede. (c) Como eu explicaria isso para outro pod? — "se o sink falha, o job do cliente não percebe; só sai um aviso". (d) A release vai afirmar isolamento de falha de rede?

### Próxima ação e encerramento

Nenhuma ação obrigatória. Owner a confirmar: raia jar, para a opção (b). Encerramento: histórico.

<a id="item-483"></a>

## PR#92 — dev: cover scripts/apex.ps1 with dry-run and secrets contract tests

Frente: historico. Encaminhamento: integrada_com_review_aprovada_teste_compara_handler.

### Identidade e estado

PR #92, `candidate/initial-package-tests` → `main`; autor `gustocezar`; `pod-2-engine`; criada em 2026-08-21, aprovada em 2026-08-25 e integrada em 2026-09-14T16:17:55Z (merge `a1ae77d`); 1 commit; 2 arquivos (`.gitignore` +3, `tests/test_apex_initial_package.py` +112).

### Intenção e benefício

Dar cobertura ao `scripts/apex.ps1` da PR #76 (que tinha zero testes): dry-run sem mutação para as 8 ações, segredos gerados localmente sem chaves literais nem comandos destrutivos, exigência de PowerShell 7 sem fallback, e `.apex/` fora do versionamento.

### Feito, faltante e não comprovado

Feito: 7 funções de teste e a correção do vazamento `.apex/` no `.gitignore`. A aprovação: "`.apex/` is now ignored. That was the leak … Dry-run and secrets checks are source-plus-dry-run, and CI is 9/9". Limite apontado depois pelo Codex (C04-12, ligado à issue #124, aberta): o teste de dispatch executa `-DryRun` e compara a string `Handler`, e o ramo retorna antes do scriptblock `Command`; trocar só o `Command` não falharia o teste. A PR #128 (2026-10-06) tratou cobertura de pwsh do #124; a força da prova do dispatcher segue aberta. Reconfirmado em 19/10 na main: `-DryRun` imprime o rótulo `Handler` declarado ao lado do `Command`, e só `help` é despachado de fato (`scripts/apex.ps1:734-806`; `tests/test_apex_initial_package.py:17-80`).

### Linhagem

PR #76 (pacote sem testes) → PR #92 (2026-08-21) → aprovação (2026-08-25) → merge na leva de 2026-09-14 → #124 aberta sobre a força do teste → PR #128.

### Fontes e corte

Snapshot (PR 92); dossiê; `fontes/api-reviews/pr92-reviews.json`; `D-CORRECOES-E-LIMITES.md` do Codex (C04-12), lido como alegação; `fontes/git/_runs-push-main-por-dia.txt`; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos, review, CI verde de PR no head. RELATADO pelo Codex e coerente com o código conferido no #64 (o dispatcher retorna `[PSCustomObject]@{ Handler = …; Command = { … } }`): a comparação por `Handler` não exercita `Command`. Review formal (API, observada em 2026-10-17T17:28:31Z): 1 — `luanmorenommaciel` APPROVED em 2026-08-25. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `729587f` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 32439176561, tentativa 1, created_at 2026-08-21 02:14:49Z, run_started_at 2026-08-21 02:14:49Z, updated_at 2026-08-21 02:17:56Z (antes do merge pelo updated_at).

### Fluxo

Fluxo testado: `apex.ps1 <ação> -DryRun` → dispatcher devolve `Handler` e `Command` → teste lê `APEX_DRY_RUN=passed … mutations=0` e o nome do `Handler`.

### Consequências e risco

Médio: a PR fechou um vazamento real (`.apex/`) e criou a primeira rede de segurança do pacote, mas a prova do mapeamento ação → handler é fraca, como o #124 registra. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter como histórico e apontar o limite para o #124 (recomendado); (b) teste discriminante com handlers inofensivos que provem a chamada do `Command`, como o Codex propõe; (c) reabrir — o trabalho continua no #124.

### Dependências e paralelismo

A opção (b) é o critério aberto do #124 (ver ficha #124 do Codex); não há dependência para a PR em si.

### Plano e aceite propostos

Condição explícita de não ação nesta PR; o passo que falta (controle discriminante sobre `Command`) pertence ao #124.

### Comunicação entre responsáveis

Para a consolidação: "PR #92 trouxe os primeiros testes do pacote; o de dispatch compara só o nome do handler".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — sem o `.gitignore`, segredos locais em `.apex/` poderiam ir para o Git. (b) Que caso o teste ainda não cobre? — `Command` trocado com `Handler` igual. (c) Como eu explicaria isso para outro pod? — "o teste confere o nome de quem seria chamado, não a chamada". (d) O teste do #124 vai substituir este ou somar?

### Próxima ação e encerramento

Nenhuma ação nesta PR. Owner do critério aberto: responsável pelo #124. Encerramento: histórico.

<a id="item-484"></a>

## PR#93 — docs: propose AQE re-plan detection decision

Frente: historico. Encaminhamento: fechada_sem_merge_substituida_pela_pr98.

### Identidade e estado

PR #93, `codex/issue65-aqe-decision-docs` → `main`; autor `gustocezar` (commits de "Augusto Silva"); criada em 2026-08-21; `CHANGES_REQUESTED` em 2026-08-25; fechada **sem merge** em 2026-09-14 pelo mantenedor; 2 commits; 1 arquivo de documentação. Ligada ao registro L02 e ao #65.

### Intenção e benefício

Propor por escrito a decisão de detecção de re-plano do AQE (#65), só documentação, sem ser pré-requisito técnico da PR #98.

### Feito, faltante e não comprovado

Não integrada: substituída pela PR #98, que consolidou o `ADR-003-AQE-REPLAN-DETECTION.md`. A review de 2026-08-25 pediu renomear para `ADR-003-...` e fechar lacunas; o comentário de fechamento: "Keeping this separate ISSUE-65 proposta would leave two decision files for the same call — the exact gap the Aug 25 review called out". O arquivo `ISSUE-65-AQE-REPLAN-DETECTION-DECISION-20260820.md` não está na main; a #98 trouxe um `ISSUE-65-AQE-REPLAN-DETECTION-DECISION.md` (+18) curto como registro de linhagem.

### Linhagem

#65 → PR #93 (docs) e PR #98 (código) em paralelo → review pede consolidação → PR #98 traz o ADR-003 → PR #93 fechada (2026-09-14).

### Fontes e corte

Snapshot (PR 93) e comentário de fechamento; dossiê; `fontes/api-reviews/pr93-reviews.json`; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: fechamento sem merge, review, arquivo ausente na main. DECISÃO: registrada no fechamento e no ADR-003 da #98. Review formal (API, observada em 2026-10-17T17:28:32Z): 1 — `luanmorenommaciel` CHANGES_REQUESTED em 2026-08-25. Comentários inline de review: 0. Runs do Actions com o head `237de62` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 32593818833, tentativa 1, created_at 2026-08-22 19:28:40Z, run_started_at 2026-08-22 19:28:40Z, updated_at 2026-08-22 19:32:17Z.

### Fluxo

Fluxo de decisão: proposta documental → review pede formato ADR → consolidação na PR de implementação → fechamento da proposta.

### Consequências e risco

Baixo: evitou dois registros de decisão concorrentes, o que é bom. O conteúdo histórico só sobrevive no branch e no resumo da #98. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) o head `237de62` não está no bundle do #105, mas segue acessível pela ref de PR do GitHub; incluí-lo no bundle só se o texto completo tiver valor histórico.

### Dependências e paralelismo

A preservação da branch depende do #105; não há dependência técnica.

### Plano e aceite propostos

Condição explícita de não ação: decisão consolidada em outro documento.

### Comunicação entre responsáveis

Para a consolidação: "PR #93 foi fechada a favor do ADR-003 da #98".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — dois documentos de decisão para o mesmo tema confundiriam qual vale. (b) Que caso o teste ainda não cobre? — não encontrei teste ligado a este item nas fontes lidas; é documento. (c) Como eu explicaria isso para outro pod? — "a proposta virou o ADR-003". (d) O texto longo da proposta tem algo que o ADR-003 perdeu?

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: histórico; a branch segue o plano do #105.

<a id="item-485"></a>

## PR#94 — engine: fail in CI when the SQL reads a column no DDL declares

Frente: historico. Encaminhamento: integrada_com_review_aprovada_apos_mudancas.

### Identidade e estado

PR #94, `test/sql-columns-match-ddl` → `main`; autor `gustocezar`; `pod-2-engine`; criada em 2026-08-22; `CHANGES_REQUESTED` em 2026-08-25, `APPROVED` em 2026-08-26; integrada em 2026-09-14T16:17:59Z (merge `1b990a8`); 2 commits; 1 arquivo de teste (+122). Ligada ao registro E19.

### Intenção e benefício

Fazer o CI falhar quando uma consulta do engine lê uma coluna que nenhum DDL declara, já que o CI não tem ClickHouse e os 11 testes de integração são pulados ("97 passed, 11 skipped").

### Feito, faltante e não comprovado

Feito: `engine/tests/test_sql_columns_exist_in_ddl.py` extrai as colunas lidas por `STAGE_AGGREGATES_SQL` e `STAGE_EVENTS_SQL` e as declaradas pelos DDLs e migrações aditivas. A primeira review achou um buraco: o extrator subtraía todo `AS <alias>` do conjunto, então `argMax(fake, ts) AS fake` passava; o commit de 2026-08-26 remove o alias do texto em vez de subtrair do conjunto, e a aprovação confirma. É a base estática que as PRs #131 (preflight em runtime) e #155 (aberta) reaproveitam.

### Linhagem

Erro `Code: 47` observado → PR #94 (2026-08-22) → buraco do alias → correção → aprovação (2026-08-26) → merge na leva de 2026-09-14 → preflight de runtime (#95/PR #131) → alinhamento fino (#154/PR #155, abertas).

### Fontes e corte

Snapshot (PR 94); dossiê; `fontes/api-reviews/pr94-reviews.json`; `fontes/git/_runs-push-main-por-dia.txt`; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivo de teste, reviews com o buraco e a correção, CI verde de PR no head (2026-08-26). Limite declarado: o extrator usa regex e exclusões, não um parser SQL completo (observação também do Codex na ficha #155). Review formal (API, observada em 2026-10-17T17:28:33Z): 2 — `luanmorenommaciel` CHANGES_REQUESTED em 2026-08-25; `luanmorenommaciel` APPROVED em 2026-08-26. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `f9f0457` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 32973509064, tentativa 1, created_at 2026-08-26 13:19:24Z, run_started_at 2026-08-26 13:19:24Z, updated_at 2026-08-26 13:22:25Z (antes do merge pelo updated_at).

### Fluxo

Fluxo do gate estático: SQL do engine → extrator de colunas (sem aliases) → conjunto lido ⊆ colunas declaradas nos DDLs → senão, falha no CI com o nome da coluna.

### Consequências e risco

Médio-alto: pega no CI uma classe de erro que só apareceria em runtime. Limite: parser por regex pode não ver colunas dentro de funções ClickHouse; isso é exatamente o ponto aberto do #154. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) seguir no #154/PR #155 o endurecimento do extrator.

### Dependências e paralelismo

O endurecimento depende do #154 e da PR #155 (abertas, fila M1).

### Plano e aceite propostos

Condição explícita de não ação nesta PR; a evolução está na fila M1.

### Comunicação entre responsáveis

Para a consolidação: "PR #94 criou o gate estático SQL × DDL; o buraco do alias foi achado na review".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — sem o gate, uma coluna inexistente chegaria verde à review. (b) Que caso o teste ainda não cobre? — coluna lida dentro de função, como `SHAPE_HISTORY_SQL` (#154). (c) Como eu explicaria isso para outro pod? — "o CI confere que toda coluna consultada existe em algum DDL". (d) Vale trocar regex por um parser SQL?

### Próxima ação e encerramento

Nenhuma ação nesta PR. Owner da evolução: responsável pela #155. Encerramento: histórico.

<a id="item-486"></a>

## PR#96 — feat(jar): preserve Spark SQL execution_id on apex.stage spans

Frente: historico. Encaminhamento: integrada_com_review_aprovada_quebrou_matriz_na_leva.

### Identidade e estado

PR #96, `codex/stage-execution-id-pr-prep` → `main`; autor `gustocezar` (commit de "Augusto Silva"); criada em 2026-08-23, aprovada em 2026-08-25 e integrada em 2026-09-14T16:18:04Z (merge `fc5cbee`); 1 commit; 8 arquivos.

### Intenção e benefício

Preservar o `execution_id` do Spark SQL nos spans `apex.stage`, como atributo Int64 opcional e aditivo (contrato v0.6), para permitir no futuro correlacionar evidência de AQE por execução com os stages que a produziram.

### Feito, faltante e não comprovado

Feito: `ApexStageEvent`, `ApexOtelSink` e `ApexStageListener` carregam o campo (+1 linha cada); `ApexOtelSinkSpec.scala` (+130) e `DriverActivationSpec` (+33); `CONTRACT.md` sobe para v0.6; Task-Spec `STAGE-EXECUTION-ID.md`. A aprovação: "Additive v0.6 … RDD and history omit the key. No sentinel". Efeito colateral na leva de 2026-09-14: o `tests/test_telemetry_compatibility_matrix.py` da PR #111, integrada dois minutos depois, esperava contrato v0.5; segundo o corpo da #121 (RELATO), isso quebrou o root gate da main; nos runs, o push do merge da #98 (`3fb411a`) concluiu em `failure` às 16:28:02Z, e o próximo `success` na main foi o do merge da #87 (`4adb854`) às 16:50:57Z, depois da #121 (merge 16:46:27Z); os jobs do run falho não foram coletados (`fontes/reconferencia/pontos08-09-tempos-de-runs.json`).

### Linhagem

Task-Spec → PR #96 (2026-08-23) → aprovação (2026-08-25) → merge 16:18:04 → PR #111 (16:20:02) com a matriz em v0.5 → `failure` no push do merge da #98 (concluído 16:28:02Z) → PR #121 (merge 16:46:27Z) → `success` no push do merge da #87 (concluído 16:50:57Z). A atribuição de execução a stages segue na #115.

### Fontes e corte

Snapshot (PR 96); dossiê; `fontes/api-reviews/pr96-reviews.json`; corpo da PR #121; `fontes/git/_runs-push-main-por-dia.txt`; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos, review, CI verde de PR no head (2026-08-23), linha do tempo dos pushes. RELATO (corpo da #121): a falha da main veio da combinação #96 + #111. FATO: cada uma tinha run de PR verde no próprio head semanas antes (#96 em 2026-08-23, #111 em 2026-08-29). A causalidade não foi observada diretamente: os jobs do run falho não foram coletados. Review formal (API, observada em 2026-10-17T17:28:33Z): 1 — `luanmorenommaciel` APPROVED em 2026-08-25. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `155c44b` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 32613002969, tentativa 1, created_at 2026-08-23 02:30:00Z, run_started_at 2026-08-23 02:30:00Z, updated_at 2026-08-23 02:33:14Z (antes do merge pelo updated_at).

### Fluxo

Fluxo do campo: Spark fornece `spark.sql.execution.id` → listener associa stage → `ApexStageEvent.executionId` → atributo `execution_id` no span → (futuro) correlação com AQE.

### Consequências e risco

Médio. Lição de processo, segundo o relato da #121: duas PRs verdes sozinhas quebraram a main juntas porque uma mudou a versão do contrato e a outra a fixava. Na leva, os pushes intermediários foram cancelados; entre a conclusão do primeiro run em `failure` (16:28:02Z) e a do primeiro `success` seguinte na main (16:50:57Z) passaram ~23 min (24 min pelos created_at). Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter como histórico e registrar a lição na DEC-N4 (método de integração) (recomendado); (b) exigir rebase e CI atual antes de cada merge de uma leva, que é o que a DEC-N4 discute.

### Dependências e paralelismo

A opção (b) depende da DEC-N4 e da DEC-02; não há dependência técnica pendente nesta PR. O mapa execution→stage que este campo permite continua aberto na #115; a correlação com linha de código é outra decisão (ADR-004).

### Plano e aceite propostos

Condição explícita de não ação nesta PR. Passo de processo: citar o par #96/#111 como exemplo na DEC-N4.

### Comunicação entre responsáveis

Para a consolidação: "PR #96 trouxe o contrato v0.6; segundo a #121, somada à #111 quebrou o root gate da main, que voltou a ter success observado às 16:50:57Z".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — um sentinela no lugar de omitir o campo poluiria eventos RDD e históricos. (b) Que caso o teste ainda não cobre? — duas PRs que mudam e fixam a versão do contrato integradas juntas. (c) Como eu explicaria isso para outro pod? — "o stage agora carrega o id da execução SQL, quando existe". (d) A fila M1 vai integrar com rebase entre cada merge?

### Próxima ação e encerramento

Nenhuma ação nesta PR. Owner da lição de processo: mantenedor (DEC-N4). Encerramento: histórico.

<a id="item-487"></a>

## PR#97 — docs(ui): define read-only Compare, Memory, and Verify contracts

Frente: historico. Encaminhamento: integrada_com_review_aprovada_documental.

### Identidade e estado

PR #97, `codex/ui43-b-compare-memory-verify-read-only` → `main`; autor `gustocezar` (commit de "Augusto Silva"); criada em 2026-08-23, aprovada em 2026-08-25 e integrada em 2026-09-14T16:18:08Z (merge `889ac9d`); 1 commit; 2 arquivos de documentação.

### Intenção e benefício

Definir os contratos de leitura das telas Compare, Memory e Verify: estados obrigatórios, fronteiras de evidência, tratamento de conteúdo não confiável e política de fixtures, sem implementar nada.

### Feito, faltante e não comprovado

Feito como documentação: `docs/architecture/UI43-B-COMPARE-MEMORY-VERIFY-READ-ONLY.md` (+100) e a Task-Spec homônima (+145). É o documento que o fechamento do #43 cita como entrega do spike. O corpo lista decisões do dono pendentes antes de implementar (stack, local, design system, transporte browser → APEX, superfície versionada para Memory e Verify); parte foi respondida depois pela PR #100 (Vite + React, nginx → ClickHouse). A aprovação: "not_comparable is a result. Predictions stay predictions. null is not 0%".

### Linhagem

Spike #43 → PR #97 (2026-08-23) → aprovação (2026-08-25) → merge na leva de 2026-09-14 → implementação da console (PR #100, mesmo dia) → follow-ups #116/#118–#120.

### Fontes e corte

Snapshot (PR 97); dossiê; `fontes/api-reviews/pr97-reviews.json`; `fontes/git/_runs-push-main-por-dia.txt`; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos e review. DECISÃO PENDENTE na época: as cinco escolhas do dono; algumas foram tomadas de fato pela PR #100, sem registro de decisão separado. Review formal (API, observada em 2026-10-17T17:28:34Z): 1 — `luanmorenommaciel` APPROVED em 2026-08-25. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `4a26781` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 32619651733, tentativa 1, created_at 2026-08-23 05:09:30Z, run_started_at 2026-08-23 05:09:30Z, updated_at 2026-08-23 05:12:42Z (antes do merge pelo updated_at).

### Fluxo

Fluxo das telas: dado do store → estado da fonte (loading, erro, vazio, dado) → apresentação que não converte `null` em 0% nem predição em resultado.

### Consequências e risco

Baixo risco; valor alto como especificação. Limite: decisões de transporte e versionamento de Memory/Verify seguem em aberto (#122, #171). Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) marcar na consolidação quais das cinco decisões a PR #100 tomou de fato.

### Dependências e paralelismo

As decisões restantes dependem de DEC-07 (#122) e DEC-08 (#171).

### Plano e aceite propostos

Condição explícita de não ação: documento integrado; as decisões abertas têm issues próprias.

### Comunicação entre responsáveis

Para a consolidação: "PR #97 especificou as telas de leitura; a PR #100 as implementou".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — mostrar `null` como 0% faria a tela afirmar um resultado inexistente. (b) Que caso o teste ainda não cobre? — conteúdo não confiável vindo do store renderizado na tela. (c) Como eu explicaria isso para outro pod? — "cada tela diz de onde vem o dado e quando não sabe". (d) Quem decide o transporte de Memory e Verify para o browser?

### Próxima ação e encerramento

Nenhuma ação nesta PR. Owner das decisões abertas: donos de DEC-07/DEC-08. Encerramento: histórico.

<a id="item-488"></a>

## PR#98 — jar: combine AQE join alignment with skew partition counts

Frente: historico. Encaminhamento: integrada_com_review_aprovada_decisao_registrada.

### Identidade e estado

PR #98, `codex/issue65-combined-20260823` → `main` (base `847d7a0`); autor `gustocezar` (commits de "Augusto Cezar" e "Augusto Silva"); criada em 2026-08-23; `CHANGES_REQUESTED` em 2026-08-25, `APPROVED` em 2026-09-14 ("Commander decision: ship option 3"); integrada em 2026-09-14T16:22:35Z (merge `3fb411a`); 3 commits; 6 arquivos.

### Intenção e benefício

Implementar a opção 3 do #65: detector combinado que alinha as sequências de joins antes/depois como problema de edição (inserção ou remoção não gera `join_switch` falso) mantendo os acumuladores de skew, e consolidar a decisão num ADR.

### Feito, faltante e não comprovado

Feito: `ApexAqeListener.scala` (+71/-11), `AqeAlignmentSpec.scala` (+68), `AqeAlignmentBenchmarkSpec.scala` (+29), `ADR-003-AQE-REPLAN-DETECTION.md` (+156), registro curto e Task-Spec do #65. Conferido para o #65: os specs existem em `1e0ba80`; o ADR-003 dizia "proposed" em `1e0ba80` e "accepted (PR #98 approved and merged 2026-09-14)" na main. O run de push do merge da #98 (`3fb411a`, 34868220960, criado 16:22:37Z, `failure` às 16:28:02Z) é o único `failure` entre os 19 runs de push da main de 2026-09-14 no universo retornado (15 `cancelled`, 3 `success`); a causa atribuída é a matriz de telemetria (#96 + #111), segundo o corpo da #121 (RELATO; jobs desse run não coletados, `fontes/reconferencia/pontos08-09-tempos-de-runs.json`). Reconfirmado em 19/10: o ADR-003 na main diz "accepted (PR #98 approved and merged 2026-09-14)".

### Linhagem

#65 → PR #93 (docs) e PR #98 (código) → review pede consolidação → ADR-003 nesta PR → aprovação com a decisão → merge → run de push do merge em `failure` (atribuído à matriz pelo corpo da #121) → PR #121 → `success` no push do merge da #87. A #93 foi fechada como substituída.

### Fontes e corte

Snapshot (PR 98); dossiê; `fontes/api-reviews/pr98-reviews.json`; `fontes/git/_65.txt`; `fontes/git/_runs-push-main-por-dia.txt`; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos, reviews, status do ADR nos dois SHAs, CI verde de PR no head (2026-08-29), push do merge falho. RELATADO: 53 ms com 2.000 joins (sintético) e teto prático de ~100 joins. Review formal (API, observada em 2026-10-17T17:28:34Z): 2 — `luanmorenommaciel` CHANGES_REQUESTED em 2026-08-25; `luanmorenommaciel` APPROVED em 2026-09-14. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `8c0739e` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 33271688168, tentativa 1, created_at 2026-08-29 19:45:28Z, run_started_at 2026-08-29 19:45:28Z, updated_at 2026-08-29 19:48:43Z (antes do merge pelo updated_at).

### Fluxo

Fluxo de detecção: plano antes/depois → alinhamento por edição das joins → transições `join_switch` só onde há troca real → contagem acumulada de partições com skew.

### Consequências e risco

Médio-alto: decisão de produto registrada como aprovação e ADR. Segundo o corpo da #121, o push vermelho do merge não vem desta PR; a combinação com a main de 2026-09-14 não teve run verde antes do merge (o run de PR do head é de 2026-08-29). Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) nenhuma correção; o follow-up de status do ADR foi cumprido.

### Dependências e paralelismo

Nenhuma dependência pendente; o status do ADR foi atualizado depois na main.

### Plano e aceite propostos

Condição explícita de não ação: decisão, código, testes e ADR na main.

### Comunicação entre responsáveis

Para a consolidação: PR #98 implementou e registrou a decisão do #65; o push do merge falhou. Atribuir a falha à matriz é relato da #121, não causalidade comprovada pelo log nesta auditoria.

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — sem o alinhamento, uma join inserida geraria cascata de `join_switch` falsos. (b) Que caso o teste ainda não cobre? — plano real com milhares de joins. (c) Como eu explicaria isso para outro pod? — "o detector entende inserções de join e mantém a contagem de skew". (d) Uma aprovação de PR é o lugar certo para registrar decisão de produto?

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: histórico; reabrir só se o detector combinado gerar `join_switch` falso em plano real.

<a id="item-489"></a>

## PR#99 — engine: make skew_ratio retry-safe

Frente: historico. Encaminhamento: integrada_com_review_aprovada_apos_mudancas.

### Identidade e estado

PR #99, `codex/issue90-current-20260823` → `main` (base `4adb854`, o merge da #87); autor `gustocezar`; criada em 2026-08-23; `CHANGES_REQUESTED` em 2026-08-25, `APPROVED` em 2026-09-14; integrada em 2026-09-14T16:54:08Z (merge `926bce8`); 2 commits, um deles com autor de commit "Cursor Agent" (2026-09-14, documentação do `CONTRACT.md`); 9 arquivos. Ligada ao registro S14.

### Intenção e benefício

Tornar o `skew_ratio` público do engine seguro a retry: usar os percentis de tasks bem-sucedidas quando `successful_task_sample_count > 0`, manter o legado para linhas históricas, preservar `legacy_skew_ratio` nos detalhes e não misturar históricos de populações diferentes no piso de ruído.

### Feito, faltante e não comprovado

Feito, conferido para o #90 (`fontes/git/_90.txt`): `schema.py` com `effective_task_duration_*`, `legacy_skew_ratio` e a escolha de população; `context.py`, `clickhouse.py`, `watchers/skew.py`; testes em `test_watchers.py`, `test_physics_rules.py`, `test_clickhouse_boundary.py`; Task-Spec `ISSUE-90-RETRY-SAFE-SKEW.md`. A primeira review apontou dois bloqueios (o primeiro: "No checks on …" o head daquele momento); a aprovação final diz que o `CONTRACT.md` documenta o comportamento. Run de PR no head final concluído com `success` às 16:51:21Z (34870838119, criado 16:48:00Z), antes do merge (16:54:08Z); run de push do merge (`926bce8`, 34871459623) criado 16:54:11Z e concluído com `success` às 16:57:45Z (`fontes/reconferencia/pontos03-05-06-runs-por-pr.json`).

### Linhagem

#90 (pergunta) → PR #89 (campos) → PR #99 baseada no head da #89 → review com bloqueios → commit com autor "Cursor Agent" no `CONTRACT.md` → aprovação → merge às 16:54:08Z, depois de o run de push do merge da #87 concluir com `success` (16:50:57Z).

### Fontes e corte

Snapshot (PR 99); dossiê; `fontes/api-reviews/pr99-reviews.json`; `fontes/git/_90.txt`; `fontes/git/_runs-push-main-por-dia.txt`; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: código, reviews, runs verdes no head e no push. RELATADO: nenhum limiar de severidade ou confiança mudou (afirmação do corpo, não reconferida linha a linha). Review formal (API, observada em 2026-10-17T17:28:35Z): 2 — `luanmorenommaciel` CHANGES_REQUESTED em 2026-08-25; `luanmorenommaciel` APPROVED em 2026-09-14. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `4c3ad27` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 34870838119, tentativa 1, created_at 2026-09-14 16:48:00Z, run_started_at 2026-09-14 16:48:00Z, updated_at 2026-09-14 16:51:21Z (antes do merge pelo updated_at).

### Fluxo

Fluxo: stage → `successful_task_sample_count > 0`? → p99/p50 bem-sucedidas : legado → `skew_ratio` → tail-bound e evidência na mesma população → `legacy_skew_ratio` nos detalhes.

### Consequências e risco

Médio-alto: muda valores de findings em stages com retry, de forma intencional e documentada. Limite: findings antigos não são recalculados. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) nenhuma alternativa: decisão do #90 tomada e entregue.

### Dependências e paralelismo

Nenhuma dependência pendente: a base (#89) e a documentação do contrato entraram antes do merge.

### Plano e aceite propostos

Condição explícita de não ação: entregue com aprovação e CI verde no head e no push.

### Comunicação entre responsáveis

Para a consolidação: "PR #99 entregou o skew seguro a retry pedido no #90".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — misturar históricos legados e bem-sucedidos produziria um piso de ruído falso. (b) Que caso o teste ainda não cobre? — shape com histórico só legado e run novo só bem-sucedido. (c) Como eu explicaria isso para outro pod? — "o skew ignora tentativas repetidas quando há dado e diz qual população usou". (d) Os detalhes do finding mostram a população usada?

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: histórico; reabrir só se a escolha de população for contestada com dado real (ver #90).

<a id="item-490"></a>

## PR#100 — feat(front): Apex Console — the seven screens as a runnable Vite + React app

Frente: historico. Encaminhamento: integrada_com_review_aprovada_apos_mudancas.

### Identidade e estado

PR #100, `feat/front-end` → `main`; autor `agmarcastro` (COLLABORATOR), com commits também de "Augusto Silva"; rótulos `crew-a`, `type:feature`, `phase:review`, `pod-1-front-end`; criada em 2026-08-24; `CHANGES_REQUESTED` em 2026-08-25, `APPROVED` em 2026-09-14; integrada em 2026-09-14T16:20:13Z (merge `8d3efa7`); 10 commits; 70 arquivos. Ligada ao registro L13.

### Intenção e benefício

Entregar a Apex Console: sete telas como app Vite + React + TypeScript alinhado ao contrato v0.5, com imagem de produção nginx e ClickHouse configurável.

### Feito, faltante e não comprovado

Feito: a review de 2026-08-25 bloqueou por quatro itens (sem job de CI do front, nginx com nome curto `clickhouse`, Dockerfile sem `package-lock.json`, `bytesPerTask` divergente do engine); o autor respondeu em 2026-08-31 que os quatro entraram em `6dc476e` (job `front (Node 22)` no `ci.yml`, `CLICKHOUSE_UPSTREAM`, `npm ci` nos dois estágios, `bytesPerTask` igual a `StageAggregate.bytes_touched`). A aprovação final confirma. Commits de 2026-09-08 corrigem textos que "mentiam" (botões e `/ask` roteirizado). A camada de dados `front/src/data/` e os blocos `/clickhouse` do nginx conferem com o #102 (`fontes/git/_102.txt`). Runs verdes de PR e de push no head em 2026-09-10. Correções posteriores na mesma fronteira: #151 (detalhe de erro textual) e #153 (paridade da Console, commits de agmarcastro).

### Linhagem

#102 (camada ausente em `c04efec`) → PR #100 → review bloqueante → correções → aprovação → merge na leva → follow-ups #116 → PRs #118/#119/#120 empilhadas sobre ela. Precisão de autoria: PR de agmarcastro; os commits 6dc476e18d e 5b4fc4f1e0 têm commit-author Augusto Silva e trazem contribuições substantivas; 9e77db95 é merge de main com o mesmo nome de autor. A resposta pública sobre os quatro itens é de Agmar, não foi reatribuída.

### Fontes e corte

Snapshot (PR 100) e comentário do autor; dossiê (70 arquivos, 10 commits); `fontes/api-reviews/pr100-reviews.json`; `fontes/git/_102.txt`; `fontes/git/_runs-push-main-por-dia.txt`; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos, reviews, runs verdes. RELATADO: verificação local dos quatro itens em `6dc476e`. INFERÊNCIA: o front tornou-se a fronteira browser → ClickHouse descrita no #102. Review formal (API, observada em 2026-10-17T17:28:36Z): 2 — `luanmorenommaciel` CHANGES_REQUESTED em 2026-08-25; `luanmorenommaciel` APPROVED em 2026-09-14. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `5b4fc4f` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` push success, run 34509624907, tentativa 1, created_at 2026-09-10 17:40:12Z, run_started_at 2026-09-10 17:40:12Z, updated_at 2026-09-10 17:43:18Z (antes do merge pelo updated_at); `CI` pull_request success, run 34509628436, tentativa 1, created_at 2026-09-10 17:40:13Z, run_started_at 2026-09-10 17:40:13Z, updated_at 2026-09-10 17:43:56Z (antes do merge pelo updated_at).

### Fluxo

Fluxo da console: browser → nginx (SPA + `/clickhouse/`) → ClickHouse com usuário de leitura (`front/contract/01-readonly-user.sql`) → telas Runs, RunDetail, Compare, Memory, Verify, Ask.

### Consequências e risco

Alto valor de produto. Limite de segurança tratado depois: o acesso direto ao ClickHouse por proxy é a base da discussão de token e exposição (#171) e da fronteira de API (#122, PR #129). Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) nenhuma alternativa nesta PR; as questões de fronteira têm issues próprias.

### Dependências e paralelismo

Questões abertas dependem de DEC-07 (#122) e DEC-08 (#171); a prova em navegador depende de #172.

### Plano e aceite propostos

Condição explícita de não ação: integrada com aprovação após quatro correções verificáveis.

### Comunicação entre responsáveis

Para a consolidação: "PR #100 é a console; entrou depois de corrigir os quatro bloqueios da review".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — calcular `bytesPerTask` diferente do engine faria a tela e o finding discordarem. (b) Que caso o teste ainda não cobre? — navegador real com ClickHouse real (#172). (c) Como eu explicaria isso para outro pod? — "a console lê o ClickHouse por um proxy com usuário só de leitura". (d) O usuário de leitura é o mesmo em todos os perfis?

### Próxima ação e encerramento

Nenhuma ação nesta PR. Owner da prova integrada: Pod 1 em #172. Encerramento: histórico.

