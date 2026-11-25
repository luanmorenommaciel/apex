# Pod 3 / Serve

Versão de 20/10/2026. Minha visão para discussão do time.

## 1. Pod 3 / Serve

Esta é minha leitura para contribuir com o planejamento do time. Autoria da base compartilhada e limites das provas permanecem explícitos. O corte documental foi reconferido em 20/10/2026, com main c3c3ea3. Não representa liberação de release nem decisão oficial do pod.

Fontes: https://github.com/luanmorenommaciel/apex/issues/181 ; https://github.com/luanmorenommaciel/apex/blob/faf8b5723abd7cd0905137e574d515216f74d287/docs/reviews/pr-revalidation-20261019/README.md

## 2. O que a #181 reúne

A leitura mantém quatro estados visíveis: integrado, aberto para revisão, evidência registrada e proposta. Uma issue aberta não comprova implementação. Um merge de documentação pode registrar uma proposta, como no ADR-004, sem ratificar todas as decisões. O material inclui uma leitura curta, fichas e anexos para não precisarmos percorrer os quase 50 mil caracteres da issue durante a reunião.

Fontes: https://github.com/luanmorenommaciel/apex/issues/181 ; https://github.com/luanmorenommaciel/apex/blob/15ab9dc2b587cb187a0413843761db3ec256da4e/docs/reviews/pod3-20261019/README.md

## 3. A base entregue e as contribuições

O Serve já tem uma base construída em conjunto. Minha #44 integrou o primeiro esqueleto MCP somente leitura. A evolução posterior inclui o servidor do Luan e as entregas L1, L2, L3, L5 e L6 do Sidymar. Na API #129, reconheço a autoria principal do Sidymar. Antes do meu commit, ele também fez as quatro correções c71c2e4. Em fab6620, concluí ajustes de integração nas projeções, no database configurado, no timestamp e na ordenação dos findings e no acesso do Front à API. As 11 PRs do recorte estão listadas no apoio, sem somar fab6620 como uma PR própria. O corpo final de fab6620 relata 289 testes Serve e 130 Front. Os 275 Serve pertencem ao corte intermediário. Manter as correções de Sidymar c71c2e4 explícitas.

Fontes: https://github.com/luanmorenommaciel/apex/pull/44 ; https://github.com/luanmorenommaciel/apex/pull/129 ; https://github.com/luanmorenommaciel/apex/commit/fab662080da499df5d2d4b563ad68be7ddc4cc9f ; https://github.com/luanmorenommaciel/apex/issues/181

## 4. MCP e HTTP no estado integrado

MCP e HTTP são duas superfícies de consumo que reutilizam a camada diagnóstica do Serve. As oito tools são analyze_run, compare_runs, explain_stage, list_runs, recall_similar_runs, search_kb, suggest_fix e verify_fix. Há evidência histórica de transporte real na #156. O caminho do navegador envolve imagem, nginx e renderização, por isso não podemos transferir automaticamente uma prova da API para a experiência visual da Console. A futura fachada Ask é uma decisão própria. A proposta API-only da #182 ainda está fora da main consultada. O E2E histórico até o App já existe e a #182 relata provas locais. A ação #172 começa por reaproveitá-las, incluindo o relato adicional de nginx.

Fontes: https://github.com/luanmorenommaciel/apex/pull/129 ; https://github.com/luanmorenommaciel/apex/issues/156 ; https://github.com/luanmorenommaciel/apex/issues/172 ; https://github.com/luanmorenommaciel/apex/blob/15ab9dc2b587cb187a0413843761db3ec256da4e/docs/reviews/pod3-20261019/MATRIZ-EVIDENCIAS-SERVE.md

## 5. As cinco PRs do Serve em revisão

