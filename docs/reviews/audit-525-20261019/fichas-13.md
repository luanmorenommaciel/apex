# Fichas documentais — lote 13

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-121"></a>

## S04 — Validação visual das telas via HTTP

Frente: Pod 1/Front. Encaminhamento: AGRUPAR_PROVA_BROWSER.

### Identidade e estado

S04 — Validação visual das telas via HTTP. Tipo: runtime/UI; frente: Pod 1/Front. #172 aberta; nenhum browser foi executado nesta revisão. O autor de um artefato não é automaticamente o responsável pelo próximo passo.

### Intenção e benefício

Comprovar a apresentação das telas no perfil DATA_SOURCE=http, incluindo estado de dado, ausência e erro que um usuário precisa distinguir.

### Feito, faltante e não comprovado

Existe seleção da fonte/API no Front e proxy /v1 no nginx. A #172 exige renderização real de telas selecionadas e explicita ausência/indisponibilidade. Recibos API de #156 não comprovam DOM, navegação, cache de config ou mensagens visuais.

### Linhagem

S04 deriva do resíduo visual #129 → #172; não recebe aceite por #157/#159 nem por S03 isolado. O elo browser/ref/fixture/captura ainda deve ser anexado ao acompanhamento.

### Fontes e corte

Fontes efetivamente lidas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; fontes/batch-public-sources/issue-172.md; fontes/main-http.txt; fontes/main-repository.txt; fontes/batch-public-sources/front__nginx.conf.txt. Registro histórico preservado até 01/10; reconciliação/publicação de 11/10; snapshots públicos de 16/10/2026. Código, quando citado, refere-se à main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. As fontes de narrativa não substituem o código/recibo identificado.

### Classe e limite da evidência

FATO OBSERVADO: o conteúdo e os estados documentais discriminados nos campos 3–5. RELATO HISTÓRICO: resultados atribuídos a autores/recibos, sem reexecução nesta auditoria. INFERÊNCIA: consequências condicionais do campo 8. PROPOSTA: alternativas e plano abaixo. DECISÃO PENDENTE: escolhas humanas explicitadas. Teste local, CI em um head, integração e aprovação humana conservam escopos separados.

### Fluxo

Proposto: config.js define http → repository HTTP → requisição same-origin → JSON ou falha → estado da tela → evidência de navegação. Ausência conhecida e falha da fonte precisam retornar estados distintos.

### Consequências e risco

Uma tela vazia pode esconder erro de credencial ou indisponibilidade; zero visual pode ser confundido com medição. Risco de experiência do usuário, sem frequência ou incidente estimados.

### Alternativas e recomendação

Escolher pequeno conjunto de telas por tipo de resposta é proporcional. Screenshots de fixtures sem rede caracterizam visual, mas não o trajeto HTTP; repetir todas as chamadas MCP não substitui a prova browser.

### Dependências e paralelismo

S03 fornece o proxy para uma prova completa, mas cenários e expectativas visuais podem ser preparados em paralelo. Escolher perfil/autenticação vigente; mudança de política em #171 é decisão distinta.

### Plano e aceite propostos

Inventariar telas/estados e fonte dos dados; fixar árvore/imagem; executar posteriormente navegação real com dados, ausência, 401 e store indisponível; observar requests, DOM e mensagens; incluir refresh para /config.js sem cache. Aceite: estados não se confundem, rotas exercitadas e não exercitadas identificadas, cleanup próprio registrado.

### Comunicação entre responsáveis

Na #172, nomear telas, browser, perfil e fixture; não chamar screenshot de evidência de toda a API nem narrar valores sintéticos como produção.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Converter 401 em lista vazia esconderia erro de credencial, e mostrar zero visual onde há ausência confundiria indisponibilidade com medição. Que caso o teste ainda não cobre? — Nenhum browser foi executado; faltam navegação real com dados, ausência, 401, store indisponível e refresh de /config.js sem cache, e as telas não exercitadas precisam ser listadas. Como eu explicaria isso para outro pod? — A ausência conhecida e a falha da fonte percorrem config.js, repository HTTP e requisição same-origin até estados de tela distintos; recibos de API da #156 não comprovam DOM nem mensagens visuais.

### Próxima ação e encerramento

Front com apoio Serve a confirmar: entrada matriz de telas e perfil HTTP; saída plano e recibo visual delimitado. S04 encerra quando o critério de browser da #172 é demonstrado ou explicitamente revisto pelo mantenedor.

<a id="item-122"></a>

## S05 — Exposição de /docs e /openapi.json sem token

Frente: Pod 3/Segurança. Encaminhamento: DECIDIR_POLITICA_SCHEMA_POR_PERFIL.

### Identidade e estado

S05 — Exposição de /docs e /openapi.json sem token. Tipo: decisão; frente: Pod 3/Segurança. #171 aberta; auth.py protege /v1 com exceções públicas e não protege docs/OpenAPI por esse prefixo. O autor de um artefato não é automaticamente o responsável pelo próximo passo.

### Intenção e benefício

Tornar explícita a exposição de /docs e /openapi.json em cada perfil, para que operador e consumidor conheçam a fronteira pública.

### Feito, faltante e não comprovado

O middleware chama o handler normalmente fora de API_PREFIX ou em PUBLIC_PATHS. Isso confirma que o gate /v1 não cobre docs/schema; não prova vazamento de dados ou comprometimento. A decisão originalmente aberta em #129 agora está em #171.

### Linhagem

