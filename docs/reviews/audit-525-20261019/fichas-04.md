# Fichas documentais — lote 4

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-031"></a>

## #178 — [Feature][Pod 2 / Harness] Respeitar o endpoint OTLP escolhido nos alvos de patologia

Frente: harness_configuracao. Encaminhamento: implementacao_delimitada_e_prova_offline.

### Identidade e estado

#178 — [Feature][Pod 2 / Harness] Respeitar o endpoint OTLP escolhido nos alvos de patologia. Autor gustocezar; sem assignee; aberta na consulta de 16/10/2026 18:29:24 UTC. O assignee histórico não ratifica owner ou prazo para a próxima entrega. Corte técnico c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Garantir que o endpoint OTLP escolhido pelo operador chegue à configuração Spark dos alvos de patologia, preservando o default quando não há override. Beneficia a reprodução em ambientes com mais de um Collector.

### Feito, faltante e não comprovado

run-pathology propaga AQE/FIX/SAFE, mas não endpoint; c3/c4 passam endpoint literal por --conf, e spark-defaults também fixa o default. Inspeção adicional: build_session e skew_join lidos não traduzem APEX_OTLP_ENDPOINT para Spark; e2e_canonical.sh traduz a variável em --conf, porém antes a redefine com literal. Logo, só acrescentar -e no launcher não demonstra propagação completa nesses caminhos.

### Linhagem

L09 → PROP-L09-HARN-BINDING → #178. Não é E16/#167 (binding de parâmetros R9D), E08/#174 (preservação de arquivo) ou E09/#175 (ownership). O vínculo L09→E09 na ficha Claude era preferência ampliada; o corpo público declara que testar propagação independe de escolher toda a identidade da stack.

### Fontes e corte

