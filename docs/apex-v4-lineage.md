# Apex v4 Corrigido - Linhagem das Melhorias

Data: 2026-06-08
Fork de evidencia: https://github.com/gustocezar/dataship-spark-plat-v0
Projeto destino: https://github.com/luanmorenommaciel/apex
Base de plataforma: https://github.com/Gabriel-Philot/dataship-spark-plat-v0

Este documento registra a linhagem tecnica do slice Apex v4 corrigido. Ele explica por que o fork existe, o que mudou em relacao ao estado anterior, quais testes provaram a correcao e como o material se conecta as issues abertas do Apex.

## Objetivo

O fork `gustocezar/dataship-spark-plat-v0` funciona como ambiente reproduzivel de prova para o Apex. Ele preserva a plataforma local do Gabriel, adiciona o slice de diagnostico Spark e guarda a evidencia de que o event log sintetico pode representar o comportamento real medido no Spark.

O repo `luanmorenommaciel/apex` continua sendo o destino do produto Apex: design, issues, codigo consolidado e decisao de governanca.

## Linha do tempo curta

1. O clone do Gabriel continha uma versao intermediaria do slice Apex.
2. Essa versao detectava skew e dava `GATE VERDE`, mas o sintetico gerava um ratio falso: `15392.3x`.
3. O log real do Spark no `real_log.ndjson` media ratio `29.5x`.
4. A v4 corrigida mudou a geracao sintetica para derivar a distribuicao de `rows * hot_share`.
5. Depois da correcao, o sintetico passou a medir ratio `27.9x`, perto do real `29.5x`.
6. O watcher continuou detectando o anti-pattern e o oraculo passou a validar fidelidade contra o Spark real.

## Baseline anterior

No clone antes da v4 corrigida, o teste Apex falhava parcialmente:

```text
python -m pytest tests/test_slice.py -q
.s.......F.FF [100%]
```

Falhas observadas:

- `test_watcher_detects_real_collapse`: o watcher detectava skew, mas nao reportava colapso 1-task com clareza.
- `test_oracle_passes_on_collapse_with_warning`: o oraculo apenas avisava ratio diferente, sem concluir fidelidade.
- `test_oracle_catches_join_mismatch`: o contrato da mensagem de erro era inconsistente.

O problema principal apareceu no fluxo manual:

```text
watcher: GATE VERDE
synthetic ratio: 15392.3x
real ratio:      29.5x
```

Esse estado provava que o watcher encontrava skew, mas nao provava que o sintetico era fiel ao Spark real.

## Correcoes da v4

### apex/apexlib.py

Responsabilidade: leitura e analise dos event logs.

Mudancas:

- Adiciona `iter_events` para leitura em streaming.
- Suporta zstd sem carregar o arquivo inteiro na memoria quando a biblioteca `zstandard` esta disponivel.
- Aceita diretorio de rolling logs (`events_1`, `events_2`, `events_10`) com ordenacao numerica.
- Seleciona o stage do join usando o nome do stage e o operador do plano.
- Associa plano final e inicial por `executionId`.
- Centraliza `compute_scenario_hash` e `validate_provenance`.

Impacto:

O parser passa a tratar formatos mais proximos do Spark History real e reduz risco de analisar o stage errado.

### generators/plan_generator.py

Responsabilidade: gerar event log sintetico sem executar Spark.

Mudanca central:

A versao anterior usava `single_task_shuffle_read_records: 200100` como volume da task quente. Como o scenario tinha `rows: 200000`, isso quebrava a distribuicao das tasks frias e inflava o ratio para `15392.3x`.

A v4 corrigida calcula:

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
hot_records ~= 160000
cold_each ~= 5714
ratio sintetico ~= 27.9x
```

Impacto:

O sintetico passa a bater com o log real dentro da tolerancia do oraculo.

### generators/code_generator.py

Responsabilidade: gerar o job PySpark e o manifesto.

Mudancas:

- Usa `apexlib.compute_scenario_hash`.
- Grava `scenario_hash`, `generator_version`, `generated_at`, `job_file`, linha real do anti-pattern e classe do anti-pattern no manifesto.
- Mantem a sentinela `# APEX::ANTIPATTERN` como saida derivada, nao como linha hardcoded.

Impacto:

O job real e o log sintetico passam a compartilhar uma cadeia de custodia baseada no mesmo scenario.

### watchers/skew_watcher.py

Responsabilidade: detectar skew e emitir finding.

Mudancas:

- Valida proveniencia antes de analisar logs sinteticos.
- Passa `join_op` para `hottest_reduce_stage`.
- Inclui `customer_id = 7` e `SortMergeJoin` no `root_cause`.
- Reporta colapso 1-task como evidencia quando o log real roda em ambiente colapsado.

Impacto:

O watcher continua gerando `GATE VERDE`, mas agora explica melhor o motivo e respeita o contrato do scenario.

### oracle/compare.py

Responsabilidade: comparar sintetico contra log real.

Mudancas:

- Cria audit trail com `scenario_hash`.
- Compara operador de join, task quente e ratio.
- Reabilita a comparacao de ratio porque a distribuicao sintetica foi corrigida.
- Trata colapso 1-task como aviso honesto, nao como falso verde.

Impacto:

O oraculo deixa de apenas avisar divergencia e passa a declarar se o sintetico esta fiel ao Spark real dentro da tolerancia.

### scenarios/skew_on_join_30x.yaml

Mudancas:

- Sobe `version` para `4`.
- Remove `hot_partition.single_task_shuffle_read_records`.
- Mantem o contrato declarativo baseado em `rows`, `hot_share`, `shuffle.partitions`, `join_operator` e `hot_stage`.
- Ajusta tolerancia do oraculo para `skew_ratio: 0.40` e `records: 0.30`.

