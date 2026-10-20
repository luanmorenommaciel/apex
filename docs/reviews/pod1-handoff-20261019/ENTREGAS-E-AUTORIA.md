> Para leitura rápida: [cinco exemplos antes/depois](EXEMPLOS-ANTES-E-DEPOIS.md). Abaixo fica o histórico detalhado com o corte da Parte 10.

# Contribuições integradas e autoria — Pod 1 / Front-end

O histórico a seguir confirma presença/merge e autoria do objeto; não concede novo aceite funcional nem reproduz testes. Colaborações na PR de outra pessoa são discriminadas abaixo. O usuário gustocezar é Augusto; quem fez merge não é automaticamente autor da implementação.

| PR | Autor da PR | Head | Merge | Entrega / papel |
|---|---|---|---|---|
| [#97](https://github.com/luanmorenommaciel/apex/pull/97) | gustocezar | `4a2678177f` | `889ac9df0d` em 2026-09-14T16:18:08Z | docs(ui): define read-only Compare, Memory, and Verify contracts |
| [#100](https://github.com/luanmorenommaciel/apex/pull/100) | agmarcastro | `5b4fc4f1e0` | `8d3efa700d` em 2026-09-14T16:20:13Z | feat(front): Apex Console — the seven screens as a runnable Vite + React app |
| [#118](https://github.com/luanmorenommaciel/apex/pull/118) | gustocezar | `a8ccc52e8a` | `fbacbf0261` em 2026-09-14T16:20:47Z | fix(front): isolate /verify source states and async selections (I1) |
| [#119](https://github.com/luanmorenommaciel/apex/pull/119) | gustocezar | `0f1971255d` | `189b3c6801` em 2026-09-14T16:21:10Z | fix(front): present /verify proposals and evidence faithfully (I2) |
| [#120](https://github.com/luanmorenommaciel/apex/pull/120) | gustocezar | `961e296b19` | `dc9f22e8f8` em 2026-09-14T16:21:23Z | fix(front): expose original proposal as named region |
| [#129](https://github.com/luanmorenommaciel/apex/pull/129) | sidymar | `fab662080d` | `83a9624bce` em 2026-10-06T19:56:50Z | feat(serve): apex-api — one HTTP layer between ClickHouse and its consumers |
| [#136](https://github.com/luanmorenommaciel/apex/pull/136) | gustocezar | `2fa0781047` | `b758f17979` em 2026-10-06T20:11:54Z | fix(front): keep mechanism and runtime verdicts independent |
| [#137](https://github.com/luanmorenommaciel/apex/pull/137) | gustocezar | `2c3ae4bdae` | `9acfcb2fe7` em 2026-10-06T20:11:58Z | fix(front): recognize retry pressure findings |
| [#138](https://github.com/luanmorenommaciel/apex/pull/138) | gustocezar | `4b5798d5a2` | `9763b2f413` em 2026-10-06T20:12:02Z | ci(front): reject warnings and empty suites |
| [#146](https://github.com/luanmorenommaciel/apex/pull/146) | gustocezar | `2e0e1023e2` | `59967a3c8a` em 2026-10-06T20:11:28Z | test(serve): pin fix_verifications projection parity with the front |
| [#151](https://github.com/luanmorenommaciel/apex/pull/151) | gustocezar | `488bd8aed0` | `9cd2b86229` em 2026-10-06T20:11:50Z | fix(front): render API error detail only when textual |
| [#153](https://github.com/luanmorenommaciel/apex/pull/153) | agmarcastro | `eb449cbec5` | `c9c35cf06f` em 2026-10-06T20:32:30Z | fix(serve,front): the console reads the same rows through either door |

## Leitura por contribuição

### #97 — docs(ui): define read-only Compare, Memory, and Verify contracts

Definir os contratos de leitura das telas Compare, Memory e Verify: estados obrigatórios, fronteiras de evidência, tratamento de conteúdo não confiável e política de fixtures, sem implementar nada.

**Implementação e limite:** Feito como documentação: `docs/architecture/UI43-B-COMPARE-MEMORY-VERIFY-READ-ONLY.md` (+100) e a Task-Spec homônima (+145). É o documento que o fechamento do #43 cita como entrega do spike. O corpo lista decisões do dono pendentes antes de implementar (stack, local, design system, transporte browser → APEX, superfície versionada para Memory e Verify); parte foi respondida depois pela PR #100 (Vite + React, nginx → ClickHouse). A aprovação: "not_comparable is a result. Predictions stay predictions. null is not 0%".

**Próximo passo histórico:** Nenhuma ação nesta PR. Owner das decisões abertas: donos de DEC-07/DEC-08. Encerramento: histórico.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-49.md#item-487).

### #100 — feat(front): Apex Console — the seven screens as a runnable Vite + React app

Entregar a Apex Console: sete telas como app Vite + React + TypeScript alinhado ao contrato v0.5, com imagem de produção nginx e ClickHouse configurável.

**Implementação e limite:** Feito: a review de 2026-08-25 bloqueou por quatro itens (sem job de CI do front, nginx com nome curto `clickhouse`, Dockerfile sem `package-lock.json`, `bytesPerTask` divergente do engine); o autor respondeu em 2026-08-31 que os quatro entraram em `6dc476e` (job `front (Node 22)` no `ci.yml`, `CLICKHOUSE_UPSTREAM`, `npm ci` nos dois estágios, `bytesPerTask` igual a `StageAggregate.bytes_touched`). A aprovação final confirma. Commits de 2026-09-08 corrigem textos que "mentiam" (botões e `/ask` roteirizado). A camada de dados `front/src/data/` e os blocos `/clickhouse` do nginx conferem com o #102 (`fontes/git/_102.txt`). Runs verdes de PR e de push no head em 2026-09-10. Correções posteriores na mesma fronteira: #151 (detalhe de erro textual) e #153 (paridade da Console, commits de agmarcastro).

**Próximo passo histórico:** Nenhuma ação nesta PR. Owner da prova integrada: Pod 1 em #172. Encerramento: histórico.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-49.md#item-490).

### #118 — fix(front): isolate /verify source states and async selections (I1)

Implementar só a parte I1 do #116: estados por fonte e seleção assíncrona segura no `/verify`, para que URLs explícitas de job/finding funcionem com a lista de runs carregando ou indisponível, e erro não vire "sem resultado".

**Implementação e limite:** Feito: `useVerifyQuery.ts` (+38), `VerifyScreen.tsx` (+89/-49), `VerifyScreen.source-state.test.tsx` (+266), ajuste no teste de erro, `vitest.config.ts`, `package.json` e `package-lock.json` (+540, dependência de teste). Empilhada sobre a #100 com base `5b4fc4f`; o próprio corpo pede reavaliar a base se a #100 entrasse antes, o que aconteceu, e a aprovação diz "Base retargeted to main". No universo de runs retornado, o único run com o head é `workflow_dispatch` de 2026-09-12 (verde); não houve run `pull_request` sobre a base final, e o push do merge foi cancelado. A combinação final só aparece no `success` do run de push do merge da #87 (`4adb854`, criado 16:47:05Z, concluído 16:50:57Z, `fontes/git/_runs-push-main-por-dia.txt`).

**Próximo passo histórico:** Nenhuma ação nesta PR. Owner da lição: mantenedor (DEC-N4). Encerramento: histórico.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-50.md#item-494).

### #119 — fix(front): present /verify proposals and evidence faithfully (I2)

Implementar a parte I2 do #116: classificação fiel da proposta (overlay JSON escalar, malformado, diff unificado completo ou texto desconhecido), sem manter mapa parcial; texto original sempre visível e copiado exato; linguagem limitada sobre segurança e runtime; contexto honesto de memória de plano.

**Implementação e limite:** Feito: `contract/rules.ts` (+69/-22) e `rules.test.ts` (+80/-17), `VerifyScreen.tsx` (+118/-46), `DualVerdictPanel.tsx`, `FindingScreen.tsx`, `RunDetailScreen.tsx` e mais testes de estado. O corpo pede: "Merge #118 first; then retarget/rebase this PR … and re-run its checks before merging". No universo de runs retornado, o único run com o head é `workflow_dispatch` de 2026-09-12; não houve run depois do retarget, e o merge veio 23 s após a #118. A combinação teve `success` no run de push do merge da #87 (criado 16:47:05Z, concluído 16:50:57Z, `fontes/git/_runs-push-main-por-dia.txt`).

**Próximo passo histórico:** Nenhuma ação nesta PR. Owner da lição: mantenedor (DEC-N4). Encerramento: histórico.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-50.md#item-495).

### #120 — fix(front): expose original proposal as named region

Corrigir acessibilidade: o bloco da proposta original usava `aria-label` num `<pre>` cujo papel implícito `generic` proíbe nome; passa a ter papel `region` explícito, e os testes exigem a região nomeada preservando texto e espaços.

**Implementação e limite:** Feito: `VerifyScreen.tsx` (+1/-1) e `VerifyScreen.source-state.test.tsx` (+2). Relatado no corpo: 42 testes focados, 87 do front, typecheck, lint, build, "independent review: approve" e CI público 10/10 no run 34708443018. Na listagem pública coletada, o único run no head é `workflow_dispatch` de 2026-09-12 (verde), coerente com esse relato; não houve run depois do retarget.

**Próximo passo histórico:** Nenhuma ação obrigatória. Owner a confirmar: Pod 1, para a opção (b). Encerramento: histórico.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-50.md#item-496).

### #129 — feat(serve): apex-api — one HTTP layer between ClickHouse and its consumers

Pôr uma camada FastAPI entre o ClickHouse e quem o lê (decidido no Weekly Sync de 15/09): com `DATA_SOURCE=http` a console guarda um token de API e nenhuma credencial de banco, porque o modo atual envia a credencial de leitura a todo visitante.

**Implementação e limite:** Feito: `serve/src/apex_api/` (app, auth, config, rotas de diagnóstico e recursos), `apex_mcp/ch.py` (+511), cliente HTTP do front (`http.ts`, `repository.ts`), `nginx.conf` com `/v1/` (conferido na main para o #102), `serve/RUNBOOK.md`, testes de app, OpenAPI, recursos e leituras da console. Review do Copilot, registrada pela API em 2026-09-21: "The job was not started because the account is locked due to a billing issue." É o relato do bot sobre o próprio job de review: o run `Running Copilot Code Review` 35616653528 terminou em `failure` às 15:06:24Z, 3 s antes da review 5268257112 (15:06:27Z). A API devolve o texto, mas ele não é consulta de billing nem a anotação originária dos jobs de CI, e não prova sozinho a causa dos jobs sem steps. Os dois runs com o head final (push e pull_request, 2026-09-23, tentativa 1) têm 11 jobs cada, com 0 steps (`fontes/git/_jobs-head-prs-outubro.json`). PRs empilhadas sobre esta: #143, #146, #150, #151, #153. Pendências públicas: token e exposição de docs/OpenAPI (#171), prova em navegador (#172), relação com o BFF do #122. Atualização 19/10: as rotas de diagnóstico da API chamam o mesmo `create_server` do MCP sobre o mesmo `ReadStore` (`serve/src/apex_api/routes/diagnostics.py:31-32`); `store_health`, da L1, alimenta `/v1/health`. Autoria dos commits: 15 de Sidymar e 1 de Augusto Silva (`fab6620`).

**Próximo passo histórico:** Owner a confirmar: donos da #171 (DEC-08) e da #172 (Pod 1). Entrada: este registro. Saída: política de token e recibo de navegador. Encerramento: a PR segue integrada.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-51.md#item-501).

### #136 — fix(front): keep mechanism and runtime verdicts independent

Desacoplar veredito de mecanismo do veredito runtime no contrato do Front; rejeitar só o par contraditório certified=true + unresolved.

**Implementação e limite:** Feito: regra atualizada; follow-up 2fa0781 corrige narração (−12% previsto vs piso 5% descrito como regressão, não 'dentro do piso'); comparações estritas, held/vacant e fronteiras zero/zero preservadas. Faltante: prova de browser (explicitamente fora). Não comprovado: Node 22 local (só Node 26); CI do head anterior bloqueada por billing (#130), CI do head novo 'a verificar'.

**Próximo passo histórico:** Histórico integrado; prova remota futura deve usar SHA e escopo do Front, com destino de CI/governança pertinente. #156 não deve virar tracker genérico de toda validação Front. A decisão funcional do Verify permanece #117.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-51.md#item-507).

### #137 — fix(front): recognize retry pressure findings

Adicionar RETRY_PRESSURE aos tipos de finding conhecidos do contrato do Front, pois o Engine já o emitia.

**Implementação e limite:** O diff acrescenta RETRY_PRESSURE a KnownFindingType e ao comentário correspondente. Não inclui TAIL_OUTLIER, que segue fora da lista na base histórica, com acompanhamento #166. #127 integrou antes da #137; a ordem citada no corpo não é bloqueio técnico atual. Comportamento de tipo desconhecido deve ser lido/testado no consumidor, sem inferir perda silenciosa só pela enumeração.

**Próximo passo histórico:** Revisar #166 no Pod 1/Engine, responsável a confirmar, e escolher controle que use TAIL_OUTLIER/tipo desconhecido no consumidor concreto. Não propor reabrir a #137 histórica.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-51.md#item-508).

### #138 — ci(front): reject warnings and empty suites

Fazer o gate de CI do Front falhar em warnings do ESLint e em suíte de testes vazia, sem mudar comportamento para suíte populada e limpa.

**Implementação e limite:** Feito: --max-warnings 0 no lint e falha de suíte vazia. Faltante: política para novas regras começarem como warning (pergunta aberta no corpo). Não comprovado: rechecagem remota pós-billing visível no snapshot; a evidência Node 22 é local, não publicada.

**Próximo passo histórico:** Conferência estática com #160 preserva lint --max-warnings 0 e ausência de passWithNoTests. Sem repetição automática de teste já relatado; política para novas regras é decisão do time, separada de defeito observado.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-51.md#item-509).

### #146 — test(serve): pin fix_verifications projection parity with the front

A fronteira de piso de runtime_certified/runtime_verdict estava escrita nas duas projeções (Front queries.ts e Serve SQL) sem nada mantê-las em sincronia; fixar paridade byte a byte por teste.

**Implementação e limite:** Feito: teste verbatim com única renomeação de binding ({finding}→{finding_id}); segundo teste garante um binding só por lado. Faltante: política de piso segue em #117. Não comprovado: execução das projeções contra ClickHouse (declarado); CI não esperado na base empilhada.

**Próximo passo histórico:** Na decisão N03/#117, editar as duas projeções e conservar controle contra edição unilateral. Responsável a combinar Verify/Front/Serve. Saída inclui política aprovada e prova proporcional; byte-paridade isolada não aceita semântica.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-52.md#item-517).

### #151 — fix(front): render API error detail only when textual

FastAPI devolve 422 com detail como lista; o Console tratava como string, podendo exibir [object Object]; mostrar detail/error só quando texto, senão status HTTP.

**Implementação e limite:** Feito: type check no client; falhas de store mantêm código sanitizado; 3 testes (validação, store, fallback); contrato da API inalterado. Faltante: resumo dos erros de campo (não discutido). Não comprovado: browser e ClickHouse real; CI remota (base empilhada).

**Próximo passo histórico:** Sem mudança adicional obrigatória. Se houver necessidade de UX comprovada, propor resumo de erros de campo com teste que preserve sanitização; escolher no Pod 1, sem tratar fallback atual como incidente real.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-53.md#item-522).

### #153 — fix(serve,front): the console reads the same rows through either door

Sweep da apex-api: uma linha deve ser a mesma linha por qualquer porta (ClickHouse direto no browser vs. API). Quatro+ lugares onde não era, invisíveis para a suíte unitária porque fake devolve o que recebe.

**Implementação e limite:** Feito: run não indexado renderizava zero medido (sentinela indexed no CTE; confirmado live: browser -1 != api 0); um formato de timestamp só (ISO 8601 T, ms, UTC, wire.py); QueryFailure em toda tela antes de empty state; badge de fonte http correto; gate six-lane corrigido (detail=full; encontrado ao rodar); C3/C4 overlay com spark.driver.host; console_parity_gate.py live; test_every_console_field_is_projected; entry point E2E console_reflection + console.live.test.tsx; compose/make prod/README para modo http. Faltante (Open declarado): /ask ainda mockup (decisão de produto D-2026-09-23), verify lane não rodada E2E. Não comprovado: CI remota (billing) — toda evidência local.

**Próximo passo histórico:** Coordenar N15 com a matriz de prova #156 e fronteira de navegador #172; comparar #158/#159 com #182 antes de alterar a mesma superfície. Responsáveis Pod 1/Pod 3 a confirmar. #159 é review de gate com efeitos próprios; não é motivo para bloquear todos os estudos.

[Ficha completa e corte da prova](https://github.com/luanmorenommaciel/apex/blob/9a3bb5e4bdb95c9c787a5f0049d01afb8e6c6bf0/docs/reviews/audit-525-20261019/fichas-53.md#item-524).

## Colaborações que precisam permanecer explícitas

- **#100 é do Agmar:** sete commits dele e três com autor de commit Augusto Silva. Um dos três é merge de main; as duas contribuições substantivas de Augusto são `6dc476e` (integração/quality gates) e `5b4fc4f` (fingerprint e erros Verify). Isso não transfere a autoria da Console.
- **#129 é do Sidymar:** HTTP source `08ac39f`, same-origin `4297125` e primeira rodada de ajustes `c71c2e4` são dele. Augusto contribuiu com `fab6620`, concluindo ajustes de integração/review. A API principal não é atribuída a Augusto.
- **#153 é do Agmar:** a contribuição e as evidências declaradas dele são preservadas. O commit posterior `c4541a5` de Luan acrescenta desempate em findings; não é trabalho de Augusto.
- **#182 é proposta aberta do Agmar**, não entrega integrada de Augusto ou da main. A leitura focal não aprova todos os arquivos.
