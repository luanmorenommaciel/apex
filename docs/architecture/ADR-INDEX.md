# Índice canônico de ADRs

Este índice é o ponto de entrada para as decisões arquiteturais canônicas que
existem neste repositório. Ele facilita a leitura sem alterar a linhagem dos
documentos já publicados.

| ADR | Decisão | Status no documento | Documento canônico |
| --- | --- | --- | --- |
| ADR-001 | Sinal de cauda extrema para skew com alta paralelização | implementado e validado localmente | [ADR-001 — Tail outlier skew signal](ADR-001-TAIL-OUTLIER-SKEW-SIGNAL.md) |
| ADR-002 | Amostra de tasks bem-sucedidas sem reinterpretar o contrato | aceito e implementado | [ADR-002 — Successful task sample contract](ADR-002-SUCCESSFUL-TASK-SAMPLE-CONTRACT.md) |
| ADR-003 | AQE re-plan detection | accepted; PR #98 merged em 2026-09-14 | [ADR-003 — AQE re-plan detection](ADR-003-AQE-REPLAN-DETECTION.md) |
| ADR-004 | Source correlation privacy boundary | proposto; nenhuma implementação autorizada | [ADR-004 — Source correlation privacy boundary](ADR-004-SOURCE-CORRELATION-BOUNDARY.md) |

## Limite deste índice

Este arquivo **não renumera**, renomeia, reescreve nem substitui ADRs. Materiais
históricos podem reutilizar identificadores como `ADR-003` ou `ADR-004`; eles
não se tornam documentos canônicos por essa referência. Interprete cada menção
histórica no arquivo e no contexto que ela cita. Quando houver ambiguidade, use
os caminhos desta tabela e a linhagem documentada, em vez de inferir identidade
apenas pelo número.
