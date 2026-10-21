# Fichas documentais — lote 27

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-261"></a>

## L10 — Verify usar runtime medido (executor_run_time_ms)

Frente: verify_modelagem. Encaminhamento: agrupar_em_179_corrigir_texto_e_estudar.

### Identidade e estado

L10 é o estudo do Pod 1/Verify sobre trabalho medido e fallback estimado no predictor. A publicação PROP-L10-VERIFY-RUNTIME criou a issue #179, aberta, sem assignee e sem comentários na captura de 16/10. Responsável técnico Verify, a confirmar. DEC-06 ajuda a confirmar ownership; não impede estudar a pergunta já publicada.

### Intenção e benefício

Problema: o Verify estima o trabalho W a partir de p50, p99 e número de tarefas porque models.py:38-40 e predict.py:19-21 e :158 dizem que executor_run_time_ms "is NOT a column in apex.spark_events"; mas a migração 039 adiciona a coluna e o Engine já a lê. Público: quem confia na previsão do Verify. Ganho: texto correto agora e, se o estudo concluir, W medido quando houver dado, com fallback estimado rotulado.

### Feito, faltante e não comprovado

Na base c3c3ea3, models.py:38–42 e predict.py:19–21,158 conservam a afirmação falsa sobre ausência da coluna; WORK_IS_ESTIMATED=True e work_bracket usa as durações efetivas p50/p99 e task_count. A migração 039 declara Int64 DEFAULT 0 e a MV; Engine lê coluna positiva com fallback ao Map. O teste da matriz exige o literal antigo de models.py. A #164 muda verify/README.md, sem tocar predictor/modelos/teste da matriz. DDL presente não prova migração aplicada ou valor útil em banco.

### Linhagem

Linhagem: runtime medido no JAR/contrato/Engine → drift estático Verify → L10 → minuta publicada como #179 → #164 corrige README em escopo próprio → correção textual coordenada e estudo de semântica ainda não demonstrados nestas fontes. O candidato local CL-02 não foi necessário para concluir esse confronto nem usado como autoridade.

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/primary-public-selected.json issue 179 (critérios: unidade, agregação, população, proveniência; zero histórico/ausente/inválido/successful-task); fontes/batch-revalidated-xldd-sources/publication-subset.json PROP-L10; fontes/batch-revalidated-xldd-sources/code/verify__src__apex_verify__models.py:38–42; fontes/batch-revalidated-xldd-sources/code/verify__src__apex_verify__predict.py:19–21,84–101,158; fontes/batch-revalidated-xldd-sources/code/infra__sql__039_executor_runtime_additive.sql; fontes/batch-revalidated-xldd-sources/code/engine__src__apex_engine__clickhouse.py:47–49,88–90; fontes/batch-revalidated-xldd-sources/code/tests__test_telemetry_compatibility_matrix.py:166; fontes/pr164-files.json (head 5d42763a…, três READMEs).

### Classe e limite da evidência

FATO OBSERVADO: textos, regra de cálculo atual, coluna/MV declaradas, fallback Engine, asserção literal e diff da #164. NÃO VERIFICADO: schema aplicado, população/valores em banco, equivalência entre executor runtime e W requerido. PROPOSTA: política measured/estimated/unavailable após estudo; >0 é comportamento do Engine, não decisão já ratificada para Verify.

### Fluxo

Fluxo estático observado: StageObservation —(p50/p99 efetivos e task_count)→ work_bracket —(intervalo de W estimado)→ bound_analysis —(limites de previsão)→ consumidor. Fonte alternativa a estudar: coluna/Map executor_run_time_ms —(unidade, população e disponibilidade)→ seleção de W ou fallback. A presença de dado não elimina incerteza de previsão nem certifica ganho runtime.

### Consequências e risco

O texto obsoleto pode induzir decisões erradas de manutenção. Usar default zero como medição também seria enganoso. Não foi demonstrado veredito errado ou que substituir W pelo runtime melhoraria o modelo. Confiança alta no drift textual, pendente na adequação semântica da medição.

### Alternativas e recomendação

Recomendado: separar em dois passos: (a) correção textual pequena em models.py, predict.py e na asserção do teste, dizendo "coluna declarada no schema; o predictor ainda não a lê", sem sugerir persistência observada; (b) estudo de W medido com fallback na #179. Alternativas: fazer tudo junto (mistura texto com fórmula); só documentar (mantém o texto falso). Reversível.

### Dependências e paralelismo

Correção textual pode ser feita em paralelo ao estudo, coordenada com a asserção da matriz (C04-16); não espera a #180 inteira, #162 ou #164. O estudo pode começar na #179; mudança de fórmula/contrato exige decisão de owner apropriada, com unidade e população definidas.

### Plano e aceite propostos

Passos: (1) corrigir as três afirmações textuais e a asserção correspondente sem alterar fórmula; controle proporcional de diff/guarda existente; (2) mapear W estimado versus executor runtime, unidades e população; (3) casos de medição válida, zero histórico, ausência, inválido e successful-task; (4) decidir usar medição, manter estimativa ou combinar limites; (5) se houver implementação aprovada, controles discriminantes de seleção/fallback. Aceite #179 exige todos os critérios ou revisão explícita; uma decisão sozinha não implementa os controles condicionais.

### Comunicação entre responsáveis

Para outro pod: “O schema declara executor_run_time_ms e o Engine tem fallback; o Verify ainda estima W. Corrigir a frase falsa exige ajustar a guarda que a fixa. Usar o runtime como W é estudo de unidade e população, sem prometer ganho por haver uma coluna.”

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Usar zero histórico como W medido confundiria ausência com medição. Que caso o teste ainda não cobre? A guarda textual não decide unidade/população nem prova fallback medido/estimado do predictor. Como eu explicaria isso para outro pod? Texto correto e seleção semântica de W são entregas separadas, com critérios próprios.

### Próxima ação e encerramento

Próxima ação: owner Verify, a confirmar, prepara correção textual coordenada e estudo na #179. Entrada: código, migração, diff #164 e critérios públicos. Saída: diff textual revisável e tabela semântica de casos. Encerramento: critérios da #179 satisfeitos ou explicitamente revistos; nenhum runtime desta revisão.

<a id="item-262"></a>

## L11 — Contribuição e esforço como histórico

