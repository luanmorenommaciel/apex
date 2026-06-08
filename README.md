# Apex - Geradores, Watcher e Oraculo (v4 corrigido)

Slice vertical do diagnostico de performance Spark. Um contrato declarativo
(`scenario.yaml`) dirige dois geradores desacoplados:

- `generators/code_generator.py` gera um job PySpark com sentinela e manifesto.
- `generators/plan_generator.py` gera um event log sintetico sem executar Spark.

O Watcher detecta o anti-pattern. O Oraculo compara o sintetico contra um log real do
Spark e valida se o comportamento continua fiel.

## Evidencia atual

Validado no Ubuntu/WSL sobre o `dataship-spark-plat-v0`:

```text
python -m pytest tests/test_slice.py -q
s.................... [100%]

watcher: GATE VERDE
synthetic ratio: 27.9x
real ratio:      29.5x
oracle: sintetico fiel ao Spark real dentro da tolerancia
```

O documento de linhagem explica o caminho completo da melhoria:

```text
docs/apex-v4-lineage.md
```

## Estrutura do slice

```text
apex/apexlib.py                  # leitura de event logs, zstd, rolling logs, plano, skew, provenance
generators/code_generator.py     # scenario -> job.py + manifesto com scenario_hash
generators/plan_generator.py     # scenario -> event log sintetico com ratio realista
watchers/skew_watcher.py         # detecta skew e valida acceptance do scenario
oracle/compare.py                # compara sintetico vs log real
tests/test_slice.py              # 21 testes: parser, provenance, watcher, oracle
scenarios/skew_on_join_30x.yaml  # contrato declarativo do anti-pattern
.github/workflows/scenario-gate.yml
```

## Como rodar

```bash
pip install -r requirements.txt
python3 -m pytest tests/test_slice.py -q
```

Fluxo operacional:

```bash
python3 generators/plan_generator.py scenarios/skew_on_join_30x.yaml /tmp/apex-synthetic.ndjson
python3 watchers/skew_watcher.py scenarios/skew_on_join_30x.yaml /tmp/apex-synthetic.ndjson
python3 oracle/compare.py scenarios/skew_on_join_30x.yaml /tmp/apex-synthetic.ndjson real_log.ndjson
```

Ou:

```bash
bash run_slice.sh
```

## O que a v4 corrigiu

| Antes | v4 corrigido |
|---|---|
| Sintetico gerava ratio `15392.3x` | Sintetico gera ratio `27.9x`, perto do real `29.5x` |
| `read_events` carregava arquivo inteiro | `iter_events` permite leitura em streaming |
| Um arquivo de log por vez | Aceita diretorio de rolling logs |
| Stage escolhido por maior volume | Stage do join escolhido por nome + operador |
| Plano podia misturar execucoes | Plano associado por `executionId` |
| Provenance parcial | `scenario_hash` compartilhado entre manifesto e log sintetico |
| Oraculo apenas avisava divergencia | Oraculo declara fidelidade ou divergencia dentro da tolerancia |

## Limite honesto

Este slice prova o anti-pattern `skew_on_join_30x` e valida um event log real versionado.
Ele ainda nao cobre todos os anti-patterns do Apex. Os proximos passos estao documentados
em `docs/apex-v4-lineage.md`: baseline sem skew, `validation_criteria`, confianca baseada
em evidencia e Action semanal do Oraculo.

## Relacao com o Apex

Este fork funciona como ambiente de evidencia reproduzivel. O produto Apex vive em:

```text
https://github.com/luanmorenommaciel/apex
```

Issues relacionadas: #9, #10, #16, #17, #19, #21, #23 e #25.
