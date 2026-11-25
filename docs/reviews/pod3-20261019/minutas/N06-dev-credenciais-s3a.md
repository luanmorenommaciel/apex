# [Study][Pod 2 / Infra] Definir a fronteira de credenciais S3A do perfil dev

## Intenção e benefício
Levantar qual credencial S3A o Spark do perfil dev usa em cada combinação (dev puro, overlay do pacote) e, com esse mapa, decidir se o conf continua com a credencial padrão do MinIO de laboratório ou passa a ler a mesma fonte de segredo que o pacote já exige.

## Evidência e limite
[dev/conf/spark-defaults.conf:13-14](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/dev/conf/spark-defaults.conf#L13-L14) fixam `spark.hadoop.fs.s3a.access.key` e `spark.hadoop.fs.s3a.secret.key` com o valor padrão do laboratório, sem mudança desde 23/07. O overlay [dev/docker-compose.package.yml:7-9](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/dev/docker-compose.package.yml#L7-L9) exige `APEX_S3_ACCESS_KEY_FILE` e `APEX_S3_SECRET_KEY_FILE`. Não foi verificado qual valor o Spark usa quando o overlay está ativo; esta issue não alega falha nem exposição de segredo. É configuração de laboratório local. A #55, destino anterior do tema, está encerrada.

## Escopo e conexões
Alternativas: manter o literal, documentado como credencial de laboratório; ler de variável ou arquivo, com default só no dev puro; exigir configuração explícita, o que quebra o dev sem setup. Não altera o Compose de infra nem a rotação da credencial do ClickHouse (#176).

## Entrega e critérios de conclusão
- [ ] Mapa de qual fonte de credencial vale em cada perfil (dev puro, pacote).
- [ ] Decisão do owner de Infra, com o efeito no dev sem configuração.
- [ ] Se houver mudança, teste da configuração renderizada sem imprimir valores.

## Como contribuir
Comente o recorte que pretende assumir antes de começar. Não use credenciais reais em testes, logs ou comentários.

## Referências
- [dev/conf/spark-defaults.conf](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/dev/conf/spark-defaults.conf#L13-L14)
- [dev/docker-compose.package.yml](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/dev/docker-compose.package.yml#L1-L12)
- #176

Rastreabilidade do backlog: E12.
