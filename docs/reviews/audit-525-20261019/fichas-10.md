# Fichas documentais — lote 10

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-091"></a>

## #42 — [SPIKE] Definir modo offline/on-prem seguro para agentes Apex

Frente: issues_restantes. Encaminhamento: decidir_prioridade_e_fronteira_offline_onprem.

### Identidade e estado

Issue #42, aberta; assignees: nenhum. Consulta 2026-10-16T18:29:24.609Z. Origens: X05. Responsável futuro a confirmar; disposição decidir_prioridade_e_fronteira_offline_onprem.

### Intenção e benefício

Mapear requisitos de agentes locais/remotos para organizações com restrições de egress, PII, secrets e acesso a código.

### Feito, faltante e não comprovado

A issue permanece aberta e não tem comentários no snapshot. Seus critérios são matriz de riscos, decisão preliminar de deployment e requisitos de redaction/audit trail. Isso não demonstra que nenhuma pesquisa local exista nem ratifica adiamento.

### Linhagem

#42 relaciona #2/#5/#33; contexto é preocupação de produto registrada por Augusto/Luan. Nenhuma dessas relações obriga trocar arquitetura ou criar modo on-prem nesta revisão.

### Fontes e corte

Corpo público preservado em fontes/batch-rest-issues-sources/issue-42.md, extraído da consulta de 16/10; comentários do snapshot-20261016. Ficha de origem: ../parte-03-claude-v2/fontes/claude-v2/C02-ISSUES-ABERTAS.md#i-42, linha 643. Código, quando citado, fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Fontes adicionais abaixo; recibo de custódia da #105 é novo em 17/10.

### Classe e limite da evidência

DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Na #105 há verificação própria de arquivo Git, sem executar código de produto; demais execuções não foram realizadas.

### Fluxo

Entrada/código/dados → fronteira de modelo e ferramentas → políticas de rede/log → resposta e trilha auditável. Modelo local e ferramentas locais não eliminam egress por si.

### Consequências e risco

Chamar solução de offline sem enumerar dependências/conectores pode transmitir uma garantia indevida. Impor disclosure como gate para todo o estudo também bloqueia trabalho independente.

### Alternativas e recomendação

Estudar local-first, BYOC, SaaS e híbrido com requisitos concretos; depois implementar/adiar/rejeitar. A escolha não foi feita pelo usuário ou mantenedor nestas fontes.

### Dependências e paralelismo

Requisitos de #2/#5 e política #33 informam o desenho. O estudo pode começar enquanto canal de disclosure é decidido; implantação exige contrato de operação próprio.

### Plano e aceite propostos

Mapear fluxos de dados, egress, identidade, ferramentas e logs por perfil. Incluir contracasos: modelo local com API externa; modo sem internet com dependência de download. Aceite do estudo: fronteiras, mitigação, owner e decisão preliminar; nenhum runtime requerido para esta leitura.

### Comunicação entre responsáveis

Usar linguagem de capacidade demonstrada e restrição proposta, sem prometer segurança absoluta. Distinguir requisito corporativo de preferência de arquitetura.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Chamar uma solução de offline sem enumerar dependências e conectores daria garantia indevida, e exigir a #33 decidida antes do estudo bloquearia trabalho independente. Que caso o teste ainda não cobre? — Falta mapear quais ferramentas ainda fazem rede, como em modelo local com API externa ou modo sem internet com download; a issue não tem comentários, o que não prova ausência de pesquisa. Como eu explicaria isso para outro pod? — O estudo compara local-first, BYOC, SaaS e híbrido pelo que precisa permanecer no ambiente e por como auditar sem expor conteúdo; qual perfil suportar primeiro não foi decidido.

### Próxima ação e encerramento

Owner produto/segurança a confirmar: decidir prioridade e produzir matriz pequena. Não encerrar por zero comentários nem exigir #33 decidida para iniciar a análise.

<a id="item-092"></a>

## #105 — [Governance] Archive historical contribution branches before deletion

Frente: issues_restantes. Encaminhamento: reconciliar_arquivo_existente_e_custodia.

### Identidade e estado

Issue #105, aberta; assignees: nenhum. Consulta 2026-10-16T18:29:24.609Z. Origens: X06, X12. Responsável futuro a confirmar; disposição reconciliar_arquivo_existente_e_custodia.

### Intenção e benefício

Preservar cinco heads históricos e recuperação verificável antes de qualquer decisão futura de excluir branches, sem mesclar árvores obsoletas na main.

### Feito, faltante e não comprovado

Bundle e quatro metadados existem no arquivo de 26/08. Nesta auditoria, SHA256SUMS passou 5/5, bundle verify passou, os cinco refs foram restaurados em bare temporário e comparados exatamente ao mapa, e fsck full strict passou. O temporário foi removido. Hash do bundle: 5523adca7e3e2a512452145b19c530de7dc8268b5cb4d8297ea809651896b526. Não houve nova consulta de heads/uso remoto; a afirmação pública de arquivo não criado está desatualizada frente à fonte local.

