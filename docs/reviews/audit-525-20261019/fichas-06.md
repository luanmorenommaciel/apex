# Fichas documentais — lote 6

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-051"></a>

## issue123-tail-outlier-runtime-gate.yaml — issue123-tail-outlier-runtime-gate.yaml

Frente: DEV / prova tail-outlier. Encaminhamento: Preservar plano de prova; manter execução integrada como pendência delimitada.

### Identidade e estado

issue123-tail-outlier-runtime-gate.yaml; TaskPlan histórico aprovado no texto; unidades T-20260920-tail-outlier-runtime-gate; origem https://github.com/luanmorenommaciel/apex/issues/123. Papel responsável DEV / prova tail-outlier, pessoa a confirmar; arquivo na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Fazer o gate canônico exigir a forma de telemetria capaz de sustentar o watcher, em vez de aceitar qualquer linha de stage. Beneficiário: operador que precisa provar um job real de cauda sem usar log antigo.

### Feito, faltante e não comprovado

O plano tem asserção offline e um eval manual do comando público. approved=true não demonstra que o eval manual foi executado, nem que o ambiente pertencia ao executor; é necessária evidência externa à declaração.

### Linhagem

https://github.com/luanmorenommaciel/apex/issues/123 → issue123-tail-outlier-runtime-gate.yaml → T-20260920-tail-outlier-runtime-gate. Inventário relaciona #127 (commit cd5f16bf8c) como antecedente histórico; não equivale a implementação comprovada de cada obrigação. Revisão e recibos por head não foram certificados nesta ficha.

### Fontes e corte

../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_issue123-tail-outlier-runtime-gate.yaml:1; unidades T-20260920-tail-outlier-runtime-gate:L8; blob 34bef3668edc28d52c2c5477d73efcde644c7d5b; https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/issue123-tail-outlier-runtime-gate.yaml. Conferência de integridade: TASKSPECS-106.json; proposta C05:1894.

### Classe e limite da evidência

FATO OBSERVADO: conteúdo preservado e sintaxe; RELATO HISTÓRICO: approved/contexto; PROPOSTA: fluxo e controles; INFERÊNCIA: adequação das fronteiras. Não houve aceite humano novo, execução de teste, CI ou runtime. Presença do manifesto não certifica implementação.

### Fluxo

Workload Spark tail_outlier → ClickHouse canônico → asserção de 100 tasks/amostras, p50>0, max/p50>10 → Engine no-Crew para job recente → verificação do watcher. Prerequisitos ausentes devem recusar antes de operar recursos alheios.

### Consequências e risco

P99 isolado ou stage genérico pode gerar falso aceite do cenário. Reuso de ambiente errado contamina prova. O risco é especificado, não ocorrência atual inferida.

### Alternativas e recomendação

Manter fixture offline para forma/limites e prova live separada permite diagnóstico preciso. Apenas inspeção de script não satisfaz integração. Rodar tudo em CI remoto seria alternativa de infraestrutura, não resultado deste gate local.

### Dependências e paralelismo

Sem depends_on declarado; depende semanticamente de workload, watcher, pacote e plataforma canônica própria. A autorização de runtime e a identidade do ambiente são entradas futuras. Não depende de Kimi/Gemini nem comprova GitHub Actions.

### Plano e aceite propostos

Entrega histórica mínima: canonical_e2e_assert.py, e2e_canonical.sh e teste. eval_1 (unittest) declara B-1/B-2 para positivo e ausência/incompletude/limites; eval_2 (pwsh tail-outlier) declara B-1…B-5, incluindo execução real e proteção de recursos. Rever se cada obrigação possui evidência distinta; um comando sem recibo não basta. Registrar job, stage, SHA, ambiente e resultados negativos antes de aceite integrado.

### Comunicação entre responsáveis

Comunicar diferença entre assertion unitária e execução manual, incluindo dados frescos e recurso próprio. Um passed local não deve ser rotulado CI remoto.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Aceitar só p99 ou qualquer linha de stage como forma de telemetria permitiria falso aceite do cenário, e reusar ambiente alheio contaminaria a prova. Que caso o teste ainda não cobre? — A relação entre o stage qualificado pela asserção e o finding final não é verificada; approved=true não mostra que o eval manual do comando público foi executado, nem em qual ambiente. Como eu explicaria isso para outro pod? — A asserção unitária exige 100 tasks e amostras, p50>0 e max/p50>10; a execução manual com dados frescos e recurso próprio é outra prova, e um passed local não é CI remoto.

### Próxima ação e encerramento

Reconciliar o plano com a evidência disponível da #123 antes de pedir nova execução. Dono DEV/Engine a confirmar; saída verificável futura: matriz de obrigações e recibos por cenário; nesta revisão apenas catalogação.

<a id="item-052"></a>

## issue124-audit-remediation.yaml — issue124-audit-remediation.yaml

Frente: Package / hardening dos testes PowerShell. Encaminhamento: Catalogar plano histórico de teste.

### Identidade e estado

issue124-audit-remediation.yaml; TaskPlan histórico aprovado no texto; unidades T-20260919-pwsh-package-audit-hardening; origem https://github.com/luanmorenommaciel/apex/issues/124. Papel responsável Package / hardening dos testes PowerShell, pessoa a confirmar; arquivo na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Impedir que DryRun de handler errado passe por correspondência de prefixo, e demonstrar que help/ação inválida não criam estado de runtime.

### Feito, faltante e não comprovado

Uma folha somente em tests/test_apex_initial_package.py. O texto exige worktree limpa sem .apex preexistente e proíbe limpar estado alheio para fabricar a precondição.

### Linhagem

https://github.com/luanmorenommaciel/apex/issues/124 → issue124-audit-remediation.yaml → T-20260919-pwsh-package-audit-hardening. Inventário relaciona #128 (commit ca3fa7de3b) como antecedente histórico; não equivale a implementação comprovada de cada obrigação. Revisão e recibos por head não foram certificados nesta ficha.

### Fontes e corte

../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_issue124-audit-remediation.yaml:1; unidades T-20260919-pwsh-package-audit-hardening:L8; blob eebd2c274581d07d7f6e34d2d552e56993cbd7f0; https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/issue124-audit-remediation.yaml. Conferência de integridade: TASKSPECS-106.json; proposta C05:1914.

