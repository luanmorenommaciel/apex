# Apex CLI API Documentation

> **Versao:** `0.1.0-alpha`  
> **Repositorio:** `luanmorenommaciel/apex`  
> **Branch:** `gustocezar/feature/kimi-desacoplamento-geradores`  

---

## 1. Visao Geral

O projeto **Apex** fornece 7 binarios CLI independentes para diagnostico, validacao, recomendacao e analise de jobs Spark, alem de dois servidores (MCP e CREI) para integracao.

| CLI | Descricao | Entrada | Saida |
|---|---|---|---|
| `diagnose` | Executa diagnostico T1 de anomalias em um job Spark | `app_id` | JSON com findings |
| `validate` | Valida evidencias de eventos contra um cenario YAML | `scenario`, `log` | JSON com status de validacao |
| `recommend` | Gera recomendacoes de correcao a partir de anomalias | `app_id`, `runbooks` | JSON com recomendacoes |
| `analyze` | Pipeline completo: diagnose -> recomendacoes -> revisao automatica | `app_id`, `output` | JSON com resultado de analise |
| `spillwatch` | Monitora spill-to-disk de um job Spark especifico | `app_id` | JSON com deteccao de spill |
| `mcp-server` | Servidor MCP (stdio) para consultas de job e recomendacoes | JSON-RPC via stdin | JSON-RPC via stdout |
| `crei-server` | Servidor HTTP CREI para analise de jobs via API REST | HTTP POST/GET | JSON com analise |

---

## 2. Documentacao por CLI

### 2.1 `diagnose`

Executa o pipeline de diagnostico T1 para detectar anomalias (skew, spill, GC pressure, OOM) em um job Spark consultando o ClickHouse.

#### Flags

| Flag | Tipo | Padrao | Obrigatorio | Descricao |
|---|---|---|---|---|
| `-app-id` | `string` | `""` | **Sim** | Spark application ID a ser analisado |

#### Exemplo de Uso

```bash
./diagnose -app-id=application_1234567890_0001
```

#### Saida Esperada (JSON)

```json
{
  "app_id": "application_1234567890_0001",
  "findings": [
    {
      "app_id": "application_1234567890_0001",
      "anomaly_type": "SKEW",
      "severity": "HIGH",
      "description": "Stage 5 has skew ratio 29.5x",
      "evidence": {"stage_id": 5, "skew_ratio": 29.5},
      "affected_stages": [5],
      "confidence": 0.92
    }
  ]
}
```

#### Codigo de Saida

| Codigo | Significado |
|---|---|
| `0` | Sucesso -- diagnostico concluido com ou sem anomalias |
| `1` | Erro -- `app-id` nao fornecido, falha na conexao com ClickHouse, ou erro no diagnostico |

---

### 2.2 `validate`

Valida evidencias de eventos Spark (formato NDJSON) contra um cenario estruturado (YAML). Aplica regras de proveniencia, schema, correlacao de operador, distribuicao e estrutura.

#### Flags

| Flag | Tipo | Padrao | Obrigatorio | Descricao |
|---|---|---|---|---|
| `-scenario` | `string` | `""` | **Sim** | Caminho para o arquivo de cenario YAML |
| `-log` | `string` | `""` | **Sim** | Caminho para o arquivo de log de eventos (NDJSON) ou diretorio |

#### Exemplo de Uso

```bash
./validate -scenario=scenarios/skew_join.yaml -log=events/app_123.ndjson
```

#### Saida Esperada (JSON)

```json
{
  "status": "valid",
  "quality_issues": [],
  "correlation_method": "operator_accumulator",
  "stage_id": 5,
  "records": [1000000, 50000, 25000],
  "metrics": {"median_records": 50000.0, "median_duration_ms": 1200.0},
  "provenance_hash": "abc123def456"
}
```

**Status possiveis:** `valid`, `invalid`, `indeterminate`

#### Codigo de Saida

