# Onboarding MCP — Claude Code, Cursor e Codex

Estado: **guia conferido documentalmente, com verificação operacional pendente**. Fontes dos fornecedores consultadas em 19/10/2026. Versões instaladas dos três clientes, ambiente e comandos deste guia não foram executados nesta etapa; registrar versões no recibo ao validar.

## Alvo e pré-requisitos

Este guia cobre o MCP stdio local já existente. A configuração de origem é [serve/.mcp.json](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/serve/.mcp.json), com `uvx --from ./serve apex-mcp`; o [README](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/serve/README.md) mostra a variante com caminho absoluto. Usar caminho absoluto para não depender do diretório de trabalho do cliente. Substitua `/CAMINHO/DO/REPO` pelo checkout escolhido antes de usar os exemplos.

Pré-requisitos: checkout na revisão escolhida; uv/uvx disponível ao processo do cliente; dependências compatíveis do Serve; conexão ClickHouse configurada no ambiente autorizado. Configure host, porta, usuário, password e database pelos meios locais da instalação. Não versionar segredo nem usar automaticamente credenciais de desenvolvimento em outro perfil. Arquivo de configuração válido não comprova conexão ou consulta.

O guia do estado atual pode avançar sem aprovar Ask ou N11. Instalar um servidor concede a ele o alcance do processo/credenciais fornecidos; este documento não realiza essa instalação ou concede permissões.

## Caminhos e formato por cliente

| Cliente | Projeto | Usuário | Formato / conferência |
|---|---|---|---|
| Claude Code | `.mcp.json` na raiz; aprovação de projeto conforme cliente | `~/.claude.json`; escopo local também é associado ao projeto nesse arquivo | JSON MCP; `claude mcp list`, `claude mcp get apex`, `/mcp` |
| Cursor | `.cursor/mcp.json` | `~/.cursor/mcp.json` | JSON; conferir Customize > MCPs, ferramentas e MCP Logs |
| Codex | `.codex/config.toml` em projeto confiável | `~/.codex/config.toml` | TOML; `codex mcp list` e painel `/mcp` do cliente compatível |

Claude: escopos e comandos na [referência MCP](https://code.claude.com/docs/en/mcp). Cursor: formato e interpolação na [referência MCP](https://cursor.com/docs/mcp), com locais e logs também no [guia de integração](https://prod.cursor.com/help/customization/mcp). Codex: configuração e encaminhamento de variáveis na [referência MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli). A frase antiga “todos leem o mesmo schema na raiz” precisa ser corrigida: Codex usa TOML e Cursor tem diretório próprio.

## Claude Code — exemplo de projeto

Modelo sem segredo literal; as variáveis referenciadas precisam existir no ambiente do cliente. Reiniciar o processo após mudanças de ambiente quando necessário.

```json
{
  "mcpServers": {
    "apex": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "/CAMINHO/DO/REPO/serve", "apex-mcp"],
      "env": {
        "CLICKHOUSE_HOST": "${CLICKHOUSE_HOST}",
        "CLICKHOUSE_PORT": "${CLICKHOUSE_PORT}",
        "CLICKHOUSE_USER": "${CLICKHOUSE_USER}",
        "CLICKHOUSE_PASSWORD": "${CLICKHOUSE_PASSWORD}",
        "CLICKHOUSE_DATABASE": "${CLICKHOUSE_DATABASE}"
      }
    }
  }
}
```

Salvar como `.mcp.json` do projeto escolhido. Após revisar a configuração e aprovar pelo fluxo do cliente, conferir `claude mcp list`, `claude mcp get apex` e `/mcp`. Configuração adicionada é etapa diferente de servidor conectado.

## Cursor — exemplo de projeto

Em `.cursor/mcp.json`, usar a sintaxe de variáveis do Cursor; não copiar referências de outro cliente literalmente.

```json
{
  "mcpServers": {
    "apex": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "/CAMINHO/DO/REPO/serve", "apex-mcp"],
      "env": {
        "CLICKHOUSE_HOST": "${env:CLICKHOUSE_HOST}",
        "CLICKHOUSE_PORT": "${env:CLICKHOUSE_PORT}",
        "CLICKHOUSE_USER": "${env:CLICKHOUSE_USER}",
        "CLICKHOUSE_PASSWORD": "${env:CLICKHOUSE_PASSWORD}",
        "CLICKHOUSE_DATABASE": "${env:CLICKHOUSE_DATABASE}"
      }
    }
  }
}
```

Conferir servidor e ferramentas em Customize > MCPs e logs no painel Output > MCP Logs. A configuração de projeto prevalece quando o mesmo nome aparece no escopo global. Reiniciar Cursor após atualizar variáveis do ambiente do processo, se necessário. Registrar a versão do cliente porque nomes de menus podem evoluir.

## Codex — exemplo de projeto confiável

Adicionar à configuração existente, sem sobrescrevê-la. Encaminhar os nomes de variáveis; valores sensíveis permanecem no ambiente.

```toml
[mcp_servers.apex]
command = "uvx"
args = ["--from", "/CAMINHO/DO/REPO/serve", "apex-mcp"]
env_vars = ["CLICKHOUSE_HOST", "CLICKHOUSE_PORT", "CLICKHOUSE_USER", "CLICKHOUSE_PASSWORD", "CLICKHOUSE_DATABASE"]
```

Conferir escopo/trust, `codex mcp list` e painel de ferramentas. Se usar o aplicativo, confirmar que as variáveis estão no ambiente do processo que inicia o servidor; não basta exportar em outro terminal depois. Configuração de projeto exige projeto confiável. Não inferir suporte carregando `.mcp.json` de outro cliente.

## Verificação operacional a realizar

1. Registrar revisão do APEX, cliente/versão, SO, versão uv/uvx, escopo e arquivo usados, sem segredos.
2. Conferir processo do servidor e lista exata observada. No snapshot são oito: analyze_run, compare_runs, explain_stage, list_runs, recall_similar_runs, search_kb, suggest_fix, verify_fix. Se houver mudança, reconciliar contrato e revisão.
3. Executar somente a consulta acordada com fixture própria; `list_runs` é uma candidata. Registrar argumentos não sensíveis, resultado esperado e observado. Store vazio e indisponível são estados distintos; ausência de dados pode ser válida.
4. Registrar logs sanitizados e marcar cliente validado somente com recibo. A lista de ferramentas prova descoberta, não todos os comportamentos.

| Sintoma | Conferência |
|---|---|
| Servidor não inicia | Executável uvx no PATH do processo; caminho absoluto do checkout; dependências/versões |
| Não aparece no cliente | Arquivo/escopo corretos; projeto confiável/aprovação pendente; nomes duplicados |
| Variável ausente | Sintaxe do cliente; ambiente de quem inicia o aplicativo; reinício necessário |
| Conecta e retorna indisponível | Endpoint/porta/permissões do store; estado da infraestrutura; envelope de erro sanitizado |
| Quantidade inesperada de tools | Revisão instalada, configuração duplicada e contrato esperado; não corrigir número cegamente |

API v1/nginx/browser têm prova e política próprias (#156/#171/#172). Este onboarding stdio não certifica o perfil compartilhado do Ask. Publicação de pacote segue [decisão de distribuição](DECISAO-DISTRIBUICAO.md).
