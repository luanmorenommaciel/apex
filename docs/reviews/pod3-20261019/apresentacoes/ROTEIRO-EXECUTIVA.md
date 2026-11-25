# APEX / três pods

Versão de 20/10/2026. Minha visão para discussão do time.

## 1. APEX / visão executiva

Esta é minha leitura para contribuir com o planejamento do time. Autoria da base compartilhada e limites das provas permanecem explícitos. O corte documental foi reconferido em 20/10/2026, com main c3c3ea3. Não representa liberação de release nem decisão oficial do pod.

Fontes: https://github.com/luanmorenommaciel/apex/issues/181 ; https://github.com/luanmorenommaciel/apex/blob/faf8b5723abd7cd0905137e574d515216f74d287/docs/reviews/pr-revalidation-20261019/README.md

## 2. O que entrego para o time

A visão não substitui as entregas de Agmar, Sidymar, Luan e demais colaboradores. Separar contribuição própria, colaboração em outra PR, implementação em branch e proposta. Não usar contagens de fichas ou testes como medida de produtividade.

Fontes: https://github.com/luanmorenommaciel/apex/issues/181 ; https://github.com/luanmorenommaciel/apex/issues/188 ; https://github.com/luanmorenommaciel/apex/issues/190 ; https://github.com/luanmorenommaciel/apex/blob/faf8b5723abd7cd0905137e574d515216f74d287/docs/reviews/pr-revalidation-20261019/README.md

## 3. Contribuições por pod

Detalhes de autoria, SHAs e provas nos históricos por pod. fab6620 é colaboração na #129 de Sidymar, não uma PR própria. A evolução #121 é de Luan. A Console original permanece atribuída ao Agmar.

Fontes: https://github.com/luanmorenommaciel/apex/blob/a296f1b3d93ba8ccba48d142be54f6b365c9746c/docs/reviews/pod1-handoff-20261019/ENTREGAS-E-AUTORIA.md ; https://github.com/luanmorenommaciel/apex/blob/db2703c36e407883b610bdf0ed7fdef1dd689835/docs/reviews/pod2-handoff-20261019/ENTREGAS-E-AUTORIA.md ; https://github.com/luanmorenommaciel/apex/blob/15ab9dc2b587cb187a0413843761db3ec256da4e/docs/reviews/pod3-20261019/README.md

## 4. Pod 1: leitura fiel e operação da Console

As provas locais de Agmar devem ser reconhecidas. O E2E histórico usa jsdom/API e a imagem de produção tem prova em fixtures. O relato adicional nginx pede reconciliação do recibo, sem negar o trabalho nem repetir prova suficiente.

Fontes: https://github.com/luanmorenommaciel/apex/issues/188 ; https://github.com/luanmorenommaciel/apex/pull/187 ; https://github.com/luanmorenommaciel/apex/pull/182 ; https://github.com/luanmorenommaciel/apex/issues/172

## 5. Pod 2: diagnóstico e contratos verificáveis

As melhorias de runner não demonstram overhead aprovado ou encerramento automático do tail-outlier. As issues #115/#123/#113 têm critérios distintos. Interfaces com Package/Harness/Infra não redefinem os três pods.

Fontes: https://github.com/luanmorenommaciel/apex/issues/190 ; https://github.com/luanmorenommaciel/apex/pull/189 ; https://github.com/luanmorenommaciel/apex/pull/155 ; https://github.com/luanmorenommaciel/apex/pull/185 ; https://github.com/luanmorenommaciel/apex/issues/115 ; https://github.com/luanmorenommaciel/apex/issues/123

## 6. Pod 3: serviços compartilhados e integração

#157 é teste de payload sem normalizar campos. #163 depende dos helpers da #157. Oito tools atuais são analyze_run, compare_runs, explain_stage, list_runs, recall_similar_runs, search_kb, suggest_fix e verify_fix. #164 já cobre parte do alinhamento documental e deve ser reaproveitada.

Fontes: https://github.com/luanmorenommaciel/apex/issues/181 ; https://github.com/luanmorenommaciel/apex/pull/183 ; https://github.com/luanmorenommaciel/apex/pull/157 ; https://github.com/luanmorenommaciel/apex/pull/163 ; https://github.com/luanmorenommaciel/apex/pull/164

## 7. Integração entre os três pods

A integração não começa do zero. Ao mesmo tempo, API disponível não demonstra Ask completo, resolvedor offline não demonstra consumidor público e um runner melhorado não demonstra benchmark aceito. A sequência depende do caso priorizado pelo time.

