# [Decision][Governança/CI] Escolher como a CI acompanha a troca de ubuntu-latest para Ubuntu 26.04

## Problema e intenção
O aviso oficial, reconferido em 18/10/2026 (horário de São Paulo), [actions/runner-images#14748](https://github.com/actions/runner-images/issues/14748), aberto em 17/09, informa que o rótulo `ubuntu-latest` passa a usar Ubuntu 26.04 num rollout de 19/10 a 19/11/2026. Os workflows do APEX usam `ubuntu-latest`. A intenção é preparar a transição com evidência de qual imagem cada run usou, sem pin nem instalação extra sem necessidade demonstrada.

## Estado
- `ci.yml` e `jar.yml` na main `c3c3ea3` usam `runs-on: ubuntu-latest`; o `ci.yml` configura Node 22 e uv e verifica o PowerShell 7 ([ci.yml:87-90](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/.github/workflows/ci.yml#L87-L90)); o `jar.yml` instala JDK por matriz.
- O manifesto da imagem Ubuntu 26.04 capturado em 17/10 lista a imagem 20261012.163.1, PowerShell 7.6.6 e Java 17 como padrão.
- Nenhum run do APEX nessa imagem foi identificado nas fontes consultadas.

## Decisão pendente
Alternativas, combináveis: (a) acompanhar `ubuntu-latest` e registrar ImageVersion e OS em cada run; (b) pin temporário em `ubuntu-24.04` se aparecer incompatibilidade, com data de revisão; (c) instalar explicitamente uma ferramenta que a nova imagem não traga; (d) transição gradual, um workflow por vez.

## Escopo e exclusões
Matriz ferramenta → setup explícito ou imagem, e critério de acompanhamento ou recuo. Fora: rodar CI agora, mudar a fila de PRs, trocar de provedor de runner. O calendário do fornecedor não é prazo do APEX.

## Evidência e limite
Fontes oficiais datadas. O manifesto não prova o comportamento do workflow, do Docker ou do Collector dentro do job.

## Critérios de conclusão
- [ ] Matriz das ferramentas de cada job (Node, uv/Python, PowerShell, Docker/otelcol, JDK) com a origem de cada uma.
- [ ] Decisão registrada e critério de recuo.
- [ ] Na próxima execução pertinente, ImageVersion e versões registradas; um run em outra imagem não conta como prova da migração.

## Como contribuir
Quem mantém a CI ou cada lane pode apontar dependências da imagem que o workflow não instala explicitamente.

Rastreabilidade do backlog: NOV-01, DEC-N1.
