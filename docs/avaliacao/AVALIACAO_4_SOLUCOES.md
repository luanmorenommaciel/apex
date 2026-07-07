# Avaliação Comparativa — 4 Abordagens para Diagnóstico Spark

> **Avaliador:** Cowork (Claude / Anthropic)  
> **Data:** 2026-07-07  
> **Branches avaliadas:**  
> - `spike/apex-v0.1` (luanmorenommaciel/apex) — Aguimar  
> - `gustocezar/feature/cowork-desacoplamento-geradores` — Claude (Cowork)  
> - `gustocezar/feature/kimi-desacoplamento-geradores` — Kimi Work  
> - DataFlint — produto comercial concorrente  
>
> **Aviso de conflito de interesse:** Este documento foi produzido pela mesma LLM que implementou a solução `cowork`. A análise tenta ser honesta sobre os limites da própria solução, mas o leitor deve considerar o viés inerente.

---

## Sumário Executivo

Três implementações internas (spike, cowork, kimi) e um concorrente SaaS (DataFlint) foram comparados em cobertura de detecção, velocidade, qualidade de engenharia e maturidade.

**Conclusão principal (Cowork / Claude):** Nenhuma das três branches internas resolve o problema sozinha. A combinação mais forte é:

1. **Detecção determinística do `spike/apex-v0.1`** (5 detectores, config YAML)
2. **T1 heurístico do `kimi`** (136ms, EvidenceValidator 7/7)
3. **`apply_fix` do `cowork`** (única branch que fecha o loop no IDE)
4. **Go loader do `spike`** (produção-grade, substitui o log_poller Python)

O DataFlint prova que há mercado. Mas a arquitetura aberta local supera o SaaS em privacidade, extensibilidade e ausência de vendor lock-in.

---

## 1. spike/apex-v0.1 — A Base Mais Madura

**Responsável:** Aguimar  
**Branch:** `spike/apex-v0.1` (luanmorenommaciel/apex, commit `53479f5`)

### O que entregou

Aguimar construiu a implementação mais completa em termos de infraestrutura e cobertura de detectores. O ponto de partida correto é o dele.

**Stack completa:**
- Spark 4.1.2 + Delta Lake + MinIO + ClickHouse 26.5.1 + HyperDX
- Go eventlog-loader (produção-grade, substitui log_poller Python)
- `uv` + pyproject.toml (gestão moderna de dependências)

**5 detectores implementados:**
- `detect_skew` — ratio max/p50 com guards (min_tasks=8, min_duration_ms=5000)
- `detect_shuffle` — volume de bytes com thresholds (256MiB warn / 1GiB crit)
- `detect_plans` — re-planning AQE (>3 replans = INFO)
- `detect_gc` — pressão de GC (>10% warn / >20% crit do tempo total do stage)
- `detect_oom` — OOM kill events

**Thresholds versionados em YAML (`diagnostics.yaml`):**
```yaml
skew:
  warning_ratio: 3.0
  critical_ratio: 6.0
  min_tasks: 8
  min_duration_ms: 5000
shuffle:
  warning_shuffle_bytes: 268435456   # 256 MiB
  critical_shuffle_bytes: 1073741824 # 1 GiB
gc:
  warning_ratio: 0.10
  critical_ratio: 0.20
```

**6 workloads sintéticos:** skew, shuffle, gc, oom, cross_join, cache_heavy  
**6 MCP tools:** `list_runs`, `detect_skew`, `detect_shuffle`, `detect_plans`, `get_report`, `analyze_run`  
**CrewAI:** Diagnostic Analyst → Recommendation Writer (sem LLM é funcional)  
**HyperDX** como UI de observabilidade

### O que falta

- `apply_fix` — recomendação chega, mas o engenheiro aplica manualmente
- Benchmarks públicos (latência não foi medida e publicada)
- Baseline negativo documentado (não confirmado)
- ADRs de decisões arquiteturais

### Julgamento (Cowork / Claude)

A branch do Aguimar é a que eu adotaria como `main` da V1 se tivesse que escolher uma só. A cobertura de 5 detectores com config YAML é a fundação correta. Os outros devem contribuir features específicas por cima.

---

## 2. cowork — O Inovador de Ciclo Fechado

**Responsável:** Claude (Anthropic / Cowork)  
**Branch:** `gustocezar/feature/cowork-desacoplamento-geradores`

### O que entregou

A contribuição central do `cowork` é o único `apply_fix` entre todas as soluções avaliadas. Isso fecha o ciclo diagnóstico → IDE → fix.

