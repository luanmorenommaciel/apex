# Fichas documentais — lote 40

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-391"></a>

## PROP-DD07-ENV-IDENTITY — [Feature][Método] Rota de identidade de ambiente e checagem de dono de porta

Frente: minutas_tooling. Encaminhamento: minuta_tooling_parcialmente_atendida.

### Identidade e estado

PROP-DD07-ENV-IDENTITY é uma minuta local de 2026-10-11 (feature, método/tooling, executor K-kimi), origem DD07: "Rota de identidade de ambiente e checagem de dono de porta". Não publicada. Owner: Augusto (a confirmar).

### Intenção e benefício

Intenção: rota de identidade de ambiente (perfil Colima, daemon, porta) em routing.md e checagem de dono de porta no preflight, para não diagnosticar JVM/ClickHouse quando o alvo é outro daemon. Público: quem usa a skill no Mac. Ganho: evitar a colisão de C38.

### Feito, faltante e não comprovado

SKILL.md pede identidade de serviço e diz que localhost/porta não identifica ambiente; routing.md exige mesmo ambiente, identidade e janela antes do diagnóstico. Preflight integral só lista Git/ferramentas e se JDWP 5005 escuta: não identifica dono de porta de serviço, perfil Colima ou daemon. A parte textual está atendida no recorte; automação é proposta residual, não falha runtime constatada.

### Linhagem

Linhagem: C38 I3 (29/07) → registro DD07 → routing.md e SKILL.md revistos em 10/10 com a regra textual → minuta Kimi de 11/10 → preflight de 30/07 inalterado em 18/10.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/PROP-DD07-ENV-IDENTITY.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-proposals-review-sources/debug-diamond__SKILL.md; fontes/batch-proposals-review-sources/debug-diamond__references__routing.md; fontes/batch-proposals-review-sources/debug-diamond__scripts__apex-debug-preflight.sh; fontes/batch-claude-registro-propostas-sources/claude/fontes/INDICE-FONTES-LOCAIS.json. Locadores: Minuta/MATRIX DD07, SKILL/routing e preflight integrais, índice de captura.

### Classe e limite da evidência

FATO OBSERVADO: regra textual e alcance exato do preflight. PROPOSTA: checagem de identidade de serviço. NÃO VERIFICADO: dono real de porta, eficácia/reuso de qualquer candidato E11 ou novo episódio C38.

### Fluxo

Fluxo conceitual: identidade declarada do alvo → observação read-only de processo/contexto/porta → comparação segundo modelo escolhido → diagnóstico na fronteira correta. Porta livre/ocupada e propriedade esperada são afirmações diferentes; o script atual só mede o listener JDWP.

### Consequências e risco

A ausência da automação torna a aplicação da regra dependente do procedimento. Pode haver diagnóstico do alvo errado, sem recorrência observada aqui. O texto já exige a checagem, e o nome fixo da porta não demonstra propriedade.

### Alternativas e recomendação

Preservar como estudo residual de automação; comparar o desenho E11 antes de decidir reuso. Manter apenas o procedimento textual é alternativa de decisão do dono; esta revisão não aplica nenhuma delas.

### Dependências e paralelismo

Inventário read-only e casos de porta livre/ocupada podem ser desenhados offline. Classificar propriedade esperada/alheia precisa contrato de identidade compatível com E09; isso não impede o estudo nem exige decidir todo o APEX.

### Plano e aceite propostos

Passo futuro possível: especificar saída sanitizada e critérios para processo, endpoint/contexto e identidade esperada, com casos ausente/divergente; reconhecer que só listar PID ou listener não prova checkout/daemon.

### Comunicação entre responsáveis

Para outro pod: DD07 já tem orientação escrita; o trabalho residual é observar e comparar identidade no preflight, separando porta ocupada de ambiente próprio.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Tomar listener ou número da porta como prova de ambiente pode direcionar investigação ao serviço errado; inferir propriedade de PID isolado também é insuficiente. Que caso o teste ainda não cobre? Não observamos porta/contexto real nem validamos automação ou candidato E11; os casos de identidade são desenho futuro. Como eu explicaria isso para outro pod? DD07 separa regra textual já presente de automação residual; o estudo de porta pode seguir antes da política completa, mas propriedade exige identidade definida.

### Próxima ação e encerramento

Próxima ação documental concluída: delimitar texto atendido e estudo residual. Nenhuma porta foi consultada, script executado ou skill modificada.

<a id="item-392"></a>

## PROP-DD09-ROUTES — [Feature][Método] Rotas para schema atrasado (Code 47) e lanes consumidoras

Frente: minutas_tooling. Encaminhamento: minuta_tooling_majoritariamente_atendida.

### Identidade e estado

PROP-DD09-ROUTES é uma minuta local de 2026-10-11 (feature, método/tooling, executor K-kimi), origem DD09: "Rotas para schema atrasado (Code 47) e lanes consumidoras". Não publicada. Owner: Augusto (a confirmar).

### Intenção e benefício

Intenção: acrescentar a routing.md uma tabela sinal→fronteira para schema atrasado (Code 47 unknown identifier) e para cada lane consumidora (Engine, Serve, Memory, Verify, Front, apex-api). Público: quem diagnostica consumidores. Ganho: começar pela fronteira certa.

### Feito, faltante e não comprovado

Routing integral já contém Engine preflight/query e divergência Serve/API, Verify, Memory ou Front na primeira fronteira diferente; SKILL seleciona a fronteira real sem impor JVM. Code 47 não é nomeado literalmente. Acrescentar o código/exemplos é refinamento opcional; unknown identifier pode exigir conferir SQL/schema/ref e não prova isoladamente schema atrasado.

### Linhagem

