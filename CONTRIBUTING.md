# Contributing — Apex

## Crew A — Padrão de operação

Antes de qualquer contribuição, ler o `CLAUDE.md` para contexto completo.

---

## Fluxo de trabalho

```
issue GitHub → branch → código → testes → gate verde → PR → merge → comentar issue
```

Cada passo conta. "Done local ≠ Done" — só conta quando visível nas issues.

---

## Antes de começar

1. **Existe uma issue?** Se não, crie antes de escrever código.
2. **O contrato está atualizado?** Mudanças no `scenario.yaml` afetam code_generator, plan_generator e Watcher.
3. **Rodou o checklist?** Ver seção abaixo.

---

## Adicionando um novo Watcher

1. Criar `watchers/<anti_pattern>_watcher.py`
2. Criar `scenarios/<scenario_id>.yaml` com `acceptance` declarado
3. O Watcher deve usar `apexlib` — nunca reimplementar `read_events`, `join_operator` ou `hottest_reduce_stage`
4. Adicionar testes em `tests/test_slice.py`
5. Verificar que o gate de CI passa: `pytest tests/ -v`

---

## Adicionando um novo cenário

1. Criar `scenarios/<scenario_id>.yaml`
2. Seguir o schema de `skew_on_join_30x.yaml` como referência
3. Incluir `acceptance.root_cause_includes` com termos específicos do cenário
4. Resolver P1-7 antes (chave hardcoded no skew_watcher)

---

## Padrão de commit

```
feat: adiciona Memory Watcher (Pod A2) — #17
fix: read_events streaming zstd elimina OOM — #19
refactor: join_operator filtra por executionId — #17
docs: ADR-005 decisão sobre Tier 2 LLM
test: manifesto job.meta.json validado — #21
```

---

## Comentário de progresso nas issues

A cada commit relevante, comentar na issue correspondente:

```markdown
## Progresso — <data>
**O que avançou:** <1-2 frases>
**Evidência:** <link do commit>
**Estado:** em andamento | bloqueado | pronto para review
**Próximo passo:** <o que vem agora>
**Honestidade:** <algum green veio de afrouxar checagem?>
```

---

## Checklist antes de abrir PR

- [ ] `pytest tests/ -v` — todos passando
- [ ] Gate do cenário verde: `python watchers/<watcher>.py scenarios/<cenário>.yaml log.ndjson`
- [ ] Issue linkada no commit
- [ ] `CHANGELOG.md` atualizado (seção Unreleased)
- [ ] `tasks/backlog.md` atualizado se um ponto foi fechado

---

## Checklist anti-pontos-cegos

Rodar antes de declarar qualquer coisa pronta:

- [ ] Rastreável — trabalho refletido numa issue com commit linkado?
- [ ] Green honesto — o verde veio de checagem real ou afrouxamento?
- [ ] Validado contra Spark real, não só sintético?
- [ ] Leu plano final pós-AQE (não o inicial)?
- [ ] Existe teste que falha se isso regredir?
- [ ] Decisão de arquitetura virou ADR?
- [ ] Blocker escalado ao Commander no mesmo dia?
- [ ] Coleta continua não-intrusiva (zero JAR, zero listener)?
- [ ] Contrato é a verdade — guard automático no CI?