Respondendo à primeira pergunta do Antony: #157 publica testes e não muda código de produção. Compara MCP call_tool em processo com HTTP TestClient. Um segundo arquivo compara store populado e vazio com os mesmos argumentos somente no MCP. #163 adiciona três casos positivos com plan_json e usa helpers da #157. Devemos combinar a forma de integração da pilha e conferir a árvore resultante. #158 fixa desempate de findings por confidence_score DESC e finding_id ASC. #159 melhora o gate e a limpeza inclusive de linhas derivadas, mas escreve no store em modo padrão. #164 é documental e a ausência de checks precisa ser lida com os filtros de paths. Os números de CI pertencem a 09/10 e aos heads individuais. Revisores e prazos continuam a combinar. A #157 compara payloads sem normalização de campos. A #159 tem relato F1c de 79 focados/572 combinados/G1 19 PASS posterior ao checkpoint histórico de 519 testes. Não confundir os cortes.

Fontes: https://github.com/luanmorenommaciel/apex/pull/157 ; https://github.com/luanmorenommaciel/apex/pull/158 ; https://github.com/luanmorenommaciel/apex/pull/159 ; https://github.com/luanmorenommaciel/apex/pull/163 ; https://github.com/luanmorenommaciel/apex/pull/164

## 6. Evidências do Serve e da Console

A #182 relata Front 202/8 skip e Serve 456. Commit 222498cf registra imagem em fixtures. O Discord acrescenta E2E via nginx, cuja árvore e recibo precisam de reconciliação com #172. Não negar a prova existente nem conceder garantia de navegador apenas por associação.

Fontes: https://github.com/luanmorenommaciel/apex/issues/156 ; https://github.com/luanmorenommaciel/apex/pull/153 ; https://github.com/luanmorenommaciel/apex/pull/159 ; https://github.com/luanmorenommaciel/apex/pull/182 ; https://github.com/luanmorenommaciel/apex/issues/172 ; https://github.com/luanmorenommaciel/apex/blob/faf8b5723abd7cd0905137e574d515216f74d287/docs/reviews/pr-revalidation-20261019/README.md

## 7. Ask: alternativas para a decisão #122

A API #129 nos dá uma base concreta. A questão pendente é como o consumidor Ask será atendido e qual fronteira de confiança o perfil compartilhado exige. Adaptação da API e fachada interna não precisam ser alternativas mutuamente exclusivas. O comparativo deve começar mapeando os cinco intents propostos aos serviços existentes. Precisamos decidir identidade, autenticação, compatibilidade, comportamento de erro, Origin/CSRF quando aplicável, readiness e concorrência. A #171 tem registro próprio para schema/token da v1 e pode avançar em paralelo, mantendo coerência com a #122. Se houver proceed, proponho fatiar contrato, adaptador Serve e integração Front, com aceite específico por entrega. Adiar ou rejeitar com motivo também são resultados válidos.

Fontes: https://github.com/luanmorenommaciel/apex/issues/122 ; https://github.com/luanmorenommaciel/apex/issues/171 ; https://github.com/luanmorenommaciel/apex/blob/15ab9dc2b587cb187a0413843761db3ec256da4e/docs/reviews/pod3-20261019/DECISAO-ASK-122.md

## 8. As 23 tarefas L1 foram reconciliadas

A #79 trouxe 23 specs. O registro declara duas done/accepted e 21 ready, mas o código evoluiu desde agosto. As duas aceitas são serverstatus-model e store-health-query. ServerStatus e store_health existem e health utiliza a leitura, enquanto apex_status não está registrada como tool. Cada uma das 23 linhas da matriz separa estado declarado, implementação observada, evidência, limite e destino proposto. Não estamos reexecutando as duas aceitas nem marcando as outras em lote. As seis famílias organizam a discussão das 21 ready. O grupo de sete apex_status não deve impor dependência artificial sobre documentação, configuração ou revisão das PRs atuais. A reconciliação deve aproveitar a #164 para o ajuste de READMEs que já está proposto, evitando tarefa duplicada.

Fontes: https://github.com/luanmorenommaciel/apex/pull/79 ; https://github.com/luanmorenommaciel/apex/blob/15ab9dc2b587cb187a0413843761db3ec256da4e/docs/reviews/pod3-20261019/MATRIZ-L1-23.md ; https://github.com/luanmorenommaciel/apex/blob/15ab9dc2b587cb187a0413843761db3ec256da4e/docs/reviews/pod3-20261019/GOVERNANCA-TASK-SPECS.md

## 9. Oportunidades para o time avaliar

