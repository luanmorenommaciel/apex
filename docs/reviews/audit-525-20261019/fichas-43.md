# Fichas documentais — lote 43

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-421"></a>

## #36 — [TASK] Implementar SparkListener MVP para telemetria Apex

Frente: historico. Encaminhamento: concluida_mas_fechada_antes_do_merge_da_prova.

### Identidade e estado

Issue #36, tarefa (`type:task`, `phase:build`, `priority:p0`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-07-04; fechada em 2026-08-21T00:37:03Z pelo próprio autor "sujeito a review do PR #91"; 1 comentário.

### Intenção e benefício

Criar um SparkListener básico, ponto de captura da V0.1, com envelope mínimo, identificadores de app/job/stage/task, sinais para diagnóstico simples, sem depender de DataFlint, e sem quebrar o job em caso de falha.

### Feito, faltante e não comprovado

Feito, mas com uma ordem de eventos que importa: o comentário diz que o último item do DoD (falha do listener não quebra o job) foi provado pela PR #91, com `ThrowingSink` num SparkContext real e 30/30 testes nas quatro células. Conferi: em `7c5460c` (main no fechamento) a classe `ThrowingSink` **não existe**; ela está em `jar/src/test/scala/apex/ListenerFailureIsolationSpec.scala:43` em `1e0ba80`. A PR #91 foi criada em 2026-08-21 e integrada em 2026-09-14 (`pulls_all.json`), 24 dias depois do fechamento. Ressalva registrada pelo autor: não há doc específico de "campos do listener" além do `CONTRACT.md` v0.5.

### Linhagem

Tarefa (2026-07-04) → listener com `Try` em cada callback (código) → evidência do "six-lane real" de 2026-08-11/12 (relato) → PR #91 aberta (2026-08-21) → fechamento no mesmo dia → PR #91 integrada (2026-09-14). Elo invertido: a issue fechou antes de a prova entrar na main. Timeline pública (API, observada em 2026-10-17T17:31:04Z; 9 eventos): fechada por `gustocezar` em 2026-08-21; referências cruzadas na timeline retornada: PR#91; eventos `referenced` com commit na timeline retornada: 79a23d2cd8, eb73b6e81c.

### Fontes e corte

