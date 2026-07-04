# Apex V1 — Objetivo, Arquitetura e Plano de Execução

> Gerado a partir da reunião 30/06/2026 (Luan, Augusto, Jaime, Aguimar) + estado atual do repositório.  
> Este é o documento #22 que o Luan disse que criaria. Serve como spec de alinhamento antes de dividir os pods.

---

## Objetivo (nas palavras de Luan)

> "O job rodou, eu tenho esse ID, eu falo: quero debugar esse ID. Debuga para mim."  
> — Luan, reunião 30/06, linha 224

O engenheiro está no Cursor ou Claude Code. Ele conectou o MCP do Apex. Ele fala o job ID.  
Apex retorna: o que aconteceu, por quê, e como corrigir — com o fix aplicado diretamente no código.

Isso é o **V0.1** (mínimo viável da reunião):

> "É ter ambiente que gera, SparkListener ok, básico, tudo básico e daí essas informações sendo enviadas para o ClickStack e dessas informações do ClickStack a gente começar a olhar o Crew.ai."  
> — Luan, linha 145–146

---

## Arquitetura V1 (5 componentes)

```
[Spark Envy]
    Docker com Spark 4.1.2 gerando jobs continuamente
    → Produz métricas via SparkListener

[SparkListener]  
    Injeta no job via spark.extraListeners
    → Captura stage metrics, task counts, spill, skew em tempo real

[ClickHouse]
    Armazena as métricas por app_id
    → Base de consulta para o diagnóstico

[Crew.ai]
    Recebe app_id, consulta ClickHouse
    → Raciocina sobre o problema, gera root cause + recomendação

[MCP]
    Servidor que expõe os findings ao Cursor / Claude Code
    → Engenheiro pergunta, Apex responde com fix concreto
```

---

## Estado atual: o que já existe

### ✅ Infra (Spark + ClickHouse) — Aguimar + plat-v0
Aguimar confirmou na reunião (linha 130):  
> "Acho que até a parte 3 está funcionando. O time pode verificar, enterar, pra gente partir pra parte 4 e 5."

- **plat-v0** (`gustocezar/dataship-spark-plat-v0`): Spark 4.1.2 + MinIO + ClickHouse + Spark History Server. 40 testes passando.
- **Branch do Aguimar**: Spark Envy + SparkListener + ClickHouse integrados.
- **Conclusão:** Passos 1–3 EXISTEM. Não recriar — integrar.

### ✅ SparkListener + Schema — v1-skeleton (esta sessão)
- `v1-skeleton/listener/spark_listener.py` — `ApexSparkListener` com `onStageCompleted` + `onTaskEnd`
- `v1-skeleton/listener/clickhouse_writer.py` — client para persistência
- `v1-skeleton/schema/init.sql` — tabelas `stage_metrics`, `task_metrics`, `findings` + view `suspicious_stages`
- `v1-skeleton/jobs/demo_skew_job.py` — job demo com hot key skew proposital
- **⚠ Conflito:** o v1-skeleton tem um docker-compose próprio. Precisa ser integrado ao plat-v0.

### ✅ MCP Server — v1-skeleton (esta sessão)
- `v1-skeleton/mcp/server.py` — 4 tools: `get_findings`, `get_stage_metrics`, `list_slow_apps`, `trigger_diagnosis`
- Funciona via `stdio_server` — compatível com Claude Code, Cursor, Codex
- **Falta:** testes e registro no `~/.claude/claude.json`

### ✅ Contratos Anti-Alucinação — apex/v3
Aguimar apontou na reunião (linha 136):
> "Chegou ponto que a IA começa a alucinar. A gente tem que ver onde a gente tem que parar. Pedi para estudar o Agent Spec, para ver aquela parte de contratos."

O apex/v3 JÁ RESOLVE ISSO via `scenario.yaml` — contrato que define acceptance criteria e impede alucinação do LLM. Precisamos estender o schema do scenario.yaml para cobrir também os padrões que o SparkListener vai capturar (além dos que o Watcher já cobre).

### ❌ Crew.ai — não existe ainda
- `v1-skeleton/analysis/diagnose.py` chama a API Anthropic diretamente (não é Crew.ai)
- Crew.ai é o passo 4 da arquitetura — precisa ser implementado
- **Pode ser feito agora em paralelo** (não depende da infra estar 100% pronta)

### ❌ Integração unificada — não existe ainda
- plat-v0 + Aguimar's branch + v1-skeleton são três mundos separados
- Precisam de um ponto único de entrada: `docker compose up` sobe tudo

---

## O que o Aguimar traz de novo

| Contribuição | Impacto |
|---|---|
| Steps 1–3 funcionando na branch | Não precisamos construir do zero — integrar |
| Concern: "IA alucina" | scenario.yaml já resolve — mostrar para ele |
| Estudou Agent Spec | Alinhado com o que temos em CLAUDE.md |
| Pesquisa DataFlint | Mapeou os 14 alertas → Apex pode reusar e superar |

---

## Plano de execução paralelo

### Bloqueante único: decisão ADR-005
A reunião 30/jun **implicitamente resolveu** o ADR-005: Luan escolheu SparkListener.  
Mas precisa ser **formalizado** para o time não ficar em dúvida.

