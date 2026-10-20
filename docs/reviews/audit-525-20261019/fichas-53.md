# Fichas documentais — lote 53

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-521"></a>

## PR#150 — test(serve): guard sanitized store errors across transports

Frente: historico. Encaminhamento: historico_integrado_com_followup_delimitado.

### Identidade e estado

PR #150 de gustocezar, mergeada em 06/10/2026 20:11 UTC; head 1cef568, 1 commit, +211, 1 arquivo; empilhada sobre #129. Histórico #181 seção 4. Sem reviews.

### Intenção e benefício

O teste de rota aceitava 500 ou 502 para falhas de store, podendo passar sem provar o que o cliente recebe; fixar o contrato sanitizado store_error nos dois transportes (HTTP e MCP).

### Feito, faltante e não comprovado

Teste de HTTP TestClient e protocolo MCP em memória sobre rotas/tools reais, com cliente de store fake. Cobre ConnectionError, OperationalError e RuntimeError em superfícies selecionadas, sem vazamento dos marcadores conhecidos; envelope permite campos extras. Não cobre automaticamente todos os códigos novos da #140, nem ClickHouse real. Outras falhas e política 500/502 conservam recorte próprio.

### Linhagem

1 commit 1cef568; depende de #129; complementa #140 (que introduziu os prefixos sanitizados) cobrindo o transporte.

### Fontes e corte

Fontes da ficha: corpo/metadados e leitura estática dos diffs registrada nos campos técnicos. Reconciliação 19–20/10: diff do teste de fronteira de erros API. O arquivo integral na main atual não foi relido nesta rodada quando isso não está explicitamente declarado. Leitura de diff não é execução ou revisão integral de todo o produto. Os recibos de CI históricos mantêm o corte próprio.

### Classe e limite da evidência

Prova autor-declarada local: Serve 289 antes, 318 depois; diff check. Classe: teste de contrato sobre rotas reais/TestClient + MCP. Limite: offline; empilhada — CI não rodou na base.

### Fluxo

Falha de store → HTTP 502 store_error / MCP código sanitizado → health segue alcançável → cliente recebe contrato estável.

### Consequências e risco

Risco baixo: 'outras classes de falha' sem dono podem derivar; pergunta do corpo pede critério para congelá-las depois. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Alternativa: congelar tudo (rejeitada — decisão de donos). Recomendação: registrar critério de quando pinar nova classe de falha.

### Dependências e paralelismo

Depende de #129; par conceitual com #140; #150 é citada nas propostas como guarda de transporte.

### Plano e aceite propostos

Plano: 29 testes de guarda. Resultado/aceite é relato histórico do corpo, não nova concessão nesta revisão; CI remota condicionada ao retarget.

### Comunicação entre responsáveis

Corpo explícito sobre o que deixou de fora e por quê.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — aceitar 500 ou 502 indistintamente não provaria o contrato da falha de store; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — códigos novos do driver e ClickHouse real. Como eu explicaria isso para outro pod? — O teste de rota aceitava 500 ou 502 para falhas de store, podendo passar sem provar o que o cliente recebe; fixar o contrato sanitizado store_error nos dois transportes (HTTP e MCP).

### Próxima ação e encerramento

Registrar critério para pinar classes de falha adicionais.

<a id="item-522"></a>

## PR#151 — fix(front): render API error detail only when textual

Frente: historico. Encaminhamento: historico_integrado_sem_nova_acao_obrigatoria.

### Identidade e estado

PR #151 de gustocezar, mergeada em 06/10/2026 20:11 UTC; head 488bd8a, 1 commit, +68/−2, 2 arquivos; empilhada sobre #129. Histórico #181 seção 4. Sem reviews.

### Intenção e benefício

FastAPI devolve 422 com detail como lista; o Console tratava como string, podendo exibir [object Object]; mostrar detail/error só quando texto, senão status HTTP.

### Feito, faltante e não comprovado

Feito: type check no client; falhas de store mantêm código sanitizado; 3 testes (validação, store, fallback); contrato da API inalterado. Faltante: resumo dos erros de campo (não discutido). Não comprovado: browser e ClickHouse real; CI remota (base empilhada).

### Linhagem

1 commit 488bd8a; depende de #129; #153 inclui guarda independente no QueryFailure para não depender da ordem de merge das duas.

### Fontes e corte

Corpo da PR via API pública em 19/10/2026; http.ts não re-lido.

### Classe e limite da evidência

Prova autor-declarada local (Node 22.23.3): Front 130 antes, 133 depois; typecheck e lint. Classe: teste unitário. Limite: sem browser; sem CI remota.

### Fluxo

Resposta 422 lista → reader verifica tipo → texto exibido ou status HTTP → usuário vê motivo legível.

