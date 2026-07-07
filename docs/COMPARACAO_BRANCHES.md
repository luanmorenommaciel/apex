# Comparação de Branches — Augusto (cowork) vs Kimi

> Análise das duas abordagens paralelas de V1 do Apex para revisão do Commander (Luan).
>
> **Branch A:** `gustocezar/feature/cowork-desacoplamento-geradores` — construída com Claude (Cowork)  
> **Branch B:** `gustocezar/feature/kimi-desacoplamento-geradores` — construída com Kimi Work  
> **Data:** 2026-07-06

---

## 1. Resumo executivo

Ambas as branches resolvem o mesmo problema: conectar event logs Spark ao diagnóstico LLM e entregar o resultado via MCP. As abordagens divergem em arquitetura, velocidade de diagnóstico e profundidade de produto.

| Dimensão | Cowork (Claude) | Kimi |
|----------|-----------------|------|
| Agentes LLM | 2 (MetricsAnalyzer + RecommendationWriter) | 3 (T1 Diagnostician + T2 Recommender + T3 Heuristic) |
| Velocidade diagnóstico | ~30–60s (LLM sempre) | ~334ms total (T1 heurístico ~136ms) |
| Deploy | Scripts Python diretos | Docker Compose (CREI + MCP como serviços) |
| MCP tools | 5 (`get_findings`, `get_stage_metrics`, `list_slow_apps`, `trigger_diagnosis`, `apply_fix`) | 2 (`query_job`, `get_recommendations`) |
| Apply fix automático | ✅ `apply_fix` edita o arquivo PySpark | ❌ Não implementado |
| Validação com dado real | ✅ Pipeline testado hoje com dados reais | ✅ Validado com `app-20260706035238-0001` |
| Baseline negativo (falso positivo) | ❌ Não tem | ✅ `no_skew_baseline.yaml` |
| ADR formalizado | ✅ ADR-005 | ❌ Não tem |
| Documentação competitiva DataFlint | ✅ `docs/competitive/` completo | ✅ Tabela no README |

---

## 2. Arquitetura — lado a lado

### Cowork (Claude)
```
Event Log (MinIO/local)
    ↓ log_poller.py (15s polling)
event_log_ingest.py
    ↓
ClickHouse (apex.stage_metrics + apex.task_metrics)
    ↓
crew_diagnose.py (Crew.ai 2 agentes sequenciais)
    ↓ ApexFinding (Pydantic, anti-alucinação)
ClickHouse (apex.findings)
    ↓
MCP server.py (5 tools) → IDE do engenheiro
    ↓ apply_fix
Arquivo PySpark do engenheiro (editado pelo LLM + backup)
```

### Kimi
```
Event Log (MinIO/local)
    ↓ Go Loader (plat-v0, externo)
ClickHouse (spark_raw_events, stages, tasks — fork Gabriel)
    ↓
CREI (docker service na porta 3001)
    ├─ T1 Diagnostician (heurístico ~136ms)
    ├─ T2 Recommender (LLM fallback + runbooks JSON)
    └─ T3 Heuristic (sem Ollama, preserva T2)
    ↓ EvidenceValidator (8 regras)
MCP Server (FastMCP porta 3000, 2 tools) → IDE do engenheiro
```

---

## 3. Diferenças técnicas principais

### 3.1 Velocidade vs profundidade de análise

O Kimi introduz **T1 heurístico** — um diagnosticador determinístico (sem LLM) que roda em ~136ms e detecta skew, spill e padrões conhecidos por regras diretas. O LLM só é chamado quando T1 não tem confiança suficiente (T2 fallback).

O Cowork vai direto ao Crew.ai a cada diagnóstico. Mais lento, mas a recomendação é mais rica e contextualizada — o LLM vê os dados reais e escreve o fix com exemplo de código.

**Impacto:** Kimi é melhor para monitoramento contínuo (alta frequência). Cowork é melhor para diagnóstico profundo por demanda.

### 3.2 apply_fix — exclusivo do Cowork

O Cowork tem a ferramenta `apply_fix` no MCP: o engenheiro chama de dentro do IDE, o servidor lê o finding do ClickHouse, passa para o LLM, que edita o arquivo `.py` diretamente e salva backup.

