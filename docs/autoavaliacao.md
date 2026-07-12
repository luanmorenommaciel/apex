# Autoavaliação F5 — Codex Round 2

Branch: `codex-round2`

Data: 2026-07-12

Base de avaliação: `pacote-comum/apex-v1-spec-reproducivel.md`, `PLANO.md`,
`ISSUES.md` e evidências locais `evidence/`.

## Scorecard C1-C6

Escala: 0 a 5.

| Critério | Nota | Evidência por célula |
| --- | ---: | --- |
| C1 Arquitetura V1 (L1-L9) | 2/5 | `PLANO.md` classifica L1, L3, L4, L6, L7 e L9 como parciais; L2 e L5 como não cumpridas; L8 como cumprida. Há componentes úteis (`apex/commander/diagnostic_mvp.py`, `apex/commander/evidence_validator.py`, `apex/commander/mcp_stdio_server.py`, `apex/commander/apply_verify.py`, adapters ClickHouse), mas ainda faltam Spark Envy Docker reproduzível da branch, SparkListener JVM real fail-safe e Crew.ai. A nota também é reduzida por proveniência: CODEX-001 e CODEX-007 mostram influência prévia de scorecard/comparativo de outras soluções. |
| C2 Cobertura de detecção | 5/5 | G2 passou nos 6 cenários oficiais de `pacote-comum/scenarios/`: baseline sem finding (`no_skew_baseline.yaml`) e 5 detectores com severidade esperada: skew high, GC critical, shuffle spill critical, OOM critical, cartesian product critical. Evidências: `evidence/g1-baseline.log`, `evidence/g2-cenarios.log`, `evidence/generated/official-scenarios/*.ndjson`, CODEX-009 a CODEX-014. |
| C3 Confiabilidade | 4/5 | Baseline negativo oficial ficou limpo em G1 (`evidence/g1-baseline.log`, CODEX-009). Findings passam por `EvidenceValidator` (`apex/commander/evidence_validator.py`) e G4/G5 validaram finding real com `accepted=true`. G5 também corrigiu bug real no token de apply guardado (CODEX-021) e adicionou regressão em `tests/test_commander_apply_verify.py`. Não é 5/5 porque ainda faltam listener real fail-safe, CI comum completo e oráculo agendado de drift (G6 não cumpre no `PLANO.md`). |
| C4 Loop no IDE | 3/5 | O ciclo funcional detectar -> preview -> apply guardado -> verify -> rerun -> limpo foi provado em G5 contra Spark real: `evidence/g5-ciclo.log`, `evidence/g5-before-diagnosis.json`, `evidence/g5-after-diagnosis.json`, `evidence/generated/g5/g5_fixed_eventlog.zstd`; finding caiu de 1/high para 0 e shuffle read caiu de 1.157.481 bytes para 0. Porém a tool ainda se chama `apply_recommendation`, não `apply_fix` (CODEX-019), e o MCP não foi validado dentro de IDE real. |
| C5 Qualidade de engenharia | 4/5 | Há 143+ testes acumulados pela branch: G0 registrou suíte ampla em `evidence/g0-testes.log`, G5 adicionou teste focado e `evidence/g5-tests.log` mostra `12 passed in 0.55s`. Todos os gates G0-G5 têm evidência crua em `evidence/`. O trabalho registrou issues formais CODEX-001 a CODEX-021 e não escondeu bugs encontrados no caminho. Não é 5/5 por dois achados de proveniência (CODEX-001, CODEX-007), por pendências abertas de contrato (`apply_fix`, CODEX-019) e por componentes V1 ainda parciais. |
| C6 Custo/latência | 5/5 | G4 mediu o caminho T1 determinístico completo contra event log real `app-20260712053414-0001` em 226.991 ms, sem LLM. Evidência: `evidence/g4-t1.log`, `tools/g4_t1_latency.py`, CODEX-017. O grep do caminho medido não encontrou referências a LLM/API. A política de escalonamento para Crew.ai quando confiança < 0.6 segue como gap honesto, não custo oculto (CODEX-018). |

Nota total: 23/30.

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

- A branch ainda não cumpre L2 como plataforma autônoma própria: G3/G5 validaram
  contra a stack `plat-v0` existente (`spv0-*`), enquanto o `docker-compose.yml`
  da branch permanece fundação standalone.
- Não há SparkListener JVM real fail-safe. O que existe é template/comando e
  parser/telemetria a partir de event log.
- Não há Crew.ai/Judge implementado. O escalonamento para LLM quando confiança
  < 0.6 é decisão de design registrada, não funcionalidade entregue.
- O contrato comum espera `apply_fix`; a branch entrega `apply_recommendation`.
  Isso está aberto como CODEX-019.
- MCP stdio existe, mas o ciclo não foi validado dentro de IDE real.

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
- A parte mais fraca é arquitetural: listener real, Crew.ai, IDE real e contrato
  `apply_fix` ainda faltam.
- A proveniência não é limpa: CODEX-001 e CODEX-007 precisam acompanhar a
  avaliação. O fix guardado foi adoção consciente de conceito visto na Cowork,
  depois implementado, testado e validado pela Codex.