Fontes lidas: fontes/batch-public-sources/issue-178.md; fontes/current-open-issues.json; _build/input-registro.json; fontes/batch-public-sources/dev__Makefile.txt:78; fontes/batch-public-sources/dev__conf__spark-defaults.conf.txt:34; fontes/batch-public-sources/dev__scripts__e2e_canonical.sh.txt:38; fontes/batch-public-sources/dev__common__session.py.txt:31; fontes/batch-public-sources/dev__jobs__skew_join.py.txt:32. Corpos/comentários preservados do snapshot 16/10/2026; código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Recibos de código em batch-public-sources/*.json preservam URL e observed_at; não atualizam o estado das issues. Linhas citadas usam os arquivos .txt/.md correspondentes.

### Classe e limite da evidência

FATO OBSERVADO: comandos/defaults e consumidores específicos lidos. INFERÊNCIA: override ignorado pode levar telemetria a um destino distinto do pretendido; nenhuma entrega OTLP foi observada. PROPOSTA: precedência única e teste do comando final. Não afirmar suporte da variável em todos os jobs: somente skew_join/factory e runner shell foram inspecionados.

### Fluxo

Override explícito/default → resolução no launcher → argumento spark.apex.otlp.endpoint de spark-submit → plugin → Collector. As três primeiras etapas devem ser verificáveis offline; envio/ingestão são prova runtime separada. Injetar ambiente sem consumo não completa a seta.

### Consequências e risco

Override perdido pode confundir diagnóstico entre stacks; um escape incorreto também pode alterar o comando. Alta confiança no literal/ausência de forwarding citados, sem incidente ou vazamento de telemetria observado. A solução não autentica nem estabelece ownership do Collector.

### Alternativas e recomendação

Recomendo resolver endpoint uma vez e usar a interface --conf já presente nos alvos, com default compatível. Alternativa: variável consumida por factory/job, desde que todos os caminhos acordados a traduzam; passar variável sem consumidor é insuficiente. Evitar duplicar precedência em cada alvo; a escolha exata deve respeitar contrato e escaping existentes.

### Dependências e paralelismo

Owner Harness decide alvos e precedência. Teste offline pode avançar em paralelo a #175 e #167/#174; a política completa de identidade não é gate técnico. Prova futura de entrega exige endpoint próprio e cenário de runtime, sem ampliar esta PR para Collector ou nomes de stack.

### Plano e aceite propostos

Inventariar run-pathology e cada c3/c4 afetado; definir default/override e tratamento de vazio; implementar forwarding até --conf; testar comando final com/sem override e caracteres/caminhos válidos; controle negativo remove o endpoint e deve falhar. Não usar make -n como isolamento automático: o Makefile tem $(shell docker network inspect ...) na linha 7, avaliado durante expansão; desenhar controle que substitua esse acesso. Aceite: comando renderizado preserva escolha/default sem executar Docker ou enviar OTLP; documentação separa propagação de entrega.

### Comunicação entre responsáveis

Explicar a cadeia host→launcher→Spark e mostrar argv/configuração sanitizada. Não apresentar teste de string ou ambiente como prova de ingestão. Documentar alvos excluídos para evitar promessa universal.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Passar -e no launcher sem um consumidor que traduza APEX_OTLP_ENDPOINT para spark.apex.otlp.endpoint não muda nada, e e2e_canonical.sh ainda redefine a variável com literal antes de traduzi-la. Que caso o teste ainda não cobre? — Os alvos c3 e c4 têm endpoint literal próprio e o spark-defaults também fixa o default; testar o comando renderizado com make -n aciona o $(shell docker network inspect) da linha 7 do Makefile. Como eu explicaria isso para outro pod? — A cadeia é override ou default, resolução no launcher, --conf do spark-submit, plugin e Collector; a prova offline cobre até o comando final, e a entrega OTLP é recibo separado.

### Próxima ação e encerramento

Owner Pod 2/Harness a confirmar: entrada Makefile/defaults e precedência acordada; saída PR pequena com comando final e controle negativo. Encerrar a implementação após review/integração e prova offline acordada; entrega OTLP fica em recibo próprio, sem condicionar tudo à decisão #175.

<a id="item-032"></a>

## #179 — [Study][Pod 1 / Verify] Avaliar trabalho medido e fallback estimado no predictor

Frente: verify_modelagem. Encaminhamento: correcao_documental_e_estudo_de_modelo.

### Identidade e estado

#179 — [Study][Pod 1 / Verify] Avaliar trabalho medido e fallback estimado no predictor. Autor gustocezar; sem assignee; aberta na consulta de 16/10/2026 18:29:24 UTC. O assignee histórico não ratifica owner ou prazo para a próxima entrega. Corte técnico c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Distinguir trabalho medido, estimado e indisponível no predictor e remover a justificativa interna obsoleta de que a coluna não existe. O benefício é explicar de onde vem W sem transformar executor runtime automaticamente em duração do job.

### Feito, faltante e não comprovado

Confirmei afirmações obsoletas em models:38–40, predict:19–21 e mensagem:158. A migração 039 define executor_run_time_ms DEFAULT 0 e Engine usa coluna positiva ou Map histórico. Verify continua estimando W; a presença da coluna não prova migração aplicada ou adequação ao modelo. #164 corrige README em PR própria, não esses pontos. O teste da matriz exige literalmente a frase obsoleta em models:166 do arquivo de teste.

### Linhagem

L10 → PROP-L10-VERIFY-RUNTIME → #179; CL-02 é candidato de correção textual, distinto do estudo de medição. #142 trata população, #164 README, #162 identidade de versão e #117 contrato de piso/atribuição. Nenhuma dessas relações demonstra que versão altere linhas persistidas ou que a medição já seja consumida por Verify.

### Fontes e corte

Fontes lidas: fontes/batch-public-sources/issue-179.md; fontes/current-open-issues.json; _build/input-registro.json; fontes/main-verify-models.txt:38; fontes/main-predict.txt:19; fontes/batch-public-sources/infra__sql__039_executor_runtime_additive.sql.txt:5; fontes/main-clickhouse.txt:83; fontes/batch-public-sources/tests__test_telemetry_compatibility_matrix.py.txt:166; fontes/pr164__verify_README.md.patch.txt. Corpos/comentários preservados do snapshot 16/10/2026; código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Recibos de código em batch-public-sources/*.json preservam URL e observed_at; não atualizam o estado das issues. Linhas citadas usam os arquivos .txt/.md correspondentes.

### Classe e limite da evidência

FATO OBSERVADO: discrepância texto/DDL/leitura Engine e asserção estática presa à frase. RELATO HISTÓRICO: candidato CL-02 cobre predict, conforme auditoria Parte03, sem reinspeção do patch local aqui. INFERÊNCIA a estudar: runtime agregado pode ou não representar W para a mesma população. PROPOSTA: correção editorial separada de escolha matemática.

### Fluxo

Coluna/Map (valor e proveniência) + população/unidades → seleção measured/estimated/unavailable a decidir → limite de makespan → previsão com incerteza. Hoje o predictor calcula estimativa; não há seta de consumo medido certificada nesta ficha.

### Consequências e risco

Texto falso pode desviar manutenção; usar zero histórico como medição ou somar população incompatível pode distorcer a previsão. Confiança alta na contradição documental; sem validação empírica de um novo modelo. Executor runtime agregado não é automaticamente wall-clock do job.

### Alternativas e recomendação

Recomendo corrigir as três afirmações preservando a explicação de que Verify atualmente estima. Em paralelo comparar manter estimativa, usar medição quando qualificada ou combinar bounds; escolher conforme unidade/população/proveniência. Corrigir só README não resolve os textos internos; substituir W diretamente amplia risco e precisa decisão.

### Dependências e paralelismo

Owner Verify/modelo decide semântica de W e fallback; estudo pode correr em paralelo a #117/#162/#164. Há coordenação de teste com #180: alterar a asserção literal para refletir a nova fonte, preservando a evidência histórica, sem esperar toda a matriz nova. Não criar dependência técnica de versão #162.

### Plano e aceite propostos

Primeira entrega: atualizar models e duas ocorrências predict, com teste da mensagem e ajuste da guarda de matriz; não mudar fórmula. Estudo seguinte: mapear soma/unidade/população, casos coluna válida, zero histórico com/sem Map, inválido/ausente e successful-task; comparar estimativa/medição com controles. Aceite do estudo é decisão fundamentada e contrato de disponibilidade. Implementação de medição futura exige testes discriminantes e não pode chamar previsão de ganho certificado.

### Comunicação entre responsáveis

Explicar separadamente coluna declarada, migração aplicada, dado útil e consumo do predictor. Na PR textual, declarar que fórmula e resultados não mudam. Na decisão de modelo, registrar como desconhecido difere de zero.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Tratar o zero histórico de executor_run_time_ms (DEFAULT 0) como trabalho medido distorceria W, e usar runtime agregado como duração do job confundiria trabalho com wall-clock. Que caso o teste ainda não cobre? — Não se sabe se o p50 e o runtime agregado vêm da mesma população; o teste da matriz ainda exige literalmente a frase obsoleta de models.py, e nenhum novo modelo foi validado. Como eu explicaria isso para outro pod? — Coluna declarada, migração aplicada, dado útil e consumo pelo predictor são etapas distintas; hoje o Verify estima W, e saber se o valor medido representa exatamente esse W é a pergunta do estudo.

### Próxima ação e encerramento

Owner Verify a confirmar: entrada três trechos obsoletos, DDL e guarda estática; saída pequena correção textual revisada, seguida de estudo com decisão measured/estimated/unavailable. Encerrar o texto após integração; manter estudo aberto até decisão, sem exigir implementação se a conclusão for manter estimativa.

<a id="item-033"></a>

## #180 — [Docs][Cross-pod] Atualizar cobertura da matriz para Front, API e proveniência

Frente: arquitetura_e_proveniencia. Encaminhamento: atualizacao_documental_com_guarda_estatica.

### Identidade e estado

#180 — [Docs][Cross-pod] Atualizar cobertura da matriz para Front, API e proveniência. Autor gustocezar; gustocezar; aberta na consulta de 16/10/2026 18:29:24 UTC. O assignee histórico não ratifica owner ou prazo para a próxima entrega. Corte técnico c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Oferecer visão atual de produtores, transportes e consumidores com proveniência por campo, mantendo o corte histórico e diferenciando declaração de observação estática e prova runtime.

### Feito, faltante e não comprovado

A matriz preservada declara base 847d7a0, Front absent/external e offline_unproven; a fonte atual tem tipos Front e rotas API que chamam ReadStore. Front declara CONTRACT_VERSION 0.5 e contrato central v0.6, sem incompatibilidade runtime demonstrada. RunSummary mantém wall_clock_ms nullable; o rollup do store parte de spark_events e usa run_outcomes para dados de shape, não duração total. Comentários relatam seis linhas de proveniência revisadas, não prova de emissão/persistência.

### Linhagem

L13 → PROP-L13-MATRIX-UPDATE → #180, com L14 absorvido explicitamente no inventário de três superfícies. #103/#111/#121 entregaram a matriz anterior e não são reabertas. #106/#108/#109 tratam graph/views/reconciliação; #78 ledger fechado é outro escopo. Estudos de 11/10 são insumo histórico, não voto de Kimi para aprovação.

### Fontes e corte

Fontes lidas: fontes/batch-public-sources/issue-180.md; fontes/current-open-issues.json; _build/input-registro.json; fontes/batch-public-sources/docs__architecture__TELEMETRY-COMPATIBILITY-MATRIX.md.txt:3; fontes/batch-public-sources/docs__architecture__TELEMETRY-COMPATIBILITY-MATRIX.md.txt:180; fontes/batch-public-sources/tests__test_telemetry_compatibility_matrix.py.txt:16; ../parte-02-gemini/evidencias/escopos/types-ts.txt:8; ../parte-02-gemini/evidencias/escopos/types-ts.txt:284; fontes/batch-public-sources/serve__src__apex_api__routes__resources.py.txt:39; fontes/lote2-serve__src__apex_mcp__ch.py.txt:330. Corpos/comentários preservados do snapshot 16/10/2026; código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Recibos de código em batch-public-sources/*.json preservam URL e observed_at; não atualizam o estado das issues. Linhas citadas usam os arquivos .txt/.md correspondentes.

### Classe e limite da evidência

FATO OBSERVADO: base declarada da matriz, tipos/rotas/query e testes estáticos. RELATO HISTÓRICO: seis linhas propostas e revisão anterior nos comentários. INFERÊNCIA: uma visão antiga lida como atual induz erro; não é regressão do produto. PROPOSTA: visão atual versionada com status por evidência. L14 não vira quatro novas implementações por ausência no inventário.

### Fluxo

Contrato e blobs na ref → inventário produtor/transportador/consumidor → matriz atual por campo; recibos de execução identificados → coluna de prova runtime, sem substituir lacuna por seta. Três superfícies × Front/API: status/duração, ambiente e decisões Memory; cada uma exige origem, unidade, transformação e ausência.

### Consequências e risco

Transferir uma declaração de 847d7a0 ao código atual pode apagar Front/API ou prometer integração pela mera query. Alta confiança no descompasso temporal; não se pode concluir incompatibilidade só por 0.5 versus v0.6 aditivo. Promover ausência de campo a requisito automático ampliaria backlog indevidamente.

### Alternativas e recomendação

Recomendo versão atual separada com link à histórica e um manifesto único para seu corte. Alternativa: versionar seções com datas/refs no mesmo documento; duplicar matrizes sem regra de atualização cria novas divergências. Manter histórico intacto é compatível com corrigir a visão corrente; não substituir tudo por system graph ou ledger.

### Dependências e paralelismo

Contribuições dos owners Front/API/Memory e mantenedor do contrato. Pode avançar em paralelo aos estudos; depende apenas das fontes para cada afirmação. Ajustes #165/#179 precisam coordenar asserções literais do teste, mas não aguardar toda esta entrega. Follow-ups devem ser reconciliados com #106/#108/#109/#117, sem duplicar IDs.

### Plano e aceite propostos

Definir ref da visão atual; registrar Front/API e rotas/store; completar seis linhas das três superfícies com producer, consulta, unidade e status declared/observed/absent/optional/offline_unproven; preservar fontes históricas. Atualizar teste para detectar aresta omitida e promoção indevida a runtime, mantendo controles de ownership/serialização. Revisar asserções que fixam PROPOSED e a frase obsoleta de Verify para não impedir correções legítimas. Aceite: toda afirmação atual tem fonte e limite; ausência classificada não cria implementação automaticamente.

### Comunicação entre responsáveis

Explicar que se atualiza o mapa, não se comprova interoperabilidade nem se reabre #111. Mostrar diferença entre status de saúde derivado e conclusão real de job, duração de shape e duração de job, configuração capturada e identidade do ambiente. Nomear L14 como origem preservada/absorvida.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Substituir a base histórica 847d7a0 pela atual sem registrar a mudança apagaria o corte declarado, e ler a matriz antiga como atual esconde Front e API. Que caso o teste ainda não cobre? — A guarda estática ainda não detecta aresta Front/API omitida nem promoção indevida de declaração a prova runtime, e fixa PROPOSED e a frase obsoleta do Verify. Como eu explicaria isso para outro pod? — Atualizar o mapa não comprova interoperabilidade nem reabre a #111; cada ausência é classificada como lacuna intencional ou destino de follow-up, sem virar implementação automática.

### Próxima ação e encerramento

Owners cross-pod a confirmar: entrada matriz histórica, blobs e seis linhas de estudo; saída visão atual e guarda estática revisadas. Encerrar após integrar atualização com cobertura das três superfícies e destinos explícitos para lacunas; preservar L14 agrupado, sem novo estudo duplicado.

<a id="item-034"></a>

## G01 — Restaurar GitHub Actions da conta luanmorenommaciel

Frente: Governança/CI. Encaminhamento: DECIDIR_OPERACAO_E_PROVA_ATUAL.

### Identidade e estado

ID original G01; título: Restaurar GitHub Actions da conta luanmorenommaciel; tipo de origem: operação externa; pod: Governança/CI; responsável para o próximo passo: responsável por Governança/CI, a confirmar; nenhuma atribuição feita nesta revisão. Objetos públicos: issue #130: open; autoria pública gustocezar; assignees nenhum no snapshot. Destino consolidado: DECIDIR_OPERACAO_E_PROVA_ATUAL. O autor público não é automaticamente assignee ou aprovador.

### Intenção e benefício

Restabelecer e demonstrar a execução efetiva do CI usado pelo time. O problema original era billing impedindo jobs; contribuidores e mantenedor precisam distinguir falha antes de steps de teste que realmente falhou.

### Feito, faltante e não comprovado

A #130 permanece aberta. No SHA c3c3ea3, a consulta direcionada registra CI push 37831091789 e JAR push 37831091718 falhos, mas JAR agendado 38266693976 verde. A #162 também tem três checks verdes no head publicado. Há capacidade hospedada parcial observada; não se demonstrou bloqueio universal atual nem CI principal verde na main nesse conjunto. Billing atual é questão operacional a confirmar.

### Linhagem

G01 → acompanhamento #130. PRs #126/#127/#128 são exemplos históricos de runs sem steps, não implementações de billing. A regularização financeira não tem PR de produto; o elo relevante é decisão do titular → execução identificada → logs por suíte → avaliação de cada mudança. Elos de revisão formal, execução independente ou aceite funcional não citados nesta ficha permanecem não verificados; não se infere ausência a partir de falta de Closes.

### Fontes e corte

Fontes confrontadas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json#/rows/0; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv#[id=G01]; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/BACKLOG-LEARNING.json#[id=G01]; ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md:8; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json#[number=130]; fontes/current-open-issues.json#[number=130]; observed_at=2026-10-16T18:29:24.609Z; fontes/runs-current-main.json; fontes/pr162-checks.json; fontes/main-workflow.txt. Base de referência de código APEX: c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. O CSV e BACKLOG-LEARNING preservam seu corte histórico; não são leitura do estado atual. A ficha Claude é proposta de partida, não validação independente.

### Classe e limite da evidência

FATO OBSERVADO: leitura dos metadados, textos e trechos estáticos expressamente citados nos campos 3–5. RELATO HISTÓRICO do registro, sem reexecução: direct_static: anotações de 99 check-runs via API em 2026-09-24; gustocezar/apex-workspace PR #4 teve gate SUCCESS (billing da outra conta funciona); delta 2026-09-29: direct_static: REMOTE-SNAPSHOT.json da Lane A (2026-09-30T01:51Z (2026-09-29 22:51 BRT)). INFERÊNCIA: consequências possíveis do campo 8, com os limites ali indicados. PROPOSTA: alternativas, plano e próximos passos desta ficha. DECISÃO PENDENTE: escolhas de escopo/owner indicadas nos campos 9–10. Teste local, CI por SHA, integração e aprovação humana não são intercambiáveis; nenhuma execução de produto foi feita nesta revisão.

### Fluxo

Fluxo observado no corte histórico: solicitação de run → GitHub Actions → verificação da conta → jobs recusados sem steps. Fluxo proposto agora: titular confirma condição operacional → run em ref identificada → steps/logs → evidência de cada suíte. O JAR verde retorna prova apenas do JAR.

### Consequências e risco

Se a interrupção voltar, PRs poderão ficar sem prova hospedada; se um vermelho sem steps for interpretado como falha de código, a equipe pode alterar código sem diagnóstico. São riscos condicionais; os verdes posteriores impedem afirmar indisponibilidade geral persistente.

### Alternativas e recomendação

Conferir cobrança/limite com o titular e pedir execução identificada é o menor caminho. Aumentar orçamento só se a causa confirmada o exigir. Runner próprio é alternativa com custo de operação e segurança, não escolha automática. Manter exigências proporcionais e não confundir dispensa de CI com restauração.

### Dependências e paralelismo

Decisão operacional do titular da conta; definição dos checks exigidos em G02. Estudos e revisão documental podem seguir em paralelo. Não há dependência técnica universal de todo backlog em G01: cada PR conserva seu resultado por SHA e workflow.

### Plano e aceite propostos

1) Conciliar os runs posteriores com os critérios históricos de #130. 2) Registrar se falta regularização ou apenas prova do CI principal na ref alvo. 3) Quando houver execução autorizada, guardar workflow, SHA, runner, steps, logs e resultados por suíte. Controle discriminante: job sem runner/steps não satisfaz execução; JAR isolado não satisfaz Front/Python/root. Encerrar a pendência operacional com confirmação do titular e critérios de #130 atendidos ou atualizados pelo mantenedor. O corpo original de #130 exige reruns específicos de #126–#128. Substituí-los por CI na main é proposta de reconciliação após os merges, não critério já ratificado; registrar atendimento ou alteração explícita pelo mantenedor.

### Comunicação entre responsáveis

Na minuta para #130, explicar a sequência de falha histórica e sucessos posteriores, apontar quais suítes ainda carecem de evidência no SHA escolhido e evitar dizer que todas as PRs estão bloqueadas. Registrar a política operacional sem expor dados financeiros.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Um JAR verde poderia ser tomado por prova de todas as lanes. Que caso o teste ainda não cobre? CI principal na main neste conjunto de runs. Como eu explicaria isso para outro pod? Disponibilidade do runner e aprovação do código são verificações separadas.

### Próxima ação e encerramento

Titular da conta e mantenedor, a confirmar: usar #130 e os três runs de c3c3ea3 como entrada; produzir nota de estado operacional e requisito de prova por workflow. Saída verificável: reconciliação datada; encerramento condicionado aos critérios explícitos, sem nova execução nesta auditoria.

<a id="item-035"></a>

## G02 — Proteger main com PR obrigatório, checks e política de bypass

Frente: Governança/CI. Encaminhamento: DECIDIR_POLITICA_DE_PROTECAO.

### Identidade e estado

ID original G02; título: Proteger main com PR obrigatório, checks e política de bypass; tipo de origem: decisão/configuração; pod: Governança/CI; responsável para o próximo passo: responsável por Governança/CI, a confirmar; nenhuma atribuição feita nesta revisão. Objetos públicos: issue #125: open; autoria pública gustocezar; assignees nenhum no snapshot. Destino consolidado: DECIDIR_POLITICA_DE_PROTECAO. O autor público não é automaticamente assignee ou aprovador.

### Intenção e benefício

Transformar a política de integração em regra verificável: PR, checks e revisão conforme decisão do mantenedor. O público é quem contribui e mantém a main; a proteção reduz entradas sem a evidência exigida, sem certificar runtime ausente dos checks.

### Feito, faltante e não comprovado

A #125 está aberta; a captura de branch reporta protected=false. O workflow atual tem três jobs principais e ignora docs/Markdown/JAR no CI geral; JAR tem workflow próprio. Os onze contextos históricos não são a configuração atual a exigir. A regra desejada de bypass e aprovações não foi escolhida nesta auditoria.

### Linhagem

G02 → issue #125 → decisão de política do administrador → configuração GitHub → controles de PR → aceite do mantenedor. G07/#148 corrige o alcance descrito do CI; #160 mudou os jobs. #21 trata análise automatizada de código e não substitui esta governança. Elos de revisão formal, execução independente ou aceite funcional não citados nesta ficha permanecem não verificados; não se infere ausência a partir de falta de Closes.

### Fontes e corte

Fontes confrontadas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json#/rows/1; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv#[id=G02]; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/BACKLOG-LEARNING.json#[id=G02]; ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md:43; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json#[number=125]; fontes/current-open-issues.json#[number=125]; observed_at=2026-10-16T18:29:24.609Z; fontes/current-branch.json; fontes/main-workflow.txt. Base de referência de código APEX: c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. O CSV e BACKLOG-LEARNING preservam seu corte histórico; não são leitura do estado atual. A ficha Claude é proposta de partida, não validação independente.

### Classe e limite da evidência

FATO OBSERVADO: leitura dos metadados, textos e trechos estáticos expressamente citados nos campos 3–5. RELATO HISTÓRICO do registro, sem reexecução: reported: corpo da #125 (protected=false em 2026-09-19); direct_static: ci.yml define 11 contextos estáveis. INFERÊNCIA: consequências possíveis do campo 8, com os limites ali indicados. PROPOSTA: alternativas, plano e próximos passos desta ficha. DECISÃO PENDENTE: escolhas de escopo/owner indicadas nos campos 9–10. Teste local, CI por SHA, integração e aprovação humana não são intercambiáveis; nenhuma execução de produto foi feita nesta revisão.

### Fluxo

Fluxo proposto: PR e resultados de checks → regra de proteção/ruleset → autorização ou recusa de merge. O administrador define os contextos e o bypass; a configuração retorna a política efetiva. Um check que nunca é disparado por paths-ignore requer tratamento explícito.

### Consequências e risco

Exigir um contexto ausente pode bloquear PR só documental; permitir bypass amplo ou não exigir revisão pode manter o risco que #125 busca reduzir. Confiança alta no problema de alinhamento de triggers; não há incidente de merge indevido demonstrado aqui.

### Alternativas e recomendação

Ruleset ou branch protection podem expressar a política, conforme recursos e preferência do administrador. Um check sentinela obrigatório pode dar resultado estável para docs; exigir jobs condicionais sem desenho adicional pode ficar pendente indefinidamente. Aprovações e bypass devem ser escolhidos explicitamente e podem ser revistos.

### Dependências e paralelismo

Administrador com permissão de configuração; lista atual de contextos e seus triggers; disponibilidade de execução para os controles. G01 informa capacidade operacional, mas os verdes já existentes devem ser considerados. Não depende de implementar o bot #21.

### Plano e aceite propostos

1) Elaborar matriz tipo de PR→workflow esperado→contexto exigido. 2) Decidir reviews, stale approvals, conversas, force-push/deleção e bypass. 3) Preparar regra revisável. 4) Após configuração autorizada, controlar PR com check faltante, falho e verde, incluindo docs-only e JAR-only. Aceite: estado de proteção consultável e os caminhos permitidos/bloqueados correspondem à decisão; documentar recuperação após bypass.

### Comunicação entre responsáveis

Explicar na #125 por que os nomes do CI antigo foram substituídos, como docs e JAR se comportam e que proteção de branch não prova integração de Spark/ClickHouse. A minuta precisa listar quem pode usar o bypass e quando.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Um job ignorado por caminho poderia bloquear documentos. Que caso o teste ainda não cobre? A configuração efetiva e os caminhos de bypass. Como eu explicaria isso para outro pod? A regra exige evidências nomeadas antes de permitir integração.

### Próxima ação e encerramento

Administrador e mantenedor, a confirmar: entrada é o workflow c3c3ea3 e critérios de #125; saída é proposta concreta de regra com matriz de controles. Encerrar após decisão, configuração e evidência de PRs positiva/negativa, não pela simples existência da minuta.

<a id="item-036"></a>

## G03 — Revisar e reduzir a fila #126–#134

Frente: Governança/Fila. Encaminhamento: ENCERRAR_FILA_HISTORICA_COM_FOLLOWUP_SEPARADO.

### Identidade e estado

ID original G03; título: Revisar e reduzir a fila #126–#134; tipo de origem: revisão; pod: Governança/Fila; responsável para o próximo passo: responsável por Governança/Fila, a confirmar; nenhuma atribuição feita nesta revisão. Objetos públicos: PR #126: integrada em 2026-10-06T19:55:46Z; autoria pública gustocezar; assignees nenhum no snapshot; PR #127: integrada em 2026-10-06T19:56:00Z; autoria pública gustocezar; assignees nenhum no snapshot; PR #128: integrada em 2026-10-06T19:56:14Z; autoria pública gustocezar; assignees nenhum no snapshot; PR #129: integrada em 2026-10-06T19:56:50Z; autoria pública sidymar; assignees nenhum no snapshot; PR #131: integrada em 2026-10-06T19:56:20Z; autoria pública gustocezar; assignees nenhum no snapshot; PR #132: integrada em 2026-10-06T20:18:13Z; autoria pública gustocezar; assignees nenhum no snapshot; PR #133: integrada em 2026-10-06T20:19:24Z; autoria pública gustocezar; assignees nenhum no snapshot; PR #134: integrada em 2026-10-06T20:18:19Z; autoria pública gustocezar; assignees nenhum no snapshot. Destino consolidado: ENCERRAR_FILA_HISTORICA_COM_FOLLOWUP_SEPARADO. O autor público não é automaticamente assignee ou aprovador.

### Intenção e benefício

Reduzir a antiga fila sobre a289e53 sem perder a separação entre composição textual, semântica e revisão humana. A utilidade atual deste ID é explicar aquela integração e impedir que sua ordem histórica seja aplicada à nova fila.

### Feito, faltante e não comprovado

As oito PRs nomeadas foram integradas em 06/10; o snapshot preservado contém os merges. A afirmação da triagem de que foram integralmente revisadas não é demonstrada pelo estado merged. A fila atual é outra: #155, #157–#159, #161–#164, com bases, checks e revisão próprios.

### Linhagem

G03 → fila #126–#134 e desdobramentos históricos → merges observados. Os relatos de merge-tree e suites locais são evidência histórica delimitada. Relação com NOV-03: sucessor de revisão da fila atual, não continuação dos mesmos heads. Review formal dos merges antigos não foi consultado neste lote. Identidades preservadas do snapshot público: #126: head 4ddb082cf8e916736e336d6a5554bccbba083a19, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge abed50893977e14dcf70ffdc4274e70793b76030; #127: head 4e44bfdce5586fe9b8ed7c96e41932b55f231a88, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge fec8a7fb0b3669343725141ab60eef0d8dff74a0; #128: head 2b84c7a14fbcc5c009a3366536ccb80ebe316ca0, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge d8c1a3c67948c047ea282ca4d839462153b4e60a; #129: head fab662080da499df5d2d4b563ad68be7ddc4cc9f, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge 83a9624bce6247417728f635d4e57e5b0e8559ac; #131: head 7b7b9b41aafa9b6fd3d45513ec7a8f394f9318fc, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge e8672329825105b4ee1ef7ab20f5338cc955929b; #132: head 1f3c2745605184d79d1dbbec73977160005b1420, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge ee8820b62703f765b6a5da14bd0068db52b937f3; #133: head 5cd5968c8cd9a1901fcc60db446dab1c8f9a7226, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge 663f04c6fc7207aaf9e11e9329176254062f72db; #134: head 3340e2fafce06605ecc89dd4836703b2f4d3c275, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge b7afeaeed5d81219e1fc35ea6b76696052a1a10d. Elos de revisão formal, execução independente ou aceite funcional não citados nesta ficha permanecem não verificados; não se infere ausência a partir de falta de Closes.

### Fontes e corte

Fontes confrontadas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json#/rows/2; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv#[id=G03]; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/BACKLOG-LEARNING.json#[id=G03]; ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md:78; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json#[number=126]; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json#[number=127]; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json#[number=128]; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json#[number=129]; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json#[number=131]; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json#[number=132]; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json#[number=133]; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json#[number=134]; fontes/current-open-pulls.json. Base de referência de código APEX: c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. O CSV e BACKLOG-LEARNING preservam seu corte histórico; não são leitura do estado atual. A ficha Claude é proposta de partida, não validação independente.

### Classe e limite da evidência

FATO OBSERVADO: leitura dos metadados, textos e trechos estáticos expressamente citados nos campos 3–5. RELATO HISTÓRICO do registro, sem reexecução: derived: merge-tree limpo em todos os 28 pares e na fusão sequencial 131→126→128→127→129→132→134→133 (clone de trabalho temporário, 2026-09-24). INFERÊNCIA: consequências possíveis do campo 8, com os limites ali indicados. PROPOSTA: alternativas, plano e próximos passos desta ficha. DECISÃO PENDENTE: escolhas de escopo/owner indicadas nos campos 9–10. Teste local, CI por SHA, integração e aprovação humana não são intercambiáveis; nenhuma execução de produto foi feita nesta revisão.

### Fluxo

Fluxo histórico: heads candidatos → composição textual local → revisão/decisão de integração → main. Fluxo documental atual: recibos de merge → visão derivada datada → encerramento da fila antiga; novos heads → fichas próprias da fila atual.

### Consequências e risco

Reutilizar a ordem antiga criaria bloqueios artificiais e confundiria resultados de outras árvores. Chamar merge de review completo atribuiria aprovação não verificada. O risco é de decisão documental errada; não demonstra regressão executada.

### Alternativas e recomendação

Recomendado: encerrar o escopo histórico na visão derivada e remeter a nova fila. Reabrir o mesmo ID para toda PR futura elimina o corte de comparação. Auditar reviews antigos é opção se houver pergunta específica de governança; não é gate retroativo automático.

### Dependências e paralelismo

Nenhuma dependência técnica nova para catalogar os merges. A atualização da visão deriva de X09/L12; a nova fila possui dependências próprias, especialmente #157/#163. Preservar o CSV histórico sem reescrevê-lo.

### Plano e aceite propostos

Conferir IDs e identidades de merge das oito PRs; anotar que revisão formal e aceite de suites não são deduzidos do merge; relacionar os follow-ups de runtime/consumidores. Aceite documental: G03 aparece como fila histórica encerrada e a fila atual está em destinos próprios, sem transferência de CI. Nenhum teste de produto novo é necessário para esse fechamento documental.

### Comunicação entre responsáveis

Explicar que a intenção de integrar aquela fila terminou administrativamente, enquanto provas e resíduos por componente continuam em seus IDs. Não editar o registro congelado nem anunciar revisão formal não localizada.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Dependências de setembro poderiam bloquear PRs de outubro sem motivo. Que caso o teste ainda não cobre? Reviews históricas e comportamento da main combinada não se deduzem do merge-tree. Como eu explicaria isso para outro pod? A fila antiga terminou; seus recibos não aprovam a nova.

### Próxima ação e encerramento

Curador da consolidação, a confirmar: registrar G03 encerrado nesta visão derivada e apontar NOV-03/fichas de PR atuais. Entrada: merges capturados; saída: mapa antigo→novo sem apagar origens. Encerramento documental satisfeito pelo vínculo, sem mudar custódia.

<a id="item-037"></a>

## G04 — Encerrar issues cobertas somente após merge (mapa corrigido)

Frente: Governança/Fila. Encaminhamento: RECONCILIAR_FECHAMENTO_POR_CRITERIO.

### Identidade e estado

ID original G04; título: Encerrar issues cobertas somente após merge (mapa corrigido); tipo de origem: governança; pod: Governança/Fila; responsável para o próximo passo: responsável por Governança/Fila, a confirmar; nenhuma atribuição feita nesta revisão. Objetos públicos: issue #95: closed; autoria pública gustocezar; assignees nenhum no snapshot; issue #115: open; autoria pública gustocezar; assignees nenhum no snapshot; issue #123: open; autoria pública gustocezar; assignees gustocezar; issue #124: open; autoria pública gustocezar; assignees nenhum no snapshot; PR #126: integrada em 2026-10-06T19:55:46Z; autoria pública gustocezar; assignees nenhum no snapshot; PR #127: integrada em 2026-10-06T19:56:00Z; autoria pública gustocezar; assignees nenhum no snapshot; PR #128: integrada em 2026-10-06T19:56:14Z; autoria pública gustocezar; assignees nenhum no snapshot; PR #131: integrada em 2026-10-06T19:56:20Z; autoria pública gustocezar; assignees nenhum no snapshot. Destino consolidado: RECONCILIAR_FECHAMENTO_POR_CRITERIO. O autor público não é automaticamente assignee ou aprovador.

### Intenção e benefício

Preservar a diferença entre contribuição de uma PR e atendimento integral da issue. Consumidores da atribuição, o gate tail-outlier e a cobertura de comandos têm critérios diferentes, embora as PRs tenham sido integradas na mesma rodada.

### Feito, faltante e não comprovado

#95 está fechada e #131 declara Closes #95. #115, #123 e #124 permanecem abertas. #126 entrega resolver offline e mantém #115 aberta. #127 documenta runtime local real, com limites de cold start/Windows; isso não significa ausência de runtime nem aceite atual integral. #128 declara routing e segurança sem mutação. Falta a decisão por critério de cada issue. Ressalva concreta de #124: o teste atual de todas as ações compara o texto Handler em -DryRun, que sai antes de executar &$actionPlan.Command; a prova separada de alcançar cada handler ainda está pendente. O mapeamento lido parece correto; não se afirma dispatcher trocado.

### Linhagem

G04 acompanha #95←#131 como fechamento explícito; #115↔#126 e #123↔#127/#124↔#128 como contribuições relacionadas. E02/E01 são remanescentes de consumidor/prova de #115; E17 trata endurecimento do gate sob #123. Ausência de Closes em #127/#128 não demonstra ausência de testes ou intenção de manter as issues para sempre. Identidades preservadas do snapshot público: #126: head 4ddb082cf8e916736e336d6a5554bccbba083a19, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge abed50893977e14dcf70ffdc4274e70793b76030; #127: head 4e44bfdce5586fe9b8ed7c96e41932b55f231a88, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge fec8a7fb0b3669343725141ab60eef0d8dff74a0; #128: head 2b84c7a14fbcc5c009a3366536ccb80ebe316ca0, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge d8c1a3c67948c047ea282ca4d839462153b4e60a; #131: head 7b7b9b41aafa9b6fd3d45513ec7a8f394f9318fc, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge e8672329825105b4ee1ef7ab20f5338cc955929b. Elos de revisão formal, execução independente ou aceite funcional não citados nesta ficha permanecem não verificados; não se infere ausência a partir de falta de Closes.

### Fontes e corte

Fontes confrontadas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json#/rows/3; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv#[id=G04]; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/BACKLOG-LEARNING.json#[id=G04]; ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md:98; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json#[number=95]; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json#[number=115]; fontes/current-open-issues.json#[number=115]; observed_at=2026-10-16T18:29:24.609Z; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json#[number=123]; fontes/current-open-issues.json#[number=123]; observed_at=2026-10-16T18:29:24.609Z; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json#[number=124]; fontes/current-open-issues.json#[number=124]; observed_at=2026-10-16T18:29:24.609Z; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json#[number=126]; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json#[number=127]; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json#[number=128]; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json#[number=131]; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/icomments_all.json; fontes/lote2-docs__e2e__TAIL_OUTLIER_RUNTIME_GATE.md.txt. Base de referência de código APEX: c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. O CSV e BACKLOG-LEARNING preservam seu corte histórico; não são leitura do estado atual. A ficha Claude é proposta de partida, não validação independente. Fonte adicional: fontes/lote2-tests__test_apex_initial_package.py.txt:55. Fonte adicional: fontes/lote2-scripts__apex.ps1.txt:734. Fonte adicional: fontes/lote2-scripts__apex.ps1.txt:785.

### Classe e limite da evidência

FATO OBSERVADO: leitura dos metadados, textos e trechos estáticos expressamente citados nos campos 3–5. RELATO HISTÓRICO do registro, sem reexecução: direct_static: closingIssuesReferences das PRs (só #131→#95); corpo da #126. INFERÊNCIA: consequências possíveis do campo 8, com os limites ali indicados. PROPOSTA: alternativas, plano e próximos passos desta ficha. DECISÃO PENDENTE: escolhas de escopo/owner indicadas nos campos 9–10. Teste local, CI por SHA, integração e aprovação humana não são intercambiáveis; nenhuma execução de produto foi feita nesta revisão.

### Fluxo

Fluxo de decisão: critério da issue → evidência com SHA/ambiente → classificação atendido, parcial ou não verificado → decisão do mantenedor. Merges fornecem estado de código; registros de runtime e testes fornecem provas diferentes; o fechamento retorna uma justificativa por critério.

### Consequências e risco

Fechar #115 só pelo resolver apagaria integração dos consumidores; rejeitar toda prova de #127 por ser histórica apagaria contribuição real. O risco é tanto fechamento sem evidência como repetição indevida de trabalho já comprovado.

### Alternativas e recomendação

Preparar checklist de critérios com remanescentes é preferível a fechar tudo por merge. O mantenedor pode manter a issue com checklist, desdobrar remanescentes ou encerrá-la com follow-up explícito. A escolha depende dos critérios públicos, sem exigir nova implementação por ausência de palavra-chave.

### Dependências e paralelismo

Leitura das fichas ISSUE-115/117/123/124 para o aceite técnico detalhado; responsável mantenedor a confirmar. Revisão de #124 pode avançar independentemente de E01; runtime de #123 conserva as condições da prova pretendida. Não há gate global de G01 para a análise documental.

### Plano e aceite propostos

Montar tabela critério→fonte→classe→SHA/data→lacuna para #115/#123/#124. Para #123 incluir os dois registros locais e separar fresh cold start, Windows e associação stage/snapshot. Para #124 mapear comando/dry-run/fail-closed sem presumir containers. Aceite: cada proposta de fechar, manter ou dividir explicita o critério atendido e destino de cada resíduo; decisão final do mantenedor. Para #124, manter pendente o critério público de alcançar cada handler até existir controle discriminante que altere Command preservando Handler e falhe, com stubs seguros sem Docker/secrets, ou decisão explícita do mantenedor alterando o escopo. CI verde não resolve essa lacuna de observação.

### Comunicação entre responsáveis

Na minuta de cada issue, mostrar o que a PR de fato entregou e qual requisito continua aberto. Citar runtime histórico como relato datado, sem dizer que stubs provam runtime ou que nunca houve execução real.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Um consumidor sem integração pareceria concluído ou uma prova válida seria apagada. Que caso o teste ainda não cobre? O cenário e a ref do critério remanescente. Como eu explicaria isso para outro pod? Fechar a issue exige reconciliar requisitos, não contar PRs.

### Próxima ação e encerramento

Mantenedor com donos de Engine/Serve/Front, a confirmar: revisar a tabela de critérios das três issues. Saída: decisão explícita de manter, dividir ou fechar e destinos de remanescentes. Esta ficha encerra a reconciliação documental do ID, não fecha as issues automaticamente. Na #124, fechamento depende especificamente desse controle de invocação ou alteração de escopo pelo mantenedor; não é melhoria opcional posterior.

<a id="item-038"></a>

## G05 — Incorporar reconciliação do roadmap/backlog do workspace

Frente: Workspace. Encaminhamento: AGRUPAR_EM_P09_COM_ACESSO_NAO_VERIFICADO.

### Identidade e estado

ID original G05; título: Incorporar reconciliação do roadmap/backlog do workspace; tipo de origem: PR; pod: Workspace; responsável para o próximo passo: responsável por Workspace, a confirmar; nenhuma atribuição feita nesta revisão. Não há objeto público APEX implementador confirmado para este ID. Destino consolidado: AGRUPAR_EM_P09_COM_ACESSO_NAO_VERIFICADO. O autor público não é automaticamente assignee ou aprovador.

### Intenção e benefício

Preservar a intenção de reconciliar roadmap/backlog do workspace sem duplicar P09. Este é trabalho de documentação do workspace externo, não uma implementação adicional em APEX.

### Feito, faltante e não comprovado

MATRIX classifica G05 como needs_revalidation e identifica gustocezar/apex-workspace#4; o registro histórico diz que G05 duplica P09. O 404 anônimo registrado não prova inexistência, remoção ou estado privado. Conteúdo e estado atuais dessa PR não foram reconfirmados neste lote.

### Linhagem

G05 → duplicata documental de P09 → referência externa gustocezar/apex-workspace#4. W01/W10/W11 preservam perspectivas do mesmo trabalho. A relação é agrupamento, não prova de merge atual; o elo público de acesso permanece não verificado. Elos de revisão formal, execução independente ou aceite funcional não citados nesta ficha permanecem não verificados; não se infere ausência a partir de falta de Closes.

### Fontes e corte

Fontes confrontadas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json#/rows/4; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv#[id=G05]; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/BACKLOG-LEARNING.json#[id=G05]; ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md:134. Base de referência de código APEX: c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. O CSV e BACKLOG-LEARNING preservam seu corte histórico; não são leitura do estado atual. A ficha Claude é proposta de partida, não validação independente.

### Classe e limite da evidência

FATO OBSERVADO: leitura dos metadados, textos e trechos estáticos expressamente citados nos campos 3–5. RELATO HISTÓRICO do registro, sem reexecução: —. INFERÊNCIA: consequências possíveis do campo 8, com os limites ali indicados. PROPOSTA: alternativas, plano e próximos passos desta ficha. DECISÃO PENDENTE: escolhas de escopo/owner indicadas nos campos 9–10. Teste local, CI por SHA, integração e aprovação humana não são intercambiáveis; nenhuma execução de produto foi feita nesta revisão.

### Fluxo

Fluxo documental proposto: G05 e P09 → conferência da mesma PR externa → uma decisão de estado → referências cruzadas no catálogo. A resposta de acesso → limite de verificação; ela não retorna conclusão sobre implementação.

### Consequências e risco

Criar tarefa APEX para a mesma reconciliação duplicaria escopo; declarar o workspace inexistente a partir de 404 perderia história. Confiança alta no agrupamento registrado; confiança insuficiente para estado público atual do destino.

### Alternativas e recomendação

Manter G05 como origem agrupada em P09 conserva rastreabilidade com uma fila. Consultar material autorizado pelo dono é a alternativa para melhorar estado; até lá, conservar desconhecido. Reabrir nova issue APEX não resolve a indisponibilidade da fonte.

### Dependências e paralelismo

P09 é o destino de ação. Eventual acesso depende do proprietário do workspace e das permissões já existentes; nenhuma tentativa de contornar acesso. A v1 APEX não depende dessa consulta documental externa.

### Plano e aceite propostos

Registrar G05→P09 com a justificativa de duplicidade; quando a fonte autorizada estiver disponível, comparar título, escopo e recibo da PR #4 e atualizar somente a visão derivada. Controle negativo: uma resposta 404 não pode ser convertida em closed/merged/deleted. Aceite documental do agrupamento: ID mantido e próximo passo localizado em P09.

### Comunicação entre responsáveis

Explicar que G05 não foi apagado: sua ação foi concentrada em P09. Identificar repositório completo para não confundir workspace #4 com apex #4 e conservar a data do relato.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? A mesma PR viraria duas entregas independentes. Que caso o teste ainda não cobre? Existência/acesso e estado atuais da PR externa. Como eu explicaria isso para outro pod? G05 é uma origem histórica, P09 concentra a verificação pendente.

### Próxima ação e encerramento

Curador do catálogo, a confirmar: registrar agrupamento G05→P09 nesta visão derivada. Entrada: identidade externa já registrada; saída: uma remissão verificável e acesso marcado não verificado. Encerrar G05 como duplicata catalogada, sem declarar P09 concluído.

<a id="item-039"></a>

## G06 — Monitor ampliado e baseline completo

Frente: Governança/Tooling local. Encaminhamento: REVALIDAR_OPERACAO_LOCAL_SE_FOR_RETOMADA.

### Identidade e estado

ID original G06; título: Monitor ampliado e baseline completo; tipo de origem: tooling; pod: Governança/Tooling local; responsável para o próximo passo: responsável por Governança/Tooling local, a confirmar; nenhuma atribuição feita nesta revisão. Não há objeto público APEX implementador confirmado para este ID. Destino consolidado: REVALIDAR_OPERACAO_LOCAL_SE_FOR_RETOMADA. O autor público não é automaticamente assignee ou aprovador.

### Intenção e benefício

Manter um monitor local com conjunto de identidades e baseline completos para detectar mudanças materiais sem escrever no GitHub. A intenção afeta o operador da automação, não o comportamento do produto APEX.

### Feito, faltante e não comprovado

O registro histórico relata expansão de 55 para 70 identidades, migração 71/70 contando main, falha fechada por baseline incompleto e execução seguinte completa. Esses números pertencem à rodada de 30/09; o código e o estado vivo do monitor não foram inspecionados neste lote. Não há prova de falha operacional atual.

### Linhagem

G06 → tools/apex_expanded_monitor.py e protocolo local CHECKPOINT-PROTOCOL.md → relatos de testes/migração e runs agendados → revalidação prospectiva se o monitor for usado. Não há PR implementadora APEX nem obrigação de recriar os antigos baselines. Elos de revisão formal, execução independente ou aceite funcional não citados nesta ficha permanecem não verificados; não se infere ausência a partir de falta de Closes.

### Fontes e corte

Fontes confrontadas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json#/rows/5; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv#[id=G06]; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/BACKLOG-LEARNING.json#[id=G06]; ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md:154. Base de referência de código APEX: c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. O CSV e BACKLOG-LEARNING preservam seu corte histórico; não são leitura do estado atual. A ficha Claude é proposta de partida, não validação independente.

### Classe e limite da evidência

FATO OBSERVADO: leitura dos metadados, textos e trechos estáticos expressamente citados nos campos 3–5. RELATO HISTÓRICO do registro, sem reexecução: direct_static: cadeia até o primeiro run versionado 013244 com baseline_complete=true, 55 itens + main, #116–#134 e três itens externos; oito testes offline e validação do baseline 2332; github_writes=false; direct_local 2026-09-30: 32 testes offline e 10 controles negativos da lane G; migração GET-only material_change 71/70 com 15 added_to_monitor e lease liberado; rodada normal sem flag no_material_change 71/70 e baseline_valid; primeira execução agendada pós-migração falhou fechada com baseline_incomplete (52 leituras: 49 RuntimeError, 3 TimeoutExpired), sem avançar o baseline; execução agendada seguinte, sem flag de migração, terminou no_material_change com baseline_complete=true, 71/70 identidades, github_writes=false e judge_called=false. INFERÊNCIA: consequências possíveis do campo 8, com os limites ali indicados. PROPOSTA: alternativas, plano e próximos passos desta ficha. DECISÃO PENDENTE: escolhas de escopo/owner indicadas nos campos 9–10. Teste local, CI por SHA, integração e aprovação humana não são intercambiáveis; nenhuma execução de produto foi feita nesta revisão.

### Fluxo

Fluxo relatado: lista de identidades → consultas somente leitura → verificação de completude → comparação com baseline → avanço apenas com leitura completa. Timeout/erro → falha fechada e manutenção do baseline. Fluxo é histórico, sem confirmação da execução atual.

### Consequências e risco

Se um baseline parcial fosse aceito, ausências temporárias poderiam parecer exclusões públicas. Se a expansão fosse repetida sem intenção, o monitor mudaria de universo silenciosamente. Confiança limitada ao desenho relatado; não há incidente atual demonstrado.

### Alternativas e recomendação

Se o monitor não for mais usado, arquivar o último corte e manter G06 como referência operacional. Se for retomado, revisar a configuração vigente antes de operar. Refazer a expansão histórica por padrão é inadequado: o conjunto desejado de identidades precisa ser explícito.

### Dependências e paralelismo

Dono local da automação, lease e protocolo do monitor se ainda aplicáveis. Independente da v1 APEX; consultas de estado deste relatório não autorizam ativar automação, agendar runs ou ampliar seu universo.

### Plano e aceite propostos

Revisar, em eventual retomada, a lista alvo e o baseline persistido; comparar cobertura desejada e observada; conferir o comportamento de timeout e preservação do baseline. Menor entrega: nota de operação com hashes/ref e decisão retomar/arquivar. Controles prospectivos: identidade faltante impede avanço, timeout libera lease conforme contrato, reexecução completa não inventa mudança material. Nenhum desses controles foi executado aqui.

### Comunicação entre responsáveis

Documentar o que significam 71/70 e as datas dos runs, sem tratá-los como contagem atual. Explicar por que a operação local permanece fora da fila de implementação APEX e qual condição reabre a avaliação.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Falha de leitura poderia virar remoção falsa de item. Que caso o teste ainda não cobre? A configuração e o baseline vivos no momento de uma retomada. Como eu explicaria isso para outro pod? O monitor só compara conjuntos completos e sua história não é incidente do produto.

### Próxima ação e encerramento

Dono da automação, a confirmar: decidir se haverá retomada. Entrada: configuração e último baseline reais; saída: nota retomar/arquivar e inventário de identidades. Encerrar administrativamente se arquivado; se retomado, exigir completude e controles documentados, sem ativação nesta revisão.

<a id="item-040"></a>

## G07 — Corrigir referência a e2e.yml inexistente no CI

Frente: Governança/CI. Encaminhamento: ENCERRAR_CORRECAO_DOCUMENTAL_INTEGRADA.

### Identidade e estado

ID original G07; título: Corrigir referência a e2e.yml inexistente no CI; tipo de origem: correção documental; pod: Governança/CI; responsável para o próximo passo: responsável por Governança/CI, a confirmar; nenhuma atribuição feita nesta revisão. Objetos públicos: PR #148: integrada em 2026-10-06T20:18:24Z; autoria pública gustocezar; assignees nenhum no snapshot; issue #125: open; autoria pública gustocezar; assignees nenhum no snapshot. Destino consolidado: ENCERRAR_CORRECAO_DOCUMENTAL_INTEGRADA. O autor público não é automaticamente assignee ou aprovador.

### Intenção e benefício

Eliminar a referência enganosa a e2e.yml como gate vivo de CI, para que a seleção de checks obrigatórios use a cobertura efetiva. A mudança beneficia mantenedores e operadores que interpretam o workflow.

### Feito, faltante e não comprovado

#148 foi integrada como correção de comentário, sem novos jobs ou triggers. Na main c3c3ea3, ci.yml declara que é service-free e que live E2E não é coberto; após #160 o JAR está em workflow separado. Isso confirma a redação atual, não execução E2E.

### Linhagem

G07 → #148 → comentário de CI corrigido → main. Relação de suporte documental a G02/#125; não implementa proteção da branch. A prova local histórica de YAML/actionlint é relato do corpo da PR; #160 substituiu a organização de jobs depois. Identidades preservadas do snapshot público: #148: head d4f85c3c58931654c91c3ba627cbca0a116d75d1, base a289e53fdfba5bcaec2f47f7da6be8849097c307, merge d07aad29ab9ec8e8a14ae6ea7b5f31cc351f2d45. Elos de revisão formal, execução independente ou aceite funcional não citados nesta ficha permanecem não verificados; não se infere ausência a partir de falta de Closes.

### Fontes e corte

Fontes confrontadas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json#/rows/6; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv#[id=G07]; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/BACKLOG-LEARNING.json#[id=G07]; ../parte-03-claude-v2/fontes/claude-v2/C03a-REGISTRO-G-P-F.md:174; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json#[number=148]; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json#[number=125]; fontes/current-open-issues.json#[number=125]; observed_at=2026-10-16T18:29:24.609Z; fontes/main-workflow.txt. Base de referência de código APEX: c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. O CSV e BACKLOG-LEARNING preservam seu corte histórico; não são leitura do estado atual. A ficha Claude é proposta de partida, não validação independente.

### Classe e limite da evidência

FATO OBSERVADO: leitura dos metadados, textos e trechos estáticos expressamente citados nos campos 3–5. RELATO HISTÓRICO do registro, sem reexecução: direct_static: grep em a289e53 e histórico completo; direct_static: .github/workflows só contém ci.yml; YAML com seis jobs; diff de uma linha; PR #148 mergeável; actionlint mantém SC2046 preexistente. INFERÊNCIA: consequências possíveis do campo 8, com os limites ali indicados. PROPOSTA: alternativas, plano e próximos passos desta ficha. DECISÃO PENDENTE: escolhas de escopo/owner indicadas nos campos 9–10. Teste local, CI por SHA, integração e aprovação humana não são intercambiáveis; nenhuma execução de produto foi feita nesta revisão.

### Fluxo

Fluxo documental observado: comentário em ci.yml → entendimento do revisor sobre cobertura → decisão de quais checks exigir. Texto agora identifica limites service-free; não há seta legítima de comentário para runtime validado.

### Consequências e risco

Sem a correção, um gate inexistente poderia ser exigido ou usado para justificar falsa prova live. A correção reduz esse risco de interpretação; não demonstra nem resolve falhas de integração Spark/Collector/ClickHouse.

### Alternativas e recomendação

Manter a explicação explícita no workflow é suficiente para este escopo. Criar um E2E real seria outro trabalho, com ambiente e aceite próprios. Reabrir #148 porque o workflow mudou em #160 duplicaria a intenção já satisfeita.

### Dependências e paralelismo

Nenhuma implementação nova para encerrar este ID. G02 deve usar a redação e os contextos atuais; eventual E2E permanece independente e não é inferido de ci.yml.

### Plano e aceite propostos

Aceite documental: observar merge da #148 e conferir na main que o comentário não atribui E2E a arquivo inexistente. Isso foi feito por leitura estática. Preservar o relato histórico de actionlint com SC2046 preexistente, sem convertê-lo em falha desta correção. Encerrar G07; reabrir apenas se a documentação voltar a afirmar cobertura não sustentada.

### Comunicação entre responsáveis

Explicar que uma linha de documentação foi corrigida e não foram criados jobs. Remeter G02 ao workflow atual para impedir que a correção seja divulgada como gate live entregue.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Um revisor poderia exigir um contexto que não existe. Que caso o teste ainda não cobre? Todo runtime live continua fora desta alteração. Como eu explicaria isso para outro pod? O CI descreve melhor o que faz, sem aumentar sua cobertura.

### Próxima ação e encerramento

Curador da consolidação: marcar G07 encerrado com #148 e o comentário atual como evidência. Entrada: snapshot e ci.yml c3c3ea3; saída: ficha encerrada com limite estático. Nenhuma nova PR ou execução é necessária para este encerramento.

