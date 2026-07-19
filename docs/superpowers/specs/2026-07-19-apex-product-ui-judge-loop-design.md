# Apex Product UI + Judge Loop Design

Data: 2026-07-19

Branch: `codex-round2`

## Objetivo

Transformar o gap restante em uma esteira incremental de produto sem quebrar o
nucleo que ja passou nos gates: T1 deterministico, EvidenceValidator,
`apply_fix` guardado, rerun e comparacao de telemetria.

O foco imediato nao e colocar Crew.ai no caminho critico. O foco e tornar a
solucao demonstravel para o Commander/Juiz como produto:

```text
evidencia real -> score de prontidao -> explicacao judge local
-> relatorio UI estatico -> proximo passo seguro
```

## Decisao

1. Criar primeiro uma UI/relatorio HTML estatico, gerado localmente, sem LLM.
2. Usar um Judge local deterministico para explicar o estado e as lacunas.
3. Manter Crew.ai/Judge real como provider futuro e opcional.
4. Nunca permitir que Judge/Crew aplique mudanca diretamente.

## Fluxo Do Slice UI-1

```text
evidence/f7-remote-real-stack-run-29671461366-loop.log
evidence/g6-mcp-ide-gui-smoke-2026-07-18.log
evidence/g4-t1.log
ISSUES.md
  -> product_report.py
  -> readiness score
  -> HTML local
  -> docs/presentations/apex-product-readiness-2026-07-19.html
```

## Componentes

| Componente | Responsabilidade |
| --- | --- |
| `apex.commander.product_report` | Ler evidencias, montar snapshot e renderizar HTML |
| `tools/generate_product_report.py` | CLI local para gerar o relatorio |
| `tests/test_commander_product_report.py` | Regressao de parsing, score e HTML |
| `docs/presentations/apex-product-readiness-2026-07-19.html` | UI estatica inicial para apresentacao |

## Judge Local

O Judge local nao chama LLM. Ele classifica sinais observaveis:

- F7 remoto verde;
- MCP GUI real verde;
- T1 menor que 1s;
- Crew.ai real ausente;
- runner self-hosted como dependencia operacional.

Saida esperada:

```json
{
  "status": "ready_for_judge_with_known_gaps",
  "score": 90,
  "strengths": ["remote_real_stack_green", "..."],
  "gaps": ["crew_judge_real_missing", "..."],
  "next_actions": ["decide_runner_lifecycle", "..."]
}
```

## Criterios De Aceite

- O relatorio HTML deve ser gerado sem rede e sem LLM.
- Deve citar app ids before/after do F7 remoto.
- Deve mostrar finding_count e max_skew_ratio antes/depois.
- Deve mostrar lacuna Crew.ai/Judge real como gap honesto.
- Deve ter teste unitario de parsing e renderizacao.

## Proximos Loops

1. UI-1: relatorio HTML estatico local.
2. UI-2: dashboard local simples lendo store/evidence.
3. Judge-1: provider deterministico com contrato explicito.
4. Judge-2: provider Crew.ai opcional, desligado por padrao.
5. Product-1: fluxo guiado para demo do Commander.
