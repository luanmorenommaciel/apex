# Divisão de Responsabilidades – Apex

| Pod | Responsabilidade | Entregues | Próximos |
|-----|----------------|-----------|----------|
| Pod 1 | Coleta de logs (History Server + raw) | eventlog-loader (Go), schema ClickHouse | fingerprint do plano, fallback REST |
| Pod 2 | Geradores (código + plano) | skew_on_join_30x.yaml, code_generator, plan_generator | 11 cenários, run_real, CLI |
| Pod 3 | Oráculo / CI | esqueleto workflow, validação manual | comparador automático, gate de PR |
| A1 | Watcher Shuffle/Skew | (pendente) | consulta SQL para hot partition |
| A2 | Watcher Memory/Cost | (pendente) | detecção de spill/GC |
| A3 | Classifier (AST) | (pendente) | parser de código PySpark |
| A4 | Coordinator/Judge | (pendente) | thresholds, CrewAI |

## Alinhamento
- Issues no GitHub são fonte única.
- PRs exigem CI verde e revisão (CODEOWNERS).
- Daily + weekly syncs.
