# Validação do Desacoplamento – Apex

**Data:** 2026-06-05  
**Executado por:** Augusto (Captain)  
**Ambiente:** `dataship-spark-plat-v0` (Spark 4.1.2, MinIO, ClickHouse)

## Objetivo
Provar que o gerador de código e o gerador de plano podem ser desacoplados usando um contrato `scenario.yaml`, sem que um dependa do outro.

## Contrato utilizado
`scenarios/skew_on_join_30x.yaml`  
Campos chave:
- `join_operator: SortMergeJoin`
- `single_task_shuffle_read_records: 200100`

## Gerador de código
```bash
python3 generators/code_generator.py scenarios/skew_on_join_30x.yaml job_demo.py