Frente: historico_contribuicao. Encaminhamento: encerrar_historico_nao_e_feature.

### Identidade e estado

L11 é documentação histórica de contribuição e esforço, sem objeto público próprio. Fonte recuperada: APEX-AUGUSTO-BRANCH-SALVAGE-AND-EFFORT-2026-08-24.md, snapshot declarado 24/08/2026 18:26 -03, 15.047 bytes. Original lido; extrato sanitizado e hash preservados. Custodiante: a confirmar.

### Intenção e benefício

Intenção: registrar métricas de cadência e contribuição (quem fez o quê, quando) como contexto histórico, deixando claro que não são features, prioridades nem timesheet. Público: quem lê o histórico do projeto. Ganho: evitar que métricas de esforço sejam usadas como medida de valor entregue.

### Feito, faltante e não comprovado

A fonte foi localizada pelo ponteiro explícito de LINEAGE-MAP.md e lida integralmente. Ela relata 391 hashes visíveis distintos e 123,73 horas de cadência entre commits próximos; ressalva reimplementações com hash diferente, sobreposição de diffs e trabalho não observado. Não são 391 features, horas totais, timesheet nem número de commits atuais da main. As métricas não foram recalculadas.

### Linhagem

Linhagem documental: análise de branches/PRs com corte em 24/08 → relatório de salvage/contribuição → ponteiro no cabeçalho de LINEAGE-MAP.md → registro L11 → triagem archive. O original agora está identificado por caminho e SHA-256; cadeia de cada commit contado não foi reconstituída.

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/local/L11-salvage-effort-excerpt.md (Contribution effort e Interpretation limits); fontes/batch-revalidated-xldd-sources/local/L11-source-receipt.json (hash do original de 15.047 bytes e do extrato); fontes/batch-revalidated-xldd-sources/local/LINEAGE-MAP.md:7, ponteiro para o relatório de 24/08; fontes/batch-revalidated-xldd-sources/selected-register-matrix.json L11. Original: [caminho local omitido]

### Classe e limite da evidência

FATO OBSERVADO: fonte localizada, conteúdo lido, ponteiro e hash. RELATO HISTÓRICO: contagens de commits, PRs, issues e horas de cadência calculadas no estudo de 24/08. NÃO VERIFICADO: recálculo independente desses números ou sua atualização posterior. Valor/qualidade de produto não decorrem de volume.

### Fluxo

Fluxo de uso correto: métricas de contribuição —(contexto)→ leitores do histórico; uso incorreto a evitar: métricas —(como prioridade ou avaliação)→ roadmap. Não há fluxo de produto.

### Consequências e risco

Sem ação, nada muda. O risco é usar contagem de commits ou PRs como medida de valor; a classificação mitiga. Confiança alta na classificação, baixa no conteúdo não lido.

### Alternativas e recomendação

Recomendado: preservar como histórico datado com os limites da fonte. Alternativa: recalcular um novo recorte de contribuição, somente se necessário e sem reescrever o snapshot. Não usar contagens como prioridade, valor ou avaliação automática de pessoas.

### Dependências e paralelismo

Nenhuma dependência de produto para catalogar. Uso futuro de uma métrica exige citar o recorte e método originais; nova comparação exige metodologia compatível e fontes específicas, não presumir que os números de agosto continuam atuais.

### Plano e aceite propostos

Conservar fonte/hash/data e interpretação: cadência observável não é timesheet; hash distinto não é feature distinta; soma de diffs pode contar sobreposição. Controle documental: qualquer citação dos números deve carregar esses limites. Não se exige teste de produto para esta catalogação.

### Comunicação entre responsáveis

Para outro pod: “O relatório de 24/08 quantifica contribuição visível no recorte histórico. As horas medem intervalos entre commits próximos; os hashes podem incluir retrabalho. Os números não são features, timesheet nem medida isolada de valor.”

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Contar hashes como features duplicaria retrabalho e confundiria volume com valor. Que caso o teste ainda não cobre? Esta revisão não recalculou a deduplicação, sessões ou horas de cadência da fonte de agosto. Como eu explicaria isso para outro pod? São métricas históricas observáveis com limites explícitos, sem uso como timesheet.

### Próxima ação e encerramento

Próxima ação: custodiante, a confirmar, cataloga L11 com fonte recuperada, hash e data. Entrada: relatório integral e extrato sanitizado. Saída: histórico rastreável e limites das métricas. Encerramento documental: fonte e interpretação registradas.

<a id="item-263"></a>

## L12 — Genealogia atual #66–#149

Frente: historico_linhagem. Encaminhamento: externo_registro_local_genealogia_ate_149.

### Identidade e estado

L12 é uma auditoria de linhagem local: genealogia atual #66-#149, em LINEAGE-MAP.md na custódia ([caminho local omitido] Referências públicas: PRs #147, #148 e #149 integradas em 06/10. Responsável: Augusto (a confirmar).

### Intenção e benefício

Intenção: manter um mapa datado das PRs e de suas arestas classificadas (implementa, depende, substitui), para revisar a fila sem inventar continuidade. Público: quem revisa PRs e auditorias. Ganho: contexto de linhagem para decisões de merge e follow-up.

### Feito, faltante e não comprovado

LINEAGE-MAP.md foi lido integralmente: corte #66–#134 em 24/09 e apêndices de 30/09 até #149. Os cortes conservam #126–#149 abertas e alegações de CI daquelas datas. Snapshot de 16/10 mostra merges e novas PRs #150–#164, incluindo a pilha #157→#163. Portanto o delta precisa atualizar mudanças materiais dos nós antigos e adicionar novos; não basta listar números posteriores a #149. Nenhuma revisão humana do mapa foi demonstrada.

### Linhagem

Linhagem documental: L02 (22/08) → mapa com corte 24/09 → apêndices de 30/09 #135–#149 → custódia e registro L12 → mudanças públicas posteriores dos nós existentes + PRs novas → delta atual ainda não demonstrado. Estados de cada corte continuam históricos; números de PR não definem a ordem temporal de merge.

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/local/LINEAGE-MAP.md, integral, SHA-256 f35155ed… (cortes, classes, árvores, follow-ups e limites); fontes/batch-revalidated-xldd-sources/L-primary-public.json PRs 147–164 e suas bases/heads/merged_at; fontes/batch-revalidated-xldd-sources/primary-public-selected.json PRs integradas 129/132–146 no recorte; fontes/batch-revalidated-xldd-sources/local/main-first-parent-c3c3ea3.txt; fontes/batch-revalidated-xldd-sources/selected-register-matrix.json L12. #150/#151 merged_at 20:11Z em 06/10 precedem #149 20:12Z, apesar do número maior.

