# Fichas documentais — lote 50

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-491"></a>

## PR#101 — chore(serve): make the three legs mergeable — one contracted tool list, untracked generated state

Frente: historico. Encaminhamento: integrada_com_review_aprovada_preparacao_de_merge.

### Identidade e estado

PR #101, `chore/serve-merge-prep` → `main`; autora `sidymar`; `pod-3-serve`; criada em 2026-08-24, aprovada em 2026-08-25 e integrada em 2026-08-26T13:38:58Z (merge `847d7a0`); 1 commit; 4 arquivos. A autora explica que criou a PR "para corrigir os demais" a pedido de coordenação.

### Intenção e benefício

Tornar mergeáveis as três pernas do serve (#86, #87, #88), que conflitavam em 5–8 arquivos por par: uma lista única `CONTRACTED_TOOLS` da qual as asserções derivam, e tirar do versionamento os arquivos gerados `tasks/_state.yaml` e `tasks/_metrics.jsonl`.

### Feito, faltante e não comprovado

Feito: `test_server_tools.py` passa a derivar tudo de uma lista ordenada (+28/-9); `.gitignore` +5; remoção de `tasks/_metrics.jsonl` (-26) e `tasks/_state.yaml` (-239), ambos ausentes na main desde então. Depois do merge, as três PRs fizeram rebase e acrescentaram uma linha cada à lista (comentários de 2026-08-26 nas fichas PR#86–#88). A aprovação: "That is the merge contract the three serve legs need". Atualização 19/10: `CONTRACTED_TOOLS` tem oito nomes na main histórica; as specs L1 de 17/08 que fixam cinco tools ficaram numericamente superadas por este controle. `tasks/_state.yaml` e `tasks/_metrics.jsonl` continuam fora da árvore.

### Linhagem

Simulação de conflitos por `gustocezar` (2026-08-22, no #86) → PR #101 (2026-08-24) → aprovação (2026-08-25) → merge (2026-08-26) → rebase das três pernas → integração em 2026-09-14.

### Fontes e corte

Snapshot (PR 101); dossiê; `fontes/api-reviews/pr101-reviews.json`; comentários nas PRs #86–#88; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos, review, CI verde de PR no head. RELATADO: números de conflitos por par (8 e 7 arquivos), confirmados por duas pessoas. Review formal (API, observada em 2026-10-17T17:28:36Z): 1 — `luanmorenommaciel` APPROVED em 2026-08-25. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `df6fe77` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 32721699398, tentativa 1, created_at 2026-08-24 11:24:31Z, run_started_at 2026-08-24 11:24:31Z, updated_at 2026-08-24 11:27:52Z (antes do merge pelo updated_at).

### Fluxo

Fluxo de merge: três branches paralelas → bloco comum criado no ancestral (lista única) → cada perna acrescenta uma linha → conflitos reduzidos ao que tem significado.

### Consequências e risco

Médio-alto valor de processo: exemplo de resolver conflito estrutural na base, em vez de em cada branch. Ao remover os arquivos gerados do Git, o frontmatter continua sendo declaração de estado e deve ser reconciliado com implementação e evidência de aceite; retirar arquivos gerados não transforma declaração em prova. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter como histórico e citar como boa prática (recomendado); (b) nenhuma ação necessária.

### Dependências e paralelismo

Nenhuma dependência pendente; as três pernas foram integradas em 2026-09-14.

### Plano e aceite propostos

Condição explícita de não ação: preparação concluída e usada.

### Comunicação entre responsáveis

Para a consolidação: "PR #101 é um bom exemplo de destravar PRs paralelas mudando o ancestral comum".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — resolver os conflitos em cada perna repetiria o trabalho e arriscaria perder testes (como quase aconteceu na #88). (b) Que caso o teste ainda não cobre? — duas pernas acrescentando o mesmo nome à lista. (c) Como eu explicaria isso para outro pod? — "criamos o lugar comum antes de cada um escrever nele". (d) O ledger de tarefas precisa de outro arquivo gerado hoje?

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: histórico; a lista `CONTRACTED_TOOLS` é o ponto a atualizar quando o serve ganhar ferramenta nova.

<a id="item-492"></a>

## PR#110 — devex: detect hidden editable .pth files on macOS

Frente: historico. Encaminhamento: integrada_com_review_aprovada_e_ci_verde.

### Identidade e estado

PR #110, `codex/issue104-editable-pth-preflight` → `main`; autor `gustocezar` (commits de "Augusto Silva"); criada em 2026-08-29, aprovada em 2026-09-14 ("Commander approve") e integrada em 2026-09-14T16:19:57Z (merge `22dad25`); 2 commits; 2 arquivos. Fecha o #104 por `Closes`.

### Intenção e benefício

Adicionar um preflight somente leitura que distinga, nas raias Engine, Serve, Memory e Verify: `.pth` editável ausente, `.pth` apontando para o lugar errado, `.pth` correto com flag `hidden` do macOS, erro de inspeção e ambiente normal; fora do macOS, não faz nada.

### Feito, faltante e não comprovado

Feito: `scripts/editable_pth_preflight.py` (+160) e `tests/test_editable_pth_preflight.py` (+361); os dois existem na main e o script não é chamado pelo Makefile nem pelos scripts do pacote (conferido, `fontes/git/_104.txt`). O comando nunca repara nem altera metadados. Commits de endurecimento: "preserve editable pth path semantics" e "harden editable pth preflight". Reconfirmado em 19/10: nenhum uso de `editable_pth` no `Makefile`, em `scripts/` ou em `dev/` além do próprio script.

### Linhagem

Incidente local de macOS → #104 → PR #110 (2026-08-29) → aprovação → merge na leva (push cancelado; o próximo `success` na main foi o run do merge da #87, criado 16:47:05Z e concluído 16:50:57Z, `fontes/git/_runs-push-main-por-dia.txt`).

### Fontes e corte

Snapshot (PR 110); dossiê; `fontes/api-reviews/pr110-reviews.json`; `fontes/git/_104.txt`; `fontes/git/_runs-push-main-por-dia.txt`; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos, review, CI verde de PR no head (2026-08-29), ausência de chamadas no pacote. RELATADO: o incidente que motivou a ferramenta. Review formal (API, observada em 2026-10-17T17:28:37Z): 1 — `luanmorenommaciel` APPROVED em 2026-09-14. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `8257116` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 33253649755, tentativa 1, created_at 2026-08-29 12:53:55Z, run_started_at 2026-08-29 12:53:55Z, updated_at 2026-08-29 12:57:21Z (antes do merge pelo updated_at).

### Fluxo

Fluxo: `python scripts/editable_pth_preflight.py` → localizar `.pth` de cada raia → validar destino → ler flag `hidden` (macOS) → diagnóstico sanitizado, sem mudança.

### Consequências e risco

Baixo risco e utilidade pontual. Limite: só ajuda quem sabe que ele existe; não está ligado ao `doctor`. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) ligar ao `doctor` se o problema reaparecer em outra máquina.

### Dependências e paralelismo

A opção (b) dependeria do dono do pacote; não há dependência técnica pendente.

### Plano e aceite propostos

Condição explícita de não ação: ferramenta integrada com teste próprio.

### Comunicação entre responsáveis

Para a consolidação: "PR #110 entregou o diagnóstico do `.pth` oculto pedido no #104".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — um preflight que reparasse metadados mexeria no ambiente do usuário sem pedir. (b) Que caso o teste ainda não cobre? — macOS real com o flag aplicado. (c) Como eu explicaria isso para outro pod? — "um script que explica por que o import some no Mac". (d) O doctor deveria rodá-lo?

### Próxima ação e encerramento

Nenhuma ação e nenhum owner. Encerramento: histórico; reabrir só se o diagnóstico errar o caso de `.pth` oculto num macOS real.

<a id="item-493"></a>

## PR#111 — docs: add executable telemetry compatibility matrix

Frente: historico. Encaminhamento: integrada_com_review_aprovada_quebrou_root_gate_na_leva.

### Identidade e estado

PR #111, `codex/issue103-telemetry-compatibility-matrix` → `main` (base `847d7a0`); autor `gustocezar` (commit de "Augusto Silva"); criada em 2026-08-29, aprovada em 2026-09-14 e integrada em 2026-09-14T16:20:02Z (merge `31a0cee`); 1 commit; 2 arquivos. Fecha o #103 por `Closes`. Ligada ao registro L08.

### Intenção e benefício

Registrar de forma executável onde cada campo de telemetria é produzido, transportado, armazenado e consumido, separando contrato declarado, implementação observada, relação derivada e `offline_unproven`.

### Feito, faltante e não comprovado

Feito: `docs/architecture/TELEMETRY-COMPATIBILITY-MATRIX.md` (+186) e `tests/test_telemetry_compatibility_matrix.py` (+200). Na leva de 2026-09-14, esta PR entrou dois minutos depois da #96, que subiu o contrato para v0.6; o teste fixava v0.5; segundo o corpo da #121, isso quebrou o root gate da main; nos runs, o push do merge da #98 concluiu em `failure` às 16:28:02Z, e o próximo `success` na main foi às 16:50:57Z (merge da #87, depois da #121). A guarda também fixa textos literais (`PROPOSED v0.4`, `PROPOSED, not ratified` e a frase obsoleta de `models.py`, linha 166), o que obriga correções em #165/#179 a ajustar o teste junto (conferido, `fontes/git/_103.txt`). Reconfirmado em 19/10: a guarda fixa `PROPOSED v0.4` e `PROPOSED, not ratified` (linhas 145–147) e a frase antiga de `models.py` (linha 166).

### Linhagem

#103 → PR #111 (base `847d7a0`, sem a #96) → aprovação → merge após a #96 → `failure` no push do merge da #98 → PR #121 atualiza para v0.6 → `success` no push do merge da #87.

### Fontes e corte

Snapshot (PR 111); dossiê; `fontes/api-reviews/pr111-reviews.json`; `fontes/git/_103.txt`; `fontes/git/_runs-push-main-por-dia.txt`; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos, review, CI verde de PR no head (2026-08-29, sobre base sem v0.6), push da main vermelho e correção posterior. RELATO da #121, compatível com a linha do tempo: a quebra teria vindo da combinação com a #96; o log do run falho não foi lido para confirmar causalidade. Review formal (API, observada em 2026-10-17T17:28:37Z): 1 — `luanmorenommaciel` APPROVED em 2026-09-14. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `4f833c7` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 33272025452, tentativa 1, created_at 2026-08-29 19:53:10Z, run_started_at 2026-08-29 19:53:10Z, updated_at 2026-08-29 19:57:09Z (antes do merge pelo updated_at).

### Fluxo

Fluxo da guarda: manifesto da matriz → asserções contra `CONTRACT.md`, DDLs e código das raias → falha se versão, tabela ou consumidor divergir.

### Consequências e risco

Médio. A matriz cumpre o papel de pegar drift (pegou a v0.6), mas o modo de fixar texto literal transforma correções de documentação em quebras de teste. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) avaliar se a guarda deve checar intenção (por exemplo, "o drift está registrado") em vez de frases literais — decisão de quem mantém a matriz.

### Dependências e paralelismo

A opção (b) se cruza com #165 (marcadores) e #179/CL-02 (texto do Verify); nenhuma dependência técnica pendente na PR.

### Plano e aceite propostos

Condição explícita de não ação nesta PR. Nota operacional: quem mudar `CONTRACT.md` ou textos fixados deve atualizar a matriz na mesma PR.

### Comunicação entre responsáveis

Para a consolidação: "PR #111 é a guarda de drift; na leva de 09-14 ela mesma acusou a v0.6 que entrou junto".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — sem a matriz, a mudança de versão do contrato passaria despercebida. (b) Que caso o teste ainda não cobre? — runtime, por desenho (`offline_unproven`). (c) Como eu explicaria isso para outro pod? — "o teste falha se o contrato e o código pararem de concordar". (d) Fixar frases literais ajuda ou atrapalha?

### Próxima ação e encerramento

Nenhuma ação nesta PR. Owner a confirmar: mantenedor da matriz, para a opção (b). Encerramento: histórico.

<a id="item-494"></a>

## PR#118 — fix(front): isolate /verify source states and async selections (I1)

Frente: historico. Encaminhamento: integrada_com_review_aprovada_ci_por_workflow_dispatch.

### Identidade e estado

PR #118, `codex/issue116-verify-source-states` → `main` (base `8d3efa7`, o merge da #100, após retarget); autor `gustocezar` (commit de "Augusto Silva"); criada em 2026-09-12, aprovada em 2026-09-14 ("Commander approve (Luan via Helm)") e integrada em 2026-09-14T16:20:47Z (merge `fbacbf0`); 1 commit; 7 arquivos. Fecha o #116 (I1). Ligada a F01.

### Intenção e benefício

Implementar só a parte I1 do #116: estados por fonte e seleção assíncrona segura no `/verify`, para que URLs explícitas de job/finding funcionem com a lista de runs carregando ou indisponível, e erro não vire "sem resultado".

### Feito, faltante e não comprovado

Feito: `useVerifyQuery.ts` (+38), `VerifyScreen.tsx` (+89/-49), `VerifyScreen.source-state.test.tsx` (+266), ajuste no teste de erro, `vitest.config.ts`, `package.json` e `package-lock.json` (+540, dependência de teste). Empilhada sobre a #100 com base `5b4fc4f`; o próprio corpo pede reavaliar a base se a #100 entrasse antes, o que aconteceu, e a aprovação diz "Base retargeted to main". No universo de runs retornado, o único run com o head é `workflow_dispatch` de 2026-09-12 (verde); não houve run `pull_request` sobre a base final, e o push do merge foi cancelado. A combinação final só aparece no `success` do run de push do merge da #87 (`4adb854`, criado 16:47:05Z, concluído 16:50:57Z, `fontes/git/_runs-push-main-por-dia.txt`).

### Linhagem

#116 (I1/I2/a11y) → PR #118 sobre a #100 → PR #119 sobre a #118 → PR #120 sobre a #119 → merges em sequência em 2026-09-14 (16:20:47, 16:21:10, 16:21:23) → `success` na main no run concluído às 16:50:57Z.

### Fontes e corte

Snapshot (PR 118); dossiê; `fontes/api-reviews/pr118-reviews.json`; `fontes/git/_runs-push-main-por-dia.txt`; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos, aprovação, tipo e data do único run no head. INFERÊNCIA: o CI provou a PR sobre a base empilhada, não sobre a main; a prova da combinação é o run de push concluído às 16:50:57Z. Review formal (API, observada em 2026-10-17T17:28:38Z): 1 — `luanmorenommaciel` APPROVED em 2026-09-14. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `a8ccc52` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` workflow_dispatch success, run 34660612065, tentativa 1, created_at 2026-09-12 00:08:31Z, run_started_at 2026-09-12 00:08:31Z, updated_at 2026-09-12 00:12:06Z (antes do merge pelo updated_at).

### Fluxo

Fluxo da tela: URL com `?job=`/`?finding=` → consultas por fonte com estado próprio → seleção automática só quando não há escolha explícita → tela não bloqueia por loading de fonte irrelevante.

### Consequências e risco

Baixo-médio: valor alto para o usuário; o risco de processo é a prova de CI feita sobre outra base. O `success` na main veio cerca de 30 min depois do merge (16:50:57Z), o que reduz o risco na prática. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) em pilhas futuras, exigir run `pull_request` depois do retarget, como o próprio autor sugeriu no corpo da #119.

### Dependências e paralelismo

A opção (b) é política de integração (DEC-N4); não há dependência técnica pendente.

### Plano e aceite propostos

Condição explícita de não ação nesta PR. Lição para a DEC-N4: PR empilhada precisa de CI depois do retarget para a main.

### Comunicação entre responsáveis

Para a consolidação: há um workflow_dispatch verde no head anterior ao retarget e um push verde posterior em árvore que inclui esta PR; isso não substitui prova pré-merge da combinação exata.

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — uma guarda global de erros bloquearia a tela num caminho que funciona, como o #116 alerta. (b) Que caso o teste ainda não cobre? — a combinação #100 + #118 testada antes do merge. (c) Como eu explicaria isso para outro pod? — "cada fonte da tela tem seu estado; o CI rodou antes de a base mudar". (d) Quem pede o run depois de um retarget?

### Próxima ação e encerramento

Nenhuma ação nesta PR. Owner da lição: mantenedor (DEC-N4). Encerramento: histórico.

<a id="item-495"></a>

## PR#119 — fix(front): present /verify proposals and evidence faithfully (I2)

Frente: historico. Encaminhamento: integrada_com_review_aprovada_ci_por_workflow_dispatch.

### Identidade e estado

PR #119, `codex/issue116-verify-evidence-i2` → `main` (base `fbacbf0`, o merge da #118); autor `gustocezar` (commits de "Augusto Silva"); criada em 2026-09-12, aprovada em 2026-09-14 e integrada em 2026-09-14T16:21:10Z (merge `189b3c6`), 23 segundos depois da #118; 2 commits; 7 arquivos. Cita o #116. Ligada a F01.

### Intenção e benefício

Implementar a parte I2 do #116: classificação fiel da proposta (overlay JSON escalar, malformado, diff unificado completo ou texto desconhecido), sem manter mapa parcial; texto original sempre visível e copiado exato; linguagem limitada sobre segurança e runtime; contexto honesto de memória de plano.

### Feito, faltante e não comprovado

Feito: `contract/rules.ts` (+69/-22) e `rules.test.ts` (+80/-17), `VerifyScreen.tsx` (+118/-46), `DualVerdictPanel.tsx`, `FindingScreen.tsx`, `RunDetailScreen.tsx` e mais testes de estado. O corpo pede: "Merge #118 first; then retarget/rebase this PR … and re-run its checks before merging". No universo de runs retornado, o único run com o head é `workflow_dispatch` de 2026-09-12; não houve run depois do retarget, e o merge veio 23 s após a #118. A combinação teve `success` no run de push do merge da #87 (criado 16:47:05Z, concluído 16:50:57Z, `fontes/git/_runs-push-main-por-dia.txt`).

### Linhagem

#116 → PR #118 (I1) → PR #119 (I2) empilhada → merge em sequência → PR #120 (a11y) → `success` na main concluído às 16:50:57Z. Problemas de contrato que restam no `/verify` estão no #117.

### Fontes e corte

Snapshot (PR 119); dossiê; `fontes/api-reviews/pr119-reviews.json`; `fontes/git/_runs-push-main-por-dia.txt`; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos, aprovação, o pedido explícito de reexecutar checks e a ausência desse run. RELATADO: comportamento SSR reproduzido no #116. Review formal (API, observada em 2026-10-17T17:28:39Z): 1 — `luanmorenommaciel` APPROVED em 2026-09-14. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `0f19712` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` workflow_dispatch success, run 34704465939, tentativa 1, created_at 2026-09-12 16:11:21Z, run_started_at 2026-09-12 16:11:21Z, updated_at 2026-09-12 16:14:55Z (antes do merge pelo updated_at).

### Fluxo

Fluxo de apresentação: proposta armazenada → classificador (`parseProposal`) → tipo reconhecido ou desconhecido → painel com texto original intacto → nada de namespace positivo para documento parcialmente interpretado.

### Consequências e risco

Médio valor para o usuário. Processo: o pedido do próprio autor (reexecutar checks após retarget) não foi seguido antes do merge; a main teve `success` observado depois (16:50:57Z), mas esse verde não prova ausência de regressões nem valida cada comportamento em runtime. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) mesma lição da PR #118 para a DEC-N4.

### Dependências e paralelismo

A opção (b) é política (DEC-N4); os problemas de contrato do `/verify` dependem do #117 (DEC-05/DEC-06).

### Plano e aceite propostos

Condição explícita de não ação nesta PR: integrada e com `success` no run de push da main concluído às 16:50:57Z; o único passo útil é levar a lição de CI após retarget para a DEC-N4.

### Comunicação entre responsáveis

Para a consolidação: "PR #119 pediu CI após retarget e entrou sem ele; a main teve success observado às 16:50:57Z".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — um namespace positivo para proposta parcialmente lida faria o usuário aplicar uma correção validada pela metade. (b) Que caso o teste ainda não cobre? — proposta real armazenada com campos não escalares em produção. (c) Como eu explicaria isso para outro pod? — "a tela mostra a proposta como ela é e diz quando não conseguiu entendê-la". (d) O merge em 23 s respeitou o que o autor pediu?

### Próxima ação e encerramento

Nenhuma ação nesta PR. Owner da lição: mantenedor (DEC-N4). Encerramento: histórico.

<a id="item-496"></a>

## PR#120 — fix(front): expose original proposal as named region

Frente: historico. Encaminhamento: integrada_com_review_aprovada_ci_por_workflow_dispatch.

### Identidade e estado

PR #120, `codex/issue116-verify-original-proposal-region` → `main` (base `189b3c6`, o merge da #119); autor `gustocezar` (commit de "Augusto Silva"); criada em 2026-09-12, aprovada em 2026-09-14 e integrada em 2026-09-14T16:21:23Z (merge `dc9f22e`); 1 commit; 2 arquivos (+3/-1). Ligada a F01.

### Intenção e benefício

Corrigir acessibilidade: o bloco da proposta original usava `aria-label` num `<pre>` cujo papel implícito `generic` proíbe nome; passa a ter papel `region` explícito, e os testes exigem a região nomeada preservando texto e espaços.

### Feito, faltante e não comprovado

Feito: `VerifyScreen.tsx` (+1/-1) e `VerifyScreen.source-state.test.tsx` (+2). Relatado no corpo: 42 testes focados, 87 do front, typecheck, lint, build, "independent review: approve" e CI público 10/10 no run 34708443018. Na listagem pública coletada, o único run no head é `workflow_dispatch` de 2026-09-12 (verde), coerente com esse relato; não houve run depois do retarget.

### Linhagem

#116 → PRs #118/#119 → PR #120 empilhada → merge 13 s depois da #119 → `success` na main concluído às 16:50:57Z.

### Fontes e corte

Snapshot (PR 120); dossiê; `fontes/api-reviews/pr120-reviews.json`; `fontes/git/_runs-push-main-por-dia.txt`; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: diff, aprovação, run no head. RELATADO: "independent review: approve" (provavelmente de outra ferramenta; tratado como alegação). Review formal (API, observada em 2026-10-17T17:28:40Z): 1 — `luanmorenommaciel` APPROVED em 2026-09-14. `APPROVED` humano antes do merge: sim; no head final: sim. Eventos de review não provam nem excluem leitura humana fora deles. Comentários inline de review: 0. Runs do Actions com o head `961e296` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` workflow_dispatch success, run 34708443018, tentativa 1, created_at 2026-09-12 17:30:45Z, run_started_at 2026-09-12 17:30:45Z, updated_at 2026-09-12 17:34:25Z (antes do merge pelo updated_at).

### Fluxo

Fluxo de acessibilidade: leitor de tela → elemento com `role="region"` e `aria-label` → nome anunciado → texto original preservado.

### Consequências e risco

Baixo risco; melhora real de acessibilidade com mudança mínima. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) checagem de acessibilidade automatizada no CI do front, se o time quiser evitar regressões do tipo.

### Dependências e paralelismo

A opção (b) depende de decisão do Pod 1; não há dependência técnica pendente.

### Plano e aceite propostos

Condição explícita de não ação: mudança mínima integrada com teste.

### Comunicação entre responsáveis

Para a consolidação: "PR #120 tornou a proposta original legível por leitor de tela".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — o `aria-label` num elemento sem papel seria ignorado por tecnologia assistiva. (b) Que caso o teste ainda não cobre? — leitor de tela real. (c) Como eu explicaria isso para outro pod? — "o bloco agora tem papel de região, então o nome é anunciado". (d) O front deveria rodar uma checagem de acessibilidade no CI?

### Próxima ação e encerramento

Nenhuma ação obrigatória. Owner a confirmar: Pod 1, para a opção (b). Encerramento: histórico.

<a id="item-497"></a>

## PR#121 — fix(tests): bump telemetry matrix to contract v0.6

Frente: historico. Encaminhamento: integrada_sem_review_formal_corrigiu_main.

### Identidade e estado

PR #121, `cursor/fix-telemetry-matrix-v06-8424` → `main` (base `3fb411a`, o merge da #98); autor `luanmorenommaciel` (OWNER), commit único `efb6773` com autor de commit "Cursor Agent" (metadado do commit; não descreve todo o processo de autoria); criada e integrada em 2026-09-14T16:46:27Z (merge `16e3819`); 2 arquivos (+8/-7 e +3/-3). Sem review formal registrada. Ligada ao registro L08.

### Intenção e benefício

Consertar o root gate da main, que falhava em `test_telemetry_compatibility_matrix.py::test_matrix_is_structural_and_derived_from_independent_sources` porque o `CONTRACT.md` passou a v0.6 (PR #96) e a matriz (PR #111) esperava v0.5.

### Feito, faltante e não comprovado

Feito: o teste e o documento passam a esperar v0.6; o manifesto de drift tira o engine de `observed_consumers_without_sample_count`, porque o engine passou a ler `sample_count` (PR #89/#99). Run de PR no head concluído com `success` às 16:45:14Z (34870161347, criado 16:41:30Z), antes do merge (16:46:27Z). O run de push do merge (`16e3819`, 34870682662) foi cancelado às 16:47:24Z, então a árvore desta PR sozinha não tem conclusão observada na main; o run de push do merge da #87 (`4adb854`, 34870745971), que já inclui esta PR, foi criado 16:47:05Z e concluiu com `success` às 16:50:57Z (`fontes/reconferencia/pontos08-09-tempos-de-runs.json`). O run vermelho do head da #87 (`run34868325801-jobs.json`) falhou no `pytest tests/` do root gate, compatível com a causa relatada no corpo; isso não prova a causa.

### Linhagem

PR #96 (v0.6) + PR #111 (matriz v0.5) na mesma leva, segundo o corpo desta PR → run de push do merge da #98 em `failure` (criado 16:22:37Z, concluído 16:28:02Z) → PR #121 (commit único com autor "Cursor Agent") → merge (16:46:27Z) → push do merge cancelado → `success` no push do merge da #87 (concluído 16:50:57Z).

### Fontes e corte

Snapshot (PR 121); dossiê; `fontes/api-reviews/pr121-reviews.json` (0 reviews); `fontes/git/_runs-push-main-por-dia.txt`; `fontes/api-reviews/run34868325801-jobs.json`; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: diff, ausência de review, runs. RELATADO no corpo: o nome do teste que falhava. INFERÊNCIA compatível com a sequência de runs, não confirmada: o primeiro `success` observado na main é numa árvore que inclui esta correção e a #87; o run da árvore desta PR foi cancelado, e cancelamento não prova causalidade; os jobs do run falho da #98 não foram coletados. Review formal (API, observada em 2026-10-17T17:28:40Z): 0 registradas; isso não prova ausência de leitura humana. Comentários inline de review: 0. Runs do Actions com o head `efb6773` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request success, run 34870161347, tentativa 1, created_at 2026-09-14 16:41:30Z, run_started_at 2026-09-14 16:41:30Z, updated_at 2026-09-14 16:45:14Z (antes do merge pelo updated_at).

### Fluxo

Fluxo da correção: `CONTRACT.md` diz v0.6 → manifesto e asserções da matriz atualizados → root gate volta a passar.

### Consequências e risco

Baixo como mudança; relevante como padrão: segundo caso neste recorte de PR com commit de autor "Cursor Agent" integrada pelo OWNER sem review formal registrada (a outra é a #80). O intervalo observado foi curto: ~23 min entre a conclusão do run em `failure` (16:28:02Z) e a do primeiro `success` seguinte na main (16:50:57Z); pelos created_at seriam 24 min (16:22:37Z → 16:47:05Z). Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter como histórico (recomendado); (b) registrar na DEC-02 se correções urgentes de CI podem dispensar review formal (caminho de emergência).

### Dependências e paralelismo

A opção (b) depende da DEC-02 (política de proteção e bypass); não há dependência técnica pendente.

### Plano e aceite propostos

Sem reabertura automática. Propor à DEC-02 uma política explícita para correções urgentes e revisão posterior; não presumir que já existia um bypass ou rito formal autorizado.

### Comunicação entre responsáveis

Para a consolidação: "PR #121 atualizou a matriz para v0.6 sem review formal registrada; o primeiro success observado na main depois dela veio no merge da #87, ~23 min após a conclusão do run falho".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — esperar review para um teste quebrado teria deixado a main vermelha por mais tempo. (b) Que caso o teste ainda não cobre? — a próxima mudança de versão do contrato. (c) Como eu explicaria isso para outro pod? — "a matriz pediu v0.5, o contrato estava em v0.6; ajustamos a matriz". (d) Correções de emergência devem ter review depois do merge?

### Próxima ação e encerramento

Owner a confirmar: mantenedor, ao decidir o caminho de emergência na DEC-02. Encerramento: histórico.

<a id="item-498"></a>

## PR#126 — feat(engine): add offline execution-stage attribution

Frente: historico. Encaminhamento: integrada_sem_review_formal_e_sem_ci_executado.

### Identidade e estado

PR #126, `gustocezar/issue-115-execution-attribution` → `main`; autor `gustocezar` (commits de "Augusto Silva"); criada em 2026-09-20 e integrada em 2026-10-06T19:55:46Z (merge `abed508`, o primeiro da leva); 13 commits; 10 arquivos. Ligada a E01, G01, G03, G04 e P01. Relação: #115 (aberta), sem `Closes`. Integrada na leva de 2026-10-06 (27 merges de PR entre 19:55:46Z e 20:32:30Z, com commits de merge do mantenedor, mais dois commits diretos na main, `fa0951f` e `c4541a5`), dentro do intervalo de 2026-09-20 a 2026-10-06 (created_at UTC) em que os 68 runs `CI` retornados pela API terminaram em `failure` (56) ou `cancelled` (12), sem `success` (`fontes/reconferencia/ponto01-intervalo-ci.json`; a contagem de 61 do pacote de 17/10 usava outro intervalo).

### Intenção e benefício

Implementar o resolvedor offline do engine que atribui uma execução SQL a stages, com escopo pela identidade completa `(app_id, job_id)`, resultados explícitos (ausente, não encontrado, atribuído, conflito) e semântica de tentativas sem duplicar membros.

### Feito, faltante e não comprovado

Feito no código: `engine/src/apex_engine/attribution.py` (+138) e `engine/tests/test_execution_attribution.py` (+218), mais quatro TaskPlans e quatro Task-Specs em `tasks/done/`. Relatado: 25 testes de atribuição e 213 offline passando em `4ddb082`, com três casos novos que separam `execution_id` 0 de ausente. O Codex (C04-13) registra que o resolvedor e os testes já cobrem conflito, escopo estrangeiro, tentativas, ausência e zero, e que o sentinela `-1` de AQE é de nível de job. Falta (fora desta PR, na #115): consumidor público da atribuição. Prova hospedada: no universo de 213 runs retornado em 2026-10-17, o único run com o head final é o 36488146081 (pull_request, tentativa 1, criado 2026-09-28T21:44:59Z, updated_at 21:45:03Z, `failure`), cujos 11 jobs coletados têm 0 steps (`fontes/reconferencia/pontos03-05-06-runs-por-pr.json`). Reconfirmado em 19/10: `attribution.py` só é importado por testes; findings de nível de job seguem com `JOB_LEVEL_STAGE_ID = -1` e `attributionIsAvailable()` retorna `false` (#115).

### Linhagem

#115 → quatro TaskPlans → PR #126 (2026-09-20) → caso zero × ausente (2026-09-27) → run do head com 11 jobs sem steps na tentativa observada → merge sem review humana registrada (2026-10-06) → run de push do merge (`abed508`, 37522575349) concluído em `failure` às 19:55:53Z, sem jobs coletados (`fontes/git/_runs-push-main-por-dia.txt`). O #115 continua aberta para os consumidores.

### Fontes e corte

Snapshot (PR 126); dossiê (10 arquivos, 13 commits); `fontes/api-reviews/pr126-reviews.json` (0); `fontes/git/_jobs-head-prs-outubro.json`; `fontes/git/_runs-push-main-por-dia.txt`; `fontes/git/_entrada-na-main.json`; correção C04-13 do Codex, lida como alegação.

### Classe e limite da evidência

DIRETO: arquivos, ausência de review, jobs sem steps no head, push do merge falho. RELATADO: contagens de testes locais. INFERÊNCIA limitada ao recorte: nenhum run com o head final concluiu com `success` no universo retornado, e a única tentativa com jobs coletados não executou steps; isso não prova que nenhuma execução hospedada tenha ocorrido em outra tentativa ou árvore. Review formal (API, observada em 2026-10-17T17:28:41Z): 0 registradas; isso não prova ausência de leitura humana. Comentários inline de review: 0. Runs do Actions com o head `4ddb082` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request failure, run 36488146081, tentativa 1, created_at 2026-09-28 21:44:59Z, run_started_at 2026-09-28 21:44:59Z, updated_at 2026-09-28 21:45:03Z (antes do merge pelo updated_at); jobs coletados desta tentativa: 11, steps: 0.

### Fluxo

Fluxo do resolvedor: observações `(app_id, job_id, stage, attempt, execution_id)` → filtro pela identidade → atribuído, conflito, ausente ou não encontrado → (futuro) consumidor no engine/serve.

### Consequências e risco

Médio. O código é offline e bem testado localmente; o risco está na prova: nenhum `success` de CI foi observado no head final antes do merge (a tentativa com jobs coletados tem 0 steps), e não há `CI` verde na main depois da integração até o fim da listagem (2026-10-12; há só um `jar` verde em 2026-10-12); os verdes de 2026-10-09 são de outras árvores (branches `codex/...-156` e outras) e não provam esta PR (NOV-02). Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter integrada e incluir na prova pós-integração (P-INT-0) (recomendado); (b) reverter até haver CI — desproporcional, pois o código não tem consumidor ainda.

### Dependências e paralelismo

A prova hospedada depende de DEC-01 (CI disponível). O consumidor público depende da #115 e da DEC-09.

### Plano e aceite propostos

Passo mínimo: quando o CI principal rodar na main, confirmar `test_execution_attribution.py` verde. Controle discriminante já presente nos testes: `execution_id` 0 não pode ser tratado como ausente.

### Comunicação entre responsáveis

Para a consolidação: "PR #126 trouxe o resolvedor offline; entrou sem review formal registrada e sem CI verde observado no head final (tentativa com jobs coletados sem steps)".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — tratar 0 como ausente perderia execuções reais de id 0. (b) Que caso o teste ainda não cobre? — o resolvedor alimentado por dados reais do ClickHouse. (c) Como eu explicaria isso para outro pod? — "o engine sabe dizer a que execução SQL um stage pertence, mas não encontrei consumidor disso na main de referência". (d) Qual será o primeiro consumidor (DEC-09)?

### Próxima ação e encerramento

Owner a confirmar: mantenedor, na prova pós-integração (M0). Entrada: CI disponível. Saída: run verde que inclua estes testes. Encerramento: a PR segue integrada; o consumidor segue na #115.

<a id="item-499"></a>

## PR#127 — feat: add deterministic tail-outlier runtime gate

Frente: historico. Encaminhamento: integrada_sem_review_formal_e_sem_ci_executado.

### Identidade e estado

PR #127, `gustocezar/issue-123-tail-outlier` → `main`; autor `gustocezar`; criada em 2026-09-20 e integrada em 2026-10-06T19:56:00Z (merge `fec8a7f`); 19 commits; 30 arquivos. Ligada a 19 IDs do registro (E08, E12, E14, E16–E18, F13, F16, F18, G03, G04, G08, P02, P08, S17, S18, X14). Relação: #123 (aberta), sem `Closes`. Integrada na leva de 2026-10-06 (27 merges de PR entre 19:55:46Z e 20:32:30Z, com commits de merge do mantenedor, mais dois commits diretos na main, `fa0951f` e `c4541a5`), dentro do intervalo de 2026-09-20 a 2026-10-06 (created_at UTC) em que os 68 runs `CI` retornados pela API terminaram em `failure` (56) ou `cancelled` (12), sem `success` (`fontes/reconferencia/ponto01-intervalo-ci.json`; a contagem de 61 do pacote de 17/10 usava outro intervalo).

### Intenção e benefício

Completar o caminho determinístico `tail_outlier`: contrato do finding, watcher seguro a retry que cede quando o skew já explica o caso, roteamento de um cenário canônico opt-in, remoção da recusa antiga no pacote, asserção da forma de cauda no ClickHouse e uma prova de runtime local documentada.

### Feito, faltante e não comprovado

Feito no código e conferido na main: `engine/src/apex_engine/watchers/tail_outlier.py`, `docs/e2e/TAIL_OUTLIER_RUNTIME_GATE.md` e `tests/test_tail_outlier_package.py` existem. Relatado (C04-10 do Codex): núcleo Spark→Collector→ClickHouse→Engine provado em 2026-09-20 e wrapper público macOS/Spark 4.0.1 em 2026-09-21, com cache de imagens; a razão `373,364` pertence ao núcleo de 20/09. Limite (C04-11): o gate procura `tail_outlier_watcher` na saída e não compara stage/snapshot da asserção; `llm_calls=0` é literal. Também corrige a leitura de segredos S3 do pacote e falha cedo sem Python 3. Resíduo conferido na main: o front não reconhece `TAIL_OUTLIER` como tipo de finding (`front/src/contract/types.ts` só lista `RETRY_PRESSURE` entre os novos; ver ficha PR#137); esse resíduo já é acompanhado pela #166, aberta. Prova hospedada: o run do head 35557495963 foi criado em 2026-09-21T03:25:53Z; a tentativa retornada é a 2, executada em 2026-09-23T03:53 (run_started_at), com 11 jobs e 0 steps (`fontes/git/_jobs-head-prs-outubro.json`); a tentativa 1 de 2026-09-21 não está coberta pela coleta (`fontes/reconferencia/pontos03-05-06-runs-por-pr.json`).

### Linhagem

#123 → TaskPlans de engine, wiring, runtime gate e remediação → PR #127 (2026-09-20) → prova local de 20–21/09 → run do head sem steps na tentativa retornada (a 2) → merge sem review (2026-10-06) → push falho. A associação forte/fraca do gate está na DEC-N6 e no E17.

### Fontes e corte

Snapshot (PR 127); dossiê (30 arquivos); `fontes/api-reviews/pr127-reviews.json` (0); `fontes/git/_jobs-head-prs-outubro.json`; `fontes/git/_runs-push-main-por-dia.txt`; correções C04-10/C04-11 do Codex; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos na main, ausência de review, jobs sem steps. RELATADO: execução de runtime em 20–21/09 com escopo e limites. INFERÊNCIA (do Codex, coerente com o código descrito): o gate prova presença do watcher no job, não associação ao stage escolhido. Review formal (API, observada em 2026-10-17T17:28:41Z): 0 registradas; isso não prova ausência de leitura humana. Comentários inline de review: 0. Runs do Actions com o head `4e44bfd` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request failure, run 35557495963, tentativa 2, created_at 2026-09-21 03:25:53Z, run_started_at 2026-09-23 03:53:01Z, updated_at 2026-09-23 03:53:08Z (antes do merge pelo updated_at); jobs coletados desta tentativa: 11, steps: 0.

### Fluxo

Fluxo do gate: job canônico de cauda → telemetria → asserção da forma no ClickHouse → `apex_engine --dry-run --no-crew` → busca `tail_outlier_watcher` na saída → PASS.

### Consequências e risco

Médio-alto: é a PR de maior alcance da leva (19 IDs). A prova de runtime é histórica e local; a de CI não foi observada (a tentativa 2 coletada tem 0 steps; a tentativa 1 não está coberta); a garantia do gate é mais fraca que o texto da #123 sugere. Atualização 19/10: o gate copia `.apex/dev.env` sobre `dev/.env` e endereça recursos `apex-*` por nome; o B-5 da spec `T-20260920-tail-outlier-runtime-gate` pede não reutilizar recursos alheios, e `docs/e2e/TAIL_OUTLIER_RUNTIME_GATE.md:69-77` admite o limite. Nova execução exige plano que preserve ambiente e ownership (#174/#175 ou ambiente descartável autorizado), sem travar estudo ou desenho. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter integrada; incluir na prova pós-integração e decidir DEC-N6 antes de usar o gate como aceite da #123 (recomendado); (b) reverter — desproporcional.

### Dependências e paralelismo

Depende de DEC-01 (CI) para prova hospedada e de DEC-N6 (garantia do gate) para o aceite da #123.

### Plano e aceite propostos

Passo mínimo: run do CI principal na main com `test_tail_outlier_package.py` e testes do watcher; decisão DEC-N6 registrada; controle negativo do gate com finding de outro stage.

### Comunicação entre responsáveis

Para a consolidação: "PR #127 entregou o tail-outlier com prova local de setembro; entrou sem review humana registrada e sem CI verde observado no head final; o gate associa só por job".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — sem ceder ao skew, o mesmo stage geraria dois findings. (b) Que caso o teste ainda não cobre? — finding de outro stage satisfazendo a busca textual. (c) Como eu explicaria isso para outro pod? — "o gate prova que o watcher disparou no job, não no stage certo". (d) A #123 deve fechar com essa garantia?

### Próxima ação e encerramento

Owner a confirmar: Pod 2, para a DEC-N6, e mantenedor, para a prova pós-integração. Encerramento: a PR segue integrada; o aceite segue na #123.

<a id="item-500"></a>

## PR#128 — test(package): make PowerShell coverage command-aware

Frente: historico. Encaminhamento: integrada_sem_review_formal_e_sem_ci_executado.

### Identidade e estado

PR #128, `gustocezar/issue-124-pwsh-coverage` → `main`; autor `gustocezar` (commits de "Augusto Silva" e "Augusto Cezar"); criada em 2026-09-20 e integrada em 2026-10-06T19:56:14Z (merge `d8c1a3c`); 5 commits; 7 arquivos. Relação: #124 (aberta), "Relates". Integrada na leva de 2026-10-06 (27 merges de PR entre 19:55:46Z e 20:32:30Z, com commits de merge do mantenedor, mais dois commits diretos na main, `fa0951f` e `c4541a5`), dentro do intervalo de 2026-09-20 a 2026-10-06 (created_at UTC) em que os 68 runs `CI` retornados pela API terminaram em `failure` (56) ou `cancelled` (12), sem `success` (`fontes/reconferencia/ponto01-intervalo-ci.json`; a contagem de 61 do pacote de 17/10 usava outro intervalo).

### Intenção e benefício

Tornar explícito e fechado no CI o contrato de comandos do pacote: verificar PowerShell 7 antes da raia de testes, falhar (não pular) sem `pwsh`, resolver um único plano de ação para execução real e `-DryRun` e reportar o handler escolhido.

### Feito, faltante e não comprovado

Feito: passo `Verify PowerShell 7` no `ci.yml` (+4), `scripts/apex.ps1` (+53/-12) com o plano de ação único, `tests/test_apex_initial_package.py` (+93/-6), TaskPlans e Task-Specs. Relatado: 18 testes focados e 69 da raiz. Limite apontado pelo Codex (C04-12) e coerente com o dispatcher conferido na ficha #64: o teste compara a string `Handler` em `-DryRun`, e o ramo retorna antes do `Command`; o critério da #124 (alcançar o handler de cada ação) segue aberto. Um commit de 2026-10-01 explica aspas ao shellcheck. Prova hospedada: o run do head (2026-10-01) tem 11 jobs com 0 steps (`fontes/git/_jobs-head-prs-outubro.json`). Reconfirmado em 19/10 na main: `-DryRun` imprime o rótulo `Handler` declarado ao lado do `Command`, e só `help` é despachado de fato (`scripts/apex.ps1:734-806`; `tests/test_apex_initial_package.py:17-80`).

### Linhagem

PR #92 (primeiros testes do pacote) → #124 → PR #128 → run do head sem steps na tentativa retornada → merge sem review (2026-10-06) → #124 aberta pela força do teste (Codex).

### Fontes e corte

Snapshot (PR 128); dossiê; `fontes/api-reviews/pr128-reviews.json` (0); `fontes/git/_jobs-head-prs-outubro.json`; `fontes/git/_runs-push-main-por-dia.txt`; `fontes/git/_64.txt` (dispatcher); correção C04-12 do Codex; `fontes/git/_entrada-na-main.json`.

### Classe e limite da evidência

DIRETO: arquivos, ausência de review e de steps. RELATADO: contagens de testes. INFERÊNCIA: a garantia "handler alcançado" não está provada. Review formal (API, observada em 2026-10-17T17:28:42Z): 0 registradas; isso não prova ausência de leitura humana. Comentários inline de review: 0. Runs do Actions com o head `2b84c7a` (universo retornado pela listagem pública em 2026-10-17: 213 runs, created_at de 2026-07-26 a 2026-10-12; não prova retenção integral da história de CI nem cobre tentativas anteriores à retornada; updated_at é proxy de conclusão do run): `CI` pull_request failure, run 36923303788, tentativa 1, created_at 2026-10-01 20:40:29Z, run_started_at 2026-10-01 20:40:29Z, updated_at 2026-10-01 20:40:34Z (antes do merge pelo updated_at); jobs coletados desta tentativa: 11, steps: 0.

### Fluxo

Fluxo testado: ação → plano único (`Handler`, `Command`) → `-DryRun` reporta o `Handler` → teste compara a string; execução real usaria `Command`.

### Consequências e risco

Médio: fecha o pulo silencioso sem `pwsh`, mas não discrimina troca de `Command`. Com o Ubuntu 26.04 listando PowerShell 7.6.6 no manifesto (DEC-N1), a exigência de `pwsh` no CI é compatível. Confiança limitada às fontes citadas; probabilidade/frequência operacional não estimada nesta auditoria.

### Alternativas e recomendação

(a) Manter integrada e completar a prova no #124 com handlers inofensivos (recomendado); (b) aceitar a prova atual mudando o escopo do #124 — decisão do mantenedor.

### Dependências e paralelismo

Depende de DEC-01 (CI disponível) para a prova hospedada e do critério aberto do #124 para o teste discriminante; não depende de outras PRs.

### Plano e aceite propostos

Passo mínimo no #124: teste que substitua cada `Command` por um handler inofensivo e prove a chamada; controle negativo: trocar `Command` sem trocar `Handler` deve falhar.

### Comunicação entre responsáveis

Para a consolidação: "PR #128 exige pwsh no CI; a prova de despacho ainda compara só o nome".

### Perguntas de revisão

(a) O que quebraria se fizéssemos diferente? — pular testes sem `pwsh` esconderia a falta de cobertura. (b) Que caso o teste ainda não cobre? — `Command` trocado com `Handler` igual. (c) Como eu explicaria isso para outro pod? — "o CI exige PowerShell; o teste ainda não prova qual função roda". (d) O #124 aceita prova por nome?

### Próxima ação e encerramento

Owner a confirmar: responsável pela #124. Entrada: este registro. Saída: teste discriminante ou mudança de escopo registrada. Encerramento: a PR segue integrada.

