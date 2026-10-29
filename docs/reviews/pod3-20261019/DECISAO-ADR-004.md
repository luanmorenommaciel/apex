# Registro de decisão — ADR-004 e correlação de origem

Estado: **proposta para discussão**. Decisor: dono indicado no ADR, a confirmar com o time. Responsável pela redação, revisor e data de decisão: **a confirmar**.

O [ADR-004](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/docs/architecture/ADR-004-SOURCE-CORRELATION-BOUNDARY.md#L3) está `proposed` e não autoriza implementação. O merge da #133 integrou a proposta. Este registro torna explícitas as cinco precondições das linhas 124–135 e preserva a possibilidade de revisar, adiar ou rejeitar.

| Decisão | Alternativas e impactos | Recomendação proposta | Resultado ratificado |
|---|---|---|---|
| 1. Locator relativo ao repositório em repouso | Opt-in relativo permite resolver origem; referência opaca por instalação reduz exposição, mas exige resolvedor local; adiamento preserva estudo | Avaliar direção opt-in do ADR com a fronteira de privacidade; referência opaca quando a instalação não autorizar locator | PENDENTE |
| 2. Configuração, raiz e sintaxe | Raiz aprovada explícita versus ausência de locator; definir nome de configuração, sintaxe, tamanho, frames externos e fallback | Sem raiz confiável ou frame permitido, retornar desconhecido; não persistir caminho absoluto, URI, home, código ou query. Nome da configuração ainda precisa ser escolhido | PENDENTE |
| 3. Identidade de notebook | Provedor explícito por plataforma; identidade opaca; desconhecido quando não houver provedor | Preferir identidade estável fornecida explicitamente; fallback desconhecido. Não inferir célula de stack trace | PENDENTE |
| 4. Payload e compatibilidade | Atributos versus colunas aditivas; cada escolha afeta contrato, Collector, store e consumidor | Comparar consumidores e migração antes da implementação. Registrar schema, compatibilidade e ausência de dados legados; não pressupor DDL | PENDENTE |
| 5. Primeiro consumidor público | Engine, Serve, Console, ou só documentação; consumo determina primeira entrega e prova | Manter estudo documental até confirmar consumidor e necessidade por stage; se houver, delimitar uma entrega pequena e sua prova | PENDENTE |

Cada recomendação é proposta. Adiar exige motivo e condição de retomada. Locator relativo ainda pode revelar metadados do projeto; um campo aditivo não comprova o fluxo completo nem pode ser usado automaticamente como identidade entre runs.

## Distinção da #115 e relações entre pods

A #115 trata execução SQL→conjunto de stages; o ADR trata stage→arquivo/linha/célula. Uma relação não resolve a outra. JAR/Engine, contrato, Collector e Infra avaliam emissão e armazenamento; Serve e Console avaliam exposição e ausência de locator. A decisão deve indicar quais lanes realmente entram no primeiro recorte.

## Registro a preencher

Para cada linha: alternativa escolhida; justificativa; limite; decisor; data; responsável pela próxima entrega; revisor; prazo combinado; link do registro no ADR/tracker. Nenhum campo está preenchido por atribuição automática de um assistente.

## Critérios de conclusão

- Cinco respostas, incluindo adiamentos justificados se houver.
- Status e justificativa do ADR atualizados pelo processo acordado; preserve o texto histórico da proposta.
- Se houver autorização de implementação: Task-Spec própria referencia as decisões, compatibilidade e a seção de evidência de aceite do ADR.
- Implementação dessa correlação aguarda as precondições; as PRs #157/#158/#159/#163 continuam com seus critérios próprios de revisão.

Redação consolidada a partir da minuta N07, fontes públicas e contribuição do Claude. Escolha de payload não deve ser deixada implícita para uma futura implementação.