Esta parte é minha visão de oportunidades, para o time complementar e priorizar. O estudo do grafo pode avançar em paralelo à decisão de adoção/schema, mas a implementação espera essa fronteira. Compare entre versões deve preservar diferenças do Engine e findings de nível de job. Recall com configuração desconhecida é uma hipótese estática com caso discriminante próprio, sem incidente de runtime demonstrado. O backlog também inclui normalização de timestamps, limpeza após falha e oráculo de custo vinculado ao job selecionado. Os anexos preservam 16 minutas e apontam os trackers existentes para evitar abrir duplicatas. O objetivo é escolher poucas próximas entregas, não converter toda ideia em requisito de merge.

Fontes: https://github.com/luanmorenommaciel/apex/issues/106 ; https://github.com/luanmorenommaciel/apex/issues/107 ; https://github.com/luanmorenommaciel/apex/issues/117 ; https://github.com/luanmorenommaciel/apex/issues/177 ; https://github.com/luanmorenommaciel/apex/blob/15ab9dc2b587cb187a0413843761db3ec256da4e/docs/reviews/pod3-20261019/DESTINOS-MINUTAS.md

## 10. A #182 implementa mudanças no Serve

A revalidação considerou corpo, 59 mensagens de commits e 65 patches da #182. Confirmou dois pontos de adaptação na combinação, sem executar branches nem comprovar conflito textual. O trabalho é do Agmar. Checks verdes por head não aceitam automaticamente a combinação.

Fontes: https://github.com/luanmorenommaciel/apex/pull/182 ; https://github.com/luanmorenommaciel/apex/pull/158 ; https://github.com/luanmorenommaciel/apex/pull/159 ; https://github.com/luanmorenommaciel/apex/blob/15ab9dc2b587cb187a0413843761db3ec256da4e/docs/reviews/pod3-20261019/COORDENACAO-PR-182.md

## 11. A #185 conecta operação e consumidores

A conferência reconsiderou os 38 patches e fontes de wrapper/sbt. EnvFile é explícito em PowerShell, com diferenças em Bash e StartDev que precisam ser comparadas pelo critério real. Não atribuir esse trabalho a Augusto nem inferir ausência de evidência do autor.

Fontes: https://github.com/luanmorenommaciel/apex/pull/185 ; https://github.com/luanmorenommaciel/apex/issues/167 ; https://github.com/luanmorenommaciel/apex/issues/174 ; https://github.com/luanmorenommaciel/apex/issues/178 ; https://github.com/luanmorenommaciel/apex/blob/faf8b5723abd7cd0905137e574d515216f74d287/docs/reviews/pr-revalidation-20261019/README.md

## 12. Privacidade e governança têm decisões próprias

O ADR-004 distingue correlação de código-fonte da atribuição execution_id para stages da #115. As cinco precondições são: possibilidade de locator relativo em repouso; configuração opt-in, raiz e sintaxe; identidade de notebook e fallback; payload e compatibilidade; primeiro consumidor. A N09 propõe separar status declarado, implementação e aceite registrado, preservando o histórico. Seis specs done/accepted:false foram conferidas no snapshot e precisam de reconciliação própria, sem aceite inventado. A #184 corrige cinco valores em três YAML por representação com blocos dobrados, sem executar comandos. Nenhuma dessas decisões cria um bloqueio geral para as PRs de testes atuais.

Fontes: https://github.com/luanmorenommaciel/apex/pull/133 ; https://github.com/luanmorenommaciel/apex/pull/184 ; https://github.com/luanmorenommaciel/apex/issues/115 ; https://github.com/luanmorenommaciel/apex/blob/15ab9dc2b587cb187a0413843761db3ec256da4e/docs/reviews/pod3-20261019/DECISAO-ADR-004.md ; https://github.com/luanmorenommaciel/apex/blob/15ab9dc2b587cb187a0413843761db3ec256da4e/docs/reviews/pod3-20261019/GOVERNANCA-TASK-SPECS.md

## 13. Onboarding e distribuição do Serve

