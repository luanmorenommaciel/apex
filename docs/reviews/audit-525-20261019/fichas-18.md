# Fichas documentais — lote 18

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-171"></a>

## T-20260817-four-to-five-doc-ripple — T-20260817-four-to-five-doc-ripple.md

Frente: Serve / L1 Connect — documentação e clientes. Encaminhamento: encerrar_meta_numerica_e_abrir_reconciliacao_documental_atual.

### Identidade e estado

`tasks/T-20260817-four-to-five-doc-ripple.md` (blob 04befff4). 'Close the four-to-five documentation ripple', M, standard, P2; owner `(none)`; depends_on register-apex-status, gate-status-assert, stdio-gate-five-tools, cursor-codex-config. Estado `ready`, `accepted: false`. Pod provável: Pod 3/Serve (inferido pelos caminhos; nenhum pod no arquivo).

### Intenção e benefício

Não deixar documento afirmando quatro tools e registrar uma contagem de testes copiada de execução real: 'VALIDATION.md registra o observado, então um registro velho é falso'. O benefício permanente é a honestidade documental, não o número cinco.

### Feito, faltante e não comprovado

A meta cinco foi superada: o servidor registra oito tools. Deriva atual confirmada: README Serve apresenta eight tools e tabela de oito, mas mantém título The six tools e comentário /mcp lists the six tools; docstring e cabeçalho do read_only_gate dizem four, embora esse gate exercite o recorte histórico; stdio gate diz six, com sete entradas. VALIDATION L5:302–304 e339–344 afirma oito no stdio, divergindo do código. SERVE.md tem checklist histórico de quatro/cinco; deve ser rotulado e preservado como histórico, sem tratá-lo inteiro como documentação atual. O eval_1 rejeitaria padrões four encontrados; ele não exige five nem compara a contagem atual.

### Linhagem

L1_tasks.md → l1-connect.yaml:1012 → spec 3a6b402 → sem recibo de execução localizado neste recorte. Docs foram tocados por L2/L3/L5/L6/#132 sem esta spec. Elo ausente: uma reconciliação documental pós-oito-tools.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260817-four-to-five-doc-ripple.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-four-to-five-doc-ripple.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L1012; fontes/batch-revalidated-specs28-sources/git/serve/README.md#L1-L23; fontes/batch-revalidated-specs28-sources/git/serve/README.md#L194-L197; fontes/batch-revalidated-specs28-sources/git/serve/tools/read_only_gate.py#L1-L1; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE.md#L55-L76; fontes/batch-revalidated-specs28-sources/git/serve/tools/mcp_stdio_gate.py#L1-L39; fontes/batch-revalidated-specs28-sources/git/serve/VALIDATION.md#L300-L305.; fontes/batch-revalidated-specs28-sources/git/serve/VALIDATION.md#L300-L305; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83). Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: as derivas listadas, por leitura direta. FATO sobre evals: eval_2 extrai um número de 'N passed' de uma execução sem exigir sucesso total (uma execução com falhas também tem 'N passed'). Tensão interna: B-3 manda alterar o critério T11 de SERVE.md e o anti-padrão manda não editar o checklist T1–T14 histórico. DECISÃO: nenhuma pendente sobre 'cinco'; a reconciliação atual é trabalho novo.

### Fluxo

Fluxo proposto: CONTRACTED_TOOLS (fonte) → documentos (README, VALIDATION, SERVE.md, docstrings de gates) → leitor de outro pod. Observado: documentos com contagens 4/6/8 coexistindo.

### Consequências e risco

Sem ação: leitores recebem contagens contraditórias (4, 6, 7, 8) e um registro de validação que afirma uma atualização ausente — risco de coordenação e de confiança em VALIDATION. Sem impacto de runtime. Confiança alta.

### Alternativas e recomendação

Recomendado: encerrar esta spec como superada e abrir 'reconciliação documental da superfície atual' que (a) preserve seções históricas datadas do VALIDATION, (b) atualize prosa atual, títulos e docstrings dos gates, (c) evite números onde possível ou derive de CONTRACTED_TOOLS. Alternativa: só corrigir os pontos listados — rápido, repete a deriva. Não reescrever registros históricos.

### Dependências e paralelismo

Encerrar não depende de nada. O item novo independe de apex_status (se apex_status vier, muda um número). Pode correr em paralelo; combina com o item do gate stdio.

### Plano e aceite propostos

Menor entrega proposta: inventário das passagens atuais e históricas; corrigir títulos/prosa atuais e esclarecer o recorte dos gates; acrescentar nota de reconciliação datada em VALIDATION sem reescrever recibos passados. Conferência documental basta para correção textual. Não copiar contagens de testes de outro SHA nem exigir uma execução nova apenas para atualizar prosa. Se houver mudança de gate, sua validação própria deve corresponder ao comportamento alterado. Registrar separadamente a substituição desta meta de cinco.

### Comunicação entre responsáveis

Explicar: 'A ripple de quatro para cinco é história; hoje os documentos dizem 4, 6, 7 e 8 em lugares diferentes. Proponho uma reconciliação nova que preserve os registros datados.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Substituir números dentro dos recibos históricos apagaria o que foi observado naquele recorte. Que caso o teste ainda não cobre? Caso documental a conferir: título atual divergente ou docstring de gate fora dos padrões do grep. Como eu explicaria isso para outro pod? A nota deve separar contagem atual, escopo histórico e prova registrada por SHA.

### Próxima ação e encerramento

Ação: encerrar e abrir item de reconciliação documental. Owner a confirmar: Serve/documentação. Entrada: inventário de ocorrências deste parecer. Saída: spec parked + item novo. Encerramento: documentos atuais coerentes com a superfície e histórico preservado.

<a id="item-172"></a>

## T-20260817-gate-status-assert — T-20260817-gate-status-assert.md

Frente: Serve / L1 Connect — apex_status. Encaminhamento: decidir_com_familia_e_prova_live_condicional.

### Identidade e estado