Linhagem: #95/#131 e PIPELINE.md → registro DD09 → routing.md revisto em 10/10 com rotas de consumidores → minuta Kimi de 11/10 → verificação de 18/10.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/PROP-DD09-ROUTES.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-proposals-review-sources/debug-diamond__SKILL.md; fontes/batch-proposals-review-sources/debug-diamond__references__routing.md; fontes/batch-claude-registro-propostas-sources/claude/fontes/INDICE-FONTES-LOCAIS.json. Locadores: Minuta/MATRIX DD09 e SKILL/routing integrais com índice de captura.

### Classe e limite da evidência

FATO OBSERVADO: rotas de consumidores e preflight/query presentes, literal Code 47 ausente no arquivo lido. INFERÊNCIA: intenção majoritariamente atendida. NÃO VERIFICADO: uso real ou causa de qualquer erro Code 47.

### Fluxo

Fluxo: sinal de falha num consumidor —(routing.md)→ primeira fronteira divergente —(payloads e contrato)→ hipótese. A minuta acrescentaria exemplos de sinal por lane.

### Consequências e risco

A skill já orienta os casos por fronteira. Exemplos podem facilitar reconhecimento, mas ausência de uma string não significa ausência de rota ou diagnóstico inviável.

### Alternativas e recomendação

Preservar candidata a não ação ou refinamento pequeno com Code 47 e exemplos úteis. Não transformar o código em diagnóstico automático de migração atrasada nem criar duplicata das rotas presentes.

### Dependências e paralelismo

Estudo/refinamento local pode seguir offline sem #131, #106, CI ou DD10 concluídos; coordenação com versão da skill é conveniente, sem gate obrigatório.

### Plano e aceite propostos

Passo futuro possível: exemplo de unknown identifier → comparar SQL exato, schema e ref antes de hipótese causal; consumidor → payload de entrada/saída no primeiro limite divergente.

### Comunicação entre responsáveis

Para outro pod: as rotas já existem; citar Code 47 ajuda reconhecimento, mas a causa ainda deve ser demonstrada na fronteira SQL/schema.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Equiparar Code 47 a schema atrasado sem conferir SQL/ref pode mandar aplicar migração desnecessária ou ignorar erro de consulta. Que caso o teste ainda não cobre? Não houve diagnóstico de consumidor, execução do roteador ou prova de que exemplos melhorariam o tempo de investigação. Como eu explicaria isso para outro pod? DD09 já tem rotas para consumidores; nomear o sintoma é refinamento opcional, sem substituir a identificação da primeira fronteira divergente.

### Próxima ação e encerramento

Próxima ação documental concluída: registrar atendimento majoritário e refinamento opcional. Nenhum routing instalado ou diagnóstico foi executado/alterado.

<a id="item-393"></a>

## PROP-DD10-EVIDENCE-SCHEMA — [Feature][Método] Versionar skill e enriquecer schema de evidência

Frente: minutas_tooling. Encaminhamento: minuta_tooling_aberta_aplicavel.

### Identidade e estado

PROP-DD10-EVIDENCE-SCHEMA é uma minuta local de 2026-10-11 (feature, método/tooling, executor K-kimi), origem DD10: "Versionar skill e enriquecer schema de evidência". Não publicada. Owner: Augusto (a confirmar).

### Intenção e benefício

Estudar formato/versionamento do tooling e campos que tornem as evidências comparáveis: interações, alternativas, classe de evidência e vínculo a Task-Spec quando aplicável. Recuperação por cópias com hash e histórico versionado são garantias distintas.

### Feito, faltante e não comprovado

Evidence-schema já pede número/fase da interação, hipótese, variável, critério, resultado e aprendizagem. Não exige tabela, alternativas rejeitadas, classe relato/direto ou hash de Task-Spec pré-submit. SKILL.md lido não declara versão; este recorte não inventariou todo repositório externo. Cópias e hashes permitem recuperação de bytes, sem demonstrar histórico completo. Logo não é correto dizer que faltam todos os campos de interação ou que a skill é irrecuperável.

### Linhagem

Padrão histórico DD01/A39/#85 → DD10 → minuta → confronto com schema/skill capturados e índices. O vínculo com Git/tag é proposta de custódia; mtime e hash não demonstram sozinhos sequência ou autor das mudanças.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/PROP-DD10-EVIDENCE-SCHEMA.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-proposals-review-sources/debug-diamond__SKILL.md; fontes/batch-proposals-review-sources/debug-diamond__references__evidence-schema.md; fontes/batch-claude-registro-propostas-sources/claude/fontes/INDICE-FONTES-LOCAIS.json; fontes/batch-revalidated-xldd-sources/local-source-manifest.json. Locadores: Minuta/MATRIX DD10, evidence-schema e SKILL integrais, índices de hashes/cópias; ausência de repositório externo não auditada exaustivamente.

### Classe e limite da evidência

FATO OBSERVADO: campos existentes, lacunas textuais delimitadas e frontmatter sem versão declarada. NÃO VERIFICADO: eventual repositório externo, histórico completo ou cumprimento operacional. PROPOSTA: enriquecimento e vínculo a versão/manifesto conforme escopo.

### Fluxo

Investigação → registro estruturado dos campos aplicáveis → classe de evidência e alternativas → versão/manifesto identificável → comparação/restauração. Task-Spec hash deve apontar artefato existente quando houver; não inventar hash retrospectivo para estudo sem spec.

### Consequências e risco

Sem enriquecimento, a comparação depende mais da prosa. Há cópias com hash, portanto não se conclui irrecuperabilidade. Falta de Git/tag neste conjunto de provas não demonstra inexistência global de repositório.

### Alternativas e recomendação

