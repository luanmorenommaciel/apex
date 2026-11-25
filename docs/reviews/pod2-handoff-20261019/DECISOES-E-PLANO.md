# Três encaminhamentos propostos — Pod 2 / Engine e interfaces

Escolher a primeira revisão e confirmar papéis/prazos com o time. Estes são recortes de preparação, não três implementações já autorizadas. Decisões adicionais ficam separadas em [PERGUNTAS-DE-DECISAO.md](PERGUNTAS-DE-DECISAO.md).

## 1. Revisar a guarda de consistência do Engine

- **Tipo:** Revisão sem runtime.
- **Entrada:** PR #155 no head 561b27e e critérios da issue #154, sobre as implementações integradas #131/#139.
- **Entrega pequena:** Parecer da guarda bidirecional e identificação do residual: integração, evidência e/ou atualização do acompanhamento.
- **Concluído quando:** A revisão identifica como coluna omitida ou extra é detectada e qual árvore receberá validação. A issue só será encerrada por decisão sobre seus critérios, não por existir link para a PR.
- **Dependência real:** Revisão estática independe de benchmark, browser ou de decisão global de infraestrutura. Checks do head falhos não demonstram por si uma asserção reprovada.
- **Papel a combinar:** Revisor de Engine e mantenedor, a confirmar.
- **Prazo:** a combinar, depois de confirmar o responsável.

## 2. Confrontar a interface R9D com a contribuição do Pod 3

- **Tipo:** Revisão sem runtime.
- **Entrada:** Critério da issue #167 e PR #185 do Agmar/Pod 3 no head a5c2ca45, antes de abrir variante paralela.
- **Entrega pequena:** Mapa de argumentos ON/OFF, parâmetros aceitos, comando produzido e lacunas remanescentes. Separar os critérios #174 e #178.
- **Concluído quando:** O mapa mostra EnvFile/AdditionalComposeFile em cada braço e propõe um controle que detecte argumento removido. Presença textual de knobs não é equivalência completa; benchmark não é inferido.
- **Dependência real:** Depende da interface candidata escolhida. Não exige resolver todas as políticas antes de comparar código; nenhuma execução de PowerShell é feita nesta revisão.
- **Papel a combinar:** Autores/revisores de Engine, Package/Harness e DEV/Pod 3, a confirmar.
- **Prazo:** a combinar, depois de confirmar o responsável.

## 3. Desenhar um controle seguro do dispatcher PowerShell

- **Tipo:** Preparação sem runtime.
- **Entrada:** Issue #124 e plano de ação integrado da #128: DryRun retorna antes de executar Command.
- **Entrega pequena:** Especificação de teste com handlers inofensivos e controle negativo que troca Command mantendo Handler.
- **Concluído quando:** Explicar por que o teste distingue o rótulo correto do comando realmente selecionado. Limitar efeitos e declarar o que não prova sobre Windows, Docker ou o fluxo E2E.
- **Dependência real:** O desenho não precisa iniciar ações do pacote. Implementar/executar o controle é trabalho posterior sob escopo próprio.
- **Papel a combinar:** Revisor do pacote/PowerShell e representante do Pod 2, a confirmar.
- **Prazo:** a combinar, depois de confirmar o responsável.

## Execução posterior

Testar uma combinação, operar stack, executar navegador ou medir overhead exige o ambiente e o escopo específicos. Preparar um controle não equivale a executá-lo. Registrar somente os resultados realmente obtidos.