### Classe e limite da evidência

FATO OBSERVADO: conteúdo preservado e sintaxe; RELATO HISTÓRICO: approved/contexto; PROPOSTA: fluxo e controles; INFERÊNCIA: adequação das fronteiras. Não houve aceite humano novo, execução de teste, CI ou runtime. Presença do manifesto não certifica implementação.

### Fluxo

Ação declarada → dispatcher PowerShell → resumo completo esperado; help/ação inválida → handler seguro ou ValidateSet; DryRun representativo → observação de ausência de .apex. É contrato de teste offline, não prova dos corpos live.

### Consequências e risco

Comparação por substring e auto-relato mutations=0 podem esconder handler incorreto ou escrita real. Risco do controle anterior descrito no plano; sem execução atual.

### Alternativas e recomendação

Igualdade exata da mensagem mais observação do filesystem são controles complementares. Usar só regex ampla é mais frágil; executar runtime para provar despacho amplia custo e fronteira sem necessidade.

### Dependências e paralelismo

Pressupõe contrato de comando e PowerShell disponível; depends_on vazio. Pode ser revisado em paralelo ao Engine, preservando interface do pacote e ambiente temporário próprio.

### Plano e aceite propostos

Plano histórico: fixar resumo de cada ação; executar help e inválida no teste; verificar .apex continua ausente. Menor entrega: arquivo de teste. eval_1 declara B-1…B-3 na suíte focada; eval_2 root. Controles negativos: handler com prefixo semelhante, ação inválida e criação indevida de diretório. Nenhum desses comandos foi executado nesta rodada.

### Comunicação entre responsáveis

Explicar a transição de auto-relato para observação de estado, e que o teste não valida Docker/Spark/ClickHouse. Não anunciar cobertura live de tail-outlier.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Aceitar só o prefixo do handler deixaria passar um DryRun de handler errado com nome parecido, e confiar no auto-relato mutations=0 esconderia escrita real. Que caso o teste ainda não cobre? — O teste pressupõe worktree limpa sem .apex preexistente; com .apex já presente a observação de não mutação perde o sentido, e o plano proíbe limpar estado alheio para fabricar a precondição. Como eu explicaria isso para outro pod? — A folha troca zero relatado por zero observado no filesystem e compara o resumo exato de cada ação; não valida Docker, Spark ou ClickHouse nem cobertura live de tail-outlier.

### Próxima ação e encerramento

Catalogar T-20260919-pwsh-package-audit-hardening, dono Package a confirmar. Saída: escopo e critérios históricos rastreados; nova alteração só com divergência específica.

<a id="item-053"></a>

## issue124-pwsh-command-aware.yaml — issue124-pwsh-command-aware.yaml

Frente: Package / interface e CI PowerShell. Encaminhamento: Catalogar contrato histórico; reconfirmar workflow apenas se houver reuso.

### Identidade e estado

issue124-pwsh-command-aware.yaml; TaskPlan histórico aprovado no texto; unidades T-20260918-pwsh-command-aware-coverage; origem https://github.com/luanmorenommaciel/apex/issues/124. Papel responsável Package / interface e CI PowerShell, pessoa a confirmar; arquivo na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874.

### Intenção e benefício

Fazer DryRun revelar o mesmo handler usado na execução real e tornar a dependência de PowerShell 7 explícita no gate, evitando falsos skips ou cobertura só aparente.

### Feito, faltante e não comprovado

O contexto declara prevenção: gate então existente tinha 64 passed e um skip de macOS; não dizia que CI havia omitido PowerShell. O plano não é diagnóstico do workflow atual e não prova o corpo live de tail-outlier.

### Linhagem

https://github.com/luanmorenommaciel/apex/issues/124 → issue124-pwsh-command-aware.yaml → T-20260918-pwsh-command-aware-coverage. Inventário relaciona #128 (commit a971f8b038) como antecedente histórico; não equivale a implementação comprovada de cada obrigação. Revisão e recibos por head não foram certificados nesta ficha.

### Fontes e corte

../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_issue124-pwsh-command-aware.yaml:1; unidades T-20260918-pwsh-command-aware-coverage:L8; blob 0d9b2bc8a8f1a4f5ebe832062785db3c02cc6efc; https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/issue124-pwsh-command-aware.yaml. Conferência de integridade: TASKSPECS-106.json; proposta C05:1934.

### Classe e limite da evidência

FATO OBSERVADO: conteúdo preservado e sintaxe; RELATO HISTÓRICO: approved/contexto; PROPOSTA: fluxo e controles; INFERÊNCIA: adequação das fronteiras. Não houve aceite humano novo, execução de teste, CI ou runtime. Presença do manifesto não certifica implementação.

### Fluxo

Workflow root → resolve versão pwsh → testes; ação → plano de despacho único → DryRun relata ou execução invoca o mesmo handler. Ausência de pwsh deve falhar como dependência, nunca virar oito skips.

### Consequências e risco

Duas tabelas independentes de dispatch podem divergir; runner sem pwsh pode produzir cobertura falsa se houver skips. Não se infere que isso ocorre hoje.

### Alternativas e recomendação

Resolução compartilhada de ação reduz drift; alternativa de duas tabelas com comparação requer manutenção duplicada. Verificação explícita de versão supera dependência implícita da imagem, mas grep no workflow é só indício da configuração.

### Dependências e paralelismo

Pressupõe PowerShell 7 e interface de ações; depende da imagem efetivamente escolhida, não de Ubuntu 26 obrigatório. Alteração de CI e prova do workflow atual pertencem a sua revisão específica; pode ser independente do detector.

### Plano e aceite propostos

Plano histórico: garantir falha de dependência; centralizar handler; cobrir todas ações sem mutação; explicitar pwsh no root gate. eval_1 declara B-2…B-5 em testes de pacote, eval_2 regressão, eval_3 grep de PowerShell/PSVersionTable/pwsh para B-1. Este último não comprova por si versão mínima nem ordem/fail-closed; conferir lógica e recibo antes de aceite funcional. Tail-outlier DryRun só prova rota.

### Comunicação entre responsáveis

