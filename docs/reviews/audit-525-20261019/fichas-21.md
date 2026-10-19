# Fichas documentais — lote 21

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-201"></a>

## F16 — Atualizar KnownFindingType (RETRY_PRESSURE já na main; TAIL_OUTLIER após #127)

Frente: consumidores_tail_outlier. Encaminhamento: dividir_retry_pressure_encerrado_tail_outlier_em_166.

### Identidade e estado

F16 é um PR pequeno do Pod 1/Front com duas partes. A parte RETRY_PRESSURE foi implementada pela PR luanmorenommaciel/apex#137 "fix(front): recognize retry pressure findings" (head 2c3ae4b), integrada em 2026-10-06T20:11:58Z no merge 9acfcb2. A parte TAIL_OUTLIER está na minuta P-TAIL (ids F13, F16, F18, S17), publicada como #166, cujo rodapé público lista só F13, F18 e S17. Sem assignee próprio.

### Intenção e benefício

Problema: types.ts dizia refletir o enum FindingType do Engine, mas não continha RETRY_PRESSURE, que o Engine já produzia (schema.py:49 no registro); TAIL_OUTLIER viria depois da #127. Público: quem lê findings na Console e quem mantém o espelho de tipos. Ganho: rótulos corretos e comentário honesto, mantendo a união aberta.

### Feito, faltante e não comprovado

Feito e visível: RETRY_PRESSURE em front/src/contract/types.ts:73. Falta: TAIL_OUTLIER, que é exatamente o escopo de F13 na #166 (não duplicar). Não comprovado: CI hospedada do head 2c3ae4b e a observação da TS14 de que o teste de consumidor de RETRY_PRESSURE era cobertura parcial, não defeito.

### Linhagem

Linhagem: revisão P11 da #127 → commit 2c3ae4b na branch codex/front-retry-pressure-type → PR #137 (27/09) → testes locais (relato) → check-runs sem steps → merge 9acfcb2 em 06/10 (parte RETRY_PRESSURE). Parte TAIL_OUTLIER: minuta P-TAIL com F16 → #166 sem F16 no rodapé [elo de rastreabilidade ausente no objeto público]. A MATRIX liga F16 a P-TAIL (proposal_key), então a origem não se perde no ledger local.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/front__src__contract__types.ts.txt. Locadores e recorte: F16; #137; P-TAIL ids versus source_ids e rodapé #166; types.ts:57–82. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: RETRY_PRESSURE presente, TAIL_OUTLIER ausente; divergência de ids entre minuta e publicação. RELATO: typecheck, lint e 87 testes do Front do autor. INFERÊNCIA: a omissão de F16 no rodapé é de rastreabilidade, não de escopo, porque F13 já descreve a inclusão do tipo no Front. Nenhum teste ou CI observado nesta revisão.

### Fluxo

Fluxo estático parcial: enum do Engine → findings.type String → união aberta FindingType no Front. RETRY_PRESSURE está na lista conhecida; TAIL_OUTLIER não. O rótulo efetivo depende do consumidor e deve ser caracterizado em F13/#166, sem inferi-lo apenas dessa união.

### Consequências e risco

Sem ação adicional, RETRY_PRESSURE já está correto; TAIL_OUTLIER fica como em F13. O risco de rastreabilidade é alguém procurar F16 na #166 e concluir que ficou sem destino. Confiança alta.

### Alternativas e recomendação

Recomendado: dividir F16: encerrar a parte RETRY_PRESSURE por #137 e tratar a parte TAIL_OUTLIER como coberta por F13 na #166, sem item novo. Alternativa: pedir ao mantenedor para acrescentar F16 ao rodapé da #166 (corrige rastreabilidade pública; exige publicação autorizada). Alternativa rejeitada: novo PR só para TAIL_OUTLIER fora da #166, que duplicaria F13.

### Dependências e paralelismo

Parte RETRY_PRESSURE: sem dependências. Parte TAIL_OUTLIER: depende da mesma decisão de apresentação de F13 e corre junto com ela. Nada aqui depende de #168.

### Plano e aceite propostos

Passo mínimo: registrar na visão consolidada "F16 = RETRY_PRESSURE entregue em 9acfcb2 + TAIL_OUTLIER coberto por F13/#166". Opcional, com autorização: comentário na #166 acrescentando F16 ao rastreamento. Nenhuma mudança de produto a partir deste ID.

### Comunicação entre responsáveis

Para outro pod: "RETRY_PRESSURE já é reconhecido pelo Front (#137). TAIL_OUTLIER entra pela #166 junto com F13; F16 só não aparece no rodapé público da issue."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Fechar a união do Front poderia rejeitar novos tipos aditivos; duplicar a inclusão de TAIL_OUTLIER fora da #166 repetiria F13. Que caso o teste ainda não cobre? O consumidor visual não foi executado nem totalmente relido; a inclusão em uma união não demonstra o rótulo final. Como eu explicaria isso para outro pod? RETRY_PRESSURE está integrado pela #137; TAIL_OUTLIER segue com F13/#166, e F16 permanece rastreável nos source_ids locais.

### Próxima ação e encerramento

Próxima ação: Codex registra a divisão de F16 na consolidação; mantenedor decide se quer F16 no rodapé da #166. Owner: Pod 1 (a confirmar). Entrada: #137 e #166. Saída: linha F16 dividida com destinos. Encerramento: parte TAIL_OUTLIER encerra junto com F13.

<a id="item-202"></a>

## F18 — Texto do mechanism_check do Verify para tipos não-skew

Frente: consumidores_tail_outlier. Encaminhamento: agrupar_em_166_parte_verify.

### Identidade e estado

