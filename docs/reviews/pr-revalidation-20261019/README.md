# Revalidação das contribuições, provas e publicações APEX

A revisão corrigiu a síntese que podia fazer trabalho já realizado parecer pendente. A contribuição e as provas apresentadas pelo Agmar nas **#182/#185**, além do E2E histórico da **#153**, foram confrontadas com as nossas publicações. As correções se limitam aos nossos textos, catálogos e fichas; não alteram código de produto ou PRs de outros autores.

## O que foi corrigido

- Reconhecimento da execução live de refused_count, gate 17/17, testes locais e E2E já relatados. A próxima ação da #172 começa por conferir/reaproveitar provas existentes e identificar somente eventual complemento.
- Três nomes MCP nos guias: **analyze_run, compare_runs e recall_similar_runs**. Reaproveitamento da #164 na matriz L1, sem propor outra tarefa para o mesmo ajuste de README.
- Atribuição dos 54 commits da #57: 36 com nome de autor Luan Moreno, 10 Augusto Cezar e 8 merges com autor gustocezar. A PR continua autoria de Luan.
- Justificativa das #52–#54: os comentários de fechamento existem. Corrigidas somente nossas camadas de leitura, preservando o registro original. #54 foi retirada da apresentação como entrega integrada.
- Provas relatadas complementadas nas fichas #70/#79; distinção entre texto original e nossa camada editorial na #74. #157 compara payloads sem normalizar campos. #159 tem evidência F1c posterior no corpo, distinta do checkpoint histórico de 519 testes em VALIDATION.
- #129: reconhecidas as correções de Sidymar antes de fab6620 e a contagem final relatada de 289 Serve, distinta dos 275 intermediários. #141: corrigida a afirmação de ADR-004 no diff; o patch acrescenta ADR-001/002/003.
- #100: contribuição principal de Agmar e commits específicos de Augusto distinguidos; #153: 13 commits, 11 com trailers de Task, com fonte do E2E e aviso histórico de job_conf.
- Organização, legibilidade e catálogos dos Pods 1/2: base SHA, comentários de coordenação, checks da #184 e cortes de contagem esclarecidos.

## Cobertura e limites

Foram inventariados **93 PRs:15 abertos e78 encerrados**. A coleta paginada teve 573 operações sem erro; os totais de arquivos e commits conferem com os objetos consultados. As fontes incluem corpo, conversas, reviews/inline e mensagens de commits, não apenas títulos ou resumos.

Os patches das duas PRs abertas do Agmar e das oito PRs técnicas abertas foram considerados integralmente, com conteúdo adicional selecionado quando necessário. Os pacotes documentais foram reconciliados por conteúdo/catálogo/estrutura; não se alega releitura linha a linha de todo pacote massivo. Nos 78 PRs históricos, o confronto desta rodada usa fontes documentais e campos 3/4/5/6/10/14 das fichas; **não é code review histórica nem nova execução de CI/runtime**.

[Consultar os93 PRs, o resultado e o alcance de cada linha](PRS-93.md). [Relação estruturada com fontes públicas e limites](PRS-93.json).

A contagem dos 525 IDs originais permanece inalterada. “Documentado”, “implementado na branch”, “integrado”, “relatado como testado” e “aceito pelo time” continuam estados distintos. O relatório não promete ausência absoluta de omissões nem concede aprovação funcional.

## O que segue para discussão técnica

Revisão humana das PRs; escolha e validação da combinação #158/#159/#182; decisão específica sobre Ask/token e critérios residuais de #172; conferência das interfaces #185 com os trackers existentes. Os complementos de prova devem partir dos recibos já apresentados, sem criar bloqueio global por ausência de reprodução nesta auditoria.

Entradas da discussão: [Pod3/#181](https://github.com/luanmorenommaciel/apex/issues/181), [Pod1/#188](https://github.com/luanmorenommaciel/apex/issues/188), [Pod2/#190](https://github.com/luanmorenommaciel/apex/issues/190). Esta é a visão documental de Augusto para o time, sem redefinir ownership, prioridades ou autoridade dos colaboradores.

## Reconferência de fechamento

Inventário reconferido em 20/10/2026 às 07:23 (São Paulo): 93 PRs, 15 abertos; main continua `c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874`. Os heads de produto e os corpos originais permanecem os da captura; as diferenças detectadas correspondem às nossas correções documentais. Os heads dos pacotes documentais mudam ao publicar essas correções e não certificam uma nova execução de testes.

Comentários, reviews e checks dos 15 abertos também foram reconsultados em 20/10: #182 continua com 3 checks verdes/zero reviews e #185 com 4 checks verdes/zero reviews; os registros estruturados guardam o SHA e o instante. Isso não converte prova local do autor em reprodução independente.