### Linhagem

#105 → arquivo de 26/08 → X06/L03 e catálogo histórico → nova verificação Codex de integridade/restauração em 17/10. Quatro refs pertencem a luanmorenommaciel/apex e um a gustocezar/apex-workspace. Custódia/publicação e exclusão são decisões separadas.

### Fontes e corte

Corpo público preservado em fontes/batch-rest-issues-sources/issue-105.md, extraído da consulta de 16/10; comentários do snapshot-20261016. Ficha de origem: ../parte-03-claude-v2/fontes/claude-v2/C02-ISSUES-ABERTAS.md#i-105, linha 70. Código, quando citado, fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Fontes adicionais abaixo; recibo de custódia da #105 é novo em 17/10.

### Classe e limite da evidência

DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Na #105 há verificação própria de arquivo Git, sem executar código de produto; demais execuções não foram realizadas.

### Fluxo

Refs publicados no snapshot → bundle com refs/archive → mapa e hashes → restauração isolada → comparação de commits. Consulta atual de uso em PRs deve ocorrer imediatamente antes de eventual decisão de exclusão.

### Consequências e risco

Mandar criar tudo de novo ignora um arquivo válido. Usar a restauração para autorizar exclusão seria outro salto: hashes não provam estado remoto atual, ausência de novos consumidores ou aprovação humana.

### Alternativas e recomendação

Reutilizar e registrar custódia do arquivo verificado. Se heads atuais diferirem numa consulta futura, decidir arquivo adicional em vez de sobrescrever história. Publicar bundle no repo é opção explícita do owner, não efeito automático desta revisão.

### Dependências e paralelismo

Arquivo é predecessor estrito de exclusão, já existe para as cinco identidades. Inventário X12 pode informar limpeza mais ampla, mas não é necessário para reconhecer este arquivo. Verificação remota/decisão de exclusão continuam separadas.

### Plano e aceite propostos

Reconciliar critérios da issue com recibo de 17/10 e metadados originais; registrar custodiante/local de recuperação. Antes de excluir no futuro, reconfirmar heads e consultas head/base de PR para cada branch e obter decisão. Controle: SHA divergente/commit faltante impede usar o arquivo como prova correspondente. Nada foi excluído ou publicado.

### Comunicação entre responsáveis

Minuta futura: bundle existente, cinco refs restaurados e limites de atualidade. Não incluir caminhos pessoais em metadado público; aqui a fonte local permanece consultável no recibo da auditoria.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Mandar criar tudo de novo ignoraria um arquivo válido, e usar a restauração para autorizar exclusão seria um salto: hashes não provam estado remoto atual nem aprovação humana. Que caso o teste ainda não cobre? — Os cinco commits restaurados conferem com o mapa, mas não houve nova consulta de heads; se alguma branch avançou e qual consulta de PR sustentaria uma exclusão continuam em aberto. Como eu explicaria isso para outro pod? — O bundle de 26/08 existe e passou por SHA256SUMS 5/5, bundle verify, restauração e fsck em 17/10; o que falta é registrar quem guarda a cópia recuperável, com exclusão e publicação como decisões separadas.

### Próxima ação e encerramento

Custodiante/mantenedor a confirmar: registrar custódia e reconciliar #105 quando autorizado. A criação/restauração já está demonstrada; eventual exclusão/publicação precisa de decisão e evidência novas, fora desta revisão.

<a id="item-093"></a>

## #106 — [ADR/Study] Evaluate a read-only APEX system and contract graph

Frente: issues_restantes. Encaminhamento: decidir_adocao_do_grafo_sem_gates_para_estudos.

### Identidade e estado

Issue #106, aberta; assignees: nenhum. Consulta 2026-10-16T18:29:24.609Z. Origens: X07. Responsável futuro a confirmar; disposição decidir_adocao_do_grafo_sem_gates_para_estudos.

### Intenção e benefício

Avaliar um grafo somente leitura de contratos, campos, produtores, consumidores e classes de evidência, sem substituir as fontes normativas.

### Feito, faltante e não comprovado

Issue aberta com decisão adopt/defer/reject ainda não marcada no snapshot. O registro X07 relata exemplo offline de seis nós/cinco arestas, não revalidado aqui; caixas abertas não provam que nada foi estudado. #180 atualiza matriz de proveniência, sem constituir adoção automática do grafo.

### Linhagem

#103 é semente estática; #106 decide schema/autoridade; #107 MCP, #108 Front e #109 reconciliação runtime são descendentes. A regra pública permite estudos paralelos e segura implementação até decisão de schema.

### Fontes e corte