Manter proposta disponível como estudo local: comparar manifesto/hash, repositório/versionamento ou combinação; decidir campos obrigatórios/condicionais e compatibilidade com registros antigos. Não impor tag/repositório como solução já escolhida.

### Dependências e paralelismo

Não depende de runtime, CI ou decisão APEX; refinamentos DD06/DD09 podem avançar sem esperá-la. Hash de Task-Spec é aplicável a trabalho com spec e deve admitir não aplicável explícito quando não existir, preservando fronteira de governança.

### Plano e aceite propostos

Passo futuro possível: esboço do schema com mapa campo atual → extensão, classe de evidência, alternativas e vínculo opcional/condicional à spec; comparar armazenamento/versão sem alterar tooling nesta rodada.

### Comunicação entre responsáveis

Para outro pod: DD10 amplia schema que já registra interações. Cópia/hash recupera bytes; versão e proveniência contam a história. A escolha de formato e destino continua aberta.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Exigir spec/hash inexistente em toda investigação produz falsa proveniência; confundir hash de cópia com histórico completo prejudica auditoria. Que caso o teste ainda não cobre? Não auditamos repositórios externos exaustivamente nem testamos migração do schema, aceitação por ferramentas ou comparação real de investigações. Como eu explicaria isso para outro pod? DD10 estuda extensões de evidência já parcialmente existente e versionamento; campos condicionais e destino precisam decisão, sem alegar irrecuperabilidade global.

### Próxima ação e encerramento

Próxima ação documental concluída: preservar proposta com lacunas e alternativas delimitadas. Nenhum repositório, tag, versão da skill ou novo campo obrigatório foi criado.

<a id="item-394"></a>

## #5 — [ADR-001] Onde o Apex roda?

Frente: historico. Encaminhamento: historico_preservado_com_justificativa.

### Identidade e estado

Issue #5, ADR de arquitetura (crew-a, `type:adr`, `phase:review`, `priority:p0`); autor `gustocezar` (COLLABORATOR); sem assignee nem milestone. Criada em 2026-05-25; fechada em 2026-08-21T01:28:10Z com `state_reason=completed`; 2 comentários. Estado lido no snapshot da API de 2026-10-16. Autor não equivale a owner designado. O identificador "ADR-001" desta issue **não** é o ADR-001 canônico do repositório: na main `c3c3ea3`, `docs/architecture/ADR-INDEX.md` atribui ADR-001 a "tail outlier skew signal" e avisa que materiais históricos reutilizam números.

### Intenção e benefício

Decidir de onde o Apex lê a execução Spark e onde opera: dentro do cluster (SparkListener) ou fora, lendo do ClickHouse. O texto original escolhe "componente externo que consome do ClickHouse" (fase 1 local, fase 2 Rail). Benefício declarado: desacoplar o Apex do ciclo de vida do job e permitir teste local sem cluster.

### Feito, faltante e não comprovado

Feito: o comentário de 2026-08-21 reinterpreta a pergunta com o código de `7c5460c`: a raia `jar` é um `SparkListener` dentro do cluster e a raia `engine` lê só do ClickHouse via `EngineStore`. Conferi os dois pontos nesse SHA: `ApexStageListener ... extends SparkListener` em `jar/src/main/scala/apex/ApexStageListener.scala:54-60`, registrado por `ApexPlugin.scala:34`, e `class EngineStore` em `engine/src/apex_engine/clickhouse.py:159`. A mesma classe segue na main. Relatado e não reproduzido: o teste com `skew_join.py` de 10 milhões de linhas citado no comentário. Falta, como resíduo documental: a decisão revista ("as duas opções, em camadas diferentes") não virou ADR canônico; o corpo continua "Status Proposed" e a decisão vive só no comentário.

### Linhagem

