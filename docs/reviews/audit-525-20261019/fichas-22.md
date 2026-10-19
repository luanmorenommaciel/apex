# Fichas documentais — lote 22

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-211"></a>

## E08 — Preservar dev/.env do operador (T33)

Frente: pacote_configuracao_runner. Encaminhamento: agrupar_em_174_revisar_candidato_conjunto.

### Identidade e estado

E08 é o desenho/PR do Pod 2/Package para preservar dev/.env do operador (seed E08, R2 T33), publicado da minuta P-E08 como issue luanmorenommaciel/apex#174 em 2026-10-11 por gustocezar, aberta, assignee gustocezar (reserva de estudo e candidato local de 11/10), com um comentário de várias rodadas. Owner da decisão de contenção: dono do pacote (a confirmar).

### Intenção e benefício

Problema: Sync-DevEnvForCanonicalScript copia .apex/dev.env sobre dev/.env com Copy-Item -Force, sem comparar nem fazer backup; e2e e tail-outlier chamam a função. Público: operadores que mantêm dev/.env próprio num checkout compartilhado. Ganho: a configuração do operador nunca é substituída silenciosamente.

### Feito, faltante e não comprovado

Base: Copy-Item -Force em Sync-DevEnvForCanonicalScript:616, chamado por Invoke-ProductGate:624 e Invoke-TailOutlierGate:681. Relato público: candidato conjunto #167/#174 encaminha EnvFile, 59+26 testes históricos e prova integral e2e em macOS com stubs e endpoint HTTP sintético em loopback (base 7/3, candidato 10/0, controle 8/2). Não é zero rede nem prova de smoke/tail-outlier, Windows ou Compose real. Escolha de binding e bytes continua aberta.

### Linhagem

Linhagem: revisão §3 da #127 e R2 T33 → desenho NA-08 e Task-Spec T-20260924-na08 (registro) → minuta P-E08 → #174 → candidato local conjunto (patch 1122d031…, binding false) → 59+26 testes e prova integral sob stubs (relato) → revisão Gemini estática e fixtures Windows propostas (15 itens não executados; W07 só cobre helper) → decisão de contrato [ausente] → PR [ausente]. A MATRIX diz "Decidir a contenção em DEC-10"; no DECISION-REGISTER, DEC-10 é o guarda-chuva "Contenção operacional da #127 (dev/.env, ownership, Windows, cold start)" e cobre E08, E09, E10, E14 e L09. A parte dev/.env pode ser decidida sem esperar a parte de ownership (E09): como a ficha Codex #174 e C04-15, não vejo dependência técnica entre elas.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-revalidated-fes-sources/scripts__apex.ps1.sanitized.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/dev__scripts__e2e_canonical.ps1.txt; D-CORRECOES-E-LIMITES.md. Locadores e recorte: E08/#174 comentário 6109648325 integral e #167; wrapper:609–656,677–687; runner:1–20; distinções C04-24/25. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: cópia destrutiva e seus dois chamadores na base. RELATO: candidato e provas locais com stubs, sem Docker/Spark reais. INFERÊNCIA: passar EnvFile ao runner elimina a necessidade da cópia, desde que o runner declare o parâmetro (#167). PROPOSTA: fixtures Windows. DECISÃO PENDENTE: contrato de entrada (DEC-N5: binding false do candidato 1122d031 versus binding padrão do PATCH-167.diff) e publicação (DEC-15).

### Fluxo

Fluxo observado: wrapper apex.ps1 —(Copy-Item -Force)→ dev/.env —(lido por)→ e2e_canonical.ps1 —(credencial MinIO gerada)→ asserts. Fluxo do candidato: wrapper —(-EnvFile .apex/dev.env)→ runner —(--env-file)→ Compose; dev/.env —(não tocado)→ operador.

### Consequências e risco

Sem correção, um dev/.env divergente é sobrescrito a cada gate; o operador perde configuração e o próximo comando pode apontar para a stack errada. É risco possível com caminho de escrita confirmado; não houve reprodução com .env real nesta revisão. Confiança alta no caminho.

### Alternativas e recomendação

Recomendado: revisar o candidato conjunto após escolher a variante de binding, mantendo a passagem direta de EnvFile. Alternativas: recusar destino divergente (preserva dados, mantém dois caminhos de configuração); backup consentido (mais complexo e cria cópias de segredo); separar #174 de #167 em duas PRs com ordem explícita. Não reimplementar do zero ignorando o candidato.

### Dependências e paralelismo

