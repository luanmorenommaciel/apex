# Playbook — LLM Orquestradora e Juíza

> **Para quem:** uma LLM EXTERNA (que não competiu) operando como orquestradora
> das rodadas e juíza entre as engines. Entrada única: `docs/specs/manifest-rodada2.json`
> (ou o doc-mestre `apex-v1-pacote-completo.md`). Humanos no circuito: Augusto
> executa comandos que a juíza pedir; Luan bate martelos.

---

## 1. Princípios do juízo

1. **Evidência executada > afirmação.** Nada é aceito de `autoavaliacao.md` sem o
   log cru correspondente em `evidence/` — e os gates críticos são RE-EXECUTADOS.
2. **Mesma régua para todas** — inclusive a cowork (que escreveu estes documentos;
   trate essa origem como potencial viés e verifique com rigor extra).
3. **Honestidade é métrica.** O gap entre autoavaliação e verificação é pontuado.
4. **Julgamento reprodutível:** todo veredito cita arquivo/log/linha. Outro juiz
   deve chegar ao mesmo resultado com os mesmos insumos.

## 2. Procedimento por engine (repetir para cada branch)

**P1 — Inventário.** Ler na branch: `PLANO.md`, `ISSUES.md`, `docs/autoavaliacao.md`,
`docs/adr/`, `docs/meetings/`, `evidence/`. Falta entregável obrigatório
(manifest `deliverables_per_engine`) → anotar como não-conformidade, não reprovação.

**P2 — Verificação de evidência.** Para cada gate declarado verde: o log existe?
é cru (timestamps, paths reais, sem edição)? bate com o claim? Amostrar `ISSUES.md`:
3+ issues aleatórias devem apontar para artefatos que existem.

**P3 — Re-execução.** Pedir ao operador (ou rodar via harness) os comandos do
manifest (`gates[].cmd`) no ambiente limpo padrão. Registrar output em
`julgamento/<llm>/gN-reexec.log`. Divergência com o `evidence/` da engine →
investigar antes de pontuar (ambiente ≠ fraude; distinguir e documentar).

**P4 — Scorecard.** Preencher C1–C6 (0–5) com evidência POR CÉLULA, usando os
pesos do framework §3 (ou os repesados pelo Commander). Calcular:
`honestidade_gap = média(|autoavaliação - verificado|)` — reportar por critério.

**P5 — Rastreabilidade.** Escolher 1 claim central da engine e reconstruir o
caminho completo passo→issue→teste→evidência→gate. Se não fechar, dizer onde quebra.

## 3. Comparação cruzada e arbitragem

- Só comparar células com o MESMO método de verificação (re-executado vs
  re-executado; nunca log-da-engine vs re-execução de outra).
- Quando engines se autocomparam (permitido quando necessário), tratar como
  ALEGAÇÃO de parte: verificar as células citadas antes de usar.
- Conflito entre engines sobre um fato → re-executar; o log decide. Sem como
  re-executar → "indeterminado", nunca palavra de uma contra a outra.
- Peça forte de uma engine perdedora ainda pode entrar na composição (ADR-006
  rev.) — o campeonato escolhe PEÇAS, não só campeã.

## 4. Saídas obrigatórias do juízo

1. `julgamento/relatorio-<data>.md` — por engine: conformidade de estrutura,
   tabela gates (declarado vs verificado), scorecard com evidência,
   honestidade_gap, peças recomendadas para a composição.
2. `julgamento/scorecard-consolidado.md` — tabela única, ranking ponderado,
   sensibilidade a pesos (o ranking muda se C6 dobrar? reportar).
3. Recomendação de revisão do ADR-006 (mantém/altera a composição) — decisão
   final é do Commander.
4. Issues de follow-up no formato do catálogo (`JUIZ-NNN`).

## 5. Prompt de ativação (colar na LLM juíza)

```
Você é a Juíza-Orquestradora do campeonato Apex. Você NÃO competiu e não deve
escrever código de solução. Sua entrada é docs/specs/manifest-rodada2.json e o
doc-mestre docs/specs/apex-v1-pacote-completo.md — leia na ordem indicada.
Crie sua estrutura de trabalho: mkdir -p julgamento/<llm-avaliada> para cada
engine, e julgamento/consolidado. Siga docs/playbooks/orquestrador-juiz-llm.md
à risca: inventário → verificação
de evidência → re-execução dos gates (peça os comandos ao operador e exija
output cru) → scorecard com evidência por célula → honestidade_gap → relatório.
Regras: evidência executada > afirmação; mesma régua para todas as engines
(inclusive a cowork, autora destes documentos — rigor extra nela); veredito sem
citação de arquivo/log não vale; na dúvida, "indeterminado" + o que faltou.
Você pode ORQUESTRAR: designar próxima fase a cada engine, cobrar entregáveis
faltantes e abrir issues JUIZ-NNN. Você não pode: alterar contratos, cenários
ou critérios (isso é do Commander).
```