F18 é o recorte Verify do follow-up de TAIL_OUTLIER (Pod 1/Verify, origem revisão B-4 da #127), agrupado na issue luanmorenommaciel/apex#166 via minuta P-TAIL. Issue aberta, assignee gustocezar como reserva de estudo de 11/10. Owner da mudança de texto no Verify: a confirmar.

### Intenção e benefício

Problema: o veto de volume do mechanism_check usa uma mensagem que fala em "not data skew" e é aplicada a qualquer tipo de finding, então um TAIL_OUTLIER recebe justificativa de skew que o watcher não alega. Público: quem lê a justificativa de verificação. Ganho: mensagem coerente com o tipo, ou "não aplicável" quando o Verify não tem mecanismo para ele.

### Feito, faltante e não comprovado

Na base: mechanism_check em verify/src/apex_verify/guardrails.py:168 começa com o teste de volume; o texto (linhas 181-187) diz que a dispersão de duração é aquecimento de JVM e jitter "not data skew", independentemente de finding_type; o teste de Join só roda para SKEW_ON_JOIN (linha 189). Falta: texto por tipo e teste da mensagem. Não comprovado: o efeito de delta 0 para TAIL_OUTLIER com predictor MECHANISM_CHECK, só relatado.

### Linhagem

Linhagem: revisão B-4 da #127 (inspeção de 21/09, linhas 179-187 citadas) → registro F18 (study_ready, depende do merge #127) → merge #127 → minuta P-TAIL → #166 (critério: documentar se um consumidor só preserva o finding) → estudo C2 no comentário → decisão de texto [ausente] → teste [ausente].

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/verify__src__apex_verify__guardrails.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/verify__src__apex_verify__predict.py.txt. Locadores e recorte: F18; #166 comentário integral; guardrails.py:168–210; predict.py ramo MECHANISM_CHECK. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: texto do veto de volume independe de finding_type; só o ramo Join é condicionado a SKEW_ON_JOIN. RELATO: tendência a delta zero no recorte MECHANISM_CHECK. PROPOSTA: mensagem por tipo ou discussão separada de não aplicabilidade. Testes existentes não foram inventariados integralmente; nenhuma ausência universal de teste é afirmada.

### Fluxo

Fluxo observado no código: finding (tipo) + StageObservation —(bytes por task)→ mechanism_check —(veto de volume com texto de skew)→ Guardrail com reasons —(justificativa)→ veredito exibido. Fluxo proposto: tipo —(seleciona texto ou não aplicável)→ reasons.

### Consequências e risco

Sem ação, a justificativa contradiz o watcher para cauda: o usuário lê "não é data skew" quando ninguém alegou skew, o que confunde mas não muda a certificação. Confiança alta no fato estático; impacto de interpretação, sem incidente.

### Alternativas e recomendação

Recomendado: decidir texto por tipo e, se a folha for somente textual, ajustar apenas a justificativa, mantendo regras e predictor. Alternativa: texto genérico neutro. Declarar mecanismo não aplicável, recusar ou mudar caps_delta_at_zero são mudanças semânticas e exigem recorte/decisão próprios na #166; não devem entrar silenciosamente na folha de mensagem.

### Dependências e paralelismo

Depende da decisão de apresentação comum da #166, mas toca só o Verify e pode correr em paralelo com F13 (Front) e S17 (Serve). Não depende de #168 nem de #117.

### Plano e aceite propostos

Menor folha textual após decisão: ajustar detail por tipo; verificar TAIL_OUTLIER e controles SKEW_ON_JOIN/RETRY_PRESSURE sem mudar fired/verdict/caps_delta_at_zero/score. Critério discriminante: a justificativa escolhida não atribui causa de skew a cauda apenas por duração. Se a decisão for não aplicável, abrir folha semântica própria com critérios antes de implementar.

### Comunicação entre responsáveis

Para outro pod: "O Verify vai deixar de dizer 'não é data skew' para um finding que nunca alegou skew; a regra de volume e o cálculo não mudam, só a explicação."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Mudar o predictor junto com a mensagem alteraria semântica e deixaria de ser uma correção textual pequena. Que caso o teste ainda não cobre? A mensagem por tipo ainda precisa de controle discriminante que preserve fired, verdict, caps_delta_at_zero e score nos tipos de controle. Como eu explicaria isso para outro pod? O veto físico tem uma explicação de skew aplicada genericamente; a primeira folha corrige a explicação, e não aplicabilidade exige decisão própria.

### Próxima ação e encerramento

Próxima ação: dono do Verify (a confirmar) registra na #166 o texto escolhido. Entrada: guardrails.py e matriz C2. Saída: PR com teste de mensagem por tipo. Encerramento: teste integrado e critério da #166 correspondente marcado.

<a id="item-203"></a>

## F19 — Proveniência de versão e docs do Verify

Frente: verify_documentacao_versao. Encaminhamento: executar_revisao_162_e_decidir_docs_lane_verify.

### Identidade e estado

F19 é um item novo do registro (documentação/decisão, Pod 1/Verify) sobre proveniência de versão e documentação do Verify. Objetos relacionados: PR luanmorenommaciel/apex#162 "fix(verify): align module version with package 0.1.0" (head 3955f9d, aberta, três checks verdes do CI atual nos recibos de checks de 16/10) e PR #164 "docs: align Serve and Verify docs with current contract" (head 5d42763, aberta, sem checks). Ambas de gustocezar, sem reviews no snapshot. Owner da decisão de versão: mantenedor + Pod 1 (a confirmar).

### Intenção e benefício

Problema: o pacote declara 0.1.0 (verify/pyproject.toml:3) e o default Verdict.verify_version é "0.1.0" (models.py:335), mas __version__ é "0.3.0" (__init__.py:72); além disso o brief docs/lanes/VERIFY.md descreve tabelas lidas e uma contagem de testes que não conferem com o código. Público: quem lê linhas de fix_verifications e quem usa a documentação da lane. Ganho: identidade de versão coerente e documentação honesta sobre o que o Verify lê.

### Feito, faltante e não comprovado

Base: pacote e default Verdict.verify_version são 0.1.0, mas __version__ é 0.3.0. O diff #162 só alinha o módulo e adiciona dois testes; to_row já serializa o valor da instância. #164 altera três READMEs, sem docs/lanes/VERIFY.md. Esse brief ainda lista spark_events/findings como leitura e 105 testes; busca lexical restrita a verify/src e verify/scripts encontrou SQL sobre job_conf e plan_transitions, sem provar ausência de leitura indireta. A contagem 105 não foi recontada e não é prova de regressão.

### Linhagem

Linhagem: verify-pipeline-map §5 q3 e §6 → registro F19 (study_ready, depende de H05) → PR #162 (versão) e PR #164 (READMEs) abertas por gustocezar → checks: #162 três verdes, #164 nenhum → reviews [ausentes] → decisão de política de versão (DEC-N2) [ausente] → correção de docs/lanes/VERIFY.md [sem objeto]. O DECISION-REGISTER inclui F19 em DEC-06 (ownership de Verify e Memory e escritor externo), o que é correto como pergunta ao dono; mas as alternativas citadas pela v2 para F19 (adaptar caminho externo, sink no Verify, contrato sem escritor) são as do escritor de fix_verifications e não respondem à pergunta de versão.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/verify__src__apex_verify__models.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/verify__src__apex_verify____init__.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/verify__pyproject.toml.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/docs__lanes__VERIFY.md.txt; fontes/pr162-files.json; fontes/pr162-checks.json; fontes/pr164-files.json; fontes/pr164-checks.json. Locadores e recorte: F19; #162/#164 diffs integrais e checks por head; models.py:335,396–429; init:72; pyproject:3; docs/lanes/VERIFY.md; busca SQL restrita. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: package 0.1.0, módulo 0.3.0 e default Verdict.verify_version 0.1.0; to_row serializa o valor da instância. Diff integral #162 muda módulo e acrescenta dois testes; diff #164 só toca três READMEs. Três checks success em #162 no head 3955f9d; zero check-runs capturados em #164. Busca lexical FROM/JOIN/INSERT INTO restrita a verify/src e verify/scripts encontrou SQL sobre job_conf e plan_transitions, não prova ausência de outros acessos indiretos. RELATO: contagens de testes dos autores. DECISÃO PENDENTE: release futura; não é gate da correção.

### Fluxo

Fluxo: pyproject.toml —(versão do pacote 0.1.0)→ distribuição; __version__ —(metadata do módulo)→ quem importa apex_verify; Verdict.verify_version default —(to_row)→ coluna verify_version em fix_verifications. Documentação: código —(tabelas realmente consultadas)→ brief da lane —(expectativa)→ outro pod. A #162 alinha o segundo ramo ao primeiro; o terceiro já estava alinhado.

### Consequências e risco

Sem ação, nenhuma linha gravada muda (já é 0.1.0); o risco é um consumidor de __version__ ver 0.3.0 e um leitor do brief supor que o Verify consulta findings diretamente. Confiança alta nos fatos estáticos; o impacto é de proveniência e documentação, não de cálculo.

### Alternativas e recomendação

Recomendado: revisar e integrar a #162 como correção de baixo risco; tratar docs/lanes/VERIFY.md num ajuste documental pequeno (ou incluir na #164 se o autor aceitar), dizendo o que é SQL próprio e o que chega por contrato, e trocando a contagem fixa por referência ao comando. Alternativas: elevar tudo para 0.3.0 (muda contrato de identidade das linhas; exige DEC-N2); não fazer nada em docs (deixa a deriva). Reversível.

### Dependências e paralelismo

#162 não depende de nada além de revisão; #164 também não. O ajuste de docs/lanes/VERIFY.md é independente de ambas e da #117. A política de versão futura (DEC-N2) não é gate da #162.

### Plano e aceite propostos

Passos: revisor examina os dois testes #162 e decide integração no head conferido; reconciliar docs/lanes/VERIFY.md distinguindo consulta SQL própria de entradas recebidas por contrato e substituindo contagem fixa por comando ou data. Conferência documental contra código basta para essa correção de baixo risco; a busca lexical delimita a evidência e não substitui análise de chamadores.

### Comunicação entre responsáveis

Para outro pod: "A #162 só alinha __version__ ao 0.1.0 que o pacote e as linhas já usam; nenhuma linha gravada muda. O brief docs/lanes/VERIFY.md ainda descreve tabelas e contagem de testes que precisam de ajuste separado."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Elevar todas as versões para 0.3.0 mudaria o default de identidade das linhas; alinhar somente __version__ a 0.1.0 preserva o default atual. Que caso o teste ainda não cobre? Os dois testes novos não foram executados nesta auditoria; contagem total e chamadores indiretos do Verify continuam fora da conferência. Como eu explicaria isso para outro pod? A #162 corrige metadata do módulo; o brief precisa distinguir SQL próprio de entradas recebidas por contrato, sem reescrever linhas históricas.

### Próxima ação e encerramento

Próxima ação: revisor Verify e mantenedor (a confirmar) decidem a #162; autor da #164 ou revisor documental decide onde corrigir docs/lanes/VERIFY.md. Entrada: heads 3955f9d e 5d42763 e o brief na base. Saída: #162 integrada ou fechada com motivo; correção do brief proposta. Encerramento: versões iguais na main e brief sem afirmações não sustentadas.

<a id="item-204"></a>

## F20 — Verify usa a população de tarefas bem-sucedidas do contrato v0.5 (TS45)

Frente: verify_populacao_tarefas. Encaminhamento: encerrar_pr_integrada_residuo_p50_sem_destino.

### Identidade e estado

F20 é uma correção de contrato do Pod 1/Verify (TS45), implementada pela PR luanmorenommaciel/apex#142 "fix(verify): use successful-task duration samples for stage analysis" (head 761f2c5), integrada em 2026-10-06T19:56:33Z no merge 7509e59. Sem assignee. A política para p50=0 (B-3), duração ausente e cobertura de amostras ficou fora da folha, segundo o registro.

### Intenção e benefício

Problema: StageObservation ignorava successful_task_p50/p99/sample_count (extra=ignore) e guardrails filtrava pela p50 legada, embora o CONTRACT.md v0.5 exija a população bem-sucedida quando sample_count > 0; com retries, skew ratio, bracket de trabalho, análise de bound e piso irmão divergiam do Engine. Público: quem confia no veredito do Verify para stages com retry. Ganho: Verify e Engine calculam sobre a mesma população.

### Feito, faltante e não comprovado

Feito na base: StageObservation escolhe successful_task_* quando successful_task_sample_count > 0 e conserva fallback legado. guardrails.py:242 exclui irmãos com p50 efetivo zero do conjunto de razões p99/p50; models.py:164 retorna skew_ratio 0 quando p50 é zero. O CV/piso de duração total usa job_runtimes_ms de forma independente (guardrails.py:262–270 e runtime_cv_pct:288–294). Falta decisão explícita para duração zero/ausente e cobertura; nenhuma alteração do piso de runtime é demonstrada pela exclusão p50=0.

### Linhagem

Linhagem: NA-09 (S14) e Lane B de 29/09 → plano apex-ts45-plan-prep → implementação TS45 com 15 testes novos (11 falhando na base) e aceite Task-Spec Tier 1 relatado (attempt 942d821e) → PR #142 (29/09) → check-runs sem steps → merge 7509e59 → resíduo p50=0. A v2 diz que o resíduo foi "registrado na #169"; o corpo da #169 menciona "histórico sem successful-task" e cita a #142, mas não menciona p50=0 e não tem comentários: elo ausente.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/verify__src__apex_verify__models.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/verify__src__apex_verify__guardrails.py.txt. Locadores e recorte: F20; #142/#169; models.py:128–170; guardrails.py:227–294. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: seleção pela população bem-sucedida e exclusão de irmãos com p50 efetivo zero. RELATO: 120 testes, 11 discriminantes, aceite Tier 1 e cinco divergências de skew Verify×Engine em dados sintéticos. INFERÊNCIA: o tratamento atual de p50=0 é implícito (exclusão), não uma política decidida. DECISÃO PENDENTE: p50=0 e duração ausente.

### Fluxo

Fluxo estático: successful_task_sample_count —(seleção de população)→ p50/p99 efetivos —(razão e análise de trabalho)→ Verify; irmãos —(p50 efetivo > 0)→ razões p99/p50 —(CV da razão)→ texto/score de instabilidade. Em ramo separado: job_runtimes_ms positivos —(CV de duração total)→ piso de verificação. Excluir p50=0 do primeiro ramo não implica removê-lo dos runtimes de job.

### Consequências e risco

Risco residual documentado: população de razões p99/p50 e cobertura de durações zero podem ser interpretadas sem política explícita. A exclusão pode mudar caracterização/score de instabilidade; não foi demonstrado que ela reduza o conjunto usado no CV de runtime. Frequência e impacto em vereditos não medidos; confiança alta na separação estática dos ramos.

### Alternativas e recomendação

Recomendado: encerrar F20 e dar ao resíduo p50=0 um destino explícito. Opções de destino: (a) nota/critério na #169, que já trata população legada, com autorização de comentário; (b) issue pequena do Verify; (c) aceitar a exclusão atual como política e documentá-la no código. Diferente da v2, não considero o resíduo já registrado na #169. O registro atribui a decisão ao owner do Verify via DEC-06 (ownership de Verify e Memory), o que é coerente; as alternativas de escritor de fix_verifications que a v2 lista ao lado não se aplicam a este resíduo.

### Dependências e paralelismo

Encerrar F20 não depende de nada. A decisão sobre p50=0 é independente de #117 e pode ocorrer junto com a decisão de população da #169, sem esperar suas migrações.

### Plano e aceite propostos

Primeiro registrar destino e política de p50=0/duração ausente, hoje sem critério nominal na #169. Se houver mudança de comportamento: menor folha verifica seleção efetiva, fallback, razão/instabilidade e separação do CV de job com entradas controladas; controles p50 positivo, zero e amostras sem sucesso. Se a decisão apenas documentar comportamento aceito, conferência documental é suficiente para a nota.

### Comunicação entre responsáveis

Para outro pod: "A #142 passou o Verify à população bem-sucedida com fallback histórico. p50=0 sai do cálculo de instabilidade p99/p50; o piso de runtime usa runtimes de job em outro ramo. Precisamos decidir a política de duração zero e registrar seu destino sem confundir os dois cálculos."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Tratar p50 zero como razão válida mudaria o conjunto de instabilidade p99/p50; isso não altera automaticamente o CV calculado de job_runtimes_ms. Que caso o teste ainda não cobre? A política de duração zero, ausente e cobertura continua pendente; não se pode atribuir sua cobertura à #169, cujo corpo não nomeia p50=0. Como eu explicaria isso para outro pod? A #142 seleciona successful-task quando há amostras; a decisão residual é como tratar zero/ausência, mantendo os dois cálculos de ruído separados.

### Próxima ação e encerramento

Próxima ação: dono do Verify (a confirmar) escolhe o destino do resíduo p50=0. Entrada: models.py, guardrails.py e #169. Saída: destino registrado. Encerramento de F20: imediato; o resíduo encerra quando a política estiver documentada ou testada.

<a id="item-205"></a>

## F21 — Verify recusa piso de ruído negativo ou não finito na certificação

Frente: verify_piso_ruido. Encaminhamento: encerrar_pr_integrada_residuos_em_dec05.

### Identidade e estado

F21 é correção do Pod 1/Verify na PR #145, head 142d6ea843103459f840f11ba7340370b072241c, integrada em 06/10 no merge fb094dc. O corpo descreve pilha sobre a branch da #142; o objeto capturado registra base SHA fa0951fe76192648025d1f9ffbe63dd06b5b9e51, não 761f2c5. O 761f2c5 é a referência histórica da pilha no registro. Sem assignee próprio.

### Intenção e benefício

Problema: um piso de ruído -1.0 certificava um delta de -11% com controle positivo aprovado (score 0.90), e NaN/inf passavam no controle positivo e apareciam na prosa como piso medido. Público: quem confia na certificação de um fix. Ganho: nenhum veredito ou magnitude é certificado com piso inválido; piso zero continua aceito.

### Feito, faltante e não comprovado

Na base, valid_noise_floor exige piso medido, finito e não negativo (models.py:259–266); significant usa esse predicado, attributable e abs(delta) >= piso (269–274); to_row grava NULL para piso inválido (417). Igualdade e política de zero permanecem decisões de compatibilidade #117/DEC-05. Roundtrip e testes históricos não foram reexecutados.

### Linhagem

Linhagem: relatório apex-verify-invalid-floor-pr145 → PR #145 head 4a35bcf (29/09) → revisão Claude independente sem defeito bloqueante (relato) → correção 142d6ea (30/09) com 8 casos de fidelidade, 4 falhando antes → empilhada sobre #142, sem CI → merge da #142 e depois da #145 em 06/10 → resíduo DEC-05. Paralelos já integrados: S21 (Serve retém veredito com piso inválido) e S22 (API rejeita noise_floor_pct inválido).

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/verify__src__apex_verify__models.py.txt. Locadores e recorte: F21; #145 head 142d6ea/base capturada fa0951f; models.py:259–279,396–429. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: valid_noise_floor exige measured, math.isfinite e floor >= 0; significant depende desse predicado; to_row escreve null para piso inválido. RELATO HISTÓRICO: 129 testes, controles e revisão cruzada do autor. Não se revalidou CI/review formal histórico; a ausência relatada de check-runs não prova que nunca existiu outra execução. DECISÃO PENDENTE: igualdade e política de zero em #117.

### Fluxo

Fluxo observado: replay —(noise_floor_pct medido)→ propriedade de piso válido —(finito e ≥ 0)→ certificação permitida; —(negativo, NaN ou inf)→ certificação recusada e prosa sem "piso medido". O Serve e a API aplicam regras paralelas (S21/S22), sem chamar o Verify.

### Consequências e risco

Sem ação, a proteção está na main. O risco residual é o caso de igualdade delta = piso e piso zero, ainda sem decisão, que pode produzir rótulos diferentes entre consumidores. Confiança alta no fato estático.

### Alternativas e recomendação

Recomendado: encerrar F21 e manter piso zero/igualdade em DEC-05 dentro do contrato #117. Alternativa: tratar piso zero como inválido também, que mudaria certificações hoje possíveis e exige decisão. Reversível.

### Dependências e paralelismo

Nenhuma dependência para encerrar. DEC-05 depende do contrato de piso/atribuição na #117 e pode ser discutida em paralelo com F20 e com a decisão de população.

### Plano e aceite propostos

Condição de não ação: nenhum passo de produto. Registrar que negativo e não finito estão cobertos e que igualdade/piso zero seguem em DEC-05. Reabrir se a main voltar a certificar com piso negativo ou não finito.

### Comunicação entre responsáveis

Para outro pod: "O Verify não certifica mais com piso negativo, NaN ou infinito (#145). Se delta igual ao piso certifica ou não, e o que fazer com piso zero, ainda é decisão do contrato #117."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Aceitar piso negativo ou não finito voltaria a sustentar certificação e prosa sem medida válida; rejeitar zero também mudaria a política atual. Que caso o teste ainda não cobre? A revisão não reproduz roundtrip em ClickHouse nem resolve a igualdade entre Verify >= e projeções >. Como eu explicaria isso para outro pod? A #145 protege a certificação e a serialização contra piso inválido; zero e igualdade são decisões separadas do contrato.

### Próxima ação e encerramento

Próxima ação: confirmar encerramento de F21 com ponteiro para DEC-05/#117. Owner: Pod 1 (a confirmar). Entrada: models.py e #145. Saída: linha F21 "entregue em fb094dc; igualdade e piso zero em DEC-05". Encerramento: imediato.

<a id="item-206"></a>

## E03 — Provar #131 contra ClickHouse real com database alternativo

Frente: engine_database_configuravel. Encaminhamento: estudar_prova_leitura_insert_db_alternativo_preflight_ja_provado.

### Identidade e estado

E03 é um item seed de runtime do Pod 2/Engine: provar a #131 contra ClickHouse real com database alternativo. Objeto público ligado: PR luanmorenommaciel/apex#131 (integrada em 06/10, merge e867232). Sem issue própria, sem assignee; owner a confirmar (Pod 2). Estado do item: parcialmente provado por relato local de 30/09; a v2 e o inventário dizem "prova com database alternativo nunca executada", o que contradiz o próprio registro.

### Intenção e benefício

Problema: depois da #131, o Engine resolve tabelas não qualificadas no database configurado; falta mostrar que um database como apex_staging é realmente lido e escrito por todo o caminho do Engine, não só pelo preflight. Público: quem opera mais de um database no mesmo ClickHouse (staging, testes, clientes). Ganho: confiança de que configurar CLICKHOUSE_DATABASE não mistura dados entre databases.

### Feito, faltante e não comprovado

Feito (relato E03, 30/09, head 7b7b9b4, ClickHouse 24.8.14.39 descartável): dois databases alternativos completos passam o preflight, um terceiro sem executor_run_time_ms falha com SchemaOutOfDateError nomeando coluna e database, erro de conexão é propagado e um controle negativo derruba o harness. Falta: leituras (STAGE_AGGREGATES_SQL e afins) e INSERT (persist_findings) com dados no database alternativo, que o relatório declara explicitamente não verificados porque os databases tinham zero linhas. Não comprovado: comportamento na main c3c3ea3, que inclui merges posteriores.

### Linhagem

Linhagem: seed E03 → candidato schema95 de 07/09 (implementação diferente, não transferível) → R2 de 27/09 sobre o head antigo d96d9b5 (não transferível) → TS16/E03 em 30/09 no head 7b7b9b4 com seis controles → merge da #131 em 06/10 → prova de leitura/INSERT [ausente] → CI hospedada [ausente]. Elo ausente: qualquer recibo de leitura/escrita com payload do Engine.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-revalidated-fes-sources/e03-report.md; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/engine__src__apex_engine__clickhouse.py.txt; fontes/batch-revalidated-fes-sources/engine__src__apex_engine__watchers____init__.py.excerpt.txt. Locadores e recorte: E03; #131; relatório E03 integral; Engine clickhouse.py:30–145,283–345,451–465; watchers/__init__.py:38–68. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO estático: connect passa settings.database ao preflight e ao EngineStore; as queries de stage são não qualificadas e persist_findings passa database=self._database ao insert. RELATO HISTÓRICO: E03 cobre apenas conexão/preflight em databases vazios, com 161/10 na suíte core sem crew. O sexto controle foi NOT APPLICABLE, não mais um teste runtime aprovado. Leitura e escrita com payload continuam sem prova nesse relatório.

### Fluxo

Fluxo estático a provar em runtime: client configurado → preflight system.columns → EngineStore.stage_aggregates via STAGE_AGGREGATES_SQL → watchers.run_all_offline/evaluate → persist_findings com database explícito. O relatório exercita só conexão/preflight; run_all usa agregados do store, sem chamar as seis constantes SQL dos watchers neste caminho.

### Consequências e risco

Risco possível: uma leitura/escrita futura ignorar o database configurado. As seis constantes com apex. merecem inventário, mas não provam mistura no caminho run_all, que usa o store. Nenhum incidente ou execução de payload em database alternativo foi demonstrado.

### Alternativas e recomendação

Recomendado: uma prova pequena e isolada com dois databases povoados com o mesmo job_id e valores diferentes, verificando que leitura e INSERT acontecem só no configurado. Alternativas: aceitar o preflight como suficiente e documentar o limite (mais barato, deixa a pergunta aberta); ou esperar a auditoria E04 terminar e provar só depois (evita provar duas vezes, mas não é obrigatório). Reversível; não altera produto.

### Dependências e paralelismo

Pode começar já com dados sintéticos; não depende de CI (#130). A recontagem E04/#173 informa quais caminhos precisam entrar na prova, mas o estudo da prova pode correr em paralelo. Não depende de #155 (E20).

### Plano e aceite propostos

Passos mínimos: (1) ClickHouse descartável com apex e apex_alt; (2) mesmo job_id em ambos, valores distintos; (3) Engine apontado para apex_alt lê e grava; (4) controles: leitura retorna valores de apex_alt, apex.findings fica intacta, um watcher com apex. literal é detectado se ler o database errado; (5) recibo com versão, comandos e hashes, sem credenciais. Aceite: discriminante entre os dois databases.

### Comunicação entre responsáveis

Para outro pod: "O preflight da #131 já foi provado em databases alternativos; ainda não sabemos se todas as leituras e escritas do Engine respeitam o database configurado. A prova proposta usa dois databases com o mesmo job_id para distinguir."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Aceitar só o preflight como prova de todo o Engine deixaria sem observação as queries e o insert com payload no database configurado. Que caso o teste ainda não cobre? Bancos vazios não distinguem leitura de apex e apex_alt; faltam duas populações com mesmo job_id e resultados distintos, mais verificação do destino do insert. Como eu explicaria isso para outro pod? E03 provou historicamente a seleção do database no preflight; a prova restante é do fluxo de dados, e constantes antigas não são prova de execução.

### Próxima ação e encerramento

Próxima ação: Pod 2 (a confirmar) decide se o aceite exige leitura/INSERT e, se sim, prepara a prova isolada. Entrada: relatório E03 e recontagem E04. Saída: recibo discriminante com dois databases. Encerramento: recibo aceito, ou decisão registrada de que o preflight basta, com o limite escrito.

<a id="item-207"></a>

## E04 — Database configurável nas lanes ainda com 'apex.' literal

Frente: engine_database_configuravel. Encaminhamento: agrupar_em_173_inventario_recontado.

### Identidade e estado

E04 é uma auditoria do Pod 2+Pod 3 sobre literais apex. que ainda fixam o database. Publicada da minuta P-E04 como issue luanmorenommaciel/apex#173 em 2026-10-11 por gustocezar, aberta, sem assignee e sem comentários no snapshot. Owner a confirmar (Engine, Memory, Serve, Verify).

### Intenção e benefício

Problema: a #131 e a #129 tornaram configurável o database do Engine e do Serve, mas outros consumidores ainda podem ter SQL com apex. qualificado, de modo que CLICKHOUSE_DATABASE teria efeito parcial. Público: quem opera databases alternativos. Ganho: uma matriz por lane que diz quem suporta database configurável e onde um literal ainda fixa a leitura.

### Feito, faltante e não comprovado

Inventário lexical c3c3ea3: 20/29/33/18 linhas com apex.<palavra> em Engine/Memory/Serve/Verify. O regex de SQL captura 6/15/1/2 linhas respectivamente, mas também apanha prosa. Após leitura, há seis constantes FROM apex.spark_events nos watchers, 11 ocorrências SQL qualificadas em Memory (10 clickhouse.py, uma recall.py) e uma em Verify config_source.py. O exemplo do Serve e o segundo do Verify são texto. run_all:64–68 busca agregados do store e chama evaluate; não utiliza essas seis constantes nesse caminho. Contagens não são prova de alcançabilidade nem inventário de SQL dinâmica.

### Linhagem

Linhagem: seed E04 e corpo da #131 (cobertura só de clickhouse.py e crew/tools.py) → contagem histórica na a289e53 → merges #129 e #131 em 06/10 → minuta P-E04 → #173 (11/10) → recontagem nesta revisão (18/10) → decisão por lane [ausente] → mudanças [ausentes]. Elo ausente: inventário público na #173.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-revalidated-fes-sources/database-literal-search.json; fontes/batch-revalidated-fes-sources/engine__src__apex_engine__watchers____init__.py.excerpt.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/engine__src__apex_engine__clickhouse.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/memory__src__apex_memory__clickhouse.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/memory__src__apex_memory__recall.py.txt. Locadores e recorte: E04/P-E04/#173; inventário lexical na base; Memory clickhouse.py/recall.py; Engine run_all e store; Verify config_source.py literal preservado no inventário. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: literais SQL e texto separados no inventário; o caminho run_all lido usa o store, cujas queries de stage são não qualificadas. PROPOSTA: matriz por consulta, configuração e chamador; DECISÃO PENDENTE: perfis suportados por lane. Nenhuma execução ou chamada indireta universalmente auditada.

### Fluxo

Fluxo lido: configuração do client → store do Engine/Serve → SQL de stage não qualificada; Engine run_all → agregados do store → evaluate. Memory e Verify contêm literais SQL apex.; a análise ainda deve relacionar cada consulta ao chamador. As seis constantes dos watchers são definições, sem chamada demonstrada em run_all.

### Consequências e risco

Sem decisão, quem configurar um database alternativo pode ter Engine/Serve lendo um database e Memory outro, produzindo histórico inconsistente. É risco possível; não há relato de uso real com database alternativo. Confiança alta na contagem, com o limite de regex.

### Alternativas e recomendação

Recomendado: publicar a matriz recontada na #173 e decidir por lane. Alternativas: (a) declarar apex como único database suportado para Memory/Verify e documentar; (b) remover qualificação nas queries e confiar no database da sessão, como fez a #129; (c) interpolar o nome configurado, que a #129 evitou por segurança. (b) é o padrão já adotado.

### Dependências e paralelismo

O inventário não depende de nada e pode correr em paralelo a E03. Mudanças em Memory dependem de decisão; as dos watchers dependem de saber se as constantes estão vivas no caminho do Engine. Nada aqui depende de #130.

### Plano e aceite propostos

Menor entrega: inventário por arquivo/consulta classificando SQL, texto e alcançabilidade; decisão por lane; mudanças aprovadas com controle de database alternativo e preservação de binding. Guarda por regex simples não deve confundir comentário com SQL nem substituir prova do chamador.

### Comunicação entre responsáveis

Para outro pod: Memory e Verify ainda contêm SQL qualificada; seis constantes antigas aparecem nos watchers, mas o run_all lido consulta o store. Primeiro mapear uso efetivo e perfis suportados; depois decidir mudanças na #173.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Substituir apex. globalmente alteraria texto e possíveis contratos intencionalmente fixos; tratar uma constante como query ativa inventaria um fluxo não demonstrado. Que caso o teste ainda não cobre? A contagem não prova alcançabilidade, SQL dinâmica ou comportamento em database não padrão; cada query precisa de chamador e controle discriminante. Como eu explicaria isso para outro pod? A #173 separa configuração do client, SQL executável e texto; run_all usa o store, enquanto Memory e Verify ainda exigem decisão por consulta.

### Próxima ação e encerramento

Próxima ação: Pods 2 e 3 (a confirmar) recebem a matriz e decidem por lane. Entrada: recontagem desta ficha. Saída: comentário/tabela na #173 e decisões. Encerramento: cada lane com decisão registrada e, se aplicável, mudança com teste.

<a id="item-208"></a>

## E05 — Reconciliação contrato declarado × runtime (#109)

Frente: arquitetura_contrato_runtime. Encaminhamento: estudar_em_paralelo_runtime_com_autorizacao_propria.

### Identidade e estado

E05 é o estudo de reconciliação entre contrato declarado e runtime (Pod 2/Infra), representado pela issue luanmorenommaciel/apex#109 "[Study][Pod 2 / Infra] Define declared-contract versus runtime reconciliation", aberta, sem assignee e sem comentários no snapshot. Owner a confirmar.

### Intenção e benefício

Problema: o contrato declara colunas, tabelas e caminhos, mas um ambiente pode divergir (schema atrás, coluna nunca preenchida, MV quebrada), e um diagnóstico construído sobre o declarado engana. Público: operadores e Pods que confiam no grafo de proveniência. Ganho: detectar drift antes de o diagnóstico ficar enganoso, com estados declarado/observado.

### Feito, faltante e não comprovado

Há relatório e schema locais de 29/08 sobre 847d7a0 com classificação ready_offline, não implementação adotada. Preflight exige colunas e verify_ddl compara nomes/tipos de sete tabelas; nenhum prova transporte/behavior. Falta reconciliar o desenho e decidir a hierarquia de probes e recibo. A #109 permite desenho e exige autorização específica para execução.

### Linhagem

Linhagem: seed E05 → issue #109 → estudo #106 sobre 847d7a0 → relatório de 29/08 (descendentes #107/#108/#109) → camada de contexto de 10/10 → decisão [ausente] → probes [ausentes]. Semente técnica: preflight #131 (P05). Elo ausente: vínculo público entre a #109 e o schema local.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-revalidated-fes-sources/system-graph-REPORT.md; fontes/batch-revalidated-fes-sources/system-graph-runtime-reconciliation.schema.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/engine__src__apex_engine__clickhouse.py.txt; fontes/batch-revalidated-fes-sources/infra__scripts__verify_ddl.py.excerpt.txt. Locadores e recorte: E05/#109 integral; relatório/schema runtime de 29/08; preflight Engine:283–294; verify_ddl.py:1–39,114–135. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: issue aberta; preflight e verify_ddl na base. RELATO: estudo ready_offline e schema local. INFERÊNCIA: o schema precisa ser revisto contra a apex-api e as migrações 034-039. DECISÃO PENDENTE: adotar/adiar (DEC-19) e autorização própria para runtime. Nenhum teste ou runtime nesta revisão.

### Fluxo

Fluxo proposto na #109: contrato/DDL esperados + probes read-only autorizados de metadados → classificação match/drift/blocked/inconclusive → recibo sanitizado vinculado à identidade. Canário OTLP e workload Spark são camadas separadas; não se promovem a provados por metadados. Nenhum reparo automático.

### Consequências e risco

Sem o estudo, divergências continuam aparecendo como erro tardio ou como finding plausível sobre dado ausente; é risco possível de diagnóstico enganoso, não incidente. Confiança média no estudo (relato) e alta no escopo limitado das proteções atuais.

### Alternativas e recomendação

Recomendado: atualizar o desenho para a superfície atual e decidir na #109 o primeiro recorte (por exemplo, colunas tipadas sempre zero após migração, ligado a E22). Alternativas: adiar pós-v1 (v2; aceitável se registrado); ampliar verify_ddl.py (mistura verificação de schema com runtime, ver E23). Diferente da v2, o estudo não espera a #106: só a implementação usa o schema do grafo.

### Dependências e paralelismo

Estudo paralelo a #106, #107, #108 e #170. Runtime exige autorização própria e ambiente descartável. A semente #131 já está integrada. Nada aqui bloqueia v1.

### Plano e aceite propostos

Passos mínimos de estudo: (1) inventário de probes read-only com custo e allowlist; (2) estados e mensagens; (3) primeiro recorte e critério; (4) decisão na #109. Para uma futura execução: controle negativo com coluna presente e sempre zero, que o preflight atual não acusa.

### Comunicação entre responsáveis

Para outro pod: nomes e tipos corretos não provam transporte nem comportamento. A #109 desenha probes com estados e identidade; sua execução permanece separada e autorizada.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Inferir transporte OTLP ou comportamento Spark de system.columns faria um schema verde parecer prova de integração. Que caso o teste ainda não cobre? O schema local e exemplos não foram executados; probes de transporte e workload exigem recibos próprios e não são cobertos por preflight. Como eu explicaria isso para outro pod? A reconciliação compara declarado e observado com identidade e limites, sem remediar o store e sem transformar metadados em runtime completo.

### Próxima ação e encerramento

Próxima ação: Infra/Engine (a confirmar) produzem plano revisável e pedem decisão na #109. Entrada: relatório de 29/08 e schema local. Saída: plano com primeiro recorte. Encerramento do estudo: decisão adotar/adiar registrada; runtime só com autorização separada.

<a id="item-209"></a>

## E06 — Protocolo versionado R9D (#113)

Frente: harness_overhead_r9d. Encaminhamento: decidir_protocolo_sem_gate_previo_do_harness.

### Identidade e estado

E06 é o protocolo versionado de evidência de overhead R9D (Pod 2/Harness), representado pela issue luanmorenommaciel/apex#113 "[Harness] Ratify a versioned R9D overhead evidence protocol", aberta, sem assignee e sem comentários. Owner a confirmar (Harness + mantenedor).

### Intenção e benefício

Problema: sem protocolo versionado, um número de overhead como +3,73% (medido num ambiente) pode ser citado como propriedade geral do produto e interpretado seletivamente. Público: quem fará alegações de overhead em release ou documentação. Ganho: cada número de overhead vem com protocolo, ambiente, repetições e limiares aprovados.

### Feito, faltante e não comprovado

Feito: protocolo validado offline em 6 casos semânticos em 29/08 (relato do registro); +3,73% registrado como medida histórica de um ambiente. Falta: thresholds, dono e se o protocolo é gate de release ou sob demanda. Não comprovado: execução do protocolo sobre a main; o harness atual tem o defeito de argumentos da #167, que afeta a execução, não o desenho.

### Linhagem

Linhagem documental: registro E06 → #113 e relato de seis casos offline de 29/08 → decisões de estimador, faixas, dono/runner [não demonstradas no objeto público] → execução própria futura. O corpo afirma nenhum predecessor técnico para desenhar; #167 trata o runner do caminho atual, não o protocolo em si.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/dev__scripts__r9d_overhead_ab.py.txt. Locadores e recorte: E06/#113 integral e registro: seis casos semânticos/+3,73% como relatos; interface do harness usada apenas para dependência. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: issue aberta sem decisão. RELATO: seis casos offline e +3,73% num ambiente. DECISÃO PENDENTE: dono dos thresholds e papel do protocolo. Sem execução nesta revisão.

### Fluxo

Fluxo proposto: protocolo versionado —(braços ON/OFF, repetições, ambiente declarado)→ harness R9D —(medições)→ análise com limiares aprovados —(número com intervalo e ambiente)→ notas de release. Execução depende do harness funcional (#167); desenho não.

### Consequências e risco

Sem protocolo, o risco é uma alegação pública de overhead sem método; se a v1 não fizer alegação de overhead, o impacto é baixo. Confiança alta na leitura da dependência.

### Alternativas e recomendação

Recomendado: decidir primeiro se as notas da v1 vão citar overhead; se sim, ratificar o protocolo antes; se não, registrar adiamento explícito. Alternativas: gate de release obrigatório (custo de runner e tempo); sob demanda (risco de esquecer). Reversível.

### Dependências e paralelismo

Desenho pode avançar em paralelo à #167/#174. Uma execução pelo harness atual exige corrigir sua interface e fixar ambiente; outro caminho aprovado deve demonstrar equivalência dos braços. A #113 não autoriza execução nem impõe gate de release sem decisão.

### Plano e aceite propostos

Passos mínimos: (1) mantenedor responde se v1 cita overhead; (2) se sim, versionar o protocolo com limiares e dono; (3) só depois uma execução separada. Critério: protocolo com número de versão e dono registrado; ou adiamento registrado.

### Comunicação entre responsáveis

Para outro pod: "O +3,73% é uma medida de um ambiente, não uma propriedade do produto. Antes de citar overhead, precisamos de um protocolo aprovado; corrigir o harness (#167) é necessário para executar, não para decidir o protocolo."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Generalizar +3,73% de um ambiente sem estimador/faixa predeclarados transformaria resultado local em propriedade do produto. Que caso o teste ainda não cobre? Os seis casos são relatos; falta ratificar versão, warm-up, amostra, classificações e settlement antes de nova execução autorizada. Como eu explicaria isso para outro pod? Consertar argumentos do runner torna um caminho executável; aprovar o protocolo define como interpretar overhead sem selecionar resultados favoráveis.

### Próxima ação e encerramento

Próxima ação: mantenedor (a confirmar) decide se v1 fará alegação de overhead. Entrada: #113 e status de #167. Saída: decisão registrada na #113. Encerramento: protocolo ratificado ou adiamento explícito.

<a id="item-210"></a>

## E07 — Rehearsal ClickHouse 26.x e rollback (#114)

Frente: infra_versao_clickhouse. Encaminhamento: adiar_ou_estudar_upgrade_sem_alterar_pin.

### Identidade e estado

E07 é um ensaio controlado de upgrade do ClickHouse para 26.x com rollback (Pod 2/Infra), representado pela issue luanmorenommaciel/apex#114 "[Study][Infra] Rehearse ClickHouse 26.x upgrade and rollback", aberta, sem assignee. Owner a confirmar (Infra + mantenedor).

### Intenção e benefício

Problema: a main fixa clickhouse/clickhouse-server:24.8 (infra/docker-compose.yml:39); evidência histórica em 26.1 existe, mas um upgrade sem rollback testado pode quebrar migrações e MVs. Público: operadores de instalações existentes. Ganho: um caminho de upgrade com rollback demonstrado quando houver motivo para subir.

### Feito, faltante e não comprovado

Base: imagem 24.8 confirmada no Compose. Feito: desenho validado offline (relato). Falta: decidir se há intenção de upgrade; plano de matriz upgrade/rollback; prova em runtime isolado. A issue, segundo a ficha Codex, não recomenda upgrade e não autoriza runtime.

### Linhagem

Linhagem: seed E07 → issue #114 → desenho offline (relato) → evidência 26.1 histórica (não transferível) → decisão [ausente] → ensaio [ausente]. Sem elo de implementação.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-revalidated-fes-sources/infra__docker-compose.yml.sanitized.txt. Locadores e recorte: E07/#114 integral; Compose infra pin 24.8; histórico separado do alvo 26.x. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: pin 24.8 na base. RELATO HISTÓRICO: desenho de ensaio validado offline e experimentos em 26.1 que não se transferem para a main. DECISÃO PENDENTE: se existe upgrade planejado e quem autoriza runtime isolado. Nenhuma execução nesta revisão.

### Fluxo

Fluxo proposto: estado 24.8 identificado → backup verificado/restaurável → candidato 26.x exato com digest → gates DDL/MV, Collector e Engine → classificação → rollback definido a partir do ponto restaurável. Trocar a imagem de volta não é prova de recuperação de volume.

### Consequências e risco

Sem ação, a main continua em 24.8 e nada quebra; o risco aparece só se alguém subir a versão sem ensaio de migrações e MVs, ou se a 24.8 sair de suporte e forçar um upgrade apressado. Confiança alta no estado; não consultei calendário de suporte do ClickHouse.

### Alternativas e recomendação

Recomendado: manter adiado enquanto não houver motivo de upgrade, com o plano de matriz preparado em paralelo se alguém tiver capacidade. Alternativas: ensaiar já (custo sem demanda); fixar uma versão 25.x intermediária (exige decisão de suporte). Reversível.

### Dependências e paralelismo

Desenho sem predecessor técnico. #109 (reconciliação) e #170 (quietude de migrações) informam critérios, mas não bloqueiam o estudo. Execução exige autorização e ambiente isolado.

### Plano e aceite propostos

Condição de não ação: sem intenção de upgrade registrada, nenhum passo além de manter a #114 aberta como estudo. Se houver intenção: matriz upgrade/rollback, critérios (schema, MVs, ingestão, verify_ddl), recibo em ambiente descartável.

### Comunicação entre responsáveis

Para outro pod: "A main usa ClickHouse 24.8. A #114 prepara um ensaio de upgrade com rollback; ela não recomenda subir a versão nem autoriza executar."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Trocar só a imagem de volta pode deixar persistência e MVs incompatíveis; o ponto restaurável precisa existir antes do ensaio. Que caso o teste ainda não cobre? Nenhum upgrade, rollback ou compatibilidade 26.x foi executado nesta auditoria; o histórico 26.1 não prova a base atual. Como eu explicaria isso para outro pod? A #114 prepara versão, backup, gates e falha parcial; o pin segue 24.8 no código lido e adoção depende de decisão.

### Próxima ação e encerramento

Próxima ação: mantenedor/Infra (a confirmar) declaram se há intenção de upgrade. Entrada: #114. Saída: decisão rehearse/defer/reject. Encerramento: decisão registrada.

