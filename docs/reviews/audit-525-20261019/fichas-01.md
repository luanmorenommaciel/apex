# Fichas documentais — lote 1

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-001"></a>

## PR#155 — test(engine): keep schema preflight aligned with stage queries

Frente: fila_prs. Encaminhamento: revisao_e_prova_de_integracao.

### Identidade e estado

PR #155 — test(engine): keep schema preflight aligned with stage queries. Autor: gustocezar; aberta. Base main@c4541a59d8e9ad4ff6cbcca67a606ad21247eb9c; head 561b27e7d1914dddf4989bf04834a33da726a45f. 1 arquivo(s). Origens: E20; #154; predecessoras #131 e #139. Autor não equivale a owner designado para o próximo passo.

### Intenção e benefício

Impedir divergência entre as colunas exigidas pelo preflight e as lidas pelas duas queries de stage. Beneficia a operação do Engine: falhar cedo continua coerente com o que a consulta realmente exige.

### Feito, faltante e não comprovado

Um teste novo compara conjuntos nos dois sentidos e enumera colunas divergentes. Produção não muda. Os 11 checks do head terminaram em failure; os recibos anteriores registram jobs sem steps. Isso não demonstra falha da asserção. Falta evidência hospedada útil de integração e review formal.

### Linhagem

E20 → #154 → candidato local relatado → 561b27e → #155 (Closes #154). #131 introduz o preflight; #139 endurece o extrator usado pelo teste. Recibo de Task-Spec citado no histórico não foi reaceito nesta revisão. Decisão de merge ausente.

### Fontes e corte

Fontes primárias: fontes/pr155-files.json (diff integral retornado pela API), fontes/pr155-checks.json (11 checks), fontes/pr155-reviews.json (0 reviews), fontes/current-open-pulls.json (corpo e topologia). Consulta em 16/10/2026, 18:29–18:31 UTC; timestamp preciso em cada recibo. Fontes de contexto adicionais: ver fontes/ e INVENTARIO-FONTES.json.

### Classe e limite da evidência

DIRETO: diff, heads, checks e ausência de reviews no endpoint. RELATADO: 46 testes focados, 310 Engine e controles de mutação no corpo. A igualdade de árvores local/publicada é relato, sem comparação independente nesta etapa. Nenhuma prova de ClickHouse real decorre deste teste.

### Fluxo

STAGE_EVENTS_SQL + STAGE_AGGREGATES_SQL → extrator → conjunto de leituras ↔ REQUIRED_SPARK_EVENTS_COLUMNS → asserção de igualdade. Fluxo observado estaticamente; o extrator usa regex e exclusões, não um parser SQL completo.

### Consequências e risco

Sem a guarda, ampliar a SQL ou reduzir o preflight pode deixar passar incompatibilidade. Confiança alta na finalidade; lacunas do extrator podem afetar os dois lados de testes que o reutilizam. Isso é limite de cobertura, não defeito de runtime demonstrado.

### Alternativas e recomendação

Recomendação: manter a pequena guarda de consistência. Derivar a constante em runtime acopla o preflight ao parser; estender agora a SHAPE_HISTORY_SQL amplia o escopo. Ambas podem ser discutidas separadamente. A mudança é reversível por retirar o teste.

### Dependências e paralelismo

Sem dependência de código das outras sete PRs. G01/#130 só condiciona a obtenção de uma nova prova remota se o acesso ao runner ainda falhar. O mantenedor escolhe como testar a integração; rebase não é obrigação universal.

### Plano e aceite propostos

Revisar o conjunto de consultas coberto e os controles de colunas omitidas/adicionadas; obter CI útil sobre a árvore de integração escolhida; decidir merge. Aceite proposto: teste discrimina as duas divergências e os checks aplicáveis executam. Só então reconciliar #154/E20. Não executar runtime só para aceitar uma guarda estática.

### Comunicação entre responsáveis

Na eventual revisão, explicar a diferença entre vermelho sem execução e teste reprovado; citar SHA/run e o limite do extrator. Texto é minuta, não comentário publicado.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Sem a guarda, ampliar STAGE_EVENTS_SQL ou STAGE_AGGREGATES_SQL, ou reduzir REQUIRED_SPARK_EVENTS_COLUMNS, deixaria o preflight aprovar um schema que a consulta não consegue ler; derivar a constante em runtime acoplaria o preflight ao extrator. Que caso o teste ainda não cobre? — A comparação vale nos dois sentidos: coluna retirada da constante e coluna extra que a SQL não lê. SHAPE_HISTORY_SQL fica fora desta guarda, e o extrator por regex com exclusões não é um parser SQL completo. Como eu explicaria isso para outro pod? — É uma guarda estática entre o que o preflight exige e o que as duas queries de stage leem; não prova conexão com ClickHouse real, e os 11 checks em failure do head não demonstram asserção reprovada.

### Próxima ação e encerramento

Autor/mantenedor a confirmar: entrada diff 561b27e e checks existentes; saída revisão e prova da integração escolhida; fechar após decisão registrada e atualização de #154, sem presumir aprovação nesta auditoria.

<a id="item-002"></a>

## PR#157 — test(serve): pin eight-tool transport parity with identical arguments

Frente: fila_prs. Encaminhamento: revisao_e_integracao.

### Identidade e estado

PR #157 — test(serve): pin eight-tool transport parity with identical arguments. Autor: gustocezar; aberta. Base main@c4541a59d8e9ad4ff6cbcca67a606ad21247eb9c; head a3ed9723af9461bd8f2ea9ad60347635b1254bad. 2 arquivo(s). Origens: S08; S24; #156; descendente #163. Autor não equivale a owner designado para o próximo passo.

