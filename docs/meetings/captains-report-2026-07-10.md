# Captain's Report — 2026-07-10

**Crew A · Captain: Augusto · Para: Commander Luan**
**Branch:** `gustocezar/feature/cowork-desacoplamento-geradores` · HEAD `28b6464` (origin + team)
**Sessões cobertas:** 09–10 jul (continuação do report de 08/07)

---

## ✅ Avançou

**Gates G0–G5 fechados — todos com evidência executada, três com dado real no plat-v0:**

- **G1** Baseline negativo: `no_skew_baseline.yaml` — zero falso positivo com threshold de produção.
- **G2** Cobertura: 4 detectores do spike portados (gc, shuffle/spill, oom, plans) + 4 cenários sintéticos; de 1 para **5 detectores com gate verde**; dispatch por classe no CI.
- **G3** Dado real multi-core: worker 8 cores, run `app-20260710021939-0000` — **ratio real 29.4x vs sintético 27.9x**, oráculo na tolerância. Era o último claim não-validado do Mundo A (pendente desde junho).
- **G4** T1 determinístico antes do LLM: skew real detectado em **333ms, zero tokens** (`t1_triage.py`); Crew.ai virou fallback (confidence < 0.6). Comparativo na mesma máquina: o caminho LLM cego gastou ~2.8k tokens para dizer "other 0.35".
- **G5** Ciclo completo "aplica nossa sugestão": finding real → `apply_fix` gerou AQE+salting+broadcast → **revisão do diff pegou 2 bugs do código gerado** (valida o design backup+diff) → job corrigido re-submetido: **shuffle eliminado (1.16MB→0), T1 = 0 findings**. MCP registrado no Claude Code.

**Composição V1 materializada (ADR-006, proposto):** `apex/evidence_validator.py` (7 regras do kimi-Py — evidência inválida bloqueia diagnóstico), `apex/telemetry.py` (envelope `job_id` do codex), detectores do spike, `apply_fix` do cowork. **52 testes verdes.** Contrato de schema unificado (`docs/specs/`) + roteiro de demo (`docs/playbooks/`).

**2 bugs de infra reais encontrados e corrigidos:**
1. ClickHouse em bind mount NTFS/Windows: **todo insert MergeTree falhava** ("rename: Permission denied") — explica por que o CH do plat-v0 nunca funcionou no Windows. Fix: named volume (`c9f6edf` no plat-v0).
2. Skew de registros ≠ skew de duração (29.4x vs 1.01x em dataset pequeno) — detecção cegava por olhar só duração. Fix nas 4 camadas: schema, ingest, T1, tools do Crew.

## 🔴 Bloqueado

- **G6 (oráculo semanal):** runner do GitHub não alcança o MinIO local do plat-v0. Secrets sozinhos não resolvem — precisa de decisão de infra (ver abaixo).
- **kimi-Go:** continua sem compilar (sem `go.sum`); fica no funil de gates.

## 🟡 Precisa do Commander

1. **Martelo no ADR-006** (composição V1) — a decisão que destrava o merge; sem ela as 4 branches seguem divergindo. Critérios/pesos do scorecard são ajustáveis.
2. **G6 — escolher:** (a) self-hosted runner, (b) MinIO acessível ao time, ou (c) oráculo agendado local.
3. **Aprovar abertura das issues A01–A08** (`docs/avaliacao/ISSUES_AVALIACAO.md`) e a migração A02 (loader Go → schema v1).

## ⚪ Honestidade

- A demo ao vivo no IDE (Claude Code chamando `get_findings`/`apply_fix`) está registrada mas **ainda não foi executada de ponta a ponta no IDE** — o ciclo foi validado via CLI com a mesma lógica da tool.
- O fix gerado pelo `apply_fix` precisou de **revisão humana** (2 bugs: import fora de ordem; coluna duplicada) — é feature do design, mas o pitch deve dizer "fix com revisão", não "fix automágico".
- Comentários de progresso nas issues #17/#19/#20/#21 seguem pendentes desde junho — este report e o anterior (08/07) são o material para regularizar.
- Durante a sessão, commits com árvore corrompida foram criados e descartados antes do push (tooling local) — a história publicada está íntegra; verificado com `git ls-tree`.
- Avaliação comparativa e composição foram produzidas pela mesma LLM da branch cowork — viés declarado nos docs; a base recomendada é a branch do Aguimar, não a nossa.
