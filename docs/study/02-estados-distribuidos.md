# Fase 2 - Estados distribuidos

Nao existe uma unica maquina de estados central. O estado muda em cada raia,
e uma transicao so e aceita quando a proxima camada recebeu o dado esperado.

```mermaid
stateDiagram-v2
    state "Spark: DEV/JAR" as Spark {
      [*] --> Preparado
      Preparado --> Executando: spark-submit + plugin
      Executando --> Capturando: TaskMetrics / AQE update
      Capturando --> Emitindo: span OTLP em fila limitada
      Emitindo --> Concluido: forceFlush no shutdown
      Capturando --> Degradado: collector indisponivel\nfalha isolada
    }
    state "COLLECT" as Collect {
      [*] --> Recebendo
      Recebendo --> Sanitizando: memory_limiter + transform
      Sanitizando --> Exportando: ClickHouse exporter
      Exportando --> Enfileirado: retry + file_storage
    }
    state "INFRA" as Infra {
      [*] --> PersistidoOTel
      PersistidoOTel --> Materializado: MV por SpanName
      Materializado --> Consultavel: job_id indexado
    }
    state "ENGINE/SERVE/Humano" as Service {
      [*] --> Analisando
      Analisando --> FindingValidado: watcher + validator
      FindingValidado --> RevisaoOpcional: LOW e critical/blocker
      RevisaoOpcional --> Proposta: Judge aceita/rejeita
      FindingValidado --> Proposta: MCP sugestao
      Proposta --> Aprovada: decisao humana
      Proposta --> Arquivada: humano recusa
    }
    Spark.Emitindo --> Collect.Recebendo: OTLP/HTTP
    Collect.Exportando --> Infra.PersistidoOTel: insert batelado
    Infra.Consultavel --> Service.Analisando: SELECT parametrizado
```

## Estados que merecem atencao

| Estado | Dono | Entrada | Saida | Falha segura |
|---|---|---|---|---|
| `Capturando` | JAR | callbacks Spark | metricas agregadas por estagio | excecoes sao recuperadas; listener nao derruba job |
| `Emitindo` | JAR | evento sanitizado | span OTLP | fila limitada descarta antes de bloquear driver |
| `Sanitizando` | COLLECT | atributos OTLP | atributos removidos/mascarados | memoria limitada e retry controlado |
| `Materializado` | INFRA | `otel_traces` | tabelas de contrato | MV separa eventos e transicoes |
| `FindingValidado` | ENGINE | evento e regra | finding tipado | sem LLM no caminho deterministico |
| `RevisaoOpcional` | Crew/Judge | candidato validado | veredito com citacoes | falha do provider preserva Tier 1 |
| `Proposta` | SERVE | finding persistido | diff e PR body como dados | nao escreve disco, Git ou Spark |

## Transicoes intencionalmente proibidas

- JAR nao consulta ClickHouse nem decide correcao.
- Collector nao interpreta causa raiz; ele transporta e sanitiza.
- Crew/Judge nao cria finding sem evidencia Tier 1.
- MCP nao aplica codigo automaticamente.
- Nenhuma camada recebe segredo dentro de um span, finding ou resposta MCP.