### Intenção e benefício

Fixar a paridade dos oito tools MCP/HTTP com argumentos idênticos, sem aceitar dois resultados vazios como prova suficiente. Beneficia consumidores que usam portas distintas para a mesma pergunta.

### Feito, faltante e não comprovado

Dois arquivos de teste cobrem store populado, tabelas ausentes e store inalcançável; o arquivo adicional fortalece o caso de argumentos iguais. Head tem 11 checks success do workflow anterior a #160. Zero reviews formais. Não há mudança de produção.

### Linhagem

#129 e testes existentes → #156/S08/S24 → a3ed972 → #157. #163 depende de helpers adicionados aqui. O corpo relata árvore local combinada com #158/#159; ela não equivale por si só à árvore isolada publicada.

### Fontes e corte

Fontes primárias: fontes/pr157-files.json (diff integral retornado pela API), fontes/pr157-checks.json (11 checks), fontes/pr157-reviews.json (0 reviews), fontes/current-open-pulls.json (corpo e topologia). Consulta em 16/10/2026, 18:29–18:31 UTC; timestamp preciso em cada recibo. Fontes de contexto adicionais: ver fontes/ e INVENTARIO-FONTES.json.

### Classe e limite da evidência

DIRETO: vetores dos oito tools, fakes, payloads comparados sem normalização de campos e igualdade nas duas portas; 11 checks verdes. RELATADO: 572 testes da combinação local e provas de transporte reais separadas. Os testes aqui usam chamadas MCP em processo e TestClient HTTP; não validam nginx, autenticação em implantação ou ClickHouse real.

### Fluxo

Mesmo nome + mesmos argumentos → MCP call_tool e HTTP TestClient → payload normalizado → igualdade + assertivas de conteúdo. FakeReadStore injeta dados populados, ausentes e erro sanitizado. As assertivas específicas evitam igualdade trivial em casos escolhidos.

### Consequências e risco

Confiança alta na proteção de despacho/serialização exercitada; SQL real e infraestrutura permanecem fora. O teste original mais fraco não invalida o reforço adicional de argumentos iguais. Helpers compartilhados criam dependência de manutenção com #163.

### Alternativas e recomendação

Recomendação: revisar e integrar a caracterização; registrar o CI existente e decidir a prova necessária para a árvore final. Reescrever a arquitetura antes de fixar a paridade aumenta o escopo. Duplicar helpers em #163 evita importação, mas perde uma fonte comum.

### Dependências e paralelismo

Independente de #158/#159 para seu objetivo; #163 depende destes helpers. NOV-03 coordena revisão, sem impor um CI novo idêntico a toda PR por regra geral.

### Plano e aceite propostos

Conferir conjunto exato dos oito tools e assertivas populadas/ausentes/erro; revisar controles que trocam argumentos e removem conteúdo; decidir integração. Aceite proporcional: proteção dos casos declarados e checks aplicáveis à árvore escolhida. #156 só fecha quando seus demais critérios também estiverem satisfeitos.

### Comunicação entre responsáveis

Comunicar a Serve/Front o que a paridade em processo protege e os limites de transporte real. Identificar se a evidência citada é do head ou de uma combinação local.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Aceitar dois resultados vazios como paridade deixaria passar divergência real entre MCP e HTTP; sem o eco de argumentos idênticos, não haveria como mostrar que as duas portas responderam à mesma pergunta. Que caso o teste ainda não cobre? — As assertivas de conteúdo cobrem store populado, tabelas ausentes e store inalcançável com FakeReadStore em processo; nginx, autenticação de implantação e SQL de ClickHouse real continuam fora mesmo com a suíte verde. Como eu explicaria isso para outro pod? — Os oito tools recebem os mesmos argumentos nas duas portas e o teste exige payload igual com conteúdo; isso protege despacho e serialização, não o transporte real, e os helpers criados aqui também sustentam a #163.

### Próxima ação e encerramento

Revisor e mantenedor a confirmar: revisar a3ed972; saída decisão e recibo da integração; atualizar S08/S24 e preservar #156 como guarda-chuva quando restarem critérios.

<a id="item-003"></a>

## PR#158 — test(serve): pin findings score-tie order on both SQL doors

Frente: fila_prs. Encaminhamento: revisao_e_integracao.

### Identidade e estado

PR #158 — test(serve): pin findings score-tie order on both SQL doors. Autor: gustocezar; aberta. Base main@c4541a59d8e9ad4ff6cbcca67a606ad21247eb9c; head 514b0e573bce9593ac1737869568161b3e951a49. 1 arquivo(s). Origens: S24; #156; complemento de #153. Autor não equivale a owner designado para o próximo passo.

### Intenção e benefício

Evitar que Front e Serve concordem entre si usando uma ordenação errada de findings empatados. O critério canônico é confidence_score DESC, finding_id ASC.

### Feito, faltante e não comprovado

Dezoito linhas de teste verificam ORDER BY nas consultas Front, Serve aditiva e Serve legada. O FakeClient não ordena linhas; a guarda é estática. Onze checks verdes do workflow anterior; zero reviews. Sem alteração de SQL de produção.

### Linhagem

#153 corrige paridade → #156 pede regressões → 514b0e5 → #158. Corpo relata validação local combinada com #157/#159. Não declara encerrar sozinho #156.

### Fontes e corte

