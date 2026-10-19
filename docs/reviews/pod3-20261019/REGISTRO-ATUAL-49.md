# Registro atualizado — 49 objetos públicos

São 12 PRs e 37 issues abertas no corte Parte08 de 19/10. O universo original continua 525 IDs; estes 49 objetos não são mais 49 IDs inéditos. Os 48 anteriores conservam seus campos históricos e limites. Os heads/estado foram comparados à recaptura; os checks/reviews das 11 PRs anteriores não foram reconsultados nesta rodada. A #185 tem quatro checks e zero reviews no novo recibo.

A classe é do próximo passo: 32 ready_offline, 17 owner_decision, zero runtime_blocked imediato. Isso **não elimina runtime**: #172a prepara o protocolo e #172b continua dependente de ambiente. Os dois rótulos são subpassos locais da mesma issue #172.

## issue #21 — [FEATURE] CI Integration (pre-merge code review)

- Fonte: https://github.com/luanmorenommaciel/apex/issues/21
- Próximo passo (owner_decision): Mantenedor/owner de produto a confirmar: decidir piloto/adiar/rejeitar e registrar escopo. A issue não está encerrada pelo cenário histórico nem automaticamente adiada nesta auditoria.
- Dependência: Definir objeto analisado, permissões e dono precede implementação. #125/#130 afetam operação futura conforme plataforma, mas não são gates para estudo. Maturidade do Serve só é dependência se a solução escolhida o usar.
- Prova/limite: DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Esta rodada não acrescenta execução de produto; considerar apenas a leitura estática e os recibos específicos deste objeto.

## issue #33 — [Governance] Add SECURITY.md (LICENSE + NOTICE done)

- Fonte: https://github.com/luanmorenommaciel/apex/issues/33
- Próximo passo (ready_offline): Mantenedor/admin a confirmar: escolher canal e responsáveis; próxima entrega é texto revisável. Encerrar quando política e canal estiverem coerentes e integrados, sem contato externo nesta auditoria.
- Dependência: Mantenedor define canal, responsáveis e suporte. Desenho de #42 pode ocorrer em paralelo; disclosure não é predecessor técnico universal de qualquer estudo on-prem.
- Prova/limite: DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Esta rodada não acrescenta execução de produto; considerar apenas a leitura estática e os recibos específicos deste objeto.

## issue #42 — [SPIKE] Definir modo offline/on-prem seguro para agentes Apex

- Fonte: https://github.com/luanmorenommaciel/apex/issues/42
- Próximo passo (ready_offline): Owner produto/segurança a confirmar: decidir prioridade e produzir matriz pequena. Não encerrar por zero comentários nem exigir #33 decidida para iniciar a análise.
- Dependência: Requisitos de #2/#5 e política #33 informam o desenho. O estudo pode começar enquanto canal de disclosure é decidido; implantação exige contrato de operação próprio.
- Prova/limite: DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Esta rodada não acrescenta execução de produto; considerar apenas a leitura estática e os recibos específicos deste objeto.

## issue #105 — [Governance] Archive historical contribution branches before deletion

- Fonte: https://github.com/luanmorenommaciel/apex/issues/105
- Próximo passo (ready_offline): Custodiante/mantenedor a confirmar: registrar custódia e reconciliar #105 quando autorizado. A criação/restauração já está demonstrada; eventual exclusão/publicação precisa de decisão e evidência novas, fora desta revisão.
- Dependência: Arquivo é predecessor estrito de exclusão, já existe para as cinco identidades. Inventário X12 pode informar limpeza mais ampla, mas não é necessário para reconhecer este arquivo. Verificação remota/decisão de exclusão continuam separadas.
- Prova/limite: DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Na #105 há verificação própria de arquivo Git, sem executar código de produto; demais execuções não foram realizadas.

## issue #106 — [ADR/Study] Evaluate a read-only APEX system and contract graph

- Fonte: https://github.com/luanmorenommaciel/apex/issues/106
- Próximo passo (owner_decision): Mantenedor cross-pod a confirmar: revisar exemplo e decidir adotar/adiar/rejeitar. Encerrar estudo com decisão; não declarar implementação nem adiamento já aprovados.
- Dependência: A semente #103 já tem entrega histórica; #180 pode atualizar conteúdo. Estudos #107–109 podem ocorrer em paralelo. Implementação depende do schema; não impor esperar toda v1 para estudar.
- Prova/limite: DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Esta rodada não acrescenta execução de produto; considerar apenas a leitura estática e os recibos específicos deste objeto.

## issue #107 — [Study][Pod 3 / Serve] Define a read-only APEX system-graph MCP interface

- Fonte: https://github.com/luanmorenommaciel/apex/issues/107
- Próximo passo (ready_offline): Owner Serve a confirmar: preparar proposta em paralelo ao schema; implementar somente após ratificação. Encerrar estudo por decisão fundamentada, não por comentário de espera apenas.
- Dependência: Implementação aguarda schema aprovado de #106; desenho e exemplos podem informar essa decisão agora. Não há dependência de iniciar ClickHouse para o estudo.
- Prova/limite: DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Esta rodada não acrescenta execução de produto; considerar apenas a leitura estática e os recibos específicos deste objeto.

## issue #108 — [Study][Pod 1 / Front-End] Explore topology and evidence-provenance views

- Fonte: https://github.com/luanmorenommaciel/apex/issues/108
- Próximo passo (ready_offline): Owner Front a confirmar: escolher view e fonte em coordenação com #106. Não aguardar toda v1 para estudar nem declarar UI pronta por existir matriz.
- Dependência: Implementação depende da decisão de schema #106; estudos podem ser paralelos. Ownership de loading segue fronteira browser/serviço; #107 é opcional.
- Prova/limite: DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Esta rodada não acrescenta execução de produto; considerar apenas a leitura estática e os recibos específicos deste objeto.