| Codigo | Significado |
|---|---|
| `0` | Sucesso -- validacao concluida (mesmo que status seja `invalid` ou `indeterminate`) |
| `1` | Erro -- falha ao ler `scenario` ou `log`, ou erro de marshaling |

---

### 2.3 `recommend`

Gera recomendacoes de correcao para anomalias detectadas em um job Spark. Usa runbooks locais como fonte primaria; faz fallback para LLM (OpenAI) quando nao ha runbook.

#### Flags

| Flag | Tipo | Padrao | Obrigatorio | Descricao |
|---|---|---|---|---|
| `-app-id` | `string` | `""` | **Sim** | Spark application ID a ser analisado |
| `-runbooks` | `string` | `"runbooks"` | Nao | Diretorio contendo os runbooks YAML |

#### Exemplo de Uso

```bash
./recommend -app-id=application_1234567890_0001 -runbooks=./runbooks
```

#### Saida Esperada (JSON)

```json
{
  "app_id": "application_1234567890_0001",
  "anomalies": [
    {
      "app_id": "application_1234567890_0001",
      "anomaly_type": "SKEW",
      "severity": "HIGH",
      "description": "Stage 5 has skew ratio 29.5x",
      "evidence": {"stage_id": 5},
      "affected_stages": [5],
      "confidence": 0.92
    }
  ],
  "recommendations": [
    {
      "anomaly_type": "SKEW",
      "confidence": 0.874,
      "summary": "Apply salting with 10 buckets to stage 5",
      "steps": [{"action": "salting", "details": "Add 10 buckets to the join key"}],
      "code_fix": "df.repartition(10, 'key').join(...)",
      "expected_impact": "Speedup 15x",
      "runbook_id": "SKEW_fix"
    }
  ]
}
```

#### Codigo de Saida

| Codigo | Significado |
|---|---|
| `0` | Sucesso -- recomendacoes geradas (mesmo que lista esteja vazia) |
| `1` | Erro -- `app-id` nao fornecido, falha na conexao com ClickHouse, ou erro no diagnostico |

---

### 2.4 `analyze`

Pipeline completo de analise: executa diagnose -> gera recomendacoes -> aplica revisao automatica das recomendacoes. E a CLI de maior cobertura, combinando as funcionalidades de `diagnose`, `recommend` e validacao heuristica.

#### Flags

| Flag | Tipo | Padrao | Obrigatorio | Descricao |
|---|---|---|---|---|
| `-app-id` | `string` | `""` | **Sim** | Spark application ID a ser analisado |
| `-output` | `string` | `""` | Nao | Caminho do arquivo de saida para o resultado JSON (opcional) |

#### Exemplo de Uso

```bash
./analyze -app-id=application_1234567890_0001 -output=result.json
```

#### Saida Esperada (JSON) -- Status HEALTHY

```json
{
  "app_id": "application_1234567890_0001",
  "status": "HEALTHY",
  "message": "Nenhuma anomalia detectada. Job dentro dos parametros normais."
}
```

#### Saida Esperada (JSON) -- Status ACTIONABLE

```json
{
  "app_id": "application_1234567890_0001",
  "status": "ACTIONABLE",
  "anomalies": [
    {
      "app_id": "application_1234567890_0001",
      "anomaly_type": "SKEW",
      "severity": "HIGH",
      "description": "Stage 5 has skew ratio 29.5x",
      "evidence": {"stage_id": 5},
      "affected_stages": [5],
      "confidence": 0.92
    }
  ],
  "recommendations": [
    {
      "anomaly_type": "SKEW",
      "confidence": 0.874,
      "summary": "Apply salting with 10 buckets to stage 5",
      "steps": [{"action": "salting", "details": "Add 10 buckets"}],
      "code_fix": "df.repartition(10, 'key').join(...)",
      "expected_impact": "Speedup 15x",
      "runbook_id": "SKEW_fix"
    }
  ],
  "reviews": [
    {
      "anomaly_type": "SKEW",
      "recommendation_summary": "Apply salting with 10 buckets to stage 5",
      "review": {
        "passed": true,
        "issues": [],
        "confidence": 0.874,
        "severity": "HIGH"
      }
    }
  ]
}
```

