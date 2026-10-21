# Fichas documentais — lote 23

Cortes históricos por ficha; propostas não são decisões nem execuções novas. Arquivos locais citados não estão publicados como prova bruta. Adendos atuais prevalecem para os objetos que atualizam.

<a id="item-221"></a>

## E20 — Ligar a constante do preflight às colunas lidas pelas queries do Engine

Frente: engine_preflight_schema. Encaminhamento: executar_revisao_155_e_escolher_prova.

### Identidade e estado

E20 é um teste do Pod 2/Engine que liga REQUIRED_SPARK_EVENTS_COLUMNS às colunas lidas pelas queries de stage. Representado pela issue luanmorenommaciel/apex#154 (aberta em 2026-10-07 por gustocezar, sem assignee, sem comentários) e pela PR #155 "test(engine): keep schema preflight aligned with stage queries" (head 561b27e, base c4541a5, aberta, Closes #154, zero reviews). Owner da revisão: Engine + mantenedor (a confirmar).

### Intenção e benefício

Problema: a constante do preflight da #131 não estava ligada às queries STAGE_EVENTS_SQL e STAGE_AGGREGATES_SQL; remover attributes da constante deixava a suíte verde. Público: quem altera queries ou preflight. Ganho: drift entre o que se exige e o que se lê passa a falhar em teste.

### Feito, faltante e não comprovado

O diff #155 altera só o teste (+27/-1) e compara conjunto derivado das queries versus REQUIRED_SPARK_EVENTS_COLUMNS nos dois sentidos. #154 registra revalidação posterior de 46 focados e 310 Engine+root/11 skips em c4541a5; 229/11 pertence à combinação histórica anterior. Onze checks failure capturados, jobs sem steps; não demonstram falha dessa asserção nem causa operacional única. Extensão SHAPE_HISTORY cd0ddf9 continua relato local separado.

### Linhagem

Linhagem: revisões independentes lote 2/3 de 28/09 (TS15) → commit local 3ca411a e combinação lane D 65e2f3f (árvore idêntica) → relatório de 01/10 com SHAPE_HISTORY_SQL (cd0ddf9) → issue #154 (07/10) → PR #155 (561b27e) → 11 checks failure sem steps → review [ausente] → decisão [ausente]. Elo ausente: publicação ou descarte explícito da extensão SHAPE_HISTORY_SQL.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/pr155-files.json; fontes/pr155-checks.json; ../parte-03-claude-v2/fontes/claude-v2/_build/snapshot-20261016/jobs_37559317393.json; fontes/batch-revalidated-fes-sources/e20-shape-history-report.md. Locadores e recorte: E20/#154 corpo integral; #155 diff integral/checks; jobs_37559317393; relatório SHAPE_HISTORY integral. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: diff test-only com comparação em duas direções, head 561b27e e 11 failure; jobs consultados não contêm steps. RELATO: controles locais e contagens por base, além de anotação de billing descrita na issue. Não se infere causa financeira atual só do vazio de steps. DECISÃO PENDENTE: integração/prova e extensão SHAPE_HISTORY.

### Fluxo

Fluxo lido no diff: STAGE_EVENTS_SQL + STAGE_AGGREGATES_SQL → _columns_read_by → duas diferenças de conjuntos contra REQUIRED_SPARK_EVENTS_COLUMNS → asserção com lista de divergências. SHAPE_HISTORY_SQL não entra nesse diff; o relatório local propõe teste adicional de inclusão.

### Consequências e risco

Sem a guarda, ampliar a SQL ou reduzir o preflight pode passar despercebido até falhar em runtime. Confiança alta na finalidade; o extrator por regex é limite partilhado com E19. Sem incidente.

### Alternativas e recomendação

Recomendado: revisar e integrar a #155 como está, e decidir separadamente se a extensão SHAPE_HISTORY_SQL vira PR própria. Alternativas: derivar a constante das queries em runtime (acopla preflight a parser); incluir SHAPE_HISTORY_SQL na mesma PR (amplia escopo e exige nova revisão). Reversível.

### Dependências e paralelismo

Sem predecessor técnico das outras PRs abertas: #131/#139 estão integradas. Revisão e decisão da prova podem ocorrer já; capacidade atual do runner precisa evidência própria, e #130 histórico não é gate universal.

### Plano e aceite propostos

Passos mínimos: (1) revisão do diff com atenção aos controles de coluna omitida/adicionada; (2) escolha da prova de integração (CI na árvore escolhida ou recibo local delimitado); (3) decisão de merge, fechando #154; (4) decisão sobre SHAPE_HISTORY_SQL. Aceite: teste falha com constante reduzida e com query ampliada.

### Comunicação entre responsáveis

Para outro pod: a #155 adiciona uma guarda bidirecional entre queries e preflight. Os checks capturados estão vermelhos sem steps; isso não é execução falha da asserção nem prova de bloqueio atual para toda a fila.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Uma query ampliada sem preflight ou um preflight com exigência não usada degradaria erro/schema sem a nova guarda detectar os dois sentidos. Que caso o teste ainda não cobre? SHAPE_HISTORY_SQL está fora do diff #155; seu teste adicional é candidato local, e jobs sem steps não executam nenhuma das asserções. Como eu explicaria isso para outro pod? É uma proteção estática test-only já publicada; 229 e 310 pertencem a árvores históricas distintas e não devem ser somados.

### Próxima ação e encerramento

Próxima ação: revisor do Engine e mantenedor (a confirmar) revisam a #155 e escolhem a prova. Entrada: head 561b27e e recibos. Saída: decisão de merge registrada e #154 atualizada. Encerramento: #155 integrada ou fechada com motivo; extensão SHAPE_HISTORY_SQL com destino.

<a id="item-222"></a>

## E21 — Guard do alvo de Materialized View não reconhece TO multilinha

Frente: infra_guard_mv. Encaminhamento: encerrar_pr_integrada_politica_em_170.

### Identidade e estado

E21 é uma correção local do Pod 2/Infra que virou a PR luanmorenommaciel/apex#147 "fix(infra): check multiline materialized-view targets" (head a07fc04), integrada em 2026-10-06T20:12:09Z no merge 928da21. Origem: issue #72 (fechada em 2026-08-18) e rodada R5 de 30/09. Sem assignee.

### Intenção e benefício

Problema histórico: guard por linha não extraía TO separado de CREATE MATERIALIZED VIEW em 010. R5 relata que ClickHouse 24.8 aceitou alvo inexistente e o controle diferenciou base e patch; isso não foi reproduzido nesta revisão. Ganho: o bootstrap verifica a existência do alvo mesmo com SQL multilinha.