## issue #109 — [Study][Pod 2 / Infra] Define declared-contract versus runtime reconciliation

- Fonte: https://github.com/luanmorenommaciel/apex/issues/109
- Próximo passo (ready_offline): Owners Infra/Engine a confirmar: produzir plano revisável e decidir o recorte. Runtime permanece fora desta revisão; não manter o estudo parado por gates globais não exigidos.
- Dependência: Schema #106 governa implementação do descendente; design é ready_offline pelo corpo. Política #170 informa possíveis probes sob ingestão, sem bloquear toda especificação.
- Prova/limite: DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Esta rodada não acrescenta execução de produto; considerar apenas a leitura estática e os recibos específicos deste objeto.

## issue #112 — [Study][Cross-lane] Define versioned deterministic runbooks and negative baselines

- Fonte: https://github.com/luanmorenommaciel/apex/issues/112
- Próximo passo (ready_offline): Owner Serve/Memory/Verify a confirmar: revisar arquivos e decidir adoção. Encerrar estudo com decisão e limites; implementação/validação ficam em folha específica se aprovadas.
- Dependência: Owner/consumidor e política de versão condicionam adoção. O estudo não depende de publicar #167/#174; usa esse candidato como exemplo, não como implementação de runbook.
- Prova/limite: DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Esta rodada não acrescenta execução de produto; considerar apenas a leitura estática e os recibos específicos deste objeto.

## issue #113 — [Harness] Ratify a versioned R9D overhead evidence protocol

- Fonte: https://github.com/luanmorenommaciel/apex/issues/113
- Próximo passo (owner_decision): Owner Harness/mantenedor a confirmar: ratificar ou adiar protocolo. Não aguardar #167 para preparar desenho e não executar R9D nesta revisão.
- Dependência: Nenhum predecessor técnico para design no corpo. Execução depende de harness funcional, ambiente e thresholds autorizados. Release gate também depende de capacidade do runner.
- Prova/limite: DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Esta rodada não acrescenta execução de produto; considerar apenas a leitura estática e os recibos específicos deste objeto.

## issue #114 — [Study][Infra] Rehearse ClickHouse 26.x upgrade and rollback

- Fonte: https://github.com/luanmorenommaciel/apex/issues/114
- Próximo passo (ready_offline): Owner Infra/mantenedor a confirmar: decidir necessidade e preparar plano. Nenhuma recomendação de versão, mudança de pin ou execução foi feita.
- Dependência: Design não tem predecessor técnico segundo o corpo. #109/#170 informam critérios e quietude; execução depende de plano específico e autorização. Não exigir fechamento dos dois estudos para começar este.
- Prova/limite: DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Esta rodada não acrescenta execução de produto; considerar apenas a leitura estática e os recibos específicos deste objeto.

## issue #115 — [Engine] Consumer-side execution_id→job→stage attribution gate (producer done in contract v0.6)

- Fonte: https://github.com/luanmorenommaciel/apex/issues/115
- Próximo passo (owner_decision): Mantenedor/owner a confirmar: registrar superfície, reaproveitar testes discriminantes existentes e fechar apenas critérios demonstrados. Encerramento requer satisfação dos critérios públicos ou uma revisão explícita de escopo, incluindo a prova SQL/RDD exigida. Três PRs e remoção geral de -1 não são requisitos autorizados.
- Dependência: A precondição histórica de integração do produtor #96 já foi atendida. #169 ajuda a explicitar seleção de tentativa, mas não bloqueia o estudo de contrato ou a definição da primeira superfície por padrão. Mudanças de schema ou thresholds não entram implicitamente. #117 pode ser estudada em paralelo.
- Prova/limite: DIRETO ESTÁTICO: regras do resolver, testes escritos e flag Front. RELATADO: 25 testes focados e 213 testes Engine/root, com 11 skips, no corpo de #126. PENDENTE: integração e recibo runtime SQL/RDD no recorte escolhido. A leitura de testes não afirma que passaram nesta auditoria.

## issue #117 — [Verify/Front/Serve] Preservar atribuição e unificar o contrato do piso de ruído

- Fonte: https://github.com/luanmorenommaciel/apex/issues/117
- Próximo passo (owner_decision): Owner Verify a confirmar com Front/Serve e Infra somente se necessária: primeiro fechar o desenho, depois aceitar as folhas e a rota delimitada. Não encerrar #117 apenas porque uma reunião decidiu ou novas issues foram criadas; encerrar após critérios atendidos ou alteração explícita e rastreável de escopo pelo mantenedor.
- Dependência: Identificar produtor/escritor/consumidores condiciona a implementação e o tipo de prova, não todo o estudo. F02/F03 (semântica), F06 (rota), F07 (amostras), F08/F09 (consumo) podem ser preparados em paralelo. F05 só é necessário se a solução escolhida alterar schema. A PR #162 trata __version__ e não bloqueia esta decisão.
- Prova/limite: DIRETO ESTÁTICO: campo omitido na serialização, representação dos DDLs, operadores de comparação, fórmulas e leitura Serve existente. RELATADO: reprodução histórica com configs iguais e vetores numéricos na issue. INFERÊNCIA CONDICIONAL: se a linha bruta for persistida e consumida sem estado de atribuição, o predicado pode certificar magnitude não atribuível. Não foi observado incidente nem comprovado um escritor de produção nesta rodada.

## issue #122 — [Decision][Cross-pod] Ratify the Ask HTTP/BFF boundary and atomic publication sequence

- Fonte: https://github.com/luanmorenommaciel/apex/issues/122
- Próximo passo (owner_decision): Mantenedor e owners Front/Serve a confirmar: reenquadrar proposta e registrar proceed/defer/reject. Preservar candidato, sem publicação em bloco ou deploy implícito.
- Dependência: Relacionar #171 para política de exposição e #115/#117 para limites sem exigir que todos estejam fechados. A própria issue permite expor resultados existentes enquanto atribuição continua indisponível.
- Prova/limite: DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Esta rodada não acrescenta execução de produto; considerar apenas a leitura estática e os recibos específicos deste objeto.

