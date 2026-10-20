# Fichas documentais — lote 47

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-461"></a>

## PR#57 — Apex v0.1 — eight lanes, one frozen contract, and a system that refuses to guess

Frente: historico. Encaminhamento: integrada_release_v010_com_ci_verde.

### Identidade e estado

PR #57, feat/base-project-e2e → main; autor luanmorenommaciel (OWNER). Criada 2026-07-29T19:14:08Z e integrada 19:14:38Z no merge 50d596e. Inventário: 54 commits e 237 arquivos; tag v0.1.0 aponta ao merge. Entrada das PRs #44–#51 na main conforme recibo de ancestralidade.

### Intenção e benefício

Entregar a v0.1: sistema aberto e auto-hospedável, telemetria capturada na JVM, aterrissada no ClickHouse do usuário, analisada por detectores determinísticos e servida ao editor por MCP. Tese do corpo: "errar menos", com a verify recusando a própria demo (finding `189e3495`).

### Feito, faltante e não comprovado

Feito e integrado. Runs com o head `ada98d1` (`fontes/batch-claude-historico-corrigido-sources/claude/fontes/reconferencia/pontos08-09-tempos-de-runs.json`): `CI push` 30483227835, na branch `feat/base-project-e2e`, criado 19:10:24Z e concluído (updated_at) com `success` às 19:13:22Z, antes do merge (19:14:38Z); `CI pull_request` 30483502373, criado 19:14:12Z e concluído com `success` às 19:17:26Z, depois do merge. Na main, o run de push 30483538928 tem head igual ao commit de merge `50d596e` (associação por head_sha) e concluiu com `success` às 19:18:10Z. Não há prova de CI de PR verde antes do merge. Na história da PR há um commit "ci: make CI actually pass — it had failed six for six since I added it" (`4d041b5`). Relatado no corpo: run real `app-20260729182801-0045` sem finding de skew por stage indevido; recusa de quatro checagens no finding `189e3495`. Não reexecutado aqui.

### Linhagem

Branch de convergência com as PRs #44–#51 (2026-07-24): 54 commits retornados, sendo 36 de Luan Moreno, 10 de Augusto Cezar e 8 commits de merge com autor gustocezar → PR #57 → tag `v0.1.0` → CHANGELOG [0.1.0] (conferido para o #15) → fechamento em lote de issues de maio em 2026-09-17, que cita a v0.1.0.

### Fontes e corte

Snapshot (PR 57); dossiê (237 arquivos, 54 commits); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/PR_57.txt` (tag, contagem de commits, arquivos-chave); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`; runs na listagem pública coletada.

### Classe e limite da evidência