Corpo público preservado em fontes/batch-rest-issues-sources/issue-106.md, extraído da consulta de 16/10; comentários do snapshot-20261016. Ficha de origem: ../parte-03-claude-v2/fontes/claude-v2/C02-ISSUES-ABERTAS.md#i-106, linha 529. Código, quando citado, fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Fontes adicionais abaixo; recibo de custódia da #105 é novo em 17/10.

### Classe e limite da evidência

DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Na #105 há verificação própria de arquivo Git, sem executar código de produto; demais execuções não foram realizadas.

### Fluxo

Artefato normativo e fonte por aresta → manifesto versionado → consulta/projeção → explicação opcional. Inferência deve continuar distinguível de fato observado.

### Consequências e risco

Um grafo sem fonte por aresta pode congelar inferências como verdade. Adotar dependência externa antes de provar valor aumenta superfície/custo; nenhum incidente foi demonstrado.

### Alternativas e recomendação

Comparar manifesto JSON versionado/gerado com ferramenta externa; considerar adiamento ou rejeição. Recomenda-se exemplo mínimo com fontes atuais antes de escolher infraestrutura.

### Dependências e paralelismo

A semente #103 já tem entrega histórica; #180 pode atualizar conteúdo. Estudos #107–109 podem ocorrer em paralelo. Implementação depende do schema; não impor esperar toda v1 para estudar.

### Plano e aceite propostos

Especificar nós/arestas, precedência de fontes e estado declared/observed/derived/runtime_unproven; revisar um exemplo com edge inválida e fonte ausente. Aceite: decisão fundamentada, fronteira read-only e descendentes delimitados, não execução runtime.

### Comunicação entre responsáveis

Explicar que grafo organiza evidência, não ratifica contratos nem substitui DDL/PIPELINE. Marcar proposta local como proposta até a decisão.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Um grafo sem fonte por aresta congelaria inferências como verdade, e adotar ferramenta externa antes de provar valor aumentaria superfície e custo. Que caso o teste ainda não cobre? — Versões conflitantes ainda não têm forma de preservação, e o exemplo de seis nós e cinco arestas do X07 não foi revalidado; caixas abertas na issue não provam que nada foi estudado. Como eu explicaria isso para outro pod? — O grafo organiza evidência sem ratificar contratos; a pergunta é o que acrescenta à matriz da #180, e estudos de consumidores como #107 e #108 podem ajudar a escolher o schema.

### Próxima ação e encerramento

Mantenedor cross-pod a confirmar: revisar exemplo e decidir adotar/adiar/rejeitar. Encerrar estudo com decisão; não declarar implementação nem adiamento já aprovados.

<a id="item-094"></a>

## #107 — [Study][Pod 3 / Serve] Define a read-only APEX system-graph MCP interface

Frente: issues_restantes. Encaminhamento: estudar_interface_em_paralelo_aguardar_schema_para_implementar.

### Identidade e estado

Issue #107, aberta; assignees: nenhum. Consulta 2026-10-16T18:29:24.609Z. Origens: S13. Responsável futuro a confirmar; disposição estudar_interface_em_paralelo_aguardar_schema_para_implementar.

### Intenção e benefício

Avaliar acesso MCP tipado ao grafo como evidência estruturada, útil a agentes sem consultar telemetria live.

### Feito, faltante e não comprovado

Critérios públicos pedem schemas, fronteira sem rede, fixture aprovada, não invenção e compatibilidade. Não há decisão final marcada no snapshot; não foi realizada busca exaustiva de estudos locais. A main já tem oito tools de diagnóstico, que não devem ser mudados implicitamente.

### Linhagem

#106 decide grafo; #103 fornece semente; #41 é contexto. #107 avalia catálogo, não reinterpreta propriedade de campos nem implementa diagnóstico novo.

### Fontes e corte

Corpo público preservado em fontes/batch-rest-issues-sources/issue-107.md, extraído da consulta de 16/10; comentários do snapshot-20261016. Ficha de origem: ../parte-03-claude-v2/fontes/claude-v2/C02-ISSUES-ABERTAS.md#i-107, linha 548. Código, quando citado, fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Fontes adicionais abaixo; recibo de custódia da #105 é novo em 17/10.

### Classe e limite da evidência

DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Na #105 há verificação própria de arquivo Git, sem executar código de produto; demais execuções não foram realizadas.

### Fluxo

Pergunta de domínio admitido → consulta limitada ao manifesto → resposta tipada com fonte/versão/classe ou recusa explícita. Ausência de ClickHouse não deveria impedir catálogo offline.

### Consequências e risco

Responder fora do domínio por inferência converte desconhecido em fato. Expor manifesto ilimitado pode gerar payload excessivo. Nenhuma falha funcional foi demonstrada nesta leitura de proposta.

### Alternativas e recomendação

Comparar catálogo pequeno APEX com search/get/trace e recurso bounded. Estudar é permitido em paralelo; adiar tudo até #106 concluir é mais restritivo que o corpo público.

### Dependências e paralelismo