## issue #123 — [Bug][Pod 2 / Engine] Complete the public tail-outlier gate integration

- Fonte: https://github.com/luanmorenommaciel/apex/issues/123
- Próximo passo (owner_decision): Mantenedor com gustocezar: reconciliar a evidência existente e ratificar a garantia pretendida. Encerramento depende desse mapa e do resíduo comprovado, com referência ao recibo correto; não apenas merge nem ausência presumida de runtime. Nenhuma publicação, fechamento ou nova execução foi feita nesta auditoria.
- Dependência: DEC-N6/E17 governa a garantia de associação. #174/E08 (dev/.env) e #175/E09 (ownership de recursos) condicionam uma nova execução segura no ambiente escolhido, mas não anulam historicamente o runtime existente. #124 cobre dispatch offline. Cold start e Windows são lacunas próprias, não requisitos universais inventados para todo item.
- Prova/limite: DIRETO ESTÁTICO: caminho do gate e seus predicados. RELATO PÚBLICO HISTÓRICO: runtimes, saídas e testes de setembro. Não foram reexecutados nem todos os logs brutos revalidados nesta rodada. O wrapper reutilizou cache de imagens com identidade conferida e recursos parciais; não provou cold start de registry vazio. Windows e main atual não se tornam certificados por esse relato. Merge é observado; review humano formal não foi inferido.

## issue #124 — [Test][Pod 2 / Engine] Make PowerShell package coverage explicit and command-aware

- Fonte: https://github.com/luanmorenommaciel/apex/issues/124
- Próximo passo (ready_offline): Owner a confirmar: manter #124 aberta para reconciliação do critério de dispatch e documentação. Fechar depois de prova discriminante e critérios restantes atendidos, ou de mudança explícita de escopo pelo mantenedor. Não mover a lacuna para follow-up opcional para justificar um fechamento prematuro.
- Dependência: A prova de dispatch pode ser desenvolvida offline sem Spark, ClickHouse, #117 ou conclusão total de #130. CI é evidência complementar sobre o SHA escolhido. Obter primeiro CI verde na main não substitui o controle discriminante nem é a única forma possível de provar a alteração. Plataforma/runner deve respeitar a matriz escolhida, sem inventar Ubuntu 26.04 ou Windows como requisito original desta issue.
- Prova/limite: DIRETO ESTÁTICO: ausência de pwsh provoca falha, oito rótulos são comparados e a execução de Command ocorre depois da saída dry-run. RELATADO: 18 testes focados/69 root na entrega da #128. INFERÊNCIA VERIFICÁVEL: mutar somente Command deixa o rótulo esperado intacto. A mutação não foi aplicada nem o produto executado nesta revisão.

## issue #125 — [Governance] Protect main with required CI checks and pull-request review

- Fonte: https://github.com/luanmorenommaciel/apex/issues/125
- Próximo passo (owner_decision): Mantenedor/admin a confirmar: revisar regra concreta e aplicar quando autorizado. Encerrar apenas com configuração e controles observados; não por minuta ou contagem de jobs.
- Dependência: Titular/admin é necessário para aplicar regra. Capacidade de CI afeta sua operação, mas desenho pode avançar com G01 em aberto. Não declarar que todas as PRs esperam regularização financeira, pois há checks verdes observados.
- Prova/limite: DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Esta rodada não acrescenta execução de produto; considerar apenas a leitura estática e os recibos específicos deste objeto.

## issue #130 — [Governance] Restore GitHub Actions billing for required CI

- Fonte: https://github.com/luanmorenommaciel/apex/issues/130
- Próximo passo (owner_decision): Titular/mantenedor a confirmar: reconciliar estado/critério e decidir prova restante. Encerrar por critérios públicos atendidos ou explicitamente revisados, sem disparo de CI nesta auditoria.
- Dependência: Titular/admin confirma condições operacionais. Revisão de PRs e política #125 podem avançar; uma nova execução depende do meio de prova quando necessário. Não impor bloqueio a toda a fila.
- Prova/limite: DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Esta rodada não acrescenta execução de produto; considerar apenas a leitura estática e os recibos específicos deste objeto.

## issue #154 — [Test][Pod 2 / Engine] Keep schema preflight aligned with stage queries

- Fonte: https://github.com/luanmorenommaciel/apex/issues/154
- Próximo passo (ready_offline): Mantenedor/revisor Engine a confirmar: revisar #155 e reconciliar critérios/board. Encerramento depende da decisão registrada sobre a contribuição; nenhuma mutação GitHub ocorreu aqui.
- Dependência: Predecessoras já integradas. Prova de integração escolhida precisa da árvore correta; G01 é condição operacional se execução remota for necessária. Mantenedor pode revisar antes de novo CI.
- Prova/limite: DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Esta rodada não acrescenta execução de produto; considerar apenas a leitura estática e os recibos específicos deste objeto.

## PR #155 — test(engine): keep schema preflight aligned with stage queries

- Fonte: https://github.com/luanmorenommaciel/apex/pull/155
- Próximo passo (ready_offline): Autor/mantenedor a confirmar: entrada diff 561b27e e checks existentes; saída revisão e prova da integração escolhida; fechar após decisão registrada e atualização de #154, sem presumir aprovação nesta auditoria.
- Dependência: Sem dependência de código das outras sete PRs. G01/#130 só condiciona a obtenção de uma nova prova remota se o acesso ao runner ainda falhar. O mantenedor escolhe como testar a integração; rebase não é obrigação universal.
- Prova/limite: DIRETO: diff, heads, checks e ausência de reviews no endpoint. RELATADO: 46 testes focados, 310 Engine e controles de mutação no corpo. A igualdade de árvores local/publicada é relato, sem comparação independente nesta etapa. Nenhuma prova de ClickHouse real decorre deste teste.