#### Saida Esperada (JSON) -- Status NEEDS_ATTENTION

```json
{
  "app_id": "application_1234567890_0001",
  "status": "NEEDS_ATTENTION",
  "anomalies": [...],
  "recommendations": [...],
  "reviews": [
    {
      "anomaly_type": "OOM",
      "recommendation_summary": "Increase executor memory",
      "review": {
        "passed": false,
        "issues": [
          "Anomalia CRITICAL sem code_fix sugerido.",
          "Confianca da recomendacao muito baixa (< 0.4)."
        ],
        "confidence": 0.3,
        "severity": "CRITICAL"
      }
    }
  ]
}
```

#### Codigo de Saida

| Codigo | Significado |
|---|---|
| `0` | Sucesso -- status `HEALTHY` ou `ACTIONABLE` |
| `1` | Erro -- status `NEEDS_ATTENTION`, ou erro de execucao (conexao, diagnostico, I/O) |

---

### 2.5 `spillwatch`

Monitora spill-to-disk de um job Spark consultando metricas de tasks no ClickHouse. Detecta quando o shuffle read/write excede o threshold de 100 MB.

#### Flags

| Flag | Tipo | Padrao | Obrigatorio | Descricao |
|---|---|---|---|---|
| `-app-id` | `string` | `""` | **Sim** | Spark application ID a ser monitorado |

#### Exemplo de Uso

```bash
./spillwatch -app-id=application_1234567890_0001
```

#### Saida Esperada (JSON) -- Sem Spill

```json
{
  "status": "OK",
  "job_id": "application_1234567890_0001",
  "threshold_mb": 100.0,
  "spills_count": 0,
  "total_spill_mb": 0.0,
  "spills": [],
  "recommendations": [
    "Verificar spark.executor.memory e memory.fraction",
    "Aumentar spark.memory.fraction para 0.8 se executor tiver > 8GB",
    "Considerar broadcast join para datasets < 10MB",
    "Monitorar 'spill (memory)' no Spark UI"
  ],
  "message": "Nenhum spill detectado."
}
```

#### Saida Esperada (JSON) -- Com Spill

```json
{
  "status": "SPILL_DETECTED",
  "job_id": "application_1234567890_0001",
  "threshold_mb": 100.0,
  "spills_count": 3,
  "total_spill_mb": 450.5,
  "spills": [
    {
      "stage_id": 5,
      "task_id": 42,
      "spill_bytes": 157286400,
      "spill_mb": 150.0,
      "spill_memory_bytes": 104857600,
      "spill_disk_bytes": 52428800,
      "peak_memory": 2147483648,
      "run_time_ms": 120000,
      "severity": "HIGH"
    }
  ],
  "recommendations": [
    "Verificar spark.executor.memory e memory.fraction",
    "Aumentar spark.memory.fraction para 0.8 se executor tiver > 8GB"
  ]
}
```

#### Codigo de Saida

| Codigo | Significado |
|---|---|
| `0` | Sucesso -- analise de spill concluida |
| `1` | Erro -- `app-id` nao fornecido, falha na conexao com ClickHouse, ou erro na query |

---

### 2.6 `mcp-server`

Servidor MCP (Model Context Protocol) usando transporte stdio. Recebe requisicoes JSON-RPC 2.0 via `stdin` e responde via `stdout`. Expoe tres metodos: `query_job`, `get_recommendations` e `health_check`.

#### Flags

> O `mcp-server` nao aceita flags via linha de comando. Toda configuracao e via variaveis de ambiente.

#### Variaveis de Ambiente

| Variavel | Padrao | Descricao |
|---|---|---|
| `CLICKHOUSE_URL` | `http://localhost:8123` | URL do ClickHouse |
| `CREI_URL` | `http://localhost:8000` | URL do servidor CREI |

#### Exemplo de Uso

```bash
export CLICKHOUSE_URL=http://clickhouse:8123
./mcp-server
```

