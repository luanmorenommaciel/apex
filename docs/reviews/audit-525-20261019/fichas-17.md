# Fichas documentais — lote 17

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-161"></a>

## P04 — PR #129 — apex-api HTTP entre ClickHouse e consumidores

Frente: serve_api_http. Encaminhamento: encerrar_pr_integrada_com_residuos_mapeados.

### Identidade e estado

P04 é a própria PR luanmorenommaciel/apex#129 (registro: tipo PR; triagem: feature; pods Pod 3/Serve e Pod 1/Front). Autor sidymar (15 commits) com o commit de revisão fab6620; integrada em 2026-10-06T19:56:50Z por luanmorenommaciel no merge 83a9624, que conferi ser ancestral da base c3c3ea3. Sem assignee; owner de qualquer passo seguinte: a confirmar. Estado da PR lido no snapshot de 16/10; a consulta de 18/10 confirma somente main igual e lista vazia de issues atualizadas desde 15/10. #130, #140, #143 e #146 são referências históricas (billing, conflito de teste e PRs empilhadas), não implementações de P04. Corpo/estado histórico lido em 16/10; o GET de main/alterações de issues de 18/10 não revalida todos os campos públicos. Reviews históricas foram consultadas separadamente em 17/10.

### Intenção e benefício

Problema que a PR resolveu: a Console consultava o ClickHouse direto do navegador e o próprio repositório dizia que a credencial apex_ro "ships to every visitor", sem limite de taxa nem registro de quem perguntou o quê. Público: quem implanta a Console para terceiros, Pod 1 (Front), Pod 3 (Serve) e integrações externas. Ganho: modo DATA_SOURCE=http em que o navegador guarda só um token de API; /v1/runs/{job}/diagnosis passa pelo mesmo FastMCP.call_tool do editor, reduzindo a possibilidade de divergência entre entradas equivalentes; a equivalência ainda exige controles próprios; o servidor recusa iniciar sem token configurado.

### Feito, faltante e não comprovado

