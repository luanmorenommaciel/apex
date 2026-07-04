# Spark — Dores Reais da Comunidade + Casos DataFlint × Correlação Apex

> Pesquisa de campo: Medium, Databricks Community, Stack Overflow, GitHub, InMobi Engineering  
> Casos DataFlint: 3 case studies oficiais (Jan–Apr 2026)  
> Gerado em: 2026-07-01

---

## Parte 1 — O que a comunidade está falando

### 1.1 Principais dores por frequência (fontes: Medium, Databricks Community, Pinterest Engineering, AWS, DZone)

| Rank | Problema | Sintoma relatado | Frequência |
|------|----------|-----------------|------------|
| 1 | **Data Skew** | "Stage com 199 tasks terminando em 2s e uma levando 38 min" | Ubíquo |
| 2 | **OOM por causa errada** | "Aumentamos a memória e não resolveu nada" | Muito alto |
| 3 | **Collapso de paralelismo silencioso** | "O código está certo, Spark só usou 83 de 800 cores" | Alto |
| 4 | **Particionamento default errado** | "200 partitions funciona para nenhum workload" | Alto |
| 5 | **Small files** | "Pipeline de leitura travando — 10k arquivos de 1MB" | Alto |
| 6 | **UDFs Python lentos** | "37x mais lento que função nativa — passei 2 dias otimizando memória" | Médio |
| 7 | **Broadcast join perdido** | "Threshold de 10MB ignora tabela de 50MB que deveria ser broadcast" | Médio |
| 8 | **coalesce() antes de write** | "coalesce(2) antes do Iceberg destruiu o stage inteiro — estava em código de terceiro" | Médio |
| 9 | **Cross-platform config divergência** | "Mesmo job: 50min Databricks, 3h EMR — sem nenhuma mudança de código" | Médio |
| 10 | **Cost attribution** | "Spark não rastreia custo por job out-of-the-box" | Crescente |

### 1.2 Citações diretas da comunidade (fontes primárias)

> **"Most Spark performance problems aren't resource problems — they're misunderstanding problems. Engineers throw memory at skew."**  
> — Medium, Mar 2026 (10M+ impressions nos posts sobre Spark skew)

> **"SimilarWeb's team turned to AI models to help diagnose the issue, but conventional AI assistants couldn't provide meaningful hints. The code was correct. The problem wasn't the code at all."**  
> — DataFlint, Jan 2026

> **"Data engineers spend 30%+ of their time debugging Spark plans and restarting failed jobs instead of building new pipelines."**  
> — Towards AI / Debugging Spark at Scale

> **"Pinterest reports that 4.6% of their 90,000+ daily Spark jobs fail from OOM, and most are caused by skew and bad joins, not insufficient memory."**  
> — Pinterest Engineering (Medium)

> **"Spark doesn't provide out-of-the-box support to measure and report job-level cost."**  
> — InMobi Engineering, Jul 2025

> **"The factors that determine whether your job runs in 40 minutes or 3 hours live outside your codebase."**  
> — DataFlint / SimilarWeb case study

> **"Before using DataFlint, the team tried an open-source MCP server for the Spark History Server. After several days of prompt engineering, the best it returned were generic suggestions like 'increase executor memory' and 'add more partitions'."**  
> — Natural Intelligence case study, Apr 2026

### 1.3 Gap confirmado: o mercado quer correlação código ↔ runtime

Três fontes independentes confirmam o mesmo gap:

1. **InMobi Engineering (Jul 2025)** construiu um framework próprio de cost attribution porque "job context is often lost after execution." Solução custom em vez de ferramenta dedicada.

2. **Natural Intelligence (Apr 2026)** tentou open-source MCP antes do DataFlint — recebeu sugestões genéricas. O problema estava em código de terceiro 5 arquivos de profundidade. Sem rastreio do plano físico, impossível de achar.

