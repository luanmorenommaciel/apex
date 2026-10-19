# Fichas documentais — lote 26

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-251"></a>

## X15 — Juiz externo Claude com circuito aberto

Frente: tooling_juiz_externo. Encaminhamento: encerrar_sem_acao_circuito_aberto_registrado.

### Identidade e estado

X15 é um estado operacional de tooling local: o juiz externo Claude do loop autônomo com circuito aberto. Sem objeto público APEX. Registro: sem ação; reabrir só com novo digest ou reset humano. Responsável: dono do loop (a confirmar).

### Intenção e benefício

Intenção: o loop autônomo de agosto usava um juiz externo apenas consultivo para revisar bundles; depois de falhas repetidas, um disjuntor impede novas chamadas até reset. Público: quem operar o loop de novo. Ganho: não gastar créditos nem gerar ruído com um juiz que falha.

### Feito, faltante e não comprovado

Verificação de 18/10 no STATE.json da custódia: external_judge com enabled true, advisory_only true, circuit_reset "new_bundle_digest_or_explicit_human_reset"; last_external_judge_run com circuit_open true, attempt_count 3, category claude_exit_1, completed_at 2026-08-31T05:50:31Z, candidato synthetic-wrapper-smoke-budget-030. Falta: nada, a menos que o loop volte a ser usado. Não comprovado: causa do claude_exit_1.

### Linhagem

Linhagem: loop autônomo de 30/08 → smoke do juiz em 31/08 com três falhas → circuito aberto → registro X15 (no_action) → STATE.json preservado na custódia → verificação de 18/10. Sem follow-up.

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/local-readonly-receipt.json x15, extrato sanitizado das chaves external_judge e last_external_judge_run com hash do STATE original; fontes/batch-revalidated-xldd-sources/selected-register-matrix.json X15. O recibo não consulta o loop em execução.

### Classe e limite da evidência

FATO OBSERVADO: STATE registra advisory_only=true, enabled=true, circuit_open=true e tentativa de 31/08 com claude_exit_1. RELATO HISTÓRICO: falhas e disjuntor descritos no registro. INFERÊNCIA LIMITADA: configuração é consultiva; nenhum gate de aceite dependente foi demonstrado neste recorte. Uso atual do loop e causa do exit não verificados.

### Fluxo

Fluxo registrado: bundle/digest —(até três tentativas consultivas)→ juiz → falhas → disjuntor aberto —(novo digest ou reset humano conforme configuração)→ elegibilidade para tentar. Isso descreve o STATE, não operação observada agora.

### Consequências e risco

Sem reativação demonstrada, não há impacto atual de produto comprovado. Risco de custo/ruído se o loop for retomado sem entender a falha; configuração consultiva não permite afirmar ausência universal de dependências.

### Alternativas e recomendação

Recomendado: manter encerrado; se o loop voltar, investigar o claude_exit_1 antes do reset. Alternativa: remover o juiz da configuração para evitar confusão. Reversível.

### Dependências e paralelismo

Nenhuma dependência e nenhum item deste recorte depende do juiz externo. Se o loop autônomo voltar a ser usado, a investigação do claude_exit_1 vem antes do reset do disjuntor.

### Plano e aceite propostos

Condição de não ação: nenhum passo. Reabrir se o loop autônomo voltar a ser usado ou se o juiz for exigido por algum processo de aceite; nesse caso, registrar a causa do claude_exit_1 antes do reset.

### Comunicação entre responsáveis

Para outro pod: “O STATE registra circuito aberto desde 31/08 para juiz consultivo; não inspecionamos o loop rodando nem todos os processos de aceite.”

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere resetar o circuito sem entender o exit histórico. Que caso o teste ainda não cobre? O STATE não testa uso atual do loop nem todas as dependências de aceite. Como eu explicaria isso para outro pod? Explique configuração consultiva e circuito registrado, sem presumir operação atual.

### Próxima ação e encerramento

Próxima ação: nenhuma; registrar como encerrado. Owner: nenhum necessário. Entrada: STATE.json. Saída: linha X15 "circuito aberto desde 2026-08-31, consultivo". Encerramento: imediato.

<a id="item-252"></a>

## X16 — Vincular Task-Specs ao workspace correto

Frente: tooling_taskspec. Encaminhamento: externo_tooling_premissa_atualizada.

### Identidade e estado

X16 é um processo de tooling (Governança/Task-Spec), fora do repositório APEX: vincular Task-Specs ao workspace correto. Registro: as sete análises de 21/09 ficaram accepted=false (BLAST_RADIUS/EVAL_FAILED) porque os handoffs apontavam para Documents/Apex, então um clone do workspace em base-project-e2e-augusto e66b28b. Responsável: Augusto (a confirmar).

### Intenção e benefício

Problema: aceites formais de Task-Spec dependem de o handoff apontar para o repositório e base corretos; apontar para outro clone gera falso EVAL_FAILED. Público: quem quiser aceitar formalmente trabalho daquela rodada. Ganho: aceites possíveis sem afrouxar gates.

### Feito, faltante e não comprovado

Verificação de 18/10: Documents/Apex está hoje em HEAD c3c4119 na branch codex/preserve-apex-knowledge-20260924 (o mesmo source_commit registrado no CUSTODY-METADATA.json), não mais em e66b28b; tasks/_state.yaml existe. A premissa histórica do registro mudou. Falta: decidir se algum handoff ainda precisa de reemissão em clone limpo da main e se as autorizações existentes cobrem isso. Não comprovado: estado dos 11 specs ready.

