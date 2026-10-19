# [Docs][Pod 1 / Verify] Atualizar o brief docs/lanes/VERIFY.md

## Intenção e benefício
Fazer o brief da lane Verify descrever a implementação atual, para que outro pod não planeje integração a partir de contagens e fontes antigas.

## Evidência e limite
[docs/lanes/VERIFY.md](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/docs/lanes/VERIFY.md) anuncia "105 tests" (linhas 5 e 159), diz que `executor_run_time_ms` não é coluna de `apex.spark_events` (linha 77) e que o Verify lê `apex.spark_events`, `apex.plan_transitions`, `apex.job_conf` e `apex.findings` (linhas 153-154). Na main, a migração 039 adiciona `executor_run_time_ms` (ver #179). As consultas SQL localizadas em `verify/` leem `apex.job_conf` ([config_source.py:72](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/verify/src/apex_verify/config_source.py#L72) e `apex.plan_transitions` ([run_replay.py:191](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/verify/scripts/run_replay.py#L191). Isso não demonstra que o Verify deixe de usar `spark_events` e `findings` por outro caminho, por exemplo dados passados pelo chamador. Conferir esse fluxo antes de concluir que a lista de fontes do brief está errada.

Leitura estática na main `c3c3ea3`, conferida documentalmente; não houve nova execução. A PR #164 corrige `verify/README.md`, não este arquivo.

## Escopo e conexões
Atualizar ou remover a contagem de testes, alinhar a frase sobre `executor_run_time_ms` com a decisão da #179 e descrever as fontes de dados conforme o fluxo conferido. Não muda código.

## Entrega e critérios de conclusão
- [ ] Decisão: atualizar o brief, apontar para o README ou remover a contagem.
- [ ] Fontes de dados descritas com referência ao código.
- [ ] A frase "Owns `apex.fix_verifications`" é fixada por [tests/test_telemetry_compatibility_matrix.py:121](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tests/test_telemetry_compatibility_matrix.py#L121); se mudar, ajustar a guarda na mesma PR.

## Como contribuir
Comente o recorte que pretende assumir antes de começar. Mudanças de contrato ou política precisam da decisão do mantenedor.

## Referências
- [docs/lanes/VERIFY.md](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/docs/lanes/VERIFY.md)
- #164, #179

Rastreabilidade do backlog: F19.
