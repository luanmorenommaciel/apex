# Casos de erro replicáveis — por PR

Formato Duplo Diamante (Descobrir → Definir → Desenvolver → Entregar), como os
documentos `C4x`/`C5x` já usados no projeto. Cada caso traz o erro literal, o
comando exato para reproduzir, o diagnóstico e a correção — para qualquer
revisor (humano ou LLM) do lado do upstream reproduzir e confirmar por conta
própria, sem precisar confiar na minha palavra.

Todos os testes abaixo rodaram localmente, em worktrees descartáveis, sem
tocar no repositório remoto upstream.

---

## PR-1 — JAR: lifecycle + telemetria medida

### Caso 1.1 — `AqeDiffSpec.scala` não pertence a este PR (erro de escopo, não de produto)

**Descobrir:** ao copiar os 9 specs novos do fork para o upstream portado, um deles
falhou ao compilar.

**Erro literal:**
```
[error] /work/src/test/scala/apex/AqeDiffSpec.scala:8:8: method diff in object
  ApexAqeListener cannot be accessed as a member of object apex.ApexAqeListener
  from class AqeDiffSpec in package apex
[error]       .diff(
[error]        ^
[error] /work/src/test/scala/apex/AqeDiffSpec.scala:9:34: not enough arguments
  for method apply: (joins: List[String], reads: List[String],
  skewAccumIds: Set[Long], signature: String): apex.ApexAqeListener.PlanShape
  in object PlanShape.
[error] three errors found
```

**Definir:** o spec testa `ApexAqeListener`, arquivo que os dois lados reescreveram
de forma incompatível (ver Caso 2.1) — não faz parte do porte do listener/sink.

**Corrigido:** removido `AqeDiffSpec.scala` do escopo do PR-1; os outros 8 specs
seguem normalmente.

**Reproduzir:**
```bash
# a partir de uma copia do upstream com as 5 classes novas + Listener/Event do
# fork ja copiados, mas ApexAqeListener.scala do upstream intocado:
cp <fork>/jar/src/test/scala/apex/AqeDiffSpec.scala <upstream-portado>/jar/src/test/scala/apex/
sbt apex_41/compile
# esperado: os tres erros acima
```

### Caso 1.2 — porte principal, sem erro (controle positivo)

**Entregar:** compilação 4/4 células, suíte completa 29/29 testes (8 specs, sem
`AqeDiffSpec`) em cada uma das 4 células (`apex_35`, `apex_352_12`, `apex_40`,
`apex_41`). Inclui `StageLifecycleSpec` — `onJobEnd`, estado zerado após 12
shuffles reutilizados.

**Reproduzir:**
```bash
sbt "apex_35/compile; apex_352_12/compile; apex_40/compile; apex_41/compile"
sbt apex_41/test   # repetir para as outras 3 celulas
```

---

## PR-2 — porte inverso (`spark4JdkGate`)

Nenhum erro encontrado. Trivial, ~20 linhas, `build.sbt`. Sem caso a replicar.

---

## PR-3/PR-4 — camada de dados aditiva + engine

### Caso 3.1 — hipótese inicial de bloqueio, refutada por teste real

**Descobrir:** suposição inicial (não testada) de que `ALTER TABLE ... MODIFY
QUERY` poderia não funcionar no ClickHouse 24.8 do upstream.

**Definir:** testar de verdade, contra o DDL completo e real do upstream (não uma
tabela sintética).

**Desenvolver + Entregar:** 7/7 migrações (`022`-`028`) aplicaram sem erro,
**confirmado 2 vezes**, incluindo `ADD COLUMN` + `MODIFY QUERY` numa MV já
populada, com linha antiga preservada (`DEFAULT 0`) e linha nova com o campo
tipado corretamente populado.

**Reproduzir:**
```bash
docker run -d --name <nome-unico> \
  -e CLICKHOUSE_USER=apex -e CLICKHOUSE_PASSWORD=apex_local_dev -e CLICKHOUSE_DB=apex \
  -v <upstream>/infra/sql:/docker-entrypoint-initdb.d:ro \
  clickhouse/clickhouse-server:24.8
# esperar estabilizar (3 confirmacoes seguidas de SELECT count() FROM apex.spark_events)
# aplicar em sequencia: 022_..sql ate 028_..sql (copiados do fork)
# esperado: todas OK, sem excecao
```

### Caso 3.2 — MV não dispara no INSERT (achado real, NÃO RESOLVIDO)