Fontes primárias: fontes/pr158-files.json (diff integral retornado pela API), fontes/pr158-checks.json (11 checks), fontes/pr158-reviews.json (0 reviews), fontes/current-open-pulls.json (corpo e topologia). Consulta em 16/10/2026, 18:29–18:31 UTC; timestamp preciso em cada recibo. Fontes de contexto adicionais: ver fontes/ e INVENTARIO-FONTES.json.

### Classe e limite da evidência

DIRETO: três consultas verificadas e checks do head. RELATADO: 572 testes da combinação. A ordem literal é comprovada no texto exercitado; execução e plano de SQL real não foram revalidados aqui.

### Fluxo

Queries de cada porta → assertiva de ORDER BY canônico. No legado, score constante torna o segundo critério especialmente importante. O mecanismo observa intenção SQL, não ordenação de um resultado real.

### Consequências e risco

Risco de produto baixo por ser só teste. Protege contra duas implementações igualmente erradas; pode precisar manutenção se houver reformatação semanticamente equivalente. Não prova todo comportamento de empates.

### Alternativas e recomendação

Recomendação: manter guarda pequena; usar #159 como complemento operacional quando necessário. Trocar por teste exclusivamente de igualdade das portas perderia o oráculo canônico. Teste SQL real é opção adicional, não requisito universal desta PR.

### Dependências e paralelismo

Pode ser revisada paralelamente a #157, #161 e #162. Não precisa esperar a política global de versão ou runtime Verify.

### Plano e aceite propostos

Revisar as três variantes; conferir que remover/inverter o desempate quebraria a assertiva. Aceite: intenção canônica explícita e checks aplicáveis à integração. Registrar separadamente qualquer controle real adicional; não atribuí-lo a esta mudança estática.

### Comunicação entre responsáveis

Explicar a Front/Serve por que paridade e correção de ordem são propriedades diferentes; citar o desempate por finding_id.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Comparar apenas Front e Serve entre si aceitaria as duas portas com o mesmo empate invertido; é o oráculo canônico confidence_score DESC, finding_id ASC que acusa esse caso. Que caso o teste ainda não cobre? — A guarda lê o ORDER BY nas variantes Front, Serve aditiva e Serve legada; no legado com score constante, o desempate por finding_id decide a ordem, e a ordenação de um resultado real depende de executar a SQL, o que este teste não faz. Como eu explicaria isso para outro pod? — Paridade entre portas e correção da ordem são propriedades diferentes; esta PR fixa no texto SQL a intenção canônica do desempate, e a #159 complementa no plano operacional.

### Próxima ação e encerramento

Revisor/mantenedor: entrada 514b0e5; saída revisão e decisão de integração. Reconciliar #156 apenas quanto a este critério.

<a id="item-004"></a>

## PR#159 — fix(serve): make parity gate diagnose drift and clean derived fixture rows

Frente: fila_prs. Encaminhamento: revisao_da_limpeza_e_integracao.

### Identidade e estado

PR #159 — fix(serve): make parity gate diagnose drift and clean derived fixture rows. Autor: gustocezar; aberta. Base main@c4541a59d8e9ad4ff6cbcca67a606ad21247eb9c; head 1685f8ac91b8e9b68a83d10176519c963e186ad4. 4 arquivo(s). Origens: S02; S24; #156; complemento de #153. Autor não equivale a owner designado para o próximo passo.

### Intenção e benefício

Tornar o gate de paridade capaz de detectar deriva, conteúdo malformado e empates errados, removendo também resíduos derivados da fixture para permitir reuso do ambiente.

### Feito, faltante e não comprovado

Quatro arquivos: gate, testes, RUNBOOK e VALIDATION. O diff completo inclui limpeza de spark_jobs_1m, empates controlados e validações de forma. Onze checks verdes do workflow antigo; zero reviews. O escopo é maior que o último ajuste isolado.

### Linhagem

#153 → #156 → sucessivos controles do gate relatados no corpo → 1685f8a/#159. O relatório local G1-F1c e a suíte combinada são relatos associados a árvores/blobs indicados pelo autor; não são uma nova execução independente.

### Fontes e corte

Fontes primárias: fontes/pr159-files.json (diff integral retornado pela API), fontes/pr159-checks.json (11 checks), fontes/pr159-reviews.json (0 reviews), fontes/current-open-pulls.json (corpo e topologia). Consulta em 16/10/2026, 18:29–18:31 UTC; timestamp preciso em cada recibo. Fontes de contexto adicionais: ver fontes/ e INVENTARIO-FONTES.json.

### Classe e limite da evidência

DIRETO: limpeza por IDs/fingerprint, mutations_sync=1, consulta de existência do rollup e propagação de falhas; testes positivos/negativos no diff. RELATADO: gate 19 PASS/0 FAIL/0 SKIP e 572 testes combinados. Testes controlados não provam concorrência nem isolamento de toda implantação. Complemento documental de 19/10: VALIDATION no head registra o checkpoint local 41ba605e/519 testes; o diagnóstico F1c e sua evidência posterior (79 focados, 572 combinados e G1-F1c 19 PASS/0 FAIL/0 NOT EXERCISED) estão no corpo da PR, com limites próprios. Não usar 519 como contagem do head atual nem exigir repetir prova já relatada. A referência de Current evidence do RUNBOOK deve ser lida com esse complemento; nenhum teste foi reproduzido nesta auditoria.

### Fluxo

Fixture com scores .5 e IDs invertidos → portas HTTP/CH → paridade + oráculo de desempate + validação de linhas. Cleanup → rollup, tabelas de origem e memória com identificadores da fixture. Deletar a origem sozinho não desfaz automaticamente o destino da MV.

### Consequências e risco

