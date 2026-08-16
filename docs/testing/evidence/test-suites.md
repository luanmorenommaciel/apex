# Suítes de teste — execução real

Todas as suítes do repositório, rodadas contra `origin/main` (`50d596e`).
Nenhuma delas exigiu mudança de código para passar.

---

## `jar` — suíte JVM, 4 células de cross-build

**Esta suíte nunca tinha rodado.** A imagem de build do JAR executa apenas
`sbt assembly` (compilação); `sbt test` não é invocado em lugar nenhum do
pipeline. Rodada aqui pela primeira vez.

Sem instalar `sbt` na máquina, usando a imagem já fixada pelo próprio projeto:

```bash
MSYS_NO_PATHCONV=1 docker run --rm -v "$PWD/jar":/workspace -w /workspace \
  sbtscala/scala-sbt:eclipse-temurin-jammy-17.0.10_7_1.10.4_3.5.2 \
  sbt -batch test
```

Resultado: **36 testes, 36 passaram, 0 falhas**, nas 4 células —
`spark35-jvm-2.12`, `spark35-jvm-2.13`, `spark40-jvm-2.13`, `spark41-jvm-2.13`.
Tempo real de parede: ~46 min.

---

## `engine` e `serve` — suítes próprias

Antes desta sessão, as duas raias tinham sido exercitadas apenas
funcionalmente (job real ponta a ponta), nunca pela própria suíte unitária.

```bash
cd engine && uv run --extra dev pytest -q -p no:warnings
cd serve  && uv run --extra dev pytest -q -p no:warnings
```

Ambas: passou, `exit 0`.

---

## Gate raiz — seis raias

```bash
cd engine && uv run --extra dev pytest ../tests -q
```

```
4 passed in 16.52s
```

---

## `verify` — suíte unitária

```bash
make test-verify
```

**105 testes, 105 passaram.** Sem necessidade de infraestrutura.

---

## `memory` — gate de recall contra job real

```bash
python -m apex_memory index      # 7 planos reais indexados
python tools/recall_gate.py
```

**15 de 18 checks passaram.** As 3 falhas são de cold-start e são esperadas
por design do próprio gate — não são regressão.

---

## `verify` — bench real de replay

O único teste que exige a infra completa de pé, e o mais demorado.

```bash
cd verify
APEX_CANONICAL_CH_PASSWORD=... CLICKHOUSE_USER=... CLICKHOUSE_HOST=... \
CLICKHOUSE_PORT=... CLICKHOUSE_DATABASE=... \
  uv run --extra dev python scripts/run_replay.py --reps 3
```

Dois braços (baseline com AQE desligado, tratamento com AQE ligado e
`coalescePartitions` desabilitado) contra o `skew_join` calibrado do `dev`.

```
mechanism_confirmed : skew_split disparou em 3/3 execuções do braço de tratamento
                      (confirmado via apex.plan_transitions)
runtime             : delta de estágio +397%, dentro do piso de ruído medido (±44,8%)
verdict             : runtime_unresolved
exit                : 0  — controle positivo PASSOU
```

**Isto é o comportamento correto, não uma falha.** A raia se recusa a
certificar uma magnitude que a escala do teste não sustenta. Um piso de ruído
alto num laptop, depois de um dia inteiro de carga concorrente de Docker e
Spark, é exatamente a condição em que uma ferramenta honesta deve dizer
"não sei" em vez de publicar um número.

Ver [`verify/README.md`](../../../verify/README.md), seção "Verdicts", e a
seção "The positive control, and why it was left failing".
