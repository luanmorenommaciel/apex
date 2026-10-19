# Fichas documentais — lote 38

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-371"></a>

## PROP-D14-UPSTREAM-BRANCHES-EVALUATION — [Study][Dataship] Avaliação de branches experimentais do repositório upstream (D14)

Frente: minutas_dataship. Encaminhamento: minuta_externa_estudo_de_leitura_util.

### Identidade e estado

PROP-D14-UPSTREAM-BRANCHES-EVALUATION é uma minuta local de 2026-10-11 para Gabriel-Philot/dataship-spark-plat-v0 (study, laboratório, executor G-gemini, publicação não autorizada), origem D14: "Avaliação de branches experimentais do repositório upstream". Sem publicação identificada nas fontes lidas; estado corrente não inferido de ausência local.

### Intenção e benefício

O registro propõe comparar duas branches de captura com o JAR APEX para identificar sobreposição ou técnicas possíveis. A ausência de comparação é estado do registro e deste recorte, não prova de que nunca tenha ocorrido em qualquer lugar.

### Feito, faltante e não comprovado

Os recortes fixados mostram a2c8b57 com um commit/10 arquivos e 4ae68e2 com 20 commits/266 arquivos de diferença. A lista inclui listener firehose na primeira e runtime/plugin/API/bridge Spark 4.1.2 na segunda, além de documentação e evidências. Contagem de arquivos não mede utilidade; conteúdo técnico comparativo ainda não foi lido neste item. A minuta é objeto de estudo; este aceite documental não ratifica nem autoriza adoção.

### Linhagem

Registro D14 → minuta local PROP-D14-UPSTREAM-BRANCHES-EVALUATION → revisão documental desta ficha. Publicação, implementação e ratificação não são consequência automática desta revisão.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-tree.txt; fontes/batch-revalidated-wdprops-sources/dataship-ddl.sql; fontes/batch-revalidated-wdprops-sources/dataship-roadmap.md; fontes/batch-revalidated-wdprops-sources/dataship-current-tables.md; fontes/batch-proposals-review-sources/PROP-D14-UPSTREAM-BRANCHES-EVALUATION.md; fontes/batch-revalidated-wdprops-sources/dataship-branch-a2c8b57.txt; fontes/batch-revalidated-wdprops-sources/dataship-branch-4ae68e2.txt. Locadores: MATRIX proposals[PROP-D14-UPSTREAM-BRANCHES-EVALUATION]; minuta integral; Recortes a2c8b57 e 4ae68e2 e minuta D14.

### Classe e limite da evidência

FATO OBSERVADO: SHAs, contagens e nomes dos arquivos nos recortes. PROPOSTA: leitura dirigida comparativa. Maior extensão não demonstra maior utilidade, correção, compatibilidade ou segurança.

### Fluxo

Fluxo proposto: branches experimentais —(diff estático)→ matriz de componentes —(comparação com jar/ do APEX)→ recomendação de reaproveitar ou descartar —(sem porte antes do parecer).

### Consequências e risco

Pode haver ganho por reconhecer técnicas existentes; isso é benefício potencial. Não se demonstrou campo faltante no APEX, desempenho, compatibilidade binária ou efeito sobre v1.

### Alternativas e recomendação

Manter estudo disponível e comparar as duas branches por perguntas: fonte dos eventos, identidade, cobertura, ciclo de vida, fila/backpressure e dependência de APIs internas. Evitar escolher só pela contagem de commits ou fixar duração sem conhecer o conteúdo.

### Dependências e paralelismo

Nenhuma dependência; é leitura de branches públicas do upstream. O resultado interessa ao Pod do JAR do APEX, sem criar gate para a v1 nem para os demais itens D.

### Plano e aceite propostos

Leitura futura: fixar fontes por SHA nas duas branches e APEX, montar matriz de captura/contrato e distinguir ideia reutilizável de código portável. Registrar riscos e perguntas sem assumir licença ou compatibilidade. Aceite documental futuro: nota com fontes e limites por afirmação.

### Comunicação entre responsáveis

Para outro pod: "A minuta D14 propõe ler duas branches experimentais do laboratório antes de inventar captura nova no APEX; é estudo de leitura, sem porte de código."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Portar um listener ou bridge de versão sem examinar ciclo de vida e contrato poderia criar incompatibilidade ou perda de dados. Que caso o teste ainda não cobre? Nomes e contagens não cobrem comportamento, overhead, versão, licença ou comparação real com o JAR. Como eu explicaria isso para outro pod? D14 é estudo de código fixado por SHA; seu resultado pode recomendar reaproveitar uma ideia sem adotar a branch.

### Próxima ação e encerramento

Próxima ação documental: manter esta minuta visível com os limites e critérios corrigidos. Estudo offline disponível; publicação ou implementação futura exige escopo e responsável definidos.

<a id="item-372"></a>

## P-TAIL — [Feature][Front/Verify/Serve] Tratar TAIL_OUTLIER nos consumidores após #127

Frente: minutas_publicadas. Encaminhamento: minuta_publicada_166_f16_omitido.

### Identidade e estado

P-TAIL é a minuta local de 11/10/2026, preservada para linhagem. PUBLICATION.json registra sua publicação/reformulação como luanmorenommaciel/apex#166 em 2026-10-11T04:24:12Z. A issue estava aberta no snapshot de 16/10; esse estado é datado. Responsável de implementação não é atribuído por esta revisão.

