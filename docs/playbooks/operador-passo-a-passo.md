# Operador (Augusto) — Passo a Passo da Rodada 2 por LLM

> Você é o OPERADOR: prepara a pasta, cola o prompt, executa os comandos que a
> engine pedir (docker/pytest/git) e cobra os entregáveis. Igual às sessões com
> a cowork. Uma engine por vez.

## Passo 0 — Governança: onde cada coisa vive (não poluir o Apex)

| Material | Onde | Regra |
|---|---|---|
| Kit do campeonato (pacote-comum, playbooks, julgamentos, relatórios) | **repo pessoal** `gustocezar/apex-workspace`, branch `campeonato/round2` | NUNCA vai ao repo do time |
| Trabalho round 2 das engines | branch `<llm>-round2` no **repo pessoal** (base: clone da branch existente delas) | push só para `origin` pessoal |
| Repo do time (`luanmorenommaciel/apex`) | intocado durante o campeonato | só recebe algo com aprovação do Commander (resultado final → ADR-006 rev. + merge decidido) |

Criação da branch do campeonato (1x — pasta própria, história limpa):
```powershell
mkdir C:\Users\Guest\projetos\apex-campeonato
cd C:\Users\Guest\projetos\apex-campeonato
git init -b campeonato/round2
git remote add origin https://github.com/gustocezar/apex-workspace.git
# copiar o kit a partir do Data Ship:
$src = "C:\Users\Guest\Claude\Projects\Data Ship"
mkdir pacote-comum\scenarios, playbooks, julgamento -Force
copy "$src\docs\specs\apex-v1-spec-reproducivel.md"    pacote-comum\
copy "$src\docs\specs\telemetry-schema-contract-v1.md" pacote-comum\
copy "$src\docs\specs\apex_telemetry_v1.sql"           pacote-comum\
copy "$src\docs\specs\criterios-e-gates.md"            pacote-comum\
copy "$src\docs\specs\manifest-rodada2.json"           pacote-comum\
copy "$src\docs\specs\apex-v1-pacote-completo.md"      pacote-comum\
copy "$src\docs\playbooks\protocolo-rodada2-llms.md"   pacote-comum\
copy "$src\docs\playbooks\g3-multicore-runbook.md"     pacote-comum\
copy "$src\docs\CREW_A_OPERATING_STANDARD.md"           pacote-comum\
copy "$src\scenarios\*.yaml"                            pacote-comum\scenarios\
copy "$src\scripts\g3_multicore_gate.py"                pacote-comum\
copy "$src\scripts\fetch_real_log.py"                   pacote-comum\
copy "$src\docs\playbooks\operador-passo-a-passo.md"   playbooks\
copy "$src\docs\playbooks\orquestrador-juiz-llm.md"    playbooks\
"placeholder" | Out-File julgamento\.gitkeep
git add -A
git commit -m "campeonato round2: kit de orquestracao, pacote comum congelado e area de julgamento"
git tag round2-freeze
git push -u origin campeonato/round2 --tags
```

## Passo 1 — Preparar a pasta da engine (1x por LLM)

**Kimi** (exemplo — para Codex, use a pasta `apex-official` que já existe):
```powershell
cd C:\Users\Guest\projetos
git clone https://github.com/luanmorenommaciel/apex.git apex-kimi-round2
cd apex-kimi-round2
git checkout gustocezar/feature/kimi-desacoplamento-geradores
git checkout -b kimi-round2
# round 2 NAO polui o repo do time: push vai para o seu workspace pessoal
git remote set-url origin https://github.com/gustocezar/apex-workspace.git
git push -u origin kimi-round2
```

## Passo 2 — Copiar o pacote comum para dentro da pasta da engine

```powershell
$src  = "C:\Users\Guest\Claude\Projects\Data Ship"
$dest = "C:\Users\Guest\projetos\apex-kimi-round2\pacote-comum"   # ajuste por engine
mkdir $dest\scenarios -Force
copy "$src\docs\specs\apex-v1-spec-reproducivel.md"      $dest
copy "$src\docs\specs\telemetry-schema-contract-v1.md"   $dest
copy "$src\docs\specs\apex_telemetry_v1.sql"             $dest
copy "$src\docs\specs\criterios-e-gates.md"              $dest
copy "$src\docs\playbooks\protocolo-rodada2-llms.md"     $dest
copy "$src\docs\playbooks\g3-multicore-runbook.md"       $dest
copy "$src\docs\CREW_A_OPERATING_STANDARD.md"            $dest
copy "$src\scenarios\*.yaml"                             $dest\scenarios\
copy "$src\scripts\g3_multicore_gate.py"                 $dest
copy "$src\scripts\fetch_real_log.py"                    $dest
```
**NÃO copiar:** framework de avaliação, MELHORIAS.md, código da cowork, docs/avaliacao.

