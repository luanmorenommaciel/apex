# Apex — Roadmap v4

**Crew A · Captain: Augusto · Projeto: Apex — diagnóstico agêntico de performance Spark**  
_Documento vivo — atualizar a cada fix fechado. Última revisão: 08 jun 2026_

---

## 1. Estado atual

### O que está funcionando — v4 branch (`gustocezar/feature/desacoplamento-geradores`)

> Branch analisada em 08 jun 2026. Issue de validação: #29.

| Componente | Status | Evidência |
|---|---|---|
| `apexlib.py` — parse centralizado com streaming | ✅ verde | `iter_events` + zstd streaming |
| Rolling logs — lê diretório com sort numérico | ✅ verde | suporte a `events_1`, `events_2`... |
| Stage-aware skew — seleção por join op + `executionId` | ✅ verde | não mais max-sum sem hint |
| AQE-aware — lê plano FINAL pós-`AdaptiveExecutionUpdate` | ✅ verde | associação por `executionId` |
| Auto-zstd — stream sem materializar arquivo completo | ✅ verde | sem OOM em logs grandes |
| Sentinela / Provenance — `compute_scenario_hash` | ✅ verde | cadeia de custódia code ↔ log |
| `skew_watcher.py` — detecta skew e emite Finding | ✅ verde | GATE VERDE `27.9x` sintético |
| Oracle — ratio real vs sintético dentro da tolerância | ✅ verde | `27.9x` sintético vs `29.5x` real |
| Testes — suite completa com streaming, rolling, executionId | ✅ verde | `s.................... [100%]` |

### O que NÃO está validado ainda

- **Distribuição real de 8 tasks** — worker multi-core nunca rodou. Oracle validado com sintético calculado, não com run multi-core.
- **P1-7 chave dinâmica** — `root_cause` ainda hardcoda `customer_id = 7`. Vai expor ao criar o segundo cenário.
- **Cenário único** — `no_skew_baseline.yaml` ainda pendente. Loop multi-cenário nunca divergiu.
- **Confiança por evidência** — fórmula `ratio/(ratio+3)` ainda sem base defensável.
- **Oracle CI semanal** — `oracle-weekly.yml` referenciado como próximo passo, não commitado ainda.

### Arquitetura atual (4 tiers)

```
Tier 1 · Watchers      → determinístico, sem LLM (skew_watcher.py)
Tier 2 · Classifier    → LLM classifica o Finding do Watcher
Tier 3 · Coordinator   → Sonnet orquestra o diagnóstico
Tier 4 · Judge         → Opus quando confiança < 0.6
```

Somente o Tier 1 está implementado. Tiers 2–4 são próxima fase.

---

## 2. Pontos de falha abertos

> Verificados diretamente no código em 07 jun 2026.  
> Critérios de done são objetivos — não conta "testes passando no caminho feliz".

---

### P0 — Quebra em produção

> ✅ **Todos os P0s resolvidos na v4** (`gustocezar/feature/desacoplamento-geradores`, 08 jun 2026).

#### P0-1 · OOM no decompress — ✅ RESOLVIDO
- **Fix aplicado:** `iter_events` com streaming. `zstandard.stream_reader` quando disponível — sem materializar o arquivo completo na memória.
- **Evidência:** teste de streaming zstd passa na suite v4.

#### P0-2 · Stage errado em jobs com múltiplos shuffles — ✅ RESOLVIDO
- **Fix aplicado:** seleção de stage pelo nome do operador de join (`hot_stage` do contrato) + `executionId`. `max(sum)` só como fallback.
- **Evidência:** teste com 2 stages de shuffle — watcher identifica o stage correto.

#### P0-3 · Só lê 1 arquivo de log — ✅ RESOLVIDO
- **Fix aplicado:** `read_events` aceita diretório; sort numérico de `events_1`, `events_2`... etc.
- **Evidência:** teste com diretório de rolling logs passa na suite v4.

---

### P1 — Incorreção lógica

#### P1-6 · `join_operator` sem filtro de `executionId` — ✅ RESOLVIDO
- **Fix aplicado:** `join_operator` associa plano final ao `executionId` correto. Jobs com múltiplas queries SQL retornam o plano da execução certa.
- **Evidência:** teste com 2 execuções SQL distintas passa na suite v4.

