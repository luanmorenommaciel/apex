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

## Casos relevantes ao Engine e interfaces

| Caso | Material existente | Lacuna específica / próxima prova |
|---|---|---|
| #126/115 | Resolver puro cobre app/job, conflito, zero/ausência e tentativas | Consumidor escolhido e prova SQL/RDD conforme critério115; não refazer o resolver |
| #127/123 | Watcher/CLI/cenário integrados; runtime setembro relatado com corte e limitações | Decidir força de associação job versus stage/tentativa/snapshot; não dizer que nunca houve runtime |
| #128/124 | pwsh explícito e plano único; DryRun retorna antes de Command | Controle troca Command mantendo Handler; stubs inofensivos antes de ações com efeitos |
| #131/139/155 | Preflight e endurecimento integrados;#155: guarda pequena aberta,11 checks failure e0 reviews na captura | Revisão/aceite e recibo da árvore escolhida; não inferir causa atual de billing |
| #167 versus185 | Main tem diferença argv/assinatura;185 expõe parâmetros candidatos; quatro checks verdes/zero reviews em a5c2ca45 | Interface/comando e equivalência ON/OFF, não apenas presença textual; benchmark é prova separada |
| #174/#175 | Escrita Copy-Item -Force e nomes fixos observados estaticamente | Não houve acesso a.env, perda reproduzida ou inspeção de containers; política e controle próprios |
| #169/#170/#173 | Contratos de população, replay e database com recortes por consumidor | Regra comum precisa decisão e prova escolhida; não extrapolar uma migração/query para todas |
| JAR semanal 39254068517 | Verde JDK17/21 no SHA c3c3ea3; extrato identifica Ubuntu24.04.5 somente no job JDK17 | Não prova Windows, migração26.04, overhead, workflow principal verde ou runner de todos jobs |

## Preparação do protocolo de interface R9D

- Escolher main ou candidato185 e identificar SHA; preservar relato de variante local sem publicá-la como necessária.
- Enumerar argv gerados para ON e OFF, parâmetros aceitos e precedência de EnvFile/AdditionalComposeFile.
- Controle proposto: remover um parâmetro aceito de apenas um braço; a prova de interface deve detectar a diferença.
- Separar validação de binding, comando completo, preflight, preservação de configuração e ownership de uma medição real de performance.
- Nenhum benchmark/pwsh/Docker iniciado nesta rodada; o desenho não é execução nem aprovação.