DIRETO: merge, tag, arquivos e tempos dos runs: `success` no push da branch antes do merge; o run de PR terminou depois do merge; `success` no push da main ligado ao commit de merge por head_sha. RELATADO: as provas de recusa e o run real. Review formal: a autoria é do OWNER, que integrou a própria PR. Review formal (API, observada em 2026-10-17T17:28:08Z): 0 registradas; isso não prova ausência de leitura humana. Comentários inline de review: 0. Runs do Actions com o head `ada98d1` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` push success, run 30483227835, tentativa 1, created_at 2026-07-29 19:10:24Z, run_started_at 2026-07-29 19:10:24Z, updated_at 2026-07-29 19:13:22Z (antes do merge pelo updated_at); `CI` pull_request success, run 30483502373, tentativa 1, created_at 2026-07-29 19:14:12Z, run_started_at 2026-07-29 19:14:12Z, updated_at 2026-07-29 19:17:26Z (depois do merge pelo updated_at).

### Fluxo

Fluxo do produto v0.1: plugin (jar) → OTLP → collector → ClickHouse (infra) → engine (Tier 1 + gate) → serve (MCP) → editor; verify recusa correções que não se sustentam.

### Consequências e risco

Alto valor histórico e de referência: o head integrado tinha `success` concluído antes do merge (run de push da branch), e o commit de merge teve `success` na main; o run de PR, não, porque terminou depois do merge. Contrasta com a integração de 2026-10-06 (nenhuma das 27 PRs com `success` no head final no universo retornado, NOV-02).

### Alternativas e recomendação

(a) Manter como registro da release (recomendado); (b) usar a v0.1.0 como baseline de comparação na prova pós-integração atual.

### Dependências e paralelismo

Nenhuma pendente. Releases futuras dependem de DEC-N2 (política de versão).

### Plano e aceite propostos

Condição explícita de não ação: release histórica. Sugestão de uso: citar este caso (head verde antes do merge, commit de merge verde depois, run de PR ainda em curso no instante do merge) como referência e como limite para a política de proteção (DEC-02).

### Comunicação entre responsáveis

Para a consolidação: "PR #57 é a v0.1.0, integrada com o head verde no CI antes do merge e o commit de merge verde depois; serve de contraste para a integração de outubro".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — integrar 237 arquivos sem CI verde observado no head, como nas PRs de outubro, tiraria a prova hospedada. (b) Que caso o teste ainda não cobre? — o run real citado não foi reproduzido. (c) Como eu explicaria isso para outro pod? — "a v0.1 entrou com o head verde no CI e uma demo que se recusa a mentir". (d) Por que o CI falhou seis vezes antes desta PR?

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: histórico; serve de baseline para M0 e M4.

<a id="item-462"></a>

## PR#66 — jar: correct stage listener lifecycle, add measured executor runtime

Frente: historico. Encaminhamento: integrada_com_review_aprovada_e_ci_verde.

### Identidade e estado

PR #66, `feature/jar-lifecycle-measured-runtime` → `main`; autor `gustocezar` (COLLABORATOR); rótulo `pod-2-engine`; criada em 2026-08-06 e integrada em 2026-08-18T20:05:31Z (merge `eaff2b3`, que é ancestral da main); 1 commit; 16 arquivos (8 de código Scala e 8 specs). Ligada aos registros L02 e L12. Fecha o #58 por `Closes`.

### Intenção e benefício

Limpar o estado do listener no fim do job (`onJobEnd`), evitando retenção em drivers longos e fluxos não SQL, e emitir `executor_run_time_ms` medido, para que o watcher de memória deixe de usar o proxy `task_count * p50`.

### Feito, faltante e não comprovado

Feito: `JobStageRegistry`/`ActiveStageRegistry` para a limpeza; `ApexStageEvent`, `StageDurationStats`, `StageTaskSamples` e `ApexPayloadLimits` para os novos campos; specs de ciclo de vida, soak, ativação, limites e semântica de falha. Conferi no merge: `ActiveStageRegistry.scala`, `StageLifecycleSpec.scala` e `DriverListenerSoakSpec.scala` existem (`fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_58.txt`). Relatado: 29 testes em 11 suítes nas quatro células e `StageLifecycleSpec` com estado zerado após 12 shuffles reutilizados. Fora do escopo por desenho: `ApexAqeListener` (#65).

### Linhagem

Issue #58 → PR66 aberta 06/08 → brief do autor 16/08 → integração em 18/08. Ordem real dos merges: #68 às 20:03:21, #70 às 20:04:50, #66 às 20:05:31. A review #66 de 20:05:29 já cita colunas na main. A relação funcional produtor→coluna→consumidor não é a ordem cronológica dos merges.

### Fontes e corte

Snapshot (PR 66) com o corpo original e o brief; dossiê (16 arquivos); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/pr66-reviews.json`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_58.txt`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos, merge, review aprovada com texto ("25 attribute keys unchanged; 13 new ones added … `onJobEnd` cleanup stops the driver leaking stage maps"). RELATADO: execução da suíte nas quatro células. CI: run de PR verde no head (ver abaixo). Review formal (API, observada em 2026-10-17T17:28:09Z): 1 — `luanmorenommaciel` APPROVED em 2026-08-18. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `bfd1d2e` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 31107729374, tentativa 1, created_at 2026-08-06 13:49:06Z, run_started_at 2026-08-06 13:49:06Z, updated_at 2026-08-06 13:52:56Z (antes do merge pelo updated_at).

### Fluxo

Fluxo do listener: `onStageSubmitted` registra stage ativo → `onStageCompleted` agrega métricas e amostras → `onJobEnd` limpa os mapas `stageToJob`/`stageToExec` → sink OTLP com 38 chaves (25 antigas + 13 novas).

### Consequências e risco

Médio-alto valor: corrige vazamento de estado e passa o runtime para "medido". Limite: o soak spec é curto comparado a um driver de produção de horas.

### Alternativas e recomendação

(a) Manter como histórico integrado (recomendado); (b) se surgir driver de longa duração em produção, medir memória do listener por horas, sem alterar código.

### Dependências e paralelismo

Nenhuma pendente. A coluna tipada e o consumo seguiram nas PRs #68 e #70, já integradas.

### Plano e aceite propostos

Condição explícita de não ação: entregue com review aprovada, CI verde de PR e specs próprias. Nada a acrescentar sem um caso de longa duração.

### Comunicação entre responsáveis

Para a consolidação: "PR #66 é exemplo do fluxo saudável de agosto: CI de PR verde, brief do autor e aprovação com justificativa".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — sem `onJobEnd`, um driver de streaming acumularia stages indefinidamente. (b) Que caso o teste ainda não cobre? — driver com horas de execução e milhares de jobs. (c) Como eu explicaria isso para outro pod? — "o listener esquece o que terminou e mede o runtime de verdade". (d) O conjunto de 13 chaves novas está todo no contrato v0.5?

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: histórico; reabrir só com evidência de retenção de estado em driver longo.

<a id="item-463"></a>

## PR#67 — infra: switch Collector to synchronous inserts, fix retry duplication

Frente: historico. Encaminhamento: integrada_com_review_aprovada_e_ci_verde_residuo_raia_collect.

### Identidade e estado

PR #67, `feature/collector-synchronous-dedup` → `main`; autor `gustocezar`; `pod-2-engine`; criada em 2026-08-06 e integrada em 2026-08-18T20:02:38Z (merge `b11689b`); 1 commit; 2 arquivos. Fecha o #63 por `Closes`.

### Intenção e benefício

Eliminar a duplicação de linhas em `otel_traces` quando o collector reenvia um lote (`retry_on_failure`), que inflava todo agregado que soma (rollup `spark_jobs_1m`, consulta de skew `sql/005`, `run_outcomes`, memória).

### Feito, faltante e não comprovado

Feito: `infra/otel-collector-config.yaml` passa a `async_insert=0` com `deduplicate_blocks_in_dependent_materialized_views=1`, e `infra/sql/033_dedup_window_additive.sql` aplica `non_replicated_deduplication_window = 100` em quatro tabelas (conferido, `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_63.txt`). Relatado: retry de 1 linha e de lote de 5, 10 clientes concorrentes, collector real 0.156.0 recebendo o mesmo span duas vezes (uma linha só); síncrono mais rápido que assíncrono em escrita sequencial (2.912 × 6.432 ms), com o próprio autor anotando que não mediu o perfil `num_consumers: 10`. Resíduo estático conferido no #63: o DDL da raia collect isolada (`collect/ddl/10_otel_traces.sql`) não tem a janela.

### Linhagem

#63 → PR #67 (2026-08-06) → brief REVIEW (2026-08-16) → aprovação (2026-08-18: "Sync inserts + additive dedup window is the correct refusal of ‘looks faster, counts twice’") → merge.

### Fontes e corte

Snapshot (PR 67); dossiê; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/pr67-reviews.json`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_63.txt`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: configuração, migração, review aprovada. RELATADO: quatro cenários de teste e medições de tempo. INFERÊNCIA: o ganho de tempo é de um perfil de escrita; não generaliza para a concorrência real do collector. Review formal (API, observada em 2026-10-17T17:28:10Z): 1 — `luanmorenommaciel` APPROVED em 2026-08-18. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `98400b3` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 31107785368, tentativa 1, created_at 2026-08-06 13:49:49Z, run_started_at 2026-08-06 13:49:49Z, updated_at 2026-08-06 13:53:14Z (antes do merge pelo updated_at).

### Fluxo

Fluxo configurado: Collector → insert síncrono com deduplicate_blocks_in_dependent_materialized_views=1 → otel_traces e alvos com janela de 100 blocos. A migração documenta deduplicação por hash de bloco, não pelo conteúdo de cada linha; reenviar o mesmo span em blocos diferentes ou fora da janela não recebe garantia nesta revisão.

### Consequências e risco

Alto valor: corrige inflação silenciosa de agregados. Limites: desempenho sob `num_consumers: 10` não medido; raia collect isolada sem a janela em `otel_traces`.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) acrescentar a janela ao DDL da raia collect (ver #63); (c) medir desempenho com a concorrência real, se a latência de ingestão virar problema.

### Dependências e paralelismo

As opções (b) e (c) são independentes entre si e da fila M1; (c) exige ambiente autorizado.

### Plano e aceite propostos

Passo mínimo opcional: o mesmo do #63 (teste estático comparando os `SETTINGS` dos dois DDLs de `otel_traces`).

### Comunicação entre responsáveis

Para a consolidação: "PR #67 introduziu configuração síncrona e janela para deduplicar blocos reenviados; os testes de retry são relatados e o DDL da raia collect isolada não inclui a janela em otel_traces no recorte auditado".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — a combinação async_insert=1 com deduplicação em MV é documentada como rejeitada no ClickHouse 24.8 fixado; retirar os controles expõe agregados somatórios a repetição de blocos. Que caso o teste ainda não cobre? — desempenho com num_consumers=10 e semântica de reenvios em blocos diferentes ou além da janela não foram certificados nesta revisão. Como eu explicaria isso para outro pod? — a configuração tenta impedir que o mesmo bloco conte duas vezes dentro da janela; o relato de ensaio não promete deduplicação por span.

### Próxima ação e encerramento

Owner a confirmar: Pod 2, para o resíduo da raia collect. Encerramento: a PR segue integrada; o resíduo vai junto do #63.

<a id="item-464"></a>

## PR#68 — infra: typed columns for the telemetry fields the JAR now emits

Frente: historico. Encaminhamento: integrada_com_review_aprovada_e_ci_verde.

### Identidade e estado

PR #68, `feature/typed-executor-runtime-column` → `main`; autor `gustocezar`; `pod-2-engine`; criada em 2026-08-06 e integrada em 2026-08-18T20:03:21Z (merge `2a6a896`); 1 commit (`78236de`); 6 migrações. Fecha o #60 por `Closes`. O #95 cita `78236de` como o commit a partir do qual volumes antigos ficam atrasados.

### Intenção e benefício

Tipar como colunas os campos que o JAR passou a emitir (duração máxima, amostras, tasks bem-sucedidas, tentativas por tipo, `executor_run_time_ms`), por desempenho de consulta e schema explícito. O corpo diz que não era pré-requisito funcional.

### Feito, faltante e não comprovado

Feito: `infra/sql/034`–`039_*_additive.sql`, com `ADD COLUMN IF NOT EXISTS ... DEFAULT` e `ALTER TABLE ... MODIFY QUERY` em `mv_spark_events`; `039` cria `executor_run_time_ms Int64 DEFAULT 0` (conferido, `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_60.txt`). Numeração 034–039 escolhida para não colidir com a PR #67. Relatado: aplicado em volume novo e em volume com dados, em ClickHouse 24.8 e 26.1, duas vezes (idempotente). Os seis arquivos acrescentam 15 colunas. O "ponto aberto" do corpo sobre janela da MV foi posteriormente retratado no #71: o autor atribui os sintomas dos ensaios à omissão de ts e ao TTL; resultados em versões e idempotência permanecem relatos.

### Linhagem

#60 → PR #68 → aprovação → merge → PR #70 consome a coluna. Posteriormente, #95 registra volumes antigos sem as migrações e PR #131 acrescenta preflight; #179 registra texto obsoleto do Verify e propõe estudar medição/fallback. Esses vínculos não atribuem à migração um defeito funcional no predictor.

### Fontes e corte

Snapshot (PR 68); dossiê; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/pr68-reviews.json`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_60.txt`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: DDLs, review aprovada. RELATADO: aplicação em duas versões e idempotência. RELATADO POSTERIOR: #71 retrata a interpretação de corrida e descreve omissão de ts/TTL nos ensaios; isso não demonstra ausência de todo defeito possível da migração. Review formal (API, observada em 2026-10-17T17:28:11Z): 1 — `luanmorenommaciel` APPROVED em 2026-08-18. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `78236de` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 31107846183, tentativa 1, created_at 2026-08-06 13:50:33Z, run_started_at 2026-08-06 13:50:33Z, updated_at 2026-08-06 13:54:07Z (antes do merge pelo updated_at).

### Fluxo

Fluxo de schema: OTLP attributes → `mv_spark_events` (consulta modificada) → colunas tipadas com default 0 em linhas antigas → leitores com fallback (PR #70).

### Consequências e risco

Migrações aditivas precisam ser aplicadas em volumes antigos; #95 relata falha por schema atrasado e recebe preflight em PR #131. #179 identifica texto interno obsoleto do Verify e exige estudo antes de escolher política measured/estimated/unavailable; não é prova de regressão causada por esta PR.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) nenhuma ação nesta PR; os efeitos têm destino (#95 fechado, #179 aberto).

### Dependências e paralelismo

Efeitos posteriores dependem de #179 (DEC-N3). Não há dependência técnica pendente desta PR.

### Plano e aceite propostos

Condição explícita de não ação: integrada, aditiva e idempotente segundo o relato; resíduos com destino próprio.

### Comunicação entre responsáveis

Para a consolidação: "PR #68 acrescentou 15 colunas em seis migrações; #95 tratou diagnóstico de schema atrasado e #179 estuda uso de runtime e texto obsoleto no Verify".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — renomear ou reaproveitar campos poderia quebrar leitores existentes; os arquivos auditados acrescentam colunas com defaults. Que caso o teste ainda não cobre? — cluster replicado não foi exercitado segundo o autor, e esta revisão não executou migrações. Como eu explicaria isso para outro pod? — quinze campos ganharam colunas próprias; volumes antigos precisam receber as migrações antes de leitores que as referenciem.

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: histórico; o resíduo textual segue no #179.

<a id="item-465"></a>

## PR#69 — scripts: refuse to bootstrap over leftover APEX Docker resources

Frente: historico. Encaminhamento: integrada_com_review_aprovada_guarda_nao_ligada.

### Identidade e estado

PR #69, `feature/clean-docker-env-guardrail` → `main`; autor `gustocezar`; `pod-2-engine`; criada em 2026-08-06 e integrada em 2026-08-18T20:02:46Z (merge `046e2cb`); 1 commit; 1 arquivo (`scripts/assert_clean_docker_env.ps1`, +86). Fecha o #64 por `Closes`. Sem run de CI no head na listagem pública; causa da ausência não determinada.

### Intenção e benefício

Detectar recursos Docker remanescentes do APEX (infra, dev, collect) e recusar, sem remover nada, antes de um setup, porque um `docker compose down -v` apagou um volume preexistente durante os testes.

### Feito, faltante e não comprovado

Feito como script avulso. O corpo propõe que make bootstrap ou outro setup o execute antes; o comentário de 16/08 e a review descrevem proteção de bootstrap. A busca em toda a árvore c3c3ea3 só encontra o nome dentro do próprio script; Start-Package não o chama. Há outra guarda no pilot-clean. scripts/apex.sh delega ao PowerShell e não acrescenta uma implementação autônoma dessa guarda. O autor relata recusa ao vivo sem mutação; não reproduzida nesta revisão.

### Linhagem

Incidente local → #64 → PR #69 → aprovação → merge, junto do pacote operacional (PR #76) no mesmo dia → nenhuma ligação ao bootstrap → o problema de ownership segue no #175.

### Fontes e corte

Snapshot (PR 69); dossiê; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/pr69-reviews.json`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_64.txt`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/PR_69.txt` (scripts na main e `apex.sh`); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: script, ausência de chamadas, review com o pedido do gêmeo shell. RELATADO: recusa ao vivo com contagem de recursos igual antes e depois. Review formal (API, observada em 2026-10-17T17:28:12Z): 1 — `luanmorenommaciel` APPROVED em 2026-08-18. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `f59c8d9`: nenhum no universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada. Isso não prova que nenhum CI tenha rodado fora desse universo.

