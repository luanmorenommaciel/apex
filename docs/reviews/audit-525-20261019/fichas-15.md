# Fichas documentais — lote 15

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-141"></a>

## DEC-N7 — Responsável por fechar Task-Specs

Frente: governanca_e_integracao. Encaminhamento: decisao_pendente_sem_autorizacao.

### Identidade e estado

DEC-N7 — Responsável por fechar Task-Specs. Papel proposto: mantenedor e autores das respectivas specs; não é atribuição nova. Estado desta ficha: decisao_pendente_sem_autorizacao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Fazer a fila de Task-Specs distinguir trabalho disponível, substituído, implementado e efetivamente aceito.

### Feito, faltante e não comprovado

A conferência de declarações cobre 87 specs e 19 planos, mas não equivale a revisão semântica desses 106 objetos. Três YAMLs têm falha de parse. Há specs com status aberto e caminhos existentes, além de referências antigas a cinco tools; isso não demonstra automaticamente entrega/aceite. Uma spec substituída já tem ficha própria; 86 seguem em revisão independente.

### Linhagem

Spec e seus B-n → eval declarado → implementação e recibo no SHA certo → aceite ou motivo de substituição → atualização rastreável de status. Plano integrado não fecha automaticamente suas folhas.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 408. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Intenção → comportamento verificável → observação → avaliação independente → estado documental; arquivo presente é somente um dos elos.

### Consequências e risco

Marcar done por grep ou presença de arquivo pode ocultar comportamento ausente. Executar spec antiga sem reconciliação pode repetir trabalho ou atingir superfície obsoleta.

### Alternativas e recomendação

Autor atualiza junto à entrega e revisor confere; ou responsável faz reconciliação periódica com prova por ID. Preservar histórico de supersessão, em vez de apagar specs para limpar a fila.

### Dependências e paralelismo

Definir responsabilidade pode avançar agora. Mudar estado de cada spec exige conferência própria; decisões PyPI/apex_status só bloqueiam folhas correspondentes, não toda a reconciliação.

### Plano e aceite propostos

Montar tabela spec/caminho/SHA/critério/recibo/status proposto. Parse inválido precisa reparo documental antes de reuso, sem execução nesta auditoria. Controle: tools/list e grep não devem passar por evidência de chamada/comportamento.

### Comunicação entre responsáveis

Propor regra em tasks/README ou CONTRIBUTING e atualizar cada folha com motivo e link ao aceite, sem declarar resultados nunca executados.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Sem um responsável definido pelo encerramento, um arquivo movido para done sem recibo vira falsa entrega, e ninguém confere se a spec antiga ainda vale antes de executá-la. Que caso o teste ainda não cobre? — Quem fecha precisa verificar se o eval mede o comportamento B-n ou só a existência de texto, como tools/list ou grep; três YAMLs falham no parse e precisam de reparo documental antes de reuso. Como eu explicaria isso para outro pod? — A decisão é quem registra e quem confere o encerramento de cada spec: autor na entrega com revisor, ou reconciliação periódica com prova por ID; o diretório não certifica o resultado.

### Próxima ação e encerramento

Próxima ação proposta, mantenedor e autores das respectivas specs: definir quem registra e quem confere o encerramento; concluir o mapa por spec. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-142"></a>

## NOV-07 — Conflito de desenho: checks exigidos (#125) × `paths-ignore` do CI enxuto

Frente: governanca_e_integracao. Encaminhamento: risco_condicional_confirmado_por_configuracao.

### Identidade e estado