**Pipeline:**
```
Event Log → MinIO → log_poller (15s) → event_log_ingest → ClickHouse
→ Crew.ai (MetricsAnalyzer + RecommendationWriter) → MCP → IDE → apply_fix
```

**5 MCP tools:** `get_findings`, `get_stage_metrics`, `list_slow_apps`, `trigger_diagnosis`, **`apply_fix`**

**ADR-005** — decisão arquitetural SparkListener vs Zero-JAR documentada formalmente.

**VALIDACAO.md** — mapeamento das issues da reunião 30/06 com status de entrega.

### O que falta

- Apenas 1 detector (skew). GC, OOM, shuffle, re-plans: não implementados.
- Sem T1 heurístico — Crew.ai é chamado para todo diagnóstico (caro e lento para jobs frequentes).
- Sem EvidenceValidator — falsos positivos não são controlados explicitamente.
- 1 workload sintético (skew) vs 6 do spike.

### Auto-crítica (Cowork / Claude)

Esta branch resolveu o problema errado primeiro. Implementar `apply_fix` antes de ter detecção robusta é como construir uma porta de saída antes do alarme. A arquitetura está correta (pipeline funcional, ADR-005 sólido), mas a prioridade deveria ter sido ampliar os detectores antes de fechar o ciclo.

O Crew.ai sendo obrigatório é um risco: se a API LLM cair, o diagnóstico para. O kimi e o spike mostraram que T1 determinístico funciona sem LLM.

---

## 3. kimi — O Especialista em Velocidade e Qualidade

**Responsável:** Kimi Work  
**Branch:** `gustocezar/feature/kimi-desacoplamento-geradores`

### O que entregou

A contribuição mais rigorosa em termos de engenharia de qualidade e latência medida.

**Pipeline em 3 tiers:**
```
T1: SQL heurístico → 136ms (sem LLM)
T2: EvidenceValidator → 198ms (7/7 regras)
T3: Runbook JSON → 0.01ms (sem LLM)
```

**Benchmarks medidos** (job `app-20260706035238-0001`, dataset real):
- T1 média: **136.40ms**
- Validator média: **197.57ms**
- T2: **0.01ms**
- Total pipeline: ~**334ms**

**EvidenceValidator com 7 regras formais** — zero falsos positivos nos testes.

**Baseline negativo** (`no_skew_baseline.yaml`) — valida que job saudável não dispara alarme.

**Docker Compose** com serviços isolados (CREI + MCP).

**LLM opcional** — T1 e T2 funcionam sem LLM. T3 (Crew.ai) é fallback para casos complexos.

### O que falta

- 2-3 detectores vs 5 do spike
- Sem `apply_fix`
- Sem HyperDX ou UI visual
- 3 workloads sintéticos vs 6 do spike

### Julgamento (Cowork / Claude)

O kimi provou o que eu não provei: velocidade e zero falsos positivos são mensuráveis. O EvidenceValidator de 7 regras é a peça que deveria existir em todas as branches. O baseline negativo é engenharia de qualidade básica que eu negligenciei.

---

## 4. DataFlint — O Concorrente Que Define o Teto

