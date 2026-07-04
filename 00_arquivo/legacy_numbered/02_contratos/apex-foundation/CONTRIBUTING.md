# Como contribuir no Apex

Estas são as regras de como o trabalho entra no projeto. Elas seguem o que o Commander definiu
e o fluxo SDD do AgentSpec.

## As regras inegociáveis

- A branch `main` é **protegida**: ninguém commita direto nela. Toda mudança entra por Pull Request.
- **Tudo vira issue antes de virar código.** Achou um problema (ex.: o Docker não builda)? Você
  não conserta na surdina — você abre uma issue. Princípio: deixe o codebase melhor do que encontrou.
- **Decisão se discute em issue, não no Discord.** Discord é pra conversa; o GitHub é a memória
  oficial. Toda decisão de arquitetura vira um ADR na pasta `docs/ADRs/`.
- **Mudança em `contracts/` é especial:** exige um ADR e review de todos os pods afetados, e mergeia
  antes dos pods adaptarem. Nunca quebre a costura no meio do caminho de todo mundo.

## O ciclo de um Pull Request (passo a passo)

1. **Pegue uma issue.** O trabalho começa por uma issue aberta — ela descreve o que fazer e por quê.
2. **Crie uma branch a partir da `main`**, nomeada pela feature:
   `feat/a1-shuffle-watcher`  ·  `fix/collector-backpressure`  ·  `docs/adr-linguagem`
3. **Implemente contra o contrato** (use Claude Code). Leia primeiro:
   `contracts/` (o formato dos dados) + o KB do tema + o `scenario.yaml` relevante.
4. **Rode os gates localmente** antes de abrir o PR: `make test` e `make scenario`.
5. **Abra o PR ligando à issue** (escreva "Closes #<numero-da-issue>" na descrição).
6. O **CODEOWNERS** chama o dono certo pra revisar; a **CI** roda os gates.
7. Com **CI verde + 1 aprovação** → squash merge na `main`.

## Os gates de merge (o que precisa passar)

Um PR só entra se passar por estes portões — são objetivos, não "achismo":

| Gate | O que verifica |
|---|---|
| **Lint / build** | O código compila e segue o estilo. |
| **Testes unitários** | Inclui os testes rápidos com Spark "de mentira" (sem subir cluster). |
| **Gate de cenário** | Se for um Watcher, ele TEM que detectar o anti-pattern plantado no `scenario.yaml`. |
| **1 review** | O dono da pasta (via CODEOWNERS) aprovou. |

> O gate de cenário é o coração da qualidade: você declara o bug num `scenario.yaml`, gera o
> código e o log do Spark com aquele bug, e o Watcher só passa se achar o bug. É o conceito de
> "eval como teste" que o Commander ensina, aplicado como porteiro do merge.

## PRs pequenos e frequentes

Prefira PRs pequenos que entram rápido a branches longas que vivem semanas e divergem da `main`.
Como cada pod trabalha na sua pasta e todos respeitam o contrato, PRs de pods diferentes não
conflitam — então pode mergear cedo e com frequência.
