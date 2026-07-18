# ADR-003 - Spark Alvo Da Branch Codex

Status: proposta para Commander

Data: 2026-07-18

## Contexto

A branch Codex validou stack autonoma com Spark 4.0.0. A branch Agmar/Spike usa Spark 4.1.2. A V1 final precisa escolher uma versao alvo para reduzir divergencia entre engines.

## Decisao Proposta

Para esta branch Codex, manter Spark 4.0.0 como alvo reprodutivel local ja validado. Para a V1 composta, tratar Spark 4.1.2 do Spike como alvo de compatibilidade a ser testado antes da padronizacao final.

## Consequencias

- Nao quebramos evidencias G3/G5 autonomas ja obtidas.
- A decisao final de produto segue aberta para o Commander.
- Qualquer migracao para Spark 4.1.2 deve passar novamente por G3, G5 e G6.

## Evidencias

- `docker-compose.autonomous.yml`
- `evidence/g3-autonomous-diagnosis.json`
- `evidence/g5-autonomous-ciclo.log`
- `docs/architecture/llm-solution-validation-framework-2026-07-15.md`

