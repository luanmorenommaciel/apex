# Ideias, backlog e oportunidades — sem novos trackers nesta etapa

Todos os encaminhamentos abaixo são propostas para discussão. Implementação candidata não é integrada; integrado não equivale a aceite funcional. Responsáveis e prazos a confirmar. Os códigos internos são genealogia, não tarefas novas para somar às issues.

## 1. Revisar arquitetura API-only

**Destino existente:** #182; S03/S06/S23/NOV-05.

**Base e limite:** PR do Agmar candidata a centralizar SQL no Serve, atualizar badge v0.6 e endurecer a Console. Rótulo Pod 1.

**Menor encaminhamento:** Revisão Front por camadas: data layer, configuração/token, nginx/CSP, loading/cache/abort e acessibilidade; separar intenção de falha comprovada.

**Critério proposto:** Parecer por superfície e decisão dos autores/revisores; não prometer aceite dos 65 arquivos por revisão focal.

## 2. Preservar controles na integração

**Destino existente:** #158/#159/#156.

**Base e limite:** R1: teste front_query removido; R2: _two_doors usa console_statements/QUERIES_TS removidos na #182.

**Menor encaminhamento:** Escolher ordem de integração e portar os dois usos; manter casos Serve aditivo/legado, empate errado, seleção inválida e cleanup.

**Critério proposto:** Controles continuam discriminando erro na árvore escolhida; conflito textual não foi demonstrado.

## 3. Prova HTTP no navegador

**Destino existente:** #172; S03/S04.

**Base e limite:** Há relatos úteis de HTTP/TestClient/jsdom/curl e stack, cada um com limites. Nenhum equivale automaticamente a browser real via nginx.

**Menor encaminhamento:** Preparar protocolo com árvore/imagem, DATA_SOURCE=http, token/perfil, rotas e estados; depois observar casos acordados em ambiente autorizado.

**Critério proposto:** Caso mostra request por nginx, resposta e estado visual; vazio/erro/indisponibilidade não viram zero medido ou fallback silencioso.

## 4. Custódia do token e exposição

**Destino existente:** #171; S06/DEC-08.

**Base e limite:** Na #182, config.js leva apiToken ao browser; não constitui identidade por usuário.

**Menor encaminhamento:** Comparar perfis local, compartilhado e protegido por proxy; escolher exposição de docs/OpenAPI e custódia sem registrar credenciais nos documentos.

**Critério proposto:** Decisão por perfil e plano de verificação; não inventar requisito universal de autenticação nova para todo estudo.

## 5. Fronteira e sequência do Ask

**Destino existente:** #122; X01/S07.

**Base e limite:** API da 129 é base integrada; fluxo Ask completo e contrato não estão entregues por consequência.

**Menor encaminhamento:** Reutilizar comparação API existente/fachada/adiamento do Pod 3; time registrar proceed/defer/reject, escopo e responsáveis.

**Critério proposto:** Contrato e sequência da fatia escolhida, sem declarar BFF obrigatório ou serviço novo por antecipação.

## 6. Atribuição e piso de ruído

**Destino existente:** #117/#115; F02/F04/F09/F10/F11/F17/X02.

**Base e limite:** Resolver offline 126 existe; consumer Front ainda não demonstra atribuição pública. Piso/unidade/igualdade/escritor são decisões diferentes.

**Menor encaminhamento:** Escolher um consumidor e uma fatia de contrato; preservar ausência/zero, direção e proveniência; alinhar produtor/storage/Serve antes de habilitar indicador no Front.

**Critério proposto:** Critério observável por identidade e unidade; não remover todos os sentinelas nem exigir três PRs como regra.

## 7. TAIL_OUTLIER compreensível

**Destino existente:** #166; F13/F16/F18/S17.

**Base e limite:** RETRY_PRESSURE foi integrado; tipo aberto não significa perda silenciosa por faltar enum.

**Menor encaminhamento:** Mostrar finding de cauda sem afirmar causa skew; testar consumidor concreto e distinguir explicação, recipe e veredito.

**Critério proposto:** Caso TAIL_OUTLIER e tipo desconhecido com narrativa honesta; não reabrir 137 nem misturar higiene do gate 123.

## 8. Predictor: trabalho medido e estimado

**Destino existente:** #179; L10/F20/F21.

**Base e limite:** Coluna executor_run_time_ms existe; isso não prova valor útil em todo registro. #142/#145 são evolução Verify compartilhada.

**Menor encaminhamento:** Separar correção de comentário e estudo do modelo W; coordenar guarda literal da matriz quando mexer em texto fixado por teste.

**Critério proposto:** Comparar medido/estimado/ausente e fallback com unidade explícita; sem trocar fórmula por parecer documental.

## 9. Matriz e contrato atuais

**Destino existente:** #165/#180; NOV-05/L13.

**Base e limite:** Contrato v0.6 e badge 0.5 na main;182 oferece badge candidato. Matriz registra corte histórico antigo.

**Menor encaminhamento:** Atualizar só superfícies atuais, mantendo histórico e teste junto; não redesenhar semântica da telemetria por divergência textual.

**Critério proposto:** Mapa produtor→transporte→consumidor e status declared/observed/runtime_unproven, com SHA.

## 10. Topologia e proveniência visual

**Destino existente:** #108, interface #106; F15.

**Base e limite:** Estudo existente; implementação de grafo MCP não é predecessor universal de estudo visual.

**Menor encaminhamento:** Protótipo documental ou projeção estática com declared/observed/derived, sem pedir acesso privilegiado só para explorar.

**Critério proposto:** Pergunta de uso e pequena demonstração conceitual; nenhuma entrega de grafo runtime inferida.

## 11. Regra SQL de recusas

**Destino existente:** #182; interface Serve.

**Base e limite:** Corpo relata seis stages sintéticos e refused_count=3 em CH24.8; TS replica booleanos e teste Python fixa fragmentos.

**Menor encaminhamento:** Conferir primeiro os artefatos da execução live já relatada; propor fixture/oráculo adicional somente para eventual garantia que o time considere necessária.

**Critério proposto:** Execução da CTE com resultado independente é prova distinta de igualdade entre portas da mesma query.


## Interfaces conferidas no diff da #182

- **#169:** a CTE de refused_count acrescenta um consumidor que escolhe valores com `argMax(..., se.ts)`. Incluir esse consumidor na comparação de população/tentativa; a PR não decide automaticamente a política global.
- **#117 / N03:** `test_projection_parity.py` passa de comparar duas cópias SQL a fixar o predicado atual da regra 2. Se houver alteração posterior do piso de certificação, atualizar o controle na árvore escolhida; isso não cria um bloqueio novo para a #182.
- **#172, pergunta de revisão:** a imagem declara CSP `connect-src 'self'`, enquanto há referência a configuração cross-origin. Conferir o perfil suportado e ajustar a orientação correspondente se necessário. O efeito no navegador não foi observado nesta auditoria.

Esses pontos são interfaces ou perguntas de revisão, não falhas de execução demonstradas. A revisão não executou a combinação de branches.
