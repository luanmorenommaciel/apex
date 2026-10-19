# Três manifestos YAML — correção documental preparada

Base: `c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874`. Os três arquivos originais falham em parse por escalares simples contendo dois-pontos seguidos de espaço. Os valores foram convertidos para blocos `>-`, preservando cada texto convertido. Nenhum comando descrito nos planos foi executado.

| Arquivo | Correção | Conferência |
|---|---|---|
| [tasks/.plans/l2-discover.yaml](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/l2-discover.yaml) | 1 escalar(es) protegido(s) | Parse YAML e igualdade textual dos escalares convertidos: PASS |
| [tasks/.plans/serve-api-e2e.yaml](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/serve-api-e2e.yaml) | 1 escalar(es) protegido(s) | Parse YAML e igualdade textual dos escalares convertidos: PASS |
| [tasks/.plans/serve-api.yaml](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/serve-api.yaml) | 3 escalar(es) protegido(s) | Parse YAML e igualdade textual dos escalares convertidos: PASS |

O recibo estruturado registra hashes e os campos modificados. A validade sintática permite revisão e futuro reuso; não aceita o plano, não atualiza status e não garante que os comandos sejam atuais ou adequados. Revisar o diff antes de integrar. Os manifests originais são inválidos, portanto não existe uma árvore YAML original válida para comparação semântica automática completa.

Critério de conclusão desta correção: sintaxe válida, textos convertidos iguais, diff restrito a representação YAML, status/aceites preservados. A ratificação da política fica no registro de governança separado.