### Classe e limite da evidência

FATO OBSERVADO: conteúdo integral do mapa, seus limites datados, metadados de merge posteriores e base #163 na branch da #157. RELATO HISTÓRICO: 108/110 checks e 10 controles negativos mencionados pelo registro; não reexecutados nem usados como prova atual. A custódia conserva bytes atuais diferentes do manifesto antigo, fato que não determina sozinho intenção/autoria da alteração.

### Fluxo

Fluxo documental: fontes públicas por objeto/data —(estado, base/head, merge, checks/reviews efetivamente lidos)→ arestas classificadas —(delta datado sem reescrever cortes)→ genealogia. Um delta deve acompanhar tanto nós que mudaram como nós novos; CI histórica não migra de SHA por mera ancestralidade.

### Consequências e risco

Sem atualização, revisões futuras podem perder relações das PRs #150-#164, como a pilha #157→#163; o risco é de contexto, não de produto. Confiança alta.

### Alternativas e recomendação

Recomendado: conservar cortes e acrescentar delta com escopo temporal declarado, cobrindo merges/alterações dos nós antigos e PRs novas, com fontes próprias de reviews/checks quando a conclusão depender delas. Alternativas: encerrar o mapa como histórico e manter sucessor identificado; reescrever os cortes apagaria a visão anterior. Atualização documental reversível.

### Dependências e paralelismo

Atualizar o mapa não depende de produto/CI executada nem de X09 completo. Exige fontes primárias para cada aresta; fichas anteriores podem orientar a busca, sem substituir os objetos públicos/código correspondentes. Não se presume que main igual revalidou checks/reviews/rulesets.

### Plano e aceite propostos

Passos: (1) definir data/ref e inventariar nós antigos alterados e PRs novas; (2) registrar deltas de estado e relações com fontes diretas; (3) identificar árvore/attempt/workflow de qualquer prova CI citada; (4) revisão documental de arestas e limites; (5) revisão humana do mapa. Aceite: delta datado cobre mudanças materiais do recorte e preserva snapshots anteriores; a contagem histórica de checks não o substitui.

### Comunicação entre responsáveis

Para outro pod: “O mapa vai até #149, com cortes de setembro. Precisamos acrescentar os merges que mudaram aqueles nós e as PRs novas, incluindo #157→#163. O número da PR não é cronologia e a CI antiga conserva seu SHA.”

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Atualizar só #150 em diante deixaria PRs antigas figurando como abertas e CI de setembro parecendo atual. Que caso o teste ainda não cobre? Controles históricos da genealogia não reconfirmam reviews/checks de novos heads. Como eu explicaria isso para outro pod? O delta registra mudanças em nós antigos e novos, com data/ref e arestas sustentadas por fontes.

### Próxima ação e encerramento

Próxima ação: Augusto/custodiante, a confirmar, decide atualizar ou encerrar o mapa como histórico. Entrada: mapa integral e fontes públicas datadas. Saída: delta de nós alterados/novos ou ponteiro para sucessor. Encerramento documental: cobertura e revisão do recorte declaradas; nenhuma implementação de produto.

<a id="item-264"></a>

## L13 — Atualizar a matriz de compatibilidade (Front, v0.6, #129)

Frente: arquitetura_matriz_telemetria. Encaminhamento: agrupar_em_180_executar_atualizacao_preservando_historico.

### Identidade e estado

L13 é documentação/teste cross-lane: atualizar a matriz de compatibilidade para Front, v0.6 e #129. Publicado da minuta PROP-L13-MATRIX-UPDATE (Kimi) como issue luanmorenommaciel/apex#180 "[Docs][Cross-pod] Atualizar cobertura da matriz para Front, API e proveniência", aberta em 2026-10-11, assignee gustocezar (reserva de estudo), um comentário; L14 foi agrupado nela. Owner: cross-pod (a confirmar).

### Intenção e benefício

Problema: a matriz da main declara base 847d7a0 e "Front-End: absent/external", embora front/ exista desde a #100 e a apex-api desde a #129; o gate estático deixou de representar a topologia. Público: todos os Pods. Ganho: um mapa atual de produtores, transportes e consumidores, sem promover declaração a prova de runtime.

### Feito, faltante e não comprovado

Base c3c3ea3: matriz/teste foram lidos integralmente; base 847d7a0, Front ausente e manifesto sem Front/API. types.ts:8 declara 0.5 enquanto CONTRACT.md declara v0.6; isso é divergência de declaração, não incompatibilidade runtime. resources.py encaminha rotas ao ReadStore. O comentário completo da #180 registra a primeira matriz parcial e, depois, seis linhas de proveniência × Front/API com corpo do store. Esses artefatos são entregas locais relatadas, sem serem equivalentes à matriz/teste atualizados na main.

### Linhagem

Linhagem: matriz #111/#121 → registro L13 → #129/#132 integradas → minuta PROP-L13 → #180 com L14 absorvido → comentário registra estudo parcial e segunda rodada de seis linhas → visão atual integrada e guarda estendida ainda não demonstradas neste recorte. A segunda rodada não foi apagada nem promovida a implementação.

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/code/docs__architecture__TELEMETRY-COMPATIBILITY-MATRIX.md, base/manifesto/Front; fontes/batch-revalidated-xldd-sources/code/tests__test_telemetry_compatibility_matrix.py, manifesto/asserções; fontes/batch-revalidated-xldd-sources/code/front__src__contract__types.ts:8,228–315; fontes/batch-revalidated-xldd-sources/code/CONTRACT.md:7–21; fontes/batch-revalidated-xldd-sources/code/serve__src__apex_api__routes__resources.py, RESOURCE_ROUTES e handlers; fontes/batch-revalidated-xldd-sources/code/serve__src__apex_mcp__ch.py:320–400; fontes/batch-revalidated-xldd-sources/primary-public-selected.json issue 180 e comentário 6109743278 integral; fontes/batch-revalidated-xldd-sources/publication-subset.json PROP-L13/PROP-L14.

