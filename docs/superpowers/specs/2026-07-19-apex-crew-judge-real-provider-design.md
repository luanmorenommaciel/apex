# Apex Crew/Judge Real Provider

Data: 2026-07-19

## Objetivo

Criar a primeira implementacao real e plugavel de Crew/Judge para a branch
Codex Round2, sem substituir o caminho T1 deterministico que ja fechou G0-G7.

O Judge entra somente depois de:

```text
event log -> detectores T1 -> EvidenceValidator -> judge_policy
```

Quando `judge_policy` decidir escalonar, a tool `crew_judge_diagnose` monta um
envelope auditavel e chama um provider. O provider padrao e seguro e local; o
provider Crew.ai real so e usado quando a dependencia estiver instalada e
habilitada explicitamente por variavel de ambiente.

## Principios

1. T1 continua obrigatorio e rapido.
2. Crew/Judge nao aplica codigo e nao executa rerun.
3. Crew/Judge precisa citar evidencia existente.
4. Se Crew.ai nao estiver instalado/configurado, o sistema degrada para
   fallback seguro e explicito.
5. Toda decisao deve ser serializavel, testavel e consumivel pelo MCP.

## Contrato

Entrada:

```json
{
  "job_id": "job-42",
  "finding": {},
  "validation": {},
  "policy": {},
  "evidence": {},
  "candidate_recommendations": []
}
```

Saida:

```json
{
  "status": "judged",
  "provider": "deterministic|crew_ai|noop",
  "decision": "confirm_finding|reject_finding|request_more_evidence|manual_review",
  "rationale": "...",
  "cited_evidence": ["..."],
  "recommended_next_action": "recommend_fix|request_more_evidence|manual_review",
  "human_review_required": true,
  "guardrails": ["must_cite_existing_evidence", "must_not_apply_changes_directly"]
}
```

## Providers

### DeterministicJudgeProvider

Provider local e sempre disponivel. Ele usa `judge_policy`, `validation` e
campos do finding para produzir uma decisao conservadora. Esse provider fecha o
contrato e serve como fallback quando Crew.ai nao estiver disponivel.

### CrewAIJudgeProvider

Provider opcional. Ele tenta importar `crewai` dinamicamente e so executa quando
`APEX_CREW_JUDGE_ENABLED=1`. Se a biblioteca ou configuracao estiver ausente,
retorna `status=not_configured` sem falhar o caminho MCP.

Para evitar alucinacao, o prompt/envelope do provider contem apenas evidencias
existentes. A resposta bruta do agente precisa ser parseada para o contrato
acima; se nao bater no contrato, a decisao cai para `manual_review`.

### NoopJudgeProvider

Fallback explicito para ambientes sem Crew.ai. Ele nao finge raciocinio; declara
que o provider real esta indisponivel e recomenda revisao humana.

## Tool MCP

Nova tool read-only:

```text
crew_judge_diagnose(job_id, provider?)
```

`provider` aceita:

- `auto`: tenta Crew.ai habilitado e cai para deterministico;
- `deterministic`: usa provider local;
- `crew_ai`: exige Crew.ai habilitado/configurado;
- `noop`: retorna fallback explicito.

## Criterios De Aceite

- `tools/list` passa a expor `crew_judge_diagnose`.
- A tool e read-only no MCP.
- Provider deterministico retorna contrato completo para um finding real.
- Provider Crew.ai nao e dependencia obrigatoria de teste/CI.
- Quando Crew.ai nao esta habilitado, a resposta declara `not_configured`.
- Testes unitarios cobrem contrato, fallback, MCP tool e anti-alucinacao basica.
- Evidencia crua fica em `evidence/crew-judge-real-provider-2026-07-19.log`.

## Limite Honesto

Este slice cria o caminho real e plugavel de Crew/Judge. Ele nao declara que uma
API LLM externa rodou no ambiente atual, a menos que `APEX_CREW_JUDGE_ENABLED=1`
e as credenciais/modelo estejam configurados. O ganho agora e remover o gap de
arquitetura e contrato, mantendo a execucao real de LLM como opcional auditavel.