Dependência técnica: o runner ON precisa declarar EnvFile (#167, E16); por isso as duas correções andam juntas. Não depende de #175/E09 nem de DEC-10 para a prova offline. Windows e Compose são camadas de prova posteriores e independentes entre si.

### Plano e aceite propostos

Passos mínimos: (1) decidir DEC-N5 (binding); (2) fixar o patch escolhido por hash; (3) testes: destino ausente, idêntico, divergente, somente leitura, fonte ausente; (4) controle contra a base que reproduz a sobrescrita; (5) caso integral para smoke e tail-outlier, não só e2e; (6) prova Windows nativa e Compose real separadas, com campos sanitizados. Aceite: dev/.env byte a byte igual após cada gate.

### Comunicação entre responsáveis

Para outro pod: "O pacote hoje copia por cima do dev/.env. O candidato local passa a configuração por parâmetro e não toca o arquivo, mas existem duas variantes de interface e a prova completa cobriu só e2e em macOS com stubs."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Declarar EnvFile no runner sem remover Copy-Item do wrapper manteria a sobrescrita; testar só o helper não observaria o dispatcher inteiro. Que caso o teste ainda não cobre? A prova integral relatada cobre e2e em macOS com stubs; smoke, tail-outlier, Windows nativo e Compose real têm recortes próprios. Como eu explicaria isso para outro pod? O candidato passa configuração diretamente para preservar dev/.env; é preciso escolher a variante e conservar a linhagem exata de cada prova.

### Próxima ação e encerramento

Próxima ação: dono do pacote e mantenedor (a confirmar) escolhem DEC-N5 e o patch. Entrada: candidato 1122d031… e PATCH-167.diff com seus recibos. Saída: PR pequena com testes de preservação. Encerramento: PR integrada e critérios da #174 marcados com evidência por entrypoint e plataforma.

<a id="item-212"></a>

## E09 — Identidade de checkout/daemon/Compose (T34a)

Frente: pacote_identidade_stacks. Encaminhamento: decidir_modelo_identidade_em_175.

### Identidade e estado

E09 é o desenho do Pod 2/Package para identidade de checkout, daemon e projeto Compose (seed E09, R2 T34a), publicado da minuta P-E09 como issue luanmorenommaciel/apex#175 em 2026-10-11 por gustocezar, aberta, assignee gustocezar (reserva de estudo), um comentário com duas rodadas de estudo. Decisão: dono do pacote/mantenedor (DEC-10), a confirmar.

### Intenção e benefício

Problema: dev/docker-compose.yml usa name: apex-dev e infra/docker-compose.yml usa name: apex-infra com container_name fixos (apex-infra-clickhouse, apex-infra-mongodb, apex-infra-hyperdx, apex-infra-otel-collector); nada verifica se a stack encontrada pertence a este checkout. Público: quem roda mais de um checkout ou perfil no mesmo daemon (incidente de colisão Colima relatado em C38). Ganho: preflights que distinguem stack própria de alheia antes de qualquer mutação.

### Feito, faltante e não comprovado

Base: nomes fixos confirmados (dev:5, infra:34-130). Feito (relato): inventário de sete Compose, matriz de 12 operações e duas opções de isolamento — parametrizar identidades e portas no daemon compartilhado, ou daemons/VMs distintos com fronteira de rede verificada, porque daemons diferentes com as mesmas portas do host não isolam. Falta: escolha do modelo, compatibilidade de stacks antigas e plano de teste de recusa. Não comprovado: nenhuma identidade real de daemon/container foi medida.

### Linhagem

Linhagem: C38 I3 (colisão Colima), HARN-CTX/HARN-NS (ADR de lacunas de 18/08) e R2 T34a → desenho NA-09 e Task-Spec T-20260925-e09 (registro, dois evals verdes) → minuta P-E09 → #175 → duas rodadas Gemini de 11/10 revistas pelo Codex → decisão DEC-10 [ausente] → guard E10 [ausente] → preflight de porta E11 [ausente]. Antecedente público: guard de recursos preexistentes da #64.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/dev__docker-compose.yml.txt; fontes/batch-revalidated-fes-sources/infra__docker-compose.yml.sanitized.txt. Locadores e recorte: E09/#175 corpo/comentário integral; dev Compose:5 e infra nomes/portas na base. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: nomes fixos na base. RELATO: inventário e matriz de 11/10; dois evals verdes do desenho NA-09. PROPOSTA: duas opções de isolamento. DECISÃO PENDENTE: modelo de identidade (labels, nonce/manifesto, caminho canônico ou combinação) e migração de stacks antigas. Nenhuma execução.

### Fluxo

Fluxo proposto: identidade do checkout e identidade observada do daemon/projeto/recursos → preflight → match demonstrado ou recusa sem mutação. O recorte estático mostra nomes fixos; não inspeciona daemon nem prova que toda operação atual ignora qualquer outra defesa.

### Consequências e risco

Sem decisão, um comando pode encontrar os nomes esperados e operar a stack de outro checkout, e uma validação pode observar o ambiente errado. É risco possível, com antecedente relatado (C38), sem incidente atual observado. Confiança alta nos fatos estáticos.

### Alternativas e recomendação

Recomendado: decidir a identidade por labels de projeto mais um nonce/manifesto do checkout, com recusa fail-closed quando ausente, e só então desenhar o guard. Alternativas: caminho canônico do checkout (frágil com symlinks e iCloud, ver X17); daemons separados (exige fronteira de rede/VM e muda o pacote); manter nomes fixos e documentar um checkout por daemon (simples, transfere o risco ao operador).

### Dependências e paralelismo

A decisão é humana e não depende de código. Inventário e desenho podem correr em paralelo a #167/#174/#178; testes offline de argv/arquivo/endpoint não precisam desta política (C04-15). E10 depende desta decisão; E11 pode estudar a recusa de porta em paralelo, mas a classificação "foreign" usa a identidade escolhida.

### Plano e aceite propostos

Passos mínimos: (1) consolidar a matriz de 12 operações em leitura/mutação; (2) escolher modelo e regra para stacks antigas (adotar com confirmação explícita ou recusar); (3) cenários de teste: dois checkouts, contextos para o mesmo daemon, porta ocupada, identidade ausente e divergente; (4) decisão registrada. Aceite: política escrita com fail-closed.

### Comunicação entre responsáveis

Para outro pod: "Hoje o pacote reconhece uma stack só pelo nome. Precisamos decidir como provar que a stack é deste checkout antes de mexer nela; daemons diferentes não isolam se as portas do host são as mesmas."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Confundir nome esperado com propriedade do checkout pode permitir observar ou mutar uma stack alheia; Docker contexts distintos ainda podem apontar ao mesmo daemon. Que caso o teste ainda não cobre? Os dois evals e a matriz são relatos de desenho; faltam cenário de dois checkouts, identidade ausente/divergente e compatibilidade com stacks antigas. Como eu explicaria isso para outro pod? A #175 escolhe o protocolo de identidade antes do guard de mutações; nomes, portas e fronteira de daemon/VM são dimensões distintas.

### Próxima ação e encerramento

Próxima ação: dono do pacote/mantenedor (a confirmar) escolhe o modelo. Entrada: inventário de 12 operações e duas opções. Saída: decisão DEC-10 registrada na #175. Encerramento: decisão com regra de compatibilidade e plano de teste do guard.

<a id="item-213"></a>

## E10 — Guard de ownership antes de mutações Docker (T34b)

Frente: pacote_identidade_stacks. Encaminhamento: agrupar_em_175_executar_apos_decisao_e09.

### Identidade e estado

E10 é um PR futuro do Pod 2/Package: guard de ownership antes de mutações Docker (seed E10, R2 T34b). Não tem issue própria; a triagem marcou needs_revalidation e a v2 o agrupou na #175 (critério "Plano de teste que recusa recurso alheio sem limpar, recriar ou adotar silenciosamente"). Owner a confirmar.

### Intenção e benefício

Problema: sem guard, gates do pacote podem submeter Spark, recriar containers ou limpar volumes de uma stack de outro checkout que tenha os mesmos nomes. Público: quem compartilha daemon entre checkouts. Ganho: zero mutação em stack alheia.

### Feito, faltante e não comprovado

O registro não demonstra entrega específica de E10; #175 trata o guard como implementação posterior à decisão de identidade. No recorte do wrapper lido não se demonstra um protocolo completo de propriedade por checkout; isso não é busca exaustiva por toda defesa do repositório. Faltam modelo decidido, folha e provas do guard.

### Linhagem

Linhagem: R2 T34b → registro E10 (study_ready, depende de E09) → triagem needs_revalidation sem objeto público → agrupado na #175 como descendente → decisão E09 [ausente] → Task-Spec/PR [ausentes].

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-revalidated-fes-sources/scripts__apex.ps1.sanitized.txt. Locadores e recorte: E10 no registro/MATRIX needs_revalidation; critério de recusa #175; wrapper lido no recorte 609–687. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: ausência de objeto público próprio. PROPOSTA: guard fail-closed. DECISÃO PENDENTE: modelo de identidade (E09). Nada executado.

### Fluxo

Fluxo proposto: comando de mutação do pacote —(antes de up/down/rm/exec)→ guard —(compara identidade declarada × observada)→ prossegue ou recusa com mensagem sanitizada; nenhuma limpeza ou recriação no caminho de recusa.

### Consequências e risco

Sem guard, o risco de mutar stack alheia depende de como os operadores usam o daemon; é possível, não observado agora. Confiança média: a probabilidade depende de uso real que não medimos.

### Alternativas e recomendação

Recomendado: implementar o guard no menor ponto comum das mutações do wrapper, depois de E09, com testes que não precisem de Docker real (stubs de inspect). Alternativas: guard por comando (duplicação e lacunas); confiar só em nomes únicos por checkout (resolve colisão, não prova dono). Reversível.

### Dependências e paralelismo

Depende de E09 (modelo). Pode ser desenhado em paralelo com o preflight de porta E11, que compartilha a mesma identidade. Prova runtime exige daemon dedicado, separado da prova offline.

### Plano e aceite propostos

Antes da decisão, pode-se preparar inventário de pontos de mutação e fixtures sem escolher identidade. Depois: Task-Spec, testes offline para identidade correta/ausente/divergente e controle de que a mutação não é chamada na recusa; runtime dedicado se a garantia escolhida o exigir.

### Comunicação entre responsáveis

Para outro pod: "O guard de ownership é a implementação que vem depois da decisão de identidade da #175; ainda não existe e não deve ser escrito antes dessa escolha."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Posicionar o guard depois de up/down/rm deixaria efeitos colaterais ocorrerem antes da recusa. Que caso o teste ainda não cobre? Não há prova de E10 neste recorte; o teste crítico deve observar que nenhuma chamada mutante ocorre com identidade ausente ou divergente. Como eu explicaria isso para outro pod? E09 escolhe como reconhecer propriedade; E10 aplica a recusa antes da mutação, enquanto inventário e casos podem ser preparados em paralelo.

### Próxima ação e encerramento

Próxima ação: Pod 2 (a confirmar) prepara inventário e matriz de recusa em paralelo à E09. Entrada: operações do wrapper e opções da #175. Saída: folha de implementação pronta após a decisão DEC-10. Encerramento: guard integrado com prova da garantia escolhida, sem adotar recursos alheios.

<a id="item-214"></a>

## E11 — Preflight read-only de dono de porta

Frente: pacote_identidade_stacks. Encaminhamento: agrupar_em_175_revalidar_candidato_porta.

### Identidade e estado

E11 é um candidato local do Pod 2/Infra/DevEx: preflight somente leitura que identifica o dono de uma porta ocupada (seed E11, R2 T32, draft 29/08, entrega 07/09). Sem issue própria; a triagem marcou needs_revalidation e a v2 o agrupou na #175. Publicação dependeria de DEC-15. Owner a confirmar.

### Intenção e benefício

Problema: a porta 8123 pode estar ocupada por outro perfil Colima ou outra stack (C38), e o pacote não diz de quem é; o operador vê um erro genérico. Público: quem roda vários perfis/daemons. Ganho: diagnóstico acionável (free, expected, foreign, unavailable) sem mutar containers.

### Feito, faltante e não comprovado

Feito (relato): patch local [caminho local omitido] 3 arquivos, sobre a base 847d7a0 de agosto, com runtime read-only em macOS relatado (dono esperado, divergente, matriz e porta livre). Falta: revalidação contra a main c3c3ea3 (que mudou o wrapper em 06/10) e definição de "expected" a partir da identidade de E09. Não comprovado: aplicação do patch na main.

### Linhagem

Linhagem: C38 → draft 29/08 → entrega 07/09 com candidate.patch → registro E11 (local_candidate) → triagem needs_revalidation → agrupado na #175 → revalidação [ausente] → publicação [ausente].

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-revalidated-fes-sources/port-owner-patch-receipt.json. Locadores e recorte: E11 no registro; hash e três diff headers do patch histórico; #175 contexto de identidade. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: patch existente, SHA-256 c38c218710babcd73b213d7aca3c33df2a4d8c68837efa31023b95f7b76cf0a2, três blocos diff correspondentes a preflight/teste/fixture. RELATO: base 847d7a0 e runtime read-only macOS. Aplicabilidade e conteúdo completo não foram revalidados; distância de base não prova conflito. DECISÃO PENDENTE: expected/foreign e destino.

### Fluxo

Fluxo proposto: preflight —(lsof/ss ou docker inspect da porta)→ dono observado —(compara com stack esperada deste checkout)→ estado free/expected/foreign/unavailable —(mensagem sem segredos)→ operador. Nenhuma mutação.

### Consequências e risco

Sem o diagnóstico pode persistir erro pouco acionável de porta. A revisão não demonstra incidente, perda de dados nem ausência universal de outro diagnóstico; impacto e probabilidade dependem do uso real.

### Alternativas e recomendação

Recomendado: revalidar o patch sobre a main como estudo e decidir publicação junto com a política da #175; a classificação "foreign" precisa da identidade escolhida. Alternativas: publicar já com "expected" definido por nome (rápido, mas herda a fragilidade de E09); descartar e reescrever depois do guard E10 (perde trabalho validado). Reversível.

### Dependências e paralelismo

Leitura de porta (free/unavailable) pode ser estudada em paralelo e não depende de E09; o estado expected/foreign depende do modelo de identidade. Publicação depende de DEC-15. Não depende de #167/#174.

### Plano e aceite propostos

Passos mínimos: (1) aplicar o patch numa cópia descartável da main e anotar conflitos; (2) separar a parte independente de identidade; (3) testes com porta livre, ocupada por processo não Docker e por container de outro projeto; (4) controle: nenhuma chamada de mutação. Aceite: mensagem correta nos quatro estados.

### Comunicação entre responsáveis

Para outro pod: "Há um preflight de dono de porta pronto em agosto, mas sobre base antiga; ele precisa ser revalidado e a noção de 'dono esperado' depende da decisão de identidade da #175."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Definir expected só por nome herdaria a fragilidade da identidade; tornar o preflight mutante violaria seu benefício de diagnóstico seguro. Que caso o teste ainda não cobre? Hash e cabeçalhos não provam aplicação nem resultado atual; faltam porta livre, processo não Docker, container alheio e ferramenta indisponível na base escolhida. Como eu explicaria isso para outro pod? Há um patch histórico de diagnóstico read-only; sua idade pede revalidação, sem permitir concluir que conflita ou continua funcionando.

### Próxima ação e encerramento

Próxima ação: Pod 2 (a confirmar) faz a revalidação estática do patch sobre a main. Entrada: candidate.patch e decisão E09 quando houver. Saída: nota de revalidação com conflitos e partes independentes. Encerramento: publicação decidida (DEC-15) ou descarte justificado.

<a id="item-215"></a>

## E12 — Fronteira de credenciais S3A do Dev

Frente: dev_credenciais_s3a. Encaminhamento: estudar_sem_destino_publico_ativo.

### Identidade e estado

E12 é um candidato local do Pod 2/Dev/Security sobre a fronteira de credenciais S3A do ambiente dev (seed E12, draft 29/08, entrega 05/09). Destino declarado: issue #55, que é tracking histórico fechado em 2026-09-17 (completed); #127 é referência. Não há issue ativa; a triagem marcou needs_revalidation. Owner a confirmar.

### Intenção e benefício

Problema: dev/conf/spark-defaults.conf traz a credencial padrão pública do MinIO em fs.s3a.access.key e fs.s3a.secret.key, o que pode acabar em conf impressa ou em event log. Público: quem usa o dev local e quem compartilha logs. Ganho: menos exposição de credenciais em conf e logs, mesmo sendo credenciais de laboratório.

### Feito, faltante e não comprovado

Na base, spark-defaults.conf:13–14 contém literais de credenciais de laboratório (não reproduzidos). O overlay exige APEX_S3_ACCESS_KEY_FILE, APEX_S3_SECRET_KEY_FILE e APEX_SPARK_DEFAULTS_PATH. Patch histórico existe com hash ee8f707f… e 14 arquivos; conteúdo/aplicabilidade não foram auditados integralmente. Runtime de setembro e último histórico de arquivo permanecem relatos, sem prova da credencial efetiva em todos os caminhos atuais.

### Linhagem

Linhagem: draft 29/08 → entrega 05/09 (s3/candidate.patch) → registro E12 com destino #55 → #55 fechada em 17/09 → #127 muda overlay de secrets em 06/10 → triagem needs_revalidation → revalidação [ausente] → issue ativa [ausente]. Elo ausente: qualquer objeto público aberto.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-revalidated-fes-sources/dev__conf__spark-defaults.conf.sanitized.txt; fontes/batch-revalidated-fes-sources/dev__docker-compose.package.yml.excerpt.txt; fontes/batch-revalidated-fes-sources/s3-patch-receipt.json. Locadores e recorte: E12; spark-defaults.conf:13–14 sanitizado; overlay package:1–26; hash/14 headers do patch histórico; #55 histórico conforme registro. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: literal no conf base e exigência de fontes por arquivo no overlay. RELATO: Spark 4.0.1/MinIO e 37 registros no candidato antigo. INFERÊNCIA CONDICIONAL: só seguindo mounts, conf gerada e submissão pode-se afirmar a credencial efetiva de um caminho. DECISÃO PENDENTE: fronteira e destino, pois #55 é tracking histórico fechado.

### Fluxo

Fluxo parcial: conf base contém fs.s3a.* literal; overlay aponta secrets e conf gerada para containers. O valor efetivo no Spark depende da composição e carregamento desse caminho, que não foi revalidado. Não se afirma vazamento em log nem remoção universal do literal pelo overlay.

### Consequências e risco

Sem ação, a credencial padrão do MinIO de laboratório continua no conf versionado; o risco prático é baixo enquanto for só laboratório, maior se alguém reutilizar o conf num MinIO exposto. Não há incidente. Confiança alta no fato estático.

### Alternativas e recomendação

Recomendado: revalidar estaticamente o patch sobre a main e, se a lacuna persistir, abrir uma issue única de estudo ou encerrar E12 com decisão explícita de aceitar a credencial de laboratório documentada. Alternativas: remover o literal e exigir variável (quebra o dev puro sem configuração); manter e documentar como credencial de laboratório não reutilizável. Reversível.

### Dependências e paralelismo

Não depende de #127 (já integrada) nem de outras issues. Publicação depende de DEC-15. Pode correr em paralelo com #33 (SECURITY.md), que pode orientar a política de segredos de laboratório.

### Plano e aceite propostos

Passos mínimos: (1) aplicar o patch numa cópia descartável e listar conflitos; (2) decidir destino; (3) se implementar: teste que falhe se spark-defaults.conf contiver credencial literal, e controle de que o dev puro ainda sobe com variável definida; (4) documentação de como configurar. Aceite: nenhum literal no conf e dev funcional.

### Comunicação entre responsáveis

Para outro pod: "O conf do dev ainda traz a credencial padrão do MinIO; o pacote usa arquivos de segredo pelo overlay. Precisamos decidir se aceitamos o literal de laboratório documentado ou se removemos."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Remover o literal sem definir uma fonte suportada pode impedir o dev simples de acessar S3; confiar só na existência do overlay pode ocultar outro caminho que lê o conf base. Que caso o teste ainda não cobre? Não se observou conf efetiva, event log ou aplicação do patch na base atual; o relato de 37 registros não supre essas lacunas. Como eu explicaria isso para outro pod? O literal versionado e os secrets do pacote coexistem; o estudo deve seguir a configuração até o Spark antes de concluir exposição ou correção.

### Próxima ação e encerramento

Próxima ação: Pod 2 (a confirmar) faz a revalidação estática e propõe destino. Entrada: patch local e conf na base. Saída: nota de revalidação e decisão de destino. Encerramento: issue de estudo aberta com autorização ou E12 encerrado com decisão registrada.

<a id="item-216"></a>

## E13 — Rotação local de credencial ClickHouse

Frente: infra_credenciais_clickhouse. Encaminhamento: agrupar_em_176_estudo_sem_gate_v1.

### Identidade e estado

E13 é um estudo do Pod 2/Infra/Security sobre rotação local de credencial do ClickHouse, publicado da minuta P-E13 como issue luanmorenommaciel/apex#176 em 2026-10-11 por gustocezar, aberta, sem assignee e sem comentários no snapshot. Owner a confirmar (Infra).

### Intenção e benefício

Problema documentado pela #176: falta consolidar e decidir um procedimento suportado de rotação/recuperação local preservando dados e limitando segredo. Há draft histórico; sua existência impede dizer que todo procedimento está ausente. Público: operadores locais e pacote.

### Feito, faltante e não comprovado

Compose parametriza usuário/senha e persiste dados; o draft de 29/08 já orienta estudar consistência entre volume e consumers, backup/rollback e decisão rotação versus recriação. Falta decidir perfil e validar comportamento com volume existente. A revisão não estabelece como a imagem 24.8 persiste usuários nem se mudar env altera a credencial após restart.

### Linhagem

Linhagem: draft forense de 29/08 → registro E13 (study_ready, rec defer) → minuta P-E13 → #176 (11/10) → estudo [ausente] → prova descartável [ausente]. Elo ausente: vínculo público entre a #176 e o draft local.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-revalidated-fes-sources/credential-rotation-draft.md; fontes/batch-revalidated-fes-sources/infra__docker-compose.yml.sanitized.txt. Locadores e recorte: E13/#176 integral; draft de rotação integral; infra Compose usuário/senha/volume e consumers. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: configuração de credencial e volume, issue aberta e draft existente. RELATO HISTÓRICO: procedimentos antigos referidos no draft. DECISÃO PENDENTE: suporte e estratégia de rotação, consumers e recuperação. Comportamento da imagem permanece não verificado; nenhuma execução.

### Fluxo

Fluxo proposto: operador —(nova credencial em arquivo/variável, fora do git)→ ClickHouse (ALTER USER in-place ou recriação com volume) —(healthcheck e clientes Engine/Serve/Memory atualizados)→ verificação —(falha)→ rollback para a credencial anterior. Nada observado.

### Consequências e risco

Sem procedimento, uma rotação improvisada pode trancar o operador fora do próprio store ou forçar recriar o volume e perder dados locais. Impacto local, sem incidente registrado. Confiança média: depende do comportamento da imagem, não medido.

### Alternativas e recomendação

Recomendado: estudo curto que documente os dois caminhos para o perfil suportado e prove um deles num ambiente descartável. Alternativas: rotação in-place com ALTER USER (preserva volume; exige acesso administrativo); recriação com novo volume (simples, perde dados); recomendar não rotacionar no perfil local (aceitável para laboratório, documentado). Reversível.

### Dependências e paralelismo

Não depende de outras issues. #33 (SECURITY.md) pode orientar a política, mas não é gate técnico. Não bloqueia v1, salvo decisão do mantenedor de exigir runbook de credenciais.

### Plano e aceite propostos

Passos mínimos: (1) inventariar onde a credencial é lida (Compose, healthcheck, clientes); (2) escrever os dois procedimentos; (3) prova descartável com dados sintéticos e controle de que os dados sobrevivem; (4) recibo sem segredos. Aceite: runbook revisado e um recibo.

### Comunicação entre responsáveis

Para outro pod: existe draft histórico, mas falta decidir e demonstrar um caminho local de rotação/recuperação. Alterar env não é, por si, prova de troca de usuário persistido.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Recriar o volume como se fosse rotação transparente pode eliminar dados; trocar só um consumer pode deixar acesso divergente. Que caso o teste ainda não cobre? Não se comprovou qual credencial vale após restart de volume existente, nem preservação de dados e recusa da antiga conforme a estratégia. Como eu explicaria isso para outro pod? A #176 consolida alternativas e recuperação por perfil; o draft é ponto de partida documental, sem executar nem ratificar a rotação.

### Próxima ação e encerramento

Próxima ação: Infra (a confirmar) produz o inventário de leitura de credencial e a proposta de runbook. Entrada: Compose de infra e draft de 29/08. Saída: runbook proposto na #176. Encerramento: runbook com recibo de prova descartável, ou decisão explícita de não suportar rotação local.

<a id="item-217"></a>

## E15 — Política de dependências e checks

Frente: governanca_ci. Encaminhamento: decidir_politica_dependencias_issue_propria_ou_125.

### Identidade e estado

E15 é governança técnica (Governança/CI): política de dependências e checks, decidida junto com a #125 segundo o registro, ou em issue própria. Objeto público mais próximo: luanmorenommaciel/apex#125 "[Governance] Protect main with required CI checks and pull-request review", aberta, sem assignee; #130 é referência. A política de dependências não está no título da #125. Owner: admin/mantenedor (a confirmar).

### Intenção e benefício

Problema: na árvore .github lida não há dependabot.yml nem CODEOWNERS e o job Front não contém npm audit; o registro pede política de severidade/exceções. Isso não prova ausência de alertas ativados por configuração externa ou vulnerabilidade concreta. Público: mantenedores e revisores.

### Feito, faltante e não comprovado

Base: .github contém apenas workflows/ci.yml e workflows/jar.yml (nenhum dependabot.yml nem CODEOWNERS na árvore); o job front não roda audit. Falta: decisão de política e destino. Não comprovado: se alertas do Dependabot estão ligados na configuração do repositório, que não é visível pela árvore.

### Linhagem

Linhagem: R2 T28b → registro E15 (decision_required, deps G01/G02) → F14/#138 deixou audit explicitamente fora → triagem needs_revalidation sem objeto próprio → #125 discute proteção de main → decisão [ausente]. Elo ausente: objeto público que nomeie a política de dependências.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/.github__workflows__ci.yml.txt; fontes/batch-revalidated-fes-sources/repository-tree-metadata.json. Locadores e recorte: E15; #125; árvore .github por git ls-tree na base e workflow ci.yml integral no recorte de jobs. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: arquivos ausentes na árvore .github e ausência de etapa audit no job lido. INFERÊNCIA LIMITADA: esse verde não representa um gate explícito de audit. DECISÃO PENDENTE: severidade, exceções, owners e destino. Settings de alertas não foram consultados.

### Fluxo

Fluxo proposto: PR de dependência → aviso ou gate por severidade → exceção com responsável/prazo → revisão. CODEOWNERS é configuração distinta de solicitação de revisores; os arquivos e etapa propostos não estão na árvore/configuração lida, sem conclusão universal sobre alertas externos.

### Consequências e risco

Sem etapa explícita de audit na CI lida, o verde observado não certifica a análise de vulnerabilidades. Alertas ou controles fora dessa configuração não foram inspecionados. O risco é genérico; nenhuma vulnerabilidade concreta foi apontada.

### Alternativas e recomendação

Recomendado: issue própria e pequena de política de dependências, separada da proteção de main, porque têm donos e ritmos diferentes. Alternativas: incluir na #125 (menos objetos, escopo maior); só Dependabot alerts sem gate (barato, não bloqueia); npm audit com limiar alto e lista de exceções versionada (gate real, risco de falso vermelho por registry). Reversível.

### Dependências e paralelismo

Não depende de #130 para decidir; executar um gate novo depende de runner. Pode ser decidido em paralelo com #125. CODEOWNERS depende de ter owners por pod definidos.

### Plano e aceite propostos

Passos mínimos: (1) mantenedor decide destino (issue própria ou #125); (2) política com severidade, exceções e responsável; (3) se gate: etapa no job front com limiar e teste negativo (dependência com vulnerabilidade conhecida em fixture); (4) documentação. Aceite: política escrita e, se houver gate, controle negativo.

### Comunicação entre responsáveis

Para outro pod: a CI lida não possui gate explícito de audit de dependências. Configurações de alertas não foram consultadas; propomos decidir uma política separada da proteção de branch.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Tratar alertas como gate daria ao verde uma garantia inexistente na configuração lida; bloquear por qualquer erro de registry também confundiria indisponibilidade com vulnerabilidade. Que caso o teste ainda não cobre? Dependências não foram auditadas e settings de alertas não foram lidos; primeiro definir severidade, exceção e modo de falha antes de controle negativo. Como eu explicaria isso para outro pod? E15 decide política de dependências; proteção de branch na #125 e ownership por caminho são decisões relacionadas, com garantias distintas.

### Próxima ação e encerramento

Próxima ação: mantenedor/admin (a confirmar) decide o destino da política. Entrada: esta ficha e #125. Saída: issue própria aberta com autorização ou decisão registrada na #125. Encerramento: política registrada ou adiamento explícito.

<a id="item-218"></a>

## E16 — Regressões do harness R9D

Frente: harness_overhead_r9d. Encaminhamento: agrupar_em_167_revisar_candidato_conjunto.

### Identidade e estado

E16 é um follow-up do Pod 2/Harness sobre regressões do harness R9D (origem revisão §1 e P8 da #127), publicado da minuta P-GATE como issue luanmorenommaciel/apex#167 em 2026-10-11 por gustocezar, aberta, assignee gustocezar (reserva e candidato local), um comentário com várias rodadas. P-GATE também listava E17, que a publicação mandou para a #123 (gate tail-outlier). Owner a confirmar (Pod 2).

### Intenção e benefício

Problema: o braço ON do experimento de overhead passa -EnvFile e -AdditionalComposeFile a um runner que não os declara, então a execução para no binding antes de medir qualquer coisa; além disso, o overlay de pacote exige variáveis de segredo S3 com :?, o que faz o compose falhar se elas faltarem. Público: quem roda o protocolo de overhead (#113). Ganho: um harness R9D executável com braços comparáveis.

### Feito, faltante e não comprovado

Base: r9d_overhead_ab.py:368-375 monta o mesmo comando para os dois braços com -EnvFile e -AdditionalComposeFile; e2e_canonical.ps1 declara só Scenario, StartDev e SkipGenerate; dev/docker-compose.package.yml usa ${APEX_S3_ACCESS_KEY_FILE:?…}, ${APEX_S3_SECRET_KEY_FILE:?…} e ${APEX_SPARK_DEFAULTS_PATH:?…}. Feito (relato local): candidato conjunto com #174 que declara os parâmetros no ON e passa EnvFile; 59+26 testes e prova integral do e2e sob stubs (7/3 → 10/0, controle 8/2). Falta: escolher a variante de binding, prova Windows, Compose real e análise da assimetria de preflight do braço OFF. Não comprovado: execução do harness.

### Linhagem

Linhagem: revisão §1/P8 da #127 → registro E16 (review_required, depende do merge #127) → merge #127 → minuta P-GATE (E16+E17) → #167 só com E16; E17 reaproveita #123 (disposição PUBLICATION) → candidato local conjunto → revisões Gemini estáticas e fixtures Windows propostas → decisão DEC-N5 [ausente] → PR [ausente] → benchmark real [fora do escopo, #113].

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/dev__scripts__r9d_overhead_ab.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/dev__scripts__e2e_canonical.ps1.txt; fontes/batch-revalidated-fes-sources/dev__docker-compose.package.yml.excerpt.txt; D-CORRECOES-E-LIMITES.md. Locadores e recorte: E16/P-GATE publicação E17→#123; #167 comentário integral; harness:368–375, runner:1–20 e overlay :1–12; C04-24/25. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO estático: harness envia dois parâmetros ausentes no runner ON avançado e overlay exige arquivos/caminho. RELATO: falha contra a base, candidato, 59+26 testes e prova e2e com stubs/loopback. Duas variantes têm bytes e provas distintos; nenhum teste executado nesta revisão, nenhum benchmark real demonstrado por esses controles. PR/integração do candidato não constam nos objetos públicos capturados.

### Fluxo

Fluxo observado: r9d_overhead_ab.e2e_command —(-EnvFile, -AdditionalComposeFile)→ e2e_canonical.ps1 (ON) —(binding falha: parâmetro inexistente)→ aborto; mesma chamada —(parâmetros declarados)→ r9d_e2e_canonical_noplugin.ps1 (OFF) —(compose com overlay :?)→ preflight. Fluxo do candidato: ON declara e encaminha os dois parâmetros ao Compose.

### Consequências e risco

Sem correção, o protocolo de overhead não executa; se alguém consertar só um braço, os braços passam a ter ambientes diferentes e qualquer número de overhead fica inválido. Risco possível, sem medição recente. Confiança alta no defeito estático.

### Alternativas e recomendação

Recomendado: revisar o candidato conjunto, escolher a variante de binding e manter interface comum explícita nos dois runners. Alternativas: adaptar só o harness para não passar os parâmetros ao ON (rompe a equivalência de configuração); copiar a configuração para dev/.env (reintroduz o problema da #174). Uma PR conjunta com E08 é coesa; dividir exige ordem clara.

### Dependências e paralelismo

Dependência técnica compartilhada com E08/#174 (mesma passagem de configuração). Não depende de #113 para corrigir a interface; #113 depende deste conserto para executar. E17/#123 segue em paralelo. Não depende de #175.

### Plano e aceite propostos

Passos mínimos: (1) DEC-N5; (2) teste sem runtime que enumera argumentos enviados e falha se algum não existir na interface do runner; (3) teste que detecta argumento removido de um só braço; (4) preflight com mensagem clara quando arquivos de segredo faltam, sem imprimir conteúdo; (5) benchmark real fora do PR. Aceite: binding provado nos dois braços.

### Comunicação entre responsáveis

Para outro pod: "O braço ON do experimento de overhead nem começa porque recebe parâmetros que não declara. O conserto está num candidato local junto com a preservação do dev/.env; um teste de argumentos não é prova de overhead."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Corrigir apenas um braço ou omitir overlay no ON pode tornar as configurações ON/OFF incomparáveis mesmo que o binding passe. Que caso o teste ainda não cobre? A prova e2e sob stubs não mede overhead nem demonstra equivalência real dos braços, Windows ou Compose; múltiplos overlays por -File pedem contrato explícito. Como eu explicaria isso para outro pod? O defeito de interface impede o caminho ON atual; a correção conjunta preserva dev/.env, enquanto protocolo e benchmark da #113 seguem separados.

### Próxima ação e encerramento

Próxima ação: Pod 2 e mantenedor (a confirmar) escolhem DEC-N5 e o patch. Entrada: candidato 1122d031… e PATCH-167.diff com recibos. Saída: PR com teste de interface dos dois braços. Encerramento: critérios da #167 marcados e benchmark encaminhado à #113 como execução separada.

<a id="item-219"></a>

## E18 — Piso absoluto de duração no watcher tail-outlier

Frente: engine_tail_outlier. Encaminhamento: agrupar_em_168_adiar_limiar_ate_corpus.

### Identidade e estado

E18 é um estudo do Pod 2/Engine sobre piso absoluto de duração no watcher tail-outlier (origem revisão B-4 item 3 da #127), publicado da minuta P-E18 como issue luanmorenommaciel/apex#168 em 2026-10-11 por gustocezar, aberta, assignee gustocezar (reserva de estudo), um comentário. Owner da decisão de limiar: Engine (a confirmar).

### Intenção e benefício

Problema hipotético: com 100 tasks/amostras e demais guards satisfeitos, uma razão max/p50 estritamente maior que 10 pode gerar WARNING mesmo em escala de milissegundos. Razão igual a 10 não passa. Falta caracterizar relevância absoluta; nenhum falso positivo real foi observado.

### Feito, faltante e não comprovado

Base: tail_outlier.py:16-37 exige MIN_TASKS_FOR_TAIL = 100, MIN_DURATION_SAMPLES_FOR_TAIL = 100, p50 efetivo positivo, razão max/p50 acima do limite e ausência de veredito do watcher de skew; não há piso absoluto. Feito (relato no comentário): grade estática C3 com 23 casos sintéticos e recomendação de adiar a escolha de um número até haver evidência de escala, variação entre execuções e contexto. Falta: corpus sanitizado com unidades e população. Não comprovado: frequência real do caso de milissegundos.

### Linhagem

Linhagem: revisão B-4 da #127 → registro E18 (study_ready, depende do merge #127) → merge #127 → minuta P-E18 → #168 (11/10) → grade C3 e contrato de corpus no comentário → corpus [ausente] → decisão de limiar [ausente]. Sem elo de implementação, corretamente.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/engine__src__apex_engine__watchers__tail_outlier.py.txt. Locadores e recorte: E18/#168 corpo e comentário 6109742610 integrais; tail_outlier.py:1–71. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: guards sem piso absoluto. RELATO: grade de 23 casos e contrato de corpus, sem execução do produto. INFERÊNCIA: o caso de milissegundos é plausível, não medido. DECISÃO PENDENTE: manter regra, acrescentar contexto de escala ou definir limiar após evidência. Nenhuma execução.

### Fluxo

Fluxo observado: StageEvent —(task_count, duration_sample_count, p50, max)→ guards do watcher —(passa e skew não reivindica)→ finding TAIL_OUTLIER WARNING —(evidência de duração)→ consumidores. Fluxo proposto pelo estudo: corpus sanitizado —(distribuição por escala)→ decisão —(regra ou contexto)→ watcher.

### Consequências e risco

Sem ação, o detector continua como integrado; o pior caso é ruído em stages muito curtos, que F13/F18/S17 podem mitigar na apresentação. Escolher um número sem corpus pode esconder atrasos reais. Confiança alta na leitura do código; baixa sobre frequência.

### Alternativas e recomendação

Recomendado: manter adiado o número e coletar corpus sanitizado; enquanto isso, a apresentação da #166 pode mostrar a escala absoluta ao lado da razão. Alternativas: piso fixo em ms (simples, arbitrário); piso relativo ao job (mais robusto, mais complexo); nenhuma mudança e só contexto na mensagem (barato). Reversível, mas mudar detector exige decisão.

### Dependências e paralelismo

Pode correr em paralelo com #166 (apresentação) e #123 (gate); não deve bloqueá-los. Precisa de contribuição de quem tem workloads reais para o corpus. Harmonizar população com #169 sem herdar seu seletor.

### Plano e aceite propostos

Passos mínimos de estudo: (1) contrato de corpus com unidades, população e contexto; (2) coleta sanitizada; (3) relatório de sensibilidade; (4) recomendação ao mantenedor. Condição de não ação no detector até lá. Se implementar depois: casos positivos, negativos e de fronteira em várias escalas, com controle de que atrasos grandes continuam detectados.

### Comunicação entre responsáveis

Para outro pod: "Não vamos inventar um piso de duração para o detector de cauda; primeiro precisamos de dados reais em várias escalas. Até lá a regra continua como está."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Um piso arbitrário pode esconder atrasos reais; razão igual a 10 já é recusada pelo guard atual, portanto não deve ser apresentada como positivo. Que caso o teste ainda não cobre? A grade de 23 casos e os exemplos de corpus não foram executados; faltam workloads sanitizados em escalas distintas e variação entre runs. Como eu explicaria isso para outro pod? O watcher mede cauda observacional com guards de população e skew; a #168 decide se escala absoluta exige contexto ou limiar após evidência.

### Próxima ação e encerramento

Próxima ação: Engine (a confirmar) publica o contrato de corpus e pede contribuições. Entrada: grade C3 e contrato do comentário. Saída: corpus sanitizado e relatório. Encerramento: recomendação registrada (implementar, adiar ou rejeitar) na #168.

<a id="item-220"></a>

## E19 — Endurecer guard SQL×DDL (#94 follow-up)

Frente: engine_guard_sql_ddl. Encaminhamento: encerrar_pr_integrada.

### Identidade e estado

E19 é um candidato local que virou a PR luanmorenommaciel/apex#139 "test(engine): harden SQL to DDL column guard" (head 087ce22, Pod 2/Engine), integrada em 2026-10-06T20:12:05Z no merge 987a5fa. Follow-up do guard da #94. Sem assignee; nada pendente neste ID.

### Intenção e benefício

Problema: NOT_COLUMNS, a lista de tokens que o guard SQL×DDL ignora, continha job_id e attributes, que são colunas reais; remover essas colunas de todos os DDLs não seria detectado. Público: quem altera DDL ou queries do Engine. Ganho: o guard da #94 passa a cobrir as duas colunas mais usadas.

### Feito, faltante e não comprovado

Base: engine/tests/test_sql_columns_exist_in_ddl.py:40-44 lista em NOT_COLUMNS apenas funções, palavras-chave SQL, "apex", "spark_events" e "String"; job_id e attributes não estão mais lá. Falta neste ID: nada. A coerência entre a constante do preflight e as queries é outro guard (E20/#155). Não comprovado: CI hospedada do head.

### Linhagem

Linhagem: entrega pr94 de 05/09 e STATE owner_decision → commit 087ce22 na branch codex/sql-ddl-guard-hardening → PR #139 (27/09) → controle negativo 2/2 e guard 7/7 relatados → check-runs sem steps → merge 987a5fa em 06/10. Follow-up: E20.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/engine__tests__test_sql_columns_exist_in_ddl.py.txt. Locadores e recorte: E19/#139; test_sql_columns_exist_in_ddl.py:1–107; NOT_COLUMNS:40–44; extrator:60–84. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: NOT_COLUMNS na base sem job_id e attributes. RELATO HISTÓRICO: controle negativo 2/2, guard 7/7 e suíte Engine 125 passed/11 skipped do autor, além de compatibilidade offline com o clickhouse.py da #131. Sem CI hospedada útil observada; runtime não se aplica a um teste estático.

### Fluxo

Fluxo observado: SQL do Engine —(tokens extraídos por regex)→ conjunto lido menos NOT_COLUMNS —(comparação)→ colunas dos DDLs —(faltante)→ falha do teste. Com job_id fora de NOT_COLUMNS, remover job_id do DDL agora falha.

### Consequências e risco

Sem ação, a proteção está na main. O limite conhecido é o extrator por regex, que pode errar em SQL não trivial; é limite de cobertura, não defeito demonstrado. Confiança alta.

### Alternativas e recomendação

Recomendado: encerrar E19. Alternativa futura: substituir regex por parser SQL; mais robusto, mais dependências, não justificado agora. Reversível.

### Dependências e paralelismo

Nenhuma dependência para encerrar. E20/#155 reutiliza o mesmo extrator de colunas; um ajuste futuro no extrator afeta os dois guards e deveria ser revisado junto, mas não é gate de nenhum deles.

### Plano e aceite propostos

Condição de não ação: nenhum passo neste ID. Reabrir se NOT_COLUMNS voltar a conter colunas reais; um controle útil para o futuro seria um teste que falhe quando um token de NOT_COLUMNS também aparecer como coluna em algum DDL.

### Comunicação entre responsáveis

Para outro pod: "O guard que confere colunas das queries contra os DDLs agora cobre job_id e attributes (#139). Ele ainda usa regex, então SQL muito criativa pode escapar; isso é limite conhecido, não defeito."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Voltar a ignorar job_id e attributes mascararia a remoção dessas colunas reais do DDL no extrator. Que caso o teste ainda não cobre? Regex não cobre toda gramática SQL nem estado de um deployment; a leitura não reproduz as mutações históricas. Como eu explicaria isso para outro pod? A #139 protege coerência entre texto SQL e colunas declaradas, enquanto preflight cobre schema aplicado e E20 liga sua constante às queries.

### Próxima ação e encerramento

Próxima ação: confirmar encerramento de E19. Owner: nenhum necessário. Entrada: teste na base. Saída: linha E19 "entregue em 987a5fa". Encerramento: imediato.