A limpeza escreve no store no modo de fixture; por isso precisa revisão do escopo de IDs/database e das falhas. --job-id evita a criação/remoção da fixture. A proteção contra eco de finding_id inválido vale para o diagnóstico novo; outros diagnósticos não garantem ausência universal de dados.

### Alternativas e recomendação

Recomendação: preservar gate com revisão explícita da limpeza e dos limites. Excluir cleanup deixa resíduos; truncar tabelas amplia perigosamente o alcance; somente comparar portas aceita dois resultados errados. Separar futuras extensões mantém esta mudança revisável.

### Dependências e paralelismo

Revisão pode ocorrer em paralelo. Uma reprodução operacional depende de store/ambiente autorizado e ownership definido; não transforma #175 em bloqueio obrigatório de todos os testes. #157/#158 complementam, sem dependência de código para o gate.

### Plano e aceite propostos

Revisar diff completo e alvos de DELETE; confrontar fixture/controle que deve sobreviver, rollup ausente, erro de lookup, linhas inválidas e empate errado em ambas as portas. Escolher se os recibos locais satisfazem o risco ou se cabe prova operacional adicional. Aceite: escopo e limites registrados, checks aplicáveis e decisão humana.

### Comunicação entre responsáveis

Comunicar modo fixture versus --job-id, alvos removidos, comportamento em erro e limites de confidencialidade. Distinguir estado final observado de ausência de interferência concorrente, que não foi demonstrada.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Sem a limpeza, resíduos da fixture ficam no rollup e nas tabelas de origem; truncar tabelas ampliaria o alcance a outros jobs, e comparar só as portas aceitaria dois resultados igualmente errados. Que caso o teste ainda não cobre? — A revisão confronta se o controle de outro job sobrevive ao DELETE, o que ocorre quando a consulta de metadata do rollup falha e o fato de apagar a origem não desfazer o destino da MV; concorrência e isolamento de toda implantação não foram demonstrados. Como eu explicaria isso para outro pod? — O gate passa a apontar deriva, linhas malformadas e empate errado, e a limpeza remove só identificadores da fixture; o modo --job-id não cria nem remove fixture, e a proteção contra eco de finding_id inválido vale só para o diagnóstico novo, sem garantir que outros diagnósticos não mostrem dados.

### Próxima ação e encerramento

Revisor de Serve e mantenedor: entrada 1685f8a e recibos citados; saída parecer da limpeza e decisão de integração. Se exigida nova prova operacional, defini-la antes em ambiente autorizado; esta auditoria não a executa.

<a id="item-005"></a>

## PR#161 — ci: keep root gate diagnostics after Python lane failures

Frente: fila_prs. Encaminhamento: revisao_e_integracao.

### Identidade e estado

PR #161 — ci: keep root gate diagnostics after Python lane failures. Autor: gustocezar; aberta. Base main@c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; head d61eab85f258592cae909fd5c2ddc9f21ef24b96. 1 arquivo(s). Origens: NOV-03; CI #160. Autor não equivale a owner designado para o próximo passo.

### Intenção e benefício

Manter diagnóstico do root gate quando uma lane Python falha, sem esconder a falha original nem tentar rodar após setup incompleto ou cancelamento.

### Feito, faltante e não comprovado

Seis linhas adicionam IDs aos passos de setup e condições explícitas. Três checks success do CI atual. Zero reviews formais. O caminho verde foi executado; o ramo de falha não foi provocado por esta auditoria.

### Linhagem

#160 reduz o CI → d61eab8/#161 restaura diagnóstico após falha de lane. Relato local de 14 cenários e cinco mutações aparece no corpo; não é execução desse ramo no runner hospedado.

### Fontes e corte

Fontes primárias: fontes/pr161-files.json (diff integral retornado pela API), fontes/pr161-checks.json (3 checks), fontes/pr161-reviews.json (0 reviews), fontes/current-open-pulls.json (corpo e topologia). Consulta em 16/10/2026, 18:29–18:31 UTC; timestamp preciso em cada recibo. Fontes de contexto adicionais: ver fontes/ e INVENTARIO-FONTES.json.

### Classe e limite da evidência

DIRETO: !cancelled() e pré-condições de checkout/uv; root também exige PowerShell pronto. A lane continua falhando, sem continue-on-error. DIRETO: três checks verdes. RELATADO: avaliação local dos cenários. PENDENTE: eventual controle de falha no runner, se requerido pelo mantenedor.

### Fluxo

checkout + uv concluídos e não cancelado → setup pwsh mesmo após lane falhar; pwsh concluído → root gate. Resultado da lane permanece no resultado do job.

### Consequências e risco

O ajuste melhora diagnóstico, sem corrigir uma falha de produto. Expressões podem comportar-se diferentemente do simulador local em condições de cancelamento; o CI verde não exerce todas as transições.

### Alternativas e recomendação

Recomendação: revisar a lógica e aceitar o limite ou pedir um controle mínimo de falha. continue-on-error dilui o sinal; mover root para outro job muda desenho/custo. Não exigir migração de runner como parte desta pequena correção.

### Dependências e paralelismo

Independente de política Verify e de #157. Mudanças futuras no workflow precisam preservar IDs e condições. DEC-N1 pode ser decidida em paralelo.

### Plano e aceite propostos

Revisar tabela de condições: setup falha, lane falha, cancelamento, caminho verde. Aceite proposto: root só roda com seus pré-requisitos e lane reprovada continua reprovada. Nova execução hospedada de falha é decisão proporcional ao risco, não fato já comprovado.

### Comunicação entre responsáveis