### Intenção e benefício

Intenção: tratar TAIL_OUTLIER em Front (rótulo), Verify (texto do mechanism_check) e Serve (sintoma e receita) depois da #127, sem falso diagnóstico de skew. Público: Pods 1 e 3. Ganho: cauda apresentada de forma coerente nos três consumidores.

### Feito, faltante e não comprovado

Confirmada a evolução de teste por consumidor para tabela de comportamento, decisão por tipo, controles SKEW_ON_JOIN/RETRY_PRESSURE e fallback/preservação explícitos na #166. KnownFindingType lido contém RETRY_PRESSURE e não TAIL_OUTLIER, mas FindingType permanece aberto. O resíduo TAIL_OUTLIER de F16 se sobrepõe a F13; a parte RETRY_PRESSURE é escopo distinto, já descrito como integrado pelo registro.

### Linhagem

Registro F13/F16/F18/S17 → minuta P-TAIL → publicação #166 (ids F13/F18/S17; source_ids inclui F16) → revisão documental. Estudos/fixtures de comentários não foram revalidados nesta ficha.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/P-TAIL.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/front__src__contract__types.ts.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/verify__src__apex_verify__guardrails.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/engine__src__apex_engine__watchers__tail_outlier.py.txt. Locadores: Minuta, PUBLICATION #166/ids/source_ids, registros F13/F16 e recortes de tipos/guard/watcher.

### Classe e limite da evidência

FATO OBSERVADO: evolução de texto/critério, diferença entre ids e source_ids e união de tipos aberta na base. Inferência delimitada: F13 representa o resíduo TAIL_OUTLIER de F16, sem absorver toda a história de RETRY_PRESSURE.

### Fluxo

Fluxo da minuta: TAIL_OUTLIER —(KnownFindingType)→ Front; —(mechanism_check)→ Verify; —(sintoma/receita)→ Serve; cada um com teste offline. A publicação manteve o fluxo e acrescentou o ramo "fallback honesto" para tipos sem receita.

### Consequências e risco

A minuta isolada pode induzir receita por tipo sem demonstrar mecanismo; a publicação pede caracterização e aceita preservação ou não aplicável. Não há prova de tela, receita ou falso diagnóstico efetivo nesta revisão.

### Alternativas e recomendação

Preservar minuta como origem da #166; registrar F16 como origem omitida do rodapé público e mapear apenas seu resíduo TAIL_OUTLIER para F13. Não é necessário abrir duplicata ou declarar consumidores corrigidos.

### Dependências e paralelismo

Nenhuma dependência para catalogar a minuta. A #166 publicada depende das decisões por consumidor; F13 (Front), F18 (Verify) e S17 (Serve) podem correr em paralelo, e nenhum depende do piso absoluto da #168.

### Plano e aceite propostos

Registrar P-TAIL → #166 e a diferença source_ids/ids. Caracterização offline dos consumidores pode continuar; decisões de texto/receita e implementação vêm de resultados, sem exigir alteração do watcher.

### Comunicação entre responsáveis

Para outro pod: #166 fortaleceu os critérios da minuta e cobre o resíduo TAIL_OUTLIER de F16 via F13; isto não prova apresentação ou receita implementadas.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Uma mensagem ou receita genérica pode atribuir skew à cauda sem evidência; fechar todo F16 como duplicata apagaria a história RETRY_PRESSURE. Que caso o teste ainda não cobre? Não houve execução dos consumidores ou dos controles de tipo/fallback; a declaração aberta de tipos não prova apresentação. Como eu explicaria isso para outro pod? A minuta evoluiu para #166 com critérios discriminantes; Front, Verify e Serve podem ser caracterizados separadamente.

### Próxima ação e encerramento

Próxima ação documental concluída: preservar a linhagem e registrar o resíduo de F16. Eventual caracterização/implementação segue na #166 por consumidor.

<a id="item-373"></a>

## P-GATE — [CONDICIONAL][Tooling][Pod 2/Engine] Higiene do gate tail-outlier e harness R9D pós-#127

Frente: minutas_publicadas. Encaminhamento: minuta_dividida_e16_em_167_e17_em_123.

### Identidade e estado

P-GATE é a minuta local de 11/10/2026, preservada para linhagem. PUBLICATION.json registra sua publicação/reformulação como luanmorenommaciel/apex#167 em 2026-10-11T04:24:13Z. A issue estava aberta no snapshot de 16/10; esse estado é datado. Responsável de implementação não é atribuído por esta revisão.

### Intenção e benefício

Intenção: tornar executáveis e honestos o harness R9D (flags e overlay, E16) e o gate tail-outlier (generate_data desnecessário, marcador llm_calls fixo, finding não amarrado ao stage, exigência de 034/035, E17). Público: Pod 2. Ganho: harness que roda e gate mais barato com evidência amarrada.

### Feito, faltante e não comprovado

A disposição P-GATE:E17 reuse_existing preserva o gate na #123, enquanto a publicação #167 contém E16 e teste de interface sem runtime. O código lido confirma que e2e_command envia EnvFile/AdditionalComposeFile e o runner ON declara apenas Scenario/StartDev/SkipGenerate. O limite stage/snapshot e llm_calls literal do gate é evidência secundária explícita C04-11, sem reproduzir o gate.