Implementação aguarda schema aprovado de #106; desenho e exemplos podem informar essa decisão agora. Não há dependência de iniciar ClickHouse para o estudo.

### Plano e aceite propostos

Definir request/response e limites; exemplos conhecido, ausente, pergunta fora do domínio e versão incompatível. Controle: entrada sem fonte não produz afirmação inventada. Aceite: compatibilidade dos clientes, read-only/no-network e decisão implementar/adiar/rejeitar.

### Comunicação entre responsáveis

Mostrar limites e retorno de recusa aos consumidores; não vender catálogo como consulta runtime. Preservar semântica dos tools existentes.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Responder fora do domínio por inferência converteria desconhecido em fato, e expor o manifesto inteiro sem limite pode gerar payload excessivo. Que caso o teste ainda não cobre? — Conferir os exemplos versionados e o tratamento de resultados no store frente ao schema escolhido. Artefatos existentes não demonstram adoção integral, nem a falta de uma conferência demonstra inexistência. Como eu explicaria isso para outro pod? — O catálogo MCP responde sobre o grafo offline com fonte e versão, ou recusa; não é consulta runtime e não muda os oito tools de diagnóstico, e a implementação espera o schema da #106.

### Próxima ação e encerramento

Owner Serve a confirmar: preparar proposta em paralelo ao schema; implementar somente após ratificação. Encerrar estudo por decisão fundamentada, não por comentário de espera apenas.

<a id="item-095"></a>

## #108 — [Study][Pod 1 / Front-End] Explore topology and evidence-provenance views

Frente: issues_restantes. Encaminhamento: estudar_view_tipificada_sem_dependencia_obrigatoria_mcp.

### Identidade e estado

Issue #108, aberta; assignees: nenhum. Consulta 2026-10-16T18:29:24.609Z. Origens: F15. Responsável futuro a confirmar; disposição estudar_view_tipificada_sem_dependencia_obrigatoria_mcp.

### Intenção e benefício

Escolher uma primeira visualização determinística de topologia/proveniência para explicar disponibilidade e origem das métricas.

### Feito, faltante e não comprovado

O corpo pede wireframe/contrato de componente, payload tipado, estados e decisão. #102/#43 são contexto de fronteira e spike histórico; fechamento deles não implementa esta view. Não se comprovou aqui ausência universal de protótipos.

### Linhagem

#106/#103 → #108; #107 é provedor possível, expressamente não predecessor estrito. #180 pode fornecer proveniência atual como semente, sem tornar UI aprovada.

### Fontes e corte

Corpo público preservado em fontes/batch-rest-issues-sources/issue-108.md, extraído da consulta de 16/10; comentários do snapshot-20261016. Ficha de origem: ../parte-03-claude-v2/fontes/claude-v2/C02-ISSUES-ABERTAS.md#i-108, linha 567. Código, quando citado, fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Fontes adicionais abaixo; recibo de custódia da #105 é novo em 17/10.

### Classe e limite da evidência

DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Na #105 há verificação própria de arquivo Git, sem executar código de produto; demais execuções não foram realizadas.

### Fluxo

Projeção estática versionada ou API tipada → validação → estado missing/optional/observed/runtime_unproven → render determinístico. Prosa LLM pode explicar, não definir a topologia.

### Consequências e risco

Dados hardcoded ou prosa como fonte podem exibir ligações falsas. Recriar Compare/Memory/Verify amplia o escopo. Grafo denso pode perder legibilidade/acessibilidade.

### Alternativas e recomendação

Começar por matriz/linhagem ou pequena topologia conforme valor de uso; comparar manifesto estático com API. Não exigir um catálogo MCP antes do primeiro protótipo.

### Dependências e paralelismo

Implementação depende da decisão de schema #106; estudos podem ser paralelos. Ownership de loading segue fronteira browser/serviço; #107 é opcional.

### Plano e aceite propostos

Esboçar uma view com payload e estados vazios/ausentes; planejar validação de schema, ordenação/render estável e navegação acessível. Negativo: aresta sem fonte não aparece como observada. Aceite do estudo: primeiro recorte e decisão implementar/adiar/rejeitar.

### Comunicação entre responsáveis

Mostrar um exemplo com fato, ausência e runtime não provado sem semáforo de certeza indevida. Dizer quais workflows de produto ficam fora do protótipo.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Usar dados hardcoded ou prosa de LLM como fonte da topologia poderia exibir ligações falsas, e recriar Compare, Memory ou Verify ampliaria o escopo. Que caso o teste ainda não cobre? — Payload desconhecido e grafo grande ainda não têm estado definido, e a navegação acessível de um grafo denso não foi desenhada; protótipos locais não foram procurados exaustivamente. Como eu explicaria isso para outro pod? — A primeira view responde a uma pergunta de usuário e distingue declarado de observado; o provider não precisa ser MCP, já que a #107 é opcional.

