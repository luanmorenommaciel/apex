# Plano: cobertura de skew por cauda extrema

## Ordem de implementacao

1. **Contrato e JAR**
   - adicionar `task_duration_max_ms` em `ApexStageEvent`, atributos OTLP e
     `ApexOtelSink`;
   - emitir `durs.lastOption.getOrElse(0L)` no listener;
   - testar nearest-rank e max para 8, 99, 100, 200 e 400 tasks.

2. **COLLECT e INFRA**
   - adicionar coluna aditiva nas copias canonicas de `spark_events`;
   - criar migration segura para ClickHouse existente;
   - projetar o atributo na materialized view de reshape;
   - manter rollups existentes, salvo necessidade comprovada de dashboard.

3. **ENGINE**
   - adicionar o campo aos modelos e leitura ClickHouse;
   - manter o watcher p99 atual;
   - adicionar avaliacao de cauda extrema somente para `task_count >= 100`;
   - emitir aviso/confiança media enquanto nao houver corroboracao AQE.

4. **Testes em camadas**
   - unitarios JVM e ENGINE;
   - contrato e migration ClickHouse;
   - telemetria OTLP para o novo atributo;
   - compatibilidade de linhas antigas sem max;
   - regressao dos gates existentes.

5. **Prova real e calibracao**
   - executar `skew_join` com 200 particoes e AQE desligado;
   - registrar p50, p99, max, finding e ausencia/presenca de AQE;
   - repetir baseline saudavel com 200 e 400 particoes;
   - ajustar limiar somente a partir desses dados, nunca para forcar verde.

## Resultado esperado

O produto diferencia distribuicao degradada (`p99/p50`) de cauda extrema
(`max/p50`), preserva compatibilidade e deixa claro quando o diagnostico e
heuristico ou confirmado pelo proprio Spark.

## Modelos sugeridos

| Etapa | Modelo |
|---|---|
| ADR, issue, plano e revisao de resultados | Terra Medio |
| Mudanca transversal e testes | Sol Medio |
| Revisao de politica/severidade antes de PR | Sol Alto, se necessario |
