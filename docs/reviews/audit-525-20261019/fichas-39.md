# Fichas documentais — lote 39

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-381"></a>

## P-E04 — [Audit][Pod 2/Pod 3] Literais 'apex.' restantes após #129 e #131

Frente: minutas_publicadas. Encaminhamento: minuta_publicada_173_inventario_ainda_ausente.

### Identidade e estado

P-E04 é minuta local de 11/10/2026, preservada para linhagem; PUBLICATION registra a representação pública luanmorenommaciel/apex#173 em 2026-10-11T04:24:33Z. Aberta no snapshot de 16/10; estado corrente e responsabilidade não inferidos desta data.

### Intenção e benefício

Intenção: recontar literais apex. depois de #129/#131, separar SQL de comentário e decidir por lane quais devem usar o database configurado. Público: Pods 2 e 3. Ganho: CLICKHOUSE_DATABASE coerente entre lanes.

### Feito, faltante e não comprovado

A publicação #173 troca contagem de literais por inventário de configuração, SQL executável, chamador e perfis; proíbe troca global. O inventário lexical revalidado distingue SQL de prosa, mas não prova caminho ativo. Seis constantes qualificadas dos watchers não são chamadas por run_all no trecho lido: ele usa store.stage_aggregates e evaluate. Portanto a recontagem é insumo, não o inventário completo que a issue pede.

### Linhagem

Registro E04 e contagem histórica a289e53 → minuta → #173 → inventário lexical c3c3ea3 → correção de alcance C04-37. Falta completar matriz de consultas/configuração/chamadores e decisões de perfil.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/P-E04.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-revalidated-fes-sources/database-literal-search.json; fontes/batch-revalidated-fes-sources/engine__src__apex_engine__watchers____init__.py.excerpt.txt; D-CORRECOES-E-LIMITES.md; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/engine__src__apex_engine__clickhouse.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/memory__src__apex_memory__clickhouse.py.txt. Locadores: Minuta/#173, inventário lexical c3c3ea3, run_all 64–68 e C04-37.

### Classe e limite da evidência

FATO OBSERVADO: texto público, resultados do inventário lexical e caminho run_all. RELATO derivado: classificação do lote E04 em seis constantes Engine, 11 ocorrências SQL Memory, uma Verify e nenhuma Serve no recorte de padrão, com prosa excluída. Isso não é contagem universal de queries dinâmicas/alcançáveis.

### Fluxo

Fluxo da minuta: recontagem —(SQL × comentário)→ decisão por lane —(lista por arquivo)→ trocar ou manter. Fluxo publicado: inventário por consulta —(explícito, herdado, texto)→ matriz de perfis —(se aprovado)→ testes com database não padrão.

### Consequências e risco

O risco relevante é consultar databases distintos apesar da configuração do client, ainda não observado como incidente. Anexar números sem alcançabilidade repetiria a limitação lexical; o material local pode alimentar matriz futura.

### Alternativas e recomendação

Preservar minuta → #173 e oferecer inventário lexical com seus limites no consolidado local. Completar o vínculo consulta→client→chamador antes de recomendar alterações; publicação de insumo não faz parte desta revisão.

### Dependências e paralelismo

Inventário estático independe de E03 ou de CI; E03 é prova distinta de database alternativo. Modificar uma query exige decidir perfil e confirmar que o caminho a usa.

### Plano e aceite propostos

Registrar C04-37 e separar constante SQL, consulta executável alcançável e prosa. Não afirmar Serve universalmente sem SQL fixa nem Engine executando seis constantes com base só em busca.

### Comunicação entre responsáveis

Para outro pod: #173 audita seleção efetiva de database. A contagem local é ponto de partida; o caminho run_all lido não usa as seis constantes qualificadas.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Substituir apex globalmente ou contar constantes como queries ativas pode alterar texto inócuo e deixar o caminho real sem correção. Que caso o teste ainda não cobre? Não se executou database alternativo nem se auditou alcançabilidade universal ou SQL dinâmica. Como eu explicaria isso para outro pod? A #173 precisa matriz por consulta/client/chamador; grep informa onde olhar e não demonstra o database efetivamente consultado.

### Próxima ação e encerramento

Próxima ação documental concluída: vincular minuta/publicação e limites da recontagem. Futuro inventário por consulta completa a investigação sem trocar literais globalmente.

<a id="item-382"></a>

## P-E08 — [Bug][Pod 2/Package] Preservar dev/.env antes de sobrescrever

Frente: minutas_publicadas. Encaminhamento: minuta_publicada_174_opcoes_ampliadas.

### Identidade e estado

P-E08 é minuta local de 11/10/2026, preservada para linhagem; PUBLICATION registra a representação pública luanmorenommaciel/apex#174 em 2026-10-11T04:24:34Z. Aberta no snapshot de 16/10; estado corrente e responsabilidade não inferidos desta data.

### Intenção e benefício

Intenção: escolher uma contenção para a cópia destrutiva de dev/.env feita por Sync-DevEnvForCanonicalScript. Público: operadores do pacote. Ganho: configuração do operador nunca substituída silenciosamente.

### Feito, faltante e não comprovado

