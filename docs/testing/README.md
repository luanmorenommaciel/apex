# `docs/testing/` — registro de testes, evidência e metodologia

**Esta branch não propõe nenhuma mudança para `main`.** Ela é base de estudo:
reúne o que foi testado no trabalho do `pod-2-engine`, a evidência bruta de
execução, os scripts que reproduzem cada caso, e a metodologia usada para
chegar até eles.

Se você (pessoa ou LLM) chegou aqui para entender o que foi feito e refazer os
testes por conta própria, leia nesta ordem:

1. [`LINEAGE.md`](LINEAGE.md) — os 11 issues, do problema até o PR que os fecha
2. [`METHODOLOGY.md`](METHODOLOGY.md) — como cada problema foi atacado, e por quê
3. [`error-cases.md`](error-cases.md) — erro literal + comando exato de repro, por PR
4. [`evidence/`](evidence/) — saída real de execução, sem edição
5. [`scripts/`](scripts/) — os scripts executáveis de cada reprodução

Base: `origin/main` em `50d596e`, a mesma das branches `candidate/*` que viraram
PR. Nada aqui depende de código que não esteja no `main`.

> **Atualização 19/08:** os 8 PRs desta jornada (#66-#70, #74-#76) foram
> revisados, aprovados e **mergeados em 18/08**. As issues ligadas a eles
> fecharam automaticamente. Seguem abertas apenas #59, #65 e #71 — as três
> que dependem de decisão do mantenedor, não de código. A linhagem em
> [`LINEAGE.md`](LINEAGE.md) descreve o caminho até o PR; o destino final de
> todos eles é o `main`.

---

## Procedência — de onde veio o que foi testado

Boa parte do que virou PR não nasceu do zero: veio **portada de uma versão
baseline independente do APEX**, construída antes deste trabalho e usada aqui
como fonte de comparação contra o `main`.

Sem isso registrado, a leitura fica errada — parece que tudo se originou no
`main`, quando na verdade o método foi *comparar duas implementações reais* e
testar o que a diferença entre elas expunha.

| | |
|---|---|
| **Baseline (fonte)** | `github.com/gustocezar/apex-workspace` |
| Branch de release | `release/apex-v1-final-augusto` @ `7f53d22` (2026-08-05) |
| Branch equivalente | `base-project-e2e-augusto` (mesmo commit) |
| **Upstream (alvo)** | `github.com/luanmorenommaciel/apex` |
| Base usada | `main` @ `50d596e` |
| Worktree local de teste | `apex-luan-e2e-baseline`, checkout de `origin/main` |

> **O repositório do baseline é privado hoje.** Quem não tiver acesso não
> consegue abrir os links acima. Para o time reproduzir a comparação (e não só
> os testes, que são autocontidos nesta branch), o acesso precisa ser
> concedido — decisão de quem é dono do repositório.

Nos documentos deste diretório, os dois lados aparecem como **`fork`** (o
baseline acima) e **`upstream`** (o `main`). Onde o `error-cases.md` cita um
caminho `<fork>/...`, é a árvore do baseline; `<upstream>/...` é este
repositório.

Os testes desta branch **não dependem** do baseline: os scripts e SQLs
necessários estão todos versionados aqui. O baseline é necessário apenas para
refazer a *comparação* entre as duas implementações — por exemplo o caso do
`ApexAqeListener` (#65), onde o ponto era justamente que cada lado falha no
teste do outro.

---

## Versões — as mesmas do `main`, de propósito

Todo teste registrado aqui rodou contra **exatamente os mesmos pins que o
`main` declara**. Nenhuma versão foi trocada para fazer um teste passar, e
nenhuma divergiu por acidente — o que vale dizer explicitamente, porque um
resultado obtido em versão diferente da que o time roda não transfere.

| Componente | Versão | Fixada em |
|---|---|---|
| **ClickHouse** | `clickhouse/clickhouse-server:24.8` | `infra/docker-compose.yml` |
| Spark | `apache/spark:4.0.1-scala2.13-java17-python3-ubuntu` (`SPARK_VERSION=4.0.1`) | `dev/.env.example` |
| MongoDB | `mongo:5.0.14-focal` | `infra/docker-compose.yml` |
| OTel Collector | `otel/opentelemetry-collector-contrib:0.156.0` | `infra/docker-compose.yml` |
| HyperDX | `hyperdx/hyperdx:2` | `infra/docker-compose.yml` |
| JDK (suíte `jar`) | 17 — imagem `sbtscala/scala-sbt:eclipse-temurin-jammy-17.0.10_7_1.10.4_3.5.2` | pin do próprio projeto |

O patch exato do ClickHouse observado nos testes foi **24.8.14.39** (a tag
`24.8` resolve para ele hoje). Onde a versão importa para o resultado, o
[`error-cases.md`](error-cases.md) cita a saída literal do servidor.

**Sobre o `26.1`:** ele aparece em uma linha do `error-cases.md` como
*comparação histórica*, não como ambiente de teste desta branch. O `24.8` é o
que roda aqui. Se o time decidir subir a versão do ClickHouse, o Caso 6.1 —
onde o `24.8` recusa `async_insert=1` com dedup em MV dependente (Code 344) —
é o primeiro a reexecutar, porque é o único achado registrado que depende
diretamente da versão.

---

## Antes de tudo: subir a infra

O pacote operacional que instala e sobe o stack completo **já está no `main`**
(PR #76, issue #62, mergeado em 18/08). Nada de branch extra:

```bash
git checkout main && git pull
make install       # macOS: instala pwsh, uv, Python 3.11 e Docker Desktop
                   # Windows: imprime os pré-requisitos, não instala
make bootstrap     # constrói e sobe as seis raias
make doctor        # verifica que subiu de verdade
make smoke         # roda o gate de produto de uma patologia
make status        # estado dos serviços
make down          # para, preservando volumes
```

Alvos disponíveis: `install`, `bootstrap`, `doctor`, `smoke`, `e2e`,
`tail-outlier`, `pilot-clean`, `status`, `down`.

O que foi de fato exercitado e o que não foi está registrado em
[`evidence/operational-package.md`](evidence/operational-package.md) —
`e2e`, `pilot-clean` e `install` **não** foram exercitados, e isso está
declarado lá em vez de presumido.

---

## Os testes, e como rodar cada um

### Suítes que já existem no repositório

Rodam sem nenhuma infraestrutura de pé:

```bash
make test            # todas as suítes (raias Python + jar + gate raiz)
make test-py         # só as raias Python
make test-jar        # jar, as 4 células de cross-build, JDK 17+ descoberto
make test-root       # só o gate raiz de seis raias
```

Resultado real desta jornada:

| Suíte | Comando | Resultado |
|---|---|---|
| `jar` (JVM) | `sbt -batch test` nas 4 células | **36/36**, 0 falhas |
| `engine` | `cd engine && uv run --extra dev pytest -q` | passou, exit 0 |
| `serve` | `cd serve && uv run --extra dev pytest -q` | passou, exit 0 |
| gate raiz | `cd engine && uv run --extra dev pytest ../tests -q` | **4 passed** |
| `verify` | `make test-verify` | **105/105** |
| `memory` | `python -m apex_memory index && python tools/recall_gate.py` | **15/18** (3 falhas de cold-start, por design) |

A suíte JVM do `jar` **nunca tinha rodado** antes — a imagem de build só executa
`sbt assembly`, nunca `sbt test`. Para rodar sem instalar `sbt` na máquina,
use a imagem fixada do próprio projeto:

```bash
MSYS_NO_PATHCONV=1 docker run --rm -v "$PWD/jar":/workspace -w /workspace \
  sbtscala/scala-sbt:eclipse-temurin-jammy-17.0.10_7_1.10.4_3.5.2 \
  sbt -batch test
```

### Reproduções específicas de cada achado

Cada script abaixo é autocontido — descobre o próprio diretório, não depende de
caminho absoluto nenhum.

| Script | Reproduz | Issue |
|---|---|---|
| [`scripts/test71_steady_state.sh`](scripts/test71_steady_state.sh) | propagação da MV em regime estável | #71 |
| [`scripts/test71_steady_state_v2.sh`](scripts/test71_steady_state_v2.sh) | idem, com janela de observação maior | #71 |
| [`scripts/test71_ts_hypothesis.sh`](scripts/test71_ts_hypothesis.sh) | a hipótese do `ts` — o teste que levou à retratação | #71 |
| [`scripts/repro-72-sql/`](scripts/repro-72-sql/) | DDL em ordem quebrada: MV antes da tabela alvo | #72 |
| [`scripts/ciclo1_concorrencia.sh`](scripts/ciclo1_concorrencia.sh) | duplicação sob retry, 10 clientes concorrentes | #63 |
| [`scripts/ciclo5_migracoes_reais_v2.sh`](scripts/ciclo5_migracoes_reais_v2.sh) | migrações aditivas + idempotência, 2 versões de ClickHouse | #60 |
| [`scripts/migrations-60/`](scripts/migrations-60/) | os 7 arquivos de migração usados acima | #60 |
| [`scripts/Dockerfile.sbt`](scripts/Dockerfile.sbt) | ambiente de build/teste da suíte JVM | #58 |

Os scripts usam containers descartáveis com credencial local fixa
(`apex`/`apex_local_dev`). Não é segredo de nada — é fixture de teste local, e
o container morre no fim. Nenhum deles toca em volume ou container de
desenvolvimento existente.

### Bench real do `verify`

O único teste desta lista que precisa da infra completa de pé e leva dezenas de
minutos:

```bash
cd verify
APEX_CANONICAL_CH_PASSWORD=... CLICKHOUSE_USER=... CLICKHOUSE_HOST=... \
  uv run --extra dev python scripts/run_replay.py --reps 3
```

Resultado real: `skew_split` disparou em **3/3** execuções do braço de
tratamento (`mechanism_confirmed`), mas o delta de runtime (+397%) caiu dentro
do piso de ruído medido (±44,8%) — veredito `runtime_unresolved`, exit 0.

Isso é o comportamento **correto**, não uma falha: a raia se recusa a certificar
uma magnitude que a escala do teste não sustenta. Ver
[`verify/README.md`](../../verify/README.md), seção "Verdicts".

---

## O que estas 11 issues tocaram — e o que não tocaram

Comparando cada branch contra `origin/main` por raia
(`git diff --stat origin/main..origin/<branch> -- <raia>`):

- **Tocadas** pelas PRs: `dev`, `infra`, `docs/architecture`, e raiz + `scripts/`
- **Não tocadas** por PR nenhuma: `jar`, `collect`, `engine`, `serve`,
  `memory`, `verify`, `contract`

Ou seja: todo o teste pesado feito nessas 7 raias **validou o código que já
existia**, não mudança nova. Está registrado aqui para não passar a impressão
de que testar muito equivale a mudar muito.