**Descobrir:** ao tentar provar "dado antigo preservado" com uma linha semente
inserida manualmente em `apex.otel_traces`, `spark_events` continuou com 0
linhas.

**Definir/diagnosticar, eliminando hipóteses uma a uma:**
1. Schema do INSERT errado (colunas incompletas) → corrigido lendo
   `infra/sql/010_otel_traces.sql` real, coluna por coluna. **Não resolveu.**
2. Instabilidade do container (`Connection refused`, típico de boot pesado) →
   eliminada rodando com 3 confirmações estáveis seguidas antes de qualquer
   comando. **Não resolveu.**
3. A MV existe? `SHOW CREATE TABLE apex.mv_spark_events` → sim, definição
   idêntica ao SQL fonte.
4. A transformação está certa? Rodei o `SELECT` da MV **manualmente** contra
   `otel_traces` (fora do mecanismo de MV) → retornou a linha certa, todos os
   campos certos, incluindo `plan_fingerprint` como `FixedString(64)` vazio
   preenchido com bytes nulos.
5. **Conclusão: a transformação está correta; o gatilho automático de INSERT→MV
   não propaga, neste ambiente.** Causa raiz não identificada.

**Comando exato para reproduzir e ajudar a diagnosticar:**
```bash
# apos o container estavel (3x SELECT count() FROM apex.spark_events OK):
docker exec -i <container> clickhouse-client --user apex --password apex_local_dev --multiquery <<'SQL'
INSERT INTO apex.otel_traces
(Timestamp, TraceId, SpanId, ParentSpanId, TraceState, SpanName, SpanKind, ServiceName,
 ResourceAttributes, ScopeName, ScopeVersion, SpanAttributes, Duration, StatusCode, StatusMessage)
VALUES
(now64(9), 'trace-seed-1', 'span-seed-1', '', '', 'apex.stage', 'SPAN_KIND_INTERNAL', 'apex-jar',
 map(), 'apex', '1.0',
 map('job_id','job-seed','app_id','app-seed','app_name','seed','stage_id','1','stage_attempt','0',
     'ts','1700000000000','shuffle_read_bytes','100','shuffle_write_bytes','100',
     'spill_disk_bytes','0','spill_mem_bytes','0','gc_time_ms','10',
     'input_bytes','100','output_bytes','100','peak_execution_mem_bytes','1000',
     'task_count','4','task_duration_p50_ms','10','task_duration_p99_ms','20'),
 1000000, 'STATUS_CODE_UNSET', '');
SQL

# checar cada camada:
docker exec -i <container> clickhouse-client --user apex --password apex_local_dev \
  --query "SELECT count() FROM apex.otel_traces"                                    # esperado: 1
docker exec -i <container> clickhouse-client --user apex --password apex_local_dev \
  --query "SELECT count() FROM apex.spark_events"                                   # obtido: 0 (aqui esta o problema)
```

**Pedido explícito para o lado do upstream:** rodar este exato repro no ambiente de
vocês (Mac/Linux, ou Windows com Docker Desktop configurado diferente) e ver
se reproduz. Se **não** reproduzir do lado de vocês, é sinal de algo específico
deste ambiente Windows/Docker Desktop, não do produto. Se **reproduzir**, é
achado real que vale investigação conjunta.

---

## PR-6 — integridade de dado no Collector (`async_insert`)

### Caso 6.1 — ClickHouse 24.8 recusa a combinação usada em produção pelo fork

**Descobrir:** o Collector do fork usa
`async_insert=1&wait_for_async_insert=1&async_insert_deduplicate=1&deduplicate_blocks_in_dependent_materialized_views=1`.

**Erro literal, reproduzido no 24.8.14.39:**
```
Received exception from server (version 24.8.14):
Code: 210. DB::NetException: Connection refused (localhost:9000). (NETWORK_ERROR)
```
Repetido, e ao isolar melhor:
```
Code: 344. DB::Exception: Received from localhost:9000. DB::Exception:
Deduplication in dependent materialized view cannot work together with async
inserts. Please disable either `deduplicate_blocks_in_dependent_materialized_views`
or `async_insert` setting.. (SUPPORT_IS_DISABLED)
```