A publicação #174 abre recusa explícita, passagem de EnvFile ou backup controlado e pede matriz ausente/idêntico/diferente/falha de escrita. O trecho 609–617 confirma Copy-Item -Force sem checagem/backup nessa função; chamadores 624/681 confirmados. A minuta nomeava recusa no problema e backup no diagrama e nas perguntas; a publicação tornou explícita também a passagem de EnvFile. Não é correto contar apenas uma alternativa na minuta. O candidato posterior é relato, não decisão desta revisão.

### Linhagem

Linhagem: revisão §3 da #127 e R2 T33 → registro E08 (DEC-10) → minuta P-E08 → #174 → candidato local conjunto com #167 → decisão [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/P-E08.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-revalidated-fes-sources/scripts__apex.ps1.sanitized.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/dev__scripts__e2e_canonical.ps1.txt; fontes/revalidated-fes-items.json. Locadores: Minuta/#174, Sync-DevEnvForCanonicalScript/chamadores e ficha E08 como relato de candidato.

### Classe e limite da evidência

FATO OBSERVADO: diferenças de alternativas e caminho de cópia/chamadores na base. RELATO: candidato posterior adota passagem de EnvFile e provas com stubs. Nenhum .env real lido ou alterado.

### Fluxo

Fluxo da minuta: decisão de contenção (recusa ou outra) —(Task-Spec)→ teste de não sobrescrita. Fluxo publicado: matriz de destino —(decisão entre três opções)→ teste negativo contra o comportamento antigo —(mensagem sem conteúdo)→ operador.

### Consequências e risco

O caminho de escrita pode substituir configuração divergente. Não houve reprodução de perda real nem decisão de que recusa é inválida; a publicação permite escolher entre alternativas e evita consentimento implícito.

### Alternativas e recomendação

Recomendado: catalogar a minuta como superada pela #174. Alternativa: manter a minuta como registro da opção de recusa, útil se o candidato de EnvFile for rejeitado. Reversível.

### Dependências e paralelismo

Estudar matriz de preservação não depende da política global #175. Se a alternativa escolhida for passar EnvFile, o runner precisa aceitá-lo (#167); recusa/backup têm outras dependências. Candidato conjunto é rota possível, não pré-requisito para todo estudo.

### Plano e aceite propostos

Registrar minuta → #174, com passagem de EnvFile tornada explícita e matriz mais precisa. O relato do candidato deve conservar seu alcance de stubs/endpoint sintético, sem ser chamado de Docker/Spark/Windows real ou zero rede.

### Comunicação entre responsáveis

Para outro pod: #174 oferece três contenções; passagem direta de EnvFile requer interface compatível com #167. O candidato relatado não substitui decisão ou prova das demais camadas.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Uma cópia forçada sem decisão pode substituir configuração; aceitar passagem de EnvFile sem parâmetro no runner pode falhar antes do gate. Que caso o teste ainda não cobre? Não houve arquivo real, Compose, Windows ou Spark; relatos de stubs não provam essas camadas. Como eu explicaria isso para outro pod? #174 preserva configuração; só a alternativa EnvFile exige o parâmetro de #167, e a política de ownership é outro estudo.

### Próxima ação e encerramento

Próxima ação documental concluída: preservar linhagem e opções da #174. Binding e eventual submissão do candidato são decisões posteriores, sem copiar arquivos de operador nesta rodada.

<a id="item-383"></a>

## P-E09 — [Decision][Pod 2/Package] Modelo de identidade de checkout, daemon e Compose (DEC-10)

Frente: minutas_publicadas. Encaminhamento: minuta_publicada_175_matriz_de_operacoes.

### Identidade e estado

P-E09 é minuta local de 11/10/2026, preservada para linhagem; PUBLICATION registra a representação pública luanmorenommaciel/apex#175 em 2026-10-11T04:24:35Z. Aberta no snapshot de 16/10; estado corrente e responsabilidade não inferidos desta data.

### Intenção e benefício

Intenção: escolher um modelo de identidade de checkout, daemon e projeto Compose (labels, nonce ou raiz canônica), base do guard E10 e do preflight de porta E11. Público: Pod 2 e operadores com vários checkouts. Ganho: distinguir stack própria de alheia.

### Feito, faltante e não comprovado

A publicação #175 acrescenta matriz de operações, cenários, compatibilidade e separação de isolamento/autenticação. Os recortes Compose confirmam apex-dev, apex-infra e apex-infra-otel-collector (a minuta omite infra no nome do Collector). O guard histórico #64 é antecedente; nomes fixos não provam ausência de qualquer proteção ou operação incorreta em runtime.

### Linhagem

Linhagem: C38 I3 e HARN-CTX/HARN-NS → registro E09 (DEC-10) → minuta P-E09 → #175 → duas rodadas Gemini (12 operações, duas opções) → decisão [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/P-E09.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/dev__docker-compose.yml.txt; fontes/batch-revalidated-fes-sources/infra__docker-compose.yml.sanitized.txt. Locadores: Minuta/#175, nomes Compose e separação das operações/estudos.

### Classe e limite da evidência

FATO OBSERVADO: textos e nomes nos recortes estáticos. RELATO: matriz posterior de operações e duas opções de isolamento. Não se mediu daemon, contexto, porta ou identidade real.

### Fluxo

Fluxo da minuta: decisão do modelo —(campos)→ Task-Spec do guard E10. Fluxo publicado: matriz de operações —(cenários)→ decisão fail-closed com compatibilidade —(plano de teste de recusa)→ guard posterior.

