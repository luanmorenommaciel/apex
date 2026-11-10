# Ideias, backlog e oportunidades — sem novos trackers nesta etapa

Todos os encaminhamentos abaixo são propostas para discussão. Implementação candidata não é integrada; integrado não equivale a aceite funcional. Responsáveis e prazos a confirmar. Os códigos internos são genealogia, não tarefas novas para somar às issues.

## 1. Guard Engine alinhado ao preflight

**Destino existente:** #154/#155; E19/E20.

**Base e limite:** 131 preflight e #139 guard estão integrados; #155 propõe pequena guarda de consistência e tem 11 checks failure no corte.

**Menor encaminhamento:** Revisar diff e controles bidirecionais; considerar recibos históricos sem inferir causa atual de billing. Reconciliar link/board só quanto ao critério satisfeito.

**Critério proposto:** Teste discrimina coluna ausente/extra e revisão da árvore de integração; ClickHouse real não é necessário só para ler guarda estática.

## 2. Consumidor de atribuição

**Destino existente:** #115; E01/E02/P01.

**Base e limite:** 126 entregou resolvedor puro com escopo app/job, conflito, zero e ausência, mas não fecha toda integração.

**Menor encaminhamento:** Escolher primeiro consumidor público e critério SQL/RDD; reaproveitar controles já existentes.

**Critério proposto:** Identidades preservadas e casos positivos/negativos observáveis no consumidor; sem reimplementar resolver por desconhecimento.

## 3. Garantia do gate tail-outlier

**Destino existente:** #123; E17/DEC-N6.

**Base e limite:** 127 integrou watcher, CLI e cenário; há relatos runtime de setembro. Associação por job/predicado é mais fraca que stage/tentativa/snapshot.

**Menor encaminhamento:** Reconciliar critério público com fontes; decidir garantia necessária e menor controle que falta.

**Critério proposto:** Não exigir nova arquitetura de vínculo sem decisão, não apagar prova histórica e não chamar hipótese de falso PASS observado.

## 4. Dispatcher PowerShell

**Destino existente:** #124; G08/P03.

**Base e limite:** 128 torna pwsh explícito e unifica ação/handler; DryRun lê rótulo e retorna antes de executar Command.

**Menor encaminhamento:** Desenhar controle seguro com handlers inofensivos; troca de Command mantendo Handler deve ser detectada.

**Critério proposto:** Provar handler alcançado ou revisar escopo explicitamente; sem iniciar ações Docker/Spark por causa desta documentação.

## 5. Argumentos R9D ON/OFF

**Destino existente:** #167; E16/DEC-N5, interface #185.

**Base e limite:** Main tem argv/assinatura incompatíveis. #185 Pod 3/Agmar é candidata externa com EnvFile/AdditionalComposeFile.

**Menor encaminhamento:** Comparar contribuição pública antes de variante local; revisar args, binding, comando completo, preflight e simetria dos braços.

**Critério proposto:** Prova discriminante de argumento removido de um braço; benchmark separado. Não declarar execução PowerShell reproduzida.

## 6. Preservar configuração do operador

**Destino existente:** #174; E08.

**Base e limite:** Sync-DevEnvForCanonicalScript usa Copy-Item -Force; não houve acesso ao arquivo de segredos nem reprodução de perda.

**Menor encaminhamento:** Definir recusa/comparação/backup ou passagem de EnvFile;185 não altera scripts/apex.ps1.

**Critério proposto:** Configuração distinta preexistente é preservada e destino é explícito; não fechar174 por ensure_env sozinho.

## 7. Identidade e ownership

**Destino existente:** #175; E09/E10/E11/DEC-10.

**Base e limite:** Nomes fixos Compose e guards existentes não definem protocolo completo entre checkouts/daemons.

**Menor encaminhamento:** Escolher identidades de checkout/context/project e operações protegidas; testar recusa de recurso alheio quando executar for autorizado.

