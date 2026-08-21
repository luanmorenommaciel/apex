# Issue #65 — decisão proposta para detecção de AQE re-plan

- Status: proposta, aguardando decisão do time
- Data: 2026-08-20
- Escopo: direção de design; nenhuma implementação incluída
- Fonte: [issue #65 — Design decision: AQE re-plan detection logic](https://github.com/luanmorenommaciel/apex/issues/65)
- Evidência consolidada: [Outcome Brief da issue #65](https://github.com/luanmorenommaciel/apex/issues/65#issuecomment-5309840436)
- Contrato local: [Task-Spec desta atividade](../lanes/task-specs/ISSUE-65-AQE-REPLAN-DETECTION-DECISION-20260820.local.md)

## Contexto

A issue #65 registra duas abordagens incompatíveis dentro da mesma função de
detecção de mudanças de plano causadas por Adaptive Query Execution (AQE). Uma
prioriza a contagem correta de partições com skew; a outra corrige o alinhamento
de joins quando há inserção ou remoção entre versões do plano. Um terceiro
candidato combina os dois comportamentos.

Este documento consolida a evidência já registrada e propõe uma direção. Ele
não altera o detector, não implementa um PR e não transforma evidência técnica
em aprovação de produto.

## Evidência técnica registrada

A evidência disponível na issue estabelece:

- No cross-test, a versão sem edit-alignment falhou em 3 de 5 testes de
  acurácia.
- A versão sem skew-count não compilou contra a especificação de precisão.
- O candidato combinado passou 34/34 testes nas quatro células de cross-build.
- O custo do algoritmo de alinhamento, medido em JVM real, foi 0,72 ms com 100
  joins.
- Não existe trace de produção disponível com mais de aproximadamente 100
  joins. Assim, o comportamento de custo acima dessa escala não foi observado
  em produção e qualquer conclusão nessa faixa depende de dados sintéticos.

Esses resultados sustentam compatibilidade funcional do candidato combinado
no conjunto testado e custo baixo na maior escala de produção observável hoje.
Eles não provam custo aceitável para planos de produção substancialmente
maiores nem substituem a escolha de produto sobre complexidade e risco.

## Opções consideradas

### 1. Skew-count

Preserva a contagem precisa de partições com skew, mas não incorpora o
alinhamento baseado em edições para inserções e remoções de joins. A evidência
cruzada mostra perda de acurácia: a versão sem edit-alignment falhou em 3 de 5
testes de acurácia.

Direção de produto associada: priorizar uma implementação mais restrita e a
semântica de skew-count, aceitando a lacuna conhecida de alinhamento.

### 2. Edit-alignment

Corrige o alinhamento de joins sob inserção e remoção, mas não preserva sozinho
o contrato de precisão do skew-count. A variante sem skew-count não compilou
contra a especificação de precisão.

Direção de produto associada: priorizar alinhamento estrutural, aceitando que o
contrato de precisão existente teria de ser redefinido ou recuperado em outra
mudança.

### 3. Candidato combinado

Combina skew-count e edit-alignment. É a única opção registrada que satisfez os
dois conjuntos de expectativas no cross-build: 34/34 testes nas quatro células.
Seu custo medido foi 0,72 ms com 100 joins em JVM real.

Direção de produto associada: preservar ambos os comportamentos, aceitando
maior complexidade de implementação e a incerteza de escala além dos traces de
produção disponíveis.

## Recomendação técnica

Recomenda-se explicitamente o candidato combinado, condicionado à aprovação do
time.

A recomendação decorre de ele ser o único candidato que preserva as duas
propriedades cobertas pela evidência cruzada, com custo medido baixo em 100
joins. A condição é material: o time precisa aceitar a complexidade adicional,
o risco de crescimento do custo de alinhamento e o limite da evidência de
produção antes de autorizar qualquer implementação.

## Decisão de produto

A decisão pendente não é “qual candidato passou os testes”; isso já pertence à
evidência técnica. A decisão de produto é se o APEX deve:

- preservar simultaneamente precisão de skew-count e alinhamento sob
  inserção/remoção;
- assumir a complexidade do candidato combinado;
- aceitar a evidência atual em aproximadamente 100 joins como suficiente para
  avançar, mantendo proteção explícita para escalas maiores.

Responsável pela decisão: time APEX. Até uma aprovação registrada, o candidato
combinado permanece recomendado, porém não aprovado e não aplicado.

## Critérios de aceite para um PR futuro

Um PR futuro somente deve ser considerado apto à revisão quando:

1. referenciar a decisão explícita do time e a issue #65;
2. limitar a mudança à lógica aprovada de detecção de AQE re-plan;
3. preservar tanto a contagem precisa de skew quanto o alinhamento correto sob
   inserção e remoção de joins;
4. incluir testes direcionados que falhem nas variantes isoladas e passem no
   candidato combinado;
5. passar os 34/34 casos nas quatro células registradas, ou uma suíte sucessora
   documentada que inclua integralmente esses comportamentos;
6. repetir a medição em JVM real com 100 joins e comparar o resultado com o
   baseline de 0,72 ms, usando um limite de regressão definido pelo time antes
   do merge;
7. incluir pelo menos um teste sintético de escala acima de 100 joins, rotulado
   como sintético e sem apresentá-lo como trace de produção;
8. documentar observabilidade, condição de abortar rollout e procedimento de
   rollback;
9. não alterar contratos, schema ou componentes não necessários à decisão sem
   aprovação separada.

Estes são critérios para um PR futuro. Nenhum deles é executado ou implementado
por esta proposta documental.

## Riscos e mitigação proposta

- Crescimento de custo: o alinhamento pode crescer de forma não linear. Mitigar
  com benchmark reproduzível em 100 joins, caso sintético maior e limite de
  regressão definido antes do merge.
- Cobertura de escala: não há trace de produção acima de ~100 joins. Não
  extrapolar o resultado medido como garantia; observar tamanho de plano e
  latência após eventual rollout.
- Complexidade combinada: preservar duas semânticas aumenta a superfície de
  manutenção. Mitigar com testes que explicitem separadamente skew-count,
  inserção, remoção e comportamento combinado.
- Variação entre versões do Spark: representações de plano podem mudar. Manter
  as quatro células de cross-build como piso de compatibilidade e registrar
  qualquer matriz sucessora.
- Falso senso de conclusão: 34/34 demonstra o conjunto testado, não todos os
  planos possíveis. Manter a decisão condicionada e evitar linguagem de prova
  universal.

## Rollback

Esta proposta não muda runtime; seu rollback imediato é descartar os dois
documentos locais não commitados.

Para um PR futuro aprovado, o plano de rollback deve ser restaurar a lógica
anterior por reversão do commit do detector, sem migração de dados ou schema.
O rollout deve ser interrompido se houver regressão de acurácia, incompatibilidade
entre células suportadas ou custo acima do limite previamente aprovado. Após a
reversão, a suíte de comportamento anterior deve ser executada para confirmar o
retorno ao baseline.

## Decisão pendente

O time deve escolher e registrar uma das três direções. Esta proposta recomenda
o candidato combinado, mas não concede aprovação para implementá-lo.

Pergunta de decisão: o time aprova o candidato combinado como base de um PR
futuro, sujeito aos critérios de aceite e às proteções de escala acima?
