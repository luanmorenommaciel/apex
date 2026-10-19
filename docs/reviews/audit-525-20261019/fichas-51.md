# Fichas documentais — lote 51

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-501"></a>

## PR#129 — feat(serve): apex-api — one HTTP layer between ClickHouse and its consumers

Frente: historico. Encaminhamento: integrada_sem_review_humana_com_evidencia_de_billing.

### Identidade e estado

PR #129, `feat/add_apex_api` → `main`; autora `sidymar` (commits também de "Augusto Silva"); `pod-3-serve`; criada em 2026-09-21 e integrada em 2026-10-06T19:56:50Z (merge `83a9624`); 16 commits; 42 arquivos. Ligada a 29 IDs do registro (S01–S09, S15–S24, F02/F03/F08/F09, E03/E04, G01/G03, L13, P04/P05, X01/X11). Reviews: só de bots (Codex `COMMENTED` e Copilot `COMMENTED`), nenhuma humana. Integrada na leva de 2026-10-06 (27 merges de PR entre 19:55:46Z e 20:32:30Z, com commits de merge do mantenedor, mais dois commits diretos na main, `fa0951f` e `c4541a5`), dentro do intervalo de 2026-09-20 a 2026-10-06 (created_at UTC) em que os 68 runs `CI` retornados pela API terminaram em `failure` (56) ou `cancelled` (12), sem `success` (`fontes/reconferencia/ponto01-intervalo-ci.json`; a contagem de 61 do pacote de 17/10 usava outro intervalo).

### Intenção e benefício

Pôr uma camada FastAPI entre o ClickHouse e quem o lê (decidido no Weekly Sync de 15/09): com `DATA_SOURCE=http` a console guarda um token de API e nenhuma credencial de banco, porque o modo atual envia a credencial de leitura a todo visitante.

### Feito, faltante e não comprovado

