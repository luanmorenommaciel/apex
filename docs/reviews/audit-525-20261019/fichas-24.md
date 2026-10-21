# Fichas documentais — lote 24

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-231"></a>

## S18 — Compare entre versões do Engine e colapso de AQE_REPLAN

Frente: serve_compare_runs. Encaminhamento: estudar_revalidar_contra_115_antes_de_issue.

### Identidade e estado

S18 é um estudo/decisão do Pod 3/Serve sobre o Compare entre versões do Engine e o colapso de AQE_REPLAN. Sem issue própria; a triagem marcou needs_revalidation e relacionou com a issue luanmorenommaciel/apex#115 (atribuição execution_id→job→stage, aberta, sem assignee). DEC-09 trata atribuição na #115; o destino próprio de compare é uma decisão adicional. Owner a confirmar (Pod 3).

### Intenção e benefício

Problema potencial: compare_findings usa (type, stage_id). Um tipo que o Engine do baseline não podia emitir pode ser apresentado como introduzido; múltiplas linhas da mesma chave podem se sobrescrever. Público: quem compara runs de proveniências distintas. Benefício proposto: distinguir novidade do detector de mudança observada no job, com política explícita. Não foi demonstrado incidente real.

### Feito, faltante e não comprovado

Base: diagnose.py:752 devolve (finding.type, finding.stage_id) como chave e a docstring da linha 769 diz "Diff two runs' findings by (type, stage_id)"; as mensagens finding_introduced/finding_resolved estão nas linhas 803 e 819. Falta: decidir se o compare deve considerar versão do detector e como tratar findings de nível de job. Não comprovado: teste de compare com baseline antigo × atual.

### Linhagem

Linhagem: revisão B-4 item 1 da #127 e decisão 3 do stage-attribution-design → registro S18 (decision_required, depende de E02) → triagem needs_revalidation → relação parcial com #115 → decisão própria de compare ainda pendente. DEC-09 é relacionada à atribuição, não o aceite desse estudo. A #115, segundo C04-13, já distingue conflitos de stages e trata o sentinel -1 de AQE como nível de job; não exige trocar findings de job por stages.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_mcp__diagnose.py.txt. Locadores e recorte: S18 no registro; #115 sentinel de job conforme corpo/comentário; diagnose751–821 dictionaries keyed(type,stage_id). O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO estático: dicts de compare_findings são indexados por (type, stage_id), sem versão do detector. Múltiplas linhas com essa chave se sobrescrevem na construção do dicionário. RELATO: inspeção histórica; efeito em runs reais ou mudança histórica de disponibilidade de tipo não foi reproduzido. PROPOSTA: política de comparabilidade e identidade de findings de job, sem converter stage -1 em stage real.

### Fluxo

Fluxo observado: findings do baseline e do atual —(chave type+stage_id)→ conjuntos —(diferença)→ finding_introduced / finding_resolved / confiança mudou —(MCP/API)→ usuário. Proposto: findings —(chave com versão do detector ou execution_id quando nível de job)→ diff.

### Consequências e risco

Risco estático condicional: baseline gerado por Engine incapaz de emitir um tipo pode produzir finding_introduced sem mudança do job; duas linhas com mesma chave podem colapsar no dict. A mera data anterior ao merge #127 não comprova incapacidade: o tipo já existia em commits anteriores. Frequência e efeito em runs reais não foram medidos.

### Alternativas e recomendação

Recomendado: estudo pequeno que defina (a) tipo novo sem histórico possível como "não comparável", não "introduzido", e (b) chave por execution_id para findings de nível de job; decidir depois se vira issue própria. Alternativas: incluir na #115 (mistura atribuição com semântica de compare); só documentar o limite no output. Reversível.

### Dependências e paralelismo

Pode ser estudado em paralelo à #115; a chave por execution_id para AQE_REPLAN usa o mesmo vínculo que a #115 trata, mas a regra de "tipo não comparável" não depende dela. Não depende de #168.

### Plano e aceite propostos

Estudo mínimo: fixtures de dois runs com conjuntos de tipos suportados declarados e de múltiplos AQE_REPLAN em stage -1; demonstrar colapso sem tratar isso como incidente. Decidir comportamento para detector incompatível, identidade de job e metadados necessários, depois destino próprio acordado. Não impor automaticamente que todo tipo novo seja não comparável.

### Comunicação entre responsáveis

Para outro pod: o compare usa uma chave que pode colapsar findings e não considera a capacidade do detector de cada run. Precisamos escolher controles e política, preservando a relação com #115 e sem afirmar regressão real não observada.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Adicionar só versão à chave poderia transformar mudança de versão em ainda mais introduzidos/resolvidos; identidade e comparabilidade precisam de políticas separadas. Que caso o teste ainda não cobre? Não se comprovou baseline real incapaz de emitir TAIL_OUTLIER nem impacto ao usuário; a fixture deve declarar suporte por versão e preservar stage -1 de nível de job. Como eu explicaria isso para outro pod? O compare usa chave curta e não considera capacidades do detector; a #115 ajuda na identidade, mas não decide sozinha semântica entre versões.

### Próxima ação e encerramento

Próxima ação: Pod3, a confirmar, propõe as duas fixtures e o comportamento de compare sob versões/populações identificadas. Entrada: código e exemplos hipotéticos delimitados. Saída: issue de estudo própria ou complemento explicitamente acordado, com decisão implementar/adiar/rejeitar. DEC-09/#115 é relação com atribuição, não a decisão já tomada sobre compare.

<a id="item-232"></a>

## S19 — list_runs.worst_p99_ms mistura tentativas de stage superadas

Frente: consumidores_tentativa_stage. Encaminhamento: agrupar_em_169_corrigir_apos_politica.

### Identidade e estado

S19 é um bug pequeno do Pod 3/Serve: list_runs.worst_p99_ms mistura tentativas de stage superadas. Agrupado na issue luanmorenommaciel/apex#169 (minuta P-DEC23), aberta, sem assignee. Correção depende da política DEC-23. Owner a confirmar (Pod 3).

### Intenção e benefício

Problema estático: RUNS_SQL diagnóstico usa max(p99) sobre todas as linhas, enquanto STAGES_SQL escolhe argMax por ts. Pode haver p99 de observações distintas na lista e no diagnóstico. A lista da Console usa rollup próprio com run_outcomes.task_time_ms; não é demonstrado que receba worst_p99_ms.

