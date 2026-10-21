# Relação dos 93 PRs revalidados no escopo declarado

A captura é de 19/10/2026 (02:01–02:02 UTC de 20/10). Commits/arquivos e paginação foram conferidos. Os heads aqui são os da captura; nossas correções posteriores têm commits próprios e não alteram código de produto. “Encerrada” não é sinônimo de merge.

## 15 PRs abertas

| PR | Autor | Head capturado | Arquivos / commits | Reconciliação |
|---|---|---|---|---|
| [#155](https://github.com/luanmorenommaciel/apex/pull/155) | gustocezar | `561b27e7d1` | 1 / 1 | Guarda de duas queries versus preflight; 11 checks failure no corte não demonstram falha de asserção. Nenhum requisito adicional inferido. |
| [#157](https://github.com/luanmorenommaciel/apex/pull/157) | gustocezar | `a3ed9723af` | 2 / 1 | Oito tools; comparação de payloads sem normalização de campos; segundo arquivo só MCP. Nomes dos guias corrigidos. |
| [#158](https://github.com/luanmorenommaciel/apex/pull/158) | gustocezar | `514b0e573b` | 1 / 1 | Guarda estática confidence_score DESC/finding_id ASC; adaptação condicional com a #182; conflito textual não demonstrado. |
| [#159](https://github.com/luanmorenommaciel/apex/pull/159) | gustocezar | `1685f8ac91` | 4 / 3 | Provas F1c no corpo distinguidas do checkpoint histórico de 519 testes em VALIDATION; complemento documental, sem nova execução. |
| [#161](https://github.com/luanmorenommaciel/apex/pull/161) | gustocezar | `d61eab85f2` | 1 / 1 | !cancelled() e outcomes de setup/root preservados. Sem always() geral ou execução negativa nova. |
| [#162](https://github.com/luanmorenommaciel/apex/pull/162) | gustocezar | `3955f9de34` | 2 / 1 | __version__ de 0.3.0→0.1.0; default de Verdict preexistente de 0.1.0, sem migração de linhas. |
| [#163](https://github.com/luanmorenommaciel/apex/pull/163) | gustocezar | `9a7e4c1a77` | 1 / 1 | Plan_json com findings vazio; depende de helpers da #157; nenhum check no corte. Não demonstra mistura de resultados/top_k ou store real. |
| [#164](https://github.com/luanmorenommaciel/apex/pull/164) | gustocezar | `5d42763aaf` | 3 / 3 | README/CI/contrato/coluna runtime: reaproveitado na reconciliação L1 para evitar tarefa duplicada. |
| [#182](https://github.com/luanmorenommaciel/apex/pull/182) | agmarcastro | `74fdb07918` | 65 / 59 | Implementação API-only/hardening/cache/a11y e provas do Agmar reconhecidas; R1/R2 da combinação mantidos; E2E histórico e relato nginx separados por alcance. |
| [#183](https://github.com/luanmorenommaciel/apex/pull/183) | gustocezar | `cd879dbb01` | 34 / 3 | Nomes MCP corrigidos; prova live/E2E existente reconhecida; matriz L1 referencia a #164; contagens/cortes esclarecidos. |
| [#184](https://github.com/luanmorenommaciel/apex/pull/184) | gustocezar | `0b1cb7b54d` | 3 / 1 | Três ajustes sintáticos YAML; recibos de checks separados de aceite/governança; sem mudança de estado Task-Spec. |
| [#185](https://github.com/luanmorenommaciel/apex/pull/185) | agmarcastro | `a5c2ca45bd` | 38 / 25 | Implementação DEV/S3/runners/fingerprint do Agmar reconhecida; wrapper/sbt conferidos; preservar critérios específicos das issues relacionadas. |
| [#186](https://github.com/luanmorenommaciel/apex/pull/186) | gustocezar | `9a3bb5e4bd` | 68 / 2 | Estudo dos 525 IDs: fichas, derivados e referências corrigidos; nova relação93 PRs com limites por linha. Não representa 525 aceites funcionais. |
| [#187](https://github.com/luanmorenommaciel/apex/pull/187) | gustocezar | `3f36b8f58b` | 17 / 1 | Plano da #172 passa a conferir provas existentes; catálogo/base/comentários/checks e organização corrigidos. |
| [#189](https://github.com/luanmorenommaciel/apex/pull/189) | gustocezar | `fa54909404` | 17 / 1 | #54 reclassificada como encerrada sem merge;#185 reconhecida; organização/catálogos/apresentação corrigidos. |

## 78 PRs encerradas

Escopo comum: fontes documentais completas descritas no JSON e campos selecionados das fichas. Nenhuma releitura integral de código/ambiente histórico é alegada. As fichas originais mantêm suas próprias fontes e cortes.

| PR | Autor | Estado da PR | Resultado documental |
|---|---|---|---|
| [#13](https://github.com/luanmorenommaciel/apex/pull/13) | antonylucas | Encerrada sem merge | Sem divergência material no recorte documental comparado. |
| [#14](https://github.com/luanmorenommaciel/apex/pull/14) | sidymar | Encerrada sem merge | Sem divergência material no recorte documental comparado. |
| [#44](https://github.com/luanmorenommaciel/apex/pull/44) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#45](https://github.com/luanmorenommaciel/apex/pull/45) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#46](https://github.com/luanmorenommaciel/apex/pull/46) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#47](https://github.com/luanmorenommaciel/apex/pull/47) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#48](https://github.com/luanmorenommaciel/apex/pull/48) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#49](https://github.com/luanmorenommaciel/apex/pull/49) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#50](https://github.com/luanmorenommaciel/apex/pull/50) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#51](https://github.com/luanmorenommaciel/apex/pull/51) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#52](https://github.com/luanmorenommaciel/apex/pull/52) | gustocezar | Encerrada sem merge | Correção ou complemento documental incorporado. Corrigida nossa camada de leitura para reconhecer o comentário de fechamento; registro original preservado. |
| [#53](https://github.com/luanmorenommaciel/apex/pull/53) | gustocezar | Encerrada sem merge | Correção ou complemento documental incorporado. Corrigida nossa camada de leitura para reconhecer o comentário de fechamento; registro original preservado. |
| [#54](https://github.com/luanmorenommaciel/apex/pull/54) | gustocezar | Encerrada sem merge | Correção ou complemento documental incorporado. Corrigida nossa camada e sua apresentação como encerrada sem merge. |
| [#57](https://github.com/luanmorenommaciel/apex/pull/57) | luanmorenommaciel | Integrada no alvo da época | Correção ou complemento documental incorporado. Corrigida a atribuição dos 54 commits: 36 Luan, 10 Augusto Cezar, 8 merges com autor gustocezar. |
| [#66](https://github.com/luanmorenommaciel/apex/pull/66) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#67](https://github.com/luanmorenommaciel/apex/pull/67) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#68](https://github.com/luanmorenommaciel/apex/pull/68) | gustocezar | Integrada no alvo da época | Conferência documental com limite específico. |
| [#69](https://github.com/luanmorenommaciel/apex/pull/69) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#70](https://github.com/luanmorenommaciel/apex/pull/70) | gustocezar | Integrada no alvo da época | Correção ou complemento documental incorporado. Acrescentados relatos 94 offline/8 integração e composição separada de cinco mudanças; sem nova execução. |
| [#74](https://github.com/luanmorenommaciel/apex/pull/74) | gustocezar | Integrada no alvo da época | Correção ou complemento documental incorporado. Menção à #81 distinguida da camada editorial posterior; não atribuída ao texto original. |
| [#75](https://github.com/luanmorenommaciel/apex/pull/75) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#76](https://github.com/luanmorenommaciel/apex/pull/76) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#77](https://github.com/luanmorenommaciel/apex/pull/77) | JaymeNeto | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#79](https://github.com/luanmorenommaciel/apex/pull/79) | sidymar | Integrada no alvo da época | Correção ou complemento documental incorporado. Acrescentados resultados relatados 102 Serve/DoD 23 e gate/accept locais; sem novo aceite. |
| [#80](https://github.com/luanmorenommaciel/apex/pull/80) | luanmorenommaciel | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#81](https://github.com/luanmorenommaciel/apex/pull/81) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#82](https://github.com/luanmorenommaciel/apex/pull/82) | sidymar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#83](https://github.com/luanmorenommaciel/apex/pull/83) | sidymar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#84](https://github.com/luanmorenommaciel/apex/pull/84) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#85](https://github.com/luanmorenommaciel/apex/pull/85) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#86](https://github.com/luanmorenommaciel/apex/pull/86) | sidymar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#87](https://github.com/luanmorenommaciel/apex/pull/87) | sidymar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#88](https://github.com/luanmorenommaciel/apex/pull/88) | sidymar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#89](https://github.com/luanmorenommaciel/apex/pull/89) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#91](https://github.com/luanmorenommaciel/apex/pull/91) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#92](https://github.com/luanmorenommaciel/apex/pull/92) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#93](https://github.com/luanmorenommaciel/apex/pull/93) | gustocezar | Encerrada sem merge | Sem divergência material no recorte documental comparado. |
| [#94](https://github.com/luanmorenommaciel/apex/pull/94) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#96](https://github.com/luanmorenommaciel/apex/pull/96) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#97](https://github.com/luanmorenommaciel/apex/pull/97) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#98](https://github.com/luanmorenommaciel/apex/pull/98) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#99](https://github.com/luanmorenommaciel/apex/pull/99) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#100](https://github.com/luanmorenommaciel/apex/pull/100) | agmarcastro | Integrada no alvo da época | Correção ou complemento documental incorporado. Precisão dos commits substantivos de Augusto Silva; PR e resposta pública permanecem de Agmar. |
| [#101](https://github.com/luanmorenommaciel/apex/pull/101) | sidymar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#110](https://github.com/luanmorenommaciel/apex/pull/110) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#111](https://github.com/luanmorenommaciel/apex/pull/111) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#118](https://github.com/luanmorenommaciel/apex/pull/118) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#119](https://github.com/luanmorenommaciel/apex/pull/119) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#120](https://github.com/luanmorenommaciel/apex/pull/120) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#121](https://github.com/luanmorenommaciel/apex/pull/121) | luanmorenommaciel | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#126](https://github.com/luanmorenommaciel/apex/pull/126) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#127](https://github.com/luanmorenommaciel/apex/pull/127) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#128](https://github.com/luanmorenommaciel/apex/pull/128) | gustocezar | Integrada no alvo da época | Correção ou complemento documental incorporado. Precisão de nomes nos commits; autoria mista já estava preservada. |
| [#129](https://github.com/luanmorenommaciel/apex/pull/129) | sidymar | Integrada no alvo da época | Correção ou complemento documental incorporado. Reconhecidas correções c71c2e4 de Sidymar antes de fab6620 e relato 289 Serve/130 Front, distinto de 275 intermediários. |
| [#131](https://github.com/luanmorenommaciel/apex/pull/131) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#132](https://github.com/luanmorenommaciel/apex/pull/132) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#133](https://github.com/luanmorenommaciel/apex/pull/133) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#134](https://github.com/luanmorenommaciel/apex/pull/134) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#135](https://github.com/luanmorenommaciel/apex/pull/135) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#136](https://github.com/luanmorenommaciel/apex/pull/136) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#137](https://github.com/luanmorenommaciel/apex/pull/137) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#138](https://github.com/luanmorenommaciel/apex/pull/138) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#139](https://github.com/luanmorenommaciel/apex/pull/139) | gustocezar | Integrada no alvo da época | Correção ou complemento documental incorporado. Fonte esclarecida: diff lido não é leitura integral do guard/DDL na main atual. |
| [#140](https://github.com/luanmorenommaciel/apex/pull/140) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#141](https://github.com/luanmorenommaciel/apex/pull/141) | gustocezar | Integrada no alvo da época | Correção ou complemento documental incorporado. Corrigida inclusão indevida de ADR-004 na descrição do diff: a PR acrescenta ADR-001/002/003; árvore posterior separada. |
| [#142](https://github.com/luanmorenommaciel/apex/pull/142) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#143](https://github.com/luanmorenommaciel/apex/pull/143) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#144](https://github.com/luanmorenommaciel/apex/pull/144) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#145](https://github.com/luanmorenommaciel/apex/pull/145) | gustocezar | Integrada no alvo da época | Correção ou complemento documental incorporado. Fonte esclarecida: leitura do diff de models/replay/testes, sem afirmar leitura integral atual da main. |
| [#146](https://github.com/luanmorenommaciel/apex/pull/146) | gustocezar | Integrada no alvo da época | Correção ou complemento documental incorporado. Precisado o nome de autor do commit: Augusto Cezar. |
| [#147](https://github.com/luanmorenommaciel/apex/pull/147) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#148](https://github.com/luanmorenommaciel/apex/pull/148) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#149](https://github.com/luanmorenommaciel/apex/pull/149) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#150](https://github.com/luanmorenommaciel/apex/pull/150) | gustocezar | Integrada no alvo da época | Correção ou complemento documental incorporado. Fonte esclarecida: diff de testes de fronteira da API; leitura integral da main separada. |
| [#151](https://github.com/luanmorenommaciel/apex/pull/151) | gustocezar | Integrada no alvo da época | Sem divergência material no recorte documental comparado. |
| [#152](https://github.com/luanmorenommaciel/apex/pull/152) | antonylucas | Integrada no alvo da época | Correção ou complemento documental incorporado. Limite esclarecido: README/lista de arquivos inspecionados; deck integral não foi revisto nesta rodada. |
| [#153](https://github.com/luanmorenommaciel/apex/pull/153) | agmarcastro | Integrada no alvo da época | Correção ou complemento documental incorporado. Precisados 13 commits/11 trailers Task, leitura estática do E2E e relato histórico de aviso job_conf. |
| [#160](https://github.com/luanmorenommaciel/apex/pull/160) | luanmorenommaciel | Integrada no alvo da época | Correção ou complemento documental incorporado. Fonte esclarecida: diff dos workflows não é consulta de toda a configuração atual nem execução. |