### Fluxo

Fluxo estático do script: docker ps/network ls/volume ls → containers por padrões/nome e redes/volumes por listas de nomes exatos → resíduos encontrados geram APEX_CLEAN_DOCKER=refused e exit 1; sem resíduos, passed. Erros de inventário lançam exceção. Não há comandos de remoção no script lido.

### Consequências e risco

Há divergência entre a descrição de bootstrap protegido no comentário/review e a ausência de chamada observada em c3c3ea3. O texto da review não prova o que o revisor sabia ou supunha. A auditoria comprova a lacuna estática, sem reproduzir incidente via make bootstrap.

### Alternativas e recomendação

(a) Registrar a lacuna e levá-la ao #175 (recomendado); (b) chamar a guarda em `Start-Package` — exige regra para "minha própria stack anterior", decisão do #175; (c) remover o script — perderia a ferramenta.

### Dependências e paralelismo

A opção (b) depende de DEC-10/#175 (identidade e ownership da stack).

### Plano e aceite propostos

Passo mínimo documental: anotar no #175 as duas guardas existentes e a ausência de guarda no bootstrap. Controle negativo, se ligada: subir de novo a própria stack não pode ser recusado.

### Comunicação entre responsáveis

Para a consolidação: "PR #69 integrou uma guarda avulsa de recursos Docker; em c3c3ea3, o nome só é referenciado pelo próprio arquivo e o bootstrap não a chama".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — ligar uma recusa geral sem regra de ownership poderia impedir reuso legítimo da própria stack. Que caso o teste ainda não cobre? — bootstrap com recursos de outra pessoa e retomada da stack própria não foram exercitados nesta auditoria. Como eu explicaria isso para outro pod? — existe uma ferramenta de inventário e recusa; sua proteção automática do bootstrap não está ligada no SHA examinado.

