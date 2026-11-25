# [Decision][Governança] Definir política de dependências e alertas de segurança

## Intenção e benefício
Decidir como o repositório acompanha vulnerabilidades e atualizações de dependências, com severidade mínima e responsável pela triagem, separado da proteção da main.

## Evidência e limite
A árvore da main `c3c3ea3` não tem `.github/dependabot.yml` nem `CODEOWNERS`; `.github/workflows` tem só `ci.yml` e `jar.yml`, e o job do Front roda `npm ci`, typecheck, lint, test e build, sem etapa explícita de `npm audit` ([ci.yml](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/.github/workflows/ci.yml#L36-L61)). Se os alertas do Dependabot estão ligados nas configurações do repositório não aparece na árvore e não foi verificado. Nenhuma vulnerabilidade foi demonstrada nesta revisão.

## Escopo e conexões
Alternativas: só alertas, sem gate; atualizações automáticas por ecossistema usado no repositório (npm no Front, Python nas lanes, sbt no JAR); audit na CI com limiar e lista de exceções versionada. Definir quem faz a triagem. A escolha de CODEOWNERS e de checks obrigatórios continua na #125.

## Entrega e critérios de conclusão
- [ ] Decisão registrada (alertas, atualizações automáticas, audit), com severidade mínima e responsável pela triagem.
- [ ] Se houver gate na CI, regra de exceção versionada e comportamento por tipo de PR coerente com a #125.

## Como contribuir
Comente o recorte que pretende assumir antes de começar. Mudanças de política precisam da decisão do mantenedor.

## Referências
- [.github/workflows/ci.yml](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/.github/workflows/ci.yml)
- #125, #130

Rastreabilidade do backlog: E15.
