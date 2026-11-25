# Distribuição do Serve — decisão e etapas

Estado: **proposta**, sem build novo, upload, credencial ou publicação nesta complementação. Decisor, executor/revisor de release, canal, nome, versão e data: **a confirmar**.

## Decisão necessária

Escolher distribuição por checkout, pacote único MCP+API ou separação de pacotes; registrar compatibilidade, dependências, entrypoints e versão. A proposta de pacote único é simples de discutir enquanto ambos compartilham código, mas não é uma decisão aceita. Comparar necessidade de instalação MCP sem API e política de manutenção antes de escolher.

O 404 de `apex-mcp` em PyPI/TestPyPI em 18/10 é captura pontual. Reconferir disponibilidade e titularidade antes de escolher nome; 404 não reserva nome e não demonstra que nunca houve publicação.

## Etapas independentes

| Etapa | Trabalho | Evidência de conclusão | Dependências reais |
|---|---|---|---|
| A. Artefato local | Build wheel/sdist; verificar metadata/conteúdo; instalar o artefato em ambiente limpo com dependências controladas | Hash dos arquivos, revisão, conteúdo instalado, entrypoints, importabilidade e smokes acordados | Escopo do pacote, ambiente e versões definidos; sem upload |
| B. Ensaio TestPyPI | Publicar artefato de ensaio no índice escolhido; instalar versão exata e conferir página/metadata | URL do índice, versão, hash, comandos e recibo de instalação/smokes | Conta/identidade/permissões e autorização do release; índices não devem ser misturados implicitamente |
| C. PyPI | Publicação acordada e instalação da versão exata fora do checkout | URL e versão pública, hash, proveniência e recibo | Nome/versão/canal ratificados, critérios de A/B satisfeitos conforme política adotada |

A fase local deve conferir `apex_mcp` e, se incluída, `apex_api`, os scripts publicados e o conteúdo esperado. A contagem de oito tools é a do snapshot; o critério precisa seguir o contrato efetivo da versão. API health, descoberta stdio e consulta com fixture são provas distintas. Evitar teste que passe por importar o checkout em vez do wheel.

Para ensaio, planejar resolução de dependências e índices explicitamente. Não recomendar `--extra-index-url` como escolha automática nem esconder a origem dos pacotes. Credenciais e permissões não são geradas pelo documento.

## Política de release a combinar

- Identidade de publicação e ambiente de release; avaliar Trusted Publishing conforme documentação oficial vigente quando configurar.
- Revisão/commit, tag e versão correspondentes ao artefato; critérios para iniciar publicação e quem os ratifica.
- Instalação e instruções por cliente atualizadas na versão publicada; coordenar README com #164.
- Critério de rollback/yank e nova versão, com limitações registradas; não presumir substituição de artefato já publicado.

A distribuição pode ser estudada em paralelo ao Ask. A publicação não depende automaticamente de aprovar N11 ou adotar outra arquitetura; depende do contrato e do pacote que o time escolher. Este documento não altera nenhuma política de segurança ou release existente.

## Conclusão

Decisão concluída quando escopo/canal/nome/versão, responsável/revisor e critérios estiverem registrados. Release concluído somente com os recibos das etapas efetivamente executadas. Rastrear as tarefas L1 correspondentes na [matriz](MATRIZ-L1-23.md), sem marcá-las `done` por existir esta proposta.
