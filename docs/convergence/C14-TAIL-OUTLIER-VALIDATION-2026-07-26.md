# C14 - Cobertura de cauda extrema com 100+ tasks

**Data:** 2026-07-26
**Branch:** `base-project-e2e-augusto`
**Status:** implementada e validada localmente; sem push

## Resultado

O contrato agora transporta `task_duration_max_ms` do listener JVM ate o
ENGINE. O sinal nao substitui p99: ele cria um candidato conservador apenas
quando o stage tem pelo menos 100 tasks, `p99/p50 <= 5` e `max/p50 > 10`.

O finding resultante e `warning`, confianca `MEDIUM`, detectado por
`tail_outlier_watcher`. Ele descreve cauda extrema e exige investigacao da
task, executor e distribuicao da chave; nao declara causa-raiz automaticamente.

## Evidencia real Spark 4.1.2

Probe controlado:

- app: `app-20260726045648-0001`;
- stage: `0`;
- tasks: `200`;
- p50: `1.229 ms`;
- p99: `4.901 ms`;
- max: `38.874 ms`;
- `p99/p50`: `3,988x`, abaixo do watcher canonico;
- `max/p50`: `31,631x`, candidato de cauda;
- ENGINE: 1 finding aceito, 0 rejeitados, 0 escritas e 0 chamadas LLM.

Log cru sanitizado:
[`evidence/p1-tail-outlier-real-e2e-2026-07-26.log`](../../evidence/p1-tail-outlier-real-e2e-2026-07-26.log).

## Tentativa que nao reproduziu a lacuna

O primeiro experimento usou o join de hot key real com 200 particoes,
app `app-20260726044042-0000`. Nesse ambiente ele produziu mais de uma task
lenta: no stage 6, `p99/p50=13,87x` e `max/p50=49,13x`. Portanto, o watcher
p99 ja detectava o caso e o gate de cauda esparsa recusou corretamente a
execucao.

Essa tentativa foi preservada como evidencia negativa em
[`evidence/p1-tail-outlier-hot-key-attempt-2026-07-26.log`](../../evidence/p1-tail-outlier-hot-key-attempt-2026-07-26.log).
O probe controlado foi necessario para isolar exatamente uma task extrema.

## Testes

- JVM Spark 4.1.2: 4/4 testes focais da matriz 8, 99, 100, 200 e 400 tasks;
- JVM Spark 4.1.2, suite integral: 8 testes em 4 suites, zero falhas;
- ENGINE: suite completa verde; dois testes opcionais pulados;
- pacote instalavel: 13 testes verdes;
- assertion DEV: 9 testes verdes;
- ClickHouse real: migration idempotente e candidato persistivel validados;
- imagem `apex-spark:4.1.2-local`: assembly novo construido e executado.

Evidencias:

- [`p1-tail-outlier-jar-spark41-2026-07-26.log`](../../evidence/p1-tail-outlier-jar-spark41-2026-07-26.log);
- [`p1-tail-outlier-jar-full-spark41-2026-07-26.log`](../../evidence/p1-tail-outlier-jar-full-spark41-2026-07-26.log);
- [`p1-tail-outlier-engine-tests-2026-07-26.log`](../../evidence/p1-tail-outlier-engine-tests-2026-07-26.log);
- [`p1-tail-outlier-package-dev-tests-2026-07-26.log`](../../evidence/p1-tail-outlier-package-dev-tests-2026-07-26.log);
- [`p1-tail-outlier-spark41-image-build-2026-07-26.log`](../../evidence/p1-tail-outlier-spark41-image-build-2026-07-26.log).

## Reproducao

Com a stack inicializada:

```powershell
.\scripts\apex.ps1 tail-outlier
```

O comando executa a prova em dry-run de findings, desabilita Crew/LLM e termina
com `APEX_TAIL_OUTLIER_GATE=passed`.

## Limite conhecido

Os baselines deterministas de 100, 200 e 400 tasks estao cobertos por testes.
Uma matriz de baselines Spark reais em diferentes tamanhos de cluster continua
util para calibracao estatistica, mas nao altera a lacuna matematica nem a
validacao funcional registrada aqui.