**Origem:** SaaS externo (https://dataflint.io)

### O que oferece

DataFlint é o produto SaaS de referência para diagnóstico de performance Spark. Serve como benchmark do que a versão comercial do mercado oferece.

**Capacidades principais:**
- Detecção AI-based de 10+ anti-patterns
- Suporte a EMR, Databricks, Dataproc
- Alertas Slack / Email automáticos
- UI visual rica (dashboard, drill-down por stage/task)
- Integração cloud (sem on-premise)
- Case study documentado: 100x redução de custo (SimilarWeb)

### Vantagens vs solução interna

- Pronto agora — sem infraestrutura para montar
- UI que qualquer engenheiro entende sem treinamento
- Cobertura de cloud providers nativos
- Suporte e evolução contínua

### Desvantagens críticas

- **Custo:** SaaS pago, escala com volume
- **Vendor lock-in:** dados de performance na nuvem deles
- **Opacidade:** thresholds e lógica são caixa preta
- **Sem `apply_fix`:** recomendações chegam, o engenheiro aplica
- **Sem ClickHouse local:** métricas históricas ficam no SaaS
- **Sem extensão local:** não é possível adicionar detectores customizados

### Julgamento (Cowork / Claude)

DataFlint é o concorrente que valida o mercado, não o alvo. O Apex precisa superar DataFlint em 3 dimensões onde um SaaS nunca ganha: privacidade de dados de produção, extensibilidade com detectores próprios, e `apply_fix` direto no IDE. Nas outras dimensões (UI, cobertura, cloud support), DataFlint ganha no curto prazo.

---

## 5. Análise por Categoria

### 5.1 Cobertura de Detecção

**Vencedor:** spike/apex-v0.1 = DataFlint (empatados no topo)

O gap entre spike (5 detectores) e cowork (1 detector) é inaceitável para produção. Jobs reais falham por GC, shuffle excessivo e OOM — não apenas skew. A contribuição do kimi em spill e memory são adicionais úteis.

**Caminho:** usar os 5 detectores do spike como base + spill do kimi = 6 detectores na V1.

### 5.2 Velocidade e Confiabilidade

**Vencedor:** kimi (único com benchmarks reais publicados)

334ms total é rápido. O mais importante: T1=136ms sem LLM garante diagnóstico mesmo com API LLM fora do ar. A dependência do cowork em Crew.ai para todo diagnóstico é um single point of failure.

**Caminho:** adotar T1 heurístico do kimi como tier zero, antes do LLM.

### 5.3 Ciclo IDE → Fix

**Vencedor:** cowork (único com apply_fix)

É o diferencial competitivo real vs DataFlint. Nenhum outro — interno ou externo — fecha o loop do diagnóstico até a correção aplicada no código do engenheiro.

**Caminho:** portar `apply_fix` para spike como sexta tool MCP.

### 5.4 Infraestrutura e Loader

**Vencedor:** spike/apex-v0.1 (Go loader vs Python polling)

O Go eventlog-loader do spike é produção-grade: concorrente, sem GIL, baixo footprint. O log_poller Python de 15s do cowork e kimi é suficiente para protótipo, mas não para volume de produção.

**Caminho:** adotar Go loader como padrão.

### 5.5 Qualidade e Falsos Positivos

**Vencedor:** kimi (EvidenceValidator 7/7)

Falso positivo é mais caro que falso negativo para um sistema de diagnóstico: engenheiros param de confiar no alerta. O kimi é o único que formalizou um gate de qualidade.

**Caminho:** adotar EvidenceValidator do kimi como gate obrigatório antes de acionar LLM.

### 5.6 Extensibilidade

**Vencedor:** spike/apex-v0.1 (YAML config)

Adicionar um novo limiar no spike = editar `diagnostics.yaml`. No cowork = editar código Python. O spike acertou a abstração.

---

## 6. Recomendação de Merge

> **Perspectiva: Cowork (Claude)** — construir a V1 final a partir das melhores peças de cada branch.

### Prioridade 1 — Base de detecção (do spike)
- 5 detectores do spike/apex-v0.1
- `diagnostics.yaml` para thresholds
- Go eventlog-loader

### Prioridade 2 — Qualidade de diagnóstico (do kimi)
- EvidenceValidator como gate obrigatório
- T1 heurístico sem LLM (136ms)
- Baseline negativo como teste de regressão

### Prioridade 3 — Ciclo fechado (do cowork)
- `apply_fix` como MCP tool #7
- ADR-005 como documentação arquitetural
- VALIDACAO.md como formato de rastreamento de issues

### Prioridade 4 — UI e observabilidade (do spike)
- HyperDX como dashboard
- Alertas Slack/Email (hoje só DataFlint tem)

### O que NÃO copiar

- Crew.ai obrigatório (cowork) → manter como opcional, T1 sem LLM primeiro
- log_poller Python 15s como solução final → substituir pelo Go loader
- Hardcoded thresholds (cowork) → YAML do spike

---

## 7. Onde o Apex Supera DataFlint

| Dimensão | Apex (merged) | DataFlint |
|----------|:---:|:---:|
| Privacidade (dados ficam locais) | ✅ | ❌ |
| Detectores customizáveis | ✅ | ❌ |
| `apply_fix` no IDE | ✅ | ❌ |
| Custo de operação contínua | Gratuito | 💰 SaaS |
| Vendor lock-in zero | ✅ | ❌ |
| UI visual | ✅ HyperDX | ✅ Melhor |
| Suporte cloud managed | ❌ | ✅ |
| Cobertura out-of-the-box | Construindo | ✅ Maior |

---

*Documento gerado por: Cowork (Claude / Anthropic) — 2026-07-07*  
*Para questionar esta avaliação, considere que o avaliador tem conflito de interesse na categoria "apply_fix" e "ADR documentation".*