## issue #156 — [Test][Pod 3 / Serve] Strengthen transport parity and console findings regression gates

- Fonte: https://github.com/luanmorenommaciel/apex/issues/156
- Próximo passo (owner_decision): Mantenedor/revisores a confirmar: revisar #157–159, escolher integração e registrar reconciliação. Encerrar #156 pelos seus critérios; preservar #163/#172 com seus recortes, sem nova execução aqui.
- Dependência: A decisão de integração e os diffs efetivos governam a prova. G01 não bloqueia genericamente os heads já verdes. #163 depende de helpers/base #157; política de release/RC é separada.
- Prova/limite: DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Esta rodada não acrescenta execução de produto; considerar apenas a leitura estática e os recibos específicos deste objeto.

## PR #157 — test(serve): pin eight-tool transport parity with identical arguments

- Fonte: https://github.com/luanmorenommaciel/apex/pull/157
- Próximo passo (ready_offline): Revisor e mantenedor a confirmar: revisar a3ed972; saída decisão e recibo da integração; atualizar S08/S24 e preservar #156 como guarda-chuva quando restarem critérios.
- Dependência: Independente de #158/#159 para seu objetivo; #163 depende destes helpers. NOV-03 (proposta interna sobre fila aberta sem revisão e ordem de ondas) coordena revisão, sem impor um CI novo idêntico a toda PR por regra geral.
- Prova/limite: DIRETO: vetores dos oito tools, fakes, normalização de payloads e igualdade nas duas portas; 11 checks verdes. RELATADO: 572 testes da combinação local e provas de transporte reais separadas. Os testes aqui usam chamadas MCP em processo e TestClient HTTP; não validam nginx, autenticação em implantação ou ClickHouse real. O payload registra base_sha c4541a59 e head próprio; main observada c3c3ea3. Os checks citados não certificam uma futura integração/rebase. A árvore efetiva de checkout de cada job não foi estabelecida a partir desse campo base_sha.

## PR #158 — test(serve): pin findings score-tie order on both SQL doors

- Fonte: https://github.com/luanmorenommaciel/apex/pull/158
- Próximo passo (ready_offline): Revisor/mantenedor: entrada 514b0e5; saída revisão e decisão de integração. Reconciliar #156 apenas quanto a este critério.
- Dependência: Pode ser revisada paralelamente a #157, #161 e #162. Não precisa esperar a política global de versão ou runtime Verify. Coordenar com #182: ela remove front_query e queries.ts; portar o teste novo mantendo os controles Serve aditivo/legado.
- Prova/limite: DIRETO: três consultas verificadas e checks do head. RELATADO: 572 testes da combinação. A ordem literal é comprovada no texto exercitado; execução e plano de SQL real não foram revalidados aqui. O payload registra base_sha c4541a59 e head próprio; main observada c3c3ea3. Os checks citados não certificam uma futura integração/rebase. A árvore efetiva de checkout de cada job não foi estabelecida a partir desse campo base_sha.

## PR #159 — fix(serve): make parity gate diagnose drift and clean derived fixture rows

- Fonte: https://github.com/luanmorenommaciel/apex/pull/159
- Próximo passo (ready_offline): Revisor de Serve e mantenedor: entrada 1685f8a e recibos citados; saída parecer da limpeza e decisão de integração. Se exigida nova prova operacional, defini-la antes em ambiente autorizado; esta auditoria não a executa.
- Dependência: Revisão pode ocorrer em paralelo. Uma reprodução operacional depende de store/ambiente autorizado e ownership definido; não transforma #175 em bloqueio obrigatório de todos os testes. #157/#158 complementam, sem dependência de código para o gate. Coordenar com #182: portar _two_doors de console_statements/QUERIES_TS para serve_statements e preservar browser_seen, controles e limpeza.
- Prova/limite: DIRETO: limpeza por IDs/fingerprint, mutations_sync=1, consulta de existência do rollup e propagação de falhas; testes positivos/negativos no diff. RELATADO: gate 19 PASS/0 FAIL/0 SKIP e 572 testes combinados. Testes controlados não provam concorrência nem isolamento de toda implantação. O payload registra base_sha c4541a59 e head próprio; main observada c3c3ea3. Os checks citados não certificam uma futura integração/rebase. A árvore efetiva de checkout de cada job não foi estabelecida a partir desse campo base_sha.

## PR #161 — ci: keep root gate diagnostics after Python lane failures

- Fonte: https://github.com/luanmorenommaciel/apex/pull/161
- Próximo passo (ready_offline): Mantenedor/revisor: entrada d61eab8, condições e checks atuais; saída decisão de integração e limite aceito ou controle de falha especificado. Não repetir CI verde sem nova razão.
- Dependência: Independente de política Verify e de #157. Mudanças futuras no workflow precisam preservar IDs e condições. DEC-N1 pode ser decidida em paralelo.
- Prova/limite: DIRETO: !cancelled() e pré-condições de checkout/uv; root também exige PowerShell pronto. A lane continua falhando, sem continue-on-error. DIRETO: três checks verdes. RELATADO: avaliação local dos cenários. PENDENTE: eventual controle de falha no runner, se requerido pelo mantenedor.

## PR #162 — fix(verify): align module version with package 0.1.0

- Fonte: https://github.com/luanmorenommaciel/apex/pull/162
- Próximo passo (ready_offline): Revisor/mantenedor: entrada 3955f9d e três checks verdes; saída decisão de integração. Corrigir F19/DEC-N2 e resumos derivados sem transformar política futura em gate desta PR.
- Dependência: Sem dependência técnica de escritor externo, migração, DEC-06 ou conclusão da política de distribuição. Se a árvore de integração mudar, avaliar checks aplicáveis; não declarar o CI atual ausente.
- Prova/limite: DIRETO: diff, pyproject e models.py no SHA da main; três checks do head. A hipótese de que esta PR corrige persistência é refutada pelo default preexistente. Uso externo de __version__ não foi inventariado; nenhuma regressão de armazenamento foi demonstrada.

