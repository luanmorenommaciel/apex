# Changelog

Todas as mudanças notáveis do Apex são documentadas aqui.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Planejado (P0 — antes de qualquer escala)
- `apexlib.read_events`: streaming zstd via `zstandard.stream_reader` (elimina OOM em logs grandes)
- `apexlib.hottest_reduce_stage`: usar `hot_stage` do contrato como hint (elimina stage errado em jobs multi-join)
- `apexlib.read_events`: aceitar diretório e concatenar múltiplos arquivos (suporte a rolling logs)

### Planejado (P1 — antes de novos watchers)
- `apexlib.join_operator`: filtrar por `executionId` (elimina captura de plano de outra query SQL)
- `skew_watcher.root_cause`: ler chave de join do contrato (elimina hardcode "customer_id")

### Planejado (P2 — antes de `status: validated`)
- Confiança derivada do contrato via `confidence_thresholds`
- Teste de manifesto `job.meta.json`
- Segundo cenário (Pod A2 — Memory/Cost Watcher)
- `oracle-weekly.yml` CI agendado
- Critérios de progressão `prototype → validated`

---

## [0.3.0] — 2026-06-06 · v3 — Causa raiz

### Added
- `apex/apexlib.py` — lib compartilhada eliminando duplicação de lógica entre Watcher e Oráculo
- `oracle/compare.py` — oráculo que valida event log sintético vs real
- `scenarios/skew_on_join_30x.yaml` — contrato declarativo desacoplando code_generator e plan_generator (ADR-004)
- `.github/workflows/scenario-gate.yml` — gate por PR: gera fixture, roda testes, exige acceptance verde

### Changed
- `watchers/skew_watcher.py`: **stage-aware skew** — isola reduce stage (shuffle > 0), não mistura com scan tasks
- `watchers/skew_watcher.py`: **AQE-aware** — lê plano FINAL pós-`SparkListenerSQLAdaptiveExecutionUpdate`
- `watchers/skew_watcher.py`: tratamento explícito de 1 task (colapso AQE), sem hack `/0`
- `generators/*.py`: ambos leem de `scenario.yaml` independentemente — sem acoplamento entre si

### Fixed
- OOM mascarado: divisão por zero em skew ratio removida pela causa raiz (skew_metrics com collapsed explícito)
- Plano errado: v2 lia plano inicial do SQL; v3 lê o plano final pós-AQE
- Stage errado: v2 misturava tasks de scan (shuffle=0) com reduce; v3 isola por shuffle > 0
- Tolerância inflada: v2 aceitava qualquer ratio com tolerância arbitrária; v3 tem acceptance declarado no contrato

### Evidência
- 25 testes passando (13 unitários + 12 do plat-v0)
- GATE VERDE no Spark 4.1.2 real — app `app-20260606030054-0000`
- Commit: `357efad` (em plat-v0, a ser migrado para este repo)

---

## [0.2.0] — 2026-05 · v2 — Band-aids

### Added
- `skew_watcher.py` v2 com detecção de skew funcional
- Sintético gerado e consumido pelo Watcher
- Testes básicos passando

### Changed
- Tolerância ajustada empiricamente para passar o gate

### Known Issues (resolvidos em v3)
- Divisão por zero mascarada com `or [1]`
- Comparação de ratio desligada em alguns casos
- Leitura do plano inicial (não o final pós-AQE)
- Mistura de tasks de scan e reduce no cálculo de skew

---

## [0.1.0] — 2026-05 · v1 — Hipótese

### Added
- Prova de conceito: event log sintético + Watcher básico
- `code_generator.py` acoplado ao `plan_generator.py`
- Primeiros testes de integração

### Lições aprendidas
- AQE muda o plano em pleno voo — o plano inicial não é o executado
- Tasks de scan leem 0 registros de shuffle — misturá-las com reduce distorce o ratio
- Sintético deve ser derivado de uma especificação compartilhada, não do código executado
