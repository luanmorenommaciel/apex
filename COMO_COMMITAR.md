# Como commitar esta estrutura no apex

> Este arquivo pode ser deletado após o commit.

## Passo 1 — Clonar o apex localmente

```bash
git clone https://github.com/luanmorenommaciel/apex
cd apex
```

## Passo 2 — Copiar o código v3 do plat-v0

```bash
# Copiar os diretórios de código do plat-v0 para o apex
# (ajustar o caminho conforme onde o plat-v0 está clonado)
cp -r <plat-v0>/apex_generators_v3/apex ./apex
cp -r <plat-v0>/apex_generators_v3/generators ./generators
cp -r <plat-v0>/apex_generators_v3/oracle ./oracle
cp -r <plat-v0>/apex_generators_v3/scenarios ./scenarios
cp -r <plat-v0>/apex_generators_v3/tests ./tests
cp -r <plat-v0>/apex_generators_v3/watchers ./watchers
cp <plat-v0>/apex_generators_v3/requirements.txt ./requirements.txt
cp <plat-v0>/apex_generators_v3/.github/workflows/scenario-gate.yml .github/workflows/
```

## Passo 3 — Copiar os arquivos de documentação desta pasta

```bash
# Copiar tudo desta pasta (06_apex_repo_ready) para o repo clonado
# exceto este arquivo COMO_COMMITAR.md
cp CLAUDE.md <apex>/
cp CHANGELOG.md <apex>/
cp CONTRIBUTING.md <apex>/
cp README.md <apex>/
cp -r docs/ <apex>/docs/
cp -r tasks/ <apex>/tasks/
cp -r .claude/ <apex>/.claude/
cp .github/workflows/oracle-weekly.yml <apex>/.github/workflows/
```

## Passo 4 — Commitar

```bash
cd apex
git add .
git commit -m "feat: estrutura v3 — código, docs, CLAUDE.md, backlog, ADR-004

- Adiciona apex/apexlib.py, generators/, watchers/, oracle/, scenarios/, tests/
- CLAUDE.md: contexto completo para Claude Code sessions
- CHANGELOG.md: histórico v1 → v2 → v3
- docs/architecture.md: 4 tiers + fluxo scenario.yaml
- docs/adr/ADR-004: desacoplamento generators via contrato (lição de casa do Commander)
- docs/llm-evals/: estrutura para comparações de LLMs (Tiers 2-4)
- tasks/backlog.md: 10 pontos de falha + LLM evals
- .github/workflows/oracle-weekly.yml: P2-12 — oracle semanal
- .claude/agents/apex/: agente especializado para Claude Code
- CONTRIBUTING.md: padrão de trabalho Crew A

Commit baseline do código: 357efad (plat-v0)
Issues relacionadas: #17 #19 #20 #21"

git push origin main
```

## Passo 5 — Atualizar as issues no GitHub

Depois do push, usar os comentários prontos em:
`Data Ship/03_documentacao/apex_github_ready_artifacts.md`