## PR #163 — test(serve): pin search_kb plan_json hits over both transports

- Fonte: https://github.com/luanmorenommaciel/apex/pull/163
- Próximo passo (ready_offline): Mantenedor/autor: entrada pilha #157→#163 e workflow filtrado; saída método escolhido, árvore de integração identificada e validação correspondente. Não mesclar nem disparar CI nesta auditoria.
- Dependência: Dependência técnica de helpers de #157; decisão humana sobre método de integração. Nenhuma dependência da política Verify. workflow_dispatch existe no arquivo; viabilidade de disparo e ref precisa ser verificada quando autorizado.
- Prova/limite: DIRETO: imports, conteúdo positivo plan_json, token vinculado, esquema e fluxos ausente/diferente; base/head e zero checks; workflow com workflow_dispatch. RELATADO: testes/mutações locais. Ausência de disparo automático não significa impossibilidade de prova manual.

## PR #164 — docs: align Serve and Verify docs with current contract

- Fonte: https://github.com/luanmorenommaciel/apex/pull/164
- Próximo passo (ready_offline): Revisor documental/mantenedor: entrada 5d42763 e fontes no SHA c3c3ea3; saída revisão, decisão de escopo CL-02 e integração. Sem exigir nova prova funcional para mudança só de texto.
- Dependência: Sem gate de CI de código obrigatório inventado para Markdown ignorado. DEC-N3 escolhe escopo de comentários; M1 não bloqueia estudos do contrato M3 nem esta revisão.
- Prova/limite: DIRETO: diff e fontes main-Makefile, main-workflow, main-contract, main-server, main-serve-pyproject, main-predict e main-verify-models. Documentação não comprova runtime. O texto de job_conf deve acompanhar o contrato capturado; não autoriza inventar defaults ausentes.

## issue #165 — [Docs][Cross-pod] Reconciliar a linhagem do contrato e os cabeçalhos SQL

- Fonte: https://github.com/luanmorenommaciel/apex/issues/165
- Próximo passo (ready_offline): Mantenedor do contrato a confirmar: receber os quatro trechos e suas fontes; devolver decisões de status/redação. Encerrar após reconciliação documental revisada e integrada, ou decisão explícita de manter marcadores com justificativa. Sem nova tarefa runtime por inferência.
- Dependência: Depende de o mantenedor identificar qual ato ratificou cada extensão e aprovar o texto correspondente. A preparação dos quatro trechos pode correr em paralelo ao gate #115 e ao estudo #117; essas entregas não são gates técnicos para reconciliar redação. Coordenação limitada adicional: tests/test_telemetry_compatibility_matrix.py:145–147 exige os marcadores PROPOSED literalmente; se a redação mudar, atualizar essa guarda com evidência da história preservada, sem depender de concluir toda #180.
- Prova/limite: FATO OBSERVADO: declarações divergentes nos arquivos fixados. RELATO HISTÓRICO: estudo e quatro alternativas atribuídos no comentário a Kimi/Codex em 11/10. PROPOSTA: reconciliação editorial com prova de autoridade para qualquer mudança normativa. Não houve teste nem prova de produtor nesta revisão.

## issue #166 — [Feature][Pods 1 e 3] Explicar TAIL_OUTLIER nos consumidores sem confundir cauda com skew

- Fonte: https://github.com/luanmorenommaciel/apex/issues/166
- Próximo passo (ready_offline): Pods 1 e 3/Verify a confirmar: escolher a política a partir dos ramos citados e revisar fixtures. Encerrar apenas quando os consumidores afetados tiverem comportamento decidido, testes discriminantes e evidência de integração correspondente; manter detector e piso absoluto fora do delta.
- Dependência: Owners dos três consumidores devem decidir mensagens e comportamento de unknown. Pode ser dividido em mudanças atômicas Front/Verify/Serve com a mesma matriz; não depende de alterar threshold da #168 nem de implementar RETRY_PRESSURE de novo. O detector da #127 é antecedente já integrado.
- Prova/limite: FATO OBSERVADO: uniões de tipos, mapeamento e ramos do código. RELATO HISTÓRICO: matrizes e fixtures locais em 11/10; não aceite novo. INFERÊNCIA delimitada: fallback pode oferecer configuração não justificada quando os gates permitirem; não afirmo que o finding padrão de confiança 0.72 oferece diff com limiar padrão 0.75. PROPOSTA: política explícita por tipo.

## issue #167 — [Bug][Pod 2] Alinhar argumentos do braço ON do harness R9D com o runner canônico

- Fonte: https://github.com/luanmorenommaciel/apex/issues/167
- Próximo passo (owner_decision): Autor/owner Pod 2 a confirmar: fornecer candidato identificado e provas existentes; saída revisável é delta mínimo e matriz de argumentos/configuração. Fechar a issue após integração e provas de aceite acordadas, sem declarar overhead medido por teste de binding. Não criar outra implementação concorrente antes de revisar o candidato.
- Dependência: O contrato compartilhado com #174 é dependência técnica do delta; publicação e escopo da PR são decisões do mantenedor. Windows e Compose são camadas posteriores de prova, não razões para repetir testes já relatados sem mudança. #113 governa benchmark; #123/E17 permanece em paralelo.
- Prova/limite: FATO OBSERVADO: incompatibilidade entre chamada Python e assinaturas PowerShell nos blobs fixados. RELATO HISTÓRICO: 85 testes iniciais e prova posterior de 10 casos com stubs; não somar como execução desta revisão. A análise de parser sem daemon não prova isolamento de rede. PROPOSTA: revisar candidato e aceitar separadamente contrato de argumentos e execução real.

## issue #168 — [Study][Pod 2] Avaliar caudas de duração muito pequenas antes de propor piso absoluto

