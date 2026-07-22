# Apex Codex e DataFlint - Comparacao Atual (2026-07-22)

## Escopo e metodo

Esta e a comparacao atual de produto da branch `codex-round2`. Ela usa as
evidencias ja versionadas nesta branch; nao reexecuta gates nesta atualizacao.
O estado de runtime referenciado e o pacote publicado em `0f345df`; o HEAD
`a500718` acrescenta somente material de apresentacao e indice documental.

DataFlint e avaliado apenas por fontes oficiais publicas consultadas em
22/07/2026. `V` significa evidencia local executavel do APEX; `P` significa
capacidade parcial; `E` significa capacidade declarada pelo fornecedor, nao
validada por este repositorio. Nao ha comparacao de preco, performance ou
qualidade em igualdade de ambiente.

## Matriz de capacidade

| Dimensao | Apex Codex | DataFlint | Leitura objetiva |
|---|---|---|---|
| Coleta Spark | **V** Spark event log, S3A/MinIO e `ApexSparkListener` JVM fail-safe em Spark 4.1.2 | **E** plugin Spark, History Server e logs enriquecidos | Ambos se conectam ao runtime Spark; o APEX prova listener e event log locais. |
| Diagnostico deterministico | **V** skew, GC, spill, OOM e cartesian com G1/G2 | **E** alertas e sugestoes de performance | O APEX publica os limiares, testes e logs; o catalogo interno do produto DataFlint nao foi auditado aqui. |
| Evidencia real | **V** G3/G5 com ratio `29.4 -> 0.0`, finding `1 -> 0` | **E** contexto de producao enriquecido | O APEX prova um caso reprodutivel; DataFlint anuncia cobertura de producao em escala. |
| Latencia sem LLM | **V** T1 em `226.991 ms`, sem LLM obrigatorio | Nao publicado | Vantagem verificavel do APEX neste recorte; nao e benchmark comparavel de ponta a ponta. |
| MCP e IDE | **V** MCP stdio, Claude Code GUI, 16 tools e preview guardado | **E** Spark MCP para Cursor, VS Code e IntelliJ | Ambos usam MCP como ponte com IDE; DataFlint declara integracao mais ampla. |
| Correcao de codigo | **V** `preview -> approval token -> apply_fix -> verify -> rerun -> compare` | **E** sugestoes e one-click fixes no IDE | O APEX torna token, hash e `apply_root` visiveis e testaveis; o fluxo interno DataFlint nao foi inspecionado. |
| Judge/LLM | **V** Crew/Judge opcional, read-only, com chamada externa observada | **E** Copilot e agentes proprietarios | O APEX mantem T1 e EvidenceValidator antes do LLM; nao oferece autonomia de producao sem aprovacao humana. |
| UI/observabilidade | **P** UI local single-user, read-only, dados versionados | **E** UI Spark, Fleet Observability e custo por stage/time | Este e o maior gap de produto do APEX: falta dashboard multi-job, identidade e operacao compartilhada. |
| Operacao autonoma | **P** runner self-hosted e rerun guardado; sem auto right-sizing | **E** Cluster Agent e Review Agent | O APEX ainda nao tem agente de cluster nem revisao automatica de PR. |
| Governanca | **P** artefatos locais, tokens de aplicacao e evidencias versionadas; sem RBAC | **E** SSO/SCIM/RBAC no plano empresarial | APEX e adequado ao laboratorio/local-first; nao e substituto de governanca corporativa. |

## O que o APEX ja prova

1. Um finding real de skew pode ser detectado, validado, corrigido sob guarda e
   comparado depois da reexecucao.
2. O caminho T1 funciona sem custo de LLM no caminho quente.
3. O listener JVM e o compose autonomo foram exercitados em Spark 4.1.2.
4. O MCP foi usado em Claude Code GUI; a UI local mostra o mesmo caso `job-42`
   sem expor token ou oferecer apply direto.

Evidencias principais: `evidence/g1-baseline.log`,
`evidence/g2-cenarios.log`, `evidence/g3-real.log`, `evidence/g4-t1.log`,
`evidence/g5-ciclo.log`, `evidence/g6-mcp-ide-gui-smoke-2026-07-18.log`,
`evidence/f7-remote-real-stack-run-29671461366-loop.log` e
`evidence/crew-judge-external-llm-success-final-2026-07-19.json`.

## O que ainda separa o APEX de um produto como DataFlint

1. UI multiusuaria com consulta de dados vivos, autenticacao e RBAC.
2. Observabilidade de frota, atribuicao de custo e ranking continuo de impacto.
3. Agente de cluster com right-sizing automatico e agente de revisao de pull
   request.
4. Compatibilidade de producao documentada para mais plataformas e suporte
   operacional.

Esses itens sao backlog de produto. Nao devem ser declarados como entregues
pelo APEX nesta rodada.

## Diferencial competitivo defensavel hoje

O APEX nao deve prometer mais cobertura de produto do que DataFlint. O seu
diferencial atual e **local-first e auditavel**: detector, validator, evidencia,
diff, token, hash e comparacao antes/depois ficam no repositorio e podem ser
reexecutados pela equipe. Isso e util para uma organizacao que queira adaptar
limiares, manter dados no proprio ambiente e revisar cada passo antes do apply.

## Fontes oficiais DataFlint

- [DataFlint OSS para Spark](https://github.com/dataflint/spark): plugin, UI,
  compatibilidade Spark 4 e release `0.9.9`.
- [DataFlint Product](https://www.dataflint.io/product): Spark MCP, Copilot,
  Cluster Agent, Review Agent e Fleet Observability.
- [Como a plataforma funciona](https://www.dataflint.io/resources/how-it-works):
  enriquecimento de logs, MCP e agentes.
- [Spark Copilot](https://www.dataflint.io/product/spark-copilot): integrações
  IDE e fluxo de sugestao/correcao.

## Documentos relacionados

- `README.md`: ponto de entrada e estado atual da branch.
- `docs/guides/apex-commander-macro-flow-2026-07-22.md`: fluxo didatico.
- `docs/playbooks/apex-operator-judge-2026-07-22.md`: roteiro operacional e
  criterios de revisao.
- `docs/architecture/llm-solution-validation-framework-2026-07-15.md`:
  historico do campeonato; nao e fonte atual de comparacao.
