# Fichas documentais — lote 28

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-271"></a>

## DD05 — Roteamento, debugger e schema de evidência

Frente: tooling_double_diamond. Encaminhamento: encerrar_historico_tooling_parcialmente_revisto.

### Identidade e estado

DD05 é o conjunto de ferramentas atuais da skill: roteamento (references/routing.md), debugger (references/debugger-playbook.md) e schema de evidência (references/evidence-schema.md), mais scripts. Registro: válidos, com sanitização e uma variável por experimento; sem ação. Owner: Augusto (a confirmar).

### Intenção e benefício

Intenção: dar ao diagnóstico uma tabela sinal→ferramenta, regras para abrir JDWP com segurança e uma lista do que a evidência deve registrar. Público: quem usa a skill. Ganho: decisões repetíveis sobre por onde começar e o que guardar.

### Feito, faltante e não comprovado

Leitura integral de routing.md, debugger-playbook.md, evidence-schema.md e preflight: routing exige mesma identidade/ambiente/janela e evidência ts/TTL; playbook escala para JVM sob evidência; schema pede interação, hipótese, variável, resultado e rollback; preflight reporta Git/ferramentas e escuta JDWP 5005, sem identificar serviços da stack. DD07/DD10 tratam complementos. A validade aqui é documental, não execução certificada.

### Linhagem

Linhagem: ferramentas de 30/07 (C49) → registro DD05 (válidos) → revisão de routing.md em 10/10 (DD08/DD09) → playbook, schema e preflight inalterados. Sem elo ausente.

### Fontes e corte

Fontes primárias lidas em 18/10/2026: fontes/batch-revalidated-xldd-sources/local/current-skill__references__routing.md; fontes/batch-revalidated-xldd-sources/local/current-skill__references__debugger-playbook.md; fontes/batch-revalidated-xldd-sources/local/current-skill__references__evidence-schema.md; fontes/batch-revalidated-xldd-sources/local/current-skill__scripts__apex-debug-preflight.sh. Proveniência e SHA-256 dos originais em fontes/batch-revalidated-xldd-sources/local-source-manifest.json; registro/triagem do ID em fontes/batch-revalidated-xldd-sources/selected-register-matrix.json. Relatos de execução permanecem relatos.

### Classe e limite da evidência

FATO OBSERVADO: datas e conteúdo dos arquivos em 18/10; routing.md revisto em 10/10, os demais de 30/07. RELATO: avaliação de validade do registro. Nenhuma execução dos scripts.

### Fluxo

Fluxo: sinal observado —(routing.md: primeira ferramenta e o que não fazer)→ ferramenta —(playbook se JVM)→ evidência —(evidence-schema.md)→ registro sanitizado. Só o primeiro trecho mudou depois de julho.

### Consequências e risco

Sem ação, as ferramentas continuam utilizáveis. O risco é o schema de evidência de julho não pedir campos que as investigações recentes já usam (classe de evidência, alternativas rejeitadas), tema de DD10. Confiança alta.

### Alternativas e recomendação

Recomendado: encerrar DD05 como histórico com a nota de que routing.md mudou em 10/10. Alternativa: revisar playbook e schema agora (é DD10). Reversível.

### Dependências e paralelismo

Nenhuma dependência para catalogar. DD07 (automação de identidade) e DD10 (schema e versão) são independentes entre si e deste encerramento.

### Plano e aceite propostos

Condição de não ação: nenhum passo neste ID. Reabrir se o playbook de JDWP ficar inconsistente com o SKILL.md atual, por exemplo quanto à porta temporária.

### Comunicação entre responsáveis

Para outro pod: "As referências da skill continuam válidas; a de roteamento foi ampliada em 10/10, as de debugger e evidência são de julho."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere abrir JDWP antes de comprovar a fronteira JVM. Que caso o teste ainda não cobre? A leitura não exercita identificação de serviços nem uma sessão real de debug. Como eu explicaria isso para outro pod? Explique roteamento, playbook e schema como artefatos diferentes.

### Próxima ação e encerramento

Próxima ação: catalogar DD05. Owner: nenhum necessário. Entrada: arquivos indexados. Saída: linha DD05 "válidas; routing revisto em 10/10; schema e playbook de julho". Encerramento: imediato.

<a id="item-272"></a>

## DD06 — Parametrizar o escopo autorizado da skill

Frente: tooling_double_diamond. Encaminhamento: externo_tooling_atendido_localmente_em_10_10.

### Identidade e estado

DD06 é uma melhoria de tooling pessoal: parametrizar o escopo autorizado da skill apex-debug-diamond. Minuta local PROP-DD06-SKILL-SCOPE (Kimi, 11/10), não publicada (tooling, fora do APEX). Owner: Augusto (a confirmar).

### Intenção e benefício

Problema registrado: o SKILL.md de julho dizia "Operate only on base-project-e2e-augusto and remote campeonato" e proibia push para origin, enquanto o fluxo atual é PR em luanmorenommaciel/apex; a skill violaria as próprias regras. Público: quem usa a skill no fluxo atual. Ganho: skill utilizável sem burlar suas regras.

### Feito, faltante e não comprovado

Verificação: o SKILL.md instalado em 10/10 removeu o escopo fixo e passou a "Derive the repository, checkout, base/ref, affected components and permitted actions from the current request and repository instructions. Branch and remote names are not evidence of authorization"; publicação exige autorização e destino verificado. A minuta pedia "parâmetro explícito (diretório, remotes, política de push)": a solução instalada é por derivação do pedido, não por parâmetro nomeado. Falta: decidir se a derivação basta ou se um parâmetro explícito ainda é desejado. Não comprovado: aceite formal.

### Linhagem

Linhagem: cópia antiga do SKILL.md com escopo fixo → registro DD06 → revisão instalada que deriva escopo do pedido → minuta de 11/10 expressamente condicional à releitura da skill → leitura independente atual. O mtime e a existência das versões não identificam sozinhos autor nem data de aceite.

### Fontes e corte

Fontes primárias lidas em 18/10/2026: fontes/batch-revalidated-xldd-sources/local/current-skill__SKILL.md; fontes/batch-revalidated-xldd-sources/local/legacy-skill__SKILL.md; fontes/batch-proposals-review-sources/PROP-DD06-SKILL-SCOPE.md. Proveniência e SHA-256 dos originais em fontes/batch-revalidated-xldd-sources/local-source-manifest.json; registro/triagem do ID em fontes/batch-revalidated-xldd-sources/selected-register-matrix.json. Relatos de execução permanecem relatos.