Explicar ao mantenedor que três checks verdes comprovam o caminho verde e que o ganho pretendido aparece quando a lane falha. Não confundir diagnóstico continuado com tolerância à falha.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Usar continue-on-error diluiria o sinal da lane reprovada, e rodar o root gate sem checkout, uv e PowerShell prontos produziria diagnóstico sem os pré-requisitos. Que caso o teste ainda não cobre? — Os três checks verdes exercem só o caminho verde; os ramos em que a lane falha, o setup de uv falha ou o run é cancelado não foram observados no runner, e os 14 cenários do corpo são avaliação local. Como eu explicaria isso para outro pod? — Quando uma lane Python falha, o root gate ainda roda se checkout, uv e PowerShell estiverem prontos e o run não tiver sido cancelado; o job continua vermelho, porque é diagnóstico continuado, não tolerância à falha.

### Próxima ação e encerramento

Mantenedor/revisor: entrada d61eab8, condições e checks atuais; saída decisão de integração e limite aceito ou controle de falha especificado. Não repetir CI verde sem nova razão.

<a id="item-006"></a>

## PR#162 — fix(verify): align module version with package 0.1.0

Frente: fila_prs. Encaminhamento: revisao_e_integracao.

### Identidade e estado

PR #162 — fix(verify): align module version with package 0.1.0. Autor: gustocezar; aberta. Base main@c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; head 3955f9de34af39824caec44dd39f307ff9c3513f. 2 arquivo(s). Origens: F19; DEC-N2 (política futura, sem bloqueio automático). Autor não equivale a owner designado para o próximo passo.

### Intenção e benefício

Alinhar a versão exportada pelo módulo Verify à versão 0.1.0 do pacote e detectar divergência futura entre metadata, módulo e default de Verdict.

### Feito, faltante e não comprovado

Muda __version__ de 0.3.0 para 0.1.0 e adiciona dois testes. Verdict.verify_version já tinha default 0.1.0; to_row usa o valor da instância. Três checks verdes do CI atual e zero reviews. Não migra linhas persistidas nem altera esse default.

### Linhagem

Divergência de identidade do módulo → 3955f9d/#162 → checks atuais verdes. A referência a extensão de contrato v0.3 não é versão do pacote. Política de release futura permanece decisão separada.

### Fontes e corte

Fontes primárias: fontes/pr162-files.json (diff integral retornado pela API), fontes/pr162-checks.json (3 checks), fontes/pr162-reviews.json (0 reviews), fontes/current-open-pulls.json (corpo e topologia). Consulta em 16/10/2026, 18:29–18:31 UTC; timestamp preciso em cada recibo. Fontes de contexto adicionais: ver fontes/ e INVENTARIO-FONTES.json.

### Classe e limite da evidência

DIRETO: diff, pyproject e models.py no SHA da main; três checks do head. A hipótese de que esta PR corrige persistência é refutada pelo default preexistente. Uso externo de __version__ não foi inventariado; nenhuma regressão de armazenamento foi demonstrada.

### Fluxo

pyproject.version ↔ teste de módulo e teste do default em Verdict.model_fields["verify_version"]. Serialização: instância Verdict → to_row com valor já existente. Não há seta causal nova da alteração em __init__ para linhas antigas.

### Consequências e risco

Risco baixo e delimitado: consumidores de __version__ passam a receber 0.1.0; testes impõem coerência futura a um default que pode precisar política explícita. Isso não justifica alegar quebra ou migração de persistência.

### Alternativas e recomendação

Recomendação: revisar a correção pequena e discutir política de versão futura em DEC-N2. Elevar todos os lugares para 0.3.0 mudaria contrato de identidade além desta correção. A mudança de módulo é reversível; não há rollback de dados aqui.

### Dependências e paralelismo

Sem dependência técnica de escritor externo, migração, DEC-06 ou conclusão da política de distribuição. Se a árvore de integração mudar, avaliar checks aplicáveis; não declarar o CI atual ausente.

### Plano e aceite propostos

Conferir os três valores e o caminho de serialização; revisar se o contrato pretendido é manter default e pacote alinhados. Aceite proposto: intenção aprovada e checks atuais aplicáveis. Retirar dos documentos a alegação de persistência e a cobrança de CI já existente.

### Comunicação entre responsáveis

Explicar a Verify/Serve: muda identidade exportada, preserva default e linhas existentes. Separar versão do pacote, versão do contrato e versão gravada por cada instância.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Elevar tudo para 0.3.0 mudaria a identidade do pacote além desta correção e confundiria a versão do pacote com a extensão de contrato v0.3. Que caso o teste ainda não cobre? — Os testes fixam a coerência entre pyproject, __version__ e o default de Verdict.verify_version, que já era 0.1.0; o uso externo de __version__ não foi inventariado, e nada aqui sustenta falar em migração de linhas persistidas. Como eu explicaria isso para outro pod? — A PR muda só a identidade exportada pelo módulo; instâncias já gravavam 0.1.0 pelo default, e se uma atualização futura deve mudar esse default automaticamente é tema da política de versão em DEC-N2.

### Próxima ação e encerramento

Revisor/mantenedor: entrada 3955f9d e três checks verdes; saída decisão de integração. Corrigir F19/DEC-N2 e resumos derivados sem transformar política futura em gate desta PR.

<a id="item-007"></a>

## PR#163 — test(serve): pin search_kb plan_json hits over both transports

Frente: fila_prs. Encaminhamento: integracao_empilhada_a_decidir.

### Identidade e estado

