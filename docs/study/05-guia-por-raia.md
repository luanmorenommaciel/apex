# Guia de estudo por raia

## 1. DEV - laboratorio de patologias

**Onde ler:** `dev/README.md`, `dev/jobs/`, `dev/scripts/e2e_canonical.ps1`.

DEV cria quatro cargas previsiveis: `skew_join`, `spill`, `bad_shuffle` e
`driver_oom`. O objetivo nao e otimizar o job; e produzir sintomas conhecidos
para validar a cadeia inteira. O `job_id` emitido na execucao e o identificador
usado nas consultas posteriores.

**Pergunta de estudo:** como uma hot key cria cauda p99/p50 e por que AQE pode
alterar o plano sem apagar a evidencia original?

## 2. JAR - captura no driver Spark

**Onde ler:** `jar/README.md`, `jar/src/`, `jar/build.sbt`.

`ApexPlugin` e o caminho primario. Ele registra o listener, agrega
`TaskMetrics`, cria fingerprint de plano logico normalizado e exporta spans por
uma fila OTel limitada. `spark.extraListeners` existe como fallback, mas nao
tem o mesmo shutdown flush nem a captura AQE completa.

**Pergunta de estudo:** por que o fingerprint e logico/canonicalizado, em vez
de hash do plano fisico depois de AQE?

## 3. COLLECT - transporte e redacao

**Onde ler:** `collect/README.md`, `collect/config.yaml`, `collect/ddl/`.

O Collector recebe em `:4318`, aplica limite de memoria e redacao, depois
exporta para `otel_traces`. Materialized Views transformam a forma OTel para
as tabelas tipadas do contrato. O exporter nao deve escrever diretamente em
`spark_events`.

**Pergunta de estudo:** por que a redacao acontece tanto no JAR quanto no
Collector? Resposta: defesa em profundidade em lados diferentes da fronteira.

## 4. INFRA - armazenamento e observabilidade

**Onde ler:** `infra/README.md`, `infra/sql/`, `infra/HYPERDX_SETUP.md`.

INFRA possui a verdade persistida: `spark_events`, `plan_transitions`,
`findings` e rollups. ClickHouse responde por filtro e correlacao por
`job_id`; HyperDX e uma camada de visualizacao que precisa de fonte customizada
para tabelas APEX.

**Pergunta de estudo:** qual a diferenca entre `otel_traces` (forma do
exporter) e `spark_events` (forma de dominio APEX)?

## 5. ENGINE - diagnostico e revisao controlada

**Onde ler:** `engine/README.md`, `engine/src/apex_engine/watchers/`,
`engine/src/apex_engine/gate.py`, `engine/src/apex_engine/crew/`.

Tier 1 tem watchers deterministicos para skew, shuffle, memoria, custo,
codigo e sinais AQE. Tier 2 somente considera candidato validado com
`confidence_score < 0.6` e `severity >= critical`. O Judge pode rejeitar ou
recalibrar; nao pode trocar identidade e evidencia medidas.

**Pergunta de estudo:** por que uma transicao `coalesce` nao deve ser rotulada
como skew? Ela normalmente indica particionamento superdimensionado.

## 6. SERVE - interface MCP e aprovacao humana

**Onde ler:** `serve/README.md`, `serve/src/apex_mcp/`, `serve/.mcp.json`.

SERVE transforma consultas e findings em contratos Pydantic para clientes MCP.
Entradas do usuario entram em queries com binding. Texto de plano e finding e
nao confiavel; ele aparece em campos tipados e e neutralizado quando incluido
em prosa gerada. A sugestao devolve um diff, nao uma escrita.

**Pergunta de estudo:** por que stdout e restrito no servidor? Porque stdout e
o canal JSON-RPC; logs ali corromperiam a conversa MCP.

## Caminho de leitura em uma sessao

1. Leia DEV e execute mentalmente um `skew_join`.
2. Leia JAR e enumere os campos que saem no span.
3. Leia COLLECT e acompanhe a redacao ate `spark_events`.
4. Leia ENGINE e reproduza a regra que gera o finding.
5. Leia SERVE e siga o `job_id` em `analyze_run`.
6. Termine em [06-testes-e-evidencias.md](06-testes-e-evidencias.md).