### Classe e limite da evidência

FATO OBSERVADO: escopo fixo ausente na versão instalada. INFERÊNCIA: o problema registrado está resolvido na redação; a forma (derivação × parâmetro) é escolha do dono. Nenhuma execução.

### Fluxo

Fluxo atual: pedido do usuário e instruções do repositório —(derivação)→ repositório, base e ações permitidas —(preflight reporta identidade, não autoriza)→ diagnóstico —(publicação só com autorização e destino verificado)→ PR, se autorizado.

### Consequências e risco

Sem ação, a skill já não força o escopo antigo. O risco remanescente é a derivação ser interpretada de forma frouxa; um parâmetro explícito seria mais auditável. Confiança alta no fato.

### Alternativas e recomendação

Recomendado: considerar DD06 atendido localmente e encerrar, ou, se o dono quiser auditabilidade, acrescentar um campo de escopo no registro de evidência (DD10) em vez de um parâmetro na skill. Alternativa: parâmetro explícito na invocação. Reversível.

### Dependências e paralelismo

Nenhuma dependência do APEX. Relaciona-se a DD10, porque registrar o escopo usado na evidência daria a auditabilidade que um parâmetro explícito daria, sem mudar a invocação.

### Plano e aceite propostos

Passo mínimo: o dono registra que a redação de 10/10 atende DD06 (ou pede o parâmetro). Condição de não ação: nenhuma mudança no repositório APEX.

### Comunicação entre responsáveis

Para outro pod: "A skill de debug já não fixa branch nem remoto; ela deriva o escopo do pedido e só publica com autorização. A minuta DD06 chegou depois dessa correção."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere tratar o nome de uma branch como autorização. Que caso o teste ainda não cobre? Não foi exercitado um pedido ambíguo de escopo na skill instalada. Como eu explicaria isso para outro pod? Explique derivação do pedido versus parâmetro explícito.

### Próxima ação e encerramento

Próxima ação: Augusto (a confirmar) decide se a redação de 10/10 encerra DD06. Entrada: diff desta ficha. Saída: decisão local registrada. Encerramento: DD06 encerrado ou parâmetro explícito adicionado.

<a id="item-273"></a>

## DD07 — Rota de identidade de ambiente (porta/perfil Colima/daemon)

Frente: tooling_double_diamond. Encaminhamento: externo_tooling_parcial_texto_sem_automacao.

### Identidade e estado

DD07 é uma melhoria de tooling pessoal: rota de identidade de ambiente (porta, perfil Colima, daemon) na skill. Minuta local PROP-DD07-ENV-IDENTITY (Kimi, 11/10), não publicada. Owner: Augusto (a confirmar).

### Intenção e benefício

Problema registrado: a lição do C38 (127.0.0.1:8123 apontando para outro perfil Colima) não estava em routing.md nem no preflight; um diagnóstico poderia culpar JVM ou ClickHouse quando o alvo era outro daemon. Público: quem diagnostica no Mac com vários perfis. Ganho: evitar investigar o ambiente errado.

### Feito, faltante e não comprovado

Verificação: o texto foi incorporado — SKILL.md pede registrar "the identity of any service actually used" e diz que "A localhost port alone does not identify the environment"; routing.md manda confirmar mesmo ambiente, identidade lógica e janela antes de rotear. A automação não: apex-debug-preflight.sh (30/07) só reporta identidade Git, ferramentas e a porta 5005 de JDWP, sem dono de porta 8123 nem perfil/daemon. Falta: checagem automática de dono de porta, que pode reaproveitar o candidato E11. Não comprovado: nada executado.

### Linhagem

Linhagem: C38 I3 (29/07) → registro DD07 (study_ready) → SKILL.md e routing.md de 10/10 com a regra textual → minuta PROP-DD07 de 11/10 → preflight inalterado → verificação de 18/10. Elo ausente: automação.

### Fontes e corte

Fontes primárias lidas em 18/10/2026: fontes/batch-revalidated-xldd-sources/local/current-skill__SKILL.md; fontes/batch-revalidated-xldd-sources/local/current-skill__references__routing.md; fontes/batch-revalidated-xldd-sources/local/current-skill__scripts__apex-debug-preflight.sh; fontes/batch-revalidated-xldd-sources/local/C38-R4B-CLEAN-PILOT-DOUBLE-DIAMOND-2026-07-29.md; fontes/batch-proposals-review-sources/PROP-DD07-ENV-IDENTITY.md. Proveniência e SHA-256 dos originais em fontes/batch-revalidated-xldd-sources/local-source-manifest.json; registro/triagem do ID em fontes/batch-revalidated-xldd-sources/selected-register-matrix.json. Relatos de execução permanecem relatos.

### Classe e limite da evidência

FATO OBSERVADO: regra textual presente; preflight sem checagem de porta de serviço. INFERÊNCIA: DD07 está parcialmente atendido. Nenhuma execução.

### Fluxo

Fluxo proposto: preflight —(porta 8123/9000 do ClickHouse e 4318 do Collector)→ dono observado (processo, contêiner, perfil Colima/contexto Docker) —(compara com o esperado da tarefa)→ alerta antes de qualquer hipótese de JVM/ClickHouse. Hoje: só o lembrete textual.

### Consequências e risco

Sem automação, a skill depende de o agente lembrar a regra; a colisão de C38 pode se repetir em ambientes com vários perfis. Impacto local, sem dado de frequência. Confiança alta no estado.

### Alternativas e recomendação

Recomendado: se priorizada pelo dono da skill, desenhar saída read-only de identidade esperada/observada e casos livre, ocupada e ambígua; avaliar reaproveitamento do candidato E11 depois de ler seus bytes e limites. Alternativa: manter checagem manual explícita. A presença de processo na porta não certifica qual stack é a correta.

### Dependências e paralelismo

Não depende do APEX. Pode reaproveitar E11; a classificação "esperado" depende do modelo de identidade de E09, mas portas livres/ocupadas não.

### Plano e aceite propostos

Passos mínimos: (1) acrescentar ao preflight a listagem read-only do dono das portas de serviço; (2) saída sanitizada (sem credenciais); (3) teste com porta livre e ocupada; (4) nota em routing.md apontando para a saída. Aceite: preflight mostra o dono da porta 8123.

### Comunicação entre responsáveis

