# Fichas documentais — lote 3

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-021"></a>

## #168 — [Study][Pod 2] Avaliar caudas de duração muito pequenas antes de propor piso absoluto

Frente: engine_evidencia. Encaminhamento: estudo_adiar_limiar_ate_evidencia.

### Identidade e estado

#168 — [Study][Pod 2] Avaliar caudas de duração muito pequenas antes de propor piso absoluto. Autor gustocezar; gustocezar; aberta na consulta de 16/10/2026 18:29:24 UTC. O assignee histórico não ratifica owner ou prazo para a próxima entrega. Corte técnico c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Decidir se uma cauda extrema em escala absoluta pequena deve ser filtrada ou apenas contextualizada, preservando atrasos acionáveis e evitando um piso arbitrário.

### Feito, faltante e não comprovado

Confirmei guards de 100 tasks, 100 amostras, p50 positivo, max/p50 > 10 e ausência de finding do skew watcher; não há guard de piso absoluto. Os comentários relatam grade de 23 casos e contrato ilustrativo de corpus com oito códigos de insuficiência/três exemplos sintéticos. Recomendação histórica: adiar o número até corpus com contexto e variação entre runs.

### Linhagem

E18 → P-E18 → #168; detector #127 é antecedente e #123 trata sua integração. Estudos C3 e corpus relatados em 11/10 não alteraram detector. Nenhuma medição real ou decisão de threshold foi apresentada nessa sequência.

### Fontes e corte

