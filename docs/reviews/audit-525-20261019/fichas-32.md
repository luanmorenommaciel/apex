# Fichas documentais — lote 32

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-311"></a>

## T-20260820-tool-surface-six — T-20260820-tool-surface-six.md

Frente: Serve / L3 Understand — legibilidade do diagnóstico (#88). Encaminhamento: encerrada_historica_sem_aceite_eval_aponta_teste_renomeado.

### Identidade e estado

`tasks/done/T-20260820-tool-surface-six.md` (blob 5275763e). 'Re-pin the tool surface at six', XS, standard, P2; owner `(none)`; depends_on explain-stage-tool. Estado `done`; `accepted: false` e `signed_off: false` por escolha registrada: o commit 9ff859b e o corpo da PR #88 dizem que esses bits pertencem a `taskspec gate --stamp`, 'which is not in this repo', e que marcá-los à mão anula seu propósito — portanto 'done sem aceite' é deliberado e não omissão. Pod provável: Pod 3/Serve (caminhos serve/; nenhum pod no arquivo).

### Intenção e benefício

Mover a asserção ordenada da superfície de cinco para seis nomes (com explain_stage), mantendo igualdade, em commit próprio para que a mudança de superfície fique legível no git log.

### Feito, faltante e não comprovado

Feito em d056c35 (autor 2026-08-20). Superação: no mesmo período, df6fe77 (autor 2026-08-24; integrado por #101 em 2026-08-26, antes de #88) introduziu a lista única `CONTRACTED_TOOLS` comparada ordenada; hoje com oito nomes em `test_the_contracted_tool_surface`. O eval_1 nomeia `test_exactly_the_six_contracted_tools`, inexistente no SHA — erro de coleta se reexecutado na main (inferência). Também foi preciso atualizar o gate stdio, que 'pinava sua própria cópia da superfície' (PR #88 'A write surface the plan did not declare', ca514b8).

### Linhagem

SERVE-LEGS L3 → l3-understand.yaml (approved: true) → specs dc1c2ce (autor 2026-08-20; commit 2026-08-26) → implementações no mesmo ramo → 9ff859b 'six units done' (status done, accepted false) → PR #88 integrada em 2026-09-14 (merge 1125cdb). Elos: df6fe77 (lista única) e ca514b8 (gate stdio, fora do raio declarado).

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260820-tool-surface-six.md; fontes/batch-revalidated-specs58-sources/history/T-20260820-tool-surface-six.txt; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_server_tools.py; fontes/batch-revalidated-specs58-sources/git/serve__tools__mcp_stdio_gate.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: teste vigente compara sorted(nomes) com lista única de oito; EXPECTED_TOOLS stdio tem sete. B-2 de tool extra continua representado pela igualdade. eval_1 aponta nó inexistente, logo já não referencia o controle atual. A decisão sobre ordem de registro está no docstring; relato histórico de gates não foi reexecutado.

### Fluxo

Fluxo observado: create_server → list_tools → sorted → == CONTRACTED_TOOLS. Paralelo e fora do teste: mcp_stdio_gate com EXPECTED_TOOLS própria (hoje defasada).

### Consequências e risco

Controle unitário de nomes permanece presente, mas não certifica metadados/comportamento nem a outra cópia stdio. A deriva demonstra acoplamento documental entre consumidores da superfície; não permite concluir ausência universal de risco no teste ou produto.

### Alternativas e recomendação

Recomendado: manter encerrada com nota do sucessor (df6fe77) e ligar ao item de reconciliação do gate stdio, que deve derivar a lista de uma fonte única. Alternativa: só nota.

### Dependências e paralelismo

Nenhuma dependência: explain-stage-tool entregue e o sucessor do controle (CONTRACTED_TOOLS) já está na main desde #101. O item de reconciliação do gate stdio é independente desta spec e pode correr em paralelo, sem ClickHouse para a edição.

### Plano e aceite propostos

Condição de não ação no código. Nota documental: 'eval_1 aponta test_exactly_the_six_contracted_tools, inexistente desde a lista única de df6fe77; controle vigente test_the_contracted_tool_surface'. O gate stdio deve passar a derivar a lista da mesma fonte (item separado).

### Comunicação entre responsáveis

Explicar: 'A superfície de seis tools foi pinada em agosto; hoje são oito numa lista única. O gate stdio tem cópia própria, e foi isso que ficou para trás.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Mantendo duas listas manuais (teste e gate stdio), cada leg nova esquece uma delas, como aconteceu no L3 e de novo no L6. Que caso o teste ainda não cobre? — A lista do gate stdio, que não deriva de CONTRACTED_TOOLS. Como eu explicaria isso para outro pod? — 'A superfície tem uma lista oficial; qualquer outra cópia deve ser derivada dela, senão envelhece.'

### Próxima ação e encerramento

Ação: nota de sucessor e vínculo ao item do gate stdio. Owner a confirmar: Serve. Entrada: df6fe77, ca514b8. Saída: nota. Encerramento: já encerrada.

<a id="item-312"></a>

## T-20260820-verification-models — T-20260820-verification-models.md

Frente: Serve / L5 Fix — superfície da verify lane (#87). Encaminhamento: encerrada_controles_presentes_convencao_de_sinal.

### Identidade e estado

`tasks/done/T-20260820-verification-models.md` (blob 73b8b564). 'Type the verification payload', S, standard, P2; owner `(none)`; sem dependências. Estado `done`, aceite gravado pelo gate (`signed_off_sig` hmac-sha256-v2, horários com segundos em 2026-08-20 14:43Z) por `sidymar`, autor da implementação — registro de ferramenta do próprio autor, não revisão independente nem autorização atual. Pod provável: Pod 3/Serve (com dependência de contrato das lanes Verify/Memory).

### Intenção e benefício

Tipar VerificationView e FixVerdict com predição, medição, segurança e confiança, declarando no schema que deltas são com sinal e negativo significa mais rápido — um erro de sinal relataria regressão como melhoria.

### Feito, faltante e não comprovado

Implementado (a24721d): `VerificationView` (`models.py:329-484`) com measured_delta_pct anulável e descrições de sinal; `FixVerdict` (485-560) com evidence, caveats, `blocked` separado de confiança e status `not_assessed`. Testes (`test_verify_view.py`): os nomeados nos evals e outros controles — medição 0.0 ≠ não medida, safe UInt8 → bool, bounds ordenados, bloqueio ≠ baixa confiança, datetimes do driver. B-2 (descrição do sinal) é verificado no JSON Schema por campo (parametrizado).

### Linhagem

SERVE-LEGS L5 → l5-fix.yaml (approved: true) → specs a8087ce (autor 2026-08-20; commit 2026-09-14) → implementação no mesmo ramo → cd59c8d 'accept and close the six L5 units' → PR #87 integrada em 2026-09-14 (merge 4adb854). Os hashes listados no corpo da PR (f3a314c, 2e13535...) não existem na main: o ramo foi rebaseado antes do merge.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260820-verification-models.md; fontes/batch-revalidated-specs58-sources/history/T-20260820-verification-models.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__models.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_verify_view.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: deltas descritos como signed/negative faster, medição defaultNone e blocked separado. Teste de sinal parametrizado lê VerificationView.model_fields[field].description, não o JSON Schema publicado. Teste dos limites verifica texto MOST/LEAST, não valida low<=high. Modelo aceita method como str e não força measuredNone em predicted; a regra depende da linha produtora e build_verdict. Nenhuma execução.

### Fluxo

Fluxo observado: linha de apex.fix_verifications → VerificationView (sinal preservado, measured nulo se não reexecutado) → build_verdict → FixVerdict (status, blocked, evidence, caveats) → verify_fix / suggest_fix.

### Consequências e risco

A camada conserva distinções do contrato e tem casos pertinentes presentes; não verifica integralmente coerência semântica entre método, medidas, intervalo e segurança. Descrição de limite ordenado não impõe ordem. A ausência de risco nesta camada não foi demonstrada.

### Alternativas e recomendação

Recomendado: manter encerrada; deixar a normalização de unidades com #117. Alternativa: inverter o sinal para exibição — anti-padrão declarado.

### Dependências e paralelismo

Nenhuma dependência pendente; a relação com #117 é de contrato futuro (unidade do piso, atribuição), não bloqueio. O estudo de unidades pode correr em paralelo; qualquer mudança de modelo decorrente seria spec nova.

### Plano e aceite propostos

Condição de não ação: controles discriminantes presentes (sinal documentado no schema por campo, medição zero ≠ não medida, bloqueio separado de confiança, not_assessed como status). Reabrir só se #117 mudar unidades ou campos de fix_verifications.

### Comunicação entre responsáveis

Explicar a outro pod: 'O payload de verificação diz o sinal no próprio schema (negativo é mais rápido), separa bloqueio de confiança e distingue não medido de medido zero; tudo testado desde #87.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Default0 confundiria não reexecutado com medição de efeito zero; inverter sinal relataria regressão como melhoria. Que caso o teste ainda não cobre? Linha predicted com measured numérico ou low>high, para decidir rejeição/preservação conforme contrato. Como eu explicaria isso para outro pod? Os modelos descrevem sinal e ausência; a consistência entre campos exige controle próprio, pois texto de schema não valida a origem.

### Próxima ação e encerramento

Ação: nenhuma no código; registrar vínculo com #117 para unidades e atribuição. Owner a confirmar: Serve+Verify. Entrada: decisões de #117. Saída: referência cruzada. Encerramento: já encerrada; reabrir só por mudança de contrato.

<a id="item-313"></a>

## T-20260820-verifications-read-layer — T-20260820-verifications-read-layer.md

Frente: Serve / L5 Fix — superfície da verify lane (#87). Encaminhamento: encerrada_sql_sem_prova_live_declarada.

### Identidade e estado

`tasks/done/T-20260820-verifications-read-layer.md` (blob 61f011d3). 'Read apex.fix_verifications from the serve store', S, standard, P2; owner `(none)`; sem dependências. Estado `done`, aceite gravado pelo gate (`signed_off_sig` hmac-sha256-v2, horários com segundos em 2026-08-20 14:43Z) por `sidymar`, autor da implementação — registro de ferramenta do próprio autor, não revisão independente nem autorização atual. Pod provável: Pod 3/Serve (com dependência de contrato das lanes Verify/Memory).

### Intenção e benefício

Ler as conclusões da verify lane (apex.fix_verifications) por job_id, opcionalmente por finding, integrando lanes pela tabela do contrato e não por import, e degradar quando a tabela aditiva v0.3 não existir.

### Feito, faltante e não comprovado

Implementado (cadd20b): `VERIFICATIONS_SQL` (`ch.py:173-200`) e `verifications()` (826-852) — valida ids antes de sondar, `table_exists('fix_verifications')` e devolve [] se ausente; testes `test_verifications_*` (`test_ch.py:352-445`), inclusive sonda feita uma vez, job_id vazio sem query e clamp de limite. Endurecimento posterior (#140): falha da sonda agora levanta e não é cacheada como ausência. Não comprovado: SQL contra ClickHouse real — VALIDATION:344 e SERVE-LEGS:219 ainda dizem que VERIFICATIONS_SQL não encontrou parser real.

### Linhagem

SERVE-LEGS L5 → l5-fix.yaml (approved: true) → specs a8087ce (autor 2026-08-20; commit 2026-09-14) → implementação no mesmo ramo → cd59c8d 'accept and close the six L5 units' → PR #87 integrada em 2026-09-14 (merge 4adb854). Os hashes listados no corpo da PR (f3a314c, 2e13535...) não existem na main: o ramo foi rebaseado antes do merge → #140 endurece table_exists. Elo ausente: execução live; eval_3 (nenhum import de outra lane) é grep negativo útil e satisfeito.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260820-verifications-read-layer.md; fontes/batch-revalidated-specs58-sources/history/T-20260820-verifications-read-layer.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__ch.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_ch.py; fontes/batch-revalidated-specs58-sources/git/serve__VALIDATION.md; fontes/batch-revalidated-specs58-sources/git/docs__lanes__SERVE-LEGS.md. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: SQL ligada com WHERE job/finding e ORDERBYverified_atDESC; validação precede probe, falhas propagam sem cache, ausência respondida é cacheada. Os testes de ordem/filtro usam linhas prontas e conferem fragmentos/parâmetros, não parser. RELATO histórico: gates L5 não executados. Recibo posterior suficiente de VERIFICATIONS_SQL não foi localizado neste recorte; não se afirma nunca executada em absoluto.

### Fluxo

Fluxo observado: verifications(job, finding?, limit) → valida ids → table_exists (system.columns, cache só de resposta) → ausente: [] + log ; presente: VERIFICATIONS_SQL ligado → linhas newest-first → VerificationView.

### Consequências e risco

Sem ação: em cluster com a tabela, um defeito de SQL só apareceria na primeira chamada real de verify_fix; probabilidade desconhecida, impacto moderado (tool falha com código sanitizado). Confiança alta nos fatos.

### Alternativas e recomendação

Recomendado: manter encerrada e priorizar uma prova live delimitada de VERIFICATIONS_SQL (item separado) antes de depender de verify_fix em v1. Alternativa: teste com parser SQL offline — mais barato, cobre parte (sintaxe), não semântica.

### Dependências e paralelismo

Nenhuma dependência para permanecer encerrada. A prova live depende de ClickHouse com DDL v0.3 e autorização; o desenho do caso pode ser feito já.

### Plano e aceite propostos

Prova live proposta: (1) store autorizado com DDL v0.3; (2) semear duas verificações do mesmo job em horários distintos; (3) verifications() devolve ambas newest-first e filtra por finding; (4) controle negativo: finding hostil → 0 linhas; (5) recibo com SHA e versão. Depois, atualizar SERVE-LEGS:219.

### Comunicação entre responsáveis

Explicar: Serve lê a tabela do Verify e distingue ausência respondida de falha da sonda. As provas selecionadas não encerram a consulta contra ClickHouse real; ordem/filtro do fake são controles de estrutura, com recibo live ainda a vincular.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Importando apex_verify, o Serve passaria a depender do código de outra lane e quebraria com mudanças internas dela. Que caso o teste ainda não cobre? — A SQL contra um ClickHouse real, onde aliases e tipos já quebraram outras consultas desta lane. Como eu explicaria isso para outro pod? — 'A integração é a tabela; o que falta é rodar a consulta uma vez num banco de verdade e guardar o recibo.'

### Próxima ação e encerramento

Ação: propor prova live de VERIFICATIONS_SQL. Owner a confirmar: Serve+Verify. Entrada: DDL v0.3 e store autorizado. Saída: recibo e atualização de SERVE-LEGS. Encerramento: limite removido com prova, ou mantido explicitamente.

<a id="item-314"></a>

## T-20260820-verify-fix-tool — T-20260820-verify-fix-tool.md

Frente: Serve / L5 Fix — superfície da verify lane (#87). Encaminhamento: encerrada_evals_desconectados_controles_reais_em_testes.

### Identidade e estado

`tasks/done/T-20260820-verify-fix-tool.md` (blob 8a475b10). 'Add verify_fix', XS, standard, P2; owner `(none)`; depends_on verifications-read-layer e verification-models. Estado `done`, aceite gravado pelo gate (`signed_off_sig` hmac-sha256-v2, horários com segundos em 2026-08-20 14:43Z) por `sidymar`, autor da implementação — registro de ferramenta do próprio autor, não revisão independente nem autorização atual. Pod provável: Pod 3/Serve (com dependência de contrato das lanes Verify/Memory).

### Intenção e benefício

Expor `verify_fix(job_id, finding_id?)` para que o usuário saiba o que a verify lane concluiu sobre as correções propostas: faixa prevista, veredito de segurança, confiança, ou que nada foi avaliado.

### Feito, faltante e não comprovado

Implementado (c57f324): tool em `server.py:556-580`. Mapeamento fraco confirmado ({C0417}): eval_1 só lista a tool e declara B-2; eval_2 é `! grep 'Five tools'` e declara B-3/B-4. Controles reais existem fora dos evals em `test_verify_fix.py`: `test_predicted_verification_reports_range_safety_and_confidence` (B-2), `test_no_verification_rows_reports_not_assessed` e `test_an_unapplied_additive_table_says_which_table_is_missing` (B-3), `test_a_safety_block_is_surfaced_not_hidden` e `test_a_block_is_not_collapsed_into_low_confidence` (B-4), além de regras de piso de ruído reforçadas por #144.

### Linhagem

SERVE-LEGS L5 → l5-fix.yaml (approved: true) → specs a8087ce (autor 2026-08-20; commit 2026-09-14) → implementação no mesmo ramo → cd59c8d 'accept and close the six L5 units' → PR #87 integrada em 2026-09-14 (merge 4adb854). Os hashes listados no corpo da PR (f3a314c, 2e13535...) não existem na main: o ramo foi rebaseado antes do merge → #144 (82be2e2) reforça piso inválido. Elo ausente: prova live (gates não rodados na leg).

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260820-verify-fix-tool.md; fontes/batch-revalidated-specs58-sources/history/T-20260820-verify-fix-tool.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__server.py; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__diagnose.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_verify_fix.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: tool consulta store e delega build_verdict; testes de comportamento presentes e distintos dos evals, que só registram/verificam texto. build_verdict usa o primeiro row como newest conforme ordem assumida do store. statusverified significa existência de verificação, inclusive previsão/recusa, não prova de efeito medido. RELATO de gate de aceite não foi reproduzido.

### Fluxo

Fluxo observado: verify_fix(job, finding?) → ReadStore.verifications → (tabela ausente: not_assessed nomeando a tabela) → VerificationView[] → build_verdict → FixVerdict(status, faixa, safety, blocked, confidence, notas de piso) → cliente.

### Consequências e risco

Há casos de chamada para range, ausência e recusa, sem executar a consulta real nesta revisão. O risco de mapeamento eval↔comportamento persiste. Consumidor deve ler method/blocked/notas e não interpretar verified isoladamente como melhoria, execução verde ou aceite humano.

### Alternativas e recomendação

Recomendado: manter encerrada; ao reutilizar o plano, apontar os evals para os testes de test_verify_fix.py. Alternativa: só nota. Não refazer a tool.

### Dependências e paralelismo

Nenhuma dependência pendente (read-layer e models entregues). A correção do mapeamento dos evals no plano l5-fix.yaml é documental e paralela; a prova live de verify_fix acompanha a de VERIFICATIONS_SQL e exige ClickHouse autorizado.

### Plano e aceite propostos

Para reuso: eval_1 → teste de faixa/safety/confiança; eval_2 → testes not_assessed e bloqueio; checagem de processo: descrição do eval deve corresponder ao corpo. Esta spec: nota.

### Comunicação entre responsáveis

Explicar a outro pod: 'verify_fix tem testes que provam faixa, segurança, confiança, not_assessed e bloqueio; os evals que fecharam a spec só conferiam o registro da tool e a ausência de um texto no docstring, então o verde deles não prova o comportamento.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Devolvendo lista vazia quando não há verificação, o usuário leria 'nada a temer' onde o Verify nem olhou. Que caso o teste ainda não cobre? — A tool contra apex.fix_verifications real; e os evals declarados, que não exercitam B-2..B-4. Como eu explicaria isso para outro pod? — 'Leia o corpo do eval: aqui o verde vinha de um grep; a prova está em outro arquivo de teste.'

### Próxima ação e encerramento

Ação: nota de mapeamento e vínculo à prova live. Owner a confirmar: Serve. Entrada: test_verify_fix.py. Saída: plano corrigido se reutilizado. Encerramento: já encerrada.

<a id="item-315"></a>

## T-20260918-execution-stage-attribution-offline — T-20260918-execution-stage-attribution-offline.md

Frente: Engine / atribuição de execução (#115, #126). Encaminhamento: encerrada_fatia_offline_sem_consumidor_issue_115_aberta.

### Identidade e estado

`tasks/done/T-20260918-execution-stage-attribution-offline.md` (blob d6334c24). 'Resolve execution identity to stages offline', S, standard, P2; owner `(none)`; source_note issue #115. Estado `done`, aceite gravado pelo gate v3 (`signed_off_sig` hmac-sha256-v3, `accepted_tier: 1`, `accepted_attempt_id`, `acceptance_record_digest`) por `augustosilva`, autor da implementação — registro da ferramenta do próprio autor, não revisão humana independente nem autorização atual. Pod provável: Pod 2/Engine (caminhos engine/; nenhum pod no arquivo). Plano tasks/.plans/issue115-execution-attribution-offline.yaml.

### Intenção e benefício

Dar ao Engine um resolvedor puro de observações de stage para um resultado de atribuição explícito e determinístico (attributed, execution_id_absent, execution_id_not_found, conflict), escopado por (app_id, job_id), sem tocar ClickHouse, findings, Serve, Front ou watchers — a fatia 'ready_offline' de #115.

### Feito, faltante e não comprovado

Implementado (5bae3c8): `attribution.py` (138 linhas) com `AttributionStatus`, `StageExecutionObservation`, `ExecutionStageRequest`, `StageAttribution` e `resolve_stage_ids` (linha 80). Testes em `test_execution_attribution.py` (218 linhas) cobrem cada B-n: ordenação distinta entre tentativas (B-1/B-2), ausente sem sentinela (B-3), não encontrado (B-4), conflito sem atribuição parcial (B-5), zero como identidade real e bloqueio de app estrangeiro (B-6), validação (B-7) — controles reais, confirmando o que Codex C04-13 registra. Falta (fora do escopo, declarado): nenhum módulo de produção importa o resolvedor (busca textual: só o próprio arquivo e o teste); superfície pública, integração de store/consulta e prova runtime seguem em #115, aberta.

### Linhagem

issue #115 (aberta no snapshot) → plano issue115-* (approved: true) → spec autorizada → implementação/teste → done no mesmo dia → PR #126 integrada em 2026-10-06 (merge abed508, head 4ddb082). Commits posteriores no teste dentro da mesma PR: ebc3df9, 02b9d91, 6f3f2a0, 4ddb082 (zero vs ausente). Elo ausente: primeira superfície consumidora (decisão do dono, #115).

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260918-execution-stage-attribution-offline.md; fontes/batch-revalidated-specs58-sources/history/T-20260918-execution-stage-attribution-offline.txt; fontes/batch-revalidated-specs58-sources/git/engine__src__apex_engine__attribution.py; fontes/batch-revalidated-specs58-sources/git/engine__tests__test_execution_attribution.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO:dataclasses validam identidades/tipos, filtragem app/job exata e classificação determinística; testes distinguem zero/None e escopos. As fontes lidas não demonstram consumidor de produção. RELATOS de25passed/suíte/head4ddb082e novo aceite independente vêm do pacote anterior; não foram executados nem ratificados nesta auditoria. Flags HMAC/accepted não são autorização atual.

### Fluxo

Fluxo observado (offline): StageExecutionObservation[] (app_id, job_id, stage_id, stage_attempt, execution_id opcional) + ExecutionStageRequest → filtra pelo escopo exato → classifica (absent | not_found | attributed com stage_ids ordenados | conflict com ids conflitantes) → StageAttribution. Fluxo proposto em #115 e não existente: telemetria v0.6 → store → resolvedor → finding/Serve/Front.

### Consequências e risco

A primitiva está presente e o escopooffline é explícito. Sem consumidor demonstrado, não há entrega de superfície execução→stage comprovada. Isso reduz exposição direta demonstrada, sem permitir afirmação universal de nenhum risco de produto ou garantia sobre futuras integrações.

### Alternativas e recomendação

Recomendado: manter encerrada como fatia offline e conduzir a escolha da primeira superfície em #115 (Codex E02), preservando os estados do resolvedor. Alternativa: não integrar e manter só a primitiva — perde o objetivo de #115. Não impor três PRs nem substituir findings de job por stages (C04-13).

### Dependências e paralelismo

Nenhuma dependência para permanecer encerrada. A integração depende de decisão do dono (#115) e, para runtime, de prova SQL/RDD autorizada; estudos de contrato e casos podem correr em paralelo.

### Plano e aceite propostos

Não ação nesta spec. Para a integração (spec nova): (1) escolher consumidor; (2) adaptador do store que produza observações escopadas; (3) testes de ponta do adaptador reutilizando os quatro estados; (4) controle negativo: linha de outro app com mesmo job_id não altera resultado; (5) prova runtime separada.

### Comunicação entre responsáveis

Explicar: 'O Engine sabe resolver execution_id para stages com quatro respostas honestas, testadas; ninguém usa isso ainda. A integração e a prova ao vivo continuam em #115.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Tratando zero como ausência ou sintetizando -1, uma execução real de id 0 seria perdida e um ausente pareceria atribuído; devolvendo atribuição parcial em conflito, um stage seria creditado a duas execuções. Que caso o teste ainda não cobre? — Observações vindas do store real (tipos e nulos do driver) e o consumidor que ainda não existe. Como eu explicaria isso para outro pod? — 'A primitiva está pronta e honesta; falta decidir onde ela aparece.'

### Próxima ação e encerramento

Ação: manter encerrada; acompanhar decisão de superfície em #115. Owner a confirmar: Engine + dono de #115. Entrada: este parecer e C04-13. Saída: decisão de primeira superfície. Encerramento: já encerrada no escopo offline.

<a id="item-316"></a>

## T-20260918-pwsh-command-aware-coverage — T-20260918-pwsh-command-aware-coverage.md

Frente: Package / interface e CI PowerShell (#124, #128). Encaminhamento: encerrada_com_lacuna_de_invocacao_mantida_em_124.

### Identidade e estado

`tasks/done/T-20260918-pwsh-command-aware-coverage.md` (blob db3f774a). 'Make package dry-run coverage explicit and command-aware', M, standard, P2; owner `(none)`; source_note issue #124. Estado `done`, aceite gravado pelo gate v3 (`signed_off_sig` hmac-sha256-v3, `accepted_tier: 1`, `accepted_attempt_id`, `acceptance_record_digest`) por `augustosilva`, autor da implementação — registro da ferramenta do próprio autor, não revisão humana independente nem autorização atual. Pod provável: Pod 2/Package (scripts/, tests/ raiz e CI). Spec, plano e implementação nasceram no mesmo commit a971f8b (2026-09-18), já como done — não há estado 'ready' anterior no histórico.

### Intenção e benefício

Verificar PowerShell 7 explicitamente no CI e fazer o DryRun reportar o mesmo handler que a execução real invocaria, sem mutações nem chamadas externas, para que uma ação nomeada não pareça coberta enquanto seu handler real é inalcançável.

### Feito, faltante e não comprovado

Implementado: passo 'Verify PowerShell 7' no job python do CI (`ci.yml:87-90`, ainda presente após o CI enxuto de #160); plano de ações em `apex.ps1:730-783` com objetos `{Handler, Command}` e DryRun em 785+; testes `test_every_command_has_a_non_mutating_dry_run` (compara o resumo completo), `test_missing_powershell_fails_closed`, `test_package_requires_powershell_7_without_legacy_fallback` (`test_apex_initial_package.py:55-160`). Lacuna confirmada (concordo com Codex C04-12): `Handler` (texto) e `Command` (scriptblock) são campos independentes do mesmo objeto; o DryRun retorna antes de executar `Command`, então trocar só o `Command` não muda o teste — B-4 ('não podem divergir') não é garantido. #124 continua aberta.

### Linhagem

Issue #124 → spec+plano+implementação a971f8b → endurecimento 767d555 (outra spec) → PR #128 integrada em 2026-10-06 (merge d8c1a3c, head 2b84c7a). Elo ausente: teste que alcance cada handler real com handlers inofensivos.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260918-pwsh-command-aware-coverage.md; fontes/batch-revalidated-specs58-sources/history/T-20260918-pwsh-command-aware-coverage.txt; fontes/batch-revalidated-specs58-sources/git/scripts__apex.ps1; fontes/batch-revalidated-specs58-sources/git/tests__test_apex_initial_package.py; fontes/batch-revalidated-specs58-sources/git/.github__workflows__ci.yml. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: CI verifica majorpwsh e pacote exigeVersion7; DryRun usa Handler e sai antes de Command, cuja associação é outro campo. Teste compara resumo textual; não mede external_calls0. Snapshot de não mutação cobre diretório runtime em ações representativas, não todo filesystem/serviços. B4não é garantido pelo mesmoobjeto. RELATOS18/69passednão foram executados aqui.

### Fluxo

Fluxo observado: apex.ps1 <ação> [-DryRun] → tabela de planos → DryRun: imprime 'APEX_DRY_RUN=passed action=... handler=<Handler> mutations=0 external_calls=0' e sai ; real: executa <Command>. CI: pwsh -Command verifica major ≥ 7 antes do gate raiz.

### Consequências e risco

Mapeamentos observados aparentam coerentes no snapshot, mas código e rótulo podem divergir sem alterar DryRun. Strings mutations0/external_calls0são declarações, não instrumentação. A ficha registra escopo e lacuna de controle sem alegar defeito runtime observado.

### Alternativas e recomendação

Recomendado: manter encerrada e tratar a lacuna em #124 (como C04-12): derivar `Handler` do próprio scriptblock, ou testar a invocação real com funções substituídas por stubs inofensivos. Alternativa: aceitar o escopo atual com revisão explícita do critério de #124 pelo mantenedor.

### Dependências e paralelismo

Nenhuma dependência para permanecer encerrada. O controle de invocação depende só de pwsh no ambiente de teste; pode correr em paralelo a #123/#167.

### Plano e aceite propostos

Para #124: (1) teste que injeta stubs para cada função-alvo e executa a ação sem -DryRun, verificando a chamada; (2) controle negativo: trocar o Command de 'smoke' por 'e2e' deve falhar; (3) manter testes de não mutação. Esta spec: nota da lacuna.

### Comunicação entre responsáveis

Explicar: 'O DryRun diz qual handler seria chamado e o CI exige pwsh 7; mas o rótulo do handler e o código executado são campos separados, e nada testa que coincidem. #124 continua aberta por isso.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Sem o passo explícito de pwsh, uma imagem de runner sem PowerShell faria os testes pularem em vez de falhar. Que caso o teste ainda não cobre? — Um Command trocado mantendo o mesmo Handler: o DryRun continuaria verde. Como eu explicaria isso para outro pod? — 'O DryRun prova o rótulo, não a chamada; para provar a chamada é preciso executar com handlers falsos.'

### Próxima ação e encerramento

Ação: vincular a lacuna de invocação a #124. Owner a confirmar: Package (Pod 2). Entrada: apex.ps1:730-800 e C04-12. Saída: spec/teste de invocação em #124. Encerramento: esta spec já encerrada; #124 fecha com o controle.

<a id="item-317"></a>

## T-20260918-tail-outlier-finding-contract — T-20260918-tail-outlier-finding-contract.md

Frente: Engine / contrato e watcher de cauda (#123, #127). Encaminhamento: encerrada_eval_aponta_teste_renomeado_pela_remediacao.

### Identidade e estado

`tasks/done/T-20260918-tail-outlier-finding-contract.md` (blob b138e80e). 'Add an honest tail-outlier finding contract', M, standard, P2; owner `(none)`; source_note issue #123. Estado `done`, aceite gravado pelo gate v3 (hmac-sha256-v3, tier 1, attempt_id, record_digest) por `augustosilva`, autor da implementação — registro da ferramenta do próprio autor, não revisão humana independente nem autorização atual. Pod provável: Pod 2/Engine (caminhos engine/; nenhum pod no arquivo). Plano issue123-tail-outlier-engine.yaml (unidade 1 de 2).

### Intenção e benefício

Criar o tipo aditivo `TAIL_OUTLIER` e um validador estreito que aceite só evidência estruturada de cauda de duração esparsa (≥100 tarefas e amostras, p50/max positivos, max/p50 estritamente > 10), sem enfraquecer o validador de skew — o código histórico rotulava candidato só de duração como SKEW_ON_JOIN.

### Feito, faltante e não comprovado

Implementado (f1dcb30): `FindingType.TAIL_OUTLIER` (`schema.py:41`) e `_tail_outlier_issues` (`validation.py:55-125`). Endurecido depois pela própria remediação (5cec1f2): rejeição de inteiros enormes (OverflowError), bool, string, NaN e infinito. Divergência de eval: o eval_1 nomeia `test_tail_outlier_type_does_not_weaken_skew_validation`, criado em f1dcb30 e renomeado em 5cec1f2 para `test_tail_outlier_details_do_not_weaken_skew_validation` (`test_contract_engine.py:449`) — reexecutado na main, o eval teria erro de coleta (inferência). Os outros dois testes nomeados existem (304, 325). O comportamento B-4 continua coberto pelo teste renomeado.

### Linhagem

issue #123 (aberta no snapshot) → plano issue123-* (approved: true) → spec autorizada → implementação → done → PR #127 integrada em 2026-10-06 (merge fec8a7f, head 4e44bfd). Elo: aceite de 2026-09-19 00:45Z sobre f1dcb30; a remediação 5cec1f2 renomeou o teste no mesmo dia.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260918-tail-outlier-finding-contract.md; fontes/batch-revalidated-specs58-sources/history/T-20260918-tail-outlier-finding-contract.txt; fontes/batch-revalidated-specs58-sources/git/engine__src__apex_engine__schema.py; fontes/batch-revalidated-specs58-sources/git/engine__src__apex_engine__validation.py; fontes/batch-revalidated-specs58-sources/git/engine__tests__test_contract_engine.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO:TAIL_OUTLIERdistinto, _tail_outlier_issuesrejeita ausência/tipos indevidos/não finitos, exigecontagens≥100, p50/maxpositivos e razão>10; testes incluem fronteiras e skewseparado. Nó test_tail_outlier_type_does_not_weaken_skew_validationnão aparece; sucessor detailsestá presente. RELATO58passednão foi reproduzido. Cobertura presente não é teste aprovado novo. _tail_outlier_issues testa limites individuais, não igualdade entre ratio e max/p50 ou contagens inteiras/coerentes. O próprio caso aceito usa max10/p501 e ratio10.1; não chamar isso de coerência aritmética validada.

### Fluxo

Fluxo observado: watcher emite Finding(TAIL_OUTLIER, details) → validate_finding → _tail_outlier_issues (finito, limites, contagens) → aceito/rejeitado ; SKEW_ON_JOIN/TASK_SKEW → _skew_issues inalterado (volume, join, forma fechada).

### Consequências e risco

Contrato está implementado com controles discriminantes para evidência declarada, mas não prova que a coleta/detector produz dados representativos nem que o gate encontra o job correto. Reexecutar evalantigo falharia por nome ausente, fato separado de regressão funcional. Não foi excluído risco universal.

### Alternativas e recomendação

Recomendado: manter encerrada com nota 'teste renomeado em 5cec1f2'. Alternativa: emendar o eval (reescreve o aceite histórico). Não reutilizar SKEW_ON_JOIN para evidência só de duração (anti-padrão).

### Dependências e paralelismo

Nenhuma dependência pendente. O watcher (spec seguinte) depende desta e está entregue. A garantia de associação do gate (#123) é frente separada.

### Plano e aceite propostos

Condição de não ação no código. Nota documental: 'eval_1 cita test_tail_outlier_type_does_not_weaken_skew_validation, renomeado em 5cec1f2 para ..._details_do_not_weaken_...'. Ao reutilizar issue123-tail-outlier-engine.yaml, atualizar o node id na linha 44 do plano.

### Comunicação entre responsáveis

Explicar: 'O tipo TAIL_OUTLIER e seu validador existem desde #127 e não afrouxam o de skew; o eval desta spec cita um teste que a remediação renomeou.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Rotulando cauda de duração como SKEW_ON_JOIN, o validador de skew exigiria volume e join que essa evidência não tem, ou seria afrouxado para aceitá-la. Que caso o teste ainda não cobre? — O eval declarado, que aponta um nó inexistente desde 5cec1f2. Como eu explicaria isso para outro pod? — 'Cauda de duração é candidato de aviso, não prova de skew de join; por isso tem tipo próprio.'

### Próxima ação e encerramento

Ação: nota de renomeação. Owner a confirmar: Engine. Entrada: 5cec1f2. Saída: nota e, se reutilizado, plano corrigido. Encerramento: já encerrada.

<a id="item-318"></a>

## T-20260918-tail-outlier-package-wiring-offline — T-20260918-tail-outlier-package-wiring-offline.md

Frente: Package / roteamento tail-outlier (#123, #127). Encaminhamento: encerrada_testes_estruturais_garantia_do_gate_em_123.

### Identidade e estado

`tasks/done/T-20260918-tail-outlier-package-wiring-offline.md` (blob 4d17d432). 'Wire tail-outlier through the canonical runner and package command', M, standard, P2; owner `(none)`; source_note #123. Estado `done`, aceite gravado pelo gate v3 (hmac-sha256-v3, tier 1, attempt_id, record_digest) por `augustosilva`, autor da implementação — registro da ferramenta do próprio autor, não revisão humana independente nem autorização atual. Pod provável: Pod 2/Package+DEV (scripts/, dev/scripts, tests/ raiz).

### Intenção e benefício

Completar o caminho offline do comando público `apex.ps1 tail-outlier` até o workload canônico, removendo o 'throw' obsoleto e mantendo as falhas explícitas (job_id ausente, saída não-zero do Engine, watcher ausente), sem executar Spark/Docker nesta folha.

### Feito, faltante e não comprovado

Implementado (7424853): `e2e_canonical.ps1` aceita e mapeia `tail_outlier`; `Invoke-TailOutlierGate` (`apex.ps1:677-711`) chama o runner com `-Scenario tail_outlier`, extrai o job_id do log, roda o Engine `--dry-run --no-crew`, exige exit 0 e a substring `tail_outlier_watcher`. Testes `test_tail_outlier_package.py` são estruturais (leem o texto do script e checam ordem de guardas e strings). B-4 ('emite ... llm_calls=0') é satisfeito pelo literal da linha 710, sem medição (concordo com Codex C04-11). Prova runtime posterior relatada no documento de entrega (2026-09-21).

### Linhagem

issue #123 (aberta no snapshot) → plano issue123-* (approved: true) → spec autorizada → implementação → done → PR #127 integrada em 2026-10-06 (merge fec8a7f, head 4e44bfd). Elos posteriores: endurecimento c0af6d9 (folha de auditoria) e ajustes 754f45e/5b41c77 citados no documento de entrega.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260918-tail-outlier-package-wiring-offline.md; fontes/batch-revalidated-specs58-sources/history/T-20260918-tail-outlier-package-wiring-offline.txt; fontes/batch-revalidated-specs58-sources/git/scripts__apex.ps1; fontes/batch-revalidated-specs58-sources/git/dev__scripts__e2e_canonical.ps1; fontes/batch-revalidated-specs58-sources/git/tests__test_tail_outlier_package.py; fontes/batch-revalidated-specs58-sources/git/docs__e2e__TAIL_OUTLIER_RUNTIME_GATE.md. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: allowlist/map tail_outlier, chamada canônica e guardas de job/exits/texto. Engine roda dry-run/no-crew; passed imprime llm_calls0literal. Substring tail_outlier_watchernão exige objeto finding válido nem stage associado. Testes leem código, sem invocar handlers. RELATOScore09/20e wrapper09/21possuem ambientes/limites distintos; não foram reproduzidos.

### Fluxo

Fluxo observado: apex.ps1 tail-outlier → Invoke-TailOutlierGate → doctor → e2e_canonical.ps1 -Scenario tail_outlier → log 'APEX_SESSION job_id=...' → Engine --dry-run --no-crew → exit 0? → saída contém 'tail_outlier_watcher'? → imprime passed + llm_calls=0 (literal).

### Consequências e risco

O script contém guardas de falhas enumeradas, mas não é prova fail-closed de toda semântica do gate: ocorrência textual do watcher pode passar sem verificar finding/stage esperado, e LLM0não é medição. A garantia pública deve permanecer limitada ao objeto realmente validado.

### Alternativas e recomendação

Recomendado: manter encerrada; a decisão de garantia (job vs stage) e a medição de chamadas LLM pertencem a #123/DEC-N6. Alternativa: remover `llm_calls=0` do marcador até medir — mais honesto, muda a saída pública.

### Dependências e paralelismo

Nenhuma dependência para permanecer encerrada. As melhorias de garantia dependem de decisão humana em #123; podem ser desenhadas offline em paralelo.

### Plano e aceite propostos

Não ação nesta spec. Em #123: (1) comparar stage do finding com o asserido; (2) medir chamadas LLM ou retirar o literal; (3) testes que executem o gate com stubs, não só leiam o texto.

### Comunicação entre responsáveis

Explicar a outro pod: 'O comando tail-outlier chega ao workload canônico e falha fechado em job ausente, Engine com erro ou watcher ausente; os testes leem o script, e o llm_calls=0 impresso no final é texto fixo, não uma contagem medida.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Removendo as guardas de job_id ou de exit code, um run sem telemetria ou um Engine quebrado poderia terminar em 'passed'. Que caso o teste ainda não cobre? — A execução do gate (os testes leem o script), um finding de outro stage e uma chamada LLM real sob --no-crew. Como eu explicaria isso para outro pod? — 'Os testes provam a forma do script; a prova de que o gate funciona é o runtime, e ele não mede LLM.'

### Próxima ação e encerramento

Ação documental: preservar entrega offline e vincular lacunas de associação/LLM à#123. Owner a confirmar: Package+Engine/acceptor. Entrada: código, testes e recibos distintos. Saída: nota com garantia por job/texto e proposta de objeto/stage validado. A revisão não altera produto nem aceita runtime.

<a id="item-319"></a>

## T-20260918-tail-outlier-watcher-offline — T-20260918-tail-outlier-watcher-offline.md

Frente: Engine / contrato e watcher de cauda (#123, #127). Encaminhamento: encerrada_controles_presentes.

### Identidade e estado

`tasks/done/T-20260918-tail-outlier-watcher-offline.md` (blob d4758c4e). 'Implement and register the deterministic tail-outlier watcher', M, standard, P2; owner `(none)`; depends_on finding-contract. Estado `done`, aceite gravado pelo gate v3 (hmac-sha256-v3, tier 1, attempt_id, record_digest) por `augustosilva`, autor da implementação — registro da ferramenta do próprio autor, não revisão humana independente nem autorização atual. Pod provável: Pod 2/Engine (caminhos engine/; nenhum pod no arquivo).

### Intenção e benefício

Um watcher puro e determinístico que emite aviso TAIL_OUTLIER só para cauda grande e esparsa de duração efetiva que o watcher de skew atual não reivindica, preferindo a população retry-safe e rotulando a fonte legada.

### Feito, faltante e não comprovado

Implementado (1cf109a): `watchers/tail_outlier.py` (72 linhas) com `MIN_TASKS_FOR_TAIL = 100`, `MIN_DURATION_SAMPLES_FOR_TAIL = 100`, `TAIL_WARNING_RATIO = 10.0`, adiando quando `skew.evaluate(...)` devolve finding (linha 37), severidade WARNING; registrado em `STAGE_WATCHERS` (segundo da tupla). Testes nomeados no eval_1 existem todos (`test_watchers.py:140-225`): população retry-safe, fallback legado, limites silenciosos, adiamento ao skew, volume alto sem dono de skew, registro e alcance. Usa `effective_*` e `tail_ratio` de #89 e o skew_ratio retry-safe de #99.

### Linhagem

issue #123 (aberta no snapshot) → plano issue123-* (approved: true) → spec autorizada → implementação → done → PR #127 integrada em 2026-10-06 (merge fec8a7f, head 4e44bfd). Dependências técnicas anteriores: #89 (campos/propriedades) e #99 (skew retry-safe).

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260918-tail-outlier-watcher-offline.md; fontes/batch-revalidated-specs58-sources/history/T-20260918-tail-outlier-watcher-offline.txt; fontes/batch-revalidated-specs58-sources/git/engine__src__apex_engine__watchers__tail_outlier.py; fontes/batch-revalidated-specs58-sources/git/engine__src__apex_engine__watchers____init__.py; fontes/batch-revalidated-specs58-sources/git/engine__tests__test_watchers.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: watcher lê propriedades effective, exige contagens/ratio e pede decisão do skew em vez de duplicar política; registry o inclui. Testes exercitam casos declarados, fonte e fronteiras. Nenhuma chamada diretaCrew/LLMno módulo lido; isso não mede todo fluxo público. Relatos45passed/runtime vêm de outro recibo e não foram executados nesta auditoria.

### Fluxo

Fluxo observado: StageAggregate → contagens < 100 ou p50 ≤ 0 ou tail_ratio ≤ 10 → None ; skew.evaluate devolve finding → None ; senão Finding(TAIL_OUTLIER, WARNING, MEDIUM, details com p50/p99/max efetivos, razões, fonte, contagens) → run_all_offline/run_all.

### Consequências e risco

A métrica detecta cauda esparsa como aviso e explicita não estabelecer causa. Sua sensibilidade a uma tarefa é desenho, mas representatividade, invalidez de dados e associação do gate público exigem evidência separada; nenhum risco universal foi excluído.

### Alternativas e recomendação

Recomendado: manter encerrada. Alternativa futura: limiar configurável por carga — exigiria dados e decisão, não há evidência para isso agora.

### Dependências e paralelismo

Nenhuma dependência pendente: contrato TAIL_OUTLIER, propriedades effective_* (#89) e skew retry-safe (#99) estão entregues. A garantia de associação do gate público segue em #123 e não bloqueia esta spec.

### Plano e aceite propostos

Condição de não ação: controles discriminantes presentes (99/100 tarefas e amostras silenciosos, razão exata 10 silenciosa, p50 zero silencioso, adiamento quando skew reivindica). Reabrir só se os limiares mudarem por decisão com dados.

### Comunicação entre responsáveis

Explicar: 'O watcher de cauda só fala quando há pelo menos 100 amostras, a cauda passa de 10× e o skew não reivindicou o stage; ele não chama LLM.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Suprimindo todo stage com volume de shuffle presente, caudas reais em stages com volume normal seriam escondidas; duplicando a política de skew aqui, as duas poderiam divergir. Que caso o teste ainda não cobre? — Telemetria real em que successful_task_sample_count e task_count discordam muito, além do runtime relatado. Como eu explicaria isso para outro pod? — 'Cauda é aviso sobre poucas tarefas muito lentas; quando o skew explica o stage, o skew fala e a cauda se cala.'

### Próxima ação e encerramento

Ação: nenhuma. Owner a confirmar: Engine (Pod 2). Entrada: nenhuma nova. Saída: ficha como referência do watcher. Encerramento: já encerrada; mudanças de limiar exigem spec nova com dados de carga real.

<a id="item-320"></a>

## T-20260919-execution-attribution-audit-hardening — T-20260919-execution-attribution-audit-hardening.md

Frente: Engine / atribuição de execução (#115, #126). Encaminhamento: encerrada_remediacao_de_testes_e_docstring.

### Identidade e estado

`tasks/done/T-20260919-execution-attribution-audit-hardening.md` (blob b40b83fd). 'Harden offline execution attribution identity-boundary coverage', S, standard, P2; owner `(none)`; source_note #115. Estado `done`, aceite gravado pelo gate v3 (`signed_off_sig` hmac-sha256-v3, `accepted_tier: 1`, `accepted_attempt_id`, `acceptance_record_digest`) por `augustosilva`, autor da implementação — registro da ferramenta do próprio autor, não revisão humana independente nem autorização atual. Pod provável: Pod 2/Engine (caminhos engine/; nenhum pod no arquivo). Spec teve o eval corrigido (f528f6d) antes da implementação.

### Intenção e benefício

Fixar por teste e documentação dois limites que uma revisão independente achou sem cobertura: linhas de job estrangeiro e o resultado misto None + id não-alvo — sem mudar o comportamento do resolvedor.

### Feito, faltante e não comprovado

Implementado (ebc3df9): testes de escopo estrangeiro e de mistura None/não-alvo (`test_foreign_application_and_job_rows_cannot_change_scoped_outcomes`, `test_none_mixed_with_non_target_identity_is_not_found`, `test_missing_observation_does_not_conflict_with_present_target_identity`) e docstring de `resolve_stage_ids` com as regras de status. A spec chama a origem de 'Independent review approved ...' — a revisão citada não está anexada ao repositório; é relato da spec. Falta: nada no escopo.

### Linhagem

issue #115 (aberta no snapshot) → plano issue115-* (approved: true) → spec autorizada → implementação/teste → done no mesmo dia → PR #126 integrada em 2026-10-06 (merge abed508, head 4ddb082). Origem declarada: revisão independente (não localizada como artefato). Commits: 1ecc310 (autorização) → f528f6d (eval corrigido) → ebc3df9 (teste/doc) → 1910d23 (done).

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260919-execution-attribution-audit-hardening.md; fontes/batch-revalidated-specs58-sources/history/T-20260919-execution-attribution-audit-hardening.txt; fontes/batch-revalidated-specs58-sources/git/engine__src__apex_engine__attribution.py; fontes/batch-revalidated-specs58-sources/git/engine__tests__test_execution_attribution.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: casosforeignapp/job em estadosabsent/not_found/conflict e misturaNone/nãoalvo; docstring corresponde à classificação presente. RELATO: origem independentreviewe alteração somente testes/doc no histórico; artefato de aprovação não foi localizado neste escopo. evals de suíte não verificam semanticamente texto; não foram executados.

### Fluxo

Fluxo observado: mesmas observações escopadas → resolve_stage_ids → estados; testes injetam linhas de app/job estrangeiros e misturas de None para provar que o escopo exato isola o resultado.

### Consequências e risco

Casos adicionais protegem a fronteira de identidade no resolvedor puro. A revisão não demonstrou consumidor de produção nem prova runtime; isso limita a entrega, sem garantir ausência universal de risco. Fidelidade da docstring requer leitura além dos evals.

### Alternativas e recomendação

Recomendado: manter encerrada. Alternativa: anexar ao plano issue115-attribution-audit-hardening a revisão independente citada no 'Why', se existir, para que a origem da remediação seja auditável. Rejeitado pela própria spec: mudar a semântica de status ou a validação de identidade nesta folha.

### Dependências e paralelismo

Nenhuma dependência técnica: a primitiva (offline) já estava aceita. Paralelo a tudo; não bloqueia nem é bloqueada pela decisão de superfície de #115 nem pela prova SQL/RDD, que são frentes separadas.

### Plano e aceite propostos

Condição de não ação: os testes de escopo estrangeiro e de mistura None/não-alvo já discriminam B-1/B-2. Para B-3, se a regra de status mudar no futuro, exigir que a revisão de docstring seja parte do aceite humano, já que nenhum eval lê documentação.

### Comunicação entre responsáveis

Explicar: 'Testes extras garantem que linhas de outro app ou job não mudam o resultado da atribuição e que None mais id diferente dá not_found; o código não mudou.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Considerando linhas de outro job como evidência, um stage com mesmo número em outro run mudaria o resultado deste. Que caso o teste ainda não cobre? — A afirmação de que o docstring descreve corretamente as regras, que nenhum eval executa. Como eu explicaria isso para outro pod? — 'Escopo exato (app, job) é a fronteira; tudo fora dela é ignorado.'

### Próxima ação e encerramento

Ação: nenhuma; registrar a ficha como encerrada sem resíduo. Owner a confirmar: Engine. Entrada: nenhuma nova. Saída: referência no índice de #115. Encerramento: já encerrada; reabrir só se a semântica de status do resolvedor mudar.

