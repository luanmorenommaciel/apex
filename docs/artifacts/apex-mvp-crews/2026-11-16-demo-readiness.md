---
title: Apex — checagem da demo e resposta ao feedback do Agmar
date: 2026-11-16
tags: [apex, apresentacao, demo, evidencias, crew-a]
status: reviewed-with-gaps
---

# Apex · demo para as crews · checagem de 16/11

**Resultado:** a apresentação v0.3 tem um roteiro guiado de console com fixtures conferidas. Diagnóstico MCP e execução real integrada exigem ensaio no ambiente escolhido. A revisão não libera o evento nem certifica o produto.

## Feedback recebido

Fonte: trecho de Discord fornecido pelo Sidymar nesta sessão. Em 09/11, Agmar perguntou se o walkthrough e o pedido à plateia já eram demonstráveis, e se seriam detalhados JAR, transporte, infra e servidor. Sidymar respondeu que não era necessário aprofundar tanto a técnica e que a demo ainda não estava no nível proposto, mas que poderiam definir os passos.

A v0.2 troca o walkthrough livre por uma investigação guiada; pede feedback e interesse em preparar um piloto; inclui conexão em cinco minutos e detalhes técnicos no apêndice. Não infere aprovação dos demais apresentadores.

## Fonte e proveniência