Explicar handler exato, dependência e non-mutation, distinguindo CI histórico, configuração estática e run atual. Não usar o plano para alegar que o runner atual não contém PowerShell.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — O plano pretende tornar o dispatch consciente de Command. O rótulo textual do DryRun não prova a invocação; a integração da #128 deixa esse critério específico pendente. Que caso o teste ainda não cobre? — pwsh presente em versão antiga não tem caso; o eval_3 só procura PowerShell, PSVersionTable e pwsh no workflow, o que não comprova versão mínima nem fail-closed. Como eu explicaria isso para outro pod? — O DryRun relata o mesmo handler que a execução invocaria e a dependência de PowerShell 7 fica explícita no gate; DryRun prova a rota, não o runtime, e o plano não descreve o workflow atual.

### Próxima ação e encerramento

Catalogar T-20260918-pwsh-command-aware-coverage; dono Package/CI a confirmar. Reuso exige confirmar workflow/head e asserções, não repetir plano antigo ou adicionar gate de imagem universal.

<a id="item-054"></a>

## l1-connect.yaml — l1-connect.yaml

Frente: Serve / conexão, distribuição e cliente. Encaminhamento: Catalogar plano histórico amplo; reconciliar antes de qualquer reuso.

### Identidade e estado

l1-connect.yaml; TaskPlan histórico com 23 unidades: T-20260817-serverstatus-model, T-20260817-store-health-query, T-20260817-table-columns-probe, T-20260817-status-assembler, T-20260817-status-degraded-path, T-20260817-register-apex-status, T-20260817-five-tools-assertion, T-20260817-status-store-down-e2e, T-20260817-resolve-settings-extract, T-20260817-name-endpoint-in-error, T-20260817-startup-stderr-banner, T-20260817-surface-defaulted-vars, T-20260817-pypi-metadata, T-20260817-wheel-content-check, T-20260817-testpypi-rehearsal, T-20260817-pypi-publish, T-20260817-drop-from-path, T-20260817-root-mcp-json, T-20260817-cursor-codex-config, T-20260817-gate-status-assert, T-20260817-stdio-gate-five-tools, T-20260817-four-to-five-doc-ripple, T-20260817-graphify-rebuild. Origem docs/lanes/L1_tasks.md; responsável Serve / conexão, distribuição e cliente, pessoa a confirmar. Literal approved=true não é autorização atual nem aceite das folhas.

### Intenção e benefício

Plano de 23 unidades para conexão e diagnóstico de instalação, não apenas ServerStatus. Cobre status tipado/saúde/schema/degradação; configuração e erros sanitizados; empacotamento e publicação; configs de clientes; gates e documentação/grafo.

### Feito, faltante e não comprovado

approved=true é registro; as unidades têm estados próprios. A superfície histórica de cinco tools com apex_status não deve substituir a atual. F-LEITURA-TASKSPECS registra caminhos ausentes e superfície atual de oito tools; presença do plano não prova 23 entregas concluídas pela #79.

### Linhagem

docs/lanes/L1_tasks.md → l1-connect.yaml → unidades nomeadas no campo 1. O inventário associa #79 (commit 3a6b40253c); relação histórica, não implementado_por. Commits/CI/revisões/aceites requerem recibos separados; esta ficha não certifica a implementação de cada folha.

### Fontes e corte

../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_l1-connect.yaml:1; unidades T-20260817-serverstatus-model:L9; T-20260817-store-health-query:L63; T-20260817-table-columns-probe:L111; T-20260817-status-assembler:L158; T-20260817-status-degraded-path:L209; T-20260817-register-apex-status:L259; T-20260817-five-tools-assertion:L306; T-20260817-status-store-down-e2e:L347; T-20260817-resolve-settings-extract:L393; T-20260817-name-endpoint-in-error:L443; T-20260817-startup-stderr-banner:L493; T-20260817-surface-defaulted-vars:L543; T-20260817-pypi-metadata:L593; T-20260817-wheel-content-check:L639; T-20260817-testpypi-rehearsal:L684; T-20260817-pypi-publish:L730; T-20260817-drop-from-path:L774; T-20260817-root-mcp-json:L817; T-20260817-cursor-codex-config:L867; T-20260817-gate-status-assert:L913; T-20260817-stdio-gate-five-tools:L963; T-20260817-four-to-five-doc-ripple:L1012; T-20260817-graphify-rebuild:L1059. Blob 6b641ec3f630f780a9006613af4faae50f82cc80 na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/l1-connect.yaml. Auditoria de declarações: _build/spec-audit.json; correções D e F da Parte04.

### Classe e limite da evidência

FATO OBSERVADO: conteúdo preservado, integridade e carregamento YAML; RELATO HISTÓRICO: approved, motivação e resultados narrados; PROPOSTA: contratos/controles; INFERÊNCIA: adequação documental. Nenhum teste, serviço, publicação ou aceite humano novo.

### Fluxo

Configuração → resolve_settings → ReadStore saúde/colunas → assembler puro → ServerStatus → tool MCP/stdio; build → wheel validado → TestPyPI → PyPI → instalação por cliente; mesmos símbolos → docs/grafo. Credenciais ficam fora do payload e stdout continua JSON-RPC.

### Consequências e risco

Reativar a igualdade histórica de cinco tools ou um wheel contendo só apex_mcp pode excluir capacidades posteriores. Repetir upload por existir uma folha ready é ação externa indevida. Riscos de reuso do plano, não incidentes atuais.

### Alternativas e recomendação

Preservar o manifesto como história e produzir somente folhas novas para lacunas atuais confirmadas. Uma compatibilidade de status distinta pode ser estudada se desejada; reaplicar as 23 unidades em bloco é inadequado. Empacotamento local, publicação e configuração por cliente exigem provas e decisões distintas.

### Dependências e paralelismo

Modelo e saúde iniciam em paralelo; assembler/degradação e probes precedem registro; registro precede igualdade/gates; metadata precede wheel, que precede TestPyPI e PyPI; remoção de --from depende de release e configs. Documentação depende da superfície aprovada. É DAG histórica, não caminho crítico obrigatório de v1.

### Plano e aceite propostos

