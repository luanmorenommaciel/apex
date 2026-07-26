# P1: cobertura de skew para 100+ tasks

**Status:** planejada, ainda sem implementacao
**Prioridade:** P1 - cobertura de deteccao
**Owner inicial:** Augusto / raia JAR + ENGINE

## Problema

O listener emite p50 e p99 por stage. Pelo nearest-rank atual, uma unica task
30x mais lenta pode nao alterar p99 quando o stage possui 100 ou mais tasks.
O watcher que usa somente `p99/p50` pode deixar de criar finding apesar da cauda
extrema existir.

## Escopo aceito

- emitir `task_duration_max_ms` de forma aditiva;
- atravessar JAR, OTLP, COLLECT, INFRA e ENGINE;
- criar regra complementar conservadora para `max/p50`;
- provar o caso real com 200 particoes e baseline saudavel.

## Fora de escopo

- renomear ou reinterpretar `task_duration_p99_ms`;
- elevar maximo isolado a causa-raiz critica sem corroboracao;
- usar LLM para fechar a lacuna matematica;
- alterar branches do Luan sem decisao explicita.

## Criterios de aceite

1. Eventos novos possuem `task_duration_max_ms`; eventos antigos seguem
   processaveis.
2. Um stage de 200 tasks com uma cauda 30x gera candidato observavel.
3. Baselines saudaveis de 100, 200 e 400 tasks nao geram finding novo.
4. `skew_split` AQE continua sendo evidencia forte independente.
5. Testes JVM, contrato, ClickHouse, ENGINE e E2E real passam.

## Evidencia atual

- Listener: `jar/src/main/scala/apex/ApexStageListener.scala`.
- Watcher: `engine/src/apex_engine/watchers/skew.py`.
- AQE independente: `engine/src/apex_engine/watchers/aqe.py`.
- Revisao de raciocinio: [ADR-001](../architecture/ADR-001-TAIL-OUTLIER-SKEW-SIGNAL.md).