### Próxima ação e encerramento

Owner a confirmar: dono do pacote, no #175. Entrada: este registro. Saída: decisão de ligar ou documentar o uso manual. Encerramento: a PR segue integrada.

<a id="item-466"></a>

## PR#70 — engine: read the typed executor runtime column, Map as fallback

Frente: historico. Encaminhamento: integrada_com_review_aprovada.

### Identidade e estado

PR #70, `feature/engine-typed-runtime-column` → `main` (base `2a6a896`, o merge da PR #68); autor `gustocezar`; `pod-2-engine`; criada em 2026-08-06 e integrada em 2026-08-18T20:04:50Z (merge `2195d40`); 1 commit; 4 arquivos. Fecha o #61 por `Closes`. Sem run de CI no head na listagem pública.

### Intenção e benefício

Fazer as duas leituras de `executor_run_time_ms` no engine preferirem a coluna tipada, mantendo o mapa de atributos como fallback, para que linhas da janela de transição não caiam de "medido" para 0.

### Feito, faltante e não comprovado

Feito: `clickhouse.py` e `watchers/memory.py` usam `argMax(if(col > 0, col, toInt64OrZero(attributes[...])), ts)` (conferido, `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_61.txt`); teste de integração novo (+63). O corpo explica o efeito: sem fallback, o `runtime_basis` do watcher de memória cairia de `measured` (0,85) para proxy (0,45), abaixo do gate de 0,6, reabrindo escalonamento. Relatado: teste que falha com a mudança revertida. No comentário de 2026-08-06, uma linha real com a coluna tipada `executor_run_time_ms` = 30000 e o Map `attributes` sem essa chave: a consulta desta PR leu 30000, e a da main de então (só Map) leu 0, sem erro. O corpo descreve outro caso: coluna 0 e Map `'10000'`, em que a leitura direta da coluna dá 0 e o fallback dá 10000. (O pacote de 17/10 misturou os dois casos.)