### Próxima ação e encerramento

Owner Front a confirmar: escolher view e fonte em coordenação com #106. Não aguardar toda v1 para estudar nem declarar UI pronta por existir matriz.

<a id="item-096"></a>

## #109 — [Study][Pod 2 / Infra] Define declared-contract versus runtime reconciliation

Frente: issues_restantes. Encaminhamento: planejar_reconciliacao_sem_executar_probes.

### Identidade e estado

Issue #109, aberta; assignees: nenhum. Consulta 2026-10-16T18:29:24.609Z. Origens: E05. Responsável futuro a confirmar; disposição planejar_reconciliacao_sem_executar_probes.

### Intenção e benefício

Desenhar comparação segura entre contrato declarado e schema/topologia efetivos, distinguindo metadados de prova de transporte/comportamento.

### Feito, faltante e não comprovado

A issue autoriza desenho, não execução. Preflight #131 cobre compatibilidade mínima para queries e verify-ddl permanece referência de comparação DDL; nenhum deles certifica OTLP inteiro. O plano ainda requer allowlist, identidade e estados.

### Linhagem

#103 evidencia estática; #106 decide modelo do grafo; #95/#131 mostram necessidade de fronteira de schema. #170 é política operacional relacionada, não uma implementação da reconciliação.

### Fontes e corte

Corpo público preservado em fontes/batch-rest-issues-sources/issue-109.md, extraído da consulta de 16/10; comentários do snapshot-20261016. Ficha de origem: ../parte-03-claude-v2/fontes/claude-v2/C02-ISSUES-ABERTAS.md#i-109, linha 586. Código, quando citado, fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Fontes adicionais abaixo; recibo de custódia da #105 é novo em 17/10.

### Classe e limite da evidência

DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Na #105 há verificação própria de arquivo Git, sem executar código de produto; demais execuções não foram realizadas.

### Fluxo

Contrato fixado + alvo identificado → probes read-only permitidos → fatos observados → match/drift/blocked/inconclusive. Transporte/canary/workload são etapas distintas, se aprovadas.

### Consequências e risco

Metadados presentes não provam ingestão nem comportamento. Endpoint não identificado pode levar a comparar outro ambiente. Auto-remediação ampliaria o escopo além do estudo.

### Alternativas e recomendação

Preparar inventário mínimo de probes e recibo antes de qualquer integração. Estudo pode avançar em paralelo a #106/#170; implementação vinculada ao grafo espera schema e execução espera autorização própria.

### Dependências e paralelismo

Schema #106 governa implementação do descendente; design é ready_offline pelo corpo. Política #170 informa possíveis probes sob ingestão, sem bloquear toda especificação.

### Plano e aceite propostos

Enumerar cada leitura, dado retornado, risco/limite e identidade; definir classificação determinística para mismatch/timeout/ambiguidade. Negativo: host/DB divergente não vira match. Aceite: plano, allowlist e recibo sanitizado, sem aplicar DDL ou executar serviços.

### Comunicação entre responsáveis

Explicar quais setas são provadas por metadados e quais precisam de dados reais. Não dizer que grafo verde é E2E verde.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Comparar com um endpoint não identificado pode medir outro ambiente, e incluir comando que muta estado ou auto-remediação ampliaria o estudo além do desenho autorizado. Que caso o teste ainda não cobre? — Metadados presentes não provam ingestão; a aresta que exige canary e a classificação de drift como certeza ou leitura inconclusiva ainda não foram definidas, e nenhum probe foi executado. Como eu explicaria isso para outro pod? — O estudo desenha probes read-only com identidade do alvo comprovada e estados match, drift, blocked e inconclusive; grafo verde não é E2E verde.

### Próxima ação e encerramento

Owners Infra/Engine a confirmar: produzir plano revisável e decidir o recorte. Runtime permanece fora desta revisão; não manter o estudo parado por gates globais não exigidos.

<a id="item-097"></a>

## #112 — [Study][Cross-lane] Define versioned deterministic runbooks and negative baselines

Frente: issues_restantes. Encaminhamento: revisar_schema_local_antes_de_decidir_adocao.

### Identidade e estado

Issue #112, aberta; assignees: gustocezar. Consulta 2026-10-16T18:29:24.609Z. Origens: S12. Responsável futuro a confirmar; disposição revisar_schema_local_antes_de_decidir_adocao.

### Intenção e benefício

Avaliar runbooks versionados e baselines negativos como contrato de evidência para Serve/Memory/Verify, sem criar executor de remediação.

### Feito, faltante e não comprovado

O comentário contém duas etapas: primeiro três objetos ilustrativos; depois JSON Schema e exemplos, com correção do pattern para allowlist @v1 versus @v99. É relato de inspeção/desserialização, não execução de validador nem implementação de consumidor. Não repetir a conclusão inicial de schema ainda não entregue sem mencionar o complemento posterior.

