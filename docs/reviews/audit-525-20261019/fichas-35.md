# Fichas documentais — lote 35

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-341"></a>

## W07 — Critérios prototype→validated para os quatro cenários

Frente: workspace_externo. Encaminhamento: externo_workspace_concluido_localmente_pr5.

### Identidade e estado

W07 é contrato/documentação do workspace: critérios prototype→validated para os quatro cenários. Implementado pela PR #5 do workspace (commits 35ed857 "docs: define scenario validation criteria" e aa077d9 "docs: require sustained scenario validation", merge 339e78e em 2026-09-25), visível no clone local; repositório 404 publicamente. Owner: Augusto.

### Intenção e benefício

Intenção: tornar objetiva a promoção de cenário para validated, sem validar prematuramente. Público: quem opera os cenários skew/no-skew/spill/no-spill. Ganho: critério único e verificável.

### Feito, faltante e não comprovado

Estado no clone local: tasks/backlog.md tem a seção "Critérios para promover cenário a validated" com tabela por cenário (contrato sintético e gate, par de controle, captura real custodiada, execução real mínima com 2+ cores e ≥8 tasks, confiança ≥0,80, verificação contra o real e workflow agendado verde por 2 semanas) e a lista "Não conta como validated". A PR alterou docs/specs/memory-watcher-v1.md, docs/specs/skew-slice-v4.md, tasks/apex_roadmap_v4.md e tasks/backlog.md (+47/-16). Falta neste ID: nada; a evidência real pertence a W02-W06.

### Linhagem

Registro W07 → PR #5, commits 35ed857/aa077d9 → merge 339e78e visível no clone → critérios documentais. Gate 36091594725, 53 testes e revisão independente permanecem relatos do registro.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/workspace-backlog.md; fontes/batch-revalidated-wdprops-sources/workspace-merges.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018/workspace-repo.json; fontes/batch-revalidated-wdprops-sources/workspace-pr5-diff.txt. Locadores: Registro/MATRIX W07; merge 339e78e, diffstat e tabela de critérios no backlog.

### Classe e limite da evidência

FATO OBSERVADO local: merge 339e78e e texto dos critérios no backlog. RELATO: gate 36091594725 SUCCESS, 53 testes e revisão independente. Nenhuma execução nesta revisão.

### Fluxo

Fluxo documental: evidências por cenário —(tabela de critérios)→ decisão de promoção —(todos os requisitos)→ validated; faltando um —(lista "não conta")→ continua prototype.

### Consequências e risco

Sem ação, nada muda; os critérios estão escritos. O risco é alguém promover um cenário só com o gate sintético; a lista explícita mitiga. Confiança alta no texto local.

### Alternativas e recomendação

Recomendado: encerrar W07 como concluído localmente. Alternativa: publicar os critérios no APEX (não pedido; o contrato de cenários vive no workspace, ver L15). Reversível.

### Dependências e paralelismo

Nenhuma dependência para encerrar. W02 a W06 usam os critérios como regra de promoção, mas nenhum deles bloqueia ou é bloqueado pelo encerramento deste item documental.

### Plano e aceite propostos

Condição de não ação: nenhum passo neste ID. Reabrir se os critérios forem alterados sem registro ou se um cenário for promovido sem cumprir a tabela.

### Comunicação entre responsáveis

Para outro pod: a PR #5 definiu critérios por cenário. No backlog fixado os quatro continuam prototype; não foi verificado o estado interno posterior do workspace.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Promover os quatro cenários em bloco apagaria diferenças de prova por cenário. Que caso o teste ainda não cobre? O gate sintético não demonstra captura real, controle negativo real nem duas semanas de verificação periódica. Como eu explicaria isso para outro pod? W07 conclui a definição documental; W02–W06 tratam evidências necessárias à promoção.

### Próxima ação e encerramento

Próxima ação: encerrar W07. Owner: nenhum necessário. Entrada: backlog em 339e78e. Saída: linha W07 "concluído localmente pela PR #5 (339e78e)". Encerramento: imediato.

<a id="item-342"></a>

## W08 — Cost Watcher

Frente: workspace_externo. Encaminhamento: estudar_em_paralelo_com_capturas.

### Identidade e estado

W08 é um estudo/feature do workspace: Cost Watcher (Pod A2). Repositório gustocezar/apex-workspace (404 anônimo). Owner: Augusto (a confirmar).

### Intenção e benefício

O backlog do workspace planeja um Cost Watcher e o marca não iniciado em 339e78e. A finalidade exata, inclusive custo monetário versus desperdício físico, precisa ser definida no estudo.

### Feito, faltante e não comprovado

Fonte local: backlog marca não iniciado. Em APEX c3c3ea3, cost.py implementa sinais determinísticos de amplificação de shuffle e leitura ampla; não é estimador monetário. Não foram procurados artefatos posteriores do workspace.

