# Apex

**Peak Performance for Spark & Databricks.**  
Catches what code reviews miss. Fixes what production reveals.

[![CI](https://github.com/luanmorenommaciel/apex/actions/workflows/scenario-gate.yml/badge.svg)](https://github.com/luanmorenommaciel/apex/actions/workflows/scenario-gate.yml)
[![Version](https://img.shields.io/badge/v4-branch-orange)](CHANGELOG.md)

> **Estrutura local espelha a branch:** `gustocezar/feature/desacoplamento-geradores`  
> Para commitar no GitHub, seguir `COMO_COMMITAR.md`.

---

## O que é

O Apex detecta anti-patterns de performance em jobs Spark analisando event logs — **sem injetar nada no cluster**. Zero JAR, zero modificação de SparkSession. Tudo via leitura de logs.

**Arquitetura em 4 tiers:**
```
Tier 1 · Watchers      → determinístico, zero LLM  ← implementado (v4)
Tier 2 · Classifier    → LLM leve (classifica o Finding)
Tier 3 · Coordinator   → Sonnet (orquestra o diagnóstico)
Tier 4 · Judge         → Opus (segunda opinião, confiança < 0.6)
```

---

## Quick Start

```bash
pip install -r requirements.txt

# Rodar slice completo
bash run_slice.sh

# Passo a passo
python3 generators/plan_generator.py scenarios/skew_on_join_30x.yaml /tmp/synthetic.ndjson
python3 watchers/skew_watcher.py scenarios/skew_on_join_30x.yaml /tmp/synthetic.ndjson
python3 oracle/compare.py scenarios/skew_on_join_30x.yaml /tmp/synthetic.ndjson real_log.ndjson

# Testes
python3 -m pytest tests/ -q
```

---

## Estrutura

```
apex/
├── .claude/                # Claude Code — agente e comandos
├── .github/workflows/      # oracle-weekly (semanal)
├── apex/apexlib.py         # lib compartilhada — parse de event logs
├── docs/
│   ├── adr/                # Architecture Decision Records
│   ├── llm-evals/          # comparação de modelos para Tiers 2–4
│   ├── playbooks/          # como rodar e interpretar cada slice
│   ├── presentations/      # HTMLs de apresentação
│   ├── specs/              # especificações técnicas por slice
│   ├── agentspec-alignment.md
│   ├── apex-v4-lineage.md
│   ├── architecture.md
│   └── team-validation-guide.md
├── generators/             # code_generator + plan_generator
├── oracle/compare.py       # valida sintético vs real
├── scenarios/              # contratos YAML dos cenários
├── tasks/
│   ├── backlog.md          # pontos de falha + próximos passos
│   └── apex_roadmap_v4.md  # roadmap vivo
├── tests/                  # suite de testes
├── watchers/               # Skew Watcher v4 (+ próximos)
├── 00_arquivo/             # legacy (não commitar)
├── AGENTS.md               # instruções para agentes de IA
├── CHANGELOG.md
├── CLAUDE.md               # contexto completo para Claude Code
├── COMO_COMMITAR.md        # guia para commitar no apex GitHub
└── CONTRIBUTING.md
```

---

## Evidência atual (v4)

```
synthetic ratio: 27.9x
real ratio:      29.5x
watcher:         GATE VERDE
oracle:          sintetico fiel ao Spark real dentro da tolerancia
```

---

## Crew A

Captain: Augusto · Commander: Luan  
Issues: [github.com/luanmorenommaciel/apex/issues](https://github.com/luanmorenommaciel/apex/issues)  
Validação v4: [Issue #29](https://github.com/luanmorenommaciel/apex/issues/29)

---

## Documentação

- [Arquitetura](docs/architecture.md) — 4 tiers, fluxo, apexlib
- [Spec do slice](docs/specs/skew-slice-v4.md) — contrato, fórmula, limites
- [Playbook](docs/playbooks/skew-slice-v4.md) — como rodar e interpretar
- [Linhagem v4](docs/apex-v4-lineage.md) — o que corrigiu e por quê
- [Guia de validação](docs/team-validation-guide.md) — para a reunião da Crew A
- [Backlog](tasks/backlog.md) — pontos de falha abertos
- [Changelog](CHANGELOG.md) — v1 → v2 → v3 → v4
- [LLM Evals](docs/llm-evals/) — comparação de modelos para Tiers 2–4
