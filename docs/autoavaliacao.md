# Autoavaliação F5 — Codex Round 2

Branch: `codex-round2`

Data: 2026-07-19

Base de avaliação: `pacote-comum/apex-v1-spec-reproducivel.md`, `PLANO.md`,
`ISSUES.md` e evidências locais `evidence/`.

## Scorecard C1-C6

Escala: 0 a 5.

| Critério | Nota | Evidência por célula |
| --- | ---: | --- |
| C1 Arquitetura V1 (L1-L9) | 4/5 | `PLANO.md` classifica L2/L3/L6/L7 como cumpridas localmente e L1/L5/L9 como parciais avançadas: há compose autônomo Spark 4.1.2, listener JVM promovido para caminho oficial dos jobs, G3/G5 reexecutados em Spark 4.1.2, MCP validado em Claude Code GUI real, `apply_fix` local e `crew_judge_diagnose` read-only com provider Crew.ai opcional. Não é 5/5 porque execução com LLM externo real ainda não foi observada. |
| C2 Cobertura de detecção | 5/5 | G2 passou nos 6 cenários oficiais de `pacote-comum/scenarios/`: baseline sem finding (`no_skew_baseline.yaml`) e 5 detectores com severidade esperada: skew high, GC critical, shuffle spill critical, OOM critical, cartesian product critical. Evidências: `evidence/g1-baseline.log`, `evidence/g2-cenarios.log`, `evidence/generated/official-scenarios/*.ndjson`, CODEX-009 a CODEX-014. |
| C3 Confiabilidade | 5/5 | Baseline negativo oficial ficou limpo em G1 (`evidence/g1-baseline.log`, CODEX-009). Findings passam por `EvidenceValidator` (`apex/commander/evidence_validator.py`) e G4/G5 validaram finding real com `accepted=true`. G5 corrigiu bug real no token de apply guardado (CODEX-021). Em F6, o listener JVM provou fail-safe com `spark.apex.listener.failMode=true` e job Spark terminando com exit 0 (`evidence/g9-listener-jvm-failsafe-spark-submit.log`). Em 15/07, o workflow remoto `Apex Scenario Gate` passou inteiro no campeonato em `6ba5238`, incluindo `gate` e `g6-oracle-drift` (`evidence/g6-remote-workflow-latest-summary.json`). |
| C4 Loop no IDE | 5/5 | O ciclo funcional detectar -> preview -> apply guardado -> verify -> rerun -> limpo foi provado em G5 contra Spark real e repetido na stack autônoma em `evidence/g5-autonomous-ciclo.log`. Em F6/F7, `apply_fix` foi validado via MCP stdio, por harness de cliente subprocesso em `evidence/g6-mcp-ide-subprocess-smoke.jsonl` e dentro do Claude Code GUI real em `evidence/g6-mcp-ide-gui-smoke-2026-07-18.log`: `tools/list`, `recommend_fix`, `preview_recommendation` e `apply_fix` com mutação guardada no `apply_root`. |
| C5 Qualidade de engenharia | 5/5 | A suíte final registrada em `evidence/ci-remote-gate-fix-tests.log` fechou com `163 passed, 2 skipped`; G0 registrou suíte ampla em `evidence/g0-testes.log`; G5 adicionou teste focado; F7 adicionou smoke MCP/Judge; o listener JVM registra `ApexSparkListenerSelfTest passed` e `BUILD SUCCESSFUL`; G3/G5 autônomos têm evidência crua própria. Em 18/07, o loop G3/G5 autônomo virou runner testado e workflow; em 19/07, o run remoto `29671461366` do GitHub Actions/self-hosted fechou verde com `loop_status=success`, before `app-20260719032011-0000`, after `app-20260719032439-0001`, finding_count `1 -> 0` e max_skew_ratio `29.4 -> 0.0`. O trabalho registrou issues formais CODEX-001 a CODEX-062 e não escondeu bugs/gaps encontrados. Os achados de proveniência continuam declarados, mas não impediram reprodutibilidade/testabilidade do pacote. |
| C6 Custo/latência | 5/5 | G4 mediu o caminho T1 determinístico completo contra event log real `app-20260712053414-0001` em 226.991 ms, sem LLM. Evidência: `evidence/g4-t1.log`, `tools/g4_t1_latency.py`, CODEX-017. O grep do caminho medido não encontrou referências a LLM/API. `crew_judge_diagnose` é read-only e opcional; Crew.ai externo só roda com `APEX_CREW_JUDGE_ENABLED=1`, evitando custo oculto. |

Nota total: 29/30.

Leitura curta: a engine está forte em prova empírica local, detecção, stack
autônoma, listener real fail-safe, ciclo fechado funcional, MCP GUI real, G6
remoto verde e F7 real-stack remoto verde. Ainda não deve ser vendida como V1 completa porque a execução
Crew.ai com LLM externo real ainda não foi observada.

## Honestidade De Proveniência

CODEX-001 registra que a branch já continha
`docs/architecture/llm-solution-validation-framework-2026-07-09.md`, um
scorecard comparativo da rodada 1, antes do reconhecimento desta rodada. Isso
significa que parte da moldura de comparação já estava presente e não pode ser
tratada como descoberta limpa desta rodada.