Para outro pod: "A skill já manda conferir o ambiente antes de culpar o JAR ou o ClickHouse, mas o script de preflight ainda não mostra quem está na porta."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere classificar porta ocupada como ambiente correto. Que caso o teste ainda não cobre? Um teste de porta livre/ocupada ainda não prova perfil Colima e daemon esperados. Como eu explicaria isso para outro pod? Explique a regra textual existente e a automação ainda proposta.

### Próxima ação e encerramento

Próxima ação: Augusto (a confirmar) decide se automatiza a checagem. Entrada: candidato E11 e preflight atual. Saída: preflight com dono de porta ou decisão de manter só texto. Encerramento: decisão registrada.

<a id="item-274"></a>

## DD08 — Checar TTL/ts antes da rota 'materialized-view-loss'

Frente: tooling_double_diamond. Encaminhamento: externo_conclusao_local_preservada_verificada.

### Identidade e estado

DD08 é uma melhoria de tooling: checar TTL e timestamp antes de emitir a rota materialized-view-loss. Registro: conclusão local preservada; não repetir. O resumo [caminho local omitido] registra a rodada concluída. Owner: Augusto.

### Intenção e benefício

Problema: a investigação #71 mostrou que linhas sem timestamp (1970) somem por TTL e imitam perda da MV; o roteador v1 transformava contagens menores em delivery-loss ou materialized-view-loss. Público: quem usa a rota para escolher hipótese. Ganho: não repetir a hipótese retratada da #71.

### Feito, faltante e não comprovado

Conferência atual: o helper instalado tem SHA f45389a5211281c7daeb71cbeb60f04bfccf9fb298742b66ec70015d9205caa6, igual ao DD08-SUMMARY. A leitura do código confirma gates de retenção apenas nos ramos delivery-loss/materialized-view-loss e evidence_origin=caller_supplied. O resumo atribui suítes 50/29 ao hash 16940fd5…22e0 e informa diferenças instaladas em comentários/usage, sem repetir as suítes. Não transferir execução de um hash a outro como teste integral refeito.

### Linhagem

Linhagem: retratação da #71 (11/08 e 22/08) → registro DD08 → rodada de três frentes (Claude 50 casos e 7 negativos; Gemini 29 controles; Kimi revisão estática) → integração local de três arquivos com backup → DD08-SUMMARY → verificação de hash em 18/10. Elo ausente por desenho: aceite formal.

### Fontes e corte

Fontes primárias lidas em 18/10/2026: fontes/batch-revalidated-xldd-sources/local/current-skill__scripts__apex-debug-route.sh; fontes/batch-revalidated-xldd-sources/local/current-skill__references__route-interface.md; fontes/batch-revalidated-xldd-sources/local/DD08-SUMMARY.md. Proveniência e SHA-256 dos originais em fontes/batch-revalidated-xldd-sources/local-source-manifest.json; registro/triagem do ID em fontes/batch-revalidated-xldd-sources/selected-register-matrix.json. Relatos de execução permanecem relatos.

### Classe e limite da evidência

FATO OBSERVADO: hash instalado igual ao declarado, condições estáticas e interface. RELATO HISTÓRICO: suítes 50/29, mutantes, igualdade da lógica, smoke e integração do resumo. INFERÊNCIA: o helper instalado incorpora o gate lido. Sem execução nesta revisão e sem prova ClickHouse.

### Fluxo

Fluxo instalado: contagens por fronteira + evidência de ts/TTL fornecida —(estado de retenção por fronteira)→ rota: perda só se a retenção não explica; senão ttl-expiry-suspected ou timestamp-retention-check com a rota de perda em deferred —(hipótese)→ próximo experimento.

### Consequências e risco

Sem ação, a melhoria já está em uso local. O limite é que a evidência é declarada pelo chamador e não verificada pelo script. Confiança alta no fato instalado.

### Alternativas e recomendação

Recomendado: manter encerrado como conclusão local; não abrir issue APEX. Alternativa: publicar a skill (DD10) para que outros usem a rota v2. Reversível com o backup registrado.

### Dependências e paralelismo

Nenhuma dependência para manter o encerramento. DD10 (versionamento) daria rastreabilidade formal a esta mudança, que hoje existe por hash e pelo backup da integração local.

### Plano e aceite propostos

Condição de não ação: nenhum passo neste ID. Reabrir só se o script instalado deixar de ter o hash f45389a5… sem registro da mudança, ou se um caso real contradisser a rota v2.

### Comunicação entre responsáveis

Para outro pod: "A rota de debug já não culpa a MV ou a entrega quando falta evidência de timestamp e TTL; isso foi instalado localmente em 10/10 e não tem prova contra ClickHouse."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere emitir perda de MV só pela diferença de contagens. Que caso o teste ainda não cobre? As suítes relatadas não provam TTL real e não foram repetidas no hash instalado. Como eu explicaria isso para outro pod? Explique hipótese de retenção, entrada declarada e causa comprovada.

### Próxima ação e encerramento

Próxima ação: catalogar DD08 como concluído localmente. Owner: Augusto. Entrada: DD08-SUMMARY e hash. Saída: linha DD08 "instalado em 10/10, sha f45389a5…; sem aceite formal". Encerramento: imediato.

<a id="item-275"></a>

## DD09 — Rotas de schema atrasado e de lanes consumidoras

Frente: tooling_double_diamond. Encaminhamento: externo_tooling_majoritariamente_atendido.

### Identidade e estado

DD09 é uma melhoria de tooling pessoal: rotas para schema atrasado (ClickHouse Code 47, unknown identifier) e para lanes consumidoras. Minuta local PROP-DD09-ROUTES (Kimi, 11/10), não publicada. Owner: Augusto (a confirmar).

### Intenção e benefício

Problema histórico: a tabela antiga não nomeava schema atrasado nem várias lanes consumidoras. A alegação de que seriam as falhas mais frequentes não tem medição nas fontes lidas. Público: quem diagnostica consumidores. Ganho: escolher a primeira fronteira com base no sintoma.

### Feito, faltante e não comprovado

Verificação: o routing.md instalado em 10/10 tem as linhas "Engine preflight and query requirements disagree → exact SQL, schema contract and a discriminating test" e "Serve/API, Verify, Memory or Front disagree about a known result → input/output payloads and the contract at the first differing boundary"; o SKILL.md manda selecionar a fronteira real, inclusive Serve/API, Verify, Memory ou Front, sem exigir rota JVM. O sinal específico "Code 47 unknown identifier" não aparece literalmente. Falta: decidir se vale nomear o código de erro. Não comprovado: uso real.

### Linhagem

