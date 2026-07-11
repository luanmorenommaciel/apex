| ID | Fase/Gate | Tipo | Título | Evidência | Status |
|---|---|---|---|---|---|
| CODEX-001 | F0 | risco | branch já continha o scorecard comparativo da rodada 1 antes do reconhecimento desta rodada | evidência: `docs/architecture/llm-solution-validation-framework-2026-07-09.md` | aberta |
| `#29` | F0/G3 | documentação | atualizar issue #29 com inventário, cobertura, arquitetura e estado validado/observado/proposto | `docs/github-issue-comment-drafts.md` | rascunho |
| CODEX-002 | G2/G3 | tarefa | criar issue formal para validar slice `skew_on_join_30x` v4 corrigido com a Crew A | `docs/github-issue-comment-drafts.md` | aberta |
| `#9` | G2/G3 | tarefa | Data Generator: revisar cenário declarativo, geração sintética e comparação com log real | `docs/github-issue-comment-drafts.md` | rascunho |
| `#16` | L2/G3 | tarefa | Spark History Parser: evoluir parser de event log para além do slice de skew | `docs/github-issue-comment-drafts.md`; `apex/apexlib.py` | rascunho |
| `#17` | G2 | tarefa | Watcher / Classifier / Judger: validar Watcher determinístico e separar o que ainda falta de Classifier/Judger | `docs/github-issue-comment-drafts.md`; `watchers/skew_watcher.py` | rascunho |
| `#19` | L1/L2 | decisão | Local Bootstrap Platform: decidir papel do fork `dataship-spark-plat-v0` como evidência reproduzível | `docs/github-issue-comment-drafts.md` | rascunho |
| `#21` | G0/G6 | tarefa | CI Integration: evoluir gate inicial para múltiplos cenários e integração de revisão | `docs/github-issue-comment-drafts.md` | rascunho |
| `#23` | F0/L7 | decisão | Shadow Repo Governance: separar repo de evidência reproduzível e slice curado no Apex | `docs/github-issue-comment-drafts.md` | rascunho |
| `#25` | F0/L7 | decisão | Commander Attention Governance: validar fluxo repo de evidência -> slice curado -> revisão coletiva | `docs/github-issue-comment-drafts.md` | rascunho |
| `#5` | L8 | decisão | ADR-001 Onde o Apex roda: preservar direção externa/não intrusiva | `docs/github-issue-comment-drafts.md`; `docs/adr-review-drafts.md` | rascunho |
| `#6` | L5/G4 | decisão | ADR-002 Tier 2: usar evidência empírica antes de escalonar para classificador pesado | `docs/github-issue-comment-drafts.md`; `docs/adr-review-drafts.md` | rascunho |
| `#7` | L4 | decisão | ADR-003 Estado histórico: definir campos de Findings e futuro schema histórico no ClickHouse | `docs/github-issue-comment-drafts.md`; `docs/adr-review-drafts.md` | rascunho |
| `#8` | L7 | decisão | ADR-004 Linguagem dos componentes: Python como laboratório/spec executável e Go como possível core futuro | `docs/github-issue-comment-drafts.md`; `docs/adr-review-drafts.md` | rascunho |
| `#22` | L8 | decisão | Go as language for OTel Collector: manter decisão de Collector separada do slice Spark/event log | `docs/github-issue-comment-drafts.md`; `docs/adr-review-drafts.md` | rascunho |
| `#24` | F0/L7 | decisão | Intentional deprioritization: registrar valor de baseline antes de divergência | `docs/github-issue-comment-drafts.md`; `docs/adr-review-drafts.md` | rascunho |
| `#40` | F0 | tarefa | branch/evidence inventory: consolidar comparação de soluções e evidência de branch | `docs/architecture/codex-branch-solution-comparison-2026-07-09.md` | aberta |
| `#38` | L5/L6 | tarefa | CrewAI/MCP por `job_id`: implementar caminho visível de produto | `docs/architecture/codex-branch-solution-comparison-2026-07-09.md` | aberta |
| `#37` | L1/L3/L4 | tarefa | SparkListener/ClickStack MVP: fechar caminho de telemetria de plataforma | `docs/architecture/codex-branch-solution-comparison-2026-07-09.md` | aberta |
| `#41` | L5/L6 | tarefa | contratos agênticos: safety, memória, MCP, RAG e autonomia | `docs/architecture/codex-branch-solution-comparison-2026-07-09.md` | aberta |
| CODEX-003 | L1/L2 | decisão | adotar `spike/apex-v0.1` como platform spine ou rejeitar formalmente | `docs/architecture/codex-branch-solution-comparison-2026-07-09.md` | aberta |
| CODEX-004 | G1/G4 | tarefa | portar Kimi EvidenceValidator e baseline negativo quando necessário ao contrato comum | `docs/architecture/codex-branch-solution-comparison-2026-07-09.md` | aberta |
| CODEX-005 | L6/G5 | tarefa | converter Cowork `apply_fix` para fix guardado preview-first | `docs/architecture/codex-branch-solution-comparison-2026-07-09.md` | aberta |
| CODEX-006 | F0 | tarefa | definir targets de paridade DataFlint: alertas, UI, MCP, comportamento agêntico e segurança | `docs/architecture/codex-branch-solution-comparison-2026-07-09.md` | aberta |
