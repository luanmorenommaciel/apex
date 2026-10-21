# Fichas documentais — lote 19

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-181"></a>

## T-20260817-status-assembler — T-20260817-status-assembler.md

Frente: Serve / L1 Connect — apex_status. Encaminhamento: decidir_com_familia_apex_status.

### Identidade e estado

`tasks/T-20260817-status-assembler.md` (blob 0d1933b1). 'Add the pure diagnose.status assembler', S, standard, P2; owner `(none)`; depends_on `[T-20260817-serverstatus-model]` (satisfeita: done). Estado `ready`, `accepted: false`, sem assinatura. Pod provável: Pod 3/Serve (inferido pelos caminhos serve/; nenhum pod no arquivo). Marcada '▶︎' (pronta) no índice L1_tasks.md.

### Intenção e benefício

Transformar números de saúde em ServerStatus acionável como função pura (sem I/O), como as demais diagnoses da lane, para testar sem ClickHouse. Benefício: remediação clara (store vazio ≠ quebrado; coluna faltante aponta a lane infra).

### Feito, faltante e não comprovado

Não implementado: `diagnose.py` não define `status` (lista de funções no SHA não contém). O contexto manda reutilizar o conjunto de colunas exigidas de `serve/tools/read_only_gate.py:33-59` como constante compartilhada; isso também não ocorreu. Falta todo o escopo. Não comprovado: se o conjunto de colunas do gate ainda reflete o contrato atual — o próprio gate rotula os conjuntos como 'Contract v0.2' (`read_only_gate.py:33`), enquanto README/CONTRACT citam v0.5; não conferi coluna a coluna.

### Linhagem