S05 → questão de revisão #129 → publicação #171. Falta decisão ratificada por responsável da política; nenhuma PR de bloqueio automático é requerida só por existir schema público.

### Fontes e corte

Fontes efetivamente lidas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; fontes/batch-public-sources/issue-171.md; fontes/batch-public-sources/serve__src__apex_api__auth.py.txt. Registro histórico preservado até 01/10; reconciliação/publicação de 11/10; snapshots públicos de 16/10/2026. Código, quando citado, refere-se à main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. As fontes de narrativa não substituem o código/recibo identificado.

### Classe e limite da evidência

FATO OBSERVADO: o conteúdo e os estados documentais discriminados nos campos 3–5. RELATO HISTÓRICO: resultados atribuídos a autores/recibos, sem reexecução nesta auditoria. INFERÊNCIA: consequências condicionais do campo 8. PROPOSTA: alternativas e plano abaixo. DECISÃO PENDENTE: escolhas humanas explicitadas. Teste local, CI em um head, integração e aprovação humana conservam escopos separados.

### Fluxo

Observado: request path → filtro de prefixo/exceção → comparação de token para /v1 → 401 antes do handler; docs/schema seguem a rota normal da aplicação. Proposto: perfil → política ratificada → controles de acesso.

### Consequências e risco

Operadores podem supor proteção que não existe; exposição de documentação tem impacto diferente de acesso a dados. Risco condicional ao perfil, sem incidente inferido.

### Alternativas e recomendação

Manter público no perfil local, proteger ou desligar em perfil compartilhado são opções legítimas. Escolher por ameaça e suporte; desligar tudo prejudica descoberta, exigir token complica clientes de schema. Reversibilidade deve constar na configuração.

### Dependências e paralelismo

Mantenedor e responsável de implantação decidem perfis; S06 define custódia do token, mas a tabela de rotas pode ser elaborada em paralelo. #122 é fronteira Ask diferente e não é gate universal.

### Plano e aceite propostos

Listar rotas e exceções; propor matriz local/compartilhado; registrar opção, dono e razão; só então eventual mudança e teste de sem token/token inválido/token válido para schema e API. Aceite: política documentada e comportamento correspondente, preservando health público se esse for o contrato.

### Comunicação entre responsáveis

Explicar que schema público não equivale a dados públicos; citar auth.py e separar decisão de documentação de qualquer alerta de segurança.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Proteger ou desligar o OpenAPI sem considerar clientes de schema pode quebrar quem precisa lê-lo, e supor que docs estão protegidos pelo gate /v1 engana o operador. Que caso o teste ainda não cobre? — Conferir a política escolhida para docs, schema e health contra os controles existentes. O recorte consultado não autoriza afirmar que nenhum teste de documentação exista. Como eu explicaria isso para outro pod? — Schema público não equivale a dados públicos: o gate cobre o prefixo /v1, e /docs e /openapi.json seguem a rota normal; a política por perfil local ou compartilhado é decisão da #171.

### Próxima ação e encerramento

Mantenedor da API/implantação a confirmar: entrada matriz de rotas; saída decisão de exposição e folha de comportamento se necessária. Encerrar S05 ao resolver esse critério em #171; não implementar uma opção nesta auditoria.

<a id="item-123"></a>

## S06 — Onde o token HTTP fica (browser vs injeção pelo nginx)

Frente: Pod 3+Pod 1. Encaminhamento: DECIDIR_CUSTODIA_TOKEN.

### Identidade e estado

S06 — Onde o token HTTP fica (browser vs injeção pelo nginx). Tipo: decisão arquitetura; frente: Pod 3+Pod 1. #171 aberta; nginx atual encaminha /v1 sem injeção explícita de Authorization. O autor de um artefato não é automaticamente o responsável pelo próximo passo.

### Intenção e benefício

Definir quem fornece, mantém e renova o token da API v1 por perfil, tornando a fronteira de confiança compreensível ao operador.

### Feito, faltante e não comprovado

O proxy fixa Host e upstream; não injeta Authorization no trecho /v1. A configuração atual permite o modelo com token do cliente descrito em #129. Isso não prova que qualquer implantação real armazena token de forma específica ou que houve exposição indevida.

### Linhagem

S06 → pergunta de #129 → #171. #122 trata Ask/BFF e pode informar futuras opções, mas a política da API v1 já existente tem identidade própria.

### Fontes e corte

Fontes efetivamente lidas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; fontes/batch-public-sources/issue-171.md; fontes/batch-public-sources/front__nginx.conf.txt; fontes/main-http.txt. Registro histórico preservado até 01/10; reconciliação/publicação de 11/10; snapshots públicos de 16/10/2026. Código, quando citado, refere-se à main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. As fontes de narrativa não substituem o código/recibo identificado.

### Classe e limite da evidência

FATO OBSERVADO: o conteúdo e os estados documentais discriminados nos campos 3–5. RELATO HISTÓRICO: resultados atribuídos a autores/recibos, sem reexecução nesta auditoria. INFERÊNCIA: consequências condicionais do campo 8. PROPOSTA: alternativas e plano abaixo. DECISÃO PENDENTE: escolhas humanas explicitadas. Teste local, CI em um head, integração e aprovação humana conservam escopos separados.

### Fluxo

Observado: browser HTTP → nginx repassa requisição → middleware da API valida token. Proposto alternativamente: cliente autenticado → proxy/gateway injeta credencial de serviço → API; essa alternativa ainda não está implementada nesta fonte.