#### Requisicao JSON-RPC -- `query_job`

```json
{"jsonrpc":"2.0","id":1,"method":"query_job","params":{"app_id":"application_1234567890_0001"}}
```

#### Resposta JSON-RPC -- `query_job`

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "{\n  \"app_id\": \"application_1234567890_0001\",\n  \"found\": true,\n  \"total_events\": 1500,\n  \"stages\": [...],\n  \"tasks\": [...],\n  \"metrics_summary\": [...]\n}"
}
```

#### Requisicao JSON-RPC -- `get_recommendations`

```json
{"jsonrpc":"2.0","id":2,"method":"get_recommendations","params":{"app_id":"application_1234567890_0001"}}
```

#### Resposta JSON-RPC -- `get_recommendations`

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": "{\n  \"app_id\": \"application_1234567890_0001\",\n  \"recommendations\": [...],\n  \"confidence\": 0.85\n}"
}
```

#### Requisicao JSON-RPC -- `health_check`

```json
{"jsonrpc":"2.0","id":3,"method":"health_check"}
```

#### Resposta JSON-RPC -- `health_check`

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": "{\n  \"mcp_version\": \"0.1.0-alpha\",\n  \"mcp_status\": \"healthy\",\n  \"clickhouse_url\": \"http://localhost:8123\",\n  \"clickhouse_status\": \"connected\",\n  \"crei_url\": \"http://localhost:8000\",\n  \"crei_status\": \"not implemented\"\n}"
}
```

#### Erro JSON-RPC

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "error": {
    "code": -32600,
    "message": "app_id is required"
  }
}
```

#### Codigo de Saida

| Codigo | Significado |
|---|---|
| `0` | Servidor encerrado normalmente (EOF no stdin) |
| `1` | Erro de scanner no stdin |

---

### 2.7 `crei-server`

Servidor HTTP REST para analise de jobs Spark. Expoe endpoints para health check, version e analise completa.

#### Flags

> O `crei-server` nao aceita flags via linha de comando. A porta e configurada via variavel de ambiente.

#### Variaveis de Ambiente

| Variavel | Padrao | Descricao |
|---|---|---|
| `CREI_PORT` | `8000` | Porta TCP onde o servidor escuta |

#### Endpoints

| Metodo | Endpoint | Descricao |
|---|---|---|
| `GET` | `/health` | Health check do servidor |
| `GET` | `/version` | Versao do CREI server |
| `POST` | `/analyze` | Executa analise completa de um job |

#### Exemplo de Uso

```bash
export CREI_PORT=8000
./crei-server
```

#### Requisicao -- `POST /analyze`

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "application_1234567890_0001",
    "job_data": {},
    "request_type": "full"
  }'
