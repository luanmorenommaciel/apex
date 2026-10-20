# Pod 1 / Front-end — comece por aqui

A Console já integra contribuições de várias pessoas. Augusto entregou correções do Verify, regras, acessibilidade, CI e integração; a Console original e a paridade são do Agmar, e a API principal é do Sidymar. Este pacote propõe uma revisão pequena da direção API-only e dos controles que precisam acompanhá-la.

**Situação deste pacote:** documentação para discussão em PR de rascunho, ainda não integrada na main. Base e evidências originais de 19/10/2026, main `c3c3ea3`; metadados e heads principais reconferidos antes da publicação. Checks e relatos conservam os seus próprios cortes.

## Três encaminhamentos para combinar

1. **Revisar a proposta API-only e preservar os testes.** Saída: Parecer por superfície Front/Serve, ordem de integração proposta e lista das duas adaptações dos testes.
2. **Escolher o perfil de exposição e custódia do token.** Saída: Registro de decisão por ambiente: exposição de docs/OpenAPI e lugar de custódia do token, com motivo e eventual adiamento.
3. **Preparar o protocolo da prova HTTP no navegador.** Saída: Protocolo com rotas, dados, passos, recibos esperados e exclusões. Sem executar navegador, stack ou serviços nesta preparação.

[Entradas, critérios e dependências de cada ação](DECISOES-E-PLANO.md). Papéis e prazos serão confirmados pelo time.

## O que precisamos decidir

Direção e ordem da #182 com #158/#159; perfil de token na #171; reconciliação das provas existentes e eventual residual da #172. **Ask #122 é uma decisão separada**, assim como a próxima fatia de contrato #117/#115 e os estudos.

[Alternativas, recomendação e consequência de adiar](PERGUNTAS-DE-DECISAO.md).

## Resultado mínimo da reunião

Escolher **uma primeira revisão**, confirmar quem assume, registrar o critério de saída e combinar quando devolver o parecer. Se uma decisão não puder ser tomada, registrar o adiamento e o que falta para retomá-la. Não é necessário resolver todo o backlog nesta reunião.

## Leitura conforme a necessidade

- **Para apresentar:** [exemplos antes/depois](EXEMPLOS-ANTES-E-DEPOIS.md), [roteiro de 10 minutos](APRESENTACAO-10-MINUTOS.md) e [ata preenchível](ATA-MODELO.md).
- **Para revisar:** [evidências dos três encaminhamentos](EVIDENCIAS-DOS-ENCAMINHAMENTOS.md), [catálogo de PRs/issues](PRS-E-ISSUES.md) e [matriz de prova](MATRIZ-DE-EVIDENCIAS.md).
- **Para aprofundar:** [autoria e histórico](ENTREGAS-E-AUTORIA.md), [ideias/backlog](IDEIAS-E-BACKLOG.md) e [índice das fichas](INDICE-DE-FICHAS.md).

[Fontes e limites](FONTES-E-LIMITES.md). Não houve novo teste de produto nem novo aceite funcional nesta revisão editorial.

## Esclarecimento após revalidação das PRs

A #182 já implementa as mudanças na branch do Agmar e apresenta provas locais; está aberta e ainda fora da main. Há também E2E histórico de jobs reais até o App, registrado pela #153. A próxima ação da #172 começa pela conferência dessas provas e do relato adicional de nginx, para identificar somente eventual complemento. A ausência de reprodução nesta auditoria não deve ser lida como ausência do trabalho do autor. Veja [evidências e seus cortes](EVIDENCIAS-DOS-ENCAMINHAMENTOS.md).