### Consequências e risco

Risco baixo: fallback para status text esconde qual campo falhou na validação (pergunta do corpo); superfície de contrato maior seria o custo da alternativa. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Alternativa: renderizar a lista de erros (não discutida no corpo). Recomendação: se 422s forem frequência real de usuário, considerar resumo de campos como melhoria de UX.

### Dependências e paralelismo

Depende de #129; guarda paralela em #153.

### Plano e aceite propostos

Plano: fix de renderização + 3 testes. Resultado/aceite é relato histórico do corpo, não nova concessão nesta revisão.

### Comunicação entre responsáveis

Corpo claro sobre escopo e limites.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — converter detail estruturado diretamente em texto poderia exibir objeto em vez do motivo; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — interação do usuário no navegador não está no stub. Como eu explicaria isso para outro pod? — FastAPI devolve 422 com detail como lista; o Console tratava como string, podendo exibir [object Object]; mostrar detail/error só quando texto, senão status HTTP.

### Próxima ação e encerramento

Sem mudança adicional obrigatória. Se houver necessidade de UX comprovada, propor resumo de erros de campo com teste que preserve sanitização; escolher no Pod1, sem tratar fallback atual como incidente real.

<a id="item-523"></a>

## PR#152 — docs(artifacts): add Apex current-state deck (main @ a289e53)

Frente: historico. Encaminhamento: historico_integrado_com_followup_delimitado.

### Identidade e estado

PR #152 de Antony Lucas (antonylucas) — única do recorte fora de gustocezar; mergeada em 06/10/2026 20:18 UTC por luanmorenommaciel; head 28b6822, 1 commit, +55, 25 arquivos. Corpo vazio; sem comentários; sem reviews.

### Intenção e benefício

Preservar deck de 23 slides sobre main a289e53, datado 17/09/2026, como artefato histórico e material de discussão; não é estado atualizado após merges de outubro.

### Feito, faltante e não comprovado

Diff adiciona README, índice e slides com fontes em notas. README declara geração a partir de leitura no Claude e números não reproduzidos; observações contra visão original exigem confirmação do Luan. Corpo da PR vazio limita o registro da revisão, mas não apaga os critérios/limites escritos no artefato. Afirmações históricas sobre contagem de testes, ausência de imports e tools não certificam main atual.

### Linhagem

1 commit 28b6822 por Antony Lucas; autoria distinta preservada; referenciada na #181 seção 15.

### Fontes e corte

Fontes da ficha: corpo/metadados e leitura estática dos diffs registrada nos campos técnicos. Reconciliação 19–20/10: metadados, lista de arquivos e README do deck; conteúdo integral dos 25 arquivos e slides não relido. O arquivo integral na main atual não foi relido nesta rodada quando isso não está explicitamente declarado. Leitura de diff não é execução ou revisão integral de todo o produto. Os recibos de CI históricos mantêm o corte próprio.

### Classe e limite da evidência

DIRETO nesta leitura: arquivos e notas do deck no diff, autoria da PR/commit Antony nos recibos. RELATO HISTÓRICO: números dos documentos e provas citadas; não reproduzidos. PROPOSTA/INFERÊNCIA: comparação com visão original, explicitamente sujeita a confirmação. Não é decisão arquitetural nem prova runtime.

### Fluxo

main @ a289e53 → deck de estado atual → leitor/planejamento.

### Consequências e risco

