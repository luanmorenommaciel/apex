# Playbook - Slice `skew_on_join_30x` v4

Este playbook mostra como rodar o slice de skew, validar a cadeia de custodia e comparar o log sintetico contra o log real versionado.

## Pre-requisitos

- Python 3.10+
- `pip install -r requirements.txt`
- Ambiente Linux/WSL recomendado para reproduzir os comandos do time.

## Validar testes

```bash
python3 -m pytest tests/test_slice.py -q
```

Resultado esperado:

```text
s.................... [100%]
```

O `s` e esperado quando o teste de zstd pula por dependencia ausente no ambiente. Com `zstandard` instalado, a suite roda completa.

## Rodar o slice completo

```bash
bash run_slice.sh
```

## Rodar passo a passo

```bash
python3 generators/code_generator.py scenarios/skew_on_join_30x.yaml /tmp/job.py
python3 generators/plan_generator.py scenarios/skew_on_join_30x.yaml /tmp/apex-synthetic.ndjson
python3 watchers/skew_watcher.py scenarios/skew_on_join_30x.yaml /tmp/apex-synthetic.ndjson
python3 oracle/compare.py scenarios/skew_on_join_30x.yaml /tmp/apex-synthetic.ndjson real_log.ndjson
```

## Interpretar o Watcher

```text
stage 4: task quente 160000 vs mediana das frias 5726 -> skew ratio 27.9x (8 tasks)
root_cause: data skew na chave de join customer_id = 7 (SortMergeJoin)
GATE VERDE
```

## Interpretar o Oraculo

```text
join:  synthetic=SortMergeJoin  real=SortMergeJoin
hot:   synthetic=160000         real=165297
ratio: synthetic=27.9           real=29.5
ORACULO: sintetico fiel ao Spark real dentro da tolerancia.
```

## Falhas comuns

**`PROVENANCE ERROR`** — log sintetico gerado com outro `scenario.yaml`. Regenerar com `plan_generator.py`.

**Ratio sintetico muito alto** — `plan_generator` regrediu para logica antiga de `single_task_shuffle_read_records`. Conferir scenario e rodar `test_plan_generator_ratio_is_realistic`.

**Watcher verde, Oraculo divergente** — Watcher detecta anti-pattern; Oraculo valida fidelidade. Verde no Watcher sem verde no Oraculo nao prova que o sintetico representa o Spark real.

## Regra de ouro

Nao reporte verde obtido afrouxando checagem.
