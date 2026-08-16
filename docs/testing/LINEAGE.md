# Linhagem — do problema até o que o fechou

Os 11 issues abertos neste trabalho, na ordem real em que cada um foi resolvido.
Datas vêm da API do GitHub, não são estimadas.

Legenda da coluna **método**:

- `diamante` — a causa era incerta: mais de uma hipótese foi testada antes de
  convergir (Duplo Diamante genuíno)
- `laço direto` — a causa já estava no próprio erro: divergir ali seria
  cerimônia, não rigor

O critério que separa os dois, e por que a distinção importa, está em
[`METHODOLOGY.md`](METHODOLOGY.md).

## De onde vieram estes problemas

A maioria não foi encontrada lendo o `main` isoladamente. Foi encontrada
**comparando o `main` contra uma versão baseline independente do APEX**
(`gustocezar/apex-workspace`, branch `release/apex-v1-final-augusto` @
`7f53d22`), construída antes deste trabalho — e testando o que a diferença
entre as duas expunha.

Isso explica o formato de vários casos abaixo: em #58, #60, #61 e #65 o achado
veio de rodar o teste de um lado contra a implementação do outro. Detalhes de
acesso e a convenção `fork`/`upstream` estão em
[`README.md`](README.md#procedência--de-onde-veio-o-que-foi-testado).

Três issues fogem desse padrão, e vale marcar: **#71**, **#72** e os 6 defeitos
do **#62** foram achados testando o `main` (ou o próprio código novo) contra
infraestrutura real, sem envolver o baseline.

---

## Tabela mestra

| Issue | Problema | Descoberta | Correção | Fecha em | Método |
|---|---|---|---|---|---|
| [#58](https://github.com/luanmorenommaciel/apex/issues/58) | estado não é limpo em driver de execução longa; telemetria estimada, não medida | os 9 erros de tipo só apareceram ao compilar contra o teste da outra ponta | lifecycle correto + runtime medido de verdade | [PR #66](https://github.com/luanmorenommaciel/apex/pull/66) | diamante |
| [#63](https://github.com/luanmorenommaciel/apex/issues/63) | linhas duplicam sob retry do Collector e inflam agregados | Collector reenvia sem idempotência; nada no caminho deduplica | 3 parâmetros de config, zero lógica nova | [PR #67](https://github.com/luanmorenommaciel/apex/pull/67) | diamante → laço |
| [#60](https://github.com/luanmorenommaciel/apex/issues/60) | o JAR emite campos que não têm coluna no destino | 6 campos novos no total, não 1 | 6 migrações aditivas, idempotentes | [PR #68](https://github.com/luanmorenommaciel/apex/pull/68) | laço → diamante |
| [#64](https://github.com/luanmorenommaciel/apex/issues/64) | volume Docker apagado por engano durante os próprios testes | nada no fluxo detecta ambiente já ocupado | guard-rail que recusa, nunca limpa sozinho | [PR #69](https://github.com/luanmorenommaciel/apex/pull/69) | diamante → laço |
| [#61](https://github.com/luanmorenommaciel/apex/issues/61) | engine ainda lê só o Map antigo, ignora a coluna tipada | troca direta perderia a linha escrita na janela de transição | leitura tipada **com fallback**, não substituição | [PR #70](https://github.com/luanmorenommaciel/apex/pull/70) | diamante → laço |
| [#59](https://github.com/luanmorenommaciel/apex/issues/59) | `main` tem gate de JDK para as células Spark 4.x? | `scripts/find-jdk.sh` já existe e já está wired em 3 alvos | nenhuma — já atendida | *sem PR* | diamante |
| [#73](https://github.com/luanmorenommaciel/apex/issues/73) | não há sonda que exercite o caminho real ponta a ponta | 7 raias nunca tinham sido exercitadas com dado real | ferramental de sonda + racional de design | [PR #74](https://github.com/luanmorenommaciel/apex/pull/74) | diamante → laço |
| [#72](https://github.com/luanmorenommaciel/apex/issues/72) | criar MV apontando para tabela inexistente não dá erro — mas rejeita todo insert depois | achado por acaso, testando o #71 | guarda de ordem antes do `apply_ddl.sh` | [PR #75](https://github.com/luanmorenommaciel/apex/pull/75) | diamante → laço |
| [#71](https://github.com/luanmorenommaciel/apex/issues/71) | `mv_spark_events` parecia perder ~1 em 5 inserts | bissecção da query inteira: nenhuma peça isolada quebra | **nenhuma** — era TTL do ambiente de teste, não bug | *comentário de retratação* | diamante |
| [#62](https://github.com/luanmorenommaciel/apex/issues/62) | não existe comando único para subir o pacote local | 3 arquivos e 1 versão faltando ao portar | pacote operacional completo (`bootstrap`…`down`) | [PR #76](https://github.com/luanmorenommaciel/apex/pull/76) | diamante → laço ×6 |
| [#65](https://github.com/luanmorenommaciel/apex/issues/65) | duas abordagens resolvem coisas diferentes na mesma função, de forma incompatível | cada uma falha no teste da outra; o combinado passa nos dois | candidato testado, **não aplicado** | *decisão do time* | diamante |

---

## Os dois casos sem PR, e por quê

**#59 — fechada sem código.** A issue pedia um gate de JDK. Rodando os dois
caminhos de falha reais (`find-jdk.sh 999` e um `APEX_JDK_HOME` inválido), os
dois retornam `exit 1` com mensagem citando literalmente "Spark 4.x cross-build
cells". O gate já existia. Escrever código aqui teria sido duplicação.

**#71 — retratada.** O achado original (perda de ~1 em 5 inserts, com forense de
10 iterações) não sobreviveu a ser reexaminado: com uma janela de retenção
maior, as linhas "perdidas" apareciam. Era TTL do ambiente de teste expirando
entre o insert e a releitura, não perda de propagação. Comentário de retratação
postado na issue com a evidência que derruba a leitura anterior.

Fica documentado aqui de propósito. Um achado tem que sobreviver a ser
reexaminado, não só a ser publicado — e o script que produziu a retratação
([`scripts/test71_ts_hypothesis.sh`](scripts/test71_ts_hypothesis.sh)) está
junto, para quem quiser refazer o caminho inteiro.

---

## O caso #62 em detalhe — 6 correções em laço direto

O #62 é o exemplo mais claro de por que nem todo problema merece as quatro
fases. Depois que o escopo foi definido (fase de diamante real), rodar o pacote
pela primeira vez contra o stack real expôs 6 defeitos, **todos no código novo
desta contribuição, nenhum no código pré-existente**:

1. `hyperdx`/`mongodb` reportam "unhealthy" transitório durante a subida, e o
   `--wait` do Compose trata isso como falha terminal → desacoplados do `--wait`
2. porta nativa do ClickHouse ainda não ligada quando o healthcheck HTTP já diz
   Healthy → laço de espera antes do `apply_ddl.sh`
3. credencial MinIO gerada aleatoriamente por bootstrap, mas o
   `spark-defaults.conf` copiado carregava o placeholder estático → substituição
   real da credencial
4. `infra/.env` residual de teste manual anterior sobrescrevendo a senha gerada
   → arquivo removido (resíduo, não bug de código)
5. `e2e_canonical.ps1` não tem os parâmetros `-EnvFile`/`-AdditionalComposeFile`
   que o rascunho assumia → parâmetros removidos, `.env` sincronizado antes
6. cenário `tail_outlier` não existe no `ValidateSet` deste repositório →
   recusa imediata com mensagem clara, em vez de exceção confusa

Em nenhum deles a causa era incerta: a mensagem de erro dizia. Abrir e fechar um
diamante por cima disso teria sido teatro. O relato completo, com a saída de
cada tentativa, está em
[`evidence/operational-package.md`](evidence/operational-package.md).