### Feito, faltante e não comprovado

Base: apply_ddl.sh:37-55 comenta a defesa da #72, explica que CREATE e TO podem estar em linhas separadas e remove comentários e quebras (sed + tr '\n' ' ') antes de extrair os alvos, verificando EXISTS TABLE para cada um. Falta neste ID: nada. Fora dele: a política de reaplicação e o alcance do verify_ddl (E22/E23, #170). Não comprovado: comportamento em outras versões do ClickHouse e CI hospedada.

### Linhagem

Linhagem: issue #72 (MV criada contra alvo ausente) → R5 de 30/09 com patch local 4a4a7ca → PR #147 (head a07fc04) → teste discriminante T1/T4 base rc 0 × patch rc 1 e 10/10 controles relatados → checks não iniciados (billing) → merge 928da21 em 06/10. Follow-up: #170.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-revalidated-fes-sources/infra__scripts__apply_ddl.sh.excerpt.txt; fontes/batch-revalidated-fes-sources/r5-report-excerpt.md. Locadores e recorte: E21/#147 e #72; apply_ddl:37–57; R5 §7E T1–T5 e limites. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: guard multilinha na base. RELATO: teste discriminante e revisão independente com bash -n e shellcheck. Sem CI hospedada útil observada; runtime relatado, não reproduzido.

### Fluxo

Fluxo observado: arquivo SQL —(remove comentários e quebras)→ texto contínuo —(regex CREATE MATERIALIZED VIEW … TO <alvo>)→ alvos —(EXISTS TABLE)→ ClickHouse —(ausente)→ erro com nome do arquivo e do alvo e saída não zero.

### Consequências e risco

Sem ação, a proteção permanece. O limite registrado é a regex shell para SQL não trivial (por exemplo, nomes entre crases ou comentários de bloco). Confiança alta.

### Alternativas e recomendação

Recomendado: encerrar E21. Alternativa futura: verificar alvos consultando system.tables depois da aplicação, independente de regex; mais robusto, fora deste ID. Reversível.

### Dependências e paralelismo

Nenhuma dependência para encerrar. A #170 (E22/E23) trata a política de reaplicação e o alcance do verify_ddl de forma independente; nenhuma decisão ali exige refazer o guard da #147.

### Plano e aceite propostos

Condição de não ação: nenhum passo neste ID. Reabrir se uma MV com alvo ausente passar pelo apply na main; o teste discriminante relatado (base rc 0 × patch rc 1) seria o controle a reexecutar nesse caso.

### Comunicação entre responsáveis

Para outro pod: "O apply-ddl agora encontra o alvo da MV mesmo quando o TO está em outra linha (#147). Se é seguro reaplicar DDL com ingestão ativa é outra decisão, na #170."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Extrair alvos linha a linha deixaria escapar o formato multilinha de 010, mesmo sem erro de aplicação segundo o ensaio histórico. Que caso o teste ainda não cobre? A regex ainda tem limites para crases/comentários de bloco e não prova ingestão; testes em outras versões não foram conferidos. Como eu explicaria isso para outro pod? A #147 encontra alvos multilinha e verifica EXISTS TABLE; segurança de ingestão durante migrações e semântica de MV continuam em #170.

### Próxima ação e encerramento

Próxima ação: confirmar encerramento de E21. Owner: nenhum necessário. Entrada: apply_ddl.sh na base. Saída: linha E21 "entregue em 928da21; política em #170". Encerramento: imediato.

<a id="item-223"></a>

## E22 — Reaplicação de DDL pode regredir temporariamente o MV de spark_events

Frente: infra_migracoes. Encaminhamento: agrupar_em_170_decidir_politica_de_reaplicacao.

### Identidade e estado

E22 é um estudo/decisão do Pod 2/Infra e Pod 3/ingestão sobre reaplicação de DDL que pode regredir temporariamente o MV de spark_events. Publicado (com E23) da minuta P-DEC25 como issue luanmorenommaciel/apex#170 em 2026-10-11 por gustocezar, aberta, sem assignee e sem comentários. Decisão: owner Infra e dono da ingestão (DEC-25), a confirmar.

### Intenção e benefício

Problema: apply_ddl.sh percorre todos os SQLs e afirma que reaplicar "is always safe and a no-op once the schema is current"; mas cada migração 034-039 faz MODIFY QUERY do MV, e um evento recebido entre a reaplicação de 034 e a de 039 pode gravar 0 nos campos tipados posteriores, sem backfill. Público: quem reaplica DDL com ingestão ativa. Ganho: saber quando reaplicar é seguro e o que fazer quando não é.

### Feito, faltante e não comprovado

Base contém alegação always safe/no-op e migrações 034–039 com MODIFY QUERY. Relatos R5 e lane1 em 24.8.14.39 distinguem estado final quiescente idempotente de linhas ingeridas na janela sintética: após só 034, 14/14 valores brutos preservados e 0/14 tipados, sem backfill após 039. Lane1 também mostra janela progressiva na primeira migração v0.1. Não há medida sob carga, spans reais do JAR, reparo nem leitura do Engine dessas linhas na lane1.

### Linhagem

Linhagem: R5 (30/09) → parecer DEC-25 (30/09) → lane1-dec25 (01/10) → registro E22 (decision_required) → minuta P-DEC25 (E22+E23) → #170 (11/10) → medição sob carga [ausente] → decisão [ausente] → reparo [ausente].

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-revalidated-fes-sources/infra__scripts__apply_ddl.sh.excerpt.txt; fontes/batch-revalidated-fes-sources/r5-report-excerpt.md; fontes/batch-revalidated-fes-sources/lane1-dec25-report.md; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/engine__src__apex_engine__clickhouse.py.txt; fontes/batch-revalidated-fes-sources/migration-query-locators.json. Locadores e recorte: E22/#170; apply_ddl:8–58; R5 S2; lane1-dec25 §§3–7 integral; Engine runtime fallback nas queries. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: comentário de segurança absoluta e migrações com MV. RELATO: fixture sintética com zeros persistentes e valores brutos preservados em attributes. INFERÊNCIA: o dado bruto em attributes permitiria reparo, não testado. DECISÃO PENDENTE: suportar ou não reaplicação com ingestão ativa e qual mitigação.

### Fluxo

Fluxo histórico relatado: evolução/reaplicação parcial do MV → evento sintético em query intermediária → tipadas ainda não projetadas em zero e attributes brutos presentes → query final restaurada → linha permanece sem backfill. A primeira migração também teve janela; leitura posterior do Engine e impacto em finding não foram executados na lane1.

