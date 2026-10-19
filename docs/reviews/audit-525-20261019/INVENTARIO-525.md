# Inventário das 525 fichas

Estado documental não significa implementação, aprovação ou aceite. Novo aceite funcional: **false em todas as 525 fichas**. [JSON](INVENTARIO-525.json) e [CSV](INVENTARIO-525.csv) têm origem e filtro dos 158 canônicos.

| ID | Tema | Origem | Canônico | Ficha |
|---|---|---|---|---|
| PR#155 | test(engine): keep schema preflight aligned with stage queries | GitHub PR | não | [ler](fichas-01.md#item-001) |
| PR#157 | test(serve): pin eight-tool transport parity with identical arguments | GitHub PR | não | [ler](fichas-01.md#item-002) |
| PR#158 | test(serve): pin findings score-tie order on both SQL doors | GitHub PR | não | [ler](fichas-01.md#item-003) |
| PR#159 | fix(serve): make parity gate diagnose drift and clean derived fixture rows | GitHub PR | não | [ler](fichas-01.md#item-004) |
| PR#161 | ci: keep root gate diagnostics after Python lane failures | GitHub PR | não | [ler](fichas-01.md#item-005) |
| PR#162 | fix(verify): align module version with package 0.1.0 | GitHub PR | não | [ler](fichas-01.md#item-006) |
| PR#163 | test(serve): pin search_kb plan_json hits over both transports | GitHub PR | não | [ler](fichas-01.md#item-007) |
| PR#164 | docs: align Serve and Verify docs with current contract | GitHub PR | não | [ler](fichas-01.md#item-008) |
| #1 | Collector MVP: configuração e rota de ingestão | GitHub issue | não | [ler](fichas-01.md#item-009) |
| #2 | Collector PII: controles apontados no encerramento | GitHub issue | não | [ler](fichas-01.md#item-010) |
| #3 | Collector backpressure: estratégia histórica documentada | GitHub issue | não | [ler](fichas-02.md#item-011) |
| #4 | Schema Collector: proposta substituída pelo contrato | GitHub issue | não | [ler](fichas-02.md#item-012) |
| T-20260923-console-auto-prefers-api | Preferência automática pela API — proposta substituída | Task-Spec do repositório | não | [ler](fichas-02.md#item-013) |
| #115 | Atribuição execution_id → stages: resolver existente e integração por escolher | GitHub issue | não | [ler](fichas-02.md#item-014) |
| #117 | Atribuição e piso de ruído entre Verify, storage, Serve e Front | GitHub issue | não | [ler](fichas-02.md#item-015) |
| #123 | Tail-outlier: integração presente, runtime histórico e associação limitada | GitHub issue | não | [ler](fichas-02.md#item-016) |
| #124 | PowerShell: dependência explícita e lacuna na prova do dispatch | GitHub issue | não | [ler](fichas-02.md#item-017) |
| #165 | [Docs][Cross-pod] Reconciliar a linhagem do contrato e os cabeçalhos SQL | GitHub issue | não | [ler](fichas-02.md#item-018) |
| #166 | [Feature][Pods 1 e 3] Explicar TAIL_OUTLIER nos consumidores sem confundir cauda com skew | GitHub issue | não | [ler](fichas-02.md#item-019) |
| #167 | [Bug][Pod 2] Alinhar argumentos do braço ON do harness R9D com o runner canônico | GitHub issue | não | [ler](fichas-02.md#item-020) |
| #168 | [Study][Pod 2] Avaliar caudas de duração muito pequenas antes de propor piso absoluto | GitHub issue | não | [ler](fichas-03.md#item-021) |
| #169 | [Decision][Cross-pod] Definir seleção de tentativa e população de métricas entre consumidores | GitHub issue | não | [ler](fichas-03.md#item-022) |
| #170 | [Decision][Pod 2 / Infra] Definir reaplicação de DDL e o alcance de verify-ddl | GitHub issue | não | [ler](fichas-03.md#item-023) |
| #171 | [Decision][Pods 1 e 3] Definir exposição do OpenAPI e quem guarda o token da API v1 | GitHub issue | não | [ler](fichas-03.md#item-024) |
| #172 | [Test][Pods 1 e 3] Validar o perfil HTTP da Console no nginx e no navegador | GitHub issue | não | [ler](fichas-03.md#item-025) |
| #173 | [Study][Pods 2 e 3] Auditar a seleção de database ClickHouse por consumidor | GitHub issue | não | [ler](fichas-03.md#item-026) |
| #174 | [Bug][Pod 2 / Package] Preservar dev/.env ao preparar o runner canônico | GitHub issue | não | [ler](fichas-03.md#item-027) |
| #175 | [Decision][Pod 2 / Package] Definir identidade e ownership de stacks entre checkouts | GitHub issue | não | [ler](fichas-03.md#item-028) |
| #176 | [Study][Pod 2 / Infra] Documentar rotação de credencial local ClickHouse e recuperação | GitHub issue | não | [ler](fichas-03.md#item-029) |
| #177 | [Study][Pod 3] Definir narração AQE usando configuração capturada em job_conf | GitHub issue | não | [ler](fichas-03.md#item-030) |
| #178 | [Feature][Pod 2 / Harness] Respeitar o endpoint OTLP escolhido nos alvos de patologia | GitHub issue | não | [ler](fichas-04.md#item-031) |
| #179 | [Study][Pod 1 / Verify] Avaliar trabalho medido e fallback estimado no predictor | GitHub issue | não | [ler](fichas-04.md#item-032) |
| #180 | [Docs][Cross-pod] Atualizar cobertura da matriz para Front, API e proveniência | GitHub issue | não | [ler](fichas-04.md#item-033) |
| G01 | Restaurar GitHub Actions da conta luanmorenommaciel | registro canônico (158) | sim | [ler](fichas-04.md#item-034) |
| G02 | Proteger main com PR obrigatório, checks e política de bypass | registro canônico (158) | sim | [ler](fichas-04.md#item-035) |
| G03 | Revisar e reduzir a fila #126–#134 | registro canônico (158) | sim | [ler](fichas-04.md#item-036) |
| G04 | Encerrar issues cobertas somente após merge (mapa corrigido) | registro canônico (158) | sim | [ler](fichas-04.md#item-037) |
| G05 | Incorporar reconciliação do roadmap/backlog do workspace | registro canônico (158) | sim | [ler](fichas-04.md#item-038) |
| G06 | Monitor ampliado e baseline completo | registro canônico (158) | sim | [ler](fichas-04.md#item-039) |
| G07 | Corrigir referência a e2e.yml inexistente no CI | registro canônico (158) | sim | [ler](fichas-04.md#item-040) |
| G08 | Validar semanticamente a combinação #127×#128 | registro canônico (158) | sim | [ler](fichas-05.md#item-041) |
| G09 | Citar o segredo gerado no gate de configuração do Collector | registro canônico (158) | sim | [ler](fichas-05.md#item-042) |
| G10 | Revisar SC2016 na combinação dos PRs de CI | registro canônico (158) | sim | [ler](fichas-05.md#item-043) |
| issue115-attribution-audit-hardening.yaml | issue115-attribution-audit-hardening.yaml | Task-Spec do repositório | não | [ler](fichas-05.md#item-044) |
| issue115-attribution-conflict-collision.yaml | issue115-attribution-conflict-collision.yaml | Task-Spec do repositório | não | [ler](fichas-05.md#item-045) |
| issue115-attribution-scope-collision.yaml | issue115-attribution-scope-collision.yaml | Task-Spec do repositório | não | [ler](fichas-05.md#item-046) |
| issue115-execution-attribution-offline.yaml | issue115-execution-attribution-offline.yaml | Task-Spec do repositório | não | [ler](fichas-05.md#item-047) |
| issue123-audit-remediation.yaml | issue123-audit-remediation.yaml | Task-Spec do repositório | não | [ler](fichas-05.md#item-048) |
| issue123-tail-outlier-engine.yaml | issue123-tail-outlier-engine.yaml | Task-Spec do repositório | não | [ler](fichas-05.md#item-049) |
| issue123-tail-outlier-package-wiring.yaml | issue123-tail-outlier-package-wiring.yaml | Task-Spec do repositório | não | [ler](fichas-05.md#item-050) |
| issue123-tail-outlier-runtime-gate.yaml | issue123-tail-outlier-runtime-gate.yaml | Task-Spec do repositório | não | [ler](fichas-06.md#item-051) |
| issue124-audit-remediation.yaml | issue124-audit-remediation.yaml | Task-Spec do repositório | não | [ler](fichas-06.md#item-052) |
| issue124-pwsh-command-aware.yaml | issue124-pwsh-command-aware.yaml | Task-Spec do repositório | não | [ler](fichas-06.md#item-053) |
| l1-connect.yaml | l1-connect.yaml | Task-Spec do repositório | não | [ler](fichas-06.md#item-054) |
| l2-discover.yaml | l2-discover.yaml | Task-Spec do repositório | não | [ler](fichas-06.md#item-055) |
| l3-understand.yaml | l3-understand.yaml | Task-Spec do repositório | não | [ler](fichas-06.md#item-056) |
| l5-fix.yaml | l5-fix.yaml | Task-Spec do repositório | não | [ler](fichas-06.md#item-057) |
| l6-learn.yaml | l6-learn.yaml | Task-Spec do repositório | não | [ler](fichas-06.md#item-058) |
| serve-api-e2e.yaml | serve-api-e2e.yaml | Task-Spec do repositório | não | [ler](fichas-06.md#item-059) |
| serve-api-sweep.yaml | serve-api-sweep.yaml | Task-Spec do repositório | não | [ler](fichas-06.md#item-060) |
| serve-api-wire.yaml | serve-api-wire.yaml | Task-Spec do repositório | não | [ler](fichas-07.md#item-061) |
| serve-api.yaml | serve-api.yaml | Task-Spec do repositório | não | [ler](fichas-07.md#item-062) |
| P01 | PR #126 — atribuição offline execution→stages | registro canônico (158) | sim | [ler](fichas-07.md#item-063) |
| P02 | PR #127 — gate determinístico tail-outlier | registro canônico (158) | sim | [ler](fichas-07.md#item-064) |
| P03 | PR #128 — cobertura PowerShell command-aware | registro canônico (158) | sim | [ler](fichas-07.md#item-065) |
| E01 | Provar #126 em runtime completo | registro canônico (158) | sim | [ler](fichas-07.md#item-066) |
| E02 | Integrar atribuição de stages aos consumidores (T24b–d) | registro canônico (158) | sim | [ler](fichas-07.md#item-067) |
| E14 | Validar #127 nas combinações Spark prometidas | registro canônico (158) | sim | [ler](fichas-07.md#item-068) |
| E17 | Higiene do gate tail-outlier (P10, P12, P13) | registro canônico (158) | sim | [ler](fichas-07.md#item-069) |
| L09 | HARN-BINDING — run-pathology repassar APEX_OTLP_ENDPOINT | registro canônico (158) | sim | [ler](fichas-07.md#item-070) |
| X06 | Arquivar branches históricas antes de excluir (#105) | registro canônico (158) | sim | [ler](fichas-08.md#item-071) |
| L03 | Salvage das cinco branches | registro canônico (158) | sim | [ler](fichas-08.md#item-072) |
| DEC-13 | Custódia do bundle #105 e escopo de branches | registro de decisões | não | [ler](fichas-08.md#item-073) |
| F02 | Tabela verdade do piso de ruído (T09a) | registro canônico (158) | sim | [ler](fichas-08.md#item-074) |
| F03 | Atribuição true/false/unknown (T09b) | registro canônico (158) | sim | [ler](fichas-08.md#item-075) |
| F04 | Corrigir modelo e serialização da atribuição (T13a) | registro canônico (158) | sim | [ler](fichas-08.md#item-076) |
| F05 | Representação persistida e migração (T13b) | registro canônico (158) | sim | [ler](fichas-08.md#item-077) |
| F06 | Gravador de fix_verifications / pipeline Verify (T08/T13c) | registro canônico (158) | sim | [ler](fichas-08.md#item-078) |
| F07 | Persistir amostras de replay para recalcular CV (T13d) | registro canônico (158) | sim | [ler](fichas-08.md#item-079) |
| F08 | VerificationView canônica e versionada (T14) | registro canônico (158) | sim | [ler](fichas-08.md#item-080) |
| F09 | Consumidor Front live compatível (T15) | registro canônico (158) | sim | [ler](fichas-09.md#item-081) |
| F10 | E2E Verify→storage→Serve→Front (T16) | registro canônico (158) | sim | [ler](fichas-09.md#item-082) |
| F11 | Direção, igualdade e delta↔saving (T11) | registro canônico (158) | sim | [ler](fichas-09.md#item-083) |
| F17 | Alinhar ou remover o recálculo de CV no Front (T10) | registro canônico (158) | sim | [ler](fichas-09.md#item-084) |
| DEC-05 | Escopo e representação do contrato de piso/atribuição (#117) | registro de decisões | não | [ler](fichas-09.md#item-085) |
| DEC-06 | Ownership de Verify e Memory e existência de escritor externo | registro de decisões | não | [ler](fichas-09.md#item-086) |
| DEC-09 | Consumo da atribuição de stage (#115) | registro de decisões | não | [ler](fichas-09.md#item-087) |
| DEC-N6 | Associação forte/fraca no gate tail-outlier (E17) | decisão nova desta revisão | não | [ler](fichas-09.md#item-088) |
| #21 | [FEATURE] CI Integration (pre-merge code review) | GitHub issue | não | [ler](fichas-09.md#item-089) |
| #33 | [Governance] Add SECURITY.md (LICENSE + NOTICE done) | GitHub issue | não | [ler](fichas-09.md#item-090) |
| #42 | [SPIKE] Definir modo offline/on-prem seguro para agentes Apex | GitHub issue | não | [ler](fichas-10.md#item-091) |
| #105 | [Governance] Archive historical contribution branches before deletion | GitHub issue | não | [ler](fichas-10.md#item-092) |
| #106 | [ADR/Study] Evaluate a read-only APEX system and contract graph | GitHub issue | não | [ler](fichas-10.md#item-093) |
| #107 | [Study][Pod 3 / Serve] Define a read-only APEX system-graph MCP interface | GitHub issue | não | [ler](fichas-10.md#item-094) |
| #108 | [Study][Pod 1 / Front-End] Explore topology and evidence-provenance views | GitHub issue | não | [ler](fichas-10.md#item-095) |
| #109 | [Study][Pod 2 / Infra] Define declared-contract versus runtime reconciliation | GitHub issue | não | [ler](fichas-10.md#item-096) |
| #112 | [Study][Cross-lane] Define versioned deterministic runbooks and negative baselines | GitHub issue | não | [ler](fichas-10.md#item-097) |
| #113 | [Harness] Ratify a versioned R9D overhead evidence protocol | GitHub issue | não | [ler](fichas-10.md#item-098) |
| #114 | [Study][Infra] Rehearse ClickHouse 26.x upgrade and rollback | GitHub issue | não | [ler](fichas-10.md#item-099) |
| #122 | [Decision][Cross-pod] Ratify the Ask HTTP/BFF boundary and atomic publication sequence | GitHub issue | não | [ler](fichas-10.md#item-100) |
| #125 | [Governance] Protect main with required CI checks and pull-request review | GitHub issue | não | [ler](fichas-11.md#item-101) |
| #130 | [Governance] Restore GitHub Actions billing for required CI | GitHub issue | não | [ler](fichas-11.md#item-102) |
| #154 | [Test][Pod 2 / Engine] Keep schema preflight aligned with stage queries | GitHub issue | não | [ler](fichas-11.md#item-103) |
| #156 | [Test][Pod 3 / Serve] Strengthen transport parity and console findings regression gates | GitHub issue | não | [ler](fichas-11.md#item-104) |
| CL-01 | Candidato local #167/#174 (`candidate.patch`, sha256 1122d031…) e prova do entrypoint integral sob stubs | relato local 2026-10-11 | não | [ler](fichas-11.md#item-105) |
| CL-02 | Correção de texto: predict.py:19-21,158 e models.py:38-40 (patch local cobre só predict.py; AC-10) | relato local 2026-10-15 + FATO | não | [ler](fichas-11.md#item-106) |
| CL-03 | Pacote `windows-ready/` (15 itens previstos) | relato local 2026-10-11 | não | [ler](fichas-11.md#item-107) |
| CL-04 | `generate_g2_results.py` com alegação obsoleta de isolamento (tooling de revisão) | relato local 2026-10-12 | não | [ler](fichas-11.md#item-108) |
| CL-05 | Correção mínima do Task-Spec 3.9.0 (handoff Tier-2 estrutural) | relato local 2026-10-12 | não | [ler](fichas-11.md#item-109) |
| CL-06 | Linhagem de aceite estrutural C2 (31 passed; sem aceite formal) | relato local 2026-10-12 | não | [ler](fichas-11.md#item-110) |
| DEC-15 | Publicação dos candidatos locais | registro de decisões | não | [ler](fichas-12.md#item-111) |
| DEC-N5 | Binding posicional do runner ON (#167) | decisão nova desta revisão | não | [ler](fichas-12.md#item-112) |
| DEC-N3 | Escopo da #164 e da correção de texto (predict.py, models.py) | decisão nova desta revisão | não | [ler](fichas-12.md#item-113) |
| PROP-D09-MAIN-TEST | [Test][Loader] Suíte de testes unitários em main_test.go para eventlog-loader (TS11) | minuta local 2026-10-11 | não | [ler](fichas-12.md#item-114) |
| PROP-D02-LOADER-MODULARIZATION | [Tooling][Dataship] Refatoração modular do eventlog-loader por responsabilidade (D02) | minuta local 2026-10-11 | não | [ler](fichas-12.md#item-115) |
| PROP-D03-SPARK-JOBS | [Feature][Dataship] Ingestão da entidade spark_jobs no ClickHouse (D03) | minuta local 2026-10-11 | não | [ler](fichas-12.md#item-116) |
| PROP-D04-SPARK-SQL-EXECUTION-JOBS | [Feature][Dataship] Mapeamento relacional spark_sql_execution_jobs (D04) | minuta local 2026-10-11 | não | [ler](fichas-12.md#item-117) |
| S01 | task_time_ms=0 para run não indexado | registro canônico (158) | sim | [ler](fichas-12.md#item-118) |
| S02 | Queries da #129 contra ClickHouse real | registro canônico (158) | sim | [ler](fichas-12.md#item-119) |
| S03 | Build/teste nginx com proxy /v1 | registro canônico (158) | sim | [ler](fichas-12.md#item-120) |
| S04 | Validação visual das telas via HTTP | registro canônico (158) | sim | [ler](fichas-13.md#item-121) |
| S05 | Exposição de /docs e /openapi.json sem token | registro canônico (158) | sim | [ler](fichas-13.md#item-122) |
| S06 | Onde o token HTTP fica (browser vs injeção pelo nginx) | registro canônico (158) | sim | [ler](fichas-13.md#item-123) |
| S07 | Decidir e implementar /ask | registro canônico (158) | sim | [ler](fichas-13.md#item-124) |
| S08 | Caracterizar os oito tools antes de refactor (T19a) | registro canônico (158) | sim | [ler](fichas-13.md#item-125) |
| S09 | MCP sem credencial direta do ClickHouse | registro canônico (158) | sim | [ler](fichas-13.md#item-126) |
| S10 | Piso Memory→Serve com proveniência (T35a/b) | registro canônico (158) | sim | [ler](fichas-13.md#item-127) |
| S11 | Falhas e conflitos do piso Memory→Serve (T35c) | registro canônico (158) | sim | [ler](fichas-13.md#item-128) |
| S12 | Catálogo de runbooks determinísticos (#112) | registro canônico (158) | sim | [ler](fichas-13.md#item-129) |
| DEC-01 | Regularizar billing do GitHub Actions da conta `luanmorenommaciel` | registro de decisões | não | [ler](fichas-13.md#item-130) |
| DEC-02 | Política de proteção da `main` e de dependências | registro de decisões | não | [ler](fichas-14.md#item-131) |
| DEC-03 | Merge e ordem da fila #126–#134 | registro de decisões | não | [ler](fichas-14.md#item-132) |
| NOV-01 | Migração de `ubuntu-latest` para Ubuntu 26 entre 2026-10-19 e 2026-11-19; o manifesto da imagem lista PowerShell 7.6.6 (AC-07) | achado desta revisão | não | [ler](fichas-14.md#item-133) |
| DEC-N1 | Runner do CI frente à migração Ubuntu 26 | decisão nova desta revisão | não | [ler](fichas-14.md#item-134) |
| NOV-02 | CI principal sem run verde na main pós-integração; prova hospedada parcial: `jar` agendado verde em 2026-10-12 no SHA atual (AC-06) | achado desta revisão | não | [ler](fichas-14.md#item-135) |
| NOV-03 | Fila aberta #155, #157–#159, #161–#164 sem review formal registrada; 3 heads com CI só do workflow anterior a #160 (AC-12) | achado desta revisão | não | [ler](fichas-14.md#item-136) |
| DEC-N4 | Método e ordem de integração da fila #155–#164 | decisão nova desta revisão | não | [ler](fichas-14.md#item-137) |
| NOV-04 | Falta uma visão atual datada: o registro CSV é histórico; o MATRIX.csv não carrega o estado reconciliado, que está em MATRIX.json (AC-04) | achado desta revisão (corrigido) | não | [ler](fichas-14.md#item-138) |
| NOV-05 | Front declara `CONTRACT_VERSION = "0.5"` enquanto `CONTRACT.md` declara v0.6 | relato #180 + FATO na main | não | [ler](fichas-14.md#item-139) |
| NOV-06 | Status desatualizado de Task-Specs em `tasks/` | achado desta revisão | não | [ler](fichas-14.md#item-140) |
| DEC-N7 | Responsável por fechar Task-Specs | decisão nova desta revisão | não | [ler](fichas-15.md#item-141) |
| NOV-07 | Conflito de desenho: checks exigidos (#125) × `paths-ignore` do CI enxuto | achado desta revisão | não | [ler](fichas-15.md#item-142) |
| DEC-N2 | Política de versão e distribuição (Verify, release v1, PyPI) | decisão nova desta revisão | não | [ler](fichas-15.md#item-143) |
| DEC-04 | Fechamento de issues após merge | registro de decisões | não | [ler](fichas-15.md#item-144) |
| DEC-07 | #122 proceed/defer/reject reenquadrado sobre a #129 | registro de decisões | não | [ler](fichas-15.md#item-145) |
| DEC-08 | Token e exposição de `/docs`/`/openapi.json` na #129 | registro de decisões | não | [ler](fichas-15.md#item-146) |
| DEC-10 | Contenção operacional da #127 (dev/.env, ownership, Windows, cold start) | registro de decisões | não | [ler](fichas-15.md#item-147) |
| DEC-11 | ADR-004 de correlação de origem e numeração de ADRs | registro de decisões | não | [ler](fichas-15.md#item-148) |
| DEC-12 | Canal e triagem do SECURITY.md | registro de decisões | não | [ler](fichas-15.md#item-149) |
| DEC-14 | Texto do CONTRACT.md e marcadores PROPOSED | registro de decisões | não | [ler](fichas-15.md#item-150) |
| DEC-16 | Atualizar escopo do monitor automático — concluída | registro de decisões | não | [ler](fichas-16.md#item-151) |
| DEC-17 | Preservar o candidato Ask V2 não commitado — concluída | registro de decisões | não | [ler](fichas-16.md#item-152) |
| DEC-18 | Custódia dos relatórios 09-21 — concluída | registro de decisões | não | [ler](fichas-16.md#item-153) |
| DEC-19 | Estudos #106–#109, #112–#114: adotar/adiar/rejeitar | registro de decisões | não | [ler](fichas-16.md#item-154) |
| DEC-20 | Merge da PR #1 e prioridade do roadmap do laboratório | registro de decisões | não | [ler](fichas-16.md#item-155) |
| DEC-21 | Merge da workspace PR #4 e valores MinIO | registro de decisões | não | [ler](fichas-16.md#item-156) |
| DEC-22 | F4.3 como leg própria do Serve | registro de decisões | não | [ler](fichas-16.md#item-157) |
| DEC-23 | Convenção de tentativa nas leituras do Serve: `ts` × `(stage_attempt, ts)` (delta 2026-09-29) | registro de decisões | não | [ler](fichas-16.md#item-158) |
| DEC-24 | Rótulo de população e migração de `run_outcomes` na Memory (delta 2026-09-29) | registro de decisões | não | [ler](fichas-16.md#item-159) |
| DEC-25 | Reaplicação de DDL durante ingestão e escopo do `verify_ddl.py` (delta 2026-09-30) | registro de decisões | não | [ler](fichas-16.md#item-160) |
| P04 | PR #129 — apex-api HTTP entre ClickHouse e consumidores | registro canônico (158) | sim | [ler](fichas-17.md#item-161) |
| P05 | PR #131 — preflight de schema do Engine | registro canônico (158) | sim | [ler](fichas-17.md#item-162) |
| P06 | PR #132 — reconciliar docs de contrato/Serve | registro canônico (158) | sim | [ler](fichas-17.md#item-163) |
| P07 | PR #133 — ADR-004 fronteira de correlação de origem (F4.1) | registro canônico (158) | sim | [ler](fichas-17.md#item-164) |
| P08 | PR #134 — README alinhado a v0.6 | registro canônico (158) | sim | [ler](fichas-17.md#item-165) |
| P09 | Workspace PR #4 — reconciliar roadmap/backlog | registro canônico (158) | sim | [ler](fichas-17.md#item-166) |
| P10 | Dataship PR #1 — output local compartilhado master/worker | registro canônico (158) | sim | [ler](fichas-17.md#item-167) |
| T-20260817-cursor-codex-config | T-20260817-cursor-codex-config.md | Task-Spec do repositório | não | [ler](fichas-17.md#item-168) |
| T-20260817-drop-from-path | T-20260817-drop-from-path.md | Task-Spec do repositório | não | [ler](fichas-17.md#item-169) |
| T-20260817-five-tools-assertion | T-20260817-five-tools-assertion.md | Task-Spec do repositório | não | [ler](fichas-17.md#item-170) |
| T-20260817-four-to-five-doc-ripple | T-20260817-four-to-five-doc-ripple.md | Task-Spec do repositório | não | [ler](fichas-18.md#item-171) |
| T-20260817-gate-status-assert | T-20260817-gate-status-assert.md | Task-Spec do repositório | não | [ler](fichas-18.md#item-172) |
| T-20260817-graphify-rebuild | T-20260817-graphify-rebuild.md | Task-Spec do repositório | não | [ler](fichas-18.md#item-173) |
| T-20260817-name-endpoint-in-error | T-20260817-name-endpoint-in-error.md | Task-Spec do repositório | não | [ler](fichas-18.md#item-174) |
| T-20260817-pypi-metadata | T-20260817-pypi-metadata.md | Task-Spec do repositório | não | [ler](fichas-18.md#item-175) |
| T-20260817-pypi-publish | T-20260817-pypi-publish.md | Task-Spec do repositório | não | [ler](fichas-18.md#item-176) |
| T-20260817-register-apex-status | T-20260817-register-apex-status.md | Task-Spec do repositório | não | [ler](fichas-18.md#item-177) |
| T-20260817-resolve-settings-extract | T-20260817-resolve-settings-extract.md | Task-Spec do repositório | não | [ler](fichas-18.md#item-178) |
| T-20260817-root-mcp-json | T-20260817-root-mcp-json.md | Task-Spec do repositório | não | [ler](fichas-18.md#item-179) |
| T-20260817-startup-stderr-banner | T-20260817-startup-stderr-banner.md | Task-Spec do repositório | não | [ler](fichas-18.md#item-180) |
| T-20260817-status-assembler | T-20260817-status-assembler.md | Task-Spec do repositório | não | [ler](fichas-19.md#item-181) |
| T-20260817-status-degraded-path | T-20260817-status-degraded-path.md | Task-Spec do repositório | não | [ler](fichas-19.md#item-182) |
| T-20260817-status-store-down-e2e | T-20260817-status-store-down-e2e.md | Task-Spec do repositório | não | [ler](fichas-19.md#item-183) |
| T-20260817-stdio-gate-five-tools | T-20260817-stdio-gate-five-tools.md | Task-Spec do repositório | não | [ler](fichas-19.md#item-184) |
| T-20260817-surface-defaulted-vars | T-20260817-surface-defaulted-vars.md | Task-Spec do repositório | não | [ler](fichas-19.md#item-185) |
| T-20260817-table-columns-probe | T-20260817-table-columns-probe.md | Task-Spec do repositório | não | [ler](fichas-19.md#item-186) |
| T-20260817-testpypi-rehearsal | T-20260817-testpypi-rehearsal.md | Task-Spec do repositório | não | [ler](fichas-19.md#item-187) |
| T-20260817-wheel-content-check | T-20260817-wheel-content-check.md | Task-Spec do repositório | não | [ler](fichas-19.md#item-188) |
| T-20260819-retry-pressure-watcher | T-20260819-retry-pressure-watcher.md | Task-Spec do repositório | não | [ler](fichas-19.md#item-189) |
| T-20260819-retry-safe-stage-fields | T-20260819-retry-safe-stage-fields.md | Task-Spec do repositório | não | [ler](fichas-19.md#item-190) |
| T-20260820-effective-duration-properties | T-20260820-effective-duration-properties.md | Task-Spec do repositório | não | [ler](fichas-20.md#item-191) |
| T-20260820-tail-outlier-raw-fields | T-20260820-tail-outlier-raw-fields.md | Task-Spec do repositório | não | [ler](fichas-20.md#item-192) |
| T-20260920-tail-outlier-runtime-gate | T-20260920-tail-outlier-runtime-gate.md | Task-Spec do repositório | não | [ler](fichas-20.md#item-193) |
| T-20260817-serverstatus-model | T-20260817-serverstatus-model.md | Task-Spec do repositório | não | [ler](fichas-20.md#item-194) |
| T-20260817-store-health-query | T-20260817-store-health-query.md | Task-Spec do repositório | não | [ler](fichas-20.md#item-195) |
| F01 | Criar issue específica do /verify | registro canônico (158) | sim | [ler](fichas-20.md#item-196) |
| F12 | Independência mecanismo/runtime no Front (T12) | registro canônico (158) | sim | [ler](fichas-20.md#item-197) |
| F13 | Apresentar TAIL_OUTLIER no Front (T29) | registro canônico (158) | sim | [ler](fichas-20.md#item-198) |
| F14 | Endurecer CI do Front | registro canônico (158) | sim | [ler](fichas-20.md#item-199) |
| F15 | Topologia e proveniência visual (#108) | registro canônico (158) | sim | [ler](fichas-20.md#item-200) |
| F16 | Atualizar KnownFindingType (RETRY_PRESSURE já na main; TAIL_OUTLIER após #127) | registro canônico (158) | sim | [ler](fichas-21.md#item-201) |
| F18 | Texto do mechanism_check do Verify para tipos não-skew | registro canônico (158) | sim | [ler](fichas-21.md#item-202) |
| F19 | Proveniência de versão e docs do Verify | registro canônico (158) | sim | [ler](fichas-21.md#item-203) |
| F20 | Verify usa a população de tarefas bem-sucedidas do contrato v0.5 (TS45) | registro canônico (158) | sim | [ler](fichas-21.md#item-204) |
| F21 | Verify recusa piso de ruído negativo ou não finito na certificação | registro canônico (158) | sim | [ler](fichas-21.md#item-205) |
| E03 | Provar #131 contra ClickHouse real com database alternativo | registro canônico (158) | sim | [ler](fichas-21.md#item-206) |
| E04 | Database configurável nas lanes ainda com 'apex.' literal | registro canônico (158) | sim | [ler](fichas-21.md#item-207) |
| E05 | Reconciliação contrato declarado × runtime (#109) | registro canônico (158) | sim | [ler](fichas-21.md#item-208) |
| E06 | Protocolo versionado R9D (#113) | registro canônico (158) | sim | [ler](fichas-21.md#item-209) |
| E07 | Rehearsal ClickHouse 26.x e rollback (#114) | registro canônico (158) | sim | [ler](fichas-21.md#item-210) |
| E08 | Preservar dev/.env do operador (T33) | registro canônico (158) | sim | [ler](fichas-22.md#item-211) |
| E09 | Identidade de checkout/daemon/Compose (T34a) | registro canônico (158) | sim | [ler](fichas-22.md#item-212) |
| E10 | Guard de ownership antes de mutações Docker (T34b) | registro canônico (158) | sim | [ler](fichas-22.md#item-213) |
| E11 | Preflight read-only de dono de porta | registro canônico (158) | sim | [ler](fichas-22.md#item-214) |
| E12 | Fronteira de credenciais S3A do Dev | registro canônico (158) | sim | [ler](fichas-22.md#item-215) |
| E13 | Rotação local de credencial ClickHouse | registro canônico (158) | sim | [ler](fichas-22.md#item-216) |
| E15 | Política de dependências e checks | registro canônico (158) | sim | [ler](fichas-22.md#item-217) |
| E16 | Regressões do harness R9D | registro canônico (158) | sim | [ler](fichas-22.md#item-218) |
| E18 | Piso absoluto de duração no watcher tail-outlier | registro canônico (158) | sim | [ler](fichas-22.md#item-219) |
| E19 | Endurecer guard SQL×DDL (#94 follow-up) | registro canônico (158) | sim | [ler](fichas-22.md#item-220) |
| E20 | Ligar a constante do preflight às colunas lidas pelas queries do Engine | registro canônico (158) | sim | [ler](fichas-23.md#item-221) |
| E21 | Guard do alvo de Materialized View não reconhece TO multilinha | registro canônico (158) | sim | [ler](fichas-23.md#item-222) |
| E22 | Reaplicação de DDL pode regredir temporariamente o MV de spark_events | registro canônico (158) | sim | [ler](fichas-23.md#item-223) |
| E23 | Explicitar alcance do verify_ddl.py além de nome e tipo | registro canônico (158) | sim | [ler](fichas-23.md#item-224) |
| E24 | Alinhar seleção de tentativa no Engine offline e SQL | registro canônico (158) | sim | [ler](fichas-23.md#item-225) |
| S13 | Interface MCP read-only de system graph (#107) | registro canônico (158) | sim | [ler](fichas-23.md#item-226) |
| S14 | Efeito das consultas legadas Serve/Memory (retry-safe, T26) | registro canônico (158) | sim | [ler](fichas-23.md#item-227) |
| S15 | F4.3 — narrar 'AQE fez X, sua config diz Y' a partir de job_conf | registro canônico (158) | sim | [ler](fichas-23.md#item-228) |
| S16 | Serve renderiza delta medido abaixo do piso ou sem piso | registro canônico (158) | sim | [ler](fichas-23.md#item-229) |
| S17 | Serve suggest_fix sem receita para TAIL_OUTLIER | registro canônico (158) | sim | [ler](fichas-23.md#item-230) |
| S18 | Compare entre versões do Engine e colapso de AQE_REPLAN | registro canônico (158) | sim | [ler](fichas-24.md#item-231) |
| S19 | list_runs.worst_p99_ms mistura tentativas de stage superadas | registro canônico (158) | sim | [ler](fichas-24.md#item-232) |
| S20 | Serve classifica falhas do ClickHouse e recupera probes de metadata | registro canônico (158) | sim | [ler](fichas-24.md#item-233) |
| S21 | Serve retém veredito e magnitude com piso inválido | registro canônico (158) | sim | [ler](fichas-24.md#item-234) |
| S22 | API HTTP rejeita noise_floor_pct negativo ou não finito | registro canônico (158) | sim | [ler](fichas-24.md#item-235) |
| S23 | Guard estático de paridade da projeção fix_verifications Front×Serve | registro canônico (158) | sim | [ler](fichas-24.md#item-236) |
| S24 | Reforçar a paridade dos oito tools com argumentos idênticos | registro canônico (158) | sim | [ler](fichas-24.md#item-237) |
| X01 | Ratificar fronteira HTTP/BFF e sequência (#122) | registro canônico (158) | sim | [ler](fichas-24.md#item-238) |
| X02 | Contrato de piso e atribuição (#117) | registro canônico (158) | sim | [ler](fichas-24.md#item-239) |
| X03 | Concluir ADR de correlação de origem | registro canônico (158) | sim | [ler](fichas-24.md#item-240) |
| X04 | SECURITY.md e canal privado (#33) | registro canônico (158) | sim | [ler](fichas-25.md#item-241) |
| X05 | Modo offline/on-prem seguro (#42) | registro canônico (158) | sim | [ler](fichas-25.md#item-242) |
| X07 | System/contract graph (#106) | registro canônico (158) | sim | [ler](fichas-25.md#item-243) |
| X08 | CI Integration — análise APEX em PR (#21) | registro canônico (158) | sim | [ler](fichas-25.md#item-244) |
| X09 | Registro canônico de oportunidades | registro canônico (158) | sim | [ler](fichas-25.md#item-245) |
| X10 | Custódia da rodada 2026-09-21 e dos pacotes locais | registro canônico (158) | sim | [ler](fichas-25.md#item-246) |
| X11 | Candidato Ask V2 preservado localmente e em conflito com #129 | registro canônico (158) | sim | [ler](fichas-25.md#item-247) |
| X12 | Inventário de branches remotas além das cinco da #105 | registro canônico (158) | sim | [ler](fichas-25.md#item-248) |
| X13 | Reconciliar texto do CONTRACT.md e marcadores PROPOSED | registro canônico (158) | sim | [ler](fichas-25.md#item-249) |
| X14 | Colisão de numeração de ADR + índice/glossário (resto de T25) | registro canônico (158) | sim | [ler](fichas-25.md#item-250) |
| X15 | Juiz externo Claude com circuito aberto | registro canônico (158) | sim | [ler](fichas-26.md#item-251) |
| X16 | Vincular Task-Specs ao workspace correto | registro canônico (158) | sim | [ler](fichas-26.md#item-252) |
| X17 | Clones locais parcialmente 'dataless' no iCloud | registro canônico (158) | sim | [ler](fichas-26.md#item-253) |
| L01 | Linhagem v4 do workspace | registro canônico (158) | sim | [ler](fichas-26.md#item-254) |
| L02 | Linhagem recursiva #66–#93 | registro canônico (158) | sim | [ler](fichas-26.md#item-255) |
| L04 | Reconciliação documental da linhagem | registro canônico (158) | sim | [ler](fichas-26.md#item-256) |
| L05 | Inventário de proveniência de campos (A1) | registro canônico (158) | sim | [ler](fichas-26.md#item-257) |
| L06 | Auditoria de linhagem por chaves (A39) | registro canônico (158) | sim | [ler](fichas-26.md#item-258) |
| L07 | Linhagem Ask HTTP contra upstream (R0) | registro canônico (158) | sim | [ler](fichas-26.md#item-259) |
| L08 | Matriz de compatibilidade de telemetria | registro canônico (158) | sim | [ler](fichas-26.md#item-260) |
| L10 | Verify usar runtime medido (executor_run_time_ms) | registro canônico (158) | sim | [ler](fichas-27.md#item-261) |
| L11 | Contribuição e esforço como histórico | registro canônico (158) | sim | [ler](fichas-27.md#item-262) |
| L12 | Genealogia atual #66–#149 | registro canônico (158) | sim | [ler](fichas-27.md#item-263) |
| L13 | Atualizar a matriz de compatibilidade (Front, v0.6, #129) | registro canônico (158) | sim | [ler](fichas-27.md#item-264) |
| L14 | Lacunas históricas A1 ainda abertas | registro canônico (158) | sim | [ler](fichas-27.md#item-265) |
| L15 | Cenário declarativo e baselines negativos na main | registro canônico (158) | sim | [ler](fichas-27.md#item-266) |
| DD01 | DOUBLE-DIAMOND-EXECUTION-STANDARD.md | registro canônico (158) | sim | [ler](fichas-27.md#item-267) |
| DD02 | C38 piloto limpo | registro canônico (158) | sim | [ler](fichas-27.md#item-268) |
| DD03 | C49 agente Debug Diamond | registro canônico (158) | sim | [ler](fichas-27.md#item-269) |
| DD04 | Skill apex-debug-diamond | registro canônico (158) | sim | [ler](fichas-27.md#item-270) |
| DD05 | Roteamento, debugger e schema de evidência | registro canônico (158) | sim | [ler](fichas-28.md#item-271) |
| DD06 | Parametrizar o escopo autorizado da skill | registro canônico (158) | sim | [ler](fichas-28.md#item-272) |
| DD07 | Rota de identidade de ambiente (porta/perfil Colima/daemon) | registro canônico (158) | sim | [ler](fichas-28.md#item-273) |
| DD08 | Checar TTL/ts antes da rota 'materialized-view-loss' | registro canônico (158) | sim | [ler](fichas-28.md#item-274) |
| DD09 | Rotas de schema atrasado e de lanes consumidoras | registro canônico (158) | sim | [ler](fichas-28.md#item-275) |
| DD10 | Schema de evidência e versionamento da skill | registro canônico (158) | sim | [ler](fichas-28.md#item-276) |
| T-20260923-console-findings-transitions-projection | T-20260923-console-findings-transitions-projection.md | Task-Spec do repositório | não | [ler](fichas-28.md#item-277) |
| T-20260923-console-http-deployment-wiring | T-20260923-console-http-deployment-wiring.md | Task-Spec do repositório | não | [ler](fichas-28.md#item-278) |
| T-20260923-navbar-source-badge | T-20260923-navbar-source-badge.md | Task-Spec do repositório | não | [ler](fichas-28.md#item-279) |
| T-20260923-run-rollup-unindexed-sentinel | T-20260923-run-rollup-unindexed-sentinel.md | Task-Spec do repositório | não | [ler](fichas-28.md#item-280) |
| T-20260923-screens-surface-query-failures | T-20260923-screens-surface-query-failures.md | Task-Spec do repositório | não | [ler](fichas-29.md#item-281) |
| T-20260929-console-parity-live-gate | T-20260929-console-parity-live-gate.md | Task-Spec do repositório | não | [ler](fichas-29.md#item-282) |
| T-20260929-wire-timestamp-format | T-20260929-wire-timestamp-format.md | Task-Spec do repositório | não | [ler](fichas-29.md#item-283) |
| T-20261006-console-e2e-reflection | T-20261006-console-e2e-reflection.md | Task-Spec do repositório | não | [ler](fichas-29.md#item-284) |
| T-20261006-dev-c3-driver-host | T-20261006-dev-c3-driver-host.md | Task-Spec do repositório | não | [ler](fichas-29.md#item-285) |
| T-20261006-six-lane-gate-full-detail | T-20261006-six-lane-gate-full-detail.md | Task-Spec do repositório | não | [ler](fichas-29.md#item-286) |
| T-20260819-auto-baseline | T-20260819-auto-baseline.md | Task-Spec do repositório | não | [ler](fichas-29.md#item-287) |
| T-20260819-discover-docs | T-20260819-discover-docs.md | Task-Spec do repositório | não | [ler](fichas-29.md#item-288) |
| T-20260819-list-runs-tool | T-20260819-list-runs-tool.md | Task-Spec do repositório | não | [ler](fichas-29.md#item-289) |
| T-20260819-run-summary-models | T-20260819-run-summary-models.md | Task-Spec do repositório | não | [ler](fichas-29.md#item-290) |
| T-20260819-runs-gates | T-20260819-runs-gates.md | Task-Spec do repositório | não | [ler](fichas-30.md#item-291) |
| T-20260819-runs-injection-hardening | T-20260819-runs-injection-hardening.md | Task-Spec do repositório | não | [ler](fichas-30.md#item-292) |
| T-20260819-runs-read-layer | T-20260819-runs-read-layer.md | Task-Spec do repositório | não | [ler](fichas-30.md#item-293) |
| T-20260819-runs-resource | T-20260819-runs-resource.md | Task-Spec do repositório | não | [ler](fichas-30.md#item-294) |
| T-20260819-serve-brief-five-tools | T-20260819-serve-brief-five-tools.md | Task-Spec do repositório | não | [ler](fichas-30.md#item-295) |
| T-20260819-tool-surface-five | T-20260819-tool-surface-five.md | Task-Spec do repositório | não | [ler](fichas-30.md#item-296) |
| T-20260820-coverage-freshness | T-20260820-coverage-freshness.md | Task-Spec do repositório | não | [ler](fichas-30.md#item-297) |
| T-20260820-critical-path | T-20260820-critical-path.md | Task-Spec do repositório | não | [ler](fichas-30.md#item-298) |
| T-20260820-detail-parameter | T-20260820-detail-parameter.md | Task-Spec do repositório | não | [ler](fichas-30.md#item-299) |
| T-20260820-explain-stage-tool | T-20260820-explain-stage-tool.md | Task-Spec do repositório | não | [ler](fichas-30.md#item-300) |
| T-20260820-l3-docs | T-20260820-l3-docs.md | Task-Spec do repositório | não | [ler](fichas-31.md#item-301) |
| T-20260820-l5-docs | T-20260820-l5-docs.md | Task-Spec do repositório | não | [ler](fichas-31.md#item-302) |
| T-20260820-l5-tool-surface | T-20260820-l5-tool-surface.md | Task-Spec do repositório | não | [ler](fichas-31.md#item-303) |
| T-20260820-l6-docs | T-20260820-l6-docs.md | Task-Spec do repositório | não | [ler](fichas-31.md#item-304) |
| T-20260820-l6-tool-surface | T-20260820-l6-tool-surface.md | Task-Spec do repositório | não | [ler](fichas-31.md#item-305) |
| T-20260820-noise-floor-honesty | T-20260820-noise-floor-honesty.md | Task-Spec do repositório | não | [ler](fichas-31.md#item-306) |
| T-20260820-plan-memory-read-layer | T-20260820-plan-memory-read-layer.md | Task-Spec do repositório | não | [ler](fichas-31.md#item-307) |
| T-20260820-recall-models | T-20260820-recall-models.md | Task-Spec do repositório | não | [ler](fichas-31.md#item-308) |
| T-20260820-recall-runs-tool | T-20260820-recall-runs-tool.md | Task-Spec do repositório | não | [ler](fichas-31.md#item-309) |
| T-20260820-suggest-fix-provenance | T-20260820-suggest-fix-provenance.md | Task-Spec do repositório | não | [ler](fichas-31.md#item-310) |
| T-20260820-tool-surface-six | T-20260820-tool-surface-six.md | Task-Spec do repositório | não | [ler](fichas-32.md#item-311) |
| T-20260820-verification-models | T-20260820-verification-models.md | Task-Spec do repositório | não | [ler](fichas-32.md#item-312) |
| T-20260820-verifications-read-layer | T-20260820-verifications-read-layer.md | Task-Spec do repositório | não | [ler](fichas-32.md#item-313) |
| T-20260820-verify-fix-tool | T-20260820-verify-fix-tool.md | Task-Spec do repositório | não | [ler](fichas-32.md#item-314) |
| T-20260918-execution-stage-attribution-offline | T-20260918-execution-stage-attribution-offline.md | Task-Spec do repositório | não | [ler](fichas-32.md#item-315) |
| T-20260918-pwsh-command-aware-coverage | T-20260918-pwsh-command-aware-coverage.md | Task-Spec do repositório | não | [ler](fichas-32.md#item-316) |
| T-20260918-tail-outlier-finding-contract | T-20260918-tail-outlier-finding-contract.md | Task-Spec do repositório | não | [ler](fichas-32.md#item-317) |
| T-20260918-tail-outlier-package-wiring-offline | T-20260918-tail-outlier-package-wiring-offline.md | Task-Spec do repositório | não | [ler](fichas-32.md#item-318) |
| T-20260918-tail-outlier-watcher-offline | T-20260918-tail-outlier-watcher-offline.md | Task-Spec do repositório | não | [ler](fichas-32.md#item-319) |
| T-20260919-execution-attribution-audit-hardening | T-20260919-execution-attribution-audit-hardening.md | Task-Spec do repositório | não | [ler](fichas-32.md#item-320) |
| T-20260919-execution-attribution-conflict-collision | T-20260919-execution-attribution-conflict-collision.md | Task-Spec do repositório | não | [ler](fichas-33.md#item-321) |
| T-20260919-execution-attribution-scope-collision | T-20260919-execution-attribution-scope-collision.md | Task-Spec do repositório | não | [ler](fichas-33.md#item-322) |
| T-20260919-pwsh-package-audit-hardening | T-20260919-pwsh-package-audit-hardening.md | Task-Spec do repositório | não | [ler](fichas-33.md#item-323) |
| T-20260919-tail-outlier-contract-audit-hardening | T-20260919-tail-outlier-contract-audit-hardening.md | Task-Spec do repositório | não | [ler](fichas-33.md#item-324) |
| T-20260919-tail-outlier-watcher-audit-hardening | T-20260919-tail-outlier-watcher-audit-hardening.md | Task-Spec do repositório | não | [ler](fichas-33.md#item-325) |
| T-20260919-tail-outlier-wiring-audit-hardening | T-20260919-tail-outlier-wiring-audit-hardening.md | Task-Spec do repositório | não | [ler](fichas-33.md#item-326) |
| T-20260920-api-diagnostic-routes | T-20260920-api-diagnostic-routes.md | Task-Spec do repositório | não | [ler](fichas-33.md#item-327) |
| T-20260920-api-openapi-auth | T-20260920-api-openapi-auth.md | Task-Spec do repositório | não | [ler](fichas-33.md#item-328) |
| T-20260920-api-resource-routes | T-20260920-api-resource-routes.md | Task-Spec do repositório | não | [ler](fichas-33.md#item-329) |
| T-20260920-api-skeleton | T-20260920-api-skeleton.md | Task-Spec do repositório | não | [ler](fichas-33.md#item-330) |
| T-20260920-console-http-repository | T-20260920-console-http-repository.md | Task-Spec do repositório | não | [ler](fichas-34.md#item-331) |
| T-20260920-readstore-console-queries | T-20260920-readstore-console-queries.md | Task-Spec do repositório | não | [ler](fichas-34.md#item-332) |
| T-20260921-console-same-origin-api | T-20260921-console-same-origin-api.md | Task-Spec do repositório | não | [ler](fichas-34.md#item-333) |
| T-20260921-pr129-review-fixes | T-20260921-pr129-review-fixes.md | Task-Spec do repositório | não | [ler](fichas-34.md#item-334) |
| W01 | Revisar/mergear workspace PR #4 | registro canônico (158) | sim | [ler](fichas-34.md#item-335) |
| W02 | Captura real com spill | registro canônico (158) | sim | [ler](fichas-34.md#item-336) |
| W03 | Baseline real sem spill | registro canônico (158) | sim | [ler](fichas-34.md#item-337) |
| W04 | Estender Oráculo para spill | registro canônico (158) | sim | [ler](fichas-34.md#item-338) |
| W05 | MinIO do Oráculo semanal | registro canônico (158) | sim | [ler](fichas-34.md#item-339) |
| W06 | Oito tasks reais em worker multi-core | registro canônico (158) | sim | [ler](fichas-34.md#item-340) |
| W07 | Critérios prototype→validated para os quatro cenários | registro canônico (158) | sim | [ler](fichas-35.md#item-341) |
| W08 | Cost Watcher | registro canônico (158) | sim | [ler](fichas-35.md#item-342) |
| W09 | Tiers 2–4 de LLM | registro canônico (158) | sim | [ler](fichas-35.md#item-343) |
| W10 | Manter roadmap histórico marcado | registro canônico (158) | sim | [ler](fichas-35.md#item-344) |
| W11 | Resíduos do backlog após PR #4 | registro canônico (158) | sim | [ler](fichas-35.md#item-345) |
| W12 | Ligar workspace issue #1 ao dataship PR #1 | registro canônico (158) | sim | [ler](fichas-35.md#item-346) |
| D01 | Validar E2E o volume compartilhado da PR #1 | registro canônico (158) | sim | [ler](fichas-35.md#item-347) |
| D02 | Refatorar loader Go por responsabilidade | registro canônico (158) | sim | [ler](fichas-35.md#item-348) |
| D03 | Adicionar spark_jobs | registro canônico (158) | sim | [ler](fichas-35.md#item-349) |
| D04 | Adicionar spark_sql_execution_jobs | registro canônico (158) | sim | [ler](fichas-35.md#item-350) |
| D05 | Normalizar updates AQE | registro canônico (158) | sim | [ler](fichas-36.md#item-351) |
| D06 | Adicionar spark_applications | registro canônico (158) | sim | [ler](fichas-36.md#item-352) |
| D07 | Extrair nós do plano | registro canônico (158) | sim | [ler](fichas-36.md#item-353) |
| D08 | Normalizar métricas de executor | registro canônico (158) | sim | [ler](fichas-36.md#item-354) |
| D09 | Testes do loader com fixtures | registro canônico (158) | sim | [ler](fichas-36.md#item-355) |
| D15 | Reproduzir dependências do módulo Go do loader | registro canônico (158) | sim | [ler](fichas-36.md#item-356) |
| D10 | Catálogo de workloads | registro canônico (158) | sim | [ler](fichas-36.md#item-357) |
| D11 | Metadados de experimento | registro canônico (158) | sim | [ler](fichas-36.md#item-358) |
| D12 | Query pack operacional | registro canônico (158) | sim | [ler](fichas-36.md#item-359) |
| D13 | Equivalência Spark Connect | registro canônico (158) | sim | [ler](fichas-36.md#item-360) |
| D14 | Branches experimentais do upstream (listener/observer) | registro canônico (158) | sim | [ler](fichas-37.md#item-361) |
| PROP-X13-CONTRACT-RECONCILIATION | [Docs][Contract] Reconciliar texto do CONTRACT.md e marcadores PROPOSED de schema SQL (DEC-14) | minuta local 2026-10-11 | não | [ler](fichas-37.md#item-362) |
| PROP-D05-AQE-UPDATES | [Feature][Dataship] Normalização de eventos adaptativos de execução AQE (D05) | minuta local 2026-10-11 | não | [ler](fichas-37.md#item-363) |
| PROP-D06-SPARK-APPLICATIONS | [Feature][Dataship] Tabela de metadados de ciclo de vida spark_applications (D06) | minuta local 2026-10-11 | não | [ler](fichas-37.md#item-364) |
| PROP-D07-PLAN-NODES-EXTRACTION | [Study][Dataship] Estudo de viabilidade da extração de nós de plano físico Spark (D07) | minuta local 2026-10-11 | não | [ler](fichas-37.md#item-365) |
| PROP-D08-EXECUTOR-METRICS-NORMALIZATION | [Study][Dataship] Avaliação de normalização de métricas de executores Spark (D08) | minuta local 2026-10-11 | não | [ler](fichas-37.md#item-366) |
| PROP-D10-WORKLOAD-CATALOG | [Feature][Dataship] Especificação de convenções e catálogo de workloads (D10) | minuta local 2026-10-11 | não | [ler](fichas-37.md#item-367) |
| PROP-D11-EXPERIMENT-METADATA | [Docs][Dataship] Padronização de metadados para rastreabilidade de experimentos (D11) | minuta local 2026-10-11 | não | [ler](fichas-37.md#item-368) |
| PROP-D12-OPERATIONAL-QUERY-PACK | [Docs][Dataship] Pacote de consultas canônicas para o ClickHouse (D12) | minuta local 2026-10-11 | não | [ler](fichas-37.md#item-369) |
| PROP-D13-SPARK-CONNECT-EQUIVALENCE | [Study][Dataship] Estudo de paridade de telemetria com Spark Connect (D13) | minuta local 2026-10-11 | não | [ler](fichas-37.md#item-370) |
| PROP-D14-UPSTREAM-BRANCHES-EVALUATION | [Study][Dataship] Avaliação de branches experimentais do repositório upstream (D14) | minuta local 2026-10-11 | não | [ler](fichas-38.md#item-371) |
| P-TAIL | [Feature][Front/Verify/Serve] Tratar TAIL_OUTLIER nos consumidores após #127 | minuta local 2026-10-11 | não | [ler](fichas-38.md#item-372) |
| P-GATE | [CONDICIONAL][Tooling][Pod 2/Engine] Higiene do gate tail-outlier e harness R9D pós-#127 | minuta local 2026-10-11 | não | [ler](fichas-38.md#item-373) |
| P-E18 | [Study][Pod 2/Engine] Piso absoluto de duração no watcher tail-outlier | minuta local 2026-10-11 | não | [ler](fichas-38.md#item-374) |
| P-DEC23 | [Decision][Pod 2/Pod 3] Seletor comum de tentativa de stage (DEC-23) e população legada | minuta local 2026-10-11 | não | [ler](fichas-38.md#item-375) |
| P-DEC25 | [Decision][Pod 2/Infra] Reaplicação do DDL e escopo do verify_ddl (DEC-25) | minuta local 2026-10-11 | não | [ler](fichas-38.md#item-376) |
| P-DEC08 | [Decision][Pod 3/Serve] Exposição de /docs e credencial HTTP (DEC-08) | minuta local 2026-10-11 | não | [ler](fichas-38.md#item-377) |
| P-DEC06 | [Decision][Pod 1/Verify] Escritor de fix_verifications e dono (DEC-06) | minuta local 2026-10-11 | não | [ler](fichas-38.md#item-378) |
| P-R129 | [Test][Pod 3/Serve] Prova runtime da #129 no head atual | minuta local 2026-10-11 | não | [ler](fichas-38.md#item-379) |
| P-S01 | [Bug][Pod 3/Serve] task_time_ms=0 para run sem run_outcomes | minuta local 2026-10-11 | não | [ler](fichas-38.md#item-380) |
| P-E04 | [Audit][Pod 2/Pod 3] Literais 'apex.' restantes após #129 e #131 | minuta local 2026-10-11 | não | [ler](fichas-39.md#item-381) |
| P-E08 | [Bug][Pod 2/Package] Preservar dev/.env antes de sobrescrever | minuta local 2026-10-11 | não | [ler](fichas-39.md#item-382) |
| P-E09 | [Decision][Pod 2/Package] Modelo de identidade de checkout, daemon e Compose (DEC-10) | minuta local 2026-10-11 | não | [ler](fichas-39.md#item-383) |
| P-E13 | [Study][Pod 2/Infra] Rotação local de credencial ClickHouse | minuta local 2026-10-11 | não | [ler](fichas-39.md#item-384) |
| P-S15 | [Feature][Pod 3/Serve] F4.3: narrar AQE a partir de job_conf | minuta local 2026-10-11 | não | [ler](fichas-39.md#item-385) |
| PROP-L09-HARN-BINDING | [Feature][Pod 2/Harness] Repassar APEX_OTLP_ENDPOINT no alvo run-pathology | minuta local 2026-10-11 | não | [ler](fichas-39.md#item-386) |
| PROP-L10-VERIFY-RUNTIME | [Question][Pod 1/Verify] Verify deve usar executor_run_time_ms medido com fallback estimado? | minuta local 2026-10-11 | não | [ler](fichas-39.md#item-387) |
| PROP-L13-MATRIX-UPDATE | [Docs][Cross-lane] Atualizar matriz de compatibilidade para topologia atual (Front, apex-api) | minuta local 2026-10-11 | não | [ler](fichas-39.md#item-388) |
| PROP-L14-PROVENANCE-GAPS | [Question][Cross-lane] Lacunas de proveniência A1 restantes (status, ambiente, decisões Memory) ainda existem? | minuta local 2026-10-11 | não | [ler](fichas-39.md#item-389) |
| PROP-DD06-SKILL-SCOPE | [Feature][Método] Parametrizar escopo autorizado da skill apex-debug-diamond | minuta local 2026-10-11 | não | [ler](fichas-39.md#item-390) |
| PROP-DD07-ENV-IDENTITY | [Feature][Método] Rota de identidade de ambiente e checagem de dono de porta | minuta local 2026-10-11 | não | [ler](fichas-40.md#item-391) |
| PROP-DD09-ROUTES | [Feature][Método] Rotas para schema atrasado (Code 47) e lanes consumidoras | minuta local 2026-10-11 | não | [ler](fichas-40.md#item-392) |
| PROP-DD10-EVIDENCE-SCHEMA | [Feature][Método] Versionar skill e enriquecer schema de evidência | minuta local 2026-10-11 | não | [ler](fichas-40.md#item-393) |
| #5 | [ADR-001] Onde o Apex roda? | GitHub issue | não | [ler](fichas-40.md#item-394) |
| #6 | [ADR-002] Quando o classificador (Tier 2) dispara? | GitHub issue | não | [ler](fichas-40.md#item-395) |
| #7 | [ADR-003] Onde mora o estado histórico do Apex? | GitHub issue | não | [ler](fichas-40.md#item-396) |
| #8 | [ADR-004] Linguagem dos componentes | GitHub issue | não | [ler](fichas-40.md#item-397) |
| #9 | [DATA GEN] Define the data generator specification for Apex | GitHub issue | não | [ler](fichas-40.md#item-398) |
| #10 | [LAB PLAT] build Apex Lab Platform v0 | GitHub issue | não | [ler](fichas-40.md#item-399) |
| #11 | teste | GitHub issue | não | [ler](fichas-40.md#item-400) |
| #12 | [TEST] SIDYMAR | GitHub issue | não | [ler](fichas-41.md#item-401) |
| #15 | [EPIC] Apex — Peak Performance for Spark & Databricks | GitHub issue | não | [ler](fichas-41.md#item-402) |
| #16 | [FEATURE] Spark History Parser | GitHub issue | não | [ler](fichas-41.md#item-403) |
| #17 | [FEATURE] Watcher / Classifier / Judger Pipeline | GitHub issue | não | [ler](fichas-41.md#item-404) |
| #18 | [FEATURE] OTel Collector Stage 02 (Go) | GitHub issue | não | [ler](fichas-41.md#item-405) |
| #19 | [FEATURE] Local Bootstrap Platform (dataship-spark-plat-v0) | GitHub issue | não | [ler](fichas-41.md#item-406) |
| #20 | [FEATURE] Performance Recommendation Engine | GitHub issue | não | [ler](fichas-41.md#item-407) |
| #22 | [ADR-001] Go as language for OTel Collector | GitHub issue | não | [ler](fichas-41.md#item-408) |
| #23 | [ADR-002] Shadow repo governance — dataship-spark-plat-v0 | GitHub issue | não | [ler](fichas-41.md#item-409) |
| #24 | [ADR-003] Intentional deprioritization strategy (bootstrap-before-divergence) | GitHub issue | não | [ler](fichas-41.md#item-410) |
| #25 | [CA] Decide shadow repo governance — dataship-spark-plat-v0 | GitHub issue | não | [ler](fichas-42.md#item-411) |
| #26 | [CA] Validate Gabriel's 'deprioritization' pivot before Tuesday sync | GitHub issue | não | [ler](fichas-42.md#item-412) |
| #27 | [CA] Coordinate dual tech leads — Gabriel + Guilherme on independent stacks | GitHub issue | não | [ler](fichas-42.md#item-413) |
| #28 | [BLOCKER] GitHub repo access for Crew A members | GitHub issue | não | [ler](fichas-42.md#item-414) |
| #29 | [TASK] Validar slice skew_on_join_30x v4 corrigido com a Crew A | GitHub issue | não | [ler](fichas-42.md#item-415) |
| #30 | [TASK] Alinhar divisao dos pods e responsabilidades da Crew A | GitHub issue | não | [ler](fichas-42.md#item-416) |
| #31 | [CA] Liberar acesso Write ao Project Crew A — Apex | GitHub issue | não | [ler](fichas-42.md#item-417) |
| #32 | [TASK] Validar contrato validation_criteria dos scenarios Apex | GitHub issue | não | [ler](fichas-42.md#item-418) |
| #34 | [COMMANDER] Consolidar escopo Apex V0.1 da reuniao 2026-06-30 | GitHub issue | não | [ler](fichas-42.md#item-419) |
| #35 | [TASK] Construir Spark Env reproduzivel para Apex V0.1 | GitHub issue | não | [ler](fichas-42.md#item-420) |
| #36 | [TASK] Implementar SparkListener MVP para telemetria Apex | GitHub issue | não | [ler](fichas-43.md#item-421) |
| #37 | [TASK] Integrar SparkListener ao ClickStack MVP | GitHub issue | não | [ler](fichas-43.md#item-422) |
| #38 | [TASK] Criar diagnostico CrewAI/MCP por job_id | GitHub issue | não | [ler](fichas-43.md#item-423) |
| #39 | [TASK] Coletar percepcao DataFlint de cada membro da Crew A | GitHub issue | não | [ler](fichas-43.md#item-424) |
| #40 | [TASK] Inventariar branches e evidencias existentes para V0.1 | GitHub issue | não | [ler](fichas-43.md#item-425) |
| #41 | [TASK] Definir contratos agenticos: memoria, RAG, skills, harness e contexto | GitHub issue | não | [ler](fichas-43.md#item-426) |
| #43 | [SPIKE] Desenhar UI local de DAG, replay e simulacao para pos-V0.1 | GitHub issue | não | [ler](fichas-43.md#item-427) |
| #55 | tracking(v1): decisões finais e evoluções após ENGINE/SERVE | GitHub issue | não | [ler](fichas-43.md#item-428) |
| #56 | tracking(e2e): decidir incorporação de 093c677 na branch Augusto | GitHub issue | não | [ler](fichas-43.md#item-429) |
| #58 | JAR: correct lifecycle + measured telemetry | GitHub issue | não | [ler](fichas-43.md#item-430) |
| #59 | JDK gate for the Spark 4.x cells | GitHub issue | não | [ler](fichas-44.md#item-431) |
| #60 | Typed column for executor runtime | GitHub issue | não | [ler](fichas-44.md#item-432) |
| #61 | Engine consuming the typed runtime column | GitHub issue | não | [ler](fichas-44.md#item-433) |
| #62 | Local operational package (bootstrap/doctor/smoke) | GitHub issue | não | [ler](fichas-44.md#item-434) |
| #63 | Data integrity in the Collector under retry | GitHub issue | não | [ler](fichas-44.md#item-435) |
| #64 | Clean Docker environment guard-rail | GitHub issue | não | [ler](fichas-44.md#item-436) |
| #65 | Design decision: AQE re-plan detection logic | GitHub issue | não | [ler](fichas-44.md#item-437) |
| #71 | mv_spark_events does not reliably propagate inserts (pre-existing, independent of #66-#68/#61) | GitHub issue | não | [ler](fichas-44.md#item-438) |
| #72 | MV creation succeeds against a missing target table, then rejects every insert (bootstrap ordering risk) | GitHub issue | não | [ler](fichas-44.md#item-439) |
| #73 | Real-pathology test tooling for dev/ + design docs for merged telemetry fields | GitHub issue | não | [ler](fichas-44.md#item-440) |
| #78 | Proposal: canonical end-to-end traceability ledger across APEX lanes | GitHub issue | não | [ler](fichas-45.md#item-441) |
| #90 | Design question: should skew_ratio route through the retry-safe fields? | GitHub issue | não | [ler](fichas-45.md#item-442) |
| #95 | Engine fails with a raw ClickHouse error when the store's schema is behind | GitHub issue | não | [ler](fichas-45.md#item-443) |
| #102 | Pod 1: consolidar camada de dados e definir fronteira browser–serviços | GitHub issue | não | [ler](fichas-45.md#item-444) |
| #103 | [Cross-lane] Add an executable telemetry compatibility matrix | GitHub issue | não | [ler](fichas-45.md#item-445) |
| #104 | [DevEx] Detect hidden editable .pth files on macOS/Python 3.14 | GitHub issue | não | [ler](fichas-45.md#item-446) |
| #116 | [Front] /verify: estados por fonte e apresentação fiel da proposta e das evidências | GitHub issue | não | [ler](fichas-45.md#item-447) |
| PR#13 | chore: permission check test | GitHub PR | não | [ler](fichas-45.md#item-448) |
| PR#14 | Add additional spacing in README.md | GitHub PR | não | [ler](fichas-45.md#item-449) |
| PR#44 | feat(serve): adicionar MCP somente leitura | GitHub PR | não | [ler](fichas-45.md#item-450) |
| PR#45 | docs(v1): definir arquitetura por raias e plano de PRs | GitHub PR | não | [ler](fichas-46.md#item-451) |
| PR#46 | feat(engine): adicionar diagnóstico determinístico | GitHub PR | não | [ler](fichas-46.md#item-452) |
| PR#47 | feat(dev): preparar ambiente Spark 4.1.2 | GitHub PR | não | [ler](fichas-46.md#item-453) |
| PR#48 | feat(infra): adicionar schema OTLP logs | GitHub PR | não | [ler](fichas-46.md#item-454) |
| PR#49 | feat(collect): adicionar contrato OTLP v0.2 | GitHub PR | não | [ler](fichas-46.md#item-455) |
| PR#50 | feat(jar): adicionar plugin Spark 4.1.2 | GitHub PR | não | [ler](fichas-46.md#item-456) |
| PR#51 | feat(e2e): validar caminho canonico seis raias | GitHub PR | não | [ler](fichas-46.md#item-457) |
| PR#52 | feat(engine): add gated CrewAI judge adapter | GitHub PR | não | [ler](fichas-46.md#item-458) |
| PR#53 | feat(serve): add KB search and safe fix proposals | GitHub PR | não | [ler](fichas-46.md#item-459) |
| PR#54 | docs(c9): record Engine and Serve delivery status | GitHub PR | não | [ler](fichas-46.md#item-460) |
| PR#57 | Apex v0.1 — eight lanes, one frozen contract, and a system that refuses to guess | GitHub PR | não | [ler](fichas-47.md#item-461) |
| PR#66 | jar: correct stage listener lifecycle, add measured executor runtime | GitHub PR | não | [ler](fichas-47.md#item-462) |
| PR#67 | infra: switch Collector to synchronous inserts, fix retry duplication | GitHub PR | não | [ler](fichas-47.md#item-463) |
| PR#68 | infra: typed columns for the telemetry fields the JAR now emits | GitHub PR | não | [ler](fichas-47.md#item-464) |
| PR#69 | scripts: refuse to bootstrap over leftover APEX Docker resources | GitHub PR | não | [ler](fichas-47.md#item-465) |
| PR#70 | engine: read the typed executor runtime column, Map as fallback | GitHub PR | não | [ler](fichas-47.md#item-466) |
| PR#74 | dev: real-pathology probe tooling and design-doc rationale for merged telemetry fields | GitHub PR | não | [ler](fichas-47.md#item-467) |
| PR#75 | infra: guard apply-ddl against MV/target bootstrap ordering | GitHub PR | não | [ler](fichas-47.md#item-468) |
| PR#76 | scripts: local operational package (bootstrap/doctor/smoke/e2e/status/down) | GitHub PR | não | [ler](fichas-47.md#item-469) |
| PR#77 | docs: fix Quick Start README (DDL order, .env step, sbt prereq) | GitHub PR | não | [ler](fichas-47.md#item-470) |
| PR#79 | serve/L1 Connect: 23 signed Task-Specs, first two units accepted | GitHub PR | não | [ler](fichas-48.md#item-471) |
| PR#80 | chore: bump contract to v0.5 with additive task analysis fields | GitHub PR | não | [ler](fichas-48.md#item-472) |
| PR#81 | dev: cover the scripts #74 shipped without tests — and make the lane actually run | GitHub PR | não | [ler](fichas-48.md#item-473) |
| PR#82 | fix: spark_events DDL cannot create the table — no fresh deployment can start | GitHub PR | não | [ler](fichas-48.md#item-474) |
| PR#83 | serve/L2 Discover: list_runs, apex://runs, and a self-selecting comparison baseline | GitHub PR | não | [ler](fichas-48.md#item-475) |
| PR#84 | harness: verify optional ClickHouse endpoint identity | GitHub PR | não | [ler](fichas-48.md#item-476) |
| PR#85 | docs: define pre-submit provenance for E2E runs | GitHub PR | não | [ler](fichas-48.md#item-477) |
| PR#86 | serve/L6 — cross-run memory: recall_similar_runs over the memory lane | GitHub PR | não | [ler](fichas-48.md#item-478) |
| PR#87 | serve/L5: expose the verify lane over MCP as verify_fix | GitHub PR | não | [ler](fichas-48.md#item-479) |
| PR#88 | serve/L3: diagnosis readability — detail levels, coverage, explain_stage, share of tail | GitHub PR | não | [ler](fichas-48.md#item-480) |
| PR#89 | engine: retry-safe telemetry — reachability + the retry_pressure watcher | GitHub PR | não | [ler](fichas-49.md#item-481) |
| PR#91 | jar: prove listener sink failure never breaks the job (#36) | GitHub PR | não | [ler](fichas-49.md#item-482) |
| PR#92 | dev: cover scripts/apex.ps1 with dry-run and secrets contract tests | GitHub PR | não | [ler](fichas-49.md#item-483) |
| PR#93 | docs: propose AQE re-plan detection decision | GitHub PR | não | [ler](fichas-49.md#item-484) |
| PR#94 | engine: fail in CI when the SQL reads a column no DDL declares | GitHub PR | não | [ler](fichas-49.md#item-485) |
| PR#96 | feat(jar): preserve Spark SQL execution_id on apex.stage spans | GitHub PR | não | [ler](fichas-49.md#item-486) |
| PR#97 | docs(ui): define read-only Compare, Memory, and Verify contracts | GitHub PR | não | [ler](fichas-49.md#item-487) |
| PR#98 | jar: combine AQE join alignment with skew partition counts | GitHub PR | não | [ler](fichas-49.md#item-488) |
| PR#99 | engine: make skew_ratio retry-safe | GitHub PR | não | [ler](fichas-49.md#item-489) |
| PR#100 | feat(front): Apex Console — the seven screens as a runnable Vite + React app | GitHub PR | não | [ler](fichas-49.md#item-490) |
| PR#101 | chore(serve): make the three legs mergeable — one contracted tool list, untracked generated state | GitHub PR | não | [ler](fichas-50.md#item-491) |
| PR#110 | devex: detect hidden editable .pth files on macOS | GitHub PR | não | [ler](fichas-50.md#item-492) |
| PR#111 | docs: add executable telemetry compatibility matrix | GitHub PR | não | [ler](fichas-50.md#item-493) |
| PR#118 | fix(front): isolate /verify source states and async selections (I1) | GitHub PR | não | [ler](fichas-50.md#item-494) |
| PR#119 | fix(front): present /verify proposals and evidence faithfully (I2) | GitHub PR | não | [ler](fichas-50.md#item-495) |
| PR#120 | fix(front): expose original proposal as named region | GitHub PR | não | [ler](fichas-50.md#item-496) |
| PR#121 | fix(tests): bump telemetry matrix to contract v0.6 | GitHub PR | não | [ler](fichas-50.md#item-497) |
| PR#126 | feat(engine): add offline execution-stage attribution | GitHub PR | não | [ler](fichas-50.md#item-498) |
| PR#127 | feat: add deterministic tail-outlier runtime gate | GitHub PR | não | [ler](fichas-50.md#item-499) |
| PR#128 | test(package): make PowerShell coverage command-aware | GitHub PR | não | [ler](fichas-50.md#item-500) |
| PR#129 | feat(serve): apex-api — one HTTP layer between ClickHouse and its consumers | GitHub PR | não | [ler](fichas-51.md#item-501) |
| PR#131 | engine: fail fast on connect when spark_events schema is behind | GitHub PR | não | [ler](fichas-51.md#item-502) |
| PR#132 | docs: reconcile current contract and Serve state | GitHub PR | não | [ler](fichas-51.md#item-503) |
| PR#133 | docs: propose source correlation privacy boundary | GitHub PR | não | [ler](fichas-51.md#item-504) |
| PR#134 | docs: align README with current contract | GitHub PR | não | [ler](fichas-51.md#item-505) |
| PR#135 | fix(serve): withhold unresolved replay deltas | GitHub PR | não | [ler](fichas-51.md#item-506) |
| PR#136 | fix(front): keep mechanism and runtime verdicts independent | GitHub PR | não | [ler](fichas-51.md#item-507) |
| PR#137 | fix(front): recognize retry pressure findings | GitHub PR | não | [ler](fichas-51.md#item-508) |
| PR#138 | ci(front): reject warnings and empty suites | GitHub PR | não | [ler](fichas-51.md#item-509) |
| PR#139 | test(engine): harden SQL to DDL column guard | GitHub PR | não | [ler](fichas-51.md#item-510) |
| PR#140 | fix(serve): classify ClickHouse failures and retry failed metadata probes | GitHub PR | não | [ler](fichas-52.md#item-511) |
| PR#141 | docs: add a discoverable index of canonical architecture decisions | GitHub PR | não | [ler](fichas-52.md#item-512) |
| PR#142 | fix(verify): use successful-task duration samples for stage analysis | GitHub PR | não | [ler](fichas-52.md#item-513) |
| PR#143 | fix(api): reject invalid HTTP noise floors | GitHub PR | não | [ler](fichas-52.md#item-514) |
| PR#144 | fix(serve): withhold verdicts from invalid noise floors | GitHub PR | não | [ler](fichas-52.md#item-515) |
| PR#145 | fix(verify): reject invalid noise floors for certification | GitHub PR | não | [ler](fichas-52.md#item-516) |
| PR#146 | test(serve): pin fix_verifications projection parity with the front | GitHub PR | não | [ler](fichas-52.md#item-517) |
| PR#147 | fix(infra): check multiline materialized-view targets | GitHub PR | não | [ler](fichas-52.md#item-518) |
| PR#148 | docs(ci): clarify that live end-to-end paths are not gated | GitHub PR | não | [ler](fichas-52.md#item-519) |
| PR#149 | fix(ci): quote generated Collector secret argument | GitHub PR | não | [ler](fichas-52.md#item-520) |
| PR#150 | test(serve): guard sanitized store errors across transports | GitHub PR | não | [ler](fichas-53.md#item-521) |
| PR#151 | fix(front): render API error detail only when textual | GitHub PR | não | [ler](fichas-53.md#item-522) |
| PR#152 | docs(artifacts): add Apex current-state deck (main @ a289e53) | GitHub PR | não | [ler](fichas-53.md#item-523) |
| PR#153 | fix(serve,front): the console reads the same rows through either door | GitHub PR | não | [ler](fichas-53.md#item-524) |
| PR#160 | ci: lean default CI (cheap PR check, heavy jobs manual/weekly) | GitHub PR | não | [ler](fichas-53.md#item-525) |