Catalogar todas as 23 unidades com dependências do YAML. Controles declarados incluem defaults, store vazio/indisponível, sanitização, allowlist, binding, stdout silencioso, wheel/metadata, instalação e configs equivalentes. Conferir sentido de cada comando antes de reuso: cursor-codex-config eval_1 só procura headings, não prova caminhos corretos/restart; testes e greps de publicação não substituem recibos dos índices/clientes. Menor entrega futura é uma lacuna atual por PR, com controle negativo e documentação correspondente.

### Comunicação entre responsáveis

Explicar por grupo o problema resolvido e separar artefatos locais, publicação, configuração real de cliente e runtime de Store. Referenciar #79 como contexto histórico, sem afirmar que integrou todas as unidades.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Voltar à lista histórica de cinco tools com apex_status, ou a um wheel só com apex_mcp, excluiria capacidades posteriores, e repetir o upload por existir uma folha ready seria ação externa indevida. Que caso o teste ainda não cobre? — O eval_1 de cursor-codex-config só procura headings, então um caminho de cliente errado passa; testes e greps de publicação não substituem recibos dos índices e dos clientes. Como eu explicaria isso para outro pod? — São 23 unidades em grupos distintos: status e saúde do store, configuração e erros sanitizados, empacotamento e publicação, configs de cliente e gates; a superfície atual tem oito tools, e #79 é contexto histórico.

### Próxima ação e encerramento

Dono Serve a confirmar: manter 23 IDs ligados ao plano; reuso depende de demanda atual e comparação com superfície/empacotamento atuais. Encerrar a revisão documental ao preservar grupos e limites, sem obrigação de reabrir as folhas.

<a id="item-055"></a>

## l2-discover.yaml — l2-discover.yaml

Frente: Serve / descoberta de runs. Encaminhamento: Catalogar plano histórico inválido como YAML; reuso condicionado.

### Identidade e estado

l2-discover.yaml; TaskPlan histórico com 10 unidades: T-20260819-runs-read-layer, T-20260819-run-summary-models, T-20260819-list-runs-tool, T-20260819-tool-surface-five, T-20260819-runs-injection-hardening, T-20260819-runs-resource, T-20260819-auto-baseline, T-20260819-runs-gates, T-20260819-discover-docs, T-20260819-serve-brief-five-tools. Origem docs/lanes/SERVE-LEGS.md; responsável Serve / descoberta de runs, pessoa a confirmar. Literal approved=true não é autorização atual nem aceite das folhas.

### Intenção e benefício

Dez unidades organizam descoberta de runs: leitura agregada limitada e parametrizada, modelos tipados, list_runs, superfície, proteção contra entrada hostil, recurso apex://runs, baseline automático e provas/documentação.

### Feito, faltante e não comprovado

O texto permanece legível, mas safe_load rejeita linha 53 por : em escalar de comando. A leitura de dez unidades é textual, não um carregamento do manifesto. Não se infere falha do consumidor histórico nem da #83.

### Linhagem

docs/lanes/SERVE-LEGS.md → l2-discover.yaml → unidades nomeadas no campo 1. O inventário associa #83 (commit d244af7985); relação histórica, não implementado_por. Commits/CI/revisões/aceites requerem recibos separados; esta ficha não certifica a implementação de cada folha.

### Fontes e corte

../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_l2-discover.yaml:1; unidades T-20260819-runs-read-layer:L8; T-20260819-run-summary-models:L66; T-20260819-list-runs-tool:L113; T-20260819-tool-surface-five:L164; T-20260819-runs-injection-hardening:L205; T-20260819-runs-resource:L250; T-20260819-auto-baseline:L297; T-20260819-runs-gates:L348; T-20260819-discover-docs:L398; T-20260819-serve-brief-five-tools:L445. Blob 11133cc3d50df0402feebe89ce778f18ccab5fe4 na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/l2-discover.yaml. Auditoria de declarações: _build/spec-audit.json; correções D e F da Parte04.

### Classe e limite da evidência

FATO OBSERVADO: conteúdo preservado, integridade e falha de parsing reproduzida na auditoria; RELATO HISTÓRICO: approved, motivação e resultados narrados; PROPOSTA: contratos/controles; INFERÊNCIA: adequação documental. Nenhum teste, serviço, publicação ou aceite humano novo.

### Fluxo

Filtro app_name/janela/limite → query bound agregada por job_id → RunList → tool/recurso; job atual → busca por mesma app e fingerprint → baseline explícito ou ausência explicada. app_name é dado não confiável, nunca instrução.

### Consequências e risco

Query sem limite ou interpolada pode ampliar leitura; baseline de plano diferente engana comparação. Reutilização do YAML atual falha no parser testado. Não há execução atual demonstrando problema no produto.

### Alternativas e recomendação

Um tool filtrável mais recurso evita multiplicar find_run/latest_run. Baseline automático só dentro da mesma forma de plano; manter baseline explícito é alternativa previsível. Para reuso, corrigir escalar em cópia derivada e validar o consumidor, preservando o original histórico.

### Dependências e paralelismo

Leitura/modelos podem começar paralelos; list_runs depende de ambos; superfície precede recurso, que precede baseline; gates e docs vêm depois. Injeção depende da leitura e pode ser testada paralelamente ao registro.

### Plano e aceite propostos

Plano histórico: dez folhas; manter controles de hostile app_name, limite/ordem, dado não executado, store indisponível, baseline inexistente e explícito. Os comandos estão presentes textualmente. Registro list_runs eval_1 lista tools, mas declara também resposta/filtro: isso não prova B-2/B-3 por si. Antes de eventual dispatch corrigir sintaxe, rever comandos contra comportamentos e selecionar somente lacunas atuais; não executar agora.

### Comunicação entre responsáveis

Informar falha de parsing na linha 53 e distinguir sintaxe do manifesto de qualidade do serviço entregue. Explicar o filtro de baseline e a fronteira entre texto observado e instrução.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Escolher baseline só por app_name compararia runs com planos diferentes; o plano exige mesma app e fingerprint, ou ausência explicada, e trata app_name como dado não confiável. Que caso o teste ainda não cobre? — O eval de registro do list_runs lista a tool, mas declara também resposta e filtro, então um filtro quebrado passa; o YAML falha no safe_load na linha 53, e a leitura das dez unidades é textual. Como eu explicaria isso para outro pod? — O plano é histórico e a falha de parsing é do manifesto, não do serviço entregue pela #83; manifesto aprovado não é prova live, e reuso exige corrigir uma cópia derivada preservando o original.

