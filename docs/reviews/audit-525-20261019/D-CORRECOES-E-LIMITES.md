> Corte histórico da consolidação. Consulte o adendo de 19/10 no diretório Pod3 para os objetos atualizados; contagens antigas abaixo são preservadas como origem.

# Correções de decisão — Parte 04

Estas correções substituem somente a interpretação da consolidação. Os relatórios anteriores continuam preservados para mostrar a evolução da análise. Uma proposta do Codex não é decisão do mantenedor.

## C04-01 — #162 não corrige persistência

O diff altera `apex_verify.__version__` de 0.3.0 para 0.1.0 e acrescenta dois testes. `Verdict.verify_version` já tem default 0.1.0 na main; `to_row()` serializa o valor da instância. Portanto não há migração, correção de linhas antigas ou novo caminho de persistência nesta PR. O teste novo apenas impede divergência futura entre metadata, módulo e default.

**Efeito:** retirar a relação causal de B/C01 e das decisões derivadas; manter política futura de versão em DEC-N2, sem transformá-la em bloqueio automático. A PR tem três checks verdes do CI atual. [Ficha #162](fichas-01.md#item-006), diff (referência no acervo de origem: `fontes/pr162-files.json`), modelo atual (referência no acervo de origem: `fontes/main-verify-models.txt`).

## C04-02 — CI precisa de recorte por SHA e workflow

No mesmo SHA da main, a consulta direcionada retornou **3/3 runs**: CI push `37831091789` falho; JAR push `37831091718` falho; JAR agendado `38266693976` verde. Assim, há prova hospedada parcial na main, mas não um CI principal verde nesse conjunto. O JAR verde não comprova lanes Python/Front/root.

Nas PRs, #157–#159 têm 11 checks verdes cada do workflow antigo; #161/#162 têm três do atual; #155 tem 11 falhos; #163/#164 não têm checks no head. Não chamar o acesso atual ao CI de universalmente bloqueado, nem transportar os 33 checks antigos para uma árvore integrada futura. Consulta completa por SHA (referência no acervo de origem: `fontes/runs-current-main.json`), fichas individuais (referência no acervo de origem: `B-FICHAS-PRS.md`).

## C04-03 — #163 é uma pilha de branches

A base da #163 é a branch da #157, no head `a3ed972`; a PR adiciona um arquivo de teste que importa seus helpers. Um merge como aberto entra nessa branch, não diretamente na main. O workflow do head filtra PRs para `main` e pushes para `main`, `feat/**`, `fix/**`; `codex/**`→`codex/**` explica a falta de disparo automático. O arquivo também contém `workflow_dispatch`.

**Efeito:** registrar duas opções legítimas: integrar #157 e reposicionar #163, ou integrar a pilha na branch e validar a combinação antes de main. Não afirmar que todo merge antes de #157 quebra a main, nem que toda prova é impossível antes de retarget. [Ficha #163](fichas-01.md#item-007), workflow exato (referência no acervo de origem: `fontes/pr163-ci.txt`).

## C04-04 — Gates de runner e M1/M3 precisam ser condicionais

A Parte03 identificou contradições entre alternativas de runner e um gate Ubuntu 26 incondicional, e entre o paralelismo M1/M3 e uma regra de merge M1→M3. A consolidação usa dependências específicas. Estudos e definições do contrato #117 podem começar enquanto PRs são revisadas; integração posterior depende do contrato efetivamente escolhido e de conflitos demonstrados, não da numeração de um marco.

Migração de imagem exige escolha: acompanhar rollout, fixar uma imagem suportada ou realizar controle de compatibilidade proporcional. Nenhuma dessas alternativas foi escolhida nesta auditoria. A previsão de datas/versão de Ubuntu veio da investigação anterior; não foi reconsultada nesta Parte04 e precisa reconfirmação antes de uma ação operacional. Fila corrigida (referência no acervo de origem: `E-FILA-E-DEPENDENCIAS.md`), resíduos registrados na Parte03 (referência no acervo de origem: `../parte-03-claude-v2/PARECER-CLAUDE-V2.md`).

## C04-05 — A Task-Spec parked já declara substituição

`T-20260923-console-auto-prefers-api` diz no `blocked_reason` que foi substituída em 29/09 por `fab6620`. A proposta antiga permitia fallback após 401; o código atual seleciona API em 401. Também distingue resposta API de um 200 com HTML. A ficha Claude dizia que a preferência ainda estava por decidir, embora transcrevesse o motivo de substituição em outro campo.

**Efeito:** catalogar como substituída; não reexecutar a spec antiga nem bloquear seu encerramento documental em #171/#122. [Ficha corrigida](fichas-02.md#item-013), resolver atual (referência no acervo de origem: `fontes/main-repository.txt`), apiPing atual (referência no acervo de origem: `fontes/main-http.txt`).

## C04-06 — Três TaskPlans não são YAML válido

O parser seguro rejeita `l2-discover.yaml` na linha 53, `serve-api-e2e.yaml` na linha 101 e `serve-api.yaml` na linha 20. Nos trechos indicados há `: ` dentro de valores plain não corretamente delimitados. As aspas internas de um comando shell não passam a delimitar o escalar YAML inteiro. As cópias correspondem aos blobs Git previamente verificados.

**Efeito:** não declarar esses manifestos prontos para regenerar/despachar. Corrigir sintaxe e verificar o consumidor antes de eventual reuso. Não se conclui que o harness histórico falhou, nem que a implementação das PRs correspondentes está quebrada. Não reabrir as PRs integradas só por isso. Diagnósticos e limites (referência no acervo de origem: `F-LEITURA-TASKSPECS.md`), resultado estruturado (referência no acervo de origem: `F-VERIFICACAO-TASKSPECS.json`).

## C04-07 — Sem Closes não significa sem teste ou sem fluxo

Nas issues #1–#3, comentários de encerramento nomeiam configuração e controles; #4 declara substituição da proposta pelo contrato. A ficha genérica “fluxo não aplicável porque encerrada” apaga a explicação, e “não há PR Closes, então não há teste ligado” vai além da evidência consultada.

**Efeito:** manter os encerramentos, registrar o fluxo histórico e seus limites, e tratar testes não localizados como não verificados. Não inventar ausência universal nem reabrir por falta de link textual. Quatro casos foram corrigidos individualmente; **os demais encerrados ainda precisam da mesma revisão**, não recebem aceite por analogia. Fichas #1–#4 (referência no acervo de origem: `C-FICHAS-CORRIGIDAS.md`), comentários preservados (referência no acervo de origem: `../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/icomments_all.json`).

## C04-08 — Review formal e cobertura têm fronteiras

O endpoint de reviews está vazio nas oito PRs abertas consultadas. Isso não permite afirmar que todas as PRs integradas em 06/10 não tiveram review. Do mesmo modo, 525 fichas com 14 rótulos não são 525 revisões semânticas. A Parte04 conserva esses estados como dimensões distintas no inventário.

**Efeito:** a fila inicial pode ser usada para orientar revisão; não é um aceite do backlog inteiro. Não chamar autor de responsável designado, `approved: true` de nova autorização, `accepted: true` de execução independente, nem publicação de implementação. Contagem auditável (referência no acervo de origem: `COBERTURA.json`), inventário (referência no acervo de origem: `A-INVENTARIO-525.json`).

## C04-09 — Reconciliação posterior prevalece sem apagar a origem

Os 158 `historical_record` do MATRIX.json são iguais às 158 linhas do CSV preservado. O MATRIX.json já contém reconciliação pública; PUBLICATION.json registra mudanças posteriores. Entre elas: F06 reutiliza #117; E17 reutiliza #123; S02 reutiliza #156; L14 é agrupado em #180. Não voltar a publicar minutas antigas como trabalho independente.

**Efeito:** o registro derivado conserva tanto o destino da triagem como a disposição de publicação; não colapsa 525 origens em 525 implementações nem transforma toda referência histórica a PR em “implementado por”. Isso comprova reconciliação documental, ainda não o mérito técnico integral de cada classificação. Visão dos 158 IDs (referência no acervo de origem: `A-REGISTRO-158.json`).

## C04-10 — #123 tem runtime histórico documentado

O documento de entrega e o corpo da PR #127 registram o núcleo Spark→Collector→ClickHouse→Engine em 20/09 e o wrapper público macOS/Spark 4.0.1 em 21/09. O segundo usou cache de imagens e recursos parciais; não foi cold start de um daemon vazio. A revisão consultou o relato, sem reproduzi-lo nem certificar a main atual. A razão `373,364` pertence ao núcleo de 20/09; não deve ser transferida ao job do wrapper de 21/09.

**Efeito:** substituir “runtime ausente” por “runtime histórico relatado, com escopo e limites”; reconciliar os critérios com esse recibo antes de exigir repetição. E14/P02/G04 devem preservar a plataforma/versão realmente relatadas. [Ficha #123](fichas-02.md#item-016), delivery record (referência no acervo de origem: `fontes/lote2-docs__e2e__TAIL_OUTLIER_RUNTIME_GATE.md.txt`).

## C04-11 — O gate atual não compara stage/snapshot nem valida o contador impresso

`Invoke-TailOutlierGate` passa o job_id ao Engine com `--dry-run --no-crew`, exige código de saída zero e procura `tail_outlier_watcher` em toda a saída. Não compara o finding ao stage/snapshot/população selecionado pela asserção; o marcador final imprime `llm_calls=0` como literal. Isso limita a garantia do gate, sem demonstrar um falso PASS real ou uma chamada LLM efetiva.

**Efeito:** DEC-N6/E17 precisam escolher a garantia e alinhar os controles a ela. Uma opção por garantia apenas no job não pode coexistir com aceite obrigatório de associação forte sem decisão adicional. A ficha anterior dizia que o gate já provava o stage escolhido, excedendo a fonte. Código do wrapper (referência no acervo de origem: `fontes/lote2-scripts__apex.ps1.txt`), teste estrutural (referência no acervo de origem: `fontes/lote2-tests__test_tail_outlier_package.py.txt`), [ficha #123](fichas-02.md#item-016).

## C04-12 — #124 ainda não prova a invocação de cada handler

A issue exige testes separados que alcancem o handler esperado de cada ação. O teste atual executa `-DryRun` e compara a string `Handler`; o ramo retorna antes de executar o scriptblock `Command`. Trocar somente `Command` mantendo `Handler` não altera o resultado dessa comparação. Os mapeamentos atuais parecem corretos na leitura; a lacuna é a força da prova, não um dispatcher trocado observado.

**Efeito:** retirar “manter aberta só gera ruído” e “fechar após CI verde”. O critério permanece aberto até controle discriminante sobre a chamada, com handlers inofensivos, ou alteração explícita de escopo pelo mantenedor. G04/G08/P03 não podem converter a lacuna em melhoria opcional após o fechamento. Critérios públicos (referência no acervo de origem: `fontes/lote2-issue124.json`), teste (referência no acervo de origem: `fontes/lote2-tests__test_apex_initial_package.py.txt`), [ficha #124](fichas-02.md#item-017).

## C04-13 — #115 já testa conflito e não exige três PRs

O resolver e seus testes distinguem o mesmo stage ligado a duas execuções não nulas de vários stages válidos de uma execução. Também cobrem escopo estrangeiro, tentativas, ausência e zero. O sentinel `-1` de AQE é explicitamente de nível de job. A lacuna de integração pública não autoriza substituir todos os findings de job por stages nem impor exatamente três PRs.

**Efeito:** E02 deve selecionar a primeira superfície e preservar os estados existentes; E01 conserva a prova SQL/RDD delimitada. A pergunta anterior sobre conflito “não testado entre dois stages” deve ser substituída por controles do adapter/consumidor efetivo. Testes existentes (referência no acervo de origem: `fontes/lote2-engine__tests__test_execution_attribution.py.txt`), resolver (referência no acervo de origem: `fontes/lote2-engine__src__apex_engine__attribution.py.txt`), [ficha #115](fichas-02.md#item-014).

## C04-14 — #117 não termina na reunião de decisão

Há omissão de `attributable` em `to_row`, diferença `>=`/`>` e fórmulas de piso distintas. Os DDLs lidos não têm a coluna de atribuição. O Serve já possui leitura/projeção de verificações; a afirmação antiga de ausência não descreve a main. A perda de representação está demonstrada estaticamente, mas não um incidente persistido. `compare_runs` usa fração para o piso; replay/linhas usam percentual, exigindo normalização explícita.

**Efeito:** decisões e folhas são passos intermediários; os critérios de comportamento, compatibilidade e rota continuam exigíveis salvo revisão explícita de escopo. Não declarar persistência fora da v1 por conta própria, não planejar uma migração com coluna presumida e não recriar as correções já integradas de piso inválido ou mecanismo/runtime. [Ficha #117 e fontes](fichas-02.md#item-015).

## C04-15 — #178 não depende de toda a política de ownership

O corpo público permite testar propagação do endpoint antes da decisão global de identidade. L09 ainda carregava E09/DEC-10 como predecessor incondicional. A inspeção também mostra que passar uma variável ao container não basta em todos os caminhos: é necessário seguir sua tradução até a configuração do Spark.

**Efeito:** remover o gate universal de ownership do trabalho offline de propagação. Definir precedência e controlar o comando final com e sem override. Não usar `make -n` como garantia de ausência de efeitos: `dev/Makefile` contém `$(shell docker network inspect ...)` avaliado durante a expansão. Corpo #178 (referência no acervo de origem: `fontes/batch-public-sources/issue-178.md`), Makefile (referência no acervo de origem: `fontes/batch-public-sources/dev__Makefile.txt`), [ficha #178](fichas-04.md#item-031).

## C04-16 — A correção de texto também alcança guardas estáticas

`test_telemetry_compatibility_matrix.py` exige literalmente `PROPOSED v0.4`, `PROPOSED, not ratified` e a frase obsoleta de `models.py` sobre a inexistência de `executor_run_time_ms`. Alterar somente esses textos pode fazer a guarda falhar mesmo preservando a intenção documental. Não se executou essa falha nesta auditoria; a dependência é visível nas asserções.

**Efeito:** coordenar #165 e o pequeno ajuste textual de #179/CL-02 com as asserções correspondentes, preservando a história e exigindo fonte para ratificação. A revisão integral de #180 não é predecessor obrigatório para toda correção. Guarda estática (referência no acervo de origem: `fontes/batch-public-sources/tests__test_telemetry_compatibility_matrix.py.txt`), fichas #165/#179/#180 (referência no acervo de origem: `H-FICHAS-ISSUES-PUBLICADAS.md`).

## C04-17 — `verifies` completo não significa teste discriminante

Em `l5-fix.yaml`, a folha `verify-fix-tool` associa B-2 (payload da verificação) a um comando que só lista tools/anotações. B-3/B-4 (sem verificação e recusa de segurança) são associados a um grep que procura a expressão `Five tools`. Em `l6-learn.yaml`, `recall-runs-tool` repete o problema para payload, shape ausente e memória indisponível. Esses comandos não exercitam os comportamentos anunciados.

**Efeito:** corrigir o mapeamento antes de reutilizar os planos ou alegar aceite pelos evals. Isso não prova ausência de outros testes ou defeito runtime. A checagem anterior dos 87 conjuntos de `verifies` continua válida apenas como integridade de IDs declarados. Plano L5 (referência no acervo de origem: `../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_l5-fix.yaml`), plano L6 (referência no acervo de origem: `../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_l6-learn.yaml`), fichas dos planos (referência no acervo de origem: `J-FICHAS-PROPOSTAS-E-PLANOS.md`).

## C04-18 — Um plano com várias unidades não herda só a primeira intenção

`l1-connect.yaml` contém 23 unidades: status/saúde, configuração, distribuição/publicação, clientes, gates e documentação. Resumi-lo como apenas `ServerStatus`, ou tratá-lo como integralmente entregue pela referência histórica #79, elimina fronteiras e decisões relevantes.

**Efeito:** preservar todas as unidades e sua DAG histórica; não reexecutar publicação por encontrar `approved: true` ou uma folha `ready`. Os 19 planos receberam leitura documental própria; essa contagem não inclui automaticamente as 87 Task-Specs individuais. [Ficha L1](fichas-06.md#item-054), plano original (referência no acervo de origem: `../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_l1-connect.yaml`).

## C04-19 — O arquivo da #105 já existe e foi restaurado nesta auditoria

Localizei o arquivo de 26/08 no diretório indicado pelo registro de custódia: bundle, mapa de branches, snapshot de uso em PRs, README e prova de restauração. Em 17/10, a conferência SHA-256 passou **5/5**; `git bundle verify`, fetch dos cinco refs para bare temporário, comparação com o mapa e `git fsck --full --strict --no-dangling` passaram. O repositório temporário foi removido. Hash do bundle: `5523adca7e3e2a512452145b19c530de7dc8268b5cb4d8297ea809651896b526`.

A ficha X06 já transcrevia “bundle existe” no problema, mas depois afirmava “bundle não criado” e mandava criá-lo. O corpo público antigo da #105 não prevalece sobre o arquivo local diretamente conferido para esse fato.

**Efeito:** substituir criação por reconciliação de critérios/custódia. Nenhum código arquivado foi executado; nenhuma branch foi excluída/publicada. A restauração não demonstra heads/uso remoto atuais, que precisam de consulta específica antes de eventual exclusão. Recibo novo (referência no acervo de origem: `fontes/batch-custody-sources/VERIFICACAO-CODEX-20261017.json`), mapa original (referência no acervo de origem: `fontes/batch-custody-sources/BRANCH-TO-SHA.tsv`), [ficha #105](fichas-10.md#item-092).

## C04-20 — Dependência de implementação não bloqueia todo estudo

#106 permite expressamente estudos paralelos de #107/#108/#109, reservando o schema para a implementação. #108 diz que um catálogo MCP é provedor opcional. #113 declara não ter predecessor técnico para desenhar o protocolo. #114 declara não ter predecessor para design, mantendo autorização própria para runtime. A #122 permite discutir transporte enquanto #115/#117 conservam limitações explícitas.

**Efeito:** retirar “aguardar #106/#170/#167” como próxima ação universal desses estudos; preparar contratos e casos em paralelo, com gates apenas na implementação/execução que deles depende. #33 também não é predecessor técnico universal de todo estudo on-prem #42. Fichas e fontes das issues (referência no acervo de origem: `M-FICHAS-ISSUES-RESTANTES.md`).

## C04-21 — Estado de discussão não comprova ausência de trabalho

Zero comentários ou caixas abertas só descrevem os objetos consultados. A #112 mostra por que é necessário ler a sequência inteira: o comentário primeiro registra falta de schema; depois registra JSON Schema e três exemplos com correção da allowlist de versão. Isso continua proposta local relatada, sem validador/consumidor implementado, mas não é mais simplesmente “schema não entregue”. O registro X07 também relata um exemplo de grafo anterior.

**Efeito:** trocar “sem trabalho” por “nenhuma entrega/decisão demonstrada neste recorte”, quando aplicável, e preservar artefatos locais como relatos até inspeção. Não confundir baseline negativa bem formada com documento inválido nem repetir a lacuna de uma etapa já complementada. Comentário completo da #112 (referência no acervo de origem: `fontes/batch-rest-issues-sources/issue-112.md`), [ficha #112](fichas-10.md#item-097).

## C04-22 — Um CI verde na main não substitui sozinho os critérios da #130

O corpo original exige início de steps/logs e reruns específicos de #126–#128. Essas PRs foram integradas e existem sucessos posteriores de outros heads/workflows. Um run principal na main pode ser a prova útil que o mantenedor escolher, mas é necessário reconciliar essa escolha com os critérios antigos; não transformar a sugestão da revisão em alteração silenciosa do aceite.

**Efeito:** manter capacidade de execução, resultado de suíte e política financeira como dimensões distintas; não bloquear toda a fila onde há verdes observados. Registrar satisfação ou revisão explícita de cada critério. Critérios da #130 (referência no acervo de origem: `fontes/batch-rest-issues-sources/issue-130.md`), [ficha #130](fichas-11.md#item-102), runs da main (referência no acervo de origem: `fontes/runs-current-main.json`).

## C04-23 — C2/31 passes pertence ao gerador G2, não ao candidato APEX

A ficha CL-06 da v2 associa a rodada C2 ao candidato #167/#174. O recibo primário nomeia `T-20261012-clean-g2-structural-verify-r2`, base `d9e32f17…`, e dois inputs: `generate_g2_results.candidate.v2.py` (SHA `21066b5a…`) e sua suíte (`f5fba79e…`). Os dois hashes foram conferidos nesta auditoria. O objeto é o gerador G2 com executor falso, sem implementação APEX. A tarefa real permanece `accepted: false`; o `ACCEPTED=1` do trial pertence a clone/attempt separado.

**Efeito:** retirar a aresta automática CL-05/CL-06 → CL-01/DEC-15. O problema de preflight pode bloquear o aceite daquela tarefa G2; não prova falta de aceite do patch APEX nem é gate técnico automático de sua publicação. Não transferir os 31 passes. Recibo primário (referência no acervo de origem: `fontes/batch-local-review-sources/g2-structural-receipt.md`), spec real (referência no acervo de origem: `fontes/batch-local-review-sources/g2-structural-task.md`), tentativas (referência no acervo de origem: `fontes/batch-local-review-sources/g2-acceptance-attempts.md`), [ficha CL-06](fichas-11.md#item-110).

## C04-24 — Duas variantes da #167 exigem linhagens de prova distintas

O `candidate.patch` SHA `1122d0316302ccad0534bd365584e2ee8a4b74df61939ab11e14b2ac3c53eec7` usa `PositionalBinding = $false` e também altera wrapper/docs/testes para #174. O `PATCH-167.diff` da rodada posterior mantém `[CmdletBinding()]` padrão e altera somente o runner. Os seis casos argv pertencem ao segundo; a prova integral e2e de dez casos usa cópias do primeiro, fixadas pelo manifesto de inputs. A diferença não é mera preferência obsoleta de um revisor.

**Efeito:** escolher contrato e bytes antes de reunir evidência. Não dizer que o patch `1122d031…` usa binding padrão, nem somar os seis casos como se fossem executados sobre ele. A prova integral e2e registra macOS/stubs e um endpoint HTTP fictício em loopback: não é zero rede/sockets nem cobertura de todas as ações. Candidato conjunto (referência no acervo de origem: `fontes/batch-local-review-sources/candidate-1122d031.patch`), patch runner (referência no acervo de origem: `fontes/batch-local-review-sources/patch-167-default-binding.diff`), prova argv (referência no acervo de origem: `fontes/batch-local-review-sources/argv-proof-report.md`), teste integral (referência no acervo de origem: `fontes/batch-local-review-sources/entrypoint-test.py`).

## C04-25 — Os quinze itens Windows não provam o wrapper integral

O protocolo explicitamente exclui o entrypoint completo. `w07` extrai o helper; a própria asserção de preservação é comentada como vácua por construção. `w01` exige binding false, portanto não pode ser aplicado sem reconciliação à variante padrão. Os **14 arquivos** listados no manifesto conferiram; **15** é a quantidade esperada de itens pytest. Não foi localizada execução nativa Windows nestas fontes.

**Efeito:** manter a prova proposta de runner/helper delimitada e criar caso integral separado se essa for a garantia pretendida. Corrigir a expressão de CL-03 “código do pacote na main”: o pacote é local. Quinze passes futuros não suprirão automaticamente um critério não exercitado. Protocolo (referência no acervo de origem: `fontes/batch-local-review-sources/windows-protocol.md`), fixtures (referência no acervo de origem: `fontes/batch-local-review-sources/windows-tests.py`), conferência de hashes (referência no acervo de origem: `fontes/batch-local-review-sources/CAPTURA-E-INTEGRIDADE.json`).

## C04-26 — Correção documental de gerador e trial positivo não são adoção nem prova completa

Já existe cópia arquivística do gerador G2 corrigindo a linguagem de isolamento, além do original preservado com a frase incorreta. Ambas ainda contêm chamadas host e caminhos fixos: a cópia textual não é tooling adotado. No fix de preflight 3.9.0, a expressão `else structural` também alcança strings não vazias sem dois-pontos. O ramo de HMAC com separador permanece no diff, mas um trial estrutural positivo não demonstra recusa de todos os casos inválidos ou preservação integral da política.

**Efeito:** CL-04 deve apontar a correção já existente e decidir destino do tooling; CL-05 requer controles de assinatura/tier/revisão/base e domínio do valor, sem anunciar uma vulnerabilidade demonstrada. Nada foi executado nesta revisão. Original (referência no acervo de origem: `fontes/batch-local-review-sources/g2-original.py`), correção documental (referência no acervo de origem: `fontes/batch-local-review-sources/g2-archival-correction.py`), patch preflight (referência no acervo de origem: `fontes/batch-local-review-sources/preflight-proposal.patch`), trial (referência no acervo de origem: `fontes/batch-local-review-sources/preflight-trial.log`).

## C04-27 — O resumo histórico do Claude mistura intervalos e extrapola jobs sem steps

AH-02 afirma que os 61 runs de CI entre 20/09 e 06/10 falharam sem executar. Recalculando as três páginas recebidas com `name=CI` e `created_at` UTC nesse intervalo inclusivo, são **68 runs: 56 failure e 12 cancelled**. Os 61 failures citados no extrato do Claude pertencem a outro intervalo, 15/09–12/10. No pacote há jobs de **22 dos 68 runs**, somando 242 jobs e zero steps nessas observações. Os 46 restantes não têm recibos de jobs nesse pacote; failure não autoriza preencher essa lacuna com zero steps.

O texto de billing na review `5268257112` é relato do Copilot preservado pela API. Sua existência é observável; não equivale a uma consulta financeira nem à anotação primária do job. Tampouco determina sozinho o instante em que um bloqueio começou.

**Efeito:** corrigir contagem, intervalo, classe da causa e alcance da amostra em AH-02/DEC-01. Recálculo Codex (referência no acervo de origem: `fontes/batch-claude-history-sources/VERIFICACAO-CODEX.json`), página 1 (referência no acervo de origem: `fontes/batch-claude-history-sources/claude/fontes/api-reviews/actions-runs-page1.json`), página 2 (referência no acervo de origem: `fontes/batch-claude-history-sources/claude/fontes/api-reviews/actions-runs-page2.json`), página 3 (referência no acervo de origem: `fontes/batch-claude-history-sources/claude/fontes/api-reviews/actions-runs-page3.json`), review do bot (referência no acervo de origem: `fontes/batch-claude-history-sources/claude/fontes/api-reviews/pr129-reviews.json`).

## C04-28 — Ausência de verde no head não demonstra que testes nunca rodaram

AH-14 transforma a consulta aos heads das 28 PRs de outubro em “testes nunca rodaram em CI hospedado”. Essa conclusão não decorre dos dados: existem verdes posteriores em outras árvores e workflows. Eles não são prova automática da integração dessas PRs, mas impedem concluir ausência universal sem examinar o que executaram. A listagem de 213 runs começa em 26/07; ser completa para a resposta retida da API não significa conservar toda a história e todas as tentativas.

**Efeito:** dizer quais heads/tentativas não têm verde observado e qual árvore ainda precisa de prova. Distinguir criação, início, conclusão e atualização do run; uma hora de `created_at` não é a hora em que o CI ficou verde. A nova versão histórica foi solicitada e ainda depende de revalidação por ID. Consulta da main por SHA (referência no acervo de origem: `fontes/runs-current-main.json`), checks #157 (referência no acervo de origem: `fontes/pr157-checks.json`), checks #161 (referência no acervo de origem: `fontes/pr161-checks.json`), resumo original preservado (referência no acervo de origem: `fontes/batch-claude-history-sources/claude/ACHADOS.md`), [NOV-02](fichas-14.md#item-135).

## C04-29 — Política de CI precisa de resultados possíveis, sem gates globais presumidos

DEC-01/02/N4 e NOV-07 herdavam bloqueios universais de billing e propunham sentinela sem explicitar seu trigger. Uma sentinela dentro de workflow omitido pelos filtros também não roda. `protected=false` não substitui a inspeção de todos os rulesets; desenho de política não precisa esperar resolução de toda a capacidade operacional. Rerun preserva SHA/ref do evento original; um novo evento só é prova útil depois de identificar a árvore e o workflow realmente executados. [Comportamento documentado de rerun](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs), [checks omitidos por filtros](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs).

**Efeito:** formular tabela por cenário docs/jar/código/misto, regra e resultado. Revisões independentes e estudos podem correr em paralelo. Não descartar prova antiga pertinente ao mesmo head, nem rotulá-la como prova de árvore nova. Workflow fixado (referência no acervo de origem: `fontes/batch-governance-sources/.github__workflows__ci.yml`), [DEC-02](fichas-14.md#item-131), [DEC-N4](fichas-14.md#item-137), [NOV-07](fichas-15.md#item-142).

## C04-30 — A decisão do ADR-004 precede a implementação candidata

A ficha DEC-11 da v2 propunha decidir apenas quando houvesse implementação candidata. O próprio ADR exige decisões de owner sobre locators, root/sintaxe, notebooks, payload e consumidor **antes** de Task-Spec ou PR de implementação. O índice canônico já existe; a questão residual não é recriá-lo nem renumerar a história. Atribuição execução-stage da #115 não resolve correlação arquivo/linha/célula.

**Efeito:** remover a dependência invertida, preparar as decisões de fronteira primeiro e conservar a implementação como não autorizada pelo documento. Não impor esse estudo como gate universal da v1. ADR-004 (referência no acervo de origem: `fontes/batch-governance-sources/docs__architecture__ADR-004-SOURCE-CORRELATION-BOUNDARY.md`), índice (referência no acervo de origem: `fontes/batch-governance-sources/docs__architecture__ADR-INDEX.md`), [DEC-11](fichas-15.md#item-148).

## C04-31 — Metadados externos não sustentam conclusões mais amplas

O recibo da Dataship PR #2 informa `changed_files=1426`; isso significa arquivos alterados, não necessariamente 1.426 arquivos adicionados. Uma resposta pública 404 do workspace não identifica sozinha a causa como “privado”. Da mesma forma, tag Git não é prova suficiente de release publicada, e metadata de pacote não prova distribuição no PyPI.

**Efeito:** manter estado externo datado e a classe de cada evidência; não criar gates APEX a partir de hipóteses sobre outro repositório. DEC-20/21/N2 foram corrigidas sem afirmar acesso a conteúdo indisponível nem revisão completa dos diffs externos. API Dataship PR #2 (referência no acervo de origem: `../parte-02-gemini/evidencias/dataship-pr2.json`), [DEC-20](fichas-16.md#item-155), [DEC-21](fichas-16.md#item-156), [DEC-N2](fichas-15.md#item-143).

## C04-32 — Main igual e consulta since vazia não revalidam todo o snapshot

O pacote Claude de 147 IDs afirma que `main` igual e respostas vazias de issues/comentários atualizados desde 15/10 tornam todo o snapshot de 16/10 atual. Essas consultas não verificam por si reviews, checks, rulesets ou todas as tentativas de workflow. Os estados continuam ligados aos respectivos endpoints e datas.

**Efeito:** remover a reconfirmação universal. Em 18/10 o Codex consultou separadamente a branch, as coleções abertas, reviews e checks dos oito heads, além dos comentários. Permanecem 8 PRs, 36 issues e zero reviews formais nos oito endpoints; isso não prova ausência de leitura humana. A consulta de rulesets incluindo pais retornou lista vazia nesse endpoint, e a branch informa `protected=false`; não houve inspeção administrativa independente de todas as políticas externas. Branch (referência no acervo de origem: `fontes/batch-publication-current-sources/main.json`), PRs (referência no acervo de origem: `fontes/batch-publication-current-sources/open-pulls.json`), issues (referência no acervo de origem: `fontes/batch-publication-current-sources/open-issues.json`), rulesets (referência no acervo de origem: `fontes/batch-publication-current-sources/rulesets.json`).

## C04-33 — A #132 deixou contradição documental sobre list_runs

P06 no novo parecer afirma que a PR integrada não tem resíduo próprio. No diff e na base, `docs/lanes/SERVE-LEGS.md:12` lista `list_runs`, mas as linhas 29–32 afirmam que toda tool exige `job_id` e que a lane não ajuda a descobrir runs. A função `list_runs` existe em `server.py:362`; o mesmo documento marca L2 como entregue. O cabeçalho conserva um snapshot de agosto junto de conteúdo atualizado, exigindo distinguir história da descrição atual.

**Efeito:** registrar uma correção documental pequena, preservando o corte histórico. Não criar uma implementação duplicada de list_runs, nem considerar que o diff atual da #164 já cobre esse arquivo. A entrega da PR #132 permanece integrada; o resíduo passa a ter destino explícito na preparação para os pods. Diff e corpo #132 (referência no acervo de origem: `fontes/batch-root-p-sources/pr132.json`), documento na base (referência no acervo de origem: `fontes/batch-root-p-sources/docs__lanes__SERVE-LEGS.md`), servidor (referência no acervo de origem: `fontes/batch-root-p-sources/serve__src__apex_mcp__server.py`).

## C04-34 — P05 precisa conservar os relatos posteriores e seus ambientes

A ficha P05 repete 154 passes/11 skips e o erro de coleta da lane como se descrevessem toda a prova mais recente. O corpo público da #131 relata 226 passes/11 skips de Engine+root no head `7b7b9b4`, além de 160/11 e 65 de root no predecessor `672dc1f`. O relatório E03, de outro ambiente/conjunto, registra erro de coleta por dependências e 161/10 após ignorar um arquivo; sua prova real cobre apenas connect/preflight em databases sem registros.

**Efeito:** não apagar resultados posteriores nem reconciliar números de suítes diferentes por soma. Preflight relatado não prova leitura/INSERT, e nenhum desses relatos certifica a main atual. Corpo atualizado e metadados #131 (referência no acervo de origem: `fontes/batch-root-p-sources/pr131.json`), relatório E03 (referência no acervo de origem: `fontes/batch-root-p-sources/E03-REPORT.md`), origem e hash (referência no acervo de origem: `fontes/batch-root-p-sources/E03-ORIGEM.json`).

## C04-35 — B-5 do gate inclui preservação de ambiente, além da associação do finding

A spec T-20260920-tail-outlier-runtime-gate exige não sobrescrever configuração nem reutilizar recursos alheios. O helper do wrapper usa Copy-Item -Force sobre dev/.env, e o registro de entrega admite ausência de ownership check. Isso é uma lacuna distinta de stage/snapshot/população e do contador LLM literal; escolher garantia fraca de associação não resolve B-5.

**Efeito:** conservar o runtime histórico como relato delimitado e encaminhar preservação de configuração/ownership pelas #174/#175, com folha própria do wrapper, que é Do-Not-Touch desta spec. A estratégia pode ser EnvFile direto, recusa ou outra alternativa aprovada. Estudo offline não espera uma execução nova. Spec (referência no acervo de origem: `fontes/batch-revalidated-specs28-sources/git/tasks/T-20260920-tail-outlier-runtime-gate.md`), registro de entrega (referência no acervo de origem: `fontes/batch-revalidated-specs28-sources/git/docs/e2e/TAIL_OUTLIER_RUNTIME_GATE.md`), wrapper (referência no acervo de origem: `fontes/batch-revalidated-specs28-sources/git/scripts/apex.ps1`).

## C04-36 — Estrutura do modelo não garante conteúdo sanitizado em strings

ServerStatus e using_defaults têm descrições de ausência de credenciais/nomes de variáveis. Strings livres e list[str] não restringem por si os valores a nomes permitidos. Os testes lidos conferem estrutura e fixtures conhecidas, não a promessa absoluta de qualquer resposta sem credenciais. Não foi localizado produtor do status MCP no recorte Serve/src, nem foi demonstrado vazamento.

**Efeito:** manter o done/accepted histórico como declaração e, se a funcionalidade for retomada, definir a fronteira que sanitiza valores e seu controle negativo. Não inventar incidente ou reabrir toda a entrega só para uma nota documental. Modelo (referência no acervo de origem: `fontes/batch-revalidated-specs28-sources/git/serve/src/apex_mcp/models.py`), testes (referência no acervo de origem: `fontes/batch-revalidated-specs28-sources/git/serve/tests/test_status.py`).

## C04-37 — Literais SQL dos watchers não demonstram o caminho ativo

E04 contava seis constantes SQL qualificadas nos watchers como se esse fosse o caminho executado. run_all chama store.stage_aggregates e run_all_offline, que percorre evaluate; não chama essas constantes no trecho lido. A busca por padrões também incluiu exemplos em prosa no Serve/Verify.

**Efeito:** a #173 precisa classificar SQL executável, exemplo e alcançabilidade por consumidor, sem substituição global de apex. Contagem lexical não prova seleção efetiva de database. Caminho dos watchers (referência no acervo de origem: `fontes/batch-revalidated-fes-sources/engine__src__apex_engine__watchers____init__.py.excerpt.txt`), busca delimitada (referência no acervo de origem: `fontes/batch-revalidated-fes-sources/database-literal-search.json`).

## C04-38 — p50 zero afeta a checagem da razão, não o CV de runtime do piso

noise_floor filtra irmãs com p50 efetivo positivo para calcular a instabilidade p99/p50; o CV do runtime usa separadamente job_runtimes_ms positivos. Tratar a exclusão de p50 zero como remoção do cálculo do piso mistura duas garantias. O filtro evita divisão por zero, mas pode deixar menos de três razões sem informar a exclusão.

**Efeito:** a proposta de estudo F20/N01 deve decidir representação ou aviso da exclusão na checagem da razão. Não afirmar veredito errado observado nem mudar automaticamente a fórmula do piso. Guardrails (referência no acervo de origem: `fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/verify__src__apex_verify__guardrails.py.txt`).

## C04-39 — O relato da janela de MV inclui a primeira migração

O ensaio lane1 DEC-25 relata uma janela progressiva tanto na reaplicação quanto na primeira migração v0.1. Linhas sintéticas inseridas na query intermediária preservaram atributos brutos, mas não receberam backfill das colunas tipadas depois. É relato local, sequencial e sem carga; não demonstra incidente de produção, duração operacional nem reparo.

**Efeito:** uma política que proíbe somente reaplicação não cobre o caso da primeira migração relatada. A #170 deve decidir coordenação da ingestão durante evolução de MV e eventual reparo separadamente do estado final do schema. Relatório integral (referência no acervo de origem: `fontes/batch-revalidated-fes-sources/lane1-dec25-report.md`), locadores das migrações (referência no acervo de origem: `fontes/batch-revalidated-fes-sources/migration-query-locators.json`).

## C04-40 — As garantias dos dois arquivos da #157 são complementares

O arquivo same_args chama apenas o helper MCP in-process nos estados populado/vazio com argumentos iguais. O arquivo vizinho compara call_tool in-process com HTTP TestClient. Nenhum desses caminhos é uma sessão MCP stdio real, navegador ou ClickHouse de produto. A #163 acrescenta outra proteção, de hits plan_json, sobre os helpers da #157.

**Efeito:** explicar a composição das garantias sem atribuir ao arquivo same_args uma comparação HTTP que ele não faz, nem vender as provas in-process como E2E de transportes reais. Diff same_args (referência no acervo de origem: `fontes/batch-revalidated-fes-sources/pr157-test_tool_transport_parity_same_args.py.diff.txt`), diff de paridade (referência no acervo de origem: `fontes/batch-revalidated-fes-sources/pr157-test_tool_transport_parity.py.diff.txt`).