### Linhagem

Salvage de linhas Cowork/Kimi/#105 → #112 → estudo de 11/10 sobre candidato #167/#174 → schema local proposto. Materiais históricos continuam fontes; a frente Kimi atual está cancelada e não é gate de adoção.

### Fontes e corte

Corpo público preservado em fontes/batch-rest-issues-sources/issue-112.md, extraído da consulta de 16/10; comentários do snapshot-20261016. Ficha de origem: ../parte-03-claude-v2/fontes/claude-v2/C02-ISSUES-ABERTAS.md#i-112, linha 605. Código, quando citado, fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Fontes adicionais abaixo; recibo de custódia da #105 é novo em 17/10.

### Classe e limite da evidência

DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Na #105 há verificação própria de arquivo Git, sem executar código de produto; demais execuções não foram realizadas.

### Fluxo

Documento de versão admitida → validação estrutural → classificação da evidência → consumidor determinístico → explicação opcional. Baseline negativa bem formada é diferente de documento inválido.

### Consequências e risco

Uma regex permissiva pode aceitar versão desconhecida; um exemplo negativo válido não deve ser rejeitado só por descrever falha. Misturar schema com executor faz uma proposta parecer produto pronto.

### Alternativas e recomendação

Adotar catálogo mínimo, manter documentação ou adiar/rejeitar com justificativa. Primeiro inspecionar arquivos/versões do candidato, sem exigir nova resposta de LLM.

### Dependências e paralelismo

Owner/consumidor e política de versão condicionam adoção. O estudo não depende de publicar #167/#174; usa esse candidato como exemplo, não como implementação de runbook.

### Plano e aceite propostos

Conferir schema e três exemplos reais; definir ordem de validação, versão desconhecida e comportamento do consumidor. Controle: documento bem formado com resultado negativo continua válido; versão fora da allowlist é rejeitada no nível apropriado. Nenhum validador foi executado nesta ficha.

### Comunicação entre responsáveis

Preservar a cronologia do comentário e declarar quais artefatos foram apenas relatados. Não chamar enum inspecionado de replay determinístico implementado.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Uma regex permissiva aceitaria versão desconhecida, e rejeitar um exemplo negativo bem formado só por descrever falha confundiria dado válido com documento inválido. Que caso o teste ainda não cobre? — O comentário relata inspeção e desserialização do JSON Schema com a correção @v1 × @v99, não execução de validador; nenhum teste exercita a validação em si. Como eu explicaria isso para outro pod? — O schema local é rascunho em revisão, não contrato adotado; quem aprova versão e consumidor decide adotar, manter só documentação ou adiar, sem criar executor de remediação.

### Próxima ação e encerramento

Owner Serve/Memory/Verify a confirmar: revisar arquivos e decidir adoção. Encerrar estudo com decisão e limites; implementação/validação ficam em folha específica se aprovadas.

<a id="item-098"></a>

## #113 — [Harness] Ratify a versioned R9D overhead evidence protocol

Frente: issues_restantes. Encaminhamento: ratificar_protocolo_sem_gate_previo_de_harness.

### Identidade e estado

Issue #113, aberta; assignees: nenhum. Consulta 2026-10-16T18:29:24.609Z. Origens: E06. Responsável futuro a confirmar; disposição ratificar_protocolo_sem_gate_previo_de_harness.

### Intenção e benefício

Definir interpretação reproduzível de overhead/soak antes de usar medições em release, com estimador e limites previamente escolhidos.

### Feito, faltante e não comprovado

O corpo não estabelece threshold universal e mantém +3,73% como medida histórica de um ambiente. Zero comentários não é prova de ausência de trabalho. A decisão de protocolo segue aberta; consertar #167 pode ser necessário ao caminho de execução escolhido, não ao desenho.

### Linhagem

Métodos históricos #73/#74 → #113/E06 → protocolo versionado → futura prova runtime autorizada. #167 é ferramenta candidata, não fonte normativa de threshold.

### Fontes e corte

Corpo público preservado em fontes/batch-rest-issues-sources/issue-113.md, extraído da consulta de 16/10; comentários do snapshot-20261016. Ficha de origem: ../parte-03-claude-v2/fontes/claude-v2/C02-ISSUES-ABERTAS.md#i-113, linha 316. Código, quando citado, fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Fontes adicionais abaixo; recibo de custódia da #105 é novo em 17/10.

### Classe e limite da evidência

DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Na #105 há verificação própria de arquivo Git, sem executar código de produto; demais execuções não foram realizadas.

### Fluxo

Identidade de workload/ambiente → braços ON/OFF equivalentes → amostras/checkpoints → estimador predeclarado → approved/rejected/inconclusive/functional_failure/missing_evidence/pending_threshold.

### Consequências e risco

Escolher threshold após observar resultado ou tratar medida ausente como verde distorce conclusão. Um protocolo correto não prova que o harness atual o executa.