PR #163 — test(serve): pin search_kb plan_json hits over both transports. Autor: gustocezar; aberta. Base codex/serve-transport-parity-156@a3ed9723af9461bd8f2ea9ad60347635b1254bad; head 9a7e4c1a775389b60bd33a0a4b61a63234ad8ae4. 1 arquivo(s). Origens: S24; #156; dependência concreta de #157. Autor não equivale a owner designado para o próximo passo.

### Intenção e benefício

Exercitar search_kb quando existe um resultado positivo de plan_json, incluindo conteúdo e proveniência, para que ausência compartilhada de dados não mascare perda da consulta de planos.

### Feito, faltante e não comprovado

Um arquivo novo com três testes e 118 linhas usa helpers introduzidos em #157. Base é codex/serve-transport-parity-156@a3ed972, não main. Nenhum check no head. Workflow desta branch filtra PRs para main e pushes main/feat/**/fix/**; esta combinação codex→codex não dispara automaticamente.

### Linhagem

#157 → helpers → 9a7e4c1/#163 → #156. O corpo relata 575 testes em árvore combinada e mutação removendo a consulta de planos. Integrar esta PR como aberta a integra na branch #157; não é automaticamente uma integração prematura na main.

### Fontes e corte

Fontes primárias: fontes/pr163-files.json (diff integral retornado pela API), fontes/pr163-checks.json (0 checks), fontes/pr163-reviews.json (0 reviews), fontes/current-open-pulls.json (corpo e topologia). Consulta em 16/10/2026, 18:29–18:31 UTC; timestamp preciso em cada recibo. Fontes de contexto adicionais: ver fontes/ e INVENTARIO-FONTES.json.

### Classe e limite da evidência

DIRETO: imports, conteúdo positivo plan_json, token vinculado, esquema e fluxos ausente/diferente; base/head e zero checks; workflow com workflow_dispatch. RELATADO: testes/mutações locais. Ausência de disparo automático não significa impossibilidade de prova manual.

### Fluxo

FakeSplitSearch: findings vazios + plano presente → search_kb via MCP/HTTP → payload igual com snippet/fingerprint/source/untrusted_fields. Helpers vêm da base #157. Não há execução SQL real.

### Consequências e risco

Risco de perder helpers ao transportar o commit isolado. Uma suíte verde de #157 não cobre este novo head. O caso positivo melhora cobertura, mas não prova limites top_k fora do valor exercitado nem rede real.

### Alternativas e recomendação

Recomendação: revisar #157 e #163 como pilha; integrar #157 e depois reposicionar #163 sobre main, conferindo diff e prova. Alternativa válida: integrar #163 na branch #157 e validar a combinação inteira antes de main. Cherry-pick isolado exige levar ou substituir os helpers.

### Dependências e paralelismo

Dependência técnica de helpers de #157; decisão humana sobre método de integração. Nenhuma dependência da política Verify. workflow_dispatch existe no arquivo; viabilidade de disparo e ref precisa ser verificada quando autorizado.

### Plano e aceite propostos

Escolher método, preservar helpers, recalcular diff/base e obter checks adequados à árvore que efetivamente será integrada. Aceite: caso plan_json positivo falha quando sua consulta é removida, sem igualdade vazia; registrar novo SHA/base e limite da prova.

### Comunicação entre responsáveis

Comunicar explicitamente branch de destino e motivo de zero checks. Evitar instrução genérica de merge direto em main ou afirmação de que nenhuma prova pode existir antes do rebase.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Levar o commit isolado para main sem os helpers de #157 quebraria os imports, e tratar o verde da base #157 como prova faria o novo head passar sem evidência própria. Que caso o teste ainda não cobre? — A prova precisa corresponder à árvore e ao escopo escolhidos para integração; o verde da base não cobre automaticamente a alteração da PR. A forma de obter essa prova é decisão do mantenedor. Como eu explicaria isso para outro pod? — Hoje um merge desta PR entraria na branch codex/serve-transport-parity-156 da #157, não na main; a pilha compartilha os helpers, mas cada head precisa de checks correspondentes à árvore que será integrada.

### Próxima ação e encerramento

Mantenedor/autor: entrada pilha #157→#163 e workflow filtrado; saída método escolhido, árvore de integração identificada e validação correspondente. Não mesclar nem disparar CI nesta auditoria.

<a id="item-008"></a>

## PR#164 — docs: align Serve and Verify docs with current contract

Frente: fila_prs. Encaminhamento: revisao_documental_e_integracao.

### Identidade e estado

PR #164 — docs: align Serve and Verify docs with current contract. Autor: gustocezar; aberta. Base main@c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; head 5d42763aaf1a74e707b41e9958e4a198bfa971a3. 3 arquivo(s). Origens: CL-02; DEC-N3; documentação atual de contrato/CI. Autor não equivale a owner designado para o próximo passo.

### Intenção e benefício

Corrigir READMEs para contrato v0.6, oito tools, dependências HTTP e distinção entre testes locais e CI. No Verify, distinguir coluna disponível de uso efetivo pelo predictor.

### Feito, faltante e não comprovado

Três READMEs mudam. Zero checks é compatível com paths-ignore para Markdown no workflow; zero reviews. Makefile confirma quatro lanes Python, root e Scala local; CI padrão e JAR têm cobertura diferente. Predictor não lê executor_run_time_ms apesar de a coluna existir.

### Linhagem

#132/#134/#148/#160 e estado atual → 5d42763/#164. CL-02 cobre comentários/docstrings remanescentes em predict.py e models.py. #179 estuda uso de trabalho medido; não é implementada por esta documentação.

