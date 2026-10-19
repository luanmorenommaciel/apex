# Fichas documentais — lote 37

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-361"></a>

## D14 — Branches experimentais do upstream (listener/observer)

Frente: dataship_externo. Encaminhamento: externo_dataship_estudar_branches_experimentais.

### Identidade e estado

D14 é um estudo do laboratório: avaliar branches experimentais do upstream (listener/observer). Minuta local PROP-D14-UPSTREAM-BRANCHES-EVALUATION. Repositório Gabriel-Philot/dataship-spark-plat-v0. Owner a confirmar.

### Intenção e benefício

O registro propõe comparar duas branches de captura com o JAR APEX para identificar sobreposição ou técnicas possíveis. A ausência de comparação é estado do registro e deste recorte, não prova de que nunca tenha ocorrido em qualquer lugar.

### Feito, faltante e não comprovado

Os recortes fixados mostram a2c8b57 com um commit/10 arquivos e 4ae68e2 com 20 commits/266 arquivos de diferença. A lista inclui listener firehose na primeira e runtime/plugin/API/bridge Spark 4.1.2 na segunda, além de documentação e evidências. Contagem de arquivos não mede utilidade; conteúdo técnico comparativo ainda não foi lido neste item.

### Linhagem

Linhagem: branches experimentais de julho → descoberta da auditoria de setembro → registro D14 (state unknown, rec study) → minuta PROP-D14 → leitura dirigida [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-tree.txt; fontes/batch-revalidated-wdprops-sources/dataship-ddl.sql; fontes/batch-revalidated-wdprops-sources/dataship-roadmap.md; fontes/batch-revalidated-wdprops-sources/dataship-current-tables.md; fontes/batch-proposals-review-sources/PROP-D14-UPSTREAM-BRANCHES-EVALUATION.md; fontes/batch-revalidated-wdprops-sources/dataship-branch-a2c8b57.txt; fontes/batch-revalidated-wdprops-sources/dataship-branch-4ae68e2.txt. Locadores: Registro/MATRIX D14; Recortes a2c8b57 e 4ae68e2 e minuta D14.

### Classe e limite da evidência

FATO OBSERVADO: SHAs, contagens e nomes dos arquivos nos recortes. PROPOSTA: leitura dirigida comparativa. Maior extensão não demonstra maior utilidade, correção, compatibilidade ou segurança.

### Fluxo

Fluxo proposto: branch experimental —(listener/observer, campos capturados)→ leitura dirigida —(comparação)→ jar/ do APEX (StageListener e campos do contrato) —(lacunas e técnicas reaproveitáveis)→ nota para o Pod do JAR.

### Consequências e risco

Pode haver ganho por reconhecer técnicas existentes; isso é benefício potencial. Não se demonstrou campo faltante no APEX, desempenho, compatibilidade binária ou efeito sobre v1.

### Alternativas e recomendação

Manter estudo disponível e comparar as duas branches por perguntas: fonte dos eventos, identidade, cobertura, ciclo de vida, fila/backpressure e dependência de APIs internas. Evitar escolher só pela contagem de commits ou fixar duração sem conhecer o conteúdo.

### Dependências e paralelismo

Não depende de nada; é estudo de leitura de branches públicas do upstream. Pode interessar ao Pod do JAR do APEX, sem criar gate para a v1 nem para outros itens D.

### Plano e aceite propostos

Leitura futura: fixar fontes por SHA nas duas branches e APEX, montar matriz de captura/contrato e distinguir ideia reutilizável de código portável. Registrar riscos e perguntas sem assumir licença ou compatibilidade. Aceite documental futuro: nota com fontes e limites por afirmação.

### Comunicação entre responsáveis

Para outro pod: "O laboratório tem duas branches experimentais de captura de julho, uma com 20 commits; vale uma leitura comparada com o JAR do APEX antes de inventar captura nova."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Portar um listener ou bridge de versão sem examinar ciclo de vida e contrato poderia criar incompatibilidade ou perda de dados. Que caso o teste ainda não cobre? Nomes e contagens não cobrem comportamento, overhead, versão, licença ou comparação real com o JAR. Como eu explicaria isso para outro pod? D14 é estudo de código fixado por SHA; seu resultado pode recomendar reaproveitar uma ideia sem adotar a branch.

### Próxima ação e encerramento

Próxima ação: Pod do JAR ou autor (a confirmar) faz a leitura dirigida quando houver capacidade. Entrada: clone local do upstream. Saída: nota comparativa. Encerramento: nota registrada ou decisão de não estudar.

<a id="item-362"></a>

## PROP-X13-CONTRACT-RECONCILIATION — [Docs][Contract] Reconciliar texto do CONTRACT.md e marcadores PROPOSED de schema SQL (DEC-14)

Frente: minutas_publicadas. Encaminhamento: minuta_publicada_165_premissa_corrigida_na_publicacao.

### Identidade e estado

PROP-X13-CONTRACT-RECONCILIATION é a minuta local de 11/10/2026, preservada para linhagem. PUBLICATION.json registra sua publicação/reformulação como luanmorenommaciel/apex#165 em 2026-10-11T04:23:54Z. A issue estava aberta no snapshot de 16/10; esse estado é datado. Responsável de implementação não é atribuído por esta revisão.

### Intenção e benefício

Intenção da minuta: reconciliar texto normativo do CONTRACT.md com a convenção v0.6 e remover ou ajustar marcadores PROPOSED legados em cabeçalhos SQL, para que colaboradores novos não leiam definições contraditórias. Público: quem lê contrato e DDL. Ganho declarado: coerência descritiva sem mudar semântica de telemetria.

### Feito, faltante e não comprovado

A minuta usa referência histórica de linha e simplifica a diferença entre stage linkage futuro e execution_id opcional em apex.stage v0.6. O contrato distingue emissão de job_conf no primeiro onJobStart (linha 30) e vínculo transition→stage como evolução (128). A #165 publicada corrige o foco e proíbe remover PROPOSED automaticamente. Os testes de matriz fixam PROPOSED v0.4 e PROPOSED, not ratified nos três cabeçalhos; tais asserções precisam ser consideradas, sem transformar o teste em prova de ratificação.

### Linhagem

X13/DEC-14 histórico → minuta original → publicação #165 com redação reformulada → comparação documental desta ficha. Comentário de estudo e ausência de PR/decisão são relatos anteriores não revalidados aqui.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/PROP-X13-CONTRACT-RECONCILIATION.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/CONTRACT.md.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/contract__job_conf.ddl.sql.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/memory__sql__030_plan_memory.sql.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/memory__sql__031_run_outcomes.sql.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/tests__test_telemetry_compatibility_matrix.py.txt. Locadores: Minuta integral, PUBLICATION #165, snapshot e recortes CONTRACT/DDL/guarda 145–147.

### Classe e limite da evidência

FATO OBSERVADO: diferenças entre minuta/publicação, cláusulas 11–14/30/128 do contrato, cabeçalhos e asserções 145–147. DECISÃO EM ABERTO no recorte: conteúdo normativo e fonte de ratificação. Nenhuma execução de teste.

### Fluxo

Fluxo da minuta: registro histórico DEC-14 —(redação)→ revisão do mantenedor —(aprovação)→ texto normativo; fluxo corrigido pela publicação: inventário de trechos com ref exata —(separar histórico, vigente e aberto)→ revisão do mantenedor —(PR documental separada)→ texto; faltando, no fluxo, a guarda literal —(asserções)→ teste da matriz.

### Consequências e risco

Se alguém executasse a minuta original ao pé da letra, poderia remover PROPOSED e quebrar a guarda literal, ou "corrigir" a cláusula errada; a publicação reduziu esse risco. Confiança alta na comparação textual.

### Alternativas e recomendação

Usar #165 como representação pública e conservar a minuta como origem. Um futuro inventário deve incluir cabeçalhos e guarda literal; qualquer atualização coordenada de texto/teste precisa justificativa da fonte normativa. Manter marcadores com explicação é alternativa válida.

### Dependências e paralelismo

Inventário e comparação offline podem começar sem decisão. Alterar texto normativo exige definição do mantenedor; isso é diferente de bloquear estudo. Coordenar escopos com #179 se tocar a matriz; #115 trata atribuição, sem decidir estes cabeçalhos.

### Plano e aceite propostos

Registrar a evolução minuta → #165 e incluir o teste literal no inventário de impacto. Não republicar a minuta como trabalho novo. Nenhuma remoção de marcador, ratificação ou alteração de teste nesta revisão.

### Comunicação entre responsáveis

Para outro pod: #165 reformulou a minuta; o contrato tem cláusulas distintas e os marcadores PROPOSED são também checados por teste. Um futuro ajuste deve ser normativamente justificado, sem apagar a história.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Remover marcadores automaticamente poderia quebrar a guarda e declarar ratificação sem evidência; corrigir a cláusula errada confundiria job_conf com stage linkage. Que caso o teste ainda não cobre? Não foi executado o teste da matriz nem revalidada integração/runtime; a fonte de ratificação ainda precisa ser identificada. Como eu explicaria isso para outro pod? A minuta é origem histórica; #165 é representação pública reformulada e a alteração normativa é uma decisão distinta do inventário.

### Próxima ação e encerramento

Próxima ação documental concluída: registrar a origem e as ressalvas desta ficha sob #165. Estudo futuro: inventário por trecho com fonte normativa e impacto em testes; owner a confirmar.

<a id="item-363"></a>

## PROP-D05-AQE-UPDATES — [Feature][Dataship] Normalização de eventos adaptativos de execução AQE (D05)

Frente: minutas_dataship. Encaminhamento: minuta_externa_nao_publicada_alinhar_ao_roadmap_upstream.

### Identidade e estado

PROP-D05-AQE-UPDATES é uma minuta local de 2026-10-11 para o repositório externo Gabriel-Philot/dataship-spark-plat-v0 (feature, laboratório, executor G-gemini, readiness draft_owner_review, publicação não autorizada naquela rodada), origem D05: "Normalização de eventos adaptativos de execução AQE". Não foi publicada; decisão do mantenedor upstream.

### Intenção e benefício

Intenção: tirar os updates adaptativos de plano do bruto spark_raw_events e estruturá-los em tabela tipada, para diagnosticar mudanças de plano em runtime. Público: quem estuda AQE no laboratório. Ganho declarado: "Estrutura nós e métricas adaptativas em colunas tipadas".

### Feito, faltante e não comprovado

Avaliação: a premissa confere com a base upstream (nenhuma tabela adaptativa no DDL da main). Pontos fracos: o benefício fala em "nós e métricas adaptativas", que é escopo de D07 (nós do plano), enquanto a fronteira diz D07 fora — contradição interna; o critério "parsing estruturado sem perda de atributos essenciais do plano adaptado" não define chave nem deduplicação. O roadmap do próprio upstream especifica spark_sql_plan_updates com (app_id, execution_id, event_uid, physical_plan, spark_plan_info_json, event_time_ms), mais concreto que a minuta.

### Linhagem

Linhagem: exploration-roadmap.md do upstream (passo 3) → registro D05 → minuta Gemini de 11/10 → revisão documental da triagem → publicação [não autorizada] → decisão upstream [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-loader.go; fontes/batch-revalidated-wdprops-sources/dataship-ddl.sql; fontes/batch-revalidated-wdprops-sources/dataship-roadmap.md; fontes/batch-proposals-review-sources/PROP-D05-AQE-UPDATES.md. Locadores: MATRIX proposals[PROP-D05-AQE-UPDATES]; minuta integral; DDL/ensureSchema, readEventLog/eventUID, roadmap spark_sql_plan_updates.

### Classe e limite da evidência

FATO OBSERVADO: premissa confirmada; contradição interna entre benefício e fronteira; especificação upstream mais precisa. PROPOSTA: a própria minuta. Nenhuma execução.

### Fluxo

Fluxo proposto pela minuta: spark_raw_events —(decodificação de eventos AQE)→ tabela específica. Fluxo do upstream: SparkListenerSQLAdaptiveExecutionUpdate —(chave app_id+execution_id+event_uid)→ spark_sql_plan_updates.

### Consequências e risco

Se usada como está, a minuta poderia levar a uma tabela sem chave de update, colapsando replanejamentos. Impacto só no laboratório. Confiança alta.

### Alternativas e recomendação

Corrigir o benefício para histórico de updates, retirando extração de nós D07; definir campos, chave e ordem sem pressupor timestamp sempre disponível.

### Dependências e paralelismo

Nenhuma dependência para revisão e estudo offline. Ordem sugerida, proteções de implementação e decisão de adoção upstream permanecem separadas.

### Plano e aceite propostos

Preparar offline o contrato de identidade, ordem e duplicação; separar planos adaptativos de extração de nós. Nenhuma publicação ou execução nesta revisão.

### Comunicação entre responsáveis

Para outro pod: "A minuta D05 do Dataship confunde planos adaptativos com nós do plano; o roadmap do próprio autor já especifica a tabela de forma mais precisa."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Colapsar por execution_id apagaria replanejamentos; assumir tempo sempre presente ordenaria incorretamente casos sem timestamp. Que caso o teste ainda não cobre? Faltam updates repetidos, timestamps ausentes/empatados e dois updates distintos da mesma execução. Como eu explicaria isso para outro pod? D05 guarda o histórico adaptativo do laboratório; D07 extrai nós e é outro escopo.

### Próxima ação e encerramento

Próxima ação documental: preservar esta minuta visível com as correções desta ficha para análise e comparação. A decisão posterior de implementar ou publicar exige escopo e responsável definidos; não exige captura real para estudar.

<a id="item-364"></a>

## PROP-D06-SPARK-APPLICATIONS — [Feature][Dataship] Tabela de metadados de ciclo de vida spark_applications (D06)

Frente: minutas_dataship. Encaminhamento: minuta_externa_estudar_identidade_e_ciclo_de_vida.

### Identidade e estado

PROP-D06-SPARK-APPLICATIONS é uma minuta local de 2026-10-11 para Gabriel-Philot/dataship-spark-plat-v0 (feature, laboratório, executor G-gemini, publicação não autorizada), origem D06: "Tabela de metadados de ciclo de vida spark_applications". Não publicada; decisão upstream.

### Intenção e benefício

Intenção: tabela própria com metadados globais da aplicação (versão Spark, app_id, usuário, início e término) para agrupar e analisar aplicações. Público: quem compara workloads no laboratório. Ganho: contexto de alto nível por aplicação.

### Feito, faltante e não comprovado

A tabela está ausente do DDL. O critério de registro único precisa definir identidade/tentativa, eventos incompletos e origem da versão Spark; a leitura de Start/End no loader só demonstra reconhecimento de timestamp. D02 é ordem de implementação, não bloqueio ao estudo.

### Linhagem

Linhagem: exploration-roadmap.md do upstream (passo 4) → registro D06 → minuta Gemini de 11/10 → publicação [não autorizada] → decisão upstream [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-loader.go; fontes/batch-revalidated-wdprops-sources/dataship-ddl.sql; fontes/batch-revalidated-wdprops-sources/dataship-roadmap.md; fontes/batch-proposals-review-sources/PROP-D06-SPARK-APPLICATIONS.md. Locadores: MATRIX proposals[PROP-D06-SPARK-APPLICATIONS]; minuta integral; DDL, readEventLog/eventTimeMillis e roadmap spark_applications.

### Classe e limite da evidência

FATO OBSERVADO: premissa confirmada no DDL da main upstream e critério verificável por application_id. INFERÊNCIA: a dependência de D02 é de ordem preferida, não técnica. Nenhuma execução.

### Fluxo

Fluxo proposto: SparkListenerApplicationStart/End —(app_id, nome, usuário, tempos, versão)→ loader —(uma linha por app)→ spark_applications.

### Consequências e risco

A minuta tem fronteira pequena, mas afirmar que é segura ou a de menor risco excede a leitura; riscos de identidade e eventos incompletos precisam contrato.

### Alternativas e recomendação

Revisar identidade, origem da versão e lifecycle incompleto antes de propor implementação. Pode ser comparada com consultas sobre raw sem esperar D02.

### Dependências e paralelismo

Nenhuma dependência para revisão e estudo offline. Ordem sugerida, proteções de implementação e decisão de adoção upstream permanecem separadas.

### Plano e aceite propostos

Definir identidade e eventual tentativa, fonte verificável da versão Spark e estado incompleto para ausência de Start/End; planejar DDL e parser com fixtures. Unicidade deve respeitar o contrato de aplicação/tentativa, não apenas uma frase de aceite.

### Comunicação entre responsáveis

Para outro pod: a proposta de aplicações é delimitada, mas ainda precisa resolver identidade, versão e ciclo incompleto.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Inventar versão a partir do ambiente de análise ou unir tentativas distintas criaria contexto enganoso. Que caso o teste ainda não cobre? Faltam ApplicationEnd ausente, End antes de Start, reingestão e fonte ausente da versão Spark. Como eu explicaria isso para outro pod? A tabela é proposta de contexto; o roadmap não basta para provar a origem de cada campo.

### Próxima ação e encerramento

Próxima ação documental: preservar esta minuta visível com as correções desta ficha para análise e comparação. A decisão posterior de implementar ou publicar exige escopo e responsável definidos; não exige captura real para estudar.

<a id="item-365"></a>

## PROP-D07-PLAN-NODES-EXTRACTION — [Study][Dataship] Estudo de viabilidade da extração de nós de plano físico Spark (D07)

Frente: minutas_dataship. Encaminhamento: minuta_externa_estudo_condicional.

### Identidade e estado

PROP-D07-PLAN-NODES-EXTRACTION é uma minuta local de 2026-10-11 para Gabriel-Philot/dataship-spark-plat-v0 (study, laboratório, executor G-gemini, publicação não autorizada), origem D07: "Estudo de viabilidade da extração de nós de plano físico Spark". Não publicada.

### Intenção e benefício

Intenção: medir custo computacional e de armazenamento de normalizar operadores da árvore SparkPlan, para decidir se a análise por operador compensa. Público: mantenedor do laboratório. Ganho: decisão informada de adotar ou arquivar.

### Feito, faltante e não comprovado

Avaliação: a minuta formula bem a pergunta (custo × benefício) e mantém a implementação fora; o critério "revisão aprovada pelo mantenedor" é formal mas não verificável por conteúdo — falta pedir números (volume por execução, tempo de parsing). Está alinhada à condição do upstream ("if operator-level analysis becomes important").

### Linhagem

Linhagem: exploration-roadmap.md do upstream (passo 5, condicionado a análise por operador) → registro D07 → minuta Gemini de 11/10 com critério só formal → publicação [não autorizada] → spike de custo [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-loader.go; fontes/batch-revalidated-wdprops-sources/dataship-ddl.sql; fontes/batch-revalidated-wdprops-sources/dataship-roadmap.md; fontes/batch-proposals-review-sources/PROP-D07-PLAN-NODES-EXTRACTION.md. Locadores: MATRIX proposals[PROP-D07-PLAN-NODES-EXTRACTION]; minuta integral; Roadmap spark_sql_plan_nodes e condição de prioridade; minuta D07.

### Classe e limite da evidência

FATO OBSERVADO: pergunta e condição alinhadas ao roadmap do upstream; critério de aceite apenas formal. PROPOSTA: a própria minuta. Nenhuma execução nesta revisão.

### Fluxo

Fluxo proposto: amostras de sparkPlanInfo —(spike de representações)→ estimativa de volume e custo —(documento de recomendação)→ mantenedor —(adotar ou arquivar).

### Consequências e risco

Se usada como está, a minuta não causa dano, mas pode produzir um parecer sem números de volume ou tempo que não ajuda a decidir. Impacto só no laboratório. Confiança alta.

### Alternativas e recomendação

Manter como estudo visível e comparar representações usando amostras estáticas ou sintéticas claramente marcadas. Uma pergunta por operador orienta a prioridade de implementação; não impede analisar a proposta offline.

### Dependências e paralelismo

Nenhuma dependência para revisão e estudo offline. Ordem sugerida, proteções de implementação e decisão de adoção upstream permanecem separadas.

### Plano e aceite propostos

Estudo offline permitido: definir perguntas, comparar nós completos e subconjunto, estimar linhas/bytes por plano e registrar limites. Medir tempo exige experimento posterior autorizado; estimativa não é benchmark.

### Comunicação entre responsáveis

Para outro pod: este estudo compara representações de planos com estimativas identificadas; execução de benchmarks fica para escopo futuro.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Confundir nós estruturais com medidas de custo atribuiria duração ao operador sem prova. Que caso o teste ainda não cobre? Não há medição de volume ou tempo nem cobertura de nós repetidos/reutilizados e versões adaptativas. Como eu explicaria isso para outro pod? D07 é estudo de representação e custo, viável offline e sem obrigação de implementar.

### Próxima ação e encerramento

Próxima ação documental: preservar esta minuta visível com as correções desta ficha para análise e comparação. A decisão posterior de implementar ou publicar exige escopo e responsável definidos; não exige captura real para estudar.

<a id="item-366"></a>

## PROP-D08-EXECUTOR-METRICS-NORMALIZATION — [Study][Dataship] Avaliação de normalização de métricas de executores Spark (D08)

Frente: minutas_dataship. Encaminhamento: minuta_externa_estudo_condicional.

### Identidade e estado

PROP-D08-EXECUTOR-METRICS-NORMALIZATION é uma minuta local de 2026-10-11 para Gabriel-Philot/dataship-spark-plat-v0 (study, laboratório, executor G-gemini, publicação não autorizada), origem D08: "Avaliação de normalização de métricas de executores Spark". Não publicada.

### Intenção e benefício

Intenção: decidir como armazenar métricas periódicas de executores (CPU, memória, GC) sem sobrecarregar o ClickHouse com séries temporais. Público: mantenedor do laboratório. Ganho: requisitos de modelagem para análise de capacidade.

### Feito, faltante e não comprovado

Avaliação: a pergunta (pontos brutos × agregação por janela) é pertinente; mas a minuta não cita os eventos que o upstream já identificou (SparkListenerExecutorMetricsUpdate e SparkListenerStageExecutorMetrics) nem a diferença de volume entre eles; o critério "aprovação técnica sobre estratégias de retenção" é formal. A fronteira (sem mudar o loader) é coerente com um estudo.

### Linhagem

Linhagem: exploration-roadmap.md do upstream (passo 6, condicionado a análise de capacidade, com dois eventos-fonte já mapeados) → registro D08 → minuta Gemini de 11/10 que não cita esses eventos → publicação [não autorizada].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-loader.go; fontes/batch-revalidated-wdprops-sources/dataship-ddl.sql; fontes/batch-revalidated-wdprops-sources/dataship-roadmap.md; fontes/batch-proposals-review-sources/PROP-D08-EXECUTOR-METRICS-NORMALIZATION.md. Locadores: MATRIX proposals[PROP-D08-EXECUTOR-METRICS-NORMALIZATION]; minuta integral; Roadmap spark_executor_metrics e condição de prioridade; minuta D08.

### Classe e limite da evidência

FATO OBSERVADO: pergunta de modelagem pertinente; eventos-fonte já mapeados pelo upstream ausentes da minuta. PROPOSTA: estudo. Nenhuma execução.

### Fluxo

Fluxo proposto: eventos de métricas de executor —(pontos brutos ou agregados por janela)→ modelo de tabela —(retenção)→ análise de capacidade. A minuta descreve só a escolha de modelagem.

### Consequências e risco

Se usada como está, a minuta pode levar a modelar séries temporais sem saber qual evento usar nem seu volume; impacto só no laboratório. Confiança alta.

### Alternativas e recomendação

Manter estudo visível: comparar ExecutorMetricsUpdate e StageExecutorMetrics, campos presentes, granularidade, retenção e perdas de agregação. Menor volume do segundo é hipótese a conferir, não medição deste recorte.

### Dependências e paralelismo

Nenhuma dependência para revisão e estudo offline. Ordem sugerida, proteções de implementação e decisão de adoção upstream permanecem separadas.

### Plano e aceite propostos

Preparar matriz de eventos/campos e estimativas transparentes com fixtures sintéticas ou amostras estáticas; demanda de capacidade orienta prioridade. Diferenciar ausência de métrica de zero e preservar unidades/granularidade.

### Comunicação entre responsáveis

Para outro pod: "A minuta D08 discute como guardar métricas de executor, mas não cita os eventos que o autor do laboratório já mapeou; vale reescrever antes de usar."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Agregar picos ou tratar ausência como zero pode esconder pressão de recurso e atribuir capacidade incorretamente. Que caso o teste ainda não cobre? Não foram medidos volume e perda por agregação, nem conferida disponibilidade de métricas por versão/configuração. Como eu explicaria isso para outro pod? D08 compara formatos e retenção de métricas do laboratório; não é prova de incidente nem gate do APEX.

### Próxima ação e encerramento

Próxima ação documental: preservar esta minuta visível com as correções desta ficha para análise e comparação. A decisão posterior de implementar ou publicar exige escopo e responsável definidos; não exige captura real para estudar.

<a id="item-367"></a>

## PROP-D10-WORKLOAD-CATALOG — [Feature][Dataship] Especificação de convenções e catálogo de workloads (D10)

Frente: minutas_dataship. Encaminhamento: minuta_externa_adiada_problema_vago.

### Identidade e estado

PROP-D10-WORKLOAD-CATALOG é uma minuta local de 2026-10-11 para Gabriel-Philot/dataship-spark-plat-v0 (feature, laboratório, executor G-gemini, publicação não autorizada), origem D10: "Especificação de convenções e catálogo de workloads". Sem publicação identificada nas fontes lidas; estado corrente não inferido de ausência local.

### Intenção e benefício

Pergunta proposta pela minuta: quais convenções de app, caminhos e parâmetros facilitariam identificar workloads comparáveis. O registro não descreve um incidente nem exemplo de confusão; benefício permanece hipótese organizacional do laboratório.

### Feito, faltante e não comprovado

O registro D10 contém problem/proof vazios e recomendação histórica defer. A árvore 8920273 não identifica um arquivo de catálogo pelo nome; seu conteúdo inteiro não foi auditado. Há scripts de exemplo e src/apps/template.md, portanto não se afirma ausência universal de convenções. A minuta fornece uma proposta, ainda sem caso concreto demonstrado. A minuta é objeto de estudo; este aceite documental não ratifica nem autoriza adoção.

### Linhagem

Registro D10 → minuta local PROP-D10-WORKLOAD-CATALOG → revisão documental desta ficha. Publicação, implementação e ratificação não são consequência automática desta revisão.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-tree.txt; fontes/batch-revalidated-wdprops-sources/dataship-ddl.sql; fontes/batch-revalidated-wdprops-sources/dataship-roadmap.md; fontes/batch-revalidated-wdprops-sources/dataship-current-tables.md; fontes/batch-proposals-review-sources/PROP-D10-WORKLOAD-CATALOG.md. Locadores: MATRIX proposals[PROP-D10-WORKLOAD-CATALOG]; minuta integral; Árvore 8920273 e minuta D10; campos vazios do registro.

### Classe e limite da evidência

FATO OBSERVADO: registro pouco especificado, nomes de arquivos na árvore e conteúdo da minuta. INFERÊNCIA: um catálogo poderia facilitar identificação. Não foi demonstrada perda atual por falta dele.

### Fluxo

Fluxo possível: workloads existentes → convenção e exemplos de nome/caminho/parâmetros → catálogo → identificação de runs. O vínculo a tabelas novas é opcional; catálogo documental não depende de spark_applications.

### Consequências e risco

O ganho potencial é reduzir ambiguidades e anotações dispersas; não se comprovou que todas as comparações dependam de memória. Impacto proposto é do laboratório; prioridade não foi definida nesta revisão.

### Alternativas e recomendação

Manter o estudo disponível: levantar convenções já existentes e comparar uma taxonomia curta com o uso atual. O adiamento do registro é histórico; um exemplo de confusão ajuda priorizar adoção, sem impedir estudo offline.

### Dependências e paralelismo

Nenhuma dependência técnica; complementar a D11 (metadados de experimento), com quem pode compartilhar a mesma convenção num único documento.

### Plano e aceite propostos

Trabalho documental possível agora: inventário de nomes/caminhos atuais e um esboço de convenção com exemplos identificados. Antes de adotar, explicitar a pergunta atendida e validar a utilidade com o responsável.

### Comunicação entre responsáveis

Para outro pod: D10 é proposta de organização de workloads com problema histórico pouco descrito; pode ser estudada por documentos existentes sem alterar o laboratório.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Uma taxonomia que ignore convenções existentes duplicaria nomes e poderia dificultar a identificação. Que caso o teste ainda não cobre? Não foi auditado todo o conteúdo de templates/docs nem demonstrada confusão em um par de runs. Como eu explicaria isso para outro pod? D10 é estudo de convenção e catálogo; falta evidência de utilidade para decidir adoção, mas ele segue disponível offline.

### Próxima ação e encerramento

Próxima ação documental: manter esta minuta visível com os limites e critérios corrigidos. Estudo offline disponível; publicação ou implementação futura exige escopo e responsável definidos.

<a id="item-368"></a>

## PROP-D11-EXPERIMENT-METADATA — [Docs][Dataship] Padronização de metadados para rastreabilidade de experimentos (D11)

Frente: minutas_dataship. Encaminhamento: minuta_externa_adiada_template_documental.

### Identidade e estado

PROP-D11-EXPERIMENT-METADATA é uma minuta local de 2026-10-11 para Gabriel-Philot/dataship-spark-plat-v0 (docs, laboratório, executor G-gemini, publicação não autorizada), origem D11: "Padronização de metadados para rastreabilidade de experimentos". Sem publicação identificada nas fontes lidas; estado corrente não inferido de ausência local.

### Intenção e benefício

A minuta pergunta como registrar ambiente, hardware, versões e parâmetros por run para apoiar comparação. O registro só declara Runs comparáveis; ausência de metadados padronizados não torna toda comparação impossível e não garante reprodução por si só.

### Feito, faltante e não comprovado

O DDL de seis tabelas não tem entidade de experimento; isso não prova ausência de anotações ou templates em todo o repositório. O registro liga D11 a D02 e adia; a minuta propõe template documental. Faltam campos, identidade do run, referências de artefatos e critérios que permitam explicar diferenças. A minuta é objeto de estudo; este aceite documental não ratifica nem autoriza adoção.

### Linhagem

Registro D11 → minuta local PROP-D11-EXPERIMENT-METADATA → revisão documental desta ficha. Publicação, implementação e ratificação não são consequência automática desta revisão.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-tree.txt; fontes/batch-revalidated-wdprops-sources/dataship-ddl.sql; fontes/batch-revalidated-wdprops-sources/dataship-roadmap.md; fontes/batch-revalidated-wdprops-sources/dataship-current-tables.md; fontes/batch-proposals-review-sources/PROP-D11-EXPERIMENT-METADATA.md. Locadores: MATRIX proposals[PROP-D11-EXPERIMENT-METADATA]; minuta integral; DDL de seis tabelas e minuta D11.

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

Próxima ação documental: manter esta minuta visível com os limites e critérios corrigidos. Estudo offline disponível; publicação ou implementação futura exige escopo e responsável definidos.

<a id="item-369"></a>

## PROP-D12-OPERATIONAL-QUERY-PACK — [Docs][Dataship] Pacote de consultas canônicas para o ClickHouse (D12)

Frente: minutas_dataship. Encaminhamento: minuta_externa_conferir_documentacao_existente.

### Identidade e estado

PROP-D12-OPERATIONAL-QUERY-PACK é uma minuta local de 2026-10-11 para Gabriel-Philot/dataship-spark-plat-v0 (docs, laboratório, executor G-gemini, publicação não autorizada), origem D12: "Pacote de consultas canônicas para o ClickHouse". Sem publicação identificada nas fontes lidas; estado corrente não inferido de ausência local.

### Intenção e benefício

Intenção: conjunto de consultas prontas sobre as seis tabelas para diagnosticar estágios, tarefas e desbalanceamento. Público: novos usuários do laboratório. Ganho: começar a explorar sem SQL do zero.

### Feito, faltante e não comprovado

Lidos integralmente exploration-roadmap.md e current-tables.md: o primeiro lista oito perguntas úteis; o segundo descreve colunas/semântica das seis tabelas e não contém consultas SQL. A árvore tem outros documentos não auditados; não se conclui ausência de exemplos em todo o repositório. A minuta propõe queries.sql, ainda sem consulta ou eficiência demonstradas. A minuta é objeto de estudo; este aceite documental não ratifica nem autoriza adoção.

### Linhagem

Registro D12 → minuta local PROP-D12-OPERATIONAL-QUERY-PACK → revisão documental desta ficha. Publicação, implementação e ratificação não são consequência automática desta revisão.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-tree.txt; fontes/batch-revalidated-wdprops-sources/dataship-ddl.sql; fontes/batch-revalidated-wdprops-sources/dataship-roadmap.md; fontes/batch-revalidated-wdprops-sources/dataship-current-tables.md; fontes/batch-proposals-review-sources/PROP-D12-OPERATIONAL-QUERY-PACK.md. Locadores: MATRIX proposals[PROP-D12-OPERATIONAL-QUERY-PACK]; minuta integral; Roadmap, current-tables.md e DDL integrais; minuta D12.

### Classe e limite da evidência

FATO OBSERVADO: oito perguntas, seis tabelas e descrição sem SQL em current-tables.md. PROPOSTA: consultas comentadas. Não foi feita execução ou busca exaustiva de exemplos em todo o projeto.

### Fluxo

Fluxo proposto: pergunta típica —(consulta SQL comentada)→ ClickHouse do laboratório —(resultado)→ usuário; idealmente uma consulta por pergunta do roadmap.

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

Próxima ação documental: manter esta minuta visível com os limites e critérios corrigidos. Estudo offline disponível; publicação ou implementação futura exige escopo e responsável definidos.

<a id="item-370"></a>

## PROP-D13-SPARK-CONNECT-EQUIVALENCE — [Study][Dataship] Estudo de paridade de telemetria com Spark Connect (D13)

Frente: minutas_dataship. Encaminhamento: minuta_externa_estudo_de_paridade_connect_prioridade_pendente.

### Identidade e estado

PROP-D13-SPARK-CONNECT-EQUIVALENCE é uma minuta local de 2026-10-11 para Gabriel-Philot/dataship-spark-plat-v0 (study, laboratório, executor G-gemini, publicação não autorizada), origem D13: "Estudo de paridade de telemetria com Spark Connect". Sem publicação identificada nas fontes lidas; estado corrente não inferido de ausência local.

### Intenção e benefício

Pergunta de estudo: quais eventos, campos, identidades e propriedades diferem entre o modo primário spark-submit e Spark Connect para o mesmo workload. As diferenças são hipóteses a comparar; não foi demonstrado que o loader esteja incorreto em Connect.

### Feito, faltante e não comprovado

O registro diz spark-submit segue primário e recomenda adiar; isso não comprova ausência de uso ou de ambiente Connect. A minuta define estudo conceitual sem implementar suporte. A árvore inclui material histórico cujo nome cita Connect; não foi avaliado como prova de paridade. A minuta é objeto de estudo; este aceite documental não ratifica nem autoriza adoção.

### Linhagem

Registro D13 → minuta local PROP-D13-SPARK-CONNECT-EQUIVALENCE → revisão documental desta ficha. Publicação, implementação e ratificação não são consequência automática desta revisão.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-tree.txt; fontes/batch-revalidated-wdprops-sources/dataship-ddl.sql; fontes/batch-revalidated-wdprops-sources/dataship-roadmap.md; fontes/batch-revalidated-wdprops-sources/dataship-current-tables.md; fontes/batch-proposals-review-sources/PROP-D13-SPARK-CONNECT-EQUIVALENCE.md; fontes/batch-revalidated-wdprops-sources/dataship-compatibility.md. Locadores: MATRIX proposals[PROP-D13-SPARK-CONNECT-EQUIVALENCE]; minuta integral; Registro D13, árvore, notas de compatibilidade e minuta.

### Classe e limite da evidência

FATO OBSERVADO: pergunta e adiamento no registro/minuta. HIPÓTESE: possíveis diferenças de eventos e identidade. Não há evidência lida suficiente para declarar ambiente inexistente, nenhum usuário ou suporte/ausência de suporte.

### Fluxo

Fluxo proposto: workload de referência —(spark-submit)→ eventos A; —(Spark Connect)→ eventos B —(comparação por tipo)→ nota técnica de paridade.

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

Próxima ação documental: manter esta minuta visível com os limites e critérios corrigidos. Estudo offline disponível; publicação ou implementação futura exige escopo e responsável definidos.

