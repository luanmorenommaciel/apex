# ADR-004 — Desacoplamento do gerador de código e do gerador de plano

**Status:** proposto (para validação na sync com Commander)  
**Data:** 06 jun 2026  
**Autor:** Augusto (Captain, Crew A)  
**Responde a:** pergunta do Commander — "como desacoplar o gerador de código do gerador de plano?"

---

## Contexto

Para testar os Watchers precisamos de event logs com anti-patterns conhecidos. No fluxo acoplado, gerar um event log exige escrever o código E executá-lo no Spark — lento (segundos a minutos por fixture) e serial, inviável para rodar a cada Pull Request.

A intuição inicial era que os geradores teriam que ser acoplados ("não existe Spark History sem job"). A pergunta em aberto: dá para desacoplar?

---

## Decisão

**Sim**, via um contrato declarativo (`scenario.yaml`) que ambos os geradores leem de forma independente — nenhum chama o outro:

- `code_generator` lê o contrato → emite o job PySpark com o anti-pattern
- `plan_generator` lê o mesmo contrato → sintetiza o event log fiel, sem executar Spark
- um `oracle` roda o job real periodicamente e valida que o sintético continua fiel

A inversão que torna o desacoplamento possível: **não derivamos um artefato do outro** (isso exigiria reimplementar o planner + AQE do Spark). Derivamos **ambos de uma especificação compartilhada**.

---

## Consequências

**Positivas:**
- Fixtures gerados em milissegundos
- Testes rodam a cada PR sem infra Spark
- Código com bug e log com sinal correspondem por construção (mesmo `scenario_id`)

**Negativas / dívidas:**
- O sintético é um modelo — precisa do oráculo para não se descolar da realidade
- No ambiente 1-core, o SortMergeJoin colapsa em 1 task de reduce (AQE), então o ratio numérico só é comparável com worker multi-core (próximo passo)

---

## Alternativas consideradas

- **Código → derivar history:** rejeitada. Exigiria simular o planner e o AQE do Spark inteiro.
- **Geradores acoplados (gerar code, executar, capturar log):** rejeitada. Lento, serial, incompatível com gate de PR.

---

## Evidência

Slice provado verde no plat-v0 (Spark 4.1.2), commit `357efad`, 25 testes passando.