### Consequências e risco

Sem ação sobre a minuta, nada muda: a decisão vive na #175. O risco de usar a minuta seria escolher o modelo antes de listar as operações que precisam dele. Confiança alta.

### Alternativas e recomendação

Recomendado: catalogar a minuta como superada pela #175. Alternativa: manter a minuta como lista inicial de opções (labels, nonce, raiz canônica), sem uso operacional. Reversível.

### Dependências e paralelismo

O estudo de identidade não bloqueia #167/#174/#178. E10 requer contrato aceito para implementar a classificação; E11 pode estudar recusa de porta offline antes, mas chamá-la foreign exige identidade escolhida. Daemons distintos não isolam por si só portas compartilhadas do host.

### Plano e aceite propostos

Condição de não ação: não republicar. Nota consolidada: "P-E09 → #175 com matriz de operações, cenários e compatibilidade de stacks antigas".

### Comunicação entre responsáveis

Para outro pod: "A minuta de identidade de stacks virou a #175, que agora pede a matriz de operações e cenários de dois checkouts antes de decidir o modelo."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Assumir propriedade por nome ou isolamento só por daemon pode direcionar leitura/mutação a recurso alheio. Que caso o teste ainda não cobre? Nenhum cenário real de dois checkouts/contextos/portas foi executado; compatibilidade e confiança do modelo ainda precisam decisão. Como eu explicaria isso para outro pod? #175 decide evidência de identidade para operações; inventário offline pode seguir em paralelo aos reparos de interface, arquivo e endpoint.

### Próxima ação e encerramento

Próxima ação documental concluída: preservar #175, nome correto do Collector e distinção de dependências. Nenhuma identidade real foi escolhida ou recurso inspecionado.

<a id="item-384"></a>

## P-E13 — [Study][Pod 2/Infra] Rotação local de credencial ClickHouse

Frente: minutas_publicadas. Encaminhamento: minuta_publicada_176_procedimento_com_matriz.

### Identidade e estado

P-E13 é minuta local de 11/10/2026, preservada para linhagem; PUBLICATION registra a representação pública luanmorenommaciel/apex#176 em 2026-10-11T04:24:36Z. Aberta no snapshot de 16/10; estado corrente e responsabilidade não inferidos desta data.

### Intenção e benefício

Intenção: definir um procedimento suportado de rotação da credencial local do ClickHouse (in-place ou recriação), com evidência em runtime descartável e sem segredo no texto. Público: operadores locais. Ganho: rotação e recuperação reprodutíveis.

### Feito, faltante e não comprovado

A minuta parte de ausência de procedimento suportado, não revalidada no registro histórico; a #176 corrige para inventariar procedimentos existentes, sem declarar ausência universal. Acrescenta credencial antiga recusada quando aplicável, restart, preservação de dados e backup/restauração para recriação. Não há prova de rotação nesta rodada.

### Linhagem

Rascunho histórico de agosto → E13/defer → minuta → #176 com inventário e matriz → revisão documental. Estado de procedimentos externos e resultado de estudo não demonstrados.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/P-E13.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-revalidated-fes-sources/infra__docker-compose.yml.sanitized.txt. Locadores: Minuta/#176 e configuração/volume no recorte infra.

### Classe e limite da evidência

FATO OBSERVADO: diferenças de qualificação de ausência e critérios, configuração/volume no recorte infra. RELATO: rascunho histórico. Nenhuma credencial ou runtime acessado.

### Fluxo

Fluxo da minuta: estudo em runtime descartável —(procedimento com passos e rollback)→ documento. Fluxo publicado: inventário —(alternativas e matriz)→ procedimento com pré-condições e verificação —(relatório com versão)→ revisão.

### Consequências e risco

A minuta prevê cuidado com segredos, mas seu ponto de partida não comprova inexistência de procedimento. Apagar volume pode perder dados; não é sinônimo de rotação transparente nem resultado desta revisão.

### Alternativas e recomendação

Preservar a minuta como histórico da #176 e substituir sua premissa de ausência por inventário com alcance. Estudo documental disponível offline; execução descartável é outra camada de prova.

### Dependências e paralelismo

Inventário e comparação de procedimentos podem ocorrer offline sem #33 ou #62 concluídas. Experimento descartável é etapa posterior com escopo próprio; não bloqueia o estudo documental.

### Plano e aceite propostos

Condição de não ação: não republicar. Nota consolidada: "P-E13 → #176 com matriz de credencial nova/antiga, restart e preservação de dados".

### Comunicação entre responsáveis

Para outro pod: "A minuta de rotação de credencial virou a #176 com uma matriz que inclui preservação de dados e recusa da credencial antiga."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Tratar recriação/exclusão de volume como rotação pode perder dados e impedir rollback; presumir ausência de procedimento duplica trabalho. Que caso o teste ainda não cobre? Não houve rotação, recusa da credencial antiga, restart, restauração ou prova de preservação de dados. Como eu explicaria isso para outro pod? #176 começa por inventário e critérios; qualquer prova descartável é posterior e não implica tocar credencial real.

### Próxima ação e encerramento

Próxima ação documental concluída: preservar P-E13 → #176 com ausência qualificada e matriz. Nenhuma credencial foi rotacionada ou volume acessado.