### Fontes e corte

Fontes primárias: fontes/pr164-files.json (diff integral retornado pela API), fontes/pr164-checks.json (0 checks), fontes/pr164-reviews.json (0 reviews), fontes/current-open-pulls.json (corpo e topologia). Consulta em 16/10/2026, 18:29–18:31 UTC; timestamp preciso em cada recibo. Fontes de contexto adicionais: ver fontes/ e INVENTARIO-FONTES.json.

### Classe e limite da evidência

DIRETO: diff e fontes main-Makefile, main-workflow, main-contract, main-server, main-serve-pyproject, main-predict e main-verify-models. Documentação não comprova runtime. O texto de job_conf deve acompanhar o contrato capturado; não autoriza inventar defaults ausentes.

### Fluxo

Código/contrato/workflow observado → README corrigido → expectativa do contribuidor. Coluna de runtime medida presente no schema ≠ predictor consumindo-a; este ainda estima por intervalos.

### Consequências e risco

Risco documental baixo: explicar mal CI pode prometer cobertura inexistente. Comentários antigos em código podem manter contradição mesmo após README corrigido; esse resíduo não torna o diff correto tecnicamente dependente de refatoração.

### Alternativas e recomendação

Recomendação: aceitar escopo documental após revisão; corrigir CL-02 nesta PR se acordado ou em follow-up pequeno. Misturar implementação do predictor com redação amplia risco e depende de estudo #179. Ambas as escolhas de texto são reversíveis.

### Dependências e paralelismo

Sem gate de CI de código obrigatório inventado para Markdown ignorado. DEC-N3 escolhe escopo de comentários; M1 não bloqueia estudos do contrato M3 nem esta revisão.

### Plano e aceite propostos

Confrontar cada afirmação com Makefile, workflow, servidor, deps e predictor. Decidir onde ficam os comentários remanescentes. Aceite: texto coerente e limites de testes locais/CI/runtime explícitos. Não rodar produto só para validar estes READMEs.

### Comunicação entre responsáveis

Comunicar a todos os pods que make test e CI não têm a mesma cobertura, e que coluna disponível não significa consumo no predictor. Referir #179 como estudo separado.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Misturar a mudança do predictor com a redação ampliaria o risco e dependeria do estudo #179; um README impreciso sobre CI prometeria cobertura que o workflow não tem. Que caso o teste ainda não cobre? — Documentação não comprova runtime; os comentários contrários em predict.py e models.py ficam no escopo de CL-02, e onde registrar esse follow-up de texto depende da escolha de escopo em DEC-N3. Como eu explicaria isso para outro pod? — make test (quatro lanes Python, root e Scala local) e o CI padrão não têm a mesma cobertura, e executor_run_time_ms existir no schema não significa que o predictor a lê; o uso de trabalho medido é estudo separado em #179.

### Próxima ação e encerramento

Revisor documental/mantenedor: entrada 5d42763 e fontes no SHA c3c3ea3; saída revisão, decisão de escopo CL-02 e integração. Sem exigir nova prova funcional para mudança só de texto.

<a id="item-009"></a>

## #1 — Collector MVP: configuração e rota de ingestão

Frente: historico. Encaminhamento: historico_preservado_com_justificativa.

### Identidade e estado

Issue #1: [Collector] OTel Collector MVP config: receivers, processors, exporters?. Autor Guilherme-daCosta; encerrada em 2026-09-17T16:45:03Z; motivo API completed. Esta ficha corrige a leitura histórica; não muda o GitHub.

### Intenção e benefício

Definir configuração mínima do Collector que recebe OTLP e exporta para ClickHouse, oferecendo um caminho concreto à equipe de ingestão.

### Feito, faltante e não comprovado

O comentário de encerramento aponta collect/config.yaml, infra/otel-collector-config.yaml, collect/README.md e otelcol validate. Relata receivers gRPC/HTTP, memory_limiter, batch e exporter nativo ClickHouse. São indícios explícitos de implementação/validação; os respectivos bytes e runs históricos não foram reexecutados nesta ficha.

### Linhagem

Issue → discussão/comentário(s) de encerramento → arquivos e controles ali citados → estado fechado. Uma PR com Closes não foi identificada por este recorte; isso não significa ausência de implementação, teste ou review. Comentários: https://github.com/luanmorenommaciel/apex/issues/1#issuecomment-5718017965.

### Fontes e corte

Fontes: snapshot preservado issues_all.json, item number=1; icomments_all.json pelos URLs https://github.com/luanmorenommaciel/apex/issues/1#issuecomment-5718017965; ficha anterior C07-HISTORICO-ENCERRADO.md. Consulta original do pacote em 16/10/2026; main atual c3c3ea3 para a distinção de versões.

### Classe e limite da evidência

DIRETO: estado, autoria e existência do texto dos comentários. RELATADO: implementação, parâmetros e validação descritos no fechamento. NÃO VERIFICADO nesta ficha: comportamento atual em runtime e cadeia completa de commits/reviews/testes. Não converter ausência de link Closes em ausência de prova.

### Fluxo

Listener → OTLP :4317/:4318 → processors → exporter ClickHouse. Fluxo relatado pelo comentário; configuração atual e tráfego real não verificados neste recorte.

### Consequências e risco

Perder o comentário apaga a localização da configuração e do controle de validação. A versão 0.156.0 citada é histórica; não transferir para a implantação atual.

### Alternativas e recomendação

Preservar como concluída e anotar o comentário. Nova divergência confirmada justificaria follow-up delimitado; reabrir só por ausência de Closes é injustificado.