**Reproduzir:**
```bash
docker run -d --name <nome-unico> -e CLICKHOUSE_USER=apex -e CLICKHOUSE_PASSWORD=apex_local_dev \
  clickhouse/clickhouse-server:24.8
docker exec -i <nome-unico> clickhouse-client --user apex --password apex_local_dev --multiquery <<'SQL'
CREATE DATABASE t; USE t;
CREATE TABLE src (k String, payload String) ENGINE=MergeTree ORDER BY k
  SETTINGS non_replicated_deduplication_window=100;
CREATE TABLE tgt AS src SETTINGS non_replicated_deduplication_window=100;
CREATE MATERIALIZED VIEW mv TO tgt AS SELECT * FROM src;
INSERT INTO src SETTINGS async_insert=1, wait_for_async_insert=1,
  async_insert_deduplicate=1, deduplicate_blocks_in_dependent_materialized_views=1
  VALUES ('k','v');
SQL
# esperado: Code 344 SUPPORT_IS_DISABLED
```

### Caso 6.2 — correção: inserts síncronos funcionam, e são mais rápidos

**Desenvolver:** trocar `async_insert=1` por `async_insert=0` (mesmos outros
settings).

**Entregar:**
```
async_insert=0 + dedup_mv=1 + janela 100/100  ->  1/1  (identico ao 26.1)
Throughput, 60 inserts de 3 linhas:
  async_insert=1 (config atual do upstream)   6432 ms
  async_insert=0 (proposta)               2912 ms   -> 2,2x mais rapido
```

**Reproduzir:** mesmo setup do Caso 6.1, trocando `async_insert=1` por
`async_insert=0` no `INSERT`. Esperado: sucesso, `1/1` em `src`/`tgt`.

### Caso 6.3 — erro do MEU teste, não do produto (timestamp gerado a cada chamada)

**Descobrir:** primeira tentativa de validar retry deu `2/2` (falha) mesmo com
`async_insert=0` + dedup.

**Diagnóstico:** o teste usava `now()` a cada `INSERT`, gerando blocos com bytes
diferentes a cada tentativa — o ClickHouse deduplica por **hash do bloco
inteiro**, então blocos diferentes nunca são reconhecidos como duplicata. Isso
não reflete o pipeline real: verificado em
`jar/src/main/scala/apex/ApexStageListener.scala:194`, o campo `ts` é atribuído
**uma única vez**, no fim do stage — o Collector nunca gera novo timestamp ao
reenviar.

**Correção do teste:** usar timestamp **fixo** nos dois inserts (simulando
retry real = mesmos bytes reenviados). Resultado após a correção: `1/1`,
correto.

**Reproduzir (mostra o padrão errado E o certo):**
```sql
-- ERRADO (usa now(), nao reflete retry real):
INSERT INTO src SETTINGS async_insert=0, deduplicate_blocks_in_dependent_materialized_views=1
  VALUES ('k', now(), 'v');
INSERT INTO src SETTINGS async_insert=0, deduplicate_blocks_in_dependent_materialized_views=1
  VALUES ('k', now(), 'v');
-- resultado: 2 linhas (nao deduplicou -- CORRETO para este input, ja que
-- os blocos sao de fato diferentes; o erro estava em usar isto como teste
-- de "retry", nao no ClickHouse)

-- CERTO (timestamp fixo, simula retry real de rede):
INSERT INTO src SETTINGS async_insert=0, deduplicate_blocks_in_dependent_materialized_views=1
  VALUES ('k', '2026-08-06 10:00:00', 'v');
INSERT INTO src SETTINGS async_insert=0, deduplicate_blocks_in_dependent_materialized_views=1
  VALUES ('k', '2026-08-06 10:00:00', 'v');
-- resultado: 1 linha (dedup funcionou)
```

### Caso 6.4 — limite real do mecanismo (não é bug, é característica)

**Descobrir:** lote de 6 linhas (5 repetidas de um lote anterior de 5 + 1 nova)
resultou em 11 linhas na fonte, não 6.

**Diagnóstico:** dedup do ClickHouse é por **hash de bloco exato**. Um bloco
diferente (6 linhas) do bloco anterior (5 linhas) nunca é reconhecido como
"parcialmente duplicata" — insere tudo.

**Isto NÃO invalida o Caso 6.2.** A `sending_queue`/`retry_on_failure` do OTel
Collector, pela arquitetura documentada do projeto, reenvia o **item de fila
exato** que falhou — nunca mescla com dado novo chegado depois. Este cenário
de bloco parcialmente sobreposto não corresponde a retry automático real; é
mais parecido com replay/backfill manual, que precisaria de cuidado adicional
(não coberto por este mecanismo).