### Alternativas e recomendação

Protocolo on-demand ou gate de release são opções com custo/ownership distintos. Não elevar resultado histórico a meta do produto; recomendar desenho mínimo antes de rodar.

### Dependências e paralelismo

Nenhum predecessor técnico para design no corpo. Execução depende de harness funcional, ambiente e thresholds autorizados. Release gate também depende de capacidade do runner.

### Plano e aceite propostos

Definir versão, run ID imutável, warm-up, amostras, estimador, banda, settlement e retomada. Controles offline para estado ausente, falha funcional e limiar não decidido; equivalência ON/OFF não permite diferenças ocultas de workload.

### Comunicação entre responsáveis

Separar ganho de método de alegação de performance. Informar ambiente, limite de inferência e quem ratificou a banda.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Escolher o threshold depois de ver o resultado, ou tratar medida ausente como verde, distorceria a conclusão; os +3,73% são medida histórica de um ambiente, não meta. Que caso o teste ainda não cobre? — Como um checkpoint incompleto termina e se ON e OFF diferem só na instrumentação ainda não estão definidos; um protocolo correto não prova que o harness atual o executa. Como eu explicaria isso para outro pod? — O protocolo fixa estimador e banda antes dos dados e classifica approved, rejected, inconclusive, functional_failure, missing_evidence ou pending_threshold; quem autoriza o custo de um gate recorrente é decisão de ownership.

### Próxima ação e encerramento

Owner Harness/mantenedor a confirmar: ratificar ou adiar protocolo. Não aguardar #167 para preparar desenho e não executar R9D nesta revisão.

<a id="item-099"></a>

## #114 — [Study][Infra] Rehearse ClickHouse 26.x upgrade and rollback

Frente: issues_restantes. Encaminhamento: decidir_estudo_de_upgrade_sem_alterar_pin.

### Identidade e estado

Issue #114, aberta; assignees: nenhum. Consulta 2026-10-16T18:29:24.609Z. Origens: E07. Responsável futuro a confirmar; disposição decidir_estudo_de_upgrade_sem_alterar_pin.

### Intenção e benefício

Preparar um ensaio de upgrade/rollback do ClickHouse com imagens, schema, ingestão e leituras identificados antes de cogitar mudança do pin.

### Feito, faltante e não comprovado

A fonte Compose lida permanece em 24.8. Experimentos 26.1 históricos são hipóteses, não prova para main ou outra versão 26.x. O corpo declara que esta issue não recomenda upgrade e não autoriza runtime.

### Linhagem

Histórico E2E 26.1 → #114/E07; #94/#95 são guardas relacionadas e #109 fronteira de evidência. Nenhuma prova estática desses itens executou upgrade/rollback.

### Fontes e corte

Corpo público preservado em fontes/batch-rest-issues-sources/issue-114.md, extraído da consulta de 16/10; comentários do snapshot-20261016. Ficha de origem: ../parte-03-claude-v2/fontes/claude-v2/C02-ISSUES-ABERTAS.md#i-114, linha 624. Código, quando citado, fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Fontes adicionais abaixo; recibo de custódia da #105 é novo em 17/10.

### Classe e limite da evidência

DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Na #105 há verificação própria de arquivo Git, sem executar código de produto; demais execuções não foram realizadas.

### Fluxo

Backup verificável → candidato exato → DDL/MV → ingestão Collector/leitura Engine → rollback e validação dos dados. Reiniciar container antigo não prova reversão de volume/schema.

### Consequências e risco

Trocar versão sem rollback pode tornar dados incompatíveis; cache/registry disponível não é prova de compatibilidade. Falha parcial precisa ser um estado explícito, não omitido.

### Alternativas e recomendação

Ensaiar, adiar ou rejeitar conforme necessidade de produto. Definir candidato/digest no momento da decisão; não inventar qual 26.x é apropriado nem recomendar uma versão apenas por número.

### Dependências e paralelismo

Design não tem predecessor técnico segundo o corpo. #109/#170 informam critérios e quietude; execução depende de plano específico e autorização. Não exigir fechamento dos dois estudos para começar este.

### Plano e aceite propostos

Plano com backup, checks de identidade/dados, tabelas/MVs, ingestão/leitura, falha parcial e cleanup próprio. Negativo: rollback com schema/dados divergentes é failure/inconclusive. Aceite do estudo é decisão e matriz de prova; adoção só após evidência apropriada.

### Comunicação entre responsáveis

Dizer versão alvo e que o pin permanece uma decisão separada. Não transpor resultado 26.1 histórico para compatibilidade genérica 26.x.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Trocar a versão sem rollback demonstrado pode deixar dados incompatíveis, e reiniciar o container antigo não prova reversão de volume nem de schema. Que caso o teste ainda não cobre? — Falha parcial durante o upgrade precisa aparecer como estado explícito na matriz; os experimentos 26.1 históricos são hipóteses e não valem para outra versão 26.x, e o digest e o volume do ensaio ainda não foram escolhidos. Como eu explicaria isso para outro pod? — O pin continua em 24.8, e a issue não recomenda upgrade; antes do ensaio é preciso haver motivo de produto, e o rollback se demonstra por backup verificável e validação dos dados, não por reinício.

