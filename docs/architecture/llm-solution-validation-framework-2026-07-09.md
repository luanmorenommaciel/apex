# LLM Solution Validation Framework — Campeonato das Soluções Apex

> **Data:** 2026-07-09 · **Avaliador:** Claude (Cowork) · **Para:** Commander Luan + Crew A
>
> **Conflito de interesse declarado:** este documento foi produzido pela mesma LLM que implementou a branch `cowork`. Toda pontuação abaixo se apoia em **evidência executada nesta sessão** (testes rodados, compilação verificada, código inspecionado) — não em autoavaliação nem nas avaliações das outras LLMs. Onde não pude verificar, está marcado como não-verificado.

---

## 1. O método

Cada LLM (Claude/Cowork, Kimi, Codex, spike humano+LLM) gerou a sua melhor solução. Este framework faz três coisas:

1. **Compara** as soluções contra critérios com pesos, derivados das premissas do Luan (reunião 30/06).
2. **Valida** cada claim com evidência executável — nenhuma parte entra na solução final por reputação.
3. **Compõe** as melhores partes numa solução única, que só avança **gate por gate** (§7).

Regra de ouro: *claim sem gate verde não entra no merge.*

---

## 2. Premissas do Luan (fonte: transcrição 30/06 + issues #22–#27)

| # | Premissa | Origem |
|---|----------|--------|
| L1 | Arquitetura em 4 passos: **Spark Envy → SparkListener → ClickHouse → Crew.ai → MCP** | #22, ADR-005 |
| L2 | `docker compose up` sobe tudo sem configuração manual | #23 |
| L3 | Listener injeta via `spark.extraListeners`, **fail-safe** (exception não mata o job) | #24 |
| L4 | ClickHouse com schema definido, query por `app_id`/`job_id` | #25 |
| L5 | "Crew.ai vai olhar e vai falar qual o problema" — diagnóstico agêntico | #26 |
| L6 | Fix entregue **via MCP no IDE** + "aplica nossa sugestão" | #26, transcrição |
| L7 | Decisão SparkListener vs zero-JAR formalizada em ADR | #27 → ADR-005 ✅ |

Qualquer solução final que não satisfaça L1–L7 não é o V1 do Luan, por melhor que seja em outra dimensão.

---

## 3. Critérios e pesos (proposta — Luan ajusta)

| Critério | Peso | Racional |
|----------|------|----------|
| C1 · Aderência à arquitetura V1 (L1–L7) | 25% | É o que foi pedido; elegância fora do escopo não conta |
| C2 · Cobertura de detecção (nº de anti-patterns com detector real) | 20% | Jobs reais falham por GC/OOM/shuffle, não só skew; DataFlint tem ~14 |
| C3 · Confiabilidade (validator, baseline negativo, anti-falso-positivo) | 15% | Alerta falso mata a confiança do engenheiro no produto |
| C4 · Fechamento de loop no IDE (MCP + apply) | 15% | Diferencial vs DataFlint; pedido direto do Luan (L6) |
| C5 · Qualidade de engenharia (testes, CI, config versionada, reprodutibilidade) | 15% | "Done local ≠ done" |
| C6 · Custo/latência (LLM opcional, não obrigatório) | 10% | Monitoramento contínuo não pode custar 30–60s + API por job |

---

## 4. Evidência verificada (o que EU executei em 08–09/07)

