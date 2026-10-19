# Fichas documentais — lote 52

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-511"></a>

## PR#140 — fix(serve): classify ClickHouse failures and retry failed metadata probes

Frente: historico. Encaminhamento: historico_integrado_com_followup_delimitado.

### Identidade e estado

PR #140 de gustocezar, mergeada em 06/10/2026 20:14 UTC; head b149569, 4 commits, +543/−49, 5 arquivos. Sem reviews. Histórico S20 (#181).

### Intenção e benefício

Classificar falhas do Serve pelo código de erro estruturado do ClickHouse (não pela classe da exceção) e fazer probes de metadata falhos levantarem erro em vez de virarem 'ausente' cacheado.

### Feito, faltante e não comprovado

Feito: _sanitize por Error.code (16/47/60 schema; 192-195/497/516 access denied; 81 database missing; resto query_failed; conexão primeiro); table_exists/memory_tables_present/findings_columns sem cache em falha; mensagem de acesso negado nomeia credenciais, IP e grants. Faltante: exercício de deployment que nega só system.columns (declarado como possibilidade, não caso observado). Não comprovado: ClickHouse real nesta PR (doubles com classes reais do driver; códigos checados contra ClickHouse 24.8 system.errors).

### Linhagem

4 commits: 6cb31ea (classificação por código), 430ab67 (probes de tabela/memória), ae7a462 (probe de colunas de findings), b149569 (mensagem de acesso negado). Conflito de append com #129 em test_ch.py (resolvido preservando ambos); combinação local com #129/#135–#138 não publicada.

### Fontes e corte

Corpo da PR via API pública em 19/10/2026; ch.py não re-lido em c3c3ea3.

### Classe e limite da evidência

