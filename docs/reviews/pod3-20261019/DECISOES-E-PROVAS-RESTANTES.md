# O que resta após concluir a análise documental

A classificação abaixo trata o **próximo passo atômico**, não o aceite completo de uma issue. `ready_offline` significa que uma revisão ou preparação pode ocorrer sem runtime, não que haja autorização para implementar ou publicar. Augusto autorizou esta publicação documental; decisões, aceites e merge continuam separados.

## Pode ser preparado/revisado sem runtime

Os 49 objetos têm próximo passo e critérios no [registro completo](REGISTRO-ATUAL-49.md). Revisão dos diffs já abertos, estudo de alternativas, guias, protocolos e controles podem avançar sem iniciar serviços. As Partes07/08 concluíram reconciliação dos pareceres, recaptura pública, coordenação focal #182/#158/#159, triagem #185 e mapa de encaminhamentos. Ver CONFERENCIA-INDEPENDENTE.md para os limites e correções.

No Pod3, a sequência de revisão continua: #157 e escolha da árvore da #163; #158/#159 coordenadas com #182; #164 e texto residual N10; #183 documental e #184 sintática em seus próprios recortes. Nenhuma review formal ou merge foi praticado pelo Codex.

## Decisões que não cabem ao auditor ratificar

| Decisão | Material já preparado | Resultado humano necessário |
|---|---|---|
| Ask #122 | Comparação API existente, fachada interna e adiamento; código já entregue separado do fluxo Ask | Escolher escopo, contrato, responsabilidade e sequência; fachada não implica serviço novo |
| Token/OpenAPI #171 | Matriz por perfil e leitura dos caminhos existentes/propostos | Política de exposição e localização/gestão da credencial por perfil; #182 não resolve identidade por usuário automaticamente |
| Governança de specs N09 | 23 L1 mapeadas (registro declara duas done/accepted e 21 ready/accepted:false), seis L3 done sem accepted, três YAML em #184; sem novo aceite | Quem altera status, quem aceita e qual evidência; parse válido não é aceite |
| ADR-004/N07 | Cinco precondições registradas e alternativas de privacidade | Ratificar/revisar/adiar cada uma; merge do documento não basta |
| Verify #117 | Piso/unidade/igualdade, atribuição, produtor e consumidores separados | Definir contrato e menor fatia; manter N03 e N01 em recortes próprios |
| Engine #115 | Resolver offline e matriz de SQL/RDD já existentes | Primeiro consumidor e critérios públicos; não impor três PRs |
| Grafo #106/#107 | Propostas de schema e MCP somente leitura | Adoção/schema antes da implementação; estudos podem seguir |
| Ownership #175 e pacote #167/#174 | Variantes, binding, preservação de dev/.env e recursos | Escolher variante/garantia e ambiente antes da prova com efeitos |
| Métricas/DDL #169/#170 | Casos de tentativas/populações e replay/quietude | Política pertinente à mudança; não criar gate universal |
| CI #125/#130 | Nomes de checks, filtros e recibos atualizados | Reconciliar critérios e política; verde isolado não consulta billing nem encerra todos os reruns |

Responsáveis e prazos permanecem a confirmar. Ata-modelo e textos de decisão já existem na Parte06; não foram preenchidos como se a reunião tivesse ocorrido.

## Provas que continuam futuras

- Navegador/nginx #172b: observação na árvore/perfil/ambiente escolhidos; distinguir curl/headers, jsdom, HTTP real e navegação de usuário. A preparação #172a é documental e está separada no registro atualizado.
- Pós-integração #156 e critérios de #130: revisar árvore efetiva e recibos específicos. A prova da base não cobre automaticamente a pilha reposicionada.
- #123/#124: preservar runtime histórico do tail-outlier e escopo do dispatcher; escolher o controle discriminante que ainda falta, sem repetir todo o histórico.
- Verify com linha real: ausência honesta no E2E não certifica produtor/escrita/consumo de um veredito existente.
- Distribuição: nome/artefato/owner decididos antes de build/instalação/TestPyPI/PyPI. Nenhuma dessas etapas foi executada nesta rodada.

Não são necessárias essas execuções para classificar a documentação; são necessárias quando forem o critério de aceite da entrega funcional escolhida.

## N08 — evidência nova do runner

O run jar `39254068517`, SHA da main `c3c3ea3`, terminou verde em 19/10 nos jobs JDK17 e JDK21. O extrato de log do **job JDK17** identifica Ubuntu24.04.5, imagem `ubuntu-24.04`, versão `20261012.334.1`. Isso resolve a dúvida para esse job; não se transfere a JDK21, Node, PowerShell ou toda execução futura de ubuntu-latest. Não é prova de migração a Ubuntu26.04. O log integral (~8,25 milhões de caracteres) não foi lido nem arquivado; foram preservadas identificação do runner e linhas finais relevantes.

Fonte direta: [job JDK17](https://github.com/luanmorenommaciel/apex/actions/runs/39254068517/job/118064815058), [run](https://github.com/luanmorenommaciel/apex/actions/runs/39254068517); extrato local em recibo local jar-runner-excerpt.json (não incluído nesta edição pública).

## Preservação e publicação

O fechamento amplo continua local. #181 e drafts #183/#184 têm seus recibos anteriores; não contêm automaticamente o adendo novo nem todas as fontes privadas. A Parte04 depende das partes anteriores e de fontes/custódia identificadas. Antes de eliminar qualquer arquivo, preparar backup recuperável e conferir completude/recuperação; esta auditoria não autoriza exclusão.

A atualização da #181 tem recibo de publicação próprio; o texto anterior permanece no acervo de origem. Esta publicação documental e seus encaminhamentos foram autorizados; merge e execução de produto não fazem parte dela.

## Adendo #185 e preparação #172

A #185 tem triagem focal própria e preserva autoria do Agmar; conferir implementação candidata antes de duplicar #167/N06. Ver TRIAGEM-PR185.md. O registro tem 32 próximos passos ready_offline e 17 owner_decision. Isso não elimina runtime: #172b e demais provas operacionais continuam futuras nos seus escopos.