A orientação antiga de copiar um mesmo JSON para todos os clientes precisa de precisão. Claude Code, Cursor e Codex têm caminhos e formatos diferentes. O guia local cobre o MCP stdio existente e não depende de aprovar Ask ou N11. Possui pré-requisitos, exemplos sem segredo, verificações e troubleshooting. A redação e o parse dos exemplos não comprovam o setup no aplicativo. Na distribuição, separamos o build e instalação do wheel das ações externas em TestPyPI e PyPI. O nome, canal, conteúdo MCP/API, versão e responsável de release aguardam decisão. O 404 histórico de um nome não reserva esse nome nem prova que nunca houve publicação.

Fontes: https://github.com/luanmorenommaciel/apex/blob/15ab9dc2b587cb187a0413843761db3ec256da4e/docs/reviews/pod3-20261019/GUIA-CLIENTES-SERVE.md ; https://github.com/luanmorenommaciel/apex/blob/15ab9dc2b587cb187a0413843761db3ec256da4e/docs/reviews/pod3-20261019/DECISAO-DISTRIBUICAO.md ; https://code.claude.com/docs/en/mcp ; https://cursor.com/docs/mcp ; https://learn.chatgpt.com/docs/extend/mcp?surface=cli

## 14. O material da complementação está acessível

O pacote já está acessível antes do merge. A #183 preserva o detalhamento das 23 tarefas e os textos integrais das sete minutas que faltavam no primeiro anexo. As outras nove já estavam na #181. A #184 permanece pequena para revisar só a sintaxe. A ata é um modelo, sem reunião ou decisão inventada. Esta apresentação mantém a #181 como referência da minha contribuição, e o time pode complementar ou corrigir o material. O estudo dos 525 IDs está documentado na #186 e recebeu correções de 17 fichas na revalidação. Isso não equivale a 525 aceites funcionais ou liberação de release. Pacote #183 corrigido com 34 arquivos conferidos. A #184 continua uma correção sintática de três YAML, sem alterar estado ou aceite das specs.

Fontes: https://github.com/luanmorenommaciel/apex/issues/181 ; https://github.com/luanmorenommaciel/apex/pull/183 ; https://github.com/luanmorenommaciel/apex/pull/184 ; https://github.com/luanmorenommaciel/apex/blob/15ab9dc2b587cb187a0413843761db3ec256da4e/docs/reviews/pod3-20261019/CONTROLE-EXECUCAO-POD3.md

## 15. O que gostaria de alinhar com vocês

Quero encerrar com próximos passos claros e pequenos, preservando os critérios de cada objeto. Podemos combinar revisores e método de integração sem esperar decidir todas as ideias de futuro. As perguntas de arquitetura ficam em seus trackers específicos. Quando faltar informação, registramos a dúvida e um encaminhamento de retomada. Responsáveis e datas devem refletir o que as pessoas realmente combinarem. A sugestão é manter bloqueios técnicos, decisões pendentes e opiniões identificados, e usar o material como apoio ao trabalho do time. Perguntar se há entregas, evidências ou restrições que precisam entrar ou ser corrigidas.

Fontes: https://github.com/luanmorenommaciel/apex/blob/15ab9dc2b587cb187a0413843761db3ec256da4e/docs/reviews/pod3-20261019/ATA-POD3-MODELO.md ; https://github.com/luanmorenommaciel/apex/issues/181

## 16. Apoio: minhas 11 PRs integradas

Este apoio explica a contagem de 11 PRs: 1 mais 3 mais 2 mais 3 mais 2. As fronteiras com Front, Verify e contrato entram quando afetam o consumo do Serve. Não é um inventário de todas as contribuições de cada colega. A #133 é uma proposta documental e precisa continuar com esse rótulo. As #53 e #54 foram fechadas sem merge e não entram nessa contagem. A #129 é da autoria de PR e implementação principal do Sidymar, com o commit fab6620 de Augusto.

Fontes: https://github.com/luanmorenommaciel/apex/issues/181 ; https://github.com/luanmorenommaciel/apex/pull/44 ; https://github.com/luanmorenommaciel/apex/pull/132 ; https://github.com/luanmorenommaciel/apex/pull/133 ; https://github.com/luanmorenommaciel/apex/pull/134 ; https://github.com/luanmorenommaciel/apex/pull/135 ; https://github.com/luanmorenommaciel/apex/pull/140 ; https://github.com/luanmorenommaciel/apex/pull/143 ; https://github.com/luanmorenommaciel/apex/pull/144 ; https://github.com/luanmorenommaciel/apex/pull/146 ; https://github.com/luanmorenommaciel/apex/pull/150 ; https://github.com/luanmorenommaciel/apex/pull/151

