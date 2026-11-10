# [Decision][Cross-pod] Registrar as decisões de fronteira do ADR-004 (correlação de origem)

## Problema e intenção
O ADR-004 propõe uma fronteira de privacidade para ligar um stage à linha de código ou célula de notebook que o produziu (F4.1). O próprio ADR diz que nenhuma implementação está autorizada até o dono registrar cinco decisões. A PR #133 integrou o documento como proposta em 06/10; o merge não registra aceite. Esta issue dá um lugar visível para essas decisões.

## Estado
- [docs/architecture/ADR-004-SOURCE-CORRELATION-BOUNDARY.md](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/docs/architecture/ADR-004-SOURCE-CORRELATION-BOUNDARY.md#L3): "Status: proposed; no implementation is authorized by this document".
- A direção recomendada é um locator opcional, opt-in e relativo à raiz aprovada, sem stack trace bruto, caminho absoluto, URI, trecho de código ou texto de query em repouso; o fallback é uma referência opaca por instalação ([linhas 28-50](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/docs/architecture/ADR-004-SOURCE-CORRELATION-BOUNDARY.md#L28-L50)).
- O índice de ADRs já existe (#141); a numeração não é problema atual.

## Decisões pendentes (seção "Preconditions for implementation", [linhas 124-135](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/docs/architecture/ADR-004-SOURCE-CORRELATION-BOUNDARY.md#L124-L135))
1. Locators relativos ao repositório podem ficar em repouso?
2. Nome da configuração opt-in, semântica da raiz e sintaxe de caminho permitida.
3. Provedor de identidade de notebook e comportamento quando ele não existe.
4. Onde fica o payload (atributos ou colunas tipadas) e o plano de compatibilidade.
5. Primeiro consumidor público: Engine, Serve, Console ou só documentação.

## Escopo e exclusões
Registrar as cinco decisões e o novo status do ADR (aceito, revisado ou rejeitado), com justificativa. Fora: implementação, mudança de contrato ou DDL, captura de código-fonte ou stack trace bruto, intervenção em job em execução. A atribuição execution→stage da #115 não resolve correlação com arquivo, linha ou célula.

## Evidência e limite
Documento na main e registro da PR; nada foi executado. As decisões cabem ao dono registrado no ADR.

## Critérios de conclusão
- [ ] Status do ADR atualizado, com as cinco decisões e a justificativa de cada uma.
- [ ] Se aceito, uma Task-Spec separada referencia as decisões e a seção "Acceptance evidence" do ADR.
- [ ] Se rejeitado ou adiado, o motivo fica registrado no ADR.

## Como contribuir
Cada pod pode comentar o risco da sua lane: JAR, Collector e Infra sobre payload e redação; Serve e Console sobre como exibir um locator ou a ausência dele.

Rastreabilidade do backlog: P07, X03, DEC-11.
