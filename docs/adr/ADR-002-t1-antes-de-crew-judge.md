# ADR-002 - T1 Deterministico Antes De Crew/Judge

Status: aceita localmente

Data: 2026-07-18

## Contexto

O Commander pediu uma arquitetura agentica, mas a branch Codex mostrou que os gates principais devem permanecer reprodutiveis antes de adicionar LLM/Crew.ai. O caminho T1 foi medido em 226.991 ms sem LLM obrigatorio e passou com evidencias reais.

## Decisao

Manter T1 deterministico como primeiro nivel de diagnostico. Crew.ai/Judge deve entrar apenas como escalonamento quando:

- `confidence < 0.6`;
- o `EvidenceValidator` rejeitar ou marcar evidencia insuficiente;
- houver necessidade de explicacao narrativa ou julgamento de trade-off.

## Consequencias

- A branch continua barata, rapida e auditavel.
- LLM nao vira dependencia para G0-G6.
- Crew/Judge real permanece pendencia futura, registrada como CODEX-018.

## Evidencias

- `evidence/g4-t1.log`
- `apex/commander/judge_policy.py`
- `tests/test_commander_judge_policy.py`
- `evidence/g8-agentic-loop-python.log`