### Linhagem

Registro E16/E17 → minuta condicional → publicação #167 para E16 e disposição reuse_existing #123 para E17 → revisão documental. Candidatos locais citados em outras fichas não são dependência automática.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/P-GATE.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/dev__scripts__r9d_overhead_ab.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/dev__scripts__e2e_canonical.ps1.txt; D-CORRECOES-E-LIMITES.md. Locadores: Minuta/condição, disposição P-GATE:E17, #167, interface e2e_command/param e C04-11.

### Classe e limite da evidência

FATO OBSERVADO: divisão publicada e incompatibilidade estática de parâmetros ON. RELATO secundário lido: C04-11 descreve busca por watcher em toda saída e marcador literal, sem falso PASS ou LLM efetivo demonstrados.

### Fluxo

Fluxo da minuta: (a) harness R9D —(flags declaradas e overlay com variáveis)→ compose config passa; (b) gate —(sem generate_data, marcador dinâmico, finding amarrado ao stage)→ evidência honesta. Na publicação, (a) ficou na #167 e (b) na #123.

### Consequências e risco

Sem ação sobre a minuta, nada muda: ela já foi aplicada corretamente. O risco seria alguém republicá-la inteira e duplicar a #123. Confiança alta.

### Alternativas e recomendação

Recomendado: catalogar a minuta como dividida e aplicada conforme a condição que ela mesma impunha. Alternativa: republicar E17 como issue própria, o que duplicaria a #123 e a decisão DEC-N6. Reversível.

### Dependências e paralelismo

Catalogar e estudar interface/gate não exige benchmark nem decisão conjunta. Um candidato compartilhado com #174 é opção de entrega; não pré-requisito de #167. A garantia exigida da #123 precisa decisão coerente com seus controles.

### Plano e aceite propostos

Registrar E16 → #167 e E17 → #123, distinguindo compatibilidade estática de interface, composição de ambiente e garantia do gate. Não usar teste de argumentos como prova de overhead ou stage binding.

### Comunicação entre responsáveis

Para outro pod: "A minuta P-GATE foi dividida como ela mesma pedia: o harness R9D virou a #167 e os problemas do gate tail-outlier continuam na #123, sem issue nova."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Republicar as duas partes duplicaria #123; aceitar um candidato de interface como prova do gate ou overhead confundiria garantias. Que caso o teste ainda não cobre? Não houve PowerShell, compose config, gate ou benchmark; stage/snapshot e contador não foram verificados em runtime. Como eu explicaria isso para outro pod? P-GATE gerou duas rotas de acompanhamento: interface R9D em #167 e garantia do gate em #123.

### Próxima ação e encerramento

Próxima ação documental concluída: preservar divisão e limites C04-11. Trabalho futuro de interface fica na #167; estudo/garantia do gate fica na #123.

<a id="item-374"></a>

## P-E18 — [Study][Pod 2/Engine] Piso absoluto de duração no watcher tail-outlier

Frente: minutas_publicadas. Encaminhamento: minuta_publicada_168_limiar_retirado.

### Identidade e estado

P-E18 é a minuta local de 11/10/2026, preservada para linhagem. PUBLICATION.json registra sua publicação/reformulação como luanmorenommaciel/apex#168 em 2026-10-11T04:24:14Z. A issue estava aberta no snapshot de 16/10; esse estado é datado. Responsável de implementação não é atribuído por esta revisão.

### Intenção e benefício

Intenção: estudar um piso absoluto de duração no watcher tail-outlier para reduzir falso positivo de warm-up sem esconder cauda real. Público: Pod 2/Engine. Ganho: menos alarme em jobs curtos.

### Feito, faltante e não comprovado

A minuta propõe limiar candidato antes de um corpus representativo; a #168 reformula para casos sintéticos de mesma razão em escalas distintas, sensibilidade e decisão sem número arbitrário. O watcher lido exige task_count e duration_sample_count ≥100, p50>0 e tail_ratio>10, além de não pertencer ao skew watcher; razão exatamente 10 não emite por esse caminho.

### Linhagem

Revisão histórica #127 → E18 → minuta → #168 com entrega reformulada → esta comparação. A grade de comentário é relato não revalidado; nenhum resultado de corpus/experimento foi produzido aqui.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/P-E18.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/engine__src__apex_engine__watchers__tail_outlier.py.txt. Locadores: Minuta/entrega, #168 e evaluate integral de tail_outlier.py.

### Classe e limite da evidência

FATO OBSERVADO: diferença de entrega e guards na base. HIPÓTESE: relevância de uma cauda em milissegundos e possível ganho de piso. Não é falso positivo real comprovado.

### Fluxo

Fluxo da minuta: fixture em escala de ms —(reproduz WARNING)→ relatório com limiar candidato —(owner)→ decisão. Fluxo publicado: casos em várias escalas —(sensibilidade)→ recomendação implementar/adiar/rejeitar —(mantenedor)→ decisão.

### Consequências e risco

Se executada ao pé da letra, a minuta poderia levar a um piso escolhido a partir de fixture sintética. A publicação corrigiu. Confiança alta.

### Alternativas e recomendação

