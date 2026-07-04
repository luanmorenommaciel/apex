# contracts/watcher.contract — o que todo Watcher recebe e devolve

Um Watcher é um detector especializado (skew, memória, custo...). Para que o Coordinator
consiga juntar os achados de QUALQUER watcher de forma uniforme, todos devolvem o mesmo
formato de "achado" (Finding). É como exigir que todo funcionário preencha o mesmo formulário
de ocorrência — não importa o departamento, o gerente lê todos da mesma forma.

## Entrada

O Watcher recebe uma **janela de eventos** (ou faz uma consulta SQL no ClickHouse) referente a
uma `execution_id` (uma query). Ele não recebe o cluster inteiro — recebe o recorte da query
que está analisando.

## Saída — o Finding

```json
{
  "watcher": "shuffle_skew",          // qual watcher gerou
  "execution_id": 1,
  "severity": "high",                  // low | medium | high
  "confidence": 0.0,                   // 0..1 — veja a regra de ouro abaixo
  "evidence": [                        // FATOS medidos, nao opiniao
    "hot key na linha job.py:58: 1 tarefa leu 200.100 registros (80% do stage)",
    "operador de join: SortMergeJoin"
  ],
  "root_cause": "data skew na chave de join customer_id",
  "recommendations": [                 // ordenadas por impacto
    "broadcast o lado customers (e pequeno)",
    "habilitar spark.sql.adaptive.skewJoin.enabled",
    "salgar a chave customer_id"
  ]
}
```

## A regra de ouro do `confidence` (lição do AgentSpec)

> A confiança é **calculada a partir da evidência, nunca auto-avaliada pelo LLM.**

Isto é o que o AgentSpec — o produto do Luan que já roda em produção — faz com todos os agentes
dele, e é o que torna a recomendação confiável pra um engenheiro sênior. Na prática:

- `confidence` alto = os números batem forte com um padrão conhecido (ex.: 1 tarefa lendo 80%
  dos registros + SortMergeJoin = skew clássico, confiança ~0.9).
- `confidence` baixo = os sinais são ambíguos.

E aqui entra o **Judge**: quando a confiança fica abaixo de um limite (ex.: 0.6) e a severidade
é alta, o Coordinator escala pro Judge — o revisor mais caro/poderoso — em vez de gastar LLM caro
em todo caso. É barato no caso óbvio, caro só no caso duvidoso. Essa é a decisão de arquitetura
que está registrada como "Quando o classificador dispara?" na pasta de ADRs do repositório.