`tasks/T-20260817-gate-status-assert.md` (blob f0645972). 'Assert apex_status in the live read-only gate', S, standard, P2; owner `(none)`; depends_on register-apex-status e surface-defaulted-vars (não satisfeitas). Estado `ready`, `accepted: false`. Pod provável: Pod 3/Serve (inferido pelos caminhos serve/; nenhum pod no arquivo). Único item da família que exige ClickHouse real (PR #79: 'needs a live ClickHouse. None is running').

### Intenção e benefício

Provar apex_status contra ClickHouse real, comparando contract_tables com o DESCRIBE independente que o gate já faz — porque um FakeClient devolve as colunas que o autor do teste digitou.

### Feito, faltante e não comprovado

Não implementado: `read_only_gate.py` não tem bloco `status_tool` nem `describe_missing`; seu docstring ainda diz 'all four tools' e a seção '-- the four tools --' (linhas 1 e 160), embora a superfície seja oito. Falta tudo. Não comprovado: execução recente do gate; o próprio VALIDATION.md registra para L5 que o gate 'não foi executado' naquela leg.

### Linhagem

L1_tasks.md → l1-connect.yaml:913 → spec 3a6b402 → sem implementação → ready. Elo ausente: ambiente ClickHouse identificado e decisão da família.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260817-gate-status-assert.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-gate-status-assert.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L913; fontes/batch-revalidated-specs28-sources/git/serve/tools/read_only_gate.py#L1-L12; fontes/batch-revalidated-specs28-sources/git/serve/tools/read_only_gate.py#L73-L90; fontes/batch-revalidated-specs28-sources/git/serve/tools/read_only_gate.py#L160-L170; fontes/batch-revalidated-specs28-sources/git/serve/VALIDATION.md#L336-L344.; fontes/batch-revalidated-specs28-sources/git/serve/VALIDATION.md#L336-L344; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83). Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: gate sem status; texto 'four tools' no gate. FATO sobre evals: eval_1 escreve `[caminho local omitido]` fixo e eval_2 lê o mesmo arquivo — acoplamento entre evals e caminho compartilhado; 'small and positive' aceita 0 ≤ idade < 3600 s, tolerância a explicitar. INFERÊNCIA: o eval_1 é discriminante (compara com DESCRIBE independente). DECISÃO PENDENTE: família + ambiente. Nenhum runtime nesta revisão.

### Fluxo

Fluxo proposto: gate semeia linhas próprias → DESCRIBE independente de 3 tabelas → [describe_missing] ; apex_status (via servidor) → [contract_tables] → comparação → JSON do gate com status_tool → limpeza só das linhas do fixture. Observado: gate atual semeia, testa argMax/binding/diagnose e limpa.

### Consequências e risco

Sem ação: a conformidade reportada por apex_status (se existir) ficaria provada só com fakes. Sem apex_status, nenhum risco. O texto 'four tools' no gate é deriva documental de baixo impacto. Confiança alta.

### Alternativas e recomendação

Recomendado: decidir a família; se adotada, executar como prova live delimitada com ambiente/commit registrados e arquivo de saída por execução (não /tmp fixo). Alternativa: aceitar prova offline com fixture de system.columns gerada a partir do DDL do contrato — mais barata, menos forte. Não usar table_columns para gerar o esperado (anti-padrão declarado).

### Dependências e paralelismo

Depende de register-apex-status, surface-defaulted-vars e de um ClickHouse autorizado. O desenho do bloco status_tool pode ser preparado offline em paralelo; a execução é etapa separada que exige autorização.

### Plano e aceite propostos

Se apex_status for adotado e esta prova live for mantida: (1) projetar offline status_tool e describe_missing contra o contrato escolhido; (2) usar saída exclusiva por execução; (3) em ambiente descartável autorizado, exigir connected, contagens positivas, comparação com DESCRIBE independente e tolerância de idade explícita; (4) caso negativo de coluna faltante somente em fixture/ambiente de teste, sem alterar tabelas operacionais; (5) recibo com SHA, plataforma, versão do banco e resultado. A correção textual four tools é independente e requer conferência documental proporcional.

### Comunicação entre responsáveis

Explicar: no gate do SHA lido não há bloco status_tool e no servidor não há apex_status. Não foi localizado recibo dessa prova live no recorte consultado. Se a funcionalidade e a prova forem adotadas, registrar ambiente/SHA e saída exclusiva por execução; o desenho pode avançar offline.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Gerar o esperado pelo próprio table_columns tornaria a comparação circular. Que caso o teste ainda não cobre? Caso a conferir: divergência de coluna em fixture descartável e idade sob relógio desviado. Como eu explicaria isso para outro pod? O DESCRIBE independente pertence à prova live escolhida; o desenho pode avançar offline.

### Próxima ação e encerramento

Ação: condicionar à decisão da família; separar a correção textual do gate (four→atual) como item pequeno independente. Owner a confirmar: Serve. Entrada: decisão + ambiente autorizado. Saída: spec revisada com recibo por execução ou parked. Encerramento: recibo live ligado ao SHA, ou parked com motivo.

<a id="item-173"></a>

## T-20260817-graphify-rebuild — T-20260817-graphify-rebuild.md

Frente: Tooling local / grafo de conhecimento. Encaminhamento: encerrar_ou_externalizar_tooling_local_nao_versionado.

### Identidade e estado

`tasks/T-20260817-graphify-rebuild.md` (blob bde36871). 'Rebuild the graphify knowledge graph for L1', XS, standard, P2; owner `(none)`; depends_on four-to-five-doc-ripple. Estado `ready`, `accepted: false`. Pod: nenhum aplicável (tooling de desenvolvimento local, não produto). `touches_paths: [graphify-out]` ausente no SHA.

### Intenção e benefício

Manter o grafo de conhecimento graphify (usado para escopar o L1 em 2026-07-27) atualizado com apex_status, ServerStatus, resolve_settings e store_health, porque um grafo velho responde sobre um código que não existe mais.

### Feito, faltante e não comprovado

A saída graphify-out não está na árvore versionada do SHA; a própria spec a chama de untracked. Há referências versionadas na spec atual, no plano, em L1_tasks.md e na spec legada docs/lanes/L1_legacy_specs/T-20260812-graphify-rebuild.md. A .gitignore lida não nomeia graphify-out. apex_status e resolve_settings não têm implementação nos módulos Serve inspecionados. Não foi verificado se alguém ainda usa o grafo local nem seu conteúdo atual; a ausência no Git não demonstra ausência de ferramenta no time.

### Linhagem

Spec legada T-20260812-graphify-rebuild descreve grafo local de 27/07 → índice L1 e plano atual → spec canônica criada por 3a6b402. Nenhum recibo de rebuild localizado neste recorte; saída e ferramenta não foram inspecionadas. A linhagem documental existe, embora o artefato derivado não seja versionado.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260817-graphify-rebuild.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-graphify-rebuild.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L1059; fontes/batch-revalidated-specs28-sources/git/.gitignore; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83); fontes/batch-revalidated-specs28-sources/graphify-tracked-search.txt; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_legacy_specs/T-20260812-graphify-rebuild.md. Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: graphify-out ausente do índice Git e referências documentais presentes nos quatro locais indicados. RELATO HISTÓRICO: a spec legada diz que o grafo apoiou o planejamento. Os evals só procuram apex_status e suggest_fix, não comprovando os quatro símbolos, o modo --update ou preservação dos demais nós; graphify não aparece em required_tools. INFERÊNCIA: saída local de desenvolvimento. DECISÃO PENDENTE: adoção e responsável atuais; nenhuma execução realizada.

