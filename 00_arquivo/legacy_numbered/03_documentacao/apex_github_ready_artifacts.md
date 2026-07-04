# Apex — Artefatos prontos para o GitHub

> Gerados seguindo o `CREW_A_OPERATING_STANDARD.md`. Cole cada bloco no lugar indicado.
> Fecham o ponto cego: tornar o trabalho v3 visível no tracking do time.

---

## A · ADR-004 — Desacoplamento dos geradores via contrato scenario.yaml

> Abrir como issue: título `[ADR-004] Decoupling generators via scenario.yaml contract`
> Labels: `crew-a` · `type:adr` · `phase:design` · `priority:p1`

```markdown
# ADR-004 — Desacoplamento do gerador de código e do gerador de plano

**Status:** proposto (para validação na sync)
**Data:** 06 jun 2026 · **Autor:** Augusto (Captain, Crew A)
**Responde a:** lição de casa do Commander — "como desacoplar o gerador de código do gerador de plano?"

## Contexto
Para testar os Watchers precisamos de event logs com anti-patterns conhecidos. No fluxo
acoplado, gerar um event log exige escrever o código E executá-lo no Spark — lento
(segundos a minutos por fixture) e serial, inviável para rodar a cada Pull Request.
A intuição inicial era que os geradores teriam que ser acoplados ("não existe Spark History
sem job"). A pergunta em aberto: dá para desacoplar?

## Decisão
Sim, via um **contrato declarativo** (`scenario.yaml`) que ambos os geradores leem de forma
independente — nenhum chama o outro:
- `code_generator` lê o contrato → emite o job PySpark com o anti-pattern;
- `plan_generator` lê o mesmo contrato → sintetiza o event log fiel, sem executar Spark;
- um `oracle` roda o job real periodicamente e valida que o sintético continua fiel.

A inversão que torna o desacoplamento possível: **não derivamos um artefato do outro**
(isso exigiria reimplementar o planner + AQE do Spark). Derivamos **ambos de uma
especificação compartilhada**.

## Consequências
**Positivas:** fixtures gerados em milissegundos; testes rodam a cada PR sem infra Spark;
código com bug e log com sinal correspondem por construção (mesmo `scenario_id`).
**Negativas / dívidas:** o sintético é um modelo — precisa do oráculo para não se descolar
da realidade. No ambiente 1-core, o SortMergeJoin colapsa em 1 task de reduce (AQE), então
o ratio numérico só é comparável com worker multi-core (próximo passo).

## Alternativas consideradas
- **Código → derivar history:** rejeitada. Exigiria simular o planner e o AQE do Spark.
- **Geradores acoplados (gerar code, executar, capturar log):** rejeitada. Lento, serial,
  incompatível com gate de PR.

## Evidência
Slice provado verde no plat-v0 (Spark 4.1.2), commit `357efad`, 25 testes passando.
```

---

## B · Captain's Report — Sync (formato internal-comms)

> Postar no canal da Crew A (Discord/Slack) e/ou como comentário na issue de coordenação.

```markdown
# Captain's Report — Crew A — 06 jun 2026

## Avançou
- Slice vertical do diagnóstico de skew: **verde de ponta a ponta** no plat-v0 (Spark 4.1.2 real). Contrato → código → log real → Watcher detecta → oráculo valida. (#17, #19, #20)
- CI gate por PR implementado: gera fixture, roda Watcher, exige acceptance. (#21)
- Hardening v3: band-aids removidos pela causa raiz (apexlib, stage-aware skew, AQE-aware, auto-zstd). 25 testes passando (13 novos + 12 do plat-v0). Commit `357efad`.

## Bloqueado
- Ratio numérico do oráculo só valida com worker multi-core. No 1-core o AQE colapsa o reduce em 1 task. Destrava com `spv0-spark-worker` em 2+ CPUs no compose.

## Precisa do Commander
- Confirmar se o acesso ao repo foi de fato desbloqueado para fechar a #28 (P0).
- Validar o ADR-004 (desacoplamento via scenario.yaml) — a lição de casa, respondida com código.
- Decidir timing do Spark Connect: proponho Sprint 2 (lane de correlação código↔execução), não o primeiro pedido.

## Honestidade
- O "verde" da v2 veio em parte de afrouxar checagens (divisão por zero mascarada, comparação de ratio desligada, tolerância inflada). Isso foi corrigido na v3 pela causa raiz, não escondido — e está documentado na spec.
- A detecção foi validada contra Spark real, não só contra o sintético. O run real ensinou 3 comportamentos do AQE (coalesce, runtime broadcast, plano final ≠ inicial) que mudaram o design do Watcher.
```

---

## C · Comentários de progresso nas issues

### Issue #17 — [FEATURE] Watcher / Classifier / Judger Pipeline
```markdown
## Progresso — 06 jun 2026
**O que avançou:** primeiro Watcher (Shuffle/Skew) implementado e detectando no log real do Spark 4.1.2.
**Evidência:** commit `357efad` · `watchers/skew_watcher.py` · GATE VERDE no log real do plat-v0.
**Estado:** pronto para review (Watcher de skew; faltam os demais do pipeline).
**Próximo passo:** Watcher de Memory/Cost (Pod A2) no mesmo padrão.
**Honestidade:** detecção validada contra Spark real, não só sintético. Lê o plano final pós-AQE.
```

### Issue #19 — [FEATURE] Local Bootstrap Platform (dataship-spark-plat-v0)
```markdown
## Progresso — 06 jun 2026
**O que avançou:** slice vertical rodando verde sobre o plat-v0 — job real submetido ao cluster, event log capturado do MinIO, Watcher consumindo.
**Evidência:** app `app-20260606030054-0000` · commit `357efad`.
**Estado:** plataforma validada para o fluxo de diagnóstico.
**Próximo passo:** escalar worker para 2+ cores para distribuição multi-task real.
```

### Issue #20 — [FEATURE] Performance Recommendation Engine
```markdown
## Progresso — 06 jun 2026
**O que avançou:** o Watcher já emite Finding estruturado com root cause + recomendações acionáveis (habilitar skewJoin, broadcast da dimensão, salt na chave), validado contra o bloco `acceptance` do contrato.
**Evidência:** commit `357efad` · saída do `skew_watcher.py` no log real.
**Estado:** primeira versão do motor de recomendação para o caso de skew.
```

### Issue #21 — [FEATURE] CI Integration (pre-merge code review)
```markdown
## Progresso — 06 jun 2026
**O que avançou:** `scenario-gate.yml` roda a cada PR — gera o fixture, roda os 13 testes do slice + o Watcher, exige acceptance verde antes do merge.
**Evidência:** commit `357efad` · `.github/workflows/scenario-gate.yml` · 25 testes passando.
**Estado:** gate funcional. É o "eval como teste" virando porteiro de merge.
```

### Issue #28 — [BLOCKER] GitHub repo access for Crew A members (P0)
```markdown
## Atualização — 06 jun 2026
Acesso ao repo foi desbloqueado — commit `357efad` (v3) já no `main`. @Commander, confirma
que o desbloqueio está completo para todos os membros da Crew A? Se sim, podemos fechar.
```