Recomendado: catalogar a minuta como superada pela #168. Alternativa: manter a minuta como histórico do raciocínio inicial, sem uso operacional; não há razão para republicá-la. Reversível.

### Dependências e paralelismo

O estudo sintético e o desenho de sensibilidade não exigem corpus real e podem avançar offline. Representatividade real interessa antes de generalizar ou adotar um piso. #166 e #123 mantêm escopos independentes.

### Plano e aceite propostos

Preservar minuta como origem e #168 como representação reformulada. Plano de estudo: variar escala mantendo razão e demais guards explícitos, comparar regra atual, explicação de escala e pisos candidatos somente como alternativas. Nenhum teste executado.

### Comunicação entre responsáveis

Para outro pod: "A minuta pedia um limiar candidato; a #168 publicada pede primeiro sensibilidade em várias escalas, sem número arbitrário."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Escolher piso por fixture única pode ocultar caudas relevantes; tratar razão 10 como maior que 10 erra a fronteira do guard. Que caso o teste ainda não cobre? Não foram executadas escalas sintéticas nem estabelecidas prevalência e representatividade em workloads reais. Como eu explicaria isso para outro pod? E18 é estudo de sensibilidade, viável offline; não é ordem para escolher um número ou alterar detector.

### Próxima ação e encerramento

Próxima ação documental concluída: registrar ausência de piso e entrega sem limiar obrigatório. O estudo continua disponível offline na #168; decisão de detector é etapa posterior.

<a id="item-375"></a>

## P-DEC23 — [Decision][Pod 2/Pod 3] Seletor comum de tentativa de stage (DEC-23) e população legada

Frente: minutas_publicadas. Encaminhamento: minuta_publicada_169_sem_residuo_p50.

### Identidade e estado

P-DEC23 é a minuta local de 11/10/2026, preservada para linhagem. PUBLICATION.json registra sua publicação/reformulação como luanmorenommaciel/apex#169 em 2026-10-11T04:24:15Z. A issue estava aberta no snapshot de 16/10; esse estado é datado. Responsável de implementação não é atribuído por esta revisão.

### Intenção e benefício

Intenção: decidir um seletor comum de tentativa de stage (DEC-23) e a população de métricas (DEC-24 para Memory), para que Engine, Serve e Memory não misturem rótulo de uma tentativa com métricas de outra. Público: Pods 2 e 3 e Memory. Ganho: paridade entre consumidores.

### Feito, faltante e não comprovado

Avaliação: a minuta descreveu bem as quatro seleções diferentes (aggregate_events, STAGE_AGGREGATES_SQL, RUNS_SQL e leituras legadas) e proibiu corrigir SQL antes da decisão; o critério "teste de caracterização que falha com a seleção divergente" é bom. A publicação acrescentou matriz por consumidor com desempate e fallback histórico, separação explícita de #115 (identidade de execução) e #117 (piso), e a ressalva "runtime sintético não será chamado de prova Spark real". Nem a minuta nem a publicação incluem o resíduo p50=0 de F20, que a v2 dizia ter sido levado para cá.

### Linhagem

E24/S14/S19 históricos → minuta → #169 com matriz por consumidor e separação de identidade/piso → revisão documental. Decisões e integração não demonstradas no recorte.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/P-DEC23.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/engine__src__apex_engine__clickhouse.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/memory__src__apex_memory__clickhouse.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/verify__src__apex_verify__guardrails.py.txt; D-CORRECOES-E-LIMITES.md. Locadores: Minuta, #169, F20, SQLs Engine/Memory, noise_floor 232–243 e C04-38.

### Classe e limite da evidência

FATO OBSERVADO: texto da minuta/publicação não inclui p50=0 de F20; SQL Engine combina max(stage_attempt) e argMax(...,ts), Memory usa argMax por ts e percentis legados. O filtro noise_floor por p50>0 foi lido; isto limita razões de instabilidade, não o CV de job runtime.

### Fluxo

Fluxo da minuta: decisão do owner —(seletor e população)→ caracterização E24 → correção S19 → convenção S14. Fluxo publicado: matriz por consumidor —(fixtures)→ decisão —(só então)→ mudanças atômicas com paridade.

### Consequências e risco

O resíduo p50=0 não está expresso no escopo #169. Isso é lacuna de rastreabilidade neste conjunto, não prova de ausência de qualquer destino externo. Evitar confundi-lo com a seleção da população ou com o cálculo independente do piso de runtime.

### Alternativas e recomendação

Preservar P-DEC23 → #169 e anotar separadamente p50=0/F20 para roteamento documental. A decisão de seletor pode ser preparada por matriz e fixtures propostas, sem corrigir SQL antes de escolher política.

### Dependências e paralelismo

Nenhuma dependência para catalogar a minuta. A #169 depende da decisão dos owners de Engine, Serve e Memory; as fixtures podem começar já, antes de qualquer correção de SQL.

### Plano e aceite propostos

Registrar que F20/p50=0 não foi incorporado explicitamente à #169. O filtro evita divisão por zero, mas pode reduzir razões disponíveis sem explicar exclusões; não remove job_runtimes_ms do CV.

### Comunicação entre responsáveis

