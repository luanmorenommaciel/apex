# Critérios C1–C6 e Gates G0–G6 (extrato para engines — sem scores de terceiros)

## Critérios de avaliação (pesos pré-registrados pelo Commander)

| Critério | Peso | O que mede |
|---|---|---|
| C1 Aderência à arquitetura V1 (premissas L1–L9 da spec) | 25% | construiu o que foi pedido |
| C2 Cobertura de detecção (anti-patterns com detector real) | 20% | além de skew: gc, oom, shuffle... |
| C3 Confiabilidade (validator, baseline negativo, anti-falso-positivo) | 15% | alerta falso mata a confiança |
| C4 Fechamento de loop no IDE (MCP + apply com backup/diff) | 15% | o diferencial do produto |
| C5 Qualidade de engenharia (testes, CI, config versionada, reprodutibilidade) | 15% | "done local ≠ done" |
| C6 Custo/latência (LLM opcional no caminho comum) | 10% | diagnóstico contínuo barato |

## Gates (critérios binários — detalhes e números de referência na spec §5)

G0 build+testes limpos · G1 baseline zero falso positivo · G2 todas as classes
detectadas nos scenarios oficiais · G3 sintético≈real no cluster (≥8 tasks) ·
G4 diagnóstico <1s sem LLM · G5 ciclo fix aplicado→job re-executado limpo ·
G6 oráculo agendado (drift).