### Classe e limite da evidência

FATO OBSERVADO: base histórica, manifesto, constante Front, rotas/store e comentário completo da #180. RELATO: duas rodadas locais, seis linhas e revisão estática declarada no comentário. INFERÊNCIA: a versão Front pode estar desatualizada ou representar consumo intencional v0.5; exige interpretação do owner. NÃO VERIFICADO: conteúdo completo dos entregáveis locais e runtime.

### Fluxo

Fluxo proposto: produtores (JAR, Collector, Engine) —(tabelas)→ store —(ReadStore)→ apex-api /v1 —(Repository HTTP)→ Front; e store —(SQL direto)→ Front modo clickhouse e MCP. Cada aresta com fonte e estado (declared/observed/runtime_unproven). A matriz atual só cobre o lado de agosto.

### Consequências e risco

Sem atualizar o escopo, uma execução verde da guarda poderia não detectar omissão de Front/API; nenhum verde atual foi observado nesta leitura. Risco: alguém tratar a matriz histórica como mapa completo ou uma rota como prova de emissão/ingestão. Sem incidente demonstrado; confiança alta no gap do manifesto.

### Alternativas e recomendação

Recomendado: acrescentar uma visão atual ao lado da histórica, cobrindo Front e API com fontes por aresta, e estender o teste só para afirmações estáticas verificáveis; tratar a constante 0.5 do Front como achado próprio a decidir pelo dono. Alternativas: reescrever a matriz (perde a história); esperar o grafo da #106 (atrasa sem necessidade). Reversível.

### Dependências e paralelismo

Pode avançar em paralelo aos estudos; ajustes de #165 e #179 coordenam asserções literais do teste, mas não precisam esperar esta entrega (C04-16). Não depende de #106; pode alimentá-lo.

### Plano e aceite propostos

Passos: (1) recuperar/conferir as seis linhas relatadas e completar fontes de produtores, transportes, stores e consumidores; (2) visão atual datada/ref separada da histórica; (3) classificar declared/observed/absent/optional/offline_unproven e as três superfícies de L14; (4) estender controles estáticos contra topologia omitida e alegação indevida de runtime, preservando controles existentes; (5) decidir interpretação da constante Front e follow-ups só de lacunas confirmadas. Aceite: todos os critérios públicos da #180 ou revisão explícita de escopo.

### Comunicação entre responsáveis

Para outro pod: "A matriz de telemetria ainda diz que não existe Front e não cobre a apex-api. A #180 acrescenta uma visão atual sem apagar a de agosto; a constante 0.5 do Front é uma pergunta separada."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Atualizar só a versão declarada manteria Front/API fora da topologia e poderia sugerir compatibilidade não provada. Que caso o teste ainda não cobre? A guarda atual não representa essas arestas nem prova emissão, persistência e ingestão reais. Como eu explicaria isso para outro pod? A #180 acrescenta visão atual com fontes e preserva o histórico; as seis linhas locais são estudo relatado.

### Próxima ação e encerramento

Próxima ação: owners Front/API e custodiante, a confirmar, conferem as seis linhas relatadas e completam matriz/controles da #180. Entrada: comentário integral, código e entregáveis locais a recuperar. Saída: proposta documental revisável, com decisão sobre constante Front e lacunas classificadas. Encerramento: critérios da #180 atendidos ou explicitamente revistos.

<a id="item-265"></a>

## L14 — Lacunas históricas A1 ainda abertas

Frente: arquitetura_proveniencia. Encaminhamento: agrupar_em_180_confirmar_por_lane.

### Identidade e estado

L14 é um estudo cross-lane: lacunas históricas A1 ainda abertas (status/duração real de job, identidade de ambiente, registro de decisão da Memory). A minuta própria PROP-L14-PROVENANCE-GAPS (Kimi) não foi publicada; PUBLICATION.json registra a disposição "grouped" em PROP-L13-MATRIX-UPDATE, ou seja, na issue luanmorenommaciel/apex#180. Owner: cross-pod (a confirmar).

### Intenção e benefício

Problema: sem essas três superfícies, comparações entre runs e entre hosts não sabem se o job terminou bem, em que ambiente rodou nem por que a memória recomendou algo. Público: quem compara runs e quem confia em recomendações da memória. Ganho: comparações mais honestas e explicáveis.

### Feito, faltante e não comprovado

O registro inferia três superfícies a partir do contrato, com state unknown; não comprova ausência universal. Leitura direta: Front RunSummary.wall_clock_ms é nullable e seu comentário diferencia duração de job de span por shape; ReadStore._run_rollup_sql parte de spark_events e usa run_outcomes para dados por shape; DDL run_outcomes define wall_clock_ms como span e contém configuração parcial/topologia por campos de recursos. Não há aqui prova de duração/status finais de job nem identidade completa de ambiente. O comentário completo #180 já relata seis linhas estudadas, portanto confirmação por lane não deve ser descrita como trabalho que nunca começou.

### Linhagem

Linhagem: A1 de 06/08 → registro L14 (hipóteses derivadas, confirmação pendente) → PROP-L14 grouped em PROP-L13/#180 → estudos locais relatados em duas rodadas → confirmação completa com fontes/escopo e prioridade de produto ainda não demonstradas neste recorte. Não se criou issue duplicada.

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/publication-subset.json disposition PROP-L14-PROVENANCE-GAPS grouped; fontes/batch-revalidated-xldd-sources/selected-register-matrix.json L14 (state unknown, proof_missing confirmação por lane); fontes/batch-revalidated-xldd-sources/local/A1-FIELD-PROVENANCE-INVENTORY-2026-08-06.md; fontes/batch-revalidated-xldd-sources/code/front__src__contract__types.ts:284–315; fontes/batch-revalidated-xldd-sources/code/serve__src__apex_mcp__ch.py:320–400; fontes/batch-revalidated-xldd-sources/code/memory__sql__031_run_outcomes.sql:15–68; fontes/batch-revalidated-xldd-sources/code/CONTRACT.md; fontes/batch-revalidated-xldd-sources/primary-public-selected.json #180 e comentário 6109743278 integral.

### Classe e limite da evidência