L1_tasks.md → l1-connect.yaml:158 → spec 3a6b402 → eval com node IDs (611dc6e) → sem implementação → ready. Dependência satisfeita (serverstatus-model done). Elo ausente: decisão de seguir com apex_status depois que L2 ocupou o 'quinto' lugar (PR #83: 'whichever lands second reconciles').

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260817-status-assembler.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-status-assembler.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L158; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_mcp/diagnose.py; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_mcp/models.py#L572-L612; fontes/batch-revalidated-specs28-sources/git/serve/tools/read_only_gate.py#L33-L59; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83). Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: ausência de diagnose.status; ServerStatus presente. FATO sobre os evals: eval_2 é grep negativo de `get_client|clickhouse_connect|ReadStore(` em diagnose.py — não exige a implementação nova, por leitura estática (diagnose não tem I/O), logo não discrimina B-1; eval_1 só existe quando os três testes nomeados forem escritos. INFERÊNCIA: implementação seria pequena. DECISÃO PENDENTE: adoção da família.

### Fluxo

Fluxo proposto: store_health + table_columns + resolve_settings + lista de tools → [números, conjuntos, defaulted] → diagnose.status (puro) → [ServerStatus: connected, age, contract_tables, remediation] → apex_status. Nada observado em runtime.

### Consequências e risco

Sem ação: nenhuma regressão; o status MCP segue inexistente. Se implementado isoladamente sem tool, vira mais código sem consumidor (como ServerStatus). Confiança alta; sem incidente.

### Alternativas e recomendação

Recomendado: decidir a família primeiro; se adotada, fundir assembler + degraded-path numa só entrega revisável (mesmo arquivo, mesmo teste), com constante de colunas extraída do contrato e não do gate. Alternativa: encerrar como não adotada. Padrão: 'functional core, imperative shell' — vantajoso para teste; custo é mais uma camada.

### Dependências e paralelismo

Depende de: decisão sobre apex_status; dados de contrato atualizados (colunas exigidas). Estudo do mapeamento remediação↔erro pode correr em paralelo. Implementação bloqueia status-degraded-path e register-apex-status, não outras frentes.

### Plano e aceite propostos

Se a funcionalidade for adotada: (1) definir a lista de colunas contra o contrato escolhido, compartilhada sem importar a camada de conexão; (2) preservar o núcleo puro com saúde, conjuntos, settings e relógio como entradas explícitas; (3) casos nomeados de idade, coluna faltante e store vazio; (4) bloquear dependências de conexão no teste e inspecionar imports/chamadas da função. Patch apenas em ch.get_client é evidência parcial de ausência de I/O e não prova universal. Documentar limites do relógio do emissor. Se não adotada, registrar a disposição da spec.

### Comunicação entre responsáveis

Explicar: diagnose.py não define status no SHA lido. O grep negativo não exige a função nova nem prova pureza; núcleo com entradas explícitas, leitura estática e controles de dependências oferecem prova proporcional. A decisão sobre o consumidor pode ocorrer em paralelo ao estudo do assembler.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? I/O dentro do assembler acoplaria o payload de saúde ao estado de conexão. Que caso o teste ainda não cobre? Caso a conferir: idade negativa pelo relógio do emissor e bloqueio de dependências além de get_client. Como eu explicaria isso para outro pod? O núcleo recebe dados e produz ServerStatus; o acesso ao store pertence à fronteira externa.

### Próxima ação e encerramento

Ação: incluir na decisão da família. Owner a confirmar: Serve. Entrada: decisão + lista atual de colunas do contrato. Saída: spec revisada (com controle por monkeypatch) ou parked. Encerramento: status coerente com a decisão.

<a id="item-182"></a>

## T-20260817-status-degraded-path — T-20260817-status-degraded-path.md

Frente: Serve / L1 Connect — apex_status. Encaminhamento: decidir_com_familia_apex_status.

### Identidade e estado

`tasks/T-20260817-status-degraded-path.md` (blob fd680450). 'Make status survive an unreachable store', S, standard, P2; owner `(none)`; depends_on `[T-20260817-status-assembler]` (não satisfeita). Estado `ready`, `accepted: false`, sem assinatura. Pod provável: Pod 3/Serve (inferido pelos caminhos serve/; nenhum pod no arquivo).

### Intenção e benefício

Fazer a chamada de status responder quando o banco está fora (ServerStatus connected=False com código sanitizado e próxima ação), em vez de levantar. É o caso de uso central do L1: 'um status que falha com o banco fora só funciona quando você não precisa'.

### Feito, faltante e não comprovado

Não implementado (depende do assembler inexistente). Existe hoje um análogo HTTP: `/v1/health` da API devolve 200 com `store: unreachable` e o código sanitizado (`app.py:160-177`) — mesma intenção na porta HTTP, não no MCP. Falta: caminho degradado no MCP, mapeamento código→remediação, propagação de exceções não-ApexStoreError. Não comprovado: que `_sanitize` atual (reescrito em #140 com classificação por código) produza todos os códigos que a remediação precisaria mapear.

### Linhagem

L1_tasks.md → l1-connect.yaml:209 → spec 3a6b402 → eval com node IDs (611dc6e) → sem implementação → ready. Elo lateral: #140 (6cb31ea, b149569) criou códigos novos `clickhouse_access_denied`/`clickhouse_database_missing` que esta spec, de agosto, não conhece.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260817-status-degraded-path.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-status-degraded-path.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L209; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_mcp/ch.py#L1217-L1262; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_mcp/ch.py#L1285-L1307; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_api/app.py#L160-L177.; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_api/app.py#L160-L177; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83). Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: ausência do caminho MCP; presença do análogo HTTP; `_sanitize` com cinco códigos. FATO sobre evals: eval_2 roda a suíte com senha sentinela exportada — exportar não garante que alguma asserção procure o sentinela (precisa teste que leia o payload). INFERÊNCIA: a remediação teria de cobrir os códigos de #140. DECISÃO PENDENTE: adoção.

### Fluxo

Fluxo proposto: apex_status → store.* levanta ApexStoreError(código) → diagnose.status captura só ApexStoreError → [connected=False, degraded_reason=código, remediation=texto Apex] → FastMCP → cliente; exceção não-ApexStoreError → propaga como erro de tool. Observado apenas o análogo HTTP.

### Consequências e risco

Sem ação: usuários MCP continuam vendo oito tools 'saudáveis' que falham por chamada (descrição atual em SERVE-LEGS.md:58-60). Impacto: experiência de instalação; não é falha de dado. Confiança média sobre a dor (relato do doc), alta sobre a ausência.

### Alternativas e recomendação

Se adotado: mapear códigos sanitizados a remediações e verificar captura só de ApexStoreError, propagação de erros inesperados e ausência de credenciais no payload. /v1/health é precedente de resposta de processo saudável com store indisponível; MCP deve definir seu próprio resultado estruturado/isError, sem transportar mecanicamente o status HTTP 200. Alternativa: orientar uso do endpoint HTTP, com seu contrato e configuração próprios.

### Dependências e paralelismo

Depende de status-assembler e da decisão de família. Pode ser estudada em paralelo com a decisão (tabela código→remediação). Não depende de ClickHouse real para a prova offline.

### Plano e aceite propostos

Se adotada: (1) tabela código→remediação para os 5 códigos de `_sanitize`; (2) teste por código com FakeClient que levanta; (3) teste de propagação de RuntimeError; (4) controle de vazamento: payload serializado não contém senha sentinela nem host/usuário do driver (asserção explícita sobre o JSON, não só exportar variável). Senão: parked com referência ao `/v1/health`.

### Comunicação entre responsáveis

Explicar: 'O caminho degradado do status MCP não existe; o /v1/health da API já faz isso na porta HTTP. Se retomado, deve conhecer os códigos novos de #140 e provar ausência de credencial lendo o payload.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Capturar toda Exception esconderia defeitos inesperados como indisponibilidade do banco. Que caso o teste ainda não cobre? Caso a conferir: códigos de database e schema distintos com remediação e payload sem credenciais. Como eu explicaria isso para outro pod? MCP precisa entregar dado degradado; /v1/health é um precedente HTTP com contrato próprio.

### Próxima ação e encerramento

Ação: incluir na decisão da família, anexando a tabela de códigos atuais. Owner a confirmar: Serve. Entrada: decisão + `_sanitize` no SHA. Saída: spec revisada ou parked. Encerramento: status coerente e vínculo explícito ao análogo HTTP.

<a id="item-183"></a>

## T-20260817-status-store-down-e2e — T-20260817-status-store-down-e2e.md

Frente: Serve / L1 Connect — apex_status. Encaminhamento: decidir_com_familia_apex_status.

### Identidade e estado

`tasks/T-20260817-status-store-down-e2e.md` (blob f909d55d). 'Prove status answers through the tool boundary while the store is down', XS, standard, P2; owner `(none)`; depends_on register-apex-status e five-tools-assertion (nenhuma satisfeita). Estado `ready`, `accepted: false`. Pod provável: Pod 3/Serve (inferido pelos caminhos serve/; nenhum pod no arquivo).

### Intenção e benefício

Provar pela fronteira da tool (create_server, `_fail()`, serialização FastMCP) que apex_status devolve dado e não erro quando toda query falha. É o controle que garante que o caminho degradado sobrevive à camada MCP.

### Feito, faltante e não comprovado

Não implementado: o teste `test_apex_status_answers_while_store_is_down` não existe; não há tool. A dependência five-tools-assertion é obsoleta (ver ficha própria) e não deveria mais bloquear. Não comprovado: se `_fail()` atual (`server.py:75`) converteria ApexStoreError em erro de tool — por leitura, sim para as tools existentes, o que reforça a necessidade deste controle se a tool for criada.

### Linhagem

L1_tasks.md → l1-connect.yaml:347 → spec 3a6b402 → eval trocado para node ID em 611dc6e (o anterior passava sem trabalho) → sem recibo de execução localizado neste recorte → ready. Elos ausentes: tool apex_status, assembler e caminho degradado; nenhuma issue ou PR posterior cita esta unidade.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260817-status-store-down-e2e.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-status-store-down-e2e.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L347; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_mcp/server.py#L75-L85; fontes/batch-revalidated-specs28-sources/git/serve/tests/test_server_tools.py#L20-L67; fontes/batch-revalidated-specs28-sources/git/serve/tests/conftest.py; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83). Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: ausência do teste e da tool. FATO sobre evals: eval_2 roda a suíte inteira com senha sentinela — sem asserção que procure o sentinela no payload, não prova B-3. INFERÊNCIA: o valor está em B-1/B-2 (passar pela fronteira). DECISÃO PENDENTE: adoção da família.

### Fluxo

Fluxo proposto: FakeClient que levanta em toda query → create_server → tools/call apex_status → diagnose.status degrada → FastMCP serializa → [ServerStatus connected=false, sem isError] → asserção. Nada observado.

### Consequências e risco

Sem ação: nenhum risco atual (tool inexistente). Se a tool for criada sem este controle, `_fail()` pode transformar a resposta degradada em erro e anular o objetivo do L1 — risco plausível, não observado.

### Alternativas e recomendação

Recomendado: se adotada, fundir com register-apex-status (o teste de fronteira é parte da entrega mínima). Alternativa: manter separado para legibilidade no git log, como o autor preferia; custo é mais uma unidade na fila. Remover a dependência de five-tools-assertion.

### Dependências e paralelismo

Depende de register-apex-status e da decisão da família; a dependência de five-tools-assertion é obsoleta. Não precisa de ClickHouse. O desenho do teste pode ser feito em paralelo com o da tool; a implementação vem junto com ela.

### Plano e aceite propostos

Se adotada: (1) FakeClient que levanta ApexStoreError em toda query (estender conftest sem quebrar fixtures); (2) invocar via `server.call_tool` e validar contra o schema de saída; (3) asserção explícita de que `CLICKHOUSE_PASSWORD` sentinela não aparece no JSON serializado; (4) controle negativo: fazer o assembler levantar → o teste deve falhar. Senão: parked.

### Comunicação entre responsáveis

Explicar: a tool apex_status e o teste de fronteira nomeado não estão nos arquivos Serve lidos. A intenção desse teste é validar o dado que o cliente receberia após serialização; conferir sentinela no payload é diferente de apenas exportar uma variável.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Testar apenas diagnose.status deixaria serialização e tratamento de erro de tool fora da prova. Que caso o teste ainda não cobre? Caso a conferir: falha de schema convertendo resposta degradada em erro no cliente. Como eu explicaria isso para outro pod? A garantia é o cliente receber ServerStatus conectado falso, atravessando create_server e FastMCP.

### Próxima ação e encerramento

Ação: incluir na decisão da família e remover a dependência obsoleta. Owner a confirmar: Serve. Entrada: decisão. Saída: spec fundida/revisada ou parked. Encerramento: status coerente.

<a id="item-184"></a>

## T-20260817-stdio-gate-five-tools — T-20260817-stdio-gate-five-tools.md

Frente: Serve / L1 Connect — apex_status. Encaminhamento: encerrar_meta_numerica_e_tratar_deriva_atual_do_gate.

### Identidade e estado

`tasks/T-20260817-stdio-gate-five-tools.md` (blob 577e2aae). 'Assert five tools in the real stdio MCP gate', XS, standard, P2; owner `(none)`; depends_on register-apex-status. Estado `ready`, `accepted: false`. Pod provável: Pod 3/Serve (inferido pelos caminhos serve/; nenhum pod no arquivo).

### Intenção e benefício

Confirmar a nova tool por um cliente MCP real sobre stdio (framing, handshake, serialização), onde um byte em stdout ou schema rejeitado apareceria. O controle é pinar a superfície exata que o cliente vê.

### Feito, faltante e não comprovado

A meta 'cinco' foi ultrapassada. Achado atual (leitura estática): `serve/tools/mcp_stdio_gate.py` no SHA tem `EXPECTED_TOOLS` com **7** entradas (falta `recall_similar_runs`) e docstring 'exactly the six contracted tools', enquanto o servidor registra **8** tools na ordem analyze_run, explain_stage, compare_runs, list_runs, search_kb, recall_similar_runs, verify_fix, suggest_fix. A comparação é `tool_metadata == EXPECTED_TOOLS` (linha 81), logo o gate, como escrito, divergiria do servidor — inferência; não executado. O VALIDATION.md (seção L5) afirma que EXPECTED_TOOLS 'was updated to the eight-tool surface', o que o arquivo não confirma.

### Linhagem

L1_tasks.md → l1-connect.yaml:963 → spec 3a6b402 → sem recibo de execução localizado neste recorte. Histórico do gate: d377e5a (#83), ca514b8 (#88), 3758d00 (#87, 'six, including verify_fix'); nenhum commit de L6 (#86) tocou o gate, embora L6 tenha adicionado recall_similar_runs e re-pinado só o teste unitário (60e6ef2). Elo ausente: reconciliação do gate após as merges paralelas de 2026-09-14.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260817-stdio-gate-five-tools.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-stdio-gate-five-tools.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L963; fontes/batch-revalidated-specs28-sources/git/serve/tools/mcp_stdio_gate.py#L1-L39; fontes/batch-revalidated-specs28-sources/git/serve/tools/mcp_stdio_gate.py#L68-L81; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_mcp/server.py#L169-L600; fontes/batch-revalidated-specs28-sources/git/serve/VALIDATION.md#L300-L305; fontes/batch-revalidated-specs28-sources/git/serve/VALIDATION.md#L336-L344; fontes/batch-revalidated-specs28-sources/git/.github/workflows/ci.yml#L63-L96; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83); fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #101 e #86); fontes/batch-revalidated-specs28-sources/git/.github/workflows/ci.yml. Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: EXPECTED_TOOLS tem sete entradas, sem recall_similar_runs; create_server tem oito registros @mcp.tool e teste de allowlist contém oito; gate faz igualdade da lista; VALIDATION L5 afirma atualização para oito. INFERÊNCIA: se o SDK listar os oito registros como o servidor declara, a comparação falha por cardinalidade independentemente da ordem. Nenhuma falha runtime foi executada ou observada aqui. ci.yml lido não invoca diretamente este gate; não foi feita busca universal de todas as automações externas.

### Fluxo

Fluxo estático: stdio_client lança uv run apex-mcp → initialize → list_tools → coleta name/readOnlyHint → igualdade contra sete entradas. O servidor declara oito registros @mcp.tool; se o SDK os listar, haverá divergência antes das invocações seguintes, por inferência. Este gate não coleta openWorldHint nessa comparação. Proposta histórica pretendia cinco incluindo apex_status; nenhuma sessão real foi executada aqui.

### Consequências e risco

Sem ação: a divergência do esperado compromete a prova manual quando o SDK listar a superfície registrada. Confiança alta na incompatibilidade estática; não se afirma resultado real de handshake/processo. A ordem é um segundo aspecto da igualdade, mas não elimina sete versus oito. Nenhum efeito em operação foi observado nesta auditoria.

### Alternativas e recomendação

Recomendado: propor encerramento da meta cinco e reconciliação pequena do gate com a superfície atual. Manter um contrato esperado explícito, independente da listagem sob teste; pode estar num módulo de contrato compartilhado, sem importar um teste em código de produto nem gerar o esperado do servidor real. Alternativa: lista própria de oito no gate e revisão de paridade; custo de duplicação. Manter controles de anotações e esclarecer divergência de VALIDATION por nota datada.

### Dependências e paralelismo

A disposição documental da meta cinco pode ser proposta sem runtime; o mantenedor confirma encerramento/substituição. A edição do gate não depende de apex_status nem de ClickHouse. A futura execução depende de ambiente autorizado e identificado.

### Plano e aceite propostos

Para reconciliação proposta: (1) manter contrato esperado de oito nomes/anotações explícito e independente da listagem real; (2) corrigir docstring e registrar nota datada sobre VALIDATION; (3) controlar tool extra/ausente e anotação divergente; (4) se a garantia incluir openWorldHint, conferir esse campo explicitamente; (5) execução futura só com SHA/ambiente e recibo próprios. Documentar a substituição da meta cinco sem declarar sucesso runtime a partir da edição.

### Comunicação entre responsáveis

Explicar: 'A meta de cinco tools é histórica. O gate stdio atual está com 7 nomes para 8 tools e a documentação diz o contrário; isso precisa de correção pequena e própria.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Derivar o esperado da própria listagem real faria uma tool extra aprovar a si mesma. Que caso o teste ainda não cobre? Caso a conferir: anotações erradas e oito nomes listados contra sete esperados, independentemente da ordem. Como eu explicaria isso para outro pod? O gate manual deve comparar o cliente a um contrato esperado explícito e registrar execução só quando realizada.

### Próxima ação e encerramento

Ação proposta: registrar a meta cinco como superada e submeter ao owner do Serve sua disposição (parked/substituída), vinculada a uma correção pequena do gate. Entrada: gate, servidor e VALIDATION no SHA. Saída: decisão documental e follow-up rastreável; não encerrar unilateralmente nem declarar o gate aprovado antes da prova escolhida.

<a id="item-185"></a>

## T-20260817-surface-defaulted-vars — T-20260817-surface-defaulted-vars.md

Frente: Serve / L1 Connect — apex_status. Encaminhamento: decidir_com_familia_apex_status_modelo_ja_preparado.

### Identidade e estado

`tasks/T-20260817-surface-defaulted-vars.md` (blob 7e3cd198). 'Surface defaulted environment variables in ServerStatus', M, standard, P2; owner `(none)`; depends_on serverstatus-model (done), resolve-settings-extract, status-assembler, status-degraded-path, startup-stderr-banner (não satisfeitas). Estado `ready`, `accepted: false`. Pod provável: Pod 3/Serve (inferido pelos caminhos serve/; nenhum pod no arquivo). A spec registra ter sido reclassificada de S para M por tocar três caminhos.

### Intenção e benefício

A intenção da spec é relatar por nome as variáveis CLICKHOUSE_* ausentes do ambiente e conectar defaults com o caso de store vazio. A afirmação de que essa é a causa mais comum é justificativa histórica da spec, não prevalência medida nesta auditoria. O benefício pretendido é orientar configuração sem expor valores.

### Feito, faltante e não comprovado

O modelo já possui using_defaults com descrição NAMES only e teste que recebe uma fixture de nomes; não há cálculo de defaulted nem ligação a apex_status no código lido. O cliente suporta seis CLICKHOUSE_*; serve/.mcp.json configura cinco e deixa SECURE no default. Essa omissão é compatível com configuração opcional; não prova inconsistência funcional. A prosa five env vars de SERVE-LEGS é histórica e deve ser reconciliada com o contrato de seis da intenção. Nenhum comportamento do cliente foi executado.

### Linhagem

L1_tasks.md → l1-connect.yaml:543 → spec 3a6b402 → eval com node IDs (611dc6e) → sem implementação. Elo lateral: campo no modelo entregue por serverstatus-model (667926055e). Elos ausentes: resolve_settings, assembler.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260817-surface-defaulted-vars.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-surface-defaulted-vars.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L543; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_mcp/models.py#L572-L612; fontes/batch-revalidated-specs28-sources/git/serve/tests/test_status.py#L65-L75; fontes/batch-revalidated-specs28-sources/git/serve/README.md#L209-L220; fontes/batch-revalidated-specs28-sources/git/serve/.mcp.json; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_mcp/ch.py#L1285-L1307.; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_mcp/ch.py#L1285-L1307; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83). Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: using_defaults é list[str] com descrição textual e teste de fixture conhecida; o tipo aceita strings arbitrárias e não garante que sejam nomes. Cálculo de variáveis não definidas está ausente nos módulos lidos. A diferença cinco configuradas/seis suportadas não demonstra erro funcional. INFERÊNCIA: há intenção de conferir nomes antes da serialização. DECISÃO PENDENTE: adotar o status e escolher garantia por produtor ou validação de modelo; teste de payload precisa discriminar valores, não apenas exportar senha.

### Fluxo

Fluxo proposto: ambiente do processo → resolve_settings() → [defaulted: nomes não definidos] → diagnose.status → using_defaults + remediação combinada com store vazio → apex_status. Observado: nenhum; get_client lê os.getenv inline.

### Consequências e risco

Sem ação: usuário com endpoint padrão errado continua sem pista no MCP. Impacto em suporte/instalação. Nota de segurança: se implementado, listar o NOME `CLICKHOUSE_PASSWORD` é seguro; o valor nunca. Confiança alta na ausência.

### Alternativas e recomendação

Recomendado: se adotada, implementar junto com resolve_settings (mesma origem da lista) e fixar a lista canônica de variáveis num único lugar; validar que cada item pertence a essa lista (B-4 forte). Alternativa: expor só no banner de stderr (startup-stderr-banner), sem mexer no status — mais simples, porém invisível ao modelo. Reversível.

### Dependências e paralelismo

Depende de resolve-settings-extract e status-assembler (e da decisão). O banner e o status podem ser projetados em paralelo; a dependência declarada do banner é de ordem de escrita em server.py, não semântica.

### Plano e aceite propostos

Se adotada: fixar lista de seis variáveis suportadas e a regra para ausente versus string vazia; verificar defaults e store vazio com remediação não categórica; definir fronteira que só permite nomes e conferir ausência do valor sentinela no payload. A config de exemplo pode omitir SECURE e usar seu default; não precisa repetir todas as variáveis para ser válida. Documentar essa distinção e registrar disposição se a funcionalidade não for adotada.

### Comunicação entre responsáveis

Explicar: o campo using_defaults existe, mas não há produtor no Serve lido. São seis variáveis suportadas; a config de exemplo pode deixar SECURE opcional no default. list[str] e descrição NAMES only não impedem valores; decidir a fronteira que garante nomes antes de expor o status.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Duplicar a regra de variáveis ou confiar apenas em list[str] pode deixar valores escaparem como nomes. Que caso o teste ainda não cobre? Caso a conferir: string vazia versus variável ausente e valor arbitrário em using_defaults. Como eu explicaria isso para outro pod? Há seis variáveis suportadas, com SECURE opcional no exemplo, e a garantia de nomes deve ter fronteira explícita.

### Próxima ação e encerramento

Ação: incluir na decisão da família e registrar a divergência 5/6 variáveis. Owner a confirmar: Serve. Entrada: decisão + lista canônica. Saída: spec revisada ou parked. Encerramento: status coerente e lista única documentada.

<a id="item-186"></a>

## T-20260817-table-columns-probe — T-20260817-table-columns-probe.md

Frente: Serve / L1 Connect — apex_status. Encaminhamento: decidir_com_familia_apex_status_mecanismo_parcial_existente.

### Identidade e estado

`tasks/T-20260817-table-columns-probe.md` (blob 97b7b765). Task-Spec 'Generalize findings_columns into an allowlisted table_columns probe', S, standard, P2; owner `(none)`; depends_on `[T-20260817-store-health-query]`. Estado: `ready`, `accepted: false`, sem assinatura (o autor recusou assinar as 21 unidades na fila, PR #79). Pod provável: Pod 3/Serve (inferido pelos caminhos serve/; nenhum pod no arquivo).

### Intenção e benefício

Permitir que a tool de status reporte conformidade de contrato para spark_events, findings e plan_transitions; o probe atual cobre uma tabela de três. Beneficia diagnóstico de implantações parciais (DDL aditiva aplicada por cluster).

### Feito, faltante e não comprovado

No código lido não há table_columns nem allowlist do recorte de status. findings_columns retorna conjunto de findings e preserva cache de respostas; table_exists usa COLUMNS_SQL com binding e cache de presença/ausência, levantando erros de probe sem cachear falhas. A necessidade declarada desta generalização vem do status de conformidade; outros consumidores futuros não foram demonstrados nem excluídos. A allowlist não corrige uma injeção observada: o nome atual já é parâmetro ligado.

### Linhagem

L1_tasks.md → l1-connect.yaml:111 → spec 3a6b402 → eval trocado para node IDs em 611dc6e (o eval anterior passava sem trabalho) → nenhum commit de implementação → status ready. Elo lateral: table_exists entrou por L5 (verificações, v0.3) e foi endurecido em #140 — não cita esta spec. Fechamento ausente.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260817-table-columns-probe.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-table-columns-probe.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L111; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_mcp/ch.py#L791-L820; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_mcp/ch.py#L854-L880; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_mcp/ch.py#L134-L137; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83). Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: ausência de `table_columns`; presença de `table_exists` e `findings_columns` com binding. FATO sobre a spec: eval_2 (`git diff HEAD -- tests/test_ch.py` sem linhas removidas) só discrimina com alterações não commitadas — depois do commit passa trivialmente, logo não prova B-2 de forma durável. INFERÊNCIA: o valor de B-1/B-3 depende da família apex_status. DECISÃO PENDENTE: adotar status de conformidade por tabela. Sem execução local/CI.

### Fluxo

Fluxo proposto: apex_status → ReadStore.table_columns(nome) → [guarda de allowlist: recusa sem query] → COLUMNS_SQL ligado → system.columns → [set de colunas] → diagnose.status → contract_tables (faltantes). Hoje observado: table_exists(nome) → COLUMNS_SQL → [bool] → verify_fix/recall (degradação 'not_assessed').

### Consequências e risco

Sem ação: a conformidade por coluna das três tabelas continua não reportada; risco de coordenação (spec ready sugere trabalho disponível). Não há risco de injeção atual: `table_exists` liga o nome como parâmetro; a allowlist seria defesa em profundidade, não correção de falha observada. Confiança alta na ausência; nenhuma prova de incidente.

### Alternativas e recomendação

Se status por coluna for adotado: introduzir probe allowlisted para o recorte de status, reutilizando COLUMNS_SQL/binding e mantendo findings_columns como chamador compatível; preservar table_exists para seus consumidores de verificações e memória, cujas tabelas excedem a allowlist das três deste item. O mecanismo compartilhado pode ser interno. Substituir git diff HEAD por controle comportamental de conjunto/cache e zero queries para nome recusado. Alternativa: manter só probes de presença existentes e arquivar a intenção de conformidade por coluna.

### Dependências e paralelismo

Depende da decisão sobre apex_status (não de execução). Estudo do contrato de conformidade pode correr em paralelo com qualquer revisão de PR; implementação depende da decisão e de não conflitar com mudanças em ch.py (17 commits desde a criação da spec).

### Plano e aceite propostos

Se adotada: (1) definir table_columns de status para spark_events/findings/plan_transitions; (2) nome fora da lista deve falhar antes de consultar; (3) preservar findings_columns e cache somente de respostas, sem cachear falha; (4) preservar consumidores e contrato booleano de table_exists para fix_verifications/plan_memory/run_outcomes; (5) controle discriminante removendo a guarda em cópia de teste, em futura etapa autorizada. Não estreitar a API existente apenas para satisfazer a spec antiga. Documento mínimo: contratos das funções.

### Comunicação entre responsáveis

Na issue: 'O probe genérico com allowlist não foi feito; table_exists (presença) e findings_columns (colunas de findings) existem. Esta spec só tem valor se apex_status for retomado; o eval_2 original não protege nada depois do commit.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Restringir table_exists às três tabelas de status quebraria consumidores de memória e verificações. Que caso o teste ainda não cobre? Caso a conferir: probe falho não cacheado e nome recusado antes de qualquer query. Como eu explicaria isso para outro pod? Presença de tabela, conjunto de colunas e conformidade são contratos diferentes.

### Próxima ação e encerramento

Ação: incluir na decisão única da família apex_status. Owner a confirmar: Serve. Entrada: decisão do mantenedor. Saída: spec reescrita sobre table_exists ou parked com motivo. Encerramento: status refletindo a decisão e referência ao mecanismo existente.

<a id="item-187"></a>

## T-20260817-testpypi-rehearsal — T-20260817-testpypi-rehearsal.md

Frente: Serve / L1 Connect — distribuição PyPI. Encaminhamento: decidir_distribuicao_v1_etapa_externa_com_credencial.

### Identidade e estado

`tasks/T-20260817-testpypi-rehearsal.md` (blob feaba671). 'Rehearse the publish on TestPyPI', XS, standard, P2; owner `(none)`; depends_on wheel-content-check e four-to-five-doc-ripple. Estado `ready`, `accepted: false`. Pod provável: Pod 3/Serve (inferido pelos caminhos; nenhum pod no arquivo). A spec declara 'human-gated' (exige token TestPyPI).

### Intenção e benefício

Ensaiar a publicação no TestPyPI antes do PyPI real, porque uma release é imutável; instalar limpo de outro diretório e registrar o resultado. Benefício: evitar release quebrada permanente.

### Feito, faltante e não comprovado

A captura preservada em 2026-10-18T04:04:19Z retorna 404 no endpoint JSON de apex-mcp do TestPyPI. Ela informa a resposta daquele nome/instante; não demonstra que nunca houve ensaio, publicação removida ou uso de outro nome. No VALIDATION lido não foi encontrado recibo TestPyPI. Falta localizar um recibo de ensaio aplicável ou planejar etapa autorizada após decisão de distribuição; a dependência na meta quatro→cinco precisa de reconciliação.

### Linhagem

L1_tasks.md → l1-connect.yaml:684 → spec 3a6b402 → sem execução. PR #79 'Not done': 'testpypi-rehearsal, pypi-publish need registry credentials'. Elo ausente: decisão e credencial.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260817-testpypi-rehearsal.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-testpypi-rehearsal.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L684; fontes/batch-revalidated-specs28-sources/git/serve/VALIDATION.md#L132-L136; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83); fontes/batch-claude-specs-sources/claude/fontes/publico/pypi_org_pypi_apex-mcp_json.txt; fontes/batch-claude-specs-sources/claude/fontes/publico/test_pypi_org_pypi_apex-mcp_json.txt. Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: 404 no TestPyPI na data; ausência de registro em VALIDATION. FATO sobre evals: eval_1 envia EOF imediato e só testa stdout vazio — uma falha de instalação/arranque sem stdout também passaria; não prova bloqueio em stdin nem resolução das dependências do índice extra (B-3); eval_2 é grep 'testpypi' no VALIDATION. DECISÃO PENDENTE: distribuição v1. Nenhuma ação externa executada.

### Fluxo

Fluxo proposto: artefatos → twine upload (token humano) → TestPyPI → uvx --index-url test.pypi --extra-index-url pypi (fora do checkout) → apex-mcp bloqueia em stdin → registro em VALIDATION. Observado: nenhum.

### Consequências e risco

Sem ação: nenhum risco enquanto não houver publicação. Executar o eval como está pode registrar falso positivo de ensaio. Confiança alta nos fatos; o 404 é só desta consulta.

### Alternativas e recomendação

Recomendado: manter como etapa externa condicionada à decisão de distribuição; antes, fortalecer o eval (exigir exit code do uvx, timeout com processo vivo e verificação de versão instalada). Alternativa: distribuir por checkout e encerrar a família de publicação como não adotada.

### Dependências e paralelismo

Depende de: decisão de canal, pypi-metadata, wheel-content-check revisada e credencial humana. Remover a dependência de four-to-five-doc-ripple. Estudo do procedimento pode correr em paralelo; o upload é ação externa separada.

### Plano e aceite propostos

Se adotada: (1) versão devN; (2) upload por executor explicitamente autorizado com credencial própria autorizada; (3) instalação em diretório temporário fora do repo com `--index-url`/`--extra-index-url`; (4) controle: processo deve continuar vivo N segundos com stdin aberto e stdout vazio, e `uvx` deve retornar sucesso na resolução; (5) registrar versão, data, hash do wheel e saída em VALIDATION. Senão: parked.

### Comunicação entre responsáveis

Explicar: a consulta preservada de 18/10 retornou 404 no TestPyPI e nenhum recibo de ensaio foi localizado no recorte. O eval aceita stdout vazio mesmo após instalação falha; não prova origem das dependências. Preparar procedimento é independente; upload exige autorização específica e credencial adequada.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? O ensaio sem versão e artefato identificados pode validar um objeto diferente da release pretendida. Que caso o teste ainda não cobre? Caso a conferir: origem real de dependências e instalação quebrada que produz stdout vazio. Como eu explicaria isso para outro pod? O 404 capturado descreve um nome naquele instante; um ensaio válido precisa de recibo próprio.

### Próxima ação e encerramento

Ação: condicionar à decisão de distribuição e reescrever o eval. Owner a confirmar: release owner. Entrada: decisão + artefatos validados + token. Saída: recibo de ensaio com versão/hash, ou parked. Encerramento: recibo registrado ou decisão de não publicar.

<a id="item-188"></a>

## T-20260817-wheel-content-check — T-20260817-wheel-content-check.md

Frente: Serve / L1 Connect — distribuição PyPI. Encaminhamento: decidir_distribuicao_v1_invariante_desatualizada.

### Identidade e estado

`tasks/T-20260817-wheel-content-check.md` (blob 526b167f). 'Assert the wheel ships the package and nothing else', S, standard, P2; owner `(none)`; depends_on pypi-metadata. Estado `ready`, `accepted: false`. Pod provável: Pod 3/Serve (inferido pelos caminhos; nenhum pod no arquivo). `creates_paths: serve/tests/test_packaging.py` ausente no SHA.

### Intenção e benefício

Provar que o wheel contém só o pacote e sua dist-info: `serve/tools` tem gates live que semeiam linhas no ClickHouse e não podem ir para o ambiente do usuário. Benefício: segurança e higiene do artefato.

### Feito, faltante e não comprovado

Não há serve/tests/test_packaging.py no índice Git. Configuração atual do alvo wheel limita packages a src/apex_mcp e src/apex_api; é uma proteção declarada de seleção, mas nenhum wheel foi construído/inspecionado nesta revisão. B-1/eval_2 antigos permitem apenas apex_mcp e dist-info, portanto conflitam com o alvo apex_api se o artefato seguir essa configuração. O prefixo permitido precisa refletir o escopo decidido; exclusão efetiva de tests/tools/scripts permanece não verificada no artefato.

### Linhagem

L1_tasks.md → l1-connect.yaml:639 → spec 3a6b402 → sem implementação. Mudança posterior que altera a premissa: #129 incluiu apex_api no mesmo wheel. Fechamento ausente.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260817-wheel-content-check.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-wheel-content-check.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L639; fontes/batch-revalidated-specs28-sources/git/serve/pyproject.toml#L33-L34; fontes/batch-revalidated-specs28-sources/git/serve/tools/read_only_gate.py#L1-L12; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83). Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: test_packaging ausente; packages com dois pacotes. INFERÊNCIA: eval_2 rejeitaria `apex_api/`; B-1 precisa ser reescrito para 'apex_mcp/ ou apex_api/ ou dist-info'. FATO sobre evals: eval_2 apaga dist e constrói (efeito no worktree). Nenhum build executado nesta revisão. DECISÃO PENDENTE: o que o wheel deve conter.

### Fluxo

Fluxo proposto: uv build → wheel → zipfile.namelist → [entradas] → asserções de prefixo e de exclusão (tests/tools/scripts) ; sdist → README.md e pyproject.toml presentes. Observado: só a configuração hatch.

### Consequências e risco

Sem reconciliação: um executor pode interpretar a inclusão deliberada de apex_api como falso negativo de aceite. Há configuração de seleção de pacotes no hatch, portanto não se afirma ausência de toda proteção. Falta prova do conteúdo de um artefato identificado; risco de distribuição não é incidente observado.

### Alternativas e recomendação

Recomendado: reescrever B-1 para o conjunto de pacotes decidido (MCP+API ou só MCP) e manter B-2/B-3; a asserção deve rodar no artefato construído. Alternativa: separar a API em pacote próprio e manter a spec quase intacta. Tradeoff: um pacote mais simples de explicar vs dois artefatos a manter.

### Dependências e paralelismo

Depende de pypi-metadata e da decisão de escopo do pacote. Independe de ClickHouse e de apex_status. Pode ser escrita em paralelo à decisão de canal (o teste vale mesmo sem publicar).

### Plano e aceite propostos

Se adotada: (1) teste em tmpdir: build, listar wheel; (2) prefixos permitidos = pacotes decididos + dist-info; (3) exclusão explícita de tests/, tools/, scripts/; (4) controle negativo: incluir `serve/tools` no alvo faz falhar; (5) sdist contém README.md e pyproject.toml. Doc: nota de release. Senão: parked.

### Comunicação entre responsáveis

Explicar: test_packaging.py está ausente do índice Git lido e o alvo atual inclui apex_api além de apex_mcp. A invariante antiga precisa ser reconciliada com o escopo da release. Configuração do hatch não equivale a inspeção do wheel; nenhum build ou teste foi executado aqui.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Executar o prefixo antigo só apex_mcp pode rejeitar a inclusão deliberada de apex_api. Que caso o teste ainda não cobre? Caso a conferir: arquivos necessários de dados e exclusão efetiva de gates no wheel construído. Como eu explicaria isso para outro pod? A configuração de pacotes é evidência estática; a composição de um wheel identificado exige inspeção do artefato.

### Próxima ação e encerramento

Ação: reescrever a invariante após decidir escopo do pacote. Owner a confirmar: release + Serve. Entrada: decisão de escopo. Saída: spec revisada ou parked. Encerramento: teste no artefato coerente com os pacotes decididos.

<a id="item-189"></a>

## T-20260819-retry-pressure-watcher — T-20260819-retry-pressure-watcher.md

Frente: Engine / telemetria retry-safe (#89). Encaminhamento: reconciliar_status_implementado_em_89_sem_reexecutar_evals.

### Identidade e estado

`tasks/T-20260819-retry-pressure-watcher.md` (blob 4f0ccb34). 'Add the retry-pressure watcher and register it', M, standard, P2; owner `(none)`; depends_on retry-safe-stage-fields (implementada). Estado `ready`, `accepted: false`, sem assinatura. Pod provável: Pod 2/Engine (PR #89 com rótulo pod-2-engine segundo a camada de leitura do corpo; nenhum pod no arquivo).

### Intenção e benefício

Acrescentar um watcher Tier-1 que relate quanto do orçamento de falhas do scheduler foi consumido por falhas contadas, como fato e sem inferir causa (código vs infraestrutura), e registrá-lo para rodar com os demais.

### Feito, faltante e não comprovado

Implementado: `watchers/retry_pressure.py` com `evaluate()` que devolve None se `task_counted_failure_attempt_count <= 0` e finding RETRY_PRESSURE em INFO com contagens contadas vs observadas; registrado em `STAGE_WATCHERS` (`watchers/__init__.py:27`); testes `test_retry_pressure_flags_counted_failures_at_info`, `..._ignores_failures_that_never_counted`, `..._is_silent_and_registered_on_a_clean_job` (`test_watchers.py:337-370`). Mudança posterior: o registro tem hoje sete watchers (tail_outlier entrou por #127) e o texto diz 'seven', não 'six' como a spec previa — eval_4 (proíbe 'five') continua satisfeito. Falta: transição de status.

### Linhagem

CONTRACT.md v0.5 → spec 04238ed (sem TaskPlan) → implementação 6fc0efd ('register it as the sixth') → PR #89 (2026-09-14) → tail_outlier adicionado por #127 (1cf109a) muda contagem para sete → spec permanece ready/false. Elos ausentes: aceite formal, TaskPlan.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260819-retry-pressure-watcher.md; fontes/batch-revalidated-specs28-sources/history/T-20260819-retry-pressure-watcher.txt; fontes/batch-revalidated-specs28-sources/git/engine/src/apex_engine/watchers/retry_pressure.py; fontes/batch-revalidated-specs28-sources/git/engine/src/apex_engine/watchers/__init__.py#L1-L50; fontes/batch-revalidated-specs28-sources/git/engine/tests/test_watchers.py#L337-L370; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #89 e #99); fontes/batch-revalidated-specs28-sources/public-captured-comments.json; issue #90, comentário 5718036779). Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: watcher, registro e testes presentes. RELATO HISTÓRICO: um finding live em ClickHouse descartável (autor, #89). INFERÊNCIA: evals 2 e 4 satisfeitos por leitura; eval_1 depende de `-k retry_pressure`, que seleciona os três testes acima. Limite do watcher (documentado no próprio módulo): não classifica causa. Nenhuma execução nesta revisão. DECISÃO PENDENTE: registro de aceite.

### Fluxo

Fluxo observado estaticamente: StageAggregate(contadores) → retry_pressure.evaluate → None ou Finding RETRY_PRESSURE/INFO com confidence_score 0.95 → run_all_offline/run_all devolve lista de findings. O SQL próprio filtra counted > 0. Persistir em findings é etapa externa ao watcher e depende do modo de execução; não foi executada aqui. A ida e volta histórica no ClickHouse é relato do autor no corpo de #89.

### Consequências e risco

Sem ação: nenhuma regressão; ruído de fila. Limite de produto (não defeito): um finding INFO sem causa pode ser lido como alerta forte por consumidores — mitigado pelo texto de impacto. Confiança alta.

### Alternativas e recomendação

Recomendado: reconciliar o estado documental com implementação 6fc0efd/#89 e distinguir aceite formal de simples constatação de código presente. Alternativa: done com accepted=false e nota explícita, se o processo permitir. Não executar os evals antigos nem alterar seven para six só para conferir carimbo; eventual prova nova deve usar contrato e SHA escolhidos.

### Dependências e paralelismo

Depende de retry-safe-stage-fields (entregue). Independente de tail_outlier, de #99 e de qualquer ambiente ClickHouse. A reconciliação pode correr em paralelo com as outras três specs de #89; nenhum estudo precisa esperar por ela.

### Plano e aceite propostos

Passos documentais: identificar 6fc0efd, merge #89 e escopo dos testes existentes; registrar o relato histórico com sua data; confirmar responsável e forma permitida de transição/aceite, sem atribuir aprovação independente. O teste que retorna None para falhas não contadas já discrimina B-2 por construção. Se alguma prova nova for necessária, ela será etapa autorizada e identificada por SHA, não requisito inventado para uma nota de reconciliação.

### Comunicação entre responsáveis

Explicar: watcher retry_pressure, registro e testes focais estão presentes no SHA lido; #89 relata resultados locais. Sete refere-se aos watchers de stage após #127, além do AQE. Reconciliar a spec ready com o que foi integrado e com o processo de aceite, sem atribuir uma execução nova.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Disparar com qualquer falha observada confundiria tentativa que não contou no orçamento com retry pressure. Que caso o teste ainda não cobre? Caso a conferir: combinação de tentativa especulativa e falha contada, sem inferir causa. Como eu explicaria isso para outro pod? O watcher produz INFO sobre contagens e deixa investigação de causa para outras fontes.

### Próxima ação e encerramento

Ação: reconciliação documental. Owner a confirmar: Engine. Entrada: 6fc0efd e testes. Saída: spec em done com nota. Encerramento: arquivo movido com rastreio ao SHA.

<a id="item-190"></a>

## T-20260819-retry-safe-stage-fields — T-20260819-retry-safe-stage-fields.md

Frente: Engine / telemetria retry-safe (#89). Encaminhamento: reconciliar_status_implementado_em_89_sem_reexecutar_evals.

### Identidade e estado

`tasks/T-20260819-retry-safe-stage-fields.md` (blob 3c330b9e). 'Land the retry-safe attempt counters on StageAggregate', S, standard, P2; owner `(none)`; sem dependências; source_note 'CONTRACT.md v0.5 changelog'. Estado no SHA: `ready`, `accepted: false`, sem assinatura. Pod provável: Pod 2/Engine (PR #89 com rótulo pod-2-engine segundo a camada de leitura do corpo; nenhum pod no arquivo). Autor da spec e da implementação: Augusto Cezar.

### Intenção e benefício

Tornar alcançáveis para os consumidores Python do Engine três colunas que o JAR já emite e a infra já guarda (task_attempt_count, task_failed_attempt_count, task_counted_failure_attempt_count), com default 0 para linhas históricas, e reservar o FindingType aditivo RETRY_PRESSURE.

### Feito, faltante e não comprovado

Implementado no SHA: os três campos existem em `StageAggregate` com `default=0, ge=0` (`schema.py:185-187`) e em `StageEvent` (133-135); `STAGE_AGGREGATES_SQL` seleciona os três via argMax (`clickhouse.py:96-98`); `RETRY_PRESSURE` no enum (`schema.py:54`). Commit de implementação a644a63 (2026-08-20), integrado por #89 em 2026-09-14. Falta: só a transição documental de status/aceite. Não comprovado nesta revisão: que a suíte do Engine passe hoje e que B-3 (nenhum membro do enum reordenado) tenha controle além do eval que checa dois membros.

### Linhagem

CONTRACT v0.5 como origem declarada → spec criada em 04238ed em 19/08/2026 às 20:55:16-03 (23:55:16Z) → a644a63 (autoria 19/08 local; commit registrado em 20/08) e endurecimentos → merge #89 c67ba0e em 14/09/2026 às16:17:47Z → spec continua ready/false no SHA lido. Nenhum TaskPlan que inclua esta unidade foi demonstrado nesta revisão; falta reconciliação de status e aceite, não reimplementação.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260819-retry-safe-stage-fields.md; fontes/batch-revalidated-specs28-sources/history/T-20260819-retry-safe-stage-fields.txt; fontes/batch-revalidated-specs28-sources/git/engine/src/apex_engine/schema.py#L170-L246; fontes/batch-revalidated-specs28-sources/git/engine/src/apex_engine/schema.py#L40-L60; fontes/batch-revalidated-specs28-sources/git/engine/src/apex_engine/clickhouse.py#L25-L145; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #89 e #99); fontes/batch-revalidated-specs28-sources/public-captured-comments.json; issue #90, comentário 5718036779). Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: três campos com default=0/ge=0 em StageAggregate e StageEvent, seleção argMax no SQL e RETRY_PRESSURE no enum. Os evals lidos conferem texto SQL, defaults do modelo e dois membros do enum; isso não prova todos os membros inalterados nem a leitura real de uma linha histórica. RELATO HISTÓRICO: #89 declara suites e round-trips locais em ClickHouse, com contagens de rodadas distintas. DECISÃO PENDENTE: forma de reconciliação/aceite; nenhuma suíte executada nesta revisão.

### Fluxo

Fluxo observado estaticamente no recorte Engine: STAGE_AGGREGATES_SQL seleciona os três contadores de spark_events com argMax por ts → StageAggregate usa defaults zero se a entrada omitir campos → retry_pressure lê counted failures. O percurso JAR→OTLP→DDL é contexto declarado da spec e de #89, não uma integração reproduzida ou integralmente reinspecionada nesta revisão.

### Consequências e risco

Sem reconciliação: ruído de fila e possível reimplementação de campos que já estão presentes. Não foi identificada regressão nova nesse recorte estático; isso não demonstra ausência de todo risco nem suíte atual passando. Confiança alta na presença de campos/SQL; execução atual não verificada.

### Alternativas e recomendação

Recomendado: registrar aceite retrospectivo apontando a644a63/#89 e mover para done, sem 'carimbar' execução nova; se o processo exigir eval, executá-lo numa etapa autorizada contra o SHA de integração e guardar recibo. Alternativa: mover para done com nota 'aceite não formalizado', preservando accepted=false. Não reimplementar.

### Dependências e paralelismo

Nenhuma dependência técnica. retry-pressure-watcher depende desta e também está implementada. Pode ser reconciliada em paralelo com as outras três specs de #89.

### Plano e aceite propostos

Passos mínimos: nota de implementação a644a63 e integração c67ba0e/#89; distinguir AuthorDate/CommitDate e criação da spec; conferir quem registra a transição documental e eventual aceite. O eval de modelo mínimo cobre default zero somente no modelo, sem se tornar prova de linha real via store ou preservação completa do enum. Se prova nova for exigida pelo processo, definir primeiro contrato e SHA, evitando transformar presença estrutural em aceite automático.

### Comunicação entre responsáveis

Explicar: 'Os contadores retry-safe estão no Engine desde #89 (2026-09-14); a spec ficou ready porque ninguém fez a transição. Proponho fechar com referência ao commit, sem fingir uma execução nova.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Trocar defaults zero por Optional mudaria o contrato de linhas históricas esperado pelos consumidores. Que caso o teste ainda não cobre? Caso a conferir: valores nulos ou schema parcial na fronteira real de leitura, sem supor que os evals os cobrem. Como eu explicaria isso para outro pod? Campos, SQL e enum estão presentes; estado ready e aceite formal são dimensões separadas.

### Próxima ação e encerramento

Ação: reconciliação documental de status. Owner a confirmar: Engine (Pod 2). Entrada: commit a644a63 e PR #89. Saída: spec em done com nota de origem do aceite, ou accepted=false explícito. Encerramento: arquivo em tasks/done com rastreio ao SHA.