O Kimi não tem equivalente — entrega o runbook mas o engenheiro aplica manualmente.

**Impacto:** Isso resolve diretamente o ponto *"aplica nossa sugestão"* pedido pelo Luan na reunião de 30/06.

### 3.3 Runbooks JSON (Kimi) vs Recomendação LLM (Cowork)

O Kimi usa runbooks versionados em JSON (`skew_on_join.json`, `spill_to_disk.json`) — determinísticos, auditáveis, fáceis de editar sem LLM. O T2 usa LLM só como fallback quando o runbook não cobre o padrão.

O Cowork gera a recomendação via LLM a cada diagnóstico — mais flexível, mais custoso, menos auditável.

**Impacto:** Para ambientes enterprise (on-premise, sem API externa), o modelo de runbooks do Kimi é mais seguro. Para flexibilidade e cobertura de padrões novos, o Cowork é mais robusto.

### 3.4 Baseline negativo (Kimi)

O Kimi tem `no_skew_baseline.yaml` — um cenário sem anti-pattern para validar falsos positivos. O Cowork não tem.

**Impacto:** Sem baseline negativo, não há como garantir que o sistema não gera alertas em jobs saudáveis.

### 3.5 Infraestrutura — acoplamento

O Kimi depende explicitamente do Fork Gabriel (`dataship-spark-plat-v0`) como infraestrutura externa. O CREI e MCP se conectam à rede Docker do Gabriel.

O Cowork é mais standalone — o `log_poller.py` pode apontar para MinIO ou para diretório local, sem depender da rede Docker do Gabriel.

---

## 4. O que cada um tem que o outro não tem

### Exclusivo Cowork
- `apply_fix` MCP tool (edita arquivo PySpark do engenheiro)
- `list_slow_apps` (top jobs mais lentos das últimas N horas)
- ADR-005 formalizado (`docs/adr/ADR-005-sparklistener-vs-zero-jar.md`)
- Análise competitiva completa DataFlint (`docs/competitive/`)
- VALIDACAO.md (mapa issues → entregue)
- Apresentação HTML 8 slides para Luan
- `apply_fix` com backup automático

### Exclusivo Kimi
- T1 heurístico (~136ms, sem LLM)
- T3 fallback sem Ollama
- EvidenceValidator (8 regras de qualidade explícitas)
- Runbooks JSON versionados (`skew_on_join.json`, `spill_to_disk.json`)
- Baseline negativo (`no_skew_baseline.yaml`)
- Docker Compose para CREI + MCP como serviços
- SpillWatcher + MemoryWatcher independentes
- Integração explícita com rede Docker do Fork Gabriel

---

## 5. Recomendação de merge

As duas abordagens são **complementares**, não concorrentes. Para a V1 ideal, o time deveria combinar:

| Componente | Origem | Por quê |
|-----------|--------|---------|
| T1 heurístico (136ms) | Kimi | Diagnóstico rápido sem LLM — essencial para produção |
| Crew.ai 2 agentes (profundo) | Cowork | Recomendação rica com código de exemplo |
| EvidenceValidator 8 regras | Kimi | Previne falsos positivos antes de chamar LLM |
| `apply_fix` MCP tool | Cowork | Fecha o loop — pedido explícito do Luan |
| Runbooks JSON | Kimi | Auditabilidade e suporte on-premise |
| ADR-005 + docs | Cowork | Registro arquitetural formal |
| Baseline negativo | Kimi | Prevenção de falsos positivos |
| Docker Compose (serviços) | Kimi | Deploy mais limpo para o time |

**Fluxo ideal combinado:**
```
Event Log → T1 heurístico (136ms)
    ├─ Confiança alta → entrega finding direto
    └─ Confiança baixa → Crew.ai 2 agentes (profundo)
         ↓ EvidenceValidator
         ↓ ApexFinding → ClickHouse
         ↓ MCP: apply_fix edita o arquivo do engenheiro
```

---

## 6. Links diretos

- Branch Cowork: https://github.com/luanmorenommaciel/apex/tree/gustocezar/feature/cowork-desacoplamento-geradores
- Branch Kimi: https://github.com/luanmorenommaciel/apex/tree/gustocezar/feature/kimi-desacoplamento-geradores