FATO OBSERVADO: agrupamento, tipos/queries/DDL e comentário público das duas rodadas. INFERÊNCIA LIMITADA: essas projeções não oferecem duração final de job ou identidade completa de ambiente no recorte lido; campos de configuração/shape são cobertura parcial. RELATO: estudo local das seis linhas. NÃO VERIFICADO: ausência em todas as lanes, produtor real e persistência/ingestão ou ledger completo de decisão Memory.

### Fluxo

Fluxo estático lido: spark_events —(base de runs)→ ReadStore; run_outcomes —(outcomes por shape e configuração parcial)→ rollup —(rotas /runs e projeções)→ Front. Fluxo de estudo: três superfícies —(inventário produtor→store→consumidor com fonte)→ classificação já coberta/parcial/lacuna/decisão na #180. Nenhuma tabela nova foi decidida nesta revisão.

### Consequências e risco

Tratar ausência derivada como total pode duplicar campos já parciais; tratar wall_clock_ms por shape como duração real do job pode induzir comparação errada. A revisão demonstra o limite estático das projeções lidas, sem incidente ou ausência universal. Confiança alta no escopo das queries, pendente no inventário completo.

### Alternativas e recomendação

Recomendado: aproveitar as seis linhas relatadas e completar inventário por superfície/lane, identificando cobertura parcial e ausência no escopo pesquisado, antes de pedir prioridade. Alternativas: adiar superfícies com limite intencional documentado; propor follow-ups só para lacunas confirmadas. Issue própria duplicaria o agrupamento da publicação.

### Dependências e paralelismo

Depende da organização da #180, mas a confirmação por lane pode correr em paralelo a L13. Não depende de #106 nem de decisões de contrato; só a priorização posterior é decisão de produto.

### Plano e aceite propostos

Passos: (1) recuperar estudo de seis linhas; (2) conferir produtores, DDLs, stores e consumidores, registrando ref e escopo de busca; (3) distinguir job final de custo/span por shape, configuração de identidade de ambiente e recall de registro de decisão; (4) classificar as três superfícies; (5) levar somente lacunas confirmadas a decisão de produto. Aceite: três superfícies rastreáveis aos critérios #180, sem promover ausência a requisito automático.

### Comunicação entre responsáveis

Para outro pod: “Há dados parciais: run_outcomes guarda outcomes por shape e alguma configuração, enquanto wall_clock_ms de job segue indisponível na projeção Front. A #180 já tem estudo relatado; precisamos conferi-lo antes de declarar ausência completa ou propor novas superfícies.”

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Usar span por shape como duração total do job inventaria uma medida que essa projeção não fornece. Que caso o teste ainda não cobre? A leitura das projeções não confirma produtor real, persistência nem ausência das três superfícies em todas as lanes. Como eu explicaria isso para outro pod? A cobertura é parcial no recorte lido e precisa de inventário rastreável na #180.

### Próxima ação e encerramento

Próxima ação: owners das lanes, a confirmar, conferem estudo e completam três classificações na #180. Entrada: fontes diretas e entregáveis locais a recuperar. Saída: inventário por superfície com cobertura/lacuna e decisão de prioridade. Encerramento: critérios correspondentes da #180 satisfeitos ou revistos pelo mantenedor.

<a id="item-266"></a>

## L15 — Cenário declarativo e baselines negativos na main

Frente: historico_cenarios. Encaminhamento: encerrar_sem_acao_superado_pelo_mantenedor.

### Identidade e estado

L15 é uma decisão registrada cross-lane: cenário declarativo e baselines negativos na main. Objeto: issue luanmorenommaciel/apex#32 "[TASK] Validar contrato validation_criteria dos scenarios Apex", criada em 2026-06-09, fechada como completed em 2026-09-17T16:46:01Z por luanmorenommaciel, com um comentário. Sem owner pendente no APEX.

### Intenção e benefício

Intenção original: validar um contrato validation_criteria para os cenários do APEX, servindo de gate de qualidade de evidência. Público: quem define cenários e baselines. Ganho: critérios explícitos para aceitar evidência de um cenário.

### Feito, faltante e não comprovado

A issue #32 está fechada no snapshot; comentário 5718031645 do mantenedor em 17/09 registra “Closing as superseded”, busca histórica “zero matches on main” e o papel dos guardrails Verify/coverage Serve. Isso demonstra a decisão e sua fundamentação declarada naquela data; não prova ausência universal histórica/atual do termo nem equivalência completa entre mecanismos. O registro aponta cenários no workspace (W07), fora da verificação pública deste ID.

### Linhagem

Linhagem: issue #32 (junho) → salvage ideia 1 → decisão do mantenedor em 17/09 (superseded) → registro L15 (no_action) → acompanhamento no workspace (W07). Sem elo ausente no APEX.

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/primary-public-selected.json issue 32 (closed_at 2026-09-17T16:46:01Z, corpo integral e critérios históricos) e comentário 5718031645 de luanmorenommaciel em 2026-09-17T16:46:00Z; fontes/batch-revalidated-xldd-sources/selected-register-matrix.json L15, disposition no_action e referência W07. URL primária: https://github.com/luanmorenommaciel/apex/issues/32#issuecomment-5718031645.

### Classe e limite da evidência

FATO OBSERVADO: fechamento e comentário do mantenedor. RELATO HISTÓRICO: busca “zero matches” e cobertura substituta declaradas pelo mantenedor. NÃO VERIFICADO: busca independente de toda a main, equivalência total dos gates e entrega W07. Não se infere execução ou aceite de um contrato de cenário ausente só pelo fechamento.

### Fluxo

Fluxo descrito pelo mantenedor, não reproduzido aqui: evidência —(guardrails Verify)→ veredito; diagnóstico —(coverage/thin-telemetry Serve)→ limite de evidência. Fluxo original proposto: event log —(validation_criteria)→ pré-condição do Watcher. A substituição é decisão registrada, não prova de equivalência funcional entre todas as pré-condições.

### Consequências e risco

Sem ação, nada muda. O risco é reabrir a #32 sem evidência nova e duplicar o papel dos guardrails do Verify e da cobertura do Serve, contrariando uma decisão explícita do mantenedor. Confiança alta.

### Alternativas e recomendação

Recomendado: encerrar sem ação e respeitar a decisão do mantenedor; tratar critérios de cenário no workspace (W07). Alternativa: reabrir com proposta concreta que mostre um caso que os guardrails não cobrem. Reversível.

