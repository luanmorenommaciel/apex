# Validação da Raia ENGINE

## Escopo

Este PR entrega o caminho determinístico da Apex: adaptação do evento de stage
do contrato v0.2, cinco watchers, `EvidenceValidator`, consulta ClickHouse
parametrizada e persistência de findings validados.

O Crew/Judge permanece fora deste recorte e não é necessário para detectar ou
persistir os cenários determinísticos.

## Contratos

- consome `apex.spark_events` e transições AQE por `job_id`;
- produz `Finding` v0.2 validado;
- persiste somente via inserção parametrizada no ClickHouse;
- trata conteúdo de plano e evidência como dados, não como instruções.

## Gate executado nesta branch

```powershell
cd engine
uv run --extra dev pytest
```

Resultado em 2026-07-23: **10 passed in 0.85s**.

Os testes cobrem schema do contrato, baseline negativo, detectores, validação
de evidência, query parametrizada e fronteira fake do ClickHouse.

## Evidência real de referência

A execução real anterior persistiu três findings para uma patologia e zero
findings para o baseline, sem LLM. Ela está documentada na branch de
convergência em `evidence/engine-c1-real-clickhouse-2026-07-22.log`.

Essa referência não substitui o gate local acima; a repetição contra a stack
integrada pertence ao PR7 de E2E, depois que as raias fundamentais forem
integradas.

## Limites e rollback

- Crew/Judge, aplicação de correções e UI não fazem parte deste PR.
- Não há segredo no código ou nos comandos de teste.
- Reverter o commit remove somente a raia `engine/` e não muda o contrato.

---

# Correção do watcher de skew (contrato v0.4, regras 1–3)

## O que estava errado

Três raias, independentemente, provaram três defeitos no `skew_watcher`:

1. **tipo fabricado** — o stage 4 de `app-20260724160310-0000` saiu como
   `SKEW_ON_JOIN` `critical`, mas seu plano lógico é um `!Aggregate` de metadados
   Delta **sem nenhum nó Join**, lê **0 bytes de shuffle** e move 278 bytes/task;
2. **limiar fixo de 5×/10×** — a regra correta é fechada:
   `tail-bound ⟺ p99/p50 > (n_tasks−1)/(slots−1)`. O volume se cancela. Os 21,62×
   celebrados precisavam de **> 49×** em 2 slots (são *work-bound*, uma correção
   perfeita devolve 0,0 ms);
3. **razão sem volume** — a razão era tratada como estatística em stages que
   movem quilobytes.

## O que passou a valer

`physics.py` (forma fechada) · `noise.py` (piso medido + atribuibilidade) ·
`jobconf.py` (largura observada + NO-OP check em `apex.job_conf`) · `plans.py`
(evidência de Join) · `context.py` (baselines por config e escala).

`slots` é **observação, nunca palpite**: `instances × cores` do `job_conf`, ou
`analyze(..., slots=)` / `$APEX_CLUSTER_SLOTS`, ou **UNKNOWN** — que limita a
confiança abaixo do gate e informa a largura de break-even. Neste cluster
standalone, **0 de 51** linhas de `job_conf` trazem `spark.executor.instances`,
então UNKNOWN é o caso normal.

## Gate executado

```bash
cd engine
.venv/bin/python -m pytest tests/ -p no:randomly
```

Resultado em 2026-07-28: **91 passed** (todos exceto `test_crew_gated.py` e um
teste pré-existente que falha igual no HEAD — o ambiente tem `ANTHROPIC_API_KEY`
real, então o caminho "sem chave" não é exercitável aqui; verificado em worktree
do HEAD).

## Evidência real — `analyze()` sobre os runs calibrados do dev

31 runs `app-2026072819*` (10M linhas, 8 slots, `shuffle.partitions=100`):

| tipo | antes | depois (largura do `job_conf`) | depois (`slots=8`) |
|---|---|---|---|
| `SKEW_ON_JOIN` | 78 | 15 | 14 |
| `TASK_SKEW` | 0 | 1 | 1 |
| `SPILL` | 35 | 35 | 35 |
| `MEMORY` | 9 | 9 | 9 |
| `AQE_REPLAN` | 5 | 5 | 5 |
| **total** | **127** | **65** | **64** |

Os 14 findings de skew que sobrevivem estão **todos** no stage do join
genuinamente enviesado (stage 21 com AQE off, stage 29 com AQE on). Os pisos de
ruído medidos por raia batem com os do dev: **32–59%** em 8 tasks (o dev mediu
37,7%) e **32,9%** no stage 21 com 100 tasks.
