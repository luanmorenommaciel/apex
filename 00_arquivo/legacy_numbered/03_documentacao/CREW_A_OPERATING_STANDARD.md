# Crew A — Padrão de Operação (Apex)

> Padrão de report, documentação e prevenção de pontos cegos para a Crew A.
> Alinhado às convenções que o Commander já usa nas issues do repo `luanmorenommaciel/apex`.
> Autor: Augusto (Captain) · v1 · 06 jun 2026

---

## 1. Princípio central

**"Done local" não é "Done".** Um trabalho só conta quando está **visível no sistema de
tracking do time** (issue atualizada) e **verificável** (commit/PR linkado, evidência de
execução). O maior ponto cego é trabalho feito que ninguém consegue ver.

---

## 2. Convenções de Issues (as que o Commander já usa)

Toda peça de trabalho referencia uma issue. Não crie um padrão novo — use o existente:

### Prefixos de título
| Prefixo | Uso |
|---|---|
| `[FEATURE]` | Capacidade que o usuário final vê (ex: Watcher pipeline) |
| `[ADR-NNN]` | Architecture Decision Record |
| `[CA]` | Item de coordenação da Crew A |
| `[BLOCKER]` | Dependência que trava outras coisas |

### Labels (taxonomia oficial)
| Grupo | Valores |
|---|---|
| `phase:` | `spec` → `design` → `build` → `ship` (fases do SDD/AgentSpec) |
| `priority:` | `p0` (crítico/urgente) · `p1` (importante) · `p2` (normal) |
| `type:` | `feature` · `adr` · `blocker` · `commander-attention` |
| outros | `crew-a` · `blocked` |

### Regra de ouro
Antes de começar qualquer trabalho: **existe uma issue?** Se não, crie (ou peça ao Commander).
Ao terminar: **a issue reflete o que foi feito?** Se não, comente com o progresso e linke o commit.

---

## 3. Padrão de Report

### 3.1 Comentário de progresso (na issue)
A cada avanço relevante, um comentário na issue correspondente, neste formato:

```
## Progresso — <data>

**O que avançou:** <1-2 frases concretas>
**Evidência:** <link do commit / output do run / screenshot>
**Estado:** <em andamento | bloqueado | pronto para review>
**Próximo passo:** <o que vem agora>
**Honestidade:** <se algum "verde" veio de afrouxar checagem, declare aqui>
```

### 3.2 Report de sync (Captain → Commander)
Um por sync, no formato de 4 blocos. Curto, escaneável:

```
# Captain's Report — Crew A — <data>

## Avançou
- <item> (issue #NN) — <evidência>

## Bloqueado
- <item> (issue #NN) — <o que destrava, quem precisa agir>

## Precisa do Commander
- <decisão necessária> (issue #NN, type:commander-attention)

## Honestidade
- <green forjado? suposição não validada? dívida técnica assumida?>
```

A seção **Honestidade** é obrigatória e nunca fica vazia por padrão — se está vazia, você
provavelmente não procurou direito.

---

## 4. Padrão de Documentação

| Artefato | Onde vive | Convenção |
|---|---|---|
| **ADR** | Issue `[ADR-NNN]` + label `type:adr` | Contexto → Decisão → Consequências → Alternativas |
| **SDD** | Doc no repo | 5 fases: Brainstorm → Define → Design → Build → Ship |
| **Spec técnica** | `docs/` no repo (HTML/MD), versionada | Documento vivo; atualiza a cada versão |
| **Playbook** | `docs/` no repo | Registro operacional: o que foi feito, problemas, soluções |
| **Commits** | — | Conventional commits (`feat:`, `fix:`, `refactor:`, `docs:`) + corpo com bullets |

### Template de ADR
```
# ADR-NNN — <título da decisão>
**Status:** proposto | aceito | substituído por ADR-MMM
**Contexto:** <o problema que força a decisão>
**Decisão:** <o que foi decidido>
**Consequências:** <o que isso implica, bom e ruim>
**Alternativas consideradas:** <o que foi descartado e por quê>
```

---

## 5. Checklist anti-pontos-cegos

Rodar **antes de declarar qualquer coisa "pronta"**. Derivado dos erros reais que morderam
esta Crew:

- [ ] **Rastreável** — o trabalho está refletido numa issue, com commit/PR linkado?
- [ ] **Green honesto** — o verde veio de uma checagem real, ou de afrouxar a checagem (tolerância, `or [1]`, `if False:`)?
- [ ] **Validado contra a realidade** — testei contra dado real (Spark real), ou só contra o sintético que eu mesmo gerei?
- [ ] **Plano certo** — li o plano final pós-AQE, não o inicial? (o plano muda em pleno voo)
- [ ] **Coberto por teste** — existe um teste que falha se isso regredir?
- [ ] **Decisão registrada** — toda escolha de arquitetura virou um ADR?
- [ ] **Bloqueio escalado** — todo blocker tem issue (`type:blocker`) e foi levado ao Commander?
- [ ] **Premissa intacta** — a coleta continua não-intrusiva (zero JAR, zero listener injetado)?
- [ ] **Contrato é a verdade** — código e telemetria correspondem ao contrato, com guard automático?

Se qualquer caixa não está marcada, **não está pronto** — está "quase".

---

## 6. Cadência

| Quando | O quê |
|---|---|
| A cada commit relevante | Comentário de progresso na issue |
| A cada sync | Captain's Report (4 blocos) |
| A cada decisão de arquitetura | ADR como issue |
| A cada blocker | Issue `type:blocker` + escalar ao Commander no mesmo dia |
| Fim de sprint | Atualizar spec + playbook no repo |

---

## 7. Ação imediata (fechar o ponto cego atual)

O trabalho v3 está invisível nas issues. Antes da próxima sync:

1. Comentar progresso em **#17** (Watcher), **#19** (plat-v0), **#20** (Recommendation), **#21** (CI) — linkando o commit `357efad`
2. Atualizar/fechar **#28** (BLOCKER repo access) — se desbloqueado de fato
3. Abrir ADR do **desacoplamento via scenario.yaml** (a lição de casa respondida) como `[ADR-NNN]` + `type:adr`
4. Levar o Captain's Report da sync com a seção Honestidade preenchida (os band-aids viraram causa raiz no v3 — isso é conteúdo de report)
