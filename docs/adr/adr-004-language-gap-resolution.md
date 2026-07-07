# ADR-004: Resolução do Gap de Linguagem — Go vs. Python

> **Status:** Proposed  
> **Data:** 2026-07-06  
> **Autor:** Kimi (Augusto Cezar)  
> **Branch:** `gustocezar/feature/kimi-desacoplamento-geradores`  
> **Relacionado:** Issue #8 (ADR-004), Issue #22 (ADR-001 Go Collector)

---

## Contexto

A ADR-004 (Issue #8) decidiu que o **core do Apex seria escrito em Go**, com as seguintes justificativas:

- Go é a linguagem da infraestrutura moderna (OTel Collector, CNCF)
- APIs limpas e idiomáticas; ecossistema maduro para HTTP, gRPC, consumers de filas, DB clients
- Concorrência nativa via goroutines — resolve o problema do GIL do Python
- Alinhado com Docker, Kubernetes, ClickHouse
- Menor barreira de entrada para o time atual (vs. Rust)

**Python foi descartado para o core** por:
- GIL limita concorrência real (problema para Watchers que processam eventos em paralelo)
- Overhead de runtime inadequado para componentes de infraestrutura
- Python faz sentido para scripts de análise, LLM calls e prototipação — não para o core

---

## Problema

O pipeline validado fim a fim na infraestrutura local foi implementado **inteiramente em Python**:

| Componente | Linguagem | Status |
|-----------|-----------|--------|
| Diagnostician (T1) | Python | ✅ Validado |
| EvidenceValidator | Python | ✅ Validado |
| Recommender (T2) | Python | ✅ Validado |
| SpillWatcher | Python | ✅ Validado |
| MCP Server | Python | ✅ Validado |
| Go Loader | Go | ✅ Validado (existe no fork Gabriel) |

**Conflito:** A Crew A decidiu Go para o core, mas o único caminho validado de diagnóstico usou Python. O Go Loader (do Gabriel) existe, mas ele é apenas o **parser/loader** — não é o diagnóstico.

---

## Análise das Opções

### Opção A: Manter Python para V0.1, migrar para Go na V0.2

**Prós:**
- V0.1 pode ser validada e demoed imediatamente
- Time não precisa reescrever código funcionando
- Risco de entrega da V0.1 é zero

**Contras:**
- V0.1 não segue a ADR-004
- GIL pode ser problema em produção com alta taxa de eventos
- Tecnical debt: reescrever T1/T2/T3 em Go posteriormente

### Opção B: Reescrever T1/T2/T3 em Go antes de validar V0.1

**Prós:**
- Alinha com ADR-004 desde o início
- Goroutines resolvem problema de concorrência
- Stack unificada para produção

**Contras:**
- Atrasa V0.1 em semanas (ou meses, dependendo da disponibilidade do time)
- Risco de não entregar nada validado para a próxima reunião
- Perde o momentum da validação atual

### Opção C: Arquitetura Híbrida — Go para infra, Python para diagnóstico

**Prós:**
- Go Loader (parser) já existe no fork do Gabriel
- Python para diagnóstico é rápido de iterar e testar
- Cada linguagem no seu domínio: Go para throughput, Python para lógica de diagnóstico

**Contras:**
- Duas linguagens no mesmo projeto aumentam complexidade de operação
- Comunicação entre Go e Python precisa de contrato (HTTP/gRPC/MCP)
- Não resolve o GIL do Python no diagnóstico

### Opção D: Python com AsyncIO/Multiprocessing para V0.1

**Prós:**
- Mantém Python (código existente)
- AsyncIO pode mitigar GIL para I/O bound (ClickHouse queries)
- Multiprocessing para CPU bound (skew detection)

**Contras:**
- Ainda não é Go
- AsyncIO + ClickHouse driver pode ter edge cases
- Complexidade adicional no código Python

---

## Proposta de Resolução

> **Recomendação: Opção A + C (Híbrida com Python-first para V0.1)**

### Decisão Proposta

1. **V0.1 usa Python para o pipeline de diagnóstico** (T1/T2/T3 heurístico)
   - O código já existe, já foi validado, e pode ser demoed
   - O foco da V0.1 é **provar o conceito fim a fim**, não otimizar para produção

2. **Go Loader (do Gabriel) é mantido como infraestrutura de parsing**
   - Ele já funciona e converte event logs para ClickHouse
   - Não precisa ser reescrito

3. **ADR-004 é reescrita para refletir:**
   - **V0.1:** Python para diagnóstico (prototipação, validação, iteração rápida)
   - **V0.2+:** Go para core de produção (quando throughput e concorrência forem críticos)
   - **Long-term:** Go para infraestrutura, Python para orquestração de LLM (CrewAI, etc.)

4. **MCP Server como ponte de linguagem**
   - O MCP Server é a interface entre o diagnóstico (Python) e o mundo externo
   - Quando o core migrar para Go, o MCP Server pode ser reescrito em Go sem mudar o contrato

---

## Justificativa

A decisão de Go para o core foi **estratégica e correta** para o longo prazo. Porém:

- A V0.1 tem como objetivo **validar o conceito** e **dar uma demo funcional**
- Reescrever código funcionando em Go atrasaria a V0.1 sem agregar valor de validação
- Python é a linguagem nativa da Crew AI (CrewAI, LangChain, etc.)
- O Go Loader já prova que Go é viável para infraestrutura
- A migração para Go pode ser feita **depois** que o contrato e o algoritmo estiverem maduros

> **Analogia:** Kubernetes foi escrito em Go, mas os primeiros protótipos de muitos sistemas de orquestração usavam Python. A linguagem de protótipo não invalida a decisão de linguagem de produção.

---

## Consequências

### Positivas
- V0.1 entregável e demoável em dias, não semanas
- Time pode focar em validar o diagnóstico, não em reescrever código
- Python permite iteração rápida nos algoritmos de detecção
- Go Loader já prova a infraestrutura

### Negativas / Trade-offs
- V0.1 não segue a ADR-004 original (aceitável para protótipo)
- GIL do Python pode ser gargalo em produção (mitigado com AsyncIO + Multiprocessing)
- Técnical debt: migração para Go precisa ser planejada
- Crew A precisa ter skills em Python + Go (ou dividir pods por linguagem)

---

## Próxima Ação

- [ ] Commander (Luan) validar se Python é aceitável para V0.1
- [ ] Se aprovado, atualizar ADR-004 com a decisão de linguagem por fase
- [ ] Criar roadmap de migração Go para V0.2 (sem compromisso de data)
- [ ] Documentar contrato MCP para que a migração seja transparente
- [ ] Avaliar se AsyncIO + Multiprocessing mitiga GIL para o volume esperado

---

## Alternativas Descartadas

| Alternativa | Motivo |
|-------------|--------|
| Rust para core | Barreira de entrada muito alta para o time atual |
| Java/Scala para core | Overhead de JVM; não alinhado com stack OTel/CNCF |
| Elixir/Erlang para core | Ninguém no time tem experiência |

---

*ADR proposta para validação da Crew A. Não substitui a ADR-004 original até aprovação do Commander.*