#### P1-7 · `root_cause` hardcoda "customer_id"
- **Arquivo:** `watchers/skew_watcher.py:59`
- **Bug:** `"data skew na chave de join customer_id"` é literal. O acceptance do cenário atual exige `"customer_id"` — isso **mascara o bug**. Quando o segundo cenário usar outra chave, o root_cause vai estar errado e o acceptance vai falhar parecendo bug novo.
- **Fix:** ler a chave de join do contrato e interpolar na string.
- **Critério de done:**
  - [ ] `root_cause` usa valor lido do `scenario.yaml` (não literal)
  - [ ] Segundo cenário com chave diferente produz root_cause correto
  - [ ] P2-10 (segundo cenário) só pode ser aberto depois deste fix

---

### P2 — Qualidade e progressão

> Resolver antes de declarar `status: validated`. Podem ser feitos em paralelo com P1s.

#### P2-8 · Fórmula de confiança arbitrária
- **Arquivo:** `watchers/skew_watcher.py:51`
- **Bug:** `min(0.99, ratio / (ratio + 3))` — os casos extremos estão OK (collapsed=0.95, inf=0.99), mas a fórmula para ratios normais não tem base defensável.
- **Fix:** definir thresholds de confiança no contrato e derivar da evidência.
- **Critério de done:**
  - [ ] `scenario.yaml` tem bloco `confidence_thresholds`
  - [ ] Watcher calcula confiança referenciando o contrato
  - [ ] Alterar o contrato muda o output proporcionalmente

#### P2-9 · Sem teste de manifesto (`job.meta.json`) — ✅ RESOLVIDO
- **Fix aplicado:** `compute_scenario_hash` centralizado + `validate_provenance`. Manifesto inclui `scenario_hash`, `generator_version`, `generated_at`, `job_file`, linha do anti-pattern e classe.
- **Evidência:** teste de hash determinístico passa — mesmo hash no manifesto do code_generator e no primeiro evento do plan_generator.

#### P2-10 · Só 1 cenário — loop multi-cenário nunca exercitado
- **Arquivo:** `scenarios/` — apenas `skew_on_join_30x.yaml`
- **Bug:** `for s in scenarios/*.yaml` nunca diverge com 1 arquivo. Erros de generalização ficam invisíveis.
- **Dependência:** P1-7 deve estar resolvido antes — senão o segundo cenário vai falhar por `customer_id` hardcoded.
- **Fix:** adicionar segundo cenário (candidato: Memory/Cost — Pod A2).
- **Critério de done:**
  - [ ] P1-7 fechado
  - [ ] `scenarios/` tem 2+ arquivos
  - [ ] CI roda gate para todos; ambos passam

#### P2-11 · `status: prototype` sem critério de progressão
- **Arquivo:** `scenarios/skew_on_join_30x.yaml:4`
- **Bug:** `status: prototype` mas não existe definição objetiva de quando vira `validated`.
- **Fix:** documentar os critérios (este doc — seção 4). Quando condições forem atendidas, atualizar o campo + linkar evidência.
- **Critério de done:**
  - [ ] Critérios de `validated` documentados (ver seção 4 abaixo)
  - [ ] Após P0s + P1s + oracle multi-core: campo atualizado para `validated` com commit linkado

#### P2-12 · Sem CI agendado para o oráculo
- **Arquivo:** `.github/workflows/scenario-gate.yml` — só `on: pull_request`
- **Bug:** o oráculo valida que o sintético continua fiel ao real — mas só roda manualmente. Drift silencioso não é detectado.
- **Fix:** workflow separado `oracle-weekly.yml` com `schedule: cron: '0 6 * * 1'`.
- **Critério de done:**
  - [ ] `oracle-weekly.yml` existe e roda toda segunda 6h
  - [ ] Falha abre issue automaticamente (`on_divergence: fail_and_open_issue` já no contrato)

---

## 3. Sequência de execução