### Consequências e risco

Sem custódia explícita, renovação e revogação podem falhar ou o operador confiar no perfil errado. Não inferir risco individual, segredo presente ou incidente a partir do desenho.

### Alternativas e recomendação

Token no browser é simples para uso local; injeção no proxy evita entregá-lo ao browser, mas exige autenticar/admitir clientes antes da injeção; gateway acrescenta operação. A decisão precisa preservar isolamento e não criar proxy aberto.

### Dependências e paralelismo

Definição de perfis e identidade do chamador; coordenar S05. Estudo não depende de merge de toda fila nem de concluir #115/#117. Implantação/gateway exige escopo e autorização posteriores.

### Plano e aceite propostos

Desenhar quem emite/guarda/renova/revoga; nomear responsável; definir recusa para cliente não autorizado e segredo ausente; preparar casos de passagem legítima, header indevido e renovação. Aceite: matriz por perfil e prova da opção implementada quando houver mudança; exemplos só com valores fictícios.

### Comunicação entre responsáveis

Explicar por que esconder o token no proxy exige controle na entrada; publicar apenas nomes de configuração, nunca credenciais, e declarar limite entre decisão e deployment.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Injetar token no proxy para qualquer visitante criaria um proxy aberto: esconder o token do browser exige autenticar o cliente antes da injeção. Que caso o teste ainda não cobre? — A renovação e a revogação do token não têm caso, nem a recusa para cliente não autorizado ou segredo ausente; não há evidência de como uma implantação real armazena o token. Como eu explicaria isso para outro pod? — Hoje o nginx repassa /v1 sem injetar Authorization, e o middleware da API valida o token do cliente; quem autentica o usuário e quem autentica o serviço é a decisão de custódia na #171.

### Próxima ação e encerramento

API/Front e operador a confirmar: entrada perfis e requisitos; saída decisão de custódia/renovação e plano verificável. Encerramento em #171 depende de responsabilidade e comportamento definidos, não de criar automaticamente um gateway.

<a id="item-124"></a>

## S07 — Decidir e implementar /ask

Frente: Pod 3+Pod 1. Encaminhamento: DECIDIR_ASK_SOBRE_API_INTEGRADA.

### Identidade e estado

S07 — Decidir e implementar /ask. Tipo: estudo/epic; frente: Pod 3+Pod 1. #122 aberta sem assignee; #129 integrada. Candidato local é evidência histórica, não implementação aceita. O autor de um artefato não é automaticamente o responsável pelo próximo passo.

### Intenção e benefício

Decidir a superfície Ask e a sequência de entregas sem duplicar a API de leitura já integrada nem mudar silenciosamente semânticas dos oito tools.

### Feito, faltante e não comprovado

A #122 pede proceed/defer/reject, perfis local/compartilhado, owners, ordem e prova. O texto parte da fronteira #102; #129 já acrescentou API v1, portanto a decisão precisa desse reenquadramento. Conflitos históricos do candidato com fab6620 não são uma comparação nova contra c3c3ea3.

### Linhagem

S07 → candidato Ask V2 c73269f, cópia sanitizada relatada 9e68c10 → #122; DEC-17 registra preservação, não publicação. #129 é mudança posterior da base arquitetural. Faltam decisão atual, contrato ratificado e folhas aceitas para implementação.

### Fontes e corte

Fontes efetivamente lidas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; fontes/batch-rest-issues-sources/issue-122.md; fontes/main-server.txt; fontes/main-http.txt; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/DECISION-REGISTER.md. Registro histórico preservado até 01/10; reconciliação/publicação de 11/10; snapshots públicos de 16/10/2026. Código, quando citado, refere-se à main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. As fontes de narrativa não substituem o código/recibo identificado.

### Classe e limite da evidência

FATO OBSERVADO: o conteúdo e os estados documentais discriminados nos campos 3–5. RELATO HISTÓRICO: resultados atribuídos a autores/recibos, sem reexecução nesta auditoria. INFERÊNCIA: consequências condicionais do campo 8. PROPOSTA: alternativas e plano abaixo. DECISÃO PENDENTE: escolhas humanas explicitadas. Teste local, CI em um head, integração e aprovação humana conservam escopos separados.

### Fluxo

Proposto: cliente Ask → same-origin → adaptador HTTP escolhido → serviços existentes/MCP → envelope de resultado. Fluxo preserva Fix como proposta e informa atribuição indisponível quando necessário.

### Consequências e risco

Publicar candidato integrado sem reenquadrar pode introduzir duas fronteiras HTTP ou alterar ferramentas. Confiança alta no risco arquitetural; conflito atual e comportamento runtime não foram reproduzidos.

### Alternativas e recomendação

Preferir avaliar extensão da API existente; BFF separado é opção com contrato/operação adicionais; adiar/rejeitar é legítimo. Nenhuma opção é escolhida pela auditoria, nem o candidato sanitizado vira baseline aceita.

### Dependências e paralelismo

#122 exige decisão antes de PR de implementação. Estudo de transporte e envelopes pode avançar com limites de #115/#117; não precisa esperar ambas fecharem. Política v1 #171 coordena perfis, não absorve Ask.

### Plano e aceite propostos

Atualizar mapa da fronteira atual; comparar candidato sanitizado apenas como referência; decidir proceed/defer/reject e owners; se proceed, ratificar envelope e slices contrato→Serve→Front ou sequência equivalente justificada. Controles: oito tools preservados, identidades não confiáveis recusadas, sem aplicação automática, ausências explícitas. Aceite de decisão é distinto de aceite funcional futuro.

