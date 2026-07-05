# ADR-005: SparkListener In-Process vs Zero-JAR Event Log para V1

**Status:** Accepted  
**Data:** 04/07/2026  
**Deciders:** Luan Moreno (Commander) · Augusto Cezar (Captain)  
**Contexto da decisão:** Reunião 30/06/2026 — Luan, Augusto, Jaime, Aguimar  
**Supersede:** Princípio zero-JAR documentado em `CLAUDE.md` (v3)

---

## Contexto

O Apex v3 (estado atual) opera com uma premissa central documentada no `CLAUDE.md`:

> *"Zero JAR injetado no cluster — Zero modificação de SparkSession"*

Essa abordagem lê event logs **após** a execução do job via MinIO REST, sem nenhum contato com o processo Spark em execução.

Na reunião de 30/06/2026, o Commander Luan apresentou uma nova arquitetura para a **V1** do Apex centrada em 5 componentes:

```
Spark Envy → SparkListener → ClickHouse → Crew.ai → MCP
```

O SparkListener captura métricas **durante** a execução do job (in-process), comunicando-se em tempo real com o ClickHouse. Isso contradiz diretamente o princípio zero-JAR da v3.

Aguimar confirmou na reunião que os passos 1–3 (Spark Envy + SparkListener + ClickHouse) já funcionam em sua branch. O ponto de tensão precisa ser resolvido formalmente para que o time avance sem ambiguidade.

---

## Decisão

**Para a V1 do Apex: adotar SparkListener in-process.**

O zero-JAR permanece como abordagem válida para diagnóstico pós-mortem (Mundo A), mas deixa de ser o caminho principal de captura de dados. A V1 constrói sobre SparkListener (Mundo B) com entrega via MCP.

---

## Opções Consideradas

### Opção A: Zero-JAR Event Log (abordagem atual, v3)

| Dimensão | Avaliação |
|---|---|
| Intrusividade | Nenhuma — leitura pós-job via MinIO |
| Latência do diagnóstico | Alta — só disponível após o job terminar |
| Dados disponíveis | Event log completo: stages, tasks, AQE, SQL |
| Complexidade de deploy | Baixa — sem modificação no cluster |
| Testes existentes | 40 testes passando no plat-v0 |
| Similaridade com DataFlint | Baixa — DataFlint usa in-process |

**Prós:**
- Não-intrusivo: nenhum risco de interferir no job
- Já funciona — 40 testes verdes, oracle validado
- Compatível com qualquer ambiente Spark (serverless, on-prem, cloud)
- Não requer acesso ao processo Spark em execução

**Contras:**
- Diagnóstico sempre pós-mortem — engenheiro recebe o resultado depois que o job morreu
- Não permite intervenção em tempo real
- MinIO polling adiciona latência e complexidade de infra
- Não alinha com a visão de experiência interativa que o Luan quer

---

### Opção B: SparkListener In-Process (decisão V1)

| Dimensão | Avaliação |
|---|---|
| Intrusividade | Média — requer `spark.extraListeners` no job |
| Latência do diagnóstico | Baixa — dados chegam em tempo real |
| Dados disponíveis | Stage metrics, task counts, spill, executor utilization |
| Complexidade de deploy | Média — listener precisa estar no classpath |
| Testes existentes | Branch do Aguimar tem passos 1–3 funcionando |
| Similaridade com DataFlint | Alta — mesma abordagem fundamental |

**Prós:**
- Dados em tempo real → diagnóstico disponível logo após o job terminar
- Base para futura intervenção durante execução (visão de longo prazo do Luan)
- Alinha com a experiência que o Luan quer: "o job rodou, eu tenho o ID, debuga pra mim"
- Aguimar já tem a implementação funcional — não part do zero
- Extensível para alertas em tempo real, DAG visualization, replay

**Contras:**
- Requer modificação na config do Spark (`spark.extraListeners` ou `spark-submit --conf`)
- Exception no listener pode impactar o job se não houver fail-safe
- Dependência de py4j para Python ↔ JVM
- Reduz diferenciação em relação ao DataFlint no nível de captura (embora o diagnóstico agentic continue diferenciando)

---

### Opção C: Híbrido (SparkListener + zero-JAR)

SparkListener para captura em tempo real + zero-JAR como fallback quando listener não disponível.

**Prós:** cobre ambos os mundos  
**Contras:** duplica a complexidade, aumenta a superfície de manutenção, confunde o foco da V1

**Descartada para V1** — pode ser reconsiderada em V2 quando ambas as abordagens estiverem maduras separadamente.

---

## Análise de Trade-offs

O ponto central da decisão é **experiência vs intrusividade**.

O zero-JAR garante que o Apex nunca toque no cluster do cliente — isso tem valor real em ambientes regulados ou onde o time de infra não dá acesso. Mas impede a experiência que o Luan quer: feedback rápido, interativo, no IDE.

O SparkListener sacrifica alguma intrusividade em troca de latência muito menor no diagnóstico. O risco de impacto no job existe, mas é mitigável com fail-safe (exception no listener não propaga para o job) e com a abordagem `spark.extraListeners` que isola o listener do classpath do job.

A decisão de Luan na reunião (30/jun, linhas 81–99) é clara: SparkListener é o caminho da V1. Aguimar já tem evidência de que funciona.

---

## Consequências

**O que fica mais fácil:**
- Diagnóstico disponível imediatamente após o job (sem esperar polling do MinIO)
- Base para futura UI de visualização de DAGs e replay de jobs
- Alinhamento com a arquitetura que o time inteiro está implementando

**O que fica mais difícil:**
- Deploy em ambientes serverless (ex: Databricks serverless, onde não se controla o Spark config)
- Clientes com restrições de classpath ou políticas de zero-modificação
- Manutenção de dois mundos (se zero-JAR se mantiver vivo para cenários específicos)

**O que precisamos revisitar em V2:**
- Suporte a ambientes sem acesso ao `spark.extraListeners` (zero-JAR como fallback)
- Decisão sobre Crew.ai vs Anthropic API direto para o diagnóstico
- On-premise mode (levantado pelo Jaime na reunião) — LLM local para clientes sem acesso à nuvem

---

## Impacto nas Issues Ativas

| Issue | Impacto |
|---|---|
| #24 — SparkListener | **Desbloqueada** — pode seguir com abordagem in-process |
| #25 — ClickHouse setup | **Desbloqueada** — schema definido em `v1-skeleton/schema/init.sql` |
| #26 — Crew.ai | **Desbloqueada** — pode receber dados do SparkListener |
| #27 — ADR-005 | **Resolvida** por este documento |

---

## Itens de Ação

- [x] Formalizar a decisão neste ADR
- [ ] Adicionar fail-safe no `spark_listener.py`: exception no listener não propaga para o job
- [ ] Validar `spark.extraListeners` no cluster do plat-v0 (Aguimar)
- [ ] Atualizar `CLAUDE.md` para refletir a nova arquitetura V1 (sem remover menção ao zero-JAR como opção futura)
- [ ] Comentar na issue #27 com link para este ADR

---

*Autoria: Claude Sonnet 4.6 (Cowork) · Revisão: Augusto Cezar · Aprovação pendente: Luan Moreno*