### Dependências e paralelismo

Nenhuma dependência no APEX. W07 (critérios de cenário no workspace) é independente, não verificável publicamente e não bloqueia nem é bloqueado por este encerramento.

### Plano e aceite propostos

Condição de não ação: nenhum passo neste ID. Reabrir somente com um caso concreto de evidência fraca que verify/guardrails e os estados de cobertura do Serve deixem passar.

### Comunicação entre responsáveis

Para outro pod: "O mantenedor fechou a #32 como superseded: o gate de qualidade de evidência hoje são os guardrails do Verify e a cobertura do Serve. Critérios de cenário seguem no workspace."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Reabrir sem caso novo duplicaria uma intenção já reconciliada pelo mantenedor. Que caso o teste ainda não cobre? Este fechamento documental não demonstra equivalência total entre validation_criteria e guardrails/coverage atuais. Como eu explicaria isso para outro pod? A #32 foi superseded por decisão explícita; cenários no workspace têm trilha separada e não foram verificados aqui.

### Próxima ação e encerramento

Próxima ação: catalogar L15 como encerrado pelo mantenedor. Owner: nenhum necessário. Entrada: comentário da #32. Saída: linha L15 "superseded em 17/09; cenários no workspace". Encerramento: imediato.

<a id="item-267"></a>

## DD01 — DOUBLE-DIAMOND-EXECUTION-STANDARD.md

Frente: tooling_double_diamond. Encaminhamento: encerrar_historico_tooling_padrao_preservado.

### Identidade e estado

DD01 é o padrão histórico de método DOUBLE-DIAMOND-EXECUTION-STANDARD.md, preservado em clone do workspace. O arquivo lido tem 4.177 bytes e hash e80632d3…; o nome não declara data própria. Sem objeto público APEX; responsável pelo método a confirmar.

### Intenção e benefício

Intenção: usar o Duplo Diamante para investigar falhas não triviais sem converter a primeira hipótese em correção, deixando explícito como cada interação mudou a seguinte (palavras do próprio padrão: "Cada rodada deve deixar explícito como a evidência de uma interação alterou a interação seguinte"). Público: quem investiga falhas no APEX. Ganho: registros por interação comparáveis entre investigações.

### Feito, faltante e não comprovado

Feito: documento exige tabela por interação, resumo quantitativo e limites, e referencia C38, C43, C49 e C51 como registros existentes. Falta neste ID: nenhuma nova entrega de produto. Aplicação uniforme e causalidade cronológica entre padrão e pilotos não foram verificadas.

### Linhagem

Linhagem documental: padrão cita C38 (29/07), C49 (30/07) e outros fechamentos → skill reaproveita o método → registro DD01 o classifica historical_evidence → DD10 propõe ampliar rastreabilidade. A referência a um piloto anterior não prova que o padrão foi escrito antes dele.

### Fontes e corte

Fontes primárias lidas em 18/10/2026: fontes/batch-revalidated-xldd-sources/local/DOUBLE-DIAMOND-EXECUTION-STANDARD.md. Proveniência e SHA-256 dos originais em fontes/batch-revalidated-xldd-sources/local-source-manifest.json; registro/triagem do ID em fontes/batch-revalidated-xldd-sources/selected-register-matrix.json. Relatos de execução permanecem relatos.

### Classe e limite da evidência

FATO OBSERVADO: texto completo do padrão, incluindo tabela e regra de não substituir logs/testes/manifestos. RELATO HISTÓRICO: os registros citados. INFERÊNCIA: utilidade para comparabilidade. Sem execução.

### Fluxo

Fluxo de método: falha observada —(Descobrir: reproduzir e contar fronteiras)→ hipótese —(Definir: critério e rollback)→ experimento de uma variável —(Desenvolver)→ evidência —(Entregar: regressão e registro)→ próxima interação. É o fluxo que a skill atual (DD04) implementa.

### Consequências e risco

Sem ação, nada muda. O risco é o padrão existir só em clones do iCloud, sujeitos a evicção (X17); a skill instalada carrega o essencial do método. Confiança alta no estado do arquivo.

### Alternativas e recomendação

Recomendado: catalogar como histórico e, se DD10 for feito, versionar o padrão junto com a skill. Alternativa: publicá-lo no repositório APEX (decisão do mantenedor; não exigido). Reversível.

### Dependências e paralelismo

Nenhuma dependência para catalogar. DD10 é o portador de qualquer evolução do registro de evidência e é independente deste catálogo; versionar o padrão junto é opcional.

### Plano e aceite propostos

Condição de não ação: nenhum passo neste ID. Se a skill for versionada (DD10), incluir uma cópia do padrão com hash para não depender do iCloud.

### Comunicação entre responsáveis

Para outro pod: "O padrão Duplo Diamante de julho explica como registrar cada interação de uma investigação; a skill apex-debug-diamond é a forma operacional dele."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere a preservação de interações inconclusivas. Que caso o teste ainda não cobre? O catálogo não testa aplicação uniforme do método em investigações posteriores. Como eu explicaria isso para outro pod? Explique a diferença entre interação, execução e rodada.

### Próxima ação e encerramento

Próxima ação: preservar o padrão e seu hash como documento histórico, dono do método a confirmar. Entrada: cópia conferida. Saída: referência recuperável. Encerramento documental: catálogo e fonte preservados; não requer novo teste.

<a id="item-268"></a>

## DD02 — C38 piloto limpo

Frente: tooling_double_diamond. Encaminhamento: encerrar_historico_tooling_licao_em_dd07_e09.

### Identidade e estado

DD02 é a evidência histórica C38-R4B-CLEAN-PILOT-DOUBLE-DIAMOND-2026-07-29.md, lida integralmente; hash 45921347…. Sem objeto público APEX próprio ou designação de responsável adicional.

### Intenção e benefício

Intenção: provar que um clone e runtime vazios permitem executar o gate oficial sem workaround, numa matriz macOS/Colima dedicada. Público: quem opera o pacote local. Ganho: pacote validado em ambiente limpo naquela data, e uma lição ambiental registrada.

### Feito, faltante e não comprovado

