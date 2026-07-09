# Apex — Backlog

_Atualizar a cada fix fechado. Ver `CHANGELOG.md` para histórico._

> **v4 branch:** `gustocezar/feature/desacoplamento-geradores` — analisada em 08 jun 2026. P0-1, P0-2, P0-3, P1-6 resolvidos. Issue #29 aberta para validação da Crew A.

---

## 🔴 P0 — Crítico (quebra em produção)

| ID | Item | Arquivo | Issue | Status |
|---|---|---|---|---|
| P0-1 | OOM no decompress — `f.read()` carrega arquivo inteiro em RAM | `apex/apexlib.py` | #19 | ✅ resolvido na v4 — `iter_events` streaming + zstd sem materializar arquivo |
| P0-2 | Stage errado em jobs multi-join — `max(sum)` sem hint do contrato | `apex/apexlib.py` | #17 | ✅ resolvido na v4 — seleção por nome do operador de join + `executionId` |
| P0-3 | Só lê 1 arquivo de log — sem suporte a rolling logs | `apex/apexlib.py` | #19 | ✅ resolvido na v4 — aceita diretório, sort numérico de rolling logs |

---

## 🟠 P1 — Incorreção lógica

| ID | Item | Arquivo | Issue | Status |
|---|---|---|---|---|
| P1-6 | `join_operator` sem filtro de `executionId` — pega plano de outra query | `apex/apexlib.py` | #17 | ✅ resolvido na v4 — associação por `executionId` explícita |
| P1-7 | `root_cause` hardcoda "customer_id" — mascara bug no segundo cenário | `watchers/skew_watcher.py` | #17 | 🟠 aberto — v4 inclui `= 7` + operador, mas ainda hardcoded. Vai expor ao criar `no_skew_baseline.yaml` |

---

## 🟡 P2 — Qualidade (resolver antes de `status: validated`)

| ID | Item | Arquivo | Issue | Status |
|---|---|---|---|---|
| P2-8 | Confiança arbitrária `ratio/(ratio+3)` sem base defensável | `watchers/skew_watcher.py:51` | #20 | 🟡 aberto |
| P2-9 | Sem teste de manifesto `job.meta.json` | `tests/test_slice.py` | #21 | ✅ resolvido na v4 — `compute_scenario_hash` + provenance validation adicionados |
| P2-10 | Só 1 cenário — loop multi-cenário nunca exercitado | `scenarios/` | #21 | ✅ resolvido 09/07 — `no_skew_baseline.yaml` (G1) + loop CI exercitado com 2 cenários world A |
| P2-11 | `status: prototype` sem critério de progressão | `scenarios/skew_on_join_30x.yaml:4` | — | 🟡 aberto |
| P2-12 | Sem CI agendado para oráculo — drift silencioso | `.github/workflows/` | #21 | 🟠 quase — `oracle-weekly.yml` corrigido em 08/07 (`fetch_real_log.py` criado, filtro world B). Falta: secrets `MINIO_*` + 1 run manual |

---

## ⚙️ Infraestrutura (próxima fase)

| Item | Issue | Status |
|---|---|---|
| Escalar worker para 2+ cores no plat-v0 | #19 | 🔴 bloqueado (travado pelo P0s) |
| Re-rodar job com distribuição real de 8 tasks | #19 | ⏳ aguardando worker 2+ cores |
| Fechar ratio real do oráculo em multi-core | #19 | ⏳ aguardando run real |
| Memory/Cost Watcher — Pod A2 | #17 | ⏳ aguardando P1-7 |
| OTel Collector Stage 02 (Go) | #18 | 🔵 outra lane (Gabriel/Guilherme) |

---

## 📋 GitHub — Ações pendentes

| Ação | Artefato pronto | Status |
|---|---|---|
| Comentar progresso em #17 | `docs/adr/` + commit 357efad | ⏳ pós-validação com Luan |
| Comentar progresso em #19 | commit 357efad | ⏳ pós-validação com Luan |
| Comentar progresso em #20 | commit 357efad | ⏳ pós-validação com Luan |
| Comentar progresso em #21 | commit 357efad | ⏳ pós-validação com Luan |
| Atualizar/fechar #28 (repo access) | — | ⏳ confirmar com Luan |
| Abrir ADR-004 | `docs/adr/ADR-004-scenario-contract.md` | ⏳ pós-validação com Luan |
| Atualizar phase labels #17 #20 #21 para `phase:build` | — | ⏳ pós-validação |

---

## 🔬 LLM Evals (Tiers 2–4)

Comparações em andamento — resultados em `docs/llm-evals/`.

| Modelo | Tier candidato | Status |
|---|---|---|
| Claude Sonnet | Tier 3 Coordinator | 🔵 testando |
| Claude Opus | Tier 4 Judge | 🔵 testando |
| Gemini | Tier 2 Classifier | 🔵 testando |
| DeepSeek | Tier 2 Classifier | 🔵 testando |
| Kimi | Tier 2 Classifier | 🔵 testando |
| ChatGPT / Codex | Tier 2 / comparativo | 🔵 testando |

---

## ✅ Concluído

| Item | Versão | Commit/Branch | Data |
|---|---|---|---|
| apexlib centralizado (sem duplicação) | v3 | 357efad | 06 jun 2026 |
| Stage-aware skew (isola reduce) | v3 | 357efad | 06 jun 2026 |
| AQE-aware (plano final) | v3 | 357efad | 06 jun 2026 |
| Auto-zstd (magic bytes) | v3 | 357efad | 06 jun 2026 |
| Sentinela de linha (CI guard) | v3 | 357efad | 06 jun 2026 |
| 25 testes verdes + GATE VERDE no Spark real | v3 | 357efad | 06 jun 2026 |
| P0-1 OOM — `iter_events` streaming + zstd sem materializar | v4 | feature/desacoplamento-geradores | 08 jun 2026 |
| P0-2 Stage errado — seleção por join op + executionId | v4 | feature/desacoplamento-geradores | 08 jun 2026 |
| P0-3 Rolling logs — aceita diretório + sort numérico | v4 | feature/desacoplamento-geradores | 08 jun 2026 |
| P1-6 executionId filter em `join_operator` | v4 | feature/desacoplamento-geradores | 08 jun 2026 |
| P2-9 Manifesto — `comput