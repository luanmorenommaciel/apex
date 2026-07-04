# Issues — Reunião 30/06/2026
> Extraído da transcrição `transcription30.06.06`  
> Participantes: Luan (Commander), Augusto, Jaime, Aguimar  
> Issues #22 em diante (existentes: #17–#21)

---

## ISSUE #22 — [spec] Documento V1 completo: arquitetura + pods + escopo

**Labels:** `type:spec` `priority:high` `owner:luan`

**Descrição:**
Luan vai compilar o trabalho de Aguimar (pesquisa DataFlint) e Augusto (branch plat-v0) em um único documento de especificação da V1.

O documento deve cobrir:
- Arquitetura em 4 passos: Spark Envy → SparkListener → ClickHouse → Crew.ai → MCP
- Divisão em pods (ver #23, #24, #25)
- Escopo mínimo de cada componente para V1
- Critérios de done para cada pod

**Saída esperada:** PDF + post no canal Discord para validação do time  
**Origem:** "Eu vou construir um plano, vou construir PDF com todo o plano, vou pegar o que o Aguimar fez, vou pegar o que o Augusto fez, eu vou compilar tudo isso dentro de um documento."

---

## ISSUE #23 — [pod/ambiente] Spark Envy: Docker gerando ambiente + jobs

**Labels:** `type:feature` `pod:ambiente` `priority:high`

**Descrição:**
Criar o ambiente Docker ("Spark Envy") que gera jobs Spark continuamente, produzindo Spark History Logs para alimentar o pipeline do Apex.

Philo tem uma versão inicial — importar e organizar no repositório.

**Critérios de done:**
- [ ] `docker compose up` sobe o ambiente sem configuração manual
- [ ] Jobs Spark rodam e geram event logs em `spark-logs/events/`
- [ ] Spark History Server acessível em `:18080`
- [ ] README documentando como rodar localmente

**Bloqueada por:** #22 (escopo definido pelo spec)  
**Origem:** "A gente vai criar o Spark Envy que vai ficar gerando o nosso ambiente lá no Dockerfile."

---

## ISSUE #24 — [pod/listener] SparkListener: captura de métricas em tempo real

**Labels:** `type:feature` `pod:listener` `priority:high`

**Descrição:**
Implementar SparkListener que se injeta na definição do job Spark e envia métricas para o ClickHouse (infra do Apex) em tempo real.

**Decisão arquitetural pendente — ver #27:** esta issue pressupõe abordagem SparkListener (discutida na reunião 30/jun). Isso difere da abordagem "zero JAR" atual do CLAUDE.md. Precisa de alinhamento antes de implementar.

**Critérios de done:**
- [ ] Listener implementado e documentado
- [ ] Injeta via `spark.extraListeners` sem modificar código do job
- [ ] Envia métricas ao ClickHouse: stage metrics, task counts, spill, executor utilization
- [ ] Fail-safe: exception no listener não mata o job
- [ ] Testado no Spark Envy (#23)

**Bloqueada por:** #22 (escopo) + #27 (decisão arquitetural)  
**Origem:** "A gente vai criar o SparkListener que a gente injeta nesse cluster, injeta lá na definição do Spark, roda o job, tem as comunicações internas dele, vai enviar essas informações para a nossa infraestrutura."

---

## ISSUE #25 — [pod/infra] ClickHouse setup: telemetria + storage de métricas

**Labels:** `type:infra` `pod:infraestrutura` `priority:high`

**Descrição:**
Setup do ClickHouse (referido na reunião como "ClickStack") para receber e armazenar métricas enviadas pelo SparkListener em tempo real.

**Critérios de done:**
- [ ] ClickHouse no `docker compose` junto ao Spark Envy
- [ ] Schema definido para métricas do SparkListener
- [ ] Dados persistem entre restarts
- [ ] Query básica de consulta por `app_id` / `job_id` funcionando
- [ ] README com schema e exemplos de query

**Bloqueada por:** #22 (escopo) + #23 (ambiente)  
**Origem:** "Nossa infraestrutura vai ser baseada no quê? Vai ser baseado em telemetria. E aí essa telemetria vai gravar essas informações no ClickStack."

---

## ISSUE #26 — [pod/diagnóstico] Crew.ai: diagnóstico e recomendação por job_id

**Labels:** `type:feature` `pod:diagnostico` `priority:medium`

**Descrição:**
Integrar Crew.ai como motor de diagnóstico. Recebe métricas do ClickHouse (por job_id), raciocina sobre o problema de performance e gera recomendação estruturada entregue via MCP.

**Fluxo esperado:**
1. Job termina → ClickHouse tem as métricas
2. Trigger dispara Crew.ai com o `job_id`
3. Crew.ai consulta métricas → gera diagnóstico + fix sugerido
4. Fix entregue via MCP ao engenheiro no IDE

**Critérios de done:**
- [ ] Crew.ai integrado ao ClickHouse
- [ ] Diagnóstico mínimo: detecta wasted cores, spill, skew
- [ ] Output estruturado (root_cause, recommendation, confidence)
- [ ] Entrega via MCP funcionando (ver #27)

**Bloqueada por:** #25 (dados no ClickHouse)  
**Origem:** "Daí isso vai trigar o Crew.ai, o Crew.ai vai olhar e vai falar, pô beleza, essas são as métricas, e daí a gente vai ver como isso vai acontecer."

---

## ISSUE #27 — [decisão] ADR-005: SparkListener in-process vs zero-JAR event log

**Labels:** `type:adr` `priority:critical` `needs-decision`

**Descrição:**
A reunião de 30/jun descreve uma abordagem com SparkListener injetado in-process, que difere diretamente do princípio atual do Apex documentado no CLAUDE.md:

> *"Zero JAR injetado no cluster — Zero modificação de SparkSession"*

Precisamos de um ADR que formalize a decisão arquitetural:

**Opção A — SparkListener (abordagem reunião 30/jun):**
- Captura métricas em tempo real durante execução do job
- Requer injeção via `spark.extraListeners`
- Permite intervenção enquanto o job roda
- Trade-off: similiar ao DataFlint (supply chain risk, in-process)

**Opção B — Zero-JAR event log (abordagem CLAUDE.md atual):**
- Lê event logs após o job terminar (ou durante via MinIO polling)
- Sem modificação no cluster ou classpath
- Mais seguro, não-intrusivo
- Trade-off: diagnóstico pós-mortem, não em tempo real

**Ou híbrido:** zero-JAR para diagnóstico, SparkListener opt-in para real-time.

**Quem decide:** Luan + Augusto  
**Urgência:** bloqueia #24 e a direção técnica do time  
**Origem:** Tensão entre "o job rodou, eu falo debuga esse job_id" (pós-mortem) e "captura ao vivo no momento do job" (real-time).

---

## ISSUE #28 — [research] Análise individual DataFlint — cada membro do time

**Labels:** `type:research` `priority:medium`

**Descrição:**
Luan pediu que cada membro do time produza um documento curto (PDF) com sua análise individual do DataFlint:
- Pontos positivos
- Pontos negativos / limitações
- O que o Apex pode usar/aprender
- O que o Apex pode fazer melhor

**Assignees:** Anthony, Philo (e demais membros do time)  
**Prazo:** antes da reunião de alinhamento V1  
**Origem:** "O que eu gostaria que todo mundo fizesse, de verdade: olhar o DataFlint, compilar uns documentos PDF, curtos, do que vocês acharam, quais são os pontos, o que a gente pode usar."

> **Nota:** Aguimar e Augusto já entregaram. Falta o restante do time.

---

## ISSUE #29 — [feedback] Revisar branch Augusto + dar feedback

**Labels:** `type:review` `priority:high` `owner:luan`

**Descrição:**
Luan vai revisar a branch criada pelo Augusto (fork do trabalho do Gabriel) e dar feedback sobre:
- Alinhamento com a arquitetura V1
- O que aproveitar para o escopo inicial
- Sugestões de ajuste

**Origem:** "Vou olhar exatamente isso aqui que você fez, Augusto, a branch que você colocou aqui, vou te trazer alguns feedbacks também."

---

## ISSUE #30 — [research] On-premise / offline mode para clientes enterprise

**Labels:** `type:research` `priority:low` `future`

**Descrição:**
Jaime levantou o ponto: como executar o Apex de forma segura para empresas que têm restrições contra rodar agentes na nuvem. Investigar viabilidade de:
- Deploy totalmente on-premise (LLM local, sem Anthropic API)
- Modo air-gapped: Spark Envy + ClickHouse + modelo local (ex: Ollama)
- Requisitos mínimos de hardware

**Não é bloqueante para V1** — registrar como pesquisa futura.  
**Origem:** "Como a gente poderia rodar isso de forma offline, no próprio hardware? Que a gente possa impedir isso e rodar aqui."

---

## Resumo executivo

| # | Título | Owner | Prioridade | Status |
|---|--------|-------|-----------|--------|
| #22 | Documento V1 + pods spec | Luan | 🔴 Alta | Luan trabalhando |
| #23 | Pod Ambiente: Spark Envy Docker | Philo/time | 🔴 Alta | Base existe (Philo) |
| #24 | Pod Listener: SparkListener | time | 🔴 Alta | **Bloqueada por #27** |
| #25 | Pod Infra: ClickHouse setup | time | 🔴 Alta | Pendente |
| #26 | Pod Diagnóstico: Crew.ai + MCP | time | 🟡 Média | Bloqueada por #25 |
| #27 | ADR-005: SparkListener vs zero-JAR | Luan+Augusto | 🔴 Crítica | Decisão pendente |
| #28 | Research DataFlint — time completo | Anthony+Philo | 🟡 Média | Parcial |
| #29 | Revisão branch Augusto | Luan | 🔴 Alta | Luan trabalhando |
| #30 | On-premise / offline mode | — | 🟢 Baixa | Future |

**Dependência crítica:** o time não pode avançar em #24 (SparkListener) sem resolver #27 (decisão arquitetural). Essa é a conversa que precisa acontecer antes de qualquer linha de código.
