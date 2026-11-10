# Exemplos de contribuição — Pod 2 / Engine e interfaces

Exemplos para explicar o benefício, com autoria e limite. Fonte detalhada: [histórico e autoria](ENTREGAS-E-AUTORIA.md). Antes/depois descreve a intenção e a alteração documentada, não uma reprodução de defeito nesta rodada.

## Telemetria retry-safe e retry pressure

- **Antes:** Retries e reachability precisavam ser representados sem inferir uma causa não demonstrada.
- **Depois:** Campos e watcher determinístico foram incorporados, com controles de tentativas e limites de interpretação.
- **Contribuição:** Augusto (`gustocezar`), [#89](https://github.com/luanmorenommaciel/apex/pull/89), [commit c731aca](https://github.com/luanmorenommaciel/apex/commit/c731acae2559812bdbee197c580b42b262f2e317).
- **Prova e limite:** PR de Augusto; não prova causa raiz nem reconcilia automaticamente status das Task-Specs.

## Resolvedor offline de atribuição

- **Antes:** Faltava um resolvedor puro para representar execução, app/job, stages, conflito e ausência.
- **Depois:** O resolvedor passou a separar esses resultados e tem controles para escopo, zero, ausência e tentativas.
- **Contribuição:** Augusto (`gustocezar`), [#126](https://github.com/luanmorenommaciel/apex/pull/126), [commit 4ddb082](https://github.com/luanmorenommaciel/apex/commit/4ddb082cf8e916736e336d6a5554bccbba083a19).
- **Prova e limite:** PR de Augusto; integração pública de um consumidor continua na #115.

## PowerShell explícito e plano único

- **Antes:** A presença de pwsh era assumida; o plano de ação precisava ficar explícito.
- **Depois:** CI passou a exigir PowerShell e o dispatcher ganhou plano único com Handler/Command.
- **Contribuição:** Augusto (`gustocezar`), [#128](https://github.com/luanmorenommaciel/apex/pull/128), [commit 2b84c7a](https://github.com/luanmorenommaciel/apex/commit/2b84c7a14fbcc5c009a3366536ccb80ebe316ca0).
- **Prova e limite:** PR de Augusto; comparar Handler em DryRun não prova execução de Command, residual da #124.

## Preflight de schema no database configurado

- **Antes:** Engine precisava detectar schema atrasado antes de seguir com consultas.
- **Depois:** O preflight consulta system.columns no database configurado e identifica incompatibilidades.
- **Contribuição:** Augusto (`gustocezar`), [#131](https://github.com/luanmorenommaciel/apex/pull/131), [commit 7b7b9b4](https://github.com/luanmorenommaciel/apex/commit/7b7b9b41aafa9b6fd3d45513ec7a8f394f9318fc).
- **Prova e limite:** PR de Augusto; não provisiona outro database nem demonstra schema real em todo ambiente.

## Guard SQL versus DDL mais discriminante

- **Antes:** job_id e attributes estavam entre exclusões que podiam ocultar colunas efetivamente lidas.
- **Depois:** Esses dois nomes foram retirados de NOT_COLUMNS e controles foram acrescentados.
- **Contribuição:** Augusto (`gustocezar`), [#139](https://github.com/luanmorenommaciel/apex/pull/139), [commit 087ce22](https://github.com/luanmorenommaciel/apex/commit/087ce22947e60525913c62fba3a49585e46bb32a).
- **Prova e limite:** PR de Augusto; a allowlist restante não foi removida. Não verifica o DDL instalado em runtime.

## Interface com outros pods

A #185 é proposta do Agmar, relacionada à interface com o Pod 3. Relaciona-se a parte dos argumentos da #167 e temas S3A/runners, sem transferir autoria ao Pod 2. O pacote operacional e Infra são interfaces explicitadas; o Pod 2 continua identificado como Engine.
