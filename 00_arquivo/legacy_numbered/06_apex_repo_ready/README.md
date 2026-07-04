# Apex

**Peak Performance for Spark & Databricks.**  
Catches what code reviews miss. Fixes what production reveals.

[![CI](https://github.com/luanmorenommaciel/apex/actions/workflows/scenario-gate.yml/badge.svg)](https://github.com/luanmorenommaciel/apex/actions/workflows/scenario-gate.yml)
[![Version](https://img.shields.io/badge/v0.3.0-prototype-orange)](CHANGELOG.md)

---

## O que é

O Apex detecta anti-patterns de performance em jobs Spark analisando event logs — **sem injetar nada no cluster**. Zero JAR, zero modificação de SparkSession. Tudo via leitura de logs do MinIO.

**Arquitetura em 4 tiers:**
```
Tier 1 · Watchers      → determinístico, zero LLM  ← implementado
Tier 2 · Classifier    → LLM leve (classifica o Finding)
Tier 3 · Coordinator   → Sonnet (orquestra o diagnóstico)
Tier 4 · Judge         → Opus (segunda opinião, confiança < 0.6)
```

---

## Quick Start

```bash
pip install -r requirements.txt

# Gerar fixture + rodar Watcher
python generators/code_generator.py scenarios/skew_on_join_30x.yaml job.py
python generators/plan_generator.py scenarios/skew_on_join_30x.yaml log.ndjson
python watchers/skew_watcher.py scenarios/skew_on_join_30x.yaml log.ndjson

# Testes
pytest tests/ -v
```

---

## Estrutura

```
apex/
├── .claude/                # Claude Code — agente e comandos
├── .github/workflows/      # scenario-gate (PR) + oracle-weekly (semanal)
├── apex/apexlib.py         # lib compartilhada — parse de event logs
├── docs/                   # arquitetura, ADRs, LLM evals
├── generators/             # code_generator + plan_generator
├── oracle/compare.py       # valida sintético vs real
├── scenarios/              # contratos YAML dos cenários
├── tasks/backlog.md        # pontos de falha + próximos passos
├── tests/                  # 13 testes unitários
├── watchers/               # Skew Watcher v3 (+ próximos)
├── CHANGELOG.md
├── CLAUDE.md               # contexto completo para Claude Code
└── CONTRIBUTING.md
```

---

## Como contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md) e [CLAUDE.md](CLAUDE.md).

**Crew A** · Captain: Augusto · Commander: Luan  
Issues: [github.com/luanmorenommaciel/apex/issues](https://github.com/luanmorenommaciel/apex/issues)

---

## Documentação

- [Arquitetura](docs/architecture.md) — 4 tiers, fluxo, apexlib, plat-v0
- [Backlog](tasks/backlog.md) — 10 pontos de falha + próximos passos
- [Changelog](CHANGELOG.md) — v1 → v2 → v3
- [ADRs](docs/adr/) — decisões de arquitetura
- [LLM Evals](docs/llm-evals/) — comparação de modelos para Tiers 2–4