```

#### Resposta -- `POST /analyze`

```json
{
  "app_id": "application_1234567890_0001",
  "diagnosis": "Stage 5 has skew ratio 29.5x | Spill detectado em stage 3",
  "root_cause": ["SKEW", "SPILL"],
  "recommendations": [
    "Apply salting with 10 buckets to stage 5",
    "Verificar spark.executor.memory e memory.fraction"
  ],
  "runbook": {
    "steps": ["Identificar stage hot", "Aplicar salting", "Re-executar job"],
    "code_fix": "df.repartition(10, 'key').join(...)",
    "validation": "Verificar skew ratio < 2.0 apos correcao"
  },
  "confidence": 0.85,
  "job_data_summary": {
    "anomalies_count": 2,
    "recommendations_count": 2
  }
}
```

#### Resposta -- `GET /health`

```json
{
  "status": "healthy",
  "version": "0.1.0-alpha"
}
```

#### Resposta -- `GET /version`

```json
{
  "version": "0.1.0-alpha"
}
```

#### Codigos HTTP

| Codigo | Significado |
|---|---|
| `200` | Sucesso -- analise concluida |
| `400` | Bad Request -- `app_id` nao fornecido ou JSON invalido |
| `405` | Method Not Allowed -- metodo HTTP nao suportado |
| `500` | Internal Server Error -- erro no diagnostician ou conexao com ClickHouse |

---

## 3. Tabela Comparativa dos CLIs

| Aspecto | `diagnose` | `validate` | `recommend` | `analyze` | `spillwatch` | `mcp-server` | `crei-server` |
|---|---|---|---|---|---|---|---|
| **Tipo** | CLI batch | CLI batch | CLI batch | CLI batch | CLI batch | Servidor stdio | Servidor HTTP |
| **Entrada obrigatoria** | `app-id` | `scenario`, `log` | `app-id` | `app-id` | `app-id` | JSON-RPC | HTTP POST |
| **Entrada opcional** | -- | -- | `runbooks` | `output` | -- | -- | -- |
| **Saida** | JSON | JSON | JSON | JSON | JSON | JSON-RPC | JSON |
| **Conecta ao ClickHouse** | Sim | Nao | Sim | Sim | Sim | Sim | Sim |
| **Usa runbooks** | Nao | Nao | Sim | Sim | Nao | Indireto | Sim |
| **Revisa recomendacoes** | Nao | Nao | Nao | Sim | Nao | Nao | Nao |
| **Codigo de saida** | 0 / 1 | 0 / 1 | 0 / 1 | 0 / 1 | 0 / 1 | 0 / 1 | HTTP 200/400/500 |
| **Cobertura do pipeline** | T1 (diagnose) | Validacao | T2 (recommend) | T1->T2->Revisao | Spill only | T1+T2 | T1+T2 |

---

## 4. Exemplos Praticos de Pipeline

### 4.1 Pipeline Completo: Diagnose -> Validate -> Recommend -> Analyze

```bash
#!/bin/bash
set -e

APP_ID="application_1234567890_0001"
SCENARIO="scenarios/skew_join.yaml"
LOG="events/app_123.ndjson"
RUNBOOKS="./runbooks"
OUTPUT="analysis_result.json"

echo "=== Stage 1: Diagnose ==="
./diagnose -app-id="$APP_ID"

echo "=== Stage 2: Validate Evidence ==="
./validate -scenario="$SCENARIO" -log="$LOG"

echo "=== Stage 3: Recommend ==="
./recommend -app-id="$APP_ID" -runbooks="$RUNBOOKS"

echo "=== Stage 4: Full Analysis ==="
./analyze -app-id="$APP_ID" -output="$OUTPUT"

echo "=== Pipeline completo. Resultado em $OUTPUT ==="
```

### 4.2 Pipeline com Validacao de Evidencias

```bash
#!/bin/bash

SCENARIO="scenarios/broadcast_join.yaml"
LOG="events/broadcast_test.ndjson"
APP_ID="application_9876543210_0001"

VALIDATION=$(./validate -scenario="$SCENARIO" -log="$LOG")
STATUS=$(echo "$VALIDATION" | jq -r '.status')

if [ "$STATUS" = "valid" ]; then
    echo "Evidencias validas. Prosseguindo com analise..."
    ./analyze -app-id="$APP_ID" -output=result.json
elif [ "$STATUS" = "indeterminate" ]; then
    echo "Evidencias indeterminadas. Analise com cautela."
    ./diagnose -app-id="$APP_ID"
else
    echo "Evidencias invalidas. Abortando."
    echo "$VALIDATION" | jq '.quality_issues'
    exit 1
fi
```

### 4.3 Pipeline de Monitoramento Continuo (Spill)

```bash
#!/bin/bash

APP_ID="application_1234567890_0001"
THRESHOLD_SPILLS=5

RESULT=$(./spillwatch -app-id="$APP_ID")
SPILL_COUNT=$(echo "$RESULT" | jq -r '.spills_count')

if [ "$SPILL_COUNT" -ge "$THRESHOLD_SPILLS" ]; then
    echo "ALERTA: $SPILL_COUNT spills detectados! Executando analise completa..."
    ./analyze -app-id="$APP_ID" -output=alert_$(date +%s).json