<a id="item-385"></a>

## P-S15 — [Feature][Pod 3/Serve] F4.3: narrar AQE a partir de job_conf

Frente: minutas_publicadas. Encaminhamento: minuta_publicada_177_premissa_corrigida.

### Identidade e estado

P-S15 é minuta local de 11/10/2026, preservada para linhagem; PUBLICATION registra a representação pública luanmorenommaciel/apex#177 em 2026-10-11T04:24:37Z. Aberta no snapshot de 16/10; estado corrente e responsabilidade não inferidos desta data.

### Intenção e benefício

Intenção: narrar "o AQE fez X, sua config diz Y" a partir de job_conf. Público: Pod 3 e quem lê o diagnóstico. Ganho: explicação acionável sem mudar contrato.

### Feito, faltante e não comprovado

Confirmada a premissa antiga da minuta: Serve já contém JOB_CONF_SQL, ReadStore.job_conf e rota de recurso, portanto leitura não é lacuna universal. A #177 a reenquadra como estudo da narrativa, com configuração presente/ausente e sem defaults inventados ou causalidade presumida. Existência da leitura não comprova que diagnose a cruze com AQE.

### Linhagem

Linhagem: L4_PROPOSAL e SERVE-LEGS F4.3 → registro S15 (grep job_conf = 0 na a289e53) → #129 porta JOB_CONF (06/10) → minuta P-S15 com a premissa antiga (11/10) → #177 com a premissa corrigida → decisão [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/P-S15.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_mcp__ch.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_api__routes__resources.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/contract__job_conf.ddl.sql.txt. Locadores: Minuta/#177, JOB_CONF_SQL, ReadStore.job_conf e rota recursos.

### Classe e limite da evidência

FATO OBSERVADO: query, método e rota job_conf no recorte; texto publicado corrige a minuta. PROPOSTA: narração com origem e escopo explícitos. Nenhuma narração ou captura real executada.

### Fluxo

Fluxo da minuta: leitura de job_conf (que já existia) —(narração)→ Task-Spec —(testes offline)→ runtime. Fluxo publicado: mapear diagnose e captura —(exemplos com ausência)→ decisão de produto —(se implementar, testes negativos contra defaults inventados)→ runtime delimitado.

### Consequências e risco

Se executada pela minuta, alguém reimplementaria a leitura de job_conf já existente e trataria a feature como pronta para Task-Spec. A publicação evitou as duas coisas. Confiança alta.

### Alternativas e recomendação

Recomendado: catalogar a minuta como superada pela #177. Alternativa: nenhuma; a premissa errada impede usar a minuta como base técnica. Reversível.

### Dependências e paralelismo

Exemplos de narrativa podem ser estudados agora. Afirmação por stage/execução precisa vínculo efetivamente integrado e sem ambiguidade no consumidor; #115 já tem trabalho de atribuição, não é correto afirmar que o mapa inteiro inexiste ou que todo estudo espera sua conclusão.

### Plano e aceite propostos

Condição de não ação: não republicar. Nota consolidada: "premissa 'Serve não lê job_conf' desatualizada desde a #129; corrigida na #177, rebaixada a estudo".

### Comunicação entre responsáveis

Para outro pod: job_conf é legível no Serve/API; #177 pergunta como narrar junto a AQE com ausência e escopo honestos. Leitura existente não demonstra narrativa integrada.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Narrar causalidade ou default não capturado pode transformar correlação em diagnóstico falso, inclusive atribuindo decisão a stage errado. Que caso o teste ainda não cobre? Não se executou narrativa com captura real nem se verificou vínculo integrado entre execução, stage e mensagem. Como eu explicaria isso para outro pod? #177 estuda narrativa sobre leitura já existente; correlação e integração por stage são garantias a demonstrar no consumidor.

### Próxima ação e encerramento

Próxima ação documental concluída: preservar minuta → #177 e sua premissa corrigida. Exemplos e decisão de produto continuam disponíveis como estudo offline.

<a id="item-386"></a>

## PROP-L09-HARN-BINDING — [Feature][Pod 2/Harness] Repassar APEX_OTLP_ENDPOINT no alvo run-pathology

Frente: minutas_publicadas. Encaminhamento: minuta_publicada_178_propagacao_completa.

### Identidade e estado

PROP-L09-HARN-BINDING é minuta local de 11/10/2026, preservada para linhagem; PUBLICATION registra a representação pública luanmorenommaciel/apex#178 em 2026-10-11T04:24:38Z. Aberta no snapshot de 16/10; estado corrente e responsabilidade não inferidos dessa data.

### Intenção e benefício

Intenção: repassar APEX_OTLP_ENDPOINT no alvo run-pathology (e c3/c4 quando aplicável), para que a telemetria vá ao Collector escolhido, mantendo o default. Público: quem roda patologias contra outro Collector. Ganho: override de endpoint respeitado.

### Feito, faltante e não comprovado

Makefile confirma a falta de repasse no run-pathology, literais nos alvos c3/c4 e expansão imediata de docker network inspect na leitura. spark-defaults fixa o endpoint. O job skew_join e build_session lidos não traduzem APEX_OTLP_ENDPOINT para SparkConf; e2e_canonical.sh redefine a variável antes de usá-la no submit. Portanto um simples -e não demonstra propagação completa. #178 já pede precedência e separa propagação de entrega OTLP.

