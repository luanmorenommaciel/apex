---
title: Apex — apresentação de produto para as outras crews (plano)
date: 2026-11-04
updated: 2026-11-16
version: "0.3"
tags: [apex, crew-a, apresentacao, pitch, demo, dataship]
status: draft
---

# Apex — apresentação de produto para as outras crews · v0.3

Revisão após o feedback do Agmar no Discord de 09/11 e a resposta do Sidymar: a demo ainda não sustenta o walkthrough livre proposto na v0.1. O foco continua nos pontos de contato Console e MCP; a apresentação mostra um roteiro fechado e seus limites. Data do evento e apresentadores continuam a confirmar. A semana de 09/11 era a previsão original, não uma data futura confirmada.

**Deck:** [HTML atualizado](2026-11-09-apresentacao-mvp-deck.html). O nome do arquivo foi mantido; o conteúdo identifica v0.3 e a revisão de 16/11.

## Revisão visual v0.3 · 16/11

Aplicação da revisão html-ppt: labels mais claros, menos texto nos slides 6–12, captura histórica do console incorporada, fluxo de quatro passos e inventário completo no apêndice. O deck contém 17 slides principais e três apêndices. A captura de skew é de 28/10, com fonte indicada; a demo em fixtures continua sendo o caso de SPILL. A revisão visual não adiciona prova de integração real ou correção executada.

Ao chegar ao encerramento, a navegação normal para ali. **A** abre o apêndice; **Esc** retorna. O contador mostra 1–17 na apresentação e Apêndice 1–3 nos backups; a barra de progresso acompanha a seção atual. A imagem do console pode ser ampliada dentro do deck. As notas continuam no drawer **N**, na mesma janela; fechá-las antes de compartilhar a tela.

## Feedback do Agmar e resposta na v0.2

| Feedback de 09/11 | Mudança |
|---|---|
| Conseguimos demonstrar o walkthrough desta forma? | Substituir três histórias abertas e um convidado operando por uma investigação guiada, ensaiada, com execução e links escolhidos antes. Fixtures são a alternativa já conferida; dados reais dependem de ensaio. |
| O pedido à plateia está adiantado? | Pedir feedback sobre o diagnóstico, descrição de um caso e interesse em preparar um piloto. Remover promessa de rodar qualquer pipeline recebido ou de onboarding imediato no MCP. |
| Vamos explicar como plugar o JAR? | Um slide curto: JAR compatível com Spark/Scala + `spark.plugins=apex.ApexPlugin` + endpoint OTLP. Configuração detalhada no apêndice. |
| History → telemetria → ClickHouse? | Corrigir a premissa para o caminho documentado: plugin → OTLP → Collector → ClickHouse. O History Server guarda event logs para consulta; não é um salto obrigatório dessa ingestão. |
| Detalhar infra e server? | Explicar as responsabilidades em um minuto. Comandos, portas e implantação ficam no apêndice e nas perguntas. |

Estas mudanças respondem ao feedback; não representam nova aprovação da equipe.

## O que foi conferido em 16/11

Fonte de código: main remota `0cc8bac1ec62724f4035865fbd95d6ec5463b1c9` (último commit de 09/11). A cópia principal local estava em `c3c3ea3`, de 08/10; a checagem usou uma cópia temporária da main remota sem modificar o checkout.

- Build do console passou (`npm run build`). Navegação no Chrome em `VITE_DATA_SOURCE=fixtures`: Runs → execução → Compare → Memory → Verify. São fixtures enriquecidas para mostrar as telas, não uma reprodução integral de execução real.
- MCP: initialize e descoberta via cliente stdio real; oito tools, sete com `readOnlyHint=true`, recurso `apex://runs`. Nenhuma tool de diagnóstico foi chamada nesta checagem; nenhum banco ou LLM foi usado.
- Docker estava parado e não havia stack local ativa para repetir o fluxo com Spark/ClickHouse. Esta revisão não certifica uma demo integrada ao vivo.
- Relatório de 30–31/10 e revisão de 02/11 do PR #207: Compare/Memory populados em experimento real de composição de branches; Verify usou uma linha sintética, sem replay de correção. O Console disse `unchanged` onde API/MCP disseram `regressed` para o mesmo par. Igualdade de transportes não prova igualdade de política de diagnóstico.

Detalhes, fontes e limites: [checagem de demonstrabilidade](2026-11-16-demo-readiness.md).

## Escopo da demo