| Solução | O que verifiquei | Resultado |
|---------|------------------|-----------|
| **cowork** `1c675cd` | `pytest tests/` local; gate de cenário completo (generator→watcher); inspeção `apply_fix`/MCP | ✅ 20 passed, 1 skip (dep. `zstandard`); GATE VERDE 27.9x; 2 bugs de CI que EU encontrei e corrigi em `0ddb550` |
| **spike** `53479f5` | `pytest tests/apex` no clone; inspeção dos 5 detectores + `diagnostics.yaml` + fakes | ✅ 22 passed (test_crew_tools não coletou: falta crewai no ambiente — dependência, não bug) |
| **kimi remoto** `e271e32` | Estrutura `go-apex/`; tentativa de build | ❌ **sem `go.sum` → nunca compilou**; zero testes; `no_skew_baseline.yaml` sumiu dos scenarios; a própria doc da branch admite "traduzido, não compilado" |
| **kimi Python local** (`apex-kimi-product-v0.1/`) | `pytest tests/unit` | 🟡 9 passed, **3 failed** (2 exigem Ollama online — ambiente; 1 falha real em `test_t3_heuristic_spill` a investigar). Validator + baseline + runbooks existem |
| **codex** `64478f6` (local, `apex-official`) | `pytest tests/` em cópia isolada; inspeção do harness Commander V0.1 | ✅ **44 passed** — a suite mais completa das 4. Harness pequeno (~200 linhas): contrato `job_id` → telemetria → store NDJSON (simula ClickStack) → diagnóstico determinístico → CLI. A própria doc é honesta: **sem** listener real, ClickHouse, Crew.ai, MCP ou apply — simulação local do fluxo, não plataforma |
| **DataFlint** | Estudo em `docs/competitive/` (07/07) | ⚪ Não reverificado na web nesta sessão; tratado como benchmark de referência, não como candidato |

> Divergência importante vs a tabela das outras LLMs: **"Kimi = melhor disciplina" era verdade na versão Python, mas a branch remota regrediu** — o pivô para Go perdeu os testes, o baseline e a executabilidade. Disciplina que não compila não é disciplina.

---

## 5. Scorecard (0–5 por critério, ponderado)

| Critério (peso) | spike | cowork | kimi-Py local | kimi-Go remoto | codex |
|---|---|---|---|---|---|
| C1 Arquitetura V1 (25%) | 4 — plataforma completa, sem MCP apply | 4 — pipeline L1–L7 ponta a ponta, infra fraca | 3 — CREI+MCP, sem listener/envy | 1 — não executa | 2 — simula o fluxo localmente; nada real (sem listener/CH/crew/MCP) |
| C2 Detecção (20%) | **5** — 5 detectores testados | 2 — 1 detector (robusto: AQE/zstd/rolling) | 3 — skew+spill com runbooks | 1 — não comprovado | 2 — skew (mesma base v4) |
| C3 Confiabilidade (15%) | 3 — thresholds com guards, sem baseline | 2 — sem validator nem baseline | **4** — EvidenceValidator + baseline | 1 | 3 — validação de evidência/stage, sem baseline |
| C4 Loop no IDE (15%) | 2 — MCP server sem apply | **5** — `apply_fix` único que fecha L6 | 2 — 2 tools, sem apply | 1 | 1 — só CLI |
| C5 Engenharia (15%) | **5** — testes+fakes+uv+config YAML | 4 — testes+CI+oráculo+ADRs | 3 — testes parciais (3 falhas) | 0 | **5** — 44 testes verdes, planos/specs disciplinados |
| C6 Custo/latência (10%) | 4 — detectores determinísticos | 2 — LLM obrigatório | **5** — T1 heurístico ~136ms | 2 — teórico | 5 — 100% determinístico |
| **Total ponderado** | **3.90** | **3.20** | **3.25** | **0.95** | **2.75** |

**Leitura:** o spike vence como **base**, mas nenhuma candidata satisfaz L1–L7 sozinha — o campeão real é a composição (§6). Nota: minha própria branch (cowork) fica em 3º; o viés declarado no topo não salvou a nota. A codex confirma o diagnóstico da tabela do time: segura e disciplinada, mas "ainda não é plataforma real" — sua melhor parte é o **contrato de telemetria `job_id`**, que deve virar a interface padrão entre listener → ClickHouse na composição.

---

## 6. Solução única proposta (composição validada)