3. **SimilarWeb** — o código estava correto. O problema era o comportamento do optimizer do Spark (predicate pushdown silencioso). Nenhuma ferramenta de análise estática resolve isso.

**Conclusão do mercado**: a dor real não é "não sei que existe skew" — é "sei que existe skew mas não consigo conectar ao código que causou."

---

## Parte 2 — Casos Oficiais DataFlint (3 cases, completos)

### CASE 1: SimilarWeb — 90x faster, 160x cheaper (Jan 2026)

**Empresa**: SimilarWeb (digital market intelligence)  
**Plataforma**: Databricks  
**Sintoma**: Job falhando após 22.2h em 200 máquinas. Código correto. AI genérica não ajudou.

**Root cause identificado pelo DataFlint**:
- Spark usava apenas **83 de 800 cores disponíveis** (10% utilização)
- Por quê: um `filter` sobre resultado de UDF ativou **predicate pushdown**
- Spark moveu o filter ANTES do repartition — **silenciosamente bypassando o repartition**
- O input tinha exatamente 83 arquivos → 83 tasks, independente da lógica de repartition
- UDF rodando duas vezes (sem `asNondeterministic()`)

**Fix**: 4 linhas — `asNondeterministic()` + `cache()` antes do write + troca de tipo de máquina (m-type → compute-optimized cd-fleet.12xlarge)

**Resultado**: 22h → 15 min | 200 máquinas → 20 | 90x faster | 160x cheaper

---

### CASE 2: SimilarWeb — 3h → 20min, migração Databricks → EMR (Mar 2026)

**Empresa**: SimilarWeb  
**Plataforma**: Databricks (dev) → EMR (staging/prod)  
**Sintoma**: Mesmo job, mesmo código → 50min no Databricks, 3h no EMR.

**Root cause identificado pelo DataFlint**:
- **EMR default**: `spark.sql.files.maxPartitionBytes = 128MB` → Spark divide arquivos de ~773MB em 6 tasks cada
- **Databricks**: otimiza automaticamente via stage retries, reduzindo de 87.010 tasks para 3.621
- EMR: 167.000 tasks × 20.000 partições = **3,36 bilhões de shuffle read files**
- Skew de **21x** flagrado pelo DataFlint imediatamente no Job Debugger
- 1.000 partitions com **7,88 GiB médio** cada → spill massivo

**Fix**: `spark.sql.files.maxPartitionBytes=1GB` → 1 task por arquivo, zero spill

**Resultado**: 3h → 20min | Zerou spill | Zerou falhas de tasks

---

### CASE 3: Natural Intelligence — 30x stage speedup, OOM 3AM (Apr 2026)

**Empresa**: Natural Intelligence (processamento de dados web, EMR + Iceberg)  
**Plataforma**: AWS EMR + Apache Iceberg  
**Sintoma**: Pipeline hourly breachando SLA de 30min (44min em pico). OOM crash às 3AM. Adicionaram mais máquinas → não ajudou nada.

**Root cause identificado pelo DataFlint**:
- Stage com **82 de 84 cores ociosos** (2.38% de utilização)
- Apenas 2 tasks processando 6.93 GiB cada → **11.2 GiB de spill**
- Causa: `.coalesce(2)` enterrado **5 arquivos de profundidade** em uma **classe utilitária de terceiro** do Iceberg — não estava no código da NI
- Agravante: produtor upstream passou a mandar string vazia em vez de `null` para `origin_uid` → skew de **37.12x** adicional (causa raiz mais profunda)
- Open-source MCP que tentaram antes: devolveu "aumente a memória executora" e "adicione mais partições" — genérico, inútil

**Fix**: `repartition(200)` em vez de `coalesce(2)` + broadcast joins + salting de hot keys + instâncias r6g memory-optimized

**Resultado**: Stage 5min → 10seg (30x) | Spill 11.2 GiB → 0 B | OOM eliminado | SLA atendido mesmo com bug do produtor ainda ativo

