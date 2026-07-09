# Captain's Report — 2026-07-08

**Crew A · Captain: Augusto · Para: Commander Luan**
**Branch:** `gustocezar/feature/cowork-desacoplamento-geradores` · HEAD `0ddb550`

---

## ✅ Avançou

- **Reavaliação completa da branch** (código, docs, CI, testes): suite Mundo A verde — 20 passed, 1 skipped (skip = `zstandard` ausente no ambiente local, não é bug). P0-1/2/3/4, P1-5/6 e P2-9 confirmados resolvidos no código.
- **2 bugs de CI encontrados e corrigidos** (commit `0ddb550`):
  1. `scenario-gate.yml` quebrava com os `listener_*.yaml` (Mundo B, sem `code_generator`) — KeyError no gerador, gate vermelho em qualquer PR. Fix: filtro world B no loop. Validado localmente (GATE VERDE 27.9x).
  2. `oracle-weekly.yml` referenciava `scripts/fetch_real_log.py` inexistente — oráculo semanal falhava silenciosamente. Script criado + `python` → `python3` + filtro world B.
- **VALIDACAO.md atualizado** com seção 7: correções, proposta de merge e caminho crítico.

## 🔴 Bloqueado

- **Oráculo semanal (P2-12):** workflow corrigido, mas precisa de secrets `MINIO_*` no repo + um `workflow_dispatch` manual para validar de ponta a ponta.
- **Validação multi-core (8 tasks reais):** worker 2+ cores nunca rodou no plat-v0 — ratio real do oráculo segue não confirmado.
- **P1-7 / P2-10:** `root_cause` ainda hardcoda `customer_id`; sem `no_skew_baseline.yaml` não há proteção contra falso positivo (o kimi já tem — portar).

## 🟡 Precisa do Commander

1. **Decisão de merge (a mais importante):** a avaliação comparativa (`docs/avaliacao/`) conclui que nenhuma branch resolve sozinha. Proposta: **spike/apex-v0.1 como base** + T1 heurístico/EvidenceValidator do kimi + `apply_fix` do cowork + Go loader do spike. Precisamos do martelo batido para parar a divergência das 3 branches.
2. **Aprovar abertura das 8 issues** prontas em `docs/avaliacao/ISSUES_AVALIACAO.md` (A01–A08) no `luanmorenommaciel/apex`.
3. **Secrets `MINIO_*`** no repo para o oráculo semanal rodar.

## ⚪ Honestidade

- A avaliação comparativa foi produzida pela mesma LLM (Claude/Cowork) que implementou a branch cowork — viés declarado no próprio doc; a recomendação de base é a branch do Aguimar, não a nossa.
- "40 testes" citados no CLAUDE.md incluem os do plat-v0; a suite local desta branch tem 21 (20 verdes + 1 skip de dependência).
- Os comentários de progresso nas issues #17/#19/#20/#21 e a confirmação da #28 estão pendentes desde junho — este report é o passo para regularizar ("done local ≠ done").
- Drift de docs conhecido: CLAUDE.md cita ADR-001–004 (existem só 004 e 005) e baseline `bc747c1` (defasado ~20 commits).
