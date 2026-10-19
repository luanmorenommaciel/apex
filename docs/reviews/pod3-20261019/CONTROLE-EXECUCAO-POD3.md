# Controle de execução documental

Data: 19/10/2026. Escopo: oito lacunas da documentação do Pod 3, com rastreabilidade das 16 minutas. Fonte pública principal: [#181](https://github.com/luanmorenommaciel/apex/issues/181). Decisões de arquitetura e compromissos humanos aguardam o time.

| Etapa | Entrega | Estado verificável | Dependência restante |
|---|---|---|---|
| P0 | Índice, quadro e fontes | Produzidos neste pacote | Manter estado após publicação/discussão |
| P1 | Matriz L1 | 23 IDs únicos, 2 done/accepted:true e 21 ready/accepted:false, com código/evidência/destino | Ratificar destinos e alterações de status por item |
| P2 | Governança e sintaxe | Regra proposta; seis divergências legadas conferidas; três YAML corrigidos e parseados | Review da correção e ratificação da regra |
| P3 | ADR-004 | Cinco decisões com alternativas, impacto, recomendação e campo de resultado | Decisor registrar respostas/status |
| P4 | Ask | Três alternativas e critérios comparativos preparados | Decisão #122 e coerência com #171 |
| P5 | Evidências | Inventário por tool/superfície/caso/árvore, limites e fila de lacunas | Provas futuras acordadas e reconciliação pós-integração |
| P6 | Minutas e ata | Dezesseis minutas roteadas; sete antes ausentes incluídas; modelo de ata pronto | Confirmar destinos, papéis e prazos |
| P7 | Discussão/decisões | PENDENTE — ata preenchível, sem reunião ou compromisso inventado | Participantes e responsáveis registrarem resultado |
| P8 | Clientes/distribuição | Guia com fontes oficiais, exemplos e troubleshooting; proposta de release por etapas | Validação operacional por cliente e decisão de release |
| P9 | Resumo/diagrama | Entrada curta, diagrama e descrição textual preparados | Atualização após decisões reais |
| P10 | Publicação | Preparação e conferência local concluídas; consultar recibo para estado público final | Review dos rascunhos e registros específicos após ratificação |

## Cobertura das oito lacunas

1. L1 por item → MATRIZ-L1-23.md / JSON / CSV.
2. Alternativas Ask → DECISAO-ASK-122.md.
3. Evidência unificada → MATRIZ-EVIDENCIAS-SERVE.md.
4. Decisões e compromissos → ATA-POD3-MODELO.md e este controle.
5. Privacidade N07 → DECISAO-ADR-004.md.
6. Governança N09 e YAML → GOVERNANCA-TASK-SPECS.md e CORRECOES-YAML.md.
7. Onboarding e release → GUIA-CLIENTES-SERVE.md e DECISAO-DISTRIBUICAO.md.
8. Entrada curta e fluxo → LEIA-PRIMEIRO-POD3.md.

## Critérios de fechamento

**Documentação preparada:** os oito complementos existem, links resolvem, propostas/limites são explícitos e os 23 IDs não têm duplicação. **Publicação:** URL acessível e leitura de volta conferida. **Decisão:** resultado factual com responsável/data no objeto específico. **Implementação/merge/release:** critérios próprios. Estes estados não são intercambiáveis.

As cinco PRs já abertas seguem em revisão; a documentação não cria gate geral sobre elas. Um bloqueio técnico, uma decisão pendente e uma sugestão permanecem distintos. O recorte não declara encerrados os 525 IDs da auditoria ampla.