### Comunicação entre responsáveis

Explicar à issue o que a #129 já entrega e o que Ask acrescentaria; registrar por que a opção atende perfis e quais provas ainda não existem.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Reutilizar o candidato Ask V2 integralmente pode criar duas fronteiras HTTP ou alterar os oito tools, porque ele parte da base anterior à API v1 da #129. Que caso o teste ainda não cobre? — A suíte do candidato Ask não foi aceita nem revalidada contra a API atual nesta ficha. Confirmar intenção e preservação dos tools antes de reaproveitar a proposta. Como eu explicaria isso para outro pod? — Transporte e semântica do diagnóstico são camadas separadas: Ask acrescentaria a superfície e o envelope, sem mudar os tools, aplicar fix ou inventar atribuição; proceed, defer ou reject segue na #122.

### Próxima ação e encerramento

Mantenedor com Pods 1/3 a confirmar: entrada #122, API atual e candidato preservado; saída decisão e plano de slices ou registro de adiamento/rejeição. S07 só encerra após escopo aprovado entregue e aceito, ou decisão explícita de não implementar.

<a id="item-125"></a>

## S08 — Caracterizar os oito tools antes de refactor (T19a)

Frente: Pod 3/Serve. Encaminhamento: REVISAR_INTEGRAR_PR_EXISTENTE.

### Identidade e estado

S08 — Caracterizar os oito tools antes de refactor (T19a). Tipo: teste de contrato; frente: Pod 3/Serve. #157 aberta no head a3ed972, 11 checks verdes do workflow antigo e zero reviews formais; #163 é descendente empilhada. O autor de um artefato não é automaticamente o responsável pelo próximo passo.

### Intenção e benefício

Caracterizar as respostas dos oito tools pelos transportes MCP/HTTP antes de um refactor, para que listar nomes ou comparar vazios não seja confundido com equivalência semântica.

### Feito, faltante e não comprovado

O diff #157 contém dois arquivos de testes para store populado, ausência e indisponibilidade; inclui reforço com mesmos argumentos. A antiga descrição de apenas lista de tools foi superada. CI cobre a3ed972, não futura integração; #156 relata transporte real delimitado. Falta review/decisão e reconciliação.

### Linhagem

S08/TS09B histórico → integração local com #129/#140 → #157 pública; S24 reforça mesma intenção com controle mais forte; #163 acrescenta positivo plan_json sobre os helpers. Aceite antigo de revalidação documental não aceita a implementação retroativamente.

### Fontes e corte

Fontes efetivamente lidas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; fontes/pr157-files.json; fontes/pr157-checks.json; fontes/pr157-reviews.json; fontes/batch-rest-issues-sources/issue-156.md. Registro histórico preservado até 01/10; reconciliação/publicação de 11/10; snapshots públicos de 16/10/2026. Código, quando citado, refere-se à main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. As fontes de narrativa não substituem o código/recibo identificado.

### Classe e limite da evidência

FATO OBSERVADO: o conteúdo e os estados documentais discriminados nos campos 3–5. RELATO HISTÓRICO: resultados atribuídos a autores/recibos, sem reexecução nesta auditoria. INFERÊNCIA: consequências condicionais do campo 8. PROPOSTA: alternativas e plano abaixo. DECISÃO PENDENTE: escolhas humanas explicitadas. Teste local, CI em um head, integração e aprovação humana conservam escopos separados.

### Fluxo

Observado no diff: fixture comum → call_tool MCP e route HTTP → comparação do payload e sinais esperados; cenários sem tabela/store indisponível verificam resposta correspondente. Runtime relatado em #156 é outra camada.

### Consequências e risco

Refactor pode conservar nomes e mudar respostas sem detecção se a fixture estiver vazia. O novo teste reduz esse risco para casos explícitos; não prova todos os parâmetros ou plataformas.

### Alternativas e recomendação

Revisar e integrar a PR já existente é preferível a recriar TS09B. Extrair serviços durante esta PR ampliaria o escopo; isso deve ocorrer depois com os testes como controle. Preservar recorte test-only torna a decisão reversível.

### Dependências e paralelismo

Nenhuma dependência serial universal de #158/#159; escolher árvore de integração. #163 depende dos helpers #157, e sua prova deve acompanhar a pilha. CI adicional só se diferenças da árvore o exigirem.

### Plano e aceite propostos

Revisar se cada tool recebe dado não vazio observável e o mesmo argumento nos caminhos; conferir ausência e falha; decidir integração; reconciliar #156 por árvore. Controle negativo útil: trocar a resposta populada por vazia deve falhar. Aceite S08: cobertura aprovada/integrada e resíduo S24/#163 identificado sem herdar verde indevidamente.

### Comunicação entre responsáveis

Na revisão, explicar os dois arquivos, origem TS09B/S24, limites de fakes e resultados por head; não dizer que refactor já ocorreu ou que CI antigo é prova da main.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Se os dois transportes devolvessem vazio, a comparação passaria sem provar comportamento; por isso a #157 usa store populado e argumentos idênticos. Que caso o teste ainda não cobre? — Parâmetros fora dos vetores escolhidos e plataformas reais não estão cobertos, e o CI verde vale para o head a3ed972, não para a integração futura; o positivo de plan_json é da #163. Como eu explicaria isso para outro pod? — Uma lista com oito nomes não prova oito comportamentos: o teste compara payloads com conteúdo pelos dois caminhos, e o refactor ainda não ocorreu.

