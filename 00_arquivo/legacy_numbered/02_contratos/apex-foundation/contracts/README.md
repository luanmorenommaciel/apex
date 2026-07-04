# contracts/ — as costuras do Apex

Esta pasta é o coração do projeto. Tudo aqui é um **acordo** entre componentes.
Mudar qualquer arquivo daqui afeta vários pods de uma vez — por isso, mudança em
`contracts/` exige uma decisão registrada (ADR) e review de todos os pods afetados.
Tudo o que está fora daqui pode mudar livremente, desde que continue respeitando estes acordos.

## Os quatro contratos do Apex

| Arquivo | O que combina | Quem produz | Quem consome |
|---|---|---|---|
| `apex-event.schema.json` | O formato de **um evento de telemetria** | Listener / Collector | Watchers |
| `clickhouse-schema.sql` | As **tabelas** onde os eventos pousam | Collector | Watchers (via SQL) |
| `apex-event-source.md` | A **interface** de onde os eventos vêm (trocável) | Listener (hoje) / leitor de log (depois) | Watchers |
| `watcher.contract.md` | O formato de um **achado** que todo watcher devolve | Watchers | Coordinator / Judge |

## A ideia em uma frase

> Os de cima (Listener/Collector) **prometem** entregar dados nesse formato.
> Os de baixo (Watchers/Coordinator) **podem confiar** que vão receber nesse formato.
> Os dois lados constroem em paralelo porque o aperto de mão já está combinado.

## Versionamento

Todo contrato tem versão (ex.: `apex-event v1`). Quando precisar mudar de forma que quebra
quem já usa, sobe a versão (`v2`) e mantém a `v1` viva até todos migrarem — nunca quebra
todo mundo de uma vez. (É o mesmo princípio da tomada: se mudar o padrão, você mantém o
adaptador antigo por um tempo.)
