# Pod 2 / Engine

Versão de 20/10/2026. Minha visão para discussão do time.

## 1. Pod 2 / Engine

Esta é minha leitura para contribuir com o planejamento do time. Autoria da base compartilhada e limites das provas permanecem explícitos. O corte documental foi reconferido em 20/10/2026, com main c3c3ea3. Não representa liberação de release nem decisão oficial do pod.

Fontes: https://github.com/luanmorenommaciel/apex/issues/190 ; https://github.com/luanmorenommaciel/apex/blob/faf8b5723abd7cd0905137e574d515216f74d287/docs/reviews/pr-revalidation-20261019/README.md

## 2. Engine e interfaces do projeto

O catálogo distingue autor da PR, autor de commit e quem fez o merge. #52 e #54 foram encerradas sem merge e não entram como entregas integradas. A #185 não transfere autoria ao Pod 2. A atualização da matriz na #121 é de Luan.

Fontes: https://github.com/luanmorenommaciel/apex/blob/db2703c36e407883b610bdf0ed7fdef1dd689835/docs/reviews/pod2-handoff-20261019/ENTREGAS-E-AUTORIA.md ; https://github.com/luanmorenommaciel/apex/pull/185

## 3. Minhas contribuições no núcleo do Engine

O resolvedor #126 não entrega sozinho consumidor público da #115. O gate #127 mantém os critérios específicos da #123. #131 detecta incompatibilidade, não provisiona outro database. #139 retirou job_id e attributes das exclusões, sem remover a allowlist inteira.

Fontes: https://github.com/luanmorenommaciel/apex/blob/db2703c36e407883b610bdf0ed7fdef1dd689835/docs/reviews/pod2-handoff-20261019/ENTREGAS-E-AUTORIA.md ; https://github.com/luanmorenommaciel/apex/blob/db2703c36e407883b610bdf0ed7fdef1dd689835/docs/reviews/pod2-handoff-20261019/EXEMPLOS-ANTES-E-DEPOIS.md

## 4. Exemplos: diagnóstico com contexto fiel

As alterações já integradas não foram reexecutadas para esta apresentação. Os contracasos do resolvedor devem ser reutilizados quando um consumidor for escolhido. Preflight e teste estático não demonstram compatibilidade do DDL instalado em todo ambiente.

Fontes: https://github.com/luanmorenommaciel/apex/blob/db2703c36e407883b610bdf0ed7fdef1dd689835/docs/reviews/pod2-handoff-20261019/EXEMPLOS-ANTES-E-DEPOIS.md

## 5. Minhas contribuições nas interfaces

O plano único do dispatcher na #128 explicita Handler/Command. DryRun compara um plano, mas não prova execução do Command. O residual continua na #124. A #147 mantém os limites do parser e não prova replay completo de todo DDL.

Fontes: https://github.com/luanmorenommaciel/apex/blob/db2703c36e407883b610bdf0ed7fdef1dd689835/docs/reviews/pod2-handoff-20261019/ENTREGAS-E-AUTORIA.md ; https://github.com/luanmorenommaciel/apex/issues/124

## 6. A guarda aberta na #155

A revisão estática não depende de benchmark, browser ou decisão global de infraestrutura. A causa de um check falho exige ler o job e seu alcance. Não declarar defeito de código apenas pela conclusão failure. Os recibos do corte estão no estudo.

Fontes: https://github.com/luanmorenommaciel/apex/pull/155 ; https://github.com/luanmorenommaciel/apex/issues/154 ; https://github.com/luanmorenommaciel/apex/blob/db2703c36e407883b610bdf0ed7fdef1dd689835/docs/reviews/pod2-handoff-20261019/DECISOES-E-PLANO.md ; https://github.com/luanmorenommaciel/apex/blob/faf8b5723abd7cd0905137e574d515216f74d287/docs/reviews/pr-revalidation-20261019/README.md

## 7. A contribuição do Agmar na #185

A contribuição é do Agmar/Pod 3 e precisa ser reaproveitada antes de criar implementação paralela. Os resultados são relatos do autor não reproduzidos nesta auditoria. Credenciais literais de Spark foram removidas, mas defaults locais MinIO continuam documentados. Não inferir incidente ou equivalente pleno entre PowerShell e Bash.

Fontes: https://github.com/luanmorenommaciel/apex/pull/185 ; https://github.com/luanmorenommaciel/apex/blob/db2703c36e407883b610bdf0ed7fdef1dd689835/docs/reviews/pod2-handoff-20261019/README.md ; https://github.com/luanmorenommaciel/apex/blob/faf8b5723abd7cd0905137e574d515216f74d287/docs/reviews/pr-revalidation-20261019/README.md

## 8. Encaminhamentos pequenos para revisão

Preservar os critérios #174 e #178 separados ao comparar runners. Para #124, handlers inofensivos e controle negativo permitem desenhar teste sem operar stack. A revisão deve indicar revisor, saída e retorno a combinar.

Fontes: https://github.com/luanmorenommaciel/apex/blob/db2703c36e407883b610bdf0ed7fdef1dd689835/docs/reviews/pod2-handoff-20261019/DECISOES-E-PLANO.md

## 9. Decisões e oportunidades do Engine

Não enfraquecer silenciosamente um critério para encerrar uma issue. O launcher não prova overhead. Nome fixo de container não prova propriedade. Escolher um consumidor ou uma garantia por vez permite manter as entregas pequenas e verificáveis.

Fontes: https://github.com/luanmorenommaciel/apex/blob/db2703c36e407883b610bdf0ed7fdef1dd689835/docs/reviews/pod2-handoff-20261019/PERGUNTAS-DE-DECISAO.md ; https://github.com/luanmorenommaciel/apex/blob/db2703c36e407883b610bdf0ed7fdef1dd689835/docs/reviews/pod2-handoff-20261019/IDEIAS-E-BACKLOG.md

## 10. Onde o time pode verificar

O catálogo relaciona 30 objetos atuais e 133 fichas originais. Isso não representa 133 entregas do Pod 2 nem uma soma de testes independentes. Responsáveis e datas ainda dependem de acordo real. Os pacotes documentais permanecem em rascunho no corte.

Fontes: https://github.com/luanmorenommaciel/apex/issues/190 ; https://github.com/luanmorenommaciel/apex/pull/189 ; https://github.com/luanmorenommaciel/apex/pull/186 ; https://github.com/luanmorenommaciel/apex/blob/faf8b5723abd7cd0905137e574d515216f74d287/docs/reviews/pr-revalidation-20261019/README.md
