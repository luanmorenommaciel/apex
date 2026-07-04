# Apex V1 Skeleton

Implementação mínima da arquitetura desenhada pelo Luan na reunião 30/06.

```
Spark Envy → SparkListener → ClickHouse → Diagnóstico LLM → MCP
```

---

## Pré-requisitos

- Docker + Docker Compose
- Python 3.11+
- `ANTHROPIC_API_KEY` no ambiente

---

## Como rodar (fim a fim)

### 1. Subir o ambiente

```bash
cd v1-skeleton
docker compose up -d
```

Aguarda o ClickHouse ficar healthy:
```bash
docker compose ps
```

### 2. Instalar dependências Python

```bash
pip install -r requirements.txt
```

### 3. Submeter o job demo (com listener)

```bash
docker exec -it <spark-master-container> spark-submit \
  --master spark://spark-master:7077 \
  --py-files /opt/listener/spark_listener.py,/opt/listener/clickhouse_writer.py \
  /opt/jobs/demo_skew_job.py
```

O job vai:
- Gerar dados com hot key `HOT_KEY` (skew proposital)
- SparkListener captura métricas de cada stage/task
- Envia ao ClickHouse em tempo real

### 4. Verificar dados no ClickHouse

```bash
# Interface HTTP: http://localhost:8123/play
# Query:
SELECT * FROM apex.suspicious_stages;
SELECT app_id, num_tasks, duration_ms, disk_spill FROM apex.stage_metrics ORDER BY disk_spill DESC;
```

### 5. Rodar o diagnóstico LLM

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export APEX_CH_HOST="localhost"

python analysis/diagnose.py --app-id <app_id_do_job>
```

Retorna um finding como:
```json
{
  "pattern": "skew",
  "severity": "high",
  "confidence": 0.91,
  "bottleneck_stage_id": 2,
  "root_cause": "Hot key 'HOT_KEY' concentra 80% dos registros em 1 task",
  "recommendation": "Adicionar salting na chave de join + repartition(50)"
}
```

### 6. Conectar o MCP ao Claude Code

```bash
python mcp/server.py
```

Registrar em `~/.claude/claude.json`:
```json
{
  "mcpServers": {
    "apex": {
      "command": "python",
      "args": ["/caminho/para/v1-skeleton/mcp/server.py"],
      "env": {
        "APEX_CH_HOST": "localhost",
        "ANTHROPIC_API_KEY": "sk-ant-..."
      }
    }
  }
}
```

Agora no Claude Code:
```
> Quais são os jobs mais lentos hoje?
> O que está errado com app-20240630-123456?
> Diagnostica o job app-20240630-123456
```

---

## Estrutura

```
v1-skeleton/
├── docker-compose.yml          # Spark Envy + ClickHouse
├── schema/
│   └── init.sql                # Schema do ClickHouse (auto-executado)
├── listener/
│   ├── spark_listener.py       # SparkListenerInterface via py4j
│   └── clickhouse_writer.py    # Client ClickHouse
├── jobs/
│   └── demo_skew_job.py        # Job demo com skew proposital
├── analysis/
│   └── diagnose.py             # LLM analysis (Anthropic API)
├── mcp/
│   └── server.py               # MCP server (Claude Code / Cursor)
└── requirements.txt
```

---

## Decisão arquitetural pendente (ADR-005)

Esta implementação usa **SparkListener in-process** (similar ao DataFlint).
A abordagem atual do Apex usa **zero-JAR event log** (leitura pós-job via MinIO).

Luan + Augusto precisam decidir qual abordagem seguir antes de escalar.
Ver issue #27 para o ADR completo.

---

## Próximos passos (V2)

- [ ] Substituir chamada direta à Anthropic API por Crew.ai multi-agent
- [ ] Adicionar watcher skew (reusar `watchers/skew_watcher.py` existente)
- [ ] Integrar com plat-v0 (MinIO + Spark existente)
- [ ] oracle.py: validar se SparkListener captura os mesmos dados do event log
