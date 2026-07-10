# G3 — Runbook: validar o run multi-core real (8 tasks)

> **Por que existe:** o oráculo só foi validado com worker 1-core (distribuição
> colapsada). O ratio real de 8 tasks NUNCA rodou — é o último claim não
> verificado do Mundo A. ~20 min com o plat-v0.

## Passo 1 — Worker com 8 cores (repo `dataship-spark-plat-v0`)

No `docker-compose.yml` do plat-v0, garantir no serviço do worker:

```yaml
environment:
  - SPARK_WORKER_CORES=8
  - SPARK_WORKER_MEMORY=4g
```

```powershell
docker compose down; docker compose up -d
# conferir na UI do master (localhost:8080): worker com 8 cores
```

## Passo 2 — Gerar e submeter o job de skew

```powershell
cd "C:\Users\Guest\Claude\Projects\Data Ship"
python generators/code_generator.py scenarios/skew_on_join_30x.yaml g3_job.py
# copiar para o container e submeter (ajustar nomes do plat-v0):
docker cp g3_job.py spark-master:/tmp/g3_job.py
docker exec spark-master spark-submit --master spark://spark-master:7077 `
  --conf spark.eventLog.enabled=true `
  --conf spark.eventLog.dir=s3a://spark-logs/events `
  /tmp/g3_job.py
```

## Passo 3 — Rodar o gate (um comando)

```powershell
# opcao A: direto do MinIO
$env:MINIO_ENDPOINT="http://localhost:29000"; $env:MINIO_ACCESS_KEY="..."; $env:MINIO_SECRET_KEY="..."
pip install minio
python scripts/g3_multicore_gate.py --from-minio --app-id <app_id>

# opcao B: log ja baixado
python scripts/g3_multicore_gate.py --real-log caminho\do\log
```

O script valida os 3 critérios do G3: distribuição >= 8 tasks (não colapsou),
oráculo dentro da tolerância (sintético ~27.9x vs real), watcher GATE VERDE no
log real. Exit 0 = **G3 VERDE**.

## Passo 4 — Registrar

Com verde: atualizar `docs/architecture/llm-solution-validation-framework-2026-07-09.md`
(§7 G3 → ✅ com o ratio real) e `tasks/backlog.md` (infra multi-core). Anexar o
output do script como comentário na issue #19 (CREW standard).

## Se der vermelho

| Sintoma | Causa provável |
|---|---|
| "1 task no stage" | worker ainda 1-core (Passo 1 não aplicado) ou AQE coalesceu — conferir spark_config do cenário (AQE off) |
| "ratio divergiu" | esperado se a tolerância (40%) for real — ISSO É O DADO QUE QUEREMOS: abrir issue com o ratio real e recalibrar o gerador |
| watcher não detectou | skew real < 10x — mesma ação: registrar e recalibrar |