Prova autor-declarada: Serve 308, depois 311 após follow-up; 90 focadas; controles negativos; combinação local 365 Serve/136 Front com reversão gerando 47 falhas; aceite Task-Spec independente. Classe: unitário com doubles fiéis + integração offline não publicada. Limite: sem live ClickHouse; sem CI remota (#130); combinação não é parte da PR.

### Fluxo

Falha ClickHouse → código do driver → classe sanitizada → mensagem acionável; probe falho → raise, nada cacheado → próxima chamada repete probe.

### Consequências e risco

Mudança de semântica estática: falha de metadata agora propaga erro sanitizado, não ausência cacheada; isso pode mudar diagnóstico de um deployment, hipótese não reproduzida aqui. _sanitize registra exceção em stderr com exc_info: sanitização da resposta não certifica política de logs inteira. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Alternativa registrada: degradação graciosa (rejeitada em favor de honestidade). Recomendação: mencionar a mudança em runbook de upgrade (#112 relacionada).

### Dependências e paralelismo

Conflito com #129 (test_ch.py); combinada localmente com #135–#138; #150 testa tratamento dos erros sanitizados nos dois transportes.

### Plano e aceite propostos

Plano: fix em 3 commits + follow-up de mensagem. Resultado/aceite é relato histórico do corpo, não nova concessão nesta revisão; runtime real segue como lacuna de deployment específico.

### Comunicação entre responsáveis

Corpo exemplar na separação entre o que é prova, o que é relato histórico e o que é combinação não publicada.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — cachear falha de probe como ausência esconderia a recuperação posterior; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — deployment real com metadata negada não foi reproduzido. Como eu explicaria isso para outro pod? — Classificar falhas do Serve pelo código de erro estruturado do ClickHouse (não pela classe da exceção) e fazer probes de metadata falhos levantarem erro em vez de virarem 'ausente' cacheado.

### Próxima ação e encerramento

Nenhuma ação imediata; vincular a mudança de comportamento 497 a runbook/upgrade notes.

<a id="item-512"></a>

## PR#141 — docs: add a discoverable index of canonical architecture decisions

Frente: historico. Encaminhamento: historico_integrado_sem_nova_acao_obrigatoria.

### Identidade e estado

PR #141 de gustocezar, mergeada em 06/10/2026 20:20 UTC; head 185a67b, 2 commits, +21, 2 arquivos. Sem reviews.

### Intenção e benefício

Criar índice canônico e link no README; no diff final o índice já inclui ADR-001 a ADR-004 com status declarado, sem renumerar ADRs.

### Feito, faltante e não comprovado

Índice e link integrados; a linha ADR-004 já aparece no diff, apontando a proposta de #133. Não existe lacuna de inclusão a corrigir neste recorte. Manutenção futura do índice é responsabilidade de revisão documental.

### Linhagem

2 commits: 337d5d5 (índice), 185a67b (linha no README). Onda documental com #132–#134; cita #133 como ADR-004 draft.

### Fontes e corte

Corpo da PR via API pública em 19/10/2026; ADR-INDEX.md atual não re-lido.

### Classe e limite da evidência

Prova autor-declarada: documental; 3/3 links resolvem; títulos/status conferem; controles negativos (target quebrado, ADR editado, link morto). Classe: verificação documental com mutação. Limite: índice mantido à mão — deriva futura não impedida.

### Fluxo

Leitor → README → ADR-INDEX → ADR canônico com status declarado.

### Consequências e risco

Risco baixo: índice manual deriva; número histórico de ADR pode ser lido como decisão vigente (o índice explica como ler). Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Alternativa: renumerar/reescrever ADRs (rejeitada). Recomendação: guard simples 'toda ADR nova exige linha no índice' no review checklist.

### Dependências e paralelismo

Conflito textual com #127 (README); #133 adiciona ADR-004.

### Plano e aceite propostos

Plano: docs em 2 commits. Resultado/aceite é relato histórico do corpo, não nova concessão nesta revisão; verificação da linha ADR-004 pendente.

### Comunicação entre responsáveis

Corpo registra resoluções de conflito e o estado draft de #133 com precisão.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — criar outra decisão sem índice dificultaria descobrir qual texto e status valem; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — manutenção do índice ao adicionar nova ADR. Como eu explicaria isso para outro pod? — Criar índice canônico e link no README; no diff final o índice já inclui ADR-001 a ADR-004 com status declarado, sem renumerar ADRs.

### Próxima ação e encerramento

Nenhuma inclusão duplicada. Encerrar o histórico preservando os links; numa nova ADR, conferir descoberta e status no índice. Owner de manutenção a combinar, sem nova issue obrigatória.

<a id="item-513"></a>

## PR#142 — fix(verify): use successful-task duration samples for stage analysis

Frente: historico. Encaminhamento: historico_integrado_com_followup_delimitado.

### Identidade e estado

PR #142 de gustocezar, mergeada em 06/10/2026 19:56 UTC; head 761f2c5, 1 commit, +188/−8, 4 arquivos. Base da pilha #145. Sem reviews.

### Intenção e benefício

Verify ignorava os campos v0.5 successful_task_*; skew e work bounds podiam ser estimados com tentativas falhas/repetidas. Caso representativo: razão 8.96x → 1.10x com amostras de sucesso.

### Feito, faltante e não comprovado

Feito: seleção de p50/p99 de tarefas bem-sucedidas quando successful_task_sample_count > 0, fallback para valores legados em linhas históricas; skew, work bound e filtro de irmãos no piso compartilham a população efetiva; razão legada preservada para auditoria. Faltante: semântica de p50 zero (decisão separada). Não comprovado: replay live em ClickHouse.

### Linhagem

1 commit 761f2c5; base da pilha que leva a #145 (piso inválido na narração). Task-Spec TS45 com aceite independente.

### Fontes e corte

Corpo da PR via API pública em 19/10/2026; código Verify não re-lido.

### Classe e limite da evidência

Prova autor-declarada local e determinística: 15 testes novos (11 falhavam na base), Verify 120 passadas. Classe: teste determinístico local. Limite: sem replay real; decisões #169 (tentativas/população de métricas) podem reabrir interpretação.

### Fluxo

Observação de estágio → há amostras de sucesso? → p50/p99 de sucesso : legado → skew/work bound/filtro de piso na mesma população.

### Consequências e risco

A seleção usa amostra bem-sucedida quando disponível; razão sintética 8.96x→1.10x não demonstra falso positivo nem incidente real. p50 zero e coerência de população têm limites próprios a decidir em N01/#169 conforme o recorte. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Alternativa: manter população legada (rejeitada). Recomendação: alimentar #169 com este caso para validação em dados reais.

### Dependências e paralelismo

Base de #145. Relacionada a #169 (população de métricas) e #117 (piso).

### Plano e aceite propostos

Plano: fix de seleção de população + testes. Resultado/aceite é relato histórico do corpo, não nova concessão nesta revisão; semântica p50 zero pendente como decisão.

### Comunicação entre responsáveis

Corpo claro sobre escopo (sem schema/DDL/zero-duration) e limites.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — misturar p50/p99 de populações distintas mudaria a interpretação do skew; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — p50 zero e mistura de população dependem de decisão. Como eu explicaria isso para outro pod? — Verify ignorava os campos v0.5 successful_task_*; skew e work bounds podiam ser estimados com tentativas falhas/repetidas. Caso representativo: razão 8.96x → 1.10x com amostras de sucesso.

### Próxima ação e encerramento

Vincular o caso 8.96x→1.10x como entrada de evidência para #169.

<a id="item-514"></a>

## PR#143 — fix(api): reject invalid HTTP noise floors

Frente: historico. Encaminhamento: historico_integrado_com_followup_delimitado.

### Identidade e estado

PR #143 de gustocezar, mergeada em 06/10/2026 20:11 UTC; head 8233763, 1 commit, +81/−4, 2 arquivos; empilhada sobre #129. Histórico S22 (#181). Sem reviews.

### Intenção e benefício

As rotas HTTP comparison e recall aceitavam noise_floor_pct de -0.1, nan e ±inf e repassavam às tools MCP com 200; rejeitar na fronteira da API.

### Feito, faltante e não comprovado

Feito: 422 para piso negativo ou não finito; omitido, zero e finito não negativo preservados; OpenAPI passa a dizer que o valor é fração (0.159 = 15.9%). Faltante: nada no escopo. Não comprovado: nenhum servidor iniciado, sem ClickHouse; ambiguidade percentual vs fração não bloqueada (pergunta do corpo).

### Linhagem

1 commit 8233763; empilhada em feat/add_apex_api (#129), retargetizada após merge; irmã da #144 (interpretação MCP).

### Fontes e corte

Corpo da PR via API pública em 19/10/2026; routes/diagnostics.py não re-lido.

### Classe e limite da evidência

Prova autor-declarada: 8 casos inválidos falhavam no head da #129 (200 em vez de 422); com a mudança, Serve 305 passadas (1 warning de deprecação Starlette). Classe: teste de fronteira HTTP com TestClient. Limite: offline; cálculo downstream intocado por design.

### Fluxo

Cliente HTTP → parâmetro noise_floor_pct → validação na rota → 422 ou repasse válido à tool MCP; OpenAPI documenta semântica de fração.

### Consequências e risco

Risco baixo: cliente enviando '15.9' significando 15.9% não é detectado (seria 1590%); mitigação é documentação, não validação. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Manter validação de finitude/não negatividade na fronteira e unidade fração explícita. Se o time quiser aceitar percentuais, decidir conversão/contrato em #117 com exemplos; não impor teto arbitrário de 100%, pois variância pode excedê-lo.

### Dependências e paralelismo

Empilhada em #129; irmã #144; #117 decide o contrato de piso.

### Plano e aceite propostos

Plano: validação de fronteira + testes. Resultado/aceite é relato histórico do corpo, não nova concessão nesta revisão; convenção de unidade segue em #117.

### Comunicação entre responsáveis

Corpo separa fronteira HTTP (#143) de interpretação MCP (#144) com clareza.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — repassar NaN/inf/negativo permitiria adjudicação com piso inválido; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — cliente confundindo fração com percentual. Como eu explicaria isso para outro pod? — As rotas HTTP comparison e recall aceitavam noise_floor_pct de -0.1, nan e ±inf e repassavam às tools MCP com 200; rejeitar na fronteira da API.

### Próxima ação e encerramento

Levar a pergunta de unidade (fração vs percentual) para #117.

<a id="item-515"></a>

## PR#144 — fix(serve): withhold verdicts from invalid noise floors

Frente: historico. Encaminhamento: historico_integrado_com_followup_delimitado.

### Identidade e estado

PR #144 de gustocezar, mergeada em 06/10/2026 20:11 UTC; head 82be2e2, 1 commit, +98/−7, 3 arquivos; empilhada sobre #135. Sem reviews.

### Intenção e benefício

Piso negativo ou não finito no MCP/Serve podia rotular delta como resolvido, renderizar magnitude de replay ou descrever nan%/inf% como piso medido; tratar como inválido para adjudicação em compare, recall e narração de replay.

### Feito, faltante e não comprovado

Piso finito/não negativo é utilizável; inválido retém veredito e magnitude de replay, preservando medições brutas. Zero permanece válido, mas recall e replay conservam semânticas próprias; não há unificação geral das fronteiras. Nenhuma execução remota ou operacional nova nesta auditoria.

### Linhagem

1 commit 82be2e2; empilhada em codex/serve-floor-narration (#135); irmã da #143 (fronteira HTTP).

### Fontes e corte

Corpo da PR via API pública em 19/10/2026; diagnose.py não re-lido.

### Classe e limite da evidência

Prova autor-declarada offline: Serve 243 antes, 261 depois; módulos afetados 99. Classe: teste unitário com fakes. Limite: empilhada — CI não rodou na base; validação de fronteira é da #143.

### Fluxo

Floor recebido pela tool → inválido? → delta mantido como medição, veredito retido; válido → cálculo normal.

### Consequências e risco

Risco baixo: definição de 'piso válido' agora espalhada por duas camadas (#143 fronteira, #144 interpretação) — pergunta do corpo sobre ownership da definição. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Alternativa: confiar só na fronteira HTTP (insuficiente para MCP stdio direto — corretamente rejeitada). Recomendação: declarar a definição canônica em um lugar (#117/contrato).

### Dependências e paralelismo

Empilhada em #135; complementa #143; #117 é a dona do contrato.

### Plano e aceite propostos

Plano: interpretação MCP + testes. Resultado/aceite é relato histórico do corpo, não nova concessão nesta revisão; CI remota condicionada ao retarget (registrado).

### Comunicação entre responsáveis

Corpo honesto sobre a pilha e sobre o que não rodou.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — validar só HTTP deixaria MCP stdio sem a mesma proteção de interpretação; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — coerência de igualdade/zero entre consumidores. Como eu explicaria isso para outro pod? — Piso negativo ou não finito no MCP/Serve podia rotular delta como resolvido, renderizar magnitude de replay ou descrever nan%/inf% como piso medido; tratar como inválido para adjudicação em compare, recall e narração de replay.

### Próxima ação e encerramento

Propor a definição canônica de piso válido como entrega da #117.

<a id="item-516"></a>

## PR#145 — fix(verify): reject invalid noise floors for certification

Frente: historico. Encaminhamento: historico_integrado_com_followup_delimitado.

### Identidade e estado

PR #145 de gustocezar, mergeada em 06/10/2026 20:11 UTC; head 142d6ea, 2 commits, +91/−10, 3 arquivos; empilhada sobre #142. Relacionada a #117 sem fechá-la. Sem reviews.

### Intenção e benefício

Verify podia certificar delta ou passar no controle positivo com piso inválido (ex.: piso negativo certificou -11%; NaN/inf passaram com score 0.90); piso só é utilizável se medido, finito e não negativo.

### Feito, faltante e não comprovado

Piso deve ser medido, finito e não negativo para certificação/controle. Piso inválido produz score floorless e to_row floor nulo; delta bruto permanece. Zero válido preservado. Comparação de significância abs(delta)>=floor deve ser reconciliada com fronteiras diferentes no Serve em #117; follow-up de caveat não ratifica contrato.

### Linhagem

2 commits: 4a35bcf (rejeição de piso inválido), 142d6ea (caveat direcional suprimido). Empilhada em #142; cross-lane: 33 Serve focadas + Front Node 22 com 87.

### Fontes e corte

Corpo da PR via API pública em 19/10/2026; models.py não re-lido.

### Classe e limite da evidência

Prova autor-declarada local: Verify 120 antes, 129 depois; controles reproduziram o comportamento inválido; checks cross-lane no head exato. Classe: teste unitário + revisão independente citada. Limite: sem live; follow-up sem Task-Spec formal.

### Fluxo

noise_floor_pct → validade (medido, finito, >= 0) → certificação/controle : score floorless + floor nulo na linha gravada.

### Consequências e risco

Risco baixo: floor nulo em to_row() apaga a distinção 'nunca medido' vs 'inválido' para auditoria futura; migração 034-039/#170 podem interagir. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Alternativa: corrigir só a comparação de significância (rejeitada — não corrigiria controle, score, texto e floor gravado). Recomendação: gravar motivo do nulo ou documentar a perda.

### Dependências e paralelismo

Empilhada em #142; relacionada a #117 (sem fechar atribuição/igualdade).

### Plano e aceite propostos

Plano: fix em 2 commits. Resultado/aceite é relato histórico do corpo, não nova concessão nesta revisão; decisões #117 pendentes.

### Comunicação entre responsáveis

Corpo registra o achado da revisão independente e a correção — boa prática.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — validar apenas significância deixaria controle/score/persistência incoerentes; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — persistência do motivo de piso inválido versus não medido. Como eu explicaria isso para outro pod? — Verify podia certificar delta ou passar no controle positivo com piso inválido (ex.: piso negativo certificou -11%; NaN/inf passaram com score 0.90); piso só é utilizável se medido, finito e não negativo.

### Próxima ação e encerramento

Registrar a perda de distinção de motivo como follow-up de auditoria (#117/#170).

<a id="item-517"></a>

## PR#146 — test(serve): pin fix_verifications projection parity with the front

Frente: historico. Encaminhamento: historico_integrado_com_followup_delimitado.

### Identidade e estado

PR #146 de gustocezar, mergeada em 06/10/2026 20:11 UTC; head 2e0e102, 1 commit, +56, 1 arquivo (test_projection_parity.py); empilhada sobre #129 (fab6620). Histórico #181 seção 4. Sem reviews.

### Intenção e benefício

A fronteira de piso de runtime_certified/runtime_verdict estava escrita nas duas projeções (Front queries.ts e Serve SQL) sem nada mantê-las em sincronia; fixar paridade byte a byte por teste.

### Feito, faltante e não comprovado

Feito: teste verbatim com única renomeação de binding ({finding}→{finding_id}); segundo teste garante um binding só por lado. Faltante: política de piso segue em #117. Não comprovado: execução das projeções contra ClickHouse (declarado); CI não esperado na base empilhada.

### Linhagem

1 commit 2e0e102; empilhada em #129; guarda citada pela proposta N03 como referência a manter.

### Fontes e corte

Corpo da PR via API pública em 19/10/2026; arquivo de teste não re-lido.

### Classe e limite da evidência

Prova autor-declarada local: baseline 289, 2 novos, full 291; 3 controles negativos em cópias descartáveis falhando só a paridade. Classe: teste estático com mutação. Limite: paridade de texto não valida semântica nem execução.

### Fluxo

Regra de fronteira escrita nos dois lados → teste compara textos → falha em edição unilateral.

### Consequências e risco

Risco baixo: estritez byte-a-byte falha em whitespace inofensivo (pergunta do corpo); proposta N03 precisará editar os dois lados juntos — o guard garante isso. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Alternativa: comparação normalizada (rejeitada; renomeação única permitida). Recomendação: manter estritez; revisitar só se edições cosméticas chatas se tornarem frequentes.

### Dependências e paralelismo

Empilhada em #129 (não mergear antes); #117 dona da política; N03 depende desta guarda.

### Plano e aceite propostos

Plano: 1 arquivo de teste. Resultado/aceite é relato histórico do corpo, não nova concessão nesta revisão; CI remota condicionada ao retarget.

### Comunicação entre responsáveis

Corpo excepcionalmente rigoroso: tabela de evidência, limites de CI da pilha e escopo estático.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — editar uma projeção isoladamente permitiria respostas diferentes pelas duas portas; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — erro semântico compartilhado pelas duas projeções. Como eu explicaria isso para outro pod? — A fronteira de piso de runtime_certified/runtime_verdict estava escrita nas duas projeções (Front queries.ts e Serve SQL) sem nada mantê-las em sincronia; fixar paridade byte a byte por teste.

### Próxima ação e encerramento

Na decisão N03/#117, editar as duas projeções e conservar controle contra edição unilateral. Responsável a combinar Verify/Front/Serve. Saída inclui política aprovada e prova proporcional; byte-paridade isolada não aceita semântica.

<a id="item-518"></a>

## PR#147 — fix(infra): check multiline materialized-view targets

Frente: historico. Encaminhamento: historico_integrado_com_followup_delimitado.

### Identidade e estado

PR #147 de gustocezar, mergeada em 06/10/2026 20:12 UTC; head a07fc04, 1 commit, +5/−2, 1 arquivo (apply_ddl.sh). Sem reviews.

### Intenção e benefício

apply_ddl.sh verificava alvos de materialized views linha a linha; em 010_otel_traces.sql o CREATE MATERIALIZED VIEW e o TO estão em linhas separadas e o alvo escapava da verificação.

### Feito, faltante e não comprovado

Feito: strip de comentários de linha e junção de linhas antes de extrair 'MATERIALIZED VIEW ... TO <target>'; cinco alvos atuais extraídos; nenhuma mudança de DDL ou ordem. Faltante: não é parser SQL geral (declarado); ingestão em migrações repetidas 034–039 permanece aberta. Não comprovado: cobertura de suites Engine/root sobre o script (explicitamente não cobrem).

### Linhagem

1 commit a07fc04; menciona #130 (CI); sem issue própria declarada.

### Fontes e corte

Corpo da PR via API pública em 19/10/2026; apply_ddl.sh atual não re-lido.

### Classe e limite da evidência

Prova autor-declarada: ClickHouse 24.8.14.39 descartável com 5 casos contra script antigo e novo (10/10), incluindo decoy de comentário '--'; bash -n, shellcheck, diff check; suites Engine/root passaram mas não cobrem o script. Classe: execução real contra ClickHouse descartável (rara neste recorte). Limite: escopo de sintaxe atual; suítes formais não cobrem o shell.

### Fluxo

Arquivo de migração → junção de linhas com comentários removidos → extração do alvo TO → verificação de existência → exit 1 nomeando o alvo.

### Consequências e risco

Risco baixo-médio: formas SQL futuras (comentário de bloco, string contendo 'TO') podem quebrar a extração — falha aberta ou fechada não determinada (pergunta do corpo); questão 034–039 segue sem dono. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Alternativa: parser SQL real (fora de escopo). Recomendação: registrar a pergunta 034–039 como issue (provavelmente #170 cobre DDL/verify-ddl).

### Dependências e paralelismo

Independente; relacionada a #170 (DDL e verify-ddl) por tema.

### Plano e aceite propostos

Plano: fix de script + prova em ClickHouse descartável. Resultado/aceite é relato histórico do corpo, não nova concessão nesta revisão.

### Comunicação entre responsáveis

Corpo declara escopo e limites (não é parser geral; suítes não cobrem) com honestidade.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — extrair apenas linha a linha perderia o alvo TO em SQL multilinha; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — sintaxe SQL fora dos formatos atuais. Como eu explicaria isso para outro pod? — apply_ddl.sh verificava alvos de materialized views linha a linha; em 010_otel_traces.sql o CREATE MATERIALIZED VIEW e o TO estão em linhas separadas e o alvo escapava da verificação.

### Próxima ação e encerramento

Preservar histórico e relato dos cinco casos no ClickHouse descartável. Se o time escolher melhorar parser/quietude/replay de DDL, conferir aderência à #170 antes de ampliar escopo. Nova execução requer ambiente próprio e prova de pós-condição, não só parse bem-sucedido.

<a id="item-519"></a>

## PR#148 — docs(ci): clarify that live end-to-end paths are not gated

Frente: historico. Encaminhamento: historico_integrado_sem_nova_acao_obrigatoria.

### Identidade e estado

PR #148 de gustocezar, mergeada em 06/10/2026 20:18 UTC; head d4f85c3, 1 commit, +1/−1, 1 arquivo (comentário no ci.yml). Sem reviews.

### Intenção e benefício

Um comentário do workflow apontava e2e.yml como gate live end-to-end, mas o arquivo não existia; risco de induzir a escolha de checks obrigatórios (#125) sobre proteção inexistente.

### Feito, faltante e não comprovado

Feito: comentário substituído por escopo real (ci.yml service-free, não cobre caminhos live E2E). Faltante: nada. Não comprovado: nenhum job/trigger mudou (intencional); actionlint segue com SC2046 pré-existente (tratado em #149).

### Linhagem

1 commit d4f85c3; relacionada a #125 (proteção de main) e #130; irmã de #149.

### Fontes e corte

Corpo da PR via API pública em 19/10/2026; ci.yml pós-#160 não re-lido.

### Classe e limite da evidência

Prova autor-declarada: workflow faz parse com seis jobs; só ci.yml existia; diff check; actionlint com mesmo warning antes/depois. Classe: verificação documental/estática. Limite: descreve a base a289e53, não o workflow atual.

### Fluxo

Comentário enganoso → comentário corrigido → escolha de required checks informada.

### Consequências e risco

Risco baixo: workflow mudou desde (#160); o comentário corrigido pode ter sido reescrito ou tornado impreciso. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Alternativa: criar o e2e.yml (fora de escopo). Recomendação: ao consolidar com #160, reafirmar o escopo service-free se ainda verdade.

### Dependências e paralelismo

Relacionada a #125/#130; #149 trata o SC2046.

### Plano e aceite propostos

Plano: comentário único. Resultado/aceite é relato histórico do corpo, não nova concessão nesta revisão; revalidar após #160.

### Comunicação entre responsáveis

Corpo preciso sobre o que mudou e o que não mudou.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — prometer E2E inexistente induziria escolha errada de checks obrigatórios; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — runtime live não é coberto por comentário de CI. Como eu explicaria isso para outro pod? — Um comentário do workflow apontava e2e.yml como gate live end-to-end, mas o arquivo não existia; risco de induzir a escolha de checks obrigatórios (#125) sobre proteção inexistente.

### Próxima ação e encerramento

Conferência estática de #160 preserva o limite service-free/live E2E não coberto. Sem alteração adicional exigida neste histórico; selecionar required checks em #125 pelos workflows efetivos.

<a id="item-520"></a>

## PR#149 — fix(ci): quote generated Collector secret argument

Frente: historico. Encaminhamento: historico_integrado_sem_nova_acao_obrigatoria.

### Identidade e estado

PR #149 de gustocezar, mergeada em 06/10/2026 20:12 UTC; head bf308c7, 1 commit, +1/−1, 1 arquivo (ci.yml). Sem reviews.

### Intenção e benefício

actionlint reportava ShellCheck SC2046 no argumento -e com REDACTION_SECRET_KEY gerado para o container de validação do Collector; quotar o argumento completo.

### Feito, faltante e não comprovado

Feito: argumento quotado; formato do segredo (64 hex) e argumento Docker inalterados. Faltante: nada. Não comprovado: nenhum container Collector ou runner iniciado (declarado); segredo com whitespace não observado (possibilidade teórica).

### Linhagem

1 commit bf308c7; separada de #148 (linhas distintas do mesmo workflow); #130 (billing) no contexto.

### Fontes e corte

Corpo da PR via API pública em 19/10/2026; ci.yml pós-#160 não re-lido.

### Classe e limite da evidência

Prova autor-declarada: actionlint passa (falhava em main); YAML parseia com seis jobs; probe de shell mostrou argv idêntico para segredo gerado; diff check. Classe: verificação estática + probe local. Limite: sem execução de container/runner.

### Fluxo

Segredo gerado (64 hex) → argumento -e quotado → argv único → container de validação.

### Consequências e risco

Risco baixo: mudança de formato do segredo no futuro (ex.: com espaços) não tem teste que detecte regressão de quoting. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Alternativa: deixar unquoted (rejeitada — SC2046 bloqueava lint limpo). Recomendação: nenhuma além do registro.

### Dependências e paralelismo

Independente; irmã de #148; ci.yml mudou depois via #160.

### Plano e aceite propostos

Plano: fix de quoting. Resultado/aceite é relato histórico do corpo, não nova concessão nesta revisão; revalidar lint após #160.

### Comunicação entre responsáveis

Corpo separa bem o que foi provado (argv idêntico) do que não foi (container real).

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — retirar aspas voltaria a permitir separação/expansão do argumento pelo shell; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — execução real do container não é provada por argv. Como eu explicaria isso para outro pod? — actionlint reportava ShellCheck SC2046 no argumento -e com REDACTION_SECRET_KEY gerado para o container de validação do Collector; quotar o argumento completo.

### Próxima ação e encerramento

Quoting permanece no workflow de #160. Encerrar a correção histórica com seu relato de argv e limite sem container/runner; nova execução só se outra mudança justificar.

