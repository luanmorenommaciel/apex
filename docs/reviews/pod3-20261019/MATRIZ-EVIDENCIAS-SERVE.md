# Evidências do Serve: superfície, caso, árvore e lacuna

Consolidação documental em 19/10/2026. Nenhuma prova nova de produto foi executada nesta etapa. Registro principal: [#156](https://github.com/luanmorenommaciel/apex/issues/156); experiência HTTP no navegador: [#172](https://github.com/luanmorenommaciel/apex/issues/172). Para cada execução futura, registrar comando/run, árvore completa, versões, configuração sem segredo, resultado e limite.

## Provas preservadas

| Objeto / caso | Tipo de prova e resultado registrado | Revisão / origem | Limite e próximo passo |
|---|---|---|---|
| #157: MCP versus HTTP com argumentos iguais; positivo, ausência e store vazio conforme casos do patch | MCP em processo / HTTP TestClient; código dos testes e 11 checks verdes individuais em 09/10 | `a3ed972`, [#157](https://github.com/luanmorenommaciel/apex/pull/157) | Não é stdio, HTTP real, ClickHouse real ou navegador; revisão humana pendente no snapshot |
| #157: mesmos argumentos em store populado versus vazio | Controle adicional MCP em processo; comparação populado/vazio por tool | `a3ed972`, arquivo `test_tool_transport_parity_same_args.py` na #157 | Este controle específico não compara HTTP; não confundir com a paridade dos outros testes |
| #158: ordenação dos findings | Regressão SQL e 11 checks verdes individuais | `514b0e5`, [#158](https://github.com/luanmorenommaciel/apex/pull/158) | Ordenação por confidence DESC e finding_id ASC; manter fixtures e árvore na conferência |
| #159: gate de findings da Console | Controles de paridade/malformado/empate/limpeza; 11 checks verdes individuais | `1685f8a`, [#159](https://github.com/luanmorenommaciel/apex/pull/159) | Escreve em store no modo padrão e limpa por job_id próprio; não transferir propriedades de outro gate/blob |
| #163: `search_kb` positivo com `plan_json` | Três testes em processo adicionais; sem checks no head no snapshot | `9a7e4c1`, base #157, [#163](https://github.com/luanmorenommaciel/apex/pull/163) | Depende de helper da #157; reposicionar/validar a árvore acordada; não declarar prova real desse positivo |
| Combinação #157/#158/#159 | 572 testes locais registrados | árvore `19e61b74e9ae4721b6c7263ed900aa6fd99709f4`, recibo completo na #156 | Não é CI da combinação nem prova da futura main |
| G1 real CLI/API/ClickHouse | 19 PASS / 0 FAIL / 0 NOT_EXERCISED registrados | gate blob `3e0b3bbe01cd181cdac4b3295f14118a5db70921`, fonte #156 | Não representa todo gate posterior, todo cenário, navegador ou Spark/Collector |
| Oito tools por MCP stdio/HTTP reais | Positivos/ausência/indisponibilidade no escopo descrito na #156 | recibos históricos completos na #156 | Cobertura não universal por parâmetro; não inclui positivo `plan_json` nem todo blob de gate |
| #129 em 23/09 | Relato de 40 focados API/console, 275 Serve, 130 Front e build | relato histórico do autor; #129 foi integrada depois | Não somar suítes sobrepostas; não reapresentar como resultado desta etapa |
| nginx/imagem/browser | Lacuna de validação delimitada | #172 | Provar navegação e estados data/empty/error/indisponível no perfil HTTP definido |
| Gate stdio de lista contratada | Leitura estática: sete nomes no gate versus oito registradas | main `c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874`, proposta N16 na #181 | Reconciliar lista/critério; não afirmar execução do gate nesta preparação |

Os SHAs abreviados acima identificam o objeto; o recibo completo do tracker é a referência para reprodução. Resultado por head individual não comprova a combinação. Não somar 33 checks individuais com os 572 testes como se fossem um único conjunto.

## Inventário por tool

| Tool contratada | Transporte real histórico | Controle em processo / caso especial | Lacuna a manter visível |
|---|---|---|---|
| analyze_job | Registrado na #156 no escopo do recibo | Catálogo de testes em #157 | Variantes fora do recibo; navegador não se aplica diretamente a uma tool |
| compare_jobs | Registrado na #156 | Catálogo de #157; estudo entre versões N05 separado | Não prova compatibilidade entre todas as versões do Engine |
| explain_stage | Registrado na #156 | Contrato e argumentos do patch #157 | Demais variantes/limites devem apontar ao caso específico |
| list_runs | Registrado na #156 | Controle em processo #157 | Corrigir contradição documental N10; lista não é execução universal |
| recall_runs | Registrado na #156 | Controle em processo #157 | Omissão no gate stdio contratual deve ser reconciliada |
| search_kb | Registrado na #156 dentro do escopo histórico | Positivo `plan_json` em #163, árvore dependente | Positivo `plan_json` real e CI dessa árvore não comprovados por esses testes |
| suggest_fix | Registrado na #156 | Controle em processo #157 | Dependências de dados/memória e casos fora do recibo |
| verify_fix | Registrado na #156 | Controle em processo #157; #117 e N03 como temas próprios | Não transforma proposta p50/noise_floor ou projeção em comportamento validado |

O inventário aponta a cobertura histórica, sem atribuir automaticamente todos os casos a todas as tools. Na execução de uma lacuna, expandir somente as linhas necessárias para argumentos, fixtures e resultado esperado. `apex_status` não integra a lista observada de oito tools.

## Rotas e experiência HTTP

| Superfície | O que existe/documentado | Próxima prova ou decisão |
|---|---|---|
| `/v1/health` | API entregue, consumo de store_health; health público no contrato atual | Readiness e limites por perfil, quando necessários, devem ser distinguidos de liveness |
| Rotas HTTP das oito tools | Camada compartilhada e provas API/MCP na #156 | Não inferir que toda variante de parâmetros foi exercitada; registrar por caso |
| Rotas de recursos usadas pela Console: execuções, stages, findings e projeções | Integração #129 e contribuição `fab6620` | Matriz por tela/query e casos de dados/vazio/erro no perfil #172 |
| `/docs` e OpenAPI | Exposição fora da proteção do prefixo v1 descrita na #171 | Decidir política de schema e token por perfil; não chamar exposição de schema de vazamento por si |
| Front→nginx→API same-origin | Implementação/configuração observadas; prova de browser ainda delimitada | Build da imagem e navegação real com fixtures próprias; registrar versões e dados |
| Ask `/api/v2/ask` | Contrato proposto na #122 | Decisão e entrega futuras; não acrescentar selo de runtime |

## Fila mínima de validação a combinar

1. Integrar/reposicionar a pilha conforme decisão do mantenedor e reconciliar provas com a árvore resultante (#156).
2. Executar apenas lacunas acordadas do browser/nginx com matriz tela × data/empty/error/indisponível (#172).
3. Reconciliar contrato do gate stdio e decidir se é necessário novo caso real de `plan_json`; cada execução recebe ambiente, fixture e recibo próprios.

Estado desta fila: **planejada**, sem execução nesta complementação. Critérios de cada issue permanecem próprios; a documentação não fecha issues automaticamente.

## Atualização: proposta #182

A [triagem de coordenação](COORDENACAO-PR-182.md) identifica proposta nova de Console API-only e alterações no gate/consultas. Evidências relatadas pelo autor devem ser mapeadas por head/caso ao #156/#172; não foram reproduzidas aqui. A sobreposição com #158/#159 exige coordenação antes de transferir controles ou resultados à nova árvore.