### Próxima ação e encerramento

Catalogar dez IDs e a associação histórica #83. Dono Serve a confirmar; saída documental: manifesto legível com diagnóstico. Reparar apenas antes de reuso autorizado, sem reabrir entrega integrada por sintaxe.

<a id="item-056"></a>

## l3-understand.yaml — l3-understand.yaml

Frente: Serve / compreensão e cobertura. Encaminhamento: Catalogar plano histórico; aceite formal das folhas permanece separado.

### Identidade e estado

l3-understand.yaml; TaskPlan histórico com 6 unidades: T-20260820-detail-parameter, T-20260820-coverage-freshness, T-20260820-explain-stage-tool, T-20260820-tool-surface-six, T-20260820-critical-path, T-20260820-l3-docs. Origem docs/lanes/SERVE-LEGS.md; responsável Serve / compreensão e cobertura, pessoa a confirmar. Literal approved=true não é autorização atual nem aceite das folhas.

### Intenção e benefício

Seis unidades ampliam analyze_run com detail summary/stages/full, cobertura/frescor, explain_stage, superfície, participação na cauda e documentação. O benefício é revelar escopo observado sem confundir diagnóstico curto com observação completa.

### Feito, faltante e não comprovado

O plano é válido como YAML e approved=true; a auditoria registra as seis folhas em done com accepted=false. Isso exige distinguir estado administrativo de recibo formal, não reimplementar por ausência do campo.

### Linhagem

docs/lanes/SERVE-LEGS.md → l3-understand.yaml → unidades nomeadas no campo 1. O inventário associa #88 (commit dc1c2ceb09); relação histórica, não implementado_por. Commits/CI/revisões/aceites requerem recibos separados; esta ficha não certifica a implementação de cada folha.

### Fontes e corte

../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_l3-understand.yaml:1; unidades T-20260820-detail-parameter:L8; T-20260820-coverage-freshness:L59; T-20260820-explain-stage-tool:L105; T-20260820-tool-surface-six:L151; T-20260820-critical-path:L192; T-20260820-l3-docs:L242. Blob c3a390318bbeae32b48632250fdf482abac16514 na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/l3-understand.yaml. Auditoria de declarações: _build/spec-audit.json; correções D e F da Parte04.

### Classe e limite da evidência

FATO OBSERVADO: conteúdo preservado, integridade e carregamento YAML; RELATO HISTÓRICO: approved, motivação e resultados narrados; PROPOSTA: contratos/controles; INFERÊNCIA: adequação documental. Nenhum teste, serviço, publicação ou aceite humano novo.

### Fluxo

Análise única → projeção summary/stages/full com mesmo veredito; eventos → contagens e idade numérica; stage selecionado → métricas/findings próprios ou não observado; durações → participação na cauda, sem afirmar caminho crítico de scheduling.

### Consequências e risco

Reanalisar por nível pode mudar veredito; omitir cobertura transmite certeza falsa; chamar tail share de critical path infere dependências inexistentes. São riscos do contrato, sem regressão atual comprovada.

### Alternativas e recomendação

Projeção pós-análise preserva consistência. Alternativa de payload full em todas chamadas simplifica contrato mas aumenta volume; análise por nível diverge. Tail share informativo é preferível a causalidade de scheduling não suportada.

### Dependências e paralelismo

detail precede coverage e explain_stage; surface depende de explain_stage; critical-path depende de coverage; docs dependem de surface/critical-path. Essa ordem interna não impõe bloqueio entre marcos atuais.

### Plano e aceite propostos

Plano histórico por seis folhas: paridade de veredito nos níveis, stage ausente explícito, idade sem julgamento stale, cobertura fina visível, cauda dominante/igual e descrição honesta. Os evals associam esses controles a testes/greps; sua força e recibos não foram certificados aqui. Se aceite formal for necessário, buscar recibos das seis folhas na ref pertinente; não preencher accepted retrospectivamente.

### Comunicação entre responsáveis

Explicar que full conserva contrato histórico enquanto summary corta arrays; idade é dado e tail share não é scheduler. Expor done/accepted=false como estado documental delimitado.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Recalcular a análise por nível de detalhe poderia mudar o veredito entre summary, stages e full; o plano projeta uma análise única depois de calculada. Que caso o teste ainda não cobre? — Um stage nunca observado deve aparecer como não observado, e a cobertura fina deve ficar visível; a força dos testes e greps associados e os recibos das seis folhas não foram certificados. Como eu explicaria isso para outro pod? — A participação na cauda é informativa e não é caminho crítico de scheduling; as seis folhas estão done com accepted=false, estado documental que não pede reimplementação.

### Próxima ação e encerramento

Catalogar seis unidades e relação histórica #88. Dono Serve a confirmar; saída: contratos e diferença de aceite rastreáveis. Só buscar aceite faltante quando necessário ao uso, sem reabrir por convenção de status.

<a id="item-057"></a>

## l5-fix.yaml — l5-fix.yaml

Frente: Serve / superfície de verificação. Encaminhamento: Catalogar plano histórico; corrigir interpretação da prova declarada.

### Identidade e estado

l5-fix.yaml; TaskPlan histórico com 6 unidades: T-20260820-verifications-read-layer, T-20260820-verification-models, T-20260820-verify-fix-tool, T-20260820-l5-tool-surface, T-20260820-suggest-fix-provenance, T-20260820-l5-docs. Origem docs/lanes/SERVE-LEGS.md; responsável Serve / superfície de verificação, pessoa a confirmar. Literal approved=true não é autorização atual nem aceite das folhas.

### Intenção e benefício

Seis folhas expõem resultados da lane Verify no MCP e nas sugestões, sem reimplementar o cálculo nem aplicar mudanças. A ausência de avaliação e uma recusa de segurança devem ser visíveis ao usuário.

### Feito, faltante e não comprovado

O plano lê fix_verifications, define modelos, registra verify_fix, atualiza superfície, carrega proveniência em suggest_fix e documenta. Não cria produtor da tabela; essa decisão pertence à #117. Os comandos da folha verify-fix-tool não sustentam todos os verifies declarados.

