# Fichas documentais — lote 41

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-401"></a>

## #12 — [TEST] SIDYMAR

Frente: historico. Encaminhamento: registro_de_teste_sem_escopo.

### Identidade e estado

Issue #12, sem labels nem assignee; autor `sidymar` (COLLABORATOR). Criada em 2026-05-26T21:08:54Z e fechada 26 segundos depois (`completed`); corpo vazio; 0 comentários. Snapshot de 2026-10-16.

### Intenção e benefício

O título "[TEST] SIDYMAR" indica um teste de acesso do colaborador, um minuto após o #11. Não há intenção de produto.

### Feito, faltante e não comprovado

Nada feito, nada faltando: corpo vazio. O motivo `completed` é padrão, não entrega.

### Linhagem

Criação → fechamento imediato. A main era o commit inicial `54ed2040`. Nas fontes consultadas, nenhuma referência de PR, issue, registro ou Task-Spec. Timeline pública (API, observada em 2026-10-17T17:30:38Z; 1 eventos): fechada por `sidymar` em 2026-05-26; referências cruzadas na timeline retornada: nenhuma; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot `issues_all.json` (item 12); [issue](https://github.com/luanmorenommaciel/apex/issues/12).

### Classe e limite da evidência

DIRETO: metadados. INFERÊNCIA: teste de acesso, pelo título e pela sequência com o #11.

### Fluxo

Fluxo administrativo: colaborador cria uma issue vazia com o próprio nome no título → fecha em 26 segundos. Nenhum fluxo de produto.

### Consequências e risco

Nenhum impacto em produto, backlog ou decisões; só ocupa o número 12 da sequência. Confiança alta, porque o corpo está vazio.

### Alternativas e recomendação

(a) Manter fechada como registro de teste — recomendado; (b) rotular ou reclassificar — custo sem ganho, pois nenhuma contagem atual a inclui como trabalho.

### Dependências e paralelismo

Nenhuma dependência: não há escopo técnico, decisão ou prova ligada a este item.

### Plano e aceite propostos

Condição explícita de não ação: item sem escopo, sem artefato a produzir e sem controle a definir.

### Comunicação entre responsáveis

Na consolidação, agrupar #11 e #12 como itens de teste de 2026-05-26; a finalidade de verificar acesso é inferida.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — reclassificar teste administrativo como entrega distorceria o backlog. Que caso o teste ainda não cobre? — não há escopo de produto declarado para definir cobertura. Como eu explicaria isso para outro pod? — item de teste fechado em 26 segundos, provavelmente ligado a acesso.

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento definitivo; não há condição de reabertura, porque não existe escopo a retomar.

<a id="item-402"></a>

## #15 — [EPIC] Apex — Peak Performance for Spark & Databricks

Frente: historico. Encaminhamento: epico_historico_substituido_por_ledger.

### Identidade e estado

Issue #15, épico (`type:epic`, `phase:build`); autor `luanmorenommaciel` (OWNER); sem assignee. Criada em 2026-05-26; fechada em 2026-09-17T16:45:20Z (`completed`) pelo próprio autor; 1 comentário. Dezesseis issues citam o épico como pai (#16–#28, #30, #33, #43).

### Intenção e benefício

Ser o épico pai do Apex: camada de observabilidade e otimização Spark, com dois problemas-alvo (execuções lentas sem diagnóstico e reviews que não pegam anti-padrões). Cliente de lançamento declarado: One Way Solution (OWS).

### Feito, faltante e não comprovado

Feito, segundo o fechamento: a visão saiu como v0.1.0 em 2026-07-29, com oito raias governadas por contrato e ~400 testes; o acompanhamento passou para `docs/lanes/*.md` e para o ledger `tasks/` + `docs/task-specs/`. Conferi em `1e0ba80`: `CHANGELOG.md` registra "[0.1.0] — 2026-07-29 … Eight lanes, one frozen contract, 400 tests"; a tag `v0.1.0` aponta para `80832de` (2026-07-29); os diretórios de lanes e task-specs existem. Não comprovado: os ~400 testes (número do CHANGELOG, não reexecutado) e a metade "pré-merge" da visão, que segue aberta em #21. Observação: o link do CHANGELOG aponta para `github.com/dataship/apex/releases`, outro repositório; não conferido.

### Linhagem

Épico (2026-05-26) → filhas #16–#28, #30, #33, #43 → v0.1.0 → migração do acompanhamento para lanes e ledger → fechamento. Elo ausente: mapa filha → resultado; parte das filhas foi fechada no mesmo minuto (2026-09-17 16:45) por triagem em lote. As referências `src/data-ship/projects/apex.md` e `crew-a-notes-2026-05-26.md` não existem na main (provável repositório externo, não verificado). Timeline pública (API, observada em 2026-10-17T17:30:39Z; 29 eventos): fechada por `luanmorenommaciel` em 2026-09-17; item adicionado a um Project do GitHub; referências cruzadas na timeline retornada: #16, #17, #18, #19, #20, #21, #22, #23, #24, #25, #26, #27, #28, #30, #33, #43; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 15); [fechamento](https://github.com/luanmorenommaciel/apex/issues/15#issuecomment-5718021647); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_15.txt` (tags, CHANGELOG e diretórios em `1e0ba802049b4ebe8fb474a7853c604df2b93aeb`).

### Classe e limite da evidência

DIRETO: data e conteúdo do CHANGELOG, tag, diretórios. RELATADO: "~400 testes", cliente de lançamento. INFERÊNCIA: o fechamento em lote de 2026-09-17 foi triagem do mantenedor, não entrega simultânea. NÃO VERIFICADO: arquivos externos citados no corpo.

### Fluxo

Fluxo de governança: épico → issues filhas → release v0.1.0 → acompanhamento em `docs/lanes` e `tasks/`. Sem fluxo de produto próprio.

### Consequências e risco

Baixo. Risco de leitura: alguém pode tomar "completed" como "visão inteira entregue", quando a metade pré-merge está em #21 (aberta). Confiança alta nos fatos de release.

### Alternativas e recomendação

(a) Manter fechado (recomendado); (b) reabrir como guarda-chuva — redundante com lanes e ledger; (c) anotar na consolidação que #21 carrega o resíduo pré-merge.

### Dependências e paralelismo

Nenhuma nova. O resíduo de visão depende de #21, que tem decisão própria (ADIAR na v2).

### Plano e aceite propostos

Não ação. Documentação mínima: a consolidação deve ligar o épico a #21 como resíduo explícito.

### Comunicação entre responsáveis

Para a consolidação: "o épico fechou com a v0.1.0; o acompanhamento mudou de lugar; a metade pré-merge está em #21".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — manter o épico aberto duplicaria o ledger de tarefas. (b) Que caso o teste ainda não cobre? — os 400 testes do CHANGELOG não foram reexecutados nesta auditoria. (c) Como eu explicaria isso para outro pod? — "o épico virou release e lanes; o que falta da visão está em #21". (d) A visão de cliente (OWS) ainda orienta prioridades?

### Próxima ação e encerramento

Nenhuma. Encerramento: já fechado; reabrir só se o mantenedor voltar a usar épicos como acompanhamento.

<a id="item-403"></a>

## #16 — [FEATURE] Spark History Parser

Frente: historico. Encaminhamento: historico_substituido_por_pivo_de_arquitetura.

### Identidade e estado

Issue #16, feature (`type:feature`, `phase:spec`, `priority:p1`); autor `luanmorenommaciel` (OWNER); sem assignee. Criada em 2026-05-26; fechada em 2026-09-17T16:45:23Z (`completed`) com comentário "superseded by an architecture pivot"; 2 comentários.

### Intenção e benefício

Transformar event logs JSON do Spark History numa estrutura com tempos de stage, shuffle, uso de executores e sinais de skew, como entrada para todas as features. Aceite original: ler logs Spark 3.x e 4.x, apontar os 5 maiores gargalos por job e gerar JSON para a F5.

### Feito, faltante e não comprovado

Substituído: em vez de ler o JSON do History, o Apex usa um `SparkListener` ao vivo (`jar/`), que agrega `TaskMetrics` por stage e envia spans OTLP para `apex.spark_events`. Conferi em `1e0ba80`: `jar/build.sbt` tem quatro células (3.5/2.12, 3.5/2.13, 4.0/2.13 e 4.1/2.13 "aditiva"); `docs/lanes/JAR.md` descreve o listener, OTLP e o agregado por stage. O parser de estudo `apex/apexlib.py` (nota de 2026-06-08) não está na main. Não entregue como especificado: "top 5 gargalos por job" e saída JSON para a F5; o aceite foi trocado pelo pivô.

### Linhagem

Feature (2026-05-26) → parser inicial em branch de estudo (#29) → pivô para listener ao vivo → fechamento. Elos ausentes: PR do pivô ligada por texto; decisão registrada de abandonar a leitura de History. #32 e #36 citam a issue. Timeline pública (API, observada em 2026-10-17T17:30:41Z; 13 eventos): fechada por `luanmorenommaciel` em 2026-09-17; item adicionado a um Project do GitHub; referências cruzadas na timeline retornada: #29, #32, #36; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 16); [nota de estudo](https://github.com/luanmorenommaciel/apex/issues/16#issuecomment-4648519358); [fechamento](https://github.com/luanmorenommaciel/apex/issues/16#issuecomment-5718022219); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_16.txt` (`jar/build.sbt`, `docs/lanes/JAR.md`, ausência de `apex/apexlib.py` em `1e0ba802049b4ebe8fb474a7853c604df2b93aeb`).

### Classe e limite da evidência

DIRETO: matriz de build em jar/build.sbt e ausência de apex/apexlib.py na árvore 1e0ba80. RELATADO: listener substitui a camada de entrada. A matriz declara alvos Spark 3.5/4.0/4.1; ela não comprova execução nem satisfaz o aceite de parsear event logs 3.x/4.x. NÃO VERIFICADO: execução das quatro células e ingestão de jobs históricos sem plugin.

### Fluxo

Fluxo substituto: job Spark → `ApexPlugin`/listener (onStageCompleted) → spans OTLP :4318 → Collector → `apex.spark_events`. Estático.

### Consequências e risco

Quem procurar "leitura de event log histórico" na main de referência não a encontrará (busca desta revisão). Para jobs já finalizados sem o plugin, não há caminho de entrada, um limite de produto real. Nenhum incidente registrado nas fontes lidas. `JAR.md` ainda lista três células e tarefas T8/T15 desmarcadas, divergindo do `build.sbt`; isso é desatualização documental.

### Alternativas e recomendação

(a) Manter fechada como substituída (recomendado); (b) issue nova para importar event logs históricos, se houver demanda de jobs sem plugin; (c) reabrir — o pivô foi deliberado.

### Dependências e paralelismo

Nenhuma. Uma eventual importação histórica seria trabalho novo da raia jar/collect, separado.

### Plano e aceite propostos

Não ação. Documentação mínima: registrar na consolidação que o pivô deixa sem cobertura jobs executados sem o plugin.

### Comunicação entre responsáveis

Para consolidação: #16 foi fechada como substituída pelo listener ao vivo; no caminho auditado, captura exige o plugin durante a execução.

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — reintroduzir o parser criaria duas fontes de verdade para os mesmos stages. (b) Que caso o teste ainda não cobre? — job finalizado sem o plugin ligado. (c) Como eu explicaria isso para outro pod? — "não lemos logs depois; capturamos durante a execução". (d) `JAR.md` deve ser atualizado para as quatro células?

### Próxima ação e encerramento

Nenhuma. Encerramento: já fechada; reabrir só com demanda de importação histórica.

<a id="item-404"></a>

## #17 — [FEATURE] Watcher / Classifier / Judger Pipeline

Frente: historico. Encaminhamento: historico_preservado_com_justificativa.

### Identidade e estado

Issue #17, feature (`type:feature`, `phase:design`, `priority:p1`); autor `luanmorenommaciel` (OWNER); sem assignee. Criada em 2026-05-26; fechada em 2026-09-17T16:45:25Z (`completed`) com "Closing as implemented"; 3 comentários.

### Intenção e benefício

Pipeline agentic em três estágios: Watcher (observa execuções), Classifier (rotula anti-padrões) e Judger (recomenda e simula antes de aplicar), cada um testável isoladamente.

### Feito, faltante e não comprovado

Fechamento relata entrega. Em 1e0ba80 há watchers determinísticos, incluindo retry_pressure, crew correlate→judge com output_pydantic=Finding e gate em engine/src/apex_engine/gate.py; o caminho engine/gate.py do comentário é impreciso. t1_triage.py, test_listener_failsafe.py e 52 testes verdes pertencem ao relato cowork de julho. A busca textual fornecida não encontrou esses termos nos conteúdos pesquisados; isso não equivale a uma listagem exaustiva de nomes de arquivo. Uso real do Classifier/Judge não foi comprovado nesta revisão.

### Linhagem

Feature (2026-05-26) → watcher de estudo em branch (2026-06-08) → progresso "cowork" (2026-07-13) → watchers, crew e gate na main → fechamento. Elos ausentes: PRs que introduziram watchers e crew, ligadas por texto; destino do achado COWORK-024 (proveniência por engine), que aparece aberto no relato de julho e não foi localizado depois. Timeline pública (API, observada em 2026-10-17T17:30:42Z; 16 eventos): fechada por `luanmorenommaciel` em 2026-09-17; item adicionado a um Project do GitHub; referências cruzadas na timeline retornada: #29, #32, #36, #38, #41; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 17); [nota](https://github.com/luanmorenommaciel/apex/issues/17#issuecomment-4648522003), [progresso](https://github.com/luanmorenommaciel/apex/issues/17#issuecomment-4963664814), [fechamento](https://github.com/luanmorenommaciel/apex/issues/17#issuecomment-5718022643); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_17.txt`.

### Classe e limite da evidência

DIRETO: lista de watchers, crew, modelos, gate. RELATADO: métricas da cowork (333 ms, 2,8 mil tokens, 52 testes) e "simulate before applying = verify". INFERÊNCIA: o "simular antes de aplicar" foi reinterpretado como verificação de bancada e recusa, não simulação de ambiente virtual. NÃO VERIFICADO: execução real do crew e resolução do COWORK-024.

### Fluxo

Fluxo estático: watchers Tier 1 → gate (confiança <0.6 e severity critical, conforme leitura de #6) → crew configurado para Sonnet/Opus → Finding mesclado; verify é a substituição declarada para simular antes de aplicar.

### Consequências e risco

Risco de leitura: o caminho `engine/gate.py` do fechamento está errado e pode confundir. O "Judger simula antes de aplicar" do corpo não é o que o produto faz, que é recusa e predição na verify. Nenhum incidente registrado nas fontes lidas.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) registrar na consolidação a reinterpretação do Judger e o destino do COWORK-024; (c) reabrir — sem base.

### Dependências e paralelismo

Nenhuma nova. A medição do uso real do crew pertence a trabalho novo de observabilidade, não a esta issue.

### Plano e aceite propostos

Não ação. Verificação documental opcional: localizar onde o COWORK-024 foi tratado (fonte local da cowork, fora deste repositório) antes de declará-lo resolvido.

### Comunicação entre responsáveis

Para a consolidação: "#17 entregue como watchers + gate + crew; o Judger não simula ambiente virtual; o caminho do gate no comentário está errado".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — chamar o LLM antes do Tier 1 voltaria a gastar tokens no caminho feliz. (b) Que caso o teste ainda não cobre? — dois engines gravando o mesmo `scenario_id` (COWORK-024). (c) Como eu explicaria isso para outro pod? — "regras primeiro; o LLM só julga o que as regras não resolvem". (d) O Judge foi exercitado em produção alguma vez?

### Próxima ação e encerramento

Nenhuma no repositório. Owner a confirmar: quem conduziu a cowork, para dizer onde o COWORK-024 terminou. Encerramento: já fechada.

<a id="item-405"></a>

## #18 — [FEATURE] OTel Collector Stage 02 (Go)

Frente: historico. Encaminhamento: historico_substituido_por_configuracao.

### Identidade e estado

Issue #18, feature (`type:feature`, `phase:build`, `priority:p0`); autor `luanmorenommaciel` (OWNER); sem assignee. Criada em 2026-05-26; fechada em 2026-09-17T16:45:27Z (`completed`) como "superseded"; 1 comentário.

### Intenção e benefício

Construir um Collector OTel próprio em Go para transformar convenções Spark, remover PII além do processador padrão e aplicar backpressure quando o ClickHouse estiver lento. Agrupava #1–#4.

### Feito, faltante e não comprovado

Substituído segundo o fechamento: o mantenedor declara o objetivo funcional atendido sem build Go. Em 1e0ba80, CHANGELOG registra collector config-only, collect/ddl contém MVs e config.yaml encadeia memory_limiter, transform/redaction, attributes/scrub e redaction/pii com sending_queue/retry_on_failure. Esse desenho estático não comprova eficácia completa de PII/backpressure; detalhes seguem nas fichas #1–#3.

### Linhagem

Feature (2026-05-26) → sub-issues #1–#4 → collector só de configuração + MVs no ClickHouse → fechamento. Elo ausente: decisão registrada de não usar Go (coerente com o #8, também substituído). Nenhuma PR do snapshot ligada por texto. Timeline pública (API, observada em 2026-10-17T17:30:43Z; 9 eventos): fechada por `luanmorenommaciel` em 2026-09-17; item adicionado a um Project do GitHub; referências cruzadas na timeline retornada: nenhuma; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 18); [fechamento](https://github.com/luanmorenommaciel/apex/issues/18#issuecomment-5718023257); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_18.txt` (CHANGELOG, `collect/ddl/`, processadores em `config.yaml` de `1e0ba802049b4ebe8fb474a7853c604df2b93aeb`).

### Classe e limite da evidência

DIRETO: CHANGELOG, arquivos de DDL e cadeia de processadores. RELATADO: "SemConv reshaping via MVs" como substituto funcional. NÃO VERIFICADO: desempenho e backpressure reais; versão atual do otelcol na main (0.156.0 no fechamento; os Compose de `infra/` e `collect/` da main também usam 0.156.0, conferido em `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_18.txt`).

### Fluxo

Fluxo de ingestão: OTLP/HTTP :4318 → `memory_limiter` → redação OTTL, scrub de atributos e redaction de PII → exporter ClickHouse com fila e retry → tabelas brutas → MVs que remodelam para `apex.spark_events`, `plan_transitions` e `job_conf`.

### Consequências e risco

A cadeia de processadores e as regras visíveis sustentam a escolha de configuração. O fechamento declara cumprimento funcional; a revisão não avaliou completude de PII real ou comportamento sob fila cheia/ClickHouse lento.

### Alternativas e recomendação

(a) Manter fechada como substituída (recomendado); (b) reabrir só se houver requisito que exija processador customizado; (c) documentar na consolidação que #1–#3 carregam os detalhes.

### Dependências e paralelismo

Nenhuma. Detalhes de PII e backpressure estão nas fichas #1–#3 do Codex.

### Plano e aceite propostos

Não ação. Se alguém quiser prova de backpressure: teste em ambiente autorizado com ClickHouse lento, com fila cheia e retry observados — fora desta auditoria.

### Comunicação entre responsáveis

Para consolidação: #18 foi encerrada como substituída por otelcol-contrib configurado e MVs; a ausência de build Go customizado é a decisão relatada e registrada no CHANGELOG.

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — um build Go próprio exigiria manter um fork do collector. (b) Que caso o teste ainda não cobre? — ClickHouse lento ou parado com fila cheia. (c) Como eu explicaria isso para outro pod? — "usamos o collector oficial com configuração; a remodelagem acontece no ClickHouse". (d) A redação cobre todos os campos com PII possível?

### Próxima ação e encerramento

Nenhuma. Encerramento: já fechada; reabrir só com requisito que o otelcol-contrib não atenda.

<a id="item-406"></a>

## #19 — [FEATURE] Local Bootstrap Platform (dataship-spark-plat-v0)

Frente: historico. Encaminhamento: historico_substituido_por_reconstrucao_interna.

### Identidade e estado

Issue #19, feature (`type:feature`, `phase:build`, `priority:p1`); autor `luanmorenommaciel` (OWNER); sem assignee. Criada em 2026-05-26; fechada em 2026-09-17T16:45:29Z (`completed`) como "superseded"; 3 comentários.

### Intenção e benefício

Dar à crew uma plataforma local comum (Spark 4.1, Delta, MinIO e ClickHouse para logs), que na época vivia no repositório-sombra `Gabriel-Philot/dataship-spark-plat-v0`, e decidir a governança: integrar, espelhar ou isolar.

### Feito, faltante e não comprovado

Feito por reconstrução: `dev/`, `infra/`, `collect/` e `scripts/apex.ps1` existem em `1e0ba80`, e a busca por "dataship-spark-plat" e "plat-v0" nesses caminhos e no README não encontrou dependência (conferido). O fechamento chama isso de "opção 1 do #23, por reconstrução". Relatado (comentário de 2026-07-13): correções de Windows (volume nomeado para ClickHouse, UTF-8, filtro `--app-name`), o oráculo semanal no Task Scheduler e um achado aberto em `apex-workspace#1`, repositório privado que responde 404 publicamente (fato registrado em DEC-21). Uma delas está presente: o ClickHouse do `infra/docker-compose.yml` usa volume nomeado `ch-data` (linhas 52 e 154) em `1e0ba80` e na main, e não bind mount (conferido). Não comprovado: as demais correções (UTF-8 e filtro de app) no `dev/` atual.

### Linhagem

Feature (2026-05-26) → estudo com fork de evidência (2026-06-08) → progresso cowork (2026-07-13) → reconstrução interna → fechamento. Elos ausentes: decisão registrada do #23 (ver ficha #23 deste lote seguinte); confirmação de que os bugs de Windows corrigidos no plat-v0 (além do volume, já conferido) não reaparecem no `dev/`. Timeline pública (API, observada em 2026-10-17T17:30:45Z; 14 eventos): fechada por `luanmorenommaciel` em 2026-09-17; item adicionado a um Project do GitHub; referências cruzadas na timeline retornada: #29, #34, #35; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 19); [nota](https://github.com/luanmorenommaciel/apex/issues/19#issuecomment-4648524535), [progresso](https://github.com/luanmorenommaciel/apex/issues/19#issuecomment-4963664969), [fechamento](https://github.com/luanmorenommaciel/apex/issues/19#issuecomment-5718024000); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_19.txt`.

### Classe e limite da evidência

DIRETO: diretórios e ausência de referência ao plat-v0 nos caminhos conferidos. RELATADO: bugs e correções de Windows, oráculo semanal. INFERÊNCIA: a reconstrução tornou o repositório-sombra desnecessário para o APEX. NÃO VERIFICADO: `apex-workspace#1`, o próprio repositório plat-v0 e o comportamento Windows do `dev/` atual.

### Fluxo

Fluxo de bootstrap atual: `scripts/apex.ps1 bootstrap` → Compose de `dev/` (Spark/MinIO/History) + `infra/` (ClickHouse) + `collect/` (otelcol) → smoke. Estático.

### Consequências e risco

O risco de ClickHouse em bind mount NTFS, achado em julho, não se aplica ao `infra/` atual, que usa volume nomeado. Outras armadilhas de Windows relatadas (cp1252, job errado em plataforma compartilhada) não foram conferidas; a pendência Windows nativa já tem destino em CL-03 e #174. Confiança alta na remoção da dependência; média sobre Windows.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) levar as demais armadilhas de Windows do relato de julho como casos para CL-03; (c) reabrir — não; a pendência Windows tem destino próprio.

### Dependências e paralelismo

Dependência de prova: CL-03 e #174/#175 cobrem Windows nativo. Não há dependência de código.

### Plano e aceite propostos

Não ação nesta issue. O elo do volume já foi fechado nesta revisão (`fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_19.txt`). Passo mínimo restante, de documentação: anexar ao plano de CL-03 os casos de Windows do relato de julho (codificação e filtro de app) como controles.

### Comunicação entre responsáveis

Para a consolidação: "#19 foi substituída pela plataforma interna; o aprendizado Windows do plat-v0 deve ser cruzado com CL-03".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — voltar a depender do repositório-sombra exigiria reconciliar duas plataformas. Que caso o teste ainda não cobre? — nesta revisão não foram observados Windows nativo, codificação UTF-8 e seleção correta de app; o Compose auditado já usa volume nomeado. Como eu explicaria isso para outro pod? — o fechamento registra reconstrução interna; aprendizados Windows precisam de validação própria em CL-03.

### Próxima ação e encerramento

Nenhuma aqui. Owner a confirmar: Pod 2, ao tratar CL-03. Encerramento: já fechada.

<a id="item-407"></a>

## #20 — [FEATURE] Performance Recommendation Engine

Frente: historico. Encaminhamento: entregue_em_parte_com_residuo_em_issue_aberta.

### Identidade e estado

Issue #20, feature (`type:feature`, `phase:spec`, `priority:p1`); autor `luanmorenommaciel` (OWNER); sem assignee. Criada em 2026-05-26; fechada em 2026-09-17T16:45:31Z (`completed`) com "Closing as implemented (post-deploy half)"; 2 comentários.

### Intenção e benefício

Recomendar otimizações Spark automaticamente: na review de código (pré-merge) e depois do deploy (execuções lentas). Pendia de uma ADR "regras × classificador de ML".

### Feito, faltante e não comprovado

Feito (metade pós-deploy), conferido em `1e0ba80`: `serve/src/apex_mcp/server.py` expõe `analyze_run` (linha 173) e `suggest_fix` (linha 583), e o modelo de proposta fixa `applied: Literal[False]` (`models.py:557`); `watchers/skew.py:333-352` faz o "NO-OP CHECK" contra a configuração do job; `verify/src/apex_verify/` tem `predict.py`, `replay.py` e `safety.py`. Falta: a metade pré-merge, que o fechamento remete à #21, ainda aberta (FATO em C02). Relatado (cowork de julho): ciclo real via cliente MCP com skew 29,2x → 0,0x e bugs do fix gerado por LLM. Não comprovado aqui: esse ciclo, executado fora do repositório.

### Linhagem

Feature (2026-05-26) → cowork com `trigger_diagnosis`/`apply_fix` (2026-07-13) → ferramentas do serve com `applied=False` → fechamento parcial → resíduo na #21. Elo ausente: a ADR "regras × ML", resolvida "na prática" (determinístico primeiro, LLM com gate), sem documento próprio. Nota: as ferramentas `trigger_diagnosis` e `apply_fix` do relato não aparecem no serve atual; ali há `suggest_fix`, que nunca aplica. Timeline pública (API, observada em 2026-10-17T17:30:46Z; 13 eventos): fechada por `luanmorenommaciel` em 2026-09-17; item adicionado a um Project do GitHub; referências cruzadas na timeline retornada: #38, #41, #43; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 20); [progresso](https://github.com/luanmorenommaciel/apex/issues/20#issuecomment-4963665112), [fechamento](https://github.com/luanmorenommaciel/apex/issues/20#issuecomment-5718024679); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_20.txt` (serve, skew watcher, verify em `1e0ba802049b4ebe8fb474a7853c604df2b93aeb`).

### Classe e limite da evidência

DIRETO: ferramentas MCP, `applied` literal falso, NO-OP CHECK, módulos da verify. RELATADO: ciclo MCP real e bugs do LLM. INFERÊNCIA: a política "humano aplica" substituiu o `apply_fix` do protótipo. NÃO VERIFICADO: metade pré-merge (#21) e qualquer runtime.

### Fluxo

Fluxo pós-deploy: execução → watchers (com NO-OP check) → `analyze_run`/`suggest_fix` no MCP (proposta, `requires_human_approval`) → verify (predição, replay, recusa) → humano aplica. Estático.

### Consequências e risco

O fechamento é honesto ao dividir a entrega. Risco: contar #20 como "recomendação completa" esconderia que a revisão de código pré-merge não existe no produto (main de referência). A troca de `apply_fix` por proposta sem aplicação reduz risco operacional; é uma escolha de segurança, não lacuna.

### Alternativas e recomendação

(a) Manter fechada com resíduo em #21 (recomendado); (b) registrar a ADR "determinístico primeiro" como documento; (c) reabrir — duplicaria a #21.

### Dependências e paralelismo

O resíduo depende da #21 (ADIAR na v2). Estudo e implementação pré-merge são independentes do serve atual.

### Plano e aceite propostos

Não ação nesta issue. Se o mantenedor quiser a ADR: documento curto citando `gate.py`, `applied=False` e o NO-OP check.

### Comunicação entre responsáveis

Para a consolidação: "#20 entregou a metade pós-deploy com proposta sem aplicação; a pré-merge está na #21".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — reativar um `apply_fix` automático permitiria alterar código sem revisão humana. (b) Que caso o teste ainda não cobre? — fix gerado por LLM com erro de sintaxe, como o relato de julho mostra. (c) Como eu explicaria isso para outro pod? — "o Apex propõe; um humano aplica". (d) O NO-OP check existe para todos os watchers ou só para skew?

### Próxima ação e encerramento

Nenhuma aqui; o resíduo segue na #21. Encerramento: já fechada.

<a id="item-408"></a>

## #22 — [ADR-001] Go as language for OTel Collector

Frente: historico. Encaminhamento: historico_substituido_sem_objeto.

### Identidade e estado

Issue #22, ADR (`type:adr`, `phase:design`, `priority:p1`); autor `luanmorenommaciel` (OWNER); sem assignee. Criada em 2026-05-26; fechada em 2026-09-17T16:45:33Z (`completed`) como "superseded"; 2 comentários. É a segunda issue chamada "ADR-001" (a primeira é #5) e colide também com o ADR-001 canônico do índice da main; X14 trata essa ambiguidade de números.

### Intenção e benefício

Decidir que o Collector customizado (Stage 02) seria escrito em Go, porque o OTel Collector da CNCF é Go e as necessidades eram PII, backpressure e convenções Spark. Status original: "aguardando ratificação do time".

### Feito, faltante e não comprovado

O fechamento considera a proposta sem objeto porque o collector adotado é config-only, conforme CHANGELOG e evidência de #18. A contagem .go de #8 é zero nas árvores históricas examinadas; isso não afirma ausência de código Go em todo repositório/branch histórico. A ratificação anterior não foi localizada nas fontes lidas.

### Linhagem

ADR (2026-05-26, justificativa de Guilherme de 2026-05-18) → nota de 2026-06-08 ("o slice não altera a decisão"; #29) → collector só de configuração → fechamento. Elo ausente: não encontrei registro da ratificação pedida nas fontes lidas; não chegou a ser necessária. Sem PR ligada. Timeline pública (API, observada em 2026-10-17T17:30:47Z; 11 eventos): fechada por `luanmorenommaciel` em 2026-09-17; item adicionado a um Project do GitHub; referências cruzadas na timeline retornada: #29; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 22); [nota](https://github.com/luanmorenommaciel/apex/issues/22#issuecomment-4648534985); [fechamento](https://github.com/luanmorenommaciel/apex/issues/22#issuecomment-5718025238); evidência compartilhada com #8 e #18 (`fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_8.txt`, `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_18.txt`).

### Classe e limite da evidência

DIRETO: config-only e ausência de .go nas árvores delimitadas de #8/#18. RELATADO: justificativa e encerramento como superseded. Ratificação não verificada no material consultado.

### Fluxo

Fluxo de decisão sem efeito: ADR propõe Go → construção de collector próprio não acontece → `otelcol-contrib` configurado assume a função → fechamento.

### Consequências e risco

Nenhum impacto técnico. Risco de leitura: a sequência de ADRs "001–003" reaparece em #22–#24 com outros assuntos, criando três famílias de números (#5–#8, #22–#24 e `docs/architecture`). Confiança alta.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) citar #22 junto de #5–#8 na seção "Limite deste índice" do ADR-INDEX como exemplo de numeração histórica; (c) reabrir — sem objeto.

### Dependências e paralelismo

Nenhuma. A ambiguidade de numeração é tratada por X14 e pelo índice.

### Plano e aceite propostos

Não ação. Documentação mínima opcional: registrar na consolidação as três famílias de ADR com o mesmo número.

### Comunicação entre responsáveis

Para consolidação: #22 foi encerrada como sem objeto após adoção do collector configurado; o mantenedor relata que não houve build Go customizado.

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — ratificar Go agora levaria a manter um fork do collector sem necessidade. (b) Que caso o teste ainda não cobre? — nenhum; é decisão de linguagem. (c) Como eu explicaria isso para outro pod? — "não escrevemos collector; usamos o oficial configurado". (d) Quantas issues históricas usam números de ADR que colidem com o índice?

### Próxima ação e encerramento

Nenhuma. Encerramento: já fechada; reabrir só se surgir requisito de collector próprio.

<a id="item-409"></a>

## #23 — [ADR-002] Shadow repo governance — dataship-spark-plat-v0

Frente: historico. Encaminhamento: historico_resolvido_por_reconstrucao.

### Identidade e estado

Issue #23, ADR de governança (`type:adr`, `phase:design`, `priority:p0`); autor `luanmorenommaciel` (OWNER); sem assignee. Criada em 2026-05-26; fechada em 2026-09-17T16:45:36Z (`completed`) como "obsolete"; 2 comentários. O número "ADR-002" colide com #6 e com o ADR-002 canônico.

### Intenção e benefício

Decidir o que fazer com a plataforma local criada por Gabriel num repositório pessoal: (1) integrar ao apex, (2) espelhar com acesso compartilhado e sincronização, (3) manter como sandbox pessoal só referenciado.

### Feito, faltante e não comprovado

Resolvido na prática pela opção 1, por reconstrução: `dev/`, `infra/` e `scripts/` existem na main e não referenciam o `plat-v0` (conferido para o #19, `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_19.txt`). O fechamento diz que o `plat-v0` ficou só como evidência externa. Relatado (2026-06-08): a proposta intermediária de usar o fork `gustocezar/dataship-spark-plat-v0` como repositório de evidência e levar só a parte curada. Não verificado: o estado atual dos repositórios externos.

### Linhagem

ADR (2026-05-26, "~47h sem decisão") → duplicata #25 (Commander Attention) → proposta intermediária (2026-06-08) → reconstrução interna em julho → fechamento. Elo ausente: registro da decisão no momento em que foi tomada; o fechamento a reconstrói depois. #19 chama a solução de "opção 1 do #23". Timeline pública (API, observada em 2026-10-17T17:30:49Z; 16 eventos): fechada por `luanmorenommaciel` em 2026-09-17; item adicionado a um Project do GitHub; referências cruzadas na timeline retornada: #29, #30, #33, #40, #19, #25; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 23); [proposta](https://github.com/luanmorenommaciel/apex/issues/23#issuecomment-4648528179); [fechamento](https://github.com/luanmorenommaciel/apex/issues/23#issuecomment-5718026016); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_19.txt`.

### Classe e limite da evidência

DIRETO: plataforma interna e busca sem referência a plat-v0 nos caminhos conferidos. RELATADO: reação Discord, proposta intermediária e integração por reconstrução. NÃO VERIFICADO: decisão contemporânea e estado atual dos repositórios externos.

### Fluxo

Fluxo de governança: plataforma em repositório pessoal → pergunta integrar/espelhar/isolar → reconstrução dentro do apex → repositório externo vira evidência histórica.

### Consequências e risco

Risco documental: as fontes lidas contêm proposta e fechamento retrospectivo, sem registro contemporâneo localizado. Não se conclui que ninguém registrou a decisão em outro local. Custódia de branches e evidência segue #105.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) registrar na consolidação o padrão "decisão por fato consumado" como risco de processo; (c) reabrir — sem objeto.

### Dependências e paralelismo

Nenhuma técnica. A custódia de branches e evidência histórica segue no #105 (bundle de 5 refs com recibo Codex de 2026-10-17: restauração e `fsck` PASS; hash reconferido aqui).

### Plano e aceite propostos

Condição explícita de não ação: a pergunta perdeu o objeto com a reconstrução interna; não há artefato, aceite ou controle a definir. Qualquer tratamento de branches históricas segue no #105.

### Comunicação entre responsáveis

Para consolidação: #23 foi encerrada com integração por reconstrução; o registro contemporâneo de decisão não foi localizado neste recorte.

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — espelhar o repositório externo hoje criaria duas plataformas para manter. (b) Que caso o teste ainda não cobre? — reproduzir resultados antigos do plat-v0 com a plataforma interna. (c) Como eu explicaria isso para outro pod? — "a plataforma do Gabriel foi refeita dentro do APEX; o repositório antigo é só histórico". (d) Onde decisões de governança deveriam ser registradas no momento em que ocorrem?

### Próxima ação e encerramento

Nenhuma ação no repositório. Owner a confirmar: nenhum; custódia de evidência fica com o responsável do #105. Encerramento: já fechada; reabrir só se o APEX voltar a depender de um repositório externo de plataforma.

<a id="item-410"></a>

## #24 — [ADR-003] Intentional deprioritization strategy (bootstrap-before-divergence)

Frente: historico. Encaminhamento: historico_obsoleto_janela_vencida.

### Identidade e estado

Issue #24, ADR de estratégia (`type:adr`, `phase:design`, `priority:p0`); autor `luanmorenommaciel` (OWNER); sem assignee. Criada em 2026-05-26; fechada em 2026-09-17T16:45:38Z (`completed`) como "obsolete"; 2 comentários. Número "ADR-003" colide com #7 e com o ADR-003 canônico.

### Intenção e benefício

Registrar a proposta da Crew A de despriorizar entregas do Commander em favor de um período de nivelamento e de uma plataforma e fonte de dados comuns, "andar devagar no começo". Pedia revisão do Commander antes da reunião de terça.

### Feito, faltante e não comprovado

Obsoleto segundo o fechamento: a janela do Tuesday sync de maio passou. #24 não fixa dia do mês; o fechamento relacionado de #26 cita 2026-05-27, uma quarta-feira, de modo que as referências de calendário não coincidem. Executed and vindicated é avaliação retrospectiva do mantenedor; a data de release 29/07 no CHANGELOG não prova aprovação prévia.

### Linhagem

Proposta (2026-05-25, via Discord) → duplicata #26 (Commander Attention) → nota de 2026-06-08 (o slice como evidência do valor da estratégia; #29) → release v0.1.0 → fechamento. Elo ausente: a resposta do Commander à proposta; não está registrada em nenhum objeto consultado. Timeline pública (API, observada em 2026-10-17T17:30:50Z; 12 eventos): fechada por `luanmorenommaciel` em 2026-09-17; item adicionado a um Project do GitHub; referências cruzadas na timeline retornada: #29, #26; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 24); [nota](https://github.com/luanmorenommaciel/apex/issues/24#issuecomment-4648535209); [fechamento](https://github.com/luanmorenommaciel/apex/issues/24#issuecomment-5718026536); CHANGELOG conferido em `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_15.txt`.

### Classe e limite da evidência

DIRETO: datas e textos. RELATADO: proposta no Discord e sua mensagem. INFERÊNCIA (do mantenedor): "vindicated". Não há evidência técnica a conferir além da data da release.

### Fluxo

Fluxo de decisão de processo: Crew propõe baseline antes de divergir → Commander deveria aprovar ou contestar → janela passa → estratégia executada → avaliação retrospectiva no fechamento.

### Consequências e risco

Nenhum impacto técnico. Risco de processo: a decisão de priorização ficou sem registro de aceite, só com avaliação posterior.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) reabrir — sem objeto, pois a janela venceu.

### Dependências e paralelismo

Nenhuma dependência técnica: a decisão era de prioridade de time, e o que dela restava (plataforma comum) foi entregue por #19/#23.

### Plano e aceite propostos

Condição de não ação: decisão de processo de maio, superada pelo tempo.

### Comunicação entre responsáveis

Para a consolidação: "#24 venceu sem decisão registrada; o mantenedor a avaliou como acertada em setembro".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — reabrir uma decisão de processo de maio só produziria ruído. (b) Que caso o teste ainda não cobre? — não encontrei teste ligado a este item nas fontes lidas; é decisão de priorização. (c) Como eu explicaria isso para outro pod? — "o time escolheu nivelar antes de dividir, e isso deu certo segundo o mantenedor". (d) Quem aprovava mudanças de prioridade naquela fase?

### Próxima ação e encerramento

Nenhuma ação ou owner nesta ficha histórica. Encerramento confirmado; o sync de maio já havia passado em setembro. A data 27/05 relatada em #26 e a menção Tuesday em #24 divergem no calendário.

