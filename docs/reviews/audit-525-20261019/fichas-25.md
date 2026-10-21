# Fichas documentais — lote 25

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-241"></a>

## X04 — SECURITY.md e canal privado (#33)

Frente: governanca_seguranca. Encaminhamento: decidir_canal_e_executar_security_md.

### Identidade e estado

X04 é a decisão/PR cross-pod de criar SECURITY.md e um canal privado de vulnerabilidades, representada pela issue luanmorenommaciel/apex#33 "[Governance] Add SECURITY.md (LICENSE + NOTICE done)", aberta, sem assignee. Decisão: mantenedor (DEC-12), a confirmar.

### Intenção e benefício

Problema: a base consultada não contém SECURITY.md na raiz e a #33 pede política de reporte privado. Isso não demonstra que todos os mecanismos privados estejam indisponíveis no GitHub. Público: quem encontra vulnerabilidades. Ganho: instrução pública de canal e triagem com responsáveis reais.

### Feito, faltante e não comprovado

Base c3c3ea3: LICENSE Apache-2.0 e NOTICE presentes; SECURITY.md ausente na raiz. Comentário do mantenedor 5718044465, de 17/09, confirma LICENSE/NOTICE feitos e restringe entrega a SECURITY.md. O corpo original preserva perguntas anteriores sobre MIT, sem reabrir a escolha. Falta canal, responsáveis e texto aprovado; nenhuma questão jurídica é decidida nesta revisão.

### Linhagem

Linhagem: seed X04 e R2 T30/H03d → issue #33 → LICENSE e NOTICE entregues (título atualizado) → decisão de canal [ausente] → PR documental [ausente].

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/primary-public-selected.json issue[33] e comentário 5718044465; fontes/batch-revalidated-xldd-sources/code/LICENSE, fontes/batch-revalidated-xldd-sources/code/NOTICE; fontes/batch-revalidated-xldd-sources/code-manifest.json (base c3c3ea3) e registro X04. A ausência foi conferida na listagem da raiz dessa ref; não foi inspecionada configuração privada do GitHub.

### Classe e limite da evidência

FATO OBSERVADO: ausência de SECURITY.md; presença de LICENSE Apache-2.0 e NOTICE. DECISÃO PENDENTE: canal (GitHub Security Advisories privados, e-mail ou outro) e responsáveis. Sem execução.

### Fluxo

Fluxo proposto: relator —(canal privado documentado)→ triagem —(confirmação/prazo)→ correção e comunicação acordada. O estado de recursos privados do GitHub não foi consultado; falta é de política no recorte da issue.

### Consequências e risco

Sem canal, uma vulnerabilidade tende a ser relatada em issue pública ou não ser relatada; é risco de processo, sem incidente conhecido. Confiança alta na ausência do arquivo.

### Alternativas e recomendação

Recomendado: usar o recurso de relato privado de vulnerabilidades do GitHub como canal, com SECURITY.md curto (versões suportadas, como relatar, prazo de resposta) e responsáveis nomeados pelo mantenedor. Alternativas: e-mail dedicado (exige caixa monitorada); só texto sem canal (insuficiente). Não inventar contato.

### Dependências e paralelismo

Não depende de nada técnico. Pode orientar E13 (credenciais locais) e E15 (dependências), sem ser gate deles. #42 (on-prem) pode ser estudado em paralelo.

### Plano e aceite propostos

Passos mínimos: (1) mantenedor escolhe canal e responsáveis; (2) PR documental com SECURITY.md; (3) se o canal for advisories privados, ativação pelo admin do repositório (fora desta revisão); (4) fechar a #33. Aceite: SECURITY.md na main com canal funcional.

### Comunicação entre responsáveis

Para outro pod: "Licença e NOTICE estão feitos; falta dizer como relatar uma vulnerabilidade em privado. A decisão é só do mantenedor: canal e quem responde."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere publicar canal sem responsável capaz de responder. Que caso o teste ainda não cobre? A conferência da raiz não testa a operação de um canal privado. Como eu explicaria isso para outro pod? Explique o escopo SECURITY.md já estreitado pelo mantenedor.

### Próxima ação e encerramento

Próxima ação: mantenedor (a confirmar) escolhe canal e responsáveis. Entrada: #33. Saída: PR com SECURITY.md. Encerramento: SECURITY.md integrado e #33 fechada.

<a id="item-242"></a>

## X05 — Modo offline/on-prem seguro (#42)

Frente: produto_onprem. Encaminhamento: estudar_em_paralelo_prioridade_do_mantenedor.

### Identidade e estado

X05 é um spike cross-pod/segurança para definir um modo offline/on-prem seguro para os agentes do APEX, representado pela issue luanmorenommaciel/apex#42 "[SPIKE] Definir modo offline/on-prem seguro para agentes Apex", aberta desde 2026-07-04, sem assignee e sem comentários. Owner: produto/segurança (a confirmar).

### Intenção e benefício

Problema: empresas sem egress não conseguem usar agentes que chamam um LLM externo; sem desenho, cada adoção improvisa. Público: clientes com dados sensíveis ou rede fechada. Ganho: um modo documentado com riscos, opções de deployment e requisitos de redaction e audit trail.

### Feito, faltante e não comprovado

Issue #42 lida integralmente: entregáveis são matriz de riscos/mitigações, decisão preliminar local-first/BYOC/SaaS/híbrido e requisitos de redaction/audit trail. Sem comentário ou estudo anexado na captura; isso não demonstra ausência de pesquisa local. Falta escolher prioridade e dono, e reconciliar eventuais estudos existentes. Nenhuma política de egress da v1 foi provada.

### Linhagem

