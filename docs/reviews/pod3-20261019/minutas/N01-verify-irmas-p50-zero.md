# [Study][Pod 1 / Verify] Decidir como tratar execuções irmãs com p50 efetivo zero no noise_floor

## Intenção e benefício
Tornar explícito o que o Verify faz quando uma execução irmã do mesmo stage tem p50 efetivo igual a zero, para que a checagem de estabilidade da razão p99/p50 não perca execuções sem avisar.

## Evidência e limite
Em `noise_floor()`, a checagem de instabilidade da razão entre execuções repetidas usa só as irmãs com `effective_task_duration_p50_ms > 0` ([guardrails.py:242](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/verify/src/apex_verify/guardrails.py#L242)) e precisa de pelo menos três razões. Uma irmã com p50 efetivo zero sai da conta sem registro; se sobrarem menos de três, a afirmação de instabilidade não é feita. O piso de verificabilidade, calculado pelo CV do runtime total, não usa esse filtro. O p50 efetivo vem da população de tarefas bem-sucedidas quando há amostras, ou da legada ([models.py:148-159](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/verify/src/apex_verify/models.py#L148-L159)).

Leitura estática na main `c3c3ea3`, conferida documentalmente; não houve nova execução. Não há relato de veredito errado; o filtro também evita divisão por zero na razão.

## Escopo e conexões
Escolher entre: manter a exclusão e documentá-la; manter a exclusão e informar quantas irmãs foram excluídas; ou tratar a irmã como dado inválido explícito. Não mudar a fórmula do piso nem o seletor de tentativa da #169. A #142 trouxe a população de tarefas bem-sucedidas; a #169 trata seleção de tentativa e população entre consumidores, sem este caso.

## Entrega e critérios de conclusão
- [ ] Decisão do owner do Verify entre as alternativas, com justificativa.
- [ ] Se houver mudança: teste com uma irmã de p50 efetivo zero que verifique o comportamento escolhido, e controle com todas as irmãs positivas inalterado.
- [ ] Se a escolha for informar, a mensagem do guardrail diz quantas irmãs foram excluídas.

## Perguntas e alternativas
Quando uma execução tem p50 efetivo zero: falta de tarefas bem-sucedidas, dado legado ou falha de coleta? A exclusão deve aparecer para quem lê o veredito?

## Como contribuir
Comente o recorte que pretende assumir antes de começar. Mudanças de contrato ou política precisam da decisão do mantenedor.

## Referências
- [verify/src/apex_verify/guardrails.py](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/verify/src/apex_verify/guardrails.py#L227-L260)
- [verify/src/apex_verify/models.py](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/verify/src/apex_verify/models.py#L148-L159)
- #142, #169

Rastreabilidade do backlog: F20.