**Reproduzir:**
```sql
INSERT INTO src SETTINGS async_insert=0, deduplicate_blocks_in_dependent_materialized_views=1
  VALUES ('a','2026-08-06 10:00:00','1'),('b','2026-08-06 10:00:00','2'),
         ('c','2026-08-06 10:00:00','3'),('d','2026-08-06 10:00:00','4'),
         ('e','2026-08-06 10:00:00','5');
INSERT INTO src SETTINGS async_insert=0, deduplicate_blocks_in_dependent_materialized_views=1
  VALUES ('a','2026-08-06 10:00:00','1'),('b','2026-08-06 10:00:00','2'),
         ('c','2026-08-06 10:00:00','3'),('d','2026-08-06 10:00:00','4'),
         ('e','2026-08-06 10:00:00','5'),('f','2026-08-06 10:00:00','6');
-- resultado: 11 linhas (5 duplicadas + 1 nova), esperado apenas se alguem
-- reenviar um lote diferente do que falhou -- nao e o caso do Collector real
```

### Caso 6.5 — concorrência real (10 clientes simultâneos)

**Entregar:** 10 processos concorrentes, cada um com insert + retry idêntico →
10 linhas, 10 jobs distintos, zero duplicata. Mais rápido que sequencial
(14001ms vs 20739ms para a mesma carga).

**Reproduzir:** disparar N processos `docker exec ... clickhouse-client`
simultâneos (`&` + `wait` em bash), cada um inserindo lote + retry idêntico
com timestamp fixo; verificar contagem final = N.

---

## Candidato `ApexAqeListener` (decisão de design, não PR fechado)

### Caso D.1 — os dois lados resolveram problemas diferentes de forma incompatível

**Descobrir:** o upstream tem contagem real de partições skewed
(`SparkListenerDriverAccumUpdates`); o fork tem alinhamento por distância de
edição (`joinReplacements`) que corrige bug de desalinhamento posicional do
upstream. Nenhum dos dois tem as duas coisas.

**Bug do upstream, isolável e replicável:**
```scala
// comparacao POSICIONAL simples:
val n = math.min(prev.joins.size, cur.joins.size)
// se um join for inserido/removido, TODOS os seguintes sao desalinhados
```
Teste que expõe (já no `AqeDiffSpec.scala` original do fork):
```scala
val before = List("SortMergeJoin", "BroadcastHashJoin")
val after = List("BroadcastHashJoin", "SortMergeJoin", "BroadcastHashJoin")
// com a comparacao posicional do upstream: reporta troca de estrategia por engano
// com o alinhamento por edicao do fork: switches.isEmpty (correto)
```

**Desenvolver:** candidato combinando os dois mecanismos, escrito em
`apex-upstream-clickhouse-test/jar/src/main/scala/apex/ApexAqeListener.scala`.

**Entregar:** 34/34 testes, incluindo 2 novos que isolam especificamente a
interação dos dois mecanismos:
```scala
test("a new skewed read reports only the accumulator ids this re-plan introduced") { ... }
test("join alignment and skew accumulator tracking do not interfere with each other") { ... }
```

**Status:** `CANDIDATO_NAO_APLICADO` — decisão de qual direção seguir
(skew do upstream / alinhamento do fork / combinado) é do time, não técnica.

---

## PR-7 — guard-rail de ambiente limpo

Ver documento dedicado `PR7-CLEAN-PILOT-GUARDRAIL.md` — já traz caso de erro
real (o incidente que motivou o PR), reprodução testada ao vivo (`-DryRun` e
recusa real, hoje), e evidência histórica (`evidence/clean-pilot-refusal-2026-07-25.log`).

---

## Resumo — o que pode ser verificado sem confiar em mim

```
Caso 1.1   reproduz erro de compilacao real, isolado
Caso 3.1   reproduz 7/7 migracoes OK contra DDL real
Caso 3.2   reproduz o mistério da MV -- ABERTO, pedido explicito de ajuda
Caso 6.1   reproduz o erro Code 344 no 24.8
Caso 6.2   reproduz a correcao (sincrono funciona, mais rapido)
Caso 6.3   mostra o padrao de teste ERRADO e o CERTO, lado a lado
Caso 6.4   reproduz o limite real (nao e bug, e caracteristica do mecanismo)
Caso 6.5   reproduz concorrencia real
Caso D.1   reproduz o bug de alinhamento posicional do upstream, isolado
```