Para outro pod: #169 decide tentativa/população; o resíduo p50=0 de F20 é distinto e não aparece expressamente no corpo. A instabilidade das razões e o piso de runtime são checks separados.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Misturar rótulo da tentativa com métricas de outra pode mudar diagnóstico; tratar p50=0 como exclusão do CV mistura checks distintos. Que caso o teste ainda não cobre? Não executamos fixtures de empate/retry/histórico ou o caso p50=0; efeito em Spark real segue não demonstrado. Como eu explicaria isso para outro pod? #169 trata seletor e população; F20/p50=0 é ressalva separada de razão, sem retirar o CV de runtime.

### Próxima ação e encerramento

Próxima ação documental concluída: preservar minuta → #169 e ressaltar resíduo F20/p50=0 com escopo correto. Destino público e decisão do resíduo não foram criados nesta revisão.

<a id="item-376"></a>

## P-DEC25 — [Decision][Pod 2/Infra] Reaplicação do DDL e escopo do verify_ddl (DEC-25)

Frente: minutas_publicadas. Encaminhamento: minuta_publicada_170_classificacao_de_arquivos.

### Identidade e estado

P-DEC25 é a minuta local de 11/10/2026, preservada para linhagem. PUBLICATION.json registra sua publicação/reformulação como luanmorenommaciel/apex#170 em 2026-10-11T04:24:16Z. A issue estava aberta no snapshot de 16/10; esse estado é datado. Responsável de implementação não é atribuído por esta revisão.

### Intenção e benefício

Intenção: decidir se reaplicar DDL com ingestão ativa é suportado e qual escopo o verify_ddl.py cobre. Público: Infra e ingestão. Ganho: a operação sabe o que um verify verde comprova.

### Feito, faltante e não comprovado

A publicação #170 reforça classificação de SQLs, matriz fresh/migrado/concorrência/rollback/backfill e separa prova de janela em runtime autorizado. Ao contrário da ressalva anterior, ela já manda revisar a alegação de no-op e compatibilizar redação com os checks. O comentário always safe and a no-op em apply_ddl.sh é um trecho concreto desse escopo, sem necessidade de criar nova pendência independente.

### Linhagem

Linhagem: R5, parecer DEC-25 e lane1-dec25 (30/09-01/10) → registro E22/E23 → minuta P-DEC25 de 11/10 → publicação #170 com classificação de arquivos → decisão do owner Infra [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/P-DEC25.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-public-sources/infra__scripts__apply_ddl.sh.txt; fontes/batch-public-sources/infra__scripts__verify_ddl.py.txt. Locadores: Minuta, PUBLICATION #170, apply_ddl integral e verify_ddl cabeçalho/SOURCES.

### Classe e limite da evidência

FATO OBSERVADO: minuta, publicação, comentário e loop ordenado de apply_ddl; cabeçalho/mapa SOURCES do verify lista sete tabelas e checks de nome/tipo. RELATO: fixture da janela 034→039. Não foi auditado aqui o verificador inteiro nem executada migração.

### Fluxo

Fluxo da minuta: relato de fixture —(decisão de política e escopo)→ owner —(se ampliar)→ testes fresh/migrado —(medição)→ janela real. Fluxo publicado: classificação de SQLs —(matriz e decisão)→ redação do verify coerente —(runtime separado e autorizado)→ prova de janela.

### Consequências e risco

Se executada ao pé da letra, a minuta poderia levar a medir a janela num store em uso; a publicação isolou a prova em ambiente autorizado. O comentário otimista do script continua visível. Confiança alta.

### Alternativas e recomendação

Preservar minuta → #170 e mapear o comentário do script ao escopo público já existente. Separar decisão operacional, descrição da garantia atual e eventual implementação do checker. Nenhuma conclusão de segurança de migração por idempotência nominal.

### Dependências e paralelismo

Nenhuma dependência para catalogar a minuta. A #170 depende do owner Infra e do dono da ingestão; E22 (reaplicação) e E23 (verify) podem ser decididos juntos ou separados.

### Plano e aceite propostos

Registrar que #170 já pede revisar a alegação de no-op. Usar apply_ddl.sh:11–12 como localizador concreto para futuro inventário, sem duplicar ação. Estudo e classificação estáticos não esperam runtime.

### Comunicação entre responsáveis

Para outro pod: #170 já inclui revisar a promessa de reaplicação segura e definir alcance do verify; o comentário do script é um ponto desse trabalho. Prova de janela é execução futura separada.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Confundir nomes/tipos verdes com migração semanticamente segura pode omitir mudanças de MV, defaults e backfill. Que caso o teste ainda não cobre? Não se executou ingestão concorrente, fresh/migrado ou validação completa do checker; a janela é relato histórico. Como eu explicaria isso para outro pod? #170 decide política e limites do verificador; inclui a promessa no-op, enquanto prova de janela requer escopo próprio.

### Próxima ação e encerramento

Próxima ação documental concluída: preservar representação #170 e corrigir a alegação de que o comentário ficou fora dela. Nenhuma alteração de SQL, script ou store.

<a id="item-377"></a>

## P-DEC08 — [Decision][Pod 3/Serve] Exposição de /docs e credencial HTTP (DEC-08)

Frente: minutas_publicadas. Encaminhamento: minuta_publicada_171_por_perfil.

### Identidade e estado