### Próxima ação e encerramento

Owner Infra/mantenedor a confirmar: decidir necessidade e preparar plano. Nenhuma recomendação de versão, mudança de pin ou execução foi feita.

<a id="item-100"></a>

## #122 — [Decision][Cross-pod] Ratify the Ask HTTP/BFF boundary and atomic publication sequence

Frente: issues_restantes. Encaminhamento: reenquadrar_decisao_ask_sobre_api_existente.

### Identidade e estado

Issue #122, aberta; assignees: nenhum. Consulta 2026-10-16T18:29:24.609Z. Origens: X01, S07, X11. Responsável futuro a confirmar; disposição reenquadrar_decisao_ask_sobre_api_existente.

### Intenção e benefício

Decidir proceed/defer/reject para fronteira Ask HTTP/BFF e ownership por perfil, preservando ferramentas e contratos existentes.

### Feito, faltante e não comprovado

API v1 da #129 foi integrada; o candidato Ask V2 local pertence a outra linha e seu conflito é relatado no catálogo. A decisão não equivale a implementar toda leitura HTTP do zero. Nem aprovação de Ask nem aceite dos patches locais foram demonstrados nesta ficha.

### Linhagem

#102 (fronteira local) + proposta Ask V2/X11 → #122/DEC-07 → #129 integrada muda a base de decisão. #115/#117 são contratos correlatos explicitamente fora da implementação de transporte.

### Fontes e corte

Corpo público preservado em fontes/batch-rest-issues-sources/issue-122.md, extraído da consulta de 16/10; comentários do snapshot-20261016. Ficha de origem: ../parte-03-claude-v2/fontes/claude-v2/C02-ISSUES-ABERTAS.md#i-122, linha 510. Código, quando citado, fixado em c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874. Fontes adicionais abaixo; recibo de custódia da #105 é novo em 17/10.

### Classe e limite da evidência

DIRETO: texto/estado dos objetos e leitura estática explicitamente indicada. RELATO: resultados antigos e candidatos locais não reaceitos integralmente. PROPOSTA: alternativas e critérios futuros. INFERÊNCIA: riscos condicionais, não incidentes. Na #105 há verificação própria de arquivo Git, sem executar código de produto; demais execuções não foram realizadas.

### Fluxo

Cliente Ask → nginx same-origin → adapter Serve → serviços existentes; perfil local pode preservar a fronteira aceita. Perfil compartilhado, auth/Origin/CSRF e identidade são decisões específicas.

### Consequências e risco

Publicar candidato antigo inteiro pode conflitar com API integrada e ampliar trust boundary. Confundir inexistência de stage attribution com impossibilidade de transporte elimina opção explicitamente admitida pelo corpo.

### Alternativas e recomendação

Proceed com slices atualizadas, defer com candidato preservado ou reject com justificativa. A sequência proposta contrato→adapter→Front deve ser reavaliada sobre #129, sem perder independência de revisão.

### Dependências e paralelismo

Relacionar #171 para política de exposição e #115/#117 para limites sem exigir que todos estejam fechados. A própria issue permite expor resultados existentes enquanto atribuição continua indisponível.

### Plano e aceite propostos

Comparar rotas/payloads do candidato com API atual; decidir perfis, cinco intents, oito tools preservados, erros, identidade e ordem atômica. Controle negativo: transporte não muda thresholds, aplica fix ou inventa atribuição. Nomear prova CI/runtime futura, sem executá-la.

### Comunicação entre responsáveis

Mostrar antes/depois da fronteira e o que é decisão versus implementação existente. Não anunciar rejeição/adiamento como fato sem decisão do mantenedor.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Publicar o candidato Ask V2 inteiro pode conflitar com a API v1 integrada pela #129 e ampliar a fronteira de confiança, e confundir falta de atribuição de stage com impossibilidade de transporte eliminaria uma opção admitida pelo corpo. Que caso o teste ainda não cobre? — Onde a identidade é validada e se o perfil local permanece ainda não foram decididos; nem a aprovação do Ask nem o aceite dos patches locais foram demonstrados. Como eu explicaria isso para outro pod? — A decisão é o que o Ask acrescenta à API v1 e qual slice deixa a main coerente sem puxar implementação da #115 ou da #117; proceed, defer ou reject cabe ao mantenedor.

### Próxima ação e encerramento

Mantenedor e owners Front/Serve a confirmar: reenquadrar proposta e registrar proceed/defer/reject. Preservar candidato, sem publicação em bloco ou deploy implícito.