### Fluxo

Fluxo proposto: código do repositório → graphify --update → graphify-out (local, não versionado) → consultas do desenvolvedor/agente. Nada observado na árvore.

### Consequências e risco

Sem ação: nenhum efeito em produto, CI ou v1. Risco limitado a respostas desatualizadas para quem ainda consulta o grafo local. Ausência da saída não é defeito do APEX. Confiança alta.

### Alternativas e recomendação

Recomendado: confirmar uso e responsável pelo artefato local e então propor parked/externalização com motivo, preservando o ID. Alternativas: política compartilhada explícita de atualização, ou busca direta no código. Sem evidência de uso atual ou decisão de adoção, esta tarefa não é gate técnico da v1. Não declarar automaticamente tooling pessoal ou ferramenta abandonada.

### Dependências e paralelismo

Dependência declarada (four-to-five-doc-ripple) é obsoleta. Nada no backlog depende desta spec. Pode ser encerrada já, em paralelo a tudo; nenhum estudo do produto precisa esperar por ela.

### Plano e aceite propostos

Condição de não ação: sem decisão do time de adotar o grafo como artefato compartilhado, não executar. Passo documental: mover para parked com motivo 'saída não versionada; ferramenta fora do escopo do produto'. Se adotado: declarar o binário em required_tools, evals que exijam os quatro símbolos e contagem de nós antes/depois.

### Comunicação entre responsáveis

Explicar: 'Esta spec atualiza um grafo local que não está no repositório; não afeta o produto. Proponho encerrar e, se alguém usa a ferramenta, documentar fora do backlog do produto.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Versionar o grafo sem política criaria outro artefato derivado sujeito a ficar desatualizado. Que caso o teste ainda não cobre? Caso a conferir: preservação de todos os nós anteriores, além de suggest_fix. Como eu explicaria isso para outro pod? A intenção surgiu em spec legada e trata tooling local cujo uso atual ainda precisa ser confirmado.

### Próxima ação e encerramento

Ação: reconciliar o uso atual com responsável a confirmar de tooling; entrada: spec atual, legada e busca no índice Git; saída verificável: decisão documentada de manter fora do produto, arquivar ou adotar com política. Encerramento documental somente após disposição registrada; nenhuma execução de graphify nesta auditoria.

<a id="item-174"></a>

## T-20260817-name-endpoint-in-error — T-20260817-name-endpoint-in-error.md

Frente: Serve / L1 Connect — configuração e erros. Encaminhamento: decidir_politica_de_mensagem_com_controle_discriminante.

### Identidade e estado

`tasks/T-20260817-name-endpoint-in-error.md` (blob 5b31b4b4). 'Name the resolved endpoint in the unavailable error', S, standard, P2; owner `(none)`; depends_on resolve-settings-extract. Estado `ready`, `accepted: false`. Pod provável: Pod 3/Serve (inferido pelos caminhos; nenhum pod no arquivo). Spec reconhece tensão com o trilho de segurança de `_sanitize`.

### Intenção e benefício

Incluir host, porta e database na mensagem `clickhouse_unavailable`, mantendo usuário e senha fora: hoje a mensagem não nomeia valor algum e o usuário não sabe se o servidor tentou o host pretendido (SERVE-LEGS F1.3: 'esconde a senha — e também a correção').

### Feito, faltante e não comprovado

