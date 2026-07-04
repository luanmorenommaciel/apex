# LLM Evals — Apex Tiers 2–4

Comparações de LLMs para o pipeline de diagnóstico do Apex.

## Objetivo

Determinar qual LLM usar em cada tier, com base em:
- **Precisão** — acerto no diagnóstico de anti-patterns Spark
- **Latência** — tempo de resposta por chamada
- **Custo** — custo por diagnóstico
- **Raciocínio** — qualidade da explicação do root cause

## Tiers

| Tier | Função | LLM candidatos |
|---|---|---|
| Tier 2 · Classifier | Classifica o Finding e decide se escala | DeepSeek, Kimi, Gemini, GPT-4o-mini |
| Tier 3 · Coordinator | Orquestra diagnóstico completo (Sonnet baseline) | Claude Sonnet, Gemini Pro |
| Tier 4 · Judge | Segunda opinião em casos de baixa confiança (Opus baseline) | Claude Opus, GPT-4o |

## Estrutura de cada eval

```
docs/llm-evals/
├── README.md                 ← este arquivo
├── tier2-classifier/
│   ├── eval-deepseek.md
│   ├── eval-kimi.md
│   ├── eval-gemini.md
│   └── summary.md
├── tier3-coordinator/
│   └── ...
└── tier4-judge/
    └── ...
```

## Template de eval (por modelo)

```markdown
# Eval — {Modelo} — Tier {N}

**Data:** YYYY-MM-DD
**Cenário:** {scenario_id}
**Input:** Finding do Watcher

## Resultado
- Classificação correta: sim/não
- Root cause identificado: sim/não/parcial
- Recomendações acionáveis: sim/não

## Latência
- P50: Xms · P95: Xms

## Custo
- Input tokens: N · Output tokens: N · Custo: $X

## Raciocínio (trechos relevantes)
> ...

## Conclusão
- Adequado para Tier N? sim/não/condicional
- Observações: ...
```

## Status atual

| Modelo | Tier | Status |
|---|---|---|
| Claude Sonnet | Tier 3 | 🔵 em andamento |
| Claude Opus | Tier 4 | 🔵 em andamento |
| Gemini | Tier 2 | 🔵 em andamento |
| DeepSeek | Tier 2 | 🔵 em andamento |
| Kimi | Tier 2 | 🔵 em andamento |
| ChatGPT / Codex | Tier 2 comparativo | 🔵 em andamento |