Feito: `serve/src/apex_api/` (app, auth, config, rotas de diagnóstico e recursos), `apex_mcp/ch.py` (+511), cliente HTTP do front (`http.ts`, `repository.ts`), `nginx.conf` com `/v1/` (conferido na main para o #102), `serve/RUNBOOK.md`, testes de app, OpenAPI, recursos e leituras da console. Review do Copilot, registrada pela API em 2026-09-21: "The job was not started because the account is locked due to a billing issue." É o relato do bot sobre o próprio job de review: o run `Running Copilot Code Review` 35616653528 terminou em `failure` às 15:06:24Z, 3 s antes da review 5268257112 (15:06:27Z). A API devolve o texto, mas ele não é consulta de billing nem a anotação originária dos jobs de CI, e não prova sozinho a causa dos jobs sem steps. Os dois runs com o head final (push e pull_request, 2026-09-23, tentativa 1) têm 11 jobs cada, com 0 steps (`fontes/git/_jobs-head-prs-outubro.json`). PRs empilhadas sobre esta: #143, #146, #150, #151, #153. Pendências públicas: token e exposição de docs/OpenAPI (#171), prova em navegador (#172), relação com o BFF do #122. Atualização 19/10: as rotas de diagnóstico da API chamam o mesmo `create_server` do MCP sobre o mesmo `ReadStore` (`serve/src/apex_api/routes/diagnostics.py:31-32`); `store_health`, da L1, alimenta `/v1/health`. Autoria dos commits: 15 de Sidymar e 1 de Augusto Silva (`fab6620`).

### Linhagem

Weekly Sync 15/09 → PR #129 (2026-09-21) → review do bot Codex e correções (`fab6620`, 2026-09-23) → runs de CI do head em `failure`, com 0 steps nos jobs coletados (causa de billing relatada pelo Copilot e pela #137) → merge sem review humana (2026-10-06) → empilhadas integradas em seguida → #171/#172 abertas.

### Fontes e corte

Snapshot (PR 129); dossiê (42 arquivos, 16 commits); `fontes/api-reviews/pr129-reviews.json` (texto do Copilot sobre billing) e `pr129-comments.json`; `fontes/git/_jobs-head-prs-outubro.json`; `fontes/git/_runs-push-main-por-dia.txt`; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos, reviews de bots, o texto de billing relatado pelo bot, obtido pela API, jobs sem steps. RELATADO: "ninguém precisa ter acesso ao nosso banco" funcionando. NÃO VERIFICADO: comportamento HTTP em runtime e no navegador. Review formal (API, observada em 2026-10-17T17:28:42Z): 2 — `chatgpt-codex-connector[bot]` COMMENTED em 2026-09-21; `copilot-pull-request-reviewer[bot]` COMMENTED em 2026-09-21. `APPROVED` humano antes do merge: não. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 4 (chatgpt-codex-connector[bot] 4). Runs do Actions com o head `fab6620` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` push failure, run 35898017600, tentativa 1, created_at 2026-09-23 17:47:28Z, run_started_at 2026-09-23 17:47:28Z, updated_at 2026-09-23 17:47:32Z (antes do merge pelo updated_at); jobs coletados desta tentativa: 11, steps: 0; `CI` pull_request failure, run 35898024026, tentativa 1, created_at 2026-09-23 17:47:31Z, run_started_at 2026-09-23 17:47:31Z, updated_at 2026-09-23 17:47:35Z (antes do merge pelo updated_at); jobs coletados desta tentativa: 11, steps: 0.

### Fluxo

Fluxo HTTP: browser → nginx `/v1/` → `apex_api` (token) → `apex_mcp/ch.py` → ClickHouse; alternativa ainda presente: browser → `/clickhouse/` → ClickHouse.

### Consequências e risco

Alto: é a maior mudança de superfície da leva e a fronteira de segurança da console. Entrou sem revisão humana registrada e sem CI verde observado no head final. A segurança de token e de docs públicos é exatamente o que a #171 discute. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter integrada e priorizar #171 e #172 como provas da fronteira (recomendado); (b) reverter — perderia a separação credencial × token e as PRs empilhadas.

### Dependências e paralelismo

Depende de DEC-08 (#171) para a política de token e de #172 para a prova em navegador; prova hospedada depende de DEC-01.

### Plano e aceite propostos

Passo mínimo: incluir os testes de `apex_api` na prova pós-integração; para #171, matriz perfil × rota com testes 401; controle negativo: rota `/v1` sem token deve recusar.

### Comunicação entre responsáveis

Para a consolidação: "PR #129 criou a API HTTP da console; entrou sem review humana registrada e sem CI verde observado no head final; a fronteira de token está na #171".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — manter só o acesso direto deixaria a credencial do banco em todo navegador. (b) Que caso o teste ainda não cobre? — `/docs` e `/openapi.json` expostos no perfil compartilhado. (c) Como eu explicaria isso para outro pod? — "a console pode falar com uma API com token em vez de falar com o banco". (d) O modo `/clickhouse/` deve ser removido no perfil compartilhado?

### Próxima ação e encerramento

Owner a confirmar: donos da #171 (DEC-08) e da #172 (Pod 1). Entrada: este registro. Saída: política de token e recibo de navegador. Encerramento: a PR segue integrada.

<a id="item-502"></a>

## PR#131 — engine: fail fast on connect when spark_events schema is behind

Frente: historico. Encaminhamento: historico_integrado_com_followup_delimitado.

### Identidade e estado

PR #131 de Augusto Silva (gustocezar), mergeada em 06/10/2026 por luanmorenommaciel; head 7b7b9b4, base a289e53; 4 commits, +479/−13, 5 arquivos. Fecha #95. Sem reviews formais registradas.

### Intenção e benefício

Falhar rápido no connect do Engine quando o volume ClickHouse tem schema antigo (docker-entrypoint-initdb.d só roda na 1ª inicialização), nomeando colunas faltantes antes de qualquer análise.

### Feito, faltante e não comprovado

Implementado: preflight de system.columns no banco configurado, conjunto manual de 35 colunas, remoção de qualificadores fixos, trim/fallback da configuração e mensagem específica para banco alternativo. Provisionamento de outro banco permanece fora do escopo. Resultados locais do corpo são relatos nos SHAs citados; jobs sem steps no recorte não comprovam causa atual de billing nem execução do head final.

### Linhagem

4 commits: d92e2c3 (preflight), d96d9b5 (leituras no banco verificado + aponta make -C infra apply-ddl), 672dc1f (normalização do env de database), 7b7b9b4 (mensagem correta para banco não-apex). Referenciada por #139 e #155; alinhada com #129.

### Fontes e corte

Corpo da PR (camada apex-flow + context 10/10 + registro original), commits, API pública do GitHub em 19/10/2026; base histórica c3c3ea3. Nenhum teste reexecutado.

### Classe e limite da evidência

Prova autor-declarada, local: preflight 8; Engine+root 226 passadas/11 skips em 7b7b9b4; 160+65 em 672dc1f; controles negativos contra pais; aceite Task-Spec independente no SHA. Classe: teste unitário local com fake client + relato histórico de ClickHouse real em SHAs anteriores (d96d9b5 + fab6620). Limite: não certifica CI remota nem runtime do head final.

### Fluxo

connect() → system.columns do banco configurado → compara com REQUIRED_SPARK_EVENTS_COLUMNS → SchemaOutOfDateError (nomes+contagem) ou prossegue; falhas de conexão propagam sem alteração.

### Consequências e risco

Baixo residual: o conjunto de colunas é mantido manualmente e pode derivar das queries de estágio; banco alternativo segue sem provisionamento automatizado. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Manter o histórico e reutilizar o endurecimento já tratado em #154/#155 para drift entre consultas e constante; não abrir duplicata por existir um conjunto manual. Provisionamento de banco alternativo é recorte próprio se o time o requerer.

### Dependências e paralelismo

Fecha #95. Paralela a #129 (config de database). Não bloqueia nada; #139/#155 a referenciam.

### Plano e aceite propostos

Sem reabertura automática: confrontar a constante com as queries na revisão #155. Entrada: diff e consultas da mesma árvore. Saída: controle que detecte coluna realmente lida e ausente; preservar teste do banco alternativo e propagação de erro. Uma execução futura deve registrar SHA e ambiente; merge não é aceite.

### Comunicação entre responsáveis

Corpo comunica limites explicitamente (billing, skips, histórico vs. head atual). Atenção: relatos de execução real pertencem a SHAs antigos e estão corretamente datados.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — ler o banco literal apex faria o preflight divergir do banco configurado; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — drift entre constante e query da mesma árvore. Como eu explicaria isso para outro pod? — Falhar rápido no connect do Engine quando o volume ClickHouse tem schema antigo (docker-entrypoint-initdb.d só roda na 1ª inicialização), nomeando colunas faltantes antes de qualquer análise.

### Próxima ação e encerramento

Encaminhar a manutenção do guard a #154/#155, responsável a confirmar no Engine; encerrar este histórico preservando a prova e sem prometer provisionamento de bancos alternativos.

<a id="item-503"></a>

## PR#132 — docs: reconcile current contract and Serve state

Frente: historico. Encaminhamento: historico_integrado_com_followup_delimitado.

### Identidade e estado

PR #132 de gustocezar, mergeada em 06/10/2026; head 1f3c274, 1 commit, +40/−23, 5 arquivos. Documental. Sem reviews.

### Intenção e benefício

Alinhar pipeline, changelog, planejamento Serve, proposta L4 e README da Console com o contrato v0.6 e oito tools, removendo descrições v0.4/v0.5 de quatro tools.

### Feito, faltante e não comprovado

Cinco documentos alinhados a v0.6/oito tools, com fronteira de execution_id preservada. No SERVE-LEGS ainda resta texto contraditório sobre list_runs: correção N10 a coordenar com #164. README raiz foi tratado separadamente na #134 e alterações de contrato exigem decisão própria.

### Linhagem

1 commit 1f3c274; relacionada a #127 (linha separada do README); precede #133/#134 (mesma onda documental). Resíduo posterior: contradição list_runs em SERVE-LEGS.md, registrada na #181/proposta N10.

### Fontes e corte

Corpo da PR e metadados via API pública em 19/10/2026. Sem leitura dos arquivos alterados no diff.

### Classe e limite da evidência

Prova autor-declarada: Serve 239 passadas, verificação AST das oito tools, git diff --check. Classe: validação documental/estática local. Limite: não reexecutado; não verifica a qualidade factual de cada linha alterada.

### Fluxo

Documentos desatualizados → alinhamento com v0.6/oito tools → CONTRACT.md intencionalmente inalterado.

### Consequências e risco

Risco baixo: merge de documento não ratifica política (especialmente fronteiras de privacidade e execution_id); leitores podem tratar 'alinhado' como 'aprovado'. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Preservar o histórico; corrigir o resíduo documental N10 em recorte combinado com #164 ou follow-up pequeno, comparando diffs antes. Não é razão para bloquear toda documentação.

### Dependências e paralelismo

Paralela a #127/#133/#134. Nenhuma dependência de código.

### Plano e aceite propostos

Plano: PR documental única. Resultado/aceite é relato histórico do corpo, não nova concessão nesta revisão; follow-up documental (SERVE-LEGS) pendente em outro recorte.

### Comunicação entre responsáveis

Corpo distingue o que foi alinhado do que foi deliberadamente excluído; comunicação adequada.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — preservar números antigos induziria leitura errada da superfície disponível; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — afirmação residual do SERVE-LEGS contra tools registradas. Como eu explicaria isso para outro pod? — Alinhar pipeline, changelog, planejamento Serve, proposta L4 e README da Console com o contrato v0.6 e oito tools, removendo descrições v0.4/v0.5 de quatro tools.

### Próxima ação e encerramento

Pod3/mantenedor a confirmar: escolher destino N10/#164, editar afirmação residual e confrontar com tools registradas na mesma árvore; saída é texto coerente sem ratificar mudança de contrato.

<a id="item-504"></a>

## PR#133 — docs: propose source correlation privacy boundary

Frente: historico. Encaminhamento: historico_integrado_com_followup_delimitado.

### Identidade e estado

PR #133 de gustocezar, mergeada em 06/10/2026; head 5cd5968, 1 commit, +170, 1 arquivo (ADR proposto). Referenciada por #141 como ADR-004. Sem reviews.

### Intenção e benefício

Propor (não implementar) fronteira de privacidade opt-in para correlação de código-fonte (F4.1): nada de stack traces brutos, paths absolutos, snippets, texto de query ou segmentos de home em repouso.

### Feito, faltante e não comprovado

ADR-004 permanece proposed na base lida, com cinco precondições a decidir pelo owner: (1) permitir localizador relativo em repouso; (2) nome da configuração opt-in, semântica da raiz e sintaxe permitida; (3) provedor de identidade de notebook e comportamento indisponível; (4) local do payload e migração/compatibilidade; (5) primeiro consumidor público. Nenhuma implementação ou ratificação comprovada; merge de proposta não é aceite. Usar a lista literal do ADR para decidir, não este resumo como substituto.

### Linhagem

1 commit 5cd5968; origem F4.1; citada como ADR-004 em #141; integra a onda documental de 06/10.

### Fontes e corte

Corpo da PR via API pública em 19/10/2026; conteúdo do ADR não lido integralmente (arquivo único, +170 linhas).

### Classe e limite da evidência

Prova autor-declarada: git diff --check; verificação estática do handling de stage-submission no JAR e do path scrubbing do Collector. Classe: leitura estática. Limite: nenhuma claim de runtime.

### Fluxo

Fluxo PROPOSTO: observação Spark → avaliação local da localização → representação opt-in limitada → referência permitida em telemetria; implementação depende das cinco decisões do ADR-004.

### Consequências e risco

Risco médio conceitual: sem fronteira acordada, uma implementação futura poderia persistir dados identificadores; também há risco de se ler 'mergeado' como 'ratificado'. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Alternativas avaliadas no ADR: localizador relativo, referência opaca, comportamento notebook. Recomendação: confirmar status do ADR (aceito/revisado) antes de qualquer implementação F4.1.

### Dependências e paralelismo

Independente de código; relaciona-se a F4.1 e ao Collector. Claude trata ADR-004 na divisão de trabalho.

### Plano e aceite propostos

Plano: ADR como draft até decisão. Aceite: status do ADR explícito; pendente fora desta PR.

### Comunicação entre responsáveis

Corpo é explicitamente uma proposta; comunicação correta sobre o que merge significa.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — persistir localização sem a decisão de privacidade pode expor dados fora da fronteira escolhida; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — o fluxo proposto ainda não foi implementado nem ratificado. Como eu explicaria isso para outro pod? — Propor (não implementar) fronteira de privacidade opt-in para correlação de código-fonte (F4.1): nada de stack traces brutos, paths absolutos, snippets, texto de query ou segmentos de home em repouso.

### Próxima ação e encerramento

Levar N07/ADR-004 ao owner indicado no documento, Luan, sem presumir resposta; registrar cada uma das cinco decisões, adiamentos e critérios antes de implementar F4.1.

<a id="item-505"></a>

## PR#134 — docs: align README with current contract

Frente: historico. Encaminhamento: historico_integrado_sem_nova_acao_obrigatoria.

### Identidade e estado

PR #134 de gustocezar, mergeada em 06/10/2026; head 3340e2f, 1 commit, +7/−3, 1 arquivo (README raiz). Sem reviews.

### Intenção e benefício

Atualizar README raiz de v0.5/quatro tools para v0.6/oito tools e explicitar a fronteira de reconstrução AQE por estágio.

### Feito, faltante e não comprovado

Feito: README em v0.6, oito tools listadas, boundary execution_id declarado (produtor existe; mapeamento read-side e prova runtime pendentes). Faltante: nada. Não comprovado: nenhuma claim de runtime (correto para docs).

### Linhagem

1 commit 3340e2f; compõe merge-tree limpo com #127 (linhas separadas); precede #164 (revisão READMEs ainda aberta).

### Fontes e corte

Corpo da PR via API pública em 19/10/2026; README atual na main não re-lido.

### Classe e limite da evidência

Prova autor-declarada: git diff --check; checagem AST das oito tools contra a tabela do README; merge-tree limpo com #127. Classe: validação estática/documental. Limite: AST amarra o README a um instante; drift futuro não impedido.

### Fluxo

Tools registradas → contrato v0.6 → README → leitor.

### Consequências e risco

Risco baixo: tabela do README pode re-derivar após próxima tool; leitor pode assumir reconstrução AQE pronta (boundary mitiga). Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Alternativa: automação de drift (gate AST recorrente). Recomendação: considerar no gate stdio N16, que já lida com deriva de superfície.

### Dependências e paralelismo

Paralela a #127; relaciona-se a #164 aberta.

### Plano e aceite propostos

Preservar README integrado e revisar #164 contra o código/contrato da árvore escolhida; manter oito nomes e limites da correlação AQE, sem converter anotação de metadado em prova de leitura somente. Saída é correspondência documental revisável; não aceite runtime.

### Comunicação entre responsáveis

Corpo registra a boundary e a composição com #127 com clareza.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — confundir execução produzida com atribuição pronta prometeria correlação não entregue; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — drift futuro da tabela contra a superfície registrada. Como eu explicaria isso para outro pod? — Atualizar README raiz de v0.5/quatro tools para v0.6/oito tools e explicitar a fronteira de reconstrução AQE por estágio.

### Próxima ação e encerramento

Nenhuma ação; alinhar com a revisão da #164 aberta.

<a id="item-506"></a>

## PR#135 — fix(serve): withhold unresolved replay deltas

Frente: historico. Encaminhamento: historico_integrado_com_followup_delimitado.

### Identidade e estado

PR #135 de gustocezar, mergeada em 06/10/2026; head 474284c, 2 commits, +72/−32, 3 arquivos; base da pilha #144. Refs #117. Sem reviews.

### Intenção e benefício

verify_fix e suggest_fix não devem narrar magnitude de replay abaixo do piso de ruído registrado ou sem piso, dizendo 'não resolvido' em vez de insinuar zero.

### Feito, faltante e não comprovado

Feito: renderer único _replay_measurement nos dois caminhos (anti-deriva de texto); payload estruturado mantém measured_delta_pct bruto. Faltante: semântica de igualdade no piso (deixada para #117). Não comprovado: comportamento em consumidor que leia o payload bruto (Front exibe campos da projeção — ver N03).

### Linhagem

2 commits: 3c889f8 (hide unresolved deltas), 474284c (igualdade de piso deixada para decisão de contrato). Base da pilha que leva a #144; refs #117.

### Fontes e corte

Corpo da PR via API pública em 19/10/2026; diagnose.py não re-lido em c3c3ea3.

### Classe e limite da evidência

Prova autor-declarada local: 239 passadas em a289e53, 243 em 474284c, 61 focadas; 4 asserções falharam contra origin/main (controle). Classe: teste unitário local com controles negativos. Limite: só texto renderizado; payload bruto inalterado; sem runtime compartilhado.

### Fluxo

Medição replay → renderer compartilhado → veredito textual retido abaixo/sem piso → verify_fix e suggest_fix com linguagem idêntica.

### Consequências e risco

Risco residual: consumidor do payload estruturado (API/Front) ainda pode apresentar a magnitude como resultado; projeção FIX_VERIFICATION_SQL compara sem checar piso inválido (proposta N03, leitura estática). Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Alternativa registrada: não assertionar igualdade (mantida, #117). Recomendação: tratar N03 como follow-up ligado a #117.

### Dependências e paralelismo

Refs #117 (contrato de piso). Pilha: #144 apoiada nela. Paralela às demais de 06/10.

### Plano e aceite propostos

Plano: fix de apresentação + testes. Resultado/aceite é relato histórico do corpo, não nova concessão nesta revisão; contrato de piso segue em #117.

### Comunicação entre responsáveis

Corpo separa claramente o que mudou (texto) do que não mudou (payload, thresholds, contrato).

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — mostrar delta bruto como magnitude resolvida ignoraria o piso de ruído; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — igualdade do piso depende da política #117. Como eu explicaria isso para outro pod? — verify_fix e suggest_fix não devem narrar magnitude de replay abaixo do piso de ruído registrado ou sem piso, dizendo 'não resolvido' em vez de insinuar zero.

### Próxima ação e encerramento

Registrar N03 como complemento de #117 com dono, sem ampliar escopo desta ficha.

<a id="item-507"></a>

## PR#136 — fix(front): keep mechanism and runtime verdicts independent

Frente: historico. Encaminhamento: historico_integrado_com_followup_delimitado.

### Identidade e estado

PR #136 de gustocezar, mergeada em 06/10/2026; head 2fa0781, 2 commits, +98/−16, 2 arquivos (rules.ts + testes). Sem reviews. Parte da combinação local descrita em #140.

### Intenção e benefício

Desacoplar veredito de mecanismo do veredito runtime no contrato do Front; rejeitar só o par contraditório certified=true + unresolved.

### Feito, faltante e não comprovado

Feito: regra atualizada; follow-up 2fa0781 corrige narração (−12% previsto vs piso 5% descrito como regressão, não 'dentro do piso'); comparações estritas, held/vacant e fronteiras zero/zero preservadas. Faltante: prova de browser (explicitamente fora). Não comprovado: Node 22 local (só Node 26); CI do head anterior bloqueada por billing (#130), CI do head novo 'a verificar'.

### Linhagem

2 commits: 78062d3 (independência mechanism/runtime), 2fa0781 (narração de slowdown além do piso). Relaciona-se a #130 (billing) e #140 (combinação local).

### Fontes e corte

Corpo da PR via API pública em 19/10/2026; rules.ts não re-lido em c3c3ea3.

### Classe e limite da evidência

Prova autor-declarada local em 2fa0781: 39 focadas, Front 93; typecheck/lint/build Node 26; mutações controladas detectadas; aceite Task-Spec independente. Classe: teste unitário local + mutação. Limite: sem browser, sem Node 22, sem CI remota do head final.

### Fluxo

Veredito mecanismo (true/false/unknown) × runtime (certified/unresolved) → rejeita só par contraditório → narração descreve slowdown além do piso como regressão.

### Consequências e risco

Risco baixo: deriva futura entre vereditos em novos consumidores; estados legítimos 'mechanism false + runtime resolved' podem confundir novos devs. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Alternativa: acoplamento anterior (rejeitado). Recomendação: documentar o estado legítimo no contrato (#165) se ainda não estiver.

### Dependências e paralelismo

Sem dependências duras; #140 a menciona como parte da combinação local.

### Plano e aceite propostos

Plano: fix de regra + testes. Resultado/aceite é relato histórico do corpo, não nova concessão nesta revisão; CI remota do head deve constar da reconciliação #156/#130 se exigida.

### Comunicação entre responsáveis

Corpo comunica limites (browser, Node 22, billing) explicitamente.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — acoplar mecanismo e magnitude esconderia estados legítimos independentes; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — navegador real e perfil de produção não são provados pelo unitário. Como eu explicaria isso para outro pod? — Desacoplar veredito de mecanismo do veredito runtime no contrato do Front; rejeitar só o par contraditório certified=true + unresolved.

### Próxima ação e encerramento

Histórico integrado; prova remota futura deve usar SHA e escopo do Front, com destino de CI/governança pertinente. #156 não deve virar tracker genérico de toda validação Front. A decisão funcional do Verify permanece #117.

<a id="item-508"></a>

## PR#137 — fix(front): recognize retry pressure findings

Frente: historico. Encaminhamento: historico_integrado_com_followup_delimitado.

### Identidade e estado

PR #137 de gustocezar, mergeada em 06/10/2026 20:11 UTC; head 2c3ae4b, 1 commit, +4/−2, 1 arquivo. Sem reviews.

### Intenção e benefício

Adicionar RETRY_PRESSURE aos tipos de finding conhecidos do contrato do Front, pois o Engine já o emitia.

### Feito, faltante e não comprovado

O diff acrescenta RETRY_PRESSURE a KnownFindingType e ao comentário correspondente. Não inclui TAIL_OUTLIER, que segue fora da lista na base histórica, com acompanhamento #166. #127 integrou antes da #137; a ordem citada no corpo não é bloqueio técnico atual. Comportamento de tipo desconhecido deve ser lido/testado no consumidor, sem inferir perda silenciosa só pela enumeração.

### Linhagem

1 commit 2c3ae4b; coordena com #127 (gate TAIL_OUTLIER) e #130 (billing). Referenciada pela combinação local #140.

### Fontes e corte

Corpo da PR via API pública em 19/10/2026; arquivo de tipos do Front não re-lido.

### Classe e limite da evidência

Prova autor-declarada: typecheck, lint, Front 87 passadas. Classe: teste unitário local. Limite: sem controles negativos citados; CI remota bloqueada por billing na época.

### Fluxo

Engine emite finding → contrato do Front reconhece o tipo → Console representa finding tipado.

### Consequências e risco

Risco baixo-médio: fallback para tipos desconhecidos não auditado; cobertura parcial de tipos pode gerar fila silenciosa de findings não representados (tratada em #166). Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Alternativa: incluir TAIL_OUTLIER já (adiada, dependia de #127). Recomendação: testar o fallback de tipo desconhecido como follow-up barato.

### Dependências e paralelismo

#127 já estava integrada antes desta PR. #166 é o destino para TAIL_OUTLIER nos consumidores; coordenação com a superfície Front, sem dependência atual artificial de novo merge da #127.

### Plano e aceite propostos

Plano: fix de contrato mínimo. Resultado/aceite é relato histórico do corpo, não nova concessão nesta revisão; fallback como follow-up.

### Comunicação entre responsáveis

Corpo honesto sobre escopo e CI bloqueada.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — omitir um tipo conhecido pode retirar sua representação tipada no consumidor; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — consumidor de TAIL_OUTLIER/tipo desconhecido em #166. Como eu explicaria isso para outro pod? — Adicionar RETRY_PRESSURE aos tipos de finding conhecidos do contrato do Front, pois o Engine já o emitia.

### Próxima ação e encerramento

Revisar #166 no Pod1/Engine, responsável a confirmar, e escolher controle que use TAIL_OUTLIER/tipo desconhecido no consumidor concreto. Não propor reabrir a #137 histórica.

<a id="item-509"></a>

## PR#138 — ci(front): reject warnings and empty suites

Frente: historico. Encaminhamento: historico_integrado_sem_nova_acao_obrigatoria.

### Identidade e estado

PR #138 de gustocezar, mergeada em 06/10/2026 20:12 UTC; head 4b5798d, 1 commit, +2/−5, 3 arquivos (.github/workflows/ci.yml, front/package.json e front/vitest.config.ts). Sem reviews.

### Intenção e benefício

Fazer o gate de CI do Front falhar em warnings do ESLint e em suíte de testes vazia, sem mudar comportamento para suíte populada e limpa.

### Feito, faltante e não comprovado

Feito: --max-warnings 0 no lint e falha de suíte vazia. Faltante: política para novas regras começarem como warning (pergunta aberta no corpo). Não comprovado: rechecagem remota pós-billing visível no snapshot; a evidência Node 22 é local, não publicada.

### Linhagem

1 commit 4b5798d; toca o mesmo workflow de #128 (seções distintas; rechecagem pedida). Relatório Node 22 (81 focadas, 136 Front, build idêntico byte a byte ao Node 26) veio como apêndice offline não publicado; GPG não verificado.

### Fontes e corte

Corpo e metadados da PR; merge diff com .github/workflows/ci.yml, front/package.json e front/vitest.config.ts, no SHA e recorte preservados. A evidência Node 22 do apêndice continua relato separado.

### Classe e limite da evidência

Prova autor-declarada: controles negativos (warning falha lint; suíte vazia falha testes), typecheck/lint/build, Front 87, YAML validado. Classe: controles locais + workflow. Limite: não é execução remota; combinação Node 22 não valida Ubuntu x64, versões futuras do node flutuante, browser ou ClickHouse real.

### Fluxo

ESLint/suíte → gate estrito → verde só se limpo e populado.

### Consequências e risco

Risco baixo: gate zero-warning torna cada nova regra bloqueante; node-version flutuante 22 no CI pode divergir do Node 22.23.3 validado localmente. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Alternativa: max-warnings > 0 com cap (há controle de cap no apêndice). Recomendação: decidir política de novas regras junto ao time.

### Dependências e paralelismo

Coordena com #128 (mesmo arquivo, seções separadas); billing #130 na época; #160 mudou workflows depois — estado atual exige releitura.

### Plano e aceite propostos

Plano: mudança de CI + controles. Resultado/aceite é relato histórico do corpo, não nova concessão nesta revisão; rechecagem remota era condição registrada.

### Comunicação entre responsáveis

Corpo registra conflito esperado com #128 e a natureza offline da evidência Node 22 — comunicação cuidadosa.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — aceitar warning ou suíte vazia permitiria verde sem o critério declarado; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — semântica de nova regra warning precisa de decisão. Como eu explicaria isso para outro pod? — Fazer o gate de CI do Front falhar em warnings do ESLint e em suíte de testes vazia, sem mudar comportamento para suíte populada e limpa.

### Próxima ação e encerramento

Conferência estática com #160 preserva lint --max-warnings 0 e ausência de passWithNoTests. Sem repetição automática de teste já relatado; política para novas regras é decisão do time, separada de defeito observado.

<a id="item-510"></a>

## PR#139 — test(engine): harden SQL to DDL column guard

Frente: historico. Encaminhamento: historico_integrado_sem_nova_acao_obrigatoria.

### Identidade e estado

PR #139 de gustocezar, mergeada em 06/10/2026 20:12 UTC; head 087ce22, 1 commit, +20/−2, 1 arquivo. Sem reviews.

### Intenção e benefício

Endurecer o guard SQL→DDL do Engine para verificar colunas referenciadas contra o DDL declarado, evitando query silenciosa sobre coluna inexistente.

### Feito, faltante e não comprovado

Diff remove apenas job_id e attributes de NOT_COLUMNS; a allowlist restante permanece. Acrescenta controle parametrizado para que leitura dessas colunas exija declaração em DDL. Comentário explica que são colunas de origem e não aliases. Não verifica schema instalado em deployment.

### Linhagem

1 commit 087ce22; revisar junto com #131 (mesmo caminho de preflight); referenciada por #155.

### Fontes e corte

Corpo da PR via API pública em 19/10/2026; guard e DDL não re-lidos.

### Classe e limite da evidência

Prova autor-declarada local: 7 testes do guard, Engine 125 passadas/11 skips, validada contra o head da #131 na época. Classe: teste estático unitário. Limite: não substitui execução contra ClickHouse real; skips não são cobertura.

### Fluxo

Queries do Engine → colunas referenciadas → comparadas ao DDL declarado → falha em coluna não declarada.

### Consequências e risco

Limite: extrator estático com regex/exclusões; verificar igualdade do universo necessário em #154/#155. Não há evidência de incidente atual ou de remoção de toda a allowlist. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

Preservar a correção focada e reutilizar #154/#155 para o restante; não criar tarefa de documentar a remoção de uma allowlist que continua no código.

### Dependências e paralelismo

Par de revisão com #131; #155 dependente conceitual.

### Plano e aceite propostos

Plano: follow-up focado do guard. Resultado/aceite é relato histórico do corpo, não nova concessão nesta revisão.

### Comunicação entre responsáveis

Corpo direto; registro de coordenação com #131 adequado.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — tratar job_id/attributes como aliases permitiria coluna sem DDL passar pelo guard; é consequência do desenho, não relato de incidente novo. Que caso o teste ainda não cobre? — extrator geral de SQL tem escopo restrito. Como eu explicaria isso para outro pod? — Endurecer o guard SQL→DDL do Engine para verificar colunas referenciadas contra o DDL declarado, evitando query silenciosa sobre coluna inexistente.

### Próxima ação e encerramento

Sem nova ação na PR histórica. Na revisão #155, confirmar controles sobre colunas lidas, aliases e função SQL com diff/DDL da mesma base. Responsável a combinar no Engine.