else
    echo "OK: $SPILL_COUNT spills (threshold: $THRESHOLD_SPILLS)"
fi
```

### 4.4 Pipeline com MCP Server

```bash
#!/bin/bash

./mcp-server &
MCP_PID=$!
sleep 1

APP_ID="application_1234567890_0001"
echo '{"jsonrpc":"2.0","id":1,"method":"query_job","params":{"app_id":"'$APP_ID'"}}' | ./mcp-server

echo '{"jsonrpc":"2.0","id":2,"method":"health_check"}' | ./mcp-server

kill $MCP_PID
```

### 4.5 Pipeline com CREI Server

```bash
#!/bin/bash

export CREI_PORT=8000
./crei-server &
CREI_PID=$!
sleep 2

APP_ID="application_1234567890_0001"

curl -s http://localhost:8000/health | jq .

curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"app_id":"'$APP_ID'","request_type":"full"}' | jq .

kill $CREI_PID
```

---

## 5. Variaveis de Ambiente Comuns

| Variavel | Usada por | Padrao | Descricao |
|---|---|---|---|
| `CLICKHOUSE_URL` | diagnose, recommend, analyze, spillwatch, mcp-server, crei-server | `http://localhost:8123` | URL do servidor ClickHouse |
| `CREI_URL` | recommend, mcp-server | `http://localhost:8000` | URL do servidor CREI |
| `CREI_PORT` | crei-server | `8000` | Porta do servidor CREI |
| `OPENAI_API_KEY` | recommend | -- | Chave da API OpenAI para fallback LLM |
| `SKEW_RATIO` | diagnostician | `5.0` | Threshold de razao de skew |
| `SPILL_THRESHOLD_MB` | diagnostician | `100.0` | Threshold de spill em MB |
| `GC_TIME_RATIO` | diagnostician | `0.3` | Threshold de razao de tempo GC |
| `FAILED_TASK_RATE` | diagnostician | `0.05` | Taxa maxima de tasks falhas |

---

## 6. Tipos de Anomalia Detectados

| Anomalia | Descricao | Severidade Tipica |
|---|---|---|
| `data_skew` | Desbalanceamento de dados entre particoes de um stage | HIGH / CRITICAL |
| `spill_to_disk` | Dados sendo escritos em disco por falta de memoria | HIGH |
| `memory_pressure` | Pressao de memoria nos executores | MEDIUM / HIGH |
| `gc_thrash` | Excesso de garbage collection | MEDIUM |
| `broadcast_missed` | Oportunidade de broadcast join nao aproveitada | MEDIUM |
| `too_many_partitions` | Numero excessivo de particoes | LOW / MEDIUM |
| `unknown` | Anomalia nao classificada | LOW |

---

## 7. Estrutura de Diretorios Relevante

```
go-apex/
├── cmd/
│   ├── diagnose/main.go      # CLI de diagnostico
│   ├── validate/main.go      # CLI de validacao
│   ├── recommend/main.go     # CLI de recomendacoes
│   ├── analyze/main.go       # CLI de analise completa
│   ├── spillwatch/main.go    # CLI de monitoramento de spill
│   ├── mcp-server/main.go    # Servidor MCP (stdio)
│   └── crei-server/main.go   # Servidor CREI (HTTP)
├── internal/
│   ├── clickhouse/           # Cliente ClickHouse
│   ├── diagnostician/        # Logica de diagnostico T1
│   ├── recommender/          # Logica de recomendacoes T2
│   ├── validator/            # Validacao de evidencias
│   ├── watcher/              # Watchers de spill e skew
│   ├── models/               # Tipos de dados compartilhados
│   └── runbook/              # Gerenciamento de runbooks
├── pkg/
│   └── mcp/                  # Funcoes MCP (QueryJob, GetRecommendations)
├── runbooks/                 # Runbooks YAML de correcao
└── docs/
    └── cli-api.md            # Este documento
```

---

*Documento gerado automaticamente a partir da analise do codigo-fonte do projeto Apex.*
