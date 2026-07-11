# Protocolo Rodada 2 — Campeonato de LLMs com Base Comparável

> **Objetivo:** cada LLM (Claude, Kimi, Codex, Gemini, DeepSeek...) **parte da
> sua própria branch já existente e verificada** — ninguém recomeça do zero — e a
> ESTRUTURA no formato comum: mesmas fases, mesmos entregáveis de nome fixo,
> mesmos critérios de aceitação. **Livre no COMO dentro de cada bloco** (a
> arquitetura que a LLM já escolheu permanece dela). No fim, a comparação é
> célula a célula, com evidência executável, não opinião.
>
> Operador: Augusto (Captain) · Juiz final: Luan (Commander)

---

## 1. O pacote comum (entregar a TODAS as LLMs, idêntico)

| Arquivo | Papel |
|---|---|
| `docs/specs/apex-v1-spec-reproducivel.md` | O QUE construir: missão, premissas L1–L9, arquitetura, thresholds, lições |
| `docs/specs/apex_telemetry_v1.sql` + `telemetry-schema-contract-v1.md` | Contratos de dados (imutáveis — interoperabilidade) |
| `scenarios/*.yaml` (os 6 world A) | Casos de teste oficiais — NÃO alterar, só consumir |
| `scripts/g3_multicore_gate.py` + `docs/playbooks/g3-multicore-runbook.md` | Gate de dado real (juiz automático) |
| `docs/architecture/llm-solution-validation-framework-2026-07-09.md` §3+§7 | Critérios C1–C6 e gates G0–G6 |
| `docs/CREW_A_OPERATING_STANDARD.md` | Padrão de reporte ("done local ≠ done") |

**Ponto de partida de cada LLM:** a SUA branch já existente (kimi:
`gustocezar/feature/kimi-desacoplamento-geradores` + `apex-kimi-product-v0.1`
local; codex: `gustocezar/feature/codex-desacoplamento-geradores`; spike:
`spike/apex-v0.1`; cowork: `cowork-desacoplamento-geradores`).

**NÃO entregar a uma LLM:** as branches DAS OUTRAS nem as avaliações
comparativas. Cada uma evolui o próprio trabalho contra a spec — comparação
justa = mesma régua, não mesmo código.

## 2. Segregação — igual para todas

- **Branch:** continuar na branch existente da LLM (ou derivar `gustocezar/feature/<llm>-estruturado` a partir dela, se preferir preservar o estado atual).
- **Estrutura obrigatória de docs** (o conteúdo é livre; os NOMES não):

```
<branch>/
├── PLANO.md                     # F0 — como a LLM pretende atacar
├── evidence/                    # logs CRUS de cada gate (gN-<nome>.log)
├── docs/
│   ├── adr/ADR-XXX-*.md         # cada decisão de arquitetura
│   ├── meetings/captains-report-<data>.md   # 4 blocos CREW A por sessão
│   └── autoavaliacao.md         # F5 — scorecard C1–C6 preenchido pela própria LLM
└── (código: estrutura livre)
```

- **Commits:** `feat|fix|docs(<escopo>): ...` com o gate no corpo quando aplicável.
- **Evidência:** output cru de terminal em `evidence/` — sem edição. Print bonito
  em doc não conta; log cru conta.

## 3. As fases (F0–F5) — mesmos blocos, atuação livre dentro

