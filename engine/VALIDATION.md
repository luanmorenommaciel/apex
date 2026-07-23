# Validação da Raia ENGINE

## Escopo

Este PR entrega o caminho determinístico da Apex: adaptação do evento de stage
do contrato v0.2, cinco watchers, `EvidenceValidator`, consulta ClickHouse
parametrizada e persistência de findings validados.

O Crew/Judge permanece fora deste recorte e não é necessário para detectar ou
persistir os cenários determinísticos.

## Contratos

- consome `apex.spark_events` e transições AQE por `job_id`;
- produz `Finding` v0.2 validado;
- persiste somente via inserção parametrizada no ClickHouse;
- trata conteúdo de plano e evidência como dados, não como instruções.

## Gate executado nesta branch

```powershell
cd engine
uv run --extra dev pytest
```

Resultado em 2026-07-23: **10 passed in 0.85s**.

Os testes cobrem schema do contrato, baseline negativo, detectores, validação
de evidência, query parametrizada e fronteira fake do ClickHouse.

## Evidência real de referência

A execução real anterior persistiu três findings para uma patologia e zero
findings para o baseline, sem LLM. Ela está documentada na branch de
convergência em `evidence/engine-c1-real-clickhouse-2026-07-22.log`.

Essa referência não substitui o gate local acima; a repetição contra a stack
integrada pertence ao PR7 de E2E, depois que as raias fundamentais forem
integradas.

## Limites e rollback

- Crew/Judge, aplicação de correções e UI não fazem parte deste PR.
- Não há segredo no código ou nos comandos de teste.
- Reverter o commit remove somente a raia `engine/` e não muda o contrato.
