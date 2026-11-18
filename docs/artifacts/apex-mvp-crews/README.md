# Apex — apresentação de MVP para as crews

**Versão final · 18/11/2026 · após o weekly de 17/11.** Cerca de 40 min com demo (40–50 min com perguntas). Apresentam Sidymar (abertura e MCP) e Agmar (demo da UI).

O plano, a checagem e a revisão visual abaixo são registros da v0.3 (16/11) e foram mantidos como histórico.

[Apresentação HTML](2026-11-09-apresentacao-mvp-deck.html) · [Plano e roteiro](2026-11-04-apresentacao-produto-crews.md) · [Evidências e limites da demo](2026-11-16-demo-readiness.md)

## Abrir e apresentar

Baixe o arquivo HTML e abra no navegador. Ele contém os estilos, o runtime, o logo e a captura do console incorporados: pode ser compartilhado como um único arquivo. As fontes do Google são opcionais; sem conexão, o navegador usa as fontes de fallback. O GitHub mostra o código-fonte, não executa a apresentação.

Com o repositório clonado, também é possível servir a pasta:

```sh
python3 -m http.server 8765 --directory docs/artifacts/apex-mvp-crews
```

Abra `http://localhost:8765/2026-11-09-apresentacao-mvp-deck.html`.

- **← / → / Espaço:** navegar. O encerramento permanece no slide 16.
- **A:** abrir o apêndice ou voltar ao encerramento. **Esc:** voltar do apêndice ou fechar a ampliação da imagem.
- **N:** notas na mesma janela. Feche as notas antes de compartilhar a tela com a plateia.
- **F:** tela cheia. **Home / End:** primeiro / último slide físico, incluindo apêndices.
- Clique na captura do console para ampliá-la.

A apresentação tem **16 slides principais** (contador 1–16) e **três apêndices** (Apêndice 1–3). A barra de progresso acompanha a seção atual.

## O que o material demonstra

A demo segue o fluxo completo proposto pelo Agmar: geração dos jobs, Spark History, query no ClickHouse e o mesmo job no Console. O plano B é a navegação com **fixtures** e finding de SPILL, conferida em 16/11. O status do MCP (cerca de metade das funcionalidades da UI, meta de paridade) é relato do weekly de 17/11, não uma medição. A captura do console é **histórica, de 28/10**, em uma integração local de branches registrada no PR #207; não é uma execução da main atual. A checagem MCP de 16/11 confirma initialize e descoberta de tools, sem executar diagnóstico.

Integração real, cliente MCP, baseline, gravação de backup e ensaio coletivo continuam a preparar. Verify não demonstra uma correção executada ou ganho de performance. O material não aprova os PRs de implementação.

## Revisão e verificações

- [Revisão visual e alterações aplicadas](2026-11-16-design-review-html-ppt.md).
- [Recibo de navegação da versão final](2026-11-16-demo-evidence/design-final-checks.json) · [recibo da v0.3](2026-11-16-demo-evidence/design-v03-checks.json).
- [Auditoria atual e proveniência da imagem](2026-11-16-demo-evidence/design-v03-audit.json).
- [Descoberta MCP](2026-11-16-demo-evidence/mcp-discovery.json).

Para repetir as nove verificações DOM, use as dependências já declaradas em `front/`:

```sh
cd front
npm ci
cd ..
node docs/artifacts/apex-mvp-crews/validate-deck.mjs
```

O comando não modifica os recibos por padrão. Para gravar um novo recibo, acrescente `--write-receipt` e revise a mudança. O teste usa JSDOM; a API nativa de dialog é substituída por um stub para verificar o wiring de eventos. Não certifica pixels, modal nativo, projeção, PDF, fontes offline ou a integração real do Apex.

A auditoria `design-audit.json` preserva a revisão da v0.2; `design-v03-audit.json` e `design-v03-checks.json` se referem à v0.3; `design-final-checks.json` se refere à versão final. O SHA-256 do HTML nos recibos permite verificar a correspondência do artefato.