P-DEC08 é a minuta local de 11/10/2026, preservada para linhagem. PUBLICATION.json registra sua publicação/reformulação como luanmorenommaciel/apex#171 em 2026-10-11T04:24:30Z. A issue estava aberta no snapshot de 16/10; esse estado é datado. Responsável de implementação não é atribuído por esta revisão.

### Intenção e benefício

Decidir exposição de docs/OpenAPI e custódia de token por perfil de implantação. O proxy pode manter a credencial fora do cliente se esse desenho for escolhido; isso não é garantia automática de ausência em respostas, configuração ou logs.

### Feito, faltante e não comprovado

Avaliação: a minuta formulou bem as duas perguntas abertas pela própria #129 (gap 4 e "One open question") e o critério "se exigir token: teste de 401 em /docs e /openapi.json". A publicação acrescentou a dimensão de perfil (local × compartilhado), a matriz de rotas públicas/protegidas e a regra de não inserir segredo em código, issue ou logs, e separou explicitamente esta API v1 da decisão Ask/BFF da #122. A base confirma a premissa: auth.py protege o prefixo /v1 com health público.

### Linhagem

Linhagem: corpo da #129 (gap 4 e "One open question") → registro S05/S06 (DEC-08) → minuta P-DEC08 de 11/10 → publicação #171 por perfil → decisão do mantenedor [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/P-DEC08.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_api__auth.py.txt; fontes/batch-public-sources/front__nginx.conf.txt. Locadores: Minuta, #171, auth.py integral e nginx.conf integral.

### Classe e limite da evidência

FATO OBSERVADO: textos, middleware com exceção /v1/health e ausência de injeção Authorization no nginx lido. O middleware deixa docs/OpenAPI ao app; não prova por si só que as rotas estejam habilitadas ou acessíveis em toda implantação. DECISÃO: política por perfil.

### Fluxo

Fluxo da minuta: decisão do owner —(aceitar ou exigir token; browser ou nginx)→ teste de 401 se mudar. Fluxo publicado: perfis —(matriz de rotas por perfil)→ custódia do token —(se mudar)→ testes de autorizado, 401 e ausência.

### Consequências e risco

Sem ação sobre a minuta, nada muda: a decisão vive na #171. O risco de usar a minuta seria decidir sem a dimensão de perfil, aplicando a mesma regra a local e compartilhado. Confiança alta.

### Alternativas e recomendação

Recomendado: catalogar a minuta como superada pela #171. Alternativa: manter a minuta como resumo curto das duas perguntas originais, sem uso operacional. Reversível.

### Dependências e paralelismo

Matriz e análise offline são independentes de #172/#122. #172 pode caracterizar perfil atual sem aguardar política futura; mudar custódia/exposição exige decisão e critérios coerentes. Nenhum incidente ou vazamento foi constatado.

### Plano e aceite propostos

Condição de não ação: não republicar. Nota consolidada: "P-DEC08 → #171, acrescida a dimensão de perfil e a regra de não pôr segredo em código, issue ou logs".

### Comunicação entre responsáveis

Para outro pod: "A decisão sobre /docs aberto e onde guardar o token da API virou a #171, agora por perfil de implantação; não confundir com a decisão do Ask (#122)."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Aplicar uma política implícita igual a todos os perfis pode expor rotas ou transportar token sem decisão consciente. Que caso o teste ainda não cobre? Não houve requests, browser ou inspeção de implantação; middleware e config não demonstram ausência de token em todo caminho. Como eu explicaria isso para outro pod? #171 é decisão de confiança da API v1 por perfil; #172 caracteriza perfil e #122 trata outra fronteira Ask/BFF.

### Próxima ação e encerramento

Próxima ação documental concluída: preservar P-DEC08 → #171 e dimensão de perfis. Eventual alteração de política/implantação não está incluída nesta revisão.

<a id="item-378"></a>

## P-DEC06 — [Decision][Pod 1/Verify] Escritor de fix_verifications e dono (DEC-06)

Frente: minutas_disposicao. Encaminhamento: minuta_nao_publicada_reaproveita_117.

### Identidade e estado

P-DEC06 é a minuta de 11/10 sobre escritor de fix_verifications/F06. A disposição PUBLICATION reuse_existing aponta para #117; não foi criada issue nova por essa minuta. Isso preserva uma pergunta existente, sem comprovar ausência universal de escritor.

### Intenção e benefício

Intenção: rastrear o produtor e o caminho de escrita relatado como não localizado no recorte histórico, e decidir entre documentar externo, criar ou aceitar/adiar gap. Leitura de uma tabela pelo Serve/Front não prova que ela esteja vazia em todo ambiente.

### Feito, faltante e não comprovado

A minuta oferece documentar escritor externo, criar ou aceitar/adiar gap. #117 já exige identificar produtor/persistência/consumidores e definir escopo quando ausente; reuse_existing é coerente. DEC-06 no registro também inclui ownership Verify/Memory e outros itens, além de F06. to_row lido não inclui attributable, mas serializador não equivale a escritor e não prova ausência de sink em todo ambiente.

### Linhagem

Linhagem: verify-pipeline-map de 21/09 → registro F06 (DEC-06) → minuta P-DEC06 (11/10) → disposição reuse_existing → #117 (aberta desde 11/09) → decisão [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/P-DEC06.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/DECISION-REGISTER.md; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/verify__src__apex_verify__models.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_mcp__ch.py.txt. Locadores: Minuta, disposição P-DEC06, corpo #117, DEC-06 e to_row/VERIFICATIONS_SQL.