NOV-07 — Conflito de desenho: checks exigidos (#125) × `paths-ignore` do CI enxuto. Papel proposto: administrador do repositório e mantenedor de CI; não é atribuição nova. Estado desta ficha: risco_condicional_confirmado_por_configuracao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Conciliar checks obrigatórios com workflows que são omitidos por filtros de caminhos.

### Feito, faltante e não comprovado

ci.yml ignora docs/**, **/*.md e jar/** em push/PR; jar.yml dispara em jar/** e no próprio workflow, além de agenda/manual. A documentação GitHub diz que filtro que omite o workflow pode deixar o check exigido pendente. Esse é risco condicional: não foi comprovada uma regra ativa causando bloqueio no APEX.

### Linhagem

#160/workflows → filtros observados → proposta #125 de exigir checks → NOV-07 explicita o caso docs/jar → escolha DEC-02.

### Fontes e corte

Origem preservada: C06B-CANDIDATOS-E-ACHADOS.md, linha 139. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Paths do diff → seleção de workflow → criação ou ausência de checks → avaliação da regra; skip de job condicional tem comportamento diferente de workflow não disparado.

### Consequências e risco

Uma sentinela colocada dentro do workflow já omitido também não executará. Trocar filtro sem avaliar custo/escopo pode adicionar carga sem ganho.

### Alternativas e recomendação

Desenhar workflow de resultado sempre presente com jobs condicionais coerentes; rever filtros e requisitos; ou usar mecanismo de política realmente suportado e inspecionado. Não basta dizer “adicionar sentinela” sem definir seu trigger.

### Dependências e paralelismo

Desenho paralelo à regularização de capacidade. A demonstração prática depende da configuração escolhida, não de fechar todas as issues de produto.

### Plano e aceite propostos

Preparar tabela de cenários docs-only/jar-only/código/misto e falha antecipada. Exigir que cada cenário produza um resultado interpretável. Configuração e PRs de demonstração são ações futuras separadas.

### Comunicação entre responsáveis

Registrar na #125 o contexto exato e como ausência, skipped, cancelled e failure serão tratados.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Uma sentinela colocada dentro do workflow ci.yml, que paths-ignore omite para docs/**, **/*.md e jar/**, também não roda e não destrava a PR; trocar o filtro sem avaliar custo pode adicionar carga sem ganho. Que caso o teste ainda não cobre? — O cenário jar-only dispara jar.yml, mas não necessariamente os checks que uma política da #125 exigiria; nenhuma regra ativa causando bloqueio foi comprovada no APEX. Como eu explicaria isso para outro pod? — O check obrigatório precisa existir no caminho que a política pretende avaliar, e skip de job condicional é diferente de workflow não disparado; a tabela de cenários docs-only, jar-only, código e misto entra na DEC-02.

### Próxima ação e encerramento

Próxima ação proposta, administrador do repositório e mantenedor de CI: incorporar a tabela de cenários à proposta DEC-02. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-143"></a>

## DEC-N2 — Política de versão e distribuição (Verify, release v1, PyPI)

Frente: governanca_e_integracao. Encaminhamento: decisao_pendente_sem_autorizacao.

### Identidade e estado

DEC-N2 — Política de versão e distribuição (Verify, release v1, PyPI). Papel proposto: mantenedor e responsáveis pelos pacotes; não é atribuição nova. Estado desta ficha: decisao_pendente_sem_autorizacao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Separar identidade do módulo, versão do contrato, dado persistido e distribuição para evitar gates sem relação com a mudança.

### Feito, faltante e não comprovado

No código base, pyproject Verify declara 0.1.0 e __version__ 0.3.0; Verdict.verify_version já tem default 0.1.0 e to_row usa o campo do Verdict. #162 alinha a identidade do módulo; seus checks capturados estão verdes. Nenhum novo escritor/persistência é criado por essa PR. Tag não é prova suficiente de uma release publicada; distribuição PyPI não foi conferida no serviço externo.

### Linhagem

Valores do pacote/módulo → PR#162 de correção mínima → política de release/distribuição separada → specs PyPI a reconciliar individualmente.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 156. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Pacote instalado → versão de código; contrato de dados → semântica; Verdict → valor persistível; canal de distribuição → artefato publicado. Esses quatro objetos não são intercambiáveis.

### Consequências e risco

Bloquear #162 por contrato/persistência mantém drift sem tratar o risco próprio da PR. Usar tag como sinônimo de release publicada ou assumir consumidor externo ausente excede o recorte.

### Alternativas e recomendação

Revisar #162 por seu diff e prova já existente; definir política de pacote/contrato/release separadamente. Publicar PyPI, distribuir pelo repositório ou adiar são escolhas de produto, sem autorização implícita.

### Dependências e paralelismo

Sem dependência técnica demonstrada entre #162 e escritor externo. Specs de distribuição dependem da política escolhida; consumidores externos de versão são uma hipótese a inventariar quando relevante.

### Plano e aceite propostos

Registrar significado de cada versão e canal escolhido; selecionar specs válidas e recibos necessários antes de eventual publicação. Controle: mudança de __version__ não deve ser descrita como alteração automática em linhas persistidas.

### Comunicação entre responsáveis

Nota de release futura deve distinguir alteração do módulo de mudança contratual. Não registrar pacote como publicado apenas porque o metadata local está pronto.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Bloquear a #162 por contrato ou persistência manteria o drift de __version__ sem tratar o risco da própria PR, porque o campo que entra na linha persistida é Verdict.verify_version, já com default 0.1.0. Que caso o teste ainda não cobre? — Consumidores externos da versão do módulo não foram inventariados, e a distribuição no PyPI não foi conferida; tag não prova release publicada. Como eu explicaria isso para outro pod? — A #162 corrige a identidade do módulo; versão do pacote, versão do contrato, valor persistido e canal de distribuição são quatro objetos distintos, e a política de distribuição é decisão à parte.

### Próxima ação e encerramento

Próxima ação proposta, mantenedor e responsáveis pelos pacotes: revisar #162 independentemente e formular a política de distribuição. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-144"></a>

## DEC-04 — Fechamento de issues após merge

Frente: decisoes_produto_e_custodia. Encaminhamento: decisao_pendente_sem_autorizacao.

### Identidade e estado

DEC-04 — Fechamento de issues após merge. Papel proposto: mantenedor e responsáveis pelas issues; não é atribuição nova. Estado desta ficha: decisao_pendente_sem_autorizacao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Reconciliar fechamento de issue com seus critérios efetivos, conservando prova já existente e lacunas funcionais.

### Feito, faltante e não comprovado

#124 compara Handler no DryRun sem observar a chamada Command; não falta somente CI. #123 tem runtime relatado em 20–21/09 com escopos diferentes, não ausência total de runtime. #115 possui resolver e testes de conflito/zero, mas o recorte não demonstrou toda a cadeia consumidor/SQL/RDD. Merge das PRs não elimina esses critérios.

### Linhagem

G04 → issues #115/#123/#124 → código e recibos delimitados → mapa critério/evidência → escolha de manter, dividir ou fechar.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 138. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Critério original → prova pertinente no artefato correto → resíduo explícito → decisão do mantenedor → estado da issue.

### Consequências e risco

Fechar #124 por CI verde preservaria a lacuna de invocação. Exigir novo runtime como se setembro não existisse repete prova sem avaliar seu alcance.

### Alternativas e recomendação

Manter com checklist reconciliado; dividir resíduo quando isso melhorar ownership sem apagar aceite; fechar somente com critério satisfeito ou alteração explícita aceita. Não recomendar fechamento conjunto automático.

### Dependências e paralelismo

As três análises podem avançar em paralelo. #124 precisa prova de comportamento; #123 depende da garantia de associação escolhida; #115 depende da superfície consumidora e do recorte runtime.

### Plano e aceite propostos

Produzir uma linha por critério com fonte, árvore/ambiente, status e resíduo. Controle: mudar Command mantendo Handler deve ser detectado pela futura prova de #124. Não executar esses controles aqui.

### Comunicação entre responsáveis

Propor comentário específico por issue, distinguindo implementação, relato de execução e decisão humana; registrar qualquer alteração de critério.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Fechar a #124 por um verde genérico preservaria a lacuna de invocação do Command, e exigir novo runtime na #123 como se setembro não existisse repetiria prova sem avaliar seu alcance. Que caso o teste ainda não cobre? — Os recibos da #123 vêm de dois ambientes e entrypoints, núcleo de 20/09 e wrapper de 21/09, e na #115 falta a cadeia consumidor/SQL/RDD; cada critério precisa de fonte, árvore ou ambiente e resíduo. Como eu explicaria isso para outro pod? — Uma issue fecha por critério satisfeito ou por alteração explícita aceita, não apenas por merge; manter, dividir ou fechar se decide issue a issue, sem fechamento conjunto automático.

### Próxima ação e encerramento

Próxima ação proposta, mantenedor e responsáveis pelas issues: montar o mapa de aceite por issue antes de propor fechamento. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-145"></a>

## DEC-07 — #122 proceed/defer/reject reenquadrado sobre a #129

Frente: decisoes_produto_e_custodia. Encaminhamento: decisao_pendente_sem_autorizacao.

### Identidade e estado

DEC-07 — #122 proceed/defer/reject reenquadrado sobre a #129. Papel proposto: mantenedor e Pods 1/3; não é atribuição nova. Estado desta ficha: decisao_pendente_sem_autorizacao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Decidir o destino do Ask HTTP/BFF em relação à API de leituras já integrada, conservando as fronteiras dos perfis.

### Feito, faltante e não comprovado

#129 integrada fornece API v1 de leituras; isso não entrega automaticamente Ask. #122 pede proceed/defer/reject, ownership e sequência publicável; seu texto ainda parte da fronteira histórica #102. O candidato local é evidência de factibilidade declarada, não autorização para publicação ou deploy.

### Linhagem

X01/S07/X11 → candidato Ask → #122 → integração posterior da API #129 → reenquadramento da decisão antes de eventual implementação.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 228. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Ask do cliente → proxy/perfil escolhido → adapter HTTP → serviços existentes; preservar semântica dos oito tools e os limites de #115/#117.

### Consequências e risco

Duplicar camadas HTTP sem explicitar responsabilidades cria contratos concorrentes. Adiar “até a API v1” é premissa superada porque ela já foi integrada.

### Alternativas e recomendação

Ask na API existente, serviço BFF separado com fronteira explícita, ou adiar/rejeitar com motivo. Se proceed, confirmar fatias contrato→Serve→Front propostas na #122; três PRs são proposta a ratificar, não fato executado.

### Dependências e paralelismo

Estudo de envelope/ownership pode avançar junto da política #171. Perfil compartilhado implementado precisa de fronteira de confiança definida. Decisão não autoriza deploy nem substitui #115/#117.

### Plano e aceite propostos

Comparar proposta Ask e superfície v1; registrar proceed/defer/reject e razões; se proceed, definir contratos, consumidores, fatias e prova futura. Controle: nenhum novo transporte muda silenciosamente os oito tools ou aplica Fix.

### Comunicação entre responsáveis

Atualização proposta na #122 ligando explicitamente #129 e #171; separar escolha de arquitetura de permissão para publicar.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Duplicar camadas HTTP sem explicitar responsabilidades criaria contratos concorrentes, e adiar até a API v1 é premissa superada, porque a #129 já a integrou. Que caso o teste ainda não cobre? — Conferir o controle que preserva os oito tools MCP e a adequação da API de leituras à intenção Ask. O candidato local não foi revalidado nesta revisão; isso não apaga testes históricos eventualmente relatados. Como eu explicaria isso para outro pod? — A escolha é a fronteira do Ask, na API existente ou num BFF separado, ou adiar ou rejeitar, sem reabrir toda a API v1; três PRs são proposta a ratificar.

### Próxima ação e encerramento

Próxima ação proposta, mantenedor e Pods 1/3: preparar comparação de opções e decisão por perfil. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-146"></a>

## DEC-08 — Token e exposição de `/docs`/`/openapi.json` na #129

Frente: decisoes_produto_e_custodia. Encaminhamento: decisao_pendente_sem_autorizacao.

### Identidade e estado

DEC-08 — Token e exposição de `/docs`/`/openapi.json` na #129. Papel proposto: mantenedor e responsáveis Front/Serve; não é atribuição nova. Estado desta ficha: decisao_pendente_sem_autorizacao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Explicitar acesso a schema e responsabilidade pelo token em cada perfil de implantação.

### Feito, faltante e não comprovado

auth.py protege paths no prefixo /v1, exceto /v1/health. Docs/OpenAPI ficam fora dessa barreira. O nginx encaminha /v1 sem injetar Authorization. #171 registra a decisão aberta e afirma que schema público não é, por si, vazamento de dados. Não foi observada exposição de credencial real.

### Linhagem

S05/S06 e #129 → política não definida → #171 → decisão por perfil → mudança somente se escolhida; Ask/BFF pertence à #122.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 246. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Cliente → nginx → middleware da API → rota pública ou autenticada; schema e health possuem decisões explícitas próprias.

### Consequências e risco

Operador pode supor proteção onde o middleware não atua. Token injetado no proxy exige proteção de acesso ao proxy; movê-lo do browser não cria autorização de usuários automaticamente.

### Alternativas e recomendação

Schema público, autenticado ou desativado conforme perfil; token no cliente local, proxy ou gateway conforme ameaça e usuários. Não impor uma arquitetura universal sem justificar a fronteira.

### Dependências e paralelismo

Desenho paralelo à #122 e à preparação de cenários #172. Implantação compartilhada precisa da política escolhida, mas não bloqueia todos os estudos ou leituras locais.

### Plano e aceite propostos

Matriz rota/perfil/identidade/token/renovação; se houver mudança, prova futura de acesso permitido, recusa 401, health e docs conforme política. Não registrar segredos na issue nem executar integração aqui.

### Comunicação entre responsáveis

Na #171, comunicar responsáveis e política por rota sem credenciais; tratar mudanças de comportamento separadamente da decisão.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Um proxy que injeta o token do serviço para qualquer um que o alcance transforma o proxy em acesso aberto; mover o token do browser não cria autorização de usuários. Que caso o teste ainda não cobre? — Health público e docs ainda não foram conferidos contra uma política escolhida: auth.py protege /v1 exceto /v1/health, e /docs e /openapi.json ficam fora dessa barreira. Como eu explicaria isso para outro pod? — Exposição do schema, identidade do usuário e token do serviço são decisões distintas por perfil; nenhuma credencial real exposta foi observada.

### Próxima ação e encerramento

Próxima ação proposta, mantenedor e responsáveis Front/Serve: propor matriz de confiança e ciclos de token para ratificação. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-147"></a>

## DEC-10 — Contenção operacional da #127 (dev/.env, ownership, Windows, cold start)

Frente: decisoes_produto_e_custodia. Encaminhamento: decisao_pendente_sem_autorizacao.

### Identidade e estado

DEC-10 — Contenção operacional da #127 (dev/.env, ownership, Windows, cold start). Papel proposto: mantenedor do pacote; não é atribuição nova. Estado desta ficha: decisao_pendente_sem_autorizacao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Conter efeitos sobre configuração e recursos de outras stacks com entregas separáveis e provas proporcionais.

### Feito, faltante e não comprovado

No corte main há cópia forçada para dev/.env. Candidato 1122d031 com binding false remove essa cópia e tem relato e2e macOS com stubs e HTTP loopback; PATCH-167.diff com binding padrão tem prova argv separada. Ownership da #175, prova Windows e cold start são resíduos distintos. Não foi demonstrada perda real de configuração ou derrubada de stack nesta auditoria.

### Linhagem

#127 integrada → E08/E09/E10/E14 → #174/#175 e candidatos CL → DEC-N5 seleciona contrato → DEC-15 seleciona publicação → provas do objeto escolhido.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 282. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Comando escolhido → arquivo de configuração explícito → recursos identificados → operação limitada ao que a política autoriza → preservação verificável do restante.

### Consequências e risco

Misturar recibos entre variantes dá cobertura falsa. Condicionar correção de .env a toda a política de ownership atrasa trabalho sem dependência técnica demonstrada.

### Alternativas e recomendação

Publicar correção de configuração delimitada após revisão/autorização; definir ownership em entrega própria; escolher prova Windows/cold start de acordo com o escopo. Restrição temporária a ambiente dedicado é opção operacional, não prova de correção.

### Dependências e paralelismo

Contrato binding e variante governam a prova de #167/#174. #175 não é predecessor universal desse patch. Estudo de ownership e preparação Windows podem avançar em paralelo; runtime depende do ambiente autorizado.

### Plano e aceite propostos

Identificar bytes e entrypoints; distinguir helper, runner e wrapper integral; planejar controles de preservação de arquivos e stack. C2/31 passes G2 não é gate de aceite APEX.

### Comunicação entre responsáveis

Na futura revisão, informar variante/hash, plataformas observadas, recurso tocado e limites; não anunciar Windows validado só porque existe pacote pronto.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Alterar PositionalBinding impede transferir automaticamente a prova entre variantes; os recibos originais continuam históricos de seus próprios objetos. O e2e macOS pertence ao candidato 1122d031 com binding false; argv pertence ao PATCH-167.diff com binding padrão. Que caso o teste ainda não cobre? — Os testes atuais exercitam wrapper integral só no e2e macOS com stubs; o w07 do pacote Windows chama apenas o helper, e ownership da #175, Windows e cold start continuam sem prova. Como eu explicaria isso para outro pod? — Configuração em dev/.env, ownership de stacks e plataformas são fronteiras distintas, cada uma com prova própria; a correção do .env não precisa esperar toda a política de ownership.

### Próxima ação e encerramento

Próxima ação proposta, mantenedor do pacote: definir o candidato e o resíduo operacional de cada issue. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-148"></a>

## DEC-11 — ADR-004 de correlação de origem e numeração de ADRs

Frente: decisoes_produto_e_custodia. Encaminhamento: decisao_pendente_sem_autorizacao.

### Identidade e estado

DEC-11 — ADR-004 de correlação de origem e numeração de ADRs. Papel proposto: owner declarado no ADR e mantenedor; não é atribuição nova. Estado desta ficha: decisao_pendente_sem_autorizacao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Ratificar ou revisar a fronteira de correlação de origem e usar nomes canônicos sem apagar a história.

### Feito, faltante e não comprovado

ADR-004 na main tem status proposed e declara não autorizar implementação. Nomeia Luan como decision owner. O índice canônico já existe e informa que números históricos não redefinem documentos. Atribuição execução-stage da #115 é explicitamente diferente de localizar arquivo/linha/célula.

### Linhagem

F4.1/L4 → PR#133/ADR-004 proposta → índice #141 → decisões de payload, opt-in e consumidor ainda requeridas pelo próprio documento.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 336. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Fonte Spark potencial → seleção local de frame permitido → descarte de trace bruto → locator opcional ou unknown → consumidor delimitado. É desenho proposto, não caminho implementado.

### Consequências e risco

Confundir número de ADR ou correlacionar por timing pode fabricar origem. Caminho relativo também pode revelar metadados operacionais; sua aceitação é decisão explícita do projeto.

### Alternativas e recomendação

Aprovar locators relativos opt-in sob limites, usar referência opaca com resolver local separado, revisar ou manter proposta. Não renumerar documentos canônicos para corrigir colisões históricas.

### Dependências e paralelismo

As decisões de fronteira precedem Task-Spec/implementação conforme ADR. Não exigir implementação candidata antes de começar a decisão que a condiciona. Não é gate universal da v1.

### Plano e aceite propostos

Registrar escolhas de root/sintaxe/notebook/payload/primeiro consumidor. Planejar controles de desconhecido, ausência e dado proibido. Runtime futuro tem recortes SQL/RDD/sem fonte; nenhuma execução nesta revisão.

### Comunicação entre responsáveis

Atualizar status e índice somente após ratificação; citar documento por caminho completo quando número histórico for ambíguo.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Um hash opaco sem resolver local não permite afirmar qual linha gerou um stage, e correlacionar por timing ou por número de ADR fabricaria origem. Que caso o teste ainda não cobre? — Conferir o tratamento de notebook sem identidade estável como unknown no protocolo proposto. O ADR-004 permanece proposed; a leitura desta ficha não comprova controle executado. Como eu explicaria isso para outro pod? — Localizar código-fonte (arquivo, linha, célula) é diferente de atribuir execução SQL a stage, que é a #115; o índice canônico já mostra que números históricos não redefinem os ADRs.

### Próxima ação e encerramento

Próxima ação proposta, owner declarado no ADR e mantenedor: preparar as cinco decisões de fronteira antes de qualquer folha de implementação. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-149"></a>

## DEC-12 — Canal e triagem do SECURITY.md

Frente: decisoes_produto_e_custodia. Encaminhamento: decisao_pendente_sem_autorizacao.

### Identidade e estado

DEC-12 — Canal e triagem do SECURITY.md. Papel proposto: mantenedor e responsável pela triagem; não é atribuição nova. Estado desta ficha: decisao_pendente_sem_autorizacao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Definir canal de relato e responsabilidade por resposta sem inventar compromisso de suporte ou gate global de release.

### Feito, faltante e não comprovado

LICENSE e NOTICE existem no corte; SECURITY.md não foi localizado na árvore examinada. #33 foi estreitada para higiene de licenciamento; canal privado é decisão associada, não evidência de ilegalidade ou comprometimento. Habilitação atual de recurso privado do GitHub não foi conferida.

### Linhagem

Registro X04/DEC-12 → pergunta de canal/suporte → decisão do mantenedor → documento e canal operacional, se adotados.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 354. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Relator → canal designado → responsável → triagem → correção e comunicação conforme política escolhida.

### Consequências e risco

Canal sem responsável pode falhar; publicar prazo sem capacidade cria compromisso impraticável. Ausência do arquivo não prova ausência de qualquer canal.

### Alternativas e recomendação

Canal privado da plataforma, e-mail operacional ou ambos após verificar disponibilidade; definir versões suportadas e tempo inicial realista. Condicionar release é escolha explícita, não norma presumida pela auditoria.

### Dependências e paralelismo

Independente do CI e da feature #21. Pode ser preparado em paralelo às PRs. Não usar esta decisão para alargar os critérios já estreitados da #33 sem concordância.

### Plano e aceite propostos

Escolher canal e responsável, confirmar acesso, documentar escopo/expectativas e revisar o texto. Encerramento exige que o caminho de relato funcione, não só que o arquivo exista.

### Comunicação entre responsáveis

Proposta de SECURITY.md e referência na documentação apropriada; não inserir contato pessoal ou promessa que o mantenedor não aprovou.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Um canal sem responsável que receba e acompanhe o relato pode falhar, e publicar prazo sem capacidade cria compromisso impraticável. Que caso o teste ainda não cobre? — Arquivo SECURITY.md presente não comprova que a caixa ou o canal é atendido; a habilitação de recurso privado do GitHub não foi conferida. Como eu explicaria isso para outro pod? — A política precisa de um caminho real e de um responsável pela triagem; LICENSE e NOTICE já existem, e o resíduo da #33 é só a política de vulnerabilidades.

### Próxima ação e encerramento

Próxima ação proposta, mantenedor e responsável pela triagem: preparar a decisão de canal, suporte e triagem. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

<a id="item-150"></a>

## DEC-14 — Texto do CONTRACT.md e marcadores PROPOSED

Frente: decisoes_produto_e_custodia. Encaminhamento: decisao_pendente_sem_autorizacao.

### Identidade e estado

DEC-14 — Texto do CONTRACT.md e marcadores PROPOSED. Papel proposto: mantenedor do contrato; não é atribuição nova. Estado desta ficha: decisao_pendente_sem_autorizacao; decisões pertencem ao mantenedor, não ao parecer.

### Intenção e benefício

Reconciliar redação vigente/histórica/proposta e as guardas que fixam essa redação, sem mudar semântica do produto por acidente.

### Feito, faltante e não comprovado

#165 aponta cláusula de onJobStart e marcadores PROPOSED. A guarda tests/test_telemetry_compatibility_matrix.py exige literalmente trechos legados; mudar só docs pode romper o controle. Publicar uma redação ou remover marcador não ratifica automaticamente novo contrato.

### Linhagem

X13/registro → minuta publicada #165 → decisão de redação → diff documental e guarda correspondente → revisão.

### Fontes e corte

Origem preservada: F-DECISOES-NECESSARIAS.md, linha 390. Revalidação documental em 18/10/2026. Código fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; APIs/capturas conservam os cortes de 16–17/10. As fontes individuais constam abaixo, sem consulta implícita de estado público atual.

### Classe e limite da evidência

OBSERVADO: bytes, metadados e declarações das fontes citadas. RELATADO: execução histórica ou conclusão expressa por terceiros. DERIVADO: contagens calculadas sobre o universo explicitado. PROPOSTO: opções, critérios e sequência desta ficha; nenhuma decisão humana ou execução funcional foi acrescentada.

### Fluxo

Contrato/DDL existentes → significado aprovado → documentação coerente → asserção que testa a regra pretendida, sem perpetuar texto obsoleto.

### Consequências e risco

Atualizar texto sem guarda correspondente deixa CI contraditório; trocar PROPOSED por RATIFIED sem fonte de decisão produz ratificação fictícia.

### Alternativas e recomendação

Atualizar texto com referência ao estado implementado; manter história com nota explícita; adiar redação se houver decisão pendente real. Escolher sem obrigar nova versão do contrato para uma correção editorial.

### Dependências e paralelismo

Sem gate global de CI ou outras decisões para preparar o diff. Mudança semântica, se descoberta, deve ser delimitada e ratificada separadamente.

### Plano e aceite propostos

Mapear quatro pontos da issue às fontes e assertivas; preparar alteração mínima de docs/teste textual proporcional. Controle: não preservar a frase obsoleta apenas para agradar a guarda.

### Comunicação entre responsáveis

Na #165, distinguir correção de redação de decisão normativa; identificar qual registro sustenta cada marcador.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Manter a frase obsoleta só para agradar a guarda perpetuaria um texto falso, e trocar PROPOSED por RATIFIED sem fonte de decisão produziria ratificação fictícia. Que caso o teste ainda não cobre? — tests/test_telemetry_compatibility_matrix.py exige literalmente trechos legados; falta confirmar se a nova redação implica alguma mudança que o DDL não contém. Como eu explicaria isso para outro pod? — Corrigir a documentação do CONTRACT.md inclui corrigir a guarda que fixa a frase antiga; correção de redação e decisão normativa são separadas, sem exigir nova versão do contrato.

### Próxima ação e encerramento

Próxima ação proposta, mantenedor do contrato: propor redação e reconciliação das assertivas por ponto. Entrada: fontes e alternativas desta ficha. Registrar a saída e seu limite; publicação/execução futura exige instrução própria.

