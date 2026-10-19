# Fichas documentais — lote 31

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-301"></a>

## T-20260820-l3-docs — T-20260820-l3-docs.md

Frente: Serve / L3 Understand — legibilidade do diagnóstico (#88). Encaminhamento: encerrada_historica_sem_aceite_formal.

### Identidade e estado

`tasks/done/T-20260820-l3-docs.md` (blob 6c2ccf54). 'Document readability across the lane docs', M, standard, P2; owner `(none)`; depends_on tool-surface-six e critical-path. Estado `done`; `accepted: false` e `signed_off: false` por escolha registrada: o commit 9ff859b e o corpo da PR #88 dizem que esses bits pertencem a `taskspec gate --stamp`, 'which is not in this repo', e que marcá-los à mão anula seu propósito — portanto 'done sem aceite' é deliberado e não omissão. Pod provável: Pod 3/Serve (caminhos serve/; nenhum pod no arquivo).

### Intenção e benefício

Refletir níveis de detalhe, explain_stage, cobertura e participação na cauda em README, VALIDATION e SERVE-LEGS, com contagem de testes copiada de execução real, sem tocar SERVE.md (lição do L2 sobre raio de escrita).

### Feito, faltante e não comprovado

Seções L3 de detalhes/cobertura/cauda e registro144passed estão presentes; README conserva título The six tools com prosa de oito. eval_2 não amarra contagem ao SHA ou seção: o crescimento da suíte não basta para prever falha, pois outra seção pode conter o mesmo número.

### Linhagem

SERVE-LEGS L3 → l3-understand.yaml (approved: true) → specs dc1c2ce (autor 2026-08-20; commit 2026-08-26) → implementações no mesmo ramo → 9ff859b 'six units done' (status done, accepted false) → PR #88 integrada em 2026-09-14 (merge 1125cdb). Elo posterior: L5/L6/#129 reescreveram os mesmos arquivos sem atualizar o título do README.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260820-l3-docs.md; fontes/batch-revalidated-specs58-sources/history/T-20260820-l3-docs.txt; fontes/batch-revalidated-specs58-sources/git/serve__README.md; fontes/batch-revalidated-specs58-sources/git/serve__VALIDATION.md; fontes/batch-revalidated-specs58-sources/git/docs__lanes__SERVE-LEGS.md. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: documentação L3 datada, limite de idade nula e tabela F3.1–F3.4. RELATO:144passed/gates de08/20. eval de contagem procura o diário inteiro e a pipeline sem pipefail pode ocultar falha de pytest; resultado atual indeterminado sem execução. A frase two callers nunca divergirem é ampla: trim preserva um objeto, mas duas chamadas podem ler snapshots diferentes.

### Fluxo

Fluxo documental: execução da suíte e dos gates (L3) → números → VALIDATION (seção datada) ; funcionalidades → README ; entrega F3.1–F3.4 → SERVE-LEGS ; leitor de outro pod → documentos.

### Consequências e risco

Sem ação: a seção datada do L3 no VALIDATION continua correta como registro; o título '## The six tools' e o '/mcp lists the six tools' do README confundem quem lê hoje, ao lado da prosa 'eight tools'. Impacto documental baixo, probabilidade alta de confusão; confiança alta nos fatos.

### Alternativas e recomendação

Recomendado: manter encerrada e incluir o título do README no item único de reconciliação documental. Alternativa: título sem número ('The tools'), que não envelhece.

### Dependências e paralelismo

Nenhuma dependência para permanecer encerrada (tool-surface-six e critical-path entregues). O item único de reconciliação documental é independente desta spec, não depende de ambiente nem de decisão sobre apex_status e pode correr em paralelo às revisões de PR.

### Plano e aceite propostos

Não ação na spec. No item documental: título do README sem contagem ou derivado; preservar a seção L3 do VALIDATION; controle estático de contagem. Nota de aceite por desenho.

### Comunicação entre responsáveis

Explicar: 'A documentação do L3 foi feita e está datada no VALIDATION; o título do README ainda diz seis tools porque ninguém o atualizou depois.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Atualizando a seção L3 do VALIDATION com números de hoje, perderíamos o registro do que foi observado em 2026-08-20, inclusive o limite da idade nula. Que caso o teste ainda não cobre? — Títulos com número diferente de 'five': o eval só procura 'five tools'. Como eu explicaria isso para outro pod? — 'Seções datadas são história; títulos e prosa sem data precisam acompanhar o código.'

### Próxima ação e encerramento

Ação: remeter o título ao item documental. Owner a confirmar: Serve/documentação. Entrada: README:11. Saída: referência cruzada. Encerramento: já encerrada.

<a id="item-302"></a>

## T-20260820-l5-docs — T-20260820-l5-docs.md

Frente: Serve / L5 Fix — superfície da verify lane (#87). Encaminhamento: encerrada_historica_com_limite_live_ainda_declarado.

### Identidade e estado

`tasks/done/T-20260820-l5-docs.md` (blob 444cac84). 'Document fix verification across the lane docs', M, standard, P2; owner `(none)`; depends_on l5-tool-surface e suggest-fix-provenance. Estado `done`, aceite gravado pelo gate (`signed_off_sig` hmac-sha256-v2, horários com segundos em 2026-08-20 14:43Z) por `sidymar`, autor da implementação — registro de ferramenta do próprio autor, não revisão independente nem autorização atual. Pod provável: Pod 3/Serve (com dependência de contrato das lanes Verify/Memory).

### Intenção e benefício

Registrar que o L5 é uma superfície MCP sobre a verify lane (que já prediz, reexecuta e aplica gates de segurança em 105 testes) e não uma reimplementação, para que o próximo leitor não reconstrua o que já existe.

### Feito, faltante e não comprovado

Feito (9706ffb): seção '## L5 — fix verification, recorded 2026-08-20' no VALIDATION (`VALIDATION.md:288-347`) com '179 passed' e 'Not run for this leg' (gates live não executados; VERIFICATIONS_SQL não validado por parser real); README com verify_fix e a convenção de sinal (linhas 21, 104-139); SERVE-LEGS L5 reescrito (176-222) nomeando apex.fix_verifications. Estado atual: SERVE-LEGS:219 ainda diz que VERIFICATIONS_SQL não encontrou um parser real — limite não resolvido até c3c3ea3 por esta leitura. A seção L5 afirma que o EXPECTED_TOOLS do gate stdio foi atualizado para oito; o arquivo tem 7 (ver lote 01 e ACHADOS).

### Linhagem

SERVE-LEGS L5 → l5-fix.yaml (approved: true) → specs a8087ce (autor 2026-08-20; commit 2026-09-14) → implementação no mesmo ramo → cd59c8d 'accept and close the six L5 units' → PR #87 integrada em 2026-09-14 (merge 4adb854). Os hashes listados no corpo da PR (f3a314c, 2e13535...) não existem na main: o ramo foi rebaseado antes do merge. Elo ausente: execução live de verify_fix contra apex.fix_verifications real; a e2e de 2026-10-06 relata que a verify lane não rodou ponta a ponta.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260820-l5-docs.md; fontes/batch-revalidated-specs58-sources/history/T-20260820-l5-docs.txt; fontes/batch-revalidated-specs58-sources/git/serve__README.md; fontes/batch-revalidated-specs58-sources/git/serve__VALIDATION.md; fontes/batch-revalidated-specs58-sources/git/docs__lanes__SERVE-LEGS.md; fontes/batch-revalidated-specs58-sources/git/serve__tools__mcp_stdio_gate.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: docs descrevem superfície sobre Verify e registram179passed; VALIDATION afirma EXPECTED_TOOLS oito mas código lista sete. RELATO histórico: gates não executados para L5. Não foi localizado neste recorte recibo posterior que encerre a prova de VERIFICATIONS_SQL; ausência documental não prova nunca executada. eval_2 busca qualquer contagem no diário e não garante sucesso integral da suíte, logo crescimento não implica falha atual.

### Fluxo

Fluxo documental: suíte e decisão de desenho (superfície sobre a verify lane) → VALIDATION (seção datada) e SERVE-LEGS (L5) → leitor de outro pod; limite 'gates não executados' → Known limits.

### Consequências e risco

Sem ação: nenhum risco novo; o registro é honesto quanto ao que não foi provado. Risco documental: a frase sobre o gate stdio 'atualizado para oito' contradiz o arquivo. Confiança alta.

### Alternativas e recomendação

Recomendado: manter encerrada; incluir a correção da frase sobre EXPECTED_TOOLS no item de reconciliação do gate stdio; manter o limite de VERIFICATIONS_SQL visível até uma prova live. Alternativa: apagar o limite — não, ele continua verdadeiro.

### Dependências e paralelismo

Nenhuma dependência para permanecer encerrada. A prova live de VERIFICATIONS_SQL depende de ClickHouse com DDL v0.3 e linhas da verify lane — estudo e preparação podem correr em paralelo; execução exige autorização.

### Plano e aceite propostos

Não ação na spec. Para a prova live (item separado): semear fix_verifications em store autorizado, chamar verify_fix e comparar com a linha; recibo com SHA e versão. Doc: atualizar SERVE-LEGS:219 só depois da prova.

### Comunicação entre responsáveis

Explicar: L5 documenta Serve lendo o juízo do Verify pela tabela. Os registros lidos dizem que a SQL não foi provada live naquela entrega; nesta auditoria não foi localizado recibo posterior suficiente para encerrar essa pendência.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Reescrevendo o L5 como construção própria, alguém duplicaria predição e reexecução que a verify lane já faz, com duas respostas divergentes para a mesma pergunta. Que caso o teste ainda não cobre? — VERIFICATIONS_SQL contra um parser real, que o FakeClient não faz. Como eu explicaria isso para outro pod? — 'O Serve lê o que o Verify concluiu pela tabela; ele não julga de novo, e a consulta ainda precisa de prova num banco real.'

### Próxima ação e encerramento

Ação: vincular a frase do gate stdio ao item de reconciliação e manter o limite. Owner a confirmar: Serve/documentação. Entrada: VALIDATION:300-345. Saída: referência cruzada. Encerramento: já encerrada.

<a id="item-303"></a>

## T-20260820-l5-tool-surface — T-20260820-l5-tool-surface.md

Frente: Serve / L5 Fix — superfície da verify lane (#87). Encaminhamento: encerrada_historica_eval_aponta_teste_renomeado.

### Identidade e estado

`tasks/done/T-20260820-l5-tool-surface.md` (blob 44dce2df). 'Re-pin the tool surface for verify_fix', XS, standard, P2; owner `(none)`; depends_on verify-fix-tool. Estado `done`, aceite gravado pelo gate (`signed_off_sig` hmac-sha256-v2, horários com segundos em 2026-08-20 14:43Z) por `sidymar`, autor da implementação — registro de ferramenta do próprio autor, não revisão independente nem autorização atual. Pod provável: Pod 3/Serve (com dependência de contrato das lanes Verify/Memory).

### Intenção e benefício

Mover a asserção exata da superfície para incluir verify_fix, em commit próprio, porque uma tool não percebida num servidor que um modelo chama é evento de segurança.

### Feito, faltante e não comprovado

Feito em 3758d00 ('re-pin the tool surface at six, including verify_fix'), que também alterou `serve/tools/mcp_stdio_gate.py` (fora de touches_paths, que lista só test_server_tools.py). No SHA: o teste unitário é `test_the_contracted_tool_surface` com oito nomes ordenados (lista única de df6fe77); o eval_1 nomeia `test_exactly_the_six_contracted_tools`, inexistente — erro de coleta se reexecutado na main (inferência). O gate stdio ficou com 7 nomes porque o ramo L6, integrado depois, não o atualizou.

### Linhagem

SERVE-LEGS L5 → l5-fix.yaml (approved: true) → specs a8087ce (autor 2026-08-20; commit 2026-09-14) → implementação no mesmo ramo → cd59c8d 'accept and close the six L5 units' → PR #87 integrada em 2026-09-14 (merge 4adb854). Os hashes listados no corpo da PR (f3a314c, 2e13535...) não existem na main: o ramo foi rebaseado antes do merge. Elo: reconciliação entre L5 e L6 no teste unitário ocorreu (oito nomes), mas não no gate stdio.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260820-l5-tool-surface.md; fontes/batch-revalidated-specs58-sources/history/T-20260820-l5-tool-surface.txt; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_server_tools.py; fontes/batch-revalidated-specs58-sources/git/serve__tools__mcp_stdio_gate.py; fontes/batch-revalidated-specs58-sources/commits/3758d0012711.txt. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

FATO OBSERVADO: 3758d00 tocou o gate stdio além do raio declarado; teste atual com oito nomes. RELATO: o corpo da #87 diz que o gate foi movido 'to the six-tool surface but is unexercised'. INFERÊNCIA: o eval não é reproduzível na main. Nenhuma execução.

### Fluxo

Fluxo observado: create_server → list_tools → sorted == CONTRACTED_TOOLS (8). Paralelo: mcp_stdio_gate → EXPECTED_TOOLS (7, inclui verify_fix por 3758d00, sem recall_similar_runs).

### Consequências e risco

Igualdade atual dos oito nomes existe; stdio espera sete, então a checagem de listagem diverge antes de provar chamadas. A alteração fora dos paths está no stat preservado. Esses fatos reduzem confiabilidade da prova manual, sem demonstrar regressão ou ausência universal de impacto no produto.

### Alternativas e recomendação

Recomendado: manter encerrada com nota de sucessor (df6fe77) e registrar que esta unidade escreveu fora do raio declarado (gate stdio), o que é a origem parcial da cópia manual que depois envelheceu. Alternativa: só nota de sucessor.

### Dependências e paralelismo

Nenhuma dependência: verify-fix-tool entregue e o sucessor do controle está na main desde #101. O item de reconciliação do gate stdio é independente, editável sem ClickHouse e pode correr em paralelo a qualquer revisão de PR.

### Plano e aceite propostos

Condição de não ação no código. Nota documental: 'eval_1 aponta test_exactly_the_six_contracted_tools, renomeado; 3758d00 alterou também mcp_stdio_gate.py fora de touches_paths'. Para reuso do plano: declarar o gate stdio no raio da unidade ou derivar sua lista de CONTRACTED_TOOLS.

### Comunicação entre responsáveis

Explicar: 'verify_fix entrou na lista de tools em agosto; o teste mudou de nome e hoje lista oito. O gate stdio recebeu verify_fix aqui, mas não recall_similar_runs depois.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Sem atualizar nenhuma lista, verify_fix teria chegado à superfície sem que um diff de teste a justificasse. Que caso o teste ainda não cobre? — A lista do gate stdio, que ficou fora do controle unitário e só falha quando alguém roda o gate. Como eu explicaria isso para outro pod? — 'Toda cópia da lista de tools precisa ser atualizada junto; esta unidade atualizou duas e a seguinte só uma.'

### Próxima ação e encerramento

Ação: nota de sucessor e de escrita fora do raio declarado. Owner a confirmar: Serve. Entrada: 3758d00 e test_server_tools.py. Saída: nota no índice e vínculo ao item do gate stdio. Encerramento: já encerrada; o controle vigente é o único a manter.

<a id="item-304"></a>

## T-20260820-l6-docs — T-20260820-l6-docs.md

Frente: Serve / L6 Learn — memória entre runs (#86). Encaminhamento: encerrada_aceite_com_formato_nao_carimbado.

### Identidade e estado

`tasks/done/T-20260820-l6-docs.md` (blob 12b4e440). 'Document cross-run memory across the lane docs', M, standard, P2; owner `(none)`; depends_on l6-tool-surface e noise-floor-honesty. Estado `done`; campos de aceite com formato diferente dos carimbados pelo gate: `accepted_by`/`signed_off_by` = e-mail, `accepted_at`/`signed_off_at` = 2026-08-20T00:00:00Z (meia-noite exata) e nenhum `signed_off_sig`; o commit 9a7659c diz 'Specs signed off, accepted'. É diferença observável de formato; não se conclui má-fé nem validade, e nenhuma autorização é inferida. Pod provável: Pod 3/Serve (com dependência de contrato das lanes Verify/Memory).

### Intenção e benefício

Registrar que o L6 é superfície MCP sobre a memory lane (47 testes, tabela de embeddings normalizada), nomeando apex.plan_memory e apex.run_outcomes, para que ninguém reconstrua um backend de embeddings.

### Feito, faltante e não comprovado

Feito (b4ecc0d): seção '## L6 — cross-run memory, recorded 2026-08-20' no VALIDATION (`VALIDATION.md:348-436`) com '162 passed', recall_gate live contra ClickHouse 24.8.14.39 e 'Two defects only a live database could find'; README com recall_similar_runs e a regra do piso; SERVE-LEGS L6 (224-260). Divergência de contagem: o commit de aceite 9a7659c diz 'suite is 159 green' e o VALIDATION/PR dizem 162 — consistente com testes acrescentados por be0a4d8 depois do aceite. A seção diz 'joins the surface as the eighth tool', escrita/ajustada após a reconciliação.

### Linhagem

SERVE-LEGS L6 → l6-learn.yaml (approved: true) → specs 5485202 (autor 2026-08-20; commit 2026-09-14) → implementação → 9a7659c 'accept all six units' → be0a4d8 (depois do aceite) corrige dois defeitos achados em ClickHouse real e acrescenta recall_gate → PR #86 integrada em 2026-09-14 (merge 1e0ba80).

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260820-l6-docs.md; fontes/batch-revalidated-specs58-sources/history/T-20260820-l6-docs.txt; fontes/batch-revalidated-specs58-sources/git/serve__README.md; fontes/batch-revalidated-specs58-sources/git/serve__VALIDATION.md; fontes/batch-revalidated-specs58-sources/git/docs__lanes__SERVE-LEGS.md; fontes/batch-revalidated-specs58-sources/commits/be0a4d8.txt. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

FATO OBSERVADO: seções; formato dos campos de aceite; divergência 159/162 entre commit e VALIDATION. RELATO: recall_gate passed, zero escritas do servidor (autor). INFERÊNCIA: aceite registrado antes da correção live. Nenhuma execução.

### Fluxo

Fluxo documental: decisão (superfície sobre memory) → SERVE-LEGS ; suíte e gate live → VALIDATION (datado) ; regra do piso → README → leitor de outro pod.

### Consequências e risco

Registro histórico de L6 é útil e separa medidas de juízos, mas nem toda prosa permanece atual: Known limits L6 diz não capturar SparkConf, enquanto o recibo06/10 no mesmo VALIDATION descreve job_conf com8chaves após rebuild. Campos de aceite sem signed_off_sig não certificam nem invalidam o ato por si sós; apenas não fornecem essa evidência de ferramenta.

### Alternativas e recomendação

Recomendado: manter encerrada; registrar no índice que o aceite do L6 não tem assinatura do gate e antecede be0a4d8. Alternativa: re-aceite pelo gate sobre o SHA integrado, se o processo exigir uniformidade.

### Dependências e paralelismo

Nenhuma dependência para permanecer encerrada. A nota de processo é paralela; um re-aceite exigiria a ferramenta externa e ClickHouse para o gate live.

### Plano e aceite propostos

Condição de não ação no conteúdo documental. Nota de processo no índice: 'aceite do L6 sem signed_off_sig, com e-mail e horário 00:00; antecede be0a4d8 (correções live)'. Se o processo exigir uniformidade, re-aceite pelo gate no SHA integrado, com recibo.

### Comunicação entre responsáveis

Explicar: 'O L6 está documentado como superfície sobre a memory lane, com gate live registrado. Os campos de aceite dessas seis specs não têm assinatura do gate, ao contrário das outras legs.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Duplicar embeddings no Serve criaria outra resposta para a memória do mesmo plano; reescrever contagens históricas apagaria a sequência159→162. Que caso o teste ainda não cobre? Ligação de contagem à seção/SHA e sucesso integral da suíte; grep no diário pode coincidir com outra entrega. Como eu explicaria isso para outro pod? Serve expõe a memória existente, os recibos têm datas e os campos de aceite são evidência histórica sem validação criptográfica nova.

### Próxima ação e encerramento

Ação: nota de processo sobre o aceite. Owner a confirmar: Serve + dono do processo Task-Spec. Entrada: front matter das seis specs L6. Saída: nota ou re-aceite. Encerramento: já encerrada.

<a id="item-305"></a>

## T-20260820-l6-tool-surface — T-20260820-l6-tool-surface.md

Frente: Serve / L6 Learn — memória entre runs (#86). Encaminhamento: encerrada_origem_da_deriva_do_gate_stdio.

### Identidade e estado

`tasks/done/T-20260820-l6-tool-surface.md` (blob 3af62347). 'Re-pin the tool surface for recall_similar_runs', XS, standard, P2; owner `(none)`; depends_on recall-runs-tool. Estado `done`; campos de aceite com formato diferente dos carimbados pelo gate: `accepted_by`/`signed_off_by` = e-mail, `accepted_at`/`signed_off_at` = 2026-08-20T00:00:00Z (meia-noite exata) e nenhum `signed_off_sig`; o commit 9a7659c diz 'Specs signed off, accepted'. É diferença observável de formato; não se conclui má-fé nem validade, e nenhuma autorização é inferida. Pod provável: Pod 3/Serve (com dependência de contrato das lanes Verify/Memory).

### Intenção e benefício

Incluir recall_similar_runs na asserção exata da superfície de tools, em commit próprio sem mudança de código, para que a mudança fique legível no git log — uma tool não percebida num servidor que um modelo chama é evento de segurança.

### Feito, faltante e não comprovado

Feito em 60e6ef2 (uma linha em test_server_tools.py). No SHA: lista única de oito nomes no teste unitário; eval_1 nomeia `test_exactly_the_six_contracted_tools`, inexistente — erro de coleta se reexecutado (inferência). Esta unidade não tocou `serve/tools/mcp_stdio_gate.py` (o L6 provou ao vivo por `recall_gate.py`), e é por isso que o gate stdio no SHA tem 7 nomes sem recall_similar_runs, apesar de o VALIDATION (seção L5) afirmar o contrário.

### Linhagem

SERVE-LEGS L6 → l6-learn.yaml (approved: true) → specs 5485202 (autor 2026-08-20; commit 2026-09-14) → implementação → 9a7659c 'accept all six units' → be0a4d8 (depois do aceite) corrige dois defeitos achados em ClickHouse real e acrescenta recall_gate → PR #86 integrada em 2026-09-14 (merge 1e0ba80). Elo ausente: atualização do gate stdio na reconciliação de 2026-09-14 entre #87 e #86.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260820-l6-tool-surface.md; fontes/batch-revalidated-specs58-sources/history/T-20260820-l6-tool-surface.txt; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_server_tools.py; fontes/batch-revalidated-specs58-sources/git/serve__tools__mcp_stdio_gate.py; fontes/batch-revalidated-specs58-sources/commits/60e6ef20ff35.txt. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: unidade60e6ef2alterou apenas teste conforme stat; lista atual tem recall e stdio não. Nó test_exactly_the_six_contracted_tools não existe no arquivo atual, portanto o eval histórico já não referencia o controle vigente. RELATO:13evals verdes no aceite. Integração paralela como causa é reconstrução consistente, não experimento executado.

### Fluxo

Fluxo observado: create_server (8) → list_tools → sorted == CONTRACTED_TOOLS ; mcp_stdio_gate → EXPECTED_TOOLS (7) → divergência ; recall_gate → recall_similar_runs ao vivo (relato).

### Consequências e risco

Controle de nomes está presente e a igualdade do stdio diverge; isso impede usar esse gate como prova atual sem reconciliação. A leitura não demonstra regressão de produto nem a ausência dela; anotações/comportamentos têm controles separados.

### Alternativas e recomendação

Recomendado: manter encerrada e usar esta ficha como origem documentada do item 'gate stdio derivado de fonte única'. Alternativa: só acrescentar recall_similar_runs ao gate — corrige o sintoma.

### Dependências e paralelismo

Nenhuma dependência: recall-runs-tool entregue; sucessor do controle na main. O item do gate stdio (derivar a lista de fonte única) é independente, paralelo e editável sem ClickHouse; executar o gate depois exige ambiente.

### Plano e aceite propostos

Condição de não ação no código desta spec. Nota documental: 'eval_1 aponta teste renomeado; esta unidade não atualizou mcp_stdio_gate.py, origem da lista de 7'. No item do gate: lista derivada, teste que falhe com nome faltante e correção da frase do VALIDATION.

### Comunicação entre responsáveis

Explicar a outro pod: 'recall_similar_runs entrou na lista oficial de tools em 60e6ef2; o gate stdio tem uma cópia própria que esta leg não atualizou, e por isso hoje ele lista sete tools para um servidor com oito.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Pinando só no gate stdio e não no teste unitário, o CI não perceberia uma tool nova, porque o gate stdio não roda no CI. Que caso o teste ainda não cobre? — O gate stdio contra a superfície de oito, que divergiria na listagem. Como eu explicaria isso para outro pod? — 'Duas listas manuais da mesma superfície envelhecem em tempos diferentes; derive a segunda da primeira.'

### Próxima ação e encerramento

Ação: vincular esta ficha como origem do item do gate stdio. Owner a confirmar: Serve. Entrada: 60e6ef2, mcp_stdio_gate.py:28-40. Saída: referência cruzada. Encerramento: já encerrada; o item novo fecha a divergência.

<a id="item-306"></a>

## T-20260820-noise-floor-honesty — T-20260820-noise-floor-honesty.md

Frente: Serve / L6 Learn — memória entre runs (#86). Encaminhamento: encerrada_controles_presentes_com_endurecimento_posterior.

### Identidade e estado

`tasks/done/T-20260820-noise-floor-honesty.md` (blob b32a6d15). 'Never call a configuration better without a floor', S, standard, P2; owner `(none)`; depends_on recall-runs-tool (a PR #86 relata que esta unidade entrou antes da tool por ser pura). Estado `done`; campos de aceite com formato diferente dos carimbados pelo gate: `accepted_by`/`signed_off_by` = e-mail, `accepted_at`/`signed_off_at` = 2026-08-20T00:00:00Z (meia-noite exata) e nenhum `signed_off_sig`; o commit 9a7659c diz 'Specs signed off, accepted'. É diferença observável de formato; não se conclui má-fé nem validade, e nenhuma autorização é inferida. Pod provável: Pod 3/Serve (com dependência de contrato das lanes Verify/Memory).

### Intenção e benefício

Relatar runs anteriores como medições e só chamar uma configuração de melhor contra um piso de ruído medido (CONTRACT regra 2), dizendo 'indistinguível da variação' dentro do piso e não comparando a partir de um único run.

### Feito, faltante e não comprovado

Implementado (ca119be): `summarise_recall` (`diagnose.py:1085-1210`); testes `test_no_floor_means_no_better_claim`, `test_difference_inside_floor_is_indistinguishable`, `test_single_prior_run_draws_no_comparison`, `test_cleared_floor_is_named` (`test_diagnose.py:681-760`) e, no nível da tool, `test_recall_without_a_floor_calls_no_configuration_better` (`test_recall_view.py:294`). Acréscimos posteriores: regra 3 de atribuição (duas configurações capturadas distintas) e retenção de veredito com piso inválido (82be2e2, #144). `PRIOR_OUTCOMES_SQL` não ordena por wall clock (afirmação do corpo #86).

### Linhagem

SERVE-LEGS L6 → l6-learn.yaml (approved: true) → specs 5485202 (autor 2026-08-20; commit 2026-09-14) → implementação → 9a7659c 'accept all six units' → be0a4d8 (depois do aceite) corrige dois defeitos achados em ClickHouse real e acrescenta recall_gate → PR #86 integrada em 2026-09-14 (merge 1e0ba80) → #144 endurece pisos inválidos.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260820-noise-floor-honesty.md; fontes/batch-revalidated-specs58-sources/history/T-20260820-noise-floor-honesty.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__diagnose.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_diagnose.py; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__models.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

FATO OBSERVADO: função e testes por regra. RELATO: '13 evals pass' (aceite) e 162 passed (VALIDATION). INFERÊNCIA: B-1..B-4 têm controles reais nos dois níveis. Limite de fronteira (#117/C04-14): o piso é fração em compare_runs e percentual em replay/linhas — normalização explícita pendente. Nenhuma execução.

### Fluxo

Fluxo observado: recall → PriorRun[] (medições) + noise_floor_pct do chamador → summarise_recall → sem piso: só medições ; diferença ≤ piso: 'indistinguishable' ; > piso e duas configs capturadas: 'better' nomeando o piso ; um run: nenhuma comparação.

### Consequências e risco

Regra recusa juízo sem piso válido e preserva medidas. Não verifica se o piso foi medido na escala certa. Inferência estática adicional: identities pode conter duas configs de outros runs; attributable exige fastest conhecido e diferente de slowest, mas não exige slowest conhecido. Se slowest é None, a desigualdade pode permitir crédito a configuração contra baseline sem config capturada. Sem reprodução runtime nesta auditoria.

### Alternativas e recomendação

Preservar a entrega histórica e acompanhar o contrato do piso na #117. Encaminhar separadamente a lacuna estática de atribuição quando o run lento tem configuração desconhecida (proposta N12 da entrega Pod 3), com caso discriminante; não tratar a spec encerrada como ausência de toda oportunidade.

### Dependências e paralelismo

Nenhuma dependência pendente; a unidade é pura e entrou antes da tool, segundo a PR. A normalização de unidade do piso pertence a #117 e é estudo paralelo; nenhuma decisão aqui bloqueia outras frentes.

### Plano e aceite propostos

Preservar entrega histórica e registrar limite do piso informado. Caso discriminante proposto: três runs, fastest comconfigA, intermediário comconfigB e slowest unknown; diferença supera piso, mas não se deve atribuir a comparação fastest/slowest à configuração. Vincular futura decisão de unidade sem executar alterações aqui.

### Comunicação entre responsáveis

Explicar: 'O Apex nunca chama uma configuração de melhor sem um piso medido para aquele plano; dentro do piso diz que não dá para distinguir.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Ordenar por duração e chamar primeiro de melhor confunde medida com causa. Que caso o teste ainda não cobre? Fastest conhecido, outro run comconfig distinta e slowest desconhecido: o conjunto tem duas identidades, mas o par extremo não é experimento capturado. Como eu explicaria isso para outro pod? Piso informado permite julgar diferença; atribuição exige que as configurações relevantes também sejam conhecidas, sem converter ausência em identidade.

### Próxima ação e encerramento

Ação: nenhuma; registrar vínculo com #117 (unidade do piso). Owner a confirmar: Serve+Memory. Entrada: decisão de #117. Saída: referência cruzada. Encerramento: já encerrada; reabrir só se a unidade canônica mudar a entrada da tool.

<a id="item-307"></a>

## T-20260820-plan-memory-read-layer — T-20260820-plan-memory-read-layer.md

Frente: Serve / L6 Learn — memória entre runs (#86). Encaminhamento: encerrada_aceite_antecede_correcao_live.

### Identidade e estado

`tasks/done/T-20260820-plan-memory-read-layer.md` (blob 799d2aa9). 'Read plan similarity and prior outcomes', S, standard, P2; owner `(none)`; sem dependências. Estado `done`; campos de aceite com formato diferente dos carimbados pelo gate: `accepted_by`/`signed_off_by` = e-mail, `accepted_at`/`signed_off_at` = 2026-08-20T00:00:00Z (meia-noite exata) e nenhum `signed_off_sig`; o commit 9a7659c diz 'Specs signed off, accepted'. É diferença observável de formato; não se conclui má-fé nem validade, e nenhuma autorização é inferida. Pod provável: Pod 3/Serve (com dependência de contrato das lanes Verify/Memory).

### Intenção e benefício

Achar formas de plano similares a um run e os runs anteriores dessas formas, com configurações e resultados, calculando similaridade no ClickHouse sobre embeddings já normalizados, sem importar a memory lane e sem assumir largura fixa.

### Feito, faltante e não comprovado

Implementado (39bce47) e corrigido depois do aceite por be0a4d8: `SIMILAR_PLANS_SQL` (`ch.py:260-290`) passou de sub-select escalar (constant-folded pelo ClickHouse, erro 125 para forma nunca vista) para INNER JOIN com chave (encoder_version, dim); `similar_plans()` (918-940) com `MIN_SIMILARITY = 0.80`; `prior_outcomes()` (942+). A classificação de erros que escondia o defeito ('_sanitize routes on the class name') também foi tratada naquele momento e depois reescrita em #140. Testes nomeados nos evals presentes (`test_ch.py:544-660`). B-3 (tabelas ausentes → vazio e log) via `memory_tables_present()`; falha de sonda agora levanta (#140).

### Linhagem

SERVE-LEGS L6 → l6-learn.yaml (approved: true) → specs 5485202 (autor 2026-08-20; commit 2026-09-14) → implementação → 9a7659c 'accept all six units' → be0a4d8 (depois do aceite) corrige dois defeitos achados em ClickHouse real e acrescenta recall_gate → PR #86 integrada em 2026-09-14 (merge 1e0ba80) → #140 reescreve a classificação de erros e a sonda de memória.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260820-plan-memory-read-layer.md; fontes/batch-revalidated-specs58-sources/history/T-20260820-plan-memory-read-layer.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__ch.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_ch.py; fontes/batch-revalidated-specs58-sources/commits/be0a4d8.txt. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: JOIN por encoder_version/dim, FINAL, limite, parâmetros e re-sonda de erro schema_missing; falha de probe não é ausência. Tests de ranking/ordem usam linhas prontas e asserções da SQL. RELATO: correções encontradas em ClickHouse real e gate verde embe0a4d8. Isso não prova todos os casos atuais. Limite adicional: substring(fingerprint,1,64) evita erro de largura, mas transforma valor longo cujo prefixo é válido em outro identificador; B-4 zero para todo hostil não é universal.

### Fluxo

Fluxo observado: plan_fingerprint → SIMILAR_PLANS_SQL (JOIN com a forma consultada; 1 - cosineDistance ≥ 0.80; dim igual) → fingerprints similares → PRIOR_OUTCOMES_SQL → runs com configs e wall clock → summarise_recall ; tabelas ausentes → memory_unavailable.

### Consequências e risco

Defeito histórico do scalar sub-select tem correção presente. Permanecem limites do fake, cache de presença por processo e normalização por truncagem dos fingerprints. Um valor longo com64caracteres válidos de prefixo pode resolver uma forma existente; é inferência do SQL, não incidente observado.

### Alternativas e recomendação

Recomendado: manter encerrada com nota 'aceite em 9a7659c; correção live em be0a4d8'. Alternativa: re-aceite formal no SHA integrado. Padrão que se mostrou necessário: gate live obrigatório para qualquer SQL nova desta lane (FakeClient não analisa SQL).

### Dependências e paralelismo

Nenhuma dependência pendente; é a primeira unidade do L6. Um re-aceite exigiria a ferramenta de gate externa e ClickHouse com DDL v0.3; a nota documental corre em paralelo a tudo.

### Plano e aceite propostos

Condição de não ação no código. Nota documental da ordem aceite→correção. Para reuso: exigir recall_gate (ou equivalente live) para mudanças em SIMILAR_PLANS_SQL/PRIOR_OUTCOMES_SQL, com caso de forma nunca vista como controle negativo.

### Comunicação entre responsáveis

Explicar: 'A leitura de memória entre runs existe desde #86; o primeiro banco real mostrou que a consulta quebrava para formas nunca vistas, e a correção entrou antes do merge.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Assumir largura fixa compara encoders incompatíveis; remover a re-sonda volta a confundir bug deconsulta com tabela ausente. Que caso o teste ainda não cobre? Fingerprint válido de64caracteres seguido de sufixo, truncado para forma existente, em vez de retornar zero conforme promessa ampla de hostilidade. Como eu explicaria isso para outro pod? A consulta respeita encoder/dim e distingue falha de ausência; truncagem evita exceção de tipo, mas precisa de contrato para valores maiores.

### Próxima ação e encerramento

Ação: nota aceite→correção no índice. Owner a confirmar: Serve+Memory. Entrada: be0a4d8 e corpo da #86. Saída: nota. Encerramento: já encerrada; reabrir se a SQL de similaridade mudar sem gate live.

<a id="item-308"></a>

## T-20260820-recall-models — T-20260820-recall-models.md

Frente: Serve / L6 Learn — memória entre runs (#86). Encaminhamento: encerrada_controles_presentes.

### Identidade e estado

`tasks/done/T-20260820-recall-models.md` (blob a4c4c62e). 'Type the recall payload', S, standard, P2; owner `(none)`; sem dependências. Estado `done`; campos de aceite com formato diferente dos carimbados pelo gate: `accepted_by`/`signed_off_by` = e-mail, `accepted_at`/`signed_off_at` = 2026-08-20T00:00:00Z (meia-noite exata) e nenhum `signed_off_sig`; o commit 9a7659c diz 'Specs signed off, accepted'. É diferença observável de formato; não se conclui má-fé nem validade, e nenhuma autorização é inferida. Pod provável: Pod 3/Serve (com dependência de contrato das lanes Verify/Memory).

### Intenção e benefício

Tipar SimilarPlan e PriorRun com similaridade (número entre 0 e 1, nunca booleano), configurações, wall clock e config_source, marcando app_name como não confiável — a afirmação sobre qual configuração funcionou é a mais consequente que este servidor faz.

### Feito, faltante e não comprovado

Implementado (937d63a): `SimilarPlan` (`models.py:697-749`), `PriorRun` (750-827), `RecallResult` (828+). Testes nomeados nos evals presentes e controles extras em `test_recall_view.py`: `config_source` nunca padrão 'observed', 'observed' alegado sem config ainda sinalizado, config ausente é null e não zero, padrão do RecallResult não conclui nada, datetimes do driver aceitos (alteração posterior em fab6620, #129). B-4 (config_source unknown visível) tem teste dedicado.

### Linhagem

SERVE-LEGS L6 → l6-learn.yaml (approved: true) → specs 5485202 (autor 2026-08-20; commit 2026-09-14) → implementação → 9a7659c 'accept all six units' → be0a4d8 (depois do aceite) corrige dois defeitos achados em ClickHouse real e acrescenta recall_gate → PR #86 integrada em 2026-09-14 (merge 1e0ba80) → fab6620 (#129) toca test_recall_view.py.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260820-recall-models.md; fontes/batch-revalidated-specs58-sources/history/T-20260820-recall-models.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__models.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_recall_view.py; fontes/batch-revalidated-specs58-sources/git/serve__VALIDATION.md. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: modelos com limites0..1, origem unknown e configs anuláveis; config_known é observed e não vazio, suficiente com um único campo. Testes cobrem defaults, origem e tipos correntes. A afirmação de que Apex não captura SparkConf é limite histórico da seção L6; recibo06/10 posterior registra job_conf com8chaves. Esta auditoria não quantificou linhas unknown nem demonstrou configuração completa real.

### Fluxo

Fluxo observado: linhas de plan_memory/run_outcomes → SimilarPlan(similarity 0..1) e PriorRun(configs anuláveis, config_source, wall clock) → RecallResult(untrusted_fields com app_name) → cliente.

### Consequências e risco

A camada mantém ausência visível e não assume observed por padrão. Config parcial observed pode ser tratada como conhecida, e a identidade usada no juízo considera somente seis campos tipados; a suficiência disso exige análise no contrato. Não é possível excluir risco nesta camada com os casos presentes.

### Alternativas e recomendação

Recomendado: manter encerrada. Alternativa de produto, separada: alimentar run_outcomes com o job_conf capturado pelo JAR para reduzir 'unknown'. Rejeitado: colapsar similaridade em booleano ou presumir 'observed' — anti-padrões declarados que transformariam palpite em evidência.

### Dependências e paralelismo

Nenhuma dependência pendente. A captura de configuração para run_outcomes é outra frente (contrato, JAR, memory lane), paralela e não bloqueante; nada nesta spec espera por ela.

### Plano e aceite propostos

Condição de não ação: controles presentes cobrem B-1..B-4 e casos extras (observed sem config sinalizado, null ≠ zero). Se a captura de config mudar, rever o teste 'config_source nunca observed por padrão' e acrescentar caso de config parcial.

### Comunicação entre responsáveis

Explicar a outro pod: 'O payload de memória mostra a similaridade como número para você julgar e nunca finge que uma configuração foi observada; quando a origem da configuração é desconhecida, o campo diz isso.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Com config_source padrão 'observed', um palpite semeado viraria evidência de que uma configuração funcionou. Que caso o teste ainda não cobre? — Linhas com config capturada parcialmente (alguns campos sim, outros não) vindas de um job_conf real. Como eu explicaria isso para outro pod? — 'Desconhecido é dito como desconhecido; similaridade é um número para você julgar.'

### Próxima ação e encerramento

Ação: nenhuma. Owner a confirmar: Serve. Entrada: nenhuma nova. Saída: esta ficha como referência. Encerramento: já encerrada; reabrir se o contrato de run_outcomes mudar a origem da configuração.

<a id="item-309"></a>

## T-20260820-recall-runs-tool — T-20260820-recall-runs-tool.md

Frente: Serve / L6 Learn — memória entre runs (#86). Encaminhamento: encerrada_evals_desconectados_controles_reais_em_testes.

### Identidade e estado

`tasks/done/T-20260820-recall-runs-tool.md` (blob 0a6126cd). 'Add recall_similar_runs', XS, standard, P2; owner `(none)`; depends_on plan-memory-read-layer e recall-models. Estado `done`; campos de aceite com formato diferente dos carimbados pelo gate: `accepted_by`/`signed_off_by` = e-mail, `accepted_at`/`signed_off_at` = 2026-08-20T00:00:00Z (meia-noite exata) e nenhum `signed_off_sig`; o commit 9a7659c diz 'Specs signed off, accepted'. É diferença observável de formato; não se conclui má-fé nem validade, e nenhuma autorização é inferida. Pod provável: Pod 3/Serve (com dependência de contrato das lanes Verify/Memory).

### Intenção e benefício

Expor `recall_similar_runs(job_id, top_k)` — a primeira tool que raciocina entre runs — devolvendo runs anteriores da mesma forma de plano com configurações e resultados, dizendo quando a forma nunca foi vista e quando a memória não existe no deployment.

### Feito, faltante e não comprovado

Implementado (d2949f8): tool em `server.py:415-528` (com `noise_floor_pct` opcional). Mapeamento fraco confirmado ({C0417}): eval_1 lista a tool e declara B-2; eval_2 é `! grep 'Five tools'` e declara B-3/B-4. Controles reais em `test_recall_view.py` (c114429): `test_recall_returns_prior_runs_with_similarity_and_wall_clock` (B-2), `test_recall_on_an_unseen_shape_says_so` (B-3), `test_recall_reports_memory_unavailable_on_an_older_deployment` (B-4), além de forma nula e escolha da forma dominante. Prova live relatada: recall_gate (corpo #86).

### Linhagem

SERVE-LEGS L6 → l6-learn.yaml:115 → spec 5485202 → tool d2949f8 → testes de ponta a ponta da tool c114429 → aceite 9a7659c (formato não carimbado) → correções live be0a4d8 e recall_gate → PR #86 (2026-09-14). Elo ausente: mapeamento dos evals para os testes c114429.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260820-recall-runs-tool.md; fontes/batch-revalidated-specs58-sources/history/T-20260820-recall-runs-tool.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__server.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_recall_view.py; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__ch.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: tool distingue memory_unavailable/no_plan_shape/no_prior_runs e constrói exact tier mesmo sem embedding. Testes invocam a tool com fake para estados e prior runs. evals declarados não exercitam B-2..B-4. top_k aplica a vizinhos estruturais; outcomes usam MAX_RECALLED_RUNS separado. RELATO de gate e aceite é histórico, não novo resultado.

### Fluxo

Fluxo observado: recall_similar_runs(job, top_k, piso?) → memory_tables_present? não: memory_unavailable ; forma dominante do job → similar_plans → prior_outcomes → summarise_recall → RecallResult (no_plan_shape | no_prior_runs | runs com medições) ; store fora: levanta (não 'sem runs').

### Consequências e risco

Há controles de chamada e caminho estático consistente. O status dos evals não certifica esses comportamentos. Limites adicionais seguem em summarise_recall e no SQL, como atribuição com configuração parcial/desconhecida e janelas de candidatos; esta folha não os elimina.

### Alternativas e recomendação

Recomendado: manter encerrada; ao reutilizar o plano, apontar eval_1 e eval_2 para os testes de test_recall_view.py. Alternativa: só nota. Rejeitado: devolver a forma mais próxima abaixo do limiar (anti-padrão) ou tratar store fora como 'sem runs'.

### Dependências e paralelismo

Nenhuma dependência pendente (read-layer e models entregues). A correção do plano é documental, paralela e independente de ambiente; re-execução do recall_gate exige ClickHouse com DDL v0.3 autorizado.

### Plano e aceite propostos

Para reuso do plano: eval_1 → test_recall_returns_prior_runs_with_similarity_and_wall_clock; eval_2 → test_recall_on_an_unseen_shape_says_so e test_recall_reports_memory_unavailable_on_an_older_deployment; checagem de processo descrição↔corpo. Esta spec: nota apenas.

### Comunicação entre responsáveis

Explicar: 'recall_similar_runs é testado pela própria tool em três deployments; os evals que fecharam a spec só conferiam registro e um texto.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Devolvendo a forma mais próxima abaixo do limiar, a tool apresentaria runs de outro plano como histórico deste. Que caso o teste ainda não cobre? — Os evals declarados, que não exercitam B-2..B-4; e um store fora durante a sonda de memória, coberto por #140 em outro teste. Como eu explicaria isso para outro pod? — 'Três respostas diferentes: tabela ausente, forma desconhecida e nenhum run anterior; nenhuma delas vira lista vazia silenciosa.'

### Próxima ação e encerramento

Ação: nota de mapeamento. Owner a confirmar: Serve. Entrada: test_recall_view.py. Saída: plano corrigido se reutilizado. Encerramento: já encerrada.

<a id="item-310"></a>

## T-20260820-suggest-fix-provenance — T-20260820-suggest-fix-provenance.md

Frente: Serve / L5 Fix — superfície da verify lane (#87). Encaminhamento: encerrada_com_endurecimentos_posteriores.

### Identidade e estado

`tasks/done/T-20260820-suggest-fix-provenance.md` (blob 71c61045). 'Tell suggest_fix what verify already concluded', S, standard, P2; owner `(none)`; depends_on verify-fix-tool. Estado `done`, aceite gravado pelo gate (`signed_off_sig` hmac-sha256-v2, horários com segundos em 2026-08-20 14:43Z) por `sidymar`, autor da implementação — registro de ferramenta do próprio autor, não revisão independente nem autorização atual. Pod provável: Pod 3/Serve (com dependência de contrato das lanes Verify/Memory).

### Intenção e benefício

Fazer suggest_fix revelar qualquer verificação já existente para o finding — inclusive uma recusa de segurança — sem mudar o que propõe; propor uma correção que o verify recusou é a pior saída possível desta lane.

### Feito, faltante e não comprovado

Implementado (ba79772): a sugestão carrega a verificação, a recusa lidera os avisos e o diff é retido quando verify bloqueou; `applied` continua `Literal[False]` e `requires_human_approval` `Literal[True]`. Testes nomeados nos evals presentes (`test_suggestion_reports_prior_verification`, `test_refused_fix_is_not_presented_as_ready`, `test_unverified_finding_output_is_unchanged`, `test_suggest_fix_safety.py:251-330`) e checagem `git status --porcelain` antes/depois (linhas 117-123, 390-399). Endurecimentos posteriores no mesmo arquivo: 3c889f8 (#135, ocultar deltas de replay não resolvidos) e 82be2e2 (#144, reter vereditos com piso inválido).

### Linhagem

SERVE-LEGS L5 → l5-fix.yaml (approved: true) → specs a8087ce (autor 2026-08-20; commit 2026-09-14) → implementação no mesmo ramo → cd59c8d 'accept and close the six L5 units' → PR #87 integrada em 2026-09-14 (merge 4adb854). Os hashes listados no corpo da PR (f3a314c, 2e13535...) não existem na main: o ramo foi rebaseado antes do merge → #135 e #144 (2026-10-06) ajustam a divulgação de medidas. Elo ausente: prova live com uma linha real de recusa da verify lane.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260820-suggest-fix-provenance.md; fontes/batch-revalidated-specs58-sources/history/T-20260820-suggest-fix-provenance.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__diagnose.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_suggest_fix_safety.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: sugestão busca primeiro row do mesmo finding, divulga notas e retém diff/PR body em recusa; testes de recusa e flags presentes. test_unverified compara chamada sem argumento com chamada verifications=[] na mesma versão atual; não compara versão anterior, portanto não prova B-3 histórico byte a byte. git status compara alterações rastreáveis do tree naquele caso, não todos efeitos externos. Não foi executado.

### Fluxo

Fluxo observado: suggest_fix(job, finding) → receita de diff → ReadStore.verifications(job, finding) → build_verdict → recusa? aviso primeiro e diff retido : predição/medição divulgadas (medição só acima de piso válido) → FixSuggestion(applied=False, requires_human_approval=True).

### Consequências e risco

Literal[False]/[True] restringe o payload e a implementação lida não aplica alterações. Isso não prova por si só ausência de qualquer efeito externo; teste git status observa só o repositório. Recusa depende de row pertinente e ordem de retorno do store. Risco universal não foi excluído.

### Alternativas e recomendação

Recomendado: manter encerrada. Alternativa: bloquear suggest_fix inteiro quando houver qualquer recusa no job — mais conservador, porém mudaria o que é proposto (a spec proíbe). Reversível.

### Dependências e paralelismo

Nenhuma dependência pendente (verify-fix-tool entregue). A prova live com uma linha real de recusa depende de ClickHouse com DDL v0.3 e da verify lane escrevendo a linha; o desenho pode ser feito em paralelo e a execução exige autorização.

### Plano e aceite propostos

Não ação. Controles existentes: retenção do diff em recusa, saída idêntica sem verificação, git status inalterado. Prova live opcional: linha de recusa semeada → suggest_fix sem diff.

### Comunicação entre responsáveis

Explicar: sugestão divulga verificação do finding e esconde diff quando a linha escolhida é uma recusa. Os controles lidos restringem payload e estado do tree no cenário testado; a compatibilidade histórica e a prova live têm escopo separado.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Tratando um bloqueio de segurança como confiança baixa, o diff de uma correção recusada apareceria como 'quase pronto'. Que caso o teste ainda não cobre? — Uma recusa registrada para outro finding do mesmo job que afete a correção proposta. Como eu explicaria isso para outro pod? — 'Bloqueio é recusa de executar, não incerteza; por isso aparece primeiro e esconde o diff.'

### Próxima ação e encerramento

Ação: nenhuma. Owner a confirmar: Serve. Entrada: —. Saída: —. Encerramento: já encerrada; reabrir se o contrato de fix_verifications mudar (#117).

