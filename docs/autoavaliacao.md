# Autoavaliação F5 — Codex Round 2

Branch: `codex-round2`

Data: 2026-07-12

Base de avaliação: `pacote-comum/apex-v1-spec-reproducivel.md`, `PLANO.md`,
`ISSUES.md` e evidências locais `evidence/`.

## Scorecard C1-C6

Escala: 0 a 5.

| Critério | Nota | Evidência por célula |
| --- | ---: | --- |
| C1 Arquitetura V1 (L1-L9) | 4/5 | `PLANO.md` classifica L2/L3 como cumpridas localmente e L1/L5/L6 como parciais: há compose autônomo paralelo que sobe e grava event log em S3A/MinIO, G3/G5 completos sem `plat-v0`, listener JVM carregado via `spark-submit --jars` com NDJSON/fail-safe, MCP subprocess estilo cliente IDE, `apply_fix` local e política Judge local. Não é 5/5 porque ainda faltam IDE GUI real e Crew.ai/LLM real. |
| C2 Cobertura de detecção | 5/5 | G2 passou nos 6 cenários oficiais de `pacote-comum/scenarios/`: baseline sem finding (`no_skew_baseline.yaml`) e 5 detectores com severidade esperada: skew high, GC critical, shuffle spill critical, OOM critical, cartesian product critical. Evidências: `evidence/g1-baseline.log`, `evidence/g2-cenarios.log`, `evidence/generated/official-scenarios/*.ndjson`, CODEX-009 a CODEX-014. |
| C3 Confiabilidade | 4/5 | Baseline negativo oficial ficou limpo em G1 (`evidence/g1-baseline.log`, CODEX-009). Findings passam por `EvidenceValidator` (`apex/commander/evidence_validator.py`) e G4/G5 validaram finding real com `accepted=true`. G5 corrigiu bug real no token de apply guardado (CODEX-021). Em F6, o listener JVM provou fail-safe com `spark.apex.listener.failMode=true` e job Spark terminando com exit 0 (`evidence/g9-listener-jvm-failsafe-spark-submit.log`). Não é 5/5 porque ainda faltam CI comum completo e oráculo agendado de drift (G6 não cumpre no `PLANO.md`). |
| C4 Loop no IDE | 4/5 | O ciclo funcional detectar -> preview -> apply guardado -> verify -> rerun -> limpo foi provado em G5 contra Spark real e repetido na stack autônoma em `evidence/g5-autonomous-ciclo.log`. Em F6/F7, `apply_fix` foi validado via MCP stdio e por um harness de cliente subprocesso estilo IDE em `evidence/g6-mcp-ide-subprocess-smoke.jsonl`, mantendo `apply_recommendation` como compatibilidade. Não é 5/5 porque ainda falta validação dentro de IDE GUI real. |
| C5 Qualidade de engenharia | 4/5 | Há 143+ testes acumulados pela branch: G0 registrou suíte ampla em `evidence/g0-testes.log`; G5 adicionou teste focado; F7 adicionou smoke MCP/Judge; o listener JVM registra `ApexSparkListenerSelfTest passed` e `BUILD SUCCESSFUL`; G3/G5 autônomos têm evidência crua própria. O trabalho registrou issues formais CODEX-001 a CODEX-028 e não escondeu bugs/gaps encontrados. Não é 5/5 por dois achados de proveniência (CODEX-001, CODEX-007) e por IDE GUI/Crew reais ainda pendentes. |
| C6 Custo/latência | 5/5 | G4 mediu o caminho T1 determinístico completo contra event log real `app-20260712053414-0001` em 226.991 ms, sem LLM. Evidência: `evidence/g4-t1.log`, `tools/g4_t1_latency.py`, CODEX-017. O grep do caminho medido não encontrou referências a LLM/API. A política de escalonamento para Crew.ai quando confiança < 0.6 segue como gap honesto, não custo oculto (CODEX-018). |

Nota total: 26/30.

Leitura curta: a engine está forte em prova empírica local, detecção e ciclo
fechado funcional. Ainda não deve ser vendida como V1 completa porque falta
plataforma própria reproduzível, listener real, Crew.ai e validação IDE/MCP
real.

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

- A branch agora cumpre L2 localmente como plataforma autônoma própria:
  `docker-compose.autonomous.yml` sobe, grava event log em S3A/MinIO e repetiu
  G3/G5 sem `plat-v0`. Ressalva: usa Spark 4.0.0 da imagem pública, diferente
  da stack histórica.
- SparkListener JVM real fail-safe foi carregado em Spark real via
  `spark-submit --jars`, emitiu NDJSON e não derrubou o job quando falhou
  internamente.
- Não há Crew.ai/Judge implementado. O escalonamento para LLM quando confiança
  < 0.6 é decisão de design registrada, não funcionalidade entregue.
- O contrato local `apply_fix` foi adicionado em F6, com `apply_recommendation`
  preservado como compatibilidade. CODEX-019 foi fechado com evidência em
  `evidence/g6-apply-fix-mcp-smoke.log`.
- MCP stdio existe e tem smoke subprocesso estilo cliente IDE, mas o ciclo não
  foi validado dentro de uma IDE GUI real.

### Precisa Do Commander

- Decidir se F6 deve priorizar V1 plataforma (`docker compose` próprio +
  SparkListener real + ClickHouse schema de produção) ou paridade de produto
  (`apply_fix` MCP/IDE primeiro).
- Decidir o papel oficial do `plat-v0`: evidência compartilhada temporária,
  submódulo/fork de referência, ou base a ser incorporada.
- Validar se broadcast do lado `customers` é a correção canônica aceitável para
  o cenário `skew_on_join_30x`, ou se a próxima versão deve exigir salting para
  casos em que o lado pequeno não caiba em broadcast.
- Autorizar ou rejeitar a promoção dos rascunhos ADR para `docs/adr/ADR-*.md`.

### Honestidade

- A solução Codex não é V1 completa. Ela é uma esteira local muito boa de prova:
  detector, validação, latência, apply guardado e rerun real.
- A parte mais forte é empírica: logs reais, app ids novos, evidência crua e
  comparação antes/depois.
- A parte mais fraca agora é produto/agência: Crew.ai real e IDE GUI real ainda
  faltam. A plataforma autônoma local e o listener real já têm evidência.
- A proveniência não é limpa: CODEX-001 e CODEX-007 precisam acompanhar a
  avaliação. O fix guardado foi adoção consciente de conceito visto na Cowork,
  depois implementado, testado e validado pela Codex.
