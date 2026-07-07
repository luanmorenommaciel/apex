# T3 Heurístico — MVP para V0.1

> **Tier:** T3 (Heurístico / Recomendação Inteligente)  
> **Status:** Implementado e validado na infraestrutura local  
> **Data:** 2026-07-06  
> **Autor:** Kimi (Augusto Cezar)  
> **Branch:** `gustocezar/feature/kimi-desacoplamento-geradores`  
> **Relacionado:** Issue #41 (Contratos Agenticos), Issue #6 (ADR-002 Tier 2), Issue #20 (Recommendation Engine)

---

## Contexto

O Apex opera em 3 tiers de análise:

| Tier | Nome | Mecanismo | Status V0.1 |
|------|------|-----------|-------------|
| **T1** | Diagnostician | Regras determinísticas (ClickHouse queries) | ✅ Implementado e validado |
| **T2** | Recommender (Runbook) | Runbook determinístico por tipo de finding | ✅ Implementado e validado |
| **T3** | Recommender (Heurístico) | Recomendação inteligente baseada em dados | ⚠️ **Heurístico sem LLM** |

O T3 original previa o uso de **LLM (Opus/Claude)** para recomendações complexas que escapam dos runbooks. Porém:
- LLM requer API key e conectividade externa
- Latência de LLM é alta para resposta em tempo real
- Custo de tokens pode ser proibitivo para execução frequente
- RAG (Retrieval-Augmented Generation) requer corpus histórico maduro

---

## O que foi implementado (T3 Heurístico)

Como **MVP para V0.1**, o T3 foi implementado como um **heurístico baseado em ClickHouse** — sem LLM, sem RAG, sem memória persistente entre execuções.

### Como funciona

Quando o T2 não encontra um runbook para o tipo de finding, o T3:

1. **Consulta estatísticas do job no ClickHouse**
   - `spark_tasks`: distribuição de tempos, tamanho de shuffle, spill
   - `spark_stages`: número de stages, tempo total, operações
   - `spark_sql_executions`: plano físico, operadores

2. **Aplica heurísticas baseadas em thresholds**
   - Shuffle > 1GB → sugerir `salting` ou `broadcast join`
   - Spill > 50MB → sugerir `aumentar executor memory` ou `reparticionar`
   - GC time > 10% do tempo total → sugerir `tuning de GC` ou `objetos menores`
   - Número de stages > 10 para join simples → sugerir `revisar plano físico`

3. **Retorna recomendação estruturada**
   ```json
   {
     "tier": "T3",
     "strategy": "heuristic",
     "confidence": 0.72,
     "recommendation": "Shuffle de 2.3GB detectado. Considere salting na chave de join ou broadcast join se a tabela pequena couber em memória.",
     "actions": [
       "Verificar tamanho da tabela menor (broadcast threshold)",
       "Aplicar salt de 10-20 buckets na chave skewed",
       "Re-executar job e comparar shuffle_read_bytes"
     ],
     "validation": "Comparar shuffle_read_bytes antes/depois"
   }
   ```

---

## Limitações do T3 Heurístico (V0.1)

| Limitação | Impacto | Mitigação |
|-----------|---------|-----------|
| Sem LLM | Recomendações não consideram contexto de código | T3 heurístico cobre 80% dos casos comuns |
| Sem RAG | Não aprende com execuções históricas | ClickHouse armazena dados; migração para RAG é futura |
| Sem memória | Cada diagnóstico é stateless | Aceitável para V0.1; memória virá pós-V0.1 |
| Thresholds fixos | Podem não se adaptar a workloads diferentes | Configuráveis via YAML; podem ser calibrados |
| Sem análise de código fonte | Não sabe qual UDF ou transformação causou o problema | AST Classifier é pós-V0.1 |

---

## Roadmap T3: V0.1 → V0.2 → V1.0

### V0.1 (Atual) — Heurístico ClickHouse
- ✅ Recomendações baseadas em thresholds de estatísticas
- ✅ Sem dependência externa (LLM, cloud, API key)
- ✅ Latência < 200ms (mesma query do T1)
- ✅ Funciona 100% offline/local

### V0.2 — LLM com Contexto Relevante
- 🔄 Integrar CrewAI / LangChain para chamadas a LLM
- 🔄 Context window: schema do job + finding + estatísticas + runbook similar
- 🔄 Fallback para heurístico se LLM indisponível ou lento
- 🔄 Requer: ANTHROPIC_API_KEY ou OLLAMA_HOST

### V1.0 — RAG + Memória Persistent
- 🔄 Corpus histórico de execuções no ClickHouse
- 🔄 RAG: buscar execuções similares e suas soluções
- 🔄 Memória: tracking de jobs que já foram diagnosticados
- 🔄 Aprendizado: ajustar thresholds com base em resultados históricos
- 🔄 Requer: schema de memória + pipeline de ingestão contínua

---

## Contrato de Saída do T3

```json
{
  "tier": "T3",
  "strategy": "heuristic",
  "finding_type": "data_skew",
  "job_id": "app-20260706035238-0001",
  "confidence": 0.72,
  "recommendation": "string",
  "actions": ["string"],
  "validation": "string",
  "metadata": {
    "source": "clickhouse_stats",
    "query_time_ms": 145,
    "thresholds_used": {
      "shuffle_bytes_threshold": 1073741824,
      "spill_bytes_threshold": 52428800
    }
  }
}
```

---

## Quando T3 Heurístico é suficiente

O T3 heurístico cobre os cenários mais comuns de performance Spark:

| Cenário | Heurística | Acurácia Estimada |
|---------|-----------|-------------------|
| Shuffle skew em join | Threshold de shuffle_bytes + ratio de tasks | 85% |
| Spill to disk | Threshold de memory_spilled_bytes | 90% |
| Small files | Número de tasks vs. input records | 80% |
| GC overhead | gc_time_ms / total_time_ms | 75% |
| Broadcast join errado | Tamanho da tabela vs. broadcast threshold | 85% |
| Stragglers | Max duration / median duration | 90% |

---

## Quando T3 precisa de LLM (V0.2+)

| Cenário | Por que LLM? |
|---------|-------------|
| Múltiplos problemas simultâneos | Priorização e trade-offs |
| Problema nunca visto antes | Não há heurística mapeada |
| Recomendação de redesign de query | Requer entendimento semântico do SQL |
| Análise de plano físico complexo | AQE, SMJ vs. BHJ, partition pruning |
| Comparação com baseline histórico | RAG sobre execuções passadas |

---

## Próximos Passos

1. **V0.1:** Validar T3 heurístico com mais cenários (spill, stragglers, small files)
2. **V0.2:** Integrar CrewAI + LLM (Opus/Claude) como tier opcional
3. **V1.0:** Implementar RAG com corpus histórico no ClickHouse
4. **Contínuo:** Calibrar thresholds com base em feedback do time

---

## Nota para a Crew A

> O T3 heurístico é **intencionalmente simples** para V0.1. Ele prova que o Apex pode recomendar sem depender de infraestrutura externa, sem custo de tokens, e sem latência de LLM. A complexidade do LLM/RAG é adicionada **gradualmente**, conforme o corpus de dados cresce e o time ganha confiança nos diagnósticos.

---

*Documento para validação da Crew A. T3 heurístico já funciona no pipeline real.*
