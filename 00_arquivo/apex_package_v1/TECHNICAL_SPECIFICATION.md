# Especificação Técnica – Apex (Desacoplamento de Geradores)

**Versão:** 1.0 | **Data:** 2026-06-05

## Arquitetura
- **Contrato:** `scenarios/*.yaml` define anti-pattern, dados, sinais esperados.
- **Gerador de código:** `generators/code_generator.py` lê YAML e gera job PySpark com bug.
- **Gerador de plano:** `generators/plan_generator.py` lê YAML e gera log sintético (NDJSON) sem executar Spark.
- **Oráculo:** (planejado) workflow semanal que compara logs reais (do MinIO) com sintéticos.
- **Ambiente real:** `dataship-spark-plat-v0` (Spark 4.1.2, MinIO, ClickHouse).

## Fluxos validados
1. `code_generator` → `job_demo.py` → executado no Spark → log real.
2. `plan_generator` → `synthetic_log.ndjson` → contém `SortMergeJoin` e `recordsRead:200100`.
3. Validação manual confirma correspondência.

## ADRs reconciliados
- ADR-001 (reconciliado): Listener in-JVM Day 1; tail externo Go Sprint 2.
- ADR-004 (reconciliado): Go para o coletor; JVM para listener.
- ADR-005 (novo): Desacoplamento via scenario.yaml (validado).

## Próximos passos
- Implementar oráculo automático (GitHub Action).
- Expandir para 11 cenários.
- Criar CLI `apex`.