- Fonte: https://github.com/luanmorenommaciel/apex/issues/168
- Próximo passo (ready_offline): Owner Engine/Pod 2 a confirmar: receber corpus sanitizado e contrato de amostragem; devolver relatório e recomendação ao mantenedor. O estudo pode encerrar com adiamento/rejeição fundamentados; implementação só após decisão, sem tornar a própria existência da issue uma autorização de threshold.
- Dependência: Precisa de corpus sanitizado com unidades/população e contribuição de owners de workloads. Pode correr paralelo à apresentação #166 e ao gate #123; não bloquear essas correções esperando a decisão do piso. Harmonizar população com #169 sem afirmar que esse estudo escolhe seu seletor.
- Prova/limite: FATO OBSERVADO: condições no evaluate. RELATO HISTÓRICO: estudos/JSON conferidos em 11/10. INFERÊNCIA: razão alta em milissegundos pode ser pouco acionável; não é falso positivo observado. PROPOSTA: estudo de sensibilidade antes da política.

## issue #169 — [Decision][Cross-pod] Definir seleção de tentativa e população de métricas entre consumidores

- Fonte: https://github.com/luanmorenommaciel/apex/issues/169
- Próximo passo (owner_decision): Owners dos consumidores a confirmar: entrada matriz dos seletores e fixtures históricas identificadas; saída decisão de desempate/população e sequência de mudanças/migração. Encerrar a decisão com registro explícito e ligar implementação separada, ou encerrar o conjunto somente após provas acordadas; não afirmar que paridade já existe.
- Dependência: Decisão entre owners Engine/Serve/Memory/Front; compatibilidade e possível migração de run_outcomes são gates humanos. Inventário e fixtures correm em paralelo; mudanças que prometem paridade dependem da política. Não impor #115 como bloqueio de toda seleção por tentativa.
- Prova/limite: FATO OBSERVADO: seletores SQL/offline citados. RELATO HISTÓRICO: resultados sintéticos no registro canônico. INFERÊNCIA sustentada pelos seletores: maior tentativa pode diferir do evento com ts mais recente. PROPOSTA/DECISÃO PENDENTE: contrato comum, fallback histórico e política de dados persistidos.

## issue #170 — [Decision][Pod 2 / Infra] Definir reaplicação de DDL e o alcance de verify-ddl

- Fonte: https://github.com/luanmorenommaciel/apex/issues/170
- Próximo passo (owner_decision): Owner Infra a confirmar: receber classificação dos SQLs e escopo observado do checker; devolver política e alternativa escolhida. Encerrar a decisão com garantia/limites e plano verificável, sem executar migração em store existente nesta revisão.
- Dependência: Owner Infra e dono da ingestão decidem garantia, janela e rollback. Documentar limites pode correr em paralelo à análise de migrações. Prova runtime futura requer store próprio e cenário decidido; #147 não substitui esse aceite nem precisa ser refeito.
- Prova/limite: FATO OBSERVADO: laço de aplicação, comentário e comparação de colunas. RELATO HISTÓRICO: testes locais de migração e fixture sintética no registro. INFERÊNCIA: o status final não prova segurança durante ingestão. DECISÃO PENDENTE: coordenação de ingestão e extensão ou limitação explícita do verificador.

## issue #171 — [Decision][Pods 1 e 3] Definir exposição do OpenAPI e quem guarda o token da API v1

- Fonte: https://github.com/luanmorenommaciel/apex/issues/171
- Próximo passo (owner_decision): Owner API/mantenedor a confirmar: receber matriz de fronteira e alternativas; saída é política versionada por perfil e plano de verificação. Encerrar a decisão com responsáveis e limites claros; implementar só o comportamento aprovado, sem declarar incidente inexistente.
- Dependência: Mantenedor/owner API define perfis e política; Front e operação participam da custódia. #172 pode caracterizar o perfil existente em paralelo, identificando a política usada. Não depender de escolher ou implementar Ask/BFF v2.
- Prova/limite: FATO OBSERVADO: regra de admissão e configuração do proxy. RELATO HISTÓRICO: escolhas abertas descritas pela #129, conforme issue. DECISÃO PENDENTE: exposição por perfil e custódia/renovação. Ausência de injeção no nginx não implica ausência de qualquer autenticação no cliente.

## issue #172 — [Test][Pods 1 e 3] Validar o perfil HTTP da Console no nginx e no navegador

- Fonte: https://github.com/luanmorenommaciel/apex/issues/172
- Próximo passo (ready_offline): Owners Front/Serve a confirmar: preparar a lista de recibos e o protocolo com árvore/imagem/DATA_SOURCE/política identificados; registrar as decisões pendentes. A execução posterior dos casos nginx/browser requer ambiente e autorização próprios.
- Dependência: Precisa de árvore/imagem identificadas, perfil HTTP configurado e ambiente próprio. Reutilizar recibos API somente quando blobs/escopo forem equivalentes; #171 só bloqueia mudança de política, não caracterização identificada do perfil atual. Pod 1 valida UI e Pod 3 a resposta/API.
- Prova/limite: FATO OBSERVADO: configuração nginx em SHA fixado e escopo público da issue. RELATO HISTÓRICO: provas API e lacuna original. PROPOSTA: inventário de recibos posteriores, depois apenas as provas de proxy/browser ainda necessárias. Não converter falta de prova consultada em prova de falha.

## issue #173 — [Study][Pods 2 e 3] Auditar a seleção de database ClickHouse por consumidor

