# Apex V1 — Pacote Completo de Recriação e Julgamento

> **Propósito:** o documento-MESTRE. Uma LLM externa (orquestradora/juiz, ou uma
> engine recriando do zero) que receba SÓ este arquivo + os caminhos listados tem
> tudo: o que construir, como estruturar, como provar, como julgar.
> **Versão:** 1.0 · 2026-07-10 · branch `gustocezar/feature/cowork-desacoplamento-geradores`

---

## 1. Ordem de leitura (para LLM externa ou harness)

| # | Arquivo | Papel | Consumidor |
|---|---|---|---|
| 1 | `docs/specs/apex-v1-spec-reproducivel.md` | O QUE construir (missão, premissas L1–L9, arquitetura, thresholds, gates, lições) | todos |
| 2 | `docs/specs/telemetry-schema-contract-v1.md` + `apex_telemetry_v1.sql` | Contratos de dados IMUTÁVEIS | engines |
| 3 | `scenarios/*.yaml` (6 world A) | Casos de teste oficiais | engines + juiz |
| 4 | `docs/playbooks/protocolo-rodada2-llms.md` | COMO estruturar (fases F0–F5, ISSUES.md, evidence/, prompt de largada) | engines |
| 5 | `docs/architecture/llm-solution-validation-framework-2026-07-09.md` | Critérios C1–C6, gates G0–G6, scorecard do round 1, método | juiz |
| 6 | `docs/playbooks/orquestrador-juiz-llm.md` | COMO julgar (verificação, score, arbitragem) | juiz |
| 7 | `docs/adr/ADR-006-composicao-v1.md` + `docs/architecture/roadmap-v01-v1-visao.md` | Decisão proposta + evolução V0.1→Visão | juiz + Commander |
| 8 | `docs/meetings/captains-report-2026-07-0{8,10}.md` | Histórico e padrão de reporte | juiz |
| 9 | `scripts/g3_multicore_gate.py` · `scripts/apply_fix_cli.py` · `watchers/*.py` | Juízes automáticos executáveis | harness |
| 10 | `tests/` (52 testes) | Prova executável da referência cowork | harness |

## 2. Manifest para harness (machine-readable)

`docs/specs/manifest-rodada2.json` — mesmo conteúdo do §1 em JSON: arquivos com
`role`, `mutable`, `consumer`, comandos dos gates com `expect`. Um harness monta
o contexto de qualquer LLM (engine ou juiz) lendo só o manifest.

## 3. Estado de referência (verificado em 10/07 — baseline do julgamento)

| Solução | Branch | Estado verificado |
|---|---|---|
| cowork | `gustocezar/feature/cowork-desacoplamento-geradores` | gates G0–G5 verdes, 52 testes, ciclo real completo |
| spike | `spike/apex-v0.1` | 22 testes, 5 detectores, melhor plataforma |
| kimi | `.../kimi-desacoplamento-geradores` (+ `apex-kimi-product-v0.1` local) | Python: 9/12 testes; Go: não compila |
| codex | `.../codex-desacoplamento-geradores` (repo apex-official) | 44 testes, harness local, contrato job_id |

Números de referência dos gates (para o juiz conferir reproduções): skew sintético
27.9x · real 29.4x (8 tasks) · T1 333ms/0 tokens · fix real: shuffle 1.16MB→0.

## 4. Ambiente de execução

plat-v0 (`github.com/gustocezar/dataship-spark-plat-v0`, compose em `build/`):
Spark 4.1.2 standalone (worker `SPARK_WORKER_CORES=8`) · MinIO :29000
(spv0minio/spv0minio123, bucket `spark-logs/events/`) · ClickHouse :28123
(spv0/spv0clickhouse123) — **ClickHouse exige named volume** (NTFS quebra
MergeTree). Python 3.11+: `pyyaml zstandard pytest clickhouse-connect minio
anthropic crewai`. Windows: `PYTHONUTF8=1` em subprocessos.

## 5. Invariantes (quebrou, desclassificou)

1. Contratos do §1.2 imutáveis. 2. Cenários oficiais intocados. 3. Evidência =
log cru em `evidence/`. 4. Baseline negativo sempre verde (falso positivo = red).
5. Honestidade > completude: parcial documentado vence completo maquiado.
6. Nenhuma engine vê o código das outras; o juiz vê tudo.