### Linhagem

docs/lanes/SERVE-LEGS.md → l5-fix.yaml → unidades nomeadas no campo 1. O inventário associa #87 (commit a8087ce524); relação histórica, não implementado_por. Commits/CI/revisões/aceites requerem recibos separados; esta ficha não certifica a implementação de cada folha.

### Fontes e corte

../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_l5-fix.yaml:1; unidades T-20260820-verifications-read-layer:L8; T-20260820-verification-models:L65; T-20260820-verify-fix-tool:L111; T-20260820-l5-tool-surface:L162; T-20260820-suggest-fix-provenance:L203; T-20260820-l5-docs:L253. Blob 811f3c9c67d64e7a1a3853b194a55077697d7be9 na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/l5-fix.yaml. Auditoria de declarações: _build/spec-audit.json; correções D e F da Parte04.

### Classe e limite da evidência

FATO OBSERVADO: conteúdo preservado, integridade e carregamento YAML; RELATO HISTÓRICO: approved, motivação e resultados narrados; PROPOSTA: contratos/controles; INFERÊNCIA: adequação documental. Nenhum teste, serviço, publicação ou aceite humano novo.

### Fluxo

job/finding → leitura bound de fix_verifications → VerificationView/FixVerdict → verify_fix e suggest_fix → previsão/medição, segurança e ressalvas; tabela ausente degrada; applied=false e aprovação humana permanecem explícitos.

### Consequências e risco

Tratar ausência como avaliação concluída ou ocultar recusa atrás de confiança baixa pode induzir aplicação sem base. Texto de docstring não testa esses resultados. Não se conclui ausência de outros testes no repositório.

### Alternativas e recomendação

Manter camada de leitura sobre Verify evita duplicação de regras. Alternativa de calcular dentro de Serve acopla lanes e deve ser decisão nova. Não criar sink por consequência de haver leitor; escritor externo/documentado ou ausência aceita são opções da #117.

### Dependências e paralelismo

Leitura e modelos podem ser paralelos; tool depende de ambos; superfície e proveniência dependem do tool; docs dependem desses dois. Sem dependência técnica demonstrada em #162 (versão).

### Plano e aceite propostos

Controles declarados: ordenação newest-first/binding, ausência de tabela, valor previsto sem medição, convenção de sinal, ausência de verificação, bloqueio, preservação de nunca aplicar. Achado específico: verify-fix-tool eval_1 apenas lista/annotation e declara B-2 de payload; eval_2 apenas procura ausência de Five tools e declara B-3/B-4 de ausência/recusa. Esses comandos não demonstram tais contratos. Buscar testes/recibos pertinentes antes de aceite; menor correção futura seria alinhar evidência ou controles, se ainda necessária.

### Comunicação entre responsáveis

Comunicar integração por leitura, sem afirmar escritor existente ou verificação executada. Registrar a incompatibilidade entre verifies e comando, sem acusar defeito da função atual.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Confundir uma superfície de leitura com um escritor criaria falsa comprovação do fluxo. Serve expõe verificações por leitura; qualquer persistência de resultados calculados por Verify precisa de uma rota identificada. Que caso o teste ainda não cobre? — Os comandos da folha verify-fix-tool não demonstram B-2 a B-4: um só lista tool e annotation, outro só procura ausência de Five tools; uma tool que exista mas esconda a recusa passaria por eles. Como eu explicaria isso para outro pod? — O Serve expõe por leitura o que o Verify calcula e persiste em fix_verifications, sem reimplementar o cálculo nem criar o escritor da tabela, cuja decisão pertence à #117.

### Próxima ação e encerramento

Catalogar seis IDs e contexto #87; dono Serve a confirmar. Encerrar revisão documental com lacuna de prova declarada nomeada; eventual aceite funcional depende de fonte específica, não contagem B/eval.

<a id="item-058"></a>

## l6-learn.yaml — l6-learn.yaml

Frente: Serve / memória entre runs. Encaminhamento: Catalogar plano histórico; limitar prova dos evals.

### Identidade e estado

l6-learn.yaml; TaskPlan histórico com 6 unidades: T-20260820-plan-memory-read-layer, T-20260820-recall-models, T-20260820-recall-runs-tool, T-20260820-l6-tool-surface, T-20260820-noise-floor-honesty, T-20260820-l6-docs. Origem docs/lanes/SERVE-LEGS.md; responsável Serve / memória entre runs, pessoa a confirmar. Literal approved=true não é autorização atual nem aceite das folhas.

### Intenção e benefício

Seis folhas expõem semelhança de planos e resultados anteriores com proveniência da configuração. A linguagem só chama uma configuração melhor quando há piso de ruído medido e a diferença o supera.

### Feito, faltante e não comprovado

O plano lê plan_memory/run_outcomes, define modelos, registra recall_similar_runs, atualiza superfície, impõe honestidade do piso e documenta. Isso não prova semelhança útil em operação nem criação das tabelas pela lane Serve.

### Linhagem

docs/lanes/SERVE-LEGS.md → l6-learn.yaml → unidades nomeadas no campo 1. O inventário associa #86 (commit 5485202420); relação histórica, não implementado_por. Commits/CI/revisões/aceites requerem recibos separados; esta ficha não certifica a implementação de cada folha.

### Fontes e corte

../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_l6-learn.yaml:1; unidades T-20260820-plan-memory-read-layer:L8; T-20260820-recall-models:L65; T-20260820-recall-runs-tool:L115; T-20260820-l6-tool-surface:L165; T-20260820-noise-floor-honesty:L206; T-20260820-l6-docs:L256. Blob 75121e30c891b83e83447aa3af64c2bda4084a02 na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/l6-learn.yaml. Auditoria de declarações: _build/spec-audit.json; correções D e F da Parte04.

### Classe e limite da evidência

FATO OBSERVADO: conteúdo preservado, integridade e carregamento YAML; RELATO HISTÓRICO: approved, motivação e resultados narrados; PROPOSTA: contratos/controles; INFERÊNCIA: adequação documental. Nenhum teste, serviço, publicação ou aceite humano novo.

### Fluxo