### Linhagem

Linhagem: registro L09 → minuta Kimi (11/10) → #178 com precedência e controle negativo → leitura Codex do caminho completo → decisão/PR [ausentes].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/PROP-L09-HARN-BINDING.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-public-sources/dev__Makefile.txt; fontes/batch-public-sources/dev__conf__spark-defaults.conf.txt; fontes/batch-public-sources/dev__scripts__e2e_canonical.sh.txt; fontes/batch-public-sources/dev__jobs__skew_join.py.txt; fontes/batch-public-sources/dev__common__session.py.txt. Locadores: Minuta/#178; Makefile integral, endpoint na linha 34 do defaults, skew_join/build_session e redefinição no e2e_canonical.sh.

### Classe e limite da evidência

FATO OBSERVADO: os caminhos estáticos nomeados e critérios publicados. INFERÊNCIA LIMITADA: o caminho skew_join/build_session lido precisa que alguma interface aplique o valor à configuração Spark. Não foi auditado todo job nem executado make, Docker, Spark ou Collector.

### Fluxo

Fluxo a comprovar futuramente: entrada explícita/default → regra de precedência → launcher → spark.apex.otlp.endpoint no submit/SparkConf. Entrega de spans ao Collector é prova distinta. Apenas exportar variável ou renderizar um fragmento não demonstra as duas garantias.

### Consequências e risco

Um teste apenas do -e pode passar enquanto o caminho lido conserva endpoint fixo. A lacuna é risco estático delimitado, sem demonstração de envio ao Collector errado. Confiança alta no recorte.

### Alternativas e recomendação

Preservar minuta → #178 e preparar desenho de precedência e captura de comando com isolamento real dos executáveis. Manter variável convertida pelo job ou --conf no launcher são alternativas a comparar; a escolha não foi feita aqui.

### Dependências e paralelismo

Estudo de propagação pode começar offline e em paralelo a #167/#174, sem esperar #175. Decisão de identidade e entrega OTLP são recortes separados. Não executar make -n supondo ausência de subprocessos, pois há expansão de shell na leitura do Makefile.

### Plano e aceite propostos

Nota consolidada: a #178 exige seguir a entrada até SparkConf; a minuta não deve virar duplicata. make -n sozinho não isola o docker network inspect da linha 7.

### Comunicação entre responsáveis

Para outro pod: #178 trata precedência até a configuração Spark. O comando precisa carregar o endpoint efetivo; receber uma variável no container e entregar OTLP são provas diferentes.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Repassar somente a variável pode conservar o endpoint fixo; usar make -n como isolamento ainda permite o shell expandido na leitura. Que caso o teste ainda não cobre? Não houve captura de argv, prova de configuração Spark, todos os jobs ou entrega OTLP; a leitura cobre os caminhos nomeados. Como eu explicaria isso para outro pod? A #178 decide a propagação até SparkConf com default preservado, independentemente da política ampla de ownership.

### Próxima ação e encerramento

Próxima ação documental concluída: preservar publicação e alcance dos caminhos lidos. O desenho e eventual implementação ficam como trabalho disponível; nenhum comando de produto foi renderizado ou executado nesta revisão.

<a id="item-387"></a>

## PROP-L10-VERIFY-RUNTIME — [Question][Pod 1/Verify] Verify deve usar executor_run_time_ms medido com fallback estimado?

Frente: minutas_publicadas. Encaminhamento: minuta_publicada_179_estudo_e_texto_separados.

### Identidade e estado

PROP-L10-VERIFY-RUNTIME é minuta local de 11/10/2026, preservada para linhagem; PUBLICATION registra a representação pública luanmorenommaciel/apex#179 em 2026-10-11T04:24:39Z. Aberta no snapshot de 16/10; estado corrente e responsabilidade não inferidos dessa data.

### Intenção e benefício

Estudar se executor runtime é evidência apropriada para W, com unidade, população e proveniência. A coluna declarada na migração não garante valor útil ou substituição semanticamente correta do bracket. Público: Verify e consumidores de suas previsões.

### Feito, faltante e não comprovado

models.py e predict.py conservam texto de coluna ausente; 039 declara Int64 DEFAULT 0 e atualiza a MV, enquanto Engine usa coluna positiva com fallback ao Map. Isso não prova schema aplicado nem medição útil em qualquer banco. #179 inclui correção de texto e estudo sem prometer equivalência com wall-clock ou ganho. O teste de matriz exige literalmente a frase antiga de models.py; removê-la precisa coordenar o guard. CL-02 só de predict.py é relato histórico, não execução desta revisão.

### Linhagem

Linhagem: drift verify_executor_runtime_claim_outdated → registro L10 (DEC-06) → minuta Kimi → #179 → patch local CL-02 só de predict.py → decisão [ausente].

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/PROP-L10-VERIFY-RUNTIME.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/verify__src__apex_verify__models.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/verify__src__apex_verify__predict.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/infra__sql__039_executor_runtime_additive.sql.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/engine__src__apex_engine__clickhouse.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/tests__test_telemetry_compatibility_matrix.py.txt. Locadores: Minuta/#179; models 38–42, predict 19–23/158, migração 039, fallback Engine e teste da matriz integral.