Verificação: a interação I3 da tabela pergunta se 127.0.0.1:8123 apontava para o ClickHouse do piloto novo; resultado "rejeitado": a porta apontava para o perfil antigo apex-r4b (colisão de perfis Colima); I4 foi aprovado depois. Feito: lição registrada. Falta neste ID: nada; a lição alimenta DD07 (skill) e E09/E11 (pacote). Não comprovado: transferência do resultado para a main atual.

### Linhagem

Linhagem: piloto R4B de 29/07 → interações I1-I4 → hipótese ambiental confirmada (colisão de porta) → registro DD02 (historical_evidence) → lição em DD07, E09 e E11. Sem elo ausente.

### Fontes e corte

Fontes primárias lidas em 18/10/2026: fontes/batch-revalidated-xldd-sources/local/C38-R4B-CLEAN-PILOT-DOUBLE-DIAMOND-2026-07-29.md. Proveniência e SHA-256 dos originais em fontes/batch-revalidated-xldd-sources/local-source-manifest.json; registro/triagem do ID em fontes/batch-revalidated-xldd-sources/selected-register-matrix.json. Relatos de execução permanecem relatos.

### Classe e limite da evidência

FATO OBSERVADO: relatório com a interação I3. RELATO: aprovação do piloto em 29/07. INFERÊNCIA: a lição de identidade de ambiente é a parte que continua válida. Nenhuma execução.

### Fluxo

Fluxo histórico: gate oficial —(conecta em 127.0.0.1:8123)→ ClickHouse do perfil antigo —(dados errados)→ investigação I3 —(comparação de perfis)→ colisão identificada —(perfil antigo parado, sem remover volumes)→ I4 aprovado.

### Consequências e risco

Sem nova ação neste ID, o relato permanece histórico. A colisão de porta pode voltar a ocorrer; a regra textual já está na skill atual, e DD07 trata a automação. Não há medição de frequência nem prova da main atual.

### Alternativas e recomendação

Recomendado: catalogar como histórico e manter a lição viva em DD07 e E11. Alternativa: repetir o piloto na main (não necessário para catalogar). Reversível.

### Dependências e paralelismo

Nenhuma dependência para catalogar. DD07 (skill) e E11 (pacote) carregam a lição de forma independente, e E09 trata a identidade de stack de modo mais amplo.

### Plano e aceite propostos

Preservar o relatório e seu recorte: commit de entrada eb5550d508548b53358d0811f277210c26436cff, Spark 4.1.2 e macOS/Colima. Reabrir para acrescentar evidência posterior ou corrigir o relato com fonte; catalogar não exige repetir o piloto.

### Comunicação entre responsáveis

Para outro pod: "No piloto de julho, a porta 8123 levava a outro perfil Colima; o diagnóstico só fechou quando se comparou o dono da porta. Esse é o motivo de DD07 e E11."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere alterar o código antes de conferir qual perfil ocupa a porta. Que caso o teste ainda não cobre? O piloto relatado não cobre a main atual nem outra plataforma. Como eu explicaria isso para outro pod? Explique por que porta e credencial não identificam sozinhas o runtime.

### Próxima ação e encerramento

Próxima ação: catalogar DD02 como histórico. Owner: nenhum necessário. Entrada: relatório C38. Saída: linha DD02 "piloto de 29/07; lição de porta em DD07/E11". Encerramento: imediato.

<a id="item-269"></a>

## DD03 — C49 agente Debug Diamond

Frente: tooling_double_diamond. Encaminhamento: encerrar_historico_tooling_criacao_da_skill.

### Identidade e estado

DD03 é a evolução histórica "C49 agente Debug Diamond" (R9), registrada em C49-R9-APEX-DEBUG-DIAMOND-AGENT-2026-07-30.md (indexado). O cabeçalho declara data 2026-07-30, branch base-project-e2e-augusto, remoto autorizado campeonato, commits de entrada 3334f6b, implementação 21c9762 e pacote 6711be3, e status "skill validada, publicada e instalada localmente". Sem objeto público APEX.

### Intenção e benefício

Intenção: criar um perfil reutilizável de diagnóstico, versionado como a skill apex-debug-diamond, que não é processo autônomo nem abre debugger por padrão. Público: quem diagnostica falhas com o Codex. Ganho: método aplicável sob demanda.

### Feito, faltante e não comprovado

Feito: skill criada e instalada em julho. A versão de julho (cópia em Documents/Apex/apex-base-project-e2e-augusto/skills/apex-debug-diamond, SKILL.md de 30/07, sha256 44a81281…) difere da instalada hoje (SKILL.md de 10/10, sha256 c2bb8baa…), ver DD04. Falta neste ID: nada. Não comprovado: os commits do cabeçalho.

### Linhagem

Linhagem: C38 (29/07) e padrão DD01 (30/07) → C49 (30/07) com commits 3334f6b → 21c9762 → 6711be3 no workspace → instalação local da skill → revisões de 10/10 (DD06, DD08, DD09 parciais) → registro DD03 (historical_evidence).

### Fontes e corte

Fontes primárias lidas em 18/10/2026: fontes/batch-revalidated-xldd-sources/local/C49-R9-APEX-DEBUG-DIAMOND-AGENT-2026-07-30.md; fontes/batch-revalidated-xldd-sources/local/legacy-skill__SKILL.md; fontes/batch-revalidated-xldd-sources/local/current-skill__SKILL.md. Proveniência e SHA-256 dos originais em fontes/batch-revalidated-xldd-sources/local-source-manifest.json; registro/triagem do ID em fontes/batch-revalidated-xldd-sources/selected-register-matrix.json. Relatos de execução permanecem relatos.

### Classe e limite da evidência

FATO OBSERVADO: relatório C49 e duas versões do SKILL.md com datas e hashes distintos (30/07 e 10/10). RELATO: commits e validação de julho no workspace. Nenhuma execução aplicável.

### Fluxo

Fluxo histórico: padrão Duplo Diamante —(R9)→ skill apex-debug-diamond em julho —(instalação)→ [caminho local omitido] —(revisões de 10/10)→ versão atual. O relatório C49 documenta o primeiro passo.

### Consequências e risco

Sem ação, nada muda. O risco é tomar o C49 como descrição da skill atual, quando a instalada foi revista em 10/10 e não segue mais o escopo fixo de julho. Confiança alta.

### Alternativas e recomendação

Recomendado: catalogar como histórico com a nota de que a skill foi revista em 10/10. Alternativa: atualizar o C49 (apagaria a história). Reversível.