Intenção (ADR de 2026-05-25) → nota de estudo de 2026-06-08 (slice `skew_on_join_30x`, issue central #29) → comentário de revisita de 2026-08-21 sobre a main `7c5460c` → fechamento pelo autor. Elos ausentes: nenhuma PR fecha a issue por texto (busca em corpos e títulos de PR); não encontrei, na main de referência, documento de decisão que registre a resposta final. A ausência de `Closes` não prova ausência de implementação; aqui a implementação é anterior e independente (raias jar e engine). A issue #7 cita #5 como precedente. Timeline pública (API, observada em 2026-10-17T17:30:30Z; 11 eventos): fechada por `gustocezar` em 2026-08-21; referências cruzadas na timeline retornada: #29, #42, #7; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot `issues_all.json` (item 5) e `icomments_all.json` ([comentário 2026-06-08](https://github.com/luanmorenommaciel/apex/issues/5#issuecomment-4648534190), [comentário 2026-08-21](https://github.com/luanmorenommaciel/apex/issues/5#issuecomment-5364075839)); verificações em `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_5.txt` no SHA `7c5460c87421d7f9493a664acb1cfbcc54259b51` e na main `c3c3ea3`; `docs/architecture/ADR-INDEX.md` na main. Corte: snapshot de 2026-10-16; Git lido em 2026-10-17.

### Classe e limite da evidência

DIRETO: estado, datas, autoria, texto do ADR e dos comentários; existência do listener e do `EngineStore` nos SHAs citados. RELATADO: execução com job Spark real e a leitura de "as duas camadas existem ao mesmo tempo". INFERÊNCIA: a pergunta original pressupunha exclusão mútua, e o código não a confirma. Não houve CI, integração nem runtime nesta revisão; nada aqui é aceite humano formal da decisão.

### Fluxo

Fluxo de captura em duas camadas: job Spark → `ApexStageListener` (dentro do cluster, raia jar) → OTLP/ClickHouse (`apex.spark_events`) → `EngineStore` (fora do cluster, raia engine) → findings. Observado estaticamente no SHA da revisita; não executado.

### Consequências e risco

Quem ler só o corpo leva a decisão errada ("só externo"), quando o código usa listener dentro do cluster. A colisão de número com o ADR-001 canônico pode fazer alguém citar a decisão errada. Não há incidente registrado; o risco é de leitura, e a confiança no fato técnico é alta para os SHAs conferidos.

### Alternativas e recomendação

(a) Manter fechada e apontar o comentário de 2026-08-21 como registro da decisão — recomendado; (b) promover a decisão a ADR canônico com número novo, já que o índice não renumera; (c) reabrir — não justificado, porque a pergunta foi respondida. Trade-off: (b) dá visibilidade, mas cria documento novo que só o mantenedor pode aceitar.

### Dependências e paralelismo

Nenhuma dependência técnica nova. Uma eventual promoção a ADR canônico depende do mantenedor e do índice de ADRs (#141 integrou o índice). Pode correr em paralelo com qualquer trabalho de produto: é documentação.

### Plano e aceite propostos

Condição explícita de não ação sobre o produto. Passo documental mínimo, se o mantenedor quiser: nota no índice de ADRs ou na consolidação, ligando "#5 (histórico, ADR-001 de maio)" ao comentário de revisita, sem renumerar. Aceite: um leitor que procure "onde o Apex roda" chega ao comentário e aos dois arquivos citados. Controle negativo: a nota não pode chamar #5 de "ADR-001 canônico".

### Comunicação entre responsáveis

Para a consolidação: "#5 continua fechada; a resposta é ‘as duas camadas’, registrada no comentário de 2026-08-21, e o número ADR-001 desta issue não é o ADR-001 do repositório". Nenhuma mensagem pública foi enviada.

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — renumerar ou reescrever o ADR histórico apagaria a linhagem que o índice protege. (b) Que caso o teste ainda não cobre? — não encontrei teste que ligue a decisão a um comportamento; o listener e o `EngineStore` existem, mas o "Apex não impacta o job" do racional não tem prova citada. (c) Como eu explicaria isso para outro pod? — "o Apex captura dentro do cluster e analisa fora; a pergunta de maio era um falso dilema". (d) Vale um ADR canônico para a arquitetura em camadas?

### Próxima ação e encerramento

Nenhuma ação de produto. Owner a confirmar: mantenedor, só se quiser registrar a decisão no índice. Entrada: este registro. Saída: nota opcional no índice ou na consolidação. Encerramento: já fechada; reabrir só se a arquitetura em camadas mudar.

<a id="item-395"></a>

## #6 — [ADR-002] Quando o classificador (Tier 2) dispara?

Frente: historico. Encaminhamento: historico_preservado_com_justificativa.

### Identidade e estado

Issue #6, ADR bloqueado (`type:adr`, `priority:p1`, label `blocked`); autor `gustocezar`; sem assignee. Criada em 2026-05-26; fechada em 2026-09-17T16:45:12Z (`completed`) por comentário de `luanmorenommaciel` um segundo antes; 2 comentários. Snapshot de 2026-10-16. O número "ADR-002" colide com o ADR-002 canônico (amostra de tasks bem-sucedidas) no índice da main.

### Intenção e benefício

Definir com dados quando o Apex escala do determinístico para o classificador com LLM (Tier 2/3), em vez de "decidir no achismo". Benefício: gastar LLM só onde regras determinísticas não bastam.

### Feito, faltante e não comprovado

Feito: o fechamento diz que o Tier 2 dispara se `confidence_score < 0.6` e `severity >= critical`, em `engine/src/apex_engine/gate.py`, documentado em `docs/lanes/ENGINE.md` T10. Conferi em `1e0ba80` (main no fechamento): `gate.py` declara `confidence < 0.6 AND severity >= high` e explica que, sem degrau `high`, o limiar é `Severity.CRITICAL` (terceiro degrau); `ESCALATE_BELOW_CONFIDENCE = 0.6` em `config.py:14`; T10 em `ENGINE.md:77` com aceite "0.9/high não escala; 0.4/high escala; 0.4/low não". As duas linhas seguem na main `c3c3ea3`. Relatado: "clean jobs cost 0 LLM calls" e evidência empírica de AQE. Não comprovado aqui: a calibração empírica do 0.6 (a ADR pedia dados; o fechamento afirma que existem, sem link).

### Linhagem

ADR bloqueada (2026-05-25) → nota de 2026-06-08 (slice como primeira amostra; #29) → implementação do gate (sem PR identificada por texto) → T10 em ENGINE.md → fechamento de 2026-09-17. Elos ausentes: PR que introduziu `gate.py` e o recibo da evidência empírica citada. A ausência de `Closes` não prova ausência de teste; o critério T10 existe, mas o teste correspondente não foi localizado nesta ficha (não verificado). #41 menciona esta issue. Timeline pública (API, observada em 2026-10-17T17:30:31Z; 10 eventos): fechada por `luanmorenommaciel` em 2026-09-17; referências cruzadas na timeline retornada: #29, #41; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot `issues_all.json` (item 6) e `icomments_all.json` ([fechamento](https://github.com/luanmorenommaciel/apex/issues/6#issuecomment-5718019827)); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_6.txt` com `gate.py`, `config.py` e `ENGINE.md` em `1e0ba802049b4ebe8fb474a7853c604df2b93aeb` e na main `c3c3ea3`.

### Classe e limite da evidência

DIRETO: texto do gate, constante 0.6, critério T10, datas. RELATADO: custo zero de LLM em jobs limpos e evidência empírica. INFERÊNCIA: a equivalência "high → critical" é uma escolha documentada no próprio código, não um erro. NÃO VERIFICADO: teste de T10 e dados que calibraram 0.6.

### Fluxo

Gate de escalonamento: finding (Tier 1 determinístico) → `should_escalate` (confiança < 0.6 e severidade ≥ critical) → crew/LLM; senão, emite direto. Observado estaticamente.

### Consequências e risco

A palavra do fechamento ("critical") e a docstring ("high") diferem, mas o código resolve a diferença explicitamente; quem ler só ENGINE.md pode procurar um degrau `high` que não existe. Nenhum incidente registrado nas fontes lidas. Limite: se a escada de severidade mudar, o mapeamento posicional pode ficar errado sem aviso.

### Alternativas e recomendação

(a) Manter fechada com a decisão registrada (recomendado); (b) acrescentar um teste que trave o mapeamento high→critical, se ainda não houver; (c) reabrir para recalibrar 0.6 — só com dados novos. Trade-off: (b) é barato e protege contra mudança na escada.

### Dependências e paralelismo

Nenhuma dependência nova. Um teste de mapeamento seria trabalho da raia engine, independente das demais.

### Plano e aceite propostos

Não ação sobre a issue. Verificação mínima sugerida, sem execução nesta auditoria: localizar o teste de T10 em `engine/tests` e confirmar que cobre os três casos do aceite e o limiar exato (0.6 escala ou não?). Controle discriminante: confiança 0.6 exata com severidade critical; o código usa `<`, logo não escala.

### Comunicação entre responsáveis

Para a consolidação: "#6 fechada por implementação; o gate está em gate.py, e ‘high’ do texto corresponde a ‘critical’ da escada do contrato".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — trocar `<` por `<=` ou incluir `warning` faria jobs comuns gastarem LLM. (b) Que caso o teste ainda não cobre? — confiança exatamente 0.6 e uma escada de severidade alterada. (c) Como eu explicaria isso para outro pod? — "só findings graves e pouco confiantes vão para o LLM". (d) Onde estão os dados que justificaram 0.6?

### Próxima ação e encerramento

Nenhuma. Owner a confirmar: raia engine, se quiser o teste de mapeamento. Encerramento: já fechada; reabrir só com evidência de escalonamento errado ou mudança na escada de severidade.

<a id="item-396"></a>

## #7 — [ADR-003] Onde mora o estado histórico do Apex?

Frente: historico. Encaminhamento: historico_preservado_com_justificativa.

### Identidade e estado

Issue #7, ADR de armazenamento (`type:adr`, `phase:review`, `priority:p1`); autor `gustocezar`; sem assignee. Criada em 2026-05-26; fechada em 2026-08-21T01:28:25Z (`completed`) pelo autor, logo após o comentário de revisita; 2 comentários. O número "ADR-003" colide com o ADR-003 canônico (AQE re-plan) do índice.

### Intenção e benefício

Decidir onde persistir histórico de análises e findings: ClickHouse local na fase 1 e Rail na fase 2, no mesmo store de leitura do #5, sem dual-write. Benefício: reavaliar decisões e acompanhar a evolução de jobs.

### Feito, faltante e não comprovado

Feito: o comentário de 2026-08-21 afirma que `apex.spark_events` e o histórico vivem no ClickHouse, sem segunda camada. Conferi em `7c5460c`: `CREATE TABLE apex.spark_events` em `contract/spark_events.ddl.sql:8` e `infra/sql/002_spark_events.sql:13`; o DDL canônico segue na main. Falta ou não comprovado: o "schema mínimo" da ADR (watcher_id, tier_triggered, recommendation…) não foi comparado campo a campo com as tabelas atuais; a fase 2 (Rail) não tem registro.

### Linhagem

ADR (2026-05-25) → nota de 2026-06-08 (campos sugeridos pelo Finding; #29) → revisita na main `7c5460c` → fechamento. Elo ausente: o documento que define o schema histórico dos findings (o ADR pedia validá-lo antes do primeiro write). Nenhuma PR do snapshot ligada por texto; isso não prova ausência de implementação. Timeline pública (API, observada em 2026-10-17T17:30:32Z; 11 eventos): fechada por `gustocezar` em 2026-08-21; referências cruzadas na timeline retornada: #29, #37; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 7); [comentário de revisita](https://github.com/luanmorenommaciel/apex/issues/7#issuecomment-5364079049); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_7.txt` com DDLs em `7c5460c87421d7f9493a664acb1cfbcc54259b51` e na main.

### Classe e limite da evidência

DIRETO: DDL de `apex.spark_events` nos dois SHAs; texto da ADR e dos comentários. RELATADO: "não apareceu segunda camada de armazenamento". NÃO VERIFICADO: tabelas de findings ou verificações versus o schema mínimo da ADR; fase Rail.

### Fluxo

Persistência no mesmo store: listener/collector → `apex.spark_events` (ClickHouse) → engine e serve leem → análises gravadas no mesmo ClickHouse (relato). Estático.

### Consequências e risco

Risco documental baixo, como avaliação: o fechamento confirma a decisão pretendida, e os DDLs lidos mostram spark_events em ClickHouse. Esses DDLs não demonstram sozinhos que todo histórico de análises usa um store único. Persistência posterior, inclusive fix_verifications (#117/#169), requer prova própria.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) anotar no índice que a decisão de store único foi confirmada; (c) reabrir para a fase 2 — sem demanda registrada.

### Dependências e paralelismo

Nenhuma. Questões de persistência atuais seguem em #117 e #169, não aqui.

### Plano e aceite propostos

Não ação. Se alguém precisar do schema histórico, partir das DDLs em `contract/` e `infra/sql/` da main, não do rascunho da ADR.

### Comunicação entre responsáveis

Para a consolidação: "#7 foi fechada pelo autor com o relato de confirmação de ClickHouse como store único; os DDLs lidos comprovam spark_events, e os detalhes das tabelas de análises e persistência seguem em #117/#169".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — um segundo store exigiria sincronização, o que a ADR quis evitar. (b) Que caso o teste ainda não cobre? — migração local → Rail. (c) Como eu explicaria isso para outro pod? — "lemos e gravamos no mesmo ClickHouse". (d) O schema mínimo da ADR ainda é útil como checklist?

### Próxima ação e encerramento

Nenhuma. Encerramento: já fechada; reabrir só se surgir um segundo store.

<a id="item-397"></a>

## #8 — [ADR-004] Linguagem dos componentes

Frente: historico. Encaminhamento: historico_substituido_pela_implementacao.

### Identidade e estado

Issue #8, ADR de linguagem (`type:adr`, `phase:review`, `priority:p1`); autor `gustocezar`; sem assignee. Criada em 2026-05-26; fechada em 2026-09-17T16:45:14Z (`completed`) com comentário de `luanmorenommaciel` "superseded by reality"; 2 comentários. O número "ADR-004" colide com o ADR-004 canônico (fronteira de correlação de origem, DEC-11) — colisão relevante, porque X14 e DEC-11 já tratam dessa ambiguidade.

### Intenção e benefício

Escolher a linguagem do core (Watchers, orquestradores). O texto escolhe Go, com Python só para análise e LLM. Benefício pretendido: concorrência sem GIL e alinhamento com infraestrutura.

### Feito, faltante e não comprovado

Não implementado como decidido: o fechamento declara que não há Go no repositório e que a stack é Python (engine/serve/memory/verify/dev), Scala (jar), TypeScript (front) e YAML (collect). Conferi: 0 arquivos `.go` em `1e0ba80` e na main `c3c3ea3`; 32 arquivos `.scala`; `jar/src/main/scala/apex/ApexPlugin.scala`, `front/package.json` e `collect/config.yaml` existem; o `CHANGELOG.md` descreve `jar/` como plugin Scala. A decisão foi substituída pela prática, não executada.

### Linhagem

ADR "In Review" (2026-05-25) → nota de 2026-06-08 (Python como laboratório; #29) → implementação seguiu outro caminho → fechamento como superada. Elo ausente: registro de decisão que revogue o "Go" explicitamente; só o comentário de fechamento o faz. #22 menciona esta issue. Timeline pública (API, observada em 2026-10-17T17:30:34Z; 10 eventos): fechada por `luanmorenommaciel` em 2026-09-17; referências cruzadas na timeline retornada: #29, #22; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 8); [fechamento](https://github.com/luanmorenommaciel/apex/issues/8#issuecomment-5718020254); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_8.txt` (contagem de `.go`/`.scala`, CHANGELOG em `1e0ba802049b4ebe8fb474a7853c604df2b93aeb`).

### Classe e limite da evidência

DIRETO: ausência de `.go` nos dois SHAs; linguagens por diretório; texto do CHANGELOG. RELATADO: motivo da mudança (não registrado além de "superseded by reality"). INFERÊNCIA: a decisão de Go não foi aplicada neste repositório (0 arquivos `.go` na main de referência).

### Fluxo

Fluxo de decisão substituída: ADR propõe Go → implementação real em Python/Scala/TypeScript → fechamento registra a substituição. Não há fluxo de produto a observar.

### Consequências e risco

Risco de leitura: quem buscar "ADR-004" pode achar esta issue (Go) ou o ADR-004 canônico (privacidade). Sem impacto técnico. Confiança alta no fato "sem Go".

### Alternativas e recomendação

(a) Manter fechada como substituída (recomendado); (b) registrar no índice que o ADR-004 histórico (#8) não tem relação com o canônico; (c) reabrir — sem motivo.

### Dependências e paralelismo

Nenhuma técnica. A ambiguidade de número já está coberta por X14 e pelo aviso do índice de ADRs.

### Plano e aceite propostos

Não ação. Documentação mínima opcional: citar #8 como exemplo da ambiguidade de número na seção "Limite deste índice".

### Comunicação entre responsáveis

Para a consolidação: "#8 foi superada; não há Go; ‘ADR-004’ aqui não é o ADR-004 de privacidade".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — tratar #8 como decisão vigente levaria alguém a portar o core para Go sem motivo atual. (b) Que caso o teste ainda não cobre? — nenhum; é decisão de linguagem. (c) Como eu explicaria isso para outro pod? — "o ADR de Go não virou código neste repositório; a stack é a do CHANGELOG". (d) Algum requisito do ADR (concorrência) ficou sem resposta na stack atual?

### Próxima ação e encerramento

Nenhuma. Encerramento: já fechada; reabrir só se alguém propuser portar componentes para Go.

<a id="item-398"></a>

## #9 — [DATA GEN] Define the data generator specification for Apex

Frente: historico. Encaminhamento: historico_substituido_com_residuo_de_escopo.

### Identidade e estado

Issue #9, feature de definição (`type:feature`, `phase:review`, `priority:p1`); autor `Gabriel-Philot` (sem associação ao repositório); sem assignee. Criada em 2026-05-26; fechada em 2026-09-17T16:45:16Z (`completed`) com comentário "superseded" de `luanmorenommaciel`; 2 comentários.

### Intenção e benefício

Definir o gerador de dados compartilhado: entidades varejo, escrita em Delta bronze, integridade referencial, escalas dev/lab/bench, semente reprodutível, perfis clean/realistic/harsh/adversarial e dimensões de patologia. Os critérios de aceite são de definição (acordo do time, escopo, entradas e saídas, tarefas prontas para outra issue), não de implementação.

### Feito, faltante e não comprovado

Feito, segundo o fechamento: o laboratório `dev/` cobre o propósito com `dev/jobs/generate_data.py` (fato e dimensão com hot keys verificadas) e os jobs `skew_join.py`, `spill.py`, `bad_shuffle.py`, `driver_oom.py` e `dev/scripts/calibrate.py`. Conferi: os seis arquivos existem em `1e0ba80` e na main; `common/data.py` usa `F.rand(SEED)` e duas hot keys (~25% cada), e `generate_data.py` imprime PASS/FAIL para hot keys entre 45% e 55%. Falta (resíduo explícito no fechamento): perfis, tiers de escala, entidades varejo e o gerador YAML declarativo, que ficou na branch `gustocezar/feature/desacoplamento-geradores` (`bd8a08b` no clone de 2026-10-16), contida no bundle do #105 (ref arquivado `bd8a08b`).

### Linhagem

Spec (2026-05-26) → slice local `skew_on_join_30x` em branch (nota de 2026-06-08; #29) → laboratório `dev/` na main (commits `02b8ef0` de 2026-07-21 e `50927d4` de 2026-07-28 em `generate_data.py`) → fechamento como superada. Elos ausentes: decisão registrada de abandonar perfis e escalas; destino das quatro variantes de branch "desacoplamento-geradores" (codex, cowork, kimi e a original), que existem no clone. Timeline pública (API, observada em 2026-10-17T17:30:35Z; 9 eventos): fechada por `luanmorenommaciel` em 2026-09-17; referências cruzadas na timeline retornada: #29, #32; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 9); [nota de estudo](https://github.com/luanmorenommaciel/apex/issues/9#issuecomment-4648516985); [fechamento](https://github.com/luanmorenommaciel/apex/issues/9#issuecomment-5718020746); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_9.txt` (arquivos em `1e0ba802049b4ebe8fb474a7853c604df2b93aeb` e na main, refs das branches, semente e hot keys); registro de custódia do #105 citado na correção C04-19 do Codex (não reaberto aqui).

### Classe e limite da evidência

DIRETO: arquivos e semente; refs de branch no clone (não é estado remoto atual). RELATADO: "delivered by the dev/ lab". INFERÊNCIA: o gerador da main cobre skew, não as demais dimensões da spec. NÃO VERIFICADO: conteúdo das branches arquivadas e qualquer acordo de time exigido pelo aceite.

### Fluxo

Fluxo do laboratório: `generate_data.py` (semente fixa, hot keys) → tabelas Delta em MinIO → jobs de patologia → event logs → `calibrate.py` mede a mecânica. Estático.

### Consequências e risco

Quem precisar de perfis ou escalas não os encontrará na main, embora a issue esteja "completed". O resíduo está declarado no fechamento, então o risco é de leitura, não de perda. Os trabalhos de gerador migraram, em parte, para o Dataship (P10/D*), fora deste repositório.

### Alternativas e recomendação

(a) Manter fechada e registrar o resíduo (recomendado); (b) abrir issue nova e delimitada se perfis e escalas forem necessários, como o fechamento sugere; (c) reabrir — contraria a sugestão do mantenedor.

### Dependências e paralelismo

Uma issue nova dependeria de decisão de produto. O arquivamento dessa branch já está no bundle do #105 (recibo Codex de 2026-10-17; hash reconferido aqui). Estudo e implementação ficam separados.

### Plano e aceite propostos

Não ação nesta issue. Se reativada: issue nova com perfis e escalas mínimos, aceite por dimensão e controle negativo (perfil clean não pode disparar o watcher de skew).

### Comunicação entre responsáveis

Para a consolidação: "#9 foi substituída pelo laboratório de skew; perfis e escalas não foram entregues e exigem issue nova".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — reabrir a spec inteira duplicaria o laboratório que já existe. (b) Que caso o teste ainda não cobre? — dimensões além de skew, como small files e nulls. (c) Como eu explicaria isso para outro pod? — "o gerador da main faz skew com semente; o resto ficou na branch arquivada". (d) As quatro variantes de branch precisam do mesmo destino de custódia?

### Próxima ação e encerramento

Nenhuma no APEX até decisão de produto. Owner a confirmar: mantenedor, para eventual issue nova. Encerramento: já fechada; resíduo e condição de reabertura registrados.

<a id="item-399"></a>

## #10 — [LAB PLAT] build Apex Lab Platform v0

Frente: historico. Encaminhamento: historico_preservado_com_divergencia_de_desenho.

### Identidade e estado

Issue #10, componente (`type:component`, `phase:review`, `priority:p1`); autor `Gabriel-Philot`; sem assignee. Criada em 2026-05-26; fechada em 2026-09-17T16:45:18Z (`completed`) com o comentário "Closing as implemented" de `luanmorenommaciel`; 1 comentário.

### Intenção e benefício

Criar um laboratório local para rodar Spark, gravar Delta, capturar event logs, inspecionar no History e carregar evidência num banco analítico. O aceite é de definição (acordo, requisitos, arquitetura, caminhos e smoke definidos, tarefas prontas e follow-ups identificados).

### Feito, faltante e não comprovado

Fechamento relata implementação; no SHA 1e0ba80, compose, configuração de event logs, Delta, scripts e README sustentam a presença estática do laboratório. O plano previa loader de event logs; o fluxo descrito do produto usa plugin jar → spans OTLP → ClickHouse. São formas distintas de captura: isso não prova que o produto realiza exatamente o não objetivo de mover event logs diretamente do Spark ao banco. A listagem de dev/scripts inclui phase_a_eventlog_report.py, sem comprovar o loader originalmente previsto.

### Linhagem

Spec (2026-05-26) → laboratório na main → fechamento "implemented". Elos ausentes: PRs de origem (não ligadas por texto); decisão registrada que troca o loader pelo caminho jar/OTLP; follow-ups pedidos pelo aceite. #34 e #35 mencionam esta issue. Timeline pública (API, observada em 2026-10-17T17:30:36Z; 8 eventos): fechada por `luanmorenommaciel` em 2026-09-17; referências cruzadas na timeline retornada: #34, #35; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 10); [fechamento](https://github.com/luanmorenommaciel/apex/issues/10#issuecomment-5718021173); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_10.txt` (compose, spark-defaults, Dockerfile, `apex.ps1` e listagem de `dev/` em `1e0ba802049b4ebe8fb474a7853c604df2b93aeb`).

### Classe e limite da evidência

DIRETO: serviços, configuração de event logs, versão Delta e comandos no SHA lido. RELATADO: implemented. DERIVADO: o caminho de telemetria documentado diverge da arquitetura de loader da proposta. NÃO VERIFICADO: execução smoke e histórico completo dos follow-ups; não se equiparam spans OTLP a event logs brutos.

### Fluxo

Fluxo do laboratório: jobs `dev/jobs` → Spark master/worker → Delta em MinIO e event logs em `s3a://spark-logs/events/` → Spark History; em paralelo, o plugin jar envia telemetria por OTLP → Collector → ClickHouse (`infra/`). Estático.

### Consequências e risco

Quem comparar a spec com o laboratório pode achar que falta o loader. Na prática, o desenho mudou. Nenhum incidente registrado nas fontes lidas. Limite: o fechamento cita "Delta" e "History" por arquivo; nenhum runtime foi observado aqui.

### Alternativas e recomendação

(a) Manter fechada e registrar a troca loader → OTLP (recomendado); (b) documentar no `dev/README.md` por que não há loader; (c) reabrir — sem motivo.

### Dependências e paralelismo

Nenhuma. A operação local do pacote segue em #62 (fechada), #174 e #175, não aqui.

### Plano e aceite propostos

Não ação. Nota opcional: registrar a mudança de desenho na consolidação para que ninguém crie o loader por leitura literal da spec.

### Comunicação entre responsáveis

Para a consolidação: "#10 foi entregue como laboratório; a ingestão seguiu jar/OTLP, não o loader da spec".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — um loader adicional precisaria de identidade e deduplicação próprias para não sobrepor dados do listener. Que caso o teste ainda não cobre? — a execução cold start não foi observada nesta auditoria. Como eu explicaria isso para outro pod? — o laboratório foi fechado como implementado; o caminho descrito captura spans ao vivo, enquanto a proposta previa importar event logs. Os follow-ups do aceite têm rastros próprios?

### Próxima ação e encerramento

Nenhuma. Encerramento: já fechada; reabrir só se o caminho OTLP for abandonado.

<a id="item-400"></a>

## #11 — teste

Frente: historico. Encaminhamento: registro_de_teste_sem_escopo.

### Identidade e estado

Issue #11, sem labels nem assignee; autor `antonylucas` (COLLABORATOR). Criada em 2026-05-26T21:07:55Z e fechada 9 segundos depois, às 21:08:04Z, com `state_reason=completed`; 0 comentários. Snapshot de 2026-10-16. Nenhum pod ou owner de produto se aplica.

### Intenção e benefício

Corpo e título dizem somente teste. Criada em 2026-05-26T21:07:55Z, 59 segundos antes de #12; teste de acesso é uma inferência pelo conteúdo e proximidade, não intenção declarada.

### Feito, faltante e não comprovado

Nada a fazer e nada a comprovar: não há escopo. O `completed` não indica entrega; é o motivo padrão de fechamento. Não comprovado: a intenção, que é inferência.

### Linhagem

Criação → fechamento imediato pelo próprio autor (fechador confirmado na timeline, ao fim deste campo). A main no fechamento é o commit inicial `54ed2040` (2026-05-05). Nas fontes consultadas (snapshot, timeline e busca no repositório), nenhuma referência de PR, issue, registro ou Task-Spec aponta para #11. Timeline pública (API, observada em 2026-10-17T17:30:37Z; 1 eventos): fechada por `antonylucas` em 2026-05-26; referências cruzadas na timeline retornada: nenhuma; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot `issues_all.json` (item 11); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_11.txt` (commit `54ed2040f0a1a9a688ee5a93c2b15e7a75a43f82`); [issue](https://github.com/luanmorenommaciel/apex/issues/11).

### Classe e limite da evidência

DIRETO: metadados e corpo. INFERÊNCIA: teste de acesso. Não há relato, decisão ou prova técnica envolvida.

### Fluxo

Fluxo administrativo: colaborador cria issue de teste → fecha em seguida. Nenhum fluxo de produto.

### Consequências e risco

Nenhum impacto. O único efeito é ocupar o número 11 na sequência. Confiança alta.

### Alternativas e recomendação

(a) Manter fechada como registro de teste — recomendado; (b) marcar com label de teste — custo sem benefício; (c) excluir — não é possível sem permissão de admin e apagaria histórico.

### Dependências e paralelismo

Nenhuma dependência: não há escopo técnico, decisão ou prova que dependa deste item, nem item que dependa dele.

### Plano e aceite propostos

Condição explícita de não ação: item sem escopo. Não exige passo, artefato ou controle.

### Comunicação entre responsáveis

Na consolidação: #11 e #12 são itens administrativos de teste; a hipótese de testar permissão não foi declarada nos corpos.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — contabilizar o item como entrega distorceria o backlog. Que caso o teste ainda não cobre? — nenhum teste técnico está ligado nas fontes lidas. Como eu explicaria isso para outro pod? — item administrativo fechado em 9 segundos; teste de acesso é hipótese.

### Próxima ação e encerramento

Nenhuma. Encerramento: definitivo; não há condição de reabertura.