### Classe e limite da evidência

FATO OBSERVADO: afirmação interna obsoleta, DDL/MV, fallback Engine e asserção literal. PROPOSTA: política measured/estimated/unavailable. NÃO VERIFICADO: valores em banco, equivalência de W, implementação ou resultados de CL-02.

### Fluxo

Correção de texto → coordenar asserção da matriz preservando seu controle; estudo de unidade/população/proveniência → decisão sobre W → eventual seleção/fallback com critérios. Texto e fórmula podem avançar em escopos separados.

### Consequências e risco

Trocar a fórmula apenas porque a coluna existe pode converter default histórico zero em medição ou misturar populações. Corrigir models.py isoladamente quebra a asserção textual lida. Nenhum resultado de predictor foi reproduzido.

### Alternativas e recomendação

Preservar minuta → #179; preparar correção textual coordenada e estudo semântico em paralelo. Alternativas legítimas do estudo são usar medição, manter estimativa ou combinar limites com disponibilidade explícita.

### Dependências e paralelismo

O estudo pode começar offline sem aguardar resposta do owner ou #117/#162/#164/#180. Alterar fórmula ou contrato exige decisão apropriada; corrigir o texto requer coordenar o guard literal, sem esperar toda a matriz futura.

### Plano e aceite propostos

Nota consolidada: #179 separa semântica de W e correção textual; models.py coordena com a asserção antiga do teste. >0 é regra observada do Engine, não política já ratificada para Verify.

### Comunicação entre responsáveis

Para outro pod: há coluna declarada e texto interno desatualizado; isso justifica corrigir a descrição, mas a escolha de W continua estudo de unidade, população e ausência.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Tratar default zero como medição ou executor runtime como W equivalente pode produzir previsão sem semântica definida; corrigir o texto sem o guard quebra a asserção antiga. Que caso o teste ainda não cobre? Não foram testados schema aplicado, valores, seleção/fallback, população successful-task ou o candidato local citado. Como eu explicaria isso para outro pod? A #179 permite estudar W e corrigir texto agora; mudar o modelo é uma decisão posterior com proveniência e unidade explícitas.

### Próxima ação e encerramento

Próxima ação documental concluída: preservar #179 e dependência textual específica. Nenhuma fórmula, teste de produto ou matriz foi alterada ou executada.

<a id="item-388"></a>

## PROP-L13-MATRIX-UPDATE — [Docs][Cross-lane] Atualizar matriz de compatibilidade para topologia atual (Front, apex-api)

Frente: minutas_publicadas. Encaminhamento: minuta_publicada_180_absorve_l14.

### Identidade e estado

PROP-L13-MATRIX-UPDATE é minuta local de 11/10/2026, preservada para linhagem; PUBLICATION registra a representação pública luanmorenommaciel/apex#180 em 2026-10-11T04:24:40Z. Aberta no snapshot de 16/10; estado corrente e responsabilidade não inferidos dessa data.

### Intenção e benefício

Intenção: atualizar a matriz de compatibilidade (base, presença do Front, apex-api) e seu teste estático para a topologia atual. Público: todos os Pods. Ganho: gate estático que volta a representar a topologia.

### Feito, faltante e não comprovado

Matriz e teste lidos integralmente: matriz fixa base 847d7a0 e Front absent/external; manifesto/teste omitem Front/API. A minuta manda atualizar manifesto/teste, mas não determina apagar a história; a publicação torna sua preservação explícita e absorve L14. Comentário completo da #180 já registra duas rodadas, incluindo seis linhas de proveniência × Front/API, não matriz atual integrada. Front declara 0.5 e CONTRACT v0.6; divergência declarada não prova incompatibilidade runtime.

### Linhagem

Registro L13 → minuta → #180 com L14 agrupado → comentário de estudo parcial e segunda rodada com seis linhas → futura visão atual/teste integrados ainda não demonstrados. A publicação amplia critérios, sem prova de que a minuta necessariamente apagaria a base antiga.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/PROP-L13-MATRIX-UPDATE.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/docs__architecture__TELEMETRY-COMPATIBILITY-MATRIX.md.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/tests__test_telemetry_compatibility_matrix.py.txt; fontes/batch-revalidated-xldd-sources/code/front__src__contract__types.ts; fontes/batch-revalidated-xldd-sources/code/CONTRACT.md; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_api__routes__resources.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_mcp__ch.py.txt; fontes/batch-publication-current-sources/issue180-comments.json. Locadores: Minuta/#180, matriz/teste integrais, tipos Front, contrato, rotas/store e comentário completo capturado em 18/10.

### Classe e limite da evidência

FATO OBSERVADO: matriz histórica, manifesto/teste, versão declarada Front/contrato, rotas e comentário completo. RELATO: entregas locais das duas rodadas. NÃO VERIFICADO: conteúdo completo dessas entregas, teste atualizado integrado ou interoperabilidade runtime.

### Fluxo

Base histórica preservada → visão atual ou versão da matriz com fonte por aresta → categorias de evidência e inventário de proveniência → teste estático coerente. Estudo local relatado é insumo; não substitui integração nem runtime.

### Consequências e risco

Aplicar a visão histórica ao head atual omite Front/API. Atualizar sem preservar sua referência poderia perder contexto, mas a minuta não manda fazê-lo. Confiança alta na diferença de exigência textual; nenhuma perda real foi constatada.