### Próxima ação e encerramento

Revisor Serve/mantenedor a confirmar: entrada diff/checks a3ed972 e #156; saída parecer e decisão de integração com reconciliação. Fechar S08 quando a guarda correspondente estiver integrada/aceita ou decisão alternativa registrada.

<a id="item-126"></a>

## S09 — MCP sem credencial direta do ClickHouse

Frente: Pod 3/Serve. Encaminhamento: ESTUDAR_NECESSIDADE_CONSUMIDOR.

### Identidade e estado

S09 — MCP sem credencial direta do ClickHouse. Tipo: estudo; frente: Pod 3/Serve. Sem issue/PR própria localizada para migrar o MCP para HTTP; #129 integrada não realiza essa migração. O autor de um artefato não é automaticamente o responsável pelo próximo passo.

### Intenção e benefício

Avaliar se há cliente MCP que precise operar sem credencial direta de ClickHouse, e qual fronteira forneceria todas as primitivas usadas pelos tools.

### Feito, faltante e não comprovado

O ReadStore cria cliente ClickHouse com variáveis de conexão, e os tools existentes usam esse caminho. A API v1 oferece rotas aos consumidores HTTP; isso não torna o servidor MCP um cliente HTTP. Nenhum requisito de consumidor identificado foi demonstrado para exigir a inversão.

### Linhagem

S09 surge como gap de #129; não é implementação faltante prometida automaticamente pelo merge da API. Faltam consumidor, requisitos, decisão e contrato. Não confundir credencial no servidor MCP com credencial no browser.

### Fontes e corte

Fontes efetivamente lidas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; fontes/main-server.txt; fontes/lote2-serve__src__apex_mcp__ch.py.txt; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/pulls_all.json. Registro histórico preservado até 01/10; reconciliação/publicação de 11/10; snapshots públicos de 16/10/2026. Código, quando citado, refere-se à main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. As fontes de narrativa não substituem o código/recibo identificado.

### Classe e limite da evidência

FATO OBSERVADO: o conteúdo e os estados documentais discriminados nos campos 3–5. RELATO HISTÓRICO: resultados atribuídos a autores/recibos, sem reexecução nesta auditoria. INFERÊNCIA: consequências condicionais do campo 8. PROPOSTA: alternativas e plano abaixo. DECISÃO PENDENTE: escolhas humanas explicitadas. Teste local, CI em um head, integração e aprovação humana conservam escopos separados.

### Fluxo

Observado: cliente MCP → servidor/tools → ReadStore → ClickHouse. Alternativa proposta: MCP → serviço HTTP → primitiva de dados; essa nova aresta demanda autenticação, cobertura e tratamento de erros próprios.

### Consequências e risco

Migrar sem necessidade pode duplicar hops e falhas ou expor primitivas amplas; manter conexão direta exige custódia no servidor. Ambas são consequências condicionais, sem incidente observado.

### Alternativas e recomendação

Primeiro estudar um consumidor concreto. Manter MCP perto do store é válido; portar para HTTP se requisito justificar requer inventário de primitivas; oferecer gateway amplo só para cumprir o título criaria escopo sem benefício comprovado.

### Dependências e paralelismo

Owner Serve e consumidor; #129 é base disponível, #122 não decide automaticamente esta migração. Inventário offline independente de runtime, token e rede reais apenas em prova futura.

### Plano e aceite propostos

Identificar necessidade operacional; mapear primitiva por tool; comparar autenticação/latência/falhas e optar manter/adiar/migrar. Se migrar, contrato mínimo e testes de paridade, indisponibilidade e autorização antes de substituição. Aceite do estudo: decisão com justificativa; implementação só se adotada.

### Comunicação entre responsáveis

Esclarecer quem deixaria de possuir a credencial e em qual processo; não usar a promessa de HTTP para browser como prova de desacoplamento MCP.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Migrar o MCP para HTTP sem uma primitiva equivalente na API quebraria tools, e um gateway amplo só para cumprir o título criaria escopo sem benefício comprovado. Que caso o teste ainda não cobre? — Fluxos de falha e autorização de uma nova aresta MCP→HTTP não têm teste, e nenhum consumidor concreto que exija operar sem credencial direta foi demonstrado. Como eu explicaria isso para outro pod? — Hoje a credencial do ClickHouse fica no servidor MCP via ReadStore, não no browser; a API v1 serve consumidores HTTP e não torna o MCP um cliente HTTP.

### Próxima ação e encerramento

Owner Serve a confirmar: entrada inventário dos tools e caso de uso; saída decisão de escopo S09. Encerrar como rejeitado/adiado ou abrir entrega definida, sem classificar a conexão atual como defeito por si só.

<a id="item-127"></a>

## S10 — Piso Memory→Serve com proveniência (T35a/b)

Frente: Pod 3+Memory. Encaminhamento: AGRUPAR_CONTRATO_PISO_PROVENIENTE.

### Identidade e estado

S10 — Piso Memory→Serve com proveniência (T35a/b). Tipo: contrato/PR; frente: Pod 3+Memory. #117 aberta; item (a) trata piso Memory→Serve; não há nova integração aceita nesta revisão. O autor de um artefato não é automaticamente o responsável pelo próximo passo.

### Intenção e benefício

Entregar um piso de ruído contextualizado por origem, métrica e escala para Serve, evitando transformar um número do chamador ou de corpus em medição específica do run.

