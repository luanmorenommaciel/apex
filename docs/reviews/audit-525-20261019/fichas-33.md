# Fichas documentais — lote 33

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-321"></a>

## T-20260919-execution-attribution-conflict-collision — T-20260919-execution-attribution-conflict-collision.md

Frente: Engine / atribuição de execução (#115, #126). Encaminhamento: encerrada_teste_discriminante_de_colisao.

### Identidade e estado

`tasks/done/T-20260919-execution-attribution-conflict-collision.md` (blob 75ddb600). 'Make foreign conflict-stage collision observable', XS, standard, P2; owner `(none)`; source_note #115. Estado `done`, aceite gravado pelo gate v3 (`signed_off_sig` hmac-sha256-v3, `accepted_tier: 1`, `accepted_attempt_id`, `acceptance_record_digest`) por `augustosilva`, autor da implementação — registro da ferramenta do próprio autor, não revisão humana independente nem autorização atual. Pod provável: Pod 2/Engine (caminhos engine/; nenhum pod no arquivo).

### Intenção e benefício

Tornar observável a colisão real de stage no conjunto de conflitos: o teste anterior usava um stage estrangeiro ausente do escopo, então não provava que uma linha estrangeira com o mesmo stage_id não entra no conjunto de conflito.

### Feito, faltante e não comprovado

Implementado (6f3f2a0): caso com stage alvo no escopo e mapeamento conflitante estrangeiro no mesmo stage_id, exigindo o conjunto de conflito exato (parte de `test_foreign_scope_collisions_cannot_change_attribution_outcomes`, `test_execution_attribution.py:70-117`). B-2 ('permanece cobertura offline estática') é meta-comportamento, verificado pelo tipo de mudança (só teste), não por eval. Falta: nada no escopo.

### Linhagem

issue #115 (aberta no snapshot) → plano issue115-* (approved: true) → spec autorizada → implementação/teste → done no mesmo dia → PR #126 integrada em 2026-10-06 (merge abed508, head 4ddb082). Commits: c6db7b9 (autorização) → 6f3f2a0 → e09eb66 (done).

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260919-execution-attribution-conflict-collision.md; fontes/batch-revalidated-specs58-sources/history/T-20260919-execution-attribution-conflict-collision.txt; fontes/batch-revalidated-specs58-sources/git/engine__tests__test_execution_attribution.py; fontes/batch-revalidated-specs58-sources/git/engine__src__apex_engine__attribution.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: caso parametrizado usa conflito interno stage3e stage4alvo sem conflito com rowsforeignno4; exige exatamenteconflicting_stage_ids(3,). A lógica do resolvedor filtra escopo antes dos conjuntos. Isso discrimina vazamento por leitura. B2de superfície de mudança é relato do histórico/paths, não prova de runtime ou novo aceite. Nada executado.

### Fluxo

Fluxo observado: escopo com stage alvo + conflito interno ; linha estrangeira com mesmo stage_id e id não-alvo → resolve_stage_ids → conflito com ids exatos do escopo.

### Consequências e risco

Casos reforçam o controle da primitiva e a ausência de atribuição parcial. A revisão não estabelece risco zero nem comportamento do adaptador futuro; teste presente é evidência de cobertura, não resultado aprovado desta rodada.

### Alternativas e recomendação

Recomendado: manter encerrada. Não há alternativa relevante: a mudança é um caso de teste mais forte para o mesmo comportamento. Rejeitado pela spec: alterar código de produção ou semântica de status nesta folha.

### Dependências e paralelismo

Nenhuma dependência técnica; folha só de teste sobre a primitiva entregue. Paralela a todas as frentes, inclusive à decisão de superfície de #115.

### Plano e aceite propostos

Condição de não ação: o caso de colisão é discriminante (a linha estrangeira no mesmo stage_id faria o conjunto de conflito crescer e o teste falhar). Reabrir só se o formato de observação mudar na integração com o store.

### Comunicação entre responsáveis

Explicar: 'Um teste agora coloca a mesma numeração de stage dentro e fora do escopo e prova que o conjunto de conflito não absorve a linha de fora.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Com o stage estrangeiro fora do escopo, como no teste original, o vazamento de conflito não seria observável e poderia passar despercebido. Que caso o teste ainda não cobre? — Colisões com tentativas múltiplas do mesmo stage estrangeiro em ordens diferentes de chegada. Como eu explicaria isso para outro pod? — 'Teste de vazamento só vale se a numeração colide de verdade.'

### Próxima ação e encerramento

Ação: nenhuma. Owner a confirmar: Engine. Entrada: nenhuma nova. Saída: ficha como referência de cobertura de conflito. Encerramento: já encerrada; o caso deve ser preservado quando o adaptador do store for escrito.

<a id="item-322"></a>

## T-20260919-execution-attribution-scope-collision — T-20260919-execution-attribution-scope-collision.md

Frente: Engine / atribuição de execução (#115, #126). Encaminhamento: encerrada_teste_discriminante_de_escopo.

### Identidade e estado

`tasks/done/T-20260919-execution-attribution-scope-collision.md` (blob dec99285). 'Pin attribution scope against realistic stage-ID collisions', S, standard, P2; owner `(none)`; source_note #115. Estado `done`, aceite gravado pelo gate v3 (`signed_off_sig` hmac-sha256-v3, `accepted_tier: 1`, `accepted_attempt_id`, `acceptance_record_digest`) por `augustosilva`, autor da implementação — registro da ferramenta do próprio autor, não revisão humana independente nem autorização atual. Pod provável: Pod 2/Engine (caminhos engine/; nenhum pod no arquivo).

### Intenção e benefício

Reforçar, só com testes, que linhas de app/job estrangeiros reutilizando stage_ids do escopo ou a identidade alvo não alteram absent, not_found, attributed nem conflict — a primeira remediação usava ids que não colidiam.

### Feito, faltante e não comprovado

Caso test_foreign_scope_collisions_cannot_change_attribution_outcomesinclui collisionsattributed/not_found/conflict e escopo vazio comforeignNone(106–112), que deve sernot_found. O teste test_missing_scope_or_other_present_execution_is_not_foundusa escopo vazio/outroID, semrowsforeign. Portanto o suporte exato deB2é a parametrização anterior.

### Linhagem

issue #115 (aberta no snapshot) → plano issue115-* (approved: true) → spec autorizada → implementação/teste → done no mesmo dia → PR #126 integrada em 2026-10-06 (merge abed508, head 4ddb082). Commits: 62b2c4d → 02b9d91 → 0294f21 (done).

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260919-execution-attribution-scope-collision.md; fontes/batch-revalidated-specs58-sources/history/T-20260919-execution-attribution-scope-collision.txt; fontes/batch-revalidated-specs58-sources/git/engine__tests__test_execution_attribution.py; fontes/batch-revalidated-specs58-sources/git/engine__src__apex_engine__attribution.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: mesma numeração/identidadefora do app/job é removida antes da classificação; caso somenteforeignNoneexige not_found. B3não alegar runtime é limite da folha, não comportamento executável. RELATO25passednoheadposterior não foi reproduzido aqui.

### Fluxo

Fluxo observado: escopo + linhas estrangeiras com stage_ids e identidades colidentes → resolve_stage_ids → mesmo resultado que sem as estrangeiras.

### Consequências e risco

Cobertura lida discrimina resultados indevidos em colisões escolhidas. Integração com store e valores do driver não estão demonstrados; nenhum risco universal de produto foi excluído por essa folha só de testes.

### Alternativas e recomendação

Recomendado: manter encerrada. Alternativa não necessária: os casos já colidem ids reais. Rejeitado pela spec: tratar linhas estrangeiras como do escopo para fazer o teste passar.

### Dependências e paralelismo

Nenhuma dependência técnica; folha só de teste sobre a primitiva entregue. Paralela à decisão de superfície de #115 e à prova runtime SQL/RDD, que permanecem separadas e não precisam esperar por ela.

### Plano e aceite propostos

Condição de não ação: controles presentes cobrem as quatro respostas com colisão. Ao integrar com o store, reutilizar os mesmos casos no teste do adaptador para provar que o escopo continua exato com dados do driver.

### Comunicação entre responsáveis

Explicar a outro pod: 'Linhas de outros runs com a mesma numeração de stage, ou até com o mesmo execution_id, não mudam a resposta deste run; só observações do mesmo (app_id, job_id) contam. Testado desde #126.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Tratando 'só linhas de fora com None' como absent, o resolvedor diria que este run não tem identidade quando na verdade não tem observação alguma no escopo. Que caso o teste ainda não cobre? — Ordenação e duplicação vindas do store real, que o teste não reproduz. Como eu explicaria isso para outro pod? — 'Sem observação no escopo é not_found; absent exige observações do escopo sem identidade.'

### Próxima ação e encerramento

Ação: nenhuma. Owner a confirmar: Engine. Entrada: nenhuma nova. Saída: ficha como referência de cobertura de escopo. Encerramento: já encerrada; reutilizar os casos no adaptador futuro de #115.

<a id="item-323"></a>

## T-20260919-pwsh-package-audit-hardening — T-20260919-pwsh-package-audit-hardening.md

Frente: Package / interface e CI PowerShell (#124, #128). Encaminhamento: encerrada_remediacao_de_testes_lacuna_de_invocacao_persiste.

### Identidade e estado

`tasks/done/T-20260919-pwsh-package-audit-hardening.md` (blob d01788e5). 'Harden PowerShell package contract regression coverage', S, standard, P2; owner `(none)`; source_note #124. Estado `done`, aceite gravado pelo gate v3 (`signed_off_sig` hmac-sha256-v3, `accepted_tier: 1`, `accepted_attempt_id`, `acceptance_record_digest`) por `augustosilva`, autor da implementação — registro da ferramenta do próprio autor, não revisão humana independente nem autorização atual. Pod provável: Pod 2/Package (scripts/, tests/ raiz e CI). Do-Not-Touch inclui `scripts/apex.ps1` e `ci.yml` (só testes).

### Intenção e benefício

Fazer os testes provarem identidade exata da ação no DryRun (resumo completo, não substring), comportamento seguro de help e ValidateSet sem criar estado, e ausência do diretório `.apex` — após uma revisão apontar que um handler errado com prefixo igual passava.

### Feito, faltante e não comprovado

Implementado (767d555): comparação do resumo completo `APEX_DRY_RUN=passed action=... handler=... mutations=0 external_calls=0` (`test_apex_initial_package.py:59-72`), `test_help_dispatches_to_safe_handler_without_runtime_state`, `test_invalid_action_is_rejected_by_validateset_without_runtime_state`, `test_representative_dry_runs_leave_runtime_directory_unchanged` (74-120). Continua não coberto (fora do escopo desta spec, que proíbe tocar apex.ps1): a invocação real de cada `Command`.

### Linhagem

#124 → plano issue124-audit-remediation.yaml (approved: true) → ca3fa7d (autorização) → 767d555 (testes) → 7d3266d (done) → PR #128 integrada em 2026-10-06 (merge d8c1a3c). Elo ausente: a revisão independente citada no 'Why' não está anexada.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260919-pwsh-package-audit-hardening.md; fontes/batch-revalidated-specs58-sources/history/T-20260919-pwsh-package-audit-hardening.txt; fontes/batch-revalidated-specs58-sources/git/tests__test_apex_initial_package.py; fontes/batch-revalidated-specs58-sources/git/scripts__apex.ps1. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: resumo é linha inteira; help/invalid usam chamada sem DryRun. _runtime_snapshot registra existência, caminhos/tipos e SHA256 do conteúdo dos arquivos (36–52); testes comparam antes/depois em74–119. Retirada a conclusão anterior incorreta de ausência de hashes. Se .apex já existir, igualdade verifica preservação do conteúdo final observado, sem provar ausência do diretório. Nada executado.

### Fluxo

Fluxo observado: pytest → subprocess pwsh apex.ps1 <ação> -DryRun → stdout com resumo → igualdade de linha ; snapshot de `.apex` antes/depois ; help sem DryRun → Show-Help ; ação inválida → erro de ValidateSet.

### Consequências e risco

Controle de rótulo e snapshots com hash estão presentes. O snapshot detecta mudança persistente de bytes dos arquivos em .apex; não observa efeitos transitórios, caminhos externos nem serviços. A lacuna de invocação de Command é separada e já pertence à#124. Nenhum defeito runtime foi reproduzido.

### Alternativas e recomendação

Recomendado: manter encerrada; o próximo controle é de invocação (stubs por função) em #124, não mais asserções de DryRun. Alternativa: derivar o Handler do próprio scriptblock para eliminar a dupla fonte. Rejeitado pela spec: alterar apex.ps1 ou o CI nesta folha.

### Dependências e paralelismo

Nenhuma dependência técnica para permanecer encerrada. O controle de invocação em #124 depende só de pwsh no ambiente de teste e pode correr em paralelo a #123 e #167/#174.

### Plano e aceite propostos

Condição de não ação nesta folha: os quatro testes acrescentados discriminam prefixo errado, help, ação inválida e criação de `.apex`. O controle que falta (invocação real) foi descrito na ficha de pwsh-command-aware-coverage e pertence a #124.

### Comunicação entre responsáveis

Explicar: 'Os testes de DryRun agora comparam a linha inteira e verificam help, ação inválida e o diretório .apex; ainda não provam que a ação real chama o código certo.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Comparando só substring do handler, 'Invoke-ProductGate' aceitaria 'Invoke-ProductGate-Full' para a ação errada. Que caso o teste ainda não cobre? — A execução real de cada Command, que o DryRun pula por desenho. Como eu explicaria isso para outro pod? — 'Agora o rótulo é exato; a chamada ainda precisa de outra prova.'

### Próxima ação e encerramento

Ação: nenhuma aqui; seguir o controle de invocação em #124. Owner a confirmar: Package (Pod 2). Entrada: C04-12 e apex.ps1:730-800. Saída: referência cruzada. Encerramento: já encerrada; #124 fecha com o controle de invocação ou revisão explícita de escopo.

<a id="item-324"></a>

## T-20260919-tail-outlier-contract-audit-hardening — T-20260919-tail-outlier-contract-audit-hardening.md

Frente: Engine / contrato e watcher de cauda (#123, #127). Encaminhamento: encerrada_fail_closed_numerico_presente.

### Identidade e estado

`tasks/done/T-20260919-tail-outlier-contract-audit-hardening.md` (blob 23009bba). 'Harden tail-outlier contract rejection boundaries', M, standard, P2; owner `(none)`; source_note #123. Estado `done`, aceite gravado pelo gate v3 (hmac-sha256-v3, tier 1, attempt_id, record_digest) por `augustosilva`, autor da implementação — registro da ferramenta do próprio autor, não revisão humana independente nem autorização atual. Pod provável: Pod 2/Engine (caminhos engine/; nenhum pod no arquivo). Plano issue123-audit-remediation.yaml (unidade 1 de 3).

### Intenção e benefício

Fazer a rejeição numérica do contrato falhar fechada para valores irrepresentáveis (inteiro enorme que levantava OverflowError), bool, string, NaN e infinito, e pinar os limites inclusivos/estritos e o isolamento do skew.

### Feito, faltante e não comprovado

Código presente: _finite_number captura OverflowError/TypeError/ValueError (validation.py:115–122); _tail_outlier_issues aplica cinco limiares (94–111). Testes de fronteira, inclusividade, seis classes de inválidos por campo e isolamento do skew estão em test_contract_engine.py:355–470. O nome _is_finite_number da ficha anterior não existe nesta base.

### Linhagem

issue #123 (aberta no snapshot) → plano issue123-* (approved: true) → spec autorizada → implementação → done → PR #127 integrada em 2026-10-06 (merge fec8a7f, head 4e44bfd). Origem: 'Independent review found ...' (não anexada). Commits: fe40eb8 → 5cec1f2 → 8ee67a7.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260919-tail-outlier-contract-audit-hardening.md; fontes/batch-revalidated-specs58-sources/history/T-20260919-tail-outlier-contract-audit-hardening.txt; fontes/batch-revalidated-specs58-sources/git/engine__src__apex_engine__validation.py; fontes/batch-revalidated-specs58-sources/git/engine__tests__test_contract_engine.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: bool/texto/não finitos e 10**400 têm rejeição determinística definida nos testes; limites de contagem >=100, medidas >0 e ratio>10. A combinação aceita no teste tem max/p50=10 e tail_ratio=10.1: o controle aceita limiares independentes, sem derivar ratio. Nada executado.

### Fluxo

Fluxo observado: details[campo] → _is_finite_number (rejeita bool, NaN, inf, overflow) → limites (≥100, >0, >10) → lista de issues determinística ; tipos de skew → _skew_issues sem atalho pela cauda.

### Consequências e risco

O controle protege conversão dos tipos Python int/float considerados e o desvio indevido de skew para tail. Não exclui defeitos com objetos arbitrários nem inconsistência entre medidas. Consequência documental: não promover controle de fronteira a prova integral da verdade da evidência.

### Alternativas e recomendação

Recomendado: manter encerrada. Alternativa sem ganho claro: validar via modelo Pydantic com tipos estritos — mudaria o formato das mensagens que outros consumidores podem ler. Rejeitado pela spec: mudar tipo, limiares ou persistência nesta folha.

### Dependências e paralelismo

Nenhuma dependência técnica pendente; watcher-audit-hardening depende desta e está entregue. Paralela a #123 (garantia do gate) e a #124 (PowerShell); nenhuma dessas frentes precisa esperar por ela.

### Plano e aceite propostos

Manter encerrada dentro do escopo de fronteiras por campo. A eventual exigência de coerência tail_ratio=max/p50 ou de contagens inteiras precisa de decisão de contrato própria em #123; não é demonstrada por estes testes.

### Comunicação entre responsáveis

Explicar: para os valores inválidos enumerados, o validador tem controles de rejeição por campo e preserva as regras do skew. Os testes foram lidos; coerência entre as medições e runtime ficam fora desta prova.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Um OverflowError não tratado interromperia a validação do valor enorme em vez de produzir a issue. Que caso o teste ainda não cobre? — Coerência entre tail_ratio e max/p50; o próprio caso aceito usa 10.1 contra uma razão de 10. Como eu explicaria isso para outro pod? — Os limiares por campo estão protegidos, e a relação entre campos exige contrato explícito.

### Próxima ação e encerramento

Ação: nenhuma. Owner a confirmar: Engine. Entrada: nenhuma nova. Saída: ficha como referência das fronteiras numéricas. Encerramento: já encerrada; reabrir com campo numérico novo no contrato.

<a id="item-325"></a>

## T-20260919-tail-outlier-watcher-audit-hardening — T-20260919-tail-outlier-watcher-audit-hardening.md

Frente: Engine / contrato e watcher de cauda (#123, #127). Encaminhamento: encerrada_contrato_emitido_pinado.

### Identidade e estado

`tasks/done/T-20260919-tail-outlier-watcher-audit-hardening.md` (blob b2b2af8d). 'Harden emitted tail-outlier watcher contract coverage', M, standard, P2; owner `(none)`; depends_on contract-audit-hardening. Estado `done`, aceite gravado pelo gate v3 (hmac-sha256-v3, tier 1, attempt_id, record_digest) por `augustosilva`, autor da implementação — registro da ferramenta do próprio autor, não revisão humana independente nem autorização atual. Pod provável: Pod 2/Engine (caminhos engine/; nenhum pod no arquivo).

### Intenção e benefício

Pinar por teste o finding realmente emitido pelo watcher (tipo, severidade WARNING, confiança MEDIUM, detector, detalhes) e passá-lo pelo validador; corrigir comentários obsoletos de contagem de watchers sem mudar detecção.

### Feito, faltante e não comprovado

test_tail_outlier_prefers_retry_safe_population fixa tipo, WARNING, MEDIUM, detector e dicionário inteiro de details, depois chama validate_finding (test_watchers.py:140–172). STAGE_WATCHERS tem sete membros e WATCHER_NAMES acrescenta AQE (__init__.py:26–28). Fallback legado é outro teste (175–185), sem chamada ao validador.

### Linhagem

issue #123 (aberta no snapshot) → plano issue123-* (approved: true) → spec autorizada → implementação → done → PR #127 integrada em 2026-10-06 (merge fec8a7f, head 4e44bfd). Commits: fe40eb8 → a2ce0cc → 0338b21.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260919-tail-outlier-watcher-audit-hardening.md; fontes/batch-revalidated-specs58-sources/history/T-20260919-tail-outlier-watcher-audit-hardening.txt; fontes/batch-revalidated-specs58-sources/git/engine__tests__test_watchers.py; fontes/batch-revalidated-specs58-sources/git/engine__src__apex_engine__watchers____init__.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: controle de contrato sobre uma emissão retry-safe e comentários coerentes com a tupla de stage; AQE é adicional. A revisão independente citada no Why é relato não anexado. Leitura corrobora a intenção B1–B3, sem executar testes nem provar que comentários históricos eram os únicos obsoletos.

### Fluxo

Fluxo observado: StageAggregate qualificado (população retry-safe) → tail_outlier.evaluate → Finding emitido → validate_finding (mesmo contrato do consumidor) → accepted=True; registro de watchers documentado como sete, igual à tupla STAGE_WATCHERS.

### Consequências e risco

Há controle discriminante contra deriva do payload escolhido; isso não exclui deriva nos demais ramos. A emissão legacy_all_attempts não tem a mesma ida e volta pelo validador neste teste. Nenhum defeito runtime reproduzido.

### Alternativas e recomendação

Recomendado: manter encerrada. Alternativa útil e pequena: repetir a ida e volta watcher→validador também para o fallback legado. Rejeitado pela spec: mudar o comportamento de detecção do watcher nesta folha.

### Dependências e paralelismo

Nenhuma dependência pendente (contract-audit-hardening entregue). Paralela a #123 e a qualquer outra frente; o teste opcional do fallback legado não exige ambiente nem decisão.

### Plano e aceite propostos

Condição de não ação: o controle de ida e volta existe. Melhoria opcional: o mesmo teste para a fonte legado_all_attempts, garantindo que o finding com fallback também passa no validador.

### Comunicação entre responsáveis

Explicar: um finding produzido com amostras de tarefas bem-sucedidas é confrontado com identidade, detalhes exatos e o validador. A garantia documental se limita ao caso lido.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Testando watcher e validador separadamente, um campo renomeado em um lado não seria notado até a persistência. Que caso o teste ainda não cobre? — O fallback legado passando pelo validador (o teste de ida e volta usa a população retry-safe). Como eu explicaria isso para outro pod? — 'O que o Engine emite é validado pelo mesmo contrato que o consumidor usa.'

### Próxima ação e encerramento

Ação: nenhuma; melhoria opcional registrada (fallback legado). Owner a confirmar: Engine. Entrada: test_watchers.py:140-175. Saída: teste extra opcional. Encerramento: já encerrada.

<a id="item-326"></a>

## T-20260919-tail-outlier-wiring-audit-hardening — T-20260919-tail-outlier-wiring-audit-hardening.md

Frente: Package / roteamento tail-outlier (#123, #127). Encaminhamento: encerrada_testes_estruturais_mais_fortes_sem_execucao.

### Identidade e estado

`tasks/done/T-20260919-tail-outlier-wiring-audit-hardening.md` (blob d0f0f503). 'Harden tail-outlier package fail-closed regression coverage', S, standard, P2; owner `(none)`; source_note #123. Estado `done`, aceite gravado pelo gate v3 (hmac-sha256-v3, tier 1, attempt_id, record_digest) por `augustosilva`, autor da implementação — registro da ferramenta do próprio autor, não revisão humana independente nem autorização atual. Pod provável: Pod 2/Package+DEV (scripts/, dev/scripts, tests/ raiz). Do-Not-Touch implícito: não muda o gate PowerShell de produção.

### Intenção e benefício

Fazer os testes estáticos provarem cada guarda fail-closed do gate como condição seguida do próprio throw (job ausente, exit não-zero, watcher ausente), porque os testes anteriores passavam mesmo removendo a condição.

### Feito, faltante e não comprovado

Implementado (c0af6d9): `test_public_gate_remains_fail_closed_and_llm_free` (`test_tail_outlier_package.py:50-80`) verifica a mensagem de throw dentro do bloco da guarda, a ordem atribuição→condição, a presença de `--no-crew` e a posição do marcador passed. Continua estrutural: lê o texto de `apex.ps1`, não executa o gate; não verifica associação ao stage nem mede LLM (B-3 declara exatamente esse limite).

### Linhagem

issue #123 (aberta no snapshot) → plano issue123-* (approved: true) → spec autorizada → implementação → done → PR #127 integrada em 2026-10-06 (merge fec8a7f, head 4e44bfd). Commits: fe40eb8 → c0af6d9 → 96c3b4f.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260919-tail-outlier-wiring-audit-hardening.md; fontes/batch-revalidated-specs58-sources/history/T-20260919-tail-outlier-wiring-audit-hardening.txt; fontes/batch-revalidated-specs58-sources/git/tests__test_tail_outlier_package.py; fontes/batch-revalidated-specs58-sources/git/scripts__apex.ps1. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: _if_block procura a condição literal e recorta até a primeira linha com fechamento indentado (24–27); testes exigem throw e ordem textual (53–78). Não há parser de PowerShell nem execução. Assim há controle contra remoção das strings exigidas, sem prova geral da semântica do bloco.

### Fluxo

Fluxo observado: pytest → lê scripts/apex.ps1 → isola o corpo de Invoke-TailOutlierGate → verifica que cada throw fica no bloco da própria condição, a ordem atribuição→condição, a presença de --no-crew e que o marcador passed vem depois das guardas.

### Consequências e risco

As condições exigem as variáveis literais corretas, portanto trocar só a variável falharia na asserção. Persistem possíveis falsos verdes se as strings ficarem em comentários ou código não executado. --no-crew e llm_calls=0 são texto/argumento verificados, sem contador observado.

### Alternativas e recomendação

Recomendado: manter encerrada; o próximo passo útil é executar o gate com runner e Engine falsos (em #123). Alternativa: parse AST do PowerShell em vez de texto — mais robusto, mais custo. Rejeitado pela spec: mudar o gate de produção nesta folha.

### Dependências e paralelismo

Nenhuma dependência técnica; folha só de teste. Paralela a #124, que tem a mesma classe de lacuna (estrutura verificada, execução não), e às decisões de garantia de #123.

### Plano e aceite propostos

Condição de não ação nesta folha: as asserções estruturais já discriminam remoção de condição. Em #123: teste que execute o gate com stubs para job ausente, exit não-zero e saída sem watcher, verificando o throw real.

### Comunicação entre responsáveis

Explicar: os testes fixam as três condições e mensagens no texto do gate. Um trecho comentado ou não executado ainda pode satisfazer essa inspeção; execução com stubs seria outra prova.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Buscar só a mensagem deixaria a remoção da condição passar na inspeção. Que caso o teste ainda não cobre? — Condições e throws exigidos preservados em comentários ou em fluxo não executado. Como eu explicaria isso para outro pod? — A proteção é textual e exata; a semântica precisa de outra prova.

### Próxima ação e encerramento

Ação: nenhuma aqui; vincular o teste de execução do gate a #123. Owner a confirmar: Package (Pod 2). Entrada: C04-11 e apex.ps1:677-711. Saída: referência cruzada. Encerramento: já encerrada.

<a id="item-327"></a>

## T-20260920-api-diagnostic-routes — T-20260920-api-diagnostic-routes.md

Frente: Serve+Front / API HTTP e adaptação da Console (#129). Encaminhamento: encerrada_controle_de_paridade_tool_rota_presente.

### Identidade e estado

`tasks/done/T-20260920-api-diagnostic-routes.md` (blob fb5f35fb). 'Expose the eight MCP tools as /v1 diagnostic routes', M, standard, P2; owner `(none)`; depends_on api-skeleton. Estado `done`; aceite gravado pelo gate (hmac-sha256-v2, segundos) por `sidymar` no próprio commit de implementação em 2026-09-20/21; a transição para `done` foi feita por outra pessoa (agmarcastro) em 9841119 (2026-09-29, PR #153). Registro da ferramenta do autor, não revisão independente nem autorização atual. Pods prováveis: Pod 3/Serve e Pod 1/Front (nenhum pod no arquivo).

### Intenção e benefício

Expor as oito tools MCP como rotas /v1 que despacham por `create_server(store).call_tool()`, com teste que falha se tools e rotas divergirem — para que Console e editor não tenham duas respostas para a mesma pergunta.

### Feito, faltante e não comprovado

TOOL_ROUTES é dict manual com oito nomes (diagnostics.py:53–62); handlers usam seus caminhos e chamam _call→call_tool (98–118,121–224). Testes comparam nomes da tabela com list_tools nos dois sentidos e unicidade de paths (54–71), depois exigem cada par método/path no schema (77–84). Não há igualdade entre todos endpoints servidos e tabela. O caso de diagnóstico compara JSON e presença de três campos (90–102), sem validação explícita do modelo. Casos de piso HTTP estão em 147–205.

### Linhagem

decisão do Weekly Sync de 15/09 (relato do corpo da #129; nota de reunião citada em source_note não está no repositório) → serve-api.yaml (approved: true; o PyYAML rejeita o arquivo na linha 20, Codex C04-06) → spec 7fb0879 (2026-09-20) → implementação com accepted:true → done em 9841119 (#153) → PR #129 integrada em 2026-10-06 (merge 83a9624) → 8233763 (#143).

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260920-api-diagnostic-routes.md; fontes/batch-revalidated-specs58-sources/history/T-20260920-api-diagnostic-routes.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_api__routes__diagnostics.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_api_diagnostics.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: nomes da tabela são confrontados com a lista do servidor; tabela não é gerada pela lista. Rotas declaradas precisam estar servidas, mas rota adicional fora da tabela não é rejeitada por esse laço. Sugestão checa applied/approval e método, sem observador de escrita. Erro contém controles negativos de DSN/traceback para o caso simulado. Nenhum teste executado.

### Fluxo

Fluxo observado: GET/POST /v1/runs/{job}/diagnosis etc. → auth → diagnostics router → create_server(store).call_tool(nome, args) → resultado tupla|dict normalizado → modelo da tool → JSON ; ApexStoreError → envelope sanitizado.

### Consequências e risco

Controles cobrem deriva de nomes da tabela e ausência de endpoint declarado; não comprovam ausência de endpoint extra nem fidelidade de todos argumentos e payloads. Asserções de applied=false não equivalem a provar zero escrita. Divergência de unidade é limite já registrado em #117.

### Alternativas e recomendação

Recomendado: manter encerrada e usar este padrão (lista derivada de list_tools) como modelo para reconciliar o gate stdio. Alternativa rejeitada pela PR: chamar diagnose.analyze direto (duas respostas).

### Dependências e paralelismo

Nenhuma dependência pendente (api-skeleton entregue). A normalização de unidade do piso fica com #117 e é estudo paralelo; a reconciliação do gate stdio pode reutilizar o padrão desta folha sem esperar nada.

### Plano e aceite propostos

Manter a folha encerrada como adaptador e referência de confronto com list_tools. Se exigir paridade exata de toda superfície diagnóstica, comparar o conjunto real de operações desse router nos dois sentidos e verificar despacho/argumentos por rota. Não derivar EXPECTED_TOOLS automaticamente sem um contrato permitido independente.

### Comunicação entre responsáveis

Explicar: oito entradas manuais encaminham para as mesmas tools; testes confrontam seus nomes com list_tools e verificam que os caminhos declarados aparecem no schema. Esse controle precisa de complemento para excluir rotas extras.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Reimplementar a análise permitiria respostas divergentes entre transportes. Que caso o teste ainda não cobre? — Endpoint diagnóstico acrescentado fora de TOOL_ROUTES: o laço de presença não rejeita extras servidos. Como eu explicaria isso para outro pod? — A tabela é manual e conferida contra as tools; a igualdade completa da superfície ainda não é provada.

### Próxima ação e encerramento

Ação: nenhuma; citar como padrão no item do gate stdio. Owner a confirmar: Serve. Entrada: —. Saída: referência. Encerramento: já encerrada.

<a id="item-328"></a>

## T-20260920-api-openapi-auth — T-20260920-api-openapi-auth.md

Frente: Serve+Front / API HTTP e adaptação da Console (#129). Encaminhamento: encerrada_exposicao_dos_docs_em_decisao_171.

### Identidade e estado

`tasks/done/T-20260920-api-openapi-auth.md` (blob 9f9a6020). 'Say in the OpenAPI schema that /v1 needs a token', S, standard, P2; owner `(none)`; depends_on api-resource-routes. Estado `done`; aceite gravado pelo gate (hmac-sha256-v2, segundos) por `sidymar` no próprio commit de implementação em 2026-09-20/21; a transição para `done` foi feita por outra pessoa (agmarcastro) em 9841119 (2026-09-29, PR #153). Registro da ferramenta do autor, não revisão independente nem autorização atual. Pods prováveis: Pod 3/Serve e Pod 1/Front (nenhum pod no arquivo). Criada ao trocar a folha 'mcp-store-selection' (8d6c9ea, 'drop mcp-store-selection, add api-openapi-auth').

### Intenção e benefício

Fazer o schema OpenAPI declarar o esquema bearer e exigi-lo em toda operação /v1 exceto health, mantendo /docs, /redoc e /openapi.json acessíveis sem token — a autenticação é middleware e o schema não dizia nada.

### Feito, faltante e não comprovado

_document_auth publica scheme http/bearer e aplica security às operações cujo path começa com /v1, exceto PUBLIC_PATHS (app.py:46–78); create_app instala middleware (126) e documentação após routers (177–181). Testes de schema e acessibilidade estão em test_api_openapi.py:20–56. O locador app.py:150–207 da ficha anterior não contém o núcleo da alteração nesta base.

### Linhagem

Histórico lido: 8d6c9ea substituiu mcp-store-selection por api-openapi-auth e 668f59f implementou a documentação; 9841119 encerrou as folhas anteriormente aceitas. A origem no sync/PR é relato herdado, sem nota de reunião relida aqui; a spec desta folha não nasceu no commit 7fb0879 do plano inicial. #171 é destino já registrado para a política de docs/token, sem consulta atual.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260920-api-openapi-auth.md; fontes/batch-revalidated-specs58-sources/history/T-20260920-api-openapi-auth.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_api__app.py; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_api__auth.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_api_openapi.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: scheme e security por operação são comparados nos testes; docs/redoc/schema retornam 200 e /v1/runs sem token espera 401. Os testes não inspecionam todas respostas de docs por ausência de dados. O middleware autoriza antes de call_next (auth.py:71–87). Nenhuma execução.

### Fluxo

Fluxo observado: GET /openapi.json (sem token) → schema com securitySchemes.bearer e security por operação /v1 (menos health) → Swagger com botão Authorize ; GET /v1/... sem token → middleware → 401.

### Consequências e risco

A documentação corresponde à política expressa, com docs anônimos. Não é prova de segurança global nem de ratificação humana por perfil. A escolha de exposição e custódia do token continua em #171 no snapshot; nenhum defeito de runtime foi reproduzido.

### Alternativas e recomendação

Recomendado: manter encerrada; ratificar ou reverter B-4 na #171 por perfil (local vs compartilhado). Alternativa: docs atrás do token em perfil compartilhado.

### Dependências e paralelismo

Nenhuma dependência técnica pendente (api-resource-routes entregue). A ratificação de B-4 (docs públicos) é decisão humana na #171, por perfil de implantação, e corre em paralelo.

### Plano e aceite propostos

Condição de não ação no código enquanto a #171 não decidir. Se decidir esconder docs em perfil compartilhado: spec nova com teste invertido (docs exigem token nesse perfil) e controle negativo (perfil local continua público, se assim decidido).

### Comunicação entre responsáveis

Explicar: 'O schema agora diz que /v1 exige token; os docs ficam públicos por escolha desta spec, e a #171 decide se isso vale para todo perfil.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Declarando a exigência por dependência de rota, a admissão passaria para depois do roteamento e reabriria o oráculo de rotas. Que caso o teste ainda não cobre? — Um perfil de implantação compartilhado em que docs públicos não sejam aceitáveis. Como eu explicaria isso para outro pod? — 'O schema descreve a regra; quem a aplica é o middleware. Se os docs devem ser públicos é decisão de política.'

### Próxima ação e encerramento

Ação: vincular B-4 a #171. Owner a confirmar: Serve + mantenedor. Entrada: #171. Saída: decisão por perfil. Encerramento: esta spec já encerrada.

<a id="item-329"></a>

## T-20260920-api-resource-routes — T-20260920-api-resource-routes.md

Frente: Serve+Front / API HTTP e adaptação da Console (#129). Encaminhamento: encerrada_b2_aceito_com_controle_fraco_corrigido_depois.

### Identidade e estado

`tasks/done/T-20260920-api-resource-routes.md` (blob 2f6d36bb). "Serve the console's row-level data over /v1", M, standard, P2; owner `(none)`; depends_on api-skeleton e readstore-console-queries. Estado `done`; aceite gravado pelo gate (hmac-sha256-v2, segundos) por `sidymar` no próprio commit de implementação em 2026-09-20/21; a transição para `done` foi feita por outra pessoa (agmarcastro) em 9841119 (2026-09-29, PR #153). Registro da ferramenta do autor, não revisão independente nem autorização atual. Pods prováveis: Pod 3/Serve e Pod 1/Front (nenhum pod no arquivo). Escopo ampliado antes da implementação (bb43291) para carregar dois portes esquecidos (RUN_LIST, FIX_VERIFICATIONS).

### Intenção e benefício

Servir os onze métodos de dados de Repository (kind é propriedade) com formatos compatíveis, 404 para run desconhecido, ausência de memória reportada e sinalização de listas no limite. A spec conserva contagem doze no Goal/B1, mas o Context e a interface têm onze métodos.

### Feito, faltante e não comprovado

RESOURCE_ROUTES enumera onze entradas (resources.py:39–51), cada uma usa store apropriado e wire quando necessário. Testes originais de formato usam subconjunto de campos (test_api_resources.py:84–110); os específicos de stages/findings/transitions estão em158–208. CONSOLE_PROJECTIONS compara nomes SQL de oito interfaces (225–280): exclui SparkEventRow e RUN_LIST, com três campos do FixVerificationRow delegados ao mapper. Não é prova integral de todos campos/tipos/valores das respostas.

### Linhagem

decisão do Weekly Sync de 15/09 (relato do corpo da #129; nota de reunião citada em source_note não está no repositório) → serve-api.yaml (approved: true; o PyYAML rejeita o arquivo na linha 20, Codex C04-06) → spec 7fb0879 (2026-09-20) → implementação com accepted:true → done em 9841119 (#153) → PR #129 integrada em 2026-10-06 (merge 83a9624). Correções posteriores: c71c2e4 (stages), fab6620 (findings/transitions), 993eaa7 (paridade por campo).

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260920-api-resource-routes.md; fontes/batch-revalidated-specs58-sources/history/T-20260920-api-resource-routes.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_api__routes__resources.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_api_resources.py; fontes/batch-revalidated-specs58-sources/git/front__src__data__repository.ts; fontes/batch-revalidated-specs58-sources/git/front__src__contract__types.ts. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: igualdade métodos TS↔chaves da tabela e presença dos endpoints no schema; 404/ausência/truncagem têm casos fake. _report_truncation sinaliza len>=cap, portanto página exatamente no cap é tratada conservadoramente como truncada. Teste de limite checa headers, sem assert de tamanho ou execução SQL. Sequência histórica de defeitos/correções vem de relatos preservados; nesta leitura não foram reexecutados commits passados.

### Fluxo

Fluxo observado: HttpRepository.<método> → /v1/<rota> → resources router → ReadStore.console_* / run / run_list / fix_verification → wire() → linha no formato de types.ts ; job desconhecido → 404 ; memória ausente → memory_unavailable ; listas → truncamento reportado.

### Consequências e risco

Projeções específicas e controles presentes reduzem deriva, mas não autorizam nenhum risco atual nem B2 garantido integralmente. O teste SQL compara nomes, não tipos/valores, e não cobre diretamente o tipo composto SparkEventRow nem RUN_LIST. Runtime e navegador permanecem não verificados nesta revisão.

### Alternativas e recomendação

Recomendado: manter encerrada com nota de que B-2 foi realmente garantido só a partir de 993eaa7. Alternativa: re-aceite sobre o SHA integrado.

### Dependências e paralelismo

Nenhuma dependência pendente (skeleton e portes entregues). A prova em navegador real (#172) e a decisão de token (#171) são frentes paralelas e não bloqueiam o encerramento documental.

### Plano e aceite propostos

Manter encerrada com limite explícito: o controle desde993eaa7 verifica nomes de oito projeções listadas, além dos testes específicos presentes. Reuso do plano deve distinguir nome de coluna, valor/tipo/ordem e paridade live; não chamar B2 inteiro de garantido por uma única asserção.

### Comunicação entre responsáveis

Explicar: onze rotas de dados estão ligadas ao Repository. Os testes por campo reforçam oito projeções SQL e casos específicos de três rotas, sem provar todos os valores ou tipos contra o banco.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Mapeando método da Console para método do ReadStore pelo nome, a rota serviria a projeção do MCP e telas mostrariam NaN ou ordem errada. Que caso o teste ainda não cobre? — Valores e ordem das linhas contra um store real; o teste por campo checa nomes projetados, e a paridade de valores é do gate live. Como eu explicaria isso para outro pod? — 'Mesmo nome de método não quer dizer mesma projeção; compare os campos.'

### Próxima ação e encerramento

Ação: nota da sequência de correções (c71c2e4, fab6620, 993eaa7). Owner a confirmar: Serve. Entrada: commits citados e spec de projeção de findings/transitions. Saída: nota no índice. Encerramento: já encerrada.

<a id="item-330"></a>

## T-20260920-api-skeleton — T-20260920-api-skeleton.md

Frente: Serve+Front / API HTTP e adaptação da Console (#129). Encaminhamento: encerrada_controles_presentes_decisao_de_token_em_171.

### Identidade e estado

`tasks/done/T-20260920-api-skeleton.md` (blob b31bfb50). 'Stand up the apex-api FastAPI application', M, standard, P2; owner `(none)`; sem dependências; source_note aponta `brain/01-projects/apex/08-meetings/krisp/2026-09-15-weekly-sync-crew-a-apex.md` (fora do repositório, não verificável aqui). Estado `done`; aceite gravado pelo gate (hmac-sha256-v2, segundos) por `sidymar` no próprio commit de implementação em 2026-09-20/21; a transição para `done` foi feita por outra pessoa (agmarcastro) em 9841119 (2026-09-29, PR #153). Registro da ferramenta do autor, não revisão independente nem autorização atual. Pods prováveis: Pod 3/Serve e Pod 1/Front (nenhum pod no arquivo).

### Intenção e benefício

Tirar o navegador da conexão direta ao ClickHouse (a credencial `apex_ro` vai a todo visitante) criando um serviço: app FastAPI com ReadStore injetável, `/v1/health`, autenticação por bearer, envelope de erro que não vaza DSN e registro automático de routers.

### Feito, faltante e não comprovado

create_app injeta store/settings, instala middleware e descobre routers (app.py:99–181); load_settings recusa conjunto vazio vindo do ambiente (config.py:43–60). auth.py:49–63 compara todas entradas sem retorno antecipado ao casar token. Testes de health/injeção/erro/descoberta/auth e scanner estão em test_api_app.py:72–219. O scanner não encontra toda forma possível de segredo: inspeciona atribuições de constantes string a nomes simples com palavras suspeitas, ignorando valores em maiúsculas.

### Linhagem

decisão do Weekly Sync de 15/09 (relato do corpo da #129; nota de reunião citada em source_note não está no repositório) → serve-api.yaml (approved: true; o PyYAML rejeita o arquivo na linha 20, Codex C04-06) → spec 7fb0879 (2026-09-20) → implementação com accepted:true → done em 9841119 (#153) → PR #129 integrada em 2026-10-06 (merge 83a9624). Elos posteriores: #171 (decisão de custódia do token e exposição do OpenAPI) aberta.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260920-api-skeleton.md; fontes/batch-revalidated-specs58-sources/history/T-20260920-api-skeleton.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_api__app.py; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_api__auth.py; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_api__config.py; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_api__routes____init__.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_api_app.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: health saudável/indisponível, isolamento de stores e router temporário têm casos fake. Sem token em path inexistente espera401 e zeroqueries (146–154); token desconhecido espera401, sem assert de query (157–161). Load_settings vazio recusa; Settings diretamente injetado não faz essa validação. Relato de comandos executados não é prova nova nesta revisão.

### Fluxo

Fluxo lido: /v1 começa no middleware, com exceção pública health; autorizado segue router descoberto/store. ApexStoreError passa a envelope502 sanitizado; erro inesperado usa corpo500 fixo e log. health absorve ApexStoreError como unreachable200, mas não toda classe arbitrária de exceção.

### Consequências e risco

Controles presentes protegem casos definidos; scanner AST não certifica ausência universal de credenciais e injeção explícita de Settings contorna load_settings. Isso não prova serviço aberto: conjunto vazio recusa todas chamadas protegidas. Token no navegador/docs e perfil seguem #171. Não há comprovação de implantação nem ausência global de risco.

### Alternativas e recomendação

Recomendado: manter encerrada; conduzir as escolhas de custódia de token e exposição de docs na #171. Alternativas registradas na própria PR: auth por dependência (rejeitada por vazar quais rotas existem via 401/404).

### Dependências e paralelismo

Nenhuma dependência técnica pendente: é a primeira folha do plano serve-api. A decisão de custódia do token e de exposição dos docs (#171) é humana e paralela; nenhuma revisão ou estudo precisa esperar por esta spec.

### Plano e aceite propostos

Não ação no código. Rastreabilidade: registrar que a fonte da decisão (nota de reunião) não está no repositório; se a #171 decidir mudanças, abrir spec própria.

### Comunicação entre responsáveis

Explicar: 'A API existe desde #129 com token obrigatório, erro sanitizado e health que responde com o banco fora; quem guarda o token e se os docs ficam públicos é decisão da #171.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Com autenticação como dependência de rota, um anônimo distinguiria rota existente (401) de inexistente (404); iniciando sem token, a API serviria aberta. Que caso o teste ainda não cobre? — A implantação real atrás do nginx e o token entregue ao navegador pelo /config.js. Como eu explicaria isso para outro pod? — 'A API troca credencial de banco por token de serviço; a guarda do token ainda é uma decisão aberta.'

### Próxima ação e encerramento

Ação: nenhuma na spec; registrar vínculo com #171 e a fonte externa não versionada da decisão de 15/09. Owner a confirmar: Serve (Pod 3). Entrada: #171. Saída: referência cruzada no índice. Encerramento: já encerrada.