### Dependências e paralelismo

Nenhuma dependência para catalogar. DD04 descreve o estado atual da skill e DD10 trata o versionamento; nenhum depende deste registro histórico.

### Plano e aceite propostos

Preservar o relatório de criação e distinguir seus bytes da versão instalada. Reabrir para corrigir fonte ou acrescentar descendente documentado; não presumir cópias adicionais que não foram inventariadas nesta revisão.

### Comunicação entre responsáveis

Para outro pod: "O C49 registra como a skill nasceu em julho; a skill instalada hoje foi revista em 10/10 e não segue mais o escopo fixo daquela versão."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere confundir o relatório de criação com os bytes instalados em outubro. Que caso o teste ainda não cobre? As validações relatadas de julho não exercitam as alterações posteriores. Como eu explicaria isso para outro pod? Explique a linhagem C49 → skill de julho → cópia instalada atual.

### Próxima ação e encerramento

Próxima ação: catalogar DD03 como histórico. Owner: nenhum necessário. Entrada: relatório C49. Saída: linha DD03 "criação de 30/07; skill revista em 10/10 (DD04)". Encerramento: imediato.

<a id="item-270"></a>

## DD04 — Skill apex-debug-diamond

Frente: tooling_double_diamond. Encaminhamento: externo_tooling_skill_revista_em_10_10.

### Identidade e estado

DD04 é a referência operacional "Skill apex-debug-diamond" (tooling pessoal), instalada em [caminho local omitido] fora do repositório APEX e sem Git próprio. Registro (corte de 01/10): referência atual com escopo e rotas de julho, review_required. Owner: Augusto (a confirmar).

### Intenção e benefício

Intenção: diagnosticar falhas APEX pela menor fronteira comprovada, com hipóteses explícitas e evidência sanitizada. Público: quem investiga falhas com o agente. Ganho: diagnóstico por fronteira sem saltar para debugger ou correção.

### Feito, faltante e não comprovado

Leitura atual de 18/10: SKILL.md c2bb8baa…, routing.md a6fc2097…, route-interface.md 5f4a4a5b… e helper f45389a5… diferem das cópias de julho. A skill deriva o escopo do pedido, exige conferir identidade do serviço, contempla consumidores e condiciona hipóteses de perda a evidência ts/TTL. evidence-schema.md e preflight preservam o conteúdo antigo. Hashes atuais coincidem com os indexados por Claude, mas o conteúdo foi lido independentemente. Datas de modificação são metadados locais, não prova externa de autoria/aceite.

### Linhagem

Linhagem: C49 (30/07) → instalação → registro DD04 (corte 01/10) → rodada DD08 de 10-11/10 com instalação de três arquivos → revisão de SKILL.md em 10/10 → cópias para estudos de 11/10 → verificação de 18/10. Elo ausente: registro versionado das mudanças (DD10).

### Fontes e corte

Fontes primárias lidas em 18/10/2026: fontes/batch-revalidated-xldd-sources/local/current-skill__SKILL.md; fontes/batch-revalidated-xldd-sources/local/current-skill__references__routing.md; fontes/batch-revalidated-xldd-sources/local/current-skill__references__route-interface.md; fontes/batch-revalidated-xldd-sources/local/current-skill__references__evidence-schema.md; fontes/batch-revalidated-xldd-sources/local/current-skill__scripts__apex-debug-preflight.sh; fontes/batch-revalidated-xldd-sources/local/current-skill__scripts__apex-debug-route.sh; fontes/batch-revalidated-xldd-sources/local/legacy-skill__SKILL.md; fontes/batch-revalidated-xldd-sources/local/DD08-SUMMARY.md. Proveniência e SHA-256 dos originais em fontes/batch-revalidated-xldd-sources/local-source-manifest.json; registro/triagem do ID em fontes/batch-revalidated-xldd-sources/selected-register-matrix.json. Relatos de execução permanecem relatos.

### Classe e limite da evidência

FATO OBSERVADO: conteúdo atual, hashes e diferenças contra as cópias antigas. RELATO HISTÓRICO: validações e instalação descritas em DD08-SUMMARY. INFERÊNCIA/PROPOSTA: DD06 atendida na redação, DD07 parcial, DD09 substancialmente coberta e DD10 residual. Não se infere falta ou existência de aprovação fora das fontes lidas.

### Fluxo

Fluxo atual da skill: pedido —(deriva repositório, base e ações permitidas)→ preflight (identidade local e ferramentas) —(Descobrir/Definir/Desenvolver/Entregar)→ rota sugerida por contagem e evidência de retenção —(hipótese, não veredito)→ evidência sanitizada segundo evidence-schema.md.

### Consequências e risco

Sem ação, a skill continua utilizável e mais correta que a de julho; o risco é ninguém saber qual versão está instalada, porque não há versão declarada nem Git. Confiança alta nos fatos.

### Alternativas e recomendação

Recomendado: catalogar DD04 com o estado de 10/10 e tratar o versionamento em DD10. Alternativas: reverter para julho (perderia correções); publicar a skill num repositório do usuário (é o próprio DD10). Reversível.

### Dependências e paralelismo

Nenhuma dependência do APEX. As melhorias DD06 a DD10 têm estados diferentes (atendida, parcial, concluída, majoritária e aberta) e podem ser fechadas uma a uma, sem ordem obrigatória.

### Plano e aceite propostos

Passo mínimo: registrar o estado de 10/10 (hashes desta ficha) como a referência atual. Condição de não ação para o APEX: nenhuma mudança de produto.

### Comunicação entre responsáveis

Para outro pod: "A skill de debug foi revista em 10/10: não fixa mais branch nem remoto, cobre lanes consumidoras e checa TTL antes de culpar a MV. O que falta é versioná-la."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere restaurar a skill de julho sem preservar as revisões posteriores. Que caso o teste ainda não cobre? A leitura estática não demonstra a execução atual do helper. Como eu explicaria isso para outro pod? Explique quais arquivos mudaram e quais ainda mantêm o schema antigo.

### Próxima ação e encerramento

Próxima ação: Augusto (a confirmar) confirma a versão de 10/10 como referência. Entrada: hashes desta ficha. Saída: registro local da versão. Encerramento: versão registrada (ou DD10 feito).

