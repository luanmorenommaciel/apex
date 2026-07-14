# Apresentacoes

## `apex-codex-solucao-end-to-end-2026-07-14.html`

Apresentacao da solucao Codex Round2 para o Commander: exemplo de skew real,
fluxo detectar -> preview -> apply_fix -> rerun -> limpo, stack autonoma,
SparkListener JVM, MCP subprocess smoke, aderencia L1-L9 e proximos passos.

Use esta apresentacao para explicar somente a nossa branch.

## `llm-solution-validation-2026-07-14.html`

Apresentacao comparativa do campeonato depois das rodadas novas: Codex Round2,
Cowork, Kimi, Codex antiga, Agmar/Spike e DataFlint. Mostra scorecard C1-C6,
matriz de evidencia, fluxos, riscos e recomendacao de composicao da V1.

Use esta apresentacao para debate de escolha/composicao entre engines.

## `llm-solution-validation-2026-07-13.html`

Versao historica do comparativo antes da rodada autonoma 14/07.

## `apex-v2-aqe-learnings.html`

Apresentacao tecnica para o time sobre a virada v1 -> v2 e os achados do AQE.

Ela registra tres aprendizados que continuam validos na v4 corrigida:

1. A linha do anti-pattern precisa ser derivada do codigo gerado, nao mantida manualmente.
2. O log sintetico precisa usar o schema real do Spark.
3. O Watcher deve ler a distribuicao das tasks e o plano executado, porque o AQE pode mudar o plano inicial.

Use esta apresentacao em syncs tecnicas. Use `docs/specs/skew-slice-v4.md` como referencia de implementacao e `docs/playbooks/skew-slice-v4.md` para reproducao.
