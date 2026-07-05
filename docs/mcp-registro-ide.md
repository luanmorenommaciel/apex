# Apex MCP — Guia de Registro no Cursor e Claude Code

O MCP do Apex expõe 4 ferramentas que permitem ao engenheiro diagnosticar jobs Spark diretamente no IDE.

```
Engenheiro: "O que está errado com o job app-20240630-123456?"
     ↓
Claude Code / Cursor chama o MCP
     ↓
MCP consulta ClickHouse → dispara Crew.ai → retorna finding
     ↓
Engenheiro: recebe root cause + fix concreto no chat
```

---

## Pré-requisitos

- Python 3.11+
- `pip install -r v1-skeleton/requirements.txt`
- Docker com `v1-skeleton/docker-compose.yml` rodando (ou plat-v0)
- `ANTHROPIC_API_KEY` configurada no ambiente

---

## 1. Registrar no Claude Code

Edite (ou crie) `~/.claude/claude.json`:

```json
{
  "mcpServers": {
    "apex": {
      "command": "python",
      "args": ["C:/Users/Guest/Claude/Projects/Data Ship/v1-skeleton/mcp/server.py"],
      "env": {
        "APEX_CH_HOST": "localhost",
        "APEX_CH_PORT": "8123",
        "APEX_CH_USER": "apex",
        "APEX_CH_PASSWORD": "apex123",
        "ANTHROPIC_API_KEY": "sk-ant-..."
      }
    }
  }
}
```

Reinicie o Claude Code após salvar. Você verá `apex` no painel de MCPs conectados.

---

## 2. Registrar no Cursor

Edite `~/.cursor/mcp.json` (crie se não existir):

```json
{
  "mcpServers": {
    "apex": {
      "command": "python",
      "args": ["C:/Users/Guest/Claude/Projects/Data Ship/v1-skeleton/mcp/server.py"],
      "env": {
        "APEX_CH_HOST": "localhost",
        "ANTHROPIC_API_KEY": "sk-ant-..."
      }
    }
  }
}
```

No Cursor: `Ctrl+Shift+P` → `MCP: Reload Servers`.

---

## 3. Ferramentas disponíveis

| Tool | O que faz | Quando usar |
|---|---|---|
| `get_findings` | Retorna diagnósticos existentes por `app_id` | Primeiro passo — ver se já foi analisado |
| `get_stage_metrics` | Métricas detalhadas dos stages de um job | Investigar qual stage é o bottleneck |
| `list_slow_apps` | Lista os jobs mais lentos das últimas 24h | Encontrar onde está o maior problema |
| `trigger_diagnosis` | Roda o pipeline Crew.ai para um `app_id` | Quando não há findings ainda |

---

## 4. Exemplos de uso no chat

```
# Verificar se um job já foi diagnosticado
"O que está errado com o job app-20240704-001?"

# Se não houver finding:
"Diagnostica o job app-20240704-001"

# Ver os jobs mais problemáticos hoje:
"Quais os 5 jobs mais lentos das últimas 24h?"

# Investigar um stage específico:
"Me mostra as métricas de stage do job app-20240704-001"
```

---

## 5. Rodar o servidor manualmente (debug)

```bash
cd "C:\Users\Guest\Claude\Projects\Data Ship"
set APEX_CH_HOST=localhost
set ANTHROPIC_API_KEY=sk-ant-...
python v1-skeleton/mcp/server.py
```

O servidor usa `stdio` — o IDE gerencia o processo automaticamente quando registrado.

---

## 6. Verificar conexão com ClickHouse

```bash
# Interface web do ClickHouse:
# http://localhost:8123/play

# Query de sanidade:
SELECT count() FROM apex.stage_metrics;
SELECT count() FROM apex.findings;
```

Se retornar 0, o SparkListener ainda não rodou nenhum job. Execute:
```bash
cd v1-skeleton
docker compose up -d
docker exec spark-master spark-submit \
  --py-files /opt/listener/spark_listener.py,/opt/listener/clickhouse_writer.py \
  /opt/jobs/demo_skew_job.py
```

---

## 7. Fluxo fim a fim (teste completo)

```
1. docker compose up -d              # sobe Spark + ClickHouse
2. spark-submit demo_skew_job.py     # roda job com skew proposital
3. No Claude Code: "diagnostica o job <app_id>"
4. Crew.ai detecta skew → retorna finding com salting recommendation
5. Claude Code sugere o fix no código
```

---

*Documento gerado por Claude Sonnet 4.6 (Cowork) — 04/07/2026*