job → fingerprint → similar_plans por cosseno/limiar → prior_outcomes → modelos com config_source e app_name não confiável → recall → medições e comparação condicionada ao piso. Forma inédita e tabelas ausentes têm explicação própria.

### Consequências e risco

Configuração unknown apresentada como observada e um único run tratado como dispersão produzem conselho excessivo. O plano evita esses casos; prova atual de qualidade da recomendação não foi medida.

### Alternativas e recomendação

Expor memória como leitura preserva fronteiras. Alternativa de retornar sempre vizinho mais próximo inventa relevância sem limiar; só listar medições é opção honesta sem piso. Algoritmo de recomendação novo exige decisão separada.

### Dependências e paralelismo

Leitura/modelos paralelos; tool depende de ambos; surface e floor-honesty dependem da tool; docs dependem de ambos. Definições de piso e atribuição em #117 não podem ser assumidas como cumpridas pelo manifesto.

### Plano e aceite propostos

Controles previstos: binding hostil, falta de tabelas/forma, score/config_source, ausência de piso, diferença dentro/acima do piso e uma única execução. Achado específico: recall-runs-tool eval_1 lista tool/annotation, não prova payload B-2; eval_2 só rejeita texto Five tools, apesar de declarar B-3/B-4 sobre forma inédita/memória indisponível. Verificar testes efetivos antes de aceite, preservando a distinção entre descrição e asserção.

### Comunicação entre responsáveis

Comunicar que sem piso se descrevem medições e que config_source pode ser unknown. Não transformar similaridade em causalidade ou falta de mapping de prova em ausência universal de testes.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Devolver sempre o vizinho mais próximo inventaria relevância sem limiar, e apresentar config_source unknown como observado produziria conselho excessivo. Que caso o teste ainda não cobre? — O eval_1 do recall-runs-tool só lista a tool e o eval_2 só rejeita o texto Five tools, então memória ausente virando sucesso vazio passaria; a qualidade da recomendação não foi medida. Como eu explicaria isso para outro pod? — A memória é exposta por leitura: sem piso de ruído medido descrevem-se as medições, e só se diz que uma configuração é melhor quando a diferença supera o piso; similaridade não prova ganho causal.

### Próxima ação e encerramento

Catalogar seis IDs e contexto #86; dono Serve/Memory a confirmar. Saída agora: contratos e limite dos evals; follow-up apenas se prova necessária não estiver em outra fonte.

<a id="item-059"></a>

## serve-api-e2e.yaml — serve-api-e2e.yaml

Frente: Console / prova integrada e DEV. Encaminhamento: Catalogar plano histórico com sintaxe inválida e alegações de prova limitadas.

### Identidade e estado

serve-api-e2e.yaml; TaskPlan histórico com 3 unidades: T-20261006-console-e2e-reflection, T-20261006-six-lane-gate-full-detail, T-20261006-dev-c3-driver-host. Origem tests/e2e/console_reflection.sh; responsável Console / prova integrada e DEV, pessoa a confirmar. Literal approved=true não é autorização atual nem aceite das folhas.

### Intenção e benefício

Três folhas registram reflexão do job no App real, pedido detail=full no gate de seis lanes e configuração de driver para C3/C4. Não são três implementações equivalentes à prova completa de browser/nginx.

### Feito, faltante e não comprovado

O YAML é rejeitado na linha 101. O contexto relata verdes de 06/10 para jobs específicos, mas recibos não foram reinspecionados aqui. A Console é montada em teste com MemoryRouter/fetch real; isso não certifica imagem nginx nem navegação em browser real.

### Linhagem

tests/e2e/console_reflection.sh → serve-api-e2e.yaml → unidades nomeadas no campo 1. O inventário associa #153 (commit eb449cbec5); relação histórica, não implementado_por. Commits/CI/revisões/aceites requerem recibos separados; esta ficha não certifica a implementação de cada folha.

### Fontes e corte

../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_serve-api-e2e.yaml:1; unidades T-20261006-console-e2e-reflection:L12; T-20261006-six-lane-gate-full-detail:L70; T-20261006-dev-c3-driver-host:L110. Blob 4f25d46b1d4b0e8eace218c76cf780d2a389b42a na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/serve-api-e2e.yaml. Auditoria de declarações: _build/spec-audit.json; correções D e F da Parte04.

### Classe e limite da evidência

FATO OBSERVADO: conteúdo preservado, integridade e falha de parsing reproduzida na auditoria; RELATO HISTÓRICO: approved, motivação e resultados narrados; PROPOSTA: contratos/controles; INFERÊNCIA: adequação documental. Nenhum teste, serviço, publicação ou aceite humano novo.

### Fluxo

Job no Store → Engine/Memory → API → paridade das linhas → App montado; probe MCP pede detail=full para comparar counts; submit C3/C4 recebe driver.host e bindAddress. Sem variáveis live, teste fica skipped, nunca passed.

### Consequências e risco

Comparar summary com arrays full pode acusar contagens falsas; executar driver com hostname inadequado pode falhar. Cleanup por porta descrito no contexto não demonstra propriedade do processo, logo não deve ser reutilizado sem identificação.

### Alternativas e recomendação

Preservar evidências históricas e usar escopo mínimo para lacunas. App montado é controle útil de renderização, mas browser/container é prova complementar em #172. Fazer todos cenários indiscriminadamente aumenta custo; pular e chamar verde oculta limite.

### Dependências e paralelismo

parent_plan serve-api-wire; as três folhas têm depends_on vazio, embora reflexão requeira Store/API/gates e contrato de dados. Podem ser analisadas separadamente. Runtime futuro depende de autorização/ambiente próprio e dados adequados.

### Plano e aceite propostos

Plano histórico: reflection deve reportar etapa e falhar em NaN/undefined/[object Object]/avisos indevidos, comparar contagens e avisar job_conf ausente; probe deve enviar full; submits devem ter duas confs. Controles incluem pytest offline do argumento, teste live e renderização make -n. Corrigir parsing antes de reuso; não executar comandos com .env/docker. Um grep de passed não substitui recibo íntegro e delimitado.

### Comunicação entre responsáveis

