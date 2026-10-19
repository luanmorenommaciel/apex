# Fichas documentais — lote 36

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-351"></a>

## D05 — Normalizar updates AQE

Frente: dataship_externo. Encaminhamento: externo_dataship_planos_adaptativos.

### Identidade e estado

D05 é schema/loader do laboratório: normalizar updates AQE. Minuta local PROP-D05-AQE-UPDATES. Repositório Gabriel-Philot/dataship-spark-plat-v0; decisão upstream. Owner a confirmar.

### Intenção e benefício

Problema: os updates adaptativos de plano ficam só em spark_raw_events; analisar como o AQE reescreveu o plano exige parsear JSON bruto. Público: quem estuda AQE no laboratório. Ganho: planos adaptativos consultáveis.

### Feito, faltante e não comprovado

No DDL e em ensureSchema não há tabela de planos adaptativos; readEventLog preserva tais eventos apenas em raw. O roadmap especifica spark_sql_plan_updates e seis campos. Falta definir identidade, deduplicação e ordenação dos updates; os eventos em si não foram capturados nesta revisão.

### Linhagem

Linhagem: roadmap de exploração do upstream (passo 3, tabela spark_sql_plan_updates a partir de SparkListenerSQLAdaptiveExecutionUpdate) → registro D05 (depende de D02 pela ordem do autor) → minuta PROP-D05 com escopo confuso com D07 → implementação [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-loader.go; fontes/batch-revalidated-wdprops-sources/dataship-ddl.sql; fontes/batch-revalidated-wdprops-sources/dataship-roadmap.md; fontes/batch-proposals-review-sources/PROP-D05-AQE-UPDATES.md. Locadores: Registro/MATRIX D05; DDL/ensureSchema, readEventLog/eventUID, roadmap spark_sql_plan_updates.

### Classe e limite da evidência

FATO OBSERVADO: nenhuma tabela adaptativa no DDL da main; especificação spark_sql_plan_updates no roadmap. PROPOSTA: implementar. DECISÃO PENDENTE: mantenedor. Nenhuma execução.

### Fluxo

Fluxo proposto: evento adaptativo → loader → linha por update identificada por aplicação/execução/evento → histórico de planos. event_time_ms é campo sugerido, mas a ordem precisa contrato quando o evento não fornece tempo ou há empate; eventUID do loader atual inclui bucket, caminho, linha e raw.

### Consequências e risco

Sem a tabela, a análise de AQE no laboratório depende de JSON bruto; o APEX tem seu próprio caminho de AQE (plan_transitions) e não depende disso. Confiança alta.

### Alternativas e recomendação

Recomendado: implementar depois de spark_jobs, com chave (app_id, execution_id, event_uid) para não colapsar updates. Alternativa: view sobre spark_raw_events (sem mudar o loader). Reversível.

### Dependências e paralelismo

D09 e D15 ajudam uma implementação verificável. Jobs antes de AQE é ordem sugerida pelo roadmap, não pré-requisito de estudo; D07 pode estudar planos iniciais independentemente desta tabela.

### Plano e aceite propostos

Passos mínimos: DDL; parsing; teste com um evento adaptativo de fixture; controle de que dois updates da mesma execução não colapsam. Aceite: updates ordenados e distintos.

### Comunicação entre responsáveis

Para outro pod: "O laboratório guarda os replanejamentos do AQE só como evento bruto; a tabela proposta é o passo 3 do roadmap do próprio autor."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Colapsar por execution_id apagaria replanejamentos; assumir tempo sempre presente ordenaria incorretamente casos sem timestamp. Que caso o teste ainda não cobre? Faltam updates repetidos, timestamps ausentes/empatados e dois updates distintos da mesma execução. Como eu explicaria isso para outro pod? D05 guarda o histórico adaptativo do laboratório; D07 extrai nós e é outro escopo.

### Próxima ação e encerramento

Próxima ação: mantenedor upstream (a confirmar) decide se quer planos adaptativos tipados agora ou depois de spark_jobs. Entrada: seção spark_sql_plan_updates do roadmap e minuta corrigida. Saída: decisão de prioridade. Encerramento: tabela integrada com chave (app_id, execution_id, event_uid) ou rejeitada upstream.

<a id="item-352"></a>

## D06 — Adicionar spark_applications

Frente: dataship_externo. Encaminhamento: externo_dataship_tabela_aplicacoes.

### Identidade e estado

D06 é schema/loader do laboratório: adicionar spark_applications. Minuta local PROP-D06-SPARK-APPLICATIONS. Repositório Gabriel-Philot/dataship-spark-plat-v0; decisão upstream. Owner a confirmar.

### Intenção e benefício

Problema: falta contexto de aplicação (nome, usuário, tempos, versão do Spark) em tabela própria; comparar runs entre versões do Spark fica difícil. Público: quem compara workloads no laboratório. Ganho: contexto de app e versão Spark consultável.

### Feito, faltante e não comprovado

Confirmada ausência de spark_applications no DDL/ensureSchema e leitura de Timestamp em ApplicationStart/End; app_id também é atualizado em readEventLog. O roadmap lista versão Spark como campo, mas esta leitura não demonstra de qual evento vem. Faltam contrato de identidade/tentativa e tratamento de ciclo incompleto.

### Linhagem

Linhagem: roadmap de exploração do upstream (passo 4, tabela spark_applications a partir de ApplicationStart/End) → registro D06 (dependência de D02 apenas de ordem) → minuta PROP-D06, a mais pronta das Dataship → implementação [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-loader.go; fontes/batch-revalidated-wdprops-sources/dataship-ddl.sql; fontes/batch-revalidated-wdprops-sources/dataship-roadmap.md; fontes/batch-proposals-review-sources/PROP-D06-SPARK-APPLICATIONS.md. Locadores: Registro/MATRIX D06; DDL, readEventLog/eventTimeMillis e roadmap spark_applications.

### Classe e limite da evidência

FATO OBSERVADO: evento de aplicação reconhecido no cálculo de timestamp, sem tabela dedicada no DDL. PROPOSTA: tabela spark_applications. Nenhuma execução.

### Fluxo

Fluxo proposto: SparkListenerApplicationStart/End —(app_id, nome, usuário, tempos, versão)→ loader —(uma linha por app)→ spark_applications —(junção por app_id)→ demais tabelas.

### Consequências e risco

A normalização facilita consultar metadados já disponíveis em raw. A extensão parece pequena pelo escopo proposto, mas custo e risco não foram medidos; não se conclui que seja a mais segura.

### Alternativas e recomendação

Comparar uma tabela de aplicações com consulta sobre raw e escolher um contrato mínimo. Pode ser uma primeira extensão se o mantenedor priorizar; isso não demonstra menor risco que todas as demais.

### Dependências e paralelismo

O roadmap do upstream a coloca no passo 4, mas tecnicamente depende só do evento de aplicação e pode vir antes; segurança de mudança depende de D09/D15.

### Plano e aceite propostos

Definir identidade e eventual tentativa, fonte verificável da versão Spark e estado incompleto para ausência de Start/End; planejar DDL e parser com fixtures. Unicidade deve respeitar o contrato de aplicação/tentativa, não apenas uma frase de aceite.

### Comunicação entre responsáveis

Para outro pod: D06 propõe contexto de aplicação consultável no laboratório; identidade, versão e ciclo incompleto ainda precisam ser especificados.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Inventar versão a partir do ambiente de análise ou unir tentativas distintas criaria contexto enganoso. Que caso o teste ainda não cobre? Faltam ApplicationEnd ausente, End antes de Start, reingestão e fonte ausente da versão Spark. Como eu explicaria isso para outro pod? A tabela é proposta de contexto; o roadmap não basta para provar a origem de cada campo.

### Próxima ação e encerramento

Próxima ação: mantenedor upstream (a confirmar) decide se spark_applications pode ser a primeira extensão do loader. Entrada: minuta PROP-D06 e caso de aplicação sem ApplicationEnd. Saída: decisão de publicar. Encerramento: tabela com uma linha por aplicação integrada ou rejeitada upstream.

<a id="item-353"></a>

## D07 — Extrair nós do plano

Frente: dataship_externo. Encaminhamento: externo_dataship_adiar_nos_do_plano.

### Identidade e estado

D07 é um estudo do laboratório: extrair nós do plano físico (sparkPlanInfo). Minuta local PROP-D07-PLAN-NODES-EXTRACTION. Repositório Gabriel-Philot/dataship-spark-plat-v0; decisão upstream. Owner a confirmar.

### Intenção e benefício

Pergunta: quais análises por operador seriam beneficiadas por normalizar sparkPlanInfo em linhas, e qual volume isso acrescentaria. Extrair nós não prova por si só qual operador gastou mais; métricas e vínculo precisam semântica.

### Feito, faltante e não comprovado

Verificação: o roadmap de exploração descreve spark_sql_plan_nodes (app_id, execution_id, event_uid, node_id, parent_node_id, node_name, simple_string, metadata_json, metrics_json) e o passo 5 diz "if operator-level analysis becomes important"; o registro também condiciona ("Só se análise por operador for prioritária"). Falta: decisão de prioridade. Não comprovado: nada.

### Linhagem

Linhagem: roadmap de exploração do upstream (passo 5, nós de sparkPlanInfo "if operator-level analysis becomes important") → registro D07 (depende de D05) → minuta PROP-D07 de estudo de custo → pergunta por operador [ausente] → decisão [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-loader.go; fontes/batch-revalidated-wdprops-sources/dataship-ddl.sql; fontes/batch-revalidated-wdprops-sources/dataship-roadmap.md; fontes/batch-proposals-review-sources/PROP-D07-PLAN-NODES-EXTRACTION.md. Locadores: Registro/MATRIX D07; Roadmap spark_sql_plan_nodes e condição de prioridade; minuta D07.

### Classe e limite da evidência

FATO OBSERVADO: especificação condicional escrita pelo próprio upstream. PROPOSTA: estudo de extração. DECISÃO PENDENTE: prioridade de análise por operador. Nenhuma execução.

### Fluxo

Fluxo proposto: sparkPlanInfo de SQLExecutionStart e de updates adaptativos —(árvore)→ normalização por nó com parent_node_id —(spark_sql_plan_nodes)→ consultas por operador.

### Consequências e risco

Sem tabela de nós, ainda é possível estudar planos no raw; normalizar pode facilitar consultas, com custo de armazenamento ainda não quantificado. Não há incidente ou medida de overhead aqui.

### Alternativas e recomendação

Manter como estudo visível e comparar representações usando amostras estáticas ou sintéticas claramente marcadas. Uma pergunta por operador orienta a prioridade de implementação; não impede analisar a proposta offline.

### Dependências e paralelismo

D05 contribui para o histórico adaptativo; planos iniciais em SQLExecutionStart permitem estudar a extração sem implementá-la. Nenhuma dependência do APEX ou de captura real para o estudo.

### Plano e aceite propostos

Estudo offline permitido: definir perguntas, comparar nós completos e subconjunto, estimar linhas/bytes por plano e registrar limites. Medir tempo exige experimento posterior autorizado; estimativa não é benchmark.

### Comunicação entre responsáveis

Para outro pod: "Extrair cada nó do plano Spark no laboratório só vale se alguém precisar de análise por operador; o próprio autor deixou isso condicional."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Confundir nós estruturais com medidas de custo atribuiria duração ao operador sem prova. Que caso o teste ainda não cobre? Não há medição de volume ou tempo nem cobertura de nós repetidos/reutilizados e versões adaptativas. Como eu explicaria isso para outro pod? D07 é estudo de representação e custo, viável offline e sem obrigação de implementar.

### Próxima ação e encerramento

Próxima ação documental: manter minuta e plano comparativo disponíveis, com critérios e amostras sintéticas/estáticas identificadas. Owner a confirmar; saída futura é nota fundamentada para adotar, adiar ou arquivar.

<a id="item-354"></a>

## D08 — Normalizar métricas de executor

Frente: dataship_externo. Encaminhamento: externo_dataship_adiar_metricas_executor.

### Identidade e estado

D08 é um estudo do laboratório: normalizar métricas de executor. Minuta local PROP-D08-EXECUTOR-METRICS-NORMALIZATION. Repositório Gabriel-Philot/dataship-spark-plat-v0; decisão upstream. Owner a confirmar.

### Intenção e benefício

Problema: métricas de executor (memória, GC, processos) ficam só em eventos brutos; análise de capacidade exige parsing. Público: quem estuda recursos no laboratório. Ganho: análise de capacidade, se ela for prioritária.

### Feito, faltante e não comprovado

Verificação: o roadmap descreve spark_executor_metrics a partir de SparkListenerExecutorMetricsUpdate e SparkListenerStageExecutorMetrics, com app_id, executor_id, stage_id, stage_attempt_id e métricas de processo quando disponíveis; o passo 6 diz "if capacity or resource analysis becomes important". Falta: decisão de prioridade. Não comprovado: nada.

### Linhagem

Linhagem: roadmap de exploração do upstream (passo 6, métricas de executor "if capacity or resource analysis becomes important") → registro D08 (depende de D02) → minuta PROP-D08 sem os eventos-fonte → demanda de capacidade [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-loader.go; fontes/batch-revalidated-wdprops-sources/dataship-ddl.sql; fontes/batch-revalidated-wdprops-sources/dataship-roadmap.md; fontes/batch-proposals-review-sources/PROP-D08-EXECUTOR-METRICS-NORMALIZATION.md. Locadores: Registro/MATRIX D08; Roadmap spark_executor_metrics e condição de prioridade; minuta D08.

### Classe e limite da evidência

FATO OBSERVADO: especificação condicional de spark_executor_metrics no roadmap do upstream. DECISÃO PENDENTE: prioridade de análise de capacidade. Nenhuma execução.

### Fluxo

Fluxo proposto: ExecutorMetricsUpdate e StageExecutorMetrics —(métricas por executor e stage)→ loader —(spark_executor_metrics)→ análise de capacidade e de memória por stage.

### Consequências e risco

A ausência de tabela dedicada torna análises de capacidade dependentes de raw ou fontes complementares; não as torna impossíveis. O custo de normalização é hipótese ainda sem quantificação.

### Alternativas e recomendação

Manter estudo visível: comparar ExecutorMetricsUpdate e StageExecutorMetrics, campos presentes, granularidade, retenção e perdas de agregação. Menor volume do segundo é hipótese a conferir, não medição deste recorte.

### Dependências e paralelismo

A leitura dos eventos e o desenho do estudo não dependem de D02/D09 nem de captura real; essas proteções interessam à eventual mudança no loader. Integração upstream continua decisão própria.

### Plano e aceite propostos

Preparar matriz de eventos/campos e estimativas transparentes com fixtures sintéticas ou amostras estáticas; demanda de capacidade orienta prioridade. Diferenciar ausência de métrica de zero e preservar unidades/granularidade.

### Comunicação entre responsáveis

Para outro pod: "Métricas de executor no laboratório Dataship só valem se houver uma pergunta de capacidade concreta; o próprio autor deixou isso para depois."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Agregar picos ou tratar ausência como zero pode esconder pressão de recurso e atribuir capacidade incorretamente. Que caso o teste ainda não cobre? Não foram medidos volume e perda por agregação, nem conferida disponibilidade de métricas por versão/configuração. Como eu explicaria isso para outro pod? D08 compara formatos e retenção de métricas do laboratório; não é prova de incidente nem gate do APEX.

### Próxima ação e encerramento

Próxima ação documental: manter o estudo e a pergunta de capacidade disponíveis, com proposta de comparação por evento e retenção. Saída futura: nota que justifique modelar, adiar ou arquivar.

<a id="item-355"></a>

## D09 — Testes do loader com fixtures

Frente: dataship_externo. Encaminhamento: externo_candidato_local_testes_ts11.

### Identidade e estado

D09 é um candidato local de testes do loader Go do laboratório (TS11), commit 8ca806a de 27/09 sobre dbbf4cb, base da PR Dataship #2. O registro relata ausência de publicação; nenhuma PR correspondente aparece no snapshot público lido de 18/10. Owner/autoria de submissão a confirmar.

### Intenção e benefício

Na árvore Dataship 8920273 não há arquivo Go de teste; há quatro arquivos Python de teste. O candidato acrescenta caracterização de helpers puros com fixtures sintéticas para apoiar alterações do loader sem Docker. Não protege todo o fluxo de ingestão.

### Feito, faltante e não comprovado

Lido main_test.go integral: oito funções Test cobrem stageFromEvent, taskFromEvent, eventTimeMillis, uintAt, eventUID e appIDFromKey, com JSON sintético decodificado por UseNumber. Há casos de métricas ausentes, falha de task, duração negativa e identidade sensível à origem. Os 11 mutantes e verdes de 30/09 são relatos do registro, sem reprodução nesta revisão. readEventLog, roteamento e E2E não estão cobertos pelo arquivo.

### Linhagem

Linhagem: baseline D09 de 25/09 (clone limpo sem go.sum/vendor falha antes de compilar) → D15/PR #2 (dbbf4cb) → TS11 8ca806a sobre dbbf4cb (27/09) → lane E 30/09 → minuta PROP-D09 → publicação [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-d09-test.go; fontes/batch-revalidated-wdprops-sources/dataship-d09-commit.txt; fontes/batch-revalidated-wdprops-sources/dataship-tree.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018/dataship-pulls.json. Locadores: Registro/MATRIX D09; main_test.go integral, commit 8ca806a, árvore 8920273 e snapshot de PRs.

### Classe e limite da evidência

FATO OBSERVADO: commit local e arquivo com oito funções Test; árvore upstream fixada sem _test.go. RELATO: execução, build/vet, shuffle e 11/11 mutantes. DECISÃO PENDENTE: autoria e caminho de submissão após a política de dependências.

### Fluxo

Fluxo de caracterização: JSON sintético → helpers de extração/tempo/identidade → comparação de structs e valores. O teste não aciona MinIO, ClickHouse, readEventLog ou insertResult. A capacidade offline depende de uma árvore de dependências reproduzível, proposta na #2.

### Consequências e risco

A main fixada não recebe proteção destes testes enquanto o candidato permanecer fora dela. Mesmo integrado, o arquivo protege os helpers caracterizados; não garante ingestão, roteamento ou semântica correta de toda métrica. Caracterizar zero em métrica ausente registra o comportamento atual, sem provar que ausência e zero sejam semanticamente equivalentes.

### Alternativas e recomendação

Preservar o candidato como unidade de um arquivo e a rota histórica de submissão após #2, com autoria e base reconfirmadas. Revisar o teste e preparar futuras folhas de roteamento é possível agora. Uma PR empilhada é alternativa de integração, a decidir separadamente.

### Dependências e paralelismo

D15 provê uma solução de dependências para compilar offline em clone limpo; outra política reproduzível também pode atendê-la. A implementação de D02 precisa uma proteção definida, mas seu estudo não espera o merge da #2. A revisão documental do candidato independe de runtime.

### Plano e aceite propostos

Próximo trabalho futuro: reconfirmar base e autoria, integrar o candidato por rota escolhida e repetir validações adequadas; manter readEventLog/roteamento e E2E como escopos distintos. Nesta rodada apenas a revisão do arquivo foi concluída.

### Comunicação entre responsáveis

Para outro pod: existe um candidato local de oito testes dos helpers puros. Os verdes e mutantes são evidência histórica; a integração e a cobertura do fluxo completo ainda são pendências.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Tratar caracterização de helpers como cobertura de ingestão esconderia falhas de roteamento e persistência. Que caso o teste ainda não cobre? O arquivo não cobre readEventLog, insertResult, objetos reingeridos nem E2E MinIO/ClickHouse; os mutantes não foram executados aqui. Como eu explicaria isso para outro pod? D09 é proteção parcial candidata, condicionada a dependências reproduzíveis para execução e ainda sem integração demonstrada.

### Próxima ação e encerramento

Próxima ação documental: manter o candidato, seus limites e a rota após #2 visíveis. Responsável de eventual submissão a confirmar. Encerramento futuro: integração revalidada ou descarte motivado; nenhum push nesta revisão.

<a id="item-356"></a>

## D15 — Reproduzir dependências do módulo Go do loader

Frente: dataship_externo. Encaminhamento: externo_pr2_aberta_aguarda_upstream.

### Identidade e estado

D15 é reprodutibilidade/testes do laboratório: reproduzir as dependências do módulo Go do loader. Publicado como Gabriel-Philot/dataship-spark-plat-v0#2 "build(eventlog-loader): version dependencies for offline builds", aberta em 2026-09-27T12:44:50Z por gustocezar, head dbbf4cb, base main; aberta e sem merge no GET de 18/10. Owner: mantenedor upstream (decisão de política de dependências).

### Intenção e benefício

No snapshot 8920273, a árvore contém go.mod, sem go.sum ou vendor; o corpo da PR #2 explica que o Dockerfile usa -mod=vendor e que bootstrap gera as dependências com rede. O problema é reproduzir build/teste em clone limpo sem cache/rede. A falha anterior é relato histórico, não reprodução atual.

### Feito, faltante e não comprovado

A captura de 18/10 mostra #2 aberta, head dbbf4cb. O diffstat local registra 1.426 arquivos alterados, 783.823 inserções e duas deleções; não significa 1.426 arquivos novos. O corpo relata go mod verify, regeneração idêntica, test/vet/build e docker build offline; isso é evidência declarada pelo autor, sem execução independente nesta rodada.

### Linhagem

Linhagem: baseline D09 de 25/09 (falha sem go.sum e com -mod=vendor) → PR #2 (27/09, dbbf4cb) → candidato D09 empilhado (8ca806a) → decisão upstream [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-tree.txt; fontes/batch-revalidated-wdprops-sources/dataship-d15-diffstat.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018/dataship-pulls.json. Locadores: Registro/MATRIX D15; árvore base, diffstat e corpo da PR #2/dbbf4cb.

### Classe e limite da evidência

FATO OBSERVADO: PR aberta no snapshot, ausência de go.sum/vendor na árvore base e tamanho do diff. RELATO: falha baseline e validações offline descritas no corpo. DECISÃO PENDENTE: política de dependências do mantenedor.

### Fluxo

Fluxo proposto: clone limpo —(go.sum e vendor/ versionados)→ go build/test -mod=vendor sem rede —(Dockerfile)→ imagem do loader. Antes: clone limpo —(make bootstrap com rede)→ vendor gerado localmente.

### Consequências e risco

Sem uma solução reproduzível, a base lida exige preparação externa de dependências para compilar offline. go.sum sozinho verifica conteúdo, mas não fornece módulos a um ambiente sem rede e sem cache. O tamanho do vendor aumenta a superfície a revisar; não é medição de dificuldade ou risco.

### Alternativas e recomendação

Recomendado: deixar ao mantenedor escolher entre vendor versionado (a PR) e só go.sum com proxy/cache (diff mínimo, exige rede ou cache). Alternativa: separar go.sum (pequeno) de vendor/ (grande) em dois commits para facilitar a revisão. Reversível.

### Dependências e paralelismo

Não depende do APEX. D09 pode usar a #2 ou outra política que forneça dependências reproduzíveis; a revisão do seu arquivo e os estudos de D02–D08 podem continuar. P10 é independente. Ausência de CI é relato do registro, não requisito para decidir a política.

### Plano e aceite propostos

Para eventual adoção: escolher política, conferir manifesto e proveniência das dependências e verificar regeneração/compilação em clone limpo com condições registradas. Revisar somente go.mod/go.sum não substitui conferir a integridade da árvore gerada. Nenhuma validação foi executada aqui.

### Comunicação entre responsáveis

Para outro pod: "A PR #2 do Dataship versiona as dependências Go para o loader compilar sem rede; é grande por causa do vendor/ e aguarda decisão do mantenedor."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Escolher apenas go.sum sem disponibilizar módulos não resolveria um clone sem rede nem cache. Que caso o teste ainda não cobre? Não reproduzimos os checks offline do head publicado, nem auditamos conteúdo e proveniência do vendor. Como eu explicaria isso para outro pod? D15 é a decisão de dependências reproduzíveis do laboratório; #2 é uma solução proposta e aberta no snapshot.

### Próxima ação e encerramento

Próxima ação: mantenedor upstream (a confirmar) decide a política. Entrada: PR #2 aberta. Saída: merge, revisão pedida ou fechamento com motivo. Encerramento: decisão upstream registrada.

<a id="item-357"></a>

## D10 — Catálogo de workloads

Frente: dataship_externo. Encaminhamento: externo_dataship_adiar_catalogo_workloads.

### Identidade e estado

D10 é uma feature do laboratório: catálogo de workloads (convenções de nome de app e caminhos). Minuta local PROP-D10-WORKLOAD-CATALOG. Repositório Gabriel-Philot/dataship-spark-plat-v0; decisão upstream. Owner a confirmar.

### Intenção e benefício

Pergunta proposta pela minuta: quais convenções de app, caminhos e parâmetros facilitariam identificar workloads comparáveis. O registro não descreve um incidente nem exemplo de confusão; benefício permanece hipótese organizacional do laboratório.

### Feito, faltante e não comprovado

O registro D10 contém problem/proof vazios e recomendação histórica defer. A árvore 8920273 não identifica um arquivo de catálogo pelo nome; seu conteúdo inteiro não foi auditado. Há scripts de exemplo e src/apps/template.md, portanto não se afirma ausência universal de convenções. A minuta fornece uma proposta, ainda sem caso concreto demonstrado.

### Linhagem

Linhagem: seed D10 → registro D10 (study_ready, rec defer, sem problema descrito) → minuta PROP-D10 → decisão [ausente]. Elo ausente: descrição do problema no próprio registro.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-tree.txt; fontes/batch-revalidated-wdprops-sources/dataship-ddl.sql; fontes/batch-revalidated-wdprops-sources/dataship-roadmap.md; fontes/batch-revalidated-wdprops-sources/dataship-current-tables.md; fontes/batch-proposals-review-sources/PROP-D10-WORKLOAD-CATALOG.md. Locadores: Registro/MATRIX D10; Árvore 8920273 e minuta D10; campos vazios do registro.

### Classe e limite da evidência

FATO OBSERVADO: registro pouco especificado, nomes de arquivos na árvore e conteúdo da minuta. INFERÊNCIA: um catálogo poderia facilitar identificação. Não foi demonstrada perda atual por falta dele.

### Fluxo

Fluxo possível: workloads existentes → convenção e exemplos de nome/caminho/parâmetros → catálogo → identificação de runs. O vínculo a tabelas novas é opcional; catálogo documental não depende de spark_applications.

### Consequências e risco

O ganho potencial é reduzir ambiguidades e anotações dispersas; não se comprovou que todas as comparações dependam de memória. Impacto proposto é do laboratório; prioridade não foi definida nesta revisão.

### Alternativas e recomendação

Manter o estudo disponível: levantar convenções já existentes e comparar uma taxonomia curta com o uso atual. O adiamento do registro é histórico; um exemplo de confusão ajuda priorizar adoção, sem impedir estudo offline.

### Dependências e paralelismo

Não depende de outros itens D nem do APEX. D11 (metadados de experimento) é complementar e pode compartilhar a mesma convenção de nomes e caminhos.

### Plano e aceite propostos

Trabalho documental possível agora: inventário de nomes/caminhos atuais e um esboço de convenção com exemplos identificados. Antes de adotar, explicitar a pergunta atendida e validar a utilidade com o responsável.

### Comunicação entre responsáveis

Para outro pod: D10 é proposta de organização de workloads com problema histórico pouco descrito; pode ser estudada por documentos existentes sem alterar o laboratório.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Uma taxonomia que ignore convenções existentes duplicaria nomes e poderia dificultar a identificação. Que caso o teste ainda não cobre? Não foi auditado todo o conteúdo de templates/docs nem demonstrada confusão em um par de runs. Como eu explicaria isso para outro pod? D10 é estudo de convenção e catálogo; falta evidência de utilidade para decidir adoção, mas ele segue disponível offline.

### Próxima ação e encerramento

Próxima ação documental: preservar a minuta e a lacuna de especificação, com plano de inventário e comparação. Adoção/publicação e responsável a definir posteriormente; o estudo não espera dor operacional.

<a id="item-358"></a>

## D11 — Metadados de experimento

Frente: dataship_externo. Encaminhamento: externo_dataship_adiar_metadados_experimento.

### Identidade e estado

D11 é schema do laboratório: metadados de experimento para rastreabilidade de runs. Minuta local PROP-D11-EXPERIMENT-METADATA. Repositório Gabriel-Philot/dataship-spark-plat-v0; decisão upstream. Owner a confirmar.

### Intenção e benefício

A minuta pergunta como registrar ambiente, hardware, versões e parâmetros por run para apoiar comparação. O registro só declara Runs comparáveis; ausência de metadados padronizados não torna toda comparação impossível e não garante reprodução por si só.

### Feito, faltante e não comprovado

O DDL de seis tabelas não tem entidade de experimento; isso não prova ausência de anotações ou templates em todo o repositório. O registro liga D11 a D02 e adia; a minuta propõe template documental. Faltam campos, identidade do run, referências de artefatos e critérios que permitam explicar diferenças.

### Linhagem

Linhagem: seed D11 → registro D11 (study_ready, depende de D02, rec defer, problema não descrito) → minuta PROP-D11 → decisão [ausente]. Elo ausente: descrição do problema no registro.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-tree.txt; fontes/batch-revalidated-wdprops-sources/dataship-ddl.sql; fontes/batch-revalidated-wdprops-sources/dataship-roadmap.md; fontes/batch-revalidated-wdprops-sources/dataship-current-tables.md; fontes/batch-proposals-review-sources/PROP-D11-EXPERIMENT-METADATA.md. Locadores: Registro/MATRIX D11; DDL de seis tabelas e minuta D11.

### Classe e limite da evidência

FATO OBSERVADO: DDL sem tabela de experimento e minuta de template. INFERÊNCIA: um template não precisa alterar o loader. O caso de comparação e a efetividade do padrão não foram demonstrados.

### Fluxo

Fluxo proposto: run identificado → metadados com hipótese, alteração, ambiente/versões e artefatos → comparação de duas execuções. Registro completo apoia rastreabilidade; não transforma diferenças de ambiente em equivalência automaticamente.

### Consequências e risco

Sem padrão comum pode ser mais difícil localizar contexto, mas não foi provado que toda comparação atual dependa de memória. O custo de arquivo versus tabela não foi medido.

### Alternativas e recomendação

Manter estudo disponível e comparar arquivo/template com tabela, começando por campos mínimos e um exemplo estático ou sintético identificado. O adiamento histórico e a maturidade do pipeline não impedem desenhar o template offline.

### Dependências e paralelismo

Na forma de template, não depende de D02 nem do pipeline pronto. É complementar a D10; qualquer ligação com DD01 é apenas inspiração a justificar, não dependência.

### Plano e aceite propostos

Preparar esboço com identidade do run, hipótese, variável, versão/configuração, origem dos dados e artefatos. Duas baterias da minuta são proposta de avaliação futura, não prova já obtida nem critério suficiente sem dizer o que comparar.

### Comunicação entre responsáveis

Para outro pod: D11 propõe contexto rastreável de experimento; pode começar como documento e não espera a refatoração do loader.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Misturar tentativas ou deixar versão/configuração sem fonte produziria comparação enganosa. Que caso o teste ainda não cobre? Não há demonstração de reprodução ou comparação de duas baterias; faltam critérios de identidade, completude e diferenças permitidas. Como eu explicaria isso para outro pod? D11 registra contexto de runs e pode ser desenhado offline, independente da implementação do loader.

### Próxima ação e encerramento

Próxima ação documental: manter minuta e comparação de formatos disponíveis. Nenhuma execução de baterias nesta revisão. Eventual adoção exige responsável, exemplos e critérios de completude definidos.

<a id="item-359"></a>

## D12 — Query pack operacional

Frente: dataship_externo. Encaminhamento: externo_dataship_adiar_query_pack.

### Identidade e estado

D12 é documentação do laboratório: um query pack operacional sobre as seis tabelas. Minuta local PROP-D12-OPERATIONAL-QUERY-PACK. Repositório Gabriel-Philot/dataship-spark-plat-v0; decisão upstream. Owner a confirmar.

### Intenção e benefício

Problema (impacto registrado "Consultas exemplares"): quem chega ao laboratório precisa de consultas prontas para responder as perguntas que as tabelas já suportam. Público: novos usuários do laboratório. Ganho: começar a explorar sem escrever SQL do zero.

### Feito, faltante e não comprovado

Lidos integralmente exploration-roadmap.md e current-tables.md: o primeiro lista oito perguntas úteis; o segundo descreve colunas/semântica das seis tabelas e não contém consultas SQL. A árvore tem outros documentos não auditados; não se conclui ausência de exemplos em todo o repositório. A minuta propõe queries.sql, ainda sem consulta ou eficiência demonstradas.

### Linhagem

Perguntas do roadmap upstream → registro D12 study_ready/defer → minuta de query pack → revalidação da documentação específica → pacote não demonstrado neste recorte. O adiamento é histórico, sem gate ao estudo.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-tree.txt; fontes/batch-revalidated-wdprops-sources/dataship-ddl.sql; fontes/batch-revalidated-wdprops-sources/dataship-roadmap.md; fontes/batch-revalidated-wdprops-sources/dataship-current-tables.md; fontes/batch-proposals-review-sources/PROP-D12-OPERATIONAL-QUERY-PACK.md. Locadores: Registro/MATRIX D12; Roadmap, current-tables.md e DDL integrais; minuta D12.

### Classe e limite da evidência

FATO OBSERVADO: oito perguntas, seis tabelas e descrição sem SQL em current-tables.md. PROPOSTA: consultas comentadas. Não foi feita execução ou busca exaustiva de exemplos em todo o projeto.

### Fluxo

Fluxo proposto: pergunta do roadmap —(consulta SQL documentada)→ ClickHouse do laboratório —(resultado)→ usuário. Uma consulta por pergunta listada.

### Consequências e risco

Um pacote pode facilitar exploração e reduzir trabalho repetido; esse ganho não foi medido. O conteúdo precisa respeitar limites das projeções atuais, por exemplo plano SQL inicial não é plano por task.

### Alternativas e recomendação

Manter estudo disponível e usar as oito perguntas como índice, verificando antes outros exemplos relevantes. Trocar plano eficiente por critérios definidos de semântica, resultado esperado e, apenas se necessário, custo mensurável.

### Dependências e paralelismo

O desenho do pacote usa o DDL atual e não depende de D02–D08 nem de captura real. Execução futura de consultas exige um ambiente/fixture identificado e escopo próprio.

### Plano e aceite propostos

Trabalho documental possível: mapear pergunta → tabelas/colunas → consulta proposta → resultado esperado em fixture sintética identificada. Verificar chaves de aplicação, tentativas e unidades. A executabilidade e o desempenho só serão demonstrados por validação futura autorizada.

### Comunicação entre responsáveis

Para outro pod: current-tables.md descreve schema, sem SQL; o roadmap dá oito perguntas para um pacote possível, ainda sem prova de execução.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Juntar por execution_id ou stage_id sem app/tentativa pode misturar execuções e gerar diagnóstico falso. Que caso o teste ainda não cobre? Não foram verificadas execução SQL, resultados esperados ou eficiência; outros documentos podem conter exemplos. Como eu explicaria isso para outro pod? D12 transforma perguntas do roadmap em propostas de consulta sobre tabelas existentes, sem exigir tabelas novas.

### Próxima ação e encerramento

Próxima ação documental: preservar minuta com índice por pergunta e limites do DDL. Eventual publicação e validação executável ficam para uma unidade com responsável definido.

<a id="item-360"></a>

## D13 — Equivalência Spark Connect

Frente: dataship_externo. Encaminhamento: externo_dataship_adiar_spark_connect.

### Identidade e estado

D13 é um estudo do laboratório: equivalência de telemetria entre Spark Connect e spark-submit. Minuta local PROP-D13-SPARK-CONNECT-EQUIVALENCE. Repositório Gabriel-Philot/dataship-spark-plat-v0; decisão upstream. Owner a confirmar.

### Intenção e benefício

Pergunta de estudo: quais eventos, campos, identidades e propriedades diferem entre o modo primário spark-submit e Spark Connect para o mesmo workload. As diferenças são hipóteses a comparar; não foi demonstrado que o loader esteja incorreto em Connect.

### Feito, faltante e não comprovado

O registro diz spark-submit segue primário e recomenda adiar; isso não comprova ausência de uso ou de ambiente Connect. A minuta define estudo conceitual sem implementar suporte. A árvore inclui material histórico cujo nome cita Connect; não foi avaliado como prova de paridade.

### Linhagem

Seed D13 → registro de prioridade primária spark-submit → minuta de paridade → protocolo/estudo ainda não demonstrado neste recorte. Adiamento declarado não bloqueia leitura e desenho offline.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-tree.txt; fontes/batch-revalidated-wdprops-sources/dataship-ddl.sql; fontes/batch-revalidated-wdprops-sources/dataship-roadmap.md; fontes/batch-revalidated-wdprops-sources/dataship-current-tables.md; fontes/batch-proposals-review-sources/PROP-D13-SPARK-CONNECT-EQUIVALENCE.md; fontes/batch-revalidated-wdprops-sources/dataship-compatibility.md. Locadores: Registro/MATRIX D13; Registro D13, árvore, notas de compatibilidade e minuta.

### Classe e limite da evidência

FATO OBSERVADO: pergunta e adiamento no registro/minuta. HIPÓTESE: possíveis diferenças de eventos e identidade. Não há evidência lida suficiente para declarar ambiente inexistente, nenhum usuário ou suporte/ausência de suporte.

### Fluxo

Fluxo proposto: mesmo workload —(spark-submit)→ event log A; —(Spark Connect)→ event log B —(loader)→ tabelas —(comparação por tipo de evento e campos)→ relatório de paridade.

### Consequências e risco

Sem estudo, a paridade permanece desconhecida. O risco de dados incompletos é condicional à diferença real e à adoção; não foi identificado incidente ou comprovada urgência.

### Alternativas e recomendação

Manter estudo disponível: preparar matriz de eventos/campos por modo e protocolo de comparação, com versões e identidades definidas. Amostras sintéticas/estáticas ajudam o desenho, sem serem prova de paridade real. Prioridade de execução é decisão separada.

### Dependências e paralelismo

Leitura e desenho offline não dependem de outros D nem de ambiente Connect. Uma comparação executada exige os dois modos configurados e autorização de execução; a existência atual desse ambiente não foi verificada.

### Plano e aceite propostos

Preparar perguntas e resultados esperados por modo, incluindo sessão/app/job/SQL, eventos ausentes e configurações. Experimento real posterior deve controlar versões, workload e origem, sem confundir diferença de configuração com diferença do modo.

### Comunicação entre responsáveis

Para outro pod: D13 compara telemetria entre modos; spark-submit primário é prioridade histórica e não prova que Connect seja inexistente ou incompatível.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Assumir paridade ou incompatibilidade a partir de nomes e ausência de prova levaria a suporte declarado sem base. Que caso o teste ainda não cobre? Não há comparação executada dos modos, nem cobertura demonstrada de sessão, identidade e propriedades SQL. Como eu explicaria isso para outro pod? D13 é pergunta de equivalência que pode ser preparada offline; ainda não há resultado de paridade neste recorte.

### Próxima ação e encerramento

Próxima ação documental: preservar minuta com plano comparativo offline e incertezas. Execução e eventual adoção ficam para escopo posterior, com responsável e condições definidos.