Fontes: https://github.com/luanmorenommaciel/apex/pull/129 ; https://github.com/luanmorenommaciel/apex/pull/153 ; https://github.com/luanmorenommaciel/apex/pull/182 ; https://github.com/luanmorenommaciel/apex/pull/126 ; https://github.com/luanmorenommaciel/apex/pull/185 ; https://github.com/luanmorenommaciel/apex/issues/167

## 8. PRs abertas que pedem coordenação

Lista selecionada para a pauta, não inventário completo dos 15 abertos. #161/#162 também constam do estudo. O relatório de 93 PRs mantém fonte e alcance por item. Não houve merge nesta rodada.

Fontes: https://github.com/luanmorenommaciel/apex/blob/faf8b5723abd7cd0905137e574d515216f74d287/docs/reviews/pr-revalidation-20261019/README.md ; https://github.com/luanmorenommaciel/apex/pull/157 ; https://github.com/luanmorenommaciel/apex/pull/155 ; https://github.com/luanmorenommaciel/apex/pull/182 ; https://github.com/luanmorenommaciel/apex/pull/185

## 9. Sequência recomendada de discussão

Não existe prazo executivo inventado nem atribuição automática de pessoas. Adiar um estudo com motivo é um resultado válido. Alinhamento decide escopo e responsabilidade; execução posterior implementa e prova a fatia escolhida.

Fontes: https://github.com/luanmorenommaciel/apex/blob/a296f1b3d93ba8ccba48d142be54f6b365c9746c/docs/reviews/pod1-handoff-20261019/DECISOES-E-PLANO.md ; https://github.com/luanmorenommaciel/apex/blob/db2703c36e407883b610bdf0ed7fdef1dd689835/docs/reviews/pod2-handoff-20261019/DECISOES-E-PLANO.md ; https://github.com/luanmorenommaciel/apex/blob/15ab9dc2b587cb187a0413843761db3ec256da4e/docs/reviews/pod3-20261019/ATA-POD3-MODELO.md

## 10. Oportunidades com destino documentado

As 23 tarefas derivam da #79: duas done/accepted e 21 ready declaradas, com implementação e aceite analisados separadamente. #164 cobre parte do README. Minutas não equivalem a prioridades aprovadas. A política de governança permanece proposta.

Fontes: https://github.com/luanmorenommaciel/apex/blob/15ab9dc2b587cb187a0413843761db3ec256da4e/docs/reviews/pod3-20261019/MATRIZ-L1-23.md ; https://github.com/luanmorenommaciel/apex/blob/15ab9dc2b587cb187a0413843761db3ec256da4e/docs/reviews/pod3-20261019/DESTINOS-MINUTAS.md ; https://github.com/luanmorenommaciel/apex/blob/a296f1b3d93ba8ccba48d142be54f6b365c9746c/docs/reviews/pod1-handoff-20261019/IDEIAS-E-BACKLOG.md ; https://github.com/luanmorenommaciel/apex/blob/db2703c36e407883b610bdf0ed7fdef1dd689835/docs/reviews/pod2-handoff-20261019/IDEIAS-E-BACKLOG.md

## 11. Rastreabilidade e limites da entrega

Nos históricos a revisão é documental, não code review integral de todos os patches. Não houve nova execução de CI/runtime. As fontes primárias prevalecem sobre resumos e pareceres de modelos. Nenhuma garantia de ausência absoluta de omissões é alegada.

Fontes: https://github.com/luanmorenommaciel/apex/blob/faf8b5723abd7cd0905137e574d515216f74d287/docs/reviews/pr-revalidation-20261019/README.md ; https://github.com/luanmorenommaciel/apex/pull/186

## 12. Material para a conversa do time

Todos os índices representam minha visão para discussão, aberta a correções e complementos. Não são fonte exclusiva nem decisão oficial dos pods. As apresentações de cada pod aprofundam exemplos e próximas ações.

Fontes: https://github.com/luanmorenommaciel/apex/issues/188 ; https://github.com/luanmorenommaciel/apex/issues/190 ; https://github.com/luanmorenommaciel/apex/issues/181 ; https://github.com/luanmorenommaciel/apex/pull/186 ; https://github.com/luanmorenommaciel/apex/blob/faf8b5723abd7cd0905137e574d515216f74d287/docs/reviews/pr-revalidation-20261019/README.md