```
[CONCLUÍDO — v4 branch]
  ✅ P0-1 · stream zstd (sem OOM)
  ✅ P0-2 · stage por join op + executionId
  ✅ P0-3 · rolling logs (diretório)
  ✅ P1-6 · filtro executionId em join_operator
  ✅ P2-9 · scenario_hash + provenance
  ✅ Oracle ratio: 15392x → 27.9x (real 29.5x)

[AGORA — pós-reunião Crew A 08 jun 2026]
  Validação coletiva da branch v4 (issue #29)
         ↓
  P1-7 · chave de join dinâmica (bloqueia segundo cenário)
         ↓
  Escalar worker para 2+ cores no compose
  → re-rodar job → capturar log com 8 tasks
  → rodar oracle → fechar ratio real multi-core
         ↓
  P2-10 · segundo cenário no_skew_baseline.yaml (Pod A2)
         ↓
  P2-8  · confiança por contrato ────────────────────────────────┐
  P2-12 · oracle-weekly.yml ─────────────────────────────────────┘
         ↓
  P2-11 · declarar status: validated (com evidência linkada)
```

**Dependências críticas:**
- P1-7 **bloqueia** P2-10 — `no_skew_baseline.yaml` vai expor o hardcode imediatamente
- Escalar worker **bloqueia** ratio real do oráculo — sem multi-core, o AQE colapsa em 1 task
- P0s e P1-6 já resolvidos na v4 — não bloqueiam mais nada

---

## 4. Milestone: `status: validated`

Para mudar `skew_on_join_30x.yaml` de `prototype` para `validated`, todas as condições abaixo devem ser atendidas e linkadas com commit ou run de evidência:

- [x] P0-1, P0-2, P0-3 fechados — com testes cobrindo os casos de quebra ✅ v4
- [ ] Worker 2+ cores no compose, job rodado, log capturado com 8+ tasks no reduce stage
- [ ] Oracle rodando com distribuição multi-task; ratio dentro da tolerância de 30%
- [x] P1-6 fechado ✅ v4
- [ ] P1-7 fechado (chave dinâmica)
- [ ] Segundo cenário no CI (P2-10)
- [ ] Oracle CI agendado rodando sem falha por 2 semanas (P2-12)
- [ ] Issues GitHub atualizadas com evidência de cada fix (#17, #19, #20, #21)

**Não conta como validated:**
- Testes passando apenas no caminho feliz
- GATE VERDE apenas em 1-core colapsado
- Issues GitHub desatualizadas (CREW_A_OPERATING_STANDARD: "Done local ≠ Done")

---

## 5. Rastreabilidade

| Issue GitHub | Componente | Status |
|---|---|---|
| #17 — Watcher Pipeline | `skew_watcher.py`, `apexlib.py` | P0-2 ✅, P1-6 ✅, P1-7 🟠 aberto |
| #19 — plat-v0 Bootstrap | Event log capture, MinIO | P0-1 ✅, P0-3 ✅ |
| #20 — Recommendation Engine | Finding + recomendações | P2-8 🟡 aberto |
| #21 — CI Integration | `scenario-gate.yml` | P2-9 ✅, P2-10 🟡 aberto, P2-12 🟡 aberto |
| #29 — Validar v4 com Crew A | slice `skew_on_join_30x` | 🔵 aberto para validação coletiva |
| #28 — BLOCKER repo access | — | Confirmar com Luan na sync |
| ADR-004 | scenario.yaml contract | Pronto para abrir (ver `06_apex_repo_ready/docs/adr/`) |

**Artefatos prontos para postar no GitHub:**  
`03_documentacao/apex_github_ready_artifacts.md` — Captain's Report, comentários #17/#19/#20/#21/#28, ADR-004 completo.

---

## 6. Log de progresso

> Atualizar aqui a cada fix fechado. Formato: `DATA · COMMIT · o que fechou · issue linkada`

| Data | Commit/Branch | Fix | Issue |
|---|---|---|---|
| 06 jun 2026 | `357efad` | v3: apexlib, stage-aware, AQE-aware, auto-zstd, sentinela — 25 testes verdes, GATE VERDE no plat-v0 | #17 #19 #20 #21 |
| 08 jun 2026 | `feature/desacoplamento-geradores` | v4: P0-1 OOM streaming, P0-2 stage correto, P0-3 rolling logs, P1-6 executionId, P2-9 scenario_hash+provenance — oracle 15392x→27.9x (real 29.5x) | #29 |

---

_Para sync com Commander: usar Captain's Report (4 blocos) do `CREW_A_OPERATING_STANDARD.md`._  
_Para apresentação visual do fluxo: `04_apresentacoes/apex_briefing_v3_06-06.html`._