**Critério proposto:** Preflight diferencia próprio/alheio/desconhecido antes da mutação; não inspecionamos containers nesta rodada.

## 8. Endpoint OTLP efetivo

**Destino existente:** #178; L09.

**Base e limite:** Remover plumbing morto em185 não prova forwarding/precedência; c3/c4 seguem com literais no trecho lido.

**Menor encaminhamento:** Escolher interface e mapear host→launcher→spark-submit; guardar default quando não houver override.

**Critério proposto:** Comando final com/sem override e controle que remove endpoint; sem iniciar Collector ou job para escrever plano.

## 9. Protocolo de overhead

**Destino existente:** #113; E06.

**Base e limite:** Launcher funcional não ratifica desenho do experimento. #185 muda drain/waits e pode afetar comparabilidade.

**Menor encaminhamento:** Versionar mínimo: braços, warm-up, amostra, estimador/banda, identificadores e interpretação de missing/inconclusive.

**Critério proposto:** Protocolo decidido antes de nova medição; não impor benchmark como gate de toda PR.

## 10. Tentativa e população de métricas

**Destino existente:** #169; E24/S14/S19, interfaces#142/#145.

**Base e limite:** Consumidores não devem ser uniformizados por intuição.125 etc não substituem contrato de população; Verify tem mudanças próprias.

**Menor encaminhamento:** Comparar stage_attempt/ts, population successful/all e legado em consumidores concretos.

**Critério proposto:** Decisão com contracasos retry/duplicata/legado; não selecionar latest global sem escopo.

## 11. DDL: replay e verificação

**Destino existente:** #170; E22/E23, interface #147.

**Base e limite:** 147 endurece alvo MV multiline; não prova no-op de todas migrações. verify_ddl tem alcance delimitado.

**Menor encaminhamento:** Separar promessa de replay, janela de alteração MV, quietude e campos inspecionados; definir ensaio/rollback conforme mudança.

**Critério proposto:** Critérios por migração e consumidor; não tratar nome/tipo como equivalência completa do DDL.

## 12. Database por consumidor

**Destino existente:** #173; E03/E04.

**Base e limite:** 131 usa database configurado; isso não provisiona schema alternativo nem corrige todos literais em outras lanes.

**Menor encaminhamento:** Inventariar executáveis versus comentários, consumidores e perfis; escolher alvo que precisa suportar alternativa.

**Critério proposto:** Consulta no database esperado e caso alternativo quando runtime autorizado; não repetir contagens antigas por lane.

## 13. Credenciais e recuperação

**Destino existente:** #176; E13, N06/#185.

**Base e limite:** S3A DEV é interface Pod 3; rotação ClickHouse é outro tema. Não foram lidos .env ou valores de credencial.

**Menor encaminhamento:** Documentar fronteira S3A candidata #185 separada da política de rotação/recuperação ClickHouse.

**Critério proposto:** Runbook com responsáveis e recuperação a combinar; sem publicar segredo ou alterar acesso nesta etapa.

## 14. Estudos de evolução

**Destino existente:** #168/#109/#114; E05/E07/E18.

**Base e limite:** Piso absoluto de cauda, reconciliação contrato/runtime e rehearsal ClickHouse são estudos já registrados.

**Menor encaminhamento:** Escolher pergunta e menor amostra/protocolo por estudo; considerar capacidade e valor antes de implementar.

**Critério proposto:** Resultado pode adotar/adiar/rejeitar com motivo; hipótese de falso positivo não é incidente comprovado.

## 15. Documentação e CI comuns

**Destino existente:** #165/#180/#125/#130; interfaces#161/#162/#164.

**Base e limite:** CI tem recortes por SHA/workflow; 161 é diagnóstico,162 é versão Verify,164 é docs.

**Menor encaminhamento:** Atualizar texto que depende de mudança escolhida; preservar causa histórica sem afirmar bloqueio atual de toda conta.

**Critério proposto:** Texto, critérios e checks aplicáveis coerentes com a árvore; nenhum aceite humano inferido de verde.