### Dependências e paralelismo

Nenhuma nova dependência imposta ao item encerrado. Localizar um recibo histórico é trabalho de linhagem, não bloqueio de produto. Um follow-up atual precisa de lacuna específica e owner a confirmar.

### Plano e aceite propostos

Se um operador precisar reproduzir a configuração, partir dos arquivos citados e da versão desejada. A auditoria não cria nova entrega de Collector.

### Comunicação entre responsáveis

Na consolidação, explicar por que #1 permanece fechada e apontar o comentário que sustenta sua interpretação. Nenhuma mensagem externa foi enviada; eventual follow-up deve distinguir fato atual de relato histórico.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Reabrir só por falta de Closes descartaria o comentário de encerramento, que localiza collect/config.yaml, infra/otel-collector-config.yaml e o controle otelcol validate. Que caso o teste ainda não cobre? — otelcol validate checa a configuração, não tráfego real; se a configuração atual ainda coincide com o relato histórico, inclusive a versão 0.156.0, não foi verificado neste recorte. Como eu explicaria isso para outro pod? — #1 continua fechada porque o comentário de encerramento aponta os arquivos com receivers gRPC/HTTP, memory_limiter, batch e exporter ClickHouse; é relato histórico, não garantia atual da implantação.

### Próxima ação e encerramento

Próxima ação de produto: nenhuma criada por esta revisão. Ação documental: conservar esta correção e, se for necessário certificar uma garantia atual, abrir recorte próprio com fonte, owner e critério discriminante.

<a id="item-010"></a>

## #2 — Collector PII: controles apontados no encerramento

Frente: historico. Encaminhamento: historico_preservado_com_justificativa.

### Identidade e estado

Issue #2: [Collector] PII scrub processor: quais campos mask?. Autor Guilherme-daCosta; encerrada em 2026-09-17T16:45:05Z; motivo API completed. Esta ficha corrige a leitura histórica; não muda o GitHub.

### Intenção e benefício

Identificar quais campos são removidos ou transformados antes da exportação para reduzir exposição de informações pessoais.

### Feito, faltante e não comprovado

Comentário de fechamento cita transform/redaction com SHA256 de query_text, attributes/scrub removendo file_path/email e redaction/pii com HMAC-SHA256 e chave via ambiente, além de redaction no JAR. São alegações históricas localizadas; não uma auditoria atual da efetividade criptográfica ou de todas as entradas.

### Linhagem

Issue → discussão/comentário(s) de encerramento → arquivos e controles ali citados → estado fechado. Uma PR com Closes não foi identificada por este recorte; isso não significa ausência de implementação, teste ou review. Comentários: https://github.com/luanmorenommaciel/apex/issues/2#issuecomment-5718018406.

### Fontes e corte

Fontes: snapshot preservado issues_all.json, item number=2; icomments_all.json pelos URLs https://github.com/luanmorenommaciel/apex/issues/2#issuecomment-5718018406; ficha anterior C07-HISTORICO-ENCERRADO.md. Consulta original do pacote em 16/10/2026; main atual c3c3ea3 para a distinção de versões.

### Classe e limite da evidência

DIRETO: estado, autoria e existência do texto dos comentários. RELATADO: implementação, parâmetros e validação descritos no fechamento. NÃO VERIFICADO nesta ficha: comportamento atual em runtime e cadeia completa de commits/reviews/testes. Não converter ausência de link Closes em ausência de prova.

### Fluxo

Emissão JAR com redaction → Collector transforma/remove campos → exportação. Ordem exata e cobertura por campo dependem de consultar configuração e testes nas refs relevantes.

### Consequências e risco

A ficha anterior omitia a trilha de controles. Nem issue fechada nem um nome de processor provam ausência de vazamento em qualquer entrada. Não foi observado incidente nesta revisão.

### Alternativas e recomendação

Preservar encerramento e registrar controles relatados. Caso um campo escape em evidência específica, abrir follow-up para esse caminho. Reexecutar toda política sem motivação confirmada amplia indevidamente o escopo.

### Dependências e paralelismo

Nenhuma nova dependência imposta ao item encerrado. Localizar um recibo histórico é trabalho de linhagem, não bloqueio de produto. Um follow-up atual precisa de lacuna específica e owner a confirmar.

### Plano e aceite propostos

Ação eventual de verificação deve usar campos sintéticos e comparar entrada/saída sem dados reais; não é requisito novo para manter o encerramento histórico.

### Comunicação entre responsáveis

Na consolidação, explicar por que #2 permanece fechada e apontar o comentário que sustenta sua interpretação. Nenhuma mensagem externa foi enviada; eventual follow-up deve distinguir fato atual de relato histórico.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Ler o encerramento como garantia de ausência de vazamento prometeria cobertura universal; apagar a trilha de controles relatada repetiria a omissão da ficha anterior. Que caso o teste ainda não cobre? — Falta localizar o teste que separa campo removido (file_path e email em attributes/scrub) de campo pseudonimizado (query_text por SHA256 e redaction/pii por HMAC-SHA256); efetividade criptográfica e todas as entradas não foram auditadas. Como eu explicaria isso para outro pod? — Há duas camadas relatadas, redaction no JAR e transformação no Collector, e uma pode cobrir falha da outra em campos específicos; nenhuma delas, nem a issue fechada, prova ausência de vazamento em qualquer entrada.

### Próxima ação e encerramento

Próxima ação de produto: nenhuma criada por esta revisão. Ação documental: conservar esta correção e, se for necessário certificar uma garantia atual, abrir recorte próprio com fonte, owner e critério discriminante.

