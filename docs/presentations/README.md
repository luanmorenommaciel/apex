# Apresentacoes

## `apex-product-readiness-2026-07-19.html`

Relatorio HTML de prontidao produto/Judge local da branch Codex Round2. Consolida
F7 remoto real-stack verde, MCP GUI real, T1 deterministico abaixo de 1s,
score `90/100`, before/after remoto e gaps conhecidos: Crew.ai/Judge real ainda
futuro e dependencia operacional de runner self-hosted preparado.

Use este artefato quando o juiz ou o Commander quiser uma leitura objetiva de
produto: o que ja esta provado, o que ainda falta, e quais evidencias sustentam
essa conclusao.

## `apex-codex-solucao-end-to-end-2026-07-15.html`

Apresentacao final da solucao Codex Round2 para o juiz e para o Commander:
G0-G6, workflow remoto verde, caso de uso skew, fluxo end-to-end, seguranca do
`apply_fix`, pacote de evidencias e proximos passos reais.

Use esta apresentacao para explicar somente a nossa branch no estado final
publicado em `6ba5238`.

## `llm-solution-validation-2026-07-15.html`

Apresentacao comparativa final do campeonato depois do G6 remoto verde:
Codex Round2, Cowork, Kimi, Agmar/Spike e DataFlint. Inclui pacote para o juiz,
scorecard C1-C6 atualizado e recomendacao de composicao da V1.

Use esta apresentacao para debate de escolha/composicao entre engines.

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
