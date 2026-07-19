# F7 Remote Real Stack Self-Hosted Playbook

Objetivo: executar remotamente o job `real-stack` do `Apex Scenario Gate` usando
um runner self-hosted temporario na maquina que ja tem Docker Desktop e a imagem
Spark 4.1.2 preparada.

Este playbook nao instala servico permanente. O modo recomendado e foreground:
o runner fica ativo somente enquanto o terminal `run.cmd` estiver aberto.

## Pre-requisitos

- `gh auth status` autenticado no GitHub com acesso admin ao repo
  `gustocezar/apex-workspace`.
- Docker Desktop rodando.
- Branch `codex-round2` publicada.
- PowerShell em Windows.

## 1. Registrar runner temporario

Na raiz da branch:

```powershell
cd C:\Users\Guest\Documents\project\codex\apex\apex-official
.\scripts\register_github_self_hosted_runner.ps1
```

O script:

- baixa o GitHub Actions runner Windows x64 mais recente;
- obtem token via `gh api` no momento da execucao;
- registra o runner com labels `apex,docker,spark412`;
- nao salva token no repositorio.

## 2. Iniciar runner em foreground

No mesmo terminal ou em outro:

```powershell
cd $env:USERPROFILE\actions-runner-apex-workspace
.\run.cmd
```

Mantenha esse terminal aberto ate o workflow terminar.

## 3. Disparar workflow real

Em outro terminal:

```powershell
gh workflow run scenario-gate.yml `
  --repo gustocezar/apex-workspace `
  --ref codex-round2 `
  -f run_real_stack=true
```

Depois observe:

```powershell
gh run list --repo gustocezar/apex-workspace --workflow scenario-gate.yml --limit 5
```

Quando aparecer a run nova:

```powershell
gh run watch <RUN_ID> --repo gustocezar/apex-workspace --exit-status
```

## 4. Evidencia esperada

O job `real-stack` deve publicar artifact `f7-autonomous-stack-loop-real` contendo:

```text
evidence/f7-autonomous-stack-loop-github-real-stack.log
evidence/generated/f7-autonomous-loop/github-real-stack/**
```

O log deve conter:

```text
loop_status=success
finding_count: before > 0, after = 0
max_skew_ratio: before > 0, after = 0.0
```

## 5. Remover runner

Quando terminar:

```powershell
cd C:\Users\Guest\Documents\project\codex\apex\apex-official
.\scripts\unregister_github_self_hosted_runner.ps1
```

Tambem pode apagar a pasta local do runner depois de remover:

```powershell
Remove-Item -Recurse -Force $env:USERPROFILE\actions-runner-apex-workspace
```

## Bloqueio Atual Registrado

As runs remotas `29664652802` e `29664707350` aceitaram dispatch, mas os jobs
`ubuntu-latest` falharam antes de executar qualquer step (`duration_ms=0`).
Por isso o caminho confiavel para fechar a evidencia remota real agora e usar o
runner self-hosted temporario acima.