### Consequências e risco

Se alguém reaplicar com ingestão ativa, algumas linhas podem ficar com métricas zeradas e virar findings errados; a ocorrência real não foi comprovada e o próprio registro diz "alto se apply rodar com ingestão ativa". Confiança média: depende da janela real, não medida.

### Alternativas e recomendação

Recomendado ao owner: definir coordenação da ingestão durante toda evolução de MV, inclusive primeira migração, e corrigir a alegação absoluta. Pausa/quiescência, consolidação de query e reparo são alternativas a decidir. Impedir só reaplicação não cobre a janela da primeira migração relatada. Reparo a partir de attributes exige prova própria.

### Dependências e paralelismo

Pode correr em paralelo com E23 (alcance do verificador) e com #109 (reconciliação). Medição sob carga exige ambiente próprio autorizado. #147 não precisa ser refeito.

### Plano e aceite propostos

Passos de decisão: classificar migrations e distinguir estado final/linhas da janela; incluir primeira migração e reaplicação na política; ajustar comentário conforme decisão. Se medir, ambiente descartável próprio com ingestão concorrente e duração; se reparar, controles de bruto presente/ausente, zero genuíno, linhas corretas e pré-migração. Documentação pequena não exige teste de produto.

### Comunicação entre responsáveis

Para outro pod: "Reaplicar DDL com ingestão ativa pode deixar algumas linhas com métricas zeradas; o estado final do schema fica certo, mas as linhas da janela não. Precisamos decidir se isso é suportado."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Impedir apenas reaplicação deixaria descoberta a janela progressiva da primeira migração; chamar schema final idempotente de ingestão sem efeito ignoraria as linhas intermediárias. Que caso o teste ainda não cobre? Os ensaios são sintéticos/sequenciais e sem carga; não provam duração real, spans do JAR, leitura pelo Engine ou reparo das 14 colunas. Como eu explicaria isso para outro pod? O MV final pode voltar ao texto correto sem recalcular linhas inseridas antes; política de ingestão e eventual reparo precisam decisão separada.

### Próxima ação e encerramento

Próxima ação: owner Infra e ingestão (a confirmar) decidem a política na #170. Entrada: três relatórios locais e o comentário de apply_ddl.sh. Saída: decisão DEC-25 e ajuste do comentário. Encerramento: política registrada, com prova de janela ou reparo se escolhidos.

<a id="item-224"></a>

## E23 — Explicitar alcance do verify_ddl.py além de nome e tipo

Frente: infra_migracoes. Encaminhamento: agrupar_em_170_decidir_alcance_verify_ddl.

### Identidade e estado

E23 é uma decisão de cobertura do Pod 2/Infra: explicitar o que verify_ddl.py verifica além de nome e tipo. Agrupado na issue luanmorenommaciel/apex#170 (minuta P-DEC25), aberta, sem assignee. Decisão: owner Infra (DEC-25), a confirmar.

### Intenção e benefício

Problema: verify_ddl.py compara colunas e tipos de sete tabelas e descarta DEFAULT, MATERIALIZED, ALIAS, COMMENT, CODEC e TTL do tipo esperado; DEFAULT, TTL, SETTINGS e MVs alterados ou ausentes deixam a verificação verde por escopo. Público: quem lê "verify-ddl verde" como prova de migração correta. Ganho: o verde passa a dizer exatamente o que garante.

### Feito, faltante e não comprovado

Base: verify_ddl.py:124 aplica re.split sobre DEFAULT|MATERIALIZED|ALIAS|COMMENT|CODEC|TTL antes de comparar o tipo (confirmado). Feito (relato): C7 DEFAULT, C8 TTL, C9 SETTINGS e C10 MV alterados ficaram verdes; S5 (Enum de chave) foi detectado, mas o apply não curou; fresh e migrado diferem só na ordem textual de SETTINGS. Falta: decidir manter o escopo documentado, ampliar o verify ou criar verificador separado. Não comprovado: CI.

### Linhagem

Linhagem: R5 de 30/09 (controles C7-C10, S5) → parecer DEC-25 com três opções → lane1-dec25 de 01/10 (MV intermediária verde após 034) → registro E23 → minuta P-DEC25 → #170 → decisão [ausente].

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-revalidated-fes-sources/infra__scripts__verify_ddl.py.excerpt.txt; fontes/batch-revalidated-fes-sources/r5-report-excerpt.md; fontes/batch-revalidated-fes-sources/lane1-dec25-report.md. Locadores e recorte: E23/#170; verify_ddl docstring/SOURCES:1–39, parser:114–135, mensagem195; R5 C7–C10/S5 e lane1. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: modificadores removidos antes da comparação. RELATO: quatro propriedades alteradas passando verde. DECISÃO PENDENTE: escopo. Nenhuma execução.

### Fluxo

Fluxo observado: DDL esperado —(remove modificadores)→ nome e tipo esperados; system.columns —(nome e tipo reais)→ comparação —(igual)→ verde, mesmo com DEFAULT/TTL/SETTINGS/MV divergentes. Proposto: verificador separado —(propriedades por critério)→ relatório por propriedade.

### Consequências e risco

Sem decisão, alguém pode usar o verde do verify_ddl como prova de que uma migração ou MV está correta. Ampliar sem critério pode criar vermelho falso em instalações legadas (ordem de SETTINGS). Confiança alta na leitura do código.

### Alternativas e recomendação

Recomendado: preservar ou ampliar conscientemente o escopo após decisão. O docstring já declara comparação por nome/tipo de sete tabelas; esclarecer a saída exactly e seus limites pode bastar. Checker separado para semântica de MV/TTL/DEFAULT/SETTINGS é alternativa se necessária, com critérios e controles próprios; nenhuma ampliação é decidida nesta revisão.

### Dependências e paralelismo

Independente de E22, mas a política de E22 pode exigir um verificador de MV; decidir os dois juntos na #170 é natural, não obrigatório. Sem dependência de CI para decidir.

### Plano e aceite propostos

Passos mínimos: (1) decisão; (2) se manter: docstring e saída do script dizendo "nome e tipo de sete tabelas"; (3) se ampliar: critério por propriedade, teste negativo para cada uma e tratamento da ordem de SETTINGS; (4) prova em fresh e migrado. Aceite: texto do verificador coerente com o que checa.

### Comunicação entre responsáveis