- Fonte: https://github.com/luanmorenommaciel/apex/issues/173
- Próximo passo (ready_offline): Owners Pods 2 e 3 a confirmar: receber lista inicial das consultas e promessa de perfis; saída é inventário por lane com decisão justificada. Encerrar estudo por implementar, manter restrição documentada ou adiar; não declarar auditoria completa de bancos nesta ficha.
- Dependência: Owners Engine/Memory/Verify/Serve definem os perfis. O inventário pode avançar sem #154/#155 nem refazer #129; mudança de contrato comum depende da decisão. Não exigir migração DDL apenas porque há literal.
- Prova/limite: FATO OBSERVADO: literais SQL e configuração de Engine/Serve citados. RELATO HISTÓRICO: inventários anteriores do E04, sem reutilizar totais. PROPOSTA: matriz por query e perfil suportado. INFERÊNCIA: configurar banco alternativo pode ser ineficaz em consultas qualificadas; só constitui defeito se o perfil for prometido.

## issue #174 — [Bug][Pod 2 / Package] Preservar dev/.env ao preparar o runner canônico

- Fonte: https://github.com/luanmorenommaciel/apex/issues/174
- Próximo passo (ready_offline): Autor/owner do pacote a confirmar: entrada candidato identificado e recibos históricos; saída revisão pequena com prova negativa de preservação. Encerrar após integração e critérios acordados para entrypoints/plataformas, mantendo runtime real e ownership com seus limites. Não gerar uma segunda correção concorrente sem confrontar o candidato existente.
- Dependência: Declaração/forwarding do parâmetro no runner (#167) é dependência técnica. Política de ownership (#175) governa operações posteriores, não precisa bloquear prova offline de preservação. Windows e Compose são provas distintas; não repetir suítes históricas sem motivo nem usar stubs como substituto dessas camadas.
- Prova/limite: FATO OBSERVADO: caminho de cópia e invocadores na base. RELATO HISTÓRICO: candidato e resultados de PowerShell/stubs em macOS, inclusive hashes/JUnit relatados pelo Codex em 11/10. INFERÊNCIA: arquivo divergente pode ser substituído; não houve acesso a .env real nem incidente reproduzido aqui. PROPOSTA: revisar e integrar contenção mínima.

## issue #175 — [Decision][Pod 2 / Package] Definir identidade e ownership de stacks entre checkouts

- Fonte: https://github.com/luanmorenommaciel/apex/issues/175
- Próximo passo (owner_decision): Mantenedor/owner do pacote a confirmar: entrada inventário e duas opções; saída política de ownership por operação e plano do guard. Encerrar estudo/decisão após aprovação fundamentada ou adiamento com limites; não declarar implementação pelo inventário.
- Dependência: Mantenedor/owner de pacote decide identidade, migração e adoção de stacks antigas. Inventário e desenho podem correr em paralelo a #167/#174/#178; testes offline de argv/arquivo/endpoint não exigem essa política completa. Provas que mutem runtime real precisam conferir ownership antes.
- Prova/limite: FATO OBSERVADO: nomes, portas e montagens nos dois Compose base. RELATO HISTÓRICO: matriz dos sete arquivos/12 operações. INFERÊNCIA: nomes globais/portas compartilhadas podem causar colisão ou seleção errada; não afirmo que redes compartilhadas sempre falham. DECISÃO PENDENTE: protocolo de ownership e compatibilidade.

## issue #176 — [Study][Pod 2 / Infra] Documentar rotação de credencial local ClickHouse e recuperação

- Fonte: https://github.com/luanmorenommaciel/apex/issues/176
- Próximo passo (ready_offline): Owner Infra a confirmar: entrada inventário de procedimentos e perfil da imagem; saída proposta de runbook/rollback para revisão. Encerrar o estudo com método e limites documentados; só declarar procedimento validado após recibo próprio da prova acordada, sem revogar credenciais nesta revisão.
- Dependência: Owner Infra define perfil e disponibilidade de ambiente descartável para prova futura; operadores de clientes participam da atualização. #33 pode orientar política, mas a ausência de SECURITY.md não é automaticamente bloqueio técnico do estudo. Não condicionar toda v1 a esse runbook sem requisito acordado.
- Prova/limite: FATO OBSERVADO: configuração do Compose. INFERÊNCIA: recuperação improvisada pode quebrar acesso ou dados; não incidente observado. PROPOSTA: inventário e runbook com rollback. DECISÃO PENDENTE: perfil suportado, método de rotação e quando recriação é permitida.

## issue #177 — [Study][Pod 3] Definir narração AQE usando configuração capturada em job_conf

- Fonte: https://github.com/luanmorenommaciel/apex/issues/177
- Próximo passo (ready_offline): Owner Serve a confirmar: receber exemplos e mapa de leitura; saída decisão de produto e, se aprovada, plano atômico com testes negativos. Encerrar estudo por decisão fundamentada, mantendo implementação como seguimento explícito; não declarar narração pronta por existir uma query.
- Dependência: Owner Pod 3 decide implementar/adiar/rejeitar e superfície. O estudo pode correr em paralelo a #115; qualquer afirmação por stage depende de vínculo válido ou deve permanecer no escopo da execução. Não bloquear o estudo com suposta inexistência de job_conf, que já é lida.
- Prova/limite: FATO OBSERVADO: query e notas AQE no código. RELATO HISTÓRICO: proposta F4.3 e contagem antiga S15. INFERÊNCIA limitada: cruzar configuração e transição pode melhorar explicação; o valor de produto deve ser avaliado. PROPOSTA: exemplos determinísticos com ausências e escopo explícito.

## issue #178 — [Feature][Pod 2 / Harness] Respeitar o endpoint OTLP escolhido nos alvos de patologia

- Fonte: https://github.com/luanmorenommaciel/apex/issues/178
- Próximo passo (ready_offline): Owner Pod 2/Harness a confirmar: entrada Makefile/defaults e precedência acordada; saída PR pequena com comando final e controle negativo. Encerrar a implementação após review/integração e prova offline acordada; entrega OTLP fica em recibo próprio, sem condicionar tudo à decisão #175.
- Dependência: Owner Harness decide alvos e precedência. Teste offline pode avançar em paralelo a #175 e #167/#174; a política completa de identidade não é gate técnico. Prova futura de entrega exige endpoint próprio e cenário de runtime, sem ampliar esta PR para Collector ou nomes de stack.
- Prova/limite: FATO OBSERVADO: comandos/defaults e consumidores específicos lidos. INFERÊNCIA: override ignorado pode levar telemetria a um destino distinto do pretendido; nenhuma entrega OTLP foi observada. PROPOSTA: precedência única e teste do comando final. Não afirmar suporte da variável em todos os jobs: somente skew_join/factory e runner shell foram inspecionados.

## issue #179 — [Study][Pod 1 / Verify] Avaliar trabalho medido e fallback estimado no predictor

- Fonte: https://github.com/luanmorenommaciel/apex/issues/179
- Próximo passo (owner_decision): Owner Verify a confirmar: entrada três trechos obsoletos, DDL e guarda estática; saída pequena correção textual revisada, seguida de estudo com decisão measured/estimated/unavailable. Encerrar o texto após integração; manter estudo aberto até decisão, sem exigir implementação se a conclusão for manter estimativa.
- Dependência: Owner Verify/modelo decide semântica de W e fallback; estudo pode correr em paralelo a #117/#162/#164. Há coordenação de teste com #180: alterar a asserção literal para refletir a nova fonte, preservando a evidência histórica, sem esperar toda a matriz nova. Não criar dependência técnica de versão #162.
- Prova/limite: FATO OBSERVADO: discrepância texto/DDL/leitura Engine e asserção estática presa à frase. RELATO HISTÓRICO: candidato CL-02 cobre predict, conforme auditoria Parte03, sem reinspeção do patch local aqui. INFERÊNCIA a estudar: runtime agregado pode ou não representar W para a mesma população. PROPOSTA: correção editorial separada de escolha matemática.

## issue #180 — [Docs][Cross-pod] Atualizar cobertura da matriz para Front, API e proveniência

- Fonte: https://github.com/luanmorenommaciel/apex/issues/180
- Próximo passo (ready_offline): Owners cross-pod a confirmar: entrada matriz histórica, blobs e seis linhas de estudo; saída visão atual e guarda estática revisadas. Encerrar após integrar atualização com cobertura das três superfícies e destinos explícitos para lacunas; preservar L14 agrupado, sem novo estudo duplicado.
- Dependência: Contribuições dos owners Front/API/Memory e mantenedor do contrato. Pode avançar em paralelo aos estudos; depende apenas das fontes para cada afirmação. Ajustes #165/#179 precisam coordenar asserções literais do teste, mas não aguardar toda esta entrega. Follow-ups devem ser reconciliados com #106/#108/#109/#117, sem duplicar IDs.
- Prova/limite: FATO OBSERVADO: base declarada da matriz, tipos/rotas/query e testes estáticos. RELATO HISTÓRICO: seis linhas propostas e revisão anterior nos comentários. INFERÊNCIA: uma visão antiga lida como atual induz erro; não é regressão do produto. PROPOSTA: visão atual versionada com status por evidência. L14 não vira quatro novas implementações por ausência no inventário.

## issue #181 — [Docs][Pod 3 / Serve] Consolidar entregas, evidências, PRs, decisões e backlog — 19/10/2026

- Fonte: https://github.com/luanmorenommaciel/apex/issues/181
- Próximo passo (owner_decision): Conferir minuta local de adendo da auditoria ampla e decidir se/onde publicar; a #181 continua a visão de Augusto para discussão, não autoridade única do projeto.
- Dependência: Confirmação do usuário antes de qualquer alteração no Git/GitHub.
- Prova/limite: Corpo público coincide com a cópia local salvo newline final; isso não demonstra que o fechamento amplo já foi publicado.

## PR #182 — feat(front): harden the console and read only through the Apex API

- Fonte: https://github.com/luanmorenommaciel/apex/pull/182
- Próximo passo (ready_offline): Revisar foco Serve/Front e coordenar #158/#159; preservar controles no SQL único e explicitar decisões de exposição e oráculos.
- Dependência: Coordenação de superfície e política #171; #122 é decisão separada.
- Prova/limite: Checks atuais observados; execução live do corpo é relato. Leitura focal de patches, sem testes novos.

## PR #183 — docs(pod3): reconcile Serve backlog, decisions and evidence for team discussion

- Fonte: https://github.com/luanmorenommaciel/apex/pull/183
- Próximo passo (ready_offline): Revisar os 28 documentos no draft; alinhar diferenças trazidas pelo adendo sem misturar implementação; decidir revisão/merge depois.
- Dependência: Revisão humana; novo CI não é exigência automática para Markdown filtrado.
- Prova/limite: Aberta draft; sem checks/reviews; head idêntico ao publicado. Não promover draft ou atualizar texto sem confirmação.

## PR #184 — docs(tasks): fix YAML syntax in three TaskPlan manifests

- Fonte: https://github.com/luanmorenommaciel/apex/pull/184
- Próximo passo (ready_offline): Revisar as três correções de sintaxe e distinguir parse válido de correção semântica/aceite das folhas.
- Dependência: Decisão humana para merge; não atribuir accepted:true automaticamente.
- Prova/limite: Draft aberto com três successes no SHA; nenhuma review registrada.

## PR #185 — fix(dev): harden the dev lane — clean clone, secrets-only S3, runner parity, Spark 4.1.2 fingerprint

- Fonte: https://github.com/luanmorenommaciel/apex/pull/185
- Próximo passo (ready_offline): Usar TRIAGEM-PR185.md para escolher revisão pequena e revisar vínculo com #167 e N06.
- Dependência: Comparar a implementação candidata com #167/N06 e preservar critérios separados de #174/#175/#178/#113.
- Prova/limite: Quatro checks verdes observados; relatos locais/runtime do autor não reproduzidos. Triagem focal, não revisão de todos os 38 arquivos.