### Linhagem

Linhagem: rodada de 21/09 → sete análises accepted=false → diagnóstico do workspace errado → DEC-18 cobre só a custódia → Documents/Apex movido para a branch de preservação (c3c4119) → reemissão [ausente]. Elo ausente: inventário atual dos handoffs pendentes.

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/local-readonly-receipt.json x16 (HEAD c3c4119804664546a1bb15ec7f5648d7eb8aa60c, branch de preservação e existência de tasks/_state.yaml); fontes/batch-revalidated-xldd-sources/local/CUSTODY-METADATA.json; fontes/batch-revalidated-xldd-sources/selected-register-matrix.json X16. Logs dos sete aceites e conteúdo integral dos handoffs não foram relidos.

### Classe e limite da evidência

FATO OBSERVADO: identidade atual do diretório Documents/Apex e metadata de custódia. RELATO HISTÓRICO: sete accepted=false e diagnóstico do caminho errado no registro. NÃO VERIFICADO: causalidade de cada falha, estado atual dos 11 specs e autorizações pertinentes. DECISÃO PENDENTE: necessidade de reemissão prospectiva.

### Fluxo

Fluxo: Task-Spec —(handoff com caminho e base)→ executor —(avaliação no repositório apontado)→ aceite. Problema histórico: caminho → clone do workspace → avaliação errada. Correção proposta: caminho → clone limpo da main na base certa.

### Consequências e risco

Sem ação, as análises de 21/09 continuam sem aceite formal; isso não afeta o produto, só a contabilidade de aceites. Confiança média: não sei quantos handoffs ainda importam.

### Alternativas e recomendação

Recomendado: inventariar quais dos 11 specs ainda têm valor depois das PRs de 06/10 e reemitir só esses em clones limpos. Alternativas: declarar a rodada histórica e não reemitir; reemitir todos (custo alto, muitos superados). Reversível.

### Dependências e paralelismo

Não depende do repositório APEX. Relaciona-se a X10 (custódia criada a partir desse commit) e a X17 (clones no iCloud); a decisão de reemitir é do usuário e não bloqueia nenhum item técnico.

### Plano e aceite propostos

Passos mínimos: (1) listar os 11 specs e marcar superados por PRs integradas; (2) para os restantes, autorização do usuário; (3) reemissão em clone limpo da main com base fixa. Aceite: lista com destino de cada spec.

### Comunicação entre responsáveis

Para outro pod: "Os aceites que falharam em 21/09 apontavam para o clone errado. O clone hoje está noutra branch; antes de reemitir, precisamos saber quais specs ainda importam."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere reemitir os 11 specs sem verificar se foram superados. Que caso o teste ainda não cobre? HEAD correto hoje não revalida a causa de cada EVAL_FAILED antigo. Como eu explicaria isso para outro pod? Explique aceite prospectivo e preservação do resultado histórico.

### Próxima ação e encerramento

Próxima ação: Augusto (a confirmar) decide se inventaria e reemite. Entrada: lista de specs em Documents/Apex/tasks. Saída: lista com destino por spec. Encerramento: decisão registrada.

<a id="item-253"></a>

## X17 — Clones locais parcialmente 'dataless' no iCloud

Frente: governanca_ambiente_local. Encaminhamento: externo_ambiente_local_contagem_atualizada.

### Identidade e estado

X17 é um risco operacional do ambiente local (Governança/Preservação), fora do repositório APEX: clones locais parcialmente "dataless" no iCloud. Decisão de política de armazenamento: usuário (Augusto, a confirmar).

### Intenção e benefício

Problema: arquivos evictados pelo iCloud fazem git status expirar e podem esconder trabalho não versionado; muitos clones têm origin encadeado para diretórios irmãos. Público: quem trabalha nesses clones. Ganho: evitar timeouts e perda de trabalho.

### Feito, faltante e não comprovado

Conferência independente de 18/10: find -flags +dataless -type f retornou 21.180 arquivos regulares em Documents/Apex, RC 0. O registro histórico citava 20.307, e o parecer anterior 21.189 sem o mesmo filtro; as contagens não são prova de crescimento ou política aplicada. Metadata declara custódia independente fora de Documents. Não foram inventariados todos os clones, mudanças locais ou estado de sincronização.

### Linhagem

Linhagem: varredura de setembro (20.307 arquivos, 116 diretórios .git) → custódia fora do iCloud (X10) → registro X17 (decision_required) → contagem de 18/10 (21.189) → política [ausente].

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/local-readonly-receipt.json x17 (comando, horário, RC e contagem 21.180 com -type f); fontes/batch-revalidated-xldd-sources/local/CUSTODY-METADATA.json (propósito e canonical automation root declarados); fontes/batch-revalidated-xldd-sources/selected-register-matrix.json X17 (20.307/116 como histórico).

### Classe e limite da evidência

FATO OBSERVADO: contagem atual de arquivos regulares com flag dataless e conteúdo da metadata. RELATO HISTÓRICO: 116 diretórios .git e timeout do git status. NÃO VERIFICADO: perda, corrupção, inventário de trabalho não commitado e mudança de política. Evicção não implica corrupção.

### Fluxo

Fluxo possível: clone em Documents —(arquivo evictado)→ acesso sob demanda —(materialização ou indisponibilidade/timeout)→ operação Git/leitura. Custódia independente é mitigação declarada na metadata; esta revisão não verifica o comportamento completo do iCloud.

### Consequências e risco

