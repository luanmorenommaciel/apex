# Apex — Estado atual da solução (deck)

Apresentação de 23 slides com o estado da `main` em `a289e53` (17/09/2026): as oito lanes,
o contrato v0.6, as provas ao vivo, os limites declarados e uma leitura crítica da visão
original contra o que está no repositório.

Paleta e tipografia seguem o console React da solução (`front/tailwind.config.js`):
superfícies escuras, laranja Spark e cores com significado (vermelho = finding,
amarelo = retido, verde = certificado).

## Conteúdo

| Caminho | O que é |
|---|---|
| `project/deck.json` | índice do deck: título, ordem dos slides, seções e fontes |
| `project/slides/<id>.html` | um slide por arquivo, canvas 1920×1080, estilos inline |

Cada slide tem as fontes citadas nas notas do apresentador (`<aside>`).

## Origem

Gerado como artefato do tipo Slides no claude.ai a partir de uma leitura da branch `main`
(README, CONTRACT, PIPELINE, CHANGELOG, ADRs e README de cada lane). Os slides são o
formato de origem do artefato, não um PDF: para apresentar, importe `project/` num artefato
Slides ou exporte a partir dele.

## Atenção

O slide `lacunas` ("Visão das reuniões contra a main") é uma leitura de quem montou o deck,
feita por buscas no repositório e pelas transcrições. Confirme com o Luan antes de tratar
como decisão. Os números vêm dos documentos da main e não foram reproduzidos.