Snapshot (item 36); [evidência e ressalva](https://github.com/luanmorenommaciel/apex/issues/36#issuecomment-5363756043); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_36.txt` (ausência de `ThrowingSink` em `7c5460c87421d7f9493a664acb1cfbcc54259b51` e presença em `1e0ba802049b4ebe8fb474a7853c604df2b93aeb`; `Try` no listener); ficha PR#91 deste pacote.

### Classe e limite da evidência

DIRETO: datas de fechamento e de merge; ausência e presença do teste nos dois SHAs. RELATADO: saídas `WARN … injected-test-failure`, 30/30 testes, 20/20 spans via OTLP. Não verificado aqui: execução do teste ou de CI daquela época.

### Fluxo

Fluxo de isolamento de falha: callback do listener → `Try` → `emit` do sink lança → `WARN` com stage e causa → job segue até `exitCode 0`; o listener continua no bus nos jobs seguintes.

### Consequências e risco

O teste citado entrou na main com a PR #91, após um intervalo de 24 dias desde o fechamento. Isso resolve a lacuna de integração do artefato, sem certificar nesta auditoria sua execução ou todos os itens do DoD. A ressalva de documentação dos campos foi explicitada pelo autor.

### Alternativas e recomendação

(a) Manter fechada e registrar a ordem invertida (recomendado); (b) responder à ressalva sobre campos do listener apontando o `CONTRACT.md` como fonte única; (c) reabrir — sem motivo, porque a prova já está na main.

### Dependências e paralelismo

Nenhuma pendente; a única dependência (PR #91) foi integrada.

### Plano e aceite propostos

Não ação. Se o mantenedor quiser fechar a ressalva: nota curta dizendo que o `CONTRACT.md` §1 é a documentação dos campos emitidos pelo listener.

### Comunicação entre responsáveis

Para consolidação: #36 foi encerrada em 21/08 sujeita à review da PR #91; o teste citado entrou na main em 14/09. Resultados de execução seguem como evidência relatada.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — remover o isolamento Try dos callbacks poderia permitir propagação de falhas do sink; o teste documenta o cenário pretendido. Que caso o teste ainda não cobre? — a revisão não verificou falha no onExecutorMetricsUpdate sob carga real. Como eu explicaria isso para outro pod? — o fechamento citou uma prova ainda em PR; o artefato foi integrado depois, sem reexecução nesta auditoria.

### Próxima ação e encerramento

Nenhuma. Encerramento: já fechada; condição de reabertura: o teste de isolamento sair da main ou falhar.

<a id="item-422"></a>

## #37 — [TASK] Integrar SparkListener ao ClickStack MVP

Frente: historico. Encaminhamento: concluida_com_evidencia_anexada.

### Identidade e estado

Issue #37, tarefa (`type:task`, `phase:build`, `priority:p0`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-07-04; fechada em 2026-08-20T18:22:22Z pelo próprio autor com evidência; 1 comentário.

### Intenção e benefício

Levar eventos do SparkListener ao ClickStack, persistir eventos mínimos, consultar por `job_id` e documentar o schema temporário da V0.1, com falhas de envio visíveis em log e referência no #4.

### Feito, faltante e não comprovado

Feito, com evidência anexada: consulta relatada de 20 spans em `apex.otel_traces` para `app-20260812002731-0000`, 20 linhas em `apex.spark_events` pela MV `mv_spark_events`, schema em `CONTRACT.md` v0.5 (PR #80) e configuração de envio. Conferi em `7c5460c`: `collect/ddl/30_mv_spark_events.sql` existe; `CONTRACT.md` declara "contract v0.5" (linha 7); `collect/config.yaml` tem `file_storage` (linha 13), `sending_queue` com `storage: file_storage` (72–78), `retry_on_failure` (83) e `level: info` (104). A PR #80 entrou em 2026-08-18, antes do fechamento. O autor também comentou no #4 (consta em `comments_mentioning_this`).

### Linhagem

Tarefa (2026-07-04) → collector com fila persistente → PR #80 (contrato v0.5, 2026-08-18) → execução relatada (app de 2026-08-12) → evidência e fechamento (2026-08-20) → comentário no #4. Timeline pública (API, observada em 2026-10-17T17:31:05Z; 8 eventos): fechada por `gustocezar` em 2026-08-20; referências cruzadas na timeline retornada: #4; eventos `referenced` com commit na timeline retornada: 79a23d2cd8.

### Fontes e corte

Snapshot (item 37); [evidência](https://github.com/luanmorenommaciel/apex/issues/37#issuecomment-5359987640); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_37.txt` (config, MV e contrato em `7c5460c87421d7f9493a664acb1cfbcc54259b51`).

### Classe e limite da evidência

DIRETO: configuração do exporter, existência da MV, versão do contrato. RELATADO: contagens 20/20 e consultas SQL executadas localmente. INFERÊNCIA (do autor): o `otelcol-contrib` loga erro de exportação com `level: info`; não houve teste de falha de envio.

### Fluxo

Fluxo de persistência: listener → OTLP/HTTP → collector (fila em disco, retry) → `apex.otel_traces` → `mv_spark_events` → `apex.spark_events` → consulta por `job_id`/stage.

### Consequências e risco

A fonte contém execução de persistência relatada e configuração estática correspondente. A revisão não reexecutou consultas nem falha de exportação; visibilidade de falha segue inferência do autor, e durabilidade efetiva não é certificada por presença de file_storage.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) prova barata de visibilidade: parar o ClickHouse e ver o erro do exporter — fora desta auditoria; (c) reabrir — desproporcional.

### Dependências e paralelismo

Nenhuma pendente. A resiliência do collector também aparece nas fichas #1–#3 do Codex.

### Plano e aceite propostos

Não ação. Se alguém quiser fechar a ressalva: teste de falha induzida em ambiente autorizado, com o log de erro do exporter como recibo.

### Comunicação entre responsáveis

Para a consolidação: "#37 fechada com evidência de persistência; a visibilidade de falha é inferida da configuração".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — remover a fila persistente aumentaria o risco de perder itens pendentes durante restart, dependendo do estado e da recuperação. Que caso o teste ainda não cobre? — ClickHouse indisponível durante ingestão e recuperação após restart não foram observados nesta auditoria. Como eu explicaria isso para outro pod? — o autor relatou 20 spans propagados pela MV; há fila/retry configurados, mas a falha de envio não foi induzida na evidência lida.

### Próxima ação e encerramento

Nenhuma ação obrigatória. Owner a confirmar: Pod 2, se quiser a prova de falha induzida. Entrada: ambiente autorizado. Saída: log de erro do exporter. Encerramento: já fechada; reabrir só se spans se perderem sem log.

<a id="item-423"></a>

## #38 — [TASK] Criar diagnostico CrewAI/MCP por job_id

Frente: historico. Encaminhamento: fechada_com_perguntas_do_autor_sem_resposta.

### Identidade e estado

Issue #38, tarefa (`type:task`, `phase:build`, `priority:p0`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-07-04; fechada em 2026-09-17T16:46:05Z por `luanmorenommaciel` como "implemented"; 2 comentários.

### Intenção e benefício

Receber `job_id`, consultar a telemetria, produzir diagnóstico curto com evidências, problema provável, causa, recomendação e confiança, expor por MCP e nunca aplicar mudança sem aprovação.

### Feito, faltante e não comprovado

Em 1e0ba80 há as oito definições de ferramentas citadas e caminhos de demo; suggest_fix é proposta conforme #20. O autor relata em 21/08 gate escalado, crew não instalado e llm_calls=0 naquele ambiente. O fechamento de 17/09 declara integração com crew real, mas não anexa resposta LLM. Essa diferença não comprova contradição: não há execução posterior demonstrada nem prova de ausência global. A busca no schema encontra cause apenas em comentários; não foi localizada resposta explícita à pergunta de campo estruturado nas fontes desta ficha.

### Linhagem

Tarefa (2026-07-04) → teste do autor (2026-08-21) com duas perguntas aos mantenedores → fechamento (2026-09-17) que não responde a nenhuma das duas. Elos ausentes: uma resposta real do crew com LLM; decisão sobre o campo de causa. Timeline pública (API, observada em 2026-10-17T17:31:06Z; 8 eventos): fechada por `luanmorenommaciel` em 2026-09-17; referências cruzadas na timeline retornada: nenhuma; eventos `referenced` com commit na timeline retornada: 79a23d2cd8.

### Fontes e corte

Snapshot (item 38); [teste e perguntas](https://github.com/luanmorenommaciel/apex/issues/38#issuecomment-5364265881); [fechamento](https://github.com/luanmorenommaciel/apex/issues/38#issuecomment-5718032619); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_38.txt` (ferramentas MCP, demo e schema em `1e0ba802049b4ebe8fb474a7853c604df2b93aeb`).

### Classe e limite da evidência

DIRETO: ferramentas, demo e ausência de `root_cause` estruturado. RELATADO: roteamento do gate escalando de fato (`gate_trace`), sem LLM. INFERÊNCIA: "real CrewAI crew" descreve o código, não uma execução comprovada.

### Fluxo

Fluxo: `job_id` → `analyze_run` → watchers → gate → (crew, se instalado e com credencial) → `Diagnosis`; sem crew, o finding Tier 1 é preservado com motivo registrado.

### Consequências e risco

Risco de alegação: a configuração de crew e o relato de gate sem LLM não comprovam resposta real. A revisão também não certifica execução determinística; ambas dependem dos recibos e de seus ambientes.

### Alternativas e recomendação

(a) Manter fechada e registrar as duas perguntas como resíduo (recomendado); (b) capturar uma execução real do crew em ambiente autorizado, com credencial própria, se a release citar diagnóstico por LLM; (c) decidir se causa vira campo estruturado (código novo, segundo o autor).

### Dependências e paralelismo

A opção (b) depende de credencial e ambiente autorizados; (c) depende de decisão de contrato do `Finding`. As duas são independentes entre si e da fila M1.

### Plano e aceite propostos

Passos mínimos, se o mantenedor quiser: (1) responder às duas perguntas na consolidação; (2) para (b), recibo com modelo, tokens e resposta, sem segredo; controle negativo: sem credencial, `llm_calls` deve continuar 0 e o finding Tier 1 preservado.

### Comunicação entre responsáveis

Para consolidação: #38 tem oito ferramentas estáticas e foi declarada implementada; esta ficha não fornece recibo de resposta real do crew, e as duas perguntas do autor não têm resposta explícita nas fontes lidas.

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — anunciar diagnóstico por LLM sem uma execução real exporia uma alegação sem prova. (b) Que caso o teste ainda não cobre? — o crew respondendo com credencial válida e saída `Finding` válida. (c) Como eu explicaria isso para outro pod? — "o MCP responde por job_id; a parte com LLM existe no código, mas não há registro de execução real nas fontes lidas". (d) Causa deve ser campo próprio ou texto dentro de `impact`?

### Próxima ação e encerramento

Owner a confirmar: mantenedor, para responder às duas perguntas. Entrada: este registro. Saída: resposta registrada. Encerramento: a issue segue fechada; o resíduo é de alegação, não de código.

<a id="item-424"></a>

## #39 — [TASK] Coletar percepcao DataFlint de cada membro da Crew A

Frente: historico. Encaminhamento: historico_substituido_estudo_em_branch.

### Identidade e estado

Issue #39, tarefa (`type:task`, `phase:review`, `documentation`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-07-04; fechada em 2026-09-17T16:46:08Z por `luanmorenommaciel` como "superseded"; 1 comentário.

### Intenção e benefício

Cada membro olhar o DataFlint e escrever um documento curto separando fato oficial, percepção técnica e sugestão para o Apex, com uma síntese e as divergências para decisão do Commander.

### Feito, faltante e não comprovado

O mantenedor declara substituição por estudo na branch e conclusões na main. O extrato confirma arquivos em docs/estudos/dataflint, frases comparativas no CONTRACT e menções SimilarWeb na verify. Autoria e conjunto completo de entregas individuais não foram conferidos; o DoD por membro e a síntese não estão demonstrados por essa listagem.

### Linhagem

Pedido do Commander (reunião de 2026-06-30) → tarefa (2026-07-04) → estudo na branch `estudo/dataflint` → conclusões no contrato e na verify → fechamento. Elo ausente: documentos individuais e síntese. A branch também contém o commit `8ec2d39` do slice de skew (conferido para o #29). Timeline pública (API, observada em 2026-10-17T17:31:07Z; 7 eventos): fechada por `luanmorenommaciel` em 2026-09-17; referências cruzadas na timeline retornada: nenhuma; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 39); [fechamento](https://github.com/luanmorenommaciel/apex/issues/39#issuecomment-5718033064); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_39.txt` (arquivos da branch, `CONTRACT.md` e `verify/` em `1e0ba802049b4ebe8fb474a7853c604df2b93aeb`).

### Classe e limite da evidência

DIRETO: arquivos da branch e trechos da main. RELATADO: "conclusions baked into main". INFERÊNCIA: as afirmações comparativas sobre DataFlint na main são de autoria da equipe, não fatos oficiais do DataFlint; a issue pedia justamente essa separação.

### Fluxo

Fluxo do estudo: análise do DataFlint → documento comparativo na branch → argumentos no `CONTRACT.md` (transições de AQE como sinal causal) e na verify (caso SimilarWeb).

### Consequências e risco

Baixo. Risco: frases comparativas como "beats DataFlint" estão no contrato sem a separação fato/percepção que a issue exigia. Não é defeito de produto.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) marcar as comparações no `CONTRACT.md` como percepção da equipe — decisão editorial; (c) preservar a branch `estudo/dataflint`, que não está entre os 5 refs do bundle do #105 (o head `8953cbe` não está contido em nenhum deles).

### Dependências e paralelismo

A preservação da branch `estudo/dataflint` não é coberta pelo bundle atual do #105 (5 refs; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/reconferencia/ponto12-bundle-105.txt`); incluí-la ou não é decisão do custodiante do #105. Não há dependência técnica.

### Plano e aceite propostos

Não ação. Nota editorial opcional sobre as afirmações comparativas.

### Comunicação entre responsáveis

Para consolidação: #39 foi substituída pelo estudo referido em estudo/dataflint; a revisão não verificou cumprimento do pedido de percepções individuais nem sua autoria.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — excluir a branch sem outra custódia poderia retirar acesso ao estudo; o head 8953cbe não aparece contido nos cinco refs examinados. Que caso o teste ainda não cobre? — é estudo documental; não foi verificada a sustentação oficial das comparações de mercado. Como eu explicaria isso para outro pod? — há estudo na branch e alegações comparativas no contrato; não foram verificadas entregas individuais nem as capacidades atuais do DataFlint.

### Próxima ação e encerramento

Nenhuma. Owner a confirmar: custodiante do #105 para a branch. Encerramento: já fechada.

<a id="item-425"></a>

## #40 — [TASK] Inventariar branches e evidencias existentes para V0.1

Frente: historico. Encaminhamento: encerrada_em_favor_de_sucessora_105.

### Identidade e estado

Issue #40, tarefa (`type:task`, `phase:review`, `priority:p1`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-07-04; fechada em 2026-09-17T16:46:10Z por `luanmorenommaciel` "in favor of #105"; 1 comentário.

### Intenção e benefício

Inventariar branches e forks relevantes (inclusive o fork de Gabriel e o material de Augusto), dizer o que cada um entrega e recomendar merge, cherry-pick, reimplementação ou descarte para a V0.1.

### Feito, faltante e não comprovado

Fechamento transfere a tarefa para #105 e relata cerca de 40 branches remotas. O extrato local registra 86 refs fora de pr/*; sua diferença pode envolver datas e refs locais retidos, mas a causa não foi demonstrada e a contagem já exclui pr/*. O recibo ponto12 informa hash conferente e cinco heads de bundle; não foram recalculados nem restaurados nesta revisão. O DoD branch a branch não é comprovado por essa listagem.

### Linhagem

Tarefa (2026-07-04) → referências cruzadas de #25 e #26 → reconstrução da plataforma → sucessora #105 → fechamento. Elo de destino: #105 (aberta na v2; bundle conferido pelo Codex). Timeline pública (API, observada em 2026-10-17T17:31:08Z; 7 eventos): fechada por `luanmorenommaciel` em 2026-09-17; referências cruzadas na timeline retornada: nenhuma; eventos `referenced` com commit na timeline retornada: 79a23d2cd8.

### Fontes e corte

Snapshot (item 40); [fechamento](https://github.com/luanmorenommaciel/apex/issues/40#issuecomment-5718033520); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_40.txt` (contagem de refs remotas no clone).

### Classe e limite da evidência

DIRETO: fechamento, listagem/contagem do extrato e recibo documental de cinco heads. RELATADO: cerca de 40 branches no fechamento e verificações de custódia anteriores. NÃO VERIFICADO: heads remotos atuais e razão da diferença de contagens.

### Fluxo

Fluxo de custódia: branches e forks → inventário → arquivamento (bundle + mapa branch→SHA) → só então exclusão.

### Consequências e risco

Baixo. O risco real (perder trabalho ao apagar branches) foi transferido à #105 com plano explícito.

### Alternativas e recomendação

(a) Manter fechada com destino na #105 (recomendado); (b) reabrir — duplicaria a #105.

### Dependências e paralelismo

Depende da #105 (aberta) e da custódia do bundle conferida pelo Codex (C04-19); não há dependência técnica de produto.

### Plano e aceite propostos

Condição explícita de não ação nesta issue: o inventário e qualquer exclusão de branch seguem na #105, que exige consulta dos heads remotos antes de apagar.

### Comunicação entre responsáveis

Para a consolidação: "#40 foi substituída pela #105; o fechamento contava ~40 branches remotas".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — excluir refs sem confrontar heads e custódia poderia perder trabalho fora do bundle. Que caso o teste ainda não cobre? — branches novas e heads alterados após a captura. Como eu explicaria isso para outro pod? — o inventário foi transferido para #105; cinco heads constam do recibo de bundle, sem equivaler a inventário remoto completo.

### Próxima ação e encerramento

Nenhuma ação aqui. Owner a confirmar: custodiante da #105. Encerramento definitivo, com destino na #105; não há condição própria de reabertura.

<a id="item-426"></a>

## #41 — [TASK] Definir contratos agenticos: memoria, RAG, skills, harness e contexto

Frente: historico. Encaminhamento: historico_preservado_contrato_distribuido.

### Identidade e estado

Issue #41, tarefa de contrato (`type:task`, `phase:design`, `priority:p1`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-07-04; fechada em 2026-09-17T16:46:12Z por `luanmorenommaciel` como "implemented"; 1 comentário. #103, #107 e #112 a citam.

### Intenção e benefício

Definir o que entra no contexto agentic, separar memória, RAG, skills e harness, criar um contrato mínimo de entrada e saída do diagnóstico, e decidir quando usar regra, agente ou humano, com guardrails contra alucinação.

### Feito, faltante e não comprovado

O fechamento aponta contrato distribuído por raias. Trechos em 1e0ba80 registram intenção de abstenção e recusa; #38 confirma ferramentas e #32 a classe Coverage. O documento único e o alinhamento contemporâneo com validation_criteria não foram localizados neste recorte. Isso não prova inexistência de outro documento ou ausência de lógica equivalente.

### Linhagem

Tarefa (2026-07-04) → raias memory/serve/verify → referências de #103, #107 e #112 → fechamento. Elo ausente: o documento de contrato agentic único e o alinhamento com o #32. Timeline pública (API, observada em 2026-10-17T17:31:09Z; 11 eventos): fechada por `luanmorenommaciel` em 2026-09-17; referências cruzadas na timeline retornada: #103, #106, #107, #112; eventos `referenced` com commit na timeline retornada: 79a23d2cd8.

### Fontes e corte

Snapshot (item 41); [fechamento](https://github.com/luanmorenommaciel/apex/issues/41#issuecomment-5718034035); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_41.txt` (memory, guardrails) e `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_38.txt` (ferramentas do serve).

### Classe e limite da evidência

DIRETO: superfícies e textos citados. RELATADO: "ZEST-style recall", "enforced". INFERÊNCIA: o contrato existe como soma de partes, não como documento. NÃO VERIFICADO: comportamento de abstenção em runtime.

### Fluxo

Fluxo agentic: telemetria → watchers (regra) → gate (confiança e severidade) → crew (agente) ou humano (aprovação) → memória (recall com abstenção) → verify (recusa como saída válida).

### Consequências e risco

Confiança alta na existência dos trechos citados e no encerramento. A soma de arquivos e comentários não certifica enforcement em runtime, completude do contrato curto ou alinhamento com todos os critérios de #32.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) um índice curto apontando as quatro superfícies, como documentação; (c) reabrir — sem ganho.

### Dependências e paralelismo

Nenhuma técnica; um índice dependeria só de leitura do código.

### Plano e aceite propostos

Não ação. Documentação mínima opcional: página-índice "contratos agentic" com links para gate, memória, verify e `Coverage`.

### Comunicação entre responsáveis

Para consolidação: #41 foi declarada implementada em superfícies distribuídas; documento único e alinhamento integral com #32 não foram demonstrados nesta revisão.

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — um agente sem fronteira de aprovação poderia aplicar mudanças. (b) Que caso o teste ainda não cobre? — memória abstendo-se quando não há run parecido. (c) Como eu explicaria isso para outro pod? — "regra primeiro, agente com gate, humano aprova, verify pode recusar". (d) Onde um novo membro lê o contrato agentic inteiro?

### Próxima ação e encerramento

Nenhuma ação obrigatória. Owner a confirmar: mantenedor, se quiser o índice de contratos agentic. Entrada: as quatro superfícies citadas. Saída: página-índice. Encerramento: já fechada; reabrir só se uma das fronteiras (gate, aprovação humana, recusa) for removida.

<a id="item-427"></a>

## #43 — [SPIKE] Desenhar UI local de DAG, replay e simulacao para pos-V0.1

Frente: historico. Encaminhamento: spike_concluido_com_escopo_reduzido.

### Identidade e estado

Issue #43, spike (`type:task`, `phase:design`, `priority:p2`, `pod-1-front-end`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-07-04; fechada em 2026-09-17T16:46:15Z por `luanmorenommaciel` como "implemented (spike)"; 1 comentário. O #108 a cita como spike histórico de UI.

### Intenção e benefício

Desenhar a UI local pós-V0.1: visualizar DAG, depurar ambiente, fazer replay e simular código novo a partir das estatísticas capturadas, sem bloquear a V0.1.

### Feito, faltante e não comprovado

Em 1e0ba80 existe UI43-B e o comentário no caminho correto front/src/components/molecules/LayerTabs.tsx explica a falta de arestas entre stages em v0.5. O fechamento relata seis telas, wireflows, contratos e exclusão deliberada de replay. O extrato fornecido não lista front/src/screens nem lê o documento inteiro; portanto essas partes e o destino da simulação não foram confirmados independentemente.

### Linhagem

Spike de julho → documento e código citados → fechamento em setembro; #108 faz referência cruzada. O recorte não estabelece a linhagem completa de cada tela nem demonstra ausência de desenho de simulação em outros documentos.

### Fontes e corte

Snapshot (item 43); [fechamento](https://github.com/luanmorenommaciel/apex/issues/43#issuecomment-5718034487); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_43.txt` (documento, telas e `LayerTabs.tsx` em `1e0ba802049b4ebe8fb474a7853c604df2b93aeb`).

### Classe e limite da evidência

DIRETO: documento, telas e o comentário no código. RELATADO: "wireflows, per-screen data contracts" (o conteúdo do documento não foi lido inteiro aqui). INFERÊNCIA: a UI entregue é de leitura (compare/memory/verify), não de simulação.

### Fluxo

Fluxo da UI: Runs → RunDetail (camadas, sem DAG) → Compare / Memory / Verify / Ask, todos de leitura.

### Consequências e risco

O comentário de código torna explícito o limite de arestas para aquele contrato. A completude do desenho pedido e a situação da simulação permanecem não verificadas no material lido.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) registrar "simulação" como fora da v1 na consolidação; (c) reabrir — sem demanda.

### Dependências e paralelismo

Uma eventual DAG depende de mudança de contrato (arestas entre stages), assunto do #106/#108, não daqui.

### Plano e aceite propostos

Não ação. Nota opcional na consolidação: a simulação pedida no spike não tem destino.

### Comunicação entre responsáveis

Para consolidação: #43 foi encerrada como spike implementado; documento e limite do DAG são corroborados, enquanto telas, wireflows e exclusão de replay são relatos do fechamento.

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — desenhar arestas sem dado no contrato mostraria um grafo inventado. (b) Que caso o teste ainda não cobre? — a tela RunDetail com stages de várias tentativas. (c) Como eu explicaria isso para outro pod? — "a UI mostra o que a telemetria prova; o DAG não está no contrato". (d) Quem decide se a simulação entra no roadmap?

### Próxima ação e encerramento

Nenhuma ação obrigatória. Owner a confirmar: Pod 1, se a simulação voltar ao roadmap. Encerramento: já fechada; reabrir só com decisão de produto sobre simulação ou com arestas de stage no contrato.

<a id="item-428"></a>

## #55 — tracking(v1): decisões finais e evoluções após ENGINE/SERVE

Frente: historico. Encaminhamento: historico_substituido_decisoes_assentadas_com_residuo.

### Identidade e estado

Issue #55, acompanhamento da V1 (sem rótulos); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-07-24; fechada em 2026-09-17T16:46:17Z por `luanmorenommaciel` como "superseded"; 1 comentário. Ligada ao registro E12.

### Intenção e benefício

Registrar as decisões finais da V1 depois de ENGINE e SERVE: revisar a branch `base-project-e2e-augusto` como pacote, decidir gate determinístico × cadeia Haiku→Sonnet→Opus, decidir `suggest_fix` sem aplicação, definir a integração e reexecutar o gate C9; listar evoluções que não bloqueavam a V1.

### Feito, faltante e não comprovado

O mantenedor declara decisões assentadas e integração por PRs posteriores. O extrato confirma engine/README com gate determinístico→Sonnet/Opus e divergência 181/21 até 1e0ba80; fontes relacionadas mostram proposta sem aplicação. Não foram verificados nesta ficha a revisão do pacote inteiro, a reexecução C9 e o mapeamento completo das sete evoluções. Falta de registro aqui não prova que nunca ocorreram.

### Linhagem

Pacote na branch Augusto (2026-07-24) → PRs #52–#54 fechadas sem merge → #56 sobre o commit `093c677` → PRs posteriores levam o conteúdo → fechamento. Elos ausentes: decisão explícita sobre a cadeia Haiku (substituída na prática pelo gate) e destino das evoluções listadas. Timeline pública (API, observada em 2026-10-17T17:31:11Z; 4 eventos): fechada por `luanmorenommaciel` em 2026-09-17; referências cruzadas na timeline retornada: #56, #34; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 55); [fechamento](https://github.com/luanmorenommaciel/apex/issues/55#issuecomment-5718034925); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_55.txt` (ref da branch, contagem 181/21, `engine/README.md` em `1e0ba802049b4ebe8fb474a7853c604df2b93aeb`).

### Classe e limite da evidência

DIRETO: divergência da branch, textos do engine e do serve. RELATADO: "content landed via later PRs". INFERÊNCIA: a escolha determinístico-primeiro respondeu à pergunta Haiku sem registro de decisão. NÃO VERIFICADO: o gate C9 na base atual.

### Fluxo

Fluxo de fechamento da V1: branch Augusto com extensões → revisão do Commander (não registrada como pacote) → integração por PRs separadas → main com gate determinístico e proposta sem aplicação.

### Consequências e risco

A lista de evoluções está preservada no corpo e pode orientar comparação com backlog posterior. Seu destino individual não foi demonstrado nesta ficha. A branch é candidata a poda segundo o mantenedor, e o recibo informa contenção do head 3d4b05b em ref do bundle; isso não autoriza exclusão nem prova completude de toda evidência.

### Alternativas e recomendação

(a) Manter fechada e transferir a lista de evoluções para a consolidação como backlog candidato (recomendado); (b) reabrir — o núcleo de decisões está assentado; (c) ignorar a lista — perderia itens como o loop guardado apply→rerun.

### Dependências e paralelismo

A poda da branch depende da decisão do #105; o conteúdo já está no bundle. Cada evolução, se retomada, é trabalho independente.

### Plano e aceite propostos

Passo mínimo documental: mapear as sete evoluções para issues atuais ou marcá-las "sem destino" na consolidação. Nenhuma execução.

### Comunicação entre responsáveis

Para consolidação: #55 foi encerrada com decisões declaradas assentadas; a arquitetura determinística está documentada, e o destino individual das sete evoluções não foi estabelecido nesta revisão.

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — reintroduzir a cadeia Haiku mudaria custo e latência sem decisão registrada. (b) Que caso o teste ainda não cobre? — o gate C9 das ferramentas MCP na main atual. (c) Como eu explicaria isso para outro pod? — "as decisões da V1 estão no código; a lista do que vinha depois ficou solta". (d) Quais das sete evoluções ainda importam?

### Próxima ação e encerramento

Owner a confirmar: mantenedor, para o destino das evoluções. Entrada: lista do corpo. Saída: mapa evolução → issue ou "sem destino". Encerramento: a issue segue fechada; reabrir só se uma decisão da V1 for revertida.

<a id="item-429"></a>

## #56 — tracking(e2e): decidir incorporação de 093c677 na branch Augusto

Frente: historico. Encaminhamento: historico_sem_objeto_commit_ja_na_main.

### Identidade e estado

Issue #56, acompanhamento (sem rótulos); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-07-26; fechada em 2026-09-17T16:46:19Z por `luanmorenommaciel` como "superseded"; 1 comentário.

### Intenção e benefício

Pedir ao Commander a decisão de incorporar o commit `093c677` (seam injetável `full_analyzer` no gate E2E) à branch Augusto antes da próxima rodada E2E, sem rebase automático.

### Feito, faltante e não comprovado

Sem objeto: o fechamento diz que `093c677` é ancestral da main e que a seam está viva. Conferi: `git merge-base --is-ancestor 093c677 1e0ba80` retorna 0; o commit é de 2026-07-24; `full_analyzer` aparece em `scripts/e2e_six_lanes.py:110-147` e em `tests/test_e2e_six_lanes.py:82-84`. A pergunta sobre a branch Augusto perdeu o sentido com o #55. O aceite proposto (repetir `pytest tests/test_e2e_six_lanes.py` e registrar) não foi registrado; não é mais necessário para a branch abandonada.

### Linhagem

Commit de 24/07 → pedido de 26/07 → ancestralidade confirmada em 1e0ba80 → fechamento como superseded. A decisão específica de incorporação na branch Augusto não foi localizada; o fechamento considera a pergunta sem objeto após #55.

### Fontes e corte

Snapshot (item 56); [fechamento](https://github.com/luanmorenommaciel/apex/issues/56#issuecomment-5718035360); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_56.txt` (ancestralidade e linhas da seam em `1e0ba802049b4ebe8fb474a7853c604df2b93aeb`).

### Classe e limite da evidência

DIRETO: ancestralidade e presença da seam. NÃO VERIFICADO: execução do teste citado (não executado nesta auditoria).

### Fluxo

Fluxo do gate E2E: `e2e_six_lanes.py` → análise determinística e `full_analyzer` (injetável em teste, AQE-inclusive em produção) → comparação com findings esperados.

### Consequências e risco

O commit e a seam estão no SHA de main auditado, sem execução certificada. O fechamento considera superada a incorporação na branch, que #55 chama de candidata a poda; não se infere abandono definitivo ou ausência de qualquer decisão anterior.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) nenhuma alternativa útil.

### Dependências e paralelismo

Nenhuma dependência pendente: a única relação era com a branch Augusto, cujo destino foi decidido no #55 (poda condicionada ao #105).

### Plano e aceite propostos

Não ação documental: a seam existe na main auditada e o mantenedor declarou a pergunta da branch superada.

### Comunicação entre responsáveis

Para a consolidação: "#56 perdeu o objeto; `093c677` está na main".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — aplicar o commit de novo na branch Augusto não teria efeito útil. (b) Que caso o teste ainda não cobre? — o caminho AQE-inclusivo de produção, que o teste substitui por um injetado. (c) Como eu explicaria isso para outro pod? — "a correção que se queria levar para a branch já estava na main". (d) O teste com `full_analyzer` injetado cobre o caminho real?

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento definitivo; reabrir só se a seam sair da main.

<a id="item-430"></a>

## #58 — JAR: correct lifecycle + measured telemetry

Frente: historico. Encaminhamento: concluida_por_pr_com_closes.

### Identidade e estado

Issue #58, melhoria (`enhancement`, `phase:backlog`, `pod-2-engine`); autor `gustocezar` (COLLABORATOR); sem assignee. Criada em 2026-08-06; fechada em 2026-08-18T20:05:32Z, um segundo depois do merge da PR #66, que a cita com `Closes`; 0 comentários.

### Intenção e benefício

Corrigir o ciclo de vida do listener de stages (estado que não era limpo em execuções longas) e emitir o runtime de executor medido, em vez de estimado.

### Feito, faltante e não comprovado

Feito pela PR #66 ("jar: correct stage listener lifecycle, add measured executor runtime"), integrada em 2026-08-18. Conferi no merge `eaff2b300`: `ActiveStageRegistry.scala`, `StageLifecycleSpec.scala` e `DriverListenerSoakSpec.scala` existem; `ApexStageListener.scala` menciona `executor_run_time`. A PR toca 16 arquivos, com specs de limites de payload, ativação, registro de jobs e estatísticas de duração. Relatado no corpo: compilação e suíte completa nas quatro células. Não reexecutado aqui.

### Linhagem

Issue (2026-08-06) → PR #66 com `Closes #58` → merge (2026-08-18 20:05:31) → fechamento um segundo depois, consistente com a palavra-chave da PR. A PR #68 também cita a issue. Linhagem completa por texto; ver ficha PR#66. Timeline pública (API, observada em 2026-10-17T17:31:13Z; 9 eventos): fechada por `luanmorenommaciel` em 2026-08-18; referências cruzadas na timeline retornada: PR#66, PR#68, #36; eventos `referenced` com commit na timeline retornada: nenhum.

### Fontes e corte

Snapshot (item 58); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_58.txt` (arquivos em `eaff2b300`); dossiê da PR #66 (16 arquivos) e sua ficha neste pacote.

### Classe e limite da evidência

DIRETO: `Closes`, datas, arquivos no merge. RELATADO: execução da suíte nas quatro células. A review formal da PR #66 está na ficha da PR (API).

### Fluxo

Fluxo declarado na PR #66: eventos de stage/job alimentam registries; onJobEnd limpa estado associado, e o listener emite executor_run_time_ms medido. O extrato confirma arquivos e literal do runtime, sem reproduzir o comportamento.

### Consequências e risco

O artefato de teste de soak existe no merge. Isso não comprova duração efetivamente executada nem ausência de vazamento em produção; a revisão não executou specs ou runtime.

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) nenhuma alternativa necessária.

### Dependências e paralelismo

Nenhuma pendente. A coluna tipada correspondente veio pela #60/PR #68 e o consumo pela #61/PR #70.

### Plano e aceite propostos

Condição de não ação: entregue pela PR #66 com specs próprias.

### Comunicação entre responsáveis

Para a consolidação: "#58 fechada pela PR #66 (Closes), com specs de ciclo de vida".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — sem limpar o registro de stages, um driver longo acumularia estado. (b) Que caso o teste ainda não cobre? — driver com milhares de stages por horas. (c) Como eu explicaria isso para outro pod? — "o listener agora esquece o stage quando termina e mede o runtime de verdade". (d) O soak spec usa quantos stages?

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: já fechada; reabrir se o soak spec falhar ou o estado voltar a vazar.