Linhagem: #42 criada em 04/07 → registro X05 recomenda defer → complemento documental público de 10/10 preserva a preocupação futura e as entregas → captura 16/10 sem comentário → decisão de prioridade não localizada no recorte. Não chamar a data de criação de última atualização.

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/primary-public-selected.json issue[42] (created_at 2026-07-04T18:17:46Z; updated_at 2026-10-10T23:26:47Z; corpo integral, Definition of Done e escopo); fontes/batch-revalidated-xldd-sources/selected-register-matrix.json X05 (recomendação histórica de adiamento, não decisão do mantenedor).

### Classe e limite da evidência

FATO OBSERVADO: issue aberta, sem comentários no snapshot. RELATO: nenhum. INFERÊNCIA: zero comentários não prova ausência de pesquisa local. DECISÃO PENDENTE: prioridade do produto e dono. Nenhuma execução.

### Fluxo

Fluxo conceitual a estudar: dados/telemetria/código —(limites de egress e redaction)→ agente —(modelo local, endpoint privado ou remoto conforme desenho)→ resposta —(audit trail)→ operador. A revisão não demonstra implementação nem inexistência universal desses caminhos.

### Consequências e risco

Sem desenho explícito, adoções com restrições de egress podem exigir adaptações ou ficar inviáveis; a frequência e a demanda não foram medidas. Não se conclui que a v1 depende de egress: essa política não está decidida nas fontes lidas.

### Alternativas e recomendação

Recomendado: dono de produto decide prioridade segundo ambientes/demanda reais; pode produzir estudo mínimo sem esperar SECURITY.md. Adiamento pós-v1 é alternativa de planejamento, não decisão já tomada nem prova de que o tema nunca seja critério da v1.

### Dependências e paralelismo

Não depende de #33 para começar (Codex); política de disclosure informa o desenho. Requisitos de redaction podem reaproveitar o tratamento de plan_json como entrada não confiável.

### Plano e aceite propostos

Condição de não ação: sem cliente ou prioridade declarada, manter adiado com motivo registrado. Se priorizado: matriz de riscos, duas opções de deployment e requisitos mínimos de redaction/audit.

### Comunicação entre responsáveis

Para outro pod: “A #42 pede um spike de requisitos e uma decisão de implantação. A captura não registra a escolha; egress da v1 também não foi ratificado por este estudo.”

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere declarar egress obrigatório sem decisão de implantação. Que caso o teste ainda não cobre? A leitura do spike não cobre redaction e audit trail em ambiente real. Como eu explicaria isso para outro pod? Explique offline, on-prem e egress como requisitos a definir.

### Próxima ação e encerramento

Próxima ação: mantenedor/produto (a confirmar) decide prioridade. Entrada: #42. Saída: decisão preliminar registrada. Encerramento: matriz entregue ou adiamento com motivo.

<a id="item-243"></a>

## X07 — System/contract graph (#106)

Frente: arquitetura_grafo_sistema. Encaminhamento: decidir_adocao_do_grafo_estudos_paralelos.

### Identidade e estado

X07 é o ADR/estudo cross-pod de um grafo read-only de sistema e contrato, representado pela issue luanmorenommaciel/apex#106 "[ADR/Study] Evaluate a read-only APEX system and contract graph", aberta, sem assignee. Decisão: adotar/adiar/rejeitar (DEC-19), mantenedor cross-pod a confirmar.

### Intenção e benefício