### Linhagem

#61 → PR #68 (coluna) → PR #70 (base no merge da #68) → aprovação ("transition rows stay `measured` … The LLM-lane dormancy is called out, not hidden") → merge.

### Fontes e corte

Snapshot (PR 70); dossiê; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/pr70-reviews.json`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_61.txt`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: SQL e teste adicionado; review aprovada. RELATADO: a prova por reversão e a consulta cruzada com outro fork. Sem CI no head na listagem; não verificado se o workflow rodou. Review formal (API, observada em 2026-10-17T17:28:13Z): 1 — `luanmorenommaciel` APPROVED em 2026-08-18. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `0a7772b`: nenhum no universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada. Isso não prova que nenhum CI tenha rodado fora desse universo. Complemento documental de 19/10, RELATADO no corpo: 94 testes offline e 8 de integração com ClickHouse 24.8 e migração 039; execução composta de #66/#67/#68/#70/#64, separada do diff, com migrações 034–039 idempotentes em 24.8/26.1. Não reproduzido nesta auditoria.

### Fluxo

Fluxo estático: por linha, coluna executor_run_time_ms > 0 tem preferência; caso contrário, usa-se toInt64OrZero do atributo; argMax por ts seleciona o valor. Se o resultado agregado for positivo, _runtime_basis retorna measured; sem ele, tenta task_count*p50 e pode retornar estimated ou unavailable. Para a regra GC, measured usa confiança 0,62 (warning) ou 0,85 (critical), enquanto estimated usa 0,45. O gate exige confiança <0,60 e severidade ao menos critical; não se deduz um finding ou escalonamento universal só pelo fallback.

### Consequências e risco