| Fase | Objetivo | Entregável fixo | Aceitação |
|---|---|---|---|
| **F0 Diagnóstico** | LLM mapeia O PRÓPRIO estado atual contra a spec | `PLANO.md`: o que já tenho (com evidência) · gaps vs L1–L9 e gates · ordem de fechamento · o que vou REAPROVEITAR vs refazer | honesto e cobre L1–L9 |
| **F1 Fundação** | contratos implementados + build limpo | código + `evidence/g0-testes.log` | **G0**: testes verdes em ambiente limpo |
| **F2 Detecção** | detectores + baseline negativo | `evidence/g1-baseline.log`, `g2-cenarios.log` | **G1**: zero falso positivo · **G2**: 5 classes detectadas nos scenarios oficiais |
| **F3 Dado real** | rodar no plat-v0, custo controlado | `evidence/g3-real.log`, `g4-t1.log` | **G3**: gate script verde · **G4**: diagnóstico <1s sem LLM no caso comum |
| **F4 Loop IDE** | MCP + aplicar fix com backup/diff | `evidence/g5-ciclo.log` (detectar→fix→re-executar limpo) | **G5**: job corrigido re-executado sem findings |
| **F5 Fechamento** | autoavaliação honesta | `docs/autoavaliacao.md` + Captain's Report final | scorecard C1–C6 com evidência POR CÉLULA + bloco Honestidade não-vazio |
| **F6 Melhoria comparativa** | pós-julgamento: aprender das outras | `MELHORIAS.md`: o que adotar de cada engine, com issue `<LLM>-NNN` por adoção | baseado no relatório do JUIZ (scorecard verificado), NÃO no código das outras |

Regras entre fases: não pular fase (F(n) exige F(n-1) verde); travou >1 sessão em
uma fase → registrar blocker no Captain's Report e seguir parcial, nunca maquiar.

## 3.1 Catálogo de issues internas (obrigatório por branch)

Toda branch mantém `ISSUES.md` na raiz — o diário estruturado do trabalho entre
gates. **Cada passo relevante vira uma entrada**: decisão, bug, blocker, teste
criado, evidência produzida. Formato fixo (uma tabela, uma linha por issue):

```markdown
| ID | Fase/Gate | Tipo | Título | Evidência | Status |
|---|---|---|---|---|---|
| KIMI-001 | F1/G0 | decisão | Manter CREI em Python, adiar Go | docs/adr/ADR-101.md | fechada |
| KIMI-002 | F2/G1 | bug | baseline disparava spill com shuffle 2MB | evidence/g1-baseline.log | fechada |
| KIMI-003 | F3/G3 | blocker | plat-v0 sem worker multi-core | captains-report-... | aberta |
```