Impacto:

O scenario volta a ser a unica fonte de verdade. O gerador de plano nao precisa de um numero observado no log real para simular skew.

### tests/test_slice.py

Responsabilidade: fixar comportamento do slice.

Novas coberturas relevantes:

- Leitura streaming de zstd.
- `iter_events` lazy.
- Diretorio de rolling logs.
- Ordenacao numerica de rolling logs.
- Stage correto do join, mesmo quando outro stage le mais shuffle.
- Associacao de plano por `executionId`.
- Ratio sintetico realista, entre `20x` e `40x`.
- Hash deterministico de scenario.
- Mesmo hash no manifesto do code generator e no primeiro evento do plan generator.
- Rejeicao de log sintetico stale.
- Log real sem provenance permitido.
- Watcher verde no sintetico.
- Oraculo fiel contra log realista.
- Oraculo detecta mismatch de join.

## Evidencia no Ubuntu

Comandos rodados em WSL/Ubuntu no clone aplicado:

```bash
cd /mnt/c/Users/Guest/projetos/dataship-spark-plat-v0
source .venv/bin/activate
python -m pytest tests/test_slice.py -q
python generators/plan_generator.py scenarios/skew_on_join_30x.yaml /tmp/apex-synthetic.ndjson
python watchers/skew_watcher.py scenarios/skew_on_join_30x.yaml /tmp/apex-synthetic.ndjson
python oracle/compare.py scenarios/skew_on_join_30x.yaml /tmp/apex-synthetic.ndjson real_log.ndjson
```

Resultado:

```text
s.................... [100%]
```

Watcher:

```text
stage 4: task quente 160000 vs mediana das frias 5726 -> skew ratio 27.9x (8 tasks)
root_cause: data skew na chave de join customer_id = 7 (SortMergeJoin)
GATE VERDE
```

Oraculo:

```text
join:  synthetic=SortMergeJoin  real=SortMergeJoin
hot:   synthetic=160000         real=165297
ratio: synthetic=27.9           real=29.5
ORACULO: sintetico fiel ao Spark real dentro da tolerancia.
```

## Arquivos que pertencem ao commit do fork

Estes arquivos representam o slice v4 corrigido e a prova reproduzivel:

```text
.github/workflows/scenario-gate.yml
AGENTS.md
apex/apexlib.py
generators/code_generator.py
generators/plan_generator.py
oracle/compare.py
real_log.ndjson
requirements.txt
run_slice.sh
scenarios/skew_on_join_30x.yaml
tests/test_slice.py
watchers/skew_watcher.py
docs/apex-v4-lineage.md
```

Estes arquivos devem ficar fora do commit principal, salvo decisao explicita:

```text
APEX_V4_COMPLETE_SPEC*
job_real.py
job_real.meta.json
job_v4.py
job_v4.meta.json
real_log.ndjson_bak
synthetic_v4.ndjson
watchers/skew_watcher.py.bak
watchers/skew_watcher.py.bak2
```

## Relacao com issues do Apex

| Issue | Papel da evidencia deste fork |
|---|---|
| https://github.com/luanmorenommaciel/apex/issues/9 | Mostra um primeiro contrato de geracao para skew, com scenario declarativo e validacao contra log real. |
| https://github.com/luanmorenommaciel/apex/issues/10 | Usa a plataforma local como ambiente de prova: Spark, event log, History/log real e workflow reproduzivel. |
| https://github.com/luanmorenommaciel/apex/issues/16 | Entrega um parser inicial de Spark History/event log com zstd, rolling logs, stage metrics, join operator e skew indicators. |
| https://github.com/luanmorenommaciel/apex/issues/17 | Entrega o primeiro Watcher deterministico para skew, com finding, root cause, evidence e recommendations. |
| https://github.com/luanmorenommaciel/apex/issues/19 | Demonstra que `dataship-spark-plat-v0` serve como plataforma local de bootstrap para Apex. |
| https://github.com/luanmorenommaciel/apex/issues/21 | Adiciona um scenario gate em GitHub Actions para rodar testes e o slice por scenario em PR. |
| https://github.com/luanmorenommaciel/apex/issues/23 | Ajuda a decisao de governanca: o fork pode funcionar como mirror/evidence repo enquanto Apex consolida o produto. |
| https://github.com/luanmorenommaciel/apex/issues/25 | Fornece um dado concreto para a decisao Commander: integrar, espelhar ou manter sandbox. |

## Recomendacao de governanca

Manter o fork `gustocezar/dataship-spark-plat-v0` como repo de evidencia reproduzivel no curto prazo.

Levar para `luanmorenommaciel/apex` em etapas:

1. Documentar a evidencia nas issues #9, #16, #17, #19, #21, #23 e #25.
2. Criar uma issue especifica para o slice `skew_on_join_30x` v4 corrigido.
3. Decidir se o codigo entra no Apex como modulo, subdiretorio, branch de laboratorio ou referencia externa.
4. Manter o contrato inegociavel: coleta nao-intrusiva via event log nativo do Spark, sem JAR, sem listener injetado e sem alterar SparkSession do cliente.

## Proximos passos tecnicos

1. Criar `scenarios/no_skew_baseline.yaml` para exercitar falso positivo e loop multi-cenario no CI.
2. Adicionar `validation_criteria` no scenario.
3. Substituir `confidence = ratio/(ratio+3)` por confianca baseada em evidencia: numero de tasks, estabilidade do ratio, operador de join e qualidade do log.
4. Criar GitHub Action semanal do oraculo contra log real versionado.
5. Atualizar o README do fork para v4 corrigido, pois ele ainda descreve v3.
