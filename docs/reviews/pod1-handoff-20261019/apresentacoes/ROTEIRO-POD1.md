# Pod 1 / Front-end

Versão de 20/10/2026. Minha visão para discussão do time.

## 1. Pod 1 / Front-end

Esta é minha leitura para contribuir com o planejamento do time. Autoria da base compartilhada e limites das provas permanecem explícitos. O corte documental foi reconferido em 20/10/2026, com main c3c3ea3. Não representa liberação de release nem decisão oficial do pod.

Fontes: https://github.com/luanmorenommaciel/apex/issues/188 ; https://github.com/luanmorenommaciel/apex/blob/faf8b5723abd7cd0905137e574d515216f74d287/docs/reviews/pr-revalidation-20261019/README.md

## 2. A base compartilhada da Console

A Console e sua paridade são contribuições do Agmar. Na #100, dois commits substantivos têm autor Augusto Silva: 6dc476e e 5b4fc4f. Isso não transfere autoria da Console. Na #129, fab6620 é minha contribuição de integração após ajustes do Sidymar. A #182 implementa mudanças na branch, ainda fora da main.

Fontes: https://github.com/luanmorenommaciel/apex/blob/a296f1b3d93ba8ccba48d142be54f6b365c9746c/docs/reviews/pod1-handoff-20261019/ENTREGAS-E-AUTORIA.md ; https://github.com/luanmorenommaciel/apex/pull/100 ; https://github.com/luanmorenommaciel/apex/pull/129 ; https://github.com/luanmorenommaciel/apex/pull/153 ; https://github.com/luanmorenommaciel/apex/pull/182

## 3. Minhas entregas integradas no Front

Estas PRs estão integradas no recorte. #146 é teste no Serve relacionado ao consumidor Front. #129 é do Sidymar e não entra como PR própria minha. Os critérios e limitações completos estão no histórico. Nenhuma dessas provas foi reexecutada para a apresentação.

Fontes: https://github.com/luanmorenommaciel/apex/blob/a296f1b3d93ba8ccba48d142be54f6b365c9746c/docs/reviews/pod1-handoff-20261019/ENTREGAS-E-AUTORIA.md

## 4. Verify: estado e evidência mais claros

Os exemplos descrevem o antes/depois documentado. Não constituem nova reprodução do defeito. A acessibilidade foi tratada por componente no recorte, sem sessão nova de leitor de tela. A decisão de contrato do Verify permanece na #117.

Fontes: https://github.com/luanmorenommaciel/apex/blob/a296f1b3d93ba8ccba48d142be54f6b365c9746c/docs/reviews/pod1-handoff-20261019/EXEMPLOS-ANTES-E-DEPOIS.md ; https://github.com/luanmorenommaciel/apex/issues/117

## 5. A implementação do Agmar na #182

O corpo integral e os patches foram considerados na revalidação. Front 202 com 8 skip, Serve 456 e gate 17/17 são provas relatadas pelo autor, não executadas por nós nesta rodada. Três checks verdes e zero reviews formais no corte consultado não equivalem a aceite funcional.

Fontes: https://github.com/luanmorenommaciel/apex/pull/182 ; https://github.com/luanmorenommaciel/apex/blob/a296f1b3d93ba8ccba48d142be54f6b365c9746c/docs/reviews/pod1-handoff-20261019/EVIDENCIAS-DOS-ENCAMINHAMENTOS.md ; https://github.com/luanmorenommaciel/apex/blob/faf8b5723abd7cd0905137e574d515216f74d287/docs/reviews/pr-revalidation-20261019/README.md

## 6. Evidências existentes e próximo complemento

Não confundir jsdom/API, imagem com fixtures, curl e navegador real. Também não concluir ausência de E2E porque o auditor não o executou. O relato do Discord deve ser reconciliado com a árvore e o recibo antes de encerrar ou ampliar a #172.

Fontes: https://github.com/luanmorenommaciel/apex/blob/a296f1b3d93ba8ccba48d142be54f6b365c9746c/docs/reviews/pod1-handoff-20261019/EVIDENCIAS-DOS-ENCAMINHAMENTOS.md ; https://github.com/luanmorenommaciel/apex/issues/172 ; https://github.com/luanmorenommaciel/apex/pull/153 ; https://github.com/luanmorenommaciel/apex/pull/182

## 7. Integração de #182 com #158 e #159

A conferência confirmou referências a símbolos removidos nas superfícies de testes/gate. Não demonstrou conflito textual inevitável. Revisão de cada PR e teste de uma combinação são provas diferentes. Papéis e prazos devem ser confirmados pelo time.

Fontes: https://github.com/luanmorenommaciel/apex/blob/15ab9dc2b587cb187a0413843761db3ec256da4e/docs/reviews/pod3-20261019/COORDENACAO-PR-182.md ; https://github.com/luanmorenommaciel/apex/pull/158 ; https://github.com/luanmorenommaciel/apex/pull/159 ; https://github.com/luanmorenommaciel/apex/pull/182

## 8. Decisões do Front com Serve

O token entregue ao navegador não prova identidade individual. Resolver integrado de atribuição não é integração completa de um consumidor. Os estudos #179/#108/#180 não precisam entrar na mesma implementação. Recomendações e alternativas detalhadas estão no pacote.

Fontes: https://github.com/luanmorenommaciel/apex/blob/a296f1b3d93ba8ccba48d142be54f6b365c9746c/docs/reviews/pod1-handoff-20261019/PERGUNTAS-DE-DECISAO.md ; https://github.com/luanmorenommaciel/apex/blob/a296f1b3d93ba8ccba48d142be54f6b365c9746c/docs/reviews/pod1-handoff-20261019/IDEIAS-E-BACKLOG.md

## 9. Sequência proposta para o Pod 1

Esta sequência propõe preparação e alinhamento. Implementação, execução de stack ou nova validação de navegador exigem o escopo escolhido. Ninguém foi designado automaticamente. A prioridade final é do time.

Fontes: https://github.com/luanmorenommaciel/apex/blob/a296f1b3d93ba8ccba48d142be54f6b365c9746c/docs/reviews/pod1-handoff-20261019/DECISOES-E-PLANO.md ; https://github.com/luanmorenommaciel/apex/issues/188

## 10. Onde o time pode verificar

O catálogo do Pod 1 reúne 23 objetos atuais e relaciona 95 fichas originais. São referências documentais e não 95 entregas aceitas. Cada fonte mantém seu SHA e seu corte de prova. A leitura pode receber complementos do time.

Fontes: https://github.com/luanmorenommaciel/apex/issues/188 ; https://github.com/luanmorenommaciel/apex/pull/187 ; https://github.com/luanmorenommaciel/apex/pull/186 ; https://github.com/luanmorenommaciel/apex/blob/faf8b5723abd7cd0905137e574d515216f74d287/docs/reviews/pr-revalidation-20261019/README.md