### Feito, faltante e não comprovado

Base: serve/src/apex_mcp/ch.py:117 "max(task_duration_p99_ms) AS worst_p99_ms" no rollup de runs (o comentário da linha 1025 liga a coluna ao RunSummary do MCP). Feito (relato): R1/Q1 de 30/09 em clickhouse-local 24.8.14.39 sem rede reproduz 7/7 linhas NA-09: worst_p99_ms 30000 contra p99 1098 em STAGES_SQL no mesmo job; C5 separa argMax(ts) de maior stage_attempt; C7 mostra que a Console pode exibir attempt 1 com p99 da tentativa 0. Falta: decisão DEC-23 e o patch. Não comprovado: emissão Spark real de tentativas falhas (TS24).

### Linhagem

Linhagem: NA-09 de 25/09 (achado secundário) → lane A de 29/09 → R1/Q1 de 30/09 (manifesto 73/73) → lane3 de 01/10 (C9/C9r) → registro S19 → minuta P-DEC23 → #169 → decisão [ausente] → patch ts46a [ausente].

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_mcp__ch.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_api__routes__diagnostics.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/front__src__data__queries.ts.txt; fontes/batch-revalidated-fes-sources/lane3-dec23-24-report.md. Locadores e recorte: S19/#169; ch:55–123 e Console runRollup próprio; diagnostics TOOL_ROUTES/list_runs; front queries54–128; lane3. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: max sem seleção de tentativa. RELATO: reprodução em clickhouse-local com fixture. INFERÊNCIA: com retries reais, a listagem superestima a cauda. DECISÃO PENDENTE: seletor (DEC-23). Sem execução nesta revisão.

### Fluxo

Fluxos distintos: todas as linhas spark_events → RUNS_SQL max(p99) → MCP list_runs e GET /v1/diagnostics/runs. Eventos → STAGES_SQL argMax(ts) → diagnóstico. Console GET /v1/runs usa outra projeção/rollup de run_outcomes; não se transfere worst_p99_ms a ela.

### Consequências e risco

Sem correção, a listagem pode apontar como pior um run cuja cauda veio de uma tentativa descartada, levando a investigar o job errado; impacto de triagem, sem incidente. Confiança alta.

### Alternativas e recomendação

Recomendado: depois de DEC-23, calcular worst_p99_ms sobre a tentativa selecionada por stage, com o mesmo seletor de STAGES_SQL. Alternativas: manter max e rotular "pior tentativa observada" (barato, honesto, diferente do diagnóstico); expor as duas métricas. Reversível.

### Dependências e paralelismo