### Alternativas e recomendação

Preservar minuta → #180 e preparar visão atual separada ou versionada com fontes por aresta. Reutilizar o estudo já relatado após conferir seus artefatos, evitando alegar que nada começou.

### Dependências e paralelismo

Atualização documental e desenho de checks podem seguir offline. #165/#179 coordenam asserções literais específicas, sem esperar a #180 inteira; #106 não é pré-requisito. Integração futura não transforma ausência em requisito de produto.

### Plano e aceite propostos

Nota consolidada: #180 explicita preservar história e inclui L14. Há duas rodadas de estudo relatadas; falta demonstrar a entrega integrada. Front 0.5 versus contrato v0.6 é divergência de declaração a interpretar.

### Comunicação entre responsáveis

Para outro pod: #180 acrescenta visão atual com Front/API e proveniência, preservando a base antiga. O estudo de seis linhas já foi relatado; isso não é matriz/teste integrados ou prova runtime.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Usar topologia antiga como atual omite consumidores; apagar sua ref perderia contexto, embora essa exclusão não esteja ordenada na minuta. Que caso o teste ainda não cobre? Não executamos o guard nem comprovamos integração da matriz nova, conteúdo completo dos estudos ou compatibilidade runtime entre declarações 0.5 e v0.6. Como eu explicaria isso para outro pod? A #180 preserva história e incorpora L14; já há estudo relatado, e a próxima entrega é a visão atual verificável com fontes por aresta.

### Próxima ação e encerramento

Próxima ação documental concluída: registrar linhagem, estudo já iniciado e limites. Nenhuma matriz de produto ou teste foi atualizado/executado nesta revisão.

<a id="item-389"></a>

## PROP-L14-PROVENANCE-GAPS — [Question][Cross-lane] Lacunas de proveniência A1 restantes (status, ambiente, decisões Memory) ainda existem?

Frente: minutas_disposicao. Encaminhamento: minuta_nao_publicada_agrupada_em_180.

### Identidade e estado

PROP-L14-PROVENANCE-GAPS é uma minuta local de 2026-10-11 (question, cross-pod, executor K-kimi), origem L14: "Lacunas de proveniência A1 restantes (status, ambiente, decisões Memory) ainda existem?". Não foi publicada: disposição grouped em PROP-L13-MATRIX-UPDATE, ou seja, na issue luanmorenommaciel/apex#180, com o motivo "Inventário de três superfícies de proveniência incorporado à atualização da matriz; evitar estudo amplo duplicado".

### Intenção e benefício

Intenção: confirmar por lane (Engine, Serve, Memory, Verify, Front, apex-api) se status/duração real de job, identidade de ambiente e registro de decisão da Memory ainda faltam. Público: cross-pod. Ganho: não transformar uma hipótese derivada do contrato em requisito.

### Feito, faltante e não comprovado

Agrupamento na #180 confirmado, com critério para as três superfícies. Comentário completo já relata seis linhas de proveniência × Front/API. Tipos Front mostram duração nullable; store diferencia dados de shape de duração de job; DDL run_outcomes possui configuração parcial e wall_clock_ms por shape. Isso é cobertura parcial no recorte, sem demonstrar status final, identidade completa ou ledger de decisão Memory em todas as lanes.

### Linhagem

Hipótese histórica A1/L14 → minuta condicional → grouped em #180 → estudo de seis linhas já relatado → confirmação por superfície/lane ainda a completar com fontes. Não há base para afirmar que nenhuma confirmação tinha começado até 18/10.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/PROP-L14-PROVENANCE-GAPS.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-publication-current-sources/issue180-comments.json; fontes/batch-revalidated-xldd-sources/code/front__src__contract__types.ts; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_mcp__ch.py.txt; fontes/batch-revalidated-xldd-sources/code/memory__sql__031_run_outcomes.sql. Locadores: Minuta, disposição grouped/#180, comentário completo, RunSummary, _run_rollup_sql e DDL run_outcomes.

### Classe e limite da evidência

FATO OBSERVADO: agrupamento, critério público, tipos/queries/DDL e comentário das duas rodadas. RELATO: estudo local das seis linhas. NÃO VERIFICADO: todas as lanes, persistência/produtor real ou ausência universal das superfícies.

### Fluxo

Fluxo da minuta: hipótese do contrato —(verificação por lane)→ relatório —(prioridade de produto)→ mantenedor. Após a disposição: o mesmo fluxo dentro do inventário da #180.

### Consequências e risco

Agrupar pode diluir o inventário e merece preservar seus três critérios visíveis; o comentário mostra trabalho iniciado. Falta de prova completa não é prova de ausência universal nem obrigação de criar novos campos.

### Alternativas e recomendação

Preservar grouped → #180; reconciliar estudo existente por campo e garantia antes de propor follow-up. Separar futuramente só um recorte confirmado e atômico, se necessário, evitando duplicação ampla.

### Dependências e paralelismo

Confirmação documental por lane pode começar/continuar offline em paralelo à visão atual de L13; não exige #106, captura real ou decisão prévia de mudar contrato. Priorizar implementação depois é decisão de produto.

### Plano e aceite propostos