Regras: ID = `<LLM>-NNN` sequencial · tipo ∈ {decisão, bug, blocker, teste,
evidência, melhoria} · toda linha aponta para um arquivo verificável · blocker
aberto >1 sessão sobe para o Captain's Report. As issues já existentes do round 1
(A01–A08, P0–P2, issues #17–#30 do GitHub) são importadas com o ID original.

**Rastreabilidade**: com ISSUES.md + evidence/gN-*.log + ADRs, o juiz reconstrói
o caminho completo passo→teste→evidência→gate de qualquer claim, sem entrevistar
a LLM. É este catálogo que torna o julgamento auditável.

## 3.2 Passos padronizados de auto-comparação (toda engine; a cowork executa primeiro como referência)

**(a) `MELHORIAS.md` — comparação honesta e adoções.** Após cada julgamento (ou,
no caso da cowork, já no round 1), a engine compara-se com TODAS as outras e lista
o que as outras fazem melhor + o que vai adotar, cada adoção virando issue no
catálogo. Fonte permitida: o scorecard/relatório VERIFICADO do juiz e os docs
públicos de avaliação — nunca o código das concorrentes (preserva o isolamento).
Formato: tabela `origem | o que fazem melhor | adoção proposta | issue | status`.

**(b) Atualização ISOLADA dos docs de comparação (economia de tokens).** Quando a
engine evolui, ela atualiza os documentos comparativos APENAS com o próprio delta,
em bloco de adendo datado marcado `[self-reported]` — **sem reanalisar as outras
branches**. As colunas das outras permanecem congeladas no último snapshot
verificado. Regra dura: adendo self-reported NUNCA sobrescreve score verificado —
convive ao lado até o juiz re-verificar. (Padrão já aplicado: adendo 10/07 no
framework §5 e na MATRIX.)

## 3.3 Congelamento da régua (antes da largada — evita alvo móvel)

1. **Pacote comum taggeado:** `git tag round2-freeze` no commit que contém spec +
   contratos + cenários + este protocolo. Toda engine e o juiz referenciam a tag —
   mudança na régua no meio da rodada invalida a comparação.
2. **Pesos pré-registrados:** o Commander fixa (ou aceita) os pesos C1–C6 ANTES da
   largada, por escrito no ADR — ajustar peso depois de ver resultado é a forma
   mais fácil de viciar campeonato.
3. **Orçamento declarado:** nº de sessões/tempo por engine registrado no PLANO.md —
   sem isso a comparação mede orçamento, não capacidade.

## 4. Prompt de largada (colar na LLM, ajustando `<LLM>`)

```
Você é a engine <LLM>. Você JÁ construiu uma solução para o Apex na branch
<branch-da-llm> — este trabalho é válido e é o seu ponto de partida. Anexo: o
pacote comum (spec reproduzível, contratos, scenarios oficiais, critérios).
Sua missão agora é ESTRUTURAR e completar a sua solução no formato comum:

0. Antes de tudo, crie a estrutura padrão na raiz da sua branch (idempotente):
   mkdir -p evidence docs/adr docs/meetings
   touch PLANO.md ISSUES.md docs/autoavaliacao.md MELHORIAS.md
   Em ISSUES.md, crie o cabeçalho da tabela do catálogo (§3.1) e importe suas
   issues já existentes com os IDs originais.
1. F0 primeiro: leia a spec e escreva PLANO.md mapeando com honestidade o seu
   estado atual — o que já cumpre cada premissa L1–L9 e cada gate G0–G5 (com
   evidência), quais são os gaps, em que ordem vai fechá-los, e o que do seu
   código será reaproveitado vs refeito.
2. Siga as fases F1–F5 fechando os gaps, sem pular fase. O que já passa num
   gate, apenas comprove: rode e salve o log cru em evidence/gN-*.log.
3. Os contratos (schema SQL apex.*, envelope job_id, scenario.yaml) são
   IMUTÁVEIS — adapte a SUA solução a eles (esta é a principal estruturação).
   O resto da sua arquitetura permanece escolha sua; decisões novas viram ADR.
4. Critério de verdade: gates G0–G5. Claim sem log cru em evidence/ não existe.
5. Ao final: docs/autoavaliacao.md com scorecard C1–C6 (0–5, evidência por
   célula) + Captain's Report com bloco de Honestidade real (o que não funciona,
   o que não deu tempo, onde tem dúvida).
"Done local ≠ done". Nunca maquiar resultado — parcial documentado vale mais.
```

## 5. Julgamento (depois que todas entregarem)

1. Augusto roda os gates de cada branch num ambiente limpo (mesma máquina,
   mesmo plat-v0) — a autoavaliação é conferida, não confiada.
2. Uma LLM que NÃO competiu (ou o Commander) preenche o scorecard cruzado —
   mesma regra de evidência executada do round 1.
3. Divergência autoavaliação vs verificação > 1 ponto em qualquer critério →
   registrada no bloco Honestidade da avaliação (mede a confiabilidade da engine,
   que também é um dado do campeonato).
4. Resultado alimenta o framework (§5) e a decisão de composição (ADR-006 rev.).

## 6. O que já existe e é reaproveitado (não recriar)

Spec ✅ · contratos ✅ · scenarios oficiais ✅ · gate G3 automático ✅ · critérios e
gates ✅ · padrão de report ✅ · **as branches de cada LLM (round 1)** ✅ · **este
protocolo** ✅. Falta por rodada: colar o prompt em cada LLM apontando para a
branch dela, operar as sessões e julgar. A cowork também passa pelo protocolo —
mesma régua para todas, incluindo a nossa.