Linhagem: #95/#131 e PIPELINE.md → registro DD09 (study_ready) → routing.md e SKILL.md de 10/10 com rotas de consumidores → minuta PROP-DD09 de 11/10 ("Confirmar na skill atual") → verificação de 18/10.

### Fontes e corte

Fontes primárias lidas em 18/10/2026: fontes/batch-revalidated-xldd-sources/local/current-skill__references__routing.md; fontes/batch-revalidated-xldd-sources/local/current-skill__SKILL.md; fontes/batch-revalidated-xldd-sources/local/legacy-skill__references__routing.md; fontes/batch-proposals-review-sources/PROP-DD09-ROUTES.md. Proveniência e SHA-256 dos originais em fontes/batch-revalidated-xldd-sources/local-source-manifest.json; registro/triagem do ID em fontes/batch-revalidated-xldd-sources/selected-register-matrix.json. Relatos de execução permanecem relatos.

### Classe e limite da evidência

FATO OBSERVADO: linhas de rota para preflight×query e para consumidores presentes em routing.md de 10/10; o código 47 não é nomeado. INFERÊNCIA: DD09 está majoritariamente atendido. Nenhuma execução.

### Fluxo

Fluxo atual: falha num consumidor —(routing.md: primeira fronteira divergente)→ payloads de entrada e saída e o contrato —(teste discriminante)→ hipótese, sem passar pelo JVM. Para schema atrasado: preflight do Engine × SQL exata × contrato de schema.

### Consequências e risco

Sem ação, a skill já orienta bem os consumidores; nomear o Code 47 ajudaria reconhecimento rápido do sintoma, sem mudar a rota. Confiança alta.

### Alternativas e recomendação

Recomendado: considerar as rotas consumidoras atendidas no texto atual; opcionalmente nomear Code 47/unknown identifier como sintoma que exige conferir SQL, schema, alias e versão. O erro sozinho não prova schema atrasado. Alternativa: encerrar sem esse exemplo. Mudança textual é reversível.

### Dependências e paralelismo

Nenhuma dependência do APEX. A linha opcional do Code 47 pode ser feita junto com DD10, para entrar já numa versão rastreável da skill; não depende de #131, que já está integrada.

### Plano e aceite propostos

Passo mínimo opcional: uma linha em routing.md com o sintoma Code 47. Condição de não ação: se o dono considerar a rota atual suficiente, encerrar.

### Comunicação entre responsáveis

Para outro pod: "A skill de debug já sabe começar por payloads e contrato quando Serve, Verify, Memory ou Front discordam; só não cita o erro Code 47 pelo nome."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere interpretar Code 47 como prova automática de migration atrasada. Que caso o teste ainda não cobre? Não foi exercitado um caso real de consulta divergente entre as lanes. Como eu explicaria isso para outro pod? Explique a primeira fronteira divergente e a decisão opcional de nomear o erro.

### Próxima ação e encerramento

Próxima ação: Augusto (a confirmar) decide se acrescenta a linha do Code 47. Entrada: routing.md atual. Saída: linha acrescentada ou DD09 encerrado. Encerramento: decisão registrada.

<a id="item-276"></a>

## DD10 — Schema de evidência e versionamento da skill

Frente: tooling_double_diamond. Encaminhamento: externo_tooling_aberto_versionar_e_schema.

### Identidade e estado

DD10 é uma melhoria de tooling pessoal: versionar a skill e enriquecer o schema de evidência. Minuta local PROP-DD10-EVIDENCE-SCHEMA (Kimi, 11/10), não publicada. Owner: Augusto (a confirmar).

### Intenção e benefício