```
BASE:        spike/apex-v0.1 (plataforma + 5 detectores + diagnostics.yaml + Go loader)
+ DO COWORK: apply_fix MCP (L6) · geradores/oráculo/CI do Mundo A como test harness · ADRs
+ DO KIMI:   EvidenceValidator + no_skew_baseline + runbooks — da versão PYTHON local
             (a reescrita Go só entra se/quando compilar e passar os mesmos gates)
+ DO CODEX:  contrato de telemetria job_id (apex/commander/telemetry.py) como interface
             padrão listener → ClickHouse + disciplina de testes (44 verdes) como referência
+ FUTURO:    kimi-Go entra pelo mesmo funil de gates, sem exceção
```

DataFlint permanece como **régua**: ~14 detectores, UI madura, alertas. Nossa vantagem defensável: on-premise, extensível, e L6 (aplicar o fix no IDE) — que o SaaS não faz.

**Matriz DataFlint completa** (capability por capability): `docs/competitive/dataflint-vs-apex-matrix.md` + `docs/avaliacao/MATRIX_COMPARATIVA.md`. Estudo de arquitetura e pain points da comunidade: `docs/competitive/dataflint-apex-study.html`. (Snapshot de 07/07 — reverificar o produto antes de decisões de roadmap.)

---

## 7. Gates de validação — implementar nesta ordem

Cada gate tem critério binário. Componente que falha não avança; falha registrada como issue no mesmo dia (CREW standard).

| Gate | O que valida | Critério de verde | Status hoje |
|------|--------------|-------------------|-------------|
| **G0** Reprodutibilidade | Build+testes de cada candidata num ambiente limpo | `pytest`/`go build` verdes documentados | spike ✅ · cowork ✅ · **codex ✅ (44 testes)** · kimi-Py 🟡 (1 falha real) · kimi-Go ❌ |
| **G1** Baseline negativo | Zero falso positivo em job saudável | `no_skew_baseline.yaml` → nenhum finding severity≥medium | ✅ **verde 09/07** — portado do kimi-Py, adaptado ao contrato v4; watcher com threshold de produção (10x): baseline 1.0x limpo + teste de falso positivo forçado passa; 25 testes verdes; fecha P2-10 |
| **G2** Detecção sintética | Cada detector pega seu cenário | gate de cenário verde por detector (hoje: só skew 27.9x ✅) | 🟡 1/5 |
| **G3** Dado real | Sintético ≈ real no plat-v0 | oráculo dentro da tolerância + run multi-core 8 tasks | 🟡 oráculo ok em 1-core; multi-core nunca rodou |
| **G4** Latência | Diagnóstico contínuo sem LLM obrigatório | T1 determinístico < 1s; LLM só quando confidence < threshold | ❌ cowork chama LLM sempre |
| **G5** Loop no IDE | MCP end-to-end no Cursor/Claude Code | `get_findings` → `apply_fix` com backup + diff revisável | 🟡 validado ad-hoc 06/07; falta roteiro reproduzível |
| **G6** CI contínuo | Nada entra sem gate | scenario-gate + oracle-weekly verdes no PR (fix de 08/07: `0ddb550`) | 🟡 corrigido; falta secrets `MINIO_*` + 1 run |

**Sequência de implementação:** G0(kimi-Py: corrigir a falha de spill) → G1 → G2(portar detectores spike, ISSUE-A01) → G4(T1 antes do LLM, ISSUE-A03) → G3 → G5(A05) → G6.

---

## 8. Decisões que este documento pede ao Luan

1. Aprovar (ou repesar) os critérios C1–C6.
2. Bater o martelo: **spike como base do merge** + composição do §6.
3. Secrets `MINIO_*` no repo para o G6 fechar.
4. A branch codex (`gustocezar/feature/codex-desacoplamento-geradores`) está só no repo pessoal — decidir se entra na revisão do time (push para `luanmorenommaciel/apex`).

---

*Método: cada LLM gera a melhor solução dela; uma LLM compara com evidência executável, valida gate por gate e compõe a solução única, testável e segura. Sem gate verde, não entra.*
