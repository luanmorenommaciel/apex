# Governança proposta — status, implementação e aceite

Estado: **aguarda ratificação do mantenedor**. Autor da atualização, revisor e data de adoção: a confirmar. Piloto documental: [23 tarefas L1](MATRIZ-L1-23.md). Origem: N09; relaciona-se à #79 e à #181.

## Problema e estados distintos

`status` e `accepted` são campos declarados. Implementação exige localizar código e commit/PR. Aceite exige conferir o critério e o respectivo recibo. Review humana é um registro adicional: uma ferramenta escrever `accepted: true` não demonstra review independente.

Na base `c3c3ea3`, o inventário anterior registra 87 specs, 19 planos e estados declarados 50 done / 26 ready / 10 in-progress / 1 parked. Esta complementação conferiu diretamente o front matter das 23 specs L1 e das seis divergências listadas abaixo. Não recontou semanticamente todas as specs do repositório.

## Regra proposta para novas entregas

1. Quem assume um item informa responsável e tracker antes de mudar para `in-progress`.
2. Antes de propor `done`, preencher código/commit ou PR, critérios relevantes, recibos, limitações e tipo de aceite. O revisor confere a correspondência; o mantenedor ratifica a regra aplicável.
3. Para entrega documental, o critério é sua própria revisão/validação documental; não exigir runtime sem relação com a mudança.
4. Para `parked`, registrar motivo e condição de retomada. Para item substituído, registrar sucessor e motivo. Confirmar o vocabulário aceito pelo formato antes de introduzir um novo valor literal `superseded` no front matter.
5. Manter o histórico; não apagar specs, reexecutá-las automaticamente ou atualizar status em massa.

**Decisão de processo ainda aberta:** `done` deve exigir aceite registrado no mesmo fluxo, ou representar integração enquanto `accepted` permanece independente? Recomendação: manter os dois eixos explícitos e exigir recibos claros para comunicar “concluído e aceito”. Se o time exigir ambos para novos `done`, a regra deve ser escrita; não aplicá-la retroativamente apagando o histórico. Um legado `done/accepted:false` permanece assim até reconciliação específica, com nota factual de aceite não registrado.

## Divergências legadas conferidas nesta etapa

Os seis arquivos abaixo declaram `status: done` e `accepted: false` no snapshot. Isso não prova falta de implementação nem ausência de review em outro lugar.

| Spec em `tasks/done/` | Encaminhamento |
|---|---|
| T-20260820-tool-surface-six | Localizar critério, commit e recibo; manter ausência de aceite explícita até conferência |
| T-20260820-detail-parameter | Mesmo procedimento por ID |
| T-20260820-explain-stage-tool | Mesmo procedimento por ID |
| T-20260820-coverage-freshness | Mesmo procedimento por ID |
| T-20260820-critical-path | Mesmo procedimento por ID |
| T-20260820-l3-docs | Conferir o critério documental específico, sem exigir runtime por associação |

Fonte reproduzível: diretório [tasks/done na base consultada](https://github.com/luanmorenommaciel/apex/tree/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/done). Nenhum status desses arquivos foi alterado.

## Modelo por spec e correções sintáticas

Campos mínimos: ID; caminho; status declarado; `accepted`; implementação observada; PR/commit; critério; recibo; limite; proposta de destino; decisão; autor/revisor/data da atualização.

As correções dos três planos YAML estão preparadas separadamente da política: [recibo e limites](CORRECOES-YAML.md). O parse dos originais falhou; as versões corrigidas usam escalares `>-`, preservando os textos convertidos. Parser válido não aceita comportamento, não executa planos e não ratifica status.

## Conclusão

Concluir a adoção quando o mantenedor escolher a semântica dos estados, autor/revisor estiverem definidos, o piloto L1 tiver encaminhamento por ID e as correções de sintaxe forem revisadas. Tratar as seis divergências legadas com notas/recibos próprios, sem inventar aceite. Esta regra proposta não altera os critérios de merge das PRs de testes atuais.

Redação com contribuição do Claude; Codex corrigiu a ambiguidade entre exigir aceite para `done` e preservar `done` legado com aceite ausente.