### Linhagem

Linhagem: plano de pods do workspace (Pod A2) → registro W08 (study_ready, deps W02-W05, rec defer) → backlog "não iniciado" em 25/09 → desenho [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/workspace-backlog.md; fontes/batch-revalidated-wdprops-sources/workspace-merges.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018/workspace-repo.json; fontes/batch-revalidated-wdprops-sources/apex-cost-c3c3ea3.py. Locadores: Registro/MATRIX W08; backlog Cost Watcher; cost.py em c3c3ea3, evaluate e SQL.

### Classe e limite da evidência

FATO OBSERVADO: rótulo não iniciado no backlog e regras do cost.py na base APEX. PROPOSTA: comparar escopos antes de duplicar responsabilidades; nenhuma execução.

### Fluxo

Fluxo proposto: event log real —(métricas de recursos e duração)→ Cost Watcher —(estimativa de custo com premissas declaradas)→ finding de custo. Não implementado.

### Consequências e risco

Sem ação, nada muda; é expansão futura do laboratório e não afeta o APEX. O risco de retomar sem olhar o watcher de custo do Engine é duplicar lógica em dois repositórios. Confiança alta.

### Alternativas e recomendação

Recomendado: iniciar estudo documental curto em paralelo às capturas, comparando finalidade, métricas e reutilização do Engine. Adiar implementação/prova real até confirmar requisitos e ambiente. O adiamento do registro é preferência histórica, não impedimento técnico para desenhar.

### Dependências e paralelismo

O registro relaciona W02–W05 à priorização e à futura prova real. Esses itens não são predecessores técnicos do estudo; premissas de preço só são necessárias se o escopo aprovado incluir custo monetário.

### Plano e aceite propostos

Menor entrega: comparar cost.py com a intenção do workspace, separar desperdício de estimativa financeira, declarar dados exigidos e decidir implementar/reutilizar/adiar. Aceite do estudo: fronteira e casos documentados; nenhuma captura ou teste novo para concluir esta revisão.

### Comunicação entre responsáveis

Para outro pod: o Engine detecta desperdício físico; o workspace ainda precisa decidir se busca o mesmo diagnóstico ou custo monetário. O estudo pode correr agora.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Reutilizar um detector de desperdício como preço monetário sem premissas produziria interpretação errada. Que caso o teste ainda não cobre? Não há prova lida de estimativa monetária entre ambientes; o código inspecionado cobre relações de bytes. Como eu explicaria isso para outro pod? O estudo define a finalidade do Cost Watcher antes de escolher dados, implementação e prova.

### Próxima ação e encerramento

Próxima ação: Augusto, a confirmar, preparar a comparação de escopo. Entrada: backlog e cost.py c3c3ea3. Saída: decisão documentada implementar/reutilizar/adiar; prova runtime pertence a uma etapa futura.

<a id="item-343"></a>

## W09 — Tiers 2–4 de LLM

Frente: workspace_externo. Encaminhamento: estudar_protocolo_offline.

### Identidade e estado

W09 é um estudo/eval do workspace: Tiers 2-4 de LLM (classificador, coordenador e juiz do crew). Repositório gustocezar/apex-workspace (404 anônimo em 18/10). Owner: Augusto (a confirmar).

### Intenção e benefício

A tabela histórica mantém modelos por papel em estado testando; esse rótulo não demonstra execuções atuais nem resultados. O objetivo documental é definir comparação rastreável por tier.

### Feito, faltante e não comprovado

README de llm-evals em 339e78e já contém objetivo, tiers, estrutura de pastas e template com diagnóstico, latência, custo e conclusão. Não é correto dizer que falta tudo do protocolo. Resultados preenchidos e execução não foram verificados.

### Linhagem

Plano histórico → backlog por tiers → README com template → registro W09 recomenda adiar. Protocolo detalhado, casos fixos e resultados completos não demonstrados no recorte.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/workspace-backlog.md; fontes/batch-revalidated-wdprops-sources/workspace-merges.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018/workspace-repo.json; fontes/batch-revalidated-wdprops-sources/workspace-evals-readme.md. Locadores: Registro/MATRIX W09; README llm-evals integral e tabela histórica do backlog.

### Classe e limite da evidência

FATO OBSERVADO: template e tabela de status. RELATO HISTÓRICO: avaliações em andamento. Não foi executado eval nem inferida ausência universal de resultados.

### Fluxo

Fluxo proposto: casos determinísticos com resposta conhecida —(modelo por tier)→ saída —(métrica do tier)→ escolha registrada. Não implementado.

### Consequências e risco

Sem ação, o crew continua sem escolha formal de modelos por papel; nada muda no APEX. O risco é a tabela sugerir testes em curso que não existem. Confiança alta.

### Alternativas e recomendação

Recomendado: detalhar protocolo offline a partir do template, com casos determinísticos e métricas; avaliar posteriormente modelos conforme autorização e orçamento. Cenários validated não são requisito universal para definir ou testar protocolo offline.

### Dependências e paralelismo

O desenho requer definição de resposta esperada e métricas, não capturas reais nem credenciais. Execuções futuras dependem de modelos, dados e orçamento autorizados; generalização ao real exige prova correspondente.

### Plano e aceite propostos

Passos documentais: escolher casos por tier e controles, definir resultado esperado e critério de abstenção, registrar versão/configuração/data/custo, separar resultado observado de julgamento. Aceite: protocolo revisável com template preenchível; nenhuma execução neste lote.

### Comunicação entre responsáveis

Para outro pod: já existe um template histórico; podemos completar o protocolo offline sem promover cenários nem presumir resultados de modelos.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Comparar modelos com casos ou métricas diferentes tornaria a seleção por tier incomparável. Que caso o teste ainda não cobre? O template não comprova desempenho medido, reprodutibilidade ou generalização a logs reais. Como eu explicaria isso para outro pod? O protocolo pode ser desenhado offline; qualquer resultado futuro deve identificar modelo, configuração, data e dados.

### Próxima ação e encerramento

Próxima ação: Augusto, a confirmar, completar protocolo com casos fixos e métricas por tier. Entrada: README e backlog. Saída: protocolo revisável; encerramento do estudo quando houver critérios definidos e decisão sobre execução futura.

<a id="item-344"></a>

## W10 — Manter roadmap histórico marcado

Frente: workspace_externo. Encaminhamento: encerrar_superado_roadmap_marcado_historico.

### Identidade e estado

W10 é documentação do workspace: manter o roadmap histórico marcado como tal. O registro o dá como coberto pela PR #4 (successor P09). Repositório gustocezar/apex-workspace (404 anônimo). Owner: nenhum necessário.

### Intenção e benefício

Intenção: impedir que o roadmap de junho seja lido como plano atual. Público: quem planeja pelo workspace. Ganho: um único documento operacional (tasks/backlog.md).

### Feito, faltante e não comprovado

Verificação no clone local: tasks/apex_roadmap_v4.md começa com "Registro histórico do plano v4 de 08 jun 2026. Para o estado operacional, use tasks/backlog.md" e traz uma atualização de reconciliação de 23/09. Feito. Falta: nada.

### Linhagem

Linhagem: roadmap v4 de 08/06 → reconciliação de 23/09 (da0e938) → PR #4 → merge e71b1bf → PR #5 também toca o roadmap → registro W10 (superseded, successor P09).

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/workspace-backlog.md; fontes/batch-revalidated-wdprops-sources/workspace-merges.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018/workspace-repo.json; fontes/batch-revalidated-wdprops-sources/workspace-roadmap.md. Locadores: Registro W10, MATRIX W10 e cabeçalho/reconciliação do roadmap em 339e78e.

### Classe e limite da evidência

FATO OBSERVADO local: marcação histórica presente no topo do roadmap em 339e78e. RELATO: nenhum adicional. Nenhuma execução nesta revisão; repositório não verificável publicamente.

### Fluxo

Fluxo documental: leitor —(abre o roadmap v4)→ aviso de registro histórico no topo —(redireciona)→ tasks/backlog.md, que tem o estado operacional e os critérios da PR #5.

### Consequências e risco

Sem ação, nada muda: o aviso já existe. O risco residual é alguém abrir uma cópia antiga do roadmap fora da branch cowork. Confiança alta no estado local.

### Alternativas e recomendação

Recomendado: encerrar W10 como superado por P09/PR #4. Alternativa: mover o roadmap para uma pasta de arquivo (mais explícito, não necessário). Reversível.

### Dependências e paralelismo

Nenhuma dependência para encerrar. P09 concentra a verificação externa do workspace e não depende deste item; W07 (critérios) também é independente.

### Plano e aceite propostos

Condição de não ação: nenhum passo neste ID. Reabrir se o aviso histórico for removido do roadmap sem que outro documento assuma o papel operacional.

### Comunicação entre responsáveis

Para outro pod: "O roadmap v4 do workspace está marcado como histórico no próprio arquivo; o estado atual e os critérios de cenário ficam em tasks/backlog.md."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Ler o roadmap de junho como atual retomaria pendências já reconciliadas. Que caso o teste ainda não cobre? O aviso histórico não prova o estado de cópias antigas nem resultados de execução. Como eu explicaria isso para outro pod? O roadmap preserva a história e encaminha para tasks/backlog.md no clone fixado.

### Próxima ação e encerramento

Próxima ação: encerrar W10. Owner: nenhum necessário. Entrada: cabeçalho do roadmap. Saída: linha W10 "superado; roadmap marcado histórico". Encerramento: imediato.

<a id="item-345"></a>

## W11 — Resíduos do backlog após PR #4

Frente: workspace_externo. Encaminhamento: encerrar_concluido_pr4.

### Identidade e estado

W11 é documentação do workspace: resíduos do backlog após a PR #4. Registro: concluído pela NA-10 em 25/09 (tasks/backlog.md em 4d46173; merge e71b1bf). Repositório gustocezar/apex-workspace (404 anônimo). Owner: nenhum necessário.

### Intenção e benefício

O registro descreve ações obsoletas sobre #17/#19/#20/#28 e referência ADR ambígua. O diff confirma sua remoção e a preservação de #21. Issues fechadas podem receber comentários; o problema documentado é obsolescência, não impossibilidade técnica de comentar.

### Feito, faltante e não comprovado

Leitura do diff 4d46173 confirma remoção das quatro ações e de Abrir ADR-004, mantendo comentário/phase label #21. O merge e71b1bf está visível no clone. Estado remoto e gate não foram reconsultados.

### Linhagem

Linhagem: NA-10 de 25/09 → commit 4d46173 na branch codex/reconcile-workspace-docs → PR #4 → gate 36090577225 SUCCESS (relato) → merge e71b1bf → registro W11 (merged_current).

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/workspace-backlog.md; fontes/batch-revalidated-wdprops-sources/workspace-merges.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018/workspace-repo.json; fontes/batch-revalidated-wdprops-sources/workspace-w11-diff.txt. Locadores: Registro/MATRIX W11; diff 4d46173 e merge e71b1bf.

### Classe e limite da evidência

FATO OBSERVADO: diff 4d46173 preserva #21 e remove entradas descritas; merge e71b1bf local. RELATO: gate 36090577225 SUCCESS e estado fechado das issues na reconciliação histórica.

### Fluxo

Fluxo documental: backlog com ações obsoletas —(NA-10)→ remoção das ações sobre issues fechadas e do ADR ambíguo —(merge)→ backlog operacional limpo.

### Consequências e risco

Sem ação, nada muda: o backlog já foi limpo. O risco é o backlog voltar a acumular ações sobre issues fechadas sem revisão periódica. Confiança alta no estado local.

### Alternativas e recomendação

Recomendado: encerrar W11 como concluído. Alternativa futura: verificação periódica que liste issues citadas no backlog e o estado delas. Reversível.

### Dependências e paralelismo

Nenhuma dependência. O encerramento não depende de P09, da visibilidade pública do workspace nem de outros itens W; o commit e o merge já estão no clone local.

### Plano e aceite propostos

Condição de não ação: nenhum passo neste ID. Reabrir se o backlog voltar a listar ações sobre issues fechadas ou referências ambíguas a ADRs.

### Comunicação entre responsáveis

Para outro pod: "O backlog do workspace deixou de pedir ações sobre issues já fechadas (PR #4) e manteve a #21; o ADR-004 do workspace não é o ADR-004 do APEX."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Manter ações obsoletas confundiria o operador sobre o que ainda precisa decidir. Que caso o teste ainda não cobre? O diff documental não comprova estado atual das issues nem execução do gate histórico. Como eu explicaria isso para outro pod? W11 limpou a seção de ações e preservou #21; não altera código ou o ADR-004 do APEX.

### Próxima ação e encerramento

Próxima ação: encerrar W11. Owner: nenhum necessário. Entrada: commit 4d46173. Saída: linha W11 "concluído em 4d46173/e71b1bf". Encerramento: imediato.

<a id="item-346"></a>

## W12 — Ligar workspace issue #1 ao dataship PR #1

Frente: workspace_externo. Encaminhamento: externo_governanca_aguarda_decisao_upstream.

### Identidade e estado

W12 é governança do workspace/laboratório: ligar a issue #1 do workspace à PR #1 do Dataship (Gabriel-Philot/dataship-spark-plat-v0#1, aberta, head e0ed228). Repositório do workspace 404 anônimo. Owner: Augusto (a confirmar).

### Intenção e benefício

O registro atribui à issue #1 do workspace a origem da PR #1 Dataship. No corpo público da PR capturado em 18/10 não aparece esse vínculo; o lado workspace não foi acessado, portanto não se conclui ausência bilateral.

### Feito, faltante e não comprovado

PR #1 aberta no snapshot, head e0ed228, corpo sem referência ao workspace. Verificar referência já existente na issue antes de propor comentário; a ligação pode preceder merge, enquanto o fechamento depende de reconciliar seus critérios.

### Linhagem

Origem workspace #1 é relato do registro → PR Dataship #1 aberta em e0ed228 → ligação não encontrada no corpo da PR; lado workspace não verificado → decisão upstream e fechamento pendentes no recorte.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/workspace-backlog.md; fontes/batch-revalidated-wdprops-sources/workspace-merges.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018/workspace-repo.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018/dataship-pulls.json. Locadores: Registro/MATRIX W12; corpo e metadados da PR Dataship #1 em dataship-pulls.json.

### Classe e limite da evidência

FATO OBSERVADO: corpo da PR #1 do Dataship sem referência ao workspace (GET de 18/10). Limite explícito: o lado do workspace não é verificável publicamente. Nenhuma execução.

### Fluxo

Fluxo proposto: issue #1 do workspace —(comentário com link)→ PR #1 do Dataship —(decisão upstream)→ fechamento da issue citando o merge ou o motivo de fechamento da PR.

### Consequências e risco

Sem ação, a origem da correção de output compartilhado fica difícil de rastrear; não há impacto técnico no APEX nem no laboratório. Confiança alta no lado público.

### Alternativas e recomendação

Recomendado: comentar já na issue do workspace (repositório do próprio usuário) com o link da PR, sem esperar o merge; fechar após o merge. Alternativa: esperar o merge para fazer tudo de uma vez (como o registro propõe). Ambos reversíveis; o primeiro deixa rastro mais cedo.

### Dependências e paralelismo

Depende de P10 (decisão upstream) apenas para o fechamento; o comentário de ligação depende só de acesso do usuário ao workspace e pode ser feito a qualquer momento.

### Plano e aceite propostos

Passo futuro autorizado: inspecionar a issue do workspace e seus critérios; se faltar vínculo, acrescentá-lo preservando referências existentes. Após decisão upstream, registrar merge ou motivo de não integração e reconciliar o fechamento. Esta revisão não envia mensagens.

### Comunicação entre responsáveis

Para outro pod: o registro conecta workspace #1 e Dataship #1; o corpo público da PR não cita a origem, e falta verificar o lado workspace. O crosslink pode preceder merge.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Fechar sem explicitar a decisão upstream apagaria a rastreabilidade da intenção. Que caso o teste ainda não cobre? O recorte não verifica o conteúdo da issue workspace #1, portanto não demonstra ausência de link nela. Como eu explicaria isso para outro pod? O vínculo documental pode ser preparado antes da integração; o fechamento conserva critérios próprios.

### Próxima ação e encerramento

Próxima ação: Augusto (a confirmar) decide se comenta já ou espera o merge. Entrada: link da PR #1. Saída: referência cruzada. Encerramento: issue fechada citando a decisão upstream.

<a id="item-347"></a>

## D01 — Validar E2E o volume compartilhado da PR #1

Frente: dataship_externo. Encaminhamento: encerrar_superado_por_p10.

### Identidade e estado

D01 é runtime do laboratório: validar E2E o volume compartilhado da PR #1 do Dataship (Gabriel-Philot/dataship-spark-plat-v0#1, aberta, head e0ed228). O registro já o marca superado, com successor P10, porque o corpo da PR relata o E2E concluído. Owner: autor da PR (gustocezar) e mantenedor upstream.

### Intenção e benefício

Intenção: provar que, com o volume compartilhado entre spark-master e spark-worker, o FileOutputCommitter grava part-files e _SUCCESS no caminho visível no host. Público: quem usa o laboratório com output local. Ganho: confiança na correção antes do merge upstream.

### Feito, faltante e não comprovado

Verificação: o corpo da PR #1 (GET de 18/10) descreve que master e worker rodam com filesystems locais independentes, que o FileOutputCommitter v1 precisa de filesystem compartilhado e que a PR monta ./var/local-output nos dois; o registro diz que o corpo relata E2E com 2 part-files e _SUCCESS visíveis em master, worker e host. Falta neste ID: nada; reprodução independente é opcional.

### Linhagem

Linhagem: issue #1 do workspace → D01 (validação E2E) → PR #1 (23/09) com E2E relatado no corpo → registro D01 (superseded, successor P10) → decisão upstream em P10. Sem elo ausente para o encerramento.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018/dataship-pulls.json. Locadores: Registro/MATRIX D01; PR #1, head e0ed228, corpo e estado aberto no snapshot de 18/10.

### Classe e limite da evidência

RELATO: E2E dirigido descrito no corpo da PR #1 (dois part-files e _SUCCESS visíveis). FATO OBSERVADO: PR aberta, sem merge, em 18/10. Nenhuma execução nem reprodução nesta revisão.

### Fluxo

Fluxo validado segundo o relato: job Spark —(tarefas no worker)→ /opt/spark/local-output compartilhado —(commit do job no driver)→ part-files e _SUCCESS no mesmo caminho —(montagem)→ host.

### Consequências e risco

Sem ação, nada muda; a validação está descrita na própria PR. O risco é tratar o relato como reprodução independente; a classificação deixa claro que não é. Confiança média no E2E (relato).

### Alternativas e recomendação

Recomendado: encerrar D01 como superado por P10. Alternativa: reprodução independente antes do merge (útil se o mantenedor pedir). Reversível.

### Dependências e paralelismo

Nenhuma dependência para encerrar. P10 concentra a decisão upstream sobre a PR #1, e W12 trata a referência cruzada com a issue do workspace; nenhum dos dois é gate deste encerramento.

### Plano e aceite propostos

Condição de não ação: nenhum passo neste ID. Se o mantenedor pedir reprodução, ela é feita no contexto de P10, com o mesmo critério (part-files e _SUCCESS visíveis no host).

### Comunicação entre responsáveis

Para outro pod: "A validação E2E do volume compartilhado do Dataship está descrita na própria PR #1; acompanhe a decisão upstream em P10 e não trate o relato como reprodução independente."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Tratar _SUCCESS isolado como prova de part-files visíveis ao host permitiria aceitar escrita incompleta para o consumidor. Que caso o teste ainda não cobre? O relato dirigido não demonstra múltiplos workers, retries nem reprodução independente no head atual. Como eu explicaria isso para outro pod? D01 preserva a origem da validação relatada e remete a decisão upstream para P10.

### Próxima ação e encerramento

Próxima ação: encerrar D01 com ponteiro para P10. Owner: nenhum necessário. Entrada: corpo da PR #1. Saída: linha D01 "superado por P10". Encerramento: imediato.

<a id="item-348"></a>

## D02 — Refatorar loader Go por responsabilidade

Frente: dataship_externo. Encaminhamento: externo_dataship_refatoracao_decisao_upstream.

### Identidade e estado

D02 é um refactor do laboratório Dataship: refatorar o loader Go por responsabilidade. Minuta local PROP-D02-LOADER-MODULARIZATION (revista pelo Codex). Repositório público Gabriel-Philot/dataship-spark-plat-v0; decisão do mantenedor upstream (DEC-20). Owner a confirmar.

### Intenção e benefício

Problema: build/images/eventlog-loader/main.go tem 582 linhas no origin/main 8920273 (2026-05-24) e não há testes Go na main; acrescentar tabelas (D03-D06) num arquivo único sem testes é arriscado. Público: quem estende o loader. Ganho: base modular e testável para novas entidades.

### Feito, faltante e não comprovado

Verificação: main.go com 582 linhas e a pasta do loader só com Dockerfile, go.mod, main.go e .dockerignore na main; o próprio upstream, em docs/logs-info/exploration-roadmap.md ("Suggested Next Implementation Order"), coloca como passo 1 "Refactor the Go loader into small packages by responsibility … while keeping current behavior unchanged". Feito: candidato de testes D09 (local) e dependências D15 (PR #2) como proteção. Falta: decomposição e prova de equivalência. Não comprovado: nada.

### Linhagem

Linhagem: roadmap de exploração do upstream (maio) → registro D02 (study_ready, depende de D09) → minuta PROP-D02 → PR #2 (D15) aberta → candidato TS11 (D09) local → refatoração [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-loader.go; fontes/batch-revalidated-wdprops-sources/dataship-ddl.sql; fontes/batch-revalidated-wdprops-sources/dataship-roadmap.md; fontes/batch-revalidated-wdprops-sources/dataship-tree.txt; fontes/batch-proposals-review-sources/PROP-D02-LOADER-MODULARIZATION.md. Locadores: Registro/MATRIX D02; main.go integral (582 linhas), árvore e ordem do exploration-roadmap.

### Classe e limite da evidência

FATO OBSERVADO: tamanho do arquivo, ausência de testes na main e ordem sugerida pelo próprio upstream. PROPOSTA: refatoração. DECISÃO PENDENTE: mantenedor upstream. Nenhuma execução.

### Fluxo

Fluxo atual lido: MinIO → readEventLog (linhas JSON, app_id e roteamento de tipos) → insertResult → tabelas normalizadas e raw; markFile registra o arquivo. ensureSchema repete o DDL. Proposta: separar leitura, parsing e escrita mantendo o mesmo contrato.

### Consequências e risco

Sem refatoração, cada tabela nova aumenta o arquivo único e o risco de regressão sem teste; o impacto é só no laboratório. Confiança alta no diagnóstico estático.

### Alternativas e recomendação

Recomendado: proteger com os testes de D09 antes, e refatorar em passos pequenos com equivalência demonstrada. Alternativas: estender sem refatorar (Codex: D03-D06 não precisam de refatoração completa se a extensão for revisável); reescrever (alto risco). Reversível por commits pequenos.

### Dependências e paralelismo

D09 fornece proteção de comportamento e D15 uma opção de reprodução offline. O inventário e desenho da decomposição podem começar já; a integração upstream de D15/D09 é ordem recomendada, não condição para estudar. Extensões D03–D06 podem ser pequenas e revisáveis sem refatoração completa.

### Plano e aceite propostos

Inventariar responsabilidades e as duas definições de schema, definir equivalência sobre arquivo fixo e extrair partes pequenas. Em futura implementação autorizada, usar testes de comportamento; aceitar somente sem alterar linhas normalizadas, raw, identidade e marcação de arquivos. Adoção upstream continua decisão do mantenedor.

### Comunicação entre responsáveis

Para outro pod: "O loader do Dataship é um arquivo de 582 linhas sem testes na main; o próprio autor sugere modularizar antes de novas tabelas, mas isso é decisão dele e não do APEX."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Mover parsing ou marcação de arquivos sem equivalência pode alterar identidade, linhas descartadas ou repetição de ingestão. Que caso o teste ainda não cobre? Não há prova nesta revisão de equivalência após decomposição, incluindo JSON inválido, ausência de app_id e arquivo parcialmente ingerido. Como eu explicaria isso para outro pod? D02 propõe modularizar o laboratório; o desenho pode começar offline e não bloqueia a v1 do APEX.

### Próxima ação e encerramento

Próxima ação: mantenedor upstream (a confirmar) decide sobre D15/D09 e a refatoração. Entrada: PR #2 e candidato TS11. Saída: decisão upstream. Encerramento: refatoração integrada ou rejeitada upstream.

<a id="item-349"></a>

## D03 — Adicionar spark_jobs

Frente: dataship_externo. Encaminhamento: externo_dataship_tabela_spark_jobs.

### Identidade e estado

D03 é schema/loader do laboratório: adicionar a tabela spark_jobs. Minuta local PROP-D03-SPARK-JOBS (revista pelo Codex). Repositório Gabriel-Philot/dataship-spark-plat-v0; decisão do mantenedor upstream. Owner a confirmar.

### Intenção e benefício

Problema observado no DDL e no roteamento: não há entidade normalizada spark_jobs. A análise SQL→job→stage exige reconstruir eventos raw; a ausência da tabela não torna toda análise por job impossível. Ganho proposto: navegação direta por job.

### Feito, faltante e não comprovado

Verificação: 001_spark_observability.sql no origin/main cria seis tabelas (spark_eventlog_files, spark_raw_events, spark_sql_executions, spark_sql_execution_ends, spark_stages, spark_tasks), sem spark_jobs; o roadmap de exploração descreve spark_jobs a partir de SparkListenerJobStart/End com app_id, job_id, tempos, result, stage_ids e sql_execution_id. Falta: DDL, parsing e contrato de cardinalidade. Não comprovado: nada.

### Linhagem

Linhagem: roadmap de exploração do upstream (passo 2 da ordem sugerida) → registro D03 (study_ready, deps D02/D09) → minuta PROP-D03 revista pelo Codex → contrato e implementação [ausentes].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-loader.go; fontes/batch-revalidated-wdprops-sources/dataship-ddl.sql; fontes/batch-revalidated-wdprops-sources/dataship-roadmap.md; fontes/batch-revalidated-wdprops-sources/dataship-tree.txt; fontes/batch-proposals-review-sources/PROP-D03-SPARK-JOBS.md. Locadores: Registro/MATRIX D03; DDL, readEventLog/insertResult e seção spark_jobs do roadmap.

### Classe e limite da evidência

FATO OBSERVADO: tabela spark_jobs ausente no DDL da main e especificada no roadmap do próprio upstream. PROPOSTA: implementar. DECISÃO PENDENTE: mantenedor upstream. Nenhuma execução.

### Fluxo

Fluxo proposto: SparkListenerJobStart/JobEnd —(app_id, job_id, stage_ids, sql_execution_id das properties)→ loader —(INSERT)→ spark_jobs —(junções)→ spark_sql_executions e spark_stages.

### Consequências e risco

Sem a tabela, análises por job no laboratório ficam impossíveis ou exigem parsing de eventos brutos; o APEX tem seu próprio modelo de stage e não depende disso. Confiança alta no estado.

### Alternativas e recomendação

Recomendado: definir o contrato (chave, eventos parciais sem JobEnd, jobs sem SQL) antes do DDL; implementar como extensão revisável, sem exigir a refatoração completa. Alternativa: derivar jobs de spark_raw_events em views (sem mudar o loader). Reversível.

### Dependências e paralelismo

D09 e a política de dependências D15 ajudam a implementação; não impedem desenhar contrato e fixtures offline. D04 usa a identidade definida aqui. D02 é ordem sugerida pelo upstream, sem necessidade demonstrada de concluir toda a refatoração primeiro.

### Plano e aceite propostos

Passos mínimos: (1) contrato; (2) DDL; (3) parsing com teste em fixture; (4) caso negativo: job sem JobEnd; (5) consulta de exemplo SQL→job→stage. Aceite: ponte navegável numa fixture.

### Comunicação entre responsáveis

Para outro pod: "O laboratório Dataship ainda não registra jobs Spark; a minuta propõe a tabela que o próprio autor listou como próximo passo."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Usar apenas job_id, sem contexto de aplicação, pode ligar execuções de aplicações distintas; descartar jobs sem SQL pode ocultar trabalho legítimo. Que caso o teste ainda não cobre? Faltam critérios para JobEnd ausente, eventos repetidos e fora de ordem, job sem SQL e IDs repetidos entre aplicações. Como eu explicaria isso para outro pod? D03 normaliza os jobs do laboratório a partir de raw; o modelo e as consultas podem ser estudados antes de implementar.

### Próxima ação e encerramento

Próxima ação: mantenedor upstream (a confirmar) decide prioridade. Entrada: roadmap de exploração e minuta. Saída: contrato aprovado. Encerramento: tabela integrada ou rejeitada upstream.

<a id="item-350"></a>

## D04 — Adicionar spark_sql_execution_jobs

Frente: dataship_externo. Encaminhamento: externo_dataship_ponte_sql_job.

### Identidade e estado

D04 é schema/loader do laboratório: adicionar spark_sql_execution_jobs, a ponte entre execuções SQL e jobs. Minuta local PROP-D04-SPARK-SQL-EXECUTION-JOBS (revista pelo Codex). Repositório Gabriel-Philot/dataship-spark-plat-v0; decisão upstream. Owner a confirmar.

### Intenção e benefício

Problema: uma execução SQL dispara vários jobs; sem a tabela de ligação, a consulta precisa extrair o vínculo de spark_raw_events toda vez. Público: quem analisa execuções SQL no laboratório. Ganho: junção direta SQL → jobs.

### Feito, faltante e não comprovado

Verificação: o passo 2 do "Suggested Next Implementation Order" diz "Add spark_jobs and spark_sql_execution_jobs bridge tables"; nenhuma das duas existe na main. Falta: depende da identidade de job de D03. Não comprovado: nada.

### Linhagem

Linhagem: roadmap de exploração do upstream (passo 2, junto com spark_jobs) → registro D04 (study_ready, depende de D03) → minuta PROP-D04 → decisão tabela × coluna [ausente] → implementação [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-revalidated-wdprops-sources/dataship-loader.go; fontes/batch-revalidated-wdprops-sources/dataship-ddl.sql; fontes/batch-revalidated-wdprops-sources/dataship-roadmap.md; fontes/batch-revalidated-wdprops-sources/dataship-tree.txt; fontes/batch-proposals-review-sources/PROP-D04-SPARK-SQL-EXECUTION-JOBS.md. Locadores: Registro/MATRIX D04; ausência da ponte no DDL/loader, passo 2 do roadmap e minuta D04.

### Classe e limite da evidência

FATO OBSERVADO: ponte SQL→job ausente no DDL da main; o upstream a pede no mesmo passo de spark_jobs. PROPOSTA: implementar após D03. Nenhuma execução.

### Fluxo

Fluxo proposto: SparkListenerJobStart —(property spark.sql.execution.id)→ loader —(par execution_id, job_id)→ spark_sql_execution_jobs —(junção)→ spark_sql_executions × spark_jobs.

### Consequências e risco

Sem a ponte, a análise SQL→job continua possível, mas cara e frágil via eventos brutos em spark_raw_events; o impacto é só no laboratório. Confiança alta no estado.

### Alternativas e recomendação

Recomendado: desenhar junto com D03, comparando coluna sql_execution_id com tabela de pares. A minuta propõe N:M, mas o roadmap não demonstra essa cardinalidade; ela deve ser justificada por casos de evento e identidade. Alternativa: coluna com vínculo opcional quando 1:N for suficiente.

### Dependências e paralelismo

Depende de D03 (identidade de job e evento JobStart). Pode ser desenhado no mesmo contrato de D03 e implementado na mesma mudança, se o mantenedor preferir.

### Plano e aceite propostos

Definir identidade com app_id e política de vínculo ausente, decidir coluna ou tabela com evidência de cardinalidade, documentar fixtures de uma execução com vários jobs e de job sem SQL. Implementação e execução futura ficam fora desta revisão; aceite deve incluir ausência de junções entre aplicações.

### Comunicação entre responsáveis

Para outro pod: "A ponte SQL→job do Dataship é parte do mesmo passo do autor que adiciona a tabela de jobs; ela não faz sentido sozinha e deve ser decidida junto com D03."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Pressupor N:M sem caso justificável amplia o modelo; pressupor vínculo sempre presente exclui jobs que não vêm de SQL. Que caso o teste ainda não cobre? Ainda falta validar múltiplos jobs por execução, job sem execução SQL e reutilização de IDs entre aplicações. Como eu explicaria isso para outro pod? D04 é a proposta de vínculo SQL→job do Dataship e compartilha o contrato de identidade com D03.

### Próxima ação e encerramento

Próxima ação: decidir junto com D03. Owner: mantenedor upstream (a confirmar). Entrada: contrato de D03. Saída: escolha tabela × coluna. Encerramento: integrada ou rejeitada upstream.

