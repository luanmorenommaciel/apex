# Apex - instrucoes para agentes

Leia primeiro:

```text
docs/apex-v4-lineage.md
```

Esse documento explica a linhagem da v4 corrigida, a evidencia rodada no Ubuntu, o
mapeamento para as issues do Apex e o escopo que deve entrar no commit do fork.

## Setup

```bash
pip install -r requirements.txt
```

## Verificar

```bash
python3 -m pytest tests -q
bash run_slice.sh
python3 generators/plan_generator.py scenarios/skew_on_join_30x.yaml /tmp/apex-synthetic.ndjson
python3 watchers/skew_watcher.py scenarios/skew_on_join_30x.yaml /tmp/apex-synthetic.ndjson
python3 oracle/compare.py scenarios/skew_on_join_30x.yaml /tmp/apex-synthetic.ndjson real_log.ndjson
```

Resultado esperado:

```text
tests: 40 passed
watcher: GATE VERDE
oracle: sintetico fiel ao Spark real dentro da tolerancia
```

## Regras

- Coleta nao-intrusiva: zero JAR, zero listener injetado, zero modificacao de SparkSession do cliente.
- Nao reporte verde obtido afrouxando checagem.
- Se um teste nao cobre um caso, diga.
- Antes de escrever codigo novo, rode o baseline e confirme o resultado.
- Nao inclua arquivos `.bak`, logs temporarios ou jobs gerados no commit principal sem decisao explicita.
- Toda mudanca de validacao, fonte, estado de evidencia ou responsabilidade deve revisar
  `docs/architecture/validation-evidence-flow.md`.
- O mesmo PR deve manter atualizados: fluxo, arquitetura, sequencia, cadeia de valor,
  gargalos e pontos de ruptura. Se uma visao nao mudar, registre que ela foi revisada.

## Proximo trabalho

1. Criar `scenarios/no_skew_baseline.yaml`.
2. Extrair o gate atual para `Evidence Validator` dirigido por `validation_criteria`.
3. Tornar Watcher e Oracle incrementais e isolados por aplicacao.
4. Substituir a confianca residual por score de qualidade e cobertura.
5. Criar Action semanal do Oraculo contra log real versionado.
6. Avaliar `watchers/memory_watcher.py` como proximo watcher.
