# Evidências dos três encaminhamentos

Corte preservado da Parte 10: fontes de 19/10/2026. Os links de código abaixo usam SHA; não são consulta a uma branch mutável. Ler um teste não equivale a executá-lo. Resultados de runtime citados como relato permanecem relatos.

## 1. Revisar a proposta API-only e preservar os testes

- **Direto, metadados:** [#182](https://github.com/luanmorenommaciel/apex/pull/182); [recibo](https://api.github.com/repos/luanmorenommaciel/apex/pulls/182). Head `74fdb0791825aa89c419694ec71f2aa3e6ea4d74`, autor `agmarcastro`.
- **Direto, metadados:** [#158](https://github.com/luanmorenommaciel/apex/pull/158); [recibo](https://api.github.com/repos/luanmorenommaciel/apex/pulls/158). Head `514b0e573bce9593ac1737869568161b3e951a49`, autor `gustocezar`.
- **Direto, metadados:** [#159](https://github.com/luanmorenommaciel/apex/pull/159); [recibo](https://api.github.com/repos/luanmorenommaciel/apex/pulls/159). Head `1685f8ac91b8e9b68a83d10176519c963e186ad4`, autor `gustocezar`.
- **Estático, ponto de integração:** [PR #182: serve/tests/test_console_reads.py](https://github.com/luanmorenommaciel/apex/blob/74fdb0791825aa89c419694ec71f2aa3e6ea4d74/serve/tests/test_console_reads.py). Dois usos de símbolos removidos exigem adaptação; execução combinada não realizada.
- **Estático, ponto de integração:** [PR #158: serve/tests/test_console_reads.py](https://github.com/luanmorenommaciel/apex/blob/514b0e573bce9593ac1737869568161b3e951a49/serve/tests/test_console_reads.py). Dois usos de símbolos removidos exigem adaptação; execução combinada não realizada.
- **Estático, ponto de integração:** [PR #159: serve/tests/test_console_parity_gate.py](https://github.com/luanmorenommaciel/apex/blob/1685f8ac91b8e9b68a83d10176519c963e186ad4/serve/tests/test_console_parity_gate.py). Dois usos de símbolos removidos exigem adaptação; execução combinada não realizada.
- **Relato preservado:** corpo da #182 descreve seis stages com refused_count=3 em ClickHouse. O teste TypeScript não executa a CTE; pedir oráculo versionado não significa negar esse relato.

## 2. Escolher o perfil de exposição e custódia do token

- **Direto, metadados:** [#171](https://github.com/luanmorenommaciel/apex/issues/171); [recibo](https://api.github.com/repos/luanmorenommaciel/apex/issues/171).
- **Estático, configuração candidata:** [runtimeConfig.ts](https://github.com/luanmorenommaciel/apex/blob/74fdb0791825aa89c419694ec71f2aa3e6ea4d74/front/src/data/runtimeConfig.ts). O token chega ao navegador; isso não demonstra identidade individual nem decisão por perfil.

## 3. Preparar o protocolo da prova HTTP no navegador

- **Direto, metadados:** [#172](https://github.com/luanmorenommaciel/apex/issues/172); [recibo](https://api.github.com/repos/luanmorenommaciel/apex/issues/172).
- **Proposto:** [protocolo e casos](MATRIZ-DE-EVIDENCIAS.md). API/TestClient/jsdom/curl e browser real são superfícies distintas; nenhuma nova prova é executada para escrever o protocolo.


## Esclarecimento da revalidação de 19/10

A contribuição do Agmar na #182 inclui implementação na branch, não somente ideias. O corpo relata live em ClickHouse 24.8 (seis stages, refused_count=3), gate 17/17, Front 202/8 skip e Serve 456. O histórico público da #153 em `serve/VALIDATION.md` relata três jobs reais até o App; o orquestrador chama Vitest/jsdom e acessa a API diretamente. O commit 222498cf da #182 relata imagem de produção em fixtures. O Discord acrescenta relato de E2E inclusive nginx, cuja árvore/recibo devem ser reconciliados antes de solicitar prova adicional. Nenhuma dessas execuções foi reproduzida nesta auditoria.

- [VALIDATION no head da #182](https://github.com/luanmorenommaciel/apex/blob/74fdb0791825aa89c419694ec71f2aa3e6ea4d74/serve/VALIDATION.md).
- [E2E até o App](https://github.com/luanmorenommaciel/apex/blob/74fdb0791825aa89c419694ec71f2aa3e6ea4d74/tests/e2e/console_reflection.sh).
- [Gate e bindings da #182](https://github.com/luanmorenommaciel/apex/blob/74fdb0791825aa89c419694ec71f2aa3e6ea4d74/serve/tools/console_parity_gate.py) e [testes do gate](https://github.com/luanmorenommaciel/apex/blob/74fdb0791825aa89c419694ec71f2aa3e6ea4d74/serve/tests/test_console_parity_gate.py). R2 está nesses arquivos, além do teste de leituras citado acima.
