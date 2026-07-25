# Fase 7 - Decisoes por raia e visao global

Este mapa complementa o fluxo e a sequencia: cada losango mostra quem toma a
decisao, qual dado e usado e para onde o caso segue. Nenhuma decisao humana e
substituida por um modelo.

## 1. DEV - executar uma patologia?

```mermaid
flowchart TD
  A[Operador inicia e2e_canonical] --> B{Dados Delta ja materializados?}
  B -- nao --> C[Gerar fact e dimension\nS3A Delta]
  B -- sim --> D[Selecionar job patologico]
  C --> D
  D --> E{Spark e plugin configurados?}
  E -- nao --> F[Parar: corrigir bootstrap/config]
  E -- sim --> G[spark-submit\njob_id novo]
  G --> H[Entregar job_id e configuracao\nao JAR]
```

## 2. JAR - emitir ou degradar com seguranca?

```mermaid
flowchart TD
  A[Callback Spark\nTaskMetrics ou AQE] --> B[Agregar por stage\ne redigir atributos]
  B --> C{Fila OTel aceita evento?}
  C -- sim --> D[Emitir apex.stage ou\napex.plan_transition via OTLP/HTTP]
  C -- nao / collector indisponivel --> E[Registrar falha isolada\ne manter job Spark vivo]
  D --> F[Payload: job_id, stage_id,\nmetricas, fingerprint/AQE]
  E --> G[Resultado degradado\nsem derrubar o driver]
```

## 3. COLLECT - aceitar e sanitizar?

```mermaid
flowchart TD
  A[Span OTLP recebido] --> B{Dentro do limite de memoria?}
  B -- nao --> C[Backpressure e fila file_storage]
  B -- sim --> D[Transform/redaction]
  C --> D
  D --> E{Contem PII ou atributo bloqueado?}
  E -- sim --> F[Remover ou mascarar/HMAC]
  E -- nao --> G[Preservar somente campos do contrato]
  F --> H[Exportar batch para ClickHouse]
  G --> H
  H --> I[Payload: span OTLP sanitizado\ncom job_id]
```

## 4. INFRA - persistir e tornar consultavel?

```mermaid
flowchart TD
  A[Insert OTLP sanitizado] --> B{Schema v0.2 aplicado?}
  B -- nao --> C[Parar a operacao\nexecutar migracao aditiva]
  B -- sim --> D[otel_traces]
  D --> E[Materialized Views]
  E --> F{Tipo de span?}
  F -- apex.stage --> G[spark_events]
  F -- apex.plan_transition --> H[plan_transitions]
  G --> I[Consulta indexada por job_id]
  H --> I
  I --> J[Entregar eventos e AQE\na ENGINE/SERVE]
```

## 5. ENGINE - publicar, escalar ou rejeitar?

```mermaid
flowchart TD
  A[Eventos e AQE por job_id] --> B[Watchers deterministicos]
  B --> C[EvidenceValidator]
  C --> D{Evidencia valida?}
  D -- nao --> E[Rejeitar finding\nregistrar motivo]
  D -- sim --> F{confidence < 0.6\ne severity critical/blocker?}
  F -- nao --> G[Persistir finding Tier 1]
  F -- sim --> H{Crew/Judge configurado?}
  H -- nao/falha --> I[Preservar finding Tier 1\nsem bloquear o fluxo]
  H -- sim --> J[Correlator e Judge\nrevisam somente evidencia existente]
  J --> K{Judge aceita?}
  K -- nao --> E
  K -- sim --> L[Revalidar e persistir veredito]
  G --> M[Payload: finding tipado\npor job_id]
  I --> M
  L --> M
```

## 6. SERVE - informar ou propor?

```mermaid
flowchart TD
  A[Cliente MCP envia job_id] --> B{Ferramenta solicitada}
  B -- analyze/compare/search --> C[SELECT parametrizado\nno ClickHouse]
  C --> D[Retornar modelo Pydantic\nJSON-RPC stdio]
  B -- suggest_fix --> E[Gerar receita e diff\na partir de finding validado]
  E --> F{Confianca >= limiar?}
  F -- nao --> G[Retornar advisory\nsem proposta forte]
  F -- sim --> H[Retornar proposta\napplied=false]
  H --> I[Engenheiro revisa fora do MCP]
  I --> J{Aprova mudanca?}
  J -- nao --> K[Arquivar/ajustar proposta]
  J -- sim --> L[Mutacao ocorre em fluxo\nexterno e auditavel]
```

## Decisao global - da telemetria a uma correcao humana

```mermaid
flowchart LR
  D[DEV\njob + job_id] -->|spark-submit e configuracao| J[JAR\nmetricas/AQE]
  J -->|OTLP/HTTP\nspan sanitizado| C[COLLECT\nredacao/backpressure]
  C -->|batch OTLP\nsem PII| I[INFRA\nClickHouse]
  I -->|SELECT parametrizado\neventos por job_id| E[ENGINE\nwatchers + validator]
  E -->|finding tipado\ne evidencia citada| S[SERVE\nMCP]
  S -->|JSON-RPC\ndiagnostico ou diff| H[Humano\nCommander/engenheiro]
  H -->|aprovacao externa\ncom auditoria| R[Repositorio/job corrigido]
  H -->|recusa ou evid. insuficiente| A[Sem mutacao\nregistrar decisao]

  classDef data fill:#dbeafe,stroke:#2563eb,color:#111827
  classDef decision fill:#fef3c7,stroke:#d97706,color:#111827
  classDef human fill:#dcfce7,stroke:#16a34a,color:#111827
  class D,J,C,I,E,S data
  class H,R,A human
```

## Regra de leitura

O `job_id` e a chave entre todas as raias. Os dados fluem automaticamente ate
o MCP; a decisao que muda codigo ou uma execucao fica deliberadamente fora do
servidor MCP e exige uma pessoa responsavel.