### Classe e limite da evidência

FATO OBSERVADO: disposição, texto #117 e amplitude de DEC-06; serialização sem attributable no trecho lido. RELATO HISTÓRICO: busca de 21/09 sem escritor encontrado no head e alcance declarados. Nenhuma inspeção de escritores externos ou dado real.

### Fluxo

Fluxo da minuta: registro sem escritor —(owner confirma)→ decisão: documentar escritor externo, criar escritor ou aceitar gap —(alimenta)→ fix_verifications —(lida por)→ Serve e Front.

### Consequências e risco

A pergunta de escritor continua na #117; a amplitude de ownership deve permanecer rastreável no registro. Não se conclui que essa parte inexista em todos os outros objetos ou que toda leitura atual seja incorreta.

### Alternativas e recomendação

Recomendado: manter a disposição reuse_existing e registrar que DEC-06 inclui perguntas de ownership (F19, L10, S14) que não estão nesta minuta. Alternativa: publicar a minuta como issue própria (duplicaria a #117). Reversível.

### Dependências e paralelismo

Inventário e estudo do caminho de escrita podem começar offline sem resposta do owner. Decidir criação/escopo e política pertence ao responsável; a parte ownership do DEC-06 não vira requisito para catalogar ou desenhar exemplos.

### Plano e aceite propostos

Condição de não ação: não publicar a minuta P-DEC06. Nota consolidada: "reuse_existing → #117; DEC-06 também cobre ownership de Verify/Memory em F19, L10 e S14".

### Comunicação entre responsáveis

Para outro pod: "A pergunta 'quem escreve fix_verifications' não virou issue nova; ela está na #117. DEC-06 também cobre ownership de Verify e Memory em outros itens."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Confundir serialização com persistência permitiria afirmar integração inexistente ou criar escritor duplicado sem conhecer o caminho externo. Que caso o teste ainda não cobre? Não há prova nova de persistência/E2E, inventário universal de sinks ou confirmação de escritor externo. Como eu explicaria isso para outro pod? P-DEC06 reutiliza #117 para a pergunta do escritor; DEC-06 é mais amplo e também registra ownership de Verify/Memory.

### Próxima ação e encerramento

Próxima ação documental concluída: preservar reuse_existing → #117 e amplitude de DEC-06. Nenhum escritor foi criado nem decisão tomada.

<a id="item-379"></a>

## P-R129 — [Test][Pod 3/Serve] Prova runtime da #129 no head atual

Frente: minutas_publicadas. Encaminhamento: minuta_dividida_s02_em_156_s03_s04_em_172.

### Identidade e estado

P-R129 é minuta local de 11/10/2026, preservada para linhagem; PUBLICATION registra a representação pública luanmorenommaciel/apex#172 em 2026-10-11T04:24:31Z. Aberta no snapshot de 16/10; estado corrente e responsabilidade não inferidos desta data.

### Intenção e benefício

Intenção: provar o caminho que o usuário percorre — queries com ClickHouse real, imagem nginx com /v1 e render no navegador com DATA_SOURCE=http. Público: Pods 1 e 3. Ganho: prova real do perfil HTTP.

### Feito, faltante e não comprovado

A publicação divide S02 para #156 e S03/S04 para #172, com inventário prévio, reuso só em blobs/escopos idênticos e estados data/empty/error/indisponível. O corpo #156 relata evidência real delimitada de API/MCP/ClickHouse e explicitamente não alega browser. O histórico #153 contém trabalho e registro de reflexão/E2E que também deve entrar no inventário; títulos/commits sozinhos não comprovam execução nem dispensam critérios.

### Linhagem

Gaps datados da #129 → S02/S03/S04 → minuta → disposição S02/#156 e publicação #172/S03-S04 → inventário de evidências posteriores ainda necessário para delimitar prova restante. Ausência de browser no relato da #156 não demonstra que nunca houve outro recibo.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/P-R129.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-claude-history-sources/claude/fontes/git/PR_153.txt. Locadores: Minuta, disposições, #172, corpo #156 e histórico PR #153.

### Classe e limite da evidência

FATO OBSERVADO: divisão e critérios publicados, limites escritos de #156 e histórico integrado #153. RELATO: resultados de API/MCP/ClickHouse no corpo #156. Não reproduzidos nem transferidos automaticamente ao head atual.

### Fluxo

Rota após divisão: evidência da API #156 → conferir blobs/escopos e limites; imagem/proxy/browser #172 → inventariar recibos posteriores → executar somente lacunas futuras em ambiente identificado. Requisição pelo proxy e render visual são garantias diferentes.

### Consequências e risco

Executar a minuta inteira sem inventário pode repetir prova já existente e ainda omitir estados visuais. Declarar S02 universalmente resolvido ou browser universalmente ausente também excede as fontes.

### Alternativas e recomendação

Preservar divisão e preparar inventário por artefato, árvore, transporte e estado visual antes de definir execução. Não abrir duplicata nem chamar todo caminho HTTP de comprovado pela API.

### Dependências e paralelismo

Nenhuma dependência para catalogar. A #172 precisa de imagem/árvore identificadas e ambiente; não depende da decisão de token (#171) para caracterizar o perfil atual.

### Plano e aceite propostos

Condição de não ação: não republicar. Nota consolidada: "P-R129 dividida: S02 → #156; S03/S04 → #172 com inventário prévio de evidências e reutilização só para blobs idênticos".

### Comunicação entre responsáveis

Para outro pod: S02 aponta para a prova delimitada #156; S03/S04 seguem #172. Há que reconciliar recibos por escopo/bytes antes de repetir ou encerrar algo.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Reutilizar prova em bytes/escopos diferentes pode mascarar regressão; tratar API verde como navegador verde ignora proxy e render. Que caso o teste ainda não cobre? Não foram construídos nginx ou navegador nem repetidas provas; evidências posteriores precisam inventário por escopo. Como eu explicaria isso para outro pod? P-R129 foi dividido entre #156 e #172, com reuso condicionado ao artefato e à garantia realmente exercitada.

### Próxima ação e encerramento

Próxima ação documental concluída: registrar divisão e limites de reaproveitamento; nenhuma imagem, API ou tela executada. O inventário futuro delimita o que ainda precisa prova.

<a id="item-380"></a>

## P-S01 — [Bug][Pod 3/Serve] task_time_ms=0 para run sem run_outcomes

Frente: minutas_disposicao. Encaminhamento: minuta_nao_publicada_ja_corrigido.

### Identidade e estado

P-S01 é uma minuta local de 2026-10-11 (bug, pods 1 e 3, executor C-claude), origem S01: "task_time_ms=0 para run sem run_outcomes". Não foi publicada: a disposição em PUBLICATION.json é already_corrected, com a prova "Front queries.ts:145 e Serve ch.py:385 usam indexed para produzir -1 na ausência. Sem nova issue; leitura estática não prova runtime."

### Intenção e benefício

Intenção: evitar que a Console mostre zero medido para um run que a memória nunca indexou (o LEFT JOIN numa coluna não-Nullable preenche 0 e o ifNull(...,-1) nunca dispara). Público: quem lê task_time_ms na Console. Ganho: nenhum zero alegando medição inexistente.

### Feito, faltante e não comprovado

A premissa antiga foi superada no código c3c3ea3: Front queries.ts e Serve ch.py usam indexed para gerar -1 quando não há run_outcomes; repository.ts converte valor negativo em null. O recorte Git #153 registra 31f16ff de 29/09 e merge c9c35cf de 06/10, ancestral da base. A disposição already_corrected é consistente com esse recorte; não é prova de renderização.

### Linhagem

Linhagem: gap 1 do corpo da #129 → registro S01 → commit 31f16ff (29/09) → PR #153 → merge c9c35cf (06/10) → minuta P-S01 (11/10, ainda com a premissa antiga) → disposição already_corrected. A minuta foi escrita depois da correção sem percebê-la; a triagem pegou.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/P-S01.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/front__src__data__queries.ts.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_mcp__ch.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/front__src__data__repository.ts.txt; fontes/batch-claude-history-sources/claude/fontes/git/PR_153.txt. Locadores: Minuta/disposição, queries 110/145, ch 364/385, notIndexed e histórico #153.

### Classe e limite da evidência

FATO OBSERVADO: projeção indexed, mapeamento notIndexed e histórico de integração #153. RELATO: reprodução do problema no head antigo. Nenhuma execução de SQL/browser nesta revisão.

### Fluxo

Fluxo estático atual: miss no LEFT JOIN → indexed sem correspondência → SQL projeta -1 → notIndexed converte para null no repository. Render correto é garantia posterior a verificar no consumidor, não observação desta leitura.

### Consequências e risco

Não há razão documental para abrir a mesma correção de SQL novamente. A evidência estática sustenta encerrar a minuta obsoleta, preservando prova de comportamento de UI em seu escopo próprio.

### Alternativas e recomendação

Recomendado: manter a disposição already_corrected e encerrar a minuta. Alternativa: prova runtime pequena da ausência na Console, que pertence a S04/#172. Reversível.

### Dependências e paralelismo

Nenhuma dependência. A eventual prova runtime da ausência na Console pertence a S04/#172 e não reabre esta disposição; a correção não depende de #117 nem da decisão de token.

### Plano e aceite propostos

Condição de não ação: não publicar a minuta. Nota consolidada com o commit 31f16ff (29/09) e a PR #153 (merge c9c35cf em 06/10) como origem da correção do zero falso.

### Comunicação entre responsáveis

Para outro pod: "O zero falso de task_time_ms já foi corrigido pela PR #153 (commit 31f16ff); a minuta P-S01 foi escrita depois e não precisa virar issue."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Trocar ausência por zero medido volta a confundir dado inexistente com medição; reabrir a mesma correção duplicaria trabalho integrado. Que caso o teste ainda não cobre? Não executamos SQL com join_use_nulls/perfil identificado ou render da Console; esses limites não apagam a correção estática. Como eu explicaria isso para outro pod? P-S01 nasceu com premissa antiga; indexed/-1/null já estão integrados no recorte, e a UI é outra camada de prova.

### Próxima ação e encerramento

Próxima ação documental concluída: registrar already_corrected com 31f16ff/#153 e mapeamento de ausência. Nenhum produto ou estado público alterado.