Para outro pod: "verify-ddl verde garante nomes e tipos de sete tabelas; não garante DEFAULT, TTL, SETTINGS nem a query do MV. Use-o como checagem de schema, não como prova de migração ou ingestão."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Ler verde como prova de query do MV ou de ingestão excederia o verificador; ampliá-lo sem critério pode reprovar ordem textual equivalente de SETTINGS. Que caso o teste ainda não cobre? DEFAULT, TTL, SETTINGS e query do MV não são comparados; o relato de MV intermediária verde não é uma nova execução nem defeito na comparação declarada. Como eu explicaria isso para outro pod? verify-ddl compara nomes e tipos das sete fontes; uma garantia operacional maior precisa outro critério, checker ou escopo explicitamente aprovado.

### Próxima ação e encerramento

Próxima ação: owner Infra (a confirmar) decide o escopo na #170. Entrada: verify_ddl.py e relatórios. Saída: decisão e ajuste textual mínimo. Encerramento: texto do verificador coerente e, se ampliado, testes negativos por propriedade.

<a id="item-225"></a>

## E24 — Alinhar seleção de tentativa no Engine offline e SQL

Frente: consumidores_tentativa_stage. Encaminhamento: agrupar_em_169_decidir_seletor_comum.

### Identidade e estado

E24 é um estudo/correção do Pod 2/Engine e Pod 3/Memory para alinhar a seleção de tentativa de stage entre o Engine offline e a SQL. Publicado (com S14 e S19) da minuta P-DEC23 como issue luanmorenommaciel/apex#169 em 2026-10-11 por gustocezar, aberta, sem assignee e sem comentários. Decisão: owners Engine/Serve/Memory/Front (DEC-23), a confirmar.

### Intenção e benefício

Problema: aggregate_events no Engine escolhe a tentativa por (stage_attempt, ts), enquanto STAGE_AGGREGATES_SQL rotula max(stage_attempt) e escolhe métricas por argMax(..., ts); com tentativas fora de ordem, o rótulo de uma tentativa pode vir com métricas de outra (C5/C6r: attempt 1 com p99 1098 offline contra p99 30000 na SQL). Público: quem compara diagnóstico offline com o do store, e Memory, que indexa histórico. Ganho: um seletor comum e documentado.

### Feito, faltante e não comprovado

Código lido confirma Engine offline (stage_attempt, ts)>=, SQL max(stage_attempt) com argMax de métricas por ts; Serve STAGES usa argMax de tentativa por ts, Console max(attempt)+argMax, e Memory usa ts. Lane3 relata C5/C6r com p99 1098 offline versus 30000 SQL e C9/C9r sensíveis à ordem da fixture. Falta decisão e teste integrado de paridade; caracterização histórica não deve ser descrita como inexistente.

### Linhagem

Linhagem: lane3-dec23-24 de 01/10 → registro E24 (decision_required, deps DEC-23 e S19) → minuta P-DEC23 (E24, S14, S19) → #169 (11/10) → caracterização [ausente] → decisão [ausente] → correção [ausente].

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/engine__src__apex_engine__clickhouse.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_mcp__ch.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/memory__src__apex_memory__clickhouse.py.txt; fontes/batch-revalidated-fes-sources/lane3-dec23-24-report.md. Locadores e recorte: E24/#169; Engine SQL:64–115/offline496–507; Serve STAGES/CONSOLE; Memory CTE; lane3 integral. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO estático: seletores divergentes nos quatro trechos de código citados. RELATO HISTÓRICO: cinco repetições em clickhouse-local e execução offline da lane3. Inferência condicionada: efeito real depende de dados/ordem; desempate observado não é contrato. DECISÃO PENDENTE: seleção, conflitos e compatibilidade.

### Fluxo

Fluxo observado: eventos por tentativa —(stage_attempt e ts)→ seleção no Engine offline (tupla) e na SQL (max + argMax por ts) —(tentativa e métricas)→ findings e memória —(rótulo de uma tentativa com métricas de outra quando fora de ordem)→ usuário.

### Consequências e risco

Sem decisão, sob retries fora de ordem o rótulo e os percentis podem divergir entre caminhos, e Memory pode indexar algo diferente do que o Engine diagnosticou. Risco possível com divergência sintética demonstrada; não medido em dados reais. Confiança alta no fato estático.

### Alternativas e recomendação

Recomendado: escolher como contrato "maior stage_attempt, desempate pelo ts mais recente dentro da tentativa" e aplicá-lo nos dois caminhos, com fixtures C1/C5/C6r/C9. Alternativas: "evento mais recente" puro (simples, mistura tentativas); seleção por tentativa bem-sucedida quando houver (exige dado que nem sempre existe). Mudança altera métricas históricas: avaliar migração.

### Dependências e paralelismo

Inventário e fixtures podem começar já; correções dependem da decisão. Não depende de #115 (identidade de execução SQL), que é outra chave. S19 (worst_p99_ms no Serve) e S14 (consultas legadas) são da mesma família e devem seguir a mesma decisão.

### Plano e aceite propostos

Passos mínimos: (1) teste de caracterização que rode C1/C5/C6r/C9 no Engine offline e na SQL e mostre a diferença; (2) decisão DEC-23; (3) mudanças atômicas por consumidor com o mesmo conjunto de fixtures; (4) controle de empate determinístico; (5) nota de compatibilidade de histórico. Aceite: paridade nas fixtures.

### Comunicação entre responsáveis

Para outro pod: "Engine offline e SQL escolhem a tentativa de stage de jeitos diferentes; com retries fora de ordem, o rótulo pode ser de uma tentativa e as métricas de outra. Precisamos de um seletor comum antes de corrigir."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Usar max(attempt) no rótulo e argMax(ts) nas métricas pode combinar duas linhas; escolher só ts mantém outro significado que precisa ser explícito. Que caso o teste ainda não cobre? A fixture histórica já caracteriza C5/C6r; falta paridade incorporada e decisão para C9/C9r sem depender da ordem de INSERT, além de emissão Spark real. Como eu explicaria isso para outro pod? A chave de tentativa e o seletor são independentes da atribuição de execução SQL da #115; a #169 decide qual linha representa cada stage.

### Próxima ação e encerramento

Próxima ação: owners dos consumidores (a confirmar) recebem a matriz de seletores e as fixtures. Entrada: #169 e relatório lane3. Saída: decisão DEC-23 registrada. Encerramento: decisão com plano de mudanças e paridade provada nas fixtures.

<a id="item-226"></a>

## S13 — Interface MCP read-only de system graph (#107)

Frente: serve_grafo_mcp. Encaminhamento: estudar_em_paralelo_implementacao_depende_106.

### Identidade e estado

