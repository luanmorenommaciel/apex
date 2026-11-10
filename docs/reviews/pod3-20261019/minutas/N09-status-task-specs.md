# [Process][Governança] Definir como o status das Task-Specs reflete implementação e aceite

## Problema e intenção
As Task-Specs em `tasks/` declaram um status (`ready`, `in-progress`, `done`, `parked`), mas o status declarado nem sempre acompanha o que foi implementado e aceito. Um leitor pode tomar uma spec `ready` como trabalho livre quando já foi entregue, ou uma `done` como aceite. A intenção é um processo que separe status declarado, implementação na main e aceite registrado.

## Estado (declarações na main `c3c3ea3`)
- 87 specs e 19 manifestos de plano. Nas specs: 50 `done`, 26 `ready`, 10 `in-progress` e 1 `parked` ([T-20260923-console-auto-prefers-api](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/parked/T-20260923-console-auto-prefers-api.md)). Os manifestos de plano não declaram status.
- Três manifestos não são YAML válido ("mapping values are not allowed"): [l2-discover.yaml](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/l2-discover.yaml#L53), [serve-api-e2e.yaml](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/serve-api-e2e.yaml#L101) e [serve-api.yaml](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/serve-api.yaml#L20).
- Contagem de declarações não é revisão do conteúdo de cada spec.

## Decisão pendente
Quem atualiza o status (o autor junto com a entrega e um revisor confere, ou uma reconciliação periódica); o que conta como evidência para `done` (commit ou PR, mais o recibo do critério); e como registrar `parked` e `superseded` sem apagar histórico.

## Escopo e exclusões
Regra de status e um mapa por spec (spec → caminho → commit ou PR → critério → recibo → status proposto), preenchido aos poucos. Fora: marcar todas como `done`, reexecutar as specs, apagar specs para limpar a fila.

## Evidência e limite
Arquivo presente ou grep não provam comportamento; cada mudança de status precisa da sua própria conferência.

## Critérios de conclusão
- [ ] Regra de atualização de status registrada.
- [ ] Os três manifestos inválidos corrigidos como documento antes de qualquer reuso.
- [ ] Destinos distintos para `done`, `parked` e `superseded`.
- [ ] Mapa por spec concluído, com evidência por mudança.

## Como contribuir
Autores de specs podem comentar o estado real das suas, com o commit ou a PR correspondente.

Rastreabilidade do backlog: NOV-06, DEC-N7.
