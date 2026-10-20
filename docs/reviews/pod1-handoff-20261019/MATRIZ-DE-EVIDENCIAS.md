# Matriz de evidências e limites

“Direto” significa leitura do objeto/código/recibo, não execução independente do produto. “Relato” significa resultado descrito por autor/entrega histórica. “Proposto” é critério futuro. Estados atuais vêm dos recibos Parte 10, com SHA e observed_at; resultados históricos conservam o próprio corte.

| Evidência | O que suporta | O que não suporta |
|---|---|---|
| Metadados PR/commit e merge | Autor, head, data e presença integrada no objeto consultado | Autoria de todo projeto, aprovação funcional ou responsável futuro |
| Checks verdes no head | Conclusão dos checks específicos retornados nesse SHA | CI de uma combinação futura, navegador real, todas lanes ou billing atual |
| Check failure com histórico de0 steps | Tentativa registrada; ausência de execução naquela tentativa quando recibo mostra steps | Falha de asserção ou causa administrativa atual sem anotação específica |
| Diff/teste lido | Existência de controle e finalidade estática | Resultado executado nesta auditoria |
| Relato de teste unitário/jsdom/TestClient | O autor descreveu esses cenários e suas contagens | Nova reprodução pelo Codex, nginx real ou browser |
| Relato de runtime com SHA | Evidência declarada do ambiente e caso descritos | Toda execução futura ou árvore diferente |
| Aceite/status Task-Spec | Declaração de governança no corte | Novo aceite concedido por esta análise |

Nenhum teste, build, container, serviço, workflow manual ou instalação foi executado para preparar este pacote. Não somar contagens de suites sobrepostas nem rebatizar relato como prova direta independente.

## Casos relevantes ao Front

| Caso | Material existente | Lacuna específica / próxima prova |
|---|---|---|
| #100/118/119/120 | Console e correções Verify integradas; autoria e cortes nas fichas | Não exigir reabrir PR histórica por ausência de prova visual nesta rodada |
| #129/fab6620 | API integrada, HTTP/same-origin e ajustes de integração | Não entrega sozinho o Ask nem a política #171 |
| #136/#137/#138/#146/#151 | Regras, CI, projeção e detalhe textual implementados | Provas unitárias/estáticas não são browser; acompanhamento por contrato consumidor |
| #153 | Autor relata stack real, paridade e telas com jobs reais; script console.live usa jsdom/App/API | Reconhecer a cadeia já relatada e comparar seus recibos com o relato adicional de nginx; somente eventual residual segue na #172 |
| #182 | Checks `repo checks (license + collector config)`, `front (Node 22)` e `python lanes + root gate` verdes no head74fdb079, zero reviews na captura; corpo relata Front 202/8 skip, Serve 456, gate 17/17 e seis stages/refused_count=3 | Contagens são relatos; não foram reproduzidas nesta auditoria. A prova live já existe como relato do autor; esta auditoria não verificou uma fixture SQL versionada com resultado esperado independente. Conferir os artefatos existentes antes de propor complemento |
| Integração158/159/182 | Dois usos de helpers removidos confirmados estaticamente | Portar e validar na árvore escolhida; não foi feito merge/rebase |
| Token/config.js | O diff documenta transmissão ao browser | Não prova identidade por usuário nem ratificação do perfil171 |

## Preparação do protocolo #172 (documental)

- Primeiro reconciliar os recibos já apresentados pelo Agmar, incluindo o E2E histórico da #153 e o relato de imagem nginx compartilhado no Discord. Registrar casos atendidos, limites e somente eventual residual; não partir da premissa de ausência de E2E.
- Árvore candidata: escolher main c3c3ea3 ou head182, sem misturar imagens/recibos.
- Identidades a preencher pelo executor: commit, imagem/tag/digest, DATA_SOURCE, endpoint, perfil de token, data, caso e rota.
- Casos: lista/detalhe de run, findings/transições, verificação conforme fixture disponível; estado carregando, vazio, erro textual, API indisponível e ausência de dado indexado.
- Registro mínimo por caso: requisição passando por nginx, status/resposta sanitizada e estado visual; rotas excluídas nomeadas.
- Controles: indisponibilidade não recai silenciosamente em fixture; erro não vira vazio; ausência não vira zero medido; não arquivar token.
- Resultado desta preparação: protocolo proposto; nenhuma execução nova por esta auditoria. Isso não nega execuções anteriores relatadas pelo autor. Qualquer complemento depende do residual identificado, árvore e ambiente.172a/172b são subpassos locais, não issues novas.