### Feito, faltante e não comprovado

compare_runs e summarise_recall aceitam noise_floor_pct do chamador e dizem que Serve não o mediu. A unidade aí é fração; replay usa percentuais. O comentário de #117 identifica o acoplamento como critério aberto. Não há base para ligar Memory automaticamente nem chamar fallback 15,9% de medição do caso.

### Linhagem

S10/T35a-b → #117(a) → DEC-05/06 de precedência/proveniência e ownership; S11 conserva falhas/conflitos. Correções #143/#144 validam entradas, mas não entregam a fonte Memory→Serve.

### Fontes e corte

Fontes efetivamente lidas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; fontes/lote2-serve__src__apex_mcp__diagnose.py.txt; fontes/lote2-issue117.json; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/DECISION-REGISTER.md. Registro histórico preservado até 01/10; reconciliação/publicação de 11/10; snapshots públicos de 16/10/2026. Código, quando citado, refere-se à main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. As fontes de narrativa não substituem o código/recibo identificado.

### Classe e limite da evidência

FATO OBSERVADO: o conteúdo e os estados documentais discriminados nos campos 3–5. RELATO HISTÓRICO: resultados atribuídos a autores/recibos, sem reexecução nesta auditoria. INFERÊNCIA: consequências condicionais do campo 8. PROPOSTA: alternativas e plano abaixo. DECISÃO PENDENTE: escolhas humanas explicitadas. Teste local, CI em um head, integração e aprovação humana conservam escopos separados.

### Fluxo

Proposto: evidência Memory por shape/escala/métrica → resultado com valor/unidade/proveniência ou ausência → política caller×Memory → compare/recall → afirmação delimitada. Hoje a aresta observada é caller → Serve.

### Consequências e risco

Usar piso de outra população pode certificar diferença espúria; escolher prioridade implícita pode ocultar conflito. Possibilidade técnica, sem taxa de ocorrência demonstrada.

### Alternativas e recomendação

Contrato pequeno de resultado proveniente é recomendado antes do adapter. Continuar caller-only é opção explícita com limite; importar Memory diretamente ou usar porta/adapter têm custos distintos. Não ampliar contrato sem owner.

### Dependências e paralelismo

Decidir precedência, unidade e compatibilidade em #117; desenho e matriz podem ocorrer já. Implementação depende da política escolhida e do produtor identificado, não de toda a prova runtime de #115.

### Plano e aceite propostos

Mapear produtor/caller/consumidores; definir resultado válido/ausente/incompatível; normalizar fração versus percentual; decidir prioridade e rastreabilidade; só depois adapter e controles S11. Aceite: origem e contexto sobrevivem até a narração, valores incompatíveis não certificam, documentação não diz que Serve mediu o que só recebeu.

### Comunicação entre responsáveis

Explicar a diferença entre piso fornecido, estimativa de corpus e medição contextual; informar unidade em cada fronteira e listar decisão de precedência ainda aberta.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Receber 15,9 onde se espera 0,159 inflaria o piso cem vezes, porque compare_runs e summarise_recall usam fração e o replay usa percentual; usar piso de outra população poderia certificar diferença espúria. Que caso o teste ainda não cobre? — Combinações de escala, métrica e shape entre o piso de Memory e o run comparado ainda não têm caso; hoje a única aresta observada é caller → Serve, e o fallback de 15,9% não é medição do caso. Como eu explicaria isso para outro pod? — O piso precisa chegar ao Serve com valor, unidade e proveniência: fornecido pelo chamador, estimado de corpus ou medido no contexto; o Serve não mediu o que só recebeu, e a precedência segue aberta na #117.

### Próxima ação e encerramento

Owners Memory/Serve a confirmar: entrada #117 e contratos atuais; saída tabela de proveniência/unidades/precedência e folha atômica se aprovada. S10 encerra com critério (a) implementado/aceito ou escopo explicitamente revisto, não só uma reunião.

<a id="item-128"></a>

## S11 — Falhas e conflitos do piso Memory→Serve (T35c)

Frente: Pod 3+Memory. Encaminhamento: AGRUPAR_CONTROLES_CONTRATO_PISO.

### Identidade e estado

S11 — Falhas e conflitos do piso Memory→Serve (T35c). Tipo: testes; frente: Pod 3+Memory. Descendente de S10; sem PR própria demonstrada. A ausência universal de testes não foi estabelecida. O autor de um artefato não é automaticamente o responsável pelo próximo passo.

### Intenção e benefício

Definir controles discriminantes para falta de histórico, métrica/escala incompatível, Memory indisponível e conflito com o chamador no futuro caminho de piso.

### Feito, faltante e não comprovado

Já existem ramos Serve para piso ausente/inválido e histórico insuficiente. Isso não exercita automaticamente a futura aquisição Memory→Serve. A afirmação histórica “não têm testes” precisa ser restrita à integração ainda não definida, sem apagar proteções atuais.

### Linhagem

S11/T35c → contrato S10/#117(a) → cenários de falha → adapter futuro. #144 cobre piso inválido na interpretação, não arbitragem entre duas fontes. Não há receipt desta nova matriz.

### Fontes e corte

Fontes efetivamente lidas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; fontes/lote2-serve__src__apex_mcp__diagnose.py.txt; fontes/lote2-issue117.json; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/DECISION-REGISTER.md. Registro histórico preservado até 01/10; reconciliação/publicação de 11/10; snapshots públicos de 16/10/2026. Código, quando citado, refere-se à main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. As fontes de narrativa não substituem o código/recibo identificado.