Apresentar os relatos de 06/10 como históricos com IDs/ambiente a localizar. Distinguir App montado, API real, nginx e browser, e incluir skipped/NOT EXERCISED.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Contar summary como full no probe do gate acusaria contagens falsas, e reaproveitar o cleanup por porta descrito no contexto sem identificar o processo poderia afetar recurso alheio. Que caso o teste ainda não cobre? — A Console montada com MemoryRouter e fetch real não cobre o container nginx nem a navegação em browser real, que ficam com a #172; sem variáveis live o teste fica skipped, não passed, e o YAML falha na linha 101. Como eu explicaria isso para outro pod? — São três folhas distintas: reflexão do job no App, pedido detail=full no gate de seis lanes e driver.host para C3/C4; os verdes de 06/10 são relatos de jobs específicos e não se transferem a outros jobs ou heads.

### Próxima ação e encerramento

Catalogar três unidades e relação #153. Dono Serve/Front/DEV a confirmar; fonte de prova adicional #156/#172. Encerrar documentalmente com diagnóstico YAML e fronteiras, sem exigir rerun de tudo.

<a id="item-060"></a>

## serve-api-sweep.yaml — serve-api-sweep.yaml

Frente: Serve / paridade da Console. Encaminhamento: Catalogar sweep histórico; não reexecutar unidade substituída.

### Identidade e estado

serve-api-sweep.yaml; TaskPlan histórico com 6 unidades: T-20260923-console-findings-transitions-projection, T-20260923-run-rollup-unindexed-sentinel, T-20260923-console-auto-prefers-api, T-20260923-navbar-source-badge, T-20260923-screens-surface-query-failures, T-20260923-console-http-deployment-wiring. Origem tasks/.plans/serve-api.yaml; responsável Serve / paridade da Console, pessoa a confirmar. Literal approved=true não é autorização atual nem aceite das folhas.

### Intenção e benefício

Seis folhas corrigem projeções de findings/transitions, ausência de indexação, seleção automática da API, rótulo da fonte, erros nas telas e configuração HTTP de deployment. A decisão Ask/LLM fica separada.

### Feito, faltante e não comprovado

O manifesto define decisão aberta Ask consumer, explicitamente não bloqueante para estas seis folhas. A unidade auto-prefers-api foi depois substituída: spec parked e código atual adotam semântica de 401 diferente; D-CORRECOES-E-LIMITES C04-05 documenta a correção.

### Linhagem

tasks/.plans/serve-api.yaml → serve-api-sweep.yaml → unidades nomeadas no campo 1. O inventário associa #153 (commit 9841119362); relação histórica, não implementado_por. Commits/CI/revisões/aceites requerem recibos separados; esta ficha não certifica a implementação de cada folha.

### Fontes e corte

../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/taskspecs/tasks_.plans_serve-api-sweep.yaml:1; unidades T-20260923-console-findings-transitions-projection:L45; T-20260923-run-rollup-unindexed-sentinel:L114; T-20260923-console-auto-prefers-api:L179; T-20260923-navbar-source-badge:L242; T-20260923-screens-surface-query-failures:L288; T-20260923-console-http-deployment-wiring:L351. Blob 6f2f22f1e23ec9030d710fc90bb0e3d2f8e3406e na main c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874; https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tasks/.plans/serve-api-sweep.yaml. Auditoria de declarações: _build/spec-audit.json; correções D e F da Parte04.

### Classe e limite da evidência

FATO OBSERVADO: conteúdo preservado, integridade e carregamento YAML; RELATO HISTÓRICO: approved, motivação e resultados narrados; PROPOSTA: contratos/controles; INFERÊNCIA: adequação documental. Nenhum teste, serviço, publicação ou aceite humano novo.

### Fluxo

Queries Console → projeções API equivalentes e rollup indexed → Repository → telas com fonte/erro explícitos; config Compose/Make → proxy same-origin. Auto antigo dizia só 200 e fallback em 401, portanto é história, não contrato atual.

### Consequências e risco

Fake retornando qualquer projeção pode esconder campo SQL ausente; LEFT JOIN pode produzir zero não medido; erro engolido parece vazio. Reaplicar fallback antigo em 401 reverteria decisão posterior.

### Alternativas e recomendação

Preservar adapters e testar projeção real evita reescrever telas. Sentinela indexed atende readonly=1 sem SETTINGS join_use_nulls. Para auto, manter comportamento vigente documentado; nova política exige motivação própria. Ask pode ser estruturado ou mediado por modelo, sem bloquear o sweep.

### Dependências e paralelismo

run-rollup depende de findings-transitions por ordem de escrita nos mesmos arquivos, explicitamente não por resultado. Demais folhas podem ser paralelas com coordenação de arquivos. Ask é decisão de produto independente; #171/#122 não bloqueiam catalogar a spec substituída.

### Plano e aceite propostos

Plano histórico: comparar campos/aliases, ordenar confidence_score, reduzir transição por max(update_seq), sentinel -1/unknown, labels exaustivos, falha antes de vazio com sanitização, Compose renderizado e comando prod. Controles negativos removem alias, mudam estado/indexação e injetam erro com segredo fictício. Grep de docs e typecheck não equivalem a execução HTTP. Reuso exclui auto antigo e exige reconciliar cada contrato com a main.

### Comunicação entre responsáveis

Explicar separadamente as seis superfícies e a dependência apenas de escrita. Citar substituição de auto e decisão Ask sem apresentar uma como bloqueio da outra.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? — Usar join_use_nulls sob readonly=1 não é possível na consulta; o plano adota o sentinela indexed, e reaplicar o fallback antigo em 401 da folha auto-prefers-api reverteria a decisão posterior. Que caso o teste ainda não cobre? — Um fake que fornece coluna que a SQL não projeta esconde campo ausente; grep de docs e typecheck não equivalem a execução HTTP, e cada contrato precisa ser reconciliado com a main antes de reuso. Como eu explicaria isso para outro pod? — São seis superfícies com dependência só de escrita nos mesmos arquivos; erro, vazio e não indexado são estados distintos na tela, e a decisão Ask/LLM não bloqueia o sweep.

### Próxima ação e encerramento

Catalogar seis unidades; dono Serve/Front a confirmar. Usar recibo de P-S01 already_corrected para não republicar o bug antigo e manter auto como substituída; pendências atuais só por evidência própria.

