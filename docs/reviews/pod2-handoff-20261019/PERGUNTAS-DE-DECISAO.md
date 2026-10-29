# Perguntas de decisão — uma escolha por registro

Alternativas e recomendações para discussão; nenhum item abaixo está ratificado. Responsáveis e prazos não foram nomeados pelo auditor. Aceitar uma arquitetura não encerra automaticamente todas as provas que dela dependem.

## Primeiro consumidor de atribuição

- **Onde registrar:** Issue #115.
- **Alternativas:** Selecionar um consumidor público; ou adiar a integração com critério de retomada.
- **Recomendação para discussão:** Reutilizar o resolvedor #126 e seus contracasos; não impor três PRs ou remoção global de sentinelas.
- **Se adiar:** O resolver integrado continua disponível, mas não equivale à integração completa do consumidor.
- **Quem precisa participar:** Engine e consumidor escolhido, a confirmar.
- **Resultado a escrever:** Consumidor, identidades, caso SQL/RDD e critério público pertinente.

## Garantia necessária do tail-outlier

- **Onde registrar:** Issue #123.
- **Alternativas:** Conferir o critério público e provar a associação requerida; ou propor revisão explícita de escopo se o time escolher outra garantia.
- **Recomendação para discussão:** Preservar runtime histórico e distinguir vínculo por job de vínculo stage/tentativa/snapshot.
- **Se adiar:** Sem decisão/prova, não encerrar por semelhança de texto ou por runner melhorado na #185.
- **Quem precisa participar:** Engine, Package e mantenedor do critério, a confirmar.
- **Resultado a escrever:** Garantia acordada e controle discriminante, sem enfraquecer silenciosamente a issue.

## Protocolo de overhead

- **Onde registrar:** Issue #113.
- **Alternativas:** Definir desenho mínimo versionado; ou adiar a medição e a alegação de performance.
- **Recomendação para discussão:** Separar launcher/binding da interpretação da medição; declarar warm-up, amostra, estimador, banda e resultados inconclusivos/ausentes.
- **Se adiar:** Melhorias funcionais independentes podem avançar; não afirmar overhead aprovado sem a evidência escolhida.
- **Quem precisa participar:** Engine/Harness e DEV/JAR pertinentes, a confirmar.
- **Resultado a escrever:** Desenho e interpretação; nenhum benchmark é feito nesta entrega.

## Configuração do operador

- **Onde registrar:** Issue #174.
- **Alternativas:** Recusar divergência; comparar e preservar; backup explícito; ou passar EnvFile sem copiar sobre o arquivo.
- **Recomendação para discussão:** Comparar com a interface proposta na #185; scripts/apex.ps1 não é corrigido por ensure_env sozinho.
- **Se adiar:** O caminho Copy-Item -Force continua precisando critério próprio.
- **Quem precisa participar:** Package e operador/DEV, a confirmar.
- **Resultado a escrever:** Política de preservação e controle com arquivo diferente preexistente.

## Identidade e ownership

- **Onde registrar:** Issue #175.
- **Alternativas:** Escolher protocolo por checkout/context/Compose; ou adiar operações que dependam dessa identificação.
- **Recomendação para discussão:** Distinguir próprio, alheio e desconhecido antes das mutações pertinentes.
- **Se adiar:** Nomes fixos de containers não provam propriedade. Estudo pode continuar sem inspecionar recursos.
- **Quem precisa participar:** Package/Infra/DEV e operadores, a confirmar.
- **Resultado a escrever:** Identidades, operações protegidas e controle de recusa.

## Contratos por consumidor

- **Onde registrar:** Issues #169/#170/#173.
- **Alternativas:** Escolher uma fatia de população/tentativa, replay ou database; ou adiar cada uma com motivo.
- **Recomendação para discussão:** Separar os três temas e seus exemplos/recibos; não impor um contrato uniforme por intuição.
- **Se adiar:** Adiar um não bloqueia toda a documentação dos demais.
- **Quem precisa participar:** Engine/Infra/Serve e consumidores pertinentes, a confirmar.
- **Resultado a escrever:** Uma decisão por contrato com hipótese, contracaso e limite.