### Classe e limite da evidência

FATO OBSERVADO: o conteúdo e os estados documentais discriminados nos campos 3–5. RELATO HISTÓRICO: resultados atribuídos a autores/recibos, sem reexecução nesta auditoria. INFERÊNCIA: consequências condicionais do campo 8. PROPOSTA: alternativas e plano abaixo. DECISÃO PENDENTE: escolhas humanas explicitadas. Teste local, CI em um head, integração e aprovação humana conservam escopos separados.

### Fluxo

Proposto: fonte responde valor/ausência/erro/incompatibilidade → adapter preserva estado → política de conflito decide ou retém adjudicação → Serve explica o limite. Erro de consulta não pode virar piso zero.

### Consequências e risco

Um fallback silencioso pode aumentar confiança justamente quando a fonte falhou. Risco condicional ao desenho futuro; não é incidente atual.

### Alternativas e recomendação

Especificar matriz de estados agora é útil; implementar testes contra uma política não ratificada cristalizaria decisão implícita. Reutilizar controles existentes para ausência/invalidade evita duplicação, mas requer novos controles do adapter.

### Dependências e paralelismo

S10 precisa decidir semântica para expectativas finais; inventário de estados e casos negativos pode começar em paralelo. Nenhuma necessidade de runtime Spark para desenhar ou testar adapter com doubles depois.

### Plano e aceite propostos

Enumerar respostas Memory e entrada caller; escolher resultados esperados com owner; escrever controles futuros de timeout, histórico vazio, unidade trocada e conflito; distinguir ausência de falha nos logs/resultados. Aceite: teste falha se o adapter promove fallback a medição ou ignora conflito; comportamento vigente de piso válido preservado.

### Comunicação entre responsáveis

Descrever quais testes existentes são reutilizados e quais provarão a integração; não escrever “sem testes” para toda a lane, nem “coberto” só porque um parâmetro inválido é recusado.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Tratar timeout de Memory como piso zero aumentaria a confiança justamente quando a fonte falhou, e um fallback silencioso esconderia a falha. Que caso o teste ainda não cobre? — O conflito entre o piso do chamador e o de Memory não tem controle, nem histórico vazio ou unidade trocada; os ramos atuais de piso ausente e inválido não exercitam a futura aquisição Memory→Serve. Como eu explicaria isso para outro pod? — Ausência de histórico é um estado conhecido, e indisponibilidade de Memory é falha da fonte; o adapter preserva os dois e não promove fallback a medição, com expectativas a ratificar em S10.

### Próxima ação e encerramento

Engenheiro Serve/Memory a confirmar: entrada contrato S10 e ramos existentes; saída matriz de falhas com expectativas ratificadas, depois testes do adapter. Encerrar S11 quando os controles da integração adotada forem demonstrados ou a integração for rejeitada explicitamente.

<a id="item-129"></a>

## S12 — Catálogo de runbooks determinísticos (#112)

Frente: Pod 3/Serve. Encaminhamento: ESTUDAR_CATALOGO_SEM_EXECUTOR.

### Identidade e estado

