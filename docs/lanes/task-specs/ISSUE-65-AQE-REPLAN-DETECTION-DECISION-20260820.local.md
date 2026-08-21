# Task-Spec local — issue #65: decisão sobre detecção de AQE re-plan

## Identidade e proveniência

- `task_spec_id`: `ISSUE-65-AQE-REPLAN-DETECTION-DECISION-20260820`
- `created_at_utc`: `2026-08-20T23:58:57Z`
- `base_ref`: `refs/remotes/origin/main`
- `base_commit_sha`: `50d596e1638a2323907fd11c2c7060aabb54ac83`
- `worktree`: `apex-issue65-aqe-decision-20260820`
- `worktree_mode`: `detached_clean`
- `issue`: `https://github.com/luanmorenommaciel/apex/issues/65`
- `issue_evidence_comment`:
  `https://github.com/luanmorenommaciel/apex/issues/65#issuecomment-5309840436`

## Objetivo

Consolidar a evidência já registrada na issue #65 em um único documento de
decisão e recomendar uma direção para o time, mantendo separadas a evidência
técnica e a decisão de produto.

## Escopo autorizado

1. Criar esta Task-Spec local.
2. Criar somente
   `docs/architecture/ISSUE-65-AQE-REPLAN-DETECTION-DECISION-20260820.md`.
3. Resumir `skew-count`, `edit-alignment` e o candidato combinado.
4. Registrar somente a evidência já publicada na issue #65.
5. Recomendar o candidato combinado, condicionado à aprovação do time.
6. Definir critérios de aceite para um PR futuro sem implementá-lo.
7. Validar links, estrutura Markdown, escopo e integridade dos dois documentos.
8. Parar e reportar `Status / Outcome / Proof / Gaps / Next / Open`.

## Evidência permitida

- A variante sem edit-alignment falhou em 3 de 5 testes de acurácia.
- A variante sem skew-count não compilou contra a especificação de precisão.
- O candidato combinado passou 34/34 testes nas quatro células de cross-build.
- O custo de alinhamento medido em JVM real foi 0,72 ms com 100 joins.
- Não há trace de produção com mais de aproximadamente 100 joins; resultados
  acima dessa escala são sintéticos e não constituem observação de produção.

## Estrutura obrigatória do documento de decisão

- contexto e escopo;
- evidência técnica separada da decisão de produto;
- comparação das três opções;
- recomendação explícita e condicionada;
- critérios de aceite para PR futuro;
- riscos e mitigações;
- rollback;
- decisão pendente e responsável pela decisão.

## Fora de escopo

- alterar código, testes existentes, JAR, Engine, schema, Docker ou CI;
- executar testes, builds, benchmarks, Spark, Docker ou qualquer runtime;
- implementar ou preparar o PR futuro;
- commit, push ou pull request;
- criar, editar ou comentar issue, PR ou qualquer recurso no GitHub;
- alterar qualquer arquivo além desta Task-Spec e do documento de decisão.

## Critério de aceite e parada

A atividade é aceita quando os dois arquivos autorizados forem os únicos itens
novos no worktree, o documento contiver todas as seções obrigatórias, seus
links forem resolvidos e a validação Markdown não encontrar erro estrutural.
Não há mutação operacional; rollback é remover os dois arquivos não commitados.
Parar imediatamente após a validação documental.
