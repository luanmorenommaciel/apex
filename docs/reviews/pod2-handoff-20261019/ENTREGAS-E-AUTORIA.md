> Para leitura rápida: [cinco exemplos antes/depois](EXEMPLOS-ANTES-E-DEPOIS.md). Abaixo fica o histórico detalhado com o corte da Parte 10.

# Contribuições, histórico e autoria — Pod 2 / Engine e interfaces Package, Harness e Infra

O histórico a seguir distingue contribuições integradas e propostas encerradas sem merge, preservando autoria do objeto; não concede novo aceite funcional nem reproduz testes. Colaborações na PR de outra pessoa são discriminadas abaixo. O usuário gustocezar é Augusto; quem fez merge não é automaticamente autor da implementação.

| PR | Autor da PR | Head | Merge | Entrega / papel |
|---|---|---|---|---|
| [#46](https://github.com/luanmorenommaciel/apex/pull/46) | gustocezar | `f11f602479` | `244686d6a7` em 2026-07-24T00:43:01Z | feat(engine): adicionar diagnóstico determinístico |
| [#52](https://github.com/luanmorenommaciel/apex/pull/52) | gustocezar | `05549bef2b` | Encerrada sem merge; contexto histórico | feat(engine): add gated CrewAI judge adapter |
| [#70](https://github.com/luanmorenommaciel/apex/pull/70) | gustocezar | `0a7772bfb3` | `2195d40121` em 2026-08-18T20:04:50Z | engine: read the typed executor runtime column, Map as fallback |
| [#76](https://github.com/luanmorenommaciel/apex/pull/76) | gustocezar | `f05a050fbf` | `884c274cab` em 2026-08-18T20:06:02Z | scripts: local operational package (bootstrap/doctor/smoke/e2e/status/down) |
| [#84](https://github.com/luanmorenommaciel/apex/pull/84) | gustocezar | `2de02dd7d4` | `7c5460c874` em 2026-08-20T02:45:43Z | harness: verify optional ClickHouse endpoint identity |
| [#89](https://github.com/luanmorenommaciel/apex/pull/89) | gustocezar | `c731acae25` | `c67ba0e3c5` em 2026-09-14T16:17:47Z | engine: retry-safe telemetry — reachability + the retry_pressure watcher |
| [#92](https://github.com/luanmorenommaciel/apex/pull/92) | gustocezar | `729587f852` | `a1ae77dede` em 2026-09-14T16:17:55Z | dev: cover scripts/apex.ps1 with dry-run and secrets contract tests |
| [#94](https://github.com/luanmorenommaciel/apex/pull/94) | gustocezar | `f9f0457584` | `1b990a8325` em 2026-09-14T16:17:59Z | engine: fail in CI when the SQL reads a column no DDL declares |
| [#99](https://github.com/luanmorenommaciel/apex/pull/99) | gustocezar | `4c3ad27389` | `926bce885d` em 2026-09-14T16:54:08Z | engine: make skew_ratio retry-safe |
| [#111](https://github.com/luanmorenommaciel/apex/pull/111) | gustocezar | `4f833c71f1` | `31a0cee198` em 2026-09-14T16:20:02Z | docs: add executable telemetry compatibility matrix |
| [#121](https://github.com/luanmorenommaciel/apex/pull/121) | luanmorenommaciel | `efb6773741` | `16e3819207` em 2026-09-14T16:46:27Z | fix(tests): bump telemetry matrix to contract v0.6 |
| [#126](https://github.com/luanmorenommaciel/apex/pull/126) | gustocezar | `4ddb082cf8` | `abed508939` em 2026-10-06T19:55:46Z | feat(engine): add offline execution-stage attribution |
| [#127](https://github.com/luanmorenommaciel/apex/pull/127) | gustocezar | `4e44bfdce5` | `fec8a7fb0b` em 2026-10-06T19:56:00Z | feat: add deterministic tail-outlier runtime gate |
| [#128](https://github.com/luanmorenommaciel/apex/pull/128) | gustocezar | `2b84c7a14f` | `d8c1a3c679` em 2026-10-06T19:56:14Z | test(package): make PowerShell coverage command-aware |
| [#131](https://github.com/luanmorenommaciel/apex/pull/131) | gustocezar | `7b7b9b41aa` | `e867232982` em 2026-10-06T19:56:20Z | engine: fail fast on connect when spark_events schema is behind |
| [#139](https://github.com/luanmorenommaciel/apex/pull/139) | gustocezar | `087ce22947` | `987a5fa079` em 2026-10-06T20:12:05Z | test(engine): harden SQL to DDL column guard |
| [#142](https://github.com/luanmorenommaciel/apex/pull/142) | gustocezar | `761f2c5af6` | `7509e59601` em 2026-10-06T19:56:33Z | fix(verify): use successful-task duration samples for stage analysis |
| [#145](https://github.com/luanmorenommaciel/apex/pull/145) | gustocezar | `142d6ea843` | `fb094dcffe` em 2026-10-06T20:11:20Z | fix(verify): reject invalid noise floors for certification |
| [#147](https://github.com/luanmorenommaciel/apex/pull/147) | gustocezar | `a07fc0477a` | `928da21d3f` em 2026-10-06T20:12:09Z | fix(infra): check multiline materialized-view targets |

## Leitura por contribuição

### #46 — feat(engine): adicionar diagnóstico determinístico

Criar o engine determinístico: schema do contrato v0.2, cinco watchers, `EvidenceValidator`, fronteira ClickHouse parametrizada e persistência de findings, antes de qualquer escalonamento para LLM.

**Implementação e limite:** Feito no recorte da época. Hoje o arquivo único `engine/src/apex_engine/watchers.py` não existe; os watchers viraram o pacote `watchers/` (conferido no #17: `skew`, `shuffle`, `memory`, `cost`, `code`, `aqe`, `retry_pressure`). Continuam: `schema.py`, `clickhouse.py`, `pipeline.py`, `validation.py`, `tests/test_clickhouse_boundary.py`, `tests/test_contract_engine.py`, `engine/VALIDATION.md`. Relatado: "10 passed em 0,85 s".

**Próximo passo histórico:** Nenhuma ação e nenhum owner. Encerramento: histórico; reabrir só se o princípio determinístico-primeiro for abandonado.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-46.md#item-452).

### #52 — feat(engine): add gated CrewAI judge adapter

Implementar o Tier 2 do engine: adaptador CrewAI preguiçoso com correlação e Judge adversarial, chamado só para candidatos CRITICAL/BLOCKER de baixa confiança, com citações tiradas da evidência do finding e sem mutações.

**Implementação e limite:** Não integrada. O comentário de fechamento diz que o trabalho foi consolidado na branch `base-project-e2e-augusto` (o texto tem caracteres de controle `\x08`/`\x0c` no lugar de "`b" e "`f", provavelmente escapes de shell). Conferi: os commits da PR não estão naquela branch, e `engine/src/apex_engine/crew.py` também não; a branch tem a mesma ideia reestruturada em `crew/judge.py`, `crew/llms.py` e `crew/tools.py`. Na main o crew segue esse desenho em pacote (`crew/judge.py`, ver #17). Relatado: `14 passed` e smoke do provedor Anthropic local.

**Próximo passo histórico:** Nenhuma ação e nenhum owner. Encerramento: histórico; a branch segue o plano do #105.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-46.md#item-458).

### #54 — docs(c9): record Engine and Serve delivery status

Dar ao Commander um ponto único de revisão das entregas ENGINE/C5 e SERVE/C4: links e ordem de merge das PRs #52 e #53, evidência sanitizada do smoke do Judge e da validação MCP stdio, e limites (sem auto-apply, rerun, UI, instalador nem CI remoto).

**Implementação e limite:** Não integrada; mesmo fechamento das PRs #52/#53. Conferi: `docs/convergence/C9-ENGINE-SERVE-DELIVERY-STATUS-2026-07-24.md` e `evidence/serve-c4-stdio-mcp-2026-07-24.log` existem na branch `base-project-e2e-augusto`; não existem na main. O corpo declara explicitamente não afirmar que #52 e #53 estavam integradas, uma boa prática.

**Próximo passo histórico:** Owner a confirmar: custodiante do #105. Entrada: mapa do bundle (conferido). Saída: decisão do custodiante sobre a branch. Encerramento: a PR segue fechada.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-46.md#item-460).

### #70 — engine: read the typed executor runtime column, Map as fallback

Fazer as duas leituras de `executor_run_time_ms` no engine preferirem a coluna tipada, mantendo o mapa de atributos como fallback, para que linhas da janela de transição não caiam de "medido" para 0.

**Implementação e limite:** Feito: `clickhouse.py` e `watchers/memory.py` usam `argMax(if(col > 0, col, toInt64OrZero(attributes[...])), ts)` (conferido, `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_61.txt`); teste de integração novo (+63). O corpo explica o efeito: sem fallback, o `runtime_basis` do watcher de memória cairia de `measured` (0,85) para proxy (0,45), abaixo do gate de 0,6, reabrindo escalonamento. Relatado: teste que falha com a mudança revertida. No comentário de 2026-08-06, uma linha real com a coluna tipada `executor_run_time_ms` = 30000 e o Map `attributes` sem essa chave: a consulta desta PR leu 30000, e a da main de então (só Map) leu 0, sem erro. O corpo descreve outro caso: coluna 0 e Map `'10000'`, em que a leitura direta da coluna dá 0 e o fallback dá 10000. (O pacote de 17/10 misturou os dois casos.)

**Próximo passo histórico:** Nenhuma ação obrigatória. Owner da extensão: quem tratar o #179. Encerramento: histórico.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-47.md#item-466).

### #76 — scripts: local operational package (bootstrap/doctor/smoke/e2e/status/down)

Oferecer uma superfície de um comando para o pacote local de seis raias: `bootstrap`, `doctor` (saúde real), `smoke`/`e2e`, `status`, `down` (preserva volumes) e `pilot-clean` (só roda em máquina limpa e nunca remove nada); Windows por `apex.ps1`, macOS por `apex.sh` que delega ao mesmo script.

**Implementação e limite:** Pacote integrado e presente em c3c3ea3; #35 relata uso de make bootstrap. A review aprovada diz que o doctor usa "this repo's apply-ddl and Spark 4.1.2 pin" e registra que o revisor não pôde rodar o e2e do pacote por não ter PowerShell 7. Conferi no merge e na main: o doctor exige **Spark 4.0.1** (`apex.ps1:482-484`, `throw "Expected Spark 4.0.1"`; `.env.example`: `SPARK_VERSION=4.0.1`); 4.1.2 aparece só como overlay de compatibilidade (linha 124). A nota da review sobre o pin é imprecisa, e o próprio autor já a corrigiu no comentário de 2026-08-19: o pacote exige 4.0.1, e a string `# Spark 4.1.2 compatibility overlay` é código morto num parâmetro `-Overlay` que nada passa (o autor se ofereceu para removê-la). Conferi que a string continua na main (`scripts/apex.ps1:124` em `c3c3ea3`); o resíduo atual é um comentário enganoso em código morto, não um pin errado ativo. Relatado: 8 bootstraps reais até verde e `make smoke` com o gate de produto. O autor explicita que e2e, pilot-clean e install não foram exercitados. Defeitos posteriores: `Copy-Item -Force` em `dev/.env` (#174) e ownership de stack (#175), ambos abertos.

**Próximo passo histórico:** Nenhuma ação nesta PR. Owner dos defeitos: dono do pacote (DEC-10). Encerramento: histórico; o trabalho atual segue em #174/#175.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-47.md#item-469).

### #84 — harness: verify optional ClickHouse endpoint identity

Acrescentar ao gate E2E de seis raias uma checagem opcional de identidade do ClickHouse: com `CLICKHOUSE_EXPECTED_HOSTNAME` definido, `SELECT hostName()` precisa coincidir antes de `run_gate()`, evitando rodar contra a instância errada em ambientes com vários runtimes.

**Implementação e limite:** Feito: `scripts/e2e_six_lanes.py` (+26), `tests/test_e2e_six_lanes.py` (+133), `docs/e2e/README.md` e `docs/task-specs/HARN-ENDPOINT.md`. Comportamento: variável ausente = legado; igual = segue; diferente, erro ou resposta inválida = falha fechada antes de análise ou escrita. Relatado: 13 testes, cobrindo os caminhos de falha e provando que `run_gate()` não é chamado. A aprovação: "Harness-only and opt-in".

**Próximo passo histórico:** Nenhuma ação obrigatória. Owner a confirmar: dono do harness, para a opção (b). Encerramento: histórico.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-48.md#item-476).

### #89 — engine: retry-safe telemetry — reachability + the retry_pressure watcher

Fazer o engine ler os ~15 campos seguros a retry do contrato v0.5 (que o JAR já emitia e ninguém lia): campos brutos em `StageAggregate`, propriedades `effective_*` que preferem o subconjunto de tasks bem-sucedidas quando há amostra, e o sexto watcher determinístico, `retry_pressure`.

**Implementação e limite:** Feito: `schema.py` (+73), `clickhouse.py` (+52), `validation.py` (+30), `watchers/retry_pressure.py` (+66), testes em quatro arquivos, quatro Task-Specs em `tasks/`. A aprovação: "the sixth deterministic watcher … reports scheduler-budget use at INFO. It does not guess a root cause". O `retry_pressure` aparece na lista de watchers da main (conferido para o #17). As quatro Task-Specs foram criadas em `tasks/T-2026081*`/`T-2026082*`, não em `tasks/done/`; o fechamento delas é assunto do NOV-06/DEC-N7. A decisão de passar o `skew_ratio` para os campos seguros veio depois, na PR #99 (#90).

**Próximo passo histórico:** Nenhuma ação obrigatória. Owner a confirmar: quem decidir a DEC-N7. Encerramento: histórico.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-49.md#item-481).

### #92 — dev: cover scripts/apex.ps1 with dry-run and secrets contract tests

Dar cobertura ao `scripts/apex.ps1` da PR #76 (que tinha zero testes): dry-run sem mutação para as 8 ações, segredos gerados localmente sem chaves literais nem comandos destrutivos, exigência de PowerShell 7 sem fallback, e `.apex/` fora do versionamento.

**Implementação e limite:** Feito: 7 funções de teste e a correção do vazamento `.apex/` no `.gitignore`. A aprovação: "`.apex/` is now ignored. That was the leak … Dry-run and secrets checks are source-plus-dry-run, and CI is 9/9". Limite apontado depois pelo Codex (C04-12, ligado à issue #124, aberta): o teste de dispatch executa `-DryRun` e compara a string `Handler`, e o ramo retorna antes do scriptblock `Command`; trocar só o `Command` não falharia o teste. A PR #128 (2026-10-06) tratou cobertura de pwsh do #124; a força da prova do dispatcher segue aberta. Reconfirmado em 19/10 na main: `-DryRun` imprime o rótulo `Handler` declarado ao lado do `Command`, e só `help` é despachado de fato (`scripts/apex.ps1:734-806`; `tests/test_apex_initial_package.py:17-80`).

**Próximo passo histórico:** Nenhuma ação nesta PR. Owner do critério aberto: responsável pelo #124. Encerramento: histórico.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-49.md#item-483).

### #94 — engine: fail in CI when the SQL reads a column no DDL declares

Fazer o CI falhar quando uma consulta do engine lê uma coluna que nenhum DDL declara, já que o CI não tem ClickHouse e os 11 testes de integração são pulados ("97 passed, 11 skipped").

**Implementação e limite:** Feito: `engine/tests/test_sql_columns_exist_in_ddl.py` extrai as colunas lidas por `STAGE_AGGREGATES_SQL` e `STAGE_EVENTS_SQL` e as declaradas pelos DDLs e migrações aditivas. A primeira review achou um buraco: o extrator subtraía todo `AS <alias>` do conjunto, então `argMax(fake, ts) AS fake` passava; o commit de 2026-08-26 remove o alias do texto em vez de subtrair do conjunto, e a aprovação confirma. É a base estática que as PRs #131 (preflight em runtime) e #155 (aberta) reaproveitam.

**Próximo passo histórico:** Nenhuma ação nesta PR. Owner da evolução: responsável pela #155. Encerramento: histórico.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-49.md#item-485).

### #99 — engine: make skew_ratio retry-safe

Tornar o `skew_ratio` público do engine seguro a retry: usar os percentis de tasks bem-sucedidas quando `successful_task_sample_count > 0`, manter o legado para linhas históricas, preservar `legacy_skew_ratio` nos detalhes e não misturar históricos de populações diferentes no piso de ruído.

**Implementação e limite:** Feito, conferido para o #90 (`fontes/git/_90.txt`): `schema.py` com `effective_task_duration_*`, `legacy_skew_ratio` e a escolha de população; `context.py`, `clickhouse.py`, `watchers/skew.py`; testes em `test_watchers.py`, `test_physics_rules.py`, `test_clickhouse_boundary.py`; Task-Spec `ISSUE-90-RETRY-SAFE-SKEW.md`. A primeira review apontou dois bloqueios (o primeiro: "No checks on …" o head daquele momento); a aprovação final diz que o `CONTRACT.md` documenta o comportamento. Run de PR no head final concluído com `success` às 16:51:21Z (34870838119, criado 16:48:00Z), antes do merge (16:54:08Z); run de push do merge (`926bce8`, 34871459623) criado 16:54:11Z e concluído com `success` às 16:57:45Z (`fontes/reconferencia/pontos03-05-06-runs-por-pr.json`).

**Próximo passo histórico:** Nenhuma ação e nenhum owner. Encerramento: histórico; reabrir só se a escolha de população for contestada com dado real (ver #90).

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-49.md#item-489).

### #111 — docs: add executable telemetry compatibility matrix

Registrar de forma executável onde cada campo de telemetria é produzido, transportado, armazenado e consumido, separando contrato declarado, implementação observada, relação derivada e `offline_unproven`.

**Implementação e limite:** Feito: `docs/architecture/TELEMETRY-COMPATIBILITY-MATRIX.md` (+186) e `tests/test_telemetry_compatibility_matrix.py` (+200). Na leva de 2026-09-14, esta PR entrou dois minutos depois da #96, que subiu o contrato para v0.6; o teste fixava v0.5; segundo o corpo da #121, isso quebrou o root gate da main; nos runs, o push do merge da #98 concluiu em `failure` às 16:28:02Z, e o próximo `success` na main foi às 16:50:57Z (merge da #87, depois da #121). A guarda também fixa textos literais (`PROPOSED v0.4`, `PROPOSED, not ratified` e a frase obsoleta de `models.py`, linha 166), o que obriga correções em #165/#179 a ajustar o teste junto (conferido, `fontes/git/_103.txt`). Reconfirmado em 19/10: a guarda fixa `PROPOSED v0.4` e `PROPOSED, not ratified` (linhas 145–147) e a frase antiga de `models.py` (linha 166).

**Próximo passo histórico:** Nenhuma ação nesta PR. Owner a confirmar: mantenedor da matriz, para a opção (b). Encerramento: histórico.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-50.md#item-493).

### #121 — fix(tests): bump telemetry matrix to contract v0.6

Consertar o root gate da main, que falhava em `test_telemetry_compatibility_matrix.py::test_matrix_is_structural_and_derived_from_independent_sources` porque o `CONTRACT.md` passou a v0.6 (PR #96) e a matriz (PR #111) esperava v0.5.

**Implementação e limite:** Feito: o teste e o documento passam a esperar v0.6; o manifesto de drift tira o engine de `observed_consumers_without_sample_count`, porque o engine passou a ler `sample_count` (PR #89/#99). Run de PR no head concluído com `success` às 16:45:14Z (34870161347, criado 16:41:30Z), antes do merge (16:46:27Z). O run de push do merge (`16e3819`, 34870682662) foi cancelado às 16:47:24Z, então a árvore desta PR sozinha não tem conclusão observada na main; o run de push do merge da #87 (`4adb854`, 34870745971), que já inclui esta PR, foi criado 16:47:05Z e concluiu com `success` às 16:50:57Z (`fontes/reconferencia/pontos08-09-tempos-de-runs.json`). O run vermelho do head da #87 (`run34868325801-jobs.json`) falhou no `pytest tests/` do root gate, compatível com a causa relatada no corpo; isso não prova a causa.

**Próximo passo histórico:** Owner a confirmar: mantenedor, ao decidir o caminho de emergência na DEC-02. Encerramento: histórico.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-50.md#item-497).

### #126 — feat(engine): add offline execution-stage attribution

Implementar o resolvedor offline do engine que atribui uma execução SQL a stages, com escopo pela identidade completa `(app_id, job_id)`, resultados explícitos (ausente, não encontrado, atribuído, conflito) e semântica de tentativas sem duplicar membros.

**Implementação e limite:** Feito no código: `engine/src/apex_engine/attribution.py` (+138) e `engine/tests/test_execution_attribution.py` (+218), mais quatro TaskPlans e quatro Task-Specs em `tasks/done/`. Relatado: 25 testes de atribuição e 213 offline passando em `4ddb082`, com três casos novos que separam `execution_id` 0 de ausente. O Codex (C04-13) registra que o resolvedor e os testes já cobrem conflito, escopo estrangeiro, tentativas, ausência e zero, e que o sentinela `-1` de AQE é de nível de job. Falta (fora desta PR, na #115): consumidor público da atribuição. Prova hospedada: no universo de 213 runs retornado em 2026-10-17, o único run com o head final é o 36488146081 (pull_request, tentativa 1, criado 2026-09-28T21:44:59Z, updated_at 21:45:03Z, `failure`), cujos 11 jobs coletados têm 0 steps (`fontes/reconferencia/pontos03-05-06-runs-por-pr.json`). Reconfirmado em 19/10: `attribution.py` só é importado por testes; findings de nível de job seguem com `JOB_LEVEL_STAGE_ID = -1` e `attributionIsAvailable()` retorna `false` (#115).

**Próximo passo histórico:** Owner a confirmar: mantenedor, na prova pós-integração (M0). Entrada: CI disponível. Saída: run verde que inclua estes testes. Encerramento: a PR segue integrada; o consumidor segue na #115.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-50.md#item-498).

### #127 — feat: add deterministic tail-outlier runtime gate

Completar o caminho determinístico `tail_outlier`: contrato do finding, watcher seguro a retry que cede quando o skew já explica o caso, roteamento de um cenário canônico opt-in, remoção da recusa antiga no pacote, asserção da forma de cauda no ClickHouse e uma prova de runtime local documentada.

**Implementação e limite:** Feito no código e conferido na main: `engine/src/apex_engine/watchers/tail_outlier.py`, `docs/e2e/TAIL_OUTLIER_RUNTIME_GATE.md` e `tests/test_tail_outlier_package.py` existem. Relatado (C04-10 do Codex): núcleo Spark→Collector→ClickHouse→Engine provado em 2026-09-20 e wrapper público macOS/Spark 4.0.1 em 2026-09-21, com cache de imagens; a razão `373,364` pertence ao núcleo de 20/09. Limite (C04-11): o gate procura `tail_outlier_watcher` na saída e não compara stage/snapshot da asserção; `llm_calls=0` é literal. Também corrige a leitura de segredos S3 do pacote e falha cedo sem Python 3. Resíduo conferido na main: o front não reconhece `TAIL_OUTLIER` como tipo de finding (`front/src/contract/types.ts` só lista `RETRY_PRESSURE` entre os novos; ver ficha PR#137); esse resíduo já é acompanhado pela #166, aberta. Prova hospedada: o run do head 35557495963 foi criado em 2026-09-21T03:25:53Z; a tentativa retornada é a 2, executada em 2026-09-23T03:53 (run_started_at), com 11 jobs e 0 steps (`fontes/git/_jobs-head-prs-outubro.json`); a tentativa 1 de 2026-09-21 não está coberta pela coleta (`fontes/reconferencia/pontos03-05-06-runs-por-pr.json`).

**Próximo passo histórico:** Owner a confirmar: Pod 2, para a DEC-N6, e mantenedor, para a prova pós-integração. Encerramento: a PR segue integrada; o aceite segue na #123.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-50.md#item-499).

### #128 — test(package): make PowerShell coverage command-aware

Tornar explícito e fechado no CI o contrato de comandos do pacote: verificar PowerShell 7 antes da raia de testes, falhar (não pular) sem `pwsh`, resolver um único plano de ação para execução real e `-DryRun` e reportar o handler escolhido.

**Implementação e limite:** Feito: passo `Verify PowerShell 7` no `ci.yml` (+4), `scripts/apex.ps1` (+53/-12) com o plano de ação único, `tests/test_apex_initial_package.py` (+93/-6), TaskPlans e Task-Specs. Relatado: 18 testes focados e 69 da raiz. Limite apontado pelo Codex (C04-12) e coerente com o dispatcher conferido na ficha #64: o teste compara a string `Handler` em `-DryRun`, e o ramo retorna antes do `Command`; o critério da #124 (alcançar o handler de cada ação) segue aberto. Um commit de 2026-10-01 explica aspas ao shellcheck. Prova hospedada: o run do head (2026-10-01) tem 11 jobs com 0 steps (`fontes/git/_jobs-head-prs-outubro.json`). Reconfirmado em 19/10 na main: `-DryRun` imprime o rótulo `Handler` declarado ao lado do `Command`, e só `help` é despachado de fato (`scripts/apex.ps1:734-806`; `tests/test_apex_initial_package.py:17-80`).

**Próximo passo histórico:** Owner a confirmar: responsável pela #124. Entrada: este registro. Saída: teste discriminante ou mudança de escopo registrada. Encerramento: a PR segue integrada.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-50.md#item-500).

### #131 — engine: fail fast on connect when spark_events schema is behind

Falhar rápido no connect do Engine quando o volume ClickHouse tem schema antigo (docker-entrypoint-initdb.d só roda na 1ª inicialização), nomeando colunas faltantes antes de qualquer análise.

**Implementação e limite:** Implementado: preflight de system.columns no banco configurado, conjunto manual de 35 colunas, remoção de qualificadores fixos, trim/fallback da configuração e mensagem específica para banco alternativo. Provisionamento de outro banco permanece fora do escopo. Resultados locais do corpo são relatos nos SHAs citados; jobs sem steps no recorte não comprovam causa atual de billing nem execução do head final.

**Próximo passo histórico:** Encaminhar a manutenção do guard a #154/#155, responsável a confirmar no Engine; encerrar este histórico preservando a prova e sem prometer provisionamento de bancos alternativos.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-51.md#item-502).

### #139 — test(engine): harden SQL to DDL column guard

Endurecer o guard SQL→DDL do Engine para verificar colunas referenciadas contra o DDL declarado, evitando query silenciosa sobre coluna inexistente.

**Implementação e limite:** Diff remove apenas job_id e attributes de NOT_COLUMNS; a allowlist restante permanece. Acrescenta controle parametrizado para que leitura dessas colunas exija declaração em DDL. Comentário explica que são colunas de origem e não aliases. Não verifica schema instalado em deployment.

**Próximo passo histórico:** Sem nova ação na PR histórica. Na revisão #155, confirmar controles sobre colunas lidas, aliases e função SQL com diff/DDL da mesma base. Responsável a combinar no Engine.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-51.md#item-510).

### #142 — fix(verify): use successful-task duration samples for stage analysis

Verify ignorava os campos v0.5 successful_task_*; skew e work bounds podiam ser estimados com tentativas falhas/repetidas. Caso representativo: razão 8.96x → 1.10x com amostras de sucesso.

**Implementação e limite:** Feito: seleção de p50/p99 de tarefas bem-sucedidas quando successful_task_sample_count > 0, fallback para valores legados em linhas históricas; skew, work bound e filtro de irmãos no piso compartilham a população efetiva; razão legada preservada para auditoria. Faltante: semântica de p50 zero (decisão separada). Não comprovado: replay live em ClickHouse.

**Próximo passo histórico:** Vincular o caso 8.96x→1.10x como entrada de evidência para #169.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-52.md#item-513).

### #145 — fix(verify): reject invalid noise floors for certification

Verify podia certificar delta ou passar no controle positivo com piso inválido (ex.: piso negativo certificou -11%; NaN/inf passaram com score 0.90); piso só é utilizável se medido, finito e não negativo.

**Implementação e limite:** Piso deve ser medido, finito e não negativo para certificação/controle. Piso inválido produz score floorless e to_row floor nulo; delta bruto permanece. Zero válido preservado. Comparação de significância abs(delta)>=floor deve ser reconciliada com fronteiras diferentes no Serve em #117; follow-up de caveat não ratifica contrato.

**Próximo passo histórico:** Registrar a perda de distinção de motivo como follow-up de auditoria (#117/#170).

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-52.md#item-516).

### #147 — fix(infra): check multiline materialized-view targets

apply_ddl.sh verificava alvos de materialized views linha a linha; em 010_otel_traces.sql o CREATE MATERIALIZED VIEW e o TO estão em linhas separadas e o alvo escapava da verificação.

**Implementação e limite:** Feito: strip de comentários de linha e junção de linhas antes de extrair 'MATERIALIZED VIEW ... TO <target>'; cinco alvos atuais extraídos; nenhuma mudança de DDL ou ordem. Faltante: não é parser SQL geral (declarado); ingestão em migrações repetidas 034–039 permanece aberta. Não comprovado: cobertura de suites Engine/root sobre o script (explicitamente não cobrem).

**Próximo passo histórico:** Preservar histórico e relato dos cinco casos no ClickHouse descartável. Se o time escolher melhorar parser/quietude/replay de DDL, conferir aderência à #170 antes de ampliar escopo. Nova execução requer ambiente próprio e prova de pós-condição, não só parse bem-sucedido.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-52.md#item-518).

## Interfaces e limites de atribuição

- **#185 é do Agmar, relacionada à interface com o Pod 3.** Neste pacote aparece como candidata externa relacionada a167/credenciais/runners, não como entrega de Augusto ou propriedade automática do Pod 2.
- **#121 é de Luan** (metadados de commit distinguem o autor técnico registrado); é evolução da matriz e não contribuição de Augusto.
- #142/#145 são Verify, #147 é Infra e #76/#84/#92/#128 são Package/Harness: entram como interfaces explicitadas, sem redefinir fronteiras dos pods.
- #155 continua aberta, ainda não é contribuição integrada. Conjuntos de testes relatados são datados; não somar testes sobrepostos nem atribuir sua execução a esta rodada.

### Contexto histórico adicional: #54

A [PR #54](https://github.com/luanmorenommaciel/apex/pull/54), de Augusto (`gustocezar`), foi **encerrada sem merge**. Head `2bd02485c0`; `merged_at=null`. O valor `merge_commit_sha` retornado pelo GitHub não é evidência de integração nessa situação. Seu registro de status/evidência permanece histórico, sem ser contado como entrega integrada.
