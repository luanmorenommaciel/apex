# Especificacao Tecnica - Slice `skew_on_join_30x` v4

## Objetivo

Provar que o Apex consegue gerar um workload Spark e um event log sintetico a partir do mesmo contrato declarativo, detectar skew com um Watcher deterministico e validar a fidelidade do sintetico contra um log real do Spark.

## Contrato

Arquivo:

```text
scenarios/skew_on_join_30x.yaml
```

Campos principais:

| Campo | Papel |
|---|---|
| `scenario_id` | Identifica o scenario |
| `code_generator.data.orders.rows` | Volume da tabela fato |
| `code_generator.data.orders.hot_key` | Chave concentrada |
| `code_generator.data.orders.hot_share` | Percentual da tabela fato na hot key |
| `spark.sql.shuffle.partitions` | Numero de particoes de shuffle |
| `plan_generator.expected_signals.join_operator` | Operador esperado no plano |
| `plan_generator.expected_signals.hot_stage` | Stage esperado para o join |
| `oracle.tolerance` | Tolerancia para comparar sintetico e real |
| `acceptance.root_cause_includes` | Termos obrigatorios no Finding |

## Fluxo

```text
scenario.yaml
  -> code_generator.py
       -> job.py
       -> job.meta.json
  -> plan_generator.py
       -> synthetic.ndjson
  -> skew_watcher.py
       -> Finding + GATE
  -> oracle/compare.py
       -> synthetic vs real_log.ndjson
```

## Cadeia de custodia

O Apex calcula:

```text
sha256(scenario.yaml)[:16]
```

O hash aparece em:

- manifesto gerado pelo `code_generator`;
- primeiro evento do log sintetico: `ApexSyntheticProvenance`;
- validacao do Watcher;
- audit trail do Oraculo.

Se o scenario muda depois da geracao do log, o Watcher deve falhar com `PROVENANCE ERROR`.

## Gerador de codigo

Arquivo:

```text
generators/code_generator.py
```

Responsabilidades:

- ler o scenario;
- gerar um job PySpark;
- marcar a linha do anti-pattern com `# APEX::ANTIPATTERN`;
- gerar manifesto com hash, versao, timestamp e linha real.

O numero de linha e saida derivada. Ele nao deve ser mantido manualmente no scenario.

## Gerador de plano

Arquivo:

```text
generators/plan_generator.py
```

Responsabilidades:

- gerar event log Spark em NDJSON;
- usar nomes reais do JsonProtocol do Spark;
- gerar distribuicao de shuffle com cauda;
- inserir `ApexSyntheticProvenance`.

Formula da v4 corrigida:

```text
hot_records = rows * hot_share
cold_total  = rows - hot_records
cold_each   = cold_total / (shuffle_partitions - 1)
```

Para o scenario atual:

```text
rows = 200000
hot_share = 0.80
shuffle_partitions = 8
hot_records = 160000
cold_each ~= 5714
ratio ~= 27.9x
```

## Parser compartilhado

Arquivo:

```text
apex/apexlib.py
```

Responsabilidades:

- ler arquivo unico, `.zstd`, `.zst` ou diretorio de rolling logs;
- expor `iter_events` para leitura lazy;
- validar schema minimo;
- detectar operador de join;
- escolher stage do join;
- calcular metricas de skew;
- validar provenance.

## Watcher

Arquivo:

```text
watchers/skew_watcher.py
```

Responsabilidades:

- validar provenance antes da analise;
- identificar operador de join;
- escolher o stage correto;
- medir skew pela cauda;
- emitir Finding com root cause e recomendacoes;
- validar acceptance do scenario.

Finding esperado:

```json
{
  "watcher": "shuffle_skew",
  "severity": "high",
  "confidence": 0.9,
  "root_cause": "data skew na chave de join customer_id = 7 (SortMergeJoin): ..."
}
```

## Oraculo

Arquivo:

```text
oracle/compare.py
```

Responsabilidades:

- comparar operador de join;
- comparar task quente;
- comparar skew ratio;
- reportar colapso 1-task como aviso;
- falhar se o sintetico divergir fora da tolerancia.

Evidencia atual:

```text
synthetic hot:   160000
real hot:        165297
synthetic ratio: 27.9
real ratio:      29.5
```

## Testes

Arquivo:

```text
tests/test_slice.py
```

Coberturas obrigatorias:

- zstd streaming;
- rolling logs;
- ordenacao numerica;
- stage do join;
- `executionId`;
- ratio realista;
- hash deterministico;
- stale artifact;
- log real sem provenance;
- Watcher verde;
- Oraculo fiel;
- mismatch de join.

## Limites

Este slice cobre skew em join. Ele nao implementa ainda:

- baseline sem skew;
- watchers de memory/cost;
- confidence baseada em evidencia;
- Action semanal do Oraculo;
- integracao com comentario automatico em PR.

Consulte a [spec do inventario](event-log-coverage-inventory-v1.md) para os
sinais disponiveis no Spark event log. A
[fronteira de observabilidade](../architecture/event-log-observability-boundary.md)
explica os pontos cegos e as fontes complementares.