Risco baixo: leitores podem tratar o deck como estado vigente quando a main avançou (#153, #160); ausência de corpo dificulta auditoria de critérios. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Alternativa: deck versionado com data/SHA em destaque (o título já leva o SHA). Recomendação: registrar na #181 a natureza de snapshot e a data de obsolescência esperada.

### Dependências e paralelismo

Independente; relacionada ao planejamento MCP (Antony) citado na #181.

### Plano e aceite propostos

Manter snapshot com SHA/data visíveis e fontes. Antes de reutilizar na reunião, confrontar afirmações com fichas posteriores (#129/#153/#160 e demais); menor entrega é nota de atualização, sem reescrever silenciosamente o snapshot.

### Comunicação entre responsáveis

Comunicação insuficiente na PR (corpo vazio) — mitigada pelo contexto da #181.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — apresentar o snapshot antigo como atual esconderia as entregas posteriores; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — números do deck não foram reproduzidos. Como eu explicaria isso para outro pod? — Preservar deck de 23 slides sobre main a289e53, datado 17/09/2026, como artefato histórico e material de discussão; não é estado atualizado após merges de outubro.

### Próxima ação e encerramento

Antony/time a confirmar: escolher manter como histórico ou produzir revisão nova com SHA/corte e limites. Saída verificável é artefato datado coerente com suas fontes; não publicar automaticamente.

<a id="item-524"></a>

## PR#153 — fix(serve,front): the console reads the same rows through either door

Frente: historico. Encaminhamento: historico_integrado_com_followup_delimitado.

### Identidade e estado

PR #153 de Agmar Castro (agmarcastro) — autoria distinta; mergeada em 06/10/2026 20:32 UTC por luanmorenommaciel; head eb449cb, 13 commits, +5364/−124, 63 arquivos; revisor solicitado: sidymar (sem review registrada).

### Intenção e benefício

Sweep da apex-api: uma linha deve ser a mesma linha por qualquer porta (ClickHouse direto no browser vs. API). Quatro+ lugares onde não era, invisíveis para a suíte unitária porque fake devolve o que recebe.

### Feito, faltante e não comprovado

Feito: run não indexado renderizava zero medido (sentinela indexed no CTE; confirmado live: browser -1 != api 0); um formato de timestamp só (ISO 8601 T, ms, UTC, wire.py); QueryFailure em toda tela antes de empty state; badge de fonte http correto; gate six-lane corrigido (detail=full; encontrado ao rodar); C3/C4 overlay com spark.driver.host; console_parity_gate.py live; test_every_console_field_is_projected; entry point E2E console_reflection + console.live.test.tsx; compose/make prod/README para modo http. Faltante (Open declarado): /ask ainda mockup (decisão de produto D-2026-09-23), verify lane não rodada E2E. Não comprovado: CI remota (billing) — toda evidência local. O commit eb449cb também relata imagem DEV anterior à emissão de job_conf e acrescenta aviso do orquestrador quando falta essa linha. É achado operacional histórico do E2E, não incidente novo nesta auditoria.

### Linhagem

13 commits no total; 11 têm trailers Task/Tasks com IDs (T-20260923-*, T-20260929-*, T-20261006-*); reconciliado com fab6620 (base prevalece em findings/transitions/auto; auto leaf parqueado como supersedido); complementa #146 e #151.

### Fontes e corte

Fontes da ficha: corpo/metadados e leitura estática dos diffs registrada nos campos técnicos. Reconciliação 19–20/10: diff/estrutura de console.live e arquivos E2E/VALIDATION selecionados, além do corpo e 13 mensagens de commit. O arquivo integral na main atual não foi relido nesta rodada quando isso não está explicitamente declarado. Leitura de diff não é execução ou revisão integral de todo o produto. Os recibos de CI históricos mantêm o corte próprio.

### Classe e limite da evidência

Prova declarada: serve 314/314, front 166/166, tsc/eslint/build, root gate 14/14; parity gate 17/17 contra stack de infra, 3 jobs reais; E2E 2026-10-06 com job skew_join + AQE skew_split: engine 3 findings, todas as telas verdes em 2 jobs gerados + 1 de julho; mutação-checked contra os 5 defeitos. Classe: execução real (ClickHouse, Spark, API, App) — a mais forte do recorte. Limite: local; CI billing-locked; verify lane E2E ausente; N15 registra limite do oráculo de custo no live test. Conferência estática Codex: console.live usa jsdom e App real contra API; não é navegador real passando por nginx. Resultados locais continuam relatos documentados, não novas execuções observadas pelo Codex.

### Fluxo

Job Spark → collector → ClickHouse → engine → memory → apex-api → console (duas portas) → parity gate compara linhas → telas lidas contra a API.

### Consequências e risco

Risco médio residual: prova é local e datada (06/10); N15 aponta oráculo de indexação ligado à contagem global de plans no live test; auto leaf parqueado pode confundir futuros maintainers. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Alternativa: confiar em suíte unitária (rejeitada — fakes não veem projeção); join_use_nulls (impossível: apex_ro readonly). Recomendação: registrar rechecagem remota pós-billing e tratar N15.

### Dependências e paralelismo

Empilhada sobre #129; revisor solicitado sidymar (sem review); #159 aberta melhora o gate de paridade (#181).

### Plano e aceite propostos

Preservar implementação e relatos em VALIDATION.md; para revalidação, escolher árvore e ambiente, controlar fixture/limpeza e distinguir NOT EXERCISED de PASS. N15 exige oráculo ligado ao job/fingerprint, não contagem global /plans; browser/nginx segue #172 e Verify com linha real tem critério separado. Não fechar esses critérios por suíte unitária verde.

### Comunicação entre responsáveis

Corpo exemplar: separa Fixed/Added/Evidence/Open, cita decisões de produto como decisões (não leaves).

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — comparar só status HTTP não detectaria projeções diferentes das linhas; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — navegador/nginx e Verify com linha real. Como eu explicaria isso para outro pod? — Sweep da apex-api: uma linha deve ser a mesma linha por qualquer porta (ClickHouse direto no browser vs. API). Quatro+ lugares onde não era, invisíveis para a suíte unitária porque fake devolve o que recebe.

### Próxima ação e encerramento

Coordenar N15 com a matriz de prova #156 e fronteira de navegador #172; comparar #158/#159 com #182 antes de alterar a mesma superfície. Responsáveis Pod1/Pod3 a confirmar. #159 é review de gate com efeitos próprios; não é motivo para bloquear todos os estudos.

<a id="item-525"></a>

## PR#160 — ci: lean default CI (cheap PR check, heavy jobs manual/weekly)

Frente: historico. Encaminhamento: historico_integrado_com_followup_delimitado.

### Identidade e estado

PR #160 de Luan Moreno (luanmorenommaciel, owner), mergeada em 08/10/2026; head e6343ca, 1 commit, +97/−56, 2 arquivos (ci.yml reshape + jar.yml novo). Merge pelo próprio autor. Sem reviews.

### Intenção e benefício

CI enxuta: mesmos comandos, menos execuções e jobs — eliminar dupla execução push+PR (~15 job-min → ~2.5–5), jar só quando jar/** muda (JDK 21; JDK 17+21 semanal).

### Feito, faltante e não comprovado

ci.yml agrupa cinco lanes Python e root, mantém Front e repo-checks, restringe pushes a main e filtra docs/md/jar; jar.yml usa JDK21 em eventos de PR/push aplicáveis e JDK17/21 semanal/manual. Gates warning/suíte vazia, quoting e limite service-free anteriores permanecem. O loop continua lanes após falha, mas exit não-zero pula steps posteriores PowerShell/root sem always; #161 trata esse recorte. Estimativas de job-min não são medições.

### Linhagem

1 commit e6343ca pelo owner; explica o avanço da main de c4541a5 (base de evidência da #156) registrado naquela issue.

### Fontes e corte

Fontes da ficha: corpo/metadados e leitura estática dos diffs registrada nos campos técnicos. Reconciliação 19–20/10: diffs dos dois workflows. O arquivo integral na main atual não foi relido nesta rodada quando isso não está explicitamente declarado. Leitura de diff não é execução ou revisão integral de todo o produto. Os recibos de CI históricos mantêm o corte próprio.

### Classe e limite da evidência

DIRETO: diff dos dois workflows e comandos/condições declarados. RELATO: actionlint limpo no corpo. ESTIMATIVA: job-min antes/depois. O recibo por SHA da main registra CI failure e jar schedule success em escopos diferentes; jar verde não valida Python/Front. Não se conclui billing presente, custo financeiro ou aprovação formal a partir do merge pelo owner.

### Fluxo

PR aberta → 1 run, 3 jobs (~2.5 job-min) → verde; jar/** → +jar.yml; semanal → matriz JDK 17+21.

### Consequências e risco

Risco médio: checks renomeados quebrariam required checks futuros (#125) se configurados com nomes antigos; lanes agrupadas dificultam reexecução isolada; JDK 17 só semanal — regressão de compatibilidade Java pode demorar uma semana. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Alternativa: manter 11 jobs (rejeitada por desperdício). Recomendação: ao configurar proteção de main (#125), usar os novos nomes de job; documentar a janela semanal do JDK 17.

### Dependências e paralelismo

Coordenar #161 (execução dos gates após falha), #125 (nomes dos checks/proteção) e #130 (reconciliação de capacidade/causa). #138/#148/#149 são preservadas na configuração final, não sobrescritas semanticamente. Nenhum gate operacional comum foi imposto aos estudos.

### Plano e aceite propostos

Revisar #161 com controle de falha antecipada e evidência da mesma árvore; configurar required checks apenas após decisão #125 com nomes efetivos. Separar prova semanal jar e CI principal. Merge pelo owner é fato de integração, não rito de aprovação explícita ou aceite funcional.

### Comunicação entre responsáveis

Corpo comunica tradeoffs e heads-up de nomes de checks com clareza; estimativas rotuladas como estimativas.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — encerrar o step após lane falha pode pular os gates posteriores, escopo de #161; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — root/PowerShell após falha de lane e prova do perfil efetivo. Como eu explicaria isso para outro pod? — CI enxuta: mesmos comandos, menos execuções e jobs — eliminar dupla execução push+PR (~15 job-min → ~2.5–5), jar só quando jar/** muda (JDK 21; JDK 17+21 semanal).

### Próxima ação e encerramento

Mantenedor a confirmar: revisar #161/#125 e confrontar recibos de runs por SHA/escopo; saída é política e prova específicas, sem pedir novo run semanal já observado só para repetir verificação.