Feito e visível na base: serve/src/apex_api com app.py, auth.py, config.py, wire.py e routes/diagnostics.py (TOOL_ROUTES na linha 53) e front/src/data/http.ts. Das cinco lacunas que o corpo pediu para ler antes de aprovar: (1) task_time_ms=0 em run não indexado está corrigido estaticamente pelo sinal indexed em front/src/data/queries.ts:145 e serve/src/apex_mcp/ch.py:382-384 (S01); (2) render no navegador e (3) build nginx com /v1 continuam sem prova (S03/S04, #172); (4) /docs e /openapi.json sem token e a pergunta aberta sobre o nginx injetar o token estão em decisão (S05/S06, #171); (5) MCP ainda lê ClickHouse direto (S09, sem demanda registrada). Há runs hospedados failure no head fab6620; não há verde nesse conjunto. Render real da Console não foi demonstrado nas fontes examinadas.

### Linhagem

Linhagem: decisão relatada da Weekly Sync de 15/09 (ata pública não localizada: elo ausente) → Task-Specs T-20260920-*/T-20260921-* e plano tasks/.plans/serve-api.yaml citados no corpo (o plano é um dos três YAML que o Codex registrou com erro de parse, C04-06) → 15 commits + fab6620 → PR #129 head fab6620 sobre a289e53 → runs CI 35898024026 (pull_request) e 35898017600 (push) com conclusão failure em 2026-09-23 → duas reviews COMMENTED de bots em commits anteriores ao head final; nenhuma aprovação humana registrada no endpoint de 17/10 → merge 83a9624 em 06/10 → follow-ups #156 (prova API real, S02), #171, #172, #177 (S15). O registro histórico pedia registrar a decisão da Weekly Sync em issue/ADR; não encontrei esse registro.

### Fontes e corte

Fontes: corpo da #129 em ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json (trecho decisivo: "Known gaps — please read before approving" e "Not run in this pass: any query against a live ClickHouse"); linha P04 do OPPORTUNITY-REGISTER.csv (sha do CSV 33d13c25…) e da MATRIX (source_row_sha256 9628e187…); runs do head em ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/runs_all.json; arquivos da base capturados em fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3 (auth.py blob 022af32e7d, diagnostics.py f51eb3005e, http.ts a35918a437, queries.ts c6f0936bce, ch.py 2c1032d6b4); GET público de 18/10 em fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018. Metadados, diff de integração e reviews preservados em fontes/batch-root-p-sources/pr129.json; head fab662080da499df5d2d4b563ad68be7ddc4cc9f, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge 83a9624bce6247417728f635d4e57e5b0e8559ac.

### Classe e limite da evidência

FATO OBSERVADO: merge 83a9624 na base; arquivos da apex-api presentes; dois runs failure no head na janela do snapshot. RELATO HISTÓRICO: 289 testes Serve, typecheck e 130 testes vitest do autor sem containers; 16/16 rotas contra ClickHouse real antes de fab6620, explicitamente não repetidas; combinação local TS14 relatada no registro. INFERÊNCIA delimitada: nos dois runs desse head presentes no snapshot não há verde; não li os jobs deles, então não afirmo que nenhum teste rodou nem transfiro verdes posteriores de outras árvores (C04-28). Integração/runtime pós-merge pertence à #156 (S02), não a este ID. DECISÃO PENDENTE: exposição de /docs e custódia do token (DEC-08, #171). Nenhum teste ou runtime executado nesta revisão. O endpoint de reviews traz comentários automatizados, sem aprovação humana; o texto de billing em review é relato histórico, não consulta financeira atual.

### Fluxo

Fluxo observado no código, com setas nomeadas: navegador da Console —(Authorization: Bearer, GET /v1/…)→ proxy same-origin Vite/nginx —(encaminha /v1)→ middleware de auth da apex-api (compare_digest; /v1/health público) —(consulta ReadStore com tabelas não qualificadas)→ ClickHouse —(linhas no formato da Console)→ navegador. Rotas diagnósticas: apex-api —(call_tool)→ oito tools FastMCP —(veredito)→ resposta. Fora da API: cliente MCP —(credencial própria)→ ClickHouse. O trecho nginx é configuração não construída no relato da PR.

### Consequências e risco

Não há nova alteração de produto exigida por este registro da PR integrada: a PR já está na main. O risco é de leitura: tratar o merge como prova de render, de nginx ou da política de token, ou tratar S01 como aberto e duplicar a correção já presente. Confiança alta no merge e na estrutura (leitura direta); média no comportamento (testes relatados, não reexecutados). Limite: não afirmo exposição ou incidente; o próprio corpo diz que o schema aberto não carrega dados, só enumera a superfície.

### Alternativas e recomendação

Recomendado: encerrar P04 como entrega integrada e manter cada lacuna no seu destino nominal. Alternativa (b): manter P04 como guarda-chuva aberto, o que duplica #171/#172/#177 e confunde quem procura o resíduo. Alternativa (c): revisão retroativa da #129 inteira, custo alto e sem evidência nova. Padrões pertinentes: API gateway/BFF com token (adotado) versus injeção do token no proxy (muda quem custodia a credencial; decisão de #171). Reversibilidade: DATA_SOURCE=clickhouse continua existindo.

### Dependências e paralelismo

Encerrar P04 não depende de nada. Os resíduos são independentes e podem andar em paralelo: decisão #171 (exposição/token), prova #172 (nginx e navegador), estudo/feature #177 (narração AQE), prova API real já registrada em #156, e S09 só se aparecer consumidor que precise de MCP sem credencial. #122 (Ask sobre a API) pode ser discutida sem esperar nenhum deles. Capacidade de CI condiciona eventual prova hospedada; não é necessário encerrar a #130 antes de toda execução futura.

### Plano e aceite propostos

Condição de não ação: nenhuma mudança de produto ou issue nova a partir deste ID. Passo documental mínimo: registrar na visão consolidada o mapa lacuna→destino (1→S01 corrigido na base; 2 e 3→#172; 4 e pergunta do token→#171; 5→S09; Ask→#122). Critério de reabertura: regressão observada em serve/src/apex_api ou uma lacuna declarada pela #129 sem destino rastreável.

### Comunicação entre responsáveis

Mensagem para outro pod: "A #129 está na main e entregou a camada HTTP e o modo DATA_SOURCE=http. Ela não provou render no navegador nem a imagem nginx (#172) e deixou para decisão o /docs aberto e onde o token mora (#171). A prova contra ClickHouse real está na #156; o zero falso de task_time_ms já foi corrigido pelo sinal indexed."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Guardar o token no proxy transfere a autoridade de chamada para o proxy; a entrada ainda exige um controle de acesso definido. Que caso o teste ainda não cobre? — Uma chamada via nginx real precisa demonstrar que a resposta 401 não aciona fallback para ClickHouse. Como eu explicaria isso para outro pod? — A camada HTTP foi entregue; render/nginx e política de exposição têm destinos próprios.

### Próxima ação e encerramento

Próxima ação: Codex/mantenedor do Serve (a confirmar) confirmar o mapa lacuna→destino e marcar P04 como encerrado documental. Entrada: corpo da #129 e os cinco destinos. Saída verificável: linha P04 com "entregue em 83a9624; resíduos #171, #172, #177, S09; S01 corrigido na base". Encerramento: nenhuma lacuna declarada pela #129 sem destino.

<a id="item-162"></a>

## P05 — PR #131 — preflight de schema do Engine

Frente: engine_preflight_schema. Encaminhamento: encerrar_pr_integrada_com_residuos_mapeados.

### Identidade e estado

P05 é a própria PR luanmorenommaciel/apex#131 "engine: fail fast on connect when spark_events schema is behind" (Pod 2/Engine), autor gustocezar, head final 7b7b9b4 (sequência registrada d96d9b5 → 672dc1f → 7b7b9b4), integrada em 2026-10-06T19:56:20Z por luanmorenommaciel no merge e867232, presente na base c3c3ea3. Fecha a issue #95 (fechada em 06/10 como completed). Sem assignee; owner de resíduo a confirmar. #130 é referência de CI, não implementação. Corpo/estado histórico lido em 16/10; o GET de main/alterações de issues de 18/10 não revalida todos os campos públicos. Reviews históricas foram consultadas separadamente em 17/10.

### Intenção e benefício

Problema: volumes ClickHouse criados antes de uma migração conservam o schema antigo e o Engine falhava no meio da análise com erro bruto de coluna desconhecida; uma variável de database em branco também podia gerar o falso relato de que todas as colunas faltavam. Público: operadores do pacote local e quem diagnostica runs com volume antigo. Ganho: falha cedo no connect com a lista nomeada das colunas ausentes e leitura no database configurado.

### Feito, faltante e não comprovado

Feito na base: REQUIRED_SPARK_EVENTS_COLUMNS em engine/src/apex_engine/clickhouse.py:130, SchemaOutOfDateError na linha 236, _preflight_schema na linha 283 e CLICKHOUSE_DATABASE com strip e default "apex" em config.py:35. Falta, mas fora deste ID: provar leituras e INSERT do Engine em database alternativo (E03 cobriu só connect/preflight) e amarrar a constante às colunas lidas pelas queries (E20, PR #155 aberta). O run hospedado 36488115551 tem failure no head 7b7b9b4; verde não observado. O corpo público mais recente relata 226 passed/11 skipped de Engine+root nesse head. Separadamente, a lane E03 relata uma tentativa de coleta com erro crewai/pydantic e 161 passed/10 skipped após ignorar um arquivo; ambientes e conjuntos distintos, sem contradição demonstrada.

### Linhagem

Linhagem: issue #95 → R2/T27 (registro) → TS06 aceita em Tier 1 (relatada) → heads d96d9b5, 672dc1f (F-1, 27/09) e 7b7b9b4 (TS06/R2-F3, 28/09) → PR #131 → run 36488115551 failure → E03 em 30/09 com ClickHouse 24.8.14.39 descartável (relato indexado) → zero reviews registradas no endpoint de 17/10; isso não prova ausência de leitura humana → merge e867232 em 06/10 e fechamento da #95 → follow-ups E03 (lacuna de leitura/INSERT) e E20/#154/#155. Elo ausente: registro público de revisão humana antes do merge.

### Fontes e corte

Fontes: corpo da #131 em ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json (trecho: "fail fast on connect with the missing columns named"; "alternative-database provisioning is out of scope"); linha P05 do registro e MATRIX (source_row_sha256 012c98e2…); run 36488115551 em ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/runs_all.json; código em fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3 (clickhouse.py blob bd12414b4f, config.py 0abbec9652); relato E03 no caminho do registro, relativo à custódia [caminho local omitido] idêntico (sha256 616b5d7a1d68…) à cópia em [caminho local omitido] Metadados, diff de integração e reviews preservados em fontes/batch-root-p-sources/pr131.json; head 7b7b9b41aafa9b6fd3d45513ec7a8f394f9318fc, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge e8672329825105b4ee1ef7ab20f5338cc955929b.

### Classe e limite da evidência

FATO OBSERVADO: merge e símbolos do preflight na base; #95 fechada. RELATO HISTÓRICO: no corpo atualizado, 226 passed/11 skipped em 7b7b9b4 e 160 passed/11 skipped + 65 root em 672dc1f; o número 154/11 do registro pertence a relato anterior e não substitui os posteriores; R2 integrou #129+#131 no head antigo d96d9b5 com ClickHouse real; E03 relata, no head 7b7b9b4, preflight passando em dois databases completos, recusa por coluna ausente no terceiro, erro de conexão propagado e controle negativo que derruba o harness. INFERÊNCIA: o runtime relatado em E03 vale para connect/preflight, não para leituras/INSERT nem para a main atual. Nenhuma CI hospedada útil observada para o head final.

### Fluxo

Fluxo observado no código: Engine.connect —(SELECT em system.columns do database configurado)→ ClickHouse —(colunas presentes)→ comparação com REQUIRED_SPARK_EVENTS_COLUMNS —(faltantes nomeadas e contadas)→ SchemaOutOfDateError, ou —(conjunto completo)→ análise de stages com tabelas não qualificadas no mesmo database. Fluxo proposto pela E20: queries de stage —(colunas lidas)→ teste de igualdade ↔ constante do preflight.

### Consequências e risco

A proteção já está integrada; esta ficha não exige nova alteração de produto: a proteção está na main. O risco é ler o merge como prova de que o Engine inteiro funciona em database alternativo, ou esquecer que a constante pode divergir das queries quando uma nova coluna for lida. Confiança alta para o comportamento estático e média para o runtime relatado em E03 (não reproduzido). Sem incidente atribuído.

### Alternativas e recomendação

Recomendado: encerrar P05 e manter os resíduos em E03 e E20/#155. Alternativa: manter P05 aberto até a prova de leitura/INSERT; mistura a entrega integrada com um estudo de cobertura que tem dono e critério próprios. Alternativa de desenho já discutida em #155: derivar a constante das queries em runtime, o que acopla o preflight ao parser SQL. Reversível.

### Dependências e paralelismo

Encerrar P05 não depende de nada. E03 (prova em database alternativo) e E20/#155 (guarda estática) são independentes e podem andar em paralelo; E04/#173 (literais apex. restantes) informa o escopo de E03 sem ser gate. Capacidade de CI importa para prova hospedada; encerrar #130 não é gate geral destes follow-ups.

### Plano e aceite propostos

Condição de não ação: nenhum passo de produto em P05. Documentar na visão consolidada que o runtime de E03 cobre connect/preflight no head 7b7b9b4 e que leitura/INSERT segue em E03. Reabrir somente com regressão do preflight na main ou evidência de que SchemaOutOfDateError deixou de nomear colunas.

### Comunicação entre responsáveis

Para outro pod: "O preflight da #131 está na main e falha cedo nomeando colunas ausentes. Isso não prova que todas as leituras e escritas funcionam em database alternativo (E03) nem que a lista exigida acompanha as queries (#155)."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Uma query que lê coluna não exigida pelo preflight pode falhar depois de uma checagem inicial bem-sucedida. Que caso o teste ainda não cobre? — Connect/preflight não demonstra INSERT e leitura com dados no database alternativo. Como eu explicaria isso para outro pod? — Provar a checagem inicial não prova todas as operações do Engine.

### Próxima ação e encerramento

Próxima ação: confirmar encerramento documental de P05 com resíduos E03 e E20. Owner: mantenedor do Engine (a confirmar). Entrada: corpo da #131, relato E03 e #155. Saída: linha P05 "entregue em e867232; resíduos E03 (leitura/INSERT) e E20 (#155)". Encerramento: nenhum resíduo sem destino.

<a id="item-163"></a>

## P06 — PR #132 — reconciliar docs de contrato/Serve

Frente: documentacao_contrato_serve. Encaminhamento: pr_integrada_com_residuo_documental_delimitado.

### Identidade e estado

P06 é a própria PR luanmorenommaciel/apex#132 "docs: reconcile current contract and Serve state" (Docs), autor gustocezar, head 1f3c274, integrada em 2026-10-06T20:18:13Z por luanmorenommaciel no merge ee8820b, presente na base c3c3ea3. Sem assignee. Há um resíduo documental no próprio conjunto tocado: SERVE-LEGS.md mantém a afirmação de que não existe list_runs. Estado de merge do snapshot, não reconfirmação universal por GET since. Corpo/estado histórico lido em 16/10; o GET de main/alterações de issues de 18/10 não revalida todos os campos públicos. Reviews históricas foram consultadas separadamente em 17/10.

### Intenção e benefício

Problema: documentos de pipeline, changelog, planejamento do Serve, proposta L4 e README da Console descreviam contrato v0.4/v0.5, quatro tools MCP e correlação por execução como ausente. Público: quem planeja trabalho novo a partir da documentação. Ganho: planejar sobre o contrato v0.6 e as oito tools, sem duplicar o campo execution_id que o produtor já emite.

### Feito, faltante e não comprovado

Feito: alinhamento documental integrado; o corpo declara que o README raiz ficou fora porque a #127 o alterava (alinhado depois pela #134/P08) e que CONTRACT.md ficou intocado por ser autoridade ratificada (resíduo levado a X13/#165). Falta, fora deste ID: o contraste de redação do CONTRACT.md com marcadores PROPOSED (#165) e a correção de READMEs de lane ainda em v0.5, que a PR #164 aberta trata (verify/README.md muda de v0.5 para v0.6). Não comprovado: CI do head (run 35922514183 failure) e revisão formal. Resíduo diretamente conferido: docs/lanes/SERVE-LEGS.md:29–32 diz que toda tool exige job_id e não há list runs, mas a tabela :12 e server.py:362 já expõem list_runs. O cabeçalho mantém snapshot histórico de agosto ao lado de conteúdo reconciliado; o ajuste deve preservar história e distinguir a descrição atual. Não é falha funcional demonstrada.

### Linhagem

Linhagem: seed P06 → commits na branch codex/reconcile-current-apex-docs → PR #132 head 1f3c274 → run 35922514183 failure em 23/09 → zero reviews registradas no endpoint de 17/10; isso não prova ausência de leitura humana → merge ee8820b em 06/10 → continuidade documental em #134 (README raiz), #165 (CONTRACT.md, X13) e #164 (READMEs de Serve/Verify, aberta). Elo ausente: nenhuma verificação documentada pós-merge de que os documentos tocados continuam coerentes. Leitura integral do diff de cinco documentos e conferência da base identificam essa contradição residual, ausente no parecer Claude.

### Fontes e corte

Fontes: corpo da #132 em ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json (trecho: "CONTRACT.md was left untouched because it is ratified authority"); linha P06 do registro (proof_have: "239 passed serve; AST dos 8 tools") e MATRIX (source_row_sha256 08ff9621…); run 35922514183 em ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/runs_all.json; diff da #164 lido no recibo Codex fontes/pr164-files.json (observado em 16/10 18:29Z). Metadados, diff de integração e reviews preservados em fontes/batch-root-p-sources/pr132.json; head 1f3c2745605184d79d1dbbec73977160005b1420, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge ee8820b62703f765b6a5da14bd0068db52b937f3.

### Classe e limite da evidência

FATO OBSERVADO: merge na base; #164 aberta altera verify/README.md de "(v0.5)" para "(v0.6)", sinal de que a reconciliação documental não terminou com a #132. RELATO: 239 testes Serve e verificação AST das oito tools pelo autor. INFERÊNCIA: a mudança é só documental; testes relatados não validam a prosa. Sem CI hospedada útil observada; nenhuma execução nesta revisão.

### Fluxo

Fluxo documental: contrato v0.6 e tools registradas —(versão e contagem)→ docs de pipeline, changelog, planejamento e Console; CONTRACT.md —(sem alteração sem decisão do mantenedor)→ X13/#165; README raiz —(excluído, editado na #134)→ P08. É fluxo de leitura conceitual, não de execução.

### Consequências e risco

Não se demonstrou uma nova falha operacional neste recorte. O risco residual é tratar a #132 como reconciliação completa e não ver que READMEs de lane ainda dizem v0.5 até a #164 entrar. Confiança alta no merge; baixa para afirmar coerência atual de todos os documentos, que não comparei. Sem impacto de produto.

### Alternativas e recomendação

Registrar P06 como PR integrada e manter resíduo explícito de documentação Serve. Menor entrega proposta: corrigir a afirmação de descoberta ausente e esclarecer o corte histórico, junto de revisão documental pertinente ou em follow-up curto. A alternativa é anotar o trecho como puramente histórico, mas precisa explicar a tabela atual no mesmo documento. Não exigir uma suíte nova para editar prosa; #164/#165 têm escopos próprios.

### Dependências e paralelismo

Nenhuma dependência para encerrar. #164 e #165 são independentes entre si e podem ser revistas em paralelo; a guarda literal de test_telemetry_compatibility_matrix.py precisa acompanhar a #165 (Codex C04-16), não a #132.

### Plano e aceite propostos

Sem alteração funcional. Conferir SERVE-LEGS :12/:29–32/L2 contra server.py:list_runs; preparar edição mínima com histórico preservado e revisar leitura cruzada. Aceite documental: não afirmar ao mesmo tempo que list_runs existe e inexiste. Se o mantenedor incluir na #164, atualizar explicitamente seu escopo; não presumir cobertura da PR atual.

### Comunicação entre responsáveis

Para outro pod: a #132 foi integrada, mas deixou uma contradição em SERVE-LEGS: a tabela lista list_runs e o texto diz que a lane não descobre runs. É correção pequena de documentação; não falta implementar a tool.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Afirmar que não existe list_runs pode induzir outro pod a planejar uma tool duplicada. Que caso o teste ainda não cobre? — Uma suíte funcional não substitui a leitura cruzada da tabela e da prosa; esta correção pede revisão documental. Como eu explicaria isso para outro pod? — A implementação existe; falta reconciliar o trecho documental e seu corte histórico.

### Próxima ação e encerramento

Próxima ação: responsável documental Serve a confirmar registra o resíduo e escolhe follow-up ou ampliação explícita da PR documental pertinente. Entrada: linhas conflitantes e função list_runs. Saída: correção proposta com fonte; encerramento da entrega histórica permanece, e o resíduo só se encerra quando a prosa estiver coerente.

<a id="item-164"></a>

## P07 — PR #133 — ADR-004 fronteira de correlação de origem (F4.1)

Frente: arquitetura_privacidade. Encaminhamento: encerrar_pr_integrada_adr_permanece_proposto.

### Identidade e estado

P07 é a própria PR luanmorenommaciel/apex#133 "docs: propose source correlation privacy boundary" (Cross-pod/Segurança), autor gustocezar, head 5cd5968, integrada em 2026-10-06T20:19:24Z por luanmorenommaciel no merge 663f04c. O ADR-004 na base declara "Status: proposed; no implementation is authorized by this document", data 2026-09-23 e "Decision owner: Luan". Owner da ratificação: Luan, segundo o próprio documento; não há assignee em issue. Corpo/estado histórico lido em 16/10; o GET de main/alterações de issues de 18/10 não revalida todos os campos públicos. Reviews históricas foram consultadas separadamente em 17/10.

### Intenção e benefício

Problema: F4.1 pergunta qual linha de código ou célula de notebook produziu um stage; responder exige guardar informação de localização que pode conter caminhos absolutos, segmentos do home do usuário, stack traces ou texto de query. Público: Pods que coletam telemetria e quem opera ambientes com código sensível. Ganho: uma fronteira opt-in e aditiva acordada antes de qualquer implementação, sem expor detalhes de sistema de arquivos em repouso.

### Feito, faltante e não comprovado

Feito: o ADR proposto está na main e no ADR-INDEX.md como "proposto; nenhuma implementação autorizada". Falta: aceitação ou revisão pelo dono da decisão, e qualquer especificação de implementação. Não comprovado e não aplicável: runtime. O merge de um documento proposto não registra aceitação; a v2 já distinguia isso e eu confirmo pela leitura integral do ADR, incluindo suas cinco precondições para uma Task-Spec/implementação.

### Linhagem

Linhagem: seed P07 e X03 → L4_PROPOSAL F4.1 → branch codex/adr-call-site-correlation → PR #133 head 5cd5968 (draft no registro) → run 35922973951 failure em 23/09 → merge 663f04c em 06/10 → ADR-INDEX (#141, X14) lista ADR-004 como proposto → decisão de ratificação [elo ausente: nenhuma decisão registrada]. X03 ("Concluir ADR de correlação de origem") foi classificado como superado pelo merge, mas a decisão de conteúdo continua aberta.

### Fontes e corte

Fontes: corpo da #133 em ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json (trecho: "merge of the document does not record the owner's acceptance"); ADR-004 na base (blob e08521720d), linhas 1-6; ADR-INDEX.md (blob 4f5d2d10bf), tabela; linha P07 do registro (decision: "Owner decide aceitar/revisar a fronteira (DEC-11)"). Metadados, diff de integração e reviews preservados em fontes/batch-root-p-sources/pr133.json; head 5cd5968c8cd9a1901fcc60db446dab1c8f9a7226, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge 663f04c6fc7207aaf9e11e9329176254062f72db. O diff integral de 170 linhas contém as cinco decisões prévias, critérios de futuro aceite e rollback; leitura não limitada ao cabeçalho.

### Classe e limite da evidência

FATO OBSERVADO: ADR presente com status proposed e índice coerente. RELATO: diff check do autor. DECISÃO PENDENTE: aceitar, revisar ou rejeitar a fronteira (registro: DEC-11, que tratava também da numeração de ADR, já resolvida em parte pelo índice). Nenhuma execução aplicável nesta revisão.

### Fluxo

Fluxo proposto (não implementado): submissão de stage Spark —(call site)→ dado de localização —(localizador relativo ao repositório ou referência opaca)→ fronteira opt-in —(sem stack trace, caminho absoluto, trecho de código ou query)→ telemetria em repouso; dono da decisão —(aceita ou revisa)→ fronteira.

### Consequências e risco

A proposta não implementa o recurso; não há incidente operacional demonstrado neste recorte. O risco possível é alguém implementar correlação de origem tomando "merged" por "aceito" e gravar caminhos identificáveis; é hipótese de processo, não incidente. Confiança alta no status (leitura direta).

### Alternativas e recomendação

Recomendado: encerrar P07 como PR documental integrada e manter a ratificação como decisão separada do mantenedor. Alternativas: mudar o status para accepted por merge (contradiz o documento); manter a PR como item aberto (confunde entrega documental com decisão). Padrões considerados no ADR: localizador relativo, referência opaca, opt-in. Reversível.

### Dependências e paralelismo

Não há dependência técnica para encerrar. Qualquer implementação de F4.1 depende da ratificação do ADR-004 pelo dono. A numeração (X14) já tem índice canônico e não bloqueia a decisão. O ADR exige antes da Task-Spec: permissão do localizador, semântica de opt-in/root, identidade de notebook, payload/migração e primeiro consumidor. Estudos conceituais podem informar a decisão; não aprovar implementação antecipadamente.

### Plano e aceite propostos

Condição de não ação: nenhuma implementação. Passo mínimo de decisão, fora deste ID: o dono registra aceitar/revisar/rejeitar no próprio ADR ou numa issue, com data. Critério de reabertura deste ID: nenhum; a decisão vive no ADR.

### Comunicação entre responsáveis

Para outro pod: "O ADR-004 está na main como proposto. O merge não autoriza implementar correlação de origem; qualquer trabalho em F4.1 espera a decisão do Luan sobre a fronteira de privacidade."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Gravar um caminho absoluto antes da decisão anteciparia a escolha de privacidade e identidade prevista no ADR. Que caso o teste ainda não cobre? — A futura prova precisa definir o tratamento de notebook sem identidade lógica. Como eu explicaria isso para outro pod? — Integrar uma proposta de ADR não registra a aceitação do dono.

### Próxima ação e encerramento

Próxima ação: registrar a PR integrada e vincular DEC-11 ao ADR proposto. Responsável documental a confirmar; Luan é o dono da decisão declarado. Saída deste ID: mapa P07→merge663f04c→ADR proposto/DEC-11. A futura alteração do status do ADR encerra a decisão correspondente, não é condição retroativa para provar que a PR documental foi integrada.

<a id="item-165"></a>

## P08 — PR #134 — README alinhado a v0.6

Frente: documentacao_readme. Encaminhamento: encerrar_pr_integrada_docs.

### Identidade e estado

P08 é a própria PR luanmorenommaciel/apex#134 "docs: align README with current contract" (Docs), autor gustocezar, head 3340e2f, integrada em 2026-10-06T20:18:19Z por luanmorenommaciel no merge b7afeae. Sem assignee e sem resíduo próprio. A PR #164 aberta altera duas linhas do README raiz (contagens de testes), escopo distinto. Corpo/estado histórico lido em 16/10; o GET de main/alterações de issues de 18/10 não revalida todos os campos públicos. Reviews históricas foram consultadas separadamente em 17/10.

### Intenção e benefício

Problema: o README raiz anunciava contrato v0.5 e quatro tools MCP e sugeria que a reconstrução AQE do lado de leitura existia. Público: quem chega ao projeto pela página inicial. Ganho: superfície atual descrita corretamente (v0.6, oito tools) e o limite AQE declarado.

### Feito, faltante e não comprovado

Feito e conferido na base: badge contract-v0.6 (README.md:9), tabela de tools com list_runs, analyze_run, compare_runs, verify_fix e suggest_fix entre as linhas 179-186, e a linha 276 dizendo que a v0.6 emite execution_id no produtor mas que o mapeamento de leitura e a prova runtime ainda são necessários. Falta neste ID: nada. Não comprovado: CI do head (run 35923379397 failure) e revisão formal; não confirmei se as contagens de testes do README estão atuais (a #164 as altera).

### Linhagem

Linhagem: seed P08 → branch codex/reconcile-root-readme → PR #134 head 3340e2f com merge-tree limpo contra #127 (relato) → run 35923379397 failure → zero reviews registradas no endpoint de 17/10; isso não prova ausência de leitura humana → merge b7afeae em 06/10 → ajustes posteriores de contagem na #164 (aberta). Sem elo ausente relevante para o escopo documental.

### Fontes e corte

Fontes: corpo da #134 em ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json (trecho: "producer-side execution_id exists; read-side mapping and runtime proof remain pending"); README na base (blob 22753a7411), linhas 9, 158, 179-186 e 276; diff da #164 no recibo fontes/pr164-files.json (README.md +2/-2). Metadados, diff de integração e reviews preservados em fontes/batch-root-p-sources/pr134.json; head 3340e2fafce06605ecc89dd4836703b2f4d3c275, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge b7afeaeed5d81219e1fc35ea6b76696052a1a10d.

### Classe e limite da evidência

FATO OBSERVADO: README da base em v0.6 com oito tools e limite AQE explícito. RELATO: verificação AST das tools e merge-tree limpo, do autor. INFERÊNCIA: as contagens de testes no README podem estar defasadas, já que a #164 as muda; não verifiquei. Nenhuma execução nesta revisão.

### Fluxo

Fluxo documental: tools registradas —(oito nomes conferidos por AST, relato)→ tabela do README; contrato v0.6 —(versão e fronteira AQE)→ README; README —(superfície atual)→ leitor novo. Fluxo de leitura, não de execução.

### Consequências e risco

Não se demonstrou uma nova falha operacional neste recorte. Risco baixo: contagens de testes no README envelhecem a cada merge e podem induzir comparações erradas, o que já está na #164. Confiança alta no conteúdo verificado das linhas citadas.

### Alternativas e recomendação

Recomendado: encerrar P08. Alternativa: transformar contagens de testes em referência ao CI em vez de números fixos, reduzindo deriva; é escolha documental para a #164 ou para o mantenedor, não resíduo deste ID. Reversível.

### Dependências e paralelismo

Nenhuma dependência para encerrar P08. A revisão da #164 é independente e pode ocorrer a qualquer momento; a revisão documental não espera #165. O filtro Markdown do workflow explica ausência de checks, mas não elimina os critérios de review e consistência aplicáveis.

### Plano e aceite propostos

Nenhum novo passo de produto neste ID. Para manutenção futura, revisar a tabela de tools quando a superfície mudar e referenciar prova datada em vez de perpetuar números sem corte. Automação só se o mantenedor identificar benefício recorrente; não é requisito para encerrar esta correção documental.

### Comunicação entre responsáveis

Para outro pod: "O README raiz já descreve v0.6 e as oito tools, e diz que o mapeamento AQE de leitura ainda não foi provado. As contagens de testes são outra correção, na #164."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Uma tabela fixada em oito tools pode envelhecer quando a superfície mudar. Que caso o teste ainda não cobre? — Conferir nomes não demonstra que cada tool funciona com dados reais. Como eu explicaria isso para outro pod? — O README descreve a superfície; os recibos de comportamento continuam separados.

### Próxima ação e encerramento

Próxima ação: confirmar encerramento de P08. Owner: revisor documental (a confirmar). Entrada: README na base. Saída: linha P08 "entregue em b7afeae; contagens na #164". Encerramento: imediato.

<a id="item-166"></a>

## P09 — Workspace PR #4 — reconciliar roadmap/backlog

Frente: workspace_externo. Encaminhamento: externo_workspace_registrar_evidencia_local.

### Identidade e estado

P09 é a PR #4 do repositório gustocezar/apex-workspace ("reconciliar roadmap/backlog"), fora do repositório APEX. Head registrado 4d46173, merge e71b1bf na branch cowork. Responsável registrado: Augusto. Estado público: GET anônimo em 2026-10-18 devolveu HTTP 404 (o mesmo da triagem de 11/10, gap G05), portanto não verificado publicamente. Evidência local: no clone [caminho local omitido] existem o commit 4d46173 (2026-09-25T00:24:04-03:00, "docs: remove closed issue actions from backlog") e o merge e71b1bf (2026-09-25T00:31:42-03:00, "Merge pull request #4").

### Intenção e benefício

Problema registrado: o roadmap de junho aparecia como atual no workspace; a PR reconciliou backlog e roadmap e, segundo o registro, W11 removeu ações sobre issues fechadas e um ADR-004 ambíguo. Público: quem planeja a partir do workspace. Ganho: uma fonte operacional única, sem ações obsoletas.

### Feito, faltante e não comprovado

Feito: o merge existe no clone local (FATO local). Falta: confirmar visibilidade/acesso do repositório e o estado atual do remoto; isso não está ao alcance de uma consulta anônima. Não comprovado nesta revisão: o run do Scenario Gate 36090577225 (SUCCESS segundo o registro), os 53 testes e o run_slice locais. O diff local do merge foi lido: dois documentos distinguem plano histórico, backlog operacional e provas sintéticas/reais. Isso confirma a mudança documental local, não o estado remoto atual.

### Linhagem

Linhagem: seed P09 + G05 + W01 + W10 → branch codex/reconcile-workspace-docs → commit 4d46173 → PR #4 → Scenario Gate 36090577225 (relato) → merge e71b1bf em cowork (visto no clone) → acompanhamento W07 em unidade separada. Elo ausente: qualquer evidência pública de 2026-10 sobre o repositório.

### Fontes e corte

Fontes: linha P09 do registro (proof_have: "Scenario Gate 36090577225=SUCCESS; 53 testes, run_slice e diff check locais; merge e71b1bf") e MATRIX (destination needs_revalidation; reason: endpoint 404); GET em fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018/workspace-repo.json (404, capturado em 2026-10-18T04:00:57Z); objetos Git lidos com git cat-file/log no clone local (refs/remotes/origin/cowork = e71b1bf no último fetch local, data de fetch desconhecida).

### Classe e limite da evidência

FATO OBSERVADO local: commits 4d46173 e e71b1bf existem no clone. FATO OBSERVADO público: 404 anônimo em 18/10. RELATO: Scenario Gate SUCCESS e testes locais. INFERÊNCIA: o 404 anônimo não identifica a causa (privado, movido, renomeado ou removido) sem autenticação (C04-31); só o dono pode esclarecer. Sem execução nesta revisão.

### Fluxo

Fluxo: roadmap/backlog antigos —(reconciliação documental)→ PR #4 —(merge e71b1bf)→ branch cowork do workspace —(fonte de planejamento)→ quem opera o workspace. Observado só até o merge local; a publicação/visibilidade é desconhecida.

### Consequências e risco

Não foi demonstrada dependência técnica da entrega APEX nesta PR externa. A leitura do backlog pode influenciar o planejamento, sem se tornar gate universal. O risco é documental: citar a PR #4 como prova pública quando ninguém de fora consegue abri-la. Confiança alta na existência local do merge; nenhuma sobre o estado remoto atual.

### Alternativas e recomendação

Recomendado: catalogar P09 como externo concluído localmente, com a ressalva de verificação pública impossível sem acesso. Alternativa: pedir ao dono que confirme visibilidade e anexe o link do run; alternativa: retirar P09 do registro APEX (perderia a origem; não recomendo). Reversível.

### Dependências e paralelismo

Nenhuma dependência técnica do APEX. Depende apenas de alguém com acesso ao workspace confirmar o estado. W01/W10/W11 compartilham a mesma fonte e podem ser confirmados no mesmo passo.

### Plano e aceite propostos

Condição de não ação no APEX: nenhuma. Passo externo mínimo: o dono do workspace confirma (a) a causa do 404 público (visibilidade, nome ou remoção), (b) o estado da branch cowork e (c) o link do run 36090577225; registrar a resposta como relato datado. Sem isso, manter "não verificado publicamente".

### Comunicação entre responsáveis

Para outro pod: "A reconciliação do workspace (PR #4) aparece integrada num clone local, mas o repositório não é visível publicamente; não usar como prova pública nem como dependência do APEX."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Apresentar o merge local como prova pública deixaria sem fonte verificável a pessoa que não tem acesso ao repositório. Que caso o teste ainda não cobre? — O relato do Scenario Gate não certifica captura real com custódia versionada. Como eu explicaria isso para outro pod? — Os dois documentos mudaram no clone; o estado remoto não foi verificado.

### Próxima ação e encerramento

Próxima ação: dono do workspace (Augusto, a confirmar) responde às três perguntas do campo 11. Entrada: acesso autenticado ao workspace. Saída: nota datada com visibilidade, head da branch cowork e link do run. Encerramento: nota registrada ou decisão explícita de manter o item como histórico local não verificável.

<a id="item-167"></a>

## P10 — Dataship PR #1 — output local compartilhado master/worker

Frente: dataship_externo. Encaminhamento: externo_dataship_aguarda_upstream.

### Identidade e estado

P10 é a PR #1 do repositório público Gabriel-Philot/dataship-spark-plat-v0 ("fix: share local output path between spark-master and spark-worker"), aberta por gustocezar em 2026-09-23T00:16:31Z, head e0ed228, base main. GET de 2026-10-18 confirma: aberta, sem merge. O repositório tem duas PRs abertas (#1 e #2) e o metadado pushed_at do repositório upstream é 2026-07-21 (não é timestamp específico da branch main). Decisão: mantenedor upstream Gabriel-Philot (DEC-20 no registro). Base observada 89202730dfd19d35d52c35d61b739dad4fcca345 e head e0ed228a493318ead9cb8afb8fdde1f98a0f0a9d.

### Intenção e benefício

Problema: sem filesystem compartilhado, o FileOutputCommitter deixava part-files em _temporary no worker e o output local do plat-v0 não ficava confiável. Público: quem usa o laboratório Dataship para gerar workloads e telemetria (origem: issue #1 do workspace). Ganho: output local completo, com part-files e _SUCCESS no caminho esperado.

### Feito, faltante e não comprovado

Feito: PR publicada upstream com 2 arquivos (+15, segundo o registro). Falta: revisão e decisão do mantenedor upstream. Não comprovado nesta revisão: docker compose config, 12 testes, E2E dirigido com 2 part-files e _SUCCESS e make smoke, todos relatados no corpo da PR. O upstream não tem CI, segundo o registro.

### Linhagem

Linhagem: issue #1 do workspace → D01 (validação E2E do volume, hoje marcada superada) → branch do autor → PR #1 head e0ed228 → relato de testes no corpo → revisão upstream [não verificada: a listagem de PRs não é o endpoint de reviews] → após decisão, W12 liga a issue do workspace à PR. Discussões/reviews upstream não foram consultadas; não inferir silêncio humano a partir de updated_at.

### Fontes e corte

Fontes: GET fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018/dataship-pulls.json e fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018/dataship-repo.json (2026-10-18, HTTP 200); linha P10 do registro (proof_have: "docker compose config; 12 testes; E2E dirigido com 2 part-files + _SUCCESS; make smoke (corpo da PR)") e MATRIX (destination existing_pr, remaining_scope: acompanhar revisão e merge upstream).

### Classe e limite da evidência

FATO OBSERVADO: PR #1 aberta, head e0ed228, sem merge, em 18/10; pushed_at do repositório em 21/07. RELATO: testes e E2E do autor. INFERÊNCIA: o metadado de push não mede disponibilidade nem intenção do mantenedor. DECISÃO PENDENTE: merge upstream. Nenhuma execução nesta revisão.

### Fluxo

Fluxo proposto pela PR: spark-master e spark-worker —(montam o mesmo caminho local de output)→ FileOutputCommitter —(commit de tarefas e do job no mesmo filesystem)→ part-files e _SUCCESS visíveis no host. Observado apenas como relato do corpo. Confronto independente do diff base...head no clone: bind mount igual em master/worker e documentação do fallback local, sem execução de containers.

### Consequências e risco

Sem ação no APEX, nada quebra: o APEX não depende do output local do plat-v0 para a v1. O impacto fica no laboratório, para quem usar workloads com escrita local. Confiança média no conserto (relato do autor), baixa sobre prazo de decisão upstream.

### Alternativas e recomendação

Recomendado: manter como externo aguardando upstream, sem gate para o APEX. Alternativas: (a) manter fork local com o patch para experimentos próprios, com custo de divergência; (b) usar storage compartilhado (MinIO/S3A) no laboratório em vez de caminho local; (c) fechar a PR se o upstream sinalizar outro caminho. Reversível.

### Dependências e paralelismo

Nenhuma dependência para o APEX. W12 pode registrar o vínculo à PR aberta antes de qualquer decisão de merge; acompanhamento de conclusão depende do upstream. D15 (PR #2, dependências Go) é independente e também aguarda o mesmo mantenedor; podem ser decididas juntas.

### Plano e aceite propostos

Condição de não ação no APEX: nenhuma. Passo externo mínimo: uma consulta pública periódica de estado ou um ping educado ao mantenedor upstream, decidido pelo autor da PR. Encerramento quando a PR for integrada ou fechada com motivo.

### Comunicação entre responsáveis

Para outro pod: "A correção do output compartilhado do Dataship está aberta upstream desde 23/09 e não é dependência do APEX; quem precisar dela hoje usa a branch do autor por conta própria."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — A escolha de storage compartilhado pode dispensar o fallback de filesystem local em um perfil, mas precisa ser explícita. Que caso o teste ainda não cobre? — O E2E relatado com dois part-files não demonstra sozinho cobertura de vários workers e retries. Como eu explicaria isso para outro pod? — A PR externa pode ser acompanhada e vinculada antes do merge, sem virar gate universal do APEX.

### Próxima ação e encerramento

Próxima ação: autor da PR (gustocezar, a confirmar) decide se pede revisão ao mantenedor ou mantém espera. Entrada: estado público da PR. Saída: PR integrada, fechada com motivo, ou nota de espera datada. Encerramento: decisão upstream registrada.

<a id="item-168"></a>

## T-20260817-cursor-codex-config — T-20260817-cursor-codex-config.md

Frente: Serve / L1 Connect — documentação e clientes. Encaminhamento: decidir_documentacao_por_cliente_com_eval_reescrito.

### Identidade e estado

`tasks/T-20260817-cursor-codex-config.md` (blob confere com snapshot). 'Document the Cursor and Codex config paths', XS, standard, P2; owner `(none)`; sem dependências. Estado `ready`, `accepted: false`. Marcada '▶︎' no índice L1. Pod provável: Pod 3/Serve (inferido pelos caminhos; nenhum pod no arquivo).

### Intenção e benefício

Permitir que um usuário de Cursor ou Codex instale o Apex só pelo README: hoje dois dos três clientes são documentados por implicação ('todos leem o mesmo schema') sem dizer onde cada um procura o arquivo, nem escopo projeto/usuário.

### Feito, faltante e não comprovado

Não implementado: `serve/README.md` tem uma seção 'Install' com bloco Claude Code e uma frase 'Project scope / Cursor / Codex: copy .mcp.json to the repository root' (`README.md:182-207`); não há subtítulos `### Cursor`, `### Codex`, `### Claude Code`, nem caminho/escopo/passo de verificação por cliente, nem aviso de reinício após exportar variável. Não comprovado: caminhos atuais de cada cliente (a spec exige verificar na documentação oficial do cliente — não consultada nesta revisão).

### Linhagem

L1_tasks.md → l1-connect.yaml:867 → spec 3a6b402 → evals em subshell (10b96e2) e node-id fix (611dc6e) → sem implementação → ready. Fechamento ausente.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260817-cursor-codex-config.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-cursor-codex-config.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L867; fontes/batch-revalidated-specs28-sources/git/serve/README.md#L182-L207; fontes/batch-revalidated-specs28-sources/git/serve/.mcp.json; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83). Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: ausência das seções por cliente. FATO sobre evals: eval_1 só exige três títulos (não caminho, escopo nem reinício, embora declare B-1/B-3); eval_2 (`grep -qiE 'mcp list|/mcp'`) **já encontra correspondência no texto lido** pelo texto 'claude mcp list' e '/mcp lists' do bloco Claude Code — pode satisfazer a condição textual sem trabalho novo e não prova verificação em cada seção. A leitura do comando confirma que ele é global, sem delimitar seções. DECISÃO PENDENTE: suporte oficial a três clientes.

### Fluxo

Fluxo proposto: usuário do cliente X → seção X do README → caminho e escopo do arquivo de config → variáveis expandem na inicialização do cliente → passo de verificação específico → servidor conectado. Observado: seção única Claude Code + frase genérica.

### Consequências e risco

Sem ação: usuários de Cursor/Codex dependem de tentativa e erro; um caminho errado documentado seria pior que nenhum (contexto da spec). Impacto em adoção, não em dado. Confiança alta.

### Alternativas e recomendação

Recomendado: manter a intenção se os três clientes forem suportados; reescrever evals por seção (caminho, escopo, verificação, reinício) e registrar a fonte oficial consultada por cliente com data. Alternativa: declarar suporte só a Claude Code e encerrar. Não acoplar a nenhuma contagem de tools.

### Dependências e paralelismo

Independe de apex_status, PyPI e ClickHouse. four-to-five-doc-ripple a lista como dependência; essa relação deixa de importar se a ripple for encerrada. Pode correr em paralelo.

### Plano e aceite propostos

Se o suporte aos três clientes for mantido: (1) consultar fontes oficiais atuais de cada cliente e registrar URL/data; (2) escrever seções com caminho, escopo, verificação e quando reiniciar; (3) revisão documental por seção, confrontando cada afirmação com sua fonte; (4) substituir os evals genéricos por conferência que delimite cada seção, se o processo exigir eval. Menor entrega: README revisado. Controle negativo documental: uma seção sem verificação deve ser identificada na revisão. Não há necessidade demonstrada de novos testes de produto para esta edição.

### Comunicação entre responsáveis

Explicar: no README do SHA lido faltam seções específicas para Cursor/Codex/Claude Code. O eval_2 global encontra o bloco Claude, portanto não demonstra verificação por cliente. Conferir caminhos e escopos em fontes oficiais atuais antes de alterar a documentação; a presente revisão não os validou.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? A distinção projeto/usuário determina onde cada cliente procura configuração. Que caso o teste ainda não cobre? Caso documental a conferir: uma seção sem caminho, reinício ou verificação específica. Como eu explicaria isso para outro pod? A explicação deve ligar caminho e escopo a uma fonte oficial datada por cliente.

### Próxima ação e encerramento

Ação: decidir suporte a três clientes e reescrever evals. Owner a confirmar: Serve/documentação. Entrada: documentação oficial atual de cada cliente. Saída: README por cliente com fontes datadas, ou parked. Encerramento: seções conferidas e eval discriminante.

<a id="item-169"></a>

## T-20260817-drop-from-path — T-20260817-drop-from-path.md

Frente: Serve / L1 Connect — distribuição PyPI. Encaminhamento: decidir_distribuicao_v1_superficie_incompleta.

### Identidade e estado

`tasks/T-20260817-drop-from-path.md` (blob 3432cfc0). 'Drop the uvx --from fallback now that the package is published', M, standard, P2; owner `(none)`; depends_on pypi-publish, root-mcp-json, four-to-five-doc-ripple. Estado `ready`, `accepted: false`. Pod provável: Pod 3/Serve (inferido pelos caminhos; nenhum pod no arquivo). O título pressupõe publicação que não ocorreu.

### Intenção e benefício

Apontar configs e documentos para `uvx apex-mcp` simples depois da publicação, executando a nota já presente em `serve/.mcp.json`. Benefício: instalação de um comando e fim da instrução 'troque depois'.

### Feito, faltante e não comprovado

No SHA c3c3ea3, serve/.mcp.json usa args ["--from", "./serve", "apex-mcp"], o README Serve documenta fallback e o README raiz:91 também contém --from; .mcp.json raiz não está na árvore versionada. A captura preservada de 18/10 retorna 404 para o nome apex-mcp no PyPI; não demonstra toda a história do índice. Não foi localizada release identificada que satisfaça a precondição. README raiz não está em touches_paths nem no eval_1. O bloco principal Install já usa uvx apex-mcp, mas logo abaixo o README explica o fallback até publicação; a melhoria é tornar essa condição clara na ordem da leitura.

### Linhagem

L1_tasks.md → l1-connect.yaml:774 → spec 3a6b402 → evals em subshell (10b96e2) → sem execução → ready. Elos ausentes: pypi-publish (externo, não ocorreu) e root-mcp-json (não implementada); nenhuma PR posterior cita a unidade.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260817-drop-from-path.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-drop-from-path.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L774; fontes/batch-revalidated-specs28-sources/git/serve/.mcp.json; fontes/batch-revalidated-specs28-sources/git/serve/README.md#L182-L207; fontes/batch-revalidated-specs28-sources/git/README.md#L88-L92; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83); fontes/batch-claude-specs-sources/claude/fontes/publico/pypi_org_pypi_apex-mcp_json.txt. Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: fallback presente em três lugares (incluindo README raiz fora do escopo); raiz .mcp.json ausente; 404 no PyPI. FATO sobre evals: eval_1 usa `! grep` e trataria arquivo ausente como ausência de '--from' (falso positivo se o .mcp.json raiz não existir mas o grep falhar por arquivo), eval_2 falharia por arquivo ausente. INFERÊNCIA: o README do serve já apresenta o comando publicado como exemplo. DECISÃO PENDENTE: distribuição v1.

### Fluxo

Fluxo proposto: release no PyPI → editar .mcp.json (raiz e serve) para args ['apex-mcp'] → README sem fallback → cliente inicia `uvx apex-mcp`. Observado: cliente inicia `uvx --from ./serve apex-mcp` a partir do repositório.

### Consequências e risco

Sem ação: nenhuma regressão; executar antes da publicação apontaria o repositório para um pacote inexistente (anti-padrão declarado). A divergência atual do README (exemplo com uvx apex-mcp) pode confundir quem instala hoje — baixo impacto. Confiança alta.

### Alternativas e recomendação

Recomendado: manter bloqueada até release; ao reescrever, incluir README raiz na superfície e no eval. Paralelamente (independente), corrigir o exemplo do serve/README para refletir o estado atual (ou rotular como pós-publicação). Alternativa: decisão de não publicar → encerrar esta spec e manter --from como forma oficial.

### Dependências e paralelismo

Depende de pypi-publish (externo) e de root-mcp-json. A dependência four-to-five-doc-ripple é obsoleta. A correção do exemplo do README é independente e pode ocorrer já.

### Plano e aceite propostos

Se adotada após release: (1) editar os dois .mcp.json e os dois READMEs; (2) eval: arquivos existem e nenhum contém '--from' (falhar se ausentes); (3) igualdade dos blocos mcpServers; (4) controle: reintroduzir '--from' num dos quatro faz falhar. Doc: VALIDATION remove o limite. Antes da release: nenhuma ação, salvo nota no README.

### Comunicação entre responsáveis

Explicar: 'Esta spec só vale depois de publicar. Hoje o fallback --from é a forma correta; o README raiz também precisa entrar quando a hora chegar, e o exemplo do serve/README já antecipa um pacote inexistente.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Trocar --from antes de uma release identificada pode impedir o cliente de iniciar. Que caso o teste ainda não cobre? Caso a conferir: README raiz ou arquivo ausente escapando de um grep negativo. Como eu explicaria isso para outro pod? A troca de comando é um follow-up da publicação e envolve os dois READMEs e as configs.

### Próxima ação e encerramento

Ação: manter bloqueada e registrar a superfície faltante (README raiz). Owner a confirmar: Serve + release. Entrada: release publicada. Saída: spec revisada com quatro arquivos, ou encerrada se não houver publicação. Encerramento: configs/docs sem fallback e release verificada, ou decisão registrada.

<a id="item-170"></a>

## T-20260817-five-tools-assertion — T-20260817-five-tools-assertion.md

Frente: Serve / L1 Connect — apex_status. Encaminhamento: encerrar_meta_numerica_superada_preservando_controle.

### Identidade e estado

`tasks/T-20260817-five-tools-assertion.md` (blob 73830595). 'Re-pin the tool surface assertion at five', XS, standard, P2; owner `(none)`; depends_on `[T-20260817-register-apex-status]` (não satisfeita). Estado `ready`, `accepted: false`, sem assinatura. Pod provável: Pod 3/Serve (inferido pelos caminhos serve/; nenhum pod no arquivo).

### Intenção e benefício

Manter a asserção exata da superfície de tools ao passar de quatro para cinco nomes: uma tool acidental num servidor que um modelo pode chamar é evento de segurança. O benefício é o controle de allowlist, não o número.

### Feito, faltante e não comprovado

O controle já existe em forma mais nova: `test_the_contracted_tool_surface` compara `sorted(nomes) == CONTRACTED_TOOLS` com oito nomes (`test_server_tools.py:23-67`), introduzido como lista única em df6fe77 (#101, 2026-08-24) para evitar colisão entre pernas paralelas. Divergência com a spec: B-1 exige lista 'ordenada exata' (ordem de registro) e o teste atual compara ordenado alfabeticamente — escolha deliberada documentada no docstring. Falta: nada útil no número cinco. Não comprovado: que a suíte passe hoje.

### Linhagem

L1_tasks.md → l1-connect.yaml:306 → spec 3a6b402 → eval com node ID (611dc6e) → sem recibo de execução localizado neste recorte. Supersessão observada: 2fd8a09 (L2, cinco), d056c35 (L3, seis), 3758d00 (L5), 60e6ef2 (L6), df6fe77 (lista única). O nó `test_exactly_the_five_contracted_tools` nomeado pelo eval_1 não existe.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260817-five-tools-assertion.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-five-tools-assertion.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L306; fontes/batch-revalidated-specs28-sources/git/serve/tests/test_server_tools.py#L20-L67; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83); fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #101 e #86); fontes/batch-revalidated-specs28-sources/git/.github/workflows/ci.yml. Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: teste atual usa igualdade exata após sorted com oito nomes, e o node ID de cinco nomes não existe. O eval_2 por grep negativo não prova comportamento com tool extra. INFERÊNCIA: substituir somente a lista esperada por cinco produziria incompatibilidade com os oito registros; remover tools para fazê-la passar alteraria comportamento e exigiria decisão própria. DECISÃO PENDENTE: homologar o encerramento documental da meta numérica; o controle de igualdade permanece no código.

### Fluxo

Fluxo observado estaticamente: create_server → FastMCP.list_tools → [nomes] → sorted → == CONTRACTED_TOOLS → falha se tool extra/ausente. Proposto pela spec: mesma comparação com cinco nomes na ordem de registro.

### Consequências e risco

Sem reconciliação: risco de alguém executar literalmente uma spec antiga sobre uma superfície de oito tools. A incompatibilidade da lista é demonstrável estaticamente; regressão de segurança ou remoção de tools não foi observada. Confiança alta no código lido.

### Alternativas e recomendação

Recomendado: encerrar como superada (parked/done-substituída com motivo), apontando df6fe77 como sucessor do controle. Alternativa: se apex_status for adotado, o 'sucessor' é inserir uma linha em CONTRACTED_TOOLS — não precisa desta spec. Não recomendo reverter para comparação por ordem de registro: o docstring explica a colisão que ela causava.

### Dependências e paralelismo

Sem dependência para encerrar: o sucessor do controle (CONTRACTED_TOOLS) já está na main. Encerrar não bloqueia nem é bloqueado pela decisão apex_status; status-store-down-e2e deve perder esta dependência declarada. Paralelo com qualquer frente; nenhum estudo precisa esperar.

### Plano e aceite propostos

Proposta documental: registrar substituição da meta cinco pelo mecanismo de lista única e igualdade do teste atual, preservando a origem e atualizando o índice se o mantenedor adotar a disposição. Nenhum novo teste necessário para essa nota. A deriva sete/oito do gate stdio é pendência separada. Encerrar esta meta não aprova nem rejeita apex_status.

### Comunicação entre responsáveis

Explicar: 'A meta de cinco tools foi ultrapassada; o controle que a spec queria proteger existe como igualdade com lista única de oito nomes. Executar a spec reduziria o controle.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Restaurar cinco nomes conflita com a superfície atual de oito, e ordem de registro não é contrato vigente. Que caso o teste ainda não cobre? Caso a conferir: tool extra ou recurso promovido a tool sem reconciliação explícita. Como eu explicaria isso para outro pod? O valor preservado é igualdade exata de allowlist; cinco é uma meta histórica.

### Próxima ação e encerramento

Ação: encerramento documental com referência ao sucessor. Owner a confirmar: Serve. Entrada: teste atual no SHA. Saída: spec em parked com motivo. Encerramento: arquivo movido e índice L1 atualizado.

