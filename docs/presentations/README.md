# Apresentacoes

## `apex-v2-aqe-learnings.html`

Apresentacao tecnica para o time sobre a virada v1 -> v2 e os achados do AQE.

Ela registra tres aprendizados que continuam validos na v4 corrigida:

1. A linha do anti-pattern precisa ser derivada do codigo gerado, nao mantida manualmente.
2. O log sintetico precisa usar o schema real do Spark.
3. O Watcher deve ler a distribuicao das tasks e o plano executado, porque o AQE pode mudar o plano inicial.

Use esta apresentacao em syncs tecnicas. Use `docs/specs/skew-slice-v4.md` como referencia de implementacao e `docs/playbooks/skew-slice-v4.md` para reproducao.
