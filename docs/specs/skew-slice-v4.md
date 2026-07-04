# Especificacao Tecnica - Slice `skew_on_join_30x` v4

## Objetivo

Provar que o Apex consegue gerar um workload Spark e um event log sintetico a partir do mesmo contrato declarativo, detectar skew com um Watcher deterministico e validar a fidelidade do sintetico contra um log real do Spark.

## Contrato

`scenarios/skew_on_join_30x.yaml` — campos principais:

| Campo | Papel |
|---|---|
| `scenario_id` | Identificador unico |
| `code_generator.data.orders.rows` | Volume da tabela fato |
| `code_generator.data.orders.hot_share` | Percentual concentrado na hot key |
| `spark.sql.shuffle.partitions` | Numero de particoes de shuffle |
| `plan_generator.expected_signals.join_operator` | Operador esperado no plano |
| `plan_generator.expected_signals.hot_stage` | Stage esperado para o join |
| `oracle.tolerance` | Tolerancia para comparar sintetico e real |
| `acceptance.root_cause_includes` | Termos obrigatorios no Finding |

## Formula da distribuicao (v4 corrigida)

```text
hot_records = rows * hot_share         = 160000
cold_total  = rows - hot_records       = 40000
cold_each   = cold_total / (partitions - 1)  ~= 5714
ratio       = hot_records / cold_each  ~= 27.9x
```

## Cadeia de custodia

`sha256(scenario.yaml)[:16]` aparece no manifesto do `code_generator`, no primeiro evento do log sintetico (`ApexSyntheticProvenance`) e no audit trail do Oraculo. Se o scenario mudar pos-geracao, o Watcher falha com `PROVENANCE ERROR`.

## Limites atuais

- Sem baseline sem skew (`no_skew_baseline.yaml`).
- Confidence ainda e `ratio/(ratio+3)` — proximo trabalho.
- Action semanal do Oraculo ainda pendente.
- Core em Go ainda nao iniciado.
