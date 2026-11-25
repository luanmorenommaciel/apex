# Destinos das 16 minutas

Estado documental, não aprovação de implementação. As nove propostas N03/N05/N10–N16 já estão públicas nos anexos da [#181](https://github.com/luanmorenommaciel/apex/issues/181). Os destinos abaixo evitam criar trackers duplicados; responsáveis e datas continuam a confirmar.

| Minuta | Tema / registro principal proposto | Próxima ação | Estado |
|---|---|---|---|
| N01 | Verify p50/noise_floor, relação #117 | Revisor Verify confrontar contrato e decidir complemento específico | Minuta preparada; decisão pendente |
| N02 | Brief VERIFY.md e lanes | Responsável Verify escolher atualização documental pequena | Minuta preparada; destino específico a confirmar |
| N03 | Projeção fix_verifications, #117 | Considerar critério adicional sem alegar incidente de runtime | Já pública na #181; incorporação pendente |
| N04 | Política de dependências | Mantenedor/CI escolher tracker transversal e critérios, com vínculo à distribuição | Minuta preparada; destino específico a confirmar |
| N05 | Compare entre versões Engine | Serve/Engine decidir estudo, adiamento ou rejeição | Já pública na #181; prioridade pendente |
| N06 | Credenciais S3A dev | Infra/Engine delimitar fronteira; separar de token da API | Minuta preparada; destino específico a confirmar |
| N07 | ADR-004 | [Registro das cinco decisões](DECISAO-ADR-004.md); atualizar ADR somente após ratificação | Complemento preparado; decisão pendente |
| N08 | CI Ubuntu 26.04 | Mantenedor conferir ferramentas e escolher acompanhamento/recuo | Complemento temporal conferido abaixo |
| N09 | Status/aceite Task-Specs | [Governança](GOVERNANCA-TASK-SPECS.md) e três YAML em correção própria | Complemento e correção preparados; ratificação pendente |
| N10 | Contradição list_runs em SERVE-LEGS | Coordenar com #164 e abrir mudança documental mínima se necessário | Já pública na #181 |
| N11 | MCP direto versus via API | Estudo Serve; alternativa não ratificada, diferente do Ask | Já pública na #181 |
| N12 | Recall com configuração desconhecida no run lento | Serve conferir atribuição e limites antes de escolher correção | Já pública na #181 |
| N13 | Limpeza do read_only_gate após falha de asserção | Serve decidir política e controle discriminante; não transferir limpeza da #159 | Já pública na #181 |
| N14 | Normalização de timestamps inválidos | Pods 1 e 3 delimitar domínio e paridade como estudo | Já pública na #181 |
| N15 | Oráculo de custo da Console, complemento #156 | Vincular prova de custo ao job selecionado; não criar tracker duplicado | Já pública na #181 |
| N16 | Contrato do gate stdio | Reconciliar sete nomes listados e oito registradas, preservando controle discriminante | Já pública na #181; execução pendente |

Os títulos exatos e critérios completos estão no texto integral de cada minuta; a tabela é roteamento. Nenhuma linha atribui trabalho a pessoa sem combinação.

## N08 — atualização temporal em 19/10/2026

O [changelog oficial do GitHub](https://github.blog/changelog/2026-09-17-ubuntu-26-generally-available-and-latest-migration/) informa rollout de `ubuntu-latest` de 19/10 a 19/11/2026. Isso não é prazo do APEX e não comprova que um job do projeto já usou a nova imagem.

A minuta registra `ci.yml` e `jar.yml` com `ubuntu-latest`. Encaminhamento: inventariar Node, uv/Python, PowerShell, Docker/Collector e JDK por job, distinguindo setup explícito de ferramenta da imagem; escolher acompanhar, pin temporário com revisão, ou migração gradual. Na próxima execução pertinente registrar OS, ImageVersion e versões. Não há execução nova ou mudança de runner nesta documentação.

## Visibilidade entre pods

Leitura Serve: L1/Ask/#156/#171/#172. Front: contrato, same-origin e experiência de browser. Engine/Verify: grafo/schema, compare, Verify e ADR. Infra/CI: credenciais, distribuição e runner. Preparar aviso contendo link, impacto, decisão/revisão necessária e prazo apenas quando combinado.