S13 é o estudo do Pod 3/Serve para uma interface MCP read-only do grafo de sistema, representado pela issue luanmorenommaciel/apex#107 "[Study][Pod 3 / Serve] Define a read-only APEX system-graph MCP interface", aberta, sem assignee e sem comentários no snapshot. Owner a confirmar (Pod 3).

### Intenção e benefício

Problema: para saber qual lane possui um campo ou consome uma tabela, hoje é preciso ler código ou prosa; um agente MCP sem catálogo tende a inventar ownership. Público: usuários de editor/agente e Pods que precisam descobrir produtores/consumidores. Ganho: descoberta determinística de ownership com cada fato marcado por basis e proof_state.

### Feito, faltante e não comprovado

Feito (relato local): a seção #107 do relatório de 29/08 recomenda reusar o FastMCP com um recurso apex://system-graph e as ferramentas catalog_get(id) e catalog_trace(id, direction, relation, max_depth, limit), limite de 100 nós/200 arestas com sinal truncated, sem ClickHouse nem rede, e testes de enumeração, versão desconhecida, ID ausente e truncamento; inclui serve-mcp-contract.schema.json. Falta: reconciliar com a superfície atual de oito tools (o relatório fala em "quatro ferramentas de leitura atuais", base 847d7a0) e decisão. Não comprovado: implementação, que depende do schema da #106.

### Linhagem

Linhagem: seed S13 → issue #107 → estudo #106 em 847d7a0 → relatório de 29/08 com schema e exemplo MCP → camada de contexto de 10/10 → decisão [ausente] → implementação [ausente]. Elo ausente: vínculo público entre a #107 e o relatório local.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-revalidated-fes-sources/system-graph-REPORT.md; fontes/batch-revalidated-fes-sources/system-graph-serve-mcp-contract.schema.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_api__routes__diagnostics.py.txt. Locadores e recorte: S13/#107 integral; relatório e schema MCP de 29/08; oito entradas TOOL_ROUTES:53–62 na base. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: issue aberta sem decisão; oito tools na base (README:179-186). RELATO: estudo ready_offline e schema local. INFERÊNCIA: o desenho é compatível com a fronteira read-only atual, mas o texto precisa ser atualizado. DECISÃO PENDENTE: adotar/adiar (DEC-19). Sem execução.

### Fluxo

Fluxo proposto: manifesto estático do grafo —(versão conhecida)→ recurso apex://system-graph e tools catalog_get/catalog_trace —(fatos com basis/proof_state, BFS limitado)→ cliente MCP; LLM —(explica, não cria fatos)→ usuário. Nenhuma consulta ao ClickHouse no caminho.

### Consequências e risco

Sem a interface proposta, o estudo identifica risco de inferir ownership por prosa livre. Isso não prova que todo agente atual invente fatos nem ausência universal de outra ferramenta; a implementação dessa proposta não é demonstrada nos objetos lidos.

### Alternativas e recomendação

Recomendado: atualizar o desenho para as oito tools e levar à #107 uma proposta mínima (só catalog_get e o recurso, sem trace) como primeira entrega. Alternativas: adiar pós-v1 (aceitável, registrado); expor o grafo pela apex-api em vez de MCP (a #108 diz que o catálogo MCP é provedor opcional para a UI). Reversível.

### Dependências e paralelismo

Estudo paralelo a #106/#108/#109; implementação depende do schema aprovado da #106. Não depende de ClickHouse nem de #130. Não altera as oito tools existentes.

### Plano e aceite propostos

Passos mínimos de estudo: (1) diff do schema de 29/08 contra a superfície atual; (2) proposta de recorte mínimo; (3) casos de teste já listados no relatório; (4) decisão na #107. Para implementação futura: controle de que nenhuma tool nova acessa rede ou store e de que ID desconhecido retorna vazio tipado.

### Comunicação entre responsáveis

Para outro pod: "O grafo MCP proposto só lê um manifesto estático e devolve fatos com fonte e estado de prova; não muda as oito tools e não consulta o banco. Precisa de decisão e do schema da #106."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Um catálogo sem fonte/proof_state ou trace ilimitado poderia inventar autoridade e expandir respostas sem limite de recursos. Que caso o teste ainda não cobre? Schema e exemplos não foram executados; versão desconhecida, ID ausente, domínio e truncamento precisam dos controles previstos se a implementação for aprovada. Como eu explicaria isso para outro pod? O MCP proposto lê manifesto estático, com limites e proveniência; estudo pode avançar já, e implementação aguarda schema #106 e decisão.

### Próxima ação e encerramento

Próxima ação: Pod 3 (a confirmar) atualiza o desenho e pede decisão na #107. Entrada: relatório de 29/08 e schema #106. Saída: proposta mínima comentada na #107. Encerramento do estudo: decisão adotar/adiar registrada.

<a id="item-227"></a>

## S14 — Efeito das consultas legadas Serve/Memory (retry-safe, T26)

Frente: consumidores_tentativa_stage. Encaminhamento: agrupar_em_169_decidir_populacao_e_migracao.

### Identidade e estado

S14 é uma investigação do Pod 3+Memory+Verify sobre o efeito das consultas legadas retry-safe (seed S14, R2 T26). Agrupada na issue luanmorenommaciel/apex#169 (minuta P-DEC23, com E24 e S19), aberta, sem assignee e sem comentários. Decisões: DEC-23 (tentativa, owner Pod 3) e DEC-24 (população e migração de run_outcomes, Memory), a confirmar.

### Intenção e benefício

Problema: Engine usa as amostras de tarefas bem-sucedidas, mas Memory reduz por ts e lê percentis legados, e o Serve tem seleções próprias; numa fixture sintética, Memory inverte o vencedor A/B (A 119500 × B 129800 ms no legado; B 99500 ms bem-sucedido). Público: quem usa recall/memória para escolher a configuração que funcionou. Ganho: baselines de memória que não sejam poluídos por retries.

### Feito, faltante e não comprovado

