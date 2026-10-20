# Pod 2 / Engine e interfaces — comece por aqui

O Engine já tem diagnóstico, telemetria retry-safe, resolvedor offline de atribuição e guardas. Augusto também contribuiu em Package/Harness/Infra; essas interfaces não mudam a identidade do Pod 2. A #185 é contribuição do Agmar/Pod 3 e deve ser aproveitada onde cobre o backlog, preservando autoria e critérios próprios.

**Situação deste pacote:** documentação para discussão em PR de rascunho, ainda não integrada na main. Base e evidências originais de 19/10/2026, main `c3c3ea3`; metadados e heads principais reconferidos antes da publicação. Checks e relatos conservam os seus próprios cortes.

## Três encaminhamentos para combinar

1. **Revisar a guarda de consistência do Engine.** Saída: Parecer da guarda bidirecional e identificação do residual: integração, evidência e/ou atualização do acompanhamento.
2. **Confrontar a interface R9D com a contribuição do Pod 3.** Saída: Mapa de argumentos ON/OFF, parâmetros aceitos, comando produzido e lacunas remanescentes. Separar os critérios #174 e #178.
3. **Desenhar um controle seguro do dispatcher PowerShell.** Saída: Especificação de teste com handlers inofensivos e controle negativo que troca Command mantendo Handler.

[Entradas, critérios e dependências de cada ação](DECISOES-E-PLANO.md). Papéis e prazos serão confirmados pelo time.

## O que precisamos decidir

Consumidor de atribuição #115, garantia do gate #123 e protocolo #113 são escolhas separadas. Preservação #174, ownership #175 e contratos #169/#170/#173 ficam em registros próprios; não precisam ser resolvidos todos numa reunião.

[Alternativas, recomendação e consequência de adiar](PERGUNTAS-DE-DECISAO.md).

## Resultado mínimo da reunião

Escolher **uma primeira revisão**, confirmar quem assume, registrar o critério de saída e combinar quando devolver o parecer. Se uma decisão não puder ser tomada, registrar o adiamento e o que falta para retomá-la. Não é necessário resolver todo o backlog nesta reunião.

## Leitura conforme a necessidade

- **Para apresentar:** [exemplos antes/depois](EXEMPLOS-ANTES-E-DEPOIS.md), [roteiro de 10 minutos](APRESENTACAO-10-MINUTOS.md) e [ata preenchível](ATA-MODELO.md).
- **Para revisar:** [evidências dos três encaminhamentos](EVIDENCIAS-DOS-ENCAMINHAMENTOS.md), [catálogo de PRs/issues](PRS-E-ISSUES.md) e [matriz de prova](MATRIZ-DE-EVIDENCIAS.md).
- **Para aprofundar:** [autoria e histórico](ENTREGAS-E-AUTORIA.md), [ideias/backlog](IDEIAS-E-BACKLOG.md) e [índice das fichas](INDICE-DE-FICHAS.md).

[Fontes e limites](FONTES-E-LIMITES.md). Não houve novo teste de produto nem novo aceite funcional nesta revisão editorial.