Não implementado: mensagens de `_sanitize` (`ch.py:1217-1262`) são strings fixas sem endpoint. Já coberto por testes existentes: B-2/B-4 (senha e DSN do driver não vazam) em `test_errors_never_leak_the_connection_string` e na variante por código (#140). Atenção: esses testes afirmam que o host e a porta **do texto do driver** não aparecem; B-1 quer o host **configurado** — compatível, mas só um teste com host configurado ≠ host do driver distingue as duas fontes. Falta B-1/B-3. Não comprovado: aprovação da política de expor endpoint.

### Linhagem

L1_tasks.md → l1-connect.yaml:443 → spec 3a6b402 → evals com node IDs (611dc6e) → sem implementação. Elo lateral: #140 reescreveu `_sanitize` (códigos access_denied/database_missing, b149569 'name the cause behind access denied') sem citar esta spec. Fechamento ausente.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260817-name-endpoint-in-error.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-name-endpoint-in-error.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L443; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_mcp/ch.py#L1217-L1262; fontes/batch-revalidated-specs28-sources/git/serve/tests/test_injection_hardening.py#L190-L250; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L64-L68.; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83). Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: _sanitize devolve mensagens fixas e os testes usam DSN/senhas sintéticas próprias para conferir a mensagem pública. O eval_2 exporta sentinelas, mas isso não prova que alguma asserção confira esses valores exportados ou o payload novo. _sanitize registra exc_info em stderr: a garantia existente analisada é não encaminhar texto do driver ao cliente, não sigilo universal dos logs. INFERÊNCIA: códigos de acesso mais específicos reduzem parte do custo de diagnóstico. DECISÃO PENDENTE: quais campos de endpoint configurado podem chegar à mensagem pública.

### Fluxo

Fluxo proposto: falha de conexão → _sanitize(exc) + resolve_settings() → 'clickhouse_unavailable: ... host:port/database' (sem user/senha, sem texto do driver) → ApexStoreError → tool/HTTP. Observado: falha → _sanitize → string fixa por classe/código → cliente.

### Consequências e risco

Sem ação: usuário com endpoint errado recebe 'não respondeu' sem saber qual endpoint — custo de suporte. Risco ao implementar: expor host interno a quem lê respostas de tool (modelo/logs de cliente). É troca de privacidade vs diagnóstico, não vulnerabilidade observada. Confiança alta nos fatos.

### Alternativas e recomendação

Decidir se endpoint configurado pode aparecer na mensagem pública clickhouse_unavailable. Alternativas: manter mensagem genérica; ou registrar campos aprovados num banner de stderr, fora do payload da tool, reconhecendo que o cliente decide como expor seus logs. Construir mensagem de campos permitidos, sem str(exc); preservar credenciais fora da saída pública. A escolha é reversível e pode ser preparada em paralelo à família status.

### Dependências e paralelismo

Depende de resolve-settings-extract (fonte do endpoint) e da decisão de política. Pode ser estudada em paralelo; não depende de apex_status.

### Plano e aceite propostos

Se adotada: (1) compor a mensagem de settings aprovados; (2) teste discriminante: CLICKHOUSE_HOST=a.example e texto do driver citando b.internal → mensagem contém a.example e não b.internal; (3) usuário sentinela nunca aparece; (4) outros códigos permanecem genéricos (anti-padrão: estender a query_failed); (5) manter os testes de não vazamento atuais. Doc: README seção de erros.

### Comunicação entre responsáveis

Explicar: 'Hoje o erro esconde tudo, o que é seguro e pouco útil. Propor mostrar só o endpoint configurado em indisponibilidade; os testes atuais de não vazamento continuam valendo e um teste novo separa endpoint configurado de texto do driver.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Usar str(exc) como fonte do endpoint pode encaminhar DSN e credencial ao cliente. Que caso o teste ainda não cobre? Caso a conferir: host configurado diferente do citado pelo driver, além das sentinelas do payload. Como eu explicaria isso para outro pod? A decisão separa endpoint configurado aprovado, credenciais e logs de stderr.

### Próxima ação e encerramento

Ação: levar à decisão de política de mensagens (junto com o banner). Owner a confirmar: Serve + segurança. Entrada: `_sanitize` atual e testes. Saída: decisão escrita e spec revisada com teste discriminante, ou parked. Encerramento: status coerente.

<a id="item-175"></a>

## T-20260817-pypi-metadata — T-20260817-pypi-metadata.md

Frente: Serve / L1 Connect — distribuição PyPI. Encaminhamento: decidir_distribuicao_v1_preparacao_offline.

### Identidade e estado

`tasks/T-20260817-pypi-metadata.md` (blob b638b6ca). 'Add PyPI metadata to the serve pyproject', XS, standard, P2; owner `(none)`; sem dependências. Estado `ready`, `accepted: false`. Marcada '▶︎' no índice L1. Pod provável: Pod 3/Serve (inferido pelos caminhos; nenhum pod no arquivo).

### Intenção e benefício

Levar readme, license, authors, keywords, classifiers e urls à metadata do wheel, para que o pacote seja publicável e a instalação seja `uvx apex-mcp` em vez de `uvx --from <caminho>`. O contexto da spec registra que a licença Apache-2.0 já resolveu a questão aberta.

### Feito, faltante e não comprovado

Não implementado: `serve/pyproject.toml` no SHA tem name/version 0.2.0/description/requires-python/dependencies/scripts, sem readme, license, authors, keywords, classifiers, urls. Deriva adicional: a description diz '3 read-only tools + 1 gated proposal tool' e 'frozen v0.2 contract', mas a superfície é 8 tools e o README cita contrato v0.5. O pacote agora inclui `apex_api` e o script `apex-api` (#129), o que muda o que se publicaria. Pin `mcp[cli]>=1.27,<2` presente (B-3 satisfeito por ora).

### Linhagem

L1_tasks.md → l1-connect.yaml:593 → spec 3a6b402 → sem implementação → ready. Último toque no pyproject: 9224cee (#129, API). Decisão de distribuição v1: não localizada.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260817-pypi-metadata.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-pypi-metadata.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L593; fontes/batch-revalidated-specs28-sources/git/serve/pyproject.toml; fontes/batch-revalidated-specs28-sources/git/LICENSE; fontes/batch-revalidated-specs28-sources/git/serve/VALIDATION.md#L132-L136; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83); fontes/batch-claude-specs-sources/claude/fontes/publico/pypi_org_pypi_apex-mcp_json.txt. Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: campos ausentes; description desatualizada; pacote com duas aplicações. FATO sobre evals: eval_1 confere chaves no TOML e assume a dependência mcp como primeira entrada; eval_2 faz `rm -rf dist && uv build` (efeito no worktree) e aceita um único PASSED. INFERÊNCIA: preparação é offline e barata. DECISÃO PENDENTE: canal de distribuição v1 e o que o wheel contém.

### Fluxo

Fluxo proposto: pyproject [metadata] → uv build → wheel/sdist com METADATA → twine check → (outra unidade) upload. Observado: pyproject sem metadata → instalação por caminho local.

### Consequências e risco

Sem ação: instalação continua por caminho/clone; metadata incompleta só importa se houver publicação. A description desatualizada engana quem lê o pacote hoje (baixo impacto). Confiança alta.

### Alternativas e recomendação

Recomendado: decidir antes o escopo do pacote (MCP só, ou MCP+API) e o canal; depois atualizar metadata e description juntas. Alternativas: distribuição por checkout (status quo) ou pacote separado para a API. Padrão: metadata validada no artefato construído, não só no TOML. Reversível até publicar.

### Dependências e paralelismo

Metadata e description podem ser estudadas e preparadas offline em paralelo à decisão de canal; o escopo final do wheel deve ser confirmado antes de construir a release para publicação. Independem de apex_status e ClickHouse. A checagem do conteúdo do wheel pode ser desenhada sobre a configuração atual sem esperar upload.

### Plano e aceite propostos

Se adotada: (1) acrescentar campos e corrigir description (8 tools, contrato atual); (2) validar METADATA do wheel construído, não só o TOML; (3) twine check por artefato (todos PASSED); (4) controle negativo: remover `license` faz a validação falhar; (5) build em diretório temporário, sem apagar dist do desenvolvedor. Doc: README de release.

### Comunicação entre responsáveis

Explicar: o pyproject lido não possui os campos de metadata propostos; a descrição ainda diz 3+1 tools, enquanto o alvo inclui MCP e API. Pode-se preparar a correção offline; escopo/canal/versionamento da release precisam ser definidos antes de publicar, sem tratar essa preparação como upload autorizado.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Publicar metadata com descrição 3+1 ocultaria a superfície de oito e a presença da API. Que caso o teste ainda não cobre? Caso a conferir: metadata válida no TOML mas incompleta ou inválida no artefato. Como eu explicaria isso para outro pod? A configuração atual inclui MCP e API; a decisão de release deve dizer o que será distribuído.

### Próxima ação e encerramento

Ação: abrir decisão de distribuição v1 (escopo do pacote e canal). Owner a confirmar: mantenedor/release. Entrada: pyproject atual e este parecer. Saída: decisão + spec revisada ou parked. Encerramento: metadata validada no artefato ou motivo registrado.

<a id="item-176"></a>

## T-20260817-pypi-publish — T-20260817-pypi-publish.md

Frente: Serve / L1 Connect — distribuição PyPI. Encaminhamento: decidir_distribuicao_v1_acao_irreversivel.

### Identidade e estado

`tasks/T-20260817-pypi-publish.md` (blob 791d1169). 'Publish apex-mcp to PyPI', XS, standard, P2; owner `(none)`; depends_on testpypi-rehearsal. Estado `ready`, `accepted: false`. Pod provável: Pod 3/Serve (inferido pelos caminhos; nenhum pod no arquivo). Spec separada da edição de configs porque publicar é irreversível.

### Intenção e benefício

Publicar o release e verificar `uvx apex-mcp` numa máquina sem checkout, com o cliente MCP reportando conectado. Benefício: instalação de um comando; risco: release imutável.

### Feito, faltante e não comprovado

Na captura preservada de 2026-10-18T04:04:18Z, GET pypi.org/pypi/apex-mcp/json retornou 404 para esse nome. O SHA lido ainda documenta Until apex-mcp is published e fallback --from. Não foi localizada release identificada neste recorte. Isso não prova que nunca houve publicação, disponibilidade do nome ou titularidade. Faltam decisão de canal/nome/versão e recibo dos artefatos efetivamente distribuídos.

### Linhagem

L1_tasks.md → l1-connect.yaml:730 → spec 3a6b402 → sem execução; PR #79 'need registry credentials'. Elos ausentes: decisão de distribuição, ensaio TestPyPI.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260817-pypi-publish.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-pypi-publish.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L730; fontes/batch-revalidated-specs28-sources/git/serve/README.md#L182-L207; fontes/batch-revalidated-specs28-sources/git/serve/VALIDATION.md#L132-L136; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83); fontes/batch-claude-specs-sources/claude/fontes/publico/pypi_org_pypi_apex-mcp_json.txt. Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: 404 no PyPI na data. FATO sobre evals: eval_1 (EOF imediato + stdout vazio) passaria com falha de instalação; eval_2 é grep 'published|pypi release' em VALIDATION e declara verificar B-2 (cliente conectado), que não é observado. Sem pin de versão no comando. DECISÃO PENDENTE do mantenedor. Nenhuma publicação nem upload executado.

### Fluxo

Fluxo proposto: árvore limpa → build → upload autorizado (credencial adequada) → PyPI → `uvx apex-mcp` em máquina limpa → cliente MCP conectado. Observado: instalação por `uvx --from <caminho>`.

### Consequências e risco

Sem ação: instalação continua por caminho; o L1 'um comando' não se cumpre. Risco de agir sem ensaio: release quebrada permanente. Status `ready` não autoriza upload. Confiança alta.

### Alternativas e recomendação

Recomendado: decisão explícita de canal, nome e versão antes de qualquer upload; exigir recibo do TestPyPI e eval fortalecido (versão fixa, processo vivo, cliente conectado observado). Alternativas: checkout/clone (status quo) ou release em índice privado. Irreversível — exige aprovação humana registrada.

### Dependências e paralelismo

Depende de testpypi-rehearsal, metadata e decisão humana. drop-from-path depende desta. Estudo e preparação podem correr em paralelo; o upload é ação externa autorizada à parte.

### Plano e aceite propostos

Se adotada: (1) decisão escrita (nome, versão, escopo do pacote); (2) build de árvore limpa ligada a commit; (3) upload por executor explicitamente autorizado; (4) verificação em máquina limpa com versão fixa `uvx apex-mcp==X`; (5) controle: `claude mcp list` mostrando conectado, com saída registrada; (6) recibo em VALIDATION com hash do wheel. Senão: parked com motivo.

### Comunicação entre responsáveis

Explicar: a consulta preservada de 18/10 retornou 404 para apex-mcp e não foi localizada uma release identificada. O eval atual só conferir stdout vazio não prova instalação/conexão. Um eventual upload exige autorização específica e deve ligar artefato, versão e conexão observada; ready não é autorização.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Um upload antes do ensaio pode fixar um artefato inadequado em uma versão publicada. Que caso o teste ainda não cobre? Caso a conferir: resolução falha com stdout vazio satisfazendo o eval antigo. Como eu explicaria isso para outro pod? Ready é estado documental; publicação precisa de autorização e recibo específico de versão/hash.

### Próxima ação e encerramento

Ação: levar à decisão de distribuição v1. Owner a confirmar: mantenedor. Entrada: decisão, recibo TestPyPI, artefato validado. Saída: autorização escrita e recibo de release, ou parked. Encerramento: release identificada e conexão comprovada, ou decisão de não publicar.

<a id="item-177"></a>

## T-20260817-register-apex-status — T-20260817-register-apex-status.md

Frente: Serve / L1 Connect — apex_status. Encaminhamento: decisao_central_da_familia_apex_status.

### Identidade e estado

`tasks/T-20260817-register-apex-status.md` (blob 7f839a21). 'Register the apex_status tool', XS, standard, P2; owner `(none)`; depends_on assembler, degraded-path, store-health-query, table-columns-probe (só store-health satisfeita). Estado `ready`, `accepted: false`, sem assinatura. Pod provável: Pod 3/Serve (inferido pelos caminhos serve/; nenhum pod no arquivo).

### Intenção e benefício

Expor apex_status como tool read-only sem parâmetros, ligada à saúde e conformidade do store e a um payload ServerStatus. O critério de saída do índice L1 é uma resposta verdadeira após instalação, inclusive com ClickHouse indisponível. Não aceitar parâmetros reduz entrada controlável pelo chamador; dados do banco, erros, configuração e serialização ainda exigem os controles de segurança declarados.

### Feito, faltante e não comprovado

Não implementado: `create_server` registra oito tools (analyze_run, explain_stage, compare_runs, list_runs, search_kb, recall_similar_runs, verify_fix, suggest_fix) e nenhuma é apex_status. A premissa 'quinta tool' caiu em 2026-08-19: L2 (#83) fixou a superfície em cinco com list_runs e avisou que 'quem entrar depois reconcilia'; depois L3/L5/L6 levaram a oito. A intenção continua viva na documentação atual: SERVE-LEGS.md (reconciliado em #132, 2026-10-06) ainda lista F1.1 'today there isn't one'. Não comprovado: prioridade para v1.

### Linhagem

Índice L1:11–13 → plano l1-connect:259 → spec gerada em 3a6b402 → ausência do registro apex_status nos módulos Serve lidos. #83 registra explicitamente a colisão da antiga quinta tool; #101 altera a organização da allowlist. Não foi feita busca exaustiva de issues por intenção equivalente; issue própria de retomada permanece não verificada. Os estados atuais da spec não constituem decisão nova.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260817-register-apex-status.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-register-apex-status.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L259; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_mcp/server.py#L1-L19; fontes/batch-revalidated-specs28-sources/git/serve/tests/test_server_tools.py#L20-L67; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/serve/tools/mcp_stdio_gate.py#L1-L39; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83); fontes/batch-revalidated-specs28-sources/git/serve/src/apex_api/app.py#L35; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_api/app.py#L159. Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: 8 tools, nenhuma apex_status; teste atual compara lista ORDENADA (sorted) e não ordem de registro (df6fe77, #101). FATO sobre evals: eval_1 só lista tools e anotações — não invoca apex_status nem valida ServerStatus, mas declara B-2; eval_2 é grep negativo de 'Four tools', já satisfeito hoje (docstring diz 'Eight tools'). RELATO: a spec prevê deixar a suíte vermelha até five-tools-assertion. DECISÃO PENDENTE do mantenedor: adotar ou não.

### Fluxo

Fluxo proposto: cliente MCP → tools/list → [apex_status, readOnlyHint=true, openWorldHint=false] → tools/call apex_status() → store_health/table_columns (ou ApexStoreError) → diagnose.status → [ServerStatus] → resposta estruturada. Fluxo atual observado: cliente → 8 tools → cada chamada falha individualmente com código sanitizado se o store cair.

### Consequências e risco

Sem ação: o critério de saída L1 ainda descreve uma tool ausente. O índice mostra 23 unidades, duas done e 21 ready; isso não equivale a vinte dependentes semânticos de apex_status. Há itens de clientes, config e distribuição independentes e elos de ordenação por arquivo. Impacto possível: ruído de planejamento e diagnóstico de instalação mais lento; nenhum incidente demonstrado.

### Alternativas e recomendação

Recomendado: decisão de produto sobre apex_status. Se adotada, preparar entrega coerente de assembler/caminho degradado/registro/controle de fronteira e atualização da allowlist vigente, sem exigir commit deliberadamente vermelho. Se não adotada, registrar disposição individual dos itens de status, preservar as intenções independentes e avaliar /v1/health como alternativa parcial HTTP. O conjunto de tools resultante depende da superfície efetiva da integração; hoje seriam nove se apenas apex_status fosse adicionado.

### Dependências e paralelismo

Depende de: decisão humana; assembler/degraded/table-columns (se adotada). Pode correr em paralelo com qualquer revisão de PR aberta. A decisão não depende de ClickHouse; a prova live (gate-status-assert) depende de ambiente.

### Plano e aceite propostos

Se adotada: (1) registrar tool sem parâmetros com READ_ONLY; (2) inserir 'apex_status' em CONTRACTED_TOOLS (uma linha ordenada); (3) teste que INVOCA a tool com FakeClient saudável e com store que levanta, validando o schema; (4) atualizar EXPECTED_TOOLS do gate stdio (hoje com 7 entradas para 8 tools — ver achado). Controle negativo: remover o registro faz o teste de superfície falhar. Senão: parked em bloco com referência a esta decisão.

### Comunicação entre responsáveis

Explicar: apex_status não está registrado no SHA lido; a intenção de resposta verdadeira do L1 continua documentada, embora a meta de ser a quinta tool tenha sido ultrapassada. Decidir adoção e replanejar os itens de status individualmente; clientes, config e distribuição conservam sua intenção própria.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Adicionar parâmetros criaria uma entrada nova para a tool e mudaria o contrato proposto. Que caso o teste ainda não cobre? Caso a conferir: tool listada com anotações corretas, mas retorno nunca invocado ou serializado. Como eu explicaria isso para outro pod? A intenção é status verdadeiro no MCP; a meta quinta tool não define a funcionalidade atual.

### Próxima ação e encerramento

Ação: registrar decisão sobre a funcionalidade apex_status; responsável a confirmar: mantenedor e Serve. Entrada: critério L1, superfície estática atual, modelo e /v1/health existente. Saída: decisão com lista explícita de IDs adotados, substituídos ou arquivados e plano proporcional. Encerramento desta intenção: disposição individual rastreável, sem conferir aceite por status ou por arquivamento em bloco.

<a id="item-178"></a>

## T-20260817-resolve-settings-extract — T-20260817-resolve-settings-extract.md

Frente: Serve / L1 Connect — configuração e erros. Encaminhamento: decidir_refatoracao_independente_de_apex_status.

### Identidade e estado

`tasks/T-20260817-resolve-settings-extract.md` (blob 6b3af43a). 'Extract resolve_settings out of get_client', S, standard, P2; owner `(none)`; depends_on `[T-20260817-table-columns-probe]` (não satisfeita; dependência de ordem de escrita em ch.py, não semântica). Estado `ready`, `accepted: false`, sem assinatura. Pod provável: Pod 3/Serve (inferido pelos caminhos; nenhum pod no arquivo).

### Intenção e benefício

Tornar a configuração resolvida inspecionável sem abrir conexão: hoje nada responde 'qual host foi resolvido' sem construir o cliente — justamente quando o cliente não pode ser construído. Beneficia o banner de stderr, a mensagem de erro com endpoint e `using_defaults`.

### Feito, faltante e não comprovado

Não implementado: `get_client()` (`ch.py:1286-1307`) ainda lê HOST, PORT, USER, PASSWORD e SECURE inline com os.getenv. Extração parcial posterior, por outro motivo: `configured_database()` (`ch.py:1272`, introduzida em fab6620, #129) centraliza só CLICKHOUSE_DATABASE para alinhar sessão e probes `system.*`. Falta: dataclass congelada, tupla `defaulted`, testes B-1..B-4. Não comprovado: compatibilidade de B-3 (SECURE em '1/true/yes' case-insensitive) — por leitura, o comportamento atual é `.lower() in {...}`, que a spec manda preservar.

### Linhagem

L1_tasks.md → l1-connect.yaml:393 → spec 3a6b402 → evals em subshell (10b96e2) → sem implementação → ready. Elo lateral não ligado à spec: configured_database (#129). Fechamento ausente.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260817-resolve-settings-extract.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-resolve-settings-extract.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L393; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_mcp/ch.py#L1268-L1307; fontes/batch-revalidated-specs28-sources/git/serve/README.md#L209-L220.; fontes/batch-revalidated-specs28-sources/git/serve/README.md#L209-L220; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83). Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: leitura inline das variáveis; configured_database presente. FATO sobre evals: eval_1 roda `test_ch.py` inteiro e não exige os testes novos (não nomeia testes novos) — não discrimina B-1..B-4; eval_2 só exige ausência de `password` e presença de `defaulted`. INFERÊNCIA: a refatoração é útil a três outras specs mesmo sem apex_status. DECISÃO PENDENTE: se há consumidor (banner/erro) aprovado.

### Fluxo

Fluxo proposto: os.environ → resolve_settings() [sem cache] → Settings(host, port, user, database, secure, defaulted) → get_client (+ password lido à parte) / banner / mensagem de erro / using_defaults. Observado: os.environ → get_client (lru_cache) → clickhouse_connect.

### Consequências e risco

Sem ação: nenhum defeito; a pergunta 'qual endpoint' continua sem resposta fora do cliente. Risco de implementar sem consumidor: refatoração sem benefício e toque num factory com cache. Confiança alta.

### Alternativas e recomendação

Recomendado: decidir junto com o primeiro consumidor escolhido (banner de stderr é o mais barato e não depende de apex_status). Alternativa: estender o padrão de configured_database a cada variável — menos estrutura, mas sem `defaulted`. Anti-padrões da spec continuam válidos: sem password na dataclass, sem cache. Reversível.

### Dependências e paralelismo

Depende de um consumidor aprovado; a dependência declarada de table-columns-probe é só ordenação de edição em ch.py e pode ser removida. Estudo e implementação podem correr em paralelo à decisão de apex_status.

### Plano e aceite propostos

Se um consumidor ou a refatoração for adotado: (1) Settings frozen sem senha e defaulted de nomes; (2) preservar configured_database(), inclusive string vazia/whitespace virando apex; (3) conferir defaults, variáveis definidas, SECURE TRUE/yes/0 e mudança de ambiente entre chamadas sem cache; (4) controle discriminante de get_client delegando à resolução; (5) ligar os casos relevantes aos evals, evitando só rodar arquivo inteiro e chamá-lo de prova das novas regras. Documento de configuração deve refletir o comportamento decidido.

### Comunicação entre responsáveis

Explicar: resolve_settings não foi localizado no módulo ch.py lido; configured_database já centraliza o database com tratamento de vazio e espaços. A extração pode atender banner ou erro mesmo sem apex_status, preservando comportamento e cache existentes.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Cachear settings impediria refletir mudanças de ambiente em chamadas posteriores. Que caso o teste ainda não cobre? Caso a conferir: DATABASE vazio ou só espaços preservando configured_database e defaults. Como eu explicaria isso para outro pod? A extração tem consumidores possíveis fora de apex_status, e senha permanece fora do payload inspecionável.

### Próxima ação e encerramento

Ação: decidir consumidor e reescrever evals com testes nomeados. Owner a confirmar: Serve. Entrada: ch.py no SHA e decisão de consumidor. Saída: spec revisada sem dependência artificial, ou parked. Encerramento: status coerente.

<a id="item-179"></a>

## T-20260817-root-mcp-json — T-20260817-root-mcp-json.md

Frente: Serve / L1 Connect — documentação e clientes. Encaminhamento: decidir_configuracao_de_projeto_independente.

### Identidade e estado

`tasks/T-20260817-root-mcp-json.md` (blob 214a5377). 'Add the root .mcp.json with a drift test', S, standard, P2; owner `(none)`; sem dependências. Estado `ready`, `accepted: false`. Marcada '▶︎' no índice L1. Pod provável: Pod 3/Serve (inferido pelos caminhos; nenhum pod no arquivo). `creates_paths` (.mcp.json raiz e serve/tests/test_config_parity.py) ausentes no SHA.

### Intenção e benefício

Entregar .mcp.json como arquivo regular na raiz e controlar a paridade com serve/.mcp.json, para que configuração por projeto não dependa de cópia manual. A spec relata que a instrução de copiar não foi concretizada na árvore versionada; não se conclui que nenhum usuário tenha feito cópias locais.

### Feito, faltante e não comprovado

Não implementado: raiz sem `.mcp.json`; teste de paridade inexistente. O README raiz orienta `claude mcp add --scope project ... -- uvx --from ./serve apex-mcp`, que gera a configuração no cliente do usuário — alternativa manual, não arquivo versionado. Falta: arquivo regular (não symlink), teste que falhe e nomeie os dois caminhos. Não comprovado: se o mantenedor quer versionar a config de projeto (decisão de produto/segurança: config com default de senha de desenvolvimento).

### Linhagem

L1_tasks.md → l1-connect.yaml:817 → spec 3a6b402 → sem implementação. Mapa de caminhos da Parte03 já registrava `.mcp.json` e `test_config_parity.py` como ausentes. Fechamento ausente.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260817-root-mcp-json.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-root-mcp-json.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L817; fontes/batch-revalidated-specs28-sources/git/serve/.mcp.json; fontes/batch-revalidated-specs28-sources/git/README.md#L88-L92; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83). Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: ausência dos dois arquivos; serve/.mcp.json presente com comentário de cópia. FATO sobre evals: eval_2 compara só `mcpServers` e tipo de arquivo — não prova descoberta pelo cliente (B-1); B-3 (falha nomeando os caminhos) exige inspeção do teste. INFERÊNCIA: entrega pequena. DECISÃO PENDENTE: versionar a config na raiz.

### Fluxo

Fluxo proposto: clone → cliente MCP abre a raiz → lê .mcp.json → expande ${VAR:-default} → `uvx --from ./serve apex-mcp`. Teste: json raiz vs json serve → igualdade de mcpServers. Observado: usuário copia manualmente ou usa `claude mcp add`.

### Consequências e risco

Sem ação: instalação de projeto continua manual; risco de duas cópias divergirem se alguém criar a raiz sem teste. Nota: versionar o arquivo distribui o default de senha de dev (já público no serve/.mcp.json) — não é vazamento novo. Confiança alta.

### Alternativas e recomendação

Recomendado: decidir se a config de projeto deve ser versionada; se sim, arquivo regular + teste de paridade (simples e reversível). Alternativas: gerar no setup (rejeitada pela spec: clone novo deve funcionar) ou documentar só `claude mcp add`. Symlink é anti-padrão declarado (Windows/sandboxes).

### Dependências e paralelismo

Independe de apex_status, de PyPI e de ClickHouse; só exige a decisão de versionar a config. drop-from-path depende desta. Estudo e implementação podem correr em paralelo a qualquer frente, inclusive antes da decisão de distribuição.

### Plano e aceite propostos

Se adotada: (1) copiar o bloco para a raiz como arquivo regular; (2) teste de paridade que, ao falhar, imprime os dois caminhos; (3) controle negativo: editar um arquivo só → teste falha; (4) teste de não-symlink; (5) diferença permitida apenas em `_comment`. Doc: atualizar o comentário do serve/.mcp.json. Senão: parked com 'config de projeto não versionada por decisão'.

### Comunicação entre responsáveis

Explicar: .mcp.json raiz e test_config_parity.py estão ausentes da árvore versionada do SHA lido; serve/.mcp.json documenta cópia manual. Decidir versionamento e, se adotado, controlar paridade e descoberta pelo cliente no escopo escolhido, sem afirmar ausência de cópias locais de usuários.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Um symlink ou cópia divergente pode alterar portabilidade e configuração por projeto. Que caso o teste ainda não cobre? Caso a conferir: arquivo regular e JSON igual sem evidência de descoberta pelo cliente. Como eu explicaria isso para outro pod? A proposta versiona estrutura de configuração, sem afirmar que versões locais nunca existiram.

### Próxima ação e encerramento

Ação: decisão do mantenedor sobre versionar a config de projeto. Owner a confirmar: Serve. Entrada: serve/.mcp.json atual. Saída: arquivo + teste, ou parked com motivo. Encerramento: status coerente.

<a id="item-180"></a>

## T-20260817-startup-stderr-banner — T-20260817-startup-stderr-banner.md

Frente: Serve / L1 Connect — configuração e erros. Encaminhamento: decidir_entrega_pequena_independente_de_apex_status.

### Identidade e estado

`tasks/T-20260817-startup-stderr-banner.md` (blob a62120af). 'Log one resolved-configuration banner to stderr at startup', S, standard, P2; owner `(none)`; depends_on resolve-settings-extract e status-store-down-e2e (a segunda só por ordem de escrita em server.py/test_server_tools.py). Estado `ready`, `accepted: false`. Pod provável: Pod 3/Serve (inferido pelos caminhos; nenhum pod no arquivo).

### Intenção e benefício

Emitir uma linha em stderr com host, porta, database e secure na inicialização: servidores MCP são iniciados por clientes cuja configuração o usuário talvez não tenha escrito, e quando o Apex parece vazio a primeira necessidade é saber qual endpoint foi resolvido.

### Feito, faltante e não comprovado

Não implementado: `main()` registra apenas 'apex-mcp starting (stdio transport)' (`server.py:632-640`). Já coberto: B-2 (zero bytes em stdout com EOF imediato) por `test_server_emits_zero_stdout_bytes_on_clean_eof` e logging em stderr por `test_logging_is_configured_to_stderr` (`test_server_tools.py:161-180`). Falta: B-1, B-3, B-4 (supressão com APEX_LOG_LEVEL=WARNING). Não comprovado: necessidade de dependência de status-store-down-e2e.

### Linhagem

L1_tasks.md → l1-connect.yaml:493 → spec 3a6b402 → evals em subshell (10b96e2) → sem implementação → ready. Elo parcial anterior e independente: os testes de stdout limpo e logging em stderr já existiam desde a fundação do serve. Fechamento ausente.

### Fontes e corte

Fontes primárias lidas no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs28-sources/git/tasks/T-20260817-startup-stderr-banner.md; fontes/batch-revalidated-specs28-sources/history/T-20260817-startup-stderr-banner.txt; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml#L493; fontes/batch-revalidated-specs28-sources/git/serve/src/apex_mcp/server.py#L623-L640; fontes/batch-revalidated-specs28-sources/git/serve/tests/test_server_tools.py#L128-L180.; fontes/batch-revalidated-specs28-sources/git/serve/tests/test_server_tools.py#L128-L180; fontes/batch-revalidated-specs28-sources/git/docs/lanes/L1_tasks.md; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md#L55-L70; fontes/batch-revalidated-specs28-sources/git/docs/lanes/SERVE-LEGS.md; fontes/batch-revalidated-specs28-sources/git/tasks/.plans/l1-connect.yaml; fontes/batch-revalidated-specs28-sources/public-captured-pulls.json; PR #79 e #83). Trechos decisivos e classe de evidência estão explicitados nos campos 3, 4 e 6. SHA-256 e igualdade com a cópia Parte03: fontes/batch-revalidated-specs28-sources/MANIFEST.json.

### Classe e limite da evidência

FATO OBSERVADO: main só registra starting, sem endpoint; os testes existentes conferem stdout vazio com EOF e stream de logging. O teste de EOF não afirma returncode zero, então sozinho não prova início saudável. Eval_1 do arquivo inteiro não obriga a existência de teste do banner ou de WARNING; eval_2 usa caminhos /tmp fixos e um grep por clickhouse, sem exigir sucesso do processo. INFERÊNCIA: item pequeno com controle de stdout já disponível; não é execução observada nesta revisão. DECISÃO PENDENTE: adotar e delimitar os campos exibidos em stderr.

### Fluxo

Fluxo proposto: main() → _configure_logging (stderr) → resolve_settings() → log.info('clickhouse endpoint host:port db secure') → stderr do processo → log do cliente MCP. stdout permanece exclusivo do JSON-RPC. Observado: main → log 'starting' → FastMCP.run(stdio).

### Consequências e risco

Sem ação: diagnóstico de endpoint continua exigindo inspeção do config do cliente. Risco de implementar: escrever em stdout por engano corromperia o framing — mitigado pelos testes existentes de stdout. Sem incidente observado.

### Alternativas e recomendação

Recomendado: entrega pequena independente de apex_status, com resolve_settings ou leitura direta mínima (se a extração for rejeitada). Alternativa: só documentar no README como ver o ambiente no cliente. Padrão: log estruturado em nível INFO, suprimível. Reversível.

### Dependências e paralelismo

Depende de uma fonte do endpoint (resolve-settings-extract ou leitura mínima). A dependência de status-store-down-e2e deve ser removida (ordem de edição de uma família que pode não existir). Pode correr em paralelo a outras frentes.

### Plano e aceite propostos

Se adotada: (1) log INFO único em main(), não na importação; (2) teste com caplog/subprocess: contém host/port/database/secure; (3) senha sentinela ausente de stderr; (4) com APEX_LOG_LEVEL=WARNING a linha não aparece; (5) manter teste de zero bytes em stdout; arquivos temporários por execução, não /tmp fixo. Doc: README 'Run and verify'.

### Comunicação entre responsáveis

Explicar: main não registra endpoint no SHA lido. Há controles existentes de stdout/logging em stderr, com limites próprios; eles não substituem os casos do banner/nível WARNING. Esta entrega pode ser planejada independentemente de apex_status.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Escrever o banner em stdout ou no import pode interferir no framing ou criar efeitos antes do main. Que caso o teste ainda não cobre? Caso a conferir: WARNING suprimindo só o banner e processo malsucedido com stdout vazio. Como eu explicaria isso para outro pod? A linha de diagnóstico deve sair em stderr e só carregar campos aprovados do endpoint.

### Próxima ação e encerramento

Ação: propor como item pequeno separado da família apex_status. Owner a confirmar: Serve. Entrada: decisão de exibir endpoint. Saída: spec revisada (sem dependência obsoleta) ou parked. Encerramento: status coerente.