Médio: protege a calibração do gate (ver #6). A review registra a "dormência da raia LLM", coerente com o #38.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) estudar população, unidade e seleção de runtime no Verify dentro de #179, que pode concluir por medição, estimativa ou combinação de limites. Copiar a regra do Engine não está decidido.

### Dependências e paralelismo

A consulta desta PR referencia a coluna tipada e exige schema atualizado com #68, mesmo quando o valor usa o Map; não é fallback para coluna inexistente. #95 registra falha Code 47 em schema atrasado. A possível política do Verify depende do estudo #179/DEC-N3, sem implementação autorizada nesta ficha.

### Plano e aceite propostos

Não ação nesta PR integrada. #179 deve primeiro decidir a política de runtime do Verify; presença de executor runtime não prova equivalência com o W exigido pelo predictor.

### Comunicação entre responsáveis

Para a consolidação: "PR #70 preservou runtime positivo vindo da coluna ou do Map em linhas de transição; valores ausentes ainda podem produzir proxy, e schema atrasado continua exigindo migração".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — ler só a coluna perderia valores históricos presentes apenas no Map; ler só o Map perderia linhas com valor somente na coluna. Que caso o teste ainda não cobre? — a fixture adicionada usa ausência em ambos, coluna zero/Map positivo e ambos positivos iguais; não discrimina coluna e Map positivos divergentes nem coluna positiva com chave ausente. Como eu explicaria isso para outro pod? — o fallback preserva o valor de transição, exige a coluna existente e só chama measured quando o runtime agregado é positivo.

### Próxima ação e encerramento

Nenhuma ação obrigatória. Owner da extensão: quem tratar o #179. Encerramento: histórico.

<a id="item-467"></a>

## PR#74 — dev: real-pathology probe tooling and design-doc rationale for merged telemetry fields

Frente: historico. Encaminhamento: integrada_com_review_aprovada_e_ci_verde.

### Identidade e estado

PR #74, `candidate/dev-real-pathology-probes` → `main`; autor `gustocezar`; `pod-2-engine`; criada em 2026-08-10 e integrada em 2026-08-18T20:05:58Z (merge `e289e18`); 1 commit; 17 arquivos. Fecha o #73 por `Closes`.

### Intenção e benefício

Trazer ao `dev/` probes que forçam condições reais do Spark (FetchFailed, retry/especulação, tail outlier, soak do listener), scripts de evidência e credencial, e documentos que explicam campos já integrados.

### Feito, faltante e não comprovado

Feito: quatro probes, sete scripts, scaffold de segredos e alterações Compose, além de três documentos de arquitetura, conforme diff e arquivos lidos. O corpo relata execução dos quatro probes, wrapper e generate_data após corrigir segredos, mas explicita que soak_driver_listener.sh e os dois orquestradores PowerShell não foram executados independentemente nesta passada. O comentário posterior relata seis raias, memória e replay; não substitui recibos de cada orquestrador nem comprova runtime nesta revisão. ADR001/002 constam do índice canônico c3c3ea3.

### Linhagem

#73 → execução parcial e bloqueio (2026-08-10) → PR #74 com segredos no Compose → aprovação → merge. O `r9d_overhead_ab.py` é a base local do número de overhead discutido no #113. A ligação posterior com a PR #81 consta na camada editorial acrescentada em 10/10; não é menção do texto original do autor.

### Fontes e corte

Snapshot (PR 74); dossiê (17 arquivos); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/pr74-reviews.json`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_73.txt`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos, segredos, review. RELATADO: execuções dos probes, wrapper, generate_data e dois scripts de evidência; comentário posterior relata seis raias/memória/replay. NÃO VERIFICADO: execução independente dos três orquestradores após a correção e qualquer runtime nesta auditoria. Review formal (API, observada em 2026-10-17T17:28:13Z): 1 — `luanmorenommaciel` APPROVED em 2026-08-18. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `cf26b68` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 31387170347, tentativa 1, created_at 2026-08-10 12:15:23Z, run_started_at 2026-08-10 12:15:23Z, updated_at 2026-08-10 12:18:41Z (antes do merge pelo updated_at).

### Fluxo

Fluxo dos probes: job com patologia induzida → Spark real → event log e telemetria → scripts de evidência (relatório de eventos, checagem de vazamento de credencial).

### Consequências e risco

Médio valor de evidência. Limite: as ADRs canônicas 001/002 nasceram como "documentos de racional" desta PR; o índice não registra essa origem.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) registrar no índice de ADRs que 001/002 vieram da PR #74.

### Dependências e paralelismo

A opção (b) é documental e independente. O uso dos probes como prova de overhead depende do #113.

### Plano e aceite propostos

Nenhuma ação nesta PR integrada. Se #113 for retomada, o próximo passo é ratificar protocolo, identidade e critérios de evidência; a issue explicita que não autoriza runtime. Executar orquestradores exige escopo e autorização próprios posteriores.

### Comunicação entre responsáveis

Para a consolidação: "PR #74 trouxe os probes de patologia real e os ADR-001/002 canônicos".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — mocks podem não representar os caminhos de scheduler e shuffle que os probes pretendem induzir. Que caso o teste ainda não cobre? — a execução independente dos três orquestradores após a correção não foi demonstrada nesta auditoria. Como eu explicaria isso para outro pod? — a PR entregou ferramentas para provocar patologias reais e registrar evidência; os ensaios são relatos históricos, e #113 ainda governa o protocolo antes de novos experimentos.

### Próxima ação e encerramento

Nenhuma ação obrigatória. Owner a confirmar: quem retomar o #113. Encerramento: histórico.

<a id="item-468"></a>

## PR#75 — infra: guard apply-ddl against MV/target bootstrap ordering

Frente: historico. Encaminhamento: integrada_com_review_aprovada_e_ci_verde.

### Identidade e estado

PR #75, `candidate/fix-mv-bootstrap-ordering` → `main`; autor `gustocezar`; `pod-2-engine`; criada em 2026-08-11 e integrada em 2026-08-18T20:02:42Z (merge `f020f9a`); 1 commit; 1 arquivo (`infra/scripts/apply_ddl.sh`, +19). Fecha o #72 por `Closes`.

### Intenção e benefício

Fazer o `apply_ddl.sh` falhar no arquivo que criou uma MV cuja tabela-alvo não existe, em vez de deixar a falha aparecer depois como rejeição total de inserts.

### Feito, faltante e não comprovado