S12 — Catálogo de runbooks determinísticos (#112). Tipo: estudo; frente: Pod 3/Serve. #112 aberta; assignee gustocezar no snapshot público. Isso não atribui automaticamente o próximo recorte. O autor de um artefato não é automaticamente o responsável pelo próximo passo.

### Intenção e benefício

Avaliar runbooks versionados com evidência obrigatória/opcional/ausente/inconclusiva para Serve, Memory e Verify, sem criar executor autônomo por consequência do estudo.

### Feito, faltante e não comprovado

A #112 é design study e proíbe inferir executor, runtime ou remediação. Comentário posterior relata schema/exemplos locais; não se verificou aqui validador implementado. A versão histórica de três schemas/quatro fixtures é relato delimitado, não prova de catálogo produtivo.

### Linhagem

Métodos Cowork/Kimi históricos → estudo #112 → exemplos locais relatados → decisão implementar/adiar/rejeitar pendente. Árvores antigas não são baseline atual; não depender de nova rodada Kimi/Gemini, canceladas pelo usuário.

### Fontes e corte

Fontes efetivamente lidas: ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/OPPORTUNITY-REGISTER.csv; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/MATRIX.json; ../parte-03-claude-v2/fontes/claude-v2/_build/inputs/PUBLICATION.json; fontes/batch-rest-issues-sources/issue-112.md; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/icomments_all.json. Registro histórico preservado até 01/10; reconciliação/publicação de 11/10; snapshots públicos de 16/10/2026. Código, quando citado, refere-se à main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. As fontes de narrativa não substituem o código/recibo identificado.

### Classe e limite da evidência

FATO OBSERVADO: o conteúdo e os estados documentais discriminados nos campos 3–5. RELATO HISTÓRICO: resultados atribuídos a autores/recibos, sem reexecução nesta auditoria. INFERÊNCIA: consequências condicionais do campo 8. PROPOSTA: alternativas e plano abaixo. DECISÃO PENDENTE: escolhas humanas explicitadas. Teste local, CI em um head, integração e aprovação humana conservam escopos separados.

### Fluxo

Proposto: check determinístico existente → runbook com versão/origem → evidência classificada → consumidor readonly → explicação opcional. A seta para execução/remediação não pertence ao escopo.

### Consequências e risco

Catálogo sem owner pode duplicar regras das lanes; ausência lida como sucesso pode produzir conselho indevido. São riscos de desenho, não defeitos confirmados no runtime atual.

### Alternativas e recomendação

Comparar pequeno schema compartilhado com documentação por lane; adotar só se consumidor e manutenção estiverem claros. Um catálogo genérico amplo cria segundo contrato; três exemplos coerentes são melhor unidade de avaliação.

### Dependências e paralelismo

Owner de versão e primeiro consumidor a confirmar. #107/#108 podem consumir no futuro, mas não são pré-condição para estudar exemplos. Não há gate de runtime para decidir o contrato offline.

### Plano e aceite propostos

Localizar schema/exemplos citados e separar proposta de validador; definir dono e compatibilidade; mapear ao menos positivo, ausente e inconclusivo a checks existentes; decidir adoção. Se implementar, validator deve recusar evidência insuficiente e versões incompatíveis; documentação conserva limites e fontes.

### Comunicação entre responsáveis

Explicar na #112 como se evita lógica paralela e por que catálogo não autoriza comandos. Atribuir exemplos históricos aos autores sem chamar opinião LLM de validação.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Tratar evidência ausente como sucesso produziria conselho indevido, e um catálogo genérico amplo criaria um segundo contrato paralelo às regras das lanes. Que caso o teste ainda não cobre? — Há exemplo de versão desconhecida no resultado da #112, além dos exemplos válidos e negativos bem formados. Isso não demonstra execução de um validador; preservar separadamente o schema/fixtures do recorte histórico. Como eu explicaria isso para outro pod? — Os runbooks referenciam checks determinísticos existentes, e cada lane continua dona das próprias regras; o catálogo não autoriza comandos nem executor de remediação.

### Próxima ação e encerramento

Mantenedor/assignee existente a confirmar: entrada #112 e artefatos citados; saída revisão do schema e decisão com primeiro consumidor. Encerramento do estudo exige escolha fundamentada; catálogo funcional é entrega posterior se adotada.

<a id="item-130"></a>

## DEC-01 — Regularizar billing do GitHub Actions da conta `luanmorenommaciel`

Frente: governanca_e_integracao. Encaminhamento: decisao_pendente_sem_autorizacao.

### Identidade e estado

DEC-01 — Regularizar billing do GitHub Actions da conta `luanmorenommaciel`. Papel proposto: titular da conta e mantenedor de CI; não é atribuição nova. Estado desta ficha: decisao_pendente_sem_autorizacao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Obter capacidade de execução verificável e distinguir falha de infraestrutura, falha de teste e ausência de coleta, sem pressupor diagnóstico financeiro atual.

### Feito, faltante e não comprovado

#130 relata bloqueio de billing em setembro; o bot na review #129 repete esse motivo, sem ser consulta financeira primária. O pacote de runs registra 68 CI entre 20/09 e 06/10 UTC: 56 failure e 12 cancelled. Há recibos de jobs para 22, com zero steps. Verdes posteriores em PRs e jar afastam a afirmação de indisponibilidade universal. Nenhuma consulta à conta foi feita.

### Linhagem

G01/registro → #130 e seus critérios de rerun de #126–128 → runs de datas/árvores diferentes → reconciliação operacional ainda necessária; DEC-01 não é prova de pagamento.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 48. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Demanda de prova → evento/ref/árvore escolhidos → disponibilidade do serviço → jobs/steps/logs → avaliação de cada suíte; cobrança é uma causa histórica relatada, não o resultado do teste.

### Consequências e risco

Supor bloqueio atual congela revisão sem evidência; supor desbloqueio completo por um verde de outra árvore encerra critérios prematuramente. Não há incidente financeiro novo constatado.

### Alternativas e recomendação

Primeiro verificar capacidade pelo registro técnico disponível e confirmar situação com o titular se necessário. Orçamento/alertas, runner próprio ou redução de carga são opções com custos e manutenção distintos; nenhuma foi selecionada aqui.

### Dependências e paralelismo

Revisão de código, desenho de política e estudos podem avançar em paralelo. Só uma prova hospedada específica depende de serviço disponível. #130 mantém critérios próprios; main verde não os substitui silenciosamente.

### Plano e aceite propostos

Preparar mapa critério #130 → run/tentativa/steps/logs. Se reruns antigos forem inviáveis ou inadequados, propor substituição justificada ao mantenedor. Em execução futura autorizada, registrar árvore e suites, sem aceitar só status da conta.

### Comunicação entre responsáveis

Atualização proposta na #130: distinguir a evidência antiga, verdes posteriores e critério ainda aberto; omitir detalhes financeiros privados.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Trocar os reruns originais de #126–#128 por uma execução na main perderia a prova sobre cada árvore e mudaria o critério da #130 sem decisão do mantenedor. Que caso o teste ainda não cobre? — Um workflow com jobs vazios, como os 242 jobs com zero steps nos 22 runs coletados entre 20/09 e 06/10, pode parecer falha de código; a conta não foi consultada, e o motivo de billing é relato. Como eu explicaria isso para outro pod? — Disponibilidade do serviço permite testar, mas só o resultado da suíte prova seu escopo; os verdes posteriores em PRs e no jar afastam indisponibilidade universal sem provar pagamento.

### Próxima ação e encerramento

Próxima ação proposta, titular da conta e mantenedor de CI: reconciliar os critérios da #130 e escolher a próxima prova necessária. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