Sem política/inventário, clones ativos podem sofrer indisponibilidade ou operações lentas e uma limpeza mal informada pode atingir trabalho único. Dataless não demonstra perda nem corrupção. Confiança alta na contagem filtrada, impacto operacional atual não medido.

### Alternativas e recomendação

Recomendado: mover para fora do iCloud apenas os clones com trabalho não commitado ou ainda em uso, e marcar o restante como histórico. Alternativas: "Keep Downloaded" para a pasta inteira (simples, ocupa disco); não fazer nada (aceita timeouts). Reversível.

### Dependências e paralelismo

Não depende do repositório APEX nem de CI. Relaciona-se a X10 (custódia fora do iCloud), X11 (candidato Ask V2 em Documents/Apex) e X16 (handoffs que apontam para Documents/Apex); a política é decisão do usuário.

### Plano e aceite propostos

Passos mínimos: (1) listar diretórios com .git em Documents/Apex e marcar os com mudanças não commitadas (sem forçar download); (2) decisão de política; (3) mover ou fixar os escolhidos. Aceite: política escrita e lista aplicada.

### Comunicação entre responsáveis

Para outro pod: “Contamos 21.180 arquivos regulares dataless; isso mede disponibilidade local, não perda. A custódia declara raiz fora de Documents, mas ainda falta identificar clones ativos e trabalho único.”

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere limpar um clone antes de localizar trabalho único. Que caso o teste ainda não cobre? Uma contagem dataless não cobre sincronização, conteúdo ou recuperabilidade. Como eu explicaria isso para outro pod? Explique disponibilidade local e risco de armazenamento sem chamar evicção de corrupção.

### Próxima ação e encerramento

Próxima ação: Augusto (a confirmar) decide a política. Entrada: contagem desta ficha. Saída: política registrada e lista de clones tratados. Encerramento: política aplicada aos clones em uso.

<a id="item-254"></a>

## L01 — Linhagem v4 do workspace

Frente: historico_linhagem. Encaminhamento: encerrar_historico_catalogado_fonte_confirmada.

### Identidade e estado

L01 é o documento histórico “Linhagem v4 do workspace”, sem objeto público próprio. O stub docs/apex-v4-lineage.md tem 42 linhas na ref local origin/cowork do workspace; o documento completo tem 278 linhas no commit bd8a08bce77674ef1441a4647807817fe3f42b1c. Responsável por preservação: custodiante, a confirmar; sem implementação de produto pendente neste ID.

### Intenção e benefício

Intenção: preservar a linhagem das melhorias "Apex v4 corrigido" (data de 2026-06-08 no próprio stub), que explica de onde vieram componentes do projeto antes da v0.1. Público: quem audita a origem de decisões antigas. Ganho: contexto histórico recuperável sem confundi-lo com estado atual.

### Feito, faltante e não comprovado

Leitura de 18/10: o stub aponta a branch gustocezar/feature/desacoplamento-geradores; o documento completo em bd8a08b descreve o slice de junho e seus resultados históricos. A captura pública de branches de 18/10 e o mapa do bundle #105 registram o mesmo SHA. Isso verifica ponteiros e conteúdo; não certifica os resultados do slice nem seu estado atual no produto.

### Linhagem

Linhagem documental: slice v4 de junho → documento completo bd8a08b → stub que aponta a branch → arquivo/bundle #105 → registro L01. O recibo da restauração de 17/10 é fonte separada de custódia. Não foi reconstruída a cadeia de cada teste histórico relatado no documento.

### Fontes e corte

Fontes lidas: fontes/batch-revalidated-xldd-sources/local/L01-workspace-stub.md (42 linhas, SHA-256 ed5c804b…); fontes/batch-revalidated-xldd-sources/local/L01-lineage-bd8a08b.md (278 linhas, SHA-256 ba9794d6…); fontes/batch-revalidated-xldd-sources/L-additional-source-manifest.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018/branches-p1.json (branch bd8a08b); fontes/batch-custody-sources/BRANCH-TO-SHA.tsv; registro/triagem L01 em fontes/batch-revalidated-xldd-sources/selected-register-matrix.json.

### Classe e limite da evidência

FATO OBSERVADO: stub, documento completo, identidade do commit e ponteiros coincidentes na captura e no mapa. RELATO HISTÓRICO: resultados Ubuntu/WSL, ratio 27,9x/29,5x e demais conclusões dentro do documento de junho. Nenhuma reprodução nesta revisão.

### Fluxo

Fluxo documental observado: documento completo —(commit bd8a08b)→ ponteiro do stub; mapa do bundle —(mesmo SHA)→ cópia arquivada. A restauração é documentada em recibo separado. Se a branch for removida, o stub deve indicar uma fonte recuperável.

### Consequências e risco

Sem ação, nada muda. O risco é a exclusão futura da branch sem que alguém saiba que o stub do workspace depende dela; o bundle da #105, já restaurado em 17/10, mitiga essa perda. Confiança alta.

### Alternativas e recomendação

Recomendado: catalogar como histórico com o ponteiro duplo (branch e bundle). Alternativa: copiar o documento completo para o workspace (duplica conteúdo histórico; não necessário). Reversível.

### Dependências e paralelismo