- Repositório confirmado: [luanmorenommaciel/apex](https://github.com/luanmorenommaciel/apex).
- Main consultada em 16/11: [`0cc8bac1ec62724f4035865fbd95d6ec5463b1c9`](https://github.com/luanmorenommaciel/apex/tree/0cc8bac1ec62724f4035865fbd95d6ec5463b1c9), último commit de 09/11. A checagem usou um snapshot temporário desse SHA; não alterou o código do produto nem os PRs de implementação.
- O checkout principal local estava em `c3c3ea3` (08/10), portanto não foi usado como prova do estado atual.
- Relatório histórico consultado: [L7 follow-up de 31/10](https://github.com/luanmorenommaciel/apex/blob/716ce8bc88ddd96fb54f69ed1900bc4b3d578eb1/docs/e2e/L7-FOLLOWUP-20261031.md) e [revisão de 02/11](https://github.com/luanmorenommaciel/apex/blob/716ce8bc88ddd96fb54f69ed1900bc4b3d578eb1/docs/e2e/L7-REVIEW-CLARIFICATIONS-20261102.md), no [PR #207](https://github.com/luanmorenommaciel/apex/pull/207), ainda aberto.
- O experimento histórico usa a árvore `0683db0f637dfc2efb647fe353e15e82de6d48bd`, composição de main `0e84c10b` com #182/#194/#195/#197. Não é a main atual nem um SHA oficial de aceite. Seus payloads privados não foram reexecutados ou validados independentemente nesta sessão.

## Verificações diretas desta revisão

| Verificação | Resultado observado | Alcance |
|---|---|---|
| Build na main fixada | [direct/pass] `npm run build`: TypeScript + Vite, 64 módulos, exit 0 | Compilação do console; não testa integração com banco |
| Runs no Chrome | [direct/pass] `source fixtures`, nove aplicações, abertura de `daily_revenue_rollup` | Interface com dados de exemplo |
| Execução | [direct/pass] job `app-20260803014217-0071`, 34 stages, stage 25, finding `f-7c41e9`, SPILL | Este exemplo não é um job de skew nem uma execução produzida agora |
| Compare | [direct/pass] botão abriu baseline `app-20260802231455-0069`, correspondência stage 22 → 25 e métricas | Valores das fixtures, sem medição de melhoria ou causalidade |
| Memory | [direct/pass] uma forma, sete runs, histórico de configuração ausente | Fixture enriquecida; task-time não é wall-clock |
| Verify | [direct/pass] proposta SPILL, formato desconhecido, runtime `unresolved`; labels de mecanismo/replays presentes | Esses campos são dados ilustrativos de fixture; não são observações de uma correção real |
| MCP stdio | [direct/pass] cliente SDK inicializou o processo real e listou tools, resources e prompts | Nenhuma chamada de diagnóstico; nenhum ClickHouse ou LLM |

O MCP retornou oito tools: `analyze_run`, `explain_stage`, `compare_runs`, `list_runs`, `search_kb`, `recall_similar_runs`, `verify_fix`, `suggest_fix`. As sete primeiras trazem `readOnlyHint=true`; `suggest_fix` traz `false`. Foi listado `apex://runs`; a lista de prompts estava vazia. Anotações de protocolo não constituem teste independente de ausência de mutação.

Recibo de descoberta: [JSON](2026-11-16-demo-evidence/mcp-discovery.json). A navegação acima foi lida da acessibilidade do Chrome, não de um teste de tela conectado à API. Fixtures são explicitamente enriquecidas no [arquivo fonte](https://github.com/luanmorenommaciel/apex/blob/0cc8bac1ec62724f4035865fbd95d6ec5463b1c9/front/src/data/fixtures.ts); não chamar esse passeio de replay integral de telemetria.

Docker estava parado (`docker.sock` ausente). Não foi iniciada uma nova stack nem executado um job Spark nesta revisão. Nenhum perfil Databricks foi selecionado ou usado.

## O que a evidência histórica permite afirmar

Segundo o relatório de 31/10 e suas correções de 02/11:

- Dois jobs reais processaram dez milhões de linhas cada e tiveram 20 stages observados. Gates Engine/Serve passaram naquele candidato local.
- Sete conjuntos de argumentos de quatro tools tiveram JSON igual em HTTP, MCP stdio via API e MCP stdio direto no ClickHouse. Isso não é cobertura de oito tools, MCP-over-HTTP nem onboarding em Claude Code/Cursor/Codex.
- Compare e Memory tiveram conteúdo em Chrome real. Há limites de correspondência entre stages e fingerprints. Não se demonstrou ganho de tuning.
- Para o mesmo par, Console disse `unchanged` e API/MCP disseram `regressed`. O deck v0.1 não podia anunciar paridade irrestrita de vereditos.
- Verify foi exercitado com ausência e com uma linha sintética; zero replays e nenhuma mudança aplicada. Labels fixos de aprovação/aplicação na UI não provam enforcement do backend.
- A contagem inicial de 23 verificações Python inclui uma alegação de controle negativo retirada. A reconciliação posterior passou 16 checks de escopos sobrepostos; não somar essas contagens como cenários E2E independentes.

Essas afirmações são **reported**, provenientes do relatório histórico. Não são novas execuções desta revisão. Por isso os KPIs genéricos da v0.1 (sete runs, zero diferenças em oito tools, 28/0 e 826 testes) foram substituídos por evidência com data e escopo.

## Conexão e infraestrutura

Fontes da main fixada: [JAR](https://github.com/luanmorenommaciel/apex/blob/0cc8bac1ec62724f4035865fbd95d6ec5463b1c9/jar/README.md), [Collect](https://github.com/luanmorenommaciel/apex/blob/0cc8bac1ec62724f4035865fbd95d6ec5463b1c9/collect/README.md), [Dev](https://github.com/luanmorenommaciel/apex/blob/0cc8bac1ec62724f4035865fbd95d6ec5463b1c9/dev/README.md), [Console](https://github.com/luanmorenommaciel/apex/blob/0cc8bac1ec62724f4035865fbd95d6ec5463b1c9/front/README.md), [MCP](https://github.com/luanmorenommaciel/apex/blob/0cc8bac1ec62724f4035865fbd95d6ec5463b1c9/serve/src/apex_mcp/server.py).

O caminho documentado é JAR/plugin → OTLP/HTTP → Collector → ClickHouse. O Engine analisa e persiste findings. O console pode ler pela API; o MCP da main usa stdio e leitura de ClickHouse. MCP lendo pela API está no PR #195. History Server é consulta complementar de event logs, não um salto obrigatório da ingestão OTLP. Compatibilidade do JAR e endpoint real devem ser confirmados no ambiente da demo.

Consulta GitHub em 16/11: #191 mergeado; #192/#193/#194/#195/#200 abertos. Não usar o plano mergeado como prova de implementação entregue. Esta consulta não aprovou ou alterou PRs.

## Decisão para a apresentação

**Base viável:** investigação guiada com fixtures rotuladas, em 15 minutos, sem convidados operando. **Alternativa condicionada:** um job real de skew com configuração, findings e baseline preparados e ensaiados. **MCP ao vivo:** só após testar diagnóstico no cliente/backend escolhidos. **Verify:** explicação de limites, sem promessa de correção medida.

O [plano v0.3](2026-11-04-apresentacao-produto-crews.md) contém comandos, URLs, argumentos e gates de ensaio. O [deck v0.3](2026-11-09-apresentacao-mvp-deck.html) tem 17 slides principais e três apêndices opcionais, com contadores separados.

Ainda não verificados: nova data, disponibilidade dos apresentadores, duração em ensaio coletivo, integração real atual, diagnóstico no cliente MCP, vídeo de backup e execução de correção com replay. São gates para a sessão; não foram silenciosamente marcados como concluídos.