Feito: após aplicar cada sql/*.sql, o script extrai alguns alvos MATERIALIZED VIEW ... TO por grep na mesma linha, consulta EXISTS TABLE e falha nomeando alvo ausente. A expressão original não cobre alvo em linha posterior; #147 corrige a extração multiline. Três containers e reproduções são relatos do autor.

### Linhagem

#71 (investigação) → #72 (risco de ordem) → PR #75 → aprovação → merge.

### Fontes e corte

Snapshot (PR 75); dossiê; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/pr75-reviews.json`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_72.txt`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: guarda no script; review; CI de PR verde no head. RELATADO: reproduções em contêineres descartáveis. Review formal (API, observada em 2026-10-17T17:28:14Z): 1 — `luanmorenommaciel` APPROVED em 2026-08-18. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `b643a9e` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 31451248372, tentativa 1, created_at 2026-08-11 02:04:25Z, run_started_at 2026-08-11 02:04:25Z, updated_at 2026-08-11 02:07:42Z (antes do merge pelo updated_at).

### Fluxo

Fluxo original: aplicar arquivo → extrair alvos TO reconhecidos pela expressão por linha → EXISTS TABLE por alvo → falhar com diagnóstico ou continuar. A verificação ocorre depois da criação da MV e não é um parser SQL completo.

### Consequências e risco

A guarda acrescenta diagnóstico para os alvos que reconhece quando o DDL passa por apply_ddl.sh. Não cobre manual/init fora dele; o extrator original também tem o limite multiline corrigido em #147. Pane e rejeição de inserts foram relatadas, sem reprodução nesta revisão.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) levar a mesma checagem ao `verify-ddl` no contexto do #170.

### Dependências e paralelismo

A opção (b) depende da decisão do #170 (DEC-25) sobre o alcance do verificador.

### Plano e aceite propostos

Condição explícita de não ação nesta PR. Sugestão ao #170: incluir "alvos de MV existem" entre as checagens.

### Comunicação entre responsáveis

Para a consolidação: "PR #75 acrescentou checagem pós-aplicação de existência dos alvos de MV reconhecidos; o limite multiline foi corrigido posteriormente em #147".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — omitir a checagem pode deixar um alvo ausente ser descoberto só na ingestão; o ensaio histórico relata esse caso. Que caso o teste ainda não cobre? — o extrator original não reconhece TO em linha posterior, limite tratado em #147, e esta auditoria não executou DDL. Como eu explicaria isso para outro pod? — o script aplica e depois confere os alvos que consegue extrair; a primeira versão não validava toda forma de SQL.

### Próxima ação e encerramento

Nenhuma ação obrigatória. Owner da extensão: owner de Infra no #170. Encerramento: histórico.

<a id="item-469"></a>

## PR#76 — scripts: local operational package (bootstrap/doctor/smoke/e2e/status/down)

Frente: historico. Encaminhamento: integrada_com_review_aprovada_e_ci_verde_nota_de_review_imprecisa.

### Identidade e estado

PR #76, `candidate/local-operational-package` → `main`; autor `gustocezar`; `pod-2-engine`; criada em 2026-08-13 e integrada em 2026-08-18T20:06:02Z (merge `884c274`); 2 commits; 4 arquivos (`Makefile` +52, `scripts/apex.ps1` +772, `scripts/apex.sh` +101, `dev/docker-compose.package.yml` +21). Fecha o #62 por `Closes`. Tem 1 review (`APPROVED`, 2026-08-18) e 2 comentários gerais do autor (2026-08-16 e 2026-08-19).

### Intenção e benefício

Oferecer uma superfície de um comando para o pacote local de seis raias: `bootstrap`, `doctor` (saúde real), `smoke`/`e2e`, `status`, `down` (preserva volumes) e `pilot-clean` (só roda em máquina limpa e nunca remove nada); Windows por `apex.ps1`, macOS por `apex.sh` que delega ao mesmo script.

### Feito, faltante e não comprovado

Pacote integrado e presente em c3c3ea3; #35 relata uso de make bootstrap. A review aprovada diz que o doctor usa "this repo's apply-ddl and Spark 4.1.2 pin" e registra que o revisor não pôde rodar o e2e do pacote por não ter PowerShell 7. Conferi no merge e na main: o doctor exige **Spark 4.0.1** (`apex.ps1:482-484`, `throw "Expected Spark 4.0.1"`; `.env.example`: `SPARK_VERSION=4.0.1`); 4.1.2 aparece só como overlay de compatibilidade (linha 124). A nota da review sobre o pin é imprecisa, e o próprio autor já a corrigiu no comentário de 2026-08-19: o pacote exige 4.0.1, e a string `# Spark 4.1.2 compatibility overlay` é código morto num parâmetro `-Overlay` que nada passa (o autor se ofereceu para removê-la). Conferi que a string continua na main (`scripts/apex.ps1:124` em `c3c3ea3`); o resíduo atual é um comentário enganoso em código morto, não um pin errado ativo. Relatado: 8 bootstraps reais até verde e `make smoke` com o gate de produto. O autor explicita que e2e, pilot-clean e install não foram exercitados. Defeitos posteriores: `Copy-Item -Force` em `dev/.env` (#174) e ownership de stack (#175), ambos abertos.

### Linhagem

#62 → PR #76 (2026-08-13) → brief (2026-08-16) → aprovação sem execução local do revisor (2026-08-18) → merge → agradecimento do autor com instruções para macOS (2026-08-19) → defeitos em #174/#175.

### Fontes e corte

Snapshot (PR 76) com três comentários; dossiê; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/pr76-reviews.json`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/PR_76.txt` (pin de Spark no merge e na main; delegação do `apex.sh`); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: código do doctor, pin 4.0.1, review com a nota de não execução, comentário do autor de 2026-08-19 que corrige a nota. RELATADO: bootstraps e smoke do autor. RELATO do revisor: não executou o e2e do pacote. Isso não exclui outras verificações não registradas. Review formal (API, observada em 2026-10-17T17:28:23Z): 1 — `luanmorenommaciel` APPROVED em 2026-08-18. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `f05a050` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 31652912975, tentativa 1, created_at 2026-08-13 00:00:17Z, run_started_at 2026-08-13 00:00:17Z, updated_at 2026-08-13 00:03:40Z (antes do merge pelo updated_at).

### Fluxo

Fluxo estático de bootstrap: Start-Package valida pré-requisitos/configuração → sobe ClickHouse → aplica DDL → inicia collect e dev → Invoke-Doctor. smoke é comando separado; Invoke-CleanPilot encadeia guarda de ambiente, bootstrap, doctor e produto. O código e o pin 4.0.1 não certificam execução nesta auditoria.

### Consequências e risco

Superfície operacional relevante e presente no SHA auditado; uso por todo usuário local não foi demonstrado. A nota de pin da review diverge do código e foi corrigida pelo autor, que também distingue comandos executados de não exercitados. #174/#175 registram resíduos próprios; runtime não reexecutado.

### Alternativas e recomendação

(a) Manter como histórico e registrar a nota imprecisa (recomendado); (b) nenhuma correção de código nesta PR; os defeitos têm destino (#174/#175).

### Dependências e paralelismo

Os defeitos dependem de DEC-10 e DEC-15 (publicação do CL-01). A prova Windows nativa depende de CL-03.

### Plano e aceite propostos

Condição explícita de não ação nesta PR. Para quem tratar #174/#175: partir de `Start-Package` (linha 506) e do `doctor` (482–503), que esta revisão conferiu.

### Comunicação entre responsáveis

Para a consolidação: "PR #76 é o pacote atual; a review declarou não ter executado o e2e e citou o pin 4.1.2, corrigido pelo autor em 2026-08-19; os defeitos estão em #174/#175".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — mudar apenas a expectativa do doctor para 4.1.2 divergiria da configuração 4.0.1 auditada. Que caso o teste ainda não cobre? — o autor não exercitou e2e, pilot-clean e install; macOS limpo e Windows nativo não foram verificados nesta revisão. Como eu explicaria isso para outro pod? — bootstrap sobe as raias e chama doctor; smoke é uma etapa própria, e o dispatcher macOS usa o mesmo PowerShell.

### Próxima ação e encerramento

Nenhuma ação nesta PR. Owner dos defeitos: dono do pacote (DEC-10). Encerramento: histórico; o trabalho atual segue em #174/#175.

<a id="item-470"></a>

## PR#77 — docs: fix Quick Start README (DDL order, .env step, sbt prereq)

Frente: historico. Encaminhamento: integrada_com_review_aprovada_e_ci_verde.

### Identidade e estado

PR #77, `fix/readme-quickstart-ddl-order` → `main`; autor `JaymeNeto` (COLLABORATOR; commits como "Jayme Leal"); criada em 2026-08-14 e integrada em 2026-08-18T20:02:06Z (merge `ba9231d`); 4 commits; 1 arquivo (`README.md`, +28/-3). É a única PR de `JaymeNeto` no recorte; das 78 PRs revisadas, 60 são de `gustocezar`, 9 de `sidymar`, 4 de `luanmorenommaciel`, 2 de `agmarcastro`, 2 de `antonylucas` e 1 desta pessoa (contagem do snapshot).

### Intenção e benefício

Corrigir o Quick Start do README: `apply-ddl` rodava antes de `docker compose up`; faltava o passo do `.env` (`HYPERDX_API_KEY`); `sbt` não constava como pré-requisito.

### Feito, faltante e não comprovado

Feito: os quatro commits corrigem a ordem, acrescentam o `.env`, incluem `sbt` e documentam o fluxo real dev → collect → infra. A review aprovada diz "Quick Start was lying about order and about what `dev` actually proves … a local pathology is not e2e until it is wired". Plano de teste marcado pelo autor: cada erro reproduzido antes da correção e o passo 1 reexecutado depois. CI verde no PR e no push (2026-08-18).

### Linhagem

Erros encontrados ao seguir o README → PR #77 (2026-08-14) → aprovação → merge. O README atual tem a seção "Quick start" (linha 61, conferida para o #34).

### Fontes e corte

Snapshot (PR 77); dossiê; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/api-reviews/pr77-reviews.json`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: diff, commits, review, runs verdes. RELATADO: reprodução dos erros pelo autor. Review formal (API, observada em 2026-10-17T17:28:24Z): 1 — `luanmorenommaciel` APPROVED em 2026-08-18. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `e2177c7` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` push success, run 32164660793, tentativa 1, created_at 2026-08-18 17:15:39Z, run_started_at 2026-08-18 17:15:39Z, updated_at 2026-08-18 17:18:47Z (antes do merge pelo updated_at); `CI` pull_request success, run 32164666165, tentativa 1, created_at 2026-08-18 17:15:43Z, run_started_at 2026-08-18 17:15:43Z, updated_at 2026-08-18 17:19:01Z (antes do merge pelo updated_at).

### Fluxo

Fluxo documentado no diff: preparar infra/.env e HYPERDX_API_KEY → docker compose up -d --wait → make apply-ddl → sbt assembly. O bloco posterior explica ligação dev→collect→infra e ressalva que dev isolado não comprova entrega de telemetria ao ClickHouse.

### Consequências e risco

Baixo risco e alto valor de onboarding: o README era a porta de entrada e estava errado. Mostra a utilidade de alguém de fora seguir o passo a passo.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) repetir o exercício de seguir o Quick Start atual do zero, como checagem documental periódica.

### Dependências e paralelismo

Não há dependência técnica pendente desta PR integrada. Ler instruções é checagem documental; executá-las do zero envolve ambiente, ferramentas e runtime e precisa de escopo próprio.

### Plano e aceite propostos

Condição explícita de não ação: integrada. Sugestão: tratar "seguir o README do zero" como controle periódico de documentação.

### Comunicação entre responsáveis

Para a consolidação: "PR #77 corrigiu o Quick Start a partir de erros reais de quem o seguiu".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — o comando antigo tentava aplicar DDL sem ClickHouse iniciado e omitia configuração e pré-requisito. Que caso o teste ainda não cobre? — esta revisão não seguiu o Quick Start atual numa máquina limpa; o autor relata só o passo corrigido e a reprodução dos erros. Como eu explicaria isso para outro pod? — o README prepara configuração antes da subida e aplica schema depois, além de explicar a ligação entre as raias.

### Próxima ação e encerramento

Nenhuma ação obrigatória. Owner a confirmar: mantenedor da documentação, para a checagem periódica. Encerramento: histórico.

