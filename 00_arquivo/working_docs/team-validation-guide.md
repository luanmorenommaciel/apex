# Guia de Validacao para a Crew A

> **Fonte canônica:** branch `gustocezar/feature/desacoplamento-geradores`  
> Ver `docs/team-validation-guide.md` na branch para versão completa com diagramas Mermaid.

## Resultado atual

```text
synthetic ratio: 27.9x
real ratio:      29.5x
watcher:         GATE VERDE
oracle:          sintetico fiel ao Spark real dentro da tolerancia
```

## O que está provado

| Ponto | Status |
|---|---|
| Scenario declarativo para skew | ✅ Provado |
| Event log sintético sem Spark | ✅ Provado |
| Watcher determinístico de skew | ✅ Provado |
| Comparação com log real | ✅ Provado |
| Testes automatizados | ✅ Provado |
| Gate inicial de CI | ✅ Provado |

## O que ainda não está provado

| Ponto | Motivo |
|---|---|
| Todos os anti-patterns | Só skew em join |
| Falso positivo sem skew | Falta `no_skew_baseline.yaml` |
| Confidence madura | Fórmula ainda simples |
| Persistência em ClickHouse | Usa arquivos versionados |
| Core em Go | Python como laboratório |

## Decisões para a Crew A

1. Aceitar slice como referência e evoluir em slices pequenos?
2. Manter fork `gustocezar/dataship-spark-plat-v0` como repo de evidência?
3. Confirmar contrato não-intrusivo (zero JAR, zero listener)?
4. Qual próximo passo técnico?

## Como o Captain conduz

**Para abrir:**
> O objetivo hoje não é dizer que o Apex está pronto. O objetivo é validar se esta fatia prova o caminho: contrato declarativo, evidência reproduzível, Watcher determinístico e comparação com log real.

**Para fechar:**
> Se o time concordar com esta abordagem, o próximo passo não é aumentar o escopo. O próximo passo é repetir o mesmo padrão com baseline sem skew e critérios de validação mais claros.