Base: memory/src/apex_memory/clickhouse.py:48-58 define _LATEST_ATTEMPT_CTE com argMax(task_duration_p50_ms, ts) e argMax(task_duration_p99_ms, ts), sem successful_task_*; Verify já usa a população bem-sucedida (models.py:146-158, F20/#142). Falta: decisão de população e rótulo em run_outcomes, convenção de tentativa do Serve e eventual migração. Não comprovado: frequência em dados reais e emissão Spark de durações de tentativas FAILED/KILLED.

### Linhagem

Linhagem: drafts retry-safe de 31/08 (aguardavam #99, integrada em 14/09) → investigação NA-09 de 25/09 → TS25/TS26 e lanes A/B de 29/09 (casos C0-C8; run_outcomes sem rótulo de população; TTL 90 d em spark_events × 365 d em run_outcomes) → F20 cobre o Verify (#142) → minuta P-DEC23 → #169 → decisões [ausentes] → folhas Serve ts46a e Memory ts44 [ausentes].

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/memory__src__apex_memory__clickhouse.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/verify__src__apex_verify__models.py.txt; fontes/batch-revalidated-fes-sources/lane3-dec23-24-report.md. Locadores e recorte: S14/P-DEC23/#169; Memory CTE:44–104; Verify models128–170; lane3 §§3–8 e políticas de TTL como relato. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: Memory lê percentis legados por ts; Verify usa população bem-sucedida. RELATO: inversão A/B e casos C0-C8 em clickhouse-local sobre fixture. INFERÊNCIA: run_outcomes antigos não dizem qual população geraram, então misturar populações em comparação histórica é possível. DECISÃO PENDENTE: DEC-23 e DEC-24.

### Fluxo

Fluxo observado: spark_events —(argMax por ts, p50/p99 legados)→ Memory _LATEST_ATTEMPT_CTE —(run_outcomes sem rótulo de população)→ recall/compare —(vencedor A/B)→ usuário. Em paralelo: spark_events —(successful_task_* quando sample_count > 0)→ Verify e Engine.

### Consequências e risco

Sem decisão, a memória pode recomendar a configuração errada quando houver retries, e o histórico de 365 dias vai misturar linhas calculadas por populações diferentes. Risco possível com fixture discriminante; frequência real desconhecida. Confiança alta no fato estático.

### Alternativas e recomendação

Recomendado: decidir população bem-sucedida com fallback rotulado em Memory, acrescentar rótulo de população a run_outcomes daqui para frente e não reescrever histórico sem plano. Alternativas: recalcular histórico dentro do TTL de spark_events (90 d) e marcar o restante como legado; manter legado e documentar (barato, mantém o viés). Mudança de schema exige migração aditiva.

### Dependências e paralelismo

Decisão de rótulos/comparabilidade pode ser preparada em paralelo ao seletor, mas a mudança do indexador e sua fixture herdam a decisão DEC-23 sobre qual linha vence. Verify já seleciona successful-task quando disponível (F20), com resíduo p50=0 separado; não declarar toda a política Verify resolvida.

### Plano e aceite propostos

Passos mínimos: (1) matriz por consumidor (Engine, Serve, Memory, Verify) com população e seletor; (2) decisão DEC-24; (3) se mudar: migração aditiva com coluna de rótulo, fixture que reproduz a inversão A/B e falha na base, controle de job sem retries inalterado; (4) nota de compatibilidade de histórico. Aceite: fixture discriminante passa.

### Comunicação entre responsáveis

Para outro pod: "A memória ainda escolhe vencedores com percentis que incluem tentativas que falharam; o Verify já não. Precisamos decidir a população e como rotular o histórico antes de mudar SQL."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Misturar populações sem rótulo pode inverter o vencedor A/B como no relato sintético; recalcular tudo sem fonte preservada inventaria histórico. Que caso o teste ainda não cobre? A inversão e TTLs são relatos/código histórico da lane3; faltam migração/roundtrip do rótulo, comparabilidade do legado e emissão real de FAILED/KILLED. Como eu explicaria isso para outro pod? Memory ainda reduz métricas legadas por ts; população, tentativa e compatibilidade são eixos explícitos na #169, e Verify já tem seleção condicional.

### Próxima ação e encerramento

Próxima ação: owners Memory e Pod 3 (a confirmar) recebem a matriz e decidem DEC-24/DEC-23. Entrada: #169 e relatórios NA-09/lanes A/B. Saída: decisão registrada. Encerramento: decisão com plano de migração e fixture discriminante.

<a id="item-228"></a>

## S15 — F4.3 — narrar 'AQE fez X, sua config diz Y' a partir de job_conf

Frente: serve_explicabilidade_aqe. Encaminhamento: agrupar_em_177_estudar_narracao_job_conf_existe.

### Identidade e estado

S15 é uma feature pequena do Pod 3/Serve, F4.3: narrar "o AQE fez X, sua config diz Y" a partir de job_conf. Publicada da minuta P-S15 como issue luanmorenommaciel/apex#177 em 2026-10-11 por gustocezar, aberta, sem assignee e sem comentários. Decisão de produto: owner Pod 3 (DEC-22), a confirmar.

### Intenção e benefício

Problema: o Serve narra transições AQE sem cruzá-las com a configuração efetiva do job, então o usuário não distingue "o AQE decidiu sozinho" de "a sua config pediu isso". Público: quem lê o diagnóstico e decide mexer em configuração. Ganho: a frase mais acionável que o APEX consegue dizer sem mudar contrato, separando observação, hipótese e conselho.

### Feito, faltante e não comprovado

Base: JOB_CONF_SQL em serve/src/apex_mcp/ch.py:448 e ReadStore.job_conf em ch.py:1101 (vazio quando o jar não emitiu job_conf, documentado como ausência), rota /v1 em apex_api/routes/resources.py:106; diagnose.py não referencia job_conf. A razão da triagem ("serve/src não lê job_conf") descreve a a289e53 anterior à #129 e está desatualizada; o corpo publicado da #177 já corrige isso. Falta: decidir superfície e exemplos; implementar a narração. Não comprovado: narração com job_conf real.

### Linhagem

Linhagem: L4_PROPOSAL e SERVE-LEGS F4.3 → registro S15 (grep job_conf em serve/src = 0 na a289e53) → #129 porta JOB_CONF para o Serve (06/10) → minuta P-S15 → #177 (11/10) com a premissa corrigida → estudo [ausente] → decisão DEC-22 [ausente] → Task-Spec [ausente].

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_mcp__ch.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_mcp__diagnose.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_api__routes__resources.py.txt. Locadores e recorte: S15/#177; JOB_CONF_SQL:444–456 e ReadStore.job_conf:1101–1107; diagnose busca lexical; #115 corpo/comentário no snapshot. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: leitura de job_conf existe no Serve e na API; diagnose não a usa. INFERÊNCIA: a implementação é de narração, não de leitura. PROPOSTA: F4.3. DECISÃO PENDENTE: implementar/adiar/rejeitar e onde exibir. Nenhuma execução.

### Fluxo

Fluxo proposto: job_conf (Map allowlisted) —(JOB_CONF_SQL/ReadStore.job_conf)→ diagnose —(cruza com plan_transitions: tipo e escopo da execução)→ nota "AQE fez X; sua config diz Y; isto é observação, não causa" —(MCP e /v1)→ usuário. Hoje só os dois primeiros trechos existem, separadamente.

### Consequências e risco

Risco de implementação: atribuir a um stage uma decisão de outra execução sem vínculo inequívoco. A #115 já tem resolver/casos históricos; sua existência não prova integração no caminho narrativo do Serve. Não há incidente nem mensuração do benefício nesta revisão.

### Alternativas e recomendação

Recomendado: estudo curto com três exemplos (config presente e coerente, config ausente, config que contradiz a decisão) e frases no escopo da execução. Alternativas: narrar só no Front (mais simples para UI, duplica lógica); adiar até o mapa execução→stage (mais preciso, mais lento). Reversível.

### Dependências e paralelismo

Pode estudar exemplos já, em paralelo à #115. Afirmação por stage requer vínculo efetivamente integrado e sem ambiguidade no consumidor; não basta a existência de helper, nem é necessário declarar que todo mapa inexiste. job_conf já está acessível ao Serve/API.

### Plano e aceite propostos

Passos mínimos: (1) três exemplos com job_conf sintético; (2) texto por caso, com ausência explícita; (3) decisão DEC-22; (4) se implementar: teste que mostra a frase com config presente, a ausência sem inventar default e controle de que nenhuma frase cita stage sem vínculo. Aceite: exemplos aprovados e testes.

### Comunicação entre responsáveis

Para outro pod: o Serve já lê job_conf; falta escolher narração que cruze configuração e AQE sem defaults ou causalidade inventados, usando somente escopo e vínculos comprovados no consumidor.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Tratar chave ausente como default inventaria configuração; projetar decisão AQE de execução em stage sem vínculo inequívoco atribuiria evidência ao lugar errado. Que caso o teste ainda não cobre? Não há prova de narração com job_conf real; o plano precisa chave ausente e captura indisponível como casos distintos, além de config presente. Como eu explicaria isso para outro pod? Ler job_conf já existe; narrar com ele exige separar configuração capturada, decisão AQE observada e inferência, preservando o escopo comprovado.

### Próxima ação e encerramento

Próxima ação: Pod 3 (a confirmar) prepara os três exemplos na #177. Entrada: JOB_CONF_SQL e notas AQE de diagnose. Saída: exemplos e pedido de decisão. Encerramento: decisão implementar/adiar/rejeitar registrada.

<a id="item-229"></a>

## S16 — Serve renderiza delta medido abaixo do piso ou sem piso

Frente: serve_piso_ruido. Encaminhamento: encerrar_prs_integradas_residuo_igualdade_em_117.

### Identidade e estado

S16 é uma correção de regra ratificada do Pod 3/Serve: não narrar delta medido abaixo do piso ou sem piso. Implementada pela PR luanmorenommaciel/apex#135 "fix(serve): withhold unresolved replay deltas" (head 474284c, merge 1a5900e em 06/10) e complementada pela #144 (piso inválido, S21). Resíduo de igualdade em #117 (DEC-05). Sem assignee.

### Intenção e benefício

Problema: build_verdict escrevia "Replayed: measured X%" mesmo quando |Δ| < piso ou piso NULL, violando a regra 2 do CONTRACT.md ("no consumer may render the number"). Público: quem lê o veredito de verificação no MCP/API. Ganho: o Serve deixa de citar magnitude que o piso não sustenta.

### Feito, faltante e não comprovado

Base: _replay_measurement em diagnose.py:1351-1372 devolve "noise floor was not measured" para piso NULL, "invalid noise floor" para piso inválido e "effect below the baseline arm's … noise floor — magnitude not resolvable" quando abs(delta) < piso; só então escreve "measured". Resíduo confirmado estaticamente: na igualdade abs(delta) = piso a narração reporta magnitude, enquanto a projeção FIX_VERIFICATION_SQL (ch.py:426-431 e front queries.ts:295-299) classifica a mesma linha como unresolved (<=). Não comprovado: CI hospedada e revisão formal.

### Linhagem

Linhagem: verify-floor-contract §5 → commits 3c889f8 e 474284c na branch codex/serve-floor-narration → PR #135 (base a289e53) → testes contra a main falhando nos quatro casos abaixo/NULL (relato) → 11 check-runs sem steps (run 36092331624) → merge 1a5900e; #144 empilhada (82be2e2) → merge 06/10 → resíduo de igualdade C32 em #117. Sem elo ausente para o escopo entregue.

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_mcp__diagnose.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_mcp__ch.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/front__src__data__queries.ts.txt. Locadores e recorte: S16/#135 e #144; diagnose:1351–1376; projeções ch412–442 e queries282–312. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: retenção abaixo/NULL/inválido na narração; comparação estrita na narração e não estrita na projeção. RELATO: testes discriminantes do autor. DECISÃO PENDENTE: igualdade (H-1/DEC-05 na #117). Sem CI útil e sem runtime.

### Fluxo

Fluxos lidos: mesma linha → narração _replay_measurement (< piso retém magnitude; = piso relata) e projeção SQL (<= piso unresolved; > certifica). Isso confirma divergência na igualdade para pisos válidos. Há outra diferença para piso inválido (S21); não se afirma que igualdade seja a única divergência de todo consumidor.

### Consequências e risco

Com delta exatamente igual a piso válido, os dois predicados podem dar rótulos diferentes; frequência não foi medida, logo não é classificada como rara. Inconsistência estática não demonstra incidente persistido.

### Alternativas e recomendação

Recomendado: encerrar S16 e manter a igualdade no contrato #117, decidindo uma única comparação para todos os consumidores. Alternativas: adotar estrito (>) como a projeção para certificar e (<=) para não resolvível em toda parte (coerente com a projeção atual); ou o contrário, ajustando a projeção. Diferença de uma linha em cada consumidor; reversível.

### Dependências e paralelismo

Encerrar S16 não depende de nada. A decisão de igualdade é parte de DEC-05/#117 e afeta Serve, Front e Verify ao mesmo tempo; pode ser decidida em paralelo às demais folhas da #117.

### Plano e aceite propostos

Condição de não ação neste ID. Passo mínimo para o resíduo (na #117): tabela de casos abaixo/igual/acima com resultado esperado por consumidor e um teste de paridade que falhe hoje na igualdade. Reabrir S16 só se a narração voltar a citar magnitude abaixo do piso.

### Comunicação entre responsáveis

Para outro pod: "O Serve não narra mais delta abaixo do piso ou sem piso (#135). Na igualdade exata, a narração e a Console ainda discordam; isso é decisão do contrato na #117."

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Alterar só um comparador preservaria respostas diferentes para a mesma linha; escolher > ou >= exige uma política comum de fronteira. Que caso o teste ainda não cobre? Não se executou a paridade de narração e SQL nos casos abaixo/igual/acima, nem se decidiu o significado de piso zero. Como eu explicaria isso para outro pod? A #135 reteve magnitude abaixo/sem piso; igualdade continua uma diferença estática no contrato #117, sem incidente demonstrado.

### Próxima ação e encerramento

Próxima ação: confirmar encerramento de S16 e anexar à #117 o caso de igualdade com as duas linhas de código. Owner: Pod 3 e owner do contrato (a confirmar). Entrada: diagnose.py:1365 e ch.py:429. Saída: linha S16 encerrada com resíduo documentado. Encerramento: imediato para S16.

<a id="item-230"></a>

## S17 — Serve suggest_fix sem receita para TAIL_OUTLIER

Frente: consumidores_tail_outlier. Encaminhamento: agrupar_em_166_parte_serve.

### Identidade e estado

S17 é o recorte Serve do follow-up de TAIL_OUTLIER (Pod 3/Serve, origem revisão B-4 da #127), agrupado na issue luanmorenommaciel/apex#166 (minuta P-TAIL), aberta, assignee gustocezar como reserva de estudo. Owner da decisão de receita: Pod 3 (a confirmar).

### Intenção e benefício

Problema: suggest_fix converte o tipo do finding em sintoma por substring; TAIL_OUTLIER não contém SKEW, SPILL, SHUFFLE, OOM, MEMORY nem GC, cai em "unknown" e recebe a receita genérica spark.sql.adaptive.enabled=true, que não decorre do finding. Público: quem recebe um diff de configuração sugerido. Ganho: sugestão coerente com o watcher, ou explicação honesta de que não há receita.

### Feito, faltante e não comprovado

Código: TAIL_OUTLIER vira unknown e seleciona fallback adaptive.enabled=true. Se confiança < min_confidence, proposed_config/diff/pr_body ficam vazios; com confiança suficiente e recusa Verify, config permanece mas diff/pr_body ficam vazios; sem recusa, podem ser emitidos. O watcher atual usa 0.72 e a rota default 0.75, portanto não se pode dizer que todo TAIL_OUTLIER atual entrega diff. Faltam política e testes dos limiares escolhidos.

### Linhagem

Linhagem: revisão B-4 da #127 → registro S17 (study_ready, depende do merge #127; referência diagnose.py:1738-1748 na a289e53, deslocada para 1765 na base) → merge #127 → minuta P-TAIL → #166 → estudo C2 com 12 casos e 16 fixtures declarativas (11/10) → decisão [ausente] → testes [ausentes].

### Fontes e corte

Fontes consultadas: fontes/batch-revalidated-fes-sources/selected-register-matrix-publication.json; fontes/batch-revalidated-fes-sources/selected-public-snapshot.json; fontes/batch-revalidated-fes-sources/code-integrity-reconfirmed.json; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/serve__src__apex_mcp__diagnose.py.txt; fontes/batch-claude-registro-propostas-sources/claude/fontes/codigo-c3c3ea3/engine__src__apex_engine__watchers__tail_outlier.py.txt. Locadores e recorte: S17/#166 comentário integral; diagnose1685–1775; tail_outlier.py confiança0.72. O registro conserva relatos históricos; não é recibo de nova execução.

### Classe e limite da evidência

FATO OBSERVADO: mapeamento por substring e fallback genérico. RELATO: matriz de 12 combinações tipo × confiança × recusa com cobertura parcial nos testes existentes. DECISÃO PENDENTE: tratamento de unknown sem recusa. Sem execução.

### Fluxo

Fluxo condicionado: tipo selecionado → unknown → receita genérica → comparação de confiança e recusa. Abaixo do limiar: config/diff/body vazios. Acima ou igual com recusa: config visível, diff/body vazios. Acima ou igual sem recusa: diff/body propostos. Não há aplicação automática.

### Consequências e risco

Sem decisão, um usuário pode receber "ligue AQE" como correção de uma cauda que nada tem a ver com AQE; o risco é aplicar uma mudança irrelevante, não um dano grave, e o próprio diff exige aprovação humana. Confiança alta no fato estático.

### Alternativas e recomendação

Recomendado: tratar unknown com explicação sem receita (proposed_config vazio e nota dizendo que não há correção sustentada) e não criar receita para TAIL_OUTLIER por enquanto. Alternativas: receita específica (exige evidência que o watcher não fornece); manter fallback com aviso (barato, continua sugerindo algo sem base). Reversível.

### Dependências e paralelismo

Depende só da decisão comum da #166 sobre tipos sem receita; toca apenas o Serve e pode correr em paralelo a F13 (Front) e F18 (Verify). Não depende do piso absoluto da #168 nem do gate da #123.

### Plano e aceite propostos

Passos mínimos: (1) decisão para unknown e TAIL_OUTLIER; (2) mudança no ramo de fallback; (3) testes para TAIL_OUTLIER abaixo, igual e acima de 0,75, com e sem recusa, verificando proposed_config, diff e PR body separadamente; (4) controles SKEW_ON_JOIN e RETRY_PRESSURE inalterados. Aceite: nenhum diff de configuração para tipo sem receita.

### Comunicação entre responsáveis

Para outro pod: o fallback de tipo desconhecido escolhe AQE; ele só vira diff quando confiança e recusa permitem. O TAIL atual 0.72 fica abaixo do default 0.75, e a #166 deve decidir resposta sem receita sustentada.

### Perguntas de revisão

O que quebraria se fizéssemos diferente? Mapear unknown para receita AQE sem evidência pode oferecer mudança irrelevante quando o limiar permitir; remover só o diff sem examinar config/body deixaria saídas inconsistentes. Que caso o teste ainda não cobre? As fixtures são declarativas; faltam execuções abaixo/igual/acima do limiar e com recusa, verificando config, diff e body separadamente. Como eu explicaria isso para outro pod? Há fallback genérico e duas proteções independentes; a política para tipos sem receita precisa ser explícita, preservando a confiança atual do watcher.

### Próxima ação e encerramento

Próxima ação: Pod 3 (a confirmar) registra na #166 a política para unknown. Entrada: matriz C2 e fixtures. Saída: PR do Serve com os testes listados. Encerramento: critério da #166 correspondente marcado com evidência.