Depende de DEC-23 (#169). Mesma família de E24 e S14; a mudança é pequena e pode ser a primeira folha depois da decisão. Não depende de #115.

### Plano e aceite propostos

Após DEC-23, ajustar o rollup diagnóstico e controlar retry com valores distintos, job sem retry e duplicata; conferir MCP list_runs e sua rota diagnóstica HTTP com os mesmos argumentos. Não exigir que uma coluna inexistente na Console tenha o mesmo valor.

### Comunicação entre responsáveis

Para outro pod: a lista diagnóstica MCP/HTTP pega o maior p99 de todas as observações, e STAGES escolhe por ts. A Console tem outro rollup; o seletor comum precisa ser decidido na #169.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Trocar max por um seletor sem decisão poderia ocultar uma tentativa relevante ou manter rótulo/métrica incoerentes; o significado da métrica precisa ser explícito. Que caso o teste ainda não cobre? A fixture histórica não comprova emissão Spark real; faltam teste incorporado e equivalência MCP/rota diagnóstica após a política escolhida. Como eu explicaria isso para outro pod? worst_p99 pertence à lista diagnóstica, enquanto Console tem rollup próprio; alinhar seleção dentro da superfície correta evita uma falsa paridade.

### Próxima ação e encerramento

Próxima ação: Pod3 prepara a fixture e a proposta em paralelo; a mudança segue a política escolhida em DEC-23/#169. Entrada: relatos R1/Q1 e código das superfícies. Saída: patch e controle discriminante para RUNS_SQL e consumidores afetados. Encerramento: métricas/rótulos obedecem à política escolhida; não basta igualar ao STAGES_SQL atual sem reconciliar seu seletor.

<a id="item-233"></a>

## S20 — Serve classifica falhas do ClickHouse e recupera probes de metadata

Frente: serve_erros_clickhouse. Encaminhamento: encerrar_pr_integrada.

### Identidade e estado

S20 é uma correção do Pod 3/Serve implementada pela PR luanmorenommaciel/apex#140 "fix(serve): classify ClickHouse failures and retry failed metadata probes" (head b149569, quatro commits 6cb31ea, 430ab67, ae7a462 e b149569), integrada em 2026-10-06T20:14:32Z no merge 04ffcf6. Origem R2 F-2. Sem assignee.

### Intenção e benefício

Problema: table_exists, memory_tables_present e findings_columns tratavam qualquer ApexStoreError como ausência e a guardavam em cache; autenticação falha e database inexistente viravam "schema_missing", e o mesmo store não se recuperava depois de uma falha transitória. Público: operadores que diagnosticam a apex-api e o MCP. Ganho: erro operacional deixa de parecer schema ausente e o store se recupera.

### Feito, faltante e não comprovado

Base lida: findings_columns, table_exists e memory_tables_present só atribuem cache após _query responder; _query sanitiza e propaga erro. _sanitize separa códigos de schema (16/47/60), acesso (inclui497/516), database ausente81 e falha sem classificação. Relatos TS07/TS14 permanecem históricos; não houve prova real de usuário negado só em system.columns nesta revisão.

### Linhagem

Linhagem: R2 F-2 de 27/09 (integração #129×#131) → plano TS07 → commits 6cb31ea a b149569 → PR #140 (28/09) → conflito de testes com #129 em serve/tests/test_ch.py resolvido no merge → 11 check-runs sem steps → merge 04ffcf6 em 06/10. Sem follow-up próprio.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_mcp__ch.py.txt. Locadores e recorte: S20/#140; ch findings_columns791–818/table_exists854–881/memory884–916/_query1164–1171/_sanitize1195–1262. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO estático: classificação por código e ausência de cache quando _query levanta erro. RELATO: aceite de folhas e controles históricos. Com código497, _sanitize retorna clickhouse_access_denied e o probe interrompe a leitura; não se comprovou cenário de grants parcial num servidor real.

### Fluxo

Fluxo observado: probe de metadata —(ApexStoreError)→ classificação —(ausência real)→ schema_missing; —(autenticação, database inexistente, 497)→ erro operacional sem cache —(nova chamada)→ novo probe. Antes: qualquer erro —(cache de ausência)→ schema_missing permanente.

### Consequências e risco

Sem ação, a proteção está na main. O limite é a hipótese de ClickHouse que nega apenas system.columns, não testada em servidor real; nesse caso o comportamento escolhido pode bloquear leituras que teriam funcionado. Confiança alta no merge, média no comportamento real.

### Alternativas e recomendação

Recomendado: encerrar S20. Se a hipótese de permissão parcial for relevante para um cliente, prova pequena com usuário sem acesso a system.columns é o passo seguinte, fora deste ID. Reversível.

### Dependências e paralelismo

Nenhuma dependência para encerrar. A prova opcional de permissão parcial em system.columns é independente de #172 (nginx/browser) e de #156 (paridade de transporte), e pode ser feita por quem tiver um ClickHouse descartável.

### Plano e aceite propostos

Condição de não ação: nenhum passo neste ID. Opcional: registrar como pergunta aberta a prova com usuário sem acesso a system.columns. Reabrir se erros operacionais voltarem a ser reportados como schema_missing.

### Comunicação entre responsáveis

Para outro pod: "Desde a #140, falha de autenticação ou database inexistente não aparece mais como 'schema ausente', e o store tenta de novo depois de uma falha passageira."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Cachear falha como ausência faria uma falha transitória parecer schema ausente durante a vida do store. Que caso o teste ainda não cobre? Permissão negada apenas em metadata não foi testada em servidor real; leitura estática do código497 não demonstra comportamento de grants da imagem. Como eu explicaria isso para outro pod? A #140 distingue erro operacional de ausência respondida e tenta o probe novamente após falha, sem transformar acesso negado em pedido de DDL.

### Próxima ação e encerramento

Próxima ação: confirmar encerramento de S20. Owner: nenhum necessário. Entrada: estado da #140. Saída: linha S20 "entregue em 04ffcf6". Encerramento: imediato.

<a id="item-234"></a>

## S21 — Serve retém veredito e magnitude com piso inválido

Frente: serve_piso_ruido. Encaminhamento: encerrar_pr_integrada_com_lacuna_na_projecao.

### Identidade e estado

S21 é uma correção do Pod 3/Serve implementada pela PR luanmorenommaciel/apex#144 "fix(serve): withhold verdicts from invalid noise floors" (head 82be2e2, empilhada sobre #135), integrada em 2026-10-06T20:11:15Z no merge afaffb9. Sem assignee. Zero e igualdade seguem em DEC-05.

### Intenção e benefício

Problema: piso negativo resolvia delta de métrica no compare, e o replay renderizava magnitude com piso negativo ou NaN, descrevendo inf%/nan% como piso medido. Público: quem lê compare, recall e veredito de replay. Ganho: nenhuma adjudicação com piso inválido; piso omitido e zero preservados.

### Feito, faltante e não comprovado

Base: _valid_noise_floor em diagnose.py:668-673 exige não nulo, finito e ≥ 0, e é usado no compare (linha 690) e na narração (linha 1360). Lacuna encontrada nesta revisão, fora do escopo literal da #144: a projeção FIX_VERIFICATION_SQL que alimenta a Console e a /v1 (serve/src/apex_mcp/ch.py:420-431 e front/src/data/queries.ts:293-299) calcula runtime_certified como abs(delta) > piso e unresolved só para NULL ou abs(delta) ≤ piso, sem exigir piso finito e não negativo; o DualVerdictPanel.tsx (linhas 37-39 e 98) exibe esses campos. Com piso negativo armazenado, a projeção certificaria. Não comprovado: existência de tal linha.

### Linhagem

Linhagem: relatório apex-serve-invalid-floor-pr144 → PR #144 (29/09, base 474284c da #135) → casos novos falhando antes (Serve 243 → 261, relato) → sem check-runs (empilhada) → merge afaffb9 em 06/10. Paralelos: F21/#145 (Verify) e S22/#143 (API). Elo ausente: nenhuma das três PRs alterou a projeção da Console, e S23/#146 só fixa a paridade textual entre as duas cópias.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_mcp__diagnose.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_mcp__ch.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/front__src__data__queries.ts.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/verify__src__apex_verify__models.py.txt. Locadores e recorte: S21/#144; diagnose668–692/1351–1376; ch412–442 e queries282–312; modelo Verify to_row396–429. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO estático: _valid_noise_floor exige finito e >=0 em compare/narração; as duas projeções SQL não contêm essa condição. Com delta não nulo e piso negativo, o predicado > pode certificar. NaN/inf no ClickHouse, linha persistida e escritor efetivo não foram demonstrados; não se deduz semântica universal de IEEE. DECISÃO PENDENTE: defesa da projeção no contrato #117.

### Fluxo

Fluxo observado: linha de fix_verifications —(noise_floor_pct)→ (a) diagnose _valid_noise_floor —(inválido)→ "invalid noise floor … not reportable"; (b) FIX_VERIFICATION_SQL —(sem validação)→ runtime_certified/runtime_verdict —(/v1 e Repository)→ DualVerdictPanel. Os dois caminhos podem divergir para pisos inválidos.

### Consequências e risco

Risco condicionado à existência de linha persistida com piso inválido: a projeção pode divergir da narração protegida. A probabilidade não foi medida e a revisão não prova ausência universal de escritor ou ocorrência do caso.

### Alternativas e recomendação

Recomendado: encerrar S21 como entregue e registrar a lacuna da projeção na #117 (ou numa folha pequena dela), aplicando na SQL a mesma condição de _valid_noise_floor nas duas cópias, mantendo a paridade da #146. Alternativas: validar no Repository do Front (corrige só a Console, não a /v1); confiar no escritor futuro (frágil). Reversível.

### Dependências e paralelismo

Encerrar S21 não depende de nada. A correção da projeção depende só de decisão no contrato de piso (#117/DEC-05) e deve mudar Front e Serve juntos por causa do guard de paridade S23/#146.

### Plano e aceite propostos

Passos mínimos para a lacuna: (1) registrar na #117 com as linhas citadas; (2) mudança nas duas cópias de FIX_VERIFICATION_SQL exigindo isFinite(piso) e piso ≥ 0 para certificar e direção; (3) teste com linhas de piso negativo, NaN, zero e NULL; (4) guard de paridade continua verde. Aceite: nenhuma certificação com piso inválido em nenhum consumidor.

### Comunicação entre responsáveis

Para outro pod: "O Serve já não narra nem compara com piso inválido (#144), mas a query que alimenta a Console e a /v1 ainda certificaria com piso negativo. É uma lacuna estática a tratar no contrato #117, nas duas cópias ao mesmo tempo."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Corrigir só o Front deixaria a projeção Serve/API com outra regra; confiar apenas no produtor não cobre linhas externas ou históricas inválidas. Que caso o teste ainda não cobre? Não há linha persistida observada nem execução SQL para NaN/inf; a lacuna negativa é estática e precisa controles reais se a correção for implementada. Como eu explicaria isso para outro pod? A #144 protege narração/compare; as duas cópias SQL compartilham outra superfície sem a mesma guarda, que a paridade textual não valida semanticamente.

### Próxima ação e encerramento

Próxima ação: Codex/owner do contrato (a confirmar) confirma a lacuna e decide registrá-la na #117. Entrada: linhas citadas no campo 3. Saída: folha pequena ou critério na #117. Encerramento de S21: imediato; a lacuna encerra com a projeção corrigida ou decisão explícita de aceitar.

<a id="item-235"></a>

## S22 — API HTTP rejeita noise_floor_pct negativo ou não finito

Frente: serve_api_http. Encaminhamento: encerrar_pr_integrada.

### Identidade e estado

S22 é uma correção do Pod 3/API implementada pela PR luanmorenommaciel/apex#143 "fix(api): reject invalid HTTP noise floors" (head 8233763, empilhada sobre a branch da #129), integrada em 2026-10-06T20:11:24Z no merge e9546a1. Origem: probe R4 de 29/09. Sem assignee.

### Intenção e benefício

Problema: /v1/runs/{id}/comparison e /recall aceitavam e repassavam -0.1, nan, inf e -inf como noise_floor_pct; além disso o parâmetro HTTP é fração (0.159 = 15,9%), enquanto o replay usa pontos percentuais. Público: integrações que chamam a API. Ganho: 422 antes do dispatch para piso inválido; zero, omitido e fração válida preservados.

### Feito, faltante e não comprovado

Feito: validação integrada; rotas diagnósticas em serve/src/apex_api/routes/diagnostics.py na base. Relato: 8 inválidos retornavam 200 e 6 válidos passavam; após o patch, 305 testes Serve em TestClient. Falta neste ID: nada. Não comprovado: servidor/nginx reais (S03), MCP stdio e recall_similar_runs fora do teste, CI. A diferença de unidade fração × percentual continua sendo um ponto do contrato #117.

### Linhagem

Linhagem: relato R4 → PR #143 sobre branch histórica da #129 (fab6620 citado no registro) → testes TestClient relatados → objeto capturado base fa0951fe76192648025d1f9ffbe63dd06b5b9e51 → merge e9546a1. O SHA histórico da pilha não deve substituir a base capturada; unidade/zero seguem em DEC-05.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_api__routes__diagnostics.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_mcp__diagnose.py.txt. Locadores e recorte: S22/#143; diagnostics NoiseFloorParam36–48 e rotas; diagnose _resolves668–692/replay1351–1376. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO estático: NoiseFloorParam usa Query ge=0 e allow_inf_nan=False nas rotas comparison/recall, com descrição de fração. RELATO: oito inválidos, seis válidos e 305 testes. Sem execução nesta revisão; igualdade/unidade/zero permanecem decisão de compatibilidade.

### Fluxo

Fluxo observado: cliente HTTP —(noise_floor_pct como fração)→ validação da rota —(inválido)→ 422; —(válido)→ call_tool compare_runs/recall —(fração)→ diagnose. Replay —(percentual)→ narração. Duas unidades para o mesmo nome de conceito.

### Consequências e risco

Sem ação, a proteção está na main. O risco residual é de unidade: alguém passar 15,9 achando que é percentual e obter um piso de 1590%; não é defeito da #143, é ambiguidade de contrato. Confiança alta.

### Alternativas e recomendação

Recomendado: encerrar S22 e levar a normalização de unidade ao contrato #117 (nome do parâmetro explícito, por exemplo noise_floor_fraction, ou validação de faixa). Alternativa: documentar só na OpenAPI. Reversível.

### Dependências e paralelismo

Nenhuma dependência para encerrar. A normalização de unidade fração × percentual é parte do contrato #117 e independe de #171 (exposição/token) e #172 (nginx/browser); pode ser decidida junto com DEC-05.

### Plano e aceite propostos

Para o resíduo: decidir unidade única ou nomes explícitos e exemplos de conversão. Se for escolhida faixa máxima, justificá-la e controlar seus limites; não presumir que toda fração >1 seja inválida sem contrato. A correção integrada de negativo/não finito permanece separada.

### Comunicação entre responsáveis

Para outro pod: "A API recusa piso negativo ou não finito com 422 (#143). Atenção: na API o piso é fração, no replay é percentual; isso ainda precisa ficar explícito no contrato."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Interpretar 15,9 como fração produz piso de 1590%; impor teto sem decisão também poderia rejeitar variação válida. Que caso o teste ainda não cobre? TestClient é relato in-process, não servidor/nginx reais; a revisão não prova uso correto de unidades por todos os clientes. Como eu explicaria isso para outro pod? A API rejeita negativo/não finito antes do dispatch; fração HTTP e percentual de replay precisam nomenclatura/conversão explícitas no contrato.

### Próxima ação e encerramento

Próxima ação: confirmar encerramento de S22 e anotar a questão de unidade na #117. Owner: Pod 3 (a confirmar). Entrada: PR #143 e ficha #117. Saída: linha S22 encerrada com resíduo de unidade em #117. Encerramento: imediato.

<a id="item-236"></a>

## S23 — Guard estático de paridade da projeção fix_verifications Front×Serve

Frente: serve_paridade_projecao. Encaminhamento: encerrar_pr_integrada_paridade_textual.

### Identidade e estado

S23 é um teste do Pod 3/Serve implementado pela PR luanmorenommaciel/apex#146 "test(serve): pin fix_verifications projection parity with the front" (head 2e0e102, aberta por gustocezar em 30/09, empilhada sobre a #129), integrada em 2026-10-06T20:11:28Z no merge 59967a3. Sem assignee.

### Intenção e benefício

Problema: a #129 replicou no Serve a projeção de certificação do Front; sem guard, as duas cópias poderiam divergir silenciosamente e a /v1 mostraria outro veredito que a Console direta. Público: Pods 1 e 3. Ganho: qualquer diferença além do nome do binding falha o teste.

### Feito, faltante e não comprovado

Base: as duas cópias são textualmente equivalentes nas partes lidas (ch.py:420-431 e queries.ts:293-299 têm as mesmas condições de runtime_certified e runtime_verdict). Feito (relato): teste focado 2/2, três mutações de fronteira que falham só no guard, suíte 291 passed. Limite importante: paridade textual preserva também a lacuna comum — nenhuma das cópias valida piso finito e não negativo (ver S21) — e não decide igualdade (H-7). Não comprovado: execução das queries em ClickHouse.

### Linhagem

Linhagem: Lane C sugere o guard → Lane B implementa (B-parity) → PR #146 (30/09, +56 em um arquivo) → revisão Codex do pacote B e teste focado reexecutado (relato) → sem check-runs (empilhada) → merge 59967a3. Follow-up: qualquer mudança de regra deve alterar as duas cópias.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-revalidated-fes-sources/serve__tests__test_projection_parity.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_mcp__ch.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/front__src__data__queries.ts.txt. Locadores e recorte: S23/#146; teste de projeção integral; ch412–442 versus queries282–312. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: teste exige igualdade literal após a única troca de binding; cópias lidas têm mesmos predicados e mesma lacuna de piso inválido. RELATO: duas asserções executadas e mutações históricas. Esta revisão não executou teste nem SQL; paridade não prova correção da regra.

### Fluxo

Fluxo lido no teste: extrai literal FIX_VERIFICATIONS do TS → substitui somente {finding:String} por {finding_id:String} → exige igualdade literal com FIX_VERIFICATION_SQL. Outro teste exige exatamente um binding por cópia. Whitespace, ordem e predicados não são normalizados; SQL não é executada.

### Consequências e risco

Sem ação, o guard continua protegendo contra deriva. O risco é ler paridade como correção da regra: as duas cópias podem estar igualmente erradas. Confiança alta.

### Alternativas e recomendação

Recomendado: encerrar S23. Para o futuro, gerar as duas cópias de uma fonte única eliminaria a necessidade de paridade, mas exige build compartilhado entre TS e Python, o que não se justifica agora. Reversível.

### Dependências e paralelismo

Nenhuma dependência para encerrar. A futura correção da lacuna de piso (S21, dentro da #117) vai depender deste guard para garantir que Front e Serve mudem juntos; o guard não depende de nada.

### Plano e aceite propostos

Condição de não ação neste ID. Reabrir somente se o guard deixar de cobrir alguma coluna da projeção ou se as cópias divergirem na main; ao corrigir a regra de piso, o mesmo teste deve continuar verde com as duas cópias alteradas.

### Comunicação entre responsáveis

Para outro pod: "Há um teste que impede que a projeção de verificação do Serve e a do Front divirjam. Ele garante igualdade de texto, não que a regra esteja certa."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Uma mudança igual nas duas cópias passaria pela paridade mesmo que a regra fosse errada; normalizar outras diferenças enfraqueceria a garantia literal existente. Que caso o teste ainda não cobre? O guard não avalia NaN, piso negativo ou igualdade num ClickHouse; esses casos exigem prova semântica própria se a regra mudar. Como eu explicaria isso para outro pod? A #146 impede deriva literal entre TS e Python, exceto pelo nome do binding; a correção do contrato compartilhado continua responsabilidade da revisão semântica.

### Próxima ação e encerramento

Próxima ação: confirmar encerramento de S23. Owner: nenhum necessário. Entrada: as duas cópias na base. Saída: linha S23 "entregue em 59967a3; paridade textual, sem decidir igualdade nem piso inválido". Encerramento: imediato.

<a id="item-237"></a>

## S24 — Reforçar a paridade dos oito tools com argumentos idênticos

Frente: serve_paridade_transporte. Encaminhamento: agrupar_em_156_executar_revisao_157.

### Identidade e estado

S24 é um teste do Pod 3/Serve: reforçar a paridade das oito tools com argumentos idênticos (Lane F, commit local 7795822). O arquivo serve/tests/test_tool_transport_parity_same_args.py (+72) está na PR luanmorenommaciel/apex#157 "test(serve): pin eight-tool transport parity with identical arguments" (head a3ed972, aberta, 11 checks success do workflow anterior à #160, zero reviews), rastreada pela issue #156. A #163 (head 9a7e4c1, base a branch da #157) adiciona outro caso. Owner da revisão: Pod 3 (a confirmar).

### Intenção e benefício

Problema: o B-4 aceito na TS09B compara job_id distintos; em seis tools o eco do ID mascara uma resposta vazia do lado populado, e o teste passaria mesmo se um transporte devolvesse vazio. Público: quem confia que MCP e HTTP devolvem a mesma resposta. Ganho: paridade presa a preenchido versus ausente com os mesmos argumentos, exigindo conteúdo real em suggest_fix.

### Feito, faltante e não comprovado

#157 contém dois arquivos: test_tool_transport_parity.py (+224) compara call_tool in-process e HTTP TestClient em dados/ausência/indisponibilidade; same_args (+72) compara apenas chamadas _over_mcp populada/vazia com argumentos idênticos e exige proposta concreta para suggest_fix. #163 (+118) é outro controle de hit plan_json usando helpers da #157. Onze success históricos são do head a3ed972/workflow antigo; nenhum teste foi executado nesta revisão.

### Linhagem

Linhagem: Lane C N3 e same-args-control.py → Lane F REPORT e commit 7795822 (árvore 8497e2a) sobre integração local #129+#140+TS09B → publicação dentro da #157 (head a3ed972) → 11 checks success no workflow antigo → review [ausente] → decisão [ausente]. Relação de pilha: #163 sobre a branch da #157 (C04-03), sem checks no head.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/pr157-files.json; fontes/pr157-checks.json; fontes/pr163-files.json; fontes/pr163-checks.json; fontes/batch-revalidated-fes-sources/pr157-test_tool_transport_parity_same_args.py.diff.txt. Locadores e recorte: S24/#157 e #163; diffs integrais dois arquivos #157/+118 #163; checks por head e base da pilha. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: arquivo presente na #157 e checks verdes de workflow antigo. RELATO: mutações M1-M3 e Serve 404/404. INFERÊNCIA: a folha S24 está publicada; o "aceite formal próprio" pedido pelo registro continua ausente. DECISÃO PENDENTE: método de integração da pilha #157/#163. Sem execução.

### Fluxo

Garantias compostas lidas: arquivo +224 → MCP call_tool in-process versus HTTP TestClient com parâmetros equivalentes, estados populado/ausente/indisponível. Arquivo same_args +72 → _over_mcp no populado versus _over_mcp no vazio, exatamente mesmos argumentos e eco igual; não chama HTTP. Nenhum desses caminhos é transporte stdio real ou rede de produto.

### Consequências e risco

Sem a folha, uma regressão em que um transporte devolve vazio passaria pelo teste antigo; com a #157 aberta, essa proteção ainda não está na main. Confiança alta no conteúdo publicado; nenhuma regressão observada.

### Alternativas e recomendação

Recomendado: revisar e integrar a #157 (que contém S24) e decidir a #163 por um dos dois métodos de C04-03: integrar #157 e reposicionar #163, ou validar a pilha combinada antes da main. Diferente da v2, não imponho a ordem única. Alternativa: extrair o arquivo same_args para PR própria (desnecessário; já está coeso na #157).

### Dependências e paralelismo

Independente de #158/#159. A #163 depende dos helpers da #157, não o contrário. Não depende de #117 nem de #130 (os checks antigos existem; prova no workflow atual é escolha do mantenedor).

### Plano e aceite propostos

Passos mínimos: (1) revisão da #157 com foco no arquivo same_args e no controle de vazio; (2) decisão de integração; (3) registrar na #156 que S24 foi entregue pela #157; (4) tratar #163 separadamente. Controle discriminante já descrito: trocar a resposta populada por vazia deve falhar.

### Comunicação entre responsáveis

Para outro pod: "O teste que compara MCP e HTTP com os mesmos argumentos já está na PR #157, aberta. A #163 é outro teste, empilhado sobre a #157; dá para integrá-las em sequência ou validar a pilha junta."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Comparar job_id diferentes pode fazer o eco do argumento mascarar duas ausências; exigir conteúdo com mesmos argumentos remove essa saída fácil. Que caso o teste ainda não cobre? same_args não chama HTTP; o arquivo vizinho é que compara transportes in-process, e nenhum comprova MCP stdio real ou ClickHouse de produto. Como eu explicaria isso para outro pod? S24 está publicada dentro da #157 como controle de conteúdo com argumentos iguais; a #163 depende dos helpers, e integração da pilha tem duas sequências possíveis.

### Próxima ação e encerramento

Próxima ação: revisor Serve e mantenedor (a confirmar) revisam a #157. Entrada: head a3ed972 e checks existentes. Saída: decisão de integração e nota na #156. Encerramento de S24: #157 integrada (ou fechada com motivo) e registro do aceite da folha.

<a id="item-238"></a>

## X01 — Ratificar fronteira HTTP/BFF e sequência (#122)

Frente: arquitetura_ask_http. Encaminhamento: decidir_em_122_reenquadrado_sobre_api_v1.

### Identidade e estado

X01 é a decisão cross-pod de ratificar a fronteira HTTP/BFF do Ask e a sequência de publicação atômica, representada pela issue luanmorenommaciel/apex#122 "[Decision][Cross-pod] Ratify the Ask HTTP/BFF boundary and atomic publication sequence", aberta, sem assignee e sem comentários no snapshot. Decisão do mantenedor (DEC-07), owners Front/Serve a confirmar. #129 é referência histórica, não implementa X01.

### Intenção e benefício

Problema: a #122 nasceu da fronteira #102 (browser→nginx→ClickHouse) e propunha um BFF para o Ask; depois a #129 integrou uma apex-api /v1 com token para todas as leituras, decidida segundo o corpo da #129 na Weekly Sync de 15/09, mas sem /ask. Sem reenquadrar, o time pode manter dois desenhos HTTP concorrentes. Público: Pods 1 e 3 e quem implementar o Ask. Ganho: um único caminho HTTP decidido para o Ask.

### Feito, faltante e não comprovado

Base c3c3ea3: a apex-api /v1 e rotas Resources/Diagnostics existem; #129 integrada em 06/10, com /ask expressamente fora da PR. O corpo relata decisão da Weekly Sync de 15/09, sem ata lida. #122 mantém aberta a decisão sobre transporte, perfis, auth, owners, ordem contrato→Serve→Front e prova necessária. Não se demonstrou entrega do Ask neste recorte.

### Linhagem

Linhagem: fronteira #102 → R2 T18/H03b e inventário ask-v2 → issue #122 → PR #129 integrada em 06/10 (outra fronteira) → candidato Ask V2 preservado localmente (X11) com conflito de 6 arquivos e 2 modify/delete contra fab6620 (relato) → decisão [ausente]. Elo ausente: registro público da decisão da Weekly Sync.

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/primary-public-selected.json issues[122] (corpo integral: proceed/defer/reject, fronteiras local/shared, oito tools e critérios) e pulls[129] (merged_at 2026-10-06T19:56:50Z, merge 83a9624…, relato da Weekly Sync e /ask fora); fontes/batch-revalidated-xldd-sources/code/serve__src__apex_api__routes__diagnostics.py; fontes/batch-revalidated-xldd-sources/code/serve__src__apex_api__routes__resources.py; fontes/batch-revalidated-xldd-sources/selected-register-matrix.json ID X01.

### Classe e limite da evidência

FATO OBSERVADO: /v1 integrada, /ask ausente, #122 sem comentários. RELATO: decisão da Weekly Sync; conflito do candidato. DECISÃO PENDENTE: DEC-07 (Ask sobre a /v1, BFF separado ou adiar). Sem execução.

### Fluxo

Fluxo proposto a decidir: cliente Ask —(envelope/intenção autenticados)→ fronteira same-origin —(adaptador HTTP sobre camada de serviço)→ tools APEX —(resultado com estados honestos)→ cliente. Uma rota na /v1 existente é alternativa; o /api/v2/ask e o perfil shared constam da #122. SDK/provedor LLM é lacuna relatada pela #129, não pré-requisito provado de toda adaptação HTTP das tools.

### Consequências e risco

Sem decisão, o candidato Ask V2 continua parado e quem retomar pode reimplementar leituras HTTP que a /v1 já oferece, ou expor uma segunda credencial. É risco de retrabalho e de fronteira, não incidente. Confiança alta.

### Alternativas e recomendação

Recomendado: confrontar #122 com a /v1 integrada e registrar se a solução reaproveita a API, mantém adaptador separado ou é adiada. Definir explicitamente autenticação, perfis e custódia de credenciais; se houver LLM, decidir seu provedor/chave. O pedido de decisão não autoriza deploy. Alternativas conservam trade-offs de isolamento versus duplicação de fronteiras.

### Dependências e paralelismo

A decisão pode ser estudada em paralelo a #115/#117: a #122 pergunta se pode expor resultados com atribuição explicitamente indisponível. Preservar contratos e estados de recusa é condição de implementação, não exigir fechamento integral das duas issues para discutir transporte. #171 informa a questão de token, sem ser resolução automática.

### Plano e aceite propostos

Passos: (1) comparar fronteiras e critérios da #122 com /v1; (2) registrar proceed/defer/reject, rationale, perfis, owners, ordem e evidência exigida; (3) se proceed, folhas contrato→Serve→Front reconciliadas com a API, com controles proporcionais de auth e preservação das tools; (4) validar cada árvore realmente integrada. Aceite deste ID: todos os critérios de decisão da #122 satisfeitos ou revisados explicitamente, não só uma palavra proceed.

### Comunicação entre responsáveis

Para outro pod: “A #129 entregou uma API e excluiu /ask; a #122 ainda decide perfis, ownership, autenticação e publicação do Ask. Devemos reconciliar os dois desenhos antes de implementar; a decisão da Weekly Sync é um relato no corpo da PR.”

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere manter duas fronteiras de autenticação para o Ask. Que caso o teste ainda não cobre? Os testes da /v1 não cobrem um Ask ainda não implementado. Como eu explicaria isso para outro pod? Explique decisão de transporte, opção de LLM e integração como etapas distintas.

### Próxima ação e encerramento

Próxima ação: mantenedor e owners Front/Serve (a confirmar) registram a decisão reenquadrada na #122. Entrada: corpo da #129 e candidato X11. Saída: comentário de decisão. Encerramento: decisão proceed/defer/reject registrada.

<a id="item-239"></a>

## X02 — Contrato de piso e atribuição (#117)

Frente: contrato_piso_atribuicao. Encaminhamento: decidir_guarda_chuva_117_sem_reabrir_correcoes.

### Identidade e estado

X02 é a decisão cross-pod de contrato de piso e atribuição, guarda-chuva da issue luanmorenommaciel/apex#117 "[Verify/Front/Serve] Preservar atribuição e unificar o contrato do piso de ruído", aberta desde 2026-09-11, sem assignee; o mantenedor a estreitou em 2026-09-17 para (a) piso Memory→Serve, (b) amostras de replay e (c) teste de atribuição write→read→render. Decisões DEC-05/DEC-06; owners Verify/Front/Serve a confirmar.

### Intenção e benefício

Problema: regras de piso e atribuição diferem entre consumidores. A busca histórica da #117 não localizou sink naquele head, e a guarda estática atual inspeciona a lane Verify; isso não prova inexistência de escritores externos, linhas antigas ou dados reais. Público: consumidores de vereditos. Ganho: contrato explícito para ausência, inválido, zero, igualdade e atribuição.

### Feito, faltante e não comprovado

Base c3c3ea3: diagnose._replay_measurement usa <, enquanto FIX_VERIFICATION_SQL e queries.ts usam <= para unresolved; _resolves usa razão relativa e replay usa percentual, contratos de contexto que precisam explicitar unidade. Measurement valida piso finito/não negativo, e to_row omite attributable; os DDLs lidos não possuem essa coluna. A projeção SQL lida não repete a validação de piso. PRs parciais integradas não encerram os critérios (a)(b)(c) do mantenedor. Nenhuma ocorrência persistida foi verificada.

### Linhagem

Linhagem: gap documentado em 5b4fc4f → issue #117 (11/09) → estreitamento do mantenedor (17/09) → correções parciais integradas em 06/10 → folhas F02–F11 e decisões DEC-05/DEC-06 (fora deste recorte) → reunião/registro de decisão [ausente] → critérios funcionais (a)(b)(c) [abertos]. O registro previa "reunião de decisão H-1..H-8 + F06"; C04-14 lembra que a reunião não encerra a issue.

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/primary-public-selected.json issue[117] e comentário 5718045230 de luanmorenommaciel (17/09: Memory→Serve, reps e write→read→render); fontes/batch-revalidated-xldd-sources/code/serve__src__apex_mcp__ch.py:424-431; fontes/batch-revalidated-xldd-sources/code/serve__src__apex_mcp__diagnose.py:668-692,1351-1376; fontes/batch-revalidated-xldd-sources/code/front__src__data__queries.ts:294-301; fontes/batch-revalidated-xldd-sources/code/verify__src__apex_verify__models.py:260-279,400-430; fontes/batch-revalidated-xldd-sources/code/infra__sql__032_fix_verifications.sql; fontes/batch-revalidated-xldd-sources/code/verify__ddl__fix_verifications.ddl.sql; fontes/batch-revalidated-xldd-sources/selected-register-matrix.json X02.

### Classe e limite da evidência

FATO OBSERVADO: condições estáticas diferentes na igualdade, contratos de unidade por contexto, omissão de attributable em to_row/DDL e critérios do comentário do mantenedor. RELATO HISTÓRICO: busca de sink no head 5b4fc4f e caso mínimo descrito pela issue. NÃO VERIFICADO: escritores externos, conteúdo do banco e efeito em linhas reais. DECISÃO PENDENTE: contrato e ownership; ausência de writer encontrado não implica ausência de dados.

### Fluxo

Fluxo proposto pelo contrato: escritor (a definir) —(linha com delta, piso, amostras, attributable)→ fix_verifications —(projeção única com a mesma regra)→ Serve /v1, MCP e Console —(veredito igual em todos)→ usuário. Fluxo observado hoje: três regras levemente diferentes sobre a mesma linha.

### Consequências e risco

Sem decisão, consumidores podem divergir em casos de borda (igualdade, piso negativo armazenado, unidade errada) e a atribuição continua sem representação persistida. Impacto real depende de existirem linhas; confiança alta nas divergências estáticas.

### Alternativas e recomendação

Recomendado: tabela de decisão única (estados × resultado esperado por consumidor) aprovada pelo dono do Verify com Front/Serve, aplicada por folhas pequenas; não reabrir as correções já integradas. Alternativas: decidir consumidor a consumidor (mais rápido, perpetua divergência); adiar persistência de atribuição (aceitável se registrado explicitamente, não por omissão).

### Dependências e paralelismo

Estudo e tabela podem começar já, em paralelo às PRs abertas; implementação depende do desenho e, para persistência, da decisão de escritor (DEC-06/F06). #162 não implementa este contrato. Folhas de igualdade e de validação na projeção são independentes da persistência.

### Plano e aceite propostos

Passos mínimos: (1) tabela de estados com unidade explícita; (2) decisão registrada na #117; (3) folhas: igualdade única, validação de piso na projeção (duas cópias + guard #146), normalização de unidade, persistência de attributable se escolhida; (4) cada folha com caso negativo. Aceite: critérios (a)(b)(c) satisfeitos ou escopo alterado explicitamente.

### Comunicação entre responsáveis

Para outro pod: "As correções de piso de setembro estão na main, mas a regra ainda não é única: a igualdade, a unidade e a projeção da Console diferem. A #117 precisa de uma tabela de decisão antes das próximas folhas."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere usar > num consumidor e >= noutro na igualdade. Que caso o teste ainda não cobre? A prova estática não cobre linhas históricas ou escritor externo. Como eu explicaria isso para outro pod? Explique piso, unidade, atribuição e persistência sem inferir inexistência de dados.

### Próxima ação e encerramento

Próxima ação: owner Verify com Front/Serve (a confirmar) produz tabela de decisão e mapeia produtor/persistência no ambiente pretendido. Entrada: código e critérios primários da #117. Saída: decisão e folhas delimitadas. Encerramento: critérios (a)(b)(c) atendidos ou escopo revisto pelo mantenedor.

<a id="item-240"></a>

## X03 — Concluir ADR de correlação de origem

Frente: arquitetura_privacidade. Encaminhamento: encerrar_superado_por_p07.

### Identidade e estado

X03 é o item seed "Concluir ADR de correlação de origem" (decisão cross-pod). O registro já o marcava superado, com successor P07: a mesma unidade de trabalho é a PR luanmorenommaciel/apex#133, integrada em 2026-10-06 (merge 663f04c), que adicionou docs/architecture/ADR-004-SOURCE-CORRELATION-BOUNDARY.md. Sem owner próprio.

### Intenção e benefício

Intenção original: escrever o ADR de correlação de origem para destravar F4.1 ("qual linha de código produziu este stage") sem vazar caminhos ou código. Público: Pods que coletam telemetria e quem decide privacidade. Ganho: fronteira documentada antes de qualquer implementação.

### Feito, faltante e não comprovado

Feito: o ADR existe na base com "Status: proposed; no implementation is authorized by this document" e está no ADR-INDEX como proposto. Falta, mas em P07/DEC-11 e não aqui: a ratificação pelo dono declarado (Luan). Não comprovado: nada a provar neste ID.

### Linhagem

Linhagem: seed X03 → mesma unidade que P07 → PR #133 → merge 663f04c → ADR-INDEX via #141 → ratificação [ausente, em P07]. Sem elo ausente para o encerramento deste ID.

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/selected-register-matrix.json X03 (superseded, successor P07), fontes/batch-revalidated-xldd-sources/primary-public-selected.json pull[133] (merge 663f04c…, 06/10) e fontes/batch-revalidated-xldd-sources/code/docs__architecture__ADR-004-SOURCE-CORRELATION-BOUNDARY.md (Status: proposed; owner Luan; decisões antes de implementar), fontes/batch-revalidated-xldd-sources/code/docs__architecture__ADR-INDEX.md.

### Classe e limite da evidência

FATO OBSERVADO: ADR-004 presente na base com status proposed e listado no ADR-INDEX como proposto. RELATO: apenas a sucessão X03 → P07 registrada no próprio registro. Nenhuma execução é necessária ou aplicável para catalogar um encerramento por sucessão.

### Fluxo

Fluxo de sucessão: X03 (seed) —(mesma unidade de trabalho)→ P07 —(PR #133, merge 663f04c)→ ADR-004 proposto na main —(decisão do dono declarado)→ aceito ou revisto; o último passo pertence a P07 e não a este ID.

### Consequências e risco

Sem ação, nada muda no produto nem na documentação. O único risco é duplicar a decisão de privacidade em dois IDs; manter X03 encerrado com ponteiro explícito para P07 evita isso. Confiança alta, por leitura direta.

### Alternativas e recomendação

Recomendado: encerrar X03 como superado e manter P07 como portador da decisão. Alternativa: fundir os IDs no registro (perderia a origem seed; não recomendado). Reversível.

### Dependências e paralelismo

Nenhuma dependência para encerrar. A decisão de privacidade do ADR-004 não é gate deste encerramento; ela continua em P07 e com o dono declarado no documento, sem prazo definido.

### Plano e aceite propostos

Condição de não ação: nenhum passo neste ID. Reabrir somente se o ADR-004 fosse removido da main sem substituto ou se surgisse um segundo documento de correlação de origem concorrente.

### Comunicação entre responsáveis

Para outro pod: "X03 e P07 são o mesmo trabalho; o ADR-004 está na main como proposto e a decisão fica com o dono declarado no documento. Procure a decisão em P07, não aqui."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere reabrir o seed ao mesmo tempo que P07. Que caso o teste ainda não cobre? Merge do ADR não testa nem aprova sua implementação futura. Como eu explicaria isso para outro pod? Explique superado como sucessão de ID, preservando a decisão proposta.

### Próxima ação e encerramento

Próxima ação: confirmar encerramento de X03 com ponteiro para P07. Owner: nenhum necessário. Entrada: P07. Saída: linha X03 "superado por P07/#133". Encerramento: imediato.

