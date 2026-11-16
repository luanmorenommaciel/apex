---
title: Apex — revisão de design com html-ppt
date: 2026-11-16
tags: [apex, apresentacao, design, html-ppt, review]
status: reviewed-with-findings
---

# Apex v0.2 · revisão de design

## Escopo

Revisão do [deck HTML v0.2](2026-11-09-apresentacao-mvp-deck.html): 17 slides principais e dois apêndices. O conteúdo foi lido em HTML/CSS/JS, a navegação sequencial foi percorrida no Firefox e foram inspecionadas capturas representativas. Esta etapa produz recomendações; não altera o design do deck.

Critérios: skill local [html-ppt](https://github.com/lewislulu/html-ppt-skill/blob/main/SKILL.md), guia de autoria, catálogo de layouts, tema gruvbox-dark, tokens/base CSS e layout image-text-split. A avaliação considera o público de engenharia e a identidade visual existente do Apex. Não exige trocar o tema nem migrar todo o runtime para julgar a qualidade do design.

Artefato avaliado, SHA-256: `763181643c45d99b0081da25cd41b2adc78dd7a31aeebcc2b3414c40518d593c`.

## Veredito

**Boa identidade visual; recomenda-se uma revisão focada em legibilidade e comunicação visual.** Fundo escuro, laranja, títulos claros e bordas consistentes conectam a apresentação ao console. O fluxo de conexão e a página de feedback têm estrutura fácil de acompanhar. Não foi confirmado bloqueio de renderização nas capturas inspecionadas.

O principal problema é a adaptação da documentação ao palco: tabelas, cards e ressalvas textuais ocupam a maior parte da narrativa. As cores de estado ajudam, mas nem sempre há um elemento visual dominante que torne a mensagem memorável.

## Achados, por impacto

### 1. Legibilidade de texto secundário · prioridade média

**Evidência direta/derivada:** CSS nas linhas 15, 44, 47 e 72. `--dim` tem contraste calculado de aproximadamente 3,76:1 sobre o canvas e 3,03:1 sobre os cards. Esse token é usado em labels de 11 px e cabeçalhos de tabela de 10 px no canvas 1280×720. Os textos principais têm contraste melhor: `--body` chega a 6,59:1 sobre canvas e 5,30:1 sobre cards; os títulos claros chegam a 13,35:1 sobre canvas.

**Impacto:** labels, cabeçalhos e rodapés podem desaparecer antes dos títulos quando a imagem é reduzida ou projetada. A hierarquia visual fica dependente de cores sutis.

**Recomendação:** reservar `--dim` para decoração ou metadado dispensável; usar texto mais claro nos rótulos necessários à compreensão. Aumentar cabeçalhos de tabela e labels essenciais. Avaliar tamanho depois de normalizar para o canvas — os 16 px desta apresentação correspondem a 24 px quando ampliados para 1920×1080; não comparar valores de fonte entre canvases diferentes sem essa conversão.

### 2. Slides de produto e evidência densos · prioridade média

**Evidência direta/derivada:** slides 6–11 e 19 têm mais de cem palavras de conteúdo visível, incluindo títulos e chrome; slide 10 tem aproximadamente 128. O slide 9 apresenta oito tools, perguntas correspondentes e três cards laterais. Há 37 cards no deck inteiro. Fontes principais: linhas 239, 258, 283 e 297.

**Impacto:** muitas unidades competem pela atenção. O público precisa ler enquanto o apresentador explica, e a evidência importante recebe o mesmo peso de detalhes operacionais.

**Recomendação por slide:**

| Slide | Tratamento sugerido |
|---|---|
| 8 · Console | Screenshot anotado de uma tela e três chamadas: execução, finding, evidência. Estado de Ask/Search KB no apêndice. |
| 9 · MCP | Um exemplo preparado de pergunta → tool → resposta, com identificação da fonte. Inventário completo de oito tools no apêndice. |
| 10 · Demo | Uma trilha visual de quatro passos: Runs → Stage → Compare → Memory. Manter o rótulo de dados de exemplo. |
| 11 · Evidências | Duas mensagens curtas: o que foi conferido agora e o que é evidência histórica. Manter a divergência de veredito e o limite de Verify em linguagem explícita. |

São recomendações de composição, não uma afirmação de que cem palavras sejam um limite universal ou de que esses slides estejam necessariamente cortados.

### 3. O produto não aparece visualmente · prioridade média

**Evidência direta:** o HTML contém apenas duas imagens, ambas com `alt="APEX"`; são o logo da capa e do encerramento. Não há captura de console nem de saída MCP no deck. O produto é descrito por tabelas e cards.

**Impacto:** a plateia entende o inventário, mas depende da demo para formar uma imagem concreta da experiência. Se o trecho ao vivo for substituído por explicação, o deck perde a referência visual do produto.

**Recomendação:** adicionar uma captura real do console, identificada como fixtures quando essa for a origem. Usar o layout `image-single` ou `image-text-split` da skill, com `.img-frame.contain`, sem recortar métricas ou rótulos que sustentem o argumento. Para MCP, mostrar saída efetivamente capturada e datada; não inventar uma resposta bem-sucedida. Diversificar com processo, timeline e screenshot em vez de repetir grids de cards.

### 4. Instruções de ensaio disputam espaço com conteúdo da plateia · prioridade média

**Evidência direta:** linhas 273, 288, 312 e 314 incluem escolha de cliente no ensaio, alternativa de captura, gravação de backup e estado de PRs. A skill orienta manter instruções destinadas ao apresentador nas notas.

**Impacto:** a apresentação de produto ganha aparência de reunião de preparação. O público recebe decisões de bastidor que não ajudam a interpretar a tela.

**Recomendação:** mover logística de ensaio e números de PR para notas ou material de apoio. Preservar no slide as limitações que mudam a interpretação: dados de exemplo, diagnóstico MCP não revalidado nesta sessão, divergência de políticas e ausência de correção real verificada. Simplificar essas mensagens sem escondê-las.

### 5. Operação por vários apresentadores pode melhorar · prioridade baixa

**Evidência direta de código:** linhas 411–437: navegação por teclado, hash, N para drawer de notas e F para tela cheia; não há overview nem janela separada de apresentador. Os apêndices seguem imediatamente o encerramento.

**Impacto:** é fácil avançar para o apêndice por engano ou abrir notas na própria superfície compartilhada. Isso é risco operacional, não uma falha observada durante a apresentação.

**Recomendação:** preparar uma visão separada de apresentador, com próximo slide e timer, e acesso deliberado ao apêndice. O runtime de html-ppt oferece esses recursos, mas sua adoção exige adaptar e testar o deck; trocar nomes de classes ou apenas incluir o script não basta. Não migrar automaticamente para outro template por causa desta revisão.

## Risco e limites da avaliação

- A avaliação de projeção é inferida a partir de tamanho e contraste; não houve teste em sala ou à distância.
- Capturas de referência foram inspecionadas no Firefox (capa, conexão, MCP, evidência, feedback e JAR) e o slide 10 também havia sido visto no Chrome. Os 19 slides foram percorridos por teclado com leituras de acessibilidade. Isso não equivale a inspeção de pixels em todos os slides e tamanhos de janela.
- Não foram certificados PDF/print, fallback de fontes offline, touchscreen ou janela separada de apresentador.
- A mudança de conteúdo da v0.2 respondeu ao feedback do Agmar; estes achados avaliam como esse conteúdo deve ser apresentado visualmente.

## Validação

- [direct/pass] Leitura de HTML/CSS/JS dos 19 slides e das referências da skill citadas.
- [direct/pass] Navegação sequencial de 1 a 19 no Firefox, com verificação dos títulos/contador pela acessibilidade; capturas representativas renderizadas.
- [derived] Contagem de palavras/cards e cálculo de contraste a partir das cores declaradas: [JSON de auditoria](2026-11-16-demo-evidence/design-audit.json).
- O artefato HTML não foi modificado nesta revisão de design.

## Recomendação

Manter a identidade escura com laranja Apex. Fazer primeiro uma revisão de slides 8–11: uma captura anotada do console, um exemplo MCP com fonte, uma trilha visual e evidência resumida. Depois clarear labels e mover logística para notas. Só então considerar o runtime de apresentador e checar a versão final na resolução do evento.


## Aplicação da revisão · v0.3

O usuário autorizou atualizar o arquivo após a revisão. Alterações aplicadas no mesmo HTML:

- Labels e cabeçalhos maiores, com tokens secundários mais claros; laranja claro nos labels de destaque.
- Visão de produto e slides 7–12 simplificados; roadmap e conversa usam layouts de processo, trilha e perguntas.
- Slide 8 incorpora uma captura histórica real de 28/10 do PR #207, preservada inteira, com callouts e ampliação no próprio deck. Não se apresenta como execução da main atual nem como fixture.
- Slide 9 resume a descoberta MCP realmente executada. Não fabrica uma resposta diagnóstica. Inventário de tools, Ask e PRs ficam no novo apêndice 20.
- Roteiro de demonstração vira quatro passos; condições de ensaio ficam nas notas e limitações materiais continuam visíveis.
- Encerramento protegido: avanço normal para no slide 17; A abre o apêndice e Esc retorna.

[Recibo DOM](2026-11-16-demo-evidence/design-v03-checks.json): nove verificações passaram, incluindo navegação dos 20 slides, hash/contador, guard do encerramento, notas, limites visíveis e integridade da imagem. Para testar o wiring da ampliação, a API nativa de dialog foi substituída por um stub no JSDOM; isso não é teste do modal nativo do navegador.

[Auditoria v0.3](2026-11-16-demo-evidence/design-v03-audit.json): cores, contagens, hash do HTML e origem/integridade da captura. Slide 8 foi conferido renderizado no Firefox. Projeção, PDF, fontes offline e janela separada de apresentador continuam fora da prova. A sugestão de presenter view permanece melhoria futura; esta alteração implementa apenas o acesso deliberado ao apêndice.