Nenhuma dependência para catalogar. Uma eventual exclusão das branches (X12/#105) deve preservar este ponteiro ou atualizar o stub, mas essa é decisão separada do custodiante e do mantenedor.

### Plano e aceite propostos

Entrega mínima deste ID: conservar ID, data, commit e dois ponteiros verificáveis. Aceite documental: o leitor distingue stub de fonte completa e relato histórico de prova atual. Uma futura exclusão de branch exige decisão e inventário próprios; não é ação deste lote.

### Comunicação entre responsáveis

Para outro pod: "A linhagem v4 completa está no commit bd8a08b da branch desacoplamento-geradores e no bundle da #105; o arquivo do workspace é só um ponteiro."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Um stub apontando só uma branch excluída perderia o caminho de recuperação. Que caso o teste ainda não cobre? A conferência documental não reproduz o slice Ubuntu/WSL de junho. Como eu explicaria isso para outro pod? O stub é ponteiro; bd8a08b contém o relato completo e o bundle conserva esse commit.

### Próxima ação e encerramento

Próxima ação: custodiante, a confirmar, mantém L01 como histórico com commit bd8a08b e ponteiros de branch/bundle. Entrada: extratos e mapa lidos. Saída: catálogo datado. Encerramento documental: ponteiros e limites registrados; nenhuma execução do slice necessária para catalogar.

<a id="item-255"></a>

## L02 — Linhagem recursiva #66–#93

Frente: historico_linhagem. Encaminhamento: encerrar_historico_snapshot_preservado.

### Identidade e estado

L02 é a auditoria histórica “Linhagem recursiva #66–#93”, com data declarada de fotografia 22/08/2026. A cópia local de 13.647 bytes foi lida integralmente. No snapshot público de 16/10, #66 foi integrada em 18/08 (eaff2b3) e #93 fechada sem merge em 14/09. Responsável de custódia, a confirmar; sem ação de produto neste ID.

### Intenção e benefício

Intenção: registrar como as PRs de agosto se encadeavam (quem dependia de quem) num momento específico, para que revisões posteriores não inventem continuidade. Público: auditoria de histórico. Ganho: snapshot datado que permite comparar com estados posteriores.

### Feito, faltante e não comprovado

O texto foi lido: registra #81/#89/#91/#92/#93 abertas na fotografia de agosto e diferencia direto/declarado/derivado/inferência/pendente. O snapshot posterior mostra estados diferentes; LINEAGE-MAP.md acrescenta cortes posteriores. Catálogo histórico preservado; não se reconferiu cada review/teste que o relatório de agosto cita.

### Linhagem

Linhagem: objetos #66–#93 → relatório datado 22/08 → mudanças públicas posteriores → cortes novos em LINEAGE-MAP.md (L12) → catálogo L02. A relação de sucessão documental é explícita no cabeçalho do mapa; a causalidade de todas as contribuições não foi reauditada neste ID.

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/local/APEX-PR-RECURSIVE-LINEAGE-2026-08-22.md, integral, SHA-256 204f546e…; fontes/batch-revalidated-xldd-sources/L-primary-public.json pulls_all.json números 66 e 93 (merged_at/closed_at/merge_commit_sha); fontes/batch-revalidated-xldd-sources/local/LINEAGE-MAP.md, cabeçalho e deltas; fontes/batch-revalidated-xldd-sources/selected-register-matrix.json L02.

### Classe e limite da evidência

FATO OBSERVADO: conteúdo do relatório e metadados públicos posteriores de #66/#93. RELATO HISTÓRICO: testes, runtime e reviews descritos no relatório de agosto; não foram reconfirmados endpoint a endpoint. A leitura integral fortalece o catálogo, não transforma o relato inteiro em prova primária de execução.

### Fluxo

Fluxo de leitura: snapshot de 22/08 —(estado das PRs naquele dia)→ leitor —(comparação)→ LINEAGE-MAP.md atualizado —(estado posterior)→ visão datada. O snapshot não deve ser lido como estado atual.

### Consequências e risco

Sem ação, nada muda. O risco é alguém citar o snapshot de 22/08 como estado de hoje, por exemplo tratando a #93 como aberta; a classificação histórica com sucessor L12 evita isso. Confiança alta.

### Alternativas e recomendação

Recomendado: catalogar como histórico e apontar para L12 como sucessor de atualização. Alternativa: atualizar o próprio snapshot (apagaria a foto de 22/08; não recomendado). Reversível.

### Dependências e paralelismo

Nenhuma dependência para catalogar. L12 é a continuação datada da genealogia e é independente deste catálogo; atualizar L12 não exige tocar o snapshot de 22/08.

### Plano e aceite propostos

Sem entrega de produto neste ID. Conservar fotografia, hash, data e ligação para L12. Controle documental: ao citar uma PR aberta no relatório de agosto, informar a data e consultar seu estado no recorte de interesse. Aceite: fotografia preservada e limites legíveis.

### Comunicação entre responsáveis

Para outro pod: "O mapa de linhagem de 22/08 é uma foto daquele dia; para o estado depois dos merges de 14/09 use a genealogia de L12, que tem apêndices datados."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Reescrever o snapshot apagaria que #93 ainda era tratada como aberta naquele corte. Que caso o teste ainda não cobre? Esta leitura não reconfirma cada suíte ou review histórico citado. Como eu explicaria isso para outro pod? L02 é a foto de agosto e L12 reúne deltas posteriores datados.

### Próxima ação e encerramento

Próxima ação: custodiante, a confirmar, conserva L02 com hash/data e ponteiro para L12. Entrada: relatório integral e estados públicos datados. Saída: catálogo histórico. Encerramento documental: fontes e sucessão identificadas.

<a id="item-256"></a>

## L04 — Reconciliação documental da linhagem

Frente: historico_metodo. Encaminhamento: encerrar_historico_politica_preservada.

### Identidade e estado

L04 é uma Task-Spec histórica de método: reconciliação documental da linhagem (DOCS-LINEAGE-RECONCILIATION-20260823.md, 4.632 bytes, em [caminho local omitido] Sem objeto público APEX. Resultado registrado: regras de fato/hipótese/decisão adotadas em PRESERVATION-POLICY.md (4.326 bytes na custódia). Owner: nenhum necessário.

### Intenção e benefício

Intenção: fixar como documentos de linhagem devem separar fato observado, hipótese e decisão, para que relatos não virem prova por repetição. Público: quem escreve ou audita registros. Ganho: regras de redação que as auditorias seguintes (inclusive esta) usam.

### Feito, faltante e não comprovado

Task-Spec e política foram lidas integralmente. A política declara expressamente incorporar as regras da Task-Spec e separa direct_*, remote_ci, reported, derived, historical e unproven; também diz que hash não prova autorização/autoria/validade atual. Isso verifica adoção textual, sem certificar conformidade de todos os documentos posteriores.

### Linhagem

Linhagem documental explícita: Task-Spec DOCS-LINEAGE-RECONCILIATION-20260823 → PRESERVATION-POLICY.md, cujo primeiro parágrafo declara a incorporação → registro L04. A data 23/09 da reconciliação e custódia posterior contextualizam o pacote; não se inferiu uma data externa de criação a partir de hash/mtime.

### Fontes e corte

Fontes integrais: fontes/batch-revalidated-xldd-sources/local/DOCS-LINEAGE-RECONCILIATION-20260823.md (SHA-256 5c079eb4…, limites, tabela e critérios); fontes/batch-revalidated-xldd-sources/local/PRESERVATION-POLICY.md (SHA-256 59c4658e…, introdução e §§3–6); origem/hashes em fontes/batch-revalidated-xldd-sources/local-source-manifest.json; registro/triagem L04 em fontes/batch-revalidated-xldd-sources/selected-register-matrix.json.

### Classe e limite da evidência

FATO OBSERVADO: regras da Task-Spec, declaração de incorporação e regras concretas da política. RELATO HISTÓRICO: fatos locais/de execução descritos dentro da Task-Spec. NÃO VERIFICADO: aplicação universal da política por outros artefatos. Nenhuma instrução dos documentos foi executada como comando.

### Fluxo

Fluxo de método: Task-Spec de reconciliação —(regras)→ PRESERVATION-POLICY —(aplicadas por)→ registros, triagens e revisões —(separação fato/relato/inferência)→ leitores. Esta revisão é um consumidor desse fluxo.

### Consequências e risco

Sem ação, a política continua disponível. O risco é ela não ser conhecida por novos colaboradores; não há impacto de produto. Confiança alta.

### Alternativas e recomendação

Recomendado: catalogar como histórico e citar a política como referência de método nas próximas consolidações. Alternativa: publicar a política no repositório (decisão do mantenedor; não exigida). Reversível.

### Dependências e paralelismo

Nenhuma dependência para catalogar. Relaciona-se a X09 (registro canônico), que aplica a política, e às revisões em curso, que a seguem; nenhum deles depende deste ID.

### Plano e aceite propostos

Condição de não ação: nenhum passo neste ID. Reabrir só se a política for perdida, contradita por uma decisão nova do usuário ou substituída por outra versão sem registro.

### Comunicação entre responsáveis

Para outro pod: "Há uma política de preservação que manda separar fato, hipótese e decisão nos registros; ela vem de uma Task-Spec de 23/08 e está guardada na custódia."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Repetir um relato como fato apagaria a fronteira entre observação e hipótese. Que caso o teste ainda não cobre? Ler a política não audita a conformidade de todos os documentos posteriores. Como eu explicaria isso para outro pod? A política incorpora o método da Task-Spec e exige fontes e limites por afirmação.

### Próxima ação e encerramento

Próxima ação: catalogar L04 como histórico. Owner: nenhum necessário. Entrada: os dois arquivos. Saída: linha L04 "Task-Spec de 23/08; política na custódia". Encerramento: imediato.

<a id="item-257"></a>

## L05 — Inventário de proveniência de campos (A1)

Frente: historico_proveniencia. Encaminhamento: encerrar_historico_residuo_em_l14.

### Identidade e estado

L05 é um estudo histórico: inventário de proveniência de campos A1, de 2026-08-06 (baseline f35c776), em [caminho local omitido] (7.716 bytes). Sem objeto público. Owner: nenhum necessário.

### Intenção e benefício

Intenção: mapear de onde vem cada campo de telemetria e quais lacunas impediam comparações honestas entre runs. Público: Pods que consomem telemetria. Ganho: baseline histórico para medir o que foi fechado depois.

### Feito, faltante e não comprovado

A1 foi lido integralmente: aceito para Define, sem mudança de contrato/produto, baseline f35c7761166377d27957ccbf363c54f94e3adeb1. CONTRACT.md na base c3c3ea3 declara job_conf em v0.4 e execution_id opcional em v0.6. Isso demonstra evolução declarada do contrato; não encerra por si a configuração real, atribuição stage-level ou comparabilidade entre ambientes. O próprio v0.6 preserva a necessidade de incremento cross-lane para usar a correlação. Resíduos de proveniência seguem L14/#180.

### Linhagem

Linhagem documental: A1 de 06/08 → incrementos declarados v0.4/v0.6 no contrato → registro L05 → hipóteses remanescentes em L14 → agrupamento na #180. Não se provou causalidade exclusiva de A1 sobre os incrementos nem fechamento runtime das lacunas.

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/local/A1-FIELD-PROVENANCE-INVENTORY-2026-08-06.md, integral, SHA-256 34eea257… (matriz e Decision and feedback); fontes/batch-revalidated-xldd-sources/code/CONTRACT.md:11–21 e 30–31 (v0.6/v0.4 e limites); fontes/batch-revalidated-xldd-sources/primary-public-selected.json issue 180; fontes/batch-revalidated-xldd-sources/selected-register-matrix.json L05/L14.

### Classe e limite da evidência

FATO OBSERVADO: conteúdo histórico de A1, declarações v0.4/v0.6 e agrupamento em #180. RELATO HISTÓRICO: caminhos/provas descritos por A1 sobre sua baseline. INFERÊNCIA LIMITADA: parte das lacunas evoluiu no contrato; nenhuma prova nova de emissão, ingestão ou atribuição ponta a ponta foi produzida.

### Fluxo

Fluxo documental: A1 —(lacunas e limites históricos)→ comparação com contrato c3c3ea3 —(declarações adicionadas e resíduos a confirmar)→ L14/#180. job_conf e execution_id declarados não equivalem a uma execução real com configuração/correlação disponíveis.

### Consequências e risco

Sem ação, nada muda. O risco é usar a lista de lacunas de agosto como lista atual; o ponteiro para L14 e #180 evita isso. Confiança alta no catálogo, média na lista restante (ver L14).

### Alternativas e recomendação

Recomendado: catalogar como histórico com ponteiro para L14. Alternativa: atualizar o A1 (apagaria o baseline; não recomendado). Reversível.

### Dependências e paralelismo

Nenhuma dependência para catalogar. L14 e a #180 seguem com o resíduo de proveniência e não precisam reabrir o inventário A1 de 06/08; o baseline continua disponível como referência de comparação.

### Plano e aceite propostos

Conservar A1 com baseline e data, e apontar para L14/#180. Quando reutilizar uma lacuna, verificar separadamente contrato, produtor, transporte e consumidor na ref escolhida. Aceite deste catálogo: não chamar o changelog de prova de fechamento runtime.

### Comunicação entre responsáveis

Para outro pod: “A1 é o inventário de agosto. O contrato posterior acrescentou job_conf e execution_id opcional, mas isso não certifica emissão nem atribuição stage-level; o resíduo precisa ser confirmado na #180.”

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Tratar execution_id opcional como atribuição stage-level completa prometeria uma ligação não certificada. Que caso o teste ainda não cobre? Esta revisão não prova emissão, ingestão e consumo reais de job_conf/correlação. Como eu explicaria isso para outro pod? O contrato evoluiu; o baseline histórico e os limites runtime continuam distintos.

### Próxima ação e encerramento

Próxima ação: catalogar L05 como histórico. Owner: nenhum necessário. Entrada: A1 e CONTRACT.md. Saída: linha L05 "baseline 06/08; resíduo em L14/#180". Encerramento: imediato.

<a id="item-258"></a>

## L06 — Auditoria de linhagem por chaves (A39)

Frente: historico_proveniencia. Encaminhamento: encerrar_historico_documentado_na_main.

### Identidade e estado

L06 é a auditoria histórica de linhagem por chaves A39, cuja fonte original ainda não foi localizada no recorte pesquisado. O processo correlato está documentado em docs/e2e/PRE_SUBMIT_PROVENANCE.md, PR #85 integrada em 2026-08-20T02:39:50Z (19/08 BRT), merge 0da32ce. Responsável de custódia, a confirmar; sem ação de produto neste ID.

### Intenção e benefício

Intenção: garantir que uma Task-Spec registre sua proveniência antes da submissão, para que aceites possam ser rastreados por chave. Público: quem prepara e aceita Task-Specs. Ganho: processo documentado na main.

### Feito, faltante e não comprovado

Documento integral lido na base c3c3ea3: convenção aditiva e opt-in; Task-Spec → hash → manifesto → hash → recibo, sem hash autorreferente; separa harness_execution_id de IDs Spark e temporalidade local de âncora externa. Isso confirma cobertura documental do processo, sem provar conformidade de todas as specs ou recuperar o resultado A39.

### Linhagem

Linhagem: A39/proven_gap [origem relatada pelo registro; original não localizado] → processo na #85 → merge 0da32ce (20/08 UTC, 19/08 BRT) → documento presente na base → registro L06. A ligação A39→#85 permanece declarada no acervo; não foi inventado recibo de execução de A39.

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/code/docs__e2e__PRE_SUBMIT_PROVENANCE.md, integral (opt-in, custody chain, identity boundaries e temporal assurance); fontes/batch-revalidated-xldd-sources/L-primary-public.json PR 85, merged_at 2026-08-20T02:39:50Z, merge 0da32ce42abcba37a13ad7e257749063ff567033; fontes/batch-revalidated-xldd-sources/local/main-first-parent-c3c3ea3.txt; fontes/batch-revalidated-xldd-sources/selected-register-matrix.json L06. Fonte A39 original não localizada.

### Classe e limite da evidência

FATO OBSERVADO: documento integral e merge da #85. RELATO HISTÓRICO: origem no proven_gap A39. NÃO VERIFICADO: arquivo/recibo A39 e conformidade de cada execução posterior. A convenção não invalida retroativamente recibos históricos.

### Fluxo

Fluxo documental proposto pelo guia: Task-Spec —(SHA-256 dos bytes)→ manifesto de autorização —(SHA-256 do manifesto)→ recibo posterior. harness_execution_id identifica a tentativa governada; app_id/job_id/stage_id só entram se o runtime os produzir. A existência do guia não prova uma tentativa concreta.

### Consequências e risco

Sem ação, nada muda: o processo está documentado na main. O risco residual é o documento envelhecer frente ao tooling atual de Task-Spec, o que a sessão de Task-Specs avalia. Confiança alta.

### Alternativas e recomendação

Recomendado: catalogar como histórico coberto pelo documento da main. Alternativa: auditar conformidade das specs posteriores (trabalho da sessão de Task-Specs, não deste lote). Reversível.

### Dependências e paralelismo

Nenhuma dependência de produto para catalogar. Auditoria de conformidade de Task-Specs é trabalho separado; esta ficha não presume quantidade ou conclusão daquela auditoria.

### Plano e aceite propostos

Condição de não ação: nenhum passo neste ID. Reabrir só se o documento for removido da main ou se o processo de pré-submissão for substituído sem registro.

### Comunicação entre responsáveis

Para outro pod: "O processo de proveniência pré-submissão de Task-Specs está documentado em docs/e2e/PRE_SUBMIT_PROVENANCE.md desde a #85; consulte-o antes de submeter uma spec."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Usar o ID do harness como job_id misturaria autorização e identidade Spark. Que caso o teste ainda não cobre? O guia presente não comprova que todas as execuções seguiram a cadeia nem recupera A39. Como eu explicaria isso para outro pod? O processo é opt-in e preserva recibos antigos com seus limites de tempo e identidade.

### Próxima ação e encerramento

Próxima ação: catalogar L06 como histórico. Owner: nenhum necessário. Entrada: documento na base. Saída: linha L06 "coberto por PRE_SUBMIT_PROVENANCE.md (#85)". Encerramento: imediato.

<a id="item-259"></a>

## L07 — Linhagem Ask HTTP contra upstream (R0)

Frente: historico_ask_http. Encaminhamento: encerrar_historico_prompt_sem_resultado.

### Identidade e estado

L07 é uma auditoria específica de linhagem: Ask HTTP contra upstream (R0). Arquivo: [caminho local omitido] (5.849 bytes). Sem objeto público. Owner: nenhum necessário.

### Intenção e benefício

Intenção: responder, em setembro, se o candidato local Ask HTTP ainda fazia sentido diante da main de Luan, das PRs e issues. Público: quem decidiria o Ask. Ganho: base para a decisão da #122.

### Feito, faltante e não comprovado

Arquivo integral lido: é o pedido de auditoria R0, com missão, candidatos/baseline, método e formato de resposta; não contém o resultado dessa auditoria. A pasta de origem tem apenas esse arquivo no recorte local observado. Não foi buscada exaustivamente outra cópia/resultados em todo o acervo. Inventário Ask V2 e X11 são fontes posteriores; nova leitura documental sobre a /v1 pode instruir DEC-07 antes da decisão.

### Linhagem

Linhagem: candidato Ask HTTP (setembro) → prompt R0 de 17/09 → resultado R0 [ausente] → inventário Ask V2 de 21/09 → preservação X11 → decisão #122 (X01) [ausente]. O resultado R0, se existiu, não está ao lado do prompt.

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/local/CLAUDE-R0-UPSTREAM-LINEAGE.md, integral, SHA-256 b3136b35… (Missão, Identidades e fontes, Método obrigatório e Formato); fontes/batch-revalidated-xldd-sources/local-source-manifest.json; fontes/batch-revalidated-xldd-sources/local-readonly-receipt.json x11 (inventário/candidato preservados); fontes/batch-revalidated-xldd-sources/primary-public-selected.json #122 e #129; fontes/batch-revalidated-xldd-sources/selected-register-matrix.json L07.

### Classe e limite da evidência

FATO OBSERVADO: o arquivo é um prompt de auditoria e está sozinho na pasta de 17/09. INFERÊNCIA: não há resultado R0 recuperável neste local. Nenhuma execução aplicável.

### Fluxo

Fluxo histórico: prompt R0 —(auditoria solicitada)→ resultado não localizado ao lado; inventário Ask V2/X11 e API #129 —(fontes posteriores)→ nova comparação documental possível —(informa)→ decisão #122. Nenhuma conclusão R0 foi inferida do prompt.

### Consequências e risco

Sem ação, nada muda. O risco é alguém tratar o prompt como resultado de auditoria e citar uma conclusão que nunca foi escrita; a classificação histórica evita isso. Confiança alta.

### Alternativas e recomendação

Recomendado: preservar o prompt como histórico e usar fontes posteriores para informar #122. Se uma nova auditoria for útil, delimitar a pergunta sobre a /v1 atual antes ou em paralelo à DEC-07. Alternativa: somente catalogar o prompt; aceitável se não for preciso aprofundar a decisão. A decisão continua necessária antes da implementação escolhida.

### Dependências e paralelismo

Catalogação e leitura documental não dependem de DEC-07. Implementação/publicação dependem da decisão e autorização adequadas. A comparação nova deve partir da ref atual realmente identificada e do candidato preservado; não reexecutar comandos só porque constam no prompt.

### Plano e aceite propostos

Condição de não ação: nenhum passo neste ID. Reabrir só se surgir um resultado R0 que contradiga o inventário Ask V2 ou a preservação de X11.

### Comunicação entre responsáveis

Para outro pod: "O arquivo R0 do Ask HTTP é o pedido de uma auditoria, não o resultado. Para decidir o Ask, use o inventário Ask V2 e a #122."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Citar a missão do prompt como veredito inventaria uma auditoria concluída. Que caso o teste ainda não cobre? Não foi localizado resultado R0 fora da pasta consultada nem validada a candidata contra a API atual. Como eu explicaria isso para outro pod? O prompt é histórico; uma comparação documental atual pode ajudar a decidir a #122.

### Próxima ação e encerramento

Próxima ação: catalogar L07 como histórico. Owner: nenhum necessário. Entrada: arquivo indexado. Saída: linha L07 "prompt sem resultado; insumo atual = inventário Ask V2". Encerramento: imediato.

<a id="item-260"></a>

## L08 — Matriz de compatibilidade de telemetria

Frente: arquitetura_matriz_telemetria. Encaminhamento: encerrar_entregue_atualizacao_em_180.

### Identidade e estado

L08 é o estudo/validador da matriz de compatibilidade de telemetria (cross-lane/contrato), entregue pela PR luanmorenommaciel/apex#111 "docs: add executable telemetry compatibility matrix" (head 4f833c7, merge 31a0cee em 2026-09-14), que fecha a issue #103, e atualizado pela #121 "fix(tests): bump telemetry matrix to contract v0.6" (head efb6773, merge 16e3819 em 14/09). Sem owner pendente.

### Intenção e benefício

Intenção: uma matriz executável de produtores, transportes e consumidores, com teste estático que falha quando o código diverge do declarado. Público: todos os Pods. Ganho: drift de telemetria detectado por teste.

### Feito, faltante e não comprovado

Base: docs/architecture/TELEMETRY-COMPATIBILITY-MATRIX.md e tests/test_telemetry_compatibility_matrix.py existem; o cabeçalho declara "Base observada: 847d7a0" e a seção da linha 180-184 diz "Front-End: absent/external", embora front/ exista desde a #100. Feito: entrega e atualização para v0.6. Falta, fora deste ID: atualizar a cobertura para Front e API (L13/#180).

### Linhagem

Linhagem: issue #103 → PR #111 (merge 31a0cee) → PR #121 v0.6 (merge 16e3819) → main → base antiga desatualizada pela #100 e #129 → atualização em L13/#180. Sem elo ausente para o encerramento.

### Fontes e corte

Fontes integrais: fontes/batch-revalidated-xldd-sources/code/docs__architecture__TELEMETRY-COMPATIBILITY-MATRIX.md (base 847d7a0, manifesto v0.6, seção Front ausente); fontes/batch-revalidated-xldd-sources/code/tests__test_telemetry_compatibility_matrix.py (_validate, manifesto, limites da busca Verify e literais PROPOSED/NOT a column); fontes/batch-revalidated-xldd-sources/L-primary-public.json PRs 111 e 121 e issue 103; fontes/batch-revalidated-xldd-sources/selected-register-matrix.json L08; fontes/batch-revalidated-xldd-sources/primary-public-selected.json #180.

### Classe e limite da evidência

FATO OBSERVADO: matriz/teste presentes e lidos; metadados de merge #111/#121; base histórica e omissão de Front/API no manifesto. RELATO: passes históricos nos corpos das PRs, não reexecutados. A busca de writer do teste se limita à lane Verify e não prova inexistência de dados/escritores externos.

### Fluxo

Fluxo estático observado no código do teste: fontes independentes de contrato/lanes —(asserções e manifesto)→ comparação estrutural; mutações adversariais —(devem provocar AssertionError)→ controle negativo. A implementação foi lida, sem executar o teste. O manifesto não cobre Front/API e não demonstra interoperabilidade runtime.

### Consequências e risco

A matriz continua útil no escopo estático que declara; tratá-la como mapa completo atual esconderia Front/API. Nenhum estado verde de execução foi observado por esta leitura. Risco documental, confiança alta na omissão do manifesto.

### Alternativas e recomendação

Recomendado: encerrar L08 e manter a atualização em L13/#180. Alternativa: atualizar aqui, o que duplicaria a #180 e misturaria entrega histórica com trabalho novo. Reversível.

### Dependências e paralelismo

Nenhuma dependência para encerrar. Mudanças de texto de #165 e #179 precisam coordenar as asserções literais do teste, independentemente de #180 (C04-16).

### Plano e aceite propostos

Condição de não ação neste ID. Reabrir somente se o teste da matriz for removido, deixar de rodar no CI ou passar a falhar sem que nenhum objeto público rastreie a falha.

### Comunicação entre responsáveis

Para outro pod: "A matriz de telemetria existe e tem teste desde a #111, mas reflete a base de agosto; a atualização para Front e API está na #180, sem apagar a versão histórica."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Tomar o manifesto de agosto como topologia completa omitiria Front e API. Que caso o teste ainda não cobre? Ele não exerce ingestão real, interoperabilidade runtime ou toda escrita externa à lane Verify. Como eu explicaria isso para outro pod? A matriz foi entregue; sua atualização está na #180 e a prova continua estática.

### Próxima ação e encerramento

Próxima ação: confirmar encerramento de L08 com ponteiro para #180. Owner: nenhum necessário. Entrada: matriz e teste na base. Saída: linha L08 "entregue em 31a0cee/16e3819; atualização em #180". Encerramento: imediato.