## 17. Apoio: contratos e governança

As 16 minutas foram preparadas para preservar ideias com problema, evidência, limite e critério. Esta primeira metade inclui temas que atravessam pods. N01 e N03 não devem ser confundidas, embora relacionadas à #117. N06 trata credenciais do perfil dev de Infra e não decide o token da API. N07 é a decisão do ADR. N08 registra o calendário oficial da transição do runner e a necessidade de conferir a imagem usada no run, sem afirmar que a migração já foi provada no APEX. Não precisamos abrir uma issue nova para cada minuta antes de discutir prioridade e destino.

Fontes: https://github.com/luanmorenommaciel/apex/blob/15ab9dc2b587cb187a0413843761db3ec256da4e/docs/reviews/pod3-20261019/DESTINOS-MINUTAS.md ; https://github.com/luanmorenommaciel/apex/issues/117 ; https://github.com/luanmorenommaciel/apex/blob/15ab9dc2b587cb187a0413843761db3ec256da4e/docs/reviews/pod3-20261019/minutas/README.md

## 18. Apoio: processo e Serve

Esta metade reúne processo e hipóteses/revisões do Serve. N11 não significa que o MCP atual esteja errado e não está aprovada. N12 é uma leitura do predicado de atribuição, sem incidente real alegado. N13 trata read_only_gate, não deve herdar propriedades da limpeza implementada em outro gate. N15 acrescenta uma pergunta de custo à #156, com vínculo ao job correto. N16 pede reconciliar a lista e o controle, não uma troca mecânica de 7 para 8. N09 conserva o histórico e precisa de uma regra explícita. N10 exige coordenação com a documentação já em revisão.

Fontes: https://github.com/luanmorenommaciel/apex/blob/15ab9dc2b587cb187a0413843761db3ec256da4e/docs/reviews/pod3-20261019/DESTINOS-MINUTAS.md ; https://github.com/luanmorenommaciel/apex/issues/181 ; https://github.com/luanmorenommaciel/apex/issues/156

## 19. O que a revalidação corrigiu

A revalidação inclui 15 PRs abertos e 78 encerrados. Nos históricos, o confronto é documental, não code review completo de todos os patches. A concordância de modelos não foi usada como prova. O time mantém autoridade sobre revisão e integração.

Fontes: https://github.com/luanmorenommaciel/apex/blob/faf8b5723abd7cd0905137e574d515216f74d287/docs/reviews/pr-revalidation-20261019/README.md ; https://github.com/luanmorenommaciel/apex/pull/186

## 20. Apoio: onde conferir e complementar

Links para abrir conforme a pergunta: https://github.com/luanmorenommaciel/apex/issues/181 ; https://github.com/luanmorenommaciel/apex/pull/183 ; https://github.com/luanmorenommaciel/apex/pull/184 ; https://github.com/luanmorenommaciel/apex/issues/156 ; https://github.com/luanmorenommaciel/apex/issues/172 . O recorte da main é c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Fatos históricos, relatos de execução, propostas e decisões humanas mantêm suas distinções. A apresentação é minha visão para discussão e pode receber correções e complementos do time.

Fontes: https://github.com/luanmorenommaciel/apex/issues/181 ; https://github.com/luanmorenommaciel/apex/pull/183 ; https://github.com/luanmorenommaciel/apex/pull/184 ; https://github.com/luanmorenommaciel/apex/issues/156 ; https://github.com/luanmorenommaciel/apex/issues/172 ; https://github.com/luanmorenommaciel/apex/blob/faf8b5723abd7cd0905137e574d515216f74d287/docs/reviews/pr-revalidation-20261019/README.md ; https://github.com/luanmorenommaciel/apex/issues/188 ; https://github.com/luanmorenommaciel/apex/issues/190
