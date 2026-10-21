# Fichas documentais — lote 34

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-331"></a>

## T-20260920-console-http-repository — T-20260920-console-http-repository.md

Frente: Serve+Front / API HTTP e adaptação da Console (#129). Encaminhamento: encerrada_401_provado_no_repositorio_tela_em_153.

### Identidade e estado

`tasks/done/T-20260920-console-http-repository.md` (blob b6ebd83b). 'Give the console an http data source', M, standard, P2; owner `(none)`; depends_on api-resource-routes. Estado `done`; aceite gravado pelo gate (hmac-sha256-v2, segundos) por `sidymar` no próprio commit de implementação em 2026-09-20/21; a transição para `done` foi feita por outra pessoa (agmarcastro) em 9841119 (2026-09-29, PR #153). Registro da ferramenta do autor, não revisão independente nem autorização atual. Pod provável: Pod 1/Front.

### Intenção e benefício

Um `HttpRepository` implementando o Repository, selecionado por DATA_SOURCE=http, com clickhouse e fixtures ainda disponíveis; 401 vira falha de autenticação e nunca recai no ClickHouse direto.

### Feito, faltante e não comprovado

HttpRepository implementa onze métodos (repository.ts:291–367), seleção pinned/http e auto em369–387. apiGet distingue401 e erros com detail textual (http.ts:78–116); teste de interface usa onze chamadas com retorno null (httpRepository.test.ts:167–202), com casos adicionais de mapeamento. QueryFailure.test.tsx:68–109 monta cinco telas em jsdom com repo rejeitado, sem browser/nginx. git diff no eval só observa worktree corrente.

### Linhagem

decisão do Weekly Sync de 15/09 (relato do corpo da #129; nota de reunião citada em source_note não está no repositório) → serve-api.yaml (approved: true; o PyYAML rejeita o arquivo na linha 20, Codex C04-06) → spec 7fb0879 (2026-09-20) → implementação com accepted:true → done em 9841119 (#153) → PR #129 integrada em 2026-10-06 (merge 83a9624) → fab6620 (auto), 488bd8a (detail), ad03572/d8c7cee (telas, #153).

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260920-console-http-repository.md; fontes/batch-revalidated-specs58-sources/history/T-20260920-console-http-repository.txt; fontes/batch-revalidated-specs58-sources/git/front__src__data__http.ts; fontes/batch-revalidated-specs58-sources/git/front__src__data__httpRepository.test.ts; fontes/batch-revalidated-specs58-sources/git/front__src__data__repository.ts; fontes/batch-revalidated-specs58-sources/git/front__src__data__runtimeConfig.ts; fontes/batch-revalidated-specs58-sources/git/front__src__components__molecules__QueryFailure.tsx; fontes/batch-revalidated-specs58-sources/git/front__src__screens__QueryFailure.test.tsx. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: pinned http não consulta probe/fallback; auto mantém API em401 e pode usar banco/fixture nos demais casos (testes93–165). apiGet captura x-apex-truncated (113–116), mas os métodos de lista extraem só data (repository.ts:294–322). O aviso não faz parte do retorno Repository e se perde antes das telas. Nada executado.

### Fluxo

Fluxo observado: runtimeConfig.dataSource=http → resolveRepository → HttpRepository → fetch /v1/... com Authorization → 401 → ApiAuthError (sem fallback) ; demais → ApiError(status, detail) ; sucesso → linhas.

### Consequências e risco

Existe proteção de401 e UI de erro nos casos lidos, sem prova de nenhum risco atual. Lacuna concreta de contrato: resposta no limite da API carrega aviso de truncagem, mas HttpRepository entrega apenas array às telas. A lista de planos/candidatos/runs pode ser interpretada como completa sem a informação; nenhum caso real de corte foi observado.

### Alternativas e recomendação

Recomendado: manter encerrada com nota da cadeia (fab6620, 488bd8a/#151, ad03572/d8c7cee/#153). Alternativa rejeitada pela PR: recair no ClickHouse após 401, o que restauraria a credencial no navegador. Padrão aplicado: Repository como costura entre fontes.

### Dependências e paralelismo

Nenhuma dependência pendente (rotas de recurso entregues). A prova em navegador real é a #172 e a custódia do token a #171, ambas paralelas e sem bloquear o encerramento.

### Plano e aceite propostos

Manter encerrada a mudança histórica de fonte e corrigir a conclusão de completude. Reuso: prova de autenticação deve citar testes da tela; política de truncagem precisa transporte até o consumidor ou estado equivalente. Destino proposto para a lacuna: nova issue Serve+Front de propagação do aviso de paginação, sem criar issue nesta revisão.

### Comunicação entre responsáveis

Explicar: a fonte HTTP possui testes de roteamento/401 e telas possuem controles de erro em jsdom. O aviso de lista no limite que chega no header é descartado pelo repositório e ainda precisa chegar ao consumidor.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Recair no banco após401 restauraria o acesso que a API recusou. Que caso o teste ainda não cobre? — Lista com x-apex-truncated=true chegando ao usuário com aviso de cobertura parcial; o repositório descarta esse campo. Como eu explicaria isso para outro pod? — Erro de token já tem caminho explícito; truncagem precisa do mesmo cuidado até a tela.

### Próxima ação e encerramento

Ação: nota da cadeia de correções no índice. Owner a confirmar: Front (Pod 1). Entrada: commits citados e C04-05. Saída: nota. Encerramento: já encerrada; a #172 cobre a prova de navegador. Complemento da integração: encaminhar para triagem a perda do indicador truncated nos métodos de lista, preservando a distinção entre header lido em apiGet e aviso exposto ao consumidor. Conferir efeitos da proposta #182 antes de definir correção; nenhuma execução nesta integração.

<a id="item-332"></a>

## T-20260920-readstore-console-queries — T-20260920-readstore-console-queries.md

Frente: Serve+Front / API HTTP e adaptação da Console (#129). Encaminhamento: encerrada_portes_com_correcao_posterior_do_rollup.

### Identidade e estado

`tasks/done/T-20260920-readstore-console-queries.md` (blob 0ac7308b). "Move the console's six remaining queries into ReadStore", M, standard, P2; owner `(none)`; sem dependências. Estado `done`; aceite gravado pelo gate (hmac-sha256-v2, segundos) por `sidymar` no próprio commit de implementação em 2026-09-20/21; a transição para `done` foi feita por outra pessoa (agmarcastro) em 9841119 (2026-09-29, PR #153). Registro da ferramenta do autor, não revisão independente nem autorização atual. Pods prováveis: Pod 3/Serve e Pod 1/Front (nenhum pod no arquivo).

### Intenção e benefício

Dar lar no servidor às seis consultas que só existiam no bundle do navegador (RUN_ONE, JOB_CONF, RUNS_SHARING_SHAPE, PLAN_SHAPES, PLAN_SAMPLE, SHAPE_RUNS) como portes fiéis, com parâmetros ligados — pré-requisito para a Console largar a conexão direta.

### Feito, faltante e não comprovado

Métodos run/job_conf/baseline_candidates/plan_shapes/plan_sample/shape_runs presentes em ch.py:1010–1145; SQL rollup usa sentinela indexed em330–403, compartilhado com queries.ts:101–159. Testes de métodos em892–976 recebem linhas prontas do _ConsoleClient (840–889); teste de igualdade do corpo SQL em1236–1249 é textual, não banco. O sentinela tem controle textual em1210–1223.

### Linhagem

decisão do Weekly Sync de 15/09 (relato do corpo da #129; nota de reunião citada em source_note não está no repositório) → serve-api.yaml (approved: true; o PyYAML rejeita o arquivo na linha 20, Codex C04-06) → spec 7fb0879 (2026-09-20) → implementação com accepted:true → done em 9841119 (#153) → PR #129 integrada em 2026-10-06 (merge 83a9624) → 31f16ff (#153) corrige o rollup nas duas portas.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260920-readstore-console-queries.md; fontes/batch-revalidated-specs58-sources/history/T-20260920-readstore-console-queries.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__ch.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_ch.py; fontes/batch-revalidated-specs58-sources/git/front__src__data__queries.ts. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: valores de caller são enviados em parameters e memória ausente levanta erro. test_new_methods_bind_parameters verifica ausência da string hostil em toda consulta, porém o flag bound só requer ao menos uma chamada com job/fingerprint (943–960); a leitura direta dos métodos completa o mapeamento, sem transformar o eval em prova por método. Ordem oldest-first no fake é pré-arranjada. Relato de correção31f16ff não foi reexecutado.

### Fluxo

Fluxo observado: rota de recurso → ReadStore.run/job_conf/... → SQL ligado (job_id, fingerprint) → ClickHouse → linhas no formato da Console ; memória ausente → memory_unavailable (não lista vazia).

### Consequências e risco

O sentinela de ausência e paridade textual estão presentes. Fake não prova semântica de LEFT JOIN, agregação, ordem ou correção de números reais; paridade de duas cópias também pode preservar um erro comum. Nenhum risco atual universal foi excluído e nenhum incidente foi reproduzido.

### Alternativas e recomendação

Manter encerrada como porte histórico com correção presente. Para uma futura alteração, combinar paridade entre portas com um oráculo independente para ausência/zero e demais fronteiras; a igualdade de cópias é um controle de deriva, não critério suficiente de verdade.

### Dependências e paralelismo

Nenhuma dependência pendente. api-resource-routes depende desta e está entregue; a correção do rollup (#153) também. Paralela à #172 (navegador) e à #171 (token).

### Plano e aceite propostos

Não ação. Nota documental. Para reuso: além de paridade com a Console, exigir caso de fronteira semântica (run não indexado) por consulta portada.

### Comunicação entre responsáveis

Explicar: as consultas têm parâmetros ligados e um corpo de rollup compartilhado entre portas. A comparação evita deriva; decidir se a ausência está representada corretamente requer expectativa independente sobre os dados.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Reescrever o porte sem comparar projeções pode mudar números entre portas. Que caso o teste ainda não cobre? — Semântica real de JOIN/ordem: o fake devolve resultado pronto e duas cópias iguais podem conter o mesmo erro. Como eu explicaria isso para outro pod? — Paridade prova concordância; um caso de fronteira com expectativa independente é que confere o significado.

### Próxima ação e encerramento

Ação: nota da correção posterior do rollup no índice. Owner a confirmar: Serve. Entrada: 31f16ff e test_run_rollup_matches_the_console_sql. Saída: nota. Encerramento: já encerrada; o gate de paridade live é o controle para mudanças futuras nessas consultas.

<a id="item-333"></a>

## T-20260921-console-same-origin-api — T-20260921-console-same-origin-api.md

Frente: Serve+Front / API HTTP e adaptação da Console (#129). Encaminhamento: encerrada_aceita_sobre_nginx_quebrado_corrigido_no_mesmo_dia.

### Identidade e estado

`tasks/done/T-20260921-console-same-origin-api.md` (blob 630e217c). 'Reach the API same-origin, the way the console reaches ClickHouse', M, standard, P2; owner `(none)`; depends_on console-http-repository. Estado `done`; aceite gravado pelo gate (hmac-sha256-v2, segundos) por `sidymar` no próprio commit de implementação em 2026-09-20/21; a transição para `done` foi feita por outra pessoa (agmarcastro) em 9841119 (2026-09-29, PR #153). Registro da ferramenta do autor, não revisão independente nem autorização atual (aceite às 12:13Z de 2026-09-21). Pod provável: Pod 1/Front.

### Intenção e benefício

Sem apiUrl configurado, chamar /v1 de mesma origem e fazer Vite (dev) e nginx (produção) encaminharem — a API não envia CORS e o navegador real falharia no preflight; os testes com fetch simulado não pegavam isso.

### Feito, faltante e não comprovado

Implementado (4297125): proxy /v1 no Vite, bloco /v1 no nginx com APEX_API_UPSTREAM, chaves apiUrl/apiToken no entrypoint. Achado de linhagem: a folha seguinte (pr129-review-fixes, aceita às 15:01Z do mesmo dia) registra que 'the nginx block was spliced INSIDE the clickhouse proxy_pass ... so no container starts at all - and the eval that was meant to guard it only grepped for a string'. O eval_2 desta spec é exatamente esse grep (`grep -q 'APEX_API_UPSTREAM' nginx.conf`). Ou seja, o aceite registrado cobriu um nginx que, segundo a própria folha de correção, não iniciava; corrigido em c71c2e4.

### Linhagem

Histórico próprio lido: b780c97 adicionou a folha same-origin em21/09; 4297125 implementou e9841119 encerrou o estado. A correção c71c2e4 é descrita na spec/histórico da folha seguinte. Origem em sync/plano/merge permanece relato herdado, sem nova consulta nem releitura da nota externa; não atribuir criação desta folha ao7fb0879.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260921-console-same-origin-api.md; fontes/batch-revalidated-specs58-sources/history/T-20260921-console-same-origin-api.txt; fontes/batch-revalidated-specs58-sources/git/front__nginx.conf; fontes/batch-revalidated-specs58-sources/git/front__vite.config.ts; fontes/batch-revalidated-specs58-sources/git/front__docker-entrypoint.d__30-apex-console-config.sh; fontes/batch-revalidated-specs58-sources/git/front__Dockerfile; fontes/batch-revalidated-specs58-sources/git/front__src__data__httpRepository.test.ts; fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260921-pr129-review-fixes.md. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: nginx tem location /v1/ (47–50); Vite proxy /v1 usa VITE_APEX_API_PROXY_TARGET (27–35). Dockerfile define upstreams e filtro antes de envsubst (23–34); entrypoint emite chaves apenas com variável set (118–122). eval2 é grep, eval3 pede chaves positivas e ausência de apiUrl na segunda chamada, sem checar ausência de apiToken. Nginx histórico quebrado é relato da remediação; nginx -t não rodou.

### Fluxo

Fluxo observado: navegador → mesma origem /v1 → Vite proxy (dev) ou nginx location /v1 (prod) → APEX_API_UPSTREAM → apex-api ; entrypoint escreve config.js com apiUrl/apiToken só quando definidos.

### Consequências e risco

O texto atual contém blocos irmãos e caminho de proxy coerente; isso não demonstra inicialização da imagem nem navegação. O teste original não discriminava sintaxe do nginx. Não concluir nenhum risco atual só por correção presente.

### Alternativas e recomendação

Recomendado: manter encerrada com nota de que o aceite antecede a correção c71c2e4; ao reutilizar, trocar eval_2 por `nginx -t` na imagem (como a folha seguinte fez).

### Dependências e paralelismo

Nenhuma dependência pendente: http-repository entregue e o nginx corrigido por c71c2e4. A prova de imagem e navegador fica com a #172, paralela e independente do fechamento documental desta folha.

### Plano e aceite propostos

Condição de não ação no código. Nota documental: 'aceite às 12:13Z antecede a correção do splice do nginx (c71c2e4, 15:01Z)'. Em reuso do plano, eval_2 deve renderizar o template e rodar `nginx -t`, como fez a folha pr129-review-fixes.

### Comunicação entre responsáveis

Explicar: o cliente pode usar /v1 relativo e proxies possuem alvos configuráveis. O relato de configuração quebrada mostrou a insuficiência do grep; o estado atual foi inspecionado, sem executar imagem ou navegador.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Uma URL de outra origem sem CORS permitido pode ser bloqueada pelo navegador; URL absoluta da própria origem não cria esse problema. Que caso o teste ainda não cobre? — Imagem completa iniciando e requisições reais atravessando proxy, além do negativo de apiToken omitido no eval3. Como eu explicaria isso para outro pod? — O texto dos proxies está presente; a sintaxe renderizada e o browser exigem provas específicas.

### Próxima ação e encerramento

Ação: nota da sequência aceite→correção no índice. Owner a confirmar: Front (Pod 1). Entrada: c71c2e4 e a spec pr129-review-fixes. Saída: nota. Encerramento: já encerrada; a #172 prova o caminho no navegador.

<a id="item-334"></a>

## T-20260921-pr129-review-fixes — T-20260921-pr129-review-fixes.md

Frente: Serve+Front / API HTTP e adaptação da Console (#129). Encaminhamento: encerrada_correcoes_de_revisao_concluidas_por_fab6620.

### Identidade e estado

`tasks/done/T-20260921-pr129-review-fixes.md` (blob ecdecc06). 'Fix the four defects Codex found on PR 129', M, standard, P2; owner `(none)`; depends_on console-same-origin-api. Estado `done`; aceite gravado pelo gate (hmac-sha256-v2, segundos) por `sidymar` no próprio commit de implementação em 2026-09-20/21; a transição para `done` foi feita por outra pessoa (agmarcastro) em 9841119 (2026-09-29, PR #153). Registro da ferramenta do autor, não revisão independente nem autorização atual. Pods prováveis: Pod 3/Serve e Pod 1/Front (nenhum pod no arquivo).

### Intenção e benefício

Corrigir os quatro defeitos reproduzidos da revisão da PR #129: nginx inválido (bloco /v1 dentro do proxy_pass), rota de stages com a projeção do MCP (NaN em três telas), proxy de dev forçando apiUrl absoluto, e fix_verification exigindo a tabela plan_memory que não lê.

### Feito, faltante e não comprovado

Nginx atual tem locations irmãos (33–50); stages chama console_stages (resources.py:95–102) e método usa CONSOLE_STAGES_SQL (ch.py:1065–1073). fix_verification verifica só tabelas lidas (1048–1063). Teste de campos SQL usa lista manual (test_ch.py:1048–1071), rota testa cinco campos e aliases (test_api_resources.py:158–173). Casos proxy target usam runtimeConfig mockado no topo de httpRepository.test.ts:19; não carregam vite.config/env real. eval nginx -t está definido na spec.

### Linhagem

Histórico lido: e759441 criou a folha de revisão em21/09 e c71c2e4 implementou;9841119 encerrou status em29/09. A spec relata revisãoCodex e reprodução de quatro defeitos; isso é relato de revisão por agente, não comprovação de revisão/aceite humano independente. Complemento fab6620 é relato herdado e não foi reconstruído integralmente nesta leitura.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__done__T-20260921-pr129-review-fixes.md; fontes/batch-revalidated-specs58-sources/history/T-20260921-pr129-review-fixes.txt; fontes/batch-revalidated-specs58-sources/git/front__nginx.conf; fontes/batch-revalidated-specs58-sources/git/front__vite.config.ts; fontes/batch-revalidated-specs58-sources/git/front__src__data__runtimeConfig.ts; fontes/batch-revalidated-specs58-sources/git/front__src__data__httpRepository.test.ts; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__ch.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_ch.py; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_api__routes__resources.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_api_resources.py. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

OBSERVADO: estado final contém os quatro ajustes e testes focados. Eval1 especifica renderização/teste do template na imagem nginx:1.27-alpine com upstreams explícitos; não valida toda a imagem APEX nem browser. Testes de fake/listas textuais discriminam campos escolhidos, sem prova integral de SparkEventRow ou resolução de ambiente do Vite. Nenhuma execução.

### Fluxo

Fluxo lido: template nginx define proxy /v1/; rota stages→console_stages→SQL de projeção→wire. Vite escolhe alvo por variável própria; runtimeConfig mantém apiUrl separado. fix_verification usa fix_verifications/run_outcomes. O nginx -t é uma receita de verificação histórica, sem execução nesta revisão.

### Consequências e risco

Correções e controles estão presentes, mas não autorizam nenhum risco atual nem SparkEventRow completo provado universalmente. A revisão por agente encontrou defeitos relatados que evals anteriores não discriminavam; não deve ser apresentada como revisão humana. Configuração integral e browser continuam fora do recorte.

### Alternativas e recomendação

Recomendado: manter encerrada; registrar que as correções de revisão terminaram em fab6620 (outro autor). Alternativa: nenhuma relevante. Padrão adotado e a replicar: validar configuração renderizando e testando (`nginx -t`) em vez de grep.

### Dependências e paralelismo

Nenhuma dependência pendente (same-origin entregue). A #172 (navegador e imagem completa) e a #171 (token) seguem em paralelo; reexecutar o eval_1 exige Docker autorizado.

### Plano e aceite propostos

Manter encerrada com alcance correto dos controles. Para reuso, preservar nginx -t como teste do template e distinguir imagem APEX completa; acrescentar resolução real de vite/env se B3 for requisito. Lista manual/fake de stages não substitui contrato dinâmico ou paridade live.

### Comunicação entre responsáveis

Explicar: os quatro ajustes estão no código e têm controles focados, incluindo receita nginx -t do template. A revisão citada foi de Codex; execução de imagem completa, ambiente e navegador têm fronteiras próprias.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Mantendo a rota de stages com a projeção do MCP, três telas renderizariam NaN; exigindo plan_memory em fix_verification, um cluster sem memória perderia as verificações. Que caso o teste ainda não cobre? — O navegador real atrás do nginx validado (#172). Como eu explicaria isso para outro pod? — 'A revisão externa achou o que os evals não viam; a correção trocou grep por validação real do nginx.'

### Próxima ação e encerramento

Ação: nota de conclusão via fab6620 no índice. Owner a confirmar: Serve+Front. Entrada: c71c2e4, fab6620 e corpo da #129. Saída: nota. Encerramento: já encerrada; a #172 fecha a prova de navegador.

<a id="item-335"></a>

## W01 — Revisar/mergear workspace PR #4

Frente: workspace_externo. Encaminhamento: encerrar_duplicata_de_p09.

### Identidade e estado

W01 é a ação "Revisar/mergear workspace PR #4" no repositório gustocezar/apex-workspace, fora do APEX. O registro já a marca como duplicata superada por P09. Estado público: 404 anônimo em 18/10. Estado local: merge e71b1bf da PR #4 presente no clone [caminho local omitido] (2026-09-25T00:31:42-03:00). Owner: Augusto (a confirmar).

### Intenção e benefício

Intenção: revisar e integrar a reconciliação do roadmap e backlog do workspace. Público: quem opera o workspace. Ganho: fonte operacional única. É a mesma intenção de P09.

### Feito, faltante e não comprovado

Feito: merge local da PR #4 visto no clone. Falta neste ID: nada; tudo que restar fica em P09. Não comprovado publicamente: estado do repositório e do run 36090577225.

### Linhagem

Linhagem: W01 → P09 como sucessor explícito no registro → PR #4 head 4d46173 → merge e71b1bf visível no clone. Isso permite encerrar a duplicata documental; revisão e run remotos não foram revalidados.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/workspace-backlog.md; fontes/batch-revalidated-wdprops-sources/workspace-merges.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018/workspace-repo.json. Locadores: Registro/MATRIX W01; workspace-merges.txt, merge e71b1bf da PR #4.

### Classe e limite da evidência

FATO OBSERVADO local: merge e71b1bf no clone do workspace. FATO OBSERVADO público: 404 anônimo em 18/10. RELATO: gate 36090577225 SUCCESS, herdado de P09. Nenhuma execução nesta revisão.

### Fluxo

Fluxo de sucessão: W01 —(mesma unidade)→ P09 —(PR #4)→ merge local e71b1bf na branch cowork. Nenhum fluxo de produto APEX está envolvido; é governança documental do workspace.

### Consequências e risco

Sem ação, nada muda; manter dois IDs ativos para a mesma PR duplicaria acompanhamento e contagem de pendências. O workspace não é dependência do APEX. Confiança alta no merge local, nula sobre o remoto.

### Alternativas e recomendação

Recomendado: encerrar W01 como duplicata de P09. Alternativa: fundir os IDs no registro, o que perderia a origem seed W01; manter os dois ativos, o que duplica trabalho. Reversível.

### Dependências e paralelismo

Nenhuma dependência para encerrar. P09 concentra a confirmação externa pendente (visibilidade do repositório e link do run), que é independente deste encerramento.

### Plano e aceite propostos

Nenhuma implementação neste ID. Preservar W01 → P09 e reabrir apenas se nova evidência demonstrar escopo distinto.

### Comunicação entre responsáveis

Para outro pod: "W01 e P09 são a mesma PR do workspace; consulte P09 para o estado e os limites de verificação. O repositório não é visível publicamente."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Manter W01 e P09 ativos duplicaria o acompanhamento da mesma PR. Que caso o teste ainda não cobre? O run 36090577225 permanece relato histórico; o merge local não demonstra seus resultados. Como eu explicaria isso para outro pod? W01 é uma origem preservada sob P09, com integração vista no clone e estado público indisponível.

### Próxima ação e encerramento

Próxima ação: encerrar W01 com ponteiro para P09. Owner: nenhum necessário. Entrada: P09. Saída: linha W01 "duplicata de P09". Encerramento: imediato.

<a id="item-336"></a>

## W02 — Captura real com spill

Frente: workspace_externo. Encaminhamento: externo_workspace_bloqueado_por_captura_real.

### Identidade e estado

W02 é evidência externa do workspace: captura real de um job Spark com spill, versionada e custodiada. Repositório gustocezar/apex-workspace (404 anônimo em 18/10). Owner: Augusto (a confirmar).

### Intenção e benefício

Problema: o Memory Watcher do workspace só foi exercitado com fixture sintética; promover o cenário memory_spill_heavy a validated exige log Spark real versionado com spill. Público: quem decide se o watcher de memória é confiável. Ganho: validar o watcher em dado real.

### Feito, faltante e não comprovado

No backlog fixado em 339e78e, o Memory Watcher é descrito como exercitado com fixtures; a captura real custodiada de spill ainda é pendência. O contrato exige spill ≥100 MiB no stage, SortMergeJoin e ≥8 tasks, worker 2+ cores, confiança ≥0,80 e controle negativo. Não foram consultadas capturas posteriores.

### Linhagem

Registro W02 → critérios de promoção na PR #5/W07 → captura real e custódia requeridas, ainda não demonstradas nas fontes lidas. A implementação sintética anterior é relato do backlog.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/workspace-backlog.md; fontes/batch-revalidated-wdprops-sources/workspace-merges.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018/workspace-repo.json. Locadores: Registro/MATRIX W02 e tabela de critérios do workspace-backlog.md em 339e78e.

### Classe e limite da evidência

FATO OBSERVADO local: backlog declara watcher só com fixtures. RELATO: avaliação do watcher. DECISÃO PENDENTE: nenhuma além de prover o ambiente. Nenhuma execução.

### Fluxo

Fluxo proposto: job Spark com spill no plat-v0 (worker 2+ cores) —(event log)→ MinIO versionado (version_id e SHA-256) —(--custody)→ Memory Watcher —(finding positivo)→ promoção do cenário, junto do baseline W03.

### Consequências e risco

Sem captura real, o cenário de spill fica em prototype e o watcher de memória não pode ser considerado validado; não há impacto no APEX. Confiança alta no estado local de 25/09, nula sobre o remoto atual.

### Alternativas e recomendação

Recomendado: manter bloqueado até W05 e W06; não fabricar captura. Alternativa: usar um log público de spill como substituto (não atende o critério de custódia). Reversível.

### Dependências e paralelismo

Depende de W05 (MinIO), de um ambiente plat-v0 com worker 2+ cores (W06) e, no laboratório, da PR #1 do Dataship (P10) se a captura usar output local. Independente do APEX.

### Plano e aceite propostos

Preparar cenário, critérios e plano de custódia offline. Em execução futura autorizada, produzir captura real com spill, metadados com schema/version_id/SHA-256, verificar o watcher e o baseline W03; registrar os limites do ambiente. Encerrar W02 pela captura/recibo; a promoção exige ainda os demais critérios de W07.

### Comunicação entre responsáveis

Para outro pod: "O watcher de memória do workspace ainda não viu um log real com spill; isso depende de MinIO versionado e de um worker com mais de um core."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Uma fixture apresentada como captura real invalidaria o critério de promoção. Que caso o teste ainda não cobre? O recorte não contém execução real de spill ≥100 MiB com par negativo e custódia verificável. Como eu explicaria isso para outro pod? W02 fornece a evidência positiva do laboratório; o aceite do cenário ainda requer os demais critérios de W07.

### Próxima ação e encerramento

Próxima ação: aguardar W05/W06; owner Augusto (a confirmar). Entrada: MinIO configurado e worker 2+ cores. Saída: log versionado e recibo do watcher. Encerramento: cenário com captura real custodiada.

<a id="item-337"></a>

## W03 — Baseline real sem spill

Frente: workspace_externo. Encaminhamento: externo_workspace_bloqueado_par_negativo.

### Identidade e estado

W03 é evidência externa do workspace: baseline real sem spill, com o mesmo schema e ambiente comparável a W02. Repositório gustocezar/apex-workspace (404 anônimo). Owner: Augusto (a confirmar).

### Intenção e benefício

Problema: um finding positivo de spill só vale se o par negativo (no_spill_baseline) continuar verde em dado real comparável; sem o baseline, um watcher que acusa sempre passaria. Público: quem valida o watcher. Ganho: controle negativo real.

### Feito, faltante e não comprovado

Estado no clone local: os critérios exigem, para "Spill negativo", log Spark real versionado sem spill, worker 2+ cores e verificação agendada; o backlog diz que nenhum cenário saiu de prototype. Falta: captura e custódia. Não comprovado: nada executado.

### Linhagem

Registro W03 → critérios de controle negativo da PR #5 → captura sem spill com métrica presente e custódia requerida. Produzir junto de W02 é recomendação para comparabilidade, não requisito de mesma sessão no contrato.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/workspace-backlog.md; fontes/batch-revalidated-wdprops-sources/workspace-merges.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018/workspace-repo.json. Locadores: Registro/MATRIX W03 e tabela Spill negativo do backlog em 339e78e.

### Classe e limite da evidência

FATO OBSERVADO local: critério de par negativo escrito no backlog de 339e78e. RELATO: nenhum resultado. DECISÃO PENDENTE: nenhuma além do ambiente e da custódia. Nenhuma execução.

### Fluxo

Fluxo proposto: job sem spill no mesmo ambiente de W02 —(log versionado)→ MinIO —(--custody)→ Memory Watcher —(nenhum finding)→ par negativo verde, permitindo promover W02.

### Consequências e risco

Sem o baseline, a promoção de W02 não é válida pelos próprios critérios do workspace, porque um watcher que acusasse sempre passaria. Impacto restrito ao workspace. Confiança alta no critério.

### Alternativas e recomendação

Recomendado: capturar W02 e W03 na mesma sessão e ambiente para garantir comparabilidade. Alternativa: baseline de outra sessão (aceitável só se o ambiente for idêntico e registrado). Reversível.

### Dependências e paralelismo

Depende de W05 (custódia MinIO) e do mesmo ambiente de W02 (W06, worker 2+ cores); pode ser feito em paralelo a W02, idealmente na mesma sessão para garantir comparabilidade.

### Plano e aceite propostos

Preparar o cenário negativo em paralelo. Na execução autorizada, registrar ambiente comparável, log real sem spill, schema/version_id/SHA-256 e resultado sem finding. Métrica ausente não equivale a zero; manter par positivo verde e evidência periódica para a promoção.

### Comunicação entre responsáveis

Para outro pod: "O baseline sem spill é o controle negativo do watcher de memória do workspace; sem ele, um finding positivo de spill não promove o cenário, pelas regras escritas na PR #5."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Aceitar métrica ausente como zero esconderia falha de observação e falso negativo. Que caso o teste ainda não cobre? Falta neste recorte o controle real com métrica presente e spill zero em ambiente comparável. Como eu explicaria isso para outro pod? W03 controla falsos positivos de W02; a mesma sessão ajuda a comparação, mas não foi imposta pelo texto dos critérios.

### Próxima ação e encerramento

Próxima ação: aguardar W05; executar junto com W02. Owner: Augusto (a confirmar). Entrada: MinIO e ambiente. Saída: log versionado sem spill e recibo. Encerramento: par negativo verde registrado.

<a id="item-338"></a>

## W04 — Estender Oráculo para spill

Frente: workspace_externo. Encaminhamento: externo_workspace_estender_oraculo_spill.

### Identidade e estado

W04 é uma PR futura do workspace: estender o Oráculo para comparar spill. Repositório gustocezar/apex-workspace (404 anônimo). Owner: Augusto (a confirmar).

### Intenção e benefício

oracle/compare.py em 339e78e deriva métricas de skew e compara operador, task quente e ratio; não contém comparação de spill. O backlog permite verificação agendada equivalente para memória enquanto essa extensão faltar.

### Feito, faltante e não comprovado

Leitura integral de compare.py confirma comparações de operador, registros quentes e skew_ratio, com tratamento de colapso em uma task. A extensão para spill é proposta; capturas reais e calibração não foram verificadas.

### Linhagem

Linhagem: registro W04 (study_ready, deps W02/W03) → critérios da PR #5 com a ressalva explícita sobre o Oráculo não comparar spill → implementação [ausente] → calibração com dado real [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/workspace-backlog.md; fontes/batch-revalidated-wdprops-sources/workspace-merges.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018/workspace-repo.json; fontes/batch-revalidated-wdprops-sources/workspace-oracle-compare.py. Locadores: Registro/MATRIX W04; workspace-oracle-compare.py, signals/main; ressalva de spill no backlog.

### Classe e limite da evidência

FATO OBSERVADO local: compare.py sem ocorrência de spill e ressalva escrita no backlog. PROPOSTA: estender o Oráculo. DECISÃO PENDENTE: tolerância. Nenhuma execução.

### Fluxo

Fluxo proposto: log real custodiado —(métricas de spill por stage)→ oracle/compare.py —(tolerância declarada)→ resultado contra a expectativa do cenário —(workflow agendado)→ evidência periódica.

### Consequências e risco

Sem a extensão, a promoção dos cenários de memória depende de uma verificação agendada alternativa; o impacto é só no workspace. Confiança alta.

### Alternativas e recomendação

Recomendado: desenhar métrica, tratamento de ausência e tolerância com fixtures offline; calibrar e aceitar comportamento real quando W02/W03 estiverem disponíveis. A verificação agendada equivalente prevista no backlog é alternativa válida.

### Dependências e paralelismo

Depende de W02/W03 para calibrar a tolerância com dado real; a implementação offline pode começar antes, desde que a tolerância fique marcada como provisória até a captura existir.

### Plano e aceite propostos

Passos mínimos: (1) definir métrica e tolerância; (2) implementar em compare.py; (3) testes com fixture positiva e negativa; (4) validação contra as capturas de W02/W03. Aceite: Oráculo compara spill dentro da tolerância declarada.

### Comunicação entre responsáveis

Para outro pod: "O Oráculo do workspace compara skew mas não spill; estender exige uma captura real para calibrar a tolerância, senão ele só confirma fixtures."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Confundir spill ausente com zero faria a comparação passar sem a métrica. Que caso o teste ainda não cobre? A extensão ainda precisa demonstrar spill positivo, baseline zero, métrica ausente e custódia inválida; nada foi executado aqui. Como eu explicaria isso para outro pod? O watcher detecta o sintoma; o Oráculo compara captura e expectativa, e pode ser desenhado antes da calibração real.

### Próxima ação e encerramento

Próxima ação: Augusto, a confirmar, preparar contrato da comparação e casos positivo/negativo offline. Entrada: compare.py e critérios W07. Saída: desenho revisável; implementação e prova real exigem autorização futura e capturas.

<a id="item-339"></a>

## W05 — MinIO do Oráculo semanal

Frente: workspace_externo. Encaminhamento: externo_workspace_bloqueado_credenciais_do_usuario.

### Identidade e estado

W05 é uma operação externa do workspace: configurar o MinIO do Oráculo semanal. Repositório gustocezar/apex-workspace (404 anônimo). Decisão: usuário provê valores e credenciais (DEC-21). Owner: Augusto (a confirmar).

### Intenção e benefício

Problema: o workflow semanal precisa de secrets MINIO_ENDPOINT, MINIO_ACCESS_KEY e MINIO_SECRET_KEY e de variáveis MINIO_REAL_LOG_OBJECT e MINIO_REAL_LOG_VERSION_ID; sem eles, o Oráculo não compara contra um log real. Público: quem depende da verificação periódica. Ganho: evidência periódica contra captura real.

### Feito, faltante e não comprovado

Em 339e78e, o workflow confere os cinco nomes de configuração e tenta baixar o objeto versionado. Falha de configuração/download comenta a issue aberta com título/label de custódia ou cria uma se não encontrar; divergência do Oráculo segue passo separado. O registro relata issue #6/run 36422233396. Commit local e40748b altera dois arquivos (+206/-1), incluindo +195 em test_minio_failclosed.py. Nenhuma branch remota conhecida do clone o contém; isso não prova que nunca foi publicado.

### Linhagem

Backlog e relato da sessão de 22/09 → issue #6/run de 28/09 relatados → commit local e40748b de 02/10 → estado de publicação e configuração atual não verificados. Os metadados lidos não autorizam afirmar ausência atual de secrets.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/workspace-backlog.md; fontes/batch-revalidated-wdprops-sources/workspace-merges.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018/workspace-repo.json; fontes/batch-revalidated-wdprops-sources/workspace-oracle-weekly.yml; fontes/batch-revalidated-wdprops-sources/workspace-commit-e40748b.txt; fontes/batch-revalidated-wdprops-sources/workspace-remote-containing-e40748b.txt. Locadores: Registro/MATRIX W05; workflow passos custody_config/fetch/Registrar custódia indisponível; commit e40748b e refs locais.

### Classe e limite da evidência

FATO OBSERVADO local: workflow e commit e40748b; nenhuma ref remota conhecida contém o commit no clone examinado. RELATO HISTÓRICO: configuração ausente, issue #6 e run 36422233396. DECISÃO PENDENTE: configuração do objeto real e destino do commit, após verificar seu estado remoto.

### Fluxo

Fluxo estático: configuração → download versionado → comparação → artefatos; falha de configuração/download → comentar issue de custódia existente ou criar uma; falha na comparação → issue de divergência.

### Consequências e risco

Se persistir a falta de configuração/captura, o workflow não comprova comparação real e registra a falha de custódia. Não se conclui que abre uma nova issue a cada falha. A promoção depende também dos demais critérios W07.

### Alternativas e recomendação

Recomendado: confirmar primeiro a configuração e a custódia pelo responsável, sem expor valores. Se faltarem, configurar nos mecanismos apropriados. Verificar a publicação de e40748b antes de decidir integrá-lo, manter ou descartar a branch.

### Dependências e paralelismo

Não depende do APEX. W02, W03 e W06 dependem deste item para custodiar logs. A decisão de publicar ou descartar o commit local e40748b é independente da configuração dos valores.

### Plano e aceite propostos

Passos mínimos: (1) configurar secrets e variáveis; (2) disparo manual do workflow; (3) registrar o run verde com version_id e SHA-256, sem valores; (4) decidir e40748b. Aceite: run semanal verde com objeto real.

### Comunicação entre responsáveis

Para outro pod: o workflow tem uma rota de custódia que reutiliza issue aberta; o snapshot histórico registra bloqueio por configuração/captura. O commit e40748b é conhecido localmente, com publicação remota não comprovada.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Tratar falta de custódia como divergência misturaria configuração indisponível com erro de comparação. Que caso o teste ainda não cobre? O recorte não comprova run com objeto real nem comportamento runtime do commit de testes. Como eu explicaria isso para outro pod? W05 provê a custódia do laboratório; refs locais e nomes de secrets não demonstram publicação nem configuração atual.

### Próxima ação e encerramento

Próxima ação: Augusto (a confirmar) configura os valores e decide e40748b. Entrada: acesso de administrador ao workspace. Saída: run verde com objeto real e destino do commit local. Encerramento: Oráculo semanal comparando contra captura real.

<a id="item-340"></a>

## W06 — Oito tasks reais em worker multi-core

Frente: workspace_externo. Encaminhamento: externo_workspace_runtime_multicore.

### Identidade e estado

W06 é runtime do workspace/laboratório: executar oito tasks reais num worker multi-core. Repositório gustocezar/apex-workspace (404 anônimo). Owner: Augusto (a confirmar).

### Intenção e benefício

Problema: o ratio real do Oráculo foi obtido num ambiente de 1 core, o que não exercita paralelismo; os critérios exigem worker com 2+ cores e stage com ≥8 tasks. Público: quem valida cenários de skew e spill. Ganho: Oráculo multi-core e critério de execução real atendido.

### Feito, faltante e não comprovado

Estado no clone local: backlog lista "Escalar worker para 2+ cores no plat-v0 — ⏳ aguardando ambiente plat-v0", "Re-rodar job com distribuição real de 8 tasks — ⏳ aguardando worker 2+ cores" e "Fechar ratio real do oráculo em multi-core — ⏳ aguardando run real". Falta: o ambiente. Não comprovado: nada executado.

### Linhagem

Linhagem: execução real de 1 core (histórica) → registro W06 (runtime_required, rec defer) → critérios da PR #5 exigem 2+ cores → ambiente [ausente] → run [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/workspace-backlog.md; fontes/batch-revalidated-wdprops-sources/workspace-merges.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018/workspace-repo.json; fontes/batch-revalidated-wdprops-sources/workspace-oracle-compare.py. Locadores: Registro/MATRIX W06; backlog Infraestrutura e compare.py, aviso collapsed.

### Classe e limite da evidência

FATO OBSERVADO local: três pendências do backlog marcadas como aguardando ambiente plat-v0. RELATO: ratio histórico obtido com 1 core. Nenhuma execução nesta revisão.

### Fluxo

Fluxo proposto: plat-v0 com worker 2+ cores —(job de 8 tasks)→ event log —(custódia W05)→ Oráculo —(ratio multi-core)→ critério de execução real.

### Consequências e risco

Sem o ambiente multi-core, os cenários do workspace não podem ser promovidos pelos próprios critérios; nada muda no APEX. Confiança alta no estado local de 25/09.

### Alternativas e recomendação

Recomendado: escalar o worker do plat-v0 junto com a captura de W02/W03 para economizar sessões. Alternativa: usar outro cluster Spark (exige registrar ambiente equivalente). Reversível.

### Dependências e paralelismo

Depende do ambiente plat-v0 com worker 2+ cores e, para escrita local de output, da PR #1 do Dataship (P10). W05 é necessário para custodiar o log produzido.

### Plano e aceite propostos

Preparar offline a configuração e o protocolo. Em execução futura autorizada, usar worker com 2+ cores e stage relevante com ≥8 tasks, registrar ambiente, custodiar o log e recalcular o ratio. A prova multi-core não substitui os pares e a periodicidade de W07.

### Comunicação entre responsáveis

Para outro pod: "Os números reais do Oráculo do workspace vêm de um worker de 1 core; para validar cenários é preciso rodar com 2+ cores e 8 tasks. Não é trabalho do APEX."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Um ratio colapsado em uma task não exercitaria a distribuição paralela exigida. Que caso o teste ainda não cobre? Falta no recorte o run multi-core com ≥8 tasks e custódia identificável. Como eu explicaria isso para outro pod? W06 é evidência do laboratório externo; não constitui gate global de APEX.

### Próxima ação e encerramento

Próxima ação: Augusto (a confirmar) provisiona o worker. Entrada: plat-v0 configurável. Saída: run multi-core custodiado. Encerramento: ratio multi-core registrado.