Fontes lidas: fontes/batch-public-sources/issue-168.md; fontes/current-open-issues.json; _build/input-registro.json; fontes/lote2-engine__src__apex_engine__watchers__tail_outlier.py.txt:15. Corpos/comentários preservados do snapshot 16/10/2026; código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Recibos novos de código em batch-public-sources/*.json registram 17/10/2026 00:47 UTC; não atualizam o estado das issues. Linhas citadas usam os arquivos .txt/.md correspondentes.

### Classe e limite da evidência

FATO OBSERVADO: condições no evaluate. RELATO HISTÓRICO: estudos/JSON conferidos em 11/10. INFERÊNCIA: razão alta em milissegundos pode ser pouco acionável; não é falso positivo observado. PROPOSTA: estudo de sensibilidade antes da política.

### Fluxo

População e durações → guards atuais → finding; corpus com escala/contexto/variação → comparação de políticas → decisão do mantenedor. A primeira seta é leitura de código; o estudo é proposto e não representa experimento já executado.

### Consequências e risco

Sem contexto, a severidade pode exagerar pequena duração; com piso arbitrário, pode ocultar problema real em job sensível. A direção dos riscos é plausível, sem frequência/probabilidade empírica. Coletar apenas exemplos extremos enviesaria a decisão.

### Alternativas e recomendação

Recomendo manter a regra durante o estudo e acrescentar contexto à avaliação. Comparar manter, contextualizar sem suprimir e introduzir limiar sustentado pelo corpus. A última opção altera recall; se aprovada, versionar rationale e permitir revisão. Não usar um valor escolhido pelo revisor como padrão.

### Dependências e paralelismo

Precisa de corpus sanitizado com unidades/população e contribuição de owners de workloads. Pode correr paralelo à apresentação #166 e ao gate #123; não bloquear essas correções esperando a decisão do piso. Harmonizar população com #169 sem afirmar que esse estudo escolhe seu seletor.

### Plano e aceite propostos

Revisar o contrato ilustrativo do corpus; incluir mesma razão em várias escalas, casos abaixo/igual/acima de 100 amostras e 10x, p50 zero e skew já reconhecido; comparar ruído evitado e casos ocultados; descrever incerteza entre execuções. Saída mínima: relatório de sensibilidade e decisão implementar/adiar/rejeitar. Testes futuros devem discriminar cada guard, sem chamar sintético de medição Spark.

### Comunicação entre responsáveis

Explicar que o finding já existe e que a questão é relevância absoluta. Identificar cada linha como real ou sintética, com população e contexto; comunicar que nenhum threshold foi aprovado.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Um piso absoluto igual para todos os jobs poderia ocultar atraso real em job sensível, e escolhê-lo sem corpus seria arbitrário. Que caso o teste ainda não cobre? — Falta comparar a mesma razão max/p50 em escalas diferentes, inclusive cauda curta com alto impacto total, e os limites de 100 amostras, 10x e p50 zero; casos sintéticos não são medição Spark. Como eu explicaria isso para outro pod? — O finding já existe e a questão é relevância absoluta; mostrar contexto sem suprimir o finding é uma das opções em comparação, e nenhum threshold foi aprovado.

### Próxima ação e encerramento

Owner Engine/Pod 2 a confirmar: receber corpus sanitizado e contrato de amostragem; devolver relatório e recomendação ao mantenedor. O estudo pode encerrar com adiamento/rejeição fundamentados; implementação só após decisão, sem tornar a própria existência da issue uma autorização de threshold.

<a id="item-022"></a>

## #169 — [Decision][Cross-pod] Definir seleção de tentativa e população de métricas entre consumidores

Frente: consumidores_telemetria. Encaminhamento: decisao_de_contrato_e_plano_de_migracao.

### Identidade e estado

#169 — [Decision][Cross-pod] Definir seleção de tentativa e população de métricas entre consumidores. Autor gustocezar; sem assignee; aberta na consulta de 16/10/2026 18:29:24 UTC. O assignee histórico não ratifica owner ou prazo para a próxima entrega. Corte técnico c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Fazer tentativa, métricas e população representarem a mesma observação entre Engine, Serve, Front e Memory. O ganho é evitar diagnósticos e comparações incompatíveis sobre o mesmo stage.

### Feito, faltante e não comprovado

O offline do Engine escolhe tupla (stage_attempt, ts); sua SQL combina max(stage_attempt) e argMax(..., ts). Serve STAGES_SQL usa argMax(stage_attempt, ts), enquanto CONSOLE_STAGES_SQL combina max com métricas por ts. Memory reduz por ts e calcula task_time_ms com p50 legado. São diferenças de implementação observadas; o efeito em produção não foi medido nesta revisão.

### Linhagem

E24, S14, S19 → P-DEC23 → #169. O registro preserva fixtures históricas sintéticas com divergências, sem recibos revalidados aqui. #142 mudou população no Verify, não define automaticamente a seleção comum. #115 é identidade execution→stage; #117 é atribuição de tratamento/piso e não escolhe este desempate.

### Fontes e corte

Fontes lidas: fontes/batch-public-sources/issue-169.md; fontes/current-open-issues.json; _build/input-registro.json; fontes/main-clickhouse.txt:65; fontes/main-clickhouse.txt:496; fontes/lote2-serve__src__apex_mcp__ch.py.txt:56; fontes/lote2-serve__src__apex_mcp__ch.py.txt:614; fontes/batch-public-sources/memory__src__apex_memory__clickhouse.py.txt:44. Corpos/comentários preservados do snapshot 16/10/2026; código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Recibos novos de código em batch-public-sources/*.json registram 17/10/2026 00:47 UTC; não atualizam o estado das issues. Linhas citadas usam os arquivos .txt/.md correspondentes.

### Classe e limite da evidência

FATO OBSERVADO: seletores SQL/offline citados. RELATO HISTÓRICO: resultados sintéticos no registro canônico. INFERÊNCIA sustentada pelos seletores: maior tentativa pode diferir do evento com ts mais recente. PROPOSTA/DECISÃO PENDENTE: contrato comum, fallback histórico e política de dados persistidos.

### Fluxo

Eventos (job, stage, tentativa, timestamp, população) → seletor por consumidor → métricas/findings/run_outcomes → tela e comparação. Fixture com ordem invertida e empate → decisão sobre a chave de seleção → mudanças de consumidores. Fluxo estático; não é cadeia runtime certificada.

### Consequências e risco

O rótulo da tentativa pode descrever uma linha e seus percentis outra; a população legada pode mudar vencedor de comparação. Alta confiança no potencial de divergência por leitura; incidência e severidade em Spark real não quantificadas. Alterar só a SQL pode deixar memória histórica com semântica anterior.

### Alternativas e recomendação

Comparar seleção por maior tentativa seguida de ts, por evento mais recente e por outra chave contratada. Recomendo decidir chave/desempate antes de harmonizar leitores. Um helper comum reduz divergência, mas SQL e offline ainda exigem controles independentes; reprocessar run_outcomes ou versionar novas linhas têm custos distintos.

### Dependências e paralelismo

Decisão entre owners Engine/Serve/Memory/Front; compatibilidade e possível migração de run_outcomes são gates humanos. Inventário e fixtures correm em paralelo; mudanças que prometem paridade dependem da política. Não impor #115 como bloqueio de toda seleção por tentativa.

### Plano e aceite propostos

Inventariar consultas e chaves; criar dados que invertam ordem de tentativa/ts, empatem ts, incluam failed/killed e ausência successful; definir qual linha deve vencer e como preservar histórico; alterar uma superfície por PR; comparar outputs offline/SQL/consumidores sob a mesma fixture. Aceite: tentativa/métricas coerentes, fallback explícito, empate determinístico acordado e plano para memória persistida. Prova sintética continua separada de Spark real.

### Comunicação entre responsáveis

Explicar diferença entre identidade SQL, tentativa e população. Publicar matriz antes/depois com exemplo que distingue os seletores; não usar comentários dizendo latest attempt como prova de equivalência.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Usar só o timestamp pode escolher um evento cujo stage_attempt não é o maior, e então o rótulo de tentativa descreveria uma linha e os percentis outra. Que caso o teste ainda não cobre? — Há caracterização histórica, inclusive casos C5/C6r/C9. Falta ratificar a política e conferir seus controles nas superfícies integradas; não se conclui que fixtures sejam inexistentes. Como eu explicaria isso para outro pod? — Engine, Serve, Front e Memory escolhem tentativa e população de formas diferentes, como max(stage_attempt) combinado com argMax por ts; a decisão é qual chave e desempate valem para todos, com efeito em produção ainda não medido.

### Próxima ação e encerramento

Owners dos consumidores a confirmar: entrada matriz dos seletores e fixtures históricas identificadas; saída decisão de desempate/população e sequência de mudanças/migração. Encerrar a decisão com registro explícito e ligar implementação separada, ou encerrar o conjunto somente após provas acordadas; não afirmar que paridade já existe.

<a id="item-023"></a>

## #170 — [Decision][Pod 2 / Infra] Definir reaplicação de DDL e o alcance de verify-ddl

Frente: infra_migracoes. Encaminhamento: decisao_operacional_e_limites_do_verificador.

### Identidade e estado

#170 — [Decision][Pod 2 / Infra] Definir reaplicação de DDL e o alcance de verify-ddl. Autor gustocezar; sem assignee; aberta na consulta de 16/10/2026 18:29:24 UTC. O assignee histórico não ratifica owner ou prazo para a próxima entrega. Corte técnico c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Definir garantias reais de reaplicação de DDL e do verify-ddl, para operadores não confundirem schema aparentemente alinhado com segurança de migração e ingestão.

### Feito, faltante e não comprovado

apply_ddl.sh reaplica arquivos ordenados e declara always safe/no-op; o verificador enumera sete tabelas, remove DEFAULT/MATERIALIZED/ALIAS/COMMENT/CODEC/TTL do tipo esperado e compara nome/tipo. O guard de alvo de MV existe. O registro E22/E23 relata fixture histórica 034→039 e controles de propriedades ignoradas; não reexecutei nem reaceitei esses resultados.

### Linhagem

E22 (janela de evolução) + E23 (alcance do checker) → P-DEC25 → #170. #147/#72 cobrem existência de destino de MV; #109 trata reconciliação declarada/runtime. Esses antecedentes não garantem migração sem janela nem cobertura de toda semântica DDL.

### Fontes e corte

Fontes lidas: fontes/batch-public-sources/issue-170.md; fontes/current-open-issues.json; _build/input-registro.json; fontes/batch-public-sources/infra__scripts__apply_ddl.sh.txt:10; fontes/batch-public-sources/infra__scripts__verify_ddl.py.txt:31; fontes/batch-public-sources/infra__scripts__verify_ddl.py.txt:124; fontes/batch-public-sources/infra__sql__039_executor_runtime_additive.sql.txt:5. Corpos/comentários preservados do snapshot 16/10/2026; código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Recibos novos de código em batch-public-sources/*.json registram 17/10/2026 00:47 UTC; não atualizam o estado das issues. Linhas citadas usam os arquivos .txt/.md correspondentes.

### Classe e limite da evidência

FATO OBSERVADO: laço de aplicação, comentário e comparação de colunas. RELATO HISTÓRICO: testes locais de migração e fixture sintética no registro. INFERÊNCIA: o status final não prova segurança durante ingestão. DECISÃO PENDENTE: coordenação de ingestão e extensão ou limitação explícita do verificador.

### Fluxo

Arquivos SQL ordenados → alterações no store; ingestão concorrente → linhas durante essas alterações; DESCRIBE → nomes/tipos → verify-ddl. Política operacional → janela/rollback/backfill. Fluxo de código observado; efeitos da janela sob carga não foram medidos.

### Consequências e risco

Um checker verde pode conviver com DEFAULT, TTL, SETTINGS ou query de MV divergentes; a declaração de reaplicação sempre segura excede o que o checker certifica. Não se conclui perda de dados de produção; risco de janela deve ser medido no ambiente relevante.

### Alternativas e recomendação

Recomendo primeiro delimitar a garantia atual e decidir política de migração. Comparar manter checker de nomes/tipos, ampliar por propriedades ou criar checker semântico separado. O separado preserva responsabilidade e reduz falsa universalidade; ampliar requer casos negativos por nova garantia. Coordenação da ingestão deve considerar pausa, atomicidade disponível e backfill, sem escolher no escuro.

### Dependências e paralelismo

Owner Infra e dono da ingestão decidem garantia, janela e rollback. Documentar limites pode correr em paralelo à análise de migrações. Prova runtime futura requer store próprio e cenário decidido; #147 não substitui esse aceite nem precisa ser refeito.

### Plano e aceite propostos

Classificar SQLs como no-op, adição ou mudança de query; revisar a frase always safe; produzir matriz fresh/migrado com ingestão e retomada; escolher checker; especificar negativos de DEFAULT/TTL/SETTINGS/MV e tipos/colunas que já devem falhar. Se houver mudança, primeira entrega deve documentar garantia e testar apenas a propriedade adicionada; prova da janela é outro recibo. Aceite: nenhuma afirmação de migração segura baseada apenas em nome/tipo.

### Comunicação entre responsáveis

Explicar ao operador o que um verde cobre, o que exige uma migração controlada e como recuperar. Relatos de fixture devem manter versão, base e ausência de produção.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Reaplicar DDL durante a ingestão pode alterar o store enquanto linhas chegam, e a frase always safe/no-op promete mais do que o verify-ddl certifica, já que ele compara só nome e tipo das colunas. Que caso o teste ainda não cobre? — O checker ignora DEFAULT, TTL, SETTINGS, CODEC e a query de MV, então um verde convive com essas divergências; a fixture 034→039 do registro é relato histórico, não reexecutado aqui. Como eu explicaria isso para outro pod? — Um verde do verify-ddl mostra nomes e tipos alinhados no estado final; idempotência desse estado não é segurança de cada etapa durante a ingestão, e a política de janela, rollback e backfill cabe ao owner Infra.

### Próxima ação e encerramento

Owner Infra a confirmar: receber classificação dos SQLs e escopo observado do checker; devolver política e alternativa escolhida. Encerrar a decisão com garantia/limites e plano verificável, sem executar migração em store existente nesta revisão.

<a id="item-024"></a>

## #171 — [Decision][Pods 1 e 3] Definir exposição do OpenAPI e quem guarda o token da API v1

Frente: api_seguranca_implantacao. Encaminhamento: decisao_de_politica_por_perfil.

### Identidade e estado

#171 — [Decision][Pods 1 e 3] Definir exposição do OpenAPI e quem guarda o token da API v1. Autor gustocezar; sem assignee; aberta na consulta de 16/10/2026 18:29:24 UTC. O assignee histórico não ratifica owner ou prazo para a próxima entrega. Corte técnico c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Explicitar quem pode ver docs/schema e quem guarda o token da API v1, por perfil local e compartilhado. O benefício é uma fronteira de confiança entendida pelos operadores e consumidores.

### Feito, faltante e não comprovado

O middleware aplica autenticação ao prefixo /v1 com exceções públicas; fora do prefixo, inclusive docs/OpenAPI, encaminha ao app. nginx encaminha /v1 sem injetar Authorization nesse bloco. Isso não demonstra comprometimento nem garante que o app exponha todas as rotas de docs em todo deploy. O corpo da issue preserva essas escolhas como decisões abertas.

### Linhagem

S05 (docs/schema) + S06 (custódia do token) → P-DEC08 → #171; origem pública #129. #122 decide Ask/BFF v2 e é fronteira distinta. Não há decisão nova do mantenedor nos comentários preservados desta issue.

### Fontes e corte

Fontes lidas: fontes/batch-public-sources/issue-171.md; fontes/current-open-issues.json; _build/input-registro.json; fontes/batch-public-sources/serve__src__apex_api__auth.py.txt:74; fontes/batch-public-sources/front__nginx.conf.txt:43. Corpos/comentários preservados do snapshot 16/10/2026; código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Recibos novos de código em batch-public-sources/*.json registram 17/10/2026 00:47 UTC; não atualizam o estado das issues. Linhas citadas usam os arquivos .txt/.md correspondentes.

### Classe e limite da evidência

FATO OBSERVADO: regra de admissão e configuração do proxy. RELATO HISTÓRICO: escolhas abertas descritas pela #129, conforme issue. DECISÃO PENDENTE: exposição por perfil e custódia/renovação. Ausência de injeção no nginx não implica ausência de qualquer autenticação no cliente.

### Fluxo

Browser → requisição same-origin → nginx → API /v1 → JSON ou 401; cliente de schema → rota fora do gate /v1 → aplicação. Política de token → fornecimento/armazenamento/renovação. Fluxo estático da fronteira, sem navegação ou teste de acesso executado.

### Consequências e risco

Operador pode presumir schema protegido ou colocar token no browser sem avaliar acesso compartilhado. Expor schema, por si, não comprova exposição de dados. A adequação depende do perfil e ameaça acordados; não classifico automaticamente como vulnerabilidade.

### Alternativas e recomendação

Comparar schema público versus protegido, e token no cliente versus proxy. Recomendo matriz por perfil antes de alterar código. Proxy evita distribuir token de backend ao browser, mas exige autenticar/controlar o acesso ao próprio proxy; apenas injetar token não cria autorização de usuários. Cliente é simples no uso local, com limites de exposição documentados.

### Dependências e paralelismo

Mantenedor/owner API define perfis e política; Front e operação participam da custódia. #172 pode caracterizar o perfil existente em paralelo, identificando a política usada. Não depender de escolher ou implementar Ask/BFF v2.

### Plano e aceite propostos

Listar rotas, exceções e perfis; definir emissor/armazenamento/renovação do token e acesso ao proxy; escolher política; planejar casos autorizado, ausente e inválido, 401 sem consulta ao store, docs conforme perfil e health público conforme contrato. Primeira entrega é decisão com exemplos sanitizados; qualquer delta posterior deve preservar rotas não alteradas e nunca embutir segredo.

### Comunicação entre responsáveis

Explicar diferença entre exposição de contrato OpenAPI e acesso a dados. Documentar onde o token vive e o que o proxy autentica; propostas não devem conter tokens, `.env` ou logs de credenciais.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Fazer o proxy injetar um token para qualquer visitante não criaria autorização de usuários; só moveria o segredo, e o acesso ao próprio proxy continuaria sem controle. Que caso o teste ainda não cobre? — A autenticação vale para o prefixo /v1; docs e OpenAPI fora dele seguem para o app, e a custódia e renovação do token estão sem política; nenhum teste de acesso foi executado. Como eu explicaria isso para outro pod? — Expor o contrato OpenAPI não é o mesmo que expor dados, e a ameaça muda entre localhost e ambiente compartilhado; a decisão é uma matriz por perfil de quem vê o schema e onde o token vive.

### Próxima ação e encerramento

Owner API/mantenedor a confirmar: receber matriz de fronteira e alternativas; saída é política versionada por perfil e plano de verificação. Encerrar a decisão com responsáveis e limites claros; implementar só o comportamento aprovado, sem declarar incidente inexistente.

<a id="item-025"></a>

## #172 — [Test][Pods 1 e 3] Validar o perfil HTTP da Console no nginx e no navegador

Frente: front_operacao. Encaminhamento: prova_de_integracao_http_e_browser.

### Identidade e estado

#172 — [Test][Pods 1 e 3] Validar o perfil HTTP da Console no nginx e no navegador. Autor gustocezar; sem assignee; aberta na consulta de 16/10/2026 18:29:24 UTC. O assignee histórico não ratifica owner ou prazo para a próxima entrega. Corte técnico c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Provar o percurso que o usuário usa em DATA_SOURCE=http: imagem da Console, proxy /v1 e renderização das telas com estados honestos. Isso cobre uma fronteira que uma API validada isoladamente não certifica.

### Feito, faltante e não comprovado

O bloco nginx /v1 existe na fonte. O corpo #172 registra que #129 tinha prova API/curl e faltava imagem/browser naquele momento; reconhece evidência posterior API/MCP/ClickHouse na #156. As fichas das PRs #157/#158/#159 distinguem testes em processo e gate de paridade da prova visual. Nenhuma evidência de browser foi reexecutada ou certificada nesta ficha.

### Linhagem

S03 (imagem/proxy) + S04 (renderização) → P-R129 → #172. #129 é antecedente; #156 e suas PRs tratam paridade/provas de outros percursos. S02 permanece ligado à prova da API na #156. #171 decide token; #122 é Ask/BFF, fora do recorte.

### Fontes e corte

Fontes lidas: fontes/batch-public-sources/issue-172.md; fontes/current-open-issues.json; _build/input-registro.json; fontes/batch-public-sources/front__nginx.conf.txt:43; B-FICHAS-PRS.md. Corpos/comentários preservados do snapshot 16/10/2026; código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Recibos novos de código em batch-public-sources/*.json registram 17/10/2026 00:47 UTC; não atualizam o estado das issues. Linhas citadas usam os arquivos .txt/.md correspondentes.

### Classe e limite da evidência

FATO OBSERVADO: configuração nginx em SHA fixado e escopo público da issue. RELATO HISTÓRICO: provas API e lacuna original. PROPOSTA: inventário de recibos posteriores, depois apenas as provas de proxy/browser ainda necessárias. Não converter falta de prova consultada em prova de falha.

### Fluxo

Navegador → GET same-origin /v1 → nginx da imagem → API → ClickHouse → JSON/ausência/erro → estado visual. Rota estática observada; sequência integrada é a prova a produzir, com fonte de dados explicitamente http.

### Consequências e risco

API verde pode coexistir com configuração de imagem, proxy ou renderização quebrados. Impacto potencial direto no usuário, probabilidade não medida. Retestar todos os tools sem avaliar recibos anteriores consome esforço e ainda pode deixar browser descoberto.

### Alternativas e recomendação

Recomendo smoke de poucas telas representativas mais estados data/empty/error/indisponível, com recibos por rota. Alternativa: E2E amplo de todas as telas, com maior custo e cobertura; mocks de browser isolados são rápidos, mas não provam nginx/API. Não substituir prova integrada por screenshot de fixture sem registrar o recorte.

### Dependências e paralelismo

Precisa de árvore/imagem identificadas, perfil HTTP configurado e ambiente próprio. Reutilizar recibos API somente quando blobs/escopo forem equivalentes; #171 só bloqueia mudança de política, não caracterização identificada do perfil atual. Pod 1 valida UI e Pod 3 a resposta/API.

### Plano e aceite propostos

Inventariar recibos de #156/#129 e PRs; selecionar rotas e casos restantes; fixar commit, imagem, DATA_SOURCE e política de token; verificar request passando por nginx e estado renderizado; repetir com vazio, erro textual e API indisponível; listar rotas não exercitadas e cleanup próprio. Aceite: ausência não vira zero, erro não vira tela vazia, perfil não recai silenciosamente em fixture. Falhas confirmadas viram follow-up delimitado.

### Comunicação entre responsáveis

Anexar evidência sanitizada com requisição, resposta e estado visual do mesmo caso; declarar rotas não cobertas e separar leitura direta ClickHouse de HTTP. O texto desta revisão é plano, não execução.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Se a Console caísse silenciosamente em fixture com DATA_SOURCE=http, uma API verde conviveria com imagem, proxy ou renderização quebrados sem ninguém perceber. Que caso o teste ainda não cobre? — Nenhuma evidência de browser foi reexecutada: faltam a passagem pelo nginx /v1 e os estados vazio, erro textual e API indisponível na mesma árvore; recibos da #156 e da #129 só se reaproveitam quando blobs e escopo forem equivalentes. Como eu explicaria isso para outro pod? — A prova da API isolada não certifica o percurso do usuário; o que falta é ver a requisição passar pelo nginx da imagem e o estado renderizado do mesmo caso, sem reabrir entregas de API já comprovadas.

### Próxima ação e encerramento

Owners Front/Serve a confirmar: entrada inventário de recibos e configuração identificada; saída pacote mínimo de prova nginx/browser. Encerrar quando os casos acordados forem observados nessa árvore e as exclusões estiverem documentadas; não reabrir entregas API já comprovadas por ausência de screenshot.

<a id="item-026"></a>

## #173 — [Study][Pods 2 e 3] Auditar a seleção de database ClickHouse por consumidor

Frente: store_e_consumidores. Encaminhamento: estudo_de_contrato_por_consumidor.

### Identidade e estado

#173 — [Study][Pods 2 e 3] Auditar a seleção de database ClickHouse por consumidor. Autor gustocezar; sem assignee; aberta na consulta de 16/10/2026 18:29:24 UTC. O assignee histórico não ratifica owner ou prazo para a próxima entrega. Corte técnico c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Definir quais lanes suportam database configurável e evitar que configuração do client aponte para um banco enquanto SQL executável lê outro. O ganho é previsibilidade para quem opera perfis fora do default apex.

### Feito, faltante e não comprovado

Confirmei consultas Memory qualificadas com apex.spark_events, apex.plan_memory, apex.run_outcomes e apex.job_conf. Engine conecta pelo settings.database, passa esse banco ao preflight e usa escrita explícita; Serve usa configured_database no client/store e SQL sem qualificação nos trechos lidos. Isso confirma diferenças de estratégia; não é inventário integral de Verify nem prova de falha operacional.

### Linhagem

E04 → P-E04 → #173. #129 e #131 são antecedentes de configuração/preflight, não implementação deste estudo. #154/#155 protegem coerência das colunas consultadas, escopo distinto. Contagens históricas de literais por lane não foram transportadas para esta base.

### Fontes e corte

Fontes lidas: fontes/batch-public-sources/issue-173.md; fontes/current-open-issues.json; _build/input-registro.json; fontes/batch-public-sources/memory__src__apex_memory__clickhouse.py.txt:72; fontes/main-clickhouse.txt:317; fontes/lote2-serve__src__apex_mcp__ch.py.txt:1268. Corpos/comentários preservados do snapshot 16/10/2026; código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Recibos de código em batch-public-sources/*.json preservam URL e observed_at; não atualizam o estado das issues. Linhas citadas usam os arquivos .txt/.md correspondentes.

### Classe e limite da evidência

FATO OBSERVADO: literais SQL e configuração de Engine/Serve citados. RELATO HISTÓRICO: inventários anteriores do E04, sem reutilizar totais. PROPOSTA: matriz por query e perfil suportado. INFERÊNCIA: configurar banco alternativo pode ser ineficaz em consultas qualificadas; só constitui defeito se o perfil for prometido.

### Fluxo

Operador → configuração de database → client/sessão; SQL qualificada → banco literal ou SQL sem qualificação → banco da sessão → leitura/escrita. Preflight deve observar o mesmo destino. Fluxo estático; perfis e política por lane ainda exigem decisão.

### Consequências e risco

Leitura e escrita em bancos distintos podem produzir ausência aparente ou mistura de resultados. Uma substituição textual global também pode afetar docs, SQL normativa e binding. A divergência de estratégia é observada; incidência e validade de banco alternativo para cada lane ainda não determinadas.

### Alternativas e recomendação

Recomendo inventariar e decidir suporte antes de trocar literais. Alternativas: manter apex obrigatório e validar configuração; usar banco de sessão consistentemente; parametrizar identificadores com validação específica onde necessário. A primeira restringe implantação, a segunda simplifica SQL, a terceira exige controle de identificador e não equivale a binding de valores.

### Dependências e paralelismo

Owners Engine/Memory/Verify/Serve definem os perfis. O inventário pode avançar sem #154/#155 nem refazer #129; mudança de contrato comum depende da decisão. Não exigir migração DDL apenas porque há literal.

### Plano e aceite propostos

Listar cada consulta e fábrica de client, distinguindo comentário, SQL e escrita; incluir Verify ainda não auditado nesta ficha; confrontar as promessas dos perfis; decidir fixo/configurável por lane. Se aprovado, mudar uma lane por vez com controles de banco não padrão, preflight no mesmo destino e valores ainda vinculados. Aceite do estudo: matriz completa e decisão; prova de runtime separado só se necessária ao perfil.

### Comunicação entre responsáveis

Explicar que literal não significa bug por si e que configurar um client não muda SQL qualificada. Na eventual PR, mostrar consultas afetadas e caso negativo de leitura no banco errado, sem divulgar credenciais.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Trocar todas as ocorrências de apex por texto afetaria docs, SQL normativa e binding de uma vez, sem decidir quais lanes suportam banco configurável. Que caso o teste ainda não cobre? — Há relato histórico de connect/preflight no recorte E03. Esse resultado não demonstra toda leitura ou INSERT em banco alternativo. O inventário E04 identifica referências SQL, mas presença de constante não prova caminho ativo. Como eu explicaria isso para outro pod? — Um literal apex não é bug por si, e configurar o client não muda SQL qualificada; a decisão é se banco alternativo é requisito de produto em cada lane ou só uma variável exposta.

### Próxima ação e encerramento

Owners Pods 2 e 3 a confirmar: receber lista inicial das consultas e promessa de perfis; saída é inventário por lane com decisão justificada. Encerrar estudo por implementar, manter restrição documentada ou adiar; não declarar auditoria completa de bancos nesta ficha.

<a id="item-027"></a>

## #174 — [Bug][Pod 2 / Package] Preservar dev/.env ao preparar o runner canônico

Frente: harness_e_pacote. Encaminhamento: revisao_de_candidato_e_prova_de_preservacao.

### Identidade e estado

#174 — [Bug][Pod 2 / Package] Preservar dev/.env ao preparar o runner canônico. Autor gustocezar; gustocezar; aberta na consulta de 16/10/2026 18:29:24 UTC. O assignee histórico não ratifica owner ou prazo para a próxima entrega. Corte técnico c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Preservar a configuração do operador em dev/.env ao preparar o runner canônico, evitando sobrescrita silenciosa e configuração do próximo comando apontando para outro ambiente.

### Feito, faltante e não comprovado

Na base, Sync-DevEnvForCanonicalScript faz Copy-Item -Force sem comparação/backup; Invoke-ProductGate e Invoke-TailOutlierGate chamam a função. Os comentários relatam candidato conjunto #167 passando .apex/dev.env por EnvFile, 85 testes iniciais e nova prova completa de e2e em macOS com stubs (base 7/3, candidato 10/0, controle 8/2). A prova posterior cobre e2e, sem estender automaticamente a smoke/tail-outlier, Windows ou Compose real.

### Linhagem

E08 → P-E08 → #174; E16/#167 compartilha a interface do runner. #62/#127/#128 são antecedentes, não prova de contenção. A sequência de comentários distingue helper W07 insuficiente e teste posterior de entrypoint integral; nenhum desses relatos publica commit/PR do candidato. #175 permanece ownership, não preservação de arquivo.

### Fontes e corte

Fontes lidas: fontes/batch-public-sources/issue-174.md; fontes/current-open-issues.json; _build/input-registro.json; fontes/lote2-scripts__apex.ps1.txt:609; fontes/lote2-scripts__apex.ps1.txt:677; fontes/lote2-dev__scripts__e2e_canonical.ps1.txt:16. Corpos/comentários preservados do snapshot 16/10/2026; código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Recibos de código em batch-public-sources/*.json preservam URL e observed_at; não atualizam o estado das issues. Linhas citadas usam os arquivos .txt/.md correspondentes.

### Classe e limite da evidência

FATO OBSERVADO: caminho de cópia e invocadores na base. RELATO HISTÓRICO: candidato e resultados de PowerShell/stubs em macOS, inclusive hashes/JUnit relatados pelo Codex em 11/10. INFERÊNCIA: arquivo divergente pode ser substituído; não houve acesso a .env real nem incidente reproduzido aqui. PROPOSTA: revisar e integrar contenção mínima.

### Fluxo

Pacote .apex/dev.env → wrapper → cópia histórica para dev/.env → runner. Candidato relatado: wrapper → EnvFile explícito → runner/Compose, preservando destino. O primeiro fluxo foi lido; o segundo é descrição de candidato, sem reinspeção do delta local nesta ficha.

### Consequências e risco

A sobrescrita pode eliminar preferências/credenciais do operador e alterar o ambiente selecionado. Alta confiança no caminho estático de escrita; não afirmar perda real. Passar EnvFile reduz esse risco, mas não comprova que o contêiner escolhido pertence ao checkout.

### Alternativas e recomendação

Recomendo revisar passagem direta de EnvFile, pois elimina a necessidade da cópia. Alternativas: recusar destino divergente ou oferecer backup explicitamente consentido, com cuidado para não criar cópias indevidas de segredo. O backup aumenta complexidade de retenção; a recusa preserva dados mas mantém dois caminhos. A escolha do candidato ainda precisa revisão do time.

### Dependências e paralelismo

Declaração/forwarding do parâmetro no runner (#167) é dependência técnica. Política de ownership (#175) governa operações posteriores, não precisa bloquear prova offline de preservação. Windows e Compose são provas distintas; não repetir suítes históricas sem motivo nem usar stubs como substituto dessas camadas.

### Plano e aceite propostos

Fixar árvore/hash do candidato e testes; revisar a remoção da cópia; controlar destino ausente/idêntico/divergente/somente leitura e fonte ausente, com bytes fictícios; conferir RC de falhas e ausência de conteúdo em logs. Preservar controle negativo que reinjeta a cópia. Cobrir entrypoints afetados por casos próprios, reutilizando e2e somente no escopo identificado. Futuras provas Windows/Compose devem registrar identidade sanitizada. Aceite: nenhum write no destino sem política explícita, forwarding correto e comportamento de falha claro.

### Comunicação entre responsáveis

Explicar que o patch evita cópia, em vez de certificar segurança de toda a stack. Relatar cada prova por plataforma e entrypoint; mostrar hash/diff identificável sem incluir arquivos .env.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Preservar dev/.env mas deixar o runner ignorar EnvFile trocaria a sobrescrita por uma configuração não aplicada; um backup automático poderia criar cópias indevidas de segredo. Que caso o teste ainda não cobre? — A prova relatada cobre o entrypoint e2e em macOS com stubs; smoke, tail-outlier, Windows e Compose real seguem sem prova própria, e o helper W07 sozinho foi considerado insuficiente. Como eu explicaria isso para outro pod? — Na base, Sync-DevEnvForCanonicalScript copia com Copy-Item -Force sem comparação; o candidato relatado passa .apex/dev.env por EnvFile, o que evita a cópia sem certificar a segurança de toda a stack.

### Próxima ação e encerramento

Autor/owner do pacote a confirmar: entrada candidato identificado e recibos históricos; saída revisão pequena com prova negativa de preservação. Encerrar após integração e critérios acordados para entrypoints/plataformas, mantendo runtime real e ownership com seus limites. Não gerar uma segunda correção concorrente sem confrontar o candidato existente.

<a id="item-028"></a>

## #175 — [Decision][Pod 2 / Package] Definir identidade e ownership de stacks entre checkouts

Frente: infra_operacao. Encaminhamento: decisao_de_identidade_e_ownership.

### Identidade e estado

#175 — [Decision][Pod 2 / Package] Definir identidade e ownership de stacks entre checkouts. Autor gustocezar; gustocezar; aberta na consulta de 16/10/2026 18:29:24 UTC. O assignee histórico não ratifica owner ou prazo para a próxima entrega. Corte técnico c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Distinguir recursos de outro checkout antes de operar uma stack no mesmo daemon. O benefício é evitar prova no ambiente errado e mutação de recursos cuja propriedade não foi estabelecida.

### Feito, faltante e não comprovado

Confirmei name: apex-dev, name: apex-infra, container_name fixos, portas de host configuráveis e volumes no Compose de infra/dev. O comentário relata inventário de sete Compose e 12 operações, além de duas opções de isolamento. Só os arquivos base foram reinspecionados aqui; nenhuma identidade de daemon/container foi medida.

### Linhagem

E09 → P-E09 → #175; #64 é guard histórico de recursos preexistentes e #113 é protocolo de overhead. Estudos de 11/10 acrescentam pré-condições por operação e distinguem volume de projeto, nome global e porta de host. Implementação de guard é descendente a delimitar após política, não resultado já incorporado.

### Fontes e corte

Fontes lidas: fontes/batch-public-sources/issue-175.md; fontes/current-open-issues.json; _build/input-registro.json; fontes/batch-public-sources/dev__docker-compose.yml.txt:5; fontes/batch-public-sources/infra__docker-compose.yml.txt:34. Corpos/comentários preservados do snapshot 16/10/2026; código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Recibos de código em batch-public-sources/*.json preservam URL e observed_at; não atualizam o estado das issues. Linhas citadas usam os arquivos .txt/.md correspondentes.

### Classe e limite da evidência

FATO OBSERVADO: nomes, portas e montagens nos dois Compose base. RELATO HISTÓRICO: matriz dos sete arquivos/12 operações. INFERÊNCIA: nomes globais/portas compartilhadas podem causar colisão ou seleção errada; não afirmo que redes compartilhadas sempre falham. DECISÃO PENDENTE: protocolo de ownership e compatibilidade.

### Fluxo

Checkout (raiz/manifesto) + contexto/endpoint Docker → daemon efetivo → projeto/serviço/container/volume/rede → preflight de identidade → operação permitida ou recusa sem mutação. Fluxo proposto; nome esperado ou contexto diferente não bastam como prova.

### Consequências e risco

A operação pode adotar ou limpar stack alheia; teste pode observar dados de outro checkout. Confiança alta na necessidade de distinguir identidades, mas risco concreto depende do deployment. Daemons distintos ainda podem competir por portas no mesmo host.

### Alternativas e recomendação

Comparar parametrizar projeto/nomes/portas em daemon compartilhado e usar daemons/VMs distintos com fronteira de rede. Recomendo protocolo verificável por operação combinando labels/manifesto/raiz e identidade do daemon, com falha fechada. Nonce dificulta adoção acidental; caminho sozinho é frágil a movimentação; nome sozinho não demonstra propriedade.

### Dependências e paralelismo

Mantenedor/owner de pacote decide identidade, migração e adoção de stacks antigas. Inventário e desenho podem correr em paralelo a #167/#174/#178; testes offline de argv/arquivo/endpoint não exigem essa política completa. Provas que mutem runtime real precisam conferir ownership antes.

### Plano e aceite propostos

Consolidar sete Compose e operações efetivas; definir quais são somente leitura e quais mutam; estabelecer provas mínimas e recusa para identidade ausente/divergente; desenhar controles com dois checkouts, contextos apontando ao mesmo daemon, portas ocupadas e stacks legadas. Aceite da decisão: política explícita, compatibilidade e testes de recusa sem limpar/recriar/adotar. Guard posterior deve alterar o menor ponto comum e reportar apenas identificadores sanitizados.

### Comunicação entre responsáveis

Explicar diferença entre isolamento por nome, identidade de recurso e autenticação. Não chamar mudar DOCKER_CONTEXT de isolamento garantido; deixar claro como o daemon e a rede foram verificados quando houver prova.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Se dois contextos Docker apontarem ao mesmo daemon, nomes fixos como apex-dev e apex-infra e container_name fixos podem levar uma operação a adotar ou limpar a stack de outro checkout. Que caso o teste ainda não cobre? — Volume legado e porta de host compartilhada ainda não têm controle, e daemons distintos ainda competem por portas no mesmo host; nenhuma identidade de daemon ou container foi medida. Como eu explicaria isso para outro pod? — Nome igual não demonstra propriedade e trocar DOCKER_CONTEXT não é isolamento garantido; a decisão é um protocolo de identidade por operação, e adotar uma stack anterior ao manifesto exige evidência que a política ainda vai definir.

### Próxima ação e encerramento

Mantenedor/owner do pacote a confirmar: entrada inventário e duas opções; saída política de ownership por operação e plano do guard. Encerrar estudo/decisão após aprovação fundamentada ou adiamento com limites; não declarar implementação pelo inventário.

<a id="item-029"></a>

## #176 — [Study][Pod 2 / Infra] Documentar rotação de credencial local ClickHouse e recuperação

Frente: infra_operacao. Encaminhamento: estudo_de_procedimento_operacional.

### Identidade e estado

#176 — [Study][Pod 2 / Infra] Documentar rotação de credencial local ClickHouse e recuperação. Autor gustocezar; sem assignee; aberta na consulta de 16/10/2026 18:29:24 UTC. O assignee histórico não ratifica owner ou prazo para a próxima entrega. Corte técnico c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Criar procedimento reproduzível de rotação/recuperação de credencial ClickHouse local que preserve dados e evite disseminar segredo. Público: operadores do ambiente local suportado.

### Feito, faltante e não comprovado

O Compose de infra usa imagem ClickHouse 24.8, usuário/senha parametrizados, access management e volume persistente ch-data. Isso não determina sozinho como rotação de usuário é persistida no perfil nem prova ausência de runbooks externos. Não há comentários adicionais no snapshot desta issue; nenhum procedimento integral foi validado nesta ficha.

### Linhagem

E13 → P-E13 → #176. Complementa pacote #62 e segurança #33; não define disclosure nem política de produção. O registro anterior é minuta histórica; não foi localizada nesta revisão uma cadeia de implementação/aceite runtime vinculada à issue.

### Fontes e corte

Fontes lidas: fontes/batch-public-sources/issue-176.md; fontes/current-open-issues.json; _build/input-registro.json; fontes/batch-public-sources/infra__docker-compose.yml.txt:38. Corpos/comentários preservados do snapshot 16/10/2026; código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Recibos de código em batch-public-sources/*.json preservam URL e observed_at; não atualizam o estado das issues. Linhas citadas usam os arquivos .txt/.md correspondentes.

### Classe e limite da evidência

FATO OBSERVADO: configuração do Compose. INFERÊNCIA: recuperação improvisada pode quebrar acesso ou dados; não incidente observado. PROPOSTA: inventário e runbook com rollback. DECISÃO PENDENTE: perfil suportado, método de rotação e quando recriação é permitida.

### Fluxo

Operador → método aprovado de rotação → estado de usuário no ClickHouse + configuração dos clientes → reconexão; verificação de dados/restart → aceite ou recuperação. Fluxo proposto, sem comandos executados nem leitura de segredo real.

### Consequências e risco

Confundir trocar variável com trocar credencial efetiva pode bloquear clientes; recriar volume pode eliminar dados. A relevância é operacional; a frequência e método exato dependem da imagem/configuração e continuam a investigar. Não apresentar exclusão de volume como rotação transparente.

### Alternativas e recomendação

Comparar rotação in-place de usuário e reconfiguração/recriação somente em ambiente descartável com backup/restauração definidos. Recomendo primeiro identificar como o usuário é gerenciado nesse perfil e inventariar procedimentos existentes. O método deve permitir recuperação controlada; escolher ALTER USER sem confirmar gestão do usuário seria prematuro.

### Dependências e paralelismo

Owner Infra define perfil e disponibilidade de ambiente descartável para prova futura; operadores de clientes participam da atualização. #33 pode orientar política, mas a ausência de SECURITY.md não é automaticamente bloqueio técnico do estudo. Não condicionar toda v1 a esse runbook sem requisito acordado.

### Plano e aceite propostos

Inventariar docs existentes; identificar origem/persistência do usuário; redigir pré-condições e comandos com placeholders seguros; desenhar casos credencial nova, antiga recusada quando aplicável, reinício, cliente desatualizado, dados preservados e rollback. Após autorização específica, validar em recurso próprio descartável. Aceite: procedimento versão/perfil identificados, resultado e recuperação demonstrados ou limitações explícitas; nunca usar credencial real nos exemplos.

### Comunicação entre responsáveis

Explicar diferença entre atualização de configuração, rotação efetiva e recriação. Registrar o que o procedimento preserva e quando restauração é necessária; omitir segredos e não anexar dumps de ambiente.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Alterar só o .env troca a variável, não necessariamente a credencial efetiva do usuário ClickHouse, e pode bloquear clientes; recriar o volume ch-data para rotacionar eliminaria dados. Que caso o teste ainda não cobre? — Restart e cliente antigo precisam de prova no recorte escolhido. Critérios desenhados na issue não equivalem a execução demonstrada; não se afirma ausência de desenho desses casos. Como eu explicaria isso para outro pod? — Atualizar configuração, rotacionar a credencial efetiva e recriar o ambiente são coisas distintas; primeiro é preciso saber como o usuário é gerenciado nesse perfil antes de escolher ALTER USER ou recriação.

### Próxima ação e encerramento

Owner Infra a confirmar: entrada inventário de procedimentos e perfil da imagem; saída proposta de runbook/rollback para revisão. Encerrar o estudo com método e limites documentados; só declarar procedimento validado após recibo próprio da prova acordada, sem revogar credenciais nesta revisão.

<a id="item-030"></a>

## #177 — [Study][Pod 3] Definir narração AQE usando configuração capturada em job_conf

Frente: serve_explicabilidade. Encaminhamento: estudo_de_produto_e_narrativa.

### Identidade e estado

#177 — [Study][Pod 3] Definir narração AQE usando configuração capturada em job_conf. Autor gustocezar; sem assignee; aberta na consulta de 16/10/2026 18:29:24 UTC. O assignee histórico não ratifica owner ou prazo para a próxima entrega. Corte técnico c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Explicar decisões AQE em relação à configuração realmente capturada, sem converter correlação em causa ou inventar defaults. O usuário ganha contexto para entender conselho e possível NO-OP.

### Feito, faltante e não comprovado

JOB_CONF_SQL existe no Serve e expande o Map em pares chave/valor, preservando ausência. diagnose produz notas de transição em escopo de execução e distingue coalesce de skew. A existência das duas superfícies não prova que a narração já as correlaciona. O registro S15 antigo dizia zero ocorrências de job_conf; isso é histórico, não estado deste SHA.

### Linhagem

S15/F4.3 → P-S15 → #177, originado no trabalho API #129. #115 governa atribuição execution→stage. A proposta atual pede decisão de benefício/escopo antes de implementação; não há PR descendente ou aceite citado nos comentários preservados.

### Fontes e corte

Fontes lidas: fontes/batch-public-sources/issue-177.md; fontes/current-open-issues.json; _build/input-registro.json; fontes/lote2-serve__src__apex_mcp__ch.py.txt:444; fontes/lote2-serve__src__apex_mcp__diagnose.py.txt:267; fontes/batch-public-sources/contract__job_conf.ddl.sql.txt:5. Corpos/comentários preservados do snapshot 16/10/2026; código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Recibos de código em batch-public-sources/*.json preservam URL e observed_at; não atualizam o estado das issues. Linhas citadas usam os arquivos .txt/.md correspondentes.

### Classe e limite da evidência

FATO OBSERVADO: query e notas AQE no código. RELATO HISTÓRICO: proposta F4.3 e contagem antiga S15. INFERÊNCIA limitada: cruzar configuração e transição pode melhorar explicação; o valor de produto deve ser avaliado. PROPOSTA: exemplos determinísticos com ausências e escopo explícito.

### Fluxo

job_conf allowlisted (chaves/ausências) + transições AQE (execution_id/tipo/confiança) → narração proposta → explicação ao usuário. Atribuição de stage só quando demonstrada. Hoje a presença das entradas é estática; a correlação completa ainda não foi certificada.

### Consequências e risco

Uma narrativa pode repetir configuração já ativa, atribuir transição ao stage errado ou usar default não capturado. Confiança alta nos limites expressos pelo contrato; não afirmo que ocorreu incidente de aconselhamento errado nesta frente.

### Alternativas e recomendação

Recomendo exemplos determinísticos de observação e contexto, com linguagem de ausência. Alternativas: manter fontes separadas, combinar texto ou expor campos estruturados para UI. Um LLM não é necessário para uma comparação de chaves e aumenta o custo de verificar afirmações; nova superfície precisa benefício justificável.

### Dependências e paralelismo

Owner Pod 3 decide implementar/adiar/rejeitar e superfície. O estudo pode correr em paralelo a #115; qualquer afirmação por stage depende de vínculo válido ou deve permanecer no escopo da execução. Não bloquear o estudo com suposta inexistência de job_conf, que já é lida.

### Plano e aceite propostos

Mapear pontos reais de leitura/narração; selecionar chaves permitidas; escrever exemplos com valor conhecido, chave ausente e captura indisponível; separar decisão AQE observada de inferência; decidir produto. Se aprovado, implementar pequena composição textual/estruturada com negativos que impedem default inventado e ligação indevida de stage. Prova com job_conf real é posterior, identificada por execução.

### Comunicação entre responsáveis

Explicar que a novidade é relacionar e apresentar contexto, não criar job_conf no Serve. Mostrar exemplo que diga a configuração observada e a transição, mantendo grau de certeza e limite de escopo.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Inferir um default para uma chave ausente de job_conf faria a narração afirmar uma configuração que não foi capturada, e ligar transição a stage sem vínculo válido atribuiria decisão ao stage errado. Que caso o teste ainda não cobre? — Conferir nos exemplos da proposta o comportamento de atributos ausentes e divergentes e a observação que sustenta cada conclusão; este recorte não aceita sua implementação. Como eu explicaria isso para outro pod? — A novidade seria relacionar e apresentar job_conf já lido com as transições AQE, sem afirmar causa; a comparação útil mostra a configuração observada e a transição, com grau de certeza e escopo de execução.

### Próxima ação e encerramento

Owner Serve a confirmar: receber exemplos e mapa de leitura; saída decisão de produto e, se aprovada, plano atômico com testes negativos. Encerrar estudo por decisão fundamentada, mantendo implementação como seguimento explícito; não declarar narração pronta por existir uma query.