CODEX-007 registra fato ainda mais específico: o fix guardado (Gate 11) adotou
o conceito `apply_fix` da Cowork, lido no comparativo de 08/07 antes do Gate 11
ser definido. A cadeia de commits citada em `ISSUES.md` é `52b181b`, `64478f6`,
`086e3a0` e `8f4b802`. Portanto, o padrão de preview/apply guardado não deve ser
apresentado como invenção paralela independente da engine Codex.

Impacto na avaliação: isso pesa principalmente em C1, porque reduz a
originalidade arquitetural da solução. Não invalida a engenharia executada
depois: G4 e G5 foram medidos em logs reais novos, com app ids próprios, mas a
proveniência conceitual precisa acompanhar qualquer julgamento comparativo.

## Captain's Report Final — CREW_A_OPERATING_STANDARD

### Avançou

- F0 formalizou o estado real da branch sem reestruturação prematura: `PLANO.md`,
  `ISSUES.md`, `docs/autoavaliacao.md`, `MELHORIAS.md`, `evidence/`, `docs/adr/`
  e `docs/meetings/`.
- G0 alinhou fundação local: DDL canônico, compose com volumes nomeados e testes
  de contrato em `evidence/g0-testes.log`.
- G1/G2 rodaram os 6 cenários oficiais do pacote comum. O baseline ficou limpo e
  os 5 detectores bateram a severidade esperada.
- G3 validou dado real contra `spv0-*`: `app-20260712053414-0001`, 8 tasks reais,
  ratio 29.4x e oráculo verde em `evidence/g3-real.log`.
- G4 mediu T1 determinístico em 226.991 ms sem chamada LLM, com finding aceito
  pelo `EvidenceValidator`.
- G5 fechou o loop funcional real: preview aprovado, apply guardado, verify,
  rerun no Spark, captura S3A, diagnóstico pós-fix limpo. Antes: 1 finding high,
  shuffle read 1.157.481 bytes, ratio 29.4. Depois: 0 finding, shuffle read 0,
  ratio válido 0.

### Bloqueado

- A branch agora tem direção de plataforma mais alinhada: Spark 4.1.2 é o alvo
  oficial, o compose raiz/autônomo sobe com o listener JVM no caminho oficial,
  `build_spark_submit_rerun_command` inclui o JAR por padrão e G3/G5 foram
  reexecutados em Spark 4.1.2. Before: `app-20260718172202-0002`, finding high
  ratio 29.4. After final: `app-20260718175410-0004`, finding_count 0.
- SparkListener JVM real fail-safe foi carregado em Spark real via
  `spark-submit --jars`, emitiu NDJSON e não derrubou o job quando falhou
  internamente.
- Crew/Judge plugável agora existe como `crew_judge_diagnose`, com contrato
  anti-alucinação, provider determinístico, fallback `noop` e provider Crew.ai
  opcional. O smoke de ambiente confirmou `crewai_installed=true`; a tentativa
  com `APEX_CREW_JUDGE_ENABLED=1` retornou `llm_credentials_missing`, sem
  chamada externa ruidosa. A execução com LLM externo real ainda depende de
  credenciais aprovadas.
- O contrato local `apply_fix` foi adicionado em F6, com `apply_recommendation`
  preservado como compatibilidade. CODEX-019 foi fechado com evidência em
  `evidence/g6-apply-fix-mcp-smoke.log`.
- MCP stdio existe e o ciclo foi validado dentro do Claude Code GUI real com
  `tools/list`, `recommend_fix`, `preview_recommendation`, `apply_fix` e
  `compare_job_telemetry`.

### Precisa Do Commander

- O runner de regressão G3/G5 Spark 4.1.2 já foi criado, executado localmente
  com sucesso em `evidence/f7-autonomous-stack-loop-20260718-real-local-6.log`
  e executado remotamente no GitHub Actions/self-hosted em
  `evidence/f7-remote-real-stack-run-29671461366-loop.log`.
- Decidir se o runner self-hosted `apex-local-GUSTUS` deve permanecer ativo
  durante a avaliação ou ser removido após o julgamento.
- Decidir se o próximo fechamento deve priorizar execução Crew.ai com LLM
  externo configurado ou UI de produto navegável. A IDE GUI real já tem
  evidência no Claude Code.
- Validar se broadcast do lado `customers` é a correção canônica aceitável para
  o cenário `skew_on_join_30x`, ou se a próxima versão deve exigir salting para
  casos em que o lado pequeno não caiba em broadcast.
- Autorizar ou rejeitar a promoção dos rascunhos ADR para `docs/adr/ADR-*.md`.

### Honestidade

- A solução Codex não é V1 completa. Ela é uma esteira local muito boa de prova:
  detector, validação, latência, apply guardado e rerun real.
- A parte mais forte é empírica: logs reais, app ids novos, evidência crua e
  comparação antes/depois.
- A parte mais fraca agora é produto/agência: execução Crew.ai com LLM externo
  real e UI de produto navegável ainda faltam. A plataforma autônoma local, o listener real e o runner de regressão
  G3/G5 já têm evidência real local e remota; o runner self-hosted continua
  sendo dependência operacional para repetir o F7.
- A proveniência não é limpa: CODEX-001 e CODEX-007 precisam acompanhar a
  avaliação. O fix guardado foi adoção consciente de conceito visto na Cowork,
  depois implementado, testado e validado pela Codex.
