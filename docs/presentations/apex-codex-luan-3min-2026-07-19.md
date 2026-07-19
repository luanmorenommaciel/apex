# Roteiro de 3 minutos: Apex Commander

## Abertura: 0:00 a 0:35

“O APEX resolve um problema simples de enunciar e caro de operar: encontrar um
alerta Spark nao prova que a correcao melhorou o job. Nesta rodada, provamos um
loop completo no caso `job-42`: evidencia, diagnostico, preview seguro e
comparacao antes/depois.”

Mostre a primeira slide. Aponte os tres numeros: skew `29.4x -> 0.0`, finding
`1 -> 0` e T1 em `226.991 ms` sem LLM obrigatorio.

## Problema e caminho: 0:35 a 1:15

“O engenheiro recebe metricas espalhadas por logs, planos e interfaces. O APEX
normaliza essa telemetria, roda detectores deterministicos e passa o finding
pelo EvidenceValidator. Depois, ele produz uma recomendacao revisavel. A
correcao so segue pelo caminho guardado, com preview, aprovacao humana e
verificacao.”

Mostre a segunda slide. Diga que o Judge pode revisar o contexto, mas nao
substitui o T1 nem aplica alteracoes.

## Prova: 1:15 a 2:10

“No caso `job-42`, a execucao antes tinha skew ratio `29.4x` e um finding high.
Depois da mitigacao e da reexecucao, o ratio caiu para `0.0` e o finding sumiu.
Essa comparacao e o que transforma uma sugestao em evidencia operacional.”

Mostre a terceira slide. Se surgir pergunta sobre seguranca, diga que o apply
continua no MCP/IDE com token, hash, raiz permitida e verify.

## Pedido ao time: 2:10 a 3:00

“A primeira entrega esta pronta para uso local. Rodem `python
tools/run_commander_ui.py`, abram o caso `job-42` e testem a recomendacao e o
preview seguro. Preciso de tres respostas: a evidencia esta clara, a
recomendacao ajuda a decidir e qual deve ser o proximo caso real? A UI ainda e
single-user e nao aplica mudancas sozinha. Esses limites sao intencionais nesta
primeira entrega.”

Mostre a quarta slide e abra a UI local se houver tempo.