---

## Parte 3 — Tabela Comparativa: Casos DataFlint × Como Apex Seria Diferente

| Dimensão | CASE 1: SimilarWeb (90x) | CASE 2: SimilarWeb (EMR) | CASE 3: Natural Intelligence (30x) |
|----------|--------------------------|--------------------------|-------------------------------------|
| **Anti-pattern real** | Predicate pushdown bypassando repartition → parallelism collapse | Config default divergente Databricks vs EMR → partitions gigantes + shuffle explosion | coalesce() em lib de terceiro → parallelism collapse + spill |
| **Sinal no event log** | Task count = 83, cores = 800 → wasted cores visível | 1.000 partitions, 7.88 GiB avg → large partition size visível | 2 tasks, 84 cores ociosos, 11.2 GiB spill → tudo visível |
| **DataFlint detectou?** | ✅ Via IDE Copilot + plano físico + runtime context | ✅ Via Job Debugger heat map + comparação cross-run | ✅ Via Agentic Copilot rastreando 5 arquivos de profundidade |
| **Como DataFlint resolveu** | LLM com contexto de produção (plano físico + file distribution) — requereu JAR + MCP + IDE | Comparou dois runs (Databricks vs EMR) via Dashboard fleet — requereu JAR + SaaS | Rastreou chamada em lib de terceiro via plano de execução — requereu IDE + codebase access |
| **Apex v4 detecta?** | 🔶 Parcialmente — wasted cores ratio calculável de SparkListenerStageCompleted (task_count vs executor_count × cores) | 🔶 Large partition size é detectável — `bytes_written / num_tasks` no event log | 🔶 2 tasks + 11.2 GiB spill → ambos detectáveis no event log via SpillMetrics |
| **Apex v4 limitação** | Apex não cruza task count vs available cores automaticamente hoje. Não tem scenario `parallelism_collapse` | Apex não tem comparação cross-run nem cross-platform. Não tem scenario `large_partition` | Apex detecta sintoma mas não rastreia causa em lib de terceiro (callSite aponta pra código da NI, não lib Iceberg) |
| **Como Apex seria diferente** | ⭐ Zero JAR. Apex lê o mesmo dado (task count = 83, stage summary) sem precisar de plugin. DataFlint precisa do JAR rodando no cluster | ⭐ oracle.py: Apex poderia comparar dois runs do mesmo scenario. DataFlint SaaS compara — DataFlint OSS não | ⭐ Apex detecta o sintoma (2 tasks, 82 cores idle, spill) sem JAR. Para a causa na lib de terceiro: gap real que só resolveremos com callSite → git |
| **Scenario Apex necessário** | `parallelism_collapse.yaml` — wasted cores rate + task undercount vs available cores | `large_partition_size.yaml` — avg partition bytes > threshold + spill correlation | `coalesce_before_write.yaml` — spill + 2 tasks + coalesce operator no plano (detectável em AQE plan) |
| **Onde Apex supera DataFlint** | Apex roda sem JAR no cluster. DataFlint Case 1 requeria IDE Copilot + MCP + SaaS | Apex oracle.py é o único mecanismo de validação entre runs. DataFlint dashboard é visual, não auditável | Apex emite `root_cause` com hot key, ratio, recomendação estruturada. DataFlint retorna fix em linguagem natural |
| **Onde DataFlint supera Apex** | DataFlint conectou IDE ao runtime via MCP — engenheiro viu o fix no VS Code sem sair do editor | DataFlint comparou Databricks vs EMR visualmente — UX superior | DataFlint rastreou 5 arquivos de profundidade em lib de terceiro — Apex não faria isso hoje |

---

## Parte 4 — Correlação Problemas da Comunidade × Versões Apex