**Ação imediata:** Augusto ou Luan confirmam por escrito: "V1 = SparkListener. Zero-JAR fica como opção futura."  
Quando confirmar, todos os tracks desbloqueiam.

---

### Tracks paralelos (podem rodar simultaneamente)

#### Track A — Infra unificada (owner: Aguimar)
```
plat-v0 + branch Aguimar → ponto único de entrada
```
- Importar a branch do Aguimar para o repo principal
- Substituir o docker-compose do v1-skeleton pelo plat-v0
- `APEX_CH_HOST` do v1-skeleton aponta para o ClickHouse do plat-v0
- **Skill:** `engineering:documentation` → README de como subir tudo

**Não bloqueia os outros tracks** — os outros podem usar mock data enquanto isso.

---

#### Track B — SparkListener production-ready (owner: Aguimar / Philo)
*Depende: Track A concluído*
```
spark_listener.py → battle-tested + fail-safe + testado no Spark Envy
```
- Adicionar fail-safe: exception no listener não mata o job
- Testes de integração: listener rodando no cluster real
- `spark.extraListeners=com.apex.ApexSparkListener` no config do Spark Envy
- **Skill:** `engineering:testing-strategy` → plano de testes

---

#### Track C — Crew.ai (owner: Augusto / quem puder)
*Independente — pode começar AGORA com mock data*
```
diagnose.py (Anthropic direto) → Crew.ai multi-agent
```
- Criar 2 agents Crew.ai:
  - `MetricsAnalyzer`: lê ClickHouse, identifica o padrão
  - `RecommendationWriter`: gera o fix concreto
- Contratos: cada agent recebe schema fixo (anti-alucinação)
- Output: mesmo schema JSON do `diagnose.py` atual (pattern, severity, confidence, root_cause, recommendation)
- **Skill:** `engineering:system-design` → design dos agents

---

#### Track D — Contratos anti-alucinação para SparkListener (owner: Augusto)
*Independente — pode começar AGORA*
```
scenario.yaml (zero-JAR) → estender para SparkListener findings
```
- Adicionar seção `listener_acceptance` no schema do scenario.yaml
- Definir critérios mínimos para cada padrão detectado: skew, spill, parallelism_collapse
- Isso blinda o Crew.ai contra alucinação (Aguimar's concern resolvido formalmente)
- **Referência:** `scenarios/skew_on_join_30x.yaml` como modelo

---

#### Track E — MCP + integração IDE (owner: Jaime / qualquer)
*Independente — pode começar AGORA*
```
mcp/server.py → testado e registrado no Claude Code + Cursor
```
- Testar os 4 tools com ClickHouse de mock
- Escrever guia de registro no Claude Code (`~/.claude/claude.json`)
- Escrever guia de registro no Cursor (`~/.cursor/mcp.json`)
- Demo: captura de tela / GIF do fluxo fim a fim
- **Skill:** `engineering:documentation` → guia de uso do MCP

---

## Ordem recomendada para semana 1

```
Dia 1-2: 
  ├── Todos: confirmar ADR-005 (SparkListener = V1)
  ├── Augusto: iniciar Track C (Crew.ai design)
  ├── Aguimar: iniciar Track A (infra unificada)
  └── Jaime: iniciar Track E (MCP + docs)

Dia 3-4:
  ├── Track C continua (Crew.ai implementação)
  ├── Track D: contratos scenario.yaml para listener
  └── Track A: merge + docker compose unificado

Dia 5:
  ├── Track B: SparkListener no ambiente unificado
  └── Integração fim a fim: job → listener → ClickHouse → Crew.ai → MCP
```

---

## Agents e Skills que podem nos ajudar

| Track | Skill / Agent | Para quê |
|---|---|---|
| ADR-005 | `engineering:architecture` | Formalizar a decisão SparkListener vs zero-JAR |
| Track C | `engineering:system-design` | Design do Crew.ai multi-agent (MetricsAnalyzer + RecommendationWriter) |
| Track B | `engineering:testing-strategy` | Plano de testes do SparkListener |
| Track E | `engineering:documentation` | Guia de registro do MCP no Cursor / Claude Code |
| #22 | `docx` ou `pdf` | Gerar o PDF de spec que o Luan mencionou para o time |
| Todos | Claude Cowork (eu) | Gerar código, revisar PRs, escrever ADRs, criar specs de cada pod |

**Paralelismo real:** Tracks C, D e E podem começar hoje mesmo. Track A depende do Aguimar. Track B depende de A. A única dependência serial é A→B.

---

## O que falta para V0.1 estar "pronto"

1. ☐ ADR-005 formalizado (Luan + Augusto, 1 hora)
2. ☐ Track A: docker compose unificado (Aguimar, 1-2 dias)
3. ☐ Track C: Crew.ai mínimo (2 agents, diagnóstico funcional)
4. ☐ Demo fim a fim: `spark-submit job.py` → MCP responde no Claude Code

Quando esses 4 itens estiverem verdes, o Luan tem o que pediu:  
> "Eu quero muito ver isso funcionando. Quando a gente vê pelo menos o V1 bem basicão vai dar visão para vocês."

---

*Documento gerado por Claude Cowork (Sonnet) em 04/07/2026, a partir da transcrição reunião 30/06 + estado atual do repositório.*  
*Autoria LLM: Claude Sonnet 4.6 — síntese + estruturação.*
