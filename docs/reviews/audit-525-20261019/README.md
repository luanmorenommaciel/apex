# Estudo APEX — fechamento documental dos 525 IDs

Esta é a visão consolidada de Augusto para discussão do projeto. **525 fichas revisadas no escopo documental / 158 registros canônicos / nenhum novo aceite funcional concedido pela auditoria.** Não substitui a decisão dos pods, revisores ou mantenedor.

1. [Inventário navegável](INVENTARIO-525.md) — um destino por ID; [CSV](INVENTARIO-525.csv) e [JSON](INVENTARIO-525.json).
2. [Fichas completas em JSON](FICHAS-525.json) — os mesmos 14 campos das 525 fichas legíveis, divididas em 53 lotes no inventário.
3. [158 registros canônicos](REGISTRO-CANONICO-158.json) — origem histórica, destinos e ressalvas.
4. [Fontes e limites](FONTES-E-LIMITES.md) — o que esta publicação preserva e o que depende do acervo local.
5. [Estado atual e encaminhamentos dos 49 objetos públicos](../pod3-20261019/REGISTRO-ATUAL-49.md) — adendo posterior, não expansão do denominador 525.
6. [Revisão cruzada Claude/Kimi conferida pelo Codex](../pod3-20261019/CONFERENCIA-INDEPENDENTE.md) e [triagem da #185 do Agmar](../pod3-20261019/TRIAGEM-PR185.md).

Cada ficha explica identidade, intenção, implementação/limite, linhagem, fonte/corte, evidência, fluxo, risco, alternativas, dependências, critério de aceite proposto, comunicação, contracasos e próxima ação. O estado público é o do corte indicado; não uma consulta implícita em tempo real.

A análise original e as revisões auxiliares foram confrontadas pelo Codex, com divergências preservadas; consenso entre modelos não foi usado como prova. Gemini revisou a apresentação desta edição. Os encaminhamentos são propostas enquanto não houver decisão registrada. Não houve teste ou runtime de produto nesta publicação.

Para o Pod3, a entrada de discussão continua a [issue #181](https://github.com/luanmorenommaciel/apex/issues/181), que reúne a visão de Augusto. A PR documental #183 e esta edição são rascunhos para revisão; a existência de um arquivo no branch não significa integração na main.

## Planejamento e critérios

- [Roadmap e decisões](ROADMAP-FINAL-E-DECISOES.md).
- [Matriz de validação por ID](MATRIZ-VALIDACAO-POR-ID.csv).
- [Mapa de ações e linhagem](MAPA-ACOES-E-LINHAGEM-525.json).
- [Correções e limites históricos](D-CORRECOES-E-LIMITES.md).

O registro de 49 objetos é o corte público anterior à publicação desta edição. A nova PR documental da edição é um objeto posterior e não foi acrescentada retroativamente ao inventário original.

## Revalidação documental posterior dos PRs

Após a publicação inicial, os PRs foram recapturados para conferir reconhecimento de contribuições, atribuição e alcance das provas. 17 fichas receberam correções, complementos ou esclarecimentos de escopo (ver relação no relatório posterior); os resultados relatados continuam distintos de reprodução independente. A contagem original de 525 IDs não mudou. Veja [escopo, correções e relação de PRs](../pr-revalidation-20261019/README.md). Os cortes anteriores permanecem identificados; esta atualização não concede aceite funcional.