## Passo 3 — Abrir a ferramenta da engine na pasta e colar o prompt de largada

Prompt (ajuste `<LLM>` e `<branch>`; para Kimi: branch
`gustocezar/feature/kimi-desacoplamento-geradores`; para Codex:
`gustocezar/feature/codex-desacoplamento-geradores` na pasta `apex-official`):

> Você é a engine `<LLM>`. Você JÁ construiu uma solução para o Apex nesta
> branch (`<branch>`) — trabalho válido, seu ponto de partida. O pacote comum
> está na pasta `pacote-comum/` deste workspace: leia primeiro
> `apex-v1-spec-reproducivel.md`, depois `protocolo-rodada2-llms.md`,
> `criterios-e-gates.md` e os contratos. Sua missão: ESTRUTURAR e completar sua
> solução no formato comum, seguindo as fases F0–F6 do protocolo. Comece AGORA
> pelo passo 0 (criar estrutura: `evidence/`, `docs/adr/`, `docs/meetings/`,
> `PLANO.md`, `ISSUES.md`, `docs/autoavaliacao.md`, `MELHORIAS.md`) e pela fase
> F0: escreva o `PLANO.md` mapeando com honestidade seu estado atual contra
> cada premissa L1–L9 e cada gate G0–G5, com evidência, gaps e ordem de
> fechamento. Contratos e scenarios do pacote são IMUTÁVEIS. Claim sem log cru
> em `evidence/` não existe. Ao terminar o PLANO.md, PARE e me apresente para
> revisão antes de seguir à F1. "Done local ≠ done".

## Passo 4 — O ciclo de cada sessão (repete até F6)

1. Engine trabalha; quando pedir comando (docker, pytest, spark-submit), você
   executa no PowerShell e cola o output — igual fazemos na cowork.
2. Fim de sessão: cobre os 3 fechamentos — `ISSUES.md` atualizado, Captain's
   Report da sessão, commit+push na branch dela.
3. Sessão seguinte, cole: *"Continue o protocolo rodada 2. Estamos na fase F<n>.
   Leia PLANO.md, ISSUES.md e o último captains-report antes de agir."*
4. Checkpoint seu por fase: o `evidence/g<n>-*.log` existe e é cru? Se não,
   não deixe avançar.

## Passo 5 — Quando a engine terminar (F5+F6 entregues)

Confira os entregáveis obrigatórios (manifest `deliverables_per_engine`),
faça o push final e repita os passos 1–4 com a próxima engine.

## Passo 6 — Julgamento (depois de TODAS)

Abra uma LLM que não competiu APONTADA PARA A PASTA `apex-campeonato`
(branch `campeonato/round2`) — os relatórios dela nascem em `julgamento/` dessa
branch, nunca no repo do time. Dê a ela acesso de leitura às branches das
engines (clones locais) + tag `round2-freeze`, e cole o prompt de ativação de
`playbooks/orquestrador-juiz-llm.md` §5. Você executa as re-execuções que
ela pedir. Saída: `julgamento/relatorio-*.md` + scorecard consolidado → sync
com o Luan → revisão do ADR-006.

## Perguntas frequentes do operador

- **"Peço para carregar arquivo?"** Não precisa — o pacote está em
  `pacote-comum/` dentro do workspace; o prompt manda ler. Se a ferramenta não
  ler arquivos sozinha, anexe os 4 primeiros do passo 2 no chat.
- **"A engine quer ver a branch da cowork/outras"** — negue; aponte a spec.
- **"Travou numa fase"** — blocker no ISSUES.md + Captain's Report, segue parcial.
- **"Posso rodar duas engines em paralelo?"** Pode (pastas separadas), mas o
  plat-v0 é um só — os gates G3/G5 fazem um de cada vez.
