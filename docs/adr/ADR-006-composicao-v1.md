# ADR-006 — Composição do Apex V1: a melhor peça validada de cada solução

**Status:** proposto (aguarda decisão do Commander)
**Data:** 2026-07-10
**Decisores:** Luan (Commander) · Crew A
**Contexto completo:** `docs/architecture/llm-solution-validation-framework-2026-07-09.md`

## Contexto

Quatro soluções paralelas foram construídas para o V1 (spike/Aguimar, cowork/Claude,
kimi, codex), cada uma com uma peça forte e nenhuma satisfazendo sozinha as premissas
L1–L7 do Commander. O framework de validação pontuou as quatro com evidência
executada (testes rodados, builds verificados, runs reais no plat-v0) e os gates
G0–G5 foram fechados entre 09–10/07, incluindo o ciclo completo com dado real:
skew 29.2x detectado em 333ms sem LLM → `apply_fix` → job re-submetido limpo
(0 findings, shuffle eliminado).

## Decisão

O V1 do Apex é a COMPOSIÇÃO das melhores peças validadas, sobre uma base única:

| Peça | Origem | Evidência | Estado na branch |
|---|---|---|---|
| Plataforma (Docker, loader Go, `diagnostics.yaml`) | **spike** | 22 testes verdes; maior score (3.90) | detectores portados (`apex/detectors.py` + `apex/diagnostics.yaml`, G2); loader Go pendente de migração ao schema v1 (A02) |
| Detecção determinística T1 antes do LLM | spike+kimi | skew real em 333ms, zero tokens (G4) | ✅ `v1-skeleton/analysis/t1_triage.py` |
| `apply_fix` via MCP no IDE (L6) | **cowork** | ciclo real: fix aplicado, diff pegou 2 bugs, job limpo (G5) | ✅ `v1-skeleton/mcp/server.py` + `scripts/apply_fix_cli.py` |
| EvidenceValidator (7 regras) + baseline negativo | **kimi-Py** | 10 testes; bloqueia diagnóstico de evidência colapsada; baseline 1.0x limpo (G1) | ✅ `apex/evidence_validator.py` (puro, sobre o contrato) + `scenarios/no_skew_baseline.yaml` |
| Envelope de telemetria `job_id` | **codex** | 44 testes na origem; regra única de identidade | ✅ `apex/telemetry.py` (`apex.telemetry.v1`) |
| Test harness (geradores, oráculo, gates de cenário, CI) | cowork | 6 cenários verdes; oráculo 27.9x vs real 29.4x (G3) | ✅ `generators/`, `oracle/`, `scenarios/`, workflows |
| Schema canônico ClickHouse | contrato | dedup por chave natural (lição spike) | ✅ `docs/specs/apex_telemetry_v1.sql` |

Princípio operante: **detector lê o contrato, não a fonte** — as mesmas regras rodam
sobre event log (Mundo A) e ClickHouse (Mundo B). E **claim sem gate verde não entra**.

## Consequências

Positivas: uma base única encerra a divergência das 4 branches; cada peça entra com
evidência, não reputação; o diferencial vs DataFlint (fechar o loop no IDE) fica no
centro do produto.

Negativas/custos: migração do loader Go do spike para o schema v1 (A02); os times
das branches kimi/codex veem partes do seu trabalho arquivadas (mitigação: as peças
fortes DELAS estão no core, com crédito); kimi-Go fica fora até compilar e passar
os mesmos gates.

## Pendências que esta decisão destrava

A02 (loader Go → schema v1) · portar runbooks JSON do kimi p/ `diagnostics.yaml` ·
P1-7 e P2-8 · CI Mundo B · Sprint 3: JAR Scala do listener (ADR-005) · camada
agêntica (memória/RAG/contratos — "onde vai o tempo", Luan 30/06).

## Alternativas rejeitadas

1. **Escolher 1 branch vencedora** — nenhuma satisfaz L1–L7 (scorecard §5).
2. **Manter branches paralelas** — custo de divergência já demonstrado (3 schemas).
3. **Reescrever do zero em Go (caminho kimi-Go)** — não compila; fica no funil de gates.