Condição de não ação: não publicar a minuta. Nota consolidada: "L14 → #180 (grouped), critério de inventário das três superfícies de proveniência".

### Comunicação entre responsáveis

Para outro pod: L14 está na #180 e as seis linhas Front/API já foram estudadas segundo comentário; ainda se distinguem fonte por campo, cobertura parcial e prova real.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Converter hipótese derivada em ausência universal pode criar requisito desnecessário; chamar span de shape de duração final de job atribui semântica incorreta. Que caso o teste ainda não cobre? Não houve confirmação de todas as lanes, runtime/produtor/persistência nem auditoria completa de decisões Memory e identidade ambiental. Como eu explicaria isso para outro pod? L14 integra a #180; reaproveitar o estudo relatado por campo e distinguir cobertura parcial de garantia final antes de criar follow-ups.

### Próxima ação e encerramento

Próxima ação documental concluída: preservar grouped, reconhecer estudo já relatado e limitar ausência ao recorte. Nenhum campo de contrato ou estado público foi criado ou alterado.

<a id="item-390"></a>

## PROP-DD06-SKILL-SCOPE — [Feature][Método] Parametrizar escopo autorizado da skill apex-debug-diamond

Frente: minutas_tooling. Encaminhamento: minuta_tooling_ja_atendida_antes_da_minuta.

### Identidade e estado

PROP-DD06-SKILL-SCOPE é uma minuta local de 2026-10-11 (feature, método/tooling, executor K-kimi), origem DD06: "Parametrizar escopo autorizado da skill apex-debug-diamond". Não publicada (tooling fora do APEX). Owner: Augusto (a confirmar).

### Intenção e benefício

Intenção: tornar o escopo autorizado da skill um parâmetro explícito (diretório, remotes, política de push), em vez do escopo fixo de julho. Público: quem usa a skill no fluxo de PR atual. Ganho: skill utilizável sem violar suas próprias regras.

### Feito, faltante e não comprovado

A cópia de SKILL.md conferida com o índice de 18/10 já deriva repositório, checkout, base e ações do pedido/instruções; publicação exige autorização e destino verificado. Isso atende ao problema de escopo fixo. A minuta pede parâmetro explícito; equivalência suficiente entre derivação e esse parâmetro é decisão do dono, não aceite formal observado. Não se atribui a origem da minuta a um registro específico só pela cronologia.

### Linhagem

Registro histórico DD06 com escopo fixo → versão de SKILL.md indexada com mtime 10/10 → minuta condicional de 11/10 → confronto documental da cópia capturada. Mtime/hash identificam arquivo e captura; não são histórico Git completo ou autorização.

### Fontes e corte

Fontes efetivamente lidas nesta revalidação: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; fontes/batch-proposals-review-sources/PROP-DD06-SKILL-SCOPE.md; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/issues_all.json; fontes/batch-proposals-review-sources/debug-diamond__SKILL.md; fontes/batch-claude-registro-propostas-sources/claude/fontes/INDICE-FONTES-LOCAIS.json. Locadores: Minuta/MATRIX DD06, SKILL.md integral e índice de hash/mtime capturado em 18/10.

### Classe e limite da evidência

FATO OBSERVADO: texto atual da cópia, metadados datados e diferença entre derivação e parâmetro nomeado. INFERÊNCIA: a dor de escopo fixo está atendida na redação. NÃO VERIFICADO: aceite formal do dono ou fluxo de uso real.

### Fluxo

Fluxo da minuta: escopo como parâmetro —(invocação)→ skill. Fluxo atual: pedido e instruções do repositório —(derivação)→ escopo —(publicação só com autorização)→ ação.

### Consequências e risco

O escopo fixo não aparece no arquivo lido. Aplicar literalmente a minuta pode acrescentar interface desnecessária, mas decidir que derivação basta pertence ao dono. Não se declara arquivamento efetivamente executado.

### Alternativas e recomendação

Preservar minuta como candidata a não ação quanto ao escopo fixo; decidir separadamente se parâmetro explícito traz benefício. Registro do escopo efetivo pode ser estudado em DD10 sem mudar a invocação.

### Dependências e paralelismo

Estudo disponível offline sem dependência do APEX. Alteração da skill ou publicação em destino escolhido exige escopo próprio; não decorre deste parecer.

### Plano e aceite propostos

Nota documental: escopo fixo ausente; derivação instalada atende à intenção, com diferença de forma ainda disponível à decisão. Não aplicar nem arquivar automaticamente tooling nesta revisão.

### Comunicação entre responsáveis

Para outro pod: a skill lida já usa o pedido para determinar escopo; a minuta não justifica repetir a correção, e parâmetro explícito é escolha residual.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Assumir autorização pelo nome de branch/remote permite operar fora do pedido; acrescentar parâmetro sem necessidade pode criar outra fonte divergente de escopo. Que caso o teste ainda não cobre? Não se testou invocação real, aceite formal do dono ou equivalência operacional entre parâmetro explícito e derivação. Como eu explicaria isso para outro pod? DD06 já está atendido na redação quanto ao escopo fixo; resta decidir se registrar ou parametrizar explicitamente melhora o uso.

### Próxima ação e encerramento

Próxima ação documental concluída: registrar atendimento da redação e escolha residual. Nenhum arquivo instalado, repositório externo ou estado de arquivamento foi alterado.