| Problema da Comunidade | Apex v3 | Apex v4 | Próxima versão (v5) |
|-----------------------|---------|---------|----------------------|
| Data Skew (join key) | ✅ SkewWatcher básico | ✅ AQE-aware + root_cause com hot key + ratio calibrado | — |
| Parallelism collapse (wasted cores) | ❌ | ❌ | 🔶 `parallelism_collapse.yaml` |
| OOM por skew (não por memória) | ❌ | 🔶 Skew detectado; não testa spill | 🔶 `memory_under_provisioning.yaml` + spill correlation |
| Small files (read) | ❌ | ❌ | 🔶 `small_files_read.yaml` |
| Large partition size | ❌ | ❌ | 🔶 `large_partition_size.yaml` |
| Broadcast miss (SMJ para tabela pequena) | ❌ | ❌ | 🔶 `broadcast_missed.yaml` |
| coalesce() antes de write | ❌ | ❌ | 🔶 sintoma detectável via plano + spill |
| UDF Python lento | ❌ | ❌ | 🔴 gap real — duração de UDF não está no event log sem JAR |
| Cross-platform config divergência | ❌ | ❌ | 🔶 oracle.py extended: comparar dois runs do mesmo scenario em plataformas diferentes |
| Cost attribution por job | ❌ | ❌ | 🔶 task_metrics × cluster cost (requer integração com billing do cloud) |
| Predicate pushdown bypassing repartition | ❌ | ❌ | 🔶 detectável indiretamente via task_count << expected_cores (parallelism collapse) |
| Código em lib de terceiro | ❌ | ❌ | 🔴 gap estrutural — callSite aponta para código próprio, não libs. Requer análise do bytecode ou plano físico |

**Legenda**: ✅ Implementado | 🔶 Planneable com scenario.yaml novo | 🔴 Gap real (decisão estratégica necessária)

---

## Parte 5 — Insight estratégico: o padrão que aparece nos 3 casos

Os 3 casos DataFlint têm uma estrutura comum:

```
Sintoma visível no event log (sempre):
  → task count anormalmente baixo
  → spill alto
  → cores idle

Causa invisível sem contexto de código/runtime:
  → predicate pushdown reordenou operações  (Case 1)
  → config default diferente por plataforma  (Case 2)
  → coalesce() em lib de terceiro            (Case 3)
```

**O event log sempre tem o sintoma. A causa raiz está no runtime context.**

DataFlint conecta os dois via JAR + IDE + MCP.  
Apex conecta os dois via event log (sintoma) + callSite → git (causa) — sem JAR.

**A proposta de valor distinta do Apex**: detectar os mesmos sintomas sem precisar que o engenheiro instale nada no cluster, e correlacionar com o código via callSite (para causas no código próprio) sem depender de um agente IDE conectado.

O gap real do Apex: causas em libs de terceiro (Case 3). Isso é uma limitação legítima, e não um defeito — o Apex seria honesto: "detectei 2 tasks em 84 cores e 11.2 GiB de spill, mas a causa está em código fora do seu callSite. Investigue o operador Coalesce no plano físico na linha X."

---

*Fontes:*  
*Community: [Medium/Spark Performance](https://alper-korukcu.medium.com/7-things-most-data-engineers-get-wrong-about-spark-performance-e677ab1f91a3) · [Pinterest Engineering](https://medium.com/pinterest-engineering/drastically-reducing-out-of-memory-errors-in-apache-spark-at-pinterest-c55d7dac2257) · [InMobi Engineering](https://technology.inmobi.com/articles/2025/07/16/cracking-the-cost-code-building-a-scalable-observability-framework-forapache-spark)*  
*Cases: [DataFlint/SimilarWeb 1](https://www.dataflint.io/resources/blog/similarweb-ai-spark-optimization-case-study) · [DataFlint/SimilarWeb 2](https://www.dataflint.io/resources/blog/similarweb-spark-runtime-3h-to-20min) · [DataFlint/Natural Intelligence](https://www.dataflint.io/resources/blog/ni-spark-hidden-bug-30x-improvement)*