Problema registrado: evidence-schema.md não exige tabela de interações, alternativas rejeitadas, classe de evidência (relato × observação direta) nem hash de Task-Spec pré-submissão (#85); e a skill só existe em [caminho local omitido] e numa branch arquivada. Público: quem compara investigações e quem precisa recuperar a skill. Ganho: fechamentos comparáveis e skill recuperável por versão.

### Feito, faltante e não comprovado

Leitura do evidence-schema.md atual (857 bytes, 8df6ab95…): ele já exige número da interação, fase, hipótese, variável alterada, resultado e aprendizagem. Não exige formato tabular, alternativas rejeitadas, classe relato/direto nem hash de Task-Spec pré-submit. SKILL.md tem name/description, sem versão declarada; não foi localizado Git próprio nessa pasta. Cópias com hash permitem recuperação, mas não demonstram o histórico completo das mudanças. Um repositório externo da skill não foi procurado exaustivamente.

### Linhagem

Linhagem: padrão DD01, A39 e #85 → registro DD10 (study_ready) → minuta PROP-DD10 → nenhuma mudança no schema em 10/10 → verificação de 18/10. Elo ausente: versionamento.

### Fontes e corte

Fontes primárias lidas em 18/10/2026: fontes/batch-revalidated-xldd-sources/local/current-skill__references__evidence-schema.md; fontes/batch-revalidated-xldd-sources/local/current-skill__SKILL.md; fontes/batch-revalidated-xldd-sources/local/DOUBLE-DIAMOND-EXECUTION-STANDARD.md; fontes/batch-proposals-review-sources/PROP-DD10-EVIDENCE-SCHEMA.md. Proveniência e SHA-256 dos originais em fontes/batch-revalidated-xldd-sources/local-source-manifest.json; registro/triagem do ID em fontes/batch-revalidated-xldd-sources/selected-register-matrix.json. Relatos de execução permanecem relatos.

### Classe e limite da evidência

FATO OBSERVADO: campos já existentes e lacunas textuais delimitadas, ausência de versão declarada no arquivo lido. PROPOSTA: enriquecer evidência e vincular versão a manifesto/commit. NÃO VERIFICADO: eventual repositório externo; não afirmar que a skill só existe nestas cópias.

### Fluxo

Fluxo proposto: investigação —(interações, alternativas e classe da prova; spec quando aplicável)→ evidência estruturada —(manifesto de bytes e versão/commit em destino escolhido)→ comparação e recuperação. O formato de metadados deve respeitar o consumidor da skill.

### Consequências e risco

Sem ação, as investigações continuam registráveis, mas menos comparáveis, e mudanças como as de 10/10 ficam sem histórico formal. Impacto de processo, não de produto. Confiança alta.

### Alternativas e recomendação

Recomendado: escolher destino de versionamento do usuário, registrar os bytes atuais e anteriores com proveniência e ampliar o schema proporcionalmente; Task-Spec/hash só quando existir essa entidade. Alternativas: manifesto local na custódia ou repositório dedicado. Versão pode ficar em changelog/manifesto, sem presumir suporte a campo novo no frontmatter.

### Dependências e paralelismo

Não depende do APEX nem de CI. É a dependência natural para dar rastreabilidade a DD06, DD08 e DD09, mas nenhuma delas precisa esperar DD10 para ser considerada atendida localmente.

### Plano e aceite propostos

Passos: (1) dono escolhe destino e política de visibilidade; (2) snapshot com hashes e origem das cópias; (3) schema registra alternativas, classe da evidência e vínculo opcional à spec; (4) identificador recuperável de versão/commit e exemplo de fechamento. Aceite documental: recuperar os bytes pela versão e distinguir prova direta, relato e não aplicável; sem novo runtime APEX.

### Comunicação entre responsáveis

Para outro pod: "A skill de debug não tem versão nem repositório; ela foi melhorada em 10/10 sem histórico formal. DD10 propõe versioná-la e acrescentar ao registro de evidência alternativas rejeitadas e classe de evidência."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Considere acrescentar versão sem registrar os bytes aos quais ela se refere. Que caso o teste ainda não cobre? Uma tag não testa se as evidências distinguem relato de observação direta. Como eu explicaria isso para outro pod? Explique recuperação por hash, histórico por commit e campos opcionais da Task-Spec.

### Próxima ação e encerramento

Próxima ação: Augusto (a confirmar) escolhe o destino de versionamento. Entrada: arquivos indexados da skill. Saída: repositório com tag e schema atualizado. Encerramento: versão publicada no destino escolhido.

<a id="item-277"></a>

## T-20260923-console-findings-transitions-projection — T-20260923-console-findings-transitions-projection.md

Frente: Serve+Front / paridade da Console (#153). Encaminhamento: reconciliar_status_implementado_e_registrar_decisao_do_probe.

### Identidade e estado

`tasks/T-20260923-console-findings-transitions-projection.md` (blob 0bc8402c). 'Serve findings and transitions in the console's projection', M, standard, P2; owner `(none)`; sem dependências; source_note front/src/data/queries.ts. Estado no SHA: `in-progress`, `accepted: false`, sem assinatura. Pods prováveis: Pod 3/Serve e Pod 1/Front (caminhos serve/ e front/); nenhum pod no arquivo. Spec criada com status in-progress no commit 9841119362 (agmarcastro, 2026-09-29, 'close the eight serve-api leaves, add the two sweep manifests'), integrada pela PR #153 em 2026-10-06 (merge c9c35cf); nenhum commit posterior mudou o status. Plano tasks/.plans/serve-api-sweep.yaml:45 (approved: true; não é autorização atual).

### Intenção e benefício

Fazer as rotas `/v1/runs/{job}/findings` e `/transitions` servirem a projeção que a Console lê (FindingRow com ts, ordem confidence_score DESC; uma linha por execution_id no maior update_seq com job_id, plan_fingerprint e ts) e criar um teste de paridade que leia os campos do TypeScript, para que o 'sexto' mapeamento por nome não volte a acontecer. Beneficia quem usa a Console via API: /verify abre no finding de maior confiança e re-planejamentos não são contados três vezes.

### Feito, faltante e não comprovado

Feito no SHA: `console_findings()` e `console_plan_transitions()` em `ch.py:1075-1099` (introduzidos antes da folha por fab6620, #129), rotas em `resources.py:111-131` usando-os, e o teste `test_every_console_field_is_projected` (`test_api_resources.py:264-280`, commit 993eaa7) com controles discriminantes: remove `ts` e troca o alias de plan_fingerprint e exige falha, e mostra que a projeção MCP falha em `ts`. Divergências da spec: o método chama-se `console_plan_transitions` (não `console_transitions`); e a spec propunha 'não sondar' as colunas aditivas v0.2, enquanto o código mantém o probe (`_console_findings_sql(self.findings_columns())`). O corpo da #153 registra 'the base prevails ... it keeps the v0.2 column probe'. Ordem atual: `confidence_score DESC, finding_id ASC` (desempate por c4541a5, commit direto na main). Falta: status/aceite. Não comprovado aqui: paridade live (relatada).

### Linhagem

queries.ts (FINDINGS/PLAN_TRANSITIONS) → revisão da #129 → fab6620 (base) → plano serve-api-sweep → spec 9841119362 (in-progress) → teste de paridade 993eaa7 → #153 (2026-10-06) → desempate c4541a5 direto na main (18:57, depois do merge) → #159 aberta (gate de paridade, fora deste SHA). Elos ausentes: atualização da spec com a decisão do probe; aceite formal; o eval_2 nomeia `test_console_transitions_collapse_per_execution` etc. (presentes em `test_ch.py:1131-1205`).

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__T-20260923-console-findings-transitions-projection.md; fontes/batch-revalidated-specs58-sources/history/T-20260923-console-findings-transitions-projection.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__ch.py; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_api__routes__resources.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_api_resources.py; fontes/batch-revalidated-specs58-sources/git/serve__VALIDATION.md; fontes/batch-revalidated-specs58-sources/public-captured-pulls.json. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

FATO OBSERVADO: métodos, SQL, rotas e testes nomeados nos evals presentes; probe mantido; desempate por finding_id. RELATO HISTÓRICO (corpo #153, autor): 'serve 314/314', 'parity gate 17/17 seeded, against the infra stack' — execução local, não CI (o corpo diz 'CI is billing-locked'), não aceite humano. INFERÊNCIA: evals 1–3 satisfeitos pelo código; eval_4 roda arquivos inteiros. DECISÃO registrada só no corpo da PR (probe mantido), não na spec: precisa ratificação documental. Nenhuma execução nesta revisão.

### Fluxo

Fluxo observado estaticamente: Console (http) → GET /v1/runs/{job}/findings → resources.findings → ReadStore.console_findings → findings_columns() (probe system.columns) → SELECT ... ORDER BY confidence_score DESC, finding_id ASC → wire() → FindingRow[]; transitions → console_plan_transitions → CTE fp (fingerprint de spark_events) + argMax por execution_id → PlanTransitionRow[]. Porta do navegador: queries.ts → ClickHouse HTTP como apex_ro.

### Consequências e risco

A projeção e o controle estático estão presentes. Persistem a divergência proposta/implementada do probe e a necessidade de vincular a prova terminal de paridade ao objeto aceito. A leitura estática reduz a dúvida de implementação, sem certificar correção runtime universal.

### Alternativas e recomendação

Reconciliar a decisão de manter o probe e o desempate em uma nota. O Context exige paridade live como prova terminal do acceptor: localizar e vincular os recibos históricos pertinentes com SHA, ambiente e cobertura, e registrar o juízo do acceptor. done pode expressar implementação concluída; accepted continua separado.

### Dependências e paralelismo

Não há dependência de código declarada. A aceitação terminal depende de evidência live row-for-row e do acceptor, conforme Context. A revisão documental pode preparar o vínculo dos registros de #153/VALIDATION; não executa o gate.

### Plano e aceite propostos

Conferir os registros #153 e serve/VALIDATION.md com seus SHAs, ambientes, jobs e limites; anexar a prova row-for-row obrigatória à nota de aceitação ou manter essa evidência pendente. Registrar a decisão do probe e o desempate c4541a5. Os controles estáticos existentes verificam aliases; não substituem a prova live.

### Comunicação entre responsáveis

Explicar: 'Findings e transitions já servem a projeção da Console desde fab6620/#153, com um teste que lê os campos do TypeScript e falha se um alias some. A spec ficou in-progress e ainda descreve não sondar colunas v0.2; a PR decidiu manter o probe.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Se a rota voltasse a usar `findings()` do MCP, /verify abriria no finding mais antigo e a Console perderia `ts`; o teste de paridade falharia por `ts`. Que caso o teste ainda não cobre? — Um cluster pré-v0.2 sem `confidence_score`, em que a ordem cai para o valor default e o desempate por finding_id decide sozinho. Como eu explicaria isso para outro pod? — 'A mesma linha precisa sair igual pelas duas portas; quem escreve uma rota nova copia a projeção da Console, não o nome do método.'

### Próxima ação e encerramento

Ação: reconciliar implementação, decisão do probe e evidência terminal. Owner a confirmar: Serve/acceptor. Entrada: spec, commits e registros #153/VALIDATION. Saída: estado documental justificado, com done separado de accepted. Encerramento da aceitação: prova live vinculada ao objeto e decisão explícita do acceptor; mover o arquivo, isoladamente, não basta.

<a id="item-278"></a>

## T-20260923-console-http-deployment-wiring — T-20260923-console-http-deployment-wiring.md

Frente: Front / implantação em modo http (#153). Encaminhamento: reconciliar_status_implementado_prova_nginx_browser_segue_em_172.

### Identidade e estado

`tasks/T-20260923-console-http-deployment-wiring.md` (blob 2912855e). 'Let compose, make prod and the README run the console in http mode', S, standard, P2; owner `(none)`; sem dependências. Estado `in-progress`, `accepted: false`. Pod provável: Pod 1/Front (e Pod 3 pela API). Spec criada com status in-progress no commit 9841119362 (agmarcastro, 2026-09-29, 'close the eight serve-api leaves, add the two sweep manifests'), integrada pela PR #153 em 2026-10-06 (merge c9c35cf); nenhum commit posterior mudou o status.

### Intenção e benefício

Permitir que `make up` (compose) alcance a API do host pelo proxy de dev, que `make prod` aceite APEX_API_UPSTREAM e APEX_API_TOKEN, e que README/.env.example descrevam o modo http como existente. Benefício: os pontos de entrada do repositório fazem o que o RUNBOOK §5 descrevia à mão.

### Feito, faltante e não comprovado

Implementado (3348582, #153): Makefile define `APEX_API_UPSTREAM ?= http://host.docker.internal:8099` e `APEX_API_TOKEN ?=` e passa ambos com -e no `prod` (linhas 29-30, 84-85), sem APEX_API_URL (comentário linha 27); README documenta `VITE_DATA_SOURCE=http ... make dev/make up` e `make prod DATA_SOURCE=http ...` (linhas 27-28, 79) e a linha /ask diz que as peças existem e falta decisão de produto `D-2026-09-23-ask-consumer`; .env.example lista as variáveis da API. Falta: status/aceite. Não comprovado: imagem nginx e navegador reais — esta folha só renderiza config; a prova visual é objeto da #172 (aberta).

### Linhagem

RUNBOOK §5 (manual) → plano serve-api-sweep:351 → spec 9841119362 → 3348582 → #153 → spec in-progress; README depois reconciliado também por #132. Elos ausentes: aceite; prova de imagem/browser (#172).

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__T-20260923-console-http-deployment-wiring.md; fontes/batch-revalidated-specs58-sources/history/T-20260923-console-http-deployment-wiring.txt; fontes/batch-revalidated-specs58-sources/git/front__docker-compose.yml; fontes/batch-revalidated-specs58-sources/git/front__Makefile; fontes/batch-revalidated-specs58-sources/public-captured-pulls.json. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

FATO OBSERVADO: compose e Makefile passam upstream/token e não passam URL cross-origin. Não houve docker compose config nem make -n; renderização é resultado a conferir no recibo histórico. O eval_3 exige upstream/token, mas não o APEX_API_URL pedido em B-4; é uma lacuna no controle documental, sem implicar ausência da variável.

### Fluxo

Fluxo observado (config): shell VITE_DATA_SOURCE=http → compose → Vite proxy /v1 → host.docker.internal:8099 → apex-api; `make prod` → docker run -e DATA_SOURCE/APEX_API_UPSTREAM/APEX_API_TOKEN → entrypoint escreve /config.js → nginx proxia /v1 → API. Token vai do shell para o bundle; nunca literal nos arquivos.

### Consequências e risco

Sem ação: nenhuma regressão. Limite: renderizar a config não prova que nginx e o navegador funcionam — o próprio corpo da spec cita a lição da #129 (grep passou num arquivo que o nginx rejeitou). Risco de segurança conhecido e decidido em outro lugar: o token fica no bundle do navegador (custódia é a #171). Confiança alta nos fatos.

### Alternativas e recomendação

Reconciliar a implementação observada com o estado da folha e seus recibos; documentar que renderizar configuração e validar imagem/navegador são provas diferentes. As remissões #171/#172 são herdadas do levantamento e não foram consultadas de novo. Manter accepted separado de done.

### Dependências e paralelismo

Sem dependência técnica. A prova de #172 depende de imagem/navegador e ambiente; a decisão de token (#171) é política. Ambas podem correr em paralelo ao fechamento documental.

### Plano e aceite propostos

Preparar nota de status com 3348582/#153 e recibo específico de renderização, quando localizado. Conferir a lista inteira de variáveis de B-4 na documentação; a asserção textual atual omite APEX_API_URL. Preservar ausência de APEX_API_URL no comando de execução. A prova de imagem/browser tem escopo próprio.

### Comunicação entre responsáveis

Explicar: 'compose, make prod e o README já suportam o modo http (3348582, #153). Isso prova a configuração, não o nginx nem o navegador, que seguem na #172; quem guarda o token é a #171.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Com o alvo 127.0.0.1 dentro do container, o proxy apontaria para o próprio container; passando APEX_API_URL, o navegador faria chamada cross-origin que a API não permite. Que caso o teste ainda não cobre? — A imagem nginx real servindo /v1 e o navegador renderizando as telas com o token injetado. Como eu explicaria isso para outro pod? — 'Esta folha prova que a configuração sai certa; a implantação funcionando é outra prova, com outra issue.'

### Próxima ação e encerramento

Ação: reconciliar status com remissões. Owner a confirmar: Front. Entrada: 3348582, #171, #172. Saída: spec em done com escopo de garantia explícito. Encerramento: arquivo movido e remissões anotadas.

<a id="item-279"></a>

## T-20260923-navbar-source-badge — T-20260923-navbar-source-badge.md

Frente: Front / identidade da fonte de dados (#153). Encaminhamento: reconciliar_status_implementado_e_ratificar_tom_visual.

### Identidade e estado

`tasks/T-20260923-navbar-source-badge.md` (blob 3ce00f21). 'Name the http source in the console header', XS, standard, P2; owner `(none)`; sem dependências. Estado `in-progress`, `accepted: false`. Pod provável: Pod 1/Front (caminho front/; nenhum pod no arquivo). Spec criada com status in-progress no commit 9841119362 (agmarcastro, 2026-09-29, 'close the eight serve-api leaves, add the two sweep manifests'), integrada pela PR #153 em 2026-10-06 (merge c9c35cf); nenhum commit posterior mudou o status.

### Intenção e benefício

Fazer o cabeçalho nomear a fonte real (clickhouse, http/apex-api, fixtures) por um mapa exaustivo, para que um quarto tipo seja erro de tipo e não um fallthrough. Benefício: a Console não afirma 'fixtures' quando as linhas vieram da API.

### Feito, faltante e não comprovado

Implementado (commit b9ed38a, #153): `const SOURCE: Record<Repository["kind"], ReactNode>` em `NavBar.tsx:14-17` e uso `SOURCE[repo.kind]` (linha 53); teste `NavBar.test.tsx` com três casos (http nomeia apex-api e não o run gravado; mantém clickhouse; mantém fixtures). Isso contradiz a classificação da v2 'VERIFICAR (sem indício por grep)': há commit dedicado e o arquivo de teste criado existe. B-3 (tsc falha com tipo sem rótulo) é garantido pelo `Record` exaustivo — por leitura do tipo, não por execução de tsc. A escolha visual (http com o mesmo '●' certificado do clickhouse) era 'proposta, aberta ao dono visual' e foi aplicada; ratificação não localizada.

### Linhagem

NavBar.tsx:39-43 (ramo binário) → plano serve-api-sweep:242 → spec 9841119362 → b9ed38a → #153 → spec in-progress. Elos ausentes: ratificação do dono visual; aceite formal.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__T-20260923-navbar-source-badge.md; fontes/batch-revalidated-specs58-sources/history/T-20260923-navbar-source-badge.txt; fontes/batch-revalidated-specs58-sources/git/front__src__components__molecules__NavBar.tsx; fontes/batch-revalidated-specs58-sources/git/front__src__components__molecules__NavBar.test.tsx; fontes/batch-revalidated-specs58-sources/public-captured-pulls.json. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

FATO OBSERVADO: mapa exaustivo e teste com os três tipos. RELATO: 'front 166/166, tsc, eslint, build' no corpo da #153 (local). INFERÊNCIA: evals 1 e 2 satisfeitos. DECISÃO PENDENTE de ratificação: tom '●' para http (identidade visual). Nenhuma execução nesta revisão.

### Fluxo

Fluxo observado: runtimeConfig → resolveRepository → repo.kind → NavBar → SOURCE[kind] → texto/ícone do cabeçalho. Teste monta NavBar com useRepository simulado por tipo.

### Consequências e risco

Implementação do rótulo observada, com teste de cada kind e Record exaustivo. Isso não prova ausência universal de risco funcional: resolver/runtime e ratificação visual ficam fora dos testes lidos. A classificação antiga sem indício deve ser corrigida para evitar retrabalho.

### Alternativas e recomendação

Recomendado: done com nota (b9ed38a/#153) e pedido explícito de ratificação do tom visual ao dono da identidade. Alternativa: tom '◐' (retido) para http se o dono considerar que dado vindo por API ainda não é 'certificado' — decisão de produto, reversível em uma linha.

### Dependências e paralelismo

Nenhuma dependência técnica: o tipo Repository["kind"] e os três repositórios já existem. A ratificação visual do tom é decisão humana que pode correr em paralelo; o fechamento documental independe das folhas serve e de qualquer ambiente.

### Plano e aceite propostos

Passos: (1) nota de fechamento; (2) registrar a decisão de tom (ratificada ou alterada) com o dono visual; (3) controle discriminante existente: teste http 'não diz fixtures'; (4) controle de exaustividade pelo tipo Record — se quiser prova executável, um teste de tipo (ts-expect-error) para um kind sem rótulo. Doc: nenhuma.

### Comunicação entre responsáveis

Explicar: 'O cabeçalho já nomeia apex-api quando a fonte é http (b9ed38a, #153). Falta só registrar o fechamento e o dono visual confirmar o tom do ícone.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Com um terceiro else-if, um novo tipo de repositório cairia de novo no rótulo de fixtures sem erro de compilação. Que caso o teste ainda não cobre? — O modo `auto` resolvendo para http em runtime: o teste injeta o tipo diretamente e não passa pelo resolver. Como eu explicaria isso para outro pod? — 'O rótulo vem do tipo resolvido do repositório, não da configuração pedida; e o compilador obriga a nomear qualquer fonte nova.'

### Próxima ação e encerramento

Ação: reconciliar status da implementação e registrar decisão visual. Owner a confirmar: Front/dono visual. Entrada: b9ed38a/#153 e os testes lidos. Saída: nota com escopo e recibos; done pode registrar entrega de código, enquanto accepted exige seu responsável e evidência. Não há novo aceite nesta auditoria.

<a id="item-280"></a>

## T-20260923-run-rollup-unindexed-sentinel — T-20260923-run-rollup-unindexed-sentinel.md

Frente: Serve+Front / paridade da Console (#153). Encaminhamento: reconciliar_status_implementado_com_prova_live_relatada.

### Identidade e estado

`tasks/T-20260923-run-rollup-unindexed-sentinel.md` (blob 51af2ca2). 'Report an unindexed run as null, not zero, in both rollups', S, standard, P2; owner `(none)`; depends_on findings-transitions-projection (dependência de ordem de escrita, declarada como tal). Estado `in-progress`, `accepted: false`. Pods prováveis: Pod 3/Serve e Pod 1/Front (caminhos serve/ e front/); nenhum pod no arquivo. Spec criada com status in-progress no commit 9841119362 (agmarcastro, 2026-09-29, 'close the eight serve-api leaves, add the two sweep manifests'), integrada pela PR #153 em 2026-10-06 (merge c9c35cf); nenhum commit posterior mudou o status.

### Intenção e benefício

Fazer as duas cópias do rollup (navegador e serve) marcarem um LEFT JOIN perdido com uma coluna sentinela e derivar -1/''/'unknown', para que um run não indexado pela memory apareça como 'não indexado' e não como zero medido. Benefício: a Console deixa de afirmar um número que ninguém mediu.

### Feito, faltante e não comprovado

Feito no SHA (commit 31f16ff, #153): CTE emite `1 AS indexed` e o SELECT lê `if(s.indexed = 1, ..., -1/''/'unknown')` (`ch.py:355-390`, comentários explicam por que não `SETTINGS join_use_nulls` com apex_ro readonly=1); teste do navegador em `front/src/data/queries.test.ts:18-28`; testes serve `test_run_rollup_marks_a_missed_shapes_join`, `..._carries_no_settings_clause`, `..._matches_the_console_sql` (`test_ch.py:1210-1250`). Divergência menor: B-1 cita task_time_ms, shaped_stage_count, plan_fingerprint e config_source; o código também marca `shape_count` (0 no miss), não pedido nem contraditório. O RUNBOOK 'Known gaps' não contém mais a frase do gap (eval_4). Falta: status/aceite.

### Linhagem

RUNBOOK 'Known gaps' → plano serve-api-sweep:114 → spec 9841119362 → 31f16ff → #153 → spec in-progress. Elo de prova: o corpo da #153 relata confirmação live 'pondo a declaração antiga de volta: browser -1 != api 0' e o gate de paridade em modo semeado. Elos ausentes: aceite formal; recibo anexado à spec.

### Fontes e corte

Fontes primárias da revalidação no SHA c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874: fontes/batch-revalidated-specs58-sources/git/tasks__T-20260923-run-rollup-unindexed-sentinel.md; fontes/batch-revalidated-specs58-sources/history/T-20260923-run-rollup-unindexed-sentinel.txt; fontes/batch-revalidated-specs58-sources/git/serve__src__apex_mcp__ch.py; fontes/batch-revalidated-specs58-sources/git/serve__tests__test_ch.py; fontes/batch-revalidated-specs58-sources/git/front__src__data__queries.test.ts; fontes/batch-revalidated-specs58-sources/git/serve__VALIDATION.md; fontes/batch-revalidated-specs58-sources/public-captured-pulls.json. Integridade dos arquivos: fontes/batch-revalidated-specs58-sources/MANIFEST.json. Os trechos decisivos e limites estão nos campos3/6 e no registro semantic_review; fontes da ficha anterior não citadas aqui não foram promovidas a releitura independente.

### Classe e limite da evidência

FATO OBSERVADO: sentinela e testes nas duas cópias; ausência de SETTINGS. RELATO HISTÓRICO: confirmação live e 17/17 do gate semeado (autor, local). INFERÊNCIA: evals 1–4 satisfeitos pelo código; o comportamento de preenchimento por DEFAULT do ClickHouse é exatamente o que nenhum teste offline prova — a spec reconhece. Nenhuma execução nesta revisão. DECISÃO: nome `indexed` era 'escolha proposta'; foi adotado sem objeção registrada.

### Fluxo

Fluxo observado: spark_events (run) LEFT JOIN shapes(run_outcomes...) → miss preenche DEFAULT (join_use_nulls=0) → `s.indexed` = 0 → if(...) → -1/''/'unknown' → repository.ts notIndexed() → null na tela. Igual nas duas portas, garantido por teste que compara as declarações normalizadas.

### Consequências e risco

Sem ação: nenhuma regressão (implementado). Risco residual: se uma das cópias mudar sem a outra, o teste de igualdade normalizada deve falhar; se o ClickHouse mudar a semântica de DEFAULT no JOIN, só a prova live percebe. Confiança alta no código, média na prova live (relato).

### Alternativas e recomendação

Reconciliar status da implementação e vincular 31f16ff aos registros de prova live. O Context exige que o acceptor veja RUN_ONE com spark_events e sem run_outcomes retornar -1; não basta mover a spec. O recibo histórico pode satisfazer essa obrigação se aceito com SHA, ambiente e cobertura identificados.

### Dependências e paralelismo

Dependência de escrita com a folha de findings já satisfeita. Prova live depende de ambiente infra autorizado; a reconciliação documental não. Paralelo às demais folhas da #153.

### Plano e aceite propostos

Preparar nota com implementação e recibo de prova live do cenário não indexado. Conferir SHA/ClickHouse/ambiente e negativo registrado em VALIDATION; não reexecutar nesta auditoria. Preservar controles offline de sentinela, ausência de SETTINGS e igualdade das cópias, sem promovê-los a prova da semântica de JOIN no store.

### Comunicação entre responsáveis

Explicar: 'Run não indexado agora mostra nulo nas duas portas desde 31f16ff (#153); o ClickHouse preenche miss de JOIN com default, por isso usamos uma coluna sentinela. A spec só não foi movida para done.'

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Com `SETTINGS join_use_nulls = 1`, a cópia do navegador seria recusada pelo apex_ro readonly=1 e a Console pararia; com ifNull, o zero medido voltaria. Que caso o teste ainda não cobre? — O preenchimento por DEFAULT do próprio ClickHouse, que só um store real mostra, e um run com shapes parcialmente indexados. Como eu explicaria isso para outro pod? — 'Zero e nulo são respostas diferentes: zero diz que medimos nada, nulo diz que não medimos.'

### Próxima ação e encerramento

Ação: reconciliar status e prova obrigatória. Owner a confirmar: Serve+Front/acceptor. Entrada: 31f16ff e registros VALIDATION/#153. Saída: nota distinguindo código concluído e aceitação. Encerramento: cobertura live do cenário vinculada e avaliada; movimento de arquivo isolado não basta.