| Fluxo | O que mostrar | Condição e limite |
|---|---|---|
| Runs → execução → finding | Identificação do job, métricas do stage, evidência e lacunas | Base com fixtures conferida. Em dados reais, escolher um job com Engine já executado e findings persistidos. Não interpretar zero findings como avaliação concluída. |
| Compare | Baseline explícita, métricas e alinhamento de stages | Fixtures conferidas. Com dados reais, validar ambos os jobs e a correspondência; não anunciar igualdade de veredito UI/MCP. |
| Memory | Histórico de uma forma de plano | Fixtures conferidas. Com dados reais, indexar antes. Task-time não é wall-clock nem economia. |
| Verify | Mostrar a separação entre proposta e resultado, inclusive `unresolved` ou ausência | Somente explicação de tela com fixtures ou evidência capturada. Não demonstrar aplicação, replay, melhoria ou certificação reais. |
| MCP: `list_runs` → `analyze_run(detail="full")` → `explain_stage` | Consultar a mesma execução, com argumentos preparados | Descoberta conferida; diagnóstico atual ao vivo pendente. Só incluir como demo ao vivo depois de ensaio no cliente e backend escolhidos. |
| `suggest_fix` | Proposta como dado, se houver saída coerente no ensaio | Opcional. Não prometer diff idêntico ao console: fonte única de proposta (#193) ainda aberta. Não aplicar nada. |
| Ask / Search KB / prompts | Apenas informar limites e próximos passos | Ask roteirizado; Search KB no console (#192) e prompts (#194) continuam abertos na consulta de 16/11. Fora do roteiro principal. |

**Frase de abertura da demo:** “Vamos percorrer uma investigação preparada. Se usarmos fixtures, os dados são ilustrativos e enriquecidos para explicar a interface; não são uma medição de resultado do produto.”

## Roteiro fechado · 15 min de console

Alternativa reproduzível sem Docker, no SHA acima:

```sh
cd front
npm ci
VITE_DATA_SOURCE=fixtures npm run dev -- --host 127.0.0.1
```

1. **Runs · 2 min:** apontar `source fixtures`, abrir `daily_revenue_rollup`, job `app-20260803014217-0071`. O finding principal deste exemplo é **SPILL**, não skew. A origem dos dados deve permanecer visível.
2. **Execução · 5 min:** selecionar stage 25, mostrar spill, métricas e evidência; explicar configuração ausente e recusa de conclusão. Não deduzir causa apenas de um rótulo de AQE ou crescimento de input.
3. **Compare · 4 min:** abrir `/compare?current=app-20260803014217-0071&baseline=app-20260802231455-0069`. Mostrar a correspondência stage 22 → 25 e explicar que os números são ilustrativos. Não anunciar ganho de performance ou causalidade por tuning.
4. **Memory · 2 min:** abrir `/memory`, distinguir histórico de shape e tempo agregado de tasks de wall-clock. A fixture tem sete runs nessa forma, sem histórico de configuração capturado.
5. **Limites · 2 min:** Verify pode ser uma breve explicação de `unresolved` em `/verify?job=app-20260803014217-0071&finding=f-7c41e9`. A fixture contém valores de mecanismo/replays ilustrativos e uma proposta de formato desconhecido; não lê-los como fatos observados. Se confundir a narrativa, omitir essa tela e usar o slide de limites.

Links e sequência foram conferidos; ensaio coletivo, tempo total e gravação continuam pendentes. O exemplo de skew com dados reais fica como alternativa depois dos gates abaixo.

## MCP · 5–10 min opcionais

Escolher um cliente MCP e uma fonte de dados explícitos. A main usa transporte **stdio**, com leitura direta de ClickHouse; MCP lendo pela API está no PR #195, ainda aberto. HTTP da API e MCP-over-HTTP são coisas diferentes. Não configurar o protótipo HTTP como se estivesse entregue.

- Antes da sessão, anotar SHA, cliente, backend, `job_id`, `stage_id` e `finding_id` reais, sem incluir credenciais no deck.
- Usar `list_runs` com janela que inclua o job; `since_hours=24` não encontrará necessariamente execuções de outubro.
- Usar `analyze_run(job_id=..., detail="full")`; o default `summary` pode omitir listas de stages/findings. Em seguida `explain_stage` no stage confirmado.
- Perguntas da plateia são mediadas pelo apresentador e restritas ao job ensaiado. Não depender de convidados instalarem clientes durante a sessão.
- Se não houver ensaio integrado aprovado pela crew, mostrar captura datada ou explicar as tools no slide. Descoberta de tools não prova diagnóstico operacional.

## Como conectar · 5 min

Mostrar o fluxo **Spark + JAR → OTLP → Collector → ClickHouse → Engine → interfaces**. O Engine gera os findings; Console/API e MCP consultam dados com limites atuais. A centralização de todos os vereditos permanece discussão P7.2.

- Distribuir JAR compatível com a combinação Spark/Scala do ambiente.
- Ativar `spark.plugins=apex.ApexPlugin` e definir `spark.apex.otlp.endpoint` com a URL base do Collector. O plugin acrescenta `/v1/traces`.
- History Server: consulta complementar de event logs, fora do caminho de exportação OTLP acima.
- Collector: recebe e transforma telemetria; ClickHouse: persiste; API: atende o console HTTP; MCP: processo stdio chamado pelo cliente. Explicar funções, sem montar infraestrutura no palco.

No apêndice, exemplo conceitual (substituir o caminho por um JAR construído e compatível; não pressupõe pacote publicado):

```sh
spark-submit \
  --jars /caminho/apex-compativel.jar \
  --conf spark.plugins=apex.ApexPlugin \
  --conf spark.apex.otlp.endpoint=http://collector:4318 \
  seu_job.py
```

`spark.extraListeners=apex.ApexStageListener` é fallback: não captura transições AQE e não tem o mesmo flush de shutdown. Não escolher esse caminho para a demo principal de AQE. Compatibilidade e acesso de rede devem ser ensaiados no ambiente escolhido; não foi feito teste em Databricks nesta revisão.

## Agenda revisada · janela de 2 horas

Janela preservada da v0.1. O segundo bloco vira discussão e retomada guiada; não promete exploração livre por convidados.

| Horário | Bloco | Responsável proposto |
|---|---|---|
| 0:00–0:10 | Incidente ilustrativo, problema e Crew A | Augusto |
| 0:10–0:20 | Console + MCP: duas formas de investigar | Antony |
| 0:20–0:25 | Como conectar: JAR, OTLP, armazenamento e interfaces | Agmar + Guilherme |
| 0:25–0:40 | Investigação guiada no console | Sidymar; Gabriel apoia se houver job real ensaiado |
| 0:40–0:50 | MCP ensaiado ou captura datada e explicação das tools | Agmar + Sidymar |
| 0:50–1:00 | Evidências, limites e o que falta | Josenildo + Jayme + Augusto |
| 1:00–1:10 | Intervalo | — |
| 1:10–1:30 | Retomar o mesmo caso e responder perguntas mediadas | Sidymar + Agmar |
| 1:30–1:50 | Roadmap e conversa sobre futuros pilotos | Antony; Augusto modera |
| 1:50–2:00 | Feedback, próximos passos e encerramento | Augusto + todos |

Papéis são propostas, não compromissos confirmados. Luan fica na plateia, conforme plano anterior. Confirmar disponibilidade de todos e nova data; não transformar o feedback do Agmar em atribuição aceita.

## Pedido à plateia

1. **O diagnóstico ficou claro?** Onde faltou evidência ou contexto para decidir o próximo passo?
2. **Que problema vocês enfrentam?** Descrever um caso e as restrições do ambiente, sem enviar dados ou prometer execução imediata.
3. **Interesse em preparar um piloto?** Combinar depois compatibilidade, acesso, responsável e critérios de sucesso. Instalação e onboarding não fazem parte da sessão.

## Gates de preparação

- [ ] Confirmar nova data, participantes e donos dos blocos.
- [ ] Escolher explicitamente modo principal: fixtures ou integração real. Não usar `auto` com fallback silencioso durante a demo.
- [ ] Fixar SHA e fonte; se composição de PRs, listar os heads e dizer que não é main aceita.
- [ ] Para dados reais: stack saudável, job escolhido, configuração, findings persistidos e baseline comparável; Memory indexada se usada.
- [ ] Ensaiar os passos no console exato e no cliente MCP exato, com os mesmos IDs; registrar os resultados e divergências.
- [ ] Validar narrativa de Compare sem confundir métricas iguais com políticas de veredito iguais.
- [ ] Não colocar Verify real no roteiro sem evidência de replays e avaliação; fixtures não satisfazem esse gate.
- [ ] Gravar backup de cada trecho escolhido e rotular fonte/data/SHA; vídeo ainda não produzido nesta revisão.
- [ ] Ensaio coletivo com cronômetro e transições entre apresentadores.

**Estado desta revisão:** plano e deck atualizados; build, navegação em fixtures e descoberta MCP verificados. Demo integrada e liberação para o palco continuam pendentes desses gates.
