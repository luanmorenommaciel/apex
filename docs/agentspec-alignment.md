# Alinhamento com AgentSpec

Referencia:

```text
https://github.com/luanmorenommaciel/agentspec
```

AgentSpec usa Spec-Driven Data Engineering: primeiro define o contrato, depois desenha, implementa, valida e registra o aprendizado. O slice Apex `skew_on_join_30x` segue o mesmo padrao.

## Mapeamento do workflow

| AgentSpec | Apex `skew_on_join_30x` |
|---|---|
| Brainstorm | Apresentacao `docs/presentations/apex-v2-aqe-learnings.html` e achados do AQE |
| Define | `scenarios/skew_on_join_30x.yaml` |
| Design | `docs/specs/skew-slice-v4.md` |
| Build | `apex/`, `generators/`, `watchers/`, `oracle/` |
| Ship | `docs/apex-v4-lineage.md`, testes e scenario gate |
| Iterate | Proximos passos: baseline sem skew, `validation_criteria`, confidence por evidencia |

## Principios aplicados

### KB-first

O slice parte de evidencia local:

- log real versionado em `real_log.ndjson`;
- resultados do Ubuntu/WSL;
- apresentacao tecnica sobre AQE;
- issues do Apex.

### Confidence-scored

O Watcher ainda usa uma formula simples de confianca. A documentacao marca isso como proximo trabalho, porque AgentSpec exige confianca baseada em evidencia, nao autoavaliacao.

Proximo desenho:

```text
confidence = f(n_tasks, estabilidade_do_ratio, join_operator, qualidade_do_log, provenance)
```

### Quality-gated

O slice nao depende de leitura manual para ser aceito. Ele tem gates executaveis:

```bash
python3 -m pytest tests/test_slice.py -q
bash run_slice.sh
python3 oracle/compare.py scenarios/skew_on_join_30x.yaml /tmp/apex-synthetic.ndjson real_log.ndjson
```

### Escalation-aware

O slice nao tenta resolver todo o Apex. Ele entrega um Watcher deterministico para skew e aponta os limites:

- memory/cost watcher fica para outro componente;
- CI integration fica para a issue #21;
- governanca do fork/plataforma fica para #23 e #25.

## Convenção para proximas entregas

Cada novo anti-pattern do Apex deve trazer:

1. `scenario.yaml` com contrato declarativo.
2. Spec tecnica em `docs/specs/`.
3. Playbook em `docs/playbooks/`.
4. Testes de unidade e fluxo.
5. Evidencia contra log real ou fixture explicita.
6. Linha de issues do Apex que justifica o trabalho.

Sem esses itens, a entrega ainda e experimento, nao slice pronto para PR.