Problema: ownership de campos, produtores e consumidores está espalhado entre CONTRACT.md, DDLs, código e a matriz de compatibilidade; não há uma fonte estruturada que as views (#108), o MCP (#107) e a reconciliação (#109) possam consumir. Público: todos os Pods. Ganho: um schema único de nós e arestas com estado de prova.

### Feito, faltante e não comprovado

Estudo local REPORT.md lido integralmente, na base 847d7a0: recomenda manifesto JSON, separa basis de proof_state e relata exemplo de 6 nós/5 arestas e validação offline. A existência do relatório está observada; validação executada nele permanece relato. Falta decisão adopt/defer/reject e atualização do exemplo contra a base escolhida; não houve validação atual do schema.

### Linhagem

Linhagem: matriz de compatibilidade #103/#111/#121 como semente → issue #106 → estudo de 29/08 → descendentes #107-#109 (relatório separado) → camada de contexto de 10/10 → decisão [ausente]. A #180 atualiza a matriz, sem constituir adoção automática do grafo (ficha Codex #106).

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/primary-public-selected.json issue[106] (corpo integral, entregas e regra que separa estudos de implementações); fontes/batch-revalidated-xldd-sources/local/REPORT.md (base 847d7a0f…, seções Modelo mínimo, Precedência e Validação executada), hash em fontes/batch-revalidated-xldd-sources/local-source-manifest.json; fontes/batch-revalidated-xldd-sources/selected-register-matrix.json X07.

### Classe e limite da evidência

FATO OBSERVADO: issue aberta e texto do estudo preservado com modelo, segurança e precedência. RELATO HISTÓRICO: validação offline de seis nós/cinco arestas. PROPOSTA: manifesto mínimo, sem nova dependência externa. DECISÃO PENDENTE: adoção; nenhuma execução.

### Fluxo

Fluxo proposto: fontes declaradas (CONTRACT, DDL, matriz) —(extração)→ manifesto do grafo versionado —(nós/arestas com basis/proof_state)→ consumidores #107 (MCP), #108 (Front), #109 (reconciliação). Nada implementado.

### Consequências e risco

Sem decisão, os três estudos descendentes (#107, #108, #109) ficam sem schema para implementar e tendem a divergir entre si; não há regressão de produto. Confiança alta no estado; o custo de esperar cresce à medida que os estudos envelhecem.

### Alternativas e recomendação

Recomendado: decidir adotar um schema mínimo (nós de lane/tabela/campo e arestas produz/consome) com estado de prova, e deixar extensões para depois. Alternativas: adiar (mantém estudos ativos sem implementação); usar só a matriz da #180 como fonte (mais simples, menos estruturado). Reversível antes de consumidores dependerem.

### Dependências e paralelismo

Decisão não depende de nada técnico. Estudos #107/#108/#109 correm em paralelo; implementações dependem desta decisão. A #180 pode alimentar o grafo, mas não precisa terminar antes da decisão.

### Plano e aceite propostos

Passos mínimos: (1) atualizar o exemplo do grafo para a main; (2) apresentar na #106 o schema mínimo; (3) decisão; (4) se adotado, validador e fixture aprovada como primeira entrega. Aceite: decisão registrada.

### Comunicação entre responsáveis

Para outro pod: "O grafo de sistema é a fonte que os estudos de UI, MCP e reconciliação precisam; a decisão de adotar um schema mínimo é o que destrava as implementações, não os estudos."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere tratar aresta derivada como prova runtime. Que caso o teste ainda não cobre? O schema histórico não cobre automaticamente a topologia da main atual. Como eu explicaria isso para outro pod? Explique basis, proof_state e decisão que bloqueia implementação, sem bloquear estudo.

### Próxima ação e encerramento

Próxima ação: mantenedor cross-pod (a confirmar) recebe o schema mínimo atualizado. Entrada: estudo de 29/08. Saída: decisão adotar/adiar/rejeitar na #106. Encerramento: decisão registrada.

<a id="item-244"></a>

## X08 — CI Integration — análise APEX em PR (#21)

Frente: produto_ci_integration. Encaminhamento: adiar_feature_ci_integration_separada_de_125.

### Identidade e estado

X08 é a feature cross-pod CI Integration — análise APEX em PR, #21, aberta na captura de 16/10, sem assignee; criada em 26/05 e atualizada em 13/07. Tem dois comentários com entregas parciais relatadas. Owner e prioridade a confirmar; distinta da governança do CI do próprio APEX (#125).

### Intenção e benefício

Problema: hoje o APEX diagnostica runs depois que acontecem; a feature proporia comentar anti-padrões Spark numa PR antes do merge. Público: times que revisam código Spark. Ganho: feedback preventivo no fluxo de revisão.

### Feito, faltante e não comprovado

Feito segundo comentários de 08/06 e 13/07: primeiro scenario-gate, correções de filtro world e fetch_real_log/oracle-weekly (commit relatado 0ddb550), e execução local Task Scheduler verde com LastTaskResult=0. O comentário de junho explicita que isso ainda não implementa comentário automático em PR. Esses relatos não foram reproduzidos nem seus commits lidos. Falta reconciliar esse trabalho parcial com o objetivo GitHub Actions/Azure DevOps e definir menor escopo de análise em PR.

### Linhagem

Linhagem: #21 criada em 26/05 → comentário 4648526848 (08/06: primeiro gate, sem análise completa) → comentário 4963665268 (13/07: correções/Task Scheduler, pendências de runner/secrets) → registro X08 recomenda defer e distingue #125 → decisão posterior de prioridade não localizada. A data 13/07 é updated_at, não a abertura.

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/primary-public-selected.json issue[21] e comentários 4648526848/4963665268 (gustocezar); fontes/batch-revalidated-xldd-sources/selected-register-matrix.json X08. O corpo pede execução do Recommendation Engine sobre diff e comentário pré-merge; comentários são evidência primária do relato histórico, sem prova técnica atual independente.

### Classe e limite da evidência

FATO OBSERVADO: issue aberta com dois comentários e escopo de produto. RELATO HISTÓRICO: primeiro gate, bugs corrigidos e execução Task Scheduler. NÃO VERIFICADO: diffs/commits e execução atual; não declarar “nada feito”. PROPOSTA/DECISÃO PENDENTE: prioridade e desenho mínimo.

### Fluxo

Fluxo proposto (conceitual): PR de código Spark —(diff e, se houver, plano)→ ação de CI com APEX —(análise estática de anti-padrões)→ comentário na PR —(revisor humano decide)→ merge. Não implementado.

### Consequências e risco

Sem ação, a feature de comentário automático continua sem entrega demonstrada neste recorte; os gates parciais relatados não equivalem ao produto completo. G01/G02 não são bloqueios técnicos para discutir prioridade ou fazer desenho. A disponibilidade operacional futura depende do ambiente escolhido.

### Alternativas e recomendação

Recomendado: manter adiado com motivo explícito até a v1 estabilizar o diagnóstico pós-run. Alternativas: protótipo como GitHub Action fora do repositório principal; rejeitar se o produto for focado em runtime. Reversível.

### Dependências e paralelismo

Não depende de #125 nem de #130 para decidir. Uma implementação futura dependeria de capacidade de runner e de um modo de análise sem runtime.

### Plano e aceite propostos

Condição de não ação: sem decisão de prioridade, manter a #21 aberta e adiada. Se priorizada: escopo mínimo (anti-padrões detectáveis só pelo diff) e protótipo isolado.

### Comunicação entre responsáveis

Para outro pod: “A #21 já tem relatos de gates e automação parcial, mas eles não implementam sozinhos análise de diff e comentário automático. Vamos reconciliar esse legado antes de decidir a próxima fatia.”

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere ignorar os gates parciais relatados antes de desenhar a feature. Que caso o teste ainda não cobre? Task Scheduler relatado não cobre comentário automático num diff de PR. Como eu explicaria isso para outro pod? Explique a diferença entre integração de produto e proteção do CI do APEX.

### Próxima ação e encerramento

Próxima ação: mantenedor (a confirmar) decide prioridade. Entrada: #21. Saída: decisão registrada. Encerramento: prioridade definida ou adiamento com motivo.

<a id="item-245"></a>

## X09 — Registro canônico de oportunidades

Frente: governanca_registro. Encaminhamento: externo_processo_visao_atual_datada.

### Identidade e estado

X09 é o processo de governança "Registro canônico de oportunidades", fora do repositório APEX. Objeto: OPPORTUNITY-REGISTER.csv em [caminho local omitido] cujo sha256 33d13c25… é idêntico ao da cópia em _build/inputs da Parte03 (conferido em 18/10). Responsável registrado: Augusto. Sem objeto público.

### Intenção e benefício

Problema: listas dispersas (seed, R2, 31/08, STATE, backlogs) geravam duplicidade e perda de rastreio. Público: quem planeja e audita o backlog. Ganho: uma matriz com ID estável, da qual a triagem (MATRIX.json) e a publicação derivam.

### Feito, faltante e não comprovado

Feito: registro com 158 IDs no corte de 2026-10-01; MATRIX.json reproduz 158 historical_record iguais às linhas do CSV (C04-09) e acrescenta representações públicas; PUBLICATION.json registra as publicações de 11/10. Falta: decisão do usuário de adotar o registro como canônico de forma explícita e, se necessário, aceite formal da ferramenta TS02 (que existe só como unidade proposta). Não comprovado: CI ou publicação da ferramenta.

### Linhagem

Linhagem: seed X09 → registro em 23/09 → reconciliações de 29/09 e 30/09 (151 → 152 IDs) → corte de 01/10 com 158 IDs → triagem de 11/10 (MATRIX/PUBLICATION) → Parte03 usa a cópia (33d13c25) → visão atual datada [ausente como artefato separado]. Elo ausente: Task-Spec assinada da TS02.

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/local-readonly-receipt.json x09 (CSV da custódia e cópia Parte03: sha256 33d13c252dca2df5bd27fe45127c492ee1f004a112af416b0e4c936eef65d686, 158 linhas); fontes/batch-revalidated-xldd-sources/selected-register-matrix.json X09; fontes/batch-revalidated-xldd-sources/publication-subset.json e MATRIX original da Parte03. Aceite/39 testes TS02 são relatos do registro; não foram executados.

### Classe e limite da evidência

FATO OBSERVADO: igualdade de hash e contagem de 158 IDs. RELATO: validações e 39 testes da ferramenta TS02. DECISÃO PENDENTE: adoção formal. Sem execução.

### Fluxo

Fluxo observado: OPPORTUNITY-REGISTER.csv (histórico, corte 01/10) —(triagem 11/10)→ MATRIX.json com representações públicas —(publicação)→ PUBLICATION.json e issues #165-#180 —(auditorias)→ Parte03/Parte04. O registro não é reescrito; o estado atual vive nas camadas derivadas.

### Consequências e risco

Sem ação, o registro continua útil como origem histórica; o risco é alguém ler um campo de 01/10 como estado atual (exemplos nesta revisão: E03, S15). Confiança alta.

### Alternativas e recomendação

Recomendado: manter o CSV congelado e publicar, ao lado, uma visão atual datada (SHA da main e horário) gerada da MATRIX e das revisões; não sobrescrever campos históricos. Alternativas: atualizar o CSV in place (perde a história); abandonar o CSV pela MATRIX (perde a origem humana). Reversível.

### Dependências e paralelismo

Não depende do repositório APEX nem de CI. Depende de decisão do usuário sobre o papel do registro. A visão atual datada pode ser produzida em paralelo às revisões em curso, consumindo as fichas à medida que forem revistas.

### Plano e aceite propostos

Passos mínimos: (1) usuário confirma o registro como canônico; (2) gerar visão atual datada com ponteiros para fichas revistas; (3) se aceite formal for desejado, folha prospectiva para a ferramenta TS02 no HEAD atual. Aceite: visão atual separada com data e SHA; CSV intacto.

### Comunicação entre responsáveis

Para outro pod: "O registro de oportunidades é histórico por desenho; o estado atual de cada ID está nas revisões datadas. Não leia o CSV como status de hoje."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere sobrescrever o CSV histórico ao atualizar o estado público. Que caso o teste ainda não cobre? O hash não comprova o comportamento da ferramenta TS02. Como eu explicaria isso para outro pod? Explique registro, triagem e publicação como camadas datadas.

### Próxima ação e encerramento

Próxima ação: usuário (Augusto, a confirmar) decide adoção e formato da visão atual. Entrada: CSV 33d13c25 e MATRIX. Saída: visão atual datada. Encerramento: visão publicada localmente e registro preservado.

<a id="item-246"></a>

## X10 — Custódia da rodada 2026-09-21 e dos pacotes locais

Frente: governanca_custodia. Encaminhamento: encerrar_sem_acao_com_manifesto_defasado_registrado.

### Identidade e estado

X10 é preservação: custódia da rodada de 2026-09-21 e dos pacotes locais, fora do repositório APEX. Objeto: [caminho local omitido] (repositório Git local, branch main, HEAD 854d629 de 2026-10-01). Registro: DEC-18 concluída, sem ação. Responsável: Augusto (a confirmar).

### Intenção e benefício

Intenção: evitar perder os 126 arquivos da rodada de 21/09, a reconciliação, a cadeia do monitor, o snapshot do STATE e o bundle Ask V2 sanitizado, mantendo-os fora do iCloud. Público: quem audita o histórico. Ganho: custódia independente e verificável por hash.

### Feito, faltante e não comprovado

Conferência independente em 18/10: HEAD da custódia 854d629…, metadata declara origem c3c4119 e contains_original_ask_v2_proof_secrets=false. Das 590 entradas do SHA256SUMS: 513 iguais, 20 diferentes e 57 ausentes; as 57 ausentes resolvem como objetos em HEAD. Git status mostra modificações, 57 deleções do diretório do monitor e vários não rastreados, incluindo tar do monitor. Não foi aberto o tar; diferenças de hash não demonstram nem corrupção nem alteração intencional.

### Linhagem

Linhagem: rodada de 21/09 → custódia criada em 24-25/09 (DEC-18) → commits até 01/10 → registro X10 "sem ação" (corte de 01/10) → verificação de 18/10 com manifesto defasado e arquivamento local não commitado. Elo ausente: registro do arquivamento do monitor.

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/local-readonly-receipt.json custody (hashes, status e 57 objetos recuperáveis em HEAD); fontes/batch-revalidated-xldd-sources/local/CUSTODY-METADATA.json e fontes/batch-revalidated-xldd-sources/local-source-manifest.json; fontes/batch-revalidated-xldd-sources/selected-register-matrix.json X10. O manifesto e a ref são independentes; não certificam todas as cópias/arquivos fora deles.

### Classe e limite da evidência

FATO OBSERVADO: contagens de hash, status Git, metadata e recuperabilidade das 57 entradas em HEAD. RELATO HISTÓRICO: 15/15, 111/111 e snapshot 294 do registro. NÃO VERIFICADO: motivo das mudanças, conteúdo/integridade do tar e intenção do dono. Mismatch não é diagnóstico de corrupção, nem prova automática de atualização legítima.

### Fluxo

Fluxo observado: custódia local —(manifesto de versão anterior)→ comparação dos bytes atuais → divergências. Git HEAD —(objetos das 57 entradas ausentes resolvem)→ possibilidade de recuperação. Tar não rastreado —(conteúdo não inspecionado)→ nenhuma conclusão de equivalência.

### Consequências e risco

Sem nota de reconciliação, alguém pode confundir manifesto defasado com dano ou limpar arquivos não rastreados sem preservá-los. Os números não provam perda nem integridade integral da custódia. Confiança alta nas observações, motivo das mudanças indeterminado.

### Alternativas e recomendação

Recomendado: preservar o estado e acrescentar nota datada de divergências, mantendo X10 como preservação histórica concluída e follow-up explícito de custódia. O dono decide verificar o tar, comparar com as entradas antigas e renovar manifesto/commit ou restaurar. Não regenerar hashes silenciosamente para apagar diferenças.

### Dependências e paralelismo

Não depende de nada para permanecer encerrado. Relaciona-se a X11 (o bundle Ask V2 sanitizado está dentro da custódia) e a X17 (motivo de manter a custódia fora do iCloud); nenhum deles é gate.

### Plano e aceite propostos

Condição de não ação nesta revisão: nenhuma escrita na custódia. Passo mínimo para o dono: decidir entre commitar o arquivamento e regenerar o manifesto, ou restaurar a pasta. Reabrir X10 se algum arquivo do HEAD ficar irrecuperável.

### Comunicação entre responsáveis

Para outro pod: “O manifesto tem 513 correspondências, 20 diferenças e 57 ausências no working tree; as 57 resolvem em HEAD. Ainda precisamos explicar as diferenças e verificar o tar. Esses números sozinhos não certificam corrupção nem integridade total.”

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere renovar hashes sem explicar as divergências existentes. Que caso o teste ainda não cobre? A conferência de bytes não cobre equivalência do tar não aberto. Como eu explicaria isso para outro pod? Explique mismatch, recuperabilidade em HEAD e integridade como alegações diferentes.

### Próxima ação e encerramento

Próxima ação: dono da custódia (Augusto, a confirmar) decide sobre o arquivamento e o manifesto. Entrada: números desta ficha. Saída: commit do arquivamento com manifesto novo, ou nota explicando a defasagem. Encerramento: X10 permanece encerrado; nota registrada.

<a id="item-247"></a>

## X11 — Candidato Ask V2 preservado localmente e em conflito com #129

Frente: arquitetura_ask_http. Encaminhamento: agrupar_em_122_preservado_sem_publicar.

### Identidade e estado

X11 é preservação/decisão cross-pod: o candidato Ask V2 preservado localmente e em conflito com a #129. Commits locais em [caminho local omitido] c73269f (2026-09-23T23:58:37-03:00, "chore: preserve Ask V2 candidate snapshot") e 9e68c10 (2026-09-24T09:32:22-03:00, "chore: preserve sanitized Ask V2 candidate"), ambos conferidos nesta revisão. Destino: decisão da #122 (X01). Responsável registrado: Augusto.

### Intenção e benefício

Problema: o candidato tinha 23 arquivos modificados, 2 removidos e 44 não rastreados e remove front/nginx.conf, que a #129 altera; sem preservação, o trabalho se perderia; publicado sem decisão, conflitaria com a /v1. Público: quem decidir o Ask. Ganho: trabalho preservado e disponível para a decisão, sem risco de publicar segredos.

### Feito, faltante e não comprovado

Feito: preservação concluída (DEC-17); segundo o registro, 504/504 arquivos iguais ao manifesto 1ea44e21 e o snapshot sanitizado 9e68c10 não tem c73269f na ancestralidade. Falta: destino definido pela #122. Não comprovado nesta revisão: o manifesto 504/504 (não reexecutei).

### Linhagem

Linhagem: ondas Ask de setembro → inventário ask-v2 → snapshot c73269f com segredos de prova → sanitização 9e68c10 (tree 7828936) → bundles locais verificados (relato) → custódia em apex-custody-20260924 → decisão #122 [ausente].

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/local-readonly-receipt.json x11, git log dos commits c73269f770a3e561aa1d3d23eb30371eaf51243c e 9e68c101da47559e400d5d54dfbfd6c3353eb712, sem ler as árvores; fontes/batch-revalidated-xldd-sources/selected-register-matrix.json X11 (504/504 e ausência de ancestralidade como relato); fontes/batch-revalidated-xldd-sources/primary-public-selected.json issue[122] e pull[129].

### Classe e limite da evidência

FATO OBSERVADO: os dois commits existem no clone local com as datas acima. RELATO: integridade 504/504 e sanitização. DECISÃO PENDENTE: X01/DEC-07. Sem execução.

### Fluxo

Fluxo de preservação: working tree Ask V2 —(commit c73269f, com segredos de prova)→ evidência local nunca publicável —(sanitização)→ 9e68c10 —(bundle e custódia)→ disponível para a decisão #122 —(se proceed)→ reconciliação com a /v1 antes de qualquer PR.

### Consequências e risco

Sem decisão, o candidato envelhece frente à main e a reconciliação fica mais cara; o risco de publicar o snapshot com segredos é o maior e está mitigado pela regra de usar só 9e68c10. Confiança alta.

### Alternativas e recomendação

Recomendado: manter preservado e sem publicação até a #122 decidir; se proceed, extrair do 9e68c10 apenas o que não duplica a /v1. Alternativas: descartar após decisão defer/reject (registrar o descarte); reimplementar sobre a /v1 sem o candidato. Reversível enquanto preservado.

### Dependências e paralelismo

O destino de implementação/publicação depende da decisão X01/#122; preservação e inventário sanitizado podem ser discutidos sem fechar a arquitetura. A custódia X10 não é gate dessa discussão. Não há autorização de publicar o candidato nesta auditoria.

### Plano e aceite propostos

Nesta revisão, catalogar commits e limites sem abrir os bytes sensíveis. Se houver proceed futuro, avaliar só a variante sanitizada 9e68c10, confirmar sua sanitização/proveniência e planejar reconciliação sobre a /v1 antes de qualquer publicação autorizada.

### Comunicação entre responsáveis

Para outro pod: "Existe um candidato Ask V2 local, sanitizado em 9e68c10; ele conflita com a #129 e só deve ser usado depois da decisão da #122. A versão original c73269f nunca deve ser publicada."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere usar a árvore original com segredos numa publicação. Que caso o teste ainda não cobre? A existência dos commits não revalida sanitização nem os 504 arquivos. Como eu explicaria isso para outro pod? Explique preservação, decisão e publicação como autorizações diferentes.

### Próxima ação e encerramento

Próxima ação: aguardar X01; nenhuma ação até lá. Owner: Augusto (a confirmar). Entrada: decisão da #122. Saída: destino do candidato (reconciliar ou descartar). Encerramento: destino registrado.

<a id="item-248"></a>

## X12 — Inventário de branches remotas além das cinco da #105

Frente: governanca_branches. Encaminhamento: agrupar_em_105_inventario_com_dados_atuais.

### Identidade e estado

X12 é um estudo de governança: inventário das branches remotas além das cinco arquivadas pela issue luanmorenommaciel/apex#105 "[Governance] Archive historical contribution branches before deletion" (aberta, sem assignee). Escopo agrupado na #105, sem issue duplicada. Owner: custodiante (a confirmar).

### Intenção e benefício

Problema: o repositório tem muitas branches históricas (o registro contou 57) e a custódia da #105 cobre só cinco; excluir branches sem inventário pode perder contribuições não arquivadas. Público: mantenedor e custodiante. Ganho: escopo de custódia completo antes de qualquer limpeza.

### Feito, faltante e não comprovado

Dados atuais (GET de 18/10, sem paginação adicional): 85 branches públicas, nenhuma protegida pela API; prefixos mais comuns codex/ (40), gustocezar/ (7), candidate/ (6), serve/ (6). As quatro branches APEX do bundle da #105 (gustocezar/feature/*-desacoplamento-geradores) existem com heads idênticos aos SHAs arquivados (bd8a08b, 48c7ef9, 8bd5672, 116be23); a quinta é do workspace. As citadas pelo registro existem: base-project-e2e-augusto (3d4b05b), feat/base-project-e2e (ada98d1), jayme/feature/cleanup-project-e2e (535e237), fix/e2e-canonical-exec-bit (faf0e70). Falta: classificação por branch (PR associada, integrada, histórica, órfã).

### Linhagem

Linhagem: descoberta da auditoria de setembro (57 branches) → registro X12 → triagem agrupa na #105 → bundle das cinco restaurado pelo Codex em 17/10 (C04-19) → GET de 18/10 com 85 branches → classificação [ausente] → decisão de escopo [ausente].

### Fontes e corte

Fontes: fontes/batch-claude-registro-propostas-sources/claude/fontes/publico-20261018/branches-p1.json (85 entradas; captured_at.txt registra janela de captura 18/10); fontes/batch-revalidated-xldd-sources/primary-public-selected.json issue[105] (cinco heads originais e repetição da consulta PR antes de exclusão); fontes/batch-custody-sources/BRANCH-TO-SHA.tsv; fontes/batch-revalidated-xldd-sources/selected-register-matrix.json X12. Listagem de branches não revalida rulesets.

### Classe e limite da evidência

FATO OBSERVADO: 85 entradas na captura de 18/10, protected=false em cada uma e quatro heads APEX iguais aos listados na #105. RELATO HISTÓRICO: 57 branches no registro e restauração anterior do bundle. NÃO VERIFICADO: causa da diferença de contagem, PRs por branch e rulesets. DECISÃO PENDENTE: escopo de arquivo e eventual exclusão.

### Fluxo

Fluxo proposto: lista de branches —(cruzamento com PRs: integrada, aberta, fechada sem merge, sem PR)→ classificação —(branches sem merge e sem PR)→ candidatas a arquivo —(bundle + verificação)→ decisão de exclusão separada.

### Consequências e risco

Sem classificação, uma limpeza futura pode remover o único ref conhecido de algum commit ainda não preservado. A captura é datada e não é consulta remota atual para autorizar exclusão. Não há medição de probabilidade nem exclusão nesta revisão.

### Alternativas e recomendação

Recomendado: classificar as 85 branches cruzando com o estado das PRs e arquivar só as que têm commits fora da main e sem PR integrada. Alternativas: arquivar todas (simples, bundle maior); não arquivar e nunca excluir (custo zero, poluição permanente). Exclusão é decisão separada e exige consulta remota atual.

### Dependências e paralelismo

Não depende de nada técnico. Relaciona-se a X06/#105 (custódia das cinco branches, já verificada pelo Codex em 17/10) e pode correr em paralelo; a exclusão de branches é decisão posterior e separada.

### Plano e aceite propostos

Passos mínimos: (1) tabela branch → head → PR associada → merge → commits fora da main; (2) escopo proposto do arquivo; (3) bundle e verificação para as escolhidas; (4) decisão de exclusão em etapa separada. Aceite: lista com decisão por branch.

### Comunicação entre responsáveis

Para outro pod: “A captura de 18/10 contém 85 branches; as quatro heads APEX do arquivo histórico coincidem. A diferença para as 57 históricas precisa de classificação por branch, sem inferir a causa nem apagar nada.”

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere apagar branch apenas porque uma PR está integrada. Que caso o teste ainda não cobre? A captura de branches não cobre commits únicos, PRs atuais e rulesets. Como eu explicaria isso para outro pod? Explique arquivo recuperável antes de eventual exclusão separada.

### Próxima ação e encerramento

Próxima ação: custodiante (a confirmar) produz a tabela de classificação. Entrada: @PUB/branches-p1.json e lista de PRs. Saída: tabela com proposta de escopo na #105. Encerramento: decisão por branch registrada.

<a id="item-249"></a>

## X13 — Reconciliar texto do CONTRACT.md e marcadores PROPOSED

Frente: contrato_documentacao. Encaminhamento: agrupar_em_165_decidir_redacao_com_guarda.

### Identidade e estado

X13 é uma decisão contratual cross-pod: reconciliar o texto do CONTRACT.md e os marcadores PROPOSED de schema SQL. Publicada da minuta PROP-X13-CONTRACT-RECONCILIATION como issue luanmorenommaciel/apex#165 em 2026-10-11 por gustocezar, aberta, assignee gustocezar (reserva de estudo), um comentário. Decisão: mantenedor do contrato (DEC-14), a confirmar.

### Intenção e benefício

Problema: o texto normativo e os cabeçalhos de DDL descrevem estados diferentes — job_conf.ddl.sql diz "PROPOSED v0.4 (awaiting central ratification)", memory/sql/030 e 031 dizem "PROPOSED, not ratified", enquanto o CONTRACT.md lista v0.4 no changelog e o comentário da #165 cita infra/sql/030 como RATIFIED. Público: colaboradores novos que leem contrato e DDL. Ganho: documentação coerente sem mudar semântica de telemetria.

### Feito, faltante e não comprovado

Base: CONTRACT.md:30 (job_conf emitido no primeiro onJobStart) e CONTRACT.md:128 ("Stage linkage … execution_id→job→stage map … a later enhancement") são pendências distintas; a premissa do registro ("CONTRACT.md:117 descreve rota onJobStart para stage linkage") estava deslocada e misturava as duas, e o estudo da #165 confirma essa distinção. tests/test_telemetry_compatibility_matrix.py:145-147 exige literalmente "PROPOSED v0.4" e "PROPOSED, not ratified" (C04-16): mudar os cabeçalhos sem ajustar a guarda faria o teste falhar. Falta: decisão de redação e PR documental coordenada com a guarda.

### Linhagem

Linhagem: drifts textuais da matriz de compatibilidade → PR #132 deixa CONTRACT.md de fora → registro X13 (DEC-14) → minuta PROP-X13 (Gemini) com premissa onJobStart/stage linkage → publicação #165 com texto reenquadrado → estudo Kimi: inventário e quatro cláusulas antes/depois, revistas pelo Codex (11/10) → decisão [ausente] → PR [ausente].

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/primary-public-selected.json issue[165] e comentário 6109741950 (estudo e quatro propostas relatadas); fontes/batch-revalidated-xldd-sources/code/CONTRACT.md:11-30,128; fontes/batch-revalidated-xldd-sources/code/contract__job_conf.ddl.sql:1; fontes/batch-revalidated-xldd-sources/code/memory__sql__030_plan_memory.sql:1-4; fontes/batch-revalidated-xldd-sources/code/memory__sql__031_run_outcomes.sql:1-3; fontes/batch-revalidated-xldd-sources/code/infra__sql__030_plan_memory.sql:1-4; fontes/batch-revalidated-xldd-sources/code/tests__test_telemetry_compatibility_matrix.py:145-147; fontes/batch-revalidated-xldd-sources/selected-register-matrix.json X13 e fontes/batch-revalidated-xldd-sources/publication-subset.json.

### Classe e limite da evidência

FATO OBSERVADO: textos PROPOSED/RATIFIED em espelhos distintos, emissão de job_conf e linkage futuro como cláusulas diferentes, guarda literal. RELATO HISTÓRICO: quatro alternativas antes/depois do estudo. DECISÃO PENDENTE: redação e fonte de ratificação; implementação não ratifica o contrato por si.

### Fluxo

Fluxo documental: decisão do mantenedor —(texto aprovado)→ CONTRACT.md e cabeçalhos SQL —(mesmos marcadores)→ teste de matriz —(asserções atualizadas na mesma PR)→ verde. Sem a coordenação: cabeçalho muda —(asserção literal antiga)→ teste vermelho.

### Consequências e risco

Sem ação, colaboradores continuam lendo "não ratificado" para tabelas que o contrato já lista, e podem hesitar em depender delas; não há efeito de runtime. Confiança alta.

### Alternativas e recomendação

Recomendado: PR documental única que (a) mantém a distinção 30/128, (b) muda os cabeçalhos só com a fonte da ratificação citada, e (c) atualiza as asserções do teste de matriz para o novo texto. Alternativas: manter PROPOSED até a próxima versão do contrato (a minuta oferecia isso); mudar só o CONTRACT.md. Reversível.

### Dependências e paralelismo

Não depende de #180 inteira (C04-16); depende da decisão do mantenedor e da fonte de ratificação. Coordena com a guarda e, se tocar texto de executor_run_time_ms, com #179/CL-02.

### Plano e aceite propostos

Passos mínimos: (1) decisão de redação a partir das quatro cláusulas; (2) PR com CONTRACT.md, três cabeçalhos e o teste de matriz; (3) controle: teste de matriz verde com os novos literais; (4) nota de linhagem citando a decisão. Aceite: zero marcadores contraditórios e guarda coerente.

### Comunicação entre responsáveis

Para outro pod: "Os cabeçalhos dizem 'não ratificado' para tabelas que o contrato já lista. A correção é só de texto, mas um teste confere essas frases literalmente e precisa mudar na mesma PR."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere mudar PROPOSED sem fonte de ratificação e sem a guarda literal. Que caso o teste ainda não cobre? O teste textual não comprova schema aplicado no runtime. Como eu explicaria isso para outro pod? Explique emissão job_conf e mapa execution→job→stage como cláusulas distintas.

### Próxima ação e encerramento

Próxima ação: mantenedor do contrato (a confirmar) escolhe a redação na #165. Entrada: quatro cláusulas do estudo e esta ficha. Saída: PR documental coordenada. Encerramento: PR integrada e critérios da #165 marcados.

<a id="item-250"></a>

## X14 — Colisão de numeração de ADR + índice/glossário (resto de T25)

Frente: documentacao_adr. Encaminhamento: encerrar_pr_integrada_sem_renumerar.

### Identidade e estado

X14 é documentação de governança (resto de T25): colisão de numeração de ADR e índice/glossário. Implementado pela PR luanmorenommaciel/apex#141 "docs: add a discoverable index of canonical architecture decisions" (head 185a67b, commits 337d5d5 índice e 185a67b link no README), integrada em 2026-10-06T20:20:34Z no merge a922a0e. Sem assignee.

### Intenção e benefício

Problema: ADR-003 significava AQE na main e Ask-HTTP-BFF num candidato; ADR-004 era a PR #133, o candidato Ask V2 e um plano do workspace; issues antigas #8 e #22-#24 usavam ADR-00x com outro sentido. Público: quem segue referências a ADRs. Ganho: referências inequívocas pelo caminho do documento.

### Feito, faltante e não comprovado

Base: docs/architecture/ADR-INDEX.md lista ADR-001 a ADR-004 com status e caminho canônico e declara que "não renumera, renomeia, reescreve nem substitui ADRs" e que materiais históricos podem reutilizar identificadores. Falta neste ID: nada; renumeração foi deliberadamente não feita (DEC-11). Não comprovado: CI (irrelevante para links estáticos, segundo o registro).

### Linhagem

Linhagem: R2 T25 e inventário ask-v2 → commit 337d5d5 na branch codex/adr-index-main → PR #141 (28/09) com 185a67b → folha do link aceita em Task-Spec Tier 1 (lote 3, relato) → conflito textual com #127 no README resolvido → merge a922a0e em 06/10.

### Fontes e corte

Fontes: fontes/batch-revalidated-xldd-sources/primary-public-selected.json pull[141] (merge a922a0e95517383b663ac526746d13f379b982d9, 06/10; validações do autor relatadas); fontes/batch-revalidated-xldd-sources/code/docs__architecture__ADR-INDEX.md (quatro linhas e regra de caminho/contexto); fontes/batch-revalidated-xldd-sources/selected-register-matrix.json X14.

### Classe e limite da evidência

FATO OBSERVADO: índice na main com regra de não renumerar. RELATO: evals, Exit Check e aceite Tier 1 da folha do link. Sem CI necessária para o escopo.

### Fluxo

Fluxo documental: menção histórica "ADR-004" —(contexto do arquivo citado)→ leitor —(dúvida)→ ADR-INDEX —(caminho canônico)→ documento certo. O índice resolve por caminho, não por número.

### Consequências e risco

Sem ação, nada regride. O risco residual é alguém criar um ADR-005 sem atualizar o índice, ou citar um número antigo sem caminho; é risco de processo, não defeito do índice. Confiança alta.

### Alternativas e recomendação

Recomendado: manter X14 entregue e usar caminho/contexto para referências históricas. Atualizar o índice junto de futuros ADRs, com conferência de links proporcional à alteração documental. Não há necessidade de inventar novo teste automatizado para encerrar este ID.

### Dependências e paralelismo

Nenhuma dependência para encerrar. A ratificação do ADR-004 (P07) é independente do índice, e uma eventual guarda automatizada do índice também não depende de outras issues.

### Plano e aceite propostos

Condição de não ação: catalogar a entrega e preservar sua linhagem. Reabrir se surgir omissão ou alvo quebrado confirmado; uma guarda automatizada futura é decisão separada, não critério novo deste encerramento.

### Comunicação entre responsáveis

Para outro pod: "Use o ADR-INDEX para saber qual documento é o ADR canônico; números antigos em issues e candidatos podem ter outro sentido."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere identificar ADR somente pelo número histórico. Que caso o teste ainda não cobre? A validação relatada de links não cobre ADRs adicionados no futuro. Como eu explicaria isso para outro pod? Explique caminho canônico sem renumerar a história.

### Próxima ação e encerramento

Próxima ação: confirmar encerramento de X14. Owner: nenhum necessário. Entrada: ADR-INDEX na base. Saída: linha X14 "entregue em a922a0e". Encerramento: imediato.

