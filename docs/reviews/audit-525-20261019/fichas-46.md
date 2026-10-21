# Fichas documentais — lote 46

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-451"></a>

## PR#45 — docs(v1): definir arquitetura por raias e plano de PRs

Frente: historico. Encaminhamento: integrada_em_branch_de_convergencia_documento_historico.

### Identidade e estado

PR #45, `docs/v1-swimlanes-contracts` → `feat/base-project-e2e`; autor `gustocezar`; criada em 2026-07-23 e integrada em 2026-07-24T02:22:40Z (merge `f96c402`); 1 commit (`85de52d`); 3 arquivos. Chegou à main pela PR #57.

### Intenção e benefício

Definir a arquitetura V1 em seis raias (JAR, DEV, COLLECT, INFRA, ENGINE, SERVE), os contratos entre elas, segurança, gates e a ordem de entrega das PRs.

### Feito, faltante e não comprovado

Feito: `docs/architecture/APEX-V1-SWIMLANES.md` (+136) e `APEX-V1-PR-PLAN.md` (+114) existem na main. Na main de `1e0ba80` o SWIMLANES se declara "HISTORICAL — the 6-lane design as approved on 2026-07-23" (conferido para o #30). A entrega final teve 8 raias (memory e verify somadas). Validação: "revisão documental contra a base", sem review formal registrada (API).

### Linhagem

Reunião de 2026-06-30 (#34) → proposta de pods (#30) → PR #45 (2026-07-23) → PRs #44, #46–#51 com os nomes de branch do plano → PR #57 leva à main. Ordem: o plano (`85de52d`, autoria 09:00 -03:00) declara que nenhuma branch ou PR existia e reaproveita commits locais anteriores como fonte (não presentes no clone público); os commits das raias são de 09:40 -03:00 em diante; #44–#46 foram abertas no mesmo instante (14:11:05Z). As raias já existiam como trabalho local antes do plano, que as reorganizou em PRs (`fontes/batch-claude-historico-corrigido-sources/claude/fontes/reconferencia/git-reconferencia.txt`). É a fonte que o #30 e o #34 citam como decisão.

### Fontes e corte

Snapshot `pulls_all.json` (PR 45); dossiê; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_30.txt` (aviso HISTORICAL); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos e aviso de histórico. RELATADO: "aprovado em 2026-07-23" (no próprio documento). DECISÃO: registrada no documento, sem review formal na PR. Review formal (API, observada em 2026-10-17T17:28:00Z): 0 registradas; isso não prova ausência de leitura humana. Comentários inline de review: 0. Runs do Actions com o head `85de52d`: nenhum no universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada. Isso não prova que nenhum CI tenha rodado fora desse universo.

### Fluxo

Fluxo de planejamento: raias → contratos entre raias → gates → ordem das PRs → revisão por raia.

### Consequências e risco

Baixo. O documento é a melhor fonte para o desenho de julho; ler como atual levaria a esquecer memory e verify.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) nenhuma ação: o próprio documento já se marca histórico.

### Dependências e paralelismo

Nenhuma dependência: o documento foi substituído na prática pela entrega de 8 raias e pelos pods atuais; nada depende dele para avançar.

### Plano e aceite propostos

Condição explícita de não ação: documento histórico autodeclarado.

### Comunicação entre responsáveis

Para a consolidação: "PR #45 registrou o desenho de 6 raias; a entrega teve 8".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — revisar raias misturadas, que o plano evitava. (b) Que caso o teste ainda não cobre? — não encontrei teste ligado a este item nas fontes lidas; é documento. (c) Como eu explicaria isso para outro pod? — "é o mapa de julho; o de hoje tem mais duas raias". (d) Quem atualiza a ordem de PRs quando o plano muda?

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: histórico; o documento só seria revisto se o mantenedor quisesse um mapa raia × pod atual (ver ficha #30).

<a id="item-452"></a>

## PR#46 — feat(engine): adicionar diagnóstico determinístico

Frente: historico. Encaminhamento: integrada_em_branch_de_convergencia_codigo_reestruturado_depois.

### Identidade e estado

PR #46, `engine/deterministic-diagnostics` → `feat/base-project-e2e`; autor `gustocezar`; criada em 2026-07-23 e integrada em 2026-07-24T00:43:01Z (merge `244686d`); 1 commit; 12 arquivos. Chegou à main pela PR #57.

### Intenção e benefício

Criar o engine determinístico: schema do contrato v0.2, cinco watchers, `EvidenceValidator`, fronteira ClickHouse parametrizada e persistência de findings, antes de qualquer escalonamento para LLM.

### Feito, faltante e não comprovado

Feito no recorte da época. Hoje o arquivo único `engine/src/apex_engine/watchers.py` não existe; os watchers viraram o pacote `watchers/` (conferido no #17: `skew`, `shuffle`, `memory`, `cost`, `code`, `aqe`, `retry_pressure`). Continuam: `schema.py`, `clickhouse.py`, `pipeline.py`, `validation.py`, `tests/test_clickhouse_boundary.py`, `tests/test_contract_engine.py`, `engine/VALIDATION.md`. Relatado: "10 passed em 0,85 s".

### Linhagem

Plano V1 (PR #45) → PR #46 → PR #57 → evolução do engine (gate, crew, retry-safe, preflight). Nenhuma issue fechada por palavra-chave no corpo da PR; o #17 cita os watchers como entrega.

### Fontes e corte

Snapshot (PR 46); dossiê (12 arquivos e presença na main); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_17.txt`.

### Classe e limite da evidência

DIRETO: arquivos e reestruturação. RELATADO: testes. INFERÊNCIA: o princípio determinístico-primeiro desta PR continua (ver #6, #55). Review formal (API, observada em 2026-10-17T17:28:01Z): 0 registradas; isso não prova ausência de leitura humana. Comentários inline de review: 0. Runs do Actions com o head `f11f602`: nenhum no universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada. Isso não prova que nenhum CI tenha rodado fora desse universo.

### Fluxo

Fluxo: `job_id` → `clickhouse.py` (consulta parametrizada) → watchers → `EvidenceValidator` → findings persistidos.

### Consequências e risco

Baixo. A PR é a origem do Tier 1; o risco é só de leitura (o arquivo `watchers.py` citado sumiu).

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) anotar na consolidação que `watchers.py` virou o pacote `watchers/`, para quem seguir o corpo da PR. Não há alternativa de produto a decidir.

### Dependências e paralelismo

Nenhuma dependência: o Tier 1 evoluiu em PRs posteriores (#70, #99, #131), cada uma com ficha própria.

### Plano e aceite propostos

Condição explícita de não ação: integrada; o código atual evoluiu a partir dela.

### Comunicação entre responsáveis

Para a consolidação: "PR #46 criou o Tier 1 determinístico".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — começar pelo LLM tornaria a detecção não reproduzível. (b) Que caso o teste ainda não cobre? — consulta parametrizada contra ClickHouse real. (c) Como eu explicaria isso para outro pod? — "regras SQL encontram o problema; o LLM só entra depois". (d) O `EvidenceValidator` ainda valida todos os watchers novos?

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: histórico; reabrir só se o princípio determinístico-primeiro for abandonado.

<a id="item-453"></a>

## PR#47 — feat(dev): preparar ambiente Spark 4.1.2

Frente: historico. Encaminhamento: integrada_em_branch_de_convergencia.

### Identidade e estado

PR #47, `dev/spark-4.1.2-env` → `feat/base-project-e2e`; autor `gustocezar`; criada em 2026-07-23 e integrada em 2026-07-24T00:43:07Z (merge `f2d2173`); 1 commit; 22 arquivos. Chegou à main pela PR #57.

### Intenção e benefício

Adicionar a célula Spark 4.1.2 ao ambiente DEV, os jobs canônicos de patologia e o overlay OTLP, e remover o adaptador JSONL legado, para que o plugin Scala seja o caminho oficial de telemetria.

### Feito, faltante e não comprovado

Feito: adiciona `dev/.env.spark41.example`, `docker-compose.c3-otlp.yml`, `scripts/canonical_e2e_assert.py`, `e2e_canonical.sh`, `ensure_env.py` e `jobs/aqe_skew_split_probe.py`; remove `dev/jvm/StageListener.java`, `dev/common/listener.py`, `dev/scripts/e2e.sh` e `dev/tests/listener_probe.py` (todos ausentes na main, como esperado). O atalho `make env-spark41` combina baseline e overlay "sem sobrescrever um .env existente". Relatado: 7 testes e Compose 4.1.2 validados. Nota: a main de 2026-08-20 usava Spark 4.0.1 no doctor (relato do #35); a célula 4.1 ficou como opção.

### Linhagem

Plano V1 → PR #47 → PR #57 → pacote operacional (#62/PR #76). A célula de build 4.1 do plugin veio na PR #50.

### Fontes e corte

Snapshot (PR 47); dossiê (22 arquivos, inclusive remoções); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos adicionados e removidos. RELATADO: testes e Compose. INFERÊNCIA: a remoção do adaptador JSONL encerra o caminho antigo de captura. Review formal (API, observada em 2026-10-17T17:28:02Z): 0 registradas; isso não prova ausência de leitura humana. Comentários inline de review: 0. Runs do Actions com o head `2dee3a7`: nenhum no universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada. Isso não prova que nenhum CI tenha rodado fora desse universo.

### Fluxo

Fluxo DEV: `make env-spark41` → baseline + overlay OTLP → jobs canônicos → plugin Scala → OTLP → collector.

### Consequências e risco

Baixo. O cuidado de não sobrescrever `.env` neste atalho contrasta com o problema posterior do pacote (#174), que sobrescreve `dev/.env`; são caminhos diferentes.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) comparar o atalho `make env-spark41` com o pacote atual quando o #174 for tratado, porque um preserva `.env` e o outro não.

### Dependências e paralelismo

Nenhuma dependência própria; a comparação sugerida depende do tratamento do #174 (DEC-10/DEC-15).

### Plano e aceite propostos

Condição explícita de não ação: integrada há meses; o único passo útil é a comparação documental com o #174.

### Comunicação entre responsáveis

Para a consolidação: "PR #47 tornou o plugin Scala o caminho oficial no DEV e removeu o adaptador JSONL".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — manter capturadores sobrepostos exigiria definir identidade e deduplicação para evitar possível contagem duplicada. Que caso o teste ainda não cobre? — célula 4.1 no pacote operacional posterior não foi exercitada nesta auditoria. Como eu explicaria isso para outro pod? — a PR removeu o adaptador JSONL e declarou o plugin como caminho oficial; seus testes e a preservação de .env são relatos da entrega.

### Próxima ação e encerramento

Nenhuma ação obrigatória. Owner a confirmar: dono do pacote, ao tratar o #174. Encerramento: histórico.

<a id="item-454"></a>

## PR#48 — feat(infra): adicionar schema OTLP logs

Frente: historico. Encaminhamento: integrada_em_branch_de_convergencia.

### Identidade e estado

PR #48, `infra/canonical-clickstack` → `feat/base-project-e2e`; autor `gustocezar`; criada em 2026-07-23 e integrada em 2026-07-24T00:43:13Z (merge `42e61c0`); 1 commit; 3 arquivos. Chegou à main pela PR #57.

### Intenção e benefício

Adicionar a tabela `apex.otel_logs` (de propriedade do exporter) ao ClickStack canônico, porque o collector declara traces e logs e a infra precisava dos dois destinos.

### Feito, faltante e não comprovado

Feito: `infra/sql/012_otel_logs.sql` (+44), `infra/README.md` e `infra/VALIDATION.md` existem na main. Relatado: Compose renderizado e DDL aceito por `clickhouse-local` descartável. Não comprovado aqui: uso de `otel_logs` por algum consumidor.

### Linhagem

Plano V1 → PR #48 (infra) junto da PR #49 (collect) → PR #57.

### Fontes e corte

Snapshot (PR 48); dossiê (3 arquivos); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos. RELATADO: validação com `clickhouse-local`. INFERÊNCIA: tabela de aterrissagem, não contratual. Review formal (API, observada em 2026-10-17T17:28:03Z): 0 registradas; isso não prova ausência de leitura humana. Comentários inline de review: 0. Runs do Actions com o head `684770d`: nenhum no universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada. Isso não prova que nenhum CI tenha rodado fora desse universo.

### Fluxo

Fluxo declarado: pipeline de logs OTLP → exporter ClickHouse → otel_logs. Consumidores e MVs posteriores não foram inventariados nesta ficha.

### Consequências e risco

Baixo: não altera tabelas contratuais nem findings, como o corpo declara.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) avaliar, no #180 (matriz de proveniência), se `otel_logs` deve aparecer como tabela sem consumidor.

### Dependências e paralelismo

Nenhuma dependência: a tabela é de aterrissagem e não bloqueia nada; a avaliação sugerida pertence ao #180.

### Plano e aceite propostos

Condição explícita de não ação: integrada, sem efeito em contratos.

### Comunicação entre responsáveis

Para consolidação: PR #48 adicionou o destino de logs OTLP; consumo posterior não foi estabelecido nesta revisão.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — sem destino compatível, o caminho de logs precisaria de criação automática ou outra provisão; a revisão não testou esse cenário. Que caso o teste ainda não cobre? — ingestão e consumo efetivos de otel_logs não foram observados aqui. Como eu explicaria isso para outro pod? — há DDL de aterrissagem para logs OTLP, com validação histórica relatada e sem inventário completo de consumidores.

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: histórico; revisitar só se algum consumidor passar a ler `otel_logs`.

<a id="item-455"></a>

## PR#49 — feat(collect): adicionar contrato OTLP v0.2

Frente: historico. Encaminhamento: integrada_em_branch_de_convergencia.

### Identidade e estado

PR #49, `collect/otlp-contract-v02` → `feat/base-project-e2e`; autor `gustocezar`; criada em 2026-07-23 e integrada em 2026-07-24T00:43:19Z (merge `ccef27e`); 1 commit; 6 arquivos. Chegou à main pela PR #57.

### Intenção e benefício

Configurar o collector para receber spans do Apex, aplicar a segunda barreira de sanitização e encaminhar ao ClickHouse, com overlay C3 para a infra; criar a fronteira JAR → COLLECT → INFRA sem escrever direto nas tabelas contratuais.

### Feito, faltante e não comprovado

Feito: `collect/.env.c3-infra.example`, `collect/docker-compose.c3-infra.yml`, `README.md`, `VALIDATION.md` e ajustes em `config.yaml`/`docker-compose.yml`. O overlay C3 é o que o pacote usa hoje (`scripts/apex.ps1:512-513`, conferido para o #63). Relatado: Compose e config validados.

### Linhagem

Plano V1 → PR #49 → PR #57 → correção de deduplicação (PR #67, #63) → pacote (PR #76).

### Fontes e corte

Snapshot (PR 49); dossiê (6 arquivos); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_63.txt` (uso do overlay no pacote); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos e uso posterior do overlay. RELATADO: validação de config. A sanitização efetiva é assunto do #2 (Codex). Review formal (API, observada em 2026-10-17T17:28:03Z): 0 registradas; isso não prova ausência de leitura humana. Comentários inline de review: 0. Runs do Actions com o head `b3db057`: nenhum no universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada. Isso não prova que nenhum CI tenha rodado fora desse universo.

### Fluxo

Fluxo: plugin → OTLP → collector (scrub) → overlay C3 → ClickHouse da infra.

### Consequências e risco

Baixo. Limite: a sanitização foi validada como configuração, não com dados reais com PII.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) levar a prova de sanitização com dado real para a ficha #2 do Codex, que é onde a PII é tratada.

### Dependências e paralelismo

Nenhuma dependência própria; a prova de PII pertence ao #2 e a resiliência ao #63.

### Plano e aceite propostos

Condição explícita de não ação: integrada; o overlay está em uso pelo pacote atual.

### Comunicação entre responsáveis

Para a consolidação: "PR #49 criou a fronteira collect → infra usada pelo pacote".

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — um caminho de escrita que contorne o collector precisaria preservar explicitamente a sanitização e as identidades; escrita direta por si só não prova vazamento. Que caso o teste ainda não cobre? — eficácia completa do scrub em dados sensíveis não foi observada nesta auditoria. Como eu explicaria isso para outro pod? — a PR configurou recepção OTLP e entrega à infra via overlay; presença de processadores não comprova remoção completa de PII.

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: histórico; reabrir só se o pacote deixar de usar o overlay C3.

<a id="item-456"></a>

## PR#50 — feat(jar): adicionar plugin Spark 4.1.2

Frente: historico. Encaminhamento: integrada_em_branch_de_convergencia.

### Identidade e estado

PR #50, `jar/spark-4.1.2-plugin` → `feat/base-project-e2e`; autor `gustocezar`; criada em 2026-07-24 e integrada em 2026-07-24T00:43:26Z (merge `b8768e7`); 3 commits; 7 arquivos. Chegou à main pela PR #57.

### Intenção e benefício

Adicionar a célula `apex_4.1` do plugin (Spark 4.1.2 / Scala 2.13.17) com assembly sem Spark, Scala ou Jackson embutidos, como caminho oficial de telemetria da V1.

### Feito, faltante e não comprovado

Feito: `jar/build.sbt` (+33/-8) e `DriverActivationSpec.scala`; a célula 4.1 continua na main (`build.sbt:162-166`, conferido para o #16, como célula "aditiva"). Relatado: 4 testes da célula aprovados; com collector indisponível, baseline 50.593 ms e instrumentado 38.216 ms; SHA-256 do assembly registrado em `jar/VALIDATION.md`. Nota de leitura: uma medição única, sem protocolo, não permite concluir ganho, ruído ou overhead.

### Linhagem

Plano V1 → PR #50 (com correções de repositórios sbt e estabilização da prova de collector indisponível) → PR #57.

### Fontes e corte

Snapshot (PR 50); dossiê (7 arquivos, 3 commits); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_16.txt` (células no build); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos e célula no build. RELATADO: testes e tempos. INFERÊNCIA: a comparação de tempo é uma execução única, sem protocolo (ver #113). Review formal (API, observada em 2026-10-17T17:28:04Z): 0 registradas; isso não prova ausência de leitura humana. Comentários inline de review: 0. Runs do Actions com o head `da2416f`: nenhum no universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada. Isso não prova que nenhum CI tenha rodado fora desse universo.

### Fluxo

Fluxo de build: `sbt apex_41/assembly` → JAR sem dependências providas → `spark.plugins=apex.ApexPlugin` → listener.

### Consequências e risco

Baixo. Risco de leitura: citar "instrumentado 38 s × baseline 50 s" como ganho seria erro; o #113 trata exatamente essa disciplina.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) marcar na consolidação que os tempos de `jar/VALIDATION.md` não são medida de overhead.

### Dependências e paralelismo

Nenhuma dependência para a PR. A interpretação de tempos depende do protocolo do #113.

### Plano e aceite propostos

Condição explícita de não ação: integrada; a célula 4.1 continua no build.

### Comunicação entre responsáveis

Para a consolidação: "PR #50 trouxe a célula 4.1; os tempos registrados não medem overhead".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — embutir Spark ou Jackson no JAR causaria conflitos de classe no cluster. (b) Que caso o teste ainda não cobre? — overhead medido com protocolo. (c) Como eu explicaria isso para outro pod? — "o plugin roda no Spark 4.1 sem carregar suas próprias dependências". (d) Por que o instrumentado saiu mais rápido?

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: histórico; reabrir só se a célula 4.1 sair do build ou passar a embutir dependências providas.

<a id="item-457"></a>

## PR#51 — feat(e2e): validar caminho canonico seis raias

Frente: historico. Encaminhamento: integrada_em_branch_de_convergencia.

### Identidade e estado

PR #51, `e2e/six-lane-canonical-gates` → `feat/base-project-e2e` (base em `b8768e7`, depois da PR #50); autor `gustocezar`; criada em 2026-07-24 e integrada em 2026-07-24T02:22:46Z (merge `7611735`); 1 commit; 8 arquivos. Chegou à main pela PR #57.

### Intenção e benefício

Criar o gate canônico que valida um `job_id` real pelas seis raias (DEV, JAR, COLLECT, INFRA, ENGINE, SERVE), com testes de invariantes, documentação sanitizada e um wrapper PowerShell para Windows.

### Feito, faltante e não comprovado

Feito: `scripts/e2e_six_lanes.py` (+200), `tests/test_e2e_six_lanes.py` (+121), `dev/scripts/e2e_canonical.ps1` (+120), `docs/e2e/CANONICAL_GATE.md` (+72). Os dois primeiros continuam na main e receberam depois a seam `full_analyzer` (conferido para o #56). Relatado: cenários skew, spill, bad shuffle e OOM aprovados; 17 eventos, 3 findings, 0 chamadas LLM, `analyze_run` somente leitura; `4 passed` e `7 passed`.

### Linhagem

Plano V1 → PR #51 → PR #57 → seam `093c677` (#56) → demo citada no fechamento do #38.

### Fontes e corte

Snapshot (PR 51); dossiê (8 arquivos); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_56.txt`; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos. RELATADO: execução dos quatro cenários e contagens. INFERÊNCIA: a prova de 0 chamadas LLM vale para aquele run. Review formal (API, observada em 2026-10-17T17:28:05Z): 0 registradas; isso não prova ausência de leitura humana. Comentários inline de review: 0. Runs do Actions com o head `42be11d`: nenhum no universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada. Isso não prova que nenhum CI tenha rodado fora desse universo.

### Fluxo

Fluxo do gate: job canônico → plugin → collector → ClickHouse → engine → MCP `analyze_run` → asserções de invariantes.

### Consequências e risco

Baixo. O gate é a principal prova integrada histórica do produto; sua repetição atual depende de runtime autorizado.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) registrar na consolidação a data do último run conhecido do gate, para não tratar a prova de julho como atual.

### Dependências e paralelismo

A repetição do gate na main atual dependeria de ambiente autorizado (fora desta auditoria).

### Plano e aceite propostos

Condição explícita de não ação: integrada; o gate atual é a evolução deste.

### Comunicação entre responsáveis

Para a consolidação: "PR #51 criou o gate de seis raias usado depois como demo".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — sem gate integrado, cada raia passaria isolada e o todo não. (b) Que caso o teste ainda não cobre? — o gate com o crew ativo. (c) Como eu explicaria isso para outro pod? — "um job real atravessa as seis raias e o MCP responde". (d) Quando o gate rodou pela última vez?

### Próxima ação e encerramento

Nenhuma ação obrigatória. Owner a confirmar: mantenedor, se quiser rodar o gate na main atual em ambiente autorizado. Encerramento: histórico.

<a id="item-458"></a>

## PR#52 — feat(engine): add gated CrewAI judge adapter

Frente: historico. Encaminhamento: fechada_sem_merge_conteudo_reimplementado.

### Identidade e estado

PR #52, `engine/c5-gated-crew-judge-pr` → `feat/base-project-e2e`; autor `gustocezar`; criada e fechada em 2026-07-24, **sem merge**; 2 commits; 5 arquivos. O head não está na main nem na branch `base-project-e2e-augusto`.

### Intenção e benefício

Implementar o Tier 2 do engine: adaptador CrewAI preguiçoso com correlação e Judge adversarial, chamado só para candidatos CRITICAL/BLOCKER de baixa confiança, com citações tiradas da evidência do finding e sem mutações.

### Feito, faltante e não comprovado

Não integrada. O comentário de fechamento diz que o trabalho foi consolidado na branch `base-project-e2e-augusto` (o texto tem caracteres de controle `\x08`/`\x0c` no lugar de "`b" e "`f", provavelmente escapes de shell). Conferi: os commits da PR não estão naquela branch, e `engine/src/apex_engine/crew.py` também não; a branch tem a mesma ideia reestruturada em `crew/judge.py`, `crew/llms.py` e `crew/tools.py`. Na main o crew segue esse desenho em pacote (`crew/judge.py`, ver #17). Relatado: `14 passed` e smoke do provedor Anthropic local.

### Linhagem

PR #52 → fechamento sem merge (2026-07-24) → reimplementação na branch Augusto → conteúdo chega à main por PRs posteriores (#55). A PR #54 a listava com ordem de merge.

### Fontes e corte

Snapshot (PR 52) e comentário de fechamento; dossiê (5 arquivos); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/PR_52.txt` (branches que contêm o head; conteúdo da branch Augusto).

### Classe e limite da evidência

DIRETO: ausência de merge, ausência dos commits e do arquivo na branch Augusto, presença do pacote `crew/`. RELATADO: testes e smoke do provedor. INFERÊNCIA: "consolidado" significa reimplementado, não os mesmos commits. Review formal (API, observada em 2026-10-17T17:28:06Z): 0 registradas; isso não prova ausência de leitura humana. Comentários inline de review: 0. Runs do Actions com o head `05549be`: nenhum no universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada. Isso não prova que nenhum CI tenha rodado fora desse universo.

### Fluxo

Fluxo pretendido: finding Tier 1 → gate (baixa confiança e severidade alta) → correlação → Judge → veredito com citações, mesclado no finding.

### Consequências e risco

O desenho semelhante aparece no pacote crew e o autor declara consolidação, sem merge destes commits. O smoke de provedor relatado aqui tem versão e ambiente próprios; não prova resposta de toda a raia na main nem contradiz automaticamente o relato posterior de #38. O recibo #105 registra preservação do caminho de log, sem nova execução.

### Alternativas e recomendação

(a) Manter fechada como histórico (recomendado); (b) recuperar o smoke de provedor como evidência, se o #38 precisar dela.

### Dependências e paralelismo

O uso como evidência depende do #38 e de credenciais autorizadas.

### Plano e aceite propostos

Condição explícita de não ação: substituída por reimplementação.

### Comunicação entre responsáveis

Para a consolidação: "PR #52 foi fechada; o Judge foi refeito na branch Augusto e chegou à main em outra forma".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — integrar esta PR depois do pacote `crew/` criaria dois adaptadores. (b) Que caso o teste ainda não cobre? — resposta real do provedor na main atual. (c) Como eu explicaria isso para outro pod? — "o Judge desta PR foi reescrito antes de entrar". (d) O log do smoke de provedor (`evidence/engine-c5-crewai-provider-2026-07-24.log`, entregue pela PR #54) segue preservado? Conferido: está no head da PR #54 e no bundle do #105.

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: histórico; a branch segue o plano do #105.

<a id="item-459"></a>

## PR#53 — feat(serve): add KB search and safe fix proposals

Frente: historico. Encaminhamento: fechada_sem_merge_conteudo_reimplementado.

### Identidade e estado

PR #53, `serve/c4-kb-suggest-fix-pr` → `feat/base-project-e2e`; autor `gustocezar`; criada e fechada em 2026-07-24, **sem merge**; 1 commit; 6 arquivos. O head não está na main nem na branch Augusto.

### Intenção e benefício

Acrescentar ao serve `search_kb(query, top_k)` sobre a evidência persistida e `suggest_fix(job_id, finding_id?, min_confidence)` como proposta somente de revisão, sempre com `applied=false` e `requires_human_approval=true`.

### Feito, faltante e não comprovado

Não integrada; mesmo comentário de fechamento da PR #52. Conferi: o commit não está na branch Augusto; a branch tem `search_kb` em `server.py:99` e `suggest_fix` em `diagnose.py:892` (código reestruturado). Na main, `search_kb` e `suggest_fix` existem e `applied` é `Literal[False]` (conferido para #20/#38). Relatado: `8 passed`.

### Linhagem

PR #53 → fechamento sem merge → reimplementação na branch Augusto → main com `diagnose.py` e o modelo de proposta.

### Fontes e corte

Snapshot (PR 53); dossiê (6 arquivos); `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/PR_53.txt` (branches e funções na branch Augusto).

### Classe e limite da evidência

DIRETO: ausência de merge e caminhos/funções em refs delimitados. RELATADO: oito testes e consolidação. DERIVADO: desenho de proposta sem aplicação aparece nas fontes relacionadas; origem exclusiva nesta PR não foi estabelecida. API capturada retorna zero reviews/inline e janela de runs não contém o head.

### Fluxo

Fluxo pretendido: `suggest_fix` → finding persistido → proposta de diff → `applied=false`, aprovação humana obrigatória; confiança baixa vira consultiva.

### Consequências e risco

Literal[False] restringe o valor validado do campo de saída; não substitui inspeção de efeitos nem controle de autorização. Esta revisão não executou serviço ou certificou segurança integral.

### Alternativas e recomendação

(a) Manter fechada como histórico (recomendado); (b) nenhuma alternativa.

### Dependências e paralelismo

Nenhuma dependência: a funcionalidade existe na main em outra forma; não há o que integrar desta PR.

### Plano e aceite propostos

Condição explícita de não ação: substituída por reimplementação.

### Comunicação entre responsáveis

Para a consolidação: "PR #53 foi fechada; KB e proposta sem aplicação chegaram à main reescritas".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — um `suggest_fix` que aplicasse mudanças contrariaria a V0.1 (#34). (b) Que caso o teste ainda não cobre? — `search_kb` com evidência de outro job. (c) Como eu explicaria isso para outro pod? — "o MCP sugere a correção; um humano decide". (d) O rebaixamento de confiança baixa para consultiva sobreviveu?

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: histórico; a branch segue o plano do #105.

<a id="item-460"></a>

## PR#54 — docs(c9): record Engine and Serve delivery status

Frente: historico. Encaminhamento: fechada_sem_merge_documento_preservado_em_branch.

### Identidade e estado

PR #54, `docs/c9-engine-serve-status` → `feat/base-project-e2e`; autor `gustocezar`; criada e fechada em 2026-07-24, **sem merge**; 2 commits; 5 arquivos.

### Intenção e benefício

Dar ao Commander um ponto único de revisão das entregas ENGINE/C5 e SERVE/C4: links e ordem de merge das PRs #52 e #53, evidência sanitizada do smoke do Judge e da validação MCP stdio, e limites (sem auto-apply, rerun, UI, instalador nem CI remoto).

### Feito, faltante e não comprovado

Não integrada; mesmo fechamento das PRs #52/#53. Conferi: `docs/convergence/C9-ENGINE-SERVE-DELIVERY-STATUS-2026-07-24.md` e `evidence/serve-c4-stdio-mcp-2026-07-24.log` existem na branch `base-project-e2e-augusto`; não existem na main. O corpo declara explicitamente não afirmar que #52 e #53 estavam integradas, uma boa prática.

### Linhagem

PRs #52/#53 → PR #54 (status) → fechamento sem merge → documento na branch Augusto → #55 acompanha a decisão.

### Fontes e corte

Snapshot (PR 54); dossiê; `fontes/batch-claude-historico-corrigido-sources/claude/fontes/git/PR_54.txt` (arquivos na branch Augusto).

### Classe e limite da evidência

DIRETO: arquivos na branch, ausência na main. RELATADO: evidências sanitizadas (logs). Review formal (API, observada em 2026-10-17T17:28:07Z): 0 registradas; isso não prova ausência de leitura humana. Comentários inline de review: 0. Runs do Actions com o head `2bd0248`: nenhum no universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada. Isso não prova que nenhum CI tenha rodado fora desse universo.

### Fluxo

Fluxo documental: entregas C4/C5 → documento de status e logs → revisão do Commander (não registrada) → fechamento.

### Consequências e risco

Baixo. Nas refs consultadas, a evidência do smoke real do Judge (`evidence/engine-c5-crewai-provider-2026-07-24.log`) não está na main e está no head desta PR (`2bd0248`, preservado pela ref de PR do GitHub) e na branch `base-project-e2e-augusto` (`3d4b05b`), contida no ref `base-project-e2e-augusto` do bundle do #105 (`7f53d22`); apagar a branch não a perderia enquanto o bundle e a ref de PR existirem (`fontes/batch-claude-historico-corrigido-sources/claude/fontes/reconferencia/ponto12-bundle-105.txt`).

### Alternativas e recomendação

(a) Manter fechada (recomendado); (b) nada a garantir neste ponto: conferi que o bundle do #105 inclui a branch `base-project-e2e-augusto` (`3d4b05b` é ancestral do ref arquivado `7f53d22`), com o log.

### Dependências e paralelismo

A preservação da evidência depende do #105 (bundle e mapa de branches); não há dependência técnica de produto.

### Plano e aceite propostos

Não ação documental: o recibo ponto12 registra hash do bundle, contenção do head 3d4b05b da branch e caminhos de evidência no ref arquivado. O head 2bd0248 da PR não é contido nos cinco refs; sua preservação adicional consta da ref de PR capturada. Nenhuma dessas verificações foi reexecutada neste turno.

### Comunicação entre responsáveis

Para a consolidação: "PR #54 foi fechada; o status C9 e os logs vivem na branch Augusto".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — apagar a branch Augusto e perder também o bundle e a ref da PR #54 apagaria o log de smoke do Judge que conhecemos. (b) Que caso o teste ainda não cobre? — não encontrei teste ligado a este item nas fontes lidas; é documento. (c) Como eu explicaria isso para outro pod? — "era o resumo para o Commander; ficou na branch de revisão". (d) Quem decide se a ref de PR e o bundle bastam como custódia?

### Próxima ação e encerramento

Owner a confirmar: custodiante do #105. Entrada: mapa do bundle (conferido). Saída: decisão do custodiante sobre a branch. Encerramento: a PR segue fechada.

