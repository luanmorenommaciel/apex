# Fichas documentais — lote 20

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-191"></a>

## T-20260820-effective-duration-properties — T-20260820-effective-duration-properties.md

Frente: Engine / telemetria retry-safe (#89). Encaminhamento: reconciliar_status_com_pergunta_aberta_resolvida_por_99.

### Identidade e estado

`tasks/T-20260820-effective-duration-properties.md` (blob 39bf4f81). 'Add the effective_* fallback properties, plus the raw fields they and tail_outlier need', S, standard, P2; owner `(none)`; depends_on tail-outlier-raw-fields (implementada). Estado `ready`, `accepted: false`. Pod provável: Pod 2/Engine (PR #89 com rótulo pod-2-engine segundo a camada de leitura do corpo; nenhum pod no arquivo). Escopo revisado três vezes em 2026-08-20 (950960245f, 3677698fc2, ad232c806e). source_note: 'ported from a prior independent APEX baseline'.

### Intenção e benefício

Acrescentar propriedades que preferem `successful_task_*` quando há amostra real e caem para os campos legados caso contrário (effective_task_duration_p50/p99/max, duration_sample_source, duration_sample_count, tail_ratio), mais quatro campos crus esquecidos pela unidade anterior — tudo aditivo.

### Feito, faltante e não comprovado

Implementado: propriedades em `schema.py:218-244` e os quatro campos crus (task_duration_sample_count, successful_task_duration_p50/p99_ms, successful_task_shuffle_read_bytes_p50) no modelo e no SQL (bce4fc6, #89; testes diretos d04bfbc). A 'Open Question' da spec (rotear skew_ratio pelos effective_*) foi decidida em #90 e implementada por 600e79d (#99): skew_ratio agora usa effective_*. Consequência: B-4/eval_4 (skew_ratio inalterado, `grep -A2 'def skew_ratio'` pela fórmula antiga) falharia na main — superado, não regressão (inferência estática).

### Linhagem

Spec de origem 9509602 e revisões 3677698/ad232c8 → bce4fc6 e testes d04bfbc → merge #89 c67ba0e → #99/600e79d altera skew_ratio → comentário do mantenedor #90/5718036779 em17/09 confirma decidido+implementado. A spec continua ready/false. O status candidate na nota docs/task-specs/ISSUE-90-RETRY-SAFE-SKEW.md é anterior e não revoga a decisão posterior. O elo pendente é a reconciliação documental do eval histórico.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260820-effective-duration-properties.md; fontes/batch-revalidated-specs28-sources/history/T-20260820-effective-duration-properties.txt; fontes/batch-revalidated-specs28-sources/git/engine/src/apex_engine/schema.py#L204-L246; fontes/batch-revalidated-specs28-sources/git/engine/src/apex_engine/clickhouse.py#L25-L145; fontes/batch-revalidated-specs28-sources/git/engine/tests/test_watchers.py#L420-L440; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #89 e #99); fontes/batch-revalidated-specs28-sources/public-captured-comments.json; issue #90, comentário 5718036779). Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: propriedades e campos presentes; skew_ratio já roteado (decisão aplicada). INFERÊNCIA: evals 1–3 satisfeitos pelo código atual; eval_4 falharia. RELATO: #89 cita 'seven direct property tests' adicionados depois (autor). Sem execução. DECISÃO: a pergunta aberta da spec está resolvida por #90/#99 — não deve mais aparecer como pendente.

### Fluxo

Fluxo observado: StageAggregate → successful_task_sample_count > 0 ? successful_task_* : task_duration_* → effective_* → skew_ratio (desde #99) e tail_ratio → watchers skew/tail_outlier. duration_sample_count = task_duration_sample_count ou task_count no ramo legado.

### Consequências e risco

Sem ação: nenhum risco de produto. Risco de processo idêntico ao da unidade anterior (eval obsoleto confundido com regressão). Limite técnico observável: com amostra de sucesso muito pequena (ex.: 1 tarefa), a razão retry-safe pode ser instável — questão levantada na camada de leitura de #99, não defeito demonstrado.

### Alternativas e recomendação

Recomendado: propor encerramento/reconciliação com bce4fc6/d04bfbc/#89 e registrar explicitamente a superação de B-4/eval_4 por #90/#99. A observação de código entregue não concede aceite retrospectivo; o responsável deve registrar a forma permitida, podendo manter accepted=false se esse for o processo. Não reverter skew_ratio para satisfazer o grep histórico.

### Dependências e paralelismo

Nenhuma dependência pendente. O watcher tail_outlier (#127) consome estas propriedades e já está entregue. A reconciliação corre em paralelo com as demais de #89 e não depende de prova runtime.

### Plano e aceite propostos

Nota de reconciliação com SHA de implementação, merge #89, comentário decisório #90 e mudança #99; preservar o eval antigo como contrato daquele recorte com limite temporal explícito. Testes atuais de população e fallback são evidência de cobertura presente, sem execução nova. Prova adicional, se necessária ao aceite escolhido, deve ter contrato/SHA identificados; um resultado histórico de #89 não certifica a main atual.

### Comunicação entre responsáveis

Explicar: 'As propriedades effective_* estão no Engine desde #89 e o tail_outlier as usa. A pergunta que a spec deixou aberta foi decidida em #90 e aplicada em #99; o eval que fixava o skew antigo é histórico.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Misturar populações successful e legacy pode criar uma razão ou piso sem a semântica declarada. Que caso o teste ainda não cobre? Caso a conferir: amostra de sucesso mínima; a revisão não declara ausência universal de cobertura. Como eu explicaria isso para outro pod? As propriedades são entregas de #89; a mudança posterior de skew_ratio pertence a #90/#99.

### Próxima ação e encerramento

Ação: reconciliação documental com nota sobre #90/#99. Owner a confirmar: Engine. Entrada: commits listados. Saída: spec em done com nota. Encerramento: arquivo movido e Open Question marcada como resolvida.

<a id="item-192"></a>

## T-20260820-tail-outlier-raw-fields — T-20260820-tail-outlier-raw-fields.md

Frente: Engine / telemetria retry-safe (#89). Encaminhamento: reconciliar_status_com_eval_invalidado_por_decisao_posterior_99.

### Identidade e estado

`tasks/T-20260820-tail-outlier-raw-fields.md` (blob 350099a6). 'Land the raw fields the tail-outlier watcher needs', S, standard, P2; owner `(none)`; sem dependências. Estado `ready`, `accepted: false`. Pod provável: Pod 2/Engine (PR #89 com rótulo pod-2-engine segundo a camada de leitura do corpo; nenhum pod no arquivo).

### Intenção e benefício

Tornar alcançáveis seis colunas v0.5 (task_duration_max_ms, successful_task_duration_max_ms, successful_task_sample_count, successful_task_shuffle_read_bytes_max, successful_task_shuffle_read_bytes_sample_count, task_speculative_attempt_count) com default 0, sem tocar propriedades existentes — preparação para o watcher tail_outlier.

### Feito, faltante e não comprovado

Implementado: os seis campos em StageAggregate e no SQL (commit 638459a, #89). Divergência relevante: B-3 exige `skew_ratio` 'byte a byte inalterado' e o eval_3 procura `self.task_duration_p99_ms / self.task_duration_p50_ms` nas duas linhas após `def skew_ratio`; no SHA, `skew_ratio` foi redefinido de propósito por 600e79d (PR #99, decisão da issue #90) para usar `effective_task_duration_*`, e a fórmula antiga está em `legacy_skew_ratio` (`schema.py:205-216`). Logo o eval_3, rodado na main, falharia — por decisão posterior legítima, não por defeito desta unidade (inferência estática).

### Linhagem

CONTRACT.md v0.5 → spec 4734222 → implementação 638459a → PR #89 integrada 16:17 UTC de 2026-09-14 → PR #99 integrada 16:54 UTC do mesmo dia, mudando skew_ratio (resposta à pergunta da issue #90, fechada 2026-09-17) → spec ready/false. Elo ausente: atualização da spec/eval após #99.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260820-tail-outlier-raw-fields.md; fontes/batch-revalidated-specs28-sources/history/T-20260820-tail-outlier-raw-fields.txt; fontes/batch-revalidated-specs28-sources/git/engine/src/apex_engine/schema.py#L170-L246; fontes/batch-revalidated-specs28-sources/git/engine/src/apex_engine/schema.py#L204-L216; fontes/batch-revalidated-specs28-sources/git/engine/src/apex_engine/clickhouse.py#L25-L145; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #89 e #99); fontes/batch-revalidated-specs28-sources/public-captured-comments.json; issue #90, comentário 5718036779). Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: seis campos no modelo/SQL; skew_ratio usa effective_*, e legacy_skew_ratio conserva a fórmula anterior. O grep do eval_3 procura fórmula antiga junto a def skew_ratio, que não corresponde ao código atual. INFERÊNCIA: esse eval não satisfaria sua condição textual no SHA lido; não foi executado. DECISÃO DOCUMENTADA: mantenedor em #90/5718036779 confirma decidido+implementado por #99. RELATO de testes de #99 não substitui execução independente ou prova runtime.

### Fluxo

Fluxo observado: spark_events (6 colunas DEFAULT 0) → STAGE_AGGREGATES_SQL → StageAggregate → propriedades effective_*/tail_ratio → tail_outlier/skew. Na época da spec: skew_ratio lia task_duration_* direto.

### Consequências e risco

Sem ação: nenhuma regressão de produto. Risco de processo: quem tentar 'mover para done rodando os evals' na main obterá falha e pode concluir, errado, que a implementação quebrou — ou reverter #99 para satisfazer o eval. Confiança alta.

### Alternativas e recomendação

Recomendado: reconciliar implementação 638459a/#89 e explicitar que B-3/eval_3 só descreve o recorte anterior a #99. Não atribuir aceite novo pelo merge. Alternativas documentais: preservar spec histórica com nota de superação, ou versão nova do contrato de aceite claramente datada sem apagar a anterior. Nunca reverter skew_ratio só para passar o eval antigo.

### Dependências e paralelismo

Nenhuma dependência técnica pendente. effective-duration-properties depende desta e também está implementada. A reconciliação documental corre em paralelo com as demais de #89; a decisão de #90 já está tomada e não bloqueia.

### Plano e aceite propostos

Passos: ligar 638459a e c67ba0e/#89 à nota de entrega; ligar 600e79d/#99 e comentário decisório de #90 ao limite temporal de B-3/eval_3; registrar a forma de transição aceita pelo responsável. Se um rerun histórico for escolhido, seu recibo só atesta aquele SHA e não a main atual. O controle atual de população retry-safe permanece referência, sem execução nesta revisão.

### Comunicação entre responsáveis

Explicar: 'Os seis campos estão no Engine desde #89. O eval que exigia skew_ratio inalterado deixou de valer quando #99 mudou skew_ratio por decisão da issue #90; isso não é regressão.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Reverter skew_ratio apenas para satisfazer o grep antigo desfaria uma decisão posterior do mantenedor. Que caso o teste ainda não cobre? Caso a conferir: amostra positiva com p50 zero e leitura por população, sob o contrato vigente. Como eu explicaria isso para outro pod? O eval antigo tinha prazo semântico: sua superação não prova regressão runtime.

### Próxima ação e encerramento

Ação: reconciliação documental com nota sobre #99. Owner a confirmar: Engine. Entrada: 638459a, 600e79d, issue #90. Saída: spec em done com nota de eval superado. Encerramento: rastreio ao SHA de integração registrado.

<a id="item-193"></a>

## T-20260920-tail-outlier-runtime-gate — T-20260920-tail-outlier-runtime-gate.md

Frente: DEV / prova tail-outlier (#123). Encaminhamento: manter_aberta_reconciliar_runtime_historico_e_garantia_do_gate.

### Identidade e estado

`tasks/T-20260920-tail-outlier-runtime-gate.md` (blob d7ae7de0). 'Prove the tail-outlier public path against real canonical telemetry', M, standard, P2; owner `(none)`; sem dependências; source_note issue #123; `signed_off_sig` hmac v3 presente, mas `accepted: false`. Estado `ready`. Pod provável: Pod 2/Package+DEV (caminhos dev/ e wrapper scripts/; nenhum pod no arquivo). Plano issue123-tail-outlier-runtime-gate.yaml (approved: true, 1 unidade).

### Intenção e benefício

Tornar tail_outlier um gate de runtime local, manual e fail-closed: validar telemetria Spark fresca (≥100 tarefas e amostras efetivas, p50 positivo, max/p50 estritamente > 10) antes do gate de pacote público procurar `tail_outlier_watcher`. Benefício: prova de que uma cauda esparsa real sobrevive à rota Spark→Collector→ClickHouse→Engine.

### Feito, faltante e não comprovado

Código e testes da asserção estão presentes; _tail_outlier_result exige ≥100 tarefas/amostras, p50 positivo finito e max/p50 >10. O registro de entrega relata núcleo em20/09 (200 tarefas, razão373.364) e wrapper macOS/Spark4.0.1 em21/09 com cache de imagens e recursos parciais. Não é cold start nem nova execução desta revisão. Lacunas separadas: status accepted=false; nenhum aceite independente inferido do merge; wrapper não associa finding a stage/snapshot/população da asserção e imprime llm_calls=0 literal. B-5 também não recebe garantia integral: Sync-DevEnvForCanonicalScript:609–616 copia sobre dev/.env com -Force, e o próprio registro:69–77/182–194 admite sobrescrita e ausência de ownership check. Nenhum incidente em ambiente alheio foi observado aqui.

### Linhagem

Issue #123 → plano e spec/implementação cd5f16b → endurecimentos85a3b8b/c236bb2 → delivery record de runtime20/09 e21/09 → merge#127 fec8a7f em06/10 → spec ready/false. Comentário de estudo#123/6109741594 preserva propostas estáticas posteriores sobre associação, sem runtime ou decisão nova. Elos pendentes: reconciliação dos critérios/runtime histórico, garantia escolhida e aceite formal. scripts/apex.ps1 é Do-Not-Touch desta spec; alterações nesse wrapper precisam de folha própria ou revisão explícita do escopo, conforme o follow-up do delivery record.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260920-tail-outlier-runtime-gate.md; fontes/batch-revalidated-specs28-sources/history/T-20260920-tail-outlier-runtime-gate.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/issue123-tail-outlier-runtime-gate.yaml#L8; fontes/batch-revalidated-specs28-sources/git/docs/e2e/TAIL_OUTLIER_RUNTIME_GATE.md; fontes/batch-revalidated-specs28-sources/git/dev/scripts/canonical_e2e_assert.py#L60-L140; fontes/batch-revalidated-specs28-sources/git/scripts/apex.ps1#L677-L711; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #127); fontes/batch-revalidated-specs28-sources/public-captured-issues.json; issue #123); fontes/batch-revalidated-specs28-sources/public-captured-comments.json; issue #123, comentário 6109741594); fontes/batch-revalidated-specs28-sources/git/scripts/apex.ps1#L609; fontes/batch-revalidated-specs28-sources/git/dev/tests/test_canonical_e2e_assert.py; fontes/batch-revalidated-specs28-sources/git/tests/test_tail_outlier_package.py; fontes/batch-revalidated-specs28-sources/git/engine/src/apex_engine/cli.py. Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: asserção de telemetria, cenário opt-in e testes focais presentes; wrapper extrai job_id, exige RC0 do Engine, procura substring em toda a saída e imprime llm_calls=0 como literal; CLI imprime também result[llm_calls]. Copy-Item -Force é observado no helper de sync. RELATO HISTÓRICO: runs locais de20/09 e21/09, contagens de testes e limitações do daemon, descritos pelo autor. INFERÊNCIA: a condição textual do wrapper não impõe associação stage/snapshot/população nem comparação do contador, e a seleção por nomes fixos não comprova ownership. Não se demonstrou falso PASS real, chamada LLM efetiva ou dano de configuração. DECISÃO PENDENTE: garantia e critérios remanescentes, mantendo B-5 explícito.

### Fluxo

Fluxo estático: package tail-outlier → configuração/doctor → sync copia .apex/dev.env para dev/.env → runner PowerShell -Scenario tail_outlier → Spark/plugin/Collector/ClickHouse, como percurso configurado → asserção qualifica stage/população → log fornece job_id → Engine --dry-run --no-crew → busca substring do watcher → marcador literal de sucesso. A asserção e o Engine recebem o mesmo job, mas o wrapper não compara stage, snapshot ou população; não se reexecutou o percurso. A preparação de ambiente é uma fronteira adicional com limite conhecido de preservação.

### Consequências e risco

Sem reconciliação: pode haver aceite excessivo do gate por confundir relato histórico e checks textuais com associação forte ou preservação universal. Um finding de outro stage satisfazer a substring é hipótese estática delimitada, não caso reproduzido. A sobrescrita de dev/.env está no código e é documentada; existência de arquivo operacional diferente ou dano não foi observada. Confiança alta nos fatos de código; runtime permanece relato autoral.

### Alternativas e recomendação

Manter aberta a reconciliação delimitada: reconhecer runtime histórico com seus limites; confrontar B-5 com overwrite/ownership; decidir se a associação exigida é apenas por job ou também stage/snapshot/população; definir como conferir o contador real já impresso pelo CLI. Se garantia fraca for escolhida, registrar revisão explícita do critério aplicável, sem apagar as outras condições. Cold start, Windows, CI e revisão humana conservam seus objetos e provas próprias, sem serem impostos como gates globais de estudos. Mudança do wrapper requer folha separada porque ele é Do-Not-Touch desta spec.

### Dependências e paralelismo

Desenho dos controles, reconciliação de critérios e decisão de garantia podem avançar offline em paralelo. Nova execução depende de ambiente autorizado e identificado; prova CI depende da capacidade e do workflow/head próprios, sem presumir billing universal atual. Correção de sync/ownership precisa de folha própria do wrapper. Nenhuma dessas decisões é nova autorização de runtime nesta auditoria.

### Plano e aceite propostos

Passos propostos: (1) nota de cobertura B-1..B-5 ligando código e recibos históricos; (2) preservar B-5 e preparar folha própria que preserve dev/.env (passagem direta de EnvFile, recusa ou outra alternativa aprovada na #174) e recuse recursos sem ownership compatível antes dos efeitos; casos negativos em cópia/handlers inofensivos, sem tocar ambiente real; (3) escolher garantia de associação e definir controle de outro stage/snapshot/população se exigida; (4) conferir result[llm_calls] emitido pelo Engine em vez de apenas imprimir literal; (5) somente numa etapa autorizada, recibo novo com SHA, contrato, plataforma/versões e condições do daemon. Reconciliar a tabela Evidence still required sem apagar relatos de setembro.

### Comunicação entre responsáveis

Explicar: o gate tem código e relato de runtime local de setembro, com cache e daemon parcial. A checagem final procura o watcher no job e imprime zero LLM sem comparar o contador; não associa stage/snapshot/população. O próprio delivery record também declara overwrite de dev/.env e falta de ownership. São garantias a reconciliar com critérios e escopo próprios; merge não concede aceite nem prova que os gates anteriores foram satisfeitos.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Aceitar só a substring do watcher não associa o finding ao stage, snapshot e população qualificados. Que caso o teste ainda não cobre? Casos a conferir: outro stage emitindo, contador LLM divergente, dev/.env diferente e recursos de outro checkout. Como eu explicaria isso para outro pod? O relato histórico prova um recorte local declarado; as garantias de associação e preservação precisam ser escolhidas e demonstradas.

### Próxima ação e encerramento

Ação: construir matriz B-1..B-5/critério de#123 → prova existente/limite → disposição necessária, com responsável a confirmar de DEV/Package, Engine e mantenedor. Entrada: spec, delivery record, wrapper, CLI e comentário de estudo. Saída: decisão de garantia e folhas de correção apropriadas, preservando runtime histórico. Encerramento: critérios satisfeitos ou explicitamente revisados, recibos ligados ao SHA e aceite de quem tem autoridade; nenhum encerramento automático por merge/ready.

<a id="item-194"></a>

## T-20260817-serverstatus-model — T-20260817-serverstatus-model.md

Frente: Serve / L1 Connect — apex_status. Encaminhamento: manter_done_historico_com_limite_B3_e_produtor_ausente.

### Identidade e estado

`tasks/done/T-20260817-serverstatus-model.md` (blob 0452b0b6, sha256 idêntico ao snapshot). Task-Spec v3, título 'Add the ServerStatus Pydantic model', esforço S, perfil standard, P2; owner `(none)`, parent `(none)`, tracker `(none)`. Estado no SHA c3c3ea3: `status: done`, `accepted: true` por `sidymar` em 2026-08-17T14:38:03Z, `signed_off: true` com `signed_off_sig` HMAC. Pod provável: Pod 3/Serve (inferido pelos caminhos serve/; nenhum pod no arquivo). Autor dos commits: Sidymar Prexedes; autor não é owner designado.

### Intenção e benefício

Definir payload tipado para a intenção apex_status antes do produtor, com schema estável e defaults de degradação. A ausência de campos chamados password/user/dsn reduz destinos óbvios para credenciais, mas não impede que strings livres recebam valores sensíveis. O benefício funcional depende de um produtor e de sua política de preenchimento/serialização.

### Feito, faltante e não comprovado

No SHA lido, ServerStatus tem connected obrigatório e defaults para os demais, incluindo contagens, timestamps, listas e remediação. test_status.py contém testes de construção/schema, ausência de nomes de credenciais e uma fixture de using_defaults. B-3 literal de qualquer resposta sem credenciais não é garantido pelo modelo: degraded_reason/remediation e itens list[str] aceitam strings, sem sanitizador ou validação de nomes. Busca nos arquivos Serve/src do recorte encontra ServerStatus apenas na definição e apex_status no comentário do modelo; não foi identificado produtor. Testes foram lidos, não executados.

### Linhagem

docs/lanes/L1_tasks.md → l1-connect.yaml:9 (approved: true) → spec gerada em 3a6b40253c → eval corrigido em 10b96e20 → implementação e `accepted: true` no mesmo commit 667926055e (2026-08-17) → transição a done em 4e2294060f (resposta ao review Codex) → PR #79 integrada em 2026-08-18 (e7519d0). Elos ausentes: consumidor (register-apex-status) nunca entregue; nenhum CI do head de #79 consultado nesta revisão; aceite é do próprio autor via `taskspec accept`, não de revisor independente.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/done/T-20260817-serverstatus-model.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-serverstatus-model.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L9; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_mcp/models.py#L572-L612; fontes/batch-revalidated-specs28-sources/git/serve/tests/test_status.py; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_api/app.py#L160-L177; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83). Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: classe, campos, defaults e testes presentes; front matter done/accepted=true por sidymar e assinatura textual presentes. RELATO HISTÓRICO: commit e PR#79 registram ACCEPTED=1/102 passed pelo autor. Isso não comprova revisão humana independente nem resultado atual. INFERÊNCIA: a entrega de estrutura/schema está presente, enquanto a redação absoluta de B-3 excede o controle de nomes de campo. Nenhum payload com segredo foi produzido nesta revisão. DECISÃO PENDENTE: destino da funcionalidade e, se retomada, fronteira que garante sanitização dos valores.

### Fluxo

Fluxo proposto (não observado em runtime): ReadStore.store_health + probes de colunas → [números e conjuntos] → diagnose.status (inexistente) → [ServerStatus] → tool apex_status (inexistente) → FastMCP → [JSON validado pelo schema] → cliente MCP. Observado estaticamente apenas o nó ServerStatus e seu schema.

### Consequências e risco

Sem ação, o modelo permanece código não usado: risco baixo (custo de manutenção e falsa impressão de que existe status MCP). Confiança alta na ausência de consumidor (busca textual); nenhum incidente associado. Limite: não verifiquei se outro consumidor indireto (API) importa o modelo — a rota `/v1/health` da API usa `store_health()` direto e devolve dict.

### Alternativas e recomendação

Manter o registro histórico done e seu accepted declarado; anotar ausência de produtor e limite de B-3 sem certificar garantia absoluta. Não reabrir toda a entrega nem apagar modelo apenas por estar ocioso. Se apex_status for adotado, o contrato do produtor deve provar ausência de credenciais nos valores; se rejeitado, remoção ou reuso HTTP são decisões separadas e reversíveis.

### Dependências e paralelismo

Não depende de nada para permanecer encerrada. Dependentes declarados: status-assembler e surface-defaulted-vars. A decisão sobre a família (register-apex-status) pode ser estudada em paralelo com qualquer outra frente; implementar um produtor depende dessa decisão, não deste modelo.

### Plano e aceite propostos

Ação documental mínima: registrar modelo entregue sem produtor e explicitar que os controles presentes cobrem estrutura/schema e nomes de campos, não ausência universal de credenciais nos valores. Nenhum novo teste exigido só para essa nota. A eventual adoção/remoção/reutilização possui escopo próprio; a família pode ser estudada em paralelo.

### Comunicação entre responsáveis

Explicar: ServerStatus e testes estruturais foram integrados por #79, e o arquivo declara aceite pelo autor. O produtor MCP não foi encontrado no Serve/src lido. O histórico done pode ser preservado com nota de que B-3 absoluto não é garantido por strings livres, sem alegar status MCP disponível ou aprovação independente.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Um dict sem schema diminuiria a explicitação do payload, mas modelo com strings livres não impede todo vazamento. Que caso o teste ainda não cobre? Caso a conferir: credencial inserida em degraded_reason, remediation ou using_defaults. Como eu explicaria isso para outro pod? ServerStatus existe sem produtor MCP; campos e testes estruturais não equivalem à funcionalidade de status disponível.

### Próxima ação e encerramento

Ação: acrescentar nota documental de entregue sem produtor e limite de B-3; responsável a confirmar: Serve. Entrada: modelo/testes e busca estática no SHA, sem depender de nova decisão apenas para registrar o fato. Saída: referência no índice/plano ou ficha de decisão futura. Encerramento histórico preservado; nenhum aceite novo emitido por esta auditoria.

<a id="item-195"></a>

## T-20260817-store-health-query — T-20260817-store-health-query.md

Frente: Serve / L1 Connect — apex_status. Encaminhamento: encerrar_concluida_com_reuso_pela_api.

### Identidade e estado

tasks/done/T-20260817-store-health-query.md (blob dfd9f45c); Task-Spec v3 Add ReadStore.store_health for counts and freshness, S/standard/P2, owner/parent/tracker (none). Front matter done/accepted=true por sidymar em17/08/2026 às14:44:09Z, assinatura HMAC textual presente. Pod provável Serve pelo caminho, sem owner designado. Git registra exclusão em556a1f6 e recriação em90c0f58 antes da implementação e transição; assinaturas e campos não foram criptograficamente validados nesta revisão.

### Intenção e benefício

Distinguir um Apex conectado-mas-vazio de um quebrado com uma leitura não indexada por job_id (contagem, jobs distintos, max(ts)). Beneficia o usuário que instala o servidor e o operador que precisa saber se há dados e quão frescos.

### Feito, faltante e não comprovado

Feito: `ReadStore.store_health()` em `ch.py:771` via `_query(HEALTH_SQL, {})` (sanitização herdada), normaliza `latest_ts` a None quando `row_count` é 0; quatro testes em `test_ch.py:152-195` (contagens, tabela vazia, store inacessível sanitizado, SQL sem interpolação). Reuso posterior observado: a rota `/v1/health` da API (`apex_api/app.py:160-177`) chama `store_health()` e reporta `store: unreachable` em vez de falhar. Falta: nada no escopo da spec. Não comprovado: B-3 depende de `_sanitize` classificar 'OperationalError' por nome — a função foi reescrita em #140 (6cb31ea) e ainda mantém esse ramo por nome (`ch.py:1232`), por leitura; não executei o teste.

### Linhagem

L1_tasks.md → l1-connect.yaml:63 → spec 3a6b402 → evals corrigidos (556a1f6: o eval proibia '{' e teria removido o binding; 90c0f58: eval lia saída suprimida por addopts) → implementação cea056e6 com `accepted: true` → done em 4e22940 → PR #79 (2026-08-18). Elo posterior não previsto na spec: reuso pela API (#129, 2026-10-06). Elo ausente: apex_status, o consumidor planejado.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/done/T-20260817-store-health-query.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-store-health-query.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L63; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_mcp/ch.py#L771-L789; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_mcp/ch.py#L126-L132; fontes/batch-revalidated-specs28-sources/git/serve/tests/test_ch.py#L127-L195; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_api/app.py#L160-L177; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_mcp/ch.py#L1217-L1262; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83). Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: HEALTH_SQL sem entrada de usuário, store_health via _query, normalização de tabela vazia, quatro testes focais e consumidor /v1/health no código. test_store_health_sql_is_bound_not_interpolated confere ausência de placeholder e parameters=={}: nesta query sem entrada, a garantia é não interpolar; não há valor do usuário a ligar. RELATO HISTÓRICO: commit/PR#79 registram ACCEPTED=1 pelo autor. Nem testes, nem implantação/produção, nem checks atuais foram observados em execução aqui. O comentário de frescor diz relógio do emissor, não ingestão.

### Fluxo

Fluxo observado estaticamente: GET /v1/health → app.health → get_store(request).store_health → _query(HEALTH_SQL,{}) → tabela spark_events da sessão configurada → row_count/job_count/latest_ts → wire → corpo {status:ok,store:ok,...}; ApexStoreError → corpo {status:ok,store:unreachable,detail}. Código de rota implica a resposta pretendida, sem prova de operação real. Fluxo MCP planejado apex_status não está implementado nos módulos lidos.

### Consequências e risco

Sem ação: nenhum risco novo; o método está em uso pela API. Limite da afirmação: `latest_ts` é o relógio do emissor (docstring), não da ingestão — um host Spark com relógio desviado aparece como frescor desviado; isso é limite documentado, não defeito observado.

### Alternativas e recomendação

Recomendado: manter encerrada e registrar o reuso HTTP como o consumidor real. Alternativa: se apex_status for adotado, reutilizar o mesmo método (evita segunda query de saúde). Não recomendo criar teste novo só para formalizar o encerramento.

### Dependências e paralelismo

Nenhuma dependência pendente. É precondição declarada de table-columns-probe e register-apex-status; essas podem ser decididas independentemente. O estudo de 'status por HTTP vs MCP' pode correr em paralelo com a decisão de apex_status.

### Plano e aceite propostos

Não ação sobre código. Passo documental: registrar no índice L1 que store_health foi entregue e hoje alimenta `/v1/health`. Controle discriminante já existente: teste de tabela vazia (zero DateTime → None) e de SQL sem interpolação. Se apex_status vier, exigir que reutilize este método e acrescentar teste de associação (mesmos números nas duas portas).

### Comunicação entre responsáveis

Explicar: store_health entrega leitura de contagens e max(ts), com normalização de store vazio, e é chamado por /v1/health no código integrado. Isso não demonstra implantação em produção. O consumidor MCP originalmente planejado continua ausente, sem desfazer o escopo entregue desta query.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Usar now() no lugar de max(ts) deixaria de reportar o frescor do dado observado. Que caso o teste ainda não cobre? Caso a conferir: linhas positivas com timestamp nulo ou relógio do emissor desviado. Como eu explicaria isso para outro pod? A rota /v1/health usa store_health no código; presença na main não comprova implantação em produção.

### Próxima ação e encerramento

Ação: anotar reuso e manter encerrada. Owner a confirmar: Serve. Entrada: este parecer. Saída: nota no índice/plano. Encerramento: já cumprido; nenhuma prova adicional exigida salvo mudança no método.

<a id="item-196"></a>

## F01 — Criar issue específica do /verify

Frente: front_verify_tela. Encaminhamento: encerrar_historico_concluido.

### Identidade e estado

F01 é um item seed do registro ("Criar issue específica do /verify", tipo issue, Pod 1/Front). O registro já o marcava superado: a issue luanmorenommaciel/apex#116 "[Front] /verify: estados por fonte e apresentação fiel da proposta e das evidências" foi criada por gustocezar em 2026-09-11 e fechada como completed em 2026-09-14T16:20:48Z por luanmorenommaciel. As PRs #118 (a8ccc52), #119 (0f19712) e #120 (961e296) foram integradas no mesmo dia (merges fbacbf0, 189b3c6 e dc9f22e na primeira linha da main). Sem assignee; nenhum owner pendente.

### Intenção e benefício

Intenção original: ter uma issue própria para a tela /verify do Front, separando estados por fonte (carregando, vazio, erro, dados) e apresentando com fidelidade a proposta original e as evidências do Verify. Público: quem usa a Console para ler um veredito de verificação. Ganho: o usuário distingue "sem dado" de "erro" e não vê uma proposta reescrita.

### Feito, faltante e não comprovado

Feito: issue criada, três PRs integradas e issue fechada. Falta neste ID: nada. Não comprovado nesta revisão: o comportamento atual da tela /verify depois das mudanças de 06/10 (#129/#136/#151); isso não é critério deste ID. Não confundir com o contrato de escrita de fix_verifications (#117/F06), que é outra pergunta: de onde vêm as linhas que a tela lê.

### Linhagem

Linhagem documental: seed F01 → issue #116 (11/09) → PR #118 (I1), #119 (I2) e #120 (região nomeada) → merges fbacbf0/189b3c6/dc9f22e em 14/09 e fechamento da issue. O fechamento ocorreu às 16:20:48Z, antes dos merges finais de #119/#120 às 16:21:10Z/16:21:23Z; a sequência não demonstra aceite de todos os critérios no instante do fechamento. Testes/revisões são relatos dos corpos das PRs, não reinspecionados como execução nesta revisão.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json. Locadores e recorte: F01 no registro; issue #116 e PRs #118–#120: estados, corpos, cronologia e identidades no snapshot. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: estado closed/completed da #116 e os três merges registrados no snapshot. RELATO HISTÓRICO: testes locais e CI citados pelos autores das PRs. INFERÊNCIA: o objetivo de criar uma issue específica está satisfeito e pode ser arquivado; isso não certifica todo o comportamento atual da tela. Nenhum teste ou runtime foi executado.

### Fluxo

Fluxo histórico da tela (do corpo da #116, não reexecutado): Repository do Front —(fix_verifications por fonte)→ tela /verify —(estado por fonte: loading/empty/error/data)→ usuário; proposta original —(região nomeada, sem reescrita)→ usuário. A origem das linhas lidas é outra fronteira (#117).

### Consequências e risco

Sem ação, nada muda: o trabalho está entregue. O único risco é reabrir /verify como issue genérica e confundi-la com o contrato de escritor da #117. Confiança alta no estado público.

### Alternativas e recomendação

Recomendado: arquivar F01 como concluído pela #116 e pelas três PRs. Alternativa: manter F01 aberto como ponteiro para melhorias da tela; não há melhoria pendente registrada, então só geraria ruído. Reversível.

### Dependências e paralelismo

Nenhuma dependência para arquivar. F01 não bloqueia nem é bloqueado pela #117 (escritor de fix_verifications) nem pelas PRs de Console de 06/10; a tela e a origem dos dados evoluem separadamente.

### Plano e aceite propostos

Condição de não ação: nenhum passo de produto ou de publicação. Reabrir somente se uma regressão observável na tela /verify for registrada com fonte, por exemplo erro de fonte mostrado como lista vazia.

### Comunicação entre responsáveis

Para outro pod: "A tela /verify ganhou estados por fonte e apresentação fiel em 14/09 (#116 e #118–#120). A pergunta sobre quem escreve fix_verifications é outra e está na #117."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Reabrir a criação de issue duplicaria a #116 já fechada; isso não resolveria o contrato de quem alimenta fix_verifications. Que caso o teste ainda não cobre? Os testes históricos não foram relidos; o comportamento da tela após os merges de outubro permanece fora deste recorte de criação da issue. Como eu explicaria isso para outro pod? F01 registra a criação e entrega histórica da tela /verify; a origem das linhas exibidas segue na fronteira #117.

### Próxima ação e encerramento

Próxima ação: confirmar arquivamento de F01 na visão consolidada. Owner: nenhum necessário. Entrada: estado da #116 e das três PRs. Saída: linha F01 "concluído por #116/#118/#119/#120 em 14/09". Encerramento: imediato.

<a id="item-197"></a>

## F12 — Independência mecanismo/runtime no Front (T12)

Frente: front_contrato_regras. Encaminhamento: encerrar_pr_integrada.

### Identidade e estado

F12 é uma correção semântica do Front (Pod 1/Front), origem seed F12 / R2 T12, implementada pela PR luanmorenommaciel/apex#136 "fix(front): keep mechanism and runtime verdicts independent" (head 2fa0781, que inclui 78062d3 de F12 e 2fa0781 de TS08/F11), integrada em 2026-10-06T20:11:54Z no merge b758f17. Sem assignee. #130 é só referência de CI.

### Intenção e benefício

Problema: a regra local do Front rejeitava um runtime certificado só porque o mecanismo era falso, contrariando a regra 4 do CONTRACT.md, que mantém mecanismo e runtime como vereditos separados. Público: quem lê vereditos de verificação na Console. Ganho: o Front deixa de contradizer o contrato ratificado e não apaga uma certificação de runtime válida.

### Feito, faltante e não comprovado

Feito e visível na base: front/src/contract/rules.ts:289 descreve "RULE 4 — mechanism and runtime are two verdicts, stored separately" e as linhas 304-305 dizem que o mecanismo não é consultado, de modo que nem falso nem nulo podem vetar o runtime. Falta neste ID: nada. Não comprovado: CI hospedada do head publicado (11 check-runs sem steps segundo o registro) e revisão formal.

### Linhagem

Linhagem: verify-floor-contract §5 (M3) e R2 T12 → commit 78062d3 na branch codex/front-mechanism-runtime (base a289e53) → PR #136 aberta em 27/09 → TS14 combina com outras PRs (relato) → check-runs sem steps (#130) → revisão formal [não verificada] → merge b758f17 em 06/10. Follow-up: nenhum.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/front__src__contract__rules.ts.txt. Locadores e recorte: F12; #136 head 2fa0781/merge b758f17; rules.ts:286–307. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: PR #136 integrada no snapshot e ruleFourNoInference em rules.ts:300–307 mantém mecanismo fora da decisão de runtime. RELATO HISTÓRICO: testes locais e controle discriminante do registro e do corpo da PR (39 focados/93 Front no head 2fa0781; os 36/90 do registro referem recorte anterior). Nenhum teste, browser ou runtime reexecutado; review formal não revalidado.

### Fluxo

Fluxo observado no código: linha de fix_verifications —(mechanism_confirmed)→ rótulo de mecanismo; mesma linha —(runtime_certified/delta/piso)→ rótulo de runtime; os dois rótulos —(sem acoplamento)→ tela. O texto em rules.ts:662 adverte que mostrar mecanismo desconhecido como falho é exatamente o erro corrigido.

### Consequências e risco

Sem ação, nada regride. O risco possível é uma refatoração futura reintroduzir o acoplamento; o controle discriminante relatado é a defesa, mas não o verifiquei. Confiança alta na leitura estática.

### Alternativas e recomendação

Recomendado: arquivar o escopo F12 como integrado, preservando os limites da prova. Alternativa: reler os testes e reviews históricos se houver pergunta de aceite ou regressão específica. O merge comprova integração; não equivale por si a aprovação formal ou validação de runtime. Revert é tecnicamente possível, exigindo o processo normal de mudança.

### Dependências e paralelismo

Nenhuma dependência para encerrar. F12 não depende da #117 (escritor e piso), porque a regra 4 já estava ratificada no CONTRACT.md; F11/TS08, que entrou no mesmo head, também já está integrada.

### Plano e aceite propostos

Condição de não ação: nenhum passo neste ID. Reabrir somente se rules.ts voltar a consultar mechanism_confirmed para decidir o veredito de runtime, o que o controle discriminante relatado deveria acusar.

### Comunicação entre responsáveis

Para outro pod: "O Front agora exibe mecanismo e runtime como vereditos independentes, como manda a regra 4; um mecanismo falso não apaga um runtime certificado."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Usar mechanism_confirmed como veto apagaria runtime certificado quando o mecanismo fosse falso ou nulo, contrariando a independência da regra 4. Que caso o teste ainda não cobre? A leitura estática não comprova renderização atual nem execução dos controles históricos; esse limite requer fonte própria se surgir regressão. Como eu explicaria isso para outro pod? O rótulo do mecanismo e o do runtime são independentes; a função só rejeita a contradição interna de runtime certificado e unresolved.

### Próxima ação e encerramento

Próxima ação: confirmar encerramento de F12. Owner: nenhum necessário. Entrada: rules.ts na base e estado da #136. Saída: linha F12 "entregue em b758f17". Encerramento: imediato.

<a id="item-198"></a>

## F13 — Apresentar TAIL_OUTLIER no Front (T29)

Frente: consumidores_tail_outlier. Encaminhamento: agrupar_em_166_parte_front.

### Identidade e estado

F13 é o recorte Front de um follow-up condicional (Pod 1/Front, origem seed F13 / R2 T29 / revisão P11 da #127). Representado na issue luanmorenommaciel/apex#166, publicada da minuta P-TAIL em 2026-10-11T04:24:12Z por gustocezar, aberta, assignee gustocezar no snapshot, com um comentário (estudo C2 e fixtures). O assignee registra reserva de estudo de 11/10, não owner ratificado da implementação.

### Intenção e benefício

Problema: TAIL_OUTLIER não está em KnownFindingType, embora FindingType aceite strings novas. Um tratamento genérico ou texto de skew é risco de apresentação a caracterizar no consumidor, não renderização demonstrada apenas pela união TypeScript. Público: leitores de findings na Console; ganho: rótulo e limite observacional claros.

### Feito, faltante e não comprovado

Na base, KnownFindingType lista RETRY_PRESSURE e omite TAIL_OUTLIER (types.ts:62–73); FindingType é aberto (82). Isso não rejeita o valor em nível de tipo, mas não prova sozinho o texto/ícone renderizado. Falta caracterizar o consumidor, decidir apresentação e implementar somente a lacuna confirmada, com controles SKEW_ON_JOIN e RETRY_PRESSURE.

### Linhagem

Linhagem: revisão P11 da #127 e R2 T29 → registro F13 (study_ready, depende do merge #127) → merge da #127 em 06/10 → minuta P-TAIL (ids F13, F16, F18, S17) → #166 em 11/10 → comentário de 11/10 com estudo C2 (12 casos) e 16 fixtures declarativas → decisão de apresentação [ausente] → implementação/teste [ausente]. O rodapé público da #166 lista F13, F18 e S17; F16 consta nos source_ids da publicação local, embora ausente dos ids/rodapé público.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/front__src__contract__types.ts.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/engine__src__apex_engine__watchers__tail_outlier.py.txt. Locadores e recorte: F13/P-TAIL e source_ids; #166 corpo e comentário 6109742308 integral; types.ts:57–82; tail_outlier.py:1–71. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: KnownFindingType lista RETRY_PRESSURE e omite TAIL_OUTLIER; FindingType é aberto. RELATO HISTÓRICO: comentário #166 registra estudo estático corrigido de 12 casos e 16 fixtures não executadas. PROPOSTA: decidir texto/fallback e implementar lacunas confirmadas. Não foi localizada prova de execução deste recorte nos objetos lidos; isso não afirma ausência universal de testes ou runtime.

### Fluxo

Fluxo estático parcial: Engine —(finding TAIL_OUTLIER)→ store findings —(String aceita por FindingType aberto)→ consumidor Front. A ausência em KnownFindingType não basta para provar o rótulo de cada componente; a renderização exata precisa ser caracterizada. Fluxo proposto: texto e fallback escolhidos —(rótulo e limites)→ usuário.

### Consequências e risco

Risco possível: apresentação genérica ou explicação insuficiente de TAIL_OUTLIER pode induzir interpretação de skew. A ausência no tipo conhecido é fato; texto/ícone efetivamente renderizado e frequência do impacto não foram medidos. Confiança alta na diferença estática, probabilidade não estimada.

### Alternativas e recomendação

Recomendado: incluir TAIL_OUTLIER em KnownFindingType com rótulo e limite explícitos ("cauda de duração; não estabelece skew") e teste discriminante. Alternativas: (a) manter fallback genérico com aviso de tipo desconhecido, mais barato e genérico; (b) mapear para skew, que eu não recomendo porque contradiz o watcher. Reversível.

### Dependências e paralelismo

Depende só da decisão de apresentação na #166; o detector da #127 já está integrado. Pode correr em paralelo com F18 (Verify) e S17 (Serve), que compartilham a matriz mas tocam arquivos diferentes; não depende do piso absoluto (#168/E18).

### Plano e aceite propostos

Passos mínimos: (1) decidir texto do rótulo e do limite; (2) incluir o membro na união; (3) teste que renderize TAIL_OUTLIER com rótulo próprio e controles SKEW_ON_JOIN e RETRY_PRESSURE inalterados; (4) caso negativo: tipo desconhecido continua no fallback; (5) documentar em types.ts que o tipo é observacional. Artefato: PR pequena do Front. Aceite: teste discriminante falha na base e passa na PR.

### Comunicação entre responsáveis

Para outro pod: "O Front vai nomear TAIL_OUTLIER como cauda de duração, sem sugerir skew; a mudança é só de apresentação e não altera o detector nem o limiar."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Apresentar cauda como skew atribuiria uma causa que o watcher explicitamente não estabelece. Que caso o teste ainda não cobre? Não se executaram tela ou fixtures; a renderização de TAIL_OUTLIER junto com SKEW_ON_JOIN e o fallback de outro tipo desconhecido ainda precisa de caracterização. Como eu explicaria isso para outro pod? A união aberta aceita o finding; a #166 decide como explicá-lo, mantendo duração extrema separada de causa raiz.

### Próxima ação e encerramento

Próxima ação: Pod 1 (a confirmar) registra na #166 a decisão de rótulo para o Front. Entrada: matriz C2 e fixtures do comentário. Saída: PR do Front com membro novo e teste discriminante. Encerramento: teste discriminante integrado e critério correspondente da #166 marcado com link.

<a id="item-199"></a>

## F14 — Endurecer CI do Front

Frente: front_ci. Encaminhamento: encerrar_pr_integrada_audit_separado.

### Identidade e estado

F14 é um PR pequeno de Pod 1/Front+CI, implementado pela PR luanmorenommaciel/apex#138 "ci(front): reject warnings and empty suites" (head 4b5798d), integrada em 2026-10-06T20:12:02Z no merge 9763b2f. Sem assignee. A política de npm audit ficou explicitamente fora e pertence a E15 (DEC-15). #130 é referência de CI.

### Intenção e benefício

Problema: o CI usava npm test com --passWithNoTests, o vitest.config.ts tinha passWithNoTests: true e o lint não tinha --max-warnings 0, então suíte vazia ou warnings passavam como verde. Público: revisores que confiam no check do Front. Ganho: verde significa que havia testes e nenhum warning.

### Feito, faltante e não comprovado

Feito e visível na base: o job "front (Node 22)" em .github/workflows/ci.yml roda npm ci, typecheck, lint, npm test -- --run e build (linhas 36-61), sem passWithNoTests; front/package.json:11 define lint como "eslint src --max-warnings 0"; vitest.config.ts tem só o alias, sem passWithNoTests. Falta, fora deste ID: npm audit (nenhuma etapa de audit no workflow). Não comprovado neste recorte: execução hospedada bem-sucedida do job na base fixa; os jobs do push da main em c3c3ea3 (run 37831091789) terminaram failure sem steps.

### Linhagem

Linhagem: drafts de 31/08 e STATE owner_decision front-ci → R2 T28a → commit 4b5798d na branch codex/front-strict-ci-gates → PR #138 (27/09) → combinação TS14 com negativos em Node 22 macOS arm64 e Ubuntu x64 emulado (relato) → check-runs sem steps (#130) → merge 9763b2f → CI enxuto da #160 manteve o job front. Elo ausente: execução hospedada do job.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/.github__workflows__ci.yml.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/front__package.json.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/front__vitest.config.ts.txt; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/jobs_37831091789.json. Locadores e recorte: F14; #138; ci.yml:36–61; package.json:6–12; vitest.config.ts integral; jobs_37831091789. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: gates estritos presentes na configuração da base; ausência de audit. RELATO: negativos executados localmente pelo autor e na combinação TS14 (não é runner hospedado). INFERÊNCIA: sem steps nos jobs da main, não há prova hospedada de que o gate roda; é limite de prova, não defeito. DECISÃO PENDENTE: severidade e exceções do npm audit (E15).

### Fluxo

Fluxo observado na configuração: push ou PR para main —(dispara workflow)→ job front —(npm ci → typecheck → lint sem warnings → vitest sem permitir suíte vazia → build)→ check verde ou vermelho. Audit de dependências não participa do fluxo.

### Consequências e risco

Sem ação, o gate continua estrito na configuração. O risco é supor que dependências vulneráveis também são barradas, o que não ocorre sem a decisão de E15. Confiança alta na leitura da configuração; baixa sobre execução hospedada recente.

### Alternativas e recomendação

Recomendado: encerrar F14 e deixar audit em E15. Alternativas para audit, a decidir em E15: npm audit com limiar de severidade, Dependabot/alertas sem bloqueio, ou lista de exceções versionada. Misturar audit aqui ampliaria escopo de uma PR já integrada. Reversível.

### Dependências e paralelismo

Nenhuma dependência técnica para catalogar o escopo F14 integrado. E15 (política de dependências) é independente. Uma nova prova hospedada depende do runner disponível no momento; #130 é histórico e não prova bloqueio universal atual.

### Plano e aceite propostos

Condição de não ação: nenhum passo neste ID. Opcional: quando houver run hospedado com steps, registrar o link do job front como evidência de execução. Reabrir somente se passWithNoTests ou a ausência de --max-warnings reaparecer na main.

### Comunicação entre responsáveis

Para outro pod: "O check do Front já rejeita warnings e suítes vazias na configuração; audit de dependências é decisão separada (E15) e não faz parte desse verde."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Reintroduzir passWithNoTests ou retirar --max-warnings 0 permitiria novamente suíte vazia ou warnings sem reprovação pelo gate configurado. Que caso o teste ainda não cobre? A configuração lida não prova execução hospedada bem-sucedida deste job na base; os negativos continuam relatos locais atribuídos. Como eu explicaria isso para outro pod? O Front tem gates estritos para lint e testes; eles não são uma política de auditoria de dependências, que segue em E15.

### Próxima ação e encerramento

Próxima ação: confirmar encerramento de F14 e o ponteiro para E15. Owner: mantenedor de CI (a confirmar). Entrada: ci.yml e package.json na base. Saída: linha F14 "entregue em 9763b2f; audit em E15". Encerramento: imediato.

<a id="item-200"></a>

## F15 — Topologia e proveniência visual (#108)

Frente: front_proveniencia_grafo. Encaminhamento: estudar_em_paralelo_implementacao_depende_106.

### Identidade e estado

F15 é o estudo de views de topologia e proveniência no Front (Pod 1/Front), representado pela issue luanmorenommaciel/apex#108 "[Study][Pod 1 / Front-End] Explore topology and evidence-provenance views", aberta por gustocezar em 2026-08-25, sem assignee e sem comentários no snapshot; labels crew-a, phase:design, priority:p2. Owner a confirmar.

### Intenção e benefício

Problema: sem uma projeção tipada, uma view de topologia tende a desenhar caminhos à mão ou por prosa e mostrar como provado o que é só declarado. Público: quem compara runs e quer saber por que uma métrica existe ou falta. Ganho: uma view que responde "de onde vem este fato e até onde foi provado", com estados declared/observed/derived/runtime_unproven.

### Feito, faltante e não comprovado

Feito (relato local): o relatório [caminho local omitido] classifica #107–#109 como ready_offline e recomenda começar pela tela "Evidence topology", com componentes SystemGraphPanel, EvidenceBadge, GraphNodeDetails e GraphEmptyState e um frontend-projection.schema.json. Falta: decisão implement/defer/reject na #108 e escolha da primeira view; schema do grafo na #106. Não comprovado: que o schema de 29/08 ainda reflete a superfície atual (base 847d7a0 e "quatro ferramentas de leitura" no texto, hoje oito tools).

### Linhagem

Linhagem: seed F15 → issue #108 (25/08) → estudo #106 sobre 847d7a0 → relatório de 29/08 com três schemas e exemplos (SYSTEM_GRAPH_DESCENDANTS=PASS schemas=3 no registro) → camada de contexto de 10/10 no corpo da #108 → decisão [ausente] → implementação [ausente]. Elo ausente: nenhum vínculo público entre a #108 e o relatório local.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-revalidated-fes-sources/system-graph-REPORT.md; fontes/batch-revalidated-fes-sources/system-graph-frontend-projection.schema.json. Locadores e recorte: F15; #108 integral; relatório de 29/08 sobre 847d7a0 e schema Front integral. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: issue aberta sem decisão; relatório e schemas locais existem. RELATO: estudo ready_offline e PASS de schemas em 29/08. INFERÊNCIA: o schema precisa ser reconciliado com oito tools e com a apex-api antes de virar contrato. DECISÃO PENDENTE: adotar/adiar/rejeitar (DEC-19). Nenhum teste ou runtime aplicável.

### Fluxo

Fluxo proposto nos documentos: projeção tipada —(manifesto versionado ou API read-only sob a fronteira #102)→ Front —(basis/proof_state)→ usuário. MCP é provedor opcional; apex-api é uma opção, não predecessor obrigatório estabelecido pela #108. IA explica fatos estruturados; não define topologia. Nenhuma implementação é demonstrada por este estudo.

### Consequências e risco

Sem ação, a Console segue sem view de proveniência; não há regressão. O risco é a decisão demorar e o estudo de agosto envelhecer até não refletir a superfície. Confiança média no estudo (relato) e alta na ausência de decisão pública.

### Alternativas e recomendação

Recomendado: reconciliar o estudo com a superfície atual e propor a primeira view na #108. Alternativas legítimas: projeção estática versionada sob schema, API read-only, ou adiamento registrado. Construir topologia manual dentro da UI é a alternativa a evitar. Estudo pode avançar em paralelo à #106; implementação usa o schema decidido.

### Dependências e paralelismo

Estudos #106/#107/#108/#109 podem avançar em paralelo. Implementação depende do schema escolhido e da fronteira de carregamento decidida sob #102; a #108 admite projeção estática versionada, portanto não exige necessariamente apex-api ou catálogo MCP. Prioridade para v1 depende do mantenedor.

### Plano e aceite propostos

Estudo: reconciliar schema e superfície atual, comparar manifesto estático/API, preparar wireframe, payload e estados; registrar decisão implement/defer/reject. Saída revisável: proposta documental citada. Se implementar, planejar schema validation, estado vazio, ordenação e acessibilidade com controles do consumidor. Nenhum teste novo é necessário para esta revalidação documental.

### Comunicação entre responsáveis

Para outro pod: "Há um estudo local de agosto propondo uma view de proveniência; ele precisa ser atualizado para a superfície atual e decidido na #108. Estudar não depende do schema; implementar sim."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Desenhar topologia por prosa ou dados internos da UI poderia mostrar uma aresta declarada como provada; uma projeção estática versionada continua sendo opção válida. Que caso o teste ainda não cobre? Os schemas e exemplos não foram executados nesta revisão; falta reconciliar o estudo de agosto e planejar os controles de vazio, versão incompatível e acessibilidade. Como eu explicaria isso para outro pod? A view renderiza fatos tipados com basis e proof_state; manifesto ou API são escolhas de entrega sob a fronteira #102.

### Próxima ação e encerramento

Próxima ação: Pod 1 (a confirmar) atualiza o estudo e publica na #108 a proposta de primeira view. Entrada: relatório de 29/08 e schema #106. Saída: comentário na #108 com wireframe, payload e decisão solicitada. Encerramento: decisão implement/defer/reject registrada.

